#!/bin/bash
# FS12b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): copy of the FS11b file with fs11b->fs12b, fs11n->fs12n, FS11b->FS12b in ALL lines (older header lines below that say FS12b mean FS11b HPP-715); default commits 730ed40a (FS12) / 9aaea58c (FS12 without FS12a).
# FS12b (HPP-715, Red Team, ROADMAP s122 item 647(d)(2)): copy of the FS10b file; fs10b -> fs12b, fs10n -> fs12n (paths, names, times label), default commits ee9632be / eded064e.
# FS12b (HPP-715, Red Team): copy of the FS9b bstepn.sh; fs9b -> fs12b, fs9n -> fs12n in code lines only.
# FS9b negative control: copy of bstep.sh calling build_fs9n.cmd, logs build_n_<name>.log.
# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): copy of the FS8b file with fs8b -> fs9b (paths, names); default commit 11164d72.
# FS8b (HPP-556, Red Team, ROADMAP s122 item 454(g)(2)): copy of the F15d file with f15d -> fs8b (paths, names).
# FS8b (HPP-515, Red Team): copy of the F15c file with f15c -> fs8b (paths, names); the stand driver stays docs/track-f/f15c/run_stand_f15c.py.
# FS8b (HPP-514): copy of the F14e bstep.sh, paths changed. Was:
# F14e (HPP-505, ROADMAP s122 item 431(v),(d)): one build step (build_f14e.cmd <args>) under the watchdog watch_fs9b.py,
# 540 s step limit (exit 6 -> rerun the step, ninja is incremental); an API check line in times.txt before the step.
# Usage: bstep.sh <log name> [build_f14e.cmd args...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs12b
N=$1; shift
bash api_chk.sh "build $N $*" > /dev/null || exit $?
python watch_fs12b.py --limit 540 --tag "build $N $*" -- cmd //c "C:\\kyty\\f287\\fs12b\\build_fs12n.cmd" "$@" > "build_n_$N.log" 2>&1
RC=$?
echo "rc=$RC"
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED|BUILD OK)|error|FAILED" "build_n_$N.log" | grep -v "warning" | head -20
tail -2 "build_n_$N.log"
exit $RC
