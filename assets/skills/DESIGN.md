# Skill Icons Design Language

Icons for lizliz.xyz `/skills` (32×32 SVG slots). This document is the icon system’s own DESIGN.md — **not** a reuse of the personal-site visual system.

---

## Forensic: where the old style came from

**Verdict (verified against files, not guessed):** the six icons were a **site-token costume** with different glyphs, not six independent mark systems.

| Evidence | Source |
|---|---|
| Plate fills `#1C1915` / `#141413` / `#141C18` | every `public/assets/icons/skills/*.svg` uses a full-bleed `rect` + `rx="8"` |
| Glyph `#E8E4DD` / `#FAF9F5` | same SVGs |
| Accent `#B14E22` (and warm neighbors) | same SVGs; site CSS `--color-accent: #b14e22` in `src/app/globals.css` |
| Site primary `#c76f3a` | `docs/DESIGN.md` → `colors.primary` |
| Site ink/paper | `globals.css`: `--color-ink: #141413`, `--color-paper: #faf9f5`, dark `--bg: #1c1a16` |

**Conclusion:** subject matter came from each skill; **form language came from lizliz.xyz tokens**. There was no icon-system DESIGN.md. That is why they felt like “one badge, six stickers.”

---

## Shared hard constraints (shared rules ≠ shared style)

1. `viewBox="0 0 32 32"`, self-contained, no external assets, **no `<text>`**.
2. Readable at **32 / 36 / 48px** (site accordion ~48, README ~36).
3. Must stay clear on three grounds: paper `#faf9f5`, dark `#1c1a16`, GitHub white `#ffffff`.
4. **No shared plate formula** — forbid “same dark rounded square + cream glyph + rust accent” across the set.
5. Prefer mid/high-chroma fills + **near-black outer stroke** (or dual edge) so silhouettes hold on light *and* dark.
6. Max ~5–7 geometric primitives; every shape earns its keep.
7. Reject AI-slop defaults (purple→white gradients, generic glassmorphism, interchangeable “app icon” chrome).

---

## Per-skill design languages

### 1. `doubao-tts` — Warm Dual-Cone

| | |
|---|---|
| **Identity** | Two hosts speaking into one warm diaphragm. |
| **Medium / metaphor** | Broadcast studio loudspeaker cone + dual capsules. |
| **Palette** | Cone `#F0B56A` · rim `#3D2614` · left host `#D4552A` · right host `#1F7A7A` · membrane `#3D2614` |
| **Geometry** | **Circle** canvas (not rounded square). Facing capsule mics + center vertical waveform bars. |
| **32px strategy** | Silhouette = disc. Color split (coral vs teal) carries “dual host”; bars carry “voice.” |
| **Why this** | Podcast essence is *two temperatures of voice in one membrane*, not “speaker UI.” |
| **Rejected** | A) Dual speakers on dark plate (old). B) Speech bubbles (reads chat). C) Vinyl grooves (music player). |

---

### 2. `geo-job-hunt` — Radar Fence

| | |
|---|---|
| **Identity** | Hunt only inside a live geofence. |
| **Medium / metaphor** | Sonar/radar sweep + map pin as quarry. |
| **Palette** | Field `#B8E0D2` · fence `#0A4F45` · sweep `#1AA6A0` · pin `#E85D04` · pin hole `#FFF8F0` |
| **Geometry** | **Octagonal CRT scope** + concentric rings + **pie sweep** + teardrop pin. |
| **32px strategy** | Octagon breaks the circle club; rings = radius; wedge = scan; orange pin = quarry. |
| **Why this** | Skill is fence + hunt, not “maps app.” Radar CRT language is the operational verb. |
| **Rejected** | A) Pin-on-dark-green plate (old). B) Compass rose (travel). C) Soft disc (too close to doubao/webgl circles). |

---

### 3. `landing-page-replication-v5` — Calibration Gate

| | |
|---|---|
| **Identity** | Fidelity is a pass/fail measurement, not vibes. |
| **Medium / metaphor** | Printer registration / optical crop marks + nested frame + gate. |
| **Palette** | Ice `#DCEAF7` · steel `#163A5F` · frame `#2B6CB0` · pass `#1F8A4C` |
| **Geometry** | **Sharp square** (`rx≈1`). Corner crop ticks, nested rect, center crosshair, pass dot. |
| **32px strategy** | Hard corners = precision. Crop marks unique vs every other icon. |
| **Why this** | Pipeline is capture → density → micro-align → gate. Registration marks *are* that metaphor. |
| **Rejected** | A) Layered browser windows (old/generic). B) Magnifier. C) Checklist clipboard. |

---

### 4. `video-script-conversion` — Beat Timeline

| | |
|---|---|
| **Identity** | Spoken logic lives on a beat rail, not a page. |
| **Medium / metaphor** | NLE edit timeline / clapper energy — hook spike then spoken bars. |
| **Palette** | Rail `#E6C84A` · ink `#1C1910` · hook `#C2185B` · secondary beats `#1C1910` |
| **Geometry** | **Horizontal stadium** (pill). Base rail + uneven vertical beat ticks; leftmost hook tallest/magenta. |
| **32px strategy** | Horizontal silhouette unique in the set. Magenta hook = “first five seconds.” |
| **Why this** | Skill audits spoken beats / 850–950 band / keep the speaker’s voice — timeline, not document+play. |
| **Rejected** | A) Script page + play (old). B) Megaphone. C) Film reel alone. |

---

### 5. `design-md-visual-system` — Split Ledger

| | |
|---|---|
| **Identity** | Tokens (machine) \| judgment (human) — Genre-A split. |
| **Medium / metaphor** | Typesetter’s dual-column galley / ledger. |
| **Palette** | Left field `#0F766E` · chips `#99F6E4` / `#5EEAD4` · right parchment `#FFF7E6` · rules `#334155` · spine `#0F172A` |
| **Geometry** | **Vertical bisect** at mid. Left = stacked token swatches; right = baseline grid lines. |
| **32px strategy** | Hard split is the whole idea — readable even when tiny. |
| **Why this** | Skill’s thesis is literally “YAML tokens + prose judgment.” Icon = that architecture. |
| **Rejected** | A) Document + accent bar (old). B) Color wheel. C) “Aa” typography mark (needs text / fails 32px). |

---

### 6. `webgl-threejs-background-animation` — Depth Dissolve

| | |
|---|---|
| **Identity** | Presence in depth that can dissolve to near-zero cost. |
| **Medium / metaphor** | Wireframe volume dissolving into phosphor particles along a helical camera path. |
| **Palette** | Glass `#CFFAFE` · wire `#0F766E` · path `#134E4A` · phosphor particles `#F59E0B` · rim `#0F172A` |
| **Geometry** | **Open glass disc** (not solid ink plate) + perspective triangle wire + spiral of shrinking dots. |
| **32px strategy** | Glass + amber particles read on dark; dark rim holds on light. Spiral = camera helix. |
| **Why this** | Dual-material dissolve + spiral camera + GPU budget → *dissolve into particles*, not “garden sketch.” |
| **Rejected** | A) Dashed ink garden (old). B) Lone cube wireframe. C) Purple nebula glow (AI slop). |

---

## Set-level differentiation checklist

| Slug | Canvas shape | Hue family | Signature move |
|---|---|---|---|
| doubao-tts | circle | warm apricot + coral/teal | dual capsules on diaphragm |
| geo-job-hunt | octagon | mint + blaze orange | radar sweep wedge |
| landing-page-replication-v5 | sharp square | blueprint ice/steel | crop marks + pass |
| video-script-conversion | horizontal pill | mustard + magenta | beat rail + hook |
| design-md-visual-system | bisected rect | teal/parchment | hard vertical split |
| webgl-threejs-background-animation | glass disc | cyan glass + amber | dissolve spiral |

If two icons share both **canvas shape** and **hue family**, the set has failed.

---

## Delivery paths

- Spec: `/tmp/skills-svg-redraw/DESIGN.md` (this file)
- Assets: `public/assets/icons/skills/<slug>.svg` (overwrite only these six)
- Summary: `/tmp/skills-svg-redraw/summary.md`
