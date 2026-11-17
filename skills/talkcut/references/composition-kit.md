# Composition kit — dark-glass ASS figure layer (2026-11-02)

`scripts/compositions.py` turns `compositions-plan.json` into ONE `.ass` vector
layer for the `ass` filter. This is the current default for explanatory
compositions on **screen-heavy / dark footage** (replaces the light paper-card
look used in 2026-10 jobs). Same discipline as before: sparse inserts, reveal
one thought at a time synced to speech, no new video stack.

## Pipeline

1. From `work/cut.json` pick the sentences whose logic is genuinely complex
   (fan-out, hierarchy, one-way communication, backstop). **One or two spots
   is usually right** — a list the speech already says clearly earns no card.
2. Write `compositions-plan.json` (see header of `scripts/compositions.py`
   for the full schema): `type`, `title`, `start`/`end` (final-cut seconds),
   content fields, and a `t` map pinning each reveal to a sentence start.
3. `python3 scripts/compositions.py plan.json -o work/compositions.ass`
4. Burn: `ffmpeg -i cut.mp4 -vf "ass=compositions.ass,format=yuv420p"
   -c:v libx264 -crf 19 -c:a aac out.mp4`

Preview without a full render: seek AFTER input so ASS timestamps apply —
`ffmpeg -i cut.mp4 -ss T -vf "ass=..." -frames:v 1 out.jpg`
(`-ss` before `-i` resets timestamps and the overlay never lands).

## Figure types

- `dispatch` — boss chip fans out to generic task chips, then thin return
  arrows take over the same lanes as outgoing arrows fade away. Use generic
  labels such as `子任务 A/B/C` when explaining the mechanism rather than
  transcribing specific project/task names.
  For "one task splits into parallel work, results come back".
- `questions` — numbered rows with small icons, revealed per spoken question.
- `stack` — boss chip on top, worker row, upward arrows (one-way report),
  dashed watchdog band at the bottom. For layered runtime architecture.
- `handoff` — 2–3 node chain with icons and a check stamp. For "X hands a
  deliverable to Y, done".

Content rules: ≤ ~10 chars of Chinese per node label; worker names real
(read them off the footage) or generic `agent`; one amber accent, one green
only for completion.

## libass gotchas learned the hard way

- **Alpha inside `\1c` is broken for `\p` drawings.** `{\1c&HD83CAAEB\p1}`
  renders solid white / opaque — always write opaque `\1c&H00BBGGRR` plus a
  separate `\1a&Hxx`. (Evidence: 2026-11-02 alpha test, three rect probe.)
- An "edge ring" drawn as a full rect + tinted inner rect reads as a solid
  block — the tinted inner blends with the opaque outer. Cut the ring with an
  **opaque** interior rect first (`SURF`), then tint on top if wanted.
- Drawings are placed by `\pos` (origin of path coords); `\fscx/\fscy` scale
  around it → pop-in nodes need paths **relative to their centre** +
  `\pos(cx,cy)`. `\move` animates that anchor (rise-in). `\clip` stays in
  absolute video coords → arrows stay `\pos(0,0)` and reveal via
  `\t(...\clip(...))` wipe, head fades on ~0.3 s later. Keep these tags
  inside ONE override block: `extra` passed to `draw_abs` must not contain
  another `{...}` block, which can make the entire shaft disappear.
- `connector(points, width=6, radius=18, head_size=22)` draws a single filled
  outline with cubic Bézier elbows/round caps plus an open, softened chevron.
  Pass distinct, orthogonal route points; separate ports at node boundaries.
  Leave a straight landing before the head so it does not crowd an elbow.
  `arrow_h` / `arrow_v` are directional straight-route wrappers.
- Keep every element's fade-out (`\fad(...,240–300)`) so cards exit cleanly.
  For opposing arrows, crossfade their phases instead of leaving both sets
  stacked: dispatch ends its outgoing event 160ms after return starts; the
  260ms exit clears the old head before the new head appears at +280ms.

## Legibility on phone

Card 948 px wide on a 1080×1920 portrait frame, ~9-10 px visual margin to
frame edge; 3 px card hairline; title 64 bold; node labels 40–44; captions
34–40. Shafts 6 px (dim returns 4 px), heads up to 22 px, scaled down for
short gaps. Check actual frames at title-only, mid, arrow handoff and complete
states — a still doesn't prove reveal order. Visually centre labels inside
chips/bands; verify padding to all nearby edges, not merely the anchor
coordinates. Keep secondary arrow labels inside the card's right padding.

Regression check (includes a synthetic libass render, no footage):
`python3 -m unittest discover -s scripts -p test_compositions.py -v`.
