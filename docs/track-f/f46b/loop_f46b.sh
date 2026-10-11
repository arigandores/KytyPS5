#!/bin/bash
# Track F, F46b (HPP-799): run one step through runq.py (watchdog watch_f46b.py) and, when a foreign lock kills it, wait
# for the release (sleep only - no other process, no write under the lock), write the deferred times line and repeat;
# the whole call ends before `budget` seconds (one tool call). Usage: loop_f46b.sh <budget s> <tag> <log> -- <cmd...>
# Exit: the step's code; 3 - still locked at the end of the budget; 9 - budget out.
export PATH=/usr/bin:/mingw64/bin:$PATH
cd C:/kyty/f287/f46b
BUDGET=$1; TAG=$2; LOG=$3; shift 4
T0=$(date +%s)
while :; do
	[ -e C:/kyty/f287/STOP ] && exit 4
	while [ -e C:/kyty/SEALED_RUN.lock ]; do
		[ $(( $(date +%s) - T0 )) -ge $BUDGET ] && { echo "loop: budget out under the lock"; exit 3; }
		sleep 10
	done
	if [ -n "$PENDING" ]; then
		echo "$(date -u +%FT%TZ) F46b watchdog $TAG: KILLED: lock $PENDING (line written after the release, rule 27)" >> C:/kyty/f287/times.txt
		PENDING=
	fi
	LEFT=$(( BUDGET - ($(date +%s) - T0) ))
	[ $LEFT -lt 40 ] && { echo "loop: budget out"; exit 9; }
	bash api_chk.sh "$TAG" > /dev/null || exit $?
	python runq.py $LEFT "$TAG" -- "$@" >> "$LOG" 2>&1
	RC=$?
	if [ $RC -eq 3 ]; then
		PENDING=$(grep -a "KILLED: lock" "$LOG" | tail -1 | awk '{print $3}')
		[ -z "$PENDING" ] && PENDING="(before start)"
		continue
	fi
	echo "loop: $TAG rc=$RC"
	exit $RC
done
