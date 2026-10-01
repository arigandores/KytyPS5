#!/bin/bash
# F6c (HPP-375, ROADMAP s122 p.287(e)); a copy of fsa/mk_wt_fsa.sh with the worktree path changed. FSa (HPP-368, ROADMAP s122 p.282(g)(1)): clean detached worktree of main at the FSa commit, LF as in git
# (core.autocrlf=false: the checkout is byte-equal to the blobs; the translator signature depends on line ends,
# p.277(b)(4)); submodules as F5a2 (mk_wt_f5a2.sh): git archive of the gitlinks, ffmpeg-core as a local --shared clone.
# No CRLF rewrite (unlike F4a2/F5a2): the shipment build is the LF tree of the commit.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f6c/wt
C=${1:?commit}
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
echo "--- git status --short (worktree vs its HEAD, literal; empty = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo "--- git diff --stat (literal, worktree vs HEAD)"
"$G" -C $WT diff --stat
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
