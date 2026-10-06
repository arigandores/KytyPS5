#!/usr/bin/env python3
"""F20j3 (HPP-646; ROADMAP s122 item 574(g)(1)): the inventory of the blocking host waits of KytyPS5 - every place has
a mark W:<kind> (verified in the source) or a line of the exception table with its reason.

    python waits_f20j3.py <src root> [--out <tsv>]

Scanned: src/** except graphics/shader/** and launcher/** (*.cpp, *.h, *.inc). Four parts:
  A. wait calls - CondVar Wait / WaitFor, std::condition_variable wait*, WaitForSingleObject / WaitForMultipleObjects,
     Sleep / SleepMicro / sleep_for, semaphore acquire, waitIdle / waitSemaphores, SDL_WaitEvent* / SDL_Delay, join;
     each line -> the rule of (file, enclosing function [, text]); MARK rules are verified: a BeginW / BeginWReg /
     BeginH of the named kind (or call) in the enclosing function above the line (or at the named caller line).
  B. Common::Mutex acquisitions (LockGuard, GpuMutexLock, .Lock() / ->Lock() on a Common::Mutex) - all covered by the
     primitive: Mutex::Lock -> LockB32 marks a contended acquisition W:emu_mutex (peer = the owner). Verified: the
     primitive has the mark; every .Lock() receiver resolves to a Common::Mutex declaration or is listed.
  C. std mutex declarations - TrackedMutex (verified in the source: the contended lock is W:emu_mutex) or an exception.
  D. spin locks - TrackingSpinLock, SpinGuard, ApplyGuard: W:spin (verified).
Exit 0 and the last line ALL OK only if every place has a verified mark or an exception, and nothing is unclassified.
"""
import os
import re
import sys

ROOT = sys.argv[1].rstrip('/\\')
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None

WAIT = re.compile(r"\.(Wait|WaitFor)\(|\.(wait|wait_for|wait_until)\(|->(Wait|WaitFor|wait|wait_for)\(|WaitForSingleObject\(|"
                  r"WaitForMultipleObjects\(|SleepMicro\(|sleep_for\(|(?<![A-Za-z_])Sleep\(|\.acquire\(\)|waitIdle\(\)|"
                  r"waitSemaphores\(|SDL_WaitEvent|SDL_Delay\(|\.join\(\)|pthread_join\(|EnterCriticalSection\(")
FUNC = re.compile(r"^(?:[\w:<>,*&\s]+?\s)?\**&?\s*((?:[A-Za-z_]\w*::)*~?[A-Za-z_]\w*)\s*\(")

# (file, function, text substring or None, status, detail). First match wins.
# status: MARK:<kind> - a new F20j3 mark (verified); OLD:<kind> - an F20j / F20j2 mark (W:<kind> or H:<call>, verified);
# CALLER:<kind>:<file>:<text> - the mark is at the caller (verified there); PRIM - the primitive itself;
# EXC:<code> - an exception (reason in detail).
R = [
    # ---- the instrument and the stands
    ('common/diagB32.cpp', 'TestSleepNow', None, 'EXC:stand', 'KYTY_TEST_B32 gpusleep/present sleep - outside every mark by item 574(g)(1) (PK-C)'),
    ('common/diagB32.cpp', 'Sampler::Run', None, 'EXC:instr', 'the sampler thread itself'),
    ('common/diagB32.cpp', 'LogHeader', None, 'EXC:instr', 'start-up wait for the sampler (once)'),
    ('common/diagB32.cpp', '*', None, 'EXC:instr', 'the M5 refresher thread (AsyncRefresh) - instrument'),
    ('common/frameStats.cpp', '*', None, 'EXC:instr', 'FrameStats sampler / knob "burn" (off by default) - instruments'),
    # ---- primitives
    ('common/threads.cpp', 'Thread::Thread', None, 'MARK:spin', 'creator waits for the thread start'),
    ('common/threads.cpp', 'Thread::Join', None, 'MARK:join', ''),
    ('common/threads.cpp', '*', None, 'PRIM', 'the primitive (CondVar / Sleep / CRITICAL_SECTION); the wait is marked at its call site, Mutex::Lock -> LockB32'),
    ('common/threads.h', '*', None, 'EXC:decl', 'declaration, not a call'),
    ('common/parallelCopy.cpp', '*', 'm_finished.wait', 'MARK:pcopy', ''),
    ('common/parallelCopy.cpp', '*', 'm_wake.wait', 'EXC:worker', 'copy worker idle wait (workers are not registered; the caller waits W:pcopy)'),
    ('common/parallelCopy.cpp', '*', 'join', 'EXC:shutdown', ''),
    # ---- GuestGpu
    ('graphics/guest_gpu/graphicsRun.cpp', 'GuestGpu::SendCommandSync', None, 'MARK:gpu_cmd', ''),
    ('graphics/guest_gpu/graphicsRun.cpp', 'GuestGpu::WaitForIdle', None, 'MARK:gpu_wait', 'item 574(a)(4)'),
    ('graphics/guest_gpu/graphicsRun.cpp', 'GuestGpu::ThreadRun', 'm_work_available.Wait(', 'OLD:gpu_idle', ''),
    ('graphics/guest_gpu/graphicsRun.cpp', 'GuestGpu::ThreadRun', 'm_work_available.WaitFor(', 'OLD:gpu_regmem', ''),
    ('graphics/guest_gpu/graphicsRun.cpp', 'BatonRelayRun', None, 'MARK:relay', 'item 574(a)(4)'),
    ('graphics/guest_gpu/graphicsRun.cpp', '*', 'cv.wait', 'EXC:worker', 'draw-ahead walker thread (knob dawalk) - not registered, its waits block nobody'),
    ('graphics/guest_gpu/graphicsRun.cpp', '*', 'to_relay.wait', 'EXC:worker', 'relay thread idle (waits for a job; while a job runs GuestGpu waits W:relay)'),
    ('graphics/guest_gpu/graphicsRun.cpp', '*', 'join', 'EXC:shutdown', ''),
    # ---- host GPU
    ('graphics/host_gpu/pageManager.cpp', '*', 'drain_cv.wait', 'MARK:pm_drain', ''),
    ('graphics/host_gpu/pageManager.cpp', '*', 'queue_cv.wait', 'EXC:worker', 'protect worker idle (not registered)'),
    ('graphics/host_gpu/pageManager.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/host_gpu/renderer/cache/bufferCache.cpp', '*', None, 'CALLEE:semwait', 'MasterSemaphore::Wait / CommandScheduler::Wait -> H:semwait (masterSemaphore.cpp)'),
    ('graphics/host_gpu/renderer/cache/faultManager.cpp', '*', None, 'CALLEE:semwait', 'CommandScheduler::Wait -> H:semwait'),
    ('graphics/host_gpu/renderer/cache/streamBuffer.cpp', '*', None, 'CALLEE:semwait', 'CommandScheduler::Wait -> H:semwait'),
    ('graphics/host_gpu/renderer/indirectArgsSanitizer.cpp', '*', None, 'CALLEE:semwait', 'CommandScheduler::Wait -> H:semwait'),
    ('graphics/host_gpu/renderer/pipeline/descriptorHeap.cpp', '*', None, 'CALLEE:semwait', 'destructor; MasterSemaphore::Wait -> H:semwait'),
    ('graphics/host_gpu/renderer/masterSemaphore.cpp', '*', None, 'OLDH:semwait', 'vkWaitSemaphores inside H:semwait'),
    ('graphics/host_gpu/renderer/cache/hostImport.cpp', '*', None, 'EXC:shutdown', 'destructor'),
    ('graphics/host_gpu/renderer/commandRecorder.cpp', 'CommandRecorder::Reserve', None, 'MARK:rec_wait', ''),
    ('graphics/host_gpu/renderer/commandRecorder.cpp', 'CommandRecorder::Drain', None, 'MARK:rec_wait', ''),
    ('graphics/host_gpu/renderer/commandRecorder.cpp', 'CommandRecorder::Loop', None, 'MARK:rec_idle', ''),
    ('graphics/host_gpu/renderer/commandRecorder.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', '*', 'm_drained.wait', 'MARK:asub_drain', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', '*', 'm_available.wait', 'MARK:asub_idle', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::Shutdown', None, 'EXC:shutdown', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::DeferOperation', None, 'MARK:ops_wait', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::DeferPriorityOperation', None, 'MARK:ops_wait', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::PriorityOperationsThread', 'm_operation_available.wait', 'MARK:ops_idle', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::PriorityOperationsThread', 'm_master.Wait', 'CALLEE:semwait', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::DrainPriorityOperations', None, 'MARK:ops_wait', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'CommandScheduler::WaitPriorityOperations', None, 'MARK:ops_wait', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', '*', 'waitIdle', 'EXC:debug', 'KYTY_SYNC_SUBMIT=1 only (debug aid)'),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', '*', 'm_master.Wait', 'CALLEE:semwait', 'MasterSemaphore::Wait -> H:semwait'),
    ('graphics/host_gpu/renderer/gpuCheckpoints.cpp', '*', None, 'EXC:debug', 'after a device loss with KYTY_GPU_CHECKPOINTS'),
    ('graphics/host_gpu/renderer/pipeline/computePretranslation.h', '*', 'queue.empty() && !running', 'EXC:teardown', '"Test/teardown only. The guest path never calls this."'),
    ('graphics/host_gpu/renderer/pipeline/computePretranslation.h', '*', None, 'EXC:worker', 'pretranslation worker idle / join'),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'PipelineCache::WaitForPendingPipelines', None, 'MARK:pipe_wait', ''),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'PipelineCache::GetGraphicsPipeline', None, 'MARK:pipe_wait', ''),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'PipelineCache::GetComputePipeline', None, 'MARK:pipe_wait', ''),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', '*', None, 'EXC:worker', 'pipeline worker / draw-ahead worker / driver-cache writer idle (not registered)'),
    ('graphics/host_gpu/renderer/shadowResolve.cpp', '*', None, 'EXC:worker', 'shadow resolve worker thread / join'),
    ('graphics/host_gpu/vma.cpp', '*', 'm_drained.wait', 'MARK:vma_flush', ''),
    ('graphics/host_gpu/vma.cpp', '*', 'm_available.wait', 'EXC:worker', 'VMA worker idle (not registered)'),
    # ---- presentation
    ('graphics/presentation/videoOut.cpp', 'VideoOutDriver::Impl::PresentThread', None, 'MARK:vo_pace', ''),
    ('graphics/presentation/videoOut.cpp', 'FlipQueue::Cancel', None, 'MARK:flip_cancel', 'item 574(a)(4)'),
    ('graphics/presentation/videoOut.cpp', 'FlipQueue::WaitForSubmitSlot', None, 'MARK:flip_slot', 'item 574(a)(4)'),
    ('graphics/presentation/videoOut.cpp', 'FlipQueue::Wait', None, 'MARK:flip_done', 'item 574(a)(4)'),
    ('graphics/presentation/videoOut.cpp', 'FlipQueue::Flip', None, 'MARK:flip_req', 'item 574(a)(4)'),
    ('graphics/presentation/videoOut.cpp', 'VideoOutDriver::WaitFlipDone', None, 'CALLER:flip_done', 'calls FlipQueue::Wait (the mark is there)'),
    ('graphics/presentation/videoOut.cpp', 'VideoOutWaitVblank', None, 'MARK:vblank', 'item 574(a)(4)'),
    ('graphics/presentation/videoOut.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/presentation/window/screenshot.cpp', 'ScreenshotGrabber::FlushVideoSlot', 'm_rec_cv.wait', 'MARK:rec_queue', ''),
    ('graphics/presentation/window/screenshot.cpp', 'ScreenshotGrabber::RecorderThread', None, 'EXC:worker', 'video encoder thread idle (KYTY_REC)'),
    ('graphics/presentation/window/screenshot.cpp', '*', 'join', 'EXC:shutdown', ''),
    ('graphics/presentation/window/screenshot.cpp', '*', None, 'CALLEE:semwait', 'CommandScheduler::Wait -> H:semwait'),
    ('graphics/presentation/window/swapchain.cpp', '*', 'm_available.Wait', 'MARK:frame_pool', ''),
    ('graphics/presentation/window/swapchain.cpp', '*', 'waitIdle', 'EXC:rare', 'Swapchain::Destroy - re-creation of the swapchain (resize / minimize), not in a hold'),
    ('graphics/presentation/window/swapchain.cpp', '*', None, 'CALLEE:semwait', 'CommandScheduler::Wait -> H:semwait (acquire / present ticks)'),
    ('graphics/presentation/window/vulkanWindow.cpp', '*', None, 'EXC:shutdown', 'device shutdown'),
    ('graphics/presentation/window/window.cpp', 'WindowContext::RunOnMainThread', None, 'MARK:main_task', ''),
    ('graphics/presentation/window/window.cpp', '*', 'SDL_Delay(16)', 'EXC:startup', 'shader preparation screen on the main thread before the guest starts'),
    ('graphics/presentation/window/window.cpp', 'WindowContext::UpdateTitle', None, 'EXC:stand', 'MainStallTest stand (knob)'),
    ('graphics/presentation/window/window.cpp', '*', None, 'EXC:stand', 'KYTY_TEST_HIDLOSS / KYTY_TEST_MINIMIZE stands'),
    ('graphics/presentation/window/hostInput.cpp', 'HostInputWaitEvent', None, 'CALLER:main_idle:graphics/presentation/window/window.cpp:const bool b32_event = HostInputWaitEvent(&loop.event);', 'the main loop marks the call'),
    # ---- kernel
    ('kernel/eventFlag.cpp', 'KernelEventFlagPrivate::Wait', None, 'OLD:evf', ''),
    ('kernel/eventFlag.cpp', 'KernelWaitEventFlag', None, 'CALLER:evf', 'calls KernelEventFlagPrivate::Wait'),
    ('kernel/eventFlag.cpp', '*', None, 'MARK:spin', '10 us sleep loops of the event flag object'),
    ('kernel/eventQueue.cpp', '*', None, 'OLD:eq', ''),
    ('kernel/pthread.cpp', 'KernelGetTscFrequencyNative', None, 'EXC:startup', 'TSC calibration at start'),
    ('kernel/pthread.cpp', 'SchedulerBackoffOnce', None, 'CALLER:sleep', 'inside SleepMicroWithSignalPoll (W:sleep at KernelUsleep / KernelSleep)'),
    ('kernel/pthread.cpp', 'SleepMicroWithSignalPoll', None, 'CALLER:sleep', 'callers KernelUsleep / KernelSleep carry W:sleep'),
    ('kernel/pthread.cpp', 'FreeDetachedThreads', None, 'EXC:worker', 'the reaper thread of detached guest threads (emulator thread)'),
    ('kernel/pthread.cpp', 'NativeMutexLock', '*timeout_us', 'MARK:mutex', 'timed lock of an owned error-check mutex'),
    ('kernel/pthread.cpp', 'NativeMutexLock', None, 'OLD:mutex', ''),
    ('kernel/pthread.cpp', 'RwlockLockCooperative', None, 'MARK:rwlock', ''),
    ('kernel/pthread.cpp', 'PthreadCondTimedwait', None, 'OLD:cond', ''),
    ('kernel/pthread.cpp', 'PthreadCondTimedwaitAbs', None, 'OLD:cond', ''),
    ('kernel/pthread.cpp', 'PthreadCondWait', None, 'OLD:cond', ''),
    ('kernel/pthread.cpp', 'pthread_once', None, 'MARK:once', ''),
    ('kernel/pthread.cpp', 'PthreadJoin', None, 'MARK:join', ''),
    ('kernel/pthread.cpp', 'pthread_join', None, 'CALLER:join', 'the POSIX wrapper calls PthreadJoin (W:join there)'),
    ('kernel/pthread.h', '*', None, 'EXC:decl', 'declaration, not a call'),
    ('kernel/semaphore.cpp', 'KernelSemaPrivate::Wait', None, 'OLD:sem', ''),
    ('kernel/semaphore.cpp', 'KernelWaitSema', None, 'CALLER:sem', 'calls KernelSemaPrivate::Wait'),
    ('kernel/semaphore.cpp', 'SemTimedwaitImpl', None, 'CALLER:psem', 'calls the POSIX semaphore Wait'),
    ('kernel/semaphore.cpp', '*', 'm_cond_var.WaitFor', 'OLD:psem', 'POSIX semaphore wait (F20j W:psem)'),
    ('kernel/semaphore.cpp', '*', None, 'MARK:spin', '10 us sleep loops of the semaphore destructor'),
    ('kernel/syncOnAddress.cpp', 'WaitPortable', None, 'MARK:addr', ''),
    # ---- libs (guest HLE)
    ('libs/audio.cpp', 'playback_simulate', None, 'EXC:worker', 'audio3d playback thread (emulator thread, not registered)'),
    ('libs/audio.cpp', '*', None, 'MARK:audio', ''),
    ('libs/libAudio2.cpp', '*', None, 'MARK:audio', ''),
    ('libs/avPlayer.cpp', '*', None, 'MARK:av', ''),
    ('libs/controller.cpp', 'PadOutput::Loop', None, 'EXC:worker', 'PadOutput thread idle (pad output worker, B24)'),
    ('libs/controller.cpp', '*', None, 'EXC:shutdown', 'pad release flush / join at exit'),
    ('libs/libAmpr.cpp', '*', None, 'EXC:name', 'a function name containing WaitOnAddress, not a wait'),
    ('libs/libC.cpp', 'std_execute_once', None, 'MARK:once', ''),
    ('libs/libKernel.cpp', 'WaitForSignalDispatch', None, 'EXC:platform', 'not compiled on Windows (#if != WINDOWS)'),
    ('libs/libKernel.cpp', 'FiberWaitAndEnterRunning', None, 'MARK:fiber', ''),
    ('libs/libKernel.cpp', 'KernelAioWaitRequest', None, 'MARK:aio', ''),
    ('libs/libUlt.cpp', 'UltSemaphoreAcquire', None, 'MARK:ult', ''),
    ('libs/libUlt.cpp', '*', 'PthreadJoin', 'CALLER:join', 'PthreadJoin carries W:join'),
    ('libs/network.cpp', '*', None, 'MARK:net', ''),
    # ---- main only (not in the test binary's base 302347b4): other tracks' code
    ('graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', '*', 'join', 'EXC:shutdown', 'S-replay capture writer stop (main only)'),
    ('graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', '*', None, 'EXC:worker', 'S-replay capture writer thread idle (main only; not registered)'),
    ('kernel/pvar.cpp', '*', None, 'EXC:knob', 'track P hold wait, KYTY_PVAR_HOLD (default 0, not shipped; main only)'),
]

# std mutex declarations: (file, name, status, reason). TRACKED - verified TrackedMutex in the source.
STD = [
    ('common/frameStats.cpp', '*', 'EXC:instr', 'FrameStats (instrument)'),
    ('common/diagB32.cpp', '*', 'EXC:instr', 'the instrument (M5 refresher list / AsyncRefresh stop)'),
    ('common/threads.cpp', 'm_mutex', 'EXC:platform', 'the non-Windows Common::Mutex branch (Windows: CRITICAL_SECTION, primitive-marked)'),
    ('common/parallelCopy.cpp', 'm_mutex', 'EXC:cv', 'the mutex of m_wake / m_finished (std::condition_variable needs std::mutex); the caller wait is W:pcopy'),
    ('graphics/guest_gpu/graphicsRun.cpp', 'mutex', 'EXC:cv', 'walker / relay mutex of their condition variables (W:relay marks the GuestGpu wait)'),
    ('graphics/guest_gpu/graphicsRun.cpp', 'g_draw_ahead_walker_mutex', 'EXC:knob', 'draw-ahead walker start / stop (knob dawalk)'),
    ('graphics/guest_gpu/graphicsRun.h', 'm_shutdown_mutex', 'EXC:shutdown', ''),
    ('graphics/host_gpu/pageManager.cpp', 'queue_mutex', 'EXC:cv', 'mutex of queue_cv / drain_cv (W:pm_drain marks the caller)'),
    ('graphics/host_gpu/renderer/commandRecorder.h', 'm_mutex', 'EXC:cv', 'mutex of m_progress / m_pending (W:rec_wait / rec_idle)'),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'm_mutex', 'EXC:cv', 'async submitter queue mutex of m_available / m_drained (W:asub_idle / asub_drain)'),
    ('graphics/host_gpu/renderer/commandScheduler.h', 'm_operation_mutex', 'EXC:cv', 'mutex of m_operation_available (W:ops_wait / ops_idle)'),
    ('graphics/host_gpu/renderer/gpuCheckpoints.cpp', '*', 'EXC:debug', 'KYTY_GPU_CHECKPOINTS (debug)'),
    ('graphics/host_gpu/renderer/pipeline/computePretranslation.h', 'mutex', 'EXC:cv', 'pretranslation queue mutex of its cv (worker)'),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 'ahead_mutex', 'EXC:cv', 'draw-ahead workers cv mutex'),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.h', 'm_job_mutex', 'EXC:cv', 'mutex of m_ready_cv / m_idle_cv / m_job_cv (W:pipe_wait)'),
    ('graphics/host_gpu/renderer/pipeline/pipelineCache.h', 'm_pcw_mutex', 'EXC:cv', 'driver-cache writer cv mutex'),
    ('graphics/host_gpu/renderer/shadowResolve.cpp', 'g_mutex', 'EXC:cv', 'shadow resolve worker cv mutex'),
    ('graphics/host_gpu/vma.cpp', 'm_mutex', 'EXC:cv', 'VMA worker queue cv mutex (W:vma_flush)'),
    ('graphics/presentation/window/screenshot.h', 'm_rec_mutex', 'EXC:cv', 'recorder queue cv mutex (W:rec_queue)'),
    ('kernel/pthread.cpp', 'm', 'EXC:layout', 'internal mutex of a guest primitive (PthreadMutex / Rwlock / Cond private, reserved[256] first - '
                                              'layout kept, RC10); the guest-level waits are W:mutex / rwlock / cond'),
    ('kernel/pthread.cpp', 'g_pthread_once_mutex', 'EXC:cv', 'mutex of g_pthread_once_cv (W:once)'),
    ('libs/avPlayer.cpp', 'mutex', 'EXC:cv', 'packet / frame queue mutexes of their cv (W:av)'),
    ('libs/controller.cpp', 'm_mutex', 'EXC:cv', 'PadOutput queue mutex of m_cv (worker)'),
    ('libs/imeDialog.cpp', 'g_mutex', 'EXC:target', 'imeDialog.cpp is compiled into ime_dialog_tests without common; IME dialog state, not opened in a hold'),
    ('libs/libC.cpp', 'g_execute_once_mutex', 'EXC:cv', 'mutex of g_execute_once_cv (W:once)'),
    ('libs/libUlt.cpp', 'mutex', 'EXC:cv', 'ULT semaphore mutex of its cv (W:ult)'),
    ('libs/network.cpp', 'g_epoll_mutex', 'EXC:cv', 'mutex of g_epoll_changed (W:net)'),
    ('loader/redZonePatcher.cpp', 'mutex', 'EXC:startup', 'module load time'),
    ('graphics/host_gpu/renderer/diagF5.cpp', '*', 'EXC:knob', 'KYTY_DIAG_F5 counters (default 0, instrument; main only)'),
    ('graphics/host_gpu/renderer/pipeline/shaderReplay.cpp', 'm_wait_mutex', 'EXC:cv', 'S-replay writer wait cv mutex (main only)'),
]


def files():
    for d, _, fs in os.walk(ROOT):
        rel = os.path.relpath(d, ROOT).replace('\\', '/')
        if rel.startswith('graphics/shader') or rel.startswith('launcher'):
            continue
        for f in sorted(fs):
            if f.endswith(('.cpp', '.h', '.inc')):
                yield (rel + '/' + f).lstrip('./')


def strip_comment(s):
    return re.sub(r'//.*', '', s)


def enclosing(lines, i):
    """(function name, first line index) of the column-0 definition above line i; ('-', i) if none."""
    for j in range(i, -1, -1):
        t = lines[j]
        if t[:1] in ('', ' ', '\t', '}', '#', '/', '{', ')'):
            continue
        if t.startswith(('namespace', 'class ', 'struct ', 'using ', 'static_assert', 'enum ', 'LIB_', 'KYTY_SUBSYSTEM')):
            return '-', j
        if t.startswith('template'):
            continue
        m = FUNC.match(t)
        if m:
            return m.group(1), j
        return '-', j
    return '-', 0


def rule_of(path, func, text):
    for f, fn, sub, st, det in R:
        if f != path:
            continue
        if fn != '*' and fn != func:
            continue
        if sub is not None and sub not in text:
            continue
        return st, det
    return None, None


def has_mark(lines, start, i, kind):
    """A Begin of the kind between the function start and line i (or 60 lines above for '-')."""
    lo = start if start < i else max(0, i - 60)
    lo = max(lo, i - 400)
    for j in range(i, lo - 1, -1):
        s = lines[j]
        if kind.startswith('H:'):
            if 'BeginH(' in s and ('Call::' + CALLS.get(kind[2:], '?')) in s:
                return True
        elif ('BeginWReg(' in s or 'BeginW(' in s) and ('Wait::' + KINDS.get(kind, '?')) in s:
            return True
    return False


KINDS = {'emu_mutex': 'EmuMutex', 'gpu_wait': 'GpuWait', 'gpu_cmd': 'GpuCmd', 'flip_slot': 'FlipSlot',
         'flip_done': 'FlipDone', 'flip_cancel': 'FlipCancel', 'flip_req': 'FlipReq', 'vo_pace': 'VoPace',
         'relay': 'Relay', 'frame_pool': 'FramePool', 'rec_wait': 'RecWait', 'rec_idle': 'RecIdle',
         'asub_idle': 'ASubIdle', 'asub_drain': 'ASubDrain', 'ops_wait': 'OpsWait', 'ops_idle': 'OpsIdle',
         'pipe_wait': 'PipeWait', 'pcopy': 'PCopy', 'pm_drain': 'PmDrain', 'vma_flush': 'VmaFlush',
         'rec_queue': 'RecQueue', 'main_task': 'MainTask', 'main_idle': 'MainIdle', 'spin': 'Spin', 'av': 'Av',
         'vblank': 'Vblank', 'once': 'Once', 'join': 'Join', 'addr': 'Addr', 'aio': 'Aio', 'fiber': 'Fiber',
         'audio': 'Audio', 'ult': 'Ult', 'net': 'Net', 'rwlock': 'Rwlock', 'cond': 'Cond', 'mutex': 'Mutex',
         'sem': 'Sem', 'psem': 'PSem', 'evf': 'Evf', 'eq': 'Eq', 'sleep': 'Sleep', 'gpu_idle': 'GpuIdle',
         'gpu_regmem': 'GpuRegmem'}
CALLS = {'semwait': 'SemWait', 'present': 'Present'}

TEXT = {}
for p in files():
    TEXT[p] = open(ROOT + '/' + p, encoding='utf-8', errors='replace').read().split('\n')

rows = []
bad = 0
# MasterSemaphore::Wait carries H:semwait (F20j): every scheduler / semaphore wait call is inside it.
_ms = TEXT.get('graphics/host_gpu/renderer/masterSemaphore.cpp', [])
SEMWAIT_OK = any('BeginH(Common::DiagB32::Call::SemWait)' in x for x in _ms)
# ---- A
for p, lines in TEXT.items():
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith('//') or not WAIT.search(strip_comment(l)):
            continue
        func, start = enclosing(lines, i)
        st, det = rule_of(p, func, s)
        ok = st is not None
        if st and st.startswith(('MARK:', 'OLD:')):
            kind = st.split(':', 1)[1]
            ok = has_mark(lines, start, i, kind)
        elif st == 'CALLEE:semwait':
            ok = SEMWAIT_OK
        elif st == 'OLDH:semwait':
            ok = has_mark(lines, start, i, 'H:semwait')
        elif st and st.startswith('CALLER:') and st.count(':') >= 4:
            _, kind, cf, ctext = st.split(':', 3)
            cl = TEXT.get(cf, [])
            ci = next((k for k, x in enumerate(cl) if ctext in x), None)
            ok = ci is not None and has_mark(cl, max(0, ci - 30), ci, kind)
        if not ok:
            bad += 1
        rows.append(('A', p, i + 1, func, st or 'UNCLASSIFIED', 'ok' if ok else 'FAIL', det or '', s[:120]))

# ---- B: Common::Mutex acquisitions
prim_ok = False
tc = TEXT.get('common/threads.cpp', [])
for i, l in enumerate(tc):
    if l.startswith('void Mutex::LockB32()'):
        body = '\n'.join(tc[i:i + 25])
        prim_ok = 'Wait::EmuMutex' in body and 'OwningThread' in body and 'EndWithPeer' in body
    if l.startswith('void Mutex::Lock()'):
        prim_ok = prim_ok or False
lock_body = '\n'.join(tc[next((k for k, x in enumerate(tc) if x.startswith('void Mutex::Lock()')), 0):][:6])
prim_ok = prim_ok and 'DiagB32::g_on' in lock_body and 'LockB32()' in lock_body
if not prim_ok:
    bad += 1
COMMON = set()
for p, lines in TEXT.items():
    for l in lines:
        m = re.search(r'(?:Common::)?Mutex\s*\*?\s+(\w+)\s*[;{=]', strip_comment(l))
        if m and 'std::' not in l and 'TrackedMutex' not in l:
            COMMON.add(m.group(1))
        m = re.search(r'unique_ptr<Common::Mutex>\s+(\w+)', l)
        if m:
            COMMON.add(m.group(1))
n_guard = 0
for p, lines in TEXT.items():
    for i, l in enumerate(lines):
        s = strip_comment(l)
        if re.search(r'\bCommon::LockGuard\b|\bLockGuard\s+\w+\(|GpuMutexLock\s+\w+\(', s) and 'class ' not in s:
            n_guard += 1
            rows.append(('B', p, i + 1, '-', 'PRIM:emu_mutex', 'ok' if prim_ok else 'FAIL', 'Common::Mutex via LockGuard', l.strip()[:120]))
        for m in re.finditer(r'([\w\]\)]+)(?:\.|->)(?:GetMutex\(\)\.)?Lock\(\)', s):
            recv = m.group(1)
            if p == 'common/threads.h' or 'class ' in s:
                continue
            known = recv in COMMON or 'GetMutex()' in s or recv in ('mutex', 'data_mutex', 'm_mutex')
            st = 'PRIM:emu_mutex' if known else 'UNCLASSIFIED'
            if not known:
                bad += 1
            rows.append(('B', p, i + 1, '-', st, 'ok' if known and prim_ok else 'FAIL', 'Common::Mutex .Lock() (%s)' % recv, l.strip()[:120]))

# ---- C: std mutex declarations
DECL = re.compile(r'^\s*(?:static |mutable |alignas\(\d+\) )*(?:Common::DiagB32::TrackedMutex<)?std::(mutex|recursive_mutex|shared_mutex)(>|,[^>]*>)?\s*&?\s+(\w+)')
for p, lines in TEXT.items():
    for i, l in enumerate(lines):
        m = DECL.match(l)
        if not m or '(' in l.split(m.group(3))[1][:2]:
            continue
        name = m.group(3)
        tracked = 'TrackedMutex<' in l
        st, det = None, None
        if tracked:
            st, det = 'TRACKED:emu_mutex', 'Common::DiagB32::TrackedMutex'
        else:
            for f, n, s2, d2 in STD:
                if f == p and (n == '*' or n == name):
                    st, det = s2, d2
                    break
        if st is None:
            bad += 1
        rows.append(('C', p, i + 1, name, st or 'UNCLASSIFIED', 'ok' if st else 'FAIL', det or '', l.strip()[:120]))

# ---- D: spin locks
for p, needle, kind in [('graphics/host_gpu/regionManager.h', 'TrackingSpinLock', 'spin'),
                        ('graphics/host_gpu/pageManager.cpp', 'SpinGuard(std::atomic_flag& lock)', 'spin'),
                        ('graphics/host_gpu/pageManager.cpp', 'ApplyGuard(std::atomic_flag& lock', 'spin')]:
    lines = TEXT.get(p, [])
    i = next((k for k, x in enumerate(lines) if needle in x), None)
    ok = i is not None and any(('Wait::Spin' in x) for x in lines[i:i + 40])
    if not ok:
        bad += 1
    rows.append(('D', p, (i or 0) + 1, needle, 'MARK:spin', 'ok' if ok else 'FAIL', 'contended spin', ''))

summary = {}
for r in rows:
    key = (r[0], r[4].split(':')[0] + (':' + r[4].split(':')[1] if r[4].startswith(('MARK', 'OLD', 'EXC', 'CALLER', 'TRACKED', 'PRIM')) and ':' in r[4] else ''))
    summary[key] = summary.get(key, 0) + 1
out = ['part\tfile\tline\tfunction/name\tstatus\tcheck\tdetail\ttext']
out += ['\t'.join(str(x) for x in r) for r in rows]
if OUT:
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
for r in rows:
    if r[5] != 'ok':
        print('FAIL\t' + '\t'.join(str(x) for x in r))
for k in sorted(summary):
    print('%s %-28s %d' % (k[0], k[1], summary[k]))
print('places: A %d, B %d (LockGuard %d), C %d, D %d; primitive mark %s; not ok %d' % (
    sum(1 for r in rows if r[0] == 'A'), sum(1 for r in rows if r[0] == 'B'), n_guard,
    sum(1 for r in rows if r[0] == 'C'), sum(1 for r in rows if r[0] == 'D'), 'ok' if prim_ok else 'FAIL', bad))
print('ALL OK' if bad == 0 else 'FAILED')
sys.exit(0 if bad == 0 else 1)
