#!/usr/bin/env python3
"""Fail the build if a plugin isn't properly represented on the bridge.ai doc site.

A plugin can silently break the landing page (docs/index.html) three ways, none
visible until someone clicks:

1. Absent from the generated PLUGINS data — the build never produced a card for
   it (e.g. its plugin.yml is missing or has no suite: block).
2. Not in a GROUPS slug list — the catalog renders only grouped slugs, so the
   data exists but no card is shown.
3. Missing a field the catalog card needs — it declares its `group` slug and
   dereferences a `pitch`/`what` blurb (`p.pitch || p.what`) unguarded; a
   plugin without them can't render a card. (The in-hub per-plugin detail view
   was removed in the descriptor migration — #/<slug> now redirects to each
   plugin's own docs site — so `cmds` and the `session`/`examples` walkthrough
   it used to read are no longer required.)

This runs after `build-spa-data.py` (it reads the generated docs/plugins.js) and
cross-references marketplace.json and the doc site GROUPS, failing loudly so the
omission never deploys. Wired into CI and `just build`.
"""
import json
import re
import sys

from _common import ROOT, plugin_names

INDEX = ROOT / "docs" / "index.html"
PLUGINS_JS = ROOT / "docs" / "plugins.js"

# Fields a plugin must declare to render a catalog card (docs/index.html): its
# `group` slug, and a blurb the card shows as `pitch || what`. The per-plugin
# detail view was removed in the descriptor migration (#/<slug> redirects to the
# plugin's own docs site), so `cmds` and the `session`/`examples` walkthrough it
# read are no longer required.
REQUIRED = ["group"]


def grouped_slugs() -> list[str]:
    block = re.search(r"const GROUPS\s*=\s*\[(.*?)\];", INDEX.read_text(), re.S)
    if not block:
        sys.exit("check-spa-coverage: could not find the GROUPS array in docs/index.html")
    slugs: list[str] = []
    for arr in re.findall(r"slugs:\s*\[([^\]]*)\]", block.group(1)):
        slugs.extend(re.findall(r'"([^"]+)"', arr))
    return slugs


def generated_plugins() -> dict:
    if not PLUGINS_JS.exists():
        sys.exit("check-spa-coverage: docs/plugins.js not found — run suite/build-spa-data.py first")
    m = re.search(r"const PLUGINS\s*=\s*(\{.*\});", PLUGINS_JS.read_text(), re.S)
    if not m:
        sys.exit("check-spa-coverage: could not parse PLUGINS from docs/plugins.js")
    return json.loads(m.group(1))


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

    if errors:
        print("check-spa-coverage: doc site representation problems:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"check-spa-coverage: all {len(marketplace)} plugins are grouped and renderable on the doc site")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
