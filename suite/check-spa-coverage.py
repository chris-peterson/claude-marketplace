#!/usr/bin/env python3
"""Fail the build if a plugin isn't properly represented on the bridge.ai SPA.

A plugin can silently break the landing page (docs/index.html) three ways, none
visible until someone clicks:

1. Absent from the generated PLUGINS data — the build never produced a card for
   it (e.g. its plugin.yml is missing or has no suite: block).
2. Not in a GROUPS slug list — the catalog renders only grouped slugs, so the
   data exists but no card is shown.
3. Missing a field the renderer reads unguarded — the per-plugin view
   (#/<slug>) dereferences `what`, `cmds`, and a `session`/`examples`
   walkthrough; a plugin without them throws and the detail page goes blank.

This runs after `build-spa-data.py` (it reads the generated docs/plugins.js) and
cross-references marketplace.json and the SPA GROUPS, failing loudly so the
omission never deploys. Wired into CI and `just build`.
"""
import json
import re
import sys

from _common import ROOT, plugin_names

INDEX = ROOT / "docs" / "index.html"
PLUGINS_JS = ROOT / "docs" / "plugins.js"

# Fields the SPA per-plugin view reads without a presence guard (docs/index.html).
REQUIRED = ["group", "what", "cmds"]


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
    if not entry.get("session") and not entry.get("examples"):
        probs.append("missing 'session' or 'examples' (the per-plugin view needs a walkthrough)")
    return probs


def main() -> int:
    marketplace = set(plugin_names())
    grouped = grouped_slugs()
    grouped_set = set(grouped)
    plugins = generated_plugins()
    rendered = set(plugins)

    errors: list[str] = []

    for name in sorted(marketplace - rendered):
        errors.append(f"{name}: in marketplace.json but not in the generated SPA data "
                      f"(ensure its plugin.yml has a suite: block)")
    for name in sorted(marketplace - grouped_set):
        errors.append(f"{name}: in marketplace.json but not in any SPA GROUPS slug list "
                      f"(add it to a group in docs/index.html)")
    for name in sorted(grouped_set - marketplace):
        errors.append(f"{name}: listed in SPA GROUPS but not in marketplace.json "
                      f"(remove it from GROUPS, or register the plugin)")
    for s in sorted({s for s in grouped if grouped.count(s) > 1}):
        errors.append(f"{s}: listed in more than one SPA group")

    for name in sorted(marketplace & rendered):
        for prob in field_problems(plugins[name]):
            errors.append(f"{name}: {prob}")

    if errors:
        print("check-spa-coverage: SPA representation problems:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"check-spa-coverage: all {len(marketplace)} plugins are grouped and renderable on the SPA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
