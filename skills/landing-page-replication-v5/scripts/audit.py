#!/usr/bin/env python3
"""Taste + runtime gates for landing-page-replication-v5.

Usage:
  python3 audit.py --imr target.png replica.png --tolerance 8
  python3 audit.py --diff target.png replica.png
  python3 audit.py --typescale https://replica.local
  python3 audit.py --density https://replica.local
  python3 audit.py --rhythm replica.png --bands 5
  python3 audit.py --scroll-length recon/offsets.json https://replica.local --min-ratio 0.85
  python3 audit.py --behavior-offline recon/runtime.json https://replica.local --out behavior-diff.json
  python3 audit.py --behavior https://target.com https://replica.local --out behavior-diff.json
  python3 audit.py --reduced-motion https://replica.local
  python3 audit.py --smooth-nav https://replica.local
  python3 audit.py --replica-only https://replica.local --signal docs/SIGNAL.md

Default Loop 5 path is --behavior-offline (one replica session; target from runtime.json).
Use --behavior only when live target re-probe is required; target probes share one session.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_rgba(path: Path):
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(
            "Pillow required for --imr/--diff/--rhythm. "
            "pip install -r scripts/requirements.txt (or: pip install Pillow)"
        ) from exc
    im = Image.open(path).convert("RGBA")
    return im


def _is_ink(r: int, g: int, b: int, a: int, paper_thresh: int = 245) -> bool:
    if a < 16:
        return False
    if r >= paper_thresh and g >= paper_thresh and b >= paper_thresh:
        return False
    if min(r, g, b) >= 230 and max(r, g, b) - min(r, g, b) < 18:
        return False
    return True


def ink_mass_ratio(im, bands: int = 1) -> list[float]:
    w, h = im.size
    px = im.load()
    out = []
    for i in range(bands):
        y0 = h * i // bands
        y1 = h * (i + 1) // bands
        ink = 0
        total = 0
        for y in range(y0, y1):
            for x in range(w):
                r, g, b, a = px[x, y]
                total += 1
                if _is_ink(r, g, b, a):
                    ink += 1
        out.append(100.0 * ink / total if total else 0.0)
    return out


def cmd_imr(args: argparse.Namespace) -> int:
    t = _load_rgba(Path(args.target))
    r = _load_rgba(Path(args.replica))
    if r.size != t.size:
        r = r.resize(t.size)
    bands = args.bands
    timr = ink_mass_ratio(t, bands)
    rimr = ink_mass_ratio(r, bands)
    print("band\ttarget_IMR%\treplica_IMR%\tdelta")
    fails = 0
    for i, (a, b) in enumerate(zip(timr, rimr)):
        d = abs(a - b)
        flag = "FAIL" if d > args.tolerance else "ok"
        if flag == "FAIL":
            fails += 1
        print(f"{i}\t{a:.2f}\t{b:.2f}\t{d:.2f}\t{flag}")
    print(f"tolerance={args.tolerance}%  fails={fails}/{bands}")
    return 1 if fails else 0


def cmd_diff(args: argparse.Namespace) -> int:
    t = _load_rgba(Path(args.target)).convert("RGB")
    r = _load_rgba(Path(args.replica)).convert("RGB")
    if r.size != t.size:
        r = r.resize(t.size)
    from PIL import ImageChops, ImageEnhance
    import statistics

    diff = ImageChops.difference(t, r)
    heat = ImageEnhance.Brightness(diff).enhance(3.0)
    out = Path(args.out or "diff-heatmap.png")
    heat.save(out)
    px = list(diff.getdata())
    means = [statistics.fmean(p) for p in px]
    mean_delta = statistics.fmean(means) if means else 0
    print(f"mean_rgb_delta={mean_delta:.2f}")
    print(f"heatmap={out}")
    try:
        from skimage.metrics import structural_similarity as ssim
        import numpy as np

        ta = np.asarray(t.convert("L"))
        ra = np.asarray(r.convert("L"))
        score = ssim(ta, ra)
        print(f"ssim={score:.4f}")
    except Exception:
        print("ssim=n/a (optional: pip install scikit-image)")
    return 0


def _playwright_eval(url: str, js: str, timeout: int = 90):
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
js = {js!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(800)
    print(json.dumps(page.evaluate(js)))
    browser.close()
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "playwright failed")
    return json.loads(proc.stdout.strip().splitlines()[-1])


RUNTIME_PROBE_JS = """() => {
  const canvases = Array.from(document.querySelectorAll('canvas')).map((c) => ({
    w: c.width || c.clientWidth,
    h: c.height || c.clientHeight,
  }));
  let webgl = false;
  for (const c of document.querySelectorAll('canvas')) {
    try {
      if (c.getContext('webgl2') || c.getContext('webgl') || c.getContext('experimental-webgl')) {
        webgl = true; break;
      }
    } catch (e) {}
  }
  const hasLenis = !!document.querySelector('[class*="lenis"], .lenis') ||
    /lenis/i.test(document.documentElement.outerHTML);
  let maxScroll = Math.max(0,
    (document.documentElement.scrollHeight || 0) - (window.innerHeight || 0));
  let primaryClass = 'document';
  for (const el of document.querySelectorAll('*')) {
    const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
    if (m > maxScroll) {
      maxScroll = m;
      primaryClass = (el.className || el.tagName || '').toString().slice(0, 80);
    }
  }
  const stickyCount = Array.from(document.querySelectorAll('*')).filter((el) => {
    const p = getComputedStyle(el).position;
    return p === 'sticky' || p === 'fixed';
  }).length;
  return {
    canvasCount: canvases.length,
    canvases,
    webgl,
    hasLenis,
    maxScroll: Math.round(maxScroll),
    stickyCount,
    primaryScroller: primaryClass,
  };
}"""


# Theater-only targets for pointer reactivity (v5).
# Broad hero/button selectors caused false positives via ordinary :hover { transform }.
THEATER_POINTER_SELECTORS = [
    "canvas",
    "[data-theater]",
    "[data-pointer]",
]

# Broad selectors for scroll-state visual sampling (not pointer reactivity).
SCROLL_SIGNAL_SELECTORS = [
    "canvas",
    "[data-theater]",
    "[data-pointer]",
    "[data-scroll-tunnel]",
    "[data-parallax]",
    "[data-scene]",
    ".scene",
    "[class*='theater']",
    "[data-tilt]",
    ".parallax",
    "main",
    "section",
    "header",
    "[data-hud]",
    "nav",
]

REPLICA_ONLY_SELECTORS = [
    "[class*='cursor-trail']",
    "[class*='cursor-follow']",
    "[data-intro]",
    "[class*='stagger-intro']",
    ".magnetic",
]

POINTER_SAMPLE_JS = f"""() => {{
  const selectors = {json.dumps(THEATER_POINTER_SELECTORS)};
  const nodes = [];
  const seen = new Set();
  for (const sel of selectors) {{
    try {{
      for (const el of document.querySelectorAll(sel)) {{
        const key = el.tagName + '#' + (el.id || '') + '.' + (el.className || '');
        if (seen.has(key)) continue;
        seen.add(key);
        const cs = getComputedStyle(el);
        nodes.push({{
          sel,
          tag: el.tagName,
          transform: cs.transform,
          opacity: cs.opacity,
          filter: cs.filter,
          rx: el.style.getPropertyValue('--rx') || '',
          ry: el.style.getPropertyValue('--ry') || '',
        }});
      }}
    }} catch (e) {{}}
  }}
  return {{
    hasProbeTarget: nodes.length > 0,
    nodes: nodes.slice(0, 8),
    canvasCount: document.querySelectorAll('canvas').length,
  }};
}}"""

# Backward-compat alias used by older call sites / docs.
POINTER_PROBE_SELECTORS = THEATER_POINTER_SELECTORS
POINTER_PROBE_JS = POINTER_SAMPLE_JS


def cmd_typescale(args: argparse.Namespace) -> int:
    js = """() => {
      const h1 = document.querySelector('h1');
      const body = document.body;
      if (!h1) return {error: 'no h1'};
      const hs = getComputedStyle(h1).fontSize;
      const bs = getComputedStyle(body).fontSize;
      const h = parseFloat(hs), b = parseFloat(bs);
      return {h1: hs, body: bs, tss: b ? h/b : null,
        h2: (document.querySelector('h2') && getComputedStyle(document.querySelector('h2')).fontSize) || null};
    }"""
    data = _playwright_eval(args.url, js)
    print(json.dumps(data, indent=2))
    tss = data.get("tss")
    if tss is None:
        return 1
    if tss < 3.0 or tss > 7.0:
        print("FAIL: TSS outside common 3.0–7.0 band — verify with target computed styles")
        return 1
    if 4.5 <= tss <= 6.5:
        print("band=modern-saas")
    elif 3.0 <= tss <= 4.0:
        print("band=editorial")
    else:
        print("band=other")
    return 0


def cmd_density(args: argparse.Namespace) -> int:
    js = """() => {
      const vh = window.innerHeight || 1;
      const leaves = Array.from(document.body.querySelectorAll('*')).filter(
        el => el.children.length === 0 && el.offsetParent !== null
      );
      const sections = Array.from(document.querySelectorAll('section, main > div, [data-section]'));
      const totalVh = Math.max(document.body.scrollHeight / vh, 1);
      const per = sections.map((s, i) => {
        const h = s.getBoundingClientRect().height || 1;
        const n = s.querySelectorAll('*');
        const leaf = Array.from(n).filter(el => el.children.length === 0).length;
        return {i, leaves: leaf, ed_per_vh: leaf / (h/vh)};
      });
      return {leaves: leaves.length, page_vh: totalVh, ed_page: leaves.length / totalVh, sections: per.slice(0, 30)};
    }"""
    data = _playwright_eval(args.url, js)
    print(json.dumps(data, indent=2))
    ed = data.get("ed_page") or 0
    if ed < 60 or ed > 120:
        print(f"FAIL: page ED {ed:.1f} outside SaaS baseline 60–120 / vh (compare to target)")
        return 1
    print("ED within SaaS baseline 60–120 / vh (still compare ±20% to target)")
    return 0


def cmd_rhythm(args: argparse.Namespace) -> int:
    im = _load_rgba(Path(args.image))
    series = ink_mass_ratio(im, args.bands)
    print("imr_series=" + ",".join(f"{x:.2f}" for x in series))
    deltas = [series[i + 1] - series[i] for i in range(len(series) - 1)]
    print("delta_series=" + ",".join(f"{x:.2f}" for x in deltas))
    if len(deltas) > 1:
        mean = sum(deltas) / len(deltas)
        var = sum((d - mean) ** 2 for d in deltas) / len(deltas)
        print(f"delta_variance={var:.2f}  (low → flat mid-mid-mid rhythm)")
    if args.target_series:
        target = [float(x) for x in Path(args.target_series).read_text().replace(",", " ").split()]
        n = max(len(series), len(target))
        s = series + [series[-1]] * (n - len(series))
        t = target + [target[-1]] * (n - len(target))
        dtw = sum(abs(a - b) for a, b in zip(s, t)) / n
        print(f"mean_abs_series_delta_vs_target={dtw:.2f}")
    return 0


def _target_max_scroll(offsets_path: Path) -> int:
    data = json.loads(offsets_path.read_text())
    if isinstance(data, dict):
        if "maxScroll" in data:
            return int(data["maxScroll"])
        if "target" in data and isinstance(data["target"], dict):
            return int(data["target"].get("maxScroll") or 0)
    raise SystemExit(f"no maxScroll in {offsets_path}")


def cmd_scroll_length(args: argparse.Namespace) -> int:
    target_max = _target_max_scroll(Path(args.offsets))
    replica = _playwright_eval(args.url, RUNTIME_PROBE_JS)
    replica_max = int(replica.get("maxScroll") or 0)
    ratio = (replica_max / target_max) if target_max else 0.0
    print(
        json.dumps(
            {
                "target_maxScroll": target_max,
                "replica_maxScroll": replica_max,
                "ratio": round(ratio, 4),
                "min_ratio": args.min_ratio,
                "replica_probe": replica,
            },
            indent=2,
        )
    )
    if ratio < args.min_ratio:
        print(
            f"FAIL: scroll-length ratio {ratio:.3f} < {args.min_ratio} "
            "(Failure Gallery J — Scroll Compress Syndrome). "
            "Document waiver in docs/GAPS.md or lengthen scroll tunnel."
        )
        return 1
    print(f"PASS: scroll-length ratio {ratio:.3f} ≥ {args.min_ratio}")
    return 0


def _parse_transform_nums(transform: str) -> list[float]:
    if not transform or transform == "none":
        return []
    import re

    return [float(x) for x in re.findall(r"-?\d+\.?\d*(?:e[-+]?\d+)?", transform)]


def _continuous_pointer_delta(samples: list[dict]) -> dict:
    """Require 3+ samples with continuous numeric drift on theater nodes.

    Binary before≠after fails: ordinary :hover { transform: scale(1.02) } flips once.
    Continuous = ≥3 distinct numeric snapshots along the mouse path for the same node.
    """
    if len(samples) < 3:
        return {
            "pointerChanged": False,
            "varDelta": False,
            "continuous": False,
            "reason": "need ≥3 samples",
        }

    if not any(s.get("hasProbeTarget") for s in samples):
        return {
            "pointerChanged": False,
            "varDelta": False,
            "continuous": False,
            "reason": "no canvas/[data-theater]/[data-pointer] target",
            "hasProbeTarget": False,
        }

    # Align nodes by index across samples
    max_nodes = max(len(s.get("nodes") or []) for s in samples)
    continuous = False
    var_delta = False
    detail = []

    for i in range(max_nodes):
        transforms = []
        vars_rx = []
        vars_ry = []
        for s in samples:
            nodes = s.get("nodes") or []
            if i >= len(nodes):
                continue
            n = nodes[i]
            transforms.append(n.get("transform") or "none")
            vars_rx.append(n.get("rx") or "")
            vars_ry.append(n.get("ry") or "")

        # CSS var continuous change
        rx_filled = [v for v in vars_rx if v]
        ry_filled = [v for v in vars_ry if v]
        if len(set(rx_filled)) >= 3 or len(set(ry_filled)) >= 3:
            var_delta = True
            continuous = True
            detail.append({"node": i, "kind": "css-var", "rx": vars_rx, "ry": vars_ry})
            continue

        # Transform matrix continuous change across ≥3 distinct values
        distinct = list(dict.fromkeys(transforms))
        if len(distinct) < 3:
            continue

        # Check numeric components drift (not a single binary flip)
        series = [_parse_transform_nums(t) for t in transforms]
        series = [row for row in series if row]
        if len(series) < 3:
            continue
        dim = min(len(row) for row in series)
        for d in range(dim):
            vals = [row[d] for row in series]
            if len(set(round(v, 4) for v in vals)) >= 3:
                # Prefer path that isn't a two-state hover: max-min should exceed
                # a trivial scale(1.02) bounce if only endpoints differ — already
                # gated by ≥3 distinct samples.
                continuous = True
                detail.append({"node": i, "kind": "transform", "dim": d, "vals": vals})
                break

        # Opacity / filter path via serialized node dump across samples
        opacities = []
        filters = []
        for s in samples:
            nodes = s.get("nodes") or []
            if i >= len(nodes):
                continue
            opacities.append(nodes[i].get("opacity") or "")
            filters.append(nodes[i].get("filter") or "")
        if len(set(opacities)) >= 3 or len(set(filters)) >= 3:
            continuous = True
            detail.append({"node": i, "kind": "opacity-filter"})

    return {
        "pointerChanged": continuous,
        "varDelta": var_delta,
        "continuous": continuous,
        "sampleCount": len(samples),
        "detail": detail[:6],
        "hasProbeTarget": True,
        "samples": samples,
    }


def _pointer_reactivity(url: str) -> dict:
    """Move mouse across ≥3 points on theater nodes; require continuous delta."""
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
sample_js = {POINTER_SAMPLE_JS!r}
points = [(360, 320), (720, 380), (1080, 440), (540, 500)]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(600)
    samples = []
    for (x, y) in points:
        page.mouse.move(x, y)
        page.wait_for_timeout(160)
        samples.append(page.evaluate(sample_js))
    browser.close()
    print(json.dumps({{'rawSamples': samples}}))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "pointerChanged": False, "continuous": False}
    raw = json.loads(proc.stdout.strip().splitlines()[-1])
    result = _continuous_pointer_delta(raw.get("rawSamples") or [])
    result["rawSamples"] = raw.get("rawSamples")
    return result


REDUCED_MOTION_JS = """() => {
  const running = [];
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    const name = cs.animationName;
    if (!name || name === 'none') continue;
    const iter = cs.animationIterationCount;
    const play = cs.animationPlayState;
    if (iter === 'infinite' && play !== 'paused') {
      running.push({
        tag: el.tagName,
        animation: name,
        playState: play,
      });
    }
  }
  return {
    infiniteRunning: running.length,
    samples: running.slice(0, 8),
    ok: running.length === 0,
  };
}"""


def _reduced_motion_probe(url: str) -> dict:
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.emulate_media(reduced_motion='reduce')
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(800)
    result = page.evaluate({REDUCED_MOTION_JS!r})
    browser.close()
    print(json.dumps(result))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "ok": False, "infiniteRunning": -1}
    return json.loads(proc.stdout.strip().splitlines()[-1])


SMOOTH_NAV_JS = """() => new Promise((resolve) => {
  const anchor = Array.from(document.querySelectorAll('a[href^="#"]'))
    .find((a) => {
      const href = a.getAttribute('href') || '';
      return href.length > 1 && !href.startsWith('#/');
    });
  if (!anchor) {
    resolve({ hasAnchor: false, frameCount: 0, smoothScrolls: false });
    return;
  }
  const targetId = anchor.getAttribute('href').slice(1);
  const target = document.getElementById(targetId);
  if (!target) {
    resolve({ hasAnchor: true, frameCount: 0, smoothScrolls: false, reason: 'no-target' });
    return;
  }
  let frames = 0;
  let lastY = window.scrollY;
  const start = performance.now();
  const tick = () => {
  const y = window.scrollY;
  if (Math.abs(y - lastY) > 0.5) {
    frames += 1;
    lastY = y;
  }
  if (performance.now() - start < 600) {
    requestAnimationFrame(tick);
  } else {
    resolve({
      hasAnchor: true,
      frameCount: frames,
      smoothScrolls: frames >= 3,
      finalY: Math.round(y),
    });
  }
  };
  anchor.click();
  requestAnimationFrame(tick);
})"""


def _smooth_nav_probe(url: str) -> dict:
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(600)
    result = page.evaluate({SMOOTH_NAV_JS!r})
    browser.close()
    print(json.dumps(result))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "hasAnchor": False, "frameCount": 0}
    return json.loads(proc.stdout.strip().splitlines()[-1])


SCROLL_SAMPLE_JS = f"""() => {{
  const selectors = {json.dumps(SCROLL_SIGNAL_SELECTORS)};
  const nodes = [];
  const seen = new Set();
  for (const sel of selectors) {{
    try {{
      for (const el of document.querySelectorAll(sel)) {{
        const key = el.tagName + '#' + (el.id || '') + '.' + String(el.className || '').slice(0, 40);
        if (seen.has(key)) continue;
        seen.add(key);
        const cs = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        // Skip fully off-screen or zero-size noise
        if (rect.width < 2 || rect.height < 2) continue;
        nodes.push({{
          sel,
          tag: el.tagName,
          transform: cs.transform,
          opacity: cs.opacity,
          filter: cs.filter,
          bg: cs.backgroundColor,
        }});
        if (nodes.length >= 10) break;
      }}
    }} catch (e) {{}}
    if (nodes.length >= 10) break;
  }}
  const body = document.body;
  return {{
    // Primary signals: generic visual props on theater/layout nodes
    nodes,
    canvas: document.querySelectorAll('canvas').length,
    // Fallback only (haoqi-class implementations may still use these)
    bodyClass: (body.className || '').toString().slice(0, 100),
    bodyBg: getComputedStyle(body).backgroundColor,
  }};
}}"""


SCROLL_TO_FRAC_JS = """() => {
  let max = Math.max(document.documentElement.scrollHeight - innerHeight, 0);
  let best = document.scrollingElement;
  for (const el of [document.documentElement, document.body, ...document.querySelectorAll('*')]) {
    if (!el) continue;
    const m = (el.scrollHeight || 0) - (el.clientHeight || 0);
    if (m > max) { max = m; best = el; }
  }
  const y = Math.round(max * __FRAC__);
  if (best === document.documentElement || best === document.body) window.scrollTo(0, y);
  else if (best) best.scrollTop = y;
}"""


def _scroll_state_count(url: str, fracs=(0.0, 0.25, 0.5, 0.75, 1.0)) -> dict:
    """Sample broad-spectrum visual signals across scroll fractions.

    Primary: transform/opacity/filter on generic theater/layout nodes.
    Fallback: bodyClass/bodyBg (implementation-specific; not sole signal).
    """
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
fracs = {list(fracs)!r}
sample_js = {SCROLL_SAMPLE_JS!r}
scroll_to_js = {SCROLL_TO_FRAC_JS!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(500)
    states = []
    for frac in fracs:
        page.evaluate(scroll_to_js.replace('__FRAC__', str(frac)))
        page.wait_for_timeout(220)
        sample = page.evaluate(sample_js)
        primary = {{
            'nodes': sample.get('nodes'),
            'canvas': sample.get('canvas'),
        }}
        states.append({{'frac': frac, 'primary': primary, 'fallback': {{
            'bodyClass': sample.get('bodyClass'),
            'bodyBg': sample.get('bodyBg'),
        }}}})
    browser.close()
    primary_keys = [json.dumps(s['primary'], sort_keys=True) for s in states]
    uniq_primary = len(set(primary_keys))
    if uniq_primary >= 2:
        uniq = uniq_primary
    else:
        uniq = len({{json.dumps({{'p': s['primary'], 'f': s['fallback']}}, sort_keys=True) for s in states}})
    print(json.dumps({{'states': states, 'distinctStates': uniq, 'distinctPrimary': uniq_primary}}))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=150
    )
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "distinctStates": 0}
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _load_sharp_edges(signal_path: str | None) -> list[str]:
    if not signal_path:
        return []
    path = Path(signal_path)
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    edges: list[str] = []
    # Collect lines under sharp-edge / Two-Reference style headings + bare bullets mentioning motion
    for line in text.splitlines():
        low = line.lower()
        if "sharp" in low or "cursor" in low or "stagger" in low or "magnetic" in low or "intro" in low:
            edges.append(line.strip())
    return edges


REPLICA_ONLY_PROBE_JS = f"""() => {{
  const selectors = {json.dumps(REPLICA_ONLY_SELECTORS)};
  const hits = [];
  for (const sel of selectors) {{
    try {{
      const els = document.querySelectorAll(sel);
      if (els.length) {{
        hits.push({{
          selector: sel,
          count: els.length,
          sampleClass: (els[0].className || '').toString().slice(0, 80),
        }});
      }}
    }} catch (e) {{}}
  }}
  return {{ hits, detected: hits.length > 0 }};
}}"""


def _replica_only_motion(url: str, sharp_edges: list[str] | None = None) -> dict:
    """Hit REPLICA_ONLY_SELECTORS; undeclared hits → blocker candidate."""
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(400)
    result = page.evaluate({REPLICA_ONLY_PROBE_JS!r})
    browser.close()
    print(json.dumps(result))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        return {
            "error": proc.stderr or proc.stdout,
            "detected": False,
            "declared_as_sharp_edge": False,
        }
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    edges_blob = " ".join(sharp_edges or []).lower()
    declared = False
    undeclared = []
    for hit in data.get("hits") or []:
        sel = (hit.get("selector") or "").lower()
        sample = (hit.get("sampleClass") or "").lower()
        tokens = [
            t
            for t in (
                "cursor-trail",
                "cursor-follow",
                "cursor",
                "stagger-intro",
                "stagger",
                "intro",
                "magnetic",
                "data-intro",
            )
            if t in sel or t in sample
        ]
        if any(tok in edges_blob for tok in tokens) or (
            edges_blob and any(tok in edges_blob for tok in ("cursor trail", "intro stagger", "magnetic"))
        ):
            declared = True
        else:
            undeclared.append(hit)
    data["declared_as_sharp_edge"] = declared and not undeclared
    data["undeclared"] = undeclared
    data["detected"] = bool(data.get("hits"))
    return data


def _parity_report(
    target: dict,
    replica: dict,
    min_ratio: float,
    pointer: dict,
    scroll_states: dict,
    reduced_motion: dict | None = None,
    smooth_nav_target: dict | None = None,
    smooth_nav_replica: dict | None = None,
    replica_only: dict | None = None,
) -> dict:
    blockers: list[str] = []
    notes: list[str] = []

    t_canvas = int(target.get("canvasCount") or 0)
    r_canvas = int(replica.get("canvasCount") or 0)
    t_webgl = bool(target.get("webgl"))
    r_webgl = bool(replica.get("webgl"))
    t_max = int(target.get("maxScroll") or 0)
    r_max = int(replica.get("maxScroll") or 0)
    ratio = (r_max / t_max) if t_max else 1.0

    # v5: require continuous theater delta — not binary hover flip
    pointer_ok = bool(pointer.get("continuous") or pointer.get("varDelta"))

    if t_canvas > 0 and r_canvas == 0:
        if pointer_ok:
            notes.append(
                "canvasCount mismatch but continuous CSS/pointer theater proven — stand-in OK if SIGNAL declares strategy"
            )
        else:
            blockers.append("canvas")
            notes.append(
                "Static Snapshot Syndrome: target has canvas, replica has 0 and no continuous pointer theater delta"
            )

    if t_webgl and not r_webgl and r_canvas == 0 and "canvas" not in blockers:
        if not pointer_ok:
            blockers.append("webgl")

    if t_max > 0 and ratio < min_ratio:
        blockers.append("scroll-length")
        notes.append(f"scroll-length ratio {ratio:.3f} < {min_ratio}")

    t_lenis = bool(target.get("hasLenis"))
    r_lenis = bool(replica.get("hasLenis"))
    if t_lenis and not r_lenis:
        notes.append("Lenis absent on replica — P1 unless Interaction Contract accepts native/lerp")

    if (t_canvas > 0 or t_webgl) and not pointer_ok:
        if "canvas" not in blockers:
            blockers.append("pointer-theater")

    distinct = int(scroll_states.get("distinctStates") or 0)
    if t_max >= 4000 and distinct < 2:
        blockers.append("scroll-states")
        notes.append(f"scroll-state count={distinct} on long page (need ≥2 distinct states)")

    rm = reduced_motion or {}
    if rm.get("infiniteRunning", 0) > 0:
        blockers.append("reduced-motion")
        notes.append(
            f"infinite CSS animations still running under prefers-reduced-motion "
            f"(count={rm.get('infiniteRunning')})"
        )

    t_nav = smooth_nav_target or {}
    r_nav = smooth_nav_replica or {}
    target_smooth = bool(t_nav.get("smoothScrolls"))
    if target_smooth:
        replica_frames = int(r_nav.get("frameCount") or 0)
        if replica_frames < 3:
            blockers.append("smooth-nav")
            notes.append(
                f"target smooth-scroll ({t_nav.get('frameCount')} frames) but replica "
                f"anchor motion={replica_frames} frames over 600ms (need ≥3)"
            )

    ro = replica_only or {}
    if ro.get("detected") and not ro.get("declared_as_sharp_edge"):
        blockers.append("replica-only-motion")
        notes.append(
            "replica-only motion selectors hit without sharp-edge declaration: "
            + ", ".join(h.get("selector", "?") for h in (ro.get("undeclared") or ro.get("hits") or [])[:5])
        )

    checks = [
        ("canvas_or_standin", "canvas" not in blockers and "webgl" not in blockers),
        ("scroll_length", "scroll-length" not in blockers),
        ("pointer", "pointer-theater" not in blockers),
        ("scroll_states", "scroll-states" not in blockers),
        ("reduced_motion", "reduced-motion" not in blockers),
        ("smooth_nav", "smooth-nav" not in blockers),
        ("replica_only_motion", "replica-only-motion" not in blockers),
    ]
    parity = sum(1 for _, ok in checks if ok) / max(len(checks), 1)

    return {
        "target": {
            "canvasCount": t_canvas,
            "webgl": t_webgl,
            "hasLenis": t_lenis,
            "maxScroll": t_max,
        },
        "replica": {
            "canvasCount": r_canvas,
            "webgl": r_webgl,
            "hasLenis": r_lenis,
            "maxScroll": r_max,
        },
        "scrollLengthRatio": round(ratio, 4),
        "pointer": {
            k: pointer.get(k)
            for k in (
                "pointerChanged",
                "varDelta",
                "continuous",
                "sampleCount",
                "hasProbeTarget",
                "detail",
                "error",
                "reason",
            )
            if k in pointer
        },
        "scrollStates": {
            "distinctStates": distinct,
            "distinctPrimary": scroll_states.get("distinctPrimary"),
            "samples": scroll_states.get("states", [])[:5],
        },
        "reducedMotion": rm,
        "smoothNav": {
            "target": t_nav,
            "replica": r_nav,
        },
        "replicaOnlyMotion": ro,
        "parityScore": round(parity, 3),
        "blockers": blockers,
        "notes": notes,
    }


def _run_target_session(url: str) -> dict:
    """Single Playwright session for all live-target probes (bot-management hygiene)."""
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
runtime_js = {RUNTIME_PROBE_JS!r}
smooth_js = {SMOOTH_NAV_JS!r}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(800)
    runtime = page.evaluate(runtime_js)
    smooth = page.evaluate(smooth_js)
    browser.close()
    print(json.dumps({{'runtime': runtime, 'smoothNav': smooth}}))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=150
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "target session failed")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _run_replica_session(url: str) -> dict:
    """Single Playwright session for all replica behavior probes."""
    script = f"""
from playwright.sync_api import sync_playwright
import json
url = {url!r}
runtime_js = {RUNTIME_PROBE_JS!r}
sample_js = {POINTER_SAMPLE_JS!r}
scroll_js = {SCROLL_SAMPLE_JS!r}
scroll_to_js = {SCROLL_TO_FRAC_JS!r}
reduced_js = {REDUCED_MOTION_JS!r}
smooth_js = {SMOOTH_NAV_JS!r}
replica_only_js = {REPLICA_ONLY_PROBE_JS!r}
points = [(360, 320), (720, 380), (1080, 440), (540, 500)]
fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={{'width': 1440, 'height': 900}})
    page.goto(url, wait_until='networkidle', timeout=60000)
    page.wait_for_timeout(600)
    runtime = page.evaluate(runtime_js)

    pointer_samples = []
    for (x, y) in points:
        page.mouse.move(x, y)
        page.wait_for_timeout(160)
        pointer_samples.append(page.evaluate(sample_js))

    states = []
    for frac in fracs:
        page.evaluate(scroll_to_js.replace('__FRAC__', str(frac)))
        page.wait_for_timeout(220)
        sample = page.evaluate(scroll_js)
        primary = {{'nodes': sample.get('nodes'), 'canvas': sample.get('canvas')}}
        states.append({{'frac': frac, 'primary': primary, 'fallback': {{
            'bodyClass': sample.get('bodyClass'),
            'bodyBg': sample.get('bodyBg'),
        }}}})
    primary_keys = [json.dumps(s['primary'], sort_keys=True) for s in states]
    uniq_primary = len(set(primary_keys))
    if uniq_primary >= 2:
        uniq = uniq_primary
    else:
        uniq = len({{json.dumps({{'p': s['primary'], 'f': s['fallback']}}, sort_keys=True) for s in states}})

    page.evaluate('() => window.scrollTo(0, 0)')
    page.wait_for_timeout(200)
    smooth = page.evaluate(smooth_js)

    replica_only = page.evaluate(replica_only_js)

    ctx = browser.new_context(viewport={{'width': 1440, 'height': 900}}, reduced_motion='reduce')
    page2 = ctx.new_page()
    page2.goto(url, wait_until='networkidle', timeout=60000)
    page2.wait_for_timeout(800)
    reduced = page2.evaluate(reduced_js)
    ctx.close()
    browser.close()
    print(json.dumps({{
        'runtime': runtime,
        'pointerSamples': pointer_samples,
        'scrollStates': {{'states': states, 'distinctStates': uniq, 'distinctPrimary': uniq_primary}},
        'smoothNav': smooth,
        'reducedMotion': reduced,
        'replicaOnly': replica_only,
    }}))
"""
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=180
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "replica session failed")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _finalize_replica_only(raw: dict, sharp_edges: list[str] | None) -> dict:
    data = dict(raw or {})
    edges_blob = " ".join(sharp_edges or []).lower()
    undeclared = []
    declared_all = True
    for hit in data.get("hits") or []:
        sel = (hit.get("selector") or "").lower()
        sample = (hit.get("sampleClass") or "").lower()
        tokens = [
            t
            for t in (
                "cursor-trail",
                "cursor-follow",
                "cursor",
                "stagger-intro",
                "stagger",
                "intro",
                "magnetic",
                "data-intro",
            )
            if t in sel or t in sample
        ]
        ok = any(tok in edges_blob for tok in tokens) or (
            edges_blob
            and any(tok in edges_blob for tok in ("cursor trail", "intro stagger", "magnetic"))
        )
        if not ok:
            declared_all = False
            undeclared.append(hit)
    data["detected"] = bool(data.get("hits"))
    data["declared_as_sharp_edge"] = bool(data.get("hits")) and declared_all and not undeclared
    data["undeclared"] = undeclared
    return data


def cmd_behavior(args: argparse.Namespace) -> int:
    """Live target + replica. Prefer --behavior-offline to avoid re-hitting target."""
    sharp_edges = _load_sharp_edges(getattr(args, "signal", None))
    target_bundle = _run_target_session(args.target)
    replica_bundle = _run_replica_session(args.replica)
    pointer = _continuous_pointer_delta(replica_bundle.get("pointerSamples") or [])
    replica_only = _finalize_replica_only(replica_bundle.get("replicaOnly") or {}, sharp_edges)
    report = _parity_report(
        target_bundle["runtime"],
        replica_bundle["runtime"],
        args.min_ratio,
        pointer,
        replica_bundle["scrollStates"],
        replica_bundle.get("reducedMotion"),
        target_bundle.get("smoothNav"),
        replica_bundle.get("smoothNav"),
        replica_only,
    )
    report["mode"] = "live"
    report["sessions"] = {"target": 1, "replica": 1}
    out = Path(args.out or "behavior-diff.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"wrote {out}")
    if report["blockers"]:
        print(f"FAIL: blockers={report['blockers']}")
        return 1
    print("PASS: no behavior blockers")
    return 0


def cmd_behavior_offline(args: argparse.Namespace) -> int:
    """Recommended Loop 5 default: target from runtime.json; one replica session."""
    target = json.loads(Path(args.runtime).read_text())
    if "target" in target and "canvasCount" not in target:
        target = target["target"]
    sharp_edges = _load_sharp_edges(getattr(args, "signal", None))
    replica_bundle = _run_replica_session(args.replica)
    pointer = _continuous_pointer_delta(replica_bundle.get("pointerSamples") or [])
    replica_only = _finalize_replica_only(replica_bundle.get("replicaOnly") or {}, sharp_edges)
    smooth_nav_target = None
    if target.get("smoothNav") or target.get("hasSmoothNav"):
        smooth_nav_target = target.get("smoothNav") or {
            "smoothScrolls": True,
            "frameCount": target.get("smoothNavFrames", 3),
        }
    report = _parity_report(
        target,
        replica_bundle["runtime"],
        args.min_ratio,
        pointer,
        replica_bundle["scrollStates"],
        replica_bundle.get("reducedMotion"),
        smooth_nav_target,
        replica_bundle.get("smoothNav"),
        replica_only,
    )
    report["mode"] = "offline-target"
    report["sessions"] = {"target": 0, "replica": 1}
    out = Path(args.out or "behavior-diff.json")
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"wrote {out}")
    if report["blockers"]:
        print(f"FAIL: blockers={report['blockers']}")
        return 1
    print("PASS: no behavior blockers")
    return 0


def cmd_reduced_motion(args: argparse.Namespace) -> int:
    result = _reduced_motion_probe(args.url)
    print(json.dumps(result, indent=2))
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return 2
    if result.get("infiniteRunning", 0) > 0:
        print(
            f"FAIL: {result['infiniteRunning']} infinite CSS animation(s) still running "
            "under prefers-reduced-motion:reduce"
        )
        return 1
    print("PASS: no infinite CSS animations under prefers-reduced-motion")
    return 0


def cmd_smooth_nav(args: argparse.Namespace) -> int:
    result = _smooth_nav_probe(args.url)
    print(json.dumps(result, indent=2))
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return 2
    if not result.get("hasAnchor"):
        print("SKIP: no in-page anchor link found")
        return 0
    frames = int(result.get("frameCount") or 0)
    if frames < 3:
        print(f"FAIL: anchor scroll produced {frames} motion frames over 600ms (need ≥3)")
        return 1
    print(f"PASS: smooth anchor scroll ({frames} frames over 600ms)")
    return 0


def cmd_replica_only(args: argparse.Namespace) -> int:
    sharp = _load_sharp_edges(getattr(args, "signal", None))
    result = _replica_only_motion(args.url, sharp)
    print(json.dumps(result, indent=2))
    if result.get("error"):
        print(f"ERROR: {result['error']}")
        return 2
    if result.get("detected") and not result.get("declared_as_sharp_edge"):
        print("FAIL: replica-only-motion detected without sharp-edge declaration")
        return 1
    if result.get("detected"):
        print("PASS: replica-only motion declared as sharp edge")
    else:
        print("PASS: no replica-only motion selectors")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--imr", nargs=2, metavar=("TARGET", "REPLICA"))
    ap.add_argument("--diff", nargs=2, metavar=("TARGET", "REPLICA"))
    ap.add_argument("--typescale", metavar="URL")
    ap.add_argument("--density", metavar="URL")
    ap.add_argument("--rhythm", metavar="IMAGE")
    ap.add_argument(
        "--scroll-length",
        nargs=2,
        metavar=("OFFSETS_JSON", "REPLICA_URL"),
        help="Compare replica maxScroll to offsets.json maxScroll",
    )
    ap.add_argument(
        "--behavior",
        nargs=2,
        metavar=("TARGET_URL", "REPLICA_URL"),
        help="Live runtime parity (supplemental). Prefer --behavior-offline. Target probes share 1 session.",
    )
    ap.add_argument(
        "--behavior-offline",
        nargs=2,
        metavar=("RUNTIME_JSON", "REPLICA_URL"),
        help="Recommended Loop 5 default: compare replica (1 session) to recon/runtime.json",
    )
    ap.add_argument(
        "--reduced-motion",
        metavar="URL",
        help="Emulate prefers-reduced-motion:reduce; fail if infinite CSS animations run",
    )
    ap.add_argument(
        "--smooth-nav",
        metavar="URL",
        help="Click first in-page anchor; fail if <3 scroll motion frames over 600ms",
    )
    ap.add_argument(
        "--replica-only",
        metavar="URL",
        help="Fail if replica-only motion selectors present without SIGNAL sharp-edge declaration",
    )
    ap.add_argument(
        "--signal",
        default="",
        help="Path to docs/SIGNAL.md (sharp edges for replica-only-motion waiver)",
    )
    ap.add_argument("--tolerance", type=float, default=8.0)
    ap.add_argument("--bands", type=int, default=3)
    ap.add_argument("--out", default="")
    ap.add_argument("--min-ratio", type=float, default=0.85)
    ap.add_argument("--target-series", default="")
    ap.add_argument("--target-imr-series", dest="target_series", default="")

    args = ap.parse_args()

    if args.imr:
        ns = argparse.Namespace(
            target=args.imr[0], replica=args.imr[1], tolerance=args.tolerance, bands=args.bands
        )
        return cmd_imr(ns)
    if args.diff:
        ns = argparse.Namespace(
            target=args.diff[0], replica=args.diff[1], out=args.out or "diff-heatmap.png"
        )
        return cmd_diff(ns)
    if args.typescale:
        return cmd_typescale(argparse.Namespace(url=args.typescale))
    if args.density:
        return cmd_density(argparse.Namespace(url=args.density))
    if args.rhythm:
        return cmd_rhythm(
            argparse.Namespace(
                image=args.rhythm, bands=args.bands, target_series=args.target_series or None
            )
        )
    if args.scroll_length:
        return cmd_scroll_length(
            argparse.Namespace(
                offsets=args.scroll_length[0],
                url=args.scroll_length[1],
                min_ratio=args.min_ratio,
            )
        )
    if args.behavior_offline:
        return cmd_behavior_offline(
            argparse.Namespace(
                runtime=args.behavior_offline[0],
                replica=args.behavior_offline[1],
                out=args.out or "behavior-diff.json",
                min_ratio=args.min_ratio,
                signal=args.signal or None,
            )
        )
    if args.behavior:
        return cmd_behavior(
            argparse.Namespace(
                target=args.behavior[0],
                replica=args.behavior[1],
                out=args.out or "behavior-diff.json",
                min_ratio=args.min_ratio,
                signal=args.signal or None,
            )
        )
    if args.reduced_motion:
        return cmd_reduced_motion(argparse.Namespace(url=args.reduced_motion))
    if args.smooth_nav:
        return cmd_smooth_nav(argparse.Namespace(url=args.smooth_nav))
    if args.replica_only:
        return cmd_replica_only(
            argparse.Namespace(url=args.replica_only, signal=args.signal or None)
        )
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
