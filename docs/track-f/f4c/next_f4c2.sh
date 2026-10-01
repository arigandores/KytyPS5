#!/bin/bash
# F4c continuation (HPP-337, V5) call wrapper (port of C:/kyty/s143/step2/next_one.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c2.sh series" (pred/f4c2.md), then a foreground wait (wait_f4c2.sh,
# < 600 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/f4c/wait_f4c2.sh      (never a second next_f4c2.sh while it runs - go_f4c2.sh also refuses by attempt files)
# The lock window of win_f4c.py is checked inside go_f4c2.sh right before its lock.  ASCII only.  usage: next_f4c2.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/f4c/go_series2.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F4c next_f4c2 STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F4c next_f4c2 STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c2.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/f4c; PLWAIT=540 bash C:/kyty/f287/f4c/go_f4c2.sh series > C:/kyty/f287/f4c/go_series2.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/f4c/go_series2.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F4c go_f4c2 series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/f4c/wait_f4c2.sh
