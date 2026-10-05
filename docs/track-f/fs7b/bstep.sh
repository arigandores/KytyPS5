#!/bin/bash
# FS7b (HPP-556, Red Team, ROADMAP s122 item 454(g)(2)): copy of the F15d file with f15d -> fs7b (paths, names).
# FS7b (HPP-515, Red Team): copy of the F15c file with f15c -> fs7b (paths, names); the stand driver stays docs/track-f/f15c/run_stand_f15c.py.
# FS7b (HPP-514): copy of the F14e bstep.sh, paths changed. Was:
# F14e (HPP-505, ROADMAP s122 item 431(v),(d)): one build step (build_f14e.cmd <args>) under the watchdog watch_fs7b.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f14e.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7b
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_fs7b.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\fs7b\\build_fs7b.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
