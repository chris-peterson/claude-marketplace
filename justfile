# Serve docs/ with docsify and open a browser.
docs:
    docsify serve docs --open

# Clone or fast-forward the sibling plugin repos on the plugins.yml roster,
# plus the plugins the groups have retired — the growth view reads their history
# out of their checkouts too.
sync:
    bash suite/sync.sh

# CI's job, for the reason noted on `build`; this recipe is for a deliberate run.
# Generate .claude-plugin/marketplace.json from plugins.yml + each plugin.yml.
marketplace:
    shipyard gen-marketplace-json

# Generate docs/plugins.js — the catalog's groups and per-plugin copy.
plugins-data:
    shipyard gen-plugins-js

# Generate docs/specs.json — the spec browser's tree, from each SPEC.md.
specs-data:
    python3 suite/build-specs-data.py

# Generate docs/events.json — the interop catalog, pairing each published key
# with the plugins that subscribe to it.
events-data:
    shipyard gen-events-json

# Append a change-point row to suite/artifacts.csv. CI's job — see the note on build.
record-artifacts:
    python3 suite/record-artifacts.py

# Generate docs/artifacts.json — the growth view's series, changelog, and releases.
artifacts-data:
    shipyard gen-artifacts-json

# Re-seed suite/artifacts.csv from each plugin repo's git history (one-time).
seed-artifacts:
    python3 suite/seed-artifacts-history.py

# record-artifacts and marketplace are deliberately absent: both write a
# committed file from whatever branch each sibling checkout happens to be on, so
# a local run would publish unmerged work. CI owns them (deploy-docs.yml).
# Regenerate every docs/ data file.
build: sync plugins-data specs-data events-data artifacts-data

# Run the suite/ unit tests.
test:
    cd suite && python3 -m unittest

# Fan MARKETPLACE_DISPATCH_TOKEN out to every plugin repo (prompts for the PAT).
set-dispatch-secret:
    bash suite/set-dispatch-secret.sh
