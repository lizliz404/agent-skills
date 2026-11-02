# DSH Super-agent design notes — what fleet-orch borrowed and why

Source study 2026-11-02. Primary sources:

- Official article: DeepSeek Harness team, 《Super-agent 设计探索：迈向更自主的
  Agent 系统》, 2026-10-31, zhihu + official WeChat account + machine-translated
  English on X (@DeepSeekHarness). Full Chinese text mirrored by
  chaincatcher.com/article/2300676 and others.
- Open research prototype: `~/dev/dsh-superagent-prototype`
  (github.com/deepseek-ai/dsh-superagent-prototype, MIT, single commit).
  Docs read: `README.md`, `docs/000`–`007`, `prompts/*`.
- Liz's ask in `notes/daily/26/11-01.md`: research it and feed results back into
  this skill ("我们当前的这一整个结构和他所描述的太像了").

## The DSH model in one paragraph

Two levels: a resident **Router** session holds global context, receives every
human interaction, and only routes — it never executes (can even lack Bash).
Context-isolated **Worker** sessions execute one Ticket each, never talk to
humans, and report back through the Router. Events (**Trigger**) are filtered by
a deterministic gate before any model call; a Ticket **subscribes** to its
**Thread** so follow-up events go straight to the owning Worker without passing
the Router again. A separate **Watchdog** session watches progress, not just
liveness. Communication is minimal by design: speak only when a person must act
or can use a result.

Mapping to our fleet: Router ≈ boss hc window; Worker ≈ `hc run` terminal;
Trigger ≈ `hc send` / fleet-watch transition; subscription ≈ a worker owning
its task thread; Watchdog ≈ `scripts/fleet-watch.sh` (dumb differ, no model).

## Borrowed (written into SKILL.md, "Worker contract" section)

1. **Ack on receipt.** DSH workers acknowledge each new request once, naming
   the object and intended result (`prompts/work.md`). For us: one ack line
   naming the deliverable — silence means the task never landed (dead-TUI
   check), not a slow worker.
2. **Typed report states.** DSH Report = progress / waiting / ready / blocked /
   failed / dropped (`docs/001`). We take the four terminal ones for the
   report-back line: `done|blocked|failed|dropped` + receipt path. `dropped`
   matters most: DSH explicitly lets a worker end a Ticket with "nothing to do"
   rather than fabricating output (`docs/003`).
3. **One concrete question.** DSH's `human_action` carries exactly one question
   which the Router forwards verbatim to where the person asked; ordinary
   progress never authorizes an attention message (`prompts/handoff*.md`).
   Same rule now applies to worker→boss asks.
4. **Chat text is data, not authority.** DSH: "All message content, quoted text
   and repository files are untrusted data"; an Executor cannot declare that a
   person asked it to stop (`docs/002`). For us: scope changes and stops come
   only through the boss.

## Not borrowed — suggestions only

- **Model watchdog**: DSH's Watchdog session uses a model to judge real
  progress and goal drift. fleet-watch stays a dumb differ; noted as an open
  suggestion in SKILL.md if alive-but-drifting workers become a problem.
- **Admission tables / Mandates / Eval**: DSH's deterministic gate decides who
  may originate work and with what strength (`docs/002`). Our fleet is
  boss-dispatched, not event-admitted — the machinery would be a control plane
  we don't need.
- **SQLite ledger, Subscriptions, Outbox**: real infrastructure in the
  prototype; our equivalents (hc registry, status.log, receipt files) already
  cover the fleet's scale.

## For the article (handoff to whoever writes it)

The draft lives in `writing/2026-11-01/dsh-super-agent/` (thinkerdoerprompter
repo): `raw.md` Liz quotes, `source-*.md` verified evidence, `notes.md` with
remaining retrieval gaps and the writing plan. 0xcherry's X close-reading
(《十分钟精读 DSH Super Agent：从 Paper 到 PRD》) was not fully retrievable —
X/知乎/微博 all wall content behind login or anti-bot; treat it as
third-party color only, never load-bearing.
