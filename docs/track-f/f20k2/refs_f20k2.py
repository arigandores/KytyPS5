# F20k2 (HPP-634): check of every <commit>:<path>:<line> reference of docs/track-f/f20k2-review.md - the line starts with
# the anchor and the next line starts with the +1 control (general rule 24(1)). Prints one line per reference and ALL OK.
import subprocess, sys

R = [
    ('8f3ee6ad', 'docs/ROADMAP.md', 23237, '552. **Звено F20k трека F (`HPP-630`, Red Team; приёмка лида', '(а) **Приёмка строкой. F20k ✓**'),
    ('8f3ee6ad', 'docs/ROADMAP.md', 23246, '553. **Звено F20j2 трека F (`HPP-633`, Emu Engineer;', '(а) **Приёмка строкой. F20j2 ✓**'),
    ('d63d7feb', 'docs/track-f/f20k-review.md', 63, '## 2. Требуемые изменения', ''),
    ('61b410bf', 'src/common/diagB32.cpp', 180, 'bool KqSchedule::Due(uint64_t now_ns) const {', 'if (win_start == 0 || now_ns < win_start + kKernelAfterNs) {'),
    ('61b410bf', 'src/common/diagB32.cpp', 192, 'void KqSchedule::NewWindow(uint64_t flip_ns, uint64_t carried_kq_ns) {', 'win_start = flip_ns;'),
    ('61b410bf', 'src/common/diagB32.cpp', 197, 'uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns) {', 'return std::max(begin_ns + kPeriodNs, now_ns);'),
    ('61b410bf', 'src/common/diagB32.cpp', 201, 'void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,', 'int32_t* out) {'),
    ('61b410bf', 'src/common/diagB32.cpp', 355, 'if (s1 < want) {', '// F20j2 (RC4): the write of this position has not finished'),
    ('61b410bf', 'src/common/diagB32.cpp', 379, '// Overwritten by a later lap before or while it was read', '(*torn)++;'),
    ('61b410bf', 'src/common/diagB32.cpp', 461, 'const bool asub = t.role == "ASubmit" &&', 't.agg.h[static_cast<size_t>(Call::QLock)] + t.agg.h[static_cast<size_t>(Call::QSubmit)] > 0;'),
    ('61b410bf', 'src/common/diagB32.cpp', 651, 'const auto  dw = [](uint64_t v, uint64_t base)', 'Append(&out,'),
    ('61b410bf', 'src/common/diagB32.cpp', 670, 'void Counters::Rebase() {', 'base.slot_full = slot_full;'),
    ('61b410bf', 'src/common/diagB32.cpp', 973, 'e.print_ns.store(g_print_prev_ns, std::memory_order_relaxed);', 'g_flip_pub.store(k + 1, std::memory_order_release);'),
    ('61b410bf', 'src/common/diagB32.cpp', 1001, 'g_print_prev_ns = print_ns;', '}'),
    ('61b410bf', 'src/common/diagB32.cpp', 1207, 'if (m_kq_ok && m_sched.Due(begin)) {', 'KernelQuery();'),
    ('61b410bf', 'src/common/diagB32.cpp', 1217, 'const uint64_t t0       = FrameStats::NowNs();', 'const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;'),
    ('61b410bf', 'src/common/diagB32.cpp', 1261, 'm_cost[pos] = FrameStats::NowNs() - begin;', 'm_hpos++;'),
    ('61b410bf', 'src/common/diagB32.cpp', 1376, 'const uint64_t extra = m_win_extra_ns + print_ns;', 'const uint64_t m5r   = m_win_m5r_ns;'),
    ('61b410bf', 'src/common/diagB32.cpp', 1386, 'if (m_t[h % kHist] <= flip_ns) {', 'break;'),
    ('61b410bf', 'src/common/diagB32.cpp', 1426, 'kq_ns += m_kqc[h % kHist];', '}'),
    ('61b410bf', 'src/common/diagB32.cpp', 1459, 'if (Core::CodeState(code) == State::S && wkq[j] == 0 && nearest[j] >= 0) {', 'const auto kc = m_kcodes['),
    ('61b410bf', 'src/common/diagB32.cpp', 1548, 'const auto pub = g_flip_pub.load(std::memory_order_acquire);', 'if (pub == m_seen_flips) {'),
    ('61b410bf', 'src/common/diagB32.cpp', 1568, 'g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn);', 'for (auto& w: m_ring_tmp) {'),
    ('61b410bf', 'src/common/diagB32.cpp', 1591, 'm_win_extra_ns += FrameStats::NowNs() - t0;', 'm_win_m5r_ns += m5r;'),
    ('61b410bf', 'src/common/diagB32.cpp', 1647, 'const auto next = Core::NextBegin(begin, now);', 'if (next >= now + 100) {'),
    ('61b410bf', 'src/common/diagB32.cpp', 854, 'void Mark::BeginH(Call call) {', 'const auto slot1 = SelfSlot();'),
    ('61b410bf', 'src/common/diagB32.cpp', 894, 'void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {', 'if (!m_active) {'),
    ('61b410bf', 'src/common/diagB32.h', 81, '~Mark() {', 'if (m_active) {'),
    ('61b410bf', 'src/common/diagB32.h', 94, 'void End(int32_t waker_slot1, bool timed_out) {', 'if (m_active) {'),
    ('61b410bf', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 129, 'if (Common::DiagB32::g_on) [[unlikely]] {', 'Common::DiagB32::RegisterRole("ASubmit");'),
    ('61b410bf', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 146, 'Common::DiagB32::Mark b32_q; // Track F, F20j2', 'if (Common::DiagB32::g_on) [[unlikely]] {'),
    ('61b410bf', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 150, 'Common::LockGuard lock(graphics.queue_mutex);', 'b32_q.End(0, false);'),
    ('61b410bf', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 174, 'b32_q.BeginH(Common::DiagB32::Call::QSubmit);', '}'),
    ('61b410bf', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 176, 'result = graphics.queue.submit(1, &submit_info, nullptr);', 'b32_q.End(0, false);'),
    ('61b410bf', 'src/graphics/presentation/window/swapchain.cpp', 800, 'Common::DiagB32::Mark b32_q;', 'if (Common::DiagB32::g_on) [[unlikely]] {'),
    ('61b410bf', 'src/graphics/presentation/window/swapchain.cpp', 804, 'Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);', 'b32_q.End(0, false);'),
    ('61b410bf', 'src/graphics/presentation/window/swapchain.cpp', 589, 'Common::LockGuard queue_lock(graphics.queue_mutex);', 'RequireVulkanSuccess(graphics.queue.waitIdle()'),
    ('61b410bf', 'src/graphics/presentation/systemOverlay.cpp', 1075, 'Common::DiagB32::Mark b32_q; // Track F, F20j2', 'if (Common::DiagB32::g_on) [[unlikely]] {'),
    ('61b410bf', 'src/graphics/presentation/videoOut.cpp', 1230, 'b32.BeginH(Common::DiagB32::Call::Present);', '}'),
    ('61b410bf', 'src/graphics/presentation/videoOut.cpp', 1232, 'Common::DiagB32::TestPresentPoint();', '}'),
    ('61b410bf', 'src/graphics/presentation/videoOut.cpp', 1234, 'm_presenter.Present(*r.frame);', 'b32.End(0, false);'),
    ('61b410bf', 'src/graphics/presentation/renderDoc.cpp', 228, 'Common::LockGuard queue_lock(renderer.GetGraphics().queue_mutex);', 'if (state == RenderDocState::Requested) {'),
    ('61b410bf', 'tests/DiagB32Tests.cpp', 625, 'if (k <= 13300000 && dt > 115000000) {', 'CHECK(o.dt_minus >= 100000000);'),
    ('61b410bf', 'tests/DiagB32Tests.cpp', 677, 'static void TestWindowDelta() {', 'Case("F20j2 RC3: zero invariants per window (_w)'),
    ('61b410bf', 'tests/DiagB32Tests.cpp', 711, 'static void TestDrainPreempted() {', 'Case("F20j2 RC4: drain with a writer preempted'),
]
cache = {}
ok = True
for c, p, n, a, b in R:
    k = (c, p)
    if k not in cache:
        cache[k] = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', c + ':' + p], capture_output=True).stdout.decode('utf-8').split('\n')
    L = cache[k]
    la = L[n - 1].strip() if n - 1 < len(L) else ''
    lb = L[n].strip() if n < len(L) else ''
    good = la.startswith(a) and lb.startswith(b)
    ok &= good
    print('%s %s:%s:%d' % ('ok  ' if good else 'FAIL', c, p, n))
print('refs %d' % len(R))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
