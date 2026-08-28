#!/usr/bin/env python3
"""Unit tests for the suite/ pure cores — the logic that runs unattended in CI
and writes straight to the live site, where a subtle regression ships silently:
the artifact-token round-trip (_common) and the date/series/changelog projection
(build-artifacts-data). Network, git, and the GROUPS scrape are left to
check-coverage and visual inspection. Run: `python3 -m unittest` from suite/,
or `just test`.
"""
import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

SUITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SUITE))

import _common as common  # noqa: E402


def _load(filename: str):
    """Import a hyphenated suite script (not a valid module name) by path."""
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"), SUITE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


artifacts = _load("build-artifacts-data.py")


class TokenRoundTrip(unittest.TestCase):
    """change_tokens encodes a diff; apply_tokens/replay decode it. The whole
    artifact history is reconstructed this way, so encode/decode must agree."""

    def test_change_tokens_format(self):
        prev = common.empty_members()
        cur = common.empty_members()
        cur["skills"].add("x")
        cur["rules"].add("y")
        self.assertEqual(common.change_tokens(prev, cur), "+skill:x +rule:y")

    def test_round_trip(self):
        prev = common.empty_members()
        prev["skills"].add("address-feedback")
        cur = common.empty_members()
        cur["skills"].add("resolve-feedback")
        replayed = common.empty_members()
        replayed["skills"].add("address-feedback")
        common.apply_tokens(replayed, common.change_tokens(prev, cur))
        self.assertEqual(replayed, cur)

    def test_apply_ignores_garbage(self):
        m = common.empty_members()
        common.apply_tokens(m, "not-a-token +skill:ok whatever")
        self.assertEqual(m["skills"], {"ok"})

    def test_replay(self):
        rows = [
            {"plugin": "anchor", "change": "+skill:a +skill:b"},
            {"plugin": "anchor", "change": "-skill:a +rule:r"},
        ]
        state = common.replay(rows)
        self.assertEqual(state["anchor"]["skills"], {"b"})
        self.assertEqual(state["anchor"]["rules"], {"r"})


class WeekBuckets(unittest.TestCase):
    def test_backs_up_to_monday(self):
        buckets = artifacts.week_buckets("2026-07-08")  # a Wednesday
        self.assertEqual(buckets[0].weekday(), 0)  # Monday
        self.assertLessEqual(buckets[0], date(2026, 7, 8))
        self.assertLess((date(2026, 7, 8) - buckets[0]).days, 7)

    def test_monday_input_unchanged(self):
        self.assertEqual(artifacts.week_buckets("2024-01-01")[0], date(2024, 1, 1))

    def test_weekly_spacing(self):
        buckets = artifacts.week_buckets("2024-01-01")
        self.assertEqual((buckets[1] - buckets[0]).days, 7)


class BuildSeries(unittest.TestCase):
    def test_forward_fill_and_none_prefix(self):
        buckets = [date(2026, 1, 5), date(2026, 1, 12), date(2026, 1, 19)]
        rows = [{"plugin": "p", "date": "2026-01-13",
                 "skills": "2", "rules": "0", "hooks": "0",
                 "commands": "0", "agents": "0"}]
        # week of Jan 5 ends Jan 11 (before the change) -> None; week of Jan 12
        # picks up the Jan 13 change -> 2; week of Jan 19 forward-fills -> 2.
        self.assertEqual(artifacts.build_series(rows, ["p"], buckets), {"p": [None, 2, 2]})


class BuildChangelog(unittest.TestCase):
    ROWS = [{"plugin": "anchor", "date": "2026-07-08", "change": "+skill:x"}]
    RELEASES = {"anchor": [
        {"tag": "v1.0.0", "url": "u1",
         "published_at": "2026-07-08T09:00:00Z", "notes": "first"},
        {"tag": "v1.1.0", "url": "u2",
         "published_at": "2026-07-08T15:00:00Z", "notes": "second"},
    ]}

    def test_releases_keep_their_instants(self):
        # Every release travels with its published_at, undated and uncollapsed —
        # the doc site picks the calendar day in the viewer's timezone.
        _, claimed = artifacts.build_changelog(self.ROWS, self.RELEASES)
        rels = artifacts.build_releases(["anchor"], self.RELEASES, claimed)
        self.assertEqual([(r["tag"], r["published_at"]) for r in rels],
                         [("v1.0.0", "2026-07-08T09:00:00Z"),
                          ("v1.1.0", "2026-07-08T15:00:00Z")])

    def test_retirement_claims_the_last_release(self):
        rows = self.ROWS + [{"plugin": "anchor", "date": "2026-07-09",
                             "change": "-plugin:anchor"}]
        cl, claimed = artifacts.build_changelog(rows, self.RELEASES)
        self.assertEqual(cl[0]["last_release"]["tag"], "v1.1.0")
        # reported on the retirement line alone, so it opens no entry of its own
        rels = artifacts.build_releases(["anchor"], self.RELEASES, claimed)
        self.assertEqual([r["tag"] for r in rels], ["v1.0.0"])

    def test_instant_rides_along_when_recorded(self):
        # `at` is what lets the doc site name the day in the reader's timezone;
        # rows logged before the column existed pass through without one.
        rows = [{"plugin": "anchor", "date": "2026-07-08", "change": "+skill:x",
                 "at": "2026-07-08T00:42:06Z"},
                {"plugin": "anchor", "date": "2026-07-06", "change": "+skill:w"}]
        cl, _ = artifacts.build_changelog(rows, {})
        self.assertEqual(cl[0]["at"], "2026-07-08T00:42:06Z")
        self.assertNotIn("at", cl[1])

    def test_entry_without_release_stays_bare(self):
        cl, claimed = artifacts.build_changelog(self.ROWS, {})
        self.assertEqual(claimed, {})
        self.assertEqual(artifacts.build_releases(["anchor"], {}, claimed), [])
        self.assertEqual(cl[0]["change"], "+skill:x")


if __name__ == "__main__":
    unittest.main()
