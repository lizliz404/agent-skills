#!/usr/bin/env python3
"""地理围栏找工作 v5:高德圈公司 ↔ 猎聘在招,支持正向/反向/增量/多格式输出。

仅依赖 Python stdlib。密钥自动发现(可用 --env 覆盖):
  AMAP_MAPS_API_KEY, MCP_LIEPIN_API_KEY

用法摘要:
  python3 geo_job_hunt.py forward --address 目标地址 --radius 3000
  python3 geo_job_hunt.py reverse --job "AI产品实习" --city 杭州 --address "..." --radius 3000
  python3 geo_job_hunt.py forward ... --state-file /tmp/geo-job.state.json --diff-only
  python3 geo_job_hunt.py forward ... --format html --out /tmp/jobs.html
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import math
import os
import re
import sys
import time
import urllib.parse
from typing import Any

# 同目录公共库
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from liepin_common import (  # noqa: E402
    LiepinClient,
    http_json,
    load_env_merged,
)

AMAP_AROUND = "https://restapi.amap.com/v3/place/around"
AMAP_GEO = "https://restapi.amap.com/v3/geocode/geo"
# 点名补搜默认清单(大厂名不含行业词,types 翻页常漏)
DEFAULT_EXTRA_KEYWORDS = (
    "阿里巴巴", "字节跳动", "同花顺", "钉钉", "vivo", "快手",
    "遥望", "中移", "BetterYeah", "斑头雁", "Rokid", "识度",
)

# 明显非办公实体噪音(不删传媒/广告,它们可能是真目标)
NOISE = (
    "驿站", "维修", "餐饮", "食堂", "酒店", "物业", "装饰", "工程", "贸易",
    "进出口", "人力资源", "暖通", "会展", "健康", "美容", "电梯", "书院",
    "门店", "停车场", "充电站", "快递", "洗衣", "超市", "便利店",
)

CITY_PREFIXES = (
    "杭州", "浙江", "深圳市", "深圳", "上海", "广州", "北京", "余杭", "西湖",
)


# ---------------------------------------------------------------------------
# geo helpers
# ---------------------------------------------------------------------------

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def parse_loc(loc: str) -> tuple[float, float] | None:
    if not loc or "," not in loc:
        return None
    try:
        lon, lat = loc.split(",", 1)
        return float(lon), float(lat)
    except ValueError:
        return None


def geocode(address: str, key: str, city: str = "") -> tuple[str | None, str | None]:
    params = {"key": key, "address": address}
    if city:
        params["city"] = city
    q = urllib.parse.urlencode(params)
    d = http_json(f"{AMAP_GEO}?{q}")
    if str(d.get("status")) == "1" and d.get("geocodes"):
        g = d["geocodes"][0]
        return g.get("location"), g.get("formatted_address", address)
    return None, None


def amap_around(params: dict[str, str], key: str) -> dict:
    q = urllib.parse.urlencode({**params, "key": key})
    return http_json(f"{AMAP_AROUND}?{q}")


def is_company_poi(p: dict) -> bool:
    return (p.get("type") or "").startswith("公司企业")


def is_noise(name: str) -> bool:
    return any(n in name for n in NOISE)


def clean_name(name: str) -> str:
    n = re.sub(r"[（(].*?[)）]", "", name).strip()
    for prefix in CITY_PREFIXES:
        if n.startswith(prefix):
            n = n[len(prefix):]
    return n.strip() or name


def company_name_variants(name: str) -> list[str]:
    """去括号 / 去省市前缀 / 截断短名,去重保序。"""
    cand = clean_name(name)
    short = cand[:8] if len(cand) > 8 else cand
    shorter = cand[:4] if len(cand) > 4 else cand
    return list(dict.fromkeys([cand, name, short, shorter]))


# ---------------------------------------------------------------------------
# Amap: collect companies in radius
# ---------------------------------------------------------------------------

def collect_companies(
    loc: str,
    radius: int,
    key: str,
    extra_keywords: tuple[str, ...] = (),
    max_pages: int = 10,
) -> list[dict]:
    """types=170000|050000 分页 + 点名关键词补漏,按 POI id 去重。"""
    pois: dict[str, dict] = {}

    def ingest(plist: list) -> None:
        for p in plist:
            if not is_company_poi(p):
                continue
            pid = p.get("id")
            if not pid:
                continue
            loc_s = p.get("location") or ""
            if not parse_loc(loc_s):
                continue
            pois[pid] = {
                "id": pid,
                "name": p.get("name", ""),
                "type": p.get("type", ""),
                "address": p.get("address") or "",
                "location": loc_s,
            }

    for t in ("170000", "050000"):
        page = 1
        while page <= max_pages:
            try:
                d = amap_around(
                    {
                        "types": t,
                        "location": loc,
                        "radius": str(radius),
                        "offset": "25",
                        "page": str(page),
                    },
                    key,
                )
            except RuntimeError as e:
                print(f"  !! 高德 types={t} page={page}: {e}", file=sys.stderr)
                break
            if str(d.get("status")) != "1":
                print(
                    f"  !! 高德 types={t} status={d.get('status')} info={d.get('info')}",
                    file=sys.stderr,
                )
                break
            plist = d.get("pois") or []
            ingest(plist)
            if len(plist) < 25:
                break
            page += 1
            time.sleep(0.25)

    for kw in extra_keywords:
        if not kw.strip():
            continue
        try:
            d = amap_around(
                {
                    "keywords": kw.strip(),
                    "location": loc,
                    "radius": str(radius),
                    "offset": "25",
                    "page": "1",
                },
                key,
            )
        except RuntimeError:
            continue
        if str(d.get("status")) == "1":
            ingest(d.get("pois") or [])
        time.sleep(0.25)

    return list(pois.values())


# ---------------------------------------------------------------------------
# Liepin: company search helpers (client in liepin_common)
# ---------------------------------------------------------------------------

def search_company_jobs(
    client: LiepinClient,
    company: str,
    *,
    job_name: str,
    city: str,
    work_experience: str = "",
    edu_level: str = "",
    salary_floor: int | None = None,
    salary_cap: int | None = None,
    salary_kind: str = "",
) -> list[dict]:
    base: dict[str, Any] = {
        "companyName": company,
        "address": city,
        "page": 0,
    }
    if job_name:
        base["jobName"] = job_name
    if work_experience:
        base["workExperience"] = work_experience
    if edu_level:
        base["eduLevel"] = edu_level
    if salary_floor is not None:
        base["salaryFloor"] = str(salary_floor)  # schema: string
    if salary_cap is not None:
        base["salaryCap"] = str(salary_cap)
    if salary_kind:
        base["salaryKind"] = salary_kind

    jobs: list[dict] = []
    for tryname in company_name_variants(company):
        if client.auth_failed:
            break
        if client.consecutive_rate_limits >= 2:
            print("  !! 连续限流 ≥2,停止本轮公司查询(疑似长窗口)", file=sys.stderr)
            break
        args = {**base, "companyName": tryname}
        try:
            jobs = client.search_jobs(args)
        except RuntimeError as e:
            print(f"  !! 猎聘 {tryname[:16]}: {e}", file=sys.stderr)
            jobs = []
            if client.auth_failed or "RATE_LIMITED" in str(e):
                break
        if jobs:
            break
        client._pace()
    return jobs


# ---------------------------------------------------------------------------
# resume keyword score (lightweight)
# ---------------------------------------------------------------------------

def resume_score(job: dict, keywords: list[str]) -> tuple[int, list[str]]:
    """简单关键词命中分:职位名 + 描述字段(若有)。返回 (score, hits)。"""
    blob = " ".join(
        str(job.get(k, ""))
        for k in ("jobName", "title", "jobDesc", "description", "duty", "require")
    )
    hits = [kw for kw in keywords if kw and kw.lower() in blob.lower()]
    return len(hits), hits


# ---------------------------------------------------------------------------
# modes
# ---------------------------------------------------------------------------

def run_forward(args: argparse.Namespace, amap_key: str, client: LiepinClient) -> list[dict]:
    if not args.location and not args.address:
        sys.exit("需要 --address 或 --location")
    if args.location:
        loc = args.location
        faddr = args.address or loc
    else:
        loc, faddr = geocode(args.address, amap_key, city=args.city)
        if not loc:
            sys.exit("地理编码失败")
    center = parse_loc(loc)
    if not center:
        sys.exit(f"无效坐标: {loc}")
    lon, lat = center
    print(f"[1/3] 坐标: {loc} ({faddr})")

    extra = tuple(k.strip() for k in (args.extra_keywords or "").split(",") if k.strip())
    if args.no_default_extra:
        keywords = extra
    else:
        keywords = tuple(dict.fromkeys([*DEFAULT_EXTRA_KEYWORDS, *extra]))

    companies = collect_companies(loc, args.radius, amap_key, extra_keywords=keywords)
    for c in companies:
        c["dist"] = round(haversine(lon, lat, *parse_loc(c["location"])))  # type: ignore
    companies.sort(key=lambda c: c["dist"])
    # 纠偏:先滤噪音再截断 max-companies
    companies = [c for c in companies if not is_noise(c["name"])]
    print(f"[2/3] 公司企业 POI(去噪后): {len(companies)} 家")

    job_re = re.compile(args.job, re.I) if args.job else None
    lp_jobname = args.job.split("|")[0] if args.job else ""
    resume_kws = [k.strip() for k in (args.resume_keywords or "").split("|") if k.strip()]

    print(f"[3/3] 猎聘批量查询(最多 {args.max_companies} 家)...")
    rows: list[dict] = []
    for c in companies[: args.max_companies]:
        if client.auth_failed:
            print("  !! 猎聘 token 失效(401)。请到 https://www.liepin.com/mcp/server 重新获取后写入 .env", file=sys.stderr)
            break
        if client.consecutive_rate_limits >= 2:
            print("  !! 连续限流,提前结束收集(避免自我续杯)", file=sys.stderr)
            break
        jobs = search_company_jobs(
            client,
            c["name"],
            job_name=lp_jobname,
            city=args.city,
            work_experience=args.work_experience,
            edu_level=args.edu_level,
            salary_floor=args.salary_floor,
            salary_cap=args.salary_cap,
            salary_kind=args.salary_kind,
        )
        client._pace()
        if job_re:
            hit = [j for j in jobs if job_re.search(j.get("jobName", "") or "")]
        else:
            hit = list(jobs)

        # 纠偏:默认只展示命中;--show-unmatched 才回退展示前 N 条
        if hit:
            shown = hit
            matched = True
        elif args.show_unmatched and jobs:
            shown = jobs[:3]
            matched = False
        else:
            shown = []
            matched = False

        if resume_kws:
            for j in shown:
                sc, hits = resume_score(j, resume_kws)
                j["_resume_score"] = sc
                j["_resume_hits"] = hits

        rows.append(
            {
                "mode": "forward",
                "company": c["name"],
                "company_id": c.get("id", ""),
                "dist_m": c["dist"],
                "address": c["address"],
                "location": c["location"],
                "jobs": shown,
                "total_jobs": len(jobs),
                "matched": matched,
                "in_radius": True,
            }
        )
        mark = "🔥" if matched and shown else ("·" if jobs else "✗")
        print(
            f"  {mark} {c['name'][:24]:24s} {c['dist']:5d}m  "
            f"在招 {len(jobs):2d} 展示 {len(shown)}"
        )
    return rows


def run_reverse(args: argparse.Namespace, amap_key: str, client: LiepinClient) -> list[dict]:
    """流程反向:猎聘按职位搜 → 对公司地址/名做高德地理编码 → 过滤半径。"""
    if args.location:
        loc = args.location
        faddr = args.address or loc
    else:
        loc, faddr = geocode(args.address, amap_key, city=args.city)
        if not loc:
            sys.exit("地理编码失败")
    center = parse_loc(loc)
    if not center:
        sys.exit(f"无效坐标: {loc}")
    lon, lat = center
    print(f"[1/3] 圆心: {loc} ({faddr}) 半径 {args.radius}m")

    lp_jobname = args.job.split("|")[0] if args.job else "实习"
    job_re = re.compile(args.job, re.I) if args.job else None
    resume_kws = [k.strip() for k in (args.resume_keywords or "").split("|") if k.strip()]

    print(f"[2/3] 猎聘按职位翻页(jobName={lp_jobname!r}, city={args.city})...")
    all_jobs: list[dict] = []
    for page in range(args.max_pages):
        if client.auth_failed:
            break
        if client.consecutive_rate_limits >= 2:
            print("  !! 连续限流,停止翻页", file=sys.stderr)
            break
        q: dict[str, Any] = {
            "jobName": lp_jobname,
            "address": args.city,
            "page": page,
        }
        if args.work_experience:
            q["workExperience"] = args.work_experience
        if args.edu_level:
            q["eduLevel"] = args.edu_level
        if args.salary_floor is not None:
            q["salaryFloor"] = str(args.salary_floor)
        if args.salary_cap is not None:
            q["salaryCap"] = str(args.salary_cap)
        if args.salary_kind:
            q["salaryKind"] = args.salary_kind
        if args.company:
            q["companyName"] = args.company
        try:
            batch = client.search_jobs(q)
        except RuntimeError as e:
            print(f"  !! page={page}: {e}", file=sys.stderr)
            break
        print(f"  page {page}: {len(batch)} 条")
        if not batch:
            break
        all_jobs.extend(batch)
        client._pace()

    if job_re:
        all_jobs = [j for j in all_jobs if job_re.search(j.get("jobName", "") or "")]

    # 按公司聚合
    by_co: dict[str, list[dict]] = {}
    for j in all_jobs:
        co = (j.get("compName") or j.get("companyName") or j.get("company") or "未知").strip()
        by_co.setdefault(co, []).append(j)
    print(f"[3/3] {len(all_jobs)} 岗位 / {len(by_co)} 家公司 → 高德验证距离...")

    rows: list[dict] = []
    geo_cache: dict[str, tuple[str | None, str | None]] = {}
    for co, jobs in by_co.items():
        # 优先用岗位自带地址字段
        sample = jobs[0]
        hint = (
            sample.get("compAddress")
            or sample.get("jobAddress")
            or sample.get("address")
            or sample.get("dqName")
            or ""
        )
        geo_key = f"{co}|{hint}|{args.city}"
        if geo_key not in geo_cache:
            # 先试 公司名+城市;再试 hint
            g_loc, g_addr = geocode(f"{args.city}{co}", amap_key, city=args.city)
            if not g_loc and hint:
                g_loc, g_addr = geocode(f"{args.city}{hint}", amap_key, city=args.city)
            geo_cache[geo_key] = (g_loc, g_addr)
            time.sleep(0.2)
        g_loc, g_addr = geo_cache[geo_key]
        dist = None
        in_radius = False
        if g_loc and parse_loc(g_loc):
            dist = round(haversine(lon, lat, *parse_loc(g_loc)))  # type: ignore
            in_radius = dist <= args.radius

        if args.require_in_radius and not in_radius:
            continue

        shown = jobs
        if resume_kws:
            for j in shown:
                sc, hits = resume_score(j, resume_kws)
                j["_resume_score"] = sc
                j["_resume_hits"] = hits
            shown = sorted(shown, key=lambda x: x.get("_resume_score", 0), reverse=True)

        rows.append(
            {
                "mode": "reverse",
                "company": co,
                "company_id": "",
                "dist_m": dist,
                "address": g_addr or hint or "",
                "location": g_loc or "",
                "jobs": shown[: args.max_jobs_per_company],
                "total_jobs": len(jobs),
                "matched": True,
                "in_radius": in_radius,
            }
        )
        mark = "✓" if in_radius else "·"
        dist_s = f"{dist}m" if dist is not None else "?"
        print(f"  {mark} {co[:24]:24s} {dist_s:>7s}  岗位 {len(jobs)}")

    rows.sort(key=lambda r: (not r["in_radius"], r["dist_m"] is None, r["dist_m"] or 10**9))
    return rows


# ---------------------------------------------------------------------------
# state / diff / output
# ---------------------------------------------------------------------------

def job_uid(company: str, job: dict) -> str:
    jid = str(job.get("jobId") or job.get("id") or "")
    name = job.get("jobName") or job.get("title") or ""
    return jid or f"{company}::{name}"


def flatten_job_keys(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for r in rows:
        for j in r.get("jobs") or []:
            uid = job_uid(r["company"], j)
            out[uid] = {
                "company": r["company"],
                "dist_m": r.get("dist_m"),
                "jobName": j.get("jobName") or j.get("title"),
                "salary": j.get("salary"),
                "workYears": j.get("workYears") or j.get("workExperience"),
                "link": j.get("jobLink") or j.get("link") or j.get("url") or "",
                "jobId": j.get("jobId") or j.get("id"),
                "jobKind": j.get("jobKind") or j.get("jobType") or "",
                "in_radius": r.get("in_radius"),
            }
    return out


def apply_diff(rows: list[dict], state_path: str, diff_only: bool) -> tuple[list[dict], dict]:
    prev: dict[str, dict] = {}
    if state_path and os.path.isfile(state_path):
        try:
            with open(state_path) as f:
                prev = json.load(f).get("jobs", {})
        except (json.JSONDecodeError, OSError) as e:
            print(f"  !! 读取 state 失败: {e}", file=sys.stderr)

    current = flatten_job_keys(rows)
    new_ids = set(current) - set(prev)
    gone_ids = set(prev) - set(current)
    meta = {
        "new_count": len(new_ids),
        "gone_count": len(gone_ids),
        "new_ids": sorted(new_ids),
        "gone_ids": sorted(gone_ids),
        "prev_count": len(prev),
        "curr_count": len(current),
    }
    print(f"[diff] 新增 {meta['new_count']} · 消失 {meta['gone_count']} · 当前 {meta['curr_count']}")

    if state_path:
        parent = os.path.dirname(state_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(
                {"updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "jobs": current},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"[diff] state 已写: {state_path}")

    if not diff_only:
        # 标注 is_new
        for r in rows:
            for j in r.get("jobs") or []:
                j["_is_new"] = job_uid(r["company"], j) in new_ids
        return rows, meta

    # 只保留含新岗位的行
    filtered = []
    for r in rows:
        new_jobs = [j for j in (r.get("jobs") or []) if job_uid(r["company"], j) in new_ids]
        if new_jobs:
            nr = dict(r)
            nr["jobs"] = new_jobs
            for j in new_jobs:
                j["_is_new"] = True
            filtered.append(nr)
    return filtered, meta


def safe_makedirs_for(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def render_md(rows: list[dict], meta: dict, args: argparse.Namespace) -> str:
    title = f"# 地理围栏找工作 v5 · {args.mode}: {args.address or args.location} · {args.radius}m"
    lines = [
        title,
        "",
        f"> 城市 {args.city} · 职位 `{args.job}` · {time.strftime('%Y-%m-%d %H:%M')}"
        + (f" · diff +{meta.get('new_count', 0)}/-{meta.get('gone_count', 0)}" if meta else ""),
        "",
        "| 公司 | 距离 | 半径内 | 在招 | 岗位 | 地址 |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        dist = f"{r['dist_m']}m" if r.get("dist_m") is not None else "?"
        inside = "Y" if r.get("in_radius") else "N"
        parts = []
        for j in (r.get("jobs") or [])[:4]:
            flag = "🆕" if j.get("_is_new") else ""
            score = j.get("_resume_score")
            sc = f",match{score}" if score is not None else ""
            parts.append(
                f"{flag}{j.get('jobName', '')}({j.get('salary', '')},"
                f"{j.get('workYears') or j.get('workExperience') or ''}{sc})"
            )
        js = " / ".join(parts) or ("无命中" if not r.get("matched") else "无")
        lines.append(
            f"| {r['company']} | {dist} | {inside} | {r.get('total_jobs', 0)} | {js} | "
            f"{(r.get('address') or '')[:28]} |"
        )
    return "\n".join(lines) + "\n"


def render_json(rows: list[dict], meta: dict, args: argparse.Namespace) -> str:
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "mode": args.mode,
        "address": args.address,
        "location": getattr(args, "location", ""),
        "radius": args.radius,
        "city": args.city,
        "job": args.job,
        "diff": meta,
        "rows": rows,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_html(rows: list[dict], meta: dict, args: argparse.Namespace) -> str:
    esc = html_lib.escape
    trs = []
    for r in rows:
        dist = f"{r['dist_m']}m" if r.get("dist_m") is not None else "?"
        jobs_html = "<br>".join(
            esc(
                f"{'🆕 ' if j.get('_is_new') else ''}{j.get('jobName', '')} · "
                f"{j.get('salary', '')} · {j.get('workYears') or ''}"
            )
            for j in (r.get("jobs") or [])[:6]
        ) or "—"
        trs.append(
            "<tr>"
            f"<td>{esc(r['company'])}</td>"
            f"<td>{esc(dist)}</td>"
            f"<td>{'Y' if r.get('in_radius') else 'N'}</td>"
            f"<td>{r.get('total_jobs', 0)}</td>"
            f"<td>{jobs_html}</td>"
            f"<td>{esc((r.get('address') or '')[:40])}</td>"
            "</tr>"
        )
    body = "\n".join(trs)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>geo-job-hunt v5</title>
<style>
body{{font-family:ui-sans-serif,system-ui,sans-serif;margin:2rem;background:#f6f7f9;color:#1a1a1a}}
h1{{font-size:1.25rem}}
.meta{{color:#555;margin-bottom:1rem}}
table{{border-collapse:collapse;width:100%;background:#fff}}
th,td{{border:1px solid #ddd;padding:.5rem .6rem;vertical-align:top;font-size:.9rem}}
th{{background:#eef1f5;text-align:left}}
tr:nth-child(even){{background:#fafbfc}}
</style></head><body>
<h1>地理围栏找工作 v5 · {esc(args.mode)}</h1>
<p class="meta">{esc(args.address or args.location or '')} · {args.radius}m · {esc(args.city)} · {esc(args.job)} · {time.strftime('%Y-%m-%d %H:%M')}
{" · diff +" + str(meta.get("new_count", 0)) if meta else ""}</p>
<table>
<thead><tr><th>公司</th><th>距离</th><th>半径内</th><th>在招</th><th>岗位</th><th>地址</th></tr></thead>
<tbody>
{body}
</tbody></table>
</body></html>
"""


def maybe_telegram(text: str, args: argparse.Namespace) -> None:
    """可选推送:读环境变量 TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID,或 --telegram-chat。"""
    if not args.telegram:
        return
    env = load_env_merged(args.env)
    token = env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = args.telegram_chat or env.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        print("  !! --telegram 已开但缺少 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID", file=sys.stderr)
        return
    # Telegram 消息上限,截断
    payload = text if len(text) < 3500 else text[:3400] + "\n…(截断)"
    data = urllib.parse.urlencode({"chat_id": chat, "text": payload}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        http_json(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        print("[telegram] 已推送")
    except RuntimeError as e:
        # sendMessage 返回的也是 JSON,但我们的 http_json 在非 MCP 场景 OK
        # Telegram 成功时有 ok:true;若解析失败仍可能已发送
        print(f"  !! telegram: {e}", file=sys.stderr)


def write_out(content: str, path: str) -> None:
    if path:
        safe_makedirs_for(path)
        with open(path, "w") as f:
            f.write(content)
        print(f"已保存: {path}")
    else:
        print(content)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def add_shared_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--address", default="", help="圆心地址(与 --location 二选一)")
    p.add_argument("--location", default="", help="圆心坐标 lon,lat(GCJ-02);若给则跳过 geocode")
    p.add_argument("--radius", type=int, default=3000, help="半径(米)")
    p.add_argument("--city", default="杭州", help="猎聘 address=城市级 + 高德 city 偏置")
    p.add_argument("--job", default="实习|产品|AI|Agent", help="职位关键词(正则,|分隔;猎聘 API 用首词)")
    p.add_argument("--work-experience", default="", help="猎聘 workExperience,如 实习/应届")
    p.add_argument("--edu-level", default="", help="猎聘 eduLevel")
    p.add_argument("--salary-floor", type=int, default=None, help="薪资下限")
    p.add_argument("--salary-cap", type=int, default=None, help="薪资上限")
    p.add_argument("--salary-kind", default="", help="月薪 或 年薪")
    p.add_argument("--resume-keywords", default="", help="简历匹配词,|分隔,写入 _resume_score")
    p.add_argument("--format", choices=("md", "json", "html"), default="md", help="输出格式")
    p.add_argument("--out", default="", help="输出路径;省略则打印到 stdout")
    p.add_argument("--env", default="", help="密钥 .env 路径(默认自动探测各 profile .env)")
    p.add_argument("--state-file", default="", help="增量 state JSON 路径")
    p.add_argument("--diff-only", action="store_true", help="只输出相对 state 的新增岗位")
    p.add_argument("--telegram", action="store_true", help="推送到 Telegram(需 token/chat)")
    p.add_argument("--telegram-chat", default="", help="覆盖 TELEGRAM_CHAT_ID")
    p.add_argument("--liepin-sleep", type=float, default=2.0, help="猎聘调用基础间隔秒(默认 2.0;实测触发点 ~1.2s 持续,勿低于 1.5)")
    p.add_argument("--liepin-backoff", type=float, default=90.0, help="触发限流后退避秒数(默认 90;实测 60 往往不够)")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="地理围栏找工作 v5:高德 ↔ 猎聘(forward/reverse),stdlib only",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = ap.add_subparsers(dest="mode", required=True)

    fwd = sub.add_parser("forward", help="公司→岗位:半径内 POI 逐家查猎聘")
    add_shared_args(fwd)
    fwd.add_argument("--max-companies", type=int, default=25, help="最多查几家公司")
    fwd.add_argument(
        "--extra-keywords",
        default="",
        help="点名补搜关键词,逗号分隔(默认已含阿里/字节/同花顺等)",
    )
    fwd.add_argument("--no-default-extra", action="store_true", help="禁用默认点名补搜清单")
    fwd.add_argument(
        "--show-unmatched",
        action="store_true",
        help="无正则命中时回退展示该公司前 3 条在招(默认不展示,避免污染)",
    )

    rev = sub.add_parser("reverse", help="岗位→公司:猎聘搜岗后高德验距")
    add_shared_args(rev)
    rev.add_argument("--company", default="", help="可选:限定公司名")
    rev.add_argument("--max-pages", type=int, default=3, help="猎聘翻页数(page 从 0)")
    rev.add_argument("--max-jobs-per-company", type=int, default=5, help="每公司最多展示岗")
    rev.add_argument(
        "--require-in-radius",
        action="store_true",
        default=True,
        help="只保留半径内(默认开)",
    )
    rev.add_argument(
        "--keep-outside",
        action="store_true",
        help="保留半径外公司(关闭 --require-in-radius)",
    )

    return ap


def main(argv: list[str] | None = None) -> None:
    # 无子命令且首参是选项时,默认 forward(兼容旧 CLI);--help/-h 除外
    raw = list(argv) if argv is not None else sys.argv[1:]
    if raw and raw[0] not in ("forward", "reverse", "-h", "--help") and raw[0].startswith("-"):
        raw = ["forward", *raw]

    ap = build_parser()
    args = ap.parse_args(raw)
    if args.mode == "reverse" and args.keep_outside:
        args.require_in_radius = False

    env = load_env_merged(args.env)
    amap_key = os.environ.get("AMAP_MAPS_API_KEY") or env.get("AMAP_MAPS_API_KEY", "")
    liepin_token = os.environ.get("MCP_LIEPIN_API_KEY") or env.get("MCP_LIEPIN_API_KEY", "")
    if not amap_key or not liepin_token:
        sys.exit("缺少 key:检查 .env 里 AMAP_MAPS_API_KEY / MCP_LIEPIN_API_KEY")

    client = LiepinClient(
        liepin_token,
        sleep=args.liepin_sleep,
        backoff_sec=args.liepin_backoff,
        max_backoff_retries=1,
    )

    if args.mode == "forward":
        rows = run_forward(args, amap_key, client)
    else:
        rows = run_reverse(args, amap_key, client)

    meta: dict = {}
    if args.state_file or args.diff_only:
        if not args.state_file:
            sys.exit("--diff-only 需要同时给 --state-file")
        rows, meta = apply_diff(rows, args.state_file, args.diff_only)

    if args.format == "json":
        content = render_json(rows, meta, args)
    elif args.format == "html":
        content = render_html(rows, meta, args)
    else:
        content = render_md(rows, meta, args)

    write_out(content, args.out)

    if args.telegram:
        # 推送精简 md
        maybe_telegram(render_md(rows, meta, args), args)

    if client.auth_failed:
        sys.exit(2)
    if client.consecutive_rate_limits >= 2:
        sys.exit(3)


if __name__ == "__main__":
    main()
