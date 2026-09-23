# Route A, Stage 3 (`RecordCtx` at N = 1): inventory and first milestone M3.1

Source: HEAD `eccc6ea`. Tags: **[M]** measured in a named run; **[I]** read from source or derived; **[U]** unknown.

## 0. Bottom line

The draw path already passes an explicit `CommandBuffer& buffer` from `graphicsRun.cpp:2125/:2397/:2465` into `DrawIndex`/`DrawAuto`/`DispatchDirect` → `ExecutePreparedDraw` → `CommitBindings` [I]. But `CommandBuffer` does not know its owner or its tick: its constructor drops the scheduler (`context.cpp:89`). Every stage therefore reaches back to the global `m_context.GetCommandScheduler()`. The smallest first milestone follows from that: **the buffer carries its owner and its tick, and the resolve path reads them from it.** It saves nothing and produces one new number, the count of mid-draw submits.

## 1. Inventory

### 1.1 The implicit tick

`CurrentTick()` appears on 43 lines: 39 call sites, 2 definitions (`commandScheduler.h:70`, `masterSemaphore.h:19`) and 2 comments. This is the review's "~43"; DESIGN_82's "38" is older [I].

| Role | N | Sites |
|---|---|---|
| **Ownership stamp** | 17 | `commandScheduler.cpp:253` pool, `:692/:703` begin, `:539/:558` deferred ops, `:668` mark; `descriptorHeap.cpp:59/:153`; `streamBuffer.cpp:320`; `indirectArgsSanitizer.cpp:116`; `faultManager.cpp:225`; `bufferCache.cpp:330, 1064, 1548, 1607, 2095`; `renderContext.cpp:280` |
| **Wait for everything so far** | 6 | `commandScheduler.cpp:368, 433, 439, 440`; `swapchain.cpp:61`; `bufferCache.cpp:1680` |
| **Age clock** | 6 | `textureCache.cpp:993, 2108`; `descriptors.cpp:1499`; `colorRenderTarget.cpp:159`; `depthRenderTarget.cpp:323`; `bufferCache.cpp:1518` |
| Diagnostics | 10 | `graphicsRun.cpp:1114`; `descriptors.cpp:4230`; `commandScheduler.cpp:685, 741`; `bufferCache.cpp:1710, 2191`; `gpuCheckpoints.cpp:525, 607`; `masterSemaphore.cpp:112, 134` |

The age-clock sites must **not** become per-context ticks. With N timelines, `tick − tick_accessed_last > NumFramesBeforeRemoval` (`textureCache.cpp:993`) would compare numbers from different timelines, so these sites need one global clock [I]. Around 25 tick consumers (`IsFree`/`KnownGpuTick`) are bound to one semaphore in the same way [I].

### 1.2 State reached by the resolve path

**(a) Per-context (duplicate)**
- `CommandScheduler` (`renderContext.h:82`): semaphore, pool, `m_command`, op queues, timestamp slot, `m_last_submit_ns`, profiler, recorder (`commandScheduler.h:136-168`).
- `DescriptorHeap` (`:83`): bound to the semaphore at `renderContext.cpp:92`, with no synchronisation.
- `RenderExecutor` scratch, memo and fast views (`render.h:357-425, :545, :565`).
- The sanitizer (`render.h:393`), bound when lazily created (`renderDraw.cpp:2455`).
- The **four `StreamBuffer`s**: they are members of the *shared* `BufferCache` (`bufferCache.h:305-316`) and each one holds a scheduler (`streamBuffer.h:104`).
- CP register context and `GetScheduler()` (`commandProcessor.h:173-201`).
- `g_last_slice_*` (`graphicsRun.cpp:1054`).
- The program-memo slice (`pipelineCache.cpp:3127, :4086, :2129`).

**(b) Shared, read-mostly (lock/epoch)**
- Pipeline maps (`pipelineCache.h:315`; creates `:4655/:4896/:5026`).
- `SamplerCache` (`samplerCache.h:55`).
- Mapped ranges (`renderContext.h:89`).
- **Unguarded** BDA epochs (`:95-97`).
- `m_const_ram` (`commandProcessor.h:189`).
- `GpuDirtyGen`, relaxed (`gpuDirtyGen.h:34-41`).

**(c) Shared and mutating: the real serialisers**
- **Render mutex** (`renderContext.h:80`): `renderDraw.cpp:2989/:3160`, `renderCompute.cpp:284`, `graphicsRun.cpp:886/:2770`, `swapchain.cpp:756/:797/:862`, `renderDoc.cpp:226`.
- **`PipelineCache::m_mutex` on the draw:** `GetGraphicsPrograms` (AheadTake) `:4541`, `QueueDrawAhead :4588`, `GetComputeProgram :4610`, `GetGraphicsPipeline :4655`.
- **Objects that captured the scheduler at construction** and record into `m_scheduler.Current()`:
  - `TextureCache` (`textureCache.h:285`, `m_lock :286`) and `BufferCache` (`bufferCache.h:256`).
  - **Every `Image`** (`image.h:237`). `Transit` calls `m_scheduler.EndRendering()` even when it is given a handle (`image.cpp:259-270`); there are 22 callers.
  - `Buffer`, `BlitHelper` (`blitHelper.h:43`), `TileManager` (`tiler.h:157`), `IndirectArgsSanitizer` (`:53`) and `FaultManager` (`faultManager.h:30`).
- **Deferred/priority ops** (`commandScheduler.cpp:534-560`): popped at draw entry *before* the mutex (`renderDraw.cpp:2972/:3145`, `renderCompute.cpp:267`) and produced by the caches, `sync.cpp:262-303` and `tiler.cpp:144`.
- **Tick issue and queue order:** `NextTick` at `commandScheduler.cpp:77/:785/:856`.
- **Recorder ring**: sticky single producer (`commandRecorder.cpp:317-326`).

Precedent: `present_scheduler` (`swapchain.cpp:381`) already runs a second timeline on the same queue [I]. Yet `CommandBuffer`'s own `context.cpp:203/:361/:449` name the *render* scheduler: a latent wrong owner, in diagnostic modes only [U].

## 2. Milestone M3.1: the command buffer names its owner

**Invariant** [I]: the render tick moves only through `NextTick` inside `Submit`. `Submit` clears `m_active`, and every renderer `Submit` is followed by `BeginNext` → `BeginCommand` (`commandScheduler.cpp:398-448, :1024`). So while `buffer` is active, `CurrentTick()` is the tick it will signal, which is exactly the assumption at `:690`.

**Changes (≈150–200 lines; nothing under `src/graphics/shader/**`, so the translation cache stays warm):**

1. **`render.h` `CommandBuffer`.** Add `CommandScheduler* m_scheduler`, `uint64_t m_tick`, `Scheduler()` and `Tick()`. `context.cpp:89` keeps the scheduler, and `CommandScheduler::BeginCommand` sets `m_command.m_tick = CurrentTick()` for both the direct and the recorded path.
2. **Unconditional `buffer.Scheduler()`** (the same object at N=1):
   - all 15 sites in `renderDraw.cpp` (`AcquireRenderTargets`, the two breadcrumb helpers, `ExecutePreparedDraw`, and `PopPendingOperationsLazy` in `DrawIndex`/`DrawAuto`);
   - all 7 in `renderCompute.cpp` (`DispatchDirect`);
   - `depthRenderTarget.cpp:459`;
   - `descriptors.cpp:1959`.
3. **Explicit ownership tick.** `DescriptorHeap::Commit/CommitRing(layout, tick)` replace `descriptorHeap.cpp:59/:153`, with callers at `descriptors.cpp:3970/:4010`. `MergeCostCensus` gets a `tick` parameter (`:4230`). The tick source is chosen by the new knob **`ctxtick`** (`KYTY_CTX_TICK`, appended last, `check_gate_order.py`):
   - 0: the old expression (default when landed);
   - 1: `buffer.Tick()`;
   - 2: 1 plus verification;
   - 3: 2 plus `EXIT`.
4. **Named age clock.** `RenderContext::AgeTick()` (still the render `CurrentTick()`) at `colorRenderTarget.cpp:159`, `depthRenderTarget.cpp:323` and `descriptors.cpp:1499`. Behaviour is identical; the class simply becomes visible in the code.
5. **Verification at `ctxtick ≥ 2`** (`FrameTrace-x`, raw):
   - `ctx_chk_n` and `ctx_chk_bad` check `&buffer.Scheduler() == &m_context.GetCommandScheduler()`, `&buffer == &Current()` and `Tick() == CurrentTick()` at entry and at each ownership site. Up to 40 lines of `CtxCheck: MISMATCH site=` are printed.
   - `ctx_midsub` counts `Submit` calls while a thread-local "inside a draw/dispatch" flag, set after the mutex, is up. The existing `SubmitSites` table names the site.
   - `ctx_rec_block` counts `CommandScheduler::Wait/Finish/FlushAndWait`, synchronous `Submit`, `MasterSemaphore::Wait`, `DrainAsyncSubmits` and `SendCommandSync` when called from a `CommandRecorder` thread (thread-local role flag). The priority thread is exempt because it waits legitimately (`:590`).

**Left for M3.2** (no `buffer` in the bind phase): `descriptors.cpp:313/:1774` (`NativeStorageBuffer`, `NativeUpload`) and the 57 stream-ring call sites.

**Acceptance (sealed in `pred/` before any run):**
1. Build passes; `check_gate_order.py` is clean; `git diff --stat src/graphics/shader` is empty. A script counts `GetCommandScheduler()`/`CurrentTick()` in the five executor files: **30 → 2**, with only `descriptors.cpp:313/:1774` remaining.
2. `shader_cfg_tests` fails exactly the known s104 set (HANDOFF §4).
3. Verify run at `ctxtick=2` in Sky Garden, 300 s:
   - `ctx_chk_bad = 0` and `ctx_rec_block = 0`;
   - `ctx_chk_n` per frame ≥ draws + dispatches (proof it was armed);
   - **publish `ctx_midsub`/frame by site**, the first datum Stage 5 needs.
4. Sealed ABBA `ctxtick=0|1`, 900 s, pinned, `gates_base.txt`, six standard controls. The criterion is a point estimate |Δ`cpu_net`| ≤ 90 µs, with Δ`dt` and 2·SE reported. From `dwk104` (2·SE 115 µs at 600 s), 900 s gives ≈94 µs, so a true zero fails ≈6 % of the time [I]. This is not a proof of equivalence.
5. Screen (not a measurement) against `61ae7347…` with the `reg104` protocol: flag CPU/draw above +2 %. This is the only view of a constant cost that both ABBA arms share.
6. Video at `ctxtick=1`: ≥3000 frames and 0 single-frame glitches (`s20_vidglitch.py`).
7. Ten entries at `ctxtick=2`, a smoke test only: P(0 hangs | 6.67 %) = 0.50. Write the rule first: a hang with the historical BVH signature (`GpuHangAbort role=4`, nvlddmkm 153) does not fail; any other signature does. The ≥60-entry test closes Stage 3, not M3.1.

**On pass:** record the decision in ROADMAP, then set the default to 1. Delete the old branch in M3.2.

## 3. Risks: how M3.1 could become non-neutral

1. **Mid-operation rollover.** Some calls submit `m_command` and begin a new one inside a draw or dispatch: the sanitizer slot wait (`indirectArgsSanitizer.cpp:112-114`, acknowledged at `renderCompute.cpp:940`), the stream wrap (`streamBuffer.cpp:356`), `DownloadBufferMemory` (`bufferCache.cpp:330-333`), the forced host read (`:1680-1693`), `FaultManager` (`:100`) and unmap (`renderContext.cpp:280`). After any of them `buffer` is the same object with a **new** tick. The old code re-reads the tick at each use. A hoisted `auto t = buffer.Tick()` would stamp a descriptor set with an already-submitted tick, and the set would then be reused under the GPU. The corruption is silent.
   - Detection: compare at the use site (knob 2) and count `ctx_midsub`.
   - Review rule: no tick in a local across a call.
2. **Stale window** between `Submit` (tick has advanced) and `BeginNext`. No converted site runs inside it [I]. Knob 2 asserts `m_active` inside `Tick()`.
3. **Deferred and priority stamps.** `:539/:558` are untouched. They carry the s81 entry-hang signature and belong to M3.4 with their own A/A. M3.1 only reroutes `PopPendingOperationsLazy`, which lands on the same object.
4. **Constant cost** (layout and inlining in `ExecutePreparedDraw`) falls in both arms, so only screen 5 sees it.
5. **Uncovered modes:** checkpoints (the direct `:253` path stays implicit), `m4baton`, RenderDoc and `KYTY_GPU_TIME`. A knob flip in the middle of a draw is harmless: both sources are equal, and knob 2 checks both.

## 4. Next milestones (one session each, each with its own A/A)

- **M3.2:** bind phase and `StreamBuffer::Commit(tick)`.
- **M3.3:** `Image`, `Buffer`, `Blit`, `Tiler` and the sanitizer take a `CommandBuffer&`.
- **M3.4:** shared-cache stamps carry (ctx, tick); wait-for-everything becomes a join.
- **M3.5:** `struct RecordCtx`, `MaxCtx = 1`.
