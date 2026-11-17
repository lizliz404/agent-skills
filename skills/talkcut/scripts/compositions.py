#!/usr/bin/env python3
"""Render a compositions-plan.json into one .ass vector layer for the `ass` filter.

Dark-glass design system for screen-heavy footage, with speech-synced reveal
(rise / pop / clip-wipe). One deterministic vector layer avoids ffmpeg
framesync queues from many delayed PNG inputs. See
references/composition-kit.md for the design system and how to time figures.

Usage:
    python3 compositions.py plan.json -o compositions.ass
    ffmpeg -i cut.mp4 -vf "ass=compositions.ass,format=yuv420p" -c:a copy out.mp4

Plan shape:
    {"figures": [
        {"type": "dispatch", "title": "...", "start": 25.6, "end": 41.3,
         "boss": "总任务 · 包工头", "items": ["子任务 A", "子任务 B", "子任务 C"],
         "t": {"boss": 27.8, "workers": 34.3, "back": 39.2}},
        {"type": "questions", "title": "...", "start": ..., "end": ...,
         "items": [{"t": 45.6, "q": "员工掉了怎么办？", "icon": "warn"}, ...]},
        {"type": "stack", "title": "...", "start": ..., "end": ...,
         "boss": "包工头 · 管全局", "workers": ["agent A", "agent B", "agent C"],
         "arrow_label": "员工 → 包工头", "watchdog": "看门狗 · 60s 巡一圈 · 兜底",
         "t": {"workers": 79.4, "boss": 82.8, "arrows": 86.9, "watchdog": 90.2}},
        {"type": "handoff", "title": "...", "start": ..., "end": ...,
         "nodes": ["包工头", "审阅报告", "你"], "check": "流程完成",
         "t": {"first": 103.6, "doc": 104.8, "you": 105.6, "check": 109.2}}]}
All times are final-cut seconds. Icons: warn | chat | bell | person | doc | terminal.
"""
import json, sys
from math import ceil, hypot
from pathlib import Path

INK   = '&H00F2F6FA'   # primary text, warm white
DIM   = '&H00A8B4C2'   # secondary text
AMBER = '&H003CAAEB'   # accent (BGR)
GREEN = '&H008DD658'
SURF  = '&H00261A0E'   # card fill, deep navy (opaque)
PANEL = '&H00382816'   # chip fill, lifted navy (opaque)
EDGE  = '&H00708CA6'   # card hairline
BLACK = '&H00000000'
FONT  = 'Noto Sans CJK SC'
# libass ignores/damages the alpha byte inside \1c for \p drawings -> use \1a
A_EDGE, A_SHADOW, A_TINT, A_DIM, A_SURF = '&H80', '&H60', '&HC0', '&H8A', '&H20'

EVENTS = []

def at(t):
    n = round(t * 100)
    return f'{n // 360000}:{n // 6000 % 60:02}:{n // 100 % 60:02}.{n % 100:02}'

def ev(start, end, body, layer=5):
    EVENTS.append(f'Dialogue: {layer},{at(start)},{at(end)},Diagram,,0,0,0,,{body}')

def rr(x, y, w, h, r):
    """Rounded-rect path, absolute coords."""
    k = round(r * .5523, 1)
    return (f'm {x+r} {y} l {x+w-r} {y} b {x+w-r+k} {y} {x+w} {y+r-k} {x+w} {y+r} '
            f'l {x+w} {y+h-r} b {x+w} {y+h-r+k} {x+w-r+k} {y+h} {x+w-r} {y+h} '
            f'l {x+r} {y+h} b {x+r-k} {y+h} {x} {y+h-r+k} {x} {y+h-r} '
            f'l {x} {y+r} b {x} {y+r-k} {x+r-k} {y} {x+r} {y}')

def ellipse(cx, cy, rx, ry):
    k = .5523
    return (f'm {cx+rx} {cy} b {cx+rx} {cy+ry*k} {cx+rx*k} {cy+ry} {cx} {cy+ry} '
            f'b {cx-rx*k} {cy+ry} {cx-rx} {cy+ry*k} {cx-rx} {cy} '
            f'b {cx-rx} {cy-ry*k} {cx-rx*k} {cy-ry} {cx} {cy-ry} '
            f'b {cx-rx*k} {cy-ry} {cx+rx*k} {cy-ry} {cx+rx} {cy-ry}')

# ---- entrances -------------------------------------------------------------
# rise: anchor moves (0,+14)->(0,0); used on absolute drawings and \pos text
def rise(dur=280):
    return r'\move(0,14,0,0,0,%d)' % dur

# pop: scale 84->104->100 around the event \pos (relative drawings / text)
POP = r'{\fscx84\fscy84\t(0,240,\fscx104\fscy104)\t(240,340,\fscx100\fscy100)\fad(160,240)}'

def draw_abs(start, end, path, color, *, layer=5, fade=(200, 260), extra='',
             alpha=None):
    a = r'\1a' + alpha if alpha else ''
    ev(start, end, r'{\an7\pos(0,0)\bord0\shad0\1c' + color + a + extra
       + r'\fad(%d,%d)\p1}' % fade + path, layer)

def draw_rel(start, end, cx, cy, path, color, *, layer=5, pop=False,
             fade=(200, 260), extra='', alpha=None):
    a = r'\1a' + alpha if alpha else ''
    tag = POP if pop else (r'{\fad(%d,%d)}' % fade)
    ev(start, end, r'{\an7\pos(%d,%d)\bord0\shad0\1c%s%s%s\p1}' % (cx, cy, color, a, extra)
       + tag + path, layer)

def text(start, end, x, y, s, *, size=52, color=INK, bold=False, an=7,
         entrance='rise', layer=6):
    safe = s.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
    if entrance == 'rise':
        pos = r'\move(%d,%d,%d,%d,0,280)' % (x, y + 16, x, y)
        tag = r'{\an%d%s\1c%s\fs%d\b%d\fad(180,260)}' % (an, pos, color, size, int(bold))
    elif entrance == 'pop':
        tag = (r'{\an%d\pos(%d,%d)\1c%s\fs%d\b%d' % (an, x, y, color, size, int(bold))
               + POP)
    else:
        tag = r'{\an%d\pos(%d,%d)\1c%s\fs%d\b%d\fad(200,260)}' % (an, x, y, color, size, int(bold))
    ev(start, end, tag + safe, layer)

def surface(start, end, x, y, w, h, r=26):
    """Dark-glass card: shadow + hairline ring + fill, rising in."""
    move = r'\move(0,16,0,0,0,300)\fad(240,300)'
    draw_abs(start, end, rr(x, y + 14, w, h, r), BLACK, layer=1, fade=(240, 300),
             extra=move, alpha=A_SHADOW)
    draw_abs(start, end, rr(x, y, w, h, r), EDGE, layer=2, fade=(240, 300),
             extra=move, alpha=A_EDGE)
    draw_abs(start, end, rr(x + 2, y + 2, w - 4, h - 4, r - 2), SURF, layer=3,
             fade=(240, 300), extra=move, alpha=A_SURF)

def chip(start, end, cx, cy, w, h, label, *, size=44, fill=PANEL, tcolor=INK,
         bold=False, r=16, layer=5, fill_alpha=None, edge=False):
    """Centered node, pops in around its own centre."""
    if edge:
        draw_rel(start, end, cx, cy, rr(-w // 2, -h // 2, w, h, r), AMBER,
                 layer=layer, pop=True)
        # opaque interior cuts a 3px amber ring; optional tint warms the centre
        draw_rel(start, end, cx, cy,
                 rr(-w // 2 + 3, -h // 2 + 3, w - 6, h - 6, max(4, r - 3)),
                 SURF, layer=layer + 1, pop=True)
        if fill_alpha:
            draw_rel(start, end, cx, cy,
                     rr(-w // 2 + 3, -h // 2 + 3, w - 6, h - 6, max(4, r - 3)),
                     fill, layer=layer + 1, pop=True, alpha=fill_alpha)
    else:
        draw_rel(start, end, cx, cy, rr(-w // 2, -h // 2, w, h, r), fill,
                 layer=layer, pop=True, alpha=fill_alpha)
    text(start + .06, end, cx, cy, label, size=size, color=tcolor, bold=bold,
         an=5, entrance='pop', layer=6)

def rounded_stroke(points, width=6, radius=18):
    """Filled, round-capped stroke of an orthogonal route, using cubic elbows.

    A single outline keeps translucent return paths uniform at their joins.
    Points must be distinct, with an axis-aligned segment on either side of
    each right-angle corner. No fonts, SVG renderer or per-frame assets needed.
    """
    units, lengths = [], []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        length = hypot(x2 - x1, y2 - y1)
        units.append(((x2 - x1) / length, (y2 - y1) / length))
        lengths.append(length)
    half, k = width / 2, .5523

    def xy(p):
        return f'{p[0]:.2f} {p[1]:.2f}'

    def offset(p, u, side):
        return p[0] - u[1] * half * side, p[1] + u[0] * half * side

    def side_path(route, directions, spans):
        path = ''
        for i, p in enumerate(route[1:-1]):
            u, v = directions[i], directions[i + 1]
            r = min(radius, spans[i] / 2, spans[i + 1] / 2)
            turn = u[0] * v[1] - u[1] * v[0]
            a = offset((p[0] - u[0] * r, p[1] - u[1] * r), u, 1)
            b = offset((p[0] + v[0] * r, p[1] + v[1] * r), v, 1)
            kr = k * (r - turn * half)
            c1 = a[0] + u[0] * kr, a[1] + u[1] * kr
            c2 = b[0] - v[0] * kr, b[1] - v[1] * kr
            path += f' l {xy(a)} b {xy(c1)} {xy(c2)} {xy(b)}'
        return path + ' l ' + xy(offset(route[-1], directions[-1], 1))

    def cap(p, u):
        # Clockwise semicircle from the left outline to the right outline.
        a, b = offset(p, u, 1), offset(p, u, -1)
        tip = p[0] + u[0] * half, p[1] + u[1] * half
        c1 = a[0] + u[0] * half * k, a[1] + u[1] * half * k
        c2 = tip[0] - u[1] * half * k, tip[1] + u[0] * half * k
        c3 = tip[0] + u[1] * half * k, tip[1] - u[0] * half * k
        c4 = b[0] + u[0] * half * k, b[1] + u[1] * half * k
        return f' b {xy(c1)} {xy(c2)} {xy(tip)} b {xy(c3)} {xy(c4)} {xy(b)}'

    reverse_units = [(-u[0], -u[1]) for u in reversed(units)]
    return ('m ' + xy(offset(points[0], units[0], 1))
            + side_path(points, units, lengths) + cap(points[-1], units[-1])
            + side_path(list(reversed(points)), reverse_units, list(reversed(lengths)))
            + cap(points[0], reverse_units[-1]))

def connector(start, end, points, *, color=AMBER, layer=4, alpha=None,
              width=6, radius=18, head_size=22):
    """Rounded orthogonal connector with an open, softened chevron tip.

    Reveal the shaft along its dominant axis; keep the approved arrow fades.
    Inline clip tags are essential: nested {...} overrides hide libass shafts.
    """
    points = list(points)
    x2, y2 = points[-1]
    dx, dy = x2 - points[-2][0], y2 - points[-2][1]
    last_length = hypot(dx, dy)
    ux, uy = dx / last_length, dy / last_length
    head = min(head_size, last_length * .65)
    points[-1] = x2 - ux * head * .38, y2 - uy * head * .38
    shaft = rounded_stroke(points, width, radius)

    # Local +x chevron, with cubic-rounded ends and nose, not a solid triangle.
    def p(x, y):
        scale = head / 22
        return f'{x2 + scale * (ux*x - uy*y):.2f} {y2 + scale * (uy*x + ux*y):.2f}'
    tip = (f'm {p(-20, -13)} b {p(-23, -15)} {p(-26, -10)} {p(-23, -8)} '
           f'l {p(-9, 0)} {p(-23, 8)} b {p(-26, 10)} {p(-23, 15)} {p(-20, 13)} '
           f'l {p(-2, 3)} b {p(1, 1)} {p(1, -1)} {p(-2, -3)} l {p(-20, -13)}')
    pad = ceil(max(width, head))
    xs, ys = zip(*points, (x2, y2))
    box = [int(min(xs)) - pad, int(min(ys)) - pad,
           ceil(max(xs)) + pad, ceil(max(ys)) + pad]
    initial = box.copy()
    axis = 0 if max(xs) - min(xs) >= max(ys) - min(ys) else 1
    if points[0][axis] < (x2, y2)[axis]:
        initial[axis + 2] = initial[axis]
    else:
        initial[axis] = initial[axis + 2]
    wipe = r'\clip(%d,%d,%d,%d)\t(0,320,\clip(%d,%d,%d,%d))' % (*initial, *box)
    draw_abs(start, end, shaft, color, layer=layer, fade=(60, 260), extra=wipe,
             alpha=alpha)
    draw_abs(start + .28, end, tip, color, layer=layer, fade=(120, 260), alpha=alpha)

def arrow_h(start, end, x1, x2, y, *, color=AMBER, layer=4, alpha=None):
    """Horizontal connector; works in either direction, including short gaps."""
    connector(start, end, [(x1, y), (x2, y)], color=color, layer=layer, alpha=alpha)

def arrow_v(start, end, x, y1, y2, *, color=AMBER, layer=4, alpha=None,
            head_size=22):
    """Vertical connector; works upward or downward without overshooting."""
    connector(start, end, [(x, y1), (x, y2)], color=color, layer=layer, alpha=alpha,
              head_size=head_size)

def dashed_h(start, end, x1, x2, y, *, color=AMBER, dash=16, gap=12, layer=4,
             alpha=None):
    x = x1
    while x < x2:
        draw_abs(start, end, f'm {x} {y} l {min(x+dash, x2)} {y} {min(x+dash, x2)} {y+4} {x} {y+4}',
                 color, layer=layer, fade=(200, 260), alpha=alpha)
        x += dash + gap

def ic_terminal(start, end, cx, cy, s, *, color=AMBER, pop=True):
    """Little terminal window: frame + prompt chevron."""
    w, h = s, round(s * .78)
    draw_rel(start, end, cx, cy, rr(-w//2, -h//2, w, h, 7), color, layer=6, pop=pop)
    draw_rel(start, end, cx, cy, rr(-w//2+4, -h//2+4, w-8, h-8, 4), SURF, layer=7, pop=pop)
    d = round(s * .2)
    draw_rel(start, end, cx, cy, f'm {-d} {-d//2} l 0 0 {-d} {d//2}', color, layer=8, pop=pop)

def ic_person(start, end, cx, cy, s, *, color=AMBER, pop=True):
    draw_rel(start, end, cx, cy, ellipse(0, -round(s*.28), round(s*.2), round(s*.2)),
             color, layer=7, pop=pop)
    draw_rel(start, end, cx, cy, rr(-round(s*.3), -round(s*.02), round(s*.6), round(s*.42), round(s*.2)),
             color, layer=7, pop=pop)

def ic_doc(start, end, cx, cy, s, *, color=AMBER, pop=True):
    w, h = round(s * .72), s
    draw_rel(start, end, cx, cy, rr(-w//2, -h//2, w, h, 6), color, layer=7, pop=pop)
    draw_rel(start, end, cx, cy, rr(-w//2+4, -h//2+4, w-8, h-8, 3), SURF, layer=8, pop=pop)
    for i in range(3):
        draw_rel(start, end, cx, cy, f'm {-w//4} {-h//4+i*h//4} l {w//4} {-h//4+i*h//4} {w//4} {-h//4+i*h//4+3} {-w//4} {-h//4+i*h//4+3}',
                 color, layer=9, pop=pop)

def ic_check(start, end, cx, cy, s, *, color=GREEN, pop=True):
    """Tick drawn on a soft green disc."""
    d = s // 2
    draw_rel(start, end, cx, cy, ellipse(0, 0, d, d), color, layer=8, pop=pop)
    p = [(-.55, .1), (-.18, .45), (.55, -.4), (.38, -.55), (-.18, .12), (-.4, -.12)]
    draw_rel(start, end, cx, cy, 'm ' + ' l '.join(f'{round(px*s)} {round(py*s)}' for px, py in p),
             SURF, layer=9, pop=pop)

def ic_warn(start, end, cx, cy, s, *, color=AMBER, pop=True):
    d = s // 2
    draw_rel(start, end, cx, cy, f'm 0 {-d} l {d} {d} {-d} {d} 0 {-d}', color, layer=7, pop=pop)
    # '!' as a small bar + dot
    draw_rel(start, end, cx, cy, f'm -3 {-d//2+4} l 3 {-d//2+4} 3 {d//4} -3 {d//4} -3 {-d//2+4}',
             SURF, layer=8, pop=pop)
    draw_rel(start, end, cx, cy, ellipse(0, round(d*.5), 3, 3), SURF, layer=8, pop=pop)

def ic_chat(start, end, cx, cy, s, *, color=AMBER, pop=True):
    w, h = s, round(s * .6)
    draw_rel(start, end, cx, cy, rr(-w//2, -h//2, w, h, 8), color, layer=7, pop=pop)
    draw_rel(start, end, cx, cy, f'm {-w//5} {h//2} l {-w//5} {h//2 + w//6} {w//10} {h//2}',
             color, layer=7, pop=pop)
    for i in (-1, 0, 1):
        draw_rel(start, end, cx, cy, ellipse(i * w // 5, 0, 3, 3), SURF, layer=8, pop=pop)

def ic_bell(start, end, cx, cy, s, *, color=AMBER, pop=True):
    w, h = round(s * .62), s
    draw_rel(start, end, cx, cy, ellipse(0, -round(h*.18), w//2, round(h*.32)),
             color, layer=7, pop=pop)
    draw_rel(start, end, cx, cy, rr(-w//2 - 4, round(h*.05), w + 8, round(h*.18), 6),
             color, layer=7, pop=pop)
    draw_rel(start, end, cx, cy, ellipse(0, round(h*.32), 6, 6), color, layer=7, pop=pop)

ICONS = {'warn': ic_warn, 'chat': ic_chat, 'bell': ic_bell,
         'person': ic_person, 'doc': ic_doc, 'terminal': ic_terminal}

def title_block(start, end, x, y, title):
    """Amber bullet + bold title + hairline rule."""
    draw_abs(start + .05, end, rr(x, y + 8, 14, 44, 5), AMBER, layer=5, fade=(160, 260))
    text(start + .05, end, x + 30, y, title, size=64, bold=True, entrance='rise')
    draw_abs(start + .1, end, f'm {x} {y+66} l {x} {y+68} {x+880} {y+68} {x+880} {y+66}',
             EDGE, layer=4, fade=(220, 260), alpha=A_EDGE)

# ---- figures ---------------------------------------------------------------
X, W = 66, 948

def fig_dispatch(f):
    x, y, h = X, 500, 470
    surface(f['start'], f['end'], x, y, W, h)
    title_block(f['start'], f['end'], x + 44, y + 34, f['title'])
    t = f['t']
    boss_cx, boss_cy = x + 210, y + 285
    chip(t['boss'], f['end'], boss_cx, boss_cy, 340, 96, f['boss'],
         size=40, fill=AMBER, fill_alpha=A_TINT, tcolor=AMBER, bold=True,
         edge=True)
    items = f['items']
    col_cx = x + 700
    gap = 108
    top = y + 178
    for i, it in enumerate(items):
        cy = top + i * gap
        chip(t['workers'] + i * .35, f['end'], col_cx, cy, 320, 84, it, size=42)
        # Distinct boss ports make a real fan-out. Reuse each lane in the
        # return phase, rather than leaving two opposing arrow sets stacked.
        port_y = boss_cy + (i - (len(items) - 1) / 2) * 30
        left, right = boss_cx + 180, col_cx - 170
        mid = (left + right) / 2
        if abs(cy - port_y) < 8:
            outward = [(left, cy), (right, cy)]
        else:
            outward = [(left, port_y), (mid, port_y), (mid, cy), (right, cy)]
        back = t['back'] + i * .15
        # The existing 260ms fade-out meets the return fade-in; the outgoing
        # head is gone before the incoming head appears (280ms after back).
        connector(t['workers'] + i * .35, min(f['end'], back + .16), outward)
        connector(back, f['end'], list(reversed(outward)), alpha=A_DIM, width=4)
    text(t['back'] + .4, f['end'], x + 44, y + h - 66, '派活下去，干完都回到包工头',
         size=40, color=DIM)

def fig_questions(f):
    x, y, h = X, 480, 430
    surface(f['start'], f['end'], x, y, W, h)
    title_block(f['start'], f['end'], x + 44, y + 34, f['title'])
    for i, it in enumerate(f['items']):
        cy = y + 158 + i * 92
        ncx = x + 92
        draw_rel(it['t'], f['end'], ncx, cy, ellipse(0, 0, 30, 30), AMBER, layer=6, pop=True)
        text(it['t'], f['end'], ncx, cy, str(i + 1), size=44, bold=True, an=5,
             entrance='pop', color='&H000E1A26')
        ICONS[it.get('icon', 'warn')](it['t'], f['end'], x + 165, cy, 56)
        text(it['t'], f['end'], x + 215, cy - 26, it['q'], size=50)

def fig_stack(f):
    x, y, h = X, 420, 610
    surface(f['start'], f['end'], x, y, W, h)
    title_block(f['start'], f['end'], x + 44, y + 34, f['title'])
    t = f['t']
    # watchdog band first (behind workers), revealed last
    wd_y = y + h - 96
    draw_abs(t['watchdog'], f['end'], rr(x + 30, wd_y, W - 60, 62, 18), AMBER,
             layer=3, fade=(240, 260), alpha=A_TINT)
    dashed_h(t['watchdog'], f['end'], x + 46, x + W - 46, wd_y - 4, color=AMBER)
    text(t['watchdog'] + .1, f['end'], x + W // 2, wd_y + 31, f['watchdog'],
         size=40, color=AMBER, an=5, entrance='rise')
    # workers row
    n = len(f['workers'])
    cw, cgap = 240, 40
    row_w = n * cw + (n - 1) * cgap
    wx = x + (W - row_w) // 2 + cw // 2
    wy = y + 350
    for i, wname in enumerate(f['workers']):
        cx = wx + i * (cw + cgap)
        chip(t['workers'] + i * .3, f['end'], cx, wy, cw, 96, wname, size=40)
    text(t['workers'] + .9, f['end'], x + W // 2, wy + 72, '并行干活，互不干扰',
         size=40, color=DIM, an=5)
    # boss on top
    chip(t['boss'], f['end'], x + W // 2, y + 190, 460, 92, f['boss'],
         size=42, fill=AMBER, fill_alpha=A_TINT, tcolor=AMBER, bold=True,
         edge=True)
    # upward arrows worker -> boss
    for i in range(n):
        cx = wx + i * (cw + cgap)
        target_x = x + W // 2 + (i - (n - 1) / 2) * 160
        bottom, top = wy - 58, y + 246
        if cx == target_x:
            arrow_v(t['arrows'] + i * .2, f['end'], cx, bottom, top, head_size=18)
        else:
            # Leave a straight landing before the tip: a head crammed into
            # the last elbow reads as a knot instead of an upward report.
            mid_y = bottom - 14
            connector(t['arrows'] + i * .2, f['end'],
                      [(cx, bottom), (cx, mid_y), (target_x, mid_y), (target_x, top)],
                      radius=10, head_size=18)
    if f.get('arrow_label'):
        text(t['arrows'] + .9, f['end'], x + W - 40,
             wy - 96, f['arrow_label'], size=34, color=AMBER, an=9)

def fig_handoff(f):
    x, y, h = X, 560, 380
    surface(f['start'], f['end'], x, y, W, h)
    title_block(f['start'], f['end'], x + 44, y + 34, f['title'])
    t = f['t']
    cy = y + 220
    nodes = f['nodes']
    xs = [x + 190, x + W // 2, x + W - 190]
    times = [t['first'], t.get('doc', t['first'] + 1), t.get('you', t['first'] + 2)]
    icons = f.get('icons') or ['terminal', 'doc', 'person']
    for i, (name, cx, tt) in enumerate(zip(nodes, xs, times)):
        ICONS[icons[i] if i < len(icons) else 'person'](tt, f['end'], cx, cy - 66, 64)
        chip(tt, f['end'], cx, cy + 40, 260, 80, name, size=44,
             fill=AMBER if i == 1 else PANEL,
             fill_alpha=A_TINT if i == 1 else None,
             tcolor=AMBER if i == 1 else INK, bold=(i == 1))
        if i:
            arrow_h(tt - .5, f['end'], xs[i-1] + 130, cx - 130, cy + 40)
    if f.get('check'):
        ic_check(t['check'], f['end'], xs[-1] + 120, cy - 96, 72)
        text(t['check'], f['end'], xs[-1] + 120, cy - 30, f['check'], size=40,
             color=GREEN, an=5, entrance='pop')

FIG = {'dispatch': fig_dispatch, 'questions': fig_questions,
       'stack': fig_stack, 'handoff': fig_handoff}

HEADER = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Diagram,%s,52,%s,%s,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
''' % (FONT, INK, INK)

def render(plan_path, out_path):
    plan = json.loads(Path(plan_path).read_text())
    EVENTS.clear()
    for f in plan['figures']:
        FIG[f['type']](f)
    Path(out_path).write_text(HEADER + '\n'.join(EVENTS) + '\n')
    print(f'{len(plan["figures"])} figures, {len(EVENTS)} events -> {out_path}')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('plan')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()
    render(a.plan, a.out)
