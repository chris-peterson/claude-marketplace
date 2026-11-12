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

Each falls into one of six jobs: plan the passage, stay safe, keep oriented, reach your waypoints, chart the waters for the people who come next, and leave standing orders for the agent that comes next. They're listed in that order.

### [rig](https://chris-peterson.github.io/rig/#/) — plan the passage

Launches Claude Code with a named set of plugins chosen for a kind of work. Pin your local plugin checkouts so edits take effect without a release, and turn on the sandbox for a launch that asks for it. `/rig:switch` moves the current session to another rig and keeps the conversation.

### [ClaudeWatch](https://chris-peterson.github.io/ClaudeWatch/#/) — stay safe

Screens every shell command — and the code Claude writes to disk — before it runs, matching real patterns rather than naive prefixes, so reordered flags and chained commands don't slip past. Blocks the genuinely dangerous; asks before anything that changes state.

### [shipshape](https://chris-peterson.github.io/shipshape/#/) — stay safe

Tells you what changed in your coding harness and keeps it current: Claude Code itself, and the plugins you've installed. Reconciles what's installed against the set you've declared, updates them, and prunes the caches an update leaves behind.

### [tack](https://chris-peterson.github.io/tack/#/) — keep oriented

Tracks what you're working on across crashes, context overflow, and jumps between projects. Start a fresh session and pick up exactly where you left off.

### [beacon](https://chris-peterson.github.io/beacon/#/) — keep oriented

Colors each session's tab so you can tell what every Claude session is doing at a glance: neutral at rest, amber working, red waiting for you. That's iTerm2 on macOS; on any OS or terminal the same state shows in a fleet dashboard you open in a browser.

### [sonar](https://chris-peterson.github.io/sonar/#/) — keep oriented

Searches everything a session can reach for what you're after: the files it has loaded, the ones they lead to, sibling repos, git history, links, and past transcripts. Shallow matches come back right away; deeper ones arrive when your next turn starts. In preview: no commands yet.

### [anchor](https://chris-peterson.github.io/anchor/#/) — reach your waypoints

Keeps your issues, commits, change requests, reviews, and releases consistent — the same quality, formatting, and content every time, not reinvented per change. `/anchor:commit` walks you through the diff, then writes a why-first message; `/anchor:prepare-review` opens the change request.

### [mate](https://chris-peterson.github.io/mate/#/) — reach your waypoints

Makes the change itself, in the two shapes it comes in. `/mate:fix` drives a defect from symptom to shipped fix: root cause, a test that fails for the reason the bug exists, then a sweep for the same bug class. `/mate:feature` adds a capability against the patterns already in the codebase. Between them, one line naming the phase that comes next.

### [fathom](https://chris-peterson.github.io/fathom/#/) — chart the waters

Keeps the facts of a piece of work (an incident, an investigation) in one versioned record, then renders each reader's document from it: an analysis for engineers, a status for managers, an explainer for everyone else. `/fathom:record` turns evidence into facts; `/fathom:render` writes a view for one reader, and every figure in it cites the fact it came from.

### [masthead](https://chris-peterson.github.io/masthead/#/) — chart the waters

Stands up a documentation hub for a repo and keeps it current as the code changes, on the docs engine you choose. Its pages are written for the people who use what the repo ships: how the thing works, and what to watch out for. In preview: no commands yet.

### [cleat](https://chris-peterson.github.io/cleat/#/) — leave standing orders

Write your project's instructions once, in the file every AI tool reads. AGENTS.md is the file about 30 of them read; Claude Code reads CLAUDE.md and nothing else, so guidance kept in either one alone reaches half your tools. cleat holds a repo in the shape that satisfies both.

### [sextant](https://chris-peterson.github.io/sextant/#/) — leave standing orders

Keeps a plain-language spec — what the code must do — under source control, and reconciles it with the code in either direction. Written for specs that lag the code as often as they lead it.
