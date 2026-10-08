#!/bin/bash
# Track F link FS10c (HPP-686; port of F25m launch_f25m.sh, names moved, no level argument): ONLY launches one detached call of
# go_fs10c.sh <tag> (process rule p.324(i): the launcher only launches, the wait is wait_fs10c.sh <= 540 s per tool command, separate
# commands).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  Item 623 (v)(1): a display OFF is woken (dispstate.py --wake) and checked again; still OFF => exit 6 and a
# times.txt line (not an attempt).  ITEM 534 (3) (general rule 33): guard_fs10c.py check (a user emulator or launcher => the block closes,
# exit 7), hold_fs10c.py check (a user session, item 606 (v)(1) => the block closes, exit 7) and status (the block must be open: two clean
# checks >= 600 s apart by guard_fs10c.py open-block, fewer than 6 tags in it; else exit 8); then the lock queue (queue_fs10c.py, item
# 322 (g): P > F > S; QUEUE BUSY => exit 9); then a TAG line of the block and the launch.  FS10C_DRYRUN=2 stops after these checks;
# FS10C_GUARD_BLOCK / FS10C_GUARD_FAKE / FS10C_TIMES / FS10C_QUEUE_SKIP=1 / FS10C_DISP_SKIP=1 (fixtures only).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/fs10c
TM=${FS10C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  fs10_s[01]|fs10_f1|fs10_v|fs10_w|fs10_s[01]_r[1-3]|fs10_f1_r[1-3]|fs10_v_r[1-3]|fs10_w_r[1-3]) ;;
  *) echo "usage: launch_fs10c.sh fs10_s1|fs10_s0|fs10_f1|fs10_v|fs10_w[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ "${FS10C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c launch_fs10c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c launch_fs10c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
GA="--block ${FS10C_GUARD_BLOCK:-$G/guard_block.txt}${FS10C_GUARD_FAKE:+ --fake $FS10C_GUARD_FAKE}"
GS=$(python $G/guard_fs10c.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_fs10c.py check)
if [ $? != 0 ]; then
  python $G/guard_fs10c.py close user_session $GA > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
BS=$(python $G/guard_fs10c.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${FS10C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_fs10c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${FS10C_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c guard (item 534): $GS; $HS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_fs10c.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_fs10c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c launch_fs10c previous output of $T moved to fs10c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS10c launch_fs10c detached call: bash $G/go_fs10c.sh $T" >> "$TM"
FS10C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_fs10c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
