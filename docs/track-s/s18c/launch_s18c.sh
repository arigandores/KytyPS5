#!/bin/bash
# Track S link S18c (HPP-644; port of S17c2 launch_s17c2.sh): ONLY launches one detached call of go_s18c.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_s18c.sh <= 540 s per tool command, separate commands).  Port of F20c launch_f20c.sh seal 2 without the FS6b window.
# General rule 33 (item 534 (3)): guard_s18c.py check (a user emulator or launcher => the block closes, a times.txt line, exit 7,
# interference) and status (the block must be open: two clean checks >= 600 s apart by guard_s18c.py open-block, fewer than 6 tags in it;
# else exit 8); then a TAG line of the block and the launch.  A previous output of a refused call is moved to old/ before the new call
# (rule p.309(i)); the output go_<tag>.out.txt ends with the line rc=<n>.  S18C_DRYRUN=2 stops after the checks (fixtures only).
# ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/s288/s18c
TM=$G/times.txt
case "$T" in s18_c01|s18_c02|s18_c03|s18_c04|s18_c05|s18_c06|s18_c07|s18_c08|s18_c09|s18_c10|s18_c11|s18_c12|s18_c13|s18_c14|s18_c15|s18_c16|s18_c17|s18_c18|s18_c19|s18_ks|s18_r|s18_e1|s18_e2|s18_v|s18_w) ;;
  *) echo "usage: launch_s18c.sh <tag of go_s18c.sh>"; exit 2;; esac
[ -e C:/kyty/s288/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
GS=$(python $G/guard_s18c.py check)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c guard (item 534): $GS - block closed, $T not launched (interference, not an attempt)" >> "$TM"
  echo "user process found: $GS"; exit 7
fi
BS=$(python $G/guard_s18c.py status)
if [ $? != 0 ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c guard (item 534): $BS - $T not launched (open the block: two clean checks >= 600 s apart)" >> "$TM"
  echo "$BS"; exit 8
fi
[ "$S18C_DRYRUN" = 2 ] && { echo "dryrun2 $BS"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c guard (item 534): $GS; $BS; $(python $G/guard_s18c.py tag $T)" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_s18c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c launch_s18c previous output of $T moved to s18c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c launch_s18c detached call: bash $G/go_s18c.sh $T" >> "$TM"
nohup bash -c "bash $G/go_s18c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
