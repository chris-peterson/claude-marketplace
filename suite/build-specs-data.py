#!/usr/bin/env python3
"""Project each plugin's SPEC.md → docs/specs.json (the spec browser's tree data:
plugin → category → requirement).

Each plugin keeps an EARS-style spec — requirements tagged `[PFX-NN]`, grouped
under category headings that carry the prefix. The suite uses two heading-label
conventions plus beacon's numbered sections, so the parser covers all three
(see HEADING_A / HEADING_B). tack has adopted a versioned layout
(`spec/v<N>/SPEC.md`); everyone else keeps a root `SPEC.md` — spec_path() prefers
the versioned file when present. docs/specs.json is ephemeral — regenerated each
deploy, not committed.
"""
import json
import re

from _common import ROOT, WORKSPACE, load_plugin, plugin_names

TARGET = ROOT / "docs" / "specs.json"

# A requirement line, tolerant of the suite's four ID-marker styles — all wrap
# the `PFX-NN` id with markup on both sides, at line start after an optional
# bullet: `**[TGT-01]**` (bold-bracket), `[RCON-01]` (bare bracket),
# `` `[CFG-1]` `` (backtick-bracket), `**RES-01.**` (bold-dot, no bracket).
# Anchored at line start, so mid-sentence cross-references (`(RES-02)`) don't match.
REQ = re.compile(r"^\s*(?:[-*]\s+)?[`*\[]{1,3}([A-Z]{2,})-(\d+)[.\]`*]{1,3}\s+(.*)")
# A markdown heading, any level. The leading `N.` / `N.N` section number (beacon,
# ClaudeWatch) is stripped before matching a category shape.
HEADING = re.compile(r"^(#{2,6})\s+(.*?)\s*#*$")
SECTION_NUM = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
# Pattern A: `PFX — Label` (em/en dash or hyphen). Pattern B: `Label (PFX)`.
HEADING_A = re.compile(r"^([A-Z]{2,})\s*[—–-]\s*(.+)$")
HEADING_B = re.compile(r"^(.+?)\s*\(([A-Z]{2,})\)\s*$")


def spec_path(name: str):
    """The plugin's spec file: the highest `spec/v<N>/SPEC.md` if the versioned
    layout exists, else the repo-root SPEC.md. None if neither is present."""
    repo = WORKSPACE / name
    versioned = sorted(repo.glob("spec/v*/SPEC.md"))
    if versioned:
        return versioned[-1]
    root = repo / "SPEC.md"
    return root if root.exists() else None


def clean_label(text: str) -> str:
    """A heading stripped of its leading section number and any trailing `(PFX)`
    tag — the display label when a requirement has no category heading of its own
    (e.g. beacon's WATCH/COLOR reqs sitting inside the WIP section)."""
    text = SECTION_NUM.sub("", text.strip())
    return re.sub(r"\s*\([A-Z]{2,}\)\s*$", "", text).strip()


def parse_heading(text: str):
    """(prefix, label) if a heading declares a requirement category, else None."""
    text = SECTION_NUM.sub("", text.strip())
    if m := HEADING_A.match(text):
        return m.group(1), m.group(2).strip()
    if m := HEADING_B.match(text):
        return m.group(2), m.group(1).strip()
    return None


def parse_spec(path) -> list[dict]:
    """Categories in document order, each {prefix, label, desc, reqs[]}. A
    requirement attaches to the last category heading seen; a category's desc is
    the prose between its heading and its first requirement."""
    cats: list[dict] = []
    by_prefix: dict[str, dict] = {}
    current: dict | None = None
    collecting_desc = False
    last_heading = ""

    def ensure(prefix: str, label: str | None = None) -> dict:
        cat = by_prefix.get(prefix)
        if cat is None:
            cat = {"prefix": prefix, "label": label or prefix, "desc": "", "reqs": []}
            by_prefix[prefix] = cat
            cats.append(cat)
        elif label and cat["label"] == prefix:
            cat["label"] = label
        return cat

    for line in path.read_text().splitlines():
        if m := HEADING.match(line):
            collecting_desc = False
            current = None
            last_heading = clean_label(m.group(2))
            parsed = parse_heading(m.group(2))
            if parsed:
                prefix, label = parsed
                current = ensure(prefix, label)
                collecting_desc = True
            continue
        if m := REQ.match(line):
            collecting_desc = False
            prefix, num, txt = m.group(1), m.group(2), m.group(3).strip()
            cat = current if current and current["prefix"] == prefix else ensure(prefix, last_heading)
            cat["reqs"].append({"id": f"{prefix}-{num}", "text": txt})
            continue
        if collecting_desc and current is not None:
            stripped = line.strip()
            if stripped:
                current["desc"] = (current["desc"] + " " + stripped).strip()

    return [c for c in cats if c["reqs"]]


def main() -> int:
    plugins = []
    for name in plugin_names():
        path = spec_path(name)
        if path is None:
            print(f"WARN: {name} has no SPEC.md — skipping", flush=True)
            continue
        cats = parse_spec(path)
        suite = (load_plugin(name) or {}).get("suite") or {}
        plugins.append({
            "name": name,
            "gloss": suite.get("gloss", ""),
            "spec": str(path.relative_to(WORKSPACE / name)),
            "categories": cats,
            "catCount": len(cats),
            "reqCount": sum(len(c["reqs"]) for c in cats),
        })

    TARGET.write_text(json.dumps({"plugins": plugins}, indent=2) + "\n")
    total = sum(p["reqCount"] for p in plugins)
    print(f"wrote {TARGET.relative_to(ROOT)} — {len(plugins)} plugins, {total} requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
