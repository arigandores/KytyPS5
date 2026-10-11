#!/bin/bash
# F42a2 (HPP-805): copy of the F42a base_build.sh, executable lines f42a -> f42a2 (paths, names). Was:
# F42a (HPP-779): base build of the worktree (FS12a 730ed40a, no F42a commit yet) - configure, kyty_emulator,
# shader_cfg_tests, shader_recompiler_compute_tests; ninja is incremental for the F42a build after the cherry-picks.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42a2
bash chain.sh cfg configure || exit $?
bash chain.sh emu || exit $?
bash chain.sh cfgt tests || exit $?
bash chain.sh rct target shader_recompiler_compute_tests || exit $?
echo BASE BUILD DONE $(date -u +%FT%TZ)
