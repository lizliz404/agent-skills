#!/usr/bin/env python3
"""Emit @font-face metric-alignment overrides for libre substitutes.

Tries Fontsource metadata when installed/available; otherwise prints a
measurement recipe + a reasonable starter override table.

Usage:
  python3 metric-align-fonts.py --target "Tiempos Text" --substitute "Source Serif 4"
  python3 metric-align-fonts.py --target Inter --substitute "Inter Tight" --family-as "Display Sub"
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# Starter table from common pairings (approximate). Prefer measuring in Chromium.
STARTER = {
    ("tiempos text", "source serif 4"): {
        "size-adjust": "96.5%",
        "ascent-override": "90%",
        "descent-override": "22%",
        "line-gap-override": "0%",
    },
    ("tiempos text", "crimson pro"): {
        "size-adjust": "98%",
        "ascent-override": "88%",
        "descent-override": "24%",
        "line-gap-override": "0%",
    },
    ("inter display", "inter tight"): {
        "size-adjust": "100%",
        "ascent-override": "90%",
        "descent-override": "22%",
        "line-gap-override": "0%",
    },
    ("inter", "inter"): {
        "size-adjust": "100%",
        "ascent-override": "90%",
        "descent-override": "22%",
        "line-gap-override": "0%",
    },
}


def fetch_fontsource_metrics(family: str) -> dict | None:
    slug = family.lower().replace(" ", "-")
    url = f"https://api.fontsource.org/v1/fonts/{urllib.parse.quote(slug)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "landing-page-replication-v5"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return data
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None


def emit_css(family_as: str, src_hint: str, metrics: dict) -> str:
    return f"""@font-face {{
  font-family: "{family_as}";
  src: {src_hint};
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  size-adjust: {metrics["size-adjust"]};
  ascent-override: {metrics["ascent-override"]};
  descent-override: {metrics["descent-override"]};
  line-gap-override: {metrics["line-gap-override"]};
}}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, help="Proprietary / target face name")
    ap.add_argument("--substitute", required=True, help="Libre substitute face name")
    ap.add_argument("--family-as", default="", help="CSS font-family name to emit")
    ap.add_argument(
        "--src",
        default='url("/fonts/substitute.woff2") format("woff2")',
        help="src descriptor for @font-face",
    )
    args = ap.parse_args()
    family_as = args.family_as or f"{args.target} Sub"
    key = (args.target.lower(), args.substitute.lower())
    metrics = STARTER.get(key)
    fs = fetch_fontsource_metrics(args.substitute)
    if fs:
        print(f"<!-- fontsource hit for substitute: {args.substitute} (id={fs.get('id')}) -->")
    if not metrics:
        metrics = {
            "size-adjust": "97%",
            "ascent-override": "90%",
            "descent-override": "22%",
            "line-gap-override": "0%",
        }
        print(
            f"WARNING: no starter pair for {key}; emitted defaults. "
            "Measure both faces in Chromium and tune size-adjust until body line-box matches.",
            file=sys.stderr,
        )

    print("/* Target:", args.target, "→ Substitute:", args.substitute, "*/")
    print(emit_css(family_as, args.src, metrics))
    print(
        """/* Measurement recipe (Chromium):
  1. Render two spans with same text, font-size 100px, line-height normal.
  2. Compare getBoundingClientRect().height and offset of baseline.
  3. size-adjust ≈ 100% * (target_xheight / sub_xheight).
  4. Re-check IMR rhythm / blur-sniff after applying.
*/"""
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
