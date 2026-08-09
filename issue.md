# Issue: Animated session playback for "Example usage"

## Summary
Replace the static "Example usage" walkthrough on the landing page with an
**animated session replay** — a terminal-style "tape" that plays one realistic
session start-to-finish, so the slash-command invocations are seen *in context*
rather than listed.

## Why
A static list of steps *tells*; a playable session *shows*. Watching the
commands run in a believable flow makes the tools concrete and earns trust
faster — especially for someone early in their AI-coding journey.

## Behavior
- A terminal/chat-style pane plays a scripted session frame by frame.
- Controls: ▶ / ⏸ play-pause, ⏭ step, ↻ restart; a step counter (current / total);
  a speed toggle (1× / 2×).
- Autoplays once when scrolled into view; pauses on any interaction.
- Command frames "type" the invocation; dialogue / outcome frames fade in.
- Single-file HTML/CSS/JS, consistent with the rest of the page. Reuse the
  plugin favicons and the four functional-area colors.

## Script — emphasis on anchor + logbook
A realistic single session. **tack, beacon, and sextant are intentionally left
out** — they're about cross-session continuity, ambient status, and spec-driven
work, none of which read well in a one-and-done session. ClaudeWatch appears
*reactively* (it intercepts a git command), which is exactly how you experience
it.

1. you → ask Claude to add retry/backoff to an API client
2. Claude → done, with tests
3. you → notice the backoff has no jitter (thundering-herd risk)
4. **`/note`** (logbook) → capture the observation mid-session, before it's lost
5. you → "before I keep this, let me actually read it"
6. **the diff** (synthesized mock — a small red/green hunk + a "rejected: <reason>"
   note) → spot the no-jitter hunk, reject it with a course correction
7. Claude → fixes it (full-jitter backoff, test updated)
8. **`/commit`** (anchor) → why-first commit message
9. **`/prepare-review`** (anchor) → rebase on main, push, open a draft CR…
10. **ClaudeWatch** (watch-git) → intercepts the push, asks to confirm
11. you → confirm (it's your draft)
12. Claude → draft change request opened, branch set to delete on merge
13. **`/retro`** (logbook) → write up the jitter lesson for the team

## Notes
- Synthesize a small diff card rather than a literal screenshot.
- Keep the human-in-control beat front and center (you reject, you confirm).
