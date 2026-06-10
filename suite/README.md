# bridge.ai suite toolkit

The marketplace maintains the suite by reading the sibling plugin repos rather
than hand-authoring per-plugin content. Each plugin declares a canonical
`plugin.yml` (see [plugin.schema.md](plugin.schema.md)); these scripts project
and aggregate from it.

| Script | Output | Purpose |
|:---|:---|:---|
| `sync.sh` | sibling checkouts | clone/fast-forward every plugin in `marketplace.json` |
| `build-spa-data.py` | `docs/plugins.js` | per-plugin SPA content from each `plugin.yml` |
| `count-artifacts.sh` | `suite/artifacts.csv` | artifact tallies, committed so git history is the time series |
| `trace-deps.py` | `docs/deps.json` | cross-plugin soft-dependency edges, cross-checked against declared `soft_deps` |

`just build` runs all four. `docs/plugins.js` and `docs/deps.json` are
regenerated each deploy and git-ignored; only `artifacts.csv` is committed.

## Releasing a bridge.ai plugin

A release is a git tag on the plugin repo. The flow:

1. On a branch, bump `version` in the plugin's `plugin.yml` and add a
   `CHANGELOG.md` entry. The pre-commit hook regenerates `plugin.json`.
2. Merge to `main` — `main` is always the latest released state, so a direct
   `claude plugin install <git-url>` (which clones the default branch) gets the
   release.
3. Tag the merge commit `v<version>`. The plugin's `release.yml` verifies
   `plugin.json` is in sync with `plugin.yml`, then sends a `repository_dispatch`
   to this repo, which rebuilds the catalog and redeploys.

### The dispatch token

`release.yml` calls the GitHub API to dispatch *into this repo*, which the
workflow's default `GITHUB_TOKEN` can't do — it's scoped to the plugin's own
repo. So each plugin repo needs a `MARKETPLACE_DISPATCH_TOKEN` secret. Three
roles, only one of them a repo:

| Role | Who/what |
|:---|:---|
| **Owns** the token | the account (`chris-peterson`) — a PAT is an account credential, created in Developer Settings |
| **Stores** it | the **plugin** repo, as the `MARKETPLACE_DISPATCH_TOKEN` Actions secret |
| **Targeted by** it | `claude-marketplace` — the dispatch writes here, so the token needs write access here |

Create a **fine-grained PAT** scoped to least privilege:

1. **Settings → Developer settings → Personal access tokens → Fine-grained → Generate new.**
2. **Resource owner:** `chris-peterson`. **Repository access:** only `claude-marketplace`.
3. **Repository permissions → Contents: Read and write.** (The dispatch endpoint's
   lever. A classic PAT works too but needs the broad `repo` scope across all your repos.)

If a fine-grained token 403s on dispatch, Contents-write is the permission to check.

### Distributing and rotating the token

The PAT is created once (above); `suite/set-dispatch-secret.sh` fans it out to
the plugin repos so you don't set it by hand N times. `chris-peterson` is a user
account, so the secret lives per-repo (only organizations share a secret across
repos) — but one command covers all of them:

```bash
just set-dispatch-secret        # every plugin in marketplace.json
# or one repo:
bash suite/set-dispatch-secret.sh anchor
```

Rotating is the same command with a fresh PAT. Adding a plugin: it's already in
`marketplace.json`, so re-run (or pass just its name). If per-repo secrets ever
become a burden, the alternatives are a **GitHub App** (short-lived tokens
minted per run) or moving the suite under a **GitHub org** (one shared secret).
