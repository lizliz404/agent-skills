# Component triggers: when each packaging layer earns its place

Decision framework distilled from the 2026-11-02 landscape demo job (vc-pi
research pack, `jobs/glide_20261102/work/component-triggers.md`). The structure
is a working rule; the specific 120/180s duration thresholds are heuristics
proposed then — adjust as more videos prove or break them.

Principle: ask what each layer helps the viewer understand. Captions, the top
navigation bar and explanatory compositions are **independent switches** — a
caption plan does not imply a nav bar, and chapters do not imply a diagram.
A player's own seek bar is not a reason to draw a second information-free
progress strip.

## Stage gate

1. `clean_review` stage → nothing is burned. Deliver the clean candidate; keep
   edit sources reversible.
2. Explicit user lock/approval always wins. An already-approved navigation or
   design stays; never retro-remove it because a new threshold appeared.
3. Then, per layer, ask the trigger question below.

## Navigation bar / in-video progress

- OFF: user forbids it; clean_review stage; fewer than 2 real chapters; no
  cross-section orientation need; a single linear demonstration.
- OFF (heuristic): <120s single-thread narrative; 120–180s with only 2 adjacent
  topics and no orientation need.
- ON: ≥3 substantive chapters that each answer a different viewer question,
  plus a real need to locate/revisit (tutorial steps, comparison axes), AND a
  safe area exists. Duration ≥180s alone does not create chapters — "opening /
  middle / end" is not 3 chapters.
- If nav is needed but no safe area: find a non-occluding layout first; never
  cover the work being demonstrated.

## Explanatory compositions

OFF by default — the demonstration itself is the evidence. OFF when:

- pure product/web demo where the cursor and page already explain it;
- the caption already says it (verbal lists, opinions, feature points);
- existing screenshots/PIP/captions express the same relation (don't stack
  three layers competing for attention);
- you cannot write one concrete viewer question (who hands to whom / who
  reports to whom / what depends on what);
- the insert can't get readable dwell time, or would cover the key operation.

ON only for a genuine abstract-relation gap (dispatch / hierarchy / handoff /
dependency / feedback), usually 1–2 inserts total. Generic labels over concrete
project names (子任务 A/B/C, not "AITOS 交付"). Opposing arrows hand off by
crossfade — never leave bidirectional lines stacked. See composition-kit.md.

Duration is not a trigger: a 10-minute demo can ship zero inserts; a 1-minute
clip can earn one.

## First-frame cover (burned poster frame)

Distinct from a standalone cover image (series-covers.md). Burn the paper-strip
cover onto frame 0 when a platform poster frame is wanted. Requirements:

- position over the first frame's real safe area — never over captions, the
  speaker's face/webcam, or the page's key content; each video computes its own
  zone, don't copy coordinates from another job;
- copy gate: captivating, keyword-bearing (e.g. "AI"), states a real
  pain/benefit the video actually delivers — no invented numbers or claims;
- style (Liz, 2026-11-02): plain and direct — ONE solid colour block, a
  second colour showing through as an offset/overflow layer behind it, and
  text in a contrasting colour on top. No logos, no dark card + accent
  border treatments unless asked. Centred is fine when the first frame's
  centre is low-focus small text; otherwise keep clear of captions,
  face/webcam and key content;
- preview the actual composed first frame, not just the overlay PNG.

## End-card URL / CTA banner

When the video demonstrates a visitable resource or the user asks for one:

- verify the real URL (repo routes + live HTTP check); never guess the slug;
- last ~5s, a visible-but-quiet placement (top-centre banner worked), larger
  than captions but restrained;
- must not double-print over the page's own heading/large text — pick the zone
  with the least text collision, use an opaque dark backing so it reads as an
  intentional banner;
- `drawbox` + `drawtext` proved more reliable for a solid backing than ASS
  `BorderStyle=3`, whose box did not render under libass in one job;
- verify by extracting real frames near the end — an ASS event existing in the
  file is not proof text rendered (a malformed `1:42:63` timecode silently
  dropped an overlay once; generate times via the shared `ass_time` helper,
  never hand-format).

## Record keeping

Per job, keep a one-line component decision record: `nav: off — <reason>`,
`compositions: off`, `captions: profile=<name>`. Proving why a layer is off
matters as much as proving why it is on. Beware stale `chapters.json` files
auto-enabling nav on a new job.
