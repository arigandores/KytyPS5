#!/bin/bash
# FSc (HPP-370) call wrapper (port of C:/kyty/s143/step2/next_one.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/fsc/go_fs.sh series" (pred/01_fs.md section 5), then a foreground wait (wait_fs.sh,
# < 600 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/fsc/wait_fs.sh      (never a second next_fs.sh while it runs - go_fs.sh also refuses by attempt files)
# The lock window (win_fs.py: HPP-369 done; HPP-357, HPP-352, HPP-364 not waiting) is checked inside go_fs.sh right before its lock.  ASCII only.  usage: next_fs.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/fsc/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FSc next_fs STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FSc next_fs STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/fsc/go_fs.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/fsc; PLWAIT=540 bash C:/kyty/f287/fsc/go_fs.sh series > C:/kyty/f287/fsc/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/fsc/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FSc go_fs series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/f287/fsc/wait_fs.sh
