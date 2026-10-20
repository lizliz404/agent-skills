# TRIAGE —— 「代理是不是挂了」的固定路径

给 agent 的 30 秒判定流程。不要重新发明，先跑一条命令。

```bash
mihomo-doctor          # 中文报告，退出码 0 正常 / 1 降级 / 2 不可用
mihomo-doctor --json   # 机器可读（字段：verdict / checks[] / airports[]）
mihomo-doctor -q       # 一行结论
```

它一次读完全部证据：服务状态、REST API、当前出口与健康数据、每家机场的
节点存活数、订阅到期/额度、3 个真实目标探针、近 60 分钟自动切换次数。
只读，不改配置、不切节点、不刷新 provider。约 8 秒。

## 读结果的判定表

| 读到的组合 | 结论 | 下一步 |
|---|---|---|
| 全部 ✅ | 代理正常 | 不要再排查。若用户仍觉得卡，问题在应用侧或目标站，不在代理 |
| `core.service` ❌ | 进程没起来 | `systemctl --user status mihomo`，看退出原因；不要先动订阅 |
| `core.api` ❌ | 核心活着但 API 不通 | 端口/secret 变了？看 `config.yaml` 的 `external-controller` |
| `exit` ❌ + 有别的机场 ✅ | 自动选择卡在死节点 | 跑 `python3 auto-select.py` 一次；持续不切 → 看 selector 日志 |
| 某机场 `0/N 节点健康` ❌ | **那一家机场死了**，不是 mihomo 的问题 | 找机场要新订阅 / 换一家；`policy.yaml` 里剔掉这家 |
| 机场 ✅ 但 `订阅 剩余 <7 天` 或 `≥90%` | 快到期/快跑光 | 这才是「该买订阅」的信号 |
| `select.flap` ⚠️ ≥3 次/小时 | 出口在抖 | 看是不是一个死机场还在参选（常见）。把死机场从候选里删掉 |
| `probe` ⚠️ 单点 2.5s+ 但都通 | 线路慢，不是断 | 换地区试（`PUT /proxies/节点列表`）；慢不是"挂" |
| `probe` ❌ 全失败 | 出口彻底不通 | 先手动切一个已知健康节点验证，再判断是机场还是本机网络 |

## 只有在 doctor 说不清时才用的命令

```bash
systemctl --user status mihomo --no-pager        # 进程为什么重启
journalctl --user -u mihomo -n 50 --no-pager     # dial 失败 / 规则命中
journalctl --user -u mihomo-auto-select -n 20    # 切换决策
jq -r '.proxies["节点列表"].now' <(curl -s -H "Authorization: Bearer $SECRET" \
    http://127.0.0.1:9090/proxies)                # 当前出口（SECRET 在 config.yaml）
curl -s -x http://127.0.0.1:7890 -o /dev/null -w '%{http_code} %{time_total}\n' \
    https://www.gstatic.com/generate_204         # 端到端，204 才算通
```

## 三个不要再犯的错误

1. **别用 `dig` / `getaddrinfo` 判断机场死没死。** 本机 DNS 被 mihomo 的
   fake-ip 接管，任何域名都会解析成 `198.18.x.x`；而 `dig` 根本没装
   （`dig: command not found` —— 空输出不等于 NXDOMAIN）。节点死活只以
   `/proxies` 里的 `alive` + `history` 为准。
2. **别把 `GET /group/<g>/delay` 当健康探针。** 它会清掉 selector 当前选择，
   并且在所有成员上各跑一次；只探单个节点用 `GET /proxies/<name>/delay`。
3. **别把"慢"说成"挂"。** 全部探针 2–3s 但都返回 200/204 = 线路慢；只有
   `code=000` / 超时 / `alive=false` 才是"不通"。

## 这台机器的当前事实（改动时同步更新这里）

| 事实 | 值 |
|---|---|
| 机场 A（主线） | 绿树 lvshu，`proxy-provider`，mihomo 每小时自动拉 |
| 机场 B（仅 fallback） | 快车 gfw2500，46 个内联静态节点；订阅 URL 待补，2026-10-20 起 46/46 全死 |
| 出口组 | `节点列表`（select），由 `auto-select.py` + `mihomo-auto-select.timer` 每 10 秒决策 |
| 层级 | 机场层级 > 地区优先级：绿树还有健康节点时不会用快车的“更好地区”抢过去 |
| 策略 SOT | `policy.yaml`（地区优先级 / 伪节点正则 / 选择器参数），脚本不得再硬编码一份 |
| 已知坑 | `profile.store-selected: true` 会把死节点持久化；DNS 为 fake-ip；`dig` 未安装 |

> 2026-10-20 的一次实测：机场 A 46/46 节点 `alive=false`、`delay=0`，机场 B
> 27/33 健康、订阅剩 17 天 / 469 GiB。结论「绿树在扛、快车已死、不必买绿树、
> 缺一家主线」——`mihomo-doctor` 一条命令就给出了同样的判断。

## 机场级 fallback（一次订阅失效 → 自动转下一家）

这不是靠 mihomo 的组类型，而是 `auto-select.py` 每分钟级别的决策：

1. **机场顺序**来自 `policy.yaml` 的 `provider_order`（→ manifest）。第一家全部节点
   不健康时，下一家的健康节点顶上；地区优先级只在同一家内部起作用。
2. **当前出口每次运行都实测**：经本机代理端口打一次 204。mihomo 的健康检查要
   60s 才反映出口刚断的事实，只读 `history` 会让切换晚 1~2 分钟。
3. **实测不通 + history 也不可信** → 立即切换，不受冷却期限制。
   **实测不通但 history 说它只是慢** → 算「慢而没死」，仍然受 5 分钟冷却约束，
   避免一条烂线把出口甩来甩去。
4. **刚失败过的节点进回避名单 10 分钟**（`state.json.avoid`），防止「切走 → 又切回
   同一个坏节点」的循环。
5. **全部机场都挂** → 刷 provider 健康检查 → 强制重拉订阅 → 还不行才 `notify-send`
   报警（半小时限频）。

实测（2026-10-20，timer 10s）：把出口手动指向死节点，**10 秒内切回健康节点**。
上限 ≈ timer 间隔（10s）+ 单次运行（约 4s，含 1 次 204 实测 + provider 刷新）。

**这条机制救不了什么**：它只能把流量转到「存活的下一家」。如果存活的只有一家、
而那一家本身在抖（当晚绿树 TLS 握手 1.5–4s、偶发超时），切换只会在这家内部挑
最不坏的节点——瓶颈在机场质量，不在 fallback 逻辑。
