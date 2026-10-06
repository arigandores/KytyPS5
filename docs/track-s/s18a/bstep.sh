#!/bin/bash
# S18a (HPP-642): copy of C:/kyty/f287/fs8a/bstep.sh, paths changed: one build step (build_s18a.cmd <args>) under the
# watchdog watch_fs8a.py (WD_STOP C:/kyty/s288/STOP, WD_TIMES C:/kyty/s288/s18a/times.txt), 540 s step limit (exit 6 ->
# rerun the step, ninja is incremental); an API check line in times.txt before the step (api_chk.sh).
# Usage: bstep.sh <log name> [build_s18a.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
export WD_STOP=C:/kyty/s288/STOP WD_TIMES=C:/kyty/s288/s18a/times.txt
cd C:/kyty/s288/s18a
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python C:/kyty/f287/fs8a/watch_fs8a.py --limit 540 --tag "S18a build $N $*" -- cmd //c "C:\\kyty\\s288\\s18a\\build_s18a.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
