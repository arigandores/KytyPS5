#!/bin/bash
# FS2c (HPP-383) call wrapper (port of C:/kyty/s143/step2/next_one.sh): stop file and lock first, then ONE detached verbatim seal
# call "PLWAIT=540 bash C:/kyty/f287/fs2c/go_fs2.sh series" (pred/01_fs2.md section 8) and RETURNS (item 324 (i)): the
# wait is a separate tool command wait_fs2.sh (<= 540 s per invocation).  The series survives the end of the tool command; a running series is waited for again with
#   bash C:/kyty/f287/fs2c/wait_fs2.sh      (never a second next_fs2.sh while it runs - go_fs2.sh also refuses by attempt files)
# The lock window (win_fs2.py) is checked inside go_fs2.sh right before its lock.  ASCII only.  usage: next_fs2.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/f287/times.txt
OUT=C:/kyty/f287/fs2c/go_series.out.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS2c next_fs2 STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
[ -e $OUT ] && { echo "series output exists - one call only"; exit 1; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS2c next_fs2 STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/f287/fs2c/go_fs2.sh series" >> $TIMES
nohup bash -c 'cd C:/kyty/f287/fs2c; PLWAIT=540 bash C:/kyty/f287/fs2c/go_fs2.sh series > C:/kyty/f287/fs2c/go_series.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/f287/fs2c/go_series.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS2c go_fs2 series call returned rc=$RC" >> C:/kyty/f287/times.txt' > /dev/null 2>&1 & disown
sleep 3
echo "started; wait with: bash C:/kyty/f287/fs2c/wait_fs2.sh"
