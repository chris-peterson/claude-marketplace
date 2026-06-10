#!/usr/bin/env bash
# Tally AI-artifact counts (skills / rules / hooks / commands / agents) per
# plugin and record them in suite/artifacts.csv. The file is committed, so its
# git history is the time series. Idempotent per day: re-running on the
# same date replaces that day's rows rather than appending duplicates.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE="$(dirname "$ROOT")"
MANIFEST="$ROOT/.claude-plugin/marketplace.json"
CSV="$ROOT/suite/artifacts.csv"
DATE="${ARTIFACTS_DATE:-$(date -u +%F)}"

# count immediate entries in a dir (each skill is a dir, each rule/hook a file)
count_dir() { if [ -d "$1" ]; then find "$1" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' '; else echo 0; fi; }

[ -f "$CSV" ] || echo "date,plugin,skills,rules,hooks,commands,agents" > "$CSV"

# drop any existing rows for today so the run is idempotent
tmp="$(mktemp)"
grep -v "^$DATE," "$CSV" > "$tmp" || true
mv "$tmp" "$CSV"

jq -r '.plugins[].name' "$MANIFEST" | while read -r name; do
  d="$WORKSPACE/$name"
  echo "$DATE,$name,$(count_dir "$d/skills"),$(count_dir "$d/rules"),$(count_dir "$d/hooks"),$(count_dir "$d/commands"),$(count_dir "$d/agents")" >> "$CSV"
done

echo "recorded $DATE counts in suite/artifacts.csv"
