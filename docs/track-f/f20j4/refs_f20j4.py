"""F20j4 (HPP-652): references of docs/track-f/f20j4.md (rule 24(1): <commit>:<path>:<line>, anchor, +1). Copy of
refs_f20j3.py (F20j3) with the F20j4 list.

  python refs_f20j4.py gen    - resolves every (commit, path, needle[, nth]) of REFS to its line (needle = the whole
                                stripped line, or its start for a needle of >= 40 characters), writes refs_f20j4.md
  python refs_f20j4.py check  - re-reads every row of refs_f20j4.md with git show: the anchor is the line, +1 the next
                                line ('пустая строка' = empty); prints ALL OK
"""
import subprocess
import sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
B = 'f2307b02'  # the worktree commit of the test binary (main: 4371ff4b, patch-id 491cf87a4853 equal)
M = '4371ff4b'
OLD = '9db7938b'
DOC = 'de144412'

REFS = [
    # decision
    (DOC, 'docs/ROADMAP.md', '581. **Звено F20k3 трека F (`HPP-647`, лид): F20k3 ПРИНЯТ'),
    (DOC, 'docs/ROADMAP.md', '(в) **Решения по RC (решение лида).** (1) **RC1 — кодом по предложению отзыва:**'),
    (DOC, 'docs/ROADMAP.md', '(д) **F20j4 (Emu Engineer) — состав (обязателен):** RC1–RC5 по (в)(1)–(5) с тестами;'),
    # RC1
    (OLD, 'src/graphics/host_gpu/renderer/commandRecorder.cpp', '// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the producer waits for the record thread.'),
    (B, 'src/graphics/host_gpu/renderer/commandRecorder.cpp', '// Track F, F20j4 (KYTY_DIAG_B32 W:rec_wait, item 581(v)(1), RC1 of F20k3): one mark over the whole retry loop - begun'),
    (B, 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 'if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {'),
    (B, 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 'b32.EndSig(&m_progress); // F20j4 (RC1): the end of the whole retry loop (one test of the flag at =0)'),
    # RC2
    (OLD, 'src/common/diagB32.h', 'void unlock() { m_m.unlock(); }'),
    (B, 'src/common/diagB32.h', 'void unlock() {'),
    (B, 'src/common/diagB32.h', 'void TakeOwner() {'),
    (B, 'src/common/diagB32.h', 'void ReleaseOwner() {'),
    (B, 'src/common/diagB32.cpp', 'm_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself', 0),
    (B, 'src/common/diagB32.cpp', 'm_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself', 1),
    # RC3
    (OLD, 'src/common/diagB32.cpp', 'const uint64_t m5r = m_m5r.TakeWorkNs();'),
    (B, 'src/common/diagB32.h', 'class M5Charge {'),
    (B, 'src/common/diagB32.cpp', 'PushRun(t0, t1);'),
    (B, 'src/common/diagB32.cpp', 'void AsyncRefresh::TakeRuns(std::vector<Run>* out) {'),
    (B, 'src/common/diagB32.cpp', 'uint64_t M5Charge::Window(uint64_t start, uint64_t end) const {'),
    (B, 'src/common/diagB32.cpp', 'const uint64_t m5r   = m_m5c.Window(start, flip_ns);'),
    (B, 'src/common/diagB32.cpp', 'm_m5c.Add(m_m5_runs, m5_cur);'),
    (B, 'src/common/diagB32.cpp', 'm_m5c.Prune(m_win_start);'),
    # RC4
    (OLD, 'src/common/threads.cpp', 'b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);'),
    (B, 'src/common/diagB32.cpp', 'void Mark::BeginWLock(Wait kind, const void* obj, int32_t peer_slot1) {'),
    (B, 'src/common/threads.cpp', 'b32.BeginWLock(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner));'),
    (B, 'src/common/diagB32.h', 'b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));', 0),
    (B, 'src/common/diagB32.h', 'b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));', 1),
    # RC4 reference: the H sites and the W kinds reachable under them
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'b32_drain.BeginH(Common::DiagB32::Call::Drain);'),
    (B, 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 'AsyncSubmitter::Get().Drain();'),
    (B, 'src/graphics/presentation/videoOut.cpp', 'b32.BeginH(Common::DiagB32::Call::Present);'),
    (B, 'src/graphics/presentation/window/swapchain.cpp', 'm_window.RunOnMainThread([this] { m_window.RecreateSurface(); });'),
    (B, 'src/graphics/presentation/window/swapchain.cpp', 'b32.BeginH(Common::DiagB32::Call::Acquire);'),
    (B, 'src/common/hostException.cpp', 'b32.BeginH(Common::DiagB32::Call::Fault);'),
    (B, 'src/common/platform/sysWindowsVirtual.cpp', 'b32.BeginH(Common::DiagB32::Call::Protect);'),
    (B, 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 'b32.BeginH(Common::DiagB32::Call::SemWait);'),
    # RC5
    (OLD, 'src/common/threads.cpp', 'b32.BeginWReg(DiagB32::Wait::Join, this, 0, 0);'),
    (B, 'src/common/diagB32.h', 'EmuJoin, Count'),
    (B, 'src/common/diagB32.h', '[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {'),
    (B, 'src/common/threads.cpp', 'b32.BeginWReg(DiagB32::Wait::EmuJoin, this, 0, 0);'),
    (B, 'src/kernel/pthread.cpp', 'b32.BeginWReg(Common::DiagB32::Wait::Join, thread, thread->b32_slot1.load(std::memory_order_relaxed), 0);'),
    # tests
    (B, 'tests/DiagB32Tests.cpp', 'CHECK(n_emu == 25 + 5);'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestM5Charge() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestPeerSelfRuntime() {'),
    (B, 'tests/DiagB32Tests.cpp', 'static void TestLockUnderHRuntime() {'),
    # main
    (M, 'src/common/diagB32.h', 'class M5Charge {'),
    (M, 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 'b32.EndSig(&m_progress); // F20j4 (RC1): the end of the whole retry loop (one test of the flag at =0)'),
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
    open('refs_f20j4.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('rows %d not found %d' % (len(rows) - 2, bad))


def check():
    bad = 0
    n = 0
    for row in open('refs_f20j4.md', encoding='utf-8').read().split('\n')[2:]:
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
