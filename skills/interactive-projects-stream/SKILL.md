---
name: interactive-projects-stream
description: 交互式项目流/logo stream/双行跑马灯/OG hover 弹窗/rAF 阻尼。Hand-roll dual-row project logo streams with hash jitter, portaled OG popups, and exp damping — not CSS marquees. Use when building interactive project streams that need per-tile speed variance, dual uneven rows, hover-following OG popups, or real clickable tiles.
metadata:
  hermes:
    category: creative
---

# Interactive Projects Stream

Cookbook for a full-bleed **interactive projects river**: dual-row floaters, deterministic hash jitter, portaled OG popup, rAF + `1-exp(-λ·dt)` damping. Zero new deps.

**Reference files:** `ProjectsMarquee.tsx` (component), `globals.css` (`.projects-marquee*`), `HomeContent.tsx` (`#projects` full-bleed layout).  
**Motion craft:** cite `webgl-threejs-background-animation` skill for exp damp + IO/visibility lifecycle — don't copy prose.

## When to use vs not

| Need | Choice |
|---|---|
| Static logo strip / pause-on-hover only | `react-fast-marquee` / CSS `@keyframes` |
| Embla carousel + auto-scroll | embla plugins (wrong paradigm for a river) |
| Magnetic springs / timeline fight | framer-motion / gsap — heavy; site had zero anim libs |
| Per-tile speed jitter, dual uneven rows, OG popup following moving tiles, real `<a>` clickable | **Hand-rolled rAF** (this skill) |

**Rule:** `react-fast-marquee` (~500k weekly) is the logo-strip default but cannot do per-tile speed variance or a viewport-fixed OG card without fighting CSS keyframes. FM/GSAP excel at magnetic UI but are oversized for one strip. Interactive stream → one client component + centralized `TUNING`.

## Quick start

1. Decide with the table above. Pure logo bar → stop; use a wheel.
2. Full-bleed layout: `#projects` is `w-full`; heading/skills sit in `max-w-* mx-auto px-6` wrappers; marquee sits between them with no horizontal pad (`HomeContent.tsx` ~160–175).
3. Client component: `buildInstances` → absolute tiles → `layoutInitial` → rAF `tick` → `wrapFloaters`.
4. Portal OG popup to `document.body` (`position: fixed`); gate main effect on `mounted`.
5. Lifecycle: `IntersectionObserver` + `visibilitychange` + `ResizeObserver` + `prefers-reduced-motion`.
6. Damping: `damp = c + (t-c)*(1-Math.exp(-λ*dt))`; cap `dt ≤ 0.05` — see webgl skill.

## Architecture spine

1. **buildInstances** — split projects across `rows`; `copies` per row; `hash01(\`${url}|r${row}|c${copy}|i${i}\`)` → `speedMul`, `gapAfter`, `phase`; first occurrence of each URL → `primary`.
2. **Dual-row floaters** — each tile absolute; `speed = speedBase * rowSpeedScale[row] * speedMul`.
3. **layoutInitial** — row Y from band geometry + Y jitter `(hash01(key+"|y")-0.5)*12`; X chain with `phaseShift = -hash01(\`row-start-${row}\`)*bandW*0.85`.
4. **tick** — sin wobble on speed; exp-damp hover scale; `wrapFloaters` recycles off-left tiles to row maxRight + gap.
5. **Popup** — imperative DOM fill (no hover setState); follow tile every frame; above/below/clamp.
6. **a11y** — reduced-motion → static grid (primary only); duplicates `aria-hidden` + `tabIndex=-1`; keyboard focus opens popup; external `_blank`+`noopener`.

Details: [references/architecture.md](references/architecture.md) · TUNING/pitfalls/验收: [references/tuning-pitfalls.md](references/tuning-pitfalls.md)

## Workflow checklist

- [ ] Decision table answered (wheel vs hand-roll)
- [ ] Full-bleed band; content column re-wrapped around heading only
- [ ] TUNING block centralized; damp uses exp, dt capped
- [ ] Popup portaled to body; `mounted` in effect deps
- [ ] IO / visibility / resize / reduced-motion wired
- [ ] Probe: dual rows, row speed diff, in-row variance, popup in viewport, reduced-motion static, no console errors
