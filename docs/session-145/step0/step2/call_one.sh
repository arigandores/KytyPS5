#!/bin/bash
# Session 145 step 2 (step 0 HPP-350, ROADMAP s122 item 273 (k); port of the session-144 file, names moved to s145): ONE verbatim
# seal call "PLWAIT=540 bash C:/kyty/s145/go145a.sh <tag>" (pred/01_sc145.md), its output into step2/go_<tag>.out.txt, the rc
# and the return time into the same file and step2/times.txt.  No game logic here.  ASCII only.  usage: call_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
cd C:/kyty/s145 || exit 1
PLWAIT=540 bash C:/kyty/s145/go145a.sh $T > step2/go_$T.out.txt 2>&1
RC=$?
echo "rc=$RC" >> step2/go_$T.out.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) call_one go145a $T call returned rc=$RC" >> step2/times.txt
