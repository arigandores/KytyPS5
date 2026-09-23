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
	BdaRegionsBitSkipped, // ... of those, skipped on the write map without reading the stamp
	BdaBitMismatches,     // gate "bdabitscheck": a map skip whose stamp had in fact moved (must be 0)
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
	// Session 64, E4/E6 (knob "shadowresolve", gate "shadowinline"): the read-only binding
	// resolution repeated and discarded (shadowResolve.h).
	ShadowJobs,       // draws whose bindings were re-read (workers and inline together)
	ShadowDropped,    // jobs the full ring dropped
	ShadowOver,       // draws with more bindings than a job holds
	ShadowImages,     // image bindings probed
	ShadowImgGone,    // ... whose image id was gone
	ShadowImgStale,   // ... whose memo checks failed
	ShadowImgSlow,    // ... not eligible for the recorded view (storage, DCC, dynamic storage)
	ShadowImgView,    // ... eligible, but FindTexture would run
	ShadowImgFast,    // ... served by the recorded view
	ShadowBuffers,    // buffer bindings probed
	ShadowBufNone,    // ... with no range
	ShadowBufFast,    // ... answered by the shadow's own request memo
	ShadowBufEpoch,   // ... whose upload interval is current
	ShadowBufStream,  // ... small CPU-dirty reads (a stream-ring copy)
	ShadowBufSlow,    // ... that SynchronizeBuffer would handle
	ShadowBufNew,     // ... that no buffer owns
	ShadowWorkerNs,   // worker time in Run
	ShadowInlineNs,   // GuestGpu time in Run (gate "shadowinline")
	ShadowPushNs,     // GuestGpu time building and queueing the job
	ShadowLockNs,     // time acquiring TextureCache::m_lock inside the probes
	ShadowTrackerNs,  // time in the locked tracker queries inside the buffer probes
	ShadowWakes,      // condition-variable wake-ups the producer issued
	// Session 67 watchdog: the resolution of the work itself, not of the largest target. Divided
	// by rt_att and by draws they are the mean pixel area of an attachment and of a viewport, and
	// those are what a step of the resolution ladder moves.
	RtAttachments,    // colour attachments bound by the draws of this frame (rt_att)
	RtPixelsK,        // ... their width * height, in units of 1024 pixels (rt_kpx)
	VpPixelsK,        // guest viewport area per draw, same units (vp_kpx)
	// Session 68. The occlusion dump is counted always (it costs one add per dump); everything
	// below is zero unless its gate or knob is on.
	OcclusionDumps,   // event 0x39 dumps of the frame (occ_dump)
	// Gate "amut": the mutating part of the draw path, timed in place. Only the outermost interval
	// counts, so the total is the union of the intervals and not their sum.
	MutateNs,         // a_mut_us
	MutateIntervals,  // a_mut_n
	// The render mutex of renderContext.h:80. Draw, dispatch and present all take this one object,
	// so the time it is held is the serial floor of every threading scheme, M4 included.
	LockHoldNs,       // a_hold_us
	LockHolds,        // a_hold_n
	LockWaitNs,       // a_wait_us
	// Knob "m4baton": a second thread runs a real PM4 range while GuestGpu is parked. The ranges
	// alternate inside one run - one on the relay thread, the next on GuestGpu - so f_full is the
	// ratio of the two per-draw times of the SAME run.
	BatonRanges,      // bat_ranges: ranges handed to the relay thread
	BatonWorkNs,      // bat_work_us: relay-thread time inside such a range
	BatonWorkDraws,   // bat_work_draws
	BatonSelfNs,      // bat_self_us: GuestGpu time inside a control range of the same shape
	BatonSelfDraws,   // bat_self_draws
	BatonSelfRanges,  // bat_self_ranges
	BatonParkNs,      // bat_park_us: GuestGpu time from handing the range over to getting it back
	BatonWakeNs,      // bat_wake_us: relay-thread time from being woken to starting the range
	BatonDropped,     // bat_drop: ranges the relay could not take (it was busy)
	// Session 82, gate "bindkey" (measurement only): does a draw's binding input repeat the
	// previous draw's?  Per stage for the hit counters, per draw for the rest; a draw counts as a
	// hit only when EVERY stage of it hit.
	BindKeyHit,       // bk_hit: stages whose (shader, snapshot, user data) equal the previous ones
	BindKeyMiss,      // bk_miss
	BindKeyDrawHit,   // bk_draw_hit: draws where every stage hit
	BindKeyDrawMiss,  // bk_draw_miss
	BindKeyHitNs,     // bk_hit_us: the binding phase of the draws that fully hit
	BindKeyMissNs,    // bk_miss_us
	// Gate "pxstat": the binding interval of a draw, split by whether the pixel stage is live.
	PxOnDraws,        // px_on_n
	PxOnBindNs,       // px_on_bind_us
	PxOffDraws,       // px_off_n: depth-only draws (the same population as da_px_off)
	PxOffBindNs,      // px_off_bind_us
	// Session 69, gate "mutsite": the phases of the render-mutex hold. The first six sum to the
	// hold of a draw, mh_disp_us is a whole dispatch and mh_pres_us a whole present; together they
	// must account for a_hold_us (plus the present, which a_hold_us does not contain).
	HoldEntries,      // mh_n: times a draw function took the render mutex
	HoldDraws,        // mh_draws: of those, the ones that reached the bindings
	HoldPrologueNs,   // mh_pro_us
	HoldTargetsNs,    // mh_rt_us: PrepareDrawRenderState / AcquireRenderTargets
	HoldProgramsNs,   // mh_prog_us: RefreshShaders / GetGraphicsPrograms
	HoldBindingsNs,   // mh_bind_us: PrepareGraphicsBindings and everything it calls
	HoldEmitNs,       // mh_emit_us: the apply-and-record tail of ExecutePreparedDraw
	HoldTailNs,       // mh_tail_us: ResetBindings, and the whole hold of an early return
	HoldDispatches,   // mh_disp_n
	HoldDispatchNs,   // mh_disp_us
	HoldPresents,     // mh_pres_n: ACQUISITIONS, not presents - a displayed frame costs two of
	                  // them (PrepareFrame and Present), so mh_pres_us/mh_pres_n is the cost of one
	                  // acquisition
	HoldPresentNs,    // mh_pres_us
	HoldPresentWaitNs, // mh_pres_wait_us: how long the present thread waits for the render mutex -
	                   // the only contention this object sees today, and the number that decides
	                   // whether splitting it buys anything
	// Session 69, gate "imgskip": the uploads the ceiling gate refused, so that
	// img_skip + img_up equals the baseline img_up and img_skip_kb is the source it did not read.
	ImgSkipped,       // img_skip
	ImgSkippedKb,     // img_skip_kb: KiB, accumulated as size/1024 at the increment site so that it
	                  // is on the same scale as img_up_kb (which is a byte counter divided by 1024
	                  // at print time). Do NOT print it through the "micros" path - that divides
	                  // by 1000 and the two stop being addable.
	// Session 70: why a recognised guest compute clear is not consumed. ResolveComputeBufferFill
	// accepts 21.6 fills per frame in Sky Garden (run clr70a), so everything below happens inside
	// TextureCache::ClearImageFromBuffer, and the four outcomes call for four different fixes.
	// No gate: they cost one Add per fill and change no decision, so a plain baseline run sizes
	// the opportunity.
	ClearConsumed,    // clr_ok: fills turned into a vkCmdClearColorImage / ClearDepthStencilImage
	ClearConsumedKb,  // clr_ok_kb: KiB of their guest ranges (KiB at the increment site)
	ClearAmbiguous,   // clr_ambig: declined because two or more live images claim the same
	                  // (address, size) - the guest keeps both rungs of its resolution ladder
	                  // registered, and the fill cannot tell which one it means
	ClearAmbiguousKb, // clr_ambig_kb: KiB of those ranges
	ClearNoMatch,     // clr_none: no image claims the range - the genuine metadata fills that
	                  // TrackDccFill picks up. Not a missed clear.
	ClearNoMatchKb,   // clr_none_kb
	ClearDecodeFail,  // clr_decode: an image claimed the range but the packed value had no decoder
	                  // for its format (imageInfo.h DecodePackedColorClear and friends)
	ClearOverlapOnly, // clr_over: images that overlapped the fill range without claiming it
	                  // exactly, summed over declined fills - sizes widening "exact" to "contained"
	// ------------------------------------------------------------------------------------------
	// Session 71, gate G-area: the census of the render passes rp_begin counts. rt_att and
	// rt_kpx (session 67) are per-DRAW sums - AcquireRenderTargets runs once per draw - so they
	// cannot tell "more passes" from "more attachments per pass" from "the same passes larger".
	// Booked once per pass in CommandBuffer::BeginRenderingImpl (one loop over at most 8 slots
	// plus 5-7 Adds, ~188 passes a frame) plus one Add per draw. No gate, no decision changed.
	// Identities the first run must satisfy: sum(rpa_aN) == sum(rpa_eN) == rp_begin;
	// sum(N * rpa_aN) == rpa_att; sum(rpd_aN) == draws; rpa_slot - rpa_att == attachment holes.
	// rpa_a0..a8, rpa_e0..e7 and rpd_a0..a8 are CONTIGUOUS runs indexed by the classifiers of
	// renderTarget.h; context.cpp static_asserts their length. Do not insert into the middle.
	PassSlots,          // rpa_slot: colour attachment SLOTS of the pass (num_color_attachments, holes in)
	PassAttachments,    // rpa_att: LIVE colour attachments (image_view != nullptr)
	PassPixelsK,        // rpa_kpx: live * width * height / 1024, summed over PASSES
	PassDepth,          // rpa_dep: passes with a depth/stencil attachment
	PassDepthPixelsK,   // rpa_dkpx: their width * height / 1024
	PassLayered,        // rpa_lay: passes with num_layers > 1 - self-check for rpa_kpx
	PassRestartPixelsK, // rpa_re_kpx: colour area of a pass begun on the targets just ended
	PassShape0,         // rpa_a0: passes with 0 live colour attachments
	PassShape1,         // rpa_a1: passes with 1 live colour attachments
	PassShape2,         // rpa_a2: passes with 2 live colour attachments
	PassShape3,         // rpa_a3: passes with 3 live colour attachments
	PassShape4,         // rpa_a4: passes with 4 live colour attachments
	PassShape5,         // rpa_a5: passes with 5 live colour attachments
	PassShape6,         // rpa_a6: passes with 6 live colour attachments
	PassShape7,         // rpa_a7: passes with 7 live colour attachments
	PassShape8,         // rpa_a8: passes with 8 live colour attachments
	PassExtent0,        // rpa_e0: passes in colour-area bucket 0
	PassExtent1,        // rpa_e1: passes in colour-area bucket 1
	PassExtent2,        // rpa_e2: passes in colour-area bucket 2
	PassExtent3,        // rpa_e3: passes in colour-area bucket 3
	PassExtent4,        // rpa_e4: passes in colour-area bucket 4
	PassExtent5,        // rpa_e5: passes in colour-area bucket 5
	PassExtent6,        // rpa_e6: passes in colour-area bucket 6
	PassExtent7,        // rpa_e7: passes in colour-area bucket 7
	PassDraw0,          // rpd_a0: draws emitted into a pass with 0 attachment slots
	PassDraw1,          // rpd_a1: draws emitted into a pass with 1 attachment slots
	PassDraw2,          // rpd_a2: draws emitted into a pass with 2 attachment slots
	PassDraw3,          // rpd_a3: draws emitted into a pass with 3 attachment slots
	PassDraw4,          // rpd_a4: draws emitted into a pass with 4 attachment slots
	PassDraw5,          // rpd_a5: draws emitted into a pass with 5 attachment slots
	PassDraw6,          // rpd_a6: draws emitted into a pass with 6 attachment slots
	PassDraw7,          // rpd_a7: draws emitted into a pass with 7 attachment slots
	PassDraw8,          // rpd_a8: draws emitted into a pass with 8 attachment slots
	// ------------------------------------------------------------------------------------------
	// Session 71, gate G-wit: what the M1 witness is made of. Witness::Words() and Runs()
	// (pipelineCache.cpp) are sums over live runs, clean runs and singles, and VerifyWitness
	// spends its 2.016 ms in three separate loops over them. With these the three separate:
	//   clean_runs = da_runs_clean, singles = da_singles,
	//   live_runs  = da_runs  - da_runs_clean - da_singles,
	//   live_words = da_words - da_words_clean - da_singles, clean_words = da_words_clean.
	DrawAheadCleanRuns,   // da_runs_clean: GPU-clean runs of a verified witness (sum)
	DrawAheadSingles,     // da_singles: singles of a verified witness (sum)
	DrawAheadQueueProbes, // da_probe_q: the QUEUE-side half of da_probe (da_probe unchanged)
	// ------------------------------------------------------------------------------------------
	// Session 71: the census of the gate "swlocal" predicate (renderDraw.cpp, both the recpack
	// tail and the direct path). Counted for every shader-write draw the gate "swdefer" did not
	// take, whether or not "swlocal" is on - swbar_loc is 0 in every s69/s70 log, so a plain
	// baseline run sizes the opportunity. The four are exclusive and sum to the draws that
	// reach the branch.
	ShaderWriteLocalEligible,     // swloc_ok: framebuffer-space stages only AND a pass open
	ShaderWriteLocalMeshBlocked,  // swloc_mesh: blocked by eMeshShaderEXT in the write mask
	ShaderWriteLocalStageBlocked, // swloc_vtx: blocked by another non-framebuffer stage
	ShaderWriteLocalClosed,       // swloc_shut: stages fine, but no pass open (or no local_read)
	// ------------------------------------------------------------------------------------------
	// Session 71: where the closer MIGRATES to if "swlocal" stops closing the pass. One Add in
	// the early-return branch of EndRenderingImpl, indexed by the RenderPassEnd reason and
	// qualified by "the pass was closed by a ShaderWrite" - so every closer is covered, not just
	// the GDS barrier session 55 warned about. CONTIGUOUS and in RenderPassEnd order, like
	// RpEnd* and RpRestart*; context.cpp static_asserts it. swmig_state counts the episodes
	// exactly (BeginRenderingImpl clears m_closed_valid), the other fourteen are an UPPER bound
	// on migrated closes because every hidden closer of an episode is counted, not just the
	// first. swmig_state - sum(the other fourteen) is therefore a LOWER bound on the restarts
	// "swlocal" would really remove.
	SwMigState,          // swmig_state: a BeginRendering - one per episode, so this counts the episodes
	SwMigTargetTransit,  // swmig_tt: attachment layout transition (AcquireRenderTargets)
	SwMigBindingTransit, // swmig_bt: layout transition of a bound image (CommitBindings)
	SwMigGds,            // swmig_gds: GDS buffer barrier - the closer session 55 warned about
	SwMigShaderWrite,    // swmig_sw: another shader-write barrier with no pass open
	SwMigDispatch,       // swmig_disp: compute dispatch
	SwMigBufferUpload,   // swmig_bup: CPU -> buffer synchronization
	SwMigBufferCopy,     // swmig_bcp: buffer copy or fill on the GPU
	SwMigImageUpload,    // swmig_iup: guest -> image upload
	SwMigTiler,          // swmig_tiler: tiler compute
	SwMigClear,          // swmig_clr: image clears outside a pass
	SwMigSanitize,       // swmig_san: indirect draw argument sanitizer
	SwMigDownload,       // swmig_dl: readbacks and image -> buffer copies
	SwMigSubmit,         // swmig_sub: command buffer end at submit
	SwMigOther,          // swmig_oth: everything else
	// ------------------------------------------------------------------------------------------
	// Session 71, candidate C3 (suppress the guest upload of an image bound as a write target).
	// RenderAttachment::is_clear (renderTarget.h) is never assigned true anywhere under src/, so
	// every colour attachment takes loadOp = eLoad and C3's premise has no support in the tree.
	// These counters say what the GUEST states: the fast-clear registers of the binding as
	// pm4Handlers decoded them, read BEFORE ResolveRenderColorTarget turns them into an
	// ImageMetadataKind and before its width%1024 / height%1024 guard, which no extent of the
	// imgskip population can pass. Register state and metadata-FILL state are counted apart and
	// never conflated. Identities the first run must satisfy:
	//   c3_ct_up + c3_dt_up + c3_st_up + c3_smp_up + c3_clr_up + c3_oth_up == c3_pop, and the
	//   same for the _kb rows against c3_pop_kb, EVERY frame and at any gate setting;
	//   c3_ct + c3_dt - rt_fast_no >= 0 (the excess is descriptors.cpp's second entrance);
	//   c3_ct_pop - c3_ct_canc - c3_ct_up >= 0 (the maybe-CPU-dirty divergence - quote it).
	C3ColorAcquires,      // c3_ct: acquisitions that reached TextureCache::FindRenderTarget
	C3ColorRegFastClear,  // c3_ct_fc: CB_COLOR*_INFO.FAST_CLEAR set AND CB_COLOR*_CMASK_BASE != 0
	C3ColorRegDcc,        // c3_ct_dcc: CB_COLOR*_INFO.DCC_ENABLE set AND CB_COLOR*_DCC_BASE != 0
	C3ColorRegDccKey,     // c3_ct_key: ... and CB_COLOR*_DCC_CONTROL.KEY_CLEAR_ENABLE set
	C3ColorMetaKind,      // c3_ct_kind: metadata.kind survived to Dcc or Cmask
	C3ColorRegDropped,    // c3_ct_drop: register clear state that colorRenderTarget.cpp dropped
	C3ColorFillPending,   // c3_ct_fill: an unconsumed metadata FILL for the bound layers
	C3ColorPop,           // c3_ct_pop: acquisitions in the imgskip population ON ENTRY
	C3ColorPopKb,         // c3_ct_pop_kb: KiB of their guest source (KiB at the increment site)
	C3ColorCancelled,     // c3_ct_canc: left the population across the two Prepare*Clear calls
	C3ColorCancelledKb,   // c3_ct_canc_kb: KiB of those
	C3DepthAcquires,      // c3_dt: acquisitions that reached FindDepthTarget
	C3Population,         // c3_pop: population members reaching the upload decision, any site
	C3PopulationKb,       // c3_pop_kb: KiB of those
	C3ColorUploads,       // c3_ct_up: population uploads at a colour-target binding - C3s ceiling
	C3ColorUploadsKb,     // c3_ct_up_kb: KiB of those
	C3ColorUploadsReg,    // c3_ct_up_reg: ... whose guest fast-clear REGISTERS were set
	C3ColorUploadsRegKb,  // c3_ct_up_reg_kb: the bytes the G-img3 question asks for
	C3ColorUploadsFill,   // c3_ct_up_fill: ... with an unconsumed metadata fill still pending
	C3ColorUploadsFillKb, // c3_ct_up_fill_kb: KiB of those
	C3DepthUploads,       // c3_dt_up: population uploads at a depth-target binding
	C3DepthUploadsKb,     // c3_dt_up_kb: KiB of those
	C3DepthUploadsReg,    // c3_dt_up_reg: ... with DB_RENDER_CONTROL.DEPTH_CLEAR_ENABLE
	C3DepthUploadsRegKb,  // c3_dt_up_reg_kb: KiB of those - the second half of R
	C3StorageUploads,     // c3_st_up: population uploads at a storage-image binding
	C3StorageUploadsKb,   // c3_st_up_kb: KiB of those
	C3SampledUploads,     // c3_smp_up: population uploads at a SAMPLED binding - the pass READS it
	C3SampledUploadsKb,   // c3_smp_up_kb: KiB of those - the direct test of s70s gpu= proxy
	C3ClearUploads,       // c3_clr_up: uploads ClearImages partial-clear path performs ITSELF
	C3ClearUploadsKb,     // c3_clr_up_kb: KiB of those
	C3OtherUploads,       // c3_oth_up: population uploads from every other site
	C3OtherUploadsKb,     // c3_oth_up_kb: KiB of those
	// ------------------------------------------------------------------------------------------
	// Session 72: proof that the knob "dawitloop" armed, and the population it removed. Counts the
	// RUNS of the loop VerifyWitness skipped, so the run checks itself: at dawitloop=1 this equals
	// da_runs_clean, at 2 it equals da_runs - da_runs_clean - da_singles, at 0 (the default) it is
	// zero. The knob is a measurement ceiling and is UNSOUND to ship - see pipelineCache.cpp.
	DrawAheadLoopSkip, // da_loop_skip: witness runs the ceiling knob did not compare
	// ------------------------------------------------------------------------------------------
	// Session 72, C1: which image uploads could have had their detile fused straight into the
	// image, so that session 71's 836.5 us copy-phase CEILING can be cut down to an ACHIEVABLE
	// one before a shader is written. Every upload lands in exactly one of four cells, by
	// (the image can take a storage write) x (this upload went through detile). The predicate is
	// image.backing.usage & eStorage, which is what the driver accepted at create time
	// (image.cpp:53-77, :747-757), not a format list of ours. Two byte counters per cell because
	// they are different numbers: _kb is the GUEST source (the unit img_up_kb is in, so the
	// identity holds) and _cp_kb is the LINEAR size copyBufferToImage actually moves (the unit
	// the 836.5 us is spent in, and therefore the right weight for the ceiling).
	C1StorageDetile,       // c1_si_dt: storage-capable image, upload went through detile - THE ACHIEVABLE CELL
	C1StorageDetileKb,     // c1_si_dt_kb: KiB of GUEST source bytes in that cell
	C1StorageDetileCopyKb, // c1_si_dt_cp_kb: KiB copyBufferToImage really moves there
	C1StorageDirect,       // c1_si_nd: storage-capable image, no detile - nothing to fuse into
	C1StorageDirectKb,     // c1_si_nd_kb: KiB of GUEST source bytes in that cell
	C1StorageDirectCopyKb, // c1_si_nd_cp_kb: KiB copyBufferToImage really moves there
	C1NoStorageDetile,     // c1_ns_dt: detiled, but the image cannot take a storage write
	C1NoStorageDetileKb,   // c1_ns_dt_kb: KiB of GUEST source bytes in that cell
	C1NoStorageDetileCopyKb, // c1_ns_dt_cp_kb: KiB copyBufferToImage really moves there
	C1NoStorageDirect,     // c1_ns_nd: neither
	C1NoStorageDirectKb,   // c1_ns_nd_kb: KiB of GUEST source bytes in that cell
	C1NoStorageDirectCopyKb, // c1_ns_nd_cp_kb: KiB copyBufferToImage really moves there
	// ------------------------------------------------------------------------------------------
	// Session 72: the render passes the session-71 census cannot see, and the area it understates.
	// Three sites call vkCmdBeginRendering without going through CommandBuffer::BeginRenderingImpl,
	// so rp_begin never counts them; two of the three call EndRendering first, so they also charge
	// a closure to the census while contributing no opening. Their frequency was NOT MEASURED.
	PassAliasClear,    // rpa_alias: ClearImage's aliased-format pass (textureCache.cpp)
	PassAliasClearKpx, // rpa_alias_kpx: Kpx of its render area x layers
	PassBlitMsDepth,   // rpa_blit: BlitHelper::ReinterpretColorAsMsDepth (its draw is not in draws)
	PassOverlay,       // rpa_ovl: the ImGui system-overlay pass, present thread
	// And the area: state.width/height is the MINIMUM over the pass's attachments, so rpa_kpx
	// understates a pass that mixes extents. rpa_tkpx uses each attachment's own extent and is
	// equal to rpa_kpx when they agree, so rpa_tkpx - rpa_kpx IS the understatement in Kpx.
	PassTrueColorPixelsK, // rpa_tkpx: colour area from each attachment's OWN extent
	PassMixedExtents,     // rpa_mix: passes whose attachments did not all share an extent
	// ------------------------------------------------------------------------------------------
	// Session 73: how much of the clean loop of VerifyWitness takes the per-word fallback. Session
	// 72 measured that loop at 1.033 ms of wall per frame (53.6 % of the witness) while it carries
	// 11.6 % of the words, and named the fallback at pipelineCache.cpp:662-673 as the suspect
	// without measuring how often it fires. One Add per fallback run, no decision changed, so an
	// ordinary base run sizes the ceiling of gate "dawitfb" before the gate is ever armed.
	// Identities: da_cl_fb <= da_runs_clean, da_cl_fb_w <= da_clean_words, and at dawitloop=1
	// both are 0 because the loop did not run.
	DrawAheadCleanFallback,      // da_cl_fb: clean runs whose page lookup failed
	DrawAheadCleanFallbackWords, // da_cl_fb_w: words compared one at a time because of it
	// Session 73: da_cl_fb read EXACTLY ZERO on the first run, so the clean loop's 1.033 ms is not
	// its per-word fallback. These three say what it is instead. CleanBackingPage looks a page up
	// in an 8-entry per-call table (CALL_SLOTS) while the live reader gets a 4096-entry table that
	// lives for the whole frame, and every miss pays IsGpuCleanRange over the page - IsGpuThread +
	// BufferCache::HasGpuDirtyBytes + TextureCache::IsRegionGpuModified.
	// Reading: da_cl_look - da_runs_clean is the specialization reader's share of the calls;
	// da_cl_miss / da_cl_look is the 8-slot table's miss rate; da_cl_fail >= da_cl_fb always.
	DrawAheadCleanLookup, // da_cl_look: CleanBackingPage calls
	DrawAheadCleanMiss,   // da_cl_miss: of those, the ones that paid the range predicate
	DrawAheadCleanFail,   // da_cl_fail: of those, the ones where the page was not GPU-clean
	// Session 73, W7 (gate "dawitcp"), the two halves of that predicate it makes cheaper.
	DrawAheadCleanLive,   // da_cl_live: clean misses whose translation came from the live table
	TexGpuModifiedCalls,  // tgm_call: TextureCache::IsRegionGpuModified calls
	TexGpuModifiedHint,   // tgm_hint: of those, answered by the lock-free page hint alone
	// ------------------------------------------------------------------------------------------
	// Session 74, M4 / G-split. The transport fork's two open numbers, neither of which any
	// existing log answers. rng_inpass / rng_total is the share of baton range HAND-OFFS (the
	// first iteration of each ProcessPm4Baton call is a slice start, not a hand-off, and is not
	// counted) that would force a render-pass close and reopen if the two sides recorded into
	// separate command buffers - session 71 measured open+close at 1.537 us of GPU. cram_write
	// decides 87.8 % of the 55 955-byte register fork, because m_const_ram is 49 152 of it and may
	// well be dead in this title; it is NOT gated on m4baton and is live in any traced run.
	BatonRangesTotal,  // rng_total: baton range hand-offs (iterations after the first)
	BatonRangesInPass, // rng_inpass: of those, taken with a render pass open
	ConstRamWrites,    // cram_write: CommandProcessor::WriteConstRam calls
	// ------------------------------------------------------------------------------------------
	// Session 74: how often would a MONOTONIC GPU-dirty generation have to move? It is the witness
	// a clean-page table would need to survive the AheadTake call, the way PersistentLive survives
	// the frame under BackingMapEpoch. IsGpuCleanRange (kernel/memory.cpp:1031-1040) reads exactly
	// two things - BufferCache::HasGpuDirtyBytes and TextureCache::IsRegionGpuModified - so these
	// four counters close the whole surface. A generation bumped at every site is already refuted:
	// rt_fast_ok alone is 2.0-2.5x the clean-table count. Only the TRANSITION-guarded form can
	// work, and dg_img + dg_buf is exactly its bump rate. Compare against da_hit + da_miss.
	GpuDirtyGenImage,     // dg_img: image clean->dirty transitions (inside Image::MarkGpuModified)
	GpuDirtyGenImageClr,  // dg_img_cl: image dirty->clean transitions
	GpuDirtyGenBuffer,    // dg_buf: GPU-modified-range Adds that actually grew the covered set
	GpuDirtyGenBufferAll, // dg_buf_all: all GPU-modified-range Adds, the denominator
	// Session 74, W8 step one. A probe, not a table: it answers "would a persistent clean-page
	// table keyed on (BackingMapEpoch, GpuDirtyGen) have held this page?" without building one.
	// da_cl_pmiss IS the predicted post-patch da_cl_miss, against today's 15 086. It does not
	// model Pages::last, so it can only OVER-count misses - conservative for the decision.
	DrawAheadCleanProbeMiss, // da_cl_pmiss: the probe would have missed
	DrawAheadCleanProbeDrop, // da_cl_pdrop: the probe's stamp moved (generation or map epoch)
	// Session 74, W8, the table itself (gate "dawitcg").
	DrawAheadCleanDrop, // da_cl_drop: the persistent clean table was tag-invalidated. Reachable
	                    // only through the gated bind, so it reads exactly 0 with the gate off and
	                    // is the arming proof. It cannot say WHICH witness moved: the bind checks
	                    // both and the per-lookup re-check sees only the generation.
	DrawAheadCleanBad,  // da_cl_bad: dawitcgcheck disagreements - MUST read 0. guards.py check 2
	                    // judges it (patch_guards_cleangen.py adds the row).
	// ------------------------------------------------------------------------------------------
	// Session 73, C1 (gate "imgfuse"). Session 72's c1_si_dt says how many uploads COULD have had
	// their detile fused by format and usage alone; these say how many actually qualify once the
	// destination subresource, the channel swap and the image shape are taken into account, and
	// they are counted with the gate OFF so an ordinary base run sizes the reachable share of the
	// 1241.7 us ceiling before a single pipeline is compiled.
	// Identity: c1_fz_ok + c1_fz_swap + c1_fz_shape + c1_fz_fmt == c1_si_dt.
	C1FuseReady,        // c1_fz_ok: passes every clause of the fuse predicate
	C1FuseReadyKb,      // c1_fz_ok_kb: KiB of guest source in that cell
	C1FuseReadyCopyKb,  // c1_fz_ok_cp_kb: KiB the copy would have moved - the ceiling's own weight
	C1FuseSwap,         // c1_fz_swap: declined, a bgra16 channel swap sits between detile and copy
	C1FuseShape,        // c1_fz_shape: declined, volume / 1D / MSAA / block texel / region shape
	C1FuseFormat,       // c1_fz_fmt: declined, no mandatory UINT view format of that element size
	// The arming proof. Identically zero while imgfuse=0; equal to c1_fz_ok while imgfuse=1.
	C1Fused,            // c1_fuse: uploads whose detile wrote the image directly
	C1FusedKb,          // c1_fuse_kb: KiB of guest source in those
	// ------------------------------------------------------------------------------------------
	// Session 75, gate "pfhint". pf_l1 is the ARMING PROOF and nothing else: the number of
	// AheadTake prefetch blocks that issued the L1 form. It must equal da_hit in the armed arm and
	// read exactly 0.000 in the other, the same shape as c1_fuse against c1_fz_ok.
	PrefetchHintL1Takes, // pf_l1: takes whose prefetch block issued __builtin_prefetch(..., 3)
	// Session 75, W3 - the per-vector byte cap of PrefetchVectorData, knob "pfcap". da_pf_b is what
	// the eleven vectors of one take OFFER; da_pf_cap_b is what the cap lets through, the sum of
	// min(bytes, pfcap) with whatever value the knob currently holds - NOT a fixed 192. Their
	// DIFFERENCE is the truncated remainder. At the shipped pfcap=1024 the ratio reads 94.4 %
	// (acc76a); at the 192 that shipped before session 76 it read 58.8 %. The pair is also the
	// ARMING PROOF of any ABBA on the knob: the ratio must move between the arms or it did not arm.
	DrawAheadPrefetchBytes,    // da_pf_b: bytes offered to PrefetchVectorData, summed over a take
	DrawAheadPrefetchCapBytes, // da_pf_cap_b: ... of those, the bytes the "pfcap" cap prefetched
	// ------------------------------------------------------------------------------------------
	// Session 75, M4 second question. A SUBMISSION SLICE is one call of CommandProcessor::Process
	// that reaches ProcessPm4 with a non-empty buffer stack. Session 74 showed a baton range
	// boundary is a pass boundary 93-94 % of the time and that the boundaries collapse onto ~12.5
	// slices a frame invariant in L; these say what a slice IS. All of them work at m4baton=0 and
	// fire about 12.5 times a frame, so they cost nothing.
	SliceTotal,         // slc_total: submission slices (predicted in advance: 11.0-14.0 / frame)
	SliceInPass,        // slc_inpass: ... taken with a render pass open (bounded in [0, 2.01])
	SliceResume,        // slc_resume: ... resuming a cursor the previous slice left, so not a fork point
	SliceSameProcessor, // slc_cp_same: ... whose predecessor ran on the same CommandProcessor
	SliceNewBuffer,     // slc_newcb: ... at which the scheduler tick moved (floor 0.838, not 0)
	// The concentration, which is what actually decides whether a two-way slice split has a prize.
	// One bucket per slice by the draws + dispatches it executed (m_range_draws delta, whose three
	// increment sites are the same three that feed Counter::Draws and Counter::Dispatches).
	SliceDraws0, // slc_d0: slices that executed < 128 draws+dispatches
	SliceDraws1, // slc_d1: 128 .. 511
	SliceDraws2, // slc_d2: 512 .. 1023
	SliceDraws3, // slc_d3: 1024 .. 2047
	SliceDraws4, // slc_d4: >= 2048
	// ------------------------------------------------------------------------------------------
	// Session 83, W1: where bda_us 2 181 us a frame goes.  Session 82 proved it is NOT the
	// 18 582 region visits - gate "bdabits" armed to 99.95 % of them and read -50.8 +- 87.5 us,
	// inside the A/A floor.  These four divide the 181 PrepareBda calls of a frame instead:
	// how many are served by the three-epoch cache without scanning at all (bda_hit), how many
	// mapped ranges the scanning ones walk (bda_rng), how many of those hold no registered
	// buffer (bda_rng_e, an early return before any region is touched), and how many dirty
	// ranges the walk then feeds to the upload pass (bda_drng) - which is also the number of
	// m_buffers map lookups it costs, the candidate the session-82 FACTS names next.
	// All four are Add-style, so unlike bda_us (a Scope, which needs TimingsEnabled) they read
	// in a KYTY_FRAME_TRACE=lite measurement run.
	BdaPrepareHits, // bda_hit: PrepareBda calls served by the three-epoch cache
	BdaRanges,      // bda_rng: SynchronizeBuffersInRange calls
	BdaRangesEmpty, // bda_rng_e: ... of those, mappings with no registered buffer intersecting
	BdaDirtyRanges, // bda_drng: dirty ranges fed to SynchronizeBuffersOfDirtyRanges
	// Session 83: the arming proof of knob "mutwide" - the wide MutScopes that armed. 0.000 at
	// mutwide=0, and 2*draws + dispatches + bda_n at mutwide=15.
	MutWideScopes,  // mw_n: MutScopes constructed with an arming counter and an active bit
	// Session 83, gate "bindpack". tnull_hit + tnull_miss is the null-T# population and must be
	// EQUAL in both arms: it is the same predicate either way. tnull_hit is 0.000 at bindpack=0.
	NullTexHits,    // tnull_hit: null-T# resolutions served by the nine-entry memo
	NullTexMisses,  // tnull_miss: ... and those that had to call FindImage
	BindKindMasks,  // bp_mask: binding-kind masks computed, one per prepared stage
	BindPackBad,    // bp_bad: gate "bindpackcheck" disagreements - must read 0
	// Session 83, gate "plkstat": PipelineCache::m_mutex, per acquisition site. WAIT is time
	// this thread was blocked by another holder; HOLD is time it held the lock out. They are
	// different quantities and are never summed. pl_prog_* is inside mh_prog_us, pl_pipe_* is
	// inside mh_emit_us and pl_cs_* is inside mh_disp_us - the three do not share a container.
	PipeLockProgWaitNs, // pl_prog_wait_us: GetGraphicsPrograms, blocked
	PipeLockProgHoldNs, // pl_prog_hold_us: ... holding
	PipeLockProgN,      // pl_prog_n: ... acquisitions
	PipeLockPipeWaitNs, // pl_pipe_wait_us: GetGraphicsPipeline, blocked
	PipeLockPipeHoldNs, // pl_pipe_hold_us: ... holding
	PipeLockPipeN,      // pl_pipe_n: ... acquisitions
	PipeLockCsWaitNs,   // pl_cs_wait_us: GetComputeProgram, blocked
	PipeLockCsHoldNs,   // pl_cs_hold_us: ... holding
	PipeLockCsN,        // pl_cs_n: ... acquisitions
	// Session 84, gate "slotstat" (MEASUREMENT ONLY): the route-C census.  All Add-style, so
	// unlike bda_us they read in a KYTY_FRAME_TRACE=lite measurement run.  Counted in
	// CommitBindings, per prepared stage, where every value a descriptor write consumes is
	// final; "previous draw" therefore means previous COMMITTED draw (an AsyncPipelines skip
	// never reaches this site) and, for the Pixel stage, previous PIXEL-ACTIVE draw, because a
	// depth-only draw resets that stage.  sl_img_same demands view AND layout (an identical
	// descriptor); sl_img_view demands only the view (an identical resolution) - ResetBindings
	// re-derives the layout every draw, so the two are different ceilings.
	SlotStages,         // sl_stage_n: prepared stages examined
	SlotStagesAll,      // sl_stage_all: ... of those, stages where EVERY slot repeated
	SlotImages,         // sl_img_n: image slots examined (identity: == b_texn)
	SlotImagesSame,     // sl_img_same: ... same VkImageView and same layout
	SlotImagesView,     // sl_img_view: ... same VkImageView, layout ignored
	SlotSamplers,       // sl_smp_n: sampler slots examined (no prior denominator existed)
	SlotSamplersSame,   // sl_smp_same: ... same VkSampler
	SlotBuffers,        // sl_buf_n: buffer slots examined (identity: == bb_n)
	SlotBuffersSame,    // sl_buf_same: ... same {VkBuffer, offset, range}
	SlotBuffersRing,    // sl_buf_ring: ... of those, stream-ring views, which CANNOT repeat
	SlotOverflow,       // sl_over: slots past the table bounds, not measured; must read 0
	// Session 84, gate "bindpack", the package's fourth item (PLAN_82_bind.md item 11).
	// bp_dsc arms D1 and reads 0.000 in the arm at 0; bp_local_make and bp_local_skip arm
	// item 9 of session 83, which shipped with no arming counter, and are deliberately ONE Add
	// in EACH arm so the proof costs the same on both sides of the contrast.
	BindPackDescSets,   // bp_dsc: commits that took the cached descriptor-set numbers
	BindPackLocalMake,  // bp_local_make: draws/dispatches that built the unread GraphicsBindings
	BindPackLocalSkip,  // bp_local_skip: ... and those that did not
	// Session 84, gate "bdalap" (MEASUREMENT ONLY): the two halves of PrepareBda.  Timed with
	// the plkstat idiom - a timestamp under Enabled(), differenced by hand - because both Scope
	// and Lap take theirs under TimingsEnabled(), which is false in a lite measurement run, and
	// that is why bda_us has never been read in one.  bda_probe_us is paid by every call,
	// bda_scan_us only by the calls the three-epoch cache does not serve.
	BdaProbeNs,         // bda_probe_us: entry through the three-epoch comparison
	BdaScanNs,          // bda_scan_us: the ForEach walk of the mapped ranges
	BdaLaps,            // bda_lap_n: the arming proof; == bda_n on, 0 off
	// Session 85, gate "bindlap" (MEASUREMENT ONLY): the binding phase timed with the
	// plkstat idiom, two timestamps per STAGE.  bl_img_n and bl_buf_n are the denominators
	// the unit price is divided by and are also the arming identities (== b_texn, == bb_n).
	BindLapStages,      // bl_stage_n: RebindImages calls; the arming proof and the regressor
	BindLapPrepareNs,   // bl_prep_us: PrepareBindings, whole body (full resolution)
	BindLapPrepares,    // bl_prep_n: ... calls
	BindLapImageNs,     // bl_img_us: RebindImages, whole body
	BindLapImages,      // bl_img_n: image slots in it (identity: == b_texn)
	BindLapBufferNs,    // bl_buf_us: RebindBuffers, whole body
	BindLapBuffers,     // bl_buf_n: buffer slots in it (identity: == bb_n)
	BindLapTransitNs,   // bl_tr_us: CommitBindings, the image transitions
	BindLapWriteNs,     // bl_wr_us: ... the write-list build
	BindLapEmitNs,      // bl_em_us: ... the emit (update + bind)
	BindLapCommits,     // bl_cmt_n: commits timed (graphics only, like cb_pool_n)
	// Session 86, gate "bindlap", task D3 (ROADMAP.md route D3): the 3 991 us a frame of
	// PrepareBindings, split by resource kind.  A rolling mark chain - the three loops are
	// separate and contiguous and the function has one exit, so the parts are additive by
	// construction and the remainder (prologue, reserves, has_gds, and these marks) is
	// DERIVED rather than counted.
	BindLapResolveNs,   // bl_res_us: the image loop, ResolveTextureWith AND BindImage
	BindLapResolves,    // bl_res_n: image slots in it (identity: == bl_img_n, 1:1 calls)
	BindLapSamplerNs,   // bl_smp_us: the sampler loop, NativeSampler
	BindLapSamplers,    // bl_smp_n: sampler slots in it
	BindLapDataNs,      // bl_sd_us: the shader_data copy loop
	// Session 85, gate "bdasplit" (MEASUREMENT ONLY): the division of the scan half of
	// PrepareBda.  bda_first_us is the one that tests the FIXED cost directly.
	BdaSplitBoundNs,    // bda_bound_us: the two m_buffers descents, paid by every call
	BdaSplitBounds,     // bda_bound_n: ... those calls (identity: == bda_rng)
	BdaSplitWalkNs,     // bda_walk_us: SynchronizeBuffersByRegion, whole
	BdaSplitWalks,      // bda_walk_n: ... its calls
	BdaSplitCollectNs,  // bda_collect_us: CollectCpuModifiedRanges (region lock + bit walk)
	BdaSplitUploadNs,   // bda_up_us: SynchronizeBuffersOfDirtyRanges (buffer walk + copies)
	BdaSplitUploads,    // bda_up_n: ... its calls (identity: == bda_scan)
	BdaSplitFirstNs,    // bda_first_us: the frame's FIRST scanning PrepareBda, charged apart
	BdaSplitFirsts,     // bda_first_n: ... those calls (one a frame while the scene is settled)
	BdaSplitLateNs,     // bda_late_us: every later scanning PrepareBda of the same frame
	BdaSplitLates,      // bda_late_n: ... those calls
	// Session 85, gate "slotstat": the three biases FACTS s84 3.5 left unquantified.  The
	// counters above keep their logic unchanged, so the s84 ratios reproduce beside these and
	// the DIFFERENCE is the measured bias.
	SlotShaderChanges,  // sl_shader_chg: stage commits whose shader differs from the previous
	                    //                commit on the same row - bias 3, measured
	SlotImagesSameShader,   // sl_img_same_sh: sl_img_same, but only when the row's previous
	                        //                 commit ran the SAME shader - bias 3, eliminated
	SlotSamplersSameShader, // sl_smp_same_sh: the same for samplers
	SlotBuffersSameShader,  // sl_buf_same_sh: ... and for buffers
	SlotStagesAllShader,    // sl_stage_all_sh: sl_stage_all under the same restriction
	SlotBuffersNull,    // sl_buf_null: slots that are the CONSTANT null descriptor
	                    //              {GetBuffer(NULL_BUFFER_ID).Handle(), 0, 16} - bias 1's
	                    //              unmeasured half; they repeat by construction
	SlotImagesNull,     // sl_img_null: image slots resolved from a null T# (desc.info.data
	                    //              empty), per SLOT rather than per resolution
	SlotImageElements,  // sl_img_elem: sum of max(1, mip_views.size()) - the descriptor
	                    //              ELEMENTS behind the image BINDINGS - bias 2
	SlotSamplerElements, // sl_smp_elem: sampler elements the write list actually emits
	// Session 86, gate "slotstat" (ROADMAP.md route C, its last idea): duplicates WITHIN one
	// stage.  The witness a repeating image slot re-evaluates is per IMAGE; these say how much
	// of it could be evaluated once an image instead of once a slot.
	SlotImageDups,      // sl_img_dup: image slots whose image_id equals an EARLIER slot of the
	                    //             SAME stage.  Not the same quantity as sl_img_view, which
	                    //             compares the same slot INDEX against the previous draw.
	SlotImageDupViews,  // sl_img_dupv: ... of those, slots whose VkImageView also matches - a
	                    //              byte-identical descriptor element, and the exploitable
	                    //              half, because a duplicate with another desc still runs
	                    //              FindTexture
	SlotImageDupStages, // sl_img_dstage: stages holding at least one duplicate
	SlotImageSq,        // sl_img_sq: sum over stages of n(n-1)/2 - the second moment of the
	                    //            per-stage image count AND the exact worst case of the
	                    //            duplicate scan itself
	SlotBad,            // sl_bad: gate "slotstatcheck" - element counts that disagree with the
	                    //         compiled layout.  MUST read 0.
	// Session 85, gate "bindpack2" (PLAN_82_bind.md item 6a) and its self-check.
	BufEpochFastHits,   // be_fast: ObtainBuffer answered the upload-epoch question itself
	                    //          instead of asking SynchronizeBuffer the same question
	BufEpochFastRaces,  // be_race: ... and the epoch HAD moved between the two reads.  This is
	                    //          the window the change widens, measured rather than assumed
	BufEpochFastBad,    // bp2_bad: the epoch did NOT move and the recomputation still
	                    //          disagreed - a contradiction.  MUST read 0.
	// Session 86, gate "proglap" (MEASUREMENT ONLY, ROADMAP.md route D2): the phases of
	// mh_prog_us that FrameStats::Lap cannot report under KYTY_FRAME_TRACE=lite, re-emitted
	// on the LapScope idiom.  The lock half is plkstat's and the memo compare is
	// pmemo_chk_us's; neither is rebuilt here.
	ProgLapPreNs,       // pg_pre_us: GetGraphicsPrograms before the lock.  An UPPER bound on
	                    //            PrepareProgram: it also holds ShaderRegistrations, the
	                    //            keep_snapshots swaps, the mesh-limit block and the clip
	                    //            block
	ProgLapCalls,       // pg_n: ... its calls (identity: == pl_prog_n, exactly)
	ProgLapKeyNs,       // pg_key_us: ProgramCache::Get up to Mark(ProgKeyNs) - the key build
	                    //            or the memo iterator, plus programs.find, plus the
	                    //            translation-cache load on a cold miss (pg_cold_n)
	ProgLapKeys,        // pg_key_n: ... those calls, slot < 2 only
	ProgLapKeyHitNs,    // pg_key_hit_us: the same interval, key_hit only - the numerator of
	                    //                the two-equation solve of pred/03
	ProgLapKeyHits,     // pg_key_hit_n: ... those calls (identity: == pmemo_hit when armed)
	ProgLapGetNs,       // pg_get_us: ProgramCache::Get, whole body, slot < 2 only.  Covers all
	                    //            four of its returns, INCLUDING the Compile path
	ProgLapGets,        // pg_get_n: ... those calls
	ProgLapCold,        // pg_cold_n: ... of those, calls that missed `programs` and reached
	                    //            the translation cache.  Contamination, counted
	ProgLapCompiles,    // pg_compile_n: ... and those that reached Compile.  Milliseconds when
	                    //               it fires; must be ~0 in a settled scene
	// Session 86, gate "drawmerge" (MEASUREMENT ONLY, ROADMAP.md route D4): how many
	// consecutive draws are merge candidates.  Classification is FIRST MATCH WINS in the order
	// below, and a LENGTH change is dm_no, never a silent one-slot difference.
	DrawMergeDraws,     // dm_n: draws classified - the denominator.  dm_n <= draws, because
	                    //       `draws` is counted at the PM4 handler before the early returns
	                    //       and the AsyncPipelines skip.  The gap is quoted, not assumed 0
	DrawMergePipe,      // dm_pipe: ... whose VkPipeline equals the previous classified draw's
	                    //          (cross-check: within 2 % of pmemo_pipe)
	DrawMergeSame,      // dm_same: dm_pipe AND every image, sampler and buffer slot equal AND
	                    //          every shader_data dword equal
	DrawMergePush,      // dm_push: ... all slots equal, shader_data differs
	DrawMergeBuf1,      // dm_buf1: ... images and samplers equal, EXACTLY ONE buffer differs
	DrawMergeNo,        // dm_no: everything else, including every length change
	DrawMergeSameNr,    // dm_same_nr: the same three with stream-ring buffer slots EXCLUDED
	DrawMergePushNr,    //             from the difference count.  ~35 % of buffer slots take a
	DrawMergeBuf1Nr,    //             fresh ring offset every draw by construction (s84: 34.94 %)
	DrawMergeRing,      // dm_ring: buffer slots whose handle is the stream ring
	DrawMergeBufSlots,  // dm_bufn: buffer slots examined - dm_ring's denominator
	DrawMergeImageDiffs,   // dm_img_d: per-slot differences, for the consistency reading
	DrawMergeSamplerDiffs, // dm_smp_d: ... against slotstat, which keys differently and is
	DrawMergeBufferDiffs,  // dm_buf_d: ... written from another function - a reading, NOT an identity
	DrawMergeMesh,      // dm_mesh: mesh draws, bucketed apart: their 6-dword draw_data push
	                    //          block changes by construction and would read as dm_push
	DrawMergeOver,      // dm_over: draws past the table bounds, EXCLUDED from classification
	                    //          rather than truncated into a match.  Must read 0
	DrawMergeBad,       // dm_bad: gate "drawmergecheck" - the field-wise verdict disagreed
	                    //         with the independent memcmp.  MUST read 0
	ProgLapPerms,       // pg_perm: permutations EXAMINED by the find_if (the Add is inside the
	                    //          predicate, so it is work and not the deque's size)
	// Session 87, gate "bindalt" (MEASUREMENT ONLY): the sampled halves of the image loop of
	// PrepareBindings.  An interval that opens after a BindImage and closes after a
	// ResolveTextureWith is exactly one resolve; each carries exactly one mark's overhead, and
	// so does each slot of bl_res_us, so the overhead cancels in bl_res_us/n - bl_rsv_us/n.
	BindAltResolveNs,   // bl_rsv_us: sampled resolve intervals, slot index >= 1
	BindAltResolves,    // bl_rsv_n: ... how many.  Expect ~0.5 x bl_res_n
	BindAltResolve0Ns,  // bl_rsv0_us: the sampled interval at slot index 0, which also contains
	                    //             prepared.images.reserve - separated so that can be said
	BindAltResolve0s,   // bl_rsv0_n: ... how many (one per phase-0 stage with any image)
	// Session 87, gate "proglap" extended (MEASUREMENT ONLY, ROADMAP.md route D2): the five
	// phases of the block session 86 measured as a RESIDUAL (pg_get_us - pg_key_us = 3 764 us a
	// frame) and called "resource materialisation".  A rolling mark chain seeded from the
	// timestamp pg_key_us already takes, closed before each reachable return.  slot < 2 only.
	// NOTE: ProgMaterializeNs is NOT MaterializeResources - it is marked twice and both marks
	// charge everything since ProgKeyNs.  These five are the division it never was.
	ProgLapLocalNs,     // pg_loc_us: the prog_memo write-back, the ResourceSnapshot and
	                    //            ResourceSpecialization locals, read_cache, SrtRuntime
	ProgLapAheadNs,     // pg_ahead_us: AheadNote + AheadTake + AheadCheck.  da_take_us is an
	                    //              independent lite-visible timer of AheadTake INSIDE this,
	                    //              so pg_ahead_us >= da_take_us in every frame and the
	                    //              difference is the price of AheadNote
	ProgLapAheads,      // pg_ahead_n: calls whose lookahead block body ran
	ProgLapMemoNs,      // pg_memo_us: MemoFind + MemoVerify + the push-data check + the hit copy.
	                    //             srtmemo is default 0, so this reads ~0 and is an arming
	                    //             proof rather than a measurement
	ProgLapMemos,       // pg_memo_n: calls whose SRT-memo block body ran
	ProgLapMatNs,       // pg_mat_us: MaterializeResources ON THE DRAW THREAD, under the pipeline
	                    //            cache lock, plus the dropped-plan path
	ProgLapMats,        // pg_mat_n: calls where MaterializeResources was actually invoked - the
	                    //           self-selected population the lookahead MISSED, whose price is
	                    //           not the price of the 97 % it hits
	ProgLapPermPhaseNs, // pg_pm_us: the permutation find_if + MemoStore + the snapshot move
	ProgLapPermPhases,  // pg_pm_n: calls reaching that phase
	// Session 88, knob "bindwit" (MEASUREMENT ONLY): the witness share of a memo-hit
	// ResolveTextureWith.  The sampled interval opens after the previous BindImage and closes
	// either after the resolve returns (bindwit=1) or at the memo-hit decision inside it
	// (bindwit=2).  Both carry exactly one mark overhead, so it cancels in the difference, and
	// the difference is what a per-stage amortisation could skip.
	BindWitNs,          // bl_wit_us: sampled intervals of slots whose resolve took the MEMO-HIT
	                    //            path, slot index >= 1
	BindWits,           // bl_wit_n: ... how many
	BindWitMissNs,      // bl_wnh_us: the same for slots whose resolve did NOT take that path.
	                    //            Identical code at bindwit=1 and at 2, so the two arms must
	                    //            agree - a null control that CAN fail
	BindWitMisses,      // bl_wnh_n: ... how many
	BindWit0Ns,         // bl_wit0_us: the sampled interval at slot index 0, which also contains
	                    //             prepared.images.reserve - excluded from the estimator
	BindWit0s,          // bl_wit0_n: ... how many (one per phase-0 stage with any image)
	// Session 89, gate "takelap" (MEASUREMENT ONLY): the six phases of AheadTake.  The chain
	// is seeded from the timestamp da_take_us already takes (pipelineCache.cpp:3069), so the
	// first mark is free and the six counters below carry FIVE marks of overhead between
	// them, not six.  Early returns - a miss (73.8 a frame) and a late/running slot (0.4 a
	// frame) - leave the chain unclosed ON PURPOSE, which can only make the parts smaller
	// than the whole, never larger.  The TAIL is DERIVED and is never a counter:
	// da_take_us - sum(the six), and it holds slot.taken, the DrawStat mark, the da_hit Add,
	// the return, and the marks themselves.
	TakeLapKeyNs,       // da_t_key_us: ClassOf + Fingerprint + AheadHash + UserDataHash, on
	                    //              every call
	TakeLapProbeNs,     // da_t_prb_us: the probe loop - slot.Matches and the state checks.
	                    //              Take-side probes are da_probe - da_probe_q, which read
	                    //              1.0432 a call in log_dwl88c: the "two-probe" loop is
	                    //              one probe on 95.7 % of calls
	TakeLapPrefetchNs,  // da_t_pfa_us: prefetch pass A (eleven PrefetchVectorData behind gate
	                    //              "daprefetch", 184 477 cache lines a frame) plus the
	                    //              five census Adds that follow it
	TakeLapPrefetchRunNs, // da_t_pfb_us: VerifyWitness entry (skip_loop, BackingMapEpoch,
	                    //              `direct`) plus prefetch pass B - one __builtin_prefetch
	                    //              per live run, 54 855 a frame.  NEITHER value of
	                    //              "dawitloop" skips it, because skip_loop is tested
	                    //              INSIDE the two comparison loops, after this pass
	TakeLapVerifyNs,    // da_t_ver_us: the live-run and clean-run comparison loops and the
	                    //              singles loop (da_singles = 0.000 in this scene).
	                    //              Session 88 priced the two loops at 567.4 + 285.1 =
	                    //              852.5 us a frame on binary 25fd4f2e; this counter
	                    //              contains exactly them plus the loop bookkeeping, so it
	                    //              is a NULL CONTROL THAT CAN FAIL - band [600, 1400] us,
	                    //              and it is cross-binary, so a control, never a measure
	TakeLapTakeNs,      // da_t_cpy_us: CopyAheadResult or the two std::swap, and the slot
	                    //              retire.  92.2 % of hits swap (gate "snapswap", shipped
	                    //              in session 58) and the 7.79 % that copy move 235 B each
	// Session 89, section 3.3 (a debt of docs/next-session-89.md): pg_pm_us reads 462 us a
	// frame at 52.10 ns a call and is UNATTRIBUTED.  The brief names two candidates inside it,
	// PushData::StartFor and the `specialization ==` compare - and OMITS the other three the
	// phase contains: MemoStore, the move-assignment of the whole ResourceSnapshot into
	// input_info.stage, and AdvancePushData.  ONE mark, taken the moment the find_if returns,
	// separates the search from the take.  IT REDEFINES pg_pm_us: from this binary on,
	// pg_pm_us is the TAKE alone and the old quantity is pg_pmf_us + pg_pm_us.  It rides in
	// the "proglap" chain, so it is on in BOTH arms of any run of this session and the two
	// arms agreeing is a free null control.
	ProgLapPermFindNs,  // pg_pmf_us: the permutation find_if - PushData::StartFor,
	                    //            ShaderDataDwords and the specialization compare, over
	                    //            pg_perm / pg_get_n = 1.059 candidates a call
	TakeLapCalls,       // da_t_n: calls that reached the first mark.  Identity:
	                    //         == da_hit + da_miss + da_late + da_stale + da_stale_old
	TakeLapReady,       // da_t_hit_n: of those, calls whose slot was AheadReady, i.e. that
	                    //             reached da_t_pfa_us.  Identity:
	                    //             == da_hit + da_stale + da_stale_old
	// Session 90, knob "bufimp" (ROADMAP.md route D1).  Every one of these is counted only
	// when the knob is non-zero, so its reading in the other arm of the run is EXACTLY
	// zero and the arming proof is free and exact, the way takelap got one in session 89.
	BufImportTries,     // bi_try: UploadCopies calls that attempted the resolution
	BufImportTakes,     // bi_ok: of those, calls where EVERY copy region resolved.  At knob
	                    //        2 these are the uploads that took the import and paid no
	                    //        host memcpy; at knob 1 they took the staging path anyway
	BufImportBytes,     // bi_b: BYTES of the taken uploads.  Bytes - not calls, not KiB;
	                    //       the comparable quantity is sync_up_kb * 1024
	BufImportRegions,   // bi_reg: copy regions resolved (a call has one or more)
	BufImportSplits,    // bi_split: of those, regions that crossed an import chunk boundary
	                    //           and needed more than one copy
	BufImportNoBacking, // bi_noback: regions TryGetBackingPointer refused - not direct
	                    //            memory, or not inside ONE mapping.  One is enough to
	                    //            abandon the whole upload, so this counts uploads lost
	                    //            as much as regions
	BufImportNoChunk,   // bi_nochunk: regions HostImport::Resolve refused (the chunk is not
	                    //             imported yet, or its import failed).  Expected 0 here:
	                    //             the log says all 27 chunks preload before the guest runs
	BufImportBad,       // bi_bad: gate "bufimpcheck" - TryGetBackingPieces disagreed with
	                    //         TryGetBackingPointer.  MUST READ 0
	BufImportResolveNs, // bi_us: wall time of the resolution itself, on the calling thread.
	                    //        This is what the census costs; the memcpy it replaces is
	                    //        inside bda_up_us = 2 118.3 us a frame (blp85a)
	// Session 90, section 3.2 (a debt of docs/next-session-90.md and FACTS s89 section 5):
	// pg_pmf_us is 337.0 us a frame and nobody knows which of its two comparisons it is.
	// Two marks INSIDE the find_if predicate, in the same "proglap" chain, divide it.  They
	// REDEFINE pg_pmf_us, which from this binary on is the loop bookkeeping left over:
	//     pg_pmp_us + pg_pms_us + pg_pmf_us == session 89 pg_pmf_us + the two new marks.
	ProgLapPmPushNs,    // pg_pmp_us: per CANDIDATE - the loop iteration, the ProgLapPerms
	                    //            Add and push_data_start_dword == PushData::StartFor(cursor,
	                    //            layout.ShaderDataDwords()).  NOT StartFor alone: the loop
	                    //            iteration rides in it, and that is named here, not hidden
	ProgLapPmSpecNs,    // pg_pms_us: per candidate - candidate.specialization == specialization
	ProgLapPmPushNo,    // pg_pmp_no: candidates whose push half was FALSE.  With proglap = 1
	                    //            the two halves are evaluated unconditionally so a mark can
	                    //            sit between them, so pg_pms_us contains this many compares
	                    //            the shipped short-circuit would not run.  It is the exact
	                    //            size of that bias, and it is printed
	// Session 90: the arming proof of knob "bufimp" = 2.  Incremented in
	// RecordBufferCopies on the imported branch ONLY, so it is EXACTLY 0 whenever the
	// knob is below 2 - including in the census arm, which pays everything else the
	// import arm pays.  Identity in the import arm: bi_cp == bi_ok.
	BufImportCopies,    // bi_cp: uploads whose copies were issued from imported guest pages
	// Session 91: the guest GPU clock (Sync::ReadReferenceClock), the value every RELEASE_MEM
	// data_sel 3 / COPY_DATA-from-clock writes into guest memory at PM4 parse.
	GpuClockReads,         // gclk_n: guest GPU-clock reads, every mode
	GpuClockPinnedReads,   // gclk_pin: of those, served by KYTY_GPU_CLOCK_PIN (1 or 2).  EXACTLY 0
	                       //           in a process without the pin, == gclk_n with it
	GpuClockAdvance,       // gclk_adv: pinned only - the guest clock's advance between consecutive
	                       //           reads on one thread, TSC ticks
	GpuClockScaledAdvance, // gclk_sadv: the scaled (shipped) clock's advance over the same reads.
	                       //           gclk_adv / gclk_sadv = 1/speed at mode 1, 0.5 at mode 2
	GpuClockBackward,      // gclk_back: pinned reads that went BACKWARDS against the previous one
	// Session 91: the upload memcpy split at ASYNC_COPY_MIN_BYTES, counted where
	// CopyGuestToStaging takes the decision.  Live in every run; bytes are RAW bytes.
	StagingPoolCopies,     // stg_pool_n: upload regions handed to AsyncMemcpy (>= 64 KiB, one mapping)
	StagingPoolBytes,      // stg_pool_b
	StagingPoolNs,         // stg_pool_ns: the caller's time to hand them over (printed raw ns)
	StagingInlineCopies,   // stg_in_n: upload regions < 64 KiB, copied inline
	StagingInlineBigCopies, // stg_inbig_n: >= 64 KiB copied inline - TryGetBackingPointer refused
	StagingInlineBytes,    // stg_in_b: bytes of both inline kinds
	StagingInlineGpuBytes, // stg_in_gpu_b: of those, on the thread registered as ThreadRole::Gpu
	StagingInlineNs,       // stg_in_ns: the inline memcpy on the calling thread (printed raw ns)
	UploadTempCopies,      // up_tmp_n: regions of the temporary-buffer fallback (staging Map failed)
	UploadTempBytes,       // up_tmp_b
	StagingImgPoolBytes,   // stg_img_pool_b: image "staging:no-owner" bytes handed to AsyncMemcpy
	StagingImgInlineBytes, // stg_img_in_b: image "staging:no-owner" bytes copied inline
	BufImportSmallRegions, // bi_reg_small: census regions < 64 KiB of TAKEN uploads (bufimp >= 1)
	BufImportSmallBytes,   // bi_b_small: their bytes; census arm: == stg_in_b while bi_noback = 0
	// Session 91: WaitPendingHostReads, timed with Enabled() so the times live in lite.
	HostReadFree,          // hr_free: counted calls whose tick was already free
	HostReadGpuWaits,      // hr_gpuw: waits on an already submitted buffer
	HostReadGpuWaitNs,     // hr_gpuw_us
	HostReadForced,        // hr_forced: waits that forced the RECORDING buffer's submit
	HostReadForcedNs,      // hr_forced_us: submit + drain + BeginNext
	HostReadSync,          // hr_sync: calls made off the GuestGpu thread (SendCommandSync)
	HostReadSyncNs,        // hr_sync_us: the calling thread's whole stall in SendCommandSync
	HostReadCallNs,        // hr_call_us: every counted call up to the wait's end (not the erase)
	// Session 92, gate "stglap" (default 0, MEASUREMENT ONLY): the split of session 91's
	// stg_pool_ns - the 173.6 us/frame GuestGpu spends handing 40.33 upload regions to the
	// copy pool.  stg_pool_ns is left WHOLE and is the total these parts are checked
	// against; the residual is what no part covers plus the instrument's own price, which
	// is the within-run difference of the two arms.  Nothing here is touched at stglap = 0.
	// Times are RAW NANOSECONDS, like stg_pool_ns and stg_in_ns.
	StagingResolveNs,      // stg_res_ns: TryGetBackingPointer inside CopyGuestToStaging,
	                       //             closed between the resolve and AsyncMemcpy, so only a
	                       //             POOLED region is counted.  A REFUSED resolve pays its
	                       //             mark and records nothing - that population is stg_inbig_n,
	                       //             which reads 0.0000 on every archived arm; if it ever
	                       //             stops reading 0, stg_res_ns undercounts the resolves
	StagingLockNs,         // stg_lock_ns: CopyPool::Enqueue from entry to the end of its
	                       //              lock_guard block - the queue lock and the push_back loop
	StagingWakeNs,         // stg_wake_ns: the notify_one / notify_all after that block
	StagingQueueDepth,     // stg_q: sum of PendingAsyncCopies() sampled BEFORE the enqueue
	                       //        (an atomic load; the queue lock is NOT taken).  Says whether the
	                       //        pool was asleep or already working when the region arrived.
	                       //        COUNTED IN CHUNKS, NOT REGIONS - m_pending counts 1 MiB jobs,
	                       //        so stg_q / stg_pool_n is jobs outstanding per region queued
	StagingUploadCalls,    // stg_up_n: BufferCache::UploadCopies calls in which at least one
	                       //           region went to the pool, so stg_pool_n / stg_up_n is regions
	                       //           per upload and separates the fixed price of an upload from
	                       //           the per-region price
	StagingChunks,         // stg_chunks: sum of ceil(size / CHUNK_BYTES), CHUNK_BYTES = 1 MiB
	                       //             - the jobs the pool really received.
	                       //             TWO POPULATIONS: stg_lock_ns, stg_wake_ns, stg_q and
	                       //             stg_chunks are counted in parallelCopy.cpp and stg_res_ns
	                       //             in CopyGuestToStaging, and BOTH callers of AsyncMemcpy pass
	                       //             there: the buffer uploads (stg_pool_n / stg_pool_b) and the
	                       //             image "staging:no-owner" path (stg_img_pool_b).  They are
	                       //             deliberately NOT separated in code
	// Session 92b, gate "stglap" (default 0): stg_wake_ns divided by the branch that
	// took it.  stg_wake_ns stays WHOLE - the same interval is added twice, once to the
	// total and once to its branch - so both identities hold BY CONSTRUCTION:
	//     stg_wake1_ns + stg_waken_ns == stg_wake_ns
	//     stg_wake1_n  + stg_waken_n  == the enqueues (stg_pool_n plus the image
	//                                    "staging:no-owner" enqueues, the same two
	//                                    populations stg_chunks already carries)
	// They price apart the 71.2 % of regions that are one chunk and take notify_one
	// from the 28.8 % that are more and take the broadcast (knob "copywake" = 0) or up
	// to one notify_one per chunk (copywake >= 1).
	StagingWakeOneNs,      // stg_wake1_ns: the notify of a ONE-chunk enqueue
	StagingWakeOneCalls,   // stg_wake1_n:  how many of those
	StagingWakeManyNs,     // stg_waken_ns: the notify of a MULTI-chunk enqueue
	StagingWakeManyCalls,  // stg_waken_n:  how many of those
	// Session 92b, gate "stglap" AND knob "copywake" = 2: the price of the worker spin,
	// paid on copy-worker cores and not on GuestGpu.  Both read EXACTLY 0 below
	// copywake = 2, where the spin is not compiled out but is never entered.
	StagingSpinNs,         // stg_spin_ns: the whole time copy workers spent spinning
	                       //              instead of sleeping, summed over the workers.
	                       //              A timed-out spin is about WORKER_SPIN_NS, so
	                       //              stg_spin_ns / 20000 - stg_spin_hit is roughly
	                       //              the number of spins that caught nothing
	StagingSpinHits,       // stg_spin_hit: spins that ended because m_pending ROSE above
	                       //               the lowest value that spin had seen, i.e. a
	                       //               chunk was queued while the worker stayed
	                       //               awake.  It does NOT claim this worker then
	                       //               copied it - the wait predicate under the queue
	                       //               lock decides that, and another worker may get
	                       //               there first - so it is an UPPER BOUND on the
	                       //               kernel wake-ups the spin saved
	// Session 93, gate "bdacap" (MEASUREMENT ONLY, pred/01_bdacap.md): the class every
	// buffer descriptor slot of a draw belongs to, decided in NativeStorageBuffer,
	// EXACTLY ONE per call, first match wins in the order written here.  formatted and
	// const-bank are decided AHEAD of the ring because neither can be expressed through a
	// device address wherever its bytes happen to live.  The five sum to the calls, which
	// is checked against bb_n (control A2).  All ten below read EXACTLY 0 unless the gate
	// is armed -- not one of them is Add-ed on the unarmed path.
	BdaCapNull,         // bc_null: address == 0 || size == 0, the early return - no buffer
	BdaCapFormatted,    // bc_fmt:  resource.formatted - a texel buffer needs a descriptor
	BdaCapConstBank,    // bc_cb:   PackedStrideConstBank - a uniform view needs a descriptor
	BdaCapRing,         // bc_ring: the slot got a stream-ring handle (either aligned copy, or
	                    //          ObtainBuffer's own ring return), so its offset is new every
	                    //          draw by construction and an address buys nothing
	BdaCapOk,           // bc_ok:   everything else - a cached buffer with a stable handle.
	                    //          THE CANDIDATE POPULATION
	BdaCapOkBytes,      // bc_ok_b: the guest ranges of the bc_ok slots, RAW BYTES
	BdaCapOkNs,         // bc_ok_ns:  RAW ns NativeStorageBuffer spent on the bc_ok slots - the
	                    //            ceiling measured directly, not a rate times a population
	BdaCapAllNs,        // bc_all_ns: the same timer over all five classes, so the parts can be
	                    //            checked against the whole and against bb_us (control A3)
	BdaCapDmaDraws,     // bc_dma: draws where at least one stage already sets info.uses_dma,
	                    //         i.e. where PrepareBda has already run and a converted slot
	                    //         would cost no new binding
	// Session 93, gate "bdacap" AND gate "drawmerge" (armed in BOTH arms of the contrast,
	// so its price cancels): of the draws dm_buf1_nr counts - same pipeline, same shape,
	// images and samplers equal, EXACTLY ONE non-ring buffer slot different - those whose
	// one differing slot NativeStorageBuffer classified bc_ok.
	DrawMergeBuf1Ok,    // dm_buf1_ok
	// Session 94, gate "bdacap": RAW ns NativeStorageBuffer spent on the bc_cb slots, the
	// const-bank uniform views BDA cannot express (58 % of all buffer slots in s93).
	BdaCapConstBankNs,  // bc_cb_ns
	// Session 94, gate "mergecost" (MEASUREMENT ONLY, pred/01_mergecost.md).  A draw is
	// ARMED when the gate was on at its entry; its PRE-CLASS time runs from right after the
	// render mutex to just before NoteDrawMerge, its POST-CLASS time from just after
	// NoteDrawMerge to the exit of ExecutePreparedDraw minus the census's own time.  P is
	// "the post-conversion signature equals the previous graphics commit's under the same
	// pipeline layout": bc_ok buffer entries masked, every other descriptor kept.  All times
	// are RAW ns.  Every one reads 0 unless the gate is armed.
	MergeCostDraws,        // mc_n:        armed draws that reached the class point
	MergeCostPreNs,        // mc_pre_ns:   mutex -> class point, all armed draws
	MergeCostPostNs,       // mc_post_ns:  class point -> exit, census excluded
	MergeCostCensusNs,     // mc_dm_ns:    NoteDrawMerge's own time (the drawmerge census)
	MergeCostSigNs,        // mc_sig_ns:   the signature census's own time
	MergeCostSigDraws,     // mc_sig:      graphics commits whose signature was built
	MergeCostBad,          // mc_bad:      commits whose walk ran out of bounds (not compared)
	MergeCostOkSlots,      // mc_okslot:   bc_ok buffer entries masked in the signatures
	MergeCostSame,         // mc_p:        P - the converted draw could reuse the previous set
	                       //              (same layout DEFINITION, same command buffer, every
	                       //              descriptor equal after masking the convertible slots)
	MergeCostSamePipe,     // mc_p_pipe:   P and the same VkPipeline as the previous commit
	MergeCostSameEqPipe,   // mc_p_eq:     ... and even the bc_ok entries equal (set equal TODAY)
	MergeCostOkDraws,      // mc_ok:       armed draws NoteDrawMerge classified dm_buf1_ok
	MergeCostSameOk,       // mc_p_ok:     mc_ok and P
	MergeCostPrePNs,       // mc_pre_p_ns
	MergeCostPostPNs,      // mc_post_p_ns
	MergeCostPreOkNs,      // mc_pre_ok_ns
	MergeCostPostOkNs,     // mc_post_ok_ns
	MergeCostTransitNs,    // mc_tr_ns:    CommitBindings image transitions (+ GDS check)
	MergeCostWriteNs,      // mc_wr_ns:    ... write-list build (+ push-data copy)
	MergeCostEmitNs,       // mc_em_ns:    ... set hand-out + bindings packet / Vulkan calls
	MergeCostTransitPNs,   // mc_tr_p_ns:  the same three over the P commits only
	MergeCostWritePNs,     // mc_wr_p_ns
	MergeCostEmitPNs,      // mc_em_p_ns
	// Why a signature differed (a commit may carry several; none of these is P):
	MergeCostDiffFirst,       // mc_d_first:   no previous commit to compare with
	MergeCostDiffShape,       // mc_d_shape:   pipeline layout, stages, kinds or counts
	MergeCostDiffImage,       // mc_d_img:     an image view or layout
	MergeCostDiffSampler,     // mc_d_smp:     a sampler
	MergeCostDiffRing,        // mc_d_ring:    a stream-ring buffer entry (new offset a draw)
	MergeCostDiffBuffer,      // mc_d_buf:     a non-ring buffer entry that is not bc_ok
	MergeCostDiffSrt,         // mc_d_srt:     the flattened-SRT or shader-data upload
	MergeCostDiffFixed,       // mc_d_fix:     GDS, BDA page table or fault buffer
	MergeCostDiffRingSrtOnly, // mc_d_rs:      differed ONLY in ring and/or SRT entries
	// Session 94, gate "bdaall" (MEASUREMENT ONLY, pred/02_bdaall.md): PrepareBda calls
	// made ONLY because the gate is armed (no stage of the draw/dispatch set uses_dma).
	BdaAllCalls,           // bda_all_n
	// Session 94, second patch (review of the first, before any run):
	MergeCostDiffCb,       // mc_d_cb:     the scheduler tick moved - a new command buffer
	MergeCostHasRing,      // mc_has_ring: commits with at least one unmasked ring entry
	MergeCostHasSrt,       // mc_has_srt:  commits with a flattened-SRT or shader-data upload
	MergeCostSamePush,     // mc_p_push:   P on a push-descriptor pipeline
	MergeCostPostPOkNs,    // mc_post_pok_ns: post-class time of draws that are P AND dm_buf1_ok
	MergeCostMaskOk,       // mc_mask_ok:  masked (convertible) entries whose bdacap class is Ok
	MergeCostMaskOther,    // mc_mask_x:   masked entries of any other class (ring, null, none)
	MergeCostWrittenSlots, // mc_wslot:    non-texel non-const-bank entries KEPT because written
	MergeCostPacket,       // mc_pkt:      commits on the recpack path (record thread does Vulkan)
	BdaCapOkWritten,       // bc_ok_w:     bc_ok slots that are written or atomic (gate bdacap)
	BdaCapOkWrittenNs,     // bc_ok_w_ns:  their RAW ns - s93's Ceiling_bind counted them
	BdaAllDispatch,        // bda_all_disp: the dispatch half of bda_all_n
	BdaAllNoCandidate,     // bda_all_skip: gate on, no uses_dma, no convertible slot - no call
	FaultProcN,            // fbp_n:       ProcessFaultBuffer calls from the garbage collector
	FaultProcNs,           // fbp_ns:      their RAW ns (Enabled(), lite-live)
	// Session 95, gate "framerep" (MEASUREMENT ONLY).  All RAW counts / ns.
	FrameRepDraws,         // fr_n:        draws the census saw with framerep armed
	FrameRepId1,           // fr_id1:      H_ident present in the multiset of frame N-1
	FrameRepId2,           // fr_id2:      ... of N-2
	FrameRepId3,           // fr_id3:      ... of N-3
	FrameRepPay1,          // fr_pay1:     H_pay (H_ident + payload bytes) present in N-1
	FrameRepFull1,         // fr_full1:    H_full (H_pay + draw args + VB/IB) present in N-1
	FrameRepFull2,         // fr_full2:    ... of N-2
	FrameRepFull3,         // fr_full3:    ... of N-3
	FrameRepIdNs,          // fr_id_ns:    the draw brackets (pre+post) of the fr_id1 draws
	FrameRepPayNs,         // fr_pay_ns:   ... of the fr_pay1 draws
	FrameRepFullNs,        // fr_full_ns:  ... of the fr_full1 draws
	FrameRepAllNs,         // fr_all_ns:   ... of ALL fr_n draws - the rule's denominator
	FrameRepRing,          // fr_ring:     fr_id1 hits carrying at least one ring entry
	FrameRepSigNs,         // fr_sig_ns:   the framerep walk's own time (post-class side)
	FrameRepPreNs,         // fr_pre_ns:   the payload hashing's own time (pre-class side)
	FrameRepPayBytes,      // fr_pay_b:    bytes hashed as SRT / shader-data payload
	FrameRepPayN,          // fr_pay_n:    payload hashes taken
	FrameRepBad,           // fr_bad:      the second walk did not line up (must read 0)
	FrameRepOverflow,      // fr_over:     a per-frame table ran out of room (must read 0)
	// Session 95 repair (pred/02_framerep_ring.md): two more readings of the SAME walk,
	// counted beside the strict one, so one run says which of them repeats.
	FrameRepIdR1,          // fr_id1r:     H_identr (ring-served convertible slots masked)
	FrameRepIdR2,          // fr_id2r:     ... in N-2
	FrameRepIdR3,          // fr_id3r:     ... in N-3
	FrameRepIdRNs,         // fr_idr_ns:   the draw brackets of the fr_id1r draws
	FrameRepIdM1,          // fr_id1m:     H_identm (ALL convertible slots masked, s94's)
	FrameRepIdMNs,         // fr_idm_ns:   the draw brackets of the fr_id1m draws
	FrameRepOkRing,        // fr_okring:   draws with >= 1 ring-served convertible slot
	FrameRepOkSlots,       // fr_okslot:   convertible slots the walk saw
	FrameRepImgN,          // fr_img:      image-view values the walk saw
	FrameRepBufN,          // fr_buf:      non-ring buffer values the walk saw
	// Session 96, gate "pathlap" (MEASUREMENT ONLY, pred/01_pathlap.md): the two splits
	// ROADMAP.md:1051-1052 names as part of M3.  Every one of these is written by PathLap,
	// which times under Enabled() and not TimingsEnabled(), so unlike the DrawVertexNs /
	// DrawAcquireRtNs / DrawPipelineNs / DrawCommitNs / DrawEmitNs chain beside it they are
	// not identically zero in a KYTY_FRAME_TRACE=lite run.  Raw ns, printed raw.
	// (a) OUTSIDE the render mutex.  pl_proc_ns is the whole submission on the GuestGpu
	// thread, so the residue is
	//     pl_proc_ns - 1000 * (a_hold_us - mh_pres_us) - sum(the named ones)
	// and THAT residue is the 4.05 ms no session has ever attributed.  THE FACTOR 1000 IS NOT
	// DECORATION: every pl_* here is RAW NANOSECONDS (micros=false in videoOut.cpp's table),
	// while a_hold_us and mh_pres_us print in MICROseconds (micros=true).  Taken off the
	// FrameTrace-x line without it, the formula is out by three orders of magnitude.
	// `named` is pl_pref + pl_eop + pl_bar + pl_sub + pl_gc + pl_cmd.  It does NOT include
	// pl_look: LookaheadSubmission's only caller is GuestGpu::Enqueue (graphicsRun.cpp:630),
	// which runs on the GUEST SUBMIT thread, outside GuestGpu::Process entirely, so its time
	// is not inside pl_proc_ns and subtracting it would subtract another thread's work from
	// this one's.
	PathProcNs,   // pl_proc_ns: wall of GuestGpu::Process, the whole submission
	PathProcN,    // pl_proc_n:  submissions it ran on
	PathLookNs,   // pl_look_ns: LookaheadSubmission (the draw-ahead / compute walk post).
	              //             ON THE GUEST SUBMIT THREAD, not GuestGpu, and therefore NOT
	              //             part of `named` and NOT inside pl_proc_ns.  Reported on its
	              //             own line: what the submitting thread pays for the lookahead.
	PathLookN,    // pl_look_n
	PathPrefNs,   // pl_pref_ns: PrefetchComputePipelines (the PM4 look-ahead walk)
	PathPrefN,    // pl_pref_n
	PathEopNs,    // pl_eop_ns:  TriggerEopEventAtEndOfPipe - the ~420 labels a frame the
	              //             CPU writes at parse time (gpu-driven.md:36, the design
	              //             constraint that killed zero-copy in s66 and D1 in s91)
	PathEopN,     // pl_eop_n
	PathBarNs,    // pl_bar_ns:  EmitGlobalBarrier.  Outside the render mutex at the
	              //             default, where the barrier is skipped before the lock;
	              //             with KYTY_EOP_BARRIER=1 it takes the mutex and this
	              //             then includes that hold
	PathBarN,     // pl_bar_n
	PathSubNs,    // pl_sub_ns:  BufferFlush and BufferFlushLazy (the submission handoff),
	              //             depth-guarded: the lazy one CALLS the plain one, so a
	              //             flush is charged once and counted once
	PathSubN,     // pl_sub_n
	PathGcNs,     // pl_gc_ns:   RunGarbageCollector - ALL FIVE call sites of
	              //             GuestGpu::Process, including the one on flip preparation
	PathGcN,      // pl_gc_n
	PathCmdNs,    // pl_cmd_ns:  ProcessCommands, the guest-command pump inside the PM4 loop
	PathCmdN,     // pl_cmd_n
	// (b) INSIDE the render mutex, the emit half of a draw (mh_emit_us).  The chain starts
	// where HoldPhase(HoldEmitNs) starts and ends where it ends, so sum(pl_em_*) == mh_emit_us
	// on the draws that ran it, up to the price of the marks themselves.
	PathEmVtxNs,  // pl_em_vtx_ns:  AcquireVertexBuffers + PrepareIndexBuffer
	PathEmRtNs,   // pl_em_rt_ns:   AcquireRenderTargets
	PathEmPipeNs, // pl_em_pipe_ns: GetGraphicsPipeline (creates pipelines)
	PathEmComNs,  // pl_em_com_ns:  CommitBindings - the 2.03 ms the rest is measured against
	PathEmRecNs,  // pl_em_rec_ns:  BeginRendering, dynamic state, EmitDrawPrimitives, record
	PathEmRestNs, // pl_em_rest_ns: the remainder of mh_emit (debug dumps, the early exits)
	PathEmN,      // pl_em_n:       draws whose emit chain ran
	// Session 96, knob "bdaevery" (MEASUREMENT ONLY, pred/03_bdaevery.md): the price of the
	// synchronisation term of M3's sealed rule, at the two granularities the sources disagree
	// about.  Raw ns / raw counts.  ALWAYS quote them with the BDA regime (regime94.py).
	BdaEveryCalls, // be_n:  PrepareBda calls this knob caused (0 when the knob is 0)
	BdaEveryNs,    // be_ns: their wall time on the GuestGpu thread
	// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053), route E
	// measurement M3: the CEILING STUB.  The picture is allowed to break; these twelve say
	// what the stub actually did, and every one of them is written inside a branch the gate
	// opened, so at bindfloor=0 all twelve read exactly 0.  Raw counts and raw ns.
	BindFloorDraws,     // bf_n:       draws that took the floor path
	BindFloorDispatch,  // bf_disp:    dispatches that took it
	BindFloorPush,      // bf_push:    commits emitted through push descriptors
	BindFloorPool,      // bf_pool:    commits emitted through a pooled descriptor set
	BindFloorImages,    // bf_img:     stub image-view descriptors written
	BindFloorBuffers,   // bf_buf:     stub buffer-view descriptors written
	BindFloorSamplers,  // bf_smp:     stub sampler descriptors written
	BindFloorNullTrans, // bf_null_tr: transitions of the <= 9 null images (per class, per
	                    //             commit - NOT a per-slot synchronisation)
	BindFloorMat,       // bf_mat:     real MaterializeResources calls under the floor
	BindFloorReuse,     // bf_reuse:   materialisations answered from the last one instead
	BindFloorBurnNs,    // bf_burn_ns: time the calibrated idle (bfmode=2/3) actually burned
	// Session 99: optional KYTY_BIND_FLOOR_CPU=1 readout, same clock as cpu_gpu_us.
	BindFloorBurnCpuNs, // bf_burn_cpu_ns: sum of successful GuestGpu CPU deltas around burn
	BindFloorBurnCpuN,  // bf_burn_cpu_n: successful strictly positive CPU sample pairs
	BindFloorBurnCpuBad,// bf_burn_cpu_bad: zero/backwards readings or zero CPU delta
	BindFloorBurnProbeNs, // bf_burn_probe_ns: wall bounds around both CPU queries, all pairs
	BindFloorSkips,     // bf_skip:    draws / dispatches the floor did NOT take (reason in
	                    //             the log for the first 64)
	// Session 99: successful existing-program resource outcomes, armed bfmode=2 only.
	// No timers or proglap dependency; cold translations and failed attempts are excluded.
	BindFloorLiveAhead, // bf_live_ahead: AheadTake supplied a live snapshot
	BindFloorLiveMat,   // bf_live_mat:   MaterializeResources returned true
	BindFloorLiveMemo,  // bf_live_memo:  verified SRT memo supplied a live snapshot
	// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053): image readbacks
	// the floor had to abandon because the image's guest range does not fit the 32 MiB
	// download ring.  Run bf96a died on exactly this (textureCache.cpp, DownloadImageMemory):
	// the floor halves the frame, the game's DRS answers with 4.00x the area (rt_kpx/rt_att
	// 2 010 -> 8 040 Kpx in 30 frames) and a linear colour target passes 32 MiB.  A nonzero
	// bf_dlskip therefore means TWO things and both must be reported: the readback was
	// skipped (stale guest bytes - a broken picture, which the floor is licensed to produce)
	// AND the arms are drawing different areas, so the frame numbers of that run are void
	// until bfmode=3 / bfburn hold the frame length.  Written only while the gate is on.
	BindFloorDlSkip,   // bf_dlskip:    readbacks abandoned
	BindFloorDlSkipKb, // bf_dlskip_kb: their guest ranges, KiB
	// Session 97, gate "bindfloor": bf_gc_hold - texture GC calls whose non-critical age pass
	// the floor suspended (textureCache.cpp RunGarbageCollector), 0 while the floor is off;
	// bf_edge - changes of the per-op latch (descriptors.cpp BindFloorLatchOp), one per
	// schedule edge, booked in the flip that first saw the new value.
	// Session 99: opt-in texture GC mechanism audit, both arms, per GC call.
	// Hold predicate = normal helper OR current submission's counted sticky armed value;
	// the latter is only an independent subset, not a proof of base/pending state.
	BindFloorImgGcChecks,   // bf_igc_checks: observed clock transitions (also below trigger)
	BindFloorImgGcHold,     // bf_igc_hold: expected paused transitions, excluding critical
	BindFloorImgGcBad,      // bf_igc_bad: wrong clock delta OR sticky subset missed by helper
	BindFloorImgGcCritical, // bf_igc_critical: expected hold but critical override permitted
	BindFloorImgGcEvict,    // bf_igc_evict: GC root evictions under expected hold, critical too
	BindFloorGcHold,   // bf_gc_hold
	BindFloorEdges,    // bf_edge
	// Session 97 (patch C): buffer GC calls whose non-aggressive pass the floor suspended.
	BindFloorBufGcHold, // bf_bgc_hold
	// Session 97 (patch D): true null descriptors the floor wrote (buffers + images).
	BindFloorNullDescs, // bf_ndesc
	// Session 98 (patch_s98a/b, MEASUREMENT ONLY, raw counts; descriptors.h has the latch).
	// bf_xover / bf_xover_acb: KYTY_BIND_FLOOR_LATCH=1, submissions of the NEW frame (seq above
	// the flip-bearing DCB) that had already run ops under the old value when the flip packet
	// opened a pending change - all queues / the async-compute queues (1..56) only.
	BindFloorXover,      // bf_xover
	BindFloorXoverAcb,   // bf_xover_acb
	// bf_mixed: completed submissions whose draw/dispatch latches saw BOTH armed and unarmed
	// (the flip-bearing DCB is judged before and after its flip packet separately).  Every mode.
	BindFloorMixed,      // bf_mixed
	// bf_defer: frame-latch adoptions that had to wait for an older submission still in flight;
	// bf_defer_force: pending changes adopted anyway after two further flip packets.
	BindFloorDefer,      // bf_defer
	BindFloorDeferForce, // bf_defer_force
	// KYTY_BIND_FLOOR_LATCH=2: falling edges adopted at a learned GDS consumer / ops held armed
	// while a falling edge waited for one / falling edges adopted by the two-flip fallback.
	BindFloorTrigFire,   // bf_trig_fire
	BindFloorTrigWait,   // bf_trig_wait
	BindFloorTrigFb,     // bf_trig_fb
	// KYTY_BIND_FLOOR_CLEAR=1: floored, shortcut-eligible dispatches whose compute clear
	// shortcuts were skipped (renderCompute.cpp).
	BindFloorClrSkip,    // bf_clr_skip
	// KYTY_GPU_MARKERS (patch_s98b): ops marked this flip, positive-control hits / misses, and 1
	// a flip when markers were requested but the device lacks VK_AMD_buffer_marker.
	GpuMarkerOps,        // gm_ops
	GpuMarkerOk,         // gm_ok
	GpuMarkerBad,        // gm_bad
	GpuMarkerUnsup,      // gm_unsup
	// Session 98 (patch_s98c): live-visibility control - marker words of ops in a tick whose
	// semaphore had NOT signalled when they were read, in patterns the end-of-submission flush
	// cannot produce (gpuCheckpoints.cpp MarkerLiveControl).
	GpuMarkerLive,       // gm_live
	GpuMarkerLiveTop,    // gm_live_top
	// Session 98 (patch_s98d): KYTY_BIND_FLOOR_CLEAR=1 - an ARMED op the floor cannot express
	// (bf_skip) dropped instead of running the real PrepareBindings over the frozen snapshot.
	BindFloorSkipDrop,   // bf_skip_drop
	// Session 100: the compute clear shortcuts ACTUALLY TAKEN, in BOTH arms and behind no
	// gate - the counter session 98 owed (ROADMAP.md:1406).  bf_clr_skip counts dispatches
	// that are shortcut-ELIGIBLE BY SHAPE and strictly over-counts; these two count the
	// consumed ones, so the base arm finally has a real denominator.
	ClearShortcutMeta,   // clr_taken_meta: TryConsumeComputeMetaClear consumed the dispatch
	ClearShortcutImage,  // clr_taken_img:  TryConsumeComputeImageClear consumed the dispatch
	// Session 100, gate "blmove" (MEASUREMENT ONLY, pred/02_moved_mark.md): the moved-mark
	// census.  Phase 0 closes after the image loop, phase 1 after the shader_data copy;
	// both pay exactly two timestamps and four Adds a stage, so the mark price cancels in
	// span1 - span0.  The phase alternates per stage TYPE, and blm_img*/blm_smp* exist so
	// that the balance of the two phases is a control and not an assumption.
	// Raw ns and raw counts; at blmove=0 all eight read exactly 0.
	BindLapMoveSpan0Ns,   // blm_s0_ns
	BindLapMoveSpan0N,    // blm_s0_n
	BindLapMoveSpan1Ns,   // blm_s1_ns
	BindLapMoveSpan1N,    // blm_s1_n
	BindLapMoveImages0,   // blm_img0
	BindLapMoveImages1,   // blm_img1
	BindLapMoveSamplers0, // blm_smp0
	BindLapMoveSamplers1, // blm_smp1
	// Session 101, gate "cbmove" (MEASUREMENT ONLY, pred/01_two_directional.md): the
	// moved-mark census of CommitBindings.  Stage phase 0 closes after cb_lap(cb_transit)
	// and phase 1 after cb_lap(cb_write), so cm_s1 - cm_s0 is the write build; commit
	// phase 0 closes immediately (a null span pricing the mark pair) and phase 1 before
	// cb_finish(), so cm_e1 - cm_e0 is the emit.  Both phases pay exactly two timestamps
	// and four Adds, so the mark price cancels in each difference.  The population
	// counters exist so that the balance of the two phases is a control, not an
	// assumption.  Raw ns and raw counts; at cbmove=0 all sixteen read exactly 0.
	CommitLapMoveStage0Ns,   // cm_s0_ns
	CommitLapMoveStage0N,    // cm_s0_n
	CommitLapMoveStage1Ns,   // cm_s1_ns
	CommitLapMoveStage1N,    // cm_s1_n
	CommitLapMoveImages0,    // cm_i0: program.info.images.size() of the phase-0 stages
	CommitLapMoveImages1,    // cm_i1
	CommitLapMoveBindings0,  // cm_b0: program.bindings.descriptors.size(), phase-0 stages
	CommitLapMoveBindings1,  // cm_b1
	CommitLapMoveEmit0Ns,    // cm_e0_ns
	CommitLapMoveEmit0N,     // cm_e0_n
	CommitLapMoveEmit1Ns,    // cm_e1_ns
	CommitLapMoveEmit1N,     // cm_e1_n
	CommitLapMoveWrites0,    // cm_w0: write_count of the phase-0 commits
	CommitLapMoveWrites1,    // cm_w1
	CommitLapMoveDesc0,      // cm_c0: descriptor_count of the phase-0 commits
	CommitLapMoveDesc1,      // cm_c1
	// Session 102, knob "dabatch": PipelineCache::QueueDrawAhead calls - the batches the walk
	// flushes (~130 a frame at 64).  Counted whenever FrameStats is on, lite included, under the
	// same condition as da_queue_us and da_q.  Raw count.
	DrawAheadQueueCalls,     // da_qcall
	// Session 103, KYTY_BVH_LOOP_CAP: invocations of a capped BVH program that exhausted their
	// step budget (bl_trip) and that returned normally after spending more than 1/16 of it
	// (bl_near), read back from the fault-buffer tail by ProcessFaultBuffer. Raw counts; they
	// land 1-3 flips after the dispatch.
	LoopCapTrips,            // bl_trip
	LoopCapNear,             // bl_near
	// Session 105, route A M3.1, knob "ctxtick" >= 2 (docs/session-105/designA3_stage3.md
	// section 2 item 5): the command-buffer identity checks made at draw / dispatch entry and at
	// each ownership site (ctx_chk_n) and those that failed (ctx_chk_bad), the Submit calls made
	// while the thread was inside a draw or dispatch (ctx_midsub), and the blocking scheduler
	// APIs entered on a CommandRecorder thread (ctx_rec_block).  Raw counts; all four read
	// exactly 0 at ctxtick 0 and 1.
	CtxCheckN,               // ctx_chk_n
	CtxCheckBad,             // ctx_chk_bad
	CtxMidSubmit,            // ctx_midsub
	CtxRecordBlock,          // ctx_rec_block
	// Session 106, KYTY_GPU_WALL=1 (measurement only, read once per process): the wall of the
	// GuestGpu thread by region - waiting for work in ThreadRun (gw_idle), all queues blocked
	// (gw_blk), one GuestGpu::Process call (gw_proc), one queued command (gw_cmd), and inside
	// Process the R_WAIT_FLIP_DONE wait in FlipQueue::Wait (gw_flip).  Raw ns / counts, live in
	// KYTY_FRAME_TRACE=lite; all read 0 without the variable.  dt - cpu_net splits into
	// idle + blk (outside Process) + flip + lock waits + the rest (other waits, preemption).
	GpuWallIdleNs,           // gw_idle_ns
	GpuWallIdleN,            // gw_idle_n
	GpuWallBlockedNs,        // gw_blk_ns
	GpuWallBlockedN,         // gw_blk_n
	GpuWallFlipNs,           // gw_flip_ns
	GpuWallFlipN,            // gw_flip_n
	GpuWallProcNs,           // gw_proc_ns
	GpuWallProcN,            // gw_proc_n
	GpuWallCmdNs,            // gw_cmd_ns
	GpuWallCmdN,             // gw_cmd_n
	// Session 107, gate "plkstat" (measurement only): GuestGpu's CONTENDED acquisitions of
	// PipelineCache::m_mutex at its three plkstat sites (a TryLock failed first): the count, the
	// wall and the thread CPU (ThreadCpuNs(Gpu)) around the blocking Lock - cpu / wall is the spin
	// share - and the same split by the holder tag read at the failed try (0 untagged, 1 walker
	// QueueDrawAhead, 2 walker PrefetchComputePipeline, 3 compute-pipeline compile completion).
	// Plus the walker's own holds, timed after its LockGuard.  Raw ns / counts.
	PipeLockContN,           // pl_cont_n
	PipeLockContWallNs,      // pl_cont_wall_ns
	PipeLockContCpuNs,       // pl_cont_cpu_ns
	PipeLockContH0N,         // pl_cont_h0_n
	PipeLockContH0Ns,        // pl_cont_h0_ns
	PipeLockContH1N,         // pl_cont_h1_n
	PipeLockContH1Ns,        // pl_cont_h1_ns
	PipeLockContH2N,         // pl_cont_h2_n
	PipeLockContH2Ns,        // pl_cont_h2_ns
	PipeLockContH3N,         // pl_cont_h3_n
	PipeLockContH3Ns,        // pl_cont_h3_ns
	PipeLockWalkQueueHoldNs, // pl_wq_hold_ns
	PipeLockWalkQueueHoldN,  // pl_wq_hold_n
	PipeLockWalkPrefHoldNs,  // pl_wp_hold_ns
	PipeLockWalkPrefHoldN,   // pl_wp_hold_n
	// Session 107, knob "cspmemo": the compute-prefetch memo.  Raw counts.
	CspMemoLook,             // cspm_look: prefetch calls that built a key (knob != 0)
	CspMemoWould,            // cspm_would: ... that found it (a skip at knob 2/3)
	CspMemoSkip,             // cspm_skip: calls returned early (knob 2)
	CspMemoBad,              // cspm_bad: knob 3 - the locked path disagreed with the memo
	CspMemoStore,            // cspm_store: entries written
	CspMemoClear,            // cspm_clear: memo cleared (stamp moved or full)
	CspPrefHave,             // cspf_have: locked prefetches whose program already had a pipeline
	CspPrefNew,              // cspf_new: ... that queued a new pipeline
	// Session 108, knob "cspfam": prefetch calls that looked the family up / returned before the lock.
	CspFamLook,              // cspfam_look
	CspFamSkip,              // cspfam_skip
	// Session 108, the guard of every run (no gate): GetComputePipeline found no pipeline and compiled it
	// synchronously on the dispatch (cs_sync_new), or found one the prefetch queued still compiling and
	// waited for it (cs_sync_wait).  Raw counts.
	CsSyncNew,               // cs_sync_new
	CsSyncWait,              // cs_sync_wait
	// Session 109, knob "cspfam" v2: family-table clears on the prefetching thread (a stamp moved:
	// programs epoch, shader registrations, a compute-pipeline creation anywhere, or capacity).
	CspFamClear,             // cspfam_clr
	// Session 109, knob "cspfree": prefetch calls that built the key (knob != 0), that found the source,
	// that found the specialization (a skip at knob 1), source unknown, specialization unknown, unlocked
	// materialization failed, memo cleared (stamp moved or full), entries stored, knob 2 disagreements at
	// equal specializations (bad) and at different ones (memory moved between the two reads).  Raw counts.
	CspFreeLook,             // cspfree_look
	CspFreeHit,              // cspfree_hit
	CspFreeSrcMiss,          // cspfree_src_miss
	CspFreeSpecMiss,         // cspfree_spec_miss
	CspFreeMatFail,          // cspfree_mat_fail
	CspFreeClear,            // cspfree_clr
	CspFreeStore,            // cspfree_store
	CspFreeBad,              // cspfree_bad
	CspFreeMoved,            // cspfree_moved
	Count
};

// Session 67 watchdog: per-frame values that are not sums. A gauge holds the largest value a
// frame saw and the flip takes it and resets it, so it is independent of the lean limit of
// Counter and of the shard sum. Printed at the end of the FrameTrace main line.
enum class Gauge : uint32_t {
	RtWidth,  // widest colour render target a draw of this frame bound (rt_w)
	RtHeight, // ... its height (rt_h)
	VpWidth,  // widest guest viewport of this frame, |xscale| * 2 (vp_w)
	VpHeight, // ... |yscale| * 2 (vp_h)
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
// Session 68, gate "amut": the nesting depth and the start of the outermost mutating interval.
inline thread_local uint32_t t_mut_depth = 0;
inline thread_local uint64_t t_mut_t0    = 0;
// Session 69, gate "mutsite": the cursor of the render-mutex phase chain (HoldLap). Thread-local
// so that ExecutePreparedDraw can add a boundary without the lap in its signature, and so that the
// present thread keeps its own chain. Zero means "not measuring".
inline thread_local uint64_t t_hold_t0   = 0;
// Session 96, gate "pathlap": nesting depth of the named outside-mutex spans that CAN nest.
// BufferFlushLazy calls BufferFlush, and both are named regions charged to pl_sub; without a
// guard the inner one charges the same interval a second time.  One counter per nestable
// group, so the guard never reaches a span that legitimately sits inside another (pl_proc
// contains every other span by construction and must not suppress them).
inline thread_local uint32_t t_path_sub_depth = 0;
// Session 96, gate "pathlap": the cursor of a PathLap chain.  Separate from t_hold_t0 so the
// emit chain can run inside the mh_* chain, and so the GuestGpu thread's outside-mutex chain
// and a draw's emit chain never share one.  Zero means "not measuring".
inline thread_local uint64_t t_path_t0   = 0;
inline constinit bool                  g_timings = false;
// No initializer to run, so no TLS guard: the shard is attached by the first Add of a thread.
inline constinit thread_local Shard*   t_shard   = nullptr;
// Gauges are global rather than sharded: a maximum does not sum across threads. Read-mostly, so
// the relaxed load of NoteMax stays in the local cache while the frame's maximum does not grow.
inline constinit std::array<std::atomic<uint32_t>, static_cast<size_t>(Gauge::Count)> g_gauges {};

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

// Raises a gauge to `value` if the frame has not seen a larger one. One relaxed load per call and
// a store only while the maximum grows, which after the first draws of a frame is never.
inline void NoteMax(Gauge gauge, uint32_t value) {
	auto& slot = Detail::g_gauges[static_cast<size_t>(gauge)];
	if (slot.load(std::memory_order_relaxed) < value) {
		slot.store(value, std::memory_order_relaxed);
	}
}

// Reads a gauge and resets it for the next frame. Called once per flip.
[[nodiscard]] uint32_t TakeMax(Gauge gauge);

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

// Session 68: the render mutex of renderContext.h:80. Constructed right after the LockGuard with
// the timestamp taken right before it, so it charges the wait to one counter and the hold to
// another. Zero means "not measuring" (gate "amut" off, or FrameStats off).
class MutexMark {
public:
	explicit MutexMark(uint64_t before): m_t(before) {
		if (m_t != 0) {
			const auto now = NowNs();
			Add(Counter::LockWaitNs, now - m_t);
			Add(Counter::LockHolds, 1);
			m_t = now;
		}
	}
	~MutexMark() {
		if (m_t != 0) {
			Add(Counter::LockHoldNs, NowNs() - m_t);
		}
	}
	MutexMark(const MutexMark&)            = delete;
	MutexMark& operator=(const MutexMark&) = delete;

private:
	uint64_t m_t;
};

// Session 83, gate "plkstat": splits one lock acquisition into the wait and the hold.
// Constructed with a timestamp taken right BEFORE the LockGuard, exactly like MutexMark of
// session 68; zero means "not measuring". Same shape, different counters, because the render
// mutex and the pipeline-cache mutex are different objects and must never share a number.
class LockSplit {
public:
	LockSplit(uint64_t before, Counter wait, Counter hold, Counter count)
	    : m_t(before), m_hold(hold) {
		if (m_t != 0) {
			const auto now = NowNs();
			Add(wait, now - m_t);
			Add(count, 1);
			m_t = now;
		}
	}
	~LockSplit() {
		if (m_t != 0) {
			Add(m_hold, NowNs() - m_t);
		}
	}
	LockSplit(const LockSplit&)            = delete;
	LockSplit& operator=(const LockSplit&) = delete;

private:
	uint64_t m_t;
	Counter  m_hold;
};

// Session 85, gate "bindlap": the plkstat idiom as a scope - a timestamp under Enabled()
// and NOT under TimingsEnabled(), differenced by hand in the destructor, so that it reads
// in a KYTY_FRAME_TRACE=lite measurement run where every Scope and every Lap reads exactly
// 0 (the trap session 68 hit and session 84 nearly repeated).  Constructed with the gate's
// value: while the gate is off nothing is read and nothing is written.  Unlike Scope it
// carries no count - the population counters are explicit Adds at the call site, because
// they are the arming identities and must be visible where they are claimed.
class LapScope {
public:
	LapScope(bool on, Counter ns): m_ns(ns), m_t0(on && Enabled() ? NowNs() : 0) {}
	~LapScope() {
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
		}
	}
	LapScope(const LapScope&)            = delete;
	LapScope& operator=(const LapScope&) = delete;

private:
	Counter  m_ns;
	uint64_t m_t0;
};

// Session 68, gate "amut": the union of the mutating intervals of the draw path (the serial floor
// A). Constructed with the gate's value; when it is off nothing is read and nothing is written.
// Nested scopes do not time themselves - the outermost one already covers them - so the total is
// the union of the intervals, which is what A is. Enabled() and not TimingsEnabled(): a
// measurement run is KYTY_FRAME_TRACE=lite, where g_timings is false.
class MutScope {
public:
	// Session 83: `arm` is the counter that proves this scope armed, for sites added behind a
	// knob. Counter::Count = none, which is what the six sites of session 68 pass by omission,
	// so they are unchanged. The count lands INSIDE the interval on purpose - it is part of the
	// instrument's price and the ABBA on the knob measures it with everything else.
	explicit MutScope(bool on, Counter arm = Counter::Count): m_active(on && Enabled()) {
		if (!m_active) {
			return;
		}
		if (arm != Counter::Count) {
			Add(arm, 1);
		}
		m_outer = Detail::t_mut_depth++ == 0;
		if (m_outer) {
			Detail::t_mut_t0 = NowNs();
		}
	}
	~MutScope() {
		if (!m_active) {
			return;
		}
		Detail::t_mut_depth--;
		if (m_outer) {
			Add(Counter::MutateNs, NowNs() - Detail::t_mut_t0);
			Add(Counter::MutateIntervals, 1);
		}
	}
	MutScope(const MutScope&)            = delete;
	MutScope& operator=(const MutScope&) = delete;

private:
	bool m_active;
	bool m_outer = false;
};

// Session 69, gate "mutsite": a lap over the phases of the render-mutex hold. Same shape as Lap
// below, with three differences that it needs and Lap must not have:
//   * it reads Enabled(), not TimingsEnabled() - a measurement run is KYTY_FRAME_TRACE=lite,
//     where g_timings is false and every Lap::Mark is a no-op (the trap session 68 hit);
//   * the destructor charges whatever is left to a counter chosen at construction, so a draw that
//     returns early out of the middle of the critical section still books its whole hold;
//   * Mark is static and the cursor is thread-local, so ExecutePreparedDraw can add a boundary
//     without the lap being plumbed through its signature. The chain never nests: DrawIndex,
//     DrawAuto and DispatchDirect each construct one and ExecutePreparedDraw is called only from
//     the first two, while the present sites run on another thread and have their own cursor.
class HoldLap {
public:
	HoldLap(bool on, Counter rest): m_rest(rest) {
		Detail::t_hold_t0 = on && Enabled() ? NowNs() : 0;
	}
	~HoldLap() {
		if (Detail::t_hold_t0 != 0) {
			Add(m_rest, NowNs() - Detail::t_hold_t0);
			Detail::t_hold_t0 = 0;
		}
	}
	static void Mark(Counter counter) {
		if (Detail::t_hold_t0 != 0) {
			const auto now = NowNs();
			Add(counter, now - Detail::t_hold_t0);
			Detail::t_hold_t0 = now;
		}
	}
	// Adds one to a population counter only while the chain is running, so the population and the
	// phases always come from the same set of draws and nothing is counted when the gate is off.
	static void Count(Counter counter) {
		if (Detail::t_hold_t0 != 0) {
			Add(counter, 1);
		}
	}
	HoldLap(const HoldLap&)            = delete;
	HoldLap& operator=(const HoldLap&) = delete;

private:
	Counter m_rest;
};

// Closes one phase of a HoldLap chain at scope exit rather than at a statement, so a function with
// several `return`s charges its whole span to that phase without a mark at each of them.
// ExecutePreparedDraw has three exits and the default one (gate "recpack") is in the middle.
class HoldPhase {
public:
	explicit HoldPhase(Counter counter): m_counter(counter) {}
	~HoldPhase() { HoldLap::Mark(m_counter); }
	HoldPhase(const HoldPhase&)            = delete;
	HoldPhase& operator=(const HoldPhase&) = delete;

private:
	Counter m_counter;
};

// Session 96, gate "pathlap": one named region of the GuestGpu thread OUTSIDE the render
// mutex, timed and counted together so the population and the time always come from the same
// entries.  Enabled() and not TimingsEnabled(), like LapScope, so it reads in a lite run.
// It refuses to arm while a HoldLap chain is running (Detail::t_hold_t0 != 0), so a region
// that can also be reached from inside the render mutex is never charged twice - once to the
// hold and once to the residue.  That check is the reason gate "pathlap" REQUIRES gate
// "mutsite" in the same arm: t_hold_t0 is the only "inside the mutex" signal there is, and
// gates_base.txt pins mutsite=0.
class PathSpan {
public:
	PathSpan(bool on, Counter ns, Counter n)
	    : m_ns(ns), m_t0(on && Enabled() && Detail::t_hold_t0 == 0 ? NowNs() : 0) {
		if (m_t0 != 0) {
			Add(n, 1);
		}
	}
	// Depth-guarded form, for a region that can be entered from inside ITSELF through another
	// function: BufferFlushLazy calls BufferFlush and both are pl_sub.  Only the outermost
	// span of the nest arms, so the interval is charged once and the population counts one
	// flush, not two.  The depth is always stepped, even when the gate is off, so a nest that
	// starts while the gate is off cannot arm halfway through.
	PathSpan(bool on, Counter ns, Counter n, uint32_t& depth)
	    : m_ns(ns),
	      m_t0(on && Enabled() && Detail::t_hold_t0 == 0 && depth == 0 ? NowNs() : 0),
	      m_depth(&depth) {
		++depth;
		if (m_t0 != 0) {
			Add(n, 1);
		}
	}
	~PathSpan() {
		if (m_depth != nullptr) {
			--*m_depth;
		}
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
		}
	}
	PathSpan(const PathSpan&)            = delete;
	PathSpan& operator=(const PathSpan&) = delete;

private:
	Counter   m_ns;
	uint64_t  m_t0;
	uint32_t* m_depth = nullptr;
};

// Session 106, KYTY_GPU_WALL=1 (measurement only): read once per process; logs "GpuWall: mode 1"
// the first time it is asked and finds the variable on.
[[nodiscard]] bool GpuWallOn();

// Session 106: the wall of one GuestGpu-thread region (counters GpuWall*), timestamped under
// Enabled() so it reads in KYTY_FRAME_TRACE=lite.  `on` is the caller's extra condition (the
// thread role for the flip wait).  Off, it costs the static read in GpuWallOn().
class WallSpan {
public:
	WallSpan(bool on, Counter ns, Counter n): m_ns(ns), m_t0(on && GpuWallOn() && Enabled() ? NowNs() : 0) {
		if (m_t0 != 0) {
			Add(n, 1);
		}
	}
	~WallSpan() {
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
		}
	}
	WallSpan(const WallSpan&)            = delete;
	WallSpan& operator=(const WallSpan&) = delete;

private:
	Counter  m_ns;
	uint64_t m_t0;
};

// Session 96, gate "pathlap": HoldLap's shape with its OWN thread-local cursor, so a chain
// can run INSIDE the mh_* chain (the emit half of a draw) without disturbing it, and a second
// one can run on the GuestGpu thread outside the render mutex.  Enabled() and NOT
// TimingsEnabled(), which is the whole point: Lap (below) and every Scope read exactly 0 in a
// KYTY_FRAME_TRACE=lite measurement run, and that is why mh_emit was never split.
// Constructed with the gate's value; while the gate is off nothing is read and nothing is
// written.  The destructor charges what is left to `rest`, so a function with several exits
// still books its whole span.
class PathLap {
public:
	PathLap(bool on, Counter rest): m_rest(rest) {
		Detail::t_path_t0 = on && Enabled() ? NowNs() : 0;
	}
	~PathLap() {
		if (Detail::t_path_t0 != 0) {
			Add(m_rest, NowNs() - Detail::t_path_t0);
			Detail::t_path_t0 = 0;
		}
	}
	static void Mark(Counter counter) {
		if (Detail::t_path_t0 != 0) {
			const auto now = NowNs();
			Add(counter, now - Detail::t_path_t0);
			Detail::t_path_t0 = now;
		}
	}
	// Population counter, added only while the chain is running, so the population and the
	// phases always come from the same set of draws.
	static void Count(Counter counter) {
		if (Detail::t_path_t0 != 0) {
			Add(counter, 1);
		}
	}
	PathLap(const PathLap&)            = delete;
	PathLap& operator=(const PathLap&) = delete;

private:
	Counter m_rest;
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
