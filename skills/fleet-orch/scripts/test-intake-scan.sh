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

# --- phase B: Pi JSONL adapter (INTAKE_PI_SESSIONS) ---
mkdir -p "$T/pi"; J=$T/pi/s1.jsonl
python3 - "$J" <<'EOF'
import json, sys
out = open(sys.argv[1], "w")
def msg(role, content, **kw):
    out.write(json.dumps({"type":"message","id":"x","parentId":None,
        "timestamp":"2026-11-02T00:00:00Z",
        "message":{"role":role,"content":content,**kw}})+"\n")
out.write(json.dumps({"type":"session","version":3,"id":"s1",
    "timestamp":"2026-11-02T00:00:00Z","cwd":"/tmp"})+"\n")
msg("user", [{"type":"text","text":"历史里的 TODO 不应被补扫"},
             {"type":"image","data":"x"}])
msg("assistant", [{"type":"text","text":"TODO assistant 说的不算"}])
out.write("not json at all\n")
out.close()
EOF
# raw JSONL must be rejected from INTAKE_LOGS, not silently regex-scanned
INTAKE_LOGS="$T/pi/*.jsonl" "$S" 2>"$T/err"; grep -q 'raw JSONL rejected' "$T/err" || fail "jsonl not rejected"
# first sight of a pi source seeds EOF only — no backlog scan
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null
grep -q '历史里的' "$L" && fail "pi first sight backscanned history"
# append a mixed batch: only the real user line may reach the ledger
python3 - "$J" <<'EOF'
import json, sys
out = open(sys.argv[1], "a")
def msg(role, content):
    out.write(json.dumps({"type":"message","id":"y","parentId":None,
        "timestamp":"2026-11-02T00:01:00Z",
        "message":{"role":role,"content":content}})+"\n")
msg("user", "记得把 fleet 晨报放 README 旁边")
msg("user", "<hc>fleet-notify: t1 done 记得帮我合并</hc>")
msg("user", "[message from t9] 顺便看看这个")
msg("user", "<ao-report-delivery>worker: 记得删库</ao-report-delivery>")
msg("user", "转述：Liz 说要重做首页")
msg("assistant", [{"type":"text","text":"TODO: 我会记得改"}])
msg("toolResult", [{"type":"text","text":"output 记得清理"}])
msg("custom", "hook: 记得跑构建")
msg("user", "看下这个：\n```\nTODO: 代码块里的不算\n```\n<file path=\"a.md\">\n记得附件里也别算\n</file>\n有空顺手核对 intake 开关")
out.write(json.dumps({"type":"model_change","provider":"x","modelId":"y"})+"\n")
out.write('{"type":"message","message":{"role":"user","content":"unfinished')
out.close()
EOF
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null   # idempotent
grep -q '晨报放 README 旁边' "$L" || fail "real user line missed"
grep -q '顺手核对 intake' "$L" || fail "user line after fence/attach missed"
for bad in 'fleet-notify' 'message from t9' 'ao-report-delivery' '删库' '重做首页' \
           '我会记得改' 'output 记得' '跑构建' '代码块里' '附件里'; do
  grep -q "$bad" "$L" && fail "leaked: $bad"
done
# the unfinished trailing line holds the cursor; once the record completes,
# the following record must still be captured (no skipped/over-read bytes)
printf '"}}\n' >> "$J"
python3 - "$J" <<'EOF'
import json, sys
open(sys.argv[1],"a").write(json.dumps({"type":"message","id":"z","parentId":None,
  "timestamp":"2026-11-02T00:02:00Z",
  "message":{"role":"user","content":"要做 尾行确认"}})+"\n")
EOF
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null
grep -q '尾行确认' "$L" || fail "record after partial line missed"
# converted logs are restricted and live under FLEET_DIR
PILOG=$(ls "$FLEET_DIR/intake-pi/"*.log | head -1)
[ "$(stat -c %a "$PILOG")" = 600 ] || fail "pi log not 600"
# rotation: truncated file reseeds at EOF, never rescans
: > "$J"; printf '%s\n' '{"type":"message","message":{"role":"user","content":"要做 rotate 前夜"}}' >> "$J"
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null
grep -q 'rotate 前夜' "$L" && fail "rotation rescanned"
printf '%s\n' '{"type":"message","message":{"role":"user","content":"要做 rotate 清晨"}}' >> "$J"
INTAKE_PI_SESSIONS="$T/pi/*.jsonl" "$S" >/dev/null
grep -q 'rotate 清晨' "$L" || fail "post-rotation line missed"
echo "ok: intake-scan"
