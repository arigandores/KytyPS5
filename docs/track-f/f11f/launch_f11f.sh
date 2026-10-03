#!/bin/bash
# F11f (HPP-468): ONLY launches one detached call of go_f11f.sh <tag> (process rule p.324(i): the launcher only launches, the wait is
# wait_f11f.sh <= 540 s per tool command, separate commands).  Port of F10e launch_f10e.sh.  A previous output of a refused call
# (rc 3 / 5, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt
# ends with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f11f
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f11f.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F11f launch_f11f previous output of $T moved to f11f/old/" >> C:/kyty/f287/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F11f launch_f11f detached call: bash $G/go_f11f.sh $T" >> C:/kyty/f287/times.txt
nohup bash -c "bash $G/go_f11f.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
