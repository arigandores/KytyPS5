# Red Team F20k3 (HPP-647): reference map of the review - <commit>:<path>:<line> with the anchor (the line) and +1
# (the next line), checked by substring. "python refs_f20k3.py" prints every reference and ALL OK / FAILED.
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
R = [
    # (commit, path, line, anchor substring, +1 substring)
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 194, 'for (;;) {', "This thread's own head"),
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 225, 'Wait::RecWait, this', '}'),
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 227, 'm_progress.wait_for(lock, WaitSlice, [this, head, want] {', 'const auto in_use'),
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 578, 'Wait::RecWait, this', '}'),
    ('9db7938b', 'src/common/diagB32.h', 217, 'void unlock() { m_m.unlock(); }', 'void lock_shared() {'),
    ('9db7938b', 'src/common/diagB32.h', 224, 'b32.BeginWReg(K, this, m_owner.load(std::memory_order_relaxed), 0);', 'm_m.lock_shared();'),
    ('9db7938b', 'src/common/diagB32.h', 238, 'b32.BeginWReg(K, this, m_owner.load(std::memory_order_relaxed), 0);', 'm_m.lock();'),
    ('9db7938b', 'src/common/diagB32.h', 242, 'm_owner.store(SelfSlotIfRegistered(), std::memory_order_relaxed);', '}'),
    ('9db7938b', 'src/graphics/host_gpu/renderer/renderContext.h', 99, 'TrackedMutex<std::shared_mutex> m_mapped_ranges_mutex;', ''),
    ('9db7938b', 'src/graphics/host_gpu/renderer/renderContext.cpp', 276, 'std::lock_guard lock(m_mapped_ranges_mutex);', ''),
    ('9db7938b', 'src/graphics/host_gpu/renderer/renderContext.cpp', 325, 'std::shared_lock          lock(m_mapped_ranges_mutex);', 'static const bool         reuse'),
    ('9db7938b', 'src/common/diagB32.cpp', 1804, 'const uint64_t m5r = m_m5r.TakeWorkNs();', 'M5Adopt();'),
    ('9db7938b', 'src/common/diagB32.cpp', 1827, 'CloseWindow(n, ns, lat, slot1, src', ''),
    ('9db7938b', 'src/common/diagB32.cpp', 1836, 'm_win_extra_ns += FrameStats::NowNs() - t0 + m5r;', 'm_win_m5r_ns += m5r;'),
    ('9db7938b', 'src/common/diagB32.cpp', 1619, 'const uint64_t extra = m_win_extra_ns + print_ns;', 'const uint64_t m5r   = m_win_m5r_ns;'),
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 162, 'b32_q.BeginH(Common::DiagB32::Call::QLock);', '}'),
    ('9db7938b', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 164, 'Common::LockGuard lock(graphics.queue_mutex);', 'b32_q.End(0, false);'),
    ('9db7938b', 'src/graphics/presentation/window/swapchain.cpp', 811, 'b32_q.BeginH(Common::DiagB32::Call::QLock);', '}'),
    ('9db7938b', 'src/graphics/presentation/window/swapchain.cpp', 813, 'Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);', 'b32_q.End(0, false);'),
    ('9db7938b', 'src/common/threads.cpp', 337, 'void Mutex::LockB32() {', '#ifdef KYTY_WIN_CS'),
    ('9db7938b', 'src/common/threads.cpp', 344, 'Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);', 'EnterCriticalSection(&m_mutex->m_cs);'),
    ('9db7938b', 'src/common/diagB32.h', 66, 'Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock, Count', '};'),
    ('9db7938b', 'src/common/diagB32.h', 72, 'return kind >= kFirstEmuWait && kind < kFirstGuestHleWait;', '}'),
    ('9db7938b', 'src/common/threads.cpp', 257, 'b32.BeginWReg(DiagB32::Wait::Join, this, 0, 0);', '}'),
    ('eead6454', 'docs/ROADMAP.md', 23220, 'RC7', ''),
    ('eead6454', 'docs/ROADMAP.md', 23423, '574. **Звено F20m трека F (`HPP-632`, лид): чтение контролей F20l', '(а) **Данные лида [c]**'),
    ('eead6454', 'docs/ROADMAP.md', 23428, '(д) **Поправка правила чтения п. 550(г)(2)(iv)', '(е) **Повтор контролей'),
    ('eead6454', 'docs/ROADMAP.md', 23459, '580. **Звено F20j3 трека F (`HPP-646`, лид): F20j3 ПРИНЯТ', '(а) **Приёмка строкой (правило 24):**'),
]


def lines_of(commit, path):
    out = subprocess.run([GIT, '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout
    return out.decode('utf-8').split('\n')


ok = True
cache = {}
for commit, path, line, a, b in R:
    key = (commit, path)
    if key not in cache:
        cache[key] = lines_of(commit, path)
    L = cache[key]
    anchor = L[line - 1].strip() if line - 1 < len(L) else ''
    nxt = L[line].strip() if line < len(L) else ''
    good = a in anchor and b in nxt
    ok &= good
    print(f'{"ok " if good else "BAD"} {commit}:{path}:{line} | {anchor[:110]} | +1 {nxt[:70]}')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
