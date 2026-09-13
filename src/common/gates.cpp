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
}};

struct KnobDefinition {
	const char* environment;
	const char* name;
	uint32_t    fallback;
	uint32_t    limit;
};

constexpr std::array<KnobDefinition, static_cast<size_t>(Knob::Count)> KNOB_DEFINITIONS {{
    {"KYTY_DRAW_AHEAD_THREADS", "dathreads", 4, 64},
}};

using KnobState = std::array<std::atomic<uint32_t>, static_cast<size_t>(Knob::Count)>;

KnobState& KnobStates() {
	static KnobState states;
	static const bool initialized = [] {
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
		return true;
	}();
	(void)initialized;
	return states;
}

using State = std::array<std::atomic<bool>, static_cast<size_t>(Gate::Count)>;

State& States() {
	static State states;
	static const bool initialized = [] {
		for (size_t index = 0; index < states.size(); index++) {
			const auto& definition = DEFINITIONS[index];
			const auto* value      = std::getenv(definition.environment);
			states[index].store(value != nullptr ? value[0] == '1' : definition.fallback,
			                    std::memory_order_relaxed);
		}
		return true;
	}();
	(void)initialized;
	return states;
}

const char* GateFile() {
	static const char* const path = std::getenv("KYTY_GATE_FILE");
	return path;
}

} // namespace

bool Enabled(Gate gate) noexcept {
	return States()[static_cast<size_t>(gate)].load(std::memory_order_relaxed);
}

uint32_t Value(Knob knob) noexcept {
	return KnobStates()[static_cast<size_t>(knob)].load(std::memory_order_relaxed);
}

void Poll(uint32_t frame) noexcept {
	const auto* path = GateFile();
	if (path == nullptr) {
		return;
	}

	// The file is tiny and written by the measurement script: "copy=1 srtpages=0 clamp=1".
	// Names that are missing keep their current state; a malformed file changes nothing.
	std::array<char, 1024> text {};
	auto*                 file = std::fopen(path, "rb");
	if (file == nullptr) {
		return;
	}
	const auto read = std::fread(text.data(), 1, text.size() - 1, file);
	std::fclose(file);
	text[read] = '\0';

	auto& states = States();
	for (size_t index = 0; index < states.size(); index++) {
		const auto& definition = DEFINITIONS[index];
		const auto* found      = std::strstr(text.data(), definition.name);
		if (found == nullptr) {
			continue;
		}
		const auto* assign = found + std::strlen(definition.name);
		if (*assign != '=' || (assign[1] != '0' && assign[1] != '1')) {
			continue;
		}
		const bool wanted = assign[1] == '1';
		if (states[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%d frame=%u\n", definition.name, wanted ? 1 : 0, frame);
		}
	}

	auto& knobs = KnobStates();
	for (size_t index = 0; index < knobs.size(); index++) {
		const auto& definition = KNOB_DEFINITIONS[index];
		const auto* found      = std::strstr(text.data(), definition.name);
		if (found == nullptr) {
			continue;
		}
		const auto* assign = found + std::strlen(definition.name);
		if (*assign != '=' || assign[1] < '0' || assign[1] > '9') {
			continue;
		}
		auto wanted = static_cast<uint32_t>(std::strtoul(assign + 1, nullptr, 10));
		wanted      = wanted < definition.limit ? wanted : definition.limit;
		if (knobs[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%u frame=%u\n", definition.name, wanted, frame);
		}
	}
}

} // namespace Common::Gates
