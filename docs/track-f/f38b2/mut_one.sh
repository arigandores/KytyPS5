#!/bin/bash
# F38b2 (HPP-778, Red Team): copy of the F38b mut_one.sh for the stand edition 3 - one mutant: apply (mut_f38b2.py =
# mut_f38b.py anchors), build the stand under the watchdog (bstep.sh), run =1 seed 38402 with the N of the comment
# 8697a133 (A 200 / K 50 / Z 50 / E 50 / T 20 / G 50), read (read_f38b2.py), restore the worktree files, git status = 0.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f38b2
G="/c/Program Files/Git/cmd/git.exe"
M=$1
python mut_f38b2.py C:/kyty/f287/f38b2/wt $M || exit 9
"$G" -C wt diff --stat | tail -1
"$G" -C wt diff > runs_mut_$M.diff
echo "$(date -u +%FT%TZ) mutant $M applied $(sha256sum runs_mut_$M.diff | cut -c1-8)" >> times.txt
bash bstep.sh mut_$M target f25_read_fail_stand > /dev/null; RC=$?
echo "build rc=$RC"
if [ $RC = 0 ]; then
  python run_stand_f38b2.py runs_mut/$M 38402 1 200 50 50 50 20 50 > runs_mut_drv_$M.txt 2>&1
  echo "stand rc=$?"
  grep -E "stand exe|DONE|FINAL|RESTORE" runs_mut_drv_$M.txt | cut -c1-200
  python read_f38b2.py 1 runs_mut/$M/rows_38402_f1.tsv > read_mut_$M.out.txt
  grep -vE "^[a-zA-Z_]+	[AKZETG]	" read_mut_$M.out.txt | cut -c1-700
  echo "$(date -u +%FT%TZ) mutant $M read $(sha256sum read_mut_$M.out.txt | cut -c1-8) $(tail -1 read_mut_$M.out.txt)" >> times.txt
fi
"$G" -C wt checkout -- src/kernel/fileSystem.cpp src/libs/libKernel.cpp
echo "worktree status lines $("$G" -C wt status --short --ignore-submodules=all | wc -l)"
