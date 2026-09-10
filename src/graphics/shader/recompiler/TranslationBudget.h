#pragma once

#include "common/assert.h"
#include <chrono>
#include <cstddef>

namespace Libs::Graphics::ShaderRecompiler {
// Counts ALL constructed instructions, including intermediates later eliminated. Only a
// speculative worker installs a budget. No clocks are read on the ordinary translation path.
struct TranslationBudget {
	std::size_t remaining = 500000;
	std::chrono::steady_clock::time_point deadline =
	    std::chrono::steady_clock::now() + std::chrono::seconds(3);
	static inline thread_local TranslationBudget* current = nullptr;
};
inline void CheckTranslationBudget(bool check_time = false) {
	if (auto* budget = TranslationBudget::current) {
		if (budget->remaining == 0 ||
		    ((check_time || (budget->remaining & 1023u) == 0) &&
		     std::chrono::steady_clock::now() > budget->deadline)) {
			EXIT("speculative translation budget exceeded\n");
		}
		--budget->remaining;
	}
}
} // namespace Libs::Graphics::ShaderRecompiler
