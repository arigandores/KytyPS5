#!/bin/bash
# Track F link F25m (HPP-680; port of F25m launch_f25m.sh, names moved; the level argument passed through): ONLY launches one detached call of go_f25m.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f25m.sh <= 540 s per tool command, separate commands).  Port of F20e launch_f20e.sh without the FS6b window (item 473 is
# closed).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ITEM 534 (3) (general rule 33): guard_f25m.py check (a user emulator or launcher => the block closes, a times.txt
# line, exit 7) and status (the block must be open: two clean checks >= 600 s apart by guard_f25m.py open-block, fewer than 6 tags in it;
# else exit 8); then the lock queue (queue_f25m.py: F20 is the last in the lock queue, item 462 (g); QUEUE BUSY => exit 9, a times.txt
# line); then a TAG line of the block and the launch.  F25M_DRYRUN=2 stops after these checks; F25M_GUARD_BLOCK / F25M_GUARD_FAKE /
# F25M_TIMES / F25M_QUEUE_SKIP=1 (fixtures only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; LA=${2:-}
G=C:/kyty/f287/f25m
TM=${F25M_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  b36_s[01]|b36_f[01]|b36_k0[1-9]|b36_k1[0-3]|b36_v|b36_w) ;;
  b36_s[01]_r[1-3]|b36_f[01]_r[1-3]|b36_k0[1-9]_r[1-3]|b36_k1[0-3]_r[1-3]|b36_v_r[1-3]|b36_w_r[1-3]) ;;
  restoreA) ;;
  *) echo "usage: launch_f25m.sh <tag> [pot|bonus] | restoreA"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
# SEAL 2 (item 620 (g)(1)): the display must be ON before the launch (exit 6, a times.txt line, not an attempt, no TAG line of the block);
# restoreA does not need it; F25M_DISP_SKIP=1 - fixtures only.
if [ "$T" != restoreA ] && [ "${F25M_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    # User direction 2026-10-07 23:39Z (HPP-680): a display OFF is not a reason to stop - wake it, then check again.
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m launch_f25m display was $DS - wake: $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m launch_f25m display not ON (item 620 (g)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
GA="--block ${F25M_GUARD_BLOCK:-$G/guard_block.txt}${F25M_GUARD_FAKE:+ --fake $F25M_GUARD_FAKE}"
GS=$(python $G/guard_f25m.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_f25m.py check)
if [ $? != 0 ]; then
  python $G/guard_f25m.py close user_session $GA > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
BS=$(python $G/guard_f25m.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F25M_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f25m.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m queue (item 462 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F25M_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m guard (item 534): $GS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f25m.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f25m.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m launch_f25m previous output of $T moved to f25m/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25m launch_f25m detached call: bash $G/go_f25m.sh $T $LA" >> "$TM"
F25M_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f25m.sh $T $LA > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
