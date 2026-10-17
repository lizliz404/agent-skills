#!/usr/bin/env python3
"""Step 7: subtitles from cut.json.

  --style simple   white text, black outline (SRT + ASS)
  --style karaoke  per-word highlight: current word recoloured + enlarged (ASS, one event per word; any player/ffmpeg can burn it)
  --burn           burn the ASS into the video with ffmpeg -> cut_<style>.mp4; otherwise only export files (drag into CapCut / 剪映)
Usage: python3 subs.py work/cut.json --caption-plan work/caption-plan.json --style karaoke --burn
Without --caption-plan only draft exports are allowed; --max-chars controls draft grouping.
"""
import argparse, json, re, subprocess
from pathlib import Path
from common import load, need, ts, video_info
from caption_plan import map_plan

PUNCT = "，。！？；、,.!?;：:"


def lines(sents, max_chars):
    """Split sentences into subtitle lines by punctuation and length, keeping word timings."""
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
p.add_argument("--highlight", default="&H00FFC864", help="ASS BGR colour, default light blue")
p.add_argument("--burn", action="store_true")
p.add_argument("--caption-plan", type=Path, help='Reviewed semantic cue JSON; required for final burning')
a = p.parse_args()
cp = Path(a.cut); c = load(cp)
video = cp.parent / c["media"]
if a.burn and not a.caption_plan:
    p.error('Final burn requires --caption-plan with reviewed semantic cues; fixed-count splitting is draft-only')
if a.caption_plan:
    plan = load(a.caption_plan)
    if a.burn and not (plan.get('reviewed_by') or plan.get('reviewed') is True):
        p.error('Semantic cue plan must be reviewed before burning (reviewed_by or reviewed:true)')
    mapped = map_plan(c, plan)
    chars = []
    for sentence in c['sentences']:
        for word in sentence['words']:
            text = word['text']; duration = word['end'] - word['start']
            chars.extend({'text':ch, 'start':word['start']+duration*j/len(text), 'end':word['start']+duration*(j+1)/len(text)} for j,ch in enumerate(text))
    L = [chars[cue['char_start']:cue['char_end']] for cue in mapped['cues']]
    cp.with_name('captions.json').write_text(json.dumps(mapped, ensure_ascii=False, indent=2), encoding='utf-8')
else:
    print('DRAFT ONLY: fixed-count cue grouping is not approved semantic segmentation')
    L = [l for l in lines(c["sentences"], a.max_chars) if clean("".join(w["text"] for w in l))]
W, H, _ = video_info(video)

def display(text):
    return text if a.caption_plan else clean(text)

def escape_ass(text):
    return text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').replace('\n', r'\N')

srt = [f"{i}\n{ts(l[0]['start'])} --> {ts(l[-1]['end'])}\n{display(''.join(w['text'] for w in l))}\n" for i, l in enumerate(L, 1)]
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
        ev.append(f"Dialogue: 0,{ass_time(l[0]['start'])},{ass_time(l[-1]['end'])},Base,,0,0,0,,{escape_ass(display(''.join(w['text'] for w in l)))}")
        continue
    words = [w for w in l if display(w["text"])]
    for k, w in enumerate(words):  # one event per word: current word highlighted and enlarged, others white
        end = words[k + 1]["start"] if k + 1 < len(words) else l[-1]["end"]
        txt = "".join((f"{{\\c{a.highlight}&\\fscx118\\fscy118}}{escape_ass(display(x['text']))}{{\\r}}" if j == k else escape_ass(display(x["text"])))
                      for j, x in enumerate(words))
        ev.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(end)},Base,,0,0,0,,{txt}")
ass = cp.with_suffix(f".{a.style}.ass")
ass.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")
print(f"{len(L)} subtitle lines -> {cp.with_suffix('.srt')} , {ass}")
if a.burn:
    out = cp.with_name(cp.stem + f"_{a.style}.mp4")
    subprocess.run([need("ffmpeg"), "-y", "-v", "error", "-i", video.name, "-vf", f"ass={ass.name}",
                    "-c:v", "libx264", "-crf", "18", "-c:a", "copy", str(out.name)], check=True, cwd=cp.parent)
    print(f"Burned in -> {out}")
