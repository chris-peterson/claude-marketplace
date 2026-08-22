#!/usr/bin/env python3
"""Fail the build if a plugin isn't properly represented on the bridge.ai doc site.

A plugin can silently break the landing page (docs/index.html) four ways, none
visible until someone clicks:

1. Absent from the generated PLUGINS data — the build never produced a card for
   it (e.g. its plugin.yml is missing or has no suite: block).
2. Not in a GROUPS slug list — the catalog renders only grouped slugs, so the
   data exists but no card is shown.
3. Unplaced in suite/tiers.yml — the card renders with no adoption tier, so a
   visitor can't tell whether it's the one to start with or the one kept only as
   a reference. Placed twice is the same error from the other side: the
   projection collapses it to whichever tier came last.
4. Missing a field the catalog card needs — it declares its `group` slug and
   dereferences a `pitch`/`what` blurb (`p.pitch || p.what`) unguarded; a
   plugin without them can't render a card. (The in-hub per-plugin detail view
   was removed in the descriptor migration — #/<slug> now redirects to each
   plugin's own docs site — so `cmds` and the `session`/`examples` walkthrough
   it used to read are no longer required.)

This runs after `build-plugins-data.py` (it reads the generated docs/plugins.js) and
cross-references marketplace.json and the doc site GROUPS, failing loudly so the
omission never deploys. Wired into CI and `just build`.
"""
import json
import re
import sys

import yaml

from _common import ROOT, plugin_names

INDEX = ROOT / "docs" / "index.html"
PLUGINS_JS = ROOT / "docs" / "plugins.js"
TIERS_YML = ROOT / "suite" / "tiers.yml"

# Fields a plugin must declare to render a catalog card (docs/index.html): its
# `group` slug, and a blurb the card shows as `pitch || what`. The per-plugin
# detail view was removed in the descriptor migration (#/<slug> redirects to the
# plugin's own docs site), so `cmds` and the `session`/`examples` walkthrough it
# read are no longer required.
REQUIRED = ["group"]


def grouped_slugs() -> list[str]:
    block = re.search(r"const GROUPS\s*=\s*\[(.*?)\];", INDEX.read_text(), re.S)
    if not block:
        sys.exit("check-coverage: could not find the GROUPS array in docs/index.html")
    slugs: list[str] = []
    for arr in re.findall(r"slugs:\s*\[([^\]]*)\]", block.group(1)):
        slugs.extend(re.findall(r'"([^"]+)"', arr))
    return slugs


def generated_plugins() -> dict:
    if not PLUGINS_JS.exists():
        sys.exit("check-coverage: docs/plugins.js not found — run suite/build-plugins-data.py first")
    m = re.search(r"const PLUGINS\s*=\s*(\{.*?\});\n", PLUGINS_JS.read_text(), re.S)
    if not m:
        sys.exit("check-coverage: could not parse PLUGINS from docs/plugins.js")
    return json.loads(m.group(1))


def generated_tiers() -> list[dict]:
    """The TIERS vocabulary as it reached docs/plugins.js. Checked separately from
    tiers.yml because the failure mode isn't a bad declaration — it's a generator
    that doesn't emit TIERS at all (shipyard's gen-plugins-js, for one, projects
    only PLUGINS). The page reads TIERS unguarded at first render, so the symptom
    is a thrown ReferenceError that takes the whole catalog with it, in the
    browser, after a green deploy."""
    m = re.search(r"const TIERS\s*=\s*(\[.*?\]);\n", PLUGINS_JS.read_text(), re.S)
    if not m:
        sys.exit("check-coverage: docs/plugins.js carries no TIERS — the catalog reads it "
                 "at first render, so the page would fail to build its cards. Regenerate "
                 "with suite/build-plugins-data.py.")
    return json.loads(m.group(1))


def tier_problems(marketplace: set[str]) -> list[str]:
    """Cross-reference suite/tiers.yml against the registry. Read from the YAML
    rather than the generated data so a plugin placed in two tiers is caught —
    the projection keeps only the last placement."""
    doc = yaml.safe_load(TIERS_YML.read_text()) or {}
    placements: dict[str, list[str]] = {}
    for tier in doc.get("tiers", []):
        for name in (tier.get("plugins") or {}):
            placements.setdefault(name, []).append(tier["key"])

    problems = []
    for name in sorted(marketplace - set(placements)):
        problems.append(f"{name}: in marketplace.json but not placed in any suite/tiers.yml tier")
    for name in sorted(set(placements) - marketplace):
        problems.append(f"{name}: placed in suite/tiers.yml but not in marketplace.json")
    for name, keys in sorted(placements.items()):
        if len(keys) > 1:
            problems.append(f"{name}: placed in more than one tier ({', '.join(keys)})")
    for tier in doc.get("tiers", []):
        for field in ("key", "label", "blurb"):
            if not tier.get(field):
                problems.append(f"tier {tier.get('key', '?')!r}: missing '{field}'")
        for name, why in (tier.get("plugins") or {}).items():
            if not why:
                problems.append(f"{name}: no rationale for its {tier.get('key')} tier "
                                f"(the chip's tooltip reads from it)")
    return problems


def field_problems(entry: dict) -> list[str]:
    probs = [f"missing '{k}'" for k in REQUIRED if not entry.get(k)]
    if not entry.get("pitch") and not entry.get("what"):
        probs.append("missing 'pitch' or 'what' (the catalog card shows one as its blurb)")
    return probs


def main() -> int:
    marketplace = set(plugin_names())
    grouped = grouped_slugs()
    grouped_set = set(grouped)
    plugins = generated_plugins()
    rendered = set(plugins)
    tier_keys = {t["key"] for t in generated_tiers()}

    errors: list[str] = []

    for name in sorted(marketplace - rendered):
        errors.append(f"{name}: in marketplace.json but not in the generated doc site data "
                      f"(ensure its plugin.yml has a suite: block)")
    for name in sorted(marketplace - grouped_set):
        errors.append(f"{name}: in marketplace.json but not in any doc site GROUPS slug list "
                      f"(add it to a group in docs/index.html)")
    for name in sorted(grouped_set - marketplace):
        errors.append(f"{name}: listed in doc site GROUPS but not in marketplace.json "
                      f"(remove it from GROUPS, or register the plugin)")
    for s in sorted({s for s in grouped if grouped.count(s) > 1}):
        errors.append(f"{s}: listed in more than one doc site group")

    for name in sorted(marketplace & rendered):
        for prob in field_problems(plugins[name]):
            errors.append(f"{name}: {prob}")

    errors.extend(tier_problems(marketplace))

    # The projection half: a tier declared in tiers.yml has to have landed on the
    # plugin's generated entry, keyed to a tier the emitted vocabulary defines.
    for name in sorted(marketplace & rendered):
        tier = plugins[name].get("tier")
        if not tier:
            errors.append(f"{name}: no tier on its generated entry — tiers.yml placed it, "
                          f"but the projection dropped it")
        elif tier not in tier_keys:
            errors.append(f"{name}: generated with tier {tier!r}, which the emitted "
                          f"TIERS vocabulary doesn't define")

    if errors:
        print("check-coverage: doc site representation problems:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"check-coverage: all {len(marketplace)} plugins are grouped, tiered, "
          f"and renderable on the doc site")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
