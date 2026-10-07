#!/bin/bash
# FS9b (HPP-672, Red Team): one run of run_stand_fs9b.py under the watchdog watch_fs9b.py (item 431(v)(1)); an API line in
# times.txt before. Usage: sstep.sh <out file>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs9b
bash api_chk.sh "stand $1" > /dev/null || exit $?
python watch_fs9b.py --limit 300 --tag "stand" -- python run_stand_fs9b.py > "$1" 2>&1
RC=$?
grep -aE "^(watch:|rc=|KILLED|STOPPED|REFUSED)|FAIL|ALL OK" "$1" | head -40
exit $RC
