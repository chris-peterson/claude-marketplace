#!/usr/bin/env python3
"""Emit an RSS 2.0 feed from markdown changelogs dated by ``## YYYY-MM-DD``.

Each date heading becomes one feed item, and the bullets under it become the
item's body. The item's guid is the date, so a reworded or added bullet updates
the item in place in a feed reader instead of showing up as a new one.

Sources are read in the order given, newest first (a live changelog, then its
archive). Each source's route is its path relative to --docs-root, minus
``.md``, and an item links to its date heading on that route.

  changelog_feed.py docs/changelog.md docs/changelog-archive.md \\
      --site-url https://example.com/docs/ --title "Example: What's New" \\
      --out _site/feed.xml

Standard library only, so it runs in a bare CI image.
"""
import argparse
import datetime
import html
import posixpath
import re
import sys
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urljoin
from xml.sax.saxutils import escape

DAY_RE = re.compile(r"^## (\d{4})-(\d{2})-(\d{2})\s*$")
BULLET_RE = re.compile(r"^- (.*)$")
TYPE_RE = re.compile(r"^\*\*(.+?):?\*\*\s*(.*)$")
FOOTNOTE_RE = re.compile(r"\[\^[^\]]+\]")
CODE_RE = re.compile(r"`([^`]+)`")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])")
TITLE_ENTRIES = 3


def parse(path):
    """Yield (date, [bullet text]) per date heading, in file order."""
    day, bullets = None, []
    for line in Path(path).read_text().splitlines():
        m = DAY_RE.match(line)
        if m:
            if day:
                yield day, bullets
            day, bullets = datetime.date(*map(int, m.groups())), []
            continue
        b = BULLET_RE.match(line)
        if day and b:
            bullets.append(FOOTNOTE_RE.sub("", b.group(1)).strip())
    if day:
        yield day, bullets


class Router:
    """Turn a site-relative markdown path into a public URL."""

    def __init__(self, site_url, mode):
        self.site = site_url if site_url.endswith("/") else site_url + "/"
        self.mode = mode

    def page(self, route, anchor=None):
        route = route.lstrip("/")
        if route.endswith(".md"):
            route = route[: -len(".md")]
        if self.mode == "docsify":
            url = f"{self.site}#/{route}"
            return f"{url}?id={anchor}" if anchor else url
        url = urljoin(self.site, f"{route}.html")
        return f"{url}#{anchor}" if anchor else url

    def heading_id(self, heading):
        # docsify's slugify prefixes an id that starts with a digit with "_".
        return re.sub(r"^(\d)", r"_\1", heading) if self.mode == "docsify" else heading

    def link(self, href, base_route):
        """Resolve a link written in a changelog that lives at base_route."""
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
            return href
        path, _, anchor = href.partition("#")
        if not path:
            return self.page(base_route, anchor or None)
        if not path.startswith("/"):
            path = posixpath.normpath(posixpath.join(posixpath.dirname(base_route), path))
        if not path.endswith(".md"):
            return urljoin(self.site, path.lstrip("/"))
        return self.page(path, anchor or None)


def inline_html(text, router, base_route):
    """Render the inline markdown a changelog bullet uses: code, links, emphasis."""
    stash = []

    def keep(fragment):
        stash.append(fragment)
        return f"\x00{len(stash) - 1}\x00"

    def emphasis(s):
        s = html.escape(s, quote=False)
        s = BOLD_RE.sub(r"<strong>\1</strong>", s)
        return ITALIC_RE.sub(r"<em>\1</em>", s)

    text = CODE_RE.sub(lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)
    text = LINK_RE.sub(
        lambda m: keep(
            f'<a href="{html.escape(router.link(m.group(2), base_route))}">{emphasis(m.group(1))}</a>'
        ),
        text,
    )
    text = emphasis(text)
    unstash = re.compile(r"\x00(\d+)\x00")
    while unstash.search(text):
        text = unstash.sub(lambda m: stash[int(m.group(1))], text)
    return text


def plain(text):
    text = LINK_RE.sub(r"\1", text)
    return CODE_RE.sub(r"\1", text).replace("**", "")


def label(bullet):
    """The short form a title uses: the bolded type plus the first link's text."""
    m = TYPE_RE.match(bullet)
    if not m:
        return plain(bullet)[:60]
    kind, rest = m.groups()
    link = LINK_RE.search(rest)
    return f"{kind} {plain(link.group(1))}" if link else kind


def item_title(day, bullets):
    labels = [label(b) for b in bullets]
    shown = ", ".join(labels[:TITLE_ENTRIES])
    if len(labels) > TITLE_ENTRIES:
        shown += f", +{len(labels) - TITLE_ENTRIES} more"
    return f"{day:%b} {day.day}, {day.year}: {shown}"


def item_body(bullets, router, base_route):
    lis = []
    for b in bullets:
        m = TYPE_RE.match(b)
        if m:
            lis.append(
                f"<li><strong>{html.escape(m.group(1))}:</strong> "
                f"{inline_html(m.group(2), router, base_route)}</li>"
            )
        else:
            lis.append(f"<li>{inline_html(b, router, base_route)}</li>")
    return "<ul>" + "".join(lis) + "</ul>"


def pub_date(day):
    # Noon UTC keeps the date the same in every reader's local time zone.
    return format_datetime(datetime.datetime(day.year, day.month, day.day, 12, tzinfo=datetime.timezone.utc))


def build(args):
    router = Router(args.site_url, args.router)
    docs_root = Path(args.docs_root or Path(args.sources[0]).parent).resolve()
    days, seen = [], set()
    for src in args.sources:
        route = Path(src).resolve().relative_to(docs_root).as_posix()
        for day, bullets in parse(src):
            if day in seen:
                raise SystemExit(f"{src}: {day} appears in more than one date heading")
            seen.add(day)
            if bullets:
                days.append((day, bullets, route))
    if not days:
        raise SystemExit("no dated entries found in " + ", ".join(args.sources))
    days.sort(key=lambda d: d[0], reverse=True)
    days = days[: args.limit]

    feed_url = urljoin(router.site, Path(args.out).name)
    home = router.page(args.home) if args.home else router.site
    items = []
    for day, bullets, route in days:
        url = router.page(route, router.heading_id(day.isoformat()))
        cats = sorted({m.group(1) for b in bullets if (m := TYPE_RE.match(b))})
        items.append(
            "    <item>\n"
            f"      <title>{escape(item_title(day, bullets))}</title>\n"
            f"      <link>{escape(url)}</link>\n"
            f'      <guid isPermaLink="false">{escape(router.site)}{day.isoformat()}</guid>\n'
            f"      <pubDate>{pub_date(day)}</pubDate>\n"
            + "".join(f"      <category>{escape(c)}</category>\n" for c in cats)
            + f"      <description>{escape(item_body(bullets, router, route))}</description>\n"
            "    </item>\n"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{escape(args.title)}</title>\n"
        f"    <link>{escape(home)}</link>\n"
        f"    <description>{escape(args.description or args.title)}</description>\n"
        f'    <atom:link href="{escape(feed_url)}" rel="self" type="application/rss+xml"/>\n'
        "    <language>en</language>\n"
        f"    <lastBuildDate>{pub_date(days[0][0])}</lastBuildDate>\n"
        + "".join(items)
        + "  </channel>\n</rss>\n"
    ), len(days)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+", help="changelog markdown files, newest first")
    ap.add_argument("--site-url", required=True, help="public base URL of the built site")
    ap.add_argument("--title", required=True, help="feed title")
    ap.add_argument("--description", help="feed description (default: the title)")
    ap.add_argument("--out", required=True, help="feed path; its filename is also the published name")
    ap.add_argument("--docs-root", help="directory routes are relative to (default: the first source's)")
    ap.add_argument("--home", help="route the channel links to, e.g. whats-new (default: the site root)")
    ap.add_argument("--router", choices=["docsify", "path"], default="docsify",
                    help="docsify: #/route?id=anchor; path: route.html#anchor")
    ap.add_argument("--limit", type=int, default=30, help="most recent dates to include (default 30)")
    args = ap.parse_args()

    xml, count = build(args)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(xml)
    print(f"feed: {count} items -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
