#!/bin/bash
# FS8a (HPP-571, ROADMAP s122 item 523(v)): cherry-pick chain of variant 1b in the worktree on FS7a d6ee2dc8:
# fcaf141b -> 082d1612 -> tests part of ff953d4f (docs/track-s/s14j dropped) -> f98e842c -> e46f55d4.
# Any conflict stops the script (set -e) - stop and question to the lead (item 523(v)).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/fs8a/wt
export GIT_AUTHOR_NAME="Emu Engineer" GIT_AUTHOR_EMAIL=<agent-email>
export GIT_COMMITTER_NAME="Emu Engineer" GIT_COMMITTER_EMAIL=<agent-email>
g() { "$G" -C $WT -c core.autocrlf=false "$@"; }
echo "--- base"; g log -1 --format='%H %s' | cut -c1-100
[ "$(g rev-parse HEAD)" = "$(g rev-parse d6ee2dc8)" ] || { echo "HEAD is not d6ee2dc8"; exit 9; }
[ "$(g status --short --ignore-submodules=all | wc -l)" = 0 ] || { echo "worktree not clean"; exit 9; }
echo "--- 1: cherry-pick -x fcaf141b 082d1612"
g cherry-pick -x fcaf141b 082d1612
echo "--- 2: cherry-pick -n ff953d4f, drop docs/track-s/s14j"
g cherry-pick -n ff953d4f
g rm -r -q --cached docs/track-s/s14j
rm -rf $WT/docs/track-s/s14j
echo "staged:"; g diff --cached --name-only
[ "$(g diff --cached --name-only)" = "tests/shaderCfgTests.cpp" ] || { echo "index is not only tests/shaderCfgTests.cpp"; exit 9; }
g commit -q -m "tests part of ff953d4f (S14j) for a clean pick of f98e842c, ROADMAP p.523(b)" -m "(partial cherry picked from commit $(g rev-parse ff953d4f); docs/track-s/s14j dropped)"
echo "--- 3: cherry-pick -x f98e842c e46f55d4"
g cherry-pick -x f98e842c e46f55d4
echo "--- log"; g log -6 --format='%H %s' | cut -c1-130
echo "--- status lines (0 = clean)"; g status --short --ignore-submodules=all | wc -l
echo "--- tree"; g rev-parse HEAD^{tree}
echo CP523 OK
