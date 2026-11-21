---
name: software-factory
description: "Use when deciding whether to industrialize software work with agents — building or assessing a 'software factory', comparing it to a swarm, a freelance marketplace, or a one-person-with-agents studio, designing intake/verification/lessons loops, or reading 2026 debates around yetone/Magpie, Factory.ai, Warp Factories, Ralph-style loops, or virtual software companies. Ships first-principles invariants, a laziness-ordered decision ladder, failure modes, and a sourced due-diligence pack. Not a biography, and not a mandate to copy anyone's prompts."
version: 1.0.0
author: Liz (lizliz.xyz)
license: MIT
---

# Software factory method

## Decision first — the lazy ladder

**"Should we build a software factory?" is a fixed question with a
laziness-ordered answer. Start at rung 1 and stop as soon as a rung fits.**

1. **No oracle, no tests, and the demand is still fuzzy → do not
   industrialize.** A factory without an independent check just manufactures
   rework. Stay in a studio: one human, one agent, a tight conversation.
2. **One well-specified task with a mechanical stop condition → a
   single-task loop.** Same prompt, a test/linter/compiler as the gate, a
   hard iteration cap. This is a cell on the line (the "Ralph" pattern),
   not a factory. See `references/landscape.md`.
3. **Several parallel jobs on one machine, a human still the boss → a
   supervised fleet.** Dispatch narrow tasks, poll state, verify receipts
   before reporting. That implementation in this repo is
   [`fleet-orch`](../fleet-orch/SKILL.md). Magpie the *product* may be the
   local model gateway those workers talk to; it is not the factory.
4. **A live product with continuous multi-channel feedback, and you can
   actually afford verification → a small factory.** Codify intake, cheap
   prefilter, an independent verification gate, a lessons ledger with a
   promotion threshold, human gates for taste / security / product
   direction, and a WIP limit on how often you ship.
5. **An organization that must instrument the whole SDLC and own the
   learning → an organizational factory.** This is what Factory.ai and Warp
   Factories sell. Do not start here. Autonomy is a maturation process;
   vendor claims of production deployment are marketing until you can see
   the gates.

If a lower rung already clears the work, building a higher one is
inventory, not leverage.

## The demand (why this exists)

A talented person plus a chat agent can write code. They cannot, at the
same time:

- listen to every issue, pull request, chat message, and public post
- keep a stable, inspectable definition of "done"
- remember last week's failure modes after the session ends
- verify on the platforms users actually use
- ship and reply without becoming the bottleneck themselves

The demand is not "more tokens." Generation got cheap and noisy.
**Judgment and verification are the scarce resources.** A factory is a
way to spend those scarce resources on gates, not on typing.

That sentence is older than this hype cycle. Jack Greenfield and Keith
Short's Software Factories work at Microsoft (2004) already framed the
problem as a capacity crisis: craft production of every application from
scratch cannot meet demand, and industrialization means systematic reuse
and automation of rote work so skilled people stop being wasted on it.
The 2025–2026 wave changes the *workers* (LLMs), not the *question*.
Lineage is in `references/lineage.md`.

## What is, and is not, a software factory

In this skill, a **software factory** is a system that turns external
signals into shipped, observed, and improved software through staged work
with interfaces, visible inventory, WIP limits, and a verification gate
the implementer does not solely adjudicate. The workers may be humans,
LLMs, or both.

### Invariants

You do not have a factory unless most of these are true:

1. **External signals start the line** — bugs, feedback, incidents,
   requirements — not a blank prompt in a vacuum.
2. **Division of labor with written interfaces** — roles, documents, APIs,
   handoff contracts — not a pile of agents sharing one context window.
3. **Inventory you can see** — a backlog, specs, tests, lessons, release
   artifacts. Hidden work is not a line; it is a mess.
4. **WIP limits** — a cap on changes in flight and on release rate. Cheap
   generation without a cap fills the line with half-finished inventory
   (Goldratt: the constraint is whatever the line cannot finish).
5. **An independent verification gate** — tests, reproduction on the
   reporter's surface, a reviewer who is not the author, a CI run that
   *finished* green. Self-grading is not a gate.
6. **A feedback loop that changes the system** — recurring failures become
   written standards the next worker must read. A loop that only emits
   more code is a treadmill.
7. **Human judgment reserved for what has no oracle** — product taste,
   security exceptions, "this must be escalated." If everything needs a
   human, you built a queue, not a factory. If nothing can call a human,
   you built an unsupervised risk engine.

### Distinct from adjacent shapes

| Shape | What it actually is | When it is the right tool |
| --- | --- | --- |
| **Studio** (one person + agents) | A craft loop. Fast, contextual, the human is still the line. | Exploration, taste-heavy work, no stable oracle. |
| **Single-task loop** (Ralph-style) | One prompt, repeated until a mechanical gate or a cap. | Greenfield or well-specified tasks with tests. |
| **Supervised fleet** (`fleet-orch`) | Parallel workers on one machine; a boss verifies receipts. | Overnight batch of narrow, checkable jobs. |
| **Swarm** | Many agents, little inventory, weak WIP, weak independent check. | Rarely. Throughput theater. |
| **Virtual company** (ChatDev, early MetaGPT) | Role-play SOPs inside one run (CEO/PM/dev/QA). | A decomposition pattern for a single artefact, not an operating system for a live product. |
| **Marketplace** | Tasks go out, results come back; little shared memory. | Burst capacity with human contracts, not a line. |
| **Model router / gateway** (yetone/magpie the *product*) | One local endpoint, many models and accounts. | An input to cells on the line. Not the factory. |
| **Organizational factory** (Factory.ai, Warp Factories) | Intake → triage → spec → implement → review → verify → ship → monitor, instrumented across the SDLC. | After rungs 1–4, when you must own learning and governance at org scale. |

Warp's own docs are useful as a contrast: their factories run the loop,
and **humans still approve and merge** — "factories never merge."
yetone's Magpie maintenance loop, as he described it and as the repo's
`LESSONS.md` states, has agents write, review, merge, and release, with
the human spending a nightly window on UI/UX and holding security /
product gates. Those are two implementations of the same invariants,
with a different answer to "who is allowed to ship." Details and sources:
`references/landscape.md`.

## What changes when the workers are LLMs

- **Generation is cheap; verification is scarce.** If the implementer also
  judges the work, you will ship confident mistakes at high frequency.
- **Context is a hard WIP limit.** Three loops editing one repo without
  worktree or merge-queue isolation will collide. This is a known gap in
  reconstructions of the Magpie loops (see `references/yetone-loops.md`).
- **Non-determinism and prompt injection are intake risks.** Issues, PR
  diffs, Discord, and X are untrusted data. A factory that reads the
  public internet is an attack surface, not just a feedback channel.
- **Institutional memory dies at session end unless it is written down.**
  The valuable piece in the Magpie case is not the `/loop` prompt. It is
  `LESSONS.md` → promotion into `docs/code-standards.md` after a rule is
  seen on three separate days, plus acceptance criteria that force "not
  run" to be listed rather than implied.
- **Rework is the hidden inventory.** Magpie's own ledger records that on
  2026-10-05, about 40 of 220 commits fixed something released that day or
  the day before, and that 294 tags in 51 hours left no CI run to finish.
  Tag count is not throughput.
- **Cost is tokens plus human review plus entropy removal.** A
  commentator-quoted reply from yetone (not independently retrieved; see
  due diligence) put Magpie + Alma spend at least at $400/month, plus
  another $200 "for work." Treat that as *claimed via secondary source*,
  not a benchmark.

## How to apply (if a rung 4+ factory is actually the answer)

Do these in order. Skip ceremony.

1. **Name the constraint.** What can the line not finish today — triage,
   reproduction, review, CI, release, or taste? Add capacity only at that
   point.
2. **Write the intake contract.** Which channels are in scope, what a
   useful report contains, what is ignored, and the canned reply for
   spam/ads. Put a cheap classifier in front of the expensive model.
3. **Give the worker a real environment** that can reproduce the reporter's
   surface (the OS, the agent, the account class). Screenshots are not a
   reproduction.
4. **Install an independent gate.** A test that fails without the change;
   "what was run, at which head"; cancelled CI is not green; merge pinned
   to the reviewed SHA. The implementer may run checks; they may not be
   the only one who sees the result.
5. **Start a lessons ledger.** Each lesson is a rule, a why, and evidence.
   Promote a rule that recurs (Magpie's threshold is three separate days)
   into standards the next worker must read. Do not let the ledger become
   a blog.
6. **Write the escalate-to-human rules before you turn the loop on.**
   Security-sensitive diffs, dependency or CI changes, product reversals,
   and "we cannot reproduce this" are the usual stops. An agent may
   *propose* a block list; a human decides.
7. **Cap WIP.** Limit in-flight changes and release rate until the gate
   can finish. Speed you cannot verify is waste.
8. **Instrument the loop.** Count intake, time-to-reproduce, rework rate,
   cancelled CI, open vs closed work, and human-gate latency. If you
   cannot see inventory, you do not have a factory; you have a vibe.

Copy prompts last, if at all. The Magpie loop texts are one operator's
standing orders, not a standard, and they are not in the repo.

## Failure modes

- **Throughput theater.** Stars, tags, and "25 releases in 24 hours" are
  not quality. Magpie's own lessons show same-day rework and cancelled CI
  as first-class failures.
- **Entropy from auto-merge.** A third loop whose job is "clean the
  mountain" is a confession that intake + merge outran standards. It is
  also a second writer on the same tree.
- **Self-graded work.** The same session implements, tests, and declares
  done. Require an instrument the implementer does not own.
- **Untrusted intake.** Malicious issues, look-alike PRs, social
  engineering against the official account, and community patches that
  harvest cookies or evade bot detection are documented failure classes
  in the Magpie case (`references/due-diligence.md`).
- **ToS and account risk.** A gateway that pours one vendor's plan into
  another agent may violate that vendor's terms. Magpie withdrew its
  built-in Antigravity path after Google account bans; treat "use any
  subscription in any agent" as a product claim with residual risk.
- **No escalate-to-human rule.** Either the human is paged constantly, or
  a silent failure ships.
- **Context collision.** Parallel loops, one checkout, crossed commits.
  LESSONS.md records two sessions in one checkout shipping each other's
  files.
- **Hype contamination.** Commentators will name a "software factory
  methodology" the operator never used. Separate his words from their
  reconstructions. That separation is the point of
  `references/due-diligence.md`.

## When not to use this

- The work has no checkable "done" (early research, pure taste, a pitch).
- You cannot pay for review time, reproduction hardware, or CI that is
  allowed to finish.
- The stakes are high (money movement, health, identity, production
  secrets) and you have not built the security stops yet.
- You are tempted to build a factory in order to have a factory. That is
  inventory.
- You only needed a model router, a CI speed-up, or a supervised fleet.
  Use those tools. This skill is the doctrine layer, not a rewrite of
  [`fleet-orch`](../fleet-orch/SKILL.md) or
  [`ai-native-cicd`](../ai-native-cicd/SKILL.md).

## The seed case is not the definition

Liz's question started from @yetone and Magpie, and from people on X
studying a "software factory" way of working around him. That case is
worth studying. It is not the method.

- **Product, observed:** [yetone/magpie](https://github.com/yetone/magpie)
  (MIT, Go) is a local LLM gateway and menu-bar router
  (`127.0.0.1:3425`, site [usemagpie.ai](https://usemagpie.ai)). It is
  not a factory framework. Do not confuse it with the 2024 UW/AI2
  *Magpie* alignment-data paper (`references/due-diligence.md`).
- **Method, in his own words (archived from public mirrors; the X API
  used for this pack could not read his posts):** three parallel Claude
  Code `/loop`s on official Opus 5.5, plus a nightly UI/UX window. He
  called it crude and said there was no magic. In sources reviewed for
  this pack, **he did not name it a "software factory."** Commentators
  and later write-ups did.
- **Method, in the repo (stronger evidence than any thread):**
  `LESSONS.md` opens with "magpie's code is written, reviewed, merged
  and released by agents"; `AGENTS.md` is a router to standards,
  contributor rules, and lessons; acceptance criteria require a test
  that fails without the change, real-use checks, and "not run" listed;
  merges use `--match-head-commit`.
- **What was not observable:** the loop harness is not in the repo; we
  could not retrieve his original posts or replies via the public X API
  (authorization error). Prompt texts are commentator transcriptions of
  screenshots, consistent across several write-ups.

Load `references/yetone-loops.md` for the reconstruction,
`references/due-diligence.md` for claims vs evidence, and
`references/posts/` for archived primary posts in their original
language.

## References (load on demand)

| File | What is in it |
| --- | --- |
| [`references/lineage.md`](references/lineage.md) | Historical software factories, industrialization, WIP and constraints |
| [`references/landscape.md`](references/landscape.md) | 2025–2026 comparables, kept or dropped with reasons |
| [`references/yetone-loops.md`](references/yetone-loops.md) | Seed case: his words vs reconstructions vs repo evidence |
| [`references/due-diligence.md`](references/due-diligence.md) | Identity, metrics, costs, security, hype, name collisions |
| [`references/source-index.md`](references/source-index.md) | Every "go read this" URL, fetched 2026-11-18, with status |
| [`references/posts/`](references/posts/) | Archived posts (original language) |
| [`evals/scenarios.md`](evals/scenarios.md) | Decision-ladder scenarios, not passing test evidence |
| [`../fleet-orch/refs/2026-11-21-lauren-tan-all-code-is-slop.md`](../fleet-orch/refs/2026-11-21-lauren-tan-all-code-is-slop.md) | Lauren Tan / Poteto talk note (user-supplied transcript): constraints and verification before factory automation; speaker claims kept separate from the distillation. Not a new factory definition, and not a source of throughput targets |
