#!/bin/bash
# FS5a (HPP-509): copy of the FS4a script, build script path changed, extra args passed through (target <name>). Was:
# FS4a (copy of the FS3a script, build script path changed). Was:
# FS3a (copy of the F9e2c script, build script path changed, 540 s step limit - exit 6, rerun the step). Was:
# F9e2c: run one build step (build_*.cmd [arg]) while watching the foreign lock and STOP: if C:/kyty/SEALED_RUN.lock or
# C:/kyty/f287/STOP appears, the step's process tree is killed (taskkill /T /F) and the script exits 3 / 4; the step is
# rerun later (ninja is incremental). General rule 27: no process of this link under a foreign lock.
# Usage: lockrun.sh <log> [configure|tests|version|target <name>]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
LOG=${1:?log}
shift
cmd //c "C:\\kyty\\f287\\fs5\\fs5a\\build_fs5a.cmd" "$@" > "$LOG" 2>&1 &
PID=$!
WINPID=$(cat /proc/$PID/winpid 2>/dev/null)
T0=$(date +%s)
while kill -0 $PID 2>/dev/null; do
	if [ $(( $(date +%s) - T0 )) -ge 540 ]; then
		taskkill //T //F //PID $WINPID > /dev/null 2>&1
		wait $PID
		echo "STOPPED: 540 s step limit $(date -u +%Y-%m-%dT%H:%M:%SZ)"
		exit 6
	fi
	if [ -e C:/kyty/SEALED_RUN.lock ] || [ -e C:/kyty/f287/STOP ]; then
		taskkill //T //F //PID $WINPID > /dev/null 2>&1
		wait $PID
		if [ -e C:/kyty/SEALED_RUN.lock ]; then
			echo "KILLED: lock appeared $(date -u +%Y-%m-%dT%H:%M:%SZ)"
			exit 3
		fi
		echo "KILLED: STOP $(date -u +%Y-%m-%dT%H:%M:%SZ)"
		exit 4
	fi
	sleep 1
done
wait $PID
RC=$?
echo "rc=$RC end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $RC
