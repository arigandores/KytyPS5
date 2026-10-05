#!/bin/bash
# Track S link S17c (HPP-613): ONLY launches one detached call of go_s17c.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_s17c.sh <= 540 s per tool command, separate commands).  Port of F20c launch_f20c.sh seal 2 without the FS6b window.
# General rule 33 (item 534 (3)): guard_s17c.py check (a user emulator or launcher => the block closes, a times.txt line, exit 7,
# interference) and status (the block must be open: two clean checks >= 600 s apart by guard_s17c.py open-block, fewer than 6 tags in it;
# else exit 8); then a TAG line of the block and the launch.  A previous output of a refused call is moved to old/ before the new call
# (rule p.309(i)); the output go_<tag>.out.txt ends with the line rc=<n>.  S17C_DRYRUN=2 stops after the checks (fixtures only).
# ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/s288/s17c
TM=$G/times.txt
case "$T" in s17c_v0|s17c_w0|s17c_c2|s17c_ca|s17c_cc|s17c_n0|s17c_r3|s17c_rs|s17c_e3|s17c_ew|s17c_ks|s17c_kn|s17c_kc) ;;
  *) echo "usage: launch_s17c.sh <tag of go_s17c.sh>"; exit 2;; esac
[ -e C:/kyty/s288/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GS=$(python $G/guard_s17c.py check)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S17c guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_s17c.py status)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S17c guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
[ "$S17C_DRYRUN" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S17c guard (item 534): $GS; $BS; $(python $G/guard_s17c.py tag $T)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_s17c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S17c launch_s17c previous output of $T moved to s17c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S17c launch_s17c detached call: bash $G/go_s17c.sh $T" >> "$TM"
nohup bash -c "bash $G/go_s17c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
