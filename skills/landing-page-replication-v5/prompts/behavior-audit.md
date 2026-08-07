# When to load: Loop 5 Behavior gate; after IMR passes but page feels dead; Static Snapshot triage
# Precondition: target runtime.json (or live URL) + replica URL; optional behavior-diff.json
# Output: PASS/FAIL on runtime blockers; ordered fix list

# Behavior / runtime audit prompt

Give the model **live URLs or runtime JSON** plus optional screenshots. Prefer FAIL with blockers over vague "add polish."

```text
You are checking landing-page RUNTIME fidelity — not static density.

Target runtime (from runtime.json or live probe):
- canvasCount / webgl / hasLenis / maxScroll / stickyCount
- flags: WEBGL_THEATER, INNER_SCROLLER, LENIS

Replica probe:
- same fields
- pointer path (≥3 points) on canvas/[data-theater]/[data-pointer] only: continuous transform/opacity/filter/--rx/--ry drift? (ordinary :hover does NOT count)
- scroll 0→25→50→75→100%: distinct broad-spectrum states (node transform/opacity/filter; body class/bg fallback only)

Prefer behavior-diff.json from --behavior-offline (default). Live --behavior is supplemental.

1. List BLOCKERS using only: canvas | webgl | scroll-length | pointer-theater | scroll-states | reduced-motion | smooth-nav | replica-only-motion
2. For each blocker: evidence (numbers) + smallest fix + which SIGNAL Interaction Contract row it maps to.
3. Scroll-length ratio = replica.maxScroll / target.maxScroll. Fail if < 0.85 unless GAPS waiver quoted.
4. Static Snapshot Syndrome: if target canvasCount>0 and replica canvasCount==0 and no continuous pointer theater → FAIL hard.
5. Call out replica-only motion (cursor trails, intro staggers, .magnetic) not listed as sharp edges.
6. Priority order to fix (must follow): scroll length → theater pointer/scroll linkage → sticky/HUD morph → nav/tabs → reduced-motion → a11y.
7. End with: PASS / FAIL on Behavior gate, one sentence why. Do not suggest ±2px polish while blockers remain.
```
