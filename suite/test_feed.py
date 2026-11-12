#!/usr/bin/env python3
"""The What's new feed: changelog_feed.py over a small changelog, parsed back.

One item per date, its guid the date, its link the date heading on
whats-new.html, and entry HTML escaped inside <description>. Run with
`just test`.
"""
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "changelog_feed.py"
SITE = "https://example.com/market/"

CHANGELOG = """# What's new

## 2026-11-11

- **new plugin:** [rig](https://example.com/rig/): launch with a <named> set.
- **changed:** six jobs.

## 2026-10-01

- **fixed:** something.
"""


class Feed(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "whats-new.md").write_text(CHANGELOG)
        out = self.dir / "feed.xml"
        subprocess.run([sys.executable, "-I", str(SCRIPT), str(self.dir / "whats-new.md"),
                        "--site-url", SITE, "--title", "t", "--home", "whats-new",
                        "--router", "path", "--out", str(out)], check=True, capture_output=True)
        self.items = ET.parse(out).getroot().findall("./channel/item")

    def test_one_item_per_date_newest_first(self):
        self.assertEqual([i.findtext("pubDate")[5:16] for i in self.items],
                         ["11 Nov 2026", "01 Oct 2026"])

    def test_link_is_the_date_heading(self):
        self.assertEqual(self.items[0].findtext("link"), SITE + "whats-new.html#2026-11-11")

    def test_guid_is_the_date(self):
        self.assertTrue(self.items[0].findtext("guid").endswith("2026-11-11"))

    def test_entry_html_is_escaped_text(self):
        body = self.items[0].findtext("description")
        self.assertIn("<strong>new plugin:</strong>", body)
        self.assertIn("&lt;named&gt;", body)


class WhatsNew(unittest.TestCase):
    """build-whats-new.py merges CHANGELOG.md's highlights with the releases and
    artifact changes in artifacts.json, a day's highlights first."""

    def build(self, changelog, artifacts):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "build_whats_new", Path(__file__).resolve().parent / "build-whats-new.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d = Path(tempfile.mkdtemp())
        (d / "CHANGELOG.md").write_text(changelog)
        (d / "artifacts.json").write_text(__import__("json").dumps(artifacts))
        return mod.build(d / "CHANGELOG.md", d / "artifacts.json")

    def test_merge_order_and_shapes(self):
        out = self.build("## 2026-11-11\n\n- **released:** bridge.ai 2.0\n", {
            "releases": [{"plugin": "anchor", "tag": "v2.0.0", "published_at": "2026-11-11T20:00:00Z",
                          "url": "https://example.com/r", "summary": {"buckets": [{"items": ["Stacks."]}]}}],
            "changelog": [{"date": "2026-11-11", "plugin": "rig", "change": "+skill:switch -hook:old"},
                          {"date": "2026-08-24", "plugin": "moor", "change": "-plugin:moor"}],
        })
        self.assertEqual(out.splitlines()[2:8], [
            "## 2026-11-11", "",
            "- **released:** bridge.ai 2.0",
            "- **released:** [anchor v2.0.0](https://example.com/r): Stacks.",
            "- **changed:** rig added skill `switch`; removed hook `old`", ""])
        self.assertIn("## 2026-08-24\n\n- **archived:** moor", out)


if __name__ == "__main__":
    unittest.main()
