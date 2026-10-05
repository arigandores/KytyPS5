#!/bin/bash
# F16o (HPP-595; copy of f16k2/bstep.sh). Was: F16k2 (HPP-590; copy of f16k/bstep.sh; build tree f16k/build reused). Was: F16k (HPP-583; copy of f23a/bstep.sh): one build step (build_f16k.cmd <args>) under the watchdog watch_f16o.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f16k.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
# F16k: survivors after a kill are looked up by the backslash path of the build tree (own bash shells use forward slashes)
export WD_MARK='f16k\'
cd C:/kyty/f287/f16o
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_f16o.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\f16o\\build_f16o.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
