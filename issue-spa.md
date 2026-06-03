# Issue: Evolve the landing page into a self-contained SPA

## Summary
Grow the single landing page into a small **single-page app** where each plugin
zooms into its own in-site view — so a visitor can learn *everything* about the
suite (what each plugin is, how to install it, how to use it, what problems it
solves, and some in-session context) **without ever leaving the site**.

Lean away from the current docsify docs site; this front page becomes the
product, and the per-plugin material lives inside it.

## Interaction model
- The current landing is the **home** view.
- Clicking a plugin (name or card) activates a **zoomed-in plugin view** — a
  "tab" / detail pane for that plugin — with a **`← Back`** breadcrumb to home.
- Hash-based routing so views are deep-linkable and the browser Back button
  works (`#/anchor`, `#/logbook`, …).
- Transitions feel like zooming into the instrument, not a page reload.

## What a plugin view holds
- What it is / the problem it solves (the "why")
- Install (the exact `claude plugin install <name>@chris-peterson` command)
- How to use it — its commands, with short examples
- Some in-session context (how it shows up while you're actually working)
- Links out to the canonical docs + source as a fallback, not the only path

## Open questions
- **Content source:** hand-authored per-plugin content in this repo, vs. pulling
  from each plugin's own docs. Pulling avoids drift but couples builds; consider
  a build step that vendors a short excerpt per plugin.
- **Docsify retirement:** fold the existing "relationships" content into the SPA
  (e.g., a "how they fit together" view) before dropping docsify.
- **Framework:** stay vanilla single-file as long as it's manageable; reach for
  a tiny framework only if the view/routing logic outgrows hand-written DOM.

## Depends on / relates to
- Builds on iteration 1 (the static landing page).
- The session-playback feature ([issue.md](issue.md)) becomes one section of the
  home view (or a plugin view's "in-session context").
