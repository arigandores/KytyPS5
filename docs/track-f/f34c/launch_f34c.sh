#!/bin/bash
# Track F link F34c (HPP-740; ROADMAP s122 item 673 (z)(2), 674, 676): ONLY launches one detached call of go_f34c.sh <tag> (process rule
# p.324(i): the launcher only launches, the wait is wait_f34c.sh <= 540 s per tool command, separate commands).  Port of F31c
# launch_f31c.sh in the form of item 634 / 660 (d)(1): no guard, no hold check, no block in the launcher - only the display (item 623
# (v)(1): OFF is woken and checked again; still OFF => exit 6, a times.txt line, not an attempt), the repeat cap of item 676 (l) (a repeat
# <tag>_rN needs its times.txt line with the member-ground first - F34C_REPEAT_OK=1 is set by the executor after writing it; the cap of the
# series is 4 started repeats: the fifth is refused, exit 11), the lock queue (queue_f34c.py, item 322 (g): P > F > S; QUEUE BUSY => exit 9)
# and the launch; the one guard scan + hold check of a call is in go_f34c.sh right after the lock.  ITEM 661 (b)(1): the first executable
# line is the form linter form634_check.py --series (FORM634 FAILED => exit 10).  A previous output of a refused call is moved to old/
# before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line rc=<n>.  F34C_DRYRUN=2 stops after the checks;
# F34C_TIMES / F34C_QUEUE_SKIP=1 / F34C_DISP_SKIP=1 / F34C_RUNS (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f34c || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f34c
TM=${F34C_TIMES:-C:/kyty/f287/times.txt}
RD=${F34C_RUNS:-$G/runs}
case "$T" in
  b6_w0|b6_v|b6_v2|b6_vl|b6_w|b6_wl) REP=0;;
  b6_w0_r[1-4]|b6_v_r[1-4]|b6_v2_r[1-4]|b6_vl_r[1-4]|b6_w_r[1-4]|b6_wl_r[1-4]) REP=1;;
  *) echo "usage: launch_f34c.sh b6_w0|b6_v|b6_v2|b6_vl|b6_w|b6_wl[_r1..4]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ $REP = 1 ]; then
  [ "${F34C_REPEAT_OK:-}" = 1 ] || { echo "a repeat needs its times.txt line with the member-ground first (item 676 (l)), then F34C_REPEAT_OK=1"; exit 11; }
  NREP=$(python -c "
import os, re, sys
rd, me = sys.argv[1], sys.argv[2]
names = set()
for d in os.listdir(rd) if os.path.isdir(rd) else []:
    m = re.match(r'^(b6_[a-z0-9]+_r[1-4])(\.[a-z]+_\d+)?$', d)
    if not m:
        continue
    run = os.path.join(rd, d, 'run.txt')
    if os.path.exists(run) and '--- attempt 1: launching' in open(run, 'rb').read().decode('ascii', 'replace'):
        names.add(m.group(1))
names.discard(me)
print(len(names))
" "$RD" "$T")
  [ "${NREP:-9}" -lt 4 ] || { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c repeat cap of the series reached ($NREP started repeats, item 676 (l)) - $T not launched" >> "$TM"; echo "repeat cap reached: $NREP"; exit 11; }
fi
if [ "${F34C_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
QS="QUEUE FREE (skipped)"
if [ "${F34C_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f34c.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F34C_DRYRUN:-}" = 2 ] && { echo "dryrun2 rep $REP"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f34c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c previous output of $T moved to f34c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F34c launch_f34c detached call: bash $G/go_f34c.sh $T" >> "$TM"
F34C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f34c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
