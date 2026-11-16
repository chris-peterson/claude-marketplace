# bridge.ai suite contracts: coverage status

Tracking status of the requirements declared in [`SPEC.md`](SPEC.md).
Maintained by `/sextant:spec-status`.

**Last audit:** 2026-11-15
**Spec version:** root SPEC.md (unversioned)
**Coverage:** 53 Covered, 0 Partial, 2 Missing/Contradicts
**Evidence pointers:** file

Most of this spec is enforced somewhere other than this repo. `CATALOG` is enforced
by shipyard when the site builds. `CHECK` is enforced by each plugin's own test
suite. Everything else is enforced by the plugin that publishes or subscribes,
so a requirement's status here is the worst status across the plugins it binds.

Several rows are Covered on the strength of branches not yet merged: shipyard's
`fail-on-orphan-subscription`, and `events-conformance` in tack, mate, beacon
and masthead. Until they land, the first audit's findings (in the audit history
below) still describe what is released.

## Status by category

| Prefix | Count | Status | Enforced by | Notes |
|--------|------:|--------|-------------|-------|
| WIRE-01..06 | 6 | All Covered | each publisher's announce script | anchor `scripts/announce.sh`, masthead `scripts/announce.sh` (a port of anchor's), tack `src/announce.ts` |
| KEY-01..05 | 5 | All Covered | review | No key in the catalog names an observer, carries its outcome in the body, or hides a routing distinction in a field. Nothing checks this mechanically. |
| EMIT-01..07 | 7 | All Covered | each publisher | anchor and masthead share the script shape (EMIT-06, EMIT-07). tack prints from `src/announce.ts`. |
| SUB-01..12 (+SUB-04a) | 13 | All Covered | each subscriber's hook tests | tack `scripts/lib-subscribe.sh` (`emit_context`), `hooks/landing-nudge.sh` (object body, matched in jq over the whole output), `scripts/lib-url.sh` (`JQ_DEFS`); mate `hooks/react.sh` (`announced`, `field`); beacon `_DISPLAY_UNSAFE_RE` (C0, DEL and C1); sextant `hooks/ledger-signal.sh` |
| SWITCH-01..06 | 6 | All Covered | each subscriber | `tack.subscribe.*` (`heard`, `switch_hint` in tack's `scripts/lib-subscribe.sh`), `mate.subscribe.*` (`subscribed`, `say`), `beacon.subscribe.*` (`_switched_off`, `_subscribed`; silent, so SWITCH-05 is beacon's HOOK-18), `sextant.subscribe.*` (`opted_out`). Each reads the switch in the payload's `cwd`. |
| DECLARE-01..06 | 6 | All Covered | shipyard schema, review | masthead's `content.routed` now names `skills/bootstrap/SKILL.md`; tack's `emitted_by` names files rather than functions. |
| CATALOG-01..06 | 6 | 4 Covered, 2 Missing | shipyard `gen-events-json` | CATALOG-02 fails the build. **CATALOG-04, CATALOG-05 Missing**; see Open questions. |
| CHECK-01..06 | 6 | All Covered | each plugin's tests | CHECK-01: anchor `tests/announce.test.sh`, tack `declared publishes` in `src/announce.test.ts`, masthead `DeclaredPublishesTest`. CHECK-04, CHECK-05: tack's landing-nudge and mate's react tests feed a non-object body, a wrong-typed field and the key above 300 KB of output. |

## Per-plugin notes

- **anchor** conforms. `commit.pushed` covers new, amend and push-existing
  commits as one outcome (KEY-04: the fact a subscriber needs is "this commit is
  on the remote", whichever path put it there). Its `EVENTS` category still
  restates WIRE in its own words rather than citing it.
- **tack** shares its subscriber rules across three hooks through
  `scripts/lib-subscribe.sh`. A switch covers the announcement only: the URL
  scrape in `capture-urls.sh` is not a subscription and keeps running.
- **mate** reads a switch only after a key has matched, so deciding whether a
  Bash call is for mate stays within bash and jq (its HOOK-03).
- **beacon** reacts silently, so its switches are documented (HOOK-18) rather
  than named in output.
- **sextant**'s subscriber is on its open change request
  (`subscribe-to-catch-a-stale-ledger`), declared there, and is the reference
  implementation the switches above follow.
- **masthead**'s `content.routed` has no subscriber yet, which CATALOG-03 reports.

## Provenance

These requirements were harvested from three generations of the same idea:

1. **morse**, a durable message bus. Dropped because its broker, honker, shipped
   no Windows binary. Its one lasting finding: a routing key was transposed
   (topic in the name slot, name in the topic slot) and nothing noticed,
   because no layer checked a subscription against a publisher. That is CATALOG-02.
2. **fairlead**, a local dispatcher. A publisher called `fairlead publish`, and
   fairlead ran each subscriber's hook and forgot the message. It contributed:
   - EMIT-02: a publish never fails its publisher (fairlead's top invariant,
     because anchor called it from inside `commit.sh`).
   - WIRE-06: stay out of output the publisher's callers parse (fairlead's
     CLI-08, found by a test when its own stdout corrupted anchor's
     `KEY=value` lines).
   - KEY-01: name the publisher for who caused the fact, not who noticed it.
   - KEY-05: routing distinctions live in the key, because the body is opaque
     to anything matching on the key.
   - CATALOG-02..05: fairlead's `verify` reported a subscription with no
     publisher, an undeclared emit, and a declared handler that was missing.
3. **Hooks** (today). A PostToolUse hook already sees every Bash call's
   stdout, so the announcement line itself is the transport, and the
   dispatcher, its config file, and its metrics store went away. What survived
   was the contract, which is this file.

## Open questions

- **Renaming or retiring a key.** Nothing says how. A rename today breaks
  every subscriber silently until CATALOG-02 fails the build. Candidate rule: publish
  both keys for one release, declare the old one `deprecated: true`, and let
  CATALOG report subscribers still on it.
- **Typed fields.** `fields` are prose. A `type` per field would let CHECK-02
  and SUB-04 assert against a declaration rather than a convention.
- **CATALOG-04/05 implementation.** shipyard has every plugin's checkout at build
  time, so it could scan source, but no scan it could run is sound. Publishers
  build the key from a bare suffix (`announce("session.started")`), and
  subscribers match with alternations (`cr\.(created|updated)`), key tuples
  (beacon) or arguments (`announced anchor cr.ready`), so a grep for literal keys
  would miss most real cases and still flag keys quoted in comments. Either the
  plugins expose their keys in a form a tool can read, or these two become
  review checks rather than build checks.

## Audit history

### 2026-11-15: Findings fixed

The first audit's findings, fixed on branches: tack's handoff nudge (pipe
buffer, unparsed body, plain stdout) and the same plain-stdout channel in its
`capture-urls.sh` and `record-landed.sh`; mate's `cr.ready` on an unparsed body;
control characters in decoded values in tack and mate, and C1 in beacon; off
switches in tack, mate and beacon; masthead's `emitted_by`; CHECK-01 tests in
tack and masthead. The sextant finding was wrong: the audit read a checkout on
another branch, and the change request that adds the hook declares it. SUB-04
gained SUB-04a, since mate's `cr.ready` reads an optional `uri` and a
wrong-typed one should read as absent rather than silence the reaction.
53 Covered, 2 Missing (CATALOG-04, CATALOG-05).

### 2026-11-15: Ledger created

The suite contract moved out of prose in `authoring/plugin-contract.md` into
this repo's `SPEC.md`, with the guide kept as the rationale. 54 requirements
across eight categories, seeded from the guide, fairlead's spec and the
subscribers' current behavior. First audit found SUB-03 contradicted in
mate and tack, a pipe-buffer bug and a plain-stdout nudge in tack, switches missing in mate, tack and beacon, sextant's undeclared
subscription, and CATALOG-02 documented as failing the build when it only warned.
CATALOG-02 is fixed on a shipyard branch, and is counted Covered here on that basis.
