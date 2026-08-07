#!/usr/bin/env python3
"""猎聘/环境公共小工具(geo-job-hunt v5)。仅 stdlib。

供 geo_job_hunt / apply_batch / probe_limit 复用,避免三份漂移。
"""
from __future__ import annotations

import glob
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

LIEPIN_MCP = "https://open-agent.liepin.com/mcp/user"
RATE_LIMIT_MARKERS = (
    "请求过于频繁",
    "请稍后再试",
    "too many requests",
    "rate limit",
    "RATE_LIMIT",
)
# 官方文档 60/min;实测疑似另有更长窗口——软上限只防「分钟级爆冲」
LIEPIN_RPM_SOFT_CAP = 50


def env_candidates(extra: str = "") -> list[str]:
    paths: list[str] = []
    if extra:
        paths.append(os.path.expanduser(extra))
    paths.append(os.path.expanduser("~/.hermes/.env"))
    paths.append(os.path.join(os.getcwd(), ".env"))
    paths.extend(sorted(glob.glob(os.path.expanduser("~/.hermes/profiles/*/.env"))))
    # 去重保序
    out, seen = [], set()
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def load_env_file(path: str) -> dict[str, str]:
    env: dict[str, str] = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return env


def load_env_merged(extra: str = "") -> dict[str, str]:
    """合并 .env。后者覆盖前者(profiles 字母序,writing 通常最后)。
    环境变量在调用方用 os.environ.get 再覆盖。
    """
    env: dict[str, str] = {}
    for p in env_candidates(extra):
        env.update(load_env_file(p))
    return env


def parse_maybe_sse_json(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        raise RuntimeError("空响应")
    if raw.startswith("{") or raw.startswith("["):
        return json.loads(raw)
    payloads = []
    for line in raw.splitlines():
        if line.startswith("data:"):
            payloads.append(line[5:].strip())
    if not payloads:
        raise RuntimeError(f"无法解析响应(非 JSON/SSE): {raw[:200]}")
    return json.loads(payloads[-1])


def http_json(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 25,
) -> Any:
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:500]
        if e.code == 429:
            raise RuntimeError(f"RATE_LIMITED: HTTP 429: {body}") from e
        raise RuntimeError(f"HTTP {e.code} {url.split('?', 1)[0]}: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误 {url.split('?', 1)[0]}: {e.reason}") from e
    return parse_maybe_sse_json(raw)


def is_rate_limited_text(txt: str) -> bool:
    if not txt:
        return False
    low = txt.lower()
    for m in RATE_LIMIT_MARKERS:
        if m.lower() in low or m in txt:
            return True
    return False


def classify_business_payload(txt: str) -> str:
    """粗分类业务文本。apply 成功形态待实测——不编造字段契约。

    返回: RATE_LIMITED | AUTH | FAIL | OK_UNVERIFIED | EMPTY
    """
    if not txt or not txt.strip():
        return "EMPTY"
    if is_rate_limited_text(txt):
        return "RATE_LIMITED"
    if "401" in txt or "未授权" in txt or "Unauthorized" in txt:
        return "AUTH"
    try:
        d = json.loads(txt)
    except json.JSONDecodeError:
        # 非 JSON 且无限流词 → 未知
        return "OK_UNVERIFIED"
    blob = json.dumps(d, ensure_ascii=False)
    if is_rate_limited_text(blob):
        return "RATE_LIMITED"
    # 常见失败暗示(保守:宁可标 FAIL 也不要假成功)
    fail_hints = ("失败", "错误", "不允许", "无法投递", '"error"', '"errMsg"', '"errmsg"')
    if any(h in blob for h in fail_hints):
        # 但「错误码 0」类可能误伤——仅当同时没有明显成功词时
        if not any(s in blob for s in ("成功", '"ok":true', '"success":true', '"flag":true')):
            return "FAIL"
    return "OK_UNVERIFIED"


class LiepinClient:
    """带软 RPM 上限 + 自适应间隔 + 限流识别的 MCP 调用客户端。"""

    def __init__(
        self,
        token: str,
        sleep: float = 2.0,
        *,
        min_sleep: float | None = None,
        max_sleep: float = 8.0,
        backoff_sec: float = 90.0,
        max_backoff_retries: int = 1,
    ):
        """稳态间隔默认 2.0s(实测触发点 ~1.2s 持续,v1.3s 仅 8% 裕量 → v5.1.1 提到 2.0s,67% 裕量)。
        自适应只负责「限流后抬升、随后缓慢回落」,回落地板 = min_sleep,不再向触发点加速。"""
        self.token = token
        self.sleep = sleep
        self.min_sleep = min_sleep if min_sleep is not None else sleep
        self.max_sleep = max_sleep
        self.backoff_sec = backoff_sec
        self.max_backoff_retries = max_backoff_retries
        self.n_calls = 0
        self._window_start = time.time()
        self.last_error: str | None = None
        self.auth_failed = False
        self.rate_limited = False
        self.rate_limit_hits = 0
        self.consecutive_rate_limits = 0

    def _throttle_rpm(self) -> None:
        if self.n_calls >= LIEPIN_RPM_SOFT_CAP:
            elapsed = time.time() - self._window_start
            if elapsed < 60:
                wait = 60 - elapsed + 0.5
                print(f"  .. RPM 软上限,等待 {wait:.0f}s", file=sys_stderr())
                time.sleep(wait)
            self.n_calls = 0
            self._window_start = time.time()

    def _pace(self) -> None:
        time.sleep(self.sleep)

    def on_success(self) -> None:
        self.consecutive_rate_limits = 0
        self.rate_limited = False
        # 成功则缓慢回落(0.97,不向触发点急加速);不低于 min_sleep
        self.sleep = max(self.min_sleep, self.sleep * 0.97)

    def on_rate_limit(self) -> None:
        self.rate_limited = True
        self.rate_limit_hits += 1
        self.consecutive_rate_limits += 1
        self.sleep = min(self.max_sleep, max(self.sleep * 1.8, self.min_sleep * 2))

    def call(self, tool: str, arguments: dict, *, _retried: bool = False) -> Any:
        self._throttle_rpm()
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool, "arguments": arguments},
            }
        ).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "x-user-token": self.token,
        }
        try:
            d = http_json(LIEPIN_MCP, data=body, headers=headers, timeout=30)
        except RuntimeError as e:
            msg = str(e)
            self.last_error = msg
            if "401" in msg or "Unauthorized" in msg.lower():
                self.auth_failed = True
            if msg.startswith("RATE_LIMITED") or "429" in msg:
                self.on_rate_limit()
                if not _retried and self.max_backoff_retries > 0:
                    print(
                        f"  .. 猎聘限流(HTTP),退避 {self.backoff_sec:.0f}s 后重试",
                        file=sys_stderr(),
                    )
                    time.sleep(self.backoff_sec)
                    return self.call(tool, arguments, _retried=True)
            raise
        self.n_calls += 1
        if "error" in d:
            err = d["error"]
            msg = json.dumps(err, ensure_ascii=False)[:300]
            self.last_error = msg
            if "401" in msg:
                self.auth_failed = True
            if is_rate_limited_text(msg):
                self.on_rate_limit()
                raise RuntimeError(f"RATE_LIMITED: {msg}")
            raise RuntimeError(f"猎聘 MCP error: {msg}")
        content = d.get("result", {}).get("content", [])
        if not content:
            self.on_success()
            return {}
        txt = content[0].get("text", "{}")
        if is_rate_limited_text(txt):
            self.on_rate_limit()
            self.last_error = "RATE_LIMITED: 请求过于频繁，请稍后再试"
            if not _retried and self.max_backoff_retries > 0:
                print(
                    f"  .. 猎聘限流(业务体),退避 {self.backoff_sec:.0f}s "
                    f"重试(hits={self.rate_limit_hits}, sleep→{self.sleep:.1f}s)",
                    file=sys_stderr(),
                )
                time.sleep(self.backoff_sec)
                return self.call(tool, arguments, _retried=True)
            raise RuntimeError(self.last_error)
        self.on_success()
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"raw": txt}

    def search_jobs(self, args: dict) -> list[dict]:
        payload = self.call("search-jobs", args)
        data = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(data, dict):
            return data.get("list") or []
        return []

    def apply_job(self, job_id: Any, job_kind: str) -> tuple[str, str]:
        """返回 (classify, raw_text)。成功形态待实测 → OK_UNVERIFIED。"""
        # schema: jobId number
        try:
            jid = int(job_id)
        except (TypeError, ValueError):
            return "FAIL", f"invalid jobId={job_id!r}"
        kind = str(job_kind or "").strip()
        if not kind:
            return "FAIL", "missing jobKind"
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "user-apply-job",
                    "arguments": {"jobId": jid, "jobKind": kind},
                },
            }
        ).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "x-user-token": self.token,
        }
        try:
            d = http_json(LIEPIN_MCP, data=body, headers=headers, timeout=30)
        except RuntimeError as e:
            msg = str(e)
            if msg.startswith("RATE_LIMITED") or is_rate_limited_text(msg):
                self.on_rate_limit()
                return "RATE_LIMITED", msg
            if "401" in msg:
                self.auth_failed = True
                return "AUTH", msg
            return "FAIL", msg
        self.n_calls += 1
        if "error" in d:
            msg = json.dumps(d["error"], ensure_ascii=False)
            if is_rate_limited_text(msg):
                self.on_rate_limit()
                return "RATE_LIMITED", msg
            if "401" in msg:
                self.auth_failed = True
                return "AUTH", msg
            return "FAIL", msg
        txt = (d.get("result", {}) or {}).get("content", [{}])[0].get("text", "")
        cls = classify_business_payload(txt)
        if cls == "RATE_LIMITED":
            self.on_rate_limit()
        elif cls in ("OK_UNVERIFIED",):
            self.on_success()
        elif cls == "AUTH":
            self.auth_failed = True
        return cls, txt


def sys_stderr():
    import sys

    return sys.stderr
