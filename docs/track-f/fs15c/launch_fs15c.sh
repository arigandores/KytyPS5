#!/bin/bash
# Track F link FS15c (HPP-822; ROADMAP s122 item 730 (g)(3)): ONLY launches one detached call of go_fs15c.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_fs15c.sh <= 540 s per tool command, separate commands).  Port of FS14c
# launch_fs14c.sh (by gen_fs15c.py: names moved) in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher -
# only the display (item 623 (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the repeat rule
# (one attempt per tag, item 730 (g)(3); a repeat <tag>_rN only by the lead's item - FS15C_REPEAT_OK=1 is set by the executor after writing
# the times.txt line with the item; without it exit 11), the lock queue (queue_fs15c.py, item 322 (g): P > F > S; QUEUE BUSY => exit 9)
# and the launch; the one guard scan + hold check of a call is in go_fs15c.sh right after the lock.  ITEM 661 (b)(1): the first executable
# line is the form linter form634_check.py --series (FORM634 FAILED => exit 10).  A previous output of a refused call is moved to old/
# before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  FS15C_DRYRUN=2 stops after the checks;
# FS15C_TIMES / FS15C_QUEUE_SKIP=1 / FS15C_DISP_SKIP=1 (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/fs15c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/fs15c
TM=${FS15C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  fs15_v|fs15_w|fs15_z) REP=0;;
  fs15_v_r[1-3]|fs15_w_r[1-3]|fs15_z_r[1-3]) REP=1;;
  *) echo "usage: launch_fs15c.sh fs15_v|fs15_w|fs15_z[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $REP = 1 ]; then
  [ "${FS15C_REPEAT_OK:-}" = 1 ] || { echo "a repeat needs the lead's item and its times.txt line first (item 730 (g)(3), 273 (z)), then FS15C_REPEAT_OK=1"; exit 11; }
fi
if [ "${FS15C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c launch_fs15c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c launch_fs15c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${FS15C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_fs15c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${FS15C_DRYRUN:-}" = 2 ] && { echo "dryrun2 rep $REP"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c launch_fs15c form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_fs15c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c launch_fs15c previous output of $T moved to fs15c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS15c launch_fs15c detached call: bash $G/go_fs15c.sh $T" >> "$TM"
FS15C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_fs15c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
