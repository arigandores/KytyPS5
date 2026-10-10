#!/bin/bash
# F33c2 (HPP-748): copy of the F33c step.sh (f33c -> f33c2, binary 2b393af8 -> a086872d). One counted stand step under the
# watchdog watch_f33c2.py (540 s), an API check line before it, start/end lines in C:/kyty/f287/times.txt and in
# C:/kyty/f287/f33c2/times.txt. Usage: step.sh <arm> <from> <to> <fix>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f33c2
bash api_chk.sh "stand $1 $2-$3 fix$4" > /dev/null || exit $?
L="$(date -u +%FT%TZ) F33c2 counted step start: arm $1 seeds $2-$3 KYTY_FIX_F21=$4 binary a086872d"
echo "$L" >> C:/kyty/f287/times.txt; echo "$L" >> times.txt
python watch_f33c2.py --limit 540 --tag "stand $1 fix$4" -- python run_stand_f33c2.py $1 $2 $3 --fix $4 --exe kyty_emulator_a086872d.exe --out C:/kyty/f287/f33c2/runs > "runs_step_$1_fix$4.log" 2>&1
RC=$?
L="$(date -u +%FT%TZ) F33c2 counted step end: arm $1 seeds $2-$3 KYTY_FIX_F21=$4 rc=$RC"
echo "$L" >> C:/kyty/f287/times.txt; echo "$L" >> times.txt
tail -3 "runs_step_$1_fix$4.log"
exit $RC
