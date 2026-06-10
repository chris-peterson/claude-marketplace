#!/usr/bin/env python3
"""Trace soft dependencies between plugins and emit docs/deps.json.

A soft dependency is one plugin referencing another at runtime — a `/other:`
slash command or a shell-out to the other plugin's CLI. This is a heuristic: it
scans each plugin's code directories (not docs) for references to the others,
then cross-checks what it finds against the `soft_deps` declared in each
plugin.yml. docs/relationships.md remains the authority; this surfaces drift
(an edge in code but not declared, or declared but not found) to reconcile.
docs/deps.json is ephemeral — regenerated each deploy.
"""
import json
import re

from _common import ROOT, WORKSPACE, load_plugin, plugin_names

TARGET = ROOT / "docs" / "deps.json"

# a reference in code is a real dependency, unlike a passing mention in docs
CODE_DIRS = ("skills", "hooks", "scripts", "commands", "bin", "rules", "src")
SCAN_SUFFIXES = (".sh", ".py", ".js", ".ts", ".md", ".json", ".yml", ".yaml")


def declared_soft_deps(name: str) -> list[str]:
    spec = load_plugin(name) or {}
    return list((spec.get("suite") or {}).get("soft_deps") or [])


def scan_edges(name: str, others: list[str]) -> dict[str, list[str]]:
    """{other_plugin: [evidence files]} for high-precision references — a
    `/other:` slash command or `other` as a shell command token (line start,
    or after | && ; $( `), counted only on non-comment lines."""
    root = WORKSPACE / name
    found: dict[str, list[str]] = {}
    patterns = {
        o: re.compile(rf"(?:/{re.escape(o)}:|(?:^|[|&;`]|\$\()\s*{re.escape(o)}\b)")
        for o in others
    }
    for code_dir in CODE_DIRS:
        base = root / code_dir
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            try:
                lines = path.read_text(errors="ignore").splitlines()
            except OSError:
                continue
            rel = path.relative_to(root).as_posix()
            for line in lines:
                if line.lstrip().startswith("#"):
                    continue
                for other, pat in patterns.items():
                    if pat.search(line) and rel not in found.setdefault(other, []):
                        found[other].append(rel)
    return found


def main() -> int:
    names = plugin_names()
    edges = []
    mismatches = {"undeclared": [], "dangling": []}
    for name in names:
        others = [o for o in names if o != name]
        discovered = scan_edges(name, others)
        declared = declared_soft_deps(name)
        for target, evidence in discovered.items():
            edges.append({"from": name, "to": target, "evidence": evidence[:5]})
            if declared and target not in declared:
                mismatches["undeclared"].append({"from": name, "to": target})
        for target in declared:
            if target not in discovered:
                mismatches["dangling"].append({"from": name, "to": target})

    out = {"nodes": names, "edges": edges, "mismatches": mismatches}
    TARGET.write_text(json.dumps(out, indent=2) + "\n")
    print(
        f"wrote {TARGET.relative_to(ROOT)} — {len(edges)} candidate edge(s), "
        f"{len(mismatches['undeclared'])} undeclared, {len(mismatches['dangling'])} dangling"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
