#!/bin/bash
# S18a (HPP-642): submodules of the worktree C:/kyty/s288/s18a/wt in the form of mk_wt_s17a.sh (git archive of the
# gitlinks, ffmpeg-core as a local --shared clone); worktree status before and after. ASCII only.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/s288/s18a/wt
cd $SRC
C=$("$G" -C $WT rev-parse HEAD)
echo "worktree HEAD $C"
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
echo "status lines (0 = clean): $("$G" -C $WT status --short --ignore-submodules=all | wc -l)"
echo SUB OK
