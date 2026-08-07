---
name: geo-job-hunt
description: "Jobs near a place: Amap radius + Liepin hiring (fwd/rev/apply)."
version: 5.1.3
author: Liz + Hermes
license: MIT
metadata:
  hermes:
    tags: [jobs, internships, amap, liepin, mcp, geolocation, job-hunt, watch, apply]
    related_skills: [native-mcp]
---

# 地理围栏找工作 v5 (Geo Job Hunt)
> v5.1.3:注释纠偏(yaml 示例「均缺」→「已应用」);v5.1.2:实测证据附录;v5.1.1:稳态间隔 2.0s;v5.1.0:死开关移除 + ensure_amap_timeout.py + git 基线。

## 场景与痛点

旧时代:打开一个封装严重、数据封闭的孤岛招聘平台 → 人工筛选 → 不会用筛选栏就一页页划 → 变成刷短视频。

本 skill:**精确坐标 → 圈定半径内公司 → 查在招**(正向),或 **搜岗位 → 验证公司是否在半径内**(反向),一张表交付。支持增量监控、HTML/JSON、Telegram 推送、投递清单、批量投递、限流看门狗。

**不需要**把简历 PDF 交给 Agent:注册猎聘时填好的账号档案就是投递数据源(见「投递与数据流」)。

## 前置条件(已配好,别重复配置)

两个 MCP 已配置到 Hermes 的 **`writing` / `lyric` / `trading`** 三个 profile 的 `config.yaml → mcp_servers`,以及根配置 `~/.hermes/config.yaml`(无名为 `default` 的 profile 目录)。

| server | transport | 说明 | 建议 |
|---|---|---|---|
| `amap` | npx stdio `@amap/amap-maps-mcp-server` | 地理编码/周边/路径/天气 | **禁止**改回 HTTP URL(`mcp.amap.com` POST-only,SDK GET-SSE → 405/500) |
| `liepin` | HTTP `https://open-agent.liepin.com/mcp/user` | 搜职位/投递/简历,header `x-user-token` | `tools/list` **公开**——connect 绿灯≠鉴权成功,必须实调 `search-jobs` |

密钥(只引用路径,勿回显):`AMAP_MAPS_API_KEY`、`MCP_LIEPIN_API_KEY`。脚本自动发现顺序:环境变量 → `~/.hermes/.env` → 当前目录 `.env` → 各 profile `.env`(字母序,`writing` 通常最后覆盖;可用 `--env` 显式指定)。

- 猎聘 token **90 天**有效;401 → [猎聘 MCP 授权页](https://www.liepin.com/mcp/auth#config)重拿(见 References)
- 猎聘限流:官方文档 **60 次/分钟**(搜索/查看/简历/投递共用);**实测更狠**,见下「限流与配额」
- 改 config/env 后:`/reload-mcp` + `/new`,或重启 gateway
- Node ≥ 22(高德 npx server 要求)

### 推荐 config 微调(已脚本化)

> amap 块补 `timeout: 120` 已幂等脚本化:`scripts/ensure_amap_timeout.py`(默认 dry-run 打印状态,`--yes` 落盘;已含 timeout 则跳过)。生产 4 处 config.yaml 均已应用(v5 合入时)。

审计记录:详见 `~/notes/geo-job-hunt-v5-draft/config-diff.md`(已应用,保留作审计记录)。

```yaml
amap:
  command: npx
  args: ["-y", "@amap/amap-maps-mcp-server"]
  env:
    AMAP_MAPS_API_KEY: ${AMAP_MAPS_API_KEY}
  connect_timeout: 90
  timeout: 120          # 已应用;新环境用 scripts/ensure_amap_timeout.py 核验
  enabled: true
liepin:
  url: https://open-agent.liepin.com/mcp/user
  headers:
    x-user-token: ${MCP_LIEPIN_API_KEY}
  timeout: 120
  connect_timeout: 60
  enabled: true
```

## 限流与配额(实测 2026-08-01)

| 项 | 数值 | 来源 |
|---|---|---|
| 官方文档 | 60 次/分钟(搜索/查看/简历更新/投递共用) | liepin.com/mcp/server |
| 实测爆发行为 | ~1.2s 间隔连续调用一段时间后,全部返回「请求过于频繁,请稍后再试」 | 本机实测 |
| 恢复窗口 | 停止调用后 ≥5 分钟未恢复(75s / 5min 均仍限);精确恢复点未测到,疑似小时级 | 本机实测 |
| 高频探测副作用 | 每 4 分钟探测一次会持续触发,疑似**自我续杯** → 必须稀疏探测 | 本机实测 |

**限流响应特征**(须全部识别):
1. HTTP **200** + 业务体含「请求过于频繁」(主形态)
2. HTTP **429**(脚本已识别;是否会出现待观察)
3. MCP `error` 文本含限流词

对策(v4,止损型):
1. 基础间隔 **≥2.0s**(v5.1.1:实测触发 ~1.2s 持续,1.3s 仅 8% 裕量 → 提至 2.0s,67% 裕量;`--liepin-sleep`/`--sleep` 可调,勿低于 1.5);**自适应**:限流则升高间隔 + 退避重试一次(默认退避 **90–120s**,因实测 60s 常不够),成功后**缓慢回落**(×0.97)至地板,**不向触发点加速**
2. **连续限流 ≥2 次 → 停手**(exit 3),不要硬冲
3. `scripts/probe_limit.py` 静默看门狗 + **state 文件**:仍限流→无 stdout;恢复→打印并附「距上次限流多久」。网络错误默认静默累计,连续失败才警告(避免假阴性「永远当限流」与假阳性「当恢复」两端)
4. Hermes cron:`liepin-limit-probe` every 6h / no_agent / 实体副本 `profiles/writing/scripts/probe_limit.py`(**改真源后必须同步副本**)
5. 收集与投递共用配额:收集完别立刻满速投

### 实测证据与参数依据(附录 v5.1.2)

参数来源与证据链。诚实标注:原始命令级探测日志**未归档**(散在 v3/v4 开发会话,仓库内仅有结论);精确恢复窗口与稳态吞吐上限**未测到**(限流窗口未恢复,无法实验)。

| 参数 | 数值 | 依据(何时测得) | 证据级别 |
|---|---|---|---|
| 官方限流 | 60 次/分钟,搜索/查看/简历/投递共用 | liepin.com/mcp/server FAQ(2026-08-01 抓取) | 高 |
| 实测触发点 | ~1.2s 间隔持续调用一段时间后全部限流 | 2026-08-01 实测(v4 开发期) | 中(单次实验,无命令日志) |
| 恢复窗口 | 停止后 75s / 5min 均仍限;疑似小时级 | 同上 + probe_state.json 时间戳链 | 中 |
| 高频探测副作用 | 每 4 分钟探测一次会**自我续杯** | 2026-08-01 实测(v4 开发期) | 中 |
| 稳态间隔 **2.0s** | 触发点 ~1.2s + 67% 裕量 | v5.1.1 决策,**由触发点推算**,非独立实验 | 中(推算) |
| 退避 90–120s | 60s 常不够 | 2026-08-01 实测 | 中 |
| 探测间隔 6h | 4 分钟续杯 → 稀疏化 | 同上 | 中 |

**探测时间戳链(本会话独立复核)**:`probe_state.json` — 2026-08-01 19:57:57 limited(v4 合入测试期)→ 20:59:29 探测仍 limited → 21:31:18 探测仍 limited。限流自 19:57 起持续 ≥1.5h,支持「小时级窗口」判断。

### 猎聘工具清单(14)·实测 `tools/list` 2026-08-01(本轮复验一致)

| 类别 | 工具 | 用途 |
|---|---|---|
| 搜索 | `search-jobs` · `user-search-job` | 按条件列岗位;**翻页用 `user-search-job` 的 `page`(从 0)**;`search-jobs` schema 未列 `page` 但代码仍传 `page:0` |
| 投递 | `user-apply-job` | **仅** `jobId`(number) + `jobKind`(string,描述为「职位类型」,**枚举值未在 schema 公布**) |
| 读简历 | `my-resume` | 读账号内结构化简历 |
| 写档案 | `add/modify-work-exp` · `add/modify-edu-exp` · `add/modify-project-exp` · `modify-job-want` · `add-job-want` · `modify-self-assess` · `modify-resume-base-info` | **维护账号档案**,不是投递附件 |

**没有** message / inbox / notification / 投递进度 / 面试邀约类工具。

**薪资参数**(tools/list `inputSchema`,证据级别**高**):
- `salaryFloor` / `salaryCap`:类型 **string**(非 number);单位/schema 未写明「元/千元」——**未能证实**
- `salaryKind`:描述为 **「月薪」或「年薪」**

Agent 会话内工具名形如 `mcp_liepin_search_jobs`(连字符→下划线)。**批量圈人用本目录脚本走 REST/MCP HTTP 直调**,避免会话里连打 50 次工具烧上下文。

## 投递与数据流

用户原问要点:**要不要再给 Agent PDF?投递时数据从哪来——猎聘账号还是本地传?**

### 结论

投递走猎聘**服务端账号内简历**;CLI/Agent/本地 skill **不传** PDF、不传简历字段。

```
[你的猎聘账号]
  注册时填写 + 可选 PDF 解析 → 服务端结构化简历
        ↑ 可用 my-resume 读 / add|modify-* 改
        │
[Agent / CLI] ──x-user-token(JWT,含 userId)──► open-agent.liepin.com
        │
        └── user-apply-job { jobId: number, jobKind: string }
              服务端:用 token 锁定账号 → 取该账号现有简历 → 对准 jobId 投递
```

| 问题 | 答案 |
|---|---|
| 还要给 Agent PDF 吗? | **不必**。官网账号已识别并落库即可 |
| 本地 skill 要存基本数据吗? | **不必**作投递源;本地只需岗位清单/追踪元数据(`jobId`/`jobKind`/状态) |
| 谁传简历? | **没人从客户端传**;服务端自取账号档案 |
| `add/modify-*` 干什么? | 事先完善/修正账号档案;官方 FAQ:Agent「只会补充缺失字段、不覆盖已填」 |
| payload 长什么样? | `{"jobId": <number>, "jobKind": "<string>"}` + header `x-user-token` |
| apply 成功响应? | **OK_UNVERIFIED**——无限流/显式失败词,**不保证**平台已接受(从未实测成功样本) |

鉴权:token 绑定 userId → 所有写操作落在该猎聘账号。限流 60 次/分钟(搜索/查看/简历/投递共用)。

## 反馈闭环

投递发出后,**结果怎么回来?MCP/CLI 能不能读?**

### 官方说法(高证据)

来源:[猎聘 MCP 授权页 FAQ](https://www.liepin.com/mcp/server)(2026-08-01 抓取):

> **「Agent 投递后,HR 的回复在哪里看?」**  
> HR 回复会通过**猎聘 App 消息推送**和**短信通知**触达。  
> **后续版本将支持 Agent 查询投递进展**,但即时沟通建议回到猎聘 App 完成。

| 渠道 | 状态 | 证据级别 |
|---|---|---|
| 猎聘 App 消息推送 | **官方确认** | 高 |
| 短信通知 | **官方确认** | 高 |
| 猎聘 App 内投递/消息记录 | **官方确认** | 高 |
| 邮箱/邮件 | MCP 页/GitHub/`tools/list` **未出现** | **未能证实** |
| MCP / CLI 读进度 | **当前不能** | 高 |

### 操作闭环(现在就能用)

| 阶段 | 谁做 | 怎么做 |
|---|---|---|
| 投递 | Agent/CLI | `user-apply-job` / `liepin-cli job`;同时 `apply_tracker.py set --status applied` |
| 即时反馈 | **人** | 看手机:**猎聘 App 消息** + **短信** |
| 定期检查 | 人 + 本地清单 | `apply_tracker.py due` → 打开 App 核对 → `set --checked` 或改状态 |
| 建议节奏 | — | 投递后 **24h** 扫一眼; **第 3 天**强制检查(`next_check`) |

## CLI 参数约定(v5 文档化,未改 CLI 契约)

| 参数 | 分隔符 | 脚本 |
|---|---|---|
| `--extra-keywords` | **逗号** `,` | `geo_job_hunt.py forward` |
| `--job` / `--resume-keywords` | **竖线** `\|`(正则或关键词列表) | `geo_job_hunt.py` |
| 猎聘间隔/退避 | `--liepin-sleep` / `--liepin-backoff` | `geo_job_hunt.py` |
| 同上 | `--sleep` / `--backoff` | `apply_batch.py`(默认 backoff 120s,高于 hunt 的 90s) |

**决定**:v5 **不统一命名**(避免破坏脚本契约),仅在文档标明差异及默认值。

## 工作流

### A. 正向 `forward`(公司 → 岗位)——默认

1. **坐标**:`--location lon,lat` 或 `--address` → REST geocode。GCJ-02;距离 haversine。
2. **圈公司**:REST `place/around`,`types=170000` 与 `050000` 分别翻页 + 点名关键词补搜。先滤噪音再截断 `--max-companies`。
3. **查在招**:每家 `search-jobs`(`companyName` 变体);`address`=**城市级**;本地正则 `--job`。

### B. 反向 `reverse`(岗位 → 公司位置验证)

猎聘翻页 → 公司 geocode → haversine 过滤。`--keep-outside` 可保留半径外并标注。

### C. 增量监控

```bash
python3 scripts/geo_job_hunt.py forward \
  --address "你的圆心地址" --radius 3000 --city 杭州 \
  --job "实习|产品|AI|Agent" --max-companies 30 \
  --state-file state.json \
  --diff-only --format md --out diff.md \
  --telegram
```

**`gone` 语义**:state diff 中「消失」= 上次快照有、本次无的 `job_uid`(岗位下架或本次未搜到/限流中断导致漏采),**不等于**公司从地图消失。

### D. cron 脚本同步(Hermes 拒绝 symlink)

真源:`~/.agents/skills/geo-job-hunt/scripts/`  
cron 实体副本:`~/.hermes/profiles/writing/scripts/{probe_limit,liepin_common}.py`

**推荐协议(v5)** — 合入真源后执行:

```bash
SRC=~/.agents/skills/geo-job-hunt/scripts
DST=~/.hermes/profiles/writing/scripts
cp "$SRC/probe_limit.py" "$SRC/liepin_common.py" "$DST/"
md5sum "$SRC/probe_limit.py" "$DST/probe_limit.py"  # 应一致
```

可选增强(未实现):wrapper `exec` 真源(若 Hermes 日后允许)或 pre-cron 哈希校验脚本。**不推荐**仅靠记忆手动 cp 而不校验。

Hermes 限流探测(已配 writing profile,every 6h,no_agent,id `bdda26d1deee`):

```bash
cp ~/.agents/skills/geo-job-hunt/scripts/probe_limit.py \
   ~/.agents/skills/geo-job-hunt/scripts/liepin_common.py \
   ~/.hermes/profiles/writing/scripts/
```

### E. 投递辅助

```bash
python3 scripts/geo_job_hunt.py forward ... --format json --out /tmp/hunt.json
python3 scripts/apply_tracker.py import-json --input /tmp/hunt.json
python3 scripts/apply_batch.py --hunt /tmp/hunt.json --max 20 --dry-run   # 先试
python3 scripts/apply_batch.py --hunt /tmp/hunt.json --max 20 --tracker-file apply-list.json
python3 scripts/apply_tracker.py due
```

## 脚本

路径(真源):`~/.agents/skills/geo-job-hunt/scripts/`

| 脚本 | 作用 |
|---|---|
| `liepin_common.py` | env 发现、SSE/HTTP、限流识别、自适应 `LiepinClient` |
| `geo_job_hunt.py` | forward/reverse/增量/多格式 |
| `apply_batch.py` | hunt JSON → `user-apply-job`;成功=`OK_UNVERIFIED` |
| `apply_tracker.py` | 投递清单 + `applied_at`/`next_check`/`due` |
| `probe_limit.py` | 静默看门狗 + state 诊断 |
| `ensure_amap_timeout.py` | 幂等补齐 4 处 config.yaml 的 `amap.timeout:120`(dry-run 默认) |

依赖:**仅 stdlib**。密钥不写输出。401 → exit 2;连续限流 → exit 3。

## 坑(踩过的)

1. 高德 HTTP MCP 端点只支持 POST 流 → **必须用 npx stdio**
2. `hermes mcp add --args` 会吞后续选项 → args 放最后,或手改 config
3. 猎聘 `address` 是城市级,不是半径
4. 限流响应 HTTP 200 里藏「请求过于频繁」
5. 限流窗口疑似小时级,高频探测会自我续杯——用 6h 稀疏探测
6. apply 与 search 共用配额——收集完别立刻满速投,间隔 ≥2.0s(实测触发 ~1.2s 持续,1.3s 裕量不足)
7. **`.env` 路径必须 `expanduser`**
8. **apply 成功响应形态待实测**
9. Hermes cron **拒绝 symlink** → 必须实体副本 + 手动同步
10. v4 曾写「default profile」——**不存在**;实为 writing/lyric/trading + 根 `~/.hermes/config.yaml`
11. `salaryFloor`/`salaryCap` schema 为 **string**,CLI 传 int 时 v5 脚本已 `str()` 转换

## 真源版本管理(已执行 v5.1.0)

`~/.agents/skills/geo-job-hunt/` 已 `git init -b main`(v5.1.0),`.gitignore` 排除 `logs/`、`__pycache__/`、`*.pyc`、`*.log`。合入草稿→真源后及时 `git add -A && git commit`;任何合入可回滚。

## v3 历史草稿

`~/notes/geo-job-hunt-v3/` 可保留作 diff 参考;**不要再引用其 scripts 路径**作合入来源。验收 v5 后可归档或删除 notes 侧 v3。

## 参考资料 (References)

> 按依赖域分组;**用途列 = 什么时候查它**(排障路径:先查对应分组,再看本机 README/native-mcp)。
> 证据级别:高 = HTTP 可达且用途已核对;中 = 可达但受限/推断;未能证实 = 未验证。URL 验证日期:2026-08-01(v5.0.1 补高德 MCP 文档层)。

### 猎聘 (Liepin)——授权 / 能力 / 排障

| 链接 | 用途(何时查) | 证据 |
|---|---|---|
| [https://www.liepin.com/mcp/auth#config](https://www.liepin.com/mcp/auth#config) | **生成/续期 token**(90 天);`401` 时来这重拿;CLI 配置入口(`#config` 锚点) | 高 |
| [https://www.liepin.com/mcp/auth](https://www.liepin.com/mcp/auth) | 同上(无锚点);与 `/mcp/server` 同 SPA 不同路由(标题「授权配置 — 猎聘 CLI」) | 中(页面关系) |
| [https://www.liepin.com/mcp/server](https://www.liepin.com/mcp/server) | 官方 FAQ:能力边界、限流 60/min、token 90 天、反馈闭环口径(HR 回复走 App/短信) | 高 |
| [https://open-agent.liepin.com/mcp/user](https://open-agent.liepin.com/mcp/user) | MCP JSON-RPC 端点;**连不上/疑似断网时先验证它**:`tools/list` 公开 POST(无需 key) | 高 |
| [https://github.com/liepin-tech-2026/liepin-job-mcp](https://github.com/liepin-tech-2026/liepin-job-mcp) | 官方仓库 README;能力声明与限流说明的交叉验证源 | 高 |

### 高德 (Amap)——MCP 服务(本 skill 的 npx stdio 层)

| 链接 | 用途(何时查) | 证据 |
|---|---|---|
| [https://developer.amap.com/api/mcp-server/gettingstarted](https://developer.amap.com/api/mcp-server/gettingstarted) | 快速接入:启动方式、工具清单、MCP 配置示例 | 高 |
| [https://lbs.amap.com/api/mcp-server/create-project-and-key](https://lbs.amap.com/api/mcp-server/create-project-and-key) | **创建应用与 Key 的权威流程**(首次配置 `AMAP_MAPS_API_KEY` / key 失效时) | 高 |
| [https://lbs.amap.com/api/mcp-server/summary](https://lbs.amap.com/api/mcp-server/summary) | 服务概述:能力范围与限制 | 高 |

### 高德 (Amap)——Web 服务 REST(脚本直连层)

| 链接 | 用途(何时查) | 证据 |
|---|---|---|
| [https://lbs.amap.com/api/webservice/guide/api/search](https://lbs.amap.com/api/webservice/guide/api/search) | `place/around` 周边搜:参数(types/offset/page)、返回结构(`pois[].location`) | 高 |
| [https://lbs.amap.com/api/webservice/guide/api/georegeo](https://lbs.amap.com/api/webservice/guide/api/georegeo) | 地理/逆地理编码:`geocodes[0].location` 返回结构 | 高 |
| [https://registry.npmjs.org/@amap/amap-maps-mcp-server](https://registry.npmjs.org/@amap/amap-maps-mcp-server) | npm 包元数据(最新 0.0.8,2026-08-01 查);npmjs.com 页面 curl 403,用 registry API | 中 |

### 本机 / Hermes

| 链接 | 用途(何时查) | 证据 |
|---|---|---|
| `native-mcp` skill | Hermes MCP 规范:`config.yaml → mcp_servers` 写法、reload 流程 | 本地 |
| 同目录 `README.md` | 另一台机器完整安装步骤(依赖/密钥/MCP/cron) | 本地 |

**范围说明**:References 覆盖「外部权威源 + 本机兜底」两层,对应 skill 三大运行时依赖(猎聘授权与端点、高德 MCP 层、高德 REST 层);每条按「什么时候查」标注,遇问题先按分组定位,不必通读。对用户问题的回答:skill 应有独立 References 小节——**是**,v5 已落实,v5.0.1 强化为分组结构。

## 背景资产

- 可选:本地公司清单作为 `--extra-keywords`
- MCP 规范:`native-mcp` skill
- 另一台机器安装:见同目录 `README.md`
- v5 审计报告:`~/notes/geo-job-hunt-v5-draft/AUDIT.md`
