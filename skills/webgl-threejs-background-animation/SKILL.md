---
name: webgl-threejs-background-animation
description: 用 Three.js 做融入页面背景的 WebGL 3D 动画与游戏内动画工艺——批处理 LineSegments/Points、config 驱动材质、双材质溶解、轨道相机视差、缓动与 game feel、视觉杠杆、性能预算、零 GPU 离屏休眠。触发词：做个 3D 背景、landing page 动效、WebGL hero、网页 3D 动画、Three.js 背景、游戏动画、粒子反馈、相机平滑、game feel、WebGL background animation、3D hero section、背景动画、融入背景的动画。Use when building decorative animated 3D backgrounds or in-game WebGL motion — batched LineSegments/Points, TUNING + CATEGORIES, dual-material dissolve, orbital/FPV camera, frame-rate-independent damping, juice/secondary motion, fog/halo levers, full lifecycle hygiene.
metadata:
  hermes:
    category: creative
---

# WebGL Three.js Background Animation & Motion Craft

> **改名历史：`lightweight-three-hero` → `threejs-landing-background` → `webgl-threejs-background-animation`。本质：Three.js + 融入页面（或游戏世界）的动画，不是画框里的展品。**
>
> **2026-08 升级：** 从「landing 背景专用」扩展为「Three.js WebGL 动画工艺」——覆盖游戏内动画、视觉杠杆、性能预算、缓动插值。目标：**低成本换高感知**，不是堆 GPU。

Cookbook for animated WebGL that doesn't punish the GPU. Core pattern: batched geometry → config-driven materials → dual-material crossfade / juice feedback → interaction-driven progress → lifecycle gate. Same spine for decorative backgrounds **and** lightweight in-game worlds.

## Design Preferences（美学准则，不可违反）

**动画不是画框里的画，而是融入页面/世界的背景。** 具体：

1. **不要矩形画框**：不用 `border-radius` + `overflow: clip` + 固定宽高比把动画框成"挂在墙上的展品"。
2. **要边缘渐隐融入**：radial-gradient mask、vignette、或 scene fog，让它"长"在页面上。
3. **背景层级**：WebGL canvas 默认 `position: fixed; inset: 0; z-index: -1`（游戏全屏例外：canvas 即视口）。
4. **内容可读性**：文字区要有 backdrop（blur / 半透明），但不要完全遮住动画。
5. **尺寸**：默认全视口；装饰件可跟容器，仍要边缘淡出。

**反模式（禁止）：**
```css
/* ❌ 画框感 */
.animation-frame {
  width: clamp(260px, 42vw, 360px);
  aspect-ratio: 1 / 1;
  border-radius: 42% 58% 53% 47% / 48% 44% 56% 52%;
  overflow: clip;
}
```

**正模式（推荐）：**
```css
/* ✅ 融入背景 */
.animation-background {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 85%);
}
```

---

**Trigger phrases (中英文都能触发):**
- "做个 3D 背景" / "加个 WebGL 动效" / "landing page 3D 动画"
- "Three.js background" / "WebGL hero animation" / "3D hero section"
- "游戏动画优化" / "game feel" / "粒子反馈" / "相机平滑"
- "hero 3D" / "landing 3D" / "网页 3D 背景"

## Core Thesis

> A decorative (or ambient game) component that carries full-application-level runtime burden has failed its job. The highest virtue is not "impressive" — it is **light, quiet, high-perceived quality**. Fix the burden first; add narrative/juice only after the base is cheap. Prefer **visual levers** (fog, halo, easing, secondary motion) over post-processing and custom pipelines.

## Decision Framework: When NOT to add Three.js (conversion landings)

This skill is strong for **controllable decorative backgrounds** and **lightweight game worlds**. It is **not** the default upgrade for every landing.

**Default NO** when most of these are true (Acriva / 融销通 2026-07-21):

1. Audience trusts **status, money amounts, seats, proof** — not SF 3D atmosphere.
2. Hero **already** has product proof UI (device mocks, desk windows, interactive demos).
3. Brand DESIGN forbids cold SaaS / neon / glass; paper-wood desk language wins.
4. Job is P0 SEO/conversion; WebGL adds bundle + GPU lifecycle without changing the buy path.

Prefer: CSS paper texture / light noise / vignette (effort S) over Three.js.

**Default YES / MAYBE** only when: user will iterate on the animation, hero lacks product proof, brand allows technical craft as signal, and SEO/meta/CTA are already solid — **or** the product *is* a WebGL game/world.

When Liz asks “能不能用 Three.js skill？”, answer with this decision table first — do not auto-implement.

## Decision Framework: When to Replace a Working Canvas 2D Animation

**The deciding question is controllability over time.** Canvas 2D pixel animations hit a controllability ceiling fast:

| Canvas 2D pain signal | Why it matters |
|---|---|
| Hardcoded x/y coordinates per frame | Any composition change = hand-tuning dozens of values |
| Single-file IIFE with coupled state | 750+ lines means every edit risks breaking unrelated parts |
| No config layer | Colors, speed, composition are scattered magic numbers |
| Pixel-grid constraint (e.g. 48×48) | Complex compositions literally cannot fit |
| No lifecycle management | Keeps rendering off-screen; battery drain on mobile |

**Three.js wins when the user will iterate.** Ask: "Will you modify composition/colors/behavior in 3–6 months?" If yes → Three.js. If truly static one-shot → Canvas 2D may still be fine.

**Brand continuity is not a blocker.** Rebuild brand characters in Three.js geometry. **Migration:** move old Canvas 2D to a secondary slot; don't delete.

---

## The System（背景动画核心架构）

```
Config Layer    TUNING (magic numbers) + CATEGORIES (visual weights)
       ↓
Geometry Layer  Float32 arrays pushed by domain-specific helpers
       ↓
Material Layer  One dashed + one solid material per category (dual for dissolve)
       ↓
Scene Layer     GridHelper ×2 + zone fills + fog + camera
       ↓
Animation Layer Helix camera + parallax + progress crossfade (+ juice if game)
       ↓
Lifecycle Layer IntersectionObserver + visibilitychange + ResizeObserver + full dispose
```

### 1. Config: Single Source of Truth

Every tunable number lives in one `TUNING` object. Every visual category lives in one `CATEGORIES` array. Materials and per-frame updates iterate the same array.

```ts
const TUNING = { camera: { radius: 13, baseY: 6.5 }, spin: { base: 0.06 }, /* ... */ } as const

const CATEGORIES: CategorySpec[] = [
  { key: 'primary',   color: 0x..., solidColor: 0x..., weight: 0.72, dash: {...}, phase: 0 },
  { key: 'secondary', color: 0x..., solidColor: 0x..., weight: 0.50, dash: {...}, phase: 0.6 },
  { key: 'detail',    color: 0x..., solidColor: 0x..., weight: 0.34, dash: {...}, phase: 1.3 },
  { key: 'accent',    color: 0x..., solidColor: 0x..., weight: 0.66, dash: {...}, phase: 2.1 },
]
```

Adding a 5th visual weight = one entry + one segment array. Nothing else changes.

### 2. Geometry: Batched Float Arrays

Push all segments into typed arrays → **one** `LineSegments` per category (not one `Line` per primitive).

```ts
function pushSeg(seg: number[], ax: number, az: number, bx: number, bz: number, y = FLOOR) {
  seg.push(ax, y, az, bx, y, bz)  // 6 floats per segment pair
}

function makeLineSegments(seg: number[], material: LineDashedMaterial | LineBasicMaterial, renderOrder = 0) {
  const geo = new BufferGeometry()
  geo.setAttribute('position', new Float32BufferAttribute(seg, 3))
  const line = new LineSegments(geo, material)
  if (material instanceof LineDashedMaterial) line.computeLineDistances()
  line.renderOrder = renderOrder
  return line
}
```

**Draw-call choice boundary (2026):**

| Primitive need | Prefer | Avoid when |
|---|---|---|
| Many static/semi-static lines | 1× `LineSegments` / category | Per-segment `Line` |
| Many particles / points | 1× `Points` + shared attrs | N× `Mesh` sprites |
| Many identical meshes, per-instance transform | `InstancedMesh` (count ≥ ~100–200 meaningful) | InstancedMesh for <50 trivial boxes |
| Static multi-color mesh pile | `mergeGeometries` + vertexColors | Merge entire terrain (kills frustum culling) |

Desktop target: **<100** draw calls. Mobile: **<50**. Monitor `renderer.info.render.calls`.

### 3. Materials: Dual for Dissolve

| Material | Role | progress=0 | progress=1 |
|---|---|---|---|
| `LineDashedMaterial` | Sketch | Full opacity | Faded |
| `LineBasicMaterial` | Solid | Zero opacity | Full opacity |

```ts
cat.dashMat.opacity  = pulse * (1 - progressEffect * 0.7)
cat.solidMat.opacity = pulse * progressEffect * 0.85
cat.dashMat.gapSize  = cat.dash.gapSize * (1 - progressEffect * 0.6)
```

Progress: hover/move + click/tap + idle ambient auto-ramp. Smooth with `1 - exp(-smoothK * dt)`. Cap at `PROGRESS_MAX` (e.g. 0.7).

### 4. Camera: Helix + Parallax + Portrait

```ts
camera.x = radius * cos(angle) + easedMouseX * parallaxAmount
camera.z = radius * sin(angle)
camera.y = (baseY - cameraDrop * progress) + amp * sin(angle * 0.5) + easedMouseY * parallaxAmount
```

- Azimuth: `(spinBase + spinWobble * sin(angle * 0.7)) * dt` — frame-rate independent
- Parallax: `1 - exp(-parallaxK * dt)` — identical at 60/120/144 Hz
- Portrait: when `aspect < 1.3`, boost FOV and orbital radius
- Follow damp λ typically **5–12**; never use raw lerp factor > 0.15 on variable dt

### 5. Lifecycle: Zero GPU When Invisible

| Gate | Mechanism | Effect |
|---|---|---|
| Off-screen | `IntersectionObserver` (threshold 0) | Cancel rAF → zero GPU |
| Hidden tab | `visibilitychange` | Pause; resume only if in view; **reset clock** (no physics spike) |
| Resize | `ResizeObserver` + `window.resize` | Recalc aspect |
| Reduced motion | `prefers-reduced-motion: reduce` | Static frame / no shake / no decorative drift |
| Context loss | `webglcontextlost` → dispose / reload prompt | Fall back to CSS |
| Unmount | Full `dispose()` | traverse geo/mats/textures → `forceContextLoss()` |

**Also:** decorative backgrounds: `powerPreference: 'low-power'`, `depth: false`, `stencil: false`. Games may use `high-performance` on desktop.

### 6. CSS Fallback

Canvas alpha-composited over CSS gradient + grid. If WebGL unavailable, component returns `null` and CSS shows through.

---

## 7. 缓动与插值（Easing & Interpolation）

### 7.1 帧率无关平滑（强制）

```ts
// ❌ Frame-coupled — 2× faster on 120Hz
eased += (target - eased) * (dt * K)

// ✅ Exponential decay — identical feel at any Hz
eased += (target - eased) * (1 - Math.exp(-λ * dt))
```

| Use case | λ 建议 | Notes |
|---|---|---|
| UI / opacity crossfade | 2–4 | Soft settle |
| Camera follow / parallax | 5–12 | Sweet spot; >15 feels snappy/harsh |
| FOV kick return | 8–12 | Punch then soft |
| Physics-facing (collision lane) | — | **Don't damp** position that collision depends on |

Shared helper (put in TUNING consumers, not magic):

```ts
export const damp = (current: number, target: number, λ: number, dt: number) =>
  current + (target - current) * (1 - Math.exp(-λ * dt))
```

### 7.2 常用缓动曲线

| Curve | When | Example |
|---|---|---|
| **ease-out** (default UI) | User-initiated feedback | Score pulse, button settle, spawn fade-in — 200–300ms |
| **ease-in-out** | Camera / mode blends | ViewRig switch; use `smoothstep` or smootherstep |
| **ease-in** | Rare — exits that accelerate | Despawn whoosh |
| **linear** | Constant-speed world scroll | Pipe advance, ground UV (physics authority) |
| **spring / overshoot** | Juice moments | Score pop, flap squash — keep amplitude tiny |

```ts
const smoothstep = (x: number) => { const t = Math.min(1, Math.max(0, x)); return t * t * (3 - 2 * t) }
const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3)
```

### 7.3 规则

1. Physics timesteps always `* dt` (never per-frame constants).
2. Visual smoothing always `1 - exp(-λ·dt)` or eased progress 0→1 over seconds.
3. Interruptible tweens: kill previous before starting new (`killTweensOf` if GSAP; else overwrite local progress).
4. Never accumulate uncapped FOV/shake — decay toward 0 with exp.

---

## 8. 游戏内动画（In-Game Motion Craft）

When the product *is* a game (or has a playable WebGL scene), keep the same config + lifecycle spine, then layer:

### 8.1 游戏循环与帧率无关运动

```
rAF → dt = min(clock.getDelta(), 0.05) → physics(dt) → visuals(dt) → render
```

- Cap dt (e.g. 0.05) so tab-return doesn't teleport.
- On `visibilitychange` hidden→visible: reset clock / ignore one huge dt.
- Separate **authority** (collision, score) from **presentation** (squash, halo, camera tilt).

### 8.2 物理手感平滑（damping / 弹簧）

| Layer | Do | Don't |
|---|---|---|
| Core hop / gravity / speed | Keep instant / authority numbers | Soften flap vy "for feel" |
| Camera pitch/roll from vy | damp λ≈8–12 | Snap rotation to vy |
| Mesh squash / wing flap | short envelope 80–200ms | Change hitbox with squash |
| Death trauma shake | trauma 0→1 then decay | Continuous Perlin camera noise in FPV |

### 8.3 程序化世界（天空 / 云 / 山 / 草 / 路径）

| Element | Preferred technique | Cost note |
|---|---|---|
| Sky | BackSide sphere + **one-time** CanvasTexture gradient OR gradient shader | Never per-frame canvas redraw |
| Sun | Soft radial CanvasTexture billboard, `fog: false` | Tiny |
| Hills | Seamless sine-cycle CanvasTexture + UV scroll ×0.2–0.5 | Parallax depth free |
| Grass | Tiling CanvasTexture; side shade as **separate** world-space overlay | Don't bake edge into repeating tile |
| Path | Non-tiling-X strip texture | Scroll V with ground |
| Fog | `Fog` / `FogExp2`; **`scene.background` === fog.color** | Near-zero GPU |
| Clouds | Few flattened sphere groups, layered speed/opacity | Prefer opacity layers over volumetric |
| Drift / dust | Shared geo+mat tiny meshes **or** one `Points` | Keep clear of play corridor |

Textures: generate once; dynamic HUD only → reuse canvas + `needsUpdate = true`.

### 8.4 粒子系统（轻量）

| Scale | Approach |
|---|---|
| ≤ ~50 feedback bits (death burst) | Mesh pool + gravity + ease-out scale; recycle |
| ~100–5k ambient | Single `Points` + `PointsMaterial`; prefer shader `uTime` if CPU update hurts |
| >5k | GPU sim / don't for decorative games |

Rules: preallocate; `depthWrite: false`; AdditiveBlending only when it helps; **never** `new Float32Array` every frame; gate with reduced-motion.

### 8.5 相机 Rig 与视角混合

```
ViewSample { y, vy, dt, t, shake, score } → ViewRig.update(cam, sample)
```

- Game never sets camera directly; rig owns pose.
- Mode blend: capture from/to pos+quat, `smoothstep`/`slerp` over `blendSec`.
- FPV: position exact (collision lane); only damp **rotation**.
- Chase/side: damp follow; look-at target ahead.
- Motion sickness: `prefers-reduced-motion` → force plain FPV; no shake; no shifter.
- Dynamic FOV: kick on flap then exp decay; portrait FOV boost when `aspect < 1.3`.

### 8.6 Game Feel 原则（Juice）

Priority = perceived impact ÷ code cost (GDC "Juice it or lose it"):

| Principle | Cheap implementation | Budget |
|---|---|---|
| **Anticipation** | Warn flash / tick 0.3s before view switch | DOM + SFX |
| **Follow-through** | FOV kick + wing settle after flap | TUNING numbers |
| **Secondary motion** | Idle bob, cloud Y bob, halo breathe, wing flap | sin / damp |
| **Squash & stretch** | Scale Y 0.88→1.08 on flap/land envelope | 2–3 frames…~150ms |
| **Timing / rhythm** | Ease-out UI 200–300ms; hit-stop 30–50ms optional | Don't stall physics long |
| **Particles** | 10–24 pooled cubes on death; optional score spark | Bound pool |
| **Screen shake** | Trauma decay, amp in TUNING, skip if reduced-motion | radians ≤ ~0.08 |

**Hit recipe (portable):** 2–3 frame squash + optional 50ms hit-stop + ~10 particles → huge feel, <30 lines.

---

## 9. 视觉杠杆（Visual Levers — 低成本高感知）

按「感知收益 ÷ 实现成本」排序。优先做表上半；后处理 / 自定义管线默认不做。

| # | Lever | Cost | Perceived gain | How |
|---|---|---|---|---|
| 1 | **Fog** + matching background | 1–3 lines | Depth, melt edges | `Fog(color, near, far)`; color === `scene.background` |
| 2 | **Edge fade / vignette** | CSS or soft fog | Non-frame blend | radial mask / fog far |
| 3 | **Exponential damping** | 1 helper | Pro motion | replace linear lerp |
| 4 | **Idle / secondary motion** | sin 0.2–0.5 Hz, 2–3% | Alive world | bob, breathe, drift Y |
| 5 | **Colour hierarchy** | palette stops | Readable layers | near saturated, far desat + fog |
| 6 | **Halo / rim (not bloom)** | BasicMaterial ring / emissive pulse | Affordance + juice | collision ring; approach emissive |
| 7 | **Parallax layers** | UV ×0.2–0.5 | Depth free | hills/clouds/ground speeds |
| 8 | **Procedural detail once** | CanvasTexture load-time | Craft without assets | grass/hills/sky |
| 9 | **Tone / exposure** | ACES 0.8–1.2 if used | Mood | games only; backgrounds often skip |
| 10 | **Full-screen bloom / DOF** | EffectComposer | Often muddy | **Trap** — avoid for line/simple scenes |

Halo: prefer mesh ring / `emissiveIntensity` pulse / view·normal rim — **not** default EffectComposer bloom.

---

## 10. 性能预算与测量（Budgets & Measurement）

### 10.1 移动端预算

| Budget | Desktop | Mobile |
|---|---|---|
| Target FPS | 60 | 30–60 (thermal reality) |
| Draw calls | <100 | <50 |
| pixelRatio cap | `min(dpr, 2)` lines: **1.25–1.5** | `min(dpr, 1)` or 1.5 max |
| Shadows | optional | **off** |
| Textures | 1024–2048 | 512–1024 |
| powerPreference | `high-performance` (game) | `low-power` (bg) / game case-by-case |
| antialias | ok if budget | off on low tier |

3× DPR ≈ 9× pixels vs 1× — always cap.

### 10.2 pixelRatio 策略

```ts
renderer.setPixelRatio(Math.min(devicePixelRatio, TUNING.maxPixelRatio))
```

- Line-only decorative: cap **1.5** or **1.25** (lines are 1px GL_LINES).
- Adaptive ladder (EMA dt): e.g. 2 → 1.5 → 1 with hysteresis (drop <45fps, recover >55fps) + cooldown ≥6s.
- Only lower DPR when fill-rate bound; verify FPS rises after each step.

### 10.3 Draw-call 边界

见 §2 表。Shared geometry/material singleton + `Map` for color variants. Prefill `InstancedMesh` capacity; runtime only shrink visible count.

### 10.4 FPS 监控与自适应降级

开发期：`renderer.info.render.calls` / `memory.geometries` / `memory.textures`.

运行期：EMA of `dt` → quality ladder (pixelRatio → disable drift → reduce cloud count). Optional boot micro-benchmark for initial tier. Dirty-flag render for **static** backgrounds (games loops still render every frame while playing).

### 10.5 内存

Unload: `scene.traverse` → dispose geometry, materials, **all map textures**; `renderer.dispose()`; `forceContextLoss()` when tearing down; Chrome ~8 contexts/page.

---

## 11. prefers-reduced-motion 与无障碍

| Preference | Required behavior |
|---|---|
| `prefers-reduced-motion: reduce` | No camera shake; no decorative scroll/drift; no shifter cams; static or minimal idle; UI flashes softened |
| Game logic | Still playable — physics/input remain |
| Background-only | Render one static frame at `idleTarget` |
| Announce | Don't rely on motion alone for scoring cues — keep SFX / HUD text |

```ts
const reduceMotion =
  typeof matchMedia === 'function' &&
  matchMedia('(prefers-reduced-motion: reduce)').matches
```

---

## Pitfalls

Collected from real audits + 2026 research. Real bugs, not hypotheticals.

1. **CDN dynamic import of Three.js** — kills tree-shaking/types/CSP. Always `import { … } from 'three'`.
2. **Frame-rate coupled lerp** — use `1 - exp(-K * dt)`.
3. **rAF when off-screen / tab hidden** — IntersectionObserver + visibilitychange; games also reset clock.
4. **Incomplete dispose** — traverse geo/mats/**textures**; `forceContextLoss()`.
5. **`useEffect([], …)` without StrictMode guard** — `initedRef` in React.
6. **`setPixelRatio(min(dpr,2))` on line-only scenes** — cap 1.25–1.5.
7. **`alpha: true` when bg controllable** — prefer `alpha: false` + clear color.
8. **No `webglcontextlost` handler** — mobile freezes; provide restore/reload UX (transient overlay, not permanent brick).
9. **Missing `renderOrder` for layered lines** — without depth test.
10. **Assuming "keep Canvas 2D" is safe** — controllability over time wins.
11. **Per-frame `new Texture()` / `new Float32Array` for canvas/particles** — reuse + `needsUpdate`.
12. **`scene.background` ≠ fog color** — harsh silhouette seams.
13. **Baking corridor edge into repeating grass tile** — zebra stripes × N.
14. **Damping collision-critical positions** — FPV eye must match hit lane.
15. **Permanent context-lost overlay** — remove on `webglcontextrestored`.
16. **InstancedMesh without `computeBoundingSphere` after matrix updates** — culling/raycast break.
17. **Merging entire terrain into one mesh** — disables useful frustum culling.
18. **Bloom by default** — 3–5ms+; use selective halo instead.
19. **Pause by setting ω=0 but keeping rAF** — still burns GPU; `cancelAnimationFrame`.
20. **Softening core flap/gravity for "feel"** — break determinism; juice the *presentation* layer.

### Communication pitfall (agent-side)

When referencing the skill's reference implementation path, **explicitly say "the skill documents this at `<path>`"** — cite the skill as authority.

### Over-optimization traps（2026 / three@0.185+ 校准）

| Trap | Why net negative |
|---|---|
| **Line2 / LineMaterial** for decorative bg | +15KB; only for UI-critical viz |
| **Custom shader replacing LineDashedMaterial** | ALU win tiny; maintainability loss |
| **InstancedMesh for < ~100 simple objects** | Batched LineSegments/Points simpler |
| **EffectComposer (bloom/FXAA/DOF)** | Line/simple scenes don't benefit; eats ms |
| **R3F for single decorative component** | Reconciler overhead; OK for 3+ 3D islands |
| **WebGPU backend for decorative/simple games** | Evolving; switching cost ≫ benefit in 2026H1 |
| **OffscreenCanvas + Worker for mouse-parallax bg** | Comms overhead > savings |
| **Volumetric clouds / raymarch for Flappy-scale** | Mesh pancakes + fog win |
| **BatchedMesh everywhere "because new"** | Use when transparency sort actually needed |
| **detect-gpu + 5 quality tiers before shipping juice** | Ship fog/easing first; tier later |

---

## Adaptation Guide

1. Design 3–5 visual categories (colors, weights, dash).
2. Domain geometry helpers: `push*(seg: number[], …)`.
3. Organize into zones.
4. `FOG_COLOR` = page mid-tone; match `scene.background`.
5. Tune camera radius/baseY/amp/spin.
6. Set `idleTarget` so mobile sees dissolve.
7. For games: add ViewRig seam, juice envelopes in TUNING, never scatter magic numbers.

### Replacing Canvas 2D

Preserve old animation in a secondary location; primary slot gets config-driven Three.js.

### Site adaptation

See `references/site-adaptation-recipe.md`: metaphor → palette from CSS → dark-mode category builder → geometry helpers → camera for compact scenes.

---

## Reference Implementation

Decorative background: bundled `examples/HeroCanvas.tsx` — the lizliz.xyz "Paper Ink Garden" full-page background (862 lines, three@0.185)

Engineering audit: keep your own review notes in your project's `docs/` — the audit that shaped §9 Visual Levers & §10 Budgets is summarized inside those sections

Game-shaped sibling: an FPV flappy-style game — TUNING + ViewRig + scenery CanvasTextures + reduced-motion gates (see §8 In-Game Motion Craft)

---

## Build Checklist

### Background / decorative
- [ ] 3–5 visual categories with clear weight hierarchy
- [ ] One `TUNING` object — no stray magic numbers
- [ ] Domain geometry helpers (append to `number[]`)
- [ ] One segment array per category + dashed/solid pair
- [ ] CSS fallback; null on WebGL failure
- [ ] IntersectionObserver + visibilitychange gate
- [ ] Full dispose + `forceContextLoss()`
- [ ] StrictMode `initedRef` (React)
- [ ] Reduced-motion static frame
- [ ] Portrait FOV/radius boost
- [ ] Idle progress ramp
- [ ] `powerPreference` appropriate; stencil off if unused
- [ ] Fog color === background
- [ ] All smoothers use `1 - exp(-λ·dt)`
- [ ] No bloom / no CDN whole three / no R3F-for-one-scene

### Game / interactive world (additional)
- [ ] dt-clamped game loop; clock reset on tab resume
- [ ] Physics authority vs presentation split
- [ ] ViewRig owns camera; collision lane undamped in FPV
- [ ] Juice: squash / halo / burst / FOV kick in TUNING
- [ ] Particle/mesh pools bounded; reduced-motion skips
- [ ] Procedural textures generated once
- [ ] Parallax layer speeds; corridor kept readable
- [ ] pixelRatio cap + optional adaptive ladder
- [ ] `renderer.info` sanity in dev
- [ ] Skin/theme changes don't allocate new geos

---

## Extensions & Future Directions

Priority = perceptual impact ÷ implementation cost.

### High priority

| Extension | Cost | Why |
|---|---|---|
| **Depth fog** | 3 lines | Distant fade; edge melt |
| **Grid / world drift** | ~4 lines | Breathing illusion |
| **Dark mode palette** | ~15 lines | `prefers-color-scheme` / theme attr |
| **Exp damp everywhere** | 1 helper | Kill frame-coupled feel |
| **Secondary idle motion** | ~10 lines | Alive without assets |
| **Approach / score halo** | ~15 lines | Fairness + juice |

### Medium priority

| Extension | Cost | Why |
|---|---|---|
| Cursor-as-light opacity boost | ~30 lines | Flashlight over blueprint |
| Adaptive quality EMA ladder | ~20 lines | Protect low-end |
| Isometric / Orthographic toggle | ~50 lines | Narrative punch |
| Score particles (Points pool) | ~40 lines | Juice without bloom |
| Skin color crossfade (damp hex) | ~20 lines | Theme polish |

### Low priority / don't do yet

| Extension | Why not now |
|---|---|
| GPU particle FBO sims | Separate architecture |
| Scroll-scrub timeline | Couples lifecycle hard |
| Voronoi / heavy procedural fields | Domain-specific companion |
| WebGPU backend | Revisit when stable for prod decorative |
| Full EffectComposer stack | Cost/clarity fail for this skill's targets |

---

## Research Top 20 → Skill Mapping（吸收清单）

| # | Practice | Skill home |
|---|---|---|
| 1 | Fog + matching background | §5 Scene, §9 Lever #1, Checklist |
| 2 | Squash + hit-stop + particles | §8.6 Game Feel |
| 3 | pixelRatio cap | §10.2 |
| 4 | InstancedMesh / merge boundary | §2 table |
| 5 | `lerp` via `1-exp(-λ·dt)` | §7.1 |
| 6 | prefers-reduced-motion | §11, Lifecycle |
| 7 | Dirty-flag static render | §10.4 |
| 8 | Points + uTime particles | §8.4 |
| 9 | UI ease-out 200–300ms | §7.2 |
| 10 | BackSide sky / one-shot gradient | §8.3 |
| 11 | Camera damp λ 5–12 | §4, §7.1, §8.5 |
| 12 | Mobile: no shadow, half tex, low-power | §10.1 |
| 13 | Halo not bloom | §9, Over-opt traps |
| 14 | traverse dispose | §5, Pitfall 4 |
| 15 | CanvasTexture reuse | §8.3, Pitfall 11 |
| 16 | Monitor draw calls | §10.4 |
| 17 | Interruptible tweens | §7.3 |
| 18 | Parallax UV 0.2–0.5 | §8.3, §9 |
| 19 | Boot quality tier optional | §10.4, Low priority |
| 20 | Shared geo/mat singleton | §2, §10.3 |
