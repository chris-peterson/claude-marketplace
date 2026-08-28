#!/usr/bin/env python3
"""Generate docs/artifacts.json — the growth view's data — from the rolling
suite/artifacts.csv. Per plugin, a forward-filled total artifact count at each
weekly bucket (the stacked-bar series), plus the named changelog.

The chart's X axis is regular weekly buckets (Monday-start) spanning the first
change point through today, so the time axis is linear — equal spacing means
equal elapsed time. The changelog stays per-change-point (one row per dated
event), independent of the buckets.

Plugins are colored by their doc site catalog category (the four functional-area
tokens), parsed from the GROUPS array in docs/index.html so the chart and the
catalog never drift. Plugins are ordered by category so each color band is
contiguous in the stack, and the Nth plugin within a category carries shade N —
the doc site lightens shade>0 so same-category plugins stay distinguishable. The doc site
resolves the tokens against the page's Dracula :root, so no hex lives here.
docs/artifacts.json is ephemeral — regenerated each deploy, not committed.
"""
import csv
import json
import os
import re
import sys
import urllib.request
from datetime import date, timedelta

from _common import CATS, ROOT, plugin_names

CSV = ROOT / "suite" / "artifacts.csv"
INDEX = ROOT / "docs" / "index.html"
TARGET = ROOT / "docs" / "artifacts.json"
RELEASES_API = "https://api.github.com/repos/chris-peterson/{}/releases"


def catalog_groups() -> list[tuple[str, list[str]]]:
    """[(ac-token, [slug, ...]), ...] in catalog order, from the doc site GROUPS.

    A group's optional `retired` list follows its `slugs`. The catalog renders
    only `slugs`, but the growth view covers both: a plugin that has left the
    roster still happened, and its series has to keep the category color and the
    place in the stack it held while it shipped. Dropping it instead would take
    its past artifacts out of every bucket it existed in and rewrite the history
    the chart is there to show.
    """
    block = re.search(r"const GROUPS\s*=\s*\[(.*?)\];", INDEX.read_text(), re.S)
    if not block:
        sys.exit("build-artifacts-data: could not find the GROUPS array in docs/index.html")
    groups = []
    for m in re.finditer(
            r'ac:\s*"([^"]+)".*?slugs:\s*\[([^\]]*)\](?:\s*,\s*retired:\s*\[([^\]]*)\])?',
            block.group(1), re.S):
        names = re.findall(r'"([^"]+)"', m.group(2))
        names += re.findall(r'"([^"]+)"', m.group(3) or "")
        groups.append((m.group(1), names))
    return groups


def week_buckets(first: str) -> list[date]:
    """Monday-start week boundaries from the week of `first` through this week."""
    start = date.fromisoformat(first)
    start -= timedelta(days=start.weekday())  # back up to that week's Monday
    today = date.today()
    buckets, cur = [], start
    while cur <= today:
        buckets.append(cur)
        cur += timedelta(days=7)
    return buckets


def fetch_releases(plugin: str) -> list[dict]:
    """Published (non-draft) GitHub releases for a plugin: [{published_at, tag, url, notes}, ...].
    Network/HTTP failure raises — release enrichment is not optional, so a bad
    fetch fails the build loudly rather than silently dropping events. A
    GITHUB_TOKEN in the env (CI) is used for the higher API rate limit."""
    req = urllib.request.Request(
        RELEASES_API.format(plugin),
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "claude-marketplace-build"},
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return [
        {"tag": r["tag_name"], "url": r["html_url"],
         "published_at": r["published_at"], "notes": (r.get("body") or "").strip()}
        for r in data if not r.get("draft")
    ]


def build_series(rows: list[dict], plugins: list[str], buckets: list[date]) -> dict:
    """Per plugin, a forward-filled total artifact count at each weekly bucket.
    Each total is the sum of that plugin's category counts at the latest change
    point on or before the bucket's week end; None before its first change point."""
    series = {}
    for p in plugins:
        pts = sorted((r for r in rows if r["plugin"] == p), key=lambda r: r["date"])
        totals, cur, i = [], None, 0
        for b in buckets:
            week_end = (b + timedelta(days=6)).isoformat()
            while i < len(pts) and pts[i]["date"] <= week_end:
                cur = sum(int(pts[i][c]) for c in CATS)
                i += 1
            totals.append(cur)  # None before the plugin's first change point
        series[p] = totals
    return series


def build_changelog(rows: list[dict],
                    releases_by_plugin: dict[str, list[dict]]) -> tuple[list[dict], dict]:
    """One changelog entry per (date, plugin) artifact change point, newest first,
    plus the set of releases claimed by a retirement. An entry carries the
    committer instant as `at` where the log recorded one, so the doc site can name
    the day in the reader's timezone rather than the committer's.

    A row retiring a plugin (a `-plugin:` token) carries the last version it
    ever shipped as `last_release`, so the version someone still has installed
    is on the line that retires it. That release is reported there alone — it
    doesn't also open an entry on its own publish date, so it's returned here
    for the release list to skip.
    """
    entries: dict[tuple[str, str], dict] = {}
    retired: dict[str, dict] = {}
    for r in rows:
        e = entries.setdefault((r["date"], r["plugin"]),
                               {"date": r["date"], "plugin": r["plugin"]})
        e["change"] = r["change"]
        if r.get("at"):
            e["at"] = r["at"]  # rows recorded before the column stay date-only
        if "-plugin:" in r["change"]:
            e["removed"] = True
            retired[r["plugin"]] = e

    claimed: dict[str, dict] = {}
    for p, e in retired.items():
        last = max(releases_by_plugin.get(p) or [],
                   key=lambda r: r["published_at"], default=None)
        if last:
            claimed[p] = last
            e["last_release"] = {"tag": last["tag"], "url": last["url"],
                                 "notes": last["notes"]}

    return sorted(entries.values(), key=lambda r: (r["date"], r["plugin"]),
                  reverse=True), claimed


def build_releases(plugins: list[str], releases_by_plugin: dict[str, list[dict]],
                   claimed: dict[str, dict]) -> list[dict]:
    """Every published release as a bare instant, for the doc site to date in the
    viewer's own timezone. A release near midnight UTC belongs to a different day
    depending on where you're reading from, so the calendar day it lands on is the
    browser's call, not this build's — which is also where a day's several releases
    get collapsed to the latest one. Releases already reported by a retirement's
    `last_release` are left out."""
    return [{"plugin": p, "published_at": rel["published_at"], "tag": rel["tag"],
             "url": rel["url"], "notes": rel["notes"]}
            for p in plugins
            for rel in releases_by_plugin.get(p, [])
            if rel is not claimed.get(p)]


def main() -> int:
    rows = list(csv.DictReader(CSV.open(newline="")))
    dates = sorted({r["date"] for r in rows})
    present = {r["plugin"] for r in rows}

    # category order + per-category shade, restricted to plugins in the log
    plugins, colors = [], {}
    for token, slugs in catalog_groups():
        for shade, slug in enumerate(s for s in slugs if s in present):
            plugins.append(slug)
            colors[slug] = {"token": token, "shade": shade}

    buckets = week_buckets(dates[0])
    labels = [b.isoformat() for b in buckets]

    series = build_series(rows, plugins, buckets)

    releases_by_plugin = {p: fetch_releases(p) for p in plugins}
    changelog, claimed = build_changelog(rows, releases_by_plugin)
    releases = build_releases(plugins, releases_by_plugin, claimed)
    n_releases = len(releases) + len(claimed)

    TARGET.write_text(json.dumps({
        "dates": labels,
        "plugins": plugins,
        "colors": colors,
        "series": series,
        "changelog": changelog,
        "releases": releases,
    }, indent=2))
    print(f"wrote {TARGET.relative_to(ROOT)} — {len(plugins)} plugins, "
          f"{len(labels)} weekly buckets, {len(dates)} change points, "
          f"{n_releases} releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
