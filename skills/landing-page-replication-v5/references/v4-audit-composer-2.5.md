# v4 Audit — Composer 2.5

**Date:** 2026-07-24
**Reference standards:** nlpm-writing-skills, loop-creating, agent-loop article
**Scope:** All 26 files in landing-page-replication-v4

## Overall: ~82/100

| Dimension | Score |
|---|---|
| SKILL.md quality (nlpm) | 78/100 |
| Loop design | 85/100 |
| Pipeline coherence | 88/100 |
| Failure gallery vs haoqi | 90/100 |
| Tool/script quality | 80/100 |

## What v4 got right (don't regress)

1. Behavior loop as first-class citizen — the single most important structural change
2. `--behavior-offline` — turns Loop 0 artifacts into Loop 5 consequences
3. Interaction Contract table — prose → machine-checkable intent
4. haoqi as evidence anchor — case-haoqi.md prevents overfitting
5. Progressive disclosure — SKILL lean; taste-rubric + failure-gallery carry depth
6. Honest build log — documents what's still soft (Lenis feel, WebGL quality)

## Maximize roadmap

### P0 — Close verifier gaps

3 claimed blockers in SKILL.md Loop 5 are NOT in audit.py:

1. **Reduced-motion** — infinite loops can ship. Add `--reduced-motion` probe.
2. **Smooth nav** — anchor click → frame count over 600ms. Never checked.
3. **Pointer probe selectors** — too narrow (`.glass-hello, [data-theater], canvas, .hero`). Broaden.
4. **Stricter exit codes** — `--typescale` / `--density` return 2 (warn), not 1 (fail).

### P1 — SKILL.md nlpm compliance

5. Rewrite description to lead with "Use when…" + explicit v4-vs-v3 scope note
6. Add inline worked example (haoqi: IMR pass 3%, scroll ratio 0.52 → FAIL)
7. Add references/gaps-template.md (mirror signal-sheet.md)
8. Fix loop count wording: 7 phases (Loop 0–6) or renumber Capture as Loop 1
9. Number H2 sections (nlpm convention: `## 1. Section`)
10. Add quality checklist section

### P2 — Pipeline hardening

11. `scripts/validate-capture.py` — exit 1 if <5 screenshots or missing runtime.json
12. `scripts/validate-signal.py` — parse Interaction Contract; fail if P0 flags lack rows
13. pipeline.yaml: budget + logs fields
14. Wire evals.json → runnable test harness

### P3 — Nice-to-have

15. Reference or remove diff-mask.py (orphan)
16. Gallery K Inner Scroller / L Tunnel Hollow
17. Per-scroll-position screenshot IMR diff

## Loops without consequence (false-green risk)

| Claimed blocker | In audit.py? |
|---|---|
| Canvas/WebGL | ✅ |
| Scroll-length | ✅ |
| Pointer theater | ✅ (but narrow selectors) |
| Scroll-states | ✅ (but heuristic, gameable) |
| **Reduced-motion** | ❌ |
| **Smooth nav** | ❌ |
| **Replica-only motion** | ❌ |

## Methodology insight

The skill's own v4-build-log named the mechanism — "the gap wasn't missing information, it was missing consequence" — but then committed the same error on a smaller scale. The Loop 5 table lists 7 blockers; audit.py implements 4 of them. The remaining 3 are prose pretending to be gates. Every blocker in a machine-readable table MUST have a corresponding function in audit.py, or it's just more IMR-for-behavior: a feeling of verification without the mechanism.
