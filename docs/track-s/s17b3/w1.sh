#!/bin/bash
# S17b3 (HPP-621) window 1: own run of TestShaderReplayWalkBits on the pinned S17a3 tests binary, then on a2fee0d9 code +
# the 9635cb0f test (wtS of S17a: only shaderReplay.cpp/.h restored to a2fee0d9; w2.sh puts them back and rebuilds).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s17b3
WT=C:/kyty/s288/s17a/wtS
B=C:/kyty/s288/s17a/buildS
P=src/graphics/host_gpu/renderer/pipeline
mkdir -p $D/bin
echo "$(date -u +%FT%TZ) w1 start, from: $1" >> $D/times.txt
echo "--- wtS HEAD and status before"
"$G" -C $WT log -1 --format=%H
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo "--- pinned S17a3 tests binary"
sha256sum C:/kyty/s288/s17a3/bin/shader_cfg_tests_58daf5c5.exe
(cd $B && KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 KYTY_TESTS_FILTER=WalkBits C:/kyty/s288/s17a3/bin/shader_cfg_tests_58daf5c5.exe > $D/walkbits_9635cb0f.log 2>&1); echo "rc=$?"
grep -a -E 'walk bits|failed|\[test\]' $D/walkbits_9635cb0f.log
echo "--- restore a2fee0d9 shaderReplay in wtS"
"$G" -C $WT checkout a2fee0d9 -- $P/shaderReplay.cpp $P/shaderReplay.h || exit 1
"$G" -C $WT diff --stat 9635cb0f -- src tests
"$G" -C $WT diff --stat a2fee0d9 -- src tests
cmd //c "C:\\kyty\\s288\\s17a\\build_s17a.cmd S tests" > $D/tests_pre_build.log 2>&1; echo "build rc=$?"
tail -2 $D/tests_pre_build.log
cp $B/shader_cfg_tests.exe $D/bin/shader_cfg_tests_pre.exe
sha256sum $D/bin/shader_cfg_tests_pre.exe
(cd $B && KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 KYTY_TESTS_FILTER=WalkBits $D/bin/shader_cfg_tests_pre.exe > $D/walkbits_a2fee0d9.log 2>&1); echo "rc=$?"
grep -a -E 'walk bits|failed|\[test\]' $D/walkbits_a2fee0d9.log
echo "$(date -u +%FT%TZ) w1 end" >> $D/times.txt
