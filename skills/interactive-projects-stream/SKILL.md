---
name: interactive-projects-stream
description: 交互式项目流 / logo stream / 无限横向内容流 / hover·长按预览 / rAF。Use when building continuous clickable content streams that need collision-safe transport, static interaction mode, user motion controls, accessible previews, and measured performance.
metadata:
  hermes:
    category: creative
---

# Interactive Projects Stream

构建“运动负责吸引、静态负责交互”的连续内容流。核心不是双行或河流皮肤，而是：有序内容、无超车 transport、可进入的 static interaction mode、真实链接和可验证的 motion policy。

## 先判定是否该流动

| 内容形态 | 选择 |
|---|---|
| 项目少、一次可读完、重复会显得造假 | Static rail / grid；到此停止 |
| 离散 slide、需要前后翻页或位置指示 | Carousel |
| 连续发现、内容顺序弱、横向运动有价值 | 本 skill |
| 每个 tile 需要独立 X 物理或碰撞 | 专用 simulation；不要偷塞进默认 runtime |

## 四条核心契约

| 契约 | 不变量 |
|---|---|
| Continuity | 同 lane 保序且维持最小 gap；全局同速只是充分条件，不是铁律 |
| Interaction | Auto motion 是 attractor；focus、user pause、reduced motion、pre-hydration 使用 static mode |
| Semantics | Primary items 是真实 `<a>`；visual repeats 不增加 keyboard/AT 噪音 |
| Control | 无限运动提供 i18n pause/resume；focus 进入后不自动重启 |

## Runtime 选择

| Runtime | 默认度 | 机制 |
|---|---:|---|
| Lane track | 默认 | 每 lane 一个 modulo offset / transform；tile 内层独立做 Y/scale |
| Independent floaters | 例外 | 仅独立 X 行为不可避免时；必须有 no-overtake 或 collision solver |
| Static mode | 必备 | Normal-flow grid/rail；也是 SSR、no-JS、focus、pause、reduced fallback |

## Concrete profiles

| 场景 | Topology | Transport | Interaction |
|---|---|---|---|
| Main Projects | 2 lanes，强 band | Calm shared lane speed | Rich preview + static mode |
| Nearby Skills | 1 lane，quiet band | Slower track | Lightweight preview + static mode |
| Partner logos | 1 lane | CSS/track only | 无 rich popup；若重复明显则 static |

## Build checklist

- [ ] 先渲染完整 static semantic source；JS 只 progressive-enhance，禁止首帧堆在 `(0,0)`。
- [ ] Measure unique cycle；按 viewport 推导 repeats，不写死 `copies: 3`。
- [ ] 默认移动 lane track；tick 内只写 transform，不读 layout，不逐 tile 建 compositor layer。
- [ ] 同 lane 禁止 per-tile X speed；允许经 probe 的 lane-level speed/direction 差异。
- [ ] IO、visibility、ResizeObserver、clock reset、reduced motion 共用一个 lifecycle。
- [ ] 多个 motion surface 共页时，共享 page-level motion governor，而非各自争夺 pause policy。

## Interaction checklist

- [ ] 用户 pause/resume 是 profile 选项（`userControl`），装饰性发现流默认 off——不暴露按钮；开启时 control 位于 region 首个 tab stop 且 user pause 不自动撤销
- [ ] Keyboard focus 默认 popup-only（流继续）；`focusStatic` 开启时 focus 切 static 且不自动恢复（键盘焦点型站点按 WCAG 2.2.2 启用）
- [ ] Hover/focus preview 必须 dismissible（Esc）、hoverable、persistent；否则改成 click disclosure。
- [ ] Touch 明确选择 `peek`（release closes）或 `pin`（outside/Esc closes）；quick tap 保持导航。
- [ ] Portal popup viewport-clamped；mount dependency、focus pointer gate、image terminal-state backfill 保留。

## Acceptance checklist

- [ ] 同 lane 无 overtaking / overlap；跨 lane speed 不影响 gap。
- [ ] JS 未执行、hydration 中、pause、focus、reduced motion 均能看到完整 static items。
- [ ] Pause control、focus-static、explicit resume、Esc、hoverable popup 全路径可操作。
- [ ] Ultrawide 无空洞；同 URL 最小间距 ≥ 2×maxTileWidth（不足则 static）；DOM repeats 为测量所得。
- [ ] 每 frame transform writes ≤ lane 数 + active popup；无 tick layout read；低端设备 frame budget 过线。
- [ ] 所有 user-facing control labels 走 host i18n；无新依赖。

架构与 scope：[references/architecture.md](references/architecture.md)  
参数、预算与 probes：[references/tuning-pitfalls.md](references/tuning-pitfalls.md)
