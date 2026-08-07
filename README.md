# Liz's Agent Skill Packs

Downloadable, unzip-and-use agent skills — the open-source mirror of [lizliz.xyz/skills](https://lizliz.xyz/skills).

Each folder is a complete skill pack (SKILL.md + scripts + references) with its own ready-to-download zip at `skills/<name>/<name>.zip`. For everything at once, use the repo's **Download ZIP** button or `git clone`.

| Skill | What it does | Zip |
|---|---|---|
| [Doubao TTS](skills/doubao-tts/) | Article voice, dual-speaker podcasts, and ASR via Volcengine 豆包语音 | [doubao-tts.zip](skills/doubao-tts/doubao-tts.zip) |
| [Geo Job Hunt](skills/geo-job-hunt/) | Jobs inside a map radius — Amap fence + Liepin hiring, batch apply with guardrails | [geo-job-hunt.zip](skills/geo-job-hunt/geo-job-hunt.zip) |
| [Landing Page Replication v5](skills/landing-page-replication-v5/) | Measurable landing-page fidelity: capture, density, micro-parity, offline behavior probes | [landing-page-replication-v5.zip](skills/landing-page-replication-v5/landing-page-replication-v5.zip) |
| [Video Script Conversion](skills/video-script-conversion/) | Rebuild, refine, and audit spoken-voice scripts from articles | [video-script-conversion.zip](skills/video-script-conversion/video-script-conversion.zip) |
| [DESIGN.md Visual System](skills/design-md-visual-system/) | Implementation-grade DESIGN.md: YAML tokens + judgment prose for coding agents | [design-md-visual-system.zip](skills/design-md-visual-system/design-md-visual-system.zip) |
| [WebGL Three.js Background Animation](skills/webgl-threejs-background-animation/) | WebGL that blends into the page — config-driven, GPU-budgeted, full lifecycle hygiene | [webgl-threejs-background-animation.zip](skills/webgl-threejs-background-animation/webgl-threejs-background-animation.zip) |

## Install

```bash
unzip skills/<name>/<name>.zip -d ~/.<agent>/skills/
# or: copy the folder into your agent's skills directory (Hermes: ~/.hermes/skills/, Claude: ~/.claude/skills/, Cursor: ~/.cursor/skills/)
```

Some packs need env vars (e.g. `AMAP_MAPS_API_KEY`, `MCP_LIEPIN_API_KEY`, `DOUBAO_API_KEY`) — see each pack's README.

## Source of truth

This repo mirrors the zips published on lizliz.xyz. When a skill updates, its zip is refreshed here and on the site together. Pack origins (Liz's dev environment):

| Pack | Canonical dev path |
|---|---|
| doubao-tts | `~/.hermes/skills/media/doubao-tts-article-audio/` |
| geo-job-hunt | `~/.agents/skills/geo-job-hunt/` |
| landing-page-replication-v5 | `~/.hermes/skills/web/landing-page-replication-v5/` |
| video-script-conversion | `~/.hermes/profiles/writing/skills/writing/video-script-conversion/` |
| design-md-visual-system | `~/.hermes/skills/creative/design-md-visual-system/` |
| webgl-threejs-background-animation | `~/.agents/skills/webgl-threejs-background-animation/` |

## License

MIT © Liz (lizliz404)
