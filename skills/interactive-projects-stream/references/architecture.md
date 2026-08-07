# Architecture — Interactive Projects Stream

Authority: `ProjectsMarquee.tsx`. CSS: `globals.css` `.projects-marquee*`. Layout: `HomeContent.tsx` `#projects` full-bleed.

Motion helpers (`damp`, dt cap, IO/visibility) — cite `webgl-threejs-background-animation` skill; don't duplicate.

## River band (CSS form)

Liz rule: **a river is a through-going band**, not a rounded floating rectangle.

```css
/* globals.css .projects-marquee::before / ::after */
inset: 0.35rem 0;   /* vertical breath only — left/right MUST be 0 */
border-radius: 0;   /* never a rounded pool panel */
```

- Keep horizontal `mask-image` on `.projects-marquee` so water fades at viewport L/R (enters/leaves).
- Ripples: `repeating-linear-gradient` ~`3.5–4%` fg opacity, ~`16–18px` period (stronger than a 1.6%/26px whisper).
- Drift light (`::after`): white mix ~`8–9%`.
- `prefers-reduced-motion`: `animation: none` on `::before`/`::after` (and strip fancy backgrounds).

Band height may stay `clamp(9.5rem, 19vw, 12rem)` — width is the “river”, not extra height.

## buildInstances + hash01

- Row pool: `projects.filter((_, i) => i % rows === row)`.
- Seed `` `${url}|r${row}|c${copy}|i${i}` `` → `gapAfter`, `phase` (bob only).
- **No `speedMul`.** Uniform speed after Liz stacking feedback.
- First URL occurrence → `primary: true`.

## Dual-row floater runtime

Floater: `{ x, y, baseY, w, h, speed, scale, targetScale, el, inst }`.

- `f.speed = TUNING.speedBase` always.
- Transform only: `translate3d(x,y,0) scale(s)`.
- Optional bob: `y = baseY + sin(clock*0.85 + phase) * bobAmp`.

## layoutInitial / wrapFloaters / tick

Same as prior refine: phaseShift X chain; wrap off-left to maxRight + gap; `dt` capped 0.05; stop when `!inView || !tabVisible || reduceMotion`.

## Popup + pointer model

**Portal** to `document.body` + `position: fixed` (band mask would clip). Include `mounted` in effect deps.

### Desktop (fine pointer)

`(hover: hover) and (pointer: fine)` → `pointerenter`/`pointerleave` show/hide. Stream does **not** pause.

### Touch (coarse) — long-press ≡ hover

```
pointerdown (non-fine, non-mouse)
  → capture pointer; start ~600ms timer; record x/y
pointermove |Δ| > 10px
  → cancel timer (scroll intent)
timer fires
  → hoveredEl = tile; showPopupFor; suppressClick = true
pointerup / cancel
  → clear timer; if long-press was active → hide popup
click (capture)
  → if suppressClick: preventDefault + stopPropagation; reset flag
contextmenu on tile/root
  → preventDefault (kill OS link preview / callout)
```

CSS on tiles: `user-select: none; -webkit-user-select: none; -webkit-touch-callout: none`.

`updatePopupPosition` must **not** require `finePointer` (long-press sets `hoveredEl` on touch). Keyboard `focusin`/`focusout` unchanged.

Quick tap (<600ms, no timer fire) → normal `<a>` navigation.

## Images

- Tile: lazy + async; onLoad fade; onError → hide img + `data-letter` fallback.
- Popup: placeholder media bg; fade on load; title/desc immediate.
- SoT: `scripts/fetch-project-previews.cjs` `FALLBACKS`/`CURATED` — prefer existing svg/32px; regenerate JSON.

## Skill icon asset

House path: `public/assets/icons/skills/<slug>.svg`  
Mirror: agent-skills repo `assets/skills/<slug>.svg` (byte-identical).  
Style: 32×32, circle `#E8E4DD` + stroke `#1C1915` 1.6, brand `#B14E22` motif, `role="img"` + `aria-label`. Motif for this skill = **full-bleed river + ripples** (not dual pills).

## a11y

| Gate | Behavior |
|---|---|
| `prefers-reduced-motion` | Stop rAF; static grid; hide duplicates; hide popup; kill water anim |
| Duplicates | `aria-hidden` + `tabIndex={-1}` |
| Primary | Focusable `<a>`; focus opens popup |
| Touch long-press | Pointer-only; not a keyboard substitute |
| External | `_blank` + `noopener` |
