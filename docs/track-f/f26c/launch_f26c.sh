#!/bin/bash
# Track F link F26c (HPP-692; port of FS10c launch_fs10c.sh, names moved, tags b25_NN): ONLY launches one detached call of go_f26c.sh <tag>
# (process rule p.324(i): the launcher only launches, the wait is wait_f26c.sh <= 540 s per tool command, separate commands).  A previous
# output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.
# Item 623 (v)(1): a display OFF is woken and checked again; still OFF => exit 6.  Item 534 (3) (general rule 33): guard check (exit 7),
# hold check (exit 7), block status (two clean checks >= 600 s apart, fewer than 10 tags in it - item 630 (d)(3); else exit 8); the lock
# queue P > F > S (queue_f26c.py; QUEUE BUSY => exit 9); a TAG line of the block and the launch.  Modes base / return skip the block and the
# TAG line (no game).  F26C_DRYRUN=2 stops after the checks.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f26c
TM=${F26C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  base|return) GAMETAG=0;;
  b25_0[1-9]|b25_[1-4][0-9]|b25_5[0-5]) GAMETAG=1;;
  *) echo "usage: launch_f26c.sh base | b25_01..b25_55 | return"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $GAMETAG = 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c launch_f26c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c launch_f26c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
GS=$(python $G/guard_f26c.py check)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
HS=$(python $G/hold_f26c.py check)
if [ $? != 0 ]; then
  python $G/guard_f26c.py close user_session > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c hold (item 606 (v)(1)): $HS - block closed, $T not launched (not an attempt)" >> "$TM"
  echo "user session: $HS"; exit 7
fi
if [ $GAMETAG = 1 ]; then
  BS=$(python $G/guard_f26c.py status)
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
    echo "$BS"; exit 8
  fi
else
  BS="mode $T (no game, no block tag)"
fi
QS=$(python $G/queue_f26c.py 2>&1 | tr '\n' ';')
if ! echo "$QS" | grep -q 'QUEUE FREE'; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
  echo "queue busy: $QS"; exit 9
fi
[ "${F26C_DRYRUN:-}" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
if [ $GAMETAG = 1 ]; then TL=$(python $G/guard_f26c.py tag $T); else TL="-"; fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c guard (item 534): $GS; $HS; $BS; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); $TL" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f26c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c launch_f26c previous output of $T moved to f26c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F26c launch_f26c detached call: bash $G/go_f26c.sh $T" >> "$TM"
F26C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f26c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
