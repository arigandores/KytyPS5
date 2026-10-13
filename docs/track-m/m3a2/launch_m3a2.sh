#!/bin/bash
# Track M link M3a2 (HPP-861; ROADMAP s122 item 778 (d)(8)): port of M3a2 launch_m3a2.sh (HPP-861) - plus the theme arm rule: a tag
# *_t1250* / *_t3060* (a theme arm of seal section 6) needs the lead's item and its times.txt line first, then M3A2_ARM_OK=1 (exit 12).
# Text of M3a2 below.  ONLY launches one detached call of go_m3a2.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_m3a2.sh <= 540 s per tool command, separate commands).  Port of FS15c
# launch_fs15c.sh in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623
# (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the repeat rule (one attempt per tag;
# a repeat <tag>_rN only by the lead's item - M3A2_REPEAT_OK=1 is set by the executor after writing the times.txt line with the item;
# without it exit 11), the tag check by the dry run of go_m3a2.sh (an unknown tag - exit 2), the lock queue (queue_m3a2.py: a ready link
# of track P holds it; QUEUE BUSY => exit 9) and the launch; the one guard scan + hold check of a call is in go_m3a2.sh right after the
# lock.  ITEM 661 (b)(1): the first executable line is the form linter form634_check.py --series (FORM634 FAILED => exit 10).  A
# previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the
# line rc=<n>.  M3A2_DRYRUN=2 stops after the checks; M3A2_TIMES / M3A2_QUEUE_SKIP=1 / M3A2_DISP_SKIP=1 (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/m657/m3a2 || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/m657/m3a2
TM=${M3A2_TIMES:-$G/times.txt}
PLAN=$(M3A2_DRYRUN=1 bash $G/go_m3a2.sh "$T" 2>/dev/null | grep '^dryrun ')
[ -n "$PLAN" ] || { echo "usage: launch_m3a2.sh <tag of the seal section 3>[_r1..3]"; exit 2; }
case "$T" in *_r[1-3]) REP=1;; *) REP=0;; esac
[ -e C:/kyty/m657/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
case "$T" in *_t1250*|*_t3060*)
  [ "${M3A2_ARM_OK:-}" = 1 ] || { echo "a theme arm needs the lead's item and its times.txt line first (seal section 6), then M3A2_ARM_OK=1"; exit 12; };;
esac
if [ $REP = 1 ]; then
  [ "${M3A2_REPEAT_OK:-}" = 1 ] || { echo "a repeat needs the lead's item and its times.txt line first (item 273 (z)), then M3A2_REPEAT_OK=1"; exit 11; }
fi
if [ "${M3A2_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 launch_m3a2 display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 launch_m3a2 display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${M3A2_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_m3a2.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${M3A2_DRYRUN:-}" = 2 ] && { echo "dryrun2 rep $REP plan $PLAN"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 launch_m3a2 form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T; plan: $(echo "$PLAN" | cut -c1-260)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_m3a2.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 launch_m3a2 previous output of $T moved to m3a2/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) M3a2 launch_m3a2 detached call: bash $G/go_m3a2.sh $T" >> "$TM"
M3A2_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_m3a2.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
