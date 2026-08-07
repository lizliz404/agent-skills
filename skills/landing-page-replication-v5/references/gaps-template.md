# When to load: Loop 3+ when a gate fails but you must advance with documented rationale
# Precondition: failing gate output saved (behavior-diff.json, scroll-length, IMR, etc.)
# Output: docs/GAPS.md — one row per open gap with owner, priority, pass criterion

# GAPS template

Record **measured** failures and explicit defers. Do not use GAPS to waive gates without
numbers. Mirror structure of `references/signal-sheet.md` but for **known misses**.

## Summary

| Priority | Open | Closed this loop |
|----------|------|------------------|
| P0 | | |
| P1 | | |
| P2/P3 | | |

## Active gaps

| ID | Syndrome / gate | Measured value | Target / pass criterion | Owner | Status |
|----|-----------------|----------------|-------------------------|-------|--------|
| G1 | Scroll Compress (Gallery J) | SLR 0.52 (6429/12319) | ≥ 0.85 or intentional compress % | | open |
| G2 | Static Snapshot (Gallery I) | canvasCount 0 vs target 1 | WebGL/CSS stand-in + pointer delta | | open |
| G3 | Reduced-motion | 4 infinite CSS loops | 0 under `prefers-reduced-motion` | | open |
| G4 | Smooth nav | 1 frame / 600ms | ≥3 frames when target smooth-scrolls | | open |
| G5 | Inner Scroller (Gallery K) | doc scroll only | Lenis on inner `.lenis` scroller | | open |
| G6 | Tunnel Hollow (Gallery L) | scroll-states=1 | ≥2 distinct mid-scroll states | | open |

## Behavior blockers → GAPS mapping

Copy `blockers[]` from `recon/behavior-diff.json`. Each P0 blocker needs a row **or**
must be fixed before Loop 5 exit.

```text
blockers: ["scroll-length", "canvas", "reduced-motion"]
```

| Blocker key | Gallery | Fix or defer? |
|-------------|---------|---------------|
| scroll-length | J | lengthen tunnel / document compress % |
| canvas / webgl / pointer-theater | I | implement stand-in or P1 defer |
| scroll-states | L | add HUD invert / tunnel progress vars |
| reduced-motion | G | pause infinite animations |
| smooth-nav | — | rAF/Lenis anchor scroll |

## Waiver rationale (required for P0 defer)

For each **open P0** defer:

1. **Why defer** (scope / legal / perf):
2. **Measured gap** (numbers, not adjectives):
3. **Pass criterion** (machine-checkable):
4. **Revisit loop** (Behavior / Polish / post-ship):

## Closed gaps (archive)

| ID | Closed | Evidence |
|----|--------|----------|
| | | `audit.py --scroll-length` PASS / screenshot / PR link |
