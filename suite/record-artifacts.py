#!/usr/bin/env python3
"""Append a row to suite/artifacts.csv when a plugin's artifact set has changed.

The recurring half of the rolling log (suite/seed-artifacts-history.py does the
one-time bootstrap). Replays the existing file to get each plugin's last-known
artifact set, compares it to the committed HEAD of the sibling repo, and appends
one dated change-point row per plugin that moved — recording the named diff in
the `change` column. Comparing name sets (not just counts) catches renames a
count would miss. A same-day row whose net change has since reverted to nil —
an artifact added and moved/removed within the same day — is dropped, since the
day's row should express the net move and there is none. Idempotent: a re-run
with nothing newly committed is a no-op.

Wired into CI (deploy-docs.yml) and `just record-artifacts`.
"""
import csv
import subprocess
import sys

from _common import (CATS, ROOT, WORKSPACE, change_tokens, counts, empty_members,
                     members_at, plugin_names, replay)

CSV = ROOT / "suite" / "artifacts.csv"


def head_date(name: str) -> str:
    return subprocess.run(
        ["git", "-C", str(WORKSPACE / name), "log", "-1", "--format=%cs", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def main() -> int:
    if not CSV.exists():
        sys.exit(f"{CSV.relative_to(ROOT)} missing — run suite/seed-artifacts-history.py to bootstrap it")

    rows = list(csv.DictReader(CSV.open(newline="")))
    recorded = []
    dropped = []
    for name in plugin_names():
        cur = members_at(name, "HEAD")
        date = head_date(name)
        # the plugin's set as of strictly before this date, so a same-day re-run
        # merges into one row rather than appending a second
        before = replay([r for r in rows if r["plugin"] == name and r["date"] < date]).get(name, empty_members())
        same_day = [r for r in rows if r["plugin"] == name and r["date"] == date]

        desired = None
        if any(cur[c] != before[c] for c in CATS):
            c = counts(cur)
            desired = {"date": date, "plugin": name, **{x: str(c[x]) for x in CATS},
                       "change": change_tokens(before, cur)}

        cols = ["date", "plugin", *CATS, "change"]
        if desired and len(same_day) == 1 and all(str(same_day[0][k]) == desired[k] for k in cols):
            continue  # already recorded at this date — nothing to do
        if not desired and not same_day:
            continue

        rows = [r for r in rows if not (r["plugin"] == name and r["date"] == date)]
        if desired:
            rows.append(desired)
            recorded.append((date, name, desired["change"]))
        else:
            # no net change vs the prior day, yet a same-day row exists — its
            # move has since reverted (added then moved/removed within the day).
            # It's already been filtered out of `rows`; note it so the file gets
            # written and the drop is reported.
            dropped += [(date, name, r["change"]) for r in same_day]

    if not recorded and not dropped:
        print(f"{CSV.relative_to(ROOT)}: no artifact changes")
        return 0

    rows.sort(key=lambda r: (r["date"], r["plugin"]))
    with CSV.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["date", "plugin", *CATS, "change"])
        w.writerows([[r["date"], r["plugin"], *(r[x] for x in CATS), r["change"]] for r in rows])
    for date, name, change in recorded:
        print(f"recorded {name} ({date}): {change}")
    for date, name, change in dropped:
        print(f"dropped {name} ({date}): {change} (net change reverted same-day)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
