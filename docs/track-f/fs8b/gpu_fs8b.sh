#!/bin/bash
# FS8b (HPP-572, Red Team, item 471(g)(2) own run of (g)(1)(b)): copy of the FS8a gpu_fs8a.sh with D=C:/kyty/f287/fs8b and watch_fs8b.py; logic unchanged.
# FS8a (HPP-571; copy of the F14e2 gpu_f14e2.sh of HPP-545, paths changed; was F14e2 copy of the F14e script of HPP-505, ROADMAP s122 item 409(g)(1)): GPU gate runs of shader_recompiler_compute_tests under the watchdog
# watch_fs8b.py (item 431(v)); each run in its own folder C:/kyty/f287/fs8a/gpu/<name>, all KYTY_* removed.
#   g1  KYTY_FIX_F19=1  --fix-f19-only
#   g0  KYTY_FIX_F19=0  --fix-f19-only
#   gu  (unset)         --fix-f19-only
#   c1  KYTY_FIX_F19=1  --fix-f19-comparison-depth   (must pass)
#   c0  KYTY_FIX_F19=0  --fix-f19-comparison-depth   (must fail with the old text)
# Usage: gpu_f14e2.sh [names...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
D=C:/kyty/f287/fs8b
EXE=$D/build/shader_recompiler_compute_tests.exe
for n in ${@:-g1 g0 gu c1 c0}; do
	case $n in
		g1) V=1; A=--fix-f19-only ;;
		g0) V=0; A=--fix-f19-only ;;
		gu) V=; A=--fix-f19-only ;;
		c1) V=1; A=--fix-f19-comparison-depth ;;
		c0) V=0; A=--fix-f19-comparison-depth ;;
	esac
	bash $D/api_chk.sh "gpu $n" > /dev/null || exit $?
	mkdir -p $D/gpu/$n
	cd $D/gpu/$n
	for k in $(env | sed -n 's/^\(KYTY_[A-Za-z0-9_]*\)=.*/\1/p'); do unset $k; done
	if [ -n "$V" ]; then export KYTY_FIX_F19=$V; else unset KYTY_FIX_F19; fi
	python $D/watch_fs8b.py --limit 300 --tag "gpu $n" -- $EXE $A > run.log 2>&1
	RC=$?
	unset KYTY_FIX_F19
	echo "$n KYTY_FIX_F19=${V:-unset} $A watchdog/test rc=$RC: $(grep -aE '^(ALL OK|KILLED|STOPPED|REFUSED)|failed|FAILED|missing required' run.log | head -3 | tr '\n' ' ')"
	[ $RC = 3 ] || [ $RC = 4 ] || [ $RC = 7 ] || [ $RC = 8 ] && exit $RC
done
exit 0
