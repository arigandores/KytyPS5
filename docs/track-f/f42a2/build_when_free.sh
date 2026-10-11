#!/bin/bash
# F42a2 (HPP-805): run one chain.sh step only after the lock and the gate process (procload.py) were absent for FREE s in a
# row (the series of F40c takes a lock per tag with ~40 s windows; a build with LTO does not fit one); a step killed by the
# watchdog (lock / procload, rc 3/7/8/5) waits again. Budget BUDGET s per call (tool limit 600 s).
# Usage: build_when_free.sh <chain.sh args>
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42a2
FREE=${FREE:-90}; BUDGET=${BUDGET:-560}; T0=$(date +%s)
gate() {
	python -c "
import psutil, os, sys
own = os.getpid()
hit = any(any(a.replace(chr(92), '/').endswith('/procload' + '.py') or a == 'procload' + '.py' for a in (p.info['cmdline'] or []))
          for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != own)
print(1 if hit else 0)"
}
while :; do
	free=0
	while [ $free -lt $FREE ]; do
		[ $(( $(date +%s) - T0 )) -gt $BUDGET ] && { echo "budget out, not started $(date -u +%FT%TZ)"; exit 9; }
		[ -e C:/kyty/f287/STOP ] && exit 4
		if [ -e C:/kyty/SEALED_RUN.lock ] || [ "$(gate)" = 1 ]; then
			free=0
		else
			free=$((free + 5))
		fi
		sleep 5
	done
	echo "free ${FREE} s at $(date -u +%FT%TZ); step $*"
	bash chain.sh "$@"; RC=$?
	echo "step rc=$RC $(date -u +%FT%TZ)"
	case $RC in 3|5|7|8) ;; *) exit $RC ;; esac
	[ $(( $(date +%s) - T0 )) -gt $BUDGET ] && exit 9
done
