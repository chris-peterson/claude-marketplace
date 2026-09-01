#!/usr/bin/env python3
"""Unit tests for the artifact-token round-trip in `_common`.

The recorder encodes each change point as +/- tokens and the whole artifact
history is reconstructed by replaying them, so encode and decode have to agree
exactly — a disagreement rewrites the past rather than failing. `shipyard`'s own
suite covers the projections that read the log. Run: `python3 -m unittest` from
suite/, or `just test`.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _common as common  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
