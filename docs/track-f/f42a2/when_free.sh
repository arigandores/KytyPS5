#!/bin/bash
# F42a2 (HPP-805): run a command only after the lock and the gate process (procload.py) were absent for FREE s in a row
# (form of build_when_free.sh, any command). Exit 9 - budget out before the start; otherwise the command's code.
# Usage: when_free.sh <command...>
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
FREE=${FREE:-60}; BUDGET=${BUDGET:-540}; T0=$(date +%s)
gate() {
	python -c "
import psutil, os, sys
own = os.getpid()
hit = any(any(a.replace(chr(92), '/').endswith('/procload' + '.py') or a == 'procload' + '.py' for a in (p.info['cmdline'] or []))
          for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != own)
print(1 if hit else 0)"
}
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
echo "free ${FREE} s at $(date -u +%FT%TZ): $*"
"$@"
