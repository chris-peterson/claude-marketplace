# claude-marketplace

Claude Code plugins by [chris-peterson](https://github.com/chris-peterson).

## Installation

```bash
claude plugin marketplace add chris-peterson/claude-marketplace
```

Then run `/plugin` inside Claude Code and open the **Discover** tab to browse and install — or install one directly by name:

```bash
claude plugin install <name>@chris-peterson
```

## Plugins

### [anchor](https://github.com/chris-peterson/anchor)

Git/forge skills that drive reviewed work into the permanent record. `/anchor:commit` writes why-focused commit messages, `/anchor:prepare-review` opens a change request on the forge, and `/anchor:commit --preview` shows in-flight changes in a visual difftool.

### [beacon](https://github.com/chris-peterson/beacon)

At-a-glance session awareness for Claude Code in iTerm2. Paints an iTerm2 badge (project name + idle/working/waiting color) and a fixed-layout status bar (project URL, branch, cwd, code, export buttons) so a glance across many windows tells you which sessions need attention.

### [ClaudeWatch](https://github.com/chris-peterson/ClaudeWatch)

`PreToolUse` hook that enforces command safety rules. Blocks or requires confirmation for destructive git ops, global installs, recursive deletes, and secret exposure — using regex matching that handles compound commands and heredocs that Claude Code's built-in permission system misses.

### [logbook](https://github.com/chris-peterson/logbook)

Turns a Claude Code, Cursor, or GitHub Copilot session into a retrospective committed to a team-owned git repository. Captures session metrics (token usage, tool counts, files touched, overlapping sessions, git activity) and uses them to draft the retro; only the published retro leaves the workstation, transcripts stay local.

### [moor](https://github.com/chris-peterson/moor)

A fast, keyboard-driven diff viewer for reviewing AI-generated code. Opens instantly, shows a two-file or directory diff, and feeds structured review feedback back to the agent that produced the change. Wires up as `git difftool`.

### [sextant](https://github.com/chris-peterson/sextant)

AI-assisted SPEC-driven development. Maintains a `SPEC.md` contract, audits implementations against it for coverage and drift, and scaffolds candidate implementations so the winner can be graduated to the repo root.

### [shipshape](https://github.com/chris-peterson/shipshape)

Keeps your *other* Claude Code plugins up to date. A `/plugin-maintenance` skill reconciles installed plugins against your desired set, updates them, and prunes the stale caches and orphan data dirs that uninstall leaves behind — while respecting the `.in_use` leases of live sessions. A `SessionStart` hook enforces marketplace auto-update so plugins stay current on their own.

### [tack](https://github.com/chris-peterson/tack)

Route-aware work tracker for AI-assisted development. Captures pivots, context switches, and multi-repo changes so that work-in-progress survives session boundaries.
