#!/bin/bash
# F16d2 (HPP-569, ROADMAP s122 item 470(v)(3)-(5)): one mutant of the test site - apply (mutate_f16d2.py), build the target
# shader_recompiler_compute_tests (bloop.sh), run the three arms (tloop.sh site), revert, and check that the worktree is back
# to the development state (sha256 of the touched files before = after). Output: mut/<name>.site.txt, mut/<name>.txt.
# Usage: mrun.sh <mutant>
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f16d2
M=$1
mkdir -p mut
WT=C:/kyty/f287/f16d2/wt
FILES="src/graphics/host_gpu/renderer/diagF5.cpp src/graphics/host_gpu/renderer/pipeline/descriptors.cpp src/graphics/host_gpu/renderer/cache/textureCache.cpp"
before=$(cd $WT && sha256sum $FILES | sha256sum | cut -c1-16)
python mutate_f16d2.py $M apply || exit 9
BUDGET=${BBUDGET:-420} bash bloop.sh mut_$M target shader_recompiler_compute_tests > mut/$M.build.txt 2>&1
B=$?
if [ $B = 0 ]; then
	BUDGET=150 bash tloop.sh site C:/kyty/f287/f16d2/build/shader_recompiler_compute_tests.exe C:/kyty/f287/f16d2/mut/$M.site.txt > mut/$M.run.txt 2>&1
	R=$?
else
	R=build$B
fi
python mutate_f16d2.py $M revert || exit 9
after=$(cd $WT && sha256sum $FILES | sha256sum | cut -c1-16)
{
	echo "mutant $M build=$B site_rc=$R tree_before=$before tree_after=$after $( [ "$before" = "$after" ] && echo REVERTED || echo NOT-REVERTED ) $(date -u +%FT%TZ)"
	grep -aE "^=== arm|failed at|FAILED|NOT OK|ALL OK" mut/$M.site.txt 2>/dev/null | head -12
} | tee mut/$M.txt
