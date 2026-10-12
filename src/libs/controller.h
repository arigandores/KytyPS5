#ifndef EMULATOR_INCLUDE_EMULATOR_CONTROLLER_H_
#define EMULATOR_INCLUDE_EMULATOR_CONTROLLER_H_

#include "common/abi.h"
#include "common/common.h"
namespace Libs::Controller {

void Initialize();
void Shutdown();
void EmergencyShutdown();

struct Lifecycle {
	static constexpr const char* name               = "Controller";
	static constexpr auto        initialize         = Libs::Controller::Initialize;
	static constexpr auto        shutdown           = Libs::Controller::Shutdown;
	static constexpr auto        emergency_shutdown = Libs::Controller::EmergencyShutdown;
};

constexpr int HOST_INPUT_CONTROLLER_ID = -1000;

constexpr uint32_t PAD_BUTTON_L3        = 0x00000002;
constexpr uint32_t PAD_BUTTON_R3        = 0x00000004;
constexpr uint32_t PAD_BUTTON_OPTIONS   = 0x00000008;
constexpr uint32_t PAD_BUTTON_UP        = 0x00000010;
constexpr uint32_t PAD_BUTTON_RIGHT     = 0x00000020;
constexpr uint32_t PAD_BUTTON_DOWN      = 0x00000040;
constexpr uint32_t PAD_BUTTON_LEFT      = 0x00000080;
constexpr uint32_t PAD_BUTTON_L2        = 0x00000100;
constexpr uint32_t PAD_BUTTON_R2        = 0x00000200;
constexpr uint32_t PAD_BUTTON_L1        = 0x00000400;
constexpr uint32_t PAD_BUTTON_R1        = 0x00000800;
constexpr uint32_t PAD_BUTTON_TRIANGLE  = 0x00001000;
constexpr uint32_t PAD_BUTTON_CIRCLE    = 0x00002000;
constexpr uint32_t PAD_BUTTON_CROSS     = 0x00004000;
constexpr uint32_t PAD_BUTTON_SQUARE    = 0x00008000;
constexpr uint32_t PAD_BUTTON_TOUCH_PAD = 0x00100000;

enum class Axis {
	LeftX        = 0,
	LeftY        = 1,
	RightX       = 2,
	RightY       = 3,
	TriggerLeft  = 4,
	TriggerRight = 5,

	AxisMax
};

struct PadControllerInformation;
struct PadData;
struct PadVibrationParam;
struct PadLightBarParam;
struct PadTriggerEffectParam;

inline int controller_get_axis(int min, int max, int value) {
	int v = (255 * (value - min)) / (max - min);
	if (v < 0) {
		return 0;
	}
	if (v > 255) {
		return 255;
	}
	return v;
}

void Connect(int id);
void Disconnect(int id);
void SetButton(int id, uint32_t button, bool down);
void SetAxis(int id, Axis axis, int value);
void SetRightStick(int id, int x, int y);
void SetTouchPad(int id, int finger, bool down, float x, float y);
// Keyboard fallback: pitch in radians about the controller X axis.
void SetMotionPitch(int id, float radians);
void SetMotionShake(int id, bool down);
void ResetInputState();
// Track F, F19c (ROADMAP s122 item 451(d)): KYTY_FIX_B24 is on (read once in Initialize).
bool FixB24On();
// Track F, F19c stand KYTY_TEST_HIDLOSS (item 451(c), F19a s6.1): pad output counters of the stand window.
// TestHidLossWindow(true) zeroes them and starts counting, TestHidLossWindow(false) stops counting; outside the window a
// pad output call does one relaxed load of a static flag and nothing else.
struct HidLossPadStats {
	uint64_t pad_vib         = 0;
	uint64_t pad_led         = 0;
	uint64_t pad_trig        = 0;
	uint64_t pad_wait_max_us = 0;
	uint64_t po_applied      = 0;
	uint64_t po_wait_max_us  = 0;
	uint64_t guest_sdl       = 0;
};
void            TestHidLossWindow(bool open);
HidLossPadStats TestHidLossPadStats();

enum class MotionSensor { Accelerometer, Gyroscope };
// Real pad sensor sample in SDL units: m/s^2 for the accelerometer, rad/s for the gyroscope.
void SetMotionSensor(int id, MotionSensor sensor, const float* data, uint64_t timestamp_us);
// Interleaved haptic PCM of an AudioOut vibration port (int16 or float).
void PushHapticsPcm(const void* pcm, uint32_t frames, uint32_t channels, bool is_float,
                    uint32_t freq);
// Track F, F8 stand (ROADMAP s122 item 441(g)): KYTY_TEST_AUDIOLOSS is set and valid (read once in Initialize).
bool TestAudioLossOn();

int KYTY_SYSV_ABI PadInit();
int KYTY_SYSV_ABI PadOpen(int user_id, int type, int index, const void* param);
int KYTY_SYSV_ABI PadGetHandle(int user_id, int type, int index);
int KYTY_SYSV_ABI PadSetMotionSensorState(int handle, bool enable);
int KYTY_SYSV_ABI PadSetAngularVelocityDeadbandState(int handle, bool enable);
int KYTY_SYSV_ABI PadResetOrientation(int handle);
int KYTY_SYSV_ABI PadGetControllerInformation(int handle, PadControllerInformation* info);
int KYTY_SYSV_ABI PadReadState(int handle, PadData* data);
int KYTY_SYSV_ABI PadRead(int handle, PadData* data, int num);
int KYTY_SYSV_ABI PadSetVibration(int handle, const PadVibrationParam* param);
int KYTY_SYSV_ABI PadSetTriggerEffect(int handle, const PadTriggerEffectParam* param);
int KYTY_SYSV_ABI PadResetLightBar(int handle);
int KYTY_SYSV_ABI PadSetLightBar(int handle, const PadLightBarParam* param);
// Track M, M2b (T272, upstream 3c62359e; HPP-839, ROADMAP s122 item 756(v)(2)): KYTY_M_T272 (default 0), read once
// per process (Initialize; line MT272: mode=). At 1 scePadGetTriggerEffectState (libPad.cpp) answers with
// PadGetTriggerEffectStateM272: the state of the last effect per trigger and the trigger travel; at 0 it stays 0.
bool              MT272On();
int KYTY_SYSV_ABI PadGetTriggerEffectStateM272(int handle, int32_t* state);

} // namespace Libs::Controller

#endif /* EMULATOR_INCLUDE_EMULATOR_CONTROLLER_H_ */
