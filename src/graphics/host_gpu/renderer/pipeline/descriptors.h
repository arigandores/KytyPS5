#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_

#include "common/assert.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/image/image.h"
#include "graphics/host_gpu/vulkanCommon.h"
#include "graphics/shader/recompiler/ir/ShaderIR.h"
#include "graphics/shader/shaderBindings.h"

#include <cstdint>
#include <cstring>
#include <type_traits>
#include <vector>

namespace Libs::Graphics {

struct ShaderStageRuntime;

struct TextureBinding {
	TextureBinding() = default;
	// Session 57, B2a: PrepareBindings builds the binding in its vector element (one ImageDesc copy).
	TextureBinding(ImageId id, const TextureCache::ImageDesc& binding_desc, uint32_t index,
	               uint32_t version)
	    : image_id(id), desc(binding_desc), memo_index(index), memo_version(version) {}

	ImageId                    image_id;
	vk::ImageView              image_view = nullptr;
	TextureCache::ImageDesc    desc;
	vk::ImageLayout            layout = vk::ImageLayout::eUndefined;
	std::vector<vk::ImageView> mip_views;
	// RenderExecutorMemo::textures slot this binding was resolved from, and that slot's version
	// then (UINT32_MAX: none). RebindImages (gate "texfast") reuses the slot's view.
	uint32_t                   memo_index   = UINT32_MAX;
	uint32_t                   memo_version = 0;
};

// Session 93, gate "bdacap" (MEASUREMENT ONLY, pred/01_bdacap.md): the class
// NativeStorageBuffer gave a buffer slot.  Exactly one per slot, first match wins in the
// order below.  Written only while the gate is armed, so every slot of an unarmed run
// stays None; it feeds no value, no decision and no side effect.
enum class BdaCapClass : uint8_t {
	None      = 0,
	Null      = 1,
	Formatted = 2,
	ConstBank = 3,
	Ring      = 4,
	Ok        = 5,
};

// Session 94, gates "bdaall" and "mergecost" (MEASUREMENT ONLY): a buffer slot a shader
// could read through a device address instead of a descriptor -- not a texel view, not a
// const-bank uniform view, and never written or atomic (the backend has no BDA store path:
// SpirvEmitter rejects writable FLAT/GLOBAL addresses).  A static property of the resource.
[[nodiscard]] inline bool BdaConvertible(const ShaderRecompiler::IR::BufferResource& res) {
	return !res.formatted && !ShaderRecompiler::IR::PackedStrideConstBank(res.packed_stride) &&
	       !res.written && !res.atomic;
}

template <typename Info>
[[nodiscard]] inline bool BdaAllCandidate(const Info& info) {
	for (const auto& res: info.buffers) {
		if (BdaConvertible(res)) {
			return true;
		}
	}
	return false;
}

struct PreparedBindings {
	struct BufferSource {
		uint64_t address = 0;
		uint64_t size    = 0;
		BufferId id;
	};

	// The draw owns the immutable compiled-program/runtime-snapshot association through commit.
	const ShaderStageRuntime* runtime = nullptr;
	// Keep the resolved guest range through cache preparation; only the host buffer ID may
	// become stale and need resolving again when bindings are rebound.
	std::vector<BufferSource>             buffer_sources;
	std::vector<vk::DescriptorBufferInfo> buffers;
	// Session 93, gate "bdacap" (MEASUREMENT ONLY): buffer_class[i] is the BdaCapClass of
	// buffers[i], pushed beside it by RebindBuffers and read by the dm_buf1_ok census in
	// renderDraw.cpp.  Parallel to buffers by construction (one push_back each, same loop).
	// All None unless the gate is armed.
	std::vector<uint8_t>                  buffer_class;
	std::vector<TextureBinding>           images;
	std::vector<vk::Sampler>              samplers;
	vk::DescriptorBufferInfo              gds {nullptr, 0, VK_WHOLE_SIZE};
	vk::DescriptorBufferInfo              flattened_srt;
	vk::DescriptorBufferInfo              shader_data_buffer;
	std::vector<uint32_t>                 shader_data;
	// Session 82, gate "bindkey" (measurement only): the hash of this stage's binding inputs and
	// whether it equalled the previous draw's.  Both are zero/false unless the gate is on.
	uint64_t                              key     = 0;
	bool                                  key_hit = false;
	// Session 95, gate "framerep" (measurement only): hashes of the payload BYTES this
	// stage uploads into the stream ring, taken where the span is already in hand.  Both
	// stay 0 unless the gate is on, and neither is read by anything but the census.
	uint64_t                              srt_hash  = 0;
	uint64_t                              data_hash = 0;
	// Session 83, gate "bindpack" (PLAN_82_bind.md item 4): which of the three binding kinds
	// the three FindBinding scans of a stage ask about are present in program.bindings, with
	// bit 3 set to mark the mask computed. Written by PrepareBindings, read by FindBuffers,
	// which already takes the same PreparedBindings. Recomputed for every stage of every draw:
	// it is not a cache and has no invalidation source.
	uint32_t                              kind_mask = 0;
	// Session 97, gate "bindfloor": true when BindFloorPrepareStage filled this stage, false
	// when PrepareBindings did (Reset clears it).  CommitBindings takes its floor branch from
	// THIS and never from a second read of the gate: the gate flips on the presentation
	// thread, and bf96b died on a falling edge that landed between two reads of one draw -
	// prepared by the floor, committed by the real path over an emptied `images`.
	bool                                  floor     = false;

	void Reset() {
		// Capacity belongs to the executor; every descriptor belongs to this draw only.
		runtime = nullptr;
		buffer_sources.clear();
		buffers.clear();
		buffer_class.clear();
		images.clear();
		samplers.clear();
		shader_data.clear();
		gds = {nullptr, 0, VK_WHOLE_SIZE};
		flattened_srt = {};
		shader_data_buffer = {};
		key       = 0;
		key_hit   = false;
		kind_mask = 0;
		srt_hash  = 0;
		data_hash = 0;
		floor     = false;
	}
};

[[nodiscard]] vk::DescriptorType
NativeDescriptorType(ShaderRecompiler::IR::DescriptorBindingKind kind);
[[nodiscard]] uint32_t
NativeDescriptorCount(const ShaderRecompiler::IR::DescriptorBinding& binding);
[[nodiscard]] vk::DescriptorImageInfo MakeImageInfo(const TextureBinding& texture,
                                                    uint32_t              element = 0);

// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053), route E measurement
// M3, the ceiling stub.  BindFloorStageSupported: whether the floor can express this stage's
// image resources as null images - NullTextureDesc aborts the process on a numeric class it
// does not know, and on the floor EVERY image slot goes through it, so the draw is screened
// first and counted bf_skip when it is not expressible.  BindFloorPrepareStage: the whole of
// what the floor puts into a PreparedBindings - the runtime pointer (CommitBindings reads the
// binding SHAPE out of it) and a zero shader_data of exactly the declared length, so the
// EXIT_IF on that length still holds.  Every other field stays empty on purpose.
[[nodiscard]] bool BindFloorStageSupported(const ShaderStageRuntime& runtime);
void BindFloorPrepareStage(const ShaderStageRuntime& runtime, PreparedBindings& prepared);

// Session 97, gate "bindfloor": the floor decision LATCHED once per op.  Gates are applied on
// the presentation thread (gates.cpp PollSchedule -> ApplyText), so any site that reads the
// gate itself can disagree with another site of the SAME draw.  BindFloorLatchOp is called
// once at the top of DrawIndex, DrawAuto and DispatchDirect, before anything reads it;
// every floor site of that op (ProgramCache::Get, ExecutePreparedDraw, DispatchDirect,
// BindFloorBurnSlice, the texture GC keep-alive) reads BindFloorCurrentOp on the same thread.
// BindFloorEverArmed: sticky, true once any op of this process latched the floor.
struct BindFloorOp {
	bool     armed = false; // gate "bindfloor" as this op latched it
	uint32_t mode  = 0;     // knob "bfmode" as this op latched it
	// Session 98: the op's GDS-trigger key (KYTY_BIND_FLOOR_LATCH=2 only, 0 otherwise).
	uint64_t key = 0;
};
// The auxiliary latch (compute prefetch; the GCs in mode 0).  Never counted in bf_mixed.
BindFloorOp                      BindFloorLatchOp();
[[nodiscard]] const BindFloorOp& BindFloorCurrentOp();
[[nodiscard]] bool               BindFloorEverArmed();

// Session 98 (patch_s98a, MEASUREMENT ONLY; C:/kyty/s98/design98/SPEC_patch98.md Part L).  Two
// environment variables read ONCE per process, identical in both arms of any schedule:
//   KYTY_BIND_FLOOR_LATCH  0 (default) = the session-97 per-op latch above, unchanged;
//                          1 = FRAME latch: the live gate is read ONLY at the GPU flip packets
//                              processed on GuestGpu; a changed value becomes `pending` and is
//                              taken by every op of a submission enqueued after the flip-bearing
//                              DCB (and by that DCB's own ops after its flip packet); it becomes
//                              the `base` once every older submission has completed;
//                          2 = GDS TRIGGER test: rising edges per op as in mode 0, a FALLING edge
//                              is held (ops stay floored) until the first draw/dispatch whose
//                              shader key is a learned real GDS consumer, or two flip packets.
//   KYTY_BIND_FLOOR_CLEAR  1 = a floored dispatch never takes the compute clear shortcuts.
[[nodiscard]] uint32_t BindFloorLatchMode();
[[nodiscard]] uint32_t BindFloorClearMode();
// The op-site latches (draw / dispatch), counted in bf_mixed.  The shader addresses are hashed
// into the GDS-trigger key only in mode 2.
BindFloorOp BindFloorLatchDraw(uint64_t vs_addr, uint64_t ps_addr);
BindFloorOp BindFloorLatchDispatch(uint64_t cs_addr);
// GC keep-alive: mode 0 = BindFloorLatchOp().armed (unchanged); modes 1/2 a NON-adopting read.
[[nodiscard]] bool BindFloorGcHold();
// Session 99 audit only: read current submission's counted sticky armed value, without
// adopting/reading a live gate. Independent subset of GcHold; base/pending are NOT witnessed.
[[nodiscard]] bool BindFloorGcAuditSticky();
// Download-ring skip: mode 0 = live gate || sticky; modes 1/2 = latched op || sticky.
[[nodiscard]] bool BindFloorDownloadSkip();
// KYTY_BIND_FLOOR_CLEAR=1 and the current op latched armed with bfmode != 2 (Session 98,
// patch_s98d: bfmode=2 does not freeze the snapshot, its clears are real work).  Also drops an
// armed op the floor cannot express (bf_skip -> bf_skip_drop).
[[nodiscard]] bool BindFloorClearSkip();
// CommitBindings' real GDS-barrier branch: mode 2 learns the current op's key.
void BindFloorNoteGdsBarrier();
// Per-submission latch state, owned by GuestGpu's Submission; the slice being processed is
// published to the latch through a thread-local pointer (BindFloorSetSlice) for the length of
// GuestGpu::Process.  seq: monotonic over ALL 57 queues, assigned at Enqueue under m_queue_mutex.
struct BindFloorSlice {
	uint64_t seq        = 0;
	uint32_t queue      = 0;     // 0 = graphics DCB, 1..56 = async compute
	uint32_t ops        = 0;     // op-site latches taken so far
	bool     after_flip = false; // a flip packet of this submission has been processed
	uint8_t  bits_pre   = 0;     // bf_mixed accumulators: 1 = armed seen, 2 = unarmed seen,
	uint8_t  bits_post  = 0;     // before / after this submission's flip packet
	// Session 98 (patch_s98d), KYTY_BIND_FLOOR_LATCH=1: the value is STICKY per submission - the
	// first op-site latch before (after) this submission's flip packet fixes it (packed
	// {armed, bfmode}); every later op-site latch of that part reuses it, resumed slices too.
	bool     sticky_pre_set  = false;
	bool     sticky_post_set = false;
	uint64_t sticky_pre      = 0;
	uint64_t sticky_post     = 0;
	// Session 98 (patch_s98e): this submission holds an armed sticky value and is counted in the
	// global sticky-armed count until it completes (BindFloorSliceComplete) - the GC keep-alive.
	bool     sticky_armed_counted = false;
};
// What GuestGpu knows about its queues at a flip packet (mode 1 only).
struct BindFloorFlipQueues {
	bool     older_in_flight = false; // a submission with seq < s_flip is not complete
	uint32_t xover           = 0;     // seq > s_flip and already ran ops, all queues
	uint32_t xover_acb       = 0;     // ... of them on queues 1..56
};
void                   BindFloorSetSlice(BindFloorSlice* slice);
[[nodiscard]] uint64_t BindFloorSliceSeq();
void                   BindFloorSliceComplete(const BindFloorSlice& slice);
[[nodiscard]] uint64_t BindFloorFlipEpoch();
// Returns true when this flip packet opened a pending change (mode 1).  Session 98 (patch_s98d):
// mode 1 EXITs when the packet is processed on a thread without a GuestGpu slice (m4baton relay).
bool                   BindFloorNoteFlipPacket(const BindFloorFlipQueues* queues);
[[nodiscard]] bool     BindFloorPendingValid();
void                   BindFloorResolve(uint64_t min_front_seq);

template <typename T>
[[nodiscard]] T DecodeNativeDescriptor(const ShaderRecompiler::IR::DescriptorValue& value) {
	static_assert(std::is_trivially_copyable_v<T>);
	static_assert(sizeof(T) % sizeof(uint32_t) == 0);
	T result {};
	EXIT_IF(value.dword_count < sizeof(result) / sizeof(uint32_t));
	std::memcpy(&result, value.dwords.data(), sizeof(result));
	return result;
}

[[nodiscard]] bool IsSupportedDepthTextureEncoding(const ShaderTextureResource& descriptor,
                                                   bool r128 = false);
void ValidateStorageTexture(const ShaderRecompiler::IR::ImageResource& resource,
                            const ShaderTextureResource& descriptor, uint64_t size);

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DESCRIPTORS_H_
