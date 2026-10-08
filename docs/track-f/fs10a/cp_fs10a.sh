#!/bin/bash
# FS10a (HPP-684, ROADMAP s122 item 624(e)(1)): one cherry-pick -x onto the worktree C:/kyty/f287/fs10a/wt (base FS9
# 11164d72). Order: a8ee1b05, b4ee756a, 0e4b2f5a (F25k), 5064c5bb (F25k2), then the FS10a main commit. On a conflict the
# script stops (exit 9) with the cherry-pick in progress and prints the unmerged files and the conflict blocks: the only
# allowed resolution is "base side" for context lines of the KYTY_DIAG_B32 code (absent in the base), done by a named
# resolver script and checked by verify_fs10a.py (equal changed lines); any other conflict - stop and question to the lead.
# Usage: cp_fs10a.sh <commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/fs10a/wt
C=${1:?commit}
echo "--- cherry-pick $C"
if ! "$G" -C $WT -c core.autocrlf=false -c merge.conflictstyle=diff3 -c user.name="Emu Engineer" -c user.email=<agent-email> cherry-pick -x "$C"; then
	echo "CONFLICT $C"
	"$G" -C $WT diff --name-only --diff-filter=U
	exit 9
fi
"$G" -C $WT log -1 --format='%H %P %s' | cut -c1-160
echo "--- git status --short (0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo CP OK
