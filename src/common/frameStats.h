#ifndef KYTY_COMMON_FRAMESTATS_H_
#define KYTY_COMMON_FRAMESTATS_H_

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
	BindBuffersNs, // FindBuffers + RebindBuffers
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
	Count
};

// Call-site attribution: a SiteScope names the operation in flight on this thread and the wait /
// submit paths charge their time to that name.
enum class Table : uint32_t { WaitSites, SubmitSites, Pm4Sites, PopSites, Count };

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

class SiteScope {
public:
	explicit SiteScope(const char* site);
	~SiteScope();
	SiteScope(const SiteScope&)            = delete;
	SiteScope& operator=(const SiteScope&) = delete;

private:
	const char* m_previous;
};

enum class ThreadRole : uint32_t { Main, Gpu, Present, Count };

// KYTY_SAMPLE_GPU=1: sampling profiler of the thread registered as ThreadRole::Gpu. Started by
// RegisterCurrentThread; the samples are logged periodically as SampleTrace: lines.
void                      StartSampler(ThreadRole role);
// Frame boundary for the per-frame sampler dumps (KYTY_SAMPLE_FRAME_MS): called from the flip.
void                      NoteFrame(uint64_t frame);

[[nodiscard]] bool Enabled();
[[nodiscard]] uint64_t NowNs();
void                   Add(Counter counter, uint64_t value);
[[nodiscard]] uint64_t Read(Counter counter);

void                   RegisterCurrentThread(ThreadRole role);
[[nodiscard]] ThreadRole CurrentRole(); // ThreadRole::Count if the thread is not registered
[[nodiscard]] uint64_t ThreadCpuNs(ThreadRole role); // 0 if unknown
[[nodiscard]] uint64_t ProcessCpuNs();

// Adds the elapsed time to `ns` and increments `count` (Counter::Count = none) when destroyed.
class Scope {
public:
	explicit Scope(Counter ns, Counter count = Counter::Count)
	    : m_ns(ns), m_count(count), m_t0(Enabled() ? NowNs() : 0) {}
	~Scope() {
		if (m_t0 != 0) {
			Add(m_ns, NowNs() - m_t0);
			if (m_count != Counter::Count) {
				Add(m_count, 1);
			}
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
	Lap(): m_t(Enabled() ? NowNs() : 0) {}
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
