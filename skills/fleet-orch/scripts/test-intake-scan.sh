#!/usr/bin/env bash
# Offline test for intake-scan.sh: temp repo + temp log, no network, no gh.
set -eu
S=$(cd "$(dirname "$0")" && pwd)/intake-scan.sh
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
export FLEET_DIR=$T/f INTAKE_REPOS=$T/r INTAKE_LOGS="$T/*.log" INTAKE_GH=
unset GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL; export GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@x
g() { git -C "$T/r" -c user.name="$1" -c user.email=a@b commit -qm m --allow-empty "${@:2}"; }
fail() { echo "FAIL: $1"; cat "$FLEET_DIR/intake.md"; exit 1; }
git init -q "$T/r"; g Liz
echo "Liz: 记得把旧的 TODO 清掉" > "$T/s.log"
"$S" >/dev/null                                   # first run: cursors only, no backlog
[ "$(grep -c '| new |' "$FLEET_DIR/intake.md")" = 0 ] || fail "first run flooded backlog"
echo "- TODO: 修安装文档" > "$T/r/a.md"; git -C "$T/r" add a.md; g Liz
echo "- TODO: bot 自己写的" > "$T/r/b.md"; git -C "$T/r" add b.md; g bot
{ echo "assistant: 我会记得帮我自己"; echo "Liz: 顺便看下 token ghp_abcdefghijklmnopqrstuvwxyz0123 失效没";
  echo "Liz: 今天天气不错"; echo "Liz > 帮我 查 Zernio | 定价"; } >> "$T/s.log"
"$S" >/dev/null; "$S" >/dev/null                  # second run must be a no-op
L=$FLEET_DIR/intake.md
[ "$(grep -c '| new |' "$L")" = 3 ] || fail "expected 3 rows"
grep -q '修安装文档' "$L" || fail "Liz commit missed"
grep -q 'bot 自己写的' "$L" && fail "bot commit leaked"
grep -q 'assistant:' "$L" && fail "assistant line leaked"
grep -q 'ghp_abc' "$L" && fail "token not redacted"
grep -q 'Zernio / 定价' "$L" || fail "pipe not escaped"
: > "$T/s.log"; echo "Liz: 记得 rotate 后的新行" > "$T/s.log"; "$S" >/dev/null
grep -q 'rotate 后' "$L" || fail "rotation missed"
echo "ok: intake-scan"
