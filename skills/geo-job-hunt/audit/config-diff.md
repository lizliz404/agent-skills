# config.yaml 补丁建议(已应用)

> **状态:已应用(2026-08-01,合入 v5 时四处均已补 `timeout: 120`)**。
> 幂等工具:`scripts/ensure_amap_timeout.py`(默认 dry-run,`--yes` 落盘;已含则跳过)。
> 本文件保留作审计记录。

## 背景

SKILL v4/v5 推荐 `amap.timeout: 120`,但以下四处生产配置**均缺少** `timeout`(仅有 `connect_timeout: 90`):

| 文件 | amap 行号(约) |
|---|---|
| `~/.hermes/config.yaml` | 649–657 |
| `~/.hermes/profiles/writing/config.yaml` | 589–597 |
| `~/.hermes/profiles/lyric/config.yaml` | 681–689 |
| `~/.hermes/profiles/trading/config.yaml` | 587–595 |

`liepin` 块四处均已含 `timeout: 120` 与 `connect_timeout: 60` —— **无漂移**。

## 建议补丁(每处 amap 块相同)

```diff
   amap:
     command: npx
     args:
       - -y
       - '@amap/amap-maps-mcp-server'
     env:
       AMAP_MAPS_API_KEY: ${AMAP_MAPS_API_KEY}
     connect_timeout: 90
+    timeout: 120
     enabled: true
```

## 风险

- **低**:仅拉长 MCP 客户端等待,不改变 transport 或密钥。
- 合入后执行 `/reload-mcp` + `/new`。

## 证据级别(当前)

**高** — v5 合入时四处均已补 `timeout: 120`;`ensure_amap_timeout.py` dry-run 四轮幂等跳过(2026-08-01 round 2 复验)。

历史背景(审计时):SKILL v4/v5 推荐 `amap.timeout: 120`,但以下四处生产配置**曾长期缺少** `timeout`:
