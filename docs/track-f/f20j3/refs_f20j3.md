| ссылка | якорь (строка) | +1 |
|---|---|---|
| `ea79e31c:docs/ROADMAP.md:23423` | «574. **Звено F20m трека F (`HPP-632`, лид): чтение контролей F20l по п. 550(д) — `b32_z0` ✓, ПК-B ✓, ПК-C ✗ (цепочка от держателя не доходит до GuestG» | «(а) **Данные лида [c]** (`C:/kyty/f287/lead/p574/lead_f20m.py` — свой разбор строк `DiagB32:` и `DiagB32-t:` кадров стендов в логах F20l `log_b32_pp.t» |
| `ea79e31c:docs/ROADMAP.md:23427` | «(г) **Правка F20j3 — состав (обязателен; детали реализации — исполнитель, ревью — F20k3).** (1) **Метки ожиданий эмулятора.** Опись скриптом всех блок» | «(д) **Поправка правила чтения п. 550(г)(2)(iv) — до кода и до данных повтора (решение лида).** Шаг по `W:<род>` ≥ 50 % — к будящему записи `-w` с наиб» |
| `ea79e31c:docs/ROADMAP.md:23428` | «(д) **Поправка правила чтения п. 550(г)(2)(iv) — до кода и до данных повтора (решение лида).** Шаг по `W:<род>` ≥ 50 % — к будящему записи `-w` с наиб» | «(е) **Повтор контролей — F20l2 (Harness Engineer; замок, F20 последним в очереди — п. 462(г), 567).** Бинарь — тестовый F20j3 по sha256 после вердикта» |
| `9db7938b:src/common/diagB32.h:63` | «EmuMutex, GpuWait, GpuCmd, FlipSlot, FlipDone, FlipCancel, FlipReq, VoPace, Relay, FramePool, RecWait, RecIdle,» | «ASubIdle, ASubDrain, OpsWait, OpsIdle, PipeWait, PCopy, PmDrain, VmaFlush, RecQueue, MainTask, MainIdle, Spin, Av,» |
| `9db7938b:src/common/diagB32.h:66` | «Vblank, Once, Join, Addr, Aio, Fiber, Audio, Ult, Net, Rwlock, Count» | «};» |
| `9db7938b:src/common/diagB32.h:71` | «[[nodiscard]] constexpr bool IsEmuWait(uint8_t kind) {» | «return kind >= kFirstEmuWait && kind < kFirstGuestHleWait;» |
| `9db7938b:src/common/diagB32.h:75` | «[[nodiscard]] constexpr bool MutexLike(uint8_t kind) {» | «return kind == static_cast<uint8_t>(Wait::Mutex) \|\| kind == static_cast<uint8_t>(Wait::EmuMutex) \|\|» |
| `9db7938b:src/common/diagB32.h:131` | «void BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us);» | «// Ends the mark (restores the previous one). For a W mark a wait record is pushed if it lasted >= 10 ms, with the» |
| `9db7938b:src/common/diagB32.h:197` | «class TrackedMutex {» | «public:» |
| `9db7938b:src/common/diagB32.cpp:1047` | «void Mark::BeginWReg(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {» | «const auto slot1 = SelfSlotIfRegistered();» |
| `9db7938b:src/common/threads.cpp:337` | «void Mutex::LockB32() {» | «#ifdef KYTY_WIN_CS» |
| `9db7938b:src/common/threads.cpp:344` | «b32.BeginWReg(DiagB32::Wait::EmuMutex, this, DiagB32::SlotOfOsTid(owner), 0);» | «EnterCriticalSection(&m_mutex->m_cs);» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:697` | «b32.BeginWReg(Common::DiagB32::Wait::GpuWait, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);» | «}» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:703` | «b32.End(m_idle.B32Waker(b32.SinceNs()), false);» | «}» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:194` | «b32.BeginWReg(Common::DiagB32::Wait::GpuCmd, &done, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), 0);» | «}» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:2676` | «b32.BeginWReg(Common::DiagB32::Wait::Relay, relay, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Relay), 0);» | «}» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:722` | «Common::DiagB32::TestGpuSleepPoint();» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:1147` | «b32.BeginWReg(Common::DiagB32::Wait::FlipSlot, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:1171` | «b32.BeginWReg(Common::DiagB32::Wait::FlipDone, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:949` | «b32.BeginWReg(Common::DiagB32::Wait::FlipCancel, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:1190` | «b32.BeginWReg(Common::DiagB32::Wait::FlipReq, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Gpu), micros);» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:4109` | «b32.BeginWReg(Common::DiagB32::Wait::Vblank, ctx, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);» | «}» |
| `9db7938b:src/graphics/presentation/videoOut.cpp:833` | «b32.BeginWReg(Common::DiagB32::Wait::VoPace, this, 0, remaining_us);» | «}» |
| `9db7938b:src/graphics/presentation/window/swapchain.cpp:117` | «b32.BeginWReg(Common::DiagB32::Wait::FramePool, this, Common::DiagB32::PeerSlot(Common::DiagB32::Peer::Present), 0);» | «}» |
| `9db7938b:src/graphics/host_gpu/renderer/commandScheduler.cpp:671` | «Common::DiagB32::RegisterRole("POps");» | «}» |
| `9db7938b:src/common/diagB32.h:97` | «enum class Peer : uint8_t { Present = 0, Gpu, ASubmit, POps, Relay, Main, Record, Count };» | «[[nodiscard]] int32_t PeerSlot(Peer peer);            // slot + 1 of the role thread, 0 - not registered (yet)» |
| `9db7938b:src/common/diagB32.h:147` | «void EndSig(const void* obj, bool timed_out = false) {» | «if (m_active) {» |
| `9db7938b:src/common/diagB32.h:388` | «int32_t  peer1    = 0; // F20j3 (item 574(g)(2), (d)): the mark's peer, slot + 1, 0 = none» | «uint8_t  kind     = 0;» |
| `9db7938b:src/common/diagB32.cpp:983` | «void NoteSignalSlow(const void* obj) {» | «g_sigtab[SigBucket(obj)].store((PackSigIfRegistered() & ((uint64_t {1} << 52u) - 1u)) \| (SigTag(obj) << 52u),» |
| `9db7938b:src/common/diagB32.cpp:1087` | «rec.peer1     = m_peer; // F20j3 (item 574(g)(2))» | «rec.kind      = static_cast<uint8_t>(m_mark & 0xffu);» |
| `9db7938b:src/common/diagB32.cpp:1741` | «w.waker1   = MutexLike(static_cast<uint8_t>(m_last_mark[i].mark & 0xffu)) ? m_last_mark[i].peer : 0;» | «w.peer1    = m_last_mark[i].peer;» |
| `9db7938b:src/common/diagB32.cpp:658` | «" waker_tid=%d req_us=%llu to=%u open=%u peer=%d peer_tid=%d\n",» | «n, SlotIndex(w.slot1), GidOf(r, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),» |
| `9db7938b:src/common/threads.cpp:446` | «int32_t CondVar::B32Waker(uint64_t since_ns) const {» | «return DiagB32::SigWaker(m_cond_var->b32_sig.load(std::memory_order_relaxed), since_ns);» |
| `9db7938b:src/libs/agc.cpp:1567` | «int KYTY_SYSV_ABI AgcSuspendPoint() {» | «PRINT_NAME();» |
| `9db7938b:src/graphics/guest_gpu/graphicsRun.cpp:333` | «void GuestGpu::Done() {» | «GpuMutexLock lock(m_submission_mutex);» |
| `9db7938b:src/common/threads.cpp:405` | «if (func(&m_cond_var->m_cv, &mutex->m_mutex->m_cs, 10) == 0 &&» | «GetLastError() == ERROR_TIMEOUT) {» |
| `9db7938b:src/kernel/pthread.cpp:1186` | «Common::CondVar::SetWaitPollCallback(KernelDispatchPendingSignalForCurrentThread);» | «пустая строка» |
| `9db7938b:src/common/diagB32.h:522` | «class AsyncRefresh {» | «public:» |
| `9db7938b:src/common/diagB32.cpp:1467` | «void Sampler::M5RefreshWork(void* user) {» | «auto&  m    = *static_cast<M5Shared*>(user);» |
| `9db7938b:src/common/diagB32.cpp:1533` | «void Sampler::M5Adopt() {» | «std::unique_lock lock(m_m5s.mutex, std::try_to_lock);» |
| `9db7938b:src/common/diagB32.cpp:1804` | «const uint64_t m5r = m_m5r.TakeWorkNs();» | «M5Adopt();» |
| `9db7938b:src/common/diagB32.cpp:1836` | «m_win_extra_ns += FrameStats::NowNs() - t0 + m5r;» | «m_win_m5r_ns += m5r;» |
| `9db7938b:src/common/diagB32.cpp:1861` | «m_m5r.Start(&Sampler::M5RefreshWork, &m_m5s, 1000000000ull);» | «if (m_ntq != nullptr) {» |
| `9db7938b:src/common/diagB32.h:459` | «uint64_t ring_hold    = 0;» | «// F20j2 (item 552(v)(3), RC3 of F20k): the zero invariants at the previous window close; Format prints» |
| `9db7938b:src/common/diagB32.cpp:1812` | «g_ring->Drain(&m_ring_tmp, &m_c.ring_drop, &m_ring_torn, &m_ring_hold);» | «for (auto& w: m_ring_tmp) {» |
| `9db7938b:src/common/diagB32.cpp:678` | «" ring_hold=%llu ring_hold_w=%llu\n",» | «n, static_cast<unsigned long long>(counters->slots), static_cast<unsigned long long>(counters->slot_full),» |
| `9db7938b:src/common/threads.cpp:323` | «if (DiagB32::g_on) [[unlikely]] { // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, item 574(g)(1)): one test at =0» | «LockB32();» |
| `9db7938b:tests/DiagB32Tests.cpp:813` | «static void TestKinds() {» | «Case("F20j3 wait kinds: names unique, older numbers kept, EMU_WAIT / guest HLE partition, mutex-like");» |
| `9db7938b:tests/DiagB32Tests.cpp:837` | «static void TestRingHold() {» | «Case("F20j3 Z1: ring_hold - the positions a drain left at an unfinished write; -x ring_hold / ring_hold_w");» |
| `9db7938b:tests/DiagB32Tests.cpp:872` | «static void TestPeerFields() {» | «Case("F20j3 (2), (d): the -w line carries the record's peer; the peer's -t line is mandatory");» |
| `9db7938b:tests/DiagB32Tests.cpp:931` | «static void TestM5Async() {» | «Case("F20j3 (4): an 80 ms M5 refresh off the sampler thread makes no gap of samples (model; control - inline)");» |
| `9db7938b:tests/DiagB32Tests.cpp:961` | «static void TestWaitLoopRuntime() {» | «Case("F20j3 (3): a wait loop with short wakeups under one mark - W >= 50 % of samples, one -w record, waker, peer");» |
| `9db7938b:tests/DiagB32Tests.cpp:1059` | «static void TestEmuMutexRuntime() {» | «Case("F20j3 (1): contended Common::Mutex and TrackedMutex - W:emu_mutex, waker and peer = the owner");» |
| `9db7938b:tests/DiagB32Tests.cpp:505` | «CHECK(text.find(" gap3p=2 ring_hold=0 ring_hold_w=0\n") != std::string::npos);» | «}» |
