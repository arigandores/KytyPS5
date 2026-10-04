#!/bin/bash
# F23c (HPP-587; copy of f23a/wait_free.sh; was F23a HPP-578): wait (sleep only, no write) while the foreign lock exists or a gate process runs (an argv element
# ending with the gate file name - the name is assembled at run time so that this script's own command line never
# matches); <= 520 s. Exit 0 - free; 1 - still busy (prints the state).
export PATH=/usr/bin:/mingw64/bin:$PATH
T0=$(date +%s)
S=""
while true; do
	if [ ! -e C:/kyty/SEALED_RUN.lock ]; then
		N=$(python -c "
import psutil, os
g = 'procload' + '.py'
me = os.getpid()
print(len([p for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != me and any(a.replace(chr(92), '/').endswith('/' + g) or a == g for a in (p.info['cmdline'] or []))]))")
		[ "$N" = 0 ] && break
		S="gate=$N"
	else
		S=lock
	fi
	[ $(( $(date +%s) - T0 )) -ge 520 ] && { echo "$(date -u +%FT%TZ) busy ($S)"; exit 1; }
	sleep 5
done
echo "$(date -u +%FT%TZ) free"
exit 0
