#!/usr/bin/env python3
"""fleet-guard: 舰队终端挂载守卫 + YOLO 审计。由 watchdog.sh 每轮调用，也可单独跑（干跑视图）。

不靠 agent 记性的两层兜底：
1) 孤儿 agent 终端（无 parent、无 herdr.space）自动挂进 Herdr 窗口：
   cwd 前缀匹配现有 space folder；无匹配则 space.new --focus false 建同名空间。
   有 parent 的 worker 不用挂——在父 tab 下以 sub_agent 可见；
   但父终端自己没挂（非 agent 父、漏挂的 agent 父）时改挂父，子随父可见；
   父已死/查不到时子按孤儿挂。
2) 所有 live agent 终端 argv 审 bypass flag；缺 flag 的一次性打 herdr.alert
   并 hc send 父会话提醒重 spawn（argv 无法运行时改）。无父的视为 Liz 手开，不审。
3) 卡住检测：status=working 但末 20 行屏（去掉 spinner/计时器/页脚后）连续
   FLEET_STALL_MIN（默认 20）分钟不变 → 按 cwd 域找当期 boss 报一次。用屏指纹不用
   turn/status_ms：pi、devin 的 TUI 里 turn 恒为 0、status_ms 全程不刷新，假的。
   上游挂起时 hc 只显示 running，不盯屏就不知道。
4) 死亡上报：上轮还活着、这轮 finished 且 exit_code≠0 → 报给父会话（worker 崩了
   跟"干完了"在 hc ls 里长得一样，这是区分两者的地方）。
3/4 都直接 hc send 并写 status.log 的 NOTIFY 行（不走 watchdog 的 notify：那条路只认默认
boss，跨域会打错收件人；stderr 只给人手跑看）。
挂载/审计动作仍打印一行给 watchdog 的 notify()。
整轮持 .yolo-alerted.lock flock，防双 watcher/手跑并发重复告警。
"""
import fcntl, hashlib, json, os, re, secrets, shutil, subprocess, sys, time

FLEET = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
    "FLEET", os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
ALERTED = os.path.join(FLEET, ".yolo-alerted")
STALLED = os.path.join(FLEET, ".stall-alerted")
DEATH = os.path.join(FLEET, ".death-alerted")
TURNS = os.path.join(FLEET, ".worker-turns")      # addr\tscreen_sig\tsince_ms
SEEN = os.path.join(FLEET, ".worker-seen")        # 上轮还活着的地址
LOG = os.path.join(FLEET, "status.log")
STALL_MIN = int(os.environ.get("FLEET_STALL_MIN") or 20)
AGENTS = ("devin", "agy", "antigravity", "claude", "codex", "gemini", "opencode")  # pi 免 flag
# agent 名 -> argv 里必须出现的串
BYPASS = {
    "devin": "dangerous",                        # --permission-mode dangerous
    "agy": "--dangerously-skip-permissions",
    "antigravity": "--dangerously-skip-permissions",
    "claude": "--dangerously-skip-permissions",
    "codex": "--dangerously-bypass-approvals-and-sandbox",
    "gemini": "--yolo",
}
HERDR_APP = shutil.which("herdr-app")


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except OSError:
        return None


def hc(*args):
    return run(["hc", *args])


def read_lines(path):
    try:
        return [l.rstrip("\n") for l in open(path) if l.strip()]
    except OSError:
        return []


def logline(to, msg):
    """自己投递的告警也留 NOTIFY 行——watchdog 的 status.log 是唯一通路审计面。"""
    try:
        with open(LOG, "a") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')} NOTIFY [{to or '-'}] guard: {msg}\n")
    except OSError:
        pass


def boss_for(cwd):
    """按 cwd 域解析当期 boss；解析不到退 FLEET_BOSS。"""
    dom = os.path.basename((cwd or "").rstrip("/"))
    if dom:
        r = run([os.path.join(HERE, "fleet-boss"), dom])
        if r is not None and r.returncode == 0 and (r.stdout or "").strip():
            return r.stdout.strip()
    if os.environ.get("FLEET_BOSS"):
        return os.environ["FLEET_BOSS"]
    r = run([os.path.join(HERE, "fleet-boss"), "--all"])
    return r.stdout.strip() if r is not None and r.returncode == 0 else ""


SPIN = re.compile("[\u2800-\u28ff\u2500-\u257f│─━┄]")
DUR = re.compile(r"\d+m ?\d+s|\d{1,2}:\d{2}:\d{2}|\b\d+s\b")
NOISE = ("esc twice", "shell ↓", "shells ↓", "ctrl+o", "tokens", "%")


def screen_sig(addr):
    """末 20 行的归一化指纹：去掉 spinner/计时器/TUI 页脚这类永远在变的东西，
    剩下的只有'它真的动了'才会变——turn/status_ms 对 pi/devin TUI 都是死的。"""
    r = hc("read", addr)
    if r is None or r.returncode != 0:
        return None
    out = []
    for l in (r.stdout or "").splitlines():
        if not l.strip():
            continue
        l = SPIN.sub("", l).strip()
        l = DUR.sub("#", l)
        if not l or any(n in l for n in NOISE):
            continue
        out.append(l)
    if not out:
        return None
    return hashlib.md5("\n".join(out[-20:]).encode("utf-8", "replace")).hexdigest()


def stall_and_death(terms, get_term):
    """3) 屏不动 4) 非零退出——hc 只报 status，不报"为什么"。"""
    now = int(time.time() * 1000)
    prev = {}
    for line in read_lines(TURNS):
        p = line.split("\t")
        if len(p) >= 3:
            try:
                prev[p[0]] = (p[1], int(p[2]))
            except ValueError:
                pass
    seen_prev = set(read_lines(SEEN))
    alerted = set(read_lines(STALLED))
    state, seen_now = [], set()
    for t in terms:
        if t.get("state") != "live":
            continue
        a = t["address"]
        seen_now.add(a)
        name = t.get("name") or a
        if "boss" in name.lower() or (t.get("status") or "") != "working":
            continue
        sig = screen_sig(a)
        if not sig:
            continue
        pa = prev.get(a)
        since = pa[1] if pa and pa[0] == sig else now
        state.append(f"{a}\t{sig}\t{since}")
        mins = (now - since) // 60000
        key = f"{a}:{sig[:8]}"
        if mins < STALL_MIN or key in alerted:
            continue
        d = get_term(a) or {}
        cwd = d.get("cwd") or t.get("cwd") or ""
        to = boss_for(cwd)
        parent = d.get("parent")
        msg = (f"fleet-guard: {a} ({name}) 还是 working，但屏幕 {mins} 分钟没变"
               f"——多半卡在授权/挂起的上游。`hc read {a}` 看一眼，确认死了就 hc kill + 重派。")
        if to:
            hc("send", to, msg)
        elif parent:
            hc("send", parent, msg)
        logline(to or parent or "", f"{a} stalled {mins}m")
        open(STALLED, "a").write(key + "\n")
        alerted.add(key)
        # 走 stderr：watchdog 只转 stdout 给默认 boss，重复投递会打错收件人
        print(f"stall {a} ({name}) {mins}m -> {to or parent or 'log-only'}", file=sys.stderr)

    try:
        with open(TURNS, "w") as f:
            f.write("\n".join(state) + ("\n" if state else ""))
        with open(SEEN, "w") as f:
            f.write("\n".join(sorted(seen_now)) + ("\n" if seen_now else ""))
    except OSError:
        pass

    # 4) 死亡上报：只看“上轮活着、这轮没了且退出码非零”
    if not seen_prev:
        return
    r = hc("ls", "--all", "--json")
    try:
        allt = json.loads(r.stdout).get("terminals", []) if r is not None else []
    except Exception:
        allt = []
    gone = set(read_lines(DEATH))
    for t in allt:
        a = t.get("address")
        if a not in seen_prev or t.get("state") == "live":
            continue
        rc = t.get("exit_code")
        if rc in (None, 0) or a in gone:
            continue
        # hc 自己会给父终端发 "<t> exited (exit N)" note，父活着就别重复打扰；
        # 真正没人管的是 --no-parent 或父已死的那类 worker。
        parent = t.get("parent")
        if parent and get_term(parent):
            open(DEATH, "a").write(a + "\n")
            gone.add(a)
            continue
        name = t.get("name") or a
        msg = (f"fleet-guard: {a} ({name}) 无声退出 rc={rc}" + (f"（signal={t.get('signal')}）" if t.get("signal") else "")
               + f"——不是 normal done。`hc read {a}` 看尾屏找原因（模型 400/欠费/超时都在那）。")
        to = parent or boss_for(t.get("cwd") or "")
        if to:
            hc("send", to, msg)
        logline(to or "", f"{a} died rc={rc}")
        open(DEATH, "a").write(a + "\n")
        gone.add(a)
        print(f"died {a} ({name}) rc={rc} -> {to or 'log-only'}", file=sys.stderr)


def main():
    try:
        seen = {l.strip() for l in open(ALERTED) if l.strip()}
    except OSError:
        seen = set()

    r = hc("ls", "--json")
    if r is None or r.returncode != 0:
        return
    try:
        terms = [t for t in json.loads(r.stdout).get("terminals", []) if t.get("state") == "live"]
    except Exception:
        return

    spaces = []
    if HERDR_APP:
        r = run([HERDR_APP, "ls"])
        if r is not None and r.returncode == 0:
            try:
                spaces = json.loads(r.stdout).get("spaces", [])
            except Exception:
                pass

    term_cache = {}

    def get_term(addr):
        # hc get 对不存在的地址 rc=0 但返回 {"error":...}，按查不到处理
        if addr not in term_cache:
            g = hc("get", addr)
            try:
                d = json.loads(g.stdout) if g is not None and g.returncode == 0 else None
                term_cache[addr] = d if d and "error" not in d and d.get("state") == "live" else None
            except Exception:
                term_cache[addr] = None
        return term_cache[addr]

    def mount(addr, name, cwd, lab):
        sid = sname = None
        for s in spaces:
            f = s.get("folder") or ""
            if f and cwd.startswith(f):
                sid, sname = s["id"], s["name"]
                break
        if not sid and cwd and HERDR_APP:
            r = run([HERDR_APP, "do", "space.new", "--name", name, "--folder", cwd, "--focus", "false"])
            if r is not None:
                try:
                    out = json.loads(r.stdout)
                    sid = out.get("id") or out.get("space")
                    sname = name
                except Exception:
                    pass
        if sid:
            hc("label", addr, f"herdr.space={sid}")
            hc("label", addr, "herdr.seen=0")
            if "where" not in lab:
                hc("label", addr, f"where={sname} / {name}")
            print(f"{cwd}\tmounted {addr} ({name}) -> space {sname}")

    for t in terms:
        ag = (t.get("agent") or "").lower()
        kind = next((k for k in AGENTS if k in ag), None)
        if not kind:
            continue
        a = t["address"]
        d = get_term(a)
        if not d:
            continue
        name = t.get("name") or d.get("name") or a
        lab, argv, parent = d.get("labels") or {}, " ".join(d.get("argv") or []), d.get("parent")

        # bypass 审计只管子终端（agent spawn 的）；无父的孤儿视为 Liz 手开，不打扰
        need = BYPASS.get(kind)
        if parent and need and need not in argv and a not in seen:
            alert = json.dumps({
                "id": secrets.token_hex(4), "at": int(time.time() * 1000),
                "title": f"{name} spawned without bypass flag",
                "body": f"argv 缺 `{need}`——会卡在授权弹窗。父会话请 kill 后带正确 flag 重 spawn，或直接用 ~/fleet-orch/fleet-spawn 重派（devin 用 --permission-mode dangerous）。",
                "about": True, "task": "fleet-guard"})
            hc("label", a, f"herdr.alert={alert}")
            hc("send", parent,
               f"fleet-guard: {a} ({name}) spawned WITHOUT bypass flag (`{need}` missing) — will stall on prompts. Kill + respawn with the flag, or respawn via ~/fleet-orch/fleet-spawn {kind} {name} --cwd <dir>.")
            open(ALERTED, "a").write(a + "\n")
            seen.add(a)
            print(f"{d.get('cwd') or ''}\talerted {a} ({name}): missing {need}")

        if "herdr.space" in lab:
            continue
        if parent:
            pd = get_term(parent)
            if pd and "herdr.space" in (pd.get("labels") or {}):
                continue
            if pd:
                # 父活着但没挂：挂父，子终端在父 tab 下随之可见
                mount(parent, pd.get("name") or parent, pd.get("cwd") or "", pd.get("labels") or {})
                continue
            # 父已死/查不到：落到下面按孤儿挂子
        mount(a, name, d.get("cwd") or "", lab)

    # 3/4) 卡住 + 非零退出（热生效：guard 每轮由 watcher 新起，改完不用重启 watcher）
    try:
        stall_and_death(terms, get_term)
    except Exception as e:      # 兜底：检测出错不能拖死挂载/审计
        print(f"guard: stall/death 检查异常 {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        _lock = open(os.path.join(FLEET, ".yolo-alerted.lock"), "w")
        fcntl.flock(_lock, fcntl.LOCK_EX)
    except OSError:
        pass
    main()
