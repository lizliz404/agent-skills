# Agent Skills

Clone-and-use skill packs for AI coding assistants — Claude Code, Cursor, Codex, Hermes, or any agent that reads a `SKILL.md`. Twenty-two packs in `skills/`, each just a folder. No installers, no frameworks, no signup.

Also published on **[lizliz.xyz/skills](https://lizliz.xyz/skills)** — same packs, browsable online.

```mermaid
graph TD
    README["README.md — you are here"] --> SKILLS["skills/ · twenty-two packs<br/>each: SKILL.md + optional scripts/ + references/ (+ evals/)"]
    SKILLS --> VOICE["Voice & content<br/>doubao-tts · video-script-conversion · talkcut"]
    SKILLS --> VISUAL["Replication & visual<br/>landing-page-replication-v5 · webgl-threejs-background-animation<br/>interactive-projects-stream · design-md-visual-system<br/>visual-explainer · claude-design · html-slides · presentation-logic"]
    SKILLS --> TOOLS["Data & tooling<br/>geo-job-hunt · seo-master · clerk-auth · feedback-pipeline · typesafe-ai"]
    SKILLS --> NET["Network / infra<br/>ai-native-mihomo · ai-native-proof-ledger · cloudflare-cost-guard · ai-native-cicd"]
    SKILLS --> METHOD["Method & orchestration<br/>fleet-orch · software-factory"]
    SKILLS -.-> SITE["lizliz.xyz/skills"]
    SKILLS -.->|"soft route"| DT["design-templates asset pack"]
```

## What This Does

**Agent skills are instruction packs for coding AIs.** Instead of re-explaining your process every session — "capture the page, check density, verify offline" — you hand the agent a skill folder and it follows the workflow, runs the scripts, and hits the same gates you would.

These packs come from real pipelines on lizliz.xyz: they were built to get actual work done, then packaged so anyone can reuse them. **AI-Native Proof Ledger** and **Software Factory** are researched reference skills; **AI-Native CI/CD** is a researched decision skill; **Cloudflare Cost Guard** combines official documentation with reviewed operational lessons; runtime coverage and delivery still require acceptance. These are not presented as production-validated pipelines. A skill is just a folder — `SKILL.md` (the workflow map) plus optional `scripts/` and `references/` that the agent loads when it needs them.

## The Packs

<p align="center">
  <img src="https://lizliz.xyz/assets/icons/skills/doubao-tts.svg" width="48" alt="Doubao TTS" />
  <img src="https://lizliz.xyz/assets/icons/skills/geo-job-hunt.svg" width="48" alt="Geo Job Hunt" />
  <img src="https://lizliz.xyz/assets/icons/skills/landing-page-replication-v5.svg" width="48" alt="Landing Page Replication v5" />
  <img src="https://lizliz.xyz/assets/icons/skills/video-script-conversion.svg" width="48" alt="Video Script Conversion" />
  <img src="https://lizliz.xyz/assets/icons/skills/design-md-visual-system.svg" width="48" alt="DESIGN.md Visual System" />
  <img src="https://lizliz.xyz/assets/icons/skills/webgl-threejs-background-animation.svg" width="48" alt="WebGL Three.js Background Animation" />
  <img src="https://lizliz.xyz/assets/icons/skills/interactive-projects-stream.svg" width="48" alt="Interactive Projects Stream" />
  <img src="https://lizliz.xyz/assets/icons/skills/seo-master.svg" width="48" alt="SEO Master" />
  <img src="https://lizliz.xyz/assets/icons/skills/github-telegram-feedback-pipeline.svg" width="48" alt="GitHub Telegram Feedback Pipeline" />
</p>

- **Doubao TTS** — Turn articles into spoken audio, dual-speaker podcasts, and ASR transcripts via Volcengine 豆包语音 · [doubao-tts/](skills/doubao-tts/)
- **Talkcut** — Cut talking-head videos: Doubao Speech (豆包语音) per-character ASR → AI keeps only the last take of repeated lines and preserves breathing pauses → localhost strike-through review → ffmpeg render + per-word highlight subtitles + chapter navigation bar · [talkcut/](skills/talkcut/)
- **Geo Job Hunt** — Find jobs inside a map radius — Amap fence + Liepin hiring, batch apply with rate-limit guardrails · [geo-job-hunt/](skills/geo-job-hunt/)
- **Landing Replication v5** — Copy a marketing landing page with measurable gates: capture, density, micro-parity, offline behavior probes · [landing-page-replication-v5/](skills/landing-page-replication-v5/)
- **Video Script Conversion** — Rebuild, refine, and audit spoken-voice scripts from articles — five seconds decide if viewers stay · [video-script-conversion/](skills/video-script-conversion/)
- **DESIGN.md Visual System** — Write implementation-grade DESIGN.md — YAML tokens plus the judgment prose agents need to ship UI without inventing taste · [design-md-visual-system/](skills/design-md-visual-system/)
- **WebGL Three.js Background Animation** — WebGL that blends into the page — config-driven, GPU-budgeted, full lifecycle hygiene · [webgl-threejs-background-animation/](skills/webgl-threejs-background-animation/)
- **Interactive Projects Stream** — Continuous clickable content stream — lane-track transport, accordion-style skill popups, D/H/P previews, zero deps · [interactive-projects-stream/](skills/interactive-projects-stream/)
- **SEO Master** — Full-site SEO/GEO audit plus generative-engine citation measurement — evidence ladder, not vibes · [seo-master/](skills/seo-master/)
- **GitHub Telegram Feedback Pipeline** — Same-origin CF Pages feedback → GitHub Issues and/or Telegram; quiet bilingual product sheet, not a SaaS FAB · [github-telegram-feedback-pipeline/](skills/github-telegram-feedback-pipeline/)
- **Clerk Auth** — Add Clerk authentication via the Clerk CLI — Windows-capable wrapper, split credential storage, Next.js matcher check · [clerk-auth/](skills/clerk-auth/)
- **AI-Native Mihomo** — Headless mihomo (Clash Meta) core + REST API as the agent control surface — self-heal, proxy doctrine, TUN debug playbook, runbook · [ai-native-mihomo/](skills/ai-native-mihomo/)
- **AI-Native Proof Ledger** — Tamper-evident, independently verifiable history for SaaS and agents — mechanism ladder L0–L5, witnessed checkpoints, anchoring, claim rubric · [ai-native-proof-ledger/](skills/ai-native-proof-ledger/)
- **Cloudflare Cost Guard** — Audit runaway billing risks and adapt quiet monitoring: native alerts first, hourly routine checks, evidence-based coverage and safe handoffs. Merged workflow with frequency-migration and delivery scenarios; no bundled monitoring daemon · [cloudflare-cost-guard/](skills/cloudflare-cost-guard/) · [cross-check report](docs/cloudflare-cost-guard-crosscheck-v0.2.0.md)
- **AI-Native CI/CD** — Choose, migrate, or optimize CI/CD: laziness-ordered decision ladder, verified 2026-11 pricing, self-hosted runner doctrine, agent-native CI features · [ai-native-cicd/](skills/ai-native-cicd/)
- **Codex Design** — High-fidelity design artifacts in HTML — landings, decks, prototypes, posters; fact-check first, commit to a visual system, avoid AI-design tropes · [claude-design/](skills/claude-design/)
- **Presentation Logic** — 学术演讲的论证先行：提炼主线、自我质疑、输出可审阅叙事文档，做幻灯片之前用 · [presentation-logic/](skills/presentation-logic/)
- **HTML Slides** — From a confirmed outline, generate 1920×1080 academic HTML slides with a strict template, then optional PPTX assembly · [html-slides/](skills/html-slides/)
- **Visual Explainer** — Turn processes, SOPs, and system relationships into beginner-friendly SVG/HTML diagrams · [visual-explainer/](skills/visual-explainer/)
- **TypeSafe AI** — TypeSafe System One (Jev) for typed semantic judgments — yes/no, closed-set choice, ordered score — not text generation · [typesafe-ai/](skills/typesafe-ai/)
- **Fleet Orch** — Supervised overnight fleet of terminal coding agents on one machine: dispatch narrow tasks, watchdog, verify receipts, hand off the boss role · [fleet-orch/](skills/fleet-orch/)
- **Software Factory** — Decide whether, and how, to industrialize agent work: first-principles invariants, a laziness-ordered ladder, and due diligence on 2026 "AI software factory" practices · 软件工厂打法 · [software-factory/](skills/software-factory/)

## Key Features

- **Clone and use** — A pack is a folder: copy it into your agent's skills directory, done. No npm, no build step, no config.
- **Agent-agnostic** — Any coding agent that reads `SKILL.md` can follow the workflow; scripts are stdlib-only Python where possible.
- **Evidence-led** — Execution packs include probes and checks where useful; reference and workflow packs state their validation requirements and limits.
- **Validation is explicit** — Production pipeline packs, researched references, and initial workflows are identified separately.
- **Free, MIT** — Use it, modify it, share it.

## Installation

Pick one pack, or grab everything:

```bash
# Everything at once
git clone https://github.com/lizliz404/agent-skills.git
# ...then copy the pack folders you want into your agent's skills directory

# Or cherry-pick one pack straight into place
git clone --depth 1 https://github.com/lizliz404/agent-skills.git
cp -r agent-skills/skills/doubao-tts ~/.claude/skills/
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
| `evals/` | Where provided: behavior scenarios or executable checks; declared cases alone are not passing test evidence |

The agent reads the map first and pulls in only the files the current task needs.

## Philosophy

This repo exists because of a few beliefs:

1. **The fastest way to learn a process is to watch someone who already runs it.** These skills are that, packaged.
2. **Dependencies are debt.** A stdlib-only Python script will work in ten years. A pinned framework will not.
3. **Vibes are not verification.** Every pack has numbers you can check: density scores, character counts, probe results.
4. **Clone and use is the whole point.** If a skill needs a ceremony to install, it is not a skill, it is a project.

## Credits

Created by [@lizliz404](https://x.com/lizliz404).

## Related

- Asset pack (soft route): [lizliz404/design-templates](https://github.com/lizliz404/design-templates) · map `templates/sibling-routes.md`
- Landing replication loads pack orbs/shaders/Beautiful UI when `WEBGL_THEATER` or agent chrome is the mechanism — it does not vendor those folders.

## License

MIT — Use it, modify it, share it.
