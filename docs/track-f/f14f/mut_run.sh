#!/bin/bash
# F14f (HPP-506): one source mutant end to end in the F14f worktree - apply, build shader_cfg_tests and
# shader_recompiler_compute_tests (under the watchdog copy), own gate and suite runs and readers, optional corpus, restore.
# Usage: mut_run.sh <M> [corpus]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
D=C:/kyty/f287/f14f
M=$1
BASE=C:/kyty/f287/f14e/base/shader_cfg_tests.exe
cd $D
mkdir -p mut/$M
echo "$(date -u +%FT%TZ) F14f mutant $M start: lock absent, STOP absent" >> C:/kyty/f287/times.txt
python f14f_mut.py apply $M > mut/$M/apply.txt 2>&1 || { cat mut/$M/apply.txt; python f14f_mut.py restore; exit 9; }
cat mut/$M/apply.txt
"/c/Program Files/Git/cmd/git.exe" -C wt diff --stat | cat > mut/$M/diffstat.txt
"/c/Program Files/Git/cmd/git.exe" -C wt diff | cat > mut/$M/mutant.diff
python watch_f14f_copy.py --limit 590 --tag "F14f mut $M tests" -- cmd //c "C:\\kyty\\f287\\f14f\\build_f14f.cmd" tests > mut/$M/build_tests.log 2>&1 || { echo build tests failed; python f14f_mut.py restore; exit 10; }
[ -e C:/kyty/SEALED_RUN.lock ] && { python f14f_mut.py restore; exit 3; }
python watch_f14f_copy.py --limit 590 --tag "F14f mut $M compute" -- cmd //c "C:\\kyty\\f287\\f14f\\build_f14f.cmd" target shader_recompiler_compute_tests > mut/$M/build_compute.log 2>&1 || { echo build compute failed; python f14f_mut.py restore; exit 10; }
sha256sum build/shader_cfg_tests.exe build/shader_recompiler_compute_tests.exe > mut/$M/exe_sha.txt
[ -e C:/kyty/SEALED_RUN.lock ] && { python f14f_mut.py restore; exit 3; }
python f14f_gate.py run $D/build/shader_recompiler_compute_tests.exe $D/mut/$M/gate > mut/$M/gate_run.txt 2>&1
python f14f_gate.py read $D/mut/$M/gate > mut/$M/gate_read.txt 2>&1
[ -e C:/kyty/SEALED_RUN.lock ] && { python f14f_mut.py restore; exit 3; }
python f14f_suite.py run $BASE $D/build/shader_cfg_tests.exe $D/mut/$M/suite > mut/$M/suite_run.txt 2>&1
python f14f_suite.py read $D/mut/$M/suite > mut/$M/suite_read.txt 2>&1
if [ "$2" = corpus ]; then
	[ -e C:/kyty/SEALED_RUN.lock ] && { python f14f_mut.py restore; exit 3; }
	python f14f_corpus.py $BASE $D/build/shader_cfg_tests.exe $D/mut/$M/corpus --configs base,f0,fu,f1,f1m16,f1m8 > mut/$M/corpus.txt 2>&1
fi
python f14f_mut.py restore
echo "--- $M gate: $(tail -1 mut/$M/gate_read.txt) | suite: $(tail -1 mut/$M/suite_read.txt) | corpus: $([ -f mut/$M/corpus.txt ] && tail -1 mut/$M/corpus.txt || echo n/a)"
grep -h "FAIL\|NOT OK" mut/$M/gate_read.txt | head -12
grep -h "differing from base\|probe lines\|failure lines [1-9]\|NOT OK" mut/$M/suite_read.txt | head -12
[ -f mut/$M/corpus.txt ] && grep -h "rows != base\|changed\|invariant\|NOT OK\|ALL OK" mut/$M/corpus.txt
echo "$(date -u +%FT%TZ) F14f mutant $M done: gate $(tail -1 mut/$M/gate_read.txt | cut -c1-60) | suite $(tail -1 mut/$M/suite_read.txt) | corpus $([ -f mut/$M/corpus.txt ] && tail -1 mut/$M/corpus.txt || echo n/a); restored" >> C:/kyty/f287/times.txt
exit 0
