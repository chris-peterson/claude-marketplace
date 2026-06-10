# `plugin.yml` schema

Each bridge.ai plugin repo carries a `plugin.yml` at its root — the **single
source of truth** for that plugin's descriptor. It projects into three targets:

- **`.claude-plugin/plugin.json`** — generated in the plugin repo by its
  `scripts/gen-plugin-json.py`; Claude Code reads the committed file at install.
- **the marketplace SPA** — the `suite:` block, consumed by
  `suite/build-spa-data.py` to generate `docs/plugins.js`.
- **the `marketplace.json` entry** (planned) — the `marketplace:` block.

Authoring rule: edit `plugin.yml`, never the generated `plugin.json`.

## Fields

| Field | Projects to | Notes |
|---|---|---|
| `name` | plugin.json, SPA key | Matches the repo/dir name. |
| `version` | plugin.json | **Authoritative here.** Release tooling bumps this; the tag is `v<version>`. |
| `description` | plugin.json, marketplace | One line. |
| `author` | plugin.json | Plain string; projected to `{ "name": ... }`. Omit if none. |
| `repository` | plugin.json | Repo URL. Omit if none. |
| `icon` | plugin.json | Repo-relative path to the mark. Omit if none. |
| `license` | plugin.json | e.g. `MIT`. |
| `keywords` | plugin.json | List. |
| `marketplace.category` | marketplace entry | e.g. `development`, `security`. |
| `marketplace.homepage` | marketplace entry | Hosted docs URL. |
| `suite.*` | SPA | Presentation block — keys match the SPA's `PLUGINS` object verbatim (see below). |

## The `suite:` block (SPA presentation)

Keys mirror the SPA's `PLUGINS` entry so the projection is a direct YAML→JSON
dump (`suite/build-spa-data.py`):

- `ac` — Dracula CSS accent token (e.g. `"--guard"`), not a hardcoded color.
- `group` — capability grouping shown in the catalog (e.g. `stay safe`).
- `cli` (bool) — has a CLI entrypoint.
- `passive` (bool) — runs without explicit invocation.
- `gloss`, `pitch`, `what` — the nautical gloss, the hook, and the full description.
- `cmds` — list of `[command, description]` pairs.
- `soft_deps` — plugins this one references at runtime; cross-checked by `suite/trace-deps.py`.
- `examples` / `session` — structured session-playback frames (see an existing migrated plugin for the frame shapes).

## Not in `plugin.yml`

Derived data is computed, never declared, so it can't drift:

- **artifact counts** — tallied from the repo by `suite/count-artifacts.sh`.
- **discovered dependency edges** — found in code by `suite/trace-deps.py` (then cross-checked against `soft_deps`).
