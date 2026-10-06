#!/bin/bash
# Track S link S15e (HPP-636): ONLY launches one detached call of go_s15e.sh s15_i (process rule p.324(i): the launcher only launches,
# the wait is wait_s15e.sh <= 540 s per tool command, separate commands).  Port of FS8e launch_fs8e.sh.  A previous output of a refused
# call (rc 3 / 5 / 9, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt
# ends with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/s288/s15e
[ -e C:/kyty/s288/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ "$T" = "s15_i" ] || { echo "usage: launch_s15e.sh s15_i"; exit 2; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_s15e.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S15e launch_s15e previous output of $T moved to s15e/old/" >> $G/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S15e launch_s15e detached call: bash $G/go_s15e.sh $T" >> $G/times.txt
nohup bash -c "bash $G/go_s15e.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
