#!/usr/bin/env python3
"""Unit tests for build-specs-data.py's spec parser.

The spec browser shows what parse_spec finds, so a layout it can't read shows up
as a plugin with zero requirements rather than as an error. These pin the
heading-per-requirement layout sextant writes, and the suite's own SPEC.md.
Run: `python3 -m unittest` from suite/.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

_spec = importlib.util.spec_from_file_location("build_specs_data", HERE / "build-specs-data.py")
bsd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bsd)


def parse(text: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "SPEC.md"
        p.write_text(text)
        return bsd.parse_spec(p)


SEXTANT_LAYOUT = """\
# demo

## Requirements

### `WIRE`
The announcement

#### `WIRE-01`
The system shall print one line
on stdout.

#### `WIRE-02a`
A lettered refinement.

### `HEAR`
Subscribing

#### `HEAR-01`
The system shall subscribe.
"""


class HeadingPerRequirement(unittest.TestCase):
    def test_category_label_comes_from_the_next_line(self):
        cats = parse(SEXTANT_LAYOUT)
        self.assertEqual([(c["prefix"], c["label"]) for c in cats],
                         [("WIRE", "The announcement"), ("HEAR", "Subscribing")])

    def test_requirement_text_is_the_paragraph_below_its_heading(self):
        wire = parse(SEXTANT_LAYOUT)[0]
        self.assertEqual(wire["reqs"][0],
                         {"id": "WIRE-01", "text": "The system shall print one line on stdout."})

    def test_a_lettered_id_is_its_own_requirement(self):
        wire = parse(SEXTANT_LAYOUT)[0]
        self.assertEqual([r["id"] for r in wire["reqs"]], ["WIRE-01", "WIRE-02a"])

    def test_bracket_layout_still_parses(self):
        cats = parse("## WIRE — The announcement\n\n- **[WIRE-01]** The system shall print.\n")
        self.assertEqual(cats[0]["reqs"], [{"id": "WIRE-01", "text": "The system shall print."}])


class SuiteSpec(unittest.TestCase):
    """The suite's SPEC.md is the one every plugin cites; it must parse whole."""

    def test_every_requirement_heading_is_found_with_text(self):
        path = bsd.ROOT / "SPEC.md"
        headings = [l for l in path.read_text().splitlines() if l.startswith("#### `")]
        reqs = [r for c in bsd.parse_spec(path) for r in c["reqs"]]
        self.assertEqual(len(reqs), len(headings))
        self.assertTrue(all(r["text"] for r in reqs), [r["id"] for r in reqs if not r["text"]])


if __name__ == "__main__":
    unittest.main()
