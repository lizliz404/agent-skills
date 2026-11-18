# Landscape — comparables, kept or dropped (surveyed 2026-11-18)

This is not a linkdump. Each entry was checked enough to say what it *is*,
how it relates to the invariants in `SKILL.md`, and whether to keep it as
a comparable. Dates are in Asia/Shanghai when converted from a source
timestamp; vendor pages that give only a date are quoted as published.

## Organizational factories (vendors)

### Factory.ai — "From coding agents to software factories"

- **Primary:** [factory.com/news/software-factory](https://factory.com/news/software-factory)
  (Matan Grinberg and Eno Reyes, dated June 15, 2026). Fetched, HTTP 200.
- **What they say:** improving individual engineers is no longer enough;
  an interconnected, agent-native, end-to-end system that improves by
  observing itself is "the software factory." Signals in (bugs, feedback,
  requirements) are triaged, planned, built, tested, reviewed, secured,
  shipped, and monitored; monitoring produces more signals. Required
  properties: model independence (or a router), "sovereign intelligence"
  (you own the learning), continual learning across the SDLC. Autonomy
  is described as a maturation process, not a switch.
- **What they claim, unverified here:** production use at "NVIDIA, EY,
  Adobe, Palo Alto Networks, Adyen, Blackstone, Wipro, Comarch and more."
  This is a company blog. Do not repeat it as fact.
- **Relation to the invariants:** the loop they draw *is* the invariant
  loop. The essay is also a product announcement. Keep it as a serious
  official definition; discount the customer list and outcome numbers
  until they are evidenced outside the vendor.

### Warp Factories

- **Primary:** Zach Lloyd, "Introducing Warp Factories,"
  [warp.dev/blog/open-infrastructure-for-building-a-software-factory](https://www.warp.dev/blog/open-infrastructure-for-building-a-software-factory)
  (August 18, 2026), and
  [docs.warp.dev/factories/how-factories-work](https://docs.warp.dev/factories/how-factories-work/).
  Both HTTP 200.
- **What they say:** interactive laptop agents created two problems —
  ROI is hard to measure, and governance is a mess when every engineer
  installs a different agent with access to everything they are logged
  into. Cloud factories are the proposed fix: intake through triage,
  specification, implementation, review, behavioral verification, human
  approval, merge, and monitoring, defined as code, with evals and
  memory. **Factories never merge**; humans approve specs, review, and
  merge. Sovereignty (BYO inference/hosting/data) is a selling point.
- **Relation:** keep. This is the cleanest official English statement
  that a factory is the *main engineering loop*, and it draws a brighter
  human-merge line than the Magpie operator loop. Closed beta / $10k
  credit offers in the blog are marketing, not evidence of results.

### Cognition / Devin

- **Site:** [cognition.ai](https://cognition.ai) redirects to
  [cognition.com](https://cognition.com/) (HTTP 200).
- **Relation:** a coding-agent / "AI software engineer" product, not a
  published factory doctrine comparable to the Factory.ai or Warp essays.
  Keep as a cell (an implementer), not as a factory definition. No
  performance claims copied here.

## Operator loops and single-task loops

### yetone / Magpie maintenance loop

The seed case. Product is a gateway; the method is an operator loop plus
repo doctrine. Full treatment: `yetone-loops.md` and `due-diligence.md`.
Keep as a high-visibility 2026 implementation, not as the definition.

### Ralph-style loops

- **Primary:** Geoffrey Huntley, "Ralph Wiggum as a 'software engineer',"
  14 July 2025, [ghuntley.com/ralph](https://ghuntley.com/ralph/) (HTTP 200).
  In its "purest form": `while :; do cat PROMPT.md | claude-code ; done`.
  Huntley presents it as a technique for greenfield work with a mechanical
  gate, "deterministically bad in an undeterministic world," tuned by
  adding signs (constraints) when it goes wrong. Field-report claims
  (overnight repos, $50k contract delivered at $297) are **claimed by
  others / in his essay**, not re-verified here.
- A Claude Code plugin named Ralph exists in marketplace listings; the
  GitHub path
  `anthropics/claude-code/plugins/ralph-wiggum/README.md` returned
  **HTTP 404** on 2026-11-18, so it is not cited as a "go read this"
  link. Prefer Huntley's page.
- **Relation:** keep as rung 2 on the ladder — a cell, not a factory.
  No multi-channel intake, no durable org learning unless the operator
  adds it.

### Supervised fleets

[`fleet-orch`](../../fleet-orch/SKILL.md) in this repo is one
implementation of supervised parallel agents on one machine (watchdog,
task cards, receipt verification). It can use Magpie as a local gateway
(`http://127.0.0.1:3425/v1`). That is rung 3. Do not duplicate its
scripts here.

## Multi-agent "virtual companies" and issue agents

### ChatDev

- Repo: [github.com/OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev)
  (HTTP 200). Paper: Qian et al., "Communicative Agents for Software
  Development," [arXiv:2307.07924](https://arxiv.org/abs/2307.07924)
  (HTTP 200).
- Agents play company roles and talk through a chat chain to produce
  software in one run. Keep as the canonical "virtual software company"
  pattern. It is a decomposition of *one* artefact, not a live-product
  factory: no standing intake, no WIP accounting, no durable lessons
  ledger unless you add them.

### MetaGPT

- Repo now at
  [github.com/FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT)
  (the older `geekan/MetaGPT` URL redirects, HTTP 200). Paper: Hong et
  al., "MetaGPT: Meta Programming for a Multi-Agent Collaborative
  Framework," [arXiv:2308.00352](https://arxiv.org/abs/2308.00352)
  (HTTP 200), later ICLR.
- Encodes SOPs so role agents (PM, architect, engineer, QA) pass
  structured artefacts, not only chat. Keep as a sibling of ChatDev:
  stronger interface discipline inside a run; still not an operating
  system for an ongoing product unless you wrap it in intake,
  verification, and memory.

### Magentic-One (Microsoft)

- Described as a generalist multi-agent system (Orchestrator plus
  specialist agents) on Microsoft Research pages. Those pages returned
  **HTTP 403** from this pack's fetch (a 403 may be kept; do not invent
  the contents). Repo context:
  [github.com/microsoft/autogen](https://github.com/microsoft/autogen)
  (HTTP 200).
- Keep as an orchestrated multi-agent *system* for complex tasks, not
  as a software-factory definition. Details beyond the public repo were
  not readable here.

### OpenHands and SWE-agent

- OpenHands (formerly OpenDevin / All Hands): repo now
  [github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
  (`All-Hands-AI/OpenHands` redirects, HTTP 200). A generalist
  software-agent platform that can work issues and PRs.
- SWE-agent: [github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
  (HTTP 200), Princeton-origin issue-solving agent.
- Keep as **cells** that can sit on a line (implement / reproduce a
  single issue). They are not factories by themselves.

## Adjacent mentions, treated carefully

- **missingstudio/eva**, "An AI-native software factory,"
  [github.com/missingstudio/eva](https://github.com/missingstudio/eva)
  (HTTP 200). Publicly pitched at @yetone in August 2026. Keep as a
  named open-source attempt; this pack did not audit its code or
  results. Do not cite stars or claims as evidence.
- **Mastra / Vercel Foreman / "eve" templates** appeared in English X
  discussion in mid-2026 as "AI software factory" branding. Not audited
  here; dropped from the comparable table until a primary doc is read.
- **Claude Code, Codex, Cursor background agents, Devin, Droid, Pi:**
  implementer harnesses. They become factory parts only when wrapped in
  the invariants.
- **Microsoft / Google "AI SDLC" material:** no single canonical public
  "software factory" essay comparable to Factory.ai or Warp was fetched
  for this pack. Do not invent one. Magentic-One is the Microsoft item
  we attempted to read (403).

## Quick map

```
signals in → triage → spec → implement → independently verify → ship → observe
                                              ↑                      |
                                              +—— lessons / evals ——-+
```

If your system is missing the arrows that change the system (lessons,
eval, WIP cap) and the independent verify step, call it a studio, a
loop, a fleet, or a swarm — not a factory.
