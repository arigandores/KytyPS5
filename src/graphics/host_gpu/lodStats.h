#ifndef KYTY_GRAPHICS_HOST_GPU_LOD_STATS_H_
#define KYTY_GRAPHICS_HOST_GPU_LOD_STATS_H_

#include "common/common.h"

#include <array>
#include <atomic>

// Texture LOD statistics (the hardware "mip stats" counters selected by the T# COUNTER_BANK_ID /
// LOD_HDW_CNT_EN fields). Every texture binding with the counter enabled touches its bank; the
// IT_GET_LOD_STATS packet dumps the banks into the guest record and optionally resets them.
//
// Record layout expected by ASTRO BOT (GfxMipStatsManager): 16 header dwords (word 0 != 0 marks a
// valid record) followed by 256 qwords, one per bank: bits 0..23 = sample count ("Drawn"),
// bits 56..59 = smallest mip level sampled, 0xf when the bank was not sampled during the interval.
namespace Libs::Graphics::LodStats {

constexpr uint32_t BANK_COUNT = 256;
constexpr uint32_t NO_SAMPLES = 0xF;

struct Bank {
	std::atomic<uint32_t> count {0};
	std::atomic<uint32_t> min_mip {NO_SAMPLES};
};

inline std::array<Bank, BANK_COUNT>& Banks() {
	static std::array<Bank, BANK_COUNT> banks;
	return banks;
}

inline void Touch(uint8_t bank, uint32_t mip) {
	auto& b = Banks()[bank];
	b.count.fetch_add(1, std::memory_order_relaxed);
	uint32_t current = b.min_mip.load(std::memory_order_relaxed);
	while (mip < current && !b.min_mip.compare_exchange_weak(current, mip, std::memory_order_relaxed)) {
	}
}

inline void Reset() {
	for (auto& b: Banks()) {
		b.count.store(0, std::memory_order_relaxed);
		b.min_mip.store(NO_SAMPLES, std::memory_order_relaxed);
	}
}

} // namespace Libs::Graphics::LodStats

#endif // KYTY_GRAPHICS_HOST_GPU_LOD_STATS_H_
