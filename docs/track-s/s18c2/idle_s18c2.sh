#!/bin/bash
# Track S link S18c2 (HPP-654; derived from S18c idle_s18c.sh): GPU idle window of ROADMAP s122 item 585 (c) before a call of a tag: 15 samples of
# nvidia-smi --query-gpu=utilization.gpu in a row with a 20 s step; PASS = median <= 5 and no sample > 10.
# Writes the result line to times.txt; on PASS launches launch_s18c2.sh <tag> right after the window (it only launches).
# Refuses under the lock and with the stop file.  ASCII only.
# usage: bash idle_s18c2.sh s18_w2
export PATH=/usr/bin:/mingw64/bin:$PATH
export ProgramFiles="C:\\Program Files"
T=$1
G=C:/kyty/s288/s18c2
TM=$G/times.txt
case "$T" in s18_w2) ;; *) echo "usage: idle_s18c2.sh s18_w2"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
V=""
for i in $(seq 1 15); do
  [ -e C:/kyty/s288/STOP ] && exit 4
  u=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
  V="$V $(date -u +%H:%M:%SZ)=$u"
  [ $i -lt 15 ] && sleep 20
done
R=$(echo "$V" | python -c "
import sys,statistics
v=[int(t.split('=')[1]) for t in sys.stdin.read().split()]
m=statistics.median(v); ok=(len(v)==15 and m<=5 and max(v)<=10)
print('PASS' if ok else 'FAIL', 'n', len(v), 'median', m, 'max', max(v))")
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) S18c2 GPU idle window p.585(c) before $T: $R; samples$V" >> $TM
tail -1 $TM
case "$R" in PASS*) ;; *) exit 9;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "LOCKED after the window"; exit 5; }
bash $G/launch_s18c2.sh $T
