#!/bin/bash
# F16e2 (HPP-570, Red Team): copy of the F16d2 script, names f16d2 -> f16e2.
# F16e2 (HPP-569, ROADMAP s122 item 431(v)): one test run (run_tests_f16e2.py <what> <exe> <out>) under watch_f16e2.py in the
# gaps of a foreign series, repeated (from the start) when the watchdog kills it, for at most BUDGET seconds (default 520).
# Exit: the run's rc (0 = ALL OK); 4 - STOP; 6 - budget spent.
# Usage: tloop.sh <site|modes|cfg> <exe> <out>
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f16e2
END=$((SECONDS + ${BUDGET:-520}))
k=0
gate() {
	python -c "
import psutil, os
print(len([p for p in psutil.process_iter(['pid','cmdline']) if p.info['pid']!=os.getpid() and any(str(a).replace(chr(92),'/').endswith('/procload'+'.py') or a=='procload'+'.py' for a in (p.info['cmdline'] or []))]))"
}
while [ $SECONDS -lt $((END - 30)) ]; do
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ] || [ "$(gate)" != "0" ]; then
		sleep 10
		continue
	fi
	k=$((k + 1))
	bash api_chk.sh "test $1 $(basename $3).$k" > /dev/null || { sleep 10; continue; }
	python watch_f16e2.py --limit $((END - SECONDS)) --tag "test $1 $(basename $3).$k" -- python run_tests_f16e2.py "$1" "$2" "$3" > "$3.watch.$k.txt" 2>&1
	RC=$?
	echo "test $1 $3 try $k rc=$RC $(date -u +%T)"
	grep -aE "^(KILLED|STOPPED|REFUSED)" "$3.watch.$k.txt" | head -2
	case $RC in
		3|5|6|7|8) sleep 5 ;;
		*) tail -14 "$3" 2>/dev/null | cut -c1-200; exit $RC ;;
	esac
done
exit 6
