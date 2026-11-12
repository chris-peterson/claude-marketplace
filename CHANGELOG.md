# What's new

Highlights for the bridge.ai suite as a whole, by date. `suite/build-whats-new.py`
merges these with every plugin release and artifact change into
`docs/whats-new.md`, which the What's new page and its RSS feed read.

## 2026-11-11

- **released:** [bridge.ai 2.0](https://chris-peterson.github.io/#/blog/2026-11-11-bridge-ai-2): new plugins [rig](https://chris-peterson.github.io/rig/#/), [fathom](https://chris-peterson.github.io/fathom/#/), [masthead](https://chris-peterson.github.io/masthead/#/), and [sonar](https://chris-peterson.github.io/sonar/#/).
- **new plugin:** [rig](https://chris-peterson.github.io/rig/#/): launch Claude Code with a named set of plugins, your local checkouts pinned in, and the sandbox when you want it.
- **new plugin:** [fathom](https://chris-peterson.github.io/fathom/#/): keep the facts of a piece of work in one record, and write each reader their own document from it.
- **new plugin:** [masthead](https://chris-peterson.github.io/masthead/#/): `/masthead:bootstrap` sets up a docs site for a repo, with search and a deploy that publishes on every push. docsify is the engine today.
- **new plugin:** [sonar](https://chris-peterson.github.io/sonar/#/): `/sonar:pulse` finds something you saw somewhere. The closest matches come back right away, and what a deeper search finds arrives at your next prompt.
- **released:** [anchor 2.0](https://chris-peterson.github.io/anchor/#/): diff reviews open in revdiff, notes land on the hunks you'd ask about, reviews work in rounds, and stacks are first class. `diff.tool` is ignored now, and revdiff 1.14+ is required.
- **released:** [ClaudeWatch 1.0](https://chris-peterson.github.io/ClaudeWatch/#/): built for auto mode, where Claude Code settles most allows before any plugin is asked, so ClaudeWatch now only restricts: it asks or blocks, in every permission mode. `/ClaudeWatch:learn` no longer proposes allow rules, rule changes survive upgrades, and `/ClaudeWatch:unattended` covers stepping away.
- **archived:** moor and logbook.
