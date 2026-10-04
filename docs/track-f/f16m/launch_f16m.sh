#!/bin/bash
# Track F link F16m (HPP-585): ONLY launches one detached call of go_f16m.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f16m.sh <= 540 s per tool command, separate commands).  Port of F16f launch_f16f.sh.  A previous output of a refused call
# (rc 3 / 5, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f16m
case "$T" in f5cmu_0|f5cmu_1|f5id_sg|f5id_ef|f5id_bh|f5id_eb) ;; *) echo "usage: launch_f16m.sh <tag>"; exit 2;; esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f16m.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F16m launch_f16m previous output of $T moved to f16m/old/" >> C:/kyty/f287/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F16m launch_f16m detached call: bash $G/go_f16m.sh $T" >> C:/kyty/f287/times.txt
nohup bash -c "bash $G/go_f16m.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched
