#include "libs/diagT188.h"

#include "common/logging/log.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cctype>
#include <chrono>
#include <cinttypes>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>
#include <vulkan/vulkan_core.h>

// Track M, M9d (HPP-869, ROADMAP s122 item 785): the counters, the class table and the readback registry of
// KYTY_DIAG_T188 (diagT188.h). The call sites call these functions only when Mode() >= 1.

namespace Libs::DiagT188 {

namespace {

int ReadMode() {
	const char* value = std::getenv("KYTY_DIAG_T188");
	if (value == nullptr) {
		return 0;
	}
	if (std::strcmp(value, "1") == 0) {
		return 1;
	}
	if (std::strcmp(value, "2") == 0) {
		return 2;
	}
	if (std::strcmp(value, "3") == 0) {
		return 3;
	}
	return 0;
}

std::vector<uint64_t> ReadClassList() {
	std::vector<uint64_t> keys;
	const char*           value = std::getenv("KYTY_DIAG_T188_CLS");
	if (value == nullptr) {
		return keys;
	}
	std::string token;
	const auto  take = [&] {
		bool ok = !token.empty() && token.size() <= 16;
		for (const char c: token) {
			ok = ok && std::isxdigit(static_cast<unsigned char>(c)) != 0;
		}
		if (ok) {
			keys.push_back(std::strtoull(token.c_str(), nullptr, 16));
		}
		token.clear();
	};
	for (const char* p = value; *p != '\0'; p++) {
		if (*p == ',') {
			take();
		} else if (*p != ' ') {
			token.push_back(*p);
		}
	}
	take();
	return keys;
}

} // namespace

int g_mode = ReadMode();

namespace {

const std::vector<uint64_t> g_cls = ReadClassList();

constexpr const char* kNames[] = {
    "part", "part_st", "part_fill", "part_copy", "part_unk", "part_off", "part_synced", "part_dlmem", "reopen", "ep_new",
    "ep_prop", "prop_merge", "w_mipal", "w_inmip", "w_other", "w_bytes", "img_bytes", "img_bytes_unsync",
    "img_full_unsync", "in_pass", "in_pass_unsync", "cl_smp", "cl_rt", "cl_rtclr", "cl_dt", "cl_sto", "cl_clrop",
    "cl_oth", "cl_vo", "cl_cover", "cl_cmp", "cl_msaa", "cl_free", "cl_commit", "cl_copydst", "cl_skip", "cl_none",
    "open", "ep_pend", "pend_done", "pend_drop", "pend_free", "pend_open", "lost_bytes", "lost_pend_bytes", "w_ovf",
    "sync_full", "sync_part", "dl_mem", "ep_bad", "lock_bad", "tint_ep", "tint_mips", "tint_bytes", "tint_part_mips",
    "tint_skip_fmt", "tint_skip_vol", "tint_skip_cls", "tint_skip_cpu", "tint_skip_ovf", "tint_bad", "tint_rb_req",
    "tint_rb0_ok", "tint_rb0_bad", "tint_rb0_none", "tint_rb0_nofmt", "tint_rb1_ok", "tint_rb1_over", "tint_rb1_bad",
    "tint_rb1_none"};
static_assert(std::size(kNames) == static_cast<size_t>(C::Count));

constexpr const char* kClassNames[] = {
    "ev", "ev_st", "ev_fill", "ev_copy", "ev_off", "ev_synced", "ev_dlmem", "ep_new", "ep_prop", "cl_smp", "cl_rt",
    "cl_rtclr", "cl_vo", "cl_commit", "cl_free", "lost_bytes", "lost_pend_bytes", "img_bytes", "tint_ep", "tint_mips",
    "tint_bytes", "tint_skip", "tint_rb0_ok", "tint_rb0_bad", "tint_rb1_ok", "tint_rb1_over", "tint_rb1_bad"};
static_assert(std::size(kClassNames) == static_cast<size_t>(CC::Count));

std::array<std::atomic<uint64_t>, static_cast<size_t>(C::Count)> g_c {};

void Add(C c, uint64_t v = 1) {
	g_c[static_cast<size_t>(c)].fetch_add(v, std::memory_order_relaxed);
}
void Sub(C c) {
	g_c[static_cast<size_t>(c)].fetch_sub(1, std::memory_order_relaxed);
}

struct ClassRec {
	ClassFields                                         f;
	bool                                                has_fields = false;
	std::array<uint64_t, static_cast<size_t>(CC::Count)> c {};
	uint32_t                                            rb_req = 0;
};

// Guards g_classes, g_rb and g_rb_final. Taken after TextureCache::m_lock, never before; no command is recorded and no
// stream buffer is mapped while it is held (a Map may run the deferred callbacks, which take it).
std::mutex                             g_mutex;
std::unordered_map<uint64_t, ClassRec> g_classes;

ClassRec& ClsLocked(uint64_t key, const ClassFields* f) {
	auto& rec = g_classes[key];
	if (f != nullptr && !rec.has_fields) {
		rec.f          = *f;
		rec.has_fields = true;
	}
	return rec;
}

void AddClass(uint64_t key, const ClassFields* f, std::initializer_list<std::pair<CC, uint64_t>> adds) {
	std::scoped_lock lock {g_mutex};
	auto&            rec = ClsLocked(key, f);
	for (const auto& [cc, v]: adds) {
		rec.c[static_cast<size_t>(cc)] += v;
	}
}

struct Rb {
	uint64_t key        = 0;
	uint32_t fmt        = 0;
	uint32_t level      = 0;
	uint32_t x          = 0;
	uint32_t y          = 0;
	uint32_t last_layer = 0;
	uint8_t  st         = 0; // 0 rb0 in flight, 1 rb0 magenta - rb1 due, 2 rb1 in flight, 3 final
	bool     wr         = false;
	bool     abandoned  = false;
};
std::vector<Rb> g_rb;
bool            g_rb_final = false;

std::atomic<uint64_t> g_pushes {0};
std::atomic<bool>     g_mode_printed {false};
std::atomic<bool>     g_exit_printed {false};
ExitHook              g_exit_hook    = nullptr;
void*                 g_exit_context = nullptr;
std::mutex            g_hook_mutex;

uint32_t Popcount(uint32_t v) {
	return static_cast<uint32_t>(std::popcount(v));
}

void CloseEpisode(ImageState& s, Close site) {
	if (Read(C::open) == 0) {
		Add(C::ep_bad); // (b): an open flag with no open episode counted
	}
	s.open = false;
	Sub(C::open);
	Add(static_cast<C>(static_cast<uint32_t>(C::cl_smp) + static_cast<uint32_t>(site)));
	CC cc = CC::Count;
	switch (site) {
		case Close::Smp: cc = CC::cl_smp; break;
		case Close::Rt: cc = CC::cl_rt; break;
		case Close::RtClr: cc = CC::cl_rtclr; break;
		case Close::Vo: cc = CC::cl_vo; break;
		case Close::Commit: cc = CC::cl_commit; break;
		case Close::Free: cc = CC::cl_free; break;
		default: break;
	}
	if (cc != CC::Count) {
		AddClass(s.key, nullptr, {{cc, 1}});
	}
}

// Adds [address, address + size) n SourceRange() to the union of s (merging touching intervals). A union that would need
// more than kSpans intervals keeps its old intervals (the union is then a subset - lost_* an upper bound) and marks the
// episode w_ovf once.
void Join(ImageState& s, const Geometry& g, uint64_t address, uint64_t size) {
	const uint64_t b = std::max(address, g.address);
	const uint64_t e = std::min(address + size, g.address + g.source_size);
	if (b >= e) {
		return;
	}
	std::array<Span, kSpans + 1> all {};
	uint32_t                     count = 0;
	for (uint32_t i = 0; i < s.n; i++) {
		all[count++] = s.w[i];
	}
	all[count++] = {b, e};
	std::sort(all.begin(), all.begin() + count, [](const Span& l, const Span& r) { return l.b < r.b; });
	std::array<Span, kSpans + 1> merged {};
	uint32_t                     m = 0;
	for (uint32_t i = 0; i < count; i++) {
		if (m != 0 && all[i].b <= merged[m - 1].e) {
			merged[m - 1].e = std::max(merged[m - 1].e, all[i].e);
		} else {
			merged[m++] = all[i];
		}
	}
	if (m > kSpans) {
		if (!s.ovf) {
			s.ovf = true;
			Add(C::w_ovf);
		}
		return;
	}
	for (uint32_t i = 0; i < m; i++) {
		s.w[i] = merged[i];
	}
	s.n = static_cast<uint8_t>(m);
}

void DropWait(ImageState& s, C outcome) {
	s.wait = false;
	Sub(C::pend_open);
	Add(outcome);
}

// The levels of [first, end) by their intersection with the union w: lost (no intersection), part (intersects, not
// covered), uploaded (every non-empty level). Adds the lost bytes to *lost.
void LevelMasks(const Geometry& g, uint32_t first, uint32_t end, const Span* w, uint32_t n, uint32_t* lost_mask,
                uint32_t* part_mask, uint32_t* up_mask, uint64_t* lost) {
	*lost_mask = *part_mask = *up_mask = 0;
	*lost                               = 0;
	const uint32_t last                 = std::min({end, g.levels, kLevels});
	for (uint32_t l = first; l < last; l++) {
		const uint64_t size = g.mips[l].size;
		if (size == 0) {
			continue;
		}
		const uint64_t b     = g.address + g.mips[l].offset;
		const uint64_t inter = IntersectLen(b, b + size, w, n);
		*up_mask |= 1u << l;
		*lost += size - inter;
		if (inter == 0) {
			*lost_mask |= 1u << l;
		} else if (inter < size) {
			*part_mask |= 1u << l;
		}
	}
}

// The plan's tint counters and the readbacks of the class (<= K per class).
void Tinted(TintPlan& plan, const Geometry& g, uint32_t mask) {
	plan.mask = mask;
	if (mask == 0) {
		return;
	}
	uint64_t bytes = 0;
	for (uint32_t l = 0; l < kLevels; l++) {
		if ((mask & (1u << l)) != 0) {
			bytes += g.mips[l].size;
		}
	}
	Add(C::tint_mips, Popcount(mask));
	Add(C::tint_bytes, bytes);
	std::scoped_lock lock {g_mutex};
	auto&            rec = ClsLocked(plan.key, nullptr);
	rec.c[static_cast<size_t>(CC::tint_mips)] += Popcount(mask);
	rec.c[static_cast<size_t>(CC::tint_bytes)] += bytes;
	uint32_t quota = K - std::min(K, rec.rb_req);
	for (uint32_t l = 0; l < kLevels && quota != 0; l++) {
		if ((mask & (1u << l)) != 0) {
			plan.rb_mask |= 1u << l;
			quota--;
		}
	}
	const auto requested = Popcount(plan.rb_mask);
	rec.rb_req += requested;
	Add(C::tint_rb_req, requested);
}

void TintEpisode(uint64_t key) {
	Add(C::tint_ep);
	AddClass(key, nullptr, {{CC::tint_ep, 1}});
}

void RbAbandonLocked(ImageState& s) {
	for (uint32_t i = 0; i < s.rb_count; i++) {
		auto& r = g_rb[s.rb_first + i];
		if (r.st == 0) {
			r.abandoned = true;
		} else if (r.st == 1) {
			r.st = 3;
			Add(C::tint_rb1_none);
		}
	}
	s.rb_count = 0;
	s.rb_pend.store(0, std::memory_order_release);
}

} // namespace

void PrintModeLine() {
	if (g_mode_printed.exchange(true)) {
		return;
	}
	if (g_cls.empty()) {
		LOGF("T188: mode=%d cls=all k=%u\n", g_mode, K);
	} else {
		LOGF("T188: mode=%d cls=%u k=%u\n", g_mode, static_cast<uint32_t>(g_cls.size()), K);
	}
}

uint64_t ClassKey(const ClassFields& f) noexcept {
	const uint32_t fields[] = {f.fmt, f.tile, f.w, f.h, f.levels, f.layers, f.cmp, f.samples, f.usage, f.vol};
	uint64_t       hash     = 0xcbf29ce484222325ull;
	for (const uint32_t field: fields) {
		const uint64_t v = field;
		for (uint32_t byte = 0; byte < 8; byte++) {
			hash ^= (v >> (8 * byte)) & 0xffu;
			hash *= 0x100000001b3ull;
		}
	}
	return hash;
}

bool ClassListed(uint64_t key) noexcept {
	return g_cls.empty() || std::find(g_cls.begin(), g_cls.end(), key) != g_cls.end();
}

bool CoversSource(const Geometry& g, uint64_t address, uint64_t size) noexcept {
	return address <= g.address && address + size >= g.address + g.source_size;
}

Shape WShape(const Geometry& g, uint64_t address, uint64_t size) noexcept {
	if (g.volume) {
		return Shape::Other;
	}
	const uint64_t b = std::max(address, g.address);
	const uint64_t e = std::min(address + size, g.address + g.source_size);
	if (b >= e) {
		return Shape::Other;
	}
	const uint64_t rb    = b - g.address;
	const uint64_t re    = e - g.address;
	bool           start = false;
	bool           stop  = false;
	const uint32_t last  = std::min(g.levels, kLevels);
	for (uint32_t l = 0; l < last; l++) {
		if (g.mips[l].size == 0) {
			continue;
		}
		start = start || rb == g.mips[l].offset;
		stop  = stop || re == g.mips[l].offset + g.mips[l].size;
	}
	if (start && stop) {
		return Shape::MipAligned;
	}
	for (uint32_t l = 0; l < last; l++) {
		if (g.mips[l].size != 0 && g.mips[l].offset <= rb && re <= g.mips[l].offset + g.mips[l].size) {
			return Shape::InMip;
		}
	}
	return Shape::Other;
}

uint64_t IntersectLen(uint64_t b, uint64_t e, const Span* w, uint32_t n) noexcept {
	uint64_t len = 0;
	for (uint32_t i = 0; i < n; i++) {
		const uint64_t lo = std::max(b, w[i].b);
		const uint64_t hi = std::min(e, w[i].e);
		if (lo < hi) {
			len += hi - lo;
		}
	}
	return len;
}

bool MagentaCode(uint32_t vk_format, uint8_t code[16], uint32_t* bytes) noexcept {
	std::memset(code, 0, 16);
	const auto put16 = [&](uint32_t i, uint16_t v) { std::memcpy(code + 2 * i, &v, 2); };
	const auto put32 = [&](uint32_t i, uint32_t v) { std::memcpy(code + 4 * i, &v, 4); };
	switch (vk_format) {
		case VK_FORMAT_R8_UNORM:
		case VK_FORMAT_R8_SRGB: code[0] = 255; *bytes = 1; return true;
		case VK_FORMAT_R8G8_UNORM:
		case VK_FORMAT_R8G8_SRGB: code[0] = 255; *bytes = 2; return true;
		case VK_FORMAT_R8G8B8A8_UNORM:
		case VK_FORMAT_R8G8B8A8_SRGB:
		case VK_FORMAT_B8G8R8A8_UNORM:
		case VK_FORMAT_B8G8R8A8_SRGB:
			code[0] = 255;
			code[2] = 255;
			code[3] = 255;
			*bytes  = 4;
			return true;
		case VK_FORMAT_R16_SFLOAT: put16(0, 0x3c00); *bytes = 2; return true;
		case VK_FORMAT_R16G16_SFLOAT: put16(0, 0x3c00); *bytes = 4; return true;
		case VK_FORMAT_R16G16B16A16_SFLOAT:
			put16(0, 0x3c00);
			put16(2, 0x3c00);
			put16(3, 0x3c00);
			*bytes = 8;
			return true;
		case VK_FORMAT_R32_SFLOAT: put32(0, 0x3f800000u); *bytes = 4; return true;
		case VK_FORMAT_R32G32_SFLOAT: put32(0, 0x3f800000u); *bytes = 8; return true;
		case VK_FORMAT_R32G32B32A32_SFLOAT:
			put32(0, 0x3f800000u);
			put32(2, 0x3f800000u);
			put32(3, 0x3f800000u);
			*bytes = 16;
			return true;
		// R 1023 (bits 0-9), G 0, B 1023 (bits 20-29), A 3 (bits 30-31).
		case VK_FORMAT_A2B10G10R10_UNORM_PACK32: put32(0, 0x3ffu | (0x3ffu << 20u) | (3u << 30u)); *bytes = 4; return true;
		// R 1.0 (11-bit float, exponent 15: 0x3c0), G 0, B 1.0 (10-bit float: 0x1e0 at bit 22).
		case VK_FORMAT_B10G11R11_UFLOAT_PACK32: put32(0, 0x3c0u | (0x1e0u << 22u)); *bytes = 4; return true;
		case VK_FORMAT_R16_UNORM: put16(0, 0xffff); *bytes = 2; return true;
		case VK_FORMAT_R16G16B16A16_UNORM:
			put16(0, 0xffff);
			put16(2, 0xffff);
			put16(3, 0xffff);
			*bytes = 8;
			return true;
		default: *bytes = 0; return false;
	}
}

bool TexelIsMagenta(uint32_t vk_format, const uint8_t* texel) noexcept {
	uint8_t  code[16];
	uint32_t bytes = 0;
	if (!MagentaCode(vk_format, code, &bytes)) {
		return false;
	}
	return std::memcmp(code, texel, bytes) == 0;
}

uint32_t VerifyTintPlan(const Geometry& g, uint32_t mask, uint32_t first, uint32_t end, const Span* w, uint32_t n) {
	for (uint32_t l = 0; l < kLevels; l++) {
		if ((mask & (1u << l)) == 0) {
			continue;
		}
		bool bad = l < first || l >= end || l >= g.levels || g.mips[l].size == 0;
		if (!bad && g_mode == 2) {
			const uint64_t b = g.address + g.mips[l].offset;
			bad              = IntersectLen(b, b + g.mips[l].size, w, n) != 0;
		}
		if (bad) {
			Add(C::tint_bad);
			mask &= ~(1u << l);
		}
	}
	return mask;
}

Ev NoteInvalidate(ImageState& s, const Geometry& g, const ClassFields& cf, bool gpu_modified, Writer writer,
                  uint64_t address, uint64_t size, bool in_pass, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return Ev::None;
	}
	const bool covers = CoversSource(g, address, size);
	if (!gpu_modified || covers) {
		if (s.open && covers) {
			CloseEpisode(s, Close::Cover);
			return Ev::Cover;
		}
		if (s.open) {
			Join(s, g, address, size); // executor decision 1 (names_before_code.md s.4)
			return Ev::Join;
		}
		return Ev::None;
	}
	Add(C::part);
	CC wcc = CC::Count;
	switch (writer) {
		case Writer::St: Add(C::part_st); wcc = CC::ev_st; break;
		case Writer::Fill: Add(C::part_fill); wcc = CC::ev_fill; break;
		case Writer::Copy: Add(C::part_copy); wcc = CC::ev_copy; break;
		default: Add(C::part_unk); break;
	}
	const bool off = address != g.address;
	if (off) {
		Add(C::part_off);
	}
	switch (WShape(g, address, size)) {
		case Shape::MipAligned: Add(C::w_mipal); break;
		case Shape::InMip: Add(C::w_inmip); break;
		default: Add(C::w_other); break;
	}
	{
		const uint64_t b = std::max(address, g.address);
		const uint64_t e = std::min(address + size, g.address + g.source_size);
		Add(C::w_bytes, b < e ? e - b : 0);
	}
	Add(C::img_bytes, g.source_size);
	if (in_pass) {
		Add(C::in_pass);
	}
	Ev       ev  = Ev::None;
	uint64_t key = 0;
	if (s.open) {
		ev  = Ev::Reopen;
		key = s.key;
		Add(C::reopen);
		Join(s, g, address, size);
	} else if (s.sseq.load(std::memory_order_acquire) == s.wseq.load(std::memory_order_acquire)) {
		ev  = Ev::Synced;
		key = ClassKey(cf);
		Add(C::part_synced);
	} else if (s.dseq.load(std::memory_order_acquire) == s.wseq.load(std::memory_order_acquire)) {
		ev  = Ev::Dlmem;
		key = ClassKey(cf);
		Add(C::part_dlmem);
	} else {
		if (s.open) {
			Add(C::ep_bad); // (a): a new episode on an image with the open flag
		}
		ev          = Ev::New;
		s.open      = true;
		s.key       = ClassKey(cf);
		s.writer    = static_cast<uint8_t>(writer);
		s.n         = 0;
		s.ovf       = false;
		key         = s.key;
		Add(C::open);
		Add(C::ep_new);
		Join(s, g, address, size);
	}
	if (ev != Ev::Synced) {
		Add(C::img_bytes_unsync, g.source_size);
		Add(C::img_full_unsync, g.data_size);
		if (in_pass) {
			Add(C::in_pass_unsync);
		}
	}
	{
		std::scoped_lock lock {g_mutex};
		auto&            rec = ClsLocked(key, &cf);
		rec.c[static_cast<size_t>(CC::ev)]++;
		if (wcc != CC::Count) {
			rec.c[static_cast<size_t>(wcc)]++;
		}
		if (off) {
			rec.c[static_cast<size_t>(CC::ev_off)]++;
		}
		if (ev == Ev::Synced) {
			rec.c[static_cast<size_t>(CC::ev_synced)]++;
		}
		if (ev == Ev::Dlmem) {
			rec.c[static_cast<size_t>(CC::ev_dlmem)]++;
		}
		if (ev == Ev::New) {
			rec.c[static_cast<size_t>(CC::ep_new)]++;
		}
		rec.c[static_cast<size_t>(CC::img_bytes)] += g.source_size;
	}
	return ev;
}

TintPlan CloseUpload(ImageState& s, const Geometry& g, const ClassFields& cf_now, Close site, uint32_t first,
                     uint32_t end, uint32_t pend_first, uint32_t pend_end, bool fmt_ok, bool cpu_dirty, bool locked) {
	(void)cf_now; // the episode keeps the class of its opening (S2 / S8)
	if (!locked) {
		Add(C::lock_bad);
		return {};
	}
	if (s.wait) {
		DropWait(s, C::pend_drop); // executor decision 4: this upload replaces the deferred levels
	}
	if (!s.open) {
		Add(C::cl_none);
		return {};
	}
	const uint64_t key = s.key;
	CloseEpisode(s, site);
	uint32_t lost_mask = 0;
	uint32_t part_mask = 0;
	uint32_t up_mask   = 0;
	uint64_t lost      = 0;
	LevelMasks(g, first, end, s.w, s.n, &lost_mask, &part_mask, &up_mask, &lost);
	Add(C::lost_bytes, lost);
	uint64_t lost_pend = 0;
	if (pend_end > pend_first) {
		uint32_t pl = 0;
		uint32_t pp = 0;
		uint32_t pu = 0;
		LevelMasks(g, pend_first, pend_end, s.w, s.n, &pl, &pp, &pu, &lost_pend);
		Add(C::lost_pend_bytes, lost_pend);
		s.wait        = true;
		s.pend_key    = key;
		s.pend_n      = s.n;
		s.pend_ovf    = s.ovf;
		s.pend_skip   = false;
		s.pend_tinted = false;
		std::copy(std::begin(s.w), std::end(s.w), std::begin(s.pend_w));
		Add(C::ep_pend);
		Add(C::pend_open);
	}
	AddClass(key, nullptr, {{CC::lost_bytes, lost}, {CC::lost_pend_bytes, lost_pend}});
	TintPlan plan;
	plan.key = key;
	if (g_mode < 2) {
		return plan;
	}
	C skip = C::Count;
	if (!ClassListed(key)) {
		skip = C::tint_skip_cls;
	} else if (g.volume) {
		skip = C::tint_skip_vol;
	} else if (!fmt_ok) {
		skip = C::tint_skip_fmt;
	} else if (cpu_dirty) {
		skip = C::tint_skip_cpu;
	} else if (s.ovf) {
		skip = C::tint_skip_ovf;
	}
	if (skip != C::Count) {
		Add(skip);
		AddClass(key, nullptr, {{CC::tint_skip, 1}});
		s.pend_skip = s.wait;
		return plan;
	}
	uint32_t mask = up_mask;
	if (g_mode == 2) {
		mask = lost_mask;
		Add(C::tint_part_mips, Popcount(part_mask));
	}
	mask = VerifyTintPlan(g, mask, first, end, s.w, s.n);
	Tinted(plan, g, mask);
	if (mask != 0) {
		TintEpisode(key);
	}
	if (s.wait) {
		s.pend_tinted = mask != 0;
	}
	return plan;
}

TintPlan PendDone(ImageState& s, const Geometry& g, uint32_t first, uint32_t end, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return {};
	}
	if (!s.wait) {
		return {};
	}
	DropWait(s, C::pend_done);
	TintPlan plan;
	plan.key = s.pend_key;
	if (g_mode < 2 || s.pend_skip) {
		return plan;
	}
	uint32_t lost_mask = 0;
	uint32_t part_mask = 0;
	uint32_t up_mask   = 0;
	uint64_t lost      = 0;
	LevelMasks(g, first, end, s.pend_w, s.pend_n, &lost_mask, &part_mask, &up_mask, &lost);
	uint32_t mask = up_mask;
	if (g_mode == 2) {
		mask = lost_mask;
		Add(C::tint_part_mips, Popcount(part_mask));
	}
	mask = VerifyTintPlan(g, mask, first, end, s.pend_w, s.pend_n);
	Tinted(plan, g, mask);
	if (mask != 0 && !s.pend_tinted) {
		TintEpisode(plan.key);
	}
	return plan;
}

void PendDrop(ImageState& s, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	if (s.wait) {
		DropWait(s, C::pend_drop);
	}
}

void CloseNoUpload(ImageState& s, Close site, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	if (s.open) {
		CloseEpisode(s, site);
	} else {
		Add(C::cl_none);
	}
}

void NoteFree(ImageState& s, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	if (s.open) {
		CloseEpisode(s, Close::Free);
	} else {
		Add(C::cl_none);
	}
	if (s.wait) {
		DropWait(s, C::pend_free);
	}
	if (s.rb_count != 0) {
		std::scoped_lock lock {g_mutex};
		RbAbandonLocked(s);
	}
}

void Propagate(ImageState& dst, const ImageState& src, const Geometry& gdst, const ClassFields& cf_dst, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	if (!src.open) {
		return;
	}
	if (!dst.open) {
		dst.open   = true;
		dst.key    = ClassKey(cf_dst);
		dst.writer = src.writer;
		dst.n      = 0;
		dst.ovf    = false;
		Add(C::open);
		Add(C::ep_prop);
		AddClass(dst.key, &cf_dst, {{CC::ep_prop, 1}});
	} else {
		Add(C::prop_merge);
	}
	for (uint32_t i = 0; i < src.n; i++) {
		Join(dst, gdst, src.w[i].b, src.w[i].e - src.w[i].b);
	}
	if (src.ovf && !dst.ovf) {
		dst.ovf = true;
		Add(C::w_ovf);
	}
}

void NoteSync(ImageState& s, bool full, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	if (full) {
		s.sseq.store(s.wseq.load(std::memory_order_acquire), std::memory_order_release);
		Add(C::sync_full);
	} else {
		Add(C::sync_part);
	}
}

void NoteDownload(ImageState& s, bool locked) {
	if (!locked) {
		Add(C::lock_bad);
		return;
	}
	s.dseq.store(s.wseq.load(std::memory_order_acquire), std::memory_order_release);
	Add(C::dl_mem);
}

uint32_t RbBegin(ImageState& s, const TintPlan& plan, const Geometry& g, uint32_t width, uint32_t height,
                 uint32_t vk_format, uint32_t frame) {
	std::scoped_lock lock {g_mutex};
	RbAbandonLocked(s);
	const auto first = static_cast<uint32_t>(g_rb.size());
	uint32_t   count = 0;
	for (uint32_t l = 0; l < kLevels; l++) {
		if ((plan.rb_mask & (1u << l)) == 0) {
			continue;
		}
		Rb r;
		r.key        = plan.key;
		r.fmt        = vk_format;
		r.level      = l;
		r.x          = std::max(width >> l, 1u) / 2;
		r.y          = std::max(height >> l, 1u) / 2;
		r.last_layer = g.layers >= 2 ? g.layers - 1 : 0;
		r.st         = g_rb_final ? 3 : 0;
		g_rb.push_back(r);
		count++;
	}
	if (count != 0 && !g_rb_final) {
		s.rb_first = first;
		s.rb_count = count;
		s.rb_frame = frame;
		s.rb_wr.store(0, std::memory_order_release);
		s.rb_pend.store(1, std::memory_order_release);
	}
	return first;
}

void RbNotRecorded(const TintPlan& plan) {
	Add(C::tint_rb0_none, Popcount(plan.rb_mask));
}

void RbDone0(uint32_t id, bool magenta) {
	std::scoped_lock lock {g_mutex};
	if (g_rb_final || id >= g_rb.size() || g_rb[id].st != 0) {
		return;
	}
	auto& r   = g_rb[id];
	auto& rec = ClsLocked(r.key, nullptr);
	if (magenta) {
		Add(C::tint_rb0_ok);
		rec.c[static_cast<size_t>(CC::tint_rb0_ok)]++;
		if (r.abandoned) {
			r.st = 3;
			Add(C::tint_rb1_none);
		} else {
			r.st = 1;
		}
	} else {
		Add(C::tint_rb0_bad);
		rec.c[static_cast<size_t>(CC::tint_rb0_bad)]++;
		r.st = 3;
	}
}

uint32_t RbWant1(ImageState& s, uint32_t frame, RbInfo* out, uint32_t max) {
	if (s.rb_count == 0) {
		s.rb_pend.store(0, std::memory_order_release);
		return 0;
	}
	if (frame <= s.rb_frame) {
		return 0;
	}
	std::scoped_lock lock {g_mutex};
	const bool       wr        = s.rb_wr.load(std::memory_order_acquire) != 0;
	uint32_t         n         = 0;
	bool             remaining = false;
	for (uint32_t i = 0; i < s.rb_count; i++) {
		const uint32_t id = s.rb_first + i;
		auto&          r  = g_rb[id];
		if (r.st == 1 && n < max) {
			r.st     = 2;
			r.wr     = wr;
			out[n++] = {id, r.level, r.x, r.y, r.last_layer, r.fmt};
		} else if (r.st == 0 || r.st == 1) {
			remaining = true;
		}
	}
	if (!remaining) {
		s.rb_count = 0;
		s.rb_pend.store(0, std::memory_order_release);
	}
	return n;
}

void RbNotRecorded1(const RbInfo* infos, uint32_t count) {
	std::scoped_lock lock {g_mutex};
	for (uint32_t i = 0; i < count; i++) {
		auto& r = g_rb[infos[i].id];
		if (r.st == 2) {
			r.st = 3;
			Add(C::tint_rb1_none);
		}
	}
}

void RbDone1(uint32_t id, bool magenta) {
	std::scoped_lock lock {g_mutex};
	if (g_rb_final || id >= g_rb.size() || g_rb[id].st != 2) {
		return;
	}
	auto& r   = g_rb[id];
	auto& rec = ClsLocked(r.key, nullptr);
	if (magenta) {
		Add(C::tint_rb1_ok);
		rec.c[static_cast<size_t>(CC::tint_rb1_ok)]++;
	} else if (r.wr) {
		Add(C::tint_rb1_over);
		rec.c[static_cast<size_t>(CC::tint_rb1_over)]++;
	} else {
		Add(C::tint_rb1_bad);
		rec.c[static_cast<size_t>(CC::tint_rb1_bad)]++;
	}
	r.st = 3;
}

uint32_t RbInFlight() {
	std::scoped_lock lock {g_mutex};
	uint32_t         n = 0;
	for (const auto& r: g_rb) {
		n += (r.st == 0 || r.st == 2) ? 1u : 0u;
	}
	return n;
}

void ExitScan(uint64_t open_flags, uint64_t wait_flags) {
	if (open_flags != Read(C::open)) {
		Add(C::ep_bad); // (v)
	}
	if (wait_flags != Read(C::pend_open)) {
		Add(C::ep_bad);
	}
}

void SetExitHook(ExitHook hook, void* context) {
	std::scoped_lock lock {g_hook_mutex};
	if (hook == nullptr) {
		if (g_exit_context == context) {
			g_exit_hook    = nullptr;
			g_exit_context = nullptr;
		}
		return;
	}
	g_exit_hook    = hook;
	g_exit_context = context;
}

uint64_t Read(C counter) noexcept {
	return g_c[static_cast<size_t>(counter)].load(std::memory_order_relaxed);
}

uint64_t ReadClass(uint64_t key, CC counter) {
	std::scoped_lock lock {g_mutex};
	const auto       found = g_classes.find(key);
	return found == g_classes.end() ? 0 : found->second.c[static_cast<size_t>(counter)];
}

void PrintStat(const char* when) {
	std::string line = "T188Stat: when=";
	line += when;
	char buffer[64];
	for (uint32_t i = 0; i < static_cast<uint32_t>(C::Count); i++) {
		std::snprintf(buffer, sizeof(buffer), " %s=%" PRIu64, kNames[i], Read(static_cast<C>(i)));
		line += buffer;
	}
	LOGF("%s\n", line.c_str());
}

namespace {

void AppendClass(std::string& line, const std::array<uint64_t, static_cast<size_t>(CC::Count)>& c) {
	char buffer[64];
	for (uint32_t i = 0; i < static_cast<uint32_t>(CC::Count); i++) {
		std::snprintf(buffer, sizeof(buffer), " %s=%" PRIu64, kClassNames[i], c[i]);
		line += buffer;
	}
}

void PrintImg() {
	std::vector<std::pair<uint64_t, ClassRec>> rows;
	{
		std::scoped_lock lock {g_mutex};
		rows.assign(g_classes.begin(), g_classes.end());
	}
	const auto lost = [](const ClassRec& r) {
		return r.c[static_cast<size_t>(CC::lost_bytes)] + r.c[static_cast<size_t>(CC::lost_pend_bytes)];
	};
	std::sort(rows.begin(), rows.end(), [&](const auto& l, const auto& r) {
		if (lost(l.second) != lost(r.second)) {
			return lost(l.second) > lost(r.second);
		}
		if (l.second.c[0] != r.second.c[0]) {
			return l.second.c[0] > r.second.c[0];
		}
		return l.first < r.first;
	});
	std::array<uint64_t, static_cast<size_t>(CC::Count)> other {};
	bool                                                 any_other = false;
	for (size_t i = 0; i < rows.size(); i++) {
		const auto& [key, rec] = rows[i];
		if (i >= kImgLines) {
			for (size_t k = 0; k < other.size(); k++) {
				other[k] += rec.c[k];
			}
			any_other = true;
			continue;
		}
		char head[256];
		std::snprintf(head, sizeof(head),
		              "T188Img: when=exit key=%016" PRIx64 " fmt=%u tile=%u w=%u h=%u levels=%u layers=%u cmp=%u samples=%u"
		              " usage=%u vol=%u",
		              key, rec.f.fmt, rec.f.tile, rec.f.w, rec.f.h, rec.f.levels, rec.f.layers, rec.f.cmp, rec.f.samples,
		              rec.f.usage, rec.f.vol);
		std::string line = head;
		AppendClass(line, rec.c);
		LOGF("%s\n", line.c_str());
	}
	if (any_other) {
		std::string line = "T188Img: when=exit key=other";
		AppendClass(line, other);
		LOGF("%s\n", line.c_str());
	}
}

} // namespace

void PrintExit() {
	{
		std::scoped_lock lock {g_mutex};
		for (auto& r: g_rb) {
			if (r.st == 0) {
				Add(C::tint_rb0_none);
			} else if (r.st == 1 || r.st == 2) {
				Add(C::tint_rb1_none);
			}
			r.st = 3;
		}
		g_rb_final = true;
	}
	PrintStat("exit");
	PrintImg();
	DiagT109::PrintStat("exit");
}

void PrintExitStat() {
	if (g_mode < 1 || g_exit_printed.exchange(true)) {
		return;
	}
	ExitHook hook    = nullptr;
	void*    context = nullptr;
	{
		std::scoped_lock lock {g_hook_mutex};
		hook    = g_exit_hook;
		context = g_exit_context;
	}
	if (hook != nullptr) {
		hook(context);
	} else {
		PrintExit();
	}
}

void NoteAudioPush() {
	if ((g_pushes.fetch_add(1, std::memory_order_relaxed) + 1) % 4096 == 0) {
		PrintStat("periodic");
		DiagT109::PrintStat("periodic");
	}
}

void ResetForStand() {
	std::scoped_lock lock {g_mutex};
	for (auto& c: g_c) {
		c.store(0, std::memory_order_relaxed);
	}
	g_classes.clear();
	g_rb.clear();
	g_rb_final = false;
}

} // namespace Libs::DiagT188

namespace Libs::DiagT109 {

namespace {

std::atomic<uint64_t> g_d32 {0};
std::atomic<uint64_t> g_zx_d32 {0};
std::atomic<uint64_t> g_zx_narrow {0};
std::atomic<uint64_t> g_bias_d32 {0};
std::atomic<uint64_t> g_bias_narrow {0};
std::atomic<uint64_t> g_ovr_w {0};
std::atomic<uint64_t> g_ovr_vpc {0};
std::atomic<uint64_t> g_zx_narrow_vi {0};   // M9d3 (item 789(v)(2))
std::atomic<uint64_t> g_bias_narrow_vi {0}; // M9d3
std::atomic<uint64_t> g_narrow_cd {0};      // M9d3

void Bump(std::atomic<uint64_t>& a) {
	a.fetch_add(1, std::memory_order_relaxed);
}

} // namespace

void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,
              const VkRect2D* scissors, uint32_t count, bool clip_disable) {
	if (depth_format != VK_FORMAT_D32_SFLOAT && depth_format != VK_FORMAT_D32_SFLOAT_S8_UINT) {
		return;
	}
	if (!test && !write) {
		return;
	}
	Bump(g_d32);
	bool narrow = false;
	for (uint32_t i = 0; i < count; i++) {
		if (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {
			continue; // M9d2: the slot does not rasterize (empty ViewportIndex slot, zero-area scissor)
		}
		const float lo = std::min(viewports[i].minDepth, viewports[i].maxDepth);
		const float hi = std::max(viewports[i].minDepth, viewports[i].maxDepth);
		if (lo > 0.0f || hi < 1.0f) {
			narrow = true;
		}
	}
	if (z_export) {
		Bump(g_zx_d32);
		if (narrow) {
			Bump(g_zx_narrow);
			if (count > 1) {
				Bump(g_zx_narrow_vi); // M9d3: the narrow slot may be one the VS never writes
			}
		}
	}
	if (bias) {
		Bump(g_bias_d32);
		if (narrow) {
			Bump(g_bias_narrow);
			if (count > 1) {
				Bump(g_bias_narrow_vi); // M9d3
			}
		}
	}
	if (narrow && (z_export || bias) && count > 1 && clip_disable) {
		Bump(g_narrow_cd); // M9d3: once per draw (reference)
	}
}

void NoteRenderOverride(uint32_t value) {
	Bump(g_ovr_w);
	if ((value & 0x10000u) != 0) { // DISABLE_VIEWPORT_CLAMP
		Bump(g_ovr_vpc);
	}
}

Totals Read() {
	const auto load = [](const std::atomic<uint64_t>& a) { return a.load(std::memory_order_relaxed); };
	return {load(g_d32),       load(g_zx_d32), load(g_zx_narrow), load(g_bias_d32),
	        load(g_bias_narrow), load(g_ovr_w),  load(g_ovr_vpc), load(g_zx_narrow_vi),
	        load(g_bias_narrow_vi), load(g_narrow_cd)};
}

void PrintStat(const char* when) {
	const auto t = Read();
	LOGF("T109Stat: when=%s d32=%" PRIu64 " zx_d32=%" PRIu64 " zx_narrow=%" PRIu64 " bias_d32=%" PRIu64
	     " bias_narrow=%" PRIu64 " ovr_w=%" PRIu64 " ovr_vpc=%" PRIu64 " zx_narrow_vi=%" PRIu64
	     " bias_narrow_vi=%" PRIu64 " narrow_cd=%" PRIu64 "\n",
	     when, t.d32, t.zx_d32, t.zx_narrow, t.bias_d32, t.bias_narrow, t.ovr_w, t.ovr_vpc, t.zx_narrow_vi,
	     t.bias_narrow_vi, t.narrow_cd);
}

void ResetForStand() {
	for (auto* a: {&g_d32, &g_zx_d32, &g_zx_narrow, &g_bias_d32, &g_bias_narrow, &g_ovr_w, &g_ovr_vpc, &g_zx_narrow_vi,
	               &g_bias_narrow_vi, &g_narrow_cd}) {
		a->store(0, std::memory_order_relaxed);
	}
}

} // namespace Libs::DiagT109
