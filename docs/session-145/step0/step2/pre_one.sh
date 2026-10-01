#!/bin/bash
# Session 145 step 2 (step 0 HPP-350; ROADMAP s122 item 273 (k)(4); port of the s144 file of item 266 (h)): the checks
# before the call of one tag, in the order of the lead's
# comment 4750ca43: the stop file and the lock, sc145.py --stop-check <tag> (its output into step2/stopcheck_<tag>.txt and
# a times.txt row with rc and sha), then step2/gate145.py --before <tag> (its own GATE row).  rc 0 - call
# step2/next_one.sh <tag> <last comment id> in the next command; rc 3 lock, 4 stop file, 5 stop rule / gate STOP.
# ASCII only.  usage: pre_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
TIMES=C:/kyty/s145/step2/times.txt
[ -e C:/kyty/s145/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) pre_one STOP file found before $T" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
cd C:/kyty/s145 || exit 1
python sc145.py --stop-check $T > step2/stopcheck_$T.txt 2>&1
SRC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) pre_one sc145.py --stop-check $T rc $SRC step2/stopcheck_$T.txt sha256 $(sha256sum step2/stopcheck_$T.txt | cut -c1-64): $(tr '\r\n' '  ' < step2/stopcheck_$T.txt | cut -c1-600)" >> $TIMES
cat step2/stopcheck_$T.txt
[ "$SRC" != "0" ] && exit 5
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
python step2/gate145.py --before $T || exit 5
exit 0
