# serve the SPA locally (after `just spa-data` to refresh generated data)
docs:
    docsify serve docs --open

# clone/fast-forward the sibling plugin repos listed in marketplace.json
sync:
    bash suite/sync.sh

# regenerate docs/plugins.js (the SPA's PLUGINS data) from each plugin.yml
spa-data:
    python3 suite/build-spa-data.py

# trace cross-plugin soft dependencies into docs/deps.json
deps:
    python3 suite/trace-deps.py

# fail if any plugin is missing from the SPA catalog or its data (run after spa-data)
check-coverage:
    python3 suite/check-spa-coverage.py

# append a change-point row to suite/artifacts.csv when a plugin's artifacts changed
record-artifacts:
    python3 suite/record-artifacts.py

# project the rolling suite/artifacts.csv into docs/artifacts.json (the growth view)
artifacts-data:
    python3 suite/build-artifacts-data.py

# one-time: (re)bootstrap suite/artifacts.csv from each plugin repo's git history
seed-artifacts:
    python3 suite/seed-artifacts-history.py

# full aggregation: sync siblings, then build all generated outputs
build: sync spa-data deps record-artifacts artifacts-data check-coverage

# set/rotate the MARKETPLACE_DISPATCH_TOKEN secret across the plugin repos
set-dispatch-secret:
    bash suite/set-dispatch-secret.sh
