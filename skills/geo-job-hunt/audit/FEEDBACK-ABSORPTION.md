# geo-job-hunt 反馈吸收报告 (Round 2)

**日期**: 2026-08-01  
**基线**: 生产真源 `~/.agents/skills/geo-job-hunt/` **v5.1.2** (git `c790389`)  
**输入**: `reviews/feedback-1-review-2026-08-01.md`、`reviews/feedback-2-critique-2026-08-01.md`  
**约束**: 只读生产;只写 `~/notes/geo-job-hunt-v5-draft/`;无实网投递;猎聘外呼 1 次 `tools/list`  

---

## 1. 本轮结论(一行版)

**feedback 中可执行的工程项均已落地(v5.1.0–v5.1.2);唯一真瓶颈仍是限流未恢复 + 零次真实投递 → 本轮仅做文档漂移纠偏 + 首投操作指引,不做 v6 式审计。**

---

## 2. Feedback 1 逐条对账

| # | 论点/建议 | 属实性 | 当前状态(v5.1.2) | 增量价值 | 本轮动作 |
|---|---|---|---|---|---|
| F1-0 | 审计两轮,真实投递=0;OK_UNVERIFIED 是数据空白非文档问题 | **高** | 仍成立;`probe_state` 自 19:57 limited,21:31 仍 limited | 无(需人投) | **无代码动作**;见 `patch-round2/FIRST-APPLY.md` |
| F1-1 | v5 审计质量可,py_compile/发现可追溯 | **高** | round 1 结论仍有效 | 无 | **已处理**,不重审 |
| F1-2.1 | `amap.timeout:120` 两轮未应用 → 应幂等脚本 | **高**(写时属实) | **已处理**: `ensure_amap_timeout.py` + 四处 config 已含 timeout;dry-run 四轮「幂等跳过」 | 无 | **验证落地质量** ✓ |
| F1-2.2 | 真源无 git → 应立即 init | **高**(写时属实) | **已处理**: `git init` 基线 `3f96094`,后续 v5.1.1/v5.1.2 有 commit | 无 | **验证** ✓ |
| F1-2.3 | `--require-kind` 死开关 | **高** | **已处理**: 仅留 `--allow-empty-kind`;`--help` 无 require-kind | 无 | **验证** ✓ |
| F1-3 | 前三条是还债,第四条需真实投递,不构成 v6 理由 | **高** | 三条已还;第四条仍阻塞 | 中(操作指引) | `FIRST-APPLY.md` |
| F1-4 | 下一步: `--max 1` 真实投递解锁契约 | **高** | 限流中禁止执行 | 高(限流恢复后) | 操作指引,非本轮执行 |
| F1-5 | 受众是 Liz/Hermes,不需破圈重排 | **高** | SKILL/README 信息密度合理 | 无 | **维持现状** |

### Feedback 1 三件执行事项 — 落地质量验证

| 事项 | 验证命令/证据 | 结果 | 证据级别 |
|---|---|---|---|
| ensure_amap_timeout | `python3 scripts/ensure_amap_timeout.py` | 4/4「已含 timeout(幂等跳过)」 | 高 |
| git 基线 | `git log --oneline` | `3f96094`→`fab47ae`→`1437321`→`c790389` | 高 |
| --require-kind 移除 | `apply_batch.py --help` | 仅 `--allow-empty-kind` | 高 |
| cron 副本同步 | `md5sum` probe_limit 真源 vs writing 副本 | 哈希一致 `d605b132…` | 高 |

---

## 3. Feedback 2 逐条对账

| # | 批判点 | 属实性 | 当前状态 | 增量价值 | 本轮动作 |
|---|---|---|---|---|---|
| F2-1 | 投递成功形态无实测,OK_UNVERIFIED 是最大不确定性 | **高** | 仍成立;`tools/list` 无 outputSchema | **无审计价值**;需 1 次真实 apply | **维持现状** + 首投指引 |
| F2-2 | 限流参数缺测试数据/日志;1.3s/90s/6h「基于实测」证据薄 | **中–高** | **部分已处理**: 默认间隔 **2.0s**(v5.1.1);回落 **0.97**;附录「实测证据与参数依据」(v5.1.2)含证据级别+诚实缺口+`probe_state` 时间戳链 | 低(附录已够诚实) | **维持现状**;附录充分性见 §4 |
| F2-3 | API schema 演进风险(jobKind 枚举、salary string) | **高** | **已文档化**: SKILL tools/list 表 + salary `str()` 转换 | 低 | **维持现状**;限流恢复后可用 `tools/list` 季度复验 |
| F2-4 | Hermes 耦合(symlink+cron 实体副本) | **高** | README 双 symlink + cp/md5sum 协议已写 | 低 | **维持现状**;wrapper 脚本 ROI 不足 |
| F2-5 | 历史负担:DEFAULT_EXTRA_KEYWORDS、v3 目录 | **中** | v3 **引用已清**;物理目录 `~/notes/geo-job-hunt-v3/` 仍在;`--no-default-extra` 可禁用默认清单 | 低 | **维持现状**;v3 归档由用户决定 |

### F2-2 附录充分性评估

v5.1.2 附录已覆盖 feedback-2 第 2 条的核心 nugget:

| 要求 | 附录是否覆盖 | 证据级别 |
|---|---|---|
| 参数→依据表 | ✓ 9 行参数表 | 高 |
| 诚实缺口(无原始命令日志) | ✓ 首段明示 | 高 |
| 2.0s 非独立实验而是推算 | ✓「中(推算)」 | 高 |
| 时间戳链 | ✓ 19:57→20:59→21:31 | 高 |

**结论**: 在「限流未恢复、无法补新实验」前提下,附录**充分**;补强原始日志需等限流恢复后刻意留痕,属运行时行为而非文档轮次。

### F2-2「1.3s」旧值

feedback 原文引用 1.3s — **已过时**。生产默认:`liepin_common.LiepinClient.sleep=2.0`,`geo_job_hunt --liepin-sleep`/`apply_batch --sleep` 默认 2.0。SKILL 仍提及 1.3s 仅作**历史对比**(为何提到 2.0s),非当前默认值 — **合理,无需删改**。

---

## 4. 本轮发现的文档漂移(有增量价值)

| ID | 问题 | 严重度 | 证据 | 草案 |
|---|---|---|---|---|
| D1 | SKILL 推荐 yaml 示例注释仍写「生产四处 config **均缺**此项」(L53),与 L42「均已应用」矛盾 | 建议 | read SKILL.md | `patch-round2/SKILL.md` 单行注释 |
| D2 | README yaml 注释「生产**可能**缺此项」 | 建议 | read README.md | `patch-round2/README.md` |
| D3 | `config-diff.md` 正文仍写「均缺少」,与头部「已应用」矛盾 | 建议 | read config-diff.md | `patch-round2/config-diff.md` |

**无代码/CLI 变更**;不涉及限流参数或 apply 逻辑。

---

## 5. 本轮增量动作清单

| 动作 | 位置 | 理由 |
|---|---|---|
| ✅ 撰写本对账报告 | `FEEDBACK-ABSORPTION.md` | 任务交付 |
| ✅ 文档漂移纠偏草案 | `patch-round2/` | D1–D3,3 分钟可合入 |
| ✅ 首投操作指引 | `patch-round2/FIRST-APPLY.md` | 响应 F1-4,非审计 |
| ❌ 新 AUDIT.md / v6 skill | — | feedback 明确禁止 |
| ❌ apply_job 合并 call() | — | 无成功响应样本 |
| ❌ sync_cron wrapper 脚本 | — | README 协议足够 |
| ❌ 改 DEFAULT_EXTRA_KEYWORDS | — | 设计特性,有 `--no-default-extra` |

---

## 6. 明确「无新动作,维持现状」项及理由

| 项 | 理由 |
|---|---|
| OK_UNVERIFIED / jobKind 枚举 | 数据空白;审计生不出契约 |
| 限流参数再调优 | 窗口未恢复,无法实验;2.0s+附录已诚实 |
| Hermes 解耦 | 目标用户即 Hermes;成本>收益 |
| v3 物理目录删除 | 用户资产,非 agent 擅自删除 |
| tools/list 以外猎聘调用 | 仍 limited,禁止自我续杯 |
| 生产真源直接修改 | 约束:仅 patch-round2 草案 |

---

## 7. 验证记录 (2026-08-01 round 2)

工作目录: `/home/ubuntu/.agents/skills/geo-job-hunt/`(只读执行)

### 7.1 py_compile

```bash
python3 -m py_compile scripts/*.py
# exit 0
```

### 7.2 --help 冒烟

```bash
python3 scripts/geo_job_hunt.py --help      # forward/reverse
python3 scripts/apply_batch.py --help       # --allow-empty-kind, 无 --require-kind
python3 scripts/probe_limit.py --help
python3 scripts/apply_tracker.py --help
python3 scripts/ensure_amap_timeout.py --help
```

### 7.3 ensure_amap_timeout dry-run

```
已含 timeout(幂等跳过): ~/.hermes/config.yaml
已含 timeout(幂等跳过): ~/.hermes/profiles/writing/config.yaml
已含 timeout(幂等跳过): ~/.hermes/profiles/lyric/config.yaml
已含 timeout(幂等跳过): ~/.hermes/profiles/trading/config.yaml
4 个文件检查完毕;dry-run,未写入(变更 0 处)
```

### 7.4 apply_batch --dry-run (合成)

```bash
python3 scripts/apply_batch.py --hunt synthetic.json --max 1 --dry-run
# hunt 去重岗位 1 个 → 过滤后可投 1 个 → dry-run OK
```

### 7.5 apply_tracker

```bash
python3 scripts/apply_tracker.py add/list  # 正常
```

### 7.6 tools/list (公开,无 key)

```bash
curl -s -X POST https://open-agent.liepin.com/mcp/user ... -d '{"method":"tools/list"}'
# HTTP 200, 14 工具, 与 v5.1.2 表格一致
```

### 7.7 限流状态(未探测)

读取 `logs/probe_state.json`: `last_status=limited`, `last_limited_at=2026-08-01T21:31:18` — **未再跑 probe_limit**,避免续杯。

### 7.8 未执行

- `forward`/`reverse` 实网
- `user-apply-job` 真实投递
- `probe_limit --strict-net`

---

## 8. 合入建议(人工,验收 patch-round2 后)

```bash
# 文档漂移(可选,3 处注释)
cp patch-round2/SKILL.md ~/.agents/skills/geo-job-hunt/SKILL.md   # 或只 cherry-pick 注释行
cp patch-round2/README.md ...
cp patch-round2/config-diff.md ~/notes/geo-job-hunt-v5-draft/

# 首投指引(可放 notes 或 skill 旁)
cp patch-round2/FIRST-APPLY.md ~/notes/geo-job-hunt-v5-draft/

# 限流恢复后 — 见 FIRST-APPLY.md
```

---

*Round 2 · 反馈吸收 · 非全量审计*
