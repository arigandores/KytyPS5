#ifndef EMULATOR_SRC_COMMON_GATES_H_
#define EMULATOR_SRC_COMMON_GATES_H_

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

namespace Common::Gates {

// Optimizations that can be turned on and off while the emulator runs, so that one gameplay run
// can compare them against itself instead of against another run with a different trajectory.
// Each gate starts from its own environment variable and keeps that value unless a gate file is
// given (KYTY_GATE_FILE), which Poll() re-reads once per flip.
enum class Gate : uint32_t {
	ConstantCopy,   // KYTY_CBUFFER_DIRECT_COPY, file name "copy"
	SrtPagePersist, // KYTY_SRT_PAGE_PERSIST,    file name "srtpages"
	ClampMemo,      // KYTY_CLAMP_MEMO,          file name "clamp"
	RegionEpoch,    // KYTY_REGION_EPOCH,        file name "regionepoch"
	SrtMemo,        // KYTY_SRT_MEMO,            file name "srtmemo"
	SrtMemoCheck,   // KYTY_SRT_MEMO_VERIFY,     file name "smemocheck"
	BdaRegionStamps, // KYTY_BDA_REGION_STAMPS,  file name "bdastamp"
	BackingPages,   // KYTY_BACKING_PAGES,       file name "backpages"
	SrtStat,        // KYTY_SRT_STAT,            file name "srtstat"
	MetaLock,       // KYTY_META_LOCK,           file name "metalock"
	DrawAhead,      // KYTY_DRAW_AHEAD,          file name "drawahead"
	DrawAheadUse,   // KYTY_DRAW_AHEAD_USE,      file name "dause"
	AsyncSubmit,    // KYTY_ASYNC_SUBMIT,        file name "asyncsubmit"
	ImageRecycle,   // KYTY_IMAGE_RECYCLE,       file name "imgrecycle"
	RecordThread,   // KYTY_RECORD_THREAD,       file name "recordthread", taken per command buffer
	TrackLockFree,  // KYTY_TRACK_LOCKFREE,      file name "trackfree"
	TrackLockFreeVerify, // KYTY_TRACK_LOCKFREE_VERIFY, file name "tfcheck"
	ProtectFast,    // KYTY_PROTECT_FAST,        file name "protfast"
	ShaderWriteLocal, // KYTY_SHADER_WRITE_LOCAL, file name "swlocal"
	ShaderWriteDefer, // KYTY_SHADER_WRITE_DEFER, file name "swdefer"
	GdsEpoch,       // KYTY_GDS_EPOCH,           file name "gdsepoch"
	AtomicImageBarrier, // KYTY_ATOMIC_IMAGE_NO_BARRIER, file name "atomimg"
	DescriptorRing, // KYTY_DESCRIPTOR_RING,     file name "dsring"
	RecordPackets,  // KYTY_RECORD_PACKETS,      file name "recpack"
	SyncFree,       // KYTY_SYNC_FREE,           file name "syncfree"
	SyncFreeVerify, // KYTY_SYNC_FREE_VERIFY,    file name "sfcheck"
	ProtectBatch,   // KYTY_PROTECT_BATCH,       file name "protbatch"
	ProtectBatchVerify, // KYTY_PROTECT_BATCH_VERIFY, file name "pbcheck"
	TexFaultHint,   // KYTY_TEX_FAULT_HINT,      file name "texfaulthint"
	DrawAheadClass,    // KYTY_DRAW_AHEAD_CLASS,    file name "daclass"
	DrawAheadPrefetch, // KYTY_DRAW_AHEAD_PREFETCH, file name "daprefetch"
	DrawAheadClone,    // KYTY_DRAW_AHEAD_CLONE,    file name "daclone"
	TexLru,         // KYTY_TEX_LRU,             file name "texlru"
	TexFast,        // KYTY_TEX_FAST,            file name "texfast"
	TexFastCheck,   // KYTY_TEX_FAST_VERIFY,     file name "texfastcheck"
	TexMemo2,       // KYTY_TEX_MEMO2,           file name "texmemo2"
	ClampVma,       // KYTY_CLAMP_VMA,           file name "clampvma"
	SamplerMemo,    // KYTY_SAMPLER_MEMO,        file name "smpmemo"
	BindSpare,      // KYTY_BIND_SPARE,          file name "bindspare"
	FrameStatsLean, // KYTY_FRAME_STATS_LEAN,    file name "fslean" (count the FrameTrace main line only)
	// Session 57, A2/A3 (page protection).
	ApplySkip,      // KYTY_APPLY_SKIP,          file name "applyskip"
	// Session 57, A4 (record publish).
	RecordBatch,    // KYTY_RECORD_BATCH,        file name "recbatch" (one publish per draw)
	RecordRelaxed,  // KYTY_RECORD_RELAXED,      file name "recrelax" (head store without lock prefix)
	RecordPin,      // KYTY_RECORD_PIN,          file name "recpin" (record thread follows "dapin"; default 1 since session 63)
	// Session 57, A1 (sticky pages).
	StickyStat,     // KYTY_STICKY_STAT,         file name "stkstat" (A1 ceiling counters only)
	// Session 57, E1/E2/E9 (draw statistics).
	DrawStat,       // KYTY_DRAW_STAT,           file name "drawstat" (E1/E2/E9 counters)
	DrawStatSlow,   // KYTY_DRAW_STAT_SLOW,      file name "dpslow" (E1 runs also cut by slow bits)
	// Session 57, A6/A7 and track B.
	DrawStateReuse, // KYTY_DRAW_STATE_REUSE,    file name "drawstate" (B1: per-thread draw state)
	SnapshotKeep,   // KYTY_SNAPSHOT_KEEP,       file name "snapkeep" (B4: kept snapshot storage)
	BufLru,         // KYTY_BUF_LRU,             file name "buflru"
	// Session 58, B4 follow-up (snapshot copies).
	SnapshotDiff,   // KYTY_SNAPSHOT_DIFF,       file name "snapdiff" (assign changed vectors only)
	SnapshotSwap,   // KYTY_SNAPSHOT_SWAP,       file name "snapswap" (swap on a slot's last use)
	// Session 58, M2 step 1 (buffer request memo).
	BufFast,        // KYTY_BUF_FAST,            file name "buffast"
	BufFastCheck,   // KYTY_BUF_FAST_VERIFY,     file name "buffastcheck"
	// Session 58, A3 phase 2 (one host protection flush per BDA dirty-range pass).
	ProtectBatchPass, // KYTY_PROTECT_BATCH2,     file name "protbatch2"
	// Session 58, Sky Garden hang: liveness of the async-copy timeline semaphore.
	AsyncCopyIdleSignal, // KYTY_ASYNC_COPY_IDLE_SIGNAL, file name "acopyidle"
	// Session 59, M1 producer off the critical thread.
	DrawAheadWalk,  // KYTY_DRAW_AHEAD_WALK,     file name "dawalk" (shadow walk on its own thread at submit)
	RenderTargetFast, // KYTY_RT_FAST,           file name "rtfast" (reuse the target views of the previous draw)
	// Session 60, B3: program lookup served by the previous draw's register inputs.
	ProgMemo,       // KYTY_PROG_MEMO,           file name "progmemo"
	ProgMemoCheck,  // KYTY_PROG_MEMO_VERIFY,    file name "progmemocheck"
	// Session 60, item 4: write watchers of read-only uploads armed by the protection worker.
	ArmDefer,       // KYTY_ARM_DEFER,           file name "armdefer"
	ArmDeferCheck,  // KYTY_ARM_DEFER_VERIFY,    file name "armcheck"
	// Session 61, ceiling experiment: M1 results taken without the witness check (UNSOUND - a
	// guest write between the worker read and the draw goes unnoticed; measurement only).
	DrawAheadWitness, // KYTY_DRAW_AHEAD_WITNESS, file name "dawitness" (default 1; 0 = skip the check)
	// Session 61: the witness compares live runs through the worker's host pointers (backing map
	// epoch as witness), prefetched up front, instead of a page-cache lookup per run.
	DrawAheadWitnessPtr, // KYTY_DRAW_AHEAD_WITNESS_PTR, file name "dawitptr"
	// Session 61: the M1 walk prefetches the slot probes of a request a few requests ahead.
	DrawAheadQueuePrefetch, // KYTY_DRAW_AHEAD_QUEUE_PREFETCH, file name "daqpre"
	// Session 62, item 3 ceiling (diagnostic): shadow compare of every stream-ring constant copy.
	CbStat,         // KYTY_CB_STAT,             file name "cbstat"
	// Session 62, item 2: lazy-handle image transitions and buffer uploads as records.
	RecordImageBarriers, // KYTY_RECORD_IMAGE_BARRIERS, file name "recimg"
	RecordUploads,       // KYTY_RECORD_UPLOADS,        file name "recup"
	// Session 64, E6: the read-only binding resolution repeated inline on the GuestGpu thread.
	ShadowInline,        // KYTY_SHADOW_INLINE,         file name "shadowinline"
	// Session 67, infrastructure: the guest's save-data memory is kept on disk between runs. Read
	// once when the game sets its memory up (about seven seconds in), so turning this on mid-run
	// only enables writing.
	SavePersist,         // KYTY_SAVE_PERSIST,          file name "savepersist"
	// Session 68, ceiling of the occlusion emulation (measurement only: the game stops seeing
	// anything and the picture breaks). The dump publishes a ready result of 0 samples instead of
	// the synthetic counter, so the guest's visibility tests answer "not visible".
	OcclusionZero,       // KYTY_OCCLUSION_ZERO,        file name "occzero"
	// Session 68, the serial floor A: the mutating part of the draw path, timed in place. The
	// intervals nest, so only the outermost one counts (MutScope in frameStats.h).
	MutateTime,          // KYTY_A_MUTATE,              file name "amut"
	// Session 68: the binding interval of a draw, split by whether the pixel stage is live. Answers
	// whether the 24 % of draws that are depth-only (counter da_px_off) pay the full price.
	PixelOffStat,        // KYTY_PX_STAT,               file name "pxstat"
	// Session 69: the phases of the render-mutex hold (mh_* in FrameTrace-x). Session 68 measured
	// the hold at 29.5 ms of a 34.0 ms frame but not what runs inside it. One timestamp per phase
	// boundary; it also arms MutexMark, so a_hold_us/a_wait_us come with it.
	MutexSites,          // KYTY_MUT_SITE,              file name "mutsite"
	// Session 69, ceiling of the guest<->GPU image ping-pong (measurement only: the surface keeps
	// whatever texels it already holds, so the picture may break). Skips the re-upload of an image
	// whose only staleness came from a GPU buffer write and whose guest source is at least
	// "imgskipkb" KiB.
	ImageSkipGpuStale,   // KYTY_IMG_SKIP_GPU_STALE,    file name "imgskip"
	// Session 70: two formats the packed-clear decoder was missing, R8_UINT/R8_SINT for colour and
	// D16_UNORM for depth. Without them a clear the guest asked for is discarded, the compute fill
	// writes guest memory instead, and the texture cache re-uploads the surface out of it - 8.65 MiB
	// per frame in Sky Garden, one colour and one depth target. Same pixels, less work.
	ClearDecodeWide,     // KYTY_CLEAR_DECODE_WIDE,     file name "cleardec"
	// Session 71, measurement only (default 1 = as before): the session-61 epoch-witness ceiling.
	// Witness::Build stamps the tracking regions of every recorded read and AheadTake walks them
	// again on every hit, inside the interval da_take_us times. Session 70 closed the question it
	// answers, so this exists to size what the answer still costs.
	DrawAheadEpochCeiling, // KYTY_DA_EPOCH_CEILING,    file name "daepceil"
	// Session 73, W6: the first candidate written for the CLEAN loop of the M1 witness, measured by
	// session 72 at 1.033 ms of wall per frame - 53.6 % of the whole verify on 11.6 % of the words.
	// When the clean loop's page lookup fails it decides per word through ReadShaderGuestMemory,
	// whose first act is to retry the same doomed page lookup; the gate asks the range predicate
	// about the RUN once instead. Same answer by construction (pipelineCache.cpp), less work.
	DrawAheadCleanRange, // KYTY_DA_CLEAN_RANGE,      file name "dawitfb"
	// Session 73, C1: the tiler's detile dispatch writes the destination image directly through a
	// UINT storage view, so the scratch buffer, the fill that gave its pad bytes a defined value
	// and the vkCmdCopyBufferToImage that moved it all disappear. Session 72 measured the ceiling
	// BY TIME - copy_fuse 1115.7 us + the fusable share of the fill 126.0 us = 1241.7 us per frame,
	// 8.06 % of non-idle GPU, 42x what the stand resolves. Everything that does not qualify keeps
	// the scratch path unchanged.
	ImageDetileFuse, // KYTY_IMAGE_DETILE_FUSE,   file name "imgfuse"
	// Session 73, W7: the M1 witness's clean loop pays 15 097 GPU-clean page predicates per frame
	// (da_cl_miss) and every one of them answers "clean" (da_cl_fail = 0). Two of those predicates'
	// three parts are avoidable: TextureCache::IsRegionGpuModified takes a spin lock where the
	// tree's own lock-free MayHaveImages would answer, and the address translation is the one the
	// persistent live page table already holds. Same answers, fewer locks.
	DrawAheadCleanPage, // KYTY_DA_CLEAN_PAGE,      file name "dawitcp"
	// Session 74, W8: the clean-page table of the M1 witness survives the AheadTake call, keyed on
	// (BackingMapEpoch, GpuDirtyGen) and tag-invalidated. Predicted before it was written by the
	// probe of patch_cleanprobe.py: da_cl_pmiss 1402.9 against today's da_cl_miss 15 098.4.
	DrawAheadCleanGen,       // KYTY_DA_CLEAN_GEN,        file name "dawitcg"
	DrawAheadCleanGenVerify, // KYTY_DA_CLEAN_GEN_VERIFY, file name "dawitcgcheck"
	// Session 75: pipelineCache.cpp includes <xmmintrin.h> below fifty-six project headers, one of
	// which has already pulled in winnt.h, whose UNGUARDED "#define _MM_HINT_T0 1" (MSVC numbering,
	// winnt.h:3649) therefore wins over clang's 3. clang lowers _mm_prefetch(p, sel) as
	// __builtin_prefetch(p, 0, sel) with GCC locality, where 1 == T2, so every prefetch of the M1
	// witness path emits PREFETCHT2 - L2, never L1 - while the source asks for L1. The installed
	// 017fc031 carries 50 prefetcht2 against 13 prefetcht0. This gate selects the intended L1 form;
	// at 0 the emitted instruction is byte-identical to today's. A prefetch changes no value and no
	// decision, so the arms are behaviourally identical by construction.
	PrefetchHintL1, // KYTY_PREFETCH_HINT_L1,    file name "pfhint"
	Count,
};

// Numeric settings with the same life cycle as the gates ("name=<decimal>" in the gate file).
enum class Knob : uint32_t {
	DrawAheadThreads, // KYTY_DRAW_AHEAD_THREADS, file name "dathreads"
	RecordArenaMb,    // KYTY_RECORD_ARENA_MB,    file name "recarena"
	DescriptorSetBatch, // KYTY_DESCRIPTOR_BATCH,  file name "dsbatch"
	DescriptorPoolSets, // KYTY_DESCRIPTOR_POOL,   file name "dspool"
	RecordSpinUs,       // KYTY_RECORD_SPIN_US,    file name "recspin" (record thread poll, us)
	DrawAheadPin,       // KYTY_DRAW_AHEAD_PIN,    file name "dapin" (0 off, 1/2 L3 group, else mask)
	ProcessPin,         // KYTY_PROCESS_PIN,       file name "procpin" (0 start mask, 1 L3 group, else mask)
	FaultWindowKb,      // KYTY_FAULT_WINDOW_KB,   file name "faultkb" (CPU write-fault window, KiB; 4 = one page, default 64)
	DrawAheadWalkLead,  // KYTY_DRAW_AHEAD_WALK_LEAD, file name "dawalklead" (gate "dawalk": walk at most this many submissions ahead of processing, 0 = no hold)
	RecordPublishEvery, // KYTY_RECORD_PUBLISH_N,  file name "recpubn" (session 61: publish the record head at most every N draw-stream records; 0/1 = every record)
	ShadowResolve,      // KYTY_SHADOW_RESOLVE,    file name "shadowresolve" (session 64, E4: K shadow readers of the binding resolution, 0 = off)
	ShadowMask,         // KYTY_SHADOW_MASK,       file name "shadowmask" (session 64: 1 = image probes, 2 = buffer probes, 3 = both)
	M4Baton,            // KYTY_M4_BATON,          file name "m4baton" (session 68: draws of the PM4 range a second thread runs while GuestGpu is parked, 0 = off)
	ImageSkipKb,        // KYTY_IMG_SKIP_KB,       file name "imgskipkb" (gate "imgskip": smallest guest source of a skipped upload, KiB; 0 = every buffer-only stale image)
	// Session 72, measurement only and UNSOUND to ship: which loop of VerifyWitness to skip, so
	// that the 2.016 ms of the M1 witness can be divided between them by an A/B instead of being
	// modelled from the word census. 0 = today (compare everything), 1 = skip the clean-run loop,
	// 2 = skip the live-run loop. Proof it armed: the counter da_loop_skip.
	DrawAheadWitnessLoop, // KYTY_DA_WITNESS_LOOP,  file name "dawitloop" (0 off, 1 skip clean, 2 skip live)
	Count,
};

namespace Detail {

// Published once the environment was read (the first slow read), then by Poll. Until `g_ready`
// is set every read takes the slow path, so a read during static initialization still sees the
// environment.
inline constinit std::array<std::atomic<bool>, static_cast<size_t>(Gate::Count)>     g_gates {};
inline constinit std::array<std::atomic<uint32_t>, static_cast<size_t>(Knob::Count)> g_knobs {};
inline constinit std::atomic<bool>                                                   g_ready {false};

// KYTY_GATE_SCHEDULE: the arm and block of the schedule running now, and the ones of the frame
// interval the caller is about to report. Poll runs before that line is logged, so the interval
// it reports was lived under the previous arm.
inline constinit std::atomic<uint32_t> g_arm {0};
inline constinit std::atomic<uint32_t> g_block {0};
inline constinit std::atomic<uint32_t> g_arm_reported {0};
inline constinit std::atomic<uint32_t> g_block_reported {0};

[[nodiscard]] bool     EnabledSlow(Gate gate) noexcept;
[[nodiscard]] uint32_t ValueSlow(Knob knob) noexcept;

} // namespace Detail

// Relaxed read of the current state. Safe to call from any thread and from hot paths.
inline bool Enabled(Gate gate) noexcept {
	if (!Detail::g_ready.load(std::memory_order_relaxed)) [[unlikely]] {
		return Detail::EnabledSlow(gate);
	}
	return Detail::g_gates[static_cast<size_t>(gate)].load(std::memory_order_relaxed);
}

// Relaxed read of a knob's current value.
inline uint32_t Value(Knob knob) noexcept {
	if (!Detail::g_ready.load(std::memory_order_relaxed)) [[unlikely]] {
		return Detail::ValueSlow(knob);
	}
	return Detail::g_knobs[static_cast<size_t>(knob)].load(std::memory_order_relaxed);
}

// The arm and block of the interval a caller is about to report (see g_arm_reported).
inline uint32_t ReportedArm() noexcept {
	return Detail::g_arm_reported.load(std::memory_order_relaxed);
}
inline uint32_t ReportedBlock() noexcept {
	return Detail::g_block_reported.load(std::memory_order_relaxed);
}

// Re-reads the gate file (if any), advances the schedule (if any) and publishes changes. Called
// once per flip.
void Poll(uint32_t frame) noexcept;

} // namespace Common::Gates

#endif // EMULATOR_SRC_COMMON_GATES_H_
