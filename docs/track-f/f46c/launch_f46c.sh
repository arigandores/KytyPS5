#!/bin/bash
# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g), 711, 714, 716): ONLY launches one detached call of go_f46c.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_f46c.sh <= 540 s per tool command, separate commands).  Port of F44c
# launch_f44c.sh in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623
# (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the machine rules of next_f46c.py --may
# (order of item 702 (g)(2); the repeat _r1 after NOT_ADMITTED, _r2/_r3 only with F46C_REPEAT_OK=1 set after the times.txt line of the
# lead's item; the event rule of the tint tags, item 711 (b)(1); the lock budget <= 150 min, item 716 - exit 7/8/11/12, a times.txt line,
# not an attempt), the lock queue (queue_f46c.py, item 322 (g): P > F > S; QUEUE BUSY => exit 9; inside F by readiness, item 714) and the
# launch; the one guard scan + hold check of a call is in go_f46c.sh right after the lock.  ITEM 661 (b)(1): the first executable line
# is the form linter form634_check.py --series (FORM634 FAILED => exit 10).  A previous output of a refused call is moved to old/ before
# the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  F46C_DRYRUN=2 stops after the checks;
# F46C_TIMES / F46C_QUEUE_SKIP=1 / F46C_DISP_SKIP=1 / F46C_RUNS (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f46c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f46c
TM=${F46C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f26s_0|f26s_1|f26s_1b|f26s_t[1-4]|f26s_c[1-4]|f26s_0_r[1-3]|f26s_1_r[1-3]|f26s_1b_r[1-3]|f26s_t[1-4]_r[1-3]|f26s_c[1-4]_r[1-3]) ;;
  *) echo "usage: launch_f46c.sh f26s_0|f26s_1|f26s_1b|f26s_t<k>|f26s_c<k>[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ -e $G/SERIES_STOP ] && { echo "SERIES_STOP: $(head -1 $G/SERIES_STOP)"; exit 1; }
MAY=$(python $G/next_f46c.py --may $T --runs ${F46C_RUNS:-$G/runs}); MR=$?
if [ $MR != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c machine rule (next_f46c.py): $MAY - $T not launched (not an attempt)" >> "$TM"
  if [ $MR = 12 ]; then echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $T lock budget (item 716): $MAY" > $G/SERIES_STOP; fi
  echo "$MAY"; exit $MR
fi
if [ "${F46C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${F46C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f46c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F46C_DRYRUN:-}" = 2 ] && { echo "dryrun2 $MAY"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f46c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c previous output of $T moved to f46c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F46c launch_f46c detached call: bash $G/go_f46c.sh $T" >> "$TM"
F46C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f46c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
