| ссылка | якорь (строка) | +1 |
|---|---|---|
| `de144412:docs/ROADMAP.md:23465` | «581. **Звено F20k3 трека F (`HPP-647`, лид): F20k3 ПРИНЯТ — отзыв `PASS_WITH_FIXES`, RC1–RC4 ПОДТВЕРЖДЕНЫ кодом лида и ИСПРАВЛЯЮТСЯ КОДОМ (RC4 — кодом» | «(а) **Приёмка строкой (правило 24):** карта ссылок ✓ (28 из 28 `ALL OK`, `refs_f20k3.txt`); инвентарь ✓ (§«Правило 24» отзыва — скрипты и выводы в `do» |
| `de144412:docs/ROADMAP.md:23468` | «(в) **Решения по RC (решение лида).** (1) **RC1 — кодом по предложению отзыва:** метка `W:rec_wait` в `CommandRecorder::Reserve` — на весь цикл повтор» | «(г) **Счёт У1.** Правка F20j4 — правка по ревью F20k3, в счёт У1 п. 550(ж) не идёт (как F20j2 — п. 552, 574(в)(1)); повторный провал У1 читается на по» |
| `de144412:docs/ROADMAP.md:23470` | «(д) **F20j4 (Emu Engineer) — состав (обязателен):** RC1–RC5 по (в)(1)–(5) с тестами; `diag_b32_tests` — прежние 21 случай и новые `ALL OK`; `shader_cf» | «(е) **F20k4 (Red Team) — ревью дельты `9db7938b..<F20j4>`:** RC1–RC5 закрыты по (в) кодом и тестами; охват цикла — своим `rt_loopmark.py` на новом код» |
| `9db7938b:src/graphics/host_gpu/renderer/commandRecorder.cpp:222` | «// Track F, F20j3 (KYTY_DIAG_B32 W:rec_wait, item 574(g)(1)): the producer waits for the record thread.» | «Common::DiagB32::Mark b32;» |
| `f2307b02:src/graphics/host_gpu/renderer/commandRecorder.cpp:194` | «// Track F, F20j4 (KYTY_DIAG_B32 W:rec_wait, item 581(v)(1), RC1 of F20k3): one mark over the whole retry loop - begun» | «// at the first pass that finds the arena full, ended before the return (as Drain); the WaitSlice waits and the work» |
| `f2307b02:src/graphics/host_gpu/renderer/commandRecorder.cpp:227` | «if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {» | «b32.BeginWReg(Common::DiagB32::Wait::RecWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Record), 0);» |
| `f2307b02:src/graphics/host_gpu/renderer/commandRecorder.cpp:262` | «b32.EndSig(&m_progress); // F20j4 (RC1): the end of the whole retry loop (one test of the flag at =0)» | «return m_data.get() + index;» |
| `9db7938b:src/common/diagB32.h:217` | «void unlock() { m_m.unlock(); }» | «void lock_shared() {» |
| `f2307b02:src/common/diagB32.h:239` | «void unlock() {» | «if (g_on) [[unlikely]] {» |
| `f2307b02:src/common/diagB32.h:273` | «void TakeOwner() {» | «if (m_depth++ == 0) {» |
| `f2307b02:src/common/diagB32.h:278` | «void ReleaseOwner() {» | «if (m_depth > 1) {» |
| `f2307b02:src/common/diagB32.cpp:1109` | «m_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself» | «m_req_us     = req_us;» |
| `f2307b02:src/common/diagB32.cpp:1129` | «m_peer       = peer_slot1 == slot1 ? 0 : peer_slot1; // F20j4 (RC2 of F20k3): never the thread itself» | «m_req_us     = req_us;» |
| `9db7938b:src/common/diagB32.cpp:1804` | «const uint64_t m5r = m_m5r.TakeWorkNs();» | «M5Adopt();» |
| `f2307b02:src/common/diagB32.h:611` | «class M5Charge {» | «public:» |
| `f2307b02:src/common/diagB32.cpp:753` | «PushRun(t0, t1);» | «m_cur_begin.store(0, std::memory_order_release);» |
| `f2307b02:src/common/diagB32.cpp:795` | «void AsyncRefresh::TakeRuns(std::vector<Run>* out) {» | «const auto w = m_wpos.load(std::memory_order_acquire);» |
| `f2307b02:src/common/diagB32.cpp:827` | «uint64_t M5Charge::Window(uint64_t start, uint64_t end) const {» | «uint64_t sum = 0;» |
| `f2307b02:src/common/diagB32.cpp:1701` | «const uint64_t m5r   = m_m5c.Window(start, flip_ns);» | «const uint64_t extra = m_win_extra_ns + print_ns + m5r; // F20j2 RC6: the report print inside this window» |
| `f2307b02:src/common/diagB32.cpp:1889` | «m_m5c.Add(m_m5_runs, m5_cur);» | «M5Adopt();» |
| `f2307b02:src/common/diagB32.cpp:1922` | «m_m5c.Prune(m_win_start);» | «}» |
| `9db7938b:src/common/threads.cpp:344` | «b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);» | «EnterCriticalSection(&m_mutex->m_cs);» |
| `f2307b02:src/common/diagB32.cpp:1136` | «void Mark::BeginWLock(Wait kind, const void* obj, int32_t peer_slot1) {» | «const auto slot1 = SelfSlotIfRegistered();» |
| `f2307b02:src/common/threads.cpp:347` | «b32.BeginWLock(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner));» | «EnterCriticalSection(&m_mutex->m_cs);» |
| `f2307b02:src/common/diagB32.h:251` | «b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));» | «m_m.lock_shared();» |
| `f2307b02:src/common/diagB32.h:265` | «b32.BeginWLock(K, this, m_owner.load(std::memory_order_relaxed));» | «m_m.lock();» |
| `f2307b02:src/graphics/host_gpu/renderer/commandScheduler.cpp:996` | «b32_drain.BeginH(Common::DiagB32::Call::Drain);» | «}» |
| `f2307b02:src/graphics/host_gpu/renderer/commandScheduler.cpp:230` | «AsyncSubmitter::Get().Drain();» | «}» |
| `f2307b02:src/graphics/presentation/videoOut.cpp:1269` | «b32.BeginH(Common::DiagB32::Call::Present);» | «}» |
| `f2307b02:src/graphics/presentation/window/swapchain.cpp:642` | «m_window.RunOnMainThread([this] { m_window.RecreateSurface(); });» | «#else» |
| `f2307b02:src/graphics/presentation/window/swapchain.cpp:668` | «b32.BeginH(Common::DiagB32::Call::Acquire);» | «}» |
| `f2307b02:src/common/hostException.cpp:176` | «b32.BeginH(Common::DiagB32::Call::Fault);» | «}» |
| `f2307b02:src/common/platform/sysWindowsVirtual.cpp:324` | «b32.BeginH(Common::DiagB32::Call::Protect);» | «}» |
| `f2307b02:src/graphics/host_gpu/renderer/masterSemaphore.cpp:102` | «b32.BeginH(Common::DiagB32::Call::SemWait);» | «}» |
| `9db7938b:src/common/threads.cpp:257` | «b32.BeginWReg(DiagB32::Wait::Join, this, 0, 0);» | «}» |
| `f2307b02:src/common/diagB32.h:72` | «EmuJoin, Count» | «};» |
| `f2307b02:src/common/diagB32.h:81` | «[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {» | «return (kind >= kFirstEmuWait && kind < kFirstGuestHleWait) \|\| kind == static_cast<uint8_t>(Wait::Vblank) \|\|» |
| `f2307b02:src/common/threads.cpp:258` | «b32.BeginWReg(DiagB32::Wait::EmuJoin, this, 0, 0);» | «}» |
| `f2307b02:src/kernel/pthread.cpp:3564` | «b32.BeginWReg(Common::DiagB32::Wait::Join, thread, thread->b32_slot1.load(std::memory_order_relaxed), 0);» | «}» |
| `f2307b02:tests/DiagB32Tests.cpp:849` | «CHECK(n_emu == 25 + 5);» | «CHECK(!IsEmuWait(static_cast<uint8_t>(Wait::Cond)) && !IsEmuWait(static_cast<uint8_t>(Wait::Join)));» |
| `f2307b02:tests/DiagB32Tests.cpp:1139` | «static void TestM5Charge() {» | «Case("F20j4 (3), RC3 of F20k3: the M5 refresh time is charged to the window it ran in (model; the run ring)");» |
| `f2307b02:tests/DiagB32Tests.cpp:1219` | «static void TestPeerSelfRuntime() {» | «Case("F20j4 (2), RC2 of F20k3: a writer waiting for two readers - peer 0; an own-slot peer is stored as 0");» |
| `f2307b02:tests/DiagB32Tests.cpp:1282` | «static void TestLockUnderHRuntime() {» | «Case("F20j4 (4), RC4 of F20k3: a contended lock inside H:qlock / H:present keeps the H mark; without H - W:emu_mutex");» |
| `4371ff4b:src/common/diagB32.h:611` | «class M5Charge {» | «public:» |
| `4371ff4b:src/graphics/host_gpu/renderer/commandRecorder.cpp:262` | «b32.EndSig(&m_progress); // F20j4 (RC1): the end of the whole retry loop (one test of the flag at =0)» | «return m_data.get() + index;» |
