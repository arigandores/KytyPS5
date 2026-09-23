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
	// Session 82, MEASUREMENT ONLY - it changes no behaviour and no output.  The binding phase
	// (mh_bind_us, about 10.5 ms of a 32.8 ms CPU frame) rebuilds PreparedBindings on every draw:
	// ~9.5 texture resolves and ~9.5 ObtainBuffer calls each, 48 000 of each per frame.  The
	// program memo says 74.8 % of draws repeat the previous draw's register inputs (pmemo_hit
	// 6519.7 against pmemo_miss 2200.2), but whether the RESOURCE SNAPSHOT repeats with them -
	// the thing a binding memo would key on - has never been measured.  This gate hashes the
	// binding inputs of each stage, counts the repeats (bk_hit / bk_miss, bk_draw_hit /
	// bk_draw_miss) and splits the binding phase by them (bk_hit_us / bk_miss_us), so the ceiling
	// of that optimisation is known before it is written.
	BindKeyStat,    // KYTY_BIND_KEY,            file name "bindkey"
	// Session 82, W1: the BDA region walk consults a write map before the per-region stamp.
	// bind78a pays 18 582 region visits a frame (bda_skip 17 518 + bda_scan 1 064) across 181
	// PrepareBda calls of 12.05 us each, and every visit is two dependent loads of scattered
	// memory. The map is a conservative superset of "the stamp moved" - a clear bit PROVES the
	// stamp is unchanged, a set bit proves nothing and falls through to today's code unchanged -
	// so the arms answer identically by construction. Proof it armed: bda_bskip, which is 0 at 0.
	// MEASURED AND IT DOES NOT PAY - kept at 0. bdb82a, a valid ABBA (area split -0.004 %, pair
	// match 100 %, work -0.146 %), armed perfectly (bda_bskip 0 against 20 601 a frame, 99.95 % of
	// all skips, bda_scan 1 066 in BOTH arms, bda_bit_bad 0) and read -50.8 us +- 87.5 (2*SE):
	// inside the A/A noise floor of +-75...92 us. The 17 518 skipped region visits a frame were
	// therefore NOT costing the ~1 ms the population suggested - the ~103 managers are re-read by
	// all 180 PrepareBda calls of the frame and stay hot, so the loads saved were already cheap.
	// What bda_us 2 181 us a frame is actually spent on is NOT MEASURED; the m_buffers std::map
	// lookups of SynchronizeBuffersInRange are the next candidate.
	BdaWriteBits,       // KYTY_BDA_WRITE_BITS,      file name "bdabits"
	// Runs the stamp comparison anyway on a skipped region and counts disagreements in
	// bda_bit_bad, which must read 0. Costs the loads the gate exists to avoid - measurement only.
	BdaWriteBitsVerify, // KYTY_BDA_WRITE_BITS_VERIFY, file name "bdabitscheck"
	// Session 83, route B: the binding-path package of PLAN_82_bind.md items 1, 4 and 9.  One
	// gate for three changes, because ROADMAP.md 5.3 fixes that route B ships in packages: each
	// of the three is individually inside the A/A noise floor of +-75...92 us.
	//   1 - the null T# descriptor memo. 1 418.1 resolutions a frame build a ~584-byte ImageDesc
	//       and call FindImage (scheduler, validate, constrain, spin lock, map) for an answer
	//       that is a pure function of three fields with at most NINE distinct values. Validated
	//       on every hit against the live slot, which is strictly more than GetNullImage does.
	//   4 - IR::FindBinding, an out-of-line linear scan, asked three questions about the SAME
	//       BindingLayout at 9 131 stages a frame. One pass answers all three. No cache and no
	//       invalidation: the mask is recomputed per stage and handed over in PreparedBindings.
	//   9 - GraphicsBindings local_bindings, fifteen empty-vector constructors and destructors
	//       per draw that are never read while ReuseBindingsEnabled() is on (the default).
	// Session 84 adds a FOURTH item and SHIPS the package (default 0 -> 1):
	//  11 - the descset bundle, two of its three edits.  descriptor_count / write_count /
	//       push_stages are constants of the pipeline and are cached on it, so CommitBindings
	//       stops rebuilding them per draw by walking program.bindings.descriptors; and the
	//       m_image_occurrences invariant loop - a pure assertion with no consumer - moves
	//       behind DrawStat::On().  Item 11's third edit, a sub-range push-constant write, was
	//       REFUSED: it leaves the remainder undefined rather than zero and no self-check can
	//       detect the failure.
	// Measured on bpk84a, VALID on all six criteria: cpu_net_us -251.7 +- 82.8 us (2*SE),
	// t = -6.08, against the -150 us threshold sealed before the run; cpu/draw -0.817 % +-
	// 0.140 %, t = -11.70 over 117 matched pairs; gpu_busy_us +0.069 %, inside its own noise.
	// Video: bpc84a, 0 one-frame glitches.
	// Arming: tnull_hit, bp_mask, bp_dsc and the symmetric pair bp_local_make / bp_local_skip.
	BindPack,      // KYTY_BIND_PACK,          file name "bindpack"
	// Recomputes the real predicate beside every fast answer and counts disagreements in
	// bp_bad, which must read 0. Costs everything the gate saves - measurement only.
	BindPackVerify, // KYTY_BIND_PACK_VERIFY,  file name "bindpackcheck"
	// Session 83, MEASUREMENT ONLY: the wait and the HOLD of PipelineCache::m_mutex at its
	// three per-draw and per-dispatch acquisitions.  The floor of session 83 wraps the whole of
	// RefreshShaders (5 850 us) because it CONTAINS mutation; this says how much of it actually
	// runs under the only lock it takes, which is what decides whether that 5 850 us is serial
	// or merely serialised by the instrument.  DESIGN_82_parallel.md section 6 item 13.
	PipeLockStat,   // KYTY_PIPE_LOCK_STAT,     file name "plkstat"
	// Session 84, MEASUREMENT ONLY (PLAN_82_bind.md item 0, ROADMAP.md route C): how many of the
	// ~95 000 descriptor slots a frame are identical to the slot the SAME STAGE bound in the
	// previous COMMITTED draw.  One site in CommitBindings, eleven Add-counters, no lock, no
	// allocation and no Scope, so all of them read under KYTY_FRAME_TRACE=lite.  Arming: every
	// sl_* is exactly 0.000 in the arm at 0, sl_img_n matches b_texn and sl_buf_n matches bb_n
	// to 2 %, and sl_over - slots past the translation-time bounds - must read 0.
	SlotStat,       // KYTY_SLOT_STAT,          file name "slotstat"
	// Session 84, MEASUREMENT ONLY: PrepareBda split into the probe every call pays and the scan
	// only a miss reaches.  bda_us reads 0 under KYTY_FRAME_TRACE=lite because it is a Scope, and
	// FrameStats::Lap would too, so this uses the plkstat idiom instead.  Arming: bda_lap_n.
	BdaLap,         // KYTY_BDA_LAP,            file name "bdalap"
	// Session 85, MEASUREMENT ONLY (ROADMAP.md route C): what one descriptor slot costs in
	// the BIND phase, split by outcome.  Every existing timer of that phase is a
	// FrameStats::Scope and reads 0 under KYTY_FRAME_TRACE=lite; this uses the plkstat
	// idiom (LapScope) instead.  Two timestamps per stage, never per slot - a per-slot pair
	// would cost as much as the thing it measures.  Arming: bl_stage_n, and bl_img_n against
	// b_texn / bl_buf_n against bb_n.
	BindLap,        // KYTY_BIND_LAP,           file name "bindlap"
	// Session 85, MEASUREMENT ONLY: the ~1.88 ms FIXED part of bda_scan_us, which session 84
	// measured as an OLS intercept and could not attribute.  Splits the scan into the
	// m_buffers descents, the region walk, the dirty-bit collection and the uploads, and
	// charges the frame's FIRST scanning call apart from every later one.  Arming:
	// bda_bound_n against bda_rng, bda_first_n + bda_late_n against bda_n - bda_hit.
	BdaSplit,       // KYTY_BDA_SPLIT,          file name "bdasplit"
	// Session 85: the self-check PLAN.md of session 84 declared for the census and never
	// built.  It is NOT a value check - the previous draw's value exists nowhere but in the
	// shadow table - it is an ELEMENT-COUNT check derived from the compiled BindingLayout
	// rather than from the runtime vectors, and it is exactly what would have caught the
	// DynamicStorage bias (sl_img_n counts bindings, the write list emits elements).
	// Costs a second walk of program.bindings.descriptors per stage - measurement only.
	SlotStatVerify, // KYTY_SLOT_STAT_VERIFY,   file name "slotstatcheck"
	// Session 85, route B: PLAN_82_bind.md item 6a.  ObtainBuffer asks UploadEpoch +
	// HasCurrentUpload about a range and, on "already current", calls SynchronizeBuffer -
	// whose first act is the same two evaluations of the same range on the same thread,
	// followed by return.  ~8 486 calls a frame.  The arms differ only in that a guest write
	// landing between the two reads is picked up one binding later instead of at once; the
	// dirty bits are untouched, so the next request for that range uploads it.  be_race
	// MEASURES how often that window is entered instead of assuming it is empty.
	BufEpochFast,       // KYTY_BUF_EPOCH_FAST,   file name "bindpack2"
	// Recomputes the replaced predicate beside every short circuit AND calls SynchronizeBuffer
	// anyway, so the checked arm does the work the gate removes.  bp2_bad must read 0.
	BufEpochFastVerify, // KYTY_BUF_EPOCH_VERIFY, file name "bindpack2check"
	// Session 86, MEASUREMENT ONLY (ROADMAP.md route D2): mh_prog_us is 5 850 us a frame and
	// nobody has ever asked what it IS.  Three of its four parts are already instrumented -
	// the lock by "plkstat", the memo compare by pmemo_chk_us - but the key build, the map
	// lookup and the materialisation are FrameStats::Lap, which reads 0 under
	// KYTY_FRAME_TRACE=lite.  This re-emits them on the LapScope idiom and adds the
	// key_hit / key_miss split that does not exist, so the shipped gate "progmemo" can serve
	// as the source of variation a collinear regression could not supply (the texfast trick
	// of session 85).  Every counter is restricted to slot < 2 - the draw's VS and PS - or
	// the denominator swallows dispatch and prefetch.  Arming: pg_n == pl_prog_n exactly.
	ProgLap,            // KYTY_PROG_LAP,           file name "proglap"
	// Session 86, MEASUREMENT ONLY (ROADMAP.md route D4): how many consecutive draws differ by
	// nothing, by push constants alone, or by exactly one buffer binding.  The necessary
	// condition - the same pipeline - is ALREADY measured by progmemo's pmemo_pipe at 77.2 %
	// of draws, so the open question is the descriptor delta and that is what this counts.
	// One site in ExecutePreparedDraw, past the AsyncPipelines skip, before the packet/direct
	// split.  Every bucket has an _nr twin with stream-ring slots excluded, because ~35 % of
	// buffer slots take a fresh ring offset every draw BY CONSTRUCTION.
	DrawMerge,          // KYTY_DRAW_MERGE,         file name "drawmerge"
	// Recomputes the equality verdict by memcmp over the live prefix of each shadow array and
	// counts disagreements in dm_bad, which must read 0.  A CROSS-IMPLEMENTATION check and not
	// a value check: both halves read the same shadow table, and the previous draw's value
	// exists nowhere else - the limitation pred/02 of session 85 stated for sl_bad.
	DrawMergeVerify,    // KYTY_DRAW_MERGE_VERIFY,  file name "drawmergecheck"
	// Session 87, MEASUREMENT ONLY (ROADMAP.md route C and D3): which half of the 65.25 ns an
	// image slot costs in PrepareBindings is ResolveTextureWith and which is BindImage.  ONE
	// timestamp a slot, taken after the resolve on half the stages and after the bind on the
	// other half, so an interval that opens after a bind and closes after a resolve is exactly
	// one resolve; the per-stage phase alternates, so every slot index is sampled in half the
	// stages.  NOT a two-pass split: deferring BindImage past the next slot's resolve would
	// break the is_bound ordering contract that ConfigureImageSourceUnlocked
	// (textureCache.cpp:1226), ResolveOverlap, ResolveDepthOverlap and ExpandImage all read,
	// and FindImage can free an id the deferred BindImage would then index.  Nothing is
	// reordered and nothing is skipped: the mark's own cost rides in the sampled intervals AND
	// in the loop total, so it cancels in the difference.  Needs "bindlap" to arm.
	BindAlt,            // KYTY_BIND_ALT,           file name "bindalt"
	// Session 89, MEASUREMENT ONLY (ROADMAP.md route D2): the residue of AheadTake, 1 607 us
	// a frame and 65 % of da_take_us, which is the largest unsplit block in the record now
	// that session 88 has priced the two VerifyWitness comparison loops at 852.5 us.  This is
	// the "proglap" rolling mark chain applied ONE LEVEL DOWN, inside AheadTake, SEEDED from
	// the timestamp Cache::Get already takes for da_take_us at pipelineCache.cpp:3069 - so
	// the first mark is free, and the gate is read BEFORE that timestamp, outside the timer.
	// Six marks divide the call into the key build, the probe loop, prefetch pass A (the
	// eleven PrefetchVectorData of gate "daprefetch"), prefetch pass B (one
	// __builtin_prefetch a live run, inside VerifyWitness at :790-806, which NEITHER value
	// of knob "dawitloop" skips and which session 88 therefore did not measure), the two
	// comparison loops, and the take.  It changes no value and no decision; its own price is
	// the within-run difference of its two arms and is reported, never hidden.
	TakeLap,            // KYTY_TAKE_LAP,           file name "takelap"
	// Session 90, SELF-CHECK of knob "bufimp" (ROADMAP.md route D1).  Beside every region
	// the import resolved with TryGetBackingPointer, recompute it with
	// TryGetBackingPieces - a SECOND, independent walk of the same mapping table, with its
	// own loop - and accuse a disagreement.  TryGetBackingPointer answers only for a range
	// inside ONE mapping, so a second piece, a different backing offset or a short piece is
	// a contradiction between two implementations and not a race.  bi_bad must read 0.
	BufImportVerify,    // KYTY_BUF_IMPORT_VERIFY,  file name "bufimpcheck"
	// Session 92, MEASUREMENT ONLY: the split of stg_pool_ns, the 173.6 us/frame GuestGpu
	// pays to hand 40.33 upload regions to the copy pool (FACTS s91 section 5, "the new
	// lever").  Three marks - the backing resolve in CopyGuestToStaging, the pool queue
	// lock in CopyPool::Enqueue, the wake after it - plus three shape counters (regions
	// per upload, chunks per region, the pool queue depth sampled before the hand-over),
	// because the price per region FALLS with the regions in the frame and only the
	// division can say which part does that.  It changes no value and no decision, and
	// the session 91 timer stg_pool_ns is left whole as the total to check against.  At
	// 0 not one timestamp and not one Add of this session is taken.
	StageLap,           // KYTY_STAGE_LAP,          file name "stglap"
	// Session 93, MEASUREMENT ONLY (pred/01_bdacap.md): the ceiling of moving V# buffer
	// slots onto a buffer device address instead of a descriptor.  Every buffer slot
	// NativeStorageBuffer builds is classified into exactly one of five classes --
	// degenerate, formatted (texel), const-bank (uniform), stream-ring, and the candidate
	// population "a cached buffer with a stable handle" -- and the time the function
	// spends on the candidates is measured DIRECTLY, not as a rate times a population.
	// Nothing is converted: no value, no decision and no side effect depends on it, and
	// at 0 not one timestamp and not one Add of this session is taken.
	BdaCap,             // KYTY_BDA_CAP,            file name "bdacap"
	// Session 94, MEASUREMENT ONLY (pred/01_mergecost.md): what a draw that merges into its
	// predecessor would really save once the bc_ok V# slots are carried by a device address.
	// Every graphics commit gets a post-conversion signature (bc_ok buffer entries masked,
	// everything else kept) compared with the previous commit's, and the commit phases and
	// the draw's time before and after its class point are booked by the outcome.  It feeds
	// no value, no decision and no side effect; at 0 not one timestamp of it is taken.
	MergeCost,          // KYTY_MERGE_COST,         file name "mergecost"
	// Session 94, MEASUREMENT ONLY (pred/02_bdaall.md): PrepareBda on every draw and
	// dispatch that has a statically convertible buffer slot (not formatted, not const-bank,
	// not written, not atomic) -- exactly where moving those slots onto BDA would set
	// info.uses_dma.  No slot is converted and no shader changes; the contrast prices the
	// extra calls and their side effects, which include WHICH slots then take the stream
	// ring (PrepareBda clears the CPU-dirty ranges first).  Never to be shipped.
	BdaAll,             // KYTY_BDA_ALL,            file name "bdaall"
	// Session 95, MEASUREMENT ONLY (pred/01_framerep.md), route E measurement M2: the
	// frame-to-frame repetition of a draw's CONTENT.  The signature census of gate
	// "mergecost" is walked a second time into three canonical hashes (resources only,
	// + payload bytes, + draw arguments) and each is looked up in the multiset of the
	// previous three frames.  Feeds no value, no decision and no side effect; it only
	// answers whether a replay COULD exist.  Requires mergecost=1 in the same arm for
	// the per-draw brackets.  Never to be shipped.
	FrameRep,           // KYTY_FRAME_REP,          file name "framerep"
	// Session 96, measurement only (pred/01_pathlap.md): the two splits ROADMAP.md:1051-1052
	// names as part of M3 - the time the GuestGpu thread spends OUTSIDE the render mutex
	// (4.05 ms, never split) and mh_emit beyond CommitBindings (~5 ms, never split).  The
	// chain already exists in renderDraw.cpp as a FrameStats::Lap and reads identically zero
	// in every lite run, because Lap times under TimingsEnabled().  This gate re-takes it with
	// PathLap, which times under Enabled().  Feeds no value, no decision and no side effect.
	// Never to be shipped: it is pure instrument price.
	PathLap,            // KYTY_PATH_LAP,           file name "pathlap"
	// Session 96, MEASUREMENT ONLY (ROADMAP.md:1048-1053), route E measurement M3: the
	// CEILING STUB.  It REMOVES AheadTake, MaterializeResources, PrepareBindings,
	// RebindBuffers / RebindImages and the per-slot synchronisations, and binds stubs (the
	// null buffer, the null images, one sampler, a zero shader_data) while KEEPING the whole
	// emit half - the descriptor writes, the set commit, the push constants, BeginRendering,
	// the dynamic state, EmitDrawPrimitives and the gate "recpack" record path.  THE PICTURE
	// IS ALLOWED TO BREAK: that is sealed at ROADMAP.md:1048 and is the only reason this may
	// exist.  It binds WRONG data by construction and can NEVER be shipped.
	// LAST row, matching the LAST enum entry before Gate::Count.
	BindFloor,          // KYTY_BIND_FLOOR,         file name "bindfloor"
	// Session 100, MEASUREMENT ONLY (pred/02_moved_mark.md): the moved-mark form of the
	// session-85 gate "bindlap".  Both phases pay exactly two timestamps and four Adds a
	// stage; phase 0 closes after the image loop and phase 1 after the shader_data copy,
	// so the price of the mark CANCELS in span1 - span0 instead of having to be estimated.
	// It binds nothing, reads no resource and changes no descriptor.  Use it with
	// "bindlap" OFF: bindlap's own marks sit inside span 1 and outside span 0.
	// LAST row, matching the LAST enum entry before Gate::Count.
	BindLapMove,        // KYTY_BIND_LAP_MOVE,      file name "blmove"
	// Session 101, MEASUREMENT ONLY (pred/01_two_directional.md): the moved-mark census of
	// CommitBindings.  Two phases a stage and two a commit, each paying exactly two
	// timestamps and four Adds at different program points, so the price of the mark
	// cancels in the difference.  It measures the SUBTRACTIVE half of the corrected M3
	// rule - the write build and the emit, which the floor keeps and a rewrite deletes.
	// It binds nothing, reads no resource and changes no descriptor.  Use it with
	// "bindlap", "drawstat" and "mergecost" OFF: those arm cb_timed, whose own four
	// timestamps a commit sit inside these spans.
	// LAST row, matching the LAST enum entry before Gate::Count.
	CommitLapMove,      // KYTY_COMMIT_LAP_MOVE,    file name "cbmove"
	Count,
};

// Numeric settings with the same life cycle as the gates ("name=<decimal>" in the gate file).
enum class Knob : uint32_t {
	DrawAheadThreads, // KYTY_DRAW_AHEAD_THREADS, file name "dathreads"
	RecordArenaMb,    // KYTY_RECORD_ARENA_MB,    file name "recarena"
	DescriptorSetBatch, // KYTY_DESCRIPTOR_BATCH,  file name "dsbatch"
	DescriptorPoolSets, // KYTY_DESCRIPTOR_POOL,   file name "dspool"
	RecordSpinUs,       // KYTY_RECORD_SPIN_US,    file name "recspin" (record thread poll, us)
	// Session 82: mode 3 added. 0 = off, 1 = the largest L3 group, 2 = the GuestGpu thread's L3
	// group, 3 = one logical processor per physical core of the largest L3 group - the portable form
	// of the raw mask 21845 that sessions 79 and 81 measured three times at -732.5 us
	// [-798.5, -666.4] of frame time. Anything else is still a raw mask, so 3 is no longer one.
	DrawAheadPin,       // KYTY_DRAW_AHEAD_PIN,    file name "dapin" (0 off, 1/2/3 modes, else mask)
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
	// Session 76, W3: the per-vector byte cap of PrefetchVectorData. SHIPPED ON 1024; the 192 that
	// shipped before it is kept as a second compile-time path so the A/B can be re-run. The cap let
	// 58.8 % of the offered bytes through at 192 and lets 94.4 % through at 1024; 4096 releases
	// essentially all of them and does not pay. Read ONCE PER TAKE, never per vector.
	PrefetchCapBytes, // KYTY_PREFETCH_CAP_B,   file name "pfcap" (bytes; default 1024, limit 4096)
	// Session 83, MEASUREMENT ONLY - it changes no value and no decision.  A BITMASK of the
	// phases of the render-mutex hold that get a MutScope of their own, so that a_mut_us stops
	// being built from six sites that leave mh_rt_us (806 us), mh_prog_us (5 831 us),
	// mh_disp_us (2 419 us) and PrepareBda (2 181 us) outside it.  1 = PrepareDrawRenderState,
	// 2 = RefreshShaders, 4 = the dispatch critical section, 8 = PrepareBda.  The scopes nest
	// with the existing six, so the total stays the UNION of the intervals - which is what the
	// serial floor S is - and the inner ones stop paying for their own clock reads.
	// The instrument is NOT free (amut alone costs 0.949-0.979 ms a frame, +958.4 us of it
	// inside mh_bind_us), so any floor quoted from it must come from an ABBA on this knob.
	MutWide,          // KYTY_MUT_WIDE,           file name "mutwide" (bitmask, 0 = today)
	// Session 88, MEASUREMENT ONLY (ROADMAP.md route C): the witness share of the 54.75 ns
	// ResolveTextureWith session 87 measured but could not divide.  ONE timestamp a slot in the
	// image loop of PrepareBindings, with a per-stage phase that alternates, exactly as
	// "bindalt" - but the mark MOVES rather than being added: at 1 it is taken after the
	// resolve returns, at 2 it is taken INSIDE the resolve, at the point the memo-hit decision
	// is complete (descriptors.cpp, immediately before ConfigureImageSource).  Both values pay
	// exactly one timestamp a slot, so the price of the mark cancels EXACTLY in the difference
	// of the two arms and never has to be estimated.  That difference is the part of a memo-hit
	// resolve which runs AFTER the proof that the earlier resolution is still valid, i.e. the
	// most a per-stage amortisation of a duplicate image slot could ever remove.  The mark at 2
	// can only be taken on the memo-hit path, so slots that miss it are accumulated separately
	// and are identical code in both arms - a null control.  Needs "bindlap" to arm.
	BindWitness,      // KYTY_BIND_WIT,           file name "bindwit" (0 off, 1 mark after the resolve, 2 mark at the memo-hit decision)
	// Session 90, ROADMAP.md route D1 - the largest untouched ceiling in the record, and
	// the only block this programme has opened since session 85 that is neither a proof
	// nor a shipped default.  BufferCache::UploadCopies copies the guest bytes of every
	// dirty range into the staging ring by hand and then has the GPU copy the ring into
	// the buffer: sync_up_kb = 22 803.8 KiB a frame over sync_ups = 75.8 uploads, and
	// bda_up_us (gate "bdasplit") = 2 118.3 us a frame - both read off blp85a, both on
	// disk since session 85.  The IMAGE path has not paid that memcpy since session 28:
	// it resolves the guest range into the VK_EXT_external_memory_host alias of the
	// backing store (HostImport) and lets the GPU read the guest pages.  This knob does
	// the same for a buffer upload, per copy region: TryGetBackingPointer gives the
	// backing offset, HostImport::Resolve gives the imported chunk buffer, and
	// RecordBufferCopies issues the copies from there.  The DESTINATION does not change -
	// same device-local Buffer, same handle, same device address, same descriptor -
	// because the imported chunks carry only eTransferSrc | eStorageBuffer and no device
	// address (hostImport.cpp) and can never be anything but a copy source.
	// THE HAZARD IS THE ONE THE IMAGE PATH ALREADY CLOSES, and it is why this ships at 0:
	// the GPU now reads the guest pages when the command buffer EXECUTES, not when
	// UploadCopies returns, so a CPU write into an imported range has to wait for that
	// read.  NotePendingHostRead publishes the range and RenderContext::HandleFault waits
	// on it for ANY guest range, images and buffers alike (renderContext.cpp:154-160).
	// Buffers are re-written by the CPU every frame BY DEFINITION - that is why they are
	// in the dirty ranges at all - and this scene already takes 1 265 write faults a
	// frame, so the cost of that wait is the open question the run answers.
	// hostread_waits and hostread_wait_us are printed already and are the diagnostic.
	// 0 = today.  1 = resolve and count, still copy (prices the resolution alone).
	// 2 = take the import.  An upload is taken only when EVERY region resolves.
	BufImport,        // KYTY_BUF_IMPORT,         file name "bufimp" (0 off, 1 census, 2 import)
	// Session 96, measurement only: add a PrepareBda at a COARSE granularity, to price the
	// "+0,5 ms (synchronisation)" term the M3 rule assumes (ROADMAP.md:1052-1053) instead of
	// assuming it.  ADDITIVE: it never removes the calls the code already makes, so arm 0 is
	// today's binary exactly.  0 = today; 1 = plus one call per submission (~8 a frame,
	// judge.md:116, count from judge.md:95); 2 = plus one call per label write (~420 a frame,
	// gpu-driven.md:136).  Session 94 measured the per-DRAW version (gate bdaall) at
	// +10 807.8 us a frame in the OLD regime -- ALWAYS report the regime with the number.
	BdaEvery,         // KYTY_BDA_EVERY,          file name "bdaevery" (0 today, 1 submit, 2 label)
	// Session 92: the wake of the copy pool.  A valid ABBA split stg_pool_ns, the
	// 185.0 us/frame GuestGpu pays to hand 40.6 upload regions to the pool, into
	// stg_res_ns 1.18 %, stg_lock_ns 3.13 % and stg_wake_ns 93.80 % - 4.27 us a region
	// in notify_one / notify_all alone.  That is the price of bringing a SLEEPING
	// thread back through the kernel: a notify with no waiter is tens of nanoseconds.
	// The pool really is asleep (stg_q / stg_pool_n = 0.430) and 28.8 % of the regions
	// are multi-chunk (stg_chunks / stg_pool_n = 1.2884) and take notify_all, which
	// wakes ALL 2-7 workers for what is at most chunks jobs.
	//   0 = today.  notify_all on a multi-chunk enqueue; a worker whose queue ran dry
	//       goes straight back to m_wake.wait.
	//   1 = no thundering herd: at most one notify_one per chunk, capped by the worker
	//       count.  It cannot lose work - ANY single woken worker drains the whole
	//       FIFO - so the count decides parallelism, never whether the queue is served.
	//   2 = 1 plus a bounded worker spin (parallelCopy.cpp WORKER_SPIN_NS, 20 us)
	//       before the worker returns to m_wake.wait, so the next notify finds it
	//       awake.  It is a LATENCY optimisation only: the spin never decides to
	//       sleep, and the only sleep decision stays the wait predicate under the
	//       queue mutex.  It burns worker cores, and stg_spin_ns is that price.
	// READ AT EVERY DECISION - on each enqueue and on each drain of a worker - so that it
	// CAN be a schedule arm, which is the only A/B this programme accepts (between-run
	// comparisons of cpu/draw are closed, ROADMAP.md section 3).  A mid-run flip is safe
	// because neither half owns state: the notify branch is chosen per enqueue, and a
	// worker that stops spinning merely reaches the wait sooner.  The read is one inline
	// relaxed atomic load against a notify that costs 4.27 us.
	CopyWake,         // KYTY_COPY_WAKE,          file name "copywake" (0 off, 1 no herd, 2 + spin)
	// Session 96, measurement only, read ONLY while gate "bindfloor" is on: how much of the
	// floor is taken.  1 (and 0) = the full stub; 2 = BINDINGS ONLY, that is AheadTake and
	// MaterializeResources stay and only the binding half is stubbed (the spare arm for the
	// fork in the sealed rule, rewrite94/gpu-driven.md:141); 3 = 1 plus the calibrated idle.
	BindFloorMode,    // KYTY_BIND_FLOOR_MODE,    file name "bfmode" (1 full, 2 bindings + optional burn, 3 full + burn)
	// Session 96/99, measurement only, read at bfmode=2/3: microseconds the translation
	// thread busy-waits per frame, spread over that frame's draws and dispatches, so the
	// floor arm keeps arm A's frame length and the DRS step cannot move between the arms
	// (ROADMAP.md:1062-1065).  bf_burn_ns reports what was really burned.
	BindFloorBurn,    // KYTY_BIND_FLOOR_BURN,    file name "bfburn" (us a frame, 0 = none)
	// Session 102: draw-lookahead requests per PipelineCache::QueueDrawAhead call (graphicsRun.cpp,
	// WalkComputeDispatches).  64 = the constant it replaces, 0 = one call at the end of the walk.
	// Read ONCE PER WALK, so a schedule flip cannot give one walk two batch sizes and it CAN be a
	// schedule arm.  Proof it armed: the counter da_qcall (QueueDrawAhead calls).
	DrawAheadBatch,   // KYTY_DRAW_AHEAD_BATCH,   file name "dabatch" (requests per queue call, 0 = whole walk)
	// Session 105, route A M3.1 (docs/session-105/designA3_stage3.md section 2): where the
	// ownership tick of a descriptor set (DescriptorHeap::Commit) and of the mergecost census
	// comes from.  0 = the render scheduler's CurrentTick(), the old expression; 1 = the tick the
	// command buffer was begun with (CommandBuffer::Tick); 2 = 1 plus the identity checks
	// ctx_chk_n / ctx_chk_bad and the counters ctx_midsub / ctx_rec_block; 3 = 2 plus EXIT on a
	// mismatch.  At N = 1 the two sources are equal by construction, so a flip between two reads
	// is harmless.  Read at every use.
	CtxTick,          // KYTY_CTX_TICK,           file name "ctxtick" (0 old, 1 buffer, 2 + check, 3 + exit)
	// Session 107: the compute-prefetch memo of PipelineCache::PrefetchComputePipeline (the
	// dawalk walker's second hold of PipelineCache::m_mutex).  0 = off; 1 = SHADOW (the key is
	// built and looked up, nothing is skipped: cspm_look / cspm_would); 2 = SKIP (a hit returns
	// before the lock and before ProgramCache::Get); 3 = skip-and-verify (a hit still runs the
	// locked path and compares the program id: cspm_bad, "CspMemoVerify:").  The memo is only a
	// hint - the dispatch always runs its own Get / GetComputePipeline - so a stale entry costs a
	// missed prefetch, never a wrong result.  Read once per prefetch call.
	CsPrefetchMemo,   // KYTY_CS_PREFETCH_MEMO,   file name "cspmemo" (0 off, 1 shadow, 2 skip, 3 skip + verify)
	// Session 108: skip PipelineCache::PrefetchComputePipeline per shader FAMILY (code hash and base plus
	// the stage static key, no user SGPRs) once the family's last K locked prefetches all found a built
	// pipeline and neither the programs epoch nor the shader registrations moved.  Session 109 (v2): nor
	// the count of compute-pipeline creations anywhere (any creation clears every streak).  0 = off; K = the
	// streak.  A new permutation of a skipped family is then compiled on the dispatch - counted by
	// cs_sync_new, the guard of every run.  Read once per prefetch call.
	// LAST row, matching the LAST entry of KNOB_DEFINITIONS.
	CsPrefetchFamily, // KYTY_CS_PREFETCH_FAMILY, file name "cspfam" (0 off, K = streak before skipping)
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
