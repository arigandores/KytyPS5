#!/bin/bash
# F44b (HPP-792): build one mutant stand: revert the two files of the worktree, apply mutant <m> (mut_f44b.py), build the
# target f29_fault_stand (loop_build.sh), copy to bin/f29_fault_stand_<m>_<sha8>.exe, print the diff stat; revert stays to the next call / final.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f44b
M=$1
G="/c/Program Files/Git/cmd/git.exe"
"$G" -C wt checkout -- src/graphics/host_gpu/renderer/cache/faultManager.cpp tests/F29FaultStand.cpp
python mut_f44b.py apply C:/kyty/f287/f44b/wt $M || exit 1
"$G" -C wt diff > mut_$M.diff
"$G" -C wt diff --stat | tail -3
bash loop_build.sh mut_$M ${2:-560} target f29_fault_stand || exit $?
H=$(sha256sum build/f29_fault_stand.exe | cut -c1-8)
cp build/f29_fault_stand.exe bin/f29_fault_stand_${M}_$H.exe
echo "$(date -u +%FT%TZ) F44b mutant $M built f29_fault_stand sha $(sha256sum build/f29_fault_stand.exe | cut -c1-64)" | tee -a times.txt
