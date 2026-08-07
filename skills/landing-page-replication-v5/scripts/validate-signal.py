#!/usr/bin/env python3
"""Validate docs/SIGNAL.md Interaction Contract vs runtime P0 flags.

Exit 1 when runtime.json P0 signals lack a matching Interaction Contract row.

Usage:
  python3 validate-signal.py docs/SIGNAL.md recon/runtime.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Map runtime.json signals → required Interaction Contract row keywords
P0_RUNTIME_SIGNALS: dict[str, list[str]] = {
    "canvasCount": ["hero theater", "canvas", "webgl", "theater"],
    "webgl": ["webgl", "hero theater", "canvas", "theater"],
    "hasLenis": ["lenis", "scroll container", "smooth scroll", "scroll container"],
    "maxScroll": ["scroll tunnel", "scroll container", "scroll length", "maxscroll"],
    "stickyCount": ["sticky", "hud", "invert", "scroll tunnel"],
    "flags.INNER_SCROLLER": ["inner scroller", "scroll container", "lenis"],
    "flags.WEBGL_THEATER": ["webgl", "hero theater", "canvas", "theater"],
    "flags.LENIS": ["lenis", "scroll container"],
}


def _runtime_value(data: dict, dotted: str):
    if "." not in dotted:
        return data.get(dotted)
    head, tail = dotted.split(".", 1)
    node = data.get(head)
    if not isinstance(node, dict):
        return None
    return node.get(tail)


def _is_p0_active(data: dict, key: str) -> bool:
    val = _runtime_value(data, key)
    if key == "canvasCount":
        return int(val or 0) > 0
    if key == "stickyCount":
        return int(val or 0) > 0
    if key == "maxScroll":
        return int(val or 0) >= 2000
    if key.startswith("flags."):
        return bool(val)
    return bool(val)


def _parse_contract_rows(signal_text: str) -> list[str]:
    rows: list[str] = []
    in_table = False
    for line in signal_text.splitlines():
        if re.match(r"^\|\s*Interaction\s*\|", line, re.I):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                in_table = False
                continue
            if re.match(r"^\|\s*[-:]+\s*\|", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].lower() not in {"interaction", "(add rows)"}:
                rows.append(cells[0].lower())
    return rows


def _contract_covers(rows: list[str], keywords: list[str]) -> bool:
    blob = " ".join(rows)
    return any(kw in blob for kw in keywords)


def validate_signal(signal_path: Path, runtime_path: Path) -> list[str]:
    errors: list[str] = []
    if not signal_path.is_file():
        return [f"missing SIGNAL.md: {signal_path}"]
    if not runtime_path.is_file():
        return [f"missing runtime.json: {runtime_path}"]

    signal_text = signal_path.read_text(encoding="utf-8", errors="replace")
    runtime = json.loads(runtime_path.read_text())

    contract_rows = _parse_contract_rows(signal_text)
    if not contract_rows:
        errors.append("Interaction Contract table has no data rows")
        return errors

    missing: list[str] = []
    for key, keywords in P0_RUNTIME_SIGNALS.items():
        if _is_p0_active(runtime, key) and not _contract_covers(contract_rows, keywords):
            missing.append(key)

    if missing:
        errors.append(
            "P0 runtime signals without Interaction Contract row: "
            + ", ".join(sorted(set(missing)))
        )
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("signal_md", type=Path, help="Path to docs/SIGNAL.md")
    ap.add_argument("runtime_json", type=Path, help="Path to recon/runtime.json")
    args = ap.parse_args()

    errors = validate_signal(args.signal_md, args.runtime_json)
    if errors:
        print("FAIL: signal validation")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("PASS: Interaction Contract covers runtime P0 flags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
