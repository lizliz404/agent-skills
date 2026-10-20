#!/usr/bin/env python3
"""mihomo 本地配置管理器。

把一份或多份 Clash/mihomo 订阅文件丢进 sources/，它会按 policy.yaml 的策略
合并、生成 candidate、用真实 mihomo 二进制校验、原子替换 live config、热重载，
并做最小 post-check。任何一步失败都保持旧配置不动，替换后失败会自动回滚。

设计要点：
  * 顶层策略（rules / dns / tun / ...）只来自 base。输入文件里的这些东西一律
    忽略 —— 新订阅不得覆盖本机策略。
  * base 只在第一次 seed 时从当前 live config 建立。之后 live 是输出不是输入，
    反复 reconcile 不会累积节点。
  * 生成物以 0600 写入，用 os.replace 原子替换。
  * 状态和 manifest 只含哈希/计数/名字，绝不含 server / uuid / public-key / secret。
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("ERROR: 缺少 PyYAML。Arch: sudo pacman -S python-yaml")

# 脚本在 <skill>/scripts/，policy.yaml / units/ / tests/ 在 skill 根目录
SKILL_DIR = Path(__file__).resolve().parent.parent
POLICY_PATH = SKILL_DIR / "policy.yaml"
UNITS_DIR = SKILL_DIR / "units"

HOME = Path.home()
CONF_DIR = HOME / ".config" / "mihomo"
LIVE = CONF_DIR / "config.yaml"
SOURCES_DIR = CONF_DIR / "sources"
BASE_FILE = SOURCES_DIR / "base.yaml"
BACKUP_DIR = CONF_DIR / "backups"
MANAGER_DIR = CONF_DIR / "manager"
MANIFEST = MANAGER_DIR / "manifest.json"
STAGING_DIR = CONF_DIR / ".staging"
CANDIDATE = STAGING_DIR / "candidate.yaml"

STATE_DIR = HOME / ".local" / "state" / "mihomo-manager"
STATE_FILE = STATE_DIR / "state.json"
LOCK_FILE = STATE_DIR / "reconcile.lock"

MIHOMO_BIN = HOME / ".local" / "bin" / "mihomo"
API_BASE = "http://127.0.0.1:9090"
SYSTEMD_USER_DIR = HOME / ".config" / "systemd" / "user"
INPUT_SUFFIXES = (".yaml", ".yml", ".json")


class ManagerError(Exception):
    """可预期的失败，直接把消息给用户看。"""


class SchemaError(ManagerError):
    """输入文件 schema 不认识。"""


# --------------------------------------------------------------------------
# 小工具
# --------------------------------------------------------------------------
def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def tail(text: str, n: int = 12) -> str:
    lines = [ln for ln in (text or "").strip().splitlines() if ln.strip()]
    return "\n".join(lines[-n:])


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path: Path, text: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)


# --------------------------------------------------------------------------
# policy
# --------------------------------------------------------------------------
def load_policy() -> dict:
    if not POLICY_PATH.is_file():
        raise ManagerError(f"找不到 policy: {POLICY_PATH}")
    with POLICY_PATH.open(encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)
    if not isinstance(policy, dict):
        raise ManagerError(f"policy 不是 mapping: {POLICY_PATH}")
    for key in ("region_order", "region_fallback", "group_name"):
        if key not in policy:
            raise ManagerError(f"policy 缺字段: {key}")
    order = policy["region_order"]
    if not isinstance(order, list) or not order:
        raise ManagerError("policy.region_order 必须是非空列表")
    if policy["region_fallback"] not in order:
        raise ManagerError("policy.region_fallback 必须在 region_order 里")
    if order[-1] != "香港":
        raise ManagerError("policy.region_order 最后一项必须是 香港（兜底语义）")
    providers = policy.get("provider_order") or []
    if not isinstance(providers, list):
        raise ManagerError("policy.provider_order 必须是列表")
    for entry in providers:
        if not isinstance(entry, dict) or "source" not in entry:
            raise ManagerError("policy.provider_order 每项必须是 {label, source}")
    return policy


def region_of(name: str, policy: dict) -> str:
    """节点属于哪个地区。按关键字包含判断，不按前缀——订阅命名五花八门，
    备线机场还可能给名字加国旗 emoji（"🇺🇸 美国-01 | AI | 解锁"）。
    与 auto-select.py 的 region() 必须同一套语义，否则选出的节点和分组对不上。"""
    fallback = policy["region_fallback"]
    for region in policy["region_order"]:
        if region != fallback and region in name:
            return region
    return fallback


def mult_of(name: str) -> int:
    m = re.search(r"(\d+)倍消耗", name)
    return int(m.group(1)) if m else 9


def rank_key(name: str, policy: dict) -> tuple:
    return (policy["region_order"].index(region_of(name, policy)), mult_of(name), name)


# --------------------------------------------------------------------------
# 输入解析
# --------------------------------------------------------------------------
def extract_proxies(data, origin: str):
    """从 full-config / provider mapping 或 proxy object list 里取出 proxies。

    其它 schema 一律明确拒绝，绝不返回空列表假装成功。
    """
    if isinstance(data, list):
        if not data:
            raise SchemaError(f"{origin}: 顶层是空列表，拒绝（不会生成空配置）")
        for i, item in enumerate(data):
            if not isinstance(item, dict) or "name" not in item:
                raise SchemaError(f"{origin}: 列表第 {i} 项不是带 name 的 proxy 对象")
        return data, "proxy-list"

    if isinstance(data, dict):
        if "proxies" not in data:
            keys = ", ".join(sorted(map(str, data))[:8]) or "(空)"
            raise SchemaError(
                f"{origin}: 顶层 mapping 没有 proxies 键（顶层键: {keys}）。"
                "只接受 full-config / provider 两种 schema"
            )
        proxies = data["proxies"]
        if not isinstance(proxies, list) or not proxies:
            raise SchemaError(f"{origin}: proxies 不是非空列表")
        for i, item in enumerate(proxies):
            if not isinstance(item, dict) or "name" not in item:
                raise SchemaError(f"{origin}: proxies 第 {i} 项不是带 name 的对象")
        kind = "provider" if set(data) <= {"proxies", "proxy-groups"} else "full-config"
        return proxies, kind

    raise SchemaError(f"{origin}: 顶层必须是 mapping 或 list，实际是 {type(data).__name__}")


def read_input(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SchemaError(f"{path}: JSON 解析失败: {exc}") from exc
    else:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise SchemaError(f"{path}: YAML 解析失败: {exc}") from exc
    return extract_proxies(data, str(path))


# --------------------------------------------------------------------------
# 归一化 / 合并
# --------------------------------------------------------------------------
def normalize_proxy(proxy: dict, policy: dict):
    p = dict(proxy)
    fixes = []
    target = (policy.get("normalize") or {}).get("client_fingerprint_random_to")
    if target and p.get("client-fingerprint") == "random":
        p["client-fingerprint"] = target
        fixes.append(f"client-fingerprint:random->{target}")
    return p, fixes


def excluded_by(name: str, policy: dict):
    for pattern in policy.get("exclude_name_patterns") or []:
        try:
            if re.search(pattern, name):
                return pattern
        except re.error:
            continue
    return None


def canonical_hash(proxy: dict) -> str:
    blob = json.dumps(proxy, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def merge_proxies(sources, policy: dict):
    """sources: [(origin, [proxy, ...]), ...]，顺序即优先级（base 在最前）。

    幂等：同名同定义直接去重；同名不同定义用 `原名 (2)` 稳定重命名并记录冲突。
    """
    out, seen, used = [], {}, set()
    conflicts, fixes, excluded = [], [], []
    for origin, proxies in sources:
        for proxy in proxies:
            name = proxy.get("name")
            if not isinstance(name, str) or not name.strip():
                raise SchemaError(f"{origin}: 存在没有有效 name 的节点")
            pattern = excluded_by(name, policy)
            if pattern:
                excluded.append({"name": name, "origin": origin, "pattern": pattern})
                continue
            norm, applied = normalize_proxy(proxy, policy)
            for item in applied:
                fixes.append({"name": name, "fix": item})
            digest = canonical_hash(norm)
            if name in seen:
                if seen[name] == digest:
                    continue  # 同名同定义 -> 去重
                new_name, i = name, 2
                while new_name in seen or new_name in used:
                    new_name = f"{name} ({i})"
                    i += 1
                conflicts.append({"name": name, "renamed_to": new_name, "origin": origin})
                norm["name"] = new_name
                name = new_name
            seen[name] = digest
            used.add(name)
            out.append(norm)
    return out, conflicts, fixes, excluded


# --------------------------------------------------------------------------
# 生成
# --------------------------------------------------------------------------
def build_groups(proxy_names, policy: dict):
    health = policy.get("health_group") or {}
    nodes = sorted(proxy_names, key=lambda n: rank_key(n, policy))
    groups = [{"name": policy["group_name"], "type": "select", "proxies": nodes}]
    for region in policy["region_order"]:
        members = [n for n in nodes if region_of(n, policy) == region]
        if not members:
            continue
        groups.append(
            {
                "name": f"{region}{policy['health_group_suffix']}",
                "type": health.get("type", "url-test"),
                "url": health.get("url", "https://www.gstatic.com/generate_204"),
                "interval": health.get("interval", 60),
                "tolerance": health.get("tolerance", 50),
                "lazy": health.get("lazy", False),
                "proxies": members,
            }
        )
    return groups


def build_config(base_cfg: dict, proxies, policy: dict) -> dict:
    cfg = {k: v for k, v in base_cfg.items() if k not in ("proxies", "proxy-groups")}
    cfg["proxies"] = proxies
    cfg["proxy-groups"] = build_groups([p["name"] for p in proxies], policy)
    return cfg


def render_config(cfg: dict, policy: dict) -> str:
    body = yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, default_flow_style=False)
    # 故意不放生成时间戳：同样输入必须得到逐字节相同的输出（幂等）。
    # 时间戳在 manifest.json / state.json 里。
    banner = (
        "# ============================================================\n"
        "# 由 mihomo-manager 生成 —— 不要手工编辑本文件。\n"
        "#   改地区优先级 / 过滤规则 / fingerprint 规范 -> policy.yaml\n"
        "#   加节点或换订阅                              -> 丢进 sources/\n"
        "#   生成时间 / 统计                             -> manager/manifest.json\n"
        f"#   节点数: {len(cfg.get('proxies') or [])}\n"
        "# ============================================================\n"
    )
    return banner + body


# --------------------------------------------------------------------------
# 输入稳定性（防复制到一半）
# --------------------------------------------------------------------------
def list_inputs():
    if not SOURCES_DIR.is_dir():
        return []
    out = []
    for path in sorted(SOURCES_DIR.iterdir()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in INPUT_SUFFIXES:
            continue
        out.append(path)
    return out


def snapshot(paths):
    return {str(p): (p.stat().st_size, file_sha256(p)) for p in paths if p.is_file()}


def settle(paths, attempts: int = 3, delay: float = 2.0):
    if not paths:
        return {}, True
    prev = None
    for i in range(attempts):
        cur = snapshot(paths)
        if prev is not None and cur == prev:
            return cur, True
        prev = cur
        if i < attempts - 1:
            time.sleep(delay)
    return prev or {}, False


# --------------------------------------------------------------------------
# base / live / 备份
# --------------------------------------------------------------------------
def load_base(policy: dict):
    if not BASE_FILE.is_file():
        raise ManagerError(f"缺少 base: {BASE_FILE}（先跑一次 seed）")
    data = yaml.safe_load(BASE_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManagerError(f"base 不是 mapping: {BASE_FILE}")
    proxies = data.get("proxies")
    if not isinstance(proxies, list) or not proxies:
        raise ManagerError(f"base 缺 proxies 列表: {BASE_FILE}")
    cfg = {k: v for k, v in data.items() if k not in ("proxies", "proxy-groups")}
    return cfg, proxies


def backup_live(policy: dict):
    if not LIVE.is_file():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / f"config.{time.strftime('%Y%m%d-%H%M%S')}.yaml"
    if dest.exists():  # 同秒内重复备份
        dest = BACKUP_DIR / f"config.{time.strftime('%Y%m%d-%H%M%S')}.{os.getpid()}.yaml"
    shutil.copy2(LIVE, dest)
    os.chmod(dest, 0o600)
    keep = int(policy.get("backups_keep", 5))
    backups = sorted(BACKUP_DIR.glob("config.*.yaml"))
    for old in backups[:-keep] if len(backups) > keep else []:
        old.unlink(missing_ok=True)
    return dest


def api_secret(cfg: dict) -> str:
    value = cfg.get("secret")
    return value if isinstance(value, str) else ""


def reload_live(secret: str, timeout: int = 15) -> int:
    body = json.dumps({"path": str(LIVE)}).encode()
    req = urllib.request.Request(
        f"{API_BASE}/configs?force=true",
        data=body,
        method="PUT",
        headers={"Authorization": f"Bearer {secret}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status


def post_check(secret: str, expected_nodes: int, group_name: str, timeout: int = 15):
    try:
        req = urllib.request.Request(f"{API_BASE}/proxies", headers={"Authorization": f"Bearer {secret}"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        return False, f"API 不可达: {exc}"
    proxies = data.get("proxies") or {}
    group = proxies.get(group_name)
    if not group:
        return False, f"出口组 {group_name} 不存在"
    got = len([n for n in (group.get("all") or []) if n in proxies])
    if got != expected_nodes:
        return False, f"{group_name} 成员数 {got} != 期望 {expected_nodes}"
    return True, f"{group_name} 成员 {got} 个"


def restore_from(backup: Path | None, secret: str) -> None:
    if backup and backup.is_file():
        shutil.copy2(backup, LIVE)
        os.chmod(LIVE, 0o600)
    try:
        reload_live(secret)
    except Exception:
        pass


# --------------------------------------------------------------------------
# 状态 / manifest
# --------------------------------------------------------------------------
def read_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(STATE_FILE, json.dumps(state, ensure_ascii=False, indent=2) + "\n", 0o600)


def write_manifest(policy: dict, proxies, regions: dict) -> None:
    """给 auto-select.py 用。只含策略和计数，绝不含节点密钥。"""
    providers_meta = {}
    for entry in policy.get("provider_order") or []:
        src = str(entry.get("source") or "")
        providers_meta["main" if src == "" else src] = {
            "name": entry.get("label") or src or "内联",
            "source": src,
        }
    manifest = {
        "generated_at": iso_now(),
        "policy_version": policy.get("version", 1),
        "group_name": policy["group_name"],
        "region_order": list(policy["region_order"]),
        "region_fallback": policy["region_fallback"],
        "health_group_suffix": policy["health_group_suffix"],
        "selector": policy.get("selector") or {},
        "provider_order": policy.get("provider_order") or [],
        "exclude_name_patterns": policy.get("exclude_name_patterns") or [],
        "node_count": len(proxies),
        "regions": regions,
        "providers": providers_meta,
    }
    atomic_write(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", 0o644)


# --------------------------------------------------------------------------
# lock
# --------------------------------------------------------------------------
def acquire_lock():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    fh = open(LOCK_FILE, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        return None
    fh.write(str(os.getpid()))
    fh.flush()
    return fh


def release_lock(fh) -> None:
    try:
        fcntl.flock(fh, fcntl.LOCK_UN)
    finally:
        fh.close()


# --------------------------------------------------------------------------
# mihomo 校验
# --------------------------------------------------------------------------
def mihomo_test(candidate: Path):
    if not MIHOMO_BIN.is_file():
        raise ManagerError(f"找不到 mihomo 二进制: {MIHOMO_BIN}")
    proc = subprocess.run(
        [str(MIHOMO_BIN), "-t", "-d", str(CONF_DIR), "-f", str(candidate)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    # 只认这两个信号；cache 文件 timeout 之类的噪声不影响判定。
    return (proc.returncode == 0 and "test is successful" in output), output


# --------------------------------------------------------------------------
# 子命令
# --------------------------------------------------------------------------
def cmd_seed(args) -> int:
    source = Path(args.source).expanduser() if args.source else LIVE
    if not source.is_file():
        raise ManagerError(f"找不到源配置: {source}")
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("proxies"), list):
        raise ManagerError(f"{source} 不像 mihomo full-config（缺 proxies 列表）")
    if BASE_FILE.exists() and not args.force:
        raise ManagerError(f"{BASE_FILE} 已存在；要覆盖请加 --force")
    atomic_write(BASE_FILE, yaml.safe_dump(data, allow_unicode=True, sort_keys=False), 0o600)
    os.chmod(BASE_FILE, 0o600)
    print(f"seed 完成: {source} -> {BASE_FILE}")
    print(f"  顶层策略键 {len(data) - 2} 个；基础节点 {len(data['proxies'])} 个")
    print("  这个文件含节点密钥，已被 .gitignore 挡住，不要提交。")
    return 0


def cmd_reconcile(args) -> int:
    policy = load_policy()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    lock = acquire_lock()
    if lock is None:
        print("另一个 reconcile 正在运行，本次跳过（不阻塞、不破坏）")
        return 0

    started = time.time()
    previous = read_state()
    try:
        base_cfg, base_proxies = load_base(policy)
        secret = api_secret(base_cfg)

        extra = [p for p in list_inputs() if p != BASE_FILE]
        _, stable = settle(extra)
        if extra and not stable:
            raise ManagerError("输入文件仍在变化（疑似正在复制），本次跳过")

        sources = [(str(BASE_FILE), base_proxies)]
        inputs_meta = [
            {
                "path": str(BASE_FILE),
                "sha256": file_sha256(BASE_FILE),
                "proxies": len(base_proxies),
                "schema": "seed-base",
            }
        ]
        for path in extra:
            proxies, schema = read_input(path)
            sources.append((str(path), proxies))
            inputs_meta.append(
                {
                    "path": str(path),
                    "sha256": file_sha256(path),
                    "proxies": len(proxies),
                    "schema": schema,
                }
            )

        proxies, conflicts, fixes, excluded = merge_proxies(sources, policy)
        if not proxies:
            raise ManagerError("合并后没有任何节点，拒绝生成空配置")

        regions: dict = {}
        for p in proxies:
            r = region_of(p["name"], policy)
            regions[r] = regions.get(r, 0) + 1

        cfg = build_config(base_cfg, proxies, policy)
        text = render_config(cfg, policy)

        atomic_write(CANDIDATE, text, 0o600)
        ok, output = mihomo_test(CANDIDATE)
        if not ok:
            raise ManagerError("candidate 未通过 mihomo -t:\n" + tail(output))

        base_state = {
            "last_attempt_at": iso_now(),
            "last_success_at": previous.get("last_success_at"),
            "active_config_nodes": len(proxies),
            "regions": regions,
            "inputs": inputs_meta,
            "normalized": {"fingerprint_fixed": sum(1 for f in fixes if "fingerprint" in f["fix"])},
            "conflicts": conflicts,
            "excluded": excluded,
            "last_error": None,
            "duration_s": round(time.time() - started, 2),
        }

        if args.dry_run:
            state = dict(base_state, status="dry-run",
                         active_config_sha256=hashlib.sha256(text.encode()).hexdigest())
            write_state(state)
            print(f"[dry-run] candidate 校验通过：{len(proxies)} 个节点，未改动 live")
            print(f"  地区分布 : {regions}")
            print(f"  冲突重命名: {len(conflicts)}   fingerprint 规范化: {state['normalized']['fingerprint_fixed']}")
            print(f"  排除伪节点: {len(excluded)}")
            print(f"  candidate: {CANDIDATE}  sha256={state['active_config_sha256'][:16]}")
            return 0

        backup = backup_live(policy)
        previous_sha = file_sha256(LIVE) if LIVE.is_file() else None
        atomic_write(LIVE, text, 0o600)
        new_sha = file_sha256(LIVE)

        try:
            code = reload_live(secret)
            if code not in (200, 204):
                raise ManagerError(f"reload 返回 HTTP {code}")
            ok, detail = post_check(secret, len(proxies), policy["group_name"])
            if not ok:
                raise ManagerError("post-check 失败: " + detail)
        except Exception as exc:
            restore_from(backup, secret)
            raise ManagerError(
                f"替换后 reload/post-check 失败，已回滚到旧配置（{previous_sha[:16] if previous_sha else 'none'}）: {exc}"
            ) from exc

        state = dict(base_state, status="ok", last_success_at=iso_now(), active_config_sha256=new_sha)
        write_state(state)
        write_manifest(policy, proxies, regions)
        print(f"reconcile 完成：{len(proxies)} 个节点 / {len(regions)} 个地区 / {state['duration_s']}s")
        print(f"  live    : {LIVE}  sha256={new_sha[:16]}")
        print(f"  备份    : {backup}")
        print(f"  重命名  : {len(conflicts)}   fingerprint 规范化: {state['normalized']['fingerprint_fixed']}   排除: {len(excluded)}")
        return 0

    except ManagerError as exc:
        state = dict(previous, status="failed", last_attempt_at=iso_now(),
                     last_error=str(exc), duration_s=round(time.time() - started, 2))
        write_state(state)
        print(f"ERROR: {exc}", file=sys.stderr)
        print("live 配置未被改动。", file=sys.stderr)
        return 1
    finally:
        release_lock(lock)


def cmd_validate(args) -> int:
    return cmd_reconcile(argparse.Namespace(dry_run=True))


def cmd_status(args) -> int:
    state = read_state()
    if not state:
        print("还没有任何 reconcile 记录。先跑：mihomo_manager.py seed && mihomo_manager.py reconcile")
        return 0
    print(f"状态        : {state.get('status')}")
    print(f"最后成功    : {state.get('last_success_at')}")
    print(f"最后尝试    : {state.get('last_attempt_at')}   耗时 {state.get('duration_s')}s")
    print(f"live 节点数 : {state.get('active_config_nodes')}")
    print(f"记录 sha256 : {(state.get('active_config_sha256') or '')[:16]}")
    print(f"地区分布    : {state.get('regions')}")
    print(f"规范化      : {state.get('normalized')}")
    print(f"冲突重命名  : {len(state.get('conflicts') or [])}")
    print(f"排除伪节点  : {len(state.get('excluded') or [])}")
    print(f"最后错误    : {state.get('last_error')}")
    for item in state.get("inputs") or []:
        print(f"  输入 {item.get('schema'):12} {item.get('proxies'):>3} 个  {(item.get('sha256') or '')[:12]}  {item.get('path')}")
    if LIVE.is_file():
        mode = oct(LIVE.stat().st_mode & 0o777)
        print(f"live 实际   : sha256={file_sha256(LIVE)[:16]}  权限={mode}")
    if BACKUP_DIR.is_dir():
        backups = sorted(BACKUP_DIR.glob("config.*.yaml"))
        print(f"备份        : {len(backups)} 个，最近 {backups[-1].name if backups else '-'}")
    return 0


def cmd_rollback(args) -> int:
    backups = sorted(BACKUP_DIR.glob("config.*.yaml")) if BACKUP_DIR.is_dir() else []
    if args.list:
        for path in backups:
            print(path)
        return 0
    if not backups:
        raise ManagerError("没有备份可回滚")
    target = Path(args.to).expanduser() if args.to else backups[-1]
    if not target.is_file():
        raise ManagerError(f"指定备份不存在: {target}")
    secret = ""
    if LIVE.is_file():
        secret = api_secret(yaml.safe_load(LIVE.read_text(encoding="utf-8")) or {})
    shutil.copy2(target, LIVE)
    os.chmod(LIVE, 0o600)
    reload_live(secret)
    print(f"已回滚到 {target}")
    print(f"  live sha256={file_sha256(LIVE)[:16]}")
    return 0


def cmd_install_units(args) -> int:
    if not UNITS_DIR.is_dir():
        raise ManagerError(f"找不到 units 目录: {UNITS_DIR}")
    SYSTEMD_USER_DIR.mkdir(parents=True, exist_ok=True)
    installed = []
    for src in sorted(UNITS_DIR.iterdir()):
        if src.suffix not in (".service", ".path", ".timer"):
            continue
        dest = SYSTEMD_USER_DIR / src.name
        shutil.copy2(src, dest)
        installed.append(dest.name)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    print("已安装 systemd units（默认不 enable，避免自动动 live 配置）：")
    for name in installed:
        print(f"  {SYSTEMD_USER_DIR / name}")
    print("要启用自动 reconcile：systemctl --user enable --now mihomo-reconcile.path")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mihomo-manager",
        description=(
            "管理 mihomo 的节点来源。把订阅文件丢进 "
            f"{SOURCES_DIR}，它会按 policy.yaml 合并、校验、原子替换 live config 并热重载。"
        ),
        epilog=(
            "典型用法：\n"
            "  1. 第一次：mihomo_manager.py seed        （把当前能用的配置存成私密 base）\n"
            "  2. 加订阅：cp 新订阅.yaml ~/.config/mihomo/sources/\n"
            "  3. 应用  ：mihomo_manager.py reconcile   （失败会自动回滚，不动现网）\n"
            "  4. 看状态：mihomo_manager.py status\n"
            "  5. 出问题：mihomo_manager.py rollback\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("seed", help="从当前 live config 建立私密 base（只做一次）")
    p.add_argument("--from", dest="source", default=None, help="源配置路径，默认当前 live config")
    p.add_argument("--force", action="store_true", help="覆盖已存在的 base")
    p.set_defaults(func=cmd_seed)

    p = sub.add_parser("validate", help="只解析+合并+生成 candidate 并校验，完全不碰 live")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser(
        "reconcile",
        help="完整流程：合并→校验→备份→原子替换→热重载→post-check（失败自动回滚）",
    )
    p.add_argument("--dry-run", action="store_true", help="只生成 candidate 并校验，不碰 live")
    p.set_defaults(func=cmd_reconcile)

    p = sub.add_parser("status", help="看上次结果、节点数、地区分布、错误")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("rollback", help="用最近的备份恢复 live 并热重载")
    p.add_argument("--list", action="store_true", help="只列出可用备份")
    p.add_argument("--to", default=None, help="指定备份文件路径")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("install-units", help="把 units/ 安装到 ~/.config/systemd/user（不自动 enable）")
    p.set_defaults(func=cmd_install_units)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 2
    try:
        return args.func(args)
    except ManagerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
