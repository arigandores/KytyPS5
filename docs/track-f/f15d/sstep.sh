#!/bin/bash
# F15d (HPP-515, Red Team): copy of the F15c file with f15c -> f15d (paths, names); the stand driver stays docs/track-f/f15c/run_stand_f15c.py.
# F15d (HPP-514, ROADMAP s122 item 412(g)(1)-(3)): one stand slice under the watchdog watch_f15d.py (540 s limit; exit 6 -> rerun
# the slice into a new file), an API check line in times.txt before. Exe - fix/b4_race_stand.exe (sha in bin_f15d.sha256.txt).
# Usage: sstep.sh <mode> <fix none|0|1> <N> <first_seed>   -> runs/stand_<mode>_<fix>_<first>.tsv
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f15d
mkdir -p runs
O=runs/stand_$1_$2_$4.tsv
bash api_chk.sh "stand $1 fix=$2 seeds $4..$(( $4 + $3 - 1 ))" > /dev/null || exit $?
python watch_f15d.py --limit 540 --tag "stand $1 $2 $4" -- python C:/kyty/KytyPS5/docs/track-f/f15c/run_stand_f15c.py fix/b4_race_stand.exe $1 $3 $O $2 $4 > runs/log_$1_$2_$4.txt 2>&1
RC=$?
echo "rc=$RC $O: $(grep -a '^# done' $O)"
exit $RC
