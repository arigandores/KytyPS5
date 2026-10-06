#!/bin/bash
# S18a (HPP-642, ROADMAP s122 items 569(d)(1)(3)-(4), 571(g)): after the builds - status, pinned copies, sha256, version
# string, translator signature (KYTY_SHADER_SOURCE_HASH of the generated kytyGitVersion.h of S18 and of FS8a, line of
# _ShaderSeeds/PPSA21564/compatibility.txt, occurrences of the hash in the S18 and FS8 exe), gate order of the worktree.
# The installed binary is not touched. ASCII only. Usage: post.sh
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s18a
WT=$D/wt
B=$D/build
FS8=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
mkdir -p $D/bin C:/kyty/s288/bin
echo "worktree HEAD $("$G" -C $WT rev-parse HEAD) tree $("$G" -C $WT rev-parse HEAD^{tree})"
echo "status after build (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
cmp $B/kyty_emulator.exe $B/install/kyty_emulator.exe && echo "build exe = install exe"
TS=$(sha256sum $B/shader_cfg_tests.exe | cut -c1-64)
ES=$(sha256sum $B/install/kyty_emulator.exe | cut -c1-64)
[ -e C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe ] && { echo "copy exists"; cmp $B/install/kyty_emulator.exe C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe || exit 1; } || cp $B/install/kyty_emulator.exe C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe
cp $B/shader_cfg_tests.exe $D/bin/shader_cfg_tests_${TS:0:8}.exe
V=$(grep -a -o -m1 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $B/install/kyty_emulator.exe | head -1)
VN=$(grep -a -o 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $B/install/kyty_emulator.exe | sort | uniq -c)
echo "emu $ES C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe version $V commit $("$G" -C $WT rev-parse HEAD)" > $D/bin_sha.txt
echo "tests $TS $D/bin/shader_cfg_tests_${TS:0:8}.exe" >> $D/bin_sha.txt
cat $D/bin_sha.txt
echo "version strings: $VN"
sha256sum C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe $D/bin/shader_cfg_tests_${TS:0:8}.exe $FS8 C:/kyty/f287/fs8a/build/shader_cfg_tests.exe
echo "--- installed binary (read only)"
sha256sum "C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
echo "--- signature"
echo "FS8 compatibility.txt: $(head -1 'C:/kyty/KytyPS5/ps5 em/_ShaderSeeds/PPSA21564/compatibility.txt' | tr -d '\r')"
echo "FS8a kytyGitVersion_fs8.h: $(grep -a KYTY_SHADER_SOURCE_HASH C:/kyty/f287/fs8a/kytyGitVersion_fs8.h | tr -d '\r')"
echo "FS8a build kytyGitVersion.h: $(grep -a KYTY_SHADER_SOURCE_HASH C:/kyty/f287/fs8a/build/kytyGitVersion.h | tr -d '\r')"
echo "S18 build kytyGitVersion.h: $(grep -a KYTY_SHADER_SOURCE_HASH $B/kytyGitVersion.h | tr -d '\r')"
H8=$(grep -a KYTY_SHADER_SOURCE_HASH C:/kyty/f287/fs8a/kytyGitVersion_fs8.h | grep -o '[0-9a-f]\{40\}')
H18=$(grep -a KYTY_SHADER_SOURCE_HASH $B/kytyGitVersion.h | grep -o '[0-9a-f]\{40\}')
[ -n "$H8" ] && [ "$H8" = "$H18" ] && echo "SOURCE HASH S18 = FS8a ($H18)" || echo "SOURCE HASH DIFFERS"
for f in $FS8 C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe; do
	echo "$f: occurrences of $H8: $(grep -a -o $H8 $f | wc -l); of ':robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19': $(grep -a -o ':robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19' $f | wc -l); of 'KytySC3': $(grep -a -o KytySC3 $f | wc -l)"
done
echo "--- gate order (worktree src)"
python C:/kyty/s113/check_gate_order.py --src $WT/src > $D/gate_order_wt.txt 2>&1; echo "rc=$?"
tail -1 $D/gate_order_wt.txt
cmp <(tr -d '\r' < $D/gate_order_wt.txt) <(tr -d '\r' < $D/gate_order_main.txt) && echo "gate order wt = main (fe4b227a)" || diff <(tr -d '\r' < $D/gate_order_main.txt) <(tr -d '\r' < $D/gate_order_wt.txt) | head -20
echo POST DONE
