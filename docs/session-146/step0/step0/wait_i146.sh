#!/bin/bash
# Session 146 step 0 (HPP-386): foreground wait for the detached install call, at most 56 x 10 s = 560 s per invocation; prints
# DONE and the rc line, or RUNNING (call again).  The stop file is reported, it does not interrupt a started call.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
F=C:/kyty/s146/step0/go_i146.out.txt
S=RUNNING
for i in $(seq 1 56); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  sleep 10
done
[ -e C:/kyty/s146/STOP ] && echo "STOP file present $(date -u +%H:%M:%SZ): $(head -1 C:/kyty/s146/STOP)"
echo "$S install $(date -u +%H:%M:%SZ)"
tail -3 $F 2>/dev/null
tail -4 C:/kyty/s146/step0/times.txt | cut -c1-260
