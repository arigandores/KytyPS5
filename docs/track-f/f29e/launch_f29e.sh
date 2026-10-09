#!/bin/bash
# Track F link F29e (HPP-704; port of F25m launch_f25m.sh, names moved, no level argument): ONLY launches one detached call of
# go_f29e.sh <tag> (process rule p.324(i): the launcher only launches, the wait is wait_f29e.sh <= 540 s per tool command, separate
# commands).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  Item 623 (v)(1): a display OFF is woken (dispstate.py --wake) and checked again; still OFF => exit 6 and a
# times.txt line (not an attempt).  ITEM 534 (3) (general rule 33): guard_f29e.py check (a user emulator or launcher => the block closes,
# exit 7), hold_f29e.py check (a user session, item 606 (v)(1) => the block closes, exit 7) and status (the block must be open: two clean
# checks >= 600 s apart by guard_f29e.py open-block, fewer than 6 tags in it; else exit 8); then the lock queue (queue_f29e.py, item
# 322 (g): P > F > S; QUEUE BUSY => exit 9); then a TAG line of the block and the launch.  F29E_DRYRUN=2 stops after these checks;
# F29E_GUARD_BLOCK / F29E_GUARD_FAKE / F29E_TIMES / F29E_QUEUE_SKIP=1 / F29E_DISP_SKIP=1 (fixtures only).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f29e
TM=${F29E_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  b12_v|b12_w|b12_v_r[1-3]|b12_w_r[1-3]) ;;
  *) echo "usage: launch_f29e.sh b12_v|b12_w[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ "${F29E_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e launch_f29e display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e launch_f29e display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
GA="--block ${F29E_GUARD_BLOCK:-$G/guard_block.txt}${F29E_GUARD_FAKE:+ --fake $F29E_GUARD_FAKE}"
GS=$(python $G/guard_f29e.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_f29e.py check)
if [ $? != 0 ]; then
  python $G/guard_f29e.py close user_session $GA > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
BS=$(python $G/guard_f29e.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F29E_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f29e.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F29E_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e guard (item 534): $GS; $HS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f29e.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f29e.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e launch_f29e previous output of $T moved to f29e/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F29e launch_f29e detached call: bash $G/go_f29e.sh $T" >> "$TM"
F29E_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f29e.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
