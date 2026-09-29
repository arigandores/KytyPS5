#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_

#include "common/common.h"
#include "graphics/host_gpu/regionDefinitions.h"

#include <array>
#include <cstdint>
#include <memory>

namespace Libs::Graphics {

enum class PageFaultAccess { Read, Write, Execute, Unknown };

class PageManager final {
	struct Impl;

public:
	PageManager();
	// The owner must stop all PageManager callers before destruction.
	~PageManager();

	KYTY_CLASS_NO_COPY(PageManager);

	[[nodiscard]] uint64_t GetPageSize() const;

	template <bool track>
	void UpdatePageWatchers(uint64_t vaddr, uint64_t size);
	template <bool track, bool is_read = false>
	void UpdatePageWatchersForRegion(uint64_t base_addr, RegionBits& mask);

	// Adds write watchers like UpdatePageWatchers<true>, but the host protection change
	// (VirtualProtect, ~60-100 ns per page, serialized in the kernel) is applied by a worker
	// thread instead of the caller. Tracker state is updated synchronously, so untracking and
	// read-watcher changes stay correct; only the moment the pages become read-only is deferred.
	// A CPU write to such a page before the worker gets to it is not observed, so the caller must
	// DrainDeferredProtection() before the guest can learn that the GPU consumed the data (flip).
	// Falls back to the synchronous path when KYTY_ASYNC_PROTECT=0.
	void UpdatePageWatchersDeferred(uint64_t vaddr, uint64_t size);
	// Waits until every deferred protection change has been applied.
	void DrainDeferredProtection();
	// KYTY_ASYNC_PROTECT: whether UpdatePageWatchersDeferred defers at all.
	[[nodiscard]] static bool DeferEnabled();
	// Session 60, gate "armdefer": UpdatePageWatchersForRegion<true, false> whose host protection
	// change is applied by the worker (pending bits, like UpdatePageWatchersDeferred). The tracker
	// state is current at once; the pages become read-only on the host when the worker gets to them.
	void UpdatePageWatchersForRegionDeferred(uint64_t base_addr, RegionBits& mask);
	// Session 60, gate "armdefer": drops from `mask` every page whose host protection may still
	// lag behind its page state - a pending page, or one inside the application in flight. What
	// stays is protected as its page state says (Region::apply, P). Lock free, like FlushBlocker.
	void KeepApplied(uint64_t base_addr, RegionBits& mask);
	// Gate "armcheck": the host says the page is writable (VirtualQuery; false off Windows).
	[[nodiscard]] static bool IsHostWritable(uint64_t vaddr);

	// Gate "protbatch". While an enabled scope is alive on a thread, the write-watcher changes
	// this thread makes through this manager (not read watchers, not the deferred texture path)
	// only mark their pages pending; Flush() - and the destructor - apply them. The memory tracker
	// opens a scope around a region lock and flushes after releasing it and before the protection
	// has to be in effect (before a copy, before a fault handler returns), so no VirtualProtect of
	// those changes runs under the tracker's spin locks. A disabled scope does nothing: the gate
	// can change at any moment, each scope keeps the value it was opened with and flushes what it
	// deferred. At most Capacity regions per scope; changes of further regions stay synchronous.
	class BatchScope final {
	public:
		BatchScope(PageManager& manager, bool enabled) noexcept;
		~BatchScope();
		KYTY_CLASS_NO_COPY(BatchScope);

		void Flush() noexcept;
		// Knob "armcopy" 1..3 (design129.md rev 2 s.2.2, C2): the windows go to the operation running on this thread
		// unapplied (each pooled chunk arms its range, GuestGpu the rest in ArmCopyFinish); the scope applies nothing.
		void Handover() noexcept;

	private:
		friend struct PageManager::Impl;
		static constexpr uint32_t Capacity = 4;
		struct Slot {
			void*    region = nullptr;
			uint64_t base   = 0;
			uint32_t first  = UINT32_MAX; // page window this scope must apply
			uint32_t last   = 0;
		};
		PageManager&               m_manager;
		BatchScope*                m_previous = nullptr;
		std::array<Slot, Capacity> m_slots {};
		uint32_t                   m_count   = 0;
		bool                       m_enabled = false;
	};

	// Gate "protbatch2" (session 58, phase 2 of "protbatch"). One pass of read-only buffer
	// synchronizations - the BDA dirty-range scan of PrepareBda, which pays one scope flush and one
	// range flush per buffer today. Every range whose CPU-dirty bits the pass is about to consume is
	// noted here before it consumes them, and Flush() applies, once per tracking region, both the
	// write watchers the pass deferred into its BatchScope and any protection another caller left
	// pending on those ranges. The scope also attributes the host protection calls made inside it to
	// the pass (pb2_vp, pb2_vp_adj, pb2_vp_near), which measures the ceiling of the merge while the
	// gate is still off. At most Capacity windows are open at once; a further region joins the
	// window that has to stretch the least for it - a window may span several regions, because
	// FlushProtection walks every region of its range. Nothing is ever closed early: a range is
	// noted BEFORE its pages are armed, so a window flushed here would have nothing pending yet
	// and would leave the deferred protection of another caller on its pages unapplied.
	class PassScope final {
	public:
		// `owns_flush`: the caller relies on this scope for the protection of its ranges (gate on).
		// Without it the scope only counts and the per-synchronization flushes stay where they are.
		PassScope(PageManager& manager, bool owns_flush) noexcept;
		~PassScope();
		KYTY_CLASS_NO_COPY(PassScope);

		// The pass is about to clear the CPU-dirty bits of this range. Does nothing when the
		// scope owns no flush and the counters are off: there is no one left to serve then.
		void Note(uint64_t vaddr, uint64_t size);
		// Must return before the pass reads a guest byte of any range it noted.
		void Flush();

	private:
		friend struct PageManager::Impl;
		static constexpr uint32_t Capacity = 8;
		struct Window {
			uint64_t base  = 0; // tracking region the window lies in
			uint64_t begin = 0;
			uint64_t end   = 0;
		};
		void NoteProtect(uint64_t vaddr, uint64_t size, uint32_t mode) noexcept;

		PageManager&                 m_manager;
		PassScope*                   m_previous = nullptr;
		std::array<Window, Capacity> m_windows {};
		uint32_t                     m_count      = 0;
		bool                         m_owns_flush = false;
		// The previous host protection call of this pass, for the merge counters above.
		uint64_t                     m_last_end  = 0;
		uint64_t                     m_last_base = 0;
		uint32_t                     m_last_mode = 0;
		bool                         m_last_seen = false;
	};

	// Applies protection changes of [vaddr, vaddr + size) that are still pending, waiting for one
	// another thread is applying right now (gate "protbatch": an invalidation must not return
	// while its page is logically writable but still protected on the host).
	void FlushProtection(uint64_t vaddr, uint64_t size);
	// Gate "pbcheck": VirtualQuery of the first and the last page of the range against the page
	// state (pb_check, pb_bad, pb_bad_rw; mismatches are printed as "PbCheck: MISMATCH").
	void VerifyProtection(uint64_t vaddr, uint64_t size);

	// Marks a scope in which the calling thread holds a tracker spin lock (RegionManager::lock,
	// TextureCache::m_lock) while it changes page watchers: host protection calls made inside are
	// counted as prot_spin_*. Diagnostic only.
	class SpinHeld final {
	public:
		SpinHeld() noexcept { t_depth++; }
		~SpinHeld() { t_depth--; }
		KYTY_CLASS_NO_COPY(SpinHeld);

		[[nodiscard]] static uint32_t Depth() noexcept { return t_depth; }

	private:
		inline static thread_local uint32_t t_depth = 0;
	};

	// Session 128, knob "protceil" (MEASUREMENT ONLY, never shipped; docs/session-128/design128.md rev 1 s.4-5 with
	// ROADMAP s122 items 88, 89). The latch of one buffer synchronization: constructed around the whole ForEachUploadRange
	// of BufferCache::SynchronizeBuffer, `engage` = on the GuestGpu thread. It reads the knob ONCE (a nested scope
	// inherits the outer latch); at 1, unless refused (armdefer; protbatch2 with protbatch), no host protection change to
	// read-only that arms a write watcher is made on this thread until it closes - the synchronous run of
	// UpdateRegionWatchers and the runs its flushes apply - and their pages are marked unarmed (U, per region, under
	// `apply`). The tracker changes exactly as at 0. Invariant (P'): the host is never stricter than the tracker and
	// differs only by the write bit of a U page. Off the GuestGpu thread nothing is latched (pc_offthr at 1 or 2).
	// At 2 (the dose, ROADMAP s122 item 93(g)(1)) every call is made as at 0 and each one a latch of 1 would skip is
	// followed by a spin of its own duration; refused without the FrameStats clock.
	class CeilScope final {
	public:
		explicit CeilScope(bool engage) noexcept;
		~CeilScope();
		KYTY_CLASS_NO_COPY(CeilScope);

	private:
		bool    m_engaged  = false;
		uint8_t m_previous = 0;
	};
	// Knob "protceil": some page is unarmed. GuestGpu thread only (only its latches of 1 mark pages).
	[[nodiscard]] bool HasUnarmed() const noexcept;
	// Knob "protceil" (item 89(v)(1)): the re-arm pass after the arm edge 1 -> 0, GuestGpu thread, no lock held. Each run
	// of unarmed pages the tracker keeps read-only (U, not pending, Perms() == Read) is handed to `declare` - the
	// guest-write declaration, which re-uploads and re-arms them the ordinary way; what it leaves read-only on the
	// tracker is protected read-only here (the fallback). A pending U page loses the mark (its application writes
	// Perms()); a U page not read-only on the tracker is pc_rearm_odd (impossible by P').
	using DeclareFunc = void (*)(void* context, uint64_t vaddr, uint64_t size);
	void CeilRearm(void* context, DeclareFunc declare);

	// Session 129, knob "armcopy" (PROTOTYPE; docs/session-129/design129.md rev 2 with ROADMAP s122 items 97(e), 98, 99,
	// 101). The latch of one buffer synchronization, next to CeilScope around the whole ForEachUploadRange of
	// BufferCache::SynchronizeBuffer, `engage` = on the GuestGpu thread. It reads the knob ONCE (a nested scope inherits the
	// outer latch) and at a value >= 1 checks the refusals (s.8.2). A written synchronization at >= 1 takes the path of 0
	// (its armings are ac_kept_wr_* at 1..3). Off the GuestGpu thread nothing is latched (ac_offthr).
	class ArmCopyScope final {
	public:
		ArmCopyScope(bool engage, bool is_written) noexcept;
		~ArmCopyScope();
		KYTY_CLASS_NO_COPY(ArmCopyScope);

	private:
		bool    m_engaged        = false;
		uint8_t m_previous_state = 0;
		uint8_t m_previous_mode  = 0;
		// Session 130, knob "acinline": the outer latch's acinline flag to restore (a nested scope leaves it untouched).
		uint8_t m_previous_ai = 0;
	};
	// Why GuestGpu still arms at a latch of 1..3 (ac_kept_{inl,gap,tmp}_*); every other arming there is "full". Session 130,
	// knob "acinline" (design130.md rev 2 s.4 I2', I10): the inline copy of an operation with acinline=1 left on GuestGpu -
	// meets no window (InlNowin), not one backing mapping (InlNomap), or >= 64 KiB not in one mapping (InlBig); each is
	// also ac_kept_inl_* (the same class as Inline).
	enum class ArmCopyReason : uint8_t { Full, Inline, Gap, Tmp, InlNowin, InlNomap, InlBig };
	// ForEachUploadRange of a read-only synchronization outside a pass and outside armdefer: the mode of this operation,
	// 0 = the previous path, else the latch 1..4. A nonzero answer is followed by ArmCopyFinish on the same thread.
	[[nodiscard]] uint32_t ArmCopyBegin() noexcept;
	// The mode of the operation running on this thread (UploadCopies), 0 outside one.
	[[nodiscard]] static uint32_t ArmCopyOpMode() noexcept;
	// UploadCopies at 1..3: a copy of the operation, pooled (its chunks arm it) or not (GuestGpu arms it before reading).
	void ArmCopyNoteCopy(uint64_t vaddr, uint64_t size, bool pooled);
	// UploadCopies at 1..3: GuestGpu arms [vaddr, vaddr + size) before it reads the guest bytes (an inline copy, the
	// temporary buffer); at 3 in the order take -> check -> apply (s.7.5).
	void ArmCopyFlush(uint64_t vaddr, uint64_t size, ArmCopyReason reason);
	// UploadCopies at 1..3, temporary buffer: GuestGpu arms every handed-over window before it reads the guest view.
	void ArmCopyFlushWindows();
	// Right after upload_func (s.2.2, RC7): at 1..3 the rest of the windows (ac_kept_gap_*), ac_orphan and at 2/3 the
	// GuestGpu-branch detector (s.7.5); ends the operation at every mode.
	void ArmCopyFinish();
	// The arm hook of a pool chunk (Common::ArmedCopyHook::arm, context = this PageManager), any thread (s.7.4).
	static bool ArmCopyChunk(void* context, uint64_t vaddr, size_t size, uint32_t mode, uint8_t* dst,
	                         const uint8_t* src);
	// Session 130, ac_cbad attribution (docs/session-130/cbad130.md rev 2 s.4 C4/C5, ROADMAP s122 items 116(d), 117-119):
	// the classification of the content events of the chunk this thread just checked (2/3/4 only - never called at 0/1).
	// The class counts of one check, summed over its batches; the caller adds them in the order of I0 (s.6.1, 6.1').
	struct ArmCopyClassCounts {
		uint64_t m      = 0; // ac_cbad_m
		uint64_t e      = 0; // ac_cbad_e
		uint64_t nosnap = 0; // R1
		uint64_t bad    = 0; // R2
		uint64_t left   = 0; // R3
		uint64_t stale  = 0; // R4
		uint64_t remark = 0; // R5
		uint64_t fresh  = 0; // R6 "new"
		uint64_t pend   = 0; // R7
		uint64_t host   = 0; // R8
		uint64_t host_d = 0; // of R8, CPU-dirty in the hold S_k (ac_cbm_host_d)
		uint64_t ro     = 0;
		uint64_t na     = 0;
		uint64_t oth    = 0;
	};
	// The CPU-dirty read of one tracker page (the buffer cache's lock-free IsCpuDirtyRelaxed), for dk in the hold S_k.
	using ArmCopyDirtyFunc = bool (*)(void* context, uint64_t page);
	// The largest batch of event pages one classification takes (one `apply` hold S_k).
	static constexpr size_t ArmCopyClassBatch = 64;
	// A batch of n <= ArmCopyClassBatch event pages (tracker-page addresses) of the chunk {vaddr, size, mode}; any thread,
	// no lock held. Adds ac_cls_*, writes the CONTENT lines and the address histogram, adds the class counts to `counts`.
	void ArmCopyClassify(uint64_t vaddr, uint64_t size, uint32_t mode, const uint64_t* pages, size_t n,
	                     ArmCopyDirtyFunc dirty, void* dirty_context, ArmCopyClassCounts* counts);
	// The last action of the chunk's check: its snapshot S_a is no longer valid on this thread.
	static void ArmCopyClassDone() noexcept;
	// Session 130, knob "acinline" (PROTOTYPE; docs/session-130/design130.md rev 2 with ROADMAP s122 items 105(zh)(1), 107,
	// 109, 110), GuestGpu thread, TLS of the operation only - no lock.
	// The operation running on this thread latched armcopy 1..3 with acinline=1 (I1'').
	[[nodiscard]] static bool ArmCopyInlineOn() noexcept;
	// [vaddr, vaddr + size) meets a window the operation was handed over (I4) - a superset of "carries its arming".
	[[nodiscard]] static bool ArmCopyInlineWindow(uint64_t vaddr, uint64_t size) noexcept;
	// UploadCopies put the inline copy [vaddr, vaddr + size) in the batch (I2'): ai_jobs, ai_b, ai_pages, pending + 1.
	static void ArmCopyInlineNote(uint64_t vaddr, uint64_t size) noexcept;
	// The entry of UploadCopies (I3'): a batch of `items` or a pending count left over is a fatal stop, never a clear.
	static void ArmCopyInlineEntry(size_t items) noexcept;
	// After AsyncMemcpyArmedBatch of n items (I3'): n must equal the pending count, which it clears; else a fatal stop.
	static void ArmCopyInlineEnqueued(size_t n) noexcept;
	// The arm hook of an inline-class chunk (I6): ArmCopyChunk with the class flag of this thread set for its duration.
	static bool ArmCopyChunkInline(void* context, uint64_t vaddr, size_t size, uint32_t mode, uint8_t* dst,
	                               const uint8_t* src);

private:
	std::unique_ptr<Impl> m_impl;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_
