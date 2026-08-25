# claude-marketplace

chris-peterson's Claude Code plugin marketplace, plus the **bridge.ai** landing
page that showcases the suite.

## Build & serve

- **Live site:** GitHub Pages serves `docs/` (`.github/workflows/deploy-docs.yml`).
  The rebuild is **event-based** — a plugin release fires a `repository_dispatch`
  (`plugin-released`); own-repo pushes and `workflow_dispatch` also rebuild. The
  workflow syncs the siblings, regenerates `marketplace.json`, then runs the
  `suite/` scripts (generate `docs/plugins.js` → record counts) before uploading
  `docs/`.
- **Local preview:** run `just build` (or at least `just plugins-data`) first to
  generate `docs/plugins.js`, then `python3 -m http.server` from `docs/` and open
  `index.html`. (Hash routing + the relative favicon want HTTP, not `file://`;
  `plugins.js` is git-ignored, so the doc site is blank without that build.)
- **Plugin registry:** `plugins.yml` is the roster — this marketplace's identity,
  which plugins it ships, and the order they list in. `shipyard
  gen-marketplace-json` projects it plus each plugin's own `plugin.yml` into
  `.claude-plugin/marketplace.json`, which is generated and committed. Each
  plugin lives in its own repo (`github.com/chris-peterson/<name>`).
  **Edit `plugins.yml`, never `marketplace.json`** — CI regenerates it and would
  overwrite a hand edit. Everything *about* a plugin (description, author,
  category, homepage, relevance) comes from that plugin's `plugin.yml`.

## Suite toolkit (`suite/`)

The bridge.ai suite is maintained by reading the sibling plugin repos (cloned by
`suite/sync.sh` from the `plugins.yml` roster). Each plugin's `plugin.yml` is its
canonical descriptor (see `suite/plugin.schema.md`). [`suite/README.md`](suite/README.md)
is the toolkit reference, including how to release a plugin and set up its
dispatch token. The scripts:

- `build-plugins-data.py` — per-plugin doc site content from each `plugin.yml` → `docs/plugins.js`.
- `record-artifacts.py` — append a change-point row to `suite/artifacts.csv` (the committed rolling log) when a plugin's artifact set changes. **CI writes this log, not you**: it reads each sibling's checked-out branch, so a local run records unmerged work as shipped — which is why `just build` omits it. `seed-artifacts-history.py` is the one-time bootstrap from each repo's git history.
- `build-artifacts-data.py` — project `suite/artifacts.csv` into the growth view's series + changelog → `docs/artifacts.json`.
- `check-coverage.py` — fails the build if a `marketplace.json` plugin isn't placed in a doc site `GROUPS` slug list (or vice versa). Runs first in CI and in `just build`.

## Structure

- `docs/index.html` — the landing page: inline CSS/JS, no framework, home view +
  per-plugin views via hash routing (`#/<plugin>`). The one thing it takes from
  outside is the family's chrome, by absolute path from the hub at
  `chris-peterson.github.io`: `/css/tokens.css` (palette and typefaces),
  `/css/titlebar.css`, and `/js/docsify-shared.js` for `initTitlebar()`. That's
  what gives this page the same header, breadcrumb, blog link, and day/night
  toggle as every plugin's docsify site. `specs.html` takes the same three.
  - **Local preview needs both trees**, since those paths resolve at the domain
    root: serve a directory with the hub's `docs/` at the root and this `docs/`
    under `claude-marketplace/`. Serving this `docs/` alone leaves the page
    unstyled above the fold and dark-only.
  - Colors resolve through the tokens, so **don't reintroduce a literal**: a
    chart that bakes one at draw time won't follow the toggle. The two chart
    blocks redraw on the `themechange` event the toggle fires.
- `docs/favicon.svg` — the bridge.ai mark (also the nav/footer mark, inline).
- `issue.md` — roadmap note for a possible next pass.
- The former docsify files (`docs/README.md`, `relationships.md`, `_sidebar.md`)
  are kept but **unlinked** — to fold into the doc site later.

## Conventions

- **Per-plugin copy has one source**: each plugin's `plugin.yml` (the `suite:`
  block). `suite/build-plugins-data.py` generates the `PLUGINS` object into
  `docs/plugins.js`, which `index.html` loads — edit gloss/what/commands in the
  plugin's `plugin.yml`, never in `index.html` or `plugins.js`.
- **Adding a plugin takes two edits**: add its name to `plugins.yml`, and add
  its slug to a `GROUPS` group in `docs/index.html` — the catalog renders only
  grouped slugs, so a plugin on the roster alone has data but no card.
  `suite/check-coverage.py` enforces this (CI + `just build`).
- **Suggestions and hard dependencies live in the plugin, not here.** A plugin's
  `marketplace.relevance:` block asks Claude Code to suggest it to matching
  sessions; a top-level `dependencies:` list names plugins Claude Code installs
  alongside it. Both are declared in that plugin's `plugin.yml` and validated by
  shipyard as it generates the manifest — see
  [Suggestions and dependencies](https://chris-peterson.github.io/shipyard/#/suggestions-and-dependencies).
  Neither is the doc site's `suite.dependencies:` graph, whose edges are soft and
  install nothing.
- **Verify plugin behavior against the real skills** before describing it —
  read `../<plugin>/skills/*/SKILL.md`, don't guess.
- **Namespace every command** as `plugin:skill` (e.g. `/anchor:commit`,
  `/tack:start`), in both the command lists and the example sessions.
- **Colors come from the Dracula CSS tokens** in `:root` — no hardcoded hex in
  layout/UI (favicon/mark SVGs are the exception).
- This is a **public repo** — no internal hosts, private paths, or personal
  references in committed files.
