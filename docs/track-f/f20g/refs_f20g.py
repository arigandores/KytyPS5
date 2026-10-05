# F20g refs map (rule 24(1)): every <commit>:<path>:<line> of the report - the anchor in the line, the +1 text in the next line.
import subprocess
import sys

NL = chr(10)
R = [
    ('R1', '2d12e087', 'docs/ROADMAP.md', 23207, '549. **Звено F20f трека F (`HPP-625`, лид; приёмка F20e', '(а) **Приёмка строкой. F20e ✓**'),
    ('R2', '2d12e087', 'docs/ROADMAP.md', 23211, '(г) **Б32 Sky Garden — «держится на установленном»**', '(д) **Проект атрибуции — F20g (Probe Designer'),
    ('R3', '2d12e087', 'docs/ROADMAP.md', 23212, '(д) **Проект атрибуции — F20g (Probe Designer', '(е) **Звенья (стадия review лида у звена исполнителя):**'),
    ('R4', '2d12e087', 'docs/ROADMAP.md', 23160, '(д) **Критерий «ИСПРАВЛЕНО Б32 Sky Garden» (решение лида, до кода).**', '(е) **Серия F20e (Harness Engineer'),
    ('R5', '2d12e087', 'docs/ROADMAP.md', 23159, '(г) **Свод после (в).**', '(д) **Критерий «ИСПРАВЛЕНО Б32 Sky Garden»'),
    ('R6', '457655e2', 'docs/ROADMAP.md', 22463, '451. **Звено F19b трека F (`HPP-544`, лид; приёмка F19a', '(а) **Приёмка строкой. F19a ✓**'),
    ('R7', '2d12e087', 'docs/ROADMAP.md', 22555, '462. **Звено F20b трека F (`HPP-552`, лид; приёмка F20a', '(а) **Приёмка строкой. F20a ✓**'),
    ('R8', '2d12e087', 'docs/ROADMAP.md', 23162, '(ж) **Чтение F20f (решено сейчас, до данных).**', '(з) **Долги F20c (п. 324(и)(5)).**'),
    ('R9', '2d12e087', 'docs/track-f/f20c.md', 132, '| тег | idx | n | `dt_us` |', '|---|'),
    ('R10', '2d12e087', 'docs/track-f/f20e.md', 114, '### Unattributed hold frames', '| tag | idx | n | `dt_us` |'),
    ('R11', '2d12e087', 'docs/ROADMAP.md', 14328, '(з) **Аудит (п. 272) и «Процесс» — строка по пункту', 'два комментария) — принят'),
    ('C1', '302347b4', 'src/graphics/presentation/videoOut.cpp', 1384, 'LOGF("FrameTrace: n=%" PRIu64 " dt_us=%llu lat_us=%llu', '" gpu_blocked=%llu submits=%llu'),
    ('C2', '302347b4', 'src/graphics/presentation/videoOut.cpp', 1381, 'const auto lat_us = r.reserve_host_ns != 0', '? (cur.host_ns - r.reserve_host_ns) / 1000u'),
    ('C3', '302347b4', 'src/graphics/presentation/videoOut.cpp', 1222, 'm_presenter.Present(*r.frame);', 'present_ns = Common::FrameStats::NowNs() - present_t0;'),
    ('C4', '302347b4', 'src/graphics/presentation/videoOut.cpp', 1236, 'r.cfg->flip_status.count++;', '// Track P, KYTY_PVAR=2'),
    ('C5', '302347b4', 'src/graphics/presentation/videoOut.cpp', 3845, 'KYTY_SYSV_ABI int VideoOutSubmitFlip(int handle, int index, int flip_mode, int64_t flip_arg) {', 'PRINT_NAME();'),
    ('C6', '302347b4', 'src/graphics/presentation/videoOut.cpp', 2565, '{"gw_idle_ns", FS::Counter::GpuWallIdleNs, false},', '{"gw_idle_n", FS::Counter::GpuWallIdleN, false},'),
    ('C7', '302347b4', 'src/common/frameStats.cpp', 636, 'uint64_t ProcessCpuNs() {', '#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS'),
    ('C8', '302347b4', 'src/common/frameStats.cpp', 618, 'uint64_t ThreadCpuNs(ThreadRole role) {', '#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS'),
    ('C9', '302347b4', 'src/common/frameStats.cpp', 607, 'bool GpuWallOn() {', 'static const bool on = [] {'),
    ('C10', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 642, 'const bool unsubmitted = operation.tick >= CurrentTick();', 'const auto wait_t0'),
    ('C11', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 655, 'LOGF("PriorityStall: tick=%llu unsub=%d us=%lld site=%s', 'static_cast<unsigned long long>(operation.tick)'),
    ('C12', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 680, 'void CommandScheduler::WaitPriorityOperations(uint64_t tick) {', 'EXIT_IF(g_deferred_callback_scheduler == this);'),
    ('C13', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 927, 'DrainAsyncSubmits();', 'const auto buffer = m_command.m_buffer;'),
    ('C14', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 938, 'Common::LockGuard lock(graphics.queue_mutex);', 'tick = m_master.NextTick();'),
    ('C15', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 959, 'result = graphics.queue.submit(1, &submit_info, nullptr);', 'RecordGpuSubmission(this, m_master.Handle(), tick, submit, true, result);'),
    ('C16', '302347b4', 'src/graphics/host_gpu/renderer/commandScheduler.cpp', 997, 'FS::Add(FS::Counter::SubmitNs, ns);', 'FS::Add(FS::Counter::Submits, 1);'),
    ('C17', '302347b4', 'src/graphics/host_gpu/renderer/masterSemaphore.cpp', 149, 'FS::Add(FS::Counter::SemWaitNs, ns);', 'FS::Add(FS::Counter::SemWaits, 1);'),
    ('C18', '302347b4', 'src/common/hostException.cpp', 173, 'const bool resolved = handler(info);', 'if (t0 != 0 && fault_trace && info.type == ExceptionType::AccessViolation) {'),
    ('C19', '302347b4', 'src/common/platform/sysWindowsVirtual.cpp', 321, 'if (VirtualProtect(reinterpret_cast<LPVOID>', 'GetProtectionFlag(mode), &old_protect) == 0) {'),
    ('C20', '302347b4', 'src/graphics/presentation/window/swapchain.cpp', 657, 'const auto result = m_window.graphic_ctx.device.acquireNextImageKHR(', 'm_handle, std::numeric_limits<uint64_t>::max()'),
    ('C21', '302347b4', 'src/graphics/guest_gpu/graphicsRun.cpp', 714, 'gpu->m_work_available.Wait(&gpu->m_queue_mutex);', '}'),
    ('C22', '302347b4', 'src/graphics/guest_gpu/graphicsRun.cpp', 749, 'gpu->m_work_available.WaitFor(&gpu->m_queue_mutex, 100);', '}'),
    ('C23', '302347b4', 'src/kernel/pthread.cpp', 3104, 'int KYTY_SYSV_ABI PthreadCondWait(PthreadCond* cond, PthreadMutex* mutex) {', 'PRINT_NAME();'),
    ('C24', '302347b4', 'src/kernel/pthread.cpp', 3143, 'thread->cond_cv.wait_for(cond_lock, std::chrono::microseconds(SIGNAL_APC_POLL_MICROS));', 'if (!ready()) {'),
    ('C25', '302347b4', 'src/kernel/pthread.cpp', 2938, 'int KYTY_SYSV_ABI PthreadCondTimedwait(PthreadCond* cond, PthreadMutex* mutex,', 'KernelUseconds'),
    ('C26', '302347b4', 'src/kernel/pthread.cpp', 1851, 'int result = NativeMutexLock(*mutex, nullptr);', ''),
    ('C27', '302347b4', 'src/kernel/pthread.cpp', 2900, 'int KYTY_SYSV_ABI PthreadCondSignal(PthreadCond* cond) {', '// PRINT_NAME();'),
    ('C28', '302347b4', 'src/kernel/pthread.cpp', 2810, 'int KYTY_SYSV_ABI PthreadCondBroadcast(PthreadCond* cond) {', 'PRINT_NAME'),
    ('C29', '302347b4', 'src/kernel/pthread.cpp', 4151, 'int KYTY_SYSV_ABI KernelUsleep(KernelUseconds microseconds) {', 'Common::Timer t;'),
    ('C30', '302347b4', 'src/kernel/pthread.cpp', 3343, 'Pthread run begin: %s, id = %d, os_thread_id', ', arg = 0x%016'),
    ('C31', '302347b4', 'src/kernel/semaphore.cpp', 294, 'auto result = sem->Wait(need, time);', ''),
    ('C32', '302347b4', 'src/kernel/semaphore.cpp', 336, 'auto result = sem->Signal(count);', ''),
    ('C33', '302347b4', 'src/kernel/eventFlag.cpp', 300, 'result = ef->Wait(bit_pattern, mode.wait, mode.clear, result_pat, timeout);', ''),
    ('C34', '302347b4', 'src/kernel/eventFlag.cpp', 350, 'ef->Set(bit_pattern);', ''),
    ('C35', '302347b4', 'src/kernel/eventQueue.cpp', 416, '*out = owner->WaitForEvents(ev, num, 0);', '}'),
    ('C36', '302347b4', 'src/graphics/host_gpu/pageManager.cpp', 775, 'FS::Add(FS::Counter::ProtGpuRoNs, ns);', 'FS::Add(FS::Counter::ProtGpuRoN'),
    ('C37', '302347b4', 'CMakeLists.txt', 155, '-D SHADER_SOURCE_DIR=${KYTY_SOURCE_DIR}/graphics/shader', '-D SHADER_CACHE_EXTRA_FILES='),
    ('C38', '302347b4', 'src/common/frameStats.cpp', 642, 'if (GetProcessTimes(GetCurrentProcess(), &creation, &exit, &kernel, &user) == 0) {', 'return 0;'),
]


def main():
    cache = {}
    bad = 0
    out = []
    for rid, c, p, n, a, b in R:
        k = (c, p)
        if k not in cache:
            res = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % k], capture_output=True)
            cache[k] = res.stdout.decode('utf-8', 'replace').split(NL)
        t = cache[k]
        l0 = t[n - 1] if n - 1 < len(t) else ''
        l1 = t[n].strip() if n < len(t) else ''
        ok = a in l0 and ((b == '' and l1 == '') or (b != '' and b in l1))
        bad += 0 if ok else 1
        out.append('%s %s %s:%s:%d | +1: %s' % ('OK  ' if ok else 'FAIL', rid, c, p, n, l1[:100]))
    out.append('refs %d, failed %d' % (len(R), bad))
    out.append('ALL OK' if bad == 0 else 'FAILED')
    open('C:/kyty/f287/f20g/refs_f20g.txt', 'w', encoding='utf-8').write(NL.join(out) + NL)
    print(NL.join(out))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
