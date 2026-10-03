#!/bin/bash
# FS4b (HPP-471, Red Team): lineage and diff checks of the FS4 worktree commit 3d0e46da (ROADMAP s122 items 378(g)(1), (5), 380(b)).
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
export PATH=/usr/bin:/mingw64/bin:$PATH
G="/c/Program Files/Git/cmd/git.exe"
cd C:/kyty/KytyPS5
T=3d0e46da
F3="src/graphics/host_gpu/graphicContext.h src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp src/graphics/presentation/window/vulkanWindow.cpp"
echo "--- parents"
"$G" log -4 --format='%H %P' $T
echo "--- diff --stat d515b901 $T (whole tree, not only src/)"
"$G" diff --stat d515b901 $T
echo "--- diff --name-only d515b901 $T"
"$G" diff --name-only d515b901 $T
echo "--- base of F10c equal to FS3 on the three files: git diff --quiet 68602c4f^ d515b901 -- <3 files>"
"$G" diff --quiet 68602c4f^ d515b901 -- $F3 && echo EQUAL || echo DIFFERENT
echo "--- three files of $T == main 17adaf80: git diff --quiet 17adaf80 $T -- <3 files>"
"$G" diff --quiet 17adaf80 $T -- $F3 && echo EQUAL || echo DIFFERENT
echo "--- three files of 92d11340 == 68602c4f: git diff --quiet 68602c4f 92d11340 -- <3 files>"
"$G" diff --quiet 68602c4f 92d11340 -- $F3 && echo EQUAL || echo DIFFERENT
echo "--- 17adaf80 touches"
"$G" show --stat --format='%H %P' 17adaf80 | cat
echo "--- 68602c4f touches"
"$G" show --stat --format='%H %P' 68602c4f | cat
echo "--- patch-id"
for c in 68602c4f 92d11340 17adaf80 $T 4e72289e d515b901; do printf '%s ' $c; "$G" show $c | "$G" patch-id --stable | cut -c1-16; done
echo "--- is-ancestor of $T"
for c in d515b901 722c5e7f 4414e235 92d11340 4e72289e 68602c4f 17adaf80 741e3312 c9b4268e; do
	if "$G" merge-base --is-ancestor $c $T; then echo "$c ancestor yes"; else echo "$c ancestor no"; fi
done
echo "--- git cherry -v $T X X^ (- = equal change in history, + = absent)"
for c in 4e72289e 68602c4f 17adaf80 741e3312 c9b4268e; do printf '%s: ' $c; "$G" cherry -v $T $c $c^ | cut -c1-60; done
echo "--- P-var / loader / B42 files untouched d515b901..$T"
for f in src/emulator/pvar.cpp src/loader/gamePatchFile.cpp src/graphics/host_gpu/renderer/descriptors.cpp src/graphics/host_gpu/renderer/textureCache.cpp src/graphics/host_gpu/renderer/textureCache.h; do
	n=$("$G" ls-tree -r --name-only $T | grep -c "$(basename $f)")
	"$G" diff --quiet d515b901 $T -- "*$(basename $f)" && echo "$(basename $f) (tree matches $n) unchanged" || echo "$(basename $f) CHANGED"
done
echo "--- src/graphics/shader touched d515b901..$T (signature)"
"$G" diff --name-only d515b901 $T -- src/graphics/shader | wc -l
echo "--- worktree fs4b status"
"$G" -C C:/kyty/f287/fs4/fs4b/wt status --short --ignore-submodules=all | wc -l
"$G" -C C:/kyty/f287/fs4/fs4b/wt rev-parse HEAD
echo LINEAGE DONE
