#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_

#include "common/assert.h"
#include "common/frameStats.h"
#include "graphics/host_gpu/pageManager.h"
#include "graphics/host_gpu/regionDefinitions.h"

#include <atomic>
#include <cstdlib>
#include <mutex>
#include <utility>

#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#undef min
#undef max
#elif defined(__APPLE__)
#include <pthread.h>
#elif defined(__linux__)
#include <sys/syscall.h>
#include <unistd.h>
#endif

namespace Libs::Graphics {

class TrackingSpinLock final {
public:
	void lock() noexcept {
		const auto thread = CurrentThread();
		if (m_owner.load(std::memory_order_relaxed) == thread) {
			EXIT("recursive region tracking lock\n");
		}
		if (m_lock.test_and_set(std::memory_order_acquire)) {
			// Contended: spin, and account the wait for KYTY_FRAME_TRACE.
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::Enabled() ? FS::NowNs() : 0;
			static const bool relaxed_spin = [] {
				const auto* value = std::getenv("KYTY_TRACKING_RELAXED_SPIN");
				return value == nullptr || value[0] != '0';
			}();
			while (m_lock.test_and_set(std::memory_order_acquire)) {
				if (m_owner.load(std::memory_order_relaxed) == thread) {
					EXIT("recursive region tracking lock while contended\n");
				}
				if (relaxed_spin) {
					// Wait with shared reads instead of repeatedly invalidating the owner's
					// cache line. The acquire RMW above still grants exclusive ownership.
					while (m_lock.test(std::memory_order_relaxed)) {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
						YieldProcessor();
#elif defined(__x86_64__) || defined(__i386__)
						__builtin_ia32_pause();
#elif defined(__aarch64__)
						asm volatile("yield");
#else
						std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
					}
				} else {
					std::atomic_signal_fence(std::memory_order_seq_cst);
				}
			}
			if (t0 != 0) {
				const auto ns = FS::NowNs() - t0;
				FS::Add(FS::Counter::LockSpinNs, ns);
				FS::Add(FS::Counter::LockSpins, 1);
				if (FS::CurrentRole() == FS::ThreadRole::Gpu) {
					FS::Add(FS::Counter::LockSpinGpuNs, ns);
				}
			}
		}
		m_owner.store(thread, std::memory_order_relaxed);
	}
	void unlock() noexcept {
		if (m_owner.load(std::memory_order_relaxed) != CurrentThread()) {
			EXIT("region tracking lock released by non-owner\n");
		}
		m_owner.store(0, std::memory_order_relaxed);
		m_lock.clear(std::memory_order_release);
	}

private:
	static uint32_t CurrentThread() noexcept {
#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS
		return GetCurrentThreadId();
#elif defined(__APPLE__)
		// mach thread port is a nonzero per-thread id (0 is the "no owner" sentinel).
		return static_cast<uint32_t>(pthread_mach_thread_np(pthread_self()));
#elif defined(__linux__)
		static thread_local const uint32_t tid = static_cast<uint32_t>(::syscall(SYS_gettid));
		return tid;
#else
		EXIT("region tracking thread identity is unsupported on this platform\n");
#endif
	}

	std::atomic_flag     m_lock = ATOMIC_FLAG_INIT;
	std::atomic_uint32_t m_owner {0};
};

static_assert(std::atomic_uint32_t::is_always_lock_free);

class RegionManager final {
public:
	RegionManager(PageManager& page_manager, uint64_t cpu_addr, std::atomic<uint64_t>& cpu_epoch)
	    : m_page_manager(page_manager), m_cpu_addr(cpu_addr), m_cpu_epoch(cpu_epoch) {
		if (m_cpu_addr % TRACKER_REGION_SIZE != 0) {
			EXIT("invalid region tracking manager construction\n");
		}
		m_cpu_dirty.Fill();
		m_writable.Fill();
		m_readable.Fill();
	}

	KYTY_CLASS_NO_COPY(RegionManager);

	[[nodiscard]] uint64_t GetCpuAddr() const { return m_cpu_addr; }
	// Write epoch of this region only. The global CPU epoch moves on every page fault anywhere
	// in the address space, which makes it useless as a "did this range change" witness; this
	// one moves only when a page of this 4 MiB region is announced as CPU-written.
	[[nodiscard]] uint64_t Epoch() const noexcept {
		return m_epoch.load(std::memory_order_acquire);
	}
	template <DirtySource source>
	[[nodiscard]] bool IsModified(uint64_t offset, uint64_t size) const {
		const auto [start, end] = GetPageRange(m_cpu_addr + offset, size);
		const auto& bits        = GetBits<source>();
		return bits.AnyInRange(start, end);
	}

	// IsModified without holding `lock` (gate "trackfree", see MemoryTracker for the
	// ownership argument that makes each possible stale answer safe). Non-const because the
	// words are read through std::atomic_ref, which does not bind to a const object.
	template <DirtySource source>
	[[nodiscard]] bool IsModifiedRelaxed(uint64_t offset, uint64_t size) {
		const auto [start, end] = GetPageRange(m_cpu_addr + offset, size);
		return GetBits<source>().AnyInRangeRelaxed(start, end);
	}

	template <DirtySource source, bool enable>
	void ChangeState(uint64_t vaddr, uint64_t size) {
		const auto [start, end] = GetPageRange(vaddr, size);
		if constexpr (source == DirtySource::Cpu && enable) {
			if (m_gpu_dirty.AnyInRange(start, end)) {
				EXIT("CPU dirty state conflicts with GPU dirty state\n");
			}
		}
		if constexpr (source == DirtySource::Gpu && enable) {
			if (m_cpu_dirty.AnyInRange(start, end)) {
				EXIT("GPU dirty state conflicts with CPU dirty state\n");
			}
		}
		auto& bits = GetBits<source>();
		if constexpr (enable) {
			if constexpr (source == DirtySource::Cpu) {
				// m_cpu_dirty is set from guest threads (InvalidateRegion) while the GuestGpu
				// thread may be scanning it without this lock, so every word it touches has to
				// be written atomically. Nothing else writes either map off that thread.
				bits.SetRangeRelaxed(start, end);
			} else {
				bits.SetRange(start, end);
			}
		} else {
			bits.UnsetRange(start, end);
		}
		if constexpr (source == DirtySource::Cpu && enable) {
			// Called with the region lock held, after the bits and before the pages become
			// writable (UpdateProtection below). Bits first, epochs second: a lock-free reader of
			// the bits (gate "syncfree") takes its epoch snapshot before it reads them, so an
			// announcement it missed moves the epochs after that snapshot and the next
			// HasCurrentUpload check fails. A BDA scan observing these epochs still acquires this
			// lock before it reads dirty bits, so the order does not matter to it.
			m_cpu_epoch.fetch_add(1, std::memory_order_release);
			m_epoch.fetch_add(1, std::memory_order_release);
		}
		if constexpr (source == DirtySource::Cpu) {
			UpdateProtection<!enable, false>();
		} else {
			// A new GPU write (or a completed download) ends the stale window of these pages:
			// the next CPU read faults again and is served from the latest completed data.
			m_stale.UnsetRange(start, end);
			UpdateProtection<enable, true>();
		}
	}

	// GPU-dirty pages of [vaddr, vaddr+size) become readable by the CPU without a fault while
	// their GPU writes are still in flight (BufferCache::ServeStaleRead): the CPU observes the
	// last completed GPU data, as it would on hardware, instead of draining the queue.
	void MarkStaleReadable(uint64_t vaddr, uint64_t size) {
		const auto [start, end] = GetPageRange(vaddr, size);
		RegionBits range;
		range.SetRange(start, end);
		range &= m_gpu_dirty;
		if (range.None()) {
			return;
		}
		m_stale |= range;
		UpdateProtection<false, true>();
	}

	template <DirtySource source, bool clear, typename Func>
	void ForEachModifiedRange(uint64_t vaddr, uint64_t size, Func&& func) {
		const auto [start, end] = GetPageRange(vaddr, size);
		auto&      bits         = GetBits<source>();
		RegionBits mask(bits, start, end);
		if constexpr (clear) {
			bits.UnsetRange(start, end);
			if constexpr (source == DirtySource::Cpu) {
				UpdateProtection<true, false>();
			} else {
				m_stale.UnsetRange(start, end);
				UpdateProtection<false, true>();
			}
		}
		for (const auto [first, last]: mask) {
			func(m_cpu_addr + first * TRACKER_PAGE_SIZE, (last - first) * TRACKER_PAGE_SIZE);
		}
	}

	TrackingSpinLock lock;

private:
	template <bool track, bool is_read>
	void UpdateProtection() {
		const auto protection = is_read ? (~m_gpu_dirty | m_stale) : m_cpu_dirty;
		auto&      previous   = is_read ? m_readable : m_writable;
		auto       mask       = protection ^ previous;
		if (mask.None()) {
			return;
		}
		previous = protection;
		// prot_held_us: every caller of UpdateProtection already holds `lock`, so this scope
		// is exactly the time the region lock stays held across the host protection change
		// (VirtualProtect plus the address-space mutex behind it). Diagnostic, no gate.
		Common::FrameStats::Scope held(Common::FrameStats::Counter::ProtectHeldNs);
		PageManager::SpinHeld    spin_held; // prot_spin_*: `lock` is held across the calls below
		m_page_manager.UpdatePageWatchersForRegion<track, is_read>(m_cpu_addr, mask);
	}

	template <DirtySource source>
	RegionBits& GetBits() {
		if constexpr (source == DirtySource::Cpu) {
			return m_cpu_dirty;
		} else {
			return m_gpu_dirty;
		}
	}

	template <DirtySource source>
	const RegionBits& GetBits() const {
		if constexpr (source == DirtySource::Cpu) {
			return m_cpu_dirty;
		} else {
			return m_gpu_dirty;
		}
	}

	[[nodiscard]] std::pair<size_t, size_t> GetPageRange(uint64_t vaddr, uint64_t size) const {
		if (size == 0 || vaddr < m_cpu_addr || vaddr >= m_cpu_addr + TRACKER_REGION_SIZE ||
		    size > m_cpu_addr + TRACKER_REGION_SIZE - vaddr) {
			EXIT("range lies outside its tracking region\n");
		}
		const auto offset = vaddr - m_cpu_addr;
		return {static_cast<size_t>(offset / TRACKER_PAGE_SIZE),
		        static_cast<size_t>((offset + size + TRACKER_PAGE_SIZE - 1) / TRACKER_PAGE_SIZE)};
	}

	PageManager& m_page_manager;
	uint64_t     m_cpu_addr = 0;
	std::atomic<uint64_t>& m_cpu_epoch;
	std::atomic<uint64_t>  m_epoch {1};
	// The dirty maps are read without the lock (IsModifiedRelaxed); give them their own
	// cache lines so those reads do not fight `lock`, which otherwise shares a line with
	// the first words of m_cpu_dirty.
	alignas(64) RegionBits m_cpu_dirty;
	RegionBits   m_gpu_dirty;
	RegionBits   m_stale; // subset of m_gpu_dirty: readable by the CPU while GPU writes are in flight
	RegionBits   m_writable;
	RegionBits   m_readable;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONMANAGER_H_
