#include "graphics/host_gpu/renderer/pipeline/fixF20.h"

#include "common/envFlag.h"
#include "common/logging/log.h"

#include <atomic>
#include <cinttypes>

// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(1), (5)): the knob and the counters of KYTY_FIX_F20 (fixF20.h).

namespace Libs::Graphics::FixF20 {

namespace {

// Totals of the "FixF20Stat:" line, pieces (uint64): calls - modules created through Apply; modules_bound - with the
// FaultBuffer binding of the translator layout; modules - with a variable named fault_buffer; sites, rewritten,
// unmatched - RewriteStats summed (item 694(v)(5): in the game unmatched = 0 and modules_bound = modules).
std::atomic<uint64_t> g_calls {0};
std::atomic<uint64_t> g_modules_bound {0};
std::atomic<uint64_t> g_modules {0};
std::atomic<uint64_t> g_sites {0};
std::atomic<uint64_t> g_rewritten {0};
std::atomic<uint64_t> g_unmatched {0};

void PrintStat(const char* when) {
	LOGF("FixF20Stat: when=%s calls=%" PRIu64 " modules_bound=%" PRIu64 " modules=%" PRIu64 " sites=%" PRIu64
	     " rewritten=%" PRIu64 " unmatched=%" PRIu64 "\n",
	     when, g_calls.load(), g_modules_bound.load(), g_modules.load(), g_sites.load(), g_rewritten.load(),
	     g_unmatched.load());
}

} // namespace

// Track F, FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any
// other value as EnvValueOn (the form of FS14a c8836f14 / FS13a 3630f116); still one reading per process.
int Mode() {
	static const int mode = [] {
		const char* env = std::getenv("KYTY_FIX_F20");
		const int value = (env == nullptr || env[0] == '\0' || Common::EnvValueOn(env)) ? 1 : 0;
		LOGF("FixF20: mode=%d\n", value);
		return value;
	}();
	return mode;
}

bool Apply(const std::vector<uint32_t>& in, bool bound, std::vector<uint32_t>& out) {
	const auto stats = RewriteFaultOr(in, bound, out);
	g_modules_bound.fetch_add(bound ? 1u : 0u);
	g_modules.fetch_add(stats.named != 0 ? 1u : 0u);
	g_sites.fetch_add(stats.sites);
	g_rewritten.fetch_add(stats.rewritten);
	g_unmatched.fetch_add(stats.unmatched);
	if ((g_calls.fetch_add(1) + 1) % 4096u == 0) {
		PrintStat("periodic");
	}
	return stats.rewritten != 0;
}

void PrintExitStat() {
	if (Mode() == 1) {
		PrintStat("exit");
	}
}

// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): getters for the stand arm E.
uint64_t Calls() {
	return g_calls.load();
}

uint64_t Rewritten() {
	return g_rewritten.load();
}

} // namespace Libs::Graphics::FixF20
