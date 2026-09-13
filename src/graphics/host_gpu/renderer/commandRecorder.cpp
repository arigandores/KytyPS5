#include "graphics/host_gpu/renderer/commandRecorder.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/pipeline/shaderResourceBarrier.h"
#include "graphics/presentation/renderDoc.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <thread>
#include <vector>

#if defined(_M_X64) || defined(__x86_64__)
#include <immintrin.h>
#endif

namespace Libs::Graphics {

namespace {

// Waits stay bounded as a second line of defence; the handshakes below do not lose notifications.
// The process runs at a 1 ms timer period - SDL_InitSubSystem calls SDL_TicksInit, which calls
// timeBeginPeriod(1) - so a 1 ms slice is about 1 ms, not the 15.6 ms default period.
constexpr auto WaitSlice  = std::chrono::milliseconds(1);
constexpr auto SleepSlice = std::chrono::milliseconds(16);

void CpuPause() noexcept {
#if defined(_M_X64) || defined(__x86_64__)
	_mm_pause();
#else
	std::this_thread::yield();
#endif
}

// Knob "recspin": how long an idle record thread (and, up to 100 us, a drain) polls before it
// sleeps.
uint64_t SpinNs() noexcept {
	return uint64_t {Common::Gates::Value(Common::Gates::Knob::RecordSpinUs)} * 1000u;
}

struct Payloads {
	struct BeginBuffer {
		uint64_t tick;
	};
	// Query-pool timestamps of the command-buffer boundaries only. GPU-time marks used to travel
	// through here and were the reason a second thread recorded into a live command buffer.
	struct Timestamp {
		vk::QueryPool pool;
		uint32_t      query;
		uint32_t      reset;
		uint32_t      bottom;
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
                                 vk::Device device)
    : m_commit(commit), m_user(user), m_current(current), m_device(device) {
	EXIT_IF(commit == nullptr || current == nullptr || device == nullptr);
	m_capacity = ArenaBytes();
	m_mask     = m_capacity - 1;
	m_data     = std::make_unique<uint8_t[]>(static_cast<size_t>(m_capacity));
	// The thread first, the registry after: DrainRecordQueues() reads m_thread through Drain(),
	// and it may run on another thread as soon as this recorder is in the list. Nothing can be
	// owed to an unregistered recorder - only its owner publishes, and it has no pointer yet.
	m_thread = std::thread([this] { Loop(); });
	{
		std::lock_guard lock(RecordersMutex());
		Recorders().push_back(this);
	}
	LOGF("RecordThread: started recorder=%p arena=%lluKiB\n", static_cast<void*>(this),
	     static_cast<unsigned long long>(m_capacity / 1024u));
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
	LOGF("RecordThread: stopped recorder=%p records=%llu peak_backlog=%lluB full=%llu\n",
	     static_cast<void*>(this), static_cast<unsigned long long>(m_records),
	     static_cast<unsigned long long>(m_peak_backlog),
	     static_cast<unsigned long long>(m_full));
}

size_t CommandRecorder::Backlog() const noexcept {
	const auto head = m_head.load(std::memory_order_acquire);
	const auto tail = m_tail.load(std::memory_order_acquire);
	return static_cast<size_t>(head - tail);
}

void CommandRecorder::WakeConsumer() {
	if (m_consumer_waiting.load(std::memory_order_seq_cst)) {
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
			// Before the wait, not after it: a sleeping record thread would otherwise be told only
			// once this thread has already lost a wait slice.
			WakeConsumer();
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
			// With only the buffer boundaries published the arena never fills; if it does, the
			// record thread is not keeping up and the size of the backlog says by how much.
			if (++m_full <= 8) {
				LOGF("RecordThread: arena full recorder=%p want=%u used=%llu capacity=%llu\n",
				     static_cast<void*>(this), want,
				     static_cast<unsigned long long>(head -
				                                     m_tail.load(std::memory_order_acquire)),
				     static_cast<unsigned long long>(m_capacity));
			}
			WakeConsumer();
			continue;
		}
		if (bytes > contiguous) {
			const RecordHeader pad {contiguous, static_cast<uint16_t>(RecordOp::Pad), 0};
			std::memcpy(m_data.get() + index, &pad, sizeof(pad));
			m_head.store(head + contiguous, std::memory_order_seq_cst);
			WakeConsumer();
			continue;
		}
		return m_data.get() + index;
	}
}

void CommandRecorder::Publish(uint32_t bytes) {
	const auto head = m_head.load(std::memory_order_relaxed);
	m_head.store(head + bytes, std::memory_order_seq_cst);
	WakeConsumer();
}

void CommandRecorder::PushRecord(RecordOp op, const void* payload, uint32_t payload_size) {
	auto* slot = BeginRecord(op, payload_size);
	if (payload_size != 0) {
		std::memcpy(slot, payload, payload_size);
	}
	EndRecord(payload_size);
}

uint8_t* CommandRecorder::BeginRecord(RecordOp op, uint32_t max_payload) {
	// One producer per recorder: the ring is single-producer, and a second publisher would
	// interleave its reservation with this one and hand the record thread a half-written record.
	// The owner is the thread that drives this scheduler (GuestGpu for the renderer, the
	// presentation thread for the swapchain).
	const auto self = std::this_thread::get_id();
	if (m_records == 0 && m_open_slot == nullptr) {
		m_producer = self;
	}
	EXIT_IF(m_producer != self || m_open_slot != nullptr);
	uint32_t bytes = static_cast<uint32_t>(sizeof(RecordHeader)) + max_payload;
	bytes          = (bytes + RecordAlign - 1u) & ~(RecordAlign - 1u);
	// Invisible to the record thread until EndRecord moves the head past it.
	m_open_slot  = Reserve(bytes);
	m_open_bytes = bytes;
	m_open_op    = op;
	return m_open_slot + sizeof(RecordHeader);
}

void CommandRecorder::EndRecord(uint32_t payload_size) {
	EXIT_IF(m_open_slot == nullptr);
	uint32_t bytes = static_cast<uint32_t>(sizeof(RecordHeader)) + payload_size;
	bytes          = (bytes + RecordAlign - 1u) & ~(RecordAlign - 1u);
	EXIT_IF(bytes > m_open_bytes);
	const RecordHeader header {bytes, static_cast<uint16_t>(m_open_op), 0};
	std::memcpy(m_open_slot, &header, sizeof(header));
	const auto op = m_open_op;
	m_open_slot   = nullptr;
	m_records++;
	Publish(bytes);
	const auto backlog =
	    m_head.load(std::memory_order_relaxed) - m_tail.load(std::memory_order_acquire);
	if (backlog > m_peak_backlog) {
		m_peak_backlog = backlog;
	}
	namespace FS = Common::FrameStats;
	FS::Add(FS::Counter::RecordPackets, 1);
	FS::Add(FS::Counter::RecordBytes, bytes);
	if (op >= RecordOp::PassEnd) {
		FS::Add(FS::Counter::RecordPackBytes, bytes);
	}
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

void CommandRecorder::PushGeneric(Common::UniqueFunction<void, vk::CommandBuffer>&& command) {
	EXIT_IF(!command);
	// The callable outlives the record: the record thread invokes it and deletes it.
	const Payloads::Generic payload {
	    new Common::UniqueFunction<void, vk::CommandBuffer>(std::move(command))};
	PushRecord(RecordOp::Generic, &payload, sizeof(payload));
}

void CommandRecorder::PushPassEnd(bool end_pass, vk::PipelineStageFlags shader_write_stages) {
	const RecordPassEnd payload {end_pass ? 1u : 0u, static_cast<uint32_t>(shader_write_stages)};
	PushRecord(RecordOp::PassEnd, &payload, sizeof(payload));
}

void CommandRecorder::PushPassBegin(const RenderState& state) {
	PushRecord(RecordOp::PassBegin, &state, sizeof(state));
}

void CommandRecorder::PushBindings(vk::PipelineBindPoint bind_point, vk::PipelineLayout layout,
                                   vk::DescriptorSet set, vk::ShaderStageFlags push_stages,
                                   std::span<const uint32_t>                 push,
                                   std::span<const vk::WriteDescriptorSet>   writes,
                                   std::span<const vk::DescriptorBufferInfo> buffers,
                                   std::span<const vk::DescriptorImageInfo>  images) {
	const auto push_size   = static_cast<uint32_t>(push.size_bytes());
	const auto push_padded = (push_size + 7u) & ~7u;
	const auto size        = static_cast<uint32_t>(
        sizeof(RecordBindings) + push_padded + writes.size() * sizeof(RecordDescriptorWrite) +
        buffers.size_bytes() + images.size_bytes());
	auto*          out = BeginRecord(RecordOp::Bindings, size);
	RecordBindings head {};
	head.layout       = layout;
	head.set          = set;
	head.bind_point   = static_cast<uint32_t>(bind_point);
	head.push_stages  = push_size != 0 ? static_cast<uint32_t>(push_stages) : 0u;
	head.push_size    = push_size;
	head.write_count  = static_cast<uint32_t>(writes.size());
	head.buffer_count = static_cast<uint32_t>(buffers.size());
	head.image_count  = static_cast<uint32_t>(images.size());
	std::memcpy(out, &head, sizeof(head));
	auto* cursor = out + sizeof(head);
	if (push_size != 0) {
		std::memcpy(cursor, push.data(), push_size);
	}
	cursor += push_padded;
	for (const auto& write: writes) {
		EXIT_IF(write.pTexelBufferView != nullptr || write.dstArrayElement != 0);
		RecordDescriptorWrite entry {};
		entry.binding      = write.dstBinding;
		entry.type         = static_cast<uint32_t>(write.descriptorType);
		entry.count        = write.descriptorCount;
		entry.buffer_start = UINT32_MAX;
		entry.image_start  = UINT32_MAX;
		if (write.pBufferInfo != nullptr) {
			const auto start = write.pBufferInfo - buffers.data();
			EXIT_IF(start < 0 || static_cast<size_t>(start) + write.descriptorCount > buffers.size());
			entry.buffer_start = static_cast<uint32_t>(start);
		}
		if (write.pImageInfo != nullptr) {
			const auto start = write.pImageInfo - images.data();
			EXIT_IF(start < 0 || static_cast<size_t>(start) + write.descriptorCount > images.size());
			entry.image_start = static_cast<uint32_t>(start);
		}
		std::memcpy(cursor, &entry, sizeof(entry));
		cursor += sizeof(entry);
	}
	if (!buffers.empty()) {
		std::memcpy(cursor, buffers.data(), buffers.size_bytes());
	}
	cursor += buffers.size_bytes();
	if (!images.empty()) {
		std::memcpy(cursor, images.data(), images.size_bytes());
	}
	EndRecord(size);
	Common::FrameStats::Add(Common::FrameStats::Counter::RecordPackBinds, 1);
}

void RecordCommandWriter::Commit(bool dispatch) {
	EXIT_IF(m_data == nullptr);
	const uint32_t stream = m_used - 8u;
	if (stream == 0) {
		m_recorder.AbandonRecord();
		m_data = nullptr;
		return;
	}
	const uint32_t words[2] {stream, 0u};
	std::memcpy(m_data, words, sizeof(words));
	m_data = nullptr;
	m_recorder.EndRecord(m_used);
	namespace FS = Common::FrameStats;
	FS::Add(dispatch ? FS::Counter::RecordPackDispatches : FS::Counter::RecordPackDraws, 1);
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
	// A short spin first: an awake record thread finishes the records of a draw well within it,
	// and the condition variable below costs two thread switches.
	bool       done    = false;
	const auto spin_ns = std::min<uint64_t>(SpinNs(), 100'000u);
	if (spin_ns != 0) {
		const auto start      = FS::NowNs();
		const auto max_rounds = spin_ns / 256u + 1u;
		for (uint64_t round = 0; round < max_rounds && !done; round++) {
			for (int i = 0; i < 64; i++) {
				if (m_tail.load(std::memory_order_acquire) >= target) {
					done = true;
					break;
				}
				CpuPause();
			}
			if (!done && FS::NowNs() - start >= spin_ns) {
				break;
			}
		}
	}
	if (!done) {
		std::unique_lock lock(m_mutex);
		// Dekker handshake with WakeWaiters: the waiter count is visible before this last look at
		// the tail, and the record thread looks at the count after it moved the tail; it notifies
		// under the mutex, which this thread releases only inside the wait.
		m_waiters.fetch_add(1, std::memory_order_seq_cst);
		while (m_tail.load(std::memory_order_seq_cst) < target) {
			m_progress.wait_for(lock, WaitSlice);
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
			// Impossible state: a timestamp without a query pool used to mean a GPU-time mark,
			// which is published in the middle of a command buffer. Recording it here put a
			// second thread inside the same VkCommandBuffer.
			EXIT_IF(mark.pool == nullptr);
			if (mark.pool != nullptr) {
				if (mark.reset != 0) {
					m_buffer.resetQueryPool(mark.pool, mark.query, mark.reset);
				}
				m_buffer.writeTimestamp(mark.bottom != 0 ? vk::PipelineStageFlagBits::eBottomOfPipe
				                                         : vk::PipelineStageFlagBits::eTopOfPipe,
				                        mark.pool, mark.query);
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
		case RecordOp::PassEnd: {
			RecordPassEnd end {};
			std::memcpy(&end, payload, sizeof(end));
			EXIT_IF(m_buffer == nullptr);
			if (end.end_pass != 0) {
				m_buffer.endRendering();
			}
			if (end.shader_write_stages != 0) {
				ShaderWriteBarrier(m_buffer, vk::PipelineStageFlags(end.shader_write_stages));
			}
			break;
		}
		case RecordOp::PassBegin: {
			RenderState state;
			std::memcpy(&state, payload, sizeof(state));
			EXIT_IF(m_buffer == nullptr);
			RecordBeginRendering(m_buffer, state);
			break;
		}
		case RecordOp::Bindings: ExecuteBindings(payload); break;
		case RecordOp::Commands: ExecuteCommands(payload); break;
	}
}

void CommandRecorder::ExecuteBindings(const uint8_t* payload) {
	EXIT_IF(m_buffer == nullptr);
	RecordBindings head {};
	std::memcpy(&head, payload, sizeof(head));
	auto*      cursor     = payload + sizeof(head);
	const auto bind_point = static_cast<vk::PipelineBindPoint>(head.bind_point);
	if (head.push_size != 0) {
		m_buffer.pushConstants(head.layout, vk::ShaderStageFlags(head.push_stages), 0, head.push_size,
		                       cursor);
	}
	cursor += (head.push_size + 7u) & ~7u;
	const auto* entries = cursor;
	cursor += head.write_count * sizeof(RecordDescriptorWrite);
	// 8-aligned in the arena: records start on 16 and every section is padded to 8.
	const auto* buffers = reinterpret_cast<const vk::DescriptorBufferInfo*>(cursor);
	cursor += head.buffer_count * sizeof(vk::DescriptorBufferInfo);
	const auto* images = reinterpret_cast<const vk::DescriptorImageInfo*>(cursor);
	if (head.write_count == 0) {
		return;
	}
	m_writes.resize(head.write_count);
	for (uint32_t i = 0; i < head.write_count; i++) {
		RecordDescriptorWrite entry {};
		std::memcpy(&entry, entries + i * sizeof(entry), sizeof(entry));
		auto& write           = m_writes[i];
		write                 = vk::WriteDescriptorSet {};
		write.dstSet          = head.set;
		write.dstBinding      = entry.binding;
		write.descriptorCount = entry.count;
		write.descriptorType  = static_cast<vk::DescriptorType>(entry.type);
		write.pBufferInfo     = entry.buffer_start != UINT32_MAX ? buffers + entry.buffer_start : nullptr;
		write.pImageInfo      = entry.image_start != UINT32_MAX ? images + entry.image_start : nullptr;
	}
	if (head.set == nullptr) {
		m_buffer.pushDescriptorSetKHR(bind_point, head.layout, 0, head.write_count, m_writes.data());
	} else {
		// The set was handed out for the tick of this buffer (DescriptorHeap), so no other update
		// of it can run until this buffer has been recorded, submitted and completed.
		m_device.updateDescriptorSets(head.write_count, m_writes.data(), 0, nullptr);
		m_buffer.bindDescriptorSets(bind_point, head.layout, 0, 1, &head.set, 0, nullptr);
	}
}

void CommandRecorder::ExecuteCommands(const uint8_t* payload) {
	EXIT_IF(m_buffer == nullptr);
	uint32_t stream = 0;
	std::memcpy(&stream, payload, sizeof(stream));
	const auto* begin  = payload + 8;
	uint32_t    offset = 0;
	while (offset < stream) {
		RecordCmdHeader command {};
		std::memcpy(&command, begin + offset, sizeof(command));
		const auto* data = begin + offset + sizeof(command);
		const auto  aux  = command.aux;
		offset += static_cast<uint32_t>(sizeof(command)) + ((command.size + 7u) & ~7u);
		switch (static_cast<RecordCmd>(command.cmd)) {
			case RecordCmd::BindVertexBuffers:
				m_buffer.bindVertexBuffers(0, aux, reinterpret_cast<const vk::Buffer*>(data),
				                           reinterpret_cast<const vk::DeviceSize*>(data + aux * 8u));
				break;
			case RecordCmd::BindIndexBuffer: {
				vk::Buffer     buffer;
				vk::DeviceSize index_offset = 0;
				std::memcpy(&buffer, data, sizeof(buffer));
				std::memcpy(&index_offset, data + 8, sizeof(index_offset));
				m_buffer.bindIndexBuffer(buffer, index_offset, static_cast<vk::IndexType>(aux));
				break;
			}
			case RecordCmd::SetViewports:
				m_buffer.setViewportWithCount(aux, reinterpret_cast<const vk::Viewport*>(data));
				break;
			case RecordCmd::SetScissors:
				m_buffer.setScissorWithCount(aux, reinterpret_cast<const vk::Rect2D*>(data));
				break;
			case RecordCmd::SetLineWidth: {
				float width = 1.0f;
				std::memcpy(&width, data, sizeof(width));
				m_buffer.setLineWidth(width);
				break;
			}
			case RecordCmd::SetBlendConstants: {
				float constants[4] {};
				std::memcpy(constants, data, sizeof(constants));
				m_buffer.setBlendConstants(constants);
				break;
			}
			case RecordCmd::SetDepthTestEnable: m_buffer.setDepthTestEnable(aux); break;
			case RecordCmd::SetDepthWriteEnable: m_buffer.setDepthWriteEnable(aux); break;
			case RecordCmd::SetDepthCompareOp:
				m_buffer.setDepthCompareOp(static_cast<vk::CompareOp>(aux));
				break;
			case RecordCmd::SetDepthBiasEnable: m_buffer.setDepthBiasEnable(aux); break;
			case RecordCmd::SetDepthBias: {
				float values[3] {};
				std::memcpy(values, data, sizeof(values));
				m_buffer.setDepthBias(values[0], values[1], values[2]);
				break;
			}
			case RecordCmd::SetStencilCompareMask:
			case RecordCmd::SetStencilWriteMask:
			case RecordCmd::SetStencilReference: {
				uint32_t value = 0;
				std::memcpy(&value, data, sizeof(value));
				const auto face = vk::StencilFaceFlags(aux);
				if (static_cast<RecordCmd>(command.cmd) == RecordCmd::SetStencilCompareMask) {
					m_buffer.setStencilCompareMask(face, value);
				} else if (static_cast<RecordCmd>(command.cmd) == RecordCmd::SetStencilWriteMask) {
					m_buffer.setStencilWriteMask(face, value);
				} else {
					m_buffer.setStencilReference(face, value);
				}
				break;
			}
			case RecordCmd::SetColorWriteEnable:
				m_buffer.setColorWriteEnableEXT(aux, reinterpret_cast<const vk::Bool32*>(data));
				break;
			case RecordCmd::SetFeedbackLoop:
				m_buffer.setAttachmentFeedbackLoopEnableEXT(vk::ImageAspectFlags(aux));
				break;
			case RecordCmd::BindPipeline: {
				vk::Pipeline pipeline;
				std::memcpy(&pipeline, data, sizeof(pipeline));
				m_buffer.bindPipeline(static_cast<vk::PipelineBindPoint>(aux), pipeline);
				break;
			}
			case RecordCmd::PushConstants: {
				vk::PipelineLayout layout;
				uint32_t           push_offset = 0;
				uint32_t           push_size   = 0;
				std::memcpy(&layout, data, sizeof(layout));
				std::memcpy(&push_offset, data + 8, sizeof(push_offset));
				std::memcpy(&push_size, data + 12, sizeof(push_size));
				m_buffer.pushConstants(layout, vk::ShaderStageFlags(aux), push_offset, push_size,
				                       data + 16);
				break;
			}
			case RecordCmd::Draw: {
				uint32_t values[4] {};
				std::memcpy(values, data, sizeof(values));
				m_buffer.draw(values[0], values[1], values[2], values[3]);
				break;
			}
			case RecordCmd::DrawIndexed: {
				uint32_t values[5] {};
				std::memcpy(values, data, sizeof(values));
				m_buffer.drawIndexed(values[0], values[1], values[2], static_cast<int32_t>(values[3]),
				                     values[4]);
				break;
			}
			case RecordCmd::DrawIndirect:
			case RecordCmd::DrawIndexedIndirect: {
				vk::Buffer     buffer;
				vk::DeviceSize args_offset = 0;
				uint32_t       count       = 0;
				uint32_t       stride      = 0;
				std::memcpy(&buffer, data, sizeof(buffer));
				std::memcpy(&args_offset, data + 8, sizeof(args_offset));
				std::memcpy(&count, data + 16, sizeof(count));
				std::memcpy(&stride, data + 20, sizeof(stride));
				if (static_cast<RecordCmd>(command.cmd) == RecordCmd::DrawIndirect) {
					m_buffer.drawIndirect(buffer, args_offset, count, stride);
				} else {
					m_buffer.drawIndexedIndirect(buffer, args_offset, count, stride);
				}
				break;
			}
			case RecordCmd::DrawMeshTasks:
			case RecordCmd::Dispatch: {
				uint32_t values[3] {};
				std::memcpy(values, data, sizeof(values));
				if (static_cast<RecordCmd>(command.cmd) == RecordCmd::DrawMeshTasks) {
					m_buffer.drawMeshTasksEXT(values[0], values[1], values[2]);
				} else {
					m_buffer.dispatch(values[0], values[1], values[2]);
				}
				break;
			}
			case RecordCmd::DispatchIndirect: {
				vk::Buffer     buffer;
				vk::DeviceSize args_offset = 0;
				std::memcpy(&buffer, data, sizeof(buffer));
				std::memcpy(&args_offset, data + 8, sizeof(args_offset));
				m_buffer.dispatchIndirect(buffer, args_offset);
				break;
			}
			case RecordCmd::ShaderWriteBarrierLocal:
				ShaderWriteBarrierLocal(m_buffer, vk::PipelineStageFlags(aux));
				break;
			case RecordCmd::ShaderWriteHazardBarrier:
				ShaderWriteHazardBarrier(m_buffer, vk::PipelineStageFlags(aux));
				break;
			case RecordCmd::ShaderAccessBarrier:
				ShaderAccessBarrier(m_buffer, vk::PipelineStageFlags(aux));
				break;
			default: EXIT("RecordThread: unknown command %u\n", static_cast<uint32_t>(command.cmd));
		}
	}
}

// Polls the head for up to "recspin" microseconds; true when work (or a stop) arrived.
bool CommandRecorder::SpinFor(uint64_t tail) {
	const auto spin_ns = SpinNs();
	if (spin_ns == 0) {
		return false;
	}
	namespace FS          = Common::FrameStats;
	const auto start      = FS::NowNs();
	const auto max_rounds = spin_ns / 256u + 1u;
	bool       arrived    = false;
	for (uint64_t round = 0; round < max_rounds && !arrived; round++) {
		for (int i = 0; i < 64; i++) {
			if (m_head.load(std::memory_order_acquire) != tail ||
			    m_stop.load(std::memory_order_acquire)) {
				arrived = true;
				break;
			}
			CpuPause();
		}
		if (!arrived && FS::NowNs() - start >= spin_ns) {
			break;
		}
	}
	FS::Add(FS::Counter::RecordSpinNs, FS::NowNs() - start);
	return arrived;
}

void CommandRecorder::Loop() {
	Common::FrameStats::RegisterCurrentThread(Common::FrameStats::ThreadRole::Record);
	for (;;) {
		const auto tail = m_tail.load(std::memory_order_relaxed);
		if (m_head.load(std::memory_order_acquire) == tail) {
			if (m_stop.load(std::memory_order_acquire)) {
				return;
			}
			if (SpinFor(tail)) {
				continue;
			}
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			{
				std::unique_lock lock(m_mutex);
				// Dekker handshake with Publish: this flag is visible before the last look at the
				// head, and Publish looks at the flag after it moved the head, both sequentially
				// consistent, so at least one of the two sees the other. Publish notifies under the
				// mutex, which this thread releases only inside the wait: no notify is lost.
				m_consumer_waiting.store(true, std::memory_order_seq_cst);
				while (!m_stop.load(std::memory_order_acquire) &&
				       m_head.load(std::memory_order_seq_cst) == tail) {
					m_pending.wait_for(lock, SleepSlice);
				}
				m_consumer_waiting.store(false, std::memory_order_seq_cst);
			}
			FS::Add(FS::Counter::RecordSleeps, 1);
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
		m_tail.store(tail + header.size, std::memory_order_seq_cst);
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
	// Gate "recordthread": KYTY_RECORD_THREAD gives the start value and the gate file moves it. It
	// is read once per native command buffer (CommandScheduler::BeginCommand), the only point where
	// the command pool and the handle change owner: switching off drains the record thread before
	// the resolving thread takes a buffer from the pool itself, switching on hands the next
	// BeginBuffer to the record thread. Nothing else touches the pool; the GPU-time chunk begins
	// through Handle() after BeginRecorded (a drain), and the frame-trace timestamps follow the
	// choice of their own buffer (BeginTimestamp / EndTimestamp).
	static const bool logged = [] {
		LOGF("RecordThread: KYTY_RECORD_THREAD=%d at start; recordthread= in the gate file moves it "
		     "at the next command buffer\n",
		     Common::Gates::Enabled(Common::Gates::Gate::RecordThread) ? 1 : 0);
		return true;
	}();
	(void)logged;
	if (!Common::Gates::Enabled(Common::Gates::Gate::RecordThread)) {
		return false;
	}
	if (graphics.gpu_breadcrumbs_enabled || graphics.diagnostic_checkpoints_enabled) {
		return false;
	}
	if (RenderDocCapturing()) {
		return false;
	}
	return true;
}

} // namespace Libs::Graphics
