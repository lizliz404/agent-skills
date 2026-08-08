# Architecture — From River Replica to Stream System

## 1. 纠偏后的本质

| 旧假设 | 新结论 | 机制 |
|---|---|---|
| 双行 / 单行是主要 abstraction | Row count 只是 topology 参数 | 同一 transport 可服务 1..N lanes |
| 所有 tile 必须全局同速 | 真正不变量是同 lane 保序、无超车、gap 不减 | Rigid track 天生满足；不同 lane 可独立 |
| Moving UI 同时承担发现与交互 | Motion 与 interaction 应分 mode | 移动吸引视线；静态保证阅读、focus、控制 |
| 每 tile absolute X 是默认 runtime | Lane track 应是默认 | O(lanes) frame writes，避免 layer explosion |
| Hover popup 能出现即可 | Additional content 有完整行为契约 | Dismissible、hoverable、persistent |

## 2. 五层模型

| Layer | Owns | 不应拥有 |
|---|---|---|
| Semantic source | 唯一 items、真实 URL、内容顺序 | visual repeats |
| Topology | lanes、分配、方向 | frame timing |
| Transport | offset、speed、wrap、pause | popup content |
| Interaction | focus、pointer、touch、pause、preview | 水面皮肤 |
| Presentation | band、mask、tile、Y/scale | semantic duplication |

Variant 应只组合这五层参数，不复制 runtime。

## 3. Mode state machine

```text
SSR / no JS
  STATIC
    └─ hydrate → MEASURING
                  ├─ eligible + allowed → MOTION
                  └─ sparse / reduced → STATIC

MOTION ── off-screen / hidden ──> SUSPENDED
MOTION ── focus / user pause ───> STATIC_INTERACTION
SUSPENDED ── visible ───────────> previous mode, clock reset
STATIC_INTERACTION ── explicit resume ──> MOTION
```

规则：

- `focusout` 不自动恢复；否则 keyboard user 刚离开就失去控制。
- `prefers-reduced-motion` 初始进入 static；不得由普通 resume 绕过。
- `userPaused` 高于 viewport/visibility 状态，直到用户显式更改。
- Static mode 是一等形态，不是“坏掉时凑合看”的 fallback。

## 4. Lane-track default

```text
region
├─ pause/resume control
└─ viewport
   ├─ lane track (one animated transform)
   │  ├─ primary cycle (semantic items)
   │  └─ measured visual repeats
   └─ lane track …
```

### Frame model

```ts
offset = (offset + laneSpeed * dt) % cycleWidth
track.style.transform = `translate3d(${-offset}px, 0, 0)`
```

- Tile 位于 normal flow；variable gap 用 margin / CSS variable。
- Hover scale 与 Y bob 放在 tile inner wrapper，避免覆盖 track transform。
- 每 lane 可以有独立 `laneSpeed` 或 direction；lane 内 tile 不得有独立 X speed。
- Tick 只写 track transforms；popup 激活时可额外写一个 fixed transform。
- Measure、`getBoundingClientRect()`、cycle width 读取只能在 layout phase / observer 回调。

### Dynamic repeats

设 unique cycle width 为 `C`、viewport 为 `V`、overscan 为 `O`：

```ts
repeats = Math.max(2, Math.ceil((V + O) / C) + 1)
```

目的不是制造更多内容，而是覆盖任意 modulo offset。重复间距判定：同 URL 相隔一个 cycle，间距须 ≥ `2×maxTileWidth`（marquee 正常第二圈）；不足说明内容密度不足，优先 static，而不是继续复制。宽屏下"同 URL 不同时出现"只适用于真正稀疏的内容（2–3 个 tile）。

- Primary cycle 独占 keyboard / AT semantics。
- Visual repeats 使用 `aria-hidden` + `tabIndex={-1}`；static mode 隐藏 repeats。
- Pause control 位于 items 前，因此 keyboard 会先触发 static mode，再进入 primary links。

## 5. Floater exception

只有以下任一成立才选 independent floaters：

- Tile 需要独立 X acceleration / attraction。
- Wrap 不是周期性的 lane modulo。
- Tile 间存在有意义的 collision / avoidance。

此时必须显式选择：

| Policy | 成本 |
|---|---|
| Same-lane equal X speed | 最简单，固定 gap |
| Order constraint + minimum gap projection | 中等，每 frame 解约束 |
| Full collision solver | 高；通常已超出本 skill |

“加一点 speed jitter”不是 policy；它只是延迟发生的 overlap bug。

## 6. Static interaction mode

进入 static mode 时：

1. 停止 transport，不只是冻结任意半屏位置。
2. Primary items 转 normal-flow grid/rail。
3. Visual repeats 隐藏且不可 focus。
4. 当前 focus item 保持同一 DOM node；禁止重建后丢 focus。
5. Popup 关闭或重新锚定；页面 layout shift 必须受控。

这同时解决：keyboard target 移动、primary instance 跑出 viewport、duplicates 污染 tab order、用户无法逐项阅读。

## 7. Preview contract

| Trigger | Open | Remain | Close |
|---|---|---|---|
| Fine hover | enter trigger | trigger 或 popup hover | leave both / Esc |
| Keyboard | focus trigger | focus remains / popup valid | blur / Esc |
| Touch `peek` | long-press completes | while held | release/cancel |
| Touch `pin` | long-press completes | pinned | outside tap / Esc |

Rich hover/focus preview 若覆盖 meaningful content，必须：

- **Dismissible**：Esc 不移动 focus 即关闭。
- **Hoverable**：pointer 可进入 popup；`pointer-events: none` 不合格。
- **Persistent**：不按 timer 自动消失。

若产品不愿承担这三项，使用 click disclosure 或只保留 tile 内信息。

## 8. Page-level motion governor

当 stream 与 WebGL background、hero animation 等同页时，共享：

```ts
type MotionPolicy = {
  reduced: boolean
  pageVisible: boolean
  userPaused: boolean
  energyTier: "static" | "low" | "full"
}
```

- 一个 user control 可暂停所有非必要持续运动。
- 各 surface 仍拥有自己的 IO gate；governor 只统一 policy，不接管 rendering。
- 不为单个 stream 引入全局 state library；React context / host signal 足够。

## 9. Scope boundary

| 收编 | 明确不收 |
|---|---|
| Static-first enhancement | Discrete carousel navigation |
| Focus/static interaction mode | Feed virtualization |
| Motion controls / shared governor | Vertical masonry / 2D physics |
| Preview accessibility | SEO/GEO、ranking、content strategy |
| Lane-level performance budget | Canvas/WebGL tile rendering |
| Lifecycle 与其他 motion skill 组合 | 通用 animation framework |

## 10. Primary evidence

- WCAG 2.2 SC 2.2.2：持续自动运动需要 pause / stop / hide mechanism。  
  https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide
- WAI APG Carousel：auto motion 遇 keyboard focus 应停止，且不应未经用户请求自动重启；control 应位于 rotating content 之前。  
  https://www.w3.org/WAI/ARIA/apg/patterns/carousel/
- WCAG 2.2 SC 1.4.13：hover/focus additional content 要 dismissible、hoverable、persistent。  
  https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus
- web.dev：动画优先 transform/opacity，并避免过量 compositor layers。  
  https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count
