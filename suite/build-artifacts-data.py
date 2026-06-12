#!/usr/bin/env python3
"""Generate docs/artifacts.json — the growth view's data — from the rolling
suite/artifacts.csv. Per plugin, a forward-filled total artifact count at each
change-point date (the stacked-bar series), plus the named changelog.

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
import re
import sys

from _common import CATS, ROOT, plugin_names

CSV = ROOT / "suite" / "artifacts.csv"
INDEX = ROOT / "docs" / "index.html"
TARGET = ROOT / "docs" / "artifacts.json"


def catalog_groups() -> list[tuple[str, list[str]]]:
    """[(ac-token, [slug, ...]), ...] in catalog order, from the SPA GROUPS."""
    block = re.search(r"const GROUPS\s*=\s*\[(.*?)\];", INDEX.read_text(), re.S)
    if not block:
        sys.exit("build-artifacts-data: could not find the GROUPS array in docs/index.html")
    groups = []
    for m in re.finditer(r'ac:\s*"([^"]+)".*?slugs:\s*\[([^\]]*)\]', block.group(1), re.S):
        groups.append((m.group(1), re.findall(r'"([^"]+)"', m.group(2))))
    return groups


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

    series = {}
    for p in plugins:
        pts = sorted((r for r in rows if r["plugin"] == p), key=lambda r: r["date"])
        totals, cur, i = [], None, 0
        for d in dates:
            while i < len(pts) and pts[i]["date"] <= d:
                cur = sum(int(pts[i][c]) for c in CATS)
                i += 1
            totals.append(cur)  # None before the plugin's first change point
        series[p] = totals

    changelog = [
        {"date": r["date"], "plugin": r["plugin"], "change": r["change"]}
        for r in sorted(rows, key=lambda r: (r["date"], r["plugin"]), reverse=True)
    ]

    TARGET.write_text(json.dumps({
        "dates": dates,
        "plugins": plugins,
        "colors": colors,
        "series": series,
        "changelog": changelog,
    }, indent=2))
    print(f"wrote {TARGET.relative_to(ROOT)} — {len(plugins)} plugins, "
          f"{len(dates)} change points")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
