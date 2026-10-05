#!/bin/bash
# F20j2 (HPP-633, ROADMAP s122 item 552(d)): copy of the F20j bstep.sh, names changed (f20j -> f20j2); worktree base 0df13a66 (= 302347b4 + 875720c5 + 0df13a66).
# F20j (HPP-629, ROADMAP s122 item 550(z)): copy of the F19c bstep.sh, names changed.
# F19c (HPP-547, ROADMAP s122 item 451(e)(3)): copy of the F18c bstep.sh, names changed. Was:
# F19c (HPP-539, ROADMAP s122 item 441(d)(3)): copy of the F15c bstep.sh, names changed. Was:
# F15c (HPP-514): copy of the F14e bstep.sh, paths changed. Was:
# F14e (HPP-505, ROADMAP s122 item 431(v),(d)): one build step (build_f14e.cmd <args>) under the watchdog watch_f15c.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f14e.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f20j2
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_f20j2.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\f20j2\\build_f20j2.cmd" "$@" > "build_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_$N.log" | grep -v "warning" | head -20
tail -2 "build_$N.log"
exit $RC
