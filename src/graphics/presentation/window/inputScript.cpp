#include "graphics/presentation/window/inputScript.h"

#include "SDL_keyboard.h"
#include "SDL_keycode.h"
#include "common/logging/log.h"
#include "graphics/presentation/window/hostInput.h"

#include <cctype>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>

namespace Libs::Graphics {

namespace {

constexpr const char* REQUEST_FILE = "_input.req";

double SteadySeconds() {
	return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch())
	    .count();
}

std::string Lower(std::string s) {
	for (auto& c: s) {
		c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
	}
	return s;
}

// Key name -> SDL keycode. Accepts SDL names ("J", "Up", "Return") and a few short aliases.
int KeyFromName(const std::string& raw) {
	const auto  name = Lower(raw);
	const char* sdl  = nullptr;
	if (name == "enter" || name == "return") {
		sdl = "Return";
	} else if (name == "lshift" || name == "shift") {
		sdl = "Left Shift";
	} else if (name == "lctrl" || name == "ctrl") {
		sdl = "Left Ctrl";
	} else if (name == "esc") {
		sdl = "Escape";
	} else if (name == "bs") {
		sdl = "Backspace";
	}
	auto key = SDL_GetKeyFromName(sdl != nullptr ? sdl : raw.c_str());
	if (key == SDLK_UNKNOWN && sdl == nullptr) {
		key = SDL_GetKeyFromName(name.c_str());
	}
	return static_cast<int>(key);
}

} // namespace

InputScript::InputScript() {
	if (const char* value = std::getenv("KYTY_KEYS"); value != nullptr && value[0] != '\0') {
		m_env     = value;
		m_has_env = true;
	}
}

InputScript::~InputScript() = default;

double InputScript::Now() const {
	return SteadySeconds() - m_first_present_s;
}

// Tokens: "<t>:<key>[/<hold_ms>]", "+<t>:<key>[/<hold_ms>]", "<key>[/<hold_ms>]"; separated by
// whitespace, commas or semicolons. `base_s` is the time a bare token fires at and the origin of
// the first "+<t>"; absolute times are relative to the first present.
void InputScript::ParseTokens(const std::string& text, double base_s, bool relative_to_now) {
	std::string normalized = text;
	for (auto& c: normalized) {
		if (c == ',' || c == ';' || c == '\r' || c == '\n' || c == '\t') {
			c = ' ';
		}
	}
	std::istringstream stream(normalized);
	std::string        token;
	double             previous_s = base_s;
	while (stream >> token) {
		Action action {};
		action.at_s = base_s;

		std::string key = token;
		const auto  colon = token.find(':');
		if (colon != std::string::npos) {
			const auto time_text = token.substr(0, colon);
			key                  = token.substr(colon + 1);
			if (!time_text.empty() && time_text[0] == '@') {
				action.at_present =
				    static_cast<uint32_t>(std::strtoul(time_text.c_str() + 1, nullptr, 10));
				if (action.at_present == 0) {
					LOGF("InputScript: bad present number in token '%s'\n", token.c_str());
					continue;
				}
			} else {
				char*      end = nullptr;
				const auto t   = std::strtod(time_text.c_str(), &end);
				if (end == time_text.c_str()) {
					LOGF("InputScript: bad time in token '%s'\n", token.c_str());
					continue;
				}
				if (time_text[0] == '+') {
					action.at_s = previous_s + t;
				} else {
					action.at_s = relative_to_now ? base_s + t : t;
				}
			}
		}
		const auto slash = key.find('/');
		if (slash != std::string::npos) {
			action.hold_s = std::strtod(key.substr(slash + 1).c_str(), nullptr) / 1000.0;
			key           = key.substr(0, slash);
			if (action.hold_s <= 0.0) {
				action.hold_s = 0.15;
			}
		}
		action.key_code = KeyFromName(key);
		if (action.key_code == SDLK_UNKNOWN) {
			LOGF("InputScript: unknown key '%s' in token '%s'\n", key.c_str(), token.c_str());
			continue;
		}
		std::strncpy(action.name, key.c_str(), sizeof(action.name) - 1);
		previous_s = action.at_s;
		m_actions.push_back(action);
		if (action.at_present != 0) {
			LOGF("InputScript: scheduled %s at present %u (hold %.0f ms)\n", action.name,
			     action.at_present, action.hold_s * 1000.0);
		} else {
			LOGF("InputScript: scheduled %s at %.2f s (hold %.0f ms)\n", action.name, action.at_s,
			     action.hold_s * 1000.0);
		}
	}
}

void InputScript::Poll() {
	m_presents++;
	if (m_first_present_s < 0.0) {
		m_first_present_s = SteadySeconds();
	}
	if (m_has_env) {
		m_has_env = false;
		ParseTokens(m_env, 0.0, false);
	}
	if ((m_presents & 7u) == 0) {
		std::error_code ec;
		if (std::filesystem::exists(REQUEST_FILE, ec)) {
			std::string text;
			{
				std::ifstream file(REQUEST_FILE);
				std::stringstream buffer;
				buffer << file.rdbuf();
				text = buffer.str();
			}
			std::filesystem::remove(REQUEST_FILE, ec);
			ParseTokens(text, Now(), true);
		}
	}
	if (m_actions.empty()) {
		return;
	}

	const auto now = Now();
	for (size_t i = 0; i < m_actions.size();) {
		auto& action = m_actions[i];
		if (!action.pressed) {
			const bool due =
			    action.at_present != 0 ? m_presents >= action.at_present : now >= action.at_s;
			if (!due) {
				i++;
				continue;
			}
			HostInputKey(action.key_code, true);
			action.pressed = true;
			action.at_s    = now; // the hold is timed from the actual press
			LOGF("InputScript: press %s at %.2f s (present %u)\n", action.name, now, m_presents);
			i++;
			continue;
		}
		if (now < action.at_s + action.hold_s) {
			i++;
			continue;
		}
		HostInputKey(action.key_code, false);
		LOGF("InputScript: release %s at %.2f s\n", action.name, now);
		m_actions.erase(m_actions.begin() + static_cast<std::ptrdiff_t>(i));
	}
}

} // namespace Libs::Graphics
