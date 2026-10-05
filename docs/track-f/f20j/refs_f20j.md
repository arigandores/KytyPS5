| ссылка | якорь (строка) | +1 |
|---|---|---|
| `fe0bf0a0:docs/ROADMAP.md:23217` | «550. **Звено F20i трека F (`HPP-628`, лид; приёмка F20g `HPP-626` и отзыва F20h `HPP-627`): F20g ПРИНЯТ — член (1) по букве п. 549(д)(1): «кто держал » | «(а) **Приёмка строкой. F20g ✓** — перепись (1) на 7 кадрах против медианы 20 соседей (`ana.txt`, `fields7.txt`), контроль Б5 (подпись Б5 записана: `cp» |
| `fe0bf0a0:docs/ROADMAP.md:23220` | «(в) **Разрешения RC (обязательны для F20j; проект F20g §2 читается с ними).** RC1 — сэмплер при `=1` пишет всегда в кольцо истории (на слот ≥ 2 с выбо» | «(г) **Правило чтения (до данных).** (1) **Кадр в счёте:** `dt_us` ≥ 100 мс, начало на ≥ 10 с сцены удержания, ридер F20c не приписал его Б5 / Б33 / Б1» |
| `fe0bf0a0:docs/ROADMAP.md:23221` | «(г) **Правило чтения (до данных).** (1) **Кадр в счёте:** `dt_us` ≥ 100 мс, начало на ≥ 10 с сцены удержания, ридер F20c не приписал его Б5 / Б33 / Б1» | «(д) **Контроли (F20l, теги до серии; чтение — F20m).** (1) `b32_z0` — `KYTY_DIAG_B32=0`: строк `DiagB32` 0, строки `mode=1` нет. (2) ПК-B `b32_pp` — `» |
| `fe0bf0a0:docs/ROADMAP.md:23225` | «(з) **Звенья (стадия review лида у звена исполнителя).** **F20j** (Emu Engineer, `todo`): код `KYTY_DIAG_B32` (M1–M5 F20g §2 с разрешениями (в)) и сте» | «(и) **Долги F20g / F20h (п. 324(и)(5)).** (1) F20g §9(3): `cat` замка и `ls` черновика командой под чужим замком `k_05` S15b — нарушение буквы общего » |
| `86abd902:docs/track-f/f20g.md:169` | «### 2.3 Сайты (`302347b4` — исходник установленного FS8; Emu Engineer вправе вернуть проект, если сайт не существует)» | «пустая строка» |
| `4bab4d66:docs/track-f/f20h-review.md:41` | «## 2. Требуемые изменения» | «пустая строка» |
| `302347b4:src/common/frameStats.cpp:618` | «uint64_t ThreadCpuNs(ThreadRole role) {» | «#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS» |
| `302347b4:src/common/threads.cpp:66` | «nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);» | «if (timer == nullptr) {» |
| `0df13a66:src/common/diagB32.cpp:31` | «bool g_on            = false;» | «bool g_test_on       = false;» |
| `0df13a66:src/common/diagB32.cpp:80` | «uint16_t Classify(uint32_t mark, uint64_t cpu_ns, uint64_t interval_ns, bool kq, uint32_t kthread_state,» | «uint32_t kwait_reason) {» |
| `0df13a66:src/common/diagB32.cpp:155` | «GapStats Gaps(const uint64_t* t, size_t n, uint64_t win_start, uint64_t win_end, uint64_t period_ns) {» | «GapStats g;» |
| `0df13a66:src/common/diagB32.cpp:180` | «void WindowSamples(const uint64_t* t, const uint64_t* cost, const uint8_t* kq, uint64_t hpos, uint32_t hist,» | «uint64_t start, uint64_t end, uint64_t extra_ns, std::vector<uint64_t>* idx, uint64_t* instr_ns,» |
| `0df13a66:src/common/diagB32.cpp:210` | «std::string SafeName(const char* name) {» | «std::string out;» |
| `0df13a66:src/common/diagB32.cpp:226` | «int32_t Registry::Allocate(uint32_t os_tid, void* handle, const char* role, const char* name, int32_t gid) {» | «const auto idx = count.fetch_add(1, std::memory_order_acq_rel);» |
| `0df13a66:src/common/diagB32.cpp:243` | «void Registry::WriteMark(int32_t idx, uint32_t mark, uint64_t obj, uint64_t since, int32_t peer) {» | «auto&      s   = slots[idx];» |
| `0df13a66:src/common/diagB32.cpp:255` | «bool Registry::ReadMark(int32_t idx, MarkSnap* out) {» | «auto& s = slots[idx];» |
| `0df13a66:src/common/diagB32.cpp:278` | «void WaitRing::Push(const WaitRec& rec) {» | «const auto i = wpos.fetch_add(1, std::memory_order_acq_rel);» |
| `0df13a66:src/common/diagB32.cpp:294` | «void WaitRing::Drain(std::vector<WaitRec>* out, uint64_t* drop, uint64_t* torn) {» | «const auto w = wpos.load(std::memory_order_acquire);» |
| `0df13a66:src/common/diagB32.cpp:410` | «void MarkMandatory(Report* report) {» | «auto&      r       = *report;» |
| `0df13a66:src/common/diagB32.cpp:488` | «std::string Format(Report* report, Counters* counters) {» | «auto& r = *report;» |
| `0df13a66:src/common/diagB32.cpp:691` | «int32_t RegisterSelf(const char* role, const char* name, int32_t gid) {» | «#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS» |
| `0df13a66:src/common/diagB32.cpp:712` | «int32_t SelfSlot() {» | «if (t_slot1 != 0) {» |
| `0df13a66:src/common/diagB32.cpp:722` | «void RegisterRole(const char* role) {» | «if (g_reg == nullptr) {» |
| `0df13a66:src/common/diagB32.cpp:741` | «int32_t RegisterGuest(int32_t gid, const char* name) {» | «if (g_reg == nullptr) {» |
| `0df13a66:src/common/diagB32.cpp:757` | «void Unregister() {» | «if (g_reg != nullptr && t_slot1 > 0) {» |
| `0df13a66:src/common/diagB32.cpp:763` | «uint64_t PackSig() {» | «const auto slot1 = SelfSlot();» |
| `0df13a66:src/common/diagB32.cpp:779` | «void Mark::BeginH(Call call) {» | «const auto slot1 = SelfSlot();» |
| `0df13a66:src/common/diagB32.cpp:799` | «void Mark::BeginW(Wait kind, const void* obj, int32_t peer_slot1, uint64_t req_us) {» | «const auto slot1 = SelfSlot();» |
| `0df13a66:src/common/diagB32.cpp:819` | «void Mark::EndSlow(int32_t waker_slot1, bool timed_out) {» | «if (!m_active) {» |
| `0df13a66:src/common/diagB32.cpp:844` | «void NoteSubmit(uint64_t seq) {» | «const auto packed = PackSig();» |
| `0df13a66:src/common/diagB32.cpp:852` | «void NoteCurrentSubmission(uint64_t seq) {» | «g_cur_submit_seq.store(seq, std::memory_order_release);» |
| `0df13a66:src/common/diagB32.cpp:860` | «void NoteFlipRequest(uint64_t request_id, bool cpu_source) {» | «int32_t slot1 = 0;» |
| `0df13a66:src/common/diagB32.cpp:877` | «void OnFlip(uint64_t n, uint64_t request_id, uint64_t reserve_host_ns) {» | «const auto now   = FrameStats::NowNs();» |
| `0df13a66:src/common/diagB32.cpp:919` | «void TestArm() {» | «if (!g_test_on \|\| g_test_armed.exchange(true, std::memory_order_acq_rel)) {» |
| `0df13a66:src/common/diagB32.cpp:929` | «static void TestSleepNow(const char* mode) {» | «const auto fire = g_test_fire_ns.load(std::memory_order_acquire);» |
| `0df13a66:src/common/diagB32.cpp:1058` | «void Sampler::KernelQuery() {» | «m_kmap.clear();» |
| `0df13a66:src/common/diagB32.cpp:1109` | «void Sampler::Sample(uint64_t t0) {» | «const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;» |
| `0df13a66:src/common/diagB32.cpp:1153` | «void Sampler::M5Refresh(uint64_t now) {» | «HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);» |
| `0df13a66:src/common/diagB32.cpp:1206` | «void Sampler::M5Snapshot() {» | «for (auto& e: m_m5) {» |
| `0df13a66:src/common/diagB32.cpp:1222` | «void Sampler::M1Snapshot(uint64_t* proc_us, uint64_t* busy_us, uint64_t* idle_us) {» | «FILETIME idle {};» |
| `0df13a66:src/common/diagB32.cpp:1254` | «void Sampler::CloseWindow(uint64_t n, uint64_t flip_ns, uint64_t lat_us, int32_t flip_slot1, uint32_t src, bool snap,» | «uint64_t proc_us, uint64_t busy_us, uint64_t idle_us, uint64_t lag_us) {» |
| `0df13a66:src/common/diagB32.cpp:1390` | «void Sampler::ProcessFlips() {» | «const auto pub = g_flip_pub.load(std::memory_order_acquire);» |
| `0df13a66:src/common/diagB32.cpp:1434` | «void Sampler::Run() {» | «SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST);» |
| `0df13a66:src/common/diagB32.cpp:1458` | «HANDLE timer = CreateWaitableTimerExW(nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);» | «if (timer == nullptr) {» |
| `0df13a66:src/common/diagB32.cpp:1482` | «void Init() {» | «static bool done = false;» |
| `0df13a66:src/common/diagB32.cpp:1546` | «void LogHeader() {» | «if (g_config_invalid) {» |
| `0df13a66:src/emulator.cpp:205` | «Common::DiagB32::Init();» | «// Process-local test overrides: no cache files are removed or modified by the cold mode.» |
| `0df13a66:src/emulator.cpp:237` | «Common::DiagB32::LogHeader(); // Track F, F20j: "DiagB32: mode=1 ..." / "TestB32: config ..." once» | «std::string title_id;» |
| `0df13a66:src/common/frameStats.cpp:238` | «Common::DiagB32::RegisterRole(static_cast<size_t>(role) < 4 ? names[static_cast<size_t>(role)] : "emu");» | «}» |
| `0df13a66:src/common/frameStats.cpp:642` | «double CpuCyclesPerNs() {» | «#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS» |
| `0df13a66:src/kernel/pthread.cpp:488` | «std::atomic<int32_t>  b32_slot1 {0}; // DiagB32 slot + 1 of this thread» | «std::atomic<uint64_t> b32_waker {0}; // DiagB32::PackSig of the thread whose Signal/Broadcast advanced cond_sequence» |
| `0df13a66:src/kernel/pthread.cpp:578` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of this waiter» | «thread->b32_waker.store(Common::DiagB32::PackSig(), std::memory_order_relaxed);» |
| `0df13a66:src/kernel/pthread.cpp:1114` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the guest main thread's slot (registered as role Main)» | «g_pthread_self->b32_slot1.store(Common::DiagB32::RegisterGuest(g_pthread_self->unique_id, "MainThread"),» |
| `0df13a66:src/kernel/pthread.cpp:1388` | «if (Common::DiagB32::g_on && mutex->owner != nullptr && (timeout_us == nullptr \|\| *timeout_us > 0)) [[unlikely]] {» | «b32.BeginW(Common::DiagB32::Wait::Mutex, mutex, mutex->owner->b32_slot1.load(std::memory_order_relaxed),» |
| `0df13a66:src/kernel/pthread.cpp:1411` | «b32.EndWithPeer(true);» | «return ETIMEDOUT;» |
| `0df13a66:src/kernel/pthread.cpp:1429` | «b32.EndWithPeer(false);» | «mutex->owner = self;» |
| `0df13a66:src/kernel/pthread.cpp:2855` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (M2 cond): the waker of every waiter» | «thread->b32_waker.store(Common::DiagB32::PackSig(), std::memory_order_relaxed);» |
| `0df13a66:src/kernel/pthread.cpp:3012` | «b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, static_cast<uint64_t>(usec));» | «}» |
| `0df13a66:src/kernel/pthread.cpp:3110` | «b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, B32ReqUs(deadline));» | «}» |
| `0df13a66:src/kernel/pthread.cpp:3196` | «b32.BeginW(Common::DiagB32::Wait::Cond, cond_value, 0, 0);» | «}» |
| `0df13a66:src/kernel/pthread.cpp:3345` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j: the slot stops being sampled» | «Common::DiagB32::Unregister();» |
| `0df13a66:src/kernel/pthread.cpp:3413` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j (KYTY_DIAG_B32): the guest thread's slot, name and id» | «thread->b32_slot1.store(Common::DiagB32::RegisterGuest(thread->unique_id, thread->name.c_str()),» |
| `0df13a66:src/kernel/pthread.cpp:4224` | «b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, static_cast<uint64_t>(microseconds));» | «}» |
| `0df13a66:src/kernel/pthread.cpp:4240` | «b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, static_cast<uint64_t>(seconds) * 1000000ull);» | «}» |
| `0df13a66:src/kernel/pthread.cpp:4274` | «b32.BeginW(Common::DiagB32::Wait::Sleep, nullptr, 0, nanos / 1000u);» | «}» |
| `0df13a66:src/kernel/semaphore.cpp:233` | «b32.BeginW(Common::DiagB32::Wait::Sem, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));» | «}» |
| `0df13a66:src/kernel/semaphore.cpp:429` | «b32.BeginW(Common::DiagB32::Wait::PSem, this, 0, timed_wait ? static_cast<uint64_t>(*micros) : 0);» | «}» |
| `0df13a66:src/kernel/semaphore.cpp:75` | «std::atomic<uint64_t> m_b32_sig {0};» | «};» |
| `0df13a66:src/kernel/semaphore.cpp:520` | «std::atomic<uint64_t> m_b32_sig {0};» | «};» |
| `0df13a66:src/kernel/eventFlag.cpp:144` | «b32.BeginW(Common::DiagB32::Wait::Evf, this, 0, infinitely ? 0 : static_cast<uint64_t>(micros));» | «}» |
| `0df13a66:src/kernel/eventFlag.cpp:53` | «std::atomic<uint64_t> m_b32_sig {0};» | «};» |
| `0df13a66:src/kernel/eventQueue.cpp:185` | «b32.BeginW(Common::DiagB32::Wait::Eq, this, 0, micros);» | «}» |
| `0df13a66:src/kernel/eventQueue.cpp:70` | «std::atomic<uint64_t> m_b32_sig {0};» | «};» |
| `0df13a66:src/graphics/presentation/videoOut.cpp:548` | «Common::DiagB32::NoteFlipRequest(request_id, source == FlipRequestSource::Cpu);» | «}» |
| `0df13a66:src/graphics/presentation/videoOut.cpp:1228` | «if (Common::DiagB32::g_present_site) [[unlikely]] {» | «if (Common::DiagB32::g_on) {» |
| `0df13a66:src/graphics/presentation/videoOut.cpp:1253` | «Common::DiagB32::OnFlip(r.cfg->flip_status.count, r.id, r.reserve_host_ns);» | «}» |
| `0df13a66:src/graphics/presentation/window/swapchain.cpp:659` | «b32.BeginH(Common::DiagB32::Call::Acquire);» | «}» |
| `0df13a66:src/graphics/presentation/window/window.cpp:1308` | «Common::DiagB32::TestArm();» | «}» |
| `0df13a66:src/graphics/host_gpu/renderer/commandScheduler.cpp:930` | «b32_drain.BeginH(Common::DiagB32::Call::Drain);» | «}» |
| `0df13a66:src/graphics/host_gpu/renderer/commandScheduler.cpp:946` | «b32_q.BeginH(Common::DiagB32::Call::QLock);» | «}» |
| `0df13a66:src/graphics/host_gpu/renderer/commandScheduler.cpp:971` | «b32_q.BeginH(Common::DiagB32::Call::QSubmit);» | «}» |
| `0df13a66:src/graphics/host_gpu/renderer/masterSemaphore.cpp:102` | «b32.BeginH(Common::DiagB32::Call::SemWait);» | «}» |
| `0df13a66:src/common/platform/sysWindowsVirtual.cpp:324` | «b32.BeginH(Common::DiagB32::Call::Protect);» | «}» |
| `0df13a66:src/common/hostException.cpp:176` | «b32.BeginH(Common::DiagB32::Call::Fault);» | «}» |
| `0df13a66:src/graphics/guest_gpu/graphicsRun.cpp:676` | «Common::DiagB32::NoteSubmit(submission.bf.seq);» | «}» |
| `0df13a66:src/graphics/guest_gpu/graphicsRun.cpp:705` | «Common::DiagB32::TestGpuSleepPoint();» | «}» |
| `0df13a66:src/graphics/guest_gpu/graphicsRun.cpp:723` | «b32.BeginW(Common::DiagB32::Wait::GpuIdle, gpu, 0, 0);» | «}» |
| `0df13a66:src/graphics/guest_gpu/graphicsRun.cpp:765` | «b32.BeginW(Common::DiagB32::Wait::GpuRegmem, gpu, 0, 100000);» | «}» |
| `0df13a66:src/graphics/guest_gpu/graphicsRun.cpp:790` | «Common::DiagB32::NoteCurrentSubmission(submission.bf.seq);» | «}» |
