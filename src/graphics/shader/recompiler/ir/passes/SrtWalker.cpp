#include "graphics/shader/recompiler/ir/passes/SrtWalker.h"

#include "common/frameStats.h"

#include "common/assert.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"

#include <algorithm>
#include <atomic>
#include <bit>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fmt/format.h>
#include <memory>
#include <unordered_map>
#include <unordered_set>

namespace Libs::Graphics::ShaderRecompiler::IR {
namespace {

constexpr uint64_t AddressMask = 0x0000ffffffffffffull;

const char* StageName(ShaderType stage) {
	switch (stage) {
		case ShaderType::Vertex: return "vertex";
		case ShaderType::Pixel: return "pixel";
		case ShaderType::Fetch: return "fetch";
		case ShaderType::Compute: return "compute";
		default: return "unknown";
	}
}

std::string Diagnostic(const ResourcePlan& program, uint32_t pc, const std::string& message) {
	return fmt::format("shader SRT: hash=0x{:016x} stage={} pc=0x{:08x} {}", program.shader_hash,
	                   StageName(program.stage), pc, message);
}

bool AddSignedAddress(uint64_t base, int64_t offset, uint64_t& result) {
	if (base > AddressMask) {
		return false;
	}
	if (offset < 0) {
		const auto magnitude = uint64_t {0} - static_cast<uint64_t>(offset);
		if (magnitude > base) {
			return false;
		}
		result = base - magnitude;
		return true;
	}
	const auto magnitude = static_cast<uint64_t>(offset);
	if (magnitude > AddressMask - base) {
		return false;
	}
	result = base + magnitude;
	return true;
}

bool IsRawRead(const ResourcePlan& values, const Inst& inst) {
	const auto op = inst.GetOpcode();
	if (op != ValueOpcode::LoadAddressU32 && op != ValueOpcode::ReadConstBuffer) {
		return false;
	}
	const auto index = inst.Flags<MemoryFlags>().index;
	if (index >= values.memory_info.size()) {
		return false;
	}
	const auto kind = values.memory_info[index].kind;
	return (op == ValueOpcode::LoadAddressU32 && kind == ResourceKind::ScalarAddress) ||
	       (op == ValueOpcode::ReadConstBuffer && kind == ResourceKind::ScalarBuffer);
}

bool IsDescriptorHandle(ValueOpcode opcode) {
	switch (opcode) {
		case ValueOpcode::GetBufferResource:
		case ValueOpcode::GetAddressResource:
		case ValueOpcode::GetImageResource:
		case ValueOpcode::GetSamplerResource: return true;
		default: return false;
	}
}

bool IsRuntimeSelect(ValueOpcode op) {
	return op == ValueOpcode::SelectU1 || op == ValueOpcode::SelectU32 ||
	       op == ValueOpcode::SelectF32;
}

bool IsRuntimeUniformOp(ValueOpcode op) {
	switch (op) {
		case ValueOpcode::BitCastU32F32:
		case ValueOpcode::BitCastF32U32:
		case ValueOpcode::ConvertU32F32:
		case ValueOpcode::ConvertF32U32:
		case ValueOpcode::CompositeConstructU64:
		case ValueOpcode::CompositeExtractU64:
		case ValueOpcode::CompositeConstructU32x2:
		case ValueOpcode::CompositeExtractU32x2:
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
		case ValueOpcode::UMin32:
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
		case ValueOpcode::SelectU1:
		case ValueOpcode::SelectU32:
		case ValueOpcode::SelectF32:
		case ValueOpcode::ULessThan32:
		case ValueOpcode::IEqual32:
		case ValueOpcode::UGreaterThan32:
		case ValueOpcode::INotEqual32:
		case ValueOpcode::LogicalOr:
		case ValueOpcode::LogicalAnd:
		case ValueOpcode::LogicalXor:
		case ValueOpcode::LogicalNot:
		case ValueOpcode::FPOrdLessThanEqual32:
		case ValueOpcode::FPOrdGreaterThanEqual32:
		case ValueOpcode::FPIsNan32:
		case ValueOpcode::FPMul32:
		case ValueOpcode::FPTrunc32: return true;
		default: return false;
	}
}

class RuntimeValidator {
public:
	explicit RuntimeValidator(const ResourcePlan& program, RuntimeValueType type)
	    : m_program(program), m_type(type) {}

	bool Run(Value value) { return Validate(value); }

private:
	bool ValidateArguments(const Inst& inst, bool require_uniform) {
		for (size_t index = 0; index < inst.NumArgs(); index++) {
			if (!Validate(inst.Arg(index), require_uniform)) return false;
		}
		return true;
	}

	bool Validate(Value value, bool require_uniform = true) {
		value = value.Resolve();
		// Host floating-point evaluation does not model shader rounding/denormal modes.
		if (m_type == RuntimeValueType::Integer &&
		    TypesOverlap(value.GetType(), Type::F16 | Type::F32 | Type::F32x2)) {
			return false;
		}
		const auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			if (!require_uniform) return true;
			switch (value.GetType()) {
				case Type::U1:
				case Type::U8:
				case Type::U16:
				case Type::U32:
				case Type::U64:
				case Type::F32: return true;
				default: return false;
			}
		}
		// Integer-only dependency checks do not depend on the active EXEC mask.
		if (!require_uniform && m_validated_dependencies.contains(inst)) return true;
		if (!m_visiting.insert(inst).second) {
			return !require_uniform;
		}
		const auto finish = [&](bool valid) {
			m_visiting.erase(inst);
			if (valid && !require_uniform) m_validated_dependencies.insert(inst);
			return valid;
		};
		const auto op = inst->GetOpcode();
		if (op == ValueOpcode::ReadConst) {
			const auto slot = inst->NumArgs() == 2 ? inst->Arg(1).Resolve() : Value {};
			if (inst->NumArgs() != 2 || inst->Arg(0).Resolve().TryInstruction() == nullptr ||
			    inst->Arg(0).Resolve().TryInstruction()->GetOpcode() !=
			        ValueOpcode::GetSrtResource ||
			    !slot.IsImmediate() || slot.GetType() != Type::U32 ||
			    slot.U32() >= m_program.srt_reads.size()) {
				return finish(false);
			}
			if (m_type == RuntimeValueType::Integer) {
				const auto active_mask = m_active_mask;
				m_active_mask          = {};
				const bool valid       = Validate(m_program.srt_reads[slot.U32()].value);
				m_active_mask          = active_mask;
				if (!valid) return finish(false);
			}
		}
		if (!require_uniform) return finish(ValidateArguments(*inst, false));
		if (!m_active_mask.IsEmpty() && IsRuntimeSelect(op) && inst->NumArgs() == 3 &&
		    inst->Arg(0).Resolve() == m_active_mask) {
			// Empty EXEC reads lane zero, so ignored operands still require integer types.
			if (m_type == RuntimeValueType::Integer && !Validate(inst->Arg(2), false)) {
				return finish(false);
			}
			return finish(Validate(inst->Arg(1)));
		}
		if (op == ValueOpcode::UndefU1 || op == ValueOpcode::UndefU8 ||
		    op == ValueOpcode::UndefU16 || op == ValueOpcode::UndefU32 ||
		    op == ValueOpcode::UndefU64 || op == ValueOpcode::Void) {
			return finish(false);
		}
		if (op == ValueOpcode::GetUserData) {
			if (inst->NumArgs() != 1 || inst->Arg(0).GetType() != Type::ScalarReg) {
				return finish(false);
			}
			const auto reg = RegIndex(inst->Arg(0).ScalarRegister());
			if (reg < m_program.user_data_base ||
			    reg - m_program.user_data_base >= m_program.user_data_count) {
				return finish(false);
			}
			return finish(true);
		}
		if (op == ValueOpcode::GetShaderBase) {
			if (inst->NumArgs() != 0) {
				return finish(false);
			}
			return finish(true);
		}
		if (op == ValueOpcode::Phi) {
			if (m_type == RuntimeValueType::Integer && !ValidateArguments(*inst, false)) {
				return finish(false);
			}
			const auto invariant = ResolveInvariantPhi(m_program, value);
			if (invariant.IsEmpty()) {
				return finish(false);
			}
			return finish(Validate(invariant));
		}
		if (op == ValueOpcode::ReadFirstLane) {
			if (inst->NumArgs() != 2 || inst->Arg(0).GetType() != Type::U32 ||
			    inst->Arg(1).GetType() != Type::U1) {
				return finish(false);
			}
			if (m_type == RuntimeValueType::Integer && !Validate(inst->Arg(1), false)) {
				return finish(false);
			}
			const auto active_mask = m_active_mask;
			m_active_mask          = inst->Arg(1).Resolve();
			const bool valid       = Validate(inst->Arg(0));
			m_active_mask          = active_mask;
			return finish(valid);
		}
		if (op == ValueOpcode::GetSrtResource) {
			if (inst->NumArgs() != 0) {
				return finish(false);
			}
			return finish(true);
		}
		if (op == ValueOpcode::LoadAddressU32 || op == ValueOpcode::ReadConstBuffer) {
			const auto  expected = op == ValueOpcode::LoadAddressU32
			                           ? ValueOpcode::GetAddressResource
			                           : ValueOpcode::GetBufferResource;
			const auto* handle = inst->NumArgs() != 0 ? inst->Arg(0).ResolveInstruction() : nullptr;
			if (!IsRawRead(m_program, *inst) || handle == nullptr ||
			    handle->GetOpcode() != expected) {
				return finish(false);
			}
		} else if (op == ValueOpcode::CompositeExtractU64) {
			const auto index = inst->NumArgs() == 2 ? inst->Arg(1).Resolve() : Value {};
			if (!index.IsImmediate() || index.GetType() != Type::U32 || index.U32() >= 2u) {
				return finish(false);
			}
		} else if (op == ValueOpcode::CompositeExtractU32x2) {
			const auto* source = inst->NumArgs() == 2 ? inst->Arg(0).ResolveInstruction() : nullptr;
			const auto  index  = inst->NumArgs() == 2 ? inst->Arg(1).Resolve() : Value {};
			if (source == nullptr || !index.IsImmediate() || index.GetType() != Type::U32 ||
			    index.U32() >= 2u ||
			    (source->GetOpcode() != ValueOpcode::CompositeConstructU32x2 &&
			     source->GetOpcode() != ValueOpcode::IAddCarry32)) {
				return finish(false);
			}
		}
		if (IsDescriptorHandle(op)) {
			size_t expected = 4u;
			if (op == ValueOpcode::GetImageResource) {
				expected = 8u;
			} else if (op == ValueOpcode::GetAddressResource) {
				expected = 2u;
			}
			if (inst->NumArgs() != expected) {
				return finish(false);
			}
		} else if (op != ValueOpcode::ReadConst && op != ValueOpcode::ReadConstBuffer &&
		           op != ValueOpcode::LoadAddressU32 && !IsRuntimeUniformOp(op)) {
			return finish(false);
		}
		return finish(ValidateArguments(*inst, true));
	}

	const ResourcePlan&             m_program;
	RuntimeValueType                m_type;
	Value                           m_active_mask;
	std::unordered_set<const Inst*> m_visiting;
	std::unordered_set<const Inst*> m_validated_dependencies;
};

std::vector<std::pair<uint64_t, uint32_t>>& SrtSlotReferenceStorage() {
	static std::vector<std::pair<uint64_t, uint32_t>> storage;
	return storage;
}

const std::vector<std::pair<uint64_t, uint32_t>>& SrtSlotReference() {
	return SrtSlotReferenceStorage();
}

class PlanBuilder {
public:
	explicit PlanBuilder(Program& program): m_program(program) {}

	void Run() {
		m_program.srt_reads.clear();
		m_program.dynamic_reads.clear();
		for (auto* block: m_program.blocks) {
			for (auto& inst: *block) {
				const auto op = inst.GetOpcode();
				if (op == ValueOpcode::LoadAddressU32 || op == ValueOpcode::ReadConstBuffer) {
					const auto flags = inst.Flags<MemoryFlags>();
					if (flags.index < m_program.memory_info.size()) {
						const auto kind       = m_program.memory_info[flags.index].kind;
						const bool crosswired = (op == ValueOpcode::LoadAddressU32 &&
						                         kind == ResourceKind::ScalarBuffer) ||
						                        (op == ValueOpcode::ReadConstBuffer &&
						                         kind == ResourceKind::ScalarAddress);
						if (crosswired) {
							Fail(flags.pc,
							     fmt::format("{} has incompatible scalar memory metadata",
							                 ValueOpcodeName(op)));
						}
					}
				}
				if (IsDescriptorHandle(inst.GetOpcode())) {
					for (size_t index = 0; index < inst.NumArgs(); index++) {
						Collect(inst.Arg(index), 0);
					}
				}
			}
		}
		for (auto* block: m_program.blocks) {
			for (auto& inst: *block) {
				if (inst.GetOpcode() == ValueOpcode::LoadAddressU32 && IsRawRead(m_program, inst) &&
				    inst.Arg(1).Resolve().IsImmediate() &&
				    ValidateRuntimeValue(m_program, Value(&inst))) {
					Collect(Value(&inst), inst.Flags<MemoryFlags>().pc);
				}
			}
		}
		RenumberToReference();
		PatchReads();
	}

private:
	struct Patch {
		Inst*    inst = nullptr;
		uint32_t slot = 0;
		bool     keep = false;
	};

	[[noreturn]] void Fail(uint32_t pc, const std::string& message) const {
		const auto diagnostic = Diagnostic(m_program, pc, message);
		EXIT("shader SRT planning failed: %s", diagnostic.c_str());
		std::abort();
	}

	void Collect(Value value, uint32_t use_pc) {
		value = value.Resolve();
		if (value.IsImmediate()) {
			return;
		}
		auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			Fail(use_pc, "invalid typed planning value");
		}
		const auto cycle = std::ranges::find(m_visiting, inst);
		if (cycle != m_visiting.end()) {
			const auto contains_phi = std::any_of(cycle, m_visiting.end(), [](const Inst* value) {
				return value->GetOpcode() == ValueOpcode::Phi;
			});
			if (contains_phi) {
				return;
			}
			Fail(use_pc, fmt::format("cyclic typed planning value {} without a phi",
			                         ValueOpcodeName(inst->GetOpcode())));
		}
		if (std::ranges::find(m_visited, inst) != m_visited.end()) {
			return;
		}
		m_visiting.push_back(inst);
		for (size_t index = 0; index < inst->NumArgs(); index++) {
			Collect(inst->Arg(index), use_pc);
		}
		m_visiting.pop_back();
		m_visited.push_back(inst);
		if (!IsRawRead(m_program, *inst)) {
			return;
		}
		const auto offset = inst->Arg(1).Resolve();
		if (!offset.IsImmediate() || offset.GetType() != Type::U32) {
			if (std::ranges::find(m_program.dynamic_reads, value) ==
			    m_program.dynamic_reads.end()) {
				m_program.dynamic_reads.push_back(value);
			}
			return;
		}
		for (uint32_t slot = 0; slot < m_program.srt_reads.size(); slot++) {
			if (EquivalentValue(m_program, value, m_program.srt_reads[slot].value)) {
				m_patches.push_back({inst, slot, false});
				return;
			}
		}
		const auto slot = static_cast<uint32_t>(m_program.srt_reads.size());
		m_program.srt_reads.push_back({value, slot});
		m_patches.push_back({inst, slot, true});
	}

	// Offline stand (KYTY_RECOMPILE): give every collected read the slot the reference plan used
	// for the same load (matched by MemoryFlags: memory index + pc). Reads the reference does not
	// know stay real loads (their patch is dropped); reference slots nobody reads any more are
	// filled with a duplicate of another read so the plan stays dense.
	void RenumberToReference() {
		const auto& reference = SrtSlotReference();
		if (reference.empty()) {
			return;
		}
		const auto            count = m_program.srt_reads.size();
		const auto            ref_count = reference.size();
		std::vector<uint32_t> new_slot(count, UINT32_MAX);
		std::vector<bool>     taken(ref_count, false);
		size_t                matched = 0;
		for (uint32_t slot = 0; slot < count; slot++) {
			const auto* inst = m_program.srt_reads[slot].value.Resolve().TryInstruction();
			if (inst == nullptr) {
				continue;
			}
			const auto key   = inst->Flags<uint64_t>();
			const auto found = std::ranges::find_if(
			    reference, [&](const std::pair<uint64_t, uint32_t>& e) { return e.first == key; });
			if (found == reference.end() || found->second >= ref_count || taken[found->second]) {
				std::fprintf(stderr, "srt plan: read %u %s flags=%016llx: %s (kept as a load)\n",
				             slot, ValueOpcodeName(inst->GetOpcode()).data(),
				             static_cast<unsigned long long>(key),
				             found == reference.end() ? "no reference entry"
				             : found->second >= ref_count ? "reference slot out of range"
				                                          : "reference slot already taken");
				continue;
			}
			new_slot[slot]       = found->second;
			taken[found->second] = true;
			matched++;
		}
		if (matched == 0) {
			std::fprintf(stderr, "srt plan: reference slot numbering not applicable (reads=%zu ref=%zu)\n",
			             count, ref_count);
			return;
		}
		uint32_t first_matched = 0;
		while (first_matched < count && new_slot[first_matched] == UINT32_MAX) {
			first_matched++;
		}
		std::vector<SrtRead> reordered(ref_count);
		for (uint32_t slot = 0; slot < ref_count; slot++) {
			reordered[slot]             = m_program.srt_reads[first_matched];
			reordered[slot].flat_offset = slot;
		}
		for (uint32_t slot = 0; slot < count; slot++) {
			if (new_slot[slot] != UINT32_MAX) {
				reordered[new_slot[slot]]             = m_program.srt_reads[slot];
				reordered[new_slot[slot]].flat_offset = new_slot[slot];
			}
		}
		if (matched != count || matched != ref_count) {
			std::fprintf(stderr, "srt plan: reference numbering: reads=%zu matched=%zu ref=%zu\n",
			             count, matched, ref_count);
		}
		m_program.srt_reads = std::move(reordered);
		std::vector<Patch> patches;
		for (auto& patch: m_patches) {
			if (new_slot[patch.slot] == UINT32_MAX) {
				continue;
			}
			patch.slot = new_slot[patch.slot];
			patches.push_back(patch);
		}
		m_patches = std::move(patches);
	}

	void PatchReads() {
		for (const auto& patch: m_patches) {
			auto* block = patch.inst->Parent();
			auto& list  = block->Instructions();
			auto  where =
			    std::ranges::find_if(list, [&](const Inst& inst) { return &inst == patch.inst; });
			const auto resource =
			    Value(&*block->PrependNewInst(where, ValueOpcode::GetSrtResource));
			const auto flat = Value(&*block->PrependNewInst(where, ValueOpcode::ReadConst,
			                                                {resource, Value(patch.slot)}));
			const auto uses = patch.inst->Uses();
			for (const auto& use: uses) {
				use.user->SetArg(use.operand, flat);
			}
			for (auto& info: m_program.block_info) {
				if (info.condition.Resolve() == Value(patch.inst)) {
					info.condition = flat;
				}
				if (info.indirect_target.Resolve() == Value(patch.inst)) {
					info.indirect_target = flat;
				}
			}
			if (patch.keep) {
				const auto memory = patch.inst->Flags<MemoryFlags>().index;
				if (memory < m_program.memory_info.size()) {
					m_program.memory_info[memory].planning_only = true;
				}
				block->AppendNewInst(ValueOpcode::ReferenceU32, {Value(patch.inst)});
			}
		}
	}

	Program&           m_program;
	std::vector<Inst*> m_visiting;
	std::vector<Inst*> m_visited;
	std::vector<Patch> m_patches;
};

class Evaluator {
public:
	Evaluator(const ResourcePlan& program, const SrtRuntime& runtime,
	          std::span<const uint8_t> clean_flat_slots = {}, Evaluator* clean_evaluator = nullptr,
	          Value active_mask = {})
	    : m_program(program), m_runtime(runtime), m_clean_flat_slots(clean_flat_slots),
	      m_clean_evaluator(clean_evaluator), m_active_mask(active_mask.Resolve()) {}

	bool Evaluate(Value value, uint32_t& result) {
		uint64_t wide = 0;
		if (!EvaluateWide(value, wide)) {
			return false;
		}
		result = static_cast<uint32_t>(wide);
		return true;
	}

	// Human readable reason for the first evaluation failure, for diagnostics only.
	[[nodiscard]] const std::string& Failure() const { return m_failure; }
	// True when a guest memory read failed since the last ClearMemoryReadFailure().
	[[nodiscard]] bool MemoryReadFailed() const { return m_memory_read_failed; }
	void               ClearMemoryReadFailure() { m_memory_read_failed = false; }

private:
	std::string m_failure;
	bool        m_memory_read_failed = false;

	void RecordFailure(std::string reason) {
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::MatFailures, 1);
		}
		if (m_failure.empty()) {
			m_failure = std::move(reason);
		}
	}

public:

private:
	static float Float32(uint64_t bits) {
		return std::bit_cast<float>(static_cast<uint32_t>(bits));
	}

	static uint64_t Float32Bits(float value) { return std::bit_cast<uint32_t>(value); }

	bool EvaluateWide(Value value, uint64_t& result) {
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::MatEvalWide, 1);
		}
		value = value.Resolve();
		if (value.IsImmediate()) {
			switch (value.GetType()) {
				case Type::U1: result = value.U1(); return true;
				case Type::U8: result = value.U8(); return true;
				case Type::U16: result = value.U16(); return true;
				case Type::U32: result = value.U32(); return true;
				case Type::U64: result = value.U64(); return true;
				case Type::F32: result = Float32Bits(value.F32Value()); return true;
				default: return false;
			}
		}
		auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			RecordFailure(fmt::format("value of type {} is not an instruction",
			                          static_cast<unsigned>(value.GetType())));
			return false;
		}
		if (!m_active_mask.IsEmpty() && IsRuntimeSelect(inst->GetOpcode()) &&
		    inst->NumArgs() == 3 && inst->Arg(0).Resolve() == m_active_mask) {
			return EvaluateWide(inst->Arg(1), result);
		}
		{
			const auto& slot = Slot(inst);
			if (slot.state == SlotDone) {
				result = slot.value;
				return true;
			}
			if (slot.state == SlotVisiting) {
				RecordFailure(fmt::format("cyclic dependency through {}",
				                          ValueOpcodeName(inst->GetOpcode())));
				return false;
			}
		}
		Slot(inst).state = SlotVisiting;
		uint64_t out     = 0;
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::MatEvalInsts, 1);
		}
		if (!EvaluateInst(*inst, out)) {
			RecordFailure(fmt::format("cannot evaluate {}", ValueOpcodeName(inst->GetOpcode())));
			// Not memoized (as before): the slot may have moved during the recursion, look it up.
			Slot(inst).state = SlotEmpty;
			return false;
		}
		auto& done = Slot(inst);
		done.state = SlotDone;
		done.value = out;
		result     = out;
		return true;
	}

	bool Arg(const Inst& inst, size_t index, uint64_t& result) {
		return EvaluateWide(inst.Arg(index), result);
	}

	bool EvaluatePhi(const Inst& inst, uint64_t& result) {
		const auto value = ResolveInvariantPhi(m_program, Value(const_cast<Inst*>(&inst)));
		if (!value.IsEmpty()) {
			return EvaluateWide(value, result);
		}
		// The incoming values are not structurally identical (for example a pointer that is
		// reloaded through a different chain on a loop back edge). The snapshot only needs the
		// value the phi has right now, so accept it when every incoming value that can be
		// evaluated at all agrees; self references are the loop back edge and carry no new value.
		bool     have   = false;
		uint64_t agreed = 0;
		for (size_t index = 0; index < inst.NumArgs(); index++) {
			const auto arg = inst.Arg(index).Resolve();
			if (arg.TryInstruction() == &inst) {
				continue;
			}
			uint64_t current = 0;
			// An operand that only becomes valid on a later loop iteration (for example a
			// pointer reloaded from memory the loop has not produced yet) cannot be evaluated
			// at snapshot time; it carries no information about the current value.
			const auto saved_failure = m_failure;
			if (!EvaluateWide(arg, current)) {
				m_failure = saved_failure;
				continue;
			}
			if (have && current != agreed) {
				RecordFailure(fmt::format("phi operands disagree ({:#x} vs {:#x})", agreed, current));
				return false;
			}
			agreed = current;
			have   = true;
		}
		if (!have) {
			RecordFailure("phi has no evaluable operand");
			return false;
		}
		result = agreed;
		return true;
	}

	bool EvaluateExtract(const Inst& inst, uint64_t& result) {
		const auto index = inst.Arg(1).Resolve();
		if (!index.IsImmediate() || index.GetType() != Type::U32) {
			return false;
		}
		const auto component = index.U32();
		if (component >= 2u) {
			return false;
		}
		if (inst.GetOpcode() == ValueOpcode::CompositeExtractU64) {
			uint64_t packed = 0;
			if (!Arg(inst, 0, packed)) {
				return false;
			}
			result = static_cast<uint32_t>(packed >> (component * 32u));
			return true;
		}
		const auto* source = inst.Arg(0).ResolveInstruction();
		if (source == nullptr) {
			return false;
		}
		if (source->GetOpcode() == ValueOpcode::CompositeConstructU32x2) {
			return EvaluateWide(source->Arg(component), result);
		}
		if (source->GetOpcode() == ValueOpcode::IAddCarry32) {
			uint64_t lhs = 0;
			uint64_t rhs = 0;
			if (!Arg(*source, 0, lhs) || !Arg(*source, 1, rhs)) {
				return false;
			}
			const auto sum =
			    static_cast<uint64_t>(static_cast<uint32_t>(lhs)) + static_cast<uint32_t>(rhs);
			result =
			    component == 0u ? static_cast<uint32_t>(sum) : static_cast<uint32_t>(sum >> 32u);
			return true;
		}
		return false;
	}

	bool EvaluateRawRead(const Inst& inst, uint64_t& result) {
		const auto flags = inst.Flags<MemoryFlags>();
		if (flags.index >= m_program.memory_info.size()) {
			return false;
		}
		const auto& mem    = m_program.memory_info[flags.index];
		const auto* handle = inst.Arg(0).ResolveInstruction();
		if (handle == nullptr) {
			return false;
		}
		uint64_t low    = 0;
		uint64_t high   = 0;
		uint64_t offset = 0;
		if (!Arg(*handle, 0, low) || !Arg(*handle, 1, high) || !Arg(inst, 1, offset)) {
			return false;
		}
		const auto base      = ((high << 32u) | static_cast<uint32_t>(low)) & AddressMask;
		const auto immediate = static_cast<int64_t>(static_cast<int32_t>(mem.offset));
		uint64_t   address   = 0;
		if (inst.GetOpcode() == ValueOpcode::ReadConstBuffer) {
			uint64_t records = 0;
			uint64_t word3   = 0;
			if (handle->NumArgs() != 4u || !Arg(*handle, 2, records) || !Arg(*handle, 3, word3)) {
				return false;
			}
			if (immediate < 0) {
				return false;
			}
			const auto byte_offset =
			    static_cast<uint64_t>(immediate) + static_cast<uint32_t>(offset);
			const auto aligned = byte_offset & ~uint64_t {3};
			const auto stride  = (static_cast<uint32_t>(high) >> 16u) & 0x3fffu;
			const auto size = stride == 0u
			                      ? static_cast<uint64_t>(static_cast<uint32_t>(records))
			                      : static_cast<uint64_t>(stride) * static_cast<uint32_t>(records);
			if (aligned > size || size - aligned < sizeof(uint32_t)) {
				return false;
			}
			address = ((base & ~uint64_t {3}) + byte_offset) & ~uint64_t {3};
		} else {
			const auto relative = (immediate & ~int64_t {3}) +
			                      static_cast<int64_t>(static_cast<uint32_t>(offset) & ~3u);
			if (!AddSignedAddress(base & ~uint64_t {3}, relative, address)) {
				return false;
			}
		}
		uint32_t word = 0;
		if (m_runtime.read_memory != nullptr) {
			Common::FrameStats::Scope read_scope(Common::FrameStats::Counter::MatReadNs);
			if (!m_runtime.read_memory(m_runtime.userdata, address, &word)) {
				RecordFailure(fmt::format("guest memory read at 0x{:016x} failed", address));
				m_memory_read_failed = true;
				return false;
			}
		} else {
			std::memcpy(&word, reinterpret_cast<const void*>(address), sizeof(word));
		}
		result = word;
		return true;
	}

	bool EvaluateInst(const Inst& inst, uint64_t& result) {
		uint64_t   a       = 0;
		uint64_t   b       = 0;
		uint64_t   c       = 0;
		const auto binary  = [&]() { return Arg(inst, 0, a) && Arg(inst, 1, b); };
		const auto ternary = [&]() {
			return Arg(inst, 0, a) && Arg(inst, 1, b) && Arg(inst, 2, c);
		};
		switch (inst.GetOpcode()) {
			case ValueOpcode::GetUserData: {
				const auto reg = RegIndex(inst.Arg(0).ScalarRegister());
				if (reg < m_program.user_data_base ||
				    reg - m_program.user_data_base >= m_runtime.user_data.size()) {
					return false;
				}
				result = m_runtime.user_data[reg - m_program.user_data_base];
				return true;
			}
			case ValueOpcode::GetShaderBase: result = m_runtime.shader_base; return true;
			case ValueOpcode::Phi: return EvaluatePhi(inst, result);
			case ValueOpcode::ReadFirstLane: {
				Evaluator active(m_program, m_runtime, m_clean_flat_slots, m_clean_evaluator,
				                 inst.Arg(1));
				return active.EvaluateWide(inst.Arg(0), result);
			}
			case ValueOpcode::BitCastU32F32:
			case ValueOpcode::BitCastF32U32: return Arg(inst, 0, result);
			case ValueOpcode::CompositeExtractU64:
			case ValueOpcode::CompositeExtractU32x2: return EvaluateExtract(inst, result);
			case ValueOpcode::CompositeConstructU64:
				if (!binary()) {
					return false;
				}
				result = static_cast<uint32_t>(a) |
				         (static_cast<uint64_t>(static_cast<uint32_t>(b)) << 32u);
				return true;
			case ValueOpcode::ReadConst: {
				const auto slot = inst.Arg(1).Resolve();
				if (!slot.IsImmediate() || slot.GetType() != Type::U32 ||
				    slot.U32() >= m_program.srt_reads.size()) {
					return false;
				}
				if (slot.U32() < m_clean_flat_slots.size() &&
				    m_clean_flat_slots[slot.U32()] != 0u && m_clean_evaluator != nullptr) {
					return m_clean_evaluator->EvaluateWide(m_program.srt_reads[slot.U32()].value,
					                                       result);
				}
				return EvaluateWide(m_program.srt_reads[slot.U32()].value, result);
			}
			case ValueOpcode::LoadAddressU32:
			case ValueOpcode::ReadConstBuffer:
				if (IsRawRead(m_program, inst)) {
					return EvaluateRawRead(inst, result);
				}
				break;
			case ValueOpcode::IAdd32:
				if (binary()) {
					result = static_cast<uint32_t>(a + b);
					return true;
				}
				return false;
			case ValueOpcode::IAdd64:
				if (binary()) {
					result = a + b;
					return true;
				}
				return false;
			case ValueOpcode::ISub32:
				if (binary()) {
					result = static_cast<uint32_t>(a - b);
					return true;
				}
				return false;
			case ValueOpcode::ISub64:
				if (binary()) {
					result = a - b;
					return true;
				}
				return false;
			case ValueOpcode::IMul32:
				if (binary()) {
					result = static_cast<uint32_t>(a * b);
					return true;
				}
				return false;
			case ValueOpcode::IMul64:
				if (binary()) {
					result = a * b;
					return true;
				}
				return false;
			case ValueOpcode::UMin32:
				if (binary()) {
					result = std::min(static_cast<uint32_t>(a), static_cast<uint32_t>(b));
					return true;
				}
				return false;
			case ValueOpcode::ConvertF32U32:
				if (Arg(inst, 0, a)) {
					result = Float32Bits(static_cast<float>(static_cast<uint32_t>(a)));
					return true;
				}
				return false;
			case ValueOpcode::ConvertU32F32:
				if (Arg(inst, 0, a)) {
					const auto value = Float32(a);
					if (!std::isfinite(value) || value < 0.0f ||
					    static_cast<double>(value) > UINT32_MAX) {
						return false;
					}
					result = static_cast<uint32_t>(value);
					return true;
				}
				return false;
			case ValueOpcode::FPMul32:
				if (binary()) {
					result = Float32Bits(Float32(a) * Float32(b));
					return true;
				}
				return false;
			case ValueOpcode::FPTrunc32:
				if (Arg(inst, 0, a)) {
					result = Float32Bits(std::trunc(Float32(a)));
					return true;
				}
				return false;
			case ValueOpcode::FPIsNan32:
				if (Arg(inst, 0, a)) {
					result = std::isnan(Float32(a));
					return true;
				}
				return false;
			case ValueOpcode::FPOrdLessThanEqual32:
				if (binary()) {
					result = Float32(a) <= Float32(b);
					return true;
				}
				return false;
			case ValueOpcode::FPOrdGreaterThanEqual32:
				if (binary()) {
					result = Float32(a) >= Float32(b);
					return true;
				}
				return false;
			case ValueOpcode::BitwiseAnd32:
				if (binary()) {
					result = static_cast<uint32_t>(a & b);
					return true;
				}
				return false;
			case ValueOpcode::BitwiseAnd64:
				if (binary()) {
					result = a & b;
					return true;
				}
				return false;
			case ValueOpcode::BitwiseOr32:
				if (binary()) {
					result = static_cast<uint32_t>(a | b);
					return true;
				}
				return false;
			case ValueOpcode::BitwiseXor32:
				if (binary()) {
					result = static_cast<uint32_t>(a ^ b);
					return true;
				}
				return false;
			case ValueOpcode::BitwiseNot32:
				if (Arg(inst, 0, a)) {
					result = ~static_cast<uint32_t>(a);
					return true;
				}
				return false;
			case ValueOpcode::ShiftLeftLogical32:
				if (binary()) {
					result = static_cast<uint32_t>(a) << (b & 31u);
					return true;
				}
				return false;
			case ValueOpcode::ShiftLeftLogical64:
				if (binary()) {
					result = a << (b & 63u);
					return true;
				}
				return false;
			case ValueOpcode::ShiftRightLogical32:
				if (binary()) {
					result = static_cast<uint32_t>(a) >> (b & 31u);
					return true;
				}
				return false;
			case ValueOpcode::ShiftRightLogical64:
				if (binary()) {
					result = a >> (b & 63u);
					return true;
				}
				return false;
			case ValueOpcode::ShiftRightArithmetic32:
				if (binary()) {
					result = static_cast<uint32_t>(
					    std::bit_cast<int32_t>(static_cast<uint32_t>(a)) >> (b & 31u));
					return true;
				}
				return false;
			case ValueOpcode::ShiftRightArithmetic64:
				if (binary()) {
					result = static_cast<uint64_t>(std::bit_cast<int64_t>(a) >> (b & 63u));
					return true;
				}
				return false;
			case ValueOpcode::BitFieldUExtract:
				if (ternary()) {
					const auto offset = static_cast<uint32_t>(b);
					const auto width  = static_cast<uint32_t>(c);
					if (offset > 32u || width > 32u - offset) {
						return false;
					}
					const auto mask = width == 32u  ? UINT32_MAX
					                  : width == 0u ? 0u
					                                : (uint32_t {1} << width) - 1u;
					result = width == 0u ? 0u : (static_cast<uint32_t>(a) >> offset) & mask;
					return true;
				}
				return false;
			case ValueOpcode::BitFieldSExtract:
				if (ternary()) {
					const auto offset = static_cast<uint32_t>(b);
					const auto width  = static_cast<uint32_t>(c);
					if (offset > 32u || width > 32u - offset) {
						return false;
					}
					if (width == 0u) {
						result = 0;
						return true;
					}
					const auto mask = width == 32u ? UINT32_MAX : (uint32_t {1} << width) - 1u;
					auto       bits = (static_cast<uint32_t>(a) >> offset) & mask;
					if (width < 32u && (bits & (uint32_t {1} << (width - 1u))) != 0u) {
						bits |= ~mask;
					}
					result = bits;
					return true;
				}
				return false;
			case ValueOpcode::BitFieldInsert: {
				uint64_t d = 0;
				if (!ternary() || !Arg(inst, 3, d)) {
					return false;
				}
				const auto offset = static_cast<uint32_t>(c);
				const auto width  = static_cast<uint32_t>(d);
				if (offset > 32u || width > 32u - offset) {
					return false;
				}
				if (width == 0u) {
					result = static_cast<uint32_t>(a);
					return true;
				}
				const auto mask =
				    width == 32u ? UINT32_MAX : ((uint32_t {1} << width) - 1u) << offset;
				result = (static_cast<uint32_t>(a) & ~mask) |
				         ((static_cast<uint32_t>(b) << offset) & mask);
				return true;
			}
			case ValueOpcode::SelectU32:
			case ValueOpcode::SelectU1:
			case ValueOpcode::SelectF32:
				if (ternary()) {
					result = a != 0u ? b : c;
					return true;
				}
				return false;
			case ValueOpcode::IEqual32:
				if (binary()) {
					result = static_cast<uint32_t>(a) == static_cast<uint32_t>(b);
					return true;
				}
				return false;
			case ValueOpcode::INotEqual32:
				if (binary()) {
					result = static_cast<uint32_t>(a) != static_cast<uint32_t>(b);
					return true;
				}
				return false;
			case ValueOpcode::ULessThan32:
				if (binary()) {
					result = static_cast<uint32_t>(a) < static_cast<uint32_t>(b);
					return true;
				}
				return false;
			case ValueOpcode::UGreaterThan32:
				if (binary()) {
					result = static_cast<uint32_t>(a) > static_cast<uint32_t>(b);
					return true;
				}
				return false;
			case ValueOpcode::LogicalAnd:
				if (binary()) {
					result = (a != 0u) && (b != 0u);
					return true;
				}
				return false;
			case ValueOpcode::LogicalOr:
				if (binary()) {
					result = (a != 0u) || (b != 0u);
					return true;
				}
				return false;
			case ValueOpcode::LogicalXor:
				if (binary()) {
					result = (a != 0u) != (b != 0u);
					return true;
				}
				return false;
			case ValueOpcode::LogicalNot:
				if (Arg(inst, 0, a)) {
					result = a == 0u;
					return true;
				}
				return false;
			case ValueOpcode::UndefU1:
			case ValueOpcode::UndefU8:
			case ValueOpcode::UndefU16:
			case ValueOpcode::UndefU32:
			case ValueOpcode::UndefU64: return false;
			default: break;
		}
		return false;
	}

	// Per-evaluation memo: open addressing keyed by instruction pointer. A snapshot evaluates
	// ~100 values per draw, so this runs once per draw; the previous unordered_map allocated a
	// node per value and the visiting list was scanned linearly.
	enum : uint8_t { SlotEmpty = 0, SlotVisiting = 1, SlotDone = 2 };
	struct TableSlot {
		const Inst* inst  = nullptr;
		uint64_t    value = 0;
		uint8_t     state = SlotEmpty;
	};

	static size_t Hash(const Inst* inst) {
		auto x = static_cast<uint64_t>(reinterpret_cast<uintptr_t>(inst));
		x ^= x >> 17u;
		x *= 0x9E3779B97F4A7C15ull;
		return static_cast<size_t>(x >> 29u);
	}

	void Rehash() {
		auto old = std::move(m_table);
		m_table.assign(old.empty() ? 256u : old.size() * 2u, {});
		m_table_used    = 0;
		const auto mask = m_table.size() - 1u;
		for (const auto& slot: old) {
			if (slot.inst == nullptr) {
				continue;
			}
			auto index = Hash(slot.inst) & mask;
			while (m_table[index].inst != nullptr) {
				index = (index + 1u) & mask;
			}
			m_table[index] = slot;
			m_table_used++;
		}
	}

	// The returned reference is invalidated by the next Slot() call that inserts.
	TableSlot& Slot(const Inst* inst) {
		if (m_table.empty() || m_table_used * 2u >= m_table.size()) {
			Rehash();
		}
		const auto mask  = m_table.size() - 1u;
		auto       index = Hash(inst) & mask;
		for (;;) {
			auto& slot = m_table[index];
			if (slot.inst == inst) {
				return slot;
			}
			if (slot.inst == nullptr) {
				slot.inst = inst;
				m_table_used++;
				return slot;
			}
			index = (index + 1u) & mask;
		}
	}

	const ResourcePlan&      m_program;
	const SrtRuntime&        m_runtime;
	std::span<const uint8_t> m_clean_flat_slots;
	Evaluator*               m_clean_evaluator = nullptr;
	Value                    m_active_mask;
	std::vector<TableSlot>   m_table;
	size_t                   m_table_used = 0;
};

const DescriptorSource* Source(const ResourcePlan& program, uint32_t source) {
	if (source >= program.descriptor_sources.size()) {
		return nullptr;
	}
	return &program.descriptor_sources[source];
}

// Diagnostics: render a value tree (depth limited) for evaluation failure messages.
void DescribeValue(const ResourcePlan& program, Value value, std::string& out, uint32_t depth,
                   std::vector<const Inst*>& seen) {
	value = value.Resolve();
	if (value.IsEmpty()) {
		out += "<empty>";
		return;
	}
	if (value.IsImmediate()) {
		switch (value.GetType()) {
			case Type::U1: out += value.U1() ? "true" : "false"; return;
			case Type::U32: out += fmt::format("{:#x}", value.U32()); return;
			case Type::U64: out += fmt::format("{:#x}", value.U64()); return;
			case Type::F32: out += fmt::format("{}f", value.F32Value()); return;
			default: out += "imm"; return;
		}
	}
	const auto* inst = value.TryInstruction();
	if (inst == nullptr) {
		if (value.GetType() == Type::ScalarReg) {
			out += fmt::format("s{}", static_cast<unsigned>(value.ScalarRegister()));
		} else if (value.GetType() == Type::VectorReg) {
			out += fmt::format("v{}", static_cast<unsigned>(value.VectorRegister()));
		} else {
			out += "?";
		}
		return;
	}
	out += ValueOpcodeName(inst->GetOpcode());
	if (inst->GetOpcode() == ValueOpcode::ReadConst && inst->NumArgs() == 2 &&
	    std::ranges::find(seen, inst) == seen.end() && depth != 0) {
		const auto slot = inst->Arg(1).Resolve();
		if (slot.IsImmediate() && slot.GetType() == Type::U32 &&
		    slot.U32() < program.srt_reads.size()) {
			out += fmt::format("[slot {:#x} = ", slot.U32());
			seen.push_back(inst);
			DescribeValue(program, program.srt_reads[slot.U32()].value, out, depth - 1u, seen);
			seen.pop_back();
			out += "]";
			return;
		}
	}
	if (inst->GetOpcode() == ValueOpcode::LoadAddressU32 ||
	    inst->GetOpcode() == ValueOpcode::ReadConstBuffer) {
		const auto index = inst->Flags<MemoryFlags>().index;
		if (index < program.memory_info.size()) {
			const auto& mem = program.memory_info[index];
			out += fmt::format("[mem{} kind={} off={:#x}]", index, static_cast<unsigned>(mem.kind),
			                   mem.offset);
		}
	}
	if (std::ranges::find(seen, inst) != seen.end()) {
		out += "(<cycle>)";
		return;
	}
	if (depth == 0) {
		out += "(...)";
		return;
	}
	seen.push_back(inst);
	out += "(";
	for (size_t index = 0; index < inst->NumArgs(); index++) {
		if (index != 0) {
			out += ", ";
		}
		DescribeValue(program, inst->Arg(index), out, depth - 1u, seen);
	}
	out += ")";
	seen.pop_back();
}

std::string DescribeValue(const ResourcePlan& program, Value value) {
	std::string              out;
	std::vector<const Inst*> seen;
	DescribeValue(program, value, out, 10u, seen);
	return out;
}

std::string DescribeSourceOwner(const ResourcePlan& program, uint32_t source_index) {
	std::string owner;
	for (uint32_t index = 0; index < program.info.buffers.size(); index++) {
		if (program.info.buffers[index].source == source_index) {
			owner += fmt::format(" buffer{}", index);
		}
	}
	for (uint32_t index = 0; index < program.info.images.size(); index++) {
		if (program.info.images[index].source == source_index) {
			owner += fmt::format(" image{}", index);
		}
	}
	for (uint32_t index = 0; index < program.info.samplers.size(); index++) {
		if (program.info.samplers[index].source == source_index) {
			owner += fmt::format(" sampler{}", index);
		}
	}
	return owner.empty() ? std::string(" <unowned>") : owner;
}


// ---- Compiled snapshot evaluation ----------------------------------------------------------
//
// MaterializeResources runs once per draw and dispatch. The recursive Evaluator above walks the
// IR value graph with a memo table each time (~10 us for ~120 values); the same graph, once
// linearized into a node array in dependency order, evaluates in ~1 us. The compiled form keeps
// the interpreter's semantics: a node fails "hard" (the interpreter returned false) or "soft" (a
// guest memory read failed, the dword becomes 0); on any hard failure the caller falls back to
// the interpreter so diagnostics and edge cases stay identical. KYTY_SRT_VERIFY=1 evaluates both
// and logs mismatches.

} // namespace

struct CompiledSrt {
	enum class Op : uint8_t {
		Const,
		UserData,
		ShaderBase,
		Fail,
		MemRead,
		Add32,
		Add64,
		Sub32,
		Sub64,
		Mul32,
		Mul64,
		UMin32,
		CvtF32U32,
		CvtU32F32,
		FMul32,
		FTrunc32,
		FIsNan32,
		FLe32,
		FGe32,
		And32,
		And64,
		Or32,
		Xor32,
		Not32,
		Shl32,
		Shl64,
		Shr32,
		Shr64,
		Sar32,
		Sar64,
		BfUExt,
		BfSExt,
		BfIns,
		Select,
		IEq32,
		INe32,
		ULt32,
		UGt32,
		LAnd,
		LOr,
		LXor,
		LNot,
		Construct64,
		ExtractCarry,
		Extract64,
		PhiAgree,
	};
	static constexpr uint32_t None = UINT32_MAX;
	// Node status after evaluation.
	static constexpr uint8_t StOk       = 0;
	static constexpr uint8_t StMemFail  = 1; // live guest read failed -> dword 0
	static constexpr uint8_t StHardFail = 2; // interpreter would have failed the dword
	static constexpr uint8_t StCleanMemFail = 3; // read through the clean reader failed

	struct Node {
		Op       op         = Op::Fail;
		uint8_t  comp       = 0; // Extract*: component; MemRead: bit0 = const buffer, bit1 = clean
		uint32_t a          = None;
		uint32_t b          = None;
		uint32_t c          = None;
		uint32_t d          = None;
		uint32_t e          = None;
		uint64_t imm        = 0; // Const value, UserData register, MemRead memory_info index
		uint32_t list_start = 0; // PhiAgree operands in `lists`
		uint32_t list_count = 0;
		bool operator==(const Node&) const = default;
	};

	std::vector<Node>     nodes;
	std::vector<uint32_t> lists;
	std::vector<uint32_t> source_root_start; // per descriptor source -> index into source_roots
	std::vector<uint32_t> source_roots;
	std::vector<uint32_t> flat_roots; // per srt_reads slot (None for variant reads)
	// Per ResourcePlan::control_flow block: the block condition (clean reads), None if absent.
	std::vector<uint32_t> block_condition_roots;
	bool                  valid = false;
};

namespace {

class SrtCompiler {
public:
	SrtCompiler(const ResourcePlan& plan, CompiledSrt& out): m_plan(plan), m_out(out) {}

	bool Run() {
		m_out.source_root_start.resize(m_plan.descriptor_sources.size());
		for (uint32_t index = 0; index < m_plan.descriptor_sources.size(); index++) {
			const auto& source            = m_plan.descriptor_sources[index];
			m_out.source_root_start[index] = static_cast<uint32_t>(m_out.source_roots.size());
			for (uint32_t dword = 0; dword < source.dword_count && dword < source.dwords.size();
			     dword++) {
				m_out.source_roots.push_back(Compile(source.dwords[dword], Ctx {}));
				if (m_failed) {
					return false;
				}
			}
		}
		m_out.flat_roots.assign(m_plan.srt_reads.size(), CompiledSrt::None);
		for (uint32_t slot = 0; slot < m_plan.srt_reads.size(); slot++) {
			const auto& read = m_plan.srt_reads[slot];
			if (read.variant) {
				continue;
			}
			const bool clean =
			    slot < m_plan.clean_flat_slots.size() && m_plan.clean_flat_slots[slot] != 0u;
			m_out.flat_roots[slot] = Compile(read.value, Ctx {nullptr, clean});
			if (m_failed) {
				return false;
			}
		}
		// Resource control flow (upstream): block conditions are evaluated through the clean
		// reader, like the interpreter does.
		m_out.block_condition_roots.assign(m_plan.control_flow.size(), CompiledSrt::None);
		for (uint32_t index = 0; index < m_plan.control_flow.size(); index++) {
			const auto& block = m_plan.control_flow[index];
			if (block.condition.IsEmpty()) {
				continue;
			}
			m_out.block_condition_roots[index] = Compile(block.condition, Ctx {nullptr, true});
			if (m_failed) {
				return false;
			}
		}
		if (std::getenv("KYTY_SRT_PLAN_STATS") != nullptr) {
			const auto reads = std::count_if(m_out.nodes.begin(), m_out.nodes.end(), [](const auto& node) {
				return node.op == CompiledSrt::Op::MemRead;
			});
			std::fprintf(stderr, "SrtPlan: hash=%016llx stage=%u nodes=%zu shared=%u reads=%zu sources=%zu flat=%zu\n",
			             static_cast<unsigned long long>(m_plan.shader_hash), static_cast<unsigned>(m_plan.stage),
			             m_out.nodes.size(), m_shared, static_cast<size_t>(reads),
			             m_plan.descriptor_sources.size(), m_plan.srt_reads.size());
		}
		return true;
	}

private:
	struct Ctx {
		const Inst* mask  = nullptr; // ReadFirstLane active mask (runtime selects take arg 1)
		bool        clean = false;   // reads go through the specialization (GPU-clean) reader
	};
	struct Key {
		const Inst* inst;
		const Inst* mask;
		bool        clean;
		bool        operator==(const Key&) const = default;
	};
	struct KeyHash {
		size_t operator()(const Key& key) const {
			auto x = static_cast<uint64_t>(reinterpret_cast<uintptr_t>(key.inst));
			x ^= static_cast<uint64_t>(reinterpret_cast<uintptr_t>(key.mask)) * 0x9E3779B97F4A7C15ull;
			x ^= key.clean ? 0x51ed27f4ull : 0ull;
			x *= 0xff51afd7ed558ccdull;
			return static_cast<size_t>(x ^ (x >> 32u));
		}
	};
	static constexpr uint32_t Visiting = UINT32_MAX - 1u;

	uint32_t Emit(CompiledSrt::Node node) {
		// Different IR instructions and live/clean walks can compute the same pure value.
		// Share their calculation within this evaluation, but never coalesce memory reads:
		// their reader, ordering and failure behavior must remain unchanged.
		static const bool common_values = [] {
			const auto* value = std::getenv("KYTY_SRT_COMMON_VALUES");
			return value == nullptr || value[0] != '0';
		}();
		const bool share = common_values && node.op != CompiledSrt::Op::MemRead &&
		                   node.op != CompiledSrt::Op::PhiAgree &&
		                   node.op != CompiledSrt::Op::Const;
		if (share) {
			if (const auto found = m_common_values.find(node); found != m_common_values.end()) {
				++m_shared;
				return found->second;
			}
		}
		m_out.nodes.push_back(node);
		const auto index = static_cast<uint32_t>(m_out.nodes.size() - 1u);
		if (share) m_common_values.emplace(node, index);
		return index;
	}
	uint32_t Fail() {
		if (m_fail_node == CompiledSrt::None) {
			CompiledSrt::Node node;
			node.op     = CompiledSrt::Op::Fail;
			m_fail_node = Emit(node);
		}
		return m_fail_node;
	}
	uint32_t Const(uint64_t value) {
		static const bool deduplicate = [] {
			const auto* setting = std::getenv("KYTY_SRT_CONST_DEDUP");
			return setting == nullptr || setting[0] != '0';
		}();
		if (deduplicate) {
			if (const auto found = m_constants.find(value); found != m_constants.end()) {
				return found->second;
			}
		}
		CompiledSrt::Node node;
		node.op  = CompiledSrt::Op::Const;
		node.imm = value;
		const auto index = Emit(node);
		if (deduplicate) m_constants.emplace(value, index);
		return index;
	}
	uint32_t Unary(CompiledSrt::Op op, const Inst& inst, Ctx ctx) {
		CompiledSrt::Node node;
		node.op = op;
		node.a  = Compile(inst.Arg(0), ctx);
		return Emit(node);
	}
	uint32_t Binary(CompiledSrt::Op op, const Inst& inst, Ctx ctx) {
		CompiledSrt::Node node;
		node.op = op;
		node.a  = Compile(inst.Arg(0), ctx);
		node.b  = Compile(inst.Arg(1), ctx);
		return Emit(node);
	}
	uint32_t Ternary(CompiledSrt::Op op, const Inst& inst, Ctx ctx) {
		CompiledSrt::Node node;
		node.op = op;
		node.a  = Compile(inst.Arg(0), ctx);
		node.b  = Compile(inst.Arg(1), ctx);
		node.c  = Compile(inst.Arg(2), ctx);
		return Emit(node);
	}

	uint32_t Compile(Value value, Ctx ctx) {
		if (m_failed) {
			return CompiledSrt::None;
		}
		value = value.Resolve();
		if (value.IsImmediate()) {
			switch (value.GetType()) {
				case Type::U1: return Const(value.U1());
				case Type::U8: return Const(value.U8());
				case Type::U16: return Const(value.U16());
				case Type::U32: return Const(value.U32());
				case Type::U64: return Const(value.U64());
				case Type::F32: return Const(std::bit_cast<uint32_t>(value.F32Value()));
				default: return Fail();
			}
		}
		auto* inst = value.TryInstruction();
		if (inst == nullptr) {
			return Fail();
		}
		if (ctx.mask != nullptr && IsRuntimeSelect(inst->GetOpcode()) && inst->NumArgs() == 3 &&
		    inst->Arg(0).Resolve() == Value(const_cast<Inst*>(ctx.mask))) {
			return Compile(inst->Arg(1), ctx);
		}
		const Key key {inst, ctx.mask, ctx.clean};
		if (const auto found = m_memo.find(key); found != m_memo.end()) {
			// A cycle: the interpreter reports "cyclic dependency" for this operand.
			return found->second == Visiting ? Fail() : found->second;
		}
		m_memo[key]     = Visiting;
		const auto node = CompileInst(*inst, ctx);
		m_memo[key]     = node;
		return node;
	}

	uint32_t CompileExtract(const Inst& inst, Ctx ctx) {
		const auto index = inst.Arg(1).Resolve();
		if (!index.IsImmediate() || index.GetType() != Type::U32) {
			return Fail();
		}
		const auto component = index.U32();
		if (component >= 2u) {
			return Fail();
		}
		if (inst.GetOpcode() == ValueOpcode::CompositeExtractU64) {
			CompiledSrt::Node node;
			node.op   = CompiledSrt::Op::Extract64;
			node.comp = static_cast<uint8_t>(component);
			node.a    = Compile(inst.Arg(0), ctx);
			return Emit(node);
		}
		const auto* source = inst.Arg(0).ResolveInstruction();
		if (source == nullptr) {
			return Fail();
		}
		if (source->GetOpcode() == ValueOpcode::CompositeConstructU32x2) {
			return Compile(source->Arg(component), ctx);
		}
		if (source->GetOpcode() == ValueOpcode::IAddCarry32) {
			CompiledSrt::Node node;
			node.op   = CompiledSrt::Op::ExtractCarry;
			node.comp = static_cast<uint8_t>(component);
			node.a    = Compile(source->Arg(0), ctx);
			node.b    = Compile(source->Arg(1), ctx);
			return Emit(node);
		}
		return Fail();
	}

	uint32_t CompileRawRead(const Inst& inst, Ctx ctx) {
		const auto flags = inst.Flags<MemoryFlags>();
		if (flags.index >= m_plan.memory_info.size()) {
			return Fail();
		}
		const auto* handle = inst.Arg(0).ResolveInstruction();
		if (handle == nullptr) {
			return Fail();
		}
		const bool        const_buffer = inst.GetOpcode() == ValueOpcode::ReadConstBuffer;
		CompiledSrt::Node node;
		node.op   = CompiledSrt::Op::MemRead;
		node.imm  = flags.index;
		node.comp = static_cast<uint8_t>((const_buffer ? 1u : 0u) | (ctx.clean ? 2u : 0u));
		node.a    = Compile(handle->Arg(0), ctx);
		node.b    = Compile(handle->Arg(1), ctx);
		node.c    = Compile(inst.Arg(1), ctx);
		if (const_buffer) {
			if (handle->NumArgs() != 4u) {
				return Fail();
			}
			node.d = Compile(handle->Arg(2), ctx);
			node.e = Compile(handle->Arg(3), ctx);
		}
		return Emit(node);
	}

	uint32_t CompileInst(const Inst& inst, Ctx ctx) {
		using Op = CompiledSrt::Op;
		switch (inst.GetOpcode()) {
			case ValueOpcode::GetUserData: {
				if (inst.NumArgs() < 1 || inst.Arg(0).GetType() != Type::ScalarReg) {
					return Fail();
				}
				CompiledSrt::Node node;
				node.op  = Op::UserData;
				node.imm = RegIndex(inst.Arg(0).ScalarRegister());
				return Emit(node);
			}
			case ValueOpcode::GetShaderBase: {
				CompiledSrt::Node node;
				node.op = Op::ShaderBase;
				return Emit(node);
			}
			case ValueOpcode::Phi: {
				const auto invariant =
				    ResolveInvariantPhi(m_plan, Value(const_cast<Inst*>(&inst)));
				if (!invariant.IsEmpty()) {
					return Compile(invariant, ctx);
				}
				std::vector<uint32_t> operands;
				for (size_t index = 0; index < inst.NumArgs(); index++) {
					const auto arg = inst.Arg(index).Resolve();
					if (arg.TryInstruction() == &inst) {
						continue;
					}
					operands.push_back(Compile(arg, ctx));
				}
				CompiledSrt::Node node;
				node.op         = Op::PhiAgree;
				node.list_start = static_cast<uint32_t>(m_out.lists.size());
				node.list_count = static_cast<uint32_t>(operands.size());
				m_out.lists.insert(m_out.lists.end(), operands.begin(), operands.end());
				return Emit(node);
			}
			case ValueOpcode::ReadFirstLane: {
				if (inst.NumArgs() < 2) {
					return Fail();
				}
				const auto  mask      = inst.Arg(1).Resolve();
				const auto* mask_inst = mask.TryInstruction();
				if (mask_inst == nullptr) {
					m_failed = true; // immediate masks: keep the interpreter
					return CompiledSrt::None;
				}
				return Compile(inst.Arg(0), Ctx {mask_inst, ctx.clean});
			}
			case ValueOpcode::BitCastU32F32:
			case ValueOpcode::BitCastF32U32: return Compile(inst.Arg(0), ctx);
			case ValueOpcode::CompositeExtractU64:
			case ValueOpcode::CompositeExtractU32x2: return CompileExtract(inst, ctx);
			case ValueOpcode::CompositeConstructU64: return Binary(Op::Construct64, inst, ctx);
			case ValueOpcode::ReadConst: {
				if (inst.NumArgs() < 2) {
					return Fail();
				}
				const auto slot = inst.Arg(1).Resolve();
				if (!slot.IsImmediate() || slot.GetType() != Type::U32 ||
				    slot.U32() >= m_plan.srt_reads.size()) {
					return Fail();
				}
				const auto index = slot.U32();
				if (!ctx.clean && index < m_plan.clean_flat_slots.size() &&
				    m_plan.clean_flat_slots[index] != 0u) {
					return Compile(m_plan.srt_reads[index].value, Ctx {nullptr, true});
				}
				return Compile(m_plan.srt_reads[index].value, ctx);
			}
			case ValueOpcode::LoadAddressU32:
			case ValueOpcode::ReadConstBuffer:
				if (IsRawRead(m_plan, inst)) {
					return CompileRawRead(inst, ctx);
				}
				return Fail();
			case ValueOpcode::IAdd32: return Binary(Op::Add32, inst, ctx);
			case ValueOpcode::IAdd64: return Binary(Op::Add64, inst, ctx);
			case ValueOpcode::ISub32: return Binary(Op::Sub32, inst, ctx);
			case ValueOpcode::ISub64: return Binary(Op::Sub64, inst, ctx);
			case ValueOpcode::IMul32: return Binary(Op::Mul32, inst, ctx);
			case ValueOpcode::IMul64: return Binary(Op::Mul64, inst, ctx);
			case ValueOpcode::UMin32: return Binary(Op::UMin32, inst, ctx);
			case ValueOpcode::ConvertF32U32: return Unary(Op::CvtF32U32, inst, ctx);
			case ValueOpcode::ConvertU32F32: return Unary(Op::CvtU32F32, inst, ctx);
			case ValueOpcode::FPMul32: return Binary(Op::FMul32, inst, ctx);
			case ValueOpcode::FPTrunc32: return Unary(Op::FTrunc32, inst, ctx);
			case ValueOpcode::FPIsNan32: return Unary(Op::FIsNan32, inst, ctx);
			case ValueOpcode::FPOrdLessThanEqual32: return Binary(Op::FLe32, inst, ctx);
			case ValueOpcode::FPOrdGreaterThanEqual32: return Binary(Op::FGe32, inst, ctx);
			case ValueOpcode::BitwiseAnd32: return Binary(Op::And32, inst, ctx);
			case ValueOpcode::BitwiseAnd64: return Binary(Op::And64, inst, ctx);
			case ValueOpcode::BitwiseOr32: return Binary(Op::Or32, inst, ctx);
			case ValueOpcode::BitwiseXor32: return Binary(Op::Xor32, inst, ctx);
			case ValueOpcode::BitwiseNot32: return Unary(Op::Not32, inst, ctx);
			case ValueOpcode::ShiftLeftLogical32: return Binary(Op::Shl32, inst, ctx);
			case ValueOpcode::ShiftLeftLogical64: return Binary(Op::Shl64, inst, ctx);
			case ValueOpcode::ShiftRightLogical32: return Binary(Op::Shr32, inst, ctx);
			case ValueOpcode::ShiftRightLogical64: return Binary(Op::Shr64, inst, ctx);
			case ValueOpcode::ShiftRightArithmetic32: return Binary(Op::Sar32, inst, ctx);
			case ValueOpcode::ShiftRightArithmetic64: return Binary(Op::Sar64, inst, ctx);
			case ValueOpcode::BitFieldUExtract: return Ternary(Op::BfUExt, inst, ctx);
			case ValueOpcode::BitFieldSExtract: return Ternary(Op::BfSExt, inst, ctx);
			case ValueOpcode::BitFieldInsert: {
				CompiledSrt::Node node;
				node.op = Op::BfIns;
				node.a  = Compile(inst.Arg(0), ctx);
				node.b  = Compile(inst.Arg(1), ctx);
				node.c  = Compile(inst.Arg(2), ctx);
				node.d  = Compile(inst.Arg(3), ctx);
				return Emit(node);
			}
			case ValueOpcode::SelectU32:
			case ValueOpcode::SelectU1:
			case ValueOpcode::SelectF32: return Ternary(Op::Select, inst, ctx);
			case ValueOpcode::IEqual32: return Binary(Op::IEq32, inst, ctx);
			case ValueOpcode::INotEqual32: return Binary(Op::INe32, inst, ctx);
			case ValueOpcode::ULessThan32: return Binary(Op::ULt32, inst, ctx);
			case ValueOpcode::UGreaterThan32: return Binary(Op::UGt32, inst, ctx);
			case ValueOpcode::LogicalAnd: return Binary(Op::LAnd, inst, ctx);
			case ValueOpcode::LogicalOr: return Binary(Op::LOr, inst, ctx);
			case ValueOpcode::LogicalXor: return Binary(Op::LXor, inst, ctx);
			case ValueOpcode::LogicalNot: return Unary(Op::LNot, inst, ctx);
			default: return Fail();
		}
	}

	const ResourcePlan&                         m_plan;
	CompiledSrt&                                m_out;
	struct NodeHash {
		size_t operator()(const CompiledSrt::Node& node) const {
			uint64_t hash = static_cast<uint8_t>(node.op);
			for (const auto value: {uint64_t(node.comp), uint64_t(node.a), uint64_t(node.b),
			                        uint64_t(node.c), uint64_t(node.d), uint64_t(node.e), node.imm,
			                        uint64_t(node.list_start), uint64_t(node.list_count)}) {
				hash ^= value + 0x9e3779b97f4a7c15ull + (hash << 6u) + (hash >> 2u);
			}
			return static_cast<size_t>(hash);
		}
	};
	std::unordered_map<CompiledSrt::Node, uint32_t, NodeHash> m_common_values;
	uint32_t m_shared = 0;
	std::unordered_map<Key, uint32_t, KeyHash>  m_memo;
	std::unordered_map<uint64_t, uint32_t>       m_constants;
	uint32_t                                    m_fail_node = CompiledSrt::None;
	bool                                        m_failed    = false;
};

const CompiledSrt& GetCompiledSrt(const ResourcePlan& plan) {
	if (plan.srt_compiled == nullptr) {
		auto compiled = std::make_shared<CompiledSrt>();
		SrtCompiler compiler(plan, *compiled);
		compiled->valid = compiler.Run();
		if (!compiled->valid) {
			compiled->nodes.clear();
			compiled->lists.clear();
		}
		plan.srt_compiled = std::move(compiled);
	}
	return *plan.srt_compiled;
}

// Evaluates every node in order; values/status must hold nodes.size() entries.
void EvaluateCompiledNodes(const CompiledSrt& compiled, const ResourcePlan& plan,
                           const SrtRuntime& runtime, uint64_t* values, uint8_t* status) {
	using Op   = CompiledSrt::Op;
	const auto float32 = [](uint64_t bits) { return std::bit_cast<float>(static_cast<uint32_t>(bits)); };
	const auto bits32  = [](float value) { return static_cast<uint64_t>(std::bit_cast<uint32_t>(value)); };
	for (uint32_t index = 0; index < compiled.nodes.size(); index++) {
		const auto& node = compiled.nodes[index];
		uint64_t&   out  = values[index];
		uint8_t&    st   = status[index];
		out              = 0;
		st               = CompiledSrt::StOk;
		// Operands are consumed in argument order; the first failing one decides the status, as the
		// interpreter stopped evaluating there.
		const auto dep = [&](uint32_t operand) noexcept {
			if (operand == CompiledSrt::None) {
				return true;
			}
			if (status[operand] != CompiledSrt::StOk) {
				st = status[operand];
				return false;
			}
			return true;
		};
		const auto A = [&]() { return values[node.a]; };
		const auto B = [&]() { return values[node.b]; };
		const auto C = [&]() { return values[node.c]; };
		switch (node.op) {
			case Op::Const: out = node.imm; break;
			case Op::UserData: {
				const auto reg = node.imm;
				if (reg < plan.user_data_base || reg - plan.user_data_base >= runtime.user_data.size()) {
					st = CompiledSrt::StHardFail;
					break;
				}
				out = runtime.user_data[reg - plan.user_data_base];
				break;
			}
			case Op::ShaderBase: out = runtime.shader_base; break;
			case Op::Fail: st = CompiledSrt::StHardFail; break;
			case Op::MemRead: {
				if (!dep(node.a) || !dep(node.b) || !dep(node.c)) {
					break;
				}
				const auto  low       = A();
				const auto  high      = B();
				const auto  offset    = C();
				const auto& mem       = plan.memory_info[node.imm];
				const auto  base      = ((high << 32u) | static_cast<uint32_t>(low)) & AddressMask;
				const auto  immediate = static_cast<int64_t>(static_cast<int32_t>(mem.offset));
				uint64_t    address   = 0;
				if ((node.comp & 1u) != 0) {
					if (!dep(node.d) || !dep(node.e)) {
						break;
					}
					const auto records = values[node.d];
					if (immediate < 0) {
						st = CompiledSrt::StHardFail;
						break;
					}
					const auto byte_offset =
					    static_cast<uint64_t>(immediate) + static_cast<uint32_t>(offset);
					const auto aligned = byte_offset & ~uint64_t {3};
					const auto stride  = (static_cast<uint32_t>(high) >> 16u) & 0x3fffu;
					const auto size    = stride == 0u
					                      ? static_cast<uint64_t>(static_cast<uint32_t>(records))
					                      : static_cast<uint64_t>(stride) * static_cast<uint32_t>(records);
					if (aligned > size || size - aligned < sizeof(uint32_t)) {
						st = CompiledSrt::StHardFail;
						break;
					}
					address = ((base & ~uint64_t {3}) + byte_offset) & ~uint64_t {3};
				} else {
					const auto relative = (immediate & ~int64_t {3}) +
					                      static_cast<int64_t>(static_cast<uint32_t>(offset) & ~3u);
					if (!AddSignedAddress(base & ~uint64_t {3}, relative, address)) {
						st = CompiledSrt::StHardFail;
						break;
					}
				}
				uint32_t   word   = 0;
				const bool clean  = (node.comp & 2u) != 0;
				const auto reader = clean ? runtime.read_specialization_memory : runtime.read_memory;
				if (reader != nullptr) {
					if (!reader(runtime.userdata, address, &word)) {
						st = clean ? CompiledSrt::StCleanMemFail : CompiledSrt::StMemFail;
						break;
					}
				} else {
					std::memcpy(&word, reinterpret_cast<const void*>(address), sizeof(word));
				}
				out = word;
				break;
			}
			case Op::Add32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() + B()); break;
			case Op::Add64: if (dep(node.a) && dep(node.b)) out = A() + B(); break;
			case Op::Sub32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() - B()); break;
			case Op::Sub64: if (dep(node.a) && dep(node.b)) out = A() - B(); break;
			case Op::Mul32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() * B()); break;
			case Op::Mul64: if (dep(node.a) && dep(node.b)) out = A() * B(); break;
			case Op::UMin32:
				if (dep(node.a) && dep(node.b)) {
					out = std::min(static_cast<uint32_t>(A()), static_cast<uint32_t>(B()));
				}
				break;
			case Op::CvtF32U32:
				if (dep(node.a)) {
					out = bits32(static_cast<float>(static_cast<uint32_t>(A())));
				}
				break;
			case Op::CvtU32F32:
				if (dep(node.a)) {
					const auto value = float32(A());
					if (!std::isfinite(value) || value < 0.0f || static_cast<double>(value) > UINT32_MAX) {
						st = CompiledSrt::StHardFail;
						break;
					}
					out = static_cast<uint32_t>(value);
				}
				break;
			case Op::FMul32: if (dep(node.a) && dep(node.b)) out = bits32(float32(A()) * float32(B())); break;
			case Op::FTrunc32: if (dep(node.a)) out = bits32(std::trunc(float32(A()))); break;
			case Op::FIsNan32: if (dep(node.a)) out = std::isnan(float32(A())) ? 1u : 0u; break;
			case Op::FLe32: if (dep(node.a) && dep(node.b)) out = float32(A()) <= float32(B()) ? 1u : 0u; break;
			case Op::FGe32: if (dep(node.a) && dep(node.b)) out = float32(A()) >= float32(B()) ? 1u : 0u; break;
			case Op::And32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() & B()); break;
			case Op::And64: if (dep(node.a) && dep(node.b)) out = A() & B(); break;
			case Op::Or32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() | B()); break;
			case Op::Xor32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A() ^ B()); break;
			case Op::Not32: if (dep(node.a)) out = ~static_cast<uint32_t>(A()); break;
			case Op::Shl32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) << (B() & 31u); break;
			case Op::Shl64: if (dep(node.a) && dep(node.b)) out = A() << (B() & 63u); break;
			case Op::Shr32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) >> (B() & 31u); break;
			case Op::Shr64: if (dep(node.a) && dep(node.b)) out = A() >> (B() & 63u); break;
			case Op::Sar32:
				if (dep(node.a) && dep(node.b)) {
					out = static_cast<uint32_t>(std::bit_cast<int32_t>(static_cast<uint32_t>(A())) >> (B() & 31u));
				}
				break;
			case Op::Sar64:
				if (dep(node.a) && dep(node.b)) {
					out = static_cast<uint64_t>(std::bit_cast<int64_t>(A()) >> (B() & 63u));
				}
				break;
			case Op::BfUExt:
			case Op::BfSExt: {
				if (!dep(node.a) || !dep(node.b) || !dep(node.c)) {
					break;
				}
				const auto offset = static_cast<uint32_t>(B());
				const auto width  = static_cast<uint32_t>(C());
				if (offset > 32u || width > 32u - offset) {
					st = CompiledSrt::StHardFail;
					break;
				}
				if (width == 0u) {
					out = 0;
					break;
				}
				const auto mask = width == 32u ? UINT32_MAX : (uint32_t {1} << width) - 1u;
				auto       bits = (static_cast<uint32_t>(A()) >> offset) & mask;
				if (node.op == Op::BfSExt && width < 32u && (bits & (uint32_t {1} << (width - 1u))) != 0u) {
					bits |= ~mask;
				}
				out = bits;
				break;
			}
			case Op::BfIns: {
				if (!dep(node.a) || !dep(node.b) || !dep(node.c) || !dep(node.d)) {
					break;
				}
				const auto offset = static_cast<uint32_t>(C());
				const auto width  = static_cast<uint32_t>(values[node.d]);
				if (offset > 32u || width > 32u - offset) {
					st = CompiledSrt::StHardFail;
					break;
				}
				if (width == 0u) {
					out = static_cast<uint32_t>(A());
					break;
				}
				const auto mask = width == 32u ? UINT32_MAX : ((uint32_t {1} << width) - 1u) << offset;
				out = (static_cast<uint32_t>(A()) & ~mask) | ((static_cast<uint32_t>(B()) << offset) & mask);
				break;
			}
			case Op::Select:
				if (dep(node.a) && dep(node.b) && dep(node.c)) {
					out = A() != 0u ? B() : C();
				}
				break;
			case Op::IEq32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) == static_cast<uint32_t>(B()) ? 1u : 0u; break;
			case Op::INe32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) != static_cast<uint32_t>(B()) ? 1u : 0u; break;
			case Op::ULt32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) < static_cast<uint32_t>(B()) ? 1u : 0u; break;
			case Op::UGt32: if (dep(node.a) && dep(node.b)) out = static_cast<uint32_t>(A()) > static_cast<uint32_t>(B()) ? 1u : 0u; break;
			case Op::LAnd: if (dep(node.a) && dep(node.b)) out = (A() != 0u && B() != 0u) ? 1u : 0u; break;
			case Op::LOr: if (dep(node.a) && dep(node.b)) out = (A() != 0u || B() != 0u) ? 1u : 0u; break;
			case Op::LXor: if (dep(node.a) && dep(node.b)) out = ((A() != 0u) != (B() != 0u)) ? 1u : 0u; break;
			case Op::LNot: if (dep(node.a)) out = A() == 0u ? 1u : 0u; break;
			case Op::Construct64:
				if (dep(node.a) && dep(node.b)) {
					out = static_cast<uint32_t>(A()) | (static_cast<uint64_t>(static_cast<uint32_t>(B())) << 32u);
				}
				break;
			case Op::ExtractCarry:
				if (dep(node.a) && dep(node.b)) {
					const auto sum = static_cast<uint64_t>(static_cast<uint32_t>(A())) + static_cast<uint32_t>(B());
					out = node.comp == 0u ? static_cast<uint32_t>(sum) : static_cast<uint32_t>(sum >> 32u);
				}
				break;
			case Op::Extract64:
				if (dep(node.a)) {
					out = static_cast<uint32_t>(A() >> (node.comp * 32u));
				}
				break;
			case Op::PhiAgree: {
				bool     have      = false;
				bool     any_mem   = false;
				bool     any_clean = false;
				uint64_t agreed    = 0;
				bool     disagree  = false;
				for (uint32_t i = 0; i < node.list_count; i++) {
					const auto operand = compiled.lists[node.list_start + i];
					if (status[operand] != CompiledSrt::StOk) {
						any_mem |= status[operand] == CompiledSrt::StMemFail;
						any_clean |= status[operand] == CompiledSrt::StCleanMemFail;
						continue;
					}
					if (have && values[operand] != agreed) {
						disagree = true;
						break;
					}
					agreed = values[operand];
					have   = true;
				}
				if (disagree || !have) {
					st = any_mem ? CompiledSrt::StMemFail
					             : (any_clean ? CompiledSrt::StCleanMemFail : CompiledSrt::StHardFail);
					break;
				}
				out = agreed;
				break;
			}
		}
	}
}

enum class CompiledResult { Done, Unsupported, HardFailure };

// Fast path of EvaluateRuntimeSourcesImpl for the materialization call (all flat slots, the
// plan's own clean-slot table). Returns Unsupported when the plan could not be compiled and
// HardFailure when the interpreter has to reproduce an evaluation failure.
CompiledResult EvaluateCompiled(const ResourcePlan& program, std::span<const uint32_t> sources,
                                const SrtRuntime& runtime, std::vector<DescriptorValue>& results,
                                std::vector<uint32_t>& flat, std::vector<uint8_t>& active_sources) {
	const auto& compiled = GetCompiledSrt(program);
	if (!compiled.valid) {
		return CompiledResult::Unsupported;
	}
	thread_local std::vector<uint64_t> values;
	thread_local std::vector<uint8_t>  status;
	if (values.size() < compiled.nodes.size()) {
		values.resize(compiled.nodes.size());
		status.resize(compiled.nodes.size());
	}
	EvaluateCompiledNodes(compiled, program, runtime, values.data(), status.data());
	// These are scratch arrays, not a cache of guest values: reset every entry on each call.
	struct Scratch {
		std::vector<uint8_t> active, visited;
		std::vector<uint32_t> pending, flattened;
		std::vector<DescriptorValue> evaluated;
	};
	static const bool reuse = [] {
		const auto* value = std::getenv("KYTY_SRT_SCRATCH");
		return value == nullptr || value[0] != '0';
	}();
	thread_local Scratch retained;
	Scratch local;
	auto& scratch = reuse ? retained : local;

	// Sources guarded by shader control flow (EvaluateRuntimeSourcesInterpreted has the
	// reference walk): a source of an unreached block is not evaluated and stays zero.
	auto& active = scratch.active;
	active.assign(program.descriptor_sources.size(), 1u);
	if (!program.control_flow.empty()) {
		if (compiled.block_condition_roots.size() != program.control_flow.size()) {
			return CompiledResult::HardFailure;
		}
		for (const auto& block: program.control_flow) {
			for (const auto source: block.sources) {
				if (source >= active.size()) {
					return CompiledResult::HardFailure;
				}
				active[source] = 0u;
			}
		}
		auto& visited = scratch.visited;
		auto& pending = scratch.pending;
		visited.assign(program.control_flow.size(), 0u);
		pending.assign(1, 0u);
		while (!pending.empty()) {
			const auto index = pending.back();
			pending.pop_back();
			if (index >= visited.size()) {
				return CompiledResult::HardFailure;
			}
			if (visited[index]) {
				continue;
			}
			visited[index]    = 1u;
			const auto& block = program.control_flow[index];
			for (const auto source: block.sources) {
				active[source] = 1u;
			}
			const auto root = compiled.block_condition_roots[index];
			if (root != CompiledSrt::None && runtime.read_specialization_memory != nullptr &&
			    status[root] == CompiledSrt::StOk && block.successors.size() >= 2u) {
				pending.push_back(block.successors[values[root] != 0u ? 0u : 1u]);
			} else {
				pending.insert(pending.end(), block.successors.begin(), block.successors.end());
			}
		}
	}

	auto& evaluated = scratch.evaluated;
	evaluated.clear();
	evaluated.reserve(sources.size());
	for (const auto source_index: sources) {
		const auto* source = Source(program, source_index);
		if (source == nullptr || source_index >= compiled.source_root_start.size()) {
			return CompiledResult::HardFailure;
		}
		DescriptorValue value;
		value.dword_count = source->dword_count;
		if (source_index < active.size() && !active[source_index]) {
			evaluated.push_back(value);
			continue;
		}
		const auto start  = compiled.source_root_start[source_index];
		for (uint32_t dword = 0; dword < source->dword_count && dword < value.dwords.size(); dword++) {
			const auto root = compiled.source_roots[start + dword];
			switch (status[root]) {
				case CompiledSrt::StOk: value.dwords[dword] = static_cast<uint32_t>(values[root]); break;
				case CompiledSrt::StMemFail: value.dwords[dword] = 0; break;
				default: return CompiledResult::HardFailure;
			}
		}
		evaluated.push_back(value);
	}
	auto& flattened = scratch.flattened;
	flattened.resize(program.srt_reads.size());
	for (uint32_t slot = 0; slot < program.srt_reads.size(); slot++) {
		const auto& read = program.srt_reads[slot];
		if (read.variant) {
			flattened[slot] = 0;
			continue;
		}
		const auto root = compiled.flat_roots[slot];
		if (root == CompiledSrt::None) {
			return CompiledResult::HardFailure;
		}
		const bool clean = slot < program.clean_flat_slots.size() && program.clean_flat_slots[slot] != 0u;
		switch (status[root]) {
			case CompiledSrt::StOk: flattened[slot] = static_cast<uint32_t>(values[root]); break;
			case CompiledSrt::StMemFail: flattened[slot] = 0; break;
			case CompiledSrt::StCleanMemFail:
				if (!clean) {
					return CompiledResult::HardFailure;
				}
				flattened[slot] = 0;
				break;
			default: return CompiledResult::HardFailure;
		}
	}
	results.swap(evaluated);
	flat.swap(flattened);
	active_sources.swap(active);
	return CompiledResult::Done;
}

bool EvaluateRuntimeSourcesInterpreted(const ResourcePlan& program, std::span<const uint32_t> sources,
                                       const SrtRuntime& runtime, std::vector<DescriptorValue>& results,
                                       std::vector<uint32_t>& flat, bool evaluate_flat,
                                       std::span<const uint8_t> clean_flat_slots,
                                       std::vector<uint8_t>&    active_sources);

bool EvaluateRuntimeSourcesImpl(const ResourcePlan& program, std::span<const uint32_t> sources,
                                const SrtRuntime& runtime, std::vector<DescriptorValue>& results,
                                std::vector<uint32_t>& flat, bool evaluate_flat,
                                std::span<const uint8_t> clean_flat_slots,
                                std::vector<uint8_t>& active_sources) {
	if (!program.srt_plan_complete) {
		return false;
	}
	if (std::ranges::any_of(clean_flat_slots, [](uint8_t clean) { return clean != 0u; }) &&
	    runtime.read_specialization_memory == nullptr) {
		return false;
	}
	static const bool compiled_enabled = [] {
		const char* value = std::getenv("KYTY_SRT_COMPILED");
		return value == nullptr || value[0] != '0';
	}();
	static const bool verify = std::getenv("KYTY_SRT_VERIFY") != nullptr;
	if (compiled_enabled && evaluate_flat && clean_flat_slots.data() == program.clean_flat_slots.data() &&
	    clean_flat_slots.size() == program.clean_flat_slots.size()) {
		thread_local std::vector<DescriptorValue> compiled_results;
		thread_local std::vector<uint32_t>        compiled_flat;
		thread_local std::vector<uint8_t>         compiled_active;
		const auto outcome = EvaluateCompiled(program, sources, runtime, compiled_results, compiled_flat,
		                                      compiled_active);
		if (outcome == CompiledResult::Done) {
			if (Common::FrameStats::Enabled()) {
				Common::FrameStats::Add(Common::FrameStats::Counter::MatMemoHits, 1);
			}
			if (verify) {
				std::vector<DescriptorValue> reference;
				std::vector<uint32_t>        reference_flat;
				std::vector<uint8_t>         reference_active;
				const bool ok = EvaluateRuntimeSourcesInterpreted(program, sources, runtime, reference,
				                                                  reference_flat, evaluate_flat, clean_flat_slots,
				                                                  reference_active);
				static std::atomic<uint32_t> logged {0};
				if ((!ok || reference != compiled_results || reference_flat != compiled_flat ||
				     reference_active != compiled_active) &&
				    logged.fetch_add(1) < 64) {
					std::string detail;
					for (size_t i = 0; i < std::min(reference.size(), compiled_results.size()); i++) {
						for (uint32_t d = 0; d < 8; d++) {
							if (reference[i].dwords[d] != compiled_results[i].dwords[d]) {
								detail += fmt::format(" src{}[{}]={:#x}/{:#x}", i, d, reference[i].dwords[d],
								                      compiled_results[i].dwords[d]);
							}
						}
					}
					for (size_t i = 0; i < std::min(reference_flat.size(), compiled_flat.size()); i++) {
						if (reference_flat[i] != compiled_flat[i]) {
							detail += fmt::format(" flat{}={:#x}/{:#x}", i, reference_flat[i], compiled_flat[i]);
						}
					}
					std::fprintf(stderr,
					             "SrtVerify: hash=0x%016llx interpreter_ok=%d sources=%zu/%zu flat=%zu/%zu%s\n",
					             static_cast<unsigned long long>(program.shader_hash), ok ? 1 : 0,
					             reference.size(), compiled_results.size(), reference_flat.size(),
					             compiled_flat.size(), detail.c_str());
				}
			}
			results.swap(compiled_results);
			flat.swap(compiled_flat);
			active_sources.swap(compiled_active);
			return true;
		}
		if (Common::FrameStats::Enabled()) {
			Common::FrameStats::Add(Common::FrameStats::Counter::MatMemoMisses, 1);
		}
	}
	return EvaluateRuntimeSourcesInterpreted(program, sources, runtime, results, flat, evaluate_flat,
	                                         clean_flat_slots, active_sources);
}

bool EvaluateRuntimeSourcesInterpreted(const ResourcePlan& program, std::span<const uint32_t> sources,
                                       const SrtRuntime& runtime, std::vector<DescriptorValue>& results,
                                       std::vector<uint32_t>& flat, bool evaluate_flat,
                                       std::span<const uint8_t> clean_flat_slots,
                                       std::vector<uint8_t>&    active_sources) {
	SrtRuntime clean_runtime  = runtime;
	clean_runtime.read_memory = runtime.read_specialization_memory;
	Evaluator            clean_evaluator(program, clean_runtime);
	Evaluator            evaluator(program, runtime, clean_flat_slots, &clean_evaluator);
	std::vector<uint8_t> active;
	if (evaluate_flat) {
		active.assign(program.descriptor_sources.size(), 1u);
	}
	if (evaluate_flat && !program.control_flow.empty()) {
		for (const auto& block: program.control_flow) {
			for (const auto source: block.sources) {
				active.at(source) = 0u;
			}
		}
		std::vector<uint8_t>  visited(program.control_flow.size());
		std::vector<uint32_t> pending {0};
		while (!pending.empty()) {
			const auto index = pending.back();
			pending.pop_back();
			if (visited.at(index)) {
				continue;
			}
			visited[index]    = 1u;
			const auto& block = program.control_flow[index];
			for (const auto source: block.sources) {
				active[source] = 1u;
			}
			uint32_t condition = 0;
			// A missing clean reader must never fall through to the evaluator's raw-memory path.
			if (!block.condition.IsEmpty() && runtime.read_specialization_memory != nullptr &&
			    clean_evaluator.Evaluate(block.condition, condition)) {
				pending.push_back(block.successors[condition != 0u ? 0u : 1u]);
			} else {
				pending.insert(pending.end(), block.successors.begin(), block.successors.end());
			}
		}
	}
	std::vector<DescriptorValue> evaluated;
	evaluated.reserve(sources.size());
	for (const auto source_index: sources) {
		const auto* source = Source(program, source_index);
		if (source == nullptr) {
			return false;
		}
		DescriptorValue value;
		value.dword_count = source->dword_count;
		if (!evaluate_flat || active[source_index]) {
			for (uint32_t index = 0; index < source->dword_count; index++) {
				evaluator.ClearMemoryReadFailure();
				if (!evaluator.Evaluate(source->dwords[index], value.dwords[index])) {
					if (evaluator.MemoryReadFailed()) {
						// The chain dereferences memory that is not mapped right now (typically a
						// pointer the game has not filled in yet, guarded by shader control flow).
						// Materialize a null descriptor instead of failing the whole shader.
						value.dwords[index] = 0;
						continue;
					}
					std::fprintf(stderr,
					             "shader resource evaluation failed: hash=0x%016llx source=%u (%s) "
					             "dword=%u: %s; value = %s\n",
					             static_cast<unsigned long long>(program.shader_hash), source_index,
					             DescribeSourceOwner(program, source_index).c_str(), index,
					             evaluator.Failure().c_str(),
					             DescribeValue(program, source->dwords[index]).c_str());
					return false;
				}
			}
		}
		evaluated.push_back(value);
	}
	std::vector<uint32_t> flattened;
	if (evaluate_flat) {
		flattened.resize(program.srt_reads.size());
		for (const auto& read: program.srt_reads) {
			if (read.variant) {
				if (read.flat_offset < flattened.size()) {
					flattened[read.flat_offset] = 0;
				}
				continue;
			}
			const bool clean    = read.flat_offset < clean_flat_slots.size() &&
			                      clean_flat_slots[read.flat_offset] != 0u;
			auto&      selected = clean ? clean_evaluator : evaluator;
			selected.ClearMemoryReadFailure();
			if (read.flat_offset < flattened.size() &&
			    !selected.Evaluate(read.value, flattened[read.flat_offset]) &&
			    selected.MemoryReadFailed()) {
				flattened[read.flat_offset] = 0;
				continue;
			}
			if (read.flat_offset >= flattened.size() ||
			    !selected.Evaluate(read.value, flattened[read.flat_offset])) {
				std::fprintf(stderr,
				             "shader resource evaluation failed: hash=0x%016llx flat slot %u: %s\n",
				             static_cast<unsigned long long>(program.shader_hash), read.flat_offset,
				             (selected.Failure() + "; value = " + DescribeValue(program, read.value)).c_str());
				return false;
			}
		}
	}
	results = std::move(evaluated);
	active_sources = std::move(active);
	if (evaluate_flat) {
		flat = std::move(flattened);
	}
	return true;
}

} // namespace

bool ValidateRuntimeValue(const ResourcePlan& program, Value value, RuntimeValueType type) {
	return RuntimeValidator(program, type).Run(value);
}

void SetSrtSlotReference(std::vector<std::pair<uint64_t, uint32_t>> reference) {
	SrtSlotReferenceStorage() = std::move(reference);
}

void BuildSrtPlan(Program& program) {
	if (program.resource_tracking_complete) {
		EXIT("shader SRT planning failed: cannot rebuild SRT after resource tracking");
	}
	program.srt_plan_complete = false;
	PlanBuilder(program).Run();
	program.srt_plan_complete = true;
}

bool EvaluateUniformValues(const ResourcePlan& program, std::span<const Value> values,
                            const SrtRuntime& runtime, std::span<uint32_t> results) {
	if (values.size() != results.size()) {
		return false;
	}
	auto clean = runtime;
	clean.read_memory = runtime.read_specialization_memory != nullptr
	                        ? runtime.read_specialization_memory
	                        : +[](void*, uint64_t, uint32_t*) { return false; };
	Evaluator evaluator(program, clean);
	for (size_t i = 0; i < values.size(); ++i) {
		if (!evaluator.Evaluate(values[i], results[i])) {
			return false;
		}
	}
	return true;
}

bool EvaluateDescriptorSource(const ResourcePlan& program, uint32_t source,
                              const SrtRuntime& runtime, DescriptorValue& result) {
	std::vector<DescriptorValue> results;
	if (!EvaluateDescriptorSources(program, std::span {&source, 1}, runtime, results)) {
		return false;
	}
	result = results.front();
	return true;
}

bool EvaluateDescriptorSources(const ResourcePlan& program, std::span<const uint32_t> sources,
                               const SrtRuntime& runtime, std::vector<DescriptorValue>& results) {
	std::vector<uint32_t> ignored;
	std::vector<uint8_t>  active;
	return EvaluateRuntimeSourcesImpl(program, sources, runtime, results, ignored, false, {},
	                                  active);
}

bool EvaluateRuntimeSources(const ResourcePlan& program, std::span<const uint32_t> sources,
                            const SrtRuntime& runtime, std::vector<DescriptorValue>& results,
                            std::vector<uint32_t>& flat, std::span<const uint8_t> clean_flat_slots,
                            std::vector<uint8_t>& active_sources) {
	return EvaluateRuntimeSourcesImpl(program, sources, runtime, results, flat, true,
	                                  clean_flat_slots, active_sources);
}

bool WalkSrt(const ResourcePlan& program, const SrtRuntime& runtime, std::vector<uint32_t>& flat) {
	std::vector<DescriptorValue> ignored;
	std::vector<uint8_t>         active;
	return EvaluateRuntimeSources(program, {}, runtime, ignored, flat, {}, active);
}

} // namespace Libs::Graphics::ShaderRecompiler::IR
