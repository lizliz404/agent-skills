#!/usr/bin/env python3
"""Step 4: AI first-pass cut marks (only edits keep flags; the video is untouched).

Two layers:
  1) Heuristic fallback (on by default): adjacent sentences with bigram Dice similarity >= threshold and gap <= max-gap s -> retake;
     keep the last take. A sentence made only of fillers -> cut. Adapted from hotclip's retakes.ts.
  2) Semantic layer (--plan plan.json): decisions the agent writes after reading the whole transcript; overrides the heuristic.
     plan.json: {"cut": [{"id": 3, "reason": "retake, keep #5"}], "keep": [7],
                 "cut_words": [{"id": 9, "from": 0, "to": 2, "reason": "false start"}]}
Usage: python3 autocut.py work/transcript.json [--plan work/plan.json] [--pause 0.5]
"""
import argparse, re
from common import load, save

FILLERS = set("嗯 啊 呃 额 哦 唉 诶 那个 就是 然后 对吧 emm um uh".split())  # Chinese + English filler words (data)


def norm(s):
    return re.sub(r"[\W_]+", "", s.lower())


def dice(a, b):
    A = [a[i:i + 2] for i in range(len(a) - 1)] or [a]
    B = [b[i:i + 2] for i in range(len(b) - 1)] or [b]
    pool, hit = list(B), 0
    for x in A:
        if x in pool:
            pool.remove(x); hit += 1
    return 2 * hit / (len(A) + len(B))


def heuristic(sents, thr, max_gap, min_chars, look):
    for i, s in enumerate(sents):
        t = norm(s["text"])
        if t and all(norm(w["text"]) in FILLERS or not norm(w["text"]) for w in s["words"]) and s["words"]:
            s["keep"], s["reason"] = False, "fillers only"
            continue
        if len(t) < min_chars:
            continue
        for j in range(i + 1, min(i + 1 + look, len(sents))):
            o = sents[j]
            if o["start"] - s["end"] > max_gap:
                break
            u = norm(o["text"])
            # The earlier take is often a fragment of the later one: also compare against the later take truncated to the same length
            sim = max(dice(t, u), dice(t, u[:len(t)]) if len(u) > len(t) else 0)
            if sim >= thr:
                s["keep"], s["reason"] = False, f"retake ({sim:.2f}), keeping #{o['id']}"
                break


p = argparse.ArgumentParser()
p.add_argument("transcript")
p.add_argument("--plan")
p.add_argument("--no-heuristic", action="store_true")
p.add_argument("--similarity", type=float, default=0.72)
p.add_argument("--max-gap", type=float, default=20)
p.add_argument("--min-chars", type=int, default=6)
p.add_argument("--lookahead", type=int, default=2)
p.add_argument("--pause", type=float, help="longest pause to keep (s); longer silences are shortened to this")
a = p.parse_args()
t = load(a.transcript)
S = t["sentences"]
if not a.no_heuristic:
    heuristic(S, a.similarity, a.max_gap, a.min_chars, a.lookahead)
if a.plan:
    plan, by = load(a.plan), {s["id"]: s for s in S}
    for c in plan.get("cut", []):
        by[c["id"]]["keep"], by[c["id"]]["reason"] = False, c.get("reason", "AI mark")
    for k in plan.get("keep", []):
        by[k]["keep"], by[k]["reason"] = True, ""
    for c in plan.get("cut_words", []):
        for w in by[c["id"]]["words"][c["from"]:c["to"] + 1]:
            w["keep"] = False
        by[c["id"]]["reason"] = c.get("reason", "words cut")
if a.pause is not None:
    t["pause_keep"] = a.pause
save(a.transcript, t)
cut = [s for s in S if not s["keep"]]
print(f"Marked {len(cut)}/{len(S)} sentences for cutting")
for s in cut:
    print(f"  #{s['id']} [{s['start']:.1f}s] {s['text'][:30]} ← {s['reason']}")
