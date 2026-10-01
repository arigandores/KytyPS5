#!/bin/bash
# F6e (HPP-377) foreground wait for the detached series (port of C:/kyty/f287/f3d/wait_f3d.sh): at most 56 x 10 s = 560 s per
# invocation; prints DONE and the rc line, or RUNNING (call again).  The stop file does not interrupt a started series
# (p.256(e) precedent); it is only reported.  ASCII only.  usage: wait_f6e.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
F=C:/kyty/f287/f6e/go_series.out.txt
S=RUNNING
for i in $(seq 1 56); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  sleep 10
done
[ -e C:/kyty/f287/STOP ] && echo "STOP file present $(date -u +%H:%M:%SZ): $(head -1 C:/kyty/f287/STOP)"
echo "$S series $(date -u +%H:%M:%SZ)"
cat $F 2>/dev/null | tail -3
grep ' F6e go_f6e ' C:/kyty/f287/times.txt | tail -4 | cut -c1-220
