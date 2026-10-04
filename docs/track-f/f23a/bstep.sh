#!/bin/bash
# F23a (HPP-578; copy of f23a/bstep.sh): one build step (build_f23a.cmd <args>) under the watchdog watch_f23a.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f23a.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
# F23a: survivors after a kill are looked up by the backslash path of the build tree (own bash shells use forward slashes)
export WD_MARK='f23a\'
cd C:/kyty/f287/f23a
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_f23a.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\f23a\\build_f23a.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
