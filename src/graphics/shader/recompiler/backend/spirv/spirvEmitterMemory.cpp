#include "graphics/shader/recompiler/backend/spirv/spirvEmitterInternal.h"

#include "graphics/host_gpu/renderer/cache/bufferCache.h"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <limits>
#include <vector>

namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter {
namespace {

uint32_t AndCondition(EmitterState& state, uint32_t lhs, uint32_t rhs) {
	return Binary(state, OpLogicalAnd, TypeBool(state), lhs, rhs);
}

uint32_t EmitDsMaskedLaneRead(EmitterState& state, uint32_t source, uint32_t target,
                              uint32_t exec) {
	if (state.lane_count == 2) {
		target = Binary(state, OpBitwiseAnd, TypeU32(state), target, ConstantU32(state, 31));
	}
	const auto shuffled = state.builder.AllocateId();
	state.builder.AddFunction({OpGroupNonUniformShuffle, TypeU32(state), shuffled,
	                           ConstantU32(state, ScopeSubgroup), source, target});
	const auto source_exec = state.builder.AllocateId();
	state.builder.AddFunction({OpGroupNonUniformShuffle, TypeBool(state), source_exec,
	                           ConstantU32(state, ScopeSubgroup), exec, target});
	const auto source_active =
	    AndCondition(state, source_exec, EmitSubgroupLaneActiveBool(state, target));
	return Select(state, TypeU32(state), source_active, shuffled, ConstantU32(state, 0));
}

uint32_t BufferByteAddress(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                           uint32_t index, uint32_t offset, uint32_t soffset) {
	auto&          state   = ctx.state;
	const uint32_t packed  = StorageBufferPackedStride(state, mem);
	const uint32_t stride  = packed & 0x3fffu;
	const bool     swizzle = stride != 0u && ((packed >> 14u) & 1u) != 0u;
	if (((packed >> 20u) & 1u) != 0u) {
		const auto lane = Binary(state, OpBitwiseAnd, TypeU32(state),
		                         EmitSubgroupLocalInvocationId(state), ConstantU32(state, 63));
		index           = Binary(state, OpIAdd, TypeU32(state), index, lane);
	}
	if (mem.offset != 0u) {
		offset = Binary(state, OpIAdd, TypeU32(state), offset, ConstantU32(state, mem.offset));
	}

	uint32_t address = 0;
	if (!swizzle) {
		if (stride == 0u) {
			address = offset;
		} else {
			const auto indexed = stride == 1u ? index
			                                  : Binary(state, OpIMul, TypeU32(state), index,
			                                           ConstantU32(state, stride));
			address            = Binary(state, OpIAdd, TypeU32(state), indexed, offset);
		}
	} else {
		const uint32_t stride_enum  = (packed >> 16u) & 3u;
		const uint32_t index_stride = 8u << stride_enum;
		const auto     index_msb    = Binary(state, OpShiftRightLogical, TypeU32(state), index,
		                                     ConstantU32(state, stride_enum + 3u));
		const auto     index_lsb    = Binary(state, OpBitwiseAnd, TypeU32(state), index,
		                                     ConstantU32(state, index_stride - 1u));
		const auto     offset_msb =
		    Binary(state, OpBitwiseAnd, TypeU32(state), offset, ConstantU32(state, ~3u));
		const auto offset_lsb =
		    Binary(state, OpBitwiseAnd, TypeU32(state), offset, ConstantU32(state, 3u));
		const auto indexed_msb = stride == 1u ? index_msb
		                                      : Binary(state, OpIMul, TypeU32(state), index_msb,
		                                               ConstantU32(state, stride));
		const auto msb = Binary(state, OpIMul, TypeU32(state),
		                        Binary(state, OpIAdd, TypeU32(state), indexed_msb, offset_msb),
		                        ConstantU32(state, index_stride));
		const auto lsb = Binary(
		    state, OpIAdd, TypeU32(state),
		    Binary(state, OpShiftLeftLogical, TypeU32(state), index_lsb, ConstantU32(state, 2u)),
		    offset_lsb);
		address = Binary(state, OpIAdd, TypeU32(state), msb, lsb);
	}

	const auto soffset_value = inst.Arg(3).Resolve();
	if (soffset_value.IsImmediate() && soffset_value.GetType() == IR::Type::U32 &&
	    soffset_value.U32() == 0u) {
		return address;
	}
	return Binary(state, OpIAdd, TypeU32(state), address, soffset);
}

uint32_t AddU64Low(EmitterState& state, uint32_t low, uint32_t high, uint32_t add_low,
                   uint32_t add_high, uint32_t& out_high) {
	const auto result = Binary(state, OpIAdd, TypeU32(state), low, add_low);
	const auto carry  = Binary(state, OpULessThan, TypeBool(state), result, low);
	out_high =
	    Binary(state, OpIAdd, TypeU32(state), Binary(state, OpIAdd, TypeU32(state), high, add_high),
	           Select(state, TypeU32(state), carry, ConstantU32(state, 1), ConstantU32(state, 0)));
	return result;
}

uint32_t ScratchByteAddress(ValueEmitContext& ctx, const IR::MemoryInfo& mem, uint32_t low,
                            uint32_t high) {
	auto& state     = ctx.state;
	auto  immediate = static_cast<int32_t>(mem.offset);
	const auto immediate_low  = ConstantU32(state, static_cast<uint32_t>(immediate));
	const auto immediate_high = ConstantU32(state, immediate < 0 ? UINT32_MAX : 0u);
	low                      = AddU64Low(state, low, high, immediate_low, immediate_high, high);
	const auto valid =
	    Binary(state, OpIEqual, TypeBool(state), high, ConstantU32(state, 0));
	return Select(state, TypeU32(state), valid, low, ConstantU32(state, UINT32_MAX));
}

uint32_t ConstantDeviceAddress(EmitterState& state, uint64_t value) {
	return state.builder.Constant(OpConstant, TypeDeviceAddress(state),
	                              {static_cast<uint32_t>(value),
	                               static_cast<uint32_t>(value >> 32u)});
}

uint32_t DeviceAddressFromWords(EmitterState& state, uint32_t low, uint32_t high) {
	const auto low64  = Unary(state, OpUConvert, TypeDeviceAddress(state), low);
	const auto high64 = Binary(state, OpShiftLeftLogical, TypeDeviceAddress(state),
	                           Unary(state, OpUConvert, TypeDeviceAddress(state), high),
	                           ConstantDeviceAddress(state, 32));
	return Binary(state, OpBitwiseOr, TypeDeviceAddress(state), low64, high64);
}

uint32_t ImmediateAddress(EmitterState& state, uint32_t address, int32_t immediate) {
	return immediate == 0
	           ? address
	           : Binary(state, OpIAdd, TypeDeviceAddress(state), address,
	                    ConstantDeviceAddress(state,
	                                          static_cast<uint64_t>(static_cast<int64_t>(immediate))));
}

uint32_t GuestAddress(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	auto& state = ctx.state;
	auto  low   = ctx.Arg(inst, 1);
	if (mem.kind == IR::ResourceKind::ScalarAddress) {
		low = Binary(state, OpBitwiseAnd, TypeU32(state), low, ConstantU32(state, ~3u));
	}
	uint32_t address = 0;
	if (mem.address_is_full) {
		address = DeviceAddressFromWords(state, low, ctx.Arg(inst, 2));
	} else {
		const auto* handle = inst.Arg(0).Resolve().TryInstruction();
		if (handle == nullptr || handle->GetOpcode() != IR::ValueOpcode::GetAddressResource ||
		    handle->NumArgs() != 2) {
			ctx.Fail(inst, "has no address base pair");
			return ConstantDeviceAddress(state, 0);
		}
		const auto base = DeviceAddressFromWords(state, ctx.Arg(*handle, 0), ctx.Arg(*handle, 1));
		address = Binary(state, OpIAdd, TypeDeviceAddress(state), base,
		                 Unary(state, OpUConvert, TypeDeviceAddress(state), low));
	}
	auto immediate = static_cast<int32_t>(mem.offset);
	if (mem.kind == IR::ResourceKind::ScalarAddress) {
		immediate = static_cast<int32_t>(static_cast<uint32_t>(immediate) & ~3u);
	}
	return immediate == 0
	           ? address
	           : Binary(state, OpIAdd, TypeDeviceAddress(state), address,
	                    ConstantDeviceAddress(state,
	                                          static_cast<uint64_t>(static_cast<int64_t>(immediate))));
}

uint32_t FaultElementPointer(EmitterState& state, uint32_t index) {
	const auto pointer = state.builder.AllocateId();
	state.builder.AddFunction({OpAccessChain, TypeStorageBufferElementPointer(state), pointer,
	                           state.fault_buffer_variable, ConstantU32(state, 0), index});
	return pointer;
}

void RecordBdaFault(EmitterState& state, uint32_t page) {
	const auto word = Binary(state, OpShiftRightLogical, TypeU32(state), page,
	                         ConstantU32(state, 5));
	const auto bit = Binary(
	    state, OpShiftLeftLogical, TypeU32(state), ConstantU32(state, 1),
	    Binary(state, OpBitwiseAnd, TypeU32(state), page, ConstantU32(state, 31)));
	const auto pointer = FaultElementPointer(state, word);
	const auto value   = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, TypeU32(state), value, pointer});
	state.builder.AddFunction(
	    {OpStore, pointer, Binary(state, OpBitwiseOr, TypeU32(state), value, bit)});
}

uint32_t GetBdaPointer(ValueEmitContext& ctx, uint32_t address, uint32_t active = 0) {
	auto&      state  = ctx.state;
	const auto result = state.builder.AllocateId();
	if (BdaNullPageEnabled()) {
		if (active == 0) {
			active = ConstantBool(state, true);
		}
		state.builder.AddFunction({OpFunctionCall, TypeDeviceAddress(state), result,
		                           state.bda_pointer_function, address, active});
		return result;
	}
	state.builder.AddFunction(
	    {OpFunctionCall, TypeDeviceAddress(state), result, state.bda_pointer_function, address});
	return result;
}

uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer);

uint32_t LoadBdaDword(ValueEmitContext& ctx, uint32_t address) {
	auto&      state   = ctx.state;
	const auto bda     = GetBdaPointer(ctx, address);
	if (BdaNullPageEnabled()) {
		return LoadBdaAt(ctx, bda);
	}
	const auto present = Binary(state, OpINotEqual, TypeBool(state), bda,
	                            ConstantDeviceAddress(state, 0));
	return EmitValueOrZeroIfCondition(state, present, [&]() {
		const auto pointer = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpConvertUToPtr, TypePhysicalU32Pointer(state), pointer, bda});
		const auto value = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpLoad, TypeU32(state), value, pointer, MemoryAccessAlignedMask, sizeof(uint32_t)});
		return value;
	});
}

uint32_t LoadBdaAt(ValueEmitContext& ctx, uint32_t pointer) {
	auto& state = ctx.state;
	if (BdaNullPageEnabled()) {
		const auto typed = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpConvertUToPtr, TypePhysicalU32Pointer(state), typed, pointer});
		const auto value = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpLoad, TypeU32(state), value, typed, MemoryAccessAlignedMask, sizeof(uint32_t)});
		return value;
	}
	const auto present = Binary(state, OpINotEqual, TypeBool(state), pointer,
	                            ConstantDeviceAddress(state, 0));
	return EmitValueOrZeroIfCondition(state, present, [&]() {
		const auto typed = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpConvertUToPtr, TypePhysicalU32Pointer(state), typed, pointer});
		const auto value = state.builder.AllocateId();
		state.builder.AddFunction(
		    {OpLoad, TypeU32(state), value, typed, MemoryAccessAlignedMask, sizeof(uint32_t)});
		return value;
	});
}

// Scalar dword load from a pointer (S_LOAD_DWORDXn with an SGPR address). The ISA ignores the low
// two address bits, so the value never straddles dwords; and the dwords of one instruction share
// the page lookup: the page pointer of the first dword plus the immediate serves the others while
// the offset stays inside the page (a compare), otherwise a full lookup runs. ASTRO BOT's tiled
// lighting shader reads its light records this way inside the per-light loop (~300 dwords): the
// generic path cost two lookups, two loads and a shift-merge per dword.
uint32_t LoadScalarBda(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                       bool use_cache) {
	auto&       state  = ctx.state;
	const auto* handle = inst.Arg(0).Resolve().TryInstruction();
	const auto  imm    = static_cast<uint32_t>(static_cast<int32_t>(mem.offset)) & ~3u;
	if (!use_cache || mem.address_is_full || handle == nullptr ||
	    handle->GetOpcode() != IR::ValueOpcode::GetAddressResource || handle->NumArgs() != 2 ||
	    imm + sizeof(uint32_t) > BufferCache::CACHING_PAGESIZE) {
		const auto address = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state),
		                            GuestAddress(ctx, inst, mem),
		                            ConstantDeviceAddress(state, ~uint64_t {3}));
		return LoadBdaAt(ctx, GetBdaPointer(ctx, address));
	}
	const auto low   = ctx.Arg(inst, 1);
	auto&      cache = state.scalar_bda;
	if (cache.handle != handle || cache.low != low || cache.block != ctx.state.current_block) {
		const auto base = DeviceAddressFromWords(state, ctx.Arg(*handle, 0), ctx.Arg(*handle, 1));
		const auto masked_low =
		    Binary(state, OpBitwiseAnd, TypeU32(state), low, ConstantU32(state, ~3u));
		auto address = Binary(state, OpIAdd, TypeDeviceAddress(state), base,
		                      Unary(state, OpUConvert, TypeDeviceAddress(state), masked_low));
		address      = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state), address,
		                      ConstantDeviceAddress(state, ~uint64_t {3}));
		cache.handle   = handle;
		cache.low      = low;
		cache.block    = ctx.state.current_block;
		cache.address  = address;
		cache.page_ptr = GetBdaPointer(ctx, address);
	}
	if (imm == 0) {
		return LoadBdaAt(ctx, cache.page_ptr);
	}
	const auto page_offset =
	    Binary(state, OpBitwiseAnd, TypeDeviceAddress(state), cache.address,
	           ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - 1));
	const auto in_page = Binary(
	    state, OpULessThanEqual, TypeBool(state), page_offset,
	    ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - sizeof(uint32_t) - imm));
	const auto have_page = Binary(state, OpINotEqual, TypeBool(state), cache.page_ptr,
	                              ConstantDeviceAddress(state, 0));
	const auto fast      = Binary(state, OpLogicalAnd, TypeBool(state), in_page, have_page);
	const auto fast_label  = state.builder.AllocateId();
	const auto slow_label  = state.builder.AllocateId();
	const auto slow_exit   = state.builder.AllocateId();
	const auto merge_label = state.builder.AllocateId();
	state.builder.AddFunction({OpSelectionMerge, merge_label, SelectionControlNone});
	state.builder.AddFunction({OpBranchConditional, fast, fast_label, slow_label});
	EmitLabel(state, fast_label);
	const auto fast_ptr = Binary(state, OpIAdd, TypeDeviceAddress(state), cache.page_ptr,
	                             ConstantDeviceAddress(state, imm));
	state.builder.AddFunction({OpBranch, merge_label});
	EmitLabel(state, slow_label);
	const auto slow_ptr =
	    GetBdaPointer(ctx, Binary(state, OpIAdd, TypeDeviceAddress(state), cache.address,
	                              ConstantDeviceAddress(state, imm)));
	state.builder.AddFunction({OpBranch, slow_exit});
	EmitLabel(state, slow_exit);
	state.builder.AddFunction({OpBranch, merge_label});
	EmitLabel(state, merge_label);
	const auto pointer = state.builder.AllocateId();
	state.builder.AddFunction({OpPhi, TypeDeviceAddress(state), pointer, fast_ptr, fast_label,
	                           slow_ptr, slow_exit});
	return LoadBdaAt(ctx, pointer);
}


// S_BUFFER_LOAD_DWORDXn as one vector load. The translator split it into n ReadConstBuffer
// dwords with the same resource and SGPR offset and immediates imm, imm+4, ...; each one cost an
// access chain, a load and (robustBufferAccess2) a driver bounds check. When the V# base
// (specialization class), the SGPR offset (static analysis of its definition) and the chunk start
// are 16- (8-) byte aligned, the dwords of one 16- (8-) byte chunk load as one uvec4 (uvec2)
// through the aliased view of the descriptor array. Members are defined eagerly and skipped through
// ctx.grouped_loads. Returns the value of `inst`, or 0 when the scalar path must be used.
namespace {

uint32_t LowestSetAlignment(uint32_t value) {
	return value == 0u ? 16u : std::min(16u, value & (0u - value));
}

// Power-of-two alignment (1..16) provably held by a byte-offset value; unknown = 1.
uint32_t KnownOffsetAlignment(IR::Value value, uint32_t depth) {
	value = value.Resolve();
	if (value.IsImmediate()) {
		return value.GetType() == IR::Type::U32 ? LowestSetAlignment(value.U32()) : 1u;
	}
	const auto* def = value.TryInstruction();
	if (def == nullptr || depth > 8u) {
		return 1u;
	}
	const auto immediate = [](IR::Value v, uint32_t& out) {
		v = v.Resolve();
		if (v.IsImmediate() && v.GetType() == IR::Type::U32) {
			out = v.U32();
			return true;
		}
		return false;
	};
	uint32_t constant = 0;
	switch (def->GetOpcode()) {
		case IR::ValueOpcode::IAdd32:
		case IR::ValueOpcode::ISub32:
		case IR::ValueOpcode::BitwiseOr32:
			return std::min(KnownOffsetAlignment(def->Arg(0), depth + 1u),
			                KnownOffsetAlignment(def->Arg(1), depth + 1u));
		case IR::ValueOpcode::IMul32:
			if (immediate(def->Arg(1), constant)) {
				return std::min(16u, KnownOffsetAlignment(def->Arg(0), depth + 1u) *
				                         LowestSetAlignment(constant));
			}
			if (immediate(def->Arg(0), constant)) {
				return std::min(16u, KnownOffsetAlignment(def->Arg(1), depth + 1u) *
				                         LowestSetAlignment(constant));
			}
			return 1u;
		case IR::ValueOpcode::ShiftLeftLogical32:
			if (immediate(def->Arg(1), constant)) {
				return std::min(16u, KnownOffsetAlignment(def->Arg(0), depth + 1u)
				                         << std::min(constant, 4u));
			}
			return 1u;
		case IR::ValueOpcode::BitwiseAnd32:
			if (immediate(def->Arg(1), constant)) {
				return std::max(KnownOffsetAlignment(def->Arg(0), depth + 1u),
				                LowestSetAlignment(constant));
			}
			if (immediate(def->Arg(0), constant)) {
				return std::max(KnownOffsetAlignment(def->Arg(1), depth + 1u),
				                LowestSetAlignment(constant));
			}
			return std::max(KnownOffsetAlignment(def->Arg(0), depth + 1u),
			                KnownOffsetAlignment(def->Arg(1), depth + 1u));
		case IR::ValueOpcode::SelectU32:
			return std::min(KnownOffsetAlignment(def->Arg(1), depth + 1u),
			                KnownOffsetAlignment(def->Arg(2), depth + 1u));
		default: return 1u;
	}
}

bool VectorConstTrace() {
	static const bool enabled = std::getenv("KYTY_VEC_CONST_TRACE") != nullptr;
	return enabled;
}

} // namespace

uint32_t LoadConstBufferVector(ValueEmitContext& ctx, const IR::Inst& inst,
                               const IR::MemoryInfo& mem) {
	auto& state = ctx.state;
	if (!VectorConstLoadsEnabled() || !RobustLoadsEnabled() || ctx.state.current_block == nullptr ||
	    inst.NumArgs() != 2u || mem.data_bits != 32u || mem.data_dwords != 1u ||
	    (mem.offset & 3u) != 0u || mem.resource >= state.program.info.buffers.size()) {
		return 0u;
	}
	const auto offset_value = inst.Arg(1).Resolve();
	const bool runtime_base = VectorConstRuntimeAlignment();
	const auto alignment    = std::min(
	    runtime_base
	        ? 16u
	        : IR::PackedStrideBaseAlignment(state.program.info.buffers[mem.resource].packed_stride),
	    KnownOffsetAlignment(offset_value, 0u));
	if (alignment < 8u) {
		if (VectorConstTrace()) {
			LOGF("VecConst: scalar pc=0x%x res=%u imm=%u base_align=%u offset_align=%u\n", inst.Flags<IR::MemoryFlags>().pc,
			     mem.resource,
			     mem.offset,
			     IR::PackedStrideBaseAlignment(state.program.info.buffers[mem.resource].packed_stride),
			     KnownOffsetAlignment(offset_value, 0u));
		}
		return 0u;
	}
	struct Member {
		const IR::Inst* inst   = nullptr;
		uint32_t        offset = 0;
	};
	std::vector<Member> members;
	members.push_back({&inst, mem.offset});
	bool     seen    = false;
	uint32_t scanned = 0;
	for (const auto& other: *ctx.state.current_block) {
		if (!seen) {
			seen = &other == &inst;
			continue;
		}
		if (++scanned > 96u) {
			break;
		}
		if (other.GetOpcode() != IR::ValueOpcode::ReadConstBuffer || other.NumArgs() != 2u ||
		    ctx.grouped_loads.contains(&other)) {
			continue;
		}
		const auto& other_mem = ctx.Memory(other);
		if (other_mem.resource != mem.resource || other_mem.planning_only ||
		    other_mem.data_bits != 32u || other_mem.data_dwords != 1u ||
		    (other_mem.offset & 3u) != 0u || !(other.Arg(1).Resolve() == offset_value)) {
			continue;
		}
		members.push_back({&other, other_mem.offset});
	}
	if (members.size() < 2u) {
		if (VectorConstTrace()) {
			LOGF("VecConst: single pc=0x%x res=%u imm=%u align=%u\n", inst.Flags<IR::MemoryFlags>().pc, mem.resource,
			     mem.offset, alignment);
		}
		return 0u;
	}
	for (uint32_t width = std::min(alignment, 16u); width >= 8u; width /= 2u) {
		const uint32_t  start      = mem.offset & ~(width - 1u);
		const uint32_t  components = width / 4u;
		const IR::Inst* slots[4]   = {};
		uint32_t        present    = 0;
		for (const auto& member: members) {
			if (member.offset >= start && member.offset < start + width) {
				auto& slot = slots[(member.offset - start) / 4u];
				if (slot == nullptr) {
					slot = member.inst;
					present++;
				}
			}
		}
		const bool bank     = UsesConstBank(state, mem.resource);
		const auto variable = bank ? (components == 4u ? state.const_buffer_u32x4_variable
		                                               : state.const_buffer_u32x2_variable)
		                           : (components == 4u ? state.storage_buffer_u32x4_variable
		                                               : state.storage_buffer_u32x2_variable);
		if (present < 2u || variable == 0u) {
			continue;
		}
		const auto pointer = state.builder.AllocateId();
		// Bound-range adjustment (uniform push data): base % StorageMinAlignment. Static mode: a
		// multiple of the specialized base alignment (the host checks it); run-time mode: tested
		// below.
		uint32_t             byte_offset = 0;
		uint32_t             slot        = 0;
		MemoryResourceAccess scalar_access {};
		const auto           chunk = Binary(state, OpIAdd, TypeU32(state), ctx.Arg(inst, 1),
		                                    ConstantU32(state, start));
		if (bank) {
			// Uniform-buffer path: cbuffers_u32xN[slot].data[byte / width]; no bounds check
			// (robustBufferAccess2 zero-fills past the bound V# range like S_BUFFER_LOAD).
			slot = ResourceForDescriptor(state, IR::DescriptorBindingKind::ConstBuffers, mem.resource);
			const auto buffer_slot =
			    ResourceForDescriptor(state, IR::DescriptorBindingKind::Buffers, mem.resource);
			byte_offset      = state.memory_byte_offsets[buffer_slot];
			const auto byte  = Binary(state, OpIAdd, TypeU32(state), chunk, byte_offset);
			const auto index = Binary(state, OpShiftRightLogical, TypeU32(state), byte,
			                          ConstantU32(state, components == 4u ? 4u : 3u));
			state.builder.AddFunction({OpAccessChain, TypeUniformElementPointer(state, components),
			                           pointer, variable, ConstantU32(state, slot),
			                           ConstantU32(state, 0), index});
		} else {
			const auto access = PrepareStorageBufferResourceAccess(
			    state, mem, variable, TypeStorageBufferU32VectorPointer(state, components));
			byte_offset      = access.byte_offset;
			const auto byte  = Binary(state, OpIAdd, TypeU32(state), chunk, byte_offset);
			const auto index = Binary(state, OpShiftRightLogical, TypeU32(state), byte,
			                          ConstantU32(state, components == 4u ? 4u : 3u));
			state.builder.AddFunction({OpAccessChain,
			                           TypeStorageBufferU32VectorElementPointer(state, components),
			                           pointer, access.object_pointer, ConstantU32(state, 0), index});
			if (runtime_base) {
				scalar_access = PrepareMemoryResourceAccess(state, mem);
			}
		}
		if (runtime_base) {
			// Run-time base alignment: `aligned` is uniform (push data), so this is a uniform
			// branch: one vector load, or one dword load per member when the base is not aligned.
			const auto aligned = Binary(
			    state, OpIEqual, TypeBool(state),
			    Binary(state, OpBitwiseAnd, TypeU32(state), byte_offset, ConstantU32(state, width - 1u)),
			    ConstantU32(state, 0));
			const auto fast_label  = state.builder.AllocateId();
			const auto slow_label  = state.builder.AllocateId();
			const auto merge_label = state.builder.AllocateId();
			state.builder.AddFunction({OpSelectionMerge, merge_label, SelectionControlNone});
			state.builder.AddFunction({OpBranchConditional, aligned, fast_label, slow_label});
			EmitLabel(state, fast_label);
			const auto vector = state.builder.AllocateId();
			state.builder.AddFunction({OpLoad, TypeU32Vector(state, components), vector, pointer});
			uint32_t fast_values[4] = {};
			for (uint32_t component = 0; component < components; component++) {
				if (slots[component] == nullptr) {
					continue;
				}
				fast_values[component] = state.builder.AllocateId();
				state.builder.AddFunction({OpCompositeExtract, TypeU32(state), fast_values[component],
				                           vector, component});
			}
			const auto fast_exit = state.current_label;
			state.builder.AddFunction({OpBranch, merge_label});
			EmitLabel(state, slow_label);
			uint32_t slow_values[4] = {};
			for (uint32_t component = 0; component < components; component++) {
				if (slots[component] == nullptr) {
					continue;
				}
				const auto byte = Binary(state, OpIAdd, TypeU32(state), chunk,
				                         Binary(state, OpIAdd, TypeU32(state), byte_offset,
				                                ConstantU32(state, component * 4u)));
				const auto element =
				    Binary(state, OpShiftRightLogical, TypeU32(state), byte, ConstantU32(state, 2));
				const auto dword_ptr = state.builder.AllocateId();
				if (bank) {
					state.builder.AddFunction({OpAccessChain, TypeUniformElementPointer(state, 1u),
					                           dword_ptr, state.const_buffer_variable,
					                           ConstantU32(state, slot), ConstantU32(state, 0), element});
				} else {
					// The bound range already includes the adjustment: index from the object base.
					state.builder.AddFunction({OpAccessChain, TypeStorageBufferElementPointer(state),
					                           dword_ptr, scalar_access.object_pointer,
					                           ConstantU32(state, 0), element});
				}
				slow_values[component] = state.builder.AllocateId();
				state.builder.AddFunction({OpLoad, TypeU32(state), slow_values[component], dword_ptr});
			}
			const auto slow_exit = state.current_label;
			state.builder.AddFunction({OpBranch, merge_label});
			EmitLabel(state, merge_label);
			if (VectorConstTrace()) {
				LOGF("VecConst: group pc=0x%x res=%u start=%u width=%u present=%u members=%zu align=%u bank=%u runtime\n",
				     inst.Flags<IR::MemoryFlags>().pc, mem.resource, start, width, present, members.size(),
				     alignment, bank ? 1u : 0u);
			}
			uint32_t result = 0;
			for (uint32_t component = 0; component < components; component++) {
				const auto* member = slots[component];
				if (member == nullptr) {
					continue;
				}
				const auto value = state.builder.AllocateId();
				state.builder.AddFunction({OpPhi, TypeU32(state), value, fast_values[component], fast_exit,
				                           slow_values[component], slow_exit});
				const auto hinted = UniformHint(state, TypeU32(state), value);
				if (member == &inst) {
					result = hinted;
				} else {
					ctx.Define(*member, hinted);
					ctx.grouped_loads.insert(member);
				}
			}
			return result;
		}
		const auto vector = state.builder.AllocateId();
		state.builder.AddFunction({OpLoad, TypeU32Vector(state, components), vector, pointer});
		if (VectorConstTrace()) {
			LOGF("VecConst: group pc=0x%x res=%u start=%u width=%u present=%u members=%zu align=%u bank=%u\n",
			     inst.Flags<IR::MemoryFlags>().pc, mem.resource, start, width, present, members.size(), alignment,
			     bank ? 1u : 0u);
		}
		uint32_t result = 0;
		for (uint32_t component = 0; component < components; component++) {
			const auto* member = slots[component];
			if (member == nullptr) {
				continue;
			}
			const auto value = state.builder.AllocateId();
			state.builder.AddFunction({OpCompositeExtract, TypeU32(state), value, vector, component});
			const auto hinted = UniformHint(state, TypeU32(state), value);
			if (member == &inst) {
				result = hinted;
			} else {
				ctx.Define(*member, hinted);
				ctx.grouped_loads.insert(member);
			}
		}
		return result;
	}
	return 0u;
}

// Grouped scalar pointer loads. The translator splits S_LOAD_DWORDXn into n dword loads with the
// same base V# and SGPR offset and immediates imm, imm+4, ...; each one cost a page lookup. Here
// the first member looks the page up once and the others load at page_ptr + delta, behind a
// uniform "the group stays inside the page" check (else: per-dword lookups). Members are
// defined eagerly; their own emission is skipped through ctx.grouped_loads. Null-page mode only
// (loads are unconditional there). Returns the value of `inst`.
bool ScalarGroupTrace() {
	static const bool enabled = std::getenv("KYTY_SCALAR_GROUP_TRACE") != nullptr;
	return enabled;
}

bool ScalarGroupEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_SCALAR_GROUP");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

uint32_t LoadScalarBdaGroup(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                            uint32_t active_id) {
	auto&       state  = ctx.state;
	const auto* handle = inst.Arg(0).Resolve().TryInstruction();
	const auto  low    = inst.Arg(1).Resolve();
	const auto  active = inst.Arg(inst.NumArgs() - 1).Resolve();
	struct Member {
		const IR::Inst* inst   = nullptr;
		int32_t         offset = 0;
	};
	std::vector<Member> members;
	members.push_back({&inst, static_cast<int32_t>(mem.offset) & ~3});
	if (ctx.state.current_block != nullptr) {
		bool     seen  = false;
		uint32_t scanned = 0;
		for (const auto& other: *ctx.state.current_block) {
			if (!seen) {
				seen = &other == &inst;
				continue;
			}
			if (++scanned > 96u) {
				break;
			}
			if (other.GetOpcode() != inst.GetOpcode() || other.NumArgs() != inst.NumArgs() ||
			    ctx.grouped_loads.contains(&other)) {
				continue;
			}
			const auto& other_mem = ctx.Memory(other);
			if (other_mem.kind != IR::ResourceKind::ScalarAddress || other_mem.address_is_full ||
			    other.Arg(0).Resolve().TryInstruction() != handle ||
			    !(other.Arg(1).Resolve() == low) ||
			    !(other.Arg(other.NumArgs() - 1).Resolve() == active)) {
				if (ScalarGroupTrace()) {
					LOGF("ScalarGroup: reject kind=%d full=%d handle=%d low=%d active=%d off=%d/%d\n",
					     static_cast<int>(other_mem.kind), other_mem.address_is_full ? 1 : 0,
					     other.Arg(0).Resolve().TryInstruction() == handle ? 1 : 0,
					     other.Arg(1).Resolve() == low ? 1 : 0,
					     other.Arg(other.NumArgs() - 1).Resolve() == active ? 1 : 0,
					     static_cast<int>(other_mem.offset), static_cast<int>(mem.offset));
				}
				continue;
			}
			members.push_back({&other, static_cast<int32_t>(other_mem.offset) & ~3});
		}
	}
	if (ScalarGroupTrace()) {
		LOGF("ScalarGroup: members=%zu first_off=%d\n", members.size(), static_cast<int>(mem.offset));
	}
	int32_t imm_min = members[0].offset;
	int32_t imm_max = members[0].offset;
	for (const auto& member: members) {
		imm_min = std::min(imm_min, member.offset);
		imm_max = std::max(imm_max, member.offset);
	}
	// Keep the group within one page window; drop the far members otherwise.
	{
		std::vector<Member> kept;
		for (const auto& member: members) {
			if (static_cast<int64_t>(member.offset) - imm_min + 4 <=
			    static_cast<int64_t>(BufferCache::CACHING_PAGESIZE)) {
				kept.push_back(member);
			}
		}
		members.swap(kept);
		imm_max = imm_min;
		for (const auto& member: members) {
			imm_max = std::max(imm_max, member.offset);
		}
	}
	const auto type       = TypeDeviceAddress(state);
	const auto base       = DeviceAddressFromWords(state, ctx.Arg(*handle, 0), ctx.Arg(*handle, 1));
	const auto masked_low = Binary(state, OpBitwiseAnd, TypeU32(state), ctx.Arg(inst, 1),
	                               ConstantU32(state, ~3u));
	auto address = Binary(state, OpIAdd, type, base, Unary(state, OpUConvert, type, masked_low));
	address      = Binary(state, OpBitwiseAnd, type, address, ConstantDeviceAddress(state, ~uint64_t {3}));
	address      = Binary(state, OpIAdd, type, address,
	                      ConstantDeviceAddress(state, static_cast<uint64_t>(static_cast<int64_t>(imm_min))));
	const auto page_ptr = GetBdaPointer(ctx, address, active_id);
	std::vector<uint32_t> values(members.size(), 0u);
	if (members.size() == 1u) {
		values[0] = LoadBdaAt(ctx, page_ptr);
	} else {
		const auto span = static_cast<uint64_t>(imm_max - imm_min) + sizeof(uint32_t);
		const auto page_offset = Binary(state, OpBitwiseAnd, type, address,
		                                ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - 1));
		const auto fits = Binary(state, OpULessThanEqual, TypeBool(state), page_offset,
		                         ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - span));
		const auto fast_label  = state.builder.AllocateId();
		const auto slow_label  = state.builder.AllocateId();
		const auto merge_label = state.builder.AllocateId();
		state.builder.AddFunction({OpSelectionMerge, merge_label, SelectionControlNone});
		state.builder.AddFunction({OpBranchConditional, fits, fast_label, slow_label});
		EmitLabel(state, fast_label);
		std::vector<uint32_t> fast_values;
		for (const auto& member: members) {
			const auto delta = static_cast<uint64_t>(member.offset - imm_min);
			const auto ptr   = delta == 0 ? page_ptr
			                              : Binary(state, OpIAdd, type, page_ptr,
			                                       ConstantDeviceAddress(state, delta));
			fast_values.push_back(LoadBdaAt(ctx, ptr));
		}
		const auto fast_exit = state.current_label;
		state.builder.AddFunction({OpBranch, merge_label});
		EmitLabel(state, slow_label);
		std::vector<uint32_t> slow_values;
		for (const auto& member: members) {
			const auto delta = static_cast<uint64_t>(member.offset - imm_min);
			const auto addr  = delta == 0 ? address
			                              : Binary(state, OpIAdd, type, address,
			                                       ConstantDeviceAddress(state, delta));
			slow_values.push_back(LoadBdaAt(ctx, GetBdaPointer(ctx, addr, active_id)));
		}
		const auto slow_exit = state.current_label;
		state.builder.AddFunction({OpBranch, merge_label});
		EmitLabel(state, merge_label);
		for (size_t i = 0; i < members.size(); i++) {
			values[i] = state.builder.AllocateId();
			state.builder.AddFunction({OpPhi, TypeU32(state), values[i], fast_values[i], fast_exit,
			                           slow_values[i], slow_exit});
		}
	}
	for (size_t i = 1; i < members.size(); i++) {
		const auto masked = active_id == 0 ? values[i]
		                                   : Select(state, TypeU32(state), active_id, values[i],
		                                            ConstantU32(state, 0));
		ctx.Define(*members[i].inst, masked);
		ctx.grouped_loads.insert(members[i].inst);
	}
	return values[0];
}

// One dword of a Flat load at a 64-bit address in null-page mode: the aligned dword loads
// unconditionally (inactive lanes read a valid page too and get masked by the caller); only the
// rare dword-crossing second load keeps a branch. Returns the unmasked value.
uint32_t LoadFlatDwordNullPage(ValueEmitContext& ctx, uint32_t address, uint32_t active_id,
                               uint32_t bits) {
	auto&      state   = ctx.state;
	const auto aligned = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state), address,
	                            ConstantDeviceAddress(state, ~uint64_t {3}));
	const auto first   = LoadBdaAt(ctx, GetBdaPointer(ctx, aligned, active_id));
	const auto byte    = Binary(state, OpBitwiseAnd, TypeU32(state),
	                            Unary(state, OpUConvert, TypeU32(state), address),
	                            ConstantU32(state, 3));
	uint32_t value = first;
	if (bits != 8u) {
		const auto crosses = Binary(state, bits == 16u ? OpUGreaterThan : OpINotEqual,
		                            TypeBool(state), byte,
		                            ConstantU32(state, bits == 16u ? 2u : 0u));
		const auto second = EmitValueOrZeroIfCondition(state, crosses, [&]() {
			return LoadBdaAt(
			    ctx, GetBdaPointer(ctx,
			                       Binary(state, OpIAdd, TypeDeviceAddress(state), aligned,
			                              ConstantDeviceAddress(state, sizeof(uint32_t))),
			                       active_id));
		});
		const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
		                          ConstantU32(state, 3));
		const auto upper_shift = Binary(
		    state, OpShiftLeftLogical, TypeU32(state),
		    Binary(state, OpBitwiseAnd, TypeU32(state),
		           Binary(state, OpISub, TypeU32(state), ConstantU32(state, 4), byte),
		           ConstantU32(state, 3)),
		    ConstantU32(state, 3));
		value = Binary(state, OpBitwiseOr, TypeU32(state),
		               Binary(state, OpShiftRightLogical, TypeU32(state), first, shift),
		               Binary(state, OpShiftLeftLogical, TypeU32(state), second, upper_shift));
	} else {
		const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
		                          ConstantU32(state, 3));
		value = Binary(state, OpShiftRightLogical, TypeU32(state), first, shift);
	}
	if (bits != 32u) {
		value = Binary(state, OpBitwiseAnd, TypeU32(state), value,
		               ConstantU32(state, bits == 8u ? 0xffu : 0xffffu));
	}
	return value;
}

// KYTY_FLAT_GROUP: 0 (default) = per-dword Flat loads at their original places; 1 = the dwords of a group
// load back to back at the first member, each through its own page lookup; 2 = two page
// lookups per group and selected pointers (A/B; run with KYTY_SHADER_CACHE=0).
uint32_t FlatGroupMode() {
	static const uint32_t mode = [] {
		const char* value = std::getenv("KYTY_FLAT_GROUP");
		// Default off: on the RenderDoc stand the grouped node loads cut 19 % of the SASS but
		// raised the register count 191 -> 246 for no time gain (BvhIntersectRay made them moot).
		return value == nullptr ? 0u : static_cast<uint32_t>(std::atoi(value));
	}();
	return mode;
}

bool FlatGroupEnabled() {
	return FlatGroupMode() != 0u;
}

// Grouped Flat dword loads at a full 64-bit address: members are the LoadAddressU32 of the same
// block with the same (handle, low, high, active) and dword-aligned immediates within one page
// window (IMAGE_BVH_INTERSECT_RAY reads 28 dwords of a node this way; the generic path cost a
// page lookup, 64-bit arithmetic and a dword-crossing branch per dword). All members are emitted
// at the first one, without branches: the RenderDoc stand showed that a fast/slow branch around
// the group loses the whole gain while any unconditional form (per-dword lookups or 128-bit
// loads) is 15-25 % faster on the tiled-lighting dispatches. Mode 2 looks the page up twice
// (aligned start and one past the last dword) and selects each dword's pointer; a dword-crossing
// (unaligned) base merges neighbouring dwords, the one past the end loaded separately.
// Null-page mode only (lookups always yield readable pointers). Members are defined eagerly
// (ctx.grouped_loads); returns the unmasked value of `inst`.
uint32_t LoadFlatBdaGroup(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                          uint32_t active_id) {
	auto&       state  = ctx.state;
	const auto  handle = inst.Arg(0).Resolve();
	const auto  low    = inst.Arg(1).Resolve();
	const auto  high   = inst.Arg(2).Resolve();
	const auto  active = inst.Arg(inst.NumArgs() - 1).Resolve();
	struct Member {
		const IR::Inst* inst   = nullptr;
		int32_t         offset = 0;
	};
	std::vector<Member> members;
	members.push_back({&inst, static_cast<int32_t>(mem.offset)});
	if (ctx.state.current_block != nullptr) {
		bool     seen    = false;
		uint32_t scanned = 0;
		for (const auto& other: *ctx.state.current_block) {
			if (!seen) {
				seen = &other == &inst;
				continue;
			}
			if (++scanned > 96u) {
				break;
			}
			if (other.GetOpcode() != inst.GetOpcode() || other.NumArgs() != inst.NumArgs() ||
			    ctx.grouped_loads.contains(&other)) {
				continue;
			}
			const auto& other_mem = ctx.Memory(other);
			if (other_mem.kind != IR::ResourceKind::Flat || !other_mem.address_is_full ||
			    (other_mem.offset & 3u) != 0u || !(other.Arg(0).Resolve() == handle) ||
			    !(other.Arg(1).Resolve() == low) || !(other.Arg(2).Resolve() == high) ||
			    !(other.Arg(other.NumArgs() - 1).Resolve() == active)) {
				continue;
			}
			const auto offset = static_cast<int32_t>(other_mem.offset);
			if (std::ranges::any_of(members, [&](const Member& m) { return m.offset == offset; })) {
				continue;
			}
			members.push_back({&other, offset});
		}
	}
	const auto type    = TypeDeviceAddress(state);
	const auto address = DeviceAddressFromWords(state, ctx.Arg(inst, 1), ctx.Arg(inst, 2));
	if (members.size() == 1u) {
		return LoadFlatDwordNullPage(ctx, ImmediateAddress(state, address, mem.offset), active_id, 32u);
	}
	int32_t imm_min = members[0].offset;
	for (const auto& member: members) {
		imm_min = std::min(imm_min, member.offset);
	}
	{
		std::vector<Member> kept;
		for (const auto& member: members) {
			if (static_cast<int64_t>(member.offset) - imm_min + 8 <=
			    static_cast<int64_t>(BufferCache::CACHING_PAGESIZE)) {
				kept.push_back(member);
			}
		}
		members.swap(kept);
	}
	std::vector<uint32_t> values(members.size(), 0u);
	if (FlatGroupMode() == 1u) {
		for (size_t i = 0; i < members.size(); i++) {
			values[i] = LoadFlatDwordNullPage(
			    ctx, ImmediateAddress(state, address, members[i].offset), active_id, 32u);
		}
	} else {
		int32_t imm_max = imm_min;
		for (const auto& member: members) {
			imm_max = std::max(imm_max, member.offset);
		}
		// span covers the members plus one dword past the end (for the unaligned merge).
		const auto span  = static_cast<uint64_t>(imm_max - imm_min) + 2u * sizeof(uint32_t);
		const auto start = Binary(state, OpBitwiseAnd, type, ImmediateAddress(state, address, imm_min),
		                          ConstantDeviceAddress(state, ~uint64_t {3}));
		const auto page0 = GetBdaPointer(ctx, start, active_id);
		const auto page1 = GetBdaPointer(
		    ctx, Binary(state, OpIAdd, type, start, ConstantDeviceAddress(state, span)), active_id);
		const auto page_offset = Binary(state, OpBitwiseAnd, type, start,
		                                ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - 1));
		const auto pointer_at = [&](uint64_t delta) {
			const auto in_first = Binary(
			    state, OpULessThan, TypeBool(state), page_offset,
			    ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - delta));
			const auto first  = delta == 0 ? page0
			                               : Binary(state, OpIAdd, type, page0,
			                                        ConstantDeviceAddress(state, delta));
			const auto second = Binary(state, OpISub, type, page1,
			                           ConstantDeviceAddress(state, span - delta));
			return Select(state, type, in_first, first, second);
		};
		// Sorted member order for the neighbour merge.
		std::vector<size_t> order(members.size());
		for (size_t i = 0; i < order.size(); i++) {
			order[i] = i;
		}
		std::ranges::sort(order,
		                  [&](size_t a, size_t b) { return members[a].offset < members[b].offset; });
		std::vector<uint32_t> raw(members.size(), 0u);
		for (size_t i = 0; i < members.size(); i++) {
			raw[i] = LoadBdaAt(ctx, pointer_at(static_cast<uint64_t>(members[i].offset - imm_min)));
		}
		const auto byte  = Binary(state, OpBitwiseAnd, TypeU32(state),
		                          Unary(state, OpUConvert, TypeU32(state),
		                                ImmediateAddress(state, address, imm_min)),
		                          ConstantU32(state, 3));
		const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
		                          ConstantU32(state, 3));
		const auto upper_shift = Binary(
		    state, OpShiftLeftLogical, TypeU32(state),
		    Binary(state, OpBitwiseAnd, TypeU32(state),
		           Binary(state, OpISub, TypeU32(state), ConstantU32(state, 4), byte),
		           ConstantU32(state, 3)),
		    ConstantU32(state, 3));
		const auto aligned = Binary(state, OpIEqual, TypeBool(state), byte, ConstantU32(state, 0));
		uint32_t   tail    = 0; // load one past the last member, shared by all who need it
		for (size_t k = 0; k < order.size(); k++) {
			const auto i    = order[k];
			uint32_t   next = 0;
			if (k + 1 < order.size() &&
			    members[order[k + 1]].offset == members[i].offset + static_cast<int32_t>(sizeof(uint32_t))) {
				next = raw[order[k + 1]];
			} else if (k + 1 == order.size()) {
				if (tail == 0) {
					tail = LoadBdaAt(ctx, pointer_at(static_cast<uint64_t>(members[i].offset - imm_min) +
					                                 sizeof(uint32_t)));
				}
				next = tail;
			} else {
				next = LoadBdaAt(ctx, pointer_at(static_cast<uint64_t>(members[i].offset - imm_min) +
				                                 sizeof(uint32_t)));
			}
			const auto merged = Binary(
			    state, OpBitwiseOr, TypeU32(state),
			    Binary(state, OpShiftRightLogical, TypeU32(state), raw[i], shift),
			    Binary(state, OpShiftLeftLogical, TypeU32(state), next, upper_shift));
			values[i] = Select(state, TypeU32(state), aligned, raw[i], merged);
		}
	}
	for (size_t i = 1; i < members.size(); i++) {
		const auto masked = active_id == 0 ? values[i]
		                                   : Select(state, TypeU32(state), active_id, values[i],
		                                            ConstantU32(state, 0));
		ctx.Define(*members[i].inst, masked);
		ctx.grouped_loads.insert(members[i].inst);
	}
	return values[0];
}

uint32_t LoadBda(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
	             uint32_t bits) {
	auto&      state         = ctx.state;
	const auto active_value  = inst.Arg(inst.NumArgs() - 1).Resolve();
	const bool always_active = active_value.IsImmediate() && active_value.U1();
	// KYTY_SCALAR_BDA=0: the generic path for scalar loads (A/B; run with KYTY_SHADER_CACHE=0,
	// the translation cache key does not include this switch).
	static const bool scalar_fast_path = [] {
		const char* value = std::getenv("KYTY_SCALAR_BDA");
		return value == nullptr || value[0] != '0';
	}();
	if (ScalarGroupTrace()) {
		const auto* handle = inst.Arg(0).Resolve().TryInstruction();
		LOGF("ScalarGroup: load kind=%d bits=%u active=%d full=%d handle_op=%d nargs=%zu off=%d" "\n",
		     static_cast<int>(mem.kind), bits, always_active ? 1 : 0, mem.address_is_full ? 1 : 0,
		     handle != nullptr ? static_cast<int>(handle->GetOpcode()) : -1,
		     handle != nullptr ? handle->NumArgs() : size_t {0}, static_cast<int>(mem.offset));
	}
	if (scalar_fast_path && mem.kind == IR::ResourceKind::ScalarAddress && bits == 32u) {
		// The shared page lookup (fast/slow branch per dword) made the NVIDIA compiler take 2.5 s
		// per tiled-lighting pipeline instead of 50 ms, for no measurable GPU gain: disabled.
		constexpr bool kSharePageLookup = false;
		if (BdaNullPageEnabled()) {
			// Every lookup yields a readable pointer, so inactive lanes load too and the
			// result is masked; the fault record honours `active`.
			const auto  active = always_active ? 0u : ctx.Arg(inst, inst.NumArgs() - 1);
			const auto* handle = inst.Arg(0).Resolve().TryInstruction();
			uint32_t    value  = 0;
			if (ScalarGroupEnabled() && !mem.address_is_full && handle != nullptr &&
			    handle->GetOpcode() == IR::ValueOpcode::GetAddressResource &&
			    handle->NumArgs() == 2) {
				value = LoadScalarBdaGroup(ctx, inst, mem, active);
			} else {
				const auto address = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state),
				                            GuestAddress(ctx, inst, mem),
				                            ConstantDeviceAddress(state, ~uint64_t {3}));
				value = LoadBdaAt(ctx, GetBdaPointer(ctx, address, active));
			}
			if (always_active) {
				return UniformHint(state, TypeU32(state), value);
			}
			return UniformHint(state, TypeU32(state),
			                   Select(state, TypeU32(state), active, value, ConstantU32(state, 0)));
		}
		if (always_active) {
			return LoadScalarBda(ctx, inst, mem, kSharePageLookup);
		}
		// Inside the activity branch the cached ids would not dominate the next dword's branch.
		return EmitValueOrZeroIfCondition(state, ctx.Arg(inst, inst.NumArgs() - 1),
		                                  [&]() { return LoadScalarBda(ctx, inst, mem, false); });
	}
	const auto address = GuestAddress(ctx, inst, mem);
	const auto active  = ctx.Arg(inst, inst.NumArgs() - 1);
	if (BdaNullPageEnabled()) {
		// Null-page mode: the aligned dword loads unconditionally (inactive lanes read a valid
		// page too and get masked); only the rare dword-crossing second load keeps a branch.
		const auto active_id = always_active ? 0u : active;
		if (bits == 32u && FlatGroupEnabled() && mem.kind == IR::ResourceKind::Flat &&
		    mem.address_is_full && (mem.offset & 3u) == 0u) {
			const auto value = LoadFlatBdaGroup(ctx, inst, mem, active_id);
			if (always_active) {
				return value;
			}
			return Select(state, TypeU32(state), active, value, ConstantU32(state, 0));
		}
		const auto aligned   = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state), address,
		                              ConstantDeviceAddress(state, ~uint64_t {3}));
		const auto first     = LoadBdaAt(ctx, GetBdaPointer(ctx, aligned, active_id));
		const auto byte      = Binary(state, OpBitwiseAnd, TypeU32(state),
		                              Unary(state, OpUConvert, TypeU32(state), address),
		                              ConstantU32(state, 3));
		uint32_t value = first;
		if (bits != 8u) {
			const auto crosses = Binary(state, bits == 16u ? OpUGreaterThan : OpINotEqual,
			                            TypeBool(state), byte,
			                            ConstantU32(state, bits == 16u ? 2u : 0u));
			const auto second = EmitValueOrZeroIfCondition(state, crosses, [&]() {
				return LoadBdaAt(
				    ctx, GetBdaPointer(ctx,
				                       Binary(state, OpIAdd, TypeDeviceAddress(state), aligned,
				                              ConstantDeviceAddress(state, sizeof(uint32_t))),
				                       active_id));
			});
			const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
			                          ConstantU32(state, 3));
			const auto upper_shift = Binary(
			    state, OpShiftLeftLogical, TypeU32(state),
			    Binary(state, OpBitwiseAnd, TypeU32(state),
			           Binary(state, OpISub, TypeU32(state), ConstantU32(state, 4), byte),
			           ConstantU32(state, 3)),
			    ConstantU32(state, 3));
			value = Binary(state, OpBitwiseOr, TypeU32(state),
			               Binary(state, OpShiftRightLogical, TypeU32(state), first, shift),
			               Binary(state, OpShiftLeftLogical, TypeU32(state), second, upper_shift));
		} else {
			const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
			                          ConstantU32(state, 3));
			value = Binary(state, OpShiftRightLogical, TypeU32(state), first, shift);
		}
		if (bits != 32u) {
			value = Binary(state, OpBitwiseAnd, TypeU32(state), value,
			               ConstantU32(state, bits == 8u ? 0xffu : 0xffffu));
		}
		if (always_active) {
			return value;
		}
		return Select(state, TypeU32(state), active, value, ConstantU32(state, 0));
	}
	return EmitValueOrZeroIfCondition(state, active, [&]() {
		const auto aligned = Binary(state, OpBitwiseAnd, TypeDeviceAddress(state), address,
		                            ConstantDeviceAddress(state, ~uint64_t {3}));
		const auto first   = LoadBdaDword(ctx, aligned);
		const auto byte = Binary(state, OpBitwiseAnd, TypeU32(state),
		                         Unary(state, OpUConvert, TypeU32(state), address),
		                         ConstantU32(state, 3));
		const auto crosses = bits == 8u
		                          ? ConstantBool(state, false)
		                          : Binary(state, bits == 16u ? OpUGreaterThan : OpINotEqual,
		                                   TypeBool(state), byte,
		                                   ConstantU32(state, bits == 16u ? 2u : 0u));
		const auto second = EmitValueOrZeroIfCondition(state, crosses, [&]() {
			return LoadBdaDword(
			    ctx, Binary(state, OpIAdd, TypeDeviceAddress(state), aligned,
			                ConstantDeviceAddress(state, sizeof(uint32_t))));
		});
		const auto shift = Binary(state, OpShiftLeftLogical, TypeU32(state), byte,
		                          ConstantU32(state, 3));
		const auto upper_shift = Binary(
		    state, OpShiftLeftLogical, TypeU32(state),
		    Binary(state, OpBitwiseAnd, TypeU32(state),
		           Binary(state, OpISub, TypeU32(state), ConstantU32(state, 4), byte),
		           ConstantU32(state, 3)),
		    ConstantU32(state, 3));
		const auto merged = Binary(
		    state, OpBitwiseOr, TypeU32(state),
		    Binary(state, OpShiftRightLogical, TypeU32(state), first, shift),
		    Binary(state, OpShiftLeftLogical, TypeU32(state), second, upper_shift));
		return bits == 32u
		           ? merged
		           : Binary(state, OpBitwiseAnd, TypeU32(state), merged,
		                    ConstantU32(state, bits == 8u ? 0xffu : 0xffffu));
	});
}

uint32_t ByteAddress(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	if (mem.kind == IR::ResourceKind::Buffer) {
		return BufferByteAddress(ctx, inst, mem, ctx.Arg(inst, 1), ctx.Arg(inst, 2),
		                         ctx.Arg(inst, 3));
	}
	if (mem.kind == IR::ResourceKind::Lds || mem.kind == IR::ResourceKind::Gds) {
		if (mem.offset == 0u) {
			return ctx.Arg(inst, 0);
		}
		return Binary(ctx.state, OpIAdd, TypeU32(ctx.state), ctx.Arg(inst, 0),
		              ConstantU32(ctx.state, mem.offset));
	}
	if (mem.kind != IR::ResourceKind::Scratch) {
		EXIT("physical address memory must use the BDA emitter\n");
	}
	return ScratchByteAddress(ctx, mem, ctx.Arg(inst, 1), ctx.Arg(inst, 2));
}

uint32_t DwordIndex(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	return Binary(ctx.state, OpShiftRightLogical, TypeU32(ctx.state), ByteAddress(ctx, inst, mem),
	              ConstantU32(ctx.state, 2));
}

struct PreparedMemoryElement {
	MemoryResourceAccess resource;
	uint32_t             index = 0;
};

PreparedMemoryElement PrepareMemoryElement(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                                           uint32_t raw_index) {
	auto       resource = PrepareMemoryResourceAccess(ctx.state, mem);
	const auto index    = EmitMemoryElementIndex(ctx.state, resource, raw_index);
	return {.resource = resource, .index = index};
}

uint32_t LoadWordInBounds(ValueEmitContext& ctx, const MemoryResourceAccess& resource,
                          uint32_t index);

uint32_t LoadSubwordInBounds(ValueEmitContext& ctx, const MemoryResourceAccess& resource,
                             uint32_t address, uint32_t index, uint32_t bits, bool sign_extend);

uint32_t LoadWordPrepared(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                          const MemoryResourceAccess& resource) {
	const auto index = EmitMemoryElementIndex(ctx.state, resource, DwordIndex(ctx, inst, mem));
	return EmitValueOrZeroIfCondition(
	    ctx.state, EmitMemoryElementInBounds(ctx.state, resource, index),
	    [&]() { return LoadWordInBounds(ctx, resource, index); });
}

uint32_t LoadWordImpl(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem);

uint32_t LoadWord(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem) {
	const auto value = LoadWordImpl(ctx, inst, mem);
	if (mem.kind == IR::ResourceKind::ScalarBuffer) {
		return UniformHint(ctx.state, TypeU32(ctx.state), value);
	}
	return value;
}

uint32_t LoadWordImpl(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem) {
	const auto active = ctx.Arg(inst, inst.NumArgs() - 1);
	if (RobustLoadsEnabled() &&
	    (mem.kind == IR::ResourceKind::Buffer || mem.kind == IR::ResourceKind::ScalarBuffer)) {
		// Inactive lanes may load too (robust range), the result is masked.
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		const auto value    = LoadWordPrepared(ctx, inst, mem, resource);
		if (active == ConstantBool(ctx.state, true)) {
			return value;
		}
		return Select(ctx.state, TypeU32(ctx.state), active, value, ConstantU32(ctx.state, 0));
	}
	return EmitValueOrZeroIfCondition(ctx.state, active, [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		return LoadWordPrepared(ctx, inst, mem, resource);
	});
}

uint32_t LoadSubwordPrepared(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                             const MemoryResourceAccess& resource, uint32_t bits,
                             bool sign_extend) {
	const auto address   = ByteAddress(ctx, inst, mem);
	const auto raw_index = Binary(ctx.state, OpShiftRightLogical, TypeU32(ctx.state), address,
	                              ConstantU32(ctx.state, 2));
	const auto index     = EmitMemoryElementIndex(ctx.state, resource, raw_index);
	return EmitValueOrZeroIfCondition(
	    ctx.state, EmitMemoryElementInBounds(ctx.state, resource, index), [&]() {
		    return LoadSubwordInBounds(ctx, resource, address, index, bits, sign_extend);
	    });
}

uint32_t LoadWordInBounds(ValueEmitContext& ctx, const MemoryResourceAccess& resource,
                          uint32_t index) {
	const auto value   = ctx.state.builder.AllocateId();
	const auto pointer = EmitMemoryElementPointer(ctx.state, resource, index);
	ctx.state.builder.AddFunction({OpLoad, TypeU32(ctx.state), value, pointer});
	return value;
}

uint32_t LoadSubwordInBounds(ValueEmitContext& ctx, const MemoryResourceAccess& resource,
                             uint32_t address, uint32_t index, uint32_t bits, bool sign_extend) {
	const auto word = LoadWordInBounds(ctx, resource, index);
	const auto byte =
	    Binary(ctx.state, OpBitwiseAnd, TypeU32(ctx.state), address, ConstantU32(ctx.state, 3));
	const auto shift =
	    Binary(ctx.state, OpShiftLeftLogical, TypeU32(ctx.state), byte, ConstantU32(ctx.state, 3));
	const auto value =
	    Binary(ctx.state, OpBitwiseAnd, TypeU32(ctx.state),
	           Binary(ctx.state, OpShiftRightLogical, TypeU32(ctx.state), word, shift),
	           ConstantU32(ctx.state, bits == 8u ? 0xffu : 0xffffu));
	if (!sign_extend) return value;
	const auto left = Binary(ctx.state, OpShiftLeftLogical, TypeU32(ctx.state), value,
	                         ConstantU32(ctx.state, 32u - bits));
	return Binary(ctx.state, OpShiftRightArithmetic, TypeU32(ctx.state), left,
	              ConstantU32(ctx.state, 32u - bits));
}

uint32_t LoadSubword(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem, uint32_t bits,
                     bool sign_extend) {
	return EmitValueOrZeroIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		return LoadSubwordPrepared(ctx, inst, mem, resource, bits, sign_extend);
	});
}

Prospero::BufferFormat BufferFormat(const ValueEmitContext& ctx, const IR::MemoryInfo& mem) {
	return mem.typed ? Format::DecodeTBufferFormat(mem.data_format, mem.number_format)
	                 : StorageBufferFormat(ctx.state, mem);
}

IR::MemoryInfo RebaseFormattedComponent(IR::MemoryInfo mem, const Format::BufferFormatInfo& info,
                                        uint32_t component) {
	mem.offset += Format::GetFormatComponentByteOffset(info, component);
	mem.data_dwords     = 1u;
	mem.component_index = component;
	return mem;
}

IR::MemoryInfo RebaseRawComponent(IR::MemoryInfo mem, uint32_t component) {
	mem.offset += component * 4u;
	mem.data_dwords     = 1u;
	mem.component_index = component;
	return mem;
}

using Format::FormattedSource;
using Format::FormattedSourceKind;

FormattedSource ResolveFormattedSource(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                                       const Format::BufferFormatInfo& info,
                                       uint32_t                        output_component) {
	if (mem.typed) {
		return output_component < info.component_count
		           ? FormattedSource {FormattedSourceKind::Memory, output_component}
		           : FormattedSource {};
	}
	const auto selector = GetDstSel(ctx.state.program.info.buffers[mem.resource].descriptor_swizzle,
	                                output_component);
	const auto source = Format::ResolveFormattedSource(info, selector);
	if (source.kind == FormattedSourceKind::Invalid) {
		ExitDescriptorBindingFailure(ctx.state, IR::DescriptorBindingKind::Buffers, mem.resource,
		                             "buffer descriptor has reserved dst_sel");
	}
	return source;
}

uint32_t FormattedConstant(ValueEmitContext& ctx, const Format::BufferFormatInfo& info,
                           FormattedSourceKind kind) {
	return ConstantU32(ctx.state, Format::FormattedConstantBits(info, kind));
}

template <typename LoadWordFn, typename LoadSubwordFn>
uint32_t LoadFormattedComponent(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                                const Format::BufferFormatInfo& info,
                                uint32_t output_component, LoadWordFn&& load_word,
                                LoadSubwordFn&& load_subword) {
	const auto source = ResolveFormattedSource(ctx, mem, info, output_component);
	if (source.kind != FormattedSourceKind::Memory) {
		return FormattedConstant(ctx, info, source.kind);
	}
	const auto component = source.component;
	const auto bits      = info.component_bits[component];
	uint32_t   raw       = 0;
	if (info.packed_bitfield) {
		raw = load_word(component);
		const auto type =
		    IsSignedFormatComponent(info.type) ? TypeI32(ctx.state) : TypeU32(ctx.state);
		const auto source_value =
		    type == TypeI32(ctx.state) ? Unary(ctx.state, OpBitcast, type, raw) : raw;
		const auto extracted = ctx.state.builder.AllocateId();
		ctx.state.builder.AddFunction(
		    {IsSignedFormatComponent(info.type) ? OpBitFieldSExtract : OpBitFieldUExtract, type,
		     extracted, source_value, ConstantU32(ctx.state, info.component_bit_offset[component]),
		     ConstantU32(ctx.state, bits)});
		raw = type == TypeI32(ctx.state)
		          ? Unary(ctx.state, OpBitcast, TypeU32(ctx.state), extracted)
		          : extracted;
	} else if (bits == 32u) {
		raw = load_word(component);
	} else {
		raw = load_subword(component, bits, IsSignedFormatComponent(info.type));
	}
	return NormalizeFormatComponent(ctx.state, info, component, raw);
}

uint32_t FormattedLoadPrepared(ValueEmitContext& ctx, const IR::Inst& inst,
                               const IR::MemoryInfo& mem, uint32_t output_component,
                               const MemoryResourceAccess& resource) {
	const auto info = Format::GetFormatInfo(BufferFormat(ctx, mem));
	if (info.type == Format::ComponentType::Unknown) {
		return LoadWordPrepared(ctx, inst, RebaseRawComponent(mem, output_component), resource);
	}
	return LoadFormattedComponent(
	    ctx, mem, info, output_component,
	    [&](uint32_t component) {
		    return LoadWordPrepared(ctx, inst, RebaseFormattedComponent(mem, info, component),
		                            resource);
	    },
	    [&](uint32_t component, uint32_t bits, bool sign_extend) {
		    return LoadSubwordPrepared(ctx, inst, RebaseFormattedComponent(mem, info, component),
		                               resource, bits, sign_extend);
	    });
}

uint32_t FormattedLoad(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	return EmitValueOrZeroIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		return FormattedLoadPrepared(ctx, inst, mem, 0u, resource);
	});
}

void StoreSubwordInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                          const MemoryResourceAccess& resource, uint32_t address, uint32_t index,
                          uint32_t bits, uint32_t data) {
	const auto pointer = EmitMemoryElementPointer(ctx.state, resource, index);
	const auto shift   = Binary(
	    ctx.state, OpShiftLeftLogical, TypeU32(ctx.state),
	    Binary(ctx.state, OpBitwiseAnd, TypeU32(ctx.state), address, ConstantU32(ctx.state, 3)),
	    ConstantU32(ctx.state, 3));
	const auto mask  = Binary(ctx.state, OpShiftLeftLogical, TypeU32(ctx.state),
	                          ConstantU32(ctx.state, bits == 8u ? 0xffu : 0xffffu), shift);
	const auto value = Binary(ctx.state, OpShiftLeftLogical, TypeU32(ctx.state),
	                          Binary(ctx.state, OpBitwiseAnd, TypeU32(ctx.state), data,
	                                 ConstantU32(ctx.state, bits == 8u ? 0xffu : 0xffffu)),
	                          shift);
	const auto merge = [&](uint32_t old) {
		return Binary(ctx.state, OpBitwiseOr, TypeU32(ctx.state),
		              Binary(ctx.state, OpBitwiseAnd, TypeU32(ctx.state), old,
		                     Unary(ctx.state, OpNot, TypeU32(ctx.state), mask)),
		              value);
	};
	if (mem.kind == IR::ResourceKind::Scratch) {
		const auto old = ctx.state.builder.AllocateId();
		ctx.state.builder.AddFunction({OpLoad, TypeU32(ctx.state), old, pointer});
		ctx.state.builder.AddFunction({OpStore, pointer, merge(old)});
	} else {
		AtomicUpdate(ctx.state, pointer, mem.kind, merge);
	}
}

void StoreSubwordPrepared(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                          const MemoryResourceAccess& resource, uint32_t bits, uint32_t data) {
	const auto address   = ByteAddress(ctx, inst, mem);
	const auto raw_index = Binary(ctx.state, OpShiftRightLogical, TypeU32(ctx.state), address,
	                              ConstantU32(ctx.state, 2));
	const auto index     = EmitMemoryElementIndex(ctx.state, resource, raw_index);
	EmitIfCondition(
	    ctx.state, EmitMemoryElementInBounds(ctx.state, resource, index), [&]() {
		    StoreSubwordInBounds(ctx, mem, resource, address, index, bits, data);
	    });
}

void StoreSubword(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem, uint32_t bits) {
	EmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		StoreSubwordPrepared(ctx, inst, mem, resource, bits, ctx.Arg(inst, inst.NumArgs() - 2));
	});
}

void StoreWordPrepared(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                       const MemoryResourceAccess& resource, uint32_t data) {
	const auto index = EmitMemoryElementIndex(ctx.state, resource, DwordIndex(ctx, inst, mem));
	EmitIfCondition(
	    ctx.state, EmitMemoryElementInBounds(ctx.state, resource, index), [&]() {
		    ctx.state.builder.AddFunction(
		        {OpStore, EmitMemoryElementPointer(ctx.state, resource, index), data});
	    });
}

void StoreWordInBounds(ValueEmitContext& ctx, const MemoryResourceAccess& resource, uint32_t index,
                       uint32_t data) {
	ctx.state.builder.AddFunction(
	    {OpStore, EmitMemoryElementPointer(ctx.state, resource, index), data});
}

void StoreWord(ValueEmitContext& ctx, const IR::Inst& inst, IR::MemoryInfo mem) {
	EmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		StoreWordPrepared(ctx, inst, mem, resource, ctx.Arg(inst, inst.NumArgs() - 2));
	});
}

void FormattedStorePrepared(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                            uint32_t component, const MemoryResourceAccess& resource,
                            uint32_t data) {
	const auto info = Format::GetFormatInfo(BufferFormat(ctx, mem));
	if (info.type == Format::ComponentType::Unknown) {
		StoreWordPrepared(ctx, inst, RebaseRawComponent(mem, component), resource, data);
		return;
	}
	if (component >= info.component_count) return;
	const auto bits          = info.component_bits[component];
	const auto component_mem = RebaseFormattedComponent(mem, info, component);
	if (bits == 8u || bits == 16u) {
		StoreSubwordPrepared(ctx, inst, component_mem, resource, bits, data);
	} else {
		StoreWordPrepared(ctx, inst, component_mem, resource, data);
	}
}

void FormattedStore(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	EmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto resource = PrepareMemoryResourceAccess(ctx.state, mem);
		FormattedStorePrepared(ctx, inst, mem, 0u, resource, ctx.Arg(inst, inst.NumArgs() - 2));
	});
}

uint32_t SpirvAtomicOpcode(IR::ValueOpcode opcode) {
	switch (opcode) {
		case IR::ValueOpcode::BufferAtomicCmpSwap32: return OpAtomicCompareExchange;
		case IR::ValueOpcode::BufferAtomicSwap32:
		case IR::ValueOpcode::BufferAtomicSwap64:
		case IR::ValueOpcode::SharedAtomicSwap32: return OpAtomicExchange;
		case IR::ValueOpcode::BufferAtomicIAdd32:
		case IR::ValueOpcode::SharedAtomicIAdd32: return OpAtomicIAdd;
		case IR::ValueOpcode::BufferAtomicISub32:
		case IR::ValueOpcode::SharedAtomicISub32: return OpAtomicISub;
		case IR::ValueOpcode::BufferAtomicSMin32:
		case IR::ValueOpcode::SharedAtomicSMin32: return OpAtomicSMin;
		case IR::ValueOpcode::BufferAtomicUMin32:
		case IR::ValueOpcode::SharedAtomicUMin32: return OpAtomicUMin;
		case IR::ValueOpcode::BufferAtomicSMax32:
		case IR::ValueOpcode::SharedAtomicSMax32: return OpAtomicSMax;
		case IR::ValueOpcode::BufferAtomicUMax32:
		case IR::ValueOpcode::SharedAtomicUMax32: return OpAtomicUMax;
		case IR::ValueOpcode::BufferAtomicAnd32:
		case IR::ValueOpcode::SharedAtomicAnd32: return OpAtomicAnd;
		case IR::ValueOpcode::BufferAtomicOr32:
		case IR::ValueOpcode::BufferAtomicOr64:
		case IR::ValueOpcode::SharedAtomicOr32: return OpAtomicOr;
		case IR::ValueOpcode::BufferAtomicXor32:
		case IR::ValueOpcode::SharedAtomicXor32: return OpAtomicXor;
		default: return 0;
	}
}

uint32_t EmitAtomicOperation(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t pointer,
                             uint32_t scope) {
	const auto old = ctx.state.builder.AllocateId();
	if (inst.GetOpcode() == IR::ValueOpcode::BufferAtomicCmpSwap32) {
		const auto desired    = ctx.Arg(inst, inst.NumArgs() - 3);
		const auto comparator = ctx.Arg(inst, inst.NumArgs() - 2);
		ctx.state.builder.AddFunction(
		    {OpAtomicCompareExchange, TypeU32(ctx.state), old, pointer, ConstantU32(ctx.state, scope),
		     ConstantU32(ctx.state, MemorySemanticsNone),
		     ConstantU32(ctx.state, MemorySemanticsNone), desired, comparator});
	} else {
		const auto value = ctx.Arg(inst, inst.NumArgs() - 2);
		ctx.state.builder.AddFunction(
		    {SpirvAtomicOpcode(inst.GetOpcode()), TypeU32(ctx.state), old, pointer,
		     ConstantU32(ctx.state, scope), ConstantU32(ctx.state, MemorySemanticsNone), value});
	}
	return old;
}

template <typename Fn>
uint32_t EmitAtomicAccess(ValueEmitContext& ctx, const IR::Inst& inst,
                          const IR::MemoryInfo& mem, Fn&& operation) {
	return EmitValueOrZeroIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto access = PrepareMemoryElement(ctx, mem, DwordIndex(ctx, inst, mem));
		return EmitValueOrZeroIfCondition(
		    ctx.state, EmitMemoryElementInBounds(ctx.state, access.resource, access.index), [&]() {
			    return operation(EmitMemoryElementPointer(ctx.state, access.resource, access.index));
		    });
	});
}

uint32_t EmitAtomic(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem) {
	return EmitAtomicAccess(ctx, inst, mem, [&](uint32_t pointer) {
		const auto scope = mem.kind == IR::ResourceKind::Lds ? ScopeWorkgroup : ScopeDevice;
		const auto old   = EmitAtomicOperation(ctx, inst, pointer, scope);
		if (mem.kind == IR::ResourceKind::Lds) {
			const auto semantics = MemorySemanticsAcquireRelease | MemorySemanticsWorkgroupMemory;
			ctx.state.builder.AddFunction({OpMemoryBarrier, ConstantU32(ctx.state, scope),
			                               ConstantU32(ctx.state, semantics)});
		} else {
			EmitDeviceAtomicMemoryBarrier(ctx.state);
		}
		return old;
	});
}

template <typename Fn>
uint32_t EmitAtomicUpdate(ValueEmitContext& ctx, const IR::Inst& inst,
                          const IR::MemoryInfo& mem, Fn&& replacement) {
	const auto value = ctx.Arg(inst, inst.NumArgs() - 2);
	return EmitAtomicAccess(ctx, inst, mem, [&](uint32_t pointer) {
		return AtomicUpdate(ctx.state, pointer, mem.kind, [&](uint32_t old) {
			return replacement(ctx.state, old, value);
		});
	});
}

uint32_t AtomicIncrement(EmitterState& state, uint32_t old, uint32_t limit) {
	// old >= limit ? 0 : old + 1 (unsigned).
	const auto wrap = Binary(state, OpUGreaterThanEqual, TypeBool(state), old, limit);
	const auto next = Binary(state, OpIAdd, TypeU32(state), old, ConstantU32(state, 1));
	return Select(state, TypeU32(state), wrap, ConstantU32(state, 0), next);
}

uint32_t AtomicDecrement(EmitterState& state, uint32_t old, uint32_t limit) {
	// old == 0 || old > limit ? limit : old - 1 (unsigned).
	const auto zero  = Binary(state, OpIEqual, TypeBool(state), old, ConstantU32(state, 0));
	const auto above = Binary(state, OpUGreaterThan, TypeBool(state), old, limit);
	const auto wrap  = Binary(state, OpLogicalOr, TypeBool(state), zero, above);
	const auto next  = Binary(state, OpISub, TypeU32(state), old, ConstantU32(state, 1));
	return Select(state, TypeU32(state), wrap, limit, next);
}

uint32_t EmitBufferAtomic64(ValueEmitContext& ctx, const IR::Inst& inst,
                            const IR::MemoryInfo& mem) {
	auto& state = ctx.state;
	return EmitValueOrDefaultIfCondition(
	    state, ctx.Arg(inst, inst.NumArgs() - 1), TypeU64(state), ConstantU64(state, 0), [&]() {
		    const auto resource = PrepareStorageBufferResourceAccess(
		        state, mem, state.storage_buffer_u64_variable, TypeStorageBufferU64Pointer(state));
		    const auto byte_address = Binary(state, OpIAdd, TypeU32(state),
		                                     ByteAddress(ctx, inst, mem), resource.byte_offset);
		    const auto index = Binary(state, OpShiftRightLogical, TypeU32(state), byte_address,
		                              ConstantU32(state, 3u));
		    return EmitValueOrDefaultIfCondition(
		        state, EmitMemoryElementInBounds(state, resource, index), TypeU64(state),
		        ConstantU64(state, 0), [&]() {
			        const auto value = Unary(state, OpBitcast, TypeScalarU64(state),
			                                 ctx.Arg(inst, inst.NumArgs() - 2));
			        const auto old   = state.builder.AllocateId();
			        state.builder.AddFunction(
			            {SpirvAtomicOpcode(inst.GetOpcode()), TypeScalarU64(state), old,
			             EmitStorageBufferElementPointer(
			                 state, resource, index, TypeStorageBufferU64ElementPointer(state)),
			             ConstantU32(state, ScopeDevice),
			             ConstantU32(state, MemorySemanticsNone), value});
			        EmitDeviceAtomicMemoryBarrier(state);
			        return Unary(state, OpBitcast, TypeU64(state), old);
		        });
	    });
}

uint32_t FloatAtomic(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                     bool max_value) {
	return EmitAtomicUpdate(ctx, inst, mem, [max_value](EmitterState& state, uint32_t old,
	                                                  uint32_t value) {
		return EmitFloatAtomicReplacement(state, old, value, max_value);
	});
}

uint32_t SharedFloatAtomic(ValueEmitContext& ctx, const IR::Inst& inst, const IR::MemoryInfo& mem,
                           bool max_value) {
	EmitIfCondition(ctx.state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto access = PrepareMemoryElement(ctx, mem, DwordIndex(ctx, inst, mem));
		EmitIfCondition(
		    ctx.state, EmitMemoryElementInBounds(ctx.state, access.resource, access.index), [&]() {
			    ctx.state.builder.AddFunction(
			        {OpStore, ctx.scratch_u32_variable, ctx.Arg(inst, 1)});
			    const auto data = ctx.state.builder.AllocateId();
			    ctx.state.builder.AddFunction(
			        {OpLoad, TypeU32(ctx.state), data, ctx.scratch_u32_variable});
			    AtomicUpdate(
			        ctx.state, EmitMemoryElementPointer(ctx.state, access.resource, access.index),
			        mem.kind, [&](uint32_t old) {
				        const auto old_f = Unary(ctx.state, OpBitcast, TypeF32(ctx.state), old);
				        const auto compare_f =
				            Unary(ctx.state, OpBitcast, TypeF32(ctx.state), ctx.Arg(inst, 2));
				        const auto data_f = Unary(ctx.state, OpBitcast, TypeF32(ctx.state), data);
				        const auto compare =
				            Binary(ctx.state, max_value ? OpFOrdGreaterThan : OpFOrdLessThan,
				                   TypeBool(ctx.state), max_value ? old_f : compare_f,
				                   max_value ? compare_f : old_f);
				        return Unary(ctx.state, OpBitcast, TypeU32(ctx.state),
				                     Select(ctx.state, TypeF32(ctx.state), compare, data_f, old_f));
			        });
		    });
	});
	return 0;
}

uint32_t AppendConsume(ValueEmitContext& ctx, const IR::Inst& inst, bool append) {
	auto&      state = ctx.state;
	if (ctx.half == 1) {
		return ctx.other_half->Def(IR::Value(const_cast<IR::Inst*>(&inst)));
	}
	const auto m0    = ctx.Arg(inst, 0);
	const auto base =
	    Binary(state, OpShiftRightLogical, TypeU32(state), m0, ConstantU32(state, 16));
	const auto size = Binary(state, OpBitwiseAnd, TypeU32(state), m0, ConstantU32(state, 0xffffu));
	const auto address =
	    Binary(state, OpIAdd, TypeU32(state), base, ConstantU32(state, ctx.Memory(inst).offset));
	const auto raw_index =
	    Binary(state, OpShiftRightLogical, TypeU32(state), address, ConstantU32(state, 2));
	const auto mem    = ctx.Memory(inst);
	const auto access = PrepareMemoryResourceAccess(state, mem);
	const auto index  = EmitMemoryElementIndex(state, access, raw_index);
	const auto exec   = ctx.Arg(inst, 1);
	const auto ballot = ctx.Ballot(inst.Arg(1));
	const auto low  = state.builder.AllocateId();
	const auto high = state.builder.AllocateId();
	state.builder.AddFunction({OpCompositeExtract, TypeU32(state), low, ballot, 0});
	state.builder.AddFunction({OpCompositeExtract, TypeU32(state), high, ballot, 1});
	const auto count =
	    Binary(state, OpIAdd, TypeU32(state), Unary(state, OpBitCount, TypeU32(state), low),
	           Unary(state, OpBitCount, TypeU32(state), high));
	const auto first       = ctx.FirstLane(ballot);
	const auto source_lane = state.lane_count == 2 ? Binary(state, OpBitwiseAnd, TypeU32(state),
	                                                        first, ConstantU32(state, 31))
	                                               : first;
	const auto is_first =
	    Binary(state, OpIEqual, TypeBool(state), EmitSubgroupLocalInvocationId(state), source_lane);
	const auto storage_bounds = EmitMemoryElementInBounds(state, access, index);
	const auto m0_bounds =
	    mem.kind == IR::ResourceKind::Gds
	        ? Binary(state, OpINotEqual, TypeBool(state), size, ConstantU32(state, 0))
	        : Binary(state, OpULessThan, TypeBool(state),
	                 ConstantU32(state, ctx.Memory(inst).offset + 3u), size);
	const auto condition = AndCondition(
	    state, is_first,
	    AndCondition(state,
	                 state.lane_count == 2
	                     ? Binary(state, OpINotEqual, TypeBool(state), count, ConstantU32(state, 0))
	                     : exec,
	                 AndCondition(state, storage_bounds, m0_bounds)));
	const auto atomic = EmitValueOrZeroIfCondition(state, condition, [&]() {
		const auto value = state.builder.AllocateId();
		state.builder.AddFunction(
		    {append ? OpAtomicIAdd : OpAtomicISub, TypeU32(state), value,
		     EmitMemoryElementPointer(state, access, index),
		     ConstantU32(state, mem.kind == IR::ResourceKind::Gds ? ScopeDevice : ScopeWorkgroup),
		     ConstantU32(state, MemorySemanticsNone), count});
		return value;
	});
	const auto result = state.builder.AllocateId();
	state.builder.AddFunction({OpGroupNonUniformShuffle, TypeU32(state), result,
	                           ConstantU32(state, ScopeSubgroup), atomic, source_lane});
	return result;
}

struct PreparedFormattedMemory {
	Format::BufferFormatInfo info;
	MemoryResourceAccess     resource;
	std::array<uint32_t, 4>  addresses {};
	std::array<uint32_t, 4>  indices {};
	uint32_t                 in_bounds = 0;
};

enum class FormattedAccess { Load, Store };

PreparedFormattedMemory PrepareFormattedMemory(ValueEmitContext& ctx, const IR::Inst& inst,
                                               const IR::MemoryInfo&       mem,
                                               const MemoryResourceAccess& resource,
                                               const Format::BufferFormatInfo& info,
                                               uint32_t components, FormattedAccess access) {
	PreparedFormattedMemory plan;
	plan.info     = info;
	plan.resource = resource;
	std::array<bool, 4> required_components {};
	if (access == FormattedAccess::Load) {
		for (uint32_t output = 0; output < components; output++) {
			const auto source = ResolveFormattedSource(ctx, mem, plan.info, output);
			if (source.kind == FormattedSourceKind::Memory) {
				required_components[source.component] = true;
			}
		}
	} else {
		for (uint32_t component = 0; component < std::min(components, plan.info.component_count);
		     component++) {
			required_components[component] = true;
		}
	}
	bool first_bound = true;
	for (uint32_t component = 0; component < plan.info.component_count; component++) {
		if (!required_components[component]) continue;
		const auto byte_offset = Format::GetFormatComponentByteOffset(plan.info, component);
		bool       reused      = false;
		for (uint32_t previous = 0; previous < component; previous++) {
			if (required_components[previous] &&
			    Format::GetFormatComponentByteOffset(plan.info, previous) == byte_offset) {
				plan.addresses[component] = plan.addresses[previous];
				plan.indices[component]   = plan.indices[previous];
				reused                    = true;
				break;
			}
		}
		if (reused) continue;
		const auto component_mem  = RebaseFormattedComponent(mem, plan.info, component);
		plan.addresses[component] = ByteAddress(ctx, inst, component_mem);
		const auto raw_index      = Binary(ctx.state, OpShiftRightLogical, TypeU32(ctx.state),
		                                   plan.addresses[component], ConstantU32(ctx.state, 2));
		plan.indices[component]   = EmitMemoryElementIndex(ctx.state, resource, raw_index);
		const auto component_bound =
		    EmitMemoryElementInBounds(ctx.state, resource, plan.indices[component]);
		if (first_bound) {
			plan.in_bounds = component_bound;
			first_bound    = false;
		} else {
			plan.in_bounds = AndCondition(ctx.state, plan.in_bounds, component_bound);
		}
	}
	if (first_bound) plan.in_bounds = ConstantBool(ctx.state, true);
	return plan;
}

uint32_t LoadFormattedInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                               const PreparedFormattedMemory& plan, uint32_t output_component) {
	return LoadFormattedComponent(
	    ctx, mem, plan.info, output_component,
	    [&](uint32_t component) {
		    return LoadWordInBounds(ctx, plan.resource, plan.indices[component]);
	    },
	    [&](uint32_t component, uint32_t bits, bool sign_extend) {
		    return LoadSubwordInBounds(ctx, plan.resource, plan.addresses[component],
		                               plan.indices[component], bits, sign_extend);
	    });
}

uint32_t ConstructU32Composite(EmitterState& state, uint32_t components,
                               const std::array<uint32_t, 4>& values) {
	const auto            result = state.builder.AllocateId();
	std::vector<uint32_t> words {OpCompositeConstruct, TypeU32Composite(state, components), result};
	words.insert(words.end(), values.begin(), values.begin() + components);
	state.builder.AddFunction(words);
	return result;
}

uint32_t FormattedOutOfBoundsValue(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                                   const PreparedFormattedMemory& plan, uint32_t components) {
	std::array<uint32_t, 4> values {};
	for (uint32_t component = 0; component < components; component++) {
		const auto source = ResolveFormattedSource(ctx, mem, plan.info, component);
		values[component] = FormattedConstant(ctx, plan.info, source.kind);
	}
	return ConstructU32Composite(ctx.state, components, values);
}

void StoreFormattedInBounds(ValueEmitContext& ctx, const IR::MemoryInfo& mem,
                            const PreparedFormattedMemory& plan, uint32_t component,
                            uint32_t data) {
	if (component >= plan.info.component_count) return;
	const auto bits = plan.info.component_bits[component];
	if (bits == 8u || bits == 16u) {
		StoreSubwordInBounds(ctx, mem, plan.resource, plan.addresses[component],
		                     plan.indices[component], bits, data);
	} else {
		StoreWordInBounds(ctx, plan.resource, plan.indices[component], data);
	}
}

uint32_t LoadWideBuffer(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t components) {
	auto& state = ctx.state;
	return EmitValueOrDefaultIfCondition(
	    state, ctx.Arg(inst, inst.NumArgs() - 1), TypeU32Composite(state, components),
	    ConstantU32CompositeZero(state, components), [&]() {
		    const auto mem      = ctx.Memory(inst);
		    const auto resource = PrepareMemoryResourceAccess(state, mem);
		    const auto info = Format::GetFormatInfo(
		        mem.formatted ? BufferFormat(ctx, mem) : Prospero::BufferFormat::kInvalid);
		    if (info.type != Format::ComponentType::Unknown) {
			    const auto plan = PrepareFormattedMemory(ctx, inst, mem, resource, info, components,
			                                             FormattedAccess::Load);
			    return EmitValueOrDefaultIfCondition(
			        state, plan.in_bounds, TypeU32Composite(state, components),
			        FormattedOutOfBoundsValue(ctx, mem, plan, components), [&]() {
				        std::array<uint32_t, 4> values {};
				        for (uint32_t component = 0; component < components; component++) {
					        values[component] = LoadFormattedInBounds(ctx, mem, plan, component);
				        }
				        return ConstructU32Composite(state, components, values);
			        });
		    }
		    std::array<uint32_t, 4> values {};
		    for (uint32_t component = 0; component < components; component++) {
			    values[component] =
			        LoadWordPrepared(ctx, inst, RebaseRawComponent(mem, component), resource);
		    }
		    const auto composite = ConstructU32Composite(state, components, values);
		    if (mem.kind == IR::ResourceKind::ScalarBuffer) {
			    return UniformHint(state, TypeU32Composite(state, components), composite);
		    }
		    return composite;
	    });
}

void StoreWideBuffer(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t components) {
	auto& state = ctx.state;
	EmitIfCondition(state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto mem       = ctx.Memory(inst);
		const auto resource  = PrepareMemoryResourceAccess(state, mem);
		const auto composite = ctx.Arg(inst, inst.NumArgs() - 2);
		const auto info = Format::GetFormatInfo(
		    mem.formatted ? BufferFormat(ctx, mem) : Prospero::BufferFormat::kInvalid);
		if (info.type != Format::ComponentType::Unknown) {
			const auto plan = PrepareFormattedMemory(ctx, inst, mem, resource, info, components,
			                                         FormattedAccess::Store);
			EmitIfCondition(state, plan.in_bounds, [&]() {
				for (uint32_t component = 0; component < components; component++) {
					const auto data = state.builder.AllocateId();
					state.builder.AddFunction(
					    {OpCompositeExtract, TypeU32(state), data, composite, component});
					StoreFormattedInBounds(ctx, mem, plan, component, data);
				}
			});
			return;
		}
		for (uint32_t component = 0; component < components; component++) {
			const auto data = state.builder.AllocateId();
			state.builder.AddFunction(
			    {OpCompositeExtract, TypeU32(state), data, composite, component});
			StoreWordPrepared(ctx, inst, RebaseRawComponent(mem, component), resource, data);
		}
	});
}

uint32_t LoadWideShared(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t components) {
	auto& state = ctx.state;
	return EmitValueOrDefaultIfCondition(
	    state, ctx.Arg(inst, inst.NumArgs() - 1), TypeU32Composite(state, components),
	    ConstantU32CompositeZero(state, components), [&]() {
		    const auto              mem      = ctx.Memory(inst);
		    const auto              resource = PrepareMemoryResourceAccess(state, mem);
		    const auto              base     = ByteAddress(ctx, inst, mem);
		    std::array<uint32_t, 4> values {};
		    for (uint32_t component = 0; component < components; component++) {
			    const auto address   = component == 0u ? base
			                                           : Binary(state, OpIAdd, TypeU32(state), base,
			                                                    ConstantU32(state, component * 4u));
			    const auto raw_index = Binary(state, OpShiftRightLogical, TypeU32(state), address,
			                                  ConstantU32(state, 2));
			    const auto index     = EmitMemoryElementIndex(state, resource, raw_index);
			    values[component]    = EmitValueOrZeroIfCondition(
			        state, EmitMemoryElementInBounds(state, resource, index),
			        [&]() { return LoadWordInBounds(ctx, resource, index); });
		    }
		    return ConstructU32Composite(state, components, values);
	    });
}

void StoreWideShared(ValueEmitContext& ctx, const IR::Inst& inst, uint32_t components) {
	auto& state = ctx.state;
	EmitIfCondition(state, ctx.Arg(inst, inst.NumArgs() - 1), [&]() {
		const auto mem      = ctx.Memory(inst);
		const auto resource = PrepareMemoryResourceAccess(state, mem);
		const auto base     = ByteAddress(ctx, inst, mem);
		for (uint32_t component = 0; component < components; component++) {
			const auto address = component == 0u ? base
			                                     : Binary(state, OpIAdd, TypeU32(state), base,
			                                              ConstantU32(state, component * 4u));
			const auto raw_index =
			    Binary(state, OpShiftRightLogical, TypeU32(state), address, ConstantU32(state, 2));
			const auto index = EmitMemoryElementIndex(state, resource, raw_index);
			EmitIfCondition(state, EmitMemoryElementInBounds(state, resource, index),
			                [&]() {
				                StoreWordInBounds(ctx, resource, index, ctx.Arg(inst, component + 1u));
			                });
		}
	});
}

} // namespace

bool BdaNullPageEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_BDA_NULLPAGE");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

// Null-page mode: at shader return, record the last missing page of this invocation.
void EmitBdaFaultFlush(EmitterState& state) {
	if (state.bda_fault_page_variable == 0 || state.fault_buffer_variable == 0) {
		return;
	}
	const auto page = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, TypeU32(state), page, state.bda_fault_page_variable});
	const auto faulted = Binary(state, OpINotEqual, TypeBool(state), page, ConstantU32(state, 0));
	EmitIfCondition(state, faulted, [&]() { RecordBdaFault(state, page); });
}

namespace {

// Branchless page lookup: entry 0 of the page table holds the address of a zero-filled
// page (BufferCache), so a missing page resolves to it instead of a null pointer and the
// callers load unconditionally. The miss is remembered per invocation (Private variable)
// and recorded at return, so the CPU still learns about uncached pages a frame later.
void DefineGetBdaPointerNullPage(EmitterState& state) {
	const auto type          = TypeDeviceAddress(state);
	const auto function_type = state.builder.Type(OpTypeFunction, {type, type, TypeBool(state)});
	state.bda_fault_page_variable = state.builder.DefineGlobalVariable(
	    TypePointer(state, StorageClassPrivate, TypeU32(state)), StorageClassPrivate);
	state.builder.AddName(state.bda_fault_page_variable, "bda_fault_page");
	state.bda_pointer_function = state.builder.AllocateId();
	const auto address         = state.builder.AllocateId();
	const auto entry_label     = state.builder.AllocateId();
	state.builder.AddName(state.bda_pointer_function, "get_bda_pointer");
	state.builder.AddFunction(
	    {OpFunction, type, state.bda_pointer_function, FunctionControlNone, function_type});
	state.builder.AddFunction({OpFunctionParameter, type, address});
	const auto active = state.builder.AllocateId();
	state.builder.AddFunction({OpFunctionParameter, TypeBool(state), active});
	EmitLabel(state, entry_label);

	const auto page64 = Binary(state, OpShiftRightLogical, type, address,
	                           ConstantDeviceAddress(state, BufferCache::CACHING_PAGEBITS));
	const auto table_length = state.builder.AllocateId();
	state.builder.AddFunction({OpArrayLength, TypeU32(state), table_length,
	                           state.bda_pagetable_variable, 0});
	const auto in_table = Binary(state, OpULessThan, TypeBool(state), page64,
	                             Unary(state, OpUConvert, type, table_length));
	const auto page = Select(state, TypeU32(state), in_table,
	                         Unary(state, OpUConvert, TypeU32(state), page64),
	                         ConstantU32(state, 0));
	const auto entry_pointer = state.builder.AllocateId();
	state.builder.AddFunction({OpAccessChain, TypeDeviceAddressStoragePointer(state), entry_pointer,
	                           state.bda_pagetable_variable, ConstantU32(state, 0), page});
	const auto loaded = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, type, loaded, entry_pointer});
	const auto null_pointer = state.builder.AllocateId();
	state.builder.AddFunction({OpAccessChain, TypeDeviceAddressStoragePointer(state), null_pointer,
	                           state.bda_pagetable_variable, ConstantU32(state, 0),
	                           ConstantU32(state, 0)});
	const auto null_base = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, type, null_base, null_pointer});
	const auto missing = Binary(state, OpLogicalOr, TypeBool(state),
	                            Unary(state, OpLogicalNot, TypeBool(state), in_table),
	                            Binary(state, OpIEqual, TypeBool(state), loaded,
	                                   ConstantDeviceAddress(state, 0)));
	const auto base = Select(state, type, missing, null_base, loaded);
	// Remember an in-table miss (page 0 is the null page itself and never misses).
	const auto previous = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, TypeU32(state), previous, state.bda_fault_page_variable});
	const auto remembered = Select(state, TypeU32(state),
	                               Binary(state, OpLogicalAnd, TypeBool(state), missing, active),
	                               page, previous);
	state.builder.AddFunction({OpStore, state.bda_fault_page_variable, remembered});
	const auto offset = Binary(state, OpBitwiseAnd, type, address,
	                           ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - 1));
	state.builder.AddFunction({OpReturnValue, Binary(state, OpIAdd, type, base, offset)});
	state.builder.AddFunction({OpFunctionEnd});
}

} // namespace

void DefineGetBdaPointer(EmitterState& state) {
	if (!state.program.info.uses_dma) {
		return;
	}
	if (BdaNullPageEnabled()) {
		DefineGetBdaPointerNullPage(state);
		return;
	}
	const auto type            = TypeDeviceAddress(state);
	const auto function_type   = state.builder.Type(OpTypeFunction, {type, type});
	state.bda_pointer_function = state.builder.AllocateId();
	const auto address         = state.builder.AllocateId();
	const auto entry_label     = state.builder.AllocateId();
	state.builder.AddName(state.bda_pointer_function, "get_bda_pointer");
	state.builder.AddFunction(
	    {OpFunction, type, state.bda_pointer_function, FunctionControlNone, function_type});
	state.builder.AddFunction({OpFunctionParameter, type, address});
	EmitLabel(state, entry_label);

	const auto page64 = Binary(
	    state, OpShiftRightLogical, type, address,
	    ConstantDeviceAddress(state, BufferCache::CACHING_PAGEBITS));
	// Addresses outside the page table (garbage pointers in never-taken paths, or guest
	// addresses above the covered range) must not index past the table: clamp the lookup to
	// entry 0 and treat the page as missing, instead of reading out of bounds.
	const auto table_length = state.builder.AllocateId();
	state.builder.AddFunction({OpArrayLength, TypeU32(state), table_length,
	                           state.bda_pagetable_variable, 0});
	const auto in_table = Binary(state, OpULessThan, TypeBool(state), page64,
	                             Unary(state, OpUConvert, type, table_length));
	const auto page = Select(state, TypeU32(state), in_table,
	                         Unary(state, OpUConvert, TypeU32(state), page64),
	                         ConstantU32(state, 0));
	const auto entry_pointer = state.builder.AllocateId();
	state.builder.AddFunction({OpAccessChain, TypeDeviceAddressStoragePointer(state), entry_pointer,
	                           state.bda_pagetable_variable, ConstantU32(state, 0), page});
	const auto loaded = state.builder.AllocateId();
	state.builder.AddFunction({OpLoad, type, loaded, entry_pointer});
	const auto base = Select(state, type, in_table, loaded, ConstantDeviceAddress(state, 0));
	const auto missing =
	    Binary(state, OpIEqual, TypeBool(state), base, ConstantDeviceAddress(state, 0));
	const auto fault_label     = state.builder.AllocateId();
	const auto available_label = state.builder.AllocateId();
	const auto merge_label     = state.builder.AllocateId();
	state.builder.AddFunction({OpSelectionMerge, merge_label, SelectionControlNone});
	state.builder.AddFunction(
	    {OpBranchConditional, missing, fault_label, available_label});

	EmitLabel(state, fault_label);
	RecordBdaFault(state, page);
	state.builder.AddFunction({OpBranch, merge_label});

	EmitLabel(state, available_label);
	const auto offset = Binary(
	    state, OpBitwiseAnd, type, address,
	    ConstantDeviceAddress(state, BufferCache::CACHING_PAGESIZE - 1));
	const auto available = Binary(state, OpIAdd, type, base, offset);
	state.builder.AddFunction({OpBranch, merge_label});

	EmitLabel(state, merge_label);
	const auto result = state.builder.AllocateId();
	state.builder.AddFunction({OpPhi, type, result, ConstantDeviceAddress(state, 0), fault_label,
	                           available, available_label});
	state.builder.AddFunction({OpReturnValue, result});
	state.builder.AddFunction({OpFunctionEnd});
}


// IMAGE_BVH_INTERSECT_RAY (BvhIntersectRay): the node type selects one of three structured
// branches -- fp16 box node (64 bytes), fp32 box node (128 bytes), triangle node (64 bytes) --
// so only its loads and math run; a fourth branch yields invalid children. Node addresses are
// multiples of 64 by the pointer encoding, so every 64-byte half is one page lookup and four
// 128-bit loads. The math follows the IR version in frontend/translate/Memory.cpp (GPURT
// IntersectNodeBvh4 / fast_intersect_triangle); min/max are EmitMinMaxF32Value (NaN-suppressing
// like the HLSL reference), so the explicit NaN selects of the IR version are not needed.
uint32_t EmitBvhIntersectRay(ValueEmitContext& ctx, const IR::Inst& inst) {
	auto&      state = ctx.state;
	const auto f32t  = TypeF32(state);
	const auto u32t  = TypeU32(state);
	const auto boolt = TypeBool(state);
	const auto addrt = TypeDeviceAddress(state);
	const auto arg   = [&](size_t index) { return ctx.Arg(inst, index); };
	const auto node_lo = arg(0);
	const auto node_hi = arg(1);
	const auto extent  = arg(2);
	const std::array<uint32_t, 3> origin {arg(3), arg(4), arg(5)};
	const std::array<uint32_t, 3> dir {arg(6), arg(7), arg(8)};
	const std::array<uint32_t, 3> inv_dir {arg(9), arg(10), arg(11)};
	const auto desc0  = arg(12);
	const auto desc1  = arg(13);
	const auto active = arg(14);
	const bool node64 = !inst.Arg(1).IsImmediate() || inst.Arg(1).U32() != 0u;

	constexpr uint32_t InvalidNode = 0xffffffffu;
	constexpr float    Infinity    = std::numeric_limits<float>::infinity();
	const auto U    = [&](uint32_t v) { return ConstantU32(state, v); };
	const auto F    = [&](float v) { return ConstantF32Value(state, v); };
	const auto fadd = [&](uint32_t a, uint32_t b) { return Binary(state, OpFAdd, f32t, a, b); };
	const auto fsub = [&](uint32_t a, uint32_t b) { return Binary(state, OpFSub, f32t, a, b); };
	const auto fmul = [&](uint32_t a, uint32_t b) { return Binary(state, OpFMul, f32t, a, b); };
	const auto fmin = [&](uint32_t a, uint32_t b) { return EmitMinMaxF32Value(state, a, b, false); };
	const auto fmax = [&](uint32_t a, uint32_t b) { return EmitMinMaxF32Value(state, a, b, true); };
	const auto flt  = [&](uint32_t a, uint32_t b) { return Binary(state, OpFOrdLessThan, boolt, a, b); };
	const auto fle  = [&](uint32_t a, uint32_t b) { return Binary(state, OpFOrdLessThanEqual, boolt, a, b); };
	const auto fge  = [&](uint32_t a, uint32_t b) { return Binary(state, OpFOrdGreaterThanEqual, boolt, a, b); };
	const auto fgt  = [&](uint32_t a, uint32_t b) { return Binary(state, OpFOrdGreaterThan, boolt, a, b); };
	const auto fnan = [&](uint32_t a) { return Unary(state, OpIsNan, boolt, a); };
	const auto fsel = [&](uint32_t c, uint32_t a, uint32_t b) { return Select(state, f32t, c, a, b); };
	const auto usel = [&](uint32_t c, uint32_t a, uint32_t b) { return Select(state, u32t, c, a, b); };
	const auto lor  = [&](uint32_t a, uint32_t b) { return Binary(state, OpLogicalOr, boolt, a, b); };
	const auto land = [&](uint32_t a, uint32_t b) { return Binary(state, OpLogicalAnd, boolt, a, b); };
	const auto f32  = [&](uint32_t v) { return Unary(state, OpBitcast, f32t, v); };
	const auto u32  = [&](uint32_t v) { return Unary(state, OpBitcast, u32t, v); };
	const auto ieq  = [&](uint32_t a, uint32_t b) { return Binary(state, OpIEqual, boolt, a, b); };
	const auto ine  = [&](uint32_t a, uint32_t b) { return Binary(state, OpINotEqual, boolt, a, b); };
	// NaN-suppressing min/max (EmitMinMaxF32Value returns the other operand for a NaN input).
	const auto nmax = fmax;
	const auto nmin = fmin;
	using Vec3      = std::array<uint32_t, 3>;
	const auto vsub = [&](const Vec3& a, const Vec3& b) {
		return Vec3 {fsub(a[0], b[0]), fsub(a[1], b[1]), fsub(a[2], b[2])};
	};
	const auto cross = [&](const Vec3& a, const Vec3& b) {
		return Vec3 {fsub(fmul(a[1], b[2]), fmul(a[2], b[1])),
		             fsub(fmul(a[2], b[0]), fmul(a[0], b[2])),
		             fsub(fmul(a[0], b[1]), fmul(a[1], b[0]))};
	};
	const auto dot = [&](const Vec3& a, const Vec3& b) {
		return fadd(fmul(a[0], b[0]), fadd(fmul(a[1], b[1]), fmul(a[2], b[2])));
	};
	const auto half2 = [&](uint32_t word) {
		const auto vec = state.builder.AllocateId();
		state.builder.AddFunction({OpExtInst, TypeF32Vector(state, 2), vec, GlslStd450(state),
		                           GlslUnpackHalf2x16, word});
		const auto lo = state.builder.AllocateId();
		state.builder.AddFunction({OpCompositeExtract, f32t, lo, vec, 0u});
		const auto hi = state.builder.AllocateId();
		state.builder.AddFunction({OpCompositeExtract, f32t, hi, vec, 1u});
		return std::pair {lo, hi};
	};

	// --- Descriptor: box sort heuristic (dword1[22:21]), grow (dword1[30:23]), sort enable (31).
	const auto bfe = [&](uint32_t v, uint32_t offset, uint32_t count) {
		const auto r = state.builder.AllocateId();
		state.builder.AddFunction({OpBitFieldUExtract, u32t, r, v, U(offset), U(count)});
		return r;
	};
	const auto box_grow     = bfe(desc1, 23u, 8u);
	const auto sort_mode    = bfe(desc1, 21u, 2u);
	const auto sort_enabled = land(ine(Binary(state, OpBitwiseAnd, u32t, desc1, U(0x80000000u)), U(0)),
	                               ine(sort_mode, U(3u)));
	const auto grow_factor  = fadd(F(1.0f), fmul(Unary(state, OpConvertUToF, f32t, box_grow),
	                                              F(5.960464478e-8f)));
	const auto sort_largest  = ieq(sort_mode, U(1u));
	const auto sort_midpoint = ieq(sort_mode, U(2u));

	// --- Node address: type in bits [2:0], 64-byte offset in [31:3]; (base >> 3) + ptr, << 3.
	const auto node_type = Binary(state, OpBitwiseAnd, u32t, node_lo, U(7u));
	const auto node_off  = Binary(state, OpBitwiseAnd, u32t, node_lo, U(~7u));
	uint32_t   node_addr = 0;
	if (node64) {
		node_addr = Binary(state, OpShiftLeftLogical, addrt, DeviceAddressFromWords(state, node_off, node_hi),
		                   ConstantDeviceAddress(state, 3));
	} else {
		const auto base = DeviceAddressFromWords(state, desc0, Binary(state, OpBitwiseAnd, u32t, desc1, U(0xffffu)));
		const auto off  = Binary(state, OpShiftLeftLogical, addrt, DeviceAddressFromWords(state, node_off, U(0)),
		                         ConstantDeviceAddress(state, 3));
		node_addr       = Binary(state, OpIAdd, addrt, base, off);
	}
	const auto is_box16 = ieq(node_type, U(4u));
	const auto is_box32 = ieq(node_type, U(5u));
	const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));
	const auto is_tri1  = ieq(node_type, U(1u));

	// --- Loads: `dwords` consecutive dwords from `address` (64-byte aligned) as 128-bit loads.
	const auto vec4t   = TypeU32Vector(state, 4);
	const auto vec4ptr = TypePointer(state, StorageClassPhysicalStorageBuffer, vec4t);
	const auto load_half = [&](uint32_t address, uint32_t dwords, std::vector<uint32_t>& out) {
		const auto page = GetBdaPointer(ctx, address, active);
		if (!BdaNullPageEnabled()) {
			// Pointer mode: a missing page is a null pointer, LoadBdaAt branches on it per dword.
			for (uint32_t i = 0; i < dwords; i++) {
				out.push_back(LoadBdaAt(ctx, i == 0 ? page : Binary(state, OpIAdd, addrt, page, ConstantDeviceAddress(state, i * 4u))));
			}
			return;
		}
		for (uint32_t i = 0; i < dwords; i += 4u) {
			const auto ptr = i == 0 ? page : Binary(state, OpIAdd, addrt, page, ConstantDeviceAddress(state, i * 4u));
			const auto typed = state.builder.AllocateId();
			state.builder.AddFunction({OpConvertUToPtr, vec4ptr, typed, ptr});
			const auto vec = state.builder.AllocateId();
			state.builder.AddFunction({OpLoad, vec4t, vec, typed, MemoryAccessAlignedMask, 16u});
			for (uint32_t k = 0; k < 4u; k++) {
				const auto element = state.builder.AllocateId();
				state.builder.AddFunction({OpCompositeExtract, u32t, element, vec, k});
				out.push_back(element);
			}
		}
	};

	struct BoxHit {
		uint32_t min_t, max_t, min_of, max_of;
	};
	const auto intersect_box = [&](const Vec3& box_min, const Vec3& box_max) {
		Vec3 interval_min {}, interval_max {};
		for (uint32_t axis = 0; axis < 3u; axis++) {
			const auto t_min    = fmul(fsub(box_min[axis], origin[axis]), inv_dir[axis]);
			const auto t_max    = fmul(fsub(box_max[axis], origin[axis]), inv_dir[axis]);
			const auto positive = fge(inv_dir[axis], F(0.0f));
			interval_min[axis]  = fsel(positive, t_min, t_max);
			interval_max[axis]  = fsel(positive, t_max, t_min);
		}
		auto       min_of = nmax(nmax(interval_min[0], interval_min[1]), interval_min[2]);
		auto       max_of = nmin(nmin(interval_max[0], interval_max[1]), interval_max[2]);
		const auto nan    = lor(fnan(min_of), fnan(max_of));
		const auto min_t  = fsel(nan, F(Infinity), nmax(min_of, F(0.0f)));
		const auto max_t  = fsel(nan, F(-Infinity), nmin(max_of, extent));
		min_of            = fsel(fnan(min_of), F(0.0f), min_of);
		max_of            = fsel(fnan(max_of), F(Infinity), max_of);
		return BoxHit {min_t, max_t, min_of, max_of};
	};
	const auto box_children = [&](const std::array<BoxHit, 4>& hits, const std::vector<uint32_t>& d) {
		std::array<uint32_t, 4> child {};
		std::array<uint32_t, 4> key {};
		for (uint32_t index = 0; index < 4u; index++) {
			const auto hit  = fle(hits[index].min_t, fmul(hits[index].max_t, grow_factor));
			child[index]    = usel(hit, d[index], U(InvalidNode));
			const auto closest  = hits[index].min_t;
			const auto largest  = fsub(hits[index].min_t, hits[index].max_t);
			const auto midpoint = fadd(hits[index].min_of, hits[index].max_of);
			key[index] = fsel(sort_largest, largest, fsel(sort_midpoint, midpoint, closest));
		}
		auto       sorted_child = child;
		auto       sorted_key   = key;
		const auto sort2        = [&](uint32_t a, uint32_t b) {
			const auto swap = lor(land(ine(sorted_child[b], U(InvalidNode)), flt(sorted_key[b], sorted_key[a])),
			                      ieq(sorted_child[a], U(InvalidNode)));
			const auto new_a = usel(swap, sorted_child[b], sorted_child[a]);
			const auto new_b = usel(swap, sorted_child[a], sorted_child[b]);
			const auto key_a = fsel(swap, sorted_key[b], sorted_key[a]);
			const auto key_b = fsel(swap, sorted_key[a], sorted_key[b]);
			sorted_child[a]  = new_a;
			sorted_child[b]  = new_b;
			sorted_key[a]    = key_a;
			sorted_key[b]    = key_b;
		};
		sort2(0, 2);
		sort2(1, 3);
		sort2(0, 1);
		sort2(2, 3);
		sort2(1, 2);
		for (uint32_t index = 0; index < 4u; index++) {
			child[index] = usel(sort_enabled, sorted_child[index], child[index]);
		}
		return child;
	};

	// if (cond) then_fn() else else_fn(), four values merged by phi.
	using Result = std::array<uint32_t, 4>;
	const auto branch = [&](uint32_t cond, auto&& then_fn, auto&& else_fn) -> Result {
		const auto then_label  = state.builder.AllocateId();
		const auto else_label  = state.builder.AllocateId();
		const auto merge_label = state.builder.AllocateId();
		state.builder.AddFunction({OpSelectionMerge, merge_label, SelectionControlNone});
		state.builder.AddFunction({OpBranchConditional, cond, then_label, else_label});
		EmitLabel(state, then_label);
		const Result then_values = then_fn();
		const auto   then_exit   = state.current_label;
		state.builder.AddFunction({OpBranch, merge_label});
		EmitLabel(state, else_label);
		const Result else_values = else_fn();
		const auto   else_exit   = state.current_label;
		state.builder.AddFunction({OpBranch, merge_label});
		EmitLabel(state, merge_label);
		Result out {};
		for (uint32_t i = 0; i < 4u; i++) {
			out[i] = state.builder.AllocateId();
			state.builder.AddFunction({OpPhi, u32t, out[i], then_values[i], then_exit, else_values[i], else_exit});
		}
		return out;
	};

	const auto box16_node = [&]() -> Result {
		std::vector<uint32_t> d;
		load_half(node_addr, 16u, d);
		std::array<BoxHit, 4> hits {};
		for (uint32_t index = 0; index < 4u; index++) {
			const uint32_t at = 4u + index * 3u;
			const auto [a_lo, a_hi] = half2(d[at]);
			const auto [b_lo, b_hi] = half2(d[at + 1u]);
			const auto [c_lo, c_hi] = half2(d[at + 2u]);
			hits[index] = intersect_box({a_lo, a_hi, b_lo}, {b_hi, c_lo, c_hi});
		}
		return box_children(hits, d);
	};
	const auto box32_node = [&]() -> Result {
		std::vector<uint32_t> d;
		load_half(node_addr, 16u, d);
		load_half(Binary(state, OpIAdd, addrt, node_addr, ConstantDeviceAddress(state, 64)), 12u, d);
		std::array<BoxHit, 4> hits {};
		for (uint32_t index = 0; index < 4u; index++) {
			const uint32_t at = 4u + index * 6u;
			hits[index] = intersect_box({f32(d[at]), f32(d[at + 1u]), f32(d[at + 2u])},
			                            {f32(d[at + 3u]), f32(d[at + 4u]), f32(d[at + 5u])});
		}
		return box_children(hits, d);
	};
	const auto triangle_node = [&]() -> Result {
		std::vector<uint32_t> d;
		load_half(node_addr, 16u, d);
		const auto vertex = [&](uint32_t index) {
			return Vec3 {f32(d[index * 3u]), f32(d[index * 3u + 1u]), f32(d[index * 3u + 2u])};
		};
		const auto vsel = [&](uint32_t c, const Vec3& a, const Vec3& b) {
			return Vec3 {fsel(c, a[0], b[0]), fsel(c, a[1], b[1]), fsel(c, a[2], b[2])};
		};
		const Vec3 v0    = vertex(0);
		const Vec3 v1    = vertex(1);
		const Vec3 v2    = vertex(2);
		const Vec3 v3    = vertex(3);
		const Vec3 tri_a = vsel(is_tri1, v1, v0);
		const Vec3 tri_b = vsel(is_tri1, v3, v1);
		const Vec3 tri_c = v2;
		const Vec3 e1    = vsub(tri_b, tri_a);
		const Vec3 e2    = vsub(tri_c, tri_a);
		const Vec3 e3    = vsub(origin, tri_a);
		const Vec3 s1    = cross(dir, e2);
		const Vec3 s2    = cross(e3, e1);
		const auto rx    = dot(e2, s2);
		const auto ry    = dot(s1, e1);
		const auto rz    = dot(e3, s1);
		const auto rw    = dot(dir, s2);
		const auto inv_ry = Binary(state, OpFDiv, f32t, F(1.0f), ry);
		const auto t      = fmul(rx, inv_ry);
		const auto u      = fmul(rz, inv_ry);
		const auto v      = fmul(rw, inv_ry);
		auto missed = lor(flt(u, F(0.0f)), fgt(u, F(1.0f)));
		missed      = lor(missed, flt(v, F(0.0f)));
		missed      = lor(missed, fgt(fadd(u, v), F(1.0f)));
		missed      = lor(missed, flt(t, F(0.0f)));
		const auto tri_x = fsel(missed, F(Infinity), rx);
		const auto tri_y = fsel(missed, F(1.0f), ry);
		const auto triangle_id = d[15];
		const auto id_shift    = Binary(state, OpShiftLeftLogical, u32t, node_type, U(3u));
		const auto bary0       = fsub(fsub(tri_y, rz), rw);
		const auto pick_bary   = [&](uint32_t extra_shift) {
			const auto index = Binary(
			    state, OpBitwiseAnd, u32t,
			    Binary(state, OpShiftRightLogical, u32t, triangle_id,
			           Binary(state, OpIAdd, u32t, id_shift, U(extra_shift))),
			    U(3u));
			return fsel(ieq(index, U(0u)), bary0,
			            fsel(ieq(index, U(1u)), rz, fsel(ieq(index, U(2u)), rw, F(0.0f))));
		};
		return Result {u32(tri_x), u32(tri_y), u32(pick_bary(0u)), u32(pick_bary(2u))};
	};
	const auto invalid_node = [&]() -> Result {
		return Result {U(InvalidNode), U(InvalidNode), U(InvalidNode), U(InvalidNode)};
	};

	const Result result = branch(
	    is_box16, box16_node, [&]() -> Result {
		    return branch(is_box32, box32_node, [&]() -> Result {
			    return branch(is_tri, triangle_node, invalid_node);
		    });
	    });
	const auto vec = state.builder.AllocateId();
	state.builder.AddFunction({OpCompositeConstruct, vec4t, vec, result[0], result[1], result[2], result[3]});
	return vec;
}

bool EmitValueMemory(ValueEmitContext& ctx, const IR::Inst& inst) {
	auto&      state             = ctx.state;
	const auto op                = inst.GetOpcode();
	if (op == IR::ValueOpcode::BvhIntersectRay) {
		ctx.Define(inst, EmitBvhIntersectRay(ctx, inst));
		return true;
	}
	const auto buffer_components = IR::BufferComponentCount(op);
	if (buffer_components > 1u) {
		const auto access = IR::BufferAccessOf(op);
		if (access == IR::BufferAccess::Read) {
			ctx.Define(inst, LoadWideBuffer(ctx, inst, buffer_components));
			return true;
		}
		if (access == IR::BufferAccess::Write) {
			StoreWideBuffer(ctx, inst, buffer_components);
			return true;
		}
	}
	const auto shared_components = IR::SharedComponentCount(op);
	if (shared_components > 1u) {
		if (IR::SharedAccessOf(op) == IR::SharedAccess::Read) {
			ctx.Define(inst, LoadWideShared(ctx, inst, shared_components));
		} else {
			StoreWideShared(ctx, inst, shared_components);
		}
		return true;
	}
	if ((op == IR::ValueOpcode::LoadAddressU32 || op == IR::ValueOpcode::ReadConstBuffer) &&
	    ctx.Memory(inst).planning_only) {
		return true;
	}
	if (op == IR::ValueOpcode::ReadConst) {
		if (state.flattened_srt_variable == 0) {
			ctx.Fail(inst, "requires the flattened SRT descriptor");
			return true;
		}
		const auto pointer = state.builder.AllocateId();
		state.builder.AddFunction({OpAccessChain, TypeStorageBufferElementPointer(state), pointer,
		                           state.flattened_srt_variable, ConstantU32(state, 0),
		                           ctx.Arg(inst, 1)});
		const auto loaded = state.builder.AllocateId();
		state.builder.AddFunction({OpLoad, TypeU32(state), loaded, pointer});
		ctx.Define(inst, UniformHint(state, TypeU32(state), loaded));
		return true;
	}
	if (op == IR::ValueOpcode::ReadConstBuffer) {
		if (ctx.grouped_loads.contains(&inst)) {
			return true;
		}
		auto mem = ctx.Memory(inst);
		mem.kind = IR::ResourceKind::ScalarBuffer;
		if (const auto vector = LoadConstBufferVector(ctx, inst, mem); vector != 0u) {
			ctx.Define(inst, vector);
			return true;
		}
		const auto address =
		    Binary(state, OpIAdd, TypeU32(state), ctx.Arg(inst, 1), ConstantU32(state, mem.offset));
		if (UsesConstBank(state, mem.resource)) {
			// Single dword through the uniform-buffer view of the V# (constant bank on NVIDIA).
			const auto slot = ResourceForDescriptor(state, IR::DescriptorBindingKind::ConstBuffers,
			                                        mem.resource);
			const auto buffer_slot =
			    ResourceForDescriptor(state, IR::DescriptorBindingKind::Buffers, mem.resource);
			const auto byte = Binary(state, OpIAdd, TypeU32(state), address,
			                         state.memory_byte_offsets[buffer_slot]);
			const auto element =
			    Binary(state, OpShiftRightLogical, TypeU32(state), byte, ConstantU32(state, 2));
			const auto pointer = state.builder.AllocateId();
			state.builder.AddFunction({OpAccessChain, TypeUniformElementPointer(state, 1u), pointer,
			                           state.const_buffer_variable, ConstantU32(state, slot),
			                           ConstantU32(state, 0), element});
			const auto value = state.builder.AllocateId();
			state.builder.AddFunction({OpLoad, TypeU32(state), value, pointer});
			ctx.Define(inst, UniformHint(state, TypeU32(state), value));
			return true;
		}
		const auto index =
		    Binary(state, OpShiftRightLogical, TypeU32(state), address, ConstantU32(state, 2));
		const auto access    = PrepareMemoryResourceAccess(state, mem);
		const auto element   = EmitMemoryElementIndex(state, access, index);
		const auto condition = EmitMemoryElementInBounds(state, access, element);
		ctx.Define(inst, UniformHint(state, TypeU32(state),
		                             EmitValueOrZeroIfCondition(state, condition, [&]() {
			                             const auto value = state.builder.AllocateId();
			                             state.builder.AddFunction(
			                                 {OpLoad, TypeU32(state), value,
			                                  EmitMemoryElementPointer(state, access, element)});
			                             return value;
		                             })));
		return true;
	}
	const auto address_info = IR::AddressOpcodeInfoOf(op);
	const bool load_address = address_info.access == IR::AddressAccess::Read;
	if (load_address && ctx.Memory(inst).kind != IR::ResourceKind::Scratch) {
		if (ctx.grouped_loads.contains(&inst)) {
			return true;
		}
		ctx.Define(inst, LoadBda(ctx, inst, ctx.Memory(inst), address_info.data_bits));
		return true;
	}
	const bool load_buffer  = op == IR::ValueOpcode::LoadBufferU8 ||
	                          op == IR::ValueOpcode::LoadBufferU16 ||
	                          op == IR::ValueOpcode::LoadBufferU32;
	const bool load_shared  = IR::SharedAccessOf(op) == IR::SharedAccess::Read;
	if (load_address || load_buffer || load_shared) {
		const auto mem   = ctx.Memory(inst);
		uint32_t   value = 0;
		if (op == IR::ValueOpcode::LoadBufferU32 && mem.formatted)
			value = FormattedLoad(ctx, inst, mem);
		else if (op == IR::ValueOpcode::LoadAddressU8 || op == IR::ValueOpcode::LoadBufferU8 ||
		         op == IR::ValueOpcode::LoadSharedU8)
			value = LoadSubword(ctx, inst, mem, 8, false);
		else if (op == IR::ValueOpcode::LoadAddressU16 || op == IR::ValueOpcode::LoadBufferU16 ||
		         op == IR::ValueOpcode::LoadSharedU16)
			value = LoadSubword(ctx, inst, mem, 16, false);
		else
			value = LoadWord(ctx, inst, mem);
		ctx.Define(inst, value);
		return true;
	}
	const bool store_address = address_info.access == IR::AddressAccess::Write;
	const bool store_buffer  = op == IR::ValueOpcode::StoreBufferU8 ||
	                           op == IR::ValueOpcode::StoreBufferU16 ||
	                           op == IR::ValueOpcode::StoreBufferU32;
	const bool store_shared  = IR::SharedAccessOf(op) == IR::SharedAccess::Write;
	if (store_address || store_buffer || store_shared) {
		const auto mem = ctx.Memory(inst);
		if (op == IR::ValueOpcode::StoreBufferU32 && mem.formatted)
			FormattedStore(ctx, inst, mem);
		else if (op == IR::ValueOpcode::StoreAddressU8 || op == IR::ValueOpcode::StoreBufferU8 ||
		         op == IR::ValueOpcode::WriteSharedU8)
			StoreSubword(ctx, inst, mem, 8);
		else if (op == IR::ValueOpcode::StoreAddressU16 || op == IR::ValueOpcode::StoreBufferU16 ||
		         op == IR::ValueOpcode::WriteSharedU16)
			StoreSubword(ctx, inst, mem, 16);
		else
			StoreWord(ctx, inst, mem);
		return true;
	}
	const auto atomic_opcode = SpirvAtomicOpcode(op);
	if (atomic_opcode != 0 && inst.GetType() == IR::Type::U64) {
		ctx.Define(inst, EmitBufferAtomic64(ctx, inst, ctx.Memory(inst)));
		return true;
	}
	if (atomic_opcode != 0) {
		ctx.Define(inst, EmitAtomic(ctx, inst, ctx.Memory(inst)));
		return true;
	}
	if (op == IR::ValueOpcode::BufferAtomicFMin32 || op == IR::ValueOpcode::BufferAtomicFMax32) {
		ctx.Define(inst, FloatAtomic(ctx, inst, ctx.Memory(inst),
		                             op == IR::ValueOpcode::BufferAtomicFMax32));
		return true;
	}
	if (op == IR::ValueOpcode::SharedAtomicInc32 || op == IR::ValueOpcode::SharedAtomicDec32) {
		const auto replacement = op == IR::ValueOpcode::SharedAtomicInc32
		                             ? AtomicIncrement : AtomicDecrement;
		ctx.Define(inst, EmitAtomicUpdate(ctx, inst, ctx.Memory(inst), replacement));
		return true;
	}
	if (op == IR::ValueOpcode::SharedAtomicFMin32 || op == IR::ValueOpcode::SharedAtomicFMax32) {
		SharedFloatAtomic(ctx, inst, ctx.Memory(inst), op == IR::ValueOpcode::SharedAtomicFMax32);
		return true;
	}
	if (op == IR::ValueOpcode::DataAppend || op == IR::ValueOpcode::DataConsume) {
		ctx.Define(inst, AppendConsume(ctx, inst, op == IR::ValueOpcode::DataAppend));
		return true;
	}
	if (op == IR::ValueOpcode::SwizzleU32 || op == IR::ValueOpcode::BpermuteU32) {
		uint32_t source = ctx.Arg(inst, 0);
		uint32_t target = 0;
		if (op == IR::ValueOpcode::SwizzleU32) {
			state.builder.AddFunction({OpStore, ctx.scratch_u32_variable, source});
			source = state.builder.AllocateId();
			state.builder.AddFunction({OpLoad, TypeU32(state), source, ctx.scratch_u32_variable});
			target = EmitDsSwizzleTargetLane(state, EmitSubgroupLocalInvocationId(state),
			                                 inst.Arg(1).IsImmediate() ? inst.Arg(1).U32() : 0);
		} else {
			const auto index = Binary(
			    state, OpBitwiseAnd, TypeU32(state),
			    Binary(state, OpShiftRightLogical, TypeU32(state), ctx.Arg(inst, 1),
			           ConstantU32(state, 2)),
			    ConstantU32(state, 31));
			const auto base =
			    Binary(state, OpBitwiseAnd, TypeU32(state), EmitSubgroupLocalInvocationId(state),
			           ConstantU32(state, ~31u));
			target = Binary(state, OpBitwiseOr, TypeU32(state), base, index);
		}
		ctx.Define(inst, EmitDsMaskedLaneRead(state, source, target, ctx.Arg(inst, 2)));
		return true;
	}
	return false;
}

} // namespace Libs::Graphics::ShaderRecompiler::Spirv::Emitter
