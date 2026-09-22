"""Session 103, M5': KYTY_BDA_LEAN - the BDA path as design G would build it (ROADMAP §0.1, the
session-103 amendment). Default OFF; every change is behind BdaLeanEnabled(), and with the switch
off the emitter must produce byte-identical SPIR-V (arm A of the session-102 capture, V-c)."""
import sys

DRY = len(sys.argv) > 1 and sys.argv[1] == '--dry'
SRC = 'C:/kyty/KytyPS5/src/graphics/shader/recompiler/backend/spirv/'
files = {}


def load(rel):
    if rel not in files:
        b = open(SRC + rel, 'rb').read().decode('utf-8')
        assert '\r\n' not in b, rel
        files[rel] = b
    return files[rel]


def rep(rel, old, new, cnt=1):
    b = load(rel)
    n = b.count(old)
    assert n == cnt, (rel, old[:100], n)
    files[rel] = b.replace(old, new)


H = 'SpirvEmitter.h'
I = 'spirvEmitterInternal.h'
M = 'spirvEmitterMemory.cpp'
P = 'spirvEmitterProgram.cpp'
D = 'spirvEmitterModule.cpp'

rep(H, '''inline constexpr uint32_t LoopTripSlots    = 8;
} // namespace Emitter''', '''inline constexpr uint32_t LoopTripSlots    = 8;
// Session 103, KYTY_BDA_LEAN (M5', measurement only, default off): the BDA path as design G would
// build it - no fault-buffer store in pixel shaders, one page-table read per lookup (the null-page
// base read once per invocation), read-only PSB views (NonWritable, Restrict when the program
// writes no memory), and uvec4 loads for the 16-byte windows of a scalar load group behind a
// run-time alignment test. Needs the null-page mode. Part of the translation cache signature.
bool BdaLeanEnabled();
} // namespace Emitter''')

rep(I, '''	uint32_t                                         loop_cap_slot            = 0;''',
    '''	uint32_t                                         loop_cap_slot            = 0;
	// KYTY_BDA_LEAN: Private u64 holding page-table entry 0 (the null page), stored at entry.
	uint32_t                                         bda_null_base_variable   = 0;''')

# --- spirvEmitterMemory.cpp -------------------------------------------------------------
rep(M, '''uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer);

uint32_t LoadBdaDword(ValueEmitContext& ctx, uint32_t address) {''', '''uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer);

// KYTY_BDA_LEAN: read-only PSB views. The pointee is a Block struct with one member at offset 0,
// decorated NonWritable, and Restrict when the program writes no buffer or image memory (a PSB
// read may otherwise alias a store through a descriptor).
bool BdaLeanRestrict(const EmitterState& state) {
	const auto& info          = state.program.info;
	const bool  buffer_writes = std::ranges::any_of(
        info.buffers, [](const IR::BufferResource& b) { return b.written || b.atomic; });
	const bool image_writes = std::ranges::any_of(
	    info.images, [](const IR::ImageResource& i) { return i.written || i.atomic; });
	return !buffer_writes && !image_writes;
}

uint32_t LoadBdaReadOnly(ValueEmitContext& ctx, uint32_t address, uint32_t components) {
	auto&      state  = ctx.state;
	const auto member = components == 1u ? TypeU32(state) : TypeU32Vector(state, components);
	const auto view =
	    BdaLeanRestrict(state)
	        ? state.builder.DecoratedType(spv::OpTypeStruct,
	                                      {{spv::OpMemberDecorate, {0, spv::DecorationOffset, 0}},
	                                       {spv::OpMemberDecorate, {0, spv::DecorationNonWritable}},
	                                       {spv::OpMemberDecorate, {0, spv::DecorationRestrict}},
	                                       {spv::OpDecorate, {spv::DecorationBlock}}},
	                                      member)
	        : state.builder.DecoratedType(spv::OpTypeStruct,
	                                      {{spv::OpMemberDecorate, {0, spv::DecorationOffset, 0}},
	                                       {spv::OpMemberDecorate, {0, spv::DecorationNonWritable}},
	                                       {spv::OpDecorate, {spv::DecorationBlock}}},
	                                      member);
	const auto view_pointer = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpConvertUToPtr,
	                          TypePointer(state, spv::StorageClassPhysicalStorageBuffer, view),
	                          view_pointer, address);
	const auto member_pointer = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpAccessChain,
	                          TypePointer(state, spv::StorageClassPhysicalStorageBuffer, member),
	                          member_pointer, view_pointer, ConstantU32(state, 0));
	const auto value = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpLoad, member, value, member_pointer,
	                          spv::MemoryAccessAlignedMask,
	                          static_cast<uint32_t>(sizeof(uint32_t) * components));
	return value;
}

uint32_t LoadBdaDword(ValueEmitContext& ctx, uint32_t address) {''')

rep(M, '''uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer) {
	auto&              state     = ctx.state;
	constexpr uint32_t alignment = sizeof(uint32_t);
	if (BdaNullPageEnabled()) {''', '''uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer) {
	auto&              state     = ctx.state;
	constexpr uint32_t alignment = sizeof(uint32_t);
	if (BdaLeanEnabled()) {
		return LoadBdaReadOnly(ctx, pointer, 1u);
	}
	if (BdaNullPageEnabled()) {''')

# the scalar group: lean fast path
rep(M, '''		EmitLabel(state, fast_label);
		std::vector<uint32_t> fast_values;
		for (const auto& member: members) {
			const auto delta = static_cast<uint64_t>(member.offset - imm_min);
			const auto ptr   = delta == 0 ? page_ptr
			                              : Binary(state, OpIAdd, type, page_ptr,
			                                       ConstantDeviceAddress(state, delta));
			fast_values.push_back(LoadBdaAt(ctx, ptr));
		}
		const auto fast_exit = state.current_label;''', '''		EmitLabel(state, fast_label);
		std::vector<uint32_t> fast_values;
		const auto load_dwords = [&]() {
			std::vector<uint32_t> out;
			for (const auto& member: members) {
				const auto delta = static_cast<uint64_t>(member.offset - imm_min);
				const auto ptr   = delta == 0 ? page_ptr
				                              : Binary(state, OpIAdd, type, page_ptr,
				                                       ConstantDeviceAddress(state, delta));
				out.push_back(LoadBdaAt(ctx, ptr));
			}
			return out;
		};
		if (!BdaLeanEnabled()) {
			fast_values = load_dwords();
		} else {
			// KYTY_BDA_LEAN: the group origin's 16-byte alignment is only known at run time (a
			// copied V#'s class describes the host copy, not the guest base), so test it: an
			// aligned origin loads every 16-byte window with two or more members as one uvec4.
			// Inside the page (this branch) an aligned 16-byte window never leaves it.
			std::vector<std::pair<uint64_t, std::vector<size_t>>> windows;
			for (size_t i = 0; i < members.size(); i++) {
				const auto window = static_cast<uint64_t>(members[i].offset - imm_min) / 16u;
				auto       found  = std::ranges::find_if(
                    windows, [&](const auto& entry) { return entry.first == window; });
				if (found == windows.end()) {
					windows.push_back({window, {i}});
				} else {
					found->second.push_back(i);
				}
			}
			const bool any_vector = std::ranges::any_of(
			    windows, [](const auto& entry) { return entry.second.size() >= 2u; });
			if (!any_vector) {
				fast_values = load_dwords();
			} else {
				const auto aligned = Binary(
				    state, OpIEqual, TypeBool(state),
				    Binary(state, OpBitwiseAnd, type, address, ConstantDeviceAddress(state, 15)),
				    ConstantDeviceAddress(state, 0));
				const auto vector_label = state.builder.AllocateId();
				const auto dword_label  = state.builder.AllocateId();
				const auto join_label   = state.builder.AllocateId();
				state.builder.AddFunction(OpSelectionMerge, join_label,
				                          spv::SelectionControlMaskNone);
				state.builder.AddFunction(OpBranchConditional, aligned, vector_label, dword_label);
				EmitLabel(state, vector_label);
				std::vector<uint32_t> vector_values(members.size(), 0u);
				for (const auto& [window, indices]: windows) {
					if (indices.size() < 2u) {
						const auto delta = static_cast<uint64_t>(members[indices[0]].offset - imm_min);
						const auto ptr   = delta == 0 ? page_ptr
						                              : Binary(state, OpIAdd, type, page_ptr,
						                                       ConstantDeviceAddress(state, delta));
						vector_values[indices[0]] = LoadBdaAt(ctx, ptr);
						continue;
					}
					const auto ptr    = window == 0 ? page_ptr
					                                : Binary(state, OpIAdd, type, page_ptr,
					                                         ConstantDeviceAddress(state, window * 16u));
					const auto vector = LoadBdaReadOnly(ctx, ptr, 4u);
					for (const auto index: indices) {
						const auto component =
						    (static_cast<uint32_t>(members[index].offset - imm_min) % 16u) / 4u;
						vector_values[index] = state.builder.AllocateId();
						state.builder.AddFunction(OpCompositeExtract, TypeU32(state),
						                          vector_values[index], vector, component);
					}
				}
				const auto vector_exit = state.current_label;
				state.builder.AddFunction(OpBranch, join_label);
				EmitLabel(state, dword_label);
				const auto dword_values = load_dwords();
				const auto dword_exit   = state.current_label;
				state.builder.AddFunction(OpBranch, join_label);
				EmitLabel(state, join_label);
				for (size_t i = 0; i < members.size(); i++) {
					const auto joined = state.builder.AllocateId();
					state.builder.AddFunction(OpPhi, TypeU32(state), joined, vector_values[i],
					                          vector_exit, dword_values[i], dword_exit);
					fast_values.push_back(joined);
				}
			}
		}
		const auto fast_exit = state.current_label;''')

# lean switch definition, next to the null-page switch
rep(M, '''// Null-page mode: at shader return, record the last missing page of this invocation.
void EmitBdaFaultFlush(EmitterState& state) {''', '''bool BdaLeanEnabled() {
	static const bool enabled = Common::EnvFlagOn("KYTY_BDA_LEAN") && BdaNullPageEnabled();
	return enabled;
}

// Null-page mode: at shader return, record the last missing page of this invocation.
void EmitBdaFaultFlush(EmitterState& state) {''')

# the lookup function
rep(M, '''	const auto function_type = state.builder.Type(OpTypeFunction, type, type, TypeBool(state));
	state.bda_fault_page_variable = state.builder.DefineGlobalVariable(
	    TypePointer(state, StorageClassPrivate, TypeU32(state)), StorageClassPrivate);
	state.builder.AddName(state.bda_fault_page_variable, "bda_fault_page");''', '''	const auto function_type = state.builder.Type(OpTypeFunction, type, type, TypeBool(state));
	// KYTY_BDA_LEAN: no fault store in pixel shaders (a miss reads the null page silently).
	const bool lean         = BdaLeanEnabled();
	const bool track_faults = !lean || state.program.stage != ShaderType::Pixel;
	if (track_faults) {
		state.bda_fault_page_variable = state.builder.DefineGlobalVariable(
		    TypePointer(state, StorageClassPrivate, TypeU32(state)), StorageClassPrivate);
		state.builder.AddName(state.bda_fault_page_variable, "bda_fault_page");
	}
	if (lean) {
		state.bda_null_base_variable = state.builder.DefineGlobalVariable(
		    TypePointer(state, StorageClassPrivate, type), StorageClassPrivate);
		state.builder.AddName(state.bda_null_base_variable, "bda_null_base");
	}''')
rep(M, '''	const auto table_length = state.builder.AllocateId();
	state.builder.AddFunction(OpArrayLength, TypeU32(state), table_length,
	                          state.bda_pagetable_variable, 0);
	const auto in_table = Binary(state, OpULessThan, TypeBool(state), page64,
	                             Unary(state, OpUConvert, type, table_length));''', '''	uint32_t in_table = 0;
	if (lean) {
		in_table = Binary(state, OpULessThan, TypeBool(state), page64,
		                  ConstantDeviceAddress(state, BufferCache::CACHING_NUMPAGES));
	} else {
		const auto table_length = state.builder.AllocateId();
		state.builder.AddFunction(OpArrayLength, TypeU32(state), table_length,
		                          state.bda_pagetable_variable, 0);
		in_table = Binary(state, OpULessThan, TypeBool(state), page64,
		                  Unary(state, OpUConvert, type, table_length));
	}''')
rep(M, '''	const auto null_pointer = state.builder.AllocateId();
	state.builder.AddFunction(OpAccessChain, TypeStorageBufferU64ElementPointer(state), null_pointer,
	                          state.bda_pagetable_variable, ConstantU32(state, 0),
	                          ConstantU32(state, 0));
	const auto null_base = state.builder.AllocateId();
	state.builder.AddFunction(OpLoad, type, null_base, null_pointer);''', '''	const auto null_base = state.builder.AllocateId();
	if (lean) {
		state.builder.AddFunction(OpLoad, type, null_base, state.bda_null_base_variable);
	} else {
		const auto null_pointer = state.builder.AllocateId();
		state.builder.AddFunction(OpAccessChain, TypeStorageBufferU64ElementPointer(state),
		                          null_pointer, state.bda_pagetable_variable,
		                          ConstantU32(state, 0), ConstantU32(state, 0));
		state.builder.AddFunction(OpLoad, type, null_base, null_pointer);
	}''')
rep(M, '''	// Remember an in-table miss (page 0 is the null page itself and never misses).
	const auto previous = state.builder.AllocateId();
	state.builder.AddFunction(OpLoad, TypeU32(state), previous, state.bda_fault_page_variable);
	const auto remembered = Select(state, TypeU32(state),
	                               Binary(state, OpLogicalAnd, TypeBool(state), missing, active),
	                               page, previous);
	state.builder.AddFunction(OpStore, state.bda_fault_page_variable, remembered);''', '''	// Remember an in-table miss (page 0 is the null page itself and never misses).
	if (track_faults) {
		const auto previous = state.builder.AllocateId();
		state.builder.AddFunction(OpLoad, TypeU32(state), previous, state.bda_fault_page_variable);
		const auto remembered = Select(state, TypeU32(state),
		                               Binary(state, OpLogicalAnd, TypeBool(state), missing, active),
		                               page, previous);
		state.builder.AddFunction(OpStore, state.bda_fault_page_variable, remembered);
	}''')

# --- spirvEmitterProgram.cpp: the null base, once per invocation
rep(P, '''	if (state.bda_fault_page_variable != 0) {
		state.builder.AddFunction(spv::OpStore, state.bda_fault_page_variable,
		                          ConstantU32(state, 0));
	}''', '''	if (state.bda_fault_page_variable != 0) {
		state.builder.AddFunction(spv::OpStore, state.bda_fault_page_variable,
		                          ConstantU32(state, 0));
	}
	if (state.bda_null_base_variable != 0) {
		// KYTY_BDA_LEAN: page-table entry 0 (the null page) read once per invocation.
		const auto entry = state.builder.AllocateId();
		state.builder.AddFunction(spv::OpAccessChain, TypeStorageBufferU64ElementPointer(state),
		                          entry, state.bda_pagetable_variable, ConstantU32(state, 0),
		                          ConstantU32(state, 0));
		const auto null_base = state.builder.AllocateId();
		state.builder.AddFunction(spv::OpLoad, TypeScalarU64(state), null_base, entry);
		state.builder.AddFunction(spv::OpStore, state.bda_null_base_variable, null_base);
	}''')

# --- spirvEmitterModule.cpp: the page table is read-only and never aliased
rep(D, '''			case IR::DescriptorBindingKind::BdaPagetable:
				state.bda_pagetable_variable = Define(StorageBufferU64Type(state), "bda_pagetable");
				break;''', '''			case IR::DescriptorBindingKind::BdaPagetable:
				state.bda_pagetable_variable = Define(StorageBufferU64Type(state), "bda_pagetable");
				if (BdaLeanEnabled()) {
					state.builder.AddAnnotation(spv::OpDecorate, state.bda_pagetable_variable,
					                            spv::DecorationNonWritable);
					state.builder.AddAnnotation(spv::OpDecorate, state.bda_pagetable_variable,
					                            spv::DecorationRestrict);
				}
				break;''')

for rel in (P, D):
    b = load(rel)
    if 'SpirvEmitter.h"' not in b:
        first = b.index('#include')
        eol = b.index('\n', first)
        files[rel] = b[:eol + 1] + '\n#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"\n' + b[eol + 1:]

if DRY:
    print('DRY ok', sorted(files))
else:
    for rel, b in files.items():
        open(SRC + rel, 'wb').write(b.encode('utf-8'))
    print('written', sorted(files))
