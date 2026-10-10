#!/bin/bash
# F33c (HPP-744): one counted stand step under the watchdog watch_f33c.py (540 s), an API check line before it,
# start/end lines in C:/kyty/f287/times.txt. Usage: step.sh <arm> <from> <to> <fix>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f33c
bash api_chk.sh "stand $1 $2-$3 fix$4" > /dev/null || exit $?
echo "$(date -u +%FT%TZ) F33c counted step start: arm $1 seeds $2-$3 KYTY_FIX_F21=$4 binary 2b393af8" >> C:/kyty/f287/times.txt
python watch_f33c.py --limit 540 --tag "stand $1 fix$4" -- python run_stand_f33c.py $1 $2 $3 --fix $4 --exe kyty_emulator_2b393af8.exe --out C:/kyty/f287/f33c/runs > "runs_step_$1_fix$4.log" 2>&1
RC=$?
echo "$(date -u +%FT%TZ) F33c counted step end: arm $1 seeds $2-$3 KYTY_FIX_F21=$4 rc=$RC" >> C:/kyty/f287/times.txt
tail -3 "runs_step_$1_fix$4.log"
exit $RC
