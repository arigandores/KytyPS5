#!/bin/bash
# F20j4 (HPP-652, ROADMAP s122 item 581(d)): the next build step of the F20j4 worktree build, one per call, under the
# watchdog (bstep.sh -> watch_f20j4.py: kills on the lock, STOP or a procload.py process; refuses when one is there).
# Steps in order, each done once its log says BUILD OK / configure done: cfg (configure), emu (kyty_emulator, repeated
# until BUILD OK - ninja is incremental), t (target diag_b32_tests), tst (shader_cfg_tests). State: done_<step> files.
# Usage: bnext.sh [budget seconds, default 30] - runs steps until the budget is spent, a step is refused / killed, or all
# are done (prints ALL BUILT).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f20j4
BUDGET=${1:-30}
T0=$(date +%s)
n=0
for step in cfg emu t tst; do
	[ -e done_$step ] && continue
	while :; do
		NOW=$(date +%s)
		[ $((NOW - T0)) -ge $BUDGET ] && { echo "budget spent before step $step"; exit 9; }
		n=$(date -u +%H%M%S)
		case $step in
			cfg) bash bstep.sh cfg_$n configure; RC=$? ;;
			emu) bash bstep.sh emu_$n; RC=$? ;;
			t) bash bstep.sh t_$n target diag_b32_tests; RC=$? ;;
			tst) bash bstep.sh tst_$n tests; RC=$? ;;
		esac
		if [ $RC -eq 0 ]; then
			touch done_$step
			echo "$(date -u +%FT%TZ) F20j4 build step $step done (log build_${step}_$n.log)" >> C:/kyty/f287/times.txt
			break
		fi
		echo "step $step rc=$RC"
		exit $RC
	done
done
echo ALL BUILT
