# Self-hosted runner playbook

Three scales of self-hosting, in the order you should reach for them:
single machine → runner scale set client → ARC on Kubernetes.

## 1. Single machine (the shelf-radar shape)

One private repo, one spare box, minutes → $0.

```bash
# as a dedicated unprivileged user — create one first:
#   sudo useradd -r -m -s /bin/bash ghrunner && sudo -iu ghrunner
mkdir -p ~/actions-runner && cd ~/actions-runner
# latest version: https://github.com/actions/runner/releases
curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/vX.Y.Z/actions-runner-linux-x64-X.Y.Z.tar.gz
tar xzf runner.tar.gz

# registration token: repo → Settings → Actions → Runners → New self-hosted runner
# (or `gh api -X POST repos/OWNER/REPO/actions/runners/registration-token`)
./config.sh --url https://github.com/OWNER/REPO --token REGTOKEN \
    --labels self-hosted,linux,hk --name hk-lighthouse --unattended --replace
./run.sh                                  # foreground check first
```

Then install as a service so it survives reboots:

```bash
sudo ./svc.sh install ghrunner            # runs as the given user
sudo ./svc.sh start && sudo ./svc.sh status
```

Workflow side: `runs-on: [self-hosted, linux, hk]` — the labels you passed
are the router.

Decisions that matter:

- **Repo-level, not org-level.** One repo → register on the repo. Org
  runners let every repo in the org schedule code onto the box.
- **Persistent vs ephemeral.** `--ephemeral` deregisters after one job, but
  on the same long-lived machine the filesystem still carries over — it's
  hygiene, not isolation. For a private repo where every committer is you,
  a persistent runner is honest and simpler. Clean workspace between jobs
  (don't `actions/checkout` over a dirty tree; or `clean: true` in workflow).
- **The runner user is the job's user.** No sudo, not in `docker` group
  (docker group ≈ root — a job container can mount the host fs). If jobs
  need containers, prefer rootless docker/podman for that user.
- **No ambient credentials.** No cloud keys on the box; OIDC per job for
  cloud access. Secrets come from GitHub secrets, never stored on disk.
- **Egress.** Outbound to github.com + package registries only; block cloud
  metadata endpoints (169.254.169.254) and internal subnets the CI doesn't
  need.
- **You own the image.** Preinstall toolchains (node, python, docker-free
  build tools). The `runner` binary auto-updates; everything else is yours.
  Disk: runner workspaces accumulate — put `_work` where there's headroom
  and cron-clean old tool caches.
- **Never on a public repo.** Forked-PR jobs are arbitrary internet code on
  your machine, full stop. GitHub documents self-hosted runners as intended
  for private repos.

## 2. Runner scale set client — autoscaling without Kubernetes

Official GitHub preview (2026-02): a standalone Go module that implements
the ARC scale-set protocol — **job-queue-driven autoscaling on any infra**
(containers, VMs, bare metal), no K8s required. You own provisioning;
GitHub owns orchestration. Native multi-label support; explicitly supports
agentic workloads (Copilot coding agent).

Repo: github.com/actions/runner (scale-set client docs under
actions/actions-runner-controller). Use when: you need N ephemeral runners
across a few machines but don't run K8s.

## 3. ARC — Actions Runner Controller (Kubernetes)

The official controller (`actions/actions-runner-controller`, now under
the actions/ org with docs on docs.github.com). Runner **scale sets** via
Helm — pod-per-job, scale to zero, the real ephemeral shape.

```bash
helm install arc --namespace arc-systems --create-namespace \
    oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
helm install arc-runner-set --namespace arc-runners --create-namespace \
    --set githubConfigUrl="https://github.com/OWNER/REPO" \
    --set githubConfigSecret.github_token="${PAT_OR_APP}" \
    oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
# runs-on: arc-runner-set  (the INSTALLATION_NAME)
```

Hard-won rules from the official docs:

- **Runner pods in a different namespace than the controller**; secrets as
  K8s secret refs, never plaintext CLI args; **GitHub App auth for prod**,
  PAT only for a quick start.
- **Don't share the cluster with production workloads** — workflows are
  arbitrary code. Isolate the cluster or accept the blast radius.
- `containerMode.type: "kubernetes"` for container jobs; needs dynamic PVs
  (or lifecycle hooks for clusters without RWX). `kubernetes-novolume` +
  non-container jobs can give the runner pod K8s API privileges — read the
  warning twice before enabling.
- `maxRunners`/`minRunners` comment-free = unbounded scale-up, scale-to-0.
  **No scheduled scaling built in** — cron it yourself.
- HA: same scale-set name in two clusters, different runner groups —
  assignment is arbitrary (a race), not routable.
- One ARC install can host scale sets registered to different
  repos/orgs/enterprises; namespace per org for isolation.

Alternatives when you want ephemeral fleets without writing it yourself:
RunsOn (AWS, managed control plane) or philips-labs/terraform-aws-github-runner.

## Security checklist (any scale)

- [ ] private repo only; if public-PR jobs must run, keep them on hosted
      runners and gate self-hosted to `push` triggers
- [ ] repo-scoped runner (or runner groups pinning which repos reach it)
- [ ] dedicated user, no sudo, no docker group
- [ ] no ambient cloud creds — OIDC per workflow
- [ ] egress: GitHub + registries only; metadata endpoint blocked
- [ ] secrets only via GitHub secrets / environment protection rules
- [ ] pin third-party actions by SHA (GitHub & GitLab docs both recommend it)
- [ ] log retention for controller/runner (ARC: collect controller + listener
      + runner logs before production)
