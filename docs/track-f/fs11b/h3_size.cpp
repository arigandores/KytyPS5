// FS11b (HPP-715, Red Team, ROADMAP s122 item 647(g) H3): size of BdaRegionStamp before (dc5d4712) and after (ee9632be),
// layouts copied from bufferCache.h:380 and memoryTracker.h:59 of each tree; REGION_COUNT from memoryTracker.h:411.
#include <cstdint>
#include <cstdio>
#include <cstddef>
struct RegionStamp { const void* manager = nullptr; uint64_t epoch = 0; };
struct Base { RegionStamp stamp; uint64_t generation = 0; };
struct Fs11 { RegionStamp stamp; uint64_t generation = 0; uint64_t walked_pass = 0; uint64_t skipped_pass = 0; };
constexpr uint64_t TRACKER_REGION_SIZE = 4ull * 1024ull * 1024ull;
constexpr uint64_t TRACKER_ADDRESS_SIZE = 1ull << 40u;
constexpr size_t REGION_COUNT = TRACKER_ADDRESS_SIZE / TRACKER_REGION_SIZE;
int main() {
  std::printf("REGION_COUNT %zu sizeof base %zu fs11 %zu bytes base %zu fs11 %zu growth %zu\n", REGION_COUNT, sizeof(Base), sizeof(Fs11),
              REGION_COUNT * sizeof(Base), REGION_COUNT * sizeof(Fs11), REGION_COUNT * (sizeof(Fs11) - sizeof(Base)));
}
