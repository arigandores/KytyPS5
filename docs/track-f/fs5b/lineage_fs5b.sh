#!/bin/bash
# FS5b (HPP-510, Red Team, ROADMAP s122 item 410(g)(2)): lineage of the FS5 worktree commit 0e72bc19, own recount (not FS5a code).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
cd C:/kyty/KytyPS5
X=0e72bc19
F6="src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h src/graphics/shader/recompiler/frontend/translate/Memory.cpp tests/ShaderRecompilerComputeTests.cpp"
echo "== parents"
"$G" log -4 --format='%h %p %s' $X | cut -c1-140
echo "== git diff --stat 3d0e46da $X (whole tree)"
"$G" diff --stat 3d0e46da $X
echo "== files of 1833ee28 / c3eb8fe8 / 8a56dc2a / $X"
for c in 1833ee28 c3eb8fe8 8a56dc2a $X; do echo "-- $c"; "$G" diff-tree --no-commit-id --name-only -r $c; done
echo "== 6 files of 1833ee28 on 1833ee28^ vs 3d0e46da (EQUAL = cherry-pick on the same text)"
"$G" diff --quiet 1833ee28^ 3d0e46da -- $F6 && echo EQUAL || echo DIFFER
echo "== 6 files: 8a56dc2a vs 1833ee28 (EQUAL = F12d copied verbatim)"
"$G" diff --quiet 8a56dc2a 1833ee28 -- $F6 && echo EQUAL || echo DIFFER
echo "== 6 files: $X vs main c3eb8fe8 (EQUAL = FS5a copied verbatim)"
"$G" diff --quiet $X c3eb8fe8 -- $F6 && echo EQUAL || echo DIFFER
echo "== diff 1833ee28 c3eb8fe8 -- 6 files (= FS5a change only)"
"$G" diff --stat 1833ee28 c3eb8fe8 -- $F6
echo "== patch-id"
for c in 1833ee28 8a56dc2a c3eb8fe8 $X; do "$G" show $c | "$G" patch-id --stable; done
echo "== track F16 / B42 / P-var files: 3d0e46da vs $X (EQUAL = untouched)"
for p in src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp src/graphics/host_gpu/renderer/graphicContext.h src/graphics/host_gpu/vulkanWindow.cpp src/graphics/host_gpu/renderer/descriptors.cpp src/graphics/host_gpu/renderer/textureCache.cpp src/graphics/host_gpu/renderer/textureCache.h; do
	if "$G" cat-file -e $X:$p 2>/dev/null; then "$G" diff --quiet 3d0e46da $X -- $p && echo "EQUAL $p" || echo "DIFFER $p"; else echo "ABSENT $p"; fi
done
for p in $("$G" ls-tree -r --name-only $X -- src | grep -i -E "pvar|gamePatch"); do "$G" diff --quiet 3d0e46da $X -- $p && echo "EQUAL $p" || echo "DIFFER $p"; done
echo "== git cherry -v $X <c> <c>^ ('-' = equal change in history)"
for c in 4e72289e 68602c4f 17adaf80 1833ee28 c3eb8fe8 741e3312 c9b4268e fcaf141b; do echo -n "$c: "; "$G" cherry -v $X $c $c^ | cut -c1-100; done
echo "== merge-base --is-ancestor <c> $X"
for c in 4414e235 722c5e7f d515b901 92d11340 3d0e46da 8a56dc2a; do "$G" merge-base --is-ancestor $c $X && echo "$c yes" || echo "$c no"; done
echo "== uses of FixF10Enabled / KYTY_FIX_F10 in $X src"
"$G" grep -n -E "FixF10Enabled|KYTY_FIX_F10" $X -- src | cut -c1-200
echo "== KYTY_GIT_REVISION and signature of the two build trees"
grep -h -E "KYTY_GIT_REVISION|KYTY_SHADER_SOURCE_HASH" C:/kyty/f287/fs5/fs5b/build/kytyGitVersion.h C:/kyty/f287/fs5/fs5a/build/kytyGitVersion.h
echo LINEAGE DONE
