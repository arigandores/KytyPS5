#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUTIMEPROFILER_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUTIMEPROFILER_H_

#include "common/common.h"
#include "graphics/host_gpu/vulkanCommon.h"

#include <atomic>
#include <cstdint>
#include <deque>
#include <mutex>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics {

struct GraphicContext;
class MasterSemaphore;

// KYTY_GPU_TIME=1: attribution of GPU time at live clocks. A bottom-of-pipe timestamp is written
// after every draw, dispatch, barrier, upload, clear and render pass boundary, and a top-of-pipe
// one at the start of every command buffer; the time between consecutive timestamps is charged to
// the operation that ends at the later one (the gap before a command buffer start is "idle": the
// GPU waited for the host). Once per guest frame the table is logged:
//   GpuTime: frame=<n> total_us=<gpu time> idle_us=<gap> marks=<n> dropped=<n>
//   GpuTime-kind: frame=<n> draw=<us> dispatch=<us> imgbar=<us> ...
//   GpuTime-top: frame=<n> <kind>:<key hex>[/<key2 hex>] us=<us> n=<count>   (largest first)
// Query slots are handed out in chunks per command buffer (vkCmdResetQueryPool must run outside
// a render pass instance); a buffer that needs more than ChunkSlots marks is truncated.
class GpuTimeProfiler final {
public:
	enum class Kind : uint8_t {
		Idle,
		Draw,
		Dispatch,
		ImageBarrier,
		Barrier,
		BufferUpload,
		ImageUpload,
		RenderPass,
		Clear,
		Other,
		Count
	};

	GpuTimeProfiler(GraphicContext& graphics, MasterSemaphore& master);
	~GpuTimeProfiler();
	KYTY_CLASS_NO_COPY(GpuTimeProfiler);

	[[nodiscard]] static bool Enabled();
	// Guest frame number of the marks recorded from now on (set at every flip).
	static void SetFrame(uint32_t frame);
	// Creates the query pool (only the main GuestGpu scheduler profiles; the present scheduler
	// does not).
	void Enable();

	// Command buffer start (outside a render pass): resets the chunk and writes the top-of-pipe
	// timestamp that separates the inter-submission gap.
	void Begin(vk::CommandBuffer command, uint64_t tick);
	// Bottom-of-pipe timestamp charged to (kind, key, key2).
	void Mark(vk::CommandBuffer command, uint64_t tick, Kind kind, uint64_t key, uint64_t key2 = 0);
	// Reads the timestamps of completed ticks and logs finished frames.
	void Harvest(bool force = false);

private:
	struct Pending {
		uint64_t tick  = 0;
		uint64_t key   = 0;
		uint64_t key2  = 0;
		uint32_t frame = 0;
		uint32_t slot  = 0;
		Kind     kind  = Kind::Idle;
		bool     begin = false;
	};
	struct Entry {
		uint64_t ns = 0;
		uint64_t n  = 0;
	};
	struct FrameTable {
		std::unordered_map<uint64_t, Entry> entries; // key: kind<<56 ^ hash(key, key2)
		std::unordered_map<uint64_t, std::pair<uint64_t, uint64_t>> keys;
		uint64_t                             kind_ns[static_cast<size_t>(Kind::Count)] {};
		uint64_t                             total_ns = 0;
		uint64_t                             marks    = 0;
	};

	void FlushFrame(uint32_t frame, FrameTable& table);

	static constexpr uint32_t ChunkSlots = 2048;
	static constexpr uint32_t Chunks     = 64;

	GraphicContext&      m_graphics;
	MasterSemaphore&     m_master;
	vk::QueryPool        m_pool = nullptr;
	double               m_period_ns = 0.0;
	uint32_t             m_bits      = 64;
	std::vector<uint64_t> m_chunk_tick;  // tick of the command buffer using each chunk
	uint32_t             m_chunk       = UINT32_MAX; // chunk of the current command buffer
	uint32_t             m_chunk_used  = 0;
	uint32_t             m_next_chunk  = 0;
	uint64_t             m_dropped     = 0;
	std::deque<Pending>  m_pending;
	std::mutex           m_mutex;
	// Harvest state: the previous timestamp (to compute deltas) and per-frame tables.
	bool                 m_have_previous = false;
	uint64_t             m_previous_ts   = 0;
	std::unordered_map<uint32_t, FrameTable> m_frames;
	uint32_t             m_last_flushed_frame = 0;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_GPUTIMEPROFILER_H_
