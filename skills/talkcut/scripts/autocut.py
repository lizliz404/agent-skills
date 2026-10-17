#!/usr/bin/env python3
"""Step 4: AI first-pass cut marks (only edits keep flags; the video is untouched).

Two layers, each recorded in sentence["by"] so the review page can show who cut what:
  1) Heuristic ("rule", on by default): adjacent sentences with bigram Dice similarity >= threshold and
     gap <= max-gap s -> retake, keep the last take; fillers-only sentence -> cut. Adapted from hotclip's retakes.ts.
  2) Semantic layer ("ai", --plan plan.json): written by the agent after reading the whole transcript
     (contract in SKILL.md). Validated strictly; overrides the heuristic.
Usage: python3 autocut.py work/transcript.json [--plan work/plan.json] [--pause 0.5] [--check-only]
"""
import argparse, re, sys
from common import load, save

FILLERS = set("嗯 啊 呃 额 哦 唉 诶 那个 就是 然后 对吧 emm um uh".split())  # Chinese + English filler words (data)
TYPES = {"retake", "false_start", "filler", "off_topic", "other"}


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


def mark(s, keep, reason, by):
    s["keep"], s["reason"], s["by"] = keep, reason, by


def heuristic(sents, thr, max_gap, min_chars, look):
    for i, s in enumerate(sents):
        if s.get("by") == "manual":
            continue  # never override the human
        t = norm(s["text"])
        if s["words"] and all(norm(w["text"]) in FILLERS or not norm(w["text"]) for w in s["words"]):
            mark(s, False, "fillers only", "rule"); continue
        if len(t) < min_chars:
            continue
        for j in range(i + 1, min(i + 1 + look, len(sents))):
            o = sents[j]
            if o["start"] - s["end"] > max_gap:
                break
            u = norm(o["text"])
            # The earlier take is often a fragment of the later one: also compare against the later take truncated
            sim = max(dice(t, u), dice(t, u[:len(t)]) if len(u) > len(t) else 0)
            if sim >= thr:
                mark(s, False, f"retake ({sim:.2f}), keeping #{o['id']}", "rule"); break


def validate(plan, sents):
    """Return a list of errors; empty list = valid."""
    err, by = [], {s["id"]: s for s in sents}
    extra = set(plan) - {"cut", "keep", "cut_words", "notes"}
    if extra:
        err.append(f"unknown top-level keys: {sorted(extra)}")
    cut_ids = set()
    for k, c in enumerate(plan.get("cut", [])):
        where = f"cut[{k}]"
        if not isinstance(c, dict) or not isinstance(c.get("id"), int):
            err.append(f"{where}: needs integer 'id'"); continue
        if c["id"] not in by:
            err.append(f"{where}: sentence id {c['id']} does not exist"); continue
        if not isinstance(c.get("reason"), str) or not c["reason"].strip():
            err.append(f"{where}: needs a non-empty 'reason'")
        if c.get("type", "other") not in TYPES:
            err.append(f"{where}: type must be one of {sorted(TYPES)}")
        if c.get("type") == "retake":
            kept = c.get("kept")
            if not isinstance(kept, int) or kept not in by:
                err.append(f"{where}: retake needs 'kept' = id of the surviving take")
            elif kept <= c["id"]:
                err.append(f"{where}: kept #{kept} must come AFTER #{c['id']} (keep the LAST take)")
        cut_ids.add(c["id"])
    for k, c in enumerate(plan.get("cut", [])):
        if isinstance(c, dict) and c.get("type") == "retake" and c.get("kept") in cut_ids:
            err.append(f"cut[{k}]: kept #{c['kept']} is itself cut; point 'kept' at the final surviving take")
    for k, x in enumerate(plan.get("keep", [])):
        i = x.get("id") if isinstance(x, dict) else x
        if i not in by:
            err.append(f"keep[{k}]: sentence id {i!r} does not exist")
        elif i in cut_ids:
            err.append(f"keep[{k}]: #{i} is also in cut")
    for k, c in enumerate(plan.get("cut_words", [])):
        where = f"cut_words[{k}]"
        if not isinstance(c, dict) or c.get("id") not in by:
            err.append(f"{where}: needs an existing sentence 'id'"); continue
        n = len(by[c["id"]]["words"])
        f, t = c.get("from"), c.get("to")
        if not (isinstance(f, int) and isinstance(t, int) and 0 <= f <= t < n):
            err.append(f"{where}: need 0 <= from <= to < {n} (word indexes, inclusive)")
        elif f == 0 and t == n - 1:
            err.append(f"{where}: covers the whole sentence; use 'cut' instead")
        if not isinstance(c.get("reason"), str) or not c["reason"].strip():
            err.append(f"{where}: needs a non-empty 'reason'")
    return err


def apply_plan(plan, sents):
    by = {s["id"]: s for s in sents}
    for c in plan.get("cut", []):
        if by[c["id"]].get("by") != "manual":
            mark(by[c["id"]], False, c["reason"], "ai")
    for x in plan.get("keep", []):
        i = x.get("id") if isinstance(x, dict) else x
        if by[i].get("by") != "manual":
            mark(by[i], True, x.get("reason", "") if isinstance(x, dict) else "", "ai")
    for c in plan.get("cut_words", []):
        s = by[c["id"]]
        for w in s["words"][c["from"]:c["to"] + 1]:
            w["keep"], w["by"] = False, "ai"
        s["reason"] = c["reason"]; s.setdefault("by", "ai")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("transcript")
    p.add_argument("--plan")
    p.add_argument("--check-only", action="store_true", help="validate plan.json and exit")
    p.add_argument("--no-heuristic", action="store_true")
    p.add_argument("--similarity", type=float, default=0.72)
    p.add_argument("--max-gap", type=float, default=20)
    p.add_argument("--min-chars", type=int, default=6)
    p.add_argument("--lookahead", type=int, default=2)
    p.add_argument("--pause", type=float, help="longest pause to keep (s); longer silences are shortened to this")
    a = p.parse_args()
    t = load(a.transcript); S = t["sentences"]
    plan = load(a.plan) if a.plan else None
    if plan is not None:
        errs = validate(plan, S)
        if errs:
            print("plan.json is invalid:\n  " + "\n  ".join(errs)); sys.exit(2)
        if a.check_only:
            print("plan.json OK"); sys.exit(0)
    if not a.no_heuristic:
        heuristic(S, a.similarity, a.max_gap, a.min_chars, a.lookahead)
    if plan is not None:
        apply_plan(plan, S)
    if a.pause is not None:
        t["pause_keep"] = a.pause
    save(a.transcript, t)
    cut = [s for s in S if not s["keep"]]
    print(f"Marked {len(cut)}/{len(S)} sentences for cutting")
    for s in cut:
        print(f"  #{s['id']} [{s['start']:.1f}s] {s['text'][:30]} <- {s.get('by')}: {s['reason']}")
