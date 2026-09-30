"""Session 140 step 0: every file:line anchor of opmap140.tsv / design140.md checked against the tree at HEAD (token on that line).
Usage: python mapcheck140.py  -> prints one line per anchor and 'ALL OK' or 'FAIL n'."""
import subprocess, sys

ROOT = 'C:/kyty/KytyPS5/'
G = 'src/graphics/guest_gpu/'
H = G + 'command_processor/pm4Handlers.cpp'
D = G + 'command_processor/pm4Dispatch.cpp'
R = G + 'graphicsRun.cpp'
P = G + 'pm4.h'
A = [
    (R, 2784, 'Pm4OpName'), (R, 2905, 'g_cp_op_func[opcode]'), (R, 2924, 'KYTY_PM4_TRACE'), (R, 2925, 'NowNs'),
    (R, 2927, 'handler('), (R, 2929, 'AddSite'), (R, 2829, 'ProcessCommands'), (R, 2853, '0x80000000u'),
    (R, 2867, 'ShouldSkipPredicatedPackets'), (R, 2919, 'EXIT("unknown op'), (R, 2767, 'ProcessIndirectBuffer'),
    (R, 948, 'PathProcNs'), (R, 1033, '"gc"'), (R, 1041, '"prefetch"'), (R, 1029, 'PathGcNs'), (R, 1047, 'BufferFlush'),
    (R, 1082, 'BufferFlush'), (R, 1124, 'PrefetchComputePipelines'), (R, 2689, 'PathPrefNs'), (R, 162, 'PathCmdNs'),
    (R, 417, 'PathSubNs'), (R, 433, 'PathSubNs'), (R, 3670, 'PathBarNs'), (R, 3725, 'PathEopNs'), (R, 3691, 'GetMutex'),
    (R, 935, 'GetMutex'), (R, 368, 'CommandProcessor::Reset'), (R, 383, 'ApplyContextStateOperation'),
    (R, 464, 'WaitCe'), (R, 470, 'WaitDeDiff'), (R, 477, 'WaitForRewind'), (R, 483, 'IncrementDe'), (R, 487, 'IncrementCe'),
    (R, 491, 'WriteConstRam'), (R, 500, 'DumpConstRam'), (R, 533, 'TestWaitRegMemValue'), (R, 555, 'SuspendPm4'),
    (R, 564, 'WriteData'), (R, 592, 'WriteReferenceClock'), (R, 601, 'LOGF'), (R, 3686, 'emit_eop_barriers'), (R, 3688, 'return'), (R, 605, 'DmaData'), (R, 2946, 'SetIndexType'),
    (R, 2950, 'SetIndexBaseAddress'), (R, 2954, 'SetIndexBufferSize'), (R, 2958, 'SetDrawIndirectArgsBaseAddress'),
    (R, 2962, 'SetDispatchIndirectArgsBaseAddress'), (R, 2967, 'SetNumInstances'), (R, 2979, 'BufferFlushAndWait'),
    (R, 3011, 'CommandProcessor::DrawIndex'), (R, 3025, 'GetRenderExecutor().DrawIndex'), (R, 3028, 'DrawIndexOffset'),
    (R, 3040, 'DrawIndex('), (R, 3043, 'CommandProcessor::DrawIndirect'), (R, 3086, 'memcpy'), (R, 3109, 'memcpy'),
    (R, 3153, 'DrawIndirectMulti'), (R, 3163, 'count_addr'), (R, 3195, 'DrawIndexAuto'), (R, 3242, 'DrawIndex('),
    (R, 3251, 'CommandProcessor::DispatchDirect'), (R, 3302, 'GetRenderExecutor().DispatchDirect'),
    (R, 3338, 'DispatchIndirect'), (R, 3359, 'DispatchDirect'), (R, 3362, 'DrawIndexAuto'), (R, 3371, 'DrawAuto'),
    (R, 3374, 'WaitFlipDone'), (R, 3376, 'BufferFlush'), (R, 3383, 'WriteAtEndOfPipe'), (R, 3645, 'WriteAtEndOfPipe32'),
    (R, 3656, 'WriteAtEndOfPipe64'), (R, 3667, 'EmitGlobalBarrier'), (R, 3722, 'TriggerEopEventAtEndOfPipe'),
    (R, 3731, 'TriggerEvent'), (R, 3746, 'EmitGlobalBarrier'), (R, 3754, 'EmitGlobalBarrier'), (R, 3764, 'EmitGlobalBarrier'),
    (R, 4048, 'CommandProcessor::Flip()'), (R, 4060, 'PrepareVideoOutFlip'), (R, 4067, 'Flush'), (R, 4070, 'Flip(void'),
    (R, 4098, 'FlipWithInterrupt'),
    (P, 22, 'IT_NOP'), (P, 46, 'IT_INDIRECT_BUFFER'), (P, 75, 'IT_SET_CONTEXT_REG_INDIRECT'), (P, 79, 'R_ZERO'),
    (P, 81, 'R_WAIT_FLIP_DONE'), (P, 87, 'R_FLIP'), (P, 88, 'R_RELEASE_MEM'), (P, 90, 'R_CONTEXT_STATE'),
    (D, 176, 'CpOpNop'), (D, 198, 'CpOpIndirectBuffer'), (D, 220, 'CpOpWaitRegMem64'), (D, 228, 'CpOpDispatchReset'),
    (D, 233, 'CpOpFlip'), (D, 234, 'CpOpReleaseMem'), (D, 235, 'CpOpContextState'),
    (H, 1318, 'CpOpAcquireMem'), (H, 1326, 'CpOpDispatchDirect'), (H, 1342, 'CpOpDispatchIndirect'), (H, 1363, 'DispatchInitiatorUseThreadDimensions'),
    (H, 1366, 'DispatchDirect'), (H, 1380, 'CpOpGetLodStats'), (H, 1447, 'CpOpDispatchReset'), (H, 1458, 'CpOpPfpSyncMe'),
    (H, 1467, 'CpOpRewind'), (H, 1479, 'CpOpSetPredication'), (H, 1512, 'CpOpCondExec'), (H, 1532, 'addr'),
    (H, 1539, 'CpOpBranch'), (H, 1574, 'ProcessIndirectBuffer'), (H, 1577, 'ProcessIndirectBuffer'), (H, 1613, 'CpOpCopyData'),
    (H, 1654, 'CpOpDmaData'), (H, 1687, 'CpOpDrawIndex'), (H, 1728, 'CpOpDrawIndirect'), (H, 1742, 'CpOpDrawIndirectMulti'),
    (H, 1766, 'CpOpDrawIndexOffset'), (H, 1784, 'CpOpDrawIndexAuto'), (H, 1799, 'CpOpClearState'), (H, 1810, 'CpOpContextState'),
    (H, 1823, 'CpOpDumpConstRam'), (H, 1842, 'CpOpEventWrite'), (H, 1863, 'CpOpEventWriteEop'), (H, 1886, 'CpOpEventWriteEos'),
    (H, 1910, 'CpOpFlip'), (H, 1927, 'CpOpIncrementCeCounter'), (H, 1939, 'CpOpIncrementDeCounter'), (H, 1951, 'CpOpIndexType'),
    (H, 1961, 'CpOpIndexBufferSize'), (H, 1971, 'CpOpIndexBase'), (H, 1983, 'CpOpSetBase'), (H, 2006, 'CpOpIndirectBuffer'),
    (H, 2046, 'ProcessIndirectBuffer'), (H, 2051, 'CpOpIndirectCxRegs'), (H, 2113, 'CpOpIndirectShRegs'), (H, 2176, 'CpOpIndirectUcRegs'),
    (H, 2230, 'CpOpMarker'), (H, 2268, 'CpOpNop'), (H, 2277, 'return'), (H, 2286, 'unknown custom code'), (H, 2291, 'CpOpNumInstances'),
    (H, 2301, 'CpOpPopMarker'), (H, 2314, 'CpOpPushMarker'), (H, 2329, 'CpOpReleaseMem'), (H, 2366, 'TriggerEopEventAtEndOfPipe'),
    (H, 2373, 'BufferFlushLazy'), (H, 2379, 'EmitGlobalBarrier'), (H, 2389, 'EmitGlobalBarrier'), (H, 2398, 'EmitGlobalBarrier'),
    (H, 2414, 'BufferFlushLazy'), (H, 2434, 'BufferFlushLazy'), (H, 2462, 'CpOpSetContextReg'), (H, 2508, 'CpOpSetShaderReg'),
    (H, 2545, 'CpOpSetUconfigReg'), (H, 2603, 'CpOpWaitFlipDone'), (H, 2668, 'CpOpWaitRegMem32'), (H, 2674, 'CpOpWaitRegMem64'),
    (H, 2680, 'CpOpWaitOnCeCounter'), (H, 2692, 'CpOpWaitOnDeCounterDiff'), (H, 2703, 'CpOpWriteConstRam'), (H, 2718, 'CpOpWriteData'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 4938, 'RenderExecutor::DrawIndex'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 4975, 'GetMutex'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 4976, 'MutexMark'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 5170, 'RenderExecutor::DrawAuto'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 5204, 'GetMutex'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 5205, 'MutexMark'),
    ('src/graphics/host_gpu/renderer/renderCompute.cpp', 383, 'RenderExecutor::DispatchDirect'),
    ('src/graphics/host_gpu/renderer/renderCompute.cpp', 416, 'GetMutex'),
    ('src/graphics/host_gpu/renderer/renderCompute.cpp', 417, 'MutexMark'),
    ('src/graphics/host_gpu/renderer/sync.cpp', 228, 'PrepareVideoOutFlip'),
    ('src/graphics/host_gpu/renderer/sync.cpp', 244, 'WaitForSubmitSlot'),
    ('src/graphics/presentation/videoOut.cpp', 964, 'FlipQueue::Prepare'),
    ('src/graphics/presentation/videoOut.cpp', 1039, 'PrepareBlankFrame'),
    ('src/graphics/presentation/videoOut.cpp', 1042, 'PrepareFrame'),
    ('src/graphics/presentation/videoOut.cpp', 3840, 'SubmitFlipFromGpu'),
    ('src/graphics/presentation/videoOut.cpp', 3849, 'Prepare(request_id'),
    ('src/graphics/presentation/videoOut.cpp', 3878, 'WaitFlipDone'),
    ('src/graphics/presentation/videoOut.cpp', 3492, 'dn / 1000u'),
    ('src/graphics/presentation/videoOut.cpp', 3490, 'dc = rows[i].count'),
    ('src/graphics/presentation/videoOut.cpp', 3478, 'FrameTrace-pm4:'),
    ('src/graphics/presentation/videoOut.cpp', 1955, 'a_hold_us'),
    ('src/graphics/presentation/window/swapchain.cpp', 748, 'PrepareFrame'),
    ('src/graphics/presentation/window/swapchain.cpp', 759, 'GetMutex'),
    ('src/graphics/presentation/window/swapchain.cpp', 769, 'HoldPresentNs'),
    ('src/graphics/presentation/window/swapchain.cpp', 794, 'PrepareBlankFrame'),
    ('src/graphics/presentation/window/swapchain.cpp', 806, 'GetMutex'),
    ('src/graphics/presentation/window/swapchain.cpp', 896, 'GetMutex'),
    ('src/graphics/host_gpu/renderer/cache/bufferCache.cpp', 3052, 'stream-prefetch'),
    ('src/common/frameStats.cpp', 91, 'MaxSites = 160'), ('src/common/frameStats.cpp', 103, 'SiteIndex'),
    ('src/common/frameStats.cpp', 117, 'MaxSites'), ('src/common/frameStats.cpp', 118, 'MaxSites - 1'),
    ('src/common/frameStats.cpp', 200, 'NowNs'), ('src/common/frameStats.cpp', 206, '__rdtsc'),
    ('src/common/frameStats.cpp', 255, 'AddSite'), ('src/common/frameStats.cpp', 258, 'fetch_add'),
    ('src/common/frameStats.h', 2965, 'class MutexMark'), ('src/common/frameStats.h', 3780, 'Reset(Cause'),
    ('src/common/frameStats.h', 3145, 'PathSpan(bool on'), ('src/common/frameStats.h', 1579, 'PathCmdNs'),
    ('src/common/envFlag.h', 35, 'EnvFlagOn'),
    (H, 2242, '0x777'), (H, 2259, 'FlipWithInterrupt'), (H, 2029, 'indirect_log_count'), (H, 1569, 'branch: take'),
    ('src/graphics/host_gpu/renderer/renderDraw.cpp', 4971, 'lock_t0'), ('src/graphics/host_gpu/renderer/renderDraw.cpp', 4941, 'RenderDocNoteGpuWork'),
    ('src/graphics/host_gpu/renderer/renderCompute.cpp', 420, 'hold_lap'), (R, 159, 'ProcessCommands'), (R, 946, 'PathSpan pl_proc'),
    ('src/common/frameStats.h', 1545, 'THE FACTOR 1000'), ('src/graphics/presentation/videoOut.cpp', 3473, '160'),
    ('src/graphics/presentation/window/swapchain.cpp', 752, 'present thread is the only other taker'), (R, 3176, 'draw_count'), (R, 2834, 'deferred_advance_dw'),
    ('src/common/frameStats.h', 2981, 'operator='),
]


def main():
    head = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    print('HEAD', head)
    cache, bad = {}, 0
    for f, ln, tok in A:
        if f not in cache:
            cache[f] = open(ROOT + f, encoding='utf-8', errors='replace').read().split('\n')
        s = cache[f][ln - 1] if ln - 1 < len(cache[f]) else ''
        ok = tok in s
        bad += not ok
        print('%s %s:%d %r' % ('ok  ' if ok else 'FAIL', f, ln, tok) + ('' if ok else '  | line: ' + s.strip()[:100]))
    print('ALL OK' if bad == 0 else 'FAIL %d' % bad)
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
