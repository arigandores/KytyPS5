#!/bin/bash
# Track F, F46b (HPP-799): one mutant m in the own worktree wt (7e8481e5): reset the two mutated files to HEAD, apply m
# (mut_f46b.py; "clean" - reset only), build shader_recompiler_compute_tests (loop_f46b.sh), run --f16k-only in the 17 arms
# (run_tests_f46b.py f16k) into mut/<m>.txt. Usage: mstep_f46b.sh <m|clean> <budget s>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f46b
M=$1; BUDGET=$2; T0=$(date +%s)
G="/c/Program Files/Git/cmd/git.exe"
mkdir -p mut
if [ ! -e mut/.applied_$M ]; then
	"$G" -C wt checkout -- src/graphics/host_gpu/renderer/cache/textureCache.cpp src/graphics/host_gpu/renderer/diagF5.cpp
	rm -f mut/.applied_*
	if [ "$M" != clean ]; then python mut_f46b.py C:/kyty/f287/f46b/wt $M || exit 2; fi
	"$G" -C wt diff --stat | tail -1
	"$G" -C wt diff > mut/$M.diff
	touch mut/.applied_$M
	rm -f mut/.built_$M
	echo "$(date -u +%FT%TZ) F46b mutant $M applied to wt ($(wc -l < mut/$M.diff) diff lines)" >> times.txt
fi
if [ ! -e mut/.built_$M ]; then
	bash loop_f46b.sh $(( BUDGET - ($(date +%s) - T0) )) "build tests $M" mut/b_$M.log -- cmd //c 'C:\kyty\f287\f46b\build_f46b.cmd' target shader_recompiler_compute_tests || exit $?
	touch mut/.built_$M
	echo "$(date -u +%FT%TZ) F46b mutant $M built: tests exe sha256 $(sha256sum build/shader_recompiler_compute_tests.exe | cut -c1-8)" >> times.txt
fi
LEFT=$(( BUDGET - ($(date +%s) - T0) ))
bash loop_f46b.sh $LEFT "f16k $M" mut/r_$M.log -- python run_tests_f46b.py f16k build/shader_recompiler_compute_tests.exe mut/$M.txt
RC=$?
[ $RC -le 1 ] && echo "$(date -u +%FT%TZ) F46b mutant $M f16k: $(tail -1 mut/$M.txt), FAIL arms $(grep -c ' FAIL$' mut/$M.txt)" >> times.txt
grep -E "^=== arm" mut/$M.txt | awk '{print $3, $NF}' | tr '\n' ' '; echo; tail -1 mut/$M.txt
exit $RC
