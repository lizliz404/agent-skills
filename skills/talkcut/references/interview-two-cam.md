# Interview two-cam methodology

Phone dual-cam interview footage: **two phones filming the same event** = two
video sources + two audio sources. This is the current production method for
interview-type videos (e.g. the 2026-11 interview batches). Codified from
Liz's spec 2026-11-08; do not water down the numbers or the hard rules.

## 1. Sources and sync

- Same event recorded by two phones → two video files, each carrying its own
  audio. Treat them as a pair, not as alternatives.
- **Time-align first.** The pipeline computes the offset by cross-correlation
  and stores it in `sync-offsets.json` (model:
  `b_time = offset_sec + (1+rate)*a_time`, with drift and residual stats).
  Never assume the two recordings started together; never hand-edit times
  before the offset is known.
- **Dual-cam output uses BOTH videos** — stacked top/bottom layout — not one
  picked winner.
- Audio source: either is acceptable if both recorded decently. Built-in phone
  mics on the same event sound similar enough that mic quality is not the
  deciding factor. Pick pragmatically: the current pipeline uses the
  **transcription-source camera's audio** so the transcript stays in A/V sync
  with the footage it describes.

## 2. Speed

- Default **1.05×–1.15×** for the interview two-cam format, never 1.0×.
- This supersedes the older more-conservative guidance in
  `production-lessons.md` §4 — Liz's new spec is the authority for this
  format. It does not apply to single-cam talking-head, which keeps its own
  defaults. If a project needs outside this range, ask; don't drift back to
  1.0.

## 3. BGM

- BGM is **always ducked under voice** (sidechain compression keyed to speech).
  It must never overpower speech — when in doubt, duck harder.
- BGM library is a growing collection. **Every track needs text metadata**
  (mood / genre / description) so the agent can select quickly and
  confidently. A track without metadata is not selectable; add the metadata
  when adding the track.

## 4. Visual framing

- Source and deliverable are **both 9:16** — no width cropping is needed. Only
  vertical framing matters.
- Keep the person's head inside the cropped band approximately. Do not
  over-engineer framing: good filming should carry most of it; slight drift
  is acceptable.
- **Leave the center black band free for subtitles.** It is a reserved zone,
  not empty space to fill.

## 5. Captions

- White text **burned on the black center band**.
- **Semantic segmentation, not mechanical character-count.** Segment at
  phrase/clause/pause boundaries; ASR sentence IDs are timing units, not
  guaranteed grammar.
- Flexible range **6–14 characters per cue**. This is deliberately relaxed
  from the older rigid 8–12 guidance: overly strict rules make the AI
  over-optimize and cost more than they gain. Short complete cues are fine;
  don't strand conjunctions or split names/number+unit to hit a count.
- **Renderer reality check:** the production composer (`compose_v2.py`) hard-caps
  cues at `CAP_MAX_CHARS = 12` at burn time. So 6–14 is the semantic
  readability guide, but interview finals must still fit ≤12 chars/line —
  when the two conflict, the renderer geometry wins.

## 6. Speaker-lit border dots (optional)

- Small dots on the frame border lit red/green by who is currently talking.
- Nice-to-have garnish: cheap to implement, visually positive. Keep optional;
  never let it block delivery.

## 7. Edit core

- **Transcript first.** The edit is decided on the transcript, not on
  scrubbing footage.
- **What counts as 废片 is defined by the human (Liz).** Pure-AI judgement
  over-cuts because of RLHF / social-media priors — it trims what "looks
  cuttable" rather than what the human wants gone. AI proposes; the human's
  cut definition wins.
- Surviving **minimal clip units** (film units) can then be freely
  recombined, reordered and truncated into storylines. Reordering is a
  feature of this format, not a violation.

## 8. Covers

- **Diversity is mandatory**: never repeat a layout/style across a batch.
- Interview-layout hard rule: **title text MUST sit in the center band** —
  this keeps both faces visible above and below it. Non-negotiable for this
  layout.

## 9. Implementation reality (read before assuming the skill runs this)

- The production pipeline for this format lives **outside this skill** at
  `/home/liz/anotherlinuxspace/video_content_creation/publish/_shared/`
  — current composer: `compose_v2.py` (1080×1920, A-cam top / B-cam bottom,
  speaker border, semantic caption re-segmentation).
- Per-project manifests drive it, e.g. `film-units-v3.json`, `bgm-map.json`,
  `sync-offsets.json`, `cover-styles.json` under each project's `work/` or
  `_shared/`.
- **Skill docs and the live pipeline can drift.** This document records the
  methodology; verify against the actual scripts/manifests before quoting
  exact parameters from either side.
