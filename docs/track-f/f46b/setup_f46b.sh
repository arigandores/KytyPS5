#!/bin/bash
# Track F, F46b (HPP-799, Red Team): own tooling (copies of the F46a scripts, f46a -> f46b) and two clean worktrees on
# 7e8481e5 (the F46a binary T tree): wt (clean build, the sha256 member) and mwt (mutants m1-m3).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
S="$1"            # scratch dir with mut_f46b.py
A=C:/kyty/KytyPS5/docs/track-f/f46a
D=C:/kyty/f287/f46b
mkdir -p $D
for f in api_chk.sh bstep.sh watch_f46a.py runq.py run_tests_f46a.py build_f46a.cmd mk_wt_f46a.sh; do
	g=$(echo $f | sed 's/f46a/f46b/')
	sed -e 's/f46a/f46b/g' -e 's/F46a/F46b/g' -e 's/HPP-798/HPP-799/g' $A/$f > $D/$g
done
sed -e 's#f287\\f46b\\wt#f287\\f46b\\mwt#' -e 's#f287\\f46b\\build"#f287\\f46b\\mbuild"#' $D/build_f46b.cmd > $D/build_f46bm.cmd
sed -e 's#build_f46b.cmd#build_f46bm.cmd#' -e 's#build_\$N.log#mbuild_$N.log#' $D/bstep.sh > $D/mstep.sh
cp "$S/mut_f46b.py" $D/
grep -n 'SRC=\|BUILD=' $D/build_f46b.cmd $D/build_f46bm.cmd
grep -n 'build_f46\|log' $D/bstep.sh $D/mstep.sh | grep -v '^.*:#'
echo "$(date -u +%FT%TZ) F46b tooling copied from docs/track-f/f46a (f46a -> f46b) into C:/kyty/f287/f46b" >> $D/times.txt
echo SETUP OK
