#!/usr/bin/env bash
# intake-scan — stage-1 rule gate for proactive intake (see references/proactive-intake.md).
# Cheap, no model: finds new lines from Liz that look like intent, appends `new` rows
# to $FLEET_DIR/intake.md. The boss does stage 2 (judgement). Safe to run from cron/tmux.
#
# Env:
#   FLEET_DIR          ledger + cursors dir (default ~/radar-run/fleet)
#   INTAKE_REPOS       space-separated git repo paths (project context etc.)
#   INTAKE_GH          space-separated owner/repo for GitHub issues (needs gh auth)
#   INTAKE_GH_AUTHOR   GitHub login whose issues/comments count (default @me)
#   INTAKE_LOGS        space-separated globs of transcript/chat files (new lines only)
#   INTAKE_LOG_AUTHOR  regex a log line must match to count as Liz's (default 'Liz|liz|^>|user:')
#   INTAKE_MARKERS     intent regex (default below)
set -u
FLEET=${FLEET_DIR:-$HOME/radar-run/fleet}
CUR=$FLEET/intake-cursors; LEDGER=$FLEET/intake.md
MARK=${INTAKE_MARKERS:-'TODO|待办|回头|之后再|顺便|记得|帮我|要做|有空|得改|should (we|i)|need to|todo:'}
mkdir -p "$CUR"
[ -f "$LEDGER" ] || printf '| id | seen | source | quote | link | state | decision/why | receipt |\n|---|---|---|---|---|---|---|---|\n' > "$LEDGER"
now=$(date '+%F %H:%M')
add() { # source quote link
  local q; q=$(printf '%s' "$2" | tr '|\n' '/ ' | cut -c1-120)
  local id; id=$(printf '%s%s' "$1" "$q" | sha1sum | cut -c1-8)
  grep -q "| $id |" "$LEDGER" && return
  printf '| %s | %s | %s | %s | %s | new | | |\n' "$id" "$now" "$1" "$q" "$3" >> "$LEDGER"; n=$((n+1))
}
n=0
for r in ${INTAKE_REPOS:-}; do
  [ -d "$r/.git" ] || continue
  key=$CUR/repo-$(echo "$r" | tr '/' '_'); head=$(git -C "$r" rev-parse HEAD)
  last=$(cat "$key" 2>/dev/null || echo "")
  if [ -n "$last" ] && [ "$last" != "$head" ]; then
    git -C "$r" log -p --no-color "$last..$head" | grep -E '^\+[^+]' | grep -Ei "$MARK" | head -50 |
      while IFS= read -r l; do add "repo:$(basename "$r")" "${l#+}" "$r@${head:0:7}"; done
  fi
  echo "$head" > "$key"
done
for g in ${INTAKE_GH:-}; do
  key=$CUR/gh-$(echo "$g" | tr '/' '_'); since=$(cat "$key" 2>/dev/null || date -d '-1 day' +%F)
  gh issue list -R "$g" --state open --search "involves:${INTAKE_GH_AUTHOR:-@me} updated:>=$since" \
     --json number,title,url --jq '.[]|"\(.number)\t\(.title)\t\(.url)"' 2>/dev/null |
    while IFS=$'\t' read -r num t u; do add "gh:$g#$num" "$t" "$u"; done
  date +%F > "$key"
done
for glob in ${INTAKE_LOGS:-}; do
  for f in $glob; do
    [ -f "$f" ] || continue
    key=$CUR/log-$(echo "$f" | md5sum | cut -c1-12); off=$(cat "$key" 2>/dev/null || echo 0)
    size=$(wc -l < "$f"); [ "$size" -lt "$off" ] && off=0
    tail -n +"$((off+1))" "$f" | grep -E "${INTAKE_LOG_AUTHOR:-Liz|liz|^>|user:}" | grep -Ei "$MARK" | head -50 |
      while IFS= read -r l; do add "log:$(basename "$f")" "$l" "$f"; done
    echo "$size" > "$key"
  done
done
c=$(grep -c '| new |' "$LEDGER"); echo "intake-scan: $c new row(s) pending in $LEDGER"
