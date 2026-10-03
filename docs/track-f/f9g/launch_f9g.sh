#!/bin/bash
# F9g (HPP-424): ONLY launches one detached call of go_f9g.sh <tag> (process rule p.324(i): the launcher only launches, the wait is
# wait_f9g.sh <= 540 s per tool command, separate commands).  Needed for f9g_sg / f9g_hb (enter_scene up to 480 s + hold 330 s
# exceeds the 600 s of one tool command).  The output go_<tag>.out.txt ends with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f9/f9g
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ -e $G/go_$T.out.txt ] && { echo "go_$T.out.txt exists - wait with wait_f9g.sh"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) launch_f9g detached call: bash $G/go_f9g.sh $T" >> C:/kyty/f287/f9/times.txt
nohup bash -c "bash $G/go_f9g.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
