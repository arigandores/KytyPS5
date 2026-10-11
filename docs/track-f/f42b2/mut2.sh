#!/bin/bash
# F42b2 (HPP-806, Red Team; ROADMAP s122 item 705(b)(6)): one mutant on the own worktree (tree = F42a2 bea8d373), resumable.
# Apply (mut_f42b2.py - the F42b anchors, whole lines, writes only what differs), build the stand (all mutants) and the
# emulator (call-site mutants m1b, m6) under the watchdog (bstep.sh), copy + sha256, the stand =1 (all) and =0 (m1b, m6)
# R=20 seed 42072, the recount rc_f42b2.py --mutant, revert. A killed step exits 7 with the mutant left applied.
# Usage: mut2.sh <m>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42b2
M=$1
O=mut/$M
mkdir -p $O
python mut_f42b2.py $M >> $O/apply.txt 2>&1 || { tail -3 $O/apply.txt; exit 2; }
"/c/Program Files/Git/cmd/git.exe" -C wt diff > $O/mutant.diff
case $M in m1b|m6) BUILDS="rct emu"; MODES="m1 m0";; *) BUILDS="rct"; MODES="m1";; esac
for b in $BUILDS; do
  [ -e $O/done_build_$b ] && continue
  case $b in rct) A="target shader_recompiler_compute_tests";; emu) A="";; esac
  bash bstep.sh "${b}_$M" $A > $O/build_$b.txt 2>&1 || { echo "build $b killed/failed"; grep -a "KILLED\|error" $O/build_$b.txt | head -3; exit 7; }
  case $b in rct) cp build/shader_recompiler_compute_tests.exe $O/;; emu) cp build/install/kyty_emulator.exe $O/;; esac
  touch $O/done_build_$b
done
(cd $O && sha256sum *.exe > sha256.txt)
for k in $MODES; do
  if [ ! -e $O/done_stand_$k ]; then
    bash api_chk.sh "mutant $M stand $k" > /dev/null || exit 7
    bash run_stand.sh $O $k ${k#m} 20 42072 C:/kyty/f287/f42b2/$O/shader_recompiler_compute_tests.exe > $O/stand_$k.txt 2>&1 || { echo "stand killed"; exit 7; }
    touch $O/done_stand_$k
  fi
done
python rc_f42b2.py $O 42072 20 $(echo $MODES | tr ' ' ',') --mutant $M > $O/rc_mut.txt 2>&1
python mut_f42b2.py revert >> $O/apply.txt 2>&1
echo "== $M"; cat $O/sha256.txt; tail -1 $O/rc_mut.txt
echo "$(date -u +%FT%TZ) F42b2 mutant $M bins $(cut -c1-8 $O/sha256.txt | tr '\n' ' ')| $(tail -1 $O/rc_mut.txt | cut -c1-200)" >> times.txt
touch $O/done_all
