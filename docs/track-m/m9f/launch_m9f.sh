#!/bin/bash
# Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(5)): ONLY launches one detached call of go_m9f.sh <tag> (port of M9f
# launch_m9f.sh, HPP-850; the queue is queue_m9f.py: M3a2 HPP-861 ready => QUEUE BUSY, item 785 (v)(5)) (process rule p.324(i): the
# launcher only launches, the wait is wait_m9f.sh <= 540 s per tool command, separate commands).  Port of M3a launch_m3a.sh in the form
# of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623 (v)(1): OFF is woken and
# checked again; still OFF => exit 6, a times.txt line, not an attempt), the repeat rule (one attempt per tag; a repeat <tag>_rN only after
# an interference - a window event is an interference and the tag is repeated (item 785 (v)(5), form V M9f) - M9F_REPEAT_OK=1 is set by the executor
# after writing the times.txt line with the reason; without it exit 11), the tag check by the dry run of go_m9f.sh (an unknown tag - exit
# 2), the lock queue (queue_m9f.py: a ready link of track P or M3a2 HPP-861 holds it; QUEUE BUSY => exit 9) and the launch; the one guard scan + hold check
# of a call is in go_m9f.sh right after the lock.  ITEM 661 (b)(1): the first executable line is the form linter form634_check.py --series
# (FORM634 FAILED => exit 10).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output
# go_<tag>.out.txt ends with the line rc=<n>.  M9F_DRYRUN=2 stops after the checks; M9F_TIMES / M9F_QUEUE_SKIP=1 / M9F_DISP_SKIP=1
# (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/m657/m9f || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/m657/m9f
TM=${M9F_TIMES:-$G/times.txt}
PLAN=$(M9F_DRYRUN=1 bash $G/go_m9f.sh "$T" 2>/dev/null | grep '^dryrun ')
[ -n "$PLAN" ] || { echo "usage: launch_m9f.sh <t188_sg2|t188_hb2|t188_mg2>[_r1..3]"; exit 2; }
case "$T" in *_r[1-3]) REP=1;; *) REP=0;; esac
[ -e C:/kyty/m657/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $REP = 1 ]; then
  [ "${M9F_REPEAT_OK:-}" = 1 ] || { echo "a repeat needs the times.txt line with the reason first (item 785 (v)(5): window event), then M9F_REPEAT_OK=1"; exit 11; }
fi
if [ "${M9F_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f launch_m9f display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f launch_m9f display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${M9F_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_m9f.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${M9F_DRYRUN:-}" = 2 ] && { echo "dryrun2 rep $REP plan $PLAN"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f launch_m9f form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T; plan: $(echo "$PLAN" | cut -c1-260)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_m9f.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f launch_m9f previous output of $T moved to m9f/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M9f launch_m9f detached call: bash $G/go_m9f.sh $T" >> "$TM"
M9F_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_m9f.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
