// Track F, F25 double read failure stand without the game (F37a HPP-761, ROADMAP s122 item 688(e)): what the guest gets
// from the file read entries when both reads of ReadGuestWithRetry (src/kernel/fileSystem.cpp) fail - the direct read
// into the guest buffer and the retry through a host buffer.
// The emulator sources are not changed: the failures are injected by an import table hook of ReadFile in this test
// executable only (all ReadFile calls of the linked emulator code go through the IAT slot of this module). The hook acts
// only on the stand thread while a trial is armed; a failed call returns FALSE, sets *lpNumberOfBytesRead = 0, writes
// nothing and does not move the file pointer ("all or nothing" - the form measured by the F22a host stand).
// Separate CMake target f25_read_fail_stand (EXCLUDE_FROM_ALL, no add_test - not in the default ctest set); the driver
// is docs/track-f/f38a/run_stand_f38a.py (edition 2; edition 1 - docs/track-f/f37a/run_stand_f37a.py).
//
// Edition 2 (F38a HPP-763, ROADMAP s122 item 691(d)(1)): arms E and T added, the emulator log goes to <out.tsv>.log (the
// lines FixF25: of KYTY_FIX_F25 are read there), every row carries the KYTY_FIX_F25 value seen by this process. The knob
// is set by the environment before FileSystem::Initialize; =0 and =1 are separate processes of one build.
//
// Arms (ROADMAP s122 items 688(e)(0)(iii), 691(d)(1)):
//   A - injected failure of the direct read (call 1, ERROR_NOACCESS) and of the retry read (call 2, ERROR_IO_DEVICE);
//   K - control: injected failure of the direct read only (call 1, ERROR_NOACCESS), the retry reads the file (F22a form);
//   Z - no injected failure;
//   E - a read from a position at or past the end of the file (remaining = 0), no injected failure;
//   T - injected failure of call 1; on call 2 the hook shortens the file to the read position through a second host
//       handle of the stand and fails the call (a real end of file after a shortening by another process). After the
//       trial the file is restored through the second handle and checked by sha256 against the original.
// Entries: 0 sceKernelRead (Cg4srZ6TKbU), 1 read (DRuBt2pvICk), 2 _read (AqBioC2vF3I), 3 sceKernelPread (+r3rMFwItV4),
//          4 pread (ezv-RSBNKqI), 5 sceKernelAioSubmitReadCommands (HgX7+AORI58) - all resolved by NID from the libkernel
//          symbol database of this build and called through the SysV ABI, as the guest calls them.
//
// Usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <out.tsv>
// Output: <out.tsv> - one row per trial (header first); <out.tsv>.log - the emulator log; stdout - "FIXF25 env=<v> on=<0|1>",
// the NID resolution, "HOOK slots=<n>", "SHA256 <hex>" of the stand file and "DONE trials=<n>". Exit 0; 2 - bad
// arguments; 3 - hook not installed; 4 - NID not resolved; 5 - stand file setup failed; 6 - the file was not restored
// after a T trial (the row is written first).
#define SDL_MAIN_HANDLED
#include "SDL.h"
#include "common/abi.h"
#include "common/emulatorConfig.h"
#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "graphics/presentation/window/windowInternal.h"
#include "kernel/fileSystem.h"
#include "libs/errno.h"
#include "loader/symbolDatabase.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <memory>
#include <random>
#include <string>
#include <vector>

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <bcrypt.h>
#undef min
#undef max

#pragma comment(lib, "bcrypt.lib")

namespace Libs {
void InitLibKernel_1(Loader::SymbolDatabase* s);
} // namespace Libs

namespace {

namespace FileSystem = Libs::LibKernel::FileSystem;

constexpr int ARM_A = 0;
constexpr int ARM_K = 1;
constexpr int ARM_Z = 2;
constexpr int ARM_E = 3;
constexpr int ARM_T = 4;
constexpr int ARM_COUNT = 5;
constexpr const char* ARM_NAMES[ARM_COUNT] = {"A", "K", "Z", "E", "T"};

constexpr int ENTRY_COUNT = 6;
constexpr const char* ENTRY_NAMES[ENTRY_COUNT] = {"sceKernelRead", "read", "_read", "sceKernelPread", "pread",
                                                  "sceKernelAioSubmitReadCommands"};
constexpr const char* ENTRY_NIDS[ENTRY_COUNT]  = {"Cg4srZ6TKbU", "DRuBt2pvICk", "AqBioC2vF3I",
                                                  "+r3rMFwItV4", "ezv-RSBNKqI", "HgX7+AORI58"};

constexpr uint64_t FILE_SIZE    = 3ull * 1024 * 1024 + 4321;
constexpr uint32_t CANARY       = 32;
constexpr uint8_t  CANARY_BYTE  = 0xA5;
constexpr int      ERRNO_SENTRY = 12345;

using KReadFn  = int64_t KYTY_SYSV_ABI (*)(int, void*, size_t);
using PReadFn  = int64_t KYTY_SYSV_ABI (*)(int, void*, size_t, int64_t);
using RReadFn  = int64_t KYTY_SYSV_ABI (*)(int, void*, uint64_t);

// Layout of KernelAioResult / KernelAioRwRequest of src/libs/libKernel.cpp (file-local there).
struct AioResult {
	int64_t  return_value;
	uint32_t state;
};
struct AioRwRequest {
	int64_t    offset;
	size_t     nbyte;
	void*      buf;
	AioResult* result;
	int32_t    fd;
};
using AioFn = int KYTY_SYSV_ABI (*)(AioRwRequest*, int32_t, int32_t, int32_t*);

uint8_t PatternByte(uint64_t i) {
	return static_cast<uint8_t>((i * 131u + (i >> 8u) * 7u + 0x5Au) & 0xFFu);
}

// ---- ReadFile import hook ----

using ReadFileFn = BOOL(WINAPI*)(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);
ReadFileFn g_real_read_file = nullptr;

struct HookState {
	int      mode       = ARM_Z;
	int      calls      = 0;
	uint64_t c1_buf     = 0;
	uint64_t c2_buf     = 0;
	uint32_t c1_size    = 0;
	uint32_t c2_size    = 0;
	int      injected   = 0;
	HANDLE   trunc_h    = INVALID_HANDLE_VALUE; // T: the second handle of the stand file
	uint64_t trunc_to   = 0;                    // T: the size the file is shortened to on call 2
	int      trunc_done = 0;                    // T: SetEndOfFile succeeded on call 2
	int64_t  size_at_c2 = -1;                   // T: the file size seen through the second handle after the shortening
};
thread_local HookState* t_hook = nullptr;

BOOL WINAPI HookReadFile(HANDLE handle, LPVOID buffer, DWORD size, LPDWORD read, LPOVERLAPPED overlapped) {
	HookState* st = t_hook;
	if (st == nullptr) {
		return g_real_read_file(handle, buffer, size, read, overlapped);
	}
	const int k = ++st->calls;
	if (k == 1) {
		st->c1_buf  = reinterpret_cast<uint64_t>(buffer);
		st->c1_size = size;
	} else if (k == 2) {
		st->c2_buf  = reinterpret_cast<uint64_t>(buffer);
		st->c2_size = size;
	}
	if (st->mode == ARM_T && k == 2) {
		// Shorten the file to the read position through the second handle, then fail the call.
		LARGE_INTEGER to {};
		to.QuadPart = static_cast<LONGLONG>(st->trunc_to);
		if (SetFilePointerEx(st->trunc_h, to, nullptr, FILE_BEGIN) != FALSE && SetEndOfFile(st->trunc_h) != FALSE) {
			st->trunc_done = 1;
		}
		LARGE_INTEGER now {};
		if (GetFileSizeEx(st->trunc_h, &now) != FALSE) {
			st->size_at_c2 = now.QuadPart;
		}
	}
	const bool fail = ((st->mode == ARM_A || st->mode == ARM_T) && (k == 1 || k == 2)) || (st->mode == ARM_K && k == 1);
	if (fail) {
		st->injected++;
		if (read != nullptr) {
			*read = 0;
		}
		SetLastError(k == 1 ? ERROR_NOACCESS : ERROR_IO_DEVICE);
		return FALSE;
	}
	return g_real_read_file(handle, buffer, size, read, overlapped);
}

int InstallReadFileHook() {
	auto* base = reinterpret_cast<uint8_t*>(GetModuleHandleW(nullptr));
	auto* dos  = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
	auto* nt   = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
	const auto& dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
	if (dir.VirtualAddress == 0) {
		return 0;
	}
	int slots = 0;
	for (auto* imp = reinterpret_cast<IMAGE_IMPORT_DESCRIPTOR*>(base + dir.VirtualAddress); imp->Name != 0; ++imp) {
		auto* names = reinterpret_cast<IMAGE_THUNK_DATA*>(
		    base + (imp->OriginalFirstThunk != 0 ? imp->OriginalFirstThunk : imp->FirstThunk));
		auto* funcs = reinterpret_cast<IMAGE_THUNK_DATA*>(base + imp->FirstThunk);
		for (; names->u1.AddressOfData != 0; ++names, ++funcs) {
			if (IMAGE_SNAP_BY_ORDINAL(names->u1.Ordinal)) {
				continue;
			}
			auto* by_name = reinterpret_cast<IMAGE_IMPORT_BY_NAME*>(base + names->u1.AddressOfData);
			if (std::strcmp(reinterpret_cast<const char*>(by_name->Name), "ReadFile") != 0) {
				continue;
			}
			DWORD old = 0;
			if (VirtualProtect(&funcs->u1.Function, sizeof(funcs->u1.Function), PAGE_READWRITE, &old) == FALSE) {
				continue;
			}
			auto* current = reinterpret_cast<ReadFileFn>(funcs->u1.Function);
			if (current != &HookReadFile) {
				if (g_real_read_file == nullptr) {
					g_real_read_file = current;
				}
				funcs->u1.Function = reinterpret_cast<ULONG_PTR>(&HookReadFile);
				slots++;
				std::printf("HOOK module=%s slot=%p real=%p\n", reinterpret_cast<const char*>(base + imp->Name),
				            static_cast<void*>(&funcs->u1.Function), reinterpret_cast<void*>(current));
			}
			VirtualProtect(&funcs->u1.Function, sizeof(funcs->u1.Function), old, &old);
		}
	}
	return slots;
}

// ---- sha256 (BCrypt) ----

std::string Sha256Hex(const uint8_t* data, size_t size) {
	BCRYPT_ALG_HANDLE  alg  = nullptr;
	BCRYPT_HASH_HANDLE hash = nullptr;
	uint8_t            digest[32] {};
	std::string        hex;
	if (BCryptOpenAlgorithmProvider(&alg, BCRYPT_SHA256_ALGORITHM, nullptr, 0) == 0) {
		if (BCryptCreateHash(alg, &hash, nullptr, 0, nullptr, 0, 0) == 0) {
			if (BCryptHashData(hash, const_cast<PUCHAR>(data), static_cast<ULONG>(size), 0) == 0 &&
			    BCryptFinishHash(hash, digest, sizeof(digest), 0) == 0) {
				char b[3];
				for (uint8_t v: digest) {
					std::snprintf(b, sizeof(b), "%02x", v);
					hex += b;
				}
			}
			BCryptDestroyHash(hash);
		}
		BCryptCloseAlgorithmProvider(alg, 0);
	}
	return hex;
}

// The whole stand file through the second handle (the real ReadFile, not the hook); false on a short read.
bool ReadWholeFile(HANDLE h, std::vector<uint8_t>* out) {
	LARGE_INTEGER size {};
	if (GetFileSizeEx(h, &size) == FALSE) {
		return false;
	}
	out->assign(static_cast<size_t>(size.QuadPart), 0);
	LARGE_INTEGER zero {};
	if (SetFilePointerEx(h, zero, nullptr, FILE_BEGIN) == FALSE) {
		return false;
	}
	size_t done = 0;
	while (done < out->size()) {
		DWORD      got  = 0;
		const auto want = static_cast<DWORD>(std::min<size_t>(out->size() - done, 1u << 20));
		if (g_real_read_file(h, out->data() + done, want, &got, nullptr) == FALSE || got == 0) {
			return false;
		}
		done += got;
	}
	return true;
}

// T: write back the file tail from `from` and the original size through the second handle, then compare by sha256.
bool RestoreFile(HANDLE h, const std::vector<uint8_t>& original, const std::string& original_sha, uint64_t from) {
	LARGE_INTEGER at {};
	at.QuadPart = static_cast<LONGLONG>(from);
	if (SetFilePointerEx(h, at, nullptr, FILE_BEGIN) == FALSE) {
		return false;
	}
	uint64_t done = from;
	while (done < original.size()) {
		DWORD      put  = 0;
		const auto want = static_cast<DWORD>(std::min<uint64_t>(original.size() - done, 1u << 20));
		if (WriteFile(h, original.data() + done, want, &put, nullptr) == FALSE || put == 0) {
			return false;
		}
		done += put;
	}
	if (SetEndOfFile(h) == FALSE) {
		return false;
	}
	std::vector<uint8_t> now;
	if (!ReadWholeFile(h, &now) || now.size() != original.size()) {
		return false;
	}
	return Sha256Hex(now.data(), now.size()) == original_sha;
}

// ---- trials ----

struct Entries {
	std::array<uint64_t, ENTRY_COUNT> vaddr {};
};

struct StandFile {
	HANDLE               h2 = INVALID_HANDLE_VALUE; // the second handle (T arm, restore and check)
	std::vector<uint8_t> original;
	std::string          sha;
};

struct Trial {
	int      entry      = 0;
	int      arm        = 0;
	int      index      = 0;
	uint64_t pos_before = 0; // file position before the call (read entries: the read position; pread entries: q)
	uint64_t offset     = 0; // read offset (read entries: = pos_before)
	uint64_t nbytes     = 0;
	uint64_t remaining  = 0;
	uint64_t expected   = 0;
	int64_t  ret        = 0; // value given to the guest (AIO: result.return_value)
	int      err        = 0; // errno after the call (ERRNO_SENTRY = not written)
	int      aio_rc     = 0;
	uint32_t aio_state  = 0;
	int64_t  pos_after  = 0;
	int      calls      = 0;
	int      injected   = 0;
	int      c1_guest   = 0; // call 1 wrote to the guest buffer
	int      c2_host    = 0; // call 2 wrote to a buffer other than the guest one, of nbytes bytes
	int      data_ok    = 0; // the first ret bytes equal the file
	int      canary_ok  = 0; // guard bytes before and after the buffer intact
	int      untouched  = 0; // the whole guest buffer still holds the fill byte
	int      trunc_done = 0; // T: the file was shortened on call 2
	int64_t  size_at_c2 = -1; // T: the file size after the shortening
	int      restore_ok = 0; // T: the file was restored and its sha256 equals the original (other arms: 1, not touched)
};

bool SeekTo(int fd, uint64_t pos) {
	return FileSystem::KernelLseek(fd, static_cast<int64_t>(pos), 0) == static_cast<int64_t>(pos);
}

void RunTrial(const Entries& e, int fd, StandFile& sf, Trial& t, std::mt19937_64& rng) {
	// Position, size: a mix of small, medium and large reads; ~25% reach past the end of the file. remaining > 0 in
	// the arms A, K, Z, T (a read at the end of the file does not take the retry - F22a 2.1 item 1); the arm E reads
	// from a position at or past the end of the file (remaining = 0).
	std::uniform_int_distribution<uint64_t> pos_dist(0, FILE_SIZE - 1);
	uint64_t                                offset = pos_dist(rng);
	if (t.arm == ARM_E) {
		offset = FILE_SIZE + rng() % 4097;
	}
	const uint64_t remaining = offset < FILE_SIZE ? FILE_SIZE - offset : 0;
	const auto     kind      = rng() % 10;
	uint64_t       n         = 0;
	if (kind < 5) {
		n = 1 + rng() % 4096;
	} else if (kind < 8) {
		n = 4097 + rng() % (256u * 1024u);
	} else {
		n = 256u * 1024u + rng() % (2u * 1024u * 1024u);
	}
	if (t.arm != ARM_E && rng() % 4 == 0) {
		n = remaining + 1 + rng() % 4096; // past the end of the file
	}
	t.offset    = offset;
	t.nbytes    = n;
	t.remaining = remaining;
	t.expected  = std::min<uint64_t>(n, remaining);

	const bool is_pread = (t.entry == 3 || t.entry == 4 || t.entry == 5);
	if (is_pread) {
		t.pos_before = pos_dist(rng); // pread does not use nor move the file position
	} else {
		t.pos_before = offset;
	}
	if (!SeekTo(fd, t.pos_before)) {
		std::printf("SEEK FAILED entry=%d index=%d\n", t.entry, t.index);
		std::_Exit(5);
	}

	std::vector<uint8_t> mem(static_cast<size_t>(n) + 2 * CANARY, CANARY_BYTE);
	uint8_t*             buf = mem.data() + CANARY;

	HookState st {};
	st.mode     = t.arm;
	st.trunc_h  = sf.h2;
	st.trunc_to = offset;
	*Libs::Posix::GetErrorAddr() = ERRNO_SENTRY;
	t_hook                       = &st;
	switch (t.entry) {
		case 0: t.ret = reinterpret_cast<KReadFn>(e.vaddr[0])(fd, buf, n); break;
		case 1: t.ret = reinterpret_cast<RReadFn>(e.vaddr[1])(fd, buf, n); break;
		case 2: t.ret = reinterpret_cast<RReadFn>(e.vaddr[2])(fd, buf, n); break;
		case 3: t.ret = reinterpret_cast<PReadFn>(e.vaddr[3])(fd, buf, n, static_cast<int64_t>(offset)); break;
		case 4: t.ret = reinterpret_cast<PReadFn>(e.vaddr[4])(fd, buf, n, static_cast<int64_t>(offset)); break;
		default: {
			AioResult    result {-777, 0};
			AioRwRequest req {static_cast<int64_t>(offset), static_cast<size_t>(n), buf, &result, fd};
			int32_t      id = -1;
			t.aio_rc        = reinterpret_cast<AioFn>(e.vaddr[5])(&req, 1, 0, &id);
			t.ret           = result.return_value;
			t.aio_state     = result.state;
			break;
		}
	}
	t_hook = nullptr;
	t.err  = *Libs::Posix::GetErrorAddr();

	t.calls      = st.calls;
	t.injected   = st.injected;
	t.c1_guest   = (st.c1_buf == reinterpret_cast<uint64_t>(buf)) ? 1 : 0;
	t.c2_host    = (st.calls >= 2 && st.c2_buf != reinterpret_cast<uint64_t>(buf) && st.c2_size == n) ? 1 : 0;
	t.pos_after  = FileSystem::KernelLseek(fd, 0, 1);
	t.trunc_done = st.trunc_done;
	t.size_at_c2 = st.size_at_c2;

	bool data_ok = t.ret >= 0 && static_cast<uint64_t>(t.ret) <= n;
	if (data_ok) {
		for (uint64_t i = 0; i < static_cast<uint64_t>(t.ret); i++) {
			if (buf[i] != PatternByte(offset + i)) {
				data_ok = false;
				break;
			}
		}
	}
	t.data_ok = data_ok ? 1 : 0;
	bool canary_ok = true;
	for (uint32_t i = 0; i < CANARY; i++) {
		if (mem[i] != CANARY_BYTE || mem[CANARY + n + i] != CANARY_BYTE) {
			canary_ok = false;
			break;
		}
	}
	t.canary_ok = canary_ok ? 1 : 0;
	t.untouched = std::all_of(buf, buf + n, [](uint8_t b) { return b == CANARY_BYTE; }) ? 1 : 0;

	t.restore_ok = 1;
	if (t.arm == ARM_T) {
		t.restore_ok = RestoreFile(sf.h2, sf.original, sf.sha, std::min<uint64_t>(offset, FILE_SIZE)) ? 1 : 0;
	}
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 8) {
		std::fprintf(stderr, "usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <out.tsv>\n");
		return 2;
	}
	const uint64_t seed = std::strtoull(argv[1], nullptr, 10);
	std::array<int, ARM_COUNT> counts {};
	for (int a = 0; a < ARM_COUNT; a++) {
		counts[a] = std::atoi(argv[2 + a]);
		if (counts[a] < 0) {
			return 2;
		}
	}
	const std::string out_path = argv[7];

	const char* fix_env = std::getenv("KYTY_FIX_F25");
	const int   fix_on  = Common::EnvValueOn(fix_env) ? 1 : 0;
	std::printf("FIXF25 env=%s on=%d\n", fix_env != nullptr ? fix_env : "(unset)", fix_on);

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction   = Config::LogDirection::File;
	options.printf_output_file = out_path + ".log";
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	// KernelRead / KernelPread call Memory::InvalidateMemory, which needs the installed RenderContext (as in
	// KernelFileSystemTests: a hidden Vulkan window; the stand buffers are host heap, not mapped GPU memory).
	if (SDL_InitSubSystem(SDL_INIT_VIDEO) != 0) {
		std::printf("SDL video init failed\n");
		return 5;
	}
	auto graphics = std::make_unique<Libs::Graphics::WindowContext>();
	graphics->graphic_ctx.screen_width  = 64;
	graphics->graphic_ctx.screen_height = 64;
	graphics->window = SDL_CreateWindow("F25ReadFailStand", 0, 0, 64, 64, SDL_WINDOW_VULKAN | SDL_WINDOW_HIDDEN);
	if (graphics->window == nullptr) {
		std::printf("window failed\n");
		return 5;
	}
	graphics->CreateVulkan();

	Loader::SymbolDatabase db;
	Libs::InitLibKernel_1(&db);
	Entries entries;
	for (int i = 0; i < ENTRY_COUNT; i++) {
		const auto* r = db.FindByNid(ENTRY_NIDS[i], Loader::SymbolType::Func);
		if (r == nullptr) {
			std::printf("NID %s not resolved\n", ENTRY_NIDS[i]);
			return 4;
		}
		entries.vaddr[i] = r->vaddr;
		std::printf("NID %d %s %s vaddr=0x%016" PRIx64 " name=%s\n", i, ENTRY_NIDS[i], ENTRY_NAMES[i], r->vaddr,
		            r->dbg_name.c_str());
	}

	const int slots = InstallReadFileHook();
	std::printf("HOOK slots=%d\n", slots);
	if (slots == 0 || g_real_read_file == nullptr) {
		return 3;
	}

	const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
	const auto dir    = std::filesystem::temp_directory_path() / ("kyty_f25_stand_" + std::to_string(unique));
	std::filesystem::create_directories(dir);
	StandFile sf;
	sf.original.resize(FILE_SIZE);
	for (uint64_t i = 0; i < FILE_SIZE; i++) {
		sf.original[i] = PatternByte(i);
	}
	sf.sha = Sha256Hex(sf.original.data(), sf.original.size());
	{
		std::ofstream out(dir / "f25_stand.bin", std::ios::binary);
		out.write(reinterpret_cast<const char*>(sf.original.data()), static_cast<std::streamsize>(sf.original.size()));
	}
	std::printf("SHA256 %s size %" PRIu64 "\n", sf.sha.c_str(), FILE_SIZE);
	FileSystem::Initialize();
	FileSystem::Mount(dir, "/app0");
	const int fd = FileSystem::KernelOpen("/app0/f25_stand.bin", 0, 0);
	if (fd < 3) {
		std::printf("open failed %d\n", fd);
		return 5;
	}
	sf.h2 = CreateFileW((dir / "f25_stand.bin").wstring().c_str(), GENERIC_READ | GENERIC_WRITE,
	                    FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, nullptr, OPEN_EXISTING,
	                    FILE_ATTRIBUTE_NORMAL, nullptr);
	if (sf.h2 == INVALID_HANDLE_VALUE) {
		std::printf("second handle failed %lu\n", GetLastError());
		return 5;
	}

	FILE* out = std::fopen(out_path.c_str(), "wb");
	if (out == nullptr) {
		return 5;
	}
	std::fprintf(out, "seed\tfix\tentry\tentry_name\tarm\tindex\tpos_before\toffset\tnbytes\tremaining\texpected\tret\terr\t"
	                  "aio_rc\taio_state\tpos_after\tcalls\tinjected\tc1_guest\tc2_host\tdata_ok\tcanary_ok\tuntouched\t"
	                  "trunc_done\tsize_at_c2\trestore_ok\n");

	std::mt19937_64 rng(seed);
	int             total = 0;
	for (int e = 0; e < ENTRY_COUNT; e++) {
		std::vector<int> arms;
		for (int a = 0; a < ARM_COUNT; a++) {
			arms.insert(arms.end(), static_cast<size_t>(counts[a]), a);
		}
		std::shuffle(arms.begin(), arms.end(), rng);
		std::array<int, ARM_COUNT> idx {};
		for (int arm: arms) {
			Trial t {};
			t.entry = e;
			t.arm   = arm;
			t.index = idx[arm]++;
			RunTrial(entries, fd, sf, t, rng);
			std::fprintf(out,
			             "%" PRIu64 "\t%d\t%d\t%s\t%s\t%d\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64 "\t%" PRIu64
			             "\t%" PRId64 "\t%d\t%d\t%u\t%" PRId64 "\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%" PRId64 "\t%d\n",
			             seed, fix_on, t.entry, ENTRY_NAMES[t.entry], ARM_NAMES[t.arm], t.index, t.pos_before, t.offset,
			             t.nbytes, t.remaining, t.expected, t.ret, t.err, t.aio_rc, t.aio_state, t.pos_after, t.calls,
			             t.injected, t.c1_guest, t.c2_host, t.data_ok, t.canary_ok, t.untouched, t.trunc_done,
			             t.size_at_c2, t.restore_ok);
			total++;
			if (t.restore_ok == 0) {
				std::fclose(out);
				std::printf("RESTORE FAILED entry=%d index=%d\n", t.entry, t.index);
				std::fflush(stdout);
				std::_Exit(6);
			}
		}
	}
	std::fclose(out);

	std::vector<uint8_t> last;
	const bool final_ok = ReadWholeFile(sf.h2, &last) && Sha256Hex(last.data(), last.size()) == sf.sha;
	std::printf("FINAL file sha256 equal %d\n", final_ok ? 1 : 0);
	CloseHandle(sf.h2);
	FileSystem::KernelClose(fd);
	FileSystem::Shutdown();
	std::error_code error;
	std::filesystem::remove_all(dir, error);
	graphics.reset();
	subsystems.Destroy();
	std::printf("DONE trials=%d\n", total);
	std::fflush(stdout);
	return 0;
}
