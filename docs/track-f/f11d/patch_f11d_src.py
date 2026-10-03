# F11d (HPP-466, ROADMAP s122 item 376(v)): KYTY_DIAG_BVHNODES - the code of the F11a project (variant E)
# with RC1-RC8 of F11b. Applies the src/ part to a tree: python patch_f11d_src.py <root>.
# Anchors are whole lines (exactly one match, checked); files keep their line endings (LF in git, CRLF
# restored if the file had it); output is written with write_bytes. Default of the knob: 0.
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
CHANGED = []


def load(rel):
    raw = (ROOT / rel).read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n").split("\n"), crlf


def save(rel, lines, crlf):
    text = "\n".join(lines)
    if crlf:
        text = text.replace("\n", "\r\n")
    (ROOT / rel).write_bytes(text.encode("utf-8"))
    CHANGED.append(rel)


def find_seq(lines, seq, rel):
    hits = [i for i in range(len(lines) - len(seq) + 1) if lines[i:i + len(seq)] == seq]
    if len(hits) != 1:
        raise SystemExit("ANCHOR %s matches %d times in %s" % (seq[0][:80], len(hits), rel))
    return hits[0]


def block(text):
    # A block of C++ lines; a leading newline of the literal is dropped.
    if text.startswith("\n"):
        text = text[1:]
    return text.split("\n")


class File:
    def __init__(self, rel):
        self.rel = rel
        self.lines, self.crlf = load(rel)

    def insert_after(self, anchor, text):
        anchor = anchor if isinstance(anchor, list) else [anchor]
        at = find_seq(self.lines, anchor, self.rel) + len(anchor)
        self.lines[at:at] = block(text)

    def insert_before(self, anchor, text):
        anchor = anchor if isinstance(anchor, list) else [anchor]
        at = find_seq(self.lines, anchor, self.rel)
        self.lines[at:at] = block(text)

    def replace(self, old, text):
        old = old if isinstance(old, list) else [old]
        at = find_seq(self.lines, old, self.rel)
        self.lines[at:at + len(old)] = block(text)

    def save(self):
        save(self.rel, self.lines, self.crlf)


# --- knob -------------------------------------------------------------------------------------------
f = File("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.h")
f.insert_after("bool   FixB1BEnabled();", r"""
// Track F, F11d (HPP-466, ROADMAP p.376(v)): KYTY_DIAG_BVHNODES, default OFF (Common::EnvFlagOn: unset,
// "", 0, false, off, no = off). On: IMAGE_BVH_INTERSECT_RAY and S_TRAP also emit the diagnostic opcodes
// BvhNodeDiag / DiagTrap (node pointer counts by type and size field, traps; fault-buffer tail words,
// SpirvEmitter.h DiagWordBase). Off: no new IR instruction, the SPIR-V is the same as without the code.
// Read once per process; the translation cache keys the value (":diagbvh") in its signature and directory.
bool   DiagBvhNodesEnabled();""")
f.save()

f = File("src/graphics/shader/recompiler/frontend/decode/ShaderDecoder.cpp")
f.insert_after(["bool FixB1BEnabled() {",
                "	static const bool enabled = [] {",
                "		const char* value = std::getenv(\"KYTY_FIX_B1B\");",
                "		return value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
                "	}();",
                "	return enabled;",
                "}"], r"""

bool DiagBvhNodesEnabled() {
	static const bool enabled = Common::EnvFlagOn("KYTY_DIAG_BVHNODES");
	return enabled;
}""")
f.save()

# --- IR ---------------------------------------------------------------------------------------------
f = File("src/graphics/shader/recompiler/ir/opcodes/ValueOpcodes.inc")
f.insert_after("VALUE_OPCODE(SharedAtomicDec32, U32, U32, U32, U1)", r"""// Track F, F11d (KYTY_DIAG_BVHNODES=1 only), appended for cache compatibility: the node pointer of an
// IMAGE_BVH_INTERSECT_RAY - node_lo, node_hi, descriptor dwords 2-3 (size field), exec - and an S_TRAP
// reached - exec. Both write the fault-buffer tail (uses_dma).
VALUE_OPCODE(BvhNodeDiag, Void, U32, U32, U32, U32, U1)
VALUE_OPCODE(DiagTrap, Void, U1)""")
f.save()

f = File("src/graphics/shader/recompiler/ir/opcodes/ValueOpcodes.cpp")
f.insert_before("		case ValueOpcode::Barrier: return true;", r"""		case ValueOpcode::BvhNodeDiag:
		case ValueOpcode::DiagTrap:""")
f.save()

f = File("src/graphics/shader/recompiler/ir/passes/ResourceTracking.cpp")
f.replace("		if (op == ValueOpcode::BvhIntersectRay) {", r"""		// Track F, F11d: the KYTY_DIAG_BVHNODES opcodes write the fault-buffer tail as well.
		if (op == ValueOpcode::BvhIntersectRay || op == ValueOpcode::BvhNodeDiag ||
		    op == ValueOpcode::DiagTrap) {""")
f.save()

# --- frontend ---------------------------------------------------------------------------------------
f = File("src/graphics/shader/recompiler/frontend/translate/Memory.cpp")
f.insert_after(["	const IR::U1 sort_enabled =",
                "	    ir.LogicalAnd(ir.INotEqual(ir.BitwiseAnd(desc1, U32C(0x80000000u)), U32C(0u)),",
                "	                  ir.INotEqual(sort_mode, U32C(3u)));"], r"""
	// Track F, F11d (ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1 counts the node pointer that reaches the
	// instruction - type, size field (descriptor dwords 2-3), lanes - ahead of the native / IR fork, so
	// both paths count the same. =0 emits nothing.
	if (Decoder::DiagBvhNodesEnabled()) {
		ir.Emit(IR::ValueOpcode::BvhNodeDiag,
		        {node_lo, node_hi, GetResourceDword(memory.resource, 2),
		         GetResourceDword(memory.resource, 3), ir.GetExec()});
	}""")
f.save()

f = File("src/graphics/shader/recompiler/frontend/translate/Scalar.cpp")
f.replace(["		case O::S_SETPRIO:",
           "		case O::S_TRAP: EmitControlNop(); return true;"], r"""		case O::S_SETPRIO: EmitControlNop(); return true;
		case O::S_TRAP:
			// Track F, F11d (ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1 counts the subgroups and lanes that
			// reach the trap, which stays a no-op; =0 emits only the no-op, as before.
			if (Decoder::DiagBvhNodesEnabled()) {
				ir.Emit(IR::ValueOpcode::DiagTrap, {ir.GetExec()});
			}
			EmitControlNop();
			return true;""")
f.save()

# --- emitter ----------------------------------------------------------------------------------------
f = File("src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.h")
f.insert_after("inline constexpr uint32_t LoopTripSlots    = 8;", r"""// Track F, F11d (HPP-466, ROADMAP p.376(v)), KYTY_DIAG_BVHNODES=1 (Decoder::DiagBvhNodesEnabled): the
// diagnostic words follow the loop-cap words; the fault-buffer tail grows by DiagWords u32 only at =1.
// Every IMAGE_BVH_INTERSECT_RAY execution adds, per host subgroup (ballot bit counts, one elected
// invocation), the active lanes by node type ([DiagT0 + type]); for 32-bit pointers the lanes past the
// descriptor size field ([DiagSizeViol]: idx = ptr >> 3 > size64 = dword2 | (dword3 & 0x3ff) << 32), their
// largest excess over = idx - size64 ([DiagOverMax]) and a histogram of it ([DiagBuckets + 4 * class +
// bucket], classes 0 triangle (types 0-3), 1 box (4-6), 2 type 7; bucket 3 = idx > 2 * size64 + 1, else
// 0 = over 1, 1 = over 2..16, 2 = over 17 or more; the buckets of all classes sum to [DiagSizeViol]); the
// lanes with size64 = 2^42 - 1 ([DiagSizeOff]); the 64-bit pointers ([DiagNode64], never in DiagSizeViol);
// the active lanes of the program ([DiagLanes + DiagBvhSlot(hash)]) and the subgroups ([DiagGroups]).
// Every S_TRAP adds the subgroups that reach it, whatever exec holds ([DiagTraps]), and its active lanes
// ([DiagTrapLanes]). The u32 counters wrap; the host diffs them modulo 2^32 (faultManager.cpp).
inline constexpr uint32_t DiagWordBase  = LoopTripWordBase + LoopTripWords;
inline constexpr uint32_t DiagWords     = 64;
inline constexpr uint32_t DiagSlotCount = 20; // the BVH programs of eboot.bin; slot DiagSlotCount = other
enum DiagWord : uint32_t {
	DiagT0        = 0, // .. 7: lanes by node type
	DiagSizeViol  = 8,
	DiagSizeOff   = 9,
	DiagNode64    = 10,
	DiagOverMax   = 11,
	DiagTraps     = 12,
	DiagTrapLanes = 13,
	DiagGroups    = 14,
	DiagBuckets   = 16, // .. 27: 3 classes x 4 buckets
	DiagLanes     = 28, // .. 48: DiagSlotCount program slots, then other
};
static_assert(DiagLanes + DiagSlotCount < DiagWords, "the diagnostic words fit the tail");
// Slot of a program in the DiagLanes words: its index in the BVH program table, DiagSlotCount = other.
uint32_t DiagBvhSlot(uint64_t shader_hash);
uint64_t DiagBvhSlotHash(uint32_t slot); // 0 for slot >= DiagSlotCount""")
f.save()

f = File("src/graphics/shader/recompiler/backend/spirv/spirvEmitterInstructions.h")
f.insert_after("uint32_t              EmitBvhIntersectRay(ValueEmitContext& ctx, const IR::Inst& inst);", r"""void                  EmitBvhNodeDiag(ValueEmitContext& ctx, const IR::Inst& inst);
void                  EmitDiagTrap(ValueEmitContext& ctx, const IR::Inst& inst);""")
f.save()

f = File("src/graphics/shader/recompiler/backend/spirv/SpirvEmitter.cpp")
f.insert_after("				case IR::ValueOpcode::Ballot: requirements.subgroup_ballot = true; break;", r"""				// Track F, F11d: KYTY_DIAG_BVHNODES counters (ballot bit counts, elect).
				case IR::ValueOpcode::BvhNodeDiag:
				case IR::ValueOpcode::DiagTrap: requirements.subgroup_ballot = true; break;""")
f.save()

f = File("src/graphics/shader/recompiler/backend/spirv/spirvEmitterMemory.cpp")
f.insert_before("// KYTY_BVH_LOOP_CAP: this invocation spent its whole step budget and returns now.", r"""// Track F, F11d (HPP-466, ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1 counters in the fault-buffer tail
// (SpirvEmitter.h, DiagWordBase). Per host subgroup a ballot bit count gives the lanes of a class and one
// elected invocation adds the non-zero counts. With lane_count 2 (wave64 on a 32-wide subgroup) each half
// is emitted on its own: each half counts its lanes, only half 0 counts the subgroup.
namespace {

// The 20 programs of eboot.bin with IMAGE_BVH_INTERSECT_RAY (track F, F3b bvhmap_f3b; F11a t1scan_f11a.py
// --all), ascending: the slots of the DiagLanes words.
constexpr std::array<uint64_t, DiagSlotCount> DiagBvhPrograms {
    0x092754e7ae8bac9aull, 0x0af122d5ac62c4c5ull, 0x1f16e50eea0c89e3ull, 0x1f3219e5899a66f2ull,
    0x380bb9d636390baeull, 0x3d27502d0a809c72ull, 0x503d7f066a496c3cull, 0x5323c4ef4f785055ull,
    0x559a0fa9def7a691ull, 0x56a15431999c5a2dull, 0x7ede18ae55120a48ull, 0x8175abf0855222dbull,
    0x99012529f9a27ba3ull, 0xa763fb769f3167ecull, 0xb76e569142635733ull, 0xcd94166bf3f2bb81ull,
    0xd234cf2781dabb34ull, 0xea8e2d64dfe34ed9ull, 0xf88d0f630ac5b35dull, 0xff8ee744ffa4dcdcull,
};

// Lanes of the subgroup with the predicate set.
uint32_t DiagLaneCount(EmitterState& state, uint32_t predicate) {
	const auto ballot = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpGroupNonUniformBallot, TypeU32Vector(state, 4), ballot,
	                          ConstantU32(state, spv::ScopeSubgroup), predicate);
	const auto count = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpGroupNonUniformBallotBitCount, TypeU32(state), count,
	                          ConstantU32(state, spv::ScopeSubgroup), spv::GroupOperationReduce,
	                          ballot);
	return count;
}

// One invocation of the subgroup (the lowest running one), whatever the guest exec holds.
uint32_t DiagElect(EmitterState& state) {
	const auto elected = state.builder.AllocateId();
	state.builder.AddFunction(spv::OpGroupNonUniformElect, TypeBool(state), elected,
	                          ConstantU32(state, spv::ScopeSubgroup));
	return elected;
}

// The elected invocation adds a non-zero count to the diagnostic word.
void DiagAdd(EmitterState& state, uint32_t elected, uint32_t word, uint32_t count) {
	const auto nonzero =
	    Binary(state, spv::OpINotEqual, TypeBool(state), count, ConstantU32(state, 0));
	EmitIfCondition(state, AndCondition(state, elected, nonzero),
	                [&]() { AtomicTailU32(state, spv::OpAtomicIAdd, DiagWordBase + word, count); });
}

} // namespace

uint32_t DiagBvhSlot(uint64_t shader_hash) {
	for (uint32_t slot = 0; slot < DiagSlotCount; slot++) {
		if (DiagBvhPrograms[slot] == shader_hash) {
			return slot;
		}
	}
	return DiagSlotCount;
}

uint64_t DiagBvhSlotHash(uint32_t slot) {
	return slot < DiagSlotCount ? DiagBvhPrograms[slot] : 0;
}

// BvhNodeDiag: node_lo, node_hi, descriptor dwords 2-3, exec (frontend Memory.cpp, ahead of the fork).
void EmitBvhNodeDiag(ValueEmitContext& ctx, const IR::Inst& inst) {
	auto& state = ctx.state;
	if (state.fault_buffer_variable == 0) {
		return;
	}
	const auto u32t  = TypeU32(state);
	const auto boolt = TypeBool(state);
	const auto U     = [&](uint32_t value) { return ConstantU32(state, value); };
	const auto land  = [&](uint32_t a, uint32_t b) { return AndCondition(state, a, b); };
	const auto lnot  = [&](uint32_t a) { return Unary(state, spv::OpLogicalNot, boolt, a); };
	const auto ieq   = [&](uint32_t a, uint32_t b) { return Binary(state, spv::OpIEqual, boolt, a, b); };
	const auto ugt   = [&](uint32_t a, uint32_t b) {
		return Binary(state, spv::OpUGreaterThan, boolt, a, b);
	};
	const auto node_lo = ctx.Arg(inst, 0);
	const auto desc2   = ctx.Arg(inst, 2);
	const auto desc3   = ctx.Arg(inst, 3);
	const auto active  = ctx.Arg(inst, 4);
	// Same rule as EmitBvhIntersectRay: the 64-bit form has a high word that is not the constant 0.
	const bool node64  = !inst.Arg(1).IsImmediate() || inst.Arg(1).U32() != 0u;
	const auto elected = DiagElect(state);
	const auto add     = [&](uint32_t word, uint32_t predicate) {
		DiagAdd(state, elected, word, DiagLaneCount(state, predicate));
	};
	const auto type = Binary(state, spv::OpBitwiseAnd, u32t, node_lo, U(7u));
	for (uint32_t index = 0; index < 8u; index++) {
		add(DiagT0 + index, land(active, ieq(type, U(index))));
	}
	const auto size_hi = Binary(state, spv::OpBitwiseAnd, u32t, desc3, U(0x3ffu));
	add(DiagSizeOff, land(active, land(ieq(desc2, U(0xffffffffu)), ieq(size_hi, U(0x3ffu)))));
	if (node64) {
		add(DiagNode64, active);
	} else {
		// idx (64-byte units from the base, 29 bits) violates when idx > size64; a size64 of 2^32 or more
		// never is exceeded. There over = idx - size64 >= 1, and idx > 2 * size64 + 1 <=> over - 1 > size64.
		const auto idx    = Binary(state, spv::OpShiftRightLogical, u32t, node_lo, U(3u));
		const auto viol   = land(active, land(ieq(size_hi, U(0u)), ugt(idx, desc2)));
		const auto over   = Binary(state, spv::OpISub, u32t, idx, desc2);
		const auto beyond = land(viol, ugt(Binary(state, spv::OpISub, u32t, over, U(1u)), desc2));
		const auto within = land(viol, lnot(beyond));
		const std::array<uint32_t, 4> buckets {
		    land(within, ieq(over, U(1u))),
		    land(within, land(ugt(over, U(1u)), lnot(ugt(over, U(16u))))),
		    land(within, ugt(over, U(16u))),
		    beyond,
		};
		const auto is_t7 = ieq(type, U(7u));
		const std::array<uint32_t, 3> classes {
		    Binary(state, spv::OpULessThan, boolt, type, U(4u)),
		    land(ugt(type, U(3u)), lnot(is_t7)),
		    is_t7,
		};
		add(DiagSizeViol, viol);
		for (uint32_t cls = 0; cls < 3u; cls++) {
			for (uint32_t bucket = 0; bucket < 4u; bucket++) {
				add(DiagBuckets + 4u * cls + bucket, land(buckets[bucket], classes[cls]));
			}
		}
		// The largest excess: violations are rare, the violating lanes take the maximum one by one.
		EmitIfCondition(state, viol, [&]() {
			AtomicTailU32(state, spv::OpAtomicUMax, DiagWordBase + DiagOverMax, over);
		});
	}
	add(DiagLanes + DiagBvhSlot(state.program.shader_hash), active);
	if (state.lane_half == 0) {
		EmitIfCondition(state, elected, [&]() {
			AtomicTailU32(state, spv::OpAtomicIAdd, DiagWordBase + DiagGroups, U(1u));
		});
	}
}

// DiagTrap: exec (frontend Scalar.cpp). S_TRAP is a scalar instruction: every subgroup that reaches it
// counts, also with exec = 0; the active lanes are counted apart.
void EmitDiagTrap(ValueEmitContext& ctx, const IR::Inst& inst) {
	auto& state = ctx.state;
	if (state.fault_buffer_variable == 0) {
		return;
	}
	const auto active  = ctx.Arg(inst, 0);
	const auto elected = DiagElect(state);
	if (state.lane_half == 0) {
		EmitIfCondition(state, elected, [&]() {
			AtomicTailU32(state, spv::OpAtomicIAdd, DiagWordBase + DiagTraps, ConstantU32(state, 1u));
		});
	}
	DiagAdd(state, elected, DiagTrapLanes, DiagLaneCount(state, active));
}
""")
f.save()

f = File("src/graphics/shader/recompiler/backend/spirv/spirvEmitterProgram.cpp")
f.insert_before("void EmitProgram(EmitterState& state) {", r"""namespace {

// Track F, F11d (ROADMAP p.376(v), RC4 of F11b): at KYTY_DIAG_BVHNODES=1 a translation of a program with
// diagnostic sites names them - the BVH and trap sites left in the program, and whether the dispatcher
// fallback emits it (its blocks run the same diagnostic opcodes).
void LogDiagBvhNodes(const IR::Program& program) {
	if (!Decoder::DiagBvhNodesEnabled()) {
		return;
	}
	size_t bvh_sites  = 0;
	size_t trap_sites = 0;
	for (const auto* block: program.blocks) {
		for (const auto& inst: *block) {
			bvh_sites += inst.GetOpcode() == IR::ValueOpcode::BvhNodeDiag ? 1 : 0;
			trap_sites += inst.GetOpcode() == IR::ValueOpcode::DiagTrap ? 1 : 0;
		}
	}
	if (bvh_sites + trap_sites == 0) {
		return;
	}
	LOGF("DiagBvhNodes: shader=%016" PRIx64 " bvh_sites=%zu trap_sites=%zu fallback=%d\n",
	     program.shader_hash, bvh_sites, trap_sites, program.dispatcher_fallback ? 1 : 0);
}

} // namespace
""")
f.insert_before("	LoopGuards loop_guards;", "	LogDiagBvhNodes(program);")
f.save()

# --- host -------------------------------------------------------------------------------------------
f = File("src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp")
f.insert_after("	// with KYTY_FIX_B26 the four combinations get four distinct signatures and directories.",
               "	// Track F, F11d (ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1 adds \":diagbvh\" the same way (default 0: none).")
f.replace("	                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? \":fixb1b\" : \"\");", r"""	                            (ShaderRecompiler::Decoder::FixB1BEnabled() ? ":fixb1b" : "") +
	                            (ShaderRecompiler::Decoder::DiagBvhNodesEnabled() ? ":diagbvh" : "");""")
f.save()

f = File("src/graphics/host_gpu/renderer/cache/faultManager.h")
f.insert_after("#include <array>", "#include <atomic>")
f.insert_after("	void ClearLoopTripTail();", r"""	// Track F, F11d (ROADMAP p.376(v)): the counter tail after the fault bitmap - the loop-cap words and,
	// at KYTY_DIAG_BVHNODES=1, the diagnostic words; ClearLoopTripTail zeroes all of it.
	[[nodiscard]] static uint64_t TailOffset();
	[[nodiscard]] static uint64_t TailBytes();""")
f.insert_after("private:", "	void ProcessDiagWords(uint64_t download_offset);\n")
f.insert_after("	uint32_t                                   m_trip_lines = 0;", r"""	// Track F, F11d: KYTY_DIAG_BVHNODES host state - read and written by the readbacks (deferred operations
	// of ProcessFaultBuffer), except m_tail_cleared: set by ClearLoopTripTail (buffer cache, first
	// registration), read when a readback is recorded; the diagnostic words are diffed only after it.
	std::array<uint32_t, 64>                   m_diag_last {};
	std::array<uint64_t, 64>                   m_diag_total {};
	uint64_t                                   m_diag_max_step    = 0;
	uint64_t                                   m_diag_last_log_ms = 0;
	uint32_t                                   m_diag_lines       = 0;
	bool                                       m_diag_pending     = false;
	std::atomic<bool>                          m_tail_cleared {false};""")
f.save()

f = File("src/graphics/host_gpu/renderer/cache/faultManager.cpp")
f.insert_after("#include \"graphics/shader/recompiler/backend/spirv/SpirvEmitter.h\"",
               "#include \"graphics/shader/recompiler/frontend/decode/ShaderDecoder.h\"")
f.insert_after("#include <bit>", "#include <chrono>")
f.insert_after("#include <cinttypes>", "#include <cstdio>")
f.insert_after("#include <limits>", "#include <string>")
f.insert_after("static_assert(LoopTripOffset == uint64_t {LoopCap::LoopTripWordBase} * sizeof(uint32_t));", r"""
// Track F, F11d (ROADMAP p.376(v)): the KYTY_DIAG_BVHNODES words follow the loop-cap words; the tail, the
// fault buffer and each readback area grow by DiagBytes only at =1.
constexpr uint64_t DiagOffset = LoopTripOffset + LoopTripBytes;
constexpr uint64_t DiagBytes  = LoopCap::DiagWords * sizeof(uint32_t);
static_assert(DiagOffset == uint64_t {LoopCap::DiagWordBase} * sizeof(uint32_t));
static_assert(LoopCap::DiagWords == 64, "faultManager.h keeps 64 diagnostic words");""")
f.insert_before(["FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,"], r"""uint64_t FaultManager::TailOffset() {
	return LoopTripOffset;
}

uint64_t FaultManager::TailBytes() {
	return LoopTripBytes + (ShaderRecompiler::Decoder::DiagBvhNodesEnabled() ? DiagBytes : 0);
}
""")
f.replace("                     LoopTripOffset + LoopTripBytes),", "                     LoopTripOffset + TailBytes()),")
f.replace("                      MaxPendingFaults * LoopTripBytes) {", "                      MaxPendingFaults * TailBytes()) {")
f.insert_after("	     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));", r"""	if (ShaderRecompiler::Decoder::DiagBvhNodesEnabled()) {
		LOGF("DiagBvhNodes: mode=1 words=%u tail_bytes=%" PRIu64 "\n", LoopCap::DiagWords, TailBytes());
	}""")
f.replace("	m_fault_buffer.Fill(LoopTripOffset, LoopTripBytes, 0);", r"""	// Track F, F11d (RC1 of F11b): the same command zeroes the diagnostic words at =1 (DeviceLocal memory
	// starts undefined); the host takes them only from readbacks recorded after this (m_tail_cleared).
	m_fault_buffer.Fill(TailOffset(), TailBytes(), 0);
	m_tail_cleared.store(true, std::memory_order_release);""")
f.replace(["	const bool trips       = LoopCap::BvhLoopCap() != 0;",
           "	const auto trip_offset = m_current_area * LoopTripBytes;",
           "	if (trips) {"], r"""	const bool trips       = LoopCap::BvhLoopCap() != 0;
	// Track F, F11d: at KYTY_DIAG_BVHNODES=1 the copy takes the whole tail (one region: loop-cap and
	// diagnostic words) once ClearLoopTripTail has zeroed it; at =0 the tail is LoopTripBytes, as before.
	const bool diag        = ShaderRecompiler::Decoder::DiagBvhNodesEnabled() &&
	                  m_tail_cleared.load(std::memory_order_acquire);
	const auto tail_bytes  = TailBytes();
	const auto trip_offset = m_current_area * tail_bytes;
	if (trips || diag) {""")
f.replace("		tail_barrier.size          = LoopTripBytes;", "		tail_barrier.size          = tail_bytes;")
f.replace("		host_barrier.size          = LoopTripBytes;", "		host_barrier.size          = tail_bytes;")
f.replace("		const vk::BufferCopy region {LoopTripOffset, trip_offset, LoopTripBytes};",
          "		const vk::BufferCopy region {LoopTripOffset, trip_offset, tail_bytes};")
f.replace("	m_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {",
          "	m_scheduler.DeferOperation([this, mapped, offset, area, trips, diag, trip_offset] {")
f.insert_before("		m_download_buffer.Invalidate(offset, PageFaultAreaSize);", r"""		if (diag) {
			ProcessDiagWords(trip_offset + LoopTripBytes);
		}""")
f.insert_before("} // namespace Libs::Graphics", r"""// Track F, F11d (ROADMAP p.376(v)): KYTY_DIAG_BVHNODES=1, the diagnostic words of one readback. The GPU
// counters are u32 and wrap: each is diffed against its last value modulo 2^32, exact while one interval
// (one readback, a frame with BDA work) adds less than 2^32 - max_step is the largest step seen. The last
// values start at 0, the value the tail holds after ClearLoopTripTail. [DiagOverMax] is a maximum and is
// taken as read. A line - cumulative totals - is printed when something grew, at most every 2 s and 1024
// times per process; a growth within the 2 s is printed by a later readback (m_diag_pending), so only the
// last 2 s before the process ends can go unprinted.
void FaultManager::ProcessDiagWords(uint64_t download_offset) {
	m_trip_download.Invalidate(download_offset, DiagBytes);
	std::array<uint32_t, LoopCap::DiagWords> words {};
	std::memcpy(words.data(), m_trip_download.Mapped().data() + download_offset, DiagBytes);
	for (uint32_t index = 0; index < LoopCap::DiagWords; index++) {
		if (index == LoopCap::DiagOverMax) {
			m_diag_pending |= words[index] != m_diag_last[index];
			m_diag_last[index]  = words[index];
			m_diag_total[index] = words[index];
			continue;
		}
		const uint32_t step = words[index] - m_diag_last[index];
		m_diag_last[index]  = words[index];
		m_diag_total[index] += step;
		m_diag_max_step = std::max<uint64_t>(m_diag_max_step, step);
		m_diag_pending |= step != 0;
	}
	const auto now_ms = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(
	                                              std::chrono::steady_clock::now().time_since_epoch())
	                                              .count());
	if (!m_diag_pending || m_diag_lines >= 1024 ||
	    (m_diag_lines != 0 && now_ms - m_diag_last_log_ms < 2000)) {
		return;
	}
	m_diag_pending     = false;
	m_diag_last_log_ms = now_ms;
	m_diag_lines++;
	const auto& total = m_diag_total;
	uint64_t    lanes = 0;
	for (uint32_t type = 0; type < 8; type++) {
		lanes += total[LoopCap::DiagT0 + type];
	}
	const auto bucket = [&](uint32_t cls, uint32_t index) {
		return total[LoopCap::DiagBuckets + 4 * cls + index];
	};
	LOGF("DiagBvhNodes: lanes=%" PRIu64 " t0=%" PRIu64 " t1=%" PRIu64 " t2=%" PRIu64 " t3=%" PRIu64
	     " t4=%" PRIu64 " t5=%" PRIu64 " t6=%" PRIu64 " t7=%" PRIu64 " size_viol=%" PRIu64
	     " size_off=%" PRIu64 " node64=%" PRIu64 " over_max=%" PRIu64 " b_tri=%" PRIu64 "/%" PRIu64
	     "/%" PRIu64 "/%" PRIu64 " b_box=%" PRIu64 "/%" PRIu64 "/%" PRIu64 "/%" PRIu64 " b_t7=%" PRIu64
	     "/%" PRIu64 "/%" PRIu64 "/%" PRIu64 " traps=%" PRIu64 " trap_lanes=%" PRIu64 " groups=%" PRIu64
	     " max_step=%" PRIu64 "\n",
	     lanes, total[LoopCap::DiagT0 + 0], total[LoopCap::DiagT0 + 1], total[LoopCap::DiagT0 + 2],
	     total[LoopCap::DiagT0 + 3], total[LoopCap::DiagT0 + 4], total[LoopCap::DiagT0 + 5],
	     total[LoopCap::DiagT0 + 6], total[LoopCap::DiagT0 + 7], total[LoopCap::DiagSizeViol],
	     total[LoopCap::DiagSizeOff], total[LoopCap::DiagNode64], total[LoopCap::DiagOverMax],
	     bucket(0, 0), bucket(0, 1), bucket(0, 2), bucket(0, 3), bucket(1, 0), bucket(1, 1), bucket(1, 2),
	     bucket(1, 3), bucket(2, 0), bucket(2, 1), bucket(2, 2), bucket(2, 3), total[LoopCap::DiagTraps],
	     total[LoopCap::DiagTrapLanes], total[LoopCap::DiagGroups], m_diag_max_step);
	std::string slots;
	for (uint32_t slot = 0; slot < LoopCap::DiagSlotCount; slot++) {
		if (total[LoopCap::DiagLanes + slot] != 0) {
			char text[64];
			std::snprintf(text, sizeof(text), " %016" PRIx64 "=%" PRIu64, LoopCap::DiagBvhSlotHash(slot),
			              total[LoopCap::DiagLanes + slot]);
			slots += text;
		}
	}
	LOGF("DiagBvhNodes: slots%s other=%" PRIu64 "\n", slots.c_str(),
	     total[LoopCap::DiagLanes + LoopCap::DiagSlotCount]);
}
""")
f.save()

print("changed", len(CHANGED))
for rel in CHANGED:
    print(" ", rel)
print("ALL OK")
