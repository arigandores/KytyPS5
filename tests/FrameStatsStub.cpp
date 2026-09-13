// Focused test targets link the SRT walker without the emulator's frame statistics.
#include "common/frameStats.h"
#include "common/gates.h"

namespace Common::FrameStats {

bool Enabled() {
	return false;
}

uint64_t NowNs() {
	return 0;
}

// The count limit stays 0, so the inline Add never attaches a shard.
Detail::Shard* Detail::AttachShard() {
	static Shard sink;
	return &sink;
}

void SetLean(bool /*lean*/) {}

} // namespace Common::FrameStats

namespace Common::Gates {

// The runtime gates belong to the emulator's flip loop; the focused targets always run the
// production path.
bool Detail::EnabledSlow(Gate /*gate*/) noexcept {
	return false;
}

uint32_t Detail::ValueSlow(Knob /*knob*/) noexcept {
	return 0;
}

void Poll(uint32_t /*frame*/) noexcept {}

} // namespace Common::Gates
