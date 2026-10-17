#!/usr/bin/env python3
"""步骤 8：章节导航条（致敬 dbskill / dbs-video-navigation 的黑底白字蓝进度条样式）。

输入 chapters.json（Agent 通读 cut.json 后写出）：
  {"chapters": [{"title": "第一部分：为什么要剪口播",
                 "segments": [{"start": 0, "desc": "剪映不懂语义"}, {"start": 12.3, "desc": "只留最后一遍"}]}]}
  start 为成片(cut.mp4)时间，秒；第一段必须从 0 开始；按时间递增。
输出：与成片等长、无音轨的 navbar.mp4（宽 = 成片宽，高 = 宽 × height_ratio），放在剪映画面顶部即可。
渲染：Pillow 每个(章节,段落)画一张文字 PNG → ffmpeg concat 定长拼接 → drawbox 画分章轨道 + 随时间增长的蓝色进度。
用法: python3 navbar.py work/cut.json work/chapters.json [-o work/navbar.mp4] [--style ../assets/navbar-black-blue.json]
"""
import argparse, json, subprocess, tempfile
from pathlib import Path
from common import load, need, video_info, duration

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument("cut"); p.add_argument("chapters")
p.add_argument("-o", "--out")
p.add_argument("--style", default=str(HERE.parent / "assets/navbar-black-blue.json"))
p.add_argument("--width", type=int)
a = p.parse_args()
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("需要 Pillow：pip install pillow")

cp = Path(a.cut); c = load(cp); st = load(a.style)
video = cp.parent / c["media"]
W0, _, fps = video_info(video)
W = a.width or W0
T = duration(video)
H = round(W * st["height_ratio"]) // 2 * 2
rows = []
for ch in load(a.chapters)["chapters"]:
    for sg in ch["segments"]:
        rows.append({"title": ch["title"], "desc": sg.get("desc", ""), "start": float(sg["start"])})
rows.sort(key=lambda r: r["start"])
assert rows and rows[0]["start"] == 0, "第一段必须从 0 开始"
for i, r in enumerate(rows):
    r["end"] = rows[i + 1]["start"] if i + 1 < len(rows) else T
    assert r["end"] > r["start"], f"段落时间必须递增: {r}"

def font(path, weight):
    if Path(path).exists():
        return path
    r = subprocess.run(["fc-match", "-f", "%{file}", f":lang=zh:weight={weight}"], capture_output=True, text=True)
    if r.returncode or not r.stdout:
        raise SystemExit(f"找不到中文字体 {path}；在样式 JSON 里填 font_title / font_desc 的绝对路径")
    return r.stdout


m = round(W * st["margin_ratio"])
ft = ImageFont.truetype(font(st["font_title"], 200), round(W * st["title_ratio"]))
fd = ImageFont.truetype(font(st["font_desc"], 80), round(W * st["desc_ratio"]))
tmp = Path(tempfile.mkdtemp(prefix="navbar-"))
concat = ["ffconcat version 1.0"]
for i, r in enumerate(rows):
    img = Image.new("RGB", (W, H), st["background"]); d = ImageDraw.Draw(img)
    for text, font, top in ((r["title"], ft, st["title_top_ratio"]), (r["desc"], fd, st["desc_top_ratio"])):
        if d.textlength(text, font=font) > W - 2 * m:
            print(f"⚠️ 文字超宽，请精简：{text}")
        d.text((m, round(W * top)), text, font=font, fill=st["foreground"])
    img.save(tmp / f"f{i:03}.png")
    concat += [f"file 'f{i:03}.png'", f"duration {r['end'] - r['start']:.6f}"]
concat.append(f"file 'f{len(rows)-1:03}.png'")
(tmp / "list.txt").write_text("\n".join(concat))

tw = W - 2 * m
th = max(2, round(W * st["track_height_ratio"]))
ty = H - round(W * st["track_bottom_ratio"]) - th
gap = max(2, round(W * st["gap_ratio"]))
f = [f"fps={fps}", f"drawbox=x={m}:y={ty}:w={tw}:h={th}:color={st['track']}:t=fill",
     f"drawbox=x={m}:y={ty}:w='max(1,{tw}*t/{T})':h={th}:color={st['progress']}:t=fill"]
prev = rows[0]["title"]
for r in rows[1:]:
    if r["title"] != prev:  # 只在章节切换处画分隔缝
        f.append(f"drawbox=x={m + round(tw * r['start'] / T) - gap // 2}:y={ty}:w={gap}:h={th}:color={st['background']}:t=fill")
        prev = r["title"]
f.append("format=yuv420p")
out = Path(a.out or cp.parent / "navbar.mp4").resolve()
subprocess.run([need("ffmpeg"), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "list.txt",
                "-vf", ",".join(f), "-t", f"{T:.6f}", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast",
                "-movflags", "+faststart", str(out)], check=True, cwd=tmp)
got = duration(out)
print(json.dumps({"output": str(out), "size": [W, H], "duration": round(got, 3), "target": round(T, 3),
                  "rows": len(rows)}, ensure_ascii=False))
if abs(got - T) > 1 / fps + 0.01:
    print("⚠️ 时长与成片不一致，请检查")
