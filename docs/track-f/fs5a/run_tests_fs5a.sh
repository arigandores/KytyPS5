#!/bin/bash
# FS5a (HPP-509, ROADMAP s122 item 410(g)(1)): members of the tests on the FS5 worktree build.
# (a) shader_cfg_tests at defaults: no KYTY_* knob in the environment except KYTY_TESTS_CONTINUE/KYTY_TESTS_VERBOSE (as FS4a).
# (b) GPU gate of F12d: shader_recompiler_compute_tests --fix-f10-only at KYTY_FIX_F10 unset / 0 / 1 x KYTY_BVH_NATIVE 0 / 1;
#     cwd = run/<case> (the gate builds a ShaderTranslationCache("PPSA21564") there).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
D=C:/kyty/f287/fs5/fs5a
B=$D/build
UNSET=""
for v in $(env | grep -o '^KYTY_[A-Za-z0-9_]*'); do UNSET="$UNSET -u $v"; done
echo "KYTY_* in environment before: ${UNSET:-none}"
mkdir -p $D/run/cfg
cd $D/run/cfg
env $UNSET KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 $B/shader_cfg_tests.exe > $D/cfgtests_defaults.log 2>&1
echo "cfg rc=$?"
for f10 in unset 0 1; do
	for nat in 0 1; do
		[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
		[ -e C:/kyty/f287/STOP ] && exit 4
		mkdir -p $D/run/g_${f10}_${nat}
		cd $D/run/g_${f10}_${nat}
		if [ $f10 = unset ]; then
			env $UNSET KYTY_BVH_NATIVE=$nat $B/shader_recompiler_compute_tests.exe --fix-f10-only > $D/gate_f10${f10}_nat${nat}.txt 2>&1
		else
			env $UNSET KYTY_FIX_F10=$f10 KYTY_BVH_NATIVE=$nat $B/shader_recompiler_compute_tests.exe --fix-f10-only > $D/gate_f10${f10}_nat${nat}.txt 2>&1
		fi
		rc=$?
		echo "gate f10=$f10 nat=$nat rc=$rc last=$(tail -n 1 $D/gate_f10${f10}_nat${nat}.txt)"
	done
done
