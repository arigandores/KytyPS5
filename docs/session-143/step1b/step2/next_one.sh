#!/bin/bash
# Session 143 step 2 call wrapper (link 1b HPP-321, ROADMAP s122 item 242 (d)/(RC5); port of C:/kyty/s142/step2/next_one.sh):
# the stop file and the lock first, then ONE detached verbatim seal call (call_one.sh), then a foreground wait (wait_one.sh,
# < 600 s per invocation).  The call survives the end of the tool command; a still-running call is waited for again with
#   bash C:/kyty/s143/step2/wait_one.sh <tag>      (never a second next_one.sh for the same tag while it runs)
# ASCII only.  usage: next_one.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
TIMES=C:/kyty/s143/step2/times.txt
case "$T" in
  v143_0[1-9]|w143_0[1-9]|v143_10|w143_10) ;;
  *) echo "usage: next_one.sh v143_NN|w143_NN"; exit 2;;
esac
[ -e C:/kyty/s143/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP file found before $T" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_one STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/s143/go143a.sh $T" >> $TIMES
nohup bash C:/kyty/s143/step2/call_one.sh $T > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/s143/step2/wait_one.sh $T
