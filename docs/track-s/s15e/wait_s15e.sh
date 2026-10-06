#!/bin/bash
# Track S link S15e (HPP-636): foreground wait for the detached call of launch_s15e.sh, at most 54 x 10 s = 540 s per invocation; prints DONE
# and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  Port of FS8e wait_fs8e.sh.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/s288/s15e/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/s288/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null
