---
name: ai-native-mihomo
description: "Use when setting up, migrating, or troubleshooting a headless Clash-family proxy stack (mihomo / Clash Meta core) on Linux in an AI-native way: headless core + REST API (external-controller) as the agent control surface, rootless systemd + TUN system-wide transparent proxy via setcap, agent self-heal of network failures, or deciding GUI-wrapper (FlClash, Clash Verge Rev) vs headless. Also covers the CN-network download doctrine (mirrors, human-phone relay) and API-driven proxy control (switch nodes, health"
version: 1.3.0
author: Liz (lizliz.xyz)
license: MIT
---

# AI-native mihomo proxy stack

## Triage first — one command, then doctrine

**"Is the proxy broken?" is a fixed question. Answer it with a fixed command,
not by re-deriving a path each session.**

```bash
mihomo-doctor          # exit 0 healthy / 1 degraded / 2 broken; --json, -q
```

It ships with this skill as `scripts/mihomo-doctor` (installed on the machine
by symlink into `~/.local/bin`), read-only, ~8 s, and reports in one pass: service + API + TUN,
current exit with its health history, **per-airport node liveness**, provider
subscription expiry/quota, three real end-to-end probes, and auto-select
flapping in the last hour. Symptom → verdict table, the few manual commands
worth keeping, and this machine's current airport inventory: `TRIAGE.md` next
to it.

The reading that matters most: **per-airport liveness**. One airport at `0/N
alive` while another is healthy is not a mihomo bug and not a reason to debug
the core — it is a dead airport, i.e. a business decision (renew, replace, or
drop it from the candidate list). "Slow everywhere but every probe returns
200" is bandwidth, not failure. Only `code=000`, timeouts, or `alive=false`
mean down.

Three measurement traps that have already produced wrong answers here:

- **Never judge node/airport liveness by DNS.** With TUN + `fake-ip`, *every*
domain resolves to `198.18.x.x`; and `dig` is not installed on this machine —
its empty output is not `NXDOMAIN`. Liveness comes from `/proxies` `alive` +
`history` only.
- **Never use `GET /group/<g>/delay` as a probe** (it clears the selection and
  tests every member) — single nodes: `GET /proxies/<name>/delay`.
- **Provider proxies may be absent from the `/proxies` map** while still working;
  they show up under `/providers/proxies/<name>` and can be the current `now`
  of a selector. Look there before declaring a node missing.

If the doctor's verdict is clear, stop investigating and act on it. Doctrine
below is for building or changing the stack, not for re-diagnosing an exit
that already has a reading.

## The pattern

Every GUI clash client (FlClash, Clash Verge Rev, ...) is a thin shell over the
**mihomo core**. The AI-native move is to drop the shell and keep the core,
because the core already exposes everything a GUI does as a **REST API**
(`external-controller`). The GUI is a disposable human convenience; the API is
the contract agents build on.

```
airport profile (yaml) ──security patch──▶ config.yaml ◀── mihomo binary (headless)
                                                │                │  (setcap: TUN without root)
                                    systemd --user service   REST API 127.0.0.1:9090
                                                │                │
                                     TUN gvisor + auto-route   agent: curl / jq / MCP
```

Properties that matter:
- **Rootless**: `systemd --user` + file capabilities. No root-owned configs, so
  agents can manage everything without sudo.
- **Declarative**: one yaml = whole state. Reproduce = copy 3 files.
- **Observable**: every dial, rule match, and delay is one GET away.

## Complexity doctrine — native config first

The default answer to "mihomo keeps picking the wrong exit" is a **config
change**, not a program. Escalate only as far as the problem forces you:

1. **Native config**: a `select` group you pin by API; `url-test` nominally
   "fastest wins"; `fallback` nominally "first healthy in list order";
   `load-balance` for spread. These are *intended* semantics, not guarantees
   — actual failover behaviour is version- and nesting-dependent (see Group
   behaviour). Most "wrong node" complaints are a group type that cannot
   express the rule you actually want.
2. **Minimal selector** (a ~100-line loop + `systemd` timer): **only** when the
   requirement is a *strict region hierarchy* — an ordered priority between
   regions that no native group type expresses. That is the entire reason the
   loop is allowed to exist.
3. **Manager / daemon / file-watcher**: only after a **reproduced** failure that
   (2) cannot handle, and only for that specific gap.

Every added moving part must name the already-reproduced failure it closes.
"It would be cleaner / more general / more future-proof" is not a reason. A
proxy exit picker for a few dozen nodes is not a system that needs an
architecture; the smaller the surface, the fewer ways it breaks at 3 a.m. and
the less there is to read when it does.

## Security doctrine

Assume every airport-exported config ships the same landmines until proven
otherwise. Patch on ingestion, before first start:

1. `external-controller: 0.0.0.0:9090` → `127.0.0.1:9090`. With the default
   empty secret this is a LAN-open control API — anyone on the Wi-Fi owns your
   proxy.
2. `secret: ''` → `openssl rand -hex 12`. The secret is not a secret from the
   local agent (it reads the same config file); it is a fence against the LAN.
3. Scan for `allow-lan: true` — keep only if LAN sharing is actually wanted.

## Download doctrine (CN networks)

A ladder; try in order, never grind a rung:

1. **Direct GitHub**: often <50 KB/s. Budget-check first
   (`curl -r 0-1M -o /dev/null -w '%{speed_download}'`), don't commit blind.
2. **Mirror prefix** (`https://ghfast.top/<github-url>`): ~250 KB/s but flaky —
   connections reset mid-stream. Always pair with `curl -C -` resume in a retry
   loop.
3. **Human-phone relay**: the phone downloads in seconds on cellular, then
   LocalSend/AirDrop to the desktop. For anything >20 MB or after two failed
   mirror attempts, hand the URL to the human and move on. The phone is the
   fastest network interface in the room.

## Privilege doctrine

The agent must never touch a password prompt — `sudo` interactively is
unreachable by design, and that is a feature. Ladder:

1. **Design root away**: `systemd --user` service +
   `setcap cap_net_admin,cap_net_bind_service=ep <binary>` gives TUN (and port
   53 bind) without root. Everything stays agent-editable.
2. **One-line human-in-the-loop**: when a privileged one-off is unavoidable,
   run `pkexec <cmd>` — a native auth dialog pops on the user's desktop; they
   type the password there, the agent orchestrates everything around it.
3. `setcap` is lost whenever the binary is replaced (update/reinstall). Re-check
   with `getcap` after every binary change.

## API cookbook

All requests: `curl -H "Authorization: Bearer $SECRET" http://127.0.0.1:9090/...`
(`$SECRET` lives in the config file). Machine-agnostic.

```bash
# self-heal loop: probe → test → switch → re-probe
curl -s -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204   # 204 = alive
curl -s "$API/proxies" | jq '.proxies | to_entries[] | select(.value.now) | {k:.key, now:.value.now}'
curl -s "$API/group/$GROUP/delay?url=https%3A%2F%2Fwww.gstatic.com%2Fgenerate_204&timeout=5000" | jq
curl -s -X PUT "$API/proxies/$GROUP" -d '{"name":"<node>"}'
curl -s -X PATCH "$API/configs" -d '{"mode":"rule|global|direct"}'
curl -s -X PUT "$API/configs?force=true" \
  -H 'Content-Type: application/json' \
  -d '{"path":"/absolute/path/to/config.yaml"}'   # reload config from disk
# an EMPTY body returns 400 Body invalid — the absolute path is required.
# Path must be inside the core's `-d` dir, else set SAFE_PATHS (colon-separated)
# or keep the candidate in the data dir.
# Clear a stuck auto-group selection (store-selected restoring a dead node):
curl -s -X DELETE "$API/proxies/$GROUP"           # Selector type excluded
# NOTE: GET /group/<name>/delay tests EVERY member and clears the auto-group's
# fixed selection — never use it as a health probe inside a selector loop.
curl -s -X PUT "$API/providers/proxies/$NAME"     # refresh a subscription provider
curl -s "$API/connections" | jq '.connections | length'   # null = inbound dead
curl -s -X POST "$API/restart"
journalctl --user -u mihomo -f                    # logs
```

## Airport-level failover — "one subscription dies, switch to the next"

Node-level health is the wrong unit for this question. A whole airport dies at
once (2026-10-20: the main line's 46 inline nodes were all `alive=false`,
`delay=0`, while the backup airport was fine). So the selector also needs an
**ordered airport list** — `provider_order` in the policy SOT, sources `""` for
inline nodes and the `proxy-provider` name otherwise — and it must outrank
region priority: the second airport's healthy node beats the first airport's
best dead one.

**Probe the exit end-to-end; do not trust the health cache.** A 204 through the
local proxy port is the only reading that tracks what the user feels. Health
history lags by up to the group/provider interval (60 s here) plus the
selector's freshness window — exactly the "it's broken for two minutes before
anything happens" complaint. Measured here with a 10 s timer: pointing the exit
at a dead node fails over in ~10 s; a history-only check lets the same failure
sit for 1–2 min.

Three details that make it stable instead of thrashy:

- **Slow ≠ dead.** If the end-to-end probe fails but fresh history still shows
  the node answering with delay in range, treat it as slow: a switch is still
  allowed, but only after the cooldown. Otherwise one congested minute becomes a
  switching storm.
- **Avoid list.** A node that just failed goes on a ~10 min avoid list so the
  selector cannot rotate back into the same bad node next run.
- **Airport order belongs in policy, not in the script.** Hard-coded
  `PRIORITY` / `PROVIDER_ORDER` constants in a several-hundred-line selector
  drift from `policy.yaml` within weeks; emit them into the generated manifest
  and have the selector read them.

And the honest limit: failover only moves traffic to a surviving airport. If
only one airport is alive and that one is congested, the selector can only pick
the least-bad node inside it — the bottleneck is airport quality, not switching
logic.

## Node strategy — region priority is a different axis from latency

Two independent dimensions, constantly confused:

- **Region priority** is a *policy*: which country's exit you want, in order. A
  typical shape is `美国 > 日本 > 新加坡 > 台湾 > 其他 > 香港`, with the home
  region **last as the backstop**. The exact order belongs to the user — get it
  from the user's own words or ask; do not invent it, and do not assume a
  default just because "overseas first, home last" is a common shape.
- **Latency** is a *measurement*: how fast the exit answers right now.

`url-test` only sees the second. If the user says "prefer overseas, fall back
home", that is priority, and a pure `url-test` will happily pin a 55 ms local
node forever. Keep priority in **one** place and make any selector read *that*
— a second hard-coded copy always drifts. Concretely: one small policy file
next to the config (e.g. `policy.yaml` with an ordered `regions:` list plus an
optional `cheap_suffix:` pattern), loaded at runtime; if no policy file exists
yet, the config's group order + a comment is the SOT until one is created.
Never split the order across script constants *and* docs. The SOT also owns
one editable **alias/classification table** (Chinese/English names, flags,
abbreviations → region): subscriptions vary and some nodes carry no marker.
Classify every imported node exactly once, report per-region **plus
unclassified** counts, and hold unclassified nodes out of active groups until
policy places them — never silently dump unknowns into “其他” or the backstop.

Within a region the same logic recurs one level down:

- **Cheaper cost tier first.** Airports label tiers in the node name (this
  machine's subscription uses an `N倍消耗` suffix); prefer the cheap tier inside
  the chosen region.
- **Same region + same tier → do not switch.** A few tens of ms between peers
  is noise; flapping costs connections and buys nothing.
- **Current exit dead → degrade immediately**, cooldown does not apply (see
  Airport-level failover for how "dead" is decided).
- **Higher-priority region or cheaper tier recovered → switch back, but obey a
  cooldown** (~5 min), so an oscillating node does not ping-pong you.

## Group behaviour: measure it, don't trust the type name

Group semantics are the least-documented, most surprising part of mihomo, and
they shift between versions. Treat what follows as **reproduced on v1.19.30 —
re-verify with the API before relying on it**, not as permanent truth:

- **A `url-test` sub-group can report `alive: true` even when every member
  fails.** A parent `fallback` then sees "member healthy", keeps it selected,
  and the chain black-holes. Reproduced: a deliberately-dead `url-test` group
  reported `alive=true`, and its parent `fallback` stayed pinned to it.
  **Consequence: never nest a `url-test` group inside `fallback`.**
- **A flat `fallback` of real leaf nodes did *not* switch** in one
  environment on v1.19.30, even with the current selection dead and its
  members correctly marked `alive: false`. Single-environment observation, not
  a universal claim — but enough that "it's a `fallback`, it will self-heal"
  is **not** a safe promise.
- **`profile.store-selected: true` persists the chosen node — including a dead
  one — across reloads and restarts.** A reload can look like it "restored the
  broken node for no reason". Clear with `DELETE /proxies/<group>` (works for
  every group type except `Selector`) or switch explicitly.
- **`GET /group/<name>/delay` clears the auto-group's fixed selection** (per
  API docs) while testing every member — so probing with it *resets* the very
  selection you are trying to observe. Probe single nodes with
  `GET /proxies/<name>/delay` instead.

**The honest reading**: how a group reacts to losing all members is
version- and nesting-dependent. Before promising self-healing, reproduce it —
kill one member in config, watch `/proxies` for `now` and `alive`, and see
whether `now` actually moves. Do not infer behaviour from the group's name.

## Minimal selector — the contract

If a strict region hierarchy forces a loop (see Complexity doctrine), this is
the whole contract. Roughly 100 lines; do not build a framework around it.

**Read**: one `GET /proxies` per run — never `GET /group/<g>/delay` in the
loop (it re-tests every member *and* clears the selection). A node is healthy
when `alive == true` **and** `history[-1].delay` is in range **and**
`history[-1].time` is fresh
(RFC3339, may carry nanoseconds — truncate to microseconds before parsing). A
node removed from every `url-test` group keeps `alive: true` with frozen
history, so **delay alone will treat a corpse as healthy**; the timestamp is
the part that catches it. Treat ~2–3× the health interval as "fresh".

**Decide**:

1. Current exit: if its record is stale, **probe it yourself**
   (`GET /proxies/<name>/delay?...`). Never let a stale cache declare the
   current exit healthy and freeze you there.
2. Candidates: sort by `(region rank, cost tier)` and take the first healthy
   one.
3. No-data / fresh-boot fallback is a **recovery-first ladder**, not an
   exhaustive scan: probe current first; if dead or no data, probe **one
   best cheap candidate per region in priority order** — so every region
   including the backstop is reachable within `regions × timeout`, not
   `nodes × timeout`. If all representatives fail, a second round-robin /
   broadened sweep over the remaining candidates runs under the same
   wall-clock budget, so a healthy second node in an already-tried region
   is not missed. After connectivity returns, later runs (plus mihomo's
   own health data) upgrade to a higher-priority/cheaper node; do not
   duplicate probes within one run. No fixed global cap (a `[:6]` slice silently
   excludes exactly the backstop you need) and no duplicate full scans.
   Bound the run with a wall-clock budget and the service's
   `TimeoutStartSec`; `OnUnitInactiveSec` + lock prevents overlap.
4. Current dead → switch now. Higher priority / cheaper tier recovered → switch
   after cooldown. Same region + same tier → hold.

**Write**: the switch is `PUT /proxies/<group>` with `{"name":"<node>"}`.
Persist `last_switch` with an **atomic write** (`tmp` + `os.replace`) so a crash
mid-write cannot corrupt state.

**Run**: a `systemd --user` timer, first run a few seconds after boot
(`OnActiveSec=15s`), then `OnUnitInactiveSec=60s` (not `OnCalendar` — the next
run starts 60 s *after the previous finished*, so a slow boot-scan can never
pile up). Guard with a lock file; a second instance exits quietly. Prefer one
explicit timer unit over `ExecStartPost` hooks: a post hook that sleeps or
does network work blocks service readiness (and its failure can mark the
service failed); a hook that merely schedules an async transient timer
returns fast but adds transient-unit lifecycle/observability complexity. If a
hook is used at all, prefix with `-` and keep it trivial.
Emit one line per run in a fixed shape — `OK <current>`,
`HOLD <current> — <reason>`, `SWITCH <from> -> <to>`, `ERROR <why>` — so
`journalctl` is readable at a glance.

## Ingesting a new profile (yaml / json / subscription)

Identify the **schema first**, and never let the incoming file dictate local
policy.

| Shape | How to tell | Action |
|---|---|---|
| full config | mapping with inline `proxies` (plus `rules`/`dns`/`tun`) | **extract `proxies` only** |
| provider-only | mapping with `proxy-providers:` and **no** inline `proxies` | two legitimate modes — (a) **preserve**: keep the `proxy-providers:` blocks for ongoing native refresh and build groups with `use:`/provider filters where suitable; (b) **materialize**: resolve provider content into an inline snapshot when strict merging/selector membership requires it. Tradeoff: (a) stays renewable, (b) goes stale. Never silently flatten a renewable provider into a stale snapshot; unresolvable → **reject**. A provider update (`PUT /providers/proxies/<name>`) is not a full config replacement |
| proxy list | top-level array of objects with `name` | take the nodes |
| subscription URL | a URL, not a file | fetch it, then re-identify (see response checklist below) |
| anything else | no usable `proxies` key, HTML/login page, scalar | **reject loudly** |

Subscription responses: check the first non-whitespace bytes before parsing —
`<` (HTML/login/expired page) → reject; if it is not YAML, try one base64
decode and re-identify, else reject; YAML that parses but yields zero nodes, or
a truncated download (size mismatch / parse error) → reject, never promote an
empty list.

Rules that matter:

- **A full config must not silently rewrite local DNS / TUN / rules /
  security.** You already have a known-good local policy shell (controller on
  localhost, a real secret, TUN settings, rule set). Keep it, pull nodes out of
  the new file, merge them in. A profile that replaces your `dns:` block or
  flips `external-controller` back to `0.0.0.0` is the classic way to lose the
  machine.
- **JSON is not a mihomo-loadable config.** Parse it structurally, map it onto
  the same node model, and only then serialise. Never hand a `.json` to the
  core.
- **Reject, don't degrade.** An unrecognised schema must produce a loud error.
  Quietly emitting an empty `proxies:` list is how a working proxy becomes a
  dead one with nobody noticing.
- **Name collisions must not silently overwrite.** Same name + same definition
  → dedupe, so re-running is idempotent and nodes never accumulate. Same name +
  different definition → rename with a stable, region-prefix-preserving suffix
  (`<name> (2)`, keeping the region prefix so classification still matches)
  and record the conflict, or reject listing the conflict. Sort
  merged output stably (e.g. by name), hash inputs, and skip the write when the
  result is unchanged — re-running the same input must be a no-op. Full
  staged procedure (candidate → validate → atomic promote → reload →
  post-check → rollback): RUNBOOK §10.
- **Candidates, sources and backups hold live credentials.** Private dir
  (`0700`), files `0600`, `umask 077` for every write; clean up temp files on
  success *and* failure; strict git-ignore — and still treat local git as
  accidentally pushable. Adjacent-to-live candidate (for `SAFE_PATHS`) is
  fine, but never world-readable.
- **Filtering airport "info" pseudo-nodes** (an entry named like a website or a
  traffic counter) is a judgement call: keep it as an **editable list of
  patterns with evidence**, not a heuristic buried in code. Exclude, and log
  what matched.
- **`client-fingerprint: random` is not a global find-and-replace.** Only the
  class of nodes where you reproduced `REALITY authentication failed` **and**
  A/B demonstrated recovery after changing the fingerprint is a normalisation
  candidate — for those REALITY/Vision nodes, `chrome` tested good. Leave every
  other protocol's vendor value alone; a blanket rewrite can break nodes that
  were fine.

## TUN debugging playbook

TUN blackout = one broken layer. Isolate with decisive tests, top to bottom;
each test has a binary reading:

| Layer | Decisive test | Reading |
|---|---|---|
| DNS hijack | `getent hosts google.com` | fake-ip `198.18.x.x` = hijack working |
| Inbound to core | curl any site, then `GET /connections` | `null` = traffic never reaches core → stack problem |
| Hijack routes | `ip rule show` **and** `ip route show table 2022` | a policy rule routed to a dedicated table (this machine: `2022`) **and** `default via <tun-ip> dev Meta` inside it |
| Outbound escape | `curl --interface <phys-iface> https://223.5.5.5` | works = bound sockets escape TUN rules; core must bind its outbounds (`auto-detect-interface: true` / top-level `interface-name`) |

Known fixes, in order of likelihood:
- `tun.stack: mixed` dead on some setups → `gvisor` (pure userspace, always
  works; restart after change).
- Core outbound dials time out while direct rules work → outbound looping into
  the TUN; ensure interface binding (see escape row above).
- Node flapping (some `000`s succeed on retry) → auto-select mid
  health-check culling; retry once before digging.

Known-harmless log noise: UDP QUIC dials `can't resolve ip: couldn't find ip`
(fake-ip + UDP relay limitation; apps fall back to TCP); provider health-check
"use HTTPS" warning.

Two traps when reading this layer:

- **`auto-route` installs a policy rule + a dedicated table, not a default in
  the main table.** `ip route` alone will look like TUN never took over. Check
  `ip rule show` (this machine: a rule sending traffic to table `2022`) and
  then `ip route show table 2022`; confirm the device (`Meta`) is up, and
  finish with a plain `curl` (no `-x`) hitting 204.
- **Do not read a bare `5353` grep as a port conflict.** Check *which* socket:
  mihomo's own DNS listener binds its configured address, while mDNS/Avahi and
  Chrome bind the multicast address `224.0.0.251:5353`. Seeing both is normal.
  `device or resource busy` on a **hot reload** is likewise usually the previous
  TUN not yet released — re-check after a clean restart before calling it a
  real failure.

## Why the GUIs are disposable — and why full delegation wins

**A GUI client is a renderer over the same REST API.** Switch node, health
check, mode toggle, reload, subscription update — the operational surface an
agent needs is all API. That is not a literal 1:1 with every GUI widget
(rule-order editing UX, profile-switch conveniences and subscription-refresh
semantics differ between clients), but nothing an agent depends on is
gui-only. The GUI is a *rendering preference*, not an interface anyone needs.

Its costs, meanwhile, compound on exactly the machines agents run on:

- **Bundled-library rot**: AppImage/Electron shells carry legacy libstdc++ and
  friends that break against rolling-release mesa (the EGL-crash class).
- **Core lag**: GUIs ship stale cores; the headless path updates the core
  alone, in one file swap.
- **Opaque state**: profiles live in app-private SQLite/prefs stores no agent
  can safely mutate. Headless mihomo's entire state is one yaml.

**Delegation is the modern control loop.** The agent is simultaneously the
first to *feel* a proxy failure (its own fetches time out before a human
notices) and the fastest to act: probe → delay-test → switch → re-probe,
seconds, zero human context switch. A GUI inserts a human into a loop that no
longer needs one. The human exits the loop entirely, remaining only for
privilege one-offs (the `pkexec` dialog) and business decisions (which airport
to pay for). The dashboard's last real job — "is it working?" — is one 204
probe.

**And the product question dissolves.** Wrappers over the API already exist
(`mihomot` with its agent-facing `/skill.md`, `mcp-server-clash-verge`,
`mihomo-mcp`, `mihomo-rs`); the API is the real surface and they are conveni-
ences over it. Any new wrapper has a hard ceiling — a ~200-line disposable
shim. The scaffold's value *is* its disposability, so build-vs-buy is not a
real decision. The stack to beat is `mihomo + REST API`, and nothing on the
market beats it by existing.

**Expiry clause**: this doctrine holds while mihomo stays a stable, actively
maintained core — it ships monthly+, patches CVEs proactively, and has been
the de-facto standard since the original Clash core was archived (2023-11);
its risks are category-level (bus factor, GFW arms race), not fixable by
switching cores. Re-review the whole setup if releases stall for months, the
API surface breaks without deprecation (it has had breaking tweaks, e.g.
`/proxies` behavior changes), or the protocol landscape resets. Keeping one
GUI installed as a cold spare is fine; architect as if it does not exist.

## Review framework — four questions before you ship

Cheap to ask, expensive to skip. Run them over any proxy change:

- **Robust** — what happens when the input is bad (half-copied file, unknown
  schema, dead node), and when the component itself dies? The failure mode must
  be "keep the previous good state", never "lose the network".
- **Scalable** — is the work per-input or per-node, and what does it cost? A
  few dozen nodes need no engineering; `O(n)` is plenty. But **count the
  probes**: 46 nodes on a 60 s interval is `46 × 1440 ≈ 66 240` health probes a
  day, and every one of them leaves the machine. Let mihomo's own groups own
  the per-node health loop — do not add a second prober that re-measures
  everything.
- **Editable / single source of truth** — can the *policy* change without
  touching code, and does it live in exactly one place? Policy split across a
  config comment, script constants and docs is three policies, and they will
  disagree. Decouple strategy from node data: nodes churn weekly, policy barely
  moves.
- **Observable / reversible** — at 3 a.m., what do you read? The surfaces are
  `journalctl -u mihomo`, `/proxies` and `/connections`, plus a small structured
  state file (last success, input hashes, node/region counts, last error) —
  credential-free, and with the last known-good config one command away.
- **Auditable / recoverable / secure** — log input hashes + node counts per
  run; every promotion keeps a timestamped backup with a one-command rollback;
  never paste secrets (secret, UUIDs, keys, hostnames, exit IPs) into docs or
  logs.

## Verification & reporting discipline

Proxy work fails silently, so the bar for "it works" is a reading, not a
feeling:

- **Back up before injecting a fault**, and state the blast radius *before*
  running it, not after.
- **Degradation must be observed end-to-end with no human in the loop.** A
  switch you triggered by hand proves the switch call, not the automation.
- **If you bypassed a safety mechanism to get a result faster, say so.**
  Deleting the cooldown state file to reach the "recovery" case is legitimate —
  calling it a natural recovery is not. Report it as "cooldown bypassed
  manually".
- **Separate observed / inferred / unverified.** "The API returned 204" is
  observed; "traffic now uses the new node" is inferred unless you probed it;
  "the config is loaded" is unverified until a request travels through the
  running core.
- **Do not measure with stale logs.** Narrow the `journalctl --since` window to
  the incident, and re-derive counts you took before a restart — a running
  counter and a windowed count look identical and mean different things.
- **Never paste secrets**: `secret:`, UUIDs, REALITY `public-key`/`short-id`,
  subscription hostnames, or exit IPs. Reference them, don't quote them.

## This machine's instantiation

Concrete instance of the pattern (paths/secret are machine-specific):

| Piece | Value |
|---|---|
| Binary | `~/.local/bin/mihomo` (official v1.19.30, caps via setcap) |
| Config | `~/.config/mihomo/config.yaml` (airport profile + patches, `tun.stack: gvisor`) |
| Geo data | `~/.config/mihomo/{GeoIP,GeoSite}.dat` (reused from FlClash data dir) |
| Service | `~/.config/systemd/user/mihomo.service` → `systemctl --user ...` |
| Diagnostics | `scripts/mihomo-doctor` + `TRIAGE.md` (both in this skill; `~/.local/bin/mihomo-doctor` symlinks to the script) |
| Selector | `mihomo-auto-select.timer` (10 s) + `scripts/auto-select.py`, policy in `policy.yaml` |
| Providers | `proxy-provider` 绿树 lvshu = primary (hourly refresh); inline 快车 gfw2500 = fallback only (no subscription URL, 46/46 dead as of 2026-10-20) |
| API | `http://127.0.0.1:9090`, secret: real value in `~/.config/mihomo/config.yaml` (never copy secrets into docs) |
| Proxy port | `127.0.0.1:7890` (mixed, `allow-lan: true` for LAN devices) |
| Legacy GUI | FlClash AppImage extracted at `~/Downloads/squashfs-root`; launch with `LD_LIBRARY_PATH=lib:syslibs` (bundled legacy libstdc++ breaks EGL on rolling mesa — bypass bundled libs, symlink only `libkeybinder-3.0.so.0`) |

Machine tooling shipped with this skill (same directory):

| Path | What |
|---|---|
| `scripts/mihomo-doctor` | one-command triage (see Triage first) |
| `scripts/auto-select.py` | exit selector: airport tier → region priority, fallback, avoid list |
| `scripts/mihomo_manager.py` | profile ingestion / merge / validate / atomic promote / rollback |
| `policy.yaml` | policy SOT for this machine (region order, airport order, junk patterns, selector knobs) |
| `units/`, `tests/`, `references/mihomo-manager.md` | systemd units, offline tests, manager docs |

Full reproduction steps with per-step completion criteria: [RUNBOOK.md](RUNBOOK.md).
