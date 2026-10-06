#!/bin/bash
# Track F link F20l3 (HPP-655): ONLY launches one detached call of go_f20l3.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f20l3.sh <= 540 s per tool command, separate commands).  Port of F20e launch_f20e.sh without the FS6b window (item 473 is
# closed).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ITEM 534 (3) (general rule 33): guard_f20l3.py check (a user emulator or launcher => the block closes, a times.txt
# line, exit 7) and status (the block must be open: two clean checks >= 600 s apart by guard_f20l3.py open-block, fewer than 6 tags in it;
# else exit 8); then the lock queue (queue_f20l3.py: F20 is the last in the lock queue, item 462 (g); QUEUE BUSY => exit 9, a times.txt
# line); then a TAG line of the block and the launch.  F20L3_DRYRUN=2 stops after these checks; F20L3_GUARD_BLOCK / F20L3_GUARD_FAKE /
# F20L3_TIMES / F20L3_QUEUE_SKIP=1 (fixtures only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f20l3
TM=${F20L3_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  b32_pa|b32_pa2|b32_s0[1-9]|b32_s[1-5][0-9]|b32_s60|b32_z0c[1-5]) ;;
  b32_pa_r[1-6]|b32_pa2_r[1-6]|b32_s0[1-9]_r[1-6]|b32_s[1-5][0-9]_r[1-6]|b32_s60_r[1-6]|b32_z0c[1-5]_r[1-6]) ;;
  *) echo "usage: launch_f20l3.sh b32_pa|b32_pa2|b32_s01..b32_s60|b32_z0c1..b32_z0c5[_r1..6]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GA="--block ${F20L3_GUARD_BLOCK:-$G/guard_block.txt}${F20L3_GUARD_FAKE:+ --fake $F20L3_GUARD_FAKE}"
GS=$(python $G/guard_f20l3.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_f20l3.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F20L3_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f20l3.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 queue (item 462 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F20L3_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 guard (item 534): $GS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f20l3.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f20l3.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 launch_f20l3 previous output of $T moved to f20l3/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20l3 launch_f20l3 detached call: bash $G/go_f20l3.sh $T" >> "$TM"
F20L3_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f20l3.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
