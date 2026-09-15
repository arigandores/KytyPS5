#include "graphics/host_gpu/renderer/commandRecorder.h"

#include "common/assert.h"
#include "common/frameStats.h"
#include "common/gates.h"
#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
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

#if defined(_WIN32)
// processthreadsapi.h (gate "recrelax"), declared here so this file does not include <windows.h>.
extern "C" __declspec(dllimport) void __stdcall FlushProcessWriteBuffers(void);
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

// Gate "recbatch" (session 57, A4): the pass and bindings records of a draw are staged and
// published with its Commands record - one head store per draw instead of about 2.2. Read per
// record; flipping it at any point is safe, since every publish makes all staged records visible.
bool BatchWanted() noexcept {
	return Common::Gates::Enabled(Common::Gates::Gate::RecordBatch);
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
	// Before the thread starts, so the record thread reads it without a race. The scheduler creates
	// its recorder lazily in BeginCommand, on the thread that owns the scheduler.
	m_gpu   = Common::FrameStats::CurrentRole() == Common::FrameStats::ThreadRole::Gpu;
	m_stats = Common::FrameStats::Enabled();
	// The thread first, the registry after: DrainRecordQueues() reads m_thread through Drain(),
	// and it may run on another thread as soon as this recorder is in the list. Nothing can be
	// owed to an unregistered recorder - only its owner publishes, and it has no pointer yet.
	m_thread = std::thread([this] { Loop(); });
	{
		std::lock_guard lock(RecordersMutex());
		Recorders().push_back(this);
	}
	LOGF("RecordThread: started recorder=%p arena=%lluKiB gpu=%d\n", static_cast<void*>(this),
	     static_cast<unsigned long long>(m_capacity / 1024u), m_gpu ? 1 : 0);
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
	// From the destructor: the producer is done, and what it staged (gate "recbatch") is published so
	// the drain below records it.
	PublishStaged();
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
	Common::FrameStats::Add(Common::FrameStats::Counter::RecordTailReads, 1);
	return static_cast<size_t>(head - tail);
}

void CommandRecorder::WakeConsumer() {
	if (m_consumer_waiting.load(std::memory_order_seq_cst)) {
		Common::FrameStats::Add(Common::FrameStats::Counter::RecordWakes, 1);
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
		// This thread's own head: every ended record, published or staged. The shared m_head line is
		// only ever written by this thread, never read by it.
		const auto head       = m_head_local;
		const auto index      = static_cast<uint32_t>(head & m_mask);
		const auto contiguous = static_cast<uint32_t>(m_capacity - index);
		// A record never straddles the end of the ring: when it does not fit, a Pad record fills
		// the remainder and the reservation restarts at offset 0.
		const auto want = bytes <= contiguous ? bytes : contiguous + bytes;
		// m_tail_seen is a tail this thread read before. The tail only grows, so the free space
		// computed from it is a lower bound; the record thread's line is read only when that bound is
		// not enough. Staged records and Pad bytes are part of head, so they count as used.
		namespace FS = Common::FrameStats;
		if (m_capacity - (head - m_tail_seen) < want) {
			m_tail_seen = m_tail.load(std::memory_order_acquire);
			FS::Add(FS::Counter::RecordTailReads, 1);
		}
		if (m_capacity - (head - m_tail_seen) < want) {
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			// The record thread frees only what it can see: a wait over staged records (gate
			// "recbatch") would never end. After this, head is the published head.
			PublishStaged();
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
			m_tail_seen = m_tail.load(std::memory_order_acquire);
			FS::Add(FS::Counter::RecordTailReads, 1);
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
			// Published at once, together with any staged records before it.
			m_head_local = head + contiguous;
			Publish();
			continue;
		}
		return m_data.get() + index;
	}
}

void CommandRecorder::Publish() {
	m_published     = m_head_local;
	m_since_publish = 0;
	// Dekker handshake with Loop, which stores its flag and then looks at the head: this stores the
	// head and then looks at the flag. Gate "recrelax" off: a sequentially consistent store (xchg
	// on x64). On: a plain store, which does not hold up retirement while the spinning record thread
	// owns the line; it may still sit in this processor's store buffer when the flag is read, so
	// Loop calls FlushProcessWriteBuffers between its flag store and its last look at the head once
	// m_relaxed_ever is set. That flag is stored sequentially consistent before the first relaxed
	// store: if Loop reads it false, every relaxed store comes after Loop's flag store, and the look
	// at the flag below sees it. Flipping the gate stays safe at any moment.
#if defined(_WIN32)
	// The GuestGpu recorder only: the presentation recorder sleeps on every present, and an
	// m_relaxed_ever set there would cost an IPI round per present.
	if (m_gpu && Common::Gates::Enabled(Common::Gates::Gate::RecordRelaxed)) {
		if (!m_relaxed_ever.load(std::memory_order_relaxed)) {
			m_relaxed_ever.store(true, std::memory_order_seq_cst);
		}
		m_head.store(m_published, std::memory_order_relaxed);
	} else {
		m_head.store(m_published, std::memory_order_seq_cst);
	}
#else
	m_head.store(m_published, std::memory_order_seq_cst);
#endif
	Common::FrameStats::Add(Common::FrameStats::Counter::RecordPublishes, 1);
	WakeConsumer();
}

void CommandRecorder::PublishStaged() {
	if (m_published != m_head_local) {
		static const bool record_check = [] {
			const auto* value = std::getenv("KYTY_RECORD_CHECK");
			return value != nullptr && value[0] == '1';
		}();
		// Producer fields: a publish from another thread could move m_head back under the tail.
		EXIT_IF(record_check && m_producer != std::this_thread::get_id());
		Common::FrameStats::Add(Common::FrameStats::Counter::RecordForcedPublishes, 1);
		Publish();
	}
}

void CommandRecorder::PushRecord(RecordOp op, const void* payload, uint32_t payload_size,
                                 bool publish) {
	auto* slot = BeginRecord(op, payload_size);
	if (payload_size != 0) {
		std::memcpy(slot, payload, payload_size);
	}
	EndRecord(payload_size, publish);
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

void CommandRecorder::EndRecord(uint32_t payload_size, bool publish) {
	EXIT_IF(m_open_slot == nullptr);
	uint32_t bytes = static_cast<uint32_t>(sizeof(RecordHeader)) + payload_size;
	bytes          = (bytes + RecordAlign - 1u) & ~(RecordAlign - 1u);
	EXIT_IF(bytes > m_open_bytes);
	const RecordHeader header {bytes, static_cast<uint16_t>(m_open_op), 0};
	std::memcpy(m_open_slot, &header, sizeof(header));
	const auto op = m_open_op;
	m_open_slot   = nullptr;
	m_records++;
	// Visible to the record thread once m_head moves past it: now, or at the next publish (gate
	// "recbatch"). No tail read here: the record thread measures the backlog peak itself.
	m_head_local += bytes;
	namespace FS = Common::FrameStats;
	FS::Add(FS::Counter::RecordPackets, 1);
	FS::Add(FS::Counter::RecordBytes, bytes);
	if (op >= RecordOp::PassEnd) {
		FS::Add(FS::Counter::RecordPackBytes, bytes);
		if (publish) {
			// Knob "recpubn" (session 61): the head store is an xchg on the line the spinning
			// record thread reads, from the other CCD most of the time - 4.6 % of the GuestGpu
			// thread at that one instruction in Sky Garden, ~10.6k publishes a frame. Publish the
			// draw stream at most every N records; the record thread is idle most of the frame,
			// and everything that needs the records visible now publishes the staged tail itself,
			// exactly as with gate "recbatch": a direct Handle() before its drain, a submit
			// (EndBuffer is not a draw-stream record and is never throttled), a wait for ring
			// space, Stop. Records below PassEnd are not throttled either.
			const auto every = Common::Gates::Value(Common::Gates::Knob::RecordPublishEvery);
			if (every > 1u && ++m_since_publish < every) {
				publish = false;
				FS::Add(FS::Counter::RecordThrottled, 1); // counted in rec_staged as well
			}
		}
	}
	if (publish) {
		Publish();
	} else {
		FS::Add(FS::Counter::RecordStaged, 1);
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

void CommandRecorder::PushImageBarriers(std::span<const vk::ImageMemoryBarrier2> barriers) {
	EXIT_IF(barriers.empty());
	const auto bytes = static_cast<uint32_t>(barriers.size_bytes());
	auto*      out   = BeginRecord(RecordOp::ImageBarriers, 8u + bytes);
	const uint32_t head[2] {static_cast<uint32_t>(barriers.size()), 0u};
	std::memcpy(out, head, sizeof(head));
	std::memcpy(out + 8, barriers.data(), bytes);
	EndRecord(8u + bytes, !BatchWanted());
}

void CommandRecorder::PushBufferUpload(vk::Buffer source, vk::Buffer destination,
                                       uint64_t                        destination_size,
                                       std::span<const vk::BufferCopy> copies) {
	EXIT_IF(copies.empty() || source == nullptr || destination == nullptr);
	const auto bytes = static_cast<uint32_t>(copies.size_bytes());
	auto* out = BeginRecord(RecordOp::BufferUpload, static_cast<uint32_t>(sizeof(RecordBufferUpload)) + bytes);
	RecordBufferUpload head {};
	head.source           = source;
	head.destination      = destination;
	head.destination_size = destination_size;
	head.count            = static_cast<uint32_t>(copies.size());
	std::memcpy(out, &head, sizeof(head));
	std::memcpy(out + sizeof(head), copies.data(), bytes);
	EndRecord(static_cast<uint32_t>(sizeof(RecordBufferUpload)) + bytes, !BatchWanted());
}

void CommandRecorder::PushPassEnd(bool end_pass, vk::PipelineStageFlags shader_write_stages) {
	const RecordPassEnd payload {end_pass ? 1u : 0u, static_cast<uint32_t>(shader_write_stages)};
	PushRecord(RecordOp::PassEnd, &payload, sizeof(payload), !BatchWanted());
}

void CommandRecorder::PushPassBegin(const RenderState& state) {
	PushRecord(RecordOp::PassBegin, &state, sizeof(state), !BatchWanted());
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
	EndRecord(size, !BatchWanted());
	Common::FrameStats::Add(Common::FrameStats::Counter::RecordPackBinds, 1);
}

void RecordCommandWriter::Commit(bool dispatch) {
	EXIT_IF(m_data == nullptr);
	const uint32_t stream = m_used - 8u;
	if (stream == 0) {
		m_recorder.AbandonRecord();
		m_data = nullptr;
		// No record of this draw to carry the staged ones (gate "recbatch").
		m_recorder.PublishStaged();
		return;
	}
	const uint32_t words[2] {stream, 0u};
	std::memcpy(m_data, words, sizeof(words));
	m_data = nullptr;
	// Published (unless knob "recpubn" stages it too): with gate "recbatch" this carries the draw's
	// staged pass and bindings records; a staged tail is published by Handle(), a submit, Reserve
	// or Stop.
	m_recorder.EndRecord(m_used, true);
	namespace FS = Common::FrameStats;
	FS::Add(dispatch ? FS::Counter::RecordPackDispatches : FS::Counter::RecordPackDraws, 1);
}

void CommandRecorder::Drain() {
	EXIT_IF(std::this_thread::get_id() == m_thread.get_id());
	if (m_producer == std::this_thread::get_id()) {
		// A drain by the producer means "everything recorded so far": what it staged (gate
		// "recbatch", knob "recpubn") is part of that. Another thread cannot publish and waits
		// for the published head only - what is staged belongs to a buffer not yet ended.
		PublishStaged();
	}
	namespace FS      = Common::FrameStats;
	const auto target = m_head.load(std::memory_order_acquire);
	FS::Add(FS::Counter::RecordTailReads, 1);
	if (m_tail.load(std::memory_order_acquire) >= target) {
		return;
	}
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
		FS::Add(FS::Counter::RecordDrainLocks, 1);
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
		case RecordOp::ImageBarriers: {
			EXIT_IF(m_buffer == nullptr);
			uint32_t count = 0;
			std::memcpy(&count, payload, sizeof(count));
			// 16-aligned record, 8 bytes of header: the array is 8-aligned in place.
			vk::DependencyInfo dependency {};
			dependency.imageMemoryBarrierCount = count;
			dependency.pImageMemoryBarriers =
			    reinterpret_cast<const vk::ImageMemoryBarrier2*>(payload + 8);
			m_buffer.pipelineBarrier2(dependency);
			break;
		}
		case RecordOp::BufferUpload: {
			EXIT_IF(m_buffer == nullptr);
			RecordBufferUpload upload {};
			std::memcpy(&upload, payload, sizeof(upload));
			const auto* copies =
			    reinterpret_cast<const vk::BufferCopy*>(payload + sizeof(RecordBufferUpload));
			vk::BufferMemoryBarrier before {};
			before.srcAccessMask = vk::AccessFlagBits::eMemoryRead |
			                       vk::AccessFlagBits::eMemoryWrite |
			                       vk::AccessFlagBits::eTransferRead |
			                       vk::AccessFlagBits::eTransferWrite;
			before.dstAccessMask       = vk::AccessFlagBits::eTransferWrite;
			before.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
			before.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
			before.buffer              = upload.destination;
			before.offset              = 0;
			before.size                = upload.destination_size;
			m_buffer.pipelineBarrier(vk::PipelineStageFlagBits::eAllCommands,
			                         vk::PipelineStageFlagBits::eTransfer,
			                         vk::DependencyFlagBits::eByRegion, 0, nullptr, 1, &before, 0,
			                         nullptr);
			m_buffer.copyBuffer(upload.source, upload.destination, upload.count, copies);
			auto after          = before;
			after.srcAccessMask = vk::AccessFlagBits::eTransferWrite;
			after.dstAccessMask = vk::AccessFlagBits::eMemoryRead | vk::AccessFlagBits::eMemoryWrite;
			m_buffer.pipelineBarrier(vk::PipelineStageFlagBits::eTransfer,
			                         vk::PipelineStageFlagBits::eAllCommands,
			                         vk::DependencyFlagBits::eByRegion, 0, nullptr, 1, &after, 0,
			                         nullptr);
			break;
		}
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
			case RecordCmd::BindVertexBuffers2:
				m_buffer.bindVertexBuffers2(
				    0, aux, reinterpret_cast<const vk::Buffer*>(data),
				    reinterpret_cast<const vk::DeviceSize*>(data + aux * 8u),
				    reinterpret_cast<const vk::DeviceSize*>(data + aux * 16u), nullptr);
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
			case RecordCmd::SetStencilTestEnable: m_buffer.setStencilTestEnable(aux); break;
			case RecordCmd::SetStencilOp: {
				uint32_t values[4] {};
				std::memcpy(values, data, sizeof(values));
				m_buffer.setStencilOp(vk::StencilFaceFlags(aux),
				                      static_cast<vk::StencilOp>(values[0]),
				                      static_cast<vk::StencilOp>(values[1]),
				                      static_cast<vk::StencilOp>(values[2]),
				                      static_cast<vk::CompareOp>(values[3]));
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
	const auto spun = FS::NowNs() - start;
	FS::Add(FS::Counter::RecordSpinNs, spun);
	if (m_gpu) {
		FS::Add(FS::Counter::RecordSpinNsGpu, spun);
	}
	return arrived;
}

void CommandRecorder::Loop() {
	Common::FrameStats::RegisterCurrentThread(Common::FrameStats::ThreadRole::Record);
	// m_data and m_mask never change after the constructor: local copies keep this loop off the
	// line of the fields around them.
	const auto* const data = m_data.get();
	const auto        mask = m_mask;
	for (;;) {
		const auto tail = m_tail.load(std::memory_order_relaxed);
		const auto head = m_head.load(std::memory_order_acquire);
		if (head == tail) {
			if (m_stop.load(std::memory_order_acquire)) {
				return;
			}
			if (SpinFor(tail)) {
				continue;
			}
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			{
				// Dekker handshake with Publish: this flag is visible before the last look at the
				// head, and Publish looks at the flag after it moved the head, both sequentially
				// consistent, so at least one of the two sees the other. Publish notifies under the
				// mutex, which this thread releases only inside the wait: no notify is lost. The flag
				// store and the flush precede the lock: a publisher that saw the flag takes the
				// mutex (draining its store buffer) before it notifies.
				m_consumer_waiting.store(true, std::memory_order_seq_cst);
#if defined(_WIN32)
				// Gate "recrelax": Publish may store the head without a lock prefix, and that store may
				// still sit in the publisher's store buffer while it reads the flag. The IPI makes every
				// processor of the process commit the stores it has retired and re-execute what it has
				// not, so the look below sees the head, or the publisher's look at the flag comes after
				// the store above. Only once the producer has used the gate (m_relaxed_ever, see
				// Publish): an IPI round to every processor per sleep is not free.
				if (m_relaxed_ever.load(std::memory_order_seq_cst)) {
					FlushProcessWriteBuffers();
					FS::Add(FS::Counter::RecordFlushBuffers, 1);
				}
#endif
				std::unique_lock lock(m_mutex);
				while (!m_stop.load(std::memory_order_acquire) &&
				       m_head.load(std::memory_order_seq_cst) == tail) {
					m_pending.wait_for(lock, SleepSlice);
				}
				m_consumer_waiting.store(false, std::memory_order_seq_cst);
			}
			FS::Add(FS::Counter::RecordSleeps, 1);
			if (m_gpu) {
				FS::Add(FS::Counter::RecordSleepsGpu, 1);
			}
			if (t0 != 0) {
				FS::Add(FS::Counter::RecordIdleNs, FS::NowNs() - t0);
			}
			continue;
		}
		if (head - tail > m_peak_backlog) {
			m_peak_backlog = head - tail;
		}
		const auto   index = static_cast<uint32_t>(tail & mask);
		RecordHeader header {};
		std::memcpy(&header, data + index, sizeof(header));
		EXIT_IF(header.size < sizeof(RecordHeader));
		if (m_gpu) {
			namespace FS = Common::FrameStats;
			if (static_cast<RecordOp>(header.op) == RecordOp::BeginBuffer) {
				// Gate "recpin", once per native command buffer: a thread-local compare when nothing
				// changed, back to the process mask when the gate went off.
				DrawAheadApplyRecordPin(Common::Gates::Enabled(Common::Gates::Gate::RecordPin));
			}
			if (m_stats && (++m_ccd_tick & 255u) == 0) {
				// The GuestGpu thread's group is known only while M1 queues work (gate "drawahead").
				FS::Add(FS::Counter::RecordCcdChecks, 1);
				const auto gpu_l3 = DrawAheadGpuL3();
				if (gpu_l3 != 0xffu && DrawAheadCurrentL3() != gpu_l3) {
					FS::Add(FS::Counter::RecordCrossCcd, 1);
				}
			}
		}
		{
			namespace FS  = Common::FrameStats;
			const auto t0 = FS::TimingsEnabled() ? FS::NowNs() : 0;
			Execute(header, data + index + sizeof(RecordHeader));
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
