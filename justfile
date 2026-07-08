docs:
    docsify serve docs --open

sync:
    bash suite/sync.sh

spa-data:
    python3 suite/build-spa-data.py

deps:
    python3 suite/build-deps-data.py

check-coverage:
    python3 suite/check-spa-coverage.py

record-artifacts:
    python3 suite/record-artifacts.py

artifacts-data:
    python3 suite/build-artifacts-data.py

seed-artifacts:
    python3 suite/seed-artifacts-history.py

build: sync spa-data deps record-artifacts artifacts-data check-coverage

test:
    cd suite && python3 -m unittest

set-dispatch-secret:
    bash suite/set-dispatch-secret.sh
