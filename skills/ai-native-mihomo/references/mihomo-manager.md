# mihomo-manager（本 skill 的配置管理部分）

这套工具原先在独立仓库 `~/dev/mihomo-manager`；2026-10-20 起并入
`ai-native-mihomo` skill 本体，路径改为本目录（下方命令都在 skill 根目录执行）。
理由：诊断/管理脚本与它服务的 doctrine 分居两个仓库，必然漂移（线上跑的和仓库里
的两份实现曾经完全不同）。

本地配置管理器。把订阅文件丢进 `sources/`，它按 `policy.yaml` 合并、用真实
mihomo 二进制校验、原子替换 live config 并热重载。**任何一步失败都保持旧配置**，
替换后失败会自动回滚。

## 为什么需要它

- mihomo 的 `fallback` 组在成员全部失效时**不会降级**，会锁死在死节点上
  （2026-09-14 实测复现），把整条链路带死。
- `url-test` 组会自动切换，但只按延迟排序，表达不了「美国 > 日本 > … > 香港」
  这种地区优先级。
- `url-test` 组即使内部节点全挂也永远上报 `alive=true`，所以 `fallback` 里嵌
  `url-test` 子组必然锁死。

于是分工：**节点来源**由本仓库管理；**出口选择**由 `auto-select.py` 按
`policy.yaml` 生成的 manifest 执行。两者共用同一份策略，不存在第二份地区顺序。

## 文件

| 文件 | 作用 |
|---|---|
| `policy.yaml` | 单一事实源：地区优先级、过滤规则、fingerprint 规范化、selector 参数 |
| `scripts/mihomo_manager.py` | CLI：seed / validate / reconcile / status / rollback / install-units |
| `scripts/auto-select.py` | 出口选择器：机场层级 → 地区优先级 + **机场级 fallback** + 失败节点回避。策略从 manifest 读 |
| `units/` | reconcile path/service + `mihomo-auto-select` service/timer（出口选择，10s 一轮） |
| `tests/` | 离线测试 + synthetic fixtures（假地址，不含真实凭据） |
| `scripts/mihomo-doctor` | 一条命令判定「代理是不是挂了、挂在哪一层」（只读，~8s，`--json` 可用） |
| `TRIAGE.md` | 给 agent 的固定排查路径 + 判定表 + 这台机器的当前机场事实 |
| `scripts/secret_scan.py` | 提交前密钥扫描 |

## 运行时路径（全部不进 Git）

| 用途 | 路径 |
|---|---|
| 输入 drop-in | `~/.config/mihomo/sources/` |
| 私密 base | `~/.config/mihomo/sources/base.yaml` |
| live 配置 | `~/.config/mihomo/config.yaml` |
| 备份 | `~/.config/mihomo/backups/` |
| manifest（无密钥，给 selector） | `~/.config/mihomo/manager/manifest.json` |
| 状态 | `~/.local/state/mihomo-manager/state.json` |

## 用法

```bash
cd ~/dev/agent-skills/skills/ai-native-mihomo

# 1. 一次性：把当前能用的配置存成私密 base
python3 scripts/mihomo_manager.py seed

# 2. 加订阅（*.yaml / *.yml / *.json 都行）
cp 新订阅.yaml ~/.config/mihomo/sources/

# 3. 先干跑：只生成 candidate 并校验，不碰 live
python3 scripts/mihomo_manager.py validate

# 4. 应用：合并 → 校验 → 备份 → 原子替换 → 热重载 → post-check（失败回滚）
python3 scripts/mihomo_manager.py reconcile

# 5. 查状态 / 回滚
python3 scripts/mihomo_manager.py status
python3 scripts/mihomo_manager.py rollback --list
python3 scripts/mihomo_manager.py rollback
```

`python3 scripts/mihomo_manager.py --help` 和 `python3 scripts/mihomo_manager.py reconcile --help`
都有说明。

## 自动 reconcile（可选）

```bash
python3 scripts/mihomo_manager.py install-units          # 只安装 units，不 enable
systemctl --user enable --now mihomo-reconcile.path   # 想自动跑再开
```

坏文件只会让这一轮失败并写进 `state.json`，**不会动 live 配置**。

## 支持的输入 schema

1. **full-config**：顶层 mapping 带 `proxies`。只取节点，里面的
   `rules` / `dns` / `tun` / `log-level` 一律忽略 —— 新订阅不允许覆盖本机策略。
2. **provider**：顶层 mapping 只有 `proxies`（可选 `proxy-groups`）。
3. **proxy list**：顶层就是节点对象数组（`.json` 常见）。

其它 schema 明确报错，**绝不静默生成空配置**。

## 合并语义（deterministic / idempotent）

- 同名同定义 → 去重。反复 reconcile 不会累积节点。
- 同名不同定义 → 稳定重命名 `原名 (2)`，保留地区前缀，并记入 `state.json`
  → `conflicts`。
- `client-fingerprint: random` → `chrome`。本机实测 `random` 会随机撞到服务端
  不接受的指纹，表现为大面积 `REALITY authentication failed`（46 个节点只剩 6 个活）。
- 机场流量/官网伪节点按 `policy.yaml` 的 `exclude_name_patterns` 排除。

## 生成的组

- `<group_name>`（默认 `节点列表`）：`select` 组，成员按「地区优先 > 倍率低优先」
  排序，由 `auto-select.py` 控制。
- 每个地区一个 `<地区>优选` 的 `url-test` 组，唯一作用是持续驱动健康检查，
  让 selector 读到新鲜数据。

地区顺序、组名、健康检查参数全部来自 `policy.yaml`；改一处，生成结果和
selector 行为一起变。

## 测试

```bash
python3 -m unittest discover -s tests     # 离线，不碰 ~/.config，不连 mihomo
python3 scripts/secret_scan.py      # 提交前必跑
```

## 提交纪律

与仓库其余部分一同提交。提交前跑 `scripts/secret_scan.py`：任何 server / uuid /
public-key / secret / 订阅域名一旦出现在被跟踪文件里就报错。
