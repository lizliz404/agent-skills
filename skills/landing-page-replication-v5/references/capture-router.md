# When to load: Loop 0 — non-SSR targets, empty curl bodies, or 403/challenge pages
# Precondition: Target URL + writable `recon/` directory
# Output: Route chosen + capture artifacts listed in pipeline.yaml (incl. runtime.json)

# Capture Router (v5)

curl is a **fast path**, not the default for every stack. Route by fingerprint, then save more than HTML. **v5 requires runtime surface capture** for theater-class targets.

## Artifacts (always aim for these)

| Artifact | Purpose |
|----------|---------|
| `recon/headers.txt` | Framework + CDN + CSP CDNs |
| `recon/index.html` | Curl body **or** Playwright `page.content()` |
| `recon/dom.html` | Post-hydration `document.documentElement.outerHTML` when SPA/Framer |
| `recon/computed.json` | Computed styles for H1/H2/body/primary button |
| `recon/css/` | Fetched stylesheet chunks |
| `recon/screenshots/` | Density acceptance set (≥5) + `scroll-00…N` for long pages |
| `recon/assets.json` | canvases / imgs / videos — feeds Static Snapshot gate |
| `recon/offsets.json` | section tops + **maxScroll** — feeds scroll-length gate |
| `recon/runtime.json` | canvasCount, webgl, Lenis, scrollContainers — feeds Behavior |

## Fingerprint → route

| Fingerprint | Route |
|-------------|-------|
| `x-nextjs-prerender` / `/_next/` + real `<h1>` in curl | **curl fast path** + fetch CSS chunks; still run `capture-runtime.py` if interactive |
| `__next` / RSC shell but **no** real headings | Playwright wait for hydration → save `dom.html` |
| Vite / SPA (`#root` / `#app` empty of product copy) | Playwright + `networkidle` / wait for selector |
| Framer (`*.framer.*`, `data-framer`) | Playwright **required** — Framer often ships little author CSS; rely on `computed.json` |
| Webflow (`.w-` classes, `webflow.css`) | curl + fetch Webflow CSS chunks; vision for spacing |
| Astro / Nuxt with SSR content | curl fast path |
| `<canvas>` / Lenis / WebGL portfolio | Playwright **required** + `capture-runtime.py` + scroll progression shots |
| Cloudflare Turnstile / 403 challenge / Datadome | **Escalate to manual DevTools** (Network + Elements). Document as legitimate Loop 0 — not a failure. |
| Google Fonts / Typekit only (no woff2 filenames) | curl OK; `extract-tokens.py` parses families from link URLs |

## Bot management (2026 default failure mode)

Known SaaS targets often block **both** curl and default headless Chromium.

Legitimate Loop 0 when blocked:
1. Open the live site in a normal browser.
2. DevTools → Network: copy response headers → `headers.txt`.
3. Elements: save outerHTML of meaningful root (or copy computed styles for H1/body/button).
4. Screenshots still required — they remain the density bar.
5. Manually note runtime: canvas count, inner scroller, approx scroll height → stub `runtime.json`.
6. Note in SIGNAL.md: `Dump quality: bot-blocked; manual capture`.

Do not burn hours fighting fingerprints before using manual capture.

## Computed styles (required when CSS is opaque)

In Playwright (or DevTools console):

```js
() => {
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
      backgroundColor: s.backgroundColor,
    };
  };
  return {
    h1: pick("h1"),
    h2: pick("h2"),
    body: pick("body"),
    button: pick("a[href*='signup'], a[href*='start'], button, .btn, [class*='button']"),
  };
}
```

Save as `recon/computed.json`. Feed TSS gate via `audit.py --typescale` (live) or compare manually in SIGNAL.md.

## Runtime probe (required for theater-class)

```bash
python3 scripts/capture-runtime.py --url https://target.com --out recon/runtime.json
```

Minimal contract:

```json
{
  "canvasCount": 2,
  "webgl": true,
  "hasLenis": true,
  "maxScroll": 12319,
  "scrollContainers": [{ "className": "lenis", "maxScroll": 12319 }],
  "flags": { "WEBGL_THEATER": true, "INNER_SCROLLER": true, "LENIS": true }
}
```

If `WEBGL_THEATER` → tag SIGNAL + fill Interaction Contract rows before Skeleton.

## Screenshots (always)

1. Full-page scroll
2. Hero (product collage / theater region)
3. Densest product-demo section
4. Dark feature band (if any)
5. Nav at top **and** mid-scroll
6. **Long pages:** `scroll-00` … `scroll-05` at 0/20/40/60/80/100% (tunnel evidence)

These images are Loop 3 acceptance criteria; scroll progression is Loop 5 evidence.

## CLI

```bash
python3 scripts/capture.py --url https://target.com --out recon/
# Force Playwright:
python3 scripts/capture.py --url https://target.com --out recon/ --engine playwright
# Skip screenshots (CI / headless missing):
python3 scripts/capture.py --url https://target.com --out recon/ --no-shots
# Runtime only:
python3 scripts/capture-runtime.py --url https://target.com --out recon/runtime.json
```
