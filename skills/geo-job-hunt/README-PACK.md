# geo-job-hunt v5.1.3 完整包

打包日期:2026-08-01 · 生产真源版本:**v5.1.3**

## 版本线

| 版本 | 内容 |
|---|---|
| v5.0.0 | 限流模型纠偏 + 公共库去重 + probe 状态诊断 + apply 成功判定诚实化(审计轮) |
| v5.0.1 | References 重组为分组结构 + 补高德 MCP Server 官方文档层 |
| v5.1.0 | 移除 `--require-kind` 死开关 + `ensure_amap_timeout.py` 幂等补 config + 真源 git 基线 |
| v5.1.1 | 稳态间隔 1.3s→2.0s(实测触发点 ~1.2s 持续,原裕量仅 8%)+ 回落 0.92→0.97 |
| v5.1.2 | 新增「实测证据与参数依据」附录(限流参数证据链 + 诚实缺口标注) |
| **v5.1.3** | 注释纠偏(yaml 示例「均缺」→「已应用」)+ 首投指引 FIRST-APPLY.md + 反馈吸收报告 FEEDBACK-ABSORPTION.md |

## 包结构

```
geo-job-hunt-pack/
├── README-PACK.md           ← 本文件
├── skill/                   ← 生产真源 v5.1.3(可直接部署)
│   ├── SKILL.md            skill 本体(References 分组小节 + 实测证据附录)
│   ├── README.md           另一台机器安装步骤
│   ├── .gitignore          部署后 git init 用
│   ├── scripts/            6 个脚本(仅 stdlib)
│   │   ├── liepin_common.py   公共库(稳态 2.0s / 回落 0.97 / 限流识别)
│   │   ├── geo_job_hunt.py    forward / reverse / 增量 / md|json|html
│   │   ├── apply_batch.py     批量投递(--allow-empty-kind 唯一开关)
│   │   ├── probe_limit.py     限流静默看门狗 + state 诊断
│   │   ├── apply_tracker.py   投递清单 add/list/set/due/export/import-json
│   │   └── ensure_amap_timeout.py  幂等补 config.yaml 的 amap.timeout:120
│   └── logs/probe_state.json   限流状态(部署时可重置)
└── audit/                   ← 审计、反馈吸收与变更记录
    ├── AUDIT.md            v5 结构化审计报告
    ├── CHANGES-v5.md       v4→v5 变更清单
    ├── CHANGES-v5.1.md     v5.0.1→v5.1.1 变更清单(复核反馈 + 稳态间隔纠偏)
    ├── FEEDBACK-ABSORPTION.md  两份 AI feedback 逐条对账(round 2)
    ├── FIRST-APPLY.md      首投操作指引(限流恢复后解锁 OK_UNVERIFIED)
    ├── config-diff.md      已应用(config timeout 补丁记录)
    ├── handoff.md          委托 Cursor agent 的原始任务书
    └── reviews/            两份原始 feedback 存档
```

## 部署(新机器)

1. `cp -a skill/ ~/.agents/skills/geo-job-hunt/`;`cd` 后 `git init -b main` + 初始 commit(可选但推荐)
2. 挂载:`ln -sfn ~/.agents/skills/geo-job-hunt ~/.hermes/skills/geo-job-hunt`(+ profile skills 双挂载,见 skill/README.md)
3. 密钥:`AMAP_MAPS_API_KEY`(https://lbs.amap.com/api/mcp-server/create-project-and-key)、`MCP_LIEPIN_API_KEY`(https://www.liepin.com/mcp/auth#config,90 天)
4. MCP:见 skill/README.md §4;amap 块缺 `timeout: 120` 时跑 `python3 scripts/ensure_amap_timeout.py`
5. cron 副本:`cp skill/scripts/{probe_limit,liepin_common}.py ~/.hermes/profiles/<profile>/scripts/` + `md5sum` 校验(Hermes cron 拒绝 symlink)

## 已知缺口与解锁清单(如实)

- **真实投递次数 = 0**,apply 成功形态仍标 OK_UNVERIFIED——唯一真正的瓶颈,审计生不出数据。
  猎聘限流窗口未恢复(2026-08-01 21:31 探测仍 limited);看门狗 cron 每 6h 探测,恢复即通知。
- **限流恢复后的解锁动作**(需账号主人确认,只投 1 个):见 `audit/FIRST-APPLY.md` 完整 checklist。
  核心三步:probe 确认恢复 → 生成 hunt JSON → `apply_batch --hunt ... --max 1` 拿原始响应体,
  据此收紧 `classify_business_payload`,OK_UNVERIFIED 升级为真契约。
- 其他已知:`jobKind` 枚举未证实;salaryFloor/Cap schema 为 string(已 str() 转换);npmjs.com 页面 curl 403 → registry API(最新 0.0.8);精确恢复窗口/稳态吞吐上限未测到(限流中)。
