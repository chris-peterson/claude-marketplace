# claude-marketplace

chris-peterson's Claude Code plugin marketplace, plus the **bridge.ai** landing
page that showcases the suite.

## Build & serve

- **Live site:** GitHub Pages serves `docs/` (`.github/workflows/deploy-docs.yml`).
  The rebuild is **event-based** — a plugin release fires a `repository_dispatch`
  (`plugin-released`); own-repo pushes and `workflow_dispatch` also rebuild. The
  workflow runs the `suite/` scripts (sync siblings → generate `docs/plugins.js`
  + `docs/deps.json` → record counts) before uploading `docs/`.
- **Local preview:** run `just build` (or at least `just spa-data`) first to
  generate `docs/plugins.js`, then `python3 -m http.server` from `docs/` and open
  `index.html`. (Hash routing + the relative favicon want HTTP, not `file://`;
  `plugins.js`/`deps.json` are git-ignored, so the SPA is blank without that build.)
- **Plugin registry:** `.claude-plugin/marketplace.json` lists the published
  plugins. Each plugin lives in its own repo (`github.com/chris-peterson/<name>`).

## Suite toolkit (`suite/`)

The bridge.ai suite is maintained by reading the sibling plugin repos (cloned by
`suite/sync.sh` from `marketplace.json`). Each plugin's `plugin.yml` is its
canonical descriptor (see `suite/plugin.schema.md`). [`suite/README.md`](suite/README.md)
is the toolkit reference, including how to release a plugin and set up its
dispatch token. The scripts:

- `build-spa-data.py` — per-plugin SPA content from each `plugin.yml` → `docs/plugins.js`.
- `count-artifacts.sh` — skills/rules/hooks/commands/agents tallies → `suite/artifacts.csv` (committed; git history is the time series).
- `trace-deps.py` — heuristic cross-plugin dependency edges → `docs/deps.json`, cross-checked against declared `soft_deps`.
- `spa-legacy.json` — verbatim snapshot of the original inline SPA content; supplies ordering + fallback for plugins not yet migrated to `plugin.yml`. Dropped once all plugins have one.

## Structure

- `docs/index.html` — the landing page, a **single-file SPA** (inline CSS/JS,
  no framework). Home view + per-plugin views via hash routing (`#/<plugin>`).
- `docs/favicon.svg` — the bridge.ai mark (also the nav/footer mark, inline).
- `issue.md`, `issue-spa.md` — roadmap notes for the next passes.
- The former docsify files (`docs/README.md`, `relationships.md`, `_sidebar.md`)
  are kept but **unlinked** — to fold into the SPA later (see `issue-spa.md`).

## Conventions

- **Per-plugin copy has one source**: each plugin's `plugin.yml` (the `suite:`
  block). `suite/build-spa-data.py` generates the `PLUGINS` object into
  `docs/plugins.js`, which `index.html` loads — edit gloss/what/commands in the
  plugin's `plugin.yml`, never in `index.html` or `plugins.js`. (Plugins not yet
  migrated still come from `suite/spa-legacy.json`.)
- **Verify plugin behavior against the real skills** before describing it —
  read `../<plugin>/skills/*/SKILL.md`, don't guess.
- **Namespace every command** as `plugin:skill` (e.g. `/anchor:commit`,
  `/logbook:note`), in both the command lists and the example sessions.
- **Colors come from the Dracula CSS tokens** in `:root` — no hardcoded hex in
  layout/UI (favicon/mark SVGs are the exception).
- This is a **public repo** — no internal hosts, private paths, or personal
  references in committed files.
