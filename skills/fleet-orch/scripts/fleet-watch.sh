#!/usr/bin/env bash
# fleet-watch — poll hc terminals + watched artifacts, notify the orchestrator
# window on state transitions, append every event to status.log.
#
# Usage:
#   FLEET_BOSS=t14 FLEET_DIR=~/fleet-orch \
#   WATCH_PROGRESS='/home/liz/radar-run/*/progress.json' \
#   EXCLUDE='t14 t19' ./fleet-watch.sh
#
# Run it in tmux so it survives: tmux new-session -d -s fleet-watch ./fleet-watch.sh
#
# Env:
#   FLEET_BOSS      hc name/address receiving notifications (default t14)
#   FLEET_DIR       dir holding status.log / notify-state.txt / *.md receipts (default ~/fleet-orch)
#   FLEET_NOTIFY    0 = log only, no messages typed into the user conversation
#   WATCH_PROGRESS  glob of progress.json files to poll (default none)
#   EXCLUDE         space-separated hc addresses to skip (default: the boss itself)
#   POLL_SECS       seconds between cycles (default 5)
#   SNAP_SECS       seconds between full state snapshots to status.log (default 600)
#
# Design notes:
# - Notifications are TYPED into the boss window via `hc send` — that is the
#   entire transport. status.log is the durable channel even if send fails.
# - Transitions only, never raw state: done/idle from working, blocked always,
#   dead always, new tmux sessions, new *.md receipts.
# - The script knows nothing about "your fleet" vs other sessions — hc's
#   terminal registry is machine-wide. EXCLUDE is the only filter.

set -u
BOSS=${FLEET_BOSS:-t14}
FLEET=${FLEET_DIR:-$HOME/fleet-orch}
POLL=${POLL_SECS:-5}
SNAP=${SNAP_SECS:-600}
EXCLUDE=${EXCLUDE:-$BOSS}
PROGRESS_GLOB=${WATCH_PROGRESS:-}

mkdir -p "$FLEET"
STATE=$FLEET/notify-state.txt
LOG=$FLEET/status.log
touch "$STATE"
snap=0

in_exclude() { case " $EXCLUDE " in *" $1 "*) return 0;; esac; return 1; }

notify() {
  echo "$(date '+%m-%d %H:%M:%S') NOTIFY $1" >> "$LOG"
  [ "${FLEET_NOTIFY:-1}" = 0 ] && return 0
  # Check the live registry first: yesterday's boss may now be a recovery shell.
  local target
  target=$(hc ls --json 2>/dev/null | python3 -c '
import json, sys
for terminal in json.load(sys.stdin).get("terminals", []):
    if sys.argv[1] in (terminal.get("address"), terminal.get("name")) and terminal.get("agent") not in (None, "zsh", "bash", "fish", "nu"):
        print(terminal["address"])
        break
' "$BOSS")
  [ -n "$target" ] && hc send --force "$target" "fleet-notify: $1" >/dev/null 2>&1
}

while true; do
  now=$FLEET/.cur-state
  : > "$now"

  # 1) hc terminal statuses
  hc ls --json 2>/dev/null | python3 -c "
import json,sys
for t in json.load(sys.stdin).get('terminals',[]):
    a=t['address']; st=t.get('status') or ''
    if st: print(f'{a}\t{st}')" >> "$now" 2>&1

  # 2) optional progress.json watches: status field + mtime
  if [ -n "$PROGRESS_GLOB" ]; then
    for f in $PROGRESS_GLOB; do
      [ -f "$f" ] || continue
      d=$(basename "$(dirname "$f")")
      st=$(python3 -c "import json;print(json.load(open('$f')).get('status','?'))" 2>/dev/null)
      mt=$(stat -c %Y "$f" 2>/dev/null)
      echo "job:$d	$st:$mt" >> "$now"
    done
  fi

  # 3) tmux session inventory (long-running jobs live there)
  tmux ls 2>/dev/null | cut -d: -f1 | while read -r s; do echo "tmux:$s	live"; done >> "$now"

  # 4) receipt file count (workers drop *.md reports here)
  # intake.md is the intake ledger, not a worker receipt
  n=$(find "$FLEET" -maxdepth 1 -name '*.md' ! -name intake.md | wc -l)
  echo "reports	$n" >> "$now"

  # diff against last snapshot — notify on transitions only
  while IFS=$'\t' read -r k v; do
    [ -z "$k" ] && continue
    in_exclude "$k" && continue
    old=$(grep -P "^${k}\t" "$STATE" 2>/dev/null | cut -f2-)
    [ "$v" = "$old" ] && continue
    case "$k" in
      t[0-9]*)
        if [[ "$v" == blocked || ( "$old" == working && "$v" =~ ^(done|idle)$ ) || "$v" == dead ]]; then
          notify "$k: ${old:-none} -> $v"
        fi ;;
      job:*)
        os=${old%%:*}; ns=${v%%:*}
        [ "$os" != "$ns" ] && notify "${k#job:} status: ${os:-?} -> $ns" ;;
      tmux:*)
        [ -z "$old" ] && [ "$v" = live ] && notify "tmux session up: ${k#tmux:}"
        ;;
      reports)
        [ "${old:-0}" != "$v" ] && [ -n "$old" ] && \
          notify "new report in fleet/ ($(find "$FLEET" -maxdepth 1 -name '*.md' ! -name intake.md -printf '%T@ %f\n' | sort -rn | head -1 | cut -d' ' -f2-))" ;;
    esac
  done < "$now"

  # tmux sessions that were live last cycle and are gone now
  grep -P '^tmux:' "$STATE" | cut -f1 | while read -r k; do
    grep -qP "^${k}\t" "$now" || notify "tmux session died: ${k#tmux:}"
  done

  cp "$now" "$STATE"

  # periodic full snapshot for postmortem/auditing
  snap=$((snap + POLL))
  if [ "$snap" -ge "$SNAP" ]; then
    snap=0
    {
      echo "── $(date '+%m-%d %H:%M:%S') ──"
      cat "$STATE"
      df -h /home /tmp 2>/dev/null | tail -n +2 | awk '{print "  " $6 " " $5 " used"}'
    } >> "$LOG"
  fi

  sleep "$POLL"
done
