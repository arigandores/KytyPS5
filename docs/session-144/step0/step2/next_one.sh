#!/bin/bash
# Session 144 step 2 call wrapper (step 0 HPP-330, ROADMAP s122 item 254 (i), (k); port of C:/kyty/s143/step2/next_one.sh):
# the tag, the stop file and the lock first, then the API check row (step2/apichk144.py, MINOR-4 of audit 143: one GET of
# the step's issue and its comments, a times.txt row with the answer; NO GO -> rc 4, no call), then ONE detached verbatim
# seal call (call_one.sh), then a foreground wait (wait_one.sh, < 600 s per invocation).  The call survives the end of the
# tool command; a still-running call is waited for again with
#   bash C:/kyty/s144/step2/wait_one.sh <tag>      (never a second next_one.sh for the same tag while it runs)
# ASCII only.  usage: next_one.sh <tag> [<id of the last comment read>]
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
AFTER=${2:-}
TIMES=C:/kyty/s144/step2/times.txt
case "$T" in
  w144_0[0-8]|v144_09|w144_09|v144_1[0-9]|w144_1[0-9]|v144_20|w144_20) ;;
  *) echo "usage: next_one.sh w144_00..w144_08|v144_NN|w144_NN (NN 09..20) [<last comment id read>]"; exit 2;;
esac
[ -e C:/kyty/s144/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP file found before $T" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
if [ -n "$AFTER" ]; then
  python C:/kyty/s144/step2/apichk144.py --tag $T --after "$AFTER" || { echo "api check NO GO before $T (row in times.txt)"; exit 4; }
else
  python C:/kyty/s144/step2/apichk144.py --tag $T || { echo "api check NO GO before $T (row in times.txt)"; exit 4; }
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock, api GO; call: PLWAIT=540 bash C:/kyty/s144/go144a.sh $T" >> $TIMES
nohup bash C:/kyty/s144/step2/call_one.sh $T > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/s144/step2/wait_one.sh $T
