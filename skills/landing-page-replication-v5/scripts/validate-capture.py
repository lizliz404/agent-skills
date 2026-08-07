#!/usr/bin/env python3
"""Validate Loop 0 capture artifacts for landing-page-replication-v5.

Exit 1 when required capture outputs are missing or under threshold.

Usage:
  python3 validate-capture.py recon/
  python3 validate-capture.py recon/ --min-screenshots 5
  python3 validate-capture.py recon/ --allow-missing-runtime  # static SSR only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate_capture(
    recon_dir: Path,
    *,
    min_screenshots: int = 5,
    allow_missing_runtime: bool = False,
) -> list[str]:
    errors: list[str] = []

    if not recon_dir.is_dir():
        return [f"recon directory not found: {recon_dir}"]

    index = recon_dir / "index.html"
    headers = recon_dir / "headers.txt"
    if not index.is_file():
        errors.append(f"missing {index}")
    if not headers.is_file():
        errors.append(f"missing {headers}")

    shots_dir = recon_dir / "screenshots"
    shot_count = 0
    if shots_dir.is_dir():
        shot_count = len(
            [p for p in shots_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
        )
    else:
        errors.append(f"missing screenshots directory: {shots_dir}")

    if shot_count < min_screenshots:
        errors.append(
            f"only {shot_count} screenshot(s) in {shots_dir} (need ≥{min_screenshots})"
        )

    runtime = recon_dir / "runtime.json"
    if not runtime.is_file():
        if allow_missing_runtime:
            print("NOTE: runtime.json missing — allowed via --allow-missing-runtime (document N/A in SIGNAL.md)")
        else:
            errors.append(
                f"missing {runtime} (run capture-runtime.py or pass --allow-missing-runtime for static SSR)"
            )
    else:
        try:
            data = json.loads(runtime.read_text())
            for key in ("canvasCount", "webgl", "maxScroll"):
                if key not in data:
                    errors.append(f"runtime.json missing key: {key}")
        except json.JSONDecodeError as exc:
            errors.append(f"runtime.json invalid JSON: {exc}")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("recon_dir", type=Path, help="Path to recon/ directory")
    ap.add_argument("--min-screenshots", type=int, default=5)
    ap.add_argument(
        "--allow-missing-runtime",
        action="store_true",
        help="Permit missing runtime.json for pure-static SSR (must document in SIGNAL.md)",
    )
    args = ap.parse_args()

    errors = validate_capture(
        args.recon_dir,
        min_screenshots=args.min_screenshots,
        allow_missing_runtime=args.allow_missing_runtime,
    )
    if errors:
        print("FAIL: capture validation")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"PASS: capture artifacts OK ({args.recon_dir})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
