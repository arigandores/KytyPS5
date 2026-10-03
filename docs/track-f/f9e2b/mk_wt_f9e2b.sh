#!/bin/bash
# F9e2b (HPP-429, ROADMAP s122 item 353(g)(4)): clean detached worktree on 4414e235 (P23 code) + the F9e2 commit 23a0b3f2
# (cherry-pick) for KYTY_FIX_B42 M2c F9e2b; copy of C:/kyty/f287/f9/f9e2/mk_wt_f9e2.sh, itself a copy of
# C:/kyty/p283/p30b/mk_wt_p30b.sh with the base and the path changed: LF as in git
# (core.autocrlf=false), submodules as P23 (git archive of the gitlinks, ffmpeg-core as a local --shared clone).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f9/f9e2b/wt
C=4414e235
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
echo "--- cherry-pick F9e2 23a0b3f2"
"$G" -C $WT -c core.autocrlf=false cherry-pick 23a0b3f2
"$G" -C $WT log -2 --format='%H %P %s' | cut -c1-160
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
