#!/bin/bash
# Session 143 step 2 (link 1b HPP-321, ROADMAP s122 item 242 (d)/(RC5); port of C:/kyty/s142/step2/call_one.sh): ONE verbatim
# seal call "PLWAIT=540 bash C:/kyty/s143/go143a.sh <tag>" (pred/02_sc143.md), its output into step2/go_<tag>.out.txt, the rc
# and the return time into the same file and step2/times.txt.  No game logic here.  ASCII only.  usage: call_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
cd C:/kyty/s143 || exit 1
PLWAIT=540 bash C:/kyty/s143/go143a.sh $T > step2/go_$T.out.txt 2>&1
RC=$?
echo "rc=$RC" >> step2/go_$T.out.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) call_one go143a $T call returned rc=$RC" >> step2/times.txt
