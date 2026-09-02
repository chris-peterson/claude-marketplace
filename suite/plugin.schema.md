# `plugin.yml` schema

> How a plugin describes *itself*. How it talks to its *siblings* is
> [`authoring/plugin-contract.md`](../authoring/plugin-contract.md).

Each bridge.ai plugin repo carries a `plugin.yml` at its root — the **single
source of truth** for that plugin's descriptor. It projects into three targets:

- **`.claude-plugin/plugin.json`** — generated in the plugin repo by `shipyard
  gen-plugin-json`; Claude Code reads the committed file at install.
- **the marketplace doc site** — the `suite:` block, consumed by
  `suite/build-plugins-data.py` to generate `docs/plugins.js`.
- **the `marketplace.json` entry** — the `marketplace:` block, projected by
  `shipyard gen-marketplace-json` in the marketplace repo.

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
| `marketplace.relevance` | marketplace entry | Signals that make Claude Code suggest this plugin — see [Suggestions](#suggestions-and-hard-dependencies). Omit if none fit. |
| `dependencies` | plugin.json | Plugins Claude Code installs alongside this one — see [Suggestions](#suggestions-and-hard-dependencies). Not `suite.dependencies`. |
| `suite.*` | doc site | Presentation block — keys match the doc site's `PLUGINS` object verbatim (see below). |
| `events.publishes` | the event catalog | Events this plugin announces, declared in full: bare `key`, `when` prose, `emitted_by`, and `fields`. See [the interop contract](../authoring/plugin-contract.md#declaring-events). |
| `events.subscribes` | the event catalog | Events this plugin reacts to: fully-qualified `key`, `handled_by`, `reason`. A consumer names the dependency, never the fields — N consumers restating one schema is N copies that drift. |

Every field above projects to something published, so its prose is read by
someone who has never seen the plugin. Keep a plugin's internal vocabulary out
of it: a spec requirement ID (`PROV-07`) names nothing a catalog reader can
resolve, and the catalog is where it lands beside every other plugin's. Say what
the thing gets the user instead.

## The `suite:` block (doc site presentation)

Keys mirror the doc site's `PLUGINS` entry so the projection is a direct YAML→JSON
dump (`suite/build-plugins-data.py`):

- `group` — the capability group this plugin belongs to, as a **slug**: `safety` / `bearings` / `waypoints` / `record`. The display label lives in the doc site's `GROUPS` (so relabeling never touches a spoke); the same slug keys the page anchors (`#g-<slug>`) and the accent CSS.
- `cli` (bool) — has a CLI entrypoint. The card marks it, and links the mark to the plugin's command reference at `/cli` where its `plugin.yml` also carries a top-level `cli:` block, which is what makes shipyard record the grammar and render that page. The link is merged in by `build-plugins-data.py` as `reference`; don't declare it.
- `gloss`, `pitch`, `what` — the nautical gloss, the hook, and the full description.
- `cmds` — list of `[command, description]` pairs.
- `describe` — one-line descriptions for the plugin's artifacts, as a map of `<category>: <artifact-name>: "<what it's for>"` (categories: `skills` / `rules` / `hooks` / `commands` / `agents`). Surfaced as tooltips in the doc site — on each artifact chip in the catalog card's expander, and (for `hooks`) on the plugin's interop-radar node. The artifact *names* are still derived from `suite/artifacts.csv` (never declared); `describe` only supplies copy for names that exist. A name with no `describe` entry renders without a tooltip; a `describe` entry for a name not in the log is simply unused.
- `activations` — what triggers this plugin, as a list from `user` (slash commands / keyword skills), `agent` (reacts to the agent's tool calls), and `session` (acts at session start — ambient rules, autoupdate). Drives the interop radar's pulse flares: a node flares on the agent pulse if it lists `agent`, the user pulse if it lists `user` (`session` is declared but doesn't pulse). Omit for the `[user]` default.
- `examples` / `session` — structured session-playback frames (see an existing migrated plugin for the frame shapes).

## Suggestions and hard dependencies

Two blocks reach Claude Code and nothing else, and Claude Code reports on
neither: a shape it doesn't recognize is ignored at load time, so the plugin
quietly does less than its owner wrote. shipyard rejects those at projection.
[Suggestions and dependencies](https://chris-peterson.github.io/shipyard/#/suggestions-and-dependencies) is the reference; the two traps worth knowing
before you open `plugin.yml`:

**`relevance` goes under `marketplace:`**, because the marketplace entry is where
Claude Code reads it. It names a `topic` and at least one signal (`cwd`, `cli`,
`hosts`, `filesRead`, `manifestDeps`). Signals earn their keep by being narrow —
a plugin surfaces at most once every three sessions, and `filesRead` over
`**/CLAUDE.md` fires in nearly all of them. Nothing surfaces at all until an
administrator allowlists this marketplace in managed settings'
`pluginSuggestionMarketplaces`.

**`dependencies` is top-level, and is not `suite.dependencies`.** The top-level
list is hard: Claude Code installs those plugins with this one, enabling this
enables them, and this plugin is disabled while one is missing. `suite.dependencies`
is the doc site's graph of preferred backends and optional collaborators — soft
edges that install nothing and disable nothing. A preferred diff backend belongs
in the second; declaring it in the first installs a second plugin on everyone.

## Not in `plugin.yml`

Derived data is computed, never declared, so it can't drift:

- **artifact counts** — tracked from each repo's git state by `suite/record-artifacts.py` (the rolling `suite/artifacts.csv` log).
- **accent color** — derived from the plugin's `group`: the doc site's `GROUPS` defines the per-group Dracula token (lightened a step per same-group sibling), so the accent is never declared per plugin.
