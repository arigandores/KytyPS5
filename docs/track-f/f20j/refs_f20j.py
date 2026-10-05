"""F20j (HPP-629): references of docs/track-f/f20j.md (rule 24(1): <commit>:<path>:<line>, anchor, +1).

  python refs_f20j.py gen    - resolves every (commit, path, needle[, nth]) of REFS to its line, writes refs_f20j.md
                               (markdown rows: ref, anchor, +1) for the report
  python refs_f20j.py check  - re-reads every row of refs_f20j.md with git show: the anchor is the line, +1 the next
                               line ('пустая строка' = empty); prints ALL OK
"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
B = '0df13a66'
DOC = 'fe0bf0a0'

REFS = [
    # decision, design, review
    (DOC, 'docs/ROADMAP.md', '550. **Звено F20i трека F (`HPP-628`, лид; приёмка F20g'),
    (DOC, 'docs/ROADMAP.md', '(в) **Разрешения RC (обязательны для F20j'),
    (DOC, 'docs/ROADMAP.md', '(г) **Правило чтения (до данных).**'),
    (DOC, 'docs/ROADMAP.md', '(з) **Звенья (стадия review лида у звена исполнителя).**'),
    ('86abd902', 'docs/track-f/f20g.md', '### 2.3 Сайты'),
    ('4bab4d66', 'docs/track-f/f20h-review.md', '## 2. Требуемые изменения'),
    # FS8 sources named by RC4 / RC12
    ('302347b4', 'src/common/frameStats.cpp', 'uint64_t ThreadCpuNs(ThreadRole role) {'),
    ('302347b4', 'src/common/threads.cpp', 'nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);'),
    # the module
    (B, 'src/common/diagB32.cpp', 'bool g_on            = false;'),
    (B, 'src/common/diagB32.cpp', 'uint16_t Classify(uint32_t mark, uint64_t cpu_ns, uint64_t interval_ns, bool kq, uint32_t kthread_state,'),
    (B, 'src/common/diagB32.cpp', 'GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns) {'),
    (B, 'src/common/diagB32.cpp', 'void WindowSamples(const uint64_t* t, const uint64_t* cost, const uint8_t* kq, uint64_t hpos, uint32_t hist,'),
    (B, 'src/common/diagB32.cpp', 'std::string SafeName(const char* name) {'),
    (B, 'src/common/diagB32.cpp', 'int32_t Registry::Allocate(uint32_t os_tid, void* handle, const char* role, const char* name, int32_t gid) {'),
    (B, 'src/common/diagB32.cpp', 'void Registry::WriteMark(int32_t idx, uint32_t mark, uint64_t obj, uint64_t since, int32_t peer) {'),
    (B, 'src/common/diagB32.cpp', 'bool Registry::ReadMark(int32_t idx, MarkSnap* out) {'),
    (B, 'src/common/diagB32.cpp', 'void WaitRing::Push(const WaitRec& rec) {'),
    (B, 'src/common/diagB32.cpp', 'void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn) {'),
    (B, 'src/common/diagB32.cpp', 'void MarkMandatory(Report* report) {'),
    (B, 'src/common/diagB32.cpp', 'std::string Format(Report* report, Counters* counters) {'),
    (B, 'src/common/diagB32.cpp', 'int32_t RegisterSelf(const char* role, const char* name, int32_t gid) {'),
    (B, 'src/common/diagB32.cpp', 'int32_t SelfSlot() {'),
    (B, 'src/common/diagB32.cpp', 'void RegisterRole(const char* role) {'),
    (B, 'src/common/diagB32.cpp', 'int32_t RegisterGuest(int32_t gid, const char* name) {'),
    (B, 'src/common/diagB32.cpp', 'void Unregister() {'),
    (B, 'src/common/diagB32.cpp', 'uint64_t PackSig() {'),
    (B, 'src/common/diagB32.cpp', 'void Mark::BeginH(Call call) {'),
    (B, 'src/common/diagB32.cpp', 'void Mark::BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {'),
    (B, 'src/common/diagB32.cpp', 'void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {'),
    (B, 'src/common/diagB32.cpp', 'void NoteSubmit(uint64_t seq) {'),
    (B, 'src/common/diagB32.cpp', 'void NoteCurrentSubmission(uint64_t seq) {'),
    (B, 'src/common/diagB32.cpp', 'void NoteFlipRequest(uint64_t request_id, bool cpu_source) {'),
    (B, 'src/common/diagB32.cpp', 'void OnFlip(uint64_t n, uint64_t request_id, uint64_t reserve_host_ns) {'),
    (B, 'src/common/diagB32.cpp', 'void TestArm() {'),
    (B, 'src/common/diagB32.cpp', 'static void TestSleepNow(const char* mode) {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::KernelQuery() {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::Sample(uint64_t t0) {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::M5Refresh(uint64_t now) {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::M5Snapshot() {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::M1Snapshot(uint64_t* proc_us, uint64_t* busy_us, uint64_t* idle_us) {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::ProcessFlips() {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::Run() {'),
    (B, 'src/common/diagB32.cpp', 'HANDLE timer = CreateWaitableTimerExW(nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);'),
    (B, 'src/common/diagB32.cpp', 'void Init() {'),
    (B, 'src/common/diagB32.cpp', 'void LogHeader() {'),
    # sites (first line of each site; the full list - sites_0df13a66.txt)
    (B, 'src/emulator.cpp', 'Common::DiagB32::Init();'),
    (B, 'src/emulator.cpp', 'Common::DiagB32::LogHeader(); // Track F, F20j: "DiagB32: mode=1 ..." / "TestB32: config ..." once'),
    (B, 'src/common/frameStats.cpp', 'Common::DiagB32::RegisterRole(static_cast<size_t>(role) < 4 ? names[static_cast<size_t>(role)] : "emu");'),
    (B, 'src/common/frameStats.cpp', 'double CpuCyclesPerNs() {'),
    (B, 'src/kernel/pthread.cpp', 'std::atomic<int32_t>  b32_slot1 {0}; // DiagB32 slot + 1 of this thread'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of this waiter'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the guest main thread\'s slot (registered as role Main)'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on && mutex->owner != nullptr && (timeout_us == nullptr || *timeout_us > 0)) [[unlikely]] {'),
    (B, 'src/kernel/pthread.cpp', 'b32.EndWithPeer(true);'),
    (B, 'src/kernel/pthread.cpp', 'b32.EndWithPeer(false);'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of every waiter'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, static_cast<uint64_t>(usec));'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, B32ReqUs(deadline));'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, 0);'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the slot stops being sampled'),
    (B, 'src/kernel/pthread.cpp', 'if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (KYTY_DIAG_B32): the guest thread\'s slot, name and id'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, static_cast<uint64_t>(microseconds));'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, static_cast<uint64_t>(seconds) * 1000000ull);'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, nanos / 1000u);'),
    (B, 'src/kernel/semaphore.cpp', 'b32.BeginW(Common::DiagB32::Wait::Sem, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));'),
    (B, 'src/kernel/semaphore.cpp', 'b32.BeginW(Common::DiagB32::Wait::PSem, this, 0, timed_wait ? static_cast<uint64_t>(*micros) : 0);'),
    (B, 'src/kernel/semaphore.cpp', 'std::atomic<uint64_t> m_b32_sig {0};', 0),
    (B, 'src/kernel/semaphore.cpp', 'std::atomic<uint64_t> m_b32_sig {0};', 1),
    (B, 'src/kernel/eventFlag.cpp', 'b32.BeginW(Common::DiagB32::Wait::Evf, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));'),
    (B, 'src/kernel/eventFlag.cpp', 'std::atomic<uint64_t> m_b32_sig {0};'),
    (B, 'src/kernel/eventQueue.cpp', 'b32.BeginW(Common::DiagB32::Wait::Eq, this, 0, micros);'),
    (B, 'src/kernel/eventQueue.cpp', 'std::atomic<uint64_t> m_b32_sig {0};'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'Common::DiagB32::NoteFlipRequest(request_id, source == FlipRequestSource::Cpu);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'if (Common::DiagB32::g_present_site) [[unlikely]] {'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);'),
    (B, 'src/graphics/presentation/window/swapchain.cpp', 'b32.BeginH(Common::DiagB32::Call::Acquire);'),
    (B, 'src/graphics/presentation/window/window.cpp', 'Common::DiagB32::TestArm();'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'b32_drain.BeginH(Common::DiagB32::Call::Drain);'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'b32_q.BeginH(Common::DiagB32::Call::QLock);'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'b32_q.BeginH(Common::DiagB32::Call::QSubmit);'),
    (B, 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 'b32.BeginH(Common::DiagB32::Call::SemWait);'),
    (B, 'src/common/platform/sysWindowsVirtual.cpp', 'b32.BeginH(Common::DiagB32::Call::Protect);'),
    (B, 'src/common/hostException.cpp', 'b32.BeginH(Common::DiagB32::Call::Fault);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'Common::DiagB32::NoteSubmit(submission.bf.seq);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'Common::DiagB32::TestGpuSleepPoint();'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.BeginW(Common::DiagB32::Wait::GpuIdle, gpu, 0, 0);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.BeginW(Common::DiagB32::Wait::GpuRegmem, gpu, 0, 100000);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'Common::DiagB32::NoteCurrentSubmission(submission.bf.seq);'),
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
        hits = [i for i, l in enumerate(lines) if needle in l]
        if len(hits) <= nth:
            print('NOT FOUND', commit, path, needle[:60])
            bad += 1
            continue
        i = hits[nth]
        anchor = lines[i].strip()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
        if len(anchor) > 150:
            anchor = anchor[:150]
        if len(nxt) > 150:
            nxt = nxt[:150]
        rows.append('| `%s:%s:%d` | «%s» | «%s» |' % (commit, path, i + 1, esc(anchor), esc(nxt)))
    open('refs_f20j.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('rows %d not found %d' % (len(rows) - 2, bad))


def check():
    bad = 0
    n = 0
    for row in open('refs_f20j.md', encoding='utf-8').read().split('\n')[2:]:
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
