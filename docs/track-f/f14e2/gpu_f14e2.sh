#!/bin/bash
# F14e2 (HPP-545; copy of the F14e script of HPP-505, ROADMAP s122 item 409(g)(1)): GPU gate runs of shader_recompiler_compute_tests under the watchdog
# watch_f14e2.py (item 431(v)); each run in its own folder C:/kyty/f287/f14e2/gpu/<name>, all KYTY_* removed.
#   g1  KYTY_FIX_F19=1  --fix-f19-only
#   g0  KYTY_FIX_F19=0  --fix-f19-only
#   gu  (unset)         --fix-f19-only
#   c1  KYTY_FIX_F19=1  --fix-f19-comparison-depth   (must pass)
#   c0  KYTY_FIX_F19=0  --fix-f19-comparison-depth   (must fail with the old text)
# Usage: gpu_f14e2.sh [names...]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
D=C:/kyty/f287/f14e2
EXE=$D/bin/shader_recompiler_compute_tests.exe
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
	python $D/watch_f14e2.py --limit 300 --tag "gpu $n" -- $EXE $A > run.log 2>&1
	RC=$?
	unset KYTY_FIX_F19
	echo "$n KYTY_FIX_F19=${V:-unset} $A watchdog/test rc=$RC: $(grep -aE '^(ALL OK|KILLED|STOPPED|REFUSED)|failed|FAILED|missing required' run.log | head -3 | tr '\n' ' ')"
	[ $RC = 3 ] || [ $RC = 4 ] || [ $RC = 7 ] || [ $RC = 8 ] && exit $RC
done
exit 0
