# Architecture — Interactive Projects Stream

Authority: `ProjectsMarquee.tsx` (file:line cites below). CSS: `globals.css` `.projects-marquee*` (~368–620). Layout: `HomeContent.tsx` `#projects` full-bleed (~160–175).

Motion helpers (`damp`, dt cap, IO/visibility) — cite `webgl-threejs-background-animation` skill; don't duplicate.

## buildInstances + hash01

```ts
// ProjectsMarquee.tsx:42–50, 87–120
function hash01(seed: string) {
  let h = 2166136261;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 4294967295;
}
```

- Row pool: `projects.filter((_, i) => i % rows === row)` (fallback to full list if empty).
- For each `copy × pool item`: seed `` `${url}|r${row}|c${copy}|i${i}` ``.
- `gapAfter = gapMin + u * (gapMax - gapMin)` — primary in-row spacing variety.
- `phase = u * Math.PI * 2` — Y bob phase only (not speed).
- First occurrence of each URL → `primary: true` (a11y / reduced-motion visibility)
- **No `speedMul`.** Speed variance removed after Liz feedback (same-row stacking).

## Dual-row floater runtime

Each DOM tile `[data-stream-tile]` maps to a floater `{ x, y, baseY, w, h, speed, scale, targetScale, el, inst }`.

- **Uniform speed:** `f.speed = TUNING.speedBase` in `layoutInitial` (~243).
- Transform only: `translate3d(x,y,0) scale(s)` — compositor-friendly.
- Optional visual bob: `y = baseY + sin(clock*0.85 + phase) * bobAmp` — does not change Δx/Δt.

## layoutInitial

```
bandH / bandW from root
usableH = bandH - 2*bandPadY - rowGap
rowH = usableH / rows
phaseShift = -hash01(`row-start-${row}`) * bandW * 0.85
baseY = pad + row*(rowH+rowGap) + (rowH-h)/2 + hashYJitter(±6)
x chain: x0 = phaseShift; next = prev + w + gapAfter
speed = speedBase  // all tiles
```

Call on mount, ResizeObserver, and leaving reduced-motion. Apply transforms immediately after to avoid flash.

## wrapFloaters

Per row: if `f.x + f.w < -40`, place after the current rightmost sibling: `f.x = maxRight + gapAfter`.

With **uniform speed**, gaps stay constant → tiles never catch each other; wrap stays seamless.

## rAF tick

```ts
// ProjectsMarquee.tsx ~316–340
dt = lastT === 0 ? 0 : Math.min((now - lastT) / 1000, 0.05)
f.x -= f.speed * dt
f.y = f.baseY + sin(clock * 0.85 + phase) * bobAmp
f.scale = damp(f.scale, hover ? hoverScale : 1, scaleK, dt)
wrapFloaters(); applyTransforms(); updatePopupPosition if hovered
```

Gate loop: stop when `!inView || !tabVisible || reduceMotion`. On tab visible again, `lastT = 0` (ignore huge dt).

## Images (tile + popup)

**Tile icons** (`ProjectsMarquee.tsx` ~505–523; CSS ~465–497):
- `loading="lazy"` + `decoding="async"`
- `onLoad` → `.is-loaded` fade-in
- `onError` → hide img, set parent `data-failed="1"` → CSS `::after` shows `data-letter` (title initial). Never show browser broken-image glyph.

**OG popup** (`fillPopup` + load/error listeners; CSS ~550–575):
- Media area always has placeholder background while `data-loaded="0"`
- Title/desc show immediately; large OG fades in on `load`
- `error` → hide media (text still useful)
- Data SoT: `scripts/fetch-project-previews.cjs` `FALLBACKS` / `CURATED` — prefer existing svg/32px icons; regenerate JSON, don't hand-edit.

## Pool surface (optional, light)

`.projects-marquee::before` (~391–409): faint tint + tiny backdrop-blur + inset highlight so tiles read as floating on a pool, not sliding on bare page bg. Soften tile `box-shadow` for a weak reflection cue. Keep cheap — no heavy glass stack.

## Popup architecture (required traps)

**Why portal to `body` + `position: fixed`:** band uses `overflow: hidden` + horizontal `mask-image`. In-band popups clip at the fade edges. Portaled fixed popup floats over page content (`globals.css` popup block; comment at TSX ~158–160).

**mounted must be set first; effect deps must include `mounted`:**

```ts
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);
// portal: {mounted && createPortal(..., document.body)}
useEffect(() => {
  const popup = popupRef.current;
  if (!root || !popup || ...) return; // early exit if popup not in DOM yet
  // ...
}, [instances, projectByUrl, mounted]); // mounted REQUIRED
```

Symptom if omitted: listeners never attach; popup never shows. Cause: first effect run sees `popupRef.current === null`, cleans up, never re-runs.

Other popup rules:
- `pointer-events: none` — never steal clicks from tiles/page
- Imperative fill (`fillPopup`) — avoid React setState on every hover (keeps rAF smooth)
- Position each frame from `getBoundingClientRect()`:
  - `left` centered on tile, clamped to `[8, innerWidth - pw - 8]`
  - prefer **above** if `rect.top - ph - 12 >= 8`
  - else **below** if fits
  - else clamp into viewport
- Fine pointer only: `(hover: hover) and (pointer: fine)`; touch skips popup
- Keyboard: `focusin`/`focusout` on root mirrors hover

## Full-bleed layout

`HomeContent.tsx` (~160–175): `#projects` section is `w-full` (sibling to padded columns, not inside them). Heading wrapper uses `max-w-lg md:max-w-2xl mx-auto px-6`; `<ProjectsMarquee />` has no horizontal pad; skills block re-wraps in the same max-width column.

## a11y

| Gate | Behavior |
|---|---|
| `prefers-reduced-motion` | Stop rAF; clear transforms; CSS grid auto-fill; hide `aria-hidden` duplicates; hide popup |
| Duplicates | `aria-hidden` + `tabIndex={-1}` |
| Primary tiles | Real focusable `<a>`, `aria-label={title}` |
| External links | `target="_blank" rel="noopener noreferrer"`; same-origin (`lizliz.xyz` or `/`) stays inline |
| Region | `role="region"` + section aria-label |

CSS reduced-motion: `.projects-marquee` height auto, mask off; stage → grid; tiles `position: relative; transform: none !important`.
