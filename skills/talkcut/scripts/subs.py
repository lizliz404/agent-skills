#!/usr/bin/env python3
"""步骤 7：从 cut.json 生成字幕。

  --style simple   白字黑描边（SRT + ASS）
  --style karaoke  逐字高亮：当前字变色 + 放大（ASS，每个字一条事件，任何播放器/ffmpeg 都能烧）
  --burn           用 ffmpeg 把 ASS 烧进视频 → *_sub.mp4；不加则只导出字幕文件，可拖进剪映
用法: python3 subs.py work/cut.json --style karaoke --burn [--max-chars 16]
"""
import argparse, re, subprocess
from pathlib import Path
from common import load, need, ts, video_info

PUNCT = "，。！？；、,.!?;：:"


def lines(sents, max_chars):
    """按标点和长度把句子拆成字幕行，每行保留字级时间。"""
    for s in sents:
        cur = []
        for w in s["words"]:
            cur.append(w)
            text = "".join(x["text"] for x in cur)
            if w["text"][-1:] in PUNCT or len(text) >= max_chars:
                yield cur; cur = []
        if cur:
            yield cur


def clean(text):
    return re.sub(f"[{PUNCT}]+$", "", text).strip()


def ass_time(x):
    return ts(x, ".")[:-1]  # h:mm:ss.cc


p = argparse.ArgumentParser()
p.add_argument("cut")
p.add_argument("--style", choices=["simple", "karaoke"], default="simple")
p.add_argument("--max-chars", type=int, default=16)
p.add_argument("--font", default="Noto Sans CJK SC")
p.add_argument("--highlight", default="&H00FFC864", help="ASS BGR 颜色，默认亮蓝")
p.add_argument("--burn", action="store_true")
a = p.parse_args()
cp = Path(a.cut); c = load(cp)
video = cp.parent / c["media"]
W, H, _ = video_info(video)
L = [l for l in lines(c["sentences"], a.max_chars) if clean("".join(w["text"] for w in l))]

srt = [f"{i}\n{ts(l[0]['start'])} --> {ts(l[-1]['end'])}\n{clean(''.join(w['text'] for w in l))}\n" for i, l in enumerate(L, 1)]
cp.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")

size = round(H * 0.055)
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,{a.font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,{max(2, size//14)},0,2,40,40,{round(H*0.08)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
for l in L:
    if a.style == "simple":
        ev.append(f"Dialogue: 0,{ass_time(l[0]['start'])},{ass_time(l[-1]['end'])},Base,,0,0,0,,{clean(''.join(w['text'] for w in l))}")
        continue
    words = [w for w in l if clean(w["text"])]
    for k, w in enumerate(words):  # 每个字一条事件：当前字高亮放大，其余白色
        end = words[k + 1]["start"] if k + 1 < len(words) else l[-1]["end"]
        txt = "".join((f"{{\\c{a.highlight}&\\fscx118\\fscy118}}{clean(x['text'])}{{\\r}}" if j == k else clean(x["text"]))
                      for j, x in enumerate(words))
        ev.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Base,,0,0,0,,{txt}")
ass = cp.with_suffix(f".{a.style}.ass")
ass.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
print(f"{len(L)} 行字幕 → {cp.with_suffix('.srt')} , {ass}")
if a.burn:
    out = cp.with_name(cp.stem + f"_{a.style}.mp4")
    subprocess.run([need("ffmpeg"), "-y", "-v", "error", "-i", video.name, "-vf", f"ass={ass.name}",
                    "-c:v", "libx264", "-crf", "18", "-c:a", "copy", str(out.name)], check=True, cwd=cp.parent)
    print(f"已烧录 → {out}")
