---
name: landing-page-replication-v5
description: >-
  Use when replicating marketing/SaaS/D2C landings or WebGL/Lenis/scroll-theater
  portfolios to measurable fidelity. v5 keeps v4's Loop 5 Behavior gates and
  closes three "missing consequence" relapses: replica-only-motion blocker,
  continuous pointer-theater probe (no :hover false positives), broad-spectrum
  scroll-state sampling. Prefer --behavior-offline. Capture → signal → skeleton
  → density → micro-parity → behavior → polish.
entrypoint: SKILL.md
estimated_context_tokens: ~2800
phases: [capture, signal-sheet, skeleton, density, micro-parity, behavior, polish]
version: 5.0.0
---

# Landing Page Replication (v5)

Domain-agnostic **7-phase** pipeline (Loop 0–6). Case specifics live in
`references/case-*.md`. Load references on demand.

**Why v5:** v4 taught "missing consequence, not missing information" — then
relapsed three levels deeper (docs naming a blocker with no function; pointer
probe beaten by ordinary `:hover`; scroll-state hardcoding haoqi fields;
self-test as string theatre; `--behavior` bombarding the target). v5 makes
those gates real. Detail: `references/v5-build-log.md`.

**Worked example (haoqi):** Hero IMR Δ **3%** (pass) + SLR **0.52** → **FAIL**
(`--scroll-length`). Fix tunnel height before ±2px chase. Gallery **J**.

## 1. Risk posture + legal

| Posture | When | Behavior |
|---------|------|----------|
| **Study / internal-only** | Never ships publicly | Single positive target OK; pick one anti-reference |
| **Ship as your product** | Live commercial product | Composite **3–5** leaders; never name source publicly; then `brand-distinction-v1` |

If unsure → **Ship**. Replicate design *language*; never copy logos, proprietary
imagery, or hotlink target fonts. (Not legal advice.) Full IP notes:
`references/ip-and-fonts.md`.

## 2. Pipeline

```text
Capture → Signal Sheet → Skeleton → Density → Micro-parity → Behavior → Polish
   │           │             │          │           │             │
   capture.py  SIGNAL.md     tokens     --imr       sharp edges   --behavior-offline  ← default
   capture-runtime.py                   --scroll-length           (--behavior live = supplemental)
```

Gates: `pipeline.yaml`. Checklists: `references/fidelity-checklist.md`.
Behavior matrix: `references/behavior-gates.md`.

### Loop 0 — Capture

Reconstruct story arc, type/color roles, density, **and runtime surface**.

**Two-Reference Rule** before Loop 1: positive target + anti-reference + 3 sharp edges.

```bash
python3 scripts/capture.py --url https://target.com --out recon/
python3 scripts/capture-runtime.py --url https://target.com --out recon/runtime.json
python3 scripts/validate-capture.py recon/
```

Route by fingerprint (`references/capture-router.md`). Bot Management is the
2026 default failure mode — do not re-hit the live target later for verification.

**Gate:** `validate-capture.py` PASS; ≥5 screenshots; `runtime.json` with
`canvasCount` / `webgl` / `maxScroll` / `hasLenis` (or static N/A). Tag
`WEBGL_THEATER` when `canvasCount > 0`.

### Loop 1 — Signal Sheet

```bash
python3 scripts/extract-tokens.py recon/index.html --base-url https://target.com
python3 scripts/validate-signal.py docs/SIGNAL.md recon/runtime.json
```

Write `docs/SIGNAL.md` from `references/signal-sheet.md`. Must include
**Interaction Contract** table (evidence / strategy / pass criterion) for every
P0 runtime signal — not prose. Template + fields: signal-sheet.md.

### Loop 2 — Skeleton

Tokens for roles used 3+ times. Reserve scroll-tunnel height from
`offsets.json` / `runtime.json.maxScroll`. Gate: `audit.py --typescale`.

### Loop 3 — Density

Pin shots at 0 / 25 / 50 / 75 / 100% scroll. Cut a weak section before adding more.

```bash
python3 scripts/audit.py --imr target.png replica.png --tolerance 8
python3 scripts/audit.py --density {replica_url}
python3 scripts/audit.py --scroll-length recon/offsets.json {replica_url} --min-ratio 0.85
```

Scroll-length fail blocks exit unless `docs/GAPS.md` waiver (Gallery **J**).

### Loop 4 — Micro-parity

Implement Two-Reference sharp edges. Font metrics: `metric-align-fonts.py`.
Do **not** invent replica-only motion unless listed as a sharp edge — now a
**machine blocker** in Loop 5 (`replica-only-motion`).

### Loop 5 — Behavior

Prove every P0 interaction live — not via frozen PNG.

```bash
# Recommended default (1 replica session; target from runtime.json):
python3 scripts/audit.py --behavior-offline recon/runtime.json {replica_url} \
  --signal docs/SIGNAL.md --out recon/behavior-diff.json
python3 scripts/audit.py --reduced-motion {replica_url}
# Live re-probe of target only when runtime.json is stale (1 shared target session):
# python3 scripts/audit.py --behavior {target} {replica_url} --signal docs/SIGNAL.md
```

Blockers (all implemented in `audit.py` — see `references/behavior-gates.md`):
`canvas` | `webgl` | `scroll-length` | `pointer-theater` | `scroll-states` |
`reduced-motion` | `smooth-nav` | `replica-only-motion`

Theater-runtime-first priority: scroll length → theater pointer/scroll → sticky
morph → nav/tabs → reduced-motion → a11y.

**Gate:** `behavior-diff.json` blockers empty **or** each deferred in GAPS with
pass criterion. Gallery **I** fails hard.

### Loop 6 — Polish

a11y → LCP → ±2px on P0 only. Do not polish while Loop 5 blockers remain.

## 3. Tool routing

| Need | Tool |
|------|------|
| Capture / runtime | `capture.py`, `capture-runtime.py`, `validate-capture.py` |
| Tokens / signal | `extract-tokens.py`, `validate-signal.py` |
| Density / type | `audit.py --imr/--diff/--typescale/--density/--rhythm` |
| Scroll-length | `audit.py --scroll-length` |
| Behavior (default) | `audit.py --behavior-offline` |
| Behavior (live supplemental) | `audit.py --behavior` (merged sessions) |
| Motion guards | `--reduced-motion` / `--smooth-nav` / `--replica-only` |
| Fonts | `metric-align-fonts.py` |
| Critique prompts | `prompts/density-critique.md`, `prompts/behavior-audit.md` |
| Self-test | `run-evals.py --self-test` (executes subcommands on fixtures) |

## 4. Common failure modes

| Failure | Fix |
|---------|-----|
| 403 / bot challenge | Manual DevTools — legitimate Loop 0 |
| IMR pass, live page dead | Loop 5; Gallery **I** |
| Page ~40% shorter | `--scroll-length`; Gallery **J** |
| Inner scroller missed | Gallery **K** |
| Long page, one scroll state | Gallery **L** (broad-spectrum sampling in v5) |
| Ordinary `:hover` "proves" theater | v5 continuous theater-node probe |
| Replica-only cursor trail | `--replica-only` / Loop 5 blocker |
| `--behavior` hammering target | Use `--behavior-offline` |
| Self-test string theatre | v5 `--self-test` executes audit subcommands |

## 5. Output layout

```text
recon/   index.html headers.txt css/ screenshots/ computed.json dom.html
         runtime.json assets.json offsets.json behavior-diff.json
docs/    SIGNAL.md  GAPS.md
src/     tokens + primitives + sections + animations/ + data.ts
```

## 6. References (load on demand)

| File | When |
|------|------|
| `behavior-gates.md` | Loop 5 blocker matrix + probe design |
| `taste-rubric.md` / `failure-gallery.md` | Density + runtime syndromes |
| `capture-router.md` | Non-SSR / bot-blocked Loop 0 |
| `gaps-template.md` / `signal-sheet.md` / `fidelity-checklist.md` | Contracts + exits |
| `ip-and-fonts.md` / `product-theater.md` | Fonts, trade dress, theater stand-ins |
| `case-*.md` / domain forks | Evidence-tiered case notes |
| `v5-build-log.md` | What changed vs v4 |

## 7. Verification

```bash
pip install -r scripts/requirements.txt
python3 scripts/validate-capture.py recon/
python3 scripts/validate-signal.py docs/SIGNAL.md recon/runtime.json
python3 scripts/audit.py --imr target.png replica.png --tolerance 8
python3 scripts/audit.py --scroll-length recon/offsets.json http://127.0.0.1:5173 --min-ratio 0.85
python3 scripts/audit.py --behavior-offline recon/runtime.json http://127.0.0.1:5173 \
  --signal docs/SIGNAL.md --out recon/behavior-diff.json
python3 scripts/run-evals.py --self-test
```

## 8. Quality checklist

- [ ] Loop 0: `validate-capture.py` PASS; runtime.json or static N/A
- [ ] Loop 1: `validate-signal.py` PASS; Interaction Contract covers P0 flags
- [ ] Loop 3: IMR mid-scroll bands; SLR ≥0.85 or GAPS row
- [ ] Loop 5: `--behavior-offline` blockers empty or each in GAPS
- [ ] Loop 5: `--reduced-motion` PASS; smooth-nav when target smooth-scrolls
- [ ] No undeclared replica-only motion
- [ ] `run-evals.py --self-test` PASS (subcommand execution, not grep-only)
- [ ] P0 gaps closed; P2/P3 listed in GAPS.md

## 9. v4 → v5 delta

| Hole in v4 | v5 fix |
|------------|--------|
| `replica-only-motion` named in 4 docs, absent in `_parity_report` | `_replica_only_motion` + blocker |
| Pointer 2-point / hero-button `:hover` false positive | ≥3-point continuous delta on `canvas`/`[data-theater]`/`[data-pointer]` only |
| Scroll-state sampling hardcoded to haoqi fields | Broad transform/opacity/filter sampling; body class/bg fallback only |
| `--self-test` string-matching theatre | Executes each audit subcommand on fixtures |
| `--behavior` opens 6–7 Chromium sessions against target | Target probes merged to 1 session; `--behavior-offline` is default |
| case-*.md evidence weight unclear | Evidence tier labels |
| Fake logo-cloud brand collision | Note in `ip-and-fonts.md` |
