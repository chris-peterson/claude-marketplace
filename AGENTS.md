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
  `plugins.yml` also declares the two things only the marketplace knows: the
  `artifacts:` log the growth view plots, and the catalog's `groups:` — each
  group's order, accent token, and label, plus the plugins it has `retired:`,
  which have no roster entry left to read from.

## Plugin authoring (`authoring/`)

Contracts a plugin repo has to hold up, as opposed to the tooling that reads
them. [`authoring/plugin-contract.md`](authoring/plugin-contract.md) is how one
plugin tells another that something happened: a routing key on stdout, matched
by the sibling's `PostToolUse` hook, with no dispatcher between them. Its key
table is the suite's only shared record of who announces what, and a key belongs
in it once both sides agree, not once it first fires.

## Suite toolkit (`suite/`)

The bridge.ai suite is maintained by reading the sibling plugin repos (cloned by
`suite/sync.sh` from the `plugins.yml` roster). Each plugin's `plugin.yml` is its
canonical descriptor (see `suite/plugin.schema.md`). [`suite/README.md`](suite/README.md)
is the toolkit reference, including how to release a plugin and set up its
dispatch token. The scripts:

- `record-artifacts.py` — append a change-point row to `suite/artifacts.csv` (the committed rolling log) when a plugin's artifact set changes. **CI writes this log, not you**: it reads each sibling's checked-out branch, so a local run records unmerged work as shipped — which is why `just build` omits it. `seed-artifacts-history.py` is the one-time bootstrap from each repo's git history.
- `build-specs-data.py` — project each sibling's `SPEC.md` into the spec browser's tree → `docs/specs.json`.
- `sync.sh` — clone or fast-forward the roster plus the plugins the groups have retired (`shipyard roster --include-retired`), since the growth view reads a retired plugin's history out of its checkout too.

**The doc site's own data files come from shipyard**, which reads this repo as an
*aggregator* (`plugins.yml`) and the siblings as its spokes: `shipyard
gen-plugins-js` writes `docs/plugins.js` (the catalog's groups and per-plugin
copy), `shipyard gen-events-json` writes `docs/events.json` (each published
interop key paired with the plugins that subscribe to it, from both sides'
`events:` blocks), and `shipyard gen-artifacts-json` writes `docs/artifacts.json`
(the growth view's series, changelog, and releases). A change to any of those
projections is a change in that repo. `just build` runs all three, so a local
build needs a `shipyard` new enough to have them.

## Structure

- `docs/index.html` — the landing page: inline CSS/JS, no framework, home view +
  per-plugin views via hash routing (`#/<plugin>`). The one thing it takes from
  outside is the family's chrome, by absolute path from the hub at
  `chris-peterson.github.io`: `/css/tokens.css` (palette and typefaces),
  `/css/titlebar.css`, and `/js/docsify-shared.js` for `initTitlebar()`. That's
  what gives this page the same header, breadcrumb, blog link, and day/night
  toggle as every plugin's docsify site. `specs.html` and `events.html` take the
  same three.
  - **Local preview needs both trees**, since those paths resolve at the domain
    root: serve a directory with the hub's `docs/` at the root and this `docs/`
    under `claude-marketplace/`. Serving this `docs/` alone leaves the page
    unstyled above the fold and dark-only.
  - Colors resolve through the tokens, so **don't reintroduce a literal**: a
    chart that bakes one at draw time won't follow the toggle. The two chart
    blocks redraw on the `themechange` event the toggle fires.
- `docs/events.html` — the interop catalog: one card per announcement, showing
  the publisher, the key, when it fires, its body fields, and who subscribes.
  Reads `docs/events.json`, and `docs/plugins.js` for the group each plugin is
  in, which is where a card's accent comes from. A key with only one end renders
  with that end dashed — subscribed-with-no-publisher leads the page, since it
  is always a defect.
- `docs/favicon.svg` — the bridge.ai mark (also the nav/footer mark, inline).
- `issue.md` — roadmap note for a possible next pass.
- The former docsify files (`docs/README.md`, `relationships.md`, `_sidebar.md`)
  are kept but **unlinked** — to fold into the doc site later.

## Conventions

- **Per-plugin copy has one source**: each plugin's `plugin.yml` (the `suite:`
  block). `shipyard gen-plugins-js` generates the `PLUGINS` object into
  `docs/plugins.js`, which `index.html` loads — edit gloss/what/commands in the
  plugin's `plugin.yml`, never in `index.html` or `plugins.js`.
- **Adding a plugin takes one edit here**: its name on `plugins.yml`'s roster,
  in the position the catalog should list it. Which group its card lands in is
  the plugin's own `plugin.yml` (`suite: group:`), naming one of the `groups:`
  keys this repo declares — shipyard refuses a group name no entry declares, so
  a plugin can't reach the catalog ungrouped.
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
