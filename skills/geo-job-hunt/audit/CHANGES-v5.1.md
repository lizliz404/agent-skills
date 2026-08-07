# v5.0.1 → v5.1.1 变更清单(复核反馈落地)

复核反馈(独立复核 v5.0.1 pack)结论:**不做 v6 式审计**——系统已过「审计能创造增量信息」拐点;
本轮按「欠的债还掉 + 缺的数据用真实投递补」执行。三件事 + 一个纠正。

## 修正 1:config timeout 补丁 —— 事实纠正 + 脚本化

- **纠正**:复核反馈称「四处 config.yaml 依然一个都没改」——**不属实**。v5 合入时四处均已补
  `amap.timeout: 120`(根 config + writing/lyric/trading,writing 经 `hermes config set`)。
  复核方看不到的原因:pack 有意不收录本机 config.yaml(敏感),其结论基于信息缺失而非事实。
- **采纳其建议**:「人工多处同步 = 漂移风险」原则同样适用于 config。新增
  `scripts/ensure_amap_timeout.py`:幂等(缺才插、已有跳过)、默认 dry-run 打印状态、
  `--yes` 落盘、模式不匹配拒绝写入。实测对 4 处 config 输出「已含 timeout(幂等跳过)」。
- 新机器/未来漂移:跑一次即可,不再依赖「人记得住」。

## 修正 2:死开关修复(复核新发现,前两轮审计均未抓到)

- `apply_batch.py` 的 `--require-kind`(`action="store_true", default=True`)是**假开关**:
  不传是 True,传了还是 True,唯一真正生效的是反面 `--allow-empty-kind`。
- 修法:删除 `--require-kind` 与 `if args.allow_empty_kind: args.require_kind = False`,
  逻辑改为 `if not args.allow_empty_kind:`。CLI 面收敛为一个真实开关,help 文案同步。
- 验证:py_compile 通过、--help 仅剩 `--allow-empty-kind`、合成数据 dry-run 3 岗→2 岗正常。

## 修正 3:真源 git 基线(复核:「不做才是风险」的唯一项)

- `~/.agents/skills/geo-job-hunt/` 已 `git init -b main`,`.gitignore` 排除
  `logs/`、`__pycache__/`、`*.pyc`、`*.log`。
- 初始基线提交 `3f96094`(v5.1.0 全量)。此后每次合入草稿→真源可回滚。
- 注意:repo 只覆盖该 skill 目录,不波及 `~/.agents/skills/` 下其他技能。

## 未做(有意,如实)

- **真实投递仍为 0**:猎聘限流窗口未恢复(2026-08-01 21:31 探测仍 `limited`)。
  复核方说的对:OK_UNVERIFIED → 真实契约、S5 是否合并、jobKind 枚举反推,
  全部依赖一次真实 `user-apply-job`。这是唯一真正的瓶颈,且**审计生不出数据**。
- 解锁清单(限流恢复后,需用户确认后执行):
  ```bash
  python3 scripts/probe_limit.py          # 看门狗输出「已恢复」再继续
  python3 scripts/geo_job_hunt.py forward --address "…" --radius 3000 --city 杭州 \
    --job "实习|产品|AI|Agent" --format json --out /tmp/hunt.json
  python3 scripts/apply_batch.py --hunt /tmp/hunt.json --max 1   # 只投 1 个,拿原始响应体
  ```
  拿到响应后:更新 `classify_business_payload` 与 SKILL 的 apply 契约描述,OK_UNVERIFIED 升级。

## 复核方结论(认可并保留)

- 工程质量非瓶颈:stdlib-only、原子写、限流 3 形态识别、退出码契约 —— 不再优化。
- SKILL/README 信息密度无虚胖,不做「更好读」重排。
- 不做 v6 式审计(Sheeran-mean 陷阱:格式工整、边际信息趋零)。

---

## v5.1.1 增补:稳态间隔纠偏(用户提问驱动)

**问题(用户原话要点)**:「开口处是不是本来就应该更小?刚刚犯的错,是不是一下把开口张很大,就导致猎聘接口一下就限额了?当前版本纠偏了吗?」

**核实结论**:
- 19:57 的限额发生在本会话之前(v4 合入测试期),非审计会话造成;本会话 21:31 探测只是确认仍受限。
- v4 的纠偏是**止损型**(限流后抬升、连续限流熔断、6h 稀疏看门狗)——防「撞了继续撞」,但**稳态开口本身没纠偏**:
  - 默认间隔 1.3s 只比实测触发点(~1.2s 持续)宽 **8%**;
  - `on_success` 回落系数 0.92 让系统在限流恢复后快速压回 1.3s,**长时间贴着触发点跑**;
  - 任何抖动(慢响应/重试)都可能把有效速率推过触发点 → 小时级锁死。
- 即:用户直觉正确——开口确实太宽,且是设计问题而非操作问题。

**修复(v5.1.1,已合入真源)**:
1. 稳态默认间隔 1.3s → **2.0s**(67% 裕量);`LiepinClient` 默认、`--liepin-sleep`、`--sleep` 三处同步;help 注明「勿低于 1.5」
2. 回落系数 0.92 → **0.97**:限流后抬升的间隔缓慢回落,不在触发点附近振荡
3. SKILL 限流对策表 + 坑 #6 同步;实测触发点数据保留为证据
4. 代价:单家查询 ~2 变体 × 2s,25 家 ≈ 100s/轮——正确性优先,可接受

**遗留**:精确恢复窗口与稳定吞吐上限仍未测到(限流窗口未恢复,无法实网测量);恢复后建议先小批量收集观察,再考虑是否微调 2.0s。
