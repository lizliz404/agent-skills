#!/usr/bin/env python3
"""投递清单管理(geo-job-hunt v5 配套)。

纯 stdlib。默认清单文件:~/.geo-job-hunt/apply-list.json

子命令:
  add       加入一条投递
  list      列出(可按 status / --due 过滤)
  set       更新状态/备注/匹配分/检查提醒
  due       列出 next_check 已到期或过期的条目
  export    导出 markdown / json
  import-json  从 geo_job_hunt.py --format json 的结果批量入库

状态机: wishlist → applied → interviewing → offer → rejected → withdrawn

v5: applied_at + next_check —— 因为猎聘 MCP/CLI 当前不能读投递反馈,
本地清单用「投递时间 + 下次检查日」补闭环(默认投递后 3 天提醒查 App/短信)。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timedelta

DEFAULT_FILE = os.path.expanduser("~/.geo-job-hunt/apply-list.json")
STATUSES = ("wishlist", "applied", "interviewing", "offer", "rejected", "withdrawn")
DEFAULT_CHECK_DAYS = 3
TS_FMT = "%Y-%m-%dT%H:%M:%S"
DAY_FMT = "%Y-%m-%d"


def now_ts() -> str:
    return time.strftime(TS_FMT)


def today_day() -> str:
    return time.strftime(DAY_FMT)


def parse_day(s: str) -> datetime | None:
    if not s:
        return None
    for fmt in (DAY_FMT, TS_FMT, "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19] if fmt == TS_FMT else s[:10], fmt if fmt != TS_FMT else TS_FMT)
        except ValueError:
            continue
    try:
        return datetime.strptime(s[:10], DAY_FMT)
    except ValueError:
        return None


def add_days(ts: str, days: int) -> str:
    base = parse_day(ts) or datetime.now()
    return (base + timedelta(days=days)).strftime(DAY_FMT)


def load(path: str) -> dict:
    if not os.path.isfile(path):
        return {"updated_at": None, "items": []}
    with open(path) as f:
        return json.load(f)


def save(path: str, data: dict) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    data["updated_at"] = now_ts()
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def stamp_applied(item: dict, check_days: int = DEFAULT_CHECK_DAYS, *, force: bool = False) -> None:
    """进入 applied 时写入 applied_at,并设 next_check=applied_at+N 天。"""
    if force or not item.get("applied_at"):
        item["applied_at"] = now_ts()
    if force or not item.get("next_check"):
        item["next_check"] = add_days(item["applied_at"], check_days)


def is_due(item: dict, as_of: str | None = None) -> bool:
    nc = item.get("next_check")
    if not nc:
        return False
    if item.get("status") not in ("applied", "interviewing"):
        return False
    ref = parse_day(as_of or today_day())
    due = parse_day(nc)
    if not ref or not due:
        return False
    return due.date() <= ref.date()


def cmd_add(args: argparse.Namespace) -> None:
    data = load(args.file)
    item = {
        "id": uuid.uuid4().hex[:10],
        "company": args.company,
        "job": args.job,
        "link": args.link or "",
        "dist_m": args.dist,
        "status": args.status,
        "score": args.score,
        "note": args.note or "",
        "source": args.source or "manual",
        "job_id": args.job_id,
        "job_kind": args.job_kind or "",
        "applied_at": args.applied_at or None,
        "next_check": args.next_check or None,
        "created_at": now_ts(),
        "updated_at": now_ts(),
    }
    if item["status"] == "applied":
        stamp_applied(item, args.check_days, force=not bool(args.applied_at))
        if args.next_check:
            item["next_check"] = args.next_check
    data["items"].append(item)
    save(args.file, data)
    extra = ""
    if item.get("applied_at"):
        extra = f"  applied_at={item['applied_at']}  next_check={item.get('next_check')}"
    print(f"已添加 {item['id']}: {item['company']} · {item['job']} [{item['status']}]{extra}")


def _print_item(i: dict) -> None:
    score = "-" if i.get("score") is None else i.get("score")
    due_flag = " DUE" if is_due(i) else ""
    tail = ""
    if i.get("applied_at") or i.get("next_check"):
        tail = f"  applied={i.get('applied_at') or '-'}  check={i.get('next_check') or '-'}{due_flag}"
    print(
        f"{i.get('id', '?'):10s}  {i.get('status', '?'):13s}  "
        f"score={score}  {i.get('company', '')} · {i.get('job', '')}"
        + tail
        + (f"  # {i['note']}" if i.get("note") else "")
    )


def cmd_list(args: argparse.Namespace) -> None:
    data = load(args.file)
    items = data.get("items") or []
    if args.status:
        items = [i for i in items if i.get("status") == args.status]
    if args.due:
        items = [i for i in items if is_due(i)]
    if not items:
        print("(空)")
        return
    for i in items:
        _print_item(i)


def cmd_due(args: argparse.Namespace) -> None:
    data = load(args.file)
    items = [i for i in (data.get("items") or []) if is_due(i, args.as_of or None)]
    if not items:
        print("(无到期检查项)")
        return
    print(f"# 反馈检查到期 · as_of={args.as_of or today_day()} · {len(items)} 条")
    for i in items:
        _print_item(i)
        print(
            f"  → 请打开猎聘 App 看消息/投递记录,并查短信;"
            f"然后: set --id {i.get('id')} --status <interviewing|rejected|...> --snooze-days {args.snooze_days}"
        )


def cmd_set(args: argparse.Namespace) -> None:
    data = load(args.file)
    found = None
    for i in data.get("items") or []:
        if i.get("id") == args.id:
            found = i
            break
    if not found:
        sys.exit(f"未找到 id={args.id}")

    prev = found.get("status")
    if args.status:
        if args.status not in STATUSES:
            sys.exit(f"非法 status,可选: {', '.join(STATUSES)}")
        found["status"] = args.status
        if args.status == "applied" and prev != "applied":
            stamp_applied(found, args.check_days, force=True)
    if args.note is not None:
        found["note"] = args.note
    if args.score is not None:
        found["score"] = args.score
    if args.link is not None:
        found["link"] = args.link
    if args.job_id is not None:
        found["job_id"] = args.job_id
    if args.job_kind is not None:
        found["job_kind"] = args.job_kind
    if args.applied_at is not None:
        found["applied_at"] = args.applied_at
    if args.next_check is not None:
        found["next_check"] = args.next_check
    if args.snooze_days is not None:
        base = found.get("next_check") or today_day()
        found["next_check"] = add_days(base, args.snooze_days)
    if args.checked:
        # 已人工检查:把下次检查再推 N 天(默认 3),状态不变
        found["next_check"] = add_days(today_day(), args.check_days)
        if args.note is None and not found.get("note"):
            pass
        note_stamp = f"[checked {today_day()}]"
        if note_stamp not in (found.get("note") or ""):
            found["note"] = ((found.get("note") or "") + " " + note_stamp).strip()

    found["updated_at"] = now_ts()
    save(args.file, data)
    print(
        f"已更新 {found['id']} → {found['status']}"
        f"  applied_at={found.get('applied_at') or '-'}  next_check={found.get('next_check') or '-'}"
    )


def cmd_export(args: argparse.Namespace) -> None:
    data = load(args.file)
    items = data.get("items") or []
    if args.status:
        items = [i for i in items if i.get("status") == args.status]
    if args.due:
        items = [i for i in items if is_due(i)]
    if args.format == "json":
        text = json.dumps({"items": items}, ensure_ascii=False, indent=2) + "\n"
    else:
        lines = [
            "# 投递清单",
            "",
            f"> {time.strftime('%Y-%m-%d %H:%M')} · {len(items)} 条",
            "",
            "| id | 状态 | 分 | 公司 | 岗位 | 投递于 | 下次检查 | 距离 | 备注 |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for i in items:
            dist = f"{i['dist_m']}m" if i.get("dist_m") is not None else ""
            score = "" if i.get("score") is None else i.get("score")
            due = "⚠" if is_due(i) else ""
            lines.append(
                f"| {i.get('id', '')} | {i.get('status', '')} | {score} | "
                f"{i.get('company', '')} | {i.get('job', '')} | "
                f"{i.get('applied_at') or ''} | {due}{i.get('next_check') or ''} | "
                f"{dist} | {i.get('note', '')} |"
            )
        text = "\n".join(lines) + "\n"
    if args.out:
        parent = os.path.dirname(args.out)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.out, "w") as f:
            f.write(text)
        print(f"已导出: {args.out}")
    else:
        print(text)


def cmd_import_json(args: argparse.Namespace) -> None:
    with open(args.input) as f:
        payload = json.load(f)
    rows = payload.get("rows") or []
    data = load(args.file)
    existing = {
        (i.get("company"), i.get("job")) for i in data.get("items") or []
    }
    n = 0
    for r in rows:
        for j in r.get("jobs") or []:
            job_name = j.get("jobName") or j.get("title") or ""
            key = (r.get("company"), job_name)
            if not job_name or key in existing:
                continue
            score = j.get("_resume_score")
            jid = j.get("jobId") or j.get("id")
            item = {
                "id": uuid.uuid4().hex[:10],
                "company": r.get("company", ""),
                "job": job_name,
                "link": j.get("jobLink") or j.get("link") or j.get("url") or "",
                "dist_m": r.get("dist_m"),
                "status": "wishlist",
                "score": score if score is not None else args.default_score,
                "note": "imported from geo_job_hunt json",
                "source": payload.get("mode", "import"),
                "job_id": int(jid) if jid is not None and str(jid).isdigit() else jid,
                "job_kind": j.get("jobKind") or j.get("kind") or "",
                "applied_at": None,
                "next_check": None,
                "created_at": now_ts(),
                "updated_at": now_ts(),
            }
            data["items"].append(item)
            existing.add(key)
            n += 1
    save(args.file, data)
    print(f"导入 {n} 条 → {args.file}")


def build_parser() -> argparse.ArgumentParser:
    file_parent = argparse.ArgumentParser(add_help=False)
    file_parent.add_argument("--file", default=DEFAULT_FILE, help="清单 JSON 路径")

    check_parent = argparse.ArgumentParser(add_help=False)
    check_parent.add_argument(
        "--check-days",
        type=int,
        default=DEFAULT_CHECK_DAYS,
        help=f"投递后多少天设 next_check(默认 {DEFAULT_CHECK_DAYS})",
    )

    ap = argparse.ArgumentParser(
        description="投递清单管理 (geo-job-hunt v5)",
        parents=[file_parent],
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="添加投递", parents=[file_parent, check_parent])
    add.add_argument("--company", required=True)
    add.add_argument("--job", required=True)
    add.add_argument("--link", default="")
    add.add_argument("--dist", type=int, default=None)
    add.add_argument("--status", default="wishlist", choices=STATUSES)
    add.add_argument("--score", type=int, default=None)
    add.add_argument("--note", default="")
    add.add_argument("--source", default="manual")
    add.add_argument("--job-id", type=int, default=None, help="猎聘 jobId(投递用)")
    add.add_argument("--job-kind", default="", help="猎聘 jobKind(投递用)")
    add.add_argument("--applied-at", default="", help="覆盖投递时间 ISO")
    add.add_argument("--next-check", default="", help="覆盖下次检查日 YYYY-MM-DD")

    ls = sub.add_parser("list", help="列出", parents=[file_parent])
    ls.add_argument("--status", choices=STATUSES, default="")
    ls.add_argument("--due", action="store_true", help="只显示 next_check 已到期")

    due = sub.add_parser("due", help="列出反馈检查到期项", parents=[file_parent])
    due.add_argument("--as-of", default="", help="参照日 YYYY-MM-DD(默认今天)")
    due.add_argument("--snooze-days", type=int, default=DEFAULT_CHECK_DAYS, help="提示用")

    st = sub.add_parser("set", help="更新", parents=[file_parent, check_parent])
    st.add_argument("--id", required=True)
    st.add_argument("--status", choices=STATUSES, default="")
    st.add_argument("--note", default=None)
    st.add_argument("--score", type=int, default=None)
    st.add_argument("--link", default=None)
    st.add_argument("--job-id", type=int, default=None)
    st.add_argument("--job-kind", default=None)
    st.add_argument("--applied-at", default=None)
    st.add_argument("--next-check", default=None)
    st.add_argument("--snooze-days", type=int, default=None, help="把 next_check 再推 N 天")
    st.add_argument("--checked", action="store_true", help="标记已检查:next_check=今天+check-days")

    ex = sub.add_parser("export", help="导出", parents=[file_parent])
    ex.add_argument("--format", choices=("md", "json"), default="md")
    ex.add_argument("--status", choices=STATUSES, default="")
    ex.add_argument("--due", action="store_true")
    ex.add_argument("--out", default="")

    im = sub.add_parser("import-json", help="从 hunt json 导入 wishlist", parents=[file_parent])
    im.add_argument("--input", required=True, help="geo_job_hunt --format json 输出文件")
    im.add_argument("--default-score", type=int, default=None)

    return ap


def main() -> None:
    ap = build_parser()
    args = ap.parse_args()
    if args.cmd == "add":
        cmd_add(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "due":
        cmd_due(args)
    elif args.cmd == "set":
        cmd_set(args)
    elif args.cmd == "export":
        cmd_export(args)
    elif args.cmd == "import-json":
        cmd_import_json(args)
    else:
        ap.error(f"unknown cmd {args.cmd}")


if __name__ == "__main__":
    main()
