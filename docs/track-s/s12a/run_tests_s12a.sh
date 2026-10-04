#!/bin/bash
# S12a (HPP-494, ROADMAP s122 item 408(l)): shader_cfg_tests at defaults on the S12 worktree build - no KYTY_* knob in the
# environment except KYTY_TESTS_CONTINUE/KYTY_TESTS_VERBOSE (as FS4a / FS5a, part (a) of run_tests_fs5a.sh).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
D=C:/kyty/s288/s12a
B=$D/build
UNSET=""
for v in $(env | grep -o '^KYTY_[A-Za-z0-9_]*'); do UNSET="$UNSET -u $v"; done
echo "KYTY_* in environment before: ${UNSET:-none}"
mkdir -p $D/run/cfg
cd $D/run/cfg
env $UNSET KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 $B/shader_cfg_tests.exe > $D/cfgtests_defaults.log 2>&1
echo "cfg rc=$?"
