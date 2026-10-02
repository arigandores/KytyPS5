#include "loader/gamePatchFile.h"

#include "common/logging/log.h"

#include <atomic>
#include <cstdlib>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>

// Track P, the opt-in patch file (ROADMAP s122 item 333(d)) - see loader/gamePatchFile.h. Threads: Load runs once on the
// main thread before Libs::InitAll and before the guest entry point, so the guest threads and the loader thread (which
// reads Pokes / PvarOn) are created after it; AudioSyncOff is also read by threads that may already run (the window and
// present threads read the guest TSC), hence the atomic.

namespace Loader::GamePatchFile {

namespace {

bool              g_active = false;
bool              g_pvar   = false;
std::atomic<bool> g_audio_off {false};
std::vector<Poke> g_pokes;

bool ReadFile(const std::filesystem::path& path, std::string* text) {
	std::ifstream file(path, std::ios::binary);
	if (!file) {
		return false;
	}
	text->assign(std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>());
	return !file.bad();
}

// Lower-case hex sha256 of the file; empty if it cannot be read (then it equals no sha256 of a file that parsed).
std::string HashFile(const std::filesystem::path& path) {
	std::ifstream file(path, std::ios::binary);
	if (!file) {
		return {};
	}
	Sha256               hash;
	std::vector<uint8_t> buffer(static_cast<size_t>(1) << 20u);
	for (;;) {
		file.read(reinterpret_cast<char*>(buffer.data()), static_cast<std::streamsize>(buffer.size()));
		const auto got = file.gcount();
		if (got > 0) {
			hash.Update(buffer.data(), static_cast<size_t>(got));
		}
		if (!file) {
			break;
		}
	}
	if (file.bad()) {
		return {};
	}
	return hash.FinalHex();
}

} // namespace

void Load(const std::filesystem::path& elf_host_path) {
	const char* path = std::getenv("KYTY_GAME_PATCH");
	if (path == nullptr || path[0] == '\0') {
		return;
	}
	std::string text;
	const bool  read = ReadFile(std::filesystem::path(path), &text);
	Env         env;
	env.pvar       = std::getenv("KYTY_PVAR");
	env.audio_sync = std::getenv("KYTY_AUDIO_SYNC");
	env.poke       = std::getenv("KYTY_POKE");
	// The eboot is hashed only when the file parsed (Decide asks for it after Parse).
	std::string eboot_sha;
	const auto  hash_eboot = [&] {
		eboot_sha = HashFile(elf_host_path);
		return eboot_sha;
	};
	Spec       spec;
	Refusal    refusal;
	const bool ok = Decide(read ? &text : nullptr, hash_eboot, env, &spec, &refusal);
	LOGF("GamePatch: file %s eboot %s\n", path, elf_host_path.string().c_str());
	if (!ok) {
		LOGF("GamePatch: refused reason=%s\n", refusal.reason.c_str());
		LOGF("GamePatch: detail %s\n", refusal.detail.c_str());
		return;
	}
	g_pokes  = std::move(spec.pokes);
	g_pvar   = spec.pvar2;
	g_active = true;
	g_audio_off.store(spec.audio_sync0, std::memory_order_relaxed);
	LOGF("GamePatch: applied sha=%s pokes=%zu pvar=%s audio_sync=%s\n", eboot_sha.substr(0, 16).c_str(), g_pokes.size(),
	     g_pvar ? "2" : "none", spec.audio_sync0 ? "0" : "none");
}

bool Active() {
	return g_active;
}

bool PvarOn() {
	return g_active && g_pvar;
}

bool AudioSyncOff() {
	return g_audio_off.load(std::memory_order_relaxed);
}

const std::vector<Poke>& Pokes() {
	return g_pokes;
}

} // namespace Loader::GamePatchFile
