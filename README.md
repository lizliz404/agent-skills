# Agent Skills

Downloadable, unzip-and-use skill packs for AI coding assistants — Claude Code, Cursor, Codex, Hermes, or any agent that reads a `SKILL.md`. Eight packs, each with its own ready-to-download zip. No installers, no frameworks, no signup.

Also published on **[lizliz.xyz/skills](https://lizliz.xyz/skills)** — same packs, same zips.

## What This Does

**Agent skills are instruction packs for coding AIs.** Instead of re-explaining your process every session — "capture the page, check density, verify offline" — you hand the agent a skill folder and it follows the workflow, runs the scripts, and hits the same gates you would.

These eight packs come from real pipelines on lizliz.xyz: they were built to get actual work done, then packaged so anyone can reuse them. A skill is just a folder — `SKILL.md` (the workflow map) plus `scripts/` and `references/` that the agent loads when it needs them.

## The Packs

<p align="center">
  <img src="assets/skills/doubao-tts.svg" width="48" alt="Doubao TTS" />
  <img src="assets/skills/geo-job-hunt.svg" width="48" alt="Geo Job Hunt" />
  <img src="assets/skills/landing-page-replication-v5.svg" width="48" alt="Landing Page Replication v5" />
  <img src="assets/skills/video-script-conversion.svg" width="48" alt="Video Script Conversion" />
  <img src="assets/skills/design-md-visual-system.svg" width="48" alt="DESIGN.md Visual System" />
  <img src="assets/skills/webgl-threejs-background-animation.svg" width="48" alt="WebGL Three.js Background Animation" />
  <img src="assets/skills/interactive-projects-stream.svg" width="48" alt="Interactive Projects Stream" />
  <img src="assets/skills/seo-master.svg" width="48" alt="SEO Master" />
</p>

- **Doubao TTS** — Turn articles into spoken audio, dual-speaker podcasts, and ASR transcripts via Volcengine 豆包语音 · [doubao-tts.zip](skills/doubao-tts/doubao-tts.zip)
- **Geo Job Hunt** — Find jobs inside a map radius — Amap fence + Liepin hiring, batch apply with rate-limit guardrails · [geo-job-hunt.zip](skills/geo-job-hunt/geo-job-hunt.zip)
- **Landing Replication v5** — Copy a marketing landing page with measurable gates: capture, density, micro-parity, offline behavior probes · [landing-page-replication-v5.zip](skills/landing-page-replication-v5/landing-page-replication-v5.zip)
- **Video Script Conversion** — Rebuild, refine, and audit spoken-voice scripts from articles — five seconds decide if viewers stay · [video-script-conversion.zip](skills/video-script-conversion/video-script-conversion.zip)
- **DESIGN.md Visual System** — Write implementation-grade DESIGN.md — YAML tokens plus the judgment prose agents need to ship UI without inventing taste · [design-md-visual-system.zip](skills/design-md-visual-system/design-md-visual-system.zip)
- **WebGL Three.js Background Animation** — WebGL that blends into the page — config-driven, GPU-budgeted, full lifecycle hygiene · [webgl-threejs-background-animation.zip](skills/webgl-threejs-background-animation/webgl-threejs-background-animation.zip)
- **Interactive Projects Stream** — Continuous clickable content stream — lane-track transport, accordion-style skill popups, D/H/P previews, zero deps · [interactive-projects-stream.zip](skills/interactive-projects-stream/interactive-projects-stream.zip)
- **SEO Master** — Full-site SEO/GEO audit plus generative-engine citation measurement — evidence ladder, not vibes · [seo-master.zip](skills/seo-master/seo-master.zip)

## Key Features

- **Unzip and use** — A pack is a folder: drop it into your agent's skills directory, done. No npm, no build step, no config.
- **Agent-agnostic** — Any coding agent that reads `SKILL.md` can follow the workflow; scripts are stdlib-only Python where possible.
- **Measurable, not vibes** — Every pack ships machine gates: probes, checks, character counters, eval scripts. You can verify the work instead of trusting it.
- **Production-tested** — These are the actual packs running lizliz.xyz pipelines, not toy examples.
- **Free, MIT** — Use it, modify it, share it.

## Installation

Pick one pack, or grab everything:

```bash
# One pack (from the site or this repo)
unzip skills/doubao-tts/doubao-tts.zip -d ~/.claude/skills/

# Everything at once
git clone https://github.com/lizliz404/agent-skills.git
# ...then copy the pack folders you want into your agent's skills directory
```

Where "your agent's skills directory" lives:

| Agent | Path |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills/` |
| Hermes | `~/.hermes/skills/` |
| Codex / others | check the agent's docs — most read `SKILL.md` from a skills folder |

Some packs need environment variables (`AMAP_MAPS_API_KEY`, `MCP_LIEPIN_API_KEY`, `DOUBAO_API_KEY`) — each pack's README explains what it needs and where to get it.

## Usage

Point your agent at the skill and let it work:

```text
Use the landing-page-replication-v5 skill to copy https://example.com — capture, audit, and report the fidelity gates.
```

```text
用 geo-job-hunt 技能：在天河区半径 5 公里内找前端岗位，反向确认公司，列 10 个可投的。
```

Each pack's `SKILL.md` starts with a workflow map, so the agent knows what to do without you spelling it out every time.

## How Each Pack Is Structured

Every pack follows the same shape — **progressive disclosure**:

| Piece | Purpose |
|---|---|
| `SKILL.md` | The workflow map and rules — loaded when the skill is invoked |
| `scripts/` | Run when a step needs computation (capture, transcribe, count, apply) |
| `references/` | Deep notes loaded on demand: API details, cases, checklists |
| `evals/` | Where a pack ships them: gates that prove the workflow did its job |

The agent reads the map first and pulls in only the files the current task needs.

## Philosophy

This repo exists because of a few beliefs:

1. **The fastest way to learn a process is to watch someone who already runs it.** These skills are that, packaged.
2. **Dependencies are debt.** A stdlib-only Python script will work in ten years. A pinned framework will not.
3. **Vibes are not verification.** Every pack has numbers you can check: density scores, character counts, probe results.
4. **Unzip and use is the whole point.** If a skill needs a ceremony to install, it is not a skill, it is a project.

## Credits

Created by [@lizliz404](https://x.com/lizliz404).

## License

MIT — Use it, modify it, share it.
