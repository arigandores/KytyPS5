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
	RecordPin,      // KYTY_RECORD_PIN,          file name "recpin" (record thread follows "dapin")
	// Session 57, A1 (sticky pages).
	StickyStat,     // KYTY_STICKY_STAT,         file name "stkstat" (A1 ceiling counters only)
	// Session 57, E1/E2/E9 (draw statistics).
	DrawStat,       // KYTY_DRAW_STAT,           file name "drawstat" (E1/E2/E9 counters)
	DrawStatSlow,   // KYTY_DRAW_STAT_SLOW,      file name "dpslow" (E1 runs also cut by slow bits)
	// Session 57, A6/A7 and track B.
	DrawStateReuse, // KYTY_DRAW_STATE_REUSE,    file name "drawstate" (B1: per-thread draw state)
	SnapshotKeep,   // KYTY_SNAPSHOT_KEEP,       file name "snapkeep" (B4: kept snapshot storage)
	BufLru,         // KYTY_BUF_LRU,             file name "buflru"
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
	FaultWindowKb,      // KYTY_FAULT_WINDOW_KB,   file name "faultkb" (CPU write-fault window, KiB; 4 = one page)
	Count,
};

namespace Detail {

// Published once the environment was read (the first slow read), then by Poll. Until `g_ready`
// is set every read takes the slow path, so a read during static initialization still sees the
// environment.
inline constinit std::array<std::atomic<bool>, static_cast<size_t>(Gate::Count)>     g_gates {};
inline constinit std::array<std::atomic<uint32_t>, static_cast<size_t>(Knob::Count)> g_knobs {};
inline constinit std::atomic<bool>                                                   g_ready {false};

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

// Re-reads the gate file (if any) and publishes changes. Called once per flip.
void Poll(uint32_t frame) noexcept;

} // namespace Common::Gates

#endif // EMULATOR_SRC_COMMON_GATES_H_
