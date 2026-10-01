# F6c (HPP-375, ROADMAP s122 item 287(c)): B9a V1 - 16 AudioPropagation functions under KYTY_FIX_B9A (default 0),
# the counter line "AudioPropagation: calls", the test hook; CMakeLists: the audio_propagation_tests target.
# Whole-line anchors; strips CR before matching and restores the file's line ends; writes bytes.
import sys

SRC = 'C:/kyty/KytyPS5/'


def load(path):
    raw = open(SRC + path, 'rb').read()
    crlf = b'\r\n' in raw
    return raw.replace(b'\r\n', b'\n').decode('utf-8'), crlf


def save(path, text, crlf):
    data = text.encode('utf-8')
    if crlf:
        data = data.replace(b'\n', b'\r\n')
    open(SRC + path, 'wb').write(data)


def replace_once(text, old, new, what):
    n = text.count(old)
    if n != 1:
        print('ANCHOR FAIL', what, n)
        sys.exit(1)
    return text.replace(old, new)


# ---------------------------------------------------------------- libAudio.cpp
path = 'src/libs/libAudio.cpp'
t, crlf = load(path)

t = replace_once(t, '#include <memory>\n', '#include <memory>\n#include <string>\n', 'include')

OLD_HANDLE = r'''static AudioPropagationHandle AudioPropagationNextHandle() {
	static std::atomic_uint64_t next_handle {1};
	return next_handle.fetch_add(1, std::memory_order_relaxed);
}
'''

NEW_HANDLE = r'''// Track F, F6 (ROADMAP s122 item 287(c), B9a): KYTY_FIX_B9A (default 0 until the shipment link; 0 - the old path byte
// for byte: the 16 NIDs of the second block of InitAudio_1_AudioPropagation are not registered, nothing is counted
// or logged).  1: V1 of the F6a design (docs/track-f/f6a-b9a.md section 5) - the 16 functions the game imports and the
// emulator did not resolve return 0 with a consistent empty state: PortalCreate and SourceCreate write a new non-zero
// handle (while the handle reads 0 the game creates the source again on every update), SourceGetAudioPathCount and
// SourceGetRays write a zero count, SourceGetAudioPath and SourceRender leave their output alone (no paths; the render
// output keeps the zeros the game wrote), the others only return 0; a null output pointer is never written.
// "AudioPropagation: calls" (only when on) logs the accumulated calls of all 22 functions and the handles issued - on
// the first call of each function and on every 256th call of the library in total.  Order: the import order of the
// game (GOT slots 1233..1254).
enum class B9aFunc : uint32_t {
	SystemUnregisterMaterial,
	SystemSetRays,
	PortalDestroy,
	SystemSetAttributes,
	SourceSetAudioPaths,
	SystemCreate,
	SystemRegisterMaterial,
	PortalSetAttributes,
	PortalCreate,
	RoomDestroy,
	SystemDestroy,
	SourceCreate,
	SourceSetAttributes,
	SourceGetRays,
	SystemQueryMemory,
	SourceGetAudioPathCount,
	SystemGetRays,
	SourceDestroy,
	SourceRender,
	SourceGetAudioPath,
	RoomCreate,
	SourceCalculateAudioPaths,
	Count
};

static constexpr size_t B9A_FUNC_COUNT = static_cast<size_t>(B9aFunc::Count);

static constexpr std::array<const char*, B9A_FUNC_COUNT> B9A_NAMES = {
    "SystemUnregisterMaterial", "SystemSetRays",          "PortalDestroy",
    "SystemSetAttributes",      "SourceSetAudioPaths",    "SystemCreate",
    "SystemRegisterMaterial",   "PortalSetAttributes",    "PortalCreate",
    "RoomDestroy",              "SystemDestroy",          "SourceCreate",
    "SourceSetAttributes",      "SourceGetRays",          "SystemQueryMemory",
    "SourceGetAudioPathCount",  "SystemGetRays",          "SourceDestroy",
    "SourceRender",             "SourceGetAudioPath",     "RoomCreate",
    "SourceCalculateAudioPaths"};

static std::atomic_bool                                     g_b9a_enabled {false};
static std::array<std::atomic_uint64_t, B9A_FUNC_COUNT>     g_b9a_calls {};
static std::atomic_uint64_t                                 g_b9a_total {0};
static std::atomic_uint64_t                                 g_b9a_handles {0};

static void B9aLogCalls(uint64_t total) {
	std::string line = "AudioPropagation: calls total=" + std::to_string(total) +
	                   " handles=" + std::to_string(g_b9a_handles.load(std::memory_order_relaxed));
	for (size_t i = 0; i < B9A_FUNC_COUNT; i++) {
		line += " ";
		line += B9A_NAMES[i];
		line += "=";
		line += std::to_string(g_b9a_calls[i].load(std::memory_order_relaxed));
	}
	LOGF("%s\n", line.c_str());
}

// Called once per call of each of the 22 functions, after its outputs are written.  Off: returns at once.
static void B9aCount(B9aFunc func) {
	if (!g_b9a_enabled.load(std::memory_order_relaxed)) {
		return;
	}
	const bool first =
	    g_b9a_calls[static_cast<size_t>(func)].fetch_add(1, std::memory_order_relaxed) == 0;
	const uint64_t total = g_b9a_total.fetch_add(1, std::memory_order_relaxed) + 1;
	if (first || total % 256 == 0) {
		B9aLogCalls(total);
	}
}

// Test hook (tests/AudioPropagationTests.cpp): index < 22 - the calls of B9aFunc index, 22 - the total, 23 - the
// handles issued while on; any other index - 0.
uint64_t AudioPropagationB9aCounterForTest(uint32_t index);
uint64_t AudioPropagationB9aCounterForTest(uint32_t index) {
	if (index < B9A_FUNC_COUNT) {
		return g_b9a_calls[index].load(std::memory_order_relaxed);
	}
	if (index == B9A_FUNC_COUNT) {
		return g_b9a_total.load(std::memory_order_relaxed);
	}
	if (index == B9A_FUNC_COUNT + 1) {
		return g_b9a_handles.load(std::memory_order_relaxed);
	}
	return 0;
}

static AudioPropagationHandle AudioPropagationNextHandle() {
	static std::atomic_uint64_t next_handle {1};
	if (g_b9a_enabled.load(std::memory_order_relaxed)) {
		g_b9a_handles.fetch_add(1, std::memory_order_relaxed);
	}
	return next_handle.fetch_add(1, std::memory_order_relaxed);
}
'''
t = replace_once(t, OLD_HANDLE, NEW_HANDLE, 'next handle')

# the 6 existing functions: a count before their "return 0;" (no other change)
COUNTS = [
    ('		out_memory->size_gpu_mem = 0;\n	}\n\n	return 0;\n',
     '		out_memory->size_gpu_mem = 0;\n	}\n\n	B9aCount(B9aFunc::SystemQueryMemory);\n	return 0;\n'),
    ('		*out_system_handle = AudioPropagationNextHandle();\n	}\n\n	return 0;\n',
     '		*out_system_handle = AudioPropagationNextHandle();\n	}\n\n	B9aCount(B9aFunc::SystemCreate);\n	return 0;\n'),
    ('		*out_room_handle = AudioPropagationNextHandle();\n	}\n\n	return 0;\n',
     '		*out_room_handle = AudioPropagationNextHandle();\n	}\n\n	B9aCount(B9aFunc::RoomCreate);\n	return 0;\n'),
    ('		*out_material_handle = AudioPropagationNextHandle();\n	}\n\n	return 0;\n',
     '		*out_material_handle = AudioPropagationNextHandle();\n	}\n\n	B9aCount(B9aFunc::SystemRegisterMaterial);\n	return 0;\n'),
    ('                                    const void* /*attributes*/, uint32_t /*num_attributes*/) {\n	PRINT_NAME();\n\n	return 0;\n',
     '                                    const void* /*attributes*/, uint32_t /*num_attributes*/) {\n	PRINT_NAME();\n\n	B9aCount(B9aFunc::SystemSetAttributes);\n	return 0;\n'),
    ('		*num_rays = 0;\n	}\n\n	return 0;\n',
     '		*num_rays = 0;\n	}\n\n	B9aCount(B9aFunc::SystemGetRays);\n	return 0;\n'),
]
for old, new in COUNTS:
    t = replace_once(t, old, new, old.split('\n')[0].strip())

OLD_DEFINE = r'''LIB_DEFINE(InitAudio_1_AudioPropagation) {
	LIB_FUNC("7xyAxrusLko", LibAudioPropagation::AudioPropagationSystemQueryMemory);
	LIB_FUNC("aNEqtSHdUSo", LibAudioPropagation::AudioPropagationSystemCreate);
	LIB_FUNC("8bI5h8req30", LibAudioPropagation::AudioPropagationRoomCreate);
	LIB_FUNC("CPLV6G-eXmk", LibAudioPropagation::AudioPropagationSystemRegisterMaterial);
	LIB_FUNC("kIdb+iQUzCs", LibAudioPropagation::AudioPropagationSystemSetAttributes);
	LIB_FUNC("ht-QXT3zGxo", LibAudioPropagation::AudioPropagationSystemGetRays);
}
'''

NEW_DEFINE = r'''// F6 (B9a) V1: the 16 functions below are registered only with KYTY_FIX_B9A=1.  Arguments - the call sites of the
// game (docs/track-f/f6a-b9a.md section 3); the names of the arguments that are not read are [I].

static int32_t KYTY_SYSV_ABI
AudioPropagationSystemUnregisterMaterial(AudioPropagationHandle /*material_handle*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SystemUnregisterMaterial);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSystemSetRays(AudioPropagationHandle /*system_handle*/,
                                                           const void* /*rays*/, uint32_t /*num_rays*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SystemSetRays);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationPortalDestroy(AudioPropagationHandle /*system_handle*/,
                                                           AudioPropagationHandle /*portal_handle*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::PortalDestroy);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceSetAudioPaths(AudioPropagationHandle /*source_handle*/,
                                                                 const void* /*paths*/, uint32_t /*num_paths*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceSetAudioPaths);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationPortalSetAttributes(AudioPropagationHandle /*portal_handle*/,
                                                                 const void* /*attributes*/,
                                                                 uint32_t /*num_attributes*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::PortalSetAttributes);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationPortalCreate(AudioPropagationHandle /*system_handle*/,
                                                          const void* /*options*/,
                                                          AudioPropagationHandle* out_portal_handle) {
	PRINT_NAME();

	if (out_portal_handle != nullptr) {
		*out_portal_handle = AudioPropagationNextHandle();
	}

	B9aCount(B9aFunc::PortalCreate);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationRoomDestroy(AudioPropagationHandle /*system_handle*/,
                                                         AudioPropagationHandle /*room_handle*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::RoomDestroy);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSystemDestroy(AudioPropagationHandle /*system_handle*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SystemDestroy);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceCreate(AudioPropagationHandle /*system_handle*/,
                                                          AudioPropagationHandle* out_source_handle) {
	PRINT_NAME();

	if (out_source_handle != nullptr) {
		*out_source_handle = AudioPropagationNextHandle();
	}

	B9aCount(B9aFunc::SourceCreate);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceSetAttributes(AudioPropagationHandle /*source_handle*/,
                                                                 const void* /*attributes*/,
                                                                 uint32_t /*num_attributes*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceSetAttributes);
	return 0;
}

// No rays: the game then hands its own tracer (a virtual call after this one) a zero count, as with SystemGetRays.
static int32_t KYTY_SYSV_ABI AudioPropagationSourceGetRays(AudioPropagationHandle /*source_handle*/,
                                                           void* /*rays*/, uint32_t* num_rays) {
	PRINT_NAME();

	if (num_rays != nullptr) {
		*num_rays = 0;
	}

	B9aCount(B9aFunc::SourceGetRays);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceGetAudioPathCount(AudioPropagationHandle /*source_handle*/,
                                                                     uint32_t* num_paths) {
	PRINT_NAME();

	if (num_paths != nullptr) {
		*num_paths = 0;
	}

	B9aCount(B9aFunc::SourceGetAudioPathCount);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceDestroy(AudioPropagationHandle /*system_handle*/,
                                                           AudioPropagationHandle /*source_handle*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceDestroy);
	return 0;
}

// The output is not written: no propagation is rendered, the bus gets the zeros the game cleared the output to.
static int32_t KYTY_SYSV_ABI AudioPropagationSourceRender(AudioPropagationHandle /*system_handle*/,
                                                          const void* /*render*/, uint32_t /*num_render*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceRender);
	return 0;
}

// Not reached while SourceGetAudioPathCount gives 0; the output is not written.
static int32_t KYTY_SYSV_ABI AudioPropagationSourceGetAudioPath(AudioPropagationHandle /*source_handle*/,
                                                                uint32_t /*index*/, void* /*out_path*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceGetAudioPath);
	return 0;
}

static int32_t KYTY_SYSV_ABI AudioPropagationSourceCalculateAudioPaths(
    AudioPropagationHandle /*source_handle*/, const void* /*rays*/, uint32_t /*num_rays*/, uint64_t /*arg3*/,
    void* /*paths*/, uint32_t /*num_paths*/) {
	PRINT_NAME();

	B9aCount(B9aFunc::SourceCalculateAudioPaths);
	return 0;
}

LIB_DEFINE(InitAudio_1_AudioPropagation) {
	LIB_FUNC("7xyAxrusLko", LibAudioPropagation::AudioPropagationSystemQueryMemory);
	LIB_FUNC("aNEqtSHdUSo", LibAudioPropagation::AudioPropagationSystemCreate);
	LIB_FUNC("8bI5h8req30", LibAudioPropagation::AudioPropagationRoomCreate);
	LIB_FUNC("CPLV6G-eXmk", LibAudioPropagation::AudioPropagationSystemRegisterMaterial);
	LIB_FUNC("kIdb+iQUzCs", LibAudioPropagation::AudioPropagationSystemSetAttributes);
	LIB_FUNC("ht-QXT3zGxo", LibAudioPropagation::AudioPropagationSystemGetRays);

	// F6 (B9a): read on each registration (the emulator registers once; the test registers with 0 and with 1).
	const bool fix_b9a = Common::EnvFlagOn("KYTY_FIX_B9A");
	g_b9a_enabled.store(fix_b9a, std::memory_order_relaxed);
	if (fix_b9a) {
		LOGF("FixB9a: on\n");
		LIB_FUNC("XKCN4gpeYsM", LibAudioPropagation::AudioPropagationSystemUnregisterMaterial);
		LIB_FUNC("VlBT16890mA", LibAudioPropagation::AudioPropagationSystemSetRays);
		LIB_FUNC("ZQXE-xS6MTE", LibAudioPropagation::AudioPropagationPortalDestroy);
		LIB_FUNC("5vzOS2pHMFc", LibAudioPropagation::AudioPropagationSourceSetAudioPaths);
		LIB_FUNC("WXMhENV2NcA", LibAudioPropagation::AudioPropagationPortalSetAttributes);
		LIB_FUNC("b-dYXrjSNZU", LibAudioPropagation::AudioPropagationPortalCreate);
		LIB_FUNC("S0JwP2AFTTE", LibAudioPropagation::AudioPropagationRoomDestroy);
		LIB_FUNC("x5VPqg5iyAk", LibAudioPropagation::AudioPropagationSystemDestroy);
		LIB_FUNC("d84otraxt2s", LibAudioPropagation::AudioPropagationSourceCreate);
		LIB_FUNC("-wsUTr31yeg", LibAudioPropagation::AudioPropagationSourceSetAttributes);
		LIB_FUNC("aKJZx7wCma8", LibAudioPropagation::AudioPropagationSourceGetRays);
		LIB_FUNC("G+QLTfyLMYk", LibAudioPropagation::AudioPropagationSourceGetAudioPathCount);
		LIB_FUNC("wkseM3LWPuc", LibAudioPropagation::AudioPropagationSourceDestroy);
		LIB_FUNC("hhz9pITnC8k", LibAudioPropagation::AudioPropagationSourceRender);
		LIB_FUNC("eEeKqFeNI3o", LibAudioPropagation::AudioPropagationSourceGetAudioPath);
		LIB_FUNC("PBcrVpEqUVY", LibAudioPropagation::AudioPropagationSourceCalculateAudioPaths);
	}
}
'''
t = replace_once(t, OLD_DEFINE, NEW_DEFINE, 'lib define')
save(path, t, crlf)
print('patched', path, 'crlf' if crlf else 'lf')

# ---------------------------------------------------------------- CMakeLists.txt
path = 'CMakeLists.txt'
t, crlf = load(path)
OLD_T = 'add_kyty_full_emulator_test(kernel_file_system_tests\n	"${KYTY_TESTS_DIR}/KernelFileSystemTests.cpp")\n'
NEW_T = OLD_T + '\n# Track F, F6 (ROADMAP s122 item 287(c)(4), B9a): the AudioPropagation NIDs through the symbol database, no game.\nadd_kyty_full_emulator_test(audio_propagation_tests\n	"${KYTY_TESTS_DIR}/AudioPropagationTests.cpp")\n'
t = replace_once(t, OLD_T, NEW_T, 'cmake test')
save(path, t, crlf)
print('patched', path, 'crlf' if crlf else 'lf')
print('PATCH OK')
