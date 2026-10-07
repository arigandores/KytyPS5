#!/bin/sh
# F25c (HPP-666, Red Team): offline check of the transfer of the 5 KYTY_DIAG_B32 commits onto the S18 source 0005e11f
# (ROADMAP p.596(v)). No working tree is touched: git merge-tree --write-tree per commit (the cherry-pick model:
# merge base = the commit's parent), git commit-tree into dangling commits only.
R=C:/kyty/KytyPS5
cd "$R" || exit 1
echo "base 302347b4 = merge-base(0005e11f, f2307b02): $(git merge-base 0005e11f f2307b02 | cut -c1-8)"
echo "-- files changed by both sides since 302347b4:"
git diff --name-only 302347b4 0005e11f | sort > /tmp/f25c_s18.txt
git diff --name-only 302347b4 f2307b02 | sort > /tmp/f25c_diag.txt
comm -12 /tmp/f25c_s18.txt /tmp/f25c_diag.txt
echo "-- sequential cherry-pick model:"
base=0005e11f
for c in 875720c5 0df13a66 61b410bf 9db7938b f2307b02; do
  out=$(git merge-tree --write-tree --merge-base "$c^" "$base" "$c"); rc=$?
  tree=$(echo "$out" | head -1)
  echo "$c rc=$rc conflicts=$(echo "$out" | tail -n +2 | grep -c .) tree=$tree"
  base=$(git commit-tree "$tree" -p "$base" -m "f25c sim $c")
done
echo "sim head tree $(git rev-parse "$base^{tree}")"
echo "one-shot merge tree $(git merge-tree --write-tree 0005e11f f2307b02 | head -1)"
echo "-- git cherry (sim head vs the 5 commits; '-' = equivalent patch present):"
git cherry "$base" f2307b02 302347b4
echo "-- signature set diff 0005e11f..sim (src/graphics/shader + SHADER_CACHE_EXTRA_FILES of CMakeLists.txt:156):"
git diff --stat 0005e11f "$base" -- src/graphics/shader src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp \
  src/graphics/guest_gpu/gpu_format.h src/graphics/guest_gpu/gpu_defs.h src/graphics/host_gpu/renderer/image/imageInfo.h
echo "(empty = same signature set)"
echo "-- diffstat 0005e11f..sim vs 302347b4..f2307b02:"
git diff --shortstat 0005e11f "$base"
git diff --shortstat 302347b4 f2307b02
echo "-- S18 hunks in the two shared files:"
git diff -U0 302347b4 0005e11f -- src/graphics/presentation/window/window.cpp src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp | grep -E '^(\+\+\+|@@)'
echo "TRANSFER CHECK DONE"
