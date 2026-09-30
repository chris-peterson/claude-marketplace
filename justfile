# What this is, and every recipe there is
[private]
default:
    @echo ""
    @echo "  bridge.ai: chris-peterson's Claude Code plugin marketplace and its doc site"
    @echo ""
    @echo "  New here?   just build    clone the sibling plugins, generate docs/ data"
    @echo "  Then        just docs     serve docs/ and open it"
    @echo ""
    @just --list --unsorted --list-heading '' --list-prefix '    '
    @echo ""
    @echo "  The data recipes read the sibling plugin repos next to this one (just sync)."
    @echo ""

# record-artifacts and marketplace are deliberately absent: both write a
# committed file from whatever branch each sibling checkout happens to be on, so
# a local run would publish unmerged work. CI owns them (deploy-docs.yml).

# Sync the siblings and regenerate every docs/ data file
[group('start here')]
build: sync plugins-data specs-data events-data artifacts-data

# Serve docs/ with docsify and open a browser
[group('start here')]
docs:
    docsify serve docs --open

# Run the suite/ unit tests
[group('start here')]
test:
    cd suite && python3 -m unittest

# The growth view reads the retired plugins' history out of their checkouts too.

# Clone or fast-forward the roster's plugin repos, plus the retired ones
[group('sibling repos')]
sync:
    bash suite/sync.sh

# Fan MARKETPLACE_DISPATCH_TOKEN out to the roster, or one named plugin (prompts for the PAT)
[group('sibling repos')]
set-dispatch-secret name="":
    bash suite/set-dispatch-secret.sh {{name}}

# Generate docs/plugins.js: the catalog's groups and per-plugin copy
[group('generate docs/ data')]
plugins-data:
    shipyard gen-plugins-js

# Generate docs/specs.json: the spec browser's tree, from each SPEC.md
[group('generate docs/ data')]
specs-data:
    python3 suite/build-specs-data.py

# Generate docs/events.json: each published event key and the plugins subscribed to it
[group('generate docs/ data')]
events-data:
    shipyard gen-events-json

# Generate docs/artifacts.json: the growth view's series, changelog, and releases
[group('generate docs/ data')]
artifacts-data:
    shipyard gen-artifacts-json

# Generate .claude-plugin/marketplace.json from plugins.yml and each plugin.yml (CI's job; see build)
[group('CI or one-time')]
marketplace:
    shipyard gen-marketplace-json

# Append a change-point row to suite/artifacts.csv (CI's job; see build)
[group('CI or one-time')]
record-artifacts:
    python3 suite/record-artifacts.py

# Re-seed suite/artifacts.csv from each plugin repo's git history (one-time bootstrap)
[group('CI or one-time')]
seed-artifacts:
    python3 suite/seed-artifacts-history.py
