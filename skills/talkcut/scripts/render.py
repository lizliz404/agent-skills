#!/usr/bin/env python3
"""Step 6: frame-accurate cut by keep flags (re-encode) and remap timestamps to the new timeline.

Rule: build ranges from kept words; pauses between kept words <= pause_keep stay as-is (breathing room),
longer pauses are shortened to pause_keep; cut words/sentences are removed. Each range gets pad s on both ends to avoid clipping.
Output: cut.mp4 + cut.json (transcript on the new timeline, for subtitles and navbar)
Usage: python3 render.py work/transcript.json -o work/cut.mp4 [--pad 0.05]
"""
import argparse, subprocess
from pathlib import Path
from common import load, save, need, duration


def segments(t, pad):
    gap = t.get("pause_keep", 0.5)
    allw = sorted((w for s in t["sentences"] for w in s["words"]), key=lambda w: w["start"])
    for i, w in enumerate(allw):  # safe bounds around each word: never cross into neighbours (including cut words)
        w["_lo"] = allw[i - 1]["end"] if i else 0.0
        w["_hi"] = allw[i + 1]["start"] if i + 1 < len(allw) else w["end"] + gap
    keep = {id(w) for s in t["sentences"] if s["keep"] for w in s["words"] if w.get("keep", True)}
    segs = []
    for w in allw:
        if id(w) not in keep:
            if segs and "broken" not in segs[-1]:
                segs[-1].append("broken")  # a cut word breaks continuity
            continue
        if segs and "broken" not in segs[-1] and w["start"] - segs[-1][1] <= gap:
            segs[-1][1] = w["end"]; segs[-1][2] = w["_hi"]
        else:
            if segs:  # close the previous range with half a pause (within bounds)
                segs[-1][1] = min(segs[-1][1] + max(pad, gap / 2), segs[-1][2])
            segs.append([max(w["_lo"], w["start"] - max(pad, gap / 2)), w["end"], w["_hi"]])
    if segs:
        segs[-1][1] = min(segs[-1][1] + max(pad, gap / 2), segs[-1][2])
    out = []
    for s in segs:
        a, b = s[0], s[1]
        if out and a <= out[-1][1] + 0.02:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def remap(t, segs):
    offs, acc = [], 0.0
    for a, b in segs:
        offs.append((a, b, acc)); acc += b - a

    def m(x):
        for a, b, o in offs:
            if a <= x <= b:
                return o + x - a
        return None
    sents = []
    for s in t["sentences"]:
        if not s["keep"]:
            continue
        ws = []
        for w in s["words"]:
            if not w.get("keep", True):
                continue
            st, en = m(w["start"]), m(w["end"])
            if st is not None and en is not None:
                ws.append({"text": w["text"], "start": round(st, 3), "end": round(en, 3)})
        if ws:
            sents.append({"id": s["id"], "start": ws[0]["start"], "end": ws[-1]["end"],
                          "text": "".join(w["text"] for w in ws), "words": ws})
    return sents, acc


p = argparse.ArgumentParser()
p.add_argument("transcript")
p.add_argument("-o", "--out", default=None)
p.add_argument("--pad", type=float, default=0.05)
a = p.parse_args()
tp = Path(a.transcript)
t = load(tp)
media = (tp.parent / t["media"]).resolve()
segs = segments(t, a.pad)
end = duration(media)
segs = [[round(x, 3), round(min(y, end), 3)] for x, y in segs if x < end]
out = Path(a.out or tp.parent / "cut.mp4")
parts = "".join(f"[0:v]trim={x}:{y},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS,"
                f"afade=t=in:d=0.01,afade=t=out:st={max(0, y - x - 0.01):.3f}:d=0.01[a{i}];" for i, (x, y) in enumerate(segs))
graph = parts + "".join(f"[v{i}][a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
fg = out.with_suffix(".filter.txt"); fg.write_text(graph, encoding="utf-8")
subprocess.run([need("ffmpeg"), "-y", "-v", "error", "-i", str(media), "-filter_complex", graph,
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
sents, total = remap(t, segs)
save(out.with_suffix(".json"), {"version": 1, "media": out.name, "duration": round(total, 3),
                                "segments": segs, "sentences": sents})
print(f"{len(segs)} ranges, {end:.1f}s -> {total:.1f}s : {out}")
