# TUNING · Pitfalls · Acceptance

Defaults from `ProjectsMarquee.tsx` TUNING (~15–36). Nudge feel here — don't scatter magic numbers.

## TUNING table

| Key | Default | Feel |
|---|---|---|
| `rows` | `2` | Max uneven lanes; denser = more GPU |
| `copies` | `3` | Fills ultrawide; drop on tiny catalogs |
| `speedBase` | `36` px/s | Base drift before row/tile scales |
| `rowSpeedScale` | `[1.08, 0.82]` | Top faster — breaks shelf sync |
| `speedJitter` | `0.42` | ±42% per-tile mul from hash |
| `speedWobble` | `0.12` | Sin amplitude on instantaneous speed |
| `gapMin` / `gapMax` | `16` / `44` | Hash-picked gap after each tile |
| `bandPadY` | `10` | Vertical pad inside band |
| `rowGap` | `12` | Space between row centers' slots |
| `hoverScale` | `1.04` | Lift while stream **keeps moving** |
| `scaleK` | `14` | Exp damp λ for scale (snappy) |

Band CSS height: `clamp(7.5rem, 16vw, 9.5rem)` — short so two favicon pills don't float in empty air. Mobile: if tiles taller than `rowH`, rows overlap → raise band height or shrink tile padding.

`damp(current, target, λ, dt) = current + (target - current) * (1 - Math.exp(-λ * dt))` — cite webgl-threejs-background-animation skill; never raw per-frame lerp.

## Pitfalls (real bugs)

### 1. Band clips popup
- **Symptom:** OG card cut off at marquee edges / invisible near fade.
- **Cause:** `overflow: hidden` + `mask-image` on `.projects-marquee`.
- **Fix:** `createPortal(popup, document.body)` + `position: fixed`; follow with viewport coords.

### 2. mounted / effect timing
- **Symptom:** Hover does nothing; no listeners; silent early return.
- **Cause:** Effect runs before portal mount → `popupRef.current === null` → return; deps omit `mounted` so never retries.
- **Fix:** `setMounted(true)` on mount; **include `mounted` in effect deps**; guard `if (!popup) return`.

### 3. Static-export hydration → false-negative speed probes
- **Symptom:** Probe says "not moving" right after load; later it moves.
- **Cause:** Static export hydrates late; rAF starts after React attach + images.
- **Fix:** Wait **~5.5s** after navigation before sampling (`probe5.py`).

### 4. Regex on `translate3d` eats numbers
- **Symptom:** Parsed X stuck / NaN; speed checks flake.
- **Cause:** Inline `style.transform` regex brittle; browsers may expose matrix only.
- **Fix:** Read `getComputedStyle(el).transform` → parse `matrix(a,b,c,d,tx,ty)` → use `tx`.

### 5. layoutInitial first-paint flash
- **Symptom:** Tiles jump from (0,0) to laid-out positions.
- **Cause:** Absolute tiles render before measure/layout runs.
- **Fix:** Call `layoutInitial()` synchronously at end of effect setup before `ensureLoop`; optional `visibility` gate until first layout.

### 6. Mobile narrow — row overlap
- **Symptom:** Two rows collide; tiles stack visually.
- **Cause:** Band height too short vs tile height + `bandPadY`/`rowGap` geometry.
- **Fix:** Raise `.projects-marquee` height clamp, or reduce tile padding / title size; re-check `rowH = usableH/rows ≥ tileH`.

## Acceptance checklist (falsifiable probes)

Browser probe (Playwright/Puppeteer-style):

- [ ] **Dual rows:** tiles with `data-row="0"` and `data-row="1"` both on-screen (or Y clusters differ).
- [ ] **Row speed diff:** mean Δx/Δt row0 > row1 (given `rowSpeedScale[0] > [1]`), sample after 5.5s hydrate wait, use matrix tx.
- [ ] **In-row variance:** same-row tiles do not share identical speed (hash jitter).
- [ ] **Popup in viewport:** on fine-pointer hover, popup `data-show="1"`, `getBoundingClientRect()` fully inside window (with 8px margin).
- [ ] **Popup not clipped by band:** popup parent is `document.body`, not inside `.projects-marquee`.
- [ ] **reduced-motion:** emulate `prefers-reduced-motion: reduce` → no rAF drift; duplicates hidden; stage is grid; popup `display:none`.
- [ ] **Keyboard:** Tab to primary tile → popup shows; Tab away → hides.
- [ ] **No console errors** during 3s observation.
- [ ] External tile has `rel` containing `noopener`.

## Research notes (why zero dep)

`react-fast-marquee` is the logo-strip default (~500k weekly npm) but cannot vary per-tile speed or host a viewport-fixed OG card without fighting CSS keyframes. FM/GSAP excel at magnetic UI but are oversized for one strip. Liz round 2 added: dual uneven rows + OG hover popup + stream keeps moving on hover (no pause — see comment at `ProjectsMarquee.tsx:11`).

## File map

| File | Role |
|---|---|
| `ProjectsMarquee.tsx` | Component (~517 lines) |
| `globals.css` `.projects-marquee*` | Band, tiles, popup, reduced-motion |
| `HomeContent.tsx` `#projects` | Full-bleed breakout |
| `webgl-threejs-background-animation` skill | exp damp + lifecycle authority |
