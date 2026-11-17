#!/usr/bin/env bash
# fleet watcher（通用，不限夜班）：状态迁移时 hc send 通知 FLEET_BOSS；每 10 分钟快照进 status.log
#
# env 契约：
#   FLEET_DIR   盘面目录，默认 /home/liz/radar-run/fleet；npd 班次传 npd-loop-YYYY-MM-DD/
#   FLEET_BOSS     默认通知端点（hc 地址）；不设则只落日志不发消息
#   FLEET_BOSS_MAP 分群路由 "cwd前缀=hc地址;..."：t* 迁移/消失通知按终端 cwd 最长前缀投递，
#                  未命中回落 FLEET_BOSS；job/tmux/reports/guard 等全局项只走 FLEET_BOSS。
#                  例：FLEET_BOSS_MAP="/home/liz/dev/cfe-app=t288;/home/liz/dev/shelf-radar=t287"
#   域/包工头解析：fleet-boss <域>（同目录）——卡片汇报写 `hc send "$(fleet-boss cfe)"`，
#                  换届自动跟随当期 *boss* 终端，不要硬编码 tXXX
#   EXCLUDE     逗号或空白分隔的 hc 地址：不进 .cur-state、不参与迁移通知（本班 boss+外班）
#
# 产物（均在 $FLEET_DIR/）：.cur-state 上轮快照、notify-state.txt 已报基线、
#   status.log NOTIFY 行+10 分钟全量快照、.watchdog.lock 单实例 flock
# 起：tmux new-session -d -s fleet-watch "set -a; . <repo>/fleet.env; exec bash <repo>/watchdog.sh"
#   （FLEET_DIR/FLEET_BOSS/FLEET_BOSS_MAP/EXCLUDE 四件套收在 <repo>/fleet.env——换班/加域改这一份）
# 停：tmux kill-session -t fleet-watch（watchdog 是窗格主进程；别在窗格里 C-c，会话即死）
# 派生入口：fleet-spawn（同目录）——kind/name/--cwd/--model/--no-parent，自动带 bypass flag + herdr.space label
FLEET=${FLEET_DIR:-/home/liz/radar-run/fleet}
exec 9>"$FLEET/.watchdog.lock"
flock -n 9 || { echo "watchdog: $FLEET 已有 watcher 在跑" >&2; exit 1; }
STATE=$FLEET/notify-state.txt
LOG=$FLEET/status.log
touch "$STATE"
snap=0
# EXCLUDE 归一化成空格串：消失项检查跳过被排终端（换 EXCLUDE 不再误报 gone）
EXCL=" $(printf '%s' "${EXCLUDE:-}" | tr -s '[:space:],' ' ') "

notify() {
  # $1=消息 $2=终端 cwd（可选）：FLEET_BOSS_MAP 最长前缀命中投递，否则回落 FLEET_BOSS；
  # 实际收件人写进 NOTIFY 行便于审计路由
  local msg="$1" cwd="${2:-}" to="${FLEET_BOSS:-}"
  local pair pre addr best="" bestlen=-1
  if [ -n "${FLEET_BOSS_MAP:-}" ] && [ -n "$cwd" ]; then
    for pair in $(printf '%s' "$FLEET_BOSS_MAP" | tr -d '[:space:]' | tr ';' ' '); do
      pre="${pair%%=*}"; addr="${pair##*=}"
      case "$cwd" in "$pre"*)
        [ ${#pre} -gt "$bestlen" ] && { best="$addr"; bestlen=${#pre}; } ;;
      esac
    done
    [ -n "$best" ] && to="$best"
  fi
  echo "$(date '+%m-%d %H:%M:%S') NOTIFY [$to] $msg" >> "$LOG"
  if [ -n "$to" ]; then
    if ! hc send "$to" "fleet-notify: $msg" >/dev/null 2>&1; then
      echo "$(date '+%m-%d %H:%M:%S') NOTIFY-FAIL [$to] $msg" >> "$LOG"
      sleep 2
      hc send "$to" "fleet-notify: $msg" >/dev/null 2>&1 || \
        echo "$(date '+%m-%d %H:%M:%S') NOTIFY-FAIL2 [$to] $msg" >> "$LOG"
    fi
  fi
}

while true; do
  now=$FLEET/.cur-state
  : > "$now"
  # 1) herdr-core 终端状态（跳过无 status 的纯 shell 和自己）
  hc ls --json 2>/dev/null | python3 -c "
import json,sys,os
skip=set(('t14','t19','t7')+tuple(os.environ.get('EXCLUDE','').replace(',',' ').split()))
for t in json.load(sys.stdin).get('terminals',[]):
    a=t['address']
    if a in skip: continue
    st=t.get('status') or ''
    if st: print(f'{a}\t{st}\t{t.get(\"cwd\") or \"\"}')" >> "$now" 2>/dev/null
  # 1.5) 挂载守卫 + YOLO 审计（不靠 agent 记性；动作才通知）
  python3 "$(dirname "$0")/fleet-guard.py" "$FLEET" 2>/dev/null | while IFS=$'\t' read -r gc g; do
    if [ -z "$g" ]; then g="$gc"; gc=""; fi
    [ -n "$g" ] && notify "guard: $g" "$gc"
  done
  # 2) 老 herdr wash-foreman
  s=$(herdr --session default pane list 2>/dev/null | python3 -c "import json,sys;p=[x for x in json.load(sys.stdin)['result']['panes'] if x['pane_id']=='w6:p39'];print(p[0]['agent_status'] if p else 'gone')" 2>/dev/null)
  echo "wash-foreman	${s:-dead}" >> "$now"
  s2=$(herdr --session default pane list 2>/dev/null | python3 -c "import json,sys;p=[x for x in json.load(sys.stdin)['result']['panes'] if x['pane_id']!='w6:p39'];print(','.join(x['pane_id']+':'+x.get('agent_status','?') for x in p) if p else 'none')" 2>/dev/null)
  echo "legacy-others	${s2:-none}" >> "$now"
  # 3) 采集任务 progress.json 的 status 字段 + mtime
  for f in /home/liz/radar-run/*/progress.json; do
    d=$(basename $(dirname "$f"))
    st=$(python3 -c "import json;print(json.load(open('$f')).get('status','?'))" 2>/dev/null)
    mt=$(stat -c %Y "$f" 2>/dev/null)
    echo "job:$d	$st:$mt" >> "$now"
  done
  # 4) tmux 会话清单
  tmux ls 2>/dev/null | cut -d: -f1 | while read s; do echo "tmux:$s	live"; done >> "$now"
  # 5) fleet 报告文件数
  n=$(ls $FLEET/receipts/*.md 2>/dev/null | wc -l); echo "reports	$n" >> "$now"

  # 比对：逐行 diff，迁移才报（key 用固定串匹配；t* 行第三列是 cwd 供分群路由，旧 state 两列兼容）
  while IFS=$'\t' read -r k v c; do
    [ -z "$k" ] && continue
    old=$(grep -F "$k"$'\t' "$STATE" | head -1 | cut -f2)
    if [ "$v" != "$old" ]; then
      case "$k" in
        t*|wash-foreman)
          # working->done/idle/blocked 才报；blocked 每次都报；dead 需首见豁免
          if [[ "$v" == blocked || ("$old" == working && "$v" =~ ^(done|idle)$) || ( -n "$old" && "$old" != "$v" && "$v" == dead ) ]]; then
            notify "$k: ${old:-none} -> $v" "$c"
          fi ;;
        job:*)
          jn=${k#job:}; os=${old%%:*}; ns=${v%%:*}
          # 首见豁免：state 重建/换盘面时不回放存量 job
          [ -n "$old" ] && [ "$os" != "$ns" ] && notify "$jn status: ${os:-?} -> $ns" ;;
        tmux:*)
          [ -z "$old" ] && [ "$v" = live ] && notify "tmux session up: ${k#tmux:}" ;;
        reports)
          [ "${old:-0}" != "$v" ] && [ -n "$old" ] && notify "new receipt in fleet/ ($(ls -t $FLEET/receipts/*.md 2>/dev/null | head -1 | xargs basename))" ;;
      esac
    fi
  done < "$now"
  # 消失项：tmux 死了要报；t* 终端被杀也要报，但 hc ls 整轮失败时 .cur-state 无 t* 行，
  # 那是「查不到」不是「全灭」，跳过避免误报风暴
  nt_now=$(grep -cP '^t[0-9a-z]+\t' "$now")
  nt_old=$(grep -cP '^t[0-9a-z]+\t' "$STATE")
  hc_dead=0; [ "$nt_now" -eq 0 ] && [ "$nt_old" -gt 0 ] && hc_dead=1
  while IFS=$'\t' read -r k v c; do
    grep -qF "$k"$'\t' "$now" || {
      case "$k" in
        tmux:*) notify "tmux session died: ${k#tmux:}" ;;
        # 只报干活中/卡住中消失的；done/idle 收工退出不算事故；EXCLUDE 里的不算消失
        t*)    [ "$hc_dead" = 0 ] && [[ "$v" =~ ^(working|blocked)$ ]] && [[ "$EXCL" != *" $k "* ]] && notify "$k gone mid-$v" "$c" ;;
      esac
    }
  done < "$STATE"

  cp "$now" "$STATE"

  # 每 10 分钟落一次完整快照
  if [ $((snap % 10)) -eq 0 ]; then
    {
      echo "===== $(date '+%Y-%m-%d %H:%M:%S') ====="
      cat "$now" | sed 's/^/  /'
      df -h /home /tmp | tail -2 | awk '{print "  "$1" "$5" used"}'
      echo
    } >> "$LOG"
  fi
  snap=$((snap+1))
  sleep 60
done
