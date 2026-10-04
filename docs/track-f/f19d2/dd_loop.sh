#!/bin/bash
# F19d2 (HPP-559, ROADMAP s122 item 460(v)(2)): resumable 1 000-cycle dd series. Next cycle = last recorded + 1 in
# runs/dd/dd_<label>_cycles.txt (a cycle killed by the watchdog is not recorded and runs again); batches of 30 cycles
# under the watchdog watch_f19d2.py (limit 120 s); while the lock or a gate process (an argument ending with
# procload.py) is there - waits in 5 s steps. Stops after ~520 s of wall (tool limit) or when cycle 999 is recorded.
# Usage: dd_loop.sh <exe> <label>
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f19d2
EXE=$1
L=$2
F=runs/dd/dd_${L}_cycles.txt
T0=$(date +%s)
bash api_chk.sh "dd series $L" > /dev/null || exit $?
while :; do
	NEXT=0
	[ -f $F ] && NEXT=$(python next_cycle.py $F)
	[ $NEXT -gt 999 ] && { echo "dd $L complete"; exit 0; }
	[ $(( $(date +%s) - T0 )) -gt 520 ] && { echo "dd $L next=$NEXT (time)"; exit 0; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ] || ! python gate_free.py > /dev/null; then
		sleep 5
		continue
	fi
	LAST=$(( NEXT + 29 ))
	[ $LAST -gt 999 ] && LAST=999
	python watch_f19d2.py --limit 120 --tag "dd $L $NEXT..$LAST" -- python run_stand_f19d2.py dd $EXE runs/dd $L $NEXT $LAST >> dd_${L}_loop.log 2>&1
	RC=$?
	echo "$(date -u +%T) batch $NEXT..$LAST rc=$RC" >> dd_${L}_loop.log
done
