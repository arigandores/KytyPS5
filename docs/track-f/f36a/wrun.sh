#!/bin/bash
# F36a (HPP-758; copy of f23f; was F23f (HPP-592; copy of f23c/wrun.sh; was F23c HPP-587, F23a HPP-578): run one resumable command inside one tool call (<= 560 s) - form of bloop.sh: sleep while the lock or
# a gate process is present; when free - API check line, then the command under watch_f36a.py with the remaining time;
# killed (7 gate / 3 lock / 6 limit) -> loop again (the command resumes). Exit = the command's code, 1 - time up, 4 - STOP.
# Usage: wrun.sh <tag> <command> [args...]
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
# the survivors sweep by command line is off (mark found in no command line): the typed command of the calling shell
# holds every script name, so any mark would also match it (21:45:03Z kill of the link's own shells); kill_tree stays
export WD_MARK='nosweep_f36a'
cd C:/kyty/f287/f36a
TAG=$1; shift
T0=$(date +%s)
K=0
while true; do
	EL=$(( $(date +%s) - T0 ))
	[ $EL -ge 530 ] && { echo "$(date -u +%FT%TZ) time up after $K attempts"; exit 1; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 5; continue; fi
	G=$(python -c "
import psutil, os
g = 'procload' + '.py'
me = os.getpid()
print(len([p for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != me and any(a.replace(chr(92), '/').endswith('/' + g) or a == g for a in (p.info['cmdline'] or []))]))")
	if [ "$G" != 0 ]; then sleep 5; continue; fi
	[ -e C:/kyty/SEALED_RUN.lock ] && continue
	K=$((K + 1))
	bash api_chk.sh "$TAG attempt $K" > /dev/null || exit $?
	python watch_f36a.py --limit $(( 555 - EL )) --tag "$TAG" -- "$@" > "wrun_${TAG}_$K.log" 2>&1
	RC=$?
	echo "$(date -u +%FT%TZ) attempt $K rc=$RC"
	tail -4 "wrun_${TAG}_$K.log"
	if [ $RC -ne 7 ] && [ $RC -ne 3 ] && [ $RC -ne 6 ]; then exit $RC; fi
done
