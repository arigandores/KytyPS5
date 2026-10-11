#!/bin/bash
# Track F link F38c (HPP-765; ROADMAP s122 item 691 (d)(4), 695 (g)): ONLY launches one detached call of go_f38c.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_f38c.sh <= 540 s per tool command, separate commands).  Port of FS12c
# launch_fs12c.sh in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623
# (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the repeat rule (one attempt, item 691
# (d)(4); a repeat f25_v_rN only by the lead's item - F38C_REPEAT_OK=1 is set by the executor after writing the times.txt line with the
# item; without it exit 11), the lock queue (queue_f38c.py, item 322 (g): P > F > S; QUEUE BUSY => exit 9) and the launch; the one guard
# scan + hold check of a call is in go_f38c.sh right after the lock.  ITEM 661 (b)(1): the first executable line is the form linter
# form634_check.py --series (FORM634 FAILED => exit 10).  A previous output of a refused call is moved to old/ before the new call (rule
# p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  F38C_DRYRUN=2 stops after the checks; F38C_TIMES /
# F38C_QUEUE_SKIP=1 / F38C_DISP_SKIP=1 (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f38c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f38c
TM=${F38C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f25_v) REP=0;;
  f25_v_r[1-3]) REP=1;;
  *) echo "usage: launch_f38c.sh f25_v[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $REP = 1 ]; then
  [ "${F38C_REPEAT_OK:-}" = 1 ] || { echo "a repeat needs the lead's item and its times.txt line first (item 691 (d)(4), 273 (z)), then F38C_REPEAT_OK=1"; exit 11; }
fi
if [ "${F38C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c launch_f38c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c launch_f38c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${F38C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f38c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F38C_DRYRUN:-}" = 2 ] && { echo "dryrun2 rep $REP"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c launch_f38c form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f38c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c launch_f38c previous output of $T moved to f38c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F38c launch_f38c detached call: bash $G/go_f38c.sh $T" >> "$TM"
F38C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f38c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
