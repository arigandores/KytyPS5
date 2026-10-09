#!/bin/bash
# Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)): the F30f (HPP-711) file with the names moved (f30f -> f30m, HPP-711 ->
# HPP-723, F30F_ -> F30M_) and the tag set of item 655 (e)(2)-(3): f30_s<1..9>_c5, f30_cy_v, f30_cy_c3, f30_cy_c4 [_r1.._r3].
# Track F link F30m (HPP-723): the F29e file with the names and the tag set moved (f29e -> f30m, HPP-704 -> HPP-723); no change of meaning.
# Track F link F30m (HPP-723; port of F25m launch_f25m.sh, names moved, no level argument): ONLY launches one detached call of
# go_f30m.sh <tag> (process rule p.324(i): the launcher only launches, the wait is wait_f30m.sh <= 540 s per tool command, separate
# commands).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  Item 623 (v)(1): a display OFF is woken (dispstate.py --wake) and checked again; still OFF => exit 6 and a
# times.txt line (not an attempt).  ITEM 534 (3) (general rule 33): guard_f30m.py check (a user emulator or launcher => the block closes,
# exit 7), hold_f30m.py check (a user session, item 606 (v)(1) => the block closes, exit 7) and status (the block must be open: two clean
# checks >= 600 s apart by guard_f30m.py open-block, fewer than 6 tags in it; else exit 8); then the lock queue (queue_f30m.py, item
# 322 (g): P > F > S; QUEUE BUSY => exit 9); then a TAG line of the block and the launch.  F30M_DRYRUN=2 stops after these checks;
# F30M_GUARD_BLOCK / F30M_GUARD_FAKE / F30M_TIMES / F30M_QUEUE_SKIP=1 / F30M_DISP_SKIP=1 (fixtures only).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f30m
TM=${F30M_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f30_s[1-9]_c5|f30_cy_v|f30_cy_c3|f30_cy_c4) ;;
  f30_s[1-9]_c5_r[1-3]|f30_cy_v_r[1-3]|f30_cy_c3_r[1-3]|f30_cy_c4_r[1-3]) ;;
  *) echo "usage: launch_f30m.sh <f30_s<1..9>_c5 | f30_cy_v | f30_cy_c3 | f30_cy_c4>[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ "${F30M_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m launch_f30m display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m launch_f30m display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
GA="--block ${F30M_GUARD_BLOCK:-$G/guard_block.txt}${F30M_GUARD_FAKE:+ --fake $F30M_GUARD_FAKE}"
GS=$(python $G/guard_f30m.py check $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_f30m.py check)
if [ $? != 0 ]; then
  python $G/guard_f30m.py close user_session $GA > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
BS=$(python $G/guard_f30m.py status $GA)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
if [ "${F30M_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f30m.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F30M_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m guard (item 534): $GS; $HS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $(python $G/guard_f30m.py tag $T $GA)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f30m.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m launch_f30m previous output of $T moved to f30m/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30m launch_f30m detached call: bash $G/go_f30m.sh $T" >> "$TM"
F30M_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f30m.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
