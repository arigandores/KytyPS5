#!/bin/bash
# F47h2 (HPP-829): one source mutant: mutate the own worktree, build f47dt_stand (bstep.sh, watchdog), copy the exe, restore
# the file (git checkout), run the stand runner of F47g2 unchanged. Usage: run_mut_f47h2.sh <m1|m2|m2p|m5|m6|m7>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/f47h/wt
D=C:/kyty/f287/f47h2
M=$1
cd $D
python mut_f47h2.py src $WT $M || exit 1
bash bstep.sh st_$M target f47dt_stand
RC=$?
if [ $RC -eq 0 ]; then cp C:/kyty/f287/f47h/build/f47dt_stand.exe stand_bin/f47dt_stand_$M.exe; fi
"$G" -C $WT checkout -- src/graphics/host_gpu/renderer/diagF47Dt.cpp
echo "git status lines: $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
[ $RC -eq 0 ] || { echo "BUILD FAILED $M"; exit 2; }
rm -rf run_$M
python run_stand_f47g2.py $D/stand_bin/f47dt_stand_$M.exe $D/run_$M > run_$M.out 2>&1
echo "stand rc=$? $(tail -1 run_$M.out)"
grep -a "FAIL" run_$M.out | head -6
echo "$(date -u +%FT%TZ) F47h2 mutant $M stand $(sha256sum stand_bin/f47dt_stand_$M.exe | cut -c1-8) run_$M.out $(sha256sum run_$M.out | cut -c1-8) last: $(tail -1 run_$M.out)" >> C:/kyty/f287/times.txt
