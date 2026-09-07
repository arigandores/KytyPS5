#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_INPUT_SCRIPT_H_
#define EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_INPUT_SCRIPT_H_

#include "common/common.h"

#include <cstdint>
#include <string>
#include <vector>

namespace Libs::Graphics {

// Scripted controller input that bypasses the window: key presses are injected straight into the
// host-input mapping (the same one SDL key events use), so they work while the window is
// minimized, covered, unfocused or running under RenderDoc.
//
// Sources (both use the keyboard names of the default mapping: j/i/k/l = Cross/Triangle/Square/
// Circle, up/down/left/right, enter = Options, q/e = L1/R1, w/a/s/d = left stick, ...):
//   KYTY_KEYS="38:j,+5:j"       tokens "<t>:<key>[/<hold_ms>]": absolute seconds since the first
//                               present, or "+<t>" seconds after the previous token; hold defaults
//                               to 150 ms. "@<n>:<key>" fires at present number n (the game steps
//                               one fixed frame per present, so this survives shader stalls):
//                               KYTY_KEYS="@2170:j,@2460:j" reaches intro_next from a cold start.
//   file "_input.req"           in the working directory, same tokens separated by whitespace or
//                               commas; a token without a time fires immediately, "+<t>" delays
//                               relative to the previous token. The file is deleted when read
//                               (checked every 8 presents, like the screenshot request).
// Every press and release is logged as "InputScript:".
class InputScript final {
public:
	InputScript();
	~InputScript();
	KYTY_CLASS_NO_COPY(InputScript);

	// Called once per present.
	void Poll();

private:
	struct Action {
		double at_s     = 0.0;
		uint32_t at_present = 0; // != 0: fire when m_presents reaches it (instead of at_s)
		double hold_s   = 0.15;
		int    key_code = 0;
		char   name[16] = {};
		bool   pressed  = false;
	};

	void   ParseTokens(const std::string& text, double base_s, bool relative_to_now);
	double Now() const;

	std::vector<Action> m_actions;
	uint32_t            m_presents        = 0;
	double              m_first_present_s = -1.0;
	bool                m_has_env         = false;
	std::string         m_env;
};

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_INPUT_SCRIPT_H_
