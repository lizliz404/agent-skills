# TUNING · Pitfalls · Acceptance

Defaults from `ProjectsMarquee.tsx` TUNING (~18–36). Nudge feel here — don't scatter magic numbers.

## TUNING table

| Key | Default | Feel |
|---|---|---|
| `rows` | `2` | Max uneven lanes; denser = more GPU |
| `copies` | `3` | Fills ultrawide; drop on tiny catalogs |
| `speedBase` | `36` px/s | **Sole** horizontal speed — all tiles identical |
| `gapMin` / `gapMax` | `16` / `44` | Hash-picked gap after each tile (primary variety) |
| `bandPadY` | `10` | Vertical pad inside band |
| `rowGap` | `12` | Space between row centers' slots |
| `bobAmp` | `2.5` | Optional sin Y bob (px); visual only, not speed |
| `hoverScale` | `1.04` | Lift while stream **keeps moving** |
| `scaleK` | `14` | Exp damp λ for scale (snappy) |

**Removed (do not reintroduce):** `rowSpeedScale`, `speedJitter`, `speedWobble` — same-row speed diffs → stacking (Liz 2026-08).

Band CSS height: `clamp(7.5rem, 16vw, 9.5rem)` — short so two favicon pills don't float in empty air. Mobile: if tiles taller than `rowH`, rows overlap → raise band height or shrink tile padding.

`damp(current, target, λ, dt) = current + (target - current) * (1 - Math.exp(-λ * dt))` — cite webgl-threejs-background-animation skill; never raw per-frame lerp.

## Pitfalls (real bugs)

### 1. Same-row speed variance → stacked tiles
- **Symptom:** One card overlaps another in the same row; feels like boxes piled on boxes.
- **Cause:** Per-tile `speedJitter`, per-row `rowSpeedScale`, and/or `speedWobble` make faster tiles catch slower ones while gaps shrink to negative.
- **Fix:** One `speedBase` for all floaters. Keep variety via hash `gapAfter`, row `phaseShift`, Y jitter/bob only. After unify, `wrapFloaters` preserves constant gaps forever.

### 2. Large icons / multi-domain lazy → “failed placeholder” misread
- **Symptom:** Grey icon squares look like broken images (esp. mobile / slow net).
- **Cause:** Not hard 404s — oversized icons (e.g. 248KB / 331KB PNG shown at 28px) + many cross-origin lazy loads → long grey background period.
- **Fix:** Data SoT (`FALLBACKS`/`CURATED` in `fetch-project-previews.cjs`) → existing light svg/32px; regenerate JSON. Component: tile `onError` letter fallback (no broken glyph); `onLoad` fade-in; popup media placeholder + fade until OG loads. Keep `loading="lazy"` + `decoding="async"`.

### 3. Band clips popup
- **Symptom:** OG card cut off at marquee edges / invisible near fade.
- **Cause:** `overflow: hidden` + `mask-image` on `.projects-marquee`.
- **Fix:** `createPortal(popup, document.body)` + `position: fixed`; follow with viewport coords.

### 4. mounted / effect timing
- **Symptom:** Hover does nothing; no listeners; silent early return.
- **Cause:** Effect runs before portal mount → `popupRef.current === null` → return; deps omit `mounted` so never retries.
- **Fix:** `setMounted(true)` on mount; **include `mounted` in effect deps**; guard `if (!popup) return`.

### 5. Static-export hydration → false-negative speed probes
- **Symptom:** Probe says "not moving" right after load; later it moves.
- **Cause:** Static export hydrates late; rAF starts after React attach + images.
- **Fix:** Wait **~5.5s** after navigation before sampling (`probe5.py`).

### 6. Regex on `translate3d` eats numbers
- **Symptom:** Parsed X stuck / NaN; speed checks flake.
- **Cause:** Inline `style.transform` regex brittle; browsers may expose matrix only.
- **Fix:** Read `getComputedStyle(el).transform` → parse `matrix(a,b,c,d,tx,ty)` → use `tx`.

### 7. layoutInitial first-paint flash
- **Symptom:** Tiles jump from (0,0) to laid-out positions.
- **Cause:** Absolute tiles render before measure/layout runs.
- **Fix:** Call `layoutInitial()` synchronously at end of effect setup before `ensureLoop`; optional `visibility` gate until first layout.

### 8. Mobile narrow — row overlap
- **Symptom:** Two rows collide; tiles stack visually.
- **Cause:** Band height too short vs tile height + `bandPadY`/`rowGap` geometry.
- **Fix:** Raise `.projects-marquee` height clamp, or reduce tile padding / title size; re-check `rowH = usableH/rows ≥ tileH`.

### 9. Pre-hydration load/error events are lost (static export)
- **Symptom:** Icons stay invisible (opacity 0 fade never fires) or show an empty icon block even though the URL loads/fails fine on curl.
- **Cause:** Static-export HTML ships `<img src>`; the browser may load (or fail) the image BEFORE React hydrates and attaches `onLoad`/`onError` — those events fire once and are gone. React handlers alone can't cover it.
- **Fix:** In the effect setup, backfill BOTH terminal states for every tile img: `im.complete && im.naturalWidth > 0` → add `is-loaded`; `im.complete && naturalWidth === 0` → mirror the onError fallback (`display:none` + `data-failed=1`). Keep React `onLoad`/`onError` for images that finish after hydration.
- **Also verify content-type, not just HTTP 200:** a SPA fallback (CF Pages single-page app) returns `text/html` 200 for ANY path — a "200 favicon.svg" that is actually HTML renders as naturalWidth=0 in browsers while curl reports success. Confirm with `curl -sI` content-type or a real-browser `naturalWidth` check (pausey 2026-08: `favicon.svg` → text/html, `favicon.png` → image/png 2.8KB).

## Acceptance checklist (falsifiable probes)

Browser probe (Playwright/Puppeteer-style):

- [ ] **Dual rows:** tiles with `data-row="0"` and `data-row="1"` both on-screen (or Y clusters differ).
- [ ] **Uniform speed / no same-row stack:** sample matrix `tx` over Δt after 5.5s hydrate wait — all tiles share the same |Δx/Δt| (±ε); same-row bounding boxes never intersect during ≥3s observation.
- [ ] **Gap variety only:** same-row gaps differ (hash), but relative order/spacing preserved over time.
- [ ] **Popup in viewport:** on fine-pointer hover, popup `data-show="1"`, `getBoundingClientRect()` fully inside window (with 8px margin).
- [ ] **Popup not clipped by band:** popup parent is `document.body`, not inside `.projects-marquee`.
- [ ] **OG placeholder:** while loading, media shows background; after load `data-loaded="1"` and img visible; no permanent grey “failed” look for successful URLs.
- [ ] **Images zero-fail UX:** no browser broken-image icons; failed loads show letter fallback (`data-failed="1"`).
- [ ] **reduced-motion:** emulate `prefers-reduced-motion: reduce` → no rAF drift; duplicates hidden; stage is grid; popup `display:none`.
- [ ] **Keyboard:** Tab to primary tile → popup shows; Tab away → hides.
- [ ] **No console errors** during 3s observation.
- [ ] External tile has `rel` containing `noopener`.

## Research notes (why zero dep)

`react-fast-marquee` is the logo-strip default (~500k weekly npm) but cannot host a viewport-fixed OG card without fighting CSS keyframes. FM/GSAP excel at magnetic UI but are oversized for one strip. Liz feedback (2026-08): dual rows + OG hover popup + stream keeps moving on hover (no pause); **speed must be uniform** to avoid confusing same-row stacks; large lazy icons misread as failures.

## File map

| File | Role |
|---|---|
| `ProjectsMarquee.tsx` | Component (~556 lines) |
| `globals.css` `.projects-marquee*` | Band, pool surface, tiles, popup, reduced-motion |
| `HomeContent.tsx` `#projects` | Full-bleed breakout |
| `scripts/fetch-project-previews.cjs` | Icon/OG SoT (`FALLBACKS`/`CURATED`) |
| `webgl-threejs-background-animation` skill | exp damp + lifecycle authority |
