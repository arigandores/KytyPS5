#!/bin/bash
# Session 146 step 2 (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of the session-145 file, names moved to s146): ONE verbatim
# seal call "PLWAIT=540 bash C:/kyty/s146/go146a.sh <tag>" (pred/01_sc146.md), its output into step2/go_<tag>.out.txt, the rc
# and the return time into the same file and step2/times.txt.  No game logic here.  ASCII only.  usage: call_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
cd C:/kyty/s146 || exit 1
PLWAIT=540 bash C:/kyty/s146/go146a.sh $T > step2/go_$T.out.txt 2>&1
RC=$?
echo "rc=$RC" >> step2/go_$T.out.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) call_one go146a $T call returned rc=$RC" >> step2/times.txt
