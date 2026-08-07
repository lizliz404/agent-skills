# v4.0.0 → v5.0.0 变更清单

## SKILL.md

| 变更 | 原因 | 风险 |
|---|---|---|
| 版本号 5.0.0;新增 **参考资料 (References)** 小节 | 用户明确要求;URL 逐个验证并标注用途 | 低 |
| 纠正 profile 表述:`default/writing/lyric/trading` → **writing/lyric/trading** + 根 `~/.hermes/config.yaml` | 无 `default` profile 目录(已 `ls` 核实) | 低 |
| 删除 cron 示例中对 `notes/geo-job-hunt-v3/scripts/` 的引用 | v3 为历史草稿,易误导合入路径 | 低 |
| 新增 cron 脚本同步协议(`cp` + `md5sum`) | Hermes 拒绝 symlink,副本漂移风险 | 低(文档) |
| 新增 CLI 参数分隔符/命名对照表 | `--extra-keywords` 逗号 vs `--resume-keywords` 竖线;`liepin-*` vs `sleep/backoff` | 低(文档) |
| 补充 `tools/list` 薪资 schema:salaryFloor/Cap 为 string;salaryKind 为月薪/年薪 | 本轮 `tools/list` 实调 | 低 |
| 补充 `search-jobs` vs `user-search-job` 翻页说明 | schema 仅后者显式含 `page` | 低 |
| 补充 `gone` diff 语义、真源 git 建议、v3 归档建议 | 初审发现项 | 低 |
| 指向 `config-diff.md` | amap `timeout` 生产漂移 | 低 |

## README.md

| 变更 | 原因 | 风险 |
|---|---|---|
| 补充 **第二处** Hermes symlink(`profiles/writing/skills/productivity/...`) | 生产实际双挂载,原 README 只写一处 | 低 |
| 三 profile + 根 config 说明 | 与 SKILL 纠偏一致 | 低 |
| 授权链到 `mcp/auth#config` | References 对齐 | 低 |
| cron 同步增加 `liepin_common.py` + `md5sum` 校验 | 与 SKILL 同步协议一致 | 低 |

## scripts/

| 文件 | 变更 | 原因 | 风险 |
|---|---|---|---|
| `geo_job_hunt.py` | `salaryFloor`/`salaryCap` 传 API 前 `str()`;版本字符串 v5 | 对齐 tools/list schema | 低 |
| `apply_tracker.py` | 文档/描述 v3→v5 | 版本漂移 | 无 |
| `apply_batch.py` | 文档 v5 | 版本漂移 | 无 |
| `liepin_common.py` | 文档 v5 | 版本漂移 | 无 |
| `probe_limit.py` | 文档 v5 | 版本漂移 | 无 |
| `liepin_common.apply_job` | **未改**(仍手写 JSON,未复用 `call()`) | 避免行为回归;留待有成功样本后再 refactor | — |

## 新增文件

| 文件 | 说明 |
|---|---|
| `AUDIT.md` | 结构化审计报告 |
| `CHANGES-v5.md` | 本文件 |
| `config-diff.md` | amap timeout 补丁建议(未应用) |

## 未做(有意)

- 未修改生产真源 `~/.agents/skills/geo-job-hunt/`
- 未改 `config.yaml` / `.env` / cron
- 未 `git init` / commit
- 未实调 `user-apply-job`
- 未统一 `--liepin-sleep` 与 `--sleep` 命名(破坏 CLI 契约)
