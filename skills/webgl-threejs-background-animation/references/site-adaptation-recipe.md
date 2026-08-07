# Site Adaptation Recipe — threejs-landing-background

Condensed from the lizliz.xyz "Paper Ink Garden" build (2026-07-18). This is the repeatable process for adapting the skill's architecture to a NEW site's brand, when the reference implementation (retail-space-planner blueprint) doesn't match the target aesthetic.

## The five decisions, in order

### 1. Theme metaphor (pick BEFORE touching code)

The reference is "architectural blueprint". Your site needs its own one-line metaphor that maps to line-based geometry. Test: can you name 3-4 geometry families that naturally belong to this metaphor?

| Site vibe | Working metaphors | Geometry families |
|---|---|---|
| Warm paper, ink, writing | Botanical plate / ink garden | spirals, bezier stems, leaves, annotation marks |
| Technical, docs, dev tools | Circuit trace / schematic | orthogonal runs, vias, pads, bus lines |
| Maps, geography, travel | Transit map | routes, stations, interchange nodes, contour lines |
| Data, analytics | Constellation chart | star points, orbit rings, connecting arcs, grid |
| Music, audio | Waveform / score | staff lines, note markers, amplitude curves |

If you can't name the geometry families in 30 seconds, the metaphor is wrong — pick another.

### 2. Palette extraction (from the site's own CSS, not invention)

Pull hex values directly from the target site's `globals.css` / theme tokens. Map them to the 4-weight hierarchy:

- `--color-ink` / `--fg` → heaviest category (`inkHeavy`)
- `--color-ink-secondary` / `--fg-secondary` → medium category
- an existing accent (`--color-accent`) → accent category — keep it constant across light/dark so the visual anchor holds
- `--color-border` / muted tones → grid + fog

Convert CSS hex → Three.js `0x` numbers verbatim. Do NOT "improve" the site's palette; the background must look like it grew out of the page.

### 3. Dark mode: lazy category builder

The reference hardcodes colors as module constants. For sites with theme switching, move CATEGORIES construction into a function:

```ts
function buildCategories(dark: boolean): CategorySpec[] {
  const ink = dark ? DARK_FG : INK
  // ...swap per-mode colors; accent usually stays constant
  return [ /* 4 entries */ ]
}
```

Call it inside the setup effect. Listen to both `prefers-color-scheme` and the site's own theme attribute (e.g. `document.documentElement.dataset.theme`) — sites with manual toggles need the attribute listener, media query alone misses manual overrides.

### 4. Geometry helpers per metaphor

Keep the `push*(seg: number[], ...)` contract (append 6 floats per segment). Write metaphor-specific helpers. From the ink garden build:

- `pushArc` (reuse from reference)
- `pushSpiral` — center-outward spiral, main flower/plant form
- `pushBezier` — sampled bezier curve → segment chain (stems, paths)
- `pushLeaf` — two mirrored arcs forming a closed leaf outline
- `pushCross` / `pushDimensionTick` — small annotation marks (botanical-plate feel)
- `pushPaperGrain` (reuse pattern: seeded-random short strokes for texture)

Density rule of thumb: total segment count across all categories should stay in the low thousands. The ink garden shipped ~2-3k segments and rendered fine on integrated GPUs.

### 5. Camera/tuning adjustments for compact compositions

The reference frames a 30-unit floor plan. A compact decorative hero (e.g. `clamp(260px, 42vw, 360px)` square) needs tighter framing:

- `camera.radius`: ~11 (vs 13)
- `camera.baseY`: ~5.5 (vs 6.5)
- `spin.base`: slower, ~0.05 — decorative pieces are contemplated, not inspected
- `fog`: match the site's page-background mid-tone, tighter range `(near 10, far 32)` for small scenes
- Keep `idleTarget` (0.32) and `idleRampSeconds` (3.5) — mobile visitors otherwise never see the dissolve

## Integration patterns proven on lizliz.xyz

- **Replacing an existing hero**: preserve the outer container's CSS (border-radius masks, overlay filters like `.home-animation-shell::after` backdrop grain) and only swap the inner element (iframe → `<HeroCanvas className="...">`). The shell CSS often carries the "blends into the page" magic — rebuilding it from scratch loses that.
- **Relocating the old animation**: don't delete the previous hero art. Move it to a secondary page (e.g. `/articles` header) at a smaller size with `loading="lazy"`. Brand assets have continuity value.
- **Sizing**: `aspect-ratio: 1/1` + `clamp()` width + `overflow: hidden` on the canvas container; the component fills the container via `clientWidth/clientHeight`, not window dimensions.
- **Bundle reality check**: three@0.185 named imports → ~540KB uncompressed / ~150KB gzip chunk on Next.js 16. Fine for a homepage hero; lazy-load (`next/dynamic`) if it lands on interior pages.

## Delegation brief shape (what worked)

When delegating the build to a subagent, the brief that produced a conforming 871-line component in one shot contained:

1. Exact palette hex table (light + dark)
2. Named 6-layer architecture + path to the reference implementation file (told to read it fully)
3. Explicit CATEGORIES list: key, color, weight, dash values, phase
4. Required geometry helper names + contracts
5. Zone-fill positions/colors/opacities
6. Full lifecycle checklist (copied from SKILL.md)
7. Exact integration diffs (old JSX → new JSX, CSS to add)
8. Verification commands + chunk-size report requirement
9. Explicit prohibitions (no R3F, no EffectComposer, no commit/push)

The two things it still needed the controller to finish: dependency install (hit a package-manager mismatch) and final verification. Budget for that tail.
