# bridge.ai suite contracts

The requirements every bridge.ai plugin holds to where it meets a sibling. A
plugin's own `SPEC.md` owns what that plugin does; this file owns what the suite
agrees on between plugins, so a rule lives here once instead of in every repo
that touches it. Today that is the events contract.

[`authoring/plugin-contract.md`](authoring/plugin-contract.md) is the guide: why
each rule exists, worked examples, and the failure stories behind them. This file
is the normative half. Where the two disagree, this file wins and the guide is
the bug. [`STATUS.md`](STATUS.md) records which plugins conform and what enforces
each requirement.

Requirements use [EARS syntax](https://alistairmavin.com/ears): Ubiquitous
(`The <system> shall …`), State-Driven (`While …`), Event-Driven (`When …`),
Optional (`Where …`), or Unwanted Behaviour (`If … then …`).

Each requirement is its own heading carrying a stable ID (`XX-NN`), one level
below its category's heading, so every requirement has a linkable anchor
(`SPEC.md#wire-01`).

**A plugin's spec cites these IDs rather than restating them.** Write
`per bridge.ai SUB-03` and spend the plugin's own requirement on what only that
plugin decides: which keys it hears and what it does about them.

## Concepts

- **announcement**: one line a plugin prints on stdout stating a fact it caused.
- **key**: `codes.bridgeai.<plugin>/<entity>.<event>`, the routing key.
- **body**: the JSON object after the key.
- **publisher**: the plugin that caused the fact and prints the announcement.
- **subscriber**: a sibling's hook that matches the key in a tool's output and
  reacts.
- **declaration**: a plugin's `events:` block in its `plugin.yml`, one half
  of a pairing.
- **catalog**: every rostered plugin's declarations, paired by key and published
  at [bridge.ai / Events](https://chris-peterson.github.io/claude-marketplace/spec/events).
- **the system**: in `WIRE`, `KEY`, and `EMIT`, the publisher; in `SUB` and
  `SWITCH`, the subscriber; in `DECLARE`, the plugin's manifest; in `CATALOG`,
  the suite build; in `CHECK`, the plugin's own test suite.

## Requirements

### `WIRE`
The announcement

#### `WIRE-01`
The system shall announce a fact as one line on the stdout of the command that
caused it: the key, one whitespace run, and one compact JSON object to end of
line.

#### `WIRE-02`
The system shall form the key as `codes.bridgeai.<plugin>/<entity>.<event>`, in
lowercase, with `<plugin>` the publishing plugin's `name:`.

#### `WIRE-03`
The system shall always carry a body that is a JSON object, `{}` when the fact
carries nothing.

#### `WIRE-04`
Where a body carries `uri`, the system shall set it to the canonical web address
of the thing the fact is about; where it carries `title`, to that thing's
human-readable name.

#### `WIRE-05`
The system shall name body fields in lowercase.

#### `WIRE-06`
The system shall add an announcement beside what a command already prints, and
shall not change any line the command's own callers parse.

### `KEY`
Naming a key

#### `KEY-01`
The system shall name a key for the plugin that caused the fact, not for
whichever component observed it.

#### `KEY-02`
The system shall name a key's event in the past tense.

#### `KEY-03`
The system shall name a key for what is true at the moment the line is printed.

#### `KEY-04`
Where one code path can end in different facts, the system shall announce a
different key for each outcome rather than one key with the outcome in the body.

#### `KEY-05`
Where a subscriber needs a distinction to decide whether to react, the system
shall carry that distinction in the key rather than in the body.

### `EMIT`
Publishing

#### `EMIT-01`
The system shall announce only facts it caused, never one it observed a sibling
cause.

#### `EMIT-02`
If announcing fails for any reason, then the system shall complete the operation
it was announcing and exit as that operation would have.

#### `EMIT-03`
The system shall announce once per phase of work, where the phase ends, not once
per mutation within it.

#### `EMIT-04`
The system shall make each announcement stand on its own, repeating any value a
subscriber needs rather than referring to other lines in the same output.

#### `EMIT-05`
Where the agent performs the operation rather than a script, the system shall
ship a publisher script the skill calls to announce it.

#### `EMIT-06`
The system's publisher script shall validate the key's shape, encode the body,
and print, and shall neither route, store, nor know of any subscriber.

#### `EMIT-07`
If a publisher script is called with a malformed key or a body it cannot encode,
then it shall print nothing on stdout, explain on stderr, and exit 0.

### `SUB`
Subscribing

#### `SUB-01`
The system shall subscribe with a `PostToolUse` hook on `Bash`, registered in its
own `hooks.yml`, reading the tool's stdout, and shall require nothing of the
publisher.

#### `SUB-02`
The system shall match a key only at the start of a line and followed by
whitespace.

#### `SUB-03`
If a matched line's body does not parse as a JSON object, then the system shall
not react to it.

#### `SUB-04`
If a field the system requires is absent or of the wrong type, then the system
shall treat the announcement as it treats a body that does not parse.

#### `SUB-04a`
Where a field the system can react without is of the wrong type, the system
shall treat it as absent.

#### `SUB-05`
The system shall exit 0 on every path, including a body that does not parse.

#### `SUB-06`
The system shall produce the same outcome when the same announcement arrives
more than once, and shall assume no order among subscribers.

#### `SUB-07`
When the system has something to tell the agent, it shall emit it as
`hookSpecificOutput.additionalContext` JSON, not as plain stdout.

#### `SUB-08`
The system shall not feed a tool's whole output through a pipe into a reader
that can stop before the writer finishes.

#### `SUB-09`
The system shall strip C0, DEL, and C1 control characters from a decoded value
before placing it on a terminal surface or into the agent's context.

#### `SUB-10`
Where a reaction is bookkeeping, the system shall perform it and print nothing.

#### `SUB-11`
Where a reaction needs the agent's judgment, the system shall emit a nudge and
act on nothing itself.

#### `SUB-12`
Where a sibling announces a fact, the system shall react to the announcement and
not to the sibling's command lines, flags, or file layout.

### `SWITCH`
Turning a subscription off

#### `SWITCH-01`
The system shall let the user turn off every subscription to one publisher with
the git config boolean `<subscriber>.subscribe.<publisher>`, and one key with
`<subscriber>.subscribe.<publisher>.<entity>-<event>`.

#### `SWITCH-02`
While neither switch for a key reads `false`, the system shall treat the
subscription as on.

#### `SWITCH-03`
The system shall read a switch in the repository the announcement is about,
taken from the hook payload's `cwd`, so a repository's value overrides the
global one.

#### `SWITCH-04`
Where the system prints a reaction, it shall end with the `git config --global`
command that turns that reaction off.

#### `SWITCH-05`
Where the system prints nothing, its plugin's events page shall name the switch
that turns the subscription off.

#### `SWITCH-06`
Where one hook handles several keys, the system shall check each key's switch
before reacting to it.

### `DECLARE`
Declarations

#### `DECLARE-01`
The system shall declare each key its plugin publishes under `events.publishes`
with a bare `key`, `when`, `emitted_by`, and `fields`.

#### `DECLARE-02`
The system shall declare each key its plugin subscribes to under
`events.subscribes` with the fully qualified `key`, `handled_by`, and `reason`,
and shall not restate the key's fields.

#### `DECLARE-03`
The system shall declare a key once both ends have agreed it, whether or not
either end has shipped.

#### `DECLARE-04`
The system shall write `when`, `reason`, and field descriptions for a reader who
has never seen the plugin, without the plugin's internal vocabulary such as its
requirement IDs.

#### `DECLARE-05`
The system shall name a file, not a symbol, in `emitted_by` and `handled_by`.

#### `DECLARE-06`
The system shall work identically whether or not any declaration is present at
runtime.

### `CATALOG`
The catalog

#### `CATALOG-01`
When the suite's site is built, the system shall pair every published key with
every plugin subscribing to it, from both halves of the declarations.

#### `CATALOG-02`
If a declared subscription names a key no plugin publishes, then the system
shall fail the build, naming the subscriber and the key.

#### `CATALOG-03`
If a published key has no declared subscriber, then the system shall report it
without failing the build.

#### `CATALOG-04`
If a plugin's source prints a key under its own namespace that its manifest does
not declare, then the system shall report it.

#### `CATALOG-05`
If a plugin's hook matches a sibling's key that its manifest does not declare
under `events.subscribes`, then the system shall report it.

#### `CATALOG-06`
The system shall publish, for each key, its publisher, `when`, fields, and every
subscriber with its `reason`.

### `CHECK`
What each end proves

#### `CHECK-01`
The system's publisher shall carry a test asserting that each key it declares
appears in the source that emits it.

#### `CHECK-02`
Where a publisher's emitting path runs under test, the system shall assert the
body carries the declared fields.

#### `CHECK-03`
The system's subscriber shall carry a test that feeds the key and asserts the
reaction on the channel the agent reads.

#### `CHECK-04`
The system's subscriber shall carry a test asserting no reaction to each
near-miss: a longer key sharing the prefix, the key mid-line, a body that does
not parse, a field of the wrong type, and unrelated output.

#### `CHECK-05`
The system's subscriber shall carry a test that places the key at the top of a
stdout larger than the pipe buffer, behind a near-miss line, and asserts the
reaction.

#### `CHECK-06`
The system's subscriber shall document a live check: both plugins installed, the
publisher run for real, and the reaction confirmed in the agent's context.
