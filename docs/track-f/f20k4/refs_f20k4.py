# Red Team F20k4 (HPP-653): every <commit>:<path>:<line> reference of the review - the anchor (a prefix of the whole line,
# leading whitespace stripped, <= 150 chars) and the next line (+1, prefix). Mode "find" prints the line numbers;
# mode "check" verifies the numbers written in REFS. Ends with ALL OK / FAILED.
import subprocess, sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'

# (commit, path, line or 0, anchor, plus1)
REFS = [
    ('f2307b02', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 197, 'Common::DiagB32::Mark b32;', 'for (;;) {'),
    ('f2307b02', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 227, 'if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {', 'b32.BeginWReg(Common::DiagB32::Wait::RecWait, this,'),
    ('f2307b02', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 262, 'b32.EndSig(&m_progress); // F20j4 (RC1)', 'return m_data.get() + index;'),
    ('f2307b02', 'src/common/diagB32.h', 239, 'void unlock() {', 'if (g_on) [[unlikely]] {'),
    ('f2307b02', 'src/common/diagB32.h', 273, 'void TakeOwner() {', 'if (m_depth++ == 0) {'),
    ('f2307b02', 'src/common/diagB32.h', 278, 'void ReleaseOwner() {', 'if (m_depth > 1) {'),
    ('f2307b02', 'src/common/diagB32.h', 289, 'int32_t              m_depth = 0;', '};'),
    ('f2307b02', 'src/common/diagB32.h', 81, '[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {', 'return (kind >= kFirstEmuWait && kind < kFirstGuestHleWait) ||'),
    ('f2307b02', 'src/common/diagB32.h', 72, 'EmuJoin, Count', '};'),
    ('f2307b02', 'src/common/diagB32.cpp', 1109, 'm_peer       = peer_slot1 == slot1 ? 0 : peer_slot1;', 'm_req_us     = req_us;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1129, 'm_peer       = peer_slot1 == slot1 ? 0 : peer_slot1;', 'm_req_us     = req_us;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1136, 'void Mark::BeginWLock(Wait kind, const void* obj, int32_t peer_slot1) {', 'const auto slot1 = SelfSlotIfRegistered();'),
    ('f2307b02', 'src/common/diagB32.cpp', 1141, 'if ((g_reg->slots[slot1 - 1].mark.load(std::memory_order_relaxed) >> 8u) == static_cast<uint32_t>(State::H)) {', 'return;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1153, 'if ((m_mark >> 8u) != static_cast<uint32_t>(State::W)) {', 'return;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1701, 'const uint64_t m5r   = m_m5c.Window(start, flip_ns);', 'const uint64_t extra = m_win_extra_ns + print_ns + m5r;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1766, 'r.m5r_us       = m5r / 1000u;', 'r.proc_us      = proc_us;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1875, 'if (pub == m_seen_flips) {', 'return;'),
    ('f2307b02', 'src/common/diagB32.cpp', 1886, 'const uint64_t m5_cur = m_m5r.CurrentBegin();', 'm_m5_runs.clear();'),
    ('f2307b02', 'src/common/diagB32.cpp', 1922, 'm_m5c.Prune(m_win_start);', '}'),
    ('f2307b02', 'src/common/diagB32.cpp', 0, 'uint64_t M5Charge::Window(uint64_t start, uint64_t end) const {', 'uint64_t sum = 0;'),
    ('f2307b02', 'src/common/diagB32.cpp', 0, 'void AsyncRefresh::TakeRuns(std::vector<Run>* out) {', 'const auto w = m_wpos.load(std::memory_order_acquire);'),
    ('f2307b02', 'src/common/diagB32.cpp', 0, 'void AsyncRefresh::PushRun(uint64_t begin_ns, uint64_t end_ns) {', 'const auto i = m_wpos.load(std::memory_order_relaxed);'),
    ('f2307b02', 'src/common/diagB32.cpp', 33, 'bool g_on            = false;', ''),
    ('f2307b02', 'src/common/diagB32.cpp', 2002, 'g_on = true;', '} else if (std::strcmp(v, "0") != 0) {'),
    ('f2307b02', 'src/common/diagB32.cpp', 2065, 'g_on = true;', ''),
    ('f2307b02', 'src/common/threads.cpp', 0, 'b32.BeginWReg(DiagB32::Wait::EmuJoin, this, 0, 0);', '}'),
    ('f2307b02', 'src/common/threads.cpp', 0, 'b32.BeginWLock(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner));', 'EnterCriticalSection(&m_mutex->m_cs);'),
    ('f2307b02', 'src/kernel/pthread.cpp', 3564, 'b32.BeginWReg(Common::DiagB32::Wait::Join, thread,', '}'),
    ('f2307b02', 'src/kernel/memory.cpp', 885, 'static Common::DiagB32::TrackedMutex<std::recursive_mutex> g_memory_operation_mutex;', ''),
    ('f2307b02', 'src/libs/libUlt.cpp', 42, 'Common::DiagB32::TrackedMutex<std::recursive_mutex, Common::DiagB32::Wait::Ult> mutex;', ''),
    ('f2307b02', 'src/graphics/presentation/videoOut.cpp', 1269, 'b32.BeginH(Common::DiagB32::Call::Present);', '}'),
    ('f2307b02', 'src/graphics/presentation/videoOut.cpp', 1273, 'm_presenter.Present(*r.frame);', 'b32.End(0, false);'),
    ('f2307b02', 'src/graphics/presentation/window/swapchain.cpp', 639, '#if defined(__APPLE__)', '// Surface recreation goes through SDL_Vulkan_CreateSurface'),
    ('f2307b02', 'src/graphics/presentation/window/swapchain.cpp', 642, 'm_window.RunOnMainThread([this] { m_window.RecreateSurface(); });', '#else'),
    ('f2307b02', 'src/graphics/presentation/window/swapchain.cpp', 1000, 'Common::LockGuard render_lock(m_impl->renderer.GetMutex());', 'if (present_wait_t0 != 0) {'),
    ('f2307b02', 'src/graphics/presentation/window/swapchain.cpp', 1050, 'if (!preparing) m_impl->window.UpdateTitle();', 'm_impl->frames.Release(&frame, true);'),
    ('f2307b02', 'src/graphics/presentation/window/window.cpp', 1523, 'const bool title_async  = !loop_running || Common::Gates::Value(Common::Gates::Knob::TitleAsync) != 0;', 'const auto title_t0    = Common::FrameStats::NowNs();'),
    ('f2307b02', 'src/graphics/presentation/window/window.cpp', 1545, 'RunOnMainThread([this, text = std::move(text)] { SDL_SetWindowTitle(window, text.c_str()); });', '}'),
    ('f2307b02', 'src/graphics/presentation/window/window.cpp', 826, 'b32.BeginWReg(Common::DiagB32::Wait::MainTask, &main_task_done,', '}'),
    ('f2307b02', 'src/common/gates.cpp', 409, '{"KYTY_TITLE_ASYNC", "titleasync", 1, 1},', ''),
    ('f2307b02', 'src/common/hostException.cpp', 176, 'b32.BeginH(Common::DiagB32::Call::Fault);', '}'),
    ('f2307b02', 'src/graphics/host_gpu/renderer/commandRecorder.h', 324, 'alignas(64) std::mutex            m_mutex;', 'std::condition_variable           m_progress;'),
    ('f2307b02', 'CMakeLists.txt', 156, '-D SHADER_CACHE_EXTRA_FILES=', ''),
    ('b487a9cc', 'docs/track-f/f20j4.md', 47, '`Common::Mutex` без `H`; выборки слота B каждую 1 мс', '`W` 0; без `H` — `W:emu_mutex` 47;'),
    ('b487a9cc', 'docs/track-f/f20j4.md', 67, 'полной арене или смене гейта `recordthread`; **`W:main_task`**', 'только при `KYTY_REC`'),
    ('51c00063', 'docs/ROADMAP.md', 23468, '(в) **Решения по RC (решение лида).**', '(г) **Счёт У1.**'),
    ('51c00063', 'docs/ROADMAP.md', 23471, '(е) **F20k4 (Red Team) — ревью дельты', '(ж) **F20l2 `HPP-648` — поправка п. 574(е):**'),
    ('51c00063', 'docs/ROADMAP.md', 23480, '(в) **Оговорки и долги (п. 324(и)(5)):**', '(г) **Дальше:**'),
]

cache = {}
def lines(commit, path):
    k = (commit, path)
    if k not in cache:
        out = subprocess.run([GIT, '-C', REPO, 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout
        cache[k] = out.decode('utf-8').replace('\r', '').split('\n')
    return cache[k]

mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
ok = True
for commit, path, line, anchor, plus1 in REFS:
    L = lines(commit, path)
    hits = [i + 1 for i, l in enumerate(L) if l.strip().startswith(anchor) and (plus1 == '' or (i + 1 < len(L) and L[i + 1].strip().startswith(plus1)))]
    if mode == 'find':
        print(f'{commit}:{path}:{hits}\t{anchor[:60]}')
        continue
    if line == 0:
        good = len(hits) == 1
        shown = hits
    else:
        good = line in hits and len(anchor) <= 150
        shown = line
    print(f'{"ok " if good else "BAD"} {commit}:{path}:{shown}')
    ok &= good
print(f'refs {len(REFS)}')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
