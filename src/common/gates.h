#ifndef EMULATOR_SRC_COMMON_GATES_H_
#define EMULATOR_SRC_COMMON_GATES_H_

#include <cstdint>

namespace Common::Gates {

// Optimizations that can be turned on and off while the emulator runs, so that one gameplay run
// can compare them against itself instead of against another run with a different trajectory.
// Each gate starts from its own environment variable and keeps that value unless a gate file is
// given (KYTY_GATE_FILE), which Poll() re-reads once per flip.
enum class Gate : uint32_t {
	ConstantCopy,   // KYTY_CBUFFER_DIRECT_COPY, file name "copy"
	SrtPagePersist, // KYTY_SRT_PAGE_PERSIST,    file name "srtpages"
	ClampMemo,      // KYTY_CLAMP_MEMO,          file name "clamp"
	RegionEpoch,    // KYTY_REGION_EPOCH,        file name "regionepoch"
	SrtMemo,        // KYTY_SRT_MEMO,            file name "srtmemo"
	SrtMemoCheck,   // KYTY_SRT_MEMO_VERIFY,     file name "smemocheck"
	BdaRegionStamps, // KYTY_BDA_REGION_STAMPS,  file name "bdastamp"
	BackingPages,   // KYTY_BACKING_PAGES,       file name "backpages"
	SrtStat,        // KYTY_SRT_STAT,            file name "srtstat"
	MetaLock,       // KYTY_META_LOCK,           file name "metalock"
	Count,
};

// Relaxed read of the current state. Safe to call from any thread and from hot paths.
[[nodiscard]] bool Enabled(Gate gate) noexcept;

// Re-reads the gate file (if any) and publishes changes. Called once per flip.
void Poll(uint32_t frame) noexcept;

} // namespace Common::Gates

#endif // EMULATOR_SRC_COMMON_GATES_H_
