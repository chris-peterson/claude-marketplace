#!/usr/bin/env python3
"""Build docs/whats-new.md: the suite's changelog, one `## YYYY-MM-DD` section a day.

Merges two sources into the shape `changelog_feed.py` reads:

- CHANGELOG.md: hand-written highlights for the suite as a whole.
- docs/artifacts.json: every plugin release (with the first line of its notes)
  and every change to a plugin's skills, hooks, rules, commands, and agents.

A day's highlights come first, then its releases, then its artifact changes.
Usage: build-whats-new.py [--changelog PATH] [--artifacts PATH] [--out PATH]
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAY = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
TEASER_MAX = 140


def highlights(path: Path) -> dict[str, list[str]]:
    days, day = defaultdict(list), None
    for line in path.read_text().splitlines():
        m = DAY.match(line)
        if m:
            day = m.group(1)
        elif day and line.startswith("- "):
            days[day].append(line)
    return days


def teaser(summary: dict) -> str:
    for bucket in (summary or {}).get("buckets") or []:
        for item in bucket.get("items") or []:
            text = item.rstrip("…").strip()
            return text if len(text) <= TEASER_MAX else text[:TEASER_MAX].rsplit(" ", 1)[0] + "…"
    return ""


def describe(change: str) -> str:
    """'+skill:a +hook:b -command:c' -> 'added skill `a`, hook `b`; removed command `c`'."""
    added, removed = [], []
    for tok in change.split():
        if len(tok) < 2 or ":" not in tok or tok[0] not in "+-":
            continue
        kind, name = tok[1:].split(":", 1)
        (added if tok[0] == "+" else removed).append(f"{kind} `{name}`")
    parts = []
    if added:
        parts.append("added " + ", ".join(added))
    if removed:
        parts.append("removed " + ", ".join(removed))
    return "; ".join(parts)


def build(changelog: Path, artifacts: Path) -> str:
    data = json.loads(artifacts.read_text())
    days = defaultdict(list)
    for day, lines in highlights(changelog).items():
        days[day].extend(lines)
    for r in sorted(data.get("releases") or [], key=lambda r: (r["published_at"], r["plugin"])):
        line = f"- **released:** [{r['plugin']} {r['tag']}]({r['url']})"
        note = teaser(r.get("summary"))
        days[r["published_at"][:10]].append(line + (f": {note}" if note else ""))
    # A plugin's first row is its debut: the whole artifact set arriving at
    # once. That's a new plugin, not a change, and when the day's highlights
    # already announce it, the inventory adds nothing to their line.
    debuted = set()
    for c in sorted(data.get("changelog") or [], key=lambda c: (c["date"], c.get("at", ""))):
        plugin, day = c["plugin"], c["date"]
        if "-plugin:" in c["change"]:
            days[day].append(f"- **archived:** {plugin}")
            continue
        debut = plugin not in debuted
        debuted.add(plugin)
        if debut and any(re.match(rf"- \*\*new plugin:\*\* \[?{re.escape(plugin)}\b", h) for h in days[day]):
            continue
        what = describe(c["change"])
        if debut:
            days[day].append(f"- **new plugin:** {plugin}" + (f", with {what.removeprefix('added ')}" if what.startswith("added ") and ";" not in what else ""))
        elif what:
            days[day].append(f"- **changed:** {plugin} {what}")
    out = ["# What's new", ""]
    for day in sorted(days, reverse=True):
        out += [f"## {day}", ""] + days[day] + [""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    ap.add_argument("--artifacts", type=Path, default=ROOT / "docs" / "artifacts.json")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "whats-new.md")
    args = ap.parse_args()
    args.out.write_text(build(args.changelog, args.artifacts))
    print(f"whats-new: {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}")


if __name__ == "__main__":
    main()
