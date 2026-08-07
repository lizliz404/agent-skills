# When to load: Loop 5 Behavior; Static Snapshot triage; writing Interaction Contract pass criteria
# Precondition: runtime.json (preferred) or live URLs; optional SIGNAL.md for sharp edges
# Output: Which blockers fire, why, and how probes are designed (so agents don't re-invent binary checks)

# Behavior gates (v5)

Machine blockers produced by `scripts/audit.py --behavior-offline` (default) or
`--behavior` (live supplemental). Every row has a corresponding function — if you
add a new named blocker to docs, implement it in `_parity_report` the same PR.

## Blocker matrix

| Blocker | Fires when | Probe |
|---------|------------|-------|
| `canvas` | Target `canvasCount>0`, replica `0`, and no continuous pointer theater | Runtime + `_continuous_pointer_delta` |
| `webgl` | Target WebGL, replica no WebGL/canvas, no continuous pointer stand-in | Runtime + pointer |
| `scroll-length` | `replica.maxScroll / target.maxScroll < 0.85` | `--scroll-length` / runtime maxScroll |
| `pointer-theater` | Target has canvas/WebGL; replica theater nodes show no continuous delta | ≥3 mouse samples on theater selectors only |
| `scroll-states` | Target `maxScroll≥4000` and replica `<2` distinct scroll fingerprints | Broad-spectrum node sampling |
| `reduced-motion` | Infinite CSS animations still running under `prefers-reduced-motion` | `--reduced-motion` |
| `smooth-nav` | Target smooth-scrolls anchors; replica `<3` motion frames / 600ms | `--smooth-nav` |
| `replica-only-motion` | Replica hits cursor-trail / stagger-intro / `.magnetic` / `[data-intro]` **and** not declared in SIGNAL sharp edges | `--replica-only` / bundled in behavior |

## Pointer probe design (anti-false-positive)

**Wrong (v4):** sample any hero/button node; compare 2 mouse points; `before !== after`
→ ordinary `:hover { transform: scale(1.02) }` clears Static Snapshot.

**Right (v5):**
1. Targets limited to `canvas`, `[data-theater]`, `[data-pointer]`
2. Sample ≥3 mouse positions along a path
3. Require **continuous** numeric drift (≥3 distinct transform/opacity/filter/CSS-var values)
4. Binary flip alone does **not** set `pointerChanged` / `continuous`

Stand-in OK note only when `continuous` or `varDelta` is true.

## Scroll-state probe design (anti-hardcoding)

**Wrong (v4):** sample `bodyClass`, `bodyBg`, `hudColor`, `--tunnel-progress` —
haoqi implementation details. GSAP/Three.js/opacity tunnels false-negative.

**Right (v5):**
1. Primary fingerprint: `transform` / `opacity` / `filter` (+ canvas count) on
   generic theater/layout nodes (`SCROLL_SIGNAL_SELECTORS`)
2. `bodyClass` / `bodyBg` are **fallback only** when primary fingerprint is flat
3. `distinctPrimary` reported alongside `distinctStates`

## Session hygiene (bot management)

| Mode | Target hits | Replica sessions | When |
|------|-------------|------------------|------|
| `--behavior-offline` (**default**) | 0 (uses `runtime.json`) | 1 merged | Always prefer |
| `--behavior` | 1 merged session (runtime + smooth-nav) | 1 merged | Only if runtime.json stale |

v4 opened a fresh Chromium per probe (6–7 target hits). That conflicts with
Capture Router's Bot Management warning. Do not regress.

## Commands

```bash
python3 scripts/audit.py --behavior-offline recon/runtime.json {replica} \
  --signal docs/SIGNAL.md --out recon/behavior-diff.json
python3 scripts/audit.py --replica-only {replica} --signal docs/SIGNAL.md
python3 scripts/audit.py --reduced-motion {replica}
python3 scripts/audit.py --smooth-nav {replica}
```

## Priority order (theater-runtime-first)

1. Scroll container + length ratio
2. WebGL/CSS theater pointer + scroll linkage
3. Sticky / scroll-driven scene morph
4. Observer-based nav / tabs
5. `prefers-reduced-motion`
6. a11y (theater `aria-hidden`)

## Habit check

Before adding any "looks like a gate" check, ask: **does this execute a real
probe with a fail exit code, or is it string/binary theatre?**
