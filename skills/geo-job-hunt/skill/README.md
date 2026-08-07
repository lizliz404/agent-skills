# geo-job-hunt · 安装说明(可分享)

面向「另一用户 / 另一台机器」。生产真源约定:`~/.agents/skills/geo-job-hunt/`。

完整能力说明、References、限流与投递语义见 `SKILL.md`(v5.0.0)。

## 1. 依赖

- Python 3.10+
- Node.js ≥ 22(`npx @amap/amap-maps-mcp-server`)
- 可选:Hermes Agent(若要用 MCP 工具而非仅 CLI 脚本)

## 2. 放置 skill

```bash
mkdir -p ~/.agents/skills
cp -a /path/to/geo-job-hunt ~/.agents/skills/geo-job-hunt

# Hermes 挂载(两处 symlink 指向同一真源)
ln -sfn ~/.agents/skills/geo-job-hunt ~/.hermes/skills/geo-job-hunt
ln -sfn ~/.agents/skills/geo-job-hunt \
  ~/.hermes/profiles/writing/skills/productivity/geo-job-hunt
# 其他 profile 可按需同样挂载到 profiles/<name>/skills/.../geo-job-hunt
```

## 3. 密钥

在 `~/.hermes/.env` 或 `~/.hermes/profiles/<name>/.env`(权限 600):

```
AMAP_MAPS_API_KEY=...
MCP_LIEPIN_API_KEY=...
```

- 高德 Key:按官方流程创建应用与 Key — https://lbs.amap.com/api/mcp-server/create-project-and-key (快速接入:https://developer.amap.com/api/mcp-server/gettingstarted)
- 猎聘 token:登录 https://www.liepin.com/mcp/auth#config 生成(90 天);FAQ/限流说明亦见 https://www.liepin.com/mcp/server。

## 4. MCP(Hermes)

在 **`writing` / `lyric` / `trading`** 各 profile 的 `config.yaml`,以及根 `~/.hermes/config.yaml` 的 `mcp_servers` 中配置:

```yaml
amap:
  command: npx
  args: ["-y", "@amap/amap-maps-mcp-server"]
  env:
    AMAP_MAPS_API_KEY: ${AMAP_MAPS_API_KEY}
  connect_timeout: 90
  timeout: 120          # 已应用;新环境: python3 scripts/ensure_amap_timeout.py
  enabled: true
liepin:
  url: https://open-agent.liepin.com/mcp/user
  headers:
    x-user-token: ${MCP_LIEPIN_API_KEY}
  timeout: 120
  connect_timeout: 60
  enabled: true
```

改完后 `/reload-mcp` + `/new`(或重启 gateway)。amap 块若缺 `timeout: 120`,跑 `python3 scripts/ensure_amap_timeout.py`(幂等,dry-run 默认)。

## 5. 冒烟(勿在已知限流窗口狂打)

```bash
cd ~/.agents/skills/geo-job-hunt
python3 scripts/probe_limit.py          # 有输出=恢复;无输出=仍限流(正常)
python3 scripts/geo_job_hunt.py forward --help
python3 scripts/apply_batch.py --help
python3 scripts/apply_tracker.py list
```

## 6. 限流探测 cron(Hermes)

Hermes cron **不能**指向 symlink 脚本。把文件**实体复制**到 profile scripts(当前为 `writing`):

```bash
SRC=~/.agents/skills/geo-job-hunt/scripts
DST=~/.hermes/profiles/writing/scripts
cp "$SRC/probe_limit.py" "$SRC/liepin_common.py" "$DST/"
md5sum "$SRC/probe_limit.py" "$DST/probe_limit.py"   # 合入后应一致
```

- Job 名:`liepin-limit-probe`,间隔 **every 360m**,`no_agent=true`
- 恢复时才有 stdout 可投递 Telegram;仍限流时静默

## 7. 不要做的事

- 不要把高德改回 HTTP URL transport
- 不要把猎聘 token / 简历 PDF 写进 skill 仓库
- 不要每几分钟 probe(自我续杯)
- 不要在限流窗口跑完整 `forward`/`apply_batch` 实网

## 8. 延伸阅读

- `SKILL.md` → **参考资料 (References)** 小节(授权页、GitHub、高德 API、端点)
- `~/notes/geo-job-hunt-v5-draft/AUDIT.md` → 生态审计报告(若已生成)
