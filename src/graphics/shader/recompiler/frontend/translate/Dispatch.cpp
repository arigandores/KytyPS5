#include "common/assert.h"
#include "graphics/shader/recompiler/frontend/translate/Translator.h"

namespace Libs::Graphics::ShaderRecompiler::Frontend {

// In wave32 the VCC mask is vcc_lo alone and vcc_hi is an ordinary SGPR (compilers use it as a
// scratch register or to save EXEC). Route it to its own scalar slot so mask writes to vcc_lo
// cannot clobber it and mask/integer reads of it follow the SGPR rules.
Decoder::Instruction Translator::NormalizeOperands(const Decoder::Instruction& source) const {
	auto inst = source;
	if (current_wave_size != 32u) {
		return inst;
	}
	for (auto* operand: {&inst.dst, &inst.dst2, &inst.src0, &inst.src1, &inst.src2, &inst.src3}) {
		if (operand->kind == Decoder::OperandKind::VccHi) {
			operand->kind = Decoder::OperandKind::Sgpr;
			operand->reg  = IR::VccHiScalarReg;
		}
	}
	return inst;
}

void Translator::TranslateInstruction(const Decoder::Instruction& source) {
	const auto inst = NormalizeOperands(source);
	current_opcode  = inst.opcode;
	current_pc      = inst.pc;

	switch (inst.opcode) {
		case Decoder::Opcode::UNKNOWN:
		case Decoder::Opcode::COUNT:
			EXIT("decoded opcode has no IR translation at pc 0x%08x", inst.pc);
		case Decoder::Opcode::UNSUPPORTED:
			EXIT("unsupported decoded instruction: %s", Decoder::InstructionToString(inst).c_str());
		default: break;
	}

	bool translated = false;
	switch (inst.family) {
		case Decoder::Family::SOP1:
		case Decoder::Family::SOP2:
		case Decoder::Family::SOPK:
		case Decoder::Family::SOPC:
		case Decoder::Family::SOPP: translated = EmitScalar(inst); break;
		case Decoder::Family::VOP1:
		case Decoder::Family::VOP2:
		case Decoder::Family::VOP3:
		case Decoder::Family::VOP3P:
		case Decoder::Family::VOPC: translated = EmitVector(inst); break;
		case Decoder::Family::SMEM:
		case Decoder::Family::MUBUF:
		case Decoder::Family::MTBUF:
		case Decoder::Family::FLAT:
		case Decoder::Family::DS:
		case Decoder::Family::MIMG: translated = EmitMemory(inst); break;
		case Decoder::Family::VINTRP: translated = EmitInterpolation(inst); break;
		case Decoder::Family::EXP:
			EXP(inst);
			translated = true;
			break;
		default: break;
	}

	if (!translated) {
		EXIT("opcode %s at pc 0x%08x has no IR translation",
		     Decoder::InstructionToString(inst).c_str(), inst.pc);
	}
}

} // namespace Libs::Graphics::ShaderRecompiler::Frontend
