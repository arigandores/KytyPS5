#include "graphics/host_gpu/renderer/commandRecorder.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/presentation/renderDoc.h"

#include <chrono>
#include <cstring>
#include <mutex>
#include <vector>

namespace Libs::Graphics {

namespace {

// A missed notification can only cost this much: every wait is bounded, so a lost wake-up is a
// latency bug and never a hang.
constexpr auto WaitSlice = std::chrono::milliseconds(1);

struct Payloads {
	struct BeginBuffer {
		uint64_t tick;
	};
	struct Timestamp {
		vk::QueryPool pool;
		uint64_t      tick;
		uint64_t      key;
		uint64_t      key2;
		uint32_t      query;
		uint32_t      reset;
		uint32_t      bottom;
		uint32_t      kind;
		uint32_t      gpu_begin;
	};
	struct Generic {
		Common::UniqueFunction<void, vk::CommandBuffer>* command;
	};
};

static_assert(std::is_trivially_copyable_v<Payloads::BeginBuffer>);
static_assert(std::is_trivially_copyable_v<Payloads::Timestamp>);
static_assert(std::is_trivially_copyable_v<Payloads::Generic>);

std::mutex&                     RecordersMutex() {
	static std::mutex mutex;
	return mutex;
}

std::vector<CommandRecorder*>& Recorders() {
	static std::vector<CommandRecorder*> recorders;
	return recorders;
}

uint64_t ArenaBytes() {
	auto megabytes = Common::Gates::Value(Common::Gates::Knob::RecordArenaMb);
	if (megabytes == 0) {
		megabytes = 1;
	}
	const uint64_t wanted = uint64_t {megabytes} * 1024u * 1024u;
	uint64_t       bytes  = 1024u * 1024u;
	while (bytes < wanted) {
		bytes *= 2u;
	}
	return bytes;
}

} // namespace

CommandRecorder::CommandRecorder(CommitFn commit, void* user, vk::CommandBuffer* current,
                                 GpuTimeProfiler* gpu_time)
    : m_commit(commit), m_user(user), m_current(current), m_gpu_time(gpu_time) {
	EXIT_IF(commit == nullptr || current == nullptr);
	m_capacity = ArenaBytes();
	m_mask     = m_capacity - 1;
	m_data     = std::make_unique<uint8_t[]>(static_cast<size_t>(m_capacity));
	{
		std::lock_guard lock(RecordersMutex());
		Recorders().push_back(this);
	}
	m_thread = std::thread([this] { Loop(); });
}

CommandRecorder::~CommandRecorder() {
	Stop();
	std::lock_guard lock(RecordersMutex());
	auto&           recorders = Recorders();
	for (size_t index = 0; index < recorders.size(); index++) {
		if (recorders[index] == this) {
			recorders.erase(recorders.begin() + static_cast<std::ptrdiff_t>(index));
			break;
		}
	}
}

void CommandRecorder::Stop() {
	if (!m_thread.joinable()) {
		return;
	}
	Drain();
	m_stop.store(true, std::memory_order_release);
	{
		std::lock_guard lock(m_mutex);
		m_pending.notify_all();
	}
	m_thread.join();
}

size_t CommandRecorder::Backlog() const noexcept {
	const auto head = m_head.load(std::memory_order_acquire);
	const auto tail = m_tail.load(std::memory_order_acquire);
	return static_cast<size_t>(head - tail);
}

void CommandRecorder::WakeConsumer() {
	if (m_consumer_waiting.load(std::memory_order_acquire)) {
		std::lock_guard lock(m_mutex);
		m_pending.notify_one();
	}
}

void CommandRecorder::WakeWaiters() {
	if (m_waiters.load(std::memory_order_seq_cst) != 0) {
		std::lock_guard lock(m_mutex);
		m_progress.notify_all();
	}
}

uint8_t* CommandRecorder::Reserve(uint32_t bytes) {
	EXIT_IF(bytes == 0 || (bytes % RecordAlign) != 0 ||
	        static_cast<uint64_t>(bytes) > m_capacity / 2u);
	for (;;) {
		const auto head       = m_head.load(std::memory_order_relaxed);
		const auto index      = static_cast<uint32_t>(head & m_mask);
		const auto contiguous = static_cast<uint32_t>(m_capacity - index);
		// A record never straddles the end of the ring: when it does not fit, a Pad record fills
		// the remainder and the reservation restarts at offset 0.
		const auto want = bytes <= contiguous ? bytes : contiguous + bytes;
		const auto used = head - m_tail.load(std::memory_order_acquire);
		if (m_capacity - used < want) {
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			{
				std::unique_lock lock(m_mutex);
				m_waiters.fetch_add(1, std::memory_order_seq_cst);
				m_progress.wait_for(lock, WaitSlice, [this, head, want] {
					const auto in_use = head - m_tail.load(std::memory_order_acquire);
					return m_capacity - in_use >= want;
				});
				m_waiters.fetch_sub(1, std::memory_order_seq_cst);
			}
			FS::Add(FS::Counter::RecordFull, 1);
			if (t0 != 0) {
				FS::Add(FS::Counter::RecordFullNs, FS::NowNs() - t0);
			}
			WakeConsumer();
			continue;
		}
		if (bytes > contiguous) {
			const RecordHeader pad {contiguous, static_cast<uint16_t>(RecordOp::Pad), 0};
			std::memcpy(m_data.get() + index, &pad, sizeof(pad));
			m_head.store(head + contiguous, std::memory_order_release);
			WakeConsumer();
			continue;
		}
		return m_data.get() + index;
	}
}

void CommandRecorder::Publish(uint32_t bytes) {
	const auto head = m_head.load(std::memory_order_relaxed);
	m_head.store(head + bytes, std::memory_order_release);
	WakeConsumer();
}

void CommandRecorder::PushRecord(RecordOp op, const void* payload, uint32_t payload_size) {
	uint32_t bytes = static_cast<uint32_t>(sizeof(RecordHeader)) + payload_size;
	bytes          = (bytes + RecordAlign - 1u) & ~(RecordAlign - 1u);
	auto*              slot = Reserve(bytes);
	const RecordHeader header {bytes, static_cast<uint16_t>(op), 0};
	std::memcpy(slot, &header, sizeof(header));
	if (payload_size != 0) {
		std::memcpy(slot + sizeof(RecordHeader), payload, payload_size);
	}
	Publish(bytes);
	namespace FS = Common::FrameStats;
	FS::Add(FS::Counter::RecordPackets, 1);
	FS::Add(FS::Counter::RecordBytes, bytes);
}

void CommandRecorder::PushBeginBuffer(uint64_t tick) {
	const Payloads::BeginBuffer payload {tick};
	PushRecord(RecordOp::BeginBuffer, &payload, sizeof(payload));
}

void CommandRecorder::PushEndBuffer(const RecordSubmit& request) {
	PushRecord(RecordOp::EndBuffer, &request, sizeof(request));
}

void CommandRecorder::PushTimestamp(vk::QueryPool pool, uint32_t query, uint32_t reset,
                                    bool bottom) {
	EXIT_IF(pool == nullptr);
	Payloads::Timestamp payload {};
	payload.pool   = pool;
	payload.query  = query;
	payload.reset  = reset;
	payload.bottom = bottom ? 1u : 0u;
	PushRecord(RecordOp::Timestamp, &payload, sizeof(payload));
}

void CommandRecorder::PushGpuTime(uint64_t tick, bool begin, GpuTimeProfiler::Kind kind,
                                  uint64_t key, uint64_t key2) {
	Payloads::Timestamp payload {};
	payload.tick      = tick;
	payload.key       = key;
	payload.key2      = key2;
	payload.kind      = static_cast<uint32_t>(kind);
	payload.gpu_begin = begin ? 1u : 0u;
	PushRecord(RecordOp::Timestamp, &payload, sizeof(payload));
}

void CommandRecorder::PushGeneric(Common::UniqueFunction<void, vk::CommandBuffer>&& command) {
	EXIT_IF(!command);
	// The callable outlives the record: the record thread invokes it and deletes it.
	const Payloads::Generic payload {
	    new Common::UniqueFunction<void, vk::CommandBuffer>(std::move(command))};
	PushRecord(RecordOp::Generic, &payload, sizeof(payload));
}

void CommandRecorder::Drain() {
	EXIT_IF(std::this_thread::get_id() == m_thread.get_id());
	const auto target = m_head.load(std::memory_order_acquire);
	if (m_tail.load(std::memory_order_acquire) >= target) {
		return;
	}
	namespace FS  = Common::FrameStats;
	const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
	WakeConsumer();
	{
		std::unique_lock lock(m_mutex);
		m_waiters.fetch_add(1, std::memory_order_seq_cst);
		while (m_tail.load(std::memory_order_acquire) < target) {
			m_progress.wait_for(lock, WaitSlice, [this, target] {
				return m_tail.load(std::memory_order_acquire) >= target;
			});
		}
		m_waiters.fetch_sub(1, std::memory_order_seq_cst);
	}
	FS::Add(FS::Counter::RecordDrains, 1);
	if (t0 != 0) {
		FS::Add(FS::Counter::RecordDrainNs, FS::NowNs() - t0);
	}
}

void CommandRecorder::Execute(const RecordHeader& header, const uint8_t* payload) {
	switch (static_cast<RecordOp>(header.op)) {
		case RecordOp::Pad: break;
		case RecordOp::BeginBuffer: {
			Payloads::BeginBuffer begin {};
			std::memcpy(&begin, payload, sizeof(begin));
			const auto buffer = m_commit(m_user, begin.tick);
			EXIT_IF(buffer == nullptr);
			m_buffer = buffer;
			// Read by the resolving thread only after a Drain(), which acquires the tail this
			// thread releases below.
			*m_current = buffer;
			vk::CommandBufferBeginInfo info {};
			info.flags        = vk::CommandBufferUsageFlagBits::eOneTimeSubmit;
			const auto result = buffer.begin(&info);
			EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
			break;
		}
		case RecordOp::EndBuffer: {
			RecordSubmit request;
			std::memcpy(&request, payload, sizeof(request));
			EXIT_IF(m_buffer == nullptr);
			const auto result = m_buffer.end();
			EXIT_NOT_IMPLEMENTED(result != vk::Result::eSuccess);
			if (request.async) {
				EnqueueAsyncSubmit(request, m_buffer);
			}
			break;
		}
		case RecordOp::Timestamp: {
			Payloads::Timestamp mark {};
			std::memcpy(&mark, payload, sizeof(mark));
			EXIT_IF(m_buffer == nullptr);
			if (mark.pool != nullptr) {
				if (mark.reset != 0) {
					m_buffer.resetQueryPool(mark.pool, mark.query, mark.reset);
				}
				m_buffer.writeTimestamp(mark.bottom != 0 ? vk::PipelineStageFlagBits::eBottomOfPipe
				                                         : vk::PipelineStageFlagBits::eTopOfPipe,
				                        mark.pool, mark.query);
			} else if (m_gpu_time != nullptr) {
				if (mark.gpu_begin != 0) {
					m_gpu_time->Begin(m_buffer, mark.tick);
				} else {
					m_gpu_time->Mark(m_buffer, mark.tick,
					                 static_cast<GpuTimeProfiler::Kind>(mark.kind), mark.key,
					                 mark.key2);
				}
			}
			break;
		}
		case RecordOp::Generic: {
			Payloads::Generic generic {};
			std::memcpy(&generic, payload, sizeof(generic));
			EXIT_IF(generic.command == nullptr || m_buffer == nullptr);
			(*generic.command)(m_buffer);
			delete generic.command;
			break;
		}
	}
}

void CommandRecorder::Loop() {
	Common::FrameStats::RegisterCurrentThread(Common::FrameStats::ThreadRole::Record);
	for (;;) {
		const auto tail = m_tail.load(std::memory_order_relaxed);
		if (m_head.load(std::memory_order_acquire) == tail) {
			if (m_stop.load(std::memory_order_acquire)) {
				return;
			}
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			{
				std::unique_lock lock(m_mutex);
				m_consumer_waiting.store(true, std::memory_order_release);
				m_pending.wait_for(lock, WaitSlice, [this, tail] {
					return m_stop.load(std::memory_order_acquire) ||
					       m_head.load(std::memory_order_acquire) != tail;
				});
				m_consumer_waiting.store(false, std::memory_order_release);
			}
			if (t0 != 0) {
				FS::Add(FS::Counter::RecordIdleNs, FS::NowNs() - t0);
			}
			continue;
		}
		const auto   index = static_cast<uint32_t>(tail & m_mask);
		RecordHeader header {};
		std::memcpy(&header, m_data.get() + index, sizeof(header));
		EXIT_IF(header.size < sizeof(RecordHeader));
		{
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			Execute(header, m_data.get() + index + sizeof(RecordHeader));
			if (t0 != 0) {
				FS::Add(FS::Counter::RecordWorkNs, FS::NowNs() - t0);
			}
		}
		m_tail.store(tail + header.size, std::memory_order_release);
		WakeWaiters();
	}
}

void DrainRecordQueues() {
	std::lock_guard lock(RecordersMutex());
	for (auto* recorder: Recorders()) {
		recorder->Drain();
	}
}

size_t RecordBacklog() {
	std::lock_guard lock(RecordersMutex());
	size_t          total = 0;
	for (const auto* recorder: Recorders()) {
		total += recorder->Backlog();
	}
	return total;
}

bool RecordThreadWanted(const GraphicContext& graphics) {
	if (graphics.gpu_breadcrumbs_enabled || graphics.diagnostic_checkpoints_enabled) {
		return false;
	}
	if (RenderDocCapturing()) {
		return false;
	}
	return Common::Gates::Enabled(Common::Gates::Gate::RecordThread);
}

} // namespace Libs::Graphics
