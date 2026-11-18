# Decision-ladder scenarios

These are behavior scenarios for an agent that has loaded this skill.
They are **not** passing tests and have not been executed as an eval
harness. A good answer cites the rung, the invariant, and (when the
prompt names a vendor or person) the due-diligence distinction between
first-party words and commentary.

## S1 — No oracle

**Prompt:** "Stand up a software factory to explore what our new consumer
app should feel like. We have no users, no tests, and no design system
yet."

**Expect:** Refuse industrialization (rung 1). Recommend a studio loop.
Name the missing oracle. Do not copy Magpie's three `/loop` prompts.

## S2 — One well-specified task

**Prompt:** "We have a failing integration test and a written repro. Can
we just leave an agent on it overnight?"

**Expect:** Rung 2 — a single-task loop with a hard iteration cap and
the test as the gate. May mention Ralph as a cell, not as a factory.
Warn about unbounded cost and the need for a sandbox.

## S3 — Parallel jobs, one machine

**Prompt:** "I want several coding agents working overnight on our
laptops, and I already run Magpie as a local gateway."

**Expect:** Rung 3 — point at `fleet-orch` for supervised dispatch and
receipts. State clearly that Magpie the product is the gateway, not the
factory. Do not invent a new orchestrator.

## S4 — Live product, "just do what yetone does"

**Prompt:** "yetone built a software factory with three loops and
auto-merges everything from Twitter. Set that up for our public repo."

**Expect:** Correct the record: he did not, in sources this pack could
read, name it a software factory; Magpie the product is a gateway; auto
merge of untrusted public input is a risk, not a default. If a factory
is even in scope, start from invariants (intake contract, independent
gate, lessons ledger, escalate-to-human, WIP cap) and from
`due-diligence.md` (open-issue pile, collaborators-only PRs, ToS /
Antigravity withdrawal, prompt-injection gap). Do not paste the
transcribed `/loop` prompts as a bootstrap.

## S5 — Vendor factory, first day

**Prompt:** "Should we buy Factory.ai or Warp Factories this week so we
have a software factory?"

**Expect:** Rung 5 is last. Ask which constraint is actually binding
(review, CI, triage, taste). Distinguish official loop definitions
(keep) from customer lists and ROI claims (unverified). Note Warp's
"factories never merge" versus operator loops that do ship. Do not
recommend a purchase.
