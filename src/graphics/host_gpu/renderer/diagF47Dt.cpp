#include "graphics/host_gpu/renderer/diagF47Dt.h"

#include "common/envFlag.h"
#include "common/logging/log.h"
#include "common/parallelCopy.h"
#include "graphics/guest_gpu/hardwareContext.h"
#include "graphics/guest_gpu/pm4.h"
#include "graphics/host_gpu/renderer/cache/bufferCache.h"
#include "graphics/host_gpu/renderer/cache/textureCache.h"
#include "graphics/host_gpu/renderer/colorRenderTarget.h"
#include "graphics/host_gpu/renderer/debug.h"
#include "graphics/host_gpu/renderer/depthRenderTarget.h"
#include "graphics/host_gpu/renderer/gpuTimeProfiler.h"
#include "graphics/host_gpu/renderer/pipeline/descriptors.h"
#include "graphics/host_gpu/renderer/pipeline/pipelineCache.h"
#include "graphics/host_gpu/renderer/render.h"
#include "graphics/host_gpu/renderer/renderContext.h"
#include "graphics/shader/shader.h"
#include "graphics/shader/shaderBindings.h"
#include "graphics/shader/recompiler/ir/passes/ResourceMaterialization.h"
#include "graphics/shader/recompiler/ir/passes/SrtWalker.h"
#include "kernel/memory.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cinttypes>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <filesystem>
#include <fmt/format.h>
#include <mutex>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <xxhash.h>

// Track F, F47g (HPP-824, ROADMAP s122 item 740(v)(1)): see diagF47Dt.h.  Hash: XXH3-64 (XXH3_64bits) for value (i),
// the source of value (ii), buffers and the SRT.

namespace Libs::Graphics {
// pipeline/shaders.cpp: the conversions the pipeline creation applies to PipelineStaticParameters (F47g wrappers).
vk::BlendFactor DiagF47DtBlendFactor(uint32_t factor);
vk::BlendOp     DiagF47DtBlendOp(uint32_t op);
} // namespace Libs::Graphics

namespace Libs::Graphics::DiagF47Dt {

namespace {

constexpr uint64_t kDefaultCap   = 2ull << 30u;   // (d): 2 GiB of files
constexpr uint64_t kMaxHashBytes = 512ull << 20u; // a range above this is "too big" (not measured)

// ---------------------------------------------------------------------------------------------------------------
// Configuration (read once, at the first On() of the process)

struct Config {
	std::vector<uint64_t> ps;
	uint32_t              first = 0;
	uint32_t              last  = UINT32_MAX;
};

Config& Cfg() {
	static Config cfg;
	return cfg;
}

void ParseConfig() {
	auto& cfg = Cfg();
	if (const char* list = std::getenv("KYTY_DIAG_F47DT_PS"); list != nullptr && list[0] != '\0') {
		const char* p = list;
		while (*p != '\0') {
			char*      end   = nullptr;
			const auto value = std::strtoull(p, &end, 16);
			if (end == p) {
				p++;
				continue;
			}
			cfg.ps.push_back(value);
			p = end;
		}
	} else {
		cfg.ps.push_back(0x45942b26d9ffbe8eull);
	}
	if (const char* frames = std::getenv("KYTY_DIAG_F47DT_FRAMES"); frames != nullptr && frames[0] != '\0') {
		char* end = nullptr;
		cfg.first = static_cast<uint32_t>(std::strtoul(frames, &end, 10));
		cfg.last  = cfg.first;
		if (end != nullptr && *end == '-') {
			cfg.last = static_cast<uint32_t>(std::strtoul(end + 1, nullptr, 10));
		}
	}
}

// ---------------------------------------------------------------------------------------------------------------
// Guest bytes

bool DefaultReader(uint64_t vaddr, uint64_t size, std::vector<uint8_t>* copy, const uint8_t** ptr) {
	const void* backing = nullptr;
	if (Libs::LibKernel::Memory::TryGetBackingPointer(vaddr, size, &backing)) {
		*ptr = static_cast<const uint8_t*>(backing);
		return true;
	}
	copy->resize(static_cast<size_t>(size));
	if (Libs::LibKernel::Memory::TryReadBacking(vaddr, copy->data(), size) ||
	    Libs::LibKernel::Memory::TryReadPrtBacking(vaddr, copy->data(), size)) {
		*ptr = copy->data();
		return true;
	}
	return false;
}

std::atomic<GuestReader> g_reader {&DefaultReader};
bool                     g_stand = false; // a stand reader is installed: no kernel memory queries
uint64_t                 g_cap   = kDefaultCap;
std::atomic<int64_t>     g_present_override {-1};

uint32_t PresentNow() {
	const auto o = g_present_override.load(std::memory_order_relaxed);
	return o >= 0 ? static_cast<uint32_t>(o) : GpuTimeProfiler::Frame();
}

struct Read {
	bool                 ok   = false;
	const char*          how  = "none"; // map | copy | none | big | zero
	const uint8_t*       data = nullptr;
	std::vector<uint8_t> copy;
};

void ReadGuest(uint64_t vaddr, uint64_t size, Read* r) {
	if (size == 0 || vaddr == 0) {
		r->how = "zero";
		return;
	}
	if (size > kMaxHashBytes) {
		r->how = "big";
		return;
	}
	const uint8_t* ptr = nullptr;
	if (!g_reader.load()(vaddr, size, &r->copy, &ptr)) {
		r->how = "none";
		return;
	}
	r->ok   = true;
	r->data = ptr;
	r->how  = ptr == r->copy.data() ? "copy" : "map";
}

uint64_t Hash(const uint8_t* data, uint64_t size) {
	return XXH3_64bits(data, static_cast<size_t>(size));
}

// ---------------------------------------------------------------------------------------------------------------
// Guest context register words (g)

struct RegName {
	uint32_t    offset;
	const char* name;
};

const std::vector<RegName>& Regs() {
	static const std::vector<RegName> regs = [] {
		std::vector<RegName> r;
		static const char* blend[8] = {"CB_BLEND0_CONTROL", "CB_BLEND1_CONTROL", "CB_BLEND2_CONTROL",
		                               "CB_BLEND3_CONTROL", "CB_BLEND4_CONTROL", "CB_BLEND5_CONTROL",
		                               "CB_BLEND6_CONTROL", "CB_BLEND7_CONTROL"};
		static const char* info[8]  = {"CB_COLOR0_INFO", "CB_COLOR1_INFO", "CB_COLOR2_INFO", "CB_COLOR3_INFO",
		                               "CB_COLOR4_INFO", "CB_COLOR5_INFO", "CB_COLOR6_INFO", "CB_COLOR7_INFO"};
		for (uint32_t t = 0; t < 8; t++) {
			r.push_back({Pm4::CB_BLEND0_CONTROL + t, blend[t]});
		}
		r.push_back({Pm4::CB_TARGET_MASK, "CB_TARGET_MASK"});
		r.push_back({Pm4::CB_SHADER_MASK, "CB_SHADER_MASK"});
		r.push_back({Pm4::CB_COLOR_CONTROL, "CB_COLOR_CONTROL"});
		for (uint32_t t = 0; t < 8; t++) {
			// CB_COLOR<t>_INFO = CB_COLOR0_INFO + 0xF * t (CB_COLOR7_INFO = 0x385 in pm4.h).
			r.push_back({Pm4::CB_COLOR0_INFO + 0xFu * t, info[t]});
		}
		r.push_back({Pm4::DB_ALPHA_TO_MASK, "DB_ALPHA_TO_MASK"});
		r.push_back({Pm4::PA_CL_VPORT_XSCALE, "PA_CL_VPORT_XSCALE"});
		r.push_back({Pm4::PA_CL_VPORT_XOFFSET, "PA_CL_VPORT_XOFFSET"});
		r.push_back({Pm4::PA_CL_VPORT_YSCALE, "PA_CL_VPORT_YSCALE"});
		r.push_back({Pm4::PA_CL_VPORT_YOFFSET, "PA_CL_VPORT_YOFFSET"});
		r.push_back({Pm4::PA_CL_VPORT_ZSCALE, "PA_CL_VPORT_ZSCALE"});
		r.push_back({Pm4::PA_CL_VPORT_ZOFFSET, "PA_CL_VPORT_ZOFFSET"});
		r.push_back({Pm4::PA_SC_SCREEN_SCISSOR_TL, "PA_SC_SCREEN_SCISSOR_TL"});
		r.push_back({Pm4::PA_SC_SCREEN_SCISSOR_BR, "PA_SC_SCREEN_SCISSOR_BR"});
		r.push_back({Pm4::PA_SC_WINDOW_OFFSET, "PA_SC_WINDOW_OFFSET"});
		r.push_back({Pm4::PA_SC_WINDOW_SCISSOR_TL, "PA_SC_WINDOW_SCISSOR_TL"});
		r.push_back({Pm4::PA_SC_WINDOW_SCISSOR_BR, "PA_SC_WINDOW_SCISSOR_BR"});
		r.push_back({Pm4::PA_SC_GENERIC_SCISSOR_TL, "PA_SC_GENERIC_SCISSOR_TL"});
		r.push_back({Pm4::PA_SC_GENERIC_SCISSOR_BR, "PA_SC_GENERIC_SCISSOR_BR"});
		r.push_back({Pm4::PA_SC_VPORT_SCISSOR_0_TL, "PA_SC_VPORT_SCISSOR_0_TL"});
		r.push_back({Pm4::PA_SC_VPORT_SCISSOR_0_BR, "PA_SC_VPORT_SCISSOR_0_BR"});
		r.push_back({Pm4::PA_SC_VPORT_ZMIN_0, "PA_SC_VPORT_ZMIN_0"});
		r.push_back({Pm4::PA_SC_VPORT_ZMAX_0, "PA_SC_VPORT_ZMAX_0"});
		r.push_back({Pm4::PA_SC_MODE_CNTL_0, "PA_SC_MODE_CNTL_0"});
		r.push_back({Pm4::DB_DEPTH_CONTROL, "DB_DEPTH_CONTROL"});
		r.push_back({Pm4::PA_SU_SC_MODE_CNTL, "PA_SU_SC_MODE_CNTL"});
		return r;
	}();
	return regs;
}

int RegIndex(uint32_t offset) {
	const auto& regs = Regs();
	for (size_t i = 0; i < regs.size(); i++) {
		if (regs[i].offset == offset) {
			return static_cast<int>(i);
		}
	}
	return -1;
}

// state: 0 = never written in this context object, 1 = written (value), 2 = reset / clear after the last write.
struct Shadow {
	const void*           ctx = nullptr;
	std::vector<uint32_t> value;
	std::vector<uint8_t>  state;
	std::vector<uint8_t>  path;
	std::vector<uint64_t> seq;
	uint64_t              resets = 0;
};

std::mutex          g_shadow_mutex;
// A handful of context objects (m_ctx, m_saved_ctx of each processor).  A deque: NoteCtxOp holds a reference to one
// element while ShadowOf may append another.
std::deque<Shadow>  g_shadows;
uint64_t            g_reg_seq = 0;

Shadow& ShadowOf(const void* ctx) {
	for (auto& s: g_shadows) {
		if (s.ctx == ctx) {
			return s;
		}
	}
	auto& s = g_shadows.emplace_back();
	s.ctx   = ctx;
	const auto n = Regs().size();
	s.value.assign(n, 0);
	s.state.assign(n, 0);
	s.path.assign(n, 0);
	s.seq.assign(n, 0);
	return s;
}

// " <name>=<hex>|U|R ... resets=<k>" of the context object ctx (U: never written, R: cleared after the last write).
void AppendRegs(std::string* s, const void* ctx) {
	std::lock_guard slock(g_shadow_mutex);
	const auto&     regs = Regs();
	const Shadow*   sh   = nullptr;
	for (const auto& x: g_shadows) {
		if (x.ctx == ctx) {
			sh = &x;
		}
	}
	for (size_t r = 0; r < regs.size(); r++) {
		if (sh == nullptr || sh->state[r] == 0) {
			fmt::format_to(std::back_inserter(*s), " {}=U", regs[r].name);
		} else if (sh->state[r] == 2) {
			fmt::format_to(std::back_inserter(*s), " {}=R", regs[r].name);
		} else {
			fmt::format_to(std::back_inserter(*s), " {}={:08x}", regs[r].name, sh->value[r]);
		}
	}
	fmt::format_to(std::back_inserter(*s), " resets={}", sh != nullptr ? sh->resets : 0);
}

// ---------------------------------------------------------------------------------------------------------------
// Upload records (source of value (ii))

const char* KindName(SrcKind k) {
	switch (k) {
		case SrcKind::None: return "none";
		case SrcKind::Owner: return "owner";
		case SrcKind::Gpu: return "gpu";
		case SrcKind::Import: return "import";
		case SrcKind::Staging: return "staging";
		case SrcKind::StagingAsync: return "staging_async";
	}
	return "?";
}

// st: hashed | pending | lost (ring generation moved before the pooled copy landed) | unmeasured
struct Src {
	SrcKind        kind  = SrcKind::None;
	const char*    st    = "unmeasured";
	const char*    why   = "-";
	uint64_t       hash  = 0;
	int            exact = 0; // 1: the hashed bytes ARE the bytes the upload read; 0: see why
	// pending (StagingAsync)
	const uint8_t* bytes      = nullptr;
	const void*    ring       = nullptr;
	RingGeneration ring_gen   = nullptr;
	uint64_t       generation = 0;
	uint64_t       copy_seq   = 0;
};

struct SrcNote {
	bool     valid = false;
	uint64_t vaddr = 0;
	uint64_t size  = 0;
	Src      src;
};

thread_local SrcNote t_note;

struct Upload {
	Src      src;
	uint32_t image_index = UINT32_MAX;
	uint32_t n           = 0;
	uint32_t d           = 0; // the draw number the next OnDraw of present n gets
	uint64_t seq         = 0; // global upload sequence
	uint32_t first_level = 0;
	uint32_t level_count = 0;
	uint32_t pending     = 0; // pending_levels after the upload
	bool     completion  = false;
	bool     referenced  = false; // printed as pending by a draw: print its resolution
};

struct Record {
	Upload cur;
	Upload prev; // valid when cur.completion (the levels uploaded before the pending completion)
	bool   has_prev = false;
};

struct KeyHash {
	size_t operator()(const std::pair<uint64_t, uint64_t>& k) const noexcept {
		return std::hash<uint64_t> {}(k.first * 0x9e3779b97f4a7c15ull ^ k.second);
	}
};

std::mutex g_mutex; // records, files, counters - GuestGpu thread in practice
std::unordered_map<std::pair<uint64_t, uint64_t>, Record, KeyHash> g_uploads;
std::vector<std::pair<uint64_t, uint64_t>>                           g_pending; // keys with a pending cur or prev
uint64_t                                                             g_upload_seq = 0;

// Draw numbering: d of present n.
uint32_t g_last_n = UINT32_MAX;
uint32_t g_next_d = 0;

// Files and counters (e).
std::unordered_set<std::string> g_files;
uint64_t                        g_file_bytes = 0;
uint64_t                        g_file_count = 0;
bool                            g_capped     = false;
uint64_t                        g_draws      = 0;
std::set<uint32_t>              g_frames;
uint64_t                        g_imgs = 0, g_bufs = 0;

void ResolveOne(Upload* u, uint64_t address, uint64_t size) {
	auto& s = u->src;
	if (std::strcmp(s.st, "pending") != 0) {
		return;
	}
	if (Common::AsyncCopyCompleted() < s.copy_seq) {
		return;
	}
	if (s.ring_gen != nullptr && s.ring_gen(s.ring) == s.generation) {
		s.hash  = Hash(s.bytes, size);
		s.st    = "hashed";
		s.exact = 1;
		s.why   = "-";
	} else {
		s.st  = "lost";
		s.why = "ring_generation_moved";
	}
	if (u->referenced) {
		LOGF("F47dt: kind=srcres useq=%" PRIu64 " addr=0x%010" PRIx64 " size=0x%" PRIx64 " sst=%s sh=%016" PRIx64
		     " n_res=%u\n",
		     u->seq, address, size, s.st, s.hash, PresentNow());
	}
}

void ResolvePendingLocked() {
	if (g_pending.empty()) {
		return;
	}
	std::vector<std::pair<uint64_t, uint64_t>> keep;
	for (const auto& key: g_pending) {
		auto it = g_uploads.find(key);
		if (it == g_uploads.end()) {
			continue;
		}
		ResolveOne(&it->second.cur, key.first, key.second);
		if (it->second.has_prev) {
			ResolveOne(&it->second.prev, key.first, key.second);
		}
		const bool still = std::strcmp(it->second.cur.src.st, "pending") == 0 ||
		                   (it->second.has_prev && std::strcmp(it->second.prev.src.st, "pending") == 0);
		if (still) {
			keep.push_back(key);
		}
	}
	g_pending.swap(keep);
}

// ---------------------------------------------------------------------------------------------------------------
// Files (d)

const char* WriteFileLocked(uint64_t address, uint64_t hash, const uint8_t* data, uint64_t size, uint32_t n,
                            uint32_t d) {
	if (data == nullptr || size == 0) {
		return "-";
	}
	char name[64];
	std::snprintf(name, sizeof(name), "%016" PRIx64 "_%016" PRIx64 ".bin", address, hash);
	if (g_files.count(name) != 0) {
		return "dup";
	}
	if (g_capped) {
		return "capped";
	}
	if (g_file_bytes + size > g_cap) {
		g_capped = true;
		LOGF("F47dt: capped n=%u d=%u addr=0x%010" PRIx64 " size=0x%" PRIx64 " bytes=%" PRIu64 " cap=%" PRIu64 "\n", n,
		     d, address, size, g_file_bytes, g_cap);
		return "capped";
	}
	std::error_code ec;
	std::filesystem::create_directories("_f47dt", ec);
	const auto path = std::string("_f47dt/") + name;
	FILE*      f    = std::fopen(path.c_str(), "wb");
	if (f == nullptr) {
		return "fopen_failed";
	}
	const auto written = std::fwrite(data, 1, static_cast<size_t>(size), f);
	std::fclose(f);
	if (written != size) {
		return "short_write";
	}
	g_files.insert(name);
	g_file_bytes += size;
	g_file_count++;
	return "new";
}

// ---------------------------------------------------------------------------------------------------------------
// Value (i) and the record of one image range, the common part of OnDraw and StandImage.

void AppendSrc(std::string* s, const char* p, const Upload& u) {
	fmt::format_to(std::back_inserter(*s),
	               " {}k={} {}st={} {}why={} {}h={} {}exact={} {}n={} {}d={} {}seq={} {}lv={}+{} {}pend={} {}comp={}",
	               p, KindName(u.src.kind), p, u.src.st, p, u.src.why, p,
	               std::strcmp(u.src.st, "hashed") == 0 ? fmt::format("{:016x}", u.src.hash) : std::string("-"), p,
	               u.src.exact, p, u.n, p, u.d, p, u.seq, p, u.first_level, u.level_count, p, u.pending, p,
	               u.completion ? 1 : 0);
}

// Appends "ih= ihow= igc= ifile= | s*= | cmp=" for [address, address + size) to *s.  n/d: the draw.
void MeasureRangeLocked(std::string* s, uint64_t address, uint64_t size, uint32_t n, uint32_t d) {
	Read r;
	ReadGuest(address, size, &r);
	const uint64_t ih    = r.ok ? Hash(r.data, size) : 0;
	const int      gc    = g_stand ? -1 : (r.ok && Libs::LibKernel::Memory::IsGpuClean(address, size) ? 1 : 0);
	const char*    file  = r.ok ? WriteFileLocked(address, ih, r.data, size, n, d) : "-";
	fmt::format_to(std::back_inserter(*s), " | ih={} ihow={} igc={} ifile={}",
	               r.ok ? fmt::format("{:016x}", ih) : std::string("-"), r.how, gc, file);
	auto it = g_uploads.find({address, size});
	if (it == g_uploads.end()) {
		fmt::format_to(std::back_inserter(*s), " | sk=norecord cmp=und");
		return;
	}
	auto& rec = it->second;
	AppendSrc(s, "s", rec.cur);
	if (std::strcmp(rec.cur.src.st, "pending") == 0) {
		rec.cur.referenced = true;
	}
	if (rec.has_prev) {
		AppendSrc(s, "p", rec.prev);
		if (std::strcmp(rec.prev.src.st, "pending") == 0) {
			rec.prev.referenced = true;
		}
	}
	// Convenience only - the reader recomputes: ne when any hashed source of the content differs from (i).
	const char* cmp = "und";
	if (r.ok) {
		const auto one = [ih](const Upload& u) {
			return std::strcmp(u.src.st, "hashed") != 0 ? 0 : (u.src.hash == ih ? 1 : 2);
		};
		// ne only when the last upload covers every level (no pending levels) and differs; a differing earlier part
		// of a completed deferred upload, or a partial last upload, is "und" (which levels changed is not known).
		const int  c       = one(rec.cur);
		const int  p       = rec.has_prev ? one(rec.prev) : 1;
		const bool partial = rec.cur.pending != 0;
		cmp = (c == 2 && !partial) ? "ne" : ((c == 1 && p == 1 && !partial) ? "eq" : "und");
	}
	fmt::format_to(std::back_inserter(*s), " cmp={} upl_now={}", cmp, (rec.cur.n == n && rec.cur.d == d) ? 1 : 0);
}

char Swz(vk::ComponentSwizzle c) {
	switch (c) {
		case vk::ComponentSwizzle::eIdentity: return 'i';
		case vk::ComponentSwizzle::eZero: return '0';
		case vk::ComponentSwizzle::eOne: return '1';
		case vk::ComponentSwizzle::eR: return 'r';
		case vk::ComponentSwizzle::eG: return 'g';
		case vk::ComponentSwizzle::eB: return 'b';
		case vk::ComponentSwizzle::eA: return 'a';
		default: return '?';
	}
}

std::string Words(const uint32_t* w, uint32_t count) {
	std::string s;
	for (uint32_t i = 0; i < count; i++) {
		fmt::format_to(std::back_inserter(s), "{}{:08x}", i == 0 ? "" : ",", w[i]);
	}
	return s.empty() ? std::string("-") : s;
}

// The PS runtime of the draw being prepared on this thread (ProgramCache::Get, pixel stage).
struct PsRuntime {
	bool                  valid       = false;
	const void*           plan        = nullptr;
	uint64_t              shader_base = 0;
	std::vector<uint32_t> user_data;
};
thread_local PsRuntime t_ps;

// Readers of the re-materialization: the guest backing as it is now, no read cache, no counters (the reader of the
// draw path, ReadShaderLiveMemory, reads the same backing through a per-call page cache; its clean twin reads only
// GPU-clean words). A word that cannot be read fails the materialization.
bool ReadLiveForDiag(void* /*userdata*/, uint64_t address, uint32_t* value) {
	return value != nullptr && Libs::LibKernel::Memory::TryReadBacking(address, value, sizeof(*value));
}
bool ReadCleanForDiag(void* /*userdata*/, uint64_t address, uint32_t* value) {
	return value != nullptr && Libs::LibKernel::Memory::TryReadGpuCleanBacking(address, value, sizeof(*value));
}

// The pipeline key of the draw being prepared on this thread.
struct KeyCopy {
	bool                     valid = false;
	PipelineStaticParameters params;
	PipelineRenderingState   rendering;
};
thread_local KeyCopy t_key;

bool Wanted(uint64_t ps_hash) {
	const auto& ps = Cfg().ps;
	return std::find(ps.begin(), ps.end(), ps_hash) != ps.end();
}

void PrintStat(const char* when) {
	LOGF("F47dtStat: when=%s draws=%" PRIu64 " frames=%zu files=%" PRIu64 " bytes=%" PRIu64 " capped=%d imgs=%" PRIu64
	     " bufs=%" PRIu64 " pending=%zu\n",
	     when, g_draws, g_frames.size(), g_file_count, g_file_bytes, g_capped ? 1 : 0, g_imgs, g_bufs,
	     g_pending.size());
}

} // namespace

bool On() {
	static const bool on = [] {
		const bool value = Common::EnvValueOn(std::getenv("KYTY_DIAG_F47DT"));
		if (value) {
			ParseConfig();
			std::string ps;
			for (const auto h: Cfg().ps) {
				fmt::format_to(std::back_inserter(ps), "{}{:016x}", ps.empty() ? "" : ",", h);
			}
			LOGF("F47dt: mode=1 ps=%s frames=%u-%u hash=xxh3_64 cap=%" PRIu64 " dir=_f47dt\n", ps.c_str(),
			     Cfg().first, Cfg().last, g_cap);
		}
		return value;
	}();
	return on;
}

void NoteCtxWrite(const void* ctx, uint32_t offset, const uint32_t* values, uint32_t count, uint32_t path) {
	if (!On()) {
		return;
	}
	std::lock_guard lock(g_shadow_mutex);
	Shadow* s = nullptr;
	for (uint32_t i = 0; i < count; i++) {
		const int index = RegIndex(offset + i);
		if (index < 0) {
			continue;
		}
		if (s == nullptr) {
			s = &ShadowOf(ctx);
		}
		s->value[index] = values[i];
		s->state[index] = 1;
		s->path[index]  = static_cast<uint8_t>(path);
		s->seq[index]   = ++g_reg_seq;
	}
}

void NoteCtxOp(const void* ctx, const void* saved, CtxOp op) {
	if (!On()) {
		return;
	}
	std::lock_guard lock(g_shadow_mutex);
	const auto clear = [](Shadow& s) {
		for (auto& st: s.state) {
			if (st != 0) {
				st = 2;
			}
		}
		s.resets++;
	};
	auto& c = ShadowOf(ctx);
	switch (op) {
		case CtxOp::Clear: clear(c); break;
		case CtxOp::Push: {
			auto& sv = ShadowOf(saved);
			sv.value = c.value;
			sv.state = c.state;
			sv.path  = c.path;
			sv.seq   = c.seq;
			break;
		}
		case CtxOp::Pop: {
			auto& sv = ShadowOf(saved);
			c.value  = sv.value;
			c.state  = sv.state;
			c.path   = sv.path;
			c.seq    = sv.seq;
			std::fill(sv.state.begin(), sv.state.end(), uint8_t {0}); // m_saved_ctx = {}
			break;
		}
		case CtxOp::PushClear: {
			auto& sv = ShadowOf(saved);
			sv.value = c.value;
			sv.state = c.state;
			sv.path  = c.path;
			sv.seq   = c.seq;
			clear(c);
			break;
		}
		case CtxOp::Reset: {
			clear(c);
			if (saved != nullptr) {
				clear(ShadowOf(saved));
			}
			break;
		}
	}
}

void NoteImageSource(SrcKind kind, uint64_t vaddr, uint64_t size, const uint8_t* bytes, const void* ring,
                     RingGeneration ring_gen, uint64_t generation) {
	if (!On()) {
		return;
	}
	auto& note = t_note;
	note       = {};
	note.valid = true;
	note.vaddr = vaddr;
	note.size  = size;
	auto& s    = note.src;
	s.kind     = kind;
	switch (kind) {
		case SrcKind::Staging:
			// The inline copy has landed (CopyGuestToStaging returned false): the staging bytes ARE the source.
			s.hash  = Hash(bytes, size);
			s.st    = "hashed";
			s.exact = 1;
			break;
		case SrcKind::StagingAsync:
			// Pooled copy: hashed once the pool's completed mark reaches the sequence queued so far, while the ring
			// is still in the generation it was mapped in (StreamBuffer::Generation()); never waited for here.
			s.st         = "pending";
			s.bytes      = bytes;
			s.ring       = ring;
			s.ring_gen   = ring_gen;
			s.generation = generation;
			s.copy_seq   = Common::AsyncCopySequence();
			break;
		case SrcKind::Import: {
			// The upload reads the imported guest pages themselves when the GPU runs the copy; a CPU write fault
			// on them waits for that read (RenderContext::HandleFault -> WaitPendingHostReads). The hash is of
			// the same pages at record time.
			Read r;
			ReadGuest(vaddr, size, &r);
			if (r.ok) {
				s.hash  = Hash(r.data, size);
				s.st    = "hashed";
				s.exact = 0;
				s.why   = "import_at_record";
			} else {
				s.why = r.how;
			}
			break;
		}
		case SrcKind::Owner: s.why = "gpu_buffer_bytes"; break;
		case SrcKind::Gpu: s.why = "gpu_modified_range"; break;
		case SrcKind::None: s.why = "no_source"; break;
	}
}

void NoteImageUpload(uint32_t image_index, uint64_t address, uint64_t size, uint32_t first_level, uint32_t level_count,
                     uint32_t pending_levels, bool pending_completion) {
	if (!On()) {
		return;
	}
	auto note    = t_note;
	t_note.valid = false;
	std::lock_guard lock(g_mutex);
	ResolvePendingLocked();
	Upload u;
	if (note.valid && note.vaddr == address && note.size == size) {
		u.src = note.src;
	} else {
		u.src.why = note.valid ? "note_range_differs" : "no_note";
	}
	const auto n  = PresentNow();
	u.image_index = image_index;
	u.n           = n;
	u.d           = n == g_last_n ? g_next_d : 0;
	u.seq         = ++g_upload_seq;
	u.first_level = first_level;
	u.level_count = level_count;
	u.pending     = pending_levels;
	u.completion  = pending_completion;
	auto& rec     = g_uploads[{address, size}];
	if (pending_completion) {
		rec.prev     = rec.cur;
		rec.has_prev = true;
	} else {
		rec.has_prev = false;
	}
	rec.cur = u;
	if (std::strcmp(u.src.st, "pending") == 0) {
		g_pending.emplace_back(address, size);
	}
}

void NotePsRuntime(const void* resource_plan, uint64_t shader_base, const uint32_t* user_data, size_t count) {
	if (!On()) {
		return;
	}
	t_ps.valid       = true;
	t_ps.plan        = resource_plan;
	t_ps.shader_base = shader_base;
	t_ps.user_data.assign(user_data, user_data + count);
}

void NoteGraphicsKey(const PipelineStaticParameters& params, const PipelineRenderingState& rendering) {
	if (!On()) {
		return;
	}
	t_key.valid     = true;
	t_key.params    = params;
	t_key.rendering = rendering;
}

void OnDraw(RenderContext& context, const CommandBuffer& buffer, const DrawArgs& args) {
	if (!On()) {
		return;
	}
	const bool key_valid = t_key.valid;
	t_key.valid          = false;
	const PsRuntime ps_rt = t_ps;
	t_ps.valid           = false;
	std::lock_guard lock(g_mutex);
	const auto      n = PresentNow();
	if (n != g_last_n) {
		g_last_n = n;
		g_next_d = 0;
	}
	const uint32_t d = g_next_d++;
	if (args.ps == nullptr || !*args.ps || !Wanted(args.ps->program->shader_hash) || n < Cfg().first ||
	    n > Cfg().last) {
		return;
	}
	ResolvePendingLocked();
	g_draws++;
	g_frames.insert(n);
	const auto& program   = *args.ps->program;
	const auto& resources = args.ps->resources;
	const auto* pixel     = args.pixel;
	// (a) header and the raw PS user data
	LOGF("F47dt: kind=draw n=%u d=%u gf=%d submit=%" PRIu64 " draw=%s ps=%016" PRIx64 " vs=%016" PRIx64
	     " idx=%u inst=%u ready=%d images=%zu buffers=%zu samplers=%zu ud=%zu:%s\n",
	     n, d, args.guest_frame, args.submit_id, args.draw_name, program.shader_hash,
	     (args.vs != nullptr && *args.vs) ? args.vs->program->shader_hash : 0u, args.index_count, args.instance_count,
	     args.pipeline_ready ? 1 : 0, program.info.images.size(), program.info.buffers.size(),
	     program.info.samplers.size(), resources.user_data.size(),
	     Words(resources.user_data.data(), static_cast<uint32_t>(resources.user_data.size())).c_str());
	auto& tc = context.GetTextureCache();
	// (b) images
	for (uint32_t i = 0; i < program.info.images.size(); i++) {
		g_imgs++;
		std::string s = fmt::format("F47dt: kind=img n={} d={} i={} cls={}", n, d, i,
		                            program.info.images[i].resource_class ==
		                                    ShaderRecompiler::IR::ImageResourceClass::Sampled
		                                ? "sampled"
		                                : "storage");
		const ShaderRecompiler::IR::DescriptorValue* raw =
		    i < resources.images.size() ? &resources.images[i] : nullptr;
		if (raw != nullptr) {
			fmt::format_to(std::back_inserter(s), " raw={}", Words(raw->dwords.data(), raw->dword_count));
		}
		if (raw != nullptr && raw->dword_count >= 8) {
			const auto t = DecodeNativeDescriptor<ShaderTextureResource>(*raw);
			fmt::format_to(std::back_inserter(s),
			               " base=0x{:010x} fmt={} w={} h={} dep={} lv={}..{} maxmip={} tile={} type={}"
			               " dstsel={},{},{},{} minlod={} bcsw={} pitchx={}",
			               t.Base40(), static_cast<uint32_t>(t.Format()), static_cast<uint32_t>(t.Width5()) + 1u,
			               static_cast<uint32_t>(t.Height5()) + 1u, static_cast<uint32_t>(t.Depth()) + 1u,
			               static_cast<uint32_t>(t.BaseLevel()), static_cast<uint32_t>(t.LastLevel()),
			               static_cast<uint32_t>(t.MaxMip()), static_cast<uint32_t>(t.TileMode()),
			               static_cast<uint32_t>(t.Type()), static_cast<uint32_t>(t.DstSelX()),
			               static_cast<uint32_t>(t.DstSelY()), static_cast<uint32_t>(t.DstSelZ()),
			               static_cast<uint32_t>(t.DstSelW()), static_cast<uint32_t>(t.MinLod()),
			               static_cast<uint32_t>(t.BCSwizzle()), static_cast<uint32_t>(t.ArrayPitch()));
		} else {
			s += " base=- (T# < 8 words)";
		}
		const TextureBinding* b = (pixel != nullptr && i < pixel->images.size()) ? &pixel->images[i] : nullptr;
		if (b == nullptr || !b->image_id) {
			s += " | id=- (no binding)";
			LOGF("%s\n", s.c_str());
			continue;
		}
		const auto& img   = tc.PeekImage(b->image_id);
		const auto  range = img.SourceRange();
		fmt::format_to(std::back_inserter(s),
		               " | id={} img=0x{:010x}+0x{:x} desc=0x{:010x}+0x{:x} pix={} gfmt={} itile={} pitch={} ext={}x{}x{}"
		               " ilv={} ilay={} vkimg_fmt={}",
		               b->image_id.index, range.address, range.size, b->desc.info.data.address,
		               b->desc.info.data.size, vk::to_string(b->desc.info.pixel_format),
		               static_cast<uint32_t>(b->desc.info.guest_format), static_cast<uint32_t>(b->desc.info.tile_mode),
		               b->desc.info.pitch, b->desc.info.extent.width, b->desc.info.extent.height,
		               b->desc.info.extent.depth, b->desc.info.resources.levels, b->desc.info.resources.layers,
		               vk::to_string(img.backing.format));
		// The view bound to the draw: the cached view object of the image whose handle the binding carries.
		const CachedImageView* view = nullptr;
		for (const auto& v: img.views) {
			if (v.view == b->image_view) {
				view = &v;
				break;
			}
		}
		if (view != nullptr) {
			const auto& vi = view->info;
			fmt::format_to(std::back_inserter(s),
			               " | view=1 vfmt={} vmap={}{}{}{} vtype={} vlev={}+{} vlay={}+{} vminlod={} mipviews={}",
			               vk::to_string(vi.format), Swz(vi.mapping.r), Swz(vi.mapping.g), Swz(vi.mapping.b),
			               Swz(vi.mapping.a), vk::to_string(vi.type), vi.base_level, vi.level_count, vi.base_layer,
			               vi.layer_count, vi.min_lod, b->mip_views.size());
		} else {
			fmt::format_to(std::back_inserter(s), " | view=0 vhandle={} mipviews={}", b->image_view ? 1 : 0,
			               b->mip_views.size());
		}
		fmt::format_to(std::back_inserter(s), " | cpu={} maybe={} bufmod={} gpumod={} cache_ok={} pend={}",
		               img.IsDefinitelyCpuDirty() ? 1 : 0, img.IsMaybeCpuDirty() ? 1 : 0,
		               img.IsBufferModified() ? 1 : 0, img.IsGpuModified() ? 1 : 0,
		               (!img.IsCpuDirty() && !img.IsBufferModified()) ? 1 : 0, img.pending_levels);
		MeasureRangeLocked(&s, range.address, range.size, n, d);
		LOGF("%s\n", s.c_str());
	}
	// (c) buffers
	auto&       stream     = context.GetBufferCache().GetUtilityBuffer(MemoryUsage::Stream);
	const auto  ring_hash  = [&stream](const vk::DescriptorBufferInfo& info, std::string* out) {
		if (info.buffer != stream.Handle()) {
			*out = "-";
			return false;
		}
		const auto mapped = stream.Mapped();
		const auto range  = info.range == VK_WHOLE_SIZE ? 0 : info.range;
		if (mapped.empty() || info.offset + range > mapped.size()) {
			*out = "unmapped";
			return true;
		}
		if (Common::AsyncCopyCompleted() < Common::AsyncCopySequence()) {
			*out = "copy_in_flight";
			return true;
		}
		*out = fmt::format("{:016x}", Hash(mapped.data() + info.offset, range));
		return true;
	};
	for (uint32_t i = 0; i < program.info.buffers.size(); i++) {
		g_bufs++;
		std::string s = fmt::format("F47dt: kind=buf n={} d={} i={} rw={}", n, d, i,
		                            program.info.buffers[i].written ? 1 : 0);
		const ShaderRecompiler::IR::DescriptorValue* raw =
		    i < resources.buffers.size() ? &resources.buffers[i] : nullptr;
		if (raw != nullptr) {
			fmt::format_to(std::back_inserter(s), " raw={}", Words(raw->dwords.data(), raw->dword_count));
		}
		if (raw != nullptr && raw->dword_count >= 4) {
			const auto v = DecodeNativeDescriptor<ShaderBufferResource>(*raw);
			fmt::format_to(std::back_inserter(s), " base=0x{:012x} stride={} records={} vsize=0x{:x} fmt={}",
			               v.Base48(), v.Stride(), v.NumRecords(), v.GetSize(), static_cast<uint32_t>(v.Format()));
		}
		if (pixel == nullptr || i >= pixel->buffer_sources.size() || i >= pixel->buffers.size()) {
			s += " | src=- (no binding)";
			LOGF("%s\n", s.c_str());
			continue;
		}
		const auto& src  = pixel->buffer_sources[i];
		const auto& info = pixel->buffers[i];
		Read        r;
		ReadGuest(src.address, src.size, &r);
		const uint64_t gh   = r.ok ? Hash(r.data, src.size) : 0;
		const char*    file = r.ok ? WriteFileLocked(src.address, gh, r.data, src.size, n, d) : "-";
		std::string    given;
		const bool     ring = ring_hash(info, &given);
		fmt::format_to(std::back_inserter(s),
		               " | addr=0x{:012x} size=0x{:x} gh={} ghow={} gfile={} | given={} goff=0x{:x} grange=0x{:x} gvh={}",
		               src.address, src.size, r.ok ? fmt::format("{:016x}", gh) : std::string("-"), r.how, file,
		               ring ? "ring_copy" : (info.buffer ? "cache_buffer" : "null"), info.offset,
		               info.range == VK_WHOLE_SIZE ? 0 : info.range,
		               ring ? given : std::string(info.buffer ? "unmeasured:gpu_memory" : "-"));
		LOGF("%s\n", s.c_str());
	}
	// (c) the flattened SRT (what SMEM loads of the PS read) and the descriptors: the draw's snapshot against a fresh
	// materialization of the same plan from guest memory now (value (i) of the SMEM / user-data inputs).
	if (pixel != nullptr) {
		std::string given;
		const bool  ring = ring_hash(pixel->flattened_srt, &given);
		std::string fresh_s;
		if (!ps_rt.valid || ps_rt.plan == nullptr) {
			fresh_s = "fresh=unmeasured:no_plan";
		} else if (ps_rt.user_data != resources.user_data) {
			fresh_s = "fresh=unmeasured:user_data_differs";
		} else {
			ShaderRecompiler::IR::ResourceSnapshot       fresh;
			ShaderRecompiler::IR::ResourceSpecialization fresh_spec;
			const ShaderRecompiler::IR::SrtRuntime       rt {
			          .user_data                  = std::span<const uint32_t>(ps_rt.user_data),
			          .shader_base                = ps_rt.shader_base,
			          .read_memory                = &ReadLiveForDiag,
			          .userdata                   = nullptr,
			          .read_specialization_memory = &ReadCleanForDiag,
            };
			const bool ok = ShaderRecompiler::IR::MaterializeResources(
			    *static_cast<const ShaderRecompiler::IR::ResourcePlan*>(ps_rt.plan), rt, fresh, fresh_spec);
			if (!ok) {
				fresh_s = "fresh=fail";
			} else {
				fresh_s = fmt::format(
				    "fresh=ok fh={} same_srt={} same_img={} same_buf={} same_smp={} same_ud={}",
				    fresh.flattened_srt.empty()
				        ? std::string("-")
				        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(fresh.flattened_srt.data()),
				                                      fresh.flattened_srt.size() * 4u)),
				    fresh.flattened_srt == resources.flattened_srt ? 1 : 0, fresh.images == resources.images ? 1 : 0,
				    fresh.buffers == resources.buffers ? 1 : 0, fresh.samplers == resources.samplers ? 1 : 0,
				    fresh.user_data == resources.user_data ? 1 : 0);
			}
		}
		const std::string snaph =
		    resources.flattened_srt.empty()
		        ? std::string("-")
		        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(resources.flattened_srt.data()),
		                                      resources.flattened_srt.size() * 4u));
		const std::string sdh =
		    pixel->shader_data.empty()
		        ? std::string("-")
		        : fmt::format("{:016x}", Hash(reinterpret_cast<const uint8_t*>(pixel->shader_data.data()),
		                                      pixel->shader_data.size() * 4u));
		LOGF("F47dt: kind=srt n=%u d=%u words=%zu snaph=%s given=%s gvh=%s %s shader_data=%zu sdh=%s\n", n, d,
		     resources.flattened_srt.size(), snaph.c_str(),
		     ring ? "ring_copy" : (pixel->flattened_srt.buffer ? "other" : "none"), ring ? given.c_str() : "-",
		     fresh_s.c_str(), pixel->shader_data.size(), sdh.c_str());
	}
	// (g) raw guest register words, last write before this draw
	{
		std::string s = fmt::format("F47dt: kind=reg n={} d={}", n, d);
		AppendRegs(&s, &buffer.GetRegisters());
		LOGF("%s\n", s.c_str());
	}
	// (g) the Vulkan state the emulator built: the pipeline key (CreateGraphicsPipelineLocked) and the dynamic state
	// (the same functions SetGraphicsDynamicParams calls)
	{
		const auto& ctx = buffer.GetRegisters();
		std::string s   = fmt::format("F47dt: kind=vk n={} d={} key={}", n, d, key_valid ? 1 : 0);
		if (key_valid) {
			const auto& p  = t_key.params;
			const auto& rd = t_key.rendering;
			fmt::format_to(std::back_inserter(s),
			               " colors={} samples={} cull_front={} cull_back={} face={} poly={} dfmt={}", rd.color_count,
			               p.samples, p.cull_front ? 1 : 0, p.cull_back ? 1 : 0, p.face ? 1 : 0,
			               vk::to_string(p.polygon_mode), vk::to_string(rd.depth_format));
			for (uint32_t t = 0; t < rd.color_count && t < RENDER_COLOR_ATTACHMENTS_MAX; t++) {
				const auto cs = DiagF47DtBlendFactor(p.color_srcblend[t]);
				const auto cd = DiagF47DtBlendFactor(p.color_destblend[t]);
				const auto co = DiagF47DtBlendOp(p.color_comb_fcn[t]);
				// pipeline/shaders.cpp: alpha factors and op are the color ones unless separate_alpha_blend.
				const auto as = p.separate_alpha_blend[t] ? DiagF47DtBlendFactor(p.alpha_srcblend[t]) : cs;
				const auto ad = p.separate_alpha_blend[t] ? DiagF47DtBlendFactor(p.alpha_destblend[t]) : cd;
				const auto ao = p.separate_alpha_blend[t] ? DiagF47DtBlendOp(p.alpha_comb_fcn[t]) : co;
				fmt::format_to(std::back_inserter(s),
				               " t{}:fmt={},mask={:x},be={},cs={},cd={},co={},as={},ad={},ao={},g={}/{}/{}/{}/{}/{}/{}", t,
				               vk::to_string(rd.color_formats[t]), p.color_mask[t], p.blend_enable[t] ? 1 : 0,
				               vk::to_string(cs), vk::to_string(cd), vk::to_string(co), vk::to_string(as),
				               vk::to_string(ad), vk::to_string(ao), p.color_srcblend[t], p.color_comb_fcn[t],
				               p.color_destblend[t], p.alpha_srcblend[t], p.alpha_comb_fcn[t], p.alpha_destblend[t],
				               p.separate_alpha_blend[t] ? 1 : 0);
			}
		}
		vk::Extent2D extent {};
		for (uint32_t c = 0; c < args.color_count; c++) {
			const auto& col  = args.colors[c];
			const auto  slot = col.target_slot;
			const auto  cwe  = render_target_mask_slot(ctx.GetRenderTargetMask(), slot) != 0 ? 1 : 0;
			fmt::format_to(std::back_inserter(s), " rt{}:slot={},img=0x{:010x},vfmt={},cwe={},export=0x{:02x}", c,
			               slot, col.desc.info.data.address, vk::to_string(col.desc.view_info.format), cwe,
			               col.export_mapping.packed);
			if (c == 0 && col.image_id) {
				extent = col.Extent();
			}
		}
		if (args.depth != nullptr) {
			fmt::format_to(std::back_inserter(s), " depth=img:{},test:{},write:{},op:{}", args.depth->image_id ? 1 : 0,
			               args.depth->depth_test_enable ? 1 : 0, args.depth->depth_write_enable ? 1 : 0,
			               vk::to_string(args.depth->depth_compare_op));
		}
		const auto& vp = ctx.GetScreenViewport();
		const auto& g0 = vp.viewports[0];
		if (ctx.GetClipControl().clip_disable) {
			s += " vp0=clip_disable";
		} else {
			fmt::format_to(std::back_inserter(s), " vp0={},{},{},{}", g0.xoffset - g0.xscale, g0.yoffset - g0.yscale,
			               g0.xscale * 2.0f, g0.yscale * 2.0f);
		}
		if (extent.width != 0) {
			const auto sc = calc_final_scissor(vp, ctx.GetScanModeControl(), extent, 0);
			fmt::format_to(std::back_inserter(s), " sc0={},{},{},{}", sc.left, sc.top, sc.right, sc.bottom);
		} else {
			s += " sc0=-";
		}
		LOGF("%s\n", s.c_str());
	}
}

void PrintExitStat() {
	if (!On()) {
		return;
	}
	std::lock_guard lock(g_mutex);
	PrintStat("exit");
}

void SetGuestReaderForStand(GuestReader reader) {
	g_reader.store(reader);
	g_stand = true;
}

void SetFileCapForStand(uint64_t bytes) {
	std::lock_guard lock(g_mutex);
	g_cap = bytes;
}

void SetPresentForStand(uint32_t n) {
	g_present_override.store(n);
}

void StandImage(uint32_t slot, uint64_t address, uint64_t size) {
	if (!On()) {
		return;
	}
	std::lock_guard lock(g_mutex);
	const auto      n = PresentNow();
	if (n != g_last_n) {
		g_last_n = n;
		g_next_d = 0;
	}
	const uint32_t d = g_next_d++;
	ResolvePendingLocked();
	g_draws++;
	g_frames.insert(n);
	g_imgs++;
	std::string s = fmt::format("F47dt: kind=img n={} d={} i={} cls=stand raw=- base=- | id=- img=0x{:010x}+0x{:x}"
	                            " | view=-",
	                            n, d, slot, address, size);
	MeasureRangeLocked(&s, address, size, n, d);
	LOGF("%s\n", s.c_str());
}


void StandRegs(const void* ctx) {
	if (!On()) {
		return;
	}
	std::string s;
	{
		std::lock_guard lock(g_mutex);
		const auto      n = PresentNow();
		if (n != g_last_n) {
			g_last_n = n;
			g_next_d = 0;
		}
		s = fmt::format("F47dt: kind=reg n={} d={}", n, g_next_d++);
	}
	AppendRegs(&s, ctx);
	LOGF("%s\n", s.c_str());
}

} // namespace Libs::Graphics::DiagF47Dt
