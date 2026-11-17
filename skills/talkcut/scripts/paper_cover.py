#!/usr/bin/env python3
"""Static-image covers: blue serif headlines on slightly tilted off-white paper.

Python: make_paper_cover(source, output, lines, kicker=..., top=340, ...)
CLI: python paper_cover.py --source frame.png --output episode-cover.jpg \
         --line 'First line' --line 'Second line' --kicker 'Series 01 / 04'
Output siblings: .jpg, .png, -paper-overlay.png, .design.json, and
<episode>-thumbnail.jpg (270 px wide). No video decoding or services.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

SERIF = '/usr/share/fonts/noto-cjk/NotoSerifCJK-Bold.ttc'
SANS = '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc'
NAVY = '#17486A'


def _strip(text, font, size, color, paper_color, padding, angle):
    face = ImageFont.truetype(str(font), size)
    left, top, right, bottom = face.getbbox(text)
    px, py = padding
    width = math.ceil(max(right - left, face.getlength(text))) + 2 * px + 16
    height = bottom - top + 2 * py + 16
    strip = Image.new('RGBA', (width + 14, height + 14))
    draw = ImageDraw.Draw(strip)
    points = [(4, 9), (width // 3, 5), (width - 2, 9),
              (width - 5, height - 3), (width // 2, height - 7), (3, height)]
    draw.polygon([(x + 5, y + 7) for x, y in points], fill=(23, 72, 106, 100))
    draw.polygon(points, fill=ImageColor.getrgb(paper_color) + (248,))
    # Correct font bearings: the actual visible glyphs, not the ascender box,
    # get equal paper padding. This avoids wasting vertical space or clipping.
    draw.text((px + 8 - left, py + 8 - top), text, font=face, fill=color)
    rotated = strip.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    rotated = rotated.crop(rotated.getbbox())
    return rotated


def _fit_strip(text, font, max_size, min_size, available, **style):
    # The rotated paper AND its shadow must fit, not just font.getlength().
    for size in range(max_size, min_size - 1, -1):
        strip = _strip(text, font, size, **style)
        if strip.width <= available:
            return strip, size
    raise ValueError(f'Line cannot fit at minimum font size: {text!r}')


def build_paper_overlay(dimensions, lines, *, kicker='', top=340, font=SERIF,
                        color=NAVY, font_size=210, min_font_size=64, margin=24,
                        padding=(18, 22), gap=14, angles=(-1.2, 0.8),
                        paper_color='#F9F7EF', kicker_font=SANS, kicker_size=36,
                        kicker_top=None):
    """Return a full-canvas transparent RGBA overlay and measured layout.

    Coordinates/font sizes are pixels in the source canvas. Lines are explicit:
    no rewriting, automatic wrapping or third line. Oversized layouts fail before
    writing files. Each headline is fitted independently up to font_size.
    """
    lines = list(lines)
    if not 1 <= len(lines) <= 2 or any(not isinstance(s, str) or not s.strip()
                                       or '\n' in s or '\r' in s for s in lines):
        raise ValueError('Provide one or two non-empty, single-line strings')
    width, height = dimensions
    if (width <= 0 or height <= 0 or margin < 0 or width <= 2 * margin
            or top < 0 or gap < 0 or len(padding) != 2 or min(padding) < 10
            or min_font_size < 1 or font_size < min_font_size or not angles
            or any(not math.isfinite(a) or abs(a) > 5 for a in angles)):
        raise ValueError('Invalid dimensions, spacing, sizes or paper angles')
    available = width - 2 * margin
    overlay = Image.new('RGBA', dimensions)
    boxes, y = [], top
    for index, text in enumerate(lines):
        angle = angles[index % len(angles)]
        strip, used_size = _fit_strip(
            text, font, font_size, min_font_size, available, color=color,
            paper_color=paper_color, padding=padding, angle=angle)
        if y + strip.height > height:
            raise ValueError('Paper headline would overflow the bottom of the canvas')
        overlay.alpha_composite(strip, (margin, y))
        boxes.append({'text': text, 'font_size': used_size, 'angle': angle,
                      'box': [margin, y, margin + strip.width, y + strip.height]})
        y += strip.height + gap
    kicker_box = None
    if kicker:
        if '\n' in kicker or '\r' in kicker or kicker_size < 1:
            raise ValueError('Kicker must be a single line with a positive font size')
        face = ImageFont.truetype(str(kicker_font), kicker_size)
        left, above, right, below = face.getbbox(kicker)
        kw, kh = right - left + 40, max(65, below - above + 24)
        ky = top - kh - 30 if kicker_top is None else kicker_top
        if kw > available or ky < 0 or ky + kh > top - 8:
            raise ValueError('Kicker must fit above the headline inside the canvas')
        draw = ImageDraw.Draw(overlay)
        kicker_box = [margin, ky, margin + kw, ky + kh]
        draw.rounded_rectangle(kicker_box, radius=9, fill='#F7F4ED')
        draw.text((margin + 20 - left, ky + (kh - (below - above)) // 2 - above),
                  kicker, font=face, fill=color)
    return overlay, {'copy': lines, 'kicker': kicker, 'top': top,
                     'font': str(font), 'foreground': color, 'paper_color': paper_color,
                     'requested_font_size': font_size, 'min_font_size': min_font_size,
                     'margin': margin, 'padding': list(padding), 'gap': gap,
                     'angles': list(angles), 'kicker_font': str(kicker_font),
                     'kicker_size': kicker_size, 'kicker_top': kicker_top,
                     'kicker_box': kicker_box, 'lines': boxes,
                     'overlay_bbox': list(overlay.getbbox())}


def make_paper_cover(source, output, lines, *, thumbnail_width=270, **style):
    """Write cover JPG/PNG, transparent overlay, thumbnail and design JSON.

    source: an existing single-frame PNG/JPEG/WebP/BMP/TIFF.
    output: cover filename ending .jpg/.jpeg/.png (both JPG and PNG are saved).
    Returns the design dictionary, including all output paths and measured boxes.
    """
    source, output = Path(source), Path(output)
    if output.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
        raise ValueError('Output must end in .jpg, .jpeg or .png')
    if source.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'):
        raise ValueError('Source must be a static image, not audio/video/GIF')
    if thumbnail_width < 1:
        raise ValueError('thumbnail_width must be positive')
    base = output.with_suffix('')
    episode = base.name.removesuffix('-cover')
    paths = {'jpg': str(base.with_suffix('.jpg')), 'png': str(base.with_suffix('.png')),
             'overlay': str(base.with_name(base.name + '-paper-overlay.png')),
             'thumbnail': str(base.with_name(episode + '-thumbnail.jpg')),
             'design': str(base.with_suffix('.design.json'))}
    if source.resolve() in [Path(p).resolve() for p in paths.values()]:
        raise ValueError('Source must not be overwritten by an output')
    with Image.open(source) as frame:
        if getattr(frame, 'n_frames', 1) != 1:
            raise ValueError('Animated sources are not accepted; provide a static frame')
        image = ImageOps.exif_transpose(frame).convert('RGBA')
    overlay, layout = build_paper_overlay(image.size, lines, **style)
    composed = Image.alpha_composite(image, overlay)
    thumb_height = max(1, round(image.height * thumbnail_width / image.width))
    thumb = composed.convert('RGB').resize((thumbnail_width, thumb_height), Image.Resampling.LANCZOS)
    design = {'schema_version': 1, 'component': 'paper_cover.make_paper_cover',
              'source': str(source.resolve()),
              'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'dimensions': list(image.size),
              'style': 'real static frame + enlarged blue serif type on offwhite tilted paper',
              **layout, 'thumbnail_dimensions': list(thumb.size), 'outputs': paths}
    output.parent.mkdir(parents=True, exist_ok=True)
    composed.convert('RGB').save(paths['jpg'], quality=95, subsampling=0)
    composed.save(paths['png'])
    overlay.save(paths['overlay'])
    thumb.save(paths['thumbnail'], quality=92, subsampling=0)
    Path(paths['design']).write_text(json.dumps(design, ensure_ascii=False, indent=2) + '\n')
    return design


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--line', dest='lines', action='append', required=True)
    parser.add_argument('--kicker', default='')
    parser.add_argument('--top', type=int, default=340)
    parser.add_argument('--font', default=SERIF)
    parser.add_argument('--color', default=NAVY)
    parser.add_argument('--font-size', type=int, default=210)
    parser.add_argument('--min-font-size', type=int, default=64)
    parser.add_argument('--margin', type=int, default=24)
    parser.add_argument('--gap', type=int, default=14)
    parser.add_argument('--padding', nargs=2, type=int, default=(18, 22), metavar=('X', 'Y'))
    parser.add_argument('--angles', nargs='+', type=float, default=(-1.2, 0.8))
    parser.add_argument('--paper-color', default='#F9F7EF')
    parser.add_argument('--kicker-font', default=SANS)
    parser.add_argument('--kicker-size', type=int, default=36)
    parser.add_argument('--kicker-top', type=int)
    parser.add_argument('--thumbnail-width', type=int, default=270)
    args = vars(parser.parse_args())
    print(json.dumps(make_paper_cover(**args), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
