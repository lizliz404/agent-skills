# TUNING · Pitfalls · Acceptance

Defaults from `ProjectsMarquee.tsx` TUNING. Nudge feel here — don't scatter magic numbers.

## TUNING table

| Key | Default | Feel |
|---|---|---|
| `rows` | `2` | Uneven lanes |
| `copies` | `3` | Ultrawide fill |
| `speedBase` | `36` px/s | **Sole** horizontal speed |
| `gapMin` / `gapMax` | `16` / `44` | Hash gap variety |
| `bandPadY` | `10` | Vertical pad |
| `rowGap` | `12` | Between row slots |
| `bobAmp` | `2.5` | Visual Y bob only |
| `hoverScale` | `1.04` | Lift while stream moves |
| `scaleK` | `14` | Exp damp λ |

**Removed:** `rowSpeedScale`, `speedJitter`, `speedWobble`.

### River CSS knobs (not in TUNING object)

| Knob | Target |
|---|---|
| `::before/::after` inset | `0.35rem 0` (L/R = 0) |
| `border-radius` | `0` |
| Ripple opacity / period | ~`3.8%` fg / `17px` |
| Drift white mix | ~`8.5%` |
| Band height | `clamp(9.5rem, 19vw, 12rem)` |

### Long-press knobs

| Knob | Target |
|---|---|
| Hold duration | `600` ms |
| Move cancel | `10` px |

`damp = c + (t-c)*(1-exp(-λ·dt))` — cite webgl skill.

## Pitfalls (real bugs)

### 1. Same-row speed variance → stacked tiles
Faster tile catches slower → boxes pile. **Fix:** one `speedBase`; variety via gap/phase/Y only.

### 2. Large icons / multi-domain lazy → “failed” grey misread
Not 404s — fat PNGs at 28px + lazy. **Fix:** light SoT icons; onError letter; popup placeholder + fade.

### 3. Rounded “pool panel” instead of a river
**Symptom:** water reads as a floating rounded rectangle, not a through band.  
**Cause:** `inset` with horizontal padding + large `border-radius` on `::before`/`::after`.  
**Fix:** L/R inset `0`, `border-radius: 0`; rely on mask for edge fade; strengthen ripples (~3.5–4% / 16–18px) and drift light (~8–9%).

### 4. Touch long-press falls through to browser chrome
**Symptom:** iOS/Android link preview / callout / context menu; no OG popup.  
**Cause:** no custom gesture; `contextmenu` + `-webkit-touch-callout` left default.  
**Fix:** 600ms timer + 10px move-cancel + `contextmenu` preventDefault + touch-callout/user-select none + `suppressClick` on release after long-press. Keep fine-pointer hover path unchanged. Do **not** gate `updatePopupPosition` on `finePointer`.

### 5. Band clips popup
Portal to `body` + `position: fixed`; include `mounted` in effect deps.

### 6. mounted / effect timing
First run before portal → null popupRef. Deps must include `mounted`.

### 7. Static-export hydration false-negative probes
Wait ~5.5s; parse `matrix` `tx`, not brittle `translate3d` regex.

### 8. layoutInitial first-paint flash
Call `layoutInitial()` before `ensureLoop`.

### 9. Mobile row overlap
Raise band height or shrink tiles if `rowH < tileH`.

## Acceptance checklist (falsifiable)

- [ ] **Dual rows** on screen (`data-row` 0 and 1).
- [ ] **Uniform speed / no same-row stack:** shared |Δx/Δt|; boxes never intersect ≥3s.
- [ ] **River band form:** computed `::before` has `border-radius: 0` and spans full band width (L/R inset 0); not a rounded inset card.
- [ ] **Ripples visible:** repeating stripe opacity ≥ ~3.5% (visual check).
- [ ] **Desktop hover unchanged:** fine pointer enter → popup; leave → hide; stream keeps moving.
- [ ] **Long-press popup:** coarse pointer down 600ms → popup; release → hide; no navigation.
- [ ] **Quick tap navigates;** drag/scroll (>10px) cancels long-press (no popup).
- [ ] **No OS callout** on long-press (`contextmenu` prevented).
- [ ] **Popup in viewport** / parent is `document.body`.
- [ ] **Images:** no broken-glyph; letter fallback on error; OG fades in.
- [ ] **reduced-motion:** static grid; water anim off; popup hidden.
- [ ] **Skill icon** present at site + agent-skills paths, river motif.

## File map

| File | Role |
|---|---|
| `ProjectsMarquee.tsx` | Component (uniform speed + hover/long-press) |
| `globals.css` `.projects-marquee*` | Full-bleed river, tiles, popup, reduced-motion |
| `HomeContent.tsx` `#projects` | Full-bleed breakout |
| `scripts/fetch-project-previews.cjs` | Icon/OG SoT |
| `public/assets/icons/skills/interactive-projects-stream.svg` | Skill icon (site) |
| `agent-skills/assets/skills/interactive-projects-stream.svg` | Skill icon (repo mirror) |
