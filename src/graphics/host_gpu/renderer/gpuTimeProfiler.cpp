#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"

#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/masterSemaphore.h"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <string>

namespace Libs::Graphics {

namespace {

std::atomic<uint32_t> g_frame {0};

const char* KindName(GpuTimeProfiler::Kind kind) {
	switch (kind) {
		case GpuTimeProfiler::Kind::Idle: return "idle";
		case GpuTimeProfiler::Kind::Draw: return "draw";
		case GpuTimeProfiler::Kind::Dispatch: return "dispatch";
		case GpuTimeProfiler::Kind::ImageBarrier: return "imgbar";
		case GpuTimeProfiler::Kind::Barrier: return "barrier";
		case GpuTimeProfiler::Kind::BufferUpload: return "bufup";
		case GpuTimeProfiler::Kind::ImageUpload: return "imgup";
		case GpuTimeProfiler::Kind::RenderPass: return "rpass";
		case GpuTimeProfiler::Kind::Clear: return "clear";
		case GpuTimeProfiler::Kind::Other: return "other";
		default: return "?";
	}
}

uint64_t EntryKey(GpuTimeProfiler::Kind kind, uint64_t key, uint64_t key2) {
	uint64_t h = key * 0x9e3779b97f4a7c15ull;
	h ^= (key2 + 0x632be59bd9b4e019ull) * 0xbf58476d1ce4e5b9ull;
	h ^= h >> 29u;
	return (static_cast<uint64_t>(kind) << 56u) ^ (h & ((uint64_t {1} << 56u) - 1u));
}

} // namespace

bool GpuTimeProfiler::Enabled() {
	static const bool enabled = std::getenv("KYTY_GPU_TIME") != nullptr;
	return enabled;
}

void GpuTimeProfiler::SetFrame(uint32_t frame) {
	g_frame.store(frame, std::memory_order_relaxed);
}

uint32_t GpuTimeProfiler::Frame() {
	return g_frame.load(std::memory_order_relaxed);
}

GpuTimeProfiler::GpuTimeProfiler(GraphicContext& graphics, MasterSemaphore& master)
    : m_graphics(graphics), m_master(master) {}

void GpuTimeProfiler::Enable() {
	if (!Enabled() || m_pool != nullptr) {
		return;
	}
	const auto& limits = m_graphics.physical_device_properties.limits;
	if (limits.timestampPeriod <= 0.0f) {
		return;
	}
	uint32_t count = 0;
	m_graphics.physical_device.getQueueFamilyProperties(&count, nullptr);
	std::vector<vk::QueueFamilyProperties> families(count);
	m_graphics.physical_device.getQueueFamilyProperties(&count, families.data());
	if (m_graphics.queue_family >= count ||
	    families[m_graphics.queue_family].timestampValidBits == 0) {
		LOGF("GpuTime: queue family has no timestamp support\n");
		return;
	}
	vk::QueryPoolCreateInfo info {};
	info.sType      = vk::StructureType::eQueryPoolCreateInfo;
	info.queryType  = vk::QueryType::eTimestamp;
	info.queryCount = ChunkSlots * Chunks;
	if (m_graphics.device.createQueryPool(&info, nullptr, &m_pool) != vk::Result::eSuccess) {
		m_pool = nullptr;
		LOGF("GpuTime: query pool creation failed\n");
		return;
	}
	m_period_ns = static_cast<double>(limits.timestampPeriod);
	m_bits      = families[m_graphics.queue_family].timestampValidBits;
	m_chunk_tick.assign(Chunks, 0);
	LOGF("GpuTime: enabled, %u slots, period %.3f ns\n", info.queryCount, m_period_ns);
}

GpuTimeProfiler::~GpuTimeProfiler() {
	if (m_pool != nullptr) {
		m_graphics.device.destroyQueryPool(m_pool, nullptr);
	}
}

void GpuTimeProfiler::Begin(vk::CommandBuffer command, uint64_t tick) {
	if (m_pool == nullptr) {
		return;
	}
	std::lock_guard lock(m_mutex);
	m_chunk = UINT32_MAX;
	for (int attempt = 0; attempt < 2 && m_chunk == UINT32_MAX; attempt++) {
		const auto candidate = m_next_chunk;
		if (m_chunk_tick[candidate] == 0 || m_master.IsFree(m_chunk_tick[candidate])) {
			m_chunk = candidate;
		} else if (attempt == 0) {
			m_master.Refresh();
		}
	}
	if (m_chunk == UINT32_MAX) {
		m_dropped++;
		return;
	}
	m_next_chunk         = (m_next_chunk + 1) % Chunks;
	m_chunk_tick[m_chunk] = tick;
	m_chunk_used         = 0;
	const auto first     = m_chunk * ChunkSlots;
	command.resetQueryPool(m_pool, first, ChunkSlots);
	command.writeTimestamp(vk::PipelineStageFlagBits::eTopOfPipe, m_pool, first);
	m_chunk_used = 1;
	m_pending.push_back({tick, 0, 0, g_frame.load(std::memory_order_relaxed), first, Kind::Idle, true});
}

void GpuTimeProfiler::Mark(vk::CommandBuffer command, uint64_t tick, Kind kind, uint64_t key,
                           uint64_t key2) {
	if (m_pool == nullptr) {
		return;
	}
	std::lock_guard lock(m_mutex);
	if (m_chunk == UINT32_MAX || m_chunk_used >= ChunkSlots || m_chunk_tick[m_chunk] != tick) {
		m_dropped++;
		return;
	}
	const auto slot = m_chunk * ChunkSlots + m_chunk_used++;
	command.writeTimestamp(vk::PipelineStageFlagBits::eBottomOfPipe, m_pool, slot);
	m_pending.push_back({tick, key, key2, g_frame.load(std::memory_order_relaxed), slot, kind, false});
}

void GpuTimeProfiler::Harvest(bool force) {
	if (m_pool == nullptr) {
		return;
	}
	std::lock_guard lock(m_mutex);
	if (m_pending.empty()) {
		return;
	}
	if (!m_master.IsFree(m_pending.front().tick)) {
		if (!force) {
			return;
		}
		m_master.Refresh();
	}
	std::vector<uint64_t> values;
	uint32_t              max_frame = 0;
	bool                  any       = false;
	while (!m_pending.empty() && m_master.IsFree(m_pending.front().tick)) {
		// Consecutive slots of one command buffer are read with a single query.
		const auto first = m_pending.front();
		size_t     count = 1;
		while (count < m_pending.size() && m_pending[count].tick == first.tick &&
		       m_pending[count].slot == first.slot + count) {
			count++;
		}
		values.assign(count, 0);
		const auto result = m_graphics.device.getQueryPoolResults(
		    m_pool, first.slot, static_cast<uint32_t>(count), count * sizeof(uint64_t),
		    values.data(), sizeof(uint64_t), vk::QueryResultFlagBits::e64);
		if (result == vk::Result::eNotReady) {
			break;
		}
		for (size_t i = 0; i < count; i++) {
			const auto& mark = m_pending[i];
			const auto  ts   = values[i];
			if (result == vk::Result::eSuccess) {
				if (m_have_previous) {
					uint64_t delta = ts - m_previous_ts;
					if (m_bits < 64) {
						delta &= (uint64_t {1} << m_bits) - 1u;
					}
					const auto ns    = static_cast<uint64_t>(static_cast<double>(delta) * m_period_ns);
					auto&      table = m_frames[mark.frame];
					const auto kind  = mark.begin ? Kind::Idle : mark.kind;
					table.kind_ns[static_cast<size_t>(kind)] += ns;
					table.total_ns += ns;
					table.marks++;
					if (!mark.begin) {
						const auto ek = EntryKey(kind, mark.key, mark.key2);
						auto&      e  = table.entries[ek];
						e.ns += ns;
						e.n++;
						table.keys.try_emplace(ek, mark.key, mark.key2);
					}
				}
				m_previous_ts   = ts;
				m_have_previous = true;
			}
			max_frame = std::max(max_frame, mark.frame);
			any       = true;
		}
		m_pending.erase(m_pending.begin(), m_pending.begin() + static_cast<std::ptrdiff_t>(count));
	}
	if (!any) {
		return;
	}
	// Marks are recorded in frame order: every frame below the newest harvested one is complete.
	std::vector<uint32_t> done;
	for (const auto& [frame, table]: m_frames) {
		if (frame < max_frame) {
			done.push_back(frame);
		}
	}
	std::sort(done.begin(), done.end());
	for (const auto frame: done) {
		FlushFrame(frame, m_frames[frame]);
		m_frames.erase(frame);
	}
}

void GpuTimeProfiler::FlushFrame(uint32_t frame, FrameTable& table) {
	LOGF("GpuTime: frame=%u total_us=%llu idle_us=%llu marks=%llu dropped=%llu\n", frame,
	     static_cast<unsigned long long>(table.total_ns / 1000u),
	     static_cast<unsigned long long>(table.kind_ns[static_cast<size_t>(Kind::Idle)] / 1000u),
	     static_cast<unsigned long long>(table.marks), static_cast<unsigned long long>(m_dropped));
	std::string kinds = "GpuTime-kind: frame=" + std::to_string(frame);
	for (size_t k = 0; k < static_cast<size_t>(Kind::Count); k++) {
		kinds += ' ';
		kinds += KindName(static_cast<Kind>(k));
		kinds += '=';
		kinds += std::to_string(table.kind_ns[k] / 1000u);
	}
	kinds += '\n';
	LOGF("%s", kinds.c_str());
	std::vector<std::pair<uint64_t, Entry>> sorted(table.entries.begin(), table.entries.end());
	std::sort(sorted.begin(), sorted.end(),
	          [](const auto& a, const auto& b) { return a.second.ns > b.second.ns; });
	size_t printed = 0;
	for (const auto& [ek, e]: sorted) {
		if (printed >= 32 || e.ns < 20'000) {
			break;
		}
		const auto  kind = static_cast<Kind>(ek >> 56u);
		const auto& keys = table.keys[ek];
		LOGF("GpuTime-top: frame=%u %s:%016llx/%016llx us=%llu n=%llu\n", frame, KindName(kind),
		     static_cast<unsigned long long>(keys.first),
		     static_cast<unsigned long long>(keys.second),
		     static_cast<unsigned long long>(e.ns / 1000u), static_cast<unsigned long long>(e.n));
		printed++;
	}
}

} // namespace Libs::Graphics
