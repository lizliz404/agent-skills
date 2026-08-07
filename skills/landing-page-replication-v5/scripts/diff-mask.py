#!/usr/bin/env python3
"""Pixel-diff heatmap wrapper (delegates to audit.py --diff).

landing-page-replication-v5

Usage:
  python3 diff-mask.py target.png replica.png [--out heatmap.png]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("replica")
    ap.add_argument("--out", default="diff-heatmap.png")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    return subprocess.call(
        [
            sys.executable,
            str(here / "audit.py"),
            "--diff",
            args.target,
            args.replica,
            "--out",
            args.out,
        ]
    )


if __name__ == "__main__":
    sys.exit(main())
