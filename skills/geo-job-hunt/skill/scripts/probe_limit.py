#!/usr/bin/env python3
"""猎聘限流探测 v5(静默看门狗 + 状态文件)。

语义:
  - 仍限流 → stdout 空,exit 0(cron no_agent 不打扰);写入 state.last_limited_at
  - 已恢复 → 打印一条消息(含距上次限流多久,若可知);exit 0
  - 找不到 key → 打印警告;exit 1
  - 网络/解析错误 → 默认 stdout 空(不误报恢复);累计到 --net-warn-after 次才打印一行;
    state 记录 last_error;exit 0(避免 cron 误当恢复),除非 --strict-net

用法:
  python3 probe_limit.py
  python3 probe_limit.py --state ~/.agents/skills/geo-job-hunt/logs/probe_state.json

PROD-FIX: Hermes cron 用的是 profiles/writing/scripts/probe_limit.py 实体副本,
合入真源后须手动同步该副本,否则 cron 继续跑旧逻辑。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from liepin_common import (  # noqa: E402
    http_json,
    is_rate_limited_text,
    load_env_merged,
    LIEPIN_MCP,
)

DEFAULT_STATE = os.path.expanduser(
    "~/.agents/skills/geo-job-hunt/logs/probe_state.json"
)


def load_state(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: str, state: dict) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def fmt_ago(ts: str | None) -> str:
    if not ts:
        return "未知(无上次限流记录)"
    try:
        # accept %Y-%m-%dT%H:%M:%S
        t = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
        mins = int((time.time() - t) / 60)
        if mins < 60:
            return f"约 {mins} 分钟前"
        return f"约 {mins/60:.1f} 小时前"
    except Exception:
        return f"记录于 {ts}"


def main() -> None:
    ap = argparse.ArgumentParser(description="猎聘限流静默看门狗 v5")
    ap.add_argument("--env", default="", help="显式 .env")
    ap.add_argument("--state", default=DEFAULT_STATE, help="状态 JSON 路径")
    ap.add_argument(
        "--net-warn-after",
        type=int,
        default=3,
        help="连续网络失败多少次后打印一行警告(默认 3)",
    )
    ap.add_argument(
        "--strict-net",
        action="store_true",
        help="网络错误也打印并 exit 4(默认静默累计)",
    )
    args = ap.parse_args()

    env = load_env_merged(args.env)
    tok = os.environ.get("MCP_LIEPIN_API_KEY") or env.get("MCP_LIEPIN_API_KEY", "")
    if not tok:
        print("⚠️ 猎聘限流探测:找不到 MCP_LIEPIN_API_KEY(环境变量或 .env)")
        sys.exit(1)

    state = load_state(args.state)
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search-jobs",
                "arguments": {
                    "companyName": "同花顺",
                    "address": "杭州",
                    "page": 0,
                },
            },
        }
    ).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-user-token": tok,
    }

    try:
        d = http_json(LIEPIN_MCP, data=body, headers=headers, timeout=25)
    except RuntimeError as e:
        msg = str(e)
        if msg.startswith("RATE_LIMITED") or is_rate_limited_text(msg):
            state["last_limited_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            state["last_status"] = "limited"
            state["consecutive_net_errors"] = 0
            save_state(args.state, state)
            return
        # 网络/其它
        n = int(state.get("consecutive_net_errors") or 0) + 1
        state["consecutive_net_errors"] = n
        state["last_error"] = msg[:300]
        state["last_status"] = "net_error"
        save_state(args.state, state)
        if args.strict_net or n >= args.net_warn_after:
            print(
                f"⚠️ 猎聘限流探测:网络/调用异常×{n}: {msg[:120]}"
            )
            if args.strict_net:
                sys.exit(4)
        return

    txt = ""
    if "error" in d:
        txt = json.dumps(d["error"], ensure_ascii=False)
    else:
        content = (d.get("result") or {}).get("content") or []
        if content:
            txt = content[0].get("text", "")

    if is_rate_limited_text(txt):
        state["last_limited_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        state["last_status"] = "limited"
        state["consecutive_net_errors"] = 0
        save_state(args.state, state)
        return

    # 恢复
    ago = fmt_ago(state.get("last_limited_at"))
    prev = state.get("last_status")
    state["last_recovered_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    state["last_status"] = "ok"
    state["consecutive_net_errors"] = 0
    save_state(args.state, state)
    extra = f";此前状态={prev}" if prev else ""
    print(
        f"✅ 猎聘限流已恢复({time.strftime('%Y-%m-%d %H:%M')})!"
        f"距上次限流 {ago}{extra}。"
        f"可以跑 geo-job-hunt 收集 + apply_batch。"
    )


if __name__ == "__main__":
    main()
