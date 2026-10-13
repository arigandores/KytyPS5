#include "common/assert.h"
#include "common/diagB32.h" // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))
#include "common/common.h"
#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/threads.h"
#include "kernel/pthread.h"
#include "libs/audio.h"
#include "libs/audio_internal.h"
#include "libs/diagM5W2.h" // Track M, M6a (KYTY_DIAG_M5W2)
#include "libs/errno.h"
#include "libs/libs.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace Libs::Audio {

namespace {

constexpr int AUDIO_OUT_PORT_TYPE_MAIN      = 0;
constexpr int AUDIO_OUT_PORT_TYPE_BGM       = 1;
constexpr int AUDIO_OUT_PORT_TYPE_VOICE     = 2;
constexpr int AUDIO_OUT_PORT_TYPE_PERSONAL  = 3;
constexpr int AUDIO_OUT_PORT_TYPE_PADSPK    = 4;
constexpr int AUDIO_OUT_PORT_TYPE_VIBRATION = 10;
constexpr int AUDIO_OUT_PORT_TYPE_AUX       = 127;

} // namespace

namespace AudioOut2 {

LIB_NAME("AudioOut2", "AudioOut");

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

struct AudioOut2Position {
	float x;
	float y;
	float z;
};

struct AudioOut2PortState {
	uint16_t output;
	uint8_t  num_channels;
	uint8_t  pad1;
	int16_t  volume;
	uint16_t reroute_counter;
	uint32_t flags;
	uint32_t pad2;
	uint64_t reserved[6];
};

struct AudioOut2SystemState {
	float    loudness;
	uint32_t pad;
	uint64_t reserved[7];
};

struct AudioOut2SpeakerAngle {
	int16_t azimuth;
	int16_t elevation;
};

struct AudioOut2SpeakerInfo {
	uint8_t               type;
	uint8_t               pad1;
	int16_t               pad2;
	uint32_t              available_bits;
	uint32_t              flags;
	uint32_t              pad3;
	AudioOut2SpeakerAngle speaker_angle[16];
};

struct AudioOut2SystemDebugStateParam {
	uint32_t debug_state_id;
	int32_t  reserved;
	void*    param;
	size_t   param_size;
};

struct AudioOut2MasteringParamsHeader {
	uint32_t params_id;
};

struct AudioOut2MasteringStatesHeader {
	uint32_t states_id;
};

struct AudioOut2MasteringStatesDescriptor {
	uint32_t id;
	uint32_t size;
};

static constexpr uint32_t AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS = 8;
static constexpr uint32_t AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS    = 3;
static constexpr uint32_t AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS_V2 = 4;

struct AudioOut2MasteringCompressorStates {
	AudioOut2MasteringStatesDescriptor descriptor;
	uint32_t                           reserved[2];
	float                              input_rms[AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS]
	                                            [AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
	float                              compression_coeff[AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS]
	                                                    [AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
};

struct AudioOut2MasteringCompressorStatesV2 {
	AudioOut2MasteringStatesDescriptor descriptor;
	uint32_t                           reserved[2];
	float                              input_rms[AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS_V2]
	                                            [AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
	float                              compression_coeff[AUDIO_OUT2_MASTERING_COMPRESSOR_BANDS_V2]
	                                                    [AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
};

struct AudioOut2MasteringLimiterStates {
	AudioOut2MasteringStatesDescriptor descriptor;
	uint32_t                           reserved[2];
	float                              input_peak[AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
	float                              output_peak[AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
	float                              gain_peak[AUDIO_OUT2_MASTERING_MAX_SYSTEM_CHANNELS];
};

struct AudioOut2MasteringStates {
	AudioOut2MasteringStatesHeader     states_header;
	uint32_t                           reserved[3];
	AudioOut2MasteringCompressorStates compressor_states;
	AudioOut2MasteringLimiterStates    limiter_states;
};

struct AudioOut2MasteringStatesV2 {
	AudioOut2MasteringStatesHeader       states_header;
	uint32_t                             reserved[3];
	AudioOut2MasteringCompressorStatesV2 compressor_states;
	AudioOut2MasteringLimiterStates      limiter_states;
};

static std::atomic_uint64_t g_audioout2_next_context {1};
static std::atomic_uint64_t g_audioout2_next_port {1};
static std::atomic_uint64_t g_audioout2_next_user {1};

struct AudioOut2ContextState {
	bool                   used        = false;
	AudioOut2ContextHandle handle      = 0;
	uint32_t               queue_depth = 4;
	uint32_t               queued      = 0;
	uint32_t               num_grains  = 512;
	uint64_t               last_update = 0;
	int                    object_audio_handle = 0; // Track M, M8a (T125): the object mix device (KYTY_M_T125=1)
};

struct AudioOut2PortStateEntry {
	bool                   used          = false;
	AudioOut2PortHandle    handle        = 0;
	AudioOut2ContextHandle context       = 0;
	uint16_t               port_type     = 0;
	uint32_t               data_format   = 0;
	uint32_t               sampling_freq = 48000;
	uint32_t               samples_num   = 512;
	AudioInternal::Format  audio_format  = AudioInternal::Format::Unknown;
	int                    audio_handle  = 0;
	const void*            pcm_data      = nullptr;
	float                  m125_gain       = 1.0f;       // Track M, M8a (T125): GAIN of an object port
	uint32_t               m125_ambisonics = UINT32_MAX; // Track M, M8a (T125): AMBISONICS of an object port
};

struct AudioOut2SpeakerArrayState {
	bool                        used          = false;
	uint32_t                    num_speakers  = 0;
	uint8_t                     is_3d         = 0;
	uint8_t                     is_ambisonics = 0;
	AudioOut2SpeakerArrayHandle handle        = nullptr;
};

struct AudioOut2LatencyState {
	bool     used       = false;
	uint32_t user_id    = 0;
	uint32_t output     = 0;
	uint32_t latency_us = 0;
};

static Common::Mutex                              g_audioout2_context_mutex;
static std::array<AudioOut2ContextState, 16>      g_audioout2_contexts;
static Common::Mutex                              g_audioout2_port_mutex;
static std::array<AudioOut2PortStateEntry, 256>   g_audioout2_ports;
static Common::Mutex                              g_audioout2_speaker_array_mutex;
static std::array<AudioOut2SpeakerArrayState, 32> g_audioout2_speaker_arrays;
static Common::Mutex                              g_audioout2_latency_mutex;
static std::array<AudioOut2LatencyState, 16>      g_audioout2_latencies;

static constexpr int AUDIO_OUT2_ERROR_NOT_READY                   = -2144960504; /* 0x80268008 */
static constexpr int AUDIO_OUT2_ERROR_PORT_FULL                   = -2144960494; /* 0x80268012 */
static constexpr int AUDIO_OUT2_ERROR_INVALID_PARAM               = -2144960511; /* 0x80268001 */
static constexpr int AUDIO_OUT2_ERROR_MASTERING_INVALID_API_PARAM = -2144959999; /* 0x80268201 */
static constexpr int AUDIO_OUT2_ERROR_MASTERING_INVALID_STATES_ID = -2144959996; /* 0x80268204 */
static constexpr uint32_t AUDIO_OUT2_PORT_ATTRIBUTE_ID_PCM        = 0;
static constexpr uint32_t AUDIO_OUT2_MASTERING_OUTPUT_RECORDING   = 2;
static constexpr uint32_t AUDIO_OUT2_MASTERING_STATES_ID_DEFAULT  = 1;
static constexpr uint32_t AUDIO_OUT2_MASTERING_STATES_ID_V2       = 2;
static constexpr uint32_t AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_COMPRESSOR_DEFAULT = 0x01010001;
static constexpr uint32_t AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_COMPRESSOR_V2      = 0x01020001;
static constexpr uint32_t AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_LIMITER_DEFAULT    = 0x01010003;

static AudioOut2ContextState* audioout2_find_context_locked(AudioOut2ContextHandle ctx) {
	for (auto& state: g_audioout2_contexts) {
		if (state.used && state.handle == ctx) {
			return &state;
		}
	}

	return nullptr;
}

static uint32_t audioout2_grain_micros(uint32_t grains) {
	const auto sample_count = (grains == 0 ? 512u : grains);
	return std::max<uint32_t>((sample_count * 1000000u) / 48000u, 1000u);
}

static uint8_t audioout2_data_format_channels(uint32_t data_format) {
	const auto channels = (data_format >> 8u) & 0xffu;
	return static_cast<uint8_t>(channels == 0 ? 2u : std::min(channels, 16u));
}

static AudioInternal::Format audioout2_data_format_to_audio_format(uint32_t data_format) {
	const auto channels  = audioout2_data_format_channels(data_format);
	const auto data_type = data_format & 0x7fu;
	const auto is_std    = (data_format & 0x80u) != 0;

	switch (data_type) {
		case 0:
			switch (channels) {
				case 1: return AudioInternal::Format::FloatMono;
				case 2: return AudioInternal::Format::FloatStereo;
				case 8:
					return is_std ? AudioInternal::Format::Float8ChStd
					              : AudioInternal::Format::Float8Ch;
				case 12:
					if (!is_std) {
						return AudioInternal::Format::Float12Ch;
					}
					break;
				default: break;
			}
			break;
		case 1:
			switch (channels) {
				case 1: return AudioInternal::Format::Signed16bitMono;
				case 2: return AudioInternal::Format::Signed16bitStereo;
				case 8:
					return is_std ? AudioInternal::Format::Signed16bit8ChStd
					              : AudioInternal::Format::Signed16bit8Ch;
				default: break;
			}
			break;
		default: break;
	}

	return AudioInternal::Format::Unknown;
}

static int audioout2_port_type_to_audio_out_type(uint16_t port_type) {
	switch (port_type & 0xffu) {
		case 0: return AUDIO_OUT_PORT_TYPE_MAIN;
		case 1: return AUDIO_OUT_PORT_TYPE_BGM;
		case 2: return AUDIO_OUT_PORT_TYPE_VOICE;
		case 3: return AUDIO_OUT_PORT_TYPE_PADSPK;
		case 4: return AUDIO_OUT_PORT_TYPE_PERSONAL;
		case 5: return AUDIO_OUT_PORT_TYPE_AUX;
		case 6: return AUDIO_OUT_PORT_TYPE_VIBRATION;
		default: return AUDIO_OUT_PORT_TYPE_MAIN;
	}
}

static bool audioout2_port_type_is_object(uint16_t port_type) {
	return (port_type & 0xff00u) == 0x0100u;
}

static void audioout2_update_context_locked(AudioOut2ContextState* state) {
	if (state == nullptr) {
		return;
	}

	const auto now = LibKernel::KernelGetProcessTime();
	if (state->last_update == 0 || state->queued == 0) {
		state->last_update = now;
		return;
	}

	const auto grain_micros = static_cast<uint64_t>(audioout2_grain_micros(state->num_grains));
	if (now <= state->last_update || grain_micros == 0) {
		return;
	}

	const auto elapsed = now - state->last_update;
	const auto drained = std::min<uint64_t>(state->queued, elapsed / grain_micros);
	if (drained == 0) {
		return;
	}

	state->queued -= static_cast<uint32_t>(drained);
	state->last_update += drained * grain_micros;
	if (state->queued == 0) {
		state->last_update = now;
	}
}

static AudioOut2PortStateEntry* audioout2_find_port_locked(AudioOut2PortHandle port) {
	for (auto& state: g_audioout2_ports) {
		if (state.used && state.handle == port) {
			return &state;
		}
	}

	return nullptr;
}

// Track M, M8a (T125, upstream c86c8b4d9 in own form; HPP-858, ROADMAP s122 item 778(g)(2)): KYTY_M_T125 (default 0),
// read once per process (line "MT125: mode="). At 1 the object ports of a context (port type 0x100, mono float or
// mono s16, 48 kHz) are mixed into one stereo float device of the context, opened by AudioOut2ContextCreate when
// max_object_ports > 0 (AudioOutOpen -> OpenSdlDevice -> the F8 owner SdlAudioAcquire), with the port GAIN and the
// stereo decode of AMBISONICS (the form of upstream audioout2_mix_object); the PCM of an object is read through its
// pointer at the push, as the PCM of a bus port. The bus ports keep the selection and the data of 0 byte for byte (no
// GAIN on them); the return codes to the game do not change (an invalid GAIN / AMBISONICS is not applied). At 0 the
// object PCM is not output, as before. "MT125Stat: when=exit mixed=<n> mixed_nz=<n>" (pushes with the mix output, of
// them with a nonzero mix sample) is printed by an at_quick_exit handler, at 1 only.
static constexpr uint32_t M125_PORT_ATTRIBUTE_ID_GAIN       = 1;
static constexpr uint32_t M125_PORT_ATTRIBUTE_ID_AMBISONICS = 8;
static std::atomic<uint64_t> g_m125_mixed {0};
static std::atomic<uint64_t> g_m125_mixed_nz {0};

static void MT125PrintExitStat() {
	LOGF("MT125Stat: when=exit mixed=%" PRIu64 " mixed_nz=%" PRIu64 "\n", g_m125_mixed.load(std::memory_order_relaxed),
	     g_m125_mixed_nz.load(std::memory_order_relaxed));
}

static bool MT125On() {
	static const bool on = [] {
		const bool value = Common::EnvFlagOn("KYTY_M_T125");
		LOGF("MT125: mode=%d\n", value ? 1 : 0);
		if (value) {
			(void)std::at_quick_exit(MT125PrintExitStat);
		}
		return value;
	}();
	return on;
}

// T125: an object port that goes into the mix - the ports upstream c86c8b4d9 creates at all (port type 0x100, 48 kHz,
// mono float or mono s16), with PCM set. Other object ports (another 0x1xx type, rate or format) are not mixed.
static bool audioout2_m125_mixable(const AudioOut2PortStateEntry& state) {
	return state.port_type == 0x100u && state.sampling_freq == 48000u &&
	       (state.audio_format == AudioInternal::Format::FloatMono ||
	        state.audio_format == AudioInternal::Format::Signed16bitMono) &&
	       state.pcm_data != nullptr;
}

// T125: (left, right) of an object by its AMBISONICS - ordinary objects (UINT32_MAX) and FuMa W (64) at the centre,
// ACN/SN3D W (0) at full gain, the first-order Y component (2, 65) as left/right cardioids; any other channel has no
// stereo share (false).
static bool audioout2_m125_coefficients(uint32_t ambisonics, float* left, float* right) {
	constexpr float half_power = 0.70710678f;
	switch (ambisonics) {
		case UINT32_MAX:
		case 64:
			*left  = half_power;
			*right = half_power;
			return true;
		case 0:
			*left  = 1.0f;
			*right = 1.0f;
			return true;
		case 2:
		case 65:
			*left  = half_power;
			*right = -half_power;
			return true;
		default: return false;
	}
}

// T125: adds one object to the stereo mix (frames x 2 floats); the caller holds g_audioout2_port_mutex.
static void audioout2_m125_mix_object(std::vector<float>* mix, const AudioOut2PortStateEntry& object, uint32_t frames) {
	float left  = 0.0f;
	float right = 0.0f;
	if (!audioout2_m125_coefficients(object.m125_ambisonics, &left, &right)) {
		return;
	}
	left *= object.m125_gain;
	right *= object.m125_gain;
	const auto* bytes    = static_cast<const uint8_t*>(object.pcm_data);
	const bool  is_float = object.audio_format == AudioInternal::Format::FloatMono;
	const auto  count    = std::min(frames, object.samples_num);
	for (uint32_t frame = 0; frame < count; frame++) {
		float sample = 0.0f;
		if (is_float) {
			std::memcpy(&sample, bytes + static_cast<size_t>(frame) * sizeof(float), sizeof(float));
		} else {
			int16_t value = 0;
			std::memcpy(&value, bytes + static_cast<size_t>(frame) * sizeof(int16_t), sizeof(int16_t));
			sample = static_cast<float>(value) / 32768.0f;
		}
		(*mix)[static_cast<size_t>(frame) * 2] += sample * left;
		(*mix)[static_cast<size_t>(frame) * 2 + 1] += sample * right;
	}
}

// T125: the object mix device of a context and its frames (0 when the context has none).
static int audioout2_m125_mix_device(AudioOut2ContextHandle ctx, uint32_t* frames) {
	int handle = 0;
	g_audioout2_context_mutex.Lock();
	if (const auto* context = audioout2_find_context_locked(ctx); context != nullptr) {
		handle  = context->object_audio_handle;
		*frames = (context->num_grains == 0 ? 512u : context->num_grains);
	}
	g_audioout2_context_mutex.Unlock();
	return handle;
}

// T125 (KYTY_M_T125=1): audioout2_context_has_queueable_device plus the object mix device when an object of the
// context is mixed. Called without g_audioout2_context_mutex (AudioOut2ContextPush), as the original.
static bool audioout2_m125_has_queueable_device(AudioOut2ContextHandle ctx) {
	uint32_t   frames     = 512;
	const int  mix_handle = audioout2_m125_mix_device(ctx, &frames);
	Common::LockGuard lock(g_audioout2_port_mutex);
	for (const auto& state: g_audioout2_ports) {
		if (!state.used || state.context != ctx) {
			continue;
		}
		if (state.audio_handle > 0 && state.pcm_data != nullptr && AudioInternal::AudioOutHasDevice(state.audio_handle)) {
			return true;
		}
		if (mix_handle > 0 && audioout2_m125_mixable(state) && AudioInternal::AudioOutHasDevice(mix_handle)) {
			return true;
		}
	}
	return false;
}

// T125 (KYTY_M_T125=1): audioout2_queue_context_audio of 0 - the bus ports exactly as at 0 (selection, order,
// pointers), then the mix of the object ports as the last output of the batch.
static void audioout2_m125_queue_context_audio(AudioOut2ContextHandle ctx, bool blocking) {
	uint32_t  frames     = 512;
	const int mix_handle = audioout2_m125_mix_device(ctx, &frames);

	std::vector<AudioInternal::OutputParam> params;
	params.reserve(AudioInternal::OUT_PORTS_MAX);
	std::vector<float> mix;
	bool               mixed = false;

	g_audioout2_port_mutex.Lock();
	for (const auto& state: g_audioout2_ports) {
		if (state.used && state.context == ctx && state.audio_handle > 0 &&
		    state.pcm_data != nullptr && params.size() < AudioInternal::OUT_PORTS_MAX) {
			params.push_back(AudioInternal::OutputParam {state.audio_handle, state.pcm_data});
		}
	}
	if (mix_handle > 0) {
		for (const auto& state: g_audioout2_ports) {
			if (state.used && state.context == ctx && audioout2_m125_mixable(state)) {
				if (!mixed) {
					mix.assign(static_cast<size_t>(frames) * 2, 0.0f);
					mixed = true;
				}
				audioout2_m125_mix_object(&mix, state, frames);
			}
		}
	}
	g_audioout2_port_mutex.Unlock();

	if (mixed && params.size() < AudioInternal::OUT_PORTS_MAX) {
		params.push_back(AudioInternal::OutputParam {mix_handle, mix.data()});
		g_m125_mixed.fetch_add(1, std::memory_order_relaxed);
		if (std::any_of(mix.begin(), mix.end(), [](float v) { return v != 0.0f; })) {
			g_m125_mixed_nz.fetch_add(1, std::memory_order_relaxed);
		}
	}

	if (params.empty()) {
		return;
	}

	(void)AudioInternal::AudioOutOutputs(params.data(), static_cast<uint32_t>(params.size()), blocking);
}

// T125 (KYTY_M_T125=1): GAIN (id 1) and AMBISONICS (id 8) of an object port, read in the order of the array; an
// invalid value is not applied and the call still returns OK (the PCM of the call is set by the common path).
static void audioout2_m125_set_object_attributes(AudioOut2PortHandle port, const AudioOut2Attribute* attributes,
                                                 uint32_t num) {
	if (attributes == nullptr) {
		return;
	}
	Common::LockGuard lock(g_audioout2_port_mutex);
	auto*             state = audioout2_find_port_locked(port);
	if (state == nullptr || !audioout2_port_type_is_object(state->port_type)) {
		return;
	}
	const uint32_t channels = audioout2_data_format_channels(state->data_format);
	for (uint32_t i = 0; i < num; i++) {
		const auto& attribute = attributes[i];
		if (attribute.value == nullptr) {
			continue;
		}
		if (attribute.attribute_id == M125_PORT_ATTRIBUTE_ID_GAIN) {
			if (attribute.value_size != channels * sizeof(float)) {
				continue;
			}
			std::array<float, 16> gains {};
			std::memcpy(gains.data(), attribute.value, attribute.value_size);
			const bool valid = std::all_of(gains.begin(), gains.begin() + channels,
			                               [](float v) { return std::isfinite(v) && v >= 0.0f; });
			if (valid) {
				state->m125_gain = gains[0];
			}
		} else if (attribute.attribute_id == M125_PORT_ATTRIBUTE_ID_AMBISONICS) {
			if (attribute.value_size != sizeof(uint32_t)) {
				continue;
			}
			uint32_t ambisonics = 0;
			std::memcpy(&ambisonics, attribute.value, sizeof(ambisonics));
			if (ambisonics == UINT32_MAX || ambisonics <= 15 || (ambisonics >= 64 && ambisonics <= 99)) {
				state->m125_ambisonics = ambisonics;
			}
		}
	}
}

static bool audioout2_context_has_queueable_device(AudioOut2ContextHandle ctx) {
	if (MT125On()) {
		return audioout2_m125_has_queueable_device(ctx); // Track M, M8a (T125)
	}
	Common::LockGuard lock(g_audioout2_port_mutex);
	for (const auto& state: g_audioout2_ports) {
		if (state.used && state.context == ctx && state.audio_handle > 0 &&
		    state.pcm_data != nullptr && AudioInternal::AudioOutHasDevice(state.audio_handle)) {
			return true;
		}
	}
	return false;
}

static void audioout2_queue_context_audio(AudioOut2ContextHandle ctx, bool blocking) {
	if (MT125On()) {
		audioout2_m125_queue_context_audio(ctx, blocking); // Track M, M8a (T125): the bus ports as below + the mix
		return;
	}
	std::vector<AudioInternal::OutputParam> params;
	params.reserve(AudioInternal::OUT_PORTS_MAX);

	g_audioout2_port_mutex.Lock();
	// Track M, M6a (HPP-848, ROADMAP s122 item 767(i)), T125: measurement only - at this queued push every port
	// of the context with PCM (object ports and the others, the live control), object ports without PCM; no decision.
	if (DiagM5W2::On()) [[unlikely]] {
		for (const auto& state: g_audioout2_ports) {
			if (!state.used || state.context != ctx) {
				continue;
			}
			const bool object_port = audioout2_port_type_is_object(state.port_type);
			if (state.pcm_data != nullptr) {
				DiagM5W2::NoteAudioPort(object_port, state.pcm_data, state.data_format, state.samples_num);
			} else if (object_port) {
				DiagM5W2::NoteAudioObjectNoPcm();
			}
		}
	}
	for (const auto& state: g_audioout2_ports) {
		if (state.used && state.context == ctx && state.audio_handle > 0 &&
		    state.pcm_data != nullptr && params.size() < AudioInternal::OUT_PORTS_MAX) {
			params.push_back(AudioInternal::OutputParam {state.audio_handle, state.pcm_data});
		}
	}
	g_audioout2_port_mutex.Unlock();
	if (DiagM5W2::On()) [[unlikely]] {
		DiagM5W2::NoteAudioPush(); // M6a: the periodic "M5W2Stat:" line every 4096 queued pushes
	}

	if (params.empty()) {
		return;
	}

	(void)AudioInternal::AudioOutOutputs(params.data(), static_cast<uint32_t>(params.size()),
	                                     blocking);
}

static void audioout2_close_audio_handle(int audio_handle) {
	if (audio_handle > 0) {
		AudioInternal::AudioOutClose(audio_handle);
	}
}

int KYTY_SYSV_ABI AudioOut2Initialize() {
	PRINT_NAME();

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextResetParam(AudioOut2ContextParam* params) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(params == nullptr);

	std::memset(params, 0, sizeof(AudioOut2ContextParam));
	params->max_ports              = 256;
	params->max_object_ports       = 256;
	params->guarantee_object_ports = 0;
	params->queue_depth            = 4;
	params->num_grains             = 512;
	params->flags                  = 1;

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextQueryMemory(const AudioOut2ContextParam* params,
                                              size_t*                      memory_size) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(params == nullptr);
	EXIT_NOT_IMPLEMENTED(memory_size == nullptr);

	const auto queue_depth = (params->queue_depth == 0 ? 4u : params->queue_depth);
	*memory_size           = 0x10000u + static_cast<size_t>(queue_depth) * 0x590u;

	LOGF("\t memory_size = 0x%016" PRIx64 "\n", static_cast<uint64_t>(*memory_size));

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextCreate(const AudioOut2ContextParam* params, void* buffer,
                                         size_t buffer_size, AudioOut2ContextHandle* ctx) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(params == nullptr);
	EXIT_NOT_IMPLEMENTED(ctx == nullptr);

	*ctx = g_audioout2_next_context.fetch_add(1, std::memory_order_relaxed);

	g_audioout2_context_mutex.Lock();
	auto* state = audioout2_find_context_locked(0);
	if (state == nullptr) {
		for (auto& candidate: g_audioout2_contexts) {
			if (!candidate.used) {
				state = &candidate;
				break;
			}
		}
	}
	EXIT_NOT_IMPLEMENTED(state == nullptr);
	*state             = AudioOut2ContextState {};
	state->used        = true;
	state->handle      = *ctx;
	state->queue_depth = (params->queue_depth == 0 ? 4u : params->queue_depth);
	state->queued      = 0;
	state->num_grains  = (params->num_grains == 0 ? 512u : params->num_grains);
	state->last_update = LibKernel::KernelGetProcessTime();
	g_audioout2_context_mutex.Unlock();
	if (MT125On() && params->max_object_ports > 0) {
		// Track M, M8a (T125): the object mix device of the context, opened outside the lock; kept only if the
		// context still exists (a concurrent destroy closes nothing of it yet). A failed open leaves 0: no mix, OK.
		const uint32_t frames = (params->num_grains == 0 ? 512u : params->num_grains);
		const int      handle = AudioInternal::AudioOutOpen(AUDIO_OUT_PORT_TYPE_MAIN, frames, 48000,
		                                                    AudioInternal::Format::FloatStereo);
		bool           kept   = false;
		g_audioout2_context_mutex.Lock();
		if (auto* created = audioout2_find_context_locked(*ctx); created != nullptr) {
			created->object_audio_handle = handle;
			kept                         = true;
		}
		g_audioout2_context_mutex.Unlock();
		if (!kept) {
			audioout2_close_audio_handle(handle);
		}
	}

	LOGF("\t buffer      = 0x%016" PRIx64 "\n"
	     "\t buffer_size = 0x%016" PRIx64 "\n"
	     "\t ctx         = 0x%016" PRIx64 "\n"
	     "\t queue_depth = %" PRIu32 ", num_grains = %" PRIu32 "\n",
	     reinterpret_cast<uint64_t>(buffer), static_cast<uint64_t>(buffer_size), *ctx,
	     state->queue_depth, state->num_grains);

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextDestroy(AudioOut2ContextHandle ctx) {
	PRINT_NAME();
	LOGF("\t ctx = 0x%016" PRIx64 "\n", ctx);

	int object_audio_handle = 0; // Track M, M8a (T125): the object mix device of the context (0 at KYTY_M_T125=0)
	g_audioout2_context_mutex.Lock();
	if (auto* state = audioout2_find_context_locked(ctx); state != nullptr) {
		object_audio_handle = state->object_audio_handle;
		*state = AudioOut2ContextState {};
	}
	g_audioout2_context_mutex.Unlock();

	std::array<int, 256> audio_handles {};
	size_t               audio_handles_num = 0;

	g_audioout2_port_mutex.Lock();
	for (auto& port_state: g_audioout2_ports) {
		if (port_state.used && port_state.context == ctx) {
			if (port_state.audio_handle > 0 && audio_handles_num < audio_handles.size()) {
				audio_handles[audio_handles_num++] = port_state.audio_handle;
			}
			port_state = AudioOut2PortStateEntry {};
		}
	}
	g_audioout2_port_mutex.Unlock();

	for (size_t i = 0; i < audio_handles_num; i++) {
		audioout2_close_audio_handle(audio_handles[i]);
	}
	audioout2_close_audio_handle(object_audio_handle); // Track M, M8a (T125): nothing for 0

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextSetAttributes(AudioOut2ContextHandle    ctx,
                                                const AudioOut2Attribute* attributes,
                                                uint32_t                  num) {
	PRINT_NAME();
	LOGF("\t ctx = 0x%016" PRIx64 ", num = %" PRIu32 "\n", ctx, num);
	EXIT_NOT_IMPLEMENTED(num != 0 && attributes == nullptr);
	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextAdvance(AudioOut2ContextHandle ctx) {
	g_audioout2_context_mutex.Lock();
	if (auto* state = audioout2_find_context_locked(ctx); state != nullptr) {
		audioout2_update_context_locked(state);
	}
	g_audioout2_context_mutex.Unlock();

	return OK;
}

int KYTY_SYSV_ABI AudioOut2ContextPush(AudioOut2ContextHandle ctx, uint32_t blocking) {
	uint32_t sleep_micros = audioout2_grain_micros(512);
	static const bool            av_trace = Common::EnvFlagOn("KYTY_AV_TRACE");
	static std::atomic<uint64_t> av_calls {0};
	if (av_trace) {
		const auto n = av_calls.fetch_add(1, std::memory_order_relaxed) + 1;
		if (n <= 5 || (n % 1000) == 0) {
			LOGF("AvTrace: push ctx=0x%" PRIx64 " blocking=%u n=%" PRIu64 " tid=%d t=%" PRIu64 "\n", ctx, blocking, n,
			     Common::Thread::GetThreadIdUnique(), LibKernel::KernelGetProcessTime());
		}
	}

	// Track F, F20j3 (KYTY_DIAG_B32 W:audio, item 574(g)(1)): from the first full-queue pass to the return (destructor).
	Common::DiagB32::Mark b32;
	for (;;) {
		// Only a synchronous submission carrying PCM to a real device can rely on the SDL queue for
		// pacing. Async pushes must retain queue-depth backpressure, and a handle without PCM (or a
		// vibration/failed-open handle) has no downstream operation that can block this call.
		const bool use_device_clock =
		    blocking != 0 && audioout2_context_has_queueable_device(ctx);

		g_audioout2_context_mutex.Lock();
		if (auto* state = audioout2_find_context_locked(ctx); state != nullptr) {
			audioout2_update_context_locked(state);
			sleep_micros = audioout2_grain_micros(state->num_grains);
			if (state->queued < state->queue_depth || use_device_clock) {
				if (state->queued == 0) {
					state->last_update = LibKernel::KernelGetProcessTime();
				}
				if (state->queued < state->queue_depth) {
					state->queued++;
				}
				g_audioout2_context_mutex.Unlock();
				b32.End(0, false); // Track F, F20j3: the wait ends; the queueing below is not a wait
				audioout2_queue_context_audio(ctx, blocking != 0);
				return OK;
			}
		}
		g_audioout2_context_mutex.Unlock();

		if (blocking == 0) {
			return AUDIO_OUT2_ERROR_NOT_READY;
		}

		if (Common::DiagB32::g_on && !b32.Active()) [[unlikely]] {
			b32.BeginWReg(Common::DiagB32::Wait::Audio, &g_audioout2_context_mutex, 0, 0);
		}
		Common::Thread::SleepMicro(sleep_micros);
	}
}

int KYTY_SYSV_ABI AudioOut2ContextGetQueueLevel(AudioOut2ContextHandle ctx, uint32_t* queue_level,
                                                uint32_t* available_queues) {
	if (queue_level != nullptr) {
		*queue_level = 0;
	}
	if (available_queues != nullptr) {
		*available_queues = 4;
	}

	g_audioout2_context_mutex.Lock();
	if (auto* state = audioout2_find_context_locked(ctx); state != nullptr) {
		audioout2_update_context_locked(state);
		if (queue_level != nullptr) {
			*queue_level = state->queued;
		}
		if (available_queues != nullptr) {
			*available_queues =
			    (state->queued < state->queue_depth ? state->queue_depth - state->queued : 0);
		}
	}
	g_audioout2_context_mutex.Unlock();

	return OK;
}

int KYTY_SYSV_ABI AudioOut2PortCreate(AudioOut2ContextHandle ctx, const AudioOut2PortParam* params,
                                      AudioOut2PortHandle* port) {
	EXIT_NOT_IMPLEMENTED(params == nullptr);
	EXIT_NOT_IMPLEMENTED(port == nullptr);

	const auto next_port    = g_audioout2_next_port.fetch_add(1, std::memory_order_relaxed);
	const auto audio_format = audioout2_data_format_to_audio_format(params->data_format);
	const auto audio_type   = audioout2_port_type_to_audio_out_type(params->port_type);

	g_audioout2_context_mutex.Lock();
	const auto* context_state = audioout2_find_context_locked(ctx);
	if (context_state == nullptr) {
		g_audioout2_context_mutex.Unlock();
		return AUDIO_OUT2_ERROR_INVALID_PARAM;
	}
	const auto samples_num = context_state->num_grains == 0 ? 512u : context_state->num_grains;

	g_audioout2_port_mutex.Lock();
	AudioOut2PortStateEntry* port_state = nullptr;
	for (auto& candidate: g_audioout2_ports) {
		if (!candidate.used) {
			port_state = &candidate;
			break;
		}
	}
	if (port_state != nullptr) {
		*port_state               = AudioOut2PortStateEntry {};
		port_state->used          = true;
		port_state->handle        = next_port;
		port_state->context       = ctx;
		port_state->port_type     = params->port_type;
		port_state->data_format   = params->data_format;
		port_state->sampling_freq = params->sampling_freq;
		port_state->samples_num   = samples_num;
		port_state->audio_format  = audio_format;
	}
	g_audioout2_port_mutex.Unlock();
	g_audioout2_context_mutex.Unlock();

	if (port_state == nullptr) {
		return AUDIO_OUT2_ERROR_PORT_FULL;
	}

	int audio_handle = 0;

	if (audio_format != AudioInternal::Format::Unknown &&
	    !audioout2_port_type_is_object(params->port_type)) {
		audio_handle = AudioInternal::AudioOutOpen(audio_type, samples_num, params->sampling_freq,
		                                           audio_format);
	}

	g_audioout2_port_mutex.Lock();
	const bool reserved = port_state->used && port_state->handle == next_port;
	if (reserved) {
		port_state->audio_handle = audio_handle;
	}
	g_audioout2_port_mutex.Unlock();
	if (!reserved) {
		audioout2_close_audio_handle(audio_handle);
		return AUDIO_OUT2_ERROR_INVALID_PARAM;
	}

	*port = next_port;

	// Object ports are created by the hundred; log them sparsely but every device port.
	if (next_port <= 16 || (next_port % 600) == 0 || !audioout2_port_type_is_object(params->port_type)) {
		PRINT_NAME();
		LOGF("\t ctx           = 0x%016" PRIx64 "\n"
		     "\t port          = 0x%016" PRIx64 "\n"
		     "\t port_type     = %" PRIu16 "\n"
		     "\t data_format   = 0x%08" PRIx32 "\n"
		     "\t sampling_freq = %" PRIu32 "\n"
		     "\t flags         = 0x%08" PRIx32 "\n"
		     "\t user          = 0x%016" PRIx64 "\n"
		     "\t audio_handle  = %d\n",
		     ctx, *port, params->port_type, params->data_format, params->sampling_freq,
		     params->flags, static_cast<uint64_t>(params->user_handle), audio_handle);
	}

	return OK;
}

int KYTY_SYSV_ABI AudioOut2PortDestroy(AudioOut2PortHandle port) {
	PRINT_NAME();
	LOGF("\t port = 0x%016" PRIx64 "\n", port);

	int audio_handle = 0;
	g_audioout2_port_mutex.Lock();
	if (auto* state = audioout2_find_port_locked(port); state != nullptr) {
		audio_handle = state->audio_handle;
		*state       = AudioOut2PortStateEntry {};
	}
	g_audioout2_port_mutex.Unlock();

	audioout2_close_audio_handle(audio_handle);

	return OK;
}

int KYTY_SYSV_ABI AudioOut2PortSetAttributes(AudioOut2PortHandle       port,
                                             const AudioOut2Attribute* attributes, uint32_t num) {
	EXIT_NOT_IMPLEMENTED(num != 0 && attributes == nullptr);
	if (MT125On()) {
		audioout2_m125_set_object_attributes(port, attributes, num); // Track M, M8a (T125): GAIN, AMBISONICS
	}

	const void* pcm_data = nullptr;
	bool        has_pcm  = false;
	for (uint32_t i = 0; i < num; i++) {
		if (attributes[i].attribute_id == AUDIO_OUT2_PORT_ATTRIBUTE_ID_PCM &&
		    attributes[i].value != nullptr && attributes[i].value_size >= sizeof(AudioOut2Pcm)) {
			AudioOut2Pcm pcm {};
			std::memcpy(&pcm, attributes[i].value, sizeof(AudioOut2Pcm));
			pcm_data = pcm.data;
			has_pcm  = true;
		}
	}

	if (has_pcm) {
		g_audioout2_port_mutex.Lock();
		if (auto* state = audioout2_find_port_locked(port); state != nullptr) {
			state->pcm_data = pcm_data;
		}
		g_audioout2_port_mutex.Unlock();
	}

	return OK;
}

int KYTY_SYSV_ABI AudioOut2PortGetState(AudioOut2PortHandle port, AudioOut2PortState* state) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(state == nullptr);

	std::memset(state, 0, sizeof(AudioOut2PortState));
	state->output          = 1;
	state->num_channels    = 2;
	state->volume          = 127;
	state->reroute_counter = 0;
	state->flags           = 0;

	g_audioout2_port_mutex.Lock();
	if (auto* port_state = audioout2_find_port_locked(port); port_state != nullptr) {
		state->num_channels = audioout2_data_format_channels(port_state->data_format);
	}
	g_audioout2_port_mutex.Unlock();

	// LOGF("\t port = 0x%016" PRIx64 "\n", port);
	// LOGF("\t num_channels = %" PRIu8 "\n", state->num_channels);

	return OK;
}

int KYTY_SYSV_ABI AudioOut2GetSystemState(AudioOut2SystemState* state) {
	PRINT_NAME();
	EXIT_NOT_IMPLEMENTED(state == nullptr);
	std::memset(state, 0, sizeof(AudioOut2SystemState));
	return OK;
}

int KYTY_SYSV_ABI AudioOut2UserCreate(uint32_t user_id, AudioOut2UserHandle* handle) {
	PRINT_NAME();
	EXIT_NOT_IMPLEMENTED(handle == nullptr);
	*handle = static_cast<AudioOut2UserHandle>(
	    g_audioout2_next_user.fetch_add(1, std::memory_order_relaxed));
	LOGF("\t user_id = %" PRIu32 ", handle = 0x%016" PRIx64 "\n", user_id,
	     static_cast<uint64_t>(*handle));
	return OK;
}

int KYTY_SYSV_ABI AudioOut2UserDestroy(AudioOut2UserHandle handle) {
	PRINT_NAME();
	LOGF("\t handle = 0x%016" PRIx64 "\n", static_cast<uint64_t>(handle));
	return OK;
}

size_t KYTY_SYSV_ABI AudioOut2GetSpeakerArrayMemorySize(uint32_t num_speakers, uint8_t is_3d,
                                                        uint8_t is_ambisonics) {
	PRINT_NAME();

	const auto speakers = std::clamp<uint32_t>(num_speakers, 1, 32);
	const auto size = static_cast<size_t>(0x400 + speakers * (is_ambisonics != 0 ? 0x100 : 0x40) +
	                                      (is_3d != 0 ? 0x200 : 0));

	LOGF("\t num_speakers  = %" PRIu32 "\n"
	     "\t is_3d         = %" PRIu8 "\n"
	     "\t is_ambisonics = %" PRIu8 "\n"
	     "\t memory_size   = 0x%016" PRIx64 "\n",
	     num_speakers, is_3d, is_ambisonics, static_cast<uint64_t>(size));

	return size;
}

int KYTY_SYSV_ABI AudioOut2SpeakerArrayCreate(AudioOut2SpeakerArrayHandle* handle,
                                              const void* vbap_params, const void* ambi_params) {
	PRINT_NAME();
	EXIT_NOT_IMPLEMENTED(handle == nullptr);

	*handle = nullptr;

	g_audioout2_speaker_array_mutex.Lock();
	for (auto& state: g_audioout2_speaker_arrays) {
		if (!state.used) {
			state              = AudioOut2SpeakerArrayState {};
			state.used         = true;
			state.handle       = &state;
			state.num_speakers = 2;
			*handle            = state.handle;
			break;
		}
	}
	g_audioout2_speaker_array_mutex.Unlock();

	LOGF("\t handle      = 0x%016" PRIx64 "\n"
	     "\t vbap_params = 0x%016" PRIx64 "\n"
	     "\t ambi_params = 0x%016" PRIx64 "\n",
	     reinterpret_cast<uint64_t>(*handle), reinterpret_cast<uint64_t>(vbap_params),
	     reinterpret_cast<uint64_t>(ambi_params));

	return (*handle != nullptr ? OK : AUDIO_OUT2_ERROR_PORT_FULL);
}

int KYTY_SYSV_ABI AudioOut2SpeakerArrayDestroy(AudioOut2SpeakerArrayHandle handle) {
	PRINT_NAME();
	LOGF("\t handle = 0x%016" PRIx64 "\n", reinterpret_cast<uint64_t>(handle));

	g_audioout2_speaker_array_mutex.Lock();
	for (auto& state: g_audioout2_speaker_arrays) {
		if (state.used && state.handle == handle) {
			state = AudioOut2SpeakerArrayState {};
			break;
		}
	}
	g_audioout2_speaker_array_mutex.Unlock();

	return OK;
}

int KYTY_SYSV_ABI AudioOut2GetSpeakerArrayCoefficients(
    AudioOut2SpeakerArrayHandle handle, AudioOut2Position pos, float spread, float* coefficients,
    uint32_t num_coefficients, uint8_t height_aware, float downmix_spread_radius) {
	PRINT_NAME();
	EXIT_NOT_IMPLEMENTED(coefficients == nullptr && num_coefficients != 0);

	if (coefficients != nullptr) {
		std::fill(coefficients, coefficients + num_coefficients, 0.0f);
		if (num_coefficients > 0) {
			coefficients[0] = 1.0f;
		}
		if (num_coefficients > 1) {
			coefficients[1] = 1.0f;
		}
	}

	LOGF("\t handle = 0x%016" PRIx64 ", coeffs = %" PRIu32
	     ", pos = (%f, %f, %f), spread = %f, height = %" PRIu8 ", downmix = %f\n",
	     reinterpret_cast<uint64_t>(handle), num_coefficients, static_cast<double>(pos.x),
	     static_cast<double>(pos.y), static_cast<double>(pos.z), static_cast<double>(spread),
	     height_aware, static_cast<double>(downmix_spread_radius));

	return OK;
}

int KYTY_SYSV_ABI AudioOut2GetSpeakerArrayAmbisonicsCoefficients(AudioOut2SpeakerArrayHandle handle,
                                                                 uint32_t ambisonics_channel,
                                                                 float*   coefficients,
                                                                 uint32_t num_coefficients) {
	PRINT_NAME();
	EXIT_NOT_IMPLEMENTED(coefficients == nullptr && num_coefficients != 0);

	if (coefficients != nullptr) {
		std::fill(coefficients, coefficients + num_coefficients, 0.0f);
		if (num_coefficients > 0) {
			coefficients[0] =
			    (ambisonics_channel == 0 || ambisonics_channel == 64 ? 0.70710677f : 1.0f);
		}
	}

	LOGF("\t handle = 0x%016" PRIx64 ", channel = %" PRIu32 ", coeffs = %" PRIu32 "\n",
	     reinterpret_cast<uint64_t>(handle), ambisonics_channel, num_coefficients);

	return OK;
}

int KYTY_SYSV_ABI AudioOut2GetSpeakerInfo(AudioOut2SpeakerInfo* info, uint32_t flags) {
	EXIT_NOT_IMPLEMENTED(info == nullptr);
	std::memset(info, 0, sizeof(AudioOut2SpeakerInfo));
	info->type             = 0;
	info->available_bits   = 0x03;
	info->flags            = 0;
	info->speaker_angle[0] = {-30, 0};
	info->speaker_angle[1] = {30, 0};

	return OK;
}

int KYTY_SYSV_ABI AudioOut2SetSystemDebugState(const AudioOut2SystemDebugStateParam* param) {
	PRINT_NAME();
	LOGF("\t param = 0x%016" PRIx64 "\n", reinterpret_cast<uint64_t>(param));
	return OK;
}

int KYTY_SYSV_ABI AudioOut2Set3DLatency(uint32_t user_id, uint32_t output, uint32_t latency_us) {
	// Not sure

	PRINT_NAME();
	LOGF("\t user_id = %" PRIu32 ", output = %" PRIu32 ", latency_us = %" PRIu32 "\n", user_id,
	     output, latency_us);

	if (output > AUDIO_OUT2_MASTERING_OUTPUT_RECORDING) {
		return AUDIO_OUT2_ERROR_INVALID_PARAM;
	}

	g_audioout2_latency_mutex.Lock();
	AudioOut2LatencyState* free_state = nullptr;
	for (auto& state: g_audioout2_latencies) {
		if (state.used && state.user_id == user_id && state.output == output) {
			state.latency_us = latency_us;
			g_audioout2_latency_mutex.Unlock();
			return OK;
		}
		if (!state.used && free_state == nullptr) {
			free_state = &state;
		}
	}

	if (free_state != nullptr) {
		*free_state = AudioOut2LatencyState {true, user_id, output, latency_us};
	}
	g_audioout2_latency_mutex.Unlock();

	return (free_state != nullptr ? OK : AUDIO_OUT2_ERROR_PORT_FULL);
}

int KYTY_SYSV_ABI AudioOut2MasteringInit(uint32_t flags) {
	PRINT_NAME();
	LOGF("\t flags = 0x%08" PRIx32 "\n", flags);
	return OK;
}

int KYTY_SYSV_ABI AudioOut2MasteringSetParam(const AudioOut2MasteringParamsHeader* param,
                                             uint32_t output, uint32_t flags) {
	PRINT_NAME();
	LOGF("\t param = 0x%016" PRIx64 ", output = %" PRIu32 ", flags = 0x%08" PRIx32 "\n",
	     reinterpret_cast<uint64_t>(param), output, flags);
	return OK;
}

int KYTY_SYSV_ABI AudioOut2MasteringGetState(AudioOut2MasteringStatesHeader* state, uint32_t output,
                                             AudioOut2UserHandle user) {
	PRINT_NAME();
	LOGF("\t state = 0x%016" PRIx64 ", output = %" PRIu32 ", user = 0x%016" PRIx64 "\n",
	     reinterpret_cast<uint64_t>(state), output, static_cast<uint64_t>(user));

	if (state == nullptr) {
		return AUDIO_OUT2_ERROR_MASTERING_INVALID_API_PARAM;
	}

	const auto states_id = state->states_id;
	switch (states_id) {
		case AUDIO_OUT2_MASTERING_STATES_ID_DEFAULT: {
			auto* full_state = reinterpret_cast<AudioOut2MasteringStates*>(state);
			std::memset(full_state, 0, sizeof(AudioOut2MasteringStates));
			full_state->states_header.states_id = AUDIO_OUT2_MASTERING_STATES_ID_DEFAULT;
			full_state->compressor_states.descriptor.id =
			    AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_COMPRESSOR_DEFAULT;
			full_state->compressor_states.descriptor.size =
			    sizeof(AudioOut2MasteringCompressorStates);
			full_state->limiter_states.descriptor.id =
			    AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_LIMITER_DEFAULT;
			full_state->limiter_states.descriptor.size = sizeof(AudioOut2MasteringLimiterStates);
			return OK;
		}
		case AUDIO_OUT2_MASTERING_STATES_ID_V2: {
			auto* full_state = reinterpret_cast<AudioOut2MasteringStatesV2*>(state);
			std::memset(full_state, 0, sizeof(AudioOut2MasteringStatesV2));
			full_state->states_header.states_id = AUDIO_OUT2_MASTERING_STATES_ID_V2;
			full_state->compressor_states.descriptor.id =
			    AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_COMPRESSOR_V2;
			full_state->compressor_states.descriptor.size =
			    sizeof(AudioOut2MasteringCompressorStatesV2);
			full_state->limiter_states.descriptor.id =
			    AUDIO_OUT2_MASTERING_STATES_STRUCT_ID_LIMITER_DEFAULT;
			full_state->limiter_states.descriptor.size = sizeof(AudioOut2MasteringLimiterStates);
			return OK;
		}
		default: return AUDIO_OUT2_ERROR_MASTERING_INVALID_STATES_ID;
	}
}

int KYTY_SYSV_ABI AudioOut2MasteringTerm() {
	PRINT_NAME();
	return OK;
}

} // namespace AudioOut2
} // namespace Libs::Audio
