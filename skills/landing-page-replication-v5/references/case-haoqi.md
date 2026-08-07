# When to load: WebGL / Lenis / HUD portfolio targets; after Static Snapshot or Scroll Compress fails
# Precondition: Studying a haoqi-class design-engineer portfolio OR validating runtime gates
# Output: Case-specific runtime patterns — do NOT cargo-cult into Attio/Linear SaaS pages

# Case study: haoqi.design → haoqi-replica (v3 stress-test → v4/v5 gates)

> Evidence tier: Verified (real build)

Evidence appendix from Composer 2.5 audit (2026-07-23) + V4.1 / v5 build logs.
Paths are environment-specific; treat as historical proof.

- Replica: `/home/ubuntu/projects/haoqi-replica`
- Docs: `docs/SIGNAL.md`, `docs/GAPS.md`, `docs/stress-test-composer-2.5-2026-07-23.md`, `docs/build-log-composer-2.5-2026-07-23.md`
- Recon: `recon/assets.json` (canvas 2160×1350), `recon/offsets.json` (`maxScroll: 12319`)

## What broke v3

| v3 gate | Result on haoqi V3/V4-pre | Reality |
|---------|---------------------------|---------|
| Hero/contact IMR ±8% | Often PASS | Frozen frames look dense |
| Loop 5 "nav/tabs/reduced-motion" | Could advance | Target has **no tabs**; identity is WebGL + scroll tunnel |
| SIGNAL Interactions (prose) | Listed Lenis/WebGL | **Not machine-checked** |
| assets.json canvas | Recorded | **Never blocked ship** |

**Root failure:** skill optimized **ink mass on screenshots**, not **runtime surface area**.

Scores from stress-test: visual ~74 / runtime ~48 / skill coverage of runtime gaps ~35.

## Target runtime inventory (identity)

| # | Behavior | Evidence |
|---|----------|----------|
| 1 | Lenis on inner scroller; doc height locked to viewport | `.lenis`, maxScroll 12,319 |
| 2 | WebGL hero theater (glass word + 3D cursor + caustics) | `assets.json` canvases |
| 3 | Scroll-linked WebGL tunnel innovate→contact (~8.4k px) | scroll-00…05 shots; contact @ 11,419 |
| 4 | Sticky innovate + scroll-driven dark field | stickyCount; HUD flips white ~78% |
| 5 | HUD instrument chrome (clock, XY, THEME, SOUND) | fixed header |
| 6 | Signature SVG path-draw | `.svg-sign__path` dashoffset |

## Replica evolution (what actually fixed the page)

| Fix | Loop that should own it | Gate that would have forced it |
|-----|-------------------------|--------------------------------|
| Scroll tunnel 6.4k → 12.5k px (99% parity) | Density / Behavior | `--scroll-length --min-ratio 0.85` |
| Inertial scroll lerp (~Lenis) | Behavior | Interaction Contract row |
| Scroll-linked CSS vars on tunnel | Behavior | scroll-state count ≥2 |
| Pointer `--rx/--ry` on glass hello | Behavior | pointer-theater (stand-in OK) |
| Signature path-draw | Micro-parity | backlog item |
| Live weather API | Polish P3 | none |

**Could NOT fix under study posture:** true WebGL meshes; photographic work boards (legal); perfect Lenis touch momentum.

## Interaction Contract example (filled)

| Interaction | Evidence | Replica strategy | Pass criterion |
|-------------|----------|------------------|----------------|
| Scroll container | `.lenis` 12319×900 | CSS lerp inertial on `.scroller` | ratio ≥ 0.85 |
| Hero theater | canvas 2160×1350 | CSS glass + SVG cursor + pointer vars | mouse move → `--rx/--ry` nonzero |
| Scroll tunnel | maxScroll 12319; sticky ~7200 | `scroll-tunnel` 5350 + stack = ~12.5k | ratio ≥ 0.85; `--tunnel-progress` changes |
| HUD invert | white @ ~78% scroll | `IntersectionObserver` / `body.is-dark` | distinct mid-scroll state |
| Reduced-motion | unknown on target | kill caustic/cursor/sound loops | no infinite animation |

## Two-Reference example

- Positive: haoqi.design (instrument portfolio + WebGL)
- Anti-reference: generic dark Inter "dev portfolio" (card stack, no HUD, no paper grid)
- Sharp edges: HUD chrome; cream paper + lime chips + `+` grid; dark innovate + glass theater

## What generalizes

- Capture `runtime.json` + `offsets.maxScroll` before Skeleton
- Interaction Contract as a **table**
- Behavior loop before polish
- CSS theater stand-in allowed **with** pointer/scroll proof
- Scroll-length is often higher leverage than another IMR band

## What does **not** generalize to Attio/Linear

- Forcing WebGL onto CRM landings that have none
- Inventing 7k-px tunnels when target is short SSR marketing
- Replacing WindowChrome tabs with HUD for SaaS product pages

If `runtime.json.flags.WEBGL_THEATER` is false, skip haoqi-specific theater rows — keep Attio/Linear density patterns.
