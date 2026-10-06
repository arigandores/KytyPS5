#!/bin/bash
# F20l2 (HPP-648): wait for the next 'lock released' line of the S18c lock log (general rule 30, item 535 (g)); prints WINDOW <line> <now>
# and exits 0 when the new line appears and no lock file exists, within 20 s of the release; exits 9 after $1 seconds without a window.
export PATH=/usr/bin:/mingw64/bin:$PATH
LL=C:/kyty/s288/s18c/runs/lock.log
MAX=${1:-540}
n0=$(grep -c 'lock released' $LL)
t0=$(date +%s)
while :; do
  [ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
  n=$(grep -c 'lock released' $LL)
  if [ "$n" != "$n0" ]; then
    L=$(grep 'lock released' $LL | tail -1)
    ts=$(echo "$L" | awk '{print $4}')
    age=$(( $(date +%s) - $(date -d "$ts" +%s) ))
    if [ -e C:/kyty/SEALED_RUN.lock ] || [ $age -gt 20 ]; then echo "MISSED $L age $age"; exit 8; fi
    echo "WINDOW $L age ${age}s now $(date -u +%H:%M:%SZ)"; exit 0
  fi
  [ $(( $(date +%s) - t0 )) -ge $MAX ] && { echo "NOWINDOW"; exit 9; }
  sleep 2
done
