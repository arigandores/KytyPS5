#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_

#include "common/abi.h"
#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))
#include "common/alignment.h"
#include "common/common.h"
#include "common/lruCache.h"
#include "common/parallelCopy.h"
#include "common/slotVector.h"
#include "graphics/host_gpu/memoryTracker.h"
#include "graphics/host_gpu/rangeSet.h"
#include "graphics/host_gpu/renderer/cache/faultManager.h"
#include "graphics/host_gpu/renderer/cache/hostImport.h"
#include "kernel/memory.h"
#include "graphics/host_gpu/renderer/cache/multiLevelPageTable.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"

#include <atomic>
#include <chrono>
#include <map>
#include <mutex>
#include <span>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <utility>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class CommandScheduler;
class TextureCache;

using BufferId = Common::SlotId;
inline constexpr BufferId NULL_BUFFER_ID {0};

// Session 136, knob "bindlean" (design136.md rev 1 s.4.3 with ROADMAP s122 items 179(d), (g)): what ObtainBuffer hands to the
// SynchronizeBuffer of its slow path at find = false and !is_written - an object on its stack, passed by pointer and never
// stored. epoch/kind: the snapshot S of ObtainBuffer (UploadEpoch before the combined query); clean: the bit "CPU-clean" (a
// completed fast scan of the combined query with a false answer); rwe/gwe (2/3 only): the range and the global write
// witnesses read right after S (RC3); mode: the value of the call.
struct SyncCarry {
	uint64_t epoch;
	uint64_t rwe;
	uint64_t gwe;
	uint8_t  kind;
	bool     clean;
	uint8_t  mode;
};

class BufferCache {
public:
	static constexpr uint32_t CACHING_PAGEBITS  = 14;
	static constexpr uint64_t CACHING_PAGESIZE  = uint64_t {1} << CACHING_PAGEBITS;
	static constexpr uint64_t CACHING_NUMPAGES  = uint64_t {1} << (40 - CACHING_PAGEBITS);
	static constexpr uint64_t BDA_PAGETABLE_SIZE =
	    CACHING_NUMPAGES * sizeof(vk::DeviceAddress);

	BufferCache(GraphicContext& graphics, CommandScheduler& scheduler, PageManager& page_manager,
	            TextureCache& texture_cache);
	~BufferCache();
	KYTY_CLASS_NO_COPY(BufferCache);

	void                   InvalidateMemory(uint64_t vaddr, uint64_t size);
	// Knob "faultkb": a CPU write fault that opens the window around the faulting page at once
	// (MemoryTracker::InvalidateWriteFault). The window lies inside one tracking region.
	void InvalidateWriteFault(uint64_t fault_vaddr, uint64_t window_begin, uint64_t window_size);
	// fw_win_armed at one page (diagnostic): MemoryTracker::WriteFaultArmedPages.
	[[nodiscard]] uint64_t WriteFaultArmedPages(uint64_t fault_vaddr, uint64_t window_begin,
	                                            uint64_t window_size);
	void                   ReadMemory(uint64_t vaddr, uint64_t size, bool is_write = false);
	// A CPU write is about to land in [vaddr, vaddr + size): wait for the GPU copies that still
	// read the range straight from guest memory (HostImport). Any thread; true if it waited.
	bool WaitPendingHostReads(uint64_t vaddr, uint64_t size);
	// Whether WaitPendingHostReads(vaddr, size) would wait (no waiting here).
	[[nodiscard]] bool HasPendingHostReads(uint64_t vaddr, uint64_t size);
	// RenderContext::HandleFault, after both caches handled a CPU write fault: the repeated-fault
	// watchdog (pb_stuck) and the sampled protection check (gate "pbcheck"). Any thread.
	// The window is the range the fault opened in the buffer tracker (the faulting page at 4 KiB).
	void NoteWriteFault(uint64_t fault_vaddr, uint64_t window_begin, uint64_t window_size);
	[[nodiscard]] Buffer&  GetBuffer(BufferId id) { return m_slot_buffers[id]; }
	[[nodiscard]] BufferId FindBuffer(uint64_t vaddr, uint64_t size);
	// Keep an already discovered owner alive when the binding uses a direct CPU copy.
	// A replaced/coalesced owner requires the ordinary ObtainBuffer path instead.
	[[nodiscard]] bool TouchReadOnlyBuffer(BufferId id, uint64_t vaddr, uint64_t size);
	// Session 64 (shadowResolve.h): what ObtainBuffer would answer for a descriptor binding,
	// read without changing anything and without a lock (the cache has none: a measurement).
	// None: no range. Fast: the per-thread request memo (gate "buffast" logic) still answers.
	// Epoch: the buffer's upload interval is current. Stream: a small CPU-dirty read (a copy into
	// the stream ring). Slow: SynchronizeBuffer would run. New: no buffer owns the range.
	enum class ShadowBufferAnswer : uint8_t { None, Fast, Epoch, Stream, Slow, New };
	[[nodiscard]] ShadowBufferAnswer ShadowProbe(uint64_t vaddr, uint64_t size, BufferId id,
	                                             bool written);
	// memoizable (gate "buffast"): this caller asks for the same guest range again draw after
	// draw and may take a remembered answer. Only the descriptor bindings do; every other caller
	// asks once, for a range it is about to write or to hand to an image upload.
	[[nodiscard]] std::pair<Buffer*, uint64_t> ObtainBuffer(uint64_t vaddr, uint64_t size,
	                                                        bool     is_written,
	                                                        bool     is_texel_buffer = false,
	                                                        BufferId id              = {},
	                                                        bool     memoizable      = false);
	// Session 135, knob "rbslow" (MEASUREMENT ONLY; design135.md rev 2 s.5.2): the census of the "buffast" hits without an
	// action on its own table - PRE before S0 of a latched slot iteration of RebindBuffers, POST after its SlotEnd (on
	// EVERY such iteration: it clears Common::RbSlow::t_rs). Neither changes a value, a decision or a side effect of a path.
	// The only write of a census slot at a would-hit is its touch_tick in POST when ocls != None (CF1, ROADMAP p.171(a)).
	void RsPre(uint64_t vaddr, uint64_t size, bool is_written, bool is_texel_buffer);
	void RsPost(uint64_t vaddr, uint64_t size, BufferId src_id);
	[[nodiscard]] StreamBuffer&                GetUtilityBuffer(MemoryUsage usage) noexcept {
		switch (usage) {
			case MemoryUsage::Upload: return m_staging_buffer;
			case MemoryUsage::Stream: return m_stream_buffer;
			case MemoryUsage::Download: return m_download_buffer;
			case MemoryUsage::DeviceLocal: return m_device_buffer;
		}
		EXIT("BufferCache: invalid utility-buffer usage\n");
	}
	[[nodiscard]] const Buffer* GetGdsBuffer() const noexcept { return &m_gds_buffer; }
	// Gate "gdsepoch": the GDS barrier of a consumer only has to order producers that actually
	// ran since the previous one. The host epoch moves on a host or transfer write to GDS (those
	// are rare: the initial clear, a DMA fill, a DMA copy); the shader epoch moves whenever a
	// draw or dispatch stage with a Gds descriptor is committed.
	[[nodiscard]] uint64_t GdsHostEpoch() const noexcept { return m_gds_host_epoch; }
	[[nodiscard]] uint64_t GdsShaderEpoch() const noexcept { return m_gds_shader_epoch; }
	void                   NoteGdsShaderAccess() noexcept { m_gds_shader_epoch++; }
	[[nodiscard]] Buffer* GetBdaPageTableBuffer() noexcept { return &m_bda_pagetable_buffer; }
	[[nodiscard]] Buffer* GetFaultBuffer() noexcept { return m_fault_manager.GetFaultBuffer(); }
	[[nodiscard]] uint64_t CpuWriteEpoch() const noexcept { return m_memory_tracker.CpuWriteEpoch(); }
	[[nodiscard]] uint64_t RegistrationEpoch() const noexcept { return m_registration_epoch; }
	// Source of an image upload: a native buffer that owns the range, a staging copy, or the
	// imported guest memory itself (HostImport). `size` is what is readable from `offset`.
	struct ImageSource {
		vk::Buffer buffer;
		uint64_t   offset       = 0;
		uint64_t   size         = 0;
		bool       host_written = false; // staging ring / imported guest memory (no GPU writer)
		bool       imported     = false; // one piece of imported guest memory: outlives this tick
	};
	// pending_levels: the source of an image whose top mip levels were deferred (TextureCache);
	// skips the CPU-animated re-upload heuristic of the import path.
	[[nodiscard]] ImageSource ObtainBufferForImage(uint64_t vaddr, uint64_t size,
	                                               bool pending_levels = false);
	static void TraceImageUpload(uint64_t vaddr, uint64_t size, const char* path);
	void FillBuffer(uint64_t vaddr, uint64_t size, uint32_t value, bool is_gds);
	void CopyBuffer(uint64_t dst_vaddr, uint64_t src_vaddr, uint64_t size, bool dst_gds,
	                bool src_gds);
	// Cache-index and exact dirty-range queries require GPU-thread serialization.
	[[nodiscard]] bool IsRegionRegistered(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool HasGpuDirtyBytes(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionCpuModified(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionGpuModified(uint64_t vaddr, uint64_t size);
	// The same two questions asked from the GuestGpu thread, where the tracker's bit maps
	// may be read without taking TrackingSpinLock (gate "trackfree", self-check "tfcheck";
	// see MemoryTracker::IsRegionGpuModifiedFast for why every stale answer is safe there).
	// Callers outside the GuestGpu thread must keep using the plain forms above.
	[[nodiscard]] bool IsRegionGpuModifiedFromGpu(uint64_t vaddr, uint64_t size);
	[[nodiscard]] bool IsRegionCpuModifiedAndGpuCleanFromGpu(uint64_t vaddr, uint64_t size);
	// Session 136, knob "bindlean" (s.4.2): the same query; `*scanned` - its fast branch completed the scan.
	[[nodiscard]] bool IsRegionCpuModifiedAndGpuCleanFromGpu(uint64_t vaddr, uint64_t size, bool* scanned);
	// Session 62, item 3 ceiling (gate "cbstat", GuestGpu thread only): `data` was just copied
	// from guest range [vaddr, vaddr + size) into the stream ring at `ring_offset`; compare it
	// with the shadow of the previous copy of the same range (cb_same / cb_diff / cb_new and the
	// epoch / ring witnesses).
	void               NoteStreamCopy(uint64_t vaddr, uint64_t size, uint64_t ring_offset);
	void               ProcessFaultBuffer();
	void               SynchronizeBuffersInRange(uint64_t vaddr, uint64_t size);
	// Forgets the per-region witnesses of the BDA scan: called when a buffer is registered or
	// dropped and when the guest map changes, because those make unscanned bytes relevant again.
	void               InvalidateBdaRegionStamps() noexcept { m_bda_stamp_generation++; }
	// Session 113, knob "bdanarrow": PrepareBda records a guest-map invalidation (the generation after it) - regions
	// scanned since then are what knob 1 keeps - and whether this pass checks what knob 1 would skip (knob 2).
	void               NoteBdaMapInvalidation() noexcept { m_bda_map_generation = m_bda_stamp_generation; }
	void               SetBdaNarrowCheck(bool check) noexcept { m_bda_narrow_check = check; }
	// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d), (g)(3)): called by PrepareBda at 1 only, around its
	// m_mapped_ranges.ForEach - the pass is open between the two calls and nowhere else, so a walk outside it is the
	// path of 0. EndBdaPass also prints "FixB12Stat:" (item 639(g)(5)).
	void               BeginBdaPass() noexcept;
	void               EndBdaPass();
	// Gate "bdabits": the generation the write map was last consulted under. While it lags
	// m_bda_stamp_generation the map is bypassed, because a generation bump invalidates stamps
	// without any region having announced a write.
	uint64_t           m_bda_bits_generation = 0;
	void               RunGarbageCollector();
	// Records asynchronous downloads of the GPU-dirty parts of regions the CPU keeps reading
	// after the GPU wrote them, so that the next CPU read finds the page clean instead of
	// draining the GPU queue on the GPU thread. Called at the end of every submission slice.
	void PrefetchHotReadbacks();
	// Texture streaming prefetch: file reads queue their destination range (any thread); the GPU
	// thread synchronizes queued ranges into native buffers under a per-frame budget so that the
	// image upload at a scene cut finds a synchronized owner instead of copying guest memory.
	void NoteStreamedRead(uint64_t vaddr, uint64_t size);
	void PrefetchStreamedRanges();
	// Drops every cached buffer intersecting the range (GPU-written bytes are downloaded first) and
	// untracks its pages: used when guest memory becomes a thread stack.
	void DeleteBuffersOverlapping(uint64_t vaddr, uint64_t size);
	// A readback split into the GPU-thread part (record the copies, submit) and the waiting part
	// (done by the guest thread that needs the data), see ReadMemory.
	struct ReadbackPiece {
		uint64_t address = 0;
		uint64_t size    = 0;
		uint64_t offset  = 0; // in the download ring, relative to base_offset
	};
	struct AsyncReadback {
		std::vector<ReadbackPiece> pieces;
		uint8_t*                   mapped      = nullptr;
		uint64_t                   base_offset = 0;
		uint64_t                   tick        = 0;
		uint64_t                   seq         = 0;
	};

	// Session 123, knob "skipceil" = 2 (census, MEASUREMENT ONLY; design123.md s.3.1, ROADMAP s122 item 28(d)): ONE map
	// of guest ranges -> {end, kind, frame} written by census operations of kind D, T or K; non-overlapping segments,
	// cut on every write.  GuestGpu thread only (no lock); cleared when a new census epoch begins.
	struct SkcQuery {
		bool     d          = false; // a D segment intersects (any age)
		bool     t          = false; // a T segment intersects
		bool     d_k0       = false; // ... D written in this frame (k = 0)
		bool     d_k1       = false; // ... D written in the previous frame (k = 1)
		bool     d_k2       = false; // ... D written two or more frames ago (k >= 2)
		uint64_t d_bytes    = 0;     // bytes of the window under D
		uint8_t  last_kind  = 0;     // the latest intersecting D / T segment: kind and frame
		uint32_t last_frame = 0;
	};
	[[nodiscard]] SkcQuery SkcQueryRange(uint64_t vaddr, uint64_t size);
	// A D / T / K write of this frame (W2 of a D / T / K operation).
	void SkcStampRange(uint64_t vaddr, uint64_t size, uint8_t kind);
	// A certain write that is not undone work (M: DMA / FillBuffer / CopyBuffer destination), on GuestGpu.
	void SkcEraseRange(uint64_t vaddr, uint64_t size);
	// A CPU invalidation, any thread: erases the window by a command on GuestGpu ([RC16]: late by one operation).
	void SkcEraseCpu(uint64_t vaddr, uint64_t size);
	// A D segment written k frames ago is live ([N8]).
	[[nodiscard]] bool SkcDLive(uint32_t k);
	// Reads that need the undone work (s.3.2): 0 skc_r_c (a CP fault on GuestGpu), 1 skc_r_g (a guest read served),
	// 2 skc_r_p (a prefetch window), 3 skc_r_m (a DMA source).
	void SkcNoteRead(uint32_t cls, uint64_t vaddr, uint64_t size);
	// A CP read (s.3.2 [RC4]): site 0 wrm, 1 cond, 2 pred, 3 icnt, 4 iarg, 5 dind.
	void SkcCpRead(uint32_t site, uint64_t vaddr, uint64_t size);
	// SkcCpuRead / SkcCpRead lines (at most 8 of each per process), from SkcCensus::FrameDump.
	void SkcDump();

private:
	friend struct BufferCacheTestAccess;

	// Session 123, knob "skipceil" = 2 (census): the map above.
	struct SkcSegment {
		uint64_t end   = 0;
		uint32_t frame = 0;
		uint8_t  kind  = 0;
	};
	struct SkcWindow {
		uint64_t kb = 0;
		uint64_t n  = 0;
	};
	void                                                          SkcSync();
	void                                                          SkcCut(uint64_t begin, uint64_t end);
	void                                                          SkcDLiveMove(uint32_t frame, bool add);
	std::map<uint64_t, SkcSegment>                                m_skc_map;
	std::unordered_map<uint32_t, uint32_t>                        m_skc_dlive; // frame -> live D segments
	uint32_t                                                      m_skc_epoch = UINT32_MAX;
	std::map<std::tuple<uint32_t, uint64_t, uint32_t>, SkcWindow> m_skc_cpu_reads; // (class, window, d0/t1)
	std::map<std::tuple<uint32_t, uint64_t, uint32_t>, SkcWindow> m_skc_cp_reads;  // (site, address, d0/t1)
	uint32_t                                                      m_skc_cpu_lines = 0;
	uint32_t                                                      m_skc_cp_lines  = 0;

	bool IsBufferInvalid(BufferId id) const {
		const auto* buffer = m_slot_buffers.try_get(id);
		return buffer == nullptr || buffer->is_deleted;
	}

	using BufferMap = std::map<uint64_t, BufferId>;
	struct OverlapResult {
		BufferMap::iterator first;
		BufferMap::iterator last;
		uint64_t            begin;
		uint64_t            end;
		bool                has_stream_leap;
	};

	struct DownloadCopy;
	using PageTable = MultiLevelPageTable<BufferId, CACHING_PAGEBITS, 40, 16>;
	static_assert(CACHING_PAGESIZE == (uint64_t {1} << PageTable::kPageBits));
	static constexpr uint64_t               DOWNLOAD_ALIGNMENT = 64;
	[[nodiscard]] static constexpr uint64_t AlignDownload(uint64_t size) noexcept {
		return Common::AlignUp(size, DOWNLOAD_ALIGNMENT);
	}
	[[nodiscard]] static std::pair<uint64_t, uint64_t> DownloadEnvelope(const DownloadCopy& copy);
	void WriteDataBuffer(Buffer& buffer, uint64_t address, const void* source, uint64_t size);
	void TouchBuffer(Buffer& buffer);
	[[nodiscard]] OverlapResult ResolveOverlaps(uint64_t vaddr, uint64_t size);
	void JoinOverlap(BufferId new_id, BufferId overlap_id, bool accumulate_stream_score);
	[[nodiscard]] BufferId CreateBuffer(uint64_t vaddr, uint64_t size);
	void                   Register(BufferId id);
	void Unregister(BufferId id);
	template <bool insert>
	void ChangeRegister(BufferId id);
	void DeleteBuffer(BufferId id);
	[[nodiscard]] std::pair<uint64_t, uint8_t> UploadEpoch(uint64_t vaddr, uint64_t size);
	// Session 136, knob "bindlean": `carry` - only from the slow path of ObtainBuffer (s.4.3); every other caller nullptr.
	[[nodiscard]] bool SynchronizeBuffer(Buffer& buffer, uint64_t vaddr, uint64_t size,
										 bool is_written, bool is_texel_buffer, const SyncCarry* carry = nullptr);
	// Gate "syncfree": true when a read-only synchronization may skip the region locks.
	[[nodiscard]] bool SyncFreeSkip(uint64_t vaddr, uint64_t size, const SyncCarry* carry = nullptr);
	// Session 136, knob "bindlean" 2/3 (s.5.2): the comparisons of part (a) and part (b) of a carried call.
	void BindLeanVerifyA(uint64_t vaddr, uint64_t size, const SyncCarry& carry, uint8_t kind);
	void BindLeanVerifyB(uint64_t vaddr, uint64_t size, const SyncCarry& carry, bool clean);
	[[nodiscard]] vk::Buffer UploadCopies(Buffer& buffer, std::span<vk::BufferCopy> copies,
	                                      uint64_t total_size);
	// Records the staging -> buffer copies of one synchronization (no-op without a source).
	void RecordBufferCopies(Buffer& buffer, vk::Buffer source,
	                        std::span<const vk::BufferCopy> copies, uint64_t total_size);
	// Gate "protbatch2": the first half of a read-only SynchronizeBuffer - everything up to the
	// copy. True when the range has bytes to copy once the caller's pass flush returned.
	[[nodiscard]] bool CollectBufferUpload(Buffer& buffer, uint64_t vaddr, uint64_t size,
	                                       std::vector<vk::BufferCopy>& copies,
	                                       uint64_t& total_size);
	[[nodiscard]] bool SynchronizeBufferFromImage(Buffer& buffer, uint64_t vaddr, uint64_t size);
	void DownloadBufferMemory(std::span<const DownloadCopy> copies, const char* reason = "read");
	[[nodiscard]] static uint64_t StagingRingBytes();
	// Returns true when the region was handed to Common::AsyncMemcpy (session 91: the callers
	// count the two branches where the decision is taken).
	bool CopyGuestToStaging(uint8_t* staging, uint64_t vaddr, uint64_t size);
	// Session 129, knob "armcopy": CopyGuestToStaging of an operation latched 1..4 (design129.md rev 2 s.2.2, C3).
	bool CopyGuestToStagingArmed(uint8_t* staging, uint64_t vaddr, uint64_t size, uint32_t mode);
	// Session 129, knob "armcopy" 2/3: the content row after a chunk copy (Common::ArmedCopyHook::check, s.7.3).
	static void ArmCopyContent(void* context, uint64_t vaddr, size_t size, uint32_t mode, const uint8_t* dst,
	                           const uint8_t* src);
	// Session 130, knob "acinline" (I6, I9): the check hook of an inline-class chunk - ArmCopyContent plus ai_cmp_pages /
	// ai_cbad.
	static void ArmCopyContentInline(void* context, uint64_t vaddr, size_t size, uint32_t mode, const uint8_t* dst,
	                                 const uint8_t* src);
	static void ArmCopyContentImpl(void* context, uint64_t vaddr, size_t size, uint32_t mode, const uint8_t* dst,
	                               const uint8_t* src, bool inline_class);
	// Knob "bufimp" (route D1): resolve every copy region of one upload into the
	// VK_EXT_external_memory_host alias of the guest backing store, so that the GPU can
	// read the guest pages instead of a staging copy of them.  Fills the thread-local
	// region list RecordBufferCopies consumes, and returns true ONLY when every region
	// resolved; the caller keeps the staging path otherwise.  Counts its population
	// either way, which is what knob value 1 is for.
	[[nodiscard]] bool TryImportUploadCopies(Buffer& buffer,
	                                        std::span<const vk::BufferCopy> copies);
	// Image source through the guest-memory import: the range is copied on the GPU from the
	// imported backing into a device-local scratch buffer (no host memcpy). False when the range
	// is not direct memory or the import is unavailable.
	[[nodiscard]] bool ObtainImportedImageSource(uint64_t vaddr, uint64_t size,
	                                             ImageSource* result, bool reupload_check = true);
	void NotePendingHostRead(uint64_t vaddr, uint64_t size, uint64_t tick);
	void ReadMemoryOnGpu(uint64_t vaddr, uint64_t size, bool is_write);
	[[nodiscard]] AsyncReadback BeginAsyncReadback(uint64_t vaddr, uint64_t size);
	bool                        FinishAsyncReadback(const AsyncReadback& job);
	// GPU thread: make the GPU-dirty pages around a CPU read readable at once (stale data) and
	// schedule the download that brings the completed GPU data in later. See ReadMemory.
	void ServeStaleRead(uint64_t vaddr, uint64_t size);
	void ApplyReadbackPieces(const std::vector<ReadbackPiece>& pieces, const uint8_t* data,
	                         uint64_t seq);

	GraphicContext&                                   m_graphics;
	CommandScheduler&                                 m_scheduler;
	FaultManager                                      m_fault_manager;
	HostImport                                        m_host_import;
	struct PendingHostRead {
		uint64_t vaddr = 0;
		uint64_t size  = 0;
		uint64_t tick  = 0;
	};
	std::vector<PendingHostRead>                       m_pending_host_reads;
	Common::DiagB32::TrackedMutex<std::mutex>                                         m_pending_host_reads_mutex; // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, ROADMAP s122 item 574(g)(1))
	std::vector<Libs::LibKernel::Memory::BackingPiece> m_import_pieces;
	// Image address -> tick of its last upload through the import (re-upload interval heuristic).
	std::unordered_map<uint64_t, uint64_t>              m_import_last_tick;
	Buffer                                            m_gds_buffer;
	uint64_t                                          m_gds_host_epoch   = 1;
	uint64_t                                          m_gds_shader_epoch = 1;
	Buffer                                            m_bda_pagetable_buffer;
	Buffer                                            m_bda_null_page;
	bool                                              m_bda_null_page_ready = false;
	Common::SlotVector<Buffer>                        m_slot_buffers;
	Common::LeastRecentlyUsedCache<BufferId, uint64_t> m_lru_cache;
	BufferMap                                         m_buffers;
	std::vector<GuestRange>                            m_bda_dirty_ranges;
	struct BdaRegionStamp {
		MemoryTracker::RegionStamp stamp;
		uint64_t                   generation = 0;
		// Track F, F29c (KYTY_FIX_B12): the BDA pass (m_bda_pass) whose scanning visit last wrote this witness; 0 - none.
		// Written and read at KYTY_FIX_B12=1 only.
		uint64_t                   walked_pass = 0;
		// F29c edition 2 (item 641(v)(1)): the BDA pass whose FIRST visit of this region skipped it (by the bit or by the
		// witness); 0 - none. Never changes stamp or generation. Written and read at KYTY_FIX_B12=1 only.
		uint64_t                   skipped_pass = 0;
	};
	// One entry per tracking region, filled lazily on the first incremental scan.
	std::vector<BdaRegionStamp>                        m_bda_region_stamps;
	uint64_t                                           m_bda_stamp_generation = 1;
	// Session 113, knob "bdanarrow": see NoteBdaMapInvalidation / MarkBdaRegions; the scanning thread, for the
	// same-thread check of the marks.
	uint64_t                                           m_bda_map_generation = 1;
	bool                                               m_bda_narrow_check   = false;
	std::thread::id                                    m_bda_scan_thread {};
	// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d)): the number of the current BDA pass and whether it is open
	// (BeginBdaPass .. EndBdaPass); the running totals of the "FixB12Stat:" line (revisits; revisits whose collected
	// piece overlaps a registered buffer) and the values and time of its last print. Render mutex (PrepareBda) only.
	uint64_t                                           m_bda_pass      = 0;
	bool                                               m_bda_pass_open = false;
	uint64_t                                           m_b12_rewalk    = 0;
	uint64_t                                           m_b12_rwd       = 0;
	uint64_t                                           m_b12_lskip     = 0; // F29c edition 2, item 641(v)(3)
	uint64_t                                           m_b12_stat_pass   = 0;
	uint64_t                                           m_b12_stat_rewalk = 0;
	uint64_t                                           m_b12_stat_rwd    = 0;
	uint64_t                                           m_b12_stat_lskip  = 0;
	std::chrono::steady_clock::time_point              m_b12_stat_time {};
	// Marks the stamps of the tracking regions of [vaddr, vaddr + size) stale (a buffer was registered there).
	void MarkBdaRegions(uint64_t vaddr, uint64_t size);
	// Knob 2 of "bdanarrow": whether the dirty ranges just collected overlap any registered buffer (the first overlap
	// is returned through the optional pointers, for the miss log).
	bool DirtyRangesTouchBuffers(uint64_t* range_address = nullptr, uint64_t* range_size = nullptr,
	                             uint64_t* buffer_address = nullptr, uint64_t* buffer_size = nullptr);
	void SynchronizeBuffersByRegion(uint64_t scan_begin, uint64_t scan_end);
	void SynchronizeBuffersOfDirtyRanges();
	void SynchronizeBuffersOfDirtyRangesBatched(PageManager::PassScope& pass);
	// Gate "protbatch2": one collected synchronization of the current pass, copied after its flush.
	struct PassUpload {
		BufferId                    id;
		uint64_t                    vaddr      = 0;
		uint64_t                    size       = 0;
		uint64_t                    total_size = 0;
		std::vector<vk::BufferCopy> copies;
	};
	// Storage kept between passes (177 passes a frame): only the first entries are live.
	std::vector<PassUpload>                            m_pass_uploads;
	size_t                                             m_pass_upload_count = 0;
	// The entries above are object state that outlives the collection phase: a reentrant pass
	// would take them over while this one still copies from them.
	bool                                               m_in_pass = false;
	uint64_t                                          m_registration_epoch = 1;
	PageTable                                         m_page_table;
	RangeSet                                          m_gpu_modified_ranges;
	MemoryTracker                                     m_memory_tracker;
	StreamBuffer                                      m_staging_buffer;
	// Session 129, knob "armcopy": the hook of the armed pool copies (PageManager::ArmCopyChunk, ArmCopyContent).
	Common::ArmedCopyHook                             m_arm_copy_hook {};
	// Session 130, knob "acinline": the hook of the inline-class chunks (PageManager::ArmCopyChunkInline,
	// ArmCopyContentInline) - the class travels with the job as its hook.
	Common::ArmedCopyHook                             m_arm_copy_hook_inline {};
	StreamBuffer                                      m_stream_buffer;
	// Gate "cbstat": shadows of the stream-ring constant copies, keyed by (address, size).
	struct StreamCopyShadow {
		std::vector<uint8_t> bytes;
		uint64_t             epoch       = 0;
		uint64_t             generation  = 0;
		uint64_t             ring_offset = 0;
	};
	std::unordered_map<uint64_t, StreamCopyShadow>    m_stream_shadows;
	uint64_t                                          m_stream_shadow_bytes = 0;
	StreamBuffer                                      m_download_buffer;
	StreamBuffer                                      m_device_buffer;
	TextureCache&                                     m_texture_cache;
	uint64_t                                          m_total_used_memory  = 0;
	uint64_t m_trigger_gc_memory  = 1ull * 1024 * 1024 * 1024;
	uint64_t m_critical_gc_memory = 2ull * 1024 * 1024 * 1024;
	uint64_t m_gc_tick            = 0;
	// Gate "buffast": tells the per-thread memo entries of different cache objects apart.
	static uint64_t NextInstance() {
		static std::atomic<uint64_t> next {1};
		return next.fetch_add(1, std::memory_order_relaxed);
	}
	uint64_t m_instance = NextInstance();

	// Readback prefetch state (PrefetchHotReadbacks). A hot region is the 512 KB window around
	// an address whose CPU read had to drain the GPU; GPU writes are sequence-stamped per 64 KB
	// bucket so a completed prefetch only clears the dirty state when no newer write landed.
	struct HotRegion {
		uint64_t begin          = 0;
		uint64_t end            = 0;
		uint32_t hits           = 0;
		int      last_hit_frame = 0;
		bool     in_flight      = false;
	};
	static constexpr uint32_t HotBucketBits = 16;
	std::unordered_map<uint64_t, HotRegion> m_hot_regions;
	std::unordered_map<uint64_t, uint64_t>  m_bucket_write_seq;
	uint64_t                                m_gpu_write_seq   = 0;
	uint64_t                                m_large_write_seq = 0;
	// Track F, F16k (KYTY_FIX_F5CMU / KYTY_DIAG_F5ID, ROADMAP s122 item 492(v)(3)): the exact write journal - the last K
	// GPU writes {lo, hi, seq} of each 64 KB bucket, beside m_bucket_write_seq and written by NoteGpuWrite in the same
	// place (the GuestGpu thread), only while DiagF5::ExactRingOn() (read once: the journal holds every write of the
	// process or none). A write larger than 16 MB touches no bucket and no ring, as before. Read only by
	// LastGpuWriteSeqExact; no decision of the cache reads it.
	struct ExactWrite {
		uint64_t lo  = 0;
		uint64_t hi  = 0;
		uint64_t seq = 0;
	};
	struct ExactRing {
		static constexpr uint32_t K = 8;
		std::array<ExactWrite, K> writes {};
		uint64_t                  count = 0; // writes recorded in this bucket; writes[(count - 1) % K] is the last
	};
	std::unordered_map<uint64_t, ExactRing> m_bucket_write_ring;
	void                   NoteGpuWrite(uint64_t vaddr, uint64_t size);

 public:
	// Sequence number of the last GPU write to the 64 KB buckets of the range (include_large: also the
	// floor set by any write larger than 16 MB, which is not tracked per bucket).
	[[nodiscard]] uint64_t LastGpuWriteSeq(uint64_t vaddr, uint64_t size, bool include_large = true) const;
	// Track F, F16k (item 492(v)(3)): the exact form of LastGpuWriteSeq(vaddr, size, false) after `since`. `seq` - the
	// newest recorded write with seq > since that crosses [vaddr, vaddr + size) (0 - none). `fallback` - a bucket of the
	// range has a write newer than `since` while its ring holds K writes all newer than `since` and older ones were
	// dropped (the history since `since` may be incomplete): only the bucket answer is safe there. Needs
	// DiagF5::ExactRingOn(); a bucket without a ring (not possible then) is a fallback.
	struct ExactWriteSeq {
		uint64_t seq      = 0;
		bool     fallback = false;
	};
	[[nodiscard]] ExactWriteSeq LastGpuWriteSeqExact(uint64_t vaddr, uint64_t size, uint64_t since) const;
	// Track F, F16k2 (KYTY_DIAG_F5ID, ROADMAP s122 item 496(b)(1)-(2)): the sequence number of the last GPU write larger
	// than 16 MB (m_large_write_seq: no bucket, no ring, any address), and MemoryTracker::RangeWriteEpoch of a range
	// (0 - an empty or invalid range, or a region not tracked; lock free). Measurement only: no decision reads them.
	[[nodiscard]] uint64_t LargeGpuWriteSeq() const noexcept { return m_large_write_seq; }
	[[nodiscard]] uint64_t F5IdRangeWriteEpoch(uint64_t vaddr, uint64_t size);

 private:

	// Stream prefetch queue (NoteStreamedRead / PrefetchStreamedRanges).
	Common::DiagB32::TrackedMutex<std::mutex>                                     m_streamed_mutex; // Track F, F20j3 (KYTY_DIAG_B32 W:emu_mutex, ROADMAP s122 item 574(g)(1))
	std::vector<std::pair<uint64_t, uint64_t>>     m_streamed_ranges;
	std::vector<std::pair<uint64_t, uint64_t>>     m_streamed_pending;
	int                                            m_streamed_frame    = -1;
	uint64_t                                       m_streamed_spent_ns = 0;
	uint64_t                                       m_prefetch_pending_bytes = 0;
	void                                           ClearPrefetchPending(Buffer& buffer);
	[[nodiscard]] bool IsRegionFullyRegistered(uint64_t vaddr, uint64_t size);
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_BUFFERCACHE_H_
