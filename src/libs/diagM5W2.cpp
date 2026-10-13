#include "libs/diagM5W2.h"

#include "common/envFlag.h"
#include "common/logging/log.h"

#include <array>
#include <atomic>
#include <cinttypes>
#include <cstring>
#include <vulkan/vulkan.hpp>

// Track M, M6a (HPP-848, ROADMAP s122 item 767(i)): the counters of KYTY_DIAG_M5W2 (diagM5W2.h). Every counter is a
// relaxed atomic summed over the process; the call sites call the Note functions only when On() is true.

namespace Libs::DiagM5W2 {

namespace {

std::atomic<uint64_t> g_ao_obj_push {0};
std::atomic<uint64_t> g_ao_obj_nz {0};
std::atomic<uint64_t> g_ao_obj_nopcm {0};
std::atomic<uint64_t> g_ao_bus_push {0};
std::atomic<uint64_t> g_ao_bus_nz {0};
std::atomic<uint64_t> g_clr_dw {0};
std::atomic<uint64_t> g_clr_dw_div {0};
std::atomic<uint64_t> g_minlod_views {0};
std::atomic<uint64_t> g_minlod_div {0};
std::atomic<uint64_t> g_inv_calls {0};
std::atomic<uint64_t> g_inv_part {0};
std::atomic<uint64_t> g_inv_gpu {0};
std::atomic<uint64_t> g_inv_off {0};
std::atomic<uint64_t> g_raw_rd {0};
std::atomic<uint64_t> g_raw_rd_gpu {0};
std::atomic<uint64_t> g_pushes {0};

// Per vk::Format value (formats >= 255 share the last row, printed fmt=255).
constexpr uint32_t                             FMT_ROWS = 256;
std::array<std::atomic<uint64_t>, FMT_ROWS> g_clr_fmt {};
std::array<std::atomic<uint64_t>, FMT_ROWS> g_clr_fmt_div {};

constexpr uint64_t PERIODIC_PUSHES = 4096;

uint64_t Load(const std::atomic<uint64_t>& a) {
	return a.load(std::memory_order_relaxed);
}

void Bump(std::atomic<uint64_t>& a) {
	a.fetch_add(1, std::memory_order_relaxed);
}

} // namespace

bool On() {
	static const bool on = [] {
		const bool value = Common::EnvFlagOn("KYTY_DIAG_M5W2");
		LOGF("M5W2: mode=%d\n", value ? 1 : 0);
		return value;
	}();
	return on;
}

bool PcmHasNonzero(const void* pcm, uint32_t data_format, uint32_t samples) {
	if (pcm == nullptr || samples == 0) {
		return false;
	}
	// Channels and type as libAudio2.cpp audioout2_data_format_channels / audioout2_data_format_to_audio_format.
	const uint32_t raw_channels = (data_format >> 8u) & 0xffu;
	const uint32_t channels     = raw_channels == 0 ? 2u : (raw_channels < 16u ? raw_channels : 16u);
	const uint32_t data_type    = data_format & 0x7fu;
	const auto*    bytes        = static_cast<const uint8_t*>(pcm);
	const uint64_t count        = static_cast<uint64_t>(samples) * channels;
	if (data_type == 0) {
		for (uint64_t i = 0; i < count; i++) {
			float v = 0.0f;
			std::memcpy(&v, bytes + i * 4u, 4u);
			if (v != 0.0f || v != v) {
				return true;
			}
		}
		return false;
	}
	const uint64_t size = count * (data_type == 1 ? 2u : 4u);
	for (uint64_t i = 0; i < size; i++) {
		if (bytes[i] != 0) {
			return true;
		}
	}
	return false;
}

void NoteAudioPort(bool object_port, const void* pcm, uint32_t data_format, uint32_t samples) {
	const bool nz = PcmHasNonzero(pcm, data_format, samples);
	if (object_port) {
		Bump(g_ao_obj_push);
		if (nz) {
			Bump(g_ao_obj_nz);
		}
	} else {
		Bump(g_ao_bus_push);
		if (nz) {
			Bump(g_ao_bus_nz);
		}
	}
}

void NoteAudioObjectNoPcm() {
	Bump(g_ao_obj_nopcm);
}

void NoteAudioPush() {
	if ((g_pushes.fetch_add(1, std::memory_order_relaxed) + 1) % PERIODIC_PUSHES == 0) {
		PrintStat("periodic");
	}
}

bool ClearDwordDiverges(uint32_t vk_format, uint32_t word) {
	switch (static_cast<vk::Format>(vk_format)) {
		case vk::Format::eR16Sfloat:
		case vk::Format::eR16Unorm: return (word & 0xffffu) != (word >> 16u);
		case vk::Format::eR16G16B16A16Sfloat:
		case vk::Format::eR16G16B16A16Unorm:
		case vk::Format::eR32G32Sfloat: return word != 0;
		default: return false;
	}
}

void NoteClearDword(uint32_t vk_format, uint32_t word) {
	const uint32_t row = vk_format < FMT_ROWS - 1 ? vk_format : FMT_ROWS - 1;
	const bool     div = ClearDwordDiverges(vk_format, word);
	Bump(g_clr_dw);
	Bump(g_clr_fmt[row]);
	if (div) {
		Bump(g_clr_dw_div);
		Bump(g_clr_fmt_div[row]);
	}
}

bool MinLodDiverges(uint32_t min_lod, uint32_t base_level, uint32_t level_count) {
	if (base_level == 0 || level_count == 0) {
		return false;
	}
	return static_cast<uint64_t>(min_lod) > static_cast<uint64_t>(level_count - 1u) * 256u;
}

void NoteMinLodView(uint32_t min_lod, uint32_t base_level, uint32_t level_count) {
	if (min_lod == 0) {
		return;
	}
	Bump(g_minlod_views);
	if (MinLodDiverges(min_lod, base_level, level_count)) {
		Bump(g_minlod_div);
	}
}

void NoteInvalidateCall() {
	Bump(g_inv_calls);
}

void NoteInvalidateImage(bool gpu_modified, uint64_t image_address, uint64_t image_size, uint64_t address,
                         uint64_t size) {
	if (!gpu_modified) {
		return;
	}
	Bump(g_inv_gpu);
	const bool covers = address <= image_address && address + size >= image_address + image_size;
	if (!covers) {
		Bump(g_inv_part);
		if (address != image_address) {
			Bump(g_inv_off);
		}
	}
}

void NoteRawRead(bool gpu_image) {
	Bump(g_raw_rd);
	if (gpu_image) {
		Bump(g_raw_rd_gpu);
	}
}

Totals Read() {
	return {Load(g_ao_obj_push), Load(g_ao_obj_nz),    Load(g_ao_obj_nopcm), Load(g_ao_bus_push),
	        Load(g_ao_bus_nz),   Load(g_clr_dw),       Load(g_clr_dw_div),   Load(g_minlod_views),
	        Load(g_minlod_div),  Load(g_inv_calls),    Load(g_inv_part),     Load(g_inv_gpu),
	        Load(g_inv_off),     Load(g_raw_rd),       Load(g_raw_rd_gpu),   Load(g_pushes)};
}

void PrintStat(const char* when) {
	const auto t = Read();
	LOGF("M5W2Stat: when=%s pushes=%" PRIu64 " ao_obj_push=%" PRIu64 " ao_obj_nz=%" PRIu64 " ao_obj_nopcm=%" PRIu64
	     " ao_bus_push=%" PRIu64 " ao_bus_nz=%" PRIu64 " clr_dw=%" PRIu64 " clr_dw_div=%" PRIu64 " minlod_views=%" PRIu64
	     " minlod_div=%" PRIu64 " inv_calls=%" PRIu64 " inv_part=%" PRIu64 " inv_gpu=%" PRIu64 " inv_off=%" PRIu64
	     " raw_rd=%" PRIu64 " raw_rd_gpu=%" PRIu64 "\n",
	     when, t.pushes, t.ao_obj_push, t.ao_obj_nz, t.ao_obj_nopcm, t.ao_bus_push, t.ao_bus_nz, t.clr_dw, t.clr_dw_div,
	     t.minlod_views, t.minlod_div, t.inv_calls, t.inv_part, t.inv_gpu, t.inv_off, t.raw_rd, t.raw_rd_gpu);
	for (uint32_t row = 0; row < FMT_ROWS; row++) {
		const uint64_t n = Load(g_clr_fmt[row]);
		if (n != 0) {
			LOGF("M5W2Clr: when=%s fmt=%u clr_dw=%" PRIu64 " clr_dw_div=%" PRIu64 "\n", when, row, n,
			     Load(g_clr_fmt_div[row]));
		}
	}
}

void PrintExitStat() {
	if (On()) {
		PrintStat("exit");
	}
}

} // namespace Libs::DiagM5W2
