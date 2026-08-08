# TUNING · Budgets · Probes

## 1. TUNING shape

```ts
const TUNING = {
  topology: { rows, allocation, directions },
  transport: { laneSpeeds, overscanPx, maxDt, runtime },
  interaction: { focusMode, touchPreview, userControl },
  presentation: { bandPadY, rowGap, bobAmp, hoverScale, scaleK },
}
```

原则：

- `laneSpeeds[row]` 可以不同；同 lane tile 不持有 X speed。
- `runtime` 默认 `"track"`；`"floaters"` 需要书面理由和 collision policy。
- `focusMode` 默认 `"static"`；不是 `"keep-moving"`。
- `userControl` 对无限 auto motion 默认开启。
- `touchPreview` 必须显式为 `"peek"` 或 `"pin"`。

## 2. Calibrated profiles, not laws

| Key | Projects profile | Skills profile | Proposal rule |
|---|---:|---:|---|
| `rows` | `2` | `1` | Topology，不是 runtime |
| `laneSpeeds` | `[36, 36]` | `[24]` px/s | 先同速；仅经 probe 后做 lane-level 变化 |
| `gapMin / gapMax` | `16 / 44` | `20 / 48` | Gap 可 hash |
| `bandPadY` | `14` | `12` | Presentation only |
| `rowGap` | `16` | `0` | Presentation only |
| `bobAmp` | `2.5` | `1.25` | Inner Y only |
| `hoverScale` | `1.04` | `1.035` | Inner transform |
| `scaleK` | `14` | `14` | Exp damping λ |

这些是已校准 profile，不是 generic skill 的不可破铁律。

## 3. Derived values

| Value | Derive | Failure prevented |
|---|---|---|
| `cycleWidth` | Measure one unique normal-flow cycle | Guess width → wrap seam |
| `repeats` | `max(2, ceil((V + O) / C) + 1)` | Ultrawide gap / narrow DOM waste |
| `laneSpeed` | Profile seed + readability probe | Arbitrary novelty |
| `maxDt` | Clamp resume spike | Hidden-tab teleport |
| static eligibility | Same-URL spacing ≥ `2×maxTileWidth`（cycle 过短 → static） | Fake density |

`overscanPx` 至少覆盖最大 tile width + 最大 gap；从 measured content 推导，不按 device type 写死。

## 4. Motion and control policy

| Event | Transport | Layout | Resume |
|---|---|---|---|
| Initial SSR / hydration | off | static | after measure + eligibility |
| Off-screen | suspended | keep mode | automatic, clock reset |
| Hidden tab | suspended | keep mode | automatic, clock reset |
| Reduced motion | off | static | only if preference changes |
| User pause | off | static | explicit control |
| Keyboard focus enters | off | static | explicit control |
| Pointer hover | product choice | motion or frozen | may auto-resume if no user/focus pause |

Do not collapse `suspended`, `reduced`, `userPaused`, and `focusPaused` into one boolean; precedence bugs will restart motion against user intent.

## 5. Performance budget

| Budget | Pass condition | Why |
|---|---|---|
| Frame writes | ≤ lane count + active popup | O(lanes), not O(tiles) |
| Frame reads | `0` layout reads in tick | Avoid forced layout |
| Animated properties | transform / opacity only | Compositor-friendly |
| Promoted layers | Tracks + active popup; not every tile | Avoid memory/layer explosion |
| JS frame cost | p95 < `4ms` on target low-end profile | Leaves paint/input headroom |
| DOM repeats | Formula-derived; no fixed copy count | Density scales with viewport |
| Idle work | `0` rAF off-screen/hidden/static | Battery and contention |

Measure with Performance panel + Layers; `will-change` without layer evidence is not optimization.

## 6. Pitfall table

| Symptom | Root cause | Corrective move |
|---|---|---|
| Smooth but inaccessible | Infinite motion has no persistent user control | Pause/resume before content |
| Keyboard chases moving links | Focus leaves transport running | Switch to static mode on focus |
| Focus pause immediately disappears | `focusout` auto-resumes | Require explicit resume |
| Same-lane pile-up | Per-tile X speed | Rigid track or gap constraint |
| Many GPU layers / mobile jank | `will-change` on every tile | Animate lane track only |
| First frame is a tile pile | Absolute runtime before measure | Static-first + `data-ready` gate |
| Ultrawide blank seam | Fixed copies underfill | Derived repeats |
| Duplicate content looks fake | Sparse source forced into infinite loop | Static rail/grid |
| Popup cannot be inspected | `pointer-events: none` or trigger-only hover | Hoverable popup surface |
| Popup blocks content | No Esc dismiss path | Global Escape handler, preserve focus |
| Motion restarts against preference | One ambiguous pause boolean | Precedence-aware motion policy |
| Rich touch preview vanishes too fast | `peek` used for long content | Choose `pin` or simplify content |
| Cached image stays placeholder | Terminal event already passed | `complete + naturalWidth` backfill |

## 7. Mechanical probes

| Probe | Pass condition |
|---|---|
| Static-first | JS disabled and hydration recording show complete readable items |
| Eligibility | No same URL appears twice in one viewport; otherwise static |
| Continuity | Lane order unchanged; nearest-neighbor gap never below minimum |
| Lane independence | Different lane speed/direction does not alter same-lane gap |
| Dynamic fill | Narrow → ultrawide has no seam and minimal measured repeats |
| Focus mode | Tab enters; layout becomes static before next paint; focus node survives |
| User control | Pause persists across focusout, scroll, visibility, and IO changes |
| Reduced motion | Starts static; ordinary resume cannot override preference |
| Popup D/H/P | Esc dismisses; pointer enters popup; no timer auto-close |
| Touch `peek` | Hold opens, release closes, completed hold suppresses click |
| Touch `pin` | Hold pins, outside/Esc closes, quick tap navigates |
| Image states | Preloaded success/failure and reused popup URL all settle |
| Frame cost | No layout read in tick; p95 JS <4ms on target low-end profile |
| Layer count | Compositor layers scale with lanes, not rendered tile count |
| Lifecycle | Off-screen/hidden yields zero rAF; resume has no jump |

## 8. Falsifiers

放弃 motion、回到 static rail/grid，只要任一成立：

- 用户测试中 pause 使用率高且 resume 低：motion 是干扰，不是发现工具。
- Wide viewport 必须同时显示重复 URL 才能填满。
- Track runtime 仍无法在目标设备满足 frame budget。
- Popup 为满足 D/H/P 被迫复杂到接近 dialog。
- Motion 没有提高 project click-through / recall，却降低阅读完成率。
