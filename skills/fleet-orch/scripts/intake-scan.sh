#!/usr/bin/env bash
# intake-scan — stage-1 rule gate for proactive intake (references/proactive-intake.md).
# No model, no actions: finds NEW lines written by Liz that look like a request and
# appends `new` rows to $FLEET_DIR/intake.md for the boss to judge. Idempotent:
# per-source cursors + id dedupe; the first run of a source only sets its cursor
# (no backlog flood). Quotes are redacted for token-like strings.
#
# Env (all optional; unset source = skipped):
#   FLEET_DIR          ledger + cursors (default ~/fleet-orch)
#   INTAKE_REPOS       git repo paths, space-separated (e.g. project-context)
#   INTAKE_GIT_AUTHOR  only commits whose author matches (default Liz|lizliz)
#   INTAKE_GH          owner/repo list; open issues Liz authored, updated since last scan
#   INTAKE_GH_USER     her GitHub login (default lizliz404)
#   INTAKE_LOGS        trusted plain-text transcript globs, NOT raw JSONL
#   INTAKE_PI_SESSIONS Pi JSONL paths/globs; user-text adapter, first sight EOF only
#   INTAKE_LOG_AUTHOR  regex marking a line as hers (default '^\s*(Liz|user)\s*[:：>]')
#   INTAKE_MARKERS     intent regex (default below)
set -u
FLEET=${FLEET_DIR:-$HOME/fleet-orch}
CUR=$FLEET/intake-cursors; LEDGER=$FLEET/intake.md
MARK=${INTAKE_MARKERS:-'TODO|待办|回头|之后再|顺便|记得|帮我|要做|有空|得改|should (we|i)\b|need to|todo:'}
LOGAUTH=${INTAKE_LOG_AUTHOR:-'^\s*(Liz|user)\s*[:：>]'}
MAX=50
umask 077
mkdir -p "$CUR"
chmod 700 "$CUR"
exec 9>"$CUR/.lock"; flock -n 9 || { echo "intake-scan: already running"; exit 0; }
# Convert only the configured Pi sources; stdout contains file paths, not bodies.
pi_logs=
if [ -n "${INTAKE_PI_SESSIONS:-}" ]; then
  pi_logs=$(python3 "$(dirname "$0")/intake-pi.py") || exit 1
fi
[ -f "$LEDGER" ] || printf '| id | seen | source | quote | link | state | decision/why | receipt |\n|---|---|---|---|---|---|---|---|\n' > "$LEDGER"
now=$(date '+%F %H:%M')

redact() { sed -E 's/(sk-|ghp_|gho_|github_pat_|xox[abp]-|AKIA)[A-Za-z0-9_-]+/\1[REDACTED]/g; s/[A-Za-z0-9+\/_=-]{32,}/[REDACTED]/g'; }
add() { # source quote link
  local q id
  q=$(printf '%s' "$2" | tr '|\n\r' '/  ' | redact | cut -c1-120)
  id=$(printf '%s%s' "$1" "$q" | sha1sum | cut -c1-8)
  grep -qF "| $id |" "$LEDGER" && return
  printf '| %s | %s | %s | %s | %s | new | | |\n' "$id" "$now" "$1" "$q" "$3" >> "$LEDGER"
}
cap() { # warn instead of silently dropping beyond MAX
  local all; all=$(cat); [ -n "$all" ] || return 0
  printf '%s\n' "$all" | head -n "$MAX"
  [ "$(printf '%s\n' "$all" | grep -c .)" -gt "$MAX" ] && echo "intake-scan: $1 had >$MAX hits, kept first $MAX" >&2
  return 0
}

for r in ${INTAKE_REPOS:-}; do
  git -C "$r" rev-parse --git-dir >/dev/null 2>&1 || { echo "intake-scan: skip $r (not a repo)" >&2; continue; }
  key=$CUR/repo-$(printf '%s' "$r" | md5sum | cut -c1-12); head=$(git -C "$r" rev-parse HEAD)
  last=$(cat "$key" 2>/dev/null || true)
  if [ -n "$last" ] && [ "$last" != "$head" ] && git -C "$r" cat-file -e "$last" 2>/dev/null; then
    git -C "$r" log -p --no-color --author="${INTAKE_GIT_AUTHOR:-Liz|lizliz}" --extended-regexp "$last..$head" |
      grep -E '^\+[^+]' | grep -Ei "$MARK" | cap "repo:$r" |
      while IFS= read -r l; do add "repo:$(basename "$r")" "${l#+}" "$r@${head:0:7}"; done
  fi
  echo "$head" > "$key"
done

for g in ${INTAKE_GH:-}; do
  key=$CUR/gh-$(printf '%s' "$g" | tr '/' '_')
  since=$(cat "$key" 2>/dev/null || true); stamp=$(date -u +%FT%TZ)
  if [ -n "$since" ]; then
    if ! out=$(gh issue list -R "$g" --state open -L "$MAX" \
        --search "author:${INTAKE_GH_USER:-lizliz404} updated:>=$since" \
        --json number,title,url --jq '.[]|"\(.number)\t\(.title)\t\(.url)"' 2>&1); then
      echo "intake-scan: gh $g failed, cursor kept: ${out:0:120}" >&2; continue
    fi
    printf '%s\n' "$out" | while IFS=$'\t' read -r num t u; do
      [ -n "$num" ] && add "gh:$g#$num" "$t" "$u"; done
  fi
  echo "$stamp" > "$key"
done

for glob in ${INTAKE_LOGS:-} $pi_logs; do
  for f in $glob; do
    [ -f "$f" ] || continue
    case "$f" in *.jsonl) echo 'intake-scan: raw JSONL rejected; use INTAKE_PI_SESSIONS' >&2; continue ;; esac
    key=$CUR/log-$(printf '%s' "$f" | md5sum | cut -c1-12)
    size=$(wc -l < "$f"); off=$(cat "$key" 2>/dev/null || echo "")
    if [ -n "$off" ]; then
      [ "$size" -lt "$off" ] && off=0   # rotated/truncated
      tail -n +"$((off+1))" "$f" | head -n "$((size-off))" | grep -P "$LOGAUTH" | grep -Ei "$MARK" | cap "log:$f" |
        while IFS= read -r l; do add "log:$(basename "$f")" "$l" "$f"; done
    fi
    echo "$size" > "$key"
  done
done

chmod 600 "$LEDGER"
echo "intake-scan: $(grep -c '| new |' "$LEDGER") new row(s) pending in $LEDGER"
