# RUNBOOK — reproduce an AI-native mihomo stack on Linux or macOS

Abstract steps; each ends in a checkable completion criterion. Gotchas are
placed where they bite, not in a separate pile. Two tracks: **Track A (Linux,
reference)** owns the TUN via `setcap`; **Track B (macOS sidecar)** joins a
machine where exactly one party (normally Clash Verge Rev) already owns the
TUN — sidecars run with `tun.enable: false` on distinct ports. Machine-specific
values from the reference installs are in `SKILL.md` § Reference
instantiations.

## 0. Pre-flight (both tracks — never skip on a lived-in machine)

- Port/controller collision: `lsof -iTCP -sTCP:LISTEN -P -n` (macOS/Linux) —
  every new `mixed-port` and `external-controller` port must be free.
- TUN ownership: exactly one TUN. Linux: `ip link show Meta` / rule table;
  macOS: `netstat -rn -f inet` + `ifconfig` — exactly one fake-ip `utun`.
  If a TUN already exists, the new core is a sidecar (`tun.enable: false`).
- Data-dir isolation: one `-d` dir per core; the candidate config path must
  sit inside its core's `-d` dir (or set `SAFE_PATHS`), else
  `PUT /configs?force=true` returns `400`.

**Done when**: chosen ports are free, the TUN owner is named, and each core
has its own data dir.

## 1. Acquire the core binary

- `mihomo` is absent from Arch's official repos (and many distros). Do **not**
  reuse a GUI client's bundled core: FlClash's `FlClashCore` is a modified
  build whose IPC runs over a unix socket — it panics standalone, and Verge's
  `verge-mihomo` is tied to its wrapper flags. Get the official release from
  `MetaCubeX/mihomo`: stable tag, `linux-amd64.gz` (Track A) or
  `darwin-arm64.gz` / `darwin-amd64.gz` (Track B, match `uname -m`).
- Fetch via the download doctrine ladder (SKILL.md). `gunzip`, install to
  `~/.local/bin/mihomo` (Linux) or a per-sidecar dir / `~/.local/bin` (macOS),
  `chmod +x`.

**Done when**: `<binary> -v` prints `Mihomo Meta vX.Y.Z` **and** the platform
matches (`linux` on Track A, `darwin` on Track B — e.g. `darwin arm64` on
Apple Silicon) with `with_gvisor` in the tags.

## 2. Acquire a profile

An airport export ("Clash subscription download"), an existing `config.yaml`,
or a subscription URL (then use `proxy-providers` instead of inline
`proxies`). The profile supplies nodes, groups, rules, DNS — you supply the
patches.

"Any full yaml works" is too strong: what matters is that it actually carries
nodes. Identify the shape first (SKILL.md § Ingesting a new profile) — a
provider-only export, a JSON blob and an HTML login page all parse as
*something*, and none of them is a drop-in config. Note the trap:
a `proxy-providers:`-only file yields **zero** inline nodes until each provider
(`url:` / `path:`) is resolved — "take the nodes" does not apply to it
directly.

**Done when**: the file parses and yields a non-empty node list through one of
the known shapes (inline `proxies` / resolved `proxy-providers` / top-level
proxy array) — and you can say which shape it was.

## 3. Patch security + append TUN

- `external-controller: 127.0.0.1:9090`, `secret: <openssl rand -hex 12>`
  (see Security doctrine — assume the profile ships LAN-open defaults).
- Append (start disabled; enable in step 7 after caps exist):

```yaml
tun:
  enable: false
  stack: gvisor        # pure userspace; `mixed` has dead-TCP failure modes
  auto-route: true
  auto-detect-interface: true
  dns-hijack:
    - any:53
```

**Done when**: `grep -E 'external-controller|secret|stack' config.yaml` shows
localhost + non-empty secret + gvisor.

## 4. Geo data (skip the first-start download stall)

Core boot blocks on `GeoIP/GeoSite` fetch if missing. Reuse any existing clash
install's files — Linux: `~/.local/share/com.follow.clash/` (FlClash),
`~/.local/share/io.github.clash-verge-rev*` (Verge); macOS: the Verge
Application Support dir or the sidecar's own data dir — copy as
`GeoIP.dat` / `GeoSite.dat` beside the config (both case variants is cheap
insurance). Profiles set `geo-auto-update: false` usually; the jsdelivr
`geox-url` in the profile covers later manual updates.

**Done when**: the core's `-d` dir holds both `.dat` files (e.g.
`ls <datadir>/*.dat` shows both).

## 5. Validate config

`mihomo -t -f <config.yaml> -d <datadir>` (same dir the service will use —
never validate against one dir and run against another).

**Done when**: `configuration file ... test is successful`.

## 6. Rootless service

Track A (Linux) — `~/.config/systemd/user/mihomo.service`:

```ini
[Unit]
Description=Mihomo (Clash Meta) user service
After=network-online.target

[Service]
ExecStart=%h/.local/bin/mihomo -d %h/.config/mihomo
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
```

`systemctl --user daemon-reload && systemctl --user enable --now mihomo`

Track B (macOS) — one LaunchAgent plist per sidecar,
`~/Library/LaunchAgents/<label>.plist` (e.g. `com.example.mihomo-sidecar`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.mihomo-sidecar</string>
  <key>ProgramArguments</key><array>
    <string>/Users/you/.local/bin/mihomo</string><string>-d</string><string>/Users/you/.mihomo-sidecar</string><string>-f</string><string>/Users/you/.mihomo-sidecar/config.yaml</string>
  </array>
  <key>WorkingDirectory</key><string>/Users/you/.mihomo-sidecar</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/Users/you/.mihomo-sidecar/out.log</string>
  <key>StandardErrorPath</key><string>/Users/you/.mihomo-sidecar/err.log</string>
</dict></plist>
```

`launchctl load ~/Library/LaunchAgents/<label>.plist` (unload to stop).
Sidecar plist uses its own data dir, own ports, and `tun.enable: false`.

**Done when**: Track A: `systemctl --user is-active mihomo` = active AND
`curl -H "Authorization: Bearer $SECRET" 127.0.0.1:9090/version` returns JSON.
Track B: `launchctl list | grep <label>` shows the label AND the sidecar's
own `external-controller` `/version` returns JSON.

## 7. Verify the proxy path (pre-TUN on Linux; pre-handoff on macOS)

`curl -x http://127.0.0.1:<mixed-port> https://www.gstatic.com/generate_204` → 204,
then exit-IP check (`curl -x ... https://ipinfo.io/json`) to confirm a real
airport node answered. On Linux verify **before** TUN so failures are
attributable to the profile, not the TUN layer. On macOS verify the sidecar
the same way **before** wiring any upstream/`DIRECT` handoff to the TUN owner.

**Done when**: 204 + plausible exit IP through the new core's own port.

## 8. TUN (system-wide — Track A only; Track B skips)

Track A:

1. One-time privilege grant (Privilege doctrine):
   `pkexec setcap cap_net_admin,cap_net_bind_service=ep ~/.local/bin/mihomo`
   — user types the password in the native dialog. `getcap` confirms.
2. Flip `tun.enable: true`, `systemctl --user restart mihomo`.
3. `ip link` shows the TUN device (`Meta`); plain `curl
   https://www.gstatic.com/generate_204` (no `-x`) → 204.

**Done when**: un-proxied curl hits 204. Everything on the machine now routes
through the core; agents need zero per-app proxy config.

Track B (macOS): **do not enable TUN on the sidecar.** The owner (Verge)
already holds the `utun` device and the approval. The sidecar proves its
handoff instead: app-critical domains resolve via the owner's TUN
(`dscacheutil` shows fake-ip where expected), `curl -x <sidecar-port>` hits
204, and un-proxied `curl` hits 204 through the owner's TUN. Two TUNs is a
misconfiguration, not redundancy.

## 9. If TUN blacks out

Work the TUN debugging playbook (SKILL.md) top to bottom — DNS, inbound,
routes, outbound escape — then apply the known fixes (gvisor, interface
binding). Retry once before digging: auto-select health-checks cause transient
`000`s on freshly started stacks.

**Done when**: the decisive test for each layer passes in order.

## 10. Ingest a new profile (staged, never in-place)

Ongoing operation, not a build step. The default is **extract nodes and merge
into the existing known-good shell** — never adopt the incoming file wholesale.

1. Identify the shape (SKILL.md table): full config / provider-only /
   proxy list / subscription URL / reject. Provider-only has two modes:
   **preserve** (`proxy-providers:` + groups with `use:`/filters, stays
   renewable) or **materialize** (inline snapshot for strict merging) —
   never silently flatten a renewable provider into a stale snapshot.
2. Timestamp a backup of the working config *before* touching anything:
   `cp config.yaml config.yaml.bak-$(date +%Y%m%d-%H%M%S)`.
   All writes under `umask 077`; dirs `0700`, files `0600`; candidates,
   sources and backups are credential-bearing — git-ignored and never
   world-readable.
3. Extract nodes. **Keep local `dns:` / `tun:` / `rules:` /
   `external-controller` / `secret` exactly as they are** — a subscription
   must not get to rewrite security or policy.
4. Merge deterministically: classify every node via the policy alias table,
   report per-region **plus unclassified** counts, and hold unclassified
   nodes out of active groups. Same name + same definition dedupes; same
   name + different definition renames (`<name> (2)`, region prefix kept)
   or is rejected with the conflict listed. Never silently overwrite.
   Sort stably, hash inputs, skip the write if unchanged.
5. Write a **candidate** file next to the live config (same dir, so the
   `PUT /configs` path stays inside the core's `-d` / `SAFE_PATHS`).
6. Validate in a **private isolated snapshot**, not `mktemp -d` alone: copy
   or symlink every local dependency the candidate references (Geo `.dat`,
   `rule-providers`, `proxy-provider` path files, certs, other relative
   assets), then `mihomo -t -f <candidate> -d <snapshot>`. If the snapshot
   cannot be assembled completely, either validate in the real data dir
   while explicitly accepting and reporting the `cache.db` contention, or
   stop and ask rather than claim isolation — prefer stopping for
   high-risk changes. Reject on any error or a zero-node result.
7. Atomic promote: backup already retained (step 2); write temp on the
   **same filesystem** + `rename` over the live file (`fsync` optional).
   Then reload by workflow — inline proxies: `PUT /configs?force=true`
   **with a JSON body naming the absolute path**
   (`-d '{"path":"/abs/path/config.yaml"}'` — an empty body returns
   `400 Body invalid`); `proxy-provider` setups:
   `PUT /providers/proxies/<name>` with **no** full reload.
8. Runtime post-check through the running core (a file that passes `mihomo -t`
   is not a loaded config): `/proxies` shows the new nodes, a real 204 flows,
   and — Track A with TUN enabled — the TUN device is still up; Track B —
   the owner's TUN is still the only `utun` and the sidecar's 204 flows. On a
   `device or resource busy` line after a hot reload, preserve/rollback
   first where possible; a clean service restart
   (`systemctl --user restart mihomo` / `launchctl unload+load <label>`) is a
   disruptive fallback — announce it per blast radius before restarting,
   then re-check before calling it a failure.
9. Rollback on any failed check: copy the timestamped backup back, reload the
   same way, re-verify. Never leave a failed candidate live.

**Done when**: change summary held (node count, per-region + unclassified
counts, renamed conflicts, exclusions), timestamped backup exists, the
running core serves the new nodes (204), and the rollback command plus its
precondition (backup path, reload method) is verified — a healthy production
activation is **not** rolled back just to prove it.

## 11. Verify policy routing (TUN) before believing it works

Track A — `auto-route` does **not** install a default route in the main table, so
checking `ip route` alone yields the false conclusion "TUN never took over":

```bash
ip rule show                  # expect a rule pointing at a dedicated table (reference: 2022)
ip route show table 2022      # expect `default via <tun-ip> dev Meta`
ip link show Meta             # device up
curl -s -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204   # NO -x → expect 204
```

Track B (macOS) — there is no policy table; the checks are:

```bash
netstat -rn -f inet           # expect 198.18.0.0 halves via a utun device (exactly one fake-ip utun)
ifconfig                      # the utun device is up (inet 198.18.0.1 --> 198.18.0.1 class)
dscacheutil -q host -a name google.com  # fake-ip 198.18.x.x = hijack working
curl -s -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204   # NO -x → expect 204
```

When reading `ss`/logs for port `5353`, check *which* socket: mihomo's own DNS
listener versus the mDNS multicast address `224.0.0.251:5353`. Seeing both is
normal — a bare port grep is not evidence of a conflict. Same for
`configure tun interface: device or resource busy` on a **hot reload**: that is
usually the previous TUN not yet released, so re-check after a clean restart
before calling it a real failure.

**Done when**: the rule exists, the dedicated table holds the default via the
TUN device, and an un-proxied curl returns 204.

## 12. Failover acceptance test

This proves the automation, not your typing. Run it once per exit-selection
change.

1. Back up first, and write the blast radius down: "this machine loses internet
   until the selector acts; worst case is one timer interval".
2. Make the current exit fail (e.g. point the in-use node at a black-hole
   address in a *candidate* config) and apply it.
3. **Touch nothing.** Watch `/proxies` `now` plus an un-proxied `curl` on a
   loop until the exit moves on its own.
4. Restore the good config and confirm the exit comes back.

**Done when**: the exit moved with no human action and the logs show the
decision line (`SWITCH ... — <reason>` in `journalctl` on Linux, in the
scheduler/sidecar log file on macOS). For the recovery half, state whether
the cooldown expired naturally or you cleared the state file — a cleared
cooldown is a bypassed mechanism, not a natural recovery.

## Gotchas that bite regardless of machine

- **`pkill -f` self-match**: a `pkill -f <pattern>` whose pattern appears in
  your own command line kills your own shell. `pgrep -x` / exact names first.
- **Caps evaporate on binary replacement (Linux)**: update = re-run setcap.
  macOS has no caps — but re-verify `mihomo -v` platform and
  `launchctl list | grep <label>` after every swap.
- **Two TUNs fight (macOS)**: a sidecar with `tun.enable: true` alongside
  Verge yields flapping `utun` devices and fake-ip wars. The fix is policy,
  not debugging: exactly one TUN owner, sidecars stay `false`.
- **Absent commands are a platform signal, not a missing package**: `ip`,
  `getent`, `journalctl`, `systemctl`, `setcap`, `pkexec` do not exist on
  macOS. Reaching for them means you are on the wrong track — switch to
  `netstat/ifconfig/dscacheutil/scutil`, plist log files, `launchctl`.
- **Mirror resets mid-stream**: pair every mirror fetch with `curl -C -` and a
  retry loop; two failures → human-phone relay.
- **Subscription refresh vs config replacement are different operations**:
  inline-profile workflows replace the file + `PUT /configs?force=true`
  **with a JSON body naming the absolute path**
  (`-d '{"path":"/abs/path/config.yaml"}'` — an empty body returns
  `400 Body invalid`, and a path outside the core's `-d` dir needs
  `SAFE_PATHS`); `proxy-provider` workflows only
  `PUT /providers/proxies/<name>` with no full reload. After either, confirm
  through the running core (`/proxies` + a real 204), not just `mihomo -t`.
- **A file that passes `mihomo -t` is not a loaded config.** Validate the
  candidate on disk, then reload, then confirm through the running core
  (`/proxies` group membership plus a real 204). "The file is correct" and "the
  core is serving it" are different claims.
