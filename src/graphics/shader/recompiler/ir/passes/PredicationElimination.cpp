#include "graphics/shader/recompiler/ir/passes/PredicationElimination.h"

#include "graphics/shader/recompiler/ir/ShaderIR.h"

#include <cstdlib>
#include <unordered_map>
#include <vector>

namespace Libs::Graphics::ShaderRecompiler::IR {
namespace {

// KYTY_PRED_MODE bisection bits (default all set): 1 = descend LogicalAnd chains when proving
// implication, 2 = LogicalAnd terminal rule, 4 = fold chains through the true slot, 8 = fold
// chains through the false slot, 16 = U1-typed operations count as lane-local pure,
// 32 = process SelectU1 too, 64 = remove selects (else only fold chains), 128 = descend
// LogicalAnd chains when folding select chains, 256 = fold a chain only when the value it
// keeps alive is live past the outer select anyway (no register-pressure growth).
uint32_t Mode() {
	static const uint32_t mode = [] {
		const char* value = std::getenv("KYTY_PRED_MODE");
		return value == nullptr ? 0xffffffffu : static_cast<uint32_t>(std::strtoul(value, nullptr, 0));
	}();
	return mode;
}

bool IsSelect(ValueOpcode opcode) {
	switch (opcode) {
		case ValueOpcode::SelectU1:
		case ValueOpcode::SelectU32:
		case ValueOpcode::SelectF32: return true;
		default: return false;
	}
}

// Operations whose result for a lane depends only on that lane's operands and that have no
// side effects: feeding them garbage for an inactive lane is harmless as long as their own
// result is discarded for that lane. Deliberately excludes subgroup operations (read/write
// lane, ballot, DPP, permutes: they read other lanes' registers, which on GCN keep their
// contents while EXEC is off), memory and image operations (addresses/coordinates must stay
// well defined), resource construction and register-state pseudo operations.
bool IsLaneLocalPure(ValueOpcode opcode) {
	switch (opcode) {
		case ValueOpcode::SelectU1:
		case ValueOpcode::SelectU32:
		case ValueOpcode::SelectF32:
		case ValueOpcode::BitCastU16F16:
		case ValueOpcode::BitCastF16U16:
		case ValueOpcode::BitCastU32F32:
		case ValueOpcode::BitCastF32U32:
		case ValueOpcode::ConvertU16U32:
		case ValueOpcode::ConvertU32U16:
		case ValueOpcode::ConvertU8U32:
		case ValueOpcode::ConvertU32U8:
		case ValueOpcode::ConvertF32F16:
		case ValueOpcode::ConvertF16F32:
		case ValueOpcode::ConvertS32F32:
		case ValueOpcode::ConvertU32F32:
		case ValueOpcode::ConvertF32S32:
		case ValueOpcode::ConvertF32U32:
		case ValueOpcode::CompositeConstructU64:
		case ValueOpcode::CompositeConstructU32x2:
		case ValueOpcode::CompositeConstructU32x3:
		case ValueOpcode::CompositeConstructF32x2:
		case ValueOpcode::CompositeConstructU32x4:
		case ValueOpcode::CompositeExtractU64:
		case ValueOpcode::CompositeExtractU32x2:
		case ValueOpcode::CompositeExtractU32x3:
		case ValueOpcode::CompositeExtractU32x4:
		case ValueOpcode::PackHalf2x16:
		case ValueOpcode::PackSnorm2x16:
		case ValueOpcode::PackUnorm2x16:
		case ValueOpcode::PackFloat2x16Rtz:
		case ValueOpcode::FPAbs32:
		case ValueOpcode::FPNeg32:
		case ValueOpcode::FPSaturate32:
		case ValueOpcode::BitFieldInsert:
		case ValueOpcode::BitFieldUExtract:
		case ValueOpcode::BitFieldSExtract:
		case ValueOpcode::IAdd32:
		case ValueOpcode::IAdd64:
		case ValueOpcode::IAddCarry32:
		case ValueOpcode::ISub32:
		case ValueOpcode::ISub64:
		case ValueOpcode::IMul32:
		case ValueOpcode::IMul64:
		case ValueOpcode::UDiv32:
		case ValueOpcode::SMulHi:
		case ValueOpcode::UMulHi:
		case ValueOpcode::IAbs32:
		case ValueOpcode::ShiftLeftLogical32:
		case ValueOpcode::ShiftLeftLogical64:
		case ValueOpcode::ShiftRightLogical32:
		case ValueOpcode::ShiftRightLogical64:
		case ValueOpcode::ShiftRightArithmetic32:
		case ValueOpcode::ShiftRightArithmetic64:
		case ValueOpcode::BitwiseAnd32:
		case ValueOpcode::BitwiseAnd64:
		case ValueOpcode::BitwiseOr32:
		case ValueOpcode::BitwiseXor32:
		case ValueOpcode::BitwiseNot32:
		case ValueOpcode::BitReverse32:
		case ValueOpcode::BitCount32:
		case ValueOpcode::BitCount64:
		case ValueOpcode::FindUMsb32:
		case ValueOpcode::FindUMsb64:
		case ValueOpcode::FindILsb32:
		case ValueOpcode::SMin32:
		case ValueOpcode::UMin32:
		case ValueOpcode::SMax32:
		case ValueOpcode::UMax32:
		case ValueOpcode::SMinTri32:
		case ValueOpcode::UMinTri32:
		case ValueOpcode::SMaxTri32:
		case ValueOpcode::UMaxTri32:
		case ValueOpcode::SMedTri32:
		case ValueOpcode::UMedTri32:
		case ValueOpcode::SLessThan32:
		case ValueOpcode::SLessThan64:
		case ValueOpcode::ULessThan32:
		case ValueOpcode::ULessThan64:
		case ValueOpcode::IEqual32:
		case ValueOpcode::IEqual64:
		case ValueOpcode::SLessThanEqual32:
		case ValueOpcode::ULessThanEqual32:
		case ValueOpcode::SGreaterThan32:
		case ValueOpcode::UGreaterThan32:
		case ValueOpcode::UGreaterThan64:
		case ValueOpcode::INotEqual32:
		case ValueOpcode::INotEqual64:
		case ValueOpcode::SGreaterThanEqual32:
		case ValueOpcode::UGreaterThanEqual32:
		case ValueOpcode::LogicalOr:
		case ValueOpcode::LogicalAnd:
		case ValueOpcode::LogicalXor:
		case ValueOpcode::LogicalNot:
		case ValueOpcode::FPOrdEqual32:
		case ValueOpcode::FPUnordEqual32:
		case ValueOpcode::FPOrdNotEqual32:
		case ValueOpcode::FPUnordNotEqual32:
		case ValueOpcode::FPOrdLessThan32:
		case ValueOpcode::FPUnordLessThan32:
		case ValueOpcode::FPOrdGreaterThan32:
		case ValueOpcode::FPUnordGreaterThan32:
		case ValueOpcode::FPOrdLessThanEqual32:
		case ValueOpcode::FPUnordLessThanEqual32:
		case ValueOpcode::FPOrdGreaterThanEqual32:
		case ValueOpcode::FPUnordGreaterThanEqual32:
		case ValueOpcode::FPIsNan32:
		case ValueOpcode::FPCmpClass32:
		case ValueOpcode::FPAdd32:
		case ValueOpcode::FPSub32:
		case ValueOpcode::FPFma32:
		case ValueOpcode::FPMul32:
		case ValueOpcode::FPMin32:
		case ValueOpcode::FPMax32:
		case ValueOpcode::FPMinTri32:
		case ValueOpcode::FPMaxTri32:
		case ValueOpcode::FPMedTri32:
		case ValueOpcode::FPRecip32:
		case ValueOpcode::FPRecipIFlag32:
		case ValueOpcode::FPRecipSqrt32:
		case ValueOpcode::FPSqrt:
		case ValueOpcode::FPSin:
		case ValueOpcode::FPCos:
		case ValueOpcode::FPExp2:
		case ValueOpcode::FPLog2:
		case ValueOpcode::FPLdexp:
		case ValueOpcode::FPRoundEven32:
		case ValueOpcode::FPFloor32:
		case ValueOpcode::FPCeil32:
		case ValueOpcode::FPTrunc32:
		case ValueOpcode::FPFract32: return true;
		default: return false;
	}
}

// True when `mask` is false for every lane where `predicate` is false: the same SSA value, or
// a conjunction that contains such a value (EXEC only ever narrows by S_AND_SAVEEXEC / V_CMPX
// inside a divergent region, and V_CMP results are `LogicalAnd(exec, compare)`).
bool ImpliesPredicate(Value mask, Value predicate, bool descend, int depth = 0) {
	mask      = mask.Resolve();
	predicate = predicate.Resolve();
	if (mask == predicate) {
		return true;
	}
	if (mask.IsImmediate()) {
		return mask.GetType() == Type::U1 && !mask.U1();
	}
	if (depth >= 8 || !descend) {
		return false;
	}
	auto* inst = mask.TryInstruction();
	if (inst == nullptr || inst->GetOpcode() != ValueOpcode::LogicalAnd) {
		return false;
	}
	return ImpliesPredicate(inst->Arg(0), predicate, descend, depth + 1) ||
	       ImpliesPredicate(inst->Arg(1), predicate, descend, depth + 1);
}

class Analyzer {
public:
	explicit Analyzer(Value predicate): predicate(predicate) {}

	// Is every consumer of `value` indifferent to what inactive lanes (predicate == false) hold?
	bool Discardable(Inst* value) {
		auto [it, inserted] = memo.try_emplace(value, State::InProgress);
		if (!inserted) {
			return it->second == State::Yes;
		}
		bool result = true;
		for (const auto& use: value->Uses()) {
			if (!UseDiscardable(*use.user, use.operand)) {
				result = false;
				break;
			}
		}
		memo[value] = result ? State::Yes : State::No;
		return result;
	}

private:
	enum class State : uint8_t { InProgress, Yes, No };

	bool UseDiscardable(Inst& user, size_t operand) {
		const auto opcode = user.GetOpcode();
		if (opcode == ValueOpcode::Identity) {
			return Discardable(&user);
		}
		if (IsSelect(opcode) && operand == 1u &&
		    ImpliesPredicate(user.Arg(0), predicate, (Mode() & 1u) != 0u)) {
			// Taken only where the (narrower) predicate holds.
			return true;
		}
		if ((Mode() & 2u) != 0u && opcode == ValueOpcode::LogicalAnd && operand < 2u &&
		    ImpliesPredicate(user.Arg(1u - operand), predicate, (Mode() & 1u) != 0u)) {
			// Masked off wherever the predicate is false (V_CMP results, EXEC narrowing).
			return true;
		}
		if (!IsLaneLocalPure(opcode)) {
			return false;
		}
		if ((Mode() & 16u) == 0u && user.GetType() == Type::U1) {
			return false;
		}
		return Discardable(&user);
	}

	Value                                   predicate;
	std::unordered_map<const Inst*, State> memo;
};

// Select(p, b, Select(p', a, c)) where p' implies... see below. Sequential VGPR writes under one
// EXEC value chain their selects through the "old" operand; each link keeps the previous
// value alive only for lanes where the outer predicate is false, where the inner select
// already produced `c` whenever the inner predicate is false too.
// Program positions (block index << 20 | instruction index) to reason about lifetimes.
struct Positions {
	std::unordered_map<const Inst*, uint32_t> of;
	std::unordered_map<const Inst*, const Block*> block_of;

	explicit Positions(const BlockList& blocks) {
		uint32_t block_index = 0;
		for (auto* block: blocks) {
			uint32_t index = 0;
			for (auto& inst: block->Instructions()) {
				of.emplace(&inst, (block_index << 20u) | index);
				block_of.emplace(&inst, block);
				index++;
			}
			block_index++;
		}
	}

	// Does `value` stay live past `at` regardless of the use `except` (an instruction that will
	// stop using it)? True for immediates and for values used in another block or later in the
	// same block.
	bool LiveAfter(Value value, const Inst& at, const Inst& except) const {
		value = value.Resolve();
		if (value.IsImmediate()) {
			return true;
		}
		auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			return true;
		}
		const auto at_pos   = of.find(&at);
		const auto at_block = block_of.find(&at);
		if (at_pos == of.end() || at_block == block_of.end()) {
			return false;
		}
		for (const auto& use: inst->Uses()) {
			if (use.user == &except) {
				continue;
			}
			const auto ub = block_of.find(use.user);
			if (ub == block_of.end() || ub->second != at_block->second) {
				return true; // another block: lives through
			}
			const auto up = of.find(use.user);
			if (up != of.end() && up->second > at_pos->second) {
				return true;
			}
		}
		return false;
	}
};

bool FoldSelectChain(Inst& inst, const Positions& positions, bool preserve_liveness) {
	const auto condition = inst.Arg(0).Resolve();
	bool       changed   = false;
	if (auto* inner = inst.Arg(2).Resolve().TryInstruction();
	    (Mode() & 8u) != 0u && inner != nullptr && IsSelect(inner->GetOpcode()) &&
	    ImpliesPredicate(inner->Arg(0), condition, (Mode() & 128u) != 0u) &&
	    (!preserve_liveness || (Mode() & 256u) == 0u ||
	     positions.LiveAfter(inner->Arg(2), inst, *inner))) {
		// condition false => inner condition false => inner == inner.false
		inst.SetArg(2, inner->Arg(2).Resolve());
		changed = true;
	}
	if (auto* inner = inst.Arg(1).Resolve().TryInstruction();
	    (Mode() & 4u) != 0u && inner != nullptr && IsSelect(inner->GetOpcode()) &&
	    ImpliesPredicate(condition, inner->Arg(0), (Mode() & 128u) != 0u) &&
	    (!preserve_liveness || (Mode() & 256u) == 0u ||
	     positions.LiveAfter(inner->Arg(1), inst, *inner))) {
		// condition true => inner condition true => inner == inner.true
		inst.SetArg(1, inner->Arg(1).Resolve());
		changed = true;
	}
	return changed;
}

} // namespace

bool PredicationEliminationEnabled() {
	static const bool enabled = [] {
		const char* value = std::getenv("KYTY_PRED_ELIM");
		return value == nullptr || value[0] != '0';
	}();
	return enabled;
}

bool PredicationPreserveLiveness(bool compute_stage) {
	static const int mode = [] {
		const char* value = std::getenv("KYTY_PRED_LIVE");
		return value == nullptr ? 1 : std::atoi(value);
	}();
	return mode == 2 || (mode == 1 && compute_stage);
}

PredicationStats EliminatePredication(const BlockList& blocks, bool preserve_liveness) {
	PredicationStats stats;
	if (!PredicationEliminationEnabled()) {
		return stats;
	}
	Positions positions(blocks);
	std::vector<Inst*> selects;
	for (auto* block: blocks) {
		for (auto& inst: block->Instructions()) {
			if (!IsSelect(inst.GetOpcode())) {
				continue;
			}
			if (FoldSelectChain(inst, positions, preserve_liveness)) {
				stats.folded_chains++;
			}
			if (!inst.Arg(0).Resolve().IsImmediate()) {
				selects.push_back(&inst);
			}
		}
	}
	for (auto* select: selects) {
		if ((Mode() & 64u) == 0u) {
			break;
		}
		if (!IsSelect(select->GetOpcode()) || !select->HasUses()) {
			continue;
		}
		if ((Mode() & 32u) == 0u && select->GetOpcode() == ValueOpcode::SelectU1) {
			continue;
		}
		const auto predicate = select->Arg(0).Resolve();
		const auto new_value = select->Arg(1).Resolve();
		const auto old_value = select->Arg(2).Resolve();
		if (new_value == old_value) {
			continue;
		}
		Analyzer analyzer(predicate);
		if (!analyzer.Discardable(select)) {
			continue;
		}
		select->ReplaceUsesWith(new_value);
		stats.removed_selects++;
	}
	return stats;
}

} // namespace Libs::Graphics::ShaderRecompiler::IR
