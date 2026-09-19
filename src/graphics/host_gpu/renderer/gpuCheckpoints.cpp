#include "graphics/host_gpu/renderer/gpuCheckpoints.h"

#include "common/logging/log.h"
#include "graphics/host_gpu/graphicContext.h"
#include "graphics/host_gpu/renderer/cache/streamBuffer.h"
#include "graphics/host_gpu/renderer/commandScheduler.h"

#include "common/frameStats.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cinttypes>
#include <cstdarg>
#include <cstdio>
#include <map>
#include <memory>
#include <string>
#include <thread>
#include <utility>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <mutex>

namespace Libs::Graphics {

namespace {

struct CheckpointRecord {
	uint64_t sequence  = 0;
	uint64_t submit_id = 0;
	uint64_t arg4      = 0;
	uint64_t arg5      = 0;
	uint32_t op        = 0;
	uint32_t arg0      = 0;
	uint32_t arg1      = 0;
	uint32_t arg2      = 0;
	uint32_t arg3      = 0;
};

// NV checkpoint markers must stay valid until the queue is inspected after a device loss.
constexpr size_t RingSize = size_t {1} << 17;

std::array<CheckpointRecord, RingSize> g_ring {};
std::atomic<uint64_t>                  g_sequence {0};
std::mutex                             g_ring_mutex;

const bool g_queue_trace_enabled = [] {
	const auto* value = std::getenv("KYTY_QUEUE_TRACE");
	return value != nullptr && value[0] != '0';
}();
// Session 98 (patch_s98b): KYTY_QUEUE_TRACE=2 - also the CPU op ring and GpuSubmitOps lines.
const bool g_queue_trace_ops = [] {
	const auto* value = std::getenv("KYTY_QUEUE_TRACE");
	return value != nullptr && value[0] == '2';
}();
const bool g_markers_requested = [] {
	const auto* value = std::getenv("KYTY_GPU_MARKERS");
	return value != nullptr && value[0] != '\0' && value[0] != '0';
}();
bool g_markers_enabled = false;
// Session 98 (patch_s98c): KYTY_GPU_MARKERS=2 - also the pre[] marker (BOTTOM_OF_PIPE before the op).
const bool g_markers_pre = [] {
	const auto* value = std::getenv("KYTY_GPU_MARKERS");
	return value != nullptr && value[0] == '2';
}();

// Defined below (the op ring); used by ReportGpuSubmissionHistory for KYTY_QUEUE_TRACE=2.
// KYTY_QUEUE_TRACE=2: (scheduler, tick) -> [first, last] seq.  Session 98 (patch_s98d): a LOCAL of
// ReportGpuSubmissionHistory (two threads can time out and report at once).
using SubmitOpsIndex = std::map<std::pair<const void*, uint64_t>, std::pair<uint32_t, uint32_t>>;
void PrintSubmitOps(const SubmitOpsIndex& index, const void* scheduler, uint64_t submit_seq,
                    uint64_t tick);
void BuildSubmitOpsIndex(SubmitOpsIndex& index);
struct SubmissionRecord {
	uint64_t sequence = 0;
	const void* scheduler = nullptr;
	vk::Semaphore master;
	uint64_t tick = 0;
	SubmitInfo submit;
	bool returned = false;
	vk::Result result = vk::Result::eNotReady;
};
std::array<SubmissionRecord, 512> g_submissions;
uint64_t g_submission_sequence = 0;
std::mutex g_submission_mutex;

// Host-visible breadcrumb buffer. Deliberately never destroyed: it is only created in the debug
// mode and must stay readable while the device loss is being reported.
Buffer*           g_breadcrumbs = nullptr;
constexpr uint64_t BreadcrumbSize = 64;

const char* OpName(uint32_t op) {
	switch (op) {
		case 0: return "DispatchDirect";
		case 1: return "DrawIndex";
		case 2: return "DrawIndexAuto";
		case 3: return "EopWrite";
		case 4: return "EopInterrupt";
		case 5: return "EopWriteBack";
		case 6: return "EopFlip";
		case 7: return "EopWriteBackFlip";
		case 8: return "EopOnlyFlip";
		case 9: return "DrawComplete";
		default: return "Unknown";
	}
}

void Print(const char* stage, const CheckpointRecord& record) {
	// Draws: args=phase,index_count,instance_count,first_instance ps=<hash> vs=<hash>.
	// Dispatches: args=x,y,z,mode ps=<cs hash>.
	LOGF("GpuCheckpoint %s: seq=%" PRIu64 " op=%s(%u) submit=%" PRIu64
	     " args=%u,%u,%u,0x%08x ps=0x%016" PRIx64 " vs=0x%016" PRIx64 "\n",
	     stage, record.sequence, OpName(record.op), record.op, record.submit_id, record.arg0,
	     record.arg1, record.arg2, record.arg3, record.arg4, record.arg5);
	std::printf("GpuCheckpoint %s: seq=%" PRIu64 " op=%s(%u) submit=%" PRIu64
	            " args=%u,%u,%u,0x%08x ps=0x%016" PRIx64 " vs=0x%016" PRIx64 "\n",
	            stage, record.sequence, OpName(record.op), record.op, record.submit_id,
	            record.arg0, record.arg1, record.arg2, record.arg3, record.arg4, record.arg5);
}

} // namespace

bool GpuQueueTraceEnabled() { return g_queue_trace_enabled; }

void RecordGpuSubmission(const void* scheduler, vk::Semaphore master, uint64_t tick,
                         const SubmitInfo& submit, bool returned, vk::Result result) {
	if (!g_queue_trace_enabled) return;
	std::lock_guard lock(g_submission_mutex);
	const auto seq = ++g_submission_sequence;
	g_submissions[seq % g_submissions.size()] = {seq, scheduler, master, tick, submit, returned, result};
}

void ReportGpuSubmissionHistory() {
	if (!g_queue_trace_enabled) return;
	std::vector<SubmissionRecord> records;
	records.reserve(g_submissions.size());
	{
		std::lock_guard lock(g_submission_mutex);
		const auto first = g_submission_sequence >= g_submissions.size()
		                       ? g_submission_sequence - g_submissions.size() + 1 : uint64_t {1};
		for (auto seq = first; seq <= g_submission_sequence; ++seq) {
			records.push_back(g_submissions[seq % g_submissions.size()]);
		}
	}
	const auto handle = [](vk::Semaphore sem) {
		return static_cast<unsigned long long>(reinterpret_cast<uintptr_t>(static_cast<VkSemaphore>(sem)));
	};
	SubmitOpsIndex ops_index;
	if (g_queue_trace_ops) {
		BuildSubmitOpsIndex(ops_index);
	}
	for (const auto& r: records) {
		LOGF("GpuSubmitHistory: seq=%llu scheduler=%p master=%016llx tick=%llu phase=%s result=%d present=%d\n",
		     static_cast<unsigned long long>(r.sequence), r.scheduler, handle(r.master),
		     static_cast<unsigned long long>(r.tick), r.returned ? "returned" : "before-api",
		     static_cast<int>(r.result), r.submit.present ? 1 : 0);
		if (g_queue_trace_ops && !r.returned) {
			PrintSubmitOps(ops_index, r.scheduler, r.sequence, r.tick);
		}
		for (uint32_t j = 0; j < r.submit.num_wait_semaphores; ++j) {
			LOGF("GpuSubmitWait: seq=%llu semaphore=%016llx value=%llu stages=%x\n",
			     static_cast<unsigned long long>(r.sequence), handle(r.submit.wait_semaphores[j]),
			     static_cast<unsigned long long>(r.submit.wait_ticks[j]),
			     static_cast<uint32_t>(r.submit.wait_stages[j]));
		}
		for (uint32_t j = 0; j < r.submit.num_signal_semaphores; ++j) {
			LOGF("GpuSubmitSignal: seq=%llu semaphore=%016llx value=%llu\n",
			     static_cast<unsigned long long>(r.sequence), handle(r.submit.signal_semaphores[j]),
			     static_cast<unsigned long long>(r.submit.signal_ticks[j]));
		}
	}
	Log::Flush();
}

void RecordGpuCheckpoint(GraphicContext& graphics, CommandScheduler& scheduler,
                         vk::CommandBuffer command, bool inside_rendering, uint32_t op,
                         uint64_t submit_id, uint32_t arg0, uint32_t arg1, uint32_t arg2,
                         uint32_t arg3, uint64_t arg4, uint64_t arg5) {
	if ((!graphics.gpu_breadcrumbs_enabled && !graphics.diagnostic_checkpoints_enabled) ||
	    command == nullptr) {
		return;
	}
	const auto sequence = g_sequence.fetch_add(1, std::memory_order_relaxed) + 1;
	auto&      record   = g_ring[sequence % RingSize];
	{
		std::lock_guard lock(g_ring_mutex);
		record = {sequence, submit_id, arg4, arg5, op, arg0, arg1, arg2, arg3};
	}

	// vkCmdUpdateBuffer must be recorded outside a render pass instance.
	if (graphics.gpu_breadcrumbs_enabled && !inside_rendering) {
		if (g_breadcrumbs == nullptr) {
			g_breadcrumbs = new Buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
			                           BreadcrumbSize);
			SetVulkanObjectNameF(graphics.device, g_breadcrumbs->Handle(), "GPU Breadcrumbs");
		}
		static_assert(sizeof(CheckpointRecord) <= BreadcrumbSize);
		command.updateBuffer(g_breadcrumbs->Handle(), 0, sizeof(record), &record);
	}
	if (graphics.diagnostic_checkpoints_enabled) {
		// Select the raw-pointer overload. The enhanced T const& overload would
		// record the address of a temporary pointer on this thread's stack.
		command.setCheckpointNV(static_cast<const void*>(&record));
	}
}

void ReportGpuCheckpointHistory() {
	std::vector<CheckpointRecord> records;
	{
		std::lock_guard lock(g_ring_mutex);
		const auto latest = g_sequence.load(std::memory_order_relaxed);
		const auto first = latest > 16 ? latest - 15 : uint64_t {1};
		for (auto sequence = first; sequence <= latest; ++sequence) {
			const auto& record = g_ring[sequence % RingSize];
			if (record.sequence == sequence) records.push_back(record);
		}
	}
	for (const auto& record: records) Print("cpu-recorded (not GPU completion)", record);
	std::fflush(stdout);
}

// Session 98 (patch_s98b): ReportGpuCheckpoints split in two.  The breadcrumb half reads a
// host-visible buffer and is safe at any time; the NV half is valid only after device loss.
void ReportGpuBreadcrumb(GraphicContext& graphics) {
	if (graphics.gpu_breadcrumbs_enabled && g_breadcrumbs != nullptr &&
	    !g_breadcrumbs->Mapped().empty()) {
		g_breadcrumbs->Invalidate(0, BreadcrumbSize);
		CheckpointRecord record {};
		std::memcpy(&record, g_breadcrumbs->Mapped().data(), sizeof(record));
		Print("breadcrumb (last started, never completed)", record);
		const auto latest = g_sequence.load(std::memory_order_relaxed);
		LOGF("GpuCheckpoint: latest recorded seq=%" PRIu64 " (%" PRIu64 " operations recorded after the breadcrumb)\n",
		     latest, latest >= record.sequence ? latest - record.sequence : 0);
		std::printf("GpuCheckpoint: latest recorded seq=%" PRIu64 "\n", latest);
	}
	std::fflush(stdout);
}

void ReportNvCheckpoints(GraphicContext& graphics) {
	if (graphics.diagnostic_checkpoints_enabled && graphics.queue != nullptr) {
		uint32_t count = 0;
		graphics.queue.getCheckpointDataNV(&count, nullptr);
		if (count == 0) {
			LOGF("GpuCheckpoint: no NV checkpoint data available\n");
		} else {
			std::vector<vk::CheckpointDataNV> data(count);
			for (auto& entry: data) {
				entry.sType = vk::StructureType::eCheckpointDataNV;
				entry.pNext = nullptr;
			}
			graphics.queue.getCheckpointDataNV(&count, data.data());
			for (uint32_t i = 0; i < count; i++) {
				const auto* marker = static_cast<const CheckpointRecord*>(data[i].pCheckpointMarker);
				const char* stage =
				    data[i].stage == vk::PipelineStageFlagBits::eBottomOfPipe ? "nv bottom-of-pipe"
				    : data[i].stage == vk::PipelineStageFlagBits::eTopOfPipe ? "nv top-of-pipe"
				                                                              : "nv other-stage";
				const bool in_ring = marker >= g_ring.data() && marker < g_ring.data() + g_ring.size();
				if (!in_ring) {
					LOGF("GpuCheckpoint %s: foreign marker %p\n", stage,
					     static_cast<const void*>(marker));
					continue;
				}
				CheckpointRecord record;
				{
					std::lock_guard lock(g_ring_mutex);
					record = *marker;
				}
				Print(stage, record);
			}
		}
	}
	std::fflush(stdout);
}

void ReportGpuCheckpoints(GraphicContext& graphics) {
	ReportGpuBreadcrumb(graphics);
	ReportNvCheckpoints(graphics);
}

// ================================================================================================
// Session 98 (patch_s98b, MEASUREMENT ONLY): GPU buffer markers and the CPU op ring
// (gpuCheckpoints.h).  Layout per scheduler: one Download buffer of 2*N u32, top[] at 0 and
// bot[] at N*4; slot = seq % N; value = seq.  The op ring uses the same slot.  Producer: the
// thread that records draws/dispatches (GuestGpu; the m4baton relay only while GuestGpu is
// parked).  An entry is published by a release store of its seq word, written last; a reader
// accepts it only if the word equals the expected seq before and after the copy.
// ================================================================================================

// Session 98 (patch_s98c): pre[] marker (KYTY_GPU_MARKERS=2), live-visibility control, culprit=.
bool g_gpu_ops_active = g_queue_trace_ops;

namespace {

constexpr uint32_t MarkerSlots   = uint32_t {1} << 16u;
constexpr uint32_t MarkerMask    = MarkerSlots - 1u;
// Readers stay this far behind the producer's slot reuse (the producer may still be running).
constexpr uint32_t MarkerWindow  = MarkerSlots - 4096u;
constexpr uint32_t MarkerMaxScheds = 8;

struct MarkerOp {
	std::atomic<uint32_t> seq {0};
	uint32_t              kind      = 0;
	uint64_t              tick      = 0;
	uint64_t              submit_id = 0;
	uint64_t              h0        = 0; // cs (dispatch) or ps (draw)
	uint64_t              h1        = 0; // vs (draw)
	uint32_t              a0        = 0;
	uint32_t              a1        = 0;
	uint32_t              a2        = 0;
	uint8_t               floor     = 0;
	uint8_t               gds       = 0;
};

struct MarkerOpCopy {
	uint32_t seq       = 0;
	uint32_t kind      = 0;
	uint64_t tick      = 0;
	uint64_t submit_id = 0;
	uint64_t h0        = 0;
	uint64_t h1        = 0;
	uint32_t a0        = 0;
	uint32_t a1        = 0;
	uint32_t a2        = 0;
	uint8_t  floor     = 0;
	uint8_t  gds       = 0;
};

struct MarkerSched {
	CommandScheduler*     scheduler = nullptr; // null once the scheduler was destroyed
	const void*           key       = nullptr; // its address (the queue-trace history key)
	uint32_t              index     = 0;
	std::atomic<uint32_t> next {0};      // last seq handed out
	std::atomic<uint32_t> published {0}; // last seq whose entry is written
	Buffer*               buffer = nullptr; // never destroyed (read after device loss)
	MarkerOp*             ops    = nullptr; // never freed
	uint64_t              checked_tick = 0; // positive control: last tick judged
};

std::array<MarkerSched, MarkerMaxScheds> g_marker_scheds;
uint32_t                                 g_marker_sched_count = 0; // under g_marker_mutex
std::mutex                               g_marker_mutex;
std::mutex                               g_marker_report_mutex;

thread_local bool                    t_marker_gds       = false;
thread_local MarkerSched*            t_marker_cache     = nullptr;
thread_local const CommandScheduler* t_marker_cache_key = nullptr;

#if defined(__clang__) || defined(__GNUC__)
__attribute__((format(printf, 1, 2)))
#endif
void MarkerOut(const char* format, ...) {
	char    text[1024];
	va_list args;
	va_start(args, format);
	std::vsnprintf(text, sizeof(text), format, args);
	va_end(args);
	LOGF("%s", text);
	std::fputs(text, stdout);
}

const char* MarkerKindName(uint32_t kind) {
	switch (static_cast<GpuMarkerKind>(kind)) {
		case GpuMarkerKind::Draw: return "draw";
		case GpuMarkerKind::DrawIndexed: return "drawIndexed";
		case GpuMarkerKind::DrawIndirect: return "drawIndirect";
		case GpuMarkerKind::DrawIndexedIndirect: return "drawIndexedIndirect";
		case GpuMarkerKind::Mesh: return "mesh";
		case GpuMarkerKind::Dispatch: return "dispatch";
		case GpuMarkerKind::DispatchIndirect: return "dispatchIndirect";
		default: return "unknown";
	}
}

bool MarkerIsDispatch(uint32_t kind) {
	return kind == static_cast<uint32_t>(GpuMarkerKind::Dispatch) ||
	       kind == static_cast<uint32_t>(GpuMarkerKind::DispatchIndirect);
}

bool ReadMarkerOp(const MarkerSched& ms, uint32_t seq, MarkerOpCopy* out) {
	if (ms.ops == nullptr || seq == 0) {
		return false;
	}
	const auto& op = ms.ops[seq & MarkerMask];
	if (op.seq.load(std::memory_order_acquire) != seq) {
		return false;
	}
	out->seq       = seq;
	out->kind      = op.kind;
	out->tick      = op.tick;
	out->submit_id = op.submit_id;
	out->h0        = op.h0;
	out->h1        = op.h1;
	out->a0        = op.a0;
	out->a1        = op.a1;
	out->a2        = op.a2;
	out->floor     = op.floor;
	out->gds       = op.gds;
	std::atomic_thread_fence(std::memory_order_acquire);
	return op.seq.load(std::memory_order_relaxed) == seq;
}

// Under g_marker_mutex.
MarkerSched* MarkerRegisterLocked(CommandScheduler* scheduler) {
	for (uint32_t i = 0; i < g_marker_sched_count; i++) {
		if (g_marker_scheds[i].scheduler == scheduler) {
			return &g_marker_scheds[i];
		}
	}
	MarkerSched* entry = nullptr;
	for (uint32_t i = 0; i < g_marker_sched_count && entry == nullptr; i++) {
		// A destroyed scheduler that never recorded an op leaves nothing worth keeping.
		if (g_marker_scheds[i].scheduler == nullptr && g_marker_scheds[i].ops == nullptr) {
			entry = &g_marker_scheds[i];
		}
	}
	if (entry == nullptr) {
		if (g_marker_sched_count >= MarkerMaxScheds) {
			static bool logged = false;
			if (!logged) {
				logged = true;
				LOGF("GpuMarkers: more than %u schedulers, scheduler=%p not marked\n",
				     MarkerMaxScheds, static_cast<void*>(scheduler));
			}
			return nullptr;
		}
		entry        = &g_marker_scheds[g_marker_sched_count];
		entry->index = g_marker_sched_count++;
	}
	entry->scheduler    = scheduler;
	entry->key          = scheduler;
	entry->checked_tick = 0;
	entry->next.store(0, std::memory_order_relaxed);
	entry->published.store(0, std::memory_order_relaxed);
	LOGF("GpuMarkers: scheduler=%p index=%u registered\n", static_cast<void*>(scheduler),
	     entry->index);
	return entry;
}

// Under g_marker_mutex: the op ring and (markers on) the slot buffer, on the first op.
void MarkerEnsureStorageLocked(MarkerSched& ms, CommandScheduler& scheduler) {
	if (ms.ops == nullptr) {
		ms.ops = new MarkerOp[MarkerSlots];
	}
	if (g_markers_enabled && ms.buffer == nullptr) {
		auto& graphics = scheduler.Graphics();
		auto* buffer = new Buffer(graphics, scheduler, MemoryUsage::Download, 0, AllFlags,
		                          uint64_t {3} * MarkerSlots * sizeof(uint32_t));
		if (buffer->Mapped().size() < uint64_t {3} * MarkerSlots * sizeof(uint32_t)) {
			EXIT("GpuMarkers: the marker buffer is not host-mapped\n");
		}
		std::memset(buffer->Mapped().data(), 0xFF, buffer->Mapped().size());
		buffer->Flush(0, buffer->Size());
		SetVulkanObjectNameF(graphics.device, buffer->Handle(), "GPU Markers");
		ms.buffer = buffer;
		LOGF("GpuMarkers: scheduler=%p index=%u buffer slots=%u bytes=%llu\n",
		     static_cast<void*>(&scheduler), ms.index, MarkerSlots,
		     static_cast<unsigned long long>(buffer->Size()));
	}
}

// The newest op in [lo, latest] recorded into a tick <= known (ticks never decrease along seq).
bool MarkerLastCompleted(const MarkerSched& ms, uint32_t latest, uint64_t known,
                         MarkerOpCopy* out) {
	if (latest == 0) {
		return false;
	}
	const uint32_t lo = latest > MarkerWindow ? latest - MarkerWindow + 1u : 1u;
	MarkerOpCopy   op;
	if (!ReadMarkerOp(ms, lo, &op) || op.tick > known) {
		return false;
	}
	uint32_t good = lo;
	*out          = op;
	uint32_t bad  = latest + 1u; // exclusive; unknown
	while (bad - good > 1u) {
		const uint32_t mid = good + (bad - good) / 2u;
		if (!ReadMarkerOp(ms, mid, &op)) {
			return false;
		}
		if (op.tick <= known) {
			good = mid;
			*out = op;
		} else {
			bad = mid;
		}
	}
	return true;
}

struct MarkerSnap {
	MarkerSched*          ms      = nullptr;
	uint32_t              index   = 0;
	const void*           key     = nullptr;
	bool                  alive   = false;
	uint32_t              latest  = 0;
	uint64_t              known   = 0;
	uint64_t              current = 0;
	std::vector<uint32_t> top;
	std::vector<uint32_t> bot;
	std::vector<uint32_t> pre;          // Session 98 (patch_s98c): 0xFFFFFFFF unless markers=2
	uint64_t              fresh    = 0; // semaphore value read AFTER the copy (else = known)
	bool                  fresh_ok = false;
};

void TakeMarkerSnaps(std::vector<MarkerSnap>& out) {
	out.clear();
	std::lock_guard lock(g_marker_mutex);
	for (uint32_t i = 0; i < g_marker_sched_count; i++) {
		auto& ms = g_marker_scheds[i];
		if (ms.buffer == nullptr || ms.ops == nullptr) {
			continue;
		}
		MarkerSnap s;
		s.ms     = &ms;
		s.index  = ms.index;
		s.key    = ms.key;
		s.alive  = ms.scheduler != nullptr;
		s.latest = ms.published.load(std::memory_order_acquire);
		if (s.alive) {
			s.known   = ms.scheduler->GetMasterSemaphore().KnownGpuTick();
			s.current = ms.scheduler->CurrentTick();
		}
		ms.buffer->Invalidate(0, ms.buffer->Size());
		const auto* words = reinterpret_cast<const uint32_t*>(ms.buffer->Mapped().data());
		s.top.assign(words, words + MarkerSlots);
		s.bot.assign(words + MarkerSlots, words + 2u * MarkerSlots);
		s.pre.assign(words + 2u * MarkerSlots, words + 3u * MarkerSlots);
		s.fresh = s.known;
		if (s.alive) {
			uint64_t value = 0;
			s.fresh_ok = ms.scheduler->Graphics().device.getSemaphoreCounterValue(
			                 ms.scheduler->GetMasterSemaphore().Handle(), &value) ==
			             vk::Result::eSuccess;
			if (s.fresh_ok) {
				s.fresh = value;
			}
		}
		out.push_back(std::move(s));
	}
}

} // namespace

bool GpuMarkersRequested() {
	return g_markers_requested;
}

void GpuMarkersSetEnabled(bool enabled) {
	g_markers_enabled = enabled;
	g_gpu_ops_active  = g_queue_trace_ops || enabled;
	if (enabled) { // Session 98 (patch_s98c)
		LOGF("GpuMarkers: pre=%d (KYTY_GPU_MARKERS=2 adds a BOTTOM_OF_PIPE marker before each op)\n",
		     g_markers_pre ? 1 : 0);
	}
}

void GpuMarkersRegisterScheduler(CommandScheduler* scheduler) {
	if (!g_gpu_ops_active) {
		return;
	}
	std::lock_guard lock(g_marker_mutex);
	(void)MarkerRegisterLocked(scheduler);
}

void GpuMarkersUnregisterScheduler(CommandScheduler* scheduler) {
	if (!g_gpu_ops_active) {
		return;
	}
	std::lock_guard lock(g_marker_mutex);
	for (uint32_t i = 0; i < g_marker_sched_count; i++) {
		if (g_marker_scheds[i].scheduler == scheduler) {
			g_marker_scheds[i].scheduler = nullptr;
		}
	}
}

void GpuMarkerNoteGds() {
	if (g_gpu_ops_active) {
		t_marker_gds = true;
	}
}

GpuMarkerSite GpuMarkerBegin(CommandScheduler& scheduler, GpuMarkerKind kind, uint64_t submit_id,
                             uint64_t h0, uint64_t h1, uint32_t a0, uint32_t a1, uint32_t a2,
                             bool floor_armed) {
	GpuMarkerSite site;
	MarkerSched*  ms = t_marker_cache;
	if (ms == nullptr || t_marker_cache_key != &scheduler || ms->scheduler != &scheduler) {
		std::lock_guard lock(g_marker_mutex);
		ms = MarkerRegisterLocked(&scheduler);
		if (ms == nullptr) {
			return site;
		}
		MarkerEnsureStorageLocked(*ms, scheduler);
		t_marker_cache     = ms;
		t_marker_cache_key = &scheduler;
	}
	const uint32_t seq = ms->next.fetch_add(1, std::memory_order_relaxed) + 1u;
	auto&          op  = ms->ops[seq & MarkerMask];
	op.seq.store(0, std::memory_order_relaxed);
	std::atomic_thread_fence(std::memory_order_release);
	op.kind      = static_cast<uint32_t>(kind);
	op.tick      = scheduler.CurrentTick();
	op.submit_id = submit_id;
	op.h0        = h0;
	op.h1        = h1;
	op.a0        = a0;
	op.a1        = a1;
	op.a2        = a2;
	op.floor     = floor_armed ? 1u : 0u;
	op.gds       = t_marker_gds ? 1u : 0u;
	t_marker_gds = false;
	op.seq.store(seq, std::memory_order_release);
	ms->published.store(seq, std::memory_order_release);
	if (ms->buffer != nullptr) {
		const uint32_t slot = seq & MarkerMask;
		site.buffer = ms->buffer->Handle();
		site.top    = vk::DeviceSize {slot} * sizeof(uint32_t);
		site.bottom = (vk::DeviceSize {MarkerSlots} + slot) * sizeof(uint32_t);
		site.seq    = seq;
		site.pre    = (vk::DeviceSize {2u * MarkerSlots} + slot) * sizeof(uint32_t); // patch_s98c
		site.pre_on = g_markers_pre;
		Common::FrameStats::Add(Common::FrameStats::Counter::GpuMarkerOps, 1);
	}
	return site;
}

namespace {

// Session 98 (patch_s98c): run totals of the live-visibility control, printed by the readout.
std::atomic<uint64_t> g_live_bot_total {0};
std::atomic<uint64_t> g_live_top_total {0};

// Under g_marker_mutex, on GuestGpu.  Over at most 256 ops after `after` (the last op of a
// completed tick, or 0): copy their top/bot words, THEN read the timeline semaphore value, so an op
// whose tick is above that value was read before its submission signalled.  The end-of-submission
// flush writes back every op of a submission together and only after all of them completed, so it
// cannot produce (a) top visible with bot not (the op has not completed, the submission has not
// ended) -> gm_live_top, or (b) inside one unsignalled tick, bot visible for some ops and not for
// others -> gm_live counts the visible ones.  gm_live > 0 in a run is the evidence that the hang
// readout can see the completed ops of the tick that never signals.
void MarkerLiveControl(MarkerSched& ms, uint32_t latest, uint32_t after) {
	namespace FS = Common::FrameStats;
	if (latest == 0) {
		return;
	}
	constexpr uint32_t Span  = 256;
	const uint32_t     lo    = latest > MarkerWindow ? latest - MarkerWindow + 1u : 1u;
	const uint32_t     first = std::max(after + 1u, lo);
	if (first > latest) {
		return;
	}
	const uint32_t last = std::min(latest, first + (Span - 1u));
	ms.buffer->Invalidate(0, ms.buffer->Size());
	const auto* words = reinterpret_cast<const uint32_t*>(ms.buffer->Mapped().data());
	std::array<uint32_t, Span> top_w {};
	std::array<uint32_t, Span> bot_w {};
	for (uint32_t k = first; k <= last; k++) {
		top_w[k - first] = words[k & MarkerMask];
		bot_w[k - first] = words[MarkerSlots + (k & MarkerMask)];
	}
	uint64_t fresh = 0;
	if (ms.scheduler->Graphics().device.getSemaphoreCounterValue(
	        ms.scheduler->GetMasterSemaphore().Handle(), &fresh) != vk::Result::eSuccess) {
		return;
	}
	uint64_t live_bot = 0;
	uint64_t live_top = 0;
	for (uint32_t k = first; k <= last;) {
		MarkerOpCopy a;
		if (!ReadMarkerOp(ms, k, &a)) {
			k++;
			continue;
		}
		uint32_t n        = 0;
		uint32_t done     = 0;
		uint32_t top_only = 0;
		uint32_t j        = k;
		for (; j <= last; j++) {
			MarkerOpCopy b;
			if (!ReadMarkerOp(ms, j, &b) || b.tick != a.tick) {
				break;
			}
			const bool bot_seen = bot_w[j - first] == j;
			n++;
			done += bot_seen ? 1u : 0u;
			top_only += (!bot_seen && top_w[j - first] == j) ? 1u : 0u;
		}
		if (a.tick > fresh) {
			live_top += top_only;
			if (done != 0 && done < n) {
				live_bot += done;
			}
		}
		k = j > k ? j : k + 1u;
	}
	if (live_bot != 0) {
		FS::Add(FS::Counter::GpuMarkerLive, live_bot);
		g_live_bot_total.fetch_add(live_bot, std::memory_order_relaxed);
	}
	if (live_top != 0) {
		FS::Add(FS::Counter::GpuMarkerLiveTop, live_top);
		g_live_top_total.fetch_add(live_top, std::memory_order_relaxed);
	}
}

} // namespace

// Positive control, every guest flip packet: the last op of the newest tick the master semaphore
// reports complete (each tick judged once) must have bot[slot] == seq.  If it has not, marker
// writes do not reach host memory without a barrier on this driver and the readout is void.
// Session 98 (patch_s98c): that control only judges ticks whose signal already flushed the caches;
// MarkerLiveControl (gm_live / gm_live_top) judges the unsignalled ones every hang readout reads.
void GpuMarkersFlip() {
	if (!g_gpu_ops_active && !g_markers_requested) {
		return;
	}
	namespace FS = Common::FrameStats;
	if (g_markers_requested && !g_markers_enabled) {
		FS::Add(FS::Counter::GpuMarkerUnsup, 1);
		return;
	}
	if (!g_markers_enabled) {
		return;
	}
	std::lock_guard lock(g_marker_mutex);
	for (uint32_t i = 0; i < g_marker_sched_count; i++) {
		auto& ms = g_marker_scheds[i];
		if (ms.scheduler == nullptr || ms.buffer == nullptr || ms.ops == nullptr) {
			continue;
		}
		const uint32_t latest = ms.published.load(std::memory_order_acquire);
		const uint64_t known  = ms.scheduler->GetMasterSemaphore().KnownGpuTick();
		MarkerOpCopy   op;
		const bool     have_done = MarkerLastCompleted(ms, latest, known, &op);
		if (have_done && op.tick > ms.checked_tick) {
			ms.checked_tick = op.tick;
			const uint32_t slot = op.seq & MarkerMask;
			const auto     top_offset = uint64_t {slot} * sizeof(uint32_t);
			const auto     bot_offset = (uint64_t {MarkerSlots} + slot) * sizeof(uint32_t);
			ms.buffer->Invalidate(top_offset, sizeof(uint32_t));
			ms.buffer->Invalidate(bot_offset, sizeof(uint32_t));
			uint32_t top = 0;
			uint32_t bot = 0;
			std::memcpy(&top, ms.buffer->Mapped().data() + top_offset, sizeof(top));
			std::memcpy(&bot, ms.buffer->Mapped().data() + bot_offset, sizeof(bot));
			if (bot == op.seq) {
				FS::Add(FS::Counter::GpuMarkerOk, 1);
			} else {
				FS::Add(FS::Counter::GpuMarkerBad, 1);
				static std::atomic<uint32_t> bad_logged {0};
				if (bad_logged.fetch_add(1, std::memory_order_relaxed) < 32) {
					LOGF("GpuMarkerControl: bad sched=%u seq=%u tick=%llu known=%llu top=0x%08x "
					     "bot=0x%08x kind=%s\n",
					     ms.index, op.seq, static_cast<unsigned long long>(op.tick),
					     static_cast<unsigned long long>(known), top, bot, MarkerKindName(op.kind));
				}
			}
		}
		MarkerLiveControl(ms, latest, have_done ? op.seq : 0u);
	}
}

// Readout.  Per scheduler with a marker buffer, over the ops of ticks above the known GPU tick:
//  - k0 = the first op recorded into an unfinished tick (tick > known);
//  - HUNG = the lowest k >= k0 with bot[k] != k (so bot[k-1] == k-1 or k == k0);
//    started = top[k] == k; if not started, op k was not reached: unmarked work, another
//    scheduler's submission, or a semaphore wait (Session 98, patch_s98d);
//    a scan that reaches the window's bottom still unfinished names nothing (window-exhausted);
//  - IN FLIGHT: every j > k with top[j] == j and bot[j] != j (64 lines, then the total);
//  - per unfinished tick: first/last seq, ops, started, done, kinds;
//  - a second snapshot 1 s later: progress=1 if any started/done count or the known tick moved.
void ReportGpuMarkers(const char* tag, bool device_lost) {
	if (!g_markers_enabled) {
		return;
	}
	std::lock_guard          report_lock(g_marker_report_mutex);
	std::vector<MarkerSnap>  first;
	TakeMarkerSnaps(first);
	struct Range {
		uint32_t k0      = 0;
		uint32_t latest  = 0;
		uint32_t started = 0;
		uint32_t done    = 0;
	};
	std::vector<Range> ranges(first.size());
	for (size_t si = 0; si < first.size(); si++) {
		const auto& s      = first[si];
		const auto  top_ok = [&](uint32_t k) { return s.top[k & MarkerMask] == k; };
		const auto  bot_ok = [&](uint32_t k) { return s.bot[k & MarkerMask] == k; };
		MarkerOut("GpuMarkers: tag=%s sched=%u scheduler=%p alive=%d device_lost=%d latest_seq=%u "
		          "known_tick=%llu current_tick=%llu\n",
		          tag, s.index, s.key, s.alive ? 1 : 0, device_lost ? 1 : 0, s.latest,
		          static_cast<unsigned long long>(s.known),
		          static_cast<unsigned long long>(s.current));
		auto& range  = ranges[si];
		range.latest = s.latest;
		range.k0     = s.latest + 1u;
		if (s.latest == 0) {
			continue;
		}
		const uint32_t lo = s.latest > MarkerWindow ? s.latest - MarkerWindow + 1u : 1u;
		MarkerOpCopy   op;
		// Session 98 (patch_s98d): the scan reached the bottom of the window with that op's tick
		// still unfinished - the first unfinished op lies below the window; name nothing.
		bool     exhausted = false;
		uint64_t lo_tick   = 0;
		for (uint32_t k = s.latest; k >= lo; k--) {
			if (!ReadMarkerOp(*s.ms, k, &op) || op.tick <= s.known) {
				break;
			}
			range.k0 = k;
			if (k == lo) {
				exhausted = lo > 1u;
				lo_tick   = op.tick;
				break;
			}
		}
		{
			// Session 98 (patch_s98c): what of the UNSIGNALLED ticks is visible right now (ticks
			// above the semaphore value read after the copy), and the run's live-control totals.
			// A readout with gm_live_total=0 has never shown that completed ops of an unsignalled
			// tick become host-visible - its "not done" may only mean "not flushed".
			const uint64_t fresh      = s.fresh;
			uint32_t       unsig      = 0;
			uint32_t       vis_bot    = 0;
			uint32_t       vis_top    = 0;
			uint32_t       partial    = 0;
			uint64_t       cur_tick   = 0;
			uint32_t       cur_n      = 0;
			uint32_t       cur_done   = 0;
			bool           cur_valid  = false;
			for (uint32_t k = range.k0; k <= s.latest; k++) {
				MarkerOpCopy v;
				if (!ReadMarkerOp(*s.ms, k, &v) || v.tick <= fresh) {
					continue;
				}
				if (!cur_valid || v.tick != cur_tick) {
					partial += (cur_valid && cur_done != 0 && cur_done < cur_n) ? 1u : 0u;
					cur_tick  = v.tick;
					cur_n     = 0;
					cur_done  = 0;
					cur_valid = true;
				}
				const bool b = bot_ok(k);
				unsig++;
				cur_n++;
				cur_done += b ? 1u : 0u;
				vis_bot += b ? 1u : 0u;
				vis_top += (!b && top_ok(k)) ? 1u : 0u;
			}
			partial += (cur_valid && cur_done != 0 && cur_done < cur_n) ? 1u : 0u;
			MarkerOut("GpuMarkerVisibility: tag=%s sched=%u fresh_tick=%llu fresh_ok=%d "
			          "unsignalled_ops=%u visible_unsignalled=%u visible_top_only=%u partial_ticks=%u "
			          "gm_live_total=%llu gm_live_top_total=%llu pre=%d\n",
			          tag, s.index, static_cast<unsigned long long>(fresh), s.fresh_ok ? 1 : 0,
			          unsig, vis_bot, vis_top, partial,
			          static_cast<unsigned long long>(g_live_bot_total.load(std::memory_order_relaxed)),
			          static_cast<unsigned long long>(g_live_top_total.load(std::memory_order_relaxed)),
			          g_markers_pre ? 1 : 0);
		}
		if (exhausted) {
			MarkerOut("GpuMarkerHung: tag=%s sched=%u none reason=window-exhausted lo=%u latest=%u "
			          "lo_tick=%llu known=%llu cur_tick=%llu (the first op of the first unfinished "
			          "tick lies below the marker window)\n",
			          tag, s.index, lo, s.latest, static_cast<unsigned long long>(lo_tick),
			          static_cast<unsigned long long>(s.known),
			          static_cast<unsigned long long>(s.current));
			range.k0 = s.latest + 1u;
			continue;
		}
		if (range.k0 > s.latest) {
			MarkerOpCopy last;
			const bool   have = ReadMarkerOp(*s.ms, s.latest, &last);
			MarkerOut("GpuMarkerHung: tag=%s sched=%u none reason=no-marked-op-in-an-unfinished-tick "
			          "last_seq=%u last_tick=%llu last_started=%d last_done=%d\n",
			          tag, s.index, s.latest,
			          static_cast<unsigned long long>(have ? last.tick : 0),
			          top_ok(s.latest) ? 1 : 0, bot_ok(s.latest) ? 1 : 0);
			continue;
		}
		for (uint32_t k = range.k0; k <= s.latest; k++) {
			range.started += top_ok(k) ? 1u : 0u;
			range.done += bot_ok(k) ? 1u : 0u;
		}
		uint32_t hung = 0;
		for (uint32_t k = range.k0; k <= s.latest; k++) {
			if (!bot_ok(k)) {
				hung = k;
				break;
			}
		}
		if (hung == 0) {
			MarkerOut("GpuMarkerHung: tag=%s sched=%u none reason=every-marked-op-of-the-unfinished-"
			          "ticks-completed first=%u last=%u (the hang is in unmarked work)\n",
			          tag, s.index, range.k0, s.latest);
		} else {
			MarkerOpCopy h;
			const bool   have = ReadMarkerOp(*s.ms, hung, &h);
			const bool   disp = have && MarkerIsDispatch(h.kind);
			// Session 98 (patch_s98c): TOP_OF_PIPE (started= / cp_reached=) is written when the
			// command processor reaches the op and does NOT wait for earlier work; only pre[]
			// (KYTY_GPU_MARKERS=2, BOTTOM_OF_PIPE before the op) shows that everything before the
			// op completed, i.e. that the hang is in the op itself.
			const bool   pre_ok  = g_markers_pre && s.pre[hung & MarkerMask] == hung;
			const char*  prior   = !g_markers_pre ? "na" : (pre_ok ? "1" : "0");
			const char*  culprit = !top_ok(hung) ? "gap"
			                       : !g_markers_pre ? "ambiguous"
			                       : pre_ok         ? "op"
			                                        : "gap";
			MarkerOut("GpuMarkerHung: tag=%s sched=%u seq=%u tick=%llu submit=%llu kind=%s "
			          "cs=0x%016llx vs=0x%016llx ps=0x%016llx args=%u,%u,%u floor=%u gds=%u "
			          "started=%d prev_done=%d first_unfinished=%u ring=%d cp_reached=%d prior_done=%s "
			          "culprit=%s cur_tick=%llu known=%llu not_submitted=%d submit_backlog=%zu "
			          "record_backlog=%zu\n",
			          tag, s.index, hung, static_cast<unsigned long long>(have ? h.tick : 0),
			          static_cast<unsigned long long>(have ? h.submit_id : 0),
			          have ? MarkerKindName(h.kind) : "overwritten",
			          static_cast<unsigned long long>(disp ? h.h0 : 0),
			          static_cast<unsigned long long>(have && !disp ? h.h1 : 0),
			          static_cast<unsigned long long>(have && !disp ? h.h0 : 0), have ? h.a0 : 0,
			          have ? h.a1 : 0, have ? h.a2 : 0, have ? h.floor : 0, have ? h.gds : 0,
			          top_ok(hung) ? 1 : 0, hung > 1 && bot_ok(hung - 1u) ? 1 : 0, range.k0,
			          have ? 1 : 0, top_ok(hung) ? 1 : 0, prior, culprit,
			          static_cast<unsigned long long>(s.current),
			          static_cast<unsigned long long>(s.known),
			          have && h.tick >= s.current ? 1 : 0, AsyncSubmitBacklog(), RecordBacklog());
			if (!top_ok(hung)) {
				MarkerOut("GpuMarkerGap: tag=%s sched=%u op %u not reached (op %u done=%d): unmarked "
				          "work, another scheduler's submission, or a semaphore wait\n",
				          tag, s.index, hung, hung - 1u, hung > 1 && bot_ok(hung - 1u) ? 1 : 0);
			} else if (g_markers_pre && !pre_ok) { // Session 98 (patch_s98c)
				MarkerOut("GpuMarkerGap: tag=%s sched=%u kind=prior-unfinished op %u was reached by the "
				          "command processor but the work recorded before it never completed (pre "
				          "marker missing): the hang is in unmarked work between op %u and op %u, "
				          "not in op %u\n",
				          tag, s.index, hung, hung - 1u, hung, hung);
			} else if (!g_markers_pre) {
				MarkerOut("GpuMarkerGap: tag=%s sched=%u kind=ambiguous op %u was reached (TOP) and did "
				          "not complete; TOP does not wait for earlier work, so the hang is in op %u OR "
				          "in unmarked work between op %u and op %u (KYTY_GPU_MARKERS=2 separates them)\n",
				          tag, s.index, hung, hung, hung - 1u, hung);
			}
			uint32_t in_flight  = 0;
			uint32_t done_after = 0;
			for (uint32_t j = hung + 1u; j <= s.latest; j++) {
				done_after += bot_ok(j) ? 1u : 0u;
				if (!top_ok(j) || bot_ok(j)) {
					continue;
				}
				if (in_flight < 64) {
					MarkerOpCopy f;
					const bool   have_f = ReadMarkerOp(*s.ms, j, &f);
					const bool   disp_f = have_f && MarkerIsDispatch(f.kind);
					MarkerOut("GpuMarkerInFlight: tag=%s sched=%u seq=%u tick=%llu kind=%s "
					          "cs=0x%016llx vs=0x%016llx ps=0x%016llx args=%u,%u,%u floor=%u gds=%u\n",
					          tag, s.index, j, static_cast<unsigned long long>(have_f ? f.tick : 0),
					          have_f ? MarkerKindName(f.kind) : "overwritten",
					          static_cast<unsigned long long>(disp_f ? f.h0 : 0),
					          static_cast<unsigned long long>(have_f && !disp_f ? f.h1 : 0),
					          static_cast<unsigned long long>(have_f && !disp_f ? f.h0 : 0),
					          have_f ? f.a0 : 0, have_f ? f.a1 : 0, have_f ? f.a2 : 0,
					          have_f ? f.floor : 0, have_f ? f.gds : 0);
				}
				in_flight++;
			}
			MarkerOut("GpuMarkerInFlight: tag=%s sched=%u total=%u completed_after_hung=%u\n", tag,
			          s.index, in_flight, done_after);
		}
		// Per unfinished tick.
		uint32_t lines = 0;
		uint32_t more  = 0;
		for (uint32_t k = range.k0; k <= s.latest;) {
			MarkerOpCopy a;
			if (!ReadMarkerOp(*s.ms, k, &a)) {
				k++;
				continue;
			}
			uint32_t last = k;
			uint32_t n = 0, started = 0, done = 0;
			uint32_t kinds[8] {};
			for (uint32_t j = k; j <= s.latest; j++) {
				MarkerOpCopy b;
				if (!ReadMarkerOp(*s.ms, j, &b) || b.tick != a.tick) {
					break;
				}
				last = j;
				n++;
				started += top_ok(j) ? 1u : 0u;
				done += bot_ok(j) ? 1u : 0u;
				kinds[b.kind & 7u]++;
			}
			if (lines < 128) {
				MarkerOut("GpuMarkerTick: tag=%s sched=%u tick=%llu first=%u last=%u ops=%u "
				          "started=%u done=%u kinds=draw:%u,idx:%u,ind:%u,idxind:%u,mesh:%u,disp:%u,"
				          "dispind:%u\n",
				          tag, s.index, static_cast<unsigned long long>(a.tick), k, last, n, started,
				          done, kinds[1], kinds[2], kinds[3], kinds[4], kinds[5], kinds[6], kinds[7]);
				lines++;
			} else {
				more++;
			}
			k = last + 1u;
		}
		if (more != 0) {
			MarkerOut("GpuMarkerTick: tag=%s sched=%u (%u more ticks not printed)\n", tag, s.index,
			          more);
		}
	}
	Log::Flush();
	std::fflush(stdout);
	if (!first.empty()) {
		std::this_thread::sleep_for(std::chrono::seconds(1));
		std::vector<MarkerSnap> second;
		TakeMarkerSnaps(second);
		for (size_t si = 0; si < first.size(); si++) {
			const auto& a = first[si];
			const auto  b = std::find_if(second.begin(), second.end(),
			                             [&](const MarkerSnap& s) { return s.ms == a.ms; });
			if (b == second.end()) {
				continue;
			}
			const auto& range   = ranges[si];
			uint32_t    started = 0;
			uint32_t    done    = 0;
			for (uint32_t k = range.k0; k <= range.latest && range.latest != 0; k++) {
				started += b->top[k & MarkerMask] == k ? 1u : 0u;
				done += b->bot[k & MarkerMask] == k ? 1u : 0u;
			}
			const bool progress = started != range.started || done != range.done ||
			                      b->known != a.known || b->latest != a.latest;
			MarkerOut("GpuMarkerProgress: tag=%s sched=%u progress=%d started=%u->%u done=%u->%u "
			          "known=%llu->%llu latest_seq=%u->%u\n",
			          tag, a.index, progress ? 1 : 0, range.started, started, range.done, done,
			          static_cast<unsigned long long>(a.known),
			          static_cast<unsigned long long>(b->known), a.latest, b->latest);
		}
	}
	Log::Flush();
	std::fflush(stdout);
}

namespace {

void BuildSubmitOpsIndex(SubmitOpsIndex& index) {
	index.clear();
	std::lock_guard lock(g_marker_mutex);
	for (uint32_t i = 0; i < g_marker_sched_count; i++) {
		const auto& ms = g_marker_scheds[i];
		if (ms.ops == nullptr) {
			continue;
		}
		const uint32_t latest = ms.published.load(std::memory_order_acquire);
		if (latest == 0) {
			continue;
		}
		const uint32_t lo = latest > MarkerWindow ? latest - MarkerWindow + 1u : 1u;
		for (uint32_t k = lo; k <= latest; k++) {
			MarkerOpCopy op;
			if (!ReadMarkerOp(ms, k, &op)) {
				continue;
			}
			auto [it, inserted] =
			    index.try_emplace({ms.key, op.tick}, std::make_pair(k, k));
			if (!inserted) {
				it->second.second = k;
			}
		}
	}
}

void AppendHashes(std::string& out, const std::vector<uint64_t>& hashes) {
	out += '[';
	const size_t shown = std::min<size_t>(hashes.size(), 24);
	for (size_t i = 0; i < shown; i++) {
		char text[24];
		std::snprintf(text, sizeof(text), "%s%016llx", i == 0 ? "" : ",",
		              static_cast<unsigned long long>(hashes[i]));
		out += text;
	}
	if (hashes.size() > shown) {
		out += ",+" + std::to_string(hashes.size() - shown);
	}
	out += ']';
}

void PrintSubmitOps(const SubmitOpsIndex& index, const void* scheduler, uint64_t submit_seq,
                    uint64_t tick) {
	const auto it = index.find({scheduler, tick});
	if (it == index.end()) {
		LOGF("GpuSubmitOps: seq=%llu tick=%llu ops=none\n",
		     static_cast<unsigned long long>(submit_seq), static_cast<unsigned long long>(tick));
		return;
	}
	const MarkerSched* ms = nullptr;
	{
		std::lock_guard lock(g_marker_mutex);
		for (uint32_t i = 0; i < g_marker_sched_count; i++) {
			if (g_marker_scheds[i].key == scheduler && g_marker_scheds[i].ops != nullptr) {
				ms = &g_marker_scheds[i];
			}
		}
	}
	if (ms == nullptr) {
		return;
	}
	uint32_t              n = 0, draws = 0, disp = 0, ind = 0, floor = 0, gds = 0;
	std::vector<uint64_t> cs;
	std::vector<uint64_t> vs;
	std::vector<uint64_t> ps;
	const auto            add = [](std::vector<uint64_t>& v, uint64_t h) {
		           if (h != 0 && std::find(v.begin(), v.end(), h) == v.end()) {
			           v.push_back(h);
		           }
	};
	for (uint32_t k = it->second.first; k <= it->second.second; k++) {
		MarkerOpCopy op;
		if (!ReadMarkerOp(*ms, k, &op) || op.tick != tick) {
			continue;
		}
		n++;
		const bool dispatch = MarkerIsDispatch(op.kind);
		disp += dispatch ? 1u : 0u;
		draws += dispatch ? 0u : 1u;
		ind += (op.kind == static_cast<uint32_t>(GpuMarkerKind::DrawIndirect) ||
		        op.kind == static_cast<uint32_t>(GpuMarkerKind::DrawIndexedIndirect) ||
		        op.kind == static_cast<uint32_t>(GpuMarkerKind::DispatchIndirect))
		           ? 1u
		           : 0u;
		floor += op.floor;
		gds += op.gds;
		if (dispatch) {
			add(cs, op.h0);
		} else {
			add(ps, op.h0);
			add(vs, op.h1);
		}
	}
	std::string text;
	text += " cs=";
	AppendHashes(text, cs);
	text += " vs=";
	AppendHashes(text, vs);
	text += " ps=";
	AppendHashes(text, ps);
	LOGF("GpuSubmitOps: seq=%llu tick=%llu ops=%u..%u n=%u draws=%u disp=%u ind=%u floor=%u "
	     "gds=%u%s\n",
	     static_cast<unsigned long long>(submit_seq), static_cast<unsigned long long>(tick),
	     it->second.first, it->second.second, n, draws, disp, ind, floor, gds, text.c_str());
}

} // namespace

} // namespace Libs::Graphics
