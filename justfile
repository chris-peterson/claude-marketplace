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

# record per-plugin artifact counts into suite/artifacts.csv (committed time series)
counts:
    bash suite/count-artifacts.sh

# full aggregation: sync siblings, then build all generated outputs
build: sync spa-data deps counts check-coverage

# set/rotate the MARKETPLACE_DISPATCH_TOKEN secret across the plugin repos
set-dispatch-secret:
    bash suite/set-dispatch-secret.sh
