#!/usr/bin/env bash
# Sync the sibling plugin repos listed in marketplace.json into the workspace
# (the directory that contains this repo). Clones what's missing, fast-forwards
# what's present. marketplace.json is the single source of "what plugins exist
# and where." Runs locally (`just sync`) and in the marketplace deploy CI.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(dirname "$ROOT")"
MANIFEST="$ROOT/.claude-plugin/marketplace.json"

jq -r '.plugins[] | "\(.name)|\(.source.url)"' "$MANIFEST" | while IFS='|' read -r name url; do
  dest="$WORKSPACE/$name"
  if [ -d "$dest/.git" ]; then
    echo "pull  $name"
    git -C "$dest" pull --ff-only --quiet || echo "  (skip: $name has local divergence)"
  else
    echo "clone $name"
    git clone --quiet "$url" "$dest"
  fi
done
