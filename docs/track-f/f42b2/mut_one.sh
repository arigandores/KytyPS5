#!/bin/bash
# F42b2 (HPP-780, Red Team; ROADMAP s122 item 694(g)(5)): one mutant, resumable. Apply (mut_f42b2.py - writes only what
# differs), then the steps with done markers in mut/<m>/: builds under the watchdog (bstep.sh: header mutants - the stand
# and the corpus tool; call-site mutants m1b/m6 - the stand and the emulator), copies + sha256, the stand (=1; =0 too for
# m1b/m6) R=20 seed 42802, the T1 corpus (header mutants), the recount in mutant mode. A killed step exits 7 with the
# mutant left applied; a re-run resumes. All steps done -> revert. Usage: mut_one.sh <m>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42b2
M=$1
O=mut/$M
mkdir -p $O
python mut_f42b2.py $M >> $O/apply.txt 2>&1 || { tail -3 $O/apply.txt; exit 2; }
"/c/Program Files/Git/cmd/git.exe" -C wt diff > $O/mutant.diff
case $M in m1b|m6) BUILDS="rct emu";; *) BUILDS="rct cfgt";; esac
for b in $BUILDS; do
  [ -e $O/done_build_$b ] && continue
  case $b in rct) A="target shader_recompiler_compute_tests";; cfgt) A="tests";; emu) A="";; esac
  bash bstep.sh "${b}_$M" $A > $O/build_$b.txt 2>&1 || { echo "build $b killed/failed"; grep -a "KILLED\|error" $O/build_$b.txt | head -3; exit 7; }
  case $b in rct) cp build/shader_recompiler_compute_tests.exe $O/;; cfgt) cp build/shader_cfg_tests.exe $O/;; emu) cp build/install/kyty_emulator.exe $O/;; esac
  touch $O/done_build_$b
done
(cd $O && sha256sum *.exe > sha256.txt)
if [ ! -e $O/done_stand1 ]; then
  bash api_chk.sh "mutant $M stand =1" > /dev/null || exit 7
  bash run_stand.sh $O m1 1 20 42802 $(pwd)/$O/shader_recompiler_compute_tests.exe > $O/stand_m1.txt 2>&1 || { echo "stand killed"; exit 7; }
  touch $O/done_stand1
fi
python rc_stand_f42b2.py $O m1 --mutant > $O/rc_stand_m1.txt 2>&1
if [ "$M" = m1b ] || [ "$M" = m6 ]; then
  if [ ! -e $O/done_stand0 ]; then
    bash api_chk.sh "mutant $M stand =0" > /dev/null || exit 7
    bash run_stand.sh $O m0 0 20 42802 $(pwd)/$O/shader_recompiler_compute_tests.exe > $O/stand_m0.txt 2>&1 || { echo "stand killed"; exit 7; }
    touch $O/done_stand0
  fi
  python rc_stand_f42b2.py $O m0 --mutant > $O/rc_stand_m0.txt 2>&1
else
  if [ ! -e $O/done_corpus ]; then
    bash api_chk.sh "mutant $M corpus" > /dev/null || exit 7
    python watch_f42b2.py --limit 600 --tag "corpus $M" -- python corpus_f42b2.py C:/kyty/f287/f42b2/$O/shader_cfg_tests.exe C:/kyty/f287/f42b2/$O/corpus --workers 4 > $O/corpus_run.txt 2>&1
    grep -q "^rows " $O/corpus_run.txt || { echo "corpus killed"; exit 7; }
    touch $O/done_corpus
  fi
  python rc_corpus_f42b2.py $O/corpus --mutant > $O/rc_corpus.txt 2>&1
fi
python mut_f42b2.py revert >> $O/apply.txt 2>&1
echo "== $M"; cat $O/sha256.txt; for f in $O/rc_stand_m1.txt $O/rc_stand_m0.txt $O/rc_corpus.txt; do [ -e $f ] && echo "$(basename $f): $(tail -1 $f)"; done
echo "$(date -u +%FT%TZ) F42b2 mutant $M bins $(cut -c1-8 $O/sha256.txt | tr '\n' ' ')| stand=1: $(tail -1 $O/rc_stand_m1.txt | cut -c1-100) | stand=0: $([ -e $O/rc_stand_m0.txt ] && tail -1 $O/rc_stand_m0.txt | cut -c1-80) | corpus: $([ -e $O/rc_corpus.txt ] && tail -1 $O/rc_corpus.txt | cut -c1-100)" >> times.txt
touch $O/done_all
