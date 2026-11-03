#!/usr/bin/env bash
# worker-unnudge — external self-heal loop: resume workers stuck in an
# upstream error state. This is the fleet-scale version of DSH §6's
# "external control loop that keeps re-checking transient external failures
# until normal" — an infra-fault watchdog, not a progress judge (progress is
# still the boss's job).
#
# Evidence 2026-11-03: a Hanzilla 503 storm left pi workers cycling
# working<->error for ~30 min. Nudging on the error state brought them back
# each time the upstream opened a window; the boss later handed stalled
# tasks to devin workers and had the pi workers write *-handoff.md.
#
# Run in tmux so it survives: tmux new-session -d -s worker-unnudge ./worker-unnudge.sh
#
# Env:
#   NUDGE_AGENTS    agent names to rescue, space-separated (default "pi")
#   NUDGE_MSG       message sent into the worker (default below)
#   NUDGE_COOLDOWN  min seconds between nudges to the same worker (default 300)
#   NUDGE_MAX       stop nudging a worker after this many sends (default 20)
#   POLL_SECS       seconds between sweeps (default 60)
#   FLEET_DIR       dir holding status.log / unnudge-state/ (default ~/fleet-orch)
#
# Limits — this is liveness repair, not health verification:
# - It acts on hc "error" state; it cannot tell whether the upstream has
#   actually recovered. During a sustained outage a worker will recover
#   briefly and error again — the cooldown keeps that from becoming a spam
#   loop. If the storm persists, the BOSS decides: switch runtime or hand
#   the task off. Do not let this loop hide a real outage.
# - The default message claims nothing about upstream health; it only tells
#   the worker to retry a transient failure.
set -u
FLEET=${FLEET_DIR:-$HOME/fleet-orch}
LOG=$FLEET/status.log
ST=$FLEET/unnudge-state
AGENTS=${NUDGE_AGENTS:-pi}
MSG=${NUDGE_MSG:-'If your last failure was a transient upstream error, retry and continue your task; if it fails again, stay in error and wait for the boss.'}
COOL=${NUDGE_COOLDOWN:-300}
MAXN=${NUDGE_MAX:-20}
POLL=${POLL_SECS:-60}
mkdir -p "$FLEET" "$ST"

while :; do
  # workers currently live + in error state, filtered to NUDGE_AGENTS
  erred=$(hc ls --json 2>/dev/null | python3 -c '
import json, sys
agents = set(sys.argv[1].split())
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
for t in d.get("terminals", []):
    if t.get("agent") in agents and t.get("status") == "error" and t.get("state") == "live":
        print(t["address"])
' "$AGENTS")

  # a worker that left error state resets its cooldown/count — next storm is new
  for f in "$ST"/*; do
    [ -e "$f" ] || continue
    case " $erred " in *" $(basename "$f") "*) ;; *) rm -f "$f";; esac
  done

  for t in $erred; do
    now=$(date +%s)
    read -r last n < "$ST/$t" 2>/dev/null || { last=0; n=0; }
    [ $((now - last)) -lt "$COOL" ] && continue
    [ "$n" -ge "$MAXN" ] && continue
    if hc send "$t" "$MSG" >/dev/null 2>&1; then
      printf '%s %s\n' "$now" "$((n + 1))" > "$ST/$t"
      echo "$(date '+%m-%d %H:%M:%S') AUTO-NUDGE $t (#$((n + 1)))" >> "$LOG"
    fi
    sleep 2
  done
  sleep "$POLL"
done
