#include "common/gates.h"

#include "common/logging/log.h"

#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace Common::Gates {

namespace {

struct Definition {
	const char* environment;
	const char* name;
	bool        fallback;
};

constexpr std::array<Definition, static_cast<size_t>(Gate::Count)> DEFINITIONS {{
    {"KYTY_CBUFFER_DIRECT_COPY", "copy", true},
    {"KYTY_SRT_PAGE_PERSIST", "srtpages", true},
    {"KYTY_CLAMP_MEMO", "clamp", true},
    {"KYTY_REGION_EPOCH", "regionepoch", false},
    {"KYTY_SRT_MEMO", "srtmemo", false},
    {"KYTY_SRT_MEMO_VERIFY", "smemocheck", false},
    {"KYTY_BDA_REGION_STAMPS", "bdastamp", true},
    {"KYTY_BACKING_PAGES", "backpages", true},
    {"KYTY_SRT_STAT", "srtstat", false},
    {"KYTY_META_LOCK", "metalock", true},
    {"KYTY_DRAW_AHEAD", "drawahead", true},
    {"KYTY_DRAW_AHEAD_USE", "dause", true},
    {"KYTY_ASYNC_SUBMIT", "asyncsubmit", true},
    {"KYTY_IMAGE_RECYCLE", "imgrecycle", true},
    {"KYTY_RECORD_THREAD", "recordthread", true},
    {"KYTY_TRACK_LOCKFREE", "trackfree", true},
    {"KYTY_TRACK_LOCKFREE_VERIFY", "tfcheck", false},
    {"KYTY_PROTECT_FAST", "protfast", false},
    {"KYTY_SHADER_WRITE_LOCAL", "swlocal", false},
    {"KYTY_SHADER_WRITE_DEFER", "swdefer", true},
    {"KYTY_GDS_EPOCH", "gdsepoch", false},
    {"KYTY_ATOMIC_IMAGE_NO_BARRIER", "atomimg", false},
    {"KYTY_DESCRIPTOR_RING", "dsring", true},
    {"KYTY_RECORD_PACKETS", "recpack", true},
    {"KYTY_SYNC_FREE", "syncfree", true},
    {"KYTY_SYNC_FREE_VERIFY", "sfcheck", false},
    {"KYTY_PROTECT_BATCH", "protbatch", true},
    {"KYTY_PROTECT_BATCH_VERIFY", "pbcheck", false},
    {"KYTY_TEX_FAULT_HINT", "texfaulthint", true},
    {"KYTY_DRAW_AHEAD_CLASS", "daclass", true},
    {"KYTY_DRAW_AHEAD_PREFETCH", "daprefetch", true},
    {"KYTY_DRAW_AHEAD_CLONE", "daclone", false},
    {"KYTY_TEX_LRU", "texlru", true},
    {"KYTY_TEX_FAST", "texfast", true},
    {"KYTY_TEX_FAST_VERIFY", "texfastcheck", false},
    {"KYTY_TEX_MEMO2", "texmemo2", false},
    {"KYTY_CLAMP_VMA", "clampvma", true},
    {"KYTY_SAMPLER_MEMO", "smpmemo", true},
    {"KYTY_BIND_SPARE", "bindspare", false},
    {"KYTY_FRAME_STATS_LEAN", "fslean", false},
    // Session 57, A2/A3 (page protection).
    {"KYTY_APPLY_SKIP", "applyskip", false},
    // Session 57, A4 (record publish).
    {"KYTY_RECORD_BATCH", "recbatch", false},
    {"KYTY_RECORD_RELAXED", "recrelax", false},
    // Session 63: on by default (Sky Garden -2.3...-3.6 % CPU per draw, three repeats).
    {"KYTY_RECORD_PIN", "recpin", true},
    // Session 57, A1 (sticky pages).
    {"KYTY_STICKY_STAT", "stkstat", false},
    // Session 57, E1/E2/E9 (draw statistics).
    {"KYTY_DRAW_STAT", "drawstat", false},
    {"KYTY_DRAW_STAT_SLOW", "dpslow", false},
    // Session 57, A6/A7 and track B.
    {"KYTY_DRAW_STATE_REUSE", "drawstate", true},
    {"KYTY_SNAPSHOT_KEEP", "snapkeep", true},
    {"KYTY_BUF_LRU", "buflru", true},
    // Session 58, B4 follow-up (snapshot copies).
    {"KYTY_SNAPSHOT_DIFF", "snapdiff", true},
    {"KYTY_SNAPSHOT_SWAP", "snapswap", true},
    // Session 58, M2 step 1 (buffer request memo).
    {"KYTY_BUF_FAST", "buffast", false},
    {"KYTY_BUF_FAST_VERIFY", "buffastcheck", false},
    // Session 58, A3 phase 2 (one host protection flush per BDA dirty-range pass).
    {"KYTY_PROTECT_BATCH2", "protbatch2", false},
    // Session 58, Sky Garden hang: liveness of the async-copy timeline semaphore.
    {"KYTY_ASYNC_COPY_IDLE_SIGNAL", "acopyidle", true},
    // Session 59, M1 producer off the critical thread.
    {"KYTY_DRAW_AHEAD_WALK", "dawalk", false},
    {"KYTY_RT_FAST", "rtfast", true},
    // Session 60, B3.
    {"KYTY_PROG_MEMO", "progmemo", true},
    {"KYTY_PROG_MEMO_VERIFY", "progmemocheck", false},
    // Session 60, item 4.
    {"KYTY_ARM_DEFER", "armdefer", false},
    {"KYTY_ARM_DEFER_VERIFY", "armcheck", false},
    {"KYTY_DRAW_AHEAD_WITNESS", "dawitness", true},
    {"KYTY_DRAW_AHEAD_WITNESS_PTR", "dawitptr", false},
    {"KYTY_DRAW_AHEAD_QUEUE_PREFETCH", "daqpre", false},
    {"KYTY_CB_STAT", "cbstat", false},
    {"KYTY_RECORD_IMAGE_BARRIERS", "recimg", false},
    {"KYTY_RECORD_UPLOADS", "recup", false},
    // Session 64, E6 (measurement only).
    {"KYTY_SHADOW_INLINE", "shadowinline", false},
    // Session 67, infrastructure.
    {"KYTY_SAVE_PERSIST", "savepersist", false},
    // Session 68, measurement only.
    {"KYTY_OCCLUSION_ZERO", "occzero", false},
    {"KYTY_A_MUTATE", "amut", false},
    {"KYTY_PX_STAT", "pxstat", false},
    // Session 69, measurement only.
    {"KYTY_MUT_SITE", "mutsite", false},
    {"KYTY_IMG_SKIP_GPU_STALE", "imgskip", false},
    // Session 70, a behaviour change: two missing cases in the packed-clear decoder.
    {"KYTY_CLEAR_DECODE_WIDE", "cleardec", false},
}};

struct KnobDefinition {
	const char* environment;
	const char* name;
	uint32_t    fallback;
	uint32_t    limit;
};

constexpr std::array<KnobDefinition, static_cast<size_t>(Knob::Count)> KNOB_DEFINITIONS {{
    {"KYTY_DRAW_AHEAD_THREADS", "dathreads", 4, 64},
    {"KYTY_RECORD_ARENA_MB", "recarena", 64, 256},
    {"KYTY_DESCRIPTOR_BATCH", "dsbatch", 32, 256},
    {"KYTY_DESCRIPTOR_POOL", "dspool", 1024, 16384},
    {"KYTY_RECORD_SPIN_US", "recspin", 300, 100000},
    {"KYTY_DRAW_AHEAD_PIN", "dapin", 1, 0xffffffffu},
    {"KYTY_PROCESS_PIN", "procpin", 0, 0xffffffffu},
    {"KYTY_FAULT_WINDOW_KB", "faultkb", 64, 4096},
    {"KYTY_DRAW_AHEAD_WALK_LEAD", "dawalklead", 1, 64},
    {"KYTY_RECORD_PUBLISH_N", "recpubn", 0, 4096},
    {"KYTY_SHADOW_RESOLVE", "shadowresolve", 0, 16},
    {"KYTY_SHADOW_MASK", "shadowmask", 3, 3},
    {"KYTY_M4_BATON", "m4baton", 0, 4096},
    {"KYTY_IMG_SKIP_KB", "imgskipkb", 4096, 1048576},
}};

using KnobState = std::array<std::atomic<uint32_t>, static_cast<size_t>(Knob::Count)>;
using State     = std::array<std::atomic<bool>, static_cast<size_t>(Gate::Count)>;

void Initialize();

KnobState& KnobStates() {
	Initialize();
	return Detail::g_knobs;
}

State& States() {
	Initialize();
	return Detail::g_gates;
}

// Environment values of every gate and knob, then g_ready (the inline fast reads).
void Initialize() {
	static const bool initialized = [] {
		auto& states = Detail::g_knobs;
		for (size_t index = 0; index < states.size(); index++) {
			const auto& definition = KNOB_DEFINITIONS[index];
			const auto* value      = std::getenv(definition.environment);
			auto        parsed     = definition.fallback;
			if (value != nullptr && value[0] >= '0' && value[0] <= '9') {
				parsed = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
			}
			states[index].store(parsed < definition.limit ? parsed : definition.limit,
			                    std::memory_order_relaxed);
		}
		auto& gates = Detail::g_gates;
		for (size_t index = 0; index < gates.size(); index++) {
			const auto& definition = DEFINITIONS[index];
			const auto* value      = std::getenv(definition.environment);
			gates[index].store(value != nullptr ? value[0] == '1' : definition.fallback,
			                   std::memory_order_relaxed);
		}
		Detail::g_ready.store(true, std::memory_order_relaxed);
		return true;
	}();
	(void)initialized;
}

// The value text after "name=" for a whole-word name in the gate file, or nullptr. A name that is
// a prefix of another ("texfast" / "texfastcheck") must not match inside the longer one.
const char* FindAssignment(const char* text, const char* name) {
	const auto length = std::strlen(name);
	for (const char* found = std::strstr(text, name); found != nullptr;
	     found             = std::strstr(found + 1, name)) {
		const bool starts = found == text || found[-1] == ' ' || found[-1] == '\t' ||
		                    found[-1] == '\n' || found[-1] == '\r' || found[-1] == ',' ||
		                    found[-1] == ';';
		if (starts && found[length] == '=') {
			return found + length + 1;
		}
	}
	return nullptr;
}

const char* GateFile() {
	static const char* const path = std::getenv("KYTY_GATE_FILE");
	return path;
}

// KYTY_GATE_SCHEDULE="<N>[+<start>]:<arm>|<arm>[|...]" alternates the arms in blocks of N
// presents from frame <start> on. An arm is the text of a gate file, so the parser below is the
// same FindAssignment and a name an arm does not list keeps its state, exactly as in the file.
// Two textually identical arms are the idle A/A run that declares a run's own threshold.
constexpr size_t SCHEDULE_ARMS_MAX = 8;
constexpr size_t SCHEDULE_TEXT_MAX = 512;

struct Schedule {
	uint32_t period = 0; // presents per block; 0 = no schedule
	uint32_t start  = 0; // first frame the schedule applies to
	uint32_t arms   = 0;
	bool     abba   = false; // two arms in the order A B B A instead of A B A B
	std::array<std::array<char, SCHEDULE_TEXT_MAX>, SCHEDULE_ARMS_MAX> text {};
	// Names any arm assigns: the gate file must not fight the schedule over them, or every flip
	// would write them twice and log a change.
	std::array<bool, static_cast<size_t>(Gate::Count)> owns_gate {};
	std::array<bool, static_cast<size_t>(Knob::Count)> owns_knob {};
};

const Schedule& ScheduleOf() {
	static const Schedule schedule = [] {
		Schedule    s {};
		const auto* value = std::getenv("KYTY_GATE_SCHEDULE");
		if (value == nullptr || value[0] < '0' || value[0] > '9') {
			return s;
		}
		char*      tail   = nullptr;
		const auto period = std::strtoul(value, &tail, 10);
		if (period == 0 || period > 100000 || tail == nullptr) {
			return Schedule {};
		}
		unsigned long start = 0;
		if (*tail == '+') {
			start = std::strtoul(tail + 1, &tail, 10);
		}
		if (tail == nullptr || *tail != ':') {
			return Schedule {};
		}
		const char* cursor = tail + 1;
		while (s.arms < SCHEDULE_ARMS_MAX) {
			const char*  bar = std::strchr(cursor, '|');
			const size_t length =
			    bar != nullptr ? static_cast<size_t>(bar - cursor) : std::strlen(cursor);
			if (length == 0 || length >= SCHEDULE_TEXT_MAX) {
				return Schedule {};
			}
			std::memcpy(s.text[s.arms].data(), cursor, length);
			s.text[s.arms][length] = '\0';
			s.arms++;
			if (bar == nullptr) {
				break;
			}
			cursor = bar + 1;
		}
		if (s.arms == 0) {
			return Schedule {};
		}
		for (uint32_t arm = 0; arm < s.arms; arm++) {
			for (size_t index = 0; index < s.owns_gate.size(); index++) {
				s.owns_gate[index] = s.owns_gate[index] ||
				                     FindAssignment(s.text[arm].data(), DEFINITIONS[index].name) != nullptr;
			}
			for (size_t index = 0; index < s.owns_knob.size(); index++) {
				s.owns_knob[index] =
				    s.owns_knob[index] ||
				    FindAssignment(s.text[arm].data(), KNOB_DEFINITIONS[index].name) != nullptr;
			}
		}
		// KYTY_GATE_SCHEDULE_ABBA=1 counterbalances a two-arm schedule: the block index runs
		// through a Gray code, so the arms go A B B A A B B A and neither of them is always the
		// second of its cycle. Session 67 measured a +0.36 % bias on the idle A/A run without it.
		const auto* abba = std::getenv("KYTY_GATE_SCHEDULE_ABBA");
		s.abba           = abba != nullptr && abba[0] == '1' && s.arms == 2;
		s.period         = static_cast<uint32_t>(period);
		s.start          = static_cast<uint32_t>(start);
		return s;
	}();
	return schedule;
}

// Applies the text of a gate file or of a schedule arm. `skip_*` are the names the schedule owns
// when the text comes from the file.
void ApplyText(const char* text, uint32_t frame, const bool* skip_gate,
               const bool* skip_knob) noexcept {
	auto& states = States();
	for (size_t index = 0; index < states.size(); index++) {
		if (skip_gate != nullptr && skip_gate[index]) {
			continue;
		}
		const auto& definition = DEFINITIONS[index];
		const auto* value      = FindAssignment(text, definition.name);
		if (value == nullptr || (value[0] != '0' && value[0] != '1')) {
			continue;
		}
		const bool wanted = value[0] == '1';
		if (states[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%d frame=%u\n", definition.name, wanted ? 1 : 0, frame);
		}
	}

	auto& knobs = KnobStates();
	for (size_t index = 0; index < knobs.size(); index++) {
		if (skip_knob != nullptr && skip_knob[index]) {
			continue;
		}
		const auto& definition = KNOB_DEFINITIONS[index];
		const auto* value      = FindAssignment(text, definition.name);
		if (value == nullptr || value[0] < '0' || value[0] > '9') {
			continue;
		}
		auto wanted = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
		wanted      = wanted < definition.limit ? wanted : definition.limit;
		if (knobs[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%u frame=%u\n", definition.name, wanted, frame);
		}
	}
}

void PollGateFile(uint32_t frame) noexcept {
	const auto* path = GateFile();
	if (path == nullptr) {
		return;
	}

	// The file is tiny and written by the measurement script: "copy=1 srtpages=0 clamp=1".
	// Names that are missing keep their current state; a malformed file changes nothing.
	std::array<char, 4096> text {};
	auto*                 file = std::fopen(path, "rb");
	if (file == nullptr) {
		return;
	}
	const auto read = std::fread(text.data(), 1, text.size() - 1, file);
	std::fclose(file);
	if (read == text.size() - 1) {
		// The last token may be cut in the middle of a number: apply nothing.
		static bool warned = false;
		if (!warned) {
			warned = true;
			LOGF("Gate: file %s is too long, ignored\n", path);
		}
		return;
	}
	text[read] = '\0';

	const auto& schedule = ScheduleOf();
	ApplyText(text.data(), frame, schedule.owns_gate.data(), schedule.owns_knob.data());
}

// Exact block boundaries in flips: this runs once per flip with a monotonic counter.
void PollSchedule(uint32_t frame) noexcept {
	const auto& schedule = ScheduleOf();
	// The line the caller logs after this reports the interval that ran under the previous arm.
	Detail::g_arm_reported.store(Detail::g_arm.load(std::memory_order_relaxed),
	                             std::memory_order_relaxed);
	Detail::g_block_reported.store(Detail::g_block.load(std::memory_order_relaxed),
	                               std::memory_order_relaxed);
	if (schedule.period == 0 || frame < schedule.start) {
		return;
	}
	const auto block = (frame - schedule.start) / schedule.period;
	const auto arm   = schedule.abba ? (((block >> 1U) ^ block) & 1U) : block % schedule.arms;
	Detail::g_arm.store(arm, std::memory_order_relaxed);
	Detail::g_block.store(block, std::memory_order_relaxed);
	// One producer: Poll only ever runs on the presentation thread.
	static uint32_t applied = 0xffffffffu;
	if (block == applied) {
		return;
	}
	applied = block;
	LOGF("GateArm: arm=%u arms=%u block=%u frame=%u period=%u abba=%u text=%s\n", arm,
	     schedule.arms, block, frame, schedule.period, schedule.abba ? 1U : 0U,
	     schedule.text[arm].data());
	ApplyText(schedule.text[arm].data(), frame, nullptr, nullptr);
}

} // namespace

bool Detail::EnabledSlow(Gate gate) noexcept {
	return States()[static_cast<size_t>(gate)].load(std::memory_order_relaxed);
}

uint32_t Detail::ValueSlow(Knob knob) noexcept {
	return KnobStates()[static_cast<size_t>(knob)].load(std::memory_order_relaxed);
}

void Poll(uint32_t frame) noexcept {
	PollGateFile(frame);
	// The schedule owns the names its arms assign, so the file above skipped them.
	PollSchedule(frame);
}

} // namespace Common::Gates
