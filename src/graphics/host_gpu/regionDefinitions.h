#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONDEFINITIONS_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONDEFINITIONS_H_

#include "common/bitArray.h"
#include "common/common.h"

#include <atomic>
#include <compare>

namespace Libs::Graphics {

constexpr uint64_t TRACKER_PAGE_SIZE    = 4ull * 1024ull;
constexpr uint64_t TRACKER_REGION_SIZE  = 4ull * 1024ull * 1024ull;
constexpr uint64_t TRACKER_ADDRESS_SIZE = 1ull << 40u;
constexpr size_t   TRACKER_REGION_PAGES = TRACKER_REGION_SIZE / TRACKER_PAGE_SIZE;

// Gate "bdabits" (session 82): one bit per tracking region, set wherever the region's write stamp
// can move and cleared by the BDA scan before it reads that region.  A CONSERVATIVE SUPERSET of
// "the stamp moved": a clear bit proves the stamp is unchanged, a set bit proves nothing and the
// stamp is consulted as before.  See BufferCache::SynchronizeBuffersByRegion.
// 2^40 of address space in 4 MiB regions is 262 144 bits = 32 KiB, zero-initialised.
constexpr size_t TRACKER_BDA_WORDS = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE / 64;
inline std::atomic<uint64_t> g_bda_write_bits[TRACKER_BDA_WORDS];

// Called wherever a region's write epoch is published, and on region creation.  Any thread.
inline void BdaNoteRegionWrite(uint64_t index) noexcept {
	if (const auto word = index / 64u; word < TRACKER_BDA_WORDS) {
		g_bda_write_bits[word].fetch_or(uint64_t {1} << (index % 64u), std::memory_order_release);
	}
}

// Test and clear, for the consumer.  True means "an announcement may have happened": the caller
// must fall through to the stamp.  Cleared BEFORE the region is read, so a racing write re-sets it.
inline bool BdaTakeRegionWrite(uint64_t index) noexcept {
	const auto word = index / 64u;
	if (word >= TRACKER_BDA_WORDS) {
		return true; // outside the map: never skip on its authority
	}
	const auto bit = uint64_t {1} << (index % 64u);
	if ((g_bda_write_bits[word].load(std::memory_order_acquire) & bit) == 0) {
		return false;
	}
	g_bda_write_bits[word].fetch_and(~bit, std::memory_order_acq_rel);
	return true;
}

struct GuestRange {
	uint64_t address = 0;
	uint64_t size    = 0;

	[[nodiscard]] constexpr bool Empty() const noexcept { return address == 0 && size == 0; }
	[[nodiscard]] constexpr bool Valid() const noexcept {
		return address != 0 && size != 0 && address < TRACKER_ADDRESS_SIZE &&
		       size <= TRACKER_ADDRESS_SIZE - address;
	}
	[[nodiscard]] constexpr bool     ValidOrEmpty() const noexcept { return Empty() || Valid(); }
	[[nodiscard]] constexpr uint64_t End() const noexcept { return address + size; }
	auto                             operator<=>(const GuestRange&) const = default;
};

enum class DirtySource { Cpu, Gpu };
using RegionBits = Common::BitArray<TRACKER_REGION_PAGES>;
static_assert(sizeof(RegionBits) == TRACKER_REGION_PAGES / 8);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_REGIONDEFINITIONS_H_
