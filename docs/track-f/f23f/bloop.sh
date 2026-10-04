#!/bin/bash
# F23f (HPP-592): copy of f23a/bloop.sh for f23f. Was:
# F23a (HPP-578): build loop inside one tool call (<= 560 s): while the lock or a gate process is present - sleep only;
# when free - one API check line and one build step under watch_f23f.py with the remaining time as its limit
# (ninja is incremental; a killed step loses only the objects in flight). Exit 0 - BUILD OK; 1 - time up; 4 - STOP.
# Usage: bloop.sh <log name> [build_f23f.cmd args...]
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
export WD_MARK='f23f\'
cd C:/kyty/f287/f23f
N=$1; shift
T0=$(date +%s)
K=0
while true; do
	EL=$(( $(date +%s) - T0 ))
	[ $EL -ge 540 ] && { echo "$(date -u +%FT%TZ) time up after $K steps"; exit 1; }
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
	bash api_chk.sh "build $N step $K $*" > /dev/null || exit $?
	python watch_f23f.py --limit $(( 555 - EL )) --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\f23f\\build_f23f.cmd" "$@" > "build_${N}_$K.log" 2>&1
	RC=$?
	echo "$(date -u +%FT%TZ) step $K rc=$RC $(grep -aE '^\[[0-9]+/[0-9]+\]' build_${N}_$K.log | tail -1 | cut -c1-60)"
	grep -aE "error|FAILED" "build_${N}_$K.log" | grep -v warning | head -5
	if grep -aq "BUILD OK" "build_${N}_$K.log"; then echo BUILD OK; exit 0; fi
	if [ $RC -ne 7 ] && [ $RC -ne 3 ] && [ $RC -ne 6 ]; then echo "step failed rc=$RC"; tail -5 "build_${N}_$K.log"; exit 2; fi
done
