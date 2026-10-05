#!/bin/bash
# S17b3 (HPP-621) window 2: wtS of S17a back to 9635cb0f (the two files of w1.sh), tests rebuilt, own run on the rebuilt
# binary; wtS must end clean at 9635cb0f.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s17b3
WT=C:/kyty/s288/s17a/wtS
B=C:/kyty/s288/s17a/buildS
P=src/graphics/host_gpu/renderer/pipeline
echo "$(date -u +%FT%TZ) w2 start, from: $1" >> $D/times.txt
"$G" -C $WT checkout 9635cb0f -- $P/shaderReplay.cpp $P/shaderReplay.h || exit 1
echo "--- wtS status after restore (0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
"$G" -C $WT log -1 --format=%H
cmd //c "C:\\kyty\\s288\\s17a\\build_s17a.cmd S tests" > $D/tests_post_build.log 2>&1; echo "build rc=$?"
tail -2 $D/tests_post_build.log
sha256sum $B/shader_cfg_tests.exe
(cd $B && KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 KYTY_TESTS_FILTER=WalkBits ./shader_cfg_tests.exe > $D/walkbits_9635cb0f_rebuilt.log 2>&1); echo "rc=$?"
grep -a -E 'walk bits|failed|\[test\]' $D/walkbits_9635cb0f_rebuilt.log
echo "$(date -u +%FT%TZ) w2 end" >> $D/times.txt
