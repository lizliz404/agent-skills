# Armstrong's lead-agent + owner-queue model

Source post preserved verbatim: `refs/2026-11-08-brian-armstrong-2119112609223827547.md`
(Brian Armstrong, X, 2026-11-08). Distilled against this skill on 2026-11-09.

## Mapping

| His mechanism | Fleet-orch equivalent | Delta |
|---|---|---|
| One lead agent per area of focus, always running | Foreman tree (`ceo` → per-domain `fm-*` workers) | already aligned |
| A chief-of-staff agent overseeing the leads | boss/orchestrator window | already aligned |
| **One prioritized queue for every decision and review, as a simple local web app** | owner questions relayed over chat/hc; decisions scattered across receipts, task cards, morning summary | **gap**: no single durable owner inbox |
| Each review item carries screenshots + a video demo | receipts are prose-dense; captures are per-shift convention | receipts for visible work should link pixels, not describe them |
| "Brian brain": the system distills his judgment so drafts improve before review | lessons land in SKILL.md/rules ad hoc after mistakes | name the loop; measure corrections-per-change |
| One queue instead of dozens of chats → less mental overhead | single boss + consolidated summary | validates batching routine transitions into the canonical summary |
| Every change still passes human review and security checks | verify-before-report; ask-before-irreversible | validates — eliminate tasks, not judgment |

## What this changes in practice

1. **Owner queue is a first-class artifact.** Decision and review items live in a
   durable per-shift file (`~/fleet-orch/<shift>/queue.md`), not only in chat.
   Each item: verbatim ask + evidence links + suggested verdicts + state
   (open/answered/parked). The boss keeps it prioritized; unanswered items
   survive session restarts and boss handoffs. Chat pings point at the queue —
   they are notifications, not the store.
2. **Visual receipts for visible work.** A receipt for anything Liz could look
   at — UI, layout, generated media — links a screenshot or clip path.
   Prose describes; pixels prove.
3. **Judgment distillation is a standing duty.** When Liz corrects a worker, a
   routing choice, or a draft, the delta goes into durable config (this skill,
   AGENTS.md, task-card boilerplate), not just into that task's receipt.
   Success metric: fewer corrections per accepted change over time.
