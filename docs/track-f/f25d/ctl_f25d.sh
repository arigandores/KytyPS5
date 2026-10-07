#!/bin/bash
# F25d (HPP-667; items 596(v), 599(v) RC9): negative control - the F25d test file in the F20j4 worktree (f2307b02 code,
# uncommitted; the cases needing the F25 fields are compiled out there - no KYTY_DIAG_B32_F25), diag_b32_tests built in
# the F20j4 build directory and run; the test file is restored by git checkout afterwards.
# Expected on F20j4: RC9 cases (TestRing, TestMandatoryAndCuts) and the rest of the old cases pass; the F25 cases E1/E2,
# 150 mandatory, window 6.6 s and 20 000 records FAIL; window 21 s passes (exhausted on both).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/f287/f25d
W=C:/kyty/f287/f20j4/wt
cp $D/wt/tests/DiagB32Tests.cpp $W/tests/DiagB32Tests.cpp
python $D/watch_f25d.py --limit 540 --tag "ctl F20j4 diag_b32_tests" -- cmd //c "C:\kyty\f287\f20j4\build_f20j4.cmd" target diag_b32_tests > $D/ctl_build.log 2>&1
echo "build rc=$?"
C:/kyty/f287/f20j4/build/diag_b32_tests.exe > $D/tests_out/ctl_f20j4.log 2>&1
echo "tests rc=$?"
"$G" -C $W checkout -- tests/DiagB32Tests.cpp
echo "restored: $("$G" -C $W status --short --ignore-submodules=all | wc -l) changed files"
"$G" -C $W log -1 --format=%H
