#!/usr/bin/env python3
"""Generate docs/artifacts.json — the growth view's data — from the rolling
suite/artifacts.csv. Per plugin, a forward-filled total artifact count at each
weekly bucket (the stacked-bar series), plus the named changelog.

The chart's X axis is regular weekly buckets (Monday-start) spanning the first
change point through today, so the time axis is linear — equal spacing means
equal elapsed time. The changelog stays per-change-point (one row per dated
event), independent of the buckets.

Plugins are colored by their SPA catalog category (the four functional-area
tokens), parsed from the GROUPS array in docs/index.html so the chart and the
catalog never drift. Plugins are ordered by category so each color band is
contiguous in the stack, and the Nth plugin within a category carries shade N —
the SPA lightens shade>0 so same-category plugins stay distinguishable. The SPA
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
    """[(ac-token, [slug, ...]), ...] in catalog order, from the SPA GROUPS."""
    block = re.search(r"const GROUPS\s*=\s*\[(.*?)\];", INDEX.read_text(), re.S)
    if not block:
        sys.exit("build-artifacts-data: could not find the GROUPS array in docs/index.html")
    groups = []
    for m in re.finditer(r'ac:\s*"([^"]+)".*?slugs:\s*\[([^\]]*)\]', block.group(1), re.S):
        groups.append((m.group(1), re.findall(r'"([^"]+)"', m.group(2))))
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
    """Published (non-draft) GitHub releases for a plugin: [{date, tag, url}, ...].
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
        {"date": r["published_at"][:10], "tag": r["tag_name"], "url": r["html_url"],
         "published_at": r["published_at"]}
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


def build_changelog(rows: list[dict], plugins: list[str],
                    releases_by_plugin: dict[str, list[dict]]) -> list[dict]:
    """One changelog entry per (date, plugin): the day's artifact change tokens
    plus the latest release published that day (a plugin is often released
    several times a day; only the latest is shown so the log stays legible). The
    SPA shows the release first, then what changed. Newest entry first."""
    entries: dict[tuple[str, str], dict] = {}

    def entry(date: str, plugin: str) -> dict:
        return entries.setdefault((date, plugin),
            {"date": date, "plugin": plugin, "change": "", "releases": []})

    for r in rows:
        entry(r["date"], r["plugin"])["change"] = r["change"]
    for p in plugins:
        for rel in releases_by_plugin.get(p, []):
            entry(rel["date"], p)["releases"].append(rel)
    for e in entries.values():
        latest = max(e["releases"], key=lambda r: r["published_at"], default=None)
        e["releases"] = [{"tag": latest["tag"], "url": latest["url"]}] if latest else []

    return sorted(entries.values(),
                  key=lambda r: (r["date"], r["plugin"]), reverse=True)


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
    changelog = build_changelog(rows, plugins, releases_by_plugin)
    n_releases = sum(len(e["releases"]) for e in changelog)

    TARGET.write_text(json.dumps({
        "dates": labels,
        "plugins": plugins,
        "colors": colors,
        "series": series,
        "changelog": changelog,
    }, indent=2))
    print(f"wrote {TARGET.relative_to(ROOT)} — {len(plugins)} plugins, "
          f"{len(labels)} weekly buckets, {len(dates)} change points, "
          f"{n_releases} releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
