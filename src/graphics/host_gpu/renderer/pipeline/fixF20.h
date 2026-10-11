#pragma once

// Track F, F42a (HPP-779, ROADMAP s122 item 694(v)(1), (5), (10); row F20): KYTY_FIX_F20, form P.
// RecordBdaFault (spirvEmitterMemory.cpp) writes one bit of the page fault bitmap as
//   %v = OpLoad %u32 %p ; %o = OpBitwiseOr %u32 %v %bit ; OpStore %p %o      (%p = OpAccessChain fault_buffer ...)
// - a non-atomic read-modify-write: invocations of one dispatch writing the same word lose bits (row F20, data race
// under the Vulkan memory model). RewriteFaultOr replaces each such triple by
//   %v = OpAtomicOr %u32 %p %scope_device %semantics_none %bit
// (12 words -> 7; the result keeps the id of the load and is not read; the scope and semantics operands are the
// existing OpConstant %u32 1 and %u32 0 of the module - RecordBdaFault itself emits both). The translation cache keeps
// the words of the translator; the rewrite runs where a Vulkan module is created from them (CreateCachedModule and the
// dual-source variant, pipelineCache.cpp / shaders.cpp) - outside the translation cache signature set
// (src/graphics/shader/** and CMakeLists.txt SHADER_CACHE_EXTRA_FILES). Header-only, no Vulkan: the GPU stand of item
// 694(g)(1) (tests/ShaderRecompilerComputeTests.cpp --f20-stand) and the corpus / replay modules of items 694(g)(3)-(4)
// (tests/shaderCfgTests.cpp KYTY_RECOMPILE_F20, KYTY_TEST_F20FILE) call this same function.

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <span>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace Libs::Graphics::FixF20 {

struct RewriteStats {
	uint32_t named     = 0;     // variables with OpName "fault_buffer"
	uint32_t sites     = 0;     // OpLoad -> OpBitwiseOr -> OpStore triples over a fault_buffer access chain
	uint32_t rewritten = 0;     // triples replaced by OpAtomicOr
	uint32_t unmatched = 0;     // see RewriteFaultOr
	bool     malformed = false; // not a SPIR-V module this walker can read (nothing rewritten)
};

// bound: the translator's binding layout of the program has the FaultBuffer binding (CompiledShaderInfo before
// AdoptDmaLayout; ROADMAP s122 item 694(v)(5), RC4 of F41b). Nothing is rewritten unless bound.
// unmatched (item 694(v)(5)): +1 malformed module; +1 bound and no variable named fault_buffer; +1 a variable named
// fault_buffer in a module that is not bound; +1 per OpLoad through an access chain on fault_buffer that does not
// start a triple; +1 per triple left as it is (the loaded value or the OR result has another use inside a function,
// or the module has no OpConstant 1 / 0 of the 32-bit unsigned type).
// out: = in with every rewritten triple replaced when rewritten > 0 (header and id bound unchanged); cleared otherwise.
inline RewriteStats RewriteFaultOr(std::span<const uint32_t> in, bool bound, std::vector<uint32_t>& out) {
	constexpr uint32_t kMagic               = 0x07230203u;
	constexpr uint32_t kOpName              = 5u;
	constexpr uint32_t kOpTypeInt           = 21u;
	constexpr uint32_t kOpConstant          = 43u;
	constexpr uint32_t kOpFunction          = 54u;
	constexpr uint32_t kOpLoad              = 61u;
	constexpr uint32_t kOpStore             = 62u;
	constexpr uint32_t kOpAccessChain       = 65u;
	constexpr uint32_t kOpInBoundsAccessChain = 66u;
	constexpr uint32_t kOpBitwiseOr         = 197u;
	constexpr uint32_t kOpAtomicOr          = 241u; // OpAtomicOr (242 is OpAtomicXor)
	constexpr uint32_t kOpSwitch            = 251u;
	constexpr size_t   kHeaderWords         = 5;
	// OpName <id> "fault_buffer": 12 characters + NUL, padded to 4 words.
	static constexpr char kName[16] = "fault_buffer";

	RewriteStats stats;
	out.clear();
	struct Ins {
		size_t   at;
		uint32_t op;
		uint32_t count;
	};
	std::vector<Ins> ins;
	if (in.size() < kHeaderWords || in[0] != kMagic) {
		stats.malformed = true;
		stats.unmatched = 1;
		return stats;
	}
	for (size_t i = kHeaderWords; i < in.size();) {
		const uint32_t count = in[i] >> 16u;
		if (count == 0 || count > in.size() - i) {
			stats.malformed = true;
			stats.unmatched = 1;
			return stats;
		}
		ins.push_back({i, in[i] & 0xffffu, count});
		i += count;
	}

	std::unordered_set<uint32_t> fault_vars;
	std::unordered_set<uint32_t> u32_types;
	uint32_t                     const_one  = 0;
	uint32_t                     const_zero = 0;
	size_t                       first_function = ins.size();
	for (size_t k = 0; k < ins.size(); k++) {
		const auto& x = ins[k];
		if (x.op == kOpName && x.count == 6 && std::memcmp(&in[x.at + 2], kName, sizeof(kName)) == 0) {
			fault_vars.insert(in[x.at + 1]);
		} else if (x.op == kOpTypeInt && x.count == 4 && in[x.at + 2] == 32u && in[x.at + 3] == 0u) {
			u32_types.insert(in[x.at + 1]);
		} else if (x.op == kOpFunction && first_function == ins.size()) {
			first_function = k;
		}
	}
	for (const auto& x: ins) {
		if (x.op == kOpConstant && x.count == 4 && u32_types.contains(in[x.at + 1])) {
			if (in[x.at + 3] == 1u && const_one == 0) {
				const_one = in[x.at + 2];
			} else if (in[x.at + 3] == 0u && const_zero == 0) {
				const_zero = in[x.at + 2];
			}
		}
	}
	stats.named = static_cast<uint32_t>(fault_vars.size());
	if (!bound) {
		stats.unmatched = stats.named != 0 ? 1u : 0u;
		return stats;
	}
	if (fault_vars.empty()) {
		stats.unmatched = 1;
		return stats;
	}

	std::unordered_set<uint32_t> chains;
	for (const auto& x: ins) {
		if ((x.op == kOpAccessChain || x.op == kOpInBoundsAccessChain) && x.count >= 4 &&
		    fault_vars.contains(in[x.at + 3])) {
			chains.insert(in[x.at + 2]);
		}
	}

	// Triples: OpLoad %u32 %v %p ; OpBitwiseOr %u32 %o (%v %bit | %bit %v) ; OpStore %p %o - three instructions in a row.
	struct Site {
		size_t   k;   // index of the OpLoad in `ins`
		uint32_t type;
		uint32_t value;
		uint32_t pointer;
		uint32_t result;
		uint32_t bit;
	};
	std::vector<Site> sites;
	for (size_t k = 0; k < ins.size(); k++) {
		const auto& x = ins[k];
		if (x.op != kOpLoad || x.count < 4 || !chains.contains(in[x.at + 3])) {
			continue;
		}
		bool triple = false;
		if (x.count == 4 && k + 2 < ins.size() && u32_types.contains(in[x.at + 1])) {
			const auto& o = ins[k + 1];
			const auto& s = ins[k + 2];
			const uint32_t v = in[x.at + 2];
			const uint32_t p = in[x.at + 3];
			if (o.op == kOpBitwiseOr && o.count == 5 && in[o.at + 1] == in[x.at + 1] &&
			    (in[o.at + 3] == v) != (in[o.at + 4] == v) && s.op == kOpStore && s.count == 3 &&
			    in[s.at + 1] == p && in[s.at + 2] == in[o.at + 2]) {
				sites.push_back({k, in[x.at + 1], v, p, in[o.at + 2], in[o.at + 3] == v ? in[o.at + 4] : in[o.at + 3]});
				triple = true;
			}
		}
		if (!triple) {
			stats.unmatched++;
		}
	}
	stats.sites = static_cast<uint32_t>(sites.size());
	if (sites.empty()) {
		return stats;
	}

	// Uses of the loaded values and OR results inside the functions: every operand word of every instruction from the
	// first OpFunction on (OpSwitch: the selector only - its other words are literals and labels). A triple is
	// rewritten only when its value and result occur exactly twice (definition + the one use inside the triple).
	std::unordered_map<uint32_t, uint32_t> uses;
	for (const auto& site: sites) {
		uses[site.value] = 0;
		uses[site.result] = 0;
	}
	for (size_t k = first_function; k < ins.size(); k++) {
		const auto&  x    = ins[k];
		const size_t last = x.op == kOpSwitch ? std::min<size_t>(x.count, 2) : x.count;
		for (size_t w = 1; w < last; w++) {
			if (auto it = uses.find(in[x.at + w]); it != uses.end()) {
				it->second++;
			}
		}
	}
	std::vector<uint8_t> rewrite(ins.size(), 0);
	for (const auto& site: sites) {
		if (const_one != 0 && const_zero != 0 && uses[site.value] == 2 && uses[site.result] == 2) {
			rewrite[site.k] = 1;
			stats.rewritten++;
		} else {
			stats.unmatched++;
		}
	}
	if (stats.rewritten == 0) {
		return stats;
	}

	out.reserve(in.size());
	out.insert(out.end(), in.begin(), in.begin() + static_cast<std::ptrdiff_t>(kHeaderWords));
	size_t s = 0;
	for (size_t k = 0; k < ins.size(); k++) {
		const auto& x = ins[k];
		if (rewrite[k] != 0) {
			while (sites[s].k != k) {
				s++;
			}
			const auto& site = sites[s];
			out.push_back((7u << 16u) | kOpAtomicOr);
			out.push_back(site.type);
			out.push_back(site.value);
			out.push_back(site.pointer);
			out.push_back(const_one);
			out.push_back(const_zero);
			out.push_back(site.bit);
			k += 2; // the OpBitwiseOr and the OpStore of the triple
			continue;
		}
		out.insert(out.end(), in.begin() + static_cast<std::ptrdiff_t>(x.at),
		           in.begin() + static_cast<std::ptrdiff_t>(x.at + x.count));
	}
	return stats;
}

// KYTY_FIX_F20 (default 1 since FS15a, HPP-820, ROADMAP s122 item 730(g)(1)): read once per process (unset or "" - 1;
// 0/false/off/no - 0; any other value as EnvValueOn); the first call prints "FixF20: mode=<0|1>". At 0 the callers
// never call Apply.
int Mode();

// At KYTY_FIX_F20=1 only: RewriteFaultOr + the totals of the "FixF20Stat:" line (printed every 4096 calls and by
// PrintExitStat). Returns true when `out` holds the rewritten module to create instead of `in`.
bool Apply(const std::vector<uint32_t>& in, bool bound, std::vector<uint32_t>& out);

// The exit line "FixF20Stat: when=exit ..." (KYTY_FIX_F20=1 only; nothing at 0).
void PrintExitStat();

// Track F, F42a2 (HPP-805, ROADMAP s122 item 705(b)(1)): the totals calls and rewritten of the "FixF20Stat:" line, read
// by the stand arm E (the log of the test process is silent; at 0 there is no line).
uint64_t Calls();
uint64_t Rewritten();

} // namespace Libs::Graphics::FixF20
