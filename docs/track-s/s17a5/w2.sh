#!/bin/bash
# S17a5 (HPP-638) step 2: wtS of S17a (clean at 9238a182 = S17a4) gets the S17a5 main commit by cherry-pick (detached HEAD;
# main after 9238a182 carries the track F code F20j, outside this link), configure, tests + emulator builds from the clean
# worktree, pinned copies, version string, full suite, signature probe (empty job list), K1(7) diffstat. ASCII only.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s17a5
WT=C:/kyty/s288/s17a/wtS
B=C:/kyty/s288/s17a/buildS
X=$1
mkdir -p $D/suite $D/bin $D/sig
echo "--- wtS before"
"$G" -C $WT log -1 --format=%H
echo "status lines (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
"$G" -C $WT checkout -q --detach 9238a182 || exit 1
GIT_AUTHOR_NAME=arigandores GIT_AUTHOR_EMAIL=arigandores@users.noreply.github.com GIT_COMMITTER_NAME=arigandores \
	GIT_COMMITTER_EMAIL=arigandores@users.noreply.github.com "$G" -C $WT cherry-pick $X || exit 1
Y=$("$G" -C $WT log -1 --format=%H)
echo "binary commit $Y (cherry-pick of $X onto 9238a182)"
echo "patch-id main: $("$G" -C C:/kyty/KytyPS5 show $X | "$G" patch-id --stable | cut -c1-40)"
echo "patch-id wtS : $("$G" -C $WT show $Y | "$G" patch-id --stable | cut -c1-40)"
echo "--- diff 9238a182..$Y (src tests CMakeLists.txt)"
"$G" -C $WT diff --stat 9238a182 $Y -- src tests CMakeLists.txt
echo "--- K1(7)"
"$G" -C $WT diff --stat 9238a182 $Y -- src/graphics/shader CMakeLists.txt \
	src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp src/graphics/guest_gpu/gpu_format.h \
	src/graphics/guest_gpu/gpu_defs.h src/graphics/host_gpu/renderer/image/imageInfo.h > $D/k1_7_diffstat.txt
echo "k1_7 lines: $(wc -l < $D/k1_7_diffstat.txt)"
echo "status lines (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
cmd //c "C:\\kyty\\s288\\s17a\\build_s17a.cmd S configure" > $D/cfgS17a5.log 2>&1; echo "configure rc=$?"
cmd //c "C:\\kyty\\s288\\s17a\\build_s17a.cmd S tests" > $D/tests_S17a5_build.log 2>&1; echo "tests build rc=$?"
tail -1 $D/tests_S17a5_build.log
cmd //c "C:\\kyty\\s288\\s17a\\build_s17a.cmd S emu" > $D/emu_S17a5_build.log 2>&1; echo "emu build rc=$?"
tail -1 $D/emu_S17a5_build.log
grep -a -i -E "pipelineCache.cpp.*(warning|error)" $D/emu_S17a5_build.log | head -10
echo "status after build (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
TS=$(sha256sum $B/shader_cfg_tests.exe | cut -c1-64)
ES=$(sha256sum $B/kyty_emulator.exe | cut -c1-64)
cp $B/shader_cfg_tests.exe $D/bin/shader_cfg_tests_${TS:0:8}.exe
cp $B/kyty_emulator.exe C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe
V=$(grep -a -o -m1 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $B/kyty_emulator.exe | head -1)
VN=$(grep -a -o 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $B/kyty_emulator.exe | wc -l)
echo "emu $ES C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe $V commit $Y" > $D/bin_sha.txt
echo "tests $TS $D/bin/shader_cfg_tests_${TS:0:8}.exe" >> $D/bin_sha.txt
cat $D/bin_sha.txt
echo "version string occurrences: $VN"
sha256sum C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe $D/bin/shader_cfg_tests_${TS:0:8}.exe
(cd $B && KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 $D/bin/shader_cfg_tests_${TS:0:8}.exe > $D/suite/suite_S17a5.log 2>&1); echo "suite rc=$?"
echo "tests: $(grep -a -c '^\[test\]' $D/suite/suite_S17a5.log) failed lines: $(grep -a -c 'ShaderCfgTests: failed:' $D/suite/suite_S17a5.log)"
grep -a 'ShaderCfgTests: failed' $D/suite/suite_S17a5.log | head
grep -a 'ShaderReplayLayout:' $D/suite/suite_S17a5.log > $D/layout_S17a5.txt
echo "--- signature probe"
: > $D/sig/jobs_empty.txt
(cd $B && KYTY_S16D_JOBS=$D/sig/jobs_empty.txt KYTY_S16D_OUT=$D/sig/out_S17a5.txt $D/bin/shader_cfg_tests_${TS:0:8}.exe > $D/sig/run_S17a5.txt 2>&1); echo "probe rc=$?"
echo "S17a5: $(cat $D/sig/out_S17a5.txt)"
echo "S17a4: $(cat C:/kyty/s288/s17a4/sig/out_S17a4.txt)"
cmp $D/sig/out_S17a5.txt C:/kyty/s288/s17a4/sig/out_S17a4.txt && echo "sig out = S17a4"
tr -d '\r' < C:/kyty/KytyPS5/docs/track-s/s17a4/layout_S17a4.txt | cmp - <(tr -d '\r' < $D/layout_S17a5.txt) && echo "layout = S17a4"
echo "--- signature string in the emulator binaries"
for f in C:/kyty/s288/bin/kyty_emulator_ed2686da.exe C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe; do
	echo "$f: translator signature hash 9177b4267de1fb8bac7d1113afd8733210addfac occurrences $(grep -a -c 9177b4267de1fb8bac7d1113afd8733210addfac $f); 40-hex near it: $(grep -a -o '[0-9a-f]\{40\}' $f | grep -c 9177b426)"
done
