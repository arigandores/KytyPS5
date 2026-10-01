#!/bin/bash
# F5a2 (HPP-366, ROADMAP p.280(d)): detached worktree of 4fc501f4 + cherry-pick d2811535 (F5a) + 01ca15d1 (F5a2), no
# branches; submodules as S5c (C:/kyty/s288/s5c/mk_wt.sh): git archive of the gitlinks (= HEAD), ffmpeg-core as a local
# --shared clone at its gitlink; then the 27 files of the signature set that are CRLF in the main working tree are
# written as CRLF (sig_f4a2.py --write), so the generated signature is 699c1e4b.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
SRC=C:/kyty/KytyPS5
WT=C:/kyty/f287/f5a2/wt
export GIT_AUTHOR_NAME="Emu Engineer" GIT_AUTHOR_EMAIL="noreply@anthropic.com"
export GIT_COMMITTER_NAME="Emu Engineer" GIT_COMMITTER_EMAIL="noreply@anthropic.com"
cd $SRC
"$G" worktree add --detach $WT 4fc501f4
"$G" -C $WT cherry-pick d2811535 01ca15d1
echo "--- worktree HEAD"
"$G" -C $WT log -3 --format='%H %s' | cut -c1-120
"$G" ls-tree 4fc501f4 3rdparty/ | while read mode type sha path; do
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
python C:/kyty/f287/f4a2/sig_f4a2.py --write $WT
echo "--- git diff --stat 4fc501f4 (worktree, literal)"
"$G" -C $WT diff --stat 4fc501f4 -- src | tail -3
echo "--- git diff --stat 4fc501f4 --ignore-cr-at-eol"
"$G" -C $WT diff --stat --ignore-cr-at-eol 4fc501f4 -- src
echo "--- git status --short (worktree vs its HEAD)"
"$G" -C $WT status --short | wc -l
echo "--- git diff --ignore-cr-at-eol --stat (worktree vs its HEAD; empty = clean up to CR, M1)"
"$G" -C $WT diff --ignore-cr-at-eol --stat
echo WT OK
