#!/bin/bash
# Track F link F25f (HPP-669; port of F20l3 wait_f20l3.sh): foreground wait for the detached call of launch_f25f.sh, at most 54 x 10 s = 540 s per invocation; prints
# DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  Port of F20e wait_f20e.sh.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/f25f/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null
