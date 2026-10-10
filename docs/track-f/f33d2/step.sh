#!/bin/bash
# F33d2 (HPP-749): one stand step. Usage: step.sh <arm> <from> <to> <fix> <exe> <outdir>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f33d2
bash api_chk.sh "stand $1 $2-$3 fix$4 $5" || exit $?
echo "$(date -u +%FT%TZ) F33d2 step start: arm $1 seeds $2-$3 fix $4 exe $5 out $6" >> times.txt
python run_stand_f33d2.py $1 $2 $3 --fix $4 --exe $5 --out C:/kyty/f287/f33d2/$6 > "log_$6_$1_fix$4.txt" 2>&1
RC=$?
echo "$(date -u +%FT%TZ) F33d2 step end: arm $1 fix $4 exe $5 out $6 rc=$RC tsv $(sha256sum $6/fix$4/stand_$1.tsv | cut -c1-8)" >> times.txt
tail -2 "log_$6_$1_fix$4.txt"
exit $RC
