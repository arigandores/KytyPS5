#!/bin/bash
# Track F link F47d (HPP-809; ROADMAP s122 item 708 (g), item 714 (b)(2)): ONLY launches one detached call of go_f47d.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_f47d.sh <= 540 s per tool command, separate commands).  Port of F46c
# launch_f46c.sh in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623
# (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the machine rules of next_f47d.py --may
# (order f47_rd -> f47_rd2 when due -> f47_hi; one repeat after NOT_ADMITTED, an interference does not spend it; the lock budget
# <= 45 min, item 708 (g)(4) - exit 7/11/12, a times.txt line, not an attempt), the lock queue (queue_f47d.py: P > F > S and no insert
# between the tags of another series, item 714 (b)(2); QUEUE BUSY => exit 9) and the launch; the one guard scan + hold check of a call is
# in go_f47d.sh right after the lock.  ITEM 661 (b)(1): the first executable line is the form linter form634_check.py --series (FORM634
# FAILED => exit 10).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output
# go_<tag>.out.txt ends with the line rc=<n>.  F47D_DRYRUN=2 stops after the checks; F47D_TIMES / F47D_QUEUE_SKIP=1 / F47D_DISP_SKIP=1 /
# F47D_RUNS (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f47d || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f47d
TM=${F47D_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f47_rd|f47_rd2|f47_hi|f47_rd_r[1-3]|f47_rd2_r[1-3]|f47_hi_r[1-3]) ;;
  *) echo "usage: launch_f47d.sh f47_rd|f47_rd2|f47_hi[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP: $(head -1 $G/SERIES_STOP)"; exit 1; }
MAY=$(python $G/next_f47d.py --may $T --runs ${F47D_RUNS:-$G/runs}); MR=$?
if [ $MR != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d machine rule (next_f47d.py): $MAY - $T not launched (not an attempt)" >> "$TM"
  if [ $MR = 12 ]; then echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $T lock budget (item 708 (g)(4)): $MAY" > $G/SERIES_STOP; fi
  echo "$MAY"; exit $MR
fi
if [ "${F47D_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${F47D_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f47d.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d queue (item 322 (g), 714 (b)(2)): $(echo "$QS" | cut -c1-260) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F47D_DRYRUN:-}" = 2 ] && { echo "dryrun2 $MAY"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f47d.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d previous output of $T moved to f47d/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F47d launch_f47d detached call: bash $G/go_f47d.sh $T" >> "$TM"
F47D_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f47d.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
