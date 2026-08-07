#!/usr/bin/env python3
"""Multi-route capture for landing-page-replication-v5.

Routes: curl fast path → Playwright when shell/SPA/Framer → documents bot blocks.
Also records assets.json (canvas/img/video) and offsets.json (maxScroll) when
Playwright runs — inputs to runtime / scroll-length gates.

Usage:
  python3 capture.py --url https://target.com --out recon/
  python3 capture.py --url https://target.com --out recon/ --engine playwright
  python3 capture.py --url https://target.com --out recon/ --no-shots
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = "landing-page-replication-v5/capture"

COMPUTED_JS = """() => {
  const pick = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    const s = getComputedStyle(el);
    return {
      fontFamily: s.fontFamily,
      fontSize: s.fontSize,
      fontWeight: s.fontWeight,
      letterSpacing: s.letterSpacing,
      lineHeight: s.lineHeight,
      color: s.color,
      backgroundColor: s.backgroundColor
    };
  };
  return {
    h1: pick("h1"),
    h2: pick("h2"),
    body: pick("body"),
    button: pick("a[href*='signup'], a[href*='start'], button, [class*='button']")
  };
}"""

ASSETS_JS = """() => {
  const imgs = Array.from(document.images).slice(0, 40).map((i) => ({
    src: (i.currentSrc || i.src || '').slice(0, 200),
    w: i.naturalWidth,
    h: i.naturalHeight,
  }));
  const canvases = Array.from(document.querySelectorAll('canvas')).map((c) => ({
    w: c.width || c.clientWidth,
    h: c.height || c.clientHeight,
    class: c.className || '',
  }));
  const videos = Array.from(document.querySelectorAll('video')).map((v) => ({
    src: (v.currentSrc || '').slice(0, 200),
    w: v.videoWidth,
    h: v.videoHeight,
  }));
  return { imgs, canvases, videos };
}"""

OFFSETS_JS = """() => {
  const sections = Array.from(
    document.querySelectorAll('section, footer, [data-section], main > div')
  ).slice(0, 40).map((el) => {
    const r = el.getBoundingClientRect();
    const top = r.top + (window.scrollY || document.documentElement.scrollTop || 0);
    return {
      tag: el.tagName,
      id: el.id || '',
      top: Math.round(top),
      h: Math.round(r.height),
      text: (el.innerText || '').trim().slice(0, 120),
    };
  });
  // Prefer longest scroll container (inner Lenis-style scroller)
  let maxScroll = Math.max(
    0,
    (document.documentElement.scrollHeight || 0) - (window.innerHeight || 0),
  );
  for (const el of document.querySelectorAll('*')) {
    const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
    if (m > maxScroll) maxScroll = m;
  }
  const heads = Array.from(document.querySelectorAll('h1,h2,h3')).slice(0, 40).map((el) => {
    const r = el.getBoundingClientRect();
    const top = r.top + (window.scrollY || 0);
    return {
      t: (el.innerText || '').trim().slice(0, 80),
      top: Math.round(top),
      fs: parseFloat(getComputedStyle(el).fontSize) || null,
    };
  });
  return { sections, heads, maxScroll: Math.round(maxScroll) };
}"""


def curl_capture(url: str, out: Path) -> tuple[str, str, int]:
    headers_path = out / "headers.txt"
    html_path = out / "index.html"
    hdr_lines: list[str] = []
    status = 0
    body = b""

    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as resp:
            status = resp.status
            hdr_lines = [f"{k}: {v}" for k, v in resp.headers.items()]
            body = resp.read(3_000_000)
    except urllib.error.HTTPError as exc:
        status = exc.code
        hdr_lines = [f"HTTPError: {exc.code} {exc.reason}"]
        try:
            body = exc.read(500_000) if exc.fp else b""
        except Exception:  # noqa: BLE001
            body = b""
    except Exception as exc:  # noqa: BLE001
        headers_path.write_text(f"capture failed: {exc}\n")
        html_path.write_text("")
        return "", str(exc), 0

    html_path.write_bytes(body)
    headers_path.write_text("\n".join(hdr_lines) + "\n")
    return body.decode("utf-8", errors="replace"), "\n".join(hdr_lines), status


def fingerprint(html: str, headers: str) -> dict:
    blob = html + "\n" + headers
    low = blob.lower()
    return {
        "nextjs": bool(re.search(r"x-nextjs|/_next/|__next", blob, re.I)),
        "vercel": "vercel" in low,
        "framer": bool(re.search(r"framer|data-framer", blob, re.I)),
        "webflow": "webflow" in low,
        "vite_spa": bool(re.search(r"""id=["'](?:root|app)["']""", html, re.I)),
        "challenge": bool(
            re.search(
                r"challenge|turnstile|cf-browser-verification|attention required",
                low,
            )
        ),
        "has_h1": bool(re.search(r"<h1\b", html, re.I)),
        "has_canvas": bool(re.search(r"<canvas\b", html, re.I)),
        "has_lenis": "lenis" in low,
    }


def needs_playwright(fp: dict, engine: str) -> bool:
    if engine == "playwright":
        return True
    if engine == "curl":
        return False
    if fp.get("challenge"):
        return False
    if fp.get("framer") or fp.get("vite_spa"):
        return True
    if fp.get("nextjs") and not fp.get("has_h1"):
        return True
    if fp.get("has_canvas") or fp.get("has_lenis"):
        return True
    if not fp.get("has_h1"):
        return True
    return False


def playwright_capture(url: str, out: Path, shots: bool) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright not installed — pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        return 2

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(url, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(1500)
            (out / "dom.html").write_text(
                page.evaluate("() => document.documentElement.outerHTML")
            )
            html = page.content()
            existing = (out / "index.html").read_text(errors="replace")
            if len(existing) < 500:
                (out / "index.html").write_text(html)
            (out / "computed.json").write_text(
                json.dumps(page.evaluate(COMPUTED_JS), indent=2)
            )
            (out / "assets.json").write_text(
                json.dumps(page.evaluate(ASSETS_JS), indent=2)
            )
            (out / "offsets.json").write_text(
                json.dumps(page.evaluate(OFFSETS_JS), indent=2)
            )
            if shots:
                shot_dir = out / "screenshots"
                shot_dir.mkdir(exist_ok=True)
                page.screenshot(path=str(shot_dir / "01-hero.png"), full_page=False)
                page.screenshot(path=str(shot_dir / "00-full.png"), full_page=True)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.35)")
                page.wait_for_timeout(400)
                page.screenshot(path=str(shot_dir / "02-mid.png"), full_page=False)
                # scroll progression for tunnel / theater sites
                for i, frac in enumerate((0.0, 0.2, 0.4, 0.6, 0.8, 1.0)):
                    page.evaluate(
                        f"""() => {{
                          let max = Math.max(
                            document.documentElement.scrollHeight - innerHeight,
                            0
                          );
                          for (const el of document.querySelectorAll('*')) {{
                            const m = el.scrollHeight - el.clientHeight;
                            if (m > max) max = m;
                          }}
                          const y = Math.round(max * {frac});
                          let best = document.scrollingElement;
                          let bestMax = 0;
                          for (const el of [document.documentElement, document.body, ...document.querySelectorAll('*')]) {{
                            if (!el) continue;
                            const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
                            if (m > bestMax) {{ bestMax = m; best = el; }}
                          }}
                          if (best === document.documentElement || best === document.body) {{
                            window.scrollTo(0, y);
                          }} else if (best) {{
                            best.scrollTop = y;
                          }}
                        }}"""
                    )
                    page.wait_for_timeout(300)
                    page.screenshot(
                        path=str(shot_dir / f"scroll-{i:02d}.png"), full_page=False
                    )
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(200)
                page.screenshot(path=str(shot_dir / "05-nav-top.png"), full_page=False)
            browser.close()
        print("playwright ok", file=sys.stderr)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"playwright failed: {exc}", file=sys.stderr)
        print(
            "If this is a bot challenge, use manual DevTools capture "
            "(see references/capture-router.md).",
            file=sys.stderr,
        )
        return 3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--engine", choices=["auto", "curl", "playwright"], default="auto")
    ap.add_argument("--no-shots", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "screenshots").mkdir(exist_ok=True)
    (args.out / "css").mkdir(exist_ok=True)

    html, headers, status = curl_capture(args.url, args.out)
    fp = fingerprint(html, headers)
    fp["http_status"] = status
    route = "curl"
    note = ""

    if status in (403, 503) or fp.get("challenge"):
        route = "manual-devtools"
        note = (
            "Bot management suspected. curl/Playwright may both fail. "
            "Use browser DevTools → Network+Elements; see references/capture-router.md."
        )
        print(f"ROUTE: {route}\n{note}", file=sys.stderr)
    elif needs_playwright(fp, args.engine):
        route = "playwright"
        print(f"ROUTE: {route} (fingerprint={fp})", file=sys.stderr)
        code = playwright_capture(args.url, args.out, shots=not args.no_shots)
        if code != 0:
            note = "Playwright failed — fall back to manual DevTools."
            route = "manual-devtools"
    else:
        print(f"ROUTE: {route} (fingerprint={fp})", file=sys.stderr)

    meta = {"url": args.url, "route": route, "fingerprint": fp, "note": note}
    (args.out / "capture-meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))

    # Best-effort runtime capture when Playwright path succeeded
    if route == "playwright":
        try:
            import subprocess

            rt_path = Path(__file__).resolve().parent / "capture-runtime.py"
            out_rt = args.out / "runtime.json"
            subprocess.run(
                [
                    sys.executable,
                    str(rt_path),
                    "--url",
                    args.url,
                    "--out",
                    str(out_rt),
                ],
                check=False,
                timeout=120,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"runtime capture skipped: {exc}", file=sys.stderr)

    if route == "manual-devtools":
        return 10
    return 0


if __name__ == "__main__":
    sys.exit(main())
