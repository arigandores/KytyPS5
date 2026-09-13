// Focused test targets link the SRT walker without the emulator's frame statistics.
#include "common/frameStats.h"
#include "common/gates.h"

namespace Common::FrameStats {

bool TimingsEnabled() { return false; }

bool Enabled() {
	return false;
}

uint64_t NowNs() {
	return 0;
}

void Add(Counter /*counter*/, uint64_t /*value*/) {}

} // namespace Common::FrameStats

namespace Common::Gates {

// The runtime gates belong to the emulator's flip loop; the focused targets always run the
// production path.
bool Enabled(Gate /*gate*/) noexcept { return false; }

void Poll(uint32_t /*frame*/) noexcept {}

} // namespace Common::Gates
