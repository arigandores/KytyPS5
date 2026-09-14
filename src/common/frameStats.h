#ifndef KYTY_COMMON_FRAMESTATS_H_
#define KYTY_COMMON_FRAMESTATS_H_

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

// KYTY_FRAME_TRACE=1 (or KYTY_AV_TRACE=1): per-flip breakdown of where the emulator spends its
// time. Cheap global counters are accumulated by the hot paths (GuestGpu thread, submits, waits,
// draws, dispatches, page faults, GPU timestamps) and FlipQueue::Flip logs the deltas since the
// previous flip as a "FrameTrace:" line next to "AvTrace: flip".
namespace Common::FrameStats {

enum class Counter : uint32_t {
	GpuThreadProcessNs, // GuestGpu thread inside Process()/commands (PM4 parsing + renderer)
	GpuThreadIdleNs,    // GuestGpu thread waiting for work (queues empty)
	GpuThreadBlockedNs, // GuestGpu thread sleeping with every queue blocked (WAIT_REG_MEM)
	SubmitNs,           // CommandScheduler::Submit (vkQueueSubmit + bookkeeping)
	Submits,
	SemWaitNs, // MasterSemaphore::Wait actually blocking in vkWaitSemaphores
	SemWaits,
	DownloadNs, // BufferCache::DownloadBufferMemory (GPU -> CPU readback drains)
	Downloads,
	DrawNs, // RenderExecutor::DrawIndex/DrawAuto (host side)
	Draws,
	DispatchNs, // RenderExecutor::DispatchDirect (host side)
	Dispatches,
	FaultNs, // resolved host page faults (memory tracker)
	Faults,
	WaitRegMemStalls, // WAIT_REG_MEM packets that suspended a queue
	GpuBusyNs,        // GPU execution time of completed command buffers (timestamp queries)
	GpuMeasured,      // number of command buffers measured
	FaultGpuNs,       // page faults taken by the GuestGpu thread itself (subset of FaultNs)
	FaultsGpu,
	SemWaitGpuNs,   // semaphore waits on the GuestGpu thread (subset of SemWaitNs)
	PriorityWaitNs, // CommandScheduler::WaitPriorityOperations blocking
	PriorityWaits,
	DmaNs, // CommandProcessor::DmaData (CopyBuffer/FillBuffer on the host)
	Dmas,
	LogNs, // Log::Write (formatting excluded, sink write included)
	Logs,
	LogGpuNs, // Log::Write on the GuestGpu thread
	// Draw path breakdown (RenderExecutor::DrawIndex/DrawAuto)
	DrawPopNs,       // PopPendingOperations
	DrawCheckNs,     // hw_check
	DrawTargetsNs,   // PrepareDrawRenderState (render target resolution)
	DrawProgramsNs,  // RefreshShaders (GetGraphicsPrograms)
	DrawBindingsNs,  // PrepareGraphicsBindings
	DrawVertexNs,    // vertex + index buffers
	DrawAcquireRtNs, // AcquireRenderTargets
	DrawPipelineNs,  // CreateGraphicsPipeline (lookup)
	DrawCommitNs,    // CommitBindings (descriptors)
	DrawEmitNs,      // dynamic state, begin rendering, vkCmdDraw*, barriers
	// Dispatch path breakdown (RenderExecutor::DispatchDirect)
	DispatchPopNs,
	DispatchProgramNs,
	DispatchPipelineNs,
	DispatchBindingsNs,
	DispatchCommitNs,
	DispatchEmitNs,
	// Program lookup breakdown (PipelineCache::GetGraphicsPrograms/GetComputeProgram)
	ProgPrepareNs,     // PrepareProgram: shader map, AGC metadata, attribute tables, hash
	ProgKeyNs,         // BuildStageStaticKey + unordered_map find
	ProgMaterializeNs, // MaterializeResources (SRT walk over guest memory)
	ProgPermNs,        // permutation search
	ProgReads,         // live guest memory reads during the SRT walk
	ProgCleanReads,    // GPU-clean guest memory reads (specialization)
	// MaterializeResources breakdown
	MatEvalNs,     // EvaluateRuntimeSources (SRT expression evaluation + reads)
	MatAssembleNs, // rest of MaterializeSnapshot (indirect images, vectors)
	MatSpecNs,     // BuildResourceSpecialization
	MatEvalInsts,  // Evaluator::EvaluateInst calls
	MatFailures,   // Evaluator::RecordFailure calls (each formats a string)
	MatMemoHits,   // materialization reused (same user data, same descriptor memory)
	MatMemoMisses,
	MatReadNs,     // time inside the SRT memory-read callback
	MatEvalWide,   // Evaluator::EvaluateWide calls (including immediates and memo hits)
	BindResolveTexNs, // RenderExecutor::ResolveTexture
	BindResolveTex,
	BindFindTexNs, // TextureCache::FindTexture (image views) in RebindImages
	BindFindTex,
	BindBuffersNs, // NativeStorageBuffer (including ObtainBuffer and aligned copies)
	BindSamplersNs,
	BindBufFindNs,   // FindBuffers (descriptor decode + BufferCache::FindBuffer)
	BindBufObtainNs, // BufferCache::ObtainBuffer called from NativeStorageBuffer
	BindBufSyncNs,   // BufferCache::SynchronizeBuffer (all callers)
	BindBufUploadNs, // NativeUpload of the flattened SRT / shader data
	BindBufN,        // storage buffer bindings
	BindTexMemoHits, // ResolveTexture served from the memo
	RtMemoHits,      // colour/depth target resolution served from the memo
	ObtainBufNs,     // BufferCache::ObtainBuffer (all callers)
	ObtainBufs,
	SyncBufUploads,  // SynchronizeBuffer copies issued
	LockSpinNs,      // TrackingSpinLock contended acquisitions (spin time)
	LockSpins,
	LockSpinGpuNs,   // ... on the GuestGpu thread
	GlobalBarriers,  // CommandProcessor::EmitGlobalBarrier (all-commands memory barrier)
	ImageBarriers,   // vkImageMemoryBarrier2 records issued by Image::Transit
	ShaderWriteBarriers, // ShaderWriteBarrier after draws with buffer writes
	RenderPassBegins,    // CommandScheduler::BeginRendering
	PendingOps,          // deferred operations run by PopPendingOperations
	PendingOpsNs,
	GlobalBarriersSkipped, // EmitGlobalBarrier with nothing recorded since the previous one
	FaultMainNs,           // page faults taken by the guest main thread (subset of FaultNs)
	FaultsMain,
	ImgInserts,      // TextureCache::InsertImage (new host image)
	ImgFrees,        // TextureCache::FreeImage
	ImgUploads,      // TextureCache::UploadImage calls
	ImgUploadBytes,  // guest bytes uploaded to images
	ImgUploadNs,     // time inside UploadImage (tiler + copy record)
	ImgInitNs,       // time inside InitializeImage (includes UploadNs)
	ImgCopyNs,       // guest -> staging copy of image data (ObtainBufferForImage)
	CbankCopyCpu,    // const-bank ranges copied to the stream ring from guest memory (misaligned base)
	CbankCopyGpu,    // ... copied on the GPU (range written by the GPU)
	CbankCopyBytes,
	AsyncCopyWaitNs, // WaitAsyncCopies before vkQueueSubmit (guest -> staging copies still running)
	AsyncCopyWaits,  // ... submits that had to wait
	ProtectNs,       // synchronous host page-protection changes (VirtualProtect) on the caller
	ProtectPages,
	ProtectWorkerNs, // ... applied by the deferred-protection worker (PageManager)
	ProtectWorkerPages,
	ProtectDrainNs,  // waits for the worker (flip)
	ProtectDrains,
	ProtectCalls,    // synchronous VirtualProtect calls, split by the protection applied
	ProtectRoCalls,  // ... to read-only (write watchers added)
	ProtectRoPages,
	ProtectNaCalls,  // ... to no-access (read watchers added: GPU-dirty pages)
	ProtectNaPages,
	ProtectRwNs,     // ... back to read-write (untrack / CPU-dirty), time and pages
	ProtectRwPages,
	ProtectMaskedNs, // ... issued from the masked (RegionManager bitmask) path
	ProtectMaskedCalls,
	ProtectGpuNs,    // ... issued on the GuestGpu thread (the frame-critical share)
	ProtectGpuCalls,
	ProtectGpuPages,
	BufCreateNs,     // Buffer::Buffer (vmaCreateBuffer)
	BufCreates,
	AsyncCopyGpuWaits, // submits that made the queue wait for the async-copy semaphore
	ImgImports,        // image sources copied on the GPU from imported guest memory (HostImport)
	ImgImportBytes,
	ImgImportPieces,   // ... physical pieces (vkCmdCopyBuffer regions)
	HostReadWaits,     // CPU writes that waited for a pending GPU read of guest memory
	HostReadWaitNs,
	ImgDetileDispatches, // tiler dispatches recorded for image uploads
	ImgCopyRegions,      // vkCmdCopyBufferToImage regions recorded for image uploads
	ImgDeferred,         // uploads that left the top mip levels pending (KYTY_MIP_DEFER)
	ImgDeferredBytes,    // ... bytes left in guest memory
	ImgPendingUploads,   // pending top levels uploaded later (bind within the frame budget, or forced)
	ImgPendingBytes,
	ImgMinLodViews,      // sampled binds served with a min-LOD view (top levels still pending)
	BdaPrepareNs,
	BdaPrepares,
	SrtPageMisses,   // SRT page translations that had to take the backing-store lock
	ClampMemoMisses, // ClampRangeSize queries that had to take the range-table lock
	SrtMemoHits,     // materializations answered from the recorded-read memo
	SrtMemoMisses,   // ... key not in the memo
	SrtMemoStale,    // ... key found but a recorded guest word had changed
	SrtMemoSkips,    // ... results that could not be recorded (too many reads, or inconsistent)
	SrtMemoReads,    // guest words re-read to validate a memo entry
	BufEpochHits,    // buffer bindings served by the upload-epoch fast path
	BdaRegionsScanned, // tracking regions a BDA preparation had to scan
	BdaRegionsSkipped, // ... regions skipped because their write stamp had not moved
	BackingPageHits,   // guest reads served from a thread-local page translation
	BackingPageMisses, // ... reads that had to take the backing-store lock
	MatNodes,          // compiled SRT nodes evaluated (the whole graph, once per materialization)
	MatNodesNeeded,    // ... nodes a demand-driven walk would evaluate (survey, gate "srtstat")
	MatReadNodes,      // guest-memory nodes in those graphs
	MatReadNodesNeeded, // ... of them reachable from the active sources and the flat slots
	MatSources,        // descriptor sources of those materializations
	MatSourcesOff,     // ... sources skipped because their shader block is not reached
	DrawAheadSeen,     // draws the PM4 shadow walk saw before they executed
	DrawAheadReady,    // ... of them with both stage programs and their user data known
	DrawAheadWalks,    // shadow walks performed
	DrawAheadNs,       // time spent in them
	DrawAheadQueued,   // materialization tasks handed to the workers
	DrawAheadNoHint,   // draws whose program the draw path has not named yet (no task)
	DrawAheadPresent,  // tasks already queued or answered for the same key
	DrawAheadBusy,     // tasks dropped: both slots of the key hold work of the same walk
	DrawAheadDone,     // tasks the workers materialized
	DrawAheadFailed,   // ... that did not materialize (or overflowed the read log)
	DrawAheadWorkerNs, // worker time spent materializing
	DrawAheadHits,     // draw stages served by a worker result
	DrawAheadStale,    // ... results whose witness no longer held
	DrawAheadLate,     // ... results still queued or running when the draw needed them
	DrawAheadMisses,   // draw stages with no result for their key
	DrawAheadWords,    // guest words compared to validate results
	DrawAheadNoPlan,   // requests whose plan has no compiled SRT yet
	DrawAheadHintFlip, // a program's hint moved to another source entry (static variants)
	DrawAheadRefresh,  // keys answered by an older walk, queued again
	DrawAheadStaleOld, // stale results that came from an older walk
	DrawAheadPredicted, // requests of multi-variant programs queued for the predicted variant only
	DrawAheadMoves,    // results taken by their last predicted user without a copy
	DrawAheadTakeNs,   // critical-thread time looking up and validating worker results
	DrawAheadQueueNs,  // walk time spent queueing tasks
	DrawAheadCleanWords, // validated words read through the GPU-clean reader
	DrawAheadRuns,     // runs (and singles) a validated result was compared in
	DrawAheadProbes,   // slot probes made in the lookahead table (queueing and taking)
	ImgInsertNs,       // TextureCache::InsertImage (host image creation and registration)
	ImgFreeNs,         // TextureCache::FreeImage
	ImgOverlapNs,      // TextureCache::ResolveDepthOverlap (insert + copy + free of a reinterpretation)
	AsyncSubmits,      // command buffers handed to the submit thread
	AsyncSubmitNs,     // submit thread time in vkQueueSubmit
	AsyncSubmitLockNs, // submit thread time waiting for the queue lock
	AsyncSubmitDrains, // synchronous submits / queue users that waited for the submit thread
	AsyncSubmitDrainNs, // ... time they waited
	ImgRecycleHits,    // host images created from the recycle pool
	ImgRecyclePuts,    // retired host images kept in the pool
	RecordPackets,     // records published to the record thread (gate "recordthread")
	RecordBytes,       // ... bytes of the ring arena they took
	RecordDirect,      // Handle() calls that still record on the resolving thread
	RecordDirectNs,    // ... time they spent draining the record queue first
	RecordDrains,      // explicit drains: synchronous submit, wait, capture boundary, shutdown
	RecordDrainNs,     // ... time they waited
	RecordFull,        // publishes that had to wait for arena space (back pressure)
	RecordFullNs,      // ... time they waited
	RecordWorkNs,      // record thread time inside vkBegin/vkEnd/vkCmd*
	RecordIdleNs,      // record thread time waiting for records
	TrackFreeHits,     // tracker queries answered without the region lock (gate "trackfree")
	TrackFreeLocked,   // ... queries that still took it
	TrackFreeMismatch, // ... answers that disagreed with the locked query (gate "tfcheck")
	ProtectMapHits,    // ProtectTransient served from the mapping memo (gate "protfast")
	ProtectMapMisses,  // ... calls that took the address-space mutex and walked the map
	ProtectHeldNs,     // region lock held across a host protection change (diagnostic)
	DescriptorAllocations, // vkAllocateDescriptorSets calls (knobs "dsbatch" / "dspool")
	ShaderWriteBarriersDeferrable, // draws whose written buffers are all flagged atomic
	ShaderWriteBarriersPlain,     // ... and draws with at least one plainly written buffer
	ShaderWriteBarriersDeferred,  // barriers actually deferred (gate "swdefer")
	ShaderWriteBarriersLocal, // shader-write barriers recorded inside the pass (gate "swlocal")
	ShaderWriteBarriersFlushed, // wide shader-write barriers issued when such a pass closed
	GdsBarriers,        // GDS buffer barriers issued by CommitBindings
	GdsBarriersSkipped, // ... skipped: no GDS producer since the last one (gate "gdsepoch")
	ImageWriteBarriersSkipped, // repeated-write image barriers skipped (gate "atomimg")
	// Render passes closed by CommandBuffer::EndRendering, one counter per RenderPassEnd reason in
	// that enum's order (renderTarget.h). RpRestart*: the next pass began on the same targets
	// (attachments, layouts, render area; clears aside), i.e. the restart that reason cost.
	RpEndState,
	RpEndTargetTransit,
	RpEndBindingTransit,
	RpEndGds,
	RpEndShaderWrite,
	RpEndDispatch,
	RpEndBufferUpload,
	RpEndBufferCopy,
	RpEndImageUpload,
	RpEndTiler,
	RpEndClear,
	RpEndSanitize,
	RpEndDownload,
	RpEndSubmit,
	RpEndOther,
	RpRestartState,
	RpRestartTargetTransit,
	RpRestartBindingTransit,
	RpRestartGds,
	RpRestartShaderWrite,
	RpRestartDispatch,
	RpRestartBufferUpload,
	RpRestartBufferCopy,
	RpRestartImageUpload,
	RpRestartTiler,
	RpRestartClear,
	RpRestartSanitize,
	RpRestartDownload,
	RpRestartSubmit,
	RpRestartOther,
	// Session 56. Printed by name in the FrameTrace-x line (videoOut.cpp), so a counter added here
	// needs one table row there and no change to the long format strings.
	DescriptorRingSets,  // descriptor sets allocated by the per-layout rings (gate "dsring")
	DescriptorRingGrows, // ... vkAllocateDescriptorSets calls made by the rings
	DescriptorRingIssued, // ... sets handed out by the rings
	RecordPackDraws,      // draw tails published as records (gate "recpack")
	RecordPackDispatches, // ... dispatch tails
	RecordPackBinds,      // push-constant and descriptor sections published as records
	RecordPackBytes,      // bytes of the pass, bindings and command records
	RecordDirectBusy,     // Handle() calls that found the record queue not empty (each one waits)
	RecordSpinNs,         // record thread time polling an empty queue before it sleeps
	RecordSleeps,         // record thread sleeps on its condition variable
	ProtectSpinNs, // VirtualProtect issued while the thread holds a tracker spin lock (patch E)
	ProtectSpinCalls, // ...
	ProtectSpinPages, // ...
	ProtectSpinGpuNs, // ... on the GuestGpu thread
	ProtectSpinGpuCalls, // ...
	ProtectSpinGpuPages, // ...
	SyncNoop, // read-only SynchronizeBuffer past the epoch check that uploaded nothing
	SyncFreeSkips, // ... answered without the region locks (gate "syncfree")
	SyncFreeMismatch, // ... lock-free answers the locked query contradicted
	TexInvalidations, // TextureCache::InvalidateMemory calls
	TexInvalidateEmpty, // ... that found no image on the range
	TexHintZero, // ... whose page hint read zero (skipped with gate "texfaulthint")
	BatchPages, // pages whose write-watcher protection was deferred to a batch scope (gate "protbatch")
	BatchFlushes, // batch-scope flushes of a region window
	BatchRuns, // VirtualProtect calls issued by flushes
	BatchKb, // KiB protected by flushes
	BatchMerged, // scope flushes that found their pages already applied by another thread
	ApplyWaitNs, // waits for the apply lock of a page-manager region
	ApplyWaitGpuNs, // ... on the GuestGpu thread
	BatchInvalidateFlushes, // invalidation flushes of the invalidated range (protbatch)
	BatchRefault, // ... that applied a change deferred by another thread
	BatchStuck, // a thread write-faulted 8 (or 100000) times in a row on one page; must stay 0
	BatchChecks, // host protections compared with the page state (pbcheck)
	BatchCheckBad, // ... pages expected read-only/no-access but writable (a lost guest write)
	BatchCheckBadRw, // ... any other difference
	DrawAheadRequests,    // M1 requests that had a hint (the unit of da_fan)
	DrawAheadFan,         // ... distinct plan fingerprints among the hint's static variants, summed
	DrawAheadFanCanon,    // ... distinct canonical plan classes among them (gate "daclass" queues these)
	DrawAheadUnused,      // worker results (Ready/Failed) overwritten or queued again with no draw taking them
	DrawAheadUnusedPixel, // ... of them pixel-stage results
	DrawAheadMeshStages,  // draws whose vertex program runs as a mesh stage (no lookahead for it)
	DrawAheadPixelOff,    // draws with a pixel program address but an inactive pixel stage
	DrawAheadClasses,     // canonical plan classes created
	DrawAheadClassShared, // source entries that joined an existing class (merged static variants)
	DrawAheadClassNs,     // time building and comparing canonical plans
	DrawAheadClones,      // results copied out by their last user (gate "daclone")
	DrawAheadCrossCcd,    // tasks a worker ran in another L3 group than the GuestGpu thread's last one
	// Patch D (bindings), printed in FrameTrace-x.
	TexLruTouches,     // TouchImage calls on registered images
	TexLruRepeats,     // ... of which the image was already touched in this GC tick (skipped by "texlru")
	TexFastOk,         // RebindImages sampled bindings answered from the memo view (gate "texfast")
	TexFastNo,         // ... bindings that ran FindTexture while the gate was on
	TexFastNoStamp,    // ... a recorded view refused: the image was invalidated since (bind_stamp)
	TexFastNoState,    // ... a recorded view refused: pending top mips or BC source trim changed
	TexFastRecord,     // views recorded into memo slots
	TexFastBad,        // gate "texfastcheck": memo view differed from FindTexture
	TexMemoEmpty,      // ResolveTexture memo miss: the slot was empty
	TexMemoCollide,    // ... the slot held another key
	TexMemoStale,      // ... same key, the cached image failed validation
	TexMemoKeyMisses,  // gate "texmemo2": resource key computed (pointer cache miss)
	ClampMissEpoch,    // ClampRangeSize memo miss: same address, older range-table epoch
	ClampMissKey,      // ... other/empty entry or a larger size than probed
	ClampVmaMisses,    // gate "clampvma": committed run looked up under the range-table lock
	SamplerMemoMisses, // gate "smpmemo": GetSampler went to the locked map
	// Session 57, A2/A3 (page protection).
	ApplyWaitSyncNs,          // apply-lock waits of synchronous watcher changes (pb_wait_sync_us)
	ApplyWaitScopeNs,         // ... of BatchScope flushes
	ApplyWaitRangeNs,         // ... of range flushes (FlushProtection)
	ApplyWaitWorkerNs,        // ... of the protection worker
	ApplySkipWould,           // FlushRegion windows with nothing pending or in flight (gate "applyskip")
	ApplySkipWouldWaitNs,     // ... the apply-lock wait they still paid (gate off): the ceiling of A2
	ApplySkipWouldWaitGpuNs,  // ... on the GuestGpu thread
	ApplySkips,               // ... skipped without the lock (gate on)
	ApplySkipBlockRw,         // FlushRegion windows held only by an in-flight ReadWrite run
	ApplySkipBlockRo,         // ... by an in-flight run of another protection
	ApplySyncNoProtect,       // synchronous watcher changes that took the apply lock and made no host call (A2b)
	ApplySyncNoProtectWaitNs, // ... their apply-lock wait
	ApplyInflightBad,         // a run published while the previous one was not withdrawn; must stay 0
	FaultWrites,              // CPU write faults on GPU-tracked memory (knob "faultkb")
	FaultWinSame,             // ... in the 64 KiB window of the same thread's previous fault (this frame)
	FaultWinRecent,           // ... in one of the thread's last four 64 KiB windows (this frame)
	FaultWinSeq,              // ... on the page right after the thread's previous fault
	FaultWinArmed,            // CPU-clean pages a fault window opens beyond the faulting page (1/16 x16 at 4 KiB)
	FaultWidened,             // pages a fault window opened beyond the faulting page
	FaultRefault,             // the same thread faulted on the same page again within 1 ms
	SyncBufUploadBytes,       // bytes copied by SynchronizeBuffer uploads (sync_up_kb)
	// Session 57, A4 (record publish).
	RecordPublishes,       // stores of the record head (EndRecord with publish, Pad, PublishStaged)
	RecordStaged,          // records ended without a publish (gate "recbatch")
	RecordForcedPublishes, // PublishStaged calls that found staged records (Handle, Reserve, Stop, barrier)
	RecordWakes,           // WakeConsumer calls that found the record thread asleep (mutex + notify_one)
	RecordDrainLocks,      // Drain calls that went past their spin to the mutex
	RecordTailReads,       // record-tail reads outside the record thread (Reserve refresh, Backlog, Drain)
	RecordCcdChecks,       // L3 checks of the GuestGpu record thread (one per 256 records, with frame stats)
	RecordCrossCcd,        // ... that found it outside the L3 group the GuestGpu thread last queued M1 from
	RecordSleepsGpu,       // RecordSleeps of the GuestGpu recorder only
	RecordSpinNsGpu,       // RecordSpinNs of the GuestGpu recorder only
	RecordFlushBuffers,    // FlushProcessWriteBuffers calls of record threads going to sleep
	// Session 57, A1 (sticky pages).
	StickyFaults,          // gate "stkstat": CPU write faults on GPU-tracked memory
	StickyFaultRepeat,     // ... on a page that write-faulted in this or the previous frame as well
	StickyFaultRepeatSame, // ... earlier in this same frame (armed again and refaulted within it)
	StickyFaultRepeatGpu,  // ... on the GuestGpu thread (WriteData, FillBuffer/CopyBuffer CPU paths)
	StickyFaultRepeatImg,  // ... on a page with an indexed image (texture page hint)
	StickyArmPages,        // pages a read-only upload armed read-only again (GuestGpu)
	StickyArmHot,          // ... armed in this or the previous frame already and CPU-dirty again
	StickyArmHotBda,       // ... inside the BDA scan of PrepareBda
	StickyArmHotImg,       // ... with an indexed image (never sticky)
	StickyHotPages,        // distinct hot pages this frame (first hot arm of a page in the frame)
	StickyCandidates,      // ... hot 3 frames in a row without an image (a sticky mechanism keeps them)
	StickySavedCalls,      // region watcher changes of an upload that would be empty for candidates
	StickyCheckEstimate,   // candidate pages in the range of each synchronization (shadow compares)
	StickyStreamHot,       // small read-only ObtainBuffer requests over a candidate (stream copies)
	// Session 57, E1/E2/E9 (draw statistics).
	DrawBetweenHard, // counted draws preceded by hard work since the previous one (cuts E1 runs)
	DrawStatDraws, // draws that reached their draw command (gate "drawstat", common/drawStat.h)
	DrawStatPure, // ... whose preparation set no hard bit (a pre-resolver need not give them up)
	DrawStatFast, // ... and no slow bit (memo and upload-epoch hits only: M2 as planned in C4)
	DrawStatClean, // ... and no bit at all
	DrawDirtyImgNew, // draws whose preparation inserted, freed or copied a host image
	DrawDirtyImgUp, // ... uploaded or cleared an image, or changed its source/maybe-dirty state
	DrawDirtyMeta, // ... changed DCC/CMASK/HTile metadata state
	DrawDirtyProt, // ... changed page watchers (host protection)
	DrawDirtyBufNew, // ... created (joined) a host buffer
	DrawDirtyBufUp, // ... uploaded, copied or downloaded buffer contents
	DrawDirtyGpuWrite, // ... marked guest memory GPU-written (written buffers, storage images)
	DrawDirtyObjNew, // ... created an image view, sampler, program or pipeline
	DrawDirtySync, // ... submitted, waited for the GPU or drained a download
	DrawDirtyTexSlow, // ... looked an image/texture/sampler up under the cache lock
	DrawDirtyBufSlow, // ... obtained a buffer off the upload-epoch fast path
	DrawDirtyLru, // ... moved an LRU entry (first touch in a GC tick)
	DrawDirtyMemo, // ... wrote a texture/target memo slot
	DrawDirtyM1, // ... took or retired a DrawAhead (M1) slot
	DrawDirtyStream, // ... wrapped a stream ring
	DrawDirtyBarrier, // ... issued a barrier (image transit, GDS)
	DrawTailHard, // draws whose tail (AcquireRenderTargets .. draw command) set a hard bit
	DrawTailImgUp, // ... of them the image-upload bit
	DrawTailMeta, // ... the metadata bit
	DrawTailProt, // ... the protection bit
	DrawTailSync, // ... the synchronization bit
	DrawTailBarrier, // ... the barrier bit
	DrawStreamMaps, // StreamBuffer::Map calls while the gate is on (all rings)
	DrawPureRuns1, // E1 runs of unblocked draws closed, by length 1|2-3|4-7|8-15|16-31|32-63|64+
	DrawPureRuns2, // ...
	DrawPureRuns4, // ...
	DrawPureRuns8, // ...
	DrawPureRuns16, // ...
	DrawPureRuns32, // ...
	DrawPureRuns64, // ...
	DrawPureRunDraws1, // ... draws in those runs, same buckets
	DrawPureRunDraws2, // ...
	DrawPureRunDraws4, // ...
	DrawPureRunDraws8, // ...
	DrawPureRunDraws16, // ...
	DrawPureRunDraws32, // ...
	DrawPureRunDraws64, // ...
	EdgeRuns1, // E2 runs of draws between hard boundaries, same buckets
	EdgeRuns2, // ...
	EdgeRuns4, // ...
	EdgeRuns8, // ...
	EdgeRuns16, // ...
	EdgeRuns32, // ...
	EdgeRuns64, // ...
	EdgeRunDraws1, // ... draws in those runs, same buckets
	EdgeRunDraws2, // ...
	EdgeRunDraws4, // ...
	EdgeRunDraws8, // ...
	EdgeRunDraws16, // ...
	EdgeRunDraws32, // ...
	EdgeRunDraws64, // ...
	EdgeCutPass, // E2 runs cut by a closed render pass (boundaries of a cut may overlap)
	EdgeCutDispatch, // ... by a dispatch
	EdgeCutBarrier, // ... by a barrier
	EdgeCutUpload, // ... by an upload, copy, clear or download
	EdgeCutSubmit, // ... by a submit
	E9Sets, // E9: graphics descriptor-set writes (CommitBindings, gate "drawstat")
	E9Push, // ... pipelines with push descriptors (not in e9_n)
	E9Adjacent, // writes with the set layout of the previous graphics write
	E9Seen, // writes whose layout had an earlier write in the table
	E9SameImages, // ... with the same image views, layouts and samplers as that write
	E9SameBuffers, // ... with the same buffer handles (offsets and ranges ignored)
	E9SameBufferRanges, // ... with the same buffer handles and ranges
	E9SameBase, // ... same images and same handles+ranges (dynamic offsets could reuse the set)
	E9SameFull, // ... identical write (images, handles, ranges, offsets)
	E9AdjacentBase, // writes equal to the previous graphics write up to buffer offsets
	E9BufferInfos, // buffer infos in the counted writes
	E9StreamInfos, // ... of them in the stream ring (a new offset every draw)
	E9RunDraws1, // E9 writes in runs of e9_adj_base, same buckets
	E9RunDraws2, // ...
	E9RunDraws4, // ...
	E9RunDraws8, // ...
	E9RunDraws16, // ...
	E9RunDraws32, // ...
	E9RunDraws64, // ...
	// Session 58, B9 (gate "drawstat"): reuse of a repeating set through dynamic offsets. The
	// three below split e9_base: ok + over + cap = e9_base.
	E9DynOk, // ... repeating writes whose moved offsets fit the device's dynamic budget
	E9DynOver, // ... whose moved offsets do not: this set can never be reused
	E9DynCapped, // ... with more buffer descriptors than the statistic keeps (not measured)
	E9DynLayoutOver, // ... whose layout has by now moved more offsets than the budget
	E9DynNeed1, // moved offsets of a repeating write: 1 | 2 | 3-4 | 5-8 | >8
	E9DynNeed2, // ...
	E9DynNeed4, // ...
	E9DynNeed8, // ...
	E9DynNeedMore, // ...
	E9DynLimit, // maxDescriptorSetStorageBuffersDynamic, added once (a delta of one frame)
	E9DynLimitUniform, // maxDescriptorSetUniformBuffersDynamic, added once
	// Session 57, A6/A7 and track B.
	SnapKeepCopies, // gate "snapkeep": lookahead results copied into the kept snapshot storage
	SnapKeepGrows,  // ... of which a vector still had to grow (allocated on this thread)
	BufLruTouches, // BufferCache::TouchBuffer calls on live buffers
	BufLruRepeats, // ... of which the buffer was already touched in this GC tick (skipped by "buflru")
	// Session 58, B4 follow-up (the snapshot copies of gate "snapkeep").
	SnapCopyBytes,       // bytes the vectors of one frame's kept copies move (snapshot + specialization)
	SnapCopySameBytes,   // ... of them in vectors the destination already held (ceiling of "snapdiff")
	SnapCopyVectors,     // non-empty vectors in those copies
	SnapCopySameVectors, // ... of them equal to the destination's
	SnapCopyUnchanged,   // copies whose whole snapshot repeats what this stage had on the previous draw
	SnapLastUseCopies,   // copies taking a slot's last use (ceiling of "snapswap")
	SnapLastUseBytes,    // bytes of those copies
	// Session 58, M2 step 1 (buffer request memo).
	BufFastOk,    // read-only buffer requests answered from the per-thread memo (gate "buffast")
	BufFastNo,    // ... requests whose slot held another guest range
	BufFastStale, // ... requests whose slot matched but whose witness had moved (CPU write, re-registration)
	BufFastSkip,  // ... requests the memo cannot answer or record (written, texel, stream copy, untracked)
	BufFastBad,   // gate "buffastcheck": the memo answer differed from the full path
	// Session 58, A3 phase 2 (gate "protbatch2"). Read with the gate OFF they are its ceiling: of
	// the pb2_vp calls a pass issues today, pb2_vp_adj continue the previous call of the same pass
	// exactly (one merged run swallows them) and pb2_vp_near share its region and protection with a
	// gap in between (a run swallows them too, at the price of pb2_gap_pages re-protected pages).
	// So the calls left after the merge are pb2_vp - pb2_vp_adj - pb2_vp_near, and never fewer than
	// pb2_reg. With the gate on the same counters show what the pass actually issued.
	PassPasses,          // BDA dirty-range passes with at least one buffer to synchronize
	PassSyncs,           // buffer synchronizations in them (today: two apply-lock holds each)
	PassRegions,         // tracking-region windows of those passes (phase 2 flushes this many)
	PassProtectCalls,    // synchronous host protection calls issued inside a pass
	PassProtectPages,    // ... pages they covered
	PassProtectAdjacent, // ... calls continuing the previous call of their pass exactly
	PassProtectNear,     // ... calls in its region and protection with a gap in between
	PassGapRuns,         // flush runs extended over pages that were not pending (gate on)
	PassGapPages,        // ... those pages, re-protected with the value they already had
	PassUploads,         // synchronizations whose copies were deferred to the pass copy phase
	// Session 59, B9 ceiling (gate "drawstat"): CommitBindings split per pooled / push set.
	CommitPoolSets,     // graphics CommitBindings calls that wrote a pooled descriptor set
	CommitPoolTransitNs, // ... their image transitions (both stages)
	CommitPoolWriteNs,  // ... building the write list (both stages)
	CommitPoolEmitNs,   // ... heap commit + packet copy, or the direct update + bind
	CommitPushSets,     // ... the same for push-descriptor pipelines
	CommitPushTransitNs, // ...
	CommitPushWriteNs,  // ...
	CommitPushEmitNs,   // ...
	// Session 59, gate "dawalk": the shadow walk on its own thread.
	DrawAheadWalkJobs,  // submissions walked by the walker thread
	DrawAheadWalkLagNs, // enqueue -> start of their walk
	DrawAheadWalkDepth, // jobs still queued when one was taken (sum; /jobs = mean depth)
	DrawAheadWalkSkipped, // process-time walks skipped because the walker had done them
	DrawAheadWalkDropped, // jobs dropped unwalked: the GuestGpu thread had passed them
	// Session 59, gate "rtfast": target views reused across draws.
	RtFastOk,       // target acquisitions served by the recorded view
	RtFastNo,       // ... that went through FindRenderTarget / FindDepthTarget
	RtFastStale,    // ... of them because the stamp or the metadata epoch had moved
	RtFastRecord,   // views recorded after a slow acquisition
	RtFastStencil,  // depth acquisitions kept slow by a stencil plane
	// Session 60, B3 (gate "progmemo"): program lookup served by the previous draw's inputs.
	ProgMemoHit,     // draw stages whose PrepareProgram, static key and programs.find were skipped
	ProgMemoMiss,    // draw stages whose register inputs differed from the previous draw's
	ProgMemoStale,   // ... equal in registers, but the vertex tables / entry / chain had moved
	ProgMemoBad,     // self-check mismatches (gate "progmemocheck")
	ProgMemoEqVs,    // ceiling: vertex stages whose inputs equal the previous draw's (memo on or "drawstat")
	ProgMemoEqPs,    // ... pixel stages
	ProgMemoPipe,    // graphics pipeline lookups served by the previous draw's key
	ProgMemoCheckNs, // building and comparing the witnesses (both stages)
	// Session 60, item 4 (gate "armdefer"): watchers of read-only uploads armed by the worker.
	ArmRequestPages, // dirty pages copied and handed to the worker for their write watcher
	ArmSettledPages, // ... copied again with the protection in effect, and cleaned
	ArmWaitPages,    // ... copied again while their protection was still pending / in flight
	ArmSyncFlushes,  // synchronous paths that flushed a pending arming before clearing dirty bits
	ArmFlushSkips,   // read-only uploads that skipped the range protection flush
	ArmBad,          // self-check (gate "armcheck"): a settled page found host-writable
	// Session 61 ceilings. Item 2: buffer uploads recorded back to back.
	SyncBufUploadSeries, // uploads with no draw or dispatch of this thread since the previous upload
	// Item 3: an M1 witness by tracking-region write epochs instead of guest words.
	DrawAheadEpochSame,    // verified witnesses whose regions' write epochs had not moved since the worker built them
	DrawAheadEpochMoved,   // ... whose epochs had moved: an epoch witness would have been stale here
	DrawAheadEpochRegions, // tracking regions per verified witness (sum)
	DrawAheadStaleFirst,   // stale witnesses whose first run already differed
	DrawAheadStaleEpochSame, // stale witnesses whose epochs had not moved: an epoch witness would be unsound here
	// Session 61, knob "recpubn".
	RecordThrottled,       // draw-stream records staged by the publish throttle
	DrawAheadUnchecked,    // M1 results taken with the witness check skipped (gate "dawitness" off)
	DrawAheadDirect,       // witnesses verified through the recorded host pointers (gate "dawitptr")
	DrawAheadDirectNo,     // ... that fell back to the page lookups (map epoch moved, or no pointers)
	// Session 62 ceilings. Item 3: copies of guest ranges into the stream ring.
	ObtainStreamCopies,    // ObtainBuffer answers served by a copy into the stream ring (CPU-dirty small reads)
	ObtainStreamBytes,     // ... bytes
	CbSame,                // gate "cbstat": stream copies whose bytes equal the previous copy of the same range
	CbDiff,                // ... whose bytes differ
	CbNew,                 // ... of a range not seen before (or evicted)
	CbSameEpoch,           // ... equal bytes and the range's write epoch unchanged
	CbDiffEpoch,           // ... different bytes and the write epoch unchanged: an epoch witness is unsound here
	CbSameRing,            // ... equal bytes and the previous ring slot still intact (ring generation unchanged)
	CbStatNs,              // time inside the shadow compare (diagnostic cost)
	ObtainStreamNs,        // ObtainBuffer stream copies: map, guest read into the ring, commit
	CbankCopyNs,           // const-bank copies of descriptors.cpp: the same three steps
	// Session 62, item 2: direct writes turned into records.
	RecordImageBarrierPackets, // image transitions published as records (gate "recimg")
	RecordUploadPackets,       // buffer uploads published as records (gate "recup")
	Count
};

// Call-site attribution: a SiteScope names the operation in flight on this thread and the wait /
// submit paths charge their time to that name.
enum class Table : uint32_t { WaitSites, SubmitSites, Pm4Sites, PopSites, DirectSites, Count };

struct SiteRow {
	const char* name  = nullptr;
	uint64_t    ns    = 0;
	uint64_t    count = 0;
};

void                      AddSite(Table table, const char* site, uint64_t ns);
size_t                    ReadSites(Table table, SiteRow* out, size_t max);
[[nodiscard]] const char* CurrentSite();
// Address relative to the executable image base (matches the linker map RVAs); the raw
// address on platforms without module information.
[[nodiscard]] uint64_t    ModuleOffset(const void* address);
// A stable site name for a code address ("+0x<rva>"), interned once per address: a return address
// can then key a site table (AddSite compares name pointers).
[[nodiscard]] const char* SiteName(const void* address);

class SiteScope {
public:
	explicit SiteScope(const char* site);
	~SiteScope();
	SiteScope(const SiteScope&)            = delete;
	SiteScope& operator=(const SiteScope&) = delete;

private:
	const char* m_previous;
};

enum class ThreadRole : uint32_t { Main, Gpu, Present, Record, Count };

// KYTY_SAMPLE_GPU=1: sampling profiler of the thread registered as ThreadRole::Gpu. Started by
// RegisterCurrentThread; the samples are logged periodically as SampleTrace: lines.
void                      StartSampler(ThreadRole role);
// Frame boundary for the per-frame sampler dumps (KYTY_SAMPLE_FRAME_MS): called from the flip.
void                      NoteFrame(uint64_t frame);

[[nodiscard]] bool Enabled();

namespace Detail {

struct Shard {
	alignas(64) std::array<std::atomic<uint64_t>, static_cast<size_t>(Counter::Count)> counters {};
};

// Counters with an index below the limit are counted: Counter::Count with KYTY_FRAME_TRACE or
// KYTY_AV_TRACE, 0 without them, and only the counters of the FrameTrace main line in the lean
// mode (gate "fslean"). Zero until frameStats.cpp is initialized.
inline constinit std::atomic<uint32_t> g_count_limit {0};
inline constinit bool                  g_timings = false;
// No initializer to run, so no TLS guard: the shard is attached by the first Add of a thread.
inline constinit thread_local Shard*   t_shard   = nullptr;

[[nodiscard]] Shard* AttachShard();

} // namespace Detail

// KYTY_FRAME_TRACE=lite retains counters and per-frame CPU time without fine-grained clocks.
inline bool TimingsEnabled() {
	return Detail::g_timings;
}

[[nodiscard]] uint64_t NowNs();

// Inline: about 250 counts per draw on the GuestGpu thread.
inline void Add(Counter counter, uint64_t value) {
	const auto index = static_cast<uint32_t>(counter);
	if (index >= Detail::g_count_limit.load(std::memory_order_relaxed)) {
		return;
	}
	auto* shard = Detail::t_shard;
	if (shard == nullptr) [[unlikely]] {
		shard = Detail::AttachShard();
	}
	auto& slot = shard->counters[index];
	slot.store(slot.load(std::memory_order_relaxed) + value, std::memory_order_relaxed);
}

// Gate "fslean": count only the FrameTrace main line (draws, CPU and GPU time, faults).
void                   SetLean(bool lean);
[[nodiscard]] uint64_t Read(Counter counter);

void                   RegisterCurrentThread(ThreadRole role);
[[nodiscard]] ThreadRole CurrentRole(); // ThreadRole::Count if the thread is not registered
[[nodiscard]] uint64_t ThreadCpuNs(ThreadRole role); // 0 if unknown
[[nodiscard]] uint64_t ProcessCpuNs();

// Adds the elapsed time to `ns` and increments `count` (Counter::Count = none) when destroyed.
class Scope {
public:
	explicit Scope(Counter ns, Counter count = Counter::Count)
	    : m_ns(ns), m_count(count), m_t0(TimingsEnabled() ? NowNs() : 0) {}
	~Scope() {
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
		}
		if (m_count != Counter::Count) {
			Add(m_count, 1);
		}
	}
	Scope(const Scope&)            = delete;
	Scope& operator=(const Scope&) = delete;

private:
	Counter  m_ns;
	Counter  m_count;
	uint64_t m_t0;
};

// Splits a sequence of phases: Mark(c) charges the time since the previous Mark (or construction)
// to counter c.
class Lap {
public:
	Lap(): m_t(TimingsEnabled() ? NowNs() : 0) {}
	void Mark(Counter counter) {
		if (m_t != 0) {
			const auto now = NowNs();
			Add(counter, now - m_t);
			m_t = now;
		}
	}

private:
	uint64_t m_t;
};

} // namespace Common::FrameStats

#endif // KYTY_COMMON_FRAMESTATS_H_
