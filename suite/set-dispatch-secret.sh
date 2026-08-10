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
#
# The prompt is silent, so a truncated paste or a stale value looks identical to
# a good one at the keyboard. Everything is therefore checked against the API
# before any secret is written: the token must authenticate, and it must be able
# to repository_dispatch to this repo. The capability check sends a real dispatch
# with an event type no workflow subscribes to, so it proves the permission
# without triggering a build.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/.claude-plugin/marketplace.json"
owner="$(jq -r '.owner.name' "$MANIFEST")"
target="$(git -C "$ROOT" remote get-url origin | sed -E 's#^(git@github\.com:|https://github\.com/)##; s#\.git$##')"

token="${MARKETPLACE_DISPATCH_TOKEN:-}"
if [ -z "$token" ]; then
  read -rsp "MARKETPLACE_DISPATCH_TOKEN value: " token
  echo
fi

trimmed="${token#"${token%%[![:space:]]*}"}"
trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
if [ "$trimmed" != "$token" ]; then
  echo "note: trimmed surrounding whitespace from the value"
  token="$trimmed"
fi
[ -n "$token" ] || { echo "no token provided" >&2; exit 1; }

case "$token" in
  github_pat_*)            kind="fine-grained PAT" ;;
  ghp_*)                   kind="classic PAT" ;;
  gho_*|ghu_*|ghs_*|ghr_*) kind="GitHub-issued token" ;;
  *)                       kind="unrecognized prefix" ;;
esac
echo "read ${#token} chars, $kind"

err="$(mktemp "${TMPDIR:-/tmp}/dispatch-token-check.XXXXXX")"
trap 'rm -f "$err"' EXIT

if ! login="$(GH_TOKEN="$token" gh api user --jq .login 2>"$err")"; then
  echo "the token does not authenticate: $(cat "$err")" >&2
  echo "generate a fresh PAT and re-run (see suite/README.md, 'The dispatch token')" >&2
  exit 1
fi
expires="$(GH_TOKEN="$token" gh api user --include 2>/dev/null \
  | sed -n 's/^[Gg]ithub-[Aa]uthentication-[Tt]oken-[Ee]xpiration: //p' | tr -d '\r')"
echo "authenticates as $login${expires:+, expires $expires}"

if ! GH_TOKEN="$token" gh api "repos/$target/dispatches" \
  -f event_type=dispatch-token-probe >/dev/null 2>"$err"; then
  echo "the token cannot dispatch to $target: $(cat "$err")" >&2
  echo "grant it Contents: Read and write on $target (fine-grained), or the repo scope (classic)" >&2
  exit 1
fi
echo "can repository_dispatch to $target"

if [ $# -ge 1 ]; then
  names="$1"
else
  names="$(jq -r '.plugins[].name' "$MANIFEST")"
fi

for name in $names; do
  echo "setting MARKETPLACE_DISPATCH_TOKEN on $owner/$name"
  printf '%s' "$token" | gh secret set MARKETPLACE_DISPATCH_TOKEN --repo "$owner/$name"
done
