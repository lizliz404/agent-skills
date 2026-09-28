---
name: ai-native-mihomo
description: >-
  Use when setting up, migrating, or troubleshooting a headless Clash-family
  proxy stack (mihomo / Clash Meta core) on Linux or macOS in an AI-native way:
  headless core + REST API (external-controller) as the agent control surface,
  rootless service (systemd on Linux, launchd on macOS) + system-wide
  transparent proxy via TUN, agent self-heal of network failures, or deciding
  GUI-wrapper (FlClash, Clash Verge Rev) vs headless vs coexistence. Also covers
  the CN-network download doctrine (mirrors, human-phone relay) and API-driven
  proxy control (switch nodes, health checks, reload, subscriptions),
  region-priority exit selection, and safely ingesting a new profile. Matches
  "Clash proxy / TUN proxy / 梯子 / 机场落地" intents. Not for picking
  airports/subscriptions (human business) or WireGuard-lane VPNs (this stack is
  proxying, not a VPN).
version: 1.3.0
author: Liz (lizliz.xyz)
license: MIT
---

# AI-native mihomo proxy stack

## The pattern

Every GUI clash client (FlClash, Clash Verge Rev, ...) is a thin shell over the
**mihomo core**. The AI-native move is to drop the shell and keep the core,
because the core already exposes everything a GUI does as a **REST API**
(`external-controller`). The GUI is a disposable human convenience; the API is
the contract agents build on.

```
airport profile (yaml) ──security patch──▶ config.yaml ◀── mihomo binary (headless)
                                                │                │  (Linux: setcap for rootless TUN;
                                                │                 │   macOS: TUN owned by one party, see Platform scope)
                                    service (systemd / launchd)  REST API 127.0.0.1:9090
                                                │                │
                                     TUN gvisor + auto-route   agent: curl / jq / MCP
```

Properties that matter:
- **Rootless service**: `systemd --user` on Linux, `launchd` LaunchAgent on
  macOS. No root-owned configs, so agents can manage everything without sudo.
- **Declarative**: one yaml = whole state. Reproduce = copy 3 files.
- **Observable**: every dial, rule match, and delay is one GET away.

## Platform scope — Linux primary, macOS sidecar

v1.2.x was Linux-only in its commands and would mislead on macOS. The pattern
is cross-platform; the mechanisms are not. Read this table before running any
step:

| Concern | Linux (reference path) | macOS (this skill supports, differently) |
|---|---|---|
| Service | `systemd --user` unit, `systemctl --user ...` | `launchd` LaunchAgent plist (`~/Library/LaunchAgents/*.plist`), `launchctl load/unload/list` |
| Rootless TUN | `setcap cap_net_admin,cap_net_bind_service=ep <binary>` + `getcap` re-check | **No `setcap`.** TUN is a Network Extension / privileged helper owned by one party (normally Clash Verge Rev + its helper bundle). Headless sidecars run with `tun.enable: false` and ride the owner's TUN or use explicit `-x` proxying |
| Privilege one-off | `pkexec <cmd>` (native auth dialog) | **No `pkexec`.** Privilege = user clicks through System Settings → Network Extension / helper install dialog by hand; the agent prepares everything around it and never touches a password prompt |
| Route inspection | `ip rule show` + `ip route show table 2022`, `ip link show Meta` | `netstat -rn -f inet` (look for `198.18.0.0` halves via a `utun` device) + `ifconfig` (`utun` with `inet 198.18.0.1 --> 198.18.0.1`), no policy-table concept |
| DNS check | `getent hosts <name>` (fake-ip `198.18.x.x` = hijack working) | `dscacheutil -q host -a name <name>`; `getent` does not exist. `scutil --dns` shows resolver order |
| Logs | `journalctl --user -u mihomo -f` | `StandardOutPath`/`StandardErrorPath` files named in the plist + `GET /connections`; there is no journal |
| Binary | `linux-amd64.gz` (or arm64) from `MetaCubeX/mihomo` | `darwin-arm64.gz` (Apple Silicon) / `darwin-amd64.gz` (Intel) from the same releases; `mihomo -v` must print `darwin` |

Coexistence doctrine (macOS default, Linux-legal too): **exactly one party
owns the TUN.** On macOS that is almost always the installed GUI (Verge) —
it already holds the helper approval, the `utun` device, and the fake-ip
`198.18/16` routes. Additional headless cores are **policy sidecars**: distinct
`mixed-port`, distinct `external-controller` port, `tun.enable: false`,
explicit upstream (`http`/`socks5` to the owner) or `DIRECT` bypass rules for
the domains the owner must not see. Never enable two TUNs, never reuse a port,
never let a sidecar rewrite the owner's `dns:`/`tun:` blocks. Port/controller
conflict check is a pre-flight step on every install (RUNBOOK §0).

## Complexity doctrine — native config first

The default answer to "mihomo keeps picking the wrong exit" is a **config
change**, not a program. Escalate only as far as the problem forces you:

1. **Native config**: a `select` group you pin by API; `url-test` nominally
   "fastest wins"; `fallback` nominally "first healthy in list order";
   `load-balance` for spread. These are *intended* semantics, not guarantees
   — actual failover behaviour is version- and nesting-dependent (see Group
   behaviour). Most "wrong node" complaints are a group type that cannot
   express the rule you actually want.
2. **Minimal selector** (a ~100-line loop + a platform scheduler): **only** when the
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
unreachable by design, and that is a feature. Ladder (Linux):

1. **Design root away**: `systemd --user` service +
   `setcap cap_net_admin,cap_net_bind_service=ep <binary>` gives TUN (and port
   53 bind) without root. Everything stays agent-editable.
2. **One-line human-in-the-loop**: when a privileged one-off is unavoidable,
   run `pkexec <cmd>` — a native auth dialog pops on the user's desktop; they
   type the password there, the agent orchestrates everything around it.
3. `setcap` is lost whenever the binary is replaced (update/reinstall). Re-check
   with `getcap` after every binary change.

macOS ladder (no `setcap`, no `pkexec` — both absent):

1. **Design root away differently**: one TUN owner (Verge + helper bundle),
   headless sidecars with `tun.enable: false`. Agent-editable scope = sidecar
   yaml + plist + ports, never the helper install.
2. **Human-in-the-loop for the one privileged click**: Network Extension /
   helper approval in System Settings. The agent stages the plist and config,
   states exactly which dialog the human will see, then stops and waits.
3. Binary replacement on macOS loses nothing capability-wise (there are no
   file caps), but re-verify with `mihomo -v` (must say `darwin arm64`) and
   `launchctl list | grep <label>` after every swap.

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
# logs: Linux `journalctl --user -u mihomo -f`; macOS: tail the plist's
# StandardOutPath/StandardErrorPath (no journal)
```

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
- **Current exit dead → degrade immediately**, cooldown does not apply.
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
   Bound the run with a wall-clock budget and the scheduler's timeout
   (systemd `TimeoutStartSec`, launchd `TimeOut`); non-overlap via
   `OnUnitInactiveSec` + lock (Linux) or `StartInterval` + lock (macOS).
4. Current dead → switch now. Higher priority / cheaper tier recovered → switch
   after cooldown. Same region + same tier → hold.

**Write**: the switch is `PUT /proxies/<group>` with `{"name":"<node>"}`.
Persist `last_switch` with an **atomic write** (`tmp` + `os.replace`) so a crash
mid-write cannot corrupt state.

**Run**: a platform scheduler — Linux: `systemd --user` timer, first run a few
seconds after boot (`OnActiveSec=15s`), then `OnUnitInactiveSec=60s` (not
`OnCalendar` — the next run starts 60 s *after the previous finished*, so a
slow boot-scan can never pile up); macOS: `launchd` plist with
`StartInterval 60` (same non-piling semantics) + `KeepAlive`. Either way guard
with a lock file; a second instance exits quietly. Prefer one
explicit timer unit over `ExecStartPost` hooks: a post hook that sleeps or
does network work blocks service readiness (and its failure can mark the
service failed); a hook that merely schedules an async transient timer
returns fast but adds transient-unit lifecycle/observability complexity. If a
hook is used at all, prefix with `-` and keep it trivial.
Emit one line per run in a fixed shape — `OK <current>`,
`HOLD <current> — <reason>`, `SWITCH <from> -> <to>`, `ERROR <why>` — so
`journalctl` (Linux) or the plist log file (macOS) is readable at a glance.

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
each test has a binary reading. Linux command first, macOS equivalent after:

| Layer | Decisive test (Linux / macOS) | Reading |
|---|---|---|
| DNS hijack | `getent hosts google.com` / `dscacheutil -q host -a name google.com` | fake-ip `198.18.x.x` = hijack working |
| Inbound to core | curl any site, then `GET /connections` (both) | `null` = traffic never reaches core → stack problem |
| Hijack routes | `ip rule show` **and** `ip route show table 2022` / `netstat -rn -f inet` + `ifconfig` (`utun` with `inet 198.18.0.1`) | Linux: a policy rule to a dedicated table **and** `default via <tun-ip> dev Meta` inside it; macOS: `198.18.0.0` halves routed via a `utun` device |
| Outbound escape | `curl --interface <phys-iface> https://223.5.5.5` (both) | works = bound sockets escape TUN rules; core must bind its outbounds (`auto-detect-interface: true` / top-level `interface-name`) |

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

- **Linux `auto-route` installs a policy rule + a dedicated table, not a
  default in the main table.** `ip route` alone will look like TUN never took
  over. Check `ip rule show` (the Linux reference used table `2022`) and
  then `ip route show table 2022`; confirm the device (`Meta`) is up, and
  finish with a plain `curl` (no `-x`) hitting 204. **On macOS there is no
  policy table**: read `netstat -rn -f inet` (fake-ip halves via `utun`) plus
  `ifconfig` for the `utun` device itself, then the same plain-curl 204.
- **Do not read a bare `5353` grep as a port conflict.** Check *which* socket:
  mihomo's own DNS listener binds its configured address, while mDNS/Avahi and
  Chrome bind the multicast address `224.0.0.251:5353`. Seeing both is normal.
  `device or resource busy` on a **hot reload** is likewise usually the previous
  TUN not yet released — re-check after a clean restart before calling it a
  real failure.

## Why the GUIs win on desktop — and where headless still earns its place

**A GUI client is a renderer over the same REST API — but on macOS the
renderer also owns the one thing agents cannot grant themselves: the TUN.**
Switch node, health check, mode toggle, reload, subscription update — the
operational surface an agent needs is all API. That is not a literal 1:1 with
every GUI widget (rule-order editing UX, profile-switch conveniences and
subscription-refresh semantics differ between clients), but nothing an agent
depends on is gui-only. The GUI is a *rendering preference*, not an interface
anyone needs — except for privilege.

Honest reflection on v1.2.x: it told desktop users to "drop the shell" while
offering no replacement for what the shell actually does for them. That is why
a user keeps Clash Verge Rev open instead of running this skill:

- **One-click TUN**: Verge ships a privileged helper bundle; the user approves
  once in System Settings and TUN works. Headless on macOS has no equivalent
  one-liner — `setcap`/`pkexec` do not exist, and the skill gave no plist, no
  dialog script, no "who owns the TUN" rule. Two TUNs fight; the skill never
  said which one must yield.
- **Zero-YAML onboarding**: subscription URL in, nodes out, latency bars, click
  to switch. The skill demanded curl + jq + hand-merged yaml before the first
  204 — all cost, no first win.
- **No coexistence path**: the skill read as migration-or-nothing. On a machine
  that already routes through Verge's TUN, "migrate" means breaking working
  internet for a doctrine. Nobody takes that trade.
- **No conflict pre-flight**: ports (`7890`/`9090`), controllers, data dirs and
  the `utun` device were assumed free. On a lived-in Mac they never are.

Corrected stance (v1.3.0): **Verge (or any installed GUI) owns the TUN on
macOS; headless cores join as policy sidecars.** The agent's value is not
"replace the GUI" but the things the GUI cannot do: region-priority policy the
group types cannot express, staged profile ingestion that never rewrites local
`dns:`/`tun:`/security, API-driven switch + verify + rollback with the blast
radius stated up front. Keeping the GUI installed is not a cold spare — on
macOS it is the supported TUN provider. Architect as: GUI = TUN + subscription
intake, sidecar = agent policy + verification.

The headless path still wins where the GUI structurally cannot follow:

- **Bundled-library rot**: AppImage/Electron shells carry legacy libstdc++ and
  friends that break against rolling-release mesa (the EGL-crash class, Linux).
- **Core lag**: GUIs ship stale cores; the headless path updates the core
  alone, in one file swap.
- **Opaque state**: profiles live in app-private stores no agent can safely
  mutate. Headless mihomo's entire state is one yaml.

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
  the service log (Linux `journalctl -u mihomo`, macOS plist log file),
  `/proxies` and `/connections`, plus a small structured
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
- **Do not measure with stale logs.** Narrow the log window to
  the incident (`journalctl --since` on Linux, time-bounded `tail`/`grep` on
  the plist log file on macOS), and re-derive counts you took before a restart — a running
  counter and a windowed count look identical and mean different things.
- **Never paste secrets**: `secret:`, UUIDs, REALITY `public-key`/`short-id`,
  subscription hostnames, or exit IPs. Reference them, don't quote them.

## Reference instantiations (no secrets in docs — ever)

Linux reference (the v1.2.x machine):

| Piece | Value |
|---|---|
| Binary | `~/.local/bin/mihomo` (official release, caps via setcap) |
| Config | `~/.config/mihomo/config.yaml` (airport profile + patches, `tun.stack: gvisor`) |
| Geo data | `~/.config/mihomo/{GeoIP,GeoSite}.dat` (reused from a GUI data dir) |
| Service | `~/.config/systemd/user/mihomo.service` → `systemctl --user ...` |
| API | `http://127.0.0.1:9090`, secret lives only in the local config file |
| Proxy port | `127.0.0.1:7890` (mixed) |

macOS coexistence shape (Verge owns TUN, sidecars do policy — observed on a
lived-in Mac, ports/labels as structure, credentials omitted):

| Piece | Value |
|---|---|
| TUN owner | Clash Verge Rev (helper bundle installed, `utun` + `198.18/16` routes, main `mixed-port`) |
| Sidecar A | own `mihomo` (darwin arm64) + own data dir, `tun.enable: false`, distinct `mixed-port` + distinct `external-controller`, LaunchAgent plist with `RunAtLoad` + `KeepAlive`, stdout/stderr to its own log files |
| Sidecar B | same shape as A, different ports/controller; `rules:` keep app-critical domains on `DIRECT` or forward to the owner via an `http` upstream — never into an exit that rejects them |
| Pre-flight | `lsof -iTCP -sTCP:LISTEN -P -n` shows no port/controller collision; `netstat -rn -f inet` shows exactly one fake-ip `utun`; `launchctl list` shows each label once |

Full reproduction steps with per-step completion criteria (Linux track +
macOS sidecar track): [RUNBOOK.md](RUNBOOK.md).
