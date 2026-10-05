#!/bin/bash
# FS7b (HPP-566, Red Team, ROADMAP s122 item 487(g)(2)): copy of the FS7a dd_loop_fs7a.sh with paths fs7a -> fs7b - 100 cycles
# (0..99) of the dd case without KYTY_FIX_B24 (driver docs/track-f/fs7a/run_stand_fs7a_b24dd.py, my own b24_pad_stand.exe).
# Next cycle = last recorded + 1 (a cycle killed by the watchdog is not recorded and runs again); batches of 25 cycles under
# watch_fs7b.py (limit 120 s); while the lock or a gate process is there - waits in 5 s steps. Stops after ~520 s of wall or
# when cycle 99 is recorded. Usage: dd_loop_fs7b.sh <label>
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7b
EXE=C:/kyty/f287/fs7b/fix/b24_pad_stand.exe
L=$1
F=runs/dd/dd_${L}_cycles.txt
T0=$(date +%s)
mkdir -p runs/dd
bash api_chk.sh "dd series $L" > /dev/null || exit $?
while :; do
	NEXT=0
	[ -f $F ] && NEXT=$(python C:/kyty/f287/fs7a/next_cycle.py $F)
	[ $NEXT -gt 99 ] && { echo "dd $L complete"; exit 0; }
	[ $(( $(date +%s) - T0 )) -gt 520 ] && { echo "dd $L next=$NEXT (time)"; exit 0; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ] || ! python C:/kyty/f287/fs7a/gate_free.py > /dev/null; then
		sleep 5
		continue
	fi
	LAST=$(( NEXT + 24 ))
	[ $LAST -gt 99 ] && LAST=99
	python watch_fs7b.py --limit 120 --tag "dd $L $NEXT..$LAST" -- python C:/kyty/KytyPS5/docs/track-f/fs7a/run_stand_fs7a_b24dd.py dd $EXE runs/dd $L $NEXT $LAST >> dd_${L}_loop.log 2>&1
	RC=$?
	[ -e C:/kyty/SEALED_RUN.lock ] || echo "$(date -u +%T) batch $NEXT..$LAST rc=$RC" >> dd_${L}_loop.log
done
