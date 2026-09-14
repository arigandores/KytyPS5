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
    {"KYTY_RECORD_PIN", "recpin", false},
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

} // namespace

bool Detail::EnabledSlow(Gate gate) noexcept {
	return States()[static_cast<size_t>(gate)].load(std::memory_order_relaxed);
}

uint32_t Detail::ValueSlow(Knob knob) noexcept {
	return KnobStates()[static_cast<size_t>(knob)].load(std::memory_order_relaxed);
}

void Poll(uint32_t frame) noexcept {
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

	auto& states = States();
	for (size_t index = 0; index < states.size(); index++) {
		const auto& definition = DEFINITIONS[index];
		const auto* value      = FindAssignment(text.data(), definition.name);
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
		const auto& definition = KNOB_DEFINITIONS[index];
		const auto* value      = FindAssignment(text.data(), definition.name);
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

} // namespace Common::Gates
