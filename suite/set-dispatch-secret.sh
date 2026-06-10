#!/usr/bin/env bash
# Fan the MARKETPLACE_DISPATCH_TOKEN secret out to the plugin repos so their
# release workflows can dispatch to this repo. Use it to pre-provision every
# plugin, add a new one, or rotate the token (just re-run with a fresh value).
#
#   bash suite/set-dispatch-secret.sh            # all plugins in marketplace.json
#   bash suite/set-dispatch-secret.sh anchor     # just one repo
#
# The token is read from $MARKETPLACE_DISPATCH_TOKEN or prompted for, and piped
# to gh via stdin — never passed on the command line.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/.claude-plugin/marketplace.json"
owner="$(jq -r '.owner.name' "$MANIFEST")"

token="${MARKETPLACE_DISPATCH_TOKEN:-}"
if [ -z "$token" ]; then
  read -rsp "MARKETPLACE_DISPATCH_TOKEN value: " token
  echo
fi
[ -n "$token" ] || { echo "no token provided" >&2; exit 1; }

if [ $# -ge 1 ]; then
  names="$1"
else
  names="$(jq -r '.plugins[].name' "$MANIFEST")"
fi

for name in $names; do
  echo "setting MARKETPLACE_DISPATCH_TOKEN on $owner/$name"
  printf '%s' "$token" | gh secret set MARKETPLACE_DISPATCH_TOKEN --repo "$owner/$name"
done
