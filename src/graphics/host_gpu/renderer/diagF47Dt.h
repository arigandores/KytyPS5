#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF47DT_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF47DT_H_

// Track F, F47g (HPP-824, ROADMAP s122 item 740(v)(1)): KYTY_DIAG_F47DT - MEASUREMENT ONLY, default 0.
// F47g2 (HPP-828, ROADMAP s122 item 742(v)): RC1-RC5 of the review F47h.
//
// At =1, for every draw whose guest PS (CompiledShaderInfo::shader_hash) is in KYTY_DIAG_F47DT_PS (hex list, default
// 45942b26d9ffbe8e) and whose show q lies in KYTY_DIAG_F47DT_FRAMES=<a>-<b> (default: all), the log gets "F47dt:"
// lines keyed by (q, d):
//   q - the show the draw lands in: the number of flips queued by the GuestGpu parse so far (NoteFlip, taken on the
//       parse thread) + 1; the flip that closes the frame of the draw prints "F47dt: kind=flip q=<the same q>", and
//       the present thread prints "F47dt: kind=shown n=<flip_status.count> rid=<request>" when it processes that
//       request (n = the n of its "FrameTrace: n=" line). n - GpuTimeProfiler::Frame() when the draw is processed (the
//       n of the last FrameTrace line, kept as a separate field). d - the number of the draw among the draws of the
//       show q that reached the pipeline lookup.
//   kind=draw  - shader hashes, counts, the raw PS user data (a)
//   kind=img   - per PS image: raw T# words and the emulator's decoding, the Vulkan view bound to the draw (taken from
//                the cached view object of the image), XXH3-64 of the guest bytes of the image range now (value (i)),
//                the XXH3-64 of the bytes the texture cache uploaded last into THIS host image (record keyed by the
//                image id with its slot generation, sid=) with the show of that upload (source of value (ii)), and the
//                cache flags (b); no record of the image but one of another image of the same range -> sk=other_image
//   kind=buf   - per PS buffer: raw V#, XXH3-64 of the guest range now with the GPU-write flag of the range (ggpu=),
//                and of what the draw got: a copy in the stream ring (hashed when the CPU filled it; a range the GPU
//                copied into the ring - gvh=unmeasured:gpu_copy) (c)
//   kind=srt   - the flattened SRT words the draw got (c)
//   kind=reg   - raw guest context register words, last write before the draw (g)
//   kind=vk    - the Vulkan state the emulator built for the draw (pipeline key and dynamic state) (g)
// and the raw guest bytes of every (i) range go to _f47dt/<address>_<hash>.bin once per (address, hash), 2 GiB in
// total (then one "F47dt: capped" line and lines only) (d). At exit: "F47dtStat: when=exit ..." (e).
//
// At =0 (unset, "", 0/false/off/no) every entry point returns at the first test of On() (one getenv per process);
// nothing is recorded, no line, no file.  At =1 the hooks only read and write their own state: no order, no
// synchronisation, no cache state and no guest memory are changed (no Touch, no wait, no readback).

#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace Libs::Graphics {
class CommandBuffer;
class RenderContext;
struct PipelineStaticParameters;
struct PipelineRenderingState;
struct PreparedBindings;
struct RenderColorInfo;
struct RenderDepthInfo;
struct ShaderStageRuntime;
} // namespace Libs::Graphics

namespace Libs::Graphics::DiagF47Dt {

// KYTY_DIAG_F47DT, read once per process.  The first call at =1 prints "F47dt: mode=1 ...".
[[nodiscard]] bool On();

// --- guest context register words (g) ---------------------------------------------------------------------------
// path: 0 = SET_CONTEXT_REG (direct), 1 = SET_CONTEXT_REG with indirect handlers, 2 = SET_CONTEXT_REG_INDIRECT.
void NoteCtxWrite(const void* ctx, uint32_t offset, const uint32_t* values, uint32_t count, uint32_t path);
enum class CtxOp : uint32_t { Clear = 0, Push = 1, Pop = 2, PushClear = 3, Reset = 4 };
void NoteCtxOp(const void* ctx, const void* saved, CtxOp op);

// --- flips (F47g2, RC1) ----------------------------------------------------------------------------------------------
// Called by CommandProcessor on the GuestGpu parse thread for every flip it queues, after the request id is known.
// path: 0 = Flip(), 1 = Flip(addr, value), 2 = FlipWithInterrupt, 3 = PrepareCpuFlip.  Prints "F47dt: kind=flip q=".
void NoteFlip(uint32_t path, uint64_t request_id);
// Called by the present thread right after flip_status.count++ of the request request_id ("F47dt: kind=shown").
void NoteShown(uint64_t count, uint64_t request_id);

// --- texture cache uploads (source of value (ii)) -----------------------------------------------------------------
enum class SrcKind : uint32_t { None = 0, Owner = 1, Gpu = 2, Import = 3, Staging = 4, StagingAsync = 5 };
using RingGeneration = uint64_t (*)(const void* ring);
// Called by BufferCache::ObtainBufferForImage on the branch it returns from (thread-local note).  bytes: the host
// bytes the upload reads (staging copy) or nullptr; ring / ring_gen / generation: the staging ring of a pooled copy.
void NoteImageSource(SrcKind kind, uint64_t vaddr, uint64_t size, const uint8_t* bytes, const void* ring,
                     RingGeneration ring_gen, uint64_t generation);
// Called by TextureCache right after UploadImage: binds the thread-local note to the image (index and slot
// generation of its ImageId) and its range.
void NoteImageUpload(uint32_t image_index, uint32_t image_generation, uint64_t address, uint64_t size,
                     uint32_t first_level, uint32_t level_count, uint32_t pending_levels, bool pending_completion);

// --- the stream ring (F47g2, RC3) ----------------------------------------------------------------------------------
// Called by NativeStorageBuffer right after the copy ON THE GPU into the stream ring (the const-bank branch "gpu"):
// [offset, offset + size) of the ring in its wrap generation holds bytes the GPU writes after the submit.
void NoteRingGpuCopy(const void* ring, uint64_t offset, uint64_t size, uint64_t generation);

// --- the draw ------------------------------------------------------------------------------------------------------
// Called by ProgramCache::Get for the pixel stage with the resource plan of the program (nullptr: not known yet),
// the program address and the user data the materialization reads (thread-local copy for the next OnDraw).
void NotePsRuntime(const void* resource_plan, uint64_t shader_base, const uint32_t* user_data, size_t count);
// Called by PipelineCache::CreateGraphicsPipelineLocked with the finished key (thread-local copy).
void NoteGraphicsKey(const PipelineStaticParameters& params, const PipelineRenderingState& rendering);

struct DrawArgs {
	uint64_t                  submit_id      = 0;
	const char*               draw_name      = "";
	uint32_t                  index_count    = 0;
	uint32_t                  instance_count = 0;
	int                       guest_frame    = 0; // GuestGpu::GetFrameNum()
	const ShaderStageRuntime* vs             = nullptr;
	const ShaderStageRuntime* ps             = nullptr; // nullptr: no PS
	const PreparedBindings*   pixel          = nullptr;
	const RenderColorInfo*    colors         = nullptr;
	uint32_t                  color_count    = 0;
	const RenderDepthInfo*    depth          = nullptr; // the depth state the draw records (dynamic)
	bool                      pipeline_ready = false; // false: the draw is skipped (async pipeline)
};
// Called by RenderExecutor::ExecutePreparedDraw right after GetGraphicsPipeline (both outcomes).
void OnDraw(RenderContext& context, const CommandBuffer& buffer, const DrawArgs& args);

void PrintExitStat();

// --- the stand (tests/F47DtStand.cpp) ------------------------------------------------------------------------------
// Reads [vaddr, vaddr + size) of guest memory without faulting: *ptr = a host pointer when the range is one mapping,
// else the bytes are copied into *copy. Returns false when the range has no backing.
using GuestReader = bool (*)(uint64_t vaddr, uint64_t size, std::vector<uint8_t>* copy, const uint8_t** ptr);
void SetGuestReaderForStand(GuestReader reader);
void SetFileCapForStand(uint64_t bytes);
void SetPresentForStand(uint32_t n);
// One "F47dt: kind=img" line of the image image_index (slot generation 1) bound to a range, without a draw (T# and
// view fields "-"): the same measurement code as OnDraw.
void StandImage(uint32_t slot, uint32_t image_index, uint64_t address, uint64_t size);
// One "F47dt: kind=reg" line of a context object (the same code as OnDraw).
void StandRegs(const void* ctx);
// One "F47dt: kind=ringstand" line: what OnDraw prints as gvh for [offset, offset + range) of a ring whose mapped bytes
// are mapped[0, mapped_size) in the wrap generation generation (the same code as OnDraw).
void StandRing(const void* ring, uint64_t generation, const uint8_t* mapped, uint64_t mapped_size, uint64_t offset,
               uint64_t range);

} // namespace Libs::Graphics::DiagF47Dt

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_DIAGF47DT_H_
