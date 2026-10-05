#ifndef EMULATOR_INCLUDE_EMULATOR_AUDIO_INTERNAL_H_
#define EMULATOR_INCLUDE_EMULATOR_AUDIO_INTERNAL_H_

#include "common/common.h"

namespace Libs::Audio::AudioInternal {

enum class Format {
	Unknown,
	Signed16bitMono,
	Signed16bitStereo,
	Signed16bit8Ch,
	FloatMono,
	FloatStereo,
	Float8Ch,
	Signed16bit8ChStd,
	Float8ChStd,
	Float12Ch,
};

struct OutputParam {
	int         handle = 0;
	const void* data   = nullptr;
};

static constexpr int OUT_PORTS_MAX = 32;

int      AudioOutOpen(int type, uint32_t samples_num, uint32_t freq, Format format);
void     AudioOutClose(int handle);
bool     AudioOutHasDevice(int handle);
uint32_t AudioOutOutputs(const OutputParam* params, uint32_t num, bool blocking = true);

// Track F, F8 (ROADMAP s122 item 441(v)): the emulator call sites of SDL_InitSubSystem / SDL_QuitSubSystem with
// SDL_INIT_AUDIO (AudioOut ports, AudioIn ports, pad haptics). KYTY_FIX_F8=0: the same SDL calls as before (each init
// counted). KYTY_FIX_F8 unset, empty or 1 (default ON since FS7a, item 467(g)(1)): init goes through SdlAudioAcquire,
// quit does nothing - the SDL reference count of the audio subsystem stays 1 for the life of the process. Read once per
// process; "FixF8: mode=1" once when on.
int  SdlAudioSubsystemInit();
void SdlAudioSubsystemQuit();
// SDL_InitSubSystem(SDL_INIT_AUDIO) at most once successfully per process (own mutex; a failure is not remembered).
int SdlAudioAcquire();
// Counters of item 441(g): real SDL_InitSubSystem(SDL_INIT_AUDIO) calls of the emulator (both modes) and
// SdlAudioAcquire calls; AudioStatForce makes every output port print its AudioStat line on its next push.
uint64_t SdlAudioInitCalls();
uint64_t SdlAudioAcquireCalls();
void     AudioStatForce();

} // namespace Libs::Audio::AudioInternal

#endif // EMULATOR_INCLUDE_EMULATOR_AUDIO_INTERNAL_H_
