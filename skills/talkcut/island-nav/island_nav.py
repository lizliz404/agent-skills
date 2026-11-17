#!/usr/bin/env python3
"""Liquid-glass chapter island. Overlay only — never blurs or vignettes the frame outside the pill.

    render_island(frame, chapter, idx, total, frac, colorway) -> RGB image

CLI (gallery for Liz, not the burn path):

    python3 island_nav.py --bases a.png b.png --out gallery/ --html gallery.html
    python3 island_nav.py --bases a.png --colorway ink --chapter 被社会做局生孩子 --idx 3 --total 7 --frac 0.4 --out one.png

Needs Pillow. Colorways live in colorways.json next to this file.
"""
import argparse, json, sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "colorways.json").read_text())
GEO = SPEC["geometry"]
BANNED = tuple(SPEC["banned_title_tokens"])


def load_colorways(path=None):
    spec = SPEC if path is None else json.loads(Path(path).read_text())
    return {c["id"]: c for c in spec["colorways"]}


def _rgba(rgb, a):
    return (int(rgb[0]), int(rgb[1]), int(rgb[2]), int(a))


def _font(path, size):
    return ImageFont.truetype(path, size)


def _text_w(font, s):
    b = font.getbbox(s)
    return b[2] - b[0]


def check_title(chapter):
    hit = [w for w in BANNED if w in chapter]
    if hit:
        raise ValueError(f"chapter title contains banned meta token(s) {hit}: {chapter!r}")


def island_box(frame_w, frame_h, geo=GEO):
    s = frame_w / SPEC["ref_width"]
    h = max(64, round(geo["height_px"] * s))
    x0 = round(frame_w * geo["margin_x_frac"])
    y0 = round(geo["top_px"] * s)
    x1 = frame_w - x0
    y1 = y0 + h
    if y1 > frame_h:
        raise ValueError(f"island {y1}px taller than frame {frame_h}px")
    return x0, y0, x1, y1, s


def _pill_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def _vgrad(w, h, top, bot):
    """1px-wide vertical gradient, stretched. top/bot are RGBA."""
    col = Image.new("RGBA", (1, h))
    px = col.load()
    for i in range(h):
        t = i / max(1, h - 1)
        px[0, i] = tuple(round(top[c] * (1 - t) + bot[c] * t) for c in range(4))
    return col.resize((w, h), Image.Resampling.NEAREST)


def _rounded_stroke(size, r, color, width):
    """1px-ish outline that follows the pill, including the corners. width is in px."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    inset = width / 2
    d.rounded_rectangle(
        [inset, inset, w - 1 - inset, h - 1 - inset],
        radius=max(1, r - inset),
        outline=color,
        width=width,
    )
    return layer


def render_island(frame, chapter, idx, total, frac, colorway, geo=None):
    """Composite the island onto a copy of `frame`. Returns a new RGB image.

    frame: PIL image or path. idx is 1-based. frac is progress inside this chapter, 0..1.
    colorway: preset id (str) or a preset dict.
    Nothing outside the pill is blurred, tinted, or given a glow.
    """
    check_title(chapter)
    if not isinstance(frame, Image.Image):
        frame = Image.open(frame)
    base = frame.convert("RGB")
    if isinstance(colorway, str):
        colorway = load_colorways()[colorway]
    g = geo or GEO
    W, H = base.size
    x0, y0, x1, y1, s = island_box(W, H, g)
    pw, ph = x1 - x0, y1 - y0
    r = min(round(g["radius_px"] * s), ph // 2)

    cw = colorway
    mask = _pill_mask(pw, ph, r)

    # Backdrop sample is clipped to the pill. The rest of the frame is never filtered.
    crop = base.crop((x0, y0, x1, y1)).filter(
        ImageFilter.GaussianBlur(radius=max(1, round(g["frost_radius_px"] * s)))
    ).convert("RGBA")
    glass = Image.new("RGBA", (pw, ph), _rgba(cw["glass"], cw["glass_alpha"]))
    body = Image.alpha_composite(crop, glass)
    body = Image.alpha_composite(body, _vgrad(
        pw, ph,
        _rgba(cw["wash_top"], cw["wash_top_alpha"]),
        _rgba(cw["wash_bot"], cw["wash_bot_alpha"]),
    ))
    body.putalpha(mask)

    # Specular follows the top rim: flat through the middle, rising into the
    # corner radius, fading out before the side. A straight dash reads as a
    # drawn line; a line that tracks the edge reads as glass.
    spec = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    gap = max(2, round(g["specular_y_px"] * s))
    inset = round(min(pw, ph) * g["specular_inset_frac"])
    col = cw["specular"]
    peak = cw["specular_alpha"]
    px = spec.load()
    thick = max(1, round(1.4 * s))
    x_start, x_end = inset, pw - inset
    span = max(1, x_end - x_start)
    for x in range(x_start, x_end):
        if x < r:
            inner = r - ((r * r - (r - x) ** 2) ** 0.5)
        elif x > pw - r:
            dx = x - (pw - r)
            inner = r - ((r * r - dx * dx) ** 0.5)
        else:
            inner = 0
        t = (x - x_start) / span
        fade = max(0.0, 1 - abs(t - 0.5) * 2) ** 1.4
        a = int(peak * fade)
        if a < 4:
            continue
        yy0 = int(round(inner + gap))
        for dy_ in range(thick):
            yy = yy0 + dy_
            if 0 <= yy < ph:
                px[x, yy] = (col[0], col[1], col[2], a)
    spec.putalpha(ImageChops.darker(spec.getchannel("A"), mask))

    stroke = _rounded_stroke((pw, ph), r, _rgba(cw["stroke"], cw["stroke_alpha"]),
                             max(1, round(g["inner_stroke_px"] * s)))
    stroke.putalpha(ImageChops.darker(stroke.getchannel("A"), mask))

    # Shadow is a second pill, shifted down, same silhouette. No blur, no halo.
    dy = max(1, round(g["shadow_dy_px"] * s))
    shadow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [0, 0, pw - 1, ph - 1], radius=r,
        fill=_rgba(cw["shadow"], g["shadow_alpha"]),
    )

    canvas = base.convert("RGBA")
    if y0 + dy + ph <= H:
        canvas.alpha_composite(shadow, (x0, y0 + dy))
    canvas.alpha_composite(body, (x0, y0))
    canvas.alpha_composite(spec, (x0, y0))
    canvas.alpha_composite(stroke, (x0, y0))

    d = ImageDraw.Draw(canvas)
    title_font = _font(SPEC["fonts"]["title"], max(16, round(g["title_size_px"] * s)))
    index_font = _font(SPEC["fonts"]["index"], max(13, round(g["index_size_px"] * s)))
    pad = round(g["pad_x_px"] * s)
    label = f"{int(idx):02d}/{int(total):02d}"
    iw = _text_w(index_font, label)
    # Anchor on the glyph top, not the em-box top. CJK fonts have a large
    # bearing above the ink, and using the em-box puts the bar through the title.
    title_box = title_font.getbbox(chapter)
    index_box = index_font.getbbox(label)
    title_top = y0 + round(g["title_y_px"] * s)
    d.text((x0 + pad, title_top - title_box[1]), chapter,
           font=title_font, fill=_rgba(cw["ink"], cw["ink_alpha"]))
    d.text((x1 - pad - iw, title_top - index_box[1] + round(g["index_baseline_nudge_px"] * s)),
           label, font=index_font, fill=_rgba(cw["index"], cw["index_alpha"]))

    # Bar sits on its own row under the chapter name, and stops before the index.
    title_w = _text_w(title_font, chapter)
    bh = max(3, round(g["bar_h_px"] * s))
    by = title_top + (title_box[3] - title_box[1]) + round(g["bar_gap_px"] * s)
    bx0 = x0 + pad
    bar_w = min(round(g["bar_max_px"] * s), max(title_w, round(120 * s)))
    bar_w = min(bar_w, (x1 - pad - iw - round(16 * s)) - bx0)
    bx1 = bx0 + bar_w
    frac = min(1.0, max(0.0, float(frac)))
    d.rounded_rectangle([bx0, by, bx1, by + bh], radius=bh / 2,
                        fill=_rgba(cw["track"], cw["track_alpha"]))
    fw = max(round(g["min_fill_px"] * s), round(bar_w * frac))
    d.rounded_rectangle([bx0, by, bx0 + fw, by + bh], radius=bh / 2,
                        fill=_rgba(cw["accent"], cw["accent_alpha"]))
    return canvas.convert("RGB")


def render_gallery(bases, out_dir, chapter, idx, total, frac, colorway_ids=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ways = load_colorways()
    ids = colorway_ids or list(ways)
    written = []
    for base in bases:
        base = Path(base)
        for cid in ids:
            dest = out_dir / f"{base.stem}__{cid}.png"
            render_island(base, chapter, idx, total, frac, ways[cid]).save(dest)
            written.append((base.name, cid, dest.name))
    return written


def write_gallery_html(written, out_html, title="灵动岛章节导航 · preset 画廊", state=None, img_prefix=""):
    """Gallery page. img_prefix is prepended to each png name, so the html can live one directory up from the renders."""
    ways = load_colorways()
    out_html = Path(out_html)
    by_base = {}
    for base_name, cid, fname in written:
        by_base.setdefault(base_name, []).append((cid, fname))
    cards = []
    for base_name, items in by_base.items():
        cards.append(f"<h2>{base_name}</h2><div class='grid'>")
        for cid, fname in items:
            cw = ways[cid]
            anchor = f" · 锚点 {cw['anchor']}" if cw.get("anchor") else ""
            cards.append(
                f"<figure><a href='{img_prefix}{fname}'><img src='{img_prefix}{fname}' alt='{cid}'></a>"
                f"<figcaption><b>{cw['name']}</b> <span>{cid}{anchor}</span><br>{cw['best_on']}</figcaption>"
                f"</figure>"
            )
        cards.append("</div>")
    note = ""
    if state:
        note = (f"<p class='sub'>预览态：{state['chapter']} · {state['idx']:02d}/{state['total']:02d}"
                f" · 本章进度 {state['frac']:.0%}</p>")
    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>{title}</title>
<style>
  body{{background:#16171a;color:#e6e3dc;font:15px/1.55 "Noto Sans CJK SC",sans-serif;margin:0;padding:28px;max-width:1280px}}
  h1{{font-size:20px;font-weight:600;margin:0 0 4px}}
  h2{{font-size:14px;font-weight:600;color:#9d9a93;margin:28px 0 10px}}
  p.sub{{color:#8d8a84;font-size:13px;margin:0 0 8px}}
  .grid{{display:flex;flex-wrap:wrap;gap:16px}}
  figure{{margin:0;width:280px;background:#1e1f23;border:1px solid #2c2d31;border-radius:10px;padding:8px}}
  img{{width:100%;display:block;border-radius:6px}}
  figcaption{{font-size:12.5px;color:#b7b3ab;padding:8px 4px 4px}}
  figcaption b{{color:#f2efe8;font-weight:600}}
  figcaption span{{color:#8d8a84}}
</style></head><body>
<h1>{title}</h1>
<p class="sub">只渲染岛本体。岛外没有磨砂、光晕、暗角。左章节名，右序号，下方是本章内进度。</p>
{note}
{''.join(cards)}
</body></html>
"""
    out_html.write_text(html)


def main(argv=None):
    p = argparse.ArgumentParser(description="Render a liquid-glass chapter island onto still frames.")
    p.add_argument("--bases", nargs="+", required=True, help="still frames to composite onto")
    p.add_argument("--out", required=True, help="output png, or a directory when rendering every colorway")
    p.add_argument("--chapter", default="被社会做局生孩子")
    p.add_argument("--idx", type=int, default=3)
    p.add_argument("--total", type=int, default=7)
    p.add_argument("--frac", type=float, default=0.40)
    p.add_argument("--colorway", help="one preset id; omit to render all presets")
    p.add_argument("--html", help="also write a gallery html (only with --out as a directory)")
    p.add_argument("--img-prefix", default="", help="prefix for image src in the gallery html")
    a = p.parse_args(argv)
    check_title(a.chapter)
    if a.colorway:
        img = render_island(a.bases[0], a.chapter, a.idx, a.total, a.frac, a.colorway)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        img.save(a.out)
        print(a.out)
        return
    written = render_gallery(a.bases, a.out, a.chapter, a.idx, a.total, a.frac)
    for row in written:
        print(row[2])
    if a.html:
        write_gallery_html(written, a.html,
                           state={"chapter": a.chapter, "idx": a.idx,
                                  "total": a.total, "frac": a.frac},
                           img_prefix=a.img_prefix)
        print(a.html)


if __name__ == "__main__":
    main()
