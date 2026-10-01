#!/bin/bash
# F5c (HPP-357) call wrapper (port of C:/kyty/f287/f4c/next_f4c2.sh): stop file and lock first, then ONE detached verbatim seal call
# "PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series" (pred/f5c.md), then a foreground wait (wait_f5c.sh, < 600 s per
# invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/f5c/wait_f5c.sh      (never a second next_f5c.sh while it runs - go_f5c.sh also refuses by attempt files)
# The lock window of win_f5c.py is checked inside go_f5c.sh right before its lock.  ASCII only.  usage: next_f5c.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/f5c/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F5c next_f5c STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only (move it aside with a times line after a BUSY rc 4)"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F5c next_f5c STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/f5c; PLWAIT=540 bash C:/kyty/f287/f5c/go_f5c.sh series > C:/kyty/f287/f5c/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/f5c/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F5c go_f5c series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/f5c/wait_f5c.sh
