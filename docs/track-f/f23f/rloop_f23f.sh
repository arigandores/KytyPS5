#!/bin/bash
# F23f (HPP-592): replay loop inside one tool call (<= 560 s): while the lock or a gate process is present - sleep only
# (wait_free.sh of F23c); when free - one rdw_f23f.sh run of rd_f23f.py with the remaining time as its limit (the script is
# resumable by event id); killed by the watchdog (7 gate / 3 lock / 6 limit) -> loop again. Exit 0 - every event of the plan has a
# line in the output; 1 - time up; 4 - STOP; other - the run's code.
# Usage: rloop_f23f.sh <tag> <capture> <plan.json> <out.jsonl>
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
G=C:/kyty/f287/f23f
TAG=$1; CAP=$2; PLAN=$3; OUTF=$4
T0=$(date +%s)
K=0
left() { python -c "
import json,sys
p=json.load(open('$PLAN'))
d=set()
try:
    for l in open('$OUTF'): d.add(json.loads(l)['eid'])
except FileNotFoundError: pass
print(len([e for e in p['events'] if e['eid'] not in d]))"; }
while true; do
	L=$(left)
	[ "$L" = 0 ] && { echo "$(date -u +%FT%TZ) all events done after $K runs"; exit 0; }
	EL=$(( $(date +%s) - T0 ))
	[ $EL -ge 470 ] && { echo "$(date -u +%FT%TZ) time up after $K runs, $L events left"; exit 1; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 5; continue; fi
	GP=$(python -c "
import psutil, os
g = 'procload' + '.py'
me = os.getpid()
print(len([p for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != me and any(a.replace(chr(92), '/').endswith('/' + g) or a == g for a in (p.info['cmdline'] or []))]))")
	if [ "$GP" != 0 ]; then sleep 5; continue; fi
	K=$((K + 1))
	RD_CAP=$CAP RD_PLAN=$PLAN RD_OUT=$OUTF RD_DIR=$G/dump bash $G/rdw_f23f.sh ${TAG}_$K $G/rd_f23f.py $(( 540 - EL ))
	RC=$?
	echo "$(date -u +%FT%TZ) run $K rc=$RC, events left $(left)"
	if [ $RC -ne 0 ] && [ $RC -ne 7 ] && [ $RC -ne 3 ] && [ $RC -ne 6 ] && [ $RC -ne 8 ]; then exit $RC; fi
	[ $RC -eq 8 ] && sleep 5
done
