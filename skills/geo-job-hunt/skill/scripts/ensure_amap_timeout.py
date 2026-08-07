#!/usr/bin/env python3
"""幂等补齐 4 处 Hermes config.yaml 的 amap.timeout:120(v5.1 工具)。

背景:SKILL 推荐 amap 块带 `timeout: 120`,但生产四处 config.yaml(根 + 3 profile)
曾长期缺失(审计 I3,两轮未落地)。本脚本把「记得手动改 4 个文件」变成可复跑的
确定性动作:缺才插、已有则跳过、默认 dry-run 只打印 diff。

用法:
  python3 ensure_amap_timeout.py            # dry-run,打印各文件状态
  python3 ensure_amap_timeout.py --yes      # 实际写入(幂等,已含 timeout 则跳过)
  python3 ensure_amap_timeout.py --paths /path/a.yaml /path/b.yaml   # 自定义路径

仅 stdlib。不依赖 PyYAML:按 amap 块文本结构插入,模式不匹配即拒绝写入并报错。
"""
from __future__ import annotations

import argparse
import os
import sys

DEFAULT_PATHS = [
    os.path.expanduser("~/.hermes/config.yaml"),
    os.path.expanduser("~/.hermes/profiles/writing/config.yaml"),
    os.path.expanduser("~/.hermes/profiles/lyric/config.yaml"),
    os.path.expanduser("~/.hermes/profiles/trading/config.yaml"),
]

AMAP_MARK = "  amap:"
CONNECT_MARK = "    connect_timeout: 90"
TIMEOUT_LINE = "    timeout: 120"


def process(path: str, apply: bool) -> str:
    if not os.path.isfile(path):
        return f"缺失文件(跳过): {path}"
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # 定位 amap 块
    amap_idx = None
    for i, ln in enumerate(lines):
        if ln.rstrip("\n") == AMAP_MARK:
            amap_idx = i
            break
    if amap_idx is None:
        return f"未找到 amap 块(跳过): {path}"

    # 块内检查:是否已有 timeout
    in_block = False
    connect_idx = None
    has_timeout = False
    for i in range(amap_idx + 1, len(lines)):
        ln = lines[i]
        stripped = ln.rstrip("\n")
        if i > amap_idx and stripped and not stripped.startswith("    ") and not stripped.startswith("  "):
            break  # 出块(缩进回到 2 空格或更浅,如 `  liepin:`)
        if stripped == CONNECT_MARK:
            connect_idx = i
        if stripped.startswith("    timeout:"):
            has_timeout = True

    if has_timeout:
        return f"已含 timeout(幂等跳过): {path}"
    if connect_idx is None:
        return f"amap 块内无 connect_timeout:90(模式不匹配,拒绝写入): {path}"

    if apply:
        lines.insert(connect_idx + 1, TIMEOUT_LINE + "\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return f"已插入 timeout:120: {path}"
    return f"待插入 timeout:120(dry-run): {path}"


def main() -> None:
    ap = argparse.ArgumentParser(description="幂等补齐 amap.timeout:120(默认 dry-run)")
    ap.add_argument("--yes", action="store_true", help="实际写入(默认只打印 diff 状态)")
    ap.add_argument("--paths", nargs="*", default=None, help="自定义路径列表(默认 4 处生产 config)")
    args = ap.parse_args()

    paths = args.paths or DEFAULT_PATHS
    changed = 0
    for p in paths:
        msg = process(p, args.yes)
        print(msg)
        if msg.startswith("待插入"):
            changed += 1
    print(f"\n{len(paths)} 个文件检查完毕;{'已写入' if args.yes else 'dry-run,未写入'}(变更 {changed} 处)")
    sys.exit(0)


if __name__ == "__main__":
    main()
