#!/usr/bin/env python3
"""步骤 1：拼接多段素材 → work/source.mp4，并抽出 16kHz 单声道 mp3 → work/audio.mp3。

用法: python3 prep.py clip1.mp4 [clip2.mp4 ...] -o work/
多段素材统一重编码后拼接（参数不一致也安全）；只有一段时直接复制。
"""
import argparse, subprocess
from pathlib import Path
from common import need, duration

p = argparse.ArgumentParser()
p.add_argument("clips", nargs="+")
p.add_argument("-o", "--out", default="work")
a = p.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
ff = need("ffmpeg")
src = out / "source.mp4"
if len(a.clips) == 1:
    subprocess.run([ff, "-y", "-v", "error", "-i", a.clips[0], "-c", "copy", "-movflags", "+faststart", str(src)], check=True)
else:
    inputs, chains = [], []
    for i, c in enumerate(a.clips):
        inputs += ["-i", c]
        chains.append(f"[{i}:v]scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1,fps=30[v{i}];[{i}:a]aresample=48000[a{i}];")
    concat = "".join(f"[v{i}][a{i}]" for i in range(len(a.clips))) + f"concat=n={len(a.clips)}:v=1:a=1[v][a]"
    subprocess.run([ff, "-y", "-v", "error", *inputs, "-filter_complex", "".join(chains) + concat,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(src)], check=True)
audio = out / "audio.mp3"
subprocess.run([ff, "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "48k", str(audio)], check=True)
print(f"source: {src} ({duration(src):.2f}s)\naudio:  {audio} ({audio.stat().st_size/1e6:.1f} MB)")
