#!/usr/bin/env python3
"""猎聘批量投递 v5.1:从 hunt JSON → user-apply-job;限流自适应;成功形态待实测。

用法:
  python3 apply_batch.py --hunt /tmp/hunt.json --max 30 [--dry-run]
  python3 apply_batch.py --hunt /tmp/hunt.json --max 10 --tracker-file ~/notes/apply-list.json

注意:
  - 成功判定标为 OK_UNVERIFIED(未见过真实成功响应样本,勿当绝对成功)
  - 连续限流 2 次则停手,避免自我续杯
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from liepin_common import LiepinClient, load_env_merged  # noqa: E402


def extract_jobs(hunt: dict) -> list[dict]:
    rows = hunt.get("rows") or hunt.get("companies") or hunt.get("results") or []
    jobs = []
    for r in rows:
        for j in r.get("jobs") or []:
            jid = j.get("jobId") or j.get("job_id") or j.get("id")
            kind = j.get("jobKind") or j.get("jobType") or j.get("job_kind") or ""
            if jid is None or jid == "":
                continue
            jobs.append(
                {
                    "jobId": jid,
                    "jobKind": str(kind),
                    "jobName": j.get("jobName") or j.get("title") or "",
                    "company": r.get("company", ""),
                    "salary": j.get("salary", ""),
                    "dist_m": r.get("dist_m", ""),
                }
            )
    seen, uniq = set(), []
    for j in jobs:
        key = str(j["jobId"])
        if key not in seen:
            seen.add(key)
            uniq.append(j)
    return uniq


def maybe_tracker_mark(tracker_file: str, job: dict, status: str) -> None:
    """可选:把成功/未验证条目写入 apply_tracker 清单(懒加载调用)。"""
    if not tracker_file:
        return
    try:
        import apply_tracker as at
    except ImportError:
        print("  !! 无法 import apply_tracker,跳过 tracker 写入", file=sys.stderr)
        return
    data = at.load(tracker_file)
    # 按 company+job 找或新建
    found = None
    for i in data.get("items") or []:
        if i.get("company") == job["company"] and i.get("job") == job["jobName"]:
            found = i
            break
    if not found:
        found = {
            "id": __import__("uuid").uuid4().hex[:10],
            "company": job["company"],
            "job": job["jobName"],
            "link": "",
            "dist_m": job.get("dist_m"),
            "status": "wishlist",
            "score": None,
            "note": "",
            "source": "apply_batch",
            "job_id": job["jobId"],
            "job_kind": job["jobKind"],
            "applied_at": None,
            "next_check": None,
            "created_at": at.now_ts(),
            "updated_at": at.now_ts(),
        }
        data.setdefault("items", []).append(found)
    found["job_id"] = job["jobId"]
    found["job_kind"] = job["jobKind"]
    if status in ("OK_UNVERIFIED",):
        found["status"] = "applied"
        at.stamp_applied(found, force=True)
        found["note"] = ((found.get("note") or "") + " [batch OK_UNVERIFIED]").strip()
    found["updated_at"] = at.now_ts()
    at.save(tracker_file, data)


def main() -> None:
    ap = argparse.ArgumentParser(description="猎聘批量投递 v5(限流自适应)")
    ap.add_argument("--hunt", required=True, help="geo_job_hunt.py --format json 输出")
    ap.add_argument("--max", type=int, default=100, help="最多投几个(去重后切片)")
    ap.add_argument("--sleep", type=float, default=2.0, help="基础间隔秒(默认 2.0;实测触发点 ~1.2s 持续,勿低于 1.5)")
    ap.add_argument("--backoff", type=float, default=120.0, help="限流退避秒(默认 120)")
    ap.add_argument("--dry-run", action="store_true", help="只统计不投递")
    ap.add_argument("--out", default="/tmp/apply_report.json", help="结果报告路径")
    ap.add_argument("--env", default="", help="显式 .env")
    ap.add_argument("--tracker-file", default="", help="可选:同步到 apply_tracker JSON")
    ap.add_argument("--allow-empty-kind", action="store_true", help="允许空 jobKind(不推荐;默认缺 jobKind 则跳过)")
    args = ap.parse_args()

    with open(args.hunt) as f:
        hunt = json.load(f)
    uniq = extract_jobs(hunt)
    missing_kind = [j for j in uniq if not j["jobKind"]]
    print(
        f"hunt 去重岗位 {len(uniq)} 个"
        + (f"(其中缺 jobKind {len(missing_kind)})" if missing_kind else "")
    )
    if not args.allow_empty_kind:
        uniq = [j for j in uniq if j["jobKind"]]
        print(f"过滤后可投 {len(uniq)} 个(缺 jobKind 已跳过;--allow-empty-kind 可放开)")

    if args.dry_run:
        preview = {
            "dry_run": True,
            "count": len(uniq[: args.max]),
            "sample": uniq[: min(5, args.max)],
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        parent = os.path.dirname(args.out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(preview, f, ensure_ascii=False, indent=2)
        print(f"dry-run,未投递;预览已写 {args.out}")
        return

    env = load_env_merged(args.env)
    tok = os.environ.get("MCP_LIEPIN_API_KEY") or env.get("MCP_LIEPIN_API_KEY", "")
    if not tok:
        sys.exit("缺少 MCP_LIEPIN_API_KEY")
    if not uniq:
        sys.exit("没有可投递的岗位(检查 hunt 是否含 jobId/jobKind)")

    client = LiepinClient(
        tok,
        sleep=args.sleep,
        backoff_sec=args.backoff,
        max_backoff_retries=0,  # apply 路径自行控制重试
    )

    results, rate_hits, successes, failures, unverified = [], 0, 0, 0, 0
    target = uniq[: args.max]
    for i, j in enumerate(target):
        print(
            f"[{i+1}/{len(target)}] {j['jobName'][:28]:28s} {j['company'][:20]:20s} "
            f"jobId={j['jobId']} kind={j['jobKind']}"
        )
        if client.consecutive_rate_limits >= 2:
            print("  !! 连续限流 ≥2,停止批量投递")
            break
        cls, raw = client.apply_job(j["jobId"], j["jobKind"])
        if cls == "RATE_LIMITED":
            rate_hits += 1
            print(f"    !! 限流,退避 {args.backoff:.0f}s 重试一次...")
            time.sleep(args.backoff)
            cls, raw = client.apply_job(j["jobId"], j["jobKind"])
        status = cls
        if cls == "OK_UNVERIFIED":
            unverified += 1
            successes += 1  # 计数上算「未报错」,报告里仍写 OK_UNVERIFIED
            maybe_tracker_mark(args.tracker_file, j, cls)
        elif cls == "AUTH":
            failures += 1
            print("    !! token 失效(401),停止")
            results.append(
                {
                    "jobId": j["jobId"],
                    "jobName": j["jobName"],
                    "company": j["company"],
                    "salary": j["salary"],
                    "dist_m": j["dist_m"],
                    "status": status,
                    "raw": raw[:200],
                }
            )
            break
        elif cls == "RATE_LIMITED":
            failures += 1
            status = "RATE_LIMITED(重试后仍限)"
        else:
            failures += 1
            print(f"    !! {cls}: {raw[:80]}")
        results.append(
            {
                "jobId": j["jobId"],
                "jobName": j["jobName"],
                "company": j["company"],
                "salary": j["salary"],
                "dist_m": j["dist_m"],
                "status": status,
                "raw": raw[:300],
            }
        )
        client._pace()

    rep = {
        "applied_unverified": unverified,
        "failed": failures,
        "rate_limit_hits": rate_hits,
        "note": "成功形态待实测;OK_UNVERIFIED=无限流/显式失败词,不保证平台已接受投递",
        "results": results,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    parent = os.path.dirname(args.out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(
        f"\n=== 完成:未验证通过 {unverified} / 失败 {failures} / 限流触发 {rate_hits} 次"
    )
    print(f"报告: {args.out}")
    if client.auth_failed:
        sys.exit(2)
    if client.consecutive_rate_limits >= 2:
        sys.exit(3)


if __name__ == "__main__":
    main()
