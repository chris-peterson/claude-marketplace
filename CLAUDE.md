# claude-marketplace

chris-peterson's Claude Code plugin marketplace, plus the **bridge.ai** landing
page that showcases the suite.

## Build & serve

- **Live site:** GitHub Pages serves `docs/` on push to `main`
  (`.github/workflows/deploy-docs.yml`). Merging to `main` = deploying.
- **Local preview:** `python3 -m http.server` from `docs/`, then open
  `index.html`. (Hash routing + the relative favicon want HTTP, not `file://`.)
- **Plugin registry:** `.claude-plugin/marketplace.json` lists the published
  plugins. Each plugin lives in its own repo (`github.com/chris-peterson/<name>`).

## Structure

- `docs/index.html` — the landing page, a **single-file SPA** (inline CSS/JS,
  no framework). Home view + per-plugin views via hash routing (`#/<plugin>`).
- `docs/favicon.svg` — the bridge.ai mark (also the nav/footer mark, inline).
- `issue.md`, `issue-spa.md` — roadmap notes for the next passes.
- The former docsify files (`docs/README.md`, `relationships.md`, `_sidebar.md`)
  are kept but **unlinked** — to fold into the SPA later (see `issue-spa.md`).

## Conventions

- **Per-plugin copy has one source**: the `PLUGINS` object in `docs/index.html`.
  The catalog cards (`#catalog`) and the plugin views both render from it — edit
  gloss/what/commands there, not in generated markup.
- **Verify plugin behavior against the real skills** before describing it —
  read `../<plugin>/skills/*/SKILL.md`, don't guess.
- **Namespace every command** as `plugin:skill` (e.g. `/anchor:commit`,
  `/logbook:note`), in both the command lists and the example sessions.
- **Colors come from the Dracula CSS tokens** in `:root` — no hardcoded hex in
  layout/UI (favicon/mark SVGs are the exception).
- This is a **public repo** — no internal hosts, private paths, or personal
  references in committed files.
