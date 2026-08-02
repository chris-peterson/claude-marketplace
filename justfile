docs:
    docsify serve docs --open

sync:
    bash suite/sync.sh

plugins-data:
    python3 suite/build-plugins-data.py

deps:
    python3 suite/build-deps-data.py

specs-data:
    python3 suite/build-specs-data.py

check-coverage:
    python3 suite/check-coverage.py

record-artifacts:
    python3 suite/record-artifacts.py

artifacts-data:
    python3 suite/build-artifacts-data.py

seed-artifacts:
    python3 suite/seed-artifacts-history.py

# record-artifacts is deliberately absent: it writes the committed log from
# whatever branch each sibling checkout is on. CI owns it (deploy-docs.yml).
build: sync plugins-data deps specs-data artifacts-data check-coverage

test:
    cd suite && python3 -m unittest

set-dispatch-secret:
    bash suite/set-dispatch-secret.sh
