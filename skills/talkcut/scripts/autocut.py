#!/usr/bin/env python3
"""步骤 4：AI 初剪标记（只改 keep 标记，不动视频）。

两层：
  1) 规则兜底（--heuristic，默认开）：相邻句 bigram Dice 相似度 ≥ 阈值且间隔 ≤ max-gap 秒 → 判为重说，
     保留最后一遍；整句只有语气词 → 删。思路参考 hotclip 的 retakes.ts。
  2) 语义层（--plan plan.json）：由 Agent 自己通读逐字稿后写出的决定，覆盖规则结果。
     plan.json 格式：{"cut": [{"id": 3, "reason": "重说，保留第 5 句"}], "keep": [7],
                      "cut_words": [{"id": 9, "from": 0, "to": 2, "reason": "开头口误"}]}
用法: python3 autocut.py work/transcript.json [--plan work/plan.json] [--pause 0.5]
"""
import argparse, re
from common import load, save

FILLERS = set("嗯 啊 呃 额 哦 唉 诶 那个 就是 然后 对吧 emm um uh".split())


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
            s["keep"], s["reason"] = False, "纯语气词"
            continue
        if len(t) < min_chars:
            continue
        for j in range(i + 1, min(i + 1 + look, len(sents))):
            o = sents[j]
            if o["start"] - s["end"] > max_gap:
                break
            u = norm(o["text"])
            # 前一遍常是后一遍的残句：比较时把长句截到短句长度 + 比较整体
            sim = max(dice(t, u), dice(t, u[:len(t)]) if len(u) > len(t) else 0)
            if sim >= thr:
                s["keep"], s["reason"] = False, f"重说（{sim:.2f}），保留第 {o['id']} 句"
                break


p = argparse.ArgumentParser()
p.add_argument("transcript")
p.add_argument("--plan")
p.add_argument("--no-heuristic", action="store_true")
p.add_argument("--similarity", type=float, default=0.72)
p.add_argument("--max-gap", type=float, default=20)
p.add_argument("--min-chars", type=int, default=6)
p.add_argument("--lookahead", type=int, default=2)
p.add_argument("--pause", type=float, help="保留的最长气口（秒），更长的静音会被压到这个长度")
a = p.parse_args()
t = load(a.transcript)
S = t["sentences"]
if not a.no_heuristic:
    heuristic(S, a.similarity, a.max_gap, a.min_chars, a.lookahead)
if a.plan:
    plan, by = load(a.plan), {s["id"]: s for s in S}
    for c in plan.get("cut", []):
        by[c["id"]]["keep"], by[c["id"]]["reason"] = False, c.get("reason", "AI 标记")
    for k in plan.get("keep", []):
        by[k]["keep"], by[k]["reason"] = True, ""
    for c in plan.get("cut_words", []):
        for w in by[c["id"]]["words"][c["from"]:c["to"] + 1]:
            w["keep"] = False
        by[c["id"]]["reason"] = c.get("reason", "删词")
if a.pause is not None:
    t["pause_keep"] = a.pause
save(a.transcript, t)
cut = [s for s in S if not s["keep"]]
print(f"标记删除 {len(cut)}/{len(S)} 句")
for s in cut:
    print(f"  #{s['id']} [{s['start']:.1f}s] {s['text'][:30]} ← {s['reason']}")
