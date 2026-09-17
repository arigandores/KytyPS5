#include "common/gates.h"

#include "common/logging/log.h"

#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace Common::Gates {

namespace {

struct Definition {
	const char* environment;
	const char* name;
	bool        fallback;
};

constexpr std::array<Definition, static_cast<size_t>(Gate::Count)> DEFINITIONS {{
    {"KYTY_CBUFFER_DIRECT_COPY", "copy", true},
    {"KYTY_SRT_PAGE_PERSIST", "srtpages", true},
    {"KYTY_CLAMP_MEMO", "clamp", true},
    {"KYTY_REGION_EPOCH", "regionepoch", false},
    {"KYTY_SRT_MEMO", "srtmemo", false},
    {"KYTY_SRT_MEMO_VERIFY", "smemocheck", false},
    {"KYTY_BDA_REGION_STAMPS", "bdastamp", true},
    {"KYTY_BACKING_PAGES", "backpages", true},
    {"KYTY_SRT_STAT", "srtstat", false},
    {"KYTY_META_LOCK", "metalock", true},
    {"KYTY_DRAW_AHEAD", "drawahead", true},
    {"KYTY_DRAW_AHEAD_USE", "dause", true},
    {"KYTY_ASYNC_SUBMIT", "asyncsubmit", true},
    {"KYTY_IMAGE_RECYCLE", "imgrecycle", true},
    {"KYTY_RECORD_THREAD", "recordthread", true},
    {"KYTY_TRACK_LOCKFREE", "trackfree", true},
    {"KYTY_TRACK_LOCKFREE_VERIFY", "tfcheck", false},
    {"KYTY_PROTECT_FAST", "protfast", false},
    {"KYTY_SHADER_WRITE_LOCAL", "swlocal", false},
    {"KYTY_SHADER_WRITE_DEFER", "swdefer", true},
    {"KYTY_GDS_EPOCH", "gdsepoch", false},
    {"KYTY_ATOMIC_IMAGE_NO_BARRIER", "atomimg", false},
    {"KYTY_DESCRIPTOR_RING", "dsring", true},
    {"KYTY_RECORD_PACKETS", "recpack", true},
    {"KYTY_SYNC_FREE", "syncfree", true},
    {"KYTY_SYNC_FREE_VERIFY", "sfcheck", false},
    {"KYTY_PROTECT_BATCH", "protbatch", true},
    {"KYTY_PROTECT_BATCH_VERIFY", "pbcheck", false},
    {"KYTY_TEX_FAULT_HINT", "texfaulthint", true},
    {"KYTY_DRAW_AHEAD_CLASS", "daclass", true},
    {"KYTY_DRAW_AHEAD_PREFETCH", "daprefetch", true},
    {"KYTY_DRAW_AHEAD_CLONE", "daclone", false},
    {"KYTY_TEX_LRU", "texlru", true},
    {"KYTY_TEX_FAST", "texfast", true},
    {"KYTY_TEX_FAST_VERIFY", "texfastcheck", false},
    {"KYTY_TEX_MEMO2", "texmemo2", false},
    {"KYTY_CLAMP_VMA", "clampvma", true},
    {"KYTY_SAMPLER_MEMO", "smpmemo", true},
    {"KYTY_BIND_SPARE", "bindspare", false},
    {"KYTY_FRAME_STATS_LEAN", "fslean", false},
    // Session 57, A2/A3 (page protection).
    {"KYTY_APPLY_SKIP", "applyskip", false},
    // Session 57, A4 (record publish).
    {"KYTY_RECORD_BATCH", "recbatch", false},
    {"KYTY_RECORD_RELAXED", "recrelax", false},
    // Session 63: on by default (Sky Garden -2.3...-3.6 % CPU per draw, three repeats).
    {"KYTY_RECORD_PIN", "recpin", true},
    // Session 57, A1 (sticky pages).
    {"KYTY_STICKY_STAT", "stkstat", false},
    // Session 57, E1/E2/E9 (draw statistics).
    {"KYTY_DRAW_STAT", "drawstat", false},
    {"KYTY_DRAW_STAT_SLOW", "dpslow", false},
    // Session 57, A6/A7 and track B.
    {"KYTY_DRAW_STATE_REUSE", "drawstate", true},
    {"KYTY_SNAPSHOT_KEEP", "snapkeep", true},
    {"KYTY_BUF_LRU", "buflru", true},
    // Session 58, B4 follow-up (snapshot copies).
    {"KYTY_SNAPSHOT_DIFF", "snapdiff", true},
    {"KYTY_SNAPSHOT_SWAP", "snapswap", true},
    // Session 58, M2 step 1 (buffer request memo).
    {"KYTY_BUF_FAST", "buffast", false},
    {"KYTY_BUF_FAST_VERIFY", "buffastcheck", false},
    // Session 58, A3 phase 2 (one host protection flush per BDA dirty-range pass).
    {"KYTY_PROTECT_BATCH2", "protbatch2", false},
    // Session 58, Sky Garden hang: liveness of the async-copy timeline semaphore.
    {"KYTY_ASYNC_COPY_IDLE_SIGNAL", "acopyidle", true},
    // Session 59, M1 producer off the critical thread.
    {"KYTY_DRAW_AHEAD_WALK", "dawalk", false},
    {"KYTY_RT_FAST", "rtfast", true},
    // Session 60, B3.
    {"KYTY_PROG_MEMO", "progmemo", true},
    {"KYTY_PROG_MEMO_VERIFY", "progmemocheck", false},
    // Session 60, item 4.
    {"KYTY_ARM_DEFER", "armdefer", false},
    {"KYTY_ARM_DEFER_VERIFY", "armcheck", false},
    {"KYTY_DRAW_AHEAD_WITNESS", "dawitness", true},
    // Session 72 ships this: measured with ABBA on bac1155d (wpt71a, 121 pairs) at
    // cpu/draw -0.467 % +/- 0.207 %, t = -4.50, which is 1.23x the stand threshold of 0.380 %,
    // for -0.152 ms of wall per frame. Behaviour is bit-identical: da_direct matched da_hit to
    // 0.0025 %, da_direct_no was 0, every da_stale* counter was 0 by sum AND by maximum in both
    // arms, and da_hit/da_miss/pmemo_* moved only with the draw count. Every recorded word is
    // still compared - the gate only changes the pointer the live runs are read through, while
    // AddressSpace::MapEpoch() (memoryAddressSpace.inc:164) witnesses that translation.
    {"KYTY_DRAW_AHEAD_WITNESS_PTR", "dawitptr", true},
    {"KYTY_DRAW_AHEAD_QUEUE_PREFETCH", "daqpre", false},
    {"KYTY_CB_STAT", "cbstat", false},
    {"KYTY_RECORD_IMAGE_BARRIERS", "recimg", false},
    {"KYTY_RECORD_UPLOADS", "recup", false},
    // Session 64, E6 (measurement only).
    {"KYTY_SHADOW_INLINE", "shadowinline", false},
    // Session 67, infrastructure.
    {"KYTY_SAVE_PERSIST", "savepersist", false},
    // Session 68, measurement only.
    {"KYTY_OCCLUSION_ZERO", "occzero", false},
    {"KYTY_A_MUTATE", "amut", false},
    {"KYTY_PX_STAT", "pxstat", false},
    // Session 69, measurement only.
    {"KYTY_MUT_SITE", "mutsite", false},
    {"KYTY_IMG_SKIP_GPU_STALE", "imgskip", false},
    // Session 70, a behaviour change: two missing cases in the packed-clear decoder.
    {"KYTY_CLEAR_DECODE_WIDE", "cleardec", false},
    // Session 71, measurement only: default 1 keeps the session-61 epoch ceiling exactly as it
    // was, 0 removes it from inside da_take_us.
    // Session 72 ships 0: the regions vector exists ONLY to answer "would an epoch witness
    // have held?", and session 70 closed that question - regionManager.h:202-210 bumps the
    // region epoch only on the protected->writable transition and :128-131 starts every region
    // all-dirty, so an epoch witness is unsound whatever the counters say. Building it costs
    // 11 005 RegionWriteStamp reads and 6110 WitnessEpochsHold calls per frame INSIDE the
    // timed region of AheadTake. Measured with ABBA on 136ebeb6 (dep72a, 108 pairs):
    // cpu/draw -0.522 % +/- 0.284 %, t = -3.68, = -0.190 ms of wall per frame, with da_hit
    // 8633.658 -> 8633.016 (0.007 %) and every da_stale* zero in both arms - the decision path
    // never reads the vector (pipelineCache.cpp:697, :2499, :2509 are its only readers, all
    // ceiling diagnostics). Setting it back to 1 restores the diagnostic da_ep_* counters.
    {"KYTY_DA_EPOCH_CEILING", "daepceil", false},
    // Session 73, W6: one range predicate per clean run instead of one per word in the fallback.
    // Removes work only - if the run is partly GPU-dirty the lookup fails and the untouched
    // per-word loop runs exactly as before.
    {"KYTY_DA_CLEAN_RANGE", "dawitfb", false},
    // Session 73, C1: fuse the detile into a storage-image write. SHIPPED at 1 after fus73a,
    // 114 ABBA pairs: gpu_busy_us -8.599 % +/- 0.469 %, t = -36.69, i.e. 14 665 -> 13 397 us =
    // -1.268 ms of GPU per frame, and cpu/draw -0.554 % +/- 0.178 %, t = -6.22 = -0.182 ms of
    // wall, with draws 0.014 % apart. That is 102 % of the 1241.7 us session 72 measured as the
    // ceiling by time; the excess is the four barrier commands, the scratch allocation and the
    // sub-dword atomics the fused path also removes. Arming proved by c1_fuse == c1_fz_ok in the
    // armed arm and 0.000 in the other. Set it to 0 to get the scratch path back.
    {"KYTY_IMAGE_DETILE_FUSE", "imgfuse", true},
    // Session 73, W7: cheapen the GPU-clean page predicate of the witness's clean loop.
    // SHIPPED at 1 after wcp73a, 124 ABBA pairs on 0af8fed6: cpu/draw -0.588 % +/- 0.177 %,
    // t = -6.66, whole-arm cpu/fr 32 678 -> 32 447 us = -0.231 ms of wall per frame (paired
    // -0.591 % of 32.56 ms = -0.191 ms; quote the interval 0.19-0.23 ms), gpu_busy_us +0.066 %
    // = noise, FPS 30.26 -> 30.48, draws 0.118 % apart. da_take_us 3298.5 -> 3018.9 us.
    // Both halves armed on 99.995 % of the misses they aim at: da_cl_live 15 071.6 of da_cl_miss
    // 15 072.4, tgm_hint 15 071.6 of tgm_call 15 072.4. Behaviour identical - da_hit = da_direct
    // in both arms, da_miss 74.06 / 73.90, every da_stale* and pmemo_bad zero (guards check 2,
    // 10/10). Expected and declared side effect: srt_miss 901.9 -> 1508.2, because half (b)
    // routes the clean misses through LiveBackingPage's own table. Set it to 0 to get the two
    // extra locks back.
    {"KYTY_DA_CLEAN_PAGE", "dawitcp", true},
    // Session 74, W8: the M1 witness's clean-page table survives the AheadTake call, keyed on
    // (BackingMapEpoch, GpuDirtyGen) and tag-invalidated. SHIPPED: -0.31...-0.32 ms of CPU wall
    // per frame (cg74b, 116 ABBA pairs, cpu/draw -0.956 % +- 0.162 %, t = -11.84, guards 10 PASS,
    // 0 FAIL); da_cl_miss 15 140.6 -> 1 406.3 per frame. The self-check below stays off by default
    // and read da_cl_bad = 0 over ~98 million checks on cgv74a.
    {"KYTY_DA_CLEAN_GEN", "dawitcg", true},
    {"KYTY_DA_CLEAN_GEN_VERIFY", "dawitcgcheck", false},
    // Session 75: the M1 prefetch asks for L2 where the source says L1, because winnt.h:3649
    // defines _MM_HINT_T0 as 1 (MSVC numbering) UNGUARDED and wins over clang's 3 in
    // pipelineCache.cpp, whose <xmmintrin.h> sits below fifty-six project headers. Measured before
    // the gate was written: the prefetch itself is worth 0.98 ms of CPU per frame (dpf75a, 125 ABBA
    // pairs, daprefetch=1|0, cpu/draw +3.064 % +/- 0.244 %, t = +25.14, whole-arm cpu/fr
    // 31 950 -> 32 926 us, draws 0.001 % apart).
    //
    // SHIPPED ON 1 IN SESSION 76, on ONE area-clean ABBA. pfh76a and pfh76b, which this comment
    // used to quote at -413 us and -482 us, are VOID: their whole-arm rt_kpx/rt_att split reads
    // +2.191 % and +3.621 %, further from arm equality than the run session 75 voided at +1.74 %,
    // and they matched only 62/112 and 188/333 pairs against the >= 90 % pre-registered. Session
    // 76 substituted that criterion after it failed and an adversary falsified the substitute;
    // the original rule is reinstated and NOTHING is quoted from those two runs.
    //   pfh76c  period 30, 121 pairs, on the installed binary with pfcap=1024 in BOTH arms - the
    //           first pfhint ABBA in the programme to pass every criterion stated in advance:
    //           area split +0.446 %, match 109/121 = 90.1 %, work +0.044 %, gap 0.026 pp;
    //           cpu/draw -0.777 % +/- 0.482 %, t = -3.23; matched -0.882 % +/- 0.360 %, t = -4.91;
    //           whole-arm cpu/fr 32 208 -> 31 963 us = -245 us; da_take_us -133 us = 54 % of it.
    // THE SHIPPED FIGURE IS 0.25 ms of CPU wall per frame, ON A SINGLE CLEAN RUN, and it is an
    // INCREMENT measured at pfcap=1024: do NOT add it to the pfcap figure, the two overlap.
    // Arming is proved by a counter in the run, never by the launcher: arm1 pf_l1 8629.075
    // against da_hit 8629.471 = 99.995 %, arm0 2.838; guards check 2 read 11/11.
    // A prefetch changes no value and no decision: the arms are identical by construction.
    // The bracketing timer da_take_us moves with this gate: -130.7 us +/- 21.2, t = -12.35 over
    // the 109 area-matched pairs, because the guest lines it touches are consumed by
    // SameRecordedWords inside VerifyWitness, inside that timer. For pfcap it nets to zero.
    // Set the gate to 0 to get the old PREFETCHT2 form back, bit for bit.
    {"KYTY_PREFETCH_HINT_L1", "pfhint", true},
    // Session 82, measurement only: the repeat rate of a draw's binding inputs.
    {"KYTY_BIND_KEY", "bindkey", false},
    // Session 82, W1: the write map of the BDA region walk, and its self-check.
    {"KYTY_BDA_WRITE_BITS", "bdabits", false},
    {"KYTY_BDA_WRITE_BITS_VERIFY", "bdabitscheck", false},
    // Session 83, route B: the binding-path package (PLAN_82_bind.md items 1, 4, 9), plus
    // session 84's item 11.  SHIPPED in session 84 at -251.7 +- 82.8 us of cpu_net_us on
    // bpk84a, against the -150 us threshold pred/01_bindpack4.md fixed before the run.
    {"KYTY_BIND_PACK", "bindpack", true},
    {"KYTY_BIND_PACK_VERIFY", "bindpackcheck", false},
    // Session 83, measurement only: the hold of PipelineCache::m_mutex, site by site.
    {"KYTY_PIPE_LOCK_STAT", "plkstat", false},
    // Session 84, measurement only: the per-slot repeat census of route C.
    {"KYTY_SLOT_STAT", "slotstat", false},
    // Session 84, measurement only: the probe/scan split of PrepareBda.
    {"KYTY_BDA_LAP", "bdalap", false},
    // Session 85, measurement only: the per-slot price of the binding phase.
    {"KYTY_BIND_LAP", "bindlap", false},
    // Session 85, measurement only: where the fixed part of bda_scan_us goes.
    {"KYTY_BDA_SPLIT", "bdasplit", false},
    // Session 85: the element-count self-check of the route-C census.
    {"KYTY_SLOT_STAT_VERIFY", "slotstatcheck", false},
    // Session 85, route B: the duplicated upload-epoch evaluation of ObtainBuffer, and its
    // self-check.  PLAN_82_bind.md item 6a.
    {"KYTY_BUF_EPOCH_FAST", "bindpack2", false},
    {"KYTY_BUF_EPOCH_VERIFY", "bindpack2check", false},
    // Session 86, measurement only: what mh_prog_us actually is, under lite.
    {"KYTY_PROG_LAP", "proglap", false},
    // Session 86, measurement only: route D4, the consecutive-draw mergeability census.
    {"KYTY_DRAW_MERGE", "drawmerge", false},
    {"KYTY_DRAW_MERGE_VERIFY", "drawmergecheck", false},
    // Session 87, measurement only: which half of an image slot in PrepareBindings is the
    // resolve and which is BindImage.  One timestamp a slot, alternating phase a stage.
    {"KYTY_BIND_ALT", "bindalt", false},
    // Session 89, measurement only: the six-phase division of AheadTake (ROADMAP.md route D2),
    // seeded free from the timestamp da_take_us already takes.  Needs FrameStats enabled, which
    // every run of this programme has.  Its own price is measured by its own ABBA and declared:
    // six marks a call against ~8 690 calls a frame, and session 87 measured a mark of this
    // shape at 7.5 ns (pgl87a, +448.5 us for the six of "proglap").
    {"KYTY_TAKE_LAP", "takelap", false},
    // Session 90: the cross-implementation self-check of knob "bufimp" -
    // TryGetBackingPieces recomputed beside every TryGetBackingPointer the import used.
    // bi_bad must read 0, and it is parsed only because guards.py SELF_CHECKS has a row.
    {"KYTY_BUF_IMPORT_VERIFY", "bufimpcheck", false},
}};

struct KnobDefinition {
	const char* environment;
	const char* name;
	uint32_t    fallback;
	uint32_t    limit;
};

constexpr std::array<KnobDefinition, static_cast<size_t>(Knob::Count)> KNOB_DEFINITIONS {{
    {"KYTY_DRAW_AHEAD_THREADS", "dathreads", 4, 64},
    {"KYTY_RECORD_ARENA_MB", "recarena", 64, 256},
    {"KYTY_DESCRIPTOR_BATCH", "dsbatch", 32, 256},
    {"KYTY_DESCRIPTOR_POOL", "dspool", 1024, 16384},
    {"KYTY_RECORD_SPIN_US", "recspin", 300, 100000},
    // Session 82: SHIPPED ON 3. One logical processor per physical core of the largest L3
    // group. dap82b, a valid ABBA on this binary, reads dt_us -820.7 us (30.791 -> 31.590 FPS,
    // cpu/draw -2.175 % +- 0.153 %, t = -28.46 over 123 matched pairs, area split +0.003 %,
    // work +0.088 %), replicating the -732.5 us [-798.5, -666.4] of sessions 79 and 81 whose
    // arm was the raw mask 21845 that mode 3 derives. OPEN: the GPU side costs +1.238 %
    // (+147.1 us), replicated a fourth time and STILL UNEXPLAINED; it does not bind here
    // (gpu_busy 12.56 ms of a 32.5 ms frame). dapin=1 restores the previous default.
    {"KYTY_DRAW_AHEAD_PIN", "dapin", 3, 0xffffffffu},
    {"KYTY_PROCESS_PIN", "procpin", 0, 0xffffffffu},
    {"KYTY_FAULT_WINDOW_KB", "faultkb", 64, 4096},
    {"KYTY_DRAW_AHEAD_WALK_LEAD", "dawalklead", 1, 64},
    {"KYTY_RECORD_PUBLISH_N", "recpubn", 0, 4096},
    {"KYTY_SHADOW_RESOLVE", "shadowresolve", 0, 16},
    {"KYTY_SHADOW_MASK", "shadowmask", 3, 3},
    {"KYTY_M4_BATON", "m4baton", 0, 4096},
    {"KYTY_IMG_SKIP_KB", "imgskipkb", 4096, 1048576},
    // Session 72, measurement ceiling (default 0 = today's behaviour; 1 and 2 are UNSOUND).
    {"KYTY_DA_WITNESS_LOOP", "dawitloop", 0, 2},
    // Session 76, W3. Measured population, base75a, 6467 frames: da_pf_b 12 535 382 B/frame
    // offered against da_pf_cap_b 7 382 040 B let through, so the old 192 truncated
    // 5 153 342 B = 80 521 cache lines a frame = 41.1 % of the offer (1452 B offered, 855 B
    // prefetched, 597 B truncated per take). 192 is kept as a compile-time path for the A/B.
    // SHIPPED ON 1024 IN SESSION 76 (W3), measured by TWO area-clean ABBAs, both with pfhint=1
    // in both arms, on the session-76 binary 240edc02:
    //   cap76a  period 30, 131 pairs: cpu/draw -0.916 % +/- 0.163 % (2*SE), t = -11.27,
    //           whole-arm cpu/fr 31 303 -> 30 997 us = -306 us, draws 0.059 % apart,
    //           whole-arm/paired gap 0.004 pp, area 126/126 matched at |d| <= 0.087 %.
    //   cap76b  period 15, 243 pairs: cpu/draw -1.083 % +/- 0.155 % (2*SE), t = -13.98,
    //           whole-arm cpu/fr 31 322 -> 31 030 us = -292 us, draws 0.166 % apart,
    //           whole-arm/paired gap 0.012 pp, area 231/233 matched (99.1 %).
    // They agree 0.167 pp apart against a combined 2*SE of 0.225 pp. SESSION 77, BY OPCODE SCAN:
    // clang RUNTIME-UNROLLS the runtime overload by eight and leaves the compile-time <1024>
    // ROLLED, so session 76's "lower bound" reasoning is wrong. But the runtime form also pays
    // ~13 extra fixed instructions per vector, repaid only above 8 lines, and the mean vector is
    // ~2 lines: the SIGN of the shape term is UNDETERMINED, its size is under ~70 us, and the
    // stand resolves 53 us. NEITHER bound is established. Re-take with both arms compile-time.
    // Arming is proved by a counter in each run: da_pf_cap_b / da_pf_b goes 58.8 % -> 94.4 % of
    // the bytes the eleven vectors offer, i.e. ~69 500 extra cache lines prefetched per frame.
    // 1024 is the operating point: 1024|4096 read +0.200 % +/- 0.166 %, inside its own predicted
    // band; arm1 used the runtime form, so no cause is attributable. 384/512 is OPEN.
    {"KYTY_PREFETCH_CAP_B", "pfcap", 1024, 4096},
    // Session 83, measurement only: which phases of the render-mutex hold carry a MutScope.
    {"KYTY_MUT_WIDE", "mutwide", 0, 15},
    // Session 88, measurement only: where the one timestamp a slot of the image loop is
    // taken - after ResolveTextureWith (1) or at the memo-hit decision inside it (2).
    {"KYTY_BIND_WIT", "bindwit", 0, 2},
    // Session 90, route D1: the guest-memory import for BUFFER uploads instead of the
    // host memcpy into the staging ring.  0 = today, 1 = census only, 2 = take it.
    // Ships at 0: the import moves the guest read from UploadCopies to command-buffer
    // execution, and a CPU write into the range then waits for it (hostread_waits).
    {"KYTY_BUF_IMPORT", "bufimp", 0, 2},
}};

using KnobState = std::array<std::atomic<uint32_t>, static_cast<size_t>(Knob::Count)>;
using State     = std::array<std::atomic<bool>, static_cast<size_t>(Gate::Count)>;

void Initialize();

KnobState& KnobStates() {
	Initialize();
	return Detail::g_knobs;
}

State& States() {
	Initialize();
	return Detail::g_gates;
}

// Environment values of every gate and knob, then g_ready (the inline fast reads).
void Initialize() {
	static const bool initialized = [] {
		auto& states = Detail::g_knobs;
		for (size_t index = 0; index < states.size(); index++) {
			const auto& definition = KNOB_DEFINITIONS[index];
			const auto* value      = std::getenv(definition.environment);
			auto        parsed     = definition.fallback;
			if (value != nullptr && value[0] >= '0' && value[0] <= '9') {
				parsed = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
			}
			states[index].store(parsed < definition.limit ? parsed : definition.limit,
			                    std::memory_order_relaxed);
		}
		auto& gates = Detail::g_gates;
		for (size_t index = 0; index < gates.size(); index++) {
			const auto& definition = DEFINITIONS[index];
			const auto* value      = std::getenv(definition.environment);
			gates[index].store(value != nullptr ? value[0] == '1' : definition.fallback,
			                   std::memory_order_relaxed);
		}
		Detail::g_ready.store(true, std::memory_order_relaxed);
		return true;
	}();
	(void)initialized;
}

// The value text after "name=" for a whole-word name in the gate file, or nullptr. A name that is
// a prefix of another ("texfast" / "texfastcheck") must not match inside the longer one.
const char* FindAssignment(const char* text, const char* name) {
	const auto length = std::strlen(name);
	for (const char* found = std::strstr(text, name); found != nullptr;
	     found             = std::strstr(found + 1, name)) {
		const bool starts = found == text || found[-1] == ' ' || found[-1] == '\t' ||
		                    found[-1] == '\n' || found[-1] == '\r' || found[-1] == ',' ||
		                    found[-1] == ';';
		if (starts && found[length] == '=') {
			return found + length + 1;
		}
	}
	return nullptr;
}

const char* GateFile() {
	static const char* const path = std::getenv("KYTY_GATE_FILE");
	return path;
}

// KYTY_GATE_SCHEDULE="<N>[+<start>]:<arm>|<arm>[|...]" alternates the arms in blocks of N
// presents from frame <start> on. An arm is the text of a gate file, so the parser below is the
// same FindAssignment and a name an arm does not list keeps its state, exactly as in the file.
// Two textually identical arms are the idle A/A run that declares a run's own threshold.
constexpr size_t SCHEDULE_ARMS_MAX = 8;
constexpr size_t SCHEDULE_TEXT_MAX = 512;

struct Schedule {
	uint32_t period = 0; // presents per block; 0 = no schedule
	uint32_t start  = 0; // first frame the schedule applies to
	uint32_t arms   = 0;
	bool     abba   = false; // two arms in the order A B B A instead of A B A B
	std::array<std::array<char, SCHEDULE_TEXT_MAX>, SCHEDULE_ARMS_MAX> text {};
	// Names any arm assigns: the gate file must not fight the schedule over them, or every flip
	// would write them twice and log a change.
	std::array<bool, static_cast<size_t>(Gate::Count)> owns_gate {};
	std::array<bool, static_cast<size_t>(Knob::Count)> owns_knob {};
};

const Schedule& ScheduleOf() {
	static const Schedule schedule = [] {
		Schedule    s {};
		const auto* value = std::getenv("KYTY_GATE_SCHEDULE");
		if (value == nullptr || value[0] < '0' || value[0] > '9') {
			return s;
		}
		char*      tail   = nullptr;
		const auto period = std::strtoul(value, &tail, 10);
		if (period == 0 || period > 100000 || tail == nullptr) {
			return Schedule {};
		}
		unsigned long start = 0;
		if (*tail == '+') {
			start = std::strtoul(tail + 1, &tail, 10);
		}
		if (tail == nullptr || *tail != ':') {
			return Schedule {};
		}
		const char* cursor = tail + 1;
		while (s.arms < SCHEDULE_ARMS_MAX) {
			const char*  bar = std::strchr(cursor, '|');
			const size_t length =
			    bar != nullptr ? static_cast<size_t>(bar - cursor) : std::strlen(cursor);
			if (length == 0 || length >= SCHEDULE_TEXT_MAX) {
				return Schedule {};
			}
			std::memcpy(s.text[s.arms].data(), cursor, length);
			s.text[s.arms][length] = '\0';
			s.arms++;
			if (bar == nullptr) {
				break;
			}
			cursor = bar + 1;
		}
		if (s.arms == 0) {
			return Schedule {};
		}
		for (uint32_t arm = 0; arm < s.arms; arm++) {
			for (size_t index = 0; index < s.owns_gate.size(); index++) {
				s.owns_gate[index] = s.owns_gate[index] ||
				                     FindAssignment(s.text[arm].data(), DEFINITIONS[index].name) != nullptr;
			}
			for (size_t index = 0; index < s.owns_knob.size(); index++) {
				s.owns_knob[index] =
				    s.owns_knob[index] ||
				    FindAssignment(s.text[arm].data(), KNOB_DEFINITIONS[index].name) != nullptr;
			}
		}
		// KYTY_GATE_SCHEDULE_ABBA=1 counterbalances a two-arm schedule: the block index runs
		// through a Gray code, so the arms go A B B A A B B A and neither of them is always the
		// second of its cycle. Session 67 measured a +0.36 % bias on the idle A/A run without it.
		const auto* abba = std::getenv("KYTY_GATE_SCHEDULE_ABBA");
		s.abba           = abba != nullptr && abba[0] == '1' && s.arms == 2;
		s.period         = static_cast<uint32_t>(period);
		s.start          = static_cast<uint32_t>(start);
		return s;
	}();
	return schedule;
}

// Applies the text of a gate file or of a schedule arm. `skip_*` are the names the schedule owns
// when the text comes from the file.
void ApplyText(const char* text, uint32_t frame, const bool* skip_gate,
               const bool* skip_knob) noexcept {
	auto& states = States();
	for (size_t index = 0; index < states.size(); index++) {
		if (skip_gate != nullptr && skip_gate[index]) {
			continue;
		}
		const auto& definition = DEFINITIONS[index];
		const auto* value      = FindAssignment(text, definition.name);
		if (value == nullptr || (value[0] != '0' && value[0] != '1')) {
			continue;
		}
		const bool wanted = value[0] == '1';
		if (states[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%d frame=%u\n", definition.name, wanted ? 1 : 0, frame);
		}
	}

	auto& knobs = KnobStates();
	for (size_t index = 0; index < knobs.size(); index++) {
		if (skip_knob != nullptr && skip_knob[index]) {
			continue;
		}
		const auto& definition = KNOB_DEFINITIONS[index];
		const auto* value      = FindAssignment(text, definition.name);
		if (value == nullptr || value[0] < '0' || value[0] > '9') {
			continue;
		}
		auto wanted = static_cast<uint32_t>(std::strtoul(value, nullptr, 10));
		wanted      = wanted < definition.limit ? wanted : definition.limit;
		if (knobs[index].exchange(wanted, std::memory_order_relaxed) != wanted) {
			LOGF("Gate: %s=%u frame=%u\n", definition.name, wanted, frame);
		}
	}
}

void PollGateFile(uint32_t frame) noexcept {
	const auto* path = GateFile();
	if (path == nullptr) {
		return;
	}

	// The file is tiny and written by the measurement script: "copy=1 srtpages=0 clamp=1".
	// Names that are missing keep their current state; a malformed file changes nothing.
	std::array<char, 4096> text {};
	auto*                 file = std::fopen(path, "rb");
	if (file == nullptr) {
		return;
	}
	const auto read = std::fread(text.data(), 1, text.size() - 1, file);
	std::fclose(file);
	if (read == text.size() - 1) {
		// The last token may be cut in the middle of a number: apply nothing.
		static bool warned = false;
		if (!warned) {
			warned = true;
			LOGF("Gate: file %s is too long, ignored\n", path);
		}
		return;
	}
	text[read] = '\0';

	const auto& schedule = ScheduleOf();
	ApplyText(text.data(), frame, schedule.owns_gate.data(), schedule.owns_knob.data());
}

// Exact block boundaries in flips: this runs once per flip with a monotonic counter.
void PollSchedule(uint32_t frame) noexcept {
	const auto& schedule = ScheduleOf();
	// The line the caller logs after this reports the interval that ran under the previous arm.
	Detail::g_arm_reported.store(Detail::g_arm.load(std::memory_order_relaxed),
	                             std::memory_order_relaxed);
	Detail::g_block_reported.store(Detail::g_block.load(std::memory_order_relaxed),
	                               std::memory_order_relaxed);
	if (schedule.period == 0 || frame < schedule.start) {
		return;
	}
	const auto block = (frame - schedule.start) / schedule.period;
	const auto arm   = schedule.abba ? (((block >> 1U) ^ block) & 1U) : block % schedule.arms;
	Detail::g_arm.store(arm, std::memory_order_relaxed);
	Detail::g_block.store(block, std::memory_order_relaxed);
	// One producer: Poll only ever runs on the presentation thread.
	static uint32_t applied = 0xffffffffu;
	if (block == applied) {
		return;
	}
	applied = block;
	LOGF("GateArm: arm=%u arms=%u block=%u frame=%u period=%u abba=%u text=%s\n", arm,
	     schedule.arms, block, frame, schedule.period, schedule.abba ? 1U : 0U,
	     schedule.text[arm].data());
	ApplyText(schedule.text[arm].data(), frame, nullptr, nullptr);
}

} // namespace

bool Detail::EnabledSlow(Gate gate) noexcept {
	return States()[static_cast<size_t>(gate)].load(std::memory_order_relaxed);
}

uint32_t Detail::ValueSlow(Knob knob) noexcept {
	return KnobStates()[static_cast<size_t>(knob)].load(std::memory_order_relaxed);
}

void Poll(uint32_t frame) noexcept {
	PollGateFile(frame);
	// The schedule owns the names its arms assign, so the file above skipped them.
	PollSchedule(frame);
}

} // namespace Common::Gates
