// Focused test targets link the SRT walker without the emulator's frame statistics.
#include "common/frameStats.h"

namespace Common::FrameStats {

bool Enabled() {
	return false;
}

uint64_t NowNs() {
	return 0;
}

void Add(Counter /*counter*/, uint64_t /*value*/) {}

} // namespace Common::FrameStats
