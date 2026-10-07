#!/bin/bash
# Track F link FS9c (HPP-673; port of F24e launch_f24e.sh, names moved; + the order check order_fs9c.py with the F25f series, item 604
# (d)(3), before the queue: not FREE => exit 10 and a times.txt line).  Track F link F24e (HPP-664): ONLY launches one detached call of go_f24e.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f24e.sh <= 540 s per tool command, separate commands).  Port of F20l3 launch_f20l3.sh.  A previous output of a refused call
# is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  ITEM 534 (3) (general
# rule 33): guard_fs9c.py check (a user emulator or launcher => the block closes, a times.txt line, exit 7) and status (the block must be
# open: two clean checks >= 600 s apart by guard_fs9c.py open-block, fewer than 6 tags in it; else exit 8); then the lock queue
# (queue_f24e.py: a ready link of the track P holds it, item 322 (g); QUEUE BUSY => exit 9, a times.txt line); then a TAG line of the block
# and the launch.  F24E_DRYRUN=2 stops after these checks; F24E_GUARD_BLOCK / F24E_GUARD_FAKE / F24E_TIMES / F24E_QUEUE_SKIP=1 (fixtures
# only) override the block file, the process list, the times file and the queue check.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/fs9c
TM=${FS9C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  fs9_v|fs9_w|fs9_v_r[1-3]|fs9_w_r[1-3]) ;;
  *) echo "usage: launch_fs9c.sh fs9_v|fs9_w[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GA="--block ${FS9C_GUARD_BLOCK:-$G/guard_block.txt}${FS9C_GUARD_FAKE:+ --fake $FS9C_GUARD_FAKE}"
GS=$(python $G/guard_fs9c.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_fs9c.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
OS=$(python $G/order_fs9c.py)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c order (item 604 (d)(3)): $OS - $T not launched" >> "$TM"
  echo "order: $OS"; exit 10
fi
if [ "${FS9C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_fs9c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${FS9C_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c guard (item 534): $GS; $BS; order: $OS; queue: $(echo "$QS" | cut -c1-200); $(python $G/guard_fs9c.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_fs9c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c launch_fs9c previous output of $T moved to fs9c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS9c launch_fs9c detached call: bash $G/go_fs9c.sh $T" >> "$TM"
FS9C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_fs9c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
