#!/bin/bash
# Track F link F18e (HPP-541): ONLY launches one detached call of go_f18e.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f18e.sh <= 540 s per tool command, separate commands).  Port of F15e launch_f15e.sh.  A previous output of a refused call
# (rc 3 / 5, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f18e
case "$T" in f8_s0|f8_s1|f8_n0|f8_n1) ;; *) echo "usage: launch_f18e.sh f8_s0|f8_s1|f8_n0|f8_n1"; exit 2;; esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f18e.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F18e launch_f18e previous output of $T moved to f18e/old/" >> C:/kyty/f287/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F18e launch_f18e detached call: bash $G/go_f18e.sh $T" >> C:/kyty/f287/times.txt
nohup bash -c "bash $G/go_f18e.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
