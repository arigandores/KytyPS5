import subprocess, sys
# Red Team F20h: independent sample check of F20g refs (anchor substring in line L, +1 substring in line L+1).
G = 'C:/Program Files/Git/cmd/git.exe'
REFS = [
    ('302347b4', 'src/graphics/presentation/videoOut.cpp', 1381, 'const auto lat_us = r.reserve_host_ns != 0', '? (cur.host_ns -'),
    ('302347b4', 'src/graphics/presentation/videoOut.cpp', 1222, 'm_presenter.Present(*r.frame);', 'present_ns = Common::FrameStats::NowNs() - present_t0;'),
    ('302347b4', 'src/graphics/presentation/videoOut.cpp', 1236, 'r.cfg->flip_status.count++;', '// Track P, KYTY_PVAR=2'),
    ('302347b4', 'src/graphics/presentation/videoOut.cpp', 3845, 'KYTY_SYSV_ABI int VideoOutSubmitFlip(int handle, int index, int flip_mode, int64_t flip_arg) {', 'PRINT_NAME();'),
    ('302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 642, 'const bool unsubmitted = operation.tick >= CurrentTick();', 'const auto wait_t0'),
    ('302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 938, 'Common::LockGuard lock(graphics.queue_mutex);', 'tick = m_master.NextTick();'),
    ('302347b4', 'src/graphics/host_gpu/pageManager.cpp', 775, 'FS::Add(FS::Counter::ProtGpuRoNs, ns);', 'FS::Add(FS::Counter::ProtGpuRoN'),
    ('302347b4', 'src/common/hostException.cpp', 173, 'const bool resolved = handler(info);', 'if (t0 != 0 && fault_trace'),
    ('302347b4', 'src/kernel/semaphore.cpp', 294, 'auto result = sem->Wait(need, time);', ''),
    ('302347b4', 'src/kernel/eventFlag.cpp', 300, 'ef->Wait(bit_pattern, mode.wait, mode.clear, result_pat, timeout);', ''),
    ('302347b4', 'src/kernel/eventQueue.cpp', 416, '*out = owner->WaitForEvents(ev, num, 0);', '}'),
    ('302347b4', 'src/graphics/guest_gpu/graphicsRun.cpp', 714, 'gpu->m_work_available.Wait(&gpu->m_queue_mutex);', '}'),
    ('302347b4', 'src/graphics/guest_gpu/graphicsRun.cpp', 749, 'gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);', '}'),
    ('302347b4', 'src/graphics/presentation/window/swapchain.cpp', 657, 'const auto result = m_window.graphic_ctx.device.acquireNextImageKHR(', 'm_handle, std::numeric_limits<uint64_t>::max()'),
    ('302347b4', 'src/common/platform/sysWindowsVirtual.cpp', 321, 'if (VirtualProtect(reinterpret_cast<LPVOID>', 'GetProtectionFlag(mode), &old_protect) == 0) {'),
    ('302347b4', 'CMakeLists.txt', 155, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader', '-D SHADER_CACHE_EXTRA_FILES='),
    ('2d12e087', 'docs/ROADMAP.md', 23212, '(д) **Проект атрибуции — F20g (Probe Designer', '(е) **Звенья (стадия review лида у звена исполнителя):**'),
    ('2d12e087', 'docs/ROADMAP.md', 14328, '(з) **Аудит (п. 272) и «Процесс» — строка по пункту', ''),
    ('2d12e087', 'docs/ROADMAP.md', 23160, '(д) **Критерий «ИСПРАВЛЕНО Б32 Sky Garden»', '(е) **Серия F20e'),
    ('86abd902', 'docs/ROADMAP.md', 12914, 'спит часами хоста', '«B на 3 вблэнках» — модель [I]'),
    ('302347b4', 'src/kernel/pthread.cpp', 3143, 'thread->cond_cv.wait_for(cond_lock, std::chrono::microseconds(SIGNAL_APC_POLL_MICROS));', 'if (!ready()) {'),
    ('302347b4', 'src/kernel/semaphore.cpp', 25, 'constexpr uint32_t SIGNAL_APC_POLL_MICROS = 10000;', ''),
    ('302347b4', 'src/kernel/pthread.cpp', 1851, 'int result = NativeMutexLock(*mutex, nullptr);', ''),
    ('302347b4', 'src/kernel/pthread.cpp', 3153, 'result = NativeMutexLockRecurse(mutex_value, recurse);', ''),
    ('302347b4', 'src/kernel/pthread.cpp', 3006, 'int lock_result = NativeMutexLockRecurse(mutex_value, recurse);', 'if (result == OK) {'),
    ('302347b4', 'src/kernel/pthread.cpp', 3090, 'int lock_result = NativeMutexLockRecurse(mutex_value, recurse);', 'if (result == OK) {'),
    ('302347b4', 'src/kernel/pthread.cpp', 1348, 'static int NativeMutexLock(PthreadMutexPrivate* mutex, KernelUseconds* timeout_us) {', 'EXIT_IF(mutex == nullptr);'),
    ('302347b4', 'src/kernel/pthread.cpp', 4160, 'unsigned int KYTY_SYSV_ABI KernelSleep(unsigned int seconds) {', 'PRINT_NAME();'),
    ('302347b4', 'src/kernel/pthread.cpp', 4171, 'int KYTY_SYSV_ABI KernelNanosleep(const KernelTimespec* rqtp, KernelTimespec* rmtp) {', 'PRINT_NAME();'),
    ('302347b4', 'src/common/frameStats.cpp', 618, 'uint64_t ThreadCpuNs(ThreadRole role) {', '#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS'),
    ('302347b4', 'src/graphics/host_gpu/renderer/commandRecorder.cpp', 38, '// timeBeginPeriod(1) - so a 1 ms slice is about 1 ms, not the 15.6 ms default period.', 'constexpr auto WaitSlice  = std::chrono::milliseconds(1);'),
    ('302347b4', 'src/common/threads.cpp', 66, 'nullptr, nullptr, CREATE_WAITABLE_TIMER_HIGH_RESOLUTION, TIMER_ALL_ACCESS);', 'if (timer == nullptr) {'),
    ('302347b4', 'CMakeLists.txt', 156, '-D SHADER_CACHE_EXTRA_FILES=', '-P ${KYTY_SOURCE_DIR}/generate_version.cmake'),
    ('86abd902', 'docs/track-f/f20e/f20e_read.py', 23, "dump lines       IR lines (first non-blank character '%')", 'B2 window'),
    ('86abd902', 'docs/track-f/f20g.md', 1, '# F20g (`HPP-626`, Probe Designer): атрибуция долгого кадра Б32', ''),
]
cache = {}
bad = 0
for c, p, l, a, b in REFS:
    k = (c, p)
    if k not in cache:
        cache[k] = subprocess.run([G, 'show', '%s:%s' % k], capture_output=True).stdout.decode('utf-8', 'replace').split('\n')
    L = cache[k]
    la = L[l - 1] if l - 1 < len(L) else ''
    lb = L[l] if l < len(L) else ''
    ok = a in la and (b == '' or b in lb)
    if b == '' and a in la:
        ok = True
    bad += 0 if ok else 1
    print('OK ' if ok else 'BAD', '%s:%s:%d' % (c, p, l), '| +1:', lb.strip()[:90])
    if not ok:
        print('    L =', la.strip()[:160])
print('ALL OK' if bad == 0 else 'BAD %d' % bad, len(REFS))
