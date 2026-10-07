# F25d (HPP-667, ROADMAP s122 items 596(v), 599): copy of f20j4/mk_wt_f20j4.sh, names f20j4 -> f25d, base 0005e11f (S18a2, source of the installed S18 b3cee576); the 5 KYTY_DIAG_B32 commits are cherry-picked by pick_f25d.sh.
#!/bin/bash
# F20j4 (HPP-652, ROADMAP s122 item 581(d)): copy of f20j3 script with names f20j3 -> f20j4; worktree base 9db7938b (F20j3 test binary source).
# F20j3 (HPP-646, ROADMAP s122 item 574(g)(6)): copy of f20j2/mk_wt_f20j2.sh, names changed (f20j2 -> f20j3); worktree base 61b410bf (= 302347b4 + 875720c5 + 0df13a66 + 61b410bf).
# F20j2 (HPP-633, ROADMAP s122 item 552(d)): copy of the F20j mk_wt_f20j.sh, names changed (f20j -> f20j2); worktree base 0df13a66.
# F20j (HPP-629, ROADMAP s122 items 550(z), 410(g)(6)(i)): copy of f16k/mk_wt_f16k.sh; base 302347b4 (source of the installed FS8 2c9b69b9).
# F16k (HPP-583, ROADMAP s122 item 492(z)(5)): copy of f23a/mk_wt_f23a.sh on main c0789a34 (code base before F16k): LF (core.autocrlf=false), submodules by git archive of the gitlinks, ffmpeg-core as a local --shared clone.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f25d/wt
C=0005e11f
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
