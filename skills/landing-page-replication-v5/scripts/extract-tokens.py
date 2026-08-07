#!/usr/bin/env python3
"""Extract ranked design signals from a landing-page HTML dump and/or CSS files.

Evidence-driven (attio-recon + v3 audits): modern SSR dumps often lack
font-family declarations and <section id> markers. Useful signals:
  - /_next/static/media/* font filenames
  - Google Fonts / Typekit link URLs (v3 — not just .css / woff2)
  - Ranked hex/rgba, headings, stylesheet URLs, filtered CSS vars
  - Tailwind arbitrary values, @keyframes, SVG density
  - Recursive @import fetch (depth ≤3), --json, fetch size cap

Usage:
    python3 extract-tokens.py recon/index.html
    python3 extract-tokens.py recon/index.html --base-url https://target.com
    python3 extract-tokens.py recon/index.html --base-url https://target.com --fetch-css recon/css
    python3 extract-tokens.py recon/index.html --json
    python3 extract-tokens.py recon/css/*.css
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from html import unescape
from pathlib import Path

MAX_FETCH_BYTES = 2_000_000
IMPORT_DEPTH = 3

GOOGLE_FONTS_RE = re.compile(
    r"https?://fonts\.googleapis\.com/css2?\?[^\"'>\s]*|"
    r"//fonts\.googleapis\.com/css2?\?[^\"'>\s]*",
    re.I,
)
TYPEKIT_RE = re.compile(
    r"https?://use\.typekit\.net/[^\"'>\s]+|//use\.typekit\.net/[^\"'>\s]+",
    re.I,
)
IMPORT_URL_RE = re.compile(
    r"""@import\s+(?:url\()?['"]?([^'")\s]+)['"]?\)?""",
    re.I,
)

# Runtime / layout vars that dominated attio-recon and are not design tokens.
NOISE_VAR_PREFIXES = (
    "--idx",
    "--max-idx",
    "--max-id",
    "--stagger",
    "--tick-",
    "--line-in",
    "--line-out",
    "--cell-",
    "--nav-idle",
    "--results-",
    "--artwork-",
    "--cta-pattern",
    "--site-header",
    "--tic",
)

TOKENISH_VAR_RE = re.compile(
    r"^--(?:color|colour|font|radius|radii|shadow|space|spacing|size|text|"
    r"bg|background|border|ease|duration|tracking|leading|z|opacity|blur)[\w-]*$",
    re.I,
)

FONT_NAME_HINTS = re.compile(
    r"(inter[_-]display|inter|tiempos[_-]?\w*|geist(?:[_-]?\w*)?|satoshi|"
    r"cabinet[_-]?\w*|general[_-]?sans|swiss|helvetica|roboto|source[_-]serif|"
    r"source[_-]sans|ibm[_-]plex|noto[_-]?\w*|playfair|georgia|mono|jetbrains|"
    r"fira|menlo|sf[_-]?pro|abc[_-]?\w*|gt[_-]?\w*)",
    re.I,
)


def _strip_tags(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _is_noise_var(name: str) -> bool:
    lower = name.lower()
    return any(lower == p or lower.startswith(p) for p in NOISE_VAR_PREFIXES)


def _google_fonts_families(text: str) -> list[str]:
    families: list[str] = []
    for match in GOOGLE_FONTS_RE.findall(text):
        qs = match.split("?", 1)[-1] if "?" in match else ""
        for fam in re.findall(r"family=([^&\"'>]+)", qs):
            name = urllib.parse.unquote(fam.split(":")[0]).replace("+", " ").strip()
            if name:
                families.append(name)
    return sorted(set(families))


def _typekit_kits(text: str) -> list[str]:
    kits = []
    for match in TYPEKIT_RE.findall(text):
        kits.append(match.split("?")[0].rstrip("/"))
    return sorted(set(kits))


def _font_from_media_url(url: str) -> str | None:
    name = url.split("/")[-1].split("?")[0].lower()
    if not name.endswith((".woff2", ".woff", ".ttf", ".otf")):
        return None
    stem = re.sub(r"\.(woff2|woff|ttf|otf)$", "", name)
    # next/font hashed names: inter_display_semibold-s.p.xxxxx
    stem = re.sub(r"-s\.p\..*$", "", stem)
    stem = re.sub(r"\.[a-z0-9~_-]{6,}$", "", stem)
    m = FONT_NAME_HINTS.search(stem.replace("-", "_"))
    if m:
        return m.group(1).replace("_", " ").replace("-", " ")
    # fallback: humanize leading alpha tokens before hash
    parts = re.split(r"[-_]", stem)
    alpha = [p for p in parts if p.isalpha() and len(p) > 2][:3]
    if alpha:
        return " ".join(alpha)
    return None


def analyze_text(text: str, source_label: str) -> dict:
    custom_all = Counter(re.findall(r"--[\w-]+", text))
    custom_tokenish = Counter()
    custom_other = Counter()
    for name, count in custom_all.items():
        if _is_noise_var(name):
            continue
        if TOKENISH_VAR_RE.match(name) or name.startswith("--color-"):
            custom_tokenish[name] = count
        else:
            custom_other[name] = count

    font_families = sorted(
        {
            f.strip().strip("'\"")
            for f in re.findall(r"font-family:\s*([^;}{]+)", text, flags=re.I)
            if f.strip()
        }
    )

    media_urls = sorted(
        set(
            re.findall(
                r"""(?:src|href)=["']([^"']+\.(?:woff2|woff|ttf|otf)[^"']*)["']""",
                text,
                flags=re.I,
            )
        )
        | set(re.findall(r"""url\((['"]?)([^"'()]+\.(?:woff2|woff|ttf|otf)[^"'()]*)\1\)""", text, flags=re.I))
    )
    # url() groups return tuples when using the second pattern — normalize
    normalized_media: list[str] = []
    for item in re.findall(
        r"""(?:src|href)=["']([^"']+\.(?:woff2|woff|ttf|otf)[^"']*)["']""",
        text,
        flags=re.I,
    ):
        normalized_media.append(item)
    for item in re.findall(
        r"""url\((['"]?)([^"'()]+\.(?:woff2|woff|ttf|otf)[^"'()]*)\1\)""",
        text,
        flags=re.I,
    ):
        normalized_media.append(item[1] if isinstance(item, tuple) else item)

    fonts_from_files = Counter()
    for url in normalized_media:
        hint = _font_from_media_url(url)
        if hint:
            fonts_from_files[hint.lower()] += 1

    hex_colors = Counter(c.lower() for c in re.findall(r"#[0-9a-fA-F]{3,8}\b", text))
    rgba_colors = Counter(re.findall(r"rgba?\([^)]+\)", text))
    oklch_colors = Counter(re.findall(r"oklch\([^)]+\)", text))
    hsl_colors = Counter(re.findall(r"hsla?\([^)]+\)", text))

    keyframes = sorted(set(re.findall(r"@keyframes\s+([\w-]+)", text)))

    stylesheet_urls = sorted(
        set(
            re.findall(
                r"""<link[^>]+href=["']([^"']+\.css[^"']*)["']""",
                text,
                flags=re.I,
            )
        )
        | set(
            re.findall(
                r"""href=["']([^"']*/_next/static/chunks/[^"']+\.css[^"']*)["']""",
                text,
                flags=re.I,
            )
        )
        # Google Fonts css2?family=… has no literal ".css" adjacency
        | set(GOOGLE_FONTS_RE.findall(text))
        | set(TYPEKIT_RE.findall(text))
    )
    stylesheet_urls = sorted(
        {
            u.rstrip("\\")
            for u in set(stylesheet_urls)
            | set(re.findall(r"/_next/static/chunks/[^\"'\\>]+\.css[^\"'\\>]*", text))
            | set(IMPORT_URL_RE.findall(text))
        }
    )

    google_fonts = _google_fonts_families(text)
    typekit_kits = _typekit_kits(text)

    headings: list[tuple[str, str]] = []
    for tag in ("h1", "h2", "h3"):
        for raw in re.findall(rf"<{tag}\b[^>]*>(.*?)</{tag}>", text, flags=re.I | re.S):
            clean = _strip_tags(raw)
            if clean and len(clean) < 200:
                headings.append((tag, clean))

    section_ids = sorted(
        set(re.findall(r"""<section\b[^>]*\bid=["']([^"']+)["']""", text, flags=re.I))
    )
    data_landmarks = sorted(
        set(
            re.findall(
                r"\s(data-(?:home|hero|section|feature|nav|header|footer)[\w-]*)=",
                text,
                flags=re.I,
            )
        )
    )

    arbitrary = Counter(
        re.findall(
            r"(?:text|leading|tracking|rounded|gap|p|px|py|pt|pb|m|mx|my|"
            r"w|h|size|top|left|right|bottom|max-w|min-h)-\[([^\]]+)\]",
            text,
        )
    )

    # Radius-like and tracking-like subsets
    radius_hits = Counter(
        v for k, c in arbitrary.items() for v in [k] * c if "px" in k or "rem" in k
    )

    svg_count = len(re.findall(r"<svg\b", text, flags=re.I))
    path_count = len(re.findall(r"<path\b", text, flags=re.I))
    clip_count = len(re.findall(r"clippath|clip-path", text, flags=re.I))

    fingerprints = {
        "nextjs": bool(
            re.search(r"/_next/|__next|x-nextjs|next-router", text, flags=re.I)
        ),
        "vercel": "vercel" in text.lower(),
        "storyblok": "storyblok" in text.lower(),
        "framer": bool(re.search(r"framer|data-framer", text, flags=re.I)),
        "webflow": "webflow" in text.lower(),
        "vite_spa": bool(re.search(r"""id=["'](?:root|app)["']""", text, flags=re.I)),
        "tailwind_hints": bool(
            re.search(r"\b(?:flex|items-center|rounded-full|tracking-\[)", text)
        ),
        "google_fonts": bool(google_fonts),
        "typekit": bool(typekit_kits),
    }

    return {
        "source": source_label,
        "custom_tokenish": custom_tokenish,
        "custom_other": custom_other,
        "custom_noise_dropped": sum(
            c for n, c in custom_all.items() if _is_noise_var(n)
        ),
        "font_families": font_families,
        "fonts_from_files": fonts_from_files,
        "fonts_google": google_fonts,
        "typekit_kits": typekit_kits,
        "font_urls": sorted(set(normalized_media)),
        "hex_colors": hex_colors,
        "rgba_colors": rgba_colors,
        "oklch_colors": oklch_colors,
        "hsl_colors": hsl_colors,
        "keyframes": keyframes,
        "stylesheet_urls": stylesheet_urls,
        "headings": headings,
        "section_ids": section_ids,
        "data_landmarks": data_landmarks,
        "arbitrary_top": arbitrary,
        "radius_spacing_candidates": radius_hits,
        "svg_count": svg_count,
        "path_count": path_count,
        "clip_count": clip_count,
        "fingerprints": fingerprints,
    }


def merge_results(results: list[dict]) -> dict:
    if len(results) == 1:
        return results[0]
    base = results[0]
    for extra in results[1:]:
        for key in (
            "custom_tokenish",
            "custom_other",
            "fonts_from_files",
            "hex_colors",
            "rgba_colors",
            "oklch_colors",
            "hsl_colors",
            "arbitrary_top",
            "radius_spacing_candidates",
        ):
            base[key] = base[key] + extra[key]
        base["font_families"] = sorted(set(base["font_families"]) | set(extra["font_families"]))
        base["fonts_google"] = sorted(
            set(base.get("fonts_google", [])) | set(extra.get("fonts_google", []))
        )
        base["typekit_kits"] = sorted(
            set(base.get("typekit_kits", [])) | set(extra.get("typekit_kits", []))
        )
        base["font_urls"] = sorted(set(base["font_urls"]) | set(extra["font_urls"]))
        base["keyframes"] = sorted(set(base["keyframes"]) | set(extra["keyframes"]))
        base["stylesheet_urls"] = sorted(
            set(base["stylesheet_urls"]) | set(extra["stylesheet_urls"])
        )
        base["section_ids"] = sorted(set(base["section_ids"]) | set(extra["section_ids"]))
        base["data_landmarks"] = sorted(
            set(base["data_landmarks"]) | set(extra["data_landmarks"])
        )
        seen = {h for _, h in base["headings"]}
        for tag, h in extra["headings"]:
            if h not in seen:
                base["headings"].append((tag, h))
                seen.add(h)
        base["svg_count"] += extra["svg_count"]
        base["path_count"] += extra["path_count"]
        base["clip_count"] += extra["clip_count"]
        base["custom_noise_dropped"] += extra["custom_noise_dropped"]
        for k, v in extra["fingerprints"].items():
            base["fingerprints"][k] = base["fingerprints"].get(k, False) or v
        base["source"] = base["source"] + " + " + extra["source"]
    return base


def _resolve_url(url: str, base_url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http"):
        return url
    base = base_url.rstrip("/")
    return f"{base}{url if url.startswith('/') else '/' + url}"


def _safe_fetch(url: str, max_bytes: int = MAX_FETCH_BYTES) -> bytes:
    full = url if "://" in url else url
    parsed = urllib.parse.urlparse(full)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"refusing non-http(s) URL: {full}")
    req = urllib.request.Request(
        full,
        headers={"User-Agent": "landing-page-replication-v5/extract-tokens"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        final = urllib.parse.urlparse(resp.geturl())
        if final.scheme not in ("http", "https"):
            raise ValueError(f"redirect to non-http(s): {resp.geturl()}")
        data = resp.read(max_bytes + 1)
        if len(data) > max_bytes:
            data = data[:max_bytes]
            print(f"  truncated {full} to {max_bytes} bytes", file=sys.stderr)
        return data


def fetch_css(
    urls: list[str],
    base_url: str,
    out_dir: Path,
    depth: int = IMPORT_DEPTH,
) -> list[Path]:
    """Fetch stylesheets; recurse @import up to `depth` levels."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(u, 0) for u in urls]

    i = 0
    while queue:
        url, level = queue.pop(0)
        full = _resolve_url(url, base_url)
        if full in seen:
            continue
        seen.add(full)
        fname = re.sub(r"[^\w.-]+", "_", full.split("?")[0].split("/")[-1]) or f"chunk-{i}.css"
        if not fname.endswith(".css"):
            fname += ".css"
        dest = out_dir / fname
        i += 1
        try:
            body = _safe_fetch(full)
            dest.write_bytes(body)
            saved.append(dest)
            print(f"  fetched {full} -> {dest}", file=sys.stderr)
            if level < depth:
                text = body.decode("utf-8", errors="replace")
                for imp in IMPORT_URL_RE.findall(text):
                    if imp.startswith(("http", "/", "//")) or imp.endswith(".css"):
                        queue.append((imp, level + 1))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            print(f"  FAILED {full}: {exc}", file=sys.stderr)
    return saved


def _serialize(data: dict) -> dict:
    """JSON-friendly view of analysis counters."""
    out = {}
    for k, v in data.items():
        if isinstance(v, Counter):
            out[k] = v.most_common(100)
        else:
            out[k] = v
    return out


def print_report(data: dict, max_hex: int = 40) -> None:
    def block(title: str) -> None:
        print(f"\n{'=' * 64}")
        print(f"  {title}")
        print(f"{'=' * 64}")

    print(f"Source: {data['source']}")

    block("Framework fingerprints")
    for k, v in data["fingerprints"].items():
        print(f"  {k:16s} {v}")

    block("Fonts from file URLs (preferred on Next.js)")
    if data["fonts_from_files"]:
        for name, count in data["fonts_from_files"].most_common(30):
            print(f"  {count:4d}  {name}")
    else:
        print("  (none found — check Google Fonts / Typekit / CSS @font-face / vision)")
    gf = data.get("fonts_google") or []
    if gf:
        print("\n  Google Fonts families:")
        for f in gf:
            print(f"    {f}")
    tk = data.get("typekit_kits") or []
    if tk:
        print("\n  Adobe Fonts / Typekit kits:")
        for f in tk:
            print(f"    {f}")
    if data["font_families"]:
        print("\n  font-family declarations:")
        for f in data["font_families"][:30]:
            print(f"    {f}")

    block("Headings → story arc")
    if data["headings"]:
        for tag, text in data["headings"][:40]:
            print(f"  <{tag}> {text[:100]}")
        if len(data["headings"]) > 40:
            print(f"  ... +{len(data['headings']) - 40} more")
    else:
        print("  (none — may be SPA shell; use Playwright render)")

    block("Section IDs / data landmarks")
    print(f"  section ids ({len(data['section_ids'])}): {', '.join(data['section_ids']) or '(none)'}")
    print(
        f"  data landmarks ({len(data['data_landmarks'])}): "
        f"{', '.join(data['data_landmarks']) or '(none)'}"
    )

    block("CSS custom properties (token-like, noise filtered)")
    print(f"  dropped noise var occurrences: {data['custom_noise_dropped']}")
    if data["custom_tokenish"]:
        for name, count in data["custom_tokenish"].most_common(50):
            print(f"  {count:4d}  {name}")
    else:
        print("  (none token-like — fetch CSS chunks)")
    if data["custom_other"]:
        print("\n  other non-noise vars (top 20):")
        for name, count in data["custom_other"].most_common(20):
            print(f"  {count:4d}  {name}")

    block(f"Hex colors (top {max_hex} by frequency)")
    for color, count in data["hex_colors"].most_common(max_hex):
        print(f"  {count:4d}  {color}")

    if data["rgba_colors"]:
        block("RGBA colors (top 20)")
        for color, count in data["rgba_colors"].most_common(20):
            print(f"  {count:4d}  {color}")

    if data["oklch_colors"] or data["hsl_colors"]:
        block("oklch / hsl")
        for color, count in (data["oklch_colors"] + data["hsl_colors"]).most_common(20):
            print(f"  {count:4d}  {color}")

    block("Spacing / radius candidates (arbitrary Tailwind values)")
    for val, count in data["radius_spacing_candidates"].most_common(25):
        print(f"  {count:4d}  {val}")

    block("Keyframes")
    if data["keyframes"]:
        for name in data["keyframes"]:
            print(f"  {name}")
    else:
        print("  (none inlined)")

    block("SVG density")
    print(f"  <svg>: {data['svg_count']}   <path>: {data['path_count']}   clipPath-ish: {data['clip_count']}")

    block("Stylesheet URLs (fetch these — tokens often live here)")
    if data["stylesheet_urls"]:
        for u in data["stylesheet_urls"]:
            print(f"  {u}")
    else:
        print("  (none detected)")

    block("Summary")
    print(f"  Fonts (file hints):     {len(data['fonts_from_files'])}")
    print(f"  Google Fonts families:  {len(data.get('fonts_google') or [])}")
    print(f"  Typekit kits:           {len(data.get('typekit_kits') or [])}")
    print(f"  Font-family decls:      {len(data['font_families'])}")
    print(f"  Token-like CSS vars:    {len(data['custom_tokenish'])}")
    print(f"  Unique hex colors:      {len(data['hex_colors'])}")
    print(f"  Headings:               {len(data['headings'])}")
    print(f"  Keyframes:              {len(data['keyframes'])}")
    print(f"  Stylesheets:            {len(data['stylesheet_urls'])}")
    print(f"  Section IDs:            {len(data['section_ids'])}")
    print()
    print("  Next: write docs/SIGNAL.md (see references/signal-sheet.md)")
    print("        then Skeleton → Density → Micro-parity.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="HTML and/or CSS files")
    parser.add_argument(
        "--base-url",
        default="",
        help="Origin for resolving relative CSS/font URLs (e.g. https://target.com)",
    )
    parser.add_argument(
        "--fetch-css",
        metavar="DIR",
        help="Download detected stylesheet URLs into DIR and merge analysis",
    )
    parser.add_argument("--max-hex", type=int, default=40)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the human report",
    )
    args = parser.parse_args()

    results: list[dict] = []
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"error: not found: {path}", file=sys.stderr)
            return 1
        text = path.read_text(errors="replace")
        results.append(analyze_text(text, str(path)))

    merged = merge_results(results)

    if args.fetch_css:
        if not args.base_url:
            print("error: --fetch-css requires --base-url", file=sys.stderr)
            return 1
        if not merged["stylesheet_urls"]:
            print("warning: no stylesheet URLs to fetch", file=sys.stderr)
        else:
            saved = fetch_css(
                merged["stylesheet_urls"], args.base_url, Path(args.fetch_css)
            )
            css_results = [
                analyze_text(p.read_text(errors="replace"), str(p)) for p in saved
            ]
            if css_results:
                merged = merge_results([merged] + css_results)

    if args.json:
        print(json.dumps(_serialize(merged), indent=2))
    else:
        print_report(merged, max_hex=args.max_hex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
