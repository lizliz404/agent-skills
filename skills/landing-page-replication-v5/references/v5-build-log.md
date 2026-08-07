# Build Log — landing-page-replication v4 → v5

**Agent:** Cursor Grok 4.5
**Date:** 2026-07-24
**Input:** v4 skill tree + `references/audit-v5-liz.md` (P0/P1/P2)
**Output:** `/home/ubuntu/.hermes/skills/web/landing-page-replication-v5/`
**Constraint:** v4 directory untouched

## What changed

### P0 — three "missing consequence" relapses

1. **`replica-only-motion` blocker** — `_replica_only_motion()` + `--replica-only` CLI; wired into `_parity_report` / behavior bundles. Hits `cursor-trail` / `stagger-intro` / `.magnetic` / `[data-intro]` unless declared in SIGNAL sharp edges (`--signal`).

2. **`_pointer_reactivity` continuity** — theater selectors only (`canvas`, `[data-theater]`, `[data-pointer]`); ≥3 mouse samples; `_continuous_pointer_delta` requires ≥3 distinct numeric snapshots. Ordinary `:hover { transform: scale(1.02) }` no longer clears Static Snapshot.

3. **`_scroll_state_count` broad-spectrum** — primary fingerprint = `transform`/`opacity`/`filter` (+ canvas) on `SCROLL_SIGNAL_SELECTORS`; `bodyClass`/`bodyBg` fallback only when primary is flat. haoqi `--tunnel-progress` / HUD color no longer the sole signal.

### P1 — self-test + session hygiene

4. **`run-evals.py --self-test`** — still checks file/flag presence, then **executes** `--imr`, `--diff`, `--rhythm`, `--typescale`, `--density`, `--scroll-length`, `--reduced-motion`, `--smooth-nav`, `--replica-only`, `--behavior-offline` against temp PNG + local HTTP fixtures. Live `--behavior` is CLI-verified only (does not hit external targets).

5. **`--behavior` session merge** — `_run_target_session` / `_run_replica_session` pack probes into one Chromium each. **`--behavior-offline` is the Loop 5 default** in SKILL.md, pipeline.yaml, checklists, and prompts.

### P2 — docs

6. Evidence tier labels on `case-haoqi.md`, `case-attio.md`, `case-linear.md`, `ecommerce-storefront.md`, `cjk-independent-site.md`.
7. Fake logo-cloud / brand-collision note in `ip-and-fonts.md`.

### Structure

8. Leaner `SKILL.md` (~estimated 2800 tokens); depth extracted to new `references/behavior-gates.md`.
9. Version bumps: skill name / pipeline / evals / UA strings → v5.
10. Historical v4 / v4.1 build logs retained for provenance (not rewritten as truth for v5).

## Files touched (high-signal)

| Path | Change |
|------|--------|
| `scripts/audit.py` | P0+P1 probes, merged sessions, `--replica-only`, `--signal` |
| `scripts/run-evals.py` | Executable self-test |
| `SKILL.md` | v5 lean loop doc; offline default |
| `pipeline.yaml` | v5; behavior-offline gate |
| `references/behavior-gates.md` | New |
| `references/v5-build-log.md` | This file |
| case / IP / gallery / rubric / fidelity / prompts | P2 + probe wording |

## Verification

```bash
python3 -m py_compile scripts/audit.py scripts/run-evals.py   # OK
python3 scripts/run-evals.py --self-test                      # PASS (8 evals)
# Pillow path executed: --imr --diff --rhythm
# Playwright URL probes skipped with notes when playwright not installed
# Unit: _continuous_pointer_delta rejects binary hover; accepts ≥3 distinct transforms
# Unit: _parity_report emits replica-only-motion + ignores non-continuous pointerChanged
```

Not verified live: full Chromium `--behavior-offline` against a real replica (playwright absent in build env). Install `playwright` + browsers to exercise URL gates.

## Methodology insight

v4 fixed "prose pretending to be a gate" once (loop table → functions). The same disease relapsed inside probe design (binary comparison; haoqi-hardcoded fields) and inside the harness that claims to prevent relapse (string grep self-test). v5 habit: **every new gate must execute something falsifiable**, not merely name a syndrome.

## Not in scope (audit P1 stress-test suggestion)

Next real stress-test should target an independent-site / cross-border e-commerce URL (not another WebGL n=1). That is a future project run, not a skill-tree edit.
