#!/bin/bash
# F14c (HPP-489, ROADMAP s122 item 400(b)): clean detached worktree on the current main for the B11 test fix - copy of
# docs/track-f/f11d/mk_wt_f11d.sh with the base (argument 1, a commit of main) and the path changed: LF as in git
# (core.autocrlf=false), submodules as F11d (git archive of the gitlinks, ffmpeg-core as a local --shared clone).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f14c/wt
C=$1
[ -n "$C" ] || { echo "usage: mk_wt_f14c.sh <commit>"; exit 2; }
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
echo "--- git status --short (worktree vs its HEAD; 0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo "--- CR bytes in src/ and tests/ (worktree files)"
python - "$WT" <<'PYEOF'
import os, sys
for sub in ("src", "tests"):
    root = os.path.join(sys.argv[1], sub)
    n = files = 0
    for d, _, fs in os.walk(root):
        for f in fs:
            files += 1
            if b"\r" in open(os.path.join(d, f), "rb").read():
                n += 1
    print(sub, "files", files, "with CR", n)
PYEOF
echo WT OK
