# `plugin.yml` schema

Each bridge.ai plugin repo carries a `plugin.yml` at its root — the **single
source of truth** for that plugin's descriptor. It projects into three targets:

- **`.claude-plugin/plugin.json`** — generated in the plugin repo by its
  `scripts/gen-plugin-json.py`; Claude Code reads the committed file at install.
- **the marketplace doc site** — the `suite:` block, consumed by
  `suite/build-plugins-data.py` to generate `docs/plugins.js`.
- **the `marketplace.json` entry** (planned) — the `marketplace:` block.

Authoring rule: edit `plugin.yml`, never the generated `plugin.json`.

## Fields

| Field | Projects to | Notes |
|---|---|---|
| `name` | plugin.json, doc site key | Matches the repo/dir name. |
| `version` | plugin.json | **Authoritative here.** Release tooling bumps this; the tag is `v<version>`. |
| `description` | plugin.json, marketplace | One line. |
| `author` | plugin.json | Plain string; projected to `{ "name": ... }`. Omit if none. |
| `repository` | plugin.json | Repo URL. Omit if none. |
| `icon` | plugin.json | Repo-relative path to the mark. Omit if none. |
| `license` | plugin.json | e.g. `MIT`. |
| `keywords` | plugin.json | List. |
| `marketplace.category` | marketplace entry | e.g. `development`, `security`. |
| `marketplace.homepage` | marketplace entry | Hosted docs URL. |
| `suite.*` | doc site | Presentation block — keys match the doc site's `PLUGINS` object verbatim (see below). |

## The `suite:` block (doc site presentation)

Keys mirror the doc site's `PLUGINS` entry so the projection is a direct YAML→JSON
dump (`suite/build-plugins-data.py`):

- `group` — the capability group this plugin belongs to, as a **slug**: `safety` / `bearings` / `waypoints` / `record`. The display label lives in the doc site's `GROUPS` (so relabeling never touches a spoke); the same slug keys the page anchors (`#g-<slug>`) and the accent CSS.
- `cli` (bool) — has a CLI entrypoint.
- `gloss`, `pitch`, `what` — the nautical gloss, the hook, and the full description.
- `cmds` — list of `[command, description]` pairs.
- `describe` — one-line descriptions for the plugin's artifacts, as a map of `<category>: <artifact-name>: "<what it's for>"` (categories: `skills` / `rules` / `hooks` / `commands` / `agents`). Surfaced as tooltips in the doc site — on each artifact chip in the catalog card's expander, and (for `hooks`) on the plugin's interop-radar node. The artifact *names* are still derived from `suite/artifacts.csv` (never declared); `describe` only supplies copy for names that exist. A name with no `describe` entry renders without a tooltip; a `describe` entry for a name not in the log is simply unused.
- `activations` — what triggers this plugin, as a list from `user` (slash commands / keyword skills), `agent` (reacts to the agent's tool calls), and `session` (acts at session start — ambient rules, autoupdate). Drives the interop radar's pulse flares: a node flares on the agent pulse if it lists `agent`, the user pulse if it lists `user` (`session` is declared but doesn't pulse). Omit for the `[user]` default.
- `examples` / `session` — structured session-playback frames (see an existing migrated plugin for the frame shapes).

## Not in `plugin.yml`

Derived data is computed, never declared, so it can't drift:

- **artifact counts** — tracked from each repo's git state by `suite/record-artifacts.py` (the rolling `suite/artifacts.csv` log).
- **accent color** — derived from the plugin's `group`: the doc site's `GROUPS` defines the per-group Dracula token (lightened a step per same-group sibling), so the accent is never declared per plugin.
