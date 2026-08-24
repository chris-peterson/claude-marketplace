#!/usr/bin/env python3
"""Bootstrap suite/artifacts.csv from each plugin repo's git history.

Run ONCE to seed the rolling change-point log (or to re-seed from scratch). The
recurring build never does this — suite/record-artifacts.py appends to the file
in place. This walks every commit in each sibling repo, computes the artifact
name set at each, and emits one row per (date, plugin) — collapsing multiple
commits on a day to the day's final state:

    date,plugin,skills,rules,hooks,commands,agents,change

`change` is the named diff against the plugin's previous row (+skill:preview, or
a rename as a -/+ pair). A plugin's first row is the day it gained its first
artifacts; replaying the change column from empty reconstructs the current set,
so the visualization is rebuilt from this file alone — no git archaeology at
render time.

Window: commits before WINDOW_START are ignored, so a repo that carried history
from before it was a plugin starts its line at its first artifacts.
"""
import csv
import subprocess

from _common import (CATS, ROOT, WORKSPACE, change_tokens, counts,
                     empty_members, members_at, plugin_names)

CSV = ROOT / "suite" / "artifacts.csv"
WINDOW_START = "2026-01-01"


def commits(name: str) -> list[tuple[str, str]]:
    """(hash, committer-date) oldest-first."""
    out = subprocess.run(
        ["git", "-C", str(WORKSPACE / name), "log", "--reverse", "--format=%H %cs"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [tuple(line.split(" ", 1)) for line in out.splitlines() if line.strip()]


def main() -> int:
    rows = []
    for name in plugin_names():
        # the plugin's member set at the end of each day it changed (collapsing
        # multiple same-day commits to the day's final state)
        by_date = {}
        prev = None
        for h, date in commits(name):
            cur = members_at(name, h)
            if prev is None or any(cur[c] != prev[c] for c in CATS):
                if date >= WINDOW_START:
                    by_date[date] = cur  # later commit on the same date wins
                prev = cur

        # one row per date, diffed against the previous recorded day
        prev_mem = empty_members()
        for date in sorted(by_date):
            mem = by_date[date]
            if all(mem[c] == prev_mem[c] for c in CATS):
                continue  # an empty-set creation day, or intra-day churn that netted out
            change = change_tokens(prev_mem, mem)
            c = counts(mem)
            rows.append([date, name, *(c[x] for x in CATS), change])
            prev_mem = mem

    rows.sort(key=lambda r: (r[0], r[1]))
    with CSV.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["date", "plugin", *CATS, "change"])
        w.writerows(rows)
    print(f"seeded {CSV.relative_to(ROOT)} — {len(rows)} change points across "
          f"{len({r[1] for r in rows})} plugins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
