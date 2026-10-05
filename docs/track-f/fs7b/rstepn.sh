#!/bin/bash
# FS7b (HPP-556, Red Team): retry runner for one build step in the gaps of a foreign series (ROADMAP s122 item 431(v)(1)):
# while the lock or a procload.py process exists - only sleep (no reads/writes); otherwise one API line (api_chk.sh) and the
# step under watch_fs7b.py with the remaining time as its limit; a step killed by the watchdog (procload/lock) is rerun
# (ninja / cmake are incremental) until it ends with its own rc or the deadline (default 560 s) passes.
# Usage: rstep.sh <log name> [build_fs7n.cmd args...]
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7b
N=$1; shift
T0=$(date +%s); DL=${DEADLINE:-560}; k=0
pl() { python -c "
import psutil
n=0
for p in psutil.process_iter():
    try: a=p.cmdline()
    except Exception: continue
    if any(x.replace(chr(92),'/').split('/')[-1]=='procload.py' for x in a): n+=1
print(n)"; }
while :; do
	left=$(( DL - ($(date +%s) - T0) ))
	[ $left -lt 20 ] && { echo "DEADLINE after $k attempts"; exit 9; }
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 5; continue; fi
	[ "$(pl)" = 0 ] || { sleep 5; continue; }
	k=$((k+1))
	bash api_chk.sh "build $N $* attempt $k" > /dev/null || { sleep 5; continue; }
	python watch_fs7b.py --limit $left --tag "build $N $* attempt $k" -- cmd //c "C:\kyty\f287\fs7b\build_fs7n.cmd" "$@" >> "buildn_$N.log" 2>&1
	RC=$?
	echo "attempt $k rc=$RC $(date -u +%T)"
	case $RC in 3|5|7|8) sleep 5; continue;; esac
	grep -aE "BUILD OK|error|FAILED" "buildn_$N.log" | grep -v warning | tail -5
	exit $RC
done
