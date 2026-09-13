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
}};

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

void Poll(uint32_t frame) noexcept {
	const auto* path = GateFile();
	if (path == nullptr) {
		return;
	}

	// The file is tiny and written by the measurement script: "copy=1 srtpages=0 clamp=1".
	// Names that are missing keep their current state; a malformed file changes nothing.
	std::array<char, 256> text {};
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
}

} // namespace Common::Gates
