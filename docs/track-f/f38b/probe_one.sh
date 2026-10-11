#!/bin/bash
# F38b (HPP-764): LOCAL probe G (never main) - apply probe_g.py to the worktree stand (once), optionally a mutant of
# mut_f38b.py, build the stand under the watchdog, run <fix> with F38B_NG=50 seed 38203, read G (read_g.py) and the
# letter (read_f38b.py), restore src/ files; the probe stays until probe_off.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f38b
G="/c/Program Files/Git/cmd/git.exe"
M=$1; FIX=$2
grep -q "F38b probe" wt/tests/F25ReadFailStand.cpp || python probe_g.py C:/kyty/f287/f38b/wt || exit 9
[ "$M" = base ] || python mut_f38b.py C:/kyty/f287/f38b/wt $M || exit 9
"$G" -C wt diff > probe_${M}_f$FIX.diff
echo "$(date -u +%FT%TZ) probe G $M fix=$FIX applied $(sha256sum probe_${M}_f$FIX.diff | cut -c1-8)" >> times.txt
bash bstep.sh probe_$M target f25_read_fail_stand > /dev/null; RC=$?
echo "build rc=$RC"
if [ $RC = 0 ]; then
  F38B_NG=50 python run_stand_f38b.py runs_probe/${M} 38203 $FIX 200 50 50 50 20 > probe_drv_${M}_f$FIX.txt 2>&1
  echo "stand rc=$?"; grep -E "DONE|FINAL|RESTORE" probe_drv_${M}_f$FIX.txt
  python read_g.py runs_probe/${M}/rows_38203_f$FIX.tsv > read_probe_${M}_f$FIX.out.txt
  python read_f38b.py $FIX runs_probe/${M}/rows_38203_f$FIX.tsv | grep -E "^letter failures" | cut -c1-400 >> read_probe_${M}_f$FIX.out.txt
  cat read_probe_${M}_f$FIX.out.txt
  echo "$(date -u +%FT%TZ) probe G $M fix=$FIX read $(sha256sum read_probe_${M}_f$FIX.out.txt | cut -c1-8)" >> times.txt
fi
"$G" -C wt checkout -- src/kernel/fileSystem.cpp src/libs/libKernel.cpp
