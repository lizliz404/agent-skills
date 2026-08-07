'use client'

import { useEffect, useRef, useState } from 'react'
import {
  Scene,
  PerspectiveCamera,
  WebGLRenderer,
  GridHelper,
  BufferGeometry,
  DoubleSide,
  LineSegments,
  LineBasicMaterial,
  LineDashedMaterial,
  Mesh,
  MeshBasicMaterial,
  PlaneGeometry,
  Float32BufferAttribute,
  Fog,
  Color,
} from 'three'

// ---------------------------------------------------------------------------
// Paper Ink Garden palette — matches globals.css theme tokens.
// Light mode is the default; dark mode swaps the dominant inks to the same
// tokens the site uses (`--bg: #1c1a16`, `--fg: #e8e4dd`, `--fg-secondary:
// #9b9488`). Accent stays constant across modes so the visual anchor holds.
// ---------------------------------------------------------------------------
const PAPER = 0xfaf9f5
const INK = 0x141413
const INK_2 = 0x716d64
const ACCENT = 0xb14e22
const BLUE = 0x4f6f8f
const GREEN = 0x6f8f72
const BORDER = 0xddd7ca
const MUTED = 0xf1eee6 // fog + "unresolved paper" tint

// Dark-mode palette
const DARK_BG = 0x1c1a16
const DARK_FG = 0xe8e4dd
const DARK_FG_2 = 0x9b9488
const DARK_BORDER = 0x3a3530

const PROGRESS_MAX = 0.7

// All hand-tuned magic numbers gathered so the "feel" is adjustable in one place.
const TUNING = {
  maxPixelRatio: 1.5,
  camera: { radius: 11, baseY: 5.5, amp: 2.2 },
  // Base azimuth speed + a small variable-speed wobble (radians/sec).
  // Slower than the reference: this garden is meant to be contemplated.
  spin: { base: 0.05, wobble: 0.018 },
  parallaxK: 5,
  parallaxAmount: 0.35,
  // Per-batch base opacity (the visual weight hierarchy) + shared breathing.
  weight: { inkHeavy: 0.72, inkMedium: 0.5, inkLight: 0.34, accent: 0.66 },
  breath: { amp: 0.1, speed: 0.5 },
  // Category-specific dash ratios: heavy ink reads nearly solid, while
  // annotations stay like light drafting marks.
  dash: {
    inkHeavy: { dashSize: 0.24, gapSize: 0.1 },
    inkMedium: { dashSize: 0.12, gapSize: 0.18 },
    inkLight: { dashSize: 0.04, gapSize: 0.22 },
    accent: { dashSize: 0.08, gapSize: 0.24 },
  },
  progress: {
    hoverPerSecond: 0.015,
    clickBoost: 0.06,
    smoothK: 2,
    cameraDrop: 0.7,
    // Ambient floor: progress rises to `idleTarget` over `idleRampSeconds`
    // just from being on screen — no pointer input required.
    idleTarget: 0.32,
    idleRampSeconds: 3.5,
  },
  // Primary grid drifts forward one cell then wraps -> "paper breathing".
  grid: { cell: 1.25, driftSpeed: 0.1 },
} as const

type CategoryKey = 'inkHeavy' | 'inkMedium' | 'inkLight' | 'accent'

interface CategorySpec {
  key: CategoryKey
  color: number
  solidColor: number
  weight: number
  dash: { dashSize: number; gapSize: number }
  phase: number
}

// Categories are built lazily inside the effect because their colors depend
// on the active theme (dark mode swaps the ink tones).
function buildCategories(dark: boolean): CategorySpec[] {
  const ink = dark ? DARK_FG : INK
  const ink2 = dark ? DARK_FG_2 : INK_2
  const solidInk = dark ? DARK_FG : 0x000000
  const solidInk2 = dark ? DARK_FG_2 : 0x4a463e
  return [
    {
      key: 'inkHeavy',
      color: ink,
      solidColor: solidInk,
      weight: TUNING.weight.inkHeavy,
      dash: TUNING.dash.inkHeavy,
      phase: 0,
    },
    {
      key: 'inkMedium',
      color: ink2,
      solidColor: solidInk2,
      weight: TUNING.weight.inkMedium,
      dash: TUNING.dash.inkMedium,
      phase: 0.6,
    },
    {
      key: 'inkLight',
      color: dark ? DARK_FG_2 : BLUE,
      solidColor: dark ? DARK_FG_2 : 0x39536f,
      weight: TUNING.weight.inkLight,
      dash: TUNING.dash.inkLight,
      phase: 1.3,
    },
    {
      key: 'accent',
      color: ACCENT,
      solidColor: ACCENT,
      weight: TUNING.weight.accent,
      dash: TUNING.dash.accent,
      phase: 2.1,
    },
  ]
}

// Cheap probe so we can bail to the CSS fallback before touching WebGLRenderer.
function webglAvailable(): boolean {
  try {
    const canvas = document.createElement('canvas')
    return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
  } catch {
    return false
  }
}

function smoothstep(value: number, edge0: number, edge1: number) {
  const x = Math.min(1, Math.max(0, (value - edge0) / (edge1 - edge0)))
  return x * x * (3 - 2 * x)
}

type Vec2 = [number, number]

const FLOOR = 0.02 // default drawing height above the grid

// --- Geometry primitives (all append segment pairs to a batch buffer) --------

// A single flat segment on the XZ plane.
function pushSeg(seg: number[], ax: number, az: number, bx: number, bz: number, y = FLOOR) {
  seg.push(ax, y, az, bx, y, bz)
}

// Arc appended as segment pairs (circles, leaves, compass rings).
function pushArc(
  seg: number[],
  cx: number,
  cz: number,
  r: number,
  a0: number,
  a1: number,
  y = FLOOR,
  segs = 24,
) {
  let px = cx + r * Math.cos(a0)
  let pz = cz + r * Math.sin(a0)
  for (let i = 1; i <= segs; i++) {
    const a = a0 + ((a1 - a0) * i) / segs
    const nx = cx + r * Math.cos(a)
    const nz = cz + r * Math.sin(a)
    seg.push(px, y, pz, nx, y, nz)
    px = nx
    pz = nz
  }
}

// Spiral from center outward — the signature "flower top view" motif.
// `turns` controls how many revolutions; `r0` is the inner radius, `r1` outer.
function pushSpiral(
  seg: number[],
  cx: number,
  cz: number,
  r0: number,
  r1: number,
  turns: number,
  y = FLOOR,
  segsPerTurn = 36,
) {
  const total = Math.max(4, Math.floor(turns * segsPerTurn))
  const a0 = 0
  const a1 = turns * Math.PI * 2
  let px = cx + r0 * Math.cos(a0)
  let pz = cz + r0 * Math.sin(a0)
  for (let i = 1; i <= total; i++) {
    const t = i / total
    const a = a0 + (a1 - a0) * t
    const r = r0 + (r1 - r0) * t
    const nx = cx + r * Math.cos(a)
    const nz = cz + r * Math.sin(a)
    seg.push(px, y, pz, nx, y, nz)
    px = nx
    pz = nz
  }
}

// Cubic bezier unfolded into a polyline of `steps` segments. Control points
// in world XZ, y constant. Used for the three "wind path" ribbons.
function pushBezier(
  seg: number[],
  p0: Vec2,
  p1: Vec2,
  p2: Vec2,
  p3: Vec2,
  y = FLOOR,
  steps = 32,
) {
  let px = p0[0]
  let pz = p0[1]
  for (let i = 1; i <= steps; i++) {
    const t = i / steps
    const u = 1 - t
    const nx =
      u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0]
    const nz =
      u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]
    seg.push(px, y, pz, nx, y, nz)
    px = nx
    pz = nz
  }
}

// A simplified leaf: two symmetric arcs meeting at both tips.
// `len` along +X, half-width `w`; rotated by `rot` radians around (cx, cz).
function pushLeaf(
  seg: number[],
  cx: number,
  cz: number,
  len: number,
  w: number,
  rot: number,
  y = FLOOR,
) {
  const halfLen = len / 2
  // Two quadratic-ish arcs: one above, one below the spine.
  // Approximate each with two segments for a hand-drawn feel.
  const steps = 14
  // Top arc
  let px = -halfLen
  let pz = 0
  for (let i = 1; i <= steps; i++) {
    const t = i / steps
    const x = -halfLen + len * t
    // Parabolic profile
    const zNorm = 1 - Math.pow(2 * t - 1, 2) // 0 at tips, 1 at mid
    const nz = w * zNorm
    const rx = cx + x * Math.cos(rot) - nz * Math.sin(rot)
    const rz = cz + x * Math.sin(rot) + nz * Math.cos(rot)
    const prx = cx + px * Math.cos(rot) - pz * Math.sin(rot)
    const prz = cz + px * Math.sin(rot) + pz * Math.cos(rot)
    seg.push(prx, y, prz, rx, y, rz)
    px = x
    pz = nz
  }
  // Bottom arc (mirror)
  px = -halfLen
  pz = 0
  for (let i = 1; i <= steps; i++) {
    const t = i / steps
    const x = -halfLen + len * t
    const zNorm = 1 - Math.pow(2 * t - 1, 2)
    const nz = -w * zNorm
    const rx = cx + x * Math.cos(rot) - nz * Math.sin(rot)
    const rz = cz + x * Math.sin(rot) + nz * Math.cos(rot)
    const prx = cx + px * Math.cos(rot) - pz * Math.sin(rot)
    const prz = cz + px * Math.sin(rot) + pz * Math.cos(rot)
    seg.push(prx, y, prz, rx, y, rz)
    px = x
    pz = nz
  }
  // Spine
  const sx0 = cx - halfLen * Math.cos(rot)
  const sz0 = cz - halfLen * Math.sin(rot)
  const sx1 = cx + halfLen * Math.cos(rot)
  const sz1 = cz + halfLen * Math.sin(rot)
  pushSeg(seg, sx0, sz0, sx1, sz1, y)
}

// Small botanical-annotation cross (four arms).
function pushCross(seg: number[], cx: number, cz: number, s: number, y = FLOOR) {
  pushSeg(seg, cx - s, cz, cx + s, cz, y)
  pushSeg(seg, cx, cz - s, cx, cz + s, y)
}

// Small dimension tick: a baseline + two end ticks (like the plant-plate marks).
function pushDimensionTick(
  seg: number[],
  x0: number,
  z0: number,
  x1: number,
  z1: number,
  tick: number,
  y = FLOOR,
) {
  pushSeg(seg, x0, z0, x1, z1, y)
  // End ticks perpendicular to the line.
  const dx = x1 - x0
  const dz = z1 - z0
  const len = Math.hypot(dx, dz) || 1
  const px = (-dz / len) * tick
  const pz = (dx / len) * tick
  pushSeg(seg, x0 - px, z0 - pz, x0 + px, z0 + pz, y)
  pushSeg(seg, x1 - px, z1 - pz, x1 + px, z1 + pz, y)
}

// A tiny dot (a single zero-length segment renders nothing, so use a very
// short 2-segment cross instead — reads as a period at line weight).
function pushDot(seg: number[], cx: number, cz: number, y = FLOOR) {
  const s = 0.02
  pushSeg(seg, cx - s, cz, cx + s, cz, y)
  pushSeg(seg, cx, cz - s, cx, cz + s, y)
}

// Paper grain: deterministic pseudo-random short strokes at low opacity.
function pushPaperGrain(seg: number[], count = 140) {
  const rand = (seed: number) => {
    const n = Math.sin(seed * 12.9898) * 43758.5453
    return n - Math.floor(n)
  }
  for (let i = 0; i < count; i++) {
    const x = -6 + rand(i + 1) * 12
    const z = -6 + rand(i + 101) * 12
    const a = rand(i + 201) * Math.PI
    const len = 0.015 + rand(i + 301) * 0.05
    seg.push(x, FLOOR * 0.5, z, x + Math.cos(a) * len, FLOOR * 0.5, z + Math.sin(a) * len)
  }
}

function makeLineSegments(seg: number[], material: LineDashedMaterial | LineBasicMaterial): LineSegments {
  const geo = new BufferGeometry()
  geo.setAttribute('position', new Float32BufferAttribute(seg, 3))
  const line = new LineSegments(geo, material)
  if (material instanceof LineDashedMaterial) line.computeLineDistances()
  return line
}

interface HeroCanvasProps {
  className?: string
}

export default function HeroCanvas({ className }: HeroCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const progressTargetRef = useRef(0)
  const progressRef = useRef(0)
  // Strict-mode / double-mount guard: only one WebGL context per mount.
  const initedRef = useRef(false)
  const [failed, setFailed] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    if (initedRef.current) return
    if (!webglAvailable()) {
      setFailed(true)
      return
    }
    initedRef.current = true

    let disposed = false
    let animId = 0
    let running = false

    const w = container.clientWidth || 360
    const h = container.clientHeight || 360

    // Detect dark mode once at mount. We observe `data-theme` so an explicit
    // user toggle (set by the site's theme switcher) wins over the OS
    // preference; when absent we fall back to `prefers-color-scheme`.
    const rootEl = document.documentElement
    const explicitTheme = rootEl.dataset.theme
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const dark = explicitTheme ? explicitTheme === 'dark' : prefersDark

    const CATEGORIES = buildCategories(dark)
    const bg = dark ? DARK_BG : PAPER
    const fogColor = dark ? DARK_BG : MUTED
    const gridColor = dark ? DARK_BORDER : BORDER
    const paperColor = dark ? DARK_FG_2 : INK_2

    const scene = new Scene()
    const fog = new Fog(fogColor, 10, 32)
    scene.fog = fog

    const camera = new PerspectiveCamera(50, w / h, 0.1, 200)

    let renderer: WebGLRenderer
    try {
      renderer = new WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'low-power',
        stencil: false,
        depth: false, // scene is all lines/transparent; depth test unused
      })
    } catch {
      initedRef.current = false
      setFailed(true)
      return
    }
    renderer.setClearColor(new Color(bg), 0)
    renderer.setSize(w, h)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, TUNING.maxPixelRatio))
    container.appendChild(renderer.domElement)

    // --- Paper grids: coarse primary (drifts) + fine secondary (static) ------
    const grid = new GridHelper(14, 11, gridColor, gridColor)
    const gridMat = grid.material as LineBasicMaterial
    gridMat.transparent = true
    gridMat.opacity = 0.22
    gridMat.depthWrite = false
    gridMat.depthTest = false
    scene.add(grid)

    const grid2 = new GridHelper(10, 28, gridColor, gridColor)
    const grid2Mat = grid2.material as LineBasicMaterial
    grid2Mat.transparent = true
    grid2Mat.opacity = 0.08
    grid2Mat.depthWrite = false
    grid2Mat.depthTest = false
    grid2.position.y = -0.01
    scene.add(grid2)

    // --- Zone fills: watercolor-ish color washes under each motif ------------
    const addZoneFill = (
      x: number,
      z: number,
      width: number,
      depth: number,
      color: number,
      opacity: number,
    ) => {
      const geo = new PlaneGeometry(width, depth)
      const mat = new MeshBasicMaterial({
        color,
        transparent: true,
        opacity,
        side: DoubleSide,
        depthWrite: false,
        depthTest: false,
      })
      const plane = new Mesh(geo, mat)
      plane.rotation.x = -Math.PI / 2
      plane.position.set(x, -0.018, z)
      plane.renderOrder = -1
      scene.add(plane)
    }

    addZoneFill(-3.2, 0.4, 3.6, 3.6, GREEN, 0.055) // left circular patch
    addZoneFill(0.2, -0.2, 3.2, 3.2, ACCENT, 0.05) // central spiral
    addZoneFill(3.4, 0.6, 3.8, 3.0, BLUE, 0.052) // right path wash

    // --- Four weighted batches (each one LineSegments = the batched layer) ---
    // inkHeavy : main flowers — concentric circles + the central spiral
    // inkMedium: three bezier wind paths sweeping left-to-right
    // inkLight : annotation crosses, dots, dimension ticks, green accents
    // accent   : five to seven orange leaves — the focal motif
    const inkHeavySeg: number[] = []
    const inkMediumSeg: number[] = []
    const inkLightSeg: number[] = []
    const accentSeg: number[] = []
    const paperSeg: number[] = []

    // ------- Flower cluster 1 (left): three concentric rings + bud ---------
    pushArc(inkHeavySeg, -3.2, 0.4, 0.55, 0, Math.PI * 2, FLOOR, 32)
    pushArc(inkHeavySeg, -3.2, 0.4, 0.95, 0, Math.PI * 2, FLOOR, 40)
    pushArc(inkHeavySeg, -3.2, 0.4, 1.35, 0, Math.PI * 2, FLOOR, 48)
    pushArc(inkHeavySeg, -3.2, 0.4, 0.2, 0, Math.PI * 2, FLOOR, 18)

    // ------- Central spiral: the signature bloom ---------------------------
    pushSpiral(inkHeavySeg, 0.2, -0.2, 0.08, 1.35, 3.5, FLOOR, 40)
    pushArc(inkHeavySeg, 0.2, -0.2, 1.45, 0, Math.PI * 2, FLOOR, 48)

    // ------- Flower cluster 2 (right): tighter bloom -----------------------
    pushArc(inkHeavySeg, 3.4, 0.6, 0.4, 0, Math.PI * 2, FLOOR, 28)
    pushArc(inkHeavySeg, 3.4, 0.6, 0.75, 0, Math.PI * 2, FLOOR, 36)
    pushArc(inkHeavySeg, 3.4, 0.6, 1.05, 0, Math.PI * 2, FLOOR, 44)

    // ------- Three wind paths: bezier ribbons crossing the scene ----------
    pushBezier(
      inkMediumSeg,
      [-5.5, 2.2],
      [-2.0, 3.4],
      [1.8, 2.4],
      [5.5, 2.8],
      FLOOR,
      40,
    )
    pushBezier(
      inkMediumSeg,
      [-5.5, -0.6],
      [-2.4, 0.4],
      [1.6, -1.4],
      [5.5, -0.4],
      FLOOR,
      40,
    )
    pushBezier(
      inkMediumSeg,
      [-5.5, -3.0],
      [-2.0, -2.0],
      [2.4, -3.4],
      [5.5, -2.2],
      FLOOR,
      40,
    )

    // ------- Annotations: crosses, ticks, dots (plant-plate style) ---------
    pushCross(inkLightSeg, -4.6, -1.6, 0.14)
    pushCross(inkLightSeg, -1.6, 2.4, 0.12)
    pushCross(inkLightSeg, 2.4, -2.2, 0.13)
    pushCross(inkLightSeg, 4.6, 2.0, 0.11)
    pushCross(inkLightSeg, -0.4, -3.4, 0.1)

    pushDimensionTick(inkLightSeg, -4.4, -2.6, -2.0, -2.6, 0.1)
    pushDimensionTick(inkLightSeg, 1.4, 1.6, 4.4, 1.6, 0.1)
    pushDimensionTick(inkLightSeg, -1.6, -3.8, 1.8, -3.8, 0.1)

    // A few scattered dots
    pushDot(inkLightSeg, -2.4, 1.2)
    pushDot(inkLightSeg, 1.4, 0.8)
    pushDot(inkLightSeg, 3.0, -1.4)
    pushDot(inkLightSeg, -3.6, -2.4)
    pushDot(inkLightSeg, 0.8, 2.4)
    pushDot(inkLightSeg, 4.2, -0.4)

    // A small green sprout icon (annotation color: green tint in light mode)
    // — drawn into the same inkLight batch so it breathes with annotations.
    pushArc(inkLightSeg, -4.8, 1.8, 0.24, 0, Math.PI * 2, FLOOR, 14)
    pushSeg(inkLightSeg, -4.8, 1.56, -4.8, 1.2)
    pushSeg(inkLightSeg, -4.8, 1.38, -4.6, 1.3)
    pushSeg(inkLightSeg, -4.8, 1.38, -5.0, 1.3)

    // ------- Accent leaves (the focal motif) --------------------------------
    pushLeaf(accentSeg, -1.4, -1.2, 1.4, 0.32, -0.4)
    pushLeaf(accentSeg, 1.6, 1.4, 1.2, 0.28, 0.7)
    pushLeaf(accentSeg, 3.4, -1.6, 1.1, 0.26, -0.2)
    pushLeaf(accentSeg, -3.6, 2.4, 1.0, 0.24, 0.3)
    pushLeaf(accentSeg, 0.2, -3.4, 1.3, 0.3, 0.1)
    pushLeaf(accentSeg, 4.6, 0.4, 0.9, 0.22, -0.9)

    // Paper grain for tactility
    pushPaperGrain(paperSeg)

    // --- Build batched LineSegments ------------------------------------------
    const paperMat = new LineBasicMaterial({
      color: paperColor,
      transparent: true,
      opacity: 0.04,
      depthWrite: false,
      depthTest: false,
    })

    const addLineBatch = (
      seg: number[],
      material: LineDashedMaterial | LineBasicMaterial,
      renderOrder: number,
    ) => {
      const line = makeLineSegments(seg, material)
      line.renderOrder = renderOrder
      scene.add(line)
      return line
    }

    addLineBatch(paperSeg, paperMat, 1)

    const segByCategory: Record<CategoryKey, number[]> = {
      inkHeavy: inkHeavySeg,
      inkMedium: inkMediumSeg,
      inkLight: inkLightSeg,
      accent: accentSeg,
    }

    // One dashed (sketch) + one solid (resolved) material per category, built
    // and animated from the single CATEGORIES config above.
    const categoryRuntime = CATEGORIES.map((cat) => {
      const segments = segByCategory[cat.key]
      const dashMat = new LineDashedMaterial({
        color: cat.color,
        transparent: true,
        opacity: cat.weight,
        depthWrite: false,
        depthTest: false,
        dashSize: cat.dash.dashSize,
        gapSize: cat.dash.gapSize,
      })
      const solidMat = new LineBasicMaterial({
        color: cat.solidColor,
        transparent: true,
        opacity: 0,
        depthWrite: false,
        depthTest: false,
      })
      addLineBatch(segments, dashMat, 2)
      addLineBatch(segments, solidMat, 3)
      return { ...cat, dashMat, solidMat }
    })

    // Applies a given progress/time state to every material in one place.
    const applyVisualState = (progressEffect: number, t: number) => {
      gridMat.opacity = 0.22 + (0.08 - 0.22) * progressEffect
      grid2Mat.opacity = 0.08 + (0.03 - 0.08) * progressEffect
      fog.near = 10 + (16 - 10) * progressEffect

      const b = TUNING.breath
      for (const cat of categoryRuntime) {
        const pulse = cat.weight + b.amp * Math.sin(t * b.speed + cat.phase)
        cat.dashMat.opacity = pulse * (1 - progressEffect * 0.7)
        cat.solidMat.opacity = pulse * progressEffect * 0.85
        cat.dashMat.gapSize = cat.dash.gapSize * (1 - progressEffect * 0.6)
      }

      paperMat.opacity = 0.04 - progressEffect * 0.01
    }

    // --- Camera helix + parallax ---------------------------------------------
    const { radius, baseY, amp } = TUNING.camera
    let angle = 0
    let gridDrift = 0
    let progressEffect = 0

    const mouse = { x: 0, y: 0 }
    const eased = { x: 0, y: 0 }

    // Portrait framing: narrow aspects boost FOV slightly so the composition
    // doesn't crop to the center.
    const portraitBoost = () => {
      const aspect = camera.aspect
      return aspect < 1.3 ? 1 - aspect / 1.3 : 0
    }

    const positionCamera = () => {
      const pa = TUNING.parallaxAmount
      const groundedBaseY = baseY - TUNING.progress.cameraDrop * progressEffect
      const pb = portraitBoost()
      const effectiveRadius = radius * (1 + pb * 0.5)
      camera.position.x = effectiveRadius * Math.cos(angle) + eased.x * pa
      camera.position.z = effectiveRadius * Math.sin(angle)
      camera.position.y = groundedBaseY + amp * Math.sin(angle * 0.5) + eased.y * pa
      camera.lookAt(eased.x * pa, 0.4, 0)
    }
    positionCamera()

    const onResize = () => {
      if (disposed) return
      const cw = container.clientWidth || 360
      const ch = container.clientHeight || 360
      camera.aspect = cw / ch
      camera.fov = 50 + portraitBoost() * 12
      camera.updateProjectionMatrix()
      renderer.setSize(cw, ch)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, TUNING.maxPixelRatio))
    }
    const ro = new ResizeObserver(onResize)
    ro.observe(container)
    window.addEventListener('resize', onResize)

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    let lastProgressMoveT = 0
    let lastBoostT = -1000
    let startTime: number | null = null

    const addProgress = (amount: number) => {
      progressTargetRef.current = Math.min(PROGRESS_MAX, progressTargetRef.current + amount)
    }

    const updatePointer = (clientX: number, clientY: number) => {
      const rect = container.getBoundingClientRect()
      const width = rect.width || 1
      const height = rect.height || 1
      mouse.x = ((clientX - rect.left) / width) * 2 - 1
      mouse.y = ((clientY - rect.top) / height) * 2 - 1
    }

    const accumulateMoveProgress = (now: number) => {
      if (now - lastProgressMoveT < 33) return
      if (lastProgressMoveT > 0) {
        const dt = Math.min((now - lastProgressMoveT) / 1000, 0.2)
        addProgress(TUNING.progress.hoverPerSecond * dt)
      }
      lastProgressMoveT = now
    }

    const onMouseMove = (e: MouseEvent) => {
      updatePointer(e.clientX, e.clientY)
      accumulateMoveProgress(performance.now())
    }

    const onClick = () => {
      const now = performance.now()
      if (now - lastBoostT < 500) return
      lastBoostT = now
      addProgress(TUNING.progress.clickBoost)
    }

    const onTouchMove = (e: TouchEvent) => {
      const touch = e.touches[0]
      if (!touch) return
      updatePointer(touch.clientX, touch.clientY)
      accumulateMoveProgress(performance.now())
    }

    const onTouchEnd = () => {
      const now = performance.now()
      if (now - lastBoostT < 500) return
      lastBoostT = now
      addProgress(TUNING.progress.clickBoost)
    }

    const onContextLost = (e: Event) => {
      e.preventDefault()
      dispose()
      setFailed(true)
    }

    // Fully release GPU resources on unmount (or context loss).
    const dispose = () => {
      if (disposed) return
      disposed = true
      cancelAnimationFrame(animId)
      running = false
      window.removeEventListener('resize', onResize)
      ro.disconnect()
      container.removeEventListener('mousemove', onMouseMove)
      container.removeEventListener('click', onClick)
      container.removeEventListener('touchmove', onTouchMove)
      container.removeEventListener('touchend', onTouchEnd)
      document.removeEventListener('visibilitychange', onVisibility)
      renderer.domElement.removeEventListener('webglcontextlost', onContextLost)
      io.disconnect()
      scene.traverse((obj) => {
        const mesh = obj as { geometry?: { dispose(): void }; material?: unknown }
        mesh.geometry?.dispose?.()
        const mat = mesh.material
        if (Array.isArray(mat)) mat.forEach((m) => (m as { dispose(): void }).dispose())
        else (mat as { dispose?: () => void })?.dispose?.()
      })
      renderer.dispose()
      renderer.forceContextLoss()
      renderer.domElement.remove()
    }

    renderer.domElement.addEventListener('webglcontextlost', onContextLost, false)

    // Reduced motion: render a single pleasing static frame, no loop.
    if (reduceMotion) {
      angle = 0.9
      progressRef.current = TUNING.progress.idleTarget
      progressTargetRef.current = TUNING.progress.idleTarget
      progressEffect = smoothstep(progressRef.current, 0, PROGRESS_MAX)
      positionCamera()
      applyVisualState(progressEffect, 0)
      renderer.render(scene, camera)
      setReady(true)
    }

    let lastT = performance.now()
    const animate = () => {
      if (!running || disposed) return
      animId = requestAnimationFrame(animate)

      const now = performance.now()
      const dt = Math.min((now - lastT) / 1000, 0.1)
      lastT = now
      const t = now * 0.001

      const elapsed = startTime === null ? 0 : (now - startTime) / 1000
      const idleFloor = TUNING.progress.idleTarget * smoothstep(elapsed, 0, TUNING.progress.idleRampSeconds)
      const target = Math.max(progressTargetRef.current, idleFloor)

      const progressAlpha = 1 - Math.exp(-TUNING.progress.smoothK * dt)
      progressRef.current += (target - progressRef.current) * progressAlpha
      progressEffect = smoothstep(progressRef.current, 0, PROGRESS_MAX)

      // Frame-rate-independent azimuth + parallax easing.
      angle += (TUNING.spin.base + TUNING.spin.wobble * Math.sin(angle * 0.7)) * dt
      const alpha = 1 - Math.exp(-TUNING.parallaxK * dt)
      eased.x += (mouse.x - eased.x) * alpha
      eased.y += (-mouse.y - eased.y) * alpha
      positionCamera()

      // Slow grid drift, wrapping every cell -> "paper breathing".
      gridDrift = (gridDrift + TUNING.grid.driftSpeed * dt) % TUNING.grid.cell
      grid.position.z = gridDrift

      applyVisualState(progressEffect, t)

      renderer.render(scene, camera)
    }

    const startLoop = () => {
      if (running || disposed || reduceMotion) return
      if (startTime === null) startTime = performance.now()
      running = true
      lastT = performance.now()
      animId = requestAnimationFrame(animate)
    }
    const stopLoop = () => {
      running = false
      cancelAnimationFrame(animId)
    }

    container.addEventListener('mousemove', onMouseMove, { passive: true })
    container.addEventListener('click', onClick, { passive: true })
    container.addEventListener('touchmove', onTouchMove, { passive: true })
    container.addEventListener('touchend', onTouchEnd, { passive: true })

    const onVisibility = () => {
      if (document.hidden) stopLoop()
      else if (isInView) startLoop()
    }
    document.addEventListener('visibilitychange', onVisibility)

    // Gate the whole render loop on viewport visibility.
    let isInView = false
    const io = new IntersectionObserver(
      ([entry]) => {
        isInView = entry.isIntersecting
        if (isInView && !document.hidden) {
          setReady(true)
          startLoop()
        } else {
          stopLoop()
        }
      },
      { threshold: 0 },
    )
    io.observe(container)

    return dispose
  }, [])

  if (failed) return null

  return (
    <div
      ref={containerRef}
      className={className}
      aria-hidden="true"
      style={{
        display: 'block',
        opacity: ready ? 1 : 0,
        transition: 'opacity 1.2s ease-out',
      }}
    />
  )
}
