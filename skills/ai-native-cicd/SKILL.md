---
name: ai-native-cicd
description: "Use when choosing, migrating, or optimizing CI/CD for a repo or org: GitHub Actions vs alternatives (GitLab/Jenkins/CircleCI/Semaphore/Buildkite/Forgejo), self-hosted runners on spare machines or ARC/scale sets, managed runner vendors (Blacksmith, Depot, Namespace, WarpBuild, Ubicloud, RunsOn, newer entrants), agent-native CI features (gh-aw, CircleCI MCP/Functions/Chunk, Semaphore sem-ai, Buildkite agentic primitives, GitLab Duo, Dagger), or answering whether the AI era changes the CI question. Ships the verified 2026-11 pricing table, the lazy-order decision ladder, self-hosted security rules, and the shelf-radar answer."
version: 1.0.0
author: Liz (lizliz.xyz)
license: MIT
---

# AI-native CI/CD selection

## Decision first — the lazy ladder

**"Which CI should we use?" is a fixed question with a laziness-ordered
answer. Start at rung 1 and stop as soon as a rung fits.**

1. **Private repo + a spare machine already exists → self-hosted runner.**
   Minutes cost drops to zero and the runner is one `config.sh` away. This is
   the single highest-leverage move in the whole space — see
   `references/self-hosted-playbook.md`. A persistent runner is fine for a
   private repo you control; go ephemeral/scale-set only when jobs come from
   people you don't fully trust or volume justifies it.
2. **No spare machine / don't want to own it → change one `runs-on:` line to
   a managed runner.** Blacksmith/Depot/Namespace/WarpBuild/Ubicloud all work
   this way; RunsOn puts ephemeral EC2 in *your* AWS account for a flat
   license. Pick on cache behavior and queue tails, not on the headline rate —
   see the pricing truth table below.
3. **Agent-heavy workflow (agents open PRs, agents fix CI) → evaluate the
   agent surface, not the runner.** CircleCI (hosted MCP + Chunk + Functions +
   Smarter Testing) and Semaphore (`sem-ai` CLI+MCP + `gha-to-semaphore`
   translator) are the two that built real agent control planes; GitHub's own
   answer is `gh-aw` agentic workflows compiled to Actions. See
   `references/agent-native-ci.md`. Source thread on keeping frontend CI under
   2 minutes for agent loops is archived at
   `references/2026-11-15-pontusab-frontend-ci-under-2-minutes.md` (+post
   images in the same folder).
4. **Full platform replacement — only for big teams or compliance.** GitLab
   (whole platform), Jenkins (self-owned, plugins), Tekton (K8s-native),
   Forgejo+Woodpecker (off-GitHub sovereignty). Migration cost eats the gains
   for anything smaller.

**The wrong question**: "which CI is best?" The right question: "which layer
is actually hurting — control plane, compute, or trust in agent output?"
Almost always it's compute (rung 1–2) or trust (rung 3), almost never the
control plane (rung 4).

## Market reality (verified 2026-11)

- **GitHub Actions is the de-facto standard and still gaining.** JetBrains
  State of CI/CD 2026 (598 orgs, multi-select): GHA **47%** (up from 41%),
  GitLab CI 32%, Jenkins 28%, Azure DevOps Server 15%, TeamCity 10%. JetBrains'
  second dataset puts Jenkins at 37% — treat ±5–9 pts as dataset noise.
- **Multi-tool is the norm, not the exception.** ~1/3 of orgs run 2+ CI tools.
  "Everyone eats GHA's shit" is wrong — big orgs mix, and that's fine.
- **Octoverse 2026 (Oct'25–Sep'26): Actions ran ~124M jobs/day (1,440/s, ≈45B
  jobs/yr). >40% of PRs were agent-started** (17% in March). CI is becoming
  the *trust layer* for agent-generated code — the strongest argument for
  investing in the pipeline instead of replacing it.
- **The managed-runner niche commoditized and started dying.** BuildJet shut
  down 2026-03-31 ("the gap we set out to fill has largely closed"); Earthly
  Cloud died 2025-07. Meanwhile new entrants keep appearing (Avrea, Latchkey,
  Vitko, Sengi) plus dedicated price-comparison sites (runnerbench, cibench,
  discountrunners). When a niche has its own price trackers, the winner is
  decided by details: cache, queue tails, BYOC.

## The core move: keep GHA's control plane, swap the compute

GitHub Actions = scheduler + YAML + checks API + secrets + marketplace. Almost
nobody's pain is in that layer. The pain is **minutes cost** (private repos),
**slow hardware**, **queue waits**, and **cache distance**. All four live in
the compute layer, which is replaceable with a one-line `runs-on:` change —
and reversible, which is the best kind of vendor relationship.

**Read the bill, not the rate card.** Three traps reproduced in the wild:

- **"2x faster" applies to CPU-bound steps, not your job.** A public-repo
  benchmark (VISP, 2026-11) measured ~2x on compile/tsc steps but only
  **1.3–1.4x whole-job** — the rest was waiting on containers and health
  checks no runner can shorten. Vendor "67% savings" headlines assume
  2x-everything.
- **Cache/storage is a separate meter.** Blacksmith's Docker layer cache /
  sticky disks: $0.50/GB/mo — one team paid $205/mo in cache storage,
  erasing the per-minute win. GitHub's own cache is 10 GB/repo free.
- **Queue tails exist on managed vendors.** Same benchmark: GitHub p99 queue
  11s vs Blacksmith p99 ~24min in one window. GitHub scheduling is
  boring-reliable; and since GitHub still schedules your jobs, a GHA outage
  holds up checks no matter whose runner you use.

### Pricing truth table (Linux x64, private repo, verified 2026-11)

| Runner | 2 vCPU/min | 4 vCPU/min | Free tier | Catch |
|---|---|---|---|---|
| GitHub-hosted | $0.006 | $0.012 | Public repos free; private draws from $12–$300/mo plan allowance | whole-minute rounding; new $-denominated allowance |
| Ubicloud | $0.00125 std / $0.002 prem | $0.0025/$0.004 | ~$2.50/mo credit (~1,250 min) | cheapest metered; open-source core |
| Namespace | $0.002 (4GB) / $0.004 (8GB) | $0.004/$0.008 | prepaid unit-minutes; $100 Team ≈ 25k min | cheap quote is the 4GB shape |
| WarpBuild | $0.004 managed / **$0.002 BYOC flat** | $0.008 | $10 signup credit | BYOC = your cloud, flat rate any size |
| Blacksmith | $0.004 (ARM $0.0025) | $0.008 | 3,000 min/mo | Docker cache/sticky disk billed per GB; queue tails reported |
| Depot | $0.006 | $0.012 | 2,000 min on $20/mo plan; $200/mo unlimited users | per-second billing; strong on Docker builds |
| RunsOn | ~$0.0009 (AWS spot) | ~$0.0014 | free for OSS/nonprofit | €300–1,800/yr license + your AWS bill; CloudFormation setup |
| Self-hosted | **$0** | **$0** | your machine | you own updates/security; free with GHA |

Larger GHA runners: Linux 4-core $0.012 → 96-core $0.252; macOS $0.062 std /
$0.077 for 12-core. Windows $0.010. ARM $0.005 (now free-tier eligible in
private repos, 2026-01). Full table + sources: `references/pricing.md`.

## Self-hosted runner doctrine

Self-hosted is **free with GitHub Actions** — you pay in maintenance, not
minutes. The rules that keep it from becoming a security incident:

1. **Private repos only.** A self-hosted runner on a public repo = anyone's
   PR runs code on your machine. On a private repo, the trust boundary is
   your contributor list — acceptable.
2. **Runner scope = repo first.** Register at repository level unless you
   deliberately want org sharing; use runner groups to fence which repos can
   reach which runners.
3. **Dedicated unprivileged user, no sudo, not in `docker` group** (docker
   group ≈ root). No ambient cloud credentials — use OIDC per job. Secrets
   live in GitHub secrets, injected per job, never on disk.
4. **Ephemeral is only real with a fresh machine.** `--ephemeral` on a
   persistent box still shares the filesystem; it's hygiene, not isolation.
   For one private repo + one owner, a persistent runner is honest — say so.
5. **Egress minimal**: GitHub + needed registries out; block cloud metadata
   endpoints and lateral movement.
6. **Scaling paths, in order of machinery**: single `actions/runner` service
   → **runner scale set client** (official, public preview 2026-02 —
   autoscaling without Kubernetes) → ARC scale sets on K8s (pod-per-job,
   scale-to-zero). Don't install K8s to run CI for one repo.
7. You own the image. Preinstall what jobs need; the runner binary
   auto-updates, your toolchain doesn't.

Full playbook (single-machine setup, scale sets, ARC, security checklist):
`references/self-hosted-playbook.md`.

## The AI-era judgment — don't build a new CI shape

The 2026 question isn't "which CI replaces GHA" — it's **"CI is the trust
layer for agent output; is yours doing that job?"** The evidence:

- >40% of GitHub PRs start with an agent. Volume of *unreviewed-by-author*
  code explodes; the pipeline is where it gets verified.
- Every vendor shipped the same product idea — **MCP server + agent-facing
  tools + autonomous fixing**: CircleCI (hosted MCP `mcp.circleci.com`, Chunk,
  Functions, Smarter Testing GA 2026-10), Semaphore (`sem-ai`), Buildkite
  (MCP + Model Providers + Preflight), GitLab (Duo fix-pipeline flows),
  GitHub itself (gh-aw: markdown→compiled Actions, read-only + firewall +
  safe-outputs, threat detection job).
- The new-form experiments mostly died (Earthly) or niched (Dagger as the
  "3rd-gen CI" overlay). The winners extended existing CI toward agents.

So the doctrine:

- **Don't invent a new CI form.** Compose: keep the workflow files you have,
  let an agent *maintain* them (the YAML-pain argument for switching
  platforms mostly evaporates when an agent edits the YAML), and put the
  effort into **gates**: required checks, flaky-test quarantine/auto-rerun,
  coverage-based test selection (CircleCI measured 60–90% skipped tests on
  feature branches), caching, and OIDC instead of long-lived deploy secrets.
- **CI's job description changed.** It now reviews agent work: stronger
  required checks, security scans, and a merge gate that treats
  agent-authored PRs as untrusted input — because that's what they are.
- **Agent surface checklist** when evaluating a platform: hosted MCP or
  agent-CLI? structured failure output (not raw logs)? rerun-from-failed and
  config-validation as tools? write ops behind scoped permissions?
- **Watch the cost shape of agent-driven CI.** More agent PRs → more runs →
  minutes math changes. That's one more reason rung 1 (self-hosted) moved to
  the top of the ladder.

## shelf-radar 结论

**私仓 + HK 空机 → self-hosted runner 是正解。** 仓库 `hanzili/shelf-radar`
为私仓，HK Lighthouse（43.161.239.146）已在跑公开服务、磁盘曾紧但算力
空闲；GHA hosted 坏了期间部署靠手动 receiver——HK 本地 runner 不但分钟
费归零，还把「CI 跑完 → 部署」变成同机操作，延迟和凭据暴露面都最小。

落地注意：repo 级 runner 不要 org 级；专用无 sudo 用户；不进 docker
组（如需 Docker 用 rootless）；工作目录定期清理（persistent runner 会
留上次 job 的文件）；`svc.sh` 装成 systemd 服务随机器重启；runner 二进制
自动更新但要盯住。GitHub→HK 连通性已验证（现在手动 deploy 就走 `hc exec
--on hk`）。详见 `references/self-hosted-playbook.md` 单机节。

## Expiry clause

This doctrine holds while GHA keeps the checks/secrets/marketplace monopoly
inside GitHub repos and while its hosted price stays ≥2–3× the managed
vendors' street rate. Re-review if: GitHub cuts private-repo prices to
managed-vendor levels; managed vendors consolidate/die further (post-BuildJet
shakeout isn't done); a vendor ships agent-PRs-write-to-prod pipelines
without the safe-output pattern becoming standard; or your repo goes public
(rung 1 becomes a security bug, revert to hosted). Prices verified 2026-11 —
re-check the rate card before quoting in a doc; the numbers move quarterly.
