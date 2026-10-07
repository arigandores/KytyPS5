#!/bin/bash
# F25d (HPP-667, ROADMAP s122 item 596(v)): cherry-pick of the 5 KYTY_DIAG_B32 commits onto S18a2 0005e11f in the worktree wt
# (original author and message kept, committer = Emu Engineer); member of item 380 - git cherry "-" for each.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/f25d/wt
export GIT_COMMITTER_NAME="<agent name>" GIT_COMMITTER_EMAIL="<agent email>" # the agent identity (the run used the real values; replaced for the privacy check)
for c in 875720c5 0df13a66 61b410bf 9db7938b f2307b02; do
	"$G" -C $WT -c core.autocrlf=false cherry-pick $c
	echo "picked $c -> $("$G" -C $WT rev-parse HEAD)"
done
echo "--- git cherry 0005e11f..f2307b02 against wt HEAD"
"$G" -C $WT cherry -v HEAD f2307b02 302347b4
echo "--- shortstat 0005e11f..HEAD vs 302347b4..f2307b02"
"$G" -C $WT diff --shortstat 0005e11f HEAD
"$G" -C $WT diff --shortstat 302347b4 f2307b02
echo "--- tree"
"$G" -C $WT rev-parse HEAD^{tree}
echo "--- diag files equal to f2307b02 (empty = equal)"
"$G" -C $WT diff --stat f2307b02 HEAD -- src/common/diagB32.h src/common/diagB32.cpp tests/DiagB32Tests.cpp
echo PICK OK
