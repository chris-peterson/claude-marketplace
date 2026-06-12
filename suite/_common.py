"""Shared helpers for the suite/ scripts: where the repos live, how to read a
plugin's descriptor, and how to read/diff/replay its artifact set. Sibling
plugin repos are checked out beside this repo.
"""
import json
import os
import pathlib
import subprocess

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"

# Artifact categories, in the column order of suite/artifacts.csv. count_dir's
# rule (one skill per dir, one rule/hook/command/agent per file) maps to the
# immediate child names under each directory.
CATS = ["skills", "rules", "hooks", "commands", "agents"]
SINGULAR = {c: c[:-1] for c in CATS}          # skills -> skill
PLURAL = {v: k for k, v in SINGULAR.items()}  # skill  -> skills


def plugin_names() -> list[str]:
    return [p["name"] for p in json.loads(MANIFEST.read_text())["plugins"]]


def load_plugin(name: str) -> dict | None:
    """Parsed plugin.yml for a plugin, or None if it hasn't migrated yet."""
    path = WORKSPACE / name / "plugin.yml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text()) or {}


def empty_members() -> dict[str, set]:
    return {c: set() for c in CATS}


def members_at(name: str, ref: str = "HEAD") -> dict[str, set]:
    """Artifact names under each category in a plugin repo at a git ref. Uses
    git (not the working tree) so the seed walk and the per-build recorder agree
    on exactly the committed state."""
    out = subprocess.run(
        ["git", "-C", str(WORKSPACE / name), "ls-tree", "-r", "--name-only", ref],
        capture_output=True, text=True, check=True,
    ).stdout
    members = empty_members()
    for path in out.splitlines():
        seg = path.split("/", 2)
        if len(seg) >= 2 and seg[0] in members:
            members[seg[0]].add(os.path.splitext(seg[1])[0])
    return members


def counts(members: dict[str, set]) -> dict[str, int]:
    return {c: len(members[c]) for c in CATS}


def change_tokens(prev: dict[str, set], cur: dict[str, set]) -> str:
    """Named +/- tokens for the move from prev to cur, e.g.
    '+skill:resolve-feedback -skill:address-feedback'."""
    parts = []
    for c in CATS:
        parts += [f"+{SINGULAR[c]}:{n}" for n in sorted(cur[c] - prev[c])]
        parts += [f"-{SINGULAR[c]}:{n}" for n in sorted(prev[c] - cur[c])]
    return " ".join(parts)


def apply_tokens(members: dict[str, set], change: str) -> None:
    """Apply a change string's +/- tokens to a member set, in place. Tokens that
    don't parse as +/-cat:name are ignored, so hand-edits stay robust."""
    for tok in change.split():
        if len(tok) < 2 or tok[0] not in "+-" or ":" not in tok:
            continue
        sg, name = tok[1:].split(":", 1)
        cat = PLURAL.get(sg)
        if cat:
            members[cat].add(name) if tok[0] == "+" else members[cat].discard(name)


def replay(rows: list[dict]) -> dict[str, dict[str, set]]:
    """Reconstruct each plugin's current member set by applying every row's
    change tokens in file order — so the recorder needs no state file and never
    re-walks git history."""
    state: dict[str, dict[str, set]] = {}
    for r in rows:
        m = state.setdefault(r["plugin"], empty_members())
        apply_tokens(m, r["change"])
    return state
