#include "libs/controller.h"

#include "SDL.h"
#include "common/assert.h"
#include "common/common.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/stringUtils.h"
#include "common/threads.h"
#include "kernel/pthread.h"
#include "libs/errno.h"
#include "libs/libs.h"
#include "libs/padData.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <mutex>
#include <vector>

namespace Libs::Controller {

LIB_NAME("Pad", "Pad");

constexpr int PAD_ERROR_INVALID_ARG    = -2137915391; /* 0x80920001 */
constexpr int PAD_ERROR_INVALID_HANDLE = -2137915389; /* 0x80920003 */

constexpr uint32_t RUMBLE_DURATION_MS = 0xffff;
constexpr uint32_t RELEASE_FLUSH_MS   = 50;

struct PadControllerInformation {
	float    touch_pixel_density;
	uint16_t touch_resolution_x;
	uint16_t touch_resolution_y;
	uint8_t  stick_dead_zone_left;
	uint8_t  stick_dead_zone_right;
	uint8_t  connection_type;
	uint8_t  connected_count;
	bool     connected;
	int      device_class;
	uint8_t  reserve[8];
};

struct PadLightBarParam {
	uint8_t r;
	uint8_t g;
	uint8_t b;
	uint8_t reserve;
};

struct PadVibrationParam {
	uint8_t large_motor;
	uint8_t small_motor;
};

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

struct DualSenseEffects {
	uint8_t enable_bits;
	uint8_t reserve[9];
	uint8_t right_trigger[11];
	uint8_t left_trigger[11];
};

static_assert(sizeof(DualSenseEffects) == 32);

// Haptic PCM of the guest's vibration port, streamed to the pad. A USB DualSense is a 4-channel
// audio device whose channels 3/4 drive the voice coils: that is how the console feels, and it
// needs no resampling since both sides run at 48 kHz. Over Bluetooth the pad exposes no such
// device and takes haptics only through HID output report 0x32, which Windows cannot send at its
// declared length (docs/local-session-44.md), so a Bluetooth pad simply stays quiet.
class HapticsOutput {
public:
	HapticsOutput() = default;
	~HapticsOutput() { Stop(); }

	KYTY_CLASS_NO_COPY(HapticsOutput);

	void Start();
	void Stop();
	void Push(const void* pcm, uint32_t frames, uint32_t channels, bool is_float, uint32_t freq);

private:
	static constexpr uint32_t FREQ     = 48000;
	static constexpr uint32_t CHANNELS = 4;
	static constexpr uint64_t RETRY_US = 3000000;
	// Keep at most ~60 ms queued so the haptics stay in step with the picture.
	static constexpr uint32_t MAX_QUEUED = FREQ * CHANNELS * sizeof(int16_t) * 60 / 1000;

	static uint64_t NowUs();
	bool            OpenLocked();
	void            CloseLocked();

	std::mutex           m_mutex;
	SDL_AudioDeviceID    m_device   = 0;
	uint64_t             m_retry_us = 0;
	uint64_t             m_pushes   = 0;
	float                m_gain     = 1.0f;
	bool                 m_enabled  = true;
	std::vector<int16_t> m_buffer;
};

static HapticsOutput* g_haptics = nullptr;

uint64_t HapticsOutput::NowUs() {
	return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::microseconds>(
	                                 std::chrono::steady_clock::now().time_since_epoch())
	                                 .count());
}

void HapticsOutput::Start() {
	if (const char* value = std::getenv("KYTY_HAPTICS"); value != nullptr && value[0] == '0') {
		m_enabled = false;
		LOGF("Haptics: disabled by KYTY_HAPTICS=0\n");
		return;
	}
	if (const char* gain = std::getenv("KYTY_HAPTICS_GAIN"); gain != nullptr) {
		m_gain = std::clamp(static_cast<float>(std::atof(gain)), 0.0f, 8.0f);
	}
}

void HapticsOutput::Stop() {
	std::lock_guard lock(m_mutex);
	m_enabled = false;
	CloseLocked();
}

bool HapticsOutput::OpenLocked() {
	if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {
		return false;
	}
	SDL_AudioSpec want {};
	want.freq     = FREQ;
	want.format   = AUDIO_S16SYS;
	want.channels = CHANNELS;
	want.samples  = 512;
	SDL_AudioSpec have {};
	for (int i = 0; i < SDL_GetNumAudioDevices(0); i++) {
		const char* name = SDL_GetAudioDeviceName(i, 0);
		if (name == nullptr || (SDL_strcasestr(name, "DualSense") == nullptr &&
		                        SDL_strcasestr(name, "Wireless Controller") == nullptr)) {
			continue;
		}
		m_device = SDL_OpenAudioDevice(name, 0, &want, &have, 0);
		if (m_device == 0) {
			LOGF("Haptics: pad audio device \"%s\" failed: %s\n", name, SDL_GetError());
			continue;
		}
		SDL_PauseAudioDevice(m_device, 0);
		LOGF("Haptics: pad audio device \"%s\" opened (%d Hz, %u ch)\n", name, have.freq,
		     have.channels);
		return true;
	}
	return false;
}

void HapticsOutput::CloseLocked() {
	if (m_device != 0) {
		SDL_ClearQueuedAudio(m_device);
		SDL_CloseAudioDevice(m_device);
		m_device = 0;
	}
}

void HapticsOutput::Push(const void* pcm, uint32_t frames, uint32_t channels, bool is_float,
                         uint32_t freq) {
	if (pcm == nullptr || frames == 0 || channels == 0 || freq != FREQ) {
		return;
	}

	std::lock_guard lock(m_mutex);
	if (!m_enabled) {
		return;
	}
	if (m_device == 0) {
		// Only a USB pad has this device; retry rarely, one may be plugged in later.
		const auto now = NowUs();
		if (m_retry_us != 0 && now - m_retry_us < RETRY_US) {
			return;
		}
		m_retry_us = now;
		if (!OpenLocked()) {
			return;
		}
	}

	const uint32_t left  = channels >= 4 ? 2 : 0;
	const uint32_t right = channels >= 4 ? 3 : (channels >= 2 ? 1 : 0);
	m_buffer.assign(size_t {frames} * CHANNELS, 0);
	for (uint32_t i = 0; i < frames; i++) {
		float l = 0.0f;
		float r = 0.0f;
		if (is_float) {
			const auto* s = static_cast<const float*>(pcm) + size_t {i} * channels;
			l             = s[left];
			r             = s[right];
		} else {
			const auto* s = static_cast<const int16_t*>(pcm) + size_t {i} * channels;
			l             = static_cast<float>(s[left]) / 32768.0f;
			r             = static_cast<float>(s[right]) / 32768.0f;
		}
		// Channels 1/2 are the pad speaker, 3/4 the voice coils.
		m_buffer[i * CHANNELS + 2] =
		    static_cast<int16_t>(std::lround(std::clamp(l * m_gain, -1.0f, 1.0f) * 32767.0f));
		m_buffer[i * CHANNELS + 3] =
		    static_cast<int16_t>(std::lround(std::clamp(r * m_gain, -1.0f, 1.0f) * 32767.0f));
	}

	if (SDL_GetQueuedAudioSize(m_device) > MAX_QUEUED) {
		SDL_ClearQueuedAudio(m_device);
	}
	if (SDL_QueueAudio(m_device, m_buffer.data(),
	                   static_cast<uint32_t>(m_buffer.size() * sizeof(int16_t))) < 0) {
		LOGF("Haptics: pad audio queue failed: %s\n", SDL_GetError());
		CloseLocked();
		return;
	}
	if (m_pushes++ == 0) {
		LOGF("Haptics: streaming to the pad haptics, gain %.2f\n", m_gain);
	}
}


struct ControllerState {
	struct Touch {
		uint8_t  id   = 0;
		bool     down = false;
		uint16_t x    = 0;
		uint16_t y    = 0;
	};

	uint64_t time                                  = 0;
	uint32_t buttons                               = 0;
	int      axes[static_cast<int>(Axis::AxisMax)] = {128, 128, 128, 128, 0, 0};
	Touch    touch[2];
	float    motion_pitch = 0.0f;
	bool     motion_enabled = true;
	bool     motion_shake = false;
	// Real pad sensors: acceleration in G, angular velocity in rad/s, integrated orientation.
	bool     real_motion         = false;
	float    real_accel[3]       = {0.0f, 0.0f, 0.0f};
	float    real_gyro[3]        = {0.0f, 0.0f, 0.0f};
	float    real_orientation[4] = {0.0f, 0.0f, 0.0f, 1.0f}; // x, y, z, w
};

class GameController {
public:
	GameController() = default;

	KYTY_CLASS_NO_COPY(GameController);

	void Connect(int id);
	void Disconnect(int id);
	void Button(int id, uint32_t button, bool down);
	void Axis(int id, Axis axis, int value);
	void RightStick(int id, int x, int y);
	void TouchPad(int id, int finger, bool down, float x, float y);
	void MotionPitch(int id, float radians);
	void MotionShake(int id, bool down);
	void MotionSensorState(bool enable);
	void MotionSample(int id, MotionSensor sensor, const float* data, uint64_t timestamp_us);
	void ResetOrientation();
	void ResetInputState();
	void ReleaseHostPads();
	void GetConnectionInfo(bool* flag, int* count);
	void SetVibration(uint8_t large_motor, uint8_t small_motor);
	void SetLightBar(uint8_t r, uint8_t g, uint8_t b);
	bool SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent);
	void ReadState(ControllerState* state, bool* flag, int* count);
	int  ReadStates(ControllerState* states, int states_num, bool* flag, int* count);

private:
	static constexpr uint32_t STATES_MAX = 64;

	void RefreshMotion();
	void CheckActive();
	void AddState();

	Common::Mutex    m_mutex;
	std::vector<int> m_connected_ids;
	int              m_active_id       = -1;
	bool             m_connected       = false;
	int              m_connected_count = 0;
	ControllerState  m_state;
	ControllerState  m_states[STATES_MAX];
	bool             m_obtained[STATES_MAX] {};
	uint32_t         m_states_num    = 0;
	uint32_t         m_first_state   = 0;
	uint8_t          m_next_touch_id = 1;
	float            m_orientation[4] = {0.0f, 0.0f, 0.0f, 1.0f}; // integrated gyro, x y z w
	uint64_t         m_gyro_timestamp = 0;
};

static GameController* g_controller = nullptr;

static void pad_fill_data(PadData* data, const ControllerState& state, bool connected,
                          int connected_count) {
	EXIT_IF(data == nullptr);

	std::memset(data, 0, sizeof(*data));

	data->buttons           = state.buttons;
	data->left_stick_x      = state.axes[static_cast<int>(Axis::LeftX)];
	data->left_stick_y      = state.axes[static_cast<int>(Axis::LeftY)];
	data->right_stick_x     = state.axes[static_cast<int>(Axis::RightX)];
	data->right_stick_y     = state.axes[static_cast<int>(Axis::RightY)];
	data->analog_buttons_l2 = state.axes[static_cast<int>(Axis::TriggerLeft)];
	data->analog_buttons_r2 = state.axes[static_cast<int>(Axis::TriggerRight)];
	data->orientation_w     = 1.0f;
	const bool keyboard_motion = state.motion_shake || state.motion_pitch != 0.0f;
	if (state.motion_enabled && state.real_motion && !keyboard_motion) {
		data->orientation_x      = state.real_orientation[0];
		data->orientation_y      = state.real_orientation[1];
		data->orientation_z      = state.real_orientation[2];
		data->orientation_w      = state.real_orientation[3];
		data->acceleration_x     = state.real_accel[0];
		data->acceleration_y     = state.real_accel[1];
		data->acceleration_z     = state.real_accel[2];
		data->angular_velocity_x = state.real_gyro[0];
		data->angular_velocity_y = state.real_gyro[1];
		data->angular_velocity_z = state.real_gyro[2];
	} else if (state.motion_enabled) {
		// Virtual keyboard motion, not a real device sensor sample. A static tilt has
		// unit gravity and zero angular velocity. Shake adds a 4 Hz translation/rotation.
		float pitch = state.motion_pitch;
		float linear_z = 0.0f;
		if (state.motion_shake) {
			constexpr float omega = 25.13274123f;
			const float phase = float(state.time % 250000) * (omega / 1000000.0f);
			pitch += 0.25f * std::sin(phase);
			linear_z = 3.0f * std::sin(phase);
			data->angular_velocity_x = 0.25f * omega * std::cos(phase);
		}
		data->orientation_x = std::sin(pitch * 0.5f);
		data->orientation_w = std::cos(pitch * 0.5f);
		data->acceleration_y = -std::cos(pitch);
		data->acceleration_z = std::sin(pitch) + linear_z;
	}
	for (const auto& touch: state.touch) {
		if (touch.down) {
			auto& output = data->touch_data.touch[data->touch_data.touch_num++];
			output.x     = touch.x;
			output.y     = touch.y;
			output.id    = touch.id;
		}
	}
	data->connected              = connected;
	data->timestamp              = state.time;
	data->connected_count        = static_cast<uint8_t>(std::min(connected_count, 255));
	data->device_unique_data_len = 0;
}

static bool trigger_effect_zones(uint8_t* effect, const uint8_t* strengths, uint8_t type,
                                 uint8_t frequency = 0) {
	uint16_t active = 0;
	uint32_t packed = 0;
	for (int i = 0; i < 10; i++) {
		if (strengths[i] > 8) {
			return false;
		}
		if (strengths[i] != 0) {
			active |= static_cast<uint16_t>(1u << i);
			packed |= static_cast<uint32_t>(strengths[i] - 1u) << (3 * i);
		}
	}

	effect[0] = active != 0 && (type != 0x26 || frequency != 0) ? type : 0x05;
	effect[1] = static_cast<uint8_t>(active);
	effect[2] = static_cast<uint8_t>(active >> 8u);
	effect[3] = static_cast<uint8_t>(packed);
	effect[4] = static_cast<uint8_t>(packed >> 8u);
	effect[5] = static_cast<uint8_t>(packed >> 16u);
	effect[6] = static_cast<uint8_t>(packed >> 24u);
	effect[9] = frequency;
	return true;
}

static bool trigger_effect_to_dualsense(const PadTriggerEffectCommand& command, uint8_t* effect) {
	std::memset(effect, 0, 11);
	effect[0] = 0x05;

	uint8_t strengths[10] = {};
	switch (command.mode) {
		case 0: return true;
		case 1:
			if (command.data[0] > 9 || command.data[1] > 8) {
				return false;
			}
			std::fill(strengths + command.data[0], strengths + 10, command.data[1]);
			return trigger_effect_zones(effect, strengths, 0x21);
		case 2: {
			const auto start    = command.data[0];
			const auto end      = command.data[1];
			const auto strength = command.data[2];
			if (start < 2 || start > 7 || end <= start || end > 8 || strength > 8) {
				return false;
			}
			if (strength == 0) {
				return true;
			}
			const uint16_t zones = static_cast<uint16_t>((1u << start) | (1u << end));
			effect[0]            = 0x25;
			effect[1]            = static_cast<uint8_t>(zones);
			effect[2]            = static_cast<uint8_t>(zones >> 8u);
			effect[3]            = strength - 1u;
			return true;
		}
		case 3:
			if (command.data[0] > 9 || command.data[1] > 8) {
				return false;
			}
			std::fill(strengths + command.data[0], strengths + 10, command.data[1]);
			return trigger_effect_zones(effect, strengths, 0x26, command.data[2]);
		case 4: return trigger_effect_zones(effect, command.data, 0x21);
		case 5: {
			const int start          = command.data[0];
			const int end            = command.data[1];
			const int start_strength = command.data[2];
			const int end_strength   = command.data[3];
			if (start > 8 || end <= start || end > 9 || start_strength < 1 || start_strength > 8 ||
			    end_strength < 1 || end_strength > 8) {
				return false;
			}
			for (int i = start; i < 10; i++) {
				const int delta  = (end_strength - start_strength) * (i - start);
				const int length = end - start;
				strengths[i]     = static_cast<uint8_t>(
				    i >= end ? end_strength
				             : start_strength +
				                   (delta + (delta < 0 ? -length / 2 : length / 2)) / length);
			}
			return trigger_effect_zones(effect, strengths, 0x21);
		}
		case 6: return trigger_effect_zones(effect, command.data + 1, 0x26, command.data[0]);
		default: return false;
	}
}

void Initialize() {
	EXIT_IF(g_controller != nullptr);

	g_haptics = new HapticsOutput;
	g_haptics->Start();
	g_controller = new GameController;
	g_controller->Connect(HOST_INPUT_CONTROLLER_ID);
}

void Shutdown() {
	EmergencyShutdown();
	delete g_controller;
	g_controller = nullptr;
	delete g_haptics;
	g_haptics = nullptr;
}

void EmergencyShutdown() {
	if (g_haptics != nullptr) {
		g_haptics->Stop();
	}
	if (g_controller != nullptr) {
		g_controller->ReleaseHostPads();
	}
}

void GameController::Connect(int id) {
	Common::LockGuard lock(m_mutex);

	if (std::find(m_connected_ids.begin(), m_connected_ids.end(), id) != m_connected_ids.end()) {
		return;
	}

	m_connected_ids.push_back(id);

	CheckActive();
}

void GameController::Disconnect(int id) {
	Common::LockGuard lock(m_mutex);

	const auto it = std::find(m_connected_ids.begin(), m_connected_ids.end(), id);
	EXIT_IF(it == m_connected_ids.end());

	m_connected_ids.erase(it);

	CheckActive();
}

void GameController::CheckActive() {
	int  new_active_id = -1;
	bool new_connected = false;

	if (!m_connected_ids.empty()) {
		new_active_id = m_connected_ids[0];
		for (const auto id: m_connected_ids) {
			if (id != HOST_INPUT_CONTROLLER_ID) {
				new_active_id = id;
				break;
			}
		}
		new_connected = true;
	}

	if (m_connected == new_connected && m_active_id == new_active_id) {
		return;
	}
	if (!m_connected && new_connected) {
		m_connected_count++;
	}
	m_active_id     = new_active_id;
	m_connected     = new_connected;
	m_state         = {};
	m_states_num    = 0;
	m_first_state   = 0;
	m_next_touch_id = 1;
	m_orientation[0] = m_orientation[1] = m_orientation[2] = 0.0f;
	m_orientation[3] = 1.0f;
	m_gyro_timestamp = 0;
}

void GameController::AddState() {
	if (m_states_num >= STATES_MAX) {
		m_states_num  = STATES_MAX - 1;
		m_first_state = (m_first_state + 1) % STATES_MAX;
	}

	const auto index  = (m_first_state + m_states_num) % STATES_MAX;
	m_states[index]   = m_state;
	m_obtained[index] = false;
	m_states_num++;
}

void GameController::Button(int id, uint32_t button, bool down) {
	Common::LockGuard lock(m_mutex);

	// The keyboard shares the player-1 pad with the active gamepad.
	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		m_state.time = LibKernel::KernelGetProcessTime();

		m_state.buttons = down ? m_state.buttons | button : m_state.buttons & ~button;

		AddState();
	}
}

void GameController::Axis(int id, Controller::Axis axis, int value) {
	Common::LockGuard lock(m_mutex);

	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		m_state.time = LibKernel::KernelGetProcessTime();

		int axis_id = static_cast<int>(axis);

		EXIT_IF(axis_id < 0 || axis_id >= static_cast<int>(Controller::Axis::AxisMax));

		m_state.axes[axis_id] = value;

		uint32_t trigger = 0;
		if (axis == Controller::Axis::TriggerLeft) {
			trigger = PAD_BUTTON_L2;
		} else if (axis == Controller::Axis::TriggerRight) {
			trigger = PAD_BUTTON_R2;
		}
		if (trigger != 0) {
			m_state.buttons = value > 0 ? m_state.buttons | trigger : m_state.buttons & ~trigger;
		}

		AddState();
	}
}

void GameController::RightStick(int id, int x, int y) {
	Common::LockGuard lock(m_mutex);

	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		m_state.time                                 = LibKernel::KernelGetProcessTime();
		m_state.axes[static_cast<int>(Axis::RightX)] = x;
		m_state.axes[static_cast<int>(Axis::RightY)] = y;
		AddState();
	}
}

void GameController::TouchPad(int id, int finger, bool down, float x, float y) {
	if (finger < 0 || finger >= 2) {
		return;
	}

	Common::LockGuard lock(m_mutex);
	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		auto& touch  = m_state.touch[finger];
		m_state.time = LibKernel::KernelGetProcessTime();
		if (down && !touch.down) {
			touch.id        = m_next_touch_id;
			m_next_touch_id = m_next_touch_id == 127 ? 1 : m_next_touch_id + 1;
		}
		touch.down = down;
		touch.x    = static_cast<uint16_t>(std::clamp(x, 0.0f, 1.0f) * 1920.0f);
		touch.y    = static_cast<uint16_t>(std::clamp(y, 0.0f, 1.0f) * 943.0f);
		if (id == HOST_INPUT_CONTROLLER_ID) {
			m_state.buttons = down ? m_state.buttons | PAD_BUTTON_TOUCH_PAD
			                       : m_state.buttons & ~PAD_BUTTON_TOUCH_PAD;
		}
		AddState();
	}
}

void GameController::MotionPitch(int id, float radians) {
	Common::LockGuard lock(m_mutex);
	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		m_state.motion_pitch = std::clamp(radians, -1.4f, 1.4f);
		LOGF("ControllerMotion: pitch=%.3f enabled=%d\n", m_state.motion_pitch,
		     m_state.motion_enabled ? 1 : 0);
		m_state.time = LibKernel::KernelGetProcessTime();
		AddState();
	}
}

void GameController::MotionShake(int id, bool down) {
	Common::LockGuard lock(m_mutex);
	if (m_active_id == id || id == HOST_INPUT_CONTROLLER_ID) {
		m_state.motion_shake = down;
		m_state.time = LibKernel::KernelGetProcessTime();
		AddState();
		LOGF("ControllerMotion: shake=%d enabled=%d\n", down ? 1 : 0,
		     m_state.motion_enabled ? 1 : 0);
	}
}

void GameController::RefreshMotion() {
	// Called under m_mutex. Keep timestamped samples moving even with a held key;
	// buffered PadRead and single-sample PadReadState then use the same motion history.
	if (m_state.motion_enabled && m_state.motion_shake) {
		m_state.time = LibKernel::KernelGetProcessTime();
		AddState();
	}
}

void GameController::MotionSensorState(bool enable) {
	Common::LockGuard lock(m_mutex);
	m_state.motion_enabled = enable;
	m_state.time = LibKernel::KernelGetProcessTime();
	AddState();
}

void GameController::MotionSample(int id, MotionSensor sensor, const float* data,
                                  uint64_t timestamp_us) {
	if (data == nullptr) {
		return;
	}

	Common::LockGuard lock(m_mutex);
	if (m_active_id != id) {
		return;
	}

	const uint64_t now = LibKernel::KernelGetProcessTime();
	if (timestamp_us == 0) {
		timestamp_us = now;
	}
	if (sensor == MotionSensor::Accelerometer) {
		constexpr float STANDARD_GRAVITY = 9.80665f;
		for (int i = 0; i < 3; i++) {
			m_state.real_accel[i] = data[i] / STANDARD_GRAVITY;
		}
	} else {
		for (int i = 0; i < 3; i++) {
			m_state.real_gyro[i] = data[i];
		}
		if (m_gyro_timestamp != 0 && timestamp_us > m_gyro_timestamp) {
			// Integrate the body-frame angular velocity: q += 0.5 * dt * q * (w, 0).
			const float dt = std::min(static_cast<float>(timestamp_us - m_gyro_timestamp) * 1e-6f, 0.05f);
			auto&       q  = m_orientation;
			const float dx = q[3] * data[0] + q[1] * data[2] - q[2] * data[1];
			const float dy = q[3] * data[1] + q[2] * data[0] - q[0] * data[2];
			const float dz = q[3] * data[2] + q[0] * data[1] - q[1] * data[0];
			const float dw = -q[0] * data[0] - q[1] * data[1] - q[2] * data[2];
			const float h  = 0.5f * dt;
			q[0] += h * dx;
			q[1] += h * dy;
			q[2] += h * dz;
			q[3] += h * dw;
			const float norm = std::sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
			if (norm > 0.0f) {
				for (float& c: q) {
					c /= norm;
				}
			}
		}
		m_gyro_timestamp = timestamp_us;
		std::copy_n(m_orientation, 4, m_state.real_orientation);
	}
	if (!m_state.real_motion) {
		m_state.real_motion = true;
		std::copy_n(m_orientation, 4, m_state.real_orientation);
		LOGF("ControllerMotion: real sensors of pad %d in use\n", id);
	}
	m_state.time = now;
}

void GameController::ResetOrientation() {
	Common::LockGuard lock(m_mutex);
	m_orientation[0] = m_orientation[1] = m_orientation[2] = 0.0f;
	m_orientation[3] = 1.0f;
	std::copy_n(m_orientation, 4, m_state.real_orientation);
}

void GameController::ResetInputState() {
	Common::LockGuard lock(m_mutex);
	const bool motion_enabled = m_state.motion_enabled;
	m_state         = {};
	m_state.motion_enabled = motion_enabled;
	m_state.time    = LibKernel::KernelGetProcessTime();
	m_states_num    = 0;
	m_first_state   = 0;
	m_next_touch_id = 1;
	AddState();
}

void GameController::ReleaseHostPads() {
	Common::LockGuard lock(m_mutex);

	std::vector<SDL_GameController*> pads;
	for (const auto id: m_connected_ids) {
		if (id == HOST_INPUT_CONTROLLER_ID) {
			continue;
		}
		if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(id));
		    pad != nullptr) {
			if (SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5) {
				DualSenseEffects effect {};
				effect.enable_bits     = 0x0c;
				effect.right_trigger[0] = 0x05;
				effect.left_trigger[0]  = 0x05;
				(void)SDL_GameControllerSendEffect(pad, &effect, sizeof(effect));
			}
			(void)SDL_GameControllerRumble(pad, 0, 0, 0);
			(void)SDL_GameControllerSetLED(pad, 0, 0, 0);
			pads.push_back(pad);
		}
	}

	if (!pads.empty()) {
		SDL_Delay(RELEASE_FLUSH_MS);
		for (auto* pad: pads) {
			SDL_GameControllerClose(pad);
		}
	}

	m_connected_ids.clear();
}

void GameController::SetVibration(uint8_t large_motor, uint8_t small_motor) {
	Common::LockGuard lock(m_mutex);

	if (m_active_id == HOST_INPUT_CONTROLLER_ID) {
		return;
	}
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad == nullptr) {
		return;
	}

	const auto large = static_cast<uint16_t>(large_motor * 0x101U);
	const auto small = static_cast<uint16_t>(small_motor * 0x101U);
	if (SDL_GameControllerRumble(pad, large, small, RUMBLE_DURATION_MS) != 0) {
		LOGF("\t rumble failed: %s\n", SDL_GetError());
	}
}

void GameController::SetLightBar(uint8_t r, uint8_t g, uint8_t b) {
	Common::LockGuard lock(m_mutex);
	if (auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	    pad != nullptr) {
		(void)SDL_GameControllerSetLED(pad, r, g, b);
	}
}

bool GameController::SetTriggerEffect(const PadTriggerEffectParam& param, bool* sent) {
	*sent = false;
	if ((param.trigger_mask & ~0x03u) != 0) {
		return false;
	}

	DualSenseEffects effect {};
	if ((param.trigger_mask & 0x01u) != 0) {
		effect.enable_bits |= 0x08;
		if (!trigger_effect_to_dualsense(param.command[0], effect.left_trigger)) {
			return false;
		}
	}
	if ((param.trigger_mask & 0x02u) != 0) {
		effect.enable_bits |= 0x04;
		if (!trigger_effect_to_dualsense(param.command[1], effect.right_trigger)) {
			return false;
		}
	}
	if (effect.enable_bits == 0) {
		return true;
	}

	Common::LockGuard lock(m_mutex);
	auto* pad = SDL_GameControllerFromInstanceID(static_cast<SDL_JoystickID>(m_active_id));
	if (pad != nullptr && SDL_GameControllerGetType(pad) == SDL_CONTROLLER_TYPE_PS5) {
		*sent = SDL_GameControllerSendEffect(pad, &effect, sizeof(effect)) == 0;
	}
	return true;
}

void GameController::GetConnectionInfo(bool* flag, int* count) {
	EXIT_IF(flag == nullptr);
	EXIT_IF(count == nullptr);

	Common::LockGuard lock(m_mutex);

	*flag  = m_connected;
	*count = m_connected_count;
}

void GameController::ReadState(ControllerState* state, bool* flag, int* count) {
	EXIT_IF(flag == nullptr);
	EXIT_IF(count == nullptr);
	EXIT_IF(state == nullptr);

	Common::LockGuard lock(m_mutex);
	RefreshMotion();

	*flag  = m_connected;
	*count = m_connected_count;
	*state = m_state;
}

int GameController::ReadStates(ControllerState* states, int states_num, bool* flag, int* count) {
	EXIT_IF(flag == nullptr);
	EXIT_IF(count == nullptr);
	EXIT_IF(states == nullptr);
	EXIT_IF(states_num < 1 || states_num > STATES_MAX);

	Common::LockGuard lock(m_mutex);
	RefreshMotion();

	*flag  = m_connected;
	*count = m_connected_count;

	int ret_num = 0;

	if (m_connected) {
		if (m_states_num != 0) {
			for (uint32_t i = 0; i < m_states_num; i++) {
				if (ret_num >= states_num) {
					break;
				}
				auto index = (m_first_state + i) % STATES_MAX;
				if (!m_obtained[index]) {
					m_obtained[index] = true;

					states[ret_num++] = m_states[index];
				}
			}
		}
	}

	return ret_num;
}

void Connect(int id) {
	g_controller->Connect(id);
}

void Disconnect(int id) {
	g_controller->Disconnect(id);
}

void SetButton(int id, uint32_t button, bool down) {
	g_controller->Button(id, button, down);
}

void SetAxis(int id, Axis axis, int value) {
	g_controller->Axis(id, axis, value);
}

void SetRightStick(int id, int x, int y) {
	g_controller->RightStick(id, x, y);
}

void SetMotionShake(int id, bool down) {
	g_controller->MotionShake(id, down);
}

void SetMotionPitch(int id, float radians) {
	g_controller->MotionPitch(id, radians);
}

void SetTouchPad(int id, int finger, bool down, float x, float y) {
	g_controller->TouchPad(id, finger, down, x, y);
}

void ResetInputState() {
	g_controller->ResetInputState();
}

void SetMotionSensor(int id, MotionSensor sensor, const float* data, uint64_t timestamp_us) {
	if (g_controller != nullptr) {
		g_controller->MotionSample(id, sensor, data, timestamp_us);
	}
}

void PushHapticsPcm(const void* pcm, uint32_t frames, uint32_t channels, bool is_float,
                    uint32_t freq) {
	if (g_haptics != nullptr) {
		g_haptics->Push(pcm, frames, channels, is_float, freq);
	}
}

int KYTY_SYSV_ABI PadInit() {
	PRINT_NAME();

	return OK;
}

static bool PadOpenArgsAreValid(int user_id, int type, int index) {
	constexpr int user_id_system     = 0xff;
	constexpr int port_type_standard = 0;
	constexpr int port_type_special  = 2;
	constexpr int port_type_remote   = 16;
	const bool    personal_port =
	    user_id == Config::GetUserId() && (type == port_type_standard || type == port_type_special);
	const bool system_remote_control = user_id == user_id_system && type == port_type_remote;
	return index == 0 && (personal_port || system_remote_control);
}

int KYTY_SYSV_ABI PadOpen(int user_id, int type, int index, const void* param) {
	PRINT_NAME();

	LOGF("\t user_id = %d\n"
	     "\t type    = %d\n"
	     "\t index   = %d\n"
	     "\t param   = 0x%016" PRIx64 "\n",
	     user_id, type, index, reinterpret_cast<uint64_t>(param));

	constexpr int pad_error_invalid_arg = -2137915391; /* 0x80920001 */

	if (!PadOpenArgsAreValid(user_id, type, index)) {
		return pad_error_invalid_arg;
	}

	int handle = 1;

	return handle;
}

int KYTY_SYSV_ABI PadGetHandle(int user_id, int type, int index) {
	PRINT_NAME();

	LOGF("\t user_id = %d\n"
	     "\t type    = %d\n"
	     "\t index   = %d\n",
	     user_id, type, index);

	constexpr int pad_error_device_no_handle = -2137915384; /* 0x80920008 */

	if (!PadOpenArgsAreValid(user_id, type, index)) {
		return pad_error_device_no_handle;
	}

	return 1;
}

int KYTY_SYSV_ABI PadSetMotionSensorState(int handle, bool enable) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}

	LOGF("\t enable = %s\n", (enable ? "true" : "false"));

	g_controller->MotionSensorState(enable);
	return OK;
}

int KYTY_SYSV_ABI PadSetAngularVelocityDeadbandState(int handle, bool enable) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}

	LOGF("\t enable = %s\n", (enable ? "true" : "false"));

	return OK;
}

int KYTY_SYSV_ABI PadResetOrientation(int handle) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}

	g_controller->MotionPitch(HOST_INPUT_CONTROLLER_ID, 0.0f);
	g_controller->ResetOrientation();
	return OK;
}

int KYTY_SYSV_ABI PadGetControllerInformation(int handle, PadControllerInformation* info) {
	PRINT_NAME();

	int  connected_count = 0;
	bool connected       = false;

	g_controller->GetConnectionInfo(&connected, &connected_count);

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (info == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	std::memset(info, 0, sizeof(*info));

	info->touch_pixel_density   = 44.86f;
	info->touch_resolution_x    = 1920;
	info->touch_resolution_y    = 943;
	info->stick_dead_zone_left  = controller_get_axis(-32768, 32767, 8000) - 128;
	info->stick_dead_zone_right = controller_get_axis(-32768, 32767, 8000) - 128;
	info->connection_type       = 0;
	info->connected_count       = static_cast<uint8_t>(std::min(connected_count, 255));
	info->connected             = connected;
	info->device_class          = 0;

	return OK;
}

int KYTY_SYSV_ABI PadReadState(int handle, PadData* data) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (data == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	int             connected_count = 0;
	bool            connected       = false;
	ControllerState state;

	g_controller->ReadState(&state, &connected, &connected_count);

	pad_fill_data(data, state, connected, connected_count);

	return OK;
}

int KYTY_SYSV_ABI PadRead(int handle, PadData* data, int num) {
	PRINT_NAME();

	EXIT_NOT_IMPLEMENTED(num < 1 || num > 64);
	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (data == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	std::memset(data, 0, sizeof(PadData) * static_cast<size_t>(num));

	int             connected_count = 0;
	bool            connected       = false;
	ControllerState states[64]      = {};

	int ret_num = g_controller->ReadStates(states, num, &connected, &connected_count);

	if (!connected || ret_num == 0) {
		if (connected) {
			g_controller->ReadState(&states[0], &connected, &connected_count);
		}
		ret_num = 1;
	}

	for (int i = 0; i < ret_num; i++) {
		pad_fill_data(&data[i], states[i], connected, connected_count);
	}

	return ret_num;
}

int KYTY_SYSV_ABI PadSetVibration(int handle, const PadVibrationParam* param) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (param == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	LOGF("\t large_motor = %d\n"
	     "\t small_motor = %d\n",
	     static_cast<int>(param->large_motor), static_cast<int>(param->small_motor));

	g_controller->SetVibration(param->large_motor, param->small_motor);

	return OK;
}

int KYTY_SYSV_ABI PadResetLightBar(int handle) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}

	return OK;
}

int KYTY_SYSV_ABI PadSetLightBar(int handle, const PadLightBarParam* param) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (param == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	g_controller->SetLightBar(param->r, param->g, param->b);

	return OK;
}

int KYTY_SYSV_ABI PadSetTriggerEffect(int handle, const PadTriggerEffectParam* param) {
	PRINT_NAME();

	if (handle != 1) {
		return PAD_ERROR_INVALID_HANDLE;
	}
	if (param == nullptr) {
		return PAD_ERROR_INVALID_ARG;
	}

	bool       sent = false;
	const bool ok   = g_controller->SetTriggerEffect(*param, &sent);

	static std::atomic<uint32_t> calls {0};
	const auto                   n = ++calls;
	if (n <= 32 || (n % 500) == 0 || (!ok && n <= 1000)) {
		const auto& l = param->command[0];
		const auto& r = param->command[1];
		LOGF("PadTriggerEffect: #%u mask=0x%02x L=%u[%02x %02x %02x %02x] R=%u[%02x %02x %02x %02x] "
		     "ok=%d sent=%d\n",
		     n, param->trigger_mask, l.mode, l.data[0], l.data[1], l.data[2], l.data[3], r.mode,
		     r.data[0], r.data[1], r.data[2], r.data[3], ok ? 1 : 0, sent ? 1 : 0);
	}

	return ok ? OK : PAD_ERROR_INVALID_ARG;
}

} // namespace Libs::Controller
