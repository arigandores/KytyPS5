#!/bin/bash
# F20j3 (HPP-646, ROADMAP s122 item 574(g)(6)): copy of f20j2/mk_wtm_f20j2.sh, names changed (f20j2 -> f20j3), base 2cde5ef2 (main with F20j3).
# F20j2 (HPP-633, ROADMAP s122 item 552(d)): copy of the F20j mk_wtm_f20j.sh for main 18dd03a6 (compile check of the cherry-pick of 61b410bf).
# F20j (HPP-629, ROADMAP s122 items 550(z), 410(g)(6)(i)): copy of f16k/mk_wt_f16k.sh; base 302347b4 (source of the installed FS8 2c9b69b9).
# F20j: the same for main 9bd96f44 (compile check of the cherry-pick with its one resolved conflict).
# F16k (HPP-583, ROADMAP s122 item 492(z)(5)): copy of f23a/mk_wt_f23a.sh on main c0789a34 (code base before F16k): LF (core.autocrlf=false), submodules by git archive of the gitlinks, ffmpeg-core as a local --shared clone.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f20j3/wtm
C=2cde5ef2
cd $SRC
"$G" -c core.autocrlf=false worktree add --detach $WT $C
echo "--- worktree HEAD"
"$G" -C $WT log -1 --format='%H %s' | cut -c1-120
"$G" ls-tree $C 3rdparty/ | while read mode type sha path; do
	[ "$type" = commit ] || continue
	if [ "$path" = 3rdparty/ffmpeg-core ]; then
		rm -rf "$WT/$path"
		"$G" clone -q --shared --no-checkout "$SRC/$path" "$WT/$path"
		"$G" -C "$WT/$path" checkout -q "$sha"
	else
		mkdir -p "$WT/$path"
		"$G" -C "$SRC/$path" archive "$sha" | tar -x -C "$WT/$path"
	fi
	echo "submodule $path $sha"
done
"$G" -C $WT log -4 --format='%H %P %s' | cut -c1-160
echo "--- git status --short (worktree vs its HEAD; 0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo "--- CR bytes in src/ (worktree files)"
python - "$WT" <<'PYEOF'
import os, sys
root = os.path.join(sys.argv[1], "src")
n = files = 0
for d, _, fs in os.walk(root):
    for f in fs:
        files += 1
        if b"\r" in open(os.path.join(d, f), "rb").read():
            n += 1
print("files", files, "with CR", n)
PYEOF
echo WT OK
