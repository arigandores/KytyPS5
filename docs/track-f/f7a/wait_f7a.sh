#!/bin/bash
# F7a (HPP-397): a foreground wait for the detached call of go_f7a.sh, at most 54 x 10 s = 540 s per invocation (item 324 (i));
# prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.  usage: wait_f7a.sh <k>
export PATH=/usr/bin:/mingw64/bin:$PATH
K=$1
F=C:/kyty/f287/f7a/go_f7a_$K.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S f7a_$K"
grep '^rc=' $F 2>/dev/null | tail -1
grep 'F7a go_f7a f7a_'$K C:/kyty/f287/times.txt | tail -3 | cut -c1-400
