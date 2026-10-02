#!/bin/bash
# F6e (HPP-377) call wrapper (port of C:/kyty/f287/f3d/next_f3d.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/f6e/go_f6e.sh series" (pred/03_f6e.md section 6), then a foreground wait (wait_f6e.sh,
# < 600 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/f6e/wait_f6e.sh      (never a second next_f6e.sh while it runs - go_f6e.sh also refuses by attempt files)
# The lock window (win_f6e.py: HPP-376, HPP-353, HPP-388, HPP-389 done; HPP-357, HPP-370 done or in_review; HPP-352, HPP-364,
# HPP-393 not waiting) is checked inside
# go_f6e.sh right before its lock.  A BUSY refusal (rc 4, nothing made) leaves go_series.out.txt: before a new call move it to
# go_series.busy<N>.out.txt with a times line.  ASCII only.  usage: next_f6e.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/f6e/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F6e next_f6e STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F6e next_f6e STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/f6e/go_f6e.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/f6e; PLWAIT=540 bash C:/kyty/f287/f6e/go_f6e.sh series > C:/kyty/f287/f6e/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/f6e/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F6e go_f6e series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/f6e/wait_f6e.sh
