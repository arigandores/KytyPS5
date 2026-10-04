#!/bin/bash
# F19d2 (HPP-560): repeat one build step (bstep.sh <log> <args>) after watchdog kills (lock 3 / refused 5, 8 /
# procload 7 / limit 6), waiting for a free window between tries; stops after ~$BT s (default 520). Exit = last rc.
export PATH=/usr/bin:/mingw64/bin:$PATH
cd C:/kyty/f287/f19d2
T0=$(date +%s); BT=${BT:-520}; RC=9
while [ $(( $(date +%s) - T0 )) -lt $BT ]; do
	bash wait_free.sh $(( BT - ($(date +%s) - T0) )) || { RC=$?; break; }
	bash bstep.sh "$@" > /dev/null; RC=$?
	echo "$(date -u +%T) try $* rc=$RC" >> bretry.log
	case $RC in 3|5|6|7|8) continue;; *) break;; esac
done
echo "rc=$RC"; tail -3 "build_$1.log"
exit $RC
