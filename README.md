# claude-marketplace

Claude Code plugins by [chris-peterson](https://github.com/chris-peterson).

## Installation

```bash
claude plugins marketplace add https://github.com/chris-peterson/claude-marketplace
```

Then install whichever plugins you want:

```bash
claude plugins install beacon@chris-peterson
claude plugins install ClaudeWatch@chris-peterson
claude plugins install scribe@chris-peterson
claude plugins install tack@chris-peterson
```

## Plugins

### [beacon](https://github.com/chris-peterson/beacon)

At-a-glance session awareness for Claude Code in iTerm2. Paints an iTerm2 badge (project name + idle/working/waiting color) and a fixed-layout status bar (project URL, branch, cwd, code, export buttons) so a glance across many windows tells you which sessions need attention.

### [ClaudeWatch](https://github.com/chris-peterson/ClaudeWatch)

`PreToolUse` hook that enforces command safety rules. Blocks or requires confirmation for destructive git ops, global installs, recursive deletes, and secret exposure — using regex matching that handles compound commands and heredocs that Claude Code's built-in permission system misses.

### [scribe](https://github.com/chris-peterson/scribe)

Turns a coding session — Claude Code, Cursor, or GitHub Copilot — into a retrospective committed to a team-owned git repository. Transcripts stay on the author's workstation; only the retro is published.

### [tack](https://github.com/chris-peterson/tack)

Route-aware work tracker for AI-assisted development. Captures pivots, context switches, and multi-repo changes so that work-in-progress survives session boundaries.
