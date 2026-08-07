# 任务:geo-job-hunt skill 生态全方位审计/纠偏/延展/优化(v5)(第 1 轮)

## 任务目标

- 对 `~/.agents/skills/geo-job-hunt/` 全部内容(SKILL.md v4.0.0 / README.md / scripts/ 下 5 个脚本)及其生态(Hermes MCP 配置、cron job)做**全方位 audit、纠偏、延展、优化**。
- 产出 **v5 草案**:SKILL.md / README.md / scripts/(如需修改)+ 结构化报告 `AUDIT.md`,全部写入 **`~/notes/geo-job-hunt-v5-draft/`**(该目录已建好)。
- 报告与产出物一律**中文**。关键论断标注证据级别(高/中/未能证实)。
- **不要**修改生产真源(`~/.agents/skills/geo-job-hunt/`)、不要改任何 `config.yaml` / `.env` / cron 配置、不要 git commit。草案验收后再由人合入。

## 用户原话(逐字引用,任务语义锚点,勿转述)

> "~/.agents/skills/geo-job-hunt/ ├── SKILL.md v4.0.0(去个人化,含 README 指引) ├── README.md 另一台机器安装步骤 └── scripts/ liepin_common / geo_job_hunt / apply_batch / probe_limit / apply_tracker " 有关该 skill 的所有内容,包括但不限于 skill 本体、相应的 MCP 和 cron job 等,全部作为本次 workspace 或 context,Delegate Cursor agent,model=composer 2.5,全方位的audit、纠偏、延展和优化一遍。 另外我想问的就是类似,"https://www.liepin.com/mcp/auth#config",这种references部分在skill里应该存在吧?"

她的问题要点:skill 里应该有一个 **References / 参考资料** 小节,收录外部权威链接(如猎聘 MCP 授权/配置页、GitHub 仓库、高德 API 文档等)。这是本轮**必需交付项**之一。

## 现有资产(先读这些)

| 资产 | 路径 |
|---|---|
| SKILL.md v4.0.0(真源) | `/home/ubuntu/.agents/skills/geo-job-hunt/SKILL.md` |
| README.md(安装指引) | `/home/ubuntu/.agents/skills/geo-job-hunt/README.md` |
| liepin_common.py(公共库) | `/home/ubuntu/.agents/skills/geo-job-hunt/scripts/liepin_common.py` |
| geo_job_hunt.py(主程序,841 行) | `/home/ubuntu/.agents/skills/geo-job-hunt/scripts/geo_job_hunt.py` |
| apply_batch.py(批量投递) | `/home/ubuntu/.agents/skills/geo-job-hunt/scripts/apply_batch.py` |
| probe_limit.py(限流看门狗) | `/home/ubuntu/.agents/skills/geo-job-hunt/scripts/probe_limit.py` |
| apply_tracker.py(投递清单) | `/home/ubuntu/.agents/skills/geo-job-hunt/scripts/apply_tracker.py` |
| 限流状态文件 | `/home/ubuntu/.agents/skills/geo-job-hunt/logs/probe_state.json` |
| v3 历史草稿(对比参考) | `/home/ubuntu/notes/geo-job-hunt-v3/` |
| 公共库技能 | `/home/ubuntu/.hermes/profiles/writing/skills/autonomous-ai-agents/cursor-agent/SKILL.md`(委托纪律,可读) |

## 生态拓扑(已核实,2026-08-01)

- **真源**:`~/.agents/skills/geo-job-hunt/`(无 git 版本管理——本身是一个待审计问题)。
- **挂载(symlink)**:`~/.hermes/skills/geo-job-hunt → 真源`;`~/.hermes/profiles/writing/skills/productivity/geo-job-hunt → 真源`。
- **MCP(Hermes)**:writing profile `config.yaml` 589–604 行:
  - `amap`:`command: npx`,args `["-y","@amap/amap-maps-mcp-server"]`,env `AMAP_MAPS_API_KEY: ${AMAP_MAPS_API_KEY}`,`connect_timeout: 90`,`enabled: true` —— **注意:SKILL 推荐配置含 `timeout: 120`,实际 config.yaml 缺这一项**(文档与配置漂移)。
  - `liepin`:`url: https://open-agent.liepin.com/mcp/user`,header `x-user-token: ${MCP_LIEPIN_API_KEY}`,`timeout: 120`,`connect_timeout: 60`,`enabled: true`。
  - lyric / trading profile 的 config.yaml 也各有 1 处 `open-agent.liepin.com`(已 grep 核实)。**SKILL 声称配置在 "default / writing / lyric / trading" 四个 profile,实际只有 lyric / trading / writing 三个**(无 default)——文档错误,需纠偏。
- **密钥**:`~/.hermes/.env` 有 `AMAP_MAPS_API_KEY=`、`MCP_LIEPIN_API_KEY=`(不读取、不回显值);各 profile `.env` 亦可能有。脚本 env 发现顺序:环境变量 → `~/.hermes/.env` → 当前目录 .env → `~/.hermes/profiles/*/.env`(字母序,writing 通常最后覆盖)。
- **cron**:Hermes job `liepin-limit-probe`(id `bdda26d1deee`),`every 360m`,`no_agent=true`,`script=probe_limit.py` → 解析到 `~/.hermes/profiles/writing/scripts/probe_limit.py`(**实体副本**,Hermes cron 拒绝 symlink)。同目录还有 `liepin_common.py` 实体副本(2026-08-01 19:57 同步,尺寸与真源一致)。**该 cron 尚未运行过**(last_run_at=null,next=2026-08-02T01:49:53+08)。
- **当前限流状态**:`probe_state.json` → `last_status: "limited"`(2026-08-01T19:57:57)。**猎聘当前大概率仍在限流窗口,禁止爆发式实网调用**(自我续杯)。

## 技术事实(已验证,别再踩 / 别推翻)

1. 猎聘 MCP 端点:`POST https://open-agent.liepin.com/mcp/user`,JSON-RPC 2.0;鉴权 header `x-user-token`(JWT,90 天有效;401 → 到猎聘官网重拿 token)。GET 该端点返回 406(已实测),必须 POST。
2. **`tools/list` 公开无需 key**:`curl -s -X POST https://open-agent.liepin.com/mcp/user -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'`。SKILL 记录 14 个工具:搜索 2(`search-jobs`/`user-search-job`)+ 投递 1(`user-apply-job`,仅 `jobId` + `jobKind`)+ 简历读写 11(add/modify-work-exp、add/modify-edu-exp、add/modify-project-exp、modify-job-want、add-job-want、modify-self-assess、modify-resume-base-info、my-resume 等);**零消息/进度/站内信工具**。你可实调一次 `tools/list` 与 SKILL 表格 diff(本轮允许的唯一高频外呼)。
3. 限流(实测 2026-08-01):官方文档 60 次/分钟(搜索/查看/简历/投递共用);实际 ~1.2s 间隔连续调用一段时间后全部返回「请求过于频繁,请稍后再试」;恢复窗口疑似小时级(75s/5min 均仍限);高频探测疑似自我续杯 → 稀疏探测(6h)。响应特征:HTTP 200 + 业务体含限流词(主形态)/ HTTP 429 / MCP error 文本。
4. 投递语义:**服务端账号内简历**投递,客户端不传 PDF;`user-apply-job` payload 仅 `{"jobId": <number>, "jobKind": "<string>"}`。apply 的**成功响应形态从未实测**(代码标 OK_UNVERIFIED)——不要编造字段契约;可查 `tools/list` 的 inputSchema 佐证 jobKind 取值范围。
5. 高德:REST `restapi.amap.com/v3/place/around`(types=170000/050000 分页 + keywords 点名补搜)与 `/v3/geocode/geo`;GCJ-02 坐标系,距离 haversine。MCP 端 `maps_geo` 返回 `return[0].location`(不是 geocodes)。**高德 MCP 必须 npx stdio**(HTTP 端点 POST-only,SDK GET-SSE → 405/500),禁止改回 HTTP URL。
6. 猎聘 `address` 参数是**城市级**;`search-jobs` 分页 `page` 从 **0** 开始;`companyName` 需变体(去括号/去省市前缀/截短)。
7. 反馈闭环:HR 回复经**猎聘 App 消息推送 + 短信**;MCP/CLI 当前**不能**查投递进度(官方 FAQ 说后续版本支持);App 可看全部记录。投递后 24h 扫一眼 + 第 3 天强制检查(next_check 机制)。
8. Hermes cron 规则:no_agent 脚本空 stdout = 静默;脚本文件**不能是 symlink**(必须实体副本)→ 真源与副本靠人工 `cp` 同步(漂移风险,可延展:更稳的同步机制)。
9. 脚本仅 stdlib(Python 3.10+);密钥不写输出;`.env` 路径必须 expanduser(v4 修过)。

## 初审发现(供你验证、深化、纠偏;验证不了的标证据级别)

1. **References 缺失**:SKILL 只有零散内联链接(`liepin.com/mcp/server`、GitHub `liepin-tech-2026/liepin-job-mcp`),无独立参考资料小节。用户指出 `https://www.liepin.com/mcp/auth#config`(已 curl 验证 HTTP 200,`/mcp/server` 亦 200;两页关系/各自用途待你核实——可能一个授权一个配置说明)。**v5 必须加 References 小节,URL 逐个验证**。
2. **profile 数量错误**:SKILL 写 "default / writing / lyric / trading" 四 profile,实际三(lyric/trading/writing)。
3. **config 漂移**:SKILL「推荐 config 微调」含 amap `timeout: 120`,writing 实际 config 无此项。
4. **apply 成功形态 OK_UNVERIFIED**:从未实测,是诚实标记但也是能力缺口;看 `tools/list` schema 能否给出更强判定依据。
5. **真源无版本管理**:`~/.agents/skills/` 非 git 仓库,无历史/回滚。给出轻量建议(如 git init 该目录 + .gitignore 排除 logs/,或归档策略),但**不要擅自执行**。
6. **v3 历史残留**:`~/notes/geo-job-hunt-v3/` 仍在,SKILL 里合入示例仍引用 `notes/geo-job-hunt-v3/scripts/`——是否清理/更新引用,给建议。
7. **cron 副本漂移机制**:`profiles/writing/scripts/probe_limit.py` 与真源靠人工 cp。评估方案:如 wrapper 脚本 exec 真源、或启动时校验版本/哈希、或保持 cp + 文档强化——给推荐并附理由。
8. **CLI 约定不一致**:`--extra-keywords` 用逗号分隔,`--resume-keywords` 用竖线;`--liepin-sleep/--liepin-backoff` 与 apply_batch 的 `--sleep/--backoff` 命名不齐。统一还是文档说明,给建议。
9. **salaryFloor/salaryCap 单位未验证**(元?千元?);`salaryKind` 取值(月薪/年薪)未验证——查 tools/list schema。
10. 其他可查项:`apply_job` 手写 JSON body 与 `call()` 重复(可复用性);`maybe_telegram` 用 `http_json` 解析 Telegram 响应(`ok:true` 语义);`probe_limit.py` 与 `LiepinClient` 限流逻辑重复;`search_company_jobs` 在 `RATE_LIMITED` 时 break 但外层 `run_forward` 对单公司内多变体的限流处理;`flatten_job_keys` 的 `gone` 语义(公司消失 vs 岗位下架);README 安装步骤与真实挂载(symlink 到 `~/.hermes/skills/` 与 profile skills 两处)是否一致;DEFAULT_EXTRA_KEYWORDS 是否过时。

## 约束(硬性)

- **只读**:`~/.agents/skills/geo-job-hunt/`(真源)、`~/.hermes/profiles/*/config.yaml`、`~/.hermes/.env` 及 profiles `.env`(密钥值**不读取不回显**)、cron 配置、`~/.hermes/profiles/writing/scripts/`。
- **只写**:`~/notes/geo-job-hunt-v5-draft/`(已存在)。所有交付物放这里。
- **禁止真实投递**:任何 `user-apply-job` 实调都不允许(外部副作用,需用户确认)。`apply_batch` 只允许 `--dry-run` + 合成 hunt JSON。
- **禁止爆发式 API 探测**:猎聘实网调用仅限 1 次 `tools/list`(公开无 key)+ 至多 1 次 `probe_limit.py --strict-net`(间隔 ≥ 数分钟,当前大概率仍限流,限流中返回静默属预期)。高德实网调用 ≤ 2 次(如确需验证 geocode)。不要跑完整的 `geo_job_hunt.py forward/reverse` 实网流程。
- 脚本修改保持**纯 stdlib**;不新增依赖;不破坏现有 CLI 契约(参数名/默认值/退出码:401→exit 2,连续限流→exit 3)。
- 密钥内容不写入任何输出文件;报告里密钥只写变量名/路径。
- 报告中文;每个关键论断给证据级别(高/中/未能证实);发现按严重度分级(阻断/重要/建议/可选)。
- 不 git commit、不 git init、不创建新仓库。

## 交付要求

1. `AUDIT.md`:审计报告——发现清单(含证据级别与严重度)、每个问题的处理决定(修正/延展/不做+理由)、对用户问题的明确回答(References 小节是否应有、应含哪些链接、各 URL 的验证结果与用途说明)。
2. v5 草案文件:仅当确有改进时才提供改后的 `SKILL.md`(版本号升 **5.0.0**)/`README.md`/`scripts/*.py`;若无修改必要则写明「保持 v4 原样 + 理由」。草案须含 **References / 参考资料** 小节(猎聘授权/配置页、GitHub 仓库、高德 API 文档、native-mcp 等,URL 逐个验证并标注)。
3. `CHANGES-v5.md`:v4 → v5 变更清单(每项:改了什么/为什么/风险)。
4. 验证记录:所有脚本 `python3 -m py_compile` 通过;`--help` 冒烟;`apply_batch --dry-run` 用合成数据跑通;`apply_tracker` 用临时清单文件跑增删改查。把验证命令与输出摘要写进 AUDIT.md。
5. 若发现 config.yaml 需要微调(如 amap timeout),写成 `config-diff.md` 补丁建议,**不要应用**。

## Suggested skills

- `native-mcp`(MCP 规范参考)
- 本目录为 skill 生态,注意 Hermes skill 格式(frontmatter: name/description/version/metadata.hermes.tags)
