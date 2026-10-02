#!/bin/bash
# P23 (HPP-404, ROADMAP s122 p.333(e)): clean detached worktree for the port of P-var onto the FS2 shipping tree.
# Base = the commit given as $1 (main tip; its tree outside docs/ equals FS2a 9c9d86ae - checked below), LF as in git
# (core.autocrlf=false), submodules as FS2a (C:/kyty/f287/fs2a/mk_wt_fs2a.sh): git archive of the gitlinks,
# ffmpeg-core as a local --shared clone.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/p283/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/p283/p23/wt
C=${1:?commit}
cd $SRC
echo "--- tree outside docs/ of $C against FS2a 9c9d86ae (empty = equal)"
"$G" diff --stat 9c9d86ae $C -- . ':!docs'
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
