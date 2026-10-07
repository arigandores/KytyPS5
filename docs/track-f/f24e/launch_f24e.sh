#!/bin/bash
# Track F link F24e (HPP-664): ONLY launches one detached call of go_f24e.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f24e.sh <= 540 s per tool command, separate commands).  Port of F20l3 launch_f20l3.sh.  A previous output of a refused call
# is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  ITEM 534 (3) (general
# rule 33): guard_f24e.py check (a user emulator or launcher => the block closes, a times.txt line, exit 7) and status (the block must be
# open: two clean checks >= 600 s apart by guard_f24e.py open-block, fewer than 6 tags in it; else exit 8); then the lock queue
# (queue_f24e.py: a ready link of the track P holds it, item 322 (g); QUEUE BUSY => exit 9, a times.txt line); then a TAG line of the block
# and the launch.  F24E_DRYRUN=2 stops after these checks; F24E_GUARD_BLOCK / F24E_GUARD_FAKE / F24E_TIMES / F24E_QUEUE_SKIP=1 (fixtures
# only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f24e
TM=${F24E_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  b13_v|b13_w|b13_v_r[1-3]|b13_w_r[1-3]) ;;
  *) echo "usage: launch_f24e.sh b13_v|b13_w[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GA="--block ${F24E_GUARD_BLOCK:-$G/guard_block.txt}${F24E_GUARD_FAKE:+ --fake $F24E_GUARD_FAKE}"
GS=$(python $G/guard_f24e.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_f24e.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F24E_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f24e.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F24E_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e guard (item 534): $GS; $BS; queue: $(echo "$QS" | cut -c1-200); $(python $G/guard_f24e.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f24e.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e launch_f24e previous output of $T moved to f24e/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F24e launch_f24e detached call: bash $G/go_f24e.sh $T" >> "$TM"
F24E_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f24e.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
