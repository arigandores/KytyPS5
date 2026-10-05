#!/bin/bash
# FS7a (HPP-565, ROADMAP s122 items 467(g)(1), 487(g)(1), 410(g)(6)(i)): copy of mk_wt_fs6a.sh - clean worktree of the
# base by item 410(g)(6)(i) at build time (FS6a 3904522d, the last shipping binary accepted by the lead and installed,
# 9325446c, p.510) + cherry-pick of F18c 10a4800b + F19c 9c726d74 + F19c2 919c1a19 + the FS7a main commit (argument 1).
# Submodules as P23 (git archive of the gitlinks, ffmpeg-core as a local --shared clone); LF as in git
# (core.autocrlf=false). A cherry-pick conflict stops the script (set -e) - stop and question to the lead (the only
# allowed resolution, item 487(g)(1): the neighbouring stand target blocks of CMakeLists.txt, both kept verbatim - by hand).
# Usage: mk_wt_fs7a.sh <FS7a main commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/fs7a/wt
C=3904522d
FS7A=${1:?FS7a commit}
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
for P in 10a4800b 9c726d74 919c1a19 $FS7A; do
	echo "--- cherry-pick $P"
	"$G" -C $WT -c core.autocrlf=false -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick $P
done
"$G" -C $WT log -6 --format='%H %P %s' | cut -c1-160
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
