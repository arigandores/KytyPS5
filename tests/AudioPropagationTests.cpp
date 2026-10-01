// Track F, F6 (ROADMAP s122 item 287(c)(4), B9a): the 22 AudioPropagation NIDs the game imports, resolved through the
// symbol database the loader uses (no game, no Vulkan device).  KYTY_FIX_B9A=0: 6 resolve (the old HLE), the 16 V1
// functions do not, nothing is counted.  KYTY_FIX_B9A=1: 22 of 22 resolve; every function returns 0; PortalCreate and
// SourceCreate write a non-zero handle, two calls differ; SourceGetAudioPathCount (input 7) and SourceGetRays
// (input 6) write 0; the functions with no output leave every byte of their buffers alone; null outputs do not
// crash; the counter of "AudioPropagation: calls" counts each call and each handle.  Last line: ALL OK.

#include "common/abi.h"
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "loader/symbolDatabase.h"

#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

namespace Libs {
void InitAudio_1(Loader::SymbolDatabase* s);
namespace LibAudioPropagation {
uint64_t AudioPropagationB9aCounterForTest(uint32_t index);
} // namespace LibAudioPropagation
} // namespace Libs

namespace {

using Handle = uint64_t;

struct Nid {
	const char* nid;
	const char* name;
	bool        v1; // registered only with KYTY_FIX_B9A=1
};

// The import order of the game (GOT slots 1233..1254) = the counter index order of libAudio.cpp (B9aFunc).
constexpr std::array<Nid, 22> NIDS = {{
    {"XKCN4gpeYsM", "SystemUnregisterMaterial", true},
    {"VlBT16890mA", "SystemSetRays", true},
    {"ZQXE-xS6MTE", "PortalDestroy", true},
    {"kIdb+iQUzCs", "SystemSetAttributes", false},
    {"5vzOS2pHMFc", "SourceSetAudioPaths", true},
    {"aNEqtSHdUSo", "SystemCreate", false},
    {"CPLV6G-eXmk", "SystemRegisterMaterial", false},
    {"WXMhENV2NcA", "PortalSetAttributes", true},
    {"b-dYXrjSNZU", "PortalCreate", true},
    {"S0JwP2AFTTE", "RoomDestroy", true},
    {"x5VPqg5iyAk", "SystemDestroy", true},
    {"d84otraxt2s", "SourceCreate", true},
    {"-wsUTr31yeg", "SourceSetAttributes", true},
    {"aKJZx7wCma8", "SourceGetRays", true},
    {"7xyAxrusLko", "SystemQueryMemory", false},
    {"G+QLTfyLMYk", "SourceGetAudioPathCount", true},
    {"ht-QXT3zGxo", "SystemGetRays", false},
    {"wkseM3LWPuc", "SourceDestroy", true},
    {"hhz9pITnC8k", "SourceRender", true},
    {"eEeKqFeNI3o", "SourceGetAudioPath", true},
    {"8bI5h8req30", "RoomCreate", false},
    {"PBcrVpEqUVY", "SourceCalculateAudioPaths", true},
}};

enum FuncIndex : uint32_t {
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
	FnCount
};

constexpr uint8_t GUARD = 0xA5;

int g_failures = 0;
int g_checks   = 0;

void Check(bool value, const std::string& text) {
	g_checks++;
	if (!value) {
		g_failures++;
		std::printf("FAIL: %s\n", text.c_str());
	}
}

void SetFixB9a(const char* value) {
#ifdef _WIN32
	_putenv_s("KYTY_FIX_B9A", value);
#else
	setenv("KYTY_FIX_B9A", value, 1);
#endif
}

const Loader::SymbolRecord* Resolve(const Loader::SymbolDatabase& db, const char* nid) {
	Loader::SymbolResolve s {};
	s.name                 = nid;
	s.library              = "AudioPropagation";
	s.library_version      = 1;
	s.module               = "AudioPropagation";
	s.module_version_major = 1;
	s.module_version_minor = 0;
	s.type                 = Loader::SymbolType::Func;
	const auto* exact      = db.Find(s);
	const auto* by_nid     = db.FindByNid(nid, Loader::SymbolType::Func);
	Check(exact == by_nid, std::string("Find == FindByNid for ") + nid);
	return exact;
}

template <typename T>
T Fn(const std::array<const Loader::SymbolRecord*, 22>& r, uint32_t index) {
	return reinterpret_cast<T>(r[index]->vaddr);
}

// A buffer with guard bytes all around the region a function may write.
struct Guarded {
	std::array<uint8_t, 256> bytes {};
	Guarded() { bytes.fill(GUARD); }
	[[nodiscard]] bool Intact(size_t skip_from = 0, size_t skip_size = 0) const {
		for (size_t i = 0; i < bytes.size(); i++) {
			if (i >= skip_from && i < skip_from + skip_size) {
				continue;
			}
			if (bytes[i] != GUARD) {
				return false;
			}
		}
		return true;
	}
	void* At(size_t offset) { return bytes.data() + offset; }
};

constexpr size_t OUT = 64; // offset of the output inside a Guarded

Handle ReadHandle(const Guarded& g) {
	Handle h = 0;
	std::memcpy(&h, g.bytes.data() + OUT, sizeof(h));
	return h;
}

uint32_t ReadU32(const Guarded& g) {
	uint32_t v = 0;
	std::memcpy(&v, g.bytes.data() + OUT, sizeof(v));
	return v;
}

void WriteU32(Guarded& g, uint32_t v) { std::memcpy(g.At(OUT), &v, sizeof(v)); }

uint64_t Counter(uint32_t index) {
	return Libs::LibAudioPropagation::AudioPropagationB9aCounterForTest(index);
}

using FnH      = int32_t KYTY_SYSV_ABI (*)(Handle);
using FnHH     = int32_t KYTY_SYSV_ABI (*)(Handle, Handle);
using FnHPU    = int32_t KYTY_SYSV_ABI (*)(Handle, const void*, uint32_t);
using FnHPHo   = int32_t KYTY_SYSV_ABI (*)(Handle, const void*, Handle*);
using FnHHo    = int32_t KYTY_SYSV_ABI (*)(Handle, Handle*);
using FnHVUo   = int32_t KYTY_SYSV_ABI (*)(Handle, void*, uint32_t*);
using FnHUo    = int32_t KYTY_SYSV_ABI (*)(Handle, uint32_t*);
using FnHUV    = int32_t KYTY_SYSV_ABI (*)(Handle, uint32_t, void*);
using FnCalc   = int32_t KYTY_SYSV_ABI (*)(Handle, const void*, uint32_t, uint64_t, void*, uint32_t);
using FnQuery  = int32_t KYTY_SYSV_ABI (*)(const void*, void*);
using FnCreate = int32_t KYTY_SYSV_ABI (*)(const void*, void*, Handle*);

void CheckOff() {
	SetFixB9a("0");
	Loader::SymbolDatabase db;
	Libs::InitAudio_1(&db);
	int resolved = 0;
	for (const auto& n: NIDS) {
		const auto* r = Resolve(db, n.nid);
		if (r != nullptr) {
			resolved++;
		}
		Check((r != nullptr) == !n.v1, std::string("=0: ") + n.name + (n.v1 ? " not registered" : " registered"));
	}
	Check(resolved == 6, "=0: 6 of 22 resolve (got " + std::to_string(resolved) + ")");
	std::printf("AudioPropagationTests: KYTY_FIX_B9A=0 resolved %d of 22\n", resolved);

	// The old functions count nothing while off.
	auto     create = reinterpret_cast<FnCreate>(Resolve(db, "aNEqtSHdUSo")->vaddr);
	Handle   system = 0;
	Guarded  memory;
	Check(create(nullptr, memory.At(OUT), &system) == 0 && system != 0, "=0: SystemCreate returns 0 and a handle");
	for (uint32_t i = 0; i < FnCount + 2; i++) {
		Check(Counter(i) == 0, "=0: counter " + std::to_string(i) + " stays 0");
	}
}

void CheckOn() {
	SetFixB9a("1");
	Loader::SymbolDatabase db;
	Libs::InitAudio_1(&db);
	std::array<const Loader::SymbolRecord*, 22> r {};
	int                                          resolved = 0;
	for (uint32_t i = 0; i < NIDS.size(); i++) {
		r[i] = Resolve(db, NIDS[i].nid);
		Check(r[i] != nullptr && r[i]->vaddr != 0, std::string("=1: ") + NIDS[i].name + " registered");
		if (r[i] != nullptr) {
			resolved++;
		}
	}
	Check(resolved == 22, "=1: 22 of 22 resolve (got " + std::to_string(resolved) + ")");
	std::printf("AudioPropagationTests: KYTY_FIX_B9A=1 resolved %d of 22\n", resolved);
	if (resolved != 22) {
		return;
	}

	std::array<uint64_t, FnCount> calls {};
	uint64_t                      handles = 0;

	// The 6 old functions, unchanged semantics.
	Guarded memory;
	Check(Fn<FnQuery>(r, SystemQueryMemory)(nullptr, memory.At(OUT)) == 0, "SystemQueryMemory returns 0");
	calls[SystemQueryMemory]++;
	Check(Fn<FnQuery>(r, SystemQueryMemory)(nullptr, nullptr) == 0, "SystemQueryMemory null out");
	calls[SystemQueryMemory]++;
	Guarded system_out;
	Check(Fn<FnCreate>(r, SystemCreate)(nullptr, nullptr, reinterpret_cast<Handle*>(system_out.At(OUT))) == 0,
	      "SystemCreate returns 0");
	calls[SystemCreate]++;
	handles++;
	const Handle system = ReadHandle(system_out);
	Check(system != 0 && system_out.Intact(OUT, sizeof(Handle)), "SystemCreate writes a handle only");
	Guarded room_out;
	Check(Fn<FnHHo>(r, RoomCreate)(system, reinterpret_cast<Handle*>(room_out.At(OUT))) == 0, "RoomCreate returns 0");
	calls[RoomCreate]++;
	handles++;
	Check(ReadHandle(room_out) != 0 && room_out.Intact(OUT, sizeof(Handle)), "RoomCreate writes a handle only");
	Guarded material_out;
	Guarded material_in;
	Check(Fn<FnHPHo>(r, SystemRegisterMaterial)(system, material_in.At(OUT),
	                                            reinterpret_cast<Handle*>(material_out.At(OUT))) == 0,
	      "SystemRegisterMaterial returns 0");
	calls[SystemRegisterMaterial]++;
	handles++;
	Check(ReadHandle(material_out) != 0 && material_out.Intact(OUT, sizeof(Handle)) && material_in.Intact(),
	      "SystemRegisterMaterial writes a handle only");
	Guarded attrs;
	Check(Fn<FnHPU>(r, SystemSetAttributes)(system, attrs.At(OUT), 3) == 0 && attrs.Intact(),
	      "SystemSetAttributes returns 0, input intact");
	calls[SystemSetAttributes]++;
	Guarded rays;
	Guarded rays_count;
	WriteU32(rays_count, 6);
	Check(Fn<FnHVUo>(r, SystemGetRays)(system, rays.At(OUT), reinterpret_cast<uint32_t*>(rays_count.At(OUT))) == 0,
	      "SystemGetRays returns 0");
	calls[SystemGetRays]++;
	Check(ReadU32(rays_count) == 0 && rays_count.Intact(OUT, 4) && rays.Intact(), "SystemGetRays writes count 0 only");

	// PortalCreate, SourceCreate: a non-zero handle, two calls differ, nothing else written.
	Guarded portal_a;
	Guarded portal_b;
	Guarded options;
	Check(Fn<FnHPHo>(r, PortalCreate)(system, options.At(OUT), reinterpret_cast<Handle*>(portal_a.At(OUT))) == 0,
	      "PortalCreate returns 0");
	Check(Fn<FnHPHo>(r, PortalCreate)(system, options.At(OUT), reinterpret_cast<Handle*>(portal_b.At(OUT))) == 0,
	      "PortalCreate returns 0 (2)");
	calls[PortalCreate] += 2;
	handles += 2;
	const Handle portal = ReadHandle(portal_a);
	Check(portal != 0 && ReadHandle(portal_b) != 0 && portal != ReadHandle(portal_b),
	      "PortalCreate: non-zero, two calls differ");
	Check(portal_a.Intact(OUT, sizeof(Handle)) && portal_b.Intact(OUT, sizeof(Handle)) && options.Intact(),
	      "PortalCreate writes the handle only");
	Check(Fn<FnHPHo>(r, PortalCreate)(system, nullptr, nullptr) == 0, "PortalCreate null out");
	calls[PortalCreate]++;

	Guarded source_a;
	Guarded source_b;
	Check(Fn<FnHHo>(r, SourceCreate)(system, reinterpret_cast<Handle*>(source_a.At(OUT))) == 0,
	      "SourceCreate returns 0");
	Check(Fn<FnHHo>(r, SourceCreate)(system, reinterpret_cast<Handle*>(source_b.At(OUT))) == 0,
	      "SourceCreate returns 0 (2)");
	calls[SourceCreate] += 2;
	handles += 2;
	const Handle source = ReadHandle(source_a);
	Check(source != 0 && ReadHandle(source_b) != 0 && source != ReadHandle(source_b),
	      "SourceCreate: non-zero, two calls differ");
	Check(source != portal && source != system, "SourceCreate: differs from the portal and system handles");
	Check(source_a.Intact(OUT, sizeof(Handle)) && source_b.Intact(OUT, sizeof(Handle)),
	      "SourceCreate writes the handle only");
	Check(Fn<FnHHo>(r, SourceCreate)(system, nullptr) == 0, "SourceCreate null out");
	calls[SourceCreate]++;

	// SourceGetAudioPathCount (input 7) and SourceGetRays (input 6): count 0, nothing else written.
	Guarded path_count;
	WriteU32(path_count, 7);
	Check(Fn<FnHUo>(r, SourceGetAudioPathCount)(source, reinterpret_cast<uint32_t*>(path_count.At(OUT))) == 0,
	      "SourceGetAudioPathCount returns 0");
	calls[SourceGetAudioPathCount]++;
	Check(ReadU32(path_count) == 0 && path_count.Intact(OUT, 4), "SourceGetAudioPathCount writes 0 only");
	Check(Fn<FnHUo>(r, SourceGetAudioPathCount)(source, nullptr) == 0, "SourceGetAudioPathCount null out");
	calls[SourceGetAudioPathCount]++;

	Guarded source_rays;
	Guarded source_rays_count;
	WriteU32(source_rays_count, 6);
	Check(Fn<FnHVUo>(r, SourceGetRays)(source, source_rays.At(OUT),
	                                   reinterpret_cast<uint32_t*>(source_rays_count.At(OUT))) == 0,
	      "SourceGetRays returns 0");
	calls[SourceGetRays]++;
	Check(ReadU32(source_rays_count) == 0 && source_rays_count.Intact(OUT, 4) && source_rays.Intact(),
	      "SourceGetRays writes count 0 only, rays intact");
	Check(Fn<FnHVUo>(r, SourceGetRays)(source, nullptr, nullptr) == 0, "SourceGetRays null out");
	calls[SourceGetRays]++;

	// No output: every byte of every buffer stays.
	{
		Guarded a;
		Check(Fn<FnHPU>(r, PortalSetAttributes)(portal, a.At(OUT), 5) == 0 && a.Intact(), "PortalSetAttributes");
		calls[PortalSetAttributes]++;
		Check(Fn<FnHPU>(r, PortalSetAttributes)(0, nullptr, 0) == 0, "PortalSetAttributes null");
		calls[PortalSetAttributes]++;
	}
	{
		Guarded a;
		Check(Fn<FnHPU>(r, SourceSetAttributes)(source, a.At(OUT), 3) == 0 && a.Intact(), "SourceSetAttributes");
		calls[SourceSetAttributes]++;
		Check(Fn<FnHPU>(r, SourceSetAttributes)(source, nullptr, 0) == 0, "SourceSetAttributes null");
		calls[SourceSetAttributes]++;
	}
	{
		Guarded a;
		Check(Fn<FnHPU>(r, SystemSetRays)(system, a.At(OUT), 6) == 0 && a.Intact(), "SystemSetRays");
		calls[SystemSetRays]++;
		Check(Fn<FnHPU>(r, SystemSetRays)(system, nullptr, 0) == 0, "SystemSetRays null");
		calls[SystemSetRays]++;
	}
	{
		Guarded a;
		Check(Fn<FnHPU>(r, SourceSetAudioPaths)(source, a.At(OUT), 1) == 0 && a.Intact(), "SourceSetAudioPaths");
		calls[SourceSetAudioPaths]++;
		Check(Fn<FnHPU>(r, SourceSetAudioPaths)(source, nullptr, 0) == 0, "SourceSetAudioPaths null");
		calls[SourceSetAudioPaths]++;
	}
	{
		Guarded in;
		Guarded paths;
		Check(Fn<FnCalc>(r, SourceCalculateAudioPaths)(source, in.At(OUT), 0, 0, paths.At(OUT), 0) == 0 &&
		          in.Intact() && paths.Intact(),
		      "SourceCalculateAudioPaths");
		calls[SourceCalculateAudioPaths]++;
		Check(Fn<FnCalc>(r, SourceCalculateAudioPaths)(source, nullptr, 0, 0, nullptr, 0) == 0,
		      "SourceCalculateAudioPaths null");
		calls[SourceCalculateAudioPaths]++;
	}
	{
		// The render descriptor carries the output pointer; the output (cleared by the game) stays as it was.
		Guarded out;
		Guarded desc;
		void*   out_ptr = out.At(OUT);
		std::memcpy(desc.At(OUT + 24), &out_ptr, sizeof(out_ptr));
		const Guarded desc_before = desc;
		Check(Fn<FnHPU>(r, SourceRender)(system, desc.At(OUT), 1) == 0, "SourceRender returns 0");
		calls[SourceRender]++;
		Check(out.Intact() && std::memcmp(desc.bytes.data(), desc_before.bytes.data(), desc.bytes.size()) == 0,
		      "SourceRender: output and descriptor intact");
		Check(Fn<FnHPU>(r, SourceRender)(system, nullptr, 0) == 0, "SourceRender null");
		calls[SourceRender]++;
	}
	{
		Guarded path;
		Check(Fn<FnHUV>(r, SourceGetAudioPath)(source, 0, path.At(OUT)) == 0 && path.Intact(), "SourceGetAudioPath");
		calls[SourceGetAudioPath]++;
		Check(Fn<FnHUV>(r, SourceGetAudioPath)(source, 0, nullptr) == 0, "SourceGetAudioPath null");
		calls[SourceGetAudioPath]++;
	}
	Check(Fn<FnHH>(r, SourceDestroy)(system, source) == 0, "SourceDestroy");
	calls[SourceDestroy]++;
	Check(Fn<FnHH>(r, PortalDestroy)(system, portal) == 0, "PortalDestroy");
	calls[PortalDestroy]++;
	Check(Fn<FnHH>(r, RoomDestroy)(system, ReadHandle(room_out)) == 0, "RoomDestroy");
	calls[RoomDestroy]++;
	Check(Fn<FnH>(r, SystemUnregisterMaterial)(ReadHandle(material_out)) == 0, "SystemUnregisterMaterial");
	calls[SystemUnregisterMaterial]++;
	Check(Fn<FnH>(r, SystemDestroy)(system) == 0, "SystemDestroy");
	calls[SystemDestroy]++;

	// The counter of "AudioPropagation: calls": each call and each handle.
	uint64_t total = 0;
	for (uint32_t i = 0; i < FnCount; i++) {
		Check(calls[i] >= 1, std::string("called: ") + NIDS[i].name);
		Check(Counter(i) == calls[i], std::string("counter ") + NIDS[i].name + " = " + std::to_string(Counter(i)) +
		                                  ", expected " + std::to_string(calls[i]));
		total += calls[i];
	}
	Check(Counter(FnCount) == total, "counter total = " + std::to_string(Counter(FnCount)) + ", expected " +
	                                     std::to_string(total));
	Check(Counter(FnCount + 1) == handles, "counter handles = " + std::to_string(Counter(FnCount + 1)) +
	                                           ", expected " + std::to_string(handles));
	std::printf("AudioPropagationTests: KYTY_FIX_B9A=1 calls %llu handles %llu\n",
	            static_cast<unsigned long long>(total), static_cast<unsigned long long>(handles));
}

} // namespace

int main() {
	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction = Config::LogDirection::Silent;
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	CheckOff();
	CheckOn();

	std::printf("AudioPropagationTests: checks %d, failures %d\n", g_checks, g_failures);
	if (g_failures != 0) {
		std::printf("FAILED\n");
		return 1;
	}
	std::printf("ALL OK\n");
	return 0;
}
