#!/bin/bash
# Track S link S12c (HPP-496) - port of C:/kyty/s288/s10/call_one.sh: ONE verbatim seal call of pred/08_s.md in the call form
# "PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh <tag>" (go_s12.sh unsets every KYTY_* and VK_LAYER_* itself), its output into
# s12/go_<tag>.out.txt, the rc and the return time into the same file and s12/times.txt.  No game logic here.  ASCII only.
# usage: call_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
cd C:/kyty/s288 || exit 1
PLWAIT=540 bash C:/kyty/s288/s12/go_s12.sh $T > s12/go_$T.out.txt 2>&1
RC=$?
echo "rc=$RC" >> s12/go_$T.out.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) call_one go_s12 $T call returned rc=$RC" >> s12/times.txt
