# Build Log — landing-page-replication v3 → v4

**Agent:** Cursor Grok 4.5 high
**Date:** 2026-07-24
**Input:** 3 audit files (stress-test-composer-2.5 + build-log-composer-2.5 + GAPS.md) + v3 skill full source
**Output:** `/home/ubuntu/.hermes/skills/web/landing-page-replication-v4/` (25 files)

## What changed

1. **New Loop 5 — Behavior** (was under-scoped Polish in v3). Machine gates for runtime parity: canvas/WebGL, scroll-length ratio, pointer-linked theater, scroll-state count. Blocks ship on "IMR pass, page dead."

2. **capture-runtime.py** (207 lines) — Playwright capture of canvasCount, WebGL, Lenis, maxScroll, scroll-state samples → `runtime.json`. The gate that would have killed V3 static immediately.

3. **audit.py upgraded** — `--scroll-length --min-ratio 0.85`, `--behavior`, `--behavior-offline`. pipeline.yaml has 19 behavior/runtime references.

4. **Scroll-length ratio gate** — `replica/target ≥ 0.85` hard gate in Loop 3 + Loop 5. Failure Gallery J for scroll-compress.

5. **Interaction Contract** — SIGNAL.md now has a machine-checkable table (evidence / strategy / pass criterion per interaction), not prose.

6. **Failure Gallery I — Static Snapshot Syndrome** — `assets.json` has canvas; replica doesn't. Hard block in Loop 5.

7. **case-haoqi.md** — WebGL portfolio domain fork as evidence anchor for runtime gates.

8. **behavior-audit.md prompt** — Loop 5 behavior critique template.

9. **Replica-only motion guard** — Loop 4 bans cursor trails / intro staggers not in Interaction Contract (Grok's G9 finding).

## Pipeline shape

```
Capture → Signal → Skeleton → Density → Micro-parity → Behavior → Polish
  6 loops                          NEW ↑
```

## What the audits drove

| Audit source | v4 outcome |
|---|---|
| Composer 2.5 stress test: "IMR passes frozen hero; canvasCount=0 ships" | Loop 5 Behavior + capture-runtime + Hard block |
| Composer 2.5: "scroll compressed 43%; no gate" | `--scroll-length --min-ratio 0.85` (Loop 3+5) |
| Composer 2.5: "Loop 5 nav/tabs-centric" | Theater-runtime-first priority order |
| Build log: "scrollHeight gate would have flagged V4 #1 gap" | Scroll-length ratio now a machine gate, not a human note |
| GAPS.md: "Interaction Contract = prose" | Structured table with pass criterion per row |

## What remains unaddressed

- Lenis vs native scroll: gate checks ratio, not inertia quality
- WebGL vs CSS stand-in: gate requires `canvasCount > 0` OR proven CSS+pointer reactivity — but CSS quality is still human judgment
- No automated scroll-state visual diff (needs per-state screenshots + IMR)
- Evals #6–#8 added but not yet run against live targets

## Methodology insight

The single highest-leverage fix was NOT adding a new loop — it was making an existing Loop 0 artifact (`assets.json` / scroll offsets) feed a machine gate that BLOCKS. V3 had the data; it just never transformed it into a decision. The gap wasn't missing information — it was missing consequence.
