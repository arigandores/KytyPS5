#!/bin/bash
# FS2c (HPP-383) foreground wait for the detached series (port of C:/kyty/s143/step2/wait_one.sh): at most 53 x 10 s = 530 s per
# invocation; prints DONE and the rc line, or RUNNING (call again).  The stop file does not interrupt a started series
# (p.256(e), as in F2c, F3d); it is only reported.  ASCII only.  usage: wait_fs2.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
F=C:/kyty/f287/fs2c/go_series.out.txt
S=RUNNING
for i in $(seq 1 53); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  sleep 10
done
[ -e C:/kyty/f287/STOP ] && echo "STOP file present $(date -u +%H:%M:%SZ): $(head -1 C:/kyty/f287/STOP)"
echo "$S series $(date -u +%H:%M:%SZ)"
cat $F 2>/dev/null | tail -3
grep ' FS2c go_fs2 ' C:/kyty/f287/times.txt | tail -4 | cut -c1-220
