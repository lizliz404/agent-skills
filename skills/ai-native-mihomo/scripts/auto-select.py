#!/usr/bin/env python3
"""mihomo 出口自动选择 —— 地区优先级 + 自动降级 + 自动恢复 + 多机场热备。

为什么需要这个脚本（而不是纯配置）：
  * mihomo 的 fallback 组在成员全部失效时不会降级 —— 实测会一直锁死在
    死节点上，把整条链路带死（2026-09-14 复现）。
  * mihomo 的 url-test 组虽然会自动切换，但只按延迟排序，没法表达
    "美国 > 日本 > 新加坡 > 台湾 > 其他 > 香港"这种地区优先级；
    而且它即使内部节点全挂也永远上报 alive=true。

做法：
  出口用 select 组（节点列表），本脚本每分钟跑一次，读 mihomo 自己维护的健康
  检查结果，挑出优先级最高的健康节点切过去。

健康数据来源（v1.19.30 实测）：
  * 主线机场的节点是内联的 → 在 GET /proxies 里，单点探测走
    GET /proxies/<name>/delay。
  * 备线机场的节点来自 proxy-provider → **不在** GET /proxies 里，单点
    /proxies/<name>/delay 会返回 Resource not found；只出现在
    GET /providers/proxies/<provider> 里，刷新健康要整家
    GET /providers/proxies/<provider>/healthcheck。

多机场热备（狡兔三窟）：
  2026-09-28 快车（主线）整体挂掉：机场域名都解析不出来了，46 个节点全超时。
  有备线 provider 在，出口会自动落到绿树上，人不用管。两家都挂时才会 ERROR，
  而且报错前先刷健康检查、再强制重拉订阅，最后才 notify-send 叫人。

出口策略：
  1. 优先级：地区优先 > 主/备机场 > 倍率低优先（美国 > 日本 > 新加坡 > 台湾 >
     其他 > 香港）。同地区里主线的健康节点优先，备线只在主线这一地区没健康
     节点时才顶上（省主线额度，语义上"备线"）。
  2. 响应慢于 MAX_DELAY 的节点，以及 history 超过 FRESHNESS 秒没刷新的节点，
     一律视为不可用 —— 节点被移出所有 url-test 组后 alive 会永久停在 true、
     history 不再刷新，只看 delay 会把它一直当成健康的。
  3. 同地区同机场同倍率之间不为几十毫秒的差异横跳。
  4. 冷却期：刚切换过 COOLDOWN 秒内，只要当前出口还能用就不动车，抑制抖动；
     当前出口挂掉时立即降级，不受冷却期限制。
"""

import datetime
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# ── 策略：一切从 manifest 来 ──────────────────────────────────────
# policy.yaml 是唯一事实源，mihomo-manager 生成 manifest.json，本脚本只读不藏。
# 下面的默认值只在 manifest 缺失/损坏时生效（会打 WARN），不应该长期被用到。
CONFIG_PATH = os.path.expanduser("~/.config/mihomo/config.yaml")
MANIFEST_PATH = os.path.expanduser("~/.config/mihomo/manager/manifest.json")

GROUP = "节点列表"
TEST_URL = "https://www.gstatic.com/generate_204"
MAX_DELAY = 1000  # ms；响应比这还慢的节点视为不可用
PROBE_TIMEOUT = 3000  # ms；脚本自己探测单点时的超时
FRESHNESS = 150  # s；history 超过这么久没刷新就当过期，不再采信
COOLDOWN = 300  # s；切换后的冷却期，抑制节点抖动导致的反复横跳
PROBE_BUDGET = 90  # s；健康数据整体缺失时逐个实测的总预算，防止跑过头
NOTIFY_INTERVAL = 1800  # s；全挂报警的最小间隔，避免每分钟刷屏
EXIT_PROBE_TIMEOUT = 4.0  # s；经本机代理端口验出口，超时即认为这个出口此刻不能用
AVOID_SECONDS = 600  # s；刚被判定失败/很慢的节点，这么久内不再当候选（防止跳回同一个坏节点）

PRIORITY = ["美国", "日本", "新加坡", "台湾", "其他", "香港"]
FALLBACK_REGION = "其他"

# [{"label": "快车 gfw2500", "source": ""}, {"label": "绿树 lvshu", "source": "lvshu"}]
# source: "" = 内联节点（主线机场），其余是 proxy-provider 的名字。
PROVIDER_ORDER = [{"label": "主机场", "source": ""}]

# 机场塞进来的广告/公告伪节点（不是真节点，永远不选）。下面是兜底副本，
# 正常路径读 policy.yaml 的 exclude_name_patterns。
JUNK_REGEX = [re.compile(p) for p in (
    r"^官网[:：]", r"^永久流量[:：]", r"^剩余流量[:：]", r"^流量[:：]",
    r"^到期时间[:：]", r"^套餐[:：]", r"^订阅[:：]",
)]


def load_manifest_policy() -> None:
    """把 policy.yaml 派生出的 manifest 覆盖到模块级策略上。"""
    global GROUP, MAX_DELAY, FRESHNESS, COOLDOWN, PRIORITY, FALLBACK_REGION
    global PROVIDER_ORDER, JUNK_REGEX
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"WARN 读不到 manifest（用内置默认值）: {exc}", file=sys.stderr)
        return
    selector = data.get("selector") or {}
    GROUP = data.get("group_name") or GROUP
    MAX_DELAY = int(selector.get("max_delay_ms", MAX_DELAY))
    FRESHNESS = int(selector.get("freshness_s", FRESHNESS))
    COOLDOWN = int(selector.get("cooldown_s", COOLDOWN))
    order = data.get("region_order")
    if isinstance(order, list) and order:
        PRIORITY = order
        FALLBACK_REGION = data.get("region_fallback") or order[-1]
    providers = data.get("provider_order")
    if isinstance(providers, list) and providers:
        PROVIDER_ORDER = providers
    patterns = data.get("exclude_name_patterns")
    if isinstance(patterns, list) and patterns:
        JUNK_REGEX = [re.compile(p) for p in patterns]


load_manifest_policy()
STATE_PATH = os.path.expanduser("~/.local/state/mihomo-auto-select.json")
LOCK_PATH = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/tmp", "mihomo-auto-select.lock")
API = "http://127.0.0.1:9090"


def read_secret():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"\s*secret:\s*(.+?)\s*$", line)
                if m:
                    return m.group(1).strip("\"'")
    except OSError:
        pass
    return ""


SECRET = read_secret()


def api(path, method="GET", body=None, timeout=10):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + SECRET, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else {}


def q(name):
    return urllib.parse.quote(name, safe="")


# ── 节点分类 ─────────────────────────────────────────────────────────────
def is_junk(name):
    return any(rx.search(name) for rx in JUNK_REGEX)


def region(name):
    """节点属于哪个地区。订阅命名五花八门（"日本一区·电信" / "🇯🇵 日本-01"），
    所以按关键字包含判断而不是前缀 —— 备线机场的名字前面是国旗 emoji。"""
    for r in PRIORITY:
        if r != FALLBACK_REGION and r in name:
            return r
    return FALLBACK_REGION


def mult(name):
    """节点名的计费倍率；没标注的排最后。"""
    m = re.search(r"(\d+)倍消耗", name)
    return int(m.group(1)) if m else 9


def _prov_sources() -> list:
    return [str(p.get("source", "")) for p in PROVIDER_ORDER]


def prov_rank(provider):
    try:
        return _prov_sources().index(provider or "")
    except ValueError:
        return len(PROVIDER_ORDER)


def prov_label(provider):
    """给人看的机场名（报告里的理由用）。"""
    for p in PROVIDER_ORDER:
        if str(p.get("source", "")) == (provider or ""):
            return str(p.get("label") or provider or "内联")
    return provider or "内联"


def tier_key(name, provider):
    """排序键：机场层级 > 地区优先 > 倍率。与延迟无关。

    机场排在地区前面，是因为「备线」就该是备线：主线还有任何健康节点时，
    绝不用备线的“更高优先级地区”抢过去。主线整体不可用才落到下一家。
    """
    return (prov_rank(provider), PRIORITY.index(region(name)), mult(name))


def rank_key(name, provider):
    return tier_key(name, provider) + (name,)


# ── 健康数据 ─────────────────────────────────────────────────────────────
def parse_time(value):
    """解析 mihomo history 里的 RFC3339 时间戳（可能带纳秒），返回 epoch 秒。"""
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    if text[-1] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    # fromisoformat 只接受 1~6 位小数秒，纳秒先截断到微秒
    text = re.sub(r"\.(\d{6})\d+", r".\1", text)
    try:
        dt = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.timestamp()


def _ingest(health, owner, name, obj, provider):
    if not name:
        return
    if name in health and owner.get(name, "") != provider:
        return  # 同名冲突以先到的（内联节点）为准，不静默覆盖
    hist = obj.get("history") or []
    last = hist[-1] if hist else {}
    health[name] = {
        "alive": bool(obj.get("alive")),
        "delay": last.get("delay"),
        "time": parse_time(last.get("time")),
    }
    owner[name] = provider


def real_providers():
    """真正的订阅 provider（HTTP/File）；跳过每组的 Compatible 影子 provider，
    那只是内联节点的只读副本，混进来会重复计数。"""
    try:
        data = api("/providers/proxies")
    except Exception:
        return []
    return [
        name
        for name, v in (data.get("providers") or {}).items()
        if (v or {}).get("vehicleType") not in (None, "Compatible")
    ]


def collect(providers):
    """一次快照：出口组、成员表、健康表、归属表。"""
    proxies = api("/proxies")["proxies"]
    group = proxies.get(GROUP) or {}
    members = list(group.get("all") or [])
    health, owner = {}, {}
    for name, obj in proxies.items():
        if obj.get("all") is not None:
            continue  # 组本身不是节点
        _ingest(health, owner, name, obj, "")
    for p in providers:
        try:
            data = api("/providers/proxies/" + q(p))
        except Exception:
            continue
        for node in data.get("proxies") or []:
            _ingest(health, owner, node.get("name"), node, p)
    return group, members, health, owner


def fresh_delay(health, name, now_ts):
    """节点此刻是否健康：alive + 有 FRESHNESS 以内的记录 + 延迟达标。"""
    if is_junk(name):
        return None
    h = health.get(name)
    if not h or not h.get("alive"):
        return None
    ts = h.get("time")
    if ts is None or now_ts - ts > FRESHNESS:
        return None
    d = h.get("delay")
    return d if isinstance(d, int) and 0 < d <= MAX_DELAY else None


def mixed_port() -> int:
    """本机代理入口端口（mixed-port）。"""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"\s*mixed-port:\s*(\d+)", line)
                if m:
                    return int(m.group(1))
    except OSError:
        pass
    return 7890


def exit_probe(attempts: int = 1) -> bool:
    """经本机代理端口打一次 204：这是用户真正能感觉到的出口健康，
    和 mihomo 最多 FRESHNESS 秒前的缓存无关。两次都失败才判死。

    为什么要它：出口刚断时，mihomo 的健康检查要再跑一轮才反映出来，
    只读 history 会让切换晚 1~2 分钟——这就是“不够丝滑”的真正来源。
    """
    proxy = f"http://127.0.0.1:{mixed_port()}"
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    )
    for _ in range(attempts):
        try:
            with opener.open(TEST_URL, timeout=EXIT_PROBE_TIMEOUT) as resp:
                if resp.status == 204:
                    return True
        except Exception:
            continue
    return False


def probe(name):
    """单点实测（只对内联节点可用），返回延迟 ms；失败返回 None。"""
    u = urllib.parse.quote(TEST_URL, safe="")
    try:
        r = api(f"/proxies/{q(name)}/delay?timeout={PROBE_TIMEOUT}&url={u}")
    except Exception:
        return None
    d = r.get("delay")
    return d if isinstance(d, int) and 0 < d <= MAX_DELAY else None


def refresh_provider(provider):
    """provider 节点没法单点探测：整家刷一次健康检查（一次 API，n 个节点）。"""
    try:
        api(f"/providers/proxies/{q(provider)}/healthcheck")
        return True
    except Exception:
        return False


def update_provider(provider):
    """强制重拉订阅（拉新的用新的；拉失败 mihomo 保留上一次的好快照）。"""
    try:
        api(f"/providers/proxies/{q(provider)}", method="PUT")
        return True
    except Exception as exc:
        print(f"WARN 重拉订阅 {provider} 失败: {exc}", file=sys.stderr)
        return False


# ── 状态 ─────────────────────────────────────────────────────────────────
def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    os.replace(tmp, STATE_PATH)


def notify(title, body):
    """故障桌面提醒：所有故障共用半小时限频，8 秒后自动消失。"""
    state = load_state()
    if time.time() - float(state.get("notified_at", 0) or 0) < NOTIFY_INTERVAL:
        return
    state["notified_at"] = time.time()
    save_state(state)
    if not shutil.which("notify-send"):
        return
    try:
        subprocess.run(
            ["notify-send", "-u", "normal", "-t", "8000", "-e",
             "-a", "mihomo", title, body],
            timeout=5,
            check=False,
        )
    except Exception:
        pass


def _avoid(name, now: float | None = None) -> None:
    """把刚失败的节点拉黑一会儿，避免“切走又切回同一个坏节点”的死循环。"""
    if not name:
        return
    ts = now or time.time()
    state = load_state()
    avoid = {n: until for n, until in (state.get("avoid") or {}).items()
             if isinstance(until, (int, float)) and until > ts}
    avoid[name] = ts + AVOID_SECONDS
    state["avoid"] = avoid
    save_state(state)


def switch_to(target, current, delay, reason):
    """切到 target 并记录切换时间（冷却期基准）。"""
    try:
        api(f"/proxies/{q(GROUP)}", method="PUT", body={"name": target})
    except Exception as exc:
        print(f"ERROR 切换失败: {exc}", file=sys.stderr)
        return 1
    state = load_state()
    state.update({"last_switch": time.time(), "from": current, "to": target})
    save_state(state)
    print(f"SWITCH {current or '(none)'} -> {target} ({delay}ms) —— {reason}")
    return 0


# ── 选择 ─────────────────────────────────────────────────────────────────
def pick_fresh(members, health, owner, now_ts, avoid=None):
    """现有健康数据里挑：按 tier 排序后第一个新鲜健康、且不在回避名单里的节点。

    回避名单空了就退回全量候选 —— 宁可回到窄路，也不能没有出口。
    """
    avoid = avoid or set()
    ordered = sorted(members, key=lambda n: rank_key(n, owner.get(n, "")))
    for name in ordered:
        if name in avoid:
            continue
        d = fresh_delay(health, name, now_ts)
        if d is not None:
            return name, d
    for name in ordered:
        d = fresh_delay(health, name, now_ts)
        if d is not None:
            return name, d
    return None, None


def ladder(providers, members, health, owner, now_ts):
    """健康数据整体缺失/过期时的恢复阶梯，不做全量扫描：

    1. 按地区优先级，每个地区挑一个代表实测（`地区数 × timeout` 就能把每个
       地区、含兜底地区都摸一遍）；
    2. 还有预算就把剩余候选按 tier 顺序补测 —— 已经试过的地区里的第二个健康
       节点不会被漏掉。
    单点探测只对内联节点可用；provider 节点靠整家刷新健康检查拿数据（每个
    provider 每次运行最多刷一次，刷完重新快照）。
    """
    deadline = time.time() + PROBE_BUDGET
    seen = set()
    refreshed = set()

    def evaluate(name):
        nonlocal health, owner
        if name in seen or time.time() > deadline:
            return None
        seen.add(name)
        provider = owner.get(name, "")
        if provider and provider not in refreshed:
            refreshed.add(provider)
            if refresh_provider(provider):
                time.sleep(1.5)
                _, members, health, owner = collect(providers)
        d = fresh_delay(health, name, now_ts)
        if d is None and not provider:
            d = probe(name)
        return d

    ordered = sorted(members, key=lambda n: rank_key(n, owner.get(n, "")))
    for r in PRIORITY:  # 1) 每个地区一个代表
        rep = next((n for n in ordered if region(n) == r), None)
        if rep:
            d = evaluate(rep)
            if d is not None:
                return rep, d
    for name in ordered:  # 2) 剩余候选
        d = evaluate(name)
        if d is not None:
            return name, d
    return None, None


def resync(providers):
    """灾难自救阶梯：刷健康检查 → 强制重拉订阅，每步之后重新评估。"""
    for step in ("healthcheck", "provider-update"):
        for p in providers:
            refresh_provider(p) if step == "healthcheck" else update_provider(p)
        time.sleep(2)
        try:
            group, members, health, owner = collect(providers)
        except Exception:
            continue
        members = [m for m in members if not is_junk(m)]
        now_ts = time.time()
        best, delay = pick_fresh(members, health, owner, now_ts)
        if best is None:
            best, delay = ladder(providers, members, health, owner, now_ts)
        if best is not None:
            return best, delay, step
    return None, None, None


def main():
    lock_fh = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock_fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("OK    另一次运行还在进行，本次跳过")
        return 0

    providers = real_providers()
    try:
        group, members, health, owner = collect(providers)
    except Exception as exc:
        print(f"ERROR 连不上 mihomo API: {exc}", file=sys.stderr)
        return 1

    if not group:
        print(f"ERROR 找不到组 {GROUP}", file=sys.stderr)
        return 1

    members = [m for m in members if not is_junk(m)]
    if not members:
        print("ERROR 出口组里一个节点都没有（订阅/配置是空的）", file=sys.stderr)
        notify("mihomo 出口组是空的", "节点列表没有任何成员，检查订阅是否拉取成功。")
        return 1

    current = group.get("now") or ""
    now_ts = time.time()

    # 当前出口的判断，两个读数都算数：
    #   1) 端到端实测（经本机代理端口打一次 204）—— 出口刚断时这是唯一及时的
    #      读数。只看 mihomo 的 history 最坏会等 FRESHNESS 秒，切换就会“卡”一两分钟。
    #   2) mihomo 的 history —— 用来拿延迟值，并作为第二意见。
    hist_delay = fresh_delay(health, current, now_ts) if current else None
    cur_delay = hist_delay
    cur_alive = bool(current) and hist_delay is not None
    slow_exit = False
    if current and exit_probe():
        # 端到端通：以实测为准。缓存里的“死”只是还没刷新。
        cur_alive = True
    elif current:
        # 端到端不通：先用 mihomo 自己的新鲜数据做第二意见。
        #   慢但没死 → 不算死节点，走正常优先级 + 冷却，不每次都强行切。
        #   history 也不可信 → 确认后立即降级。
        if cur_alive:
            slow_exit = True
        else:
            provider = owner.get(current, "")
            if provider:
                if refresh_provider(provider):
                    time.sleep(1.5)
                    _, _, health, owner = collect(providers)
                    cur_delay = fresh_delay(health, current, time.time())
            else:
                cur_delay = probe(current)
            cur_alive = cur_delay is not None

    state = load_state()
    avoid = {n for n, until in (state.get("avoid") or {}).items()
             if isinstance(until, (int, float)) and until > now_ts}

    target, target_delay = pick_fresh(members, health, owner, now_ts, avoid)
    if target is None:
        target, target_delay = ladder(providers, members, health, owner, now_ts)

    if target is None:  # 真·全挂：先自救，再叫人
        target, target_delay, step = resync(providers)
        if target is not None:
            print(f"RECOVER 自救（{step}）后拿到健康节点")
        else:
            state = load_state()
            state.update({"last_error": time.time(), "error": "没有任何健康节点可用",
                          "nodes": len(members), "providers": providers})
            save_state(state)
            print(f"ERROR 没有任何健康节点可用"
                  f"（{len(providers)} 家机场、{len(members)} 个节点全部不可用，已尝试刷新订阅）",
                  file=sys.stderr)
            notify("mihomo 出口全挂",
                   f"{len(providers)} 家机场、{len(members)} 个节点全部不可用，已尝试刷新订阅。")
            return 1

    state = load_state()
    state.update({"last_ok": time.time(), "nodes": len(members),
                  "providers": providers, "current": current or target,
                  "target": target, "delay": target_delay})
    state.pop("error", None)
    save_state(state)

    if target == current:
        print(f"OK    {current} ({target_delay}ms) 已是最优先的健康节点")
        return 0
    if not cur_alive:
        _avoid(current)
        return switch_to(target, current, target_delay, "当前出口实测不通，立即转到下一家")

    cur_ms = f"{cur_delay}ms" if cur_delay is not None else "实测通"

    if slow_exit:
        since = now_ts - float(load_state().get("last_switch", 0) or 0)
        if since < COOLDOWN:
            print(f"HOLD  {current} ({cur_ms}) 保持 —— 出口实测很慢但未到必换，"
                  f"距上次切换 {since:.0f}s（冷却 {COOLDOWN}s）")
            return 0
        _avoid(current)
        why = f"更健康的节点（本出口实测 {cur_ms} 不通畅）"
        return switch_to(target, current, target_delay, why)

    current_provider = owner.get(current, "")
    target_provider = owner.get(target, "")
    t_key, c_key = tier_key(target, target_provider), tier_key(current, current_provider)
    if t_key > c_key:
        print(f"HOLD  {current} ({cur_ms}) 保持 —— 候选 {target} ({target_delay}ms) 优先级不高于当前")
        return 0
    if t_key == c_key:
        print(f"HOLD  {current} ({cur_ms}) 保持 —— 同地区同机场同倍率候选 {target} "
              f"({target_delay}ms)，不切换")
        return 0

    if t_key[0] < c_key[0]:
        why = (f"更高层级机场可用（{prov_label(target_provider)} → "
               f"{prov_label(current_provider)} 降为备线）")
    elif t_key[1] < c_key[1]:
        why = f"同机场内更高优先级地区 {region(target)}"
    else:
        why = f"同机场同地区更低倍率 {mult(target)}倍"

    since = now_ts - float(state.get("last_switch", 0) or 0)
    if since < COOLDOWN:
        print(f"HOLD  {current} ({cur_ms}) 保持 —— 更优的 {target} ({target_delay}ms) 存在（{why}），"
              f"但距离上次切换仅 {since:.0f}s（冷却 {COOLDOWN}s）")
        return 0
    return switch_to(target, current, target_delay, why)


if __name__ == "__main__":
    sys.exit(main())
