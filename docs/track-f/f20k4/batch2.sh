[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo STOP; exit 4; }
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
S="$PAPERCLIP_RUN_SCRATCH_DIR"
cd C:/kyty/KytyPS5 || exit 5
O="$S/batch2.out"
: > "$O"
echo "start $(date -u +%FT%TZ)" >> "$O"
echo "== present-path callers" >> "$O"
git grep -nE "UpdateTitle\(|DeferOperation\(|DeferPriorityOperation\(|WaitPriorityOperations\(|DrainPriorityOperations\(|GetGraphicsPipeline\(|GetComputePipeline\(|WaitForPendingPipelines\(|RecreateSurface\(|ParallelCopy|FlushVideoSlot\(|DrainAsyncSubmits\(|\.Reserve\(|->Reserve\(" f2307b02 -- src/graphics/presentation >> "$O"
echo "== RecreateSurface def" >> "$O"
git grep -nE "void .*RecreateSurface\(" f2307b02 -- src >> "$O"
echo "== UpdateTitle callers all" >> "$O"
git grep -nE "UpdateTitle\(" f2307b02 -- src >> "$O"
echo "== Presenter::Present def" >> "$O"
git grep -nE "Presenter::Present\(|void Presenter::Present" f2307b02 -- src >> "$O"
echo "== hostException H:fault body" >> "$O"
git show f2307b02:src/common/hostException.cpp | sed -n 165,200p >> "$O"
echo "== diag Init g_on" >> "$O"
git show f2307b02:src/common/diagB32.cpp | sed -n 1990,2010p >> "$O"
echo "== Mark ctor/dtor at Reserve; WaitName order check" >> "$O"
git show 9db7938b:src/common/diagB32.h | grep -n "Vblank, Once" >> "$O"
echo "end $(date -u +%FT%TZ)" >> "$O"
echo done
