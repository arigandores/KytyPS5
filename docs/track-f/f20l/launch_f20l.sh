#!/bin/bash
# Track F link F20l (HPP-631): ONLY launches one detached call of go_f20l.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f20l.sh <= 540 s per tool command, separate commands).  Port of F20e launch_f20e.sh without the FS6b window (item 473 is
# closed).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ITEM 534 (3) (general rule 33): guard_f20l.py check (a user emulator or launcher => the block closes, a times.txt
# line, exit 7) and status (the block must be open: two clean checks >= 600 s apart by guard_f20l.py open-block, fewer than 6 tags in it;
# else exit 8); then the lock queue (queue_f20l.py: F20 is the last in the lock queue, item 462 (g); QUEUE BUSY => exit 9, a times.txt
# line); then a TAG line of the block and the launch.  F20L_DRYRUN=2 stops after these checks; F20L_GUARD_BLOCK / F20L_GUARD_FAKE /
# F20L_TIMES / F20L_QUEUE_SKIP=1 (fixtures only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f20l
TM=${F20L_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  b32_z0|b32_pp|b32_pc|b32_pd|b32_pd2|b32_z0_r[1-6]|b32_pp_r[1-6]|b32_pc_r[1-6]|b32_pd_r[1-6]|b32_pd2_r[1-6]) ;;
  *) echo "usage: launch_f20l.sh b32_z0|b32_pp|b32_pc|b32_pd|b32_pd2[_r1..6]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GA="--block ${F20L_GUARD_BLOCK:-$G/guard_block.txt}${F20L_GUARD_FAKE:+ --fake $F20L_GUARD_FAKE}"
GS=$(python $G/guard_f20l.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_f20l.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F20L_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f20l.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l queue (item 462 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F20L_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l guard (item 534): $GS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f20l.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f20l.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l launch_f20l previous output of $T moved to f20l/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l launch_f20l detached call: bash $G/go_f20l.sh $T" >> "$TM"
nohup bash -c "bash $G/go_f20l.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
