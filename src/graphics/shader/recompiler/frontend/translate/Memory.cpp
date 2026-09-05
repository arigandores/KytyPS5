#include "graphics/shader/recompiler/frontend/translate/Translator.h"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <limits>

namespace Libs::Graphics::ShaderRecompiler::Frontend {

namespace {

using IR::ResourceKind;

const Decoder::Operand& DecodedSourceAt(const Decoder::Instruction& decoded, uint32_t index) {
	switch (index) {
		case 0: return decoded.src0;
		case 1: return decoded.src1;
		case 2: return decoded.src2;
		default: return decoded.src3;
	}
}

Decoder::Operand OffsetDecodedRegister(const Decoder::Operand& operand, uint32_t index) {
	if (index == 0) {
		return operand;
	}
	auto result               = operand;
	result.sdwa_sel           = 6;
	result.sdwa_dst_unused    = 2;
	result.omod               = 0;
	result.sdwa_sext          = false;
	result.op_sel             = false;
	result.op_sel_hi          = false;
	result.negate             = false;
	result.negate_hi          = false;
	result.absolute           = false;
	result.dpp_ctrl           = 0;
	result.dpp_row_mask       = 0xf;
	result.dpp_bank_mask      = 0xf;
	result.explicit_sdwa_dst  = false;
	result.dpp_fetch_inactive = false;
	result.dpp_bound_ctrl     = false;
	result.dpp                = false;
	if (result.kind == Decoder::OperandKind::Vgpr || result.kind == Decoder::OperandKind::Sgpr) {
		result.reg += index;
	}
	return result;
}

uint32_t ResourceIndexFromOperand(const Decoder::Operand& operand) {
	switch (operand.kind) {
		case Decoder::OperandKind::Sgpr: return operand.reg / 4u;
		case Decoder::OperandKind::Vgpr: return operand.reg;
		case Decoder::OperandKind::IntegerInlineConstant:
		case Decoder::OperandKind::LiteralConstant: return operand.value;
		default: return 0;
	}
}

uint32_t RawScalarLoadBase(const Decoder::Operand& operand) {
	if (operand.kind == Decoder::OperandKind::Sgpr) {
		return operand.reg;
	}
	return operand.kind == Decoder::OperandKind::VccLo ? 106u : 0u;
}

ResourceKind FlatSegmentResourceKind(uint32_t segment) {
	switch (segment) {
		case 1u: return ResourceKind::Scratch;
		case 2u: return ResourceKind::Global;
		default: return ResourceKind::Flat;
	}
}

ResourceKind MemoryKind(const Decoder::Instruction& decoded) {
	switch (decoded.family) {
		case Decoder::Family::SMEM:
			return decoded.opcode == Decoder::Opcode::S_LOAD_DWORD ||
			               decoded.opcode == Decoder::Opcode::S_LOAD_DWORDX2 ||
			               decoded.opcode == Decoder::Opcode::S_LOAD_DWORDX4 ||
			               decoded.opcode == Decoder::Opcode::S_LOAD_DWORDX8 ||
			               decoded.opcode == Decoder::Opcode::S_LOAD_DWORDX16
			           ? ResourceKind::ScalarAddress
			           : ResourceKind::ScalarBuffer;
		case Decoder::Family::MUBUF:
		case Decoder::Family::MTBUF: return ResourceKind::Buffer;
		case Decoder::Family::FLAT: return FlatSegmentResourceKind(decoded.memory_segment);
		case Decoder::Family::DS: return decoded.gds ? ResourceKind::Gds : ResourceKind::Lds;
		case Decoder::Family::MIMG: return ResourceKind::Image;
		default: return ResourceKind::None;
	}
}

IR::MemoryInfo MemoryInfoFromDecoded(const Decoder::Instruction& decoded) {
	IR::MemoryInfo memory;
	memory.kind             = MemoryKind(decoded);
	memory.offset           = decoded.offset;
	memory.secondary_offset = decoded.secondary_offset;
	memory.dmask            = decoded.dmask;
	memory.data_dwords      = decoded.data_dwords;
	memory.data_bits        = decoded.data_bits;
	memory.component_count =
	    decoded.data_components != 0u ? decoded.data_components : decoded.data_dwords;
	memory.data_format              = decoded.data_format;
	memory.number_format            = decoded.number_format;
	memory.image_sample_flags       = decoded.image_sample_flags;
	memory.image_dimension          = decoded.image_dimension;
	memory.image_address_components = decoded.image_address_components;
	memory.image_nsa_dwords         = decoded.image_nsa_dwords;
	for (uint32_t index = 0; index < Decoder::MaxImageNsaAddressComponents; index++) {
		memory.image_nsa_addr[index] = decoded.image_nsa_addr[index];
	}
	memory.memory_segment = decoded.memory_segment;
	memory.address_is_full =
	    memory.kind == ResourceKind::Flat ||
	    (memory.kind == ResourceKind::Global && decoded.src1.kind == Decoder::OperandKind::Vgpr);
	memory.data_signed   = decoded.data_signed;
	memory.typed         = decoded.typed;
	memory.formatted     = decoded.formatted;
	memory.image_has_mip = decoded.opcode == Decoder::Opcode::IMAGE_LOAD_MIP ||
	                       decoded.opcode == Decoder::Opcode::IMAGE_STORE_MIP;
	memory.image_r128    = decoded.image_r128;
	memory.glc           = decoded.glc;
	memory.slc           = decoded.slc;
	memory.idxen         = decoded.idxen;
	memory.offen         = decoded.offen;
	memory.resource      = ResourceIndexFromOperand(decoded.src1);
	memory.sampler       = ResourceIndexFromOperand(decoded.src2);
	if (memory.kind == ResourceKind::ScalarBuffer) {
		memory.resource = ResourceIndexFromOperand(decoded.src0);
	} else if (IsAddressResourceKind(memory.kind) || memory.kind == ResourceKind::Lds ||
	           memory.kind == ResourceKind::Gds) {
		memory.resource = 0;
		memory.sampler  = 0;
	}
	if (decoded.opcode == Decoder::Opcode::DS_READ2_B64 ||
	    decoded.opcode == Decoder::Opcode::DS_READ2ST64_B64 ||
	    decoded.opcode == Decoder::Opcode::DS_WRITE2_B64 ||
	    decoded.opcode == Decoder::Opcode::DS_WRITE2ST64_B64) {
		memory.data_dwords = 4u;
	} else if (decoded.opcode == Decoder::Opcode::DS_READ2_B32 ||
	           decoded.opcode == Decoder::Opcode::DS_READ2ST64_B32 ||
	           decoded.opcode == Decoder::Opcode::DS_WRITE2_B32 ||
	           decoded.opcode == Decoder::Opcode::DS_WRITE2ST64_B32) {
		memory.data_dwords = 2u;
	}
	return memory;
}

bool IsScalarAddressLoad(Decoder::Opcode opcode) {
	switch (opcode) {
		case Decoder::Opcode::S_LOAD_DWORD:
		case Decoder::Opcode::S_LOAD_DWORDX2:
		case Decoder::Opcode::S_LOAD_DWORDX4:
		case Decoder::Opcode::S_LOAD_DWORDX8:
		case Decoder::Opcode::S_LOAD_DWORDX16: return true;
		default: return false;
	}
}

bool IsScalarBufferLoad(Decoder::Opcode opcode) {
	switch (opcode) {
		case Decoder::Opcode::S_BUFFER_LOAD_DWORD:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX2:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX4:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX8:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX16: return true;
		default: return false;
	}
}

Decoder::Operand MakeM0Operand() {
	Decoder::Operand operand;
	operand.kind = Decoder::OperandKind::M0;
	return operand;
}

Decoder::Operand MakeImmediate(uint32_t value) {
	Decoder::Operand operand;
	operand.kind  = Decoder::OperandKind::LiteralConstant;
	operand.value = value;
	return operand;
}

Decoder::Operand MemorySourceAt(const Decoder::Instruction& decoded, uint32_t index) {
	if (IsScalarAddressLoad(decoded.opcode) || IsScalarBufferLoad(decoded.opcode)) {
		return decoded.src1;
	}
	if (decoded.family == Decoder::Family::MUBUF || decoded.family == Decoder::Family::MTBUF) {
		const bool store_or_atomic =
		    (decoded.opcode >= Decoder::Opcode::BUFFER_STORE_FORMAT_X &&
		     decoded.opcode <= Decoder::Opcode::BUFFER_STORE_FORMAT_XYZW) ||
		    (decoded.opcode >= Decoder::Opcode::BUFFER_STORE_BYTE &&
		     decoded.opcode <= Decoder::Opcode::BUFFER_STORE_DWORDX4) ||
		    (decoded.opcode >= Decoder::Opcode::TBUFFER_STORE_FORMAT_X &&
		     decoded.opcode <= Decoder::Opcode::TBUFFER_STORE_FORMAT_XYZW) ||
		    (decoded.opcode >= Decoder::Opcode::BUFFER_ATOMIC_SWAP &&
		     decoded.opcode <= Decoder::Opcode::BUFFER_ATOMIC_FMAX);
		uint32_t cursor = 0;
		if (store_or_atomic) {
			if (index == cursor++) return decoded.dst;
		}
		if (decoded.idxen) {
			if (index == cursor++) return decoded.src0;
		}
		if (decoded.offen) {
			if (index == cursor++)
				return decoded.idxen ? OffsetDecodedRegister(decoded.src0, 1u) : decoded.src0;
		}
		if (index == cursor) return decoded.src2;
		return MakeImmediate(0u);
	}
	if (decoded.family == Decoder::Family::FLAT) {
		const bool store = decoded.opcode == Decoder::Opcode::FLAT_STORE_BYTE ||
		                   decoded.opcode == Decoder::Opcode::FLAT_STORE_SHORT ||
		                   decoded.opcode == Decoder::Opcode::FLAT_STORE_DWORD ||
		                   decoded.opcode == Decoder::Opcode::FLAT_STORE_DWORDX2 ||
		                   decoded.opcode == Decoder::Opcode::FLAT_STORE_DWORDX3 ||
		                   decoded.opcode == Decoder::Opcode::FLAT_STORE_DWORDX4;
		if (store) {
			return index == 0u ? decoded.dst : DecodedSourceAt(decoded, index - 1u);
		}
		return DecodedSourceAt(decoded, index);
	}
	if (decoded.family == Decoder::Family::MIMG) {
		const bool store_or_atomic = decoded.opcode == Decoder::Opcode::IMAGE_STORE ||
		                             decoded.opcode == Decoder::Opcode::IMAGE_STORE_MIP ||
		                             (decoded.opcode >= Decoder::Opcode::IMAGE_ATOMIC_SWAP &&
		                              decoded.opcode <= Decoder::Opcode::IMAGE_ATOMIC_XOR);
		if (store_or_atomic) {
			return index == 0u ? decoded.dst : decoded.src0;
		}
		return decoded.src0;
	}
	if (decoded.family == Decoder::Family::DS) {
		switch (decoded.opcode) {
			case Decoder::Opcode::DS_SWIZZLE_B32:
				return index == 0u ? decoded.src0 : MakeImmediate(decoded.offset & 0xffffu);
			case Decoder::Opcode::DS_CONSUME:
			case Decoder::Opcode::DS_APPEND:
			case Decoder::Opcode::DS_READ_ADDTID_B32: return MakeM0Operand();
			case Decoder::Opcode::DS_WRITE_ADDTID_B32:
				return index == 0u ? decoded.src1 : MakeM0Operand();
			case Decoder::Opcode::DS_MIN_F32:
			case Decoder::Opcode::DS_MAX_F32:
				return index == 0u ? decoded.src1 : index == 1u ? decoded.src0 : decoded.src2;
			case Decoder::Opcode::DS_WRITE_B8:
			case Decoder::Opcode::DS_WRITE_B16:
			case Decoder::Opcode::DS_WRITE_B16_D16_HI:
			case Decoder::Opcode::DS_WRITE_B32:
			case Decoder::Opcode::DS_WRITE_B64:
			case Decoder::Opcode::DS_WRITE_B96:
			case Decoder::Opcode::DS_WRITE_B128:
			case Decoder::Opcode::DS_WRITE2_B32:
			case Decoder::Opcode::DS_WRITE2ST64_B32:
			case Decoder::Opcode::DS_WRITE2_B64:
			case Decoder::Opcode::DS_WRITE2ST64_B64:
				return index == 0u ? decoded.src1 : index == 1u ? decoded.src0 : decoded.src2;
			default:
				if (decoded.opcode >= Decoder::Opcode::DS_ADD_U32 &&
				    decoded.opcode <= Decoder::Opcode::DS_WRXCHG_RTN_B32) {
					return index == 0u ? decoded.src1 : decoded.src0;
				}
				return decoded.src0;
		}
	}
	return DecodedSourceAt(decoded, index);
}

} // namespace

IR::MemoryFlags Translator::AddMemoryInfo(const IR::MemoryInfo& memory, uint32_t pc) {
	const auto index = static_cast<uint32_t>(program.memory_info.size());
	program.memory_info.push_back(memory);
	return {.index = index, .pc = pc};
}

IR::U32 Translator::GetResourceDword(uint32_t index, uint32_t dword) {
	return ReadScalarCode(index * 4u + dword);
}

IR::Value Translator::GetBufferResource(const IR::MemoryInfo& memory) {
	return ir.Emit(IR::ValueOpcode::GetBufferResource,
	               {GetResourceDword(memory.resource, 0), GetResourceDword(memory.resource, 1),
	                GetResourceDword(memory.resource, 2), GetResourceDword(memory.resource, 3)});
}

IR::Value Translator::GetAddressResource(IR::Value low, IR::Value high) {
	return ir.Emit(IR::ValueOpcode::GetAddressResource, {low, high});
}

Translator::AddressOperands Translator::ReadAddressOperands(const Decoder::Instruction& inst,
                                                            uint32_t first_source) {
	const auto memory       = MemoryInfoFromDecoded(inst);
	const auto low          = ReadU32(MemorySourceAt(inst, first_source));
	const auto high_or_base = MemorySourceAt(inst, first_source + 1u);
	if (memory.kind == IR::ResourceKind::Scratch) {
		const auto offset =
		    high_or_base.kind != Decoder::OperandKind::Vgpr ? ReadU32(high_or_base) : low;
		return {ir.Emit(IR::ValueOpcode::GetScratchResource), offset, IR::Value(0u)};
	}
	if (memory.kind == IR::ResourceKind::Global &&
	    high_or_base.kind != Decoder::OperandKind::Vgpr) {
		const auto base_low  = ReadU32(high_or_base);
		const auto base_high = ReadU32(OffsetOperand(high_or_base, 1u));
		return {GetAddressResource(base_low, base_high), low, IR::Value(0u)};
	}
	const auto high = ReadU32(high_or_base);
	return {GetAddressResource(low, high), low, high};
}

IR::Value Translator::GetScalarAddressResource(uint32_t base) {
	return GetAddressResource(ReadScalarCode(base), ReadScalarCode(base + 1u));
}

IR::Value Translator::GetImageResource(const IR::MemoryInfo& memory) {
	const auto dword = [&](uint32_t index) {
		return memory.image_r128 && index >= 4u ? IR::U32(IR::Value(0u))
		                                        : GetResourceDword(memory.resource, index);
	};
	return ir.Emit(IR::ValueOpcode::GetImageResource, {dword(0), dword(1), dword(2), dword(3),
	                                                   dword(4), dword(5), dword(6), dword(7)});
}

IR::Value Translator::GetSamplerResource(const IR::MemoryInfo& memory) {
	return ir.Emit(IR::ValueOpcode::GetSamplerResource,
	               {GetResourceDword(memory.sampler, 0), GetResourceDword(memory.sampler, 1),
	                GetResourceDword(memory.sampler, 2), GetResourceDword(memory.sampler, 3)});
}

IR::Value Translator::MakeImageAddress(const Decoder::Instruction& inst,
                                       const Decoder::Operand&     base) {
	const auto                memory = MemoryInfoFromDecoded(inst);
	std::array<IR::Value, 13> components {};
	components[0] = ReadRawU32(PlainOperand(base));
	const auto nsa_components =
	    std::min(memory.image_nsa_dwords * 4u, Decoder::MaxImageNsaAddressComponents);
	for (uint32_t index = 1; index < components.size(); index++) {
		if (index - 1u < nsa_components) {
			components[index] =
			    ir.GetVectorReg(static_cast<IR::VectorReg>(memory.image_nsa_addr[index - 1u]));
		} else {
			components[index] = ReadRawU32(OffsetOperand(PlainOperand(base), index));
		}
	}
	return ir.Emit(IR::ValueOpcode::MakeImageAddress,
	               {components[0], components[1], components[2], components[3], components[4],
	                components[5], components[6], components[7], components[8], components[9],
	                components[10], components[11], components[12]});
}

IR::Value Translator::ConstructU32x4(const Decoder::Operand& base, uint32_t count) {
	std::array<IR::Value, 4> components {IR::Value(0u), IR::Value(0u), IR::Value(0u),
	                                     IR::Value(0u)};
	for (uint32_t index = 0; index < std::min(count, 4u); index++) {
		components[index] = ReadRawU32(OffsetOperand(PlainOperand(base), index));
	}
	return ir.Emit(IR::ValueOpcode::CompositeConstructU32x4,
	               {components[0], components[1], components[2], components[3]});
}

void Translator::WriteImageComponents(const Decoder::Operand& dst, IR::Value value,
                                      const IR::MemoryInfo& memory, uint32_t component_limit) {
	if (memory.data_bits == 16u) {
		for (uint32_t index = 0; index < memory.data_dwords; index++) {
			WriteOperand(OffsetOperand(dst, index), ir.Emit(IR::ValueOpcode::CompositeExtractU32x4,
			                                                {value, IR::Value(index)}));
		}
		return;
	}
	const auto mask      = memory.dmask != 0u ? memory.dmask : 1u;
	uint32_t   dst_index = 0;
	for (uint32_t component = 0; component < component_limit; component++) {
		if (((mask >> component) & 1u) == 0u) {
			continue;
		}
		WriteOperand(
		    OffsetOperand(dst, dst_index++),
		    ir.Emit(IR::ValueOpcode::CompositeExtractU32x4, {value, IR::Value(component)}));
	}
}

Translator::BufferAddress Translator::ReadBufferAddress(const Decoder::Instruction& inst,
                                                        uint32_t                    first_source) {
	const auto memory  = MemoryInfoFromDecoded(inst);
	uint32_t   cursor  = first_source;
	const auto next    = [&]() { return ReadU32(MemorySourceAt(inst, cursor++)); };
	const auto index   = memory.idxen ? next() : IR::U32(IR::Value(0u));
	const auto offset  = memory.offen ? next() : IR::U32(IR::Value(0u));
	const auto soffset = next();
	return {index, offset, soffset};
}

IR::U32 Translator::WidenSubdword(IR::Value value, uint32_t bits, bool sign) {
	IR::U32 widened = bits == 8u ? IR::U32(ir.Emit(IR::ValueOpcode::ConvertU32U8, {value}))
	                             : IR::U32(ir.Emit(IR::ValueOpcode::ConvertU32U16, {value}));
	if (sign) {
		widened = IR::U32(
		    ir.Emit(IR::ValueOpcode::BitFieldSExtract, {widened, IR::Value(0u), IR::Value(bits)}));
	}
	return widened;
}

IR::Value Translator::NarrowSubdword(IR::U32 value, uint32_t bits) {
	return bits == 8u ? ir.Emit(IR::ValueOpcode::ConvertU8U32, {value})
	                  : ir.Emit(IR::ValueOpcode::ConvertU16U32, {value});
}

bool Translator::S_LOAD(const Decoder::Instruction& inst, bool raw) {
	const auto memory = MemoryInfoFromDecoded(inst);
	const auto resource =
	    raw ? GetScalarAddressResource(RawScalarLoadBase(inst.src0)) : GetBufferResource(memory);
	const auto                offset = ReadU32(inst.src1);
	std::array<IR::Value, 16> loaded {};
	for (uint32_t component = 0; component < memory.data_dwords; component++) {
		auto scalar = memory;
		scalar.offset += component * sizeof(uint32_t);
		scalar.data_dwords     = 1u;
		scalar.component_index = component;
		if (!raw) {
			loaded[component] = ir.Emit(IR::ValueOpcode::ReadConstBuffer, {resource, offset},
			                            AddMemoryInfo(scalar, inst.pc));
		} else {
			loaded[component] = ir.Emit(IR::ValueOpcode::LoadAddressU32,
			                            {resource, offset, IR::Value(0u), IR::Value(true)},
			                            AddMemoryInfo(scalar, inst.pc));
		}
	}
	for (uint32_t component = 0; component < memory.data_dwords; component++) {
		WriteOperand(ScalarDestinationOperand(inst.dst, component), loaded[component]);
	}
	return true;
}

bool Translator::BUFFER_LOAD(const Decoder::Instruction& inst) {
	const auto      memory = MemoryInfoFromDecoded(inst);
	IR::ValueOpcode opcode;
	const auto      bits = memory.data_bits;
	const auto      sign = memory.data_signed;
	switch (bits) {
		case 8u: opcode = IR::ValueOpcode::LoadBufferU8; break;
		case 16u: opcode = IR::ValueOpcode::LoadBufferU16; break;
		case 32u:
			switch (memory.data_dwords) {
				case 1u: opcode = IR::ValueOpcode::LoadBufferU32; break;
				case 2u: opcode = IR::ValueOpcode::LoadBufferU32x2; break;
				case 3u: opcode = IR::ValueOpcode::LoadBufferU32x3; break;
				case 4u: opcode = IR::ValueOpcode::LoadBufferU32x4; break;
				default: return false;
			}
			break;
		default: return false;
	}
	const auto resource = GetBufferResource(memory);
	const auto address  = ReadBufferAddress(inst, 0);
	const auto loaded =
	    ir.Emit(opcode, {resource, address.index, address.offset, address.soffset, ir.GetExec()},
	            AddMemoryInfo(memory, inst.pc));
	if (bits != 32u) {
		WriteOperand(inst.dst, WidenSubdword(loaded, bits, sign));
	} else if (memory.data_dwords == 1u) {
		WriteOperand(inst.dst, loaded);
	} else {
		for (uint32_t component = 0; component < memory.data_dwords; component++) {
			WriteOperand(OffsetOperand(inst.dst, component),
			             ir.CompositeExtract(loaded, component));
		}
	}
	return true;
}

bool Translator::BUFFER_STORE(const Decoder::Instruction& inst) {
	const auto      memory   = MemoryInfoFromDecoded(inst);
	const auto      resource = GetBufferResource(memory);
	const auto      address  = ReadBufferAddress(inst, 1);
	const auto      data_src = MemorySourceAt(inst, 0);
	const auto      data     = ReadU32(data_src);
	IR::ValueOpcode opcode;
	IR::Value       value;
	switch (memory.data_bits) {
		case 8u:
			opcode = IR::ValueOpcode::StoreBufferU8;
			value  = NarrowSubdword(data, 8u);
			break;
		case 16u:
			opcode = IR::ValueOpcode::StoreBufferU16;
			value  = NarrowSubdword(data, 16u);
			break;
		case 32u:
			switch (memory.data_dwords) {
				case 1u:
					opcode = IR::ValueOpcode::StoreBufferU32;
					value  = data;
					break;
				case 2u:
					opcode = IR::ValueOpcode::StoreBufferU32x2;
					value  = ir.Emit(IR::ValueOpcode::CompositeConstructU32x2,
					                 {data, ReadU32(OffsetOperand(data_src, 1u))});
					break;
				case 3u:
					opcode = IR::ValueOpcode::StoreBufferU32x3;
					value  = ir.Emit(IR::ValueOpcode::CompositeConstructU32x3,
					                 {data, ReadU32(OffsetOperand(data_src, 1u)),
					                  ReadU32(OffsetOperand(data_src, 2u))});
					break;
				case 4u:
					opcode = IR::ValueOpcode::StoreBufferU32x4;
					value  = ir.Emit(IR::ValueOpcode::CompositeConstructU32x4,
					                 {data, ReadU32(OffsetOperand(data_src, 1u)),
					                  ReadU32(OffsetOperand(data_src, 2u)),
					                  ReadU32(OffsetOperand(data_src, 3u))});
					break;
				default: return false;
			}
			break;
		default: return false;
	}
	ir.Emit(opcode, {resource, address.index, address.offset, address.soffset, value, ir.GetExec()},
	        AddMemoryInfo(memory, inst.pc));
	return true;
}

bool Translator::BUFFER_ATOMIC(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetBufferResource(memory);
	const auto address  = ReadBufferAddress(inst, 1);
	const auto data_src = MemorySourceAt(inst, 0);
	const auto flags    = AddMemoryInfo(memory, inst.pc);
	IR::Value  result;
	if (opcode == IR::ValueOpcode::BufferAtomicCmpSwap32) {
		const auto desired    = ReadU32(data_src);
		const auto comparator = ReadU32(OffsetOperand(data_src, 1u));
		result = ir.Emit(opcode,
		                 {resource, address.index, address.offset, address.soffset, desired,
		                  comparator, ir.GetExec()},
		                 flags);
	} else {
		const IR::Value value =
		    memory.data_dwords == 2u ? IR::Value(ReadU64(data_src)) : IR::Value(ReadU32(data_src));
		result = ir.Emit(opcode,
		                 {resource, address.index, address.offset, address.soffset, value,
		                  ir.GetExec()},
		                 flags);
	}
	if (inst.glc) {
		WriteOperand(inst.dst, result);
	}
	return true;
}

bool Translator::IMAGE_ATOMIC(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 1));
	const auto result =
	    ir.Emit(opcode, {resource, address, ReadU32(MemorySourceAt(inst, 0)), ir.GetExec()},
	            AddMemoryInfo(memory, inst.pc));
	if (inst.glc) {
		WriteOperand(inst.dst, result);
	}
	return true;
}

bool Translator::DS_ATOMIC(const Decoder::Instruction& inst, IR::ValueOpcode opcode,
                           bool returns_value) {
	const auto memory  = MemoryInfoFromDecoded(inst);
	const auto address = ReadU32(MemorySourceAt(inst, 1));
	const auto result  = ir.Emit(opcode, {address, ReadU32(MemorySourceAt(inst, 0)), ir.GetExec()},
	                             AddMemoryInfo(memory, inst.pc));
	if (returns_value) {
		WriteOperand(inst.dst, result);
	}
	return true;
}

bool Translator::FLAT_LOAD(const Decoder::Instruction& inst) {
	const auto      memory = MemoryInfoFromDecoded(inst);
	IR::ValueOpcode opcode;
	const auto      bits = memory.data_bits;
	const auto      sign = memory.data_signed;
	switch (bits) {
		case 8u: opcode = IR::ValueOpcode::LoadAddressU8; break;
		case 16u: opcode = IR::ValueOpcode::LoadAddressU16; break;
		case 32u: opcode = IR::ValueOpcode::LoadAddressU32; break;
		default: return false;
	}
	const auto address = ReadAddressOperands(inst, 0);
	const auto active  = ir.GetExec();
	const auto count   = bits == 32u ? std::min(memory.data_dwords, 4u) : 1u;
	for (uint32_t index = 0; index < count; index++) {
		auto component = memory;
		component.offset += index * 4u;
		component.data_dwords     = 1u;
		component.component_index = index;
		const auto loaded = ir.Emit(opcode, {address.resource, address.low, address.high, active},
		                            AddMemoryInfo(component, inst.pc));
		WriteOperand(OffsetOperand(inst.dst, index),
		             bits == 32u ? loaded : WidenSubdword(loaded, bits, sign));
	}
	return true;
}

bool Translator::FLAT_STORE(const Decoder::Instruction& inst) {
	const auto      memory  = MemoryInfoFromDecoded(inst);
	const auto      data_op = MemorySourceAt(inst, 0);
	const auto      address = ReadAddressOperands(inst, 1);
	IR::ValueOpcode opcode;
	switch (memory.data_bits) {
		case 8u: opcode = IR::ValueOpcode::StoreAddressU8; break;
		case 16u: opcode = IR::ValueOpcode::StoreAddressU16; break;
		case 32u: opcode = IR::ValueOpcode::StoreAddressU32; break;
		default: return false;
	}
	const auto count = memory.data_bits == 32u ? memory.data_dwords : 1u;
	for (uint32_t index = 0; index < count; index++) {
		auto component = memory;
		component.offset += index * 4u;
		component.data_dwords     = 1u;
		component.component_index = index;
		auto value                = IR::Value(ReadU32(OffsetOperand(data_op, index)));
		if (memory.data_bits != 32u) {
			value = NarrowSubdword(IR::U32(value), memory.data_bits);
		}
		ir.Emit(opcode, {address.resource, address.low, address.high, value, ir.GetExec()},
		        AddMemoryInfo(component, inst.pc));
	}
	return true;
}

bool Translator::IMAGE_GET_RESINFO(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));
	const auto result   = ir.Emit(IR::ValueOpcode::ImageQueryDimensions, {resource, address},
	                              AddMemoryInfo(memory, inst.pc));
	WriteImageComponents(inst.dst, result, memory, 4u);
	return true;
}

bool Translator::IMAGE_GET_LOD(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto sampler  = GetSamplerResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));
	const auto result   = ir.Emit(IR::ValueOpcode::ImageQueryLod, {resource, sampler, address},
	                              AddMemoryInfo(memory, inst.pc));
	WriteImageComponents(inst.dst, result, memory, 2u);
	return true;
}

bool Translator::IMAGE_LOAD(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));
	const auto result   = ir.Emit(IR::ValueOpcode::ImageRead, {resource, address, ir.GetExec()},
	                              AddMemoryInfo(memory, inst.pc));
	WriteImageComponents(inst.dst, result, memory, 4u);
	return true;
}

bool Translator::IMAGE_STORE(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 1));
	const auto data     = ConstructU32x4(MemorySourceAt(inst, 0), memory.data_dwords);
	ir.Emit(IR::ValueOpcode::ImageWrite, {resource, address, data, ir.GetExec()},
	        AddMemoryInfo(memory, inst.pc));
	return true;
}

bool Translator::IMAGE_SAMPLE(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto sampler  = GetSamplerResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));
	const auto result   = ir.Emit(IR::ValueOpcode::ImageSampleRaw, {resource, sampler, address},
	                              AddMemoryInfo(memory, inst.pc));
	const bool dref     = (memory.image_sample_flags & Decoder::ImageSampleFlagCompare) != 0u;
	if (dref && memory.data_bits != 16u) {
		const auto component =
		    ir.Emit(IR::ValueOpcode::CompositeExtractU32x4, {result, IR::Value(0u)});
		for (uint32_t index = 0; index < memory.data_dwords; index++) {
			WriteOperand(OffsetOperand(inst.dst, index), component);
		}
	} else {
		WriteImageComponents(inst.dst, result, memory, 4u);
	}
	return true;
}

bool Translator::IMAGE_GATHER(const Decoder::Instruction& inst) {
	const auto memory   = MemoryInfoFromDecoded(inst);
	const auto resource = GetImageResource(memory);
	const auto sampler  = GetSamplerResource(memory);
	const auto address  = MakeImageAddress(inst, MemorySourceAt(inst, 0));
	const auto result   = ir.Emit(IR::ValueOpcode::ImageGatherRaw, {resource, sampler, address},
	                              AddMemoryInfo(memory, inst.pc));
	for (uint32_t index = 0; index < memory.data_dwords; index++) {
		WriteOperand(OffsetOperand(inst.dst, index),
		             ir.Emit(IR::ValueOpcode::CompositeExtractU32x4, {result, IR::Value(index)}));
	}
	return true;
}

// IMAGE_BVH_INTERSECT_RAY / IMAGE_BVH64_INTERSECT_RAY (RDNA2 hardware ray tracing).
//
// The hardware tests one ray against one BVH node and returns 4 dwords:
//   box node (types 4 = fp16 boxes, 5 = fp32 boxes): the 4 child node pointers whose boxes
//     were hit, optionally sorted by the descriptor box sort heuristic, misses = 0xffffffff;
//   triangle node (types 0 and 1): {t_num, t_denom, i_num, j_num} as raw floats, a miss is
//     encoded as {+inf, 1.0, ...};
//   anything else: 0xffffffff x4.
// The node layouts and the intersection math follow the software fallback in the AMD GPURT
// library (IntersectCommon.hlsl), which is what the closed hardware implements.
// The intersection is emitted branch-free: all node kinds are evaluated and the result is
// selected by node type, so no extra basic blocks are needed inside the translator.
bool Translator::IMAGE_BVH_INTERSECT_RAY(const Decoder::Instruction& inst, bool node64) {
	const auto memory = MemoryInfoFromDecoded(inst);
	const bool a16    = (inst.image_sample_flags & Decoder::ImageSampleFlagA16) != 0u;

	// Debug aid: KYTY_BVH_STUB=1 makes every ray miss without touching BVH memory.
	static const bool stub = std::getenv("KYTY_BVH_STUB") != nullptr;
	if (stub) {
		const IR::Value miss(0xffffffffu);
		WriteImageComponents(inst.dst,
		                     ir.Emit(IR::ValueOpcode::CompositeConstructU32x4, {miss, miss, miss, miss}),
		                     memory, 4u);
		return true;
	}

	constexpr uint32_t InvalidNode = 0xffffffffu;
	constexpr float    Infinity    = std::numeric_limits<float>::infinity();

	const auto U32C = [](uint32_t value) { return IR::U32(IR::Value(value)); };
	const auto F32C = [](float value) { return IR::F32(IR::Value::F32(value)); };

	const auto f32  = [&](IR::U32 value) { return ir.BitCastF32(value); };
	const auto fadd = [&](IR::F32 a, IR::F32 b) {
		return IR::F32(ir.Emit(IR::ValueOpcode::FPAdd32, {a, b}));
	};
	const auto fsub = [&](IR::F32 a, IR::F32 b) {
		return IR::F32(ir.Emit(IR::ValueOpcode::FPSub32, {a, b}));
	};
	const auto fmul = [&](IR::F32 a, IR::F32 b) {
		return IR::F32(ir.Emit(IR::ValueOpcode::FPMul32, {a, b}));
	};
	const auto fmin = [&](IR::F32 a, IR::F32 b) {
		return IR::F32(ir.Emit(IR::ValueOpcode::FPMin32, {a, b}));
	};
	const auto fmax = [&](IR::F32 a, IR::F32 b) {
		return IR::F32(ir.Emit(IR::ValueOpcode::FPMax32, {a, b}));
	};
	const auto flt = [&](IR::F32 a, IR::F32 b) {
		return IR::U1(ir.Emit(IR::ValueOpcode::FPOrdLessThan32, {a, b}));
	};
	const auto fle = [&](IR::F32 a, IR::F32 b) {
		return IR::U1(ir.Emit(IR::ValueOpcode::FPOrdLessThanEqual32, {a, b}));
	};
	const auto fge = [&](IR::F32 a, IR::F32 b) {
		return IR::U1(ir.Emit(IR::ValueOpcode::FPOrdGreaterThanEqual32, {a, b}));
	};
	const auto fgt = [&](IR::F32 a, IR::F32 b) {
		return IR::U1(ir.Emit(IR::ValueOpcode::FPOrdGreaterThan32, {a, b}));
	};
	const auto fnan = [&](IR::F32 a) { return IR::U1(ir.Emit(IR::ValueOpcode::FPIsNan32, {a})); };
	const auto fsel = [&](IR::U1 c, IR::F32 a, IR::F32 b) { return SelectF32(c, a, b); };
	// HLSL-style NaN suppressing min/max, which is what the GPURT reference relies on.
	const auto nmax = [&](IR::F32 a, IR::F32 b) {
		return fsel(fnan(a), b, fsel(fnan(b), a, fmax(a, b)));
	};
	const auto nmin = [&](IR::F32 a, IR::F32 b) {
		return fsel(fnan(a), b, fsel(fnan(b), a, fmin(a, b)));
	};
	const auto half_to_f32 = [&](IR::U32 word, bool high) {
		const IR::U32 bits =
		    high ? ir.ShiftRightLogical(word, U32C(16u)) : ir.BitwiseAnd(word, U32C(0xffffu));
		const auto u16 = ir.Emit(IR::ValueOpcode::ConvertU16U32, {bits});
		const auto f16 = ir.Emit(IR::ValueOpcode::BitCastF16U16, {u16});
		return IR::F32(ir.Emit(IR::ValueOpcode::ConvertF32F16, {f16}));
	};

	using Vec3      = std::array<IR::F32, 3>;
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

	// --- Instruction operands: vaddr plus the NSA registers, same order as MakeImageAddress.
	const auto              base = PlainOperand(MemorySourceAt(inst, 0));
	std::array<IR::U32, 13> comp {};
	const auto              nsa_components =
	    std::min(memory.image_nsa_dwords * 4u, Decoder::MaxImageNsaAddressComponents);
	const auto component_count =
	    std::min<uint32_t>(inst.image_address_components, static_cast<uint32_t>(comp.size()));
	for (uint32_t index = 0; index < component_count; index++) {
		if (index == 0u) {
			comp[index] = ReadRawU32(base);
		} else if (index - 1u < nsa_components) {
			comp[index] =
			    ir.GetVectorReg(static_cast<IR::VectorReg>(memory.image_nsa_addr[index - 1u]));
		} else {
			comp[index] = ReadRawU32(OffsetOperand(base, index));
		}
	}
	for (uint32_t index = component_count; index < comp.size(); index++) {
		comp[index] = U32C(0u);
	}

	uint32_t      cursor  = 0;
	const IR::U32 node_lo = comp[cursor++];
	const IR::U32 node_hi = node64 ? comp[cursor++] : U32C(0u);
	const IR::F32 extent  = f32(comp[cursor++]);
	Vec3          origin {}, dir {}, inv_dir {};
	for (auto& value : origin) {
		value = f32(comp[cursor++]);
	}
	if (!a16) {
		for (auto& value : dir) {
			value = f32(comp[cursor++]);
		}
		for (auto& value : inv_dir) {
			value = f32(comp[cursor++]);
		}
	} else {
		// fp16 pairs: {dir.x, dir.y}, {dir.z, inv_dir.x}, {inv_dir.y, inv_dir.z}
		const IR::U32 w0 = comp[cursor++];
		const IR::U32 w1 = comp[cursor++];
		const IR::U32 w2 = comp[cursor++];
		dir     = {half_to_f32(w0, false), half_to_f32(w0, true), half_to_f32(w1, false)};
		inv_dir = {half_to_f32(w1, true), half_to_f32(w2, false), half_to_f32(w2, true)};
	}

	// --- BVH descriptor (T#, 128-bit):
	//   dword0        = base_address[31:0]
	//   dword1[15:0]  = base_address[47:32]
	//   dword1[22:21] = box sort heuristic (0 closest, 1 largest, 2 midpoint, 3 disabled)
	//   dword1[30:23] = box grow value (ulps)
	//   dword1[31]    = box sort enable
	const IR::U32 desc0 = GetResourceDword(memory.resource, 0);
	const IR::U32 desc1 = GetResourceDword(memory.resource, 1);
	const IR::U32 box_grow =
	    IR::U32(ir.Emit(IR::ValueOpcode::BitFieldUExtract, {desc1, U32C(23u), U32C(8u)}));
	const IR::U32 sort_mode =
	    IR::U32(ir.Emit(IR::ValueOpcode::BitFieldUExtract, {desc1, U32C(21u), U32C(2u)}));
	const IR::U1 sort_enabled =
	    ir.LogicalAnd(ir.INotEqual(ir.BitwiseAnd(desc1, U32C(0x80000000u)), U32C(0u)),
	                  ir.INotEqual(sort_mode, U32C(3u)));

	// --- Node address: the node pointer holds the node type in bits [2:0] and the offset in
	// 64-byte units in bits [31:3]; the hardware computes (base >> 3) + pointer, then << 3.
	const IR::U32 node_type = ir.BitwiseAnd(node_lo, U32C(7u));
	const IR::U32 node_off  = ir.BitwiseAnd(node_lo, U32C(~7u));
	IR::U64       node_addr;
	if (node64) {
		node_addr = IR::U64(ir.Emit(IR::ValueOpcode::ShiftLeftLogical64,
		                            {ir.ConstructU64(node_off, node_hi), U32C(3u)}));
	} else {
		const IR::U64 base64 = ir.ConstructU64(desc0, ir.BitwiseAnd(desc1, U32C(0xffffu)));
		const IR::U64 off64  = IR::U64(ir.Emit(IR::ValueOpcode::ShiftLeftLogical64,
		                                       {ir.ConstructU64(node_off, U32C(0u)), U32C(3u)}));
		node_addr            = IR::U64(ir.Emit(IR::ValueOpcode::IAdd64, {base64, off64}));
	}
	const IR::U32 addr_lo = ir.CompositeExtract(node_addr, 0);
	const IR::U32 addr_hi = ir.CompositeExtract(node_addr, 1);

	const IR::U1 is_box16 = ir.IEqual(node_type, U32C(4u));
	const IR::U1 is_box32 = ir.IEqual(node_type, U32C(5u));
	const IR::U1 is_tri   = ir.ULessThan(node_type, U32C(2u));

	// --- Node memory: dwords 0..15 cover fp16 box nodes (64 bytes) and triangle nodes (64
	// bytes); fp32 box nodes are 128 bytes, so dwords 16..27 are only read for them.
	const auto exec       = ir.GetExec();
	const auto resource   = GetAddressResource(addr_lo, addr_hi);
	const auto load_dword = [&](uint32_t dword, IR::U1 active) {
		IR::MemoryInfo info;
		info.kind            = IR::ResourceKind::Flat;
		info.address_is_full = true;
		info.offset          = dword * sizeof(uint32_t);
		info.data_dwords     = 1u;
		info.data_bits       = 32u;
		info.component_index = 0u;
		info.component_count = 1u;
		return IR::U32(ir.Emit(IR::ValueOpcode::LoadAddressU32,
		                       {resource, addr_lo, addr_hi, active}, AddMemoryInfo(info, inst.pc)));
	};
	std::array<IR::U32, 28> d {};
	const auto              active32 = ir.LogicalAnd(exec, is_box32);
	for (uint32_t index = 0; index < d.size(); index++) {
		d[index] = load_dword(index, index < 16u ? exec : active32);
	}

	// --- Ray vs. box, GPURT fast_intersect_bbox: returns {min_t, max_t, min_of, max_of}.
	struct BoxHit {
		IR::F32 min_t, max_t, min_of, max_of;
	};
	const auto intersect_box = [&](const Vec3& box_min, const Vec3& box_max) {
		Vec3 interval_min {}, interval_max {};
		for (uint32_t axis = 0; axis < 3u; axis++) {
			const IR::F32 t_min    = fmul(fsub(box_min[axis], origin[axis]), inv_dir[axis]);
			const IR::F32 t_max    = fmul(fsub(box_max[axis], origin[axis]), inv_dir[axis]);
			const IR::U1  positive = fge(inv_dir[axis], F32C(0.0f));
			interval_min[axis]     = fsel(positive, t_min, t_max);
			interval_max[axis]     = fsel(positive, t_max, t_min);
		}
		IR::F32       min_of = nmax(nmax(interval_min[0], interval_min[1]), interval_min[2]);
		IR::F32       max_of = nmin(nmin(interval_max[0], interval_max[1]), interval_max[2]);
		const IR::U1  nan    = ir.LogicalOr(fnan(min_of), fnan(max_of));
		const IR::F32 min_t  = fsel(nan, F32C(Infinity), nmax(min_of, F32C(0.0f)));
		const IR::F32 max_t  = fsel(nan, F32C(-Infinity), nmin(max_of, extent));
		min_of               = fsel(fnan(min_of), F32C(0.0f), min_of);
		max_of               = fsel(fnan(max_of), F32C(Infinity), max_of);
		return BoxHit {min_t, max_t, min_of, max_of};
	};

	// Box test against the grown extent, then the optional distance sort
	// (GPURT IntersectNodeBvh4).
	const IR::F32 grow_factor =
	    fadd(F32C(1.0f), fmul(IR::F32(ir.Emit(IR::ValueOpcode::ConvertF32U32, {box_grow})),
	                          F32C(5.960464478e-8f)));
	const auto box_children = [&](const std::array<BoxHit, 4>& hits) {
		std::array<IR::U32, 4> child {};
		std::array<IR::F32, 4> key {};
		for (uint32_t index = 0; index < 4u; index++) {
			const IR::U1 hit = fle(hits[index].min_t, fmul(hits[index].max_t, grow_factor));
			child[index]     = ir.Select(hit, d[index], U32C(InvalidNode));
			const IR::F32 closest  = hits[index].min_t;
			const IR::F32 largest  = fsub(hits[index].min_t, hits[index].max_t);
			const IR::F32 midpoint = fadd(hits[index].min_of, hits[index].max_of);
			key[index]             = fsel(ir.IEqual(sort_mode, U32C(1u)), largest,
			                              fsel(ir.IEqual(sort_mode, U32C(2u)), midpoint, closest));
		}
		auto       sorted_child = child;
		auto       sorted_key   = key;
		const auto sort2        = [&](uint32_t a, uint32_t b) {
			const IR::U1 swap =
			    ir.LogicalOr(ir.LogicalAnd(ir.INotEqual(sorted_child[b], U32C(InvalidNode)),
			                               flt(sorted_key[b], sorted_key[a])),
			                 ir.IEqual(sorted_child[a], U32C(InvalidNode)));
			const IR::U32 new_a = ir.Select(swap, sorted_child[b], sorted_child[a]);
			const IR::U32 new_b = ir.Select(swap, sorted_child[a], sorted_child[b]);
			const IR::F32 key_a = fsel(swap, sorted_key[b], sorted_key[a]);
			const IR::F32 key_b = fsel(swap, sorted_key[a], sorted_key[b]);
			sorted_child[a]     = new_a;
			sorted_child[b]     = new_b;
			sorted_key[a]       = key_a;
			sorted_key[b]       = key_b;
		};
		sort2(0, 2);
		sort2(1, 3);
		sort2(0, 1);
		sort2(2, 3);
		sort2(1, 2);
		for (uint32_t index = 0; index < 4u; index++) {
			child[index] = ir.Select(sort_enabled, sorted_child[index], child[index]);
		}
		return child;
	};

	// fp32 box node: children d[0..3], then 4 x (min.xyz, max.xyz).
	std::array<BoxHit, 4> hits32 {};
	for (uint32_t index = 0; index < 4u; index++) {
		const uint32_t at = 4u + index * 6u;
		hits32[index]     = intersect_box({f32(d[at]), f32(d[at + 1u]), f32(d[at + 2u])},
		                                  {f32(d[at + 3u]), f32(d[at + 4u]), f32(d[at + 5u])});
	}
	const auto box32_result = box_children(hits32);

	// fp16 box node: children d[0..3], then 4 x 3 dwords packed as
	// {min.x | min.y << 16}, {min.z | max.x << 16}, {max.y | max.z << 16}.
	std::array<BoxHit, 4> hits16 {};
	for (uint32_t index = 0; index < 4u; index++) {
		const uint32_t at = 4u + index * 3u;
		hits16[index]     = intersect_box(
		    {half_to_f32(d[at], false), half_to_f32(d[at], true), half_to_f32(d[at + 1u], false)},
		    {half_to_f32(d[at + 1u], true), half_to_f32(d[at + 2u], false),
		     half_to_f32(d[at + 2u], true)});
	}
	const auto box16_result = box_children(hits16);

	// --- Triangle node: 4 vertices; type 0 = (v0, v1, v2), type 1 = (v1, v3, v2),
	// triangle id in dword 15 (GPURT fast_intersect_triangle + SwizzleBarycentrics).
	const IR::U1 is_tri1 = ir.IEqual(node_type, U32C(1u));
	const auto   vertex  = [&](uint32_t index) {
		return Vec3 {f32(d[index * 3u]), f32(d[index * 3u + 1u]), f32(d[index * 3u + 2u])};
	};
	const auto vsel = [&](IR::U1 c, const Vec3& a, const Vec3& b) {
		return Vec3 {fsel(c, a[0], b[0]), fsel(c, a[1], b[1]), fsel(c, a[2], b[2])};
	};
	const Vec3 v0    = vertex(0);
	const Vec3 v1    = vertex(1);
	const Vec3 v2    = vertex(2);
	const Vec3 v3    = vertex(3);
	const Vec3 tri_a = vsel(is_tri1, v1, v0);
	const Vec3 tri_b = vsel(is_tri1, v3, v1);
	const Vec3 tri_c = v2;

	const Vec3    e1     = vsub(tri_b, tri_a);
	const Vec3    e2     = vsub(tri_c, tri_a);
	const Vec3    e3     = vsub(origin, tri_a);
	const Vec3    s1     = cross(dir, e2);
	const Vec3    s2     = cross(e3, e1);
	const IR::F32 rx     = dot(e2, s2);
	const IR::F32 ry     = dot(s1, e1);
	const IR::F32 rz     = dot(e3, s1);
	const IR::F32 rw     = dot(dir, s2);
	const IR::F32 inv_ry = IR::F32(ir.Emit(IR::ValueOpcode::FPRecip32, {ry}));
	const IR::F32 t      = fmul(rx, inv_ry);
	const IR::F32 u      = fmul(rz, inv_ry);
	const IR::F32 v      = fmul(rw, inv_ry);
	IR::U1        missed = ir.LogicalOr(flt(u, F32C(0.0f)), fgt(u, F32C(1.0f)));
	missed               = ir.LogicalOr(missed, flt(v, F32C(0.0f)));
	missed               = ir.LogicalOr(missed, fgt(fadd(u, v), F32C(1.0f)));
	missed               = ir.LogicalOr(missed, flt(t, F32C(0.0f)));
	const IR::F32 tri_x  = fsel(missed, F32C(Infinity), rx);
	const IR::F32 tri_y  = fsel(missed, F32C(1.0f), ry);

	const IR::U32 triangle_id = d[15];
	const IR::U32 id_shift    = ir.ShiftLeftLogical(node_type, U32C(3u));
	const IR::F32 bary0       = fsub(fsub(tri_y, rz), rw);
	const auto    pick_bary   = [&](uint32_t extra_shift) {
		const IR::U32 index = ir.BitwiseAnd(
		    ir.ShiftRightLogical(triangle_id, ir.IAdd(id_shift, U32C(extra_shift))), U32C(3u));
		return fsel(ir.IEqual(index, U32C(0u)), bary0,
		            fsel(ir.IEqual(index, U32C(1u)), rz,
		                 fsel(ir.IEqual(index, U32C(2u)), rw, F32C(0.0f))));
	};
	const std::array<IR::U32, 4> tri_result {ir.BitCastU32(tri_x), ir.BitCastU32(tri_y),
	                                         ir.BitCastU32(pick_bary(0u)),
	                                         ir.BitCastU32(pick_bary(2u))};

	// --- Select by node type and write the 4 result dwords.
	std::array<IR::U32, 4> result {};
	for (uint32_t index = 0; index < 4u; index++) {
		result[index] =
		    ir.Select(is_box32, box32_result[index],
		              ir.Select(is_box16, box16_result[index],
		                        ir.Select(is_tri, tri_result[index], U32C(InvalidNode))));
	}
	WriteImageComponents(inst.dst,
	                     ir.Emit(IR::ValueOpcode::CompositeConstructU32x4,
	                             {result[0], result[1], result[2], result[3]}),
	                     memory, 4u);
	return true;
}

IR::Value Translator::LoadSharedU32(uint32_t width, IR::U32 address, const IR::MemoryInfo& memory,
                                    uint32_t pc) {
	IR::ValueOpcode opcode;
	switch (width) {
		case 1u: opcode = IR::ValueOpcode::LoadSharedU32; break;
		case 2u: opcode = IR::ValueOpcode::LoadSharedU32x2; break;
		case 3u: opcode = IR::ValueOpcode::LoadSharedU32x3; break;
		case 4u: opcode = IR::ValueOpcode::LoadSharedU32x4; break;
		default: EXIT("invalid shared load width");
	}
	return ir.Emit(opcode, {address, ir.GetExec()}, AddMemoryInfo(memory, pc));
}

IR::Value Translator::ExtractSharedU32(IR::Value value, uint32_t width, uint32_t index) {
	if (width == 1u) {
		return value;
	}
	IR::ValueOpcode opcode;
	switch (width) {
		case 2u: opcode = IR::ValueOpcode::CompositeExtractU32x2; break;
		case 3u: opcode = IR::ValueOpcode::CompositeExtractU32x3; break;
		case 4u: opcode = IR::ValueOpcode::CompositeExtractU32x4; break;
		default: EXIT("invalid shared extract width");
	}
	return ir.Emit(opcode, {value, IR::Value(index)});
}

void Translator::WriteSharedU32(uint32_t width, IR::U32 address,
                                const std::array<IR::Value, 4>& values,
                                const IR::MemoryInfo& memory, uint32_t pc) {
	switch (width) {
		case 1u:
			ir.Emit(IR::ValueOpcode::WriteSharedU32, {address, values[0], ir.GetExec()},
			        AddMemoryInfo(memory, pc));
			break;
		case 2u:
			ir.Emit(IR::ValueOpcode::WriteSharedU32x2,
			        {address, values[0], values[1], ir.GetExec()}, AddMemoryInfo(memory, pc));
			break;
		case 3u:
			ir.Emit(IR::ValueOpcode::WriteSharedU32x3,
			        {address, values[0], values[1], values[2], ir.GetExec()},
			        AddMemoryInfo(memory, pc));
			break;
		case 4u:
			ir.Emit(IR::ValueOpcode::WriteSharedU32x4,
			        {address, values[0], values[1], values[2], values[3], ir.GetExec()},
			        AddMemoryInfo(memory, pc));
			break;
		default: EXIT("invalid shared store width");
	}
}

bool Translator::DS_READ(const Decoder::Instruction& inst) {
	const auto memory  = MemoryInfoFromDecoded(inst);
	const auto address = ReadU32(MemorySourceAt(inst, 0));
	if (memory.data_bits == 32u) {
		const auto width  = memory.data_dwords;
		const auto loaded = LoadSharedU32(width, address, memory, inst.pc);
		for (uint32_t index = 0; index < width; index++) {
			WriteOperand(OffsetOperand(inst.dst, index), ExtractSharedU32(loaded, width, index));
		}
		return true;
	}
	const auto opcode =
	    memory.data_bits == 8u ? IR::ValueOpcode::LoadSharedU8 : IR::ValueOpcode::LoadSharedU16;
	const auto loaded = ir.Emit(opcode, {address, ir.GetExec()}, AddMemoryInfo(memory, inst.pc));
	WriteOperand(inst.dst, WidenSubdword(loaded, memory.data_bits, memory.data_signed));
	return true;
}

bool Translator::DS_READ2(const Decoder::Instruction& inst) {
	const auto memory       = MemoryInfoFromDecoded(inst);
	const auto width        = memory.data_dwords / 2u;
	const auto address      = ReadU32(MemorySourceAt(inst, 0));
	auto       first        = memory;
	first.data_dwords       = width;
	first.component_count   = width;
	const auto first_value  = LoadSharedU32(width, address, first, inst.pc);
	IR::Value  second_value = first_value;
	if (memory.secondary_offset != memory.offset) {
		auto second   = first;
		second.offset = memory.secondary_offset;
		second_value  = LoadSharedU32(width, address, second, inst.pc);
	}
	for (uint32_t index = 0; index < width; index++) {
		WriteOperand(OffsetOperand(inst.dst, index), ExtractSharedU32(first_value, width, index));
		WriteOperand(OffsetOperand(inst.dst, width + index),
		             ExtractSharedU32(second_value, width, index));
	}
	return true;
}

bool Translator::DS_WRITE(const Decoder::Instruction& inst) {
	const auto               memory       = MemoryInfoFromDecoded(inst);
	const auto               width        = memory.data_dwords;
	const auto               data_operand = MemorySourceAt(inst, 0);
	std::array<IR::Value, 4> values {};
	for (uint32_t index = 0; index < width; index++) {
		values[index] = ReadU32(OffsetOperand(data_operand, index));
	}
	const auto address = ReadU32(MemorySourceAt(inst, 1));
	if (memory.data_bits == 32u) {
		WriteSharedU32(width, address, values, memory, inst.pc);
		return true;
	}
	const auto opcode =
	    memory.data_bits == 8u ? IR::ValueOpcode::WriteSharedU8 : IR::ValueOpcode::WriteSharedU16;
	ir.Emit(opcode, {address, NarrowSubdword(IR::U32(values[0]), memory.data_bits), ir.GetExec()},
	        AddMemoryInfo(memory, inst.pc));
	return true;
}

bool Translator::DS_WRITE2(const Decoder::Instruction& inst) {
	const auto               memory      = MemoryInfoFromDecoded(inst);
	const auto               width       = memory.data_dwords / 2u;
	const auto               address     = ReadU32(MemorySourceAt(inst, 1));
	const auto               first_data  = MemorySourceAt(inst, 0);
	const auto               second_data = MemorySourceAt(inst, 2);
	std::array<IR::Value, 4> first_values {};
	std::array<IR::Value, 4> second_values {};
	for (uint32_t index = 0; index < width; index++) {
		first_values[index]  = ReadU32(OffsetOperand(first_data, index));
		second_values[index] = ReadU32(OffsetOperand(second_data, index));
	}
	auto first            = memory;
	first.data_dwords     = width;
	first.component_count = width;
	WriteSharedU32(width, address, first_values, first, inst.pc);
	if (memory.secondary_offset != memory.offset) {
		auto second   = first;
		second.offset = memory.secondary_offset;
		WriteSharedU32(width, address, second_values, second, inst.pc);
	}
	return true;
}

bool Translator::DS_MINMAX_F32(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {
	const auto memory = MemoryInfoFromDecoded(inst);
	ir.Emit(opcode,
	        {ReadU32(MemorySourceAt(inst, 1)), ReadU32(MemorySourceAt(inst, 0)),
	         ReadU32(MemorySourceAt(inst, 2)), ir.GetExec()},
	        AddMemoryInfo(memory, inst.pc));
	return true;
}

bool Translator::DS_APPEND_CONSUME(const Decoder::Instruction& inst, IR::ValueOpcode opcode) {
	const auto memory = MemoryInfoFromDecoded(inst);
	WriteOperand(inst.dst, ir.Emit(opcode,
	                               {ReadU32(MemorySourceAt(inst, 0)), ir.GetExec(), ir.GetExecLo(),
	                                ir.GetExecHi()},
	                               AddMemoryInfo(memory, inst.pc)));
	return true;
}

bool Translator::DS_ADDTID(const Decoder::Instruction& inst, bool write) {
	const auto memory = MemoryInfoFromDecoded(inst);
	const auto base =
	    ir.BitwiseAnd(ReadU32(MemorySourceAt(inst, write ? 1u : 0u)), IR::U32(IR::Value(0xffffu)));
	const auto lane    = IR::U32(ir.Emit(IR::ValueOpcode::LaneId));
	const auto address = ir.IAdd(base, ir.ShiftLeftLogical(lane, IR::U32(IR::Value(2u))));
	if (write) {
		ir.Emit(IR::ValueOpcode::WriteSharedU32,
		        {address, ReadU32(MemorySourceAt(inst, 0)), ir.GetExec()},
		        AddMemoryInfo(memory, inst.pc));
	} else {
		WriteOperand(inst.dst, ir.Emit(IR::ValueOpcode::LoadSharedU32, {address, ir.GetExec()},
		                               AddMemoryInfo(memory, inst.pc)));
	}
	return true;
}

bool Translator::DS_SWIZZLE_B32(const Decoder::Instruction& inst) {
	WriteOperand(inst.dst, ir.Emit(IR::ValueOpcode::SwizzleU32,
	                               {ReadU32(MemorySourceAt(inst, 0)),
	                                ReadU32(MemorySourceAt(inst, 1)), ir.GetExec()}));
	return true;
}

bool Translator::DS_BPERMUTE_B32(const Decoder::Instruction& inst) {
	const auto address = ir.IAdd(ReadU32(inst.src0), IR::U32(IR::Value(inst.offset)));
	WriteOperand(inst.dst, ir.Emit(IR::ValueOpcode::BpermuteU32,
	                               {ReadU32(inst.src1), address, ir.GetExec()}));
	return true;
}

bool Translator::EmitMemory(const Decoder::Instruction& inst) {
	switch (inst.opcode) {
		case Decoder::Opcode::S_LOAD_DWORD:
		case Decoder::Opcode::S_LOAD_DWORDX2:
		case Decoder::Opcode::S_LOAD_DWORDX4:
		case Decoder::Opcode::S_LOAD_DWORDX8:
		case Decoder::Opcode::S_LOAD_DWORDX16: return S_LOAD(inst, true);
		case Decoder::Opcode::S_BUFFER_LOAD_DWORD:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX2:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX4:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX8:
		case Decoder::Opcode::S_BUFFER_LOAD_DWORDX16: return S_LOAD(inst, false);

		case Decoder::Opcode::BUFFER_LOAD_UBYTE:
		case Decoder::Opcode::BUFFER_LOAD_SBYTE:
		case Decoder::Opcode::BUFFER_LOAD_USHORT:
		case Decoder::Opcode::BUFFER_LOAD_SSHORT:
		case Decoder::Opcode::BUFFER_LOAD_DWORD:
		case Decoder::Opcode::BUFFER_LOAD_DWORDX2:
		case Decoder::Opcode::BUFFER_LOAD_DWORDX3:
		case Decoder::Opcode::BUFFER_LOAD_DWORDX4:
		case Decoder::Opcode::BUFFER_LOAD_FORMAT_X:
		case Decoder::Opcode::BUFFER_LOAD_FORMAT_XY:
		case Decoder::Opcode::BUFFER_LOAD_FORMAT_XYZ:
		case Decoder::Opcode::BUFFER_LOAD_FORMAT_XYZW:
		case Decoder::Opcode::TBUFFER_LOAD_FORMAT_X:
		case Decoder::Opcode::TBUFFER_LOAD_FORMAT_XY:
		case Decoder::Opcode::TBUFFER_LOAD_FORMAT_XYZ:
		case Decoder::Opcode::TBUFFER_LOAD_FORMAT_XYZW: return BUFFER_LOAD(inst);

		case Decoder::Opcode::BUFFER_STORE_DWORD:
		case Decoder::Opcode::BUFFER_STORE_DWORDX2:
		case Decoder::Opcode::BUFFER_STORE_DWORDX3:
		case Decoder::Opcode::BUFFER_STORE_DWORDX4:
		case Decoder::Opcode::BUFFER_STORE_BYTE:
		case Decoder::Opcode::BUFFER_STORE_SHORT:
		case Decoder::Opcode::BUFFER_STORE_FORMAT_X:
		case Decoder::Opcode::BUFFER_STORE_FORMAT_XY:
		case Decoder::Opcode::BUFFER_STORE_FORMAT_XYZ:
		case Decoder::Opcode::BUFFER_STORE_FORMAT_XYZW:
		case Decoder::Opcode::TBUFFER_STORE_FORMAT_X:
		case Decoder::Opcode::TBUFFER_STORE_FORMAT_XY:
		case Decoder::Opcode::TBUFFER_STORE_FORMAT_XYZ:
		case Decoder::Opcode::TBUFFER_STORE_FORMAT_XYZW: return BUFFER_STORE(inst);

		case Decoder::Opcode::BUFFER_ATOMIC_SWAP:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicSwap32);
		case Decoder::Opcode::BUFFER_ATOMIC_CMPSWAP:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicCmpSwap32);
		case Decoder::Opcode::BUFFER_ATOMIC_SWAP_X2:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicSwap64);
		case Decoder::Opcode::BUFFER_ATOMIC_ADD:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicIAdd32);
		case Decoder::Opcode::BUFFER_ATOMIC_SUB:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicISub32);
		case Decoder::Opcode::BUFFER_ATOMIC_SMIN:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicSMin32);
		case Decoder::Opcode::BUFFER_ATOMIC_UMIN:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicUMin32);
		case Decoder::Opcode::BUFFER_ATOMIC_SMAX:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicSMax32);
		case Decoder::Opcode::BUFFER_ATOMIC_UMAX:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicUMax32);
		case Decoder::Opcode::BUFFER_ATOMIC_AND:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicAnd32);
		case Decoder::Opcode::BUFFER_ATOMIC_OR:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicOr32);
		case Decoder::Opcode::BUFFER_ATOMIC_OR_X2:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicOr64);
		case Decoder::Opcode::BUFFER_ATOMIC_XOR:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicXor32);
		case Decoder::Opcode::BUFFER_ATOMIC_FMIN:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicFMin32);
		case Decoder::Opcode::BUFFER_ATOMIC_FMAX:
			return BUFFER_ATOMIC(inst, IR::ValueOpcode::BufferAtomicFMax32);

		case Decoder::Opcode::DS_ADD_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicIAdd32, false);
		case Decoder::Opcode::DS_ADD_RTN_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicIAdd32, true);
		case Decoder::Opcode::DS_SUB_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicISub32, false);
		case Decoder::Opcode::DS_SUB_RTN_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicISub32, true);
		case Decoder::Opcode::DS_MIN_I32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicSMin32, false);
		case Decoder::Opcode::DS_MIN_RTN_I32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicSMin32, true);
		case Decoder::Opcode::DS_MAX_I32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicSMax32, false);
		case Decoder::Opcode::DS_MAX_RTN_I32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicSMax32, true);
		case Decoder::Opcode::DS_MIN_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicUMin32, false);
		case Decoder::Opcode::DS_MIN_RTN_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicUMin32, true);
		case Decoder::Opcode::DS_MAX_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicUMax32, false);
		case Decoder::Opcode::DS_MAX_RTN_U32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicUMax32, true);
		case Decoder::Opcode::DS_AND_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicAnd32, false);
		case Decoder::Opcode::DS_AND_RTN_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicAnd32, true);
		case Decoder::Opcode::DS_OR_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicOr32, false);
		case Decoder::Opcode::DS_OR_RTN_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicOr32, true);
		case Decoder::Opcode::DS_XOR_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicXor32, false);
		case Decoder::Opcode::DS_XOR_RTN_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicXor32, true);
		case Decoder::Opcode::DS_WRXCHG_RTN_B32:
			return DS_ATOMIC(inst, IR::ValueOpcode::SharedAtomicSwap32, true);

		case Decoder::Opcode::IMAGE_ATOMIC_SWAP:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicSwap32);
		case Decoder::Opcode::IMAGE_ATOMIC_ADD:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicIAdd32);
		case Decoder::Opcode::IMAGE_ATOMIC_UMIN:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicUMin32);
		case Decoder::Opcode::IMAGE_ATOMIC_UMAX:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicUMax32);
		case Decoder::Opcode::IMAGE_ATOMIC_AND:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicAnd32);
		case Decoder::Opcode::IMAGE_ATOMIC_OR:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicOr32);
		case Decoder::Opcode::IMAGE_ATOMIC_XOR:
			return IMAGE_ATOMIC(inst, IR::ValueOpcode::ImageAtomicXor32);

		case Decoder::Opcode::FLAT_LOAD_UBYTE:
		case Decoder::Opcode::FLAT_LOAD_SBYTE:
		case Decoder::Opcode::FLAT_LOAD_USHORT:
		case Decoder::Opcode::FLAT_LOAD_SSHORT:
		case Decoder::Opcode::FLAT_LOAD_DWORD:
		case Decoder::Opcode::FLAT_LOAD_DWORDX2:
		case Decoder::Opcode::FLAT_LOAD_DWORDX3:
		case Decoder::Opcode::FLAT_LOAD_DWORDX4: return FLAT_LOAD(inst);

		case Decoder::Opcode::FLAT_STORE_BYTE:
		case Decoder::Opcode::FLAT_STORE_SHORT:
		case Decoder::Opcode::FLAT_STORE_DWORD:
		case Decoder::Opcode::FLAT_STORE_DWORDX2:
		case Decoder::Opcode::FLAT_STORE_DWORDX3:
		case Decoder::Opcode::FLAT_STORE_DWORDX4: return FLAT_STORE(inst);

		case Decoder::Opcode::IMAGE_GET_RESINFO: return IMAGE_GET_RESINFO(inst);
		case Decoder::Opcode::IMAGE_GET_LOD: return IMAGE_GET_LOD(inst);
		case Decoder::Opcode::IMAGE_LOAD:
		case Decoder::Opcode::IMAGE_LOAD_MIP: return IMAGE_LOAD(inst);
		case Decoder::Opcode::IMAGE_STORE:
		case Decoder::Opcode::IMAGE_STORE_MIP: return IMAGE_STORE(inst);
		case Decoder::Opcode::IMAGE_SAMPLE: return IMAGE_SAMPLE(inst);
		case Decoder::Opcode::IMAGE_GATHER4_LZ:
		case Decoder::Opcode::IMAGE_GATHER4_C:
		case Decoder::Opcode::IMAGE_GATHER4_C_LZ:
		case Decoder::Opcode::IMAGE_GATHER4_LZ_O:
		case Decoder::Opcode::IMAGE_GATHER4_C_O:
		case Decoder::Opcode::IMAGE_GATHER4_C_LZ_O:
		case Decoder::Opcode::IMAGE_GATHER4H: return IMAGE_GATHER(inst);
		case Decoder::Opcode::IMAGE_BVH_INTERSECT_RAY: return IMAGE_BVH_INTERSECT_RAY(inst, false);
		case Decoder::Opcode::IMAGE_BVH64_INTERSECT_RAY: return IMAGE_BVH_INTERSECT_RAY(inst, true);

		case Decoder::Opcode::DS_MIN_F32:
			return DS_MINMAX_F32(inst, IR::ValueOpcode::SharedAtomicFMin32);
		case Decoder::Opcode::DS_MAX_F32:
			return DS_MINMAX_F32(inst, IR::ValueOpcode::SharedAtomicFMax32);
		case Decoder::Opcode::DS_SWIZZLE_B32: return DS_SWIZZLE_B32(inst);
		case Decoder::Opcode::DS_BPERMUTE_B32: return DS_BPERMUTE_B32(inst);
		case Decoder::Opcode::DS_CONSUME:
			return DS_APPEND_CONSUME(inst, IR::ValueOpcode::DataConsume);
		case Decoder::Opcode::DS_APPEND:
			return DS_APPEND_CONSUME(inst, IR::ValueOpcode::DataAppend);
		case Decoder::Opcode::DS_WRITE_ADDTID_B32: return DS_ADDTID(inst, true);
		case Decoder::Opcode::DS_READ_ADDTID_B32: return DS_ADDTID(inst, false);
		case Decoder::Opcode::DS_READ2_B32:
		case Decoder::Opcode::DS_READ2ST64_B32:
		case Decoder::Opcode::DS_READ2_B64:
		case Decoder::Opcode::DS_READ2ST64_B64: return DS_READ2(inst);
		case Decoder::Opcode::DS_READ_I8:
		case Decoder::Opcode::DS_READ_U8:
		case Decoder::Opcode::DS_READ_I16:
		case Decoder::Opcode::DS_READ_U16:
		case Decoder::Opcode::DS_READ_U16_D16:
		case Decoder::Opcode::DS_READ_U16_D16_HI:
		case Decoder::Opcode::DS_READ_B32:
		case Decoder::Opcode::DS_READ_B64:
		case Decoder::Opcode::DS_READ_B96:
		case Decoder::Opcode::DS_READ_B128: return DS_READ(inst);
		case Decoder::Opcode::DS_WRITE2_B32:
		case Decoder::Opcode::DS_WRITE2ST64_B32:
		case Decoder::Opcode::DS_WRITE2_B64:
		case Decoder::Opcode::DS_WRITE2ST64_B64: return DS_WRITE2(inst);
		case Decoder::Opcode::DS_WRITE_B8:
		case Decoder::Opcode::DS_WRITE_B16:
		case Decoder::Opcode::DS_WRITE_B16_D16_HI:
		case Decoder::Opcode::DS_WRITE_B32:
		case Decoder::Opcode::DS_WRITE_B64:
		case Decoder::Opcode::DS_WRITE_B96:
		case Decoder::Opcode::DS_WRITE_B128: return DS_WRITE(inst);
		default: return false;
	}
}

} // namespace Libs::Graphics::ShaderRecompiler::Frontend
