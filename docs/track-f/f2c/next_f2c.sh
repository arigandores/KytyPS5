#!/bin/bash
# F2c (HPP-310) call wrapper (port of C:/kyty/s143/step2/next_one.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/f2c/go_f2c.sh series" (pred/01_f2c.md section 4), then a foreground wait (wait_f2c.sh,
# < 600 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/f2c/wait_f2c.sh      (never a second next_f2c.sh while it runs - go_f2c.sh also refuses by attempt files)
# The HPP-332 window of p.256(e) is checked inside go_f2c.sh right before its lock.  ASCII only.  usage: next_f2c.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/f2c/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F2c next_f2c STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F2c next_f2c STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/f2c/go_f2c.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/f2c; PLWAIT=540 bash C:/kyty/f287/f2c/go_f2c.sh series > C:/kyty/f287/f2c/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/f2c/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F2c go_f2c series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/f2c/wait_f2c.sh
