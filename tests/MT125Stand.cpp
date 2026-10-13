// Track M, M8a (HPP-858, ROADMAP s122 item 778(g)(2)(i)): stand of T125 (KYTY_M_T125) without the game. The real
// src/libs/libAudio2.cpp; the device layer of AudioInternal is replaced here (it records every device and copies the
// bytes of every output). One process is one value of the knob (environment); the driver
// docs/track-m/m8a/run_stand_m8a.py runs it with KYTY_M_T125=0 and =1, compares the bus outputs of the two runs byte for
// byte and the exit line "MT125Stat:" with the EXPECT line. Usage: m_t125_stand <out dir>; exit code 0 = every member
// of this process passed.
#include "libs/audio.h"
#include "libs/audio_internal.h"
#include "libs/errno.h"

#if __has_include("libs/diagM5W2.h")
#include "libs/diagM5W2.h" // main and later trees: libAudio2.cpp calls the measurement of M6a (KYTY_DIAG_M5W2)
#define KYTY_MT125_STAND_DIAG_STUBS 1
#endif

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <mutex>
#include <string>
#include <vector>

namespace {

namespace AudioOut2 = Libs::Audio::AudioOut2;
using Libs::Audio::AudioInternal::Format;

constexpr uint32_t GRAINS     = 512;
constexpr float    HALF_POWER = 0.70710678f;
constexpr double   TOL        = 1e-6;

struct Device {
	int      handle  = 0;
	int      type    = 0;
	uint32_t samples = 0;
	uint32_t freq    = 0;
	Format   format  = Format::Unknown;
	bool     live    = false;
	bool     in_ctx  = false; // opened inside AudioOut2ContextCreate (the object mix device)
};

struct Output {
	int                  handle = 0;
	std::vector<uint8_t> bytes;
};

std::mutex          g_mutex;
std::vector<Device> g_devices;
std::vector<Output> g_outputs;
int                 g_next_handle = 1;
bool                g_in_ctx      = false;
bool                g_fail        = false;
std::string         g_out_dir;
int                 g_mode = 0;

uint32_t FormatBytes(Format format, uint32_t samples) {
	switch (format) {
		case Format::Signed16bitMono: return samples * 2;
		case Format::Signed16bitStereo: return samples * 4;
		case Format::FloatMono: return samples * 4;
		case Format::FloatStereo: return samples * 8;
		default: return 0;
	}
}

void Member(const std::string& name, bool ok, const std::string& detail) {
	std::printf("MEMBER %s %s %s\n", name.c_str(), ok ? "OK" : "FAIL", detail.c_str());
	if (!ok) {
		g_fail = true;
	}
}

struct PortParam {
	uint16_t port_type;
	uint16_t pad;
	uint32_t data_format;
	uint32_t sampling_freq;
	uint32_t flags;
	uint64_t user_handle;
	uint32_t reserved[10];
};

struct ContextParam {
	uint32_t max_ports;
	uint32_t max_object_ports;
	uint32_t guarantee_object_ports;
	uint32_t queue_depth;
	uint32_t num_grains;
	uint32_t flags;
	uint32_t reserved[10];
};

struct Attribute {
	uint32_t    attribute_id;
	int32_t     reserved;
	const void* value;
	size_t      value_size;
};

struct Pcm {
	const void* data;
};

AudioOut2::AudioOut2ContextHandle CreateContext(uint32_t max_object_ports) {
	ContextParam param {};
	param.max_ports        = 256;
	param.max_object_ports = max_object_ports;
	param.queue_depth      = 64; // no queue-model sleep in the stand
	param.num_grains       = GRAINS;
	AudioOut2::AudioOut2ContextHandle ctx = 0;
	{
		std::lock_guard lock(g_mutex);
		g_in_ctx = true;
	}
	const int rc = AudioOut2::AudioOut2ContextCreate(reinterpret_cast<const AudioOut2::AudioOut2ContextParam*>(&param),
	                                                 nullptr, 0, &ctx);
	{
		std::lock_guard lock(g_mutex);
		g_in_ctx = false;
	}
	if (rc != OK) {
		Member("ctx_create", false, "rc=" + std::to_string(rc));
	}
	return ctx;
}

AudioOut2::AudioOut2PortHandle CreatePort(AudioOut2::AudioOut2ContextHandle ctx, uint16_t port_type, uint32_t data_format,
                                          uint32_t freq) {
	PortParam param {};
	param.port_type     = port_type;
	param.data_format   = data_format;
	param.sampling_freq = freq;
	param.user_handle   = 1;
	AudioOut2::AudioOut2PortHandle port = 0;
	const int rc = AudioOut2::AudioOut2PortCreate(ctx, reinterpret_cast<const AudioOut2::AudioOut2PortParam*>(&param), &port);
	if (rc != OK) {
		Member("port_create", false, "rc=" + std::to_string(rc));
	}
	return port;
}

int SetAttributes(AudioOut2::AudioOut2PortHandle port, const Attribute* attributes, uint32_t num) {
	return AudioOut2::AudioOut2PortSetAttributes(port, reinterpret_cast<const AudioOut2::AudioOut2Attribute*>(attributes),
	                                             num);
}

void SetPcm(AudioOut2::AudioOut2PortHandle port, const void* data) {
	const Pcm       pcm {data};
	const Attribute attribute {0, 0, &pcm, sizeof(pcm)};
	if (SetAttributes(port, &attribute, 1) != OK) {
		Member("set_pcm", false, "rc!=OK");
	}
}

void SetGain(AudioOut2::AudioOut2PortHandle port, const void* value, size_t size) {
	const Attribute attribute {1, 0, value, size};
	if (SetAttributes(port, &attribute, 1) != OK) {
		Member("set_gain_rc", false, "rc!=OK (the return code must not change)");
	}
}

void SetAmbisonics(AudioOut2::AudioOut2PortHandle port, uint32_t value) {
	const Attribute attribute {8, 0, &value, sizeof(value)};
	if (SetAttributes(port, &attribute, 1) != OK) {
		Member("set_amb_rc", false, "rc!=OK (the return code must not change)");
	}
}

std::vector<Output> Push(AudioOut2::AudioOut2ContextHandle ctx) {
	{
		std::lock_guard lock(g_mutex);
		g_outputs.clear();
	}
	if (AudioOut2::AudioOut2ContextPush(ctx, 1) != OK) {
		Member("push_rc", false, "rc!=OK");
	}
	std::lock_guard lock(g_mutex);
	return g_outputs;
}

const Device* FindDevice(int handle) {
	std::lock_guard lock(g_mutex);
	for (const auto& d: g_devices) {
		if (d.handle == handle) {
			return &d;
		}
	}
	return nullptr;
}

int LiveDevices() {
	std::lock_guard lock(g_mutex);
	return static_cast<int>(std::count_if(g_devices.begin(), g_devices.end(), [](const Device& d) { return d.live; }));
}

std::vector<int> CtxDevices() {
	std::lock_guard lock(g_mutex);
	std::vector<int> r;
	for (const auto& d: g_devices) {
		if (d.in_ctx) {
			r.push_back(d.handle);
		}
	}
	return r;
}

// Max |out - ref| over the stereo float frames of an output; ref = (left, right) per frame.
double MaxDiff(const Output& out, const std::vector<double>& ref) {
	if (out.bytes.size() != ref.size() * sizeof(float)) {
		return std::numeric_limits<double>::infinity();
	}
	double m = 0.0;
	for (size_t i = 0; i < ref.size(); i++) {
		float v = 0.0f;
		std::memcpy(&v, out.bytes.data() + i * sizeof(float), sizeof(float));
		if (!std::isfinite(v)) {
			// Track M, M8c (RC3 of M8b, ROADMAP s122 item 783(g)): a non-finite output sample fails the comparison;
			// std::max(m, NaN) keeps m, so without this a NaN mix (NaN GAIN accepted) compared as max_diff 0.
			return std::numeric_limits<double>::infinity();
		}
		m = std::max(m, std::fabs(static_cast<double>(v) - ref[i]));
	}
	return m;
}

void WriteFile(const std::string& name, const std::vector<uint8_t>& bytes) {
	const std::string path = g_out_dir + "/" + name;
	FILE*             f    = std::fopen(path.c_str(), "wb");
	if (f == nullptr) {
		Member("write_file", false, path);
		return;
	}
	std::fwrite(bytes.data(), 1, bytes.size(), f);
	std::fclose(f);
}

double Sine(double amplitude, double hz, uint32_t t) {
	return amplitude * std::sin(2.0 * 3.14159265358979323846 * hz * static_cast<double>(t) / 48000.0);
}

uint64_t g_expect_mixed    = 0;
uint64_t g_expect_mixed_nz = 0;

// Scene A: 4 bus ports (types 0, 1, 3, 6; stereo float, different sines) + N = 4 objects in the mix (3 mono float, 1
// mono s16; 48 kHz; GAIN 0.25 / 0.5 / 1.0 / 0.75) + objects that must not be mixed (0x100 stereo float, 0x100 at
// 44.1 kHz, type 0x101, 0x100 without PCM) + a second context with its own object that must not leak into A.
void SceneA() {
	const auto devices_before = static_cast<int>(CtxDevices().size());
	const auto ctx            = CreateContext(8);
	const auto ctx_devices    = CtxDevices();
	const int  opened         = static_cast<int>(ctx_devices.size()) - devices_before;
	int        mix_handle     = 0;
	if (g_mode == 1) {
		bool ok = opened == 1;
		if (ok) {
			mix_handle    = ctx_devices.back();
			const auto* d = FindDevice(mix_handle);
			ok = d != nullptr && d->type == 0 && d->format == Format::FloatStereo && d->freq == 48000 && d->samples == GRAINS;
		}
		Member("A_mix_device", ok, "opened_in_create=" + std::to_string(opened));
	} else {
		Member("A_no_mix_device", opened == 0, "opened_in_create=" + std::to_string(opened));
	}

	const uint16_t bus_types[4] = {0, 1, 3, 6};
	const double   bus_hz[4]    = {110.0, 165.0, 247.0, 370.0};
	std::array<AudioOut2::AudioOut2PortHandle, 4> bus {};
	for (int i = 0; i < 4; i++) {
		bus[i] = CreatePort(ctx, bus_types[i], 0x200, 48000);
	}
	struct Obj {
		uint32_t format;
		double   hz;
		double   amplitude;
		float    gain;
	};
	const Obj objs[4] = {{0x100, 220.0, 0.8, 0.25f}, {0x100, 330.0, 0.8, 0.5f}, {0x100, 440.0, 0.8, 1.0f},
	                     {0x101, 550.0, 12000.0, 0.75f}};
	std::array<AudioOut2::AudioOut2PortHandle, 4> obj {};
	for (int i = 0; i < 4; i++) {
		obj[i] = CreatePort(ctx, 0x100, objs[i].format, 48000);
		const float gain = objs[i].gain;
		const Attribute gain_attribute {1, 0, &gain, sizeof(gain)};
		if (SetAttributes(obj[i], &gain_attribute, 1) != OK) {
			Member("A_gain_rc", false, "rc!=OK");
		}
	}
	const auto x_stereo = CreatePort(ctx, 0x100, 0x200, 48000); // stereo float object
	const auto x_44k    = CreatePort(ctx, 0x100, 0x100, 44100); // mono float at 44.1 kHz
	const auto x_type   = CreatePort(ctx, 0x101, 0x100, 48000); // another object type
	(void)CreatePort(ctx, 0x100, 0x100, 48000);                // object without PCM

	const auto  ctx_b   = CreateContext(1);
	const auto  b_obj   = CreatePort(ctx_b, 0x100, 0x100, 48000);
	std::vector<float> b_pcm(GRAINS, 1.0f);
	SetPcm(b_obj, b_pcm.data());

	std::vector<float> x_pcm(GRAINS * 2, 0.9f);
	SetPcm(x_stereo, x_pcm.data());
	SetPcm(x_44k, x_pcm.data());
	SetPcm(x_type, x_pcm.data());

	for (uint32_t k = 0; k < 4; k++) {
		std::array<std::vector<float>, 4> bus_pcm;
		for (int i = 0; i < 4; i++) {
			bus_pcm[i].resize(GRAINS * 2);
			for (uint32_t t = 0; t < GRAINS; t++) {
				const auto s           = static_cast<float>(Sine(0.5, bus_hz[i], k * GRAINS + t));
				bus_pcm[i][t * 2]     = s;
				bus_pcm[i][t * 2 + 1] = -s;
			}
			SetPcm(bus[i], bus_pcm[i].data());
		}
		std::array<std::vector<float>, 3> obj_f;
		std::vector<int16_t>              obj_s(GRAINS);
		std::vector<double>               ref(GRAINS * 2, 0.0);
		for (int i = 0; i < 4; i++) {
			for (uint32_t t = 0; t < GRAINS; t++) {
				double x = 0.0;
				if (i < 3) {
					obj_f[i].resize(GRAINS);
					obj_f[i][t] = static_cast<float>(Sine(objs[i].amplitude, objs[i].hz, k * GRAINS + t));
					x           = obj_f[i][t];
				} else {
					obj_s[t] = static_cast<int16_t>(std::lround(Sine(objs[i].amplitude, objs[i].hz, k * GRAINS + t)));
					x        = obj_s[t] / 32768.0;
				}
				ref[t * 2] += x * objs[i].gain * HALF_POWER;
				ref[t * 2 + 1] += x * objs[i].gain * HALF_POWER;
			}
			SetPcm(obj[i], i < 3 ? static_cast<const void*>(obj_f[i].data()) : obj_s.data());
		}
		const auto out = Push(ctx);
		const size_t want = (g_mode == 1 ? 5u : 4u);
		Member("A" + std::to_string(k) + "_outputs", out.size() == want,
		       "n=" + std::to_string(out.size()) + " want=" + std::to_string(want));
		bool bus_ok = out.size() >= 4;
		for (int i = 0; i < 4 && bus_ok; i++) {
			const auto* d = FindDevice(out[i].handle);
			bus_ok = d != nullptr && !d->in_ctx && out[i].bytes.size() == GRAINS * 8 &&
			         std::memcmp(out[i].bytes.data(), bus_pcm[i].data(), GRAINS * 8) == 0;
			WriteFile("bus_A" + std::to_string(k) + "_" + std::to_string(i) + ".bin", out[i].bytes);
		}
		Member("A" + std::to_string(k) + "_bus_is_bus_pcm", bus_ok, "4 outputs = the 4 bus PCM buffers in order");
		if (g_mode == 1) {
			bool   mix_ok = out.size() == 5 && out[4].handle == mix_handle;
			double diff   = mix_ok ? MaxDiff(out[4], ref) : 1e9;
			Member("A" + std::to_string(k) + "_mix_eq_ref", mix_ok && diff <= TOL, "max_diff=" + std::to_string(diff));
			if (out.size() == 5) {
				WriteFile("mix_A" + std::to_string(k) + ".bin", out[4].bytes);
			}
			g_expect_mixed++;
			g_expect_mixed_nz++;
		} else {
			bool none = true;
			for (const auto& o: out) {
				const auto* d = FindDevice(o.handle);
				none = none && d != nullptr && !d->in_ctx;
			}
			Member("A" + std::to_string(k) + "_no_object_pcm", none && out.size() == 4, "no output on a mix device");
		}
	}

	// The second context: its object only, never in A.
	const auto out_b = Push(ctx_b);
	if (g_mode == 1) {
		std::vector<double> ref_b(GRAINS * 2, HALF_POWER);
		const bool ok = out_b.size() == 1;
		Member("B_mix_own_object", ok && MaxDiff(out_b[0], ref_b) <= TOL, "n=" + std::to_string(out_b.size()));
		g_expect_mixed++;
		g_expect_mixed_nz++;
	} else {
		Member("B_no_output", out_b.empty(), "n=" + std::to_string(out_b.size()));
	}
	AudioOut2::AudioOut2ContextDestroy(ctx_b);
	const int live_before_destroy = LiveDevices();
	AudioOut2::AudioOut2ContextDestroy(ctx);
	const int live_after = LiveDevices();
	Member("A_destroy_closes", live_after == 0,
	       "live_before=" + std::to_string(live_before_destroy) + " live_after=" + std::to_string(live_after));
}

// The cases of upstream TestObjectGainAndAmbisonics that are the mix (c86c8b4d9 tests/AudioOut2PortTests.cpp): the
// AMBISONICS table x GAIN 0.5, two pushes each (no accumulation), zero GAIN mutes, GAIN persists; plus invalid GAIN /
// AMBISONICS values not applied. Float (0x100) and s16 (0x101) objects.
void SceneGain() {
	struct Case {
		uint32_t channel;
		float    left;
		float    right;
	};
	const Case cases[] = {{UINT32_MAX, HALF_POWER, HALF_POWER}, {0, 1.0f, 1.0f}, {1, 0.0f, 0.0f}, {2, HALF_POWER, -HALF_POWER},
	                      {3, 0.0f, 0.0f}, {64, HALF_POWER, HALF_POWER}, {65, HALF_POWER, -HALF_POWER}, {66, 0.0f, 0.0f},
	                      {99, 0.0f, 0.0f}};
	for (const uint32_t format: {0x100u, 0x101u}) {
		const std::string tag = (format == 0x100 ? "G_f32" : "G_s16");
		const auto        ctx = CreateContext(1);
		const auto        port = CreatePort(ctx, 0x100, format, 48000);
		std::vector<float>   floating(GRAINS, 0.5f);
		std::vector<int16_t> integer(GRAINS, 16384);
		const void*          pcm = format == 0x100 ? static_cast<const void*>(floating.data()) : integer.data();
		auto check = [&](const std::string& name, double left, double right, bool counts_nz) {
			const auto out = Push(ctx);
			if (g_mode == 0) {
				Member(tag + "_" + name, out.empty(), "n=" + std::to_string(out.size()));
				return;
			}
			std::vector<double> ref(GRAINS * 2);
			for (uint32_t t = 0; t < GRAINS; t++) {
				ref[t * 2]     = left;
				ref[t * 2 + 1] = right;
			}
			const bool ok = out.size() == 1;
			Member(tag + "_" + name, ok && MaxDiff(out[0], ref) <= TOL,
			       "n=" + std::to_string(out.size()) + (ok ? " max_diff=" + std::to_string(MaxDiff(out[0], ref)) : ""));
			g_expect_mixed++;
			if (counts_nz) {
				g_expect_mixed_nz++;
			}
		};
		for (const auto& c: cases) {
			const Pcm       input {pcm};
			const float     gain = 0.5f;
			const Attribute attributes[] {{0, 0, &input, sizeof(input)}, {1, 0, &gain, sizeof(gain)},
			                              {8, 0, &c.channel, sizeof(c.channel)}};
			if (SetAttributes(port, attributes, 3) != OK) {
				Member(tag + "_set3_rc", false, "rc!=OK");
			}
			const bool nz = c.left != 0.0f || c.right != 0.0f;
			for (int push = 0; push < 2; push++) {
				check("amb" + std::to_string(c.channel) + "_p" + std::to_string(push), 0.25 * c.left, 0.25 * c.right, nz);
			}
		}
		SetAmbisonics(port, UINT32_MAX);
		const float zero = 0.0f;
		SetGain(port, &zero, sizeof(zero));
		SetPcm(port, pcm);
		check("zero_gain_mutes", 0.0, 0.0, false);
		SetPcm(port, pcm);
		check("gain_persists", 0.0, 0.0, false);
		const float one = 1.0f;
		SetGain(port, &one, sizeof(one));
		const float negative = -1.0f;
		SetGain(port, &negative, sizeof(negative));
		const float nan = std::numeric_limits<float>::quiet_NaN();
		SetGain(port, &nan, sizeof(nan));
		const float two[2] = {2.0f, 2.0f};
		SetGain(port, two, sizeof(two));
		SetAmbisonics(port, 16);
		SetAmbisonics(port, 100);
		SetPcm(port, pcm);
		check("invalid_not_applied", 0.5 * HALF_POWER, 0.5 * HALF_POWER, true);
		AudioOut2::AudioOut2ContextDestroy(ctx);
		Member(tag + "_destroy_closes", LiveDevices() == 0, "live=" + std::to_string(LiveDevices()));
	}
}

} // namespace

namespace Libs::Audio::AudioInternal {

int AudioOutOpen(int type, uint32_t samples_num, uint32_t freq, Format format) {
	std::lock_guard lock(g_mutex);
	Device d;
	d.handle  = g_next_handle++;
	d.type    = type;
	d.samples = samples_num;
	d.freq    = freq;
	d.format  = format;
	d.live    = true;
	d.in_ctx  = g_in_ctx;
	g_devices.push_back(d);
	return d.handle;
}

void AudioOutClose(int handle) {
	std::lock_guard lock(g_mutex);
	for (auto& d: g_devices) {
		if (d.handle == handle) {
			d.live = false;
		}
	}
}

bool AudioOutHasDevice(int handle) {
	std::lock_guard lock(g_mutex);
	for (const auto& d: g_devices) {
		if (d.handle == handle) {
			return d.live && d.type != 10;
		}
	}
	return false;
}

uint32_t AudioOutOutputs(const OutputParam* params, uint32_t num, bool /*blocking*/) {
	std::lock_guard lock(g_mutex);
	for (uint32_t i = 0; i < num; i++) {
		Output out;
		out.handle = params[i].handle;
		for (const auto& d: g_devices) {
			if (d.handle == params[i].handle && params[i].data != nullptr) {
				const auto* bytes = static_cast<const uint8_t*>(params[i].data);
				out.bytes.assign(bytes, bytes + FormatBytes(d.format, d.samples));
			}
		}
		g_outputs.push_back(std::move(out));
	}
	return GRAINS;
}

} // namespace Libs::Audio::AudioInternal

namespace Libs {
// Defined by src/libs/libs.cpp in the emulator (read by PRINT_NAME); the stand links libAudio2.cpp alone.
thread_local bool g_print_name_thread_forced = false;
} // namespace Libs

namespace Libs::LibKernel {

uint64_t KYTY_SYSV_ABI KernelGetProcessTime() {
	static std::atomic_uint64_t now {0};
	return now.fetch_add(1000);
}

} // namespace Libs::LibKernel

#if defined(KYTY_MT125_STAND_DIAG_STUBS)
namespace Libs::DiagM5W2 {
// The measurement of M6a is not part of this stand (KYTY_DIAG_M5W2 = 0 here).
bool On() {
	return false;
}
void NoteAudioPort(bool /*object_port*/, const void* /*pcm*/, uint32_t /*data_format*/, uint32_t /*samples*/) {}
void NoteAudioObjectNoPcm() {}
void NoteAudioPush() {}
} // namespace Libs::DiagM5W2
#endif

int main(int argc, char** argv) {
	std::setvbuf(stdout, nullptr, _IONBF, 0);
	if (argc < 2) {
		std::printf("usage: m_t125_stand <out dir>\n");
		return 2;
	}
	g_out_dir      = argv[1];
	const char* m  = std::getenv("KYTY_M_T125");
	g_mode         = (m != nullptr && m[0] == '1' && m[1] == '\0') ? 1 : 0;
	std::printf("STAND MT125 env=%s\n", m == nullptr ? "(unset)" : m);
	SceneA();
	SceneGain();
	std::printf("EXPECT mixed=%llu mixed_nz=%llu\n", static_cast<unsigned long long>(g_expect_mixed),
	            static_cast<unsigned long long>(g_expect_mixed_nz));
	std::printf("STAND DONE mode=%d fail=%d\n", g_mode, g_fail ? 1 : 0);
	std::fflush(stdout);
	std::quick_exit(g_fail ? 1 : 0);
}
