# The plugin events contract

How one bridge.ai plugin tells another that something happened.

Plugins in this suite ship from separate repos and install independently, so any
two of them may or may not be present together. This is the contract that lets
them collaborate anyway: **a plugin announces a fact it caused, on stdout, as one
line. Whoever cares matches that line.** Neither side names the other.

There is no broker, no daemon, and no dispatcher between them. Claude Code's own
hook system is the bus: a publisher's stdout reaches a `PostToolUse` hook as
`tool_response.stdout`, and reaches the agent as tool output. Both readers are
already there. What each side declares about itself lives in its own
`plugin.yml` ([Declaring events](#declaring-events)), and nothing at runtime
reads those declarations.

## The announcement

One line: the key, one whitespace run, then a single compact JSON object to end
of line.

```text
codes.bridgeai.<plugin>/<entity>.<event> {"uri":"…"}
```

```text
codes.bridgeai.anchor/cr.created {"uri":"https://github.com/o/r/pull/3533","title":"Add the events contract"}
```

| Part | Rule |
|---|---|
| `codes.bridgeai.` | Fixed prefix. Makes the line unmistakable in a transcript and greppable in one pass. |
| `<plugin>` | Whoever **caused** the fact, not whoever noticed it. |
| `<entity>.<event>` | Lowercase, past tense. `cr.created`, `commit.pushed`, `route.bound`. |
| the body | One JSON object, compact, no literal newline. Required; `{}` when the event carries nothing. |

Two field names are reserved, because they are the two any consumer can use
without knowing the producer:

| Field | Meaning |
|---|---|
| `uri` | the canonical web address of the thing this event is about |
| `title` | its human-readable name, where the producer knows it |

Everything else is the producer's own, and declared in its manifest. Field names
are lowercase.

**The body is required and JSON.** `{}` rather than nothing, so every parser has
one shape to handle. A body that does not parse means **skip the announcement
and exit 0**. A malformed line from one plugin must never take another one
down.

Compact JSON is what keeps the line whole: a serializer cannot emit a literal
newline inside a string (it writes the two characters `\` and `n`), so the
one-line guarantee is structural rather than a rule anyone has to remember.

**Parse the line** by splitting off the key at the first whitespace, then the
key on its single `/`. Left of the slash is who published, right of it is what
happened; both are dotted internally, and the slash is the only boundary worth
reasoning about.

`codes.bridgeai.<plugin>` is a literal name, not a URI scheme, so nothing
percent-decodes it and there is no authority to resolve. The form is the
reverse-domain convention [RFC 7595](https://www.rfc-editor.org/rfc/rfc7595.html)
§3.8 asks of a private namespace, over a domain this suite owns
(`bridgeai.codes`), which is what makes it safe to use unregistered; the
subdomain per plugin needs no DNS record any more than a Java package does.

Staying a name rather than becoming a scheme (`codes.bridgeai.anchor:`) is
deliberate. A scheme invites the rest of URI syntax, and a `?query` payload
would put the one-line guarantee back into percent-encoding discipline that
every producer has to get right, where a JSON object gets it structurally. §6
would also want a provisional IANA registration before anything using such a
scheme left this suite.

## Publishing

Where a script already does the work, add the line to what it already prints:

```bash
echo "CR_URL=$cr_url"
printf 'codes.bridgeai.anchor/cr.created {"uri":%s,"title":%s}\n' \
  "$(jq -Rn --arg v "$cr_url" '$v')" "$(jq -Rn --arg v "$title" '$v')"
```

The announcement repeats what the block above it already said. One line has to
stand on its own, because a subscriber reads a whole tool output and cannot tell
which of two runs a loose `CR_URL=` belonged to.

Where the **agent** does the work (it ran the forge CLI, the skill told it to),
the plugin still owns the announcement. Ship a publisher the skill calls:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/announce.sh" cr.updated uri="$CR_URL"
```

Such a publisher validates the key shape, encodes the body, and echoes. It
routes nothing, stores nothing, and knows no subscribers. Keep it that way: the
moment it grows a lookup of who is listening, it is a message broker, and the
reason this contract is short is that it isn't one.

**Rules:**

- **Announce facts you caused.** Not facts you observed a sibling cause.
- **Announcing must never fail the operation.** Exit 0 on every path.
- **One announcement per phase, not per mutation.** A run that writes a
  description, sets labels, and attaches a milestone has changed one thing as
  far as a subscriber is concerned. Emit once, where the phase ends, rather than
  making every consumer debounce.
- **Don't leave a key with no other end.** A publisher nobody hears and a
  subscriber nothing feeds are both silent, and silence is the one failure this
  contract can't show you.

The two ends ship from separate repos, so one of them lands first. That gap is
fine while it is tracked and closed; what is not fine is discovering a year
later that it never closed. The manifests are where the in-between state shows,
which is why a key goes into one when it is **agreed**, not when it first fires.

## Subscribing

A `PostToolUse` hook on `Bash`, matching the key in the tool's stdout and
parsing what follows:

```bash
input=$(cat)
output=$(printf '%s' "$input" | jq -r '.tool_response.stdout // empty' 2>/dev/null) || exit 0
line=$(printf '%s' "$output" | grep -m1 '^codes\.bridgeai\.anchor/cr\.created[[:space:]]') || exit 0
uri=$(printf '%s' "${line#* }" | jq -r '.uri // empty' 2>/dev/null) || exit 0
```

Register it in the subscriber's own `hooks.yml`. The publisher gains no entry,
no config, and no knowledge that anyone subscribed.

**Rules:**

- **Match the whole key, anchored.** `^codes\.bridgeai\.anchor/cr\.created[[:space:]]`
  does not also match `cr.createdagain`.
- **Exit 0 on every path**, a body that won't parse included. `PostToolUse` on
  `Bash` runs on every Bash call in every session where the plugin is enabled. A
  subscriber that errors or hangs taxes turns that have nothing to do with it.
- **Be idempotent.** There is no ordering guarantee between subscribers and no
  once-only guarantee: a session can publish the same key twice.
- **Silent for facts, printing for judgment.** See below.
- **Sanitize a value before you render it.** See the next section; this one is
  not optional.

## A parsed value is not a safe value

The format guarantees the announcement occupies one line. It does not make what
you decode out of it safe to put anywhere.

JSON can represent what the line cannot contain: `{"title":"a\nb"}` decodes to a
real newline, and a `\u` escape decodes to whatever control character it
names, ESC included. So a decoded value reaching a surface can still forge a
line in the agent's context, or emit a control sequence into a terminal: an
ESC inside OSC-8 link text corrupts the pane it renders in.

**Strip control characters from any value before putting it on a terminal
surface or into the agent's context.** Print with a formatter that does not
expand escapes (`printf '%s'`, never `'%b'`). Treat every value as text a
stranger wrote, because the producer got it from a forge, a branch name, or a
commit message.

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
the thing to replace. Before this contract, tack detected a described CR by
grepping the *command line* for `gh pr ` plus `--body-file`, or `merge_requests`
plus `description=@`. It worked, and it coupled tack to which flags anchor
happened to pass. Change anchor to `glab mr update --description-file` and tack
stops firing, with nothing failing and nothing to notice.

The test: if the publisher renamed a flag, switched CLIs, or refactored a
script, would the subscriber still work? If not, you are reading an
implementation detail, and there is a fact underneath it the publisher should be
announcing instead.

## Declaring events

Each side declares its half in its own `plugin.yml`, and the two halves are
deliberately asymmetric.

**A producer declares the event fully**, because it is the one emitting the
fields. The key is bare: `name:` already supplies `codes.bridgeai.<plugin>`, so
a producer cannot typo its own prefix.

```yaml
events:
  publishes:
    - key: cr.created
      when: prepare-review opened a change request
      emitted_by: scripts/prepare-review.sh
      fields:
        uri: the change request's web address
        title: its title, as anchor set it
```

**A consumer declares only the key it depends on**, fully qualified because it
belongs to someone else. It does not restate the fields: with N consumers
declaring a schema, there are N copies to drift, and a consumer has standing to
assert a dependency, not a shape.

```yaml
events:
  subscribes:
    - key: codes.bridgeai.anchor/cr.created
      handled_by: hooks/capture-urls.sh
      reason: records the change request on the session's route
```

**Both halves are published**, into each plugin's own events page and into the
suite catalog that pairs them — so `when:`, `reason:`, and the field descriptions
are read by someone who has never seen the plugin. Two things follow.

Keep a plugin's internal vocabulary out of them. A spec requirement ID
(`PROV-07`, `STATUSLINE-03`) names nothing a catalog reader can resolve, least of
all in the aggregate, where a reader on one plugin's events page has no reason to
know another's spec. Say what the event or the subscription gets the user:
`moves the change request to what the session has shipped`, not `feeds
STATUSLINE-03's delivered line`.

`emitted_by:` and `handled_by:` name the **file**, not a symbol inside it. A file
is something a reader can open, and a rename shows up in the diff; a function
name drifts silently, because nothing resolves either one — these fields are
prose for a reader, not a reference the tooling follows.

`when:` is prose and earns its place. It is where a producer says the thing no
consumer can infer from a key name: which paths emit it today, whether a
re-run fires it again, what it means when the same key arrives twice.

### What the declarations are checked for

The two directions cannot be gated the same way:

- **A subscription to a key nobody publishes fails the build.** It is a typo or
  a stale reference, always.
- **A published key with no subscriber warns.** CI reads each sibling's
  committed branch, so hard-failing would break the first half of every
  two-repo rollout for as long as the second half takes to land.

### Producers verify their own declarations

A manifest that drives documentation drifts from the code that emits, silently,
because nothing fails when it does. So a producer carries its own check: for
every key it declares, assert the key appears in the source that emits it, and
where the emitting path is exercised by a test, assert the fields come out as
declared.

Be clear about the reach of that check. It catches a rename landing in one place
and not the other, which is the common drift. It does not prove a consumer's
matcher works; that is the subscriber's own obligation, below.

## The failure mode this contract has

A subscriber that never matches looks exactly like an event that never fired.
Both are silence, and the declarations catch only the half that is written down.

Two subscribers to `tack:end` once shipped watching only half the events they
needed and sat inert for three months with a green test suite. A synthetic
payload test proves the matcher and nothing else.

So every new subscriber owes both halves:

- **The synthetic test** — feed a payload carrying the key, assert the reaction;
  feed the near-misses (a longer key sharing the prefix, the key inside a larger
  word, a body that won't parse, unrelated output), assert silence.
- **The live check** — install both plugins, run the publisher for real, and
  confirm the reaction. Nothing short of this separates "the matcher is right"
  from "the line actually arrives."

## Published keys

Every key in the suite, until the manifests above are what the catalog is built
from. `State` is `agreed` for a key both sides have settled on, and `wired` once
both ends are emitting and matching it. The declarations themselves are rendered
at [bridge.ai / Events](https://chris-peterson.github.io/claude-marketplace/spec/events),
which pairs each published key with whoever subscribes to it.

| Key | Publisher | Subscriber | Body | State |
|---|---|---|---|---|
| `codes.bridgeai.anchor/cr.created` | anchor, `scripts/prepare-review.sh --open` | tack, `hooks/capture-urls.sh` + `hooks/landing-nudge.sh`<br>beacon, `_read_announcements` (PROV-07 tier 0) | `uri`, `title` | wired |
| `codes.bridgeai.anchor/cr.updated` | anchor, `skills/prepare-review`, end of the mutation phase | tack, `hooks/capture-urls.sh` + `hooks/landing-nudge.sh`<br>beacon, `_read_announcements` (PROV-07 tier 0) | `uri`, `title` | wired |

Every subscriber matches **both** keys, because a run announces one or the other
and never both: a fresh change request reports only `cr.created` and only a
pre-existing one reports `cr.updated`. A subscriber keyed to a single one is
silent for half the cases, which is the shape of mistake this table exists to
make visible.

## Related

- [`suite/plugin.schema.md`](../suite/plugin.schema.md) — how a plugin describes
  itself to the marketplace. This document is how it talks to its siblings.
- The `subscribe` skill builds a subscriber that fires on a **skill invocation**
  rather than an announcement, for reacting to a sibling that publishes nothing.
