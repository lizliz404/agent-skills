# Lineage — industrialization of software, before this hype cycle

This note exists so the skill is not ahistorical. "Software factory" was a
term of art twenty years before anyone routed Claude Code at a public
issue tracker. The 2025–2026 wave changes the workers, not the invariants
in `SKILL.md`.

Confidence labels used here and in the rest of this pack: **observed**
(primary source opened for this pack), **inferred**, **claimed by others**,
**unverified**.

## Microsoft Software Factories (2004)

Jack Greenfield, then at Microsoft, stated the motivation in "The Case for
Software Factories" (MSDN, July 2004): other industries raised capacity by
moving from craftsmanship — whole products made from scratch by individuals
or small teams — to manufacturing, where variants are assembled from
reusable components and machines take rote work. A Software Factory, in
that vocabulary, is "a development environment configured to support the
rapid development of a specific type of application." The key is not to
turn developers into drones; it is to stop wasting scarce skilled time on
end products that will be replaced in months.

The book is *Software Factories: Assembling Applications with Patterns,
Frameworks, Models & Tools* (Greenfield and Keith Short, with Steve Cook
and Stuart Kent; Wiley, September 2004, ISBN 0471202843). The companion
site [softwarefactories.com](https://softwarefactories.com/) frames a
coming capacity crisis and defines a factory as a software product line
that configures extensible tools with DSLs, patterns, frameworks, and
guidance so a family of similar systems can be produced quickly. The
OOPSLA 2003 paper "Software Factories" (Greenfield et al., PDF at
[s23m.com/oopsla2003/greenfield.pdf](https://s23m.com/oopsla2003/greenfield.pdf))
puts the same confluence — components, model-driven development, product
lines — in academic form.

**Observed, and still the right first principle:** industrialization is
systematic reuse plus automation of rote work, aimed at a *family* of
products, not a smarter typist for a one-off.

**What does not transfer naively:** 2004 factories assumed human
developers plus models and code generation. They did not assume
non-deterministic workers, prompt injection, or verification as the
scarce resource. Do not pretend the Microsoft method "predicted" LLM
loops.

## CMMI, product lines, and the older factory metaphor

Long before Greenfield, people used "software factory" loosely for any
attempt to run development like a plant: standard processes, stages,
handoffs, and measured output. CMMI and ISO-style process maturity, cleanroom
methods, and software product-line engineering (SEI) all contributed
vocabulary — work intake, defined stages, verification gates, organizational
learning. This pack does not re-litigate that literature. Two cautions:

- Process maturity without a real oracle becomes paperwork. That failure
  mode recurs in AI factories that emit tags and dashboards.
- "Industrialization" has always been sold ahead of evidence. Treat 2026
  vendor essays the way a skeptical reader treated 1990s CMM theatre.

## Constraints, inventory, and WIP

Two operations ideas are load-bearing for this skill, and they are not
AI ideas.

- **Eliyahu Goldratt, *The Goal* (1984), Theory of Constraints.** Throughput
  of a line is set by its bottleneck. Adding capacity upstream of the
  constraint only grows inventory. In an LLM factory the bottleneck is
  usually reproduction, review, CI that is allowed to finish, or human
  taste — not token generation. Magpie's own `LESSONS.md` (observed) is a
  worked example: 294 tags in 51 hours left no CI run to finish, after
  which a rule was added that a cancelled run is not a pass.
- **WIP limits (lean / Kanban).** Visible work-in-process, and a cap on
  it, are what keep a line from looking busy while nothing ships ready.
  Release-rate caps, merge queues, and "one loop may not start another
  change until the last one is verified" are WIP limits. A swarm with no
  cap is not lean; it is a pile.

Handoff cost is the third old idea: every interface between stages
(spec → implement → review → ship) loses information. Written contracts
(acceptance criteria, "what was run at which head," escalate-to-human
rules) exist to make handoffs cheap enough that division of labor is
worth it. ChatDev-style role play that happens inside one context window
avoids some handoff cost and also avoids durable memory; that is why it
is a different shape (see `landscape.md`).

## The 2023–2026 shift

What is new is not the factory metaphor. It is that generation became
cheap, noisy, and always-on, while independent checking did not.

- 2023–2024: "virtual software company" multi-agent papers (ChatDev,
  MetaGPT) and issue-solving agents (SWE-agent, later OpenHands). These
  are mostly single-run or single-issue systems.
- 2025: single-task loops popularized as "Ralph" (Huntley): a bash `while`
  around a coding agent until a mechanical gate or a cap.
- 2026: vendors re-claim "software factory" for an instrumented SDLC
  (Factory.ai, June 2026; Warp Factories, August 2026), and a few
  operators show a live-product loop that reads public feedback, changes
  a real repo, and ships. yetone's Magpie maintenance practice is one
  such operator loop. It is a data point, not a standard.

The invariant that survived every generation: **the line is only as real
as its gate and its memory.**
