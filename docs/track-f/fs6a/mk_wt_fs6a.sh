#!/bin/bash
# FS6a (HPP-555, ROADMAP s122 items 454(g)(1), 410(g)(6)(i)): copy of mk_wt_fs5a.sh / mk_wt_f15c.sh - clean worktree of the
# base by item 410(g)(6)(i) at build time (S12a 4d9e8ab7, the last shipping binary accepted by the lead and installed,
# adb0c82f, p.437) + cherry-pick of F15c a86a5ad0 + cherry-pick of the FS6a main commit (argument 1). Submodules as P23
# (git archive of the gitlinks, ffmpeg-core as a local --shared clone); LF as in git (core.autocrlf=false). A cherry-pick
# conflict stops the script (set -e) - stop and question to the lead (item 454(g)(1)).
# Usage: mk_wt_fs6a.sh <FS6a main commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/fs6a/wt
C=4d9e8ab7
FS6A=${1:?FS6a commit}
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
echo "--- cherry-pick F15c a86a5ad0"
"$G" -C $WT -c core.autocrlf=false -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick a86a5ad0
echo "--- cherry-pick FS6a $FS6A"
"$G" -C $WT -c core.autocrlf=false -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick $FS6A
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
