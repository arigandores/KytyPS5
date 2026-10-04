#!/bin/bash
# FS6a (HPP-555, ROADMAP s122 item 454(g)(1)): copy of the F15c sstep.sh - one stand slice under the watchdog watch_fs6a.py
# (540 s limit), an API check line in times.txt before. Exe - fix/b4_race_stand.exe of the FS6 worktree build; driver -
# run_stand_fs6a.py (plane L expects the FS6 default).
# Usage: sstep.sh <mode> <fix none|0|1> <N> <first_seed>   -> runs/stand_<mode>_<fix>_<first>.tsv
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs6a
mkdir -p runs
O=runs/stand_$1_$2_$4.tsv
bash api_chk.sh "stand $1 fix=$2 seeds $4..$(( $4 + $3 - 1 ))" > /dev/null || exit $?
python watch_fs6a.py --limit 540 --tag "stand $1 $2 $4" -- python run_stand_fs6a.py fix/b4_race_stand.exe $1 $3 $O $2 $4 > runs/log_$1_$2_$4.txt 2>&1
RC=$?
echo "rc=$RC $O: $(grep -a '^# done' $O)"
exit $RC
