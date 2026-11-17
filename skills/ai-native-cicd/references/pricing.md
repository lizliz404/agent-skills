# Pricing & market data — verified 2026-11

All rates are per-minute, Linux x64, private repos, read 2026-11-09..16.
Re-verify before quoting; this market moves quarterly. Sources listed at
the bottom.

## GitHub-hosted

- Included compute is now a **dollar allowance**, not minutes: Free $12,
  Pro $18, Team $18, Enterprise Cloud $300/mo. $300 ≈ 50,000 std Linux min.
- Rates: Linux slim 1-core $0.002 · Linux 2-core $0.006 · Linux ARM $0.005 ·
  Windows 2-core $0.010 · Windows ARM $0.010 · macOS $0.062.
- Larger runners (Team/Ent only): Linux 4c $0.012 / 8c $0.022 / 16c $0.042 /
  32c $0.082 / 64c $0.162 / 96c $0.252; Windows 4c $0.022 → 96c $0.552;
  macOS 12c $0.077.
- Jobs round up to whole minutes. Effective multipliers on the allowance
  are now price ratios (Windows ≈1.67×, macOS ≈10.3× — measured, not the
  old 2×/10×).
- Cache 10 GB/repo free; artifact storage 500MB–50GB by plan.
- 2026-01: arm64 standard runners in private repos, free-tier eligible.
- 2026-10: multi-cloud compute — eligible Linux jobs may run on AWS too;
  update IP allowlists (`GET /meta`, `actions` array).

## Managed runners (the `runs-on:` swap)

| Vendor | 2 vCPU | 4 vCPU | Free / included | Notes |
|---|---|---|---|---|
| Blacksmith | $0.004 (ARM $0.0025) | $0.008 (ARM $0.005) | 3,000 min/mo | colocated cache; Docker layer cache & sticky disks $0.50/GB/mo billed separately; migration wizard writes the PR |
| Depot | $0.006 | $0.012 | $20/mo plan w/ 2,000 min (1 user); $200/mo w/ 20,000 (unlim users) | per-second billing; Docker/image builds are their home turf |
| Namespace | $0.002 (4GB) / $0.004 (8GB) | $0.004 (8GB) / $0.008 (16GB) | $100/mo Team ≈ 25,000 unit-min | unit-minutes; cheap headline is the 4GB shape; also does mac runners, cache volumes, ephemeral envs |
| WarpBuild | $0.004 | $0.008 | $10 signup credit | **BYOC $0.002 flat any size** — runners in your cloud account |
| Ubicloud | $0.00125 std / $0.002 prem | $0.0025/$0.004 | ~$2.50/mo credit (~1,250 std min) | cheapest metered; open-source IaaS core |
| RunsOn | no per-min; ~$0.0009–0.0014 (AWS spot 2–4 vCPU us-east-1) | — | free for OSS/nonprofit/edu | license €300/yr <50k jobs/mo, €900 <200k, €1,800 <500k; ephemeral EC2 in your VPC; CloudFormation; per-second AWS billing |
| New entrants | Avrea $0.004/3k min · Latchkey $0.0025/2–6k min · Vitko $0.002/2k min per-second · Sengi | — | — | niche commoditizing; price trackers: runnerbench.com, cibench.com, discountrunners.io |
| BuildJet | — | — | — | **dead 2026-03-31**; exit quote: "the gap we set out to fill has largely closed" |

### Real-world readings (not rate cards)

- VISP benchmark (public repo, 2026-11): Blacksmith ~2× on CPU-bound steps
  (tsc 60s→27s, Vite 33s→16s) but **1.3–1.4× whole-job** — a third of the
  pipeline is waiting on containers/health checks. GitHub queue p99 11s vs
  Blacksmith p99 1453s (one in five jobs waited >1min). Stayed anyway —
  3,000-min free tier covers their volume; the switch is one line and
  reversible.
- howardjohn (agentgateway): E2E 10–11min → 2–3min after moving to
  Blacksmith; sponsored, disclosed.
- Full Stack House (2026-10): jobs 7–11min → 3–8min; but **cache storage
  billed $205/mo** made September cost 25% *more* than the GitHub baseline —
  the sticker rate was not the bill.
- Honest heuristic: compute-bound pipelines ≈1.5–2× real speedup; pipelines
  that wait on services ≈1.2×. Fix the waiting first if that dominates.

## Buildkite (the hybrid)

- $30/active user/mo Pro; self-hosted agents: 10 included then $3.50/agent/mo.
- Hosted agents: Linux $0.004/vCPU-min (2vCPU small = $0.008/min), Mac
  $0.02/vCPU-min, Windows $0.008/vCPU-min. Free plan: 5 users, 2,000 Linux
  vCPU-min/mo.
- The pitch that aged well: control plane managed, compute yours — the same
  "keep control, swap compute" shape, at platform level.

## Market share (JetBrains State of CI/CD 2026)

- Org adoption, multi-select, n=598 (576 CI users): **GHA 47%** (was 41%),
  GitLab CI 32%, Jenkins 28%, Azure DevOps Server 15%, TeamCity 10%,
  AWS CodePipeline/CodeBuild 7%, Bitbucket 6%.
- Multi-tool is normal: earlier wave showed 32% of orgs use 2 tools, 9% use 3+.
- Personal projects: GHA far ahead (~39–62% depending on dataset).
- Caveat: JetBrains' two 2026 datasets disagree (Jenkins 28% vs 37%);
  ±5–9pts dataset noise. No census exists; every source counts a different
  unit (orgs vs individuals vs platform events).

## Volume & agent share (GitHub Octoverse 2026, Oct'25–Sep'26)

- Actions: **1,440 jobs/sec = ~124M/day ≈ 45B jobs/yr**, 3× last year.
- **>40% of PRs were agent-started in September** (17% in March); ~110M
  agent-started PRs that month alone; they merge slightly faster now.
- Repos with an agent config file: ~8× the commits of new repos without.
- Copilot MAU: 55% use agentic features; Copilot cloud agent +230% YoY.

## Sources

- github.blog Octoverse 2026; GitHub changelog (multi-cloud 2026-10-28,
  arm64 2026-01-29, scale-set client 2026-02-05); docs.github.com billing &
  runner pricing
- jetbrains.com/pages/state-of-cicd2026; safeguard.sh methodology breakdown
- Pricing: avrea.com/github-actions-runner-pricing (checked 2026-11-11),
  latchkey.dev/learn/runners (2026-09-20), cibench.com/prices (2026-10-24),
  runs-on.com/alternatives (2026-10-03), spillway.sh
- Field reports: visp-stream.com Blacksmith benchmark (2026-11-08),
  fullstack.house (2026-10-02), blog.howardjohn.info (2026-04),
  lighthouselocal.ai
- buildjet.com shutdown notice; earthly.dev shutdown post; EarthBuild fork
- circleci.com (Functions 2026-11-04, Smarter Testing GA 2026-10-13,
  hosted MCP changelog 2026-09-14); docs.semaphore.io sem-ai;
  github.com/github/gh-aw; buildkite.com pricing & agentic-workflows;
  about.gitlab.com Duo Agent Platform; dagger.io + Dagger for GitLab
  (2026-11-10)
