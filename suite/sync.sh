#!/usr/bin/env bash
# Sync the sibling plugin repos on the roster into the workspace (the directory
# that contains this repo). Clones what's missing, fast-forwards what's present.
# Runs locally (`just sync`) and in the marketplace deploy CI.
#
# The roster comes from plugins.yml, not from the manifest this repo publishes:
# marketplace.json is generated *from* the synced plugins, so reading it here
# would make the clone step depend on its own output. `shipyard roster` resolves
# plugins.yml's URL template with nothing on disk, which is what breaks that.
#
# --include-retired adds the plugins the groups have retired. Nothing the
# marketplace publishes names them, but the growth view plots what they shipped,
# and it reads that out of their checkouts like any other plugin's.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(dirname "$ROOT")"

shipyard roster --include-retired --root "$ROOT" | while IFS=$'\t' read -r name url; do
  dest="$WORKSPACE/$name"
  if [ -d "$dest/.git" ]; then
    echo "pull  $name"
    git -C "$dest" pull --ff-only --quiet || echo "  (skip: $name has local divergence)"
  else
    echo "clone $name"
    git clone --quiet "$url" "$dest"
  fi
done
