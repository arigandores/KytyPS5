"""F20j3 (HPP-646): references of docs/track-f/f20j3.md (rule 24(1): <commit>:<path>:<line>, anchor, +1). Copy of
refs_f20j2.py (F20j2) with the F20j3 list.

  python refs_f20j3.py gen    - resolves every (commit, path, needle[, nth]) of REFS to its line (needle = the whole
                                stripped line, or its start for a needle of >= 40 characters), writes refs_f20j3.md
  python refs_f20j3.py check  - re-reads every row of refs_f20j3.md with git show: the anchor is the line, +1 the next
                                line ('пустая строка' = empty); prints ALL OK
"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
B = '9db7938b'  # the worktree commit of the test binary (main: 2cde5ef2, patch-id 68ed8d1c equal)
DOC = 'ea79e31c'

REFS = [
    # decision
    (DOC, 'docs/ROADMAP.md', '574. **Звено F20m трека F (`HPP-632`, лид): чтение контролей F20l'),
    (DOC, 'docs/ROADMAP.md', '(г) **Правка F20j3 — состав (обязателен; детали реализации — исполнитель'),
    (DOC, 'docs/ROADMAP.md', '(д) **Поправка правила чтения п. 550(г)(2)(iv) — до кода и до данных повтора'),
    # (g)(1) kinds and marks
    (B, 'src/common/diagB32.h', 'EmuMutex, GpuWait, GpuCmd, FlipSlot, FlipDone, FlipCancel, FlipReq, VoPace, Relay, FramePool, RecWait, RecIdle,'),
    (B, 'src/common/diagB32.h', 'Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock, Count'),
    (B, 'src/common/diagB32.h', '[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {'),
    (B, 'src/common/diagB32.h', '[[nodiscard]] constexpr bool MutexLike(uint8_t kind) {'),
    (B, 'src/common/diagB32.h', 'void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);'),
    (B, 'src/common/diagB32.h', 'class TrackedMutex {'),
    (B, 'src/common/diagB32.cpp', 'void Mark::BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {'),
    (B, 'src/common/threads.cpp', 'void Mutex::LockB32() {'),
    (B, 'src/common/threads.cpp', 'b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::GpuWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.End(m_idle.B32Waker(b32.SinceNs()), false);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::GpuCmd, &done, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::Relay, relay, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Relay), 0);'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'Common::DiagB32::TestGpuSleepPoint();'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::FlipSlot, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::FlipDone, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::FlipCancel, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::FlipReq, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), micros);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::Vblank, ctx, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::VoPace, this, 0, remaining_us);'),
    (B, 'src/graphics/presentation/window/swapchain.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::FramePool, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'Common::DiagB32::RegisterRole("POps");'),
    # (g)(2) waker / peer
    (B, 'src/common/diagB32.h', 'enum class Peer : uint8_t { Present = 0, Gpu, ASubmit, POps, Relay, Main, Record, Count };'),
    (B, 'src/common/diagB32.h', 'void EndSig(const void* obj, bool timed_out = false) {'),
    (B, 'src/common/diagB32.h', 'int32_t  peer1    = 0; // F20j3 (item 574(g)(2), (d)): the mark\'s peer, slot + 1, 0 = none'),
    (B, 'src/common/diagB32.cpp', 'void NoteSignalSlow(const void* obj) {'),
    (B, 'src/common/diagB32.cpp', 'rec.peer1     = m_peer; // F20j3 (item 574(g)(2))'),
    (B, 'src/common/diagB32.cpp', 'w.waker1   = MutexLike(static_cast<uint8_t>(m_last_mark[i].mark & 0xffu)) ? m_last_mark[i].peer : 0;'),
    (B, 'src/common/diagB32.cpp', '" waker_tid=%d req_us=%llu to=%u open=%u peer=%d peer_tid=%d\\n",'),
    (B, 'src/common/threads.cpp', 'int32_t CondVar::B32Waker(uint64_t since_ns) const {'),
    # (g)(3) the DrawThread wait - the code path
    (B, 'src/libs/agc.cpp', 'int KYTY_SYSV_ABI AgcSuspendPoint() {'),
    (B, 'src/graphics/guest_gpu/graphicsRun.cpp', 'void GuestGpu::Done() {'),
    (B, 'src/common/threads.cpp', 'if (func(&m_cond_var->m_cv, &mutex->m_mutex->m_cs, 10) == 0 &&'),
    (B, 'src/kernel/pthread.cpp', 'Common::CondVar::SetWaitPollCallback(KernelDispatchPendingSignalForCurrentThread);'),
    # (g)(4) M5
    (B, 'src/common/diagB32.h', 'class AsyncRefresh {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::M5RefreshWork(void* user) {'),
    (B, 'src/common/diagB32.cpp', 'void Sampler::M5Adopt() {'),
    (B, 'src/common/diagB32.cpp', 'const uint64_t m5r = m_m5r.TakeWorkNs();'),
    (B, 'src/common/diagB32.cpp', 'm_win_extra_ns += FrameStats::NowNs() - t0 + m5r;'),
    (B, 'src/common/diagB32.cpp', 'm_m5r.Start(&Sampler::M5RefreshWork, &m_m5s, 1000000000ull);'),
    # (g)(5) Z1
    (B, 'src/common/diagB32.h', 'uint64_t ring_hold    = 0;'),
    (B, 'src/common/diagB32.cpp', 'g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn, &m_ring_hold);'),
    (B, 'src/common/diagB32.cpp', '" ring_hold=%llu ring_hold_w=%llu\\n",'),
    # (g)(6) =0 - the primitive's one test
    (B, 'src/common/threads.cpp', 'if (DiagB32::g_on) [[unlikely]] { // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, item 574(g)(1)): one test at =0'),
    # tests
    (B, 'tests/DiagB32Tests.cpp', 'static void TestKinds() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestRingHold() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestPeerFields() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestM5Async() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestWaitLoopRuntime() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestEmuMutexRuntime() {'),
    (B, 'tests/DiagB32Tests.cpp', 'CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0\\n") != std::string::npos);'),
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
        if len(hits) != 1 and len(item) <= 3:
            print('NOT UNIQUE (%d)' % len(hits), commit, path, needle[:70])
            bad += 1
            continue
        i = hits[nth]
        anchor = lines[i].strip()[:150]
        nxt = (lines[i + 1].strip() if i + 1 < len(lines) else '')[:150]
        rows.append('| `%s:%s:%d` | «%s» | «%s» |' % (commit, path, i + 1, esc(anchor), esc(nxt)))
    open('refs_f20j3.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('rows %d not found %d' % (len(rows) - 2, bad))


def check():
    bad = 0
    n = 0
    for row in open('refs_f20j3.md', encoding='utf-8').read().split('\n')[2:]:
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
