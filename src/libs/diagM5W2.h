#pragma once

// Track M, M6a (HPP-848, ROADMAP s122 item 767(i)): KYTY_DIAG_M5W2 - MEASUREMENT ONLY (default 0, no decision of the
// emulator changes at any value). Counters of the wave 2 candidates of M5a / M5b, summed over the process and printed
// as "M5W2Stat:" every 4096 queued AudioOut2 pushes (when=periodic) and at both exits of Execute (when=exit):
//   T125 (libAudio2.cpp, audioout2_queue_context_audio): per queued push, every port of the context with PCM -
//     ao_obj_push / ao_obj_nz (object ports, (port_type & 0xff00) == 0x0100, and of them with >= 1 nonzero sample of
//     the grain), ao_bus_push / ao_bus_nz (the other ports - the live control of the scan), ao_obj_nopcm (object ports
//     without PCM, reference);
//   T313 + T179 (textureCache.cpp, ClearImageFromBuffer): clr_dw - colour DWORD fills accepted (ClearImage issued),
//     clr_dw_div - of them the forms where our clear differs from upstream 57c97ebd8 / 89792a3bc: R16 (R16_SFLOAT,
//     R16_UNORM) with lo != hi, RGBA16F / RGBA16_UNORM / RG32F with the word != 0; also per vk::Format ("M5W2Clr:");
//   T021 (imageView.cpp, FindView - a created view): minlod_views - views with min_lod > 0, minlod_div - of them
//     base_level > 0 and min_lod > (level_count - 1) * 256 (our clamp level_count - 1 differs from the absolute one);
//   T188 (textureCache.cpp, InvalidateMemoryFromGPU): inv_calls - calls with a valid range; inv_part - (call, colour
//     image) pairs where the image IsGpuModified and the write does not cover the image's range; inv_gpu - pairs with
//     IsGpuModified (reference); inv_off - inv_part whose write starts at an address other than the image's base
//     (the case upstream ebe401d05 skips, reference);
//   T258 (descriptors.cpp, NativeStorageBuffer before ObtainBuffer): raw_rd - bindings read neither written nor
//     formatted; raw_rd_gpu - of them FindImageFromRange(address, size) gives an image (base == address and
//     SafeToDownload, i.e. IsGpuModified) - the buffer is read without the image's content.
// Outside the translation signature set (src/graphics/shader/** and SHADER_CACHE_EXTRA_FILES are not touched).

#include <cstdint>

namespace Libs::DiagM5W2 {

// KYTY_DIAG_M5W2, read once per process (0/false/off/no and unset = 0); prints "M5W2: mode=<0|1>" at the first read.
bool On();

// T125: one call per (queued push, port of the context with pcm != nullptr). object_port as
// audioout2_port_type_is_object; the grain is samples * channels(data_format) samples of data_format's type
// (0 = float32, 1 = int16; any other type - the bytes are scanned).
void NoteAudioPort(bool object_port, const void* pcm, uint32_t data_format, uint32_t samples);
// T125: object port of the context without PCM at a queued push (reference).
void NoteAudioObjectNoPcm();
// One queued push (after its ports): prints the periodic line every 4096.
void NoteAudioPush();
// True if the grain has >= 1 nonzero sample (pure; float: value != 0.0f, NaN counts).
bool PcmHasNonzero(const void* pcm, uint32_t data_format, uint32_t samples);

// T313 + T179: an accepted colour DWORD fill of a surface of vk::Format vk_format with the 32-bit word.
void NoteClearDword(uint32_t vk_format, uint32_t word);
// True if our decode of (vk_format, word) differs from upstream 57c97ebd8 / 89792a3bc (pure).
bool ClearDwordDiverges(uint32_t vk_format, uint32_t word);

// T021: a created image view with this min_lod (4.8 fixed point), base_level and level_count.
void NoteMinLodView(uint32_t min_lod, uint32_t base_level, uint32_t level_count);
// True if base_level > 0 and min_lod > (level_count - 1) * 256 (pure; min_lod > 0 assumed).
bool MinLodDiverges(uint32_t min_lod, uint32_t base_level, uint32_t level_count);

// T188: one InvalidateMemoryFromGPU call with a valid range; then one call per colour image it overlaps.
void NoteInvalidateCall();
void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t address,
                         uint64_t size);

// T258: one raw read binding (!written && !formatted); gpu_image - FindImageFromRange found an image.
void NoteRawRead(bool gpu_image);

struct Totals {
	uint64_t ao_obj_push;
	uint64_t ao_obj_nz;
	uint64_t ao_obj_nopcm;
	uint64_t ao_bus_push;
	uint64_t ao_bus_nz;
	uint64_t clr_dw;
	uint64_t clr_dw_div;
	uint64_t minlod_views;
	uint64_t minlod_div;
	uint64_t inv_calls;
	uint64_t inv_part;
	uint64_t inv_gpu;
	uint64_t inv_off;
	uint64_t raw_rd;
	uint64_t raw_rd_gpu;
	uint64_t pushes;
};
Totals Read();

// "M5W2Stat: when=<when> ..." and one "M5W2Clr: when=<when> fmt=..." per vk::Format with clr_dw > 0.
void PrintStat(const char* when);
// The exit line (KYTY_DIAG_M5W2=1 only; nothing at 0).
void PrintExitStat();

} // namespace Libs::DiagM5W2
