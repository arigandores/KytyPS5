#!/bin/bash
# F3d (HPP-342) call wrapper (port of C:/kyty/s143/step2/next_one.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/f3d/go_f3d.sh series" (pred/01_f3d.md section 5), then a foreground wait (wait_f3d.sh,
# < 600 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/f3d/wait_f3d.sh      (never a second next_f3d.sh while it runs - go_f3d.sh also refuses by attempt files)
# The lock window (win_f3d.py: HPP-333, HPP-341 done; HPP-337, HPP-352, HPP-364 not waiting) is checked inside go_f3d.sh right before its lock.  ASCII only.  usage: next_f3d.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/f3d/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F3d next_f3d STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F3d next_f3d STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/f3d/go_f3d.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/f3d; PLWAIT=540 bash C:/kyty/f287/f3d/go_f3d.sh series > C:/kyty/f287/f3d/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/f3d/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F3d go_f3d series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/f3d/wait_f3d.sh
