#!/bin/bash
# F25d (HPP-667; item 599(b)(8)): equivalence of the index fix - the worktree files are rebuilt from HEAD by the patch
# scripts: (1) F25 C1-C6 + tests + dump mode -> build -> dump bench_ref2 (the quadratic code of F20j4 with the F25
# constants); (2) + the index fix -> build -> dump bench_idx2; every text equal byte for byte -> EQUIV OK.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/f287/f25d
cd $D/wt
"$G" checkout HEAD -- src/common/diagB32.h src/common/diagB32.cpp tests/DiagB32Tests.cpp
cd $D
python patch_f25d.py $D/wt
python patch_f25d_tests.py $D/wt
python patch_f25d_dump.py $D/wt
bash bstep.sh e1 target diag_b32_tests | tail -1
rm -rf bench_ref2 bench_idx2; mkdir -p bench_ref2 bench_idx2
./build/diag_b32_tests.exe --dump-bench $D/bench_ref2
python patch_f25d_index.py $D/wt
bash bstep.sh e2 target diag_b32_tests | tail -1
./build/diag_b32_tests.exe --dump-bench $D/bench_idx2
ok=1
for f in bench_ref2/*.txt; do
	b=$(basename $f)
	if cmp -s $f bench_idx2/$b; then echo "EQUAL $b $(sha256sum < $f | cut -c1-16)"; else echo "DIFF $b"; ok=0; fi
done
[ $ok = 1 ] && echo "EQUIV OK" || { echo "EQUIV FAILED"; exit 1; }
