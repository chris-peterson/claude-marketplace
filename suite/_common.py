"""Shared helpers for the suite/ scripts: where the repos live and how to read
a plugin's descriptor. Sibling plugin repos are checked out beside this repo.
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"


def plugin_names() -> list[str]:
    return [p["name"] for p in json.loads(MANIFEST.read_text())["plugins"]]


def load_plugin(name: str) -> dict | None:
    """Parsed plugin.yml for a plugin, or None if it hasn't migrated yet."""
    path = WORKSPACE / name / "plugin.yml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text()) or {}
