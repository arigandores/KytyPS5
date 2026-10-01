#!/bin/bash
# Session 144 step 2 (step 0 HPP-330, ROADMAP s122 item 254 (k); port of the session-143 file, names moved to s144): a foreground
# wait for one detached call, at most 56 x 10 s = 560 s per invocation (under the 600 s of a tool command); prints DONE and
# the rc line, or RUNNING (call this script again); the stop file ends the wait (not the call).  ASCII only.
# usage: wait_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/s144/step2/go_$T.out.txt
S=RUNNING
for i in $(seq 1 56); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/s144/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
grep '^rc=' $F 2>/dev/null | tail -1
tail -4 C:/kyty/s144/go144a.log
