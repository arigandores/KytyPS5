#ifndef EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_
#define EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_

#include <string_view>

namespace Libs::Graphics {

// Track F, F5a2 (ROADMAP s122 item 280(v), RC2 of F5b): true when the guest text holds the level entry line
// "Level has started: <level>" - after the prefix, before the end of that line ('\n' or the end of the text), there is
// a non-blank character.  The game first writes the line with an empty name; that line is not the entry line (item
// 221(v)).  Header-only so that a test can build it without the window code.
inline bool TestMinimizeIsLevelEntry(std::string_view text) {
	constexpr std::string_view prefix = "Level has started: ";
	for (auto pos = text.find(prefix); pos != std::string_view::npos; pos = text.find(prefix, pos + 1)) {
		for (auto i = pos + prefix.size(); i < text.size() && text[i] != '\n'; i++) {
			const char c = text[i];
			if (c != ' ' && c != '\t' && c != '\r' && c != '\v' && c != '\f') {
				return true;
			}
		}
	}
	return false;
}

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_PRESENTATION_WINDOW_TESTMINIMIZELINE_H_
