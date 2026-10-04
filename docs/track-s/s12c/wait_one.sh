#!/bin/bash
# Track S link S12c (HPP-496) - port of C:/kyty/s288/s10/wait_one.sh: a foreground wait for one detached call, at most
# 52 x 10 s = 520 s per invocation (under the 540 s of item 324 (i)); prints DONE and the rc line, or RUNNING (call this
# script again); the stop file ends the wait (not the call).  ASCII only.  usage: wait_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/s288/s12/go_$T.out.txt
S=RUNNING
for i in $(seq 1 52); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/s288/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
grep '^rc=' $F 2>/dev/null | tail -1
tail -3 C:/kyty/s288/s12/go_s12.log 2>/dev/null | cut -c1-300
