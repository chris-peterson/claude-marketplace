# claude-marketplace

Claude Code plugins by [chris-peterson](https://github.com/chris-peterson).

## Installation

```bash
claude plugins marketplace add https://github.com/chris-peterson/claude-marketplace
```

Then install whichever plugins you want:

```bash
claude plugins install tack@claude-marketplace
claude plugins install ClaudeWatch@claude-marketplace
```

## Plugins

### [tack](https://github.com/chris-peterson/tack)

Route-aware work tracker for AI-assisted development. Captures pivots, context switches, and multi-repo changes so that work-in-progress survives session boundaries.

### [ClaudeWatch](https://github.com/chris-peterson/ClaudeWatch)

`PreToolUse` hook that enforces command safety rules. Blocks or requires confirmation for destructive git ops, global installs, recursive deletes, and secret exposure — using regex matching that handles compound commands and heredocs that Claude Code's built-in permission system misses.
