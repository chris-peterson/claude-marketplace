#!/usr/bin/env python3
"""Project each plugin's declared dependencies → docs/deps.json (the dependency
graph the doc site's interop view reads).

Edges are *declared* in each plugin.yml (`suite.dependencies`, a list of
`{name, required}`), never discovered. Introducing a dependency is an intentional
act, so deps.json is a direct projection of the declared graph — no code scan, no
drift heuristic. docs/deps.json is ephemeral — regenerated each deploy, not committed.
"""
import json

from _common import ROOT, load_plugin, plugin_names

TARGET = ROOT / "docs" / "deps.json"


def main() -> int:
    names = plugin_names()
    edges = []
    for name in names:
        spec = load_plugin(name) or {}
        for dep in (spec.get("suite") or {}).get("dependencies") or []:
            edges.append({"from": name, "to": dep["name"],
                          "required": bool(dep.get("required", False)),
                          "reason": dep.get("reason", "")})
    TARGET.write_text(json.dumps({"nodes": names, "edges": edges}, indent=2) + "\n")
    print(f"wrote {TARGET.relative_to(ROOT)} — {len(edges)} declared edge(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
