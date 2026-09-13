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

private:
	std::unique_ptr<Impl> m_impl;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_PAGEMANAGER_H_
