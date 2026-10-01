#!/bin/bash
# Session 144 step 2 (step 0 HPP-330, ROADMAP s122 item 254 (k); port of the session-143 file, names moved to s144): ONE verbatim
# seal call "PLWAIT=540 bash C:/kyty/s144/go144a.sh <tag>" (pred/01_sc144.md), its output into step2/go_<tag>.out.txt, the rc
# and the return time into the same file and step2/times.txt.  No game logic here.  ASCII only.  usage: call_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
cd C:/kyty/s144 || exit 1
PLWAIT=540 bash C:/kyty/s144/go144a.sh $T > step2/go_$T.out.txt 2>&1
RC=$?
echo "rc=$RC" >> step2/go_$T.out.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) call_one go144a $T call returned rc=$RC" >> step2/times.txt
