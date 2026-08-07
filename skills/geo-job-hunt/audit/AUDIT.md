# geo-job-hunt 生态审计报告 (v5 第 1 轮)

**审计日期**: 2026-08-01  
**范围**: `~/.agents/skills/geo-job-hunt/`(只读)、Hermes MCP/cron、草案 `~/notes/geo-job-hunt-v5-draft/`  
**执行约束**: 无真实投递;猎聘外呼仅 `tools/list` 1 次 + `probe_limit --strict-net` 1 次  

---

## 1. 执行摘要

| 维度 | 结论 |
|---|---|
| 整体健康度 | **可用**,文档与生产存在若干可纠偏项,无阻断级代码缺陷 |
| 关键纠偏 | References 缺失、profile 数量错误、amap timeout 漂移、v3 路径残留 |
| v5 草案 | 已写入 `~/notes/geo-job-hunt-v5-draft/`(SKILL 5.0.0 + README + scripts + 本报告) |
| 猎聘限流 | **仍在限流窗口**(`probe_state.last_status=limited`,本轮探测确认) |
| 用户问题 | **skill 应有 References 小节** — 已在 v5 SKILL 交付 |

---

## 2. 生态拓扑(核实)

```
~/.agents/skills/geo-job-hunt/          ← 真源(无 git)
    ↑ symlink
    ├── ~/.hermes/skills/geo-job-hunt
    └── ~/.hermes/profiles/writing/skills/productivity/geo-job-hunt

MCP config: ~/.hermes/config.yaml + profiles/{writing,lyric,trading}/config.yaml
Cron: ~/.hermes/profiles/writing/cron/jobs.json → liepin-limit-probe (id bdda26d1deee)
Cron 脚本实体副本: ~/.hermes/profiles/writing/scripts/{probe_limit,liepin_common}.py
```

| 检查项 | 结果 | 证据级别 |
|---|---|---|
| symlink 双挂载 | 均指向真源 | 高 |
| cron 副本哈希 | 与真源 `md5` 一致(2026-08-01 19:57 同步) | 高 |
| cron 未运行过 | `last_run_at=null`, `next_run_at=2026-08-02T01:49:53+08` | 高 |
| profile 目录 | 仅 `writing` / `lyric` / `trading` | 高 |
| 「default」profile | **不存在** | 高 |

---

## 3. 发现清单(按严重度)

### 3.1 阻断 (0)

无。

### 3.2 重要

| ID | 发现 | 证据 | 处理决定 |
|---|---|---|---|
| I1 | SKILL 缺独立 **References** 小节 | 用户原话 + 全文检索 | **v5 新增**,URL 已验证 |
| I2 | SKILL 写「default / writing / lyric / trading」四 profile | `ls ~/.hermes/profiles/` 仅 3 个 | **v5 纠偏**为 writing/lyric/trading + 根 config |
| I3 | 推荐 `amap.timeout:120`,生产四处均缺 | 逐文件 read config | **config-diff.md**,不自动应用 |
| I4 | cron 脚本靠手动 `cp`,漂移风险 | Hermes 拒绝 symlink + jobs.json | **v5 文档化**同步协议 + md5sum |
| I5 | `apply` 成功响应 **OK_UNVERIFIED** | 无实测样本;tools/list 无 outputSchema | **保持诚实标记**;禁止编造契约 |
| I6 | 真源无版本管理 | `~/.agents/skills/` 非 git | **建议** git init + ignore logs(未执行) |

### 3.3 建议

| ID | 发现 | 证据 | 处理决定 |
|---|---|---|---|
| S1 | SKILL cron 示例引用 `geo-job-hunt-v3/scripts/` | SKILL.md L206 | **v5 删除**,建议归档 v3 notes |
| S2 | CLI 命名不一致(`--liepin-sleep` vs `--sleep` 等) | 各脚本 `--help` | **文档说明**,不改 CLI |
| S3 | `salaryFloor`/`salaryCap` schema 为 string;单位未写明 | tools/list 2026-08-01 | **v5 文档** + 脚本 `str()` 转换 |
| S4 | `search-jobs` schema 无 `page`;代码传 `page:0` | tools/list | **文档注明**;优先 `user-search-job` 翻页 |
| S5 | `apply_job` 与 `call()` 重复实现 | 代码阅读 | **v5 不改**,待有成功样本后 refactor |
| S6 | `probe_limit` 与 `LiepinClient` 限流逻辑部分重复 | 代码阅读 | **接受**(probe 需静默语义,不宜强耦合) |
| S7 | `flatten_job_keys` 的 `gone` 易被误解为公司消失 | 代码逻辑 | **v5 文档**说明=岗位 uid 消失 |
| S8 | `maybe_telegram` 用 `http_json` 未校验 `ok:true` | 代码阅读 | **暂不修**(失败会打 stderr);低风险 |
| S9 | `DEFAULT_EXTRA_KEYWORDS` 含杭州区域公司名 | geo_job_hunt.py L37-40 | **保留**(点名补搜设计);用户可用 `--no-default-extra` |
| S10 | README 只写一处 symlink | 对比生产 | **v5 README** 补第二处 |

### 3.4 可选

| ID | 发现 | 处理 |
|---|---|---|
| O1 | npm 包页 curl 403 | References 标证据级别**中**,包名来自官方 MCP 配置 |
| O2 | `/mcp/auth` 与 `/mcp/server` 同页标题 | References 注明可能同 SPA |
| O3 | `jobKind` 枚举值 | **未能证实**;投递需从 hunt 结果字段带入 |

---

## 4. 对用户问题的明确回答

### Q: skill 里应该有 References 吗?类似 `https://www.liepin.com/mcp/auth#config`?

**答:应该有。** v5 `SKILL.md` 已新增 **「参考资料 (References)」** 小节,包含:

| URL | 用途 | HTTP | 证据 |
|---|---|---|---|
| https://www.liepin.com/mcp/auth#config | 授权/token/CLI 配置入口 | 200 | 高 |
| https://www.liepin.com/mcp/auth | 同上 | 200 | 高 |
| https://www.liepin.com/mcp/server | FAQ、能力、限流说明 | 200 | 高 |
| https://open-agent.liepin.com/mcp/user | MCP JSON-RPC 端点 | POST 200 | 高 |
| https://github.com/liepin-tech-2026/liepin-job-mcp | 官方仓库 | 200 | 高 |
| https://lbs.amap.com/api/webservice/guide/api/search | 高德周边搜 | 200 | 高 |
| https://lbs.amap.com/api/webservice/guide/api/georegeo | 高德 geocode | 200 | 高 |

`/mcp/auth` 与 `/mcp/server` 页面 title 均为「授权配置 — 猎聘 CLI」(**中**):可能为同一前端不同路由;授权与 FAQ 均可从此生态获取。

---

## 5. tools/list 复验 (2026-08-01)

**命令**:
```bash
curl -s -X POST https://open-agent.liepin.com/mcp/user \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

**结果**: 14 工具,与 SKILL v4 表格 **完全一致**。  
**与 v4 文档差异(新发现)**:
- `salaryFloor`/`salaryCap`: **string** 类型(非 int)
- `salaryKind`: 描述明确「月薪」或「年薪」
- `user-apply-job`: 仅 `jobId`+`jobKind`,required;**无 outputSchema**
- `search-jobs`: **无** `page` 字段;`user-search-job` 有 `page`(从 0)

证据级别: **高**

---

## 6. 限流状态

| 项 | 值 |
|---|---|
| 真源 state | `~/.agents/skills/geo-job-hunt/logs/probe_state.json` → `limited` @ 2026-08-01T19:57:57 |
| 本轮 `probe_limit --strict-net` | 静默 exit 0,state 更新为 `limited` @ 20:59:29 |
| 解读 | 符合预期;**禁止**爆发式实网调用 |

---

## 7. cron 副本漂移 — 方案评估

| 方案 | 优点 | 缺点 | 推荐 |
|---|---|---|---|
| 保持 `cp` + 文档 | 简单,符合 Hermes 限制 | 人为遗忘 | **当前推荐** + md5sum |
| wrapper `exec` 真源 | 单点维护 | Hermes 可能仍拒绝 | 待 Hermes 行为确认 |
| 启动时哈希校验 | 可自动报警 | 需额外脚本/cron | 可选增强 |
| symlink | 无漂移 | **已被 Hermes 拒绝** | 不可用 |

---

## 8. 验证记录

工作目录: `~/notes/geo-job-hunt-v5-draft/`

### 8.1 py_compile

```bash
python3 -m py_compile scripts/*.py
# 输出: (无错误)
```

### 8.2 --help 冒烟

```bash
python3 scripts/geo_job_hunt.py --help      # → forward/reverse 子命令
python3 scripts/apply_batch.py --help       # → --hunt --dry-run 等
python3 scripts/probe_limit.py --help       # → --state --strict-net
python3 scripts/apply_tracker.py --help     # → add/list/due/set/export/import-json
```

### 8.3 apply_batch --dry-run (合成数据)

```bash
python3 scripts/apply_batch.py \
  --hunt /tmp/geo-v5-verify/synthetic_hunt.json \
  --max 5 --dry-run --out /tmp/geo-v5-verify/apply_dry.json
```

**摘要**: 去重 3 岗,缺 jobKind 1,过滤后可投 2;`dry_run.count=2`。

### 8.4 apply_tracker CRUD (临时文件)

```bash
TRACKER=/tmp/geo-v5-verify/apply-list.json
python3 scripts/apply_tracker.py add --file $TRACKER --company 测试公司 --job 产品实习 ...
python3 scripts/apply_tracker.py import-json --file $TRACKER --input synthetic_hunt.json
python3 scripts/apply_tracker.py set --file $TRACKER --id <id> --status applied
python3 scripts/apply_tracker.py due --file $TRACKER        # → (无到期检查项)
python3 scripts/apply_tracker.py export --file $TRACKER --format md --out tracker.md
```

**摘要**: add/import/set/export 均正常;`applied` 自动写 `next_check=+3天`。

### 8.5 probe_limit --strict-net

```bash
python3 scripts/probe_limit.py --strict-net --state /tmp/geo-v5-verify/probe_state.json
# exit 0, 无 stdout(仍限流)
```

### 8.6 未执行(约束内)

- `geo_job_hunt.py forward/reverse` 实网
- `apply_batch` 真实投递
- 高德 REST 实调(本轮未必要;逻辑与 v4 相同)

---

## 9. v3 历史草稿建议

路径: `~/notes/geo-job-hunt-v3/`  
**建议**: v5 合入真源后,将 v3 移至 `~/notes/.archive/geo-job-hunt-v3/` 或加 README 标明「已废弃」;**不要**再从 v3 scripts 路径 cp 到 cron。

---

## 10. 合入清单(人工)

验收通过后:

1. `cp -a ~/notes/geo-job-hunt-v5-draft/* ~/.agents/skills/geo-job-hunt/`(或逐文件)
2. 按 `config-diff.md` 手动补 `amap.timeout:120`(四处)
3. 同步 cron 副本 + `md5sum` 校验
4. `/reload-mcp` + `/new`
5. 可选:`git init` 于 `~/.agents/skills/geo-job-hunt/`

---

## 11. 证据级别图例

- **高**: 本机命令输出、配置文件直读、官方 endpoint 实调
- **中**: 页面标题/机器人限制/推断性结论
- **未能证实**: schema 未写明或缺少实测样本

---

*报告生成: geo-job-hunt v5 审计第 1 轮 · 草案目录 `~/notes/geo-job-hunt-v5-draft/`*
