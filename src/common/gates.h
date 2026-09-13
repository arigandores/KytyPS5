#ifndef EMULATOR_SRC_COMMON_GATES_H_
#define EMULATOR_SRC_COMMON_GATES_H_

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
	RecordThread,   // KYTY_RECORD_THREAD,       file name "recordthread"
	TrackLockFree,  // KYTY_TRACK_LOCKFREE,      file name "trackfree"
	TrackLockFreeVerify, // KYTY_TRACK_LOCKFREE_VERIFY, file name "tfcheck"
	ProtectFast,    // KYTY_PROTECT_FAST,        file name "protfast"
	ShaderWriteLocal, // KYTY_SHADER_WRITE_LOCAL, file name "swlocal"
	GdsEpoch,       // KYTY_GDS_EPOCH,           file name "gdsepoch"
	AtomicImageBarrier, // KYTY_ATOMIC_IMAGE_NO_BARRIER, file name "atomimg"
	Count,
};

// Numeric settings with the same life cycle as the gates ("name=<decimal>" in the gate file).
enum class Knob : uint32_t {
	DrawAheadThreads, // KYTY_DRAW_AHEAD_THREADS, file name "dathreads"
	RecordArenaMb,    // KYTY_RECORD_ARENA_MB,    file name "recarena"
	DescriptorSetBatch, // KYTY_DESCRIPTOR_BATCH,  file name "dsbatch"
	DescriptorPoolSets, // KYTY_DESCRIPTOR_POOL,   file name "dspool"
	Count,
};

// Relaxed read of the current state. Safe to call from any thread and from hot paths.
[[nodiscard]] bool Enabled(Gate gate) noexcept;

// Relaxed read of a knob's current value.
[[nodiscard]] uint32_t Value(Knob knob) noexcept;

// Re-reads the gate file (if any) and publishes changes. Called once per flip.
void Poll(uint32_t frame) noexcept;

} // namespace Common::Gates

#endif // EMULATOR_SRC_COMMON_GATES_H_
