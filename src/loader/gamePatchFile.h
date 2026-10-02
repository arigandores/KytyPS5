#ifndef KYTY_LOADER_GAME_PATCH_FILE_H_
#define KYTY_LOADER_GAME_PATCH_FILE_H_

// Track P, the opt-in patch file of the P-var iteration (ROADMAP s122 item 333(d)). KYTY_GAME_PATCH=<path> names a text
// file bound to one eboot.bin by its sha256:
//   sha256 <64 hex>            exactly one, the first directive
//   poke <offset hex>:<bytes>  offset from the main module base (< 0x100000000), bytes as KYTY_POKE
//   pvar 2                     the P-var mode 2 (as KYTY_PVAR=2), at most once
//   audio_sync 0               the guest speed (audio tempo) off (as KYTY_AUDIO_SYNC=0), at most once
//   # ...                      a comment up to the end of the line; blank lines are ignored
// An unknown directive, a bad argument, bad hex or two overlapping poke ranges refuse the whole file; so do a sha256 that
// differs from the loaded eboot.bin ("reason=sha": nothing of the file is applied) and an explicit KYTY_PVAR /
// KYTY_AUDIO_SYNC / KYTY_POKE that contradicts the file ("reason=env", "reason=overlap"). KYTY_POKE is written after the
// pokes of the file. KYTY_GAME_PATCH unset or empty - the file is not looked for and nothing here changes the old path.
//
// The part above Load() needs only the standard library: the P23 fixture (docs/track-p/p23/test_gamepatchfile.cpp)
// compiles this header without the project configuration and without gamePatchFile.cpp.

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>

namespace Loader::GamePatchFile {

// FIPS 180-4 SHA-256, incremental.
class Sha256 {
public:
	Sha256() = default;

	void Update(const uint8_t* data, size_t size) {
		m_length += static_cast<uint64_t>(size);
		while (size > 0) {
			const size_t take = (size < 64 - m_used) ? size : 64 - m_used;
			for (size_t i = 0; i < take; i++) {
				m_block[m_used + i] = data[i];
			}
			m_used += take;
			data += take;
			size -= take;
			if (m_used == 64) {
				Compress();
				m_used = 0;
			}
		}
	}

	// Lower-case hex of the digest; the object is spent afterwards.
	std::string FinalHex() {
		const uint64_t bits = m_length * 8u;
		const uint8_t  one  = 0x80;
		Update(&one, 1);
		const uint8_t zero = 0;
		while (m_used != 56) {
			Update(&zero, 1);
		}
		uint8_t tail[8];
		for (int i = 0; i < 8; i++) {
			tail[i] = static_cast<uint8_t>(bits >> (56 - 8 * i));
		}
		Update(tail, 8);
		static constexpr char digits[] = "0123456789abcdef";
		std::string           text;
		for (uint32_t word: m_h) {
			for (int shift = 28; shift >= 0; shift -= 4) {
				text += digits[(word >> static_cast<uint32_t>(shift)) & 0xfu];
			}
		}
		return text;
	}

private:
	static uint32_t Rotr(uint32_t x, uint32_t n) { return (x >> n) | (x << (32u - n)); }

	void Compress() {
		static constexpr uint32_t K[64] = {
		    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
		    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
		    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
		    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
		    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
		    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
		    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
		    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};
		uint32_t w[64];
		for (int i = 0; i < 16; i++) {
			w[i] = (static_cast<uint32_t>(m_block[4 * i]) << 24u) | (static_cast<uint32_t>(m_block[4 * i + 1]) << 16u) |
			       (static_cast<uint32_t>(m_block[4 * i + 2]) << 8u) | static_cast<uint32_t>(m_block[4 * i + 3]);
		}
		for (int i = 16; i < 64; i++) {
			const uint32_t s0 = Rotr(w[i - 15], 7) ^ Rotr(w[i - 15], 18) ^ (w[i - 15] >> 3u);
			const uint32_t s1 = Rotr(w[i - 2], 17) ^ Rotr(w[i - 2], 19) ^ (w[i - 2] >> 10u);
			w[i]              = w[i - 16] + s0 + w[i - 7] + s1;
		}
		uint32_t a = m_h[0], b = m_h[1], c = m_h[2], d = m_h[3], e = m_h[4], f = m_h[5], g = m_h[6], h = m_h[7];
		for (int i = 0; i < 64; i++) {
			const uint32_t s1  = Rotr(e, 6) ^ Rotr(e, 11) ^ Rotr(e, 25);
			const uint32_t ch  = (e & f) ^ (~e & g);
			const uint32_t t1  = h + s1 + ch + K[i] + w[i];
			const uint32_t s0  = Rotr(a, 2) ^ Rotr(a, 13) ^ Rotr(a, 22);
			const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
			const uint32_t t2  = s0 + maj;
			h                  = g;
			g                  = f;
			f                  = e;
			e                  = d + t1;
			d                  = c;
			c                  = b;
			b                  = a;
			a                  = t1 + t2;
		}
		m_h[0] += a;
		m_h[1] += b;
		m_h[2] += c;
		m_h[3] += d;
		m_h[4] += e;
		m_h[5] += f;
		m_h[6] += g;
		m_h[7] += h;
	}

	std::array<uint32_t, 8> m_h {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
	                             0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
	std::array<uint8_t, 64> m_block {};
	size_t                  m_used   = 0;
	uint64_t                m_length = 0;
};

struct Poke {
	uint64_t             offset = 0; // from the main module base
	std::vector<uint8_t> bytes;
	std::string          hex; // as written in the file (for the log line)
};

struct Spec {
	std::string       sha256; // lower-case, 64 hex
	std::vector<Poke> pokes;
	bool              pvar2       = false;
	bool              audio_sync0 = false;
};

// reason: open | directive | hex | overlap | sha | env; detail - one line for the log.
struct Refusal {
	std::string reason;
	std::string detail;
};

// The environment the decision reads; nullptr - the variable is not set.
struct Env {
	const char* pvar       = nullptr; // KYTY_PVAR
	const char* audio_sync = nullptr; // KYTY_AUDIO_SYNC
	const char* poke       = nullptr; // KYTY_POKE
};

namespace Detail {

inline bool IsHex(char ch) {
	return (ch >= '0' && ch <= '9') || (ch >= 'a' && ch <= 'f') || (ch >= 'A' && ch <= 'F');
}

inline uint8_t HexValue(char ch) {
	if (ch >= '0' && ch <= '9') {
		return static_cast<uint8_t>(ch - '0');
	}
	if (ch >= 'a' && ch <= 'f') {
		return static_cast<uint8_t>(ch - 'a' + 10);
	}
	return static_cast<uint8_t>(ch - 'A' + 10);
}

inline bool AllHex(std::string_view text) {
	if (text.empty()) {
		return false;
	}
	for (char ch: text) {
		if (!IsHex(ch)) {
			return false;
		}
	}
	return true;
}

inline std::vector<std::string_view> Tokens(std::string_view line) {
	std::vector<std::string_view> tokens;
	size_t                        i = 0;
	while (i < line.size()) {
		while (i < line.size() && (line[i] == ' ' || line[i] == '\t')) {
			i++;
		}
		const size_t start = i;
		while (i < line.size() && line[i] != ' ' && line[i] != '\t') {
			i++;
		}
		if (i > start) {
			tokens.push_back(line.substr(start, i - start));
		}
	}
	return tokens;
}

inline bool Fail(Refusal* refusal, const char* reason, size_t line_no, const std::string& what) {
	refusal->reason = reason;
	refusal->detail = "line=" + std::to_string(line_no) + " " + what;
	return false;
}

// Half-open ranges [a, a + n) and [b, b + m).
inline bool Overlap(uint64_t a, uint64_t n, uint64_t b, uint64_t m) {
	return n > 0 && m > 0 && a < b + m && b < a + n;
}

// Common::Split(text, sep) of common/stringUtils.h (keep_empty = false), which the KYTY_POKE loop uses: empty parts drop.
inline std::vector<std::string> Split(std::string_view text, char sep) {
	std::vector<std::string> parts;
	size_t                   start = 0;
	for (;;) {
		const size_t pos = text.find(sep, start);
		if (pos == std::string_view::npos) {
			break;
		}
		if (pos != start) {
			parts.emplace_back(text.substr(start, pos - start));
		}
		start = pos + 1;
	}
	if (start != text.size()) {
		parts.emplace_back(text.substr(start));
	}
	return parts;
}

inline std::string Hex64(uint64_t value) {
	static constexpr char digits[] = "0123456789abcdef";
	std::string           text;
	bool                  started = false;
	for (int shift = 60; shift >= 0; shift -= 4) {
		const auto nibble = static_cast<uint32_t>(value >> static_cast<uint32_t>(shift)) & 0xfu;
		if (nibble != 0 || started || shift == 0) {
			text += digits[nibble];
			started = true;
		}
	}
	return text;
}

} // namespace Detail

// The file text -> spec. False with a refusal "directive", "hex" or "overlap" (the whole file).
inline bool Parse(std::string_view text, Spec* spec, Refusal* refusal) {
	*spec          = Spec {};
	size_t line_no = 0;
	bool   any     = false; // a directive seen
	bool   pvar    = false;
	bool   audio   = false;
	size_t pos     = 0;
	while (pos <= text.size()) {
		size_t end = text.find('\n', pos);
		if (end == std::string_view::npos) {
			end = text.size();
		}
		std::string_view line = text.substr(pos, end - pos);
		pos                   = end + 1;
		line_no++;
		if (const size_t hash = line.find('#'); hash != std::string_view::npos) {
			line = line.substr(0, hash);
		}
		if (!line.empty() && line.back() == '\r') {
			line.remove_suffix(1);
		}
		const auto tokens = Detail::Tokens(line);
		if (tokens.empty()) {
			if (end == text.size()) {
				break;
			}
			continue;
		}
		const std::string_view name = tokens[0];
		if (name == "sha256") {
			if (any) {
				return Detail::Fail(refusal, "directive", line_no, "sha256 not the first directive");
			}
			if (tokens.size() != 2) {
				return Detail::Fail(refusal, "directive", line_no, "sha256 takes one argument");
			}
			if (tokens[1].size() != 64 || !Detail::AllHex(tokens[1])) {
				return Detail::Fail(refusal, "hex", line_no, "sha256 needs 64 hex digits");
			}
			for (char ch: tokens[1]) {
				spec->sha256 += (ch >= 'A' && ch <= 'F') ? static_cast<char>(ch - 'A' + 'a') : ch;
			}
		} else if (!any) {
			return Detail::Fail(refusal, "directive", line_no, "the first directive is not sha256");
		} else if (name == "poke") {
			if (tokens.size() != 2) {
				return Detail::Fail(refusal, "directive", line_no, "poke takes one argument");
			}
			const std::string_view arg   = tokens[1];
			const size_t           colon = arg.find(':');
			if (colon == std::string_view::npos || arg.find(':', colon + 1) != std::string_view::npos) {
				return Detail::Fail(refusal, "hex", line_no, "poke needs <offset>:<bytes>");
			}
			const std::string_view offset = arg.substr(0, colon);
			const std::string_view bytes  = arg.substr(colon + 1);
			if (!Detail::AllHex(offset) || offset.size() > 8) {
				return Detail::Fail(refusal, "hex", line_no, "poke offset is not hex below 0x100000000");
			}
			if (!Detail::AllHex(bytes) || bytes.size() % 2 != 0) {
				return Detail::Fail(refusal, "hex", line_no, "poke bytes are not whole hex bytes");
			}
			Poke poke;
			for (char ch: offset) {
				poke.offset = poke.offset * 16u + Detail::HexValue(ch);
			}
			for (size_t i = 0; i < bytes.size(); i += 2) {
				poke.bytes.push_back(
				    static_cast<uint8_t>(Detail::HexValue(bytes[i]) * 16u + Detail::HexValue(bytes[i + 1])));
			}
			poke.hex = std::string(bytes);
			for (const auto& other: spec->pokes) {
				if (Detail::Overlap(poke.offset, poke.bytes.size(), other.offset, other.bytes.size())) {
					return Detail::Fail(refusal, "overlap", line_no,
					                    "poke " + Detail::Hex64(poke.offset) + " overlaps poke " +
					                        Detail::Hex64(other.offset));
				}
			}
			spec->pokes.push_back(std::move(poke));
		} else if (name == "pvar") {
			if (pvar || tokens.size() != 2 || tokens[1] != "2") {
				return Detail::Fail(refusal, "directive", line_no, "pvar: once, value 2 only");
			}
			pvar        = true;
			spec->pvar2 = true;
		} else if (name == "audio_sync") {
			if (audio || tokens.size() != 2 || tokens[1] != "0") {
				return Detail::Fail(refusal, "directive", line_no, "audio_sync: once, value 0 only");
			}
			audio             = true;
			spec->audio_sync0 = true;
		} else {
			return Detail::Fail(refusal, "directive", line_no, "unknown directive " + std::string(name));
		}
		any = true;
		if (end == text.size()) {
			break;
		}
	}
	if (!any) {
		refusal->reason = "directive";
		refusal->detail = "no sha256";
		return false;
	}
	return true;
}

// An explicit environment against the file: KYTY_PVAR other than "2" with "pvar 2" and KYTY_AUDIO_SYNC that turns the
// guest speed on (atoi != 0, the reading of GuestSpeedEnabled) with "audio_sync 0" - "env"; a KYTY_POKE item, parsed as
// RuntimeLinker::Execute parses it, whose range overlaps a poke of the file - "overlap"; a KYTY_POKE item at an absolute
// address (>= 0x100000000, not checkable against the offsets of the file) - "env".
inline bool CheckEnv(const Spec& spec, const Env& env, Refusal* refusal) {
	if (spec.pvar2 && env.pvar != nullptr && std::string_view(env.pvar) != "2") {
		refusal->reason = "env";
		refusal->detail = "KYTY_PVAR=" + std::string(env.pvar) + " against pvar 2";
		return false;
	}
	if (spec.audio_sync0 && env.audio_sync != nullptr && std::atoi(env.audio_sync) != 0) {
		refusal->reason = "env";
		refusal->detail = "KYTY_AUDIO_SYNC=" + std::string(env.audio_sync) + " against audio_sync 0";
		return false;
	}
	if (env.poke != nullptr) {
		for (const auto& item: Detail::Split(env.poke, ',')) {
			const auto parts = Detail::Split(item, ':');
			// The KYTY_POKE loop skips an item that is not exactly two parts.
			if (parts.size() != 2) {
				continue;
			}
			const uint64_t addr  = std::strtoull(parts[0].c_str(), nullptr, 16);
			const uint64_t count = parts[1].size() / 2; // the loop writes whole byte pairs only
			if (addr >= 0x100000000ull) {
				refusal->reason = "env";
				refusal->detail = "KYTY_POKE at an absolute address " + Detail::Hex64(addr);
				return false;
			}
			for (const auto& poke: spec.pokes) {
				if (Detail::Overlap(addr, count, poke.offset, poke.bytes.size())) {
					refusal->reason = "overlap";
					refusal->detail = "KYTY_POKE " + Detail::Hex64(addr) + " overlaps poke " + Detail::Hex64(poke.offset);
					return false;
				}
			}
		}
	}
	return true;
}

// The whole decision. text - the file (nullptr: not read); eboot_sha256 - lower-case hex of the loaded eboot.bin (asked
// for only after the file parsed, so the caller may hash lazily). True - apply *spec; false - *refusal, *spec cleared.
template <typename HashFn>
bool Decide(const std::string* text, HashFn&& eboot_sha256, const Env& env, Spec* spec, Refusal* refusal) {
	*refusal = Refusal {};
	bool ok  = false;
	if (text == nullptr) {
		refusal->reason = "open";
		refusal->detail = "the file cannot be read";
	} else if (Parse(*text, spec, refusal)) {
		const std::string actual = eboot_sha256();
		if (actual != spec->sha256) {
			refusal->reason = "sha";
			refusal->detail = "file " + spec->sha256.substr(0, 16) + " eboot " + actual.substr(0, 16);
		} else {
			ok = CheckEnv(*spec, env, refusal);
		}
	}
	if (!ok) {
		*spec = Spec {};
	}
	return ok;
}

// --- the emulator part (gamePatchFile.cpp) ---

// Once, on the main thread before Libs::InitAll (PVar::Mode() and the library registration read the decision):
// KYTY_GAME_PATCH unset or empty - returns at once (no file is looked for, no line). Otherwise reads the file, hashes
// elf_host_path and logs "GamePatch: refused reason=..." or "GamePatch: applied sha=... pokes=N pvar=... audio_sync=...".
void Load(const std::filesystem::path& elf_host_path);
// The file applied (false without KYTY_GAME_PATCH and after a refusal).
bool Active();
// The file applied and has "pvar 2" / "audio_sync 0".
bool PvarOn();
bool AudioSyncOff();
// The pokes of the applied file (empty otherwise), written by RuntimeLinker::Execute before KYTY_POKE.
const std::vector<Poke>& Pokes();

} // namespace Loader::GamePatchFile

#endif // KYTY_LOADER_GAME_PATCH_FILE_H_
