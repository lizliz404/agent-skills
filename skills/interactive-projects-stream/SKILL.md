---
name: interactive-projects-stream
description: 交互式项目流/logo stream/双行跑马灯/OG hover·长按弹窗/rAF 阻尼。Hand-roll dual-row project logo streams with a full-bleed river band, hash gap/phase variety, portaled OG popups (hover + touch long-press), and exp damping — not CSS marquees. Use when building interactive project streams that need dual uneven rows, uniform-speed drift (no same-row stacking), hover/long-press OG popups, or real clickable tiles.
metadata:
  hermes:
    category: creative
---

# Interactive Projects Stream

Cookbook for a full-bleed **interactive projects river**: dual-row floaters on a **through-going water band**, deterministic hash variety (gaps/phase/Y — **not** speed), portaled OG popup (desktop hover ≡ touch long-press), rAF + `1-exp(-λ·dt)` damping. Zero new deps.

**Reference files:** `ProjectsMarquee.tsx` (component), `globals.css` (`.projects-marquee*`), `HomeContent.tsx` (`#projects` full-bleed layout).  
**Motion craft:** cite `webgl-threejs-background-animation` skill for exp damp + IO/visibility lifecycle — don't copy prose.  
**Skill icon:** `/assets/icons/skills/interactive-projects-stream.svg` (site `public/` + agent-skills repo `assets/skills/` — keep both identical).

## When to use vs not

| Need | Choice |
|---|---|
| Static logo strip / pause-on-hover only | `react-fast-marquee` / CSS `@keyframes` |
| Embla carousel + auto-scroll | embla plugins (wrong paradigm for a river) |
| Magnetic springs / timeline fight | framer-motion / gsap — heavy; site had zero anim libs |
| Dual uneven rows, full-bleed river band, OG popup (hover + long-press), real `<a>` clickable | **Hand-rolled rAF** (this skill) |

**Rule:** `react-fast-marquee` is the logo-strip default but cannot host a viewport-fixed OG card without fighting CSS keyframes. Interactive stream → one client component + centralized `TUNING`.

**Speed rule (Liz 2026-08):** all tiles share one `speedBase`. Do **not** add per-tile jitter, per-row scale, or sin speed wobble — same-row speed variance → stacked boxes. Variety = gaps / phaseShift / Y only.

**River form rule (Liz 2026-08):** the water surface is a **full-bleed band** (`inset` left/right `0`, `border-radius: 0`), not a rounded floating panel. Horizontal mask fades the river in/out at viewport edges. Ripples/light should be clearly readable (see TUNING/CSS values).

**Touch rule:** long-press (~600ms) ≡ hover for the OG popup. Never rely on browser link preview / system callout — own the gesture (`contextmenu` preventDefault + `-webkit-touch-callout: none` + click suppress after long-press).

## Quick start

1. Decide with the table above. Pure logo bar → stop; use a wheel.
2. Full-bleed layout: `#projects` is `w-full`; heading/skills in `max-w-* mx-auto px-6`; marquee has no horizontal pad.
3. Client component: `buildInstances` → absolute tiles → `layoutInitial` → rAF `tick` → `wrapFloaters`.
4. Portal OG popup to `document.body`; gate main effect on `mounted`.
5. Lifecycle: IO + visibility + resize + reduced-motion.
6. Desktop: fine-pointer hover. Touch: long-press timer + move-cancel + click suppress.
7. CSS river: `::before`/`::after` span left→right, no radius; ripples stronger than a faint strip.
8. Icons: light SoT sources; tile onError letter fallback; popup placeholder + fade.

## Architecture spine

1. **buildInstances** — rows × copies; hash → `gapAfter`, `phase`; first URL → `primary`.
2. **Floaters** — absolute tiles; **every** `speed = speedBase`.
3. **layoutInitial** — Y from band + hash jitter; X chain + row `phaseShift`.
4. **tick** — uniform Δx; optional Y bob; exp-damp hover/long-press scale; wrap.
5. **Popup** — imperative fill; hover (fine) + long-press (touch); follow each frame.
6. **River CSS** — full-bleed band + ripple + drift light; mask edge fade; reduced-motion kills anim.
7. **a11y** — reduced-motion static grid; keyboard focus still opens popup; long-press is not a keyboard path.

Details: [references/architecture.md](references/architecture.md) · TUNING/pitfalls/验收: [references/tuning-pitfalls.md](references/tuning-pitfalls.md)

## Workflow checklist

- [ ] Decision table answered (wheel vs hand-roll)
- [ ] Full-bleed band; content column re-wrapped around heading only
- [ ] River `::before`/`::after`: L/R inset 0, `border-radius: 0`, ripples readable
- [ ] TUNING: no speedJitter / speedWobble / rowSpeedScale
- [ ] Popup portaled; `mounted` in effect deps; OG placeholder + fade
- [ ] Touch long-press ≡ hover; contextmenu blocked; quick tap still navigates
- [ ] Skill icon at `/assets/icons/skills/<slug>.svg` (site + agent-skills synced)
- [ ] Probe: dual rows, no same-row stack, band form, long-press popup, hover unchanged, reduced-motion static
