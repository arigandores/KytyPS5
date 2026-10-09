#!/bin/bash
# Track F link F31c (HPP-731; ROADMAP s122 item 667 (d)): ONLY launches one detached call of go_f31c.sh <tag> (process rule p.324(i): the
# launcher only launches, the wait is wait_f31c.sh <= 540 s per tool command, separate commands).  Port of F26c launch_f26c.sh in the form
# of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623 (v)(1): OFF is woken and checked
# again; still OFF => exit 6, a times.txt line, not an attempt), the lock queue (queue_f31c.py, item 322 (g): P > F > S; QUEUE BUSY =>
# exit 9) and the launch; the one guard scan + hold check of a call is in go_f31c.sh right after the lock.  ITEM 661 (b)(1): the first
# executable line is the form linter form634_check.py --series (FORM634 FAILED => exit 10: no lock, no files, not an attempt).  A previous
# output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.
# Modes base / return skip the display.  F31C_DRYRUN=2 stops after the checks; F31C_TIMES / F31C_QUEUE_SKIP=1 / F31C_DISP_SKIP=1
# (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f31c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f31c
TM=${F31C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  base|return) GAMETAG=0;;
  b25m_0[1-9]|b25m_[12][0-9]|b25m_3[0-6]) GAMETAG=1;;
  *) echo "usage: launch_f31c.sh base | b25m_01..b25m_36 | return"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $GAMETAG = 1 ] && [ "${F31C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c launch_f31c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c launch_f31c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${F31C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f31c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F31C_DRYRUN:-}" = 2 ] && { echo "dryrun2"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c launch_f31c form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f31c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c launch_f31c previous output of $T moved to f31c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F31c launch_f31c detached call: bash $G/go_f31c.sh $T" >> "$TM"
F31C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f31c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
