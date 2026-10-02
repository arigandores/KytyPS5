#!/bin/bash
# Session 146 step 2 (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of the session-145 file, names moved to s146): a foreground
# wait for one detached call, at most 56 x 10 s = 560 s per invocation (under the 600 s of a tool command); prints DONE and
# the rc line, or RUNNING (call this script again); the stop file ends the wait (not the call).  ASCII only.
# usage: wait_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/s146/step2/go_$T.out.txt
S=RUNNING
for i in $(seq 1 56); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/s146/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
grep '^rc=' $F 2>/dev/null | tail -1
tail -4 C:/kyty/s146/go146a.log
