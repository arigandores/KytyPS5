#!/bin/bash
# F16o (HPP-595; copy of f16k2/mrun.sh). Was: F16k2 (HPP-590): one mutant under tstep.sh; after it the worktree diff must equal wt_patch.diff (else: restore from it).
# The restore and its times line wait for the release of a foreign lock first (rule 27: no write under a foreign lock;
# the first form of this script wrote at 20:58:37Z under the lock of the HPP-500 series).
cd C:/kyty/f287/f16o2
WT=C:/kyty/f287/f16k/wt
bash tstep.sh "mut $1" python mut_f16o2.py $1 > mut_$1.log 2>&1
RC=$?
while [ -e C:/kyty/SEALED_RUN.lock ]; do sleep 5; done
echo "$1 rc=$RC $(tail -1 mut/$1.result 2>/dev/null)"
if ! git -C $WT diff | cmp -s - wt_patch.diff; then
	git -C $WT checkout -- src tests && git -C $WT apply C:/kyty/f287/f16o2/wt_patch.diff && echo "  wt restored from wt_patch.diff"
	echo "$(date -u +%FT%TZ) F16o2 mutant $1 rc=$RC left wt mutated - restored from wt_patch.diff" >> C:/kyty/f287/times.txt
fi
git -C $WT diff | cmp -s - wt_patch.diff && echo "  wt = patch" || echo "  WT DIFFERS"
