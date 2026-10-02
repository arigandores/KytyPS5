#!/bin/bash
# Session 146 step 2 call wrapper (step 0 HPP-386, ROADMAP s122 item 309 (k)-(l); port of C:/kyty/s146/step2/next_one.sh;
# debt D-9 of s146 (item 309 (i)): the previous output step2/go_<tag>.out.txt of the tag is moved to step2/old/ before a new
# call - a file without its "rc=" line is a call still running: refused rc 1, wait with wait_one.sh):
# the tag, the stop file and the lock first, then the API check row (step2/apichk146.py, MINOR-4 of audit 143: one GET of
# the step's issue and its comments, a times.txt row with the answer; NO GO -> rc 4, no call), then ONE detached verbatim
# seal call (call_one.sh), then a foreground wait (wait_one.sh, < 600 s per invocation).  The call survives the end of the
# tool command; a still-running call is waited for again with
#   bash C:/kyty/s146/step2/wait_one.sh <tag>      (never a second next_one.sh for the same tag while it runs)
# ASCII only.  usage: next_one.sh <tag> [<id of the last comment read>]
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
AFTER=${2:-}
TIMES=C:/kyty/s146/step2/times.txt
case "$T" in
  w146_00|r146_0[1-4]|v146_0[5-9]|w146_0[5-9]|v146_1[0-9]|w146_1[0-9]) ;;
  *) echo "usage: next_one.sh w146_00|r146_0N (N 1..4)|v146_NN|w146_NN (NN 05..19) [<last comment id read>]"; exit 2;;
esac
[ -e C:/kyty/s146/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP file found before $T" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
if [ -n "$AFTER" ]; then
  python C:/kyty/s146/step2/apichk146.py --tag $T --after "$AFTER" || { echo "api check NO GO before $T (row in times.txt)"; exit 4; }
else
  python C:/kyty/s146/step2/apichk146.py --tag $T || { echo "api check NO GO before $T (row in times.txt)"; exit 4; }
fi
GO=C:/kyty/s146/step2/go_$T.out.txt
if [ -e $GO ]; then
  grep -q '^rc=' $GO || { echo "the previous call of $T has no rc line (running) - wait with wait_one.sh, no new call"; exit 1; }
  mkdir -p C:/kyty/s146/step2/old
  NEWN=C:/kyty/s146/step2/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  mv $GO $NEWN && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one previous output of $T moved to step2/old/$(basename $NEWN) (D-9)" >> $TIMES
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock, api GO; call: PLWAIT=540 bash C:/kyty/s146/go146a.sh $T" >> $TIMES
nohup bash C:/kyty/s146/step2/call_one.sh $T > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/s146/step2/wait_one.sh $T
