#!/bin/bash
# Track F link F25f (HPP-669; port of F25f launch_f25f.sh, names moved; the level argument passed through): ONLY launches one detached call of go_f25f.sh <tag> [pot|bonus] (process rule p.324(i): the launcher only launches, the
# wait is wait_f25f.sh <= 540 s per tool command, separate commands).  Port of F20e launch_f20e.sh without the FS6b window (item 473 is
# closed).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ITEM 534 (3) (general rule 33): guard_f25f.py check (a user emulator or launcher => the block closes, a times.txt
# line, exit 7) and status (the block must be open: two clean checks >= 600 s apart by guard_f25f.py open-block, fewer than 6 tags in it;
# else exit 8); then the lock queue (queue_f25f.py: F20 is the last in the lock queue, item 462 (g); QUEUE BUSY => exit 9, a times.txt
# line); then a TAG line of the block and the launch.  F25F_DRYRUN=2 stops after these checks; F25F_GUARD_BLOCK / F25F_GUARD_FAKE /
# F25F_TIMES / F25F_QUEUE_SKIP=1 (fixtures only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; LA=${2:-}
G=C:/kyty/f287/f25f
TM=${F25F_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f25_c[12]|f25_z[12]|f25_p[bc]|f25_s0[1-9]|f25_s[1-3][0-9]|f25_s40|f25_k0[1-9]|f25_k10) ;;
  f25_c[12]_r[1-6]|f25_z[12]_r[1-6]|f25_p[bc]_r[1-6]|f25_s0[1-9]_r[1-6]|f25_s[1-3][0-9]_r[1-6]|f25_s40_r[1-6]|f25_k0[1-9]_r[1-6]|f25_k10_r[1-6]) ;;
  restoreA) ;;
  *) echo "usage: launch_f25f.sh <tag> [pot|bonus] | restoreA"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GA="--block ${F25F_GUARD_BLOCK:-$G/guard_block.txt}${F25F_GUARD_FAKE:+ --fake $F25F_GUARD_FAKE}"
GS=$(python $G/guard_f25f.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_f25f.py check)
if [ $? != 0 ]; then
  python $G/guard_f25f.py close user_session $GA > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
BS=$(python $G/guard_f25f.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F25F_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f25f.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f queue (item 462 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F25F_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f guard (item 534): $GS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f25f.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f25f.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f launch_f25f previous output of $T moved to f25f/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f launch_f25f detached call: bash $G/go_f25f.sh $T $LA" >> "$TM"
F25F_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f25f.sh $T $LA > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
