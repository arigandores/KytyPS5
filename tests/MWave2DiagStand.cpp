// Track M, M6a (HPP-848, ROADMAP s122 item 767(i), (v), (z)): stand without the game of the measurement-only knob
// KYTY_DIAG_M5W2 (src/libs/diagM5W2.cpp) and of the signature lines without a knob. The emulator sources of this build
// are linked (not copied). The driver C:/kyty/m657/m6a/run_stand_m6a.py runs one process per arm (and per knob value
// where the arm reads the knob) and decides from the printed "MStand: m6 ..." lines and from the log file of the arm.
// Separate CMake target m_wave2_diag_stand (EXCLUDE_FROM_ALL, no add_test).
//
// Usage: m_wave2_diag_stand <arm> <log file>       (LOGF of the emulator code goes to <log file>)
//   pure   every counter through its Note function: per field one input where the field must grow by 1 and one where
//          it must stay (its denominator, if any, grows). Line per check:
//            MStand: m6 arm=pure case=<name> field=<f> delta=<d> want=<w> match=<0|1>
//   audio  T125 through the real AudioOut2 functions (ContextCreate, PortCreate, PortSetAttributes, ContextPush): an
//          object port (port_type 0x100, mono float) and a bus port (port_type 0, 3-channel float - no host device is
//          opened for it); push 1 - both grains nonzero, push 2 - both zero, push 3 - the object port has no PCM. Line per
//          push with the counter deltas (at KYTY_DIAG_M5W2=0 every delta must be 0 - the site is gated):
//            MStand: m6 arm=audio push=<i> knob=<k> d_obj_push= d_obj_nz= d_obj_nopcm= d_bus_push= d_bus_nz= d_pushes=
//   printf T031 through the guest printf: "%.*s" with -1 twice and with 2 once; the log must hold exactly one line
//          "GuestPrintf: negative precision prec=-1".
//   ampr   T309 through the real Ampr command buffer NIDs (8aI7R7WaOlc constructor, N-FSPA4S3nI set buffer 0x40 bytes,
//          j0+3uJMxYJY write address x3, then x22 more): the first two records fit, the third is refused (EBUSY); the log
//          must hold "AmprRecordSpace: refused why=space" and "AmprWriteAddress: refused why=ensure", at most 20 of each.
//            MStand: m6 arm=ampr call=<i> rc=<rc>
//   agc    T023 through Gen5::AgcAcbResetQueue (AllocateDW(2) -> ReserveDW) on a command buffer with cursor_up null,
//          cursor_down null, both null, cursor_down < cursor_up (the grow callback repairs the cursors), a normal one,
//          then 22 more bad ones; the log must hold the classes up0, down0, both0, down_lt_up once each in that order,
//          no line for the normal call, and at most 20 lines in total.
//            MStand: m6 arm=agc call=<i> state=<s> ok=<0|1>
// Every arm ends with "MStand: m6 arm=<arm> knob=<0|1> total=<n> match=<m> END". Exit 0 unless the arguments are bad (2).

#define SDL_MAIN_HANDLED
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "kernel/memory.h"
#include "libs/agc.h"
#include "libs/audio.h"
#include "libs/diagM5W2.h"
#include "libs/guestPrintf.h"
#include "libs/libs.h"
#include "loader/symbolDatabase.h"
#include "loader/timer.h"

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <vulkan/vulkan.hpp>

// The layouts of libAudio2.cpp (the same definitions; audio.h only declares them).
namespace Libs::Audio::AudioOut2 {
struct AudioOut2ContextParam {
	uint32_t max_ports;
	uint32_t max_object_ports;
	uint32_t guarantee_object_ports;
	uint32_t queue_depth;
	uint32_t num_grains;
	uint32_t flags;
	uint32_t reserved[10];
};
struct AudioOut2PortParam {
	uint16_t            port_type;
	uint16_t            pad;
	uint32_t            data_format;
	uint32_t            sampling_freq;
	uint32_t            flags;
	AudioOut2UserHandle user_handle;
	uint32_t            reserved[10];
};
struct AudioOut2Attribute {
	uint32_t    attribute_id;
	int32_t     reserved;
	const void* value;
	size_t      value_size;
};
struct AudioOut2Pcm {
	const void* data;
};
} // namespace Libs::Audio::AudioOut2

namespace Libs::LibAmpr {
void InitAmpr_1(Loader::SymbolDatabase* s);
} // namespace Libs::LibAmpr

namespace {

namespace D   = Libs::DiagM5W2;
namespace AO2 = Libs::Audio::AudioOut2;

int g_total = 0;
int g_match = 0;

int KnobValue() {
	return Common::EnvFlagOn("KYTY_DIAG_M5W2") ? 1 : 0;
}

void* FindFunc(Loader::SymbolDatabase& symbols, const char* nid) {
	const auto* symbol = symbols.FindByNid(nid, Loader::SymbolType::Func);
	if (symbol == nullptr) {
		std::printf("MStand: m6 missing nid %s\n", nid);
		std::fflush(stdout);
		std::_Exit(3);
	}
	return reinterpret_cast<void*>(symbol->vaddr);
}

uint64_t Field(const D::Totals& t, const std::string& f) {
	if (f == "ao_obj_push") return t.ao_obj_push;
	if (f == "ao_obj_nz") return t.ao_obj_nz;
	if (f == "ao_obj_nopcm") return t.ao_obj_nopcm;
	if (f == "ao_bus_push") return t.ao_bus_push;
	if (f == "ao_bus_nz") return t.ao_bus_nz;
	if (f == "clr_dw") return t.clr_dw;
	if (f == "clr_dw_div") return t.clr_dw_div;
	if (f == "minlod_views") return t.minlod_views;
	if (f == "minlod_div") return t.minlod_div;
	if (f == "inv_calls") return t.inv_calls;
	if (f == "inv_part") return t.inv_part;
	if (f == "inv_gpu") return t.inv_gpu;
	if (f == "inv_off") return t.inv_off;
	if (f == "raw_rd") return t.raw_rd;
	if (f == "raw_rd_gpu") return t.raw_rd_gpu;
	if (f == "pushes") return t.pushes;
	if (f == "minlod_div_x") return t.minlod_div_x;
	if (f == "clr_dw_div8") return t.clr_dw_div8;
	if (f == "ao_obj_unread") return t.ao_obj_unread;
	if (f == "inv_part_src") return t.inv_part_src;
	std::printf("MStand: m6 unknown field %s\n", f.c_str());
	std::_Exit(2);
}

// Runs fn and checks the delta of every named field against its wanted value.
template <typename Fn>
void Check(const char* name, Fn fn, std::initializer_list<std::pair<const char*, uint64_t>> want) {
	const auto before = D::Read();
	fn();
	const auto after = D::Read();
	for (const auto& [f, w]: want) {
		const uint64_t d  = Field(after, f) - Field(before, f);
		const bool     ok = d == w;
		std::printf("MStand: m6 arm=pure case=%s field=%s delta=%llu want=%llu match=%d\n", name, f,
		            static_cast<unsigned long long>(d), static_cast<unsigned long long>(w), ok ? 1 : 0);
		g_total++;
		g_match += ok ? 1 : 0;
	}
}

// M6a2: guest memory for object PCM (the object grain is read through TryReadBacking since M6a2). One flexible
// mapping of 256 KiB, CPU read/write, handed out in 4 KiB-aligned pieces.
uint8_t* GuestAlloc(size_t size) {
	static uint8_t* base = nullptr;
	static size_t   used = 0;
	constexpr size_t TOTAL = 0x40000;
	if (base == nullptr) {
		void*     addr = nullptr;
		const int rc   = Libs::LibKernel::Memory::KernelMapNamedFlexibleMemory(&addr, TOTAL, 0x3, 0, "m6a2stand");
		if (rc != 0 || addr == nullptr) {
			std::printf("MStand: m6 guest map failed rc=%d\n", rc);
			std::fflush(stdout);
			std::_Exit(3);
		}
		base = static_cast<uint8_t*>(addr);
		std::memset(base, 0, TOTAL);
	}
	const size_t aligned = (size + 0xfffu) & ~size_t {0xfff};
	if (used + aligned > TOTAL) {
		std::printf("MStand: m6 guest memory exhausted\n");
		std::fflush(stdout);
		std::_Exit(3);
	}
	uint8_t* p = base + used;
	used += aligned;
	return p;
}

template <typename V>
V* GuestCopy(const std::vector<V>& v) {
	auto* p = reinterpret_cast<V*>(GuestAlloc(v.size() * sizeof(V)));
	std::memcpy(p, v.data(), v.size() * sizeof(V));
	return p;
}

// M6a2: a pointer no guest mapping covers (and no host page either) - the guarded reader refuses it.
const void* const UNREADABLE = reinterpret_cast<const void*>(uintptr_t {0x1000});

// ------------------------------------------------------------------------------------------------ pure
int ArmPure() {
	// M6a2: the PCM of every object case lives in guest memory; bus cases keep host memory (raw read).
	const float*   f_nz = GuestCopy(std::vector<float> {0.0f, 0.0f, 0.25f, 0.0f});
	const float*   f_z  = GuestCopy(std::vector<float>(4, 0.0f));
	const int16_t* s_nz = GuestCopy(std::vector<int16_t> {0, 0, 0, 7});
	const int16_t* s_z  = GuestCopy(std::vector<int16_t>(4, 0));
	const std::vector<float> hf_nz {0.0f, 0.0f, 0.25f, 0.0f};
	const std::vector<float> hf_z(4, 0.0f);
	// T125: mono float (0x100) and mono int16 (0x101), 4 samples.
	Check("ao_obj_nz_float", [&] { D::NoteAudioPort(true, f_nz, 0x100, 4); },
	      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}, {"ao_obj_unread", 0}, {"ao_bus_push", 0}, {"ao_bus_nz", 0}});
	Check("ao_obj_zero_float", [&] { D::NoteAudioPort(true, f_z, 0x100, 4); },
	      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});
	Check("ao_obj_nz_int16", [&] { D::NoteAudioPort(true, s_nz, 0x101, 4); },
	      {{"ao_obj_push", 1}, {"ao_obj_nz", 1}, {"ao_obj_unread", 0}});
	Check("ao_obj_zero_int16", [&] { D::NoteAudioPort(true, s_z, 0x101, 4); },
	      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});
	// M6a2 (item 770(g)): an unreadable object pointer - counted, not read, the process lives.
	Check("ao_obj_unread", [&] { D::NoteAudioPort(true, UNREADABLE, 0x100, 4); },
	      {{"ao_obj_push", 1}, {"ao_obj_unread", 1}, {"ao_obj_nz", 0}});
	Check("ao_bus_nz", [&] { D::NoteAudioPort(false, hf_nz.data(), 0x100, 4); },
	      {{"ao_bus_push", 1}, {"ao_bus_nz", 1}, {"ao_obj_push", 0}, {"ao_obj_nz", 0}, {"ao_obj_unread", 0}});
	Check("ao_bus_zero", [&] { D::NoteAudioPort(false, hf_z.data(), 0x100, 4); },
	      {{"ao_bus_push", 1}, {"ao_bus_nz", 0}});
	Check("ao_obj_nopcm", [&] { D::NoteAudioObjectNoPcm(); }, {{"ao_obj_nopcm", 1}, {"ao_obj_push", 0}});
	Check("pushes", [&] { D::NoteAudioPush(); }, {{"pushes", 1}});
	// T313 + T179 (vk::Format values).
	const auto fmt = [](vk::Format f) { return static_cast<uint32_t>(f); };
	Check("clr_r16f_lo_ne_hi", [&] { D::NoteClearDword(fmt(vk::Format::eR16Sfloat), 0x00003c00u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 1}, {"clr_dw_div8", 0}});
	Check("clr_r16f_lo_eq_hi", [&] { D::NoteClearDword(fmt(vk::Format::eR16Sfloat), 0x3c003c00u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});
	Check("clr_r16unorm_lo_ne_hi", [&] { D::NoteClearDword(fmt(vk::Format::eR16Unorm), 0x0000ffffu); },
	      {{"clr_dw", 1}, {"clr_dw_div", 1}, {"clr_dw_div8", 0}});
	Check("clr_rgba16f_nz", [&] { D::NoteClearDword(fmt(vk::Format::eR16G16B16A16Sfloat), 0x3c003c00u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 1}, {"clr_dw_div8", 0}});
	Check("clr_rgba16f_zero", [&] { D::NoteClearDword(fmt(vk::Format::eR16G16B16A16Sfloat), 0u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});
	Check("clr_rgba16unorm_nz", [&] { D::NoteClearDword(fmt(vk::Format::eR16G16B16A16Unorm), 1u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 1}, {"clr_dw_div8", 0}});
	Check("clr_rg32f_nz", [&] { D::NoteClearDword(fmt(vk::Format::eR32G32Sfloat), 0x3f800000u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 1}, {"clr_dw_div8", 0}});
	Check("clr_rgba8_nz", [&] { D::NoteClearDword(fmt(vk::Format::eR8G8B8A8Unorm), 0xffffffffu); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});
	// M6a2 (item 770(v)): class (a3) of M5a - R8Unorm without a repeated byte, R8G8Unorm with lo != hi.
	Check("clr_r8_div8", [&] { D::NoteClearDword(fmt(vk::Format::eR8Unorm), 0x00ff00ffu); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 1}});
	Check("clr_r8_rep", [&] { D::NoteClearDword(fmt(vk::Format::eR8Unorm), 0x7f7f7f7fu); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});
	Check("clr_rg8_div8", [&] { D::NoteClearDword(fmt(vk::Format::eR8G8Unorm), 0x00001234u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 1}});
	Check("clr_rg8_rep", [&] { D::NoteClearDword(fmt(vk::Format::eR8G8Unorm), 0x12341234u); },
	      {{"clr_dw", 1}, {"clr_dw_div", 0}, {"clr_dw_div8", 0}});
	// T021.
	// M6a2 (item 770(b)): minlod_div_x - case (B 1, count 3, M 768) both 1; case (B 2, count 2, M 384) div 1, x 0.
	Check("minlod_div", [&] { D::NoteMinLodView(3 * 256, 1, 3); },
	      {{"minlod_views", 1}, {"minlod_div", 1}, {"minlod_div_x", 1}});
	Check("minlod_div_not_x", [&] { D::NoteMinLodView(384, 2, 2); },
	      {{"minlod_views", 1}, {"minlod_div", 1}, {"minlod_div_x", 0}});
	Check("minlod_base0", [&] { D::NoteMinLodView(3 * 256, 0, 3); },
	      {{"minlod_views", 1}, {"minlod_div", 0}, {"minlod_div_x", 0}});
	Check("minlod_inside", [&] { D::NoteMinLodView(2 * 256, 1, 3); },
	      {{"minlod_views", 1}, {"minlod_div", 0}, {"minlod_div_x", 0}});
	Check("minlod_zero", [&] { D::NoteMinLodView(0, 1, 3); },
	      {{"minlod_views", 0}, {"minlod_div", 0}, {"minlod_div_x", 0}});
	// T188.
	Check("inv_call", [&] { D::NoteInvalidateCall(); }, {{"inv_calls", 1}});
	Check("inv_part_off", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0x11000, 0x100); },
	      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 1}, {"inv_part_src", 1}});
	Check("inv_part_base", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0x10000, 0x100); },
	      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 0}, {"inv_part_src", 1}});
	Check("inv_cover", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x4000, 0xf000, 0x8000); },
	      {{"inv_gpu", 1}, {"inv_part", 0}, {"inv_off", 0}, {"inv_part_src", 0}});
	Check("inv_not_gpu", [&] { D::NoteInvalidateImage(false, 0x10000, 0x4000, 0x4000, 0x11000, 0x100); },
	      {{"inv_gpu", 0}, {"inv_part", 0}, {"inv_off", 0}, {"inv_part_src", 0}});
	// M6a2 (item 770(d)): source_size 0x1000 < data size 0x4000 - the write covers the source, not the data.
	Check("inv_src_cover", [&] { D::NoteInvalidateImage(true, 0x10000, 0x4000, 0x1000, 0x10000, 0x1000); },
	      {{"inv_gpu", 1}, {"inv_part", 1}, {"inv_off", 0}, {"inv_part_src", 0}});
	// T258.
	Check("raw_rd_gpu", [&] { D::NoteRawRead(true); }, {{"raw_rd", 1}, {"raw_rd_gpu", 1}});
	Check("raw_rd_plain", [&] { D::NoteRawRead(false); }, {{"raw_rd", 1}, {"raw_rd_gpu", 0}});
	D::PrintStat("stand");
	std::printf("MStand: m6 arm=pure knob=%d on=%d total=%d match=%d END\n", KnobValue(), D::On() ? 1 : 0, g_total,
	            g_match);
	return 0;
}

// ------------------------------------------------------------------------------------------------ audio
int ArmAudio() {
	AO2::AudioOut2ContextParam cp {};
	AO2::AudioOut2ContextResetParam(&cp);
	cp.num_grains = 256;
	std::vector<uint8_t>       ctx_mem(0x20000);
	AO2::AudioOut2ContextHandle ctx = 0;
	if (AO2::AudioOut2ContextCreate(&cp, ctx_mem.data(), ctx_mem.size(), &ctx) != 0) {
		std::printf("MStand: m6 arm=audio context failed\n");
		return 2;
	}
	AO2::AudioOut2PortParam pp_obj {};
	pp_obj.port_type     = 0x100;
	pp_obj.data_format   = 0x100; // mono float
	pp_obj.sampling_freq = 48000;
	AO2::AudioOut2PortParam pp_bus {};
	pp_bus.port_type     = 0;
	pp_bus.data_format   = 0x300; // 3-channel float: no AudioInternal format, no host device opened
	pp_bus.sampling_freq = 48000;
	AO2::AudioOut2PortHandle obj = 0;
	AO2::AudioOut2PortHandle bus = 0;
	if (AO2::AudioOut2PortCreate(ctx, &pp_obj, &obj) != 0 || AO2::AudioOut2PortCreate(ctx, &pp_bus, &bus) != 0) {
		std::printf("MStand: m6 arm=audio port failed\n");
		return 2;
	}
	// M6a2: the object PCM lives in guest memory (read through TryReadBacking); bus PCM stays in host memory.
	auto*              obj_nz = reinterpret_cast<float*>(GuestAlloc(256 * sizeof(float)));
	auto*              obj_z  = reinterpret_cast<float*>(GuestAlloc(256 * sizeof(float)));
	std::vector<float> bus_nz(256 * 3, 0.0f);
	std::vector<float> bus_z(256 * 3, 0.0f);
	obj_nz[255]  = 0.5f;
	bus_nz[100]  = -0.25f;
	const auto set_pcm = [](AO2::AudioOut2PortHandle port, const void* data) {
		AO2::AudioOut2Pcm       pcm {data};
		AO2::AudioOut2Attribute a {};
		a.attribute_id = 0; // AUDIO_OUT2_PORT_ATTRIBUTE_ID_PCM
		a.value        = &pcm;
		a.value_size   = sizeof(pcm);
		AO2::AudioOut2PortSetAttributes(port, &a, 1);
	};
	const int knob = KnobValue();
	// push 1: both nonzero; push 2: both zero; push 3: a fresh object port without PCM (the old ports keep zeros);
	// M6a2 push 4: the first object port points to an unreadable address (ao_obj_unread 1 at =1; alive at 0 and 1).
	struct Want {
		uint64_t obj_push, obj_nz, obj_nopcm, bus_push, bus_nz, pushes, obj_unread;
	};
	const Want wants[4] = {{1, 1, 0, 1, 1, 1, 0}, {1, 0, 0, 1, 0, 1, 0}, {1, 0, 1, 1, 0, 1, 0}, {1, 0, 1, 1, 0, 1, 1}};
	for (int i = 0; i < 4; i++) {
		if (i == 0) {
			set_pcm(obj, obj_nz);
			set_pcm(bus, bus_nz.data());
		} else if (i == 1) {
			set_pcm(obj, obj_z);
			set_pcm(bus, bus_z.data());
		} else if (i == 3) {
			set_pcm(obj, UNREADABLE);
		} else {
			AO2::AudioOut2PortHandle obj2 = 0;
			if (AO2::AudioOut2PortCreate(ctx, &pp_obj, &obj2) != 0) {
				std::printf("MStand: m6 arm=audio port2 failed\n");
				return 2;
			}
		}
		const auto before = D::Read();
		const int  rc     = AO2::AudioOut2ContextPush(ctx, 0);
		const auto after  = D::Read();
		const Want w      = knob != 0 ? wants[i] : Want {0, 0, 0, 0, 0, 0, 0};
		const Want d {after.ao_obj_push - before.ao_obj_push, after.ao_obj_nz - before.ao_obj_nz,
		              after.ao_obj_nopcm - before.ao_obj_nopcm, after.ao_bus_push - before.ao_bus_push,
		              after.ao_bus_nz - before.ao_bus_nz, after.pushes - before.pushes,
		              after.ao_obj_unread - before.ao_obj_unread};
		const bool ok = rc == 0 && std::memcmp(&w, &d, sizeof(Want)) == 0;
		std::printf("MStand: m6 arm=audio push=%d knob=%d rc=%d d_obj_push=%llu d_obj_nz=%llu d_obj_nopcm=%llu "
		            "d_bus_push=%llu d_bus_nz=%llu d_pushes=%llu d_obj_unread=%llu match=%d\n",
		            i + 1, knob, rc, static_cast<unsigned long long>(d.obj_push),
		            static_cast<unsigned long long>(d.obj_nz), static_cast<unsigned long long>(d.obj_nopcm),
		            static_cast<unsigned long long>(d.bus_push), static_cast<unsigned long long>(d.bus_nz),
		            static_cast<unsigned long long>(d.pushes), static_cast<unsigned long long>(d.obj_unread), ok ? 1 : 0);
		g_total++;
		g_match += ok ? 1 : 0;
	}
	std::printf("MStand: m6 arm=audio knob=%d on=%d total=%d match=%d END\n", knob, D::On() ? 1 : 0, g_total, g_match);
	return 0;
}

// ------------------------------------------------------------------------------------------------ printf
int ArmPrintf() {
	auto pf = Libs::GetGuestPrintfStdFunc();
	pf("MStandPrintf A [%.*s]\n", -1, "abcdef");
	pf("MStandPrintf B [%.*s]\n", -1, "abcdef");
	pf("MStandPrintf C [%.*s]\n", 2, "abcdef");
	std::printf("MStand: m6 arm=printf knob=%d total=0 match=0 END\n", KnobValue());
	return 0;
}

// ------------------------------------------------------------------------------------------------ ampr
int ArmAmpr() {
	Loader::SymbolDatabase symbols;
	Libs::LibAmpr::InitAmpr_1(&symbols);
	using Ctor   = int(KYTY_SYSV_ABI*)(void*);
	using SetBuf = int(KYTY_SYSV_ABI*)(void*, void*, uint32_t);
	using WrAddr = int(KYTY_SYSV_ABI*)(void*, volatile uint64_t*, uint64_t, uint32_t);
	const auto ctor    = reinterpret_cast<Ctor>(FindFunc(symbols, "8aI7R7WaOlc"));
	const auto set_buf = reinterpret_cast<SetBuf>(FindFunc(symbols, "N-FSPA4S3nI"));
	const auto wr_addr = reinterpret_cast<WrAddr>(FindFunc(symbols, "j0+3uJMxYJY"));
	alignas(64) static uint8_t cb[0x1000];
	alignas(64) static uint8_t buf[0x40];
	static volatile uint64_t   target = 0;
	const int                  rc_c   = ctor(cb);
	const int                  rc_s   = set_buf(cb, buf, sizeof(buf));
	std::printf("MStand: m6 arm=ampr ctor=%d set_buffer=%d\n", rc_c, rc_s);
	for (int i = 0; i < 25; i++) {
		const int rc = wr_addr(cb, &target, 0x1000u + static_cast<uint64_t>(i), 0);
		std::printf("MStand: m6 arm=ampr call=%d rc=%d\n", i + 1, rc);
	}
	std::printf("MStand: m6 arm=ampr knob=%d total=0 match=0 END\n", KnobValue());
	return 0;
}

// ------------------------------------------------------------------------------------------------ agc
// The layout of Gen5::CommandBuffer (agc.cpp: bottom, top, cursor_up, cursor_down, callback, user_data, reserved_dw).
struct AgcBuffer {
	uint32_t* bottom;
	uint32_t* top;
	uint32_t* cursor_up;
	uint32_t* cursor_down;
	void*     callback;
	void*     user_data;
	uint32_t  reserved_dw;
};

uint32_t g_agc_store[4096];

KYTY_SYSV_ABI bool AgcGrow(void* raw, uint32_t /*need*/, void* /*user*/) {
	auto* b        = static_cast<AgcBuffer*>(raw);
	b->bottom      = g_agc_store;
	b->top         = g_agc_store + 4096;
	b->cursor_up   = g_agc_store;
	b->cursor_down = g_agc_store + 4096;
	return true;
}

int ArmAgc() {
	const char* states[] = {"up0", "down0", "both0", "down_lt_up", "normal"};
	for (int i = 0; i < 5 + 22; i++) {
		const char* st = i < 5 ? states[i] : states[i % 4];
		AgcBuffer   b {};
		b.bottom      = g_agc_store;
		b.top         = g_agc_store + 4096;
		b.callback    = reinterpret_cast<void*>(&AgcGrow);
		b.cursor_up   = g_agc_store + 16;
		b.cursor_down = g_agc_store + 4096;
		if (std::strcmp(st, "up0") == 0) {
			b.cursor_up = nullptr;
		} else if (std::strcmp(st, "down0") == 0) {
			b.cursor_down = nullptr;
		} else if (std::strcmp(st, "both0") == 0) {
			b.cursor_up   = nullptr;
			b.cursor_down = nullptr;
		} else if (std::strcmp(st, "down_lt_up") == 0) {
			b.cursor_up   = g_agc_store + 100;
			b.cursor_down = g_agc_store + 50;
		}
		const auto* cmd = Libs::Graphics::Gen5::AgcAcbResetQueue(reinterpret_cast<Libs::Graphics::Gen5::CommandBuffer*>(&b), 0);
		std::printf("MStand: m6 arm=agc call=%d state=%s ok=%d\n", i + 1, st, cmd != nullptr ? 1 : 0);
	}
	std::printf("MStand: m6 arm=agc knob=%d total=0 match=0 END\n", KnobValue());
	return 0;
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 3) {
		std::fprintf(stderr, "usage: m_wave2_diag_stand pure|audio|printf|ampr|agc <log file>\n");
		return 2;
	}
	const std::string arm = argv[1];
	if (arm != "pure" && arm != "audio" && arm != "printf" && arm != "ampr" && arm != "agc") {
		std::fprintf(stderr, "bad arm %s\n", arm.c_str());
		return 2;
	}

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction   = Config::LogDirection::File;
	options.printf_output_file = argv[2];
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();
	subsystems.Initialize<Loader::Timer::Lifecycle>();
	if (arm == "pure" || arm == "audio") {
		subsystems.Initialize<Libs::LibKernel::Memory::Lifecycle>(); // M6a2: guest memory for object PCM
	}

	int rc = 2;
	if (arm == "pure") {
		rc = ArmPure();
	} else if (arm == "audio") {
		rc = ArmAudio();
	} else if (arm == "printf") {
		rc = ArmPrintf();
	} else if (arm == "ampr") {
		rc = ArmAmpr();
	} else {
		rc = ArmAgc();
	}
	Log::Flush();
	Log::DrainForExit(); // the asynchronous writer (KYTY_FIX_B36=1) drains before _Exit
	std::fflush(stdout);
	// No subsystem teardown, as the emulator.
	std::_Exit(rc);
}
