# Agent-native CI — what's real as of 2026-11

Every major CI vendor shipped the same product shape: **an agent-facing
control surface (MCP or JSON-first CLI) + autonomous-fixing agents +
agent-safe pipeline primitives**. Details and honest limits below.

## GitHub — Agentic Workflows (`gh-aw`)

- `gh extension install github/gh-aw` — write automation in **Markdown +
  frontmatter**, `gh aw` compiles it to a standard Actions workflow
  (`.lock.yml`). Technical preview 2026-02 → **public preview 2026-06**;
  5.6k★, MIT.
- Engines: Copilot CLI (default), Claude Code, Codex, Gemini, Pi.
- Safety model is the interesting part: read-only by default, sandboxed,
  **Agent Workflow Firewall**, writes only via validated `safe-outputs`
  jobs, SHA-pinned deps, a dedicated threat-detection job scans proposed
  changes before apply.
- Positioning is deliberately narrow: **reasoning tasks** — issue triage,
  PR review, CI failure investigation, docs/reporting. Complements CI,
  doesn't replace builds/tests. Prebuilt catalog: githubnext/agentics.
- Take: GitHub's own answer to "CI for agent output", and it's additive —
  evidence for "don't build a new CI form".

## CircleCI — most complete agent surface

- **Hosted MCP** `https://mcp.circleci.com/v1/mcp` (OAuth2, 2026-09-14),
  24 tools: list_runs → job → logs/tests/artifacts, rerun_workflow
  (from_failed), cancel, validate_config (compiles+expands orbs without
  pushing), orb lookup, deployments/rollback. Earlier npx server deprecated;
  MCP now also embedded in the CircleCI CLI.
- **Design lessons worth stealing** (from their changelog): don't send raw
  logs — replay step output through a terminal model so progress redraws
  collapse, then `tail_lines` (default 500) the end; bounded ring buffer so
  peak memory is bounded; typed output schemas; errors that say what was
  wrong so the model can fix the call; ship instructions on which tool
  answers which question.
- **Chunk** (2025-09 → Chunk CLI): autonomous validation agent — fixes
  flaky tests, config drift, coverage gaps, in the pipelines you already run.
- **Functions** (beta, 2026-11-04): compiled, versioned, tested CI steps
  agents can *discover, configure and validate before running* via CLI/MCP —
  the "orbs, but agent-legible" idea. 10 CircleCI-authored; internal claim:
  ~2× faster pipeline setup, ~40% fewer tokens.
- **Smarter Testing** (GA 2026-10-13): coverage-based test impact analysis
  (run only affected tests — 60–90% skipped on feature branches), in-job
  auto-rerun of flakes, dynamic splitting. Metered in "test atoms".

## Semaphore — `sem-ai`

- One binary, three surfaces: JSON-first CLI, `sem-ai mcp` embedded MCP
  server, Claude Code/Codex plugin (skills + `/sem-ai:init`,
  `/sem-ai:gha-to-semaphore` — a **GHA→Semaphore translator**).
- Compound ops built for agents: `diagnose` chains workflow→pipeline→failed
  jobs→logs→parsed JUnit in one call; `test summary`; `blast-radius` /
  topology; `testbox` runs commands in a real CI env **before you push** —
  closes the fix loop locally.
- Hosted MCP too (OAuth 2.1); write tools (`workflow_run/rerun`) need
  org-level enablement via support.
- Take: the sharpest agent-tooling execution of any CI vendor; also the
  clearest signal that "agent-friendly" is now a competitive axis.

## Buildkite — agentic primitives on the hybrid model

- Four composable blocks: **MCP Server** (remote or local), **Model
  Providers** (LLM calls inside pipeline steps, token handled), **Pipeline
  Triggers**, **Preflight** (experimental — instant fail signal + structured
  results to an agent before commit).
- Wayfair: build-fix time 30min → <5min via the MCP server; marketing claims
  100k+ concurrent CI agents (2026-06).
- Ships Buildkite skills for coding agents; claude-summarize plugin for
  failure analysis.
- Fits the same hybrid doctrine: your compute, their control plane — now
  with an agent surface on top.

## GitLab — Duo Agent Platform

- Agents + Flows over the Orbit context graph. Includes a **CI pipeline
  diagnose-and-fix agent** (root cause → fix MR), a **pipeline-to-GitLab-CI
  converter**, and **Custom Flows** triggered by events incl. pipeline
  events → self-healing pipeline patterns (analyze failed test → generate
  fix → commit → notify) with human checkpoints.
- Goal-driven flows: `/goal Fix the checkout timeout. Continue until tests
  pass and CI is green.` (Duo CLI, headless, Agentic Chat). Announced at
  Transcend 2026-10.
- Take: deepest "CI as one stage of an agent-run lifecycle" vision; only
  relevant if you're already on GitLab.

## Dagger — the overlay bet

- Repositioned as "third-generation CI for coding agents": typed artifacts,
  lazy incremental DAG of sandboxed functions, same pipeline locally and on
  Dagger Cloud with one cache — no YAML in the repo.
- 2026-11-10: runs checks on **GitLab MRs without a GitLab CI job or
  runner** (post-push on Dagger Cloud, pre-push locally). Already did
  GitHub + Entire.
- Take: the credible "new form" — but it's an *execution engine beneath*
  the forge, not a GHA-shaped service. Watch; don't bet the repo on it.

## What "agent-native" actually buys

1. **Structured failure output** — parsed test results, typed schemas, log
   tails — saves tokens and makes agent diagnosis reliable.
2. **Local/before-push loop** — validate config, testbox, act-style local
   runs, gh-aw compile — the agent fixes CI without burning pushes.
3. **Scoped write surface** — rerun-from-failed yes; merge/deploy behind
   environment protection + OIDC + approval rules.
4. **The trust-layer job** — required checks, quarantine/auto-rerun for
   flakes, test selection, SHA-pinned actions, safe-outputs for agent
   writes. This is the part that matters more than any vendor feature.

Also in the space: `nektos/act` for local GHA iteration (Forgejo's runner
is built on it); Harness flaky-test tooling; Trunk merge queue for
agent-volume merge traffic. Not agent-native but adjacent: supply-chain
hardening (StepSecurity hard-runner) on any runner choice.
