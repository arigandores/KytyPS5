#!/bin/bash
# FS9a (HPP-671): copy of the FS8a bstep.sh, paths and names changed. Was:
# FS8a (HPP-571): copy of the FS7a bstep.sh, paths and names changed. Was:
# FS8a (HPP-571): copy of the FS6a bstep.sh, paths changed. Was:
# FS8a (HPP-571): copy of the F15c bstep.sh, paths changed. Was:
# F15c (HPP-514): copy of the F14e bstep.sh, paths changed. Was:
# F14e (HPP-505, ROADMAP s122 item 431(v),(d)): one build step (build_f14e.cmd <args>) under the watchdog watch_fs9a.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f14e.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs9a
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_fs9a.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\fs9a\\build_fs9a.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
