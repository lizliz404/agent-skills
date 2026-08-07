#!/usr/bin/env python3
"""Capture runtime surface area for landing-page-replication-v5.

Writes recon/runtime.json used by Signal Interaction Contract and
audit.py --behavior / --scroll-length. This is the gate that would have
failed haoqi V3 immediately after build (canvasCount=0, scroll compress).

Usage:
  python3 capture-runtime.py --url https://target.com --out recon/runtime.json
  python3 capture-runtime.py --url http://127.0.0.1:5173 --out recon/replica-runtime.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RUNTIME_JS = """() => {
  const all = Array.from(document.querySelectorAll('*'));
  const canvases = Array.from(document.querySelectorAll('canvas')).map((c) => ({
    w: c.width || c.clientWidth,
    h: c.height || c.clientHeight,
    className: c.className || '',
  }));

  let webgl = false;
  for (const c of document.querySelectorAll('canvas')) {
    try {
      if (c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl')) {
        webgl = true;
        break;
      }
    } catch (e) {}
  }

  const html = document.documentElement.outerHTML || '';
  const bodyClass = document.body ? document.body.className : '';
  const hasLenis =
    !!document.querySelector('[class*="lenis"], .lenis') ||
    /lenis/i.test(html) ||
    /lenis/i.test(bodyClass);

  const scrollContainers = [];
  const candidates = [
    document.scrollingElement,
    document.documentElement,
    document.body,
    ...Array.from(document.querySelectorAll('[class*="scroll"], [data-scroller], .lenis, main')),
  ].filter(Boolean);

  const seen = new Set();
  for (const el of candidates) {
    const key = el.tagName + (el.className || '') + (el.id || '');
    if (seen.has(key)) continue;
    seen.add(key);
    const sh = el.scrollHeight || 0;
    const ch = el.clientHeight || 0;
    if (sh > ch + 40) {
      scrollContainers.push({
        tag: el.tagName,
        id: el.id || '',
        className: String(el.className || '').slice(0, 120),
        scrollHeight: sh,
        clientHeight: ch,
        maxScroll: Math.max(0, sh - ch),
      });
    }
  }
  scrollContainers.sort((a, b) => b.maxScroll - a.maxScroll);

  const stickyCount = all.filter((el) => {
    const s = getComputedStyle(el).position;
    return s === 'sticky' || s === 'fixed';
  }).length;

  const audioNodes = document.querySelectorAll('audio, [data-sound], [class*="sound"]').length;

  const docScroll =
    Math.max(
      document.body ? document.body.scrollHeight : 0,
      document.documentElement ? document.documentElement.scrollHeight : 0,
    ) - (window.innerHeight || 0);

  const primary = scrollContainers[0];
  const maxScroll = primary ? primary.maxScroll : Math.max(0, docScroll);

  return {
    viewport: { w: window.innerWidth, h: window.innerHeight },
    canvasCount: canvases.length,
    canvases,
    webgl,
    hasLenis,
    stickyCount,
    audioNodes,
    maxScroll,
    documentScrollHeight: document.documentElement
      ? document.documentElement.scrollHeight
      : 0,
    scrollContainers: scrollContainers.slice(0, 8),
    flags: {
      WEBGL_THEATER: canvases.length > 0 || webgl,
      INNER_SCROLLER: !!(primary && primary.maxScroll > (window.innerHeight || 900)),
      LENIS: hasLenis,
    },
  };
}"""


def capture_with_playwright(url: str) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "playwright required for capture-runtime.py. "
            "pip install playwright && playwright install chromium"
        ) from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(1200)
        data = page.evaluate(RUNTIME_JS)
        # sample a few scroll positions for mid-page state hints
        states = []
        scroller = page.evaluate(
            """() => {
              const list = Array.from(document.querySelectorAll('*'));
              let best = document.scrollingElement || document.documentElement;
              let bestMax = 0;
              for (const el of [document.documentElement, document.body, ...list]) {
                if (!el) continue;
                const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
                if (m > bestMax) { bestMax = m; best = el; }
              }
              return { max: bestMax, isDoc: best === document.documentElement || best === document.body };
            }"""
        )
        max_scroll = int(scroller.get("max") or data.get("maxScroll") or 0)
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = int(max_scroll * frac)
            if scroller.get("isDoc"):
                page.evaluate(f"window.scrollTo(0, {y})")
            else:
                page.evaluate(
                    f"""() => {{
                      const list = Array.from(document.querySelectorAll('*'));
                      let best = document.scrollingElement;
                      let bestMax = 0;
                      for (const el of [document.documentElement, document.body, ...list]) {{
                        if (!el) continue;
                        const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
                        if (m > bestMax) {{ bestMax = m; best = el; }}
                      }}
                      if (best) best.scrollTop = {y};
                    }}"""
                )
            page.wait_for_timeout(250)
            sample = page.evaluate(
                """() => {
                  const canvas = document.querySelectorAll('canvas').length;
                  const bodyBg = getComputedStyle(document.body).backgroundColor;
                  const darkish = document.body.className || '';
                  return { canvasCount: canvas, bodyClass: darkish.slice(0, 80), bodyBg };
                }"""
            )
            states.append({"frac": frac, "y": y, **sample})
        page.evaluate("window.scrollTo(0, 0)")
        browser.close()

    data["scrollStateSamples"] = states
    data["scrollStateCountHint"] = len(
        {json.dumps(s, sort_keys=True) for s in states}
    )
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    data = capture_with_playwright(args.url)
    data["url"] = args.url
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))

    # Soft warnings to stderr for agent visibility
    if data.get("canvasCount", 0) > 0:
        print(
            f"WARN: WEBGL_THEATER — canvasCount={data['canvasCount']} webgl={data.get('webgl')}",
            file=sys.stderr,
        )
    if data.get("maxScroll", 0) > 3000:
        print(
            f"WARN: long scroll tunnel candidate — maxScroll={data['maxScroll']}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
