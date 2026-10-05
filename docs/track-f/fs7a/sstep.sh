#!/bin/bash
# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1)): one step (stand driver or tests) under the watchdog
# watch_fs7a.py (540 s limit; killed at the lock, STOP or a procload.py process - item 431(v)(1)); an API check line in
# times.txt before. Form of the FS6a sstep.sh with the command given as arguments.
# Usage: sstep.sh <log name> <command...>   -> runs/log_<log name>.txt
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7a
mkdir -p runs
N=$1; shift
bash api_chk.sh "step $N" > /dev/null || exit $?
python watch_fs7a.py --limit 540 --tag "step $N" -- "$@" > runs/log_$N.txt 2>&1
RC=$?
echo "rc=$RC"
tail -4 runs/log_$N.txt
exit $RC
