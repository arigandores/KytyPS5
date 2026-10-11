#!/bin/bash
# FS13a (HPP-787, ROADMAP s122 item 683(g)(1)): copy of the FS11a cp_fs11a.sh - one cherry-pick -x onto the worktree
# C:/kyty/f287/fs13a/wt (base FS11 ee9632be). Order: 227e1b36 (code F33c), e5979953 (stand edition 2), 5237fdff (stand
# edition 3), then the FS13a main commit cbfe8375. On a conflict the script stops (exit 9) with the cherry-pick in
# progress and prints the unmerged files: item 683(g)(1) - a conflict or a dependency on code outside the base is a stop
# and a question to the lead (no resolver in this link).
# Was:
# FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): copy of the FS10a cp_fs10a.sh - one cherry-pick -x onto the worktree
# C:/kyty/f287/fs11a/wt (base FS10 dc5d4712). Order: 73a6e411 (stand F29a), c94c49e0, 726e751e (code F29c), 0db3b3eb (stand
# arm B12-9b), then the FS11a main commit. On a conflict the script stops (exit 9) with the cherry-pick in progress and
# prints the unmerged files: item 647(d)(1) - a conflict or a dependency on code outside the base is a stop and a
# question to the lead (no resolver in this link).
# Usage: cp_fs11a.sh <commit>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/fs13a/wt
C=${1:?commit}
echo "--- cherry-pick $C"
if ! "$G" -C $WT -c core.autocrlf=false -c merge.conflictstyle=diff3 -c user.name="Emu Engineer" -c user.email=emu-engineer@agents.invalid cherry-pick -x "$C"; then
	echo "CONFLICT $C"
	"$G" -C $WT diff --name-only --diff-filter=U
	exit 9
fi
"$G" -C $WT log -1 --format='%H %P %s' | cut -c1-160
echo "--- git status --short (0 = clean)"
"$G" -C $WT status --short --ignore-submodules=all | wc -l
echo CP OK
