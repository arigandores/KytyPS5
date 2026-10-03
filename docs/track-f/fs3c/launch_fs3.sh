#!/bin/bash
# FS3c (HPP-449): ONLY launches one detached call of go_fs3.sh <tag> (process rule p.324(i): the launcher only launches, the wait is
# wait_fs3.sh <= 540 s per tool command, separate commands).  Port of F9g launch_f9g.sh.  A previous output of a refused call
# (rc 3 / 5, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt
# ends with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/fs3/fs3c
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_fs3.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) launch_fs3 previous output of $T moved to fs3c/old/" >> C:/kyty/f287/fs3/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) launch_fs3 detached call: bash $G/go_fs3.sh $T" >> C:/kyty/f287/fs3/times.txt
nohup bash -c "bash $G/go_fs3.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
