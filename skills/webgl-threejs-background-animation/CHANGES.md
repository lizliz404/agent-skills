# CHANGES — webgl-threejs-background-animation

## 2026-08 upgrade

- **Scope expansion**: landing backgrounds → Three.js WebGL animation craft (decorative backgrounds **and** in-game motion)
- New sections: §7 Easing & Interpolation (frame-rate-independent damping `1 - exp(-λ·dt)`), §8 In-Game Motion Craft (game loop, juice / game feel, ViewRig camera, lightweight particles, procedural worlds), §9 Visual Levers (cost-vs-perceived-gain table), §10 Performance Budgets (draw calls, pixelRatio ladders, memory), §11 prefers-reduced-motion & accessibility
- Added "Research Top 20 → Skill Mapping" absorption list
- Reference implementation now bundled: `examples/HeroCanvas.tsx` (the lizliz.xyz "Paper Ink Garden" full-page WebGL background, 862 lines)
- Pack contents: SKILL.md + references/site-adaptation-recipe.md + examples/HeroCanvas.tsx

## History

- `lightweight-three-hero` → `threejs-landing-background` → `webgl-threejs-background-animation` (renames reflect scope growth; the spine — batched geometry → config-driven materials → dual-material dissolve → lifecycle gate — is unchanged)
