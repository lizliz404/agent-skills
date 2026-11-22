# fleet 派工卡模板（C 组机制修法落地版 · 2026-11-08）

> 来源：`~/fleet-orch/day-1107/concept-boundary-map.md` §C 五修法 + `design-amend-proposals.md` §C，Liz 签字「写入派工模板执行」。派工人逐卡照抄字段；worker 回执缺强制字段不收。

## 必填头

```
worker: <name>（spawn 方式：~/fleet-orch/fleet-spawn <kind> <name> --cwd <dir> [--model M]）
地盘（唯一授权目录）: <dirs> —— 其他一切目录不碰；hc ls 看到的舰队动态是观测信息不是工单；绝不接别的 worker 的活、不收养别人的终端
commit 纪律: 本地 commit 一旦落下视为已发布（增量 pusher ~2min 推 main → CF Pages）；禁 amend/rebase/reset 已 commit 历史；修错一律追加新 commit；小步提交、每步验证过再落
汇报: ~/fleet-orch/fleet-report <域> "<一句话结论+证据路径>"   # 域=space名/项目目录名；解析当期包工头，换届不 stale；解析失败会退非零而不是静默发空地址
回执: <run>/receipts/<name>.md（验收用 ~/fleet-orch/fleet-verify <回执> --card <卡> --worker <addr>）
交付正本: <project-scope 路径——产物/内容类交付（口播稿、文章、草稿、数据集、素材）的唯一落处；回执只留一行指针，不装正本>   # 内容 Liz 会消费的（口播稿/文章/草稿）落 ~/dev/repos/thinkerdoerprompter/writing/YYYY-MM-DD/<slug>/，口播按 video-script-conversion Step 8 + writing/AGENTS.md（w37c 教训 2026-11-22）
```

> 派工前先体检，别让 worker 拿死通道白跑：`~/fleet-orch/fleet-doctor`（3~6 秒：hc / watcher / boss 解析 / magpie 通道 / 目录卫生）。
> 用 `fleet-spawn ... --model M` 时它已内置同一体检；通道死了会拒派并给出可用后备。
> 工具都不在 PATH 上，一律写 `~/fleet-orch/<工具>`（fleet-doctor / fleet-spawn / fleet-report / fleet-boss / fleet-verify）。

## 产物落位（2026-11-17 加）

- 每班一个 `<域>-YYYY-MM-DD>/`（例：`cfe-2026-11-17/`、`npd-loop-2026-11-17/`），内含 `cards/` `receipts/`，需要时 `queue.md` `summary.md`。
- 任务卡进 `<run>/cards/`，回执进 `<run>/receipts/`，文件名与卡同名——验收脚本靠这个对齐。
- 内容类交付（口播稿/文章/草稿，Liz 会消费的）正本落 writing 项目（`~/dev/repos/thinkerdoerprompter/writing/YYYY-MM-DD/<slug>/`），回执只留指针行——w37c 教训：整份口播稿曾只存在于 fleet receipts，2026-11-22 纠正。
- 仓库根只放**机制件**（watchdog/fleet-* / task-card-template / DECISIONS）与历史账本；新的一次性产物不落根。
- 历史散件进 `_archived/root-scratch-YYYY-MM-DD/`，不直接删（留档）。

## 机制字段（新增/改动样式或动效时必填，缺一不收）

```
新增具名概念 = <类名族/token/组件名 或 "无">        # 登记闸：新概念必须有名有姓
登记行 = <DESIGN.md §0.1 行号/提案 或 "N/A">
许可值域 = <可用缓动集合、时长上限、scale 上限、类名族命名位>  # 品味指令翻译成值域，worker 域内自由、越界回执不合格
机制消费者清单 = <本任务要动的 markup 消费了哪些已登记机制（附行号）>  # 防 15d20a0 式回归
参照物 = <case evidence 文件路径（PNG/DOM/TEARDOWN 行号）或 "无">   # 视觉任务必须给可抄原物，禁止三次蒸馏
共享机制检查 = <是否复制了已登记实现？新 target 只许扩 selector 列表，禁第二份实现>  # 单实现纪律
```

## 验收字段

```
验收 = <build/typecheck + 本地预览截图/行为核验描述；"build 绿"≠"视觉验收过">
视觉验收对照 = <参照物 PNG 同宽截图并排 或 "N/A">
```

## 使用口径

- §0.1 是生效态表不是 replay 材料：派工引用**生效行**，不引覆盖史。
- 任务卡禁止"改动最小化"裸指令——配参照物后允许整段重写对齐。
- worker 越过许可值域 = 回执不合格打回，不派第二人补。
