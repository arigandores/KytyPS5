#!/bin/bash
# F9e2c (copy of the F9e2b script, build script path changed): run one build step (build_f9e2.cmd [arg]) while watching the foreign lock and STOP: if C:/kyty/SEALED_RUN.lock or
# C:/kyty/f287/STOP appears, the step's process tree is killed (taskkill /T /F) and the script exits 3 / 4; the step is
# rerun later (ninja is incremental). General rule 27: no process of this link under a foreign lock.
# Usage: lockrun.sh <log> [configure|tests|version]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
LOG=${1:?log}
ARG=$2
cmd //c "C:\\kyty\\f287\\f9\\f9e2c\\build_f9e2c.cmd" $ARG > "$LOG" 2>&1 &
PID=$!
WINPID=$(cat /proc/$PID/winpid 2>/dev/null)
while kill -0 $PID 2>/dev/null; do
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
