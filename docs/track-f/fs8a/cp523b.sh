#!/bin/bash
# FS8a (HPP-571, ROADMAP s122 item 523(v)): continuation of cp523.sh after its stop at step 2 - ff953d4f carries 12 docs
# files: 11 under docs/track-s/s14j/ and docs/track-s/s14j.md (git show --stat); item 523(b)(2) and (g)(e')(1) drop all
# docs of ff953d4f ("12 files docs/track-s/s14j/*" in the lead's comment = this count), so s14j.md is dropped as well.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
set -e
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
WT=C:/kyty/f287/fs8a/wt
export GIT_AUTHOR_NAME="Emu Engineer" GIT_AUTHOR_EMAIL=<agent-email>
export GIT_COMMITTER_NAME="Emu Engineer" GIT_COMMITTER_EMAIL=<agent-email>
g() { "$G" -C $WT -c core.autocrlf=false "$@"; }
echo "--- HEAD"; g log -1 --format='%H %s' | cut -c1-100
g rm -q --cached docs/track-s/s14j.md
rm -f $WT/docs/track-s/s14j.md
echo "staged:"; g diff --cached --name-only
[ "$(g diff --cached --name-only)" = "tests/shaderCfgTests.cpp" ] || { echo "index is not only tests/shaderCfgTests.cpp"; exit 9; }
echo "untracked/unstaged (0 expected):"; g status --short --ignore-submodules=all | grep -v '^M  tests/shaderCfgTests.cpp$' | wc -l
g commit -q -m "tests part of ff953d4f (S14j) for a clean pick of f98e842c, ROADMAP p.523(b)" -m "(partial cherry picked from commit $(g rev-parse ff953d4f); docs/track-s/s14j/ and docs/track-s/s14j.md dropped)"
echo "--- 3: cherry-pick -x f98e842c e46f55d4"
g cherry-pick -x f98e842c e46f55d4
echo "--- log"; g log -6 --format='%H %s' | cut -c1-130
echo "--- status lines (0 = clean)"; g status --short --ignore-submodules=all | wc -l
echo "--- tree"; g rev-parse HEAD^{tree}
echo CP523 OK
