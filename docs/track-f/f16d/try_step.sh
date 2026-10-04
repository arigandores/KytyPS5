#!/bin/bash
# F16d (HPP-521, ROADMAP s122 item 431(v)): wait (sleeping only, no work, no writes) up to WAIT_S seconds for a window -
# no lock, no STOP, no process whose argv ends with procload.py - then run one build/test step via bstep.sh / tstep.sh
# under the watchdog. Usage: try_step.sh <bstep.sh|tstep.sh> <step args...>
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
WAIT_S=${WAIT_S:-520}
T0=$(date +%s)
while :; do
	[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
	if [ ! -e C:/kyty/SEALED_RUN.lock ]; then
		n=$(python -c "
import psutil, os
print(len([p for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != os.getpid() and any(a.replace(chr(92), '/').endswith('/procload' + '.py') or a == 'procload' + '.py' for a in (p.info['cmdline'] or []))]))" 2>/dev/null)
		[ "$n" = 0 ] && break
	fi
	[ $(( $(date +%s) - T0 )) -ge "$WAIT_S" ] && { echo "NO WINDOW after ${WAIT_S}s $(date -u +%T)"; exit 9; }
	sleep 10
done
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
cd C:/kyty/f287/f16d || exit 1
S=$1; shift
bash "$S" "$@"
