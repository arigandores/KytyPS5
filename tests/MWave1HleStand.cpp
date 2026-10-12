// Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)): stand without the game of the HLE themes of upstream wave 1 - the
// emulator sources of this build are linked (not copied): src/libs/libAmpr.cpp (T265), src/libs/controller.cpp and
// src/libs/libPad.cpp (T272), src/libs/libFont.cpp (T231). Each theme's knob (KYTY_M_T265, KYTY_M_T272, KYTY_M_T231) is
// read by the emulator code once per process; the driver C:/kyty/m657/m2b/run_stand_m2b.py runs one process per arm at
// =0 and =1 and decides from the printed lines. Separate CMake target m_wave1_hle_stand (EXCLUDE_FROM_ALL, no add_test).
//
// Usage:
//   m_wave1_hle_stand t265 <package dir> <pairs.tsv>
//       The package directory is mounted as /app0 (read only: resolve, stat, size). For every pair of pairs.tsv (prefix,
//       FNV-1a 31-bit id, kind and size of path A, path A, kind and size of path B, path B): A is resolved, then B, then
//       the file ID API reads A's ID back. Line per pair:
//         MStand: t265 pair=<i> prefix=<p> rc_a= id_a= size_a= rc_b= id_b= size_b= same_id=<0|1> size_by_id_a= stat_a=
//                 stat_size_a= rc_a2= id_a2= keep_a=<0|1> expect_upstream=<0|1>
//       keep_a = the file ID API returns A's own size for A's ID; expect_upstream = the answer of upstream's test
//       (distinct valid IDs, the size and stat of A by A's ID, re-resolution keeps the ID).
//   m_wave1_hle_stand t272
//       Upstream's test TestTriggerEffectState (tests/ControllerSettingsTests.cpp of 3c62359e) step by step, without its
//       two lines of the trigger intensity setting (not in this tree). Line per check:
//         MStand: t272 step=<i> name="<upstream message>" rc=<rc> got=<l>,<r> want_rc=<rc> want=<l>,<r> match=<0|1>
//       (for a check of a return code only, got/want are the output left as it was).
//   m_wave1_hle_stand t231 <font file> <scale> <codes>
//       The font file (the game's) is opened with sceFontOpenFontMemory, sceFontSetScalePixel(<scale>, <scale>); every
//       character of <codes> is rendered with sceFontRenderCharGlyphImageHorizontal into a 4096 x 2048 one-byte surface
//       and measured with sceFontGetCharGlyphMetrics. The reference is the upstream raster (f96a14a0 + 58978d15): the
//       stb_truetype code of this build at stbtt_ScaleForMappingEmToPixels(<scale>), the bitmap box of the glyph, the
//       bitmap of stbtt_MakeCodepointBitmap at its own width. Line per character:
//         MStand: t231 code=<hex> img_w= img_h= ref_w= ref_h= ink_w= ink_h= ref_ink_w= ref_ink_h= sum= ref_sum=
//                 met_h= ref_met_h= clamp128=<0|1> match=<0|1>
//       clamp128 = the rendered image is at most 128 x 128 while the reference is larger; match = image size, ink box and
//       the sum of the pixels equal the reference and the metric height equals the em-scale height.
// Every arm ends with "MStand: <arm> knob=<0|1> total=<n> match=<m> END". Exit 0 unless the arguments are bad (2).

#define SDL_MAIN_HANDLED
#include "SDL.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/file.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "kernel/fileSystem.h"
#include "libs/controller.h"
#include "libs/errno.h"
#include "loader/symbolDatabase.h"

#include "stb_truetype.h"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

namespace Libs {
void InitPad_1(Loader::SymbolDatabase* s);
void InitFont_1(Loader::SymbolDatabase* s);
namespace LibKernelApr {
void InitLibKernel_1_Apr(Loader::SymbolDatabase* s);
} // namespace LibKernelApr
} // namespace Libs

namespace {

namespace FileSystem = Libs::LibKernel::FileSystem;
namespace Controller = Libs::Controller;

int KnobValue(const char* name) {
	return Common::EnvValueOn(std::getenv(name)) ? 1 : 0;
}

void* FindFunc(Loader::SymbolDatabase& symbols, const char* nid) {
	const auto* symbol = symbols.FindByNid(nid, Loader::SymbolType::Func);
	if (symbol == nullptr) {
		std::printf("MStand: missing nid %s\n", nid);
		std::fflush(stdout);
		std::_Exit(3);
	}
	return reinterpret_cast<void*>(symbol->vaddr);
}

// ------------------------------------------------------------------------------------------------ T265
int ArmT265(const char* package, const char* pairs_path) {
	Loader::SymbolDatabase symbols;
	Libs::LibKernelApr::InitLibKernel_1_Apr(&symbols);
	using Resolve = int(KYTY_SYSV_ABI*)(const char*, const char* const*, uint32_t, uint32_t*, uint64_t*, uint32_t*);
	using Stat    = int(KYTY_SYSV_ABI*)(uint32_t, FileSystem::FileStat*);
	using Size    = int(KYTY_SYSV_ABI*)(uint32_t, uint64_t*);
	const auto resolve = reinterpret_cast<Resolve>(FindFunc(symbols, "w5fcCG+t31g"));
	const auto stat    = reinterpret_cast<Stat>(FindFunc(symbols, "ApkYaHb8Sek"));
	const auto size    = reinterpret_cast<Size>(FindFunc(symbols, "WvEu7yl3Ivg"));

	FileSystem::Initialize();
	FileSystem::Mount(package, "/app0");

	std::ifstream in(pairs_path);
	std::string   line;
	int           total = 0;
	int           match = 0;
	while (std::getline(in, line)) {
		if (line.empty() || line[0] == '#' || line.rfind("ALL OK", 0) == 0 || line.rfind("FAIL", 0) == 0) {
			continue;
		}
		std::vector<std::string> f;
		std::stringstream        ss(line);
		std::string              col;
		while (std::getline(ss, col, '\t')) {
			f.push_back(col);
		}
		if (f.size() != 8) {
			continue;
		}
		const std::string& prefix = f[0];
		const char*        path_a = f[4].c_str();
		const char*        path_b = f[7].c_str();
		uint32_t           id_a = 0xffffffffu, id_b = 0xffffffffu, id_a2 = 0xffffffffu, err = 0;
		uint64_t           size_a = 0, size_b = 0, size_a2 = 0;
		const int          rc_a = resolve(prefix.c_str(), &path_a, 1, &id_a, &size_a, &err);
		const int          rc_b = resolve(prefix.c_str(), &path_b, 1, &id_b, &size_b, &err);
		uint64_t           size_by_id_a = 0;
		const int          rc_size      = size(id_a, &size_by_id_a);
		FileSystem::FileStat st {};
		const int            rc_stat = stat(id_a, &st);
		const int            rc_a2   = resolve(prefix.c_str(), &path_a, 1, &id_a2, &size_a2, &err);
		// The size the file ID API keeps for a directory is 0 (the resolve reports 0x10000).
		const uint64_t own_a  = f[2] == "d" ? 0 : size_a;
		const bool     keep_a = rc_size == 0 && size_by_id_a == own_a;
		const bool     upstream = rc_a == 0 && rc_b == 0 && id_a != id_b && id_a != 0xffffffffu && id_b != 0xffffffffu &&
		                      keep_a && rc_stat == 0 &&
		                      (f[2] == "d" || st.st_size == static_cast<int64_t>(size_a)) && rc_a2 == 0 && id_a2 == id_a;
		std::printf("MStand: t265 pair=%d prefix=%s rc_a=%d id_a=0x%08x size_a=%llu rc_b=%d id_b=0x%08x size_b=%llu "
		            "same_id=%d size_by_id_a=%llu stat_a=%d stat_size_a=%lld rc_a2=%d id_a2=0x%08x keep_a=%d "
		            "expect_upstream=%d a=%s b=%s\n",
		            total, prefix.c_str(), rc_a, id_a, static_cast<unsigned long long>(size_a), rc_b, id_b,
		            static_cast<unsigned long long>(size_b), id_a == id_b ? 1 : 0,
		            static_cast<unsigned long long>(size_by_id_a), rc_stat, static_cast<long long>(st.st_size), rc_a2,
		            id_a2, keep_a ? 1 : 0, upstream ? 1 : 0, f[4].c_str(), f[7].c_str());
		total++;
		match += upstream ? 1 : 0;
	}
	FileSystem::Umount("/app0");
	FileSystem::Shutdown();
	std::printf("MStand: t265 knob=%d total=%d match=%d END\n", KnobValue("KYTY_M_T265"), total, match);
	return 0;
}

// ------------------------------------------------------------------------------------------------ T272
struct PadTriggerEffectCommand {
	uint32_t mode;
	uint8_t  reserve[4];
	uint8_t  data[48];
};

struct PadTriggerEffectParam {
	uint8_t                 trigger_mask;
	uint8_t                 reserve[7];
	PadTriggerEffectCommand command[2];
};

static_assert(sizeof(PadTriggerEffectCommand) == 56);
static_assert(sizeof(PadTriggerEffectParam) == 120);

struct PadTriggerEffectStateInformation {
	int32_t state[2];
};

constexpr int PAD_OK                   = 0;
constexpr int PAD_ERROR_INVALID_ARG    = -2137915391; /* 0x80920001 */
constexpr int PAD_ERROR_INVALID_HANDLE = -2137915389; /* 0x80920003 */

int ArmT272() {
	SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI, "0");
	SDL_SetHint(SDL_HINT_JOYSTICK_RAWINPUT, "0");
	SDL_SetHint(SDL_HINT_JOYSTICK_WGI, "0");
	SDL_SetHint(SDL_HINT_XINPUT_ENABLED, "0");
	SDL_SetHint(SDL_HINT_DIRECTINPUT_ENABLED, "0");
	if (SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) < 0) {
		std::printf("MStand: t272 sdl_init_failed\n");
		return 4;
	}
	Controller::Initialize();
	Controller::Connect(1);

	Loader::SymbolDatabase symbols;
	Libs::InitPad_1(&symbols);
	using GetState = int(KYTY_SYSV_ABI*)(int, PadTriggerEffectStateInformation*);
	const auto get_state = reinterpret_cast<GetState>(FindFunc(symbols, "znaWI0gpuo8"));

	int  total = 0;
	int  match = 0;
	auto report = [&](const char* name, int rc, int want_rc, int32_t l, int32_t r, int32_t want_l, int32_t want_r) {
		const bool ok = rc == want_rc && l == want_l && r == want_r;
		std::printf("MStand: t272 step=%d name=\"%s\" rc=%d got=%d,%d want_rc=%d want=%d,%d match=%d\n", total, name, rc,
		            l, r, want_rc, want_l, want_r, ok ? 1 : 0);
		total++;
		match += ok ? 1 : 0;
	};
	PadTriggerEffectStateInformation info {{-1, -1}};
	const auto check_state = [&](int32_t left, int32_t right, const char* message) {
		info.state[0] = -1;
		info.state[1] = -1;
		const int rc  = get_state(1, &info);
		report(message, rc, PAD_OK, info.state[0], info.state[1], left, right);
	};
	const auto axis = [&](int left, int right) {
		Controller::SetAxis(1, Controller::Axis::TriggerLeft, left);
		Controller::SetAxis(1, Controller::Axis::TriggerRight, right);
	};
	PadTriggerEffectParam param {};
	const auto            set_effect = [&] {
		const int rc =
		    Controller::PadSetTriggerEffect(1, reinterpret_cast<const Controller::PadTriggerEffectParam*>(&param));
		if (rc != PAD_OK) {
			std::printf("MStand: t272 trigger request failed rc=%d\n", rc);
		}
	};
	const auto set_axis = [&](int id, Controller::Axis a, int v) { Controller::SetAxis(id, a, v); };

	info = {{-1, -1}};
	int rc = get_state(2, &info);
	report("invalid trigger handle changed the output", rc, PAD_ERROR_INVALID_HANDLE, info.state[0], info.state[1], -1,
	       -1);
	rc = get_state(2, nullptr);
	report("trigger state checked the output before the handle", rc, PAD_ERROR_INVALID_HANDLE, 0, 0, 0, 0);
	rc = get_state(1, nullptr);
	report("trigger state accepted a null output", rc, PAD_ERROR_INVALID_ARG, 0, 0, 0, 0);
	check_state(0, 0, "unset trigger effects did not report off");

	param.trigger_mask       = 3;
	param.command[0].mode    = 1;
	param.command[0].data[0] = 7;
	param.command[0].data[1] = 8;
	param.command[1].mode    = 2;
	param.command[1].data[0] = 2;
	param.command[1].data[1] = 7;
	param.command[1].data[2] = 6;
	set_effect();
	axis(191, 63);
	check_state(1, 3, "triggers activated before the documented start positions");
	axis(192, 64);
	check_state(2, 4, "triggers did not activate at the documented start positions");
	axis(255, 223);
	check_state(2, 4, "weapon fired before its end position");
	set_axis(1, Controller::Axis::TriggerRight, 224);
	set_axis(1, Controller::Axis::TriggerRight, 100);
	check_state(2, 5, "unpolled weapon firing was lost on partial release");
	check_state(2, 5, "reading trigger state changed the weapon latch");
	set_effect();
	check_state(2, 5, "repeating a weapon request rearmed a held trigger");
	// Upstream: CycleSetting(Setting::TriggerEffectIntensity) and its check - the setting is not in this tree.

	// A rejected two-trigger request must leave both cached commands and states intact.
	auto invalid               = param;
	invalid.command[0].mode    = 0;
	invalid.command[1].data[1] = 2;
	rc = Controller::PadSetTriggerEffect(1, reinterpret_cast<const Controller::PadTriggerEffectParam*>(&invalid));
	report("invalid weapon end position was accepted", rc, PAD_ERROR_INVALID_ARG, 0, 0, 0, 0);
	set_axis(1, Controller::Axis::TriggerLeft, 255);
	check_state(2, 5, "an invalid request changed cached trigger commands or states");
	set_axis(1, Controller::Axis::TriggerRight, 63);
	set_axis(1, Controller::Axis::TriggerRight, 100);
	check_state(2, 4, "unpolled release did not rearm the weapon");
	param.trigger_mask       = 2;
	param.command[1].data[1] = 8;
	set_effect();
	axis(255, 253);
	check_state(2, 4, "weapon end position 8 fired before output 254");
	set_axis(1, Controller::Axis::TriggerRight, 254);
	check_state(2, 5, "weapon end position 8 did not fire at output 254");

	// Masked updates preserve the other trigger, including its fired state.
	param.trigger_mask       = 1;
	param.command[0].data[0] = 9;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 254);
	check_state(1, 5, "feedback position 9 activated before full travel");
	set_axis(Controller::HOST_INPUT_CONTROLLER_ID, Controller::Axis::TriggerLeft, 255);
	check_state(2, 5, "keyboard trigger travel did not activate feedback");
	param.command[0].data[0] = 0;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 0);
	check_state(2, 5, "feedback at position 0 was suppressed by a dead zone");
	param.command[0].data[1] = 0;
	set_effect();
	check_state(1, 5, "zero-strength feedback reported active");

	param.command[0]         = {};
	param.command[0].mode    = 4;
	param.command[0].data[0] = 4;
	param.command[0].data[2] = 4;
	param.command[0].data[8] = 4;
	set_effect();
	const int feedback_cases[][2] = {{0, 2},  {1, 1},   {31, 1},  {32, 2},  {63, 2},
	                                 {64, 1}, {223, 1}, {224, 2}, {254, 2}, {255, 1}};
	for (const auto& test: feedback_cases) {
		set_axis(1, Controller::Axis::TriggerLeft, test[0]);
		check_state(test[1], 5, "multi-position feedback used the wrong position");
	}

	param.command[0]         = {};
	param.command[0].mode    = 5;
	param.command[0].data[0] = 3;
	param.command[0].data[1] = 7;
	param.command[0].data[2] = 2;
	param.command[0].data[3] = 6;
	set_effect();
	const int slope_cases[][2] = {{63, 1}, {64, 2}, {191, 2}, {192, 1}, {255, 1}};
	for (const auto& test: slope_cases) {
		set_axis(1, Controller::Axis::TriggerLeft, test[0]);
		check_state(test[1], 5, "slope feedback did not respect its start and end");
	}
	param.command[0].data[0] = 0;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 0);
	check_state(2, 5, "slope feedback at position 0 was suppressed");

	param.command[0]         = {};
	param.command[0].mode    = 3;
	param.command[0].data[0] = 6;
	param.command[0].data[1] = 4;
	param.command[0].data[2] = 20;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 159);
	check_state(6, 5, "vibration activated before position 6");
	set_axis(1, Controller::Axis::TriggerLeft, 160);
	check_state(7, 5, "vibration did not activate at position 6");
	param.command[0].data[0] = 0;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 0);
	check_state(7, 5, "vibration at position 0 was suppressed");
	param.command[0].data[2] = 0;
	set_effect();
	check_state(6, 5, "zero-frequency vibration reported active");

	param.command[0]          = {};
	param.command[0].mode     = 6;
	param.command[0].data[0]  = 20;
	param.command[0].data[10] = 4;
	set_effect();
	set_axis(1, Controller::Axis::TriggerLeft, 254);
	check_state(6, 5, "multi-position vibration activated before position 9");
	set_axis(1, Controller::Axis::TriggerLeft, 255);
	check_state(7, 5, "multi-position vibration did not activate at position 9");
	param.command[0].data[0] = 0;
	set_effect();
	check_state(6, 5, "zero-frequency multi-position vibration reported active");

	Controller::ResetInputState();
	check_state(6, 3, "input reset retained a fired weapon");
	param.command[0].mode = 0;
	set_effect();
	check_state(0, 3, "off mode retained an effect state");
	Controller::Connect(2);
	Controller::Disconnect(1);
	check_state(0, 0, "switching controllers retained effect states");

	std::printf("MStand: t272 knob=%d total=%d match=%d END\n", KnobValue("KYTY_M_T272"), total, match);
	std::fflush(stdout);
	Controller::EmergencyShutdown();
	return 0;
}

// ------------------------------------------------------------------------------------------------ T231
struct FontGlyphMetrics {
	float width;
	float height;
	struct {
		float bearing_x;
		float bearing_y;
		float advance;
	} horizontal;
	struct {
		float bearing_x;
		float bearing_y;
		float advance;
	} vertical;
};

struct FontRenderSurface {
	void*   buffer;
	int32_t width_byte;
	int8_t  pixel_size_byte;
	uint8_t system_ext0;
	uint8_t system_ext1;
	uint8_t system_ext2;
	int32_t width;
	int32_t height;
	struct {
		uint32_t x0;
		uint32_t y0;
		uint32_t x1;
		uint32_t y1;
	} scissor;
	uint32_t system_use[22];
};

struct FontTransImage {
	uint8_t* address;
	uint32_t width_byte;
	uint32_t image_width;
	uint32_t image_height;
};

struct FontSurfaceImage {
	uint8_t* address;
	uint32_t width_byte;
	uint8_t  pixel_size_byte;
	uint8_t  pixel_format;
};

struct FontGlyphImageMetrics {
	float    bearing_x;
	float    bearing_y;
	float    advance;
	float    stride;
	uint32_t width;
	uint32_t height;
};

struct FontRenderResult {
	const FontTransImage* trans_image;
	FontSurfaceImage      surface_image;
	struct {
		uint32_t x;
		uint32_t y;
		uint32_t w;
		uint32_t h;
	} update_rect;
	FontGlyphImageMetrics image_metrics;
};

struct InkBox {
	int      w   = 0;
	int      h   = 0;
	uint64_t sum = 0;
};

InkBox Ink(const uint8_t* data, int width, int height, int stride) {
	int      x0 = width, y0 = height, x1 = -1, y1 = -1;
	uint64_t sum = 0;
	for (int y = 0; y < height; y++) {
		for (int x = 0; x < width; x++) {
			const auto v = data[static_cast<size_t>(y) * stride + x];
			if (v != 0) {
				x0 = std::min(x0, x);
				y0 = std::min(y0, y);
				x1 = std::max(x1, x);
				y1 = std::max(y1, y);
				sum += v;
			}
		}
	}
	InkBox box;
	if (x1 >= 0) {
		box.w = x1 - x0 + 1;
		box.h = y1 - y0 + 1;
	}
	box.sum = sum;
	return box;
}

int ArmT231(const char* font_path, float scale, const char* codes) {
	std::ifstream     file(font_path, std::ios::binary);
	std::vector<char> raw((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
	std::vector<uint8_t> font_data(raw.begin(), raw.end());
	if (font_data.empty()) {
		std::printf("MStand: t231 font read failed\n");
		return 2;
	}

	Loader::SymbolDatabase symbols;
	Libs::InitFont_1(&symbols);
	using OpenMemory  = int(KYTY_SYSV_ABI*)(void*, const void*, uint32_t, const void*, void**);
	using SetScale    = int(KYTY_SYSV_ABI*)(void*, float, float);
	using Metrics     = int(KYTY_SYSV_ABI*)(void*, uint32_t, FontGlyphMetrics*);
	using SurfaceInit = void(KYTY_SYSV_ABI*)(FontRenderSurface*, void*, int, int, int, int);
	using Render      = int(KYTY_SYSV_ABI*)(void*, uint32_t, FontRenderSurface*, float, float, FontGlyphMetrics*,
                                       FontRenderResult*);
	const auto open_memory  = reinterpret_cast<OpenMemory>(FindFunc(symbols, "KXUpebrFk1U"));
	const auto set_scale    = reinterpret_cast<SetScale>(FindFunc(symbols, "N1EBMeGhf7E"));
	const auto metrics_of   = reinterpret_cast<Metrics>(FindFunc(symbols, "L97d+3OgMlE"));
	const auto surface_init = reinterpret_cast<SurfaceInit>(FindFunc(symbols, "gdUCnU0gHdI"));
	const auto render       = reinterpret_cast<Render>(FindFunc(symbols, "3G4zhgKuxE8"));

	void* handle = nullptr;
	int   dummy_library = 0;
	if (open_memory(&dummy_library, font_data.data(), static_cast<uint32_t>(font_data.size()), nullptr, &handle) != 0 ||
	    handle == nullptr) {
		std::printf("MStand: t231 open failed\n");
		return 2;
	}
	set_scale(handle, scale, scale);

	stbtt_fontinfo info {};
	if (stbtt_InitFont(&info, font_data.data(), 0) == 0) {
		std::printf("MStand: t231 stbtt_InitFont failed\n");
		return 2;
	}
	const float ref_scale = stbtt_ScaleForMappingEmToPixels(&info, scale);

	constexpr int        SW = 4096;
	constexpr int        SH = 2048;
	std::vector<uint8_t> surface_buf(static_cast<size_t>(SW) * SH);
	int                  total = 0;
	int                  match = 0;
	for (const char* p = codes; *p != 0; p++) {
		const auto code = static_cast<uint32_t>(static_cast<uint8_t>(*p));
		std::fill(surface_buf.begin(), surface_buf.end(), 0);
		FontRenderSurface surf {};
		surface_init(&surf, surface_buf.data(), SW, 1, SW, SH);
		FontGlyphMetrics m {};
		FontRenderResult result {};
		render(handle, code, &surf, 256.0f, 1024.0f, &m, &result);
		const uint32_t img_w = result.image_metrics.width;
		const uint32_t img_h = result.image_metrics.height;
		const InkBox   ink   = Ink(surface_buf.data(), SW, SH, SW);
		FontGlyphMetrics gm {};
		metrics_of(handle, code, &gm);

		int x0 = 0, y0 = 0, x1 = 0, y1 = 0;
		stbtt_GetCodepointBitmapBox(&info, static_cast<int>(code), ref_scale, ref_scale, &x0, &y0, &x1, &y1);
		const int            ref_w = std::max(x1 - x0, 0);
		const int            ref_h = std::max(y1 - y0, 0);
		std::vector<uint8_t> ref(std::max<size_t>(static_cast<size_t>(ref_w) * ref_h, 1), 0);
		if (ref_w > 0 && ref_h > 0) {
			stbtt_MakeCodepointBitmap(&info, ref.data(), ref_w, ref_h, ref_w, ref_scale, ref_scale,
			                          static_cast<int>(code));
		}
		const InkBox ref_ink = Ink(ref.data(), ref_w, ref_h, ref_w);
		int          bx0 = 0, by0 = 0, bx1 = 0, by1 = 0;
		stbtt_GetCodepointBox(&info, static_cast<int>(code), &bx0, &by0, &bx1, &by1);
		const float ref_met_h = static_cast<float>(by1 - by0) * ref_scale;
		const bool  clamp128  = img_w <= 128 && img_h <= 128 && (ref_w > 128 || ref_h > 128);
		const bool  ok = static_cast<int>(img_w) == ref_w && static_cast<int>(img_h) == ref_h && ink.w == ref_ink.w &&
		                ink.h == ref_ink.h && ink.sum == ref_ink.sum && std::fabs(gm.height - ref_met_h) < 0.01f;
		std::printf("MStand: t231 code=%02x img_w=%u img_h=%u ref_w=%d ref_h=%d ink_w=%d ink_h=%d ref_ink_w=%d "
		            "ref_ink_h=%d sum=%llu ref_sum=%llu met_h=%.3f ref_met_h=%.3f clamp128=%d match=%d\n",
		            code, img_w, img_h, ref_w, ref_h, ink.w, ink.h, ref_ink.w, ref_ink.h,
		            static_cast<unsigned long long>(ink.sum), static_cast<unsigned long long>(ref_ink.sum),
		            static_cast<double>(gm.height), static_cast<double>(ref_met_h), clamp128 ? 1 : 0, ok ? 1 : 0);
		total++;
		match += ok ? 1 : 0;
	}
	std::printf("MStand: t231 knob=%d total=%d match=%d END\n", KnobValue("KYTY_M_T231"), total, match);
	return 0;
}

} // namespace

int main(int argc, char** argv) {
	if (argc < 2) {
		std::fprintf(stderr, "usage: m_wave1_hle_stand t265 <package> <pairs.tsv> | t272 | t231 <font> <scale> <codes>\n");
		return 2;
	}
	const std::string arm = argv[1];
	if (!((arm == "t265" && argc == 4) || (arm == "t272" && argc == 2) || (arm == "t231" && argc == 5))) {
		std::fprintf(stderr, "bad arguments for %s\n", arm.c_str());
		return 2;
	}

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = Config::LogDirection::Silent;
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	int rc = 2;
	if (arm == "t265") {
		rc = ArmT265(argv[2], argv[3]);
	} else if (arm == "t272") {
		rc = ArmT272();
	} else {
		rc = ArmT231(argv[2], static_cast<float>(std::atof(argv[3])), argv[4]);
	}
	Log::Flush();
	std::fflush(stdout);
	// No SDL_Quit and no subsystem teardown, as the emulator.
	std::_Exit(rc);
}
