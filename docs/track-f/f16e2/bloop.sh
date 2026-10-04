#!/bin/bash
# F16e2 (HPP-570, Red Team): copy of the F16d2 script, names f16d2 -> f16e2.
# F16e2 (HPP-569, ROADMAP s122 item 431(v)): repeat one build step (bstep.sh -> build_f16e2.cmd under watch_f16e2.py) in the
# gaps of a foreign series for at most BUDGET seconds (default 520, below the 600 s tool limit). While the lock exists or a
# process with an argv element ending in procload.py is alive, nothing is started (one psutil listing every 10 s, no
# write); a step killed by the watchdog (lock / procload / limit) is repeated in the next gap - ninja is incremental.
# Exit: 0 - the step finished rc 0; 4 - STOP; 6 - budget spent; other - the step's own error.
# Usage: bloop.sh <log name> [build_f16e2.cmd args...]
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f16e2
N=$1; shift
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
	bash api_chk.sh "build $N.$k $*" > /dev/null || { sleep 10; continue; }
	python watch_f16e2.py --limit $((END - SECONDS)) --tag "build $N.$k $*" -- cmd //c "C:\\kyty\\f287\\f16e2\\build_f16e2.cmd" "$@" > "build_$N.$k.log" 2>&1
	RC=$?
	echo "step $N.$k rc=$RC $(date -u +%T)"
	grep -aE "^(KILLED|STOPPED|REFUSED|BUILD OK)" "build_$N.$k.log" | head -3
	grep -aE "error[: ]" "build_$N.$k.log" | grep -v warning | head -5
	tail -1 "build_$N.$k.log" | cut -c1-160
	# cmd //c does not pass the batch's exit /b 1 through: a finished step counts only with its "BUILD OK" line.
	if [ $RC = 0 ] && ! grep -aqE "^BUILD OK|Build files have been written" "build_$N.$k.log"; then
		RC=1
	fi
	case $RC in
		0) exit 0 ;;
		3|5|6|7|8) sleep 5 ;;
		4) exit 4 ;;
		*) grep -aE "\[[0-9]+/[0-9]+\]" "build_$N.$k.log" | tail -1 | cut -c1-120; [ -e C:/kyty/SEALED_RUN.lock ] || [ "$(gate)" != "0" ] || exit $RC ;;
	esac
done
exit 6
