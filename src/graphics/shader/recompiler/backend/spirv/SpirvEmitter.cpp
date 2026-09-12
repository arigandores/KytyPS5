#include "graphics/shader/recompiler/backend/spirv/SpirvEmitter.h"

#include "common/assert.h"
#include "graphics/shader/recompiler/backend/spirv/spirvEmitterInternal.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"

#include <algorithm>
#include <array>
#include <optional>

namespace Libs::Graphics::ShaderRecompiler::Spirv {

namespace {

// Upper bound of a U32 address expression (immediates, lane id, add/shift/and/mul/select/phi
// of bounded values); nullopt when it depends on something unbounded.
std::optional<uint64_t> StaticAddressBound(const IR::Value& value_in, int depth) {
	const auto value = value_in.Resolve();
	if (value.IsImmediate()) {
		return value.GetType() == IR::Type::U32 ? std::optional<uint64_t> {value.U32()}
		                                        : std::nullopt;
	}
	const auto* inst = value.TryInstruction();
	if (inst == nullptr || depth > 12) {
		return std::nullopt;
	}
	const auto arg = [&](size_t i) { return StaticAddressBound(inst->Arg(i), depth + 1); };
	const auto imm = [&](size_t i) -> std::optional<uint32_t> {
		const auto v = inst->Arg(i).Resolve();
		return v.IsImmediate() && v.GetType() == IR::Type::U32 ? std::optional<uint32_t> {v.U32()}
		                                                       : std::nullopt;
	};
	switch (inst->GetOpcode()) {
		case IR::ValueOpcode::LaneId: return 63u;
		case IR::ValueOpcode::IAdd32: {
			const auto a = arg(0);
			const auto b = arg(1);
			return a && b ? std::optional<uint64_t> {std::min<uint64_t>(*a + *b, UINT32_MAX)}
			              : std::nullopt;
		}
		case IR::ValueOpcode::ShiftLeftLogical32: {
			const auto a = arg(0);
			const auto s = imm(1);
			return a && s && *s < 32u
			           ? std::optional<uint64_t> {std::min<uint64_t>(*a << *s, UINT32_MAX)}
			           : std::nullopt;
		}
		case IR::ValueOpcode::BitwiseAnd32: {
			const auto m0 = imm(0);
			const auto m1 = imm(1);
			const auto a  = arg(0);
			const auto b  = arg(1);
			uint64_t   bound = UINT32_MAX;
			bool       known = false;
			for (const auto& m: {m0, m1}) {
				if (m) {
					bound = std::min<uint64_t>(bound, *m);
					known = true;
				}
			}
			for (const auto& x: {a, b}) {
				if (x) {
					bound = std::min<uint64_t>(bound, *x);
					known = true;
				}
			}
			return known ? std::optional<uint64_t> {bound} : std::nullopt;
		}
		case IR::ValueOpcode::IMul32: {
			const auto a = arg(0);
			const auto b = arg(1);
			return a && b ? std::optional<uint64_t> {std::min<uint64_t>(*a * *b, UINT32_MAX)}
			              : std::nullopt;
		}
		case IR::ValueOpcode::SelectU32: {
			const auto a = arg(1);
			const auto b = arg(2);
			return a && b ? std::optional<uint64_t> {std::max(*a, *b)} : std::nullopt;
		}
		case IR::ValueOpcode::Phi: {
			uint64_t bound = 0;
			for (size_t i = 0; i < inst->NumArgs(); i++) {
				const auto a = arg(i);
				if (!a) {
					return std::nullopt;
				}
				bound = std::max(bound, *a);
			}
			return bound;
		}
		case IR::ValueOpcode::BitFieldUExtract: {
			const auto count = imm(2);
			if (!count || *count == 0u || *count > 32u) {
				return std::nullopt;
			}
			const uint64_t mask = *count == 32u ? UINT32_MAX : (uint64_t {1} << *count) - 1u;
			const auto     a    = arg(0);
			return a ? std::optional<uint64_t> {std::min(*a, mask)} : std::optional<uint64_t> {mask};
		}
		default: return std::nullopt;
	}
}

[[noreturn]] void Fail(const IR::Program& program, const char* reason) {
	EXIT("SPIR-V validation failed: hash=0x%016" PRIx64 " stage=%u reason=%s\n",
	     program.shader_hash, static_cast<unsigned>(program.stage), reason);
	std::abort();
}

void ValidateNativeProgram(const IR::Program& program) {
	using Kind                                             = IR::DescriptorBindingKind;
	constexpr auto                               KindCount = static_cast<size_t>(Kind::Count);
	std::array<std::vector<uint32_t>, KindCount> expected;
	std::array<bool, KindCount>                  present {};
	const auto                                   Dense = [](size_t size) {
		std::vector<uint32_t> values(size);
		for (uint32_t i = 0; i < values.size(); i++) {
			values[i] = i;
		}
		return values;
	};
	auto Expect = [&](Kind kind, std::vector<uint32_t> resources = {}) {
		const auto index = static_cast<size_t>(kind);
		present[index]   = true;
		expected[index]  = std::move(resources);
	};
	if (!program.info.buffers.empty()) {
		Expect(Kind::Buffers, Dense(program.info.buffers.size()));
	}
	if (auto const_bank = IR::ConstBankResources(program.info); !const_bank.empty()) {
		Expect(Kind::ConstBuffers, std::move(const_bank));
	}
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		const auto kind = IR::DescriptorBindingForImage(program.info.images[i]);
		if (!kind.has_value()) {
			Fail(program, "native shader plan has an invalid image class");
		}
		present[static_cast<size_t>(*kind)] = true;
		const auto dynamic = program.info.images[i].mip_mode == IR::ImageMipMode::DynamicStorage;
		const auto count   = dynamic ? program.info.images[i].mip_count : 1u;
		if (count == 0u || (!dynamic && program.info.images[i].mip_count != 1u)) {
			Fail(program, "native shader plan has an invalid image mip descriptor count");
		}
		expected[static_cast<size_t>(*kind)].insert(expected[static_cast<size_t>(*kind)].end(),
		                                            count, i);
	}
	if (!program.info.samplers.empty()) {
		Expect(Kind::Samplers, Dense(program.info.samplers.size()));
	}
	bool uses_gds = false;
	for (const auto* block: program.blocks) {
		for (const auto& inst: *block) {
			if (IR::SharedAccessOf(inst.GetOpcode()) == IR::SharedAccess::None) {
				continue;
			}
			const auto index = inst.Flags<IR::MemoryFlags>().index;
			if (index >= program.memory_info.size()) {
				Fail(program, "shared operation has invalid memory metadata");
			}
			const auto kind = program.memory_info[index].kind;
			if (kind != IR::ResourceKind::Lds && kind != IR::ResourceKind::Gds) {
				Fail(program, "shared operation has invalid resource kind");
			}
			uses_gds |= kind == IR::ResourceKind::Gds;
		}
	}
	if (uses_gds) {
		Expect(Kind::Gds);
	}
	if (program.info.uses_dma) {
		Expect(Kind::BdaPagetable);
		Expect(Kind::FaultBuffer);
	}
	const bool uses_flattened_runtime =
	    !program.srt_reads.empty() ||
	     std::ranges::any_of(program.info.images, [](const IR::ImageResource& image) {
		     return image.indirect_search_iterations != 0u;
	     });
	if (uses_flattened_runtime) {
		Expect(Kind::FlattenedSrt);
	}
	if (program.bindings.ShaderDataDwords() != 0 && !program.bindings.UsesPushData()) {
		Expect(Kind::ShaderData);
	}

	std::array<bool, KindCount> seen {};
	for (const auto& binding: program.bindings.descriptors) {
		const auto kind = static_cast<size_t>(binding.kind);
		if (kind >= KindCount || seen[kind] || !present[kind] ||
		    binding.resources != expected[kind]) {
			Fail(program, "native descriptor groups do not match shader topology");
		}
		seen[kind] = true;
	}
	for (size_t i = 0; i < KindCount; i++) {
		if (present[i] != seen[i]) {
			Fail(program, "native shader plan is missing a required descriptor group");
		}
	}
	const auto has_shader_data_storage = present[static_cast<size_t>(Kind::ShaderData)];
	const auto shader_data_dwords = program.bindings.ShaderDataDwords();
	if ((program.bindings.UsesPushData() &&
	     !IR::PushData::CanFit(program.bindings.push_data_start_dword, shader_data_dwords)) ||
	    program.bindings.memory_offset_dword != program.bindings.user_data_registers.size() ||
	    program.bindings.memory_offset_count != program.info.buffers.size() ||
	    has_shader_data_storage != (shader_data_dwords != 0 && !program.bindings.UsesPushData()) ||
	    !std::is_sorted(program.bindings.user_data_registers.begin(),
	                    program.bindings.user_data_registers.end()) ||
	    std::adjacent_find(program.bindings.user_data_registers.begin(),
	                       program.bindings.user_data_registers.end()) !=
	        program.bindings.user_data_registers.end()) {
		Fail(program, "native shader-data layout is inconsistent");
	}

	const auto planning_only_handle = [&](const IR::Inst& handle) {
		return !handle.Uses().empty() &&
		       std::ranges::all_of(handle.Uses(), [&](const IR::Use& use) {
			       const auto op = use.user->GetOpcode();
			       if (op != IR::ValueOpcode::LoadAddressU32 &&
			           op != IR::ValueOpcode::ReadConstBuffer) {
				       return false;
			       }
			       const auto index = use.user->Flags<IR::MemoryFlags>().index;
			       return index < program.memory_info.size() &&
			              program.memory_info[index].planning_only;
		       });
	};
	for (const auto* block: program.blocks) {
		for (const auto& inst: *block) {
			const auto dense = inst.Flags<uint32_t>();
			switch (inst.GetOpcode()) {
				case IR::ValueOpcode::GetBufferResource:
					if (planning_only_handle(inst)) {
						break;
					}
					if (dense >= program.info.buffers.size()) {
						Fail(program, "typed buffer handle has an invalid dense resource");
					}
					break;
				case IR::ValueOpcode::GetAddressResource:
					if (planning_only_handle(inst)) {
						break;
					}
					if (inst.NumArgs() != 2 || !program.info.uses_dma) {
						Fail(program, "typed address handle has invalid DMA metadata");
					}
					break;
				case IR::ValueOpcode::GetScratchResource:
					if (inst.NumArgs() != 0 || program.scratch_dwords == 0) {
						Fail(program, "typed scratch handle has invalid shader metadata");
					}
					break;
				case IR::ValueOpcode::GetImageResource:
					if (dense >= program.info.images.size()) {
						Fail(program, "typed image handle has an invalid dense resource");
					}
					break;
				case IR::ValueOpcode::GetSamplerResource:
					if (dense >= program.info.samplers.size()) {
						Fail(program, "typed sampler handle has an invalid dense resource");
					}
					break;
				case IR::ValueOpcode::ReadConst: {
					const auto slot = inst.Arg(1).Resolve();
					if (!slot.IsImmediate() || slot.GetType() != IR::Type::U32 ||
					    slot.U32() >= program.srt_reads.size()) {
						Fail(program, "flattened SRT read has an invalid dense slot");
					}
					break;
				}
				default: break;
			}
		}
	}
}

} // namespace

Emitter::SpirvRequirements Emitter::AnalyzeProgramRequirements(const IR::Program& program) {
	SpirvRequirements requirements {};
	for (const auto* block: program.blocks) {
		for (const auto& inst: *block) {
			if (IR::BufferAccessOf(inst.GetOpcode()) == IR::BufferAccess::Atomic &&
			    inst.GetType() == IR::Type::U64) {
				requirements.buffer_int64_atomics = true;
			}
			if (inst.GetOpcode() == IR::ValueOpcode::ReadConstBuffer) {
				if (Emitter::VectorConstLoadsEnabled() && Emitter::RobustLoadsEnabled()) {
					requirements.scalar_vector_loads = true;
				}
				const auto memory_index = inst.Flags<IR::MemoryFlags>().index;
				if (memory_index < program.memory_info.size()) {
					const auto& memory = program.memory_info[memory_index];
					if (memory.resource < program.info.buffers.size() &&
					    IR::PackedStrideConstBank(
					        program.info.buffers[memory.resource].packed_stride)) {
						requirements.const_bank_loads = true;
					}
				}
			}
			const auto address_access = IR::AddressOpcodeInfoOf(inst.GetOpcode()).access;
			if (address_access != IR::AddressAccess::None) {
				const auto memory_index = inst.Flags<IR::MemoryFlags>().index;
				if (memory_index >= program.memory_info.size()) {
					Fail(program, "address operation has invalid memory metadata");
				}
				if (program.memory_info[memory_index].kind == IR::ResourceKind::Scratch) {
					if (program.scratch_dwords == 0) {
						Fail(program, "scratch operation has no per-thread storage");
					}
					requirements.function_scratch = true;
				} else if (address_access == IR::AddressAccess::Write) {
					Fail(program, "writable FLAT/GLOBAL addresses require GPU ownership tracking");
				}
			}
			if (IR::BufferAccessOf(inst.GetOpcode()) != IR::BufferAccess::None) {
				const auto memory_index = inst.Flags<IR::MemoryFlags>().index;
				if (memory_index >= program.memory_info.size()) {
					Fail(program, "buffer operation has invalid memory metadata");
				}
				const auto& memory = program.memory_info[memory_index];
				if (memory.kind == IR::ResourceKind::Buffer) {
					if (memory.resource >= program.info.buffers.size()) {
						Fail(program, "buffer operation has invalid resource metadata");
					}
					if ((program.info.buffers[memory.resource].packed_stride & (1u << 20u)) != 0u) {
						if (program.stage != ShaderType::Compute) {
							Fail(program, "buffer ADD_TID is only valid for compute shaders");
						}
						requirements.subgroup_local_invocation_id = true;
					}
				}
			}
			const auto shared_access = IR::SharedAccessOf(inst.GetOpcode());
			if (shared_access != IR::SharedAccess::None) {
				const auto index = inst.Flags<IR::MemoryFlags>().index;
				if (index >= program.memory_info.size()) {
					Fail(program, "shared operation has invalid memory metadata");
				}
				const auto kind = program.memory_info[index].kind;
				if (kind != IR::ResourceKind::Lds && kind != IR::ResourceKind::Gds) {
					Fail(program, "shared operation has invalid resource kind");
				}
				if (program.stage != ShaderType::Compute && program.stage != ShaderType::Mesh &&
				    kind == IR::ResourceKind::Lds) {
					requirements.function_lds = true;
					// The array is private to the invocation: size it by the address bound.
					const auto& memory = program.memory_info[index];
					const auto  bound  = shared_access == IR::SharedAccess::Append ||
					                            shared_access == IR::SharedAccess::Consume
					                         ? std::nullopt
					                         : StaticAddressBound(inst.Arg(0), 0);
					if (!bound) {
						requirements.function_lds_unbounded = true;
					} else {
						const uint64_t end = *bound + memory.offset + memory.data_dwords * 4ull + 4ull;
						requirements.function_lds_dwords = static_cast<uint32_t>(std::max<uint64_t>(
						    requirements.function_lds_dwords, std::min<uint64_t>(end / 4u, 8192u)));
					}
				}
				if (shared_access == IR::SharedAccess::Append ||
				    shared_access == IR::SharedAccess::Consume) {
					requirements.subgroup_ballot              = true;
					requirements.subgroup_shuffle             = true;
					requirements.subgroup_local_invocation_id = true;
				}
			}
			switch (inst.GetOpcode()) {
				case IR::ValueOpcode::Ballot: requirements.subgroup_ballot = true; break;
				case IR::ValueOpcode::DppMoveU32:
				case IR::ValueOpcode::ReadFirstLane:
				case IR::ValueOpcode::ReadLane: {
					requirements.subgroup_ballot  = true;
					requirements.subgroup_shuffle = true;
					if (inst.GetOpcode() == IR::ValueOpcode::DppMoveU32) {
						requirements.subgroup_local_invocation_id = true;
					}
					break;
				}
				case IR::ValueOpcode::DppUpdateU32:
				case IR::ValueOpcode::WriteLane: {
					requirements.subgroup_ballot              = true;
					requirements.subgroup_local_invocation_id = true;
					break;
				}
				case IR::ValueOpcode::Permlane16U32: {
					requirements.subgroup_ballot              = true;
					requirements.subgroup_shuffle             = true;
					requirements.subgroup_local_invocation_id = true;
					break;
				}
				case IR::ValueOpcode::SwizzleU32:
				case IR::ValueOpcode::BpermuteU32: {
					requirements.subgroup_ballot              = true;
					requirements.subgroup_shuffle             = true;
					requirements.subgroup_local_invocation_id = true;
					break;
				}
				case IR::ValueOpcode::LaneId:
					requirements.subgroup_local_invocation_id = true;
					break;
				case IR::ValueOpcode::ImageQueryLod: requirements.compute_derivatives = true; break;
				case IR::ValueOpcode::ImageGatherRaw:
					requirements.image_gather_extended = true;
					break;
				case IR::ValueOpcode::SetAttribute: {
					const auto index = inst.Flags<IR::ExportFlags>().index;
					if (index >= program.export_info.size()) {
						Fail(program, "attribute export has invalid metadata");
					}
					if (program.stage == ShaderType::Pixel &&
					    program.export_info[index].vm) {
						requirements.pixel_valid_mask = true;
					}
					break;
				}
				default: break;
			}
		}
	}
	return requirements;
}

std::vector<uint32_t> EmitProgram(const IR::Program& program,
                                  ShaderStageInputInfo input_info) {
	using namespace Emitter;

	if (program.stage != ShaderType::Compute && program.stage != ShaderType::Vertex &&
	    program.stage != ShaderType::Pixel && program.stage != ShaderType::Mesh) {
		Fail(program, "binary SPIR-V emitter supports compute, vertex, and pixel shaders");
	}
	if (!program.srt_plan_complete || !program.resource_tracking_complete ||
	    !program.shader_info_complete || !program.binding_layout_complete) {
		Fail(program, "SPIR-V emitter requires a fully planned native shader program");
	}
	ValidateNativeProgram(program);
	IR::ValidateProgram(program, true);
	EmitterState state(program, input_info);
	const auto* workgroup = ShaderWorkgroupInput(program.stage, input_info);
	state.lane_count =
	    workgroup != nullptr && program.wave_size == 64u && workgroup->host_subgroup_size == 32u
	        ? 2u
	        : 1u;
	DefineModule(state);
	EmitProgram(state);
	state.builder.AddEntryPoint(ExecutionModelForStage(state.program.stage), state.main_func,
	                            "main", state.interface_variables);

	return state.builder.Build();
}

} // namespace Libs::Graphics::ShaderRecompiler::Spirv
