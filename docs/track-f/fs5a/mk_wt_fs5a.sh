#!/bin/bash
# FS5a (HPP-509, ROADMAP s122 item 410(g)(1), (6)(i)): copy of mk_wt_fs4a.sh on the FS4 worktree commit 3d0e46da (base by
# item 410(g)(6)(i): S12a not accepted) + cherry-pick of the F12d commit 1833ee28 (the FS5a commit is cherry-picked after
# the main commit). Was: FS4a - d515b901 + cherry-pick 68602c4f; submodules as P23 (git archive of the gitlinks,
# ffmpeg-core as a local --shared clone); LF as in git (core.autocrlf=false). A cherry-pick conflict stops the script
# (set -e) - stop and question to the lead (item 410(g)(1)).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/fs5/fs5a/wt
C=3d0e46da
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
echo "--- cherry-pick F12d 1833ee28"
"$G" -C $WT -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick 1833ee28

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
