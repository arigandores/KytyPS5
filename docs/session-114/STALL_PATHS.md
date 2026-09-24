# STALL_PATHS — how a priority operation can sit on the recording tick for seconds (event `vbn113k`, frame 9672)

Read-only analysis. Source: `C:/kyty/KytyPS5` at HEAD `ba07f75`. `vbn113k` ran build `cf22e223` (commit `967d1aa`);
`git diff 967d1aa HEAD` over `src/graphics`, `src/common` and `src/libs` shows only the session-113 instrument
(`NoteIdlePriority`, `PriorityStall`, three counters), so every path below is the one that ran. Line numbers are HEAD
line numbers, so `graphicsRun.cpp` lines after 334 sit about 16–18 lines lower in the `vbn113k` binary. The log
(`C:/kyty/s113/log_vbn113k.txt`) was read only by streaming Python in `rb` mode; log positions are given as `L<n>`.

---

## 0. Verdict (short)

The priority-operation thread waited because **the GuestGpu thread was blocked inside a flip packet**, not because it
was idle. The chain:

1. The presentation thread was presenting guest flip 9672. It holds `VideoOutConfig::mutex` for the whole
   present, from `videoOut.cpp:1138` to `videoOut.cpp:2564`. Inside `Presenter::Present` it got stuck for about 3 s
   **after** its queue submit, which is present-scheduler tick 9728. The ring shows that submit early in frame
   9672. The prime suspect is `UpdateTitle` → `RunOnMainThread` (`swapchain.cpp:903` → `window.cpp:1093`, which waits
   with no bound at `window.cpp:784-787` for the SDL main thread).
2. Meanwhile the GuestGpu thread had queued an EOP-interrupt priority operation on the recording tick (329576). This is
   routine: `BufferFlushLazy` skips the submit within 300 µs of the last one. GuestGpu then reached the next flip
   packet, and `FlipWithInterrupt` → `PrepareVideoOutFlip` → `ReserveFlipRequest` blocked on the same
   `VideoOutConfig::mutex` (`videoOut.cpp:525`). That is **before** the flip's own `Flush` (`graphicsRun.cpp:3113`),
   which is the flush that normally submits such an interrupt within microseconds.
3. So nothing submitted 329576. The priority thread sat in `m_master.Wait(329576)` (`commandScheduler.cpp:644`), and
   after 2 s it printed `GpuWaitSlow role=4 requested=current`. The GPU was idle. Guest threads were blocked in
   `VideoOutIsFlipPending` on the same mutex (`videoOut.cpp:2577`) and on the flip/EOP events.
4. The stall ended when the presentation thread returned. It took the FrameTrace snapshot for 9672, fired the flip event,
   and released the mutex. GuestGpu's reserve went through, its flush submitted 329576, and the priority wait ended.
   That order is why the 2.975-s wait is counted in row n=9673. **No emulator timeout ends it.** The ~3 s is however
   long the presentation thread's blocking call lasted.

Every fact in §1 fits this chain, with no loose ends. Each of the other mechanisms asked about is either impossible by
the code or ruled out by the log (§4). Fixes are in §6. The root fix is to stop the present path from blocking
synchronously on the main thread while holding `VideoOutConfig::mutex`. The symptom fix is to flush the recording
buffer before the flip packet can block.

---

## 1. Facts from the log, and what each proves

| # | Fact (log) | Consequence |
|---|---|---|
| F1 | `GpuWaitSlow: role=4 requested=329576 known=329575 current=329576 ... submit_backlog=0 record_backlog=0 acopy=476880/476880/476880 acopy_pending=0` (L1257663) | `CurrentTick()` is the next tick to hand out (`masterSemaphore.h:19-21`), and it moves only through `NextTick` (`masterSemaphore.h:26-28`) inside `CommandScheduler::Submit`, at `commandScheduler.cpp:865` (async/record path) or `:938` (sync path). `requested == current` means **`Submit` was never called for 329576**. Everything already reserved was on the GPU and done (`known = current−1`, both backlogs 0, async copies all signalled). |
| F2 | The history ring (L1257664–L1258719, 512 entries) ends with render tick 329575 `returned` (L1258716–L1258719). It holds 7 present-scheduler submits (`scheduler=0x100008a3778 present=1`); the last, present tick 9728, sits **between render ticks 329547 and 329548**. | See F4. |
| F3 | FrameTrace n=9671 (L1257502): `submits=24`. n=9672 (L1258720): `dt_us=3032310 lat_us=3005002 submits=66 draws=9719 semwaits=47 semwait_us=53393 cpu_main_us=18317 cpu_gpu_us=55950 cpu_present_us=3751 cpu_proc_us=1062500 semwait_gpu_us=0`. n=9673 (L1258742): `dt_us=2965 lat_us=2404 submits=7 semwaits=1 semwait_us=2975432 draws=0 dispatches=146`. FrameTrace-wait for 9673 (L1258746): `other=2977138/2`. FrameTrace-submit for 9673 (L1258747): `flip=9/1 ...`. | Row n is cut when flip n is presented (`videoOut.cpp:1178`, snapshot at `:1237-1241`). `lat_us` = snapshot time − `reserve_host_ns` of the presented request (`videoOut.cpp:1256-1258`), and it is stamped in `FlipQueue::Reserve` (`videoOut.cpp:888`). |
| F4 | Present submits line up exactly with the windows. Present 9727 sits between render 329510 and 329511, and window 9671 = render 329488..329510 (23) + present 9727 = 24 ✓. Window 9672 = **render 329511..329575 (65) + present 9728 (1) = 66** ✓. | **Every** submit of window 9672, including the present submit of request 9672 itself, happened **before** the stall. That present submit was made ~37 render submits into the frame (≈ 30 ms), yet the snapshot of 9672 came 3 s later. **The presentation thread was blocked between its present submit and its snapshot.** |
| F5 | The 2.975-s wait is booked in row 9673, not 9672 (F3). | The semaphore-wait `Add` (`masterSemaphore.cpp:147-155`) on the priority thread came **after** the snapshot of 9672 (`FS::Read` under the registry mutex, `frameStats.cpp:214-223`). So 329576 completed only after the presentation thread had finished presenting 9672. |
| F6 | `lat_us(9672)=3.005 s` ≈ `dt`, but `lat_us(9673)=2.4 ms`, and 9673 was presented 2.965 ms after 9672. | Flip 9672 was reserved 27 ms into the frame; flip 9673 was reserved only **after** the stall. GuestGpu processed the 9673 flip packet only after the stall and then submitted it (`flip=9/1` in row 9673). A block **at or before** `FlipQueue::Reserve` of flip 9673 fits this. |
| F7 | The first guest line after the stall block is `flipPendingNum = 0` (L1258729), right after the 9672 FrameTrace lines. The guest logged nothing between guest time 05:08.913 and `GpuWaitSlow`. | `VideoOutIsFlipPending` logs after `GetFlipStatus`, which takes `cfg.mutex` (`videoOut.cpp:2577`, `:2956-2958`). A guest thread was blocked on that mutex and released when the presentation thread unlocked it (`videoOut.cpp:2564`). |
| F8 | `gpuclk_vbn113k.csv`: 0 % from 20:29:13.904 to 20:29:15.938, 38 % at 20:29:16.439. `cpuclk_vbn113k.csv` at t=312.051: `proc_cpu_s=1.3906` per 2 s and `busy_all=2.69 %`. Frame 9672: `cpu_gpu_us=55950`, `cpu_present_us=3751`, `cpu_main_us=18317`. | Nothing spun. GuestGpu, the presentation thread and the guest main thread were all blocked, not busy. `semwait_gpu_us=0` means GuestGpu did not wait on any master semaphore (`masterSemaphore.cpp:151-153`). |
| F9 | No `PresentTrace`, `WaitTrace`, `CsStall`, `Pause:`, swapchain-recreate, `AsyncPipelines` or `DrainTrace` lines near the stall. `PriorityStall`/`GpuIdlePrio` do not exist in this build. | No compile stall, no swapchain event, no pause. |

---

## 2. Who can wait on master `0xff62592a10` with `requested == current` (the belief, verified)

Master `0xff62592a10` belongs to scheduler `0xffa2a16148`: every `GpuSubmitHistory` line names both. That scheduler
is the GuestGpu render scheduler (`RecordThread: scheduler=0xffa2a16148 ... gpu=1`, L16427–L16428; one
`GraphicContext`, `vulkanWindow.cpp:1244`). `role=4` is `ThreadRole::Count`, i.e. unregistered
(`frameStats.h:1914`). Only the guest main thread (`runtimeLinker.cpp:1512`), GuestGpu (`graphicsRun.cpp:681`),
the presentation thread (`videoOut.cpp:797`) and record threads (`commandRecorder.cpp:955`) are registered.

| Waiter | Thread | Can it request == CurrentTick? |
|---|---|---|
| `PriorityOperationsThread` → `m_master.Wait(operation.tick)` (`commandScheduler.cpp:624-671`, wait `:644`) | `m_priority_thread`, a jthread created at `commandScheduler.cpp:296`; unregistered → role 4 | **Yes.** `DeferPriorityOperation` stamps `CurrentTick()` (`:589`), which is the unsubmitted recording tick. |
| `CommandScheduler::Wait` (`:443-458`) | GuestGpu (sanitizer `indirectArgsSanitizer.cpp:114`, fault buffer `faultManager.cpp:99`, stream wrap `streamBuffer.cpp:356`, host-read `bufferCache.cpp:1697`) | No. If `tick == CurrentTick` it submits first (`:446-453`). |
| `Finish` / `FlushAndWait` / `Shutdown` (`:432-441`, `:425-430`, `:347-390`) | GuestGpu (`graphicsRun.cpp:446,451,3137`, `bufferCache.cpp:337`, `renderContext.cpp:119,282`, `textureCache.cpp:1291`); shutdown | No. It submits, then waits `CurrentTick()−1`. |
| `MasterSemaphore::Wait(job.tick)` (`bufferCache.cpp:500`) | Guest thread, role 4 (or Main) | No. Reached only with `KYTY_STALE_READ=0` (`bufferCache.cpp:475-481`; the default serves a stale read and sends `ServeStaleRead` at `:487`), and `job.tick` was already flushed by `BeginAsyncReadback` (`:2112-2116`). No `download-async` submit site appears in any row. |
| `DescriptorHeap::~DescriptorHeap` (`descriptorHeap.cpp:41,45`) | Shutdown | No. |
| Present-scheduler waits (`swapchain.cpp:61,185,584`, `screenshot.cpp:403,527`) and the present scheduler's own priority thread | Presentation thread, GuestGpu in `FramePool::WaitForFrame`, present priority thread | Different master (the `present_scheduler`, `swapchain.cpp:343-344`). |

**Belief confirmed.** The only role-4 waiter that can request the recording tick of this master is the render
scheduler's `PriorityOperationsThread`.

---

## 3. The flush discipline: where priority ops are queued and what submits their tick

| Queued by (DeferPriorityOperation caller) | Thread | What submits that tick |
|---|---|---|
| EOP interrupt: `TriggerEopEventAtEndOfPipe` (`sync.cpp:298-305`, defer `:303`), from `RecordEndOfPipeWrite` (`sync.cpp:135-138`) and `WriteAtEndOfPipe` with selector 1 on the gfx queue (`graphicsRun.cpp:2546-2549`) | GuestGpu, PM4 | `BufferFlushLazy` (`graphicsRun.cpp:424-443`) only when ≥ 300 µs have passed since the last submit (`:440`). RELEASE_MEM: `pm4Handlers.cpp:2339-2340` (irq), `:2380-2381` (data_sel 1), `:2399-2402` (data_sel 5 only with selector 1); **data_sel 2/3 (`:2423`) never flushes**. The guaranteed backstop is the slice-end flush (`graphicsRun.cpp:1019`, `:1054`) or any earlier full flush. |
| Flip completion: `WriteAtEndOfPipeWithInterruptWriteBackFlip32` / `WithFlip32` / `OnlyFlip` (`sync.cpp:262`, `:280`, `:294`) | GuestGpu, flip packets | The flip's own `Flush` right after: `graphicsRun.cpp:3113`, `:3057`, `:3082`. |
| `ServeStaleRead` readback (`bufferCache.cpp:2211`) | GuestGpu (a command) | Its own `Flush` (`bufferCache.cpp:2235-2238`). The early returns (`:2139-2147`, `:2177-2190`) queue nothing. |
| `PrefetchHotReadbacks` (`bufferCache.cpp:2617`) | GuestGpu, slice end | Called only at `graphicsRun.cpp:1011` and `:1051`, each followed by the slice-end flush (`:1019`, `:1054`). |
| Image download (`textureCache.cpp:2914`) via `ProcessDownloadImages` (`:3455-3464`) or GC eviction (`:3428`), reached from `RenderContext::RunGarbageCollector` (`renderContext.cpp:395-413`) | GuestGpu | After a slice that made progress: the slice-end flush (GC at `graphicsRun.cpp:1003`/`:1049`, then flush `:1019`/`:1054`). FlipPreparation: `PrepareCpuFlip`'s flush (`:1067-1068` → `:3131`). The **no-progress** branches (`:1020-1025`, `:1055-1060`) have **no flush**. |

Consequence: outside the no-progress GC branches, a priority op can stay on the recording tick only while GuestGpu is
**inside** `GuestGpu::Process`, between the defer and that slice's flush. So a seconds-long unsubmitted op means one of
two things. Either GuestGpu blocked inside a packet handler before the flush (M1/M2 below), or the no-progress GC branch
ran (M3).

---

## 4. Candidate mechanisms

### M1 — the flip packet blocks on `VideoOutConfig::mutex` held by the presentation thread — **POSSIBLE; matches every fact**

Sequence:

1. **Presentation thread** (`PresentThread`, `videoOut.cpp:796-870`, `Flip(0)` at `:830`). `FlipQueue::Flip` locks
   `r.cfg->mutex` (`videoOut.cpp:1138`) and holds it until `:2564`. That covers `m_presenter.Present(*r.frame)`
   (`:1167`), the flip-status update, `Gates::Poll` (`:1180`), the FrameTrace snapshot and log lines (`:1237-2552`),
   `TriggerVideoOutEvents(Flip)` (`:2558`) and the `m_done_cond_var` signal (`:2561`). Inside `Presenter::Present`
   (`swapchain.cpp:838-909`) it acquires the image (`:849`), records and submits (`:862-880`, present tick 9728 in the
   ring), presents (`:883`), and then calls `UpdateTitle()` (`:903`). `UpdateTitle` → `RunOnMainThread`
   (`window.cpp:1093`) pushes a task and **waits with no bound** for the SDL main thread to run it (`window.cpp:784-787`).
   The main thread runs tasks only between events (`window.cpp:815-829`, `DrainMainThreadTasks` `:790-805`). This runs
   on **every** present.
2. **GuestGpu thread**, working through guest frame 9673. A RELEASE_MEM with interrupt queues `TriggerInterrupt` on tick
   329576, and its lazy flush is skipped (< 300 µs since the last submit, `graphicsRun.cpp:440`), or it is a data_sel 2/3
   interrupt, which has no flush at all (`pm4Handlers.cpp:2423`). Normal: `prio_unsub` ≈ 5.7 per frame in
   `vbn113m`/`vid113` (FACTS §1.5).
3. **Priority thread** takes that op at once, flags it unsubmitted (`commandScheduler.cpp:642`) and waits (`:644`).
4. **GuestGpu** reaches the flip marker `0x781` (`pm4Handlers.cpp:2221-2227`). `FlipWithInterrupt`
   (`graphicsRun.cpp:3085-3114`) writes the label (`:3104`) and calls `PrepareVideoOutFlip` (`:3106` → `sync.cpp:228-246`
   → `SubmitFlipFromGpu`, `videoOut.cpp:2872-2884` → `ReserveFlipRequest`). There it takes
   `Common::LockGuard lock(video_out->mutex)` (`videoOut.cpp:525`) and **blocks**. It has not reached `Reserve`
   (`:530`, stamp `:888`) and not reached the flip's `Flush` (`graphicsRun.cpp:3113`).
5. **Guest threads** block in `VideoOutIsFlipPending` → `GetFlipStatus` → `cfg.mutex` (`videoOut.cpp:2577`). They also
   wait for the flip event (fired only at `:2558`) and for the EOP interrupt.
6. After 2 s the priority thread prints `GpuWaitSlow`: requested == current, backlogs 0, GPU idle.

What ends it: the presentation thread's blocking call returns. For `RunOnMainThread`, that is the SDL main thread
getting back to `DrainMainThreadTasks`. `FlipQueue::Flip` then finishes: snapshot 9672 (`:1237`), FrameTrace lines,
flip event (`:2558`), done-signal (`:2561`), unlock (`:2563-2564`). The guest's `IsFlipPending` returns (F7). GuestGpu
gets the mutex and reserves flip 9673 (F6, `lat_us=2404`), queues its completion, and `Flush` (`graphicsRun.cpp:3113`)
submits 329576. The GPU runs it, the priority wait ends after the snapshot (F5), and the op runs. Flip 9673 is Ready
almost at once. The presentation loop's `total_wait` is deeply negative after a 3-s iteration (`videoOut.cpp:804-814`,
`:868`), so it does not sleep and presents 9673 **2.965 ms** after 9672 (F3).

Why it fits:

- F1: `Submit` was never called for 329576.
- F4: all 65 render submits of the window came before the stall, and the present submit of 9672 was early while its
  snapshot was 3 s late.
- F5 and F6: the snapshot/wait ordering and the `lat_us` pattern.
- F7: the guest's `IsFlipPending` returned right after the unlock.
- F8: every thread was blocked, not spinning; `semwait_gpu_us=0`.

Why the block must be at `videoOut.cpp:525`: it had to be inside `Process` and before the flip's flush (§3). It had to
depend on the presentation thread (F4/F5). And it had to be before `Reserve` (F6). The other presentation-dependent
waits inside the flip packet come **after** `Reserve`: `FlipQueue::Prepare` → `cfg->mutex` (`videoOut.cpp:992`),
`FramePool::Acquire` (`swapchain.cpp:109-111`), and the render mutex in `PrepareFrame` (`swapchain.cpp:756`). They would
have given `lat_us(9673)` ≈ 3 s. `WaitFlipDone` flushes before it blocks (`graphicsRun.cpp:2497`), so it could not have
left 329576 unsubmitted.

Where exactly the presentation thread blocked (between the present submit, `swapchain.cpp:879`, and the snapshot,
`videoOut.cpp:1237`):

| Call in that interval | Can it block ~3 s? | Verdict |
|---|---|---|
| `swapchain.Present()` → `queue_mutex` + `vkQueuePresentKHR` (`swapchain.cpp:883`, `:721-723`) | Driver/DWM | **Ruled out.** The 28 render submits 329548..329575 appear after present 9728 in the ring. Each took the same `queue_mutex` (`commandScheduler.cpp:140`; one `GraphicContext`, `vulkanWindow.cpp:1244`), and `vkQueuePresentKHR` runs right after the submit returns (`swapchain.cpp:879-883`). It released the mutex before them. |
| `screenshot.Finish` (`swapchain.cpp:897-899`) | Only when a screenshot was requested | Not this run. |
| **`UpdateTitle` → `RunOnMainThread`** (`swapchain.cpp:903`, `window.cpp:1052-1094`, `:766-788`) | **Yes, unbounded:** a cross-thread round trip to the SDL main thread on every present | **Prime suspect.** It is bounded only by whatever keeps the main loop from returning to `DrainMainThreadTasks`: a long `ProcessEvent`, message pumping inside `SDL_WaitEvent`/`SDL_WaitEventTimeout` (`hostInput.cpp:421-439`; Windows modal loops, slow WM_* handling, SDL joystick/HIDAPI enumeration). This log does not say which. |
| `frames.Release` (`swapchain.cpp:904`, `:165-180`) | Pool mutex; GuestGpu never holds it while waiting (`:109-111`) | No. |
| `FlipQueue::m_mutex` (`videoOut.cpp:1171`) | Holders: Reserve, Prepare, Wait (released during the condvar wait), Complete — all short. Lock order cfg → m_mutex everywhere. | No. |
| `Gates::Poll` → `fopen`/`fread` of `KYTY_GATE_FILE` on **every flip** (`videoOut.cpp:1180`, `gates.cpp:583-611`) | File I/O; bounded by the OS | Second suspect, only if the file system stalled. |
| `KernelSetGuestSpeed`, `VulkanLogMemoryStats` (only every 300 flips: 9672 % 300 ≠ 0), `FS::Read` | Short | No. |

Distinguishing signals:

- Stall row with `lat_us ≈ dt_us`; the next row with tiny `dt_us` and `lat_us`.
- The stall row's `submits` all precede the stall, which you can check against the ring's present-scheduler entries.
- `semwait_gpu_us = 0`.
- Session-113 instrument: `prio_stall ≥ 1`. `PriorityStall: tick=<T> unsub=1 us≈3e6 site=+0x…` names the op's caller:
  the return address inside `TriggerEopEventAtEndOfPipe` or the RELEASE_MEM path. **`gw_idle_prio = 0` and no
  `GpuIdlePrio:` line**, because GuestGpu is not idle; it is inside `Process`.
- `KYTY_GPU_WALL=1`: `gw_proc_ns` ≈ 3 s in the stall row (GuestGpu inside `Process`), not `gw_idle_ns`/`gw_blk_ns`.
- `KYTY_PRESENT_TRACE=1`: the `PresentTrace: present … present_us=` line (`swapchain.cpp:884-892`) prints right after
  `vkQueuePresentKHR`. If it shows up on time while the FrameTrace row is 3 s late, the block is after presentKHR:
  `UpdateTitle`, `Release` or `Gates::Poll`.

### M1′ — the same with CPU flips (FlipPreparation) — **POSSIBLE (not this event)**

`SubmissionType::FlipPreparation` runs the GC first (`graphicsRun.cpp:1067`, which can queue image downloads at
`textureCache.cpp:2914`). It then calls `PrepareCpuFlip` → `PrepareFlip` → `FlipQueue::Prepare`, which takes
`cfg->mutex` (`videoOut.cpp:992`) and `FramePool::Acquire`, all **before** the flush at `graphicsRun.cpp:3131`. Same
shape as M1, with the op's site in the texture cache. ASTRO BOT uses GPU flips here (site `flip`, never `cpu-flip`).

### M2 — a synchronous `Submit` blocked before `NextTick` — **POSSIBLE in general; ruled out here**

A sync submit (`allow_async=false`, a present, or caller semaphores — `commandScheduler.cpp:854-855`) does
`DrainAsyncSubmits` (`:926` → `DrainRecordQueues` `commandRecorder.cpp:1045-1050` + `AsyncSubmitter::Drain`
`commandScheduler.cpp:110-122`) and takes `queue_mutex` (`:937`) **before** `NextTick` (`:938`). If GuestGpu blocks there
(for example behind a `vkQueuePresentKHR` holding `queue_mutex`, `swapchain.cpp:721-723`), `CurrentTick` stays equal to a
tick that already carries priority ops. GuestGpu's sync submits are `FlushAndWait`, `Finish`, and `Wait(current)`.
Ruled out for `vbn113k`: there is no present submit after tick 9728 in the ring, so no `vkQueuePresentKHR` could hold the
mutex during the stall; `record_backlog=0`; `submit_backlog=0`. Signal: same `GpuWaitSlow` shape, but `PresentTrace`
would show a long `present_us`.

### M3 — the no-progress GC branch, then GuestGpu goes idle — **IMPOSSIBLE in practice (latent)**

Sequence: a `Process` call with `progressed == false && complete == true` runs `RunGarbageCollector`
(`graphicsRun.cpp:1020-1025`, `:1055-1060`), which can queue an image download (`textureCache.cpp:2914`). There is no
flush. ThreadRun then idles at `graphicsRun.cpp:694-703` (no timeout) or sleeps in the all-blocked loop (`:723-755`,
100-ms `WaitFor` at `:737`, which never flushes). The op waits until new work arrives.

Why unreachable: every executed packet sets `m_made_progress` (`graphicsRun.cpp:1977`, `:1994`, `:2029`, `:2070`); a
suspended handler that later passes sets it on resume. "Complete without progress" therefore needs an empty command
span, and both entry points reject empty spans (`graphicsRun.cpp:193-195`, `:209`).

What would end it: any `Enqueue` or `SendCommand` (`graphicsRun.cpp:667`, `:155`). A stale read's `ServeStaleRead`
flushes (`bufferCache.cpp:2237`); a progressing slice flushes at the slice end.

Signal: `GpuIdlePrio: where=idle|blocked site=+0x<textureCache>` and `gw_idle_prio > 0`.

### M4 — ThreadRun's idle wait or all-blocked sleep on its own — **IMPOSSIBLE**

The idle wait (`graphicsRun.cpp:694-703`) and the blocked sleep (`:723-755`) are reached only after `Process` returned or
a command ran. Every progressing slice has flushed by then (`:1019`, `:1054`). A slice that suspended on its first packet
queued nothing except through the command pump (`:1967-1969`), and the commands flush (M6). So neither wait can start
with an unsubmitted op unless M3 happened.

### M5 — the lazy RELEASE_MEM flush alone — **IMPOSSIBLE as a cause (it is the precondition)**

A skipped lazy flush (`graphicsRun.cpp:440`) leaves the interrupt for the next flush. At worst that is the slice end
(`:1019`/`:1054`), and before a flip it is the flip's flush (`:3113`). The delay equals the rest of the slice: normally
µs–ms (`prio_unsub` ≈ 5.7 a frame with `prio_stall` 0 in `vbn113m`/`vid113`). It becomes seconds only if the slice
blocks before its flush (M1/M2).

### M6 — commands in `m_commands` — **IMPOSSIBLE**

The complete list of `SendCommand`/`SendCommandSync` users:

| Command | Behaviour |
|---|---|
| `ReadMemoryOnGpu` (`bufferCache.cpp:480`) | Calls `DownloadBufferMemory`, which does `Finish` + `WaitPriorityOperations` (`:337-338`). |
| `ServeStaleRead` (`:487`) | Flushes whenever it queues (`:2235-2238`). |
| `BeginAsyncReadback` / `FinishAsyncReadback` (`:494`, `:503`; only with `KYTY_STALE_READ=0`) | `Flush` (`:2113-2116`) / applies bytes. |
| Host-read wait (`:1709`) | `Wait` submits the current tick (`:1697`). |
| `ApplyReadbackPieces` (`:2228`, `:2636`) | Records no GPU work. |
| `ReleaseGuestStack` (`renderContext.cpp:233`) | `InvalidateMemory` → `ReadMemory` inline → `Finish`. |
| `UnmapMemory` (`renderContext.cpp:297`) | `Finish` + `WaitPriorityOperations` (`:282-283`). |

Commands run either in ThreadRun (`graphicsRun.cpp:772-787`) or from the pump between packets (`:1967-1969`). None
leaves a priority op unsubmitted.

### M7 — WAIT_REG_MEM / SuspendPm4 circular wait — **IMPOSSIBLE on its own**

A suspended slice (`graphicsRun.cpp:545-550`, `:2062-2066`) returns. If it progressed, it flushed (`:997-1019`); if it
did not, it queued nothing. Labels are written by the CPU at parse time (`graphicsRun.cpp:2570`, `:3104`), so a guest
waiting on a label is not held by an unsubmitted tick. A wait on an **interrupt** would be, but that needs an unflushed
interrupt, i.e. M1/M2/M3 first. The 100-ms sleep (`:737`) only clears `blocked` (`:749-753`) and never flushes.

### M8 — the record thread / async submit thread ("submitted" is only "reserved") — **POSSIBLE in general; IMPOSSIBLE for this event**

With `recordthread=1`, `Submit` reserves the tick on GuestGpu (`commandScheduler.cpp:865`) and hands the buffer over
(`EndRecorded`, `:880`). The record thread ends it and queues it (`EnqueueAsyncSubmit`, `:203-220` → `EnqueueReserved`,
`:97-108`), and the submit thread calls `vkQueueSubmit` (`:125-181`, `:162`). A buffer can therefore sit reserved but not
yet submitted. That produces `requested < current` with `record_backlog`/`submit_backlog > 0`. The event had
`requested == current` and both backlogs 0.

`DrainRecordQueues` from another thread waits only for the published head, never for an unended buffer
(`commandRecorder.cpp:520-533`), so the present path cannot deadlock on GuestGpu's open buffer.

### M9 — a guest-thread readback wait — **IMPOSSIBLE here**

See §2: it needs `KYTY_STALE_READ=0`, and its tick is flushed before the wait.

### M10 — GuestGpu `WaitPriorityOperations` deadlock — **IMPOSSIBLE**

Every GuestGpu call submits and completes the tick first:

- `bufferCache.cpp:337-338`
- `renderContext.cpp:282-283`
- `streamBuffer.cpp:356-359`
- `commandScheduler.cpp:550`, which runs only for free ticks (`:543-545`)

The FIFO is in tick order because all defers happen on GuestGpu with a monotonic `CurrentTick()`. A permanent deadlock
would also not end after 3 s.

### M11 — GuestGpu blocked in `WaitFlipDone` — **IMPOSSIBLE as the unsubmitted-op cause**

`WaitFlipDone` flushes before `FlipQueue::Wait` (`graphicsRun.cpp:2495-2501`). The tick left open while it waits is empty
and nothing can queue on it while GuestGpu is blocked. (It can still hold GuestGpu while the presentation thread is
slow, but without a `GpuWaitSlow`.)

---

## 5. Why the existing session-113 instrument alone would not have named M1

`gw_idle_prio` (`graphicsRun.cpp:339-351`, called at `:697` and `:731`) looks only where GuestGpu goes idle or blocked
in ThreadRun. In M1, GuestGpu is blocked **inside a packet**, so it stays 0. `prio_stall`/`PriorityStall`
(`commandScheduler.cpp:651-659`) will fire and name the queuing site, but not the blocker. See §7 for what to add.

---

## 6. Ranked mechanisms and fixes

| Rank | Mechanism | Verdict | Minimal fix | Risk |
|---|---|---|---|---|
| **1** | **M1**: the presentation thread blocks while holding `VideoOutConfig::mutex` (`videoOut.cpp:1138…2564`), with `UpdateTitle` → `RunOnMainThread` (`swapchain.cpp:903`, `window.cpp:784-787`) as prime suspect. GuestGpu blocks in `ReserveFlipRequest` (`videoOut.cpp:525`) before the flip's flush, leaving a lazy EOP interrupt on the recording tick. | **POSSIBLE; fits F1–F9** | **(a) Root:** make the title update non-blocking. Post it to the main thread without waiting, or have the main loop set the title from an atomic fps/frame value about once per second, and never call it inside the `cfg->mutex` region. **(b)** Stop holding `cfg->mutex` across `m_presenter.Present` (and `Gates::Poll`): unlock after `IsFlipDueLocked` and the state change (`:1139-1153`), then relock before the status update (`:1178`). Closing already waits on `m_processing` (`videoOut.cpp:917-919`). **(c) Symptom:** in `FlipWithInterrupt`/`Flip`/`Flip(addr)`/`PrepareCpuFlip`, flush before `PrepareVideoOutFlip`/`PrepareFlip` (`graphicsRun.cpp:3106/3051/3075/3129`) when priority ops were queued since the last submit. A counter bumped in `DeferPriorityOperation` and reset in `Submit` is cheaper than the try-lock query. | (a) Very low: title text only. (b) Medium: flip-status reads, generation and close must be rechecked after the relock; guests may see pre-present status while a present is in flight (hardware-like). (c) Low: at most one extra submit per flip (~12 µs host, `graphicsRun.cpp:418-423`), and the flip copy moves to the next buffer on the same queue. **(c) alone does not remove the 3-s hitch:** the guest still blocks in `IsFlipPending` and waits for the flip event. It only removes the unsubmitted-tick wait and lets EOP interrupts through. |
| 2 | M1′: CPU flips (FlipPreparation GC → `Prepare`, before `graphicsRun.cpp:3131`) | POSSIBLE, not this event | Covered by (b) and (c). Also flush after the GC at `graphicsRun.cpp:1067`. | Low |
| 3 | M2: a sync `Submit` blocked before `NextTick` (`commandScheduler.cpp:926-938`) | POSSIBLE in general; ruled out by the ring | Take the tick before blocking, or keep `vkQueuePresentKHR` off `queue_mutex` contention (present from the submit thread). | Medium |
| 4 | M3: the no-progress GC branch, then idle | Reachable only with empty spans, which the entry points reject | `cp.BufferFlush()` after `RunGarbageCollector` at `graphicsRun.cpp:1024` and `:1059`. Defence in depth: before the idle `Wait` (`:702`) and the blocked `WaitFor` (`:737`), when `UnsubmittedPriorityOperation` reports an op, drop `m_queue_mutex`, flush, relock and re-check. | Very low (dead path today); the ThreadRun flush must run outside `m_queue_mutex` and only when the scheduler is Active with a valid buffer. |
| — | Bounded wait in `PriorityOperationsThread` that asks GuestGpu to flush (`SendCommand`) | **Ineffective for M1.** Commands run only between packets (`graphicsRun.cpp:1967-1969`) or in ThreadRun (`:709-787`), and GuestGpu is stuck inside one. The priority thread cannot flush itself: GuestGpu owns the buffer. Helps only M3. | — | Medium for little gain |
| — | M4–M11 | IMPOSSIBLE (or ruled out) by the code | none | — |

---

## 7. How to confirm M1 at the next occurrence

**Existing switches:**

- `KYTY_PRESENT_TRACE=1`: the `PresentTrace: present` line is printed right after `vkQueuePresentKHR`
  (`swapchain.cpp:884-892`). On time, with the FrameTrace row late, means the block is after presentKHR.
- `KYTY_GPU_WALL=1`: `gw_proc_ns` ≈ stall length.
- The session-113 counters: `prio_stall=1` with a `PriorityStall … unsub=1` site in the EOP path, and `gw_idle_prio=0`.

**Proposed instrument (small, no behaviour change):**

1. Time `RunOnMainThread`'s wait (`window.cpp:784-787`) and log `MainThreadWait: us=` above 50 ms, together with the
   last SDL event type the main loop handled.
2. Time the `cfg->mutex` hold in `FlipQueue::Flip` (`videoOut.cpp:1138…2564`), split into Present, title, `Gates::Poll`
   and snapshot/log; log `FlipHold:` above 50 ms.
3. In `ReserveFlipRequest` (`videoOut.cpp:525`), `FlipQueue::Prepare` (`:992`) and `GetFlipStatus` (`:2577`), try the
   lock first and time the blocking lock. Log `CfgMutexWait: site= us=` above 50 ms.

(1) and (2) name the blocker; (3) proves GuestGpu's and the guest's side of the chain.
