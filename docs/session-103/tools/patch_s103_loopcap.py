"""Session 103: KYTY_BVH_LOOP_CAP in spirvEmitterProgram.cpp (the emitter half)."""
import sys

P = 'C:/kyty/KytyPS5/src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp'
DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'
b = open(P, 'rb').read().decode('utf-8')
crlf = '\r\n' in b
b = b.replace('\r\n', '\n')


def rep(old, new, cnt=1):
    global b
    n = b.count(old)
    assert n == cnt, (old[:90], n)
    b = b.replace(old, new)


rep('''void EmitReturn(ValueEmitContext& ctx) {
	EmitKillIfPixelValidMaskInactive(ctx.state);
	EmitBdaFaultFlush(ctx.state);
	ctx.state.builder.AddFunction(spv::OpReturn);
}''', '''void EmitReturnTail(ValueEmitContext& ctx) {
	EmitKillIfPixelValidMaskInactive(ctx.state);
	EmitBdaFaultFlush(ctx.state);
	ctx.state.builder.AddFunction(spv::OpReturn);
}

void EmitReturn(ValueEmitContext& ctx) {
	EmitLoopCapNear(ctx.state); // no-op unless KYTY_BVH_LOOP_CAP covers the program
	EmitReturnTail(ctx);
}''')

rep('''using LoopGuardVariables = std::unordered_map<const IR::Block*, uint32_t>;
''', '''// Loop headers and the counters they spend. KYTY_LOOP_LIMIT: one counter per loop, a bare return
// on abort (debug aid, unchanged). KYTY_BVH_LOOP_CAP: every header of a capped program spends from
// ONE budget per invocation, and the abort counts a trip and leaves through the normal return
// path (fault flush, pixel kill).
struct LoopGuards {
	std::unordered_map<const IR::Block*, uint32_t> variables;
	std::vector<uint32_t>                          declared;
	uint32_t                                       limit = 0;
	bool                                           cap   = false;
};
''')

rep('''bool EmitLoopGuard(ValueEmitContext& ctx, const IR::BlockInfo& info, uint32_t variable) {''',
    '''bool EmitLoopGuard(ValueEmitContext& ctx, const IR::BlockInfo& info, uint32_t variable,
                   const LoopGuards& guards) {''')
rep('''	state.builder.AddFunction(spv::OpUGreaterThan, TypeBool(state), over, next,
	                          ConstantU32(state, LoopGuardLimit()));''', '''	state.builder.AddFunction(spv::OpUGreaterThan, TypeBool(state), over, next,
	                          ConstantU32(state, guards.limit));''')
rep('''	EmitLabel(state, abort_label);
	state.builder.AddFunction(spv::OpReturn);
	EmitLabel(state, after_label);
	return true;''', '''	EmitLabel(state, abort_label);
	if (guards.cap) {
		EmitLoopCapTrip(state, next);
		EmitReturnTail(ctx);
	} else {
		state.builder.AddFunction(spv::OpReturn);
	}
	EmitLabel(state, after_label);
	return true;''')
rep('''void EmitStructuredFunction(ValueEmitContext& ctx, const LoopGuardVariables& loop_guards) {''',
    '''void EmitStructuredFunction(ValueEmitContext& ctx, const LoopGuards& loop_guards) {''')
rep('''		if (const auto found = loop_guards.find(block); found != loop_guards.end()) {
			guarded = EmitLoopGuard(ctx, info, found->second);
		}''', '''		if (const auto found = loop_guards.variables.find(block);
		    found != loop_guards.variables.end()) {
			guarded = EmitLoopGuard(ctx, info, found->second, loop_guards);
		}''')

NL = chr(92) + 'n'
rep('''	LoopGuardVariables loop_guards;
	if (LoopGuardLimit() != 0 && !state.program.dispatcher_fallback) {
		for (size_t index = 0; index < program.blocks.size(); index++) {
			if (program.block_info[index].terminator.loop_header) {
				loop_guards.emplace(program.blocks[index], state.builder.AllocateId());
			}
		}
		if (!loop_guards.empty()) {
			LOGF("SPIR-V loop guard: shader=0x%016" PRIx64 " loops=%zu limit=%u@NL@",
			     program.shader_hash, loop_guards.size(), LoopGuardLimit());
		}
	}'''.replace('@NL@', NL), '''	LoopGuards loop_guards;
	const int  cap_slot = BvhLoopCap() != 0 ? BvhLoopCapSlot(program.shader_hash) : -1;
	if (cap_slot >= 0 && state.program.dispatcher_fallback) {
		LOGF("BvhLoopCap: shader=0x%016" PRIx64 " UNCAPPED (dispatcher fallback)@NL@",
		     program.shader_hash);
	} else if (cap_slot >= 0) {
		const auto budget = state.builder.AllocateId();
		for (size_t index = 0; index < program.blocks.size(); index++) {
			if (program.block_info[index].terminator.loop_header) {
				loop_guards.variables.emplace(program.blocks[index], budget);
			}
		}
		if (!loop_guards.variables.empty()) {
			loop_guards.declared.push_back(budget);
			loop_guards.limit              = BvhLoopCap();
			loop_guards.cap                = true;
			state.loop_cap_budget_variable = budget;
			state.loop_cap_limit           = BvhLoopCap();
			state.loop_cap_slot            = static_cast<uint32_t>(cap_slot);
			state.builder.AddName(budget, "bvh_loop_budget");
		}
		LOGF("BvhLoopCap: shader=0x%016" PRIx64 " loops=%zu cap=%u slot=%d@NL@", program.shader_hash,
		     loop_guards.variables.size(), BvhLoopCap(), cap_slot);
	} else if (LoopGuardLimit() != 0 && !state.program.dispatcher_fallback) {
		for (size_t index = 0; index < program.blocks.size(); index++) {
			if (program.block_info[index].terminator.loop_header) {
				const auto variable = state.builder.AllocateId();
				loop_guards.variables.emplace(program.blocks[index], variable);
				loop_guards.declared.push_back(variable);
			}
		}
		loop_guards.limit = LoopGuardLimit();
		if (!loop_guards.variables.empty()) {
			LOGF("SPIR-V loop guard: shader=0x%016" PRIx64 " loops=%zu limit=%u@NL@",
			     program.shader_hash, loop_guards.variables.size(), LoopGuardLimit());
		}
	}'''.replace('@NL@', NL))
rep('''	for (const auto& [guarded_block, variable]: loop_guards) {
		(void)guarded_block;
		state.builder.AddFunction(spv::OpVariable,''', '''	for (const auto variable: loop_guards.declared) {
		state.builder.AddFunction(spv::OpVariable,''')

# Public knob functions, right after the anonymous namespace closes (before TypeId).
rep('''} // namespace

uint32_t TypeId(EmitterState& state, IR::Type type) {''', '''} // namespace

namespace {

constexpr uint64_t BvhLoopCapDefaultHash = 0x380bb9d636390baeull;
constexpr uint32_t BvhLoopCapDefault     = 65536;

struct BvhLoopCapConfig {
	uint32_t              cap = BvhLoopCapDefault;
	std::vector<uint64_t> set {BvhLoopCapDefaultHash};
	std::string           token;
};

const BvhLoopCapConfig& LoopCapConfig() {
	static const BvhLoopCapConfig config = [] {
		BvhLoopCapConfig result;
		if (const char* value = std::getenv("KYTY_BVH_LOOP_CAP"); value != nullptr) {
			result.cap = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
		}
		if (const char* value = std::getenv("KYTY_BVH_LOOP_CAP_SET"); value != nullptr) {
			result.set.clear();
			const char* cursor = value;
			while (*cursor != 0 && result.set.size() < LoopTripSlots) {
				char*      end  = nullptr;
				const auto hash = std::strtoull(cursor, &end, 16);
				if (end == cursor) {
					break;
				}
				result.set.push_back(hash);
				cursor = *end == ',' ? end + 1 : end;
			}
		}
		const bool is_default = result.cap == BvhLoopCapDefault && result.set.size() == 1 &&
		                        result.set.front() == BvhLoopCapDefaultHash;
		if (!is_default) {
			result.token = ":bvhcap" + std::to_string(result.cap);
			for (const auto hash: result.set) {
				char text[24];
				std::snprintf(text, sizeof(text), "-%016llx", static_cast<unsigned long long>(hash));
				result.token += text;
			}
		}
		return result;
	}();
	return config;
}

} // namespace

uint32_t BvhLoopCap() {
	return LoopCapConfig().cap;
}

int BvhLoopCapSlot(uint64_t shader_hash) {
	const auto& set = LoopCapConfig().set;
	for (size_t index = 0; index < set.size(); index++) {
		if (set[index] == shader_hash) {
			return static_cast<int>(index);
		}
	}
	return -1;
}

std::string BvhLoopCapSignatureToken() {
	return LoopCapConfig().token;
}

uint32_t TypeId(EmitterState& state, IR::Type type) {''')

rep('''#include "graphics/shader/recompiler/backend/spirv/spirvEmitterInstructions.h"

#include "common/assert.h"''', '''#include "graphics/shader/recompiler/backend/spirv/spirvEmitterInstructions.h"

#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"

#include "common/assert.h"''')
rep('''#include <cinttypes>
#include <cstdlib>
#include <functional>''', '''#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <functional>''')

if crlf:
    b = b.replace('\n', '\r\n')
if DRY:
    print('DRY ok')
else:
    open(P, 'wb').write(b.encode('utf-8'))
    print('written', P)
