#!/bin/bash
# S18a2 (HPP-650, ROADMAP s122 item 576(g)(1),(4)): after the builds - status of the S18a worktree, pinned copy, sha256,
# version strings, translator signature hash (generated kytyGitVersion.h vs FS8a; occurrences in the S18a2, S18a and FS8
# exe), installed binary sha256 (read only), gate order of the worktree vs main. Form of C:/kyty/s288/s18a/post.sh.
# ASCII only. Usage: post.sh
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
G="/c/Program Files/Git/cmd/git.exe"
D=C:/kyty/s288/s18a2
WT=C:/kyty/s288/s18a/wt
B=C:/kyty/s288/s18a/build
FS8=C:/kyty/f287/bin/kyty_emulator_2c9b69b9.exe
S18A=C:/kyty/s288/bin/kyty_emulator_0c78df03.exe
mkdir -p $D/bin
echo "worktree HEAD $("$G" -C $WT rev-parse HEAD) tree $("$G" -C $WT rev-parse HEAD^{tree})"
echo "status after build (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
cmp $B/kyty_emulator.exe $B/install/kyty_emulator.exe && echo "build exe = install exe"
TS=$(sha256sum $B/shader_cfg_tests.exe | cut -c1-64)
ES=$(sha256sum $B/install/kyty_emulator.exe | cut -c1-64)
OUT=C:/kyty/s288/bin/kyty_emulator_${ES:0:8}.exe
if [ -e $OUT ]; then echo "copy exists"; cmp $B/install/kyty_emulator.exe $OUT || exit 1; else cp $B/install/kyty_emulator.exe $OUT; fi
cp $B/shader_cfg_tests.exe $D/bin/shader_cfg_tests_${TS:0:8}.exe
V=$(grep -a -o -m1 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $OUT | head -1)
VN=$(grep -a -o 'KytyPS5-20[0-9-]*-[0-9a-f]*-[0-9]*-g[0-9a-f]*' $OUT | sort | uniq -c)
echo "emu $ES $OUT version $V commit $("$G" -C $WT rev-parse HEAD)" > $D/bin_sha.txt
echo "tests $TS $D/bin/shader_cfg_tests_${TS:0:8}.exe" >> $D/bin_sha.txt
cat $D/bin_sha.txt
echo "version strings: $VN"
sha256sum $OUT $D/bin/shader_cfg_tests_${TS:0:8}.exe $S18A $FS8
echo "--- installed binary (read only)"
sha256sum "C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe"
echo "--- signature"
H8=$(grep -a KYTY_SHADER_SOURCE_HASH C:/kyty/f287/fs8a/kytyGitVersion_fs8.h | grep -o '[0-9a-f]\{40\}')
H18=$(grep -a KYTY_SHADER_SOURCE_HASH $B/kytyGitVersion.h | grep -o '[0-9a-f]\{40\}')
echo "FS8a $H8 S18a2 $H18"
[ -n "$H8" ] && [ "$H8" = "$H18" ] && echo "SOURCE HASH S18a2 = FS8a ($H18)" || echo "SOURCE HASH DIFFERS"
for f in $FS8 $S18A $OUT; do
	echo "$f: occurrences of $H8: $(grep -a -o $H8 $f | wc -l)"
done
echo "--- gate order (worktree src)"
python C:/kyty/s113/check_gate_order.py --src $WT/src > $D/gate_order_wt.txt 2>&1; echo "rc=$?"
tail -1 $D/gate_order_wt.txt
cmp <(tr -d '\r' < $D/gate_order_wt.txt) <(tr -d '\r' < $D/gate_order_main.txt) && echo "gate order wt = main (7c31481b)" || diff <(tr -d '\r' < $D/gate_order_main.txt) <(tr -d '\r' < $D/gate_order_wt.txt) | head -20
echo POST DONE
