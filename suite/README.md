# bridge.ai suite toolkit

The marketplace maintains the suite by reading the sibling plugin repos rather
than hand-authoring per-plugin content. Each plugin declares a canonical
`plugin.yml` (see [plugin.schema.md](plugin.schema.md)); these scripts project
and aggregate from it.

| Script | Output | Purpose |
|:---|:---|:---|
| `sync.sh` | sibling checkouts | clone/fast-forward every plugin in `marketplace.json` |
| `build-plugins-data.py` | `docs/plugins.js` | per-plugin doc site content from each `plugin.yml` |
| `record-artifacts.py` | `suite/artifacts.csv` | append a change-point row when a plugin's artifact set changes |
| `build-artifacts-data.py` | `docs/artifacts.json` | project the rolling log into the growth view's series + changelog |
| `build-deps-data.py` | `docs/deps.json` | project each plugin's declared `soft_deps` into the dependency graph |
| `check-coverage.py` | (gate) | fail the build if a plugin isn't grouped/renderable on the doc site |

`just build` regenerates the doc site's data. `docs/plugins.js`,
`docs/deps.json`, and `docs/artifacts.json` are rebuilt each deploy and
git-ignored; only `artifacts.csv` is committed, and it has one writer — see
[The artifact log](#the-artifact-log).

### The artifact log

`suite/artifacts.csv` is a **rolling change-point log**, one row per change to a
plugin's artifact set:

```text
date,plugin,skills,rules,hooks,commands,agents,change
2026-06-12,anchor,6,2,2,0,0,+skill:issue
```

The `change` column names what moved (`+skill:issue`, or a rename as a paired
`-skill:address-feedback +skill:resolve-feedback`). Replaying every row's `+/-`
tokens from empty reconstructs each plugin's current set, so `record-artifacts.py`
needs no state file and the growth view rebuilds from this file alone — never
re-walking git. `record-artifacts.py` compares the committed `HEAD` of each
sibling repo to the replayed set and appends only when it changed; a re-run with
nothing newly committed is a no-op.

**The log is CI's to write.** `deploy-docs.yml` runs the recorder against
freshly-synced siblings and commits the result itself, which is why every row
lands as a `chore: record artifact changes` commit. `HEAD` means the default
branch there because CI clones fresh — but in a local workspace it means
whichever branch each sibling happens to be on, so a local run can log unmerged
work as shipped. `just record-artifacts` still exists for a deliberate run;
`just build` leaves it out.

`seed-artifacts-history.py` is the one-time bootstrap (`just seed-artifacts`): it
walks each sibling repo's full git history to lay down the initial change points.
Run it only to recreate the log from scratch — the recurring build appends in
place.

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
