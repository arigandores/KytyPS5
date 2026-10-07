#!/bin/bash
# FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): cherry-pick -x onto the base worktree C:/kyty/f287/fs9a/wt (0005e11f):
# 1570d110 (stands and hooks), 21f8ca76 (F24c) - its only allowed conflict is the include context line of regionManager.h
# (resolve_fs9a.py: exactly one block of that form, item 601(b)); then the FS9a main commit (argument 1).
# Any other conflict: the script stops (exit 9) - stop and question to the lead.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/fs9a/wt
FS9A=${1:?FS9a commit}
CP() { "$G" -C $WT -c core.autocrlf=false -c merge.conflictstyle=diff3 -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick -x "$@"; }
echo "--- cherry-pick 1570d110"
CP 1570d110 || { echo "CONFLICT 1570d110"; "$G" -C $WT status --short; exit 9; }
echo "--- cherry-pick 21f8ca76"
if ! CP 21f8ca76; then
	U=$("$G" -C $WT diff --name-only --diff-filter=U)
	echo "unmerged: $U"
	[ "$U" = "src/graphics/host_gpu/regionManager.h" ] || { echo "OTHER CONFLICT"; exit 9; }
	python C:/kyty/f287/fs9a/resolve_fs9a.py $WT || { echo "RESOLVE FAILED"; exit 9; }
	"$G" -C $WT add src/graphics/host_gpu/regionManager.h
	"$G" -C $WT -c core.autocrlf=false -c user.name="Emu Engineer" -c user.email=<agent-email> -c core.editor=true cherry-pick --continue || exit 9
fi
echo "--- cherry-pick $FS9A"
CP $FS9A || { echo "CONFLICT $FS9A"; "$G" -C $WT status --short; exit 9; }
"$G" -C $WT log -4 --format='%H %P %s' | cut -c1-160
echo "--- git status --short (0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo CP OK
