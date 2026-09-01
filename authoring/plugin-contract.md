# The plugin interop contract

How one bridge.ai plugin tells another that something happened.

Plugins in this suite ship from separate repos and install independently, so any
two of them may or may not be present together. This is the contract that lets
them collaborate anyway: **a plugin announces a fact it caused, on stdout, as one
line. Whoever cares matches that line.** Neither side names the other.

There is no broker, no daemon, and no dispatcher between them. Claude Code's own
hook system is the bus: a publisher's stdout reaches a `PostToolUse` hook as
`tool_response.stdout`, and reaches the agent as tool output. Both readers are
already there. The only shared artifact is [the key table](#published-keys) at
the bottom of this page, which no code reads.

## The announcement

One line, self-contained:

```text
codes.bridgeai.<plugin>/<entity>.<event> [KEY=value ...]
```

```text
codes.bridgeai.anchor/cr.opened CR_IID=88 CR_URL=https://github.com/o/r/pull/88 CR_DRAFT=1
```

| Part | Rule |
|---|---|
| `codes.bridgeai.` | Fixed prefix. Makes the line unmistakable in a transcript and greppable in one pass. |
| `<plugin>` | Whoever **caused** the fact, not whoever noticed it. |
| `<entity>.<event>` | Lowercase, past tense. `cr.opened`, `commit.pushed`, `route.bound`. |
| `KEY=value` | Bare tokens only: identifiers, numbers, URLs, booleans. **No spaces, no newlines, no quoting.** |

The payload restriction is not a simplification to revisit later. A value that
can carry arbitrary text is a value that can forge a second line, and the line
structure has to stay the publisher's to decide. Anything that needs prose is a
path to a file, not a field.

**Parse it by splitting on whitespace**, then on the single `/`. Left of the
slash is who published, right of it is what happened; both are dotted
internally, and the slash is the only boundary worth reasoning about.

`codes.bridgeai.<plugin>` is a literal name, not a URI scheme, so nothing
percent-decodes it and there is no authority component to resolve. The form is
the reverse-domain convention [RFC 7595](https://www.rfc-editor.org/rfc/rfc7595.html)
§3.8 asks of a private namespace, over a domain this suite owns
(`bridgeai.codes`) — which is what makes it safe to use unregistered, and the
subdomain per plugin needs no DNS record any more than a Java package does.

Staying a name rather than becoming a scheme (`codes.bridgeai.anchor:`) is
deliberate. URI syntax brings percent-encoding with it, and a `%0A` in a query
string puts a newline back inside a value, which is the one thing the payload
rule above exists to prevent. §6 would also want a provisional IANA
registration before anything using such a scheme left this suite.

## Publishing

Where a script already does the work, it already prints the payload. Add the
line:

```bash
echo "CR_IID=$cr_iid"
echo "CR_URL=$cr_url"
echo "codes.bridgeai.anchor/cr.opened CR_IID=$cr_iid CR_URL=$cr_url CR_DRAFT=$cr_draft"
```

The announcement repeats the fields rather than leaning on the block above it.
One line has to stand on its own, because a subscriber reads a whole tool
output and cannot tell which of two runs a loose `CR_IID=` belonged to.

Where the **agent** does the work (it ran the forge CLI, the skill told it to),
the plugin still owns the announcement. Ship a publisher the skill calls:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/announce.sh" cr.described CR_IID=88
```

`announce.sh` validates the key shape and echoes. It routes nothing, stores
nothing, and knows no subscribers. Keep it that way: the moment it grows a
lookup of who is listening, it is a message broker, and the reason this contract
is three paragraphs long is that it isn't one.

**Rules:**

- **Announce facts you caused.** Not facts you observed a sibling cause.
- **Announcing must never fail the operation.** Exit 0 on every path.
- **Don't leave a key with no other end.** A publisher nobody hears and a
  subscriber nothing feeds are both silent, and silence is the one failure this
  contract can't show you.

The two ends ship from separate repos, so one of them lands first. That gap is
fine while it is tracked and closed; what is not fine is discovering a year
later that it never closed. [Published keys](#published-keys) is where the
in-between state lives, which is why a key goes in that table when it is
**agreed**, not when it first fires.

## Subscribing

A `PostToolUse` hook on `Bash`, matching the key in the tool's stdout:

```bash
input=$(cat)
output=$(printf '%s' "$input" | jq -r '.tool_response.stdout // empty' 2>/dev/null) || exit 0
line=$(printf '%s' "$output" | grep -m1 '^codes\.bridgeai\.anchor/cr\.described\b') || exit 0
```

Register it in the subscriber's own `hooks.yml`. The publisher gains no entry,
no config, and no knowledge that anyone subscribed.

**Rules:**

- **Match the whole key, anchored.** `^codes\.bridgeai\.anchor/cr\.opened\b` does not
  also match `cr.opened.retry`.
- **Exit 0 on every path.** `PostToolUse` on `Bash` runs on every Bash call in
  every session where the plugin is enabled. A subscriber that errors or hangs
  taxes turns that have nothing to do with it.
- **Be idempotent.** There is no ordering guarantee between subscribers and no
  once-only guarantee: a session can publish the same key twice.
- **Silent for facts, printing for judgment.** See below.
- **Never `printf '%b'` on a harvested value.** `%b` expands a backslash escape
  into real newlines, letting a payload emit free-standing lines into the
  agent's context. Use `%s`.

## Facts go to hooks, judgment goes to the agent

Both readers see the same line. Which one you want decides whether the
subscriber prints:

| The reaction | Subscriber | Guarantee |
|---|---|---|
| Bookkeeping (record it, set a flag, touch a file) | does the work, prints nothing | the hook runs, so it happens |
| A decision (should we open a route? is this the handoff point?) | prints a nudge, acts on nothing | the agent may or may not act |

Facts move over hooks; judgment stays with the agent. Don't route bookkeeping
through the model's attention, and don't have a hook decide something that needs
context it can't see.

## Announcements, not archaeology

A hook that watches tool output is doing one of two things, and only one of them
is this contract.

**Watching for a shape of data, from anywhere.** Legitimate. tack's
`capture-urls.sh` scans for any forge URL in any Bash output: a `gh pr view`, a
paste, a sibling plugin, a script nobody wrote down. No announcement could cover
that, because the point is that the source is unknown.

**Inferring a sibling's action from how that sibling is implemented.** This is
the thing to replace. Before this contract, tack detected "anchor described a
CR" by grepping the *command line* for `gh pr ` plus `--body-file`, or
`merge_requests` plus `description=@`. It worked, and it coupled tack to which
flags anchor happened to pass. Change anchor to `glab mr update
--description-file` and tack stops firing, with nothing failing and nothing to
notice.

The test: if the publisher renamed a flag, switched CLIs, or refactored a
script, would the subscriber still work? If not, you are reading an
implementation detail, and there is a fact underneath it the publisher should
be announcing instead.

## The failure mode this contract has

A subscriber that never matches looks exactly like an event that never fired.
Both are silence.

Two subscribers to `tack:end` once shipped watching only half the events they
needed and sat inert for three months with a green test suite. A synthetic
payload test proves the matcher and nothing else.

So every new subscriber owes both halves:

- **The synthetic test** — feed a payload carrying the key, assert the reaction;
  feed the near-misses (a longer key sharing the prefix, the key inside a larger
  word, an empty payload, unrelated output), assert silence.
- **The live check** — install both plugins, run the publisher for real, and
  confirm the reaction. Nothing short of this separates "the matcher is right"
  from "the line actually arrives."

## Published keys

Every key in the suite, agreed or live. `State` is `wired` once both ends are in
place; otherwise it names the end still owed.

| Key | Publisher | Subscriber | Payload | State |
|---|---|---|---|---|
| `codes.bridgeai.anchor/cr.opened` | anchor, `scripts/prepare-review.sh --open` | tack, `hooks/capture-urls.sh`<br>beacon, `_read_announcements` (PROV-07 tier 0) | `CR_IID`, `CR_URL`, `CR_DRAFT` | wired |
| `codes.bridgeai.anchor/cr.described` | anchor, `skills/prepare-review` step 4, via `scripts/announce.sh` | tack, `hooks/landing-nudge.sh` | `CR_IID`, `CR_URL` | wired |

While a key reads anything but `wired`, the subscriber is inert and whatever it
replaced has to keep running until the other end lands.

## Related

- [`suite/plugin.schema.md`](../suite/plugin.schema.md) — how a plugin describes
  itself to the marketplace. This document is how it talks to its siblings.
- The `subscribe` skill builds a subscriber that fires on a **skill invocation**
  rather than an announcement, for reacting to a sibling that publishes nothing.
