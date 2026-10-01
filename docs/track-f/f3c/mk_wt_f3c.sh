#!/bin/bash
# F3c (HPP-341): detached worktree of 478868b5 (no branches); submodules as C:/kyty/f287/f4a2/mk_wt_f4a2.sh.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f3c/wt
cd $SRC
"$G" worktree add --detach $WT 478868b5
"$G" ls-tree 478868b5 3rdparty/ | while read mode type sha path; do
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
"$G" -C $WT log -1 --format='%H'
"$G" -C $WT diff --stat 478868b5 -- src tests | tail -1
echo WT OK
