# F20k (HPP-630, Red Team): the references of docs/track-f/f20k-review.md - <commit>:<path>:<line>, anchor = a substring
# of that line, +1 = a substring of the next line (general rule 24(1)). Usage: python refs_f20k.py check (from any dir).
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
W = '0df13a66'
REFS = [
    (W, 'src/common/diagB32.cpp', 1110, 'const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;', 'bool           kq       = false;'),
    (W, 'src/common/diagB32.cpp', 1112, 'if (m_kq_ok && m_win_start != 0 && t0 >= m_win_start + kKernelAfterNs) {', 'KernelQuery();'),
    (W, 'src/common/diagB32.cpp', 1149, 'm_cost[pos] = FrameStats::NowNs() - t0;', 'm_hpos++;'),
    (W, 'src/common/diagB32.cpp', 1472, 'Sample(FrameStats::NowNs());', 'SetWaitableTimerEx(timer, &due, 0, nullptr, nullptr, nullptr, 0);'),
    (W, 'src/common/diagB32.cpp', 1064, 'LONG  status = m_ntq(5 /* SystemProcessInformation */', 'if (status == static_cast<LONG>(0xC0000004L)'),
    (W, 'src/common/diagB32.cpp', 1376, 'm_c.torn      = g_reg->torn.load(std::memory_order_relaxed) + m_ring_torn;', 'm_c.print_us  = g_print_us.load(std::memory_order_relaxed);'),
    (W, 'src/common/diagB32.cpp', 492, 'counters->sgap_bad++;', '}'),
    (W, 'src/common/diagB32.cpp', 1277, 'm_c.ring_drop++; // the history ring no longer holds the start of this window', '}'),
    (W, 'src/common/diagB32.cpp', 507, 'counters->lines_cut += must.size() - kMustCap;', 'must.resize(kMustCap);'),
    (W, 'src/common/diagB32.cpp', 300, 'for (; rpos < w; rpos++) {', 'auto& x  = e[rpos % kWaitRing];'),
    (W, 'src/common/diagB32.cpp', 333, '(*torn)++;', '}'),
    (W, 'src/common/diagB32.cpp', 279, 'const auto i = wpos.fetch_add(1, std::memory_order_acq_rel);', 'auto&      x = e[i % kWaitRing];'),
    (W, 'src/common/diagB32.cpp', 882, 'if (r.id.load(std::memory_order_acquire) == request_id) {', 'slot1 = r.slot1.load(std::memory_order_relaxed);'),
    (W, 'src/common/diagB32.cpp', 867, 'if (e.seq.load(std::memory_order_acquire) == seq) {', 'slot1 = e.slot1.load(std::memory_order_relaxed);'),
    (W, 'src/common/diagB32.cpp', 1401, 'M5Refresh(t0);', '}'),
    (W, 'src/graphics/presentation/videoOut.cpp', 1174, 'r.cfg->mutex.Lock();', '// Session 114 (ROADMAP item 4): the hold of VideoOutConfig::mutex by phase'),
    (W, 'src/graphics/presentation/videoOut.cpp', 1242, 'm_mutex.Lock();', 'if (m_requests.empty() || m_requests.front().id != r.id ||'),
    (W, 'src/graphics/presentation/videoOut.cpp', 1251, '// reports the sampler has closed are printed here, outside m_mutex.', 'if (Common::DiagB32::g_on) [[unlikely]] {'),
    (W, 'src/graphics/presentation/videoOut.cpp', 3550, 'm_mutex.Unlock();', ''),
    (W, 'src/graphics/presentation/videoOut.cpp', 3567, 'r.cfg->mutex.Unlock();', ''),
    (W, 'src/graphics/presentation/videoOut.cpp', 530, 'if (!video_out->mutex.TryLock()) {', 'const auto wait_t0 = Common::FrameStats::NowNs();'),
    (W, 'src/graphics/presentation/window/swapchain.cpp', 798, 'Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);', 'result = m_window.graphic_ctx.queue.presentKHR(&present);'),
    (W, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 141, 'Common::LockGuard lock(graphics.queue_mutex);', 'locked_ns    = Common::FrameStats::NowNs();'),
    (W, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 163, 'result = graphics.queue.submit(1, &submit_info, nullptr);', 'RecordGpuSubmission(record.scheduler, record.master, record.tick, submit, true, result);'),
    (W, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 857, 'Common::Gates::Enabled(Common::Gates::Gate::AsyncSubmit);', ''),
    (W, 'src/common/gates.cpp', 34, '{"KYTY_ASYNC_SUBMIT", "asyncsubmit", true},', ''),
    (W, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 948, 'Common::LockGuard lock(graphics.queue_mutex);', 'b32_q.End(0, false);'),
    (W, 'src/graphics/presentation/systemOverlay.cpp', 1074, 'Common::LockGuard queue_lock(graphics.queue_mutex);', ''),
    (W, 'src/kernel/pthread.cpp', 488, 'std::atomic<int32_t>  b32_slot1 {0};', 'std::atomic<uint64_t> b32_waker {0};'),
    (W, 'src/kernel/pthread.cpp', 491, 'uintptr_t guest_host_gs8;', 'uintptr_t guest_host_gs10;'),
    (W, 'src/common/hostException.cpp', 176, 'b32.BeginH(Common::DiagB32::Call::Fault);', '}'),
    (W, 'src/common/hostException.cpp', 149, 'return EXCEPTION_CONTINUE_SEARCH;', '}'),
    (W, 'src/common/diagB32.cpp', 694, 'HANDLE     handle = OpenThread(THREAD_QUERY_LIMITED_INFORMATION, FALSE, tid);', 'const auto idx    = g_reg->Allocate(tid, handle, role, name, gid);'),
    (W, 'src/kernel/semaphore.cpp', 409, 'static_assert(sizeof(PosixSemGuest) == 16);', ''),
    (W, 'src/kernel/eventQueue.cpp', 46, 'KYTY_CLASS_NO_COPY(KernelEqueuePrivate);', ''),
    ('065a81bf', 'docs/ROADMAP.md', 23229, '551. **Звено F20j трека F (`HPP-629`, Emu Engineer;', '(а) **Приёмка строкой. F20j ✓**'),
    ('fe0bf0a0', 'docs/ROADMAP.md', 23217, '550. **Звено F20i трека F (`HPP-628`, лид; приёмка F20g', '(а) **Приёмка строкой. F20g ✓**'),
]

def show(c, p):
    out = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout
    return out.decode('utf-8', 'replace').replace('\r', '').split('\n')

def main():
    cache = {}
    bad = 0
    for c, p, n, a, b in REFS:
        L = cache.setdefault((c, p), show(c, p))
        ok = a in L[n - 1] and (b == '' or b in L[n])
        if not ok:
            bad += 1
            print('FAIL %s:%s:%d\n  line: %s\n  +1:   %s' % (c, p, n, L[n - 1].strip()[:140], L[n].strip()[:140]))
        else:
            print('ok   %s:%s:%d' % (c, p, n))
    print('refs %d, failures %d' % (len(REFS), bad))
    print('ALL OK' if bad == 0 else 'FAILED')
    return 0 if bad == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
