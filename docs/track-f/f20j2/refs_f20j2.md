| ссылка | якорь (строка) | +1 |
|---|---|---|
| `aaf4504e:docs/ROADMAP.md:23237` | «552. **Звено F20k трека F (`HPP-630`, Red Team; приёмка лида на стадии review): F20k ПРИНЯТ — отзыв `PASS_WITH_FIXES`, RC1–RC7 приняты все, ни один не» | «(а) **Приёмка строкой. F20k ✓** — ответы на передачу п. 551(г) 5 из 5 (§1 отзыва); RC1–RC15 п. 550(в) — таблица §3 с местом по каждому (RC7 — частично» |
| `aaf4504e:docs/ROADMAP.md:23240` | «(в) **Разрешения RC1–RC7 F20k (обязательны для F20j2; п. 550(в) и п. 551(б)–(в) читаются с ними).** (1) **RC1 — поправка разрешения RC3 п. 550(в):** о» | «(г) **Поправка У2 и остановки серии п. 550(е)(2), (ж) — до данных.** `K_I` — удержания хотя бы с одним кадром, проходящим (г)(1) п. 550 без условия `d» |
| `aaf4504e:docs/ROADMAP.md:23242` | «(д) **Звенья (стадия review лида у звена исполнителя).** **F20j2** (Emu Engineer, `todo`): код (в)(1)–(7) в `main` KytyPS5; `=0` — путь байт в байт, о» | «(е) **Долги F20k (п. 324(и)(5)).** (1) Замечание §1(1) — AV чужих потоков регистрирует их и тратит слоты — видно по `slots=` / `slot_full_w`; паркуетс» |
| `d63d7feb:docs/track-f/f20k-review.md:63` | «## 2. Требуемые изменения» | «пустая строка» |
| `61b410bf:src/common/diagB32.h:43` | «constexpr uint64_t kKqBudgetDiv   = 10;» | «constexpr uint64_t kKqNearNs      = 60000000;» |
| `61b410bf:src/common/diagB32.h:194` | «struct KqSchedule {» | «uint64_t win_start  = 0; // the previous flip (0 - no flip yet: no query)» |
| `61b410bf:src/common/diagB32.cpp:180` | «bool KqSchedule::Due(uint64_t now_ns) const {» | «if (win_start == 0 \|\| now_ns < win_start + kKernelAfterNs) {» |
| `61b410bf:src/common/diagB32.cpp:184` | «return (win_kq_ns + last_kq_ns) * kKqBudgetDiv <= now_ns - win_start;» | «}» |
| `61b410bf:src/common/diagB32.cpp:197` | «uint64_t NextBegin(uint64_t begin_ns, uint64_t now_ns) {» | «return std::max(begin_ns + kPeriodNs, now_ns);» |
| `61b410bf:src/common/diagB32.cpp:201` | «void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,» | «int32_t* out) {» |
| `61b410bf:src/common/diagB32.cpp:1207` | «if (m_kq_ok && m_sched.Due(begin)) {» | «KernelQuery();» |
| `61b410bf:src/common/diagB32.cpp:1391` | «m_sched.NewWindow(flip_ns, carried);» | «}» |
| `61b410bf:src/common/diagB32.cpp:1430` | «Core::NearestSnapshot(times.data(), wkq.data(), wkqt.data(), idx.size(), kKqNearNs, nearest.data());» | «Core::Report r;» |
| `61b410bf:src/common/diagB32.cpp:1459` | «if (Core::CodeState(code) == State::S && wkq[j] == 0 && nearest[j] >= 0) {» | «const auto kc = m_kcodes[static_cast<size_t>(i) * kHist + idx[static_cast<size_t>(nearest[j])] % kHist];» |
| `61b410bf:src/common/diagB32.cpp:1640` | «// A flip published together with the timer is taken first, so the schedule sees the current window start.» | «for (;;) {» |
| `61b410bf:src/common/diagB32.cpp:1647` | «const auto next = Core::NextBegin(begin, now);» | «if (next >= now + 100) {» |
| `61b410bf:src/common/diagB32.cpp:580` | «" kq_n=%u kq_us=%llu m5r_us=%llu"» | «" proc_us=%llu sys_busy_us=%llu sys_idle_us=%llu other_us=%lld ncpu=%u snap_ok=%u snap_lag_us=%llu"» |
| `61b410bf:src/common/diagB32.cpp:1616` | «g_kq_first_us.store((FrameStats::NowNs() - q0) / 1000u, std::memory_order_relaxed); // F20j2: kq_us of mode=1» | «m_kq_ok = !m_kmap.empty();» |
| `61b410bf:tests/DiagB32Tests.cpp:579` | «static void TestSchedule() {» | «Case("F20j2 RC1: kernel query schedule (>= 40 ms, <= 10 % of the window, absolute period), item 552(v)(1)");» |
| `61b410bf:tests/DiagB32Tests.cpp:633` | «static void TestNearest() {» | «Case("F20j2: S split by the nearest snapshot of the same window <= 60 ms");» |
| `61b410bf:src/common/diagB32.cpp:1217` | «const uint64_t t0       = FrameStats::NowNs();» | «const uint64_t interval = m_last_t != 0 && t0 > m_last_t ? t0 - m_last_t : kPeriodNs;» |
| `61b410bf:src/common/diagB32.cpp:1258` | «m_kqt[pos]  = kq_t;» | «m_kqc[pos]  = kq_ns;» |
| `61b410bf:src/common/diagB32.cpp:1261` | «m_cost[pos] = FrameStats::NowNs() - begin; // RC9: the whole sample, the kernel query included» | «m_hpos++;» |
| `61b410bf:src/common/diagB32.cpp:653` | «"DiagB32-x: n=%llu slots=%llu slot_full=%llu slot_full_w=%llu torn=%llu torn_w=%llu ring_drop=%llu ring_drop_w=%llu"» | «" sgap_bad=%llu sgap_bad_w=%llu lines_cut=%llu lines_cut_w=%llu req_miss=%llu req_miss_w=%llu sub_miss=%llu"» |
| `61b410bf:src/common/diagB32.cpp:670` | «void Counters::Rebase() {» | «base.slot_full = slot_full;» |
| `61b410bf:src/common/diagB32.cpp:1366` | «void Sampler::RefreshCounters() {» | «m_c.slot_full = g_reg->slot_full.load(std::memory_order_relaxed);» |
| `61b410bf:src/common/diagB32.cpp:1394` | «RefreshCounters();» | «if (start == 0 \|\| flip_ns <= start) {» |
| `61b410bf:tests/DiagB32Tests.cpp:677` | «static void TestWindowDelta() {» | «Case("F20j2 RC3: zero invariants per window (_w) - an event in window k, a clean window k+1");» |
| `61b410bf:src/common/diagB32.cpp:326` | «uint64_t WaitRing::Reserve() {» | «return wpos.fetch_add(1, std::memory_order_acq_rel);» |
| `61b410bf:src/common/diagB32.cpp:355` | «if (s1 < want) {» | «// F20j2 (RC4): the write of this position has not finished - not started (an older lap's word) or in progress» |
| `61b410bf:src/common/diagB32.cpp:379` | «// Overwritten by a later lap before or while it was read: the record is lost (F20j2 RC4 - only this is torn).» | «(*torn)++;» |
| `61b410bf:tests/DiagB32Tests.cpp:711` | «static void TestDrainPreempted() {» | «Case("F20j2 RC4: drain with a writer preempted between Reserve and the final word");» |
| `61b410bf:src/graphics/host_gpu/renderer/commandScheduler.cpp:130` | «Common::DiagB32::RegisterRole("ASubmit");» | «}» |
| `61b410bf:src/graphics/host_gpu/renderer/commandScheduler.cpp:146` | «Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock / H:qsubmit, RC5 of F20k)» | «if (Common::DiagB32::g_on) [[unlikely]] {» |
| `61b410bf:src/graphics/host_gpu/renderer/commandScheduler.cpp:173` | «if (Common::DiagB32::g_on) [[unlikely]] { // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qsubmit, RC5 of F20k)» | «b32_q.BeginH(Common::DiagB32::Call::QSubmit);» |
| `61b410bf:src/graphics/presentation/window/swapchain.cpp:798` | «// Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k): nested in H:present - a sample shows the innermost mark,» | «// End restores H:present.» |
| `61b410bf:src/graphics/presentation/systemOverlay.cpp:1075` | «Common::DiagB32::Mark b32_q; // Track F, F20j2 (KYTY_DIAG_B32 M3 H:qlock, RC5 of F20k)» | «if (Common::DiagB32::g_on) [[unlikely]] {» |
| `61b410bf:src/common/diagB32.cpp:461` | «const bool asub = t.role == "ASubmit" &&» | «t.agg.h[static_cast<size_t>(Call::QLock)] + t.agg.h[static_cast<size_t>(Call::QSubmit)] > 0;» |
| `61b410bf:src/graphics/presentation/videoOut.cpp:1232` | «Common::DiagB32::TestPresentPoint();» | «}» |
| `61b410bf:src/graphics/presentation/videoOut.cpp:1234` | «m_presenter.Present(*r.frame);» | «b32.End(0, false);» |
| `61b410bf:tests/DiagB32Tests.cpp:756` | «static void TestASubmit() {» | «Case("F20j2 RC5: the async submitter's -t line is mandatory in a window with H:qlock / H:qsubmit");» |
| `61b410bf:src/common/diagB32.cpp:973` | «e.print_ns.store(g_print_prev_ns, std::memory_order_relaxed);» | «g_flip_pub.store(k + 1, std::memory_order_release);» |
| `61b410bf:src/common/diagB32.cpp:1001` | «g_print_prev_ns = print_ns;» | «}» |
| `61b410bf:src/common/diagB32.cpp:1376` | «const uint64_t extra = m_win_extra_ns + print_ns; // F20j2 RC6: the report print inside this window» | «const uint64_t m5r   = m_win_m5r_ns;» |
| `61b410bf:src/graphics/presentation/videoOut.cpp:1251` | «// reports the sampler has closed are printed here, under FlipQueue::m_mutex and VideoOutConfig::mutex (F20j2, RC6 of» | «// F20k: the print time goes into instr_us of the window open during the print).» |
| `61b410bf:src/common/diagB32.cpp:945` | «g_sub_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten» | «}» |
| `61b410bf:src/common/diagB32.cpp:963` | «g_req_miss.fetch_add(1, std::memory_order_relaxed); // F20j2 RC7: the entry was overwritten» | «}» |
| `61b410bf:src/common/diagB32.cpp:1560` | «m5r = FrameStats::NowNs() - t0; // F20j2 (item 552(e)(3)): the refresh's share of the boundary work» | «}» |
| `0df13a66:src/graphics/presentation/window/swapchain.cpp:798` | «Common::LockGuard lock(m_window.graphic_ctx.queue_mutex);» | «result = m_window.graphic_ctx.queue.presentKHR(&present);» |
| `0df13a66:src/graphics/host_gpu/renderer/commandScheduler.cpp:141` | «Common::LockGuard lock(graphics.queue_mutex);» | «locked_ns    = Common::FrameStats::NowNs();» |
| `0df13a66:src/graphics/presentation/systemOverlay.cpp:1074` | «Common::LockGuard queue_lock(graphics.queue_mutex);» | «ImGui_ImplVulkan_RenderDrawData(ImGui::GetDrawData(),» |
| `61b410bf:src/graphics/presentation/window/swapchain.cpp:589` | «Common::LockGuard queue_lock(graphics.queue_mutex);» | «RequireVulkanSuccess(graphics.queue.waitIdle(), "wait for swapchain queue");» |
| `61b410bf:src/graphics/presentation/renderDoc.cpp:228` | «Common::LockGuard queue_lock(renderer.GetGraphics().queue_mutex);» | «if (state == RenderDocState::Requested) {» |
