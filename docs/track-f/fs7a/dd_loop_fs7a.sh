#!/bin/bash
# FS7a (HPP-565, ROADMAP s122 item 487(g)(1)): copy of the F19c2 dd_loop.sh - 100 cycles (0..99) of the dd case without
# KYTY_FIX_B24 (run_stand_fs7a_b24dd.py; FS7 default ON). Next cycle = last recorded + 1 in runs/dd/dd_<label>_cycles.txt
# (a cycle killed by the watchdog is not recorded and runs again); batches of 25 cycles under the watchdog watch_fs7a.py
# (limit 120 s); while the lock or a gate process (an argument ending with procload.py) is there - waits in 5 s steps.
# Stops after ~520 s of wall (tool limit) or when cycle 99 is recorded.
# Usage: dd_loop_fs7a.sh <exe> <label>
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7a
EXE=$1
L=$2
F=runs/dd/dd_${L}_cycles.txt
T0=$(date +%s)
bash api_chk.sh "dd series $L" > /dev/null || exit $?
while :; do
	NEXT=0
	[ -f $F ] && NEXT=$(python next_cycle.py $F)
	[ $NEXT -gt 99 ] && { echo "dd $L complete"; exit 0; }
	[ $(( $(date +%s) - T0 )) -gt 520 ] && { echo "dd $L next=$NEXT (time)"; exit 0; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ] || ! python gate_free.py > /dev/null; then
		sleep 5
		continue
	fi
	LAST=$(( NEXT + 24 ))
	[ $LAST -gt 99 ] && LAST=99
	python watch_fs7a.py --limit 120 --tag "dd $L $NEXT..$LAST" -- python run_stand_fs7a_b24dd.py dd $EXE runs/dd $L $NEXT $LAST >> dd_${L}_loop.log 2>&1
	RC=$?
	[ -e C:/kyty/SEALED_RUN.lock ] || echo "$(date -u +%T) batch $NEXT..$LAST rc=$RC" >> dd_${L}_loop.log
done
