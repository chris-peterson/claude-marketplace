# bridge.ai

Claude Code plugins by [chris-peterson](https://github.com/chris-peterson), for AI-assisted development. The catalog, with what each plugin does and how they fit together, is at **[bridge.ai](https://chris-peterson.github.io/claude-marketplace/)**.

## Installation

```bash
claude plugin marketplace add chris-peterson/claude-marketplace
```

Then run `/plugin` inside Claude Code and open the **Discover** tab to browse and install — or install one directly by name:

```bash
claude plugin install <name>@chris-peterson
```

## Plugins

Each falls into one of four jobs: stay safe, keep oriented, reach your waypoints, write it down.

### [anchor](https://chris-peterson.github.io/anchor/#/) — reach your waypoints

Keeps your issues, commits, change requests, reviews, and releases consistent — the same quality, formatting, and content every time, not reinvented per change. `/anchor:commit` walks you through the diff, then writes a why-first message; `/anchor:prepare-review` opens the change request.

### [beacon](https://chris-peterson.github.io/beacon/#/) — keep oriented

Colors each session's tab so you can tell what every Claude session is doing at a glance: neutral at rest, amber working, red waiting for you. That's iTerm2 on macOS; on any OS or terminal the same state shows in a fleet dashboard you open in a browser.

### [ClaudeWatch](https://chris-peterson.github.io/ClaudeWatch/#/) — stay safe

Screens every shell command — and the code Claude writes to disk — before it runs, matching real patterns rather than naive prefixes, so reordered flags and chained commands don't slip past. Blocks the genuinely dangerous; asks before anything that changes state.

### [cleat](https://chris-peterson.github.io/cleat/#/) — write it down

Write your project's instructions once, in the file every AI tool reads. AGENTS.md is the file about 30 of them read; Claude Code reads CLAUDE.md and nothing else, so guidance kept in either one alone reaches half your tools. cleat holds a repo in the shape that satisfies both.

### [sextant](https://chris-peterson.github.io/sextant/#/) — write it down

Keeps a plain-language spec — what the code must do — under source control, and reconciles it with the code in either direction. Written for specs that lag the code as often as they lead it.

### [shipshape](https://chris-peterson.github.io/shipshape/#/) — stay safe

Tells you what changed in your coding harness and keeps it current: Claude Code itself, and the plugins you've installed. Reconciles what's installed against the set you've declared, updates them, and prunes the caches an update leaves behind.

### [tack](https://chris-peterson.github.io/tack/#/) — keep oriented

Tracks what you're working on across crashes, context overflow, and jumps between projects. Start a fresh session and pick up exactly where you left off.
