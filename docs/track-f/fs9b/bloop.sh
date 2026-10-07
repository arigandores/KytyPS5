#!/bin/bash
# FS9b (HPP-672, Red Team): run one step (bstep.sh / any script) in the gaps of the foreign series F25f (HPP-669): only
# when there is no lock, no procload.py process, and the last line of C:/kyty/f287/f25f/runs/lock.log is "lock released"
# at least 20 s ago (item 535(g) form); a step killed by the watchdog (rc 3/5/7/8) is rerun (ninja is incremental).
# Total wall cap 550 s (tool limit 600 s), exit 9 at the cap. Usage: bloop.sh <script> <args...>
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs9b
T0=$(date +%s)
S=$1; shift
while :; do
	[ -e C:/kyty/f287/STOP ] && exit 4
	[ $(( $(date +%s) - T0 )) -ge 550 ] && { echo "bloop cap"; exit 9; }
	if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 3; continue; fi
	P=$(python -c "
import psutil,os
print(len([p for p in psutil.process_iter(['pid','cmdline']) if p.info['pid']!=os.getpid() and any(a.replace(chr(92),'/').split('/')[-1]=='procload.py' for a in (p.info['cmdline'] or []))]))")
	if [ "$P" != 0 ]; then sleep 3; continue; fi
	L=$(tail -1 C:/kyty/f287/f25f/runs/lock.log)
	case "$L" in "lock released"*) ;; *) sleep 3; continue;; esac
	TS=$(echo "$L" | awk '{print $NF}')
	AGE=$(( $(date +%s) - $(date -d "$TS" +%s) ))
	if [ $AGE -lt 20 ]; then sleep 3; continue; fi
	REM=$(( 550 - ($(date +%s) - T0) ))
	[ $REM -lt 30 ] && { echo "bloop cap"; exit 9; }
	echo "bloop: start step $(date -u +%FT%TZ) (lock released ${AGE} s ago)"
	bash $S "$@"; RC=$?
	case $RC in 3|5|7|8) sleep 5; continue;; esac
	exit $RC
done
