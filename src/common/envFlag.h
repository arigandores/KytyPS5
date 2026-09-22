#ifndef KYTY_COMMON_ENV_FLAG_H_
#define KYTY_COMMON_ENV_FLAG_H_

#include <cstddef>
#include <cstdlib>

namespace Common {

// Session 102: boolean environment switches are decided by their VALUE, not by their presence.
// Session 101 found KYTY_GPU_CHECKPOINTS=0 turning the checkpoints ON, because the reader tested
// getenv() != nullptr; the same test sat behind every other on/off switch of this class.
// OFF: unset, "", "0", "false", "off", "no" (ASCII case-insensitive, exact match, no trimming).
// ON: any other value, exactly as before ("1", "nv", "yes", "00", " 0", ...).
[[nodiscard]] inline bool EnvValueOn(const char* value) noexcept {
	if (value == nullptr || value[0] == '\0') {
		return false;
	}
	const auto equals = [value](const char* word) noexcept {
		std::size_t i = 0;
		for (; word[i] != '\0'; i++) {
			char c = value[i];
			if (c >= 'A' && c <= 'Z') {
				c = static_cast<char>(c - 'A' + 'a');
			}
			if (c != word[i]) {
				return false;
			}
		}
		return value[i] == '\0';
	};
	return !(equals("0") || equals("false") || equals("off") || equals("no"));
}

// Session 102: EnvValueOn(std::getenv(name)); replaces `std::getenv(name) != nullptr`.
[[nodiscard]] inline bool EnvFlagOn(const char* name) noexcept {
	return EnvValueOn(std::getenv(name));
}

} // namespace Common

#endif /* KYTY_COMMON_ENV_FLAG_H_ */
