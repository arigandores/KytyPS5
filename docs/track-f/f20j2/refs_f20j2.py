"""F20j2 (HPP-633): references of docs/track-f/f20j2.md (rule 24(1): <commit>:<path>:<line>, anchor, +1). Copy of
refs_f20j.py (F20j) with the F20j2 list.

  python refs_f20j2.py gen    - resolves every (commit, path, needle[, nth]) of REFS to its line (needle = the whole
                                stripped line, or its start for a line longer than 150 characters), writes refs_f20j2.md
  python refs_f20j2.py check  - re-reads every row of refs_f20j2.md with git show: the anchor is the line, +1 the next
                                line ('пустая строка' = empty); prints ALL OK
"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
B = '61b410bf'  # the worktree commit of the test binary (main: 18dd03a6, the same added/removed lines)
DOC = 'aaf4504e'

REFS = [
    # decision and review
    (DOC, 'docs/ROADMAP.md', '552. **Звено F20k трека F (`HPP-630`, Red Team; приёмка лида'),
    (DOC, 'docs/ROADMAP.md', '(в) **Разрешения RC1–RC7 F20k (обязательны для F20j2;'),
    (DOC, 'docs/ROADMAP.md', '(д) **Звенья (стадия review лида у звена исполнителя).** **F20j2**'),
    ('d63d7feb', 'docs/track-f/f20k-review.md', '## 2. Требуемые изменения'),
    # RC1 - schedule, absolute period, nearest snapshot, kq_n / kq_us
    (B, 'src/common/diagB32.h', 'constexpr uint64_t kKqBudgetDiv   = 10;'),
    (B, 'src/common/diagB32.h', 'struct KqSchedule {'),
    (B, 'src/common/diagB32.cpp', 'bool KqSchedule::Due(uint64_t now_ns) const {'),
    (B, 'src/common/diagB32.cpp', 'return (win_kq_ns + last_kq_ns) * kKqBudgetDiv <= now_ns - win_start;'),
    (B, 'src/common/diagB32.cpp', 'uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns) {'),
    (B, 'src/common/diagB32.cpp', 'void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,'),
    (B, 'src/common/diagB32.cpp', 'if (m_kq_ok && m_sched.Due(begin)) {'),
    (B, 'src/common/diagB32.cpp', 'm_sched.NewWindow(flip_ns, carried);'),
    (B, 'src/common/diagB32.cpp', 'Core::NearestSnapshot(times.data(), wkq.data(), wkqt.data(), idx.size(), kKqNearNs, nearest.data());'),
    (B, 'src/common/diagB32.cpp', 'if (Core::CodeState(code) == State::S && wkq[j] == 0 && nearest[j] >= 0) {'),
    (B, 'src/common/diagB32.cpp', '// A flip published together with the timer is taken first, so the schedule sees the current window start.'),
    (B, 'src/common/diagB32.cpp', 'const auto next = Core::NextBegin(begin, now);'),
    (B, 'src/common/diagB32.cpp', '" kq_n=%u kq_us=%llu m5r_us=%llu"'),
    (B, 'src/common/diagB32.cpp', 'g_kq_first_us.store((FrameStats::NowNs() - q0) / 1000u, std::memory_order_relaxed); // F20j2: kq_us of mode=1'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestSchedule() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestNearest() {'),
    # RC2
    (B, 'src/common/diagB32.cpp', 'const uint64_t t0       = FrameStats::NowNs();'),
    (B, 'src/common/diagB32.cpp', 'm_kqt[pos]  = kq_t;'),
    (B, 'src/common/diagB32.cpp', 'm_cost[pos] = FrameStats::NowNs() - begin; // RC9: the whole sample, the kernel query included'),
    # RC3
    (B, 'src/common/diagB32.cpp', '"DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"'),
    (B, 'src/common/diagB32.cpp', 'void Counters::Rebase() {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::RefreshCounters() {'),
    (B, 'src/common/diagB32.cpp', 'RefreshCounters();'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestWindowDelta() {'),
    # RC4
    (B, 'src/common/diagB32.cpp', 'uint64_t WaitRing::Reserve() {'),
    (B, 'src/common/diagB32.cpp', 'if (s1 < want) {'),
    (B, 'src/common/diagB32.cpp', '// Overwritten by a later lap before or while it was read: the record is lost (F20j2 RC4 - only this is torn).'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestDrainPreempted() {'),
    # RC5
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'Common::DiagB32::RegisterRole("ASubmit");'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock / H:qsubmit, RC5 of F20k)'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qsubmit, RC5 of F20k)'),
    (B, 'src/graphics/presentation/window/swapchain.cpp', '// Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k): nested in H:present - a sample shows the innermost mark,'),
    (B, 'src/graphics/presentation/systemOverlay.cpp', 'Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k)'),
    (B, 'src/common/diagB32.cpp', 'const bool asub = t.role == "ASubmit" &&'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'Common::DiagB32::TestPresentPoint();'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'm_presenter.Present(*r.frame);'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestASubmit() {'),
    # RC6
    (B, 'src/common/diagB32.cpp', 'e.print_ns.store(g_print_prev_ns, std::memory_order_relaxed);'),
    (B, 'src/common/diagB32.cpp', 'g_print_prev_ns = print_ns;'),
    (B, 'src/common/diagB32.cpp', 'const uint64_t extra = m_win_extra_ns + print_ns; // F20j2 RC6: the report print inside this window'),
    (B, 'src/graphics/presentation/videoOut.cpp', '// reports the sampler has closed are printed here, under FlipQueue::m_mutex and VideoOutConfig::mutex (F20j2, RC6 of'),
    # RC7
    (B, 'src/common/diagB32.cpp', 'g_sub_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten'),
    (B, 'src/common/diagB32.cpp', 'g_req_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten'),
    # item 552(e)(3)
    (B, 'src/common/diagB32.cpp', 'm5r = FrameStats::NowNs() - t0; // F20j2 (item 552(e)(3)): the refresh\'s share of the boundary work'),
    # F20k sites named in RC5 (the binary of F20j)
    ('0df13a66', 'src/graphics/presentation/window/swapchain.cpp', 'Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);'),
    ('0df13a66', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'Common::LockGuard lock(graphics.queue_mutex);', 0),  # the first of two: the async submitter (:141); the second is the synchronous Submit
    ('0df13a66', 'src/graphics/presentation/systemOverlay.cpp', 'Common::LockGuard queue_lock(graphics.queue_mutex);'),
    # queue_mutex captures outside the RC5 inventory (not marked)
    (B, 'src/graphics/presentation/window/swapchain.cpp', 'Common::LockGuard queue_lock(graphics.queue_mutex);'),
    (B, 'src/graphics/presentation/renderDoc.cpp', 'Common::LockGuard queue_lock(renderer.GetGraphics().queue_mutex);'),
]


def show(commit, path, cache={}):
    k = (commit, path)
    if k not in cache:
        cache[k] = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True,
                                  check=True).stdout.decode('utf-8').replace('\r\n', '\n').split('\n')
    return cache[k]


def esc(s):
    return s.replace('|', '\\|') if s else 'пустая строка'


def gen():
    rows = ['| ссылка | якорь (строка) | +1 |', '|---|---|---|']
    bad = 0
    for item in REFS:
        commit, path, needle = item[0], item[1], item[2]
        nth = item[3] if len(item) > 3 else 0
        lines = show(commit, path)
        hits = [i for i, l in enumerate(lines) if l.strip() == needle or (len(needle) >= 40 and l.strip().startswith(needle))]
        if len(hits) != 1 and nth == 0 and len(item) <= 3:
            print('NOT UNIQUE (%d)' % len(hits), commit, path, needle[:70])
            bad += 1
            continue
        i = hits[nth]
        anchor = lines[i].strip()[:150]
        nxt = (lines[i + 1].strip() if i + 1 < len(lines) else '')[:150]
        rows.append('| `%s:%s:%d` | «%s» | «%s» |' % (commit, path, i + 1, esc(anchor), esc(nxt)))
    open('refs_f20j2.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('rows %d not found %d' % (len(rows) - 2, bad))


def check():
    bad = 0
    n = 0
    for row in open('refs_f20j2.md', encoding='utf-8').read().split('\n')[2:]:
        if not row:
            continue
        parts = row.split(' | ')
        ref = parts[0].strip('| `')
        anchor = parts[1].strip()[1:-1].replace('\\|', '|')
        nxt = parts[2].strip(' |')[1:-1].replace('\\|', '|')
        commit, path, line = ref.split(':')
        lines = show(commit, path)
        i = int(line) - 1
        a = lines[i].strip()[:150]
        b = (lines[i + 1].strip() if i + 1 < len(lines) else '')[:150]
        ok = a == anchor and (b == nxt or (nxt == 'пустая строка' and b == ''))
        n += 1
        if not ok:
            bad += 1
            print('BAD', ref)
    print('refs %d bad %d' % (n, bad))
    print('ALL OK' if bad == 0 else 'FAILED')


if __name__ == '__main__':
    gen() if sys.argv[1] == 'gen' else check()
