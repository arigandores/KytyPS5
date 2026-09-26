#ifndef EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO8_H_
#define EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO8_H_

// Session 121, knob "texmemo8" (C:/kyty/s121/design/design121.md; texmemo8.md with RC1-RC8 of texmemo8_review.md): the
// pure set/way logic of the 8-way texture memo.  No dependency beyond the standard library ON PURPOSE, so that the
// offline unit test (C:/kyty/s121/unit) compiles THIS file against a brute-force LRU without building the emulator.
// The memo itself (RenderExecutorMemo::textures, 4 096 entries) is unchanged: under texmemo8 >= 1 entry set * 8 + way
// is way `way` of set `set`, set = the low 9 bits of the memo hash, tag = its high 32 bits.

#include <array>
#include <cstddef>
#include <cstdint>

namespace Libs::Graphics {

constexpr uint32_t TexMemo8Ways  = 8;
constexpr uint32_t TexMemo8Slots = 4096;                          // = RenderExecutorMemo::TextureSlots
constexpr uint32_t TexMemo8Sets  = TexMemo8Slots / TexMemo8Ways;  // 512
static_assert((TexMemo8Sets & (TexMemo8Sets - 1)) == 0);

// One 64-byte line per set: the compact tag and the LRU stamp of each way.  use == 0 <=> the way is empty <=> its entry
// is not valid (ResolveTextureWith keeps the two in step).  The tag only filters: a hit still needs the full proof
// (resource_key, 32-byte T#, liveness).
struct alignas(64) TexMemo8Set {
	std::array<uint32_t, TexMemo8Ways> tag {};
	std::array<uint32_t, TexMemo8Ways> use {};
};
static_assert(sizeof(TexMemo8Set) == 64);

// = the census's R1Tag: the set index uses the low bits of the memo hash, the tag the high ones.
inline uint32_t TexMemo8Tag(uint64_t hash) noexcept {
	return static_cast<uint32_t>(hash >> 32u);
}
inline uint32_t TexMemo8SetOf(uint64_t hash) noexcept {
	return static_cast<uint32_t>(hash) & (TexMemo8Sets - 1u);
}

// The non-empty ways of `s` whose tag equals `tag`, as a bit mask.  Branch-free on purpose: the set probe runs on every
// lookup.
inline uint32_t TexMemo8TagMask(const TexMemo8Set& s, uint32_t tag) noexcept {
	uint32_t mask = 0;
	for (uint32_t w = 0; w < TexMemo8Ways; w++) {
		mask |= static_cast<uint32_t>(s.tag[w] == tag && s.use[w] != 0) << w;
	}
	return mask;
}

// The way a store takes on a key miss: an empty way, else the least recently used (lowest stamp) - the census's
// R1Victim on the same line.
inline uint32_t TexMemo8Victim(const TexMemo8Set& s) noexcept {
	uint32_t best = 0;
	for (uint32_t w = 0; w < TexMemo8Ways; w++) {
		if (s.use[w] == 0) {
			return w;
		}
		if (s.use[w] < s.use[best]) {
			best = w;
		}
	}
	return best;
}

// Before the clock wraps: every non-empty way gets its rank (1..8) among the non-empty ways of its set - the LRU order
// is kept exactly (stamps are unique), empty ways stay 0.  The caller sets the clock to 8.
inline void TexMemo8Renorm(TexMemo8Set* sets, size_t count) noexcept {
	for (size_t i = 0; i < count; i++) {
		auto&                              s = sets[i];
		std::array<uint32_t, TexMemo8Ways> rank {};
		for (uint32_t w = 0; w < TexMemo8Ways; w++) {
			if (s.use[w] == 0) {
				continue;
			}
			rank[w] = 1;
			for (uint32_t v = 0; v < TexMemo8Ways; v++) {
				rank[w] += (s.use[v] != 0 && s.use[v] < s.use[w]) ? 1u : 0u;
			}
		}
		s.use = rank;
	}
}

// The wrap of the LRU clock, out of line and cold ON PURPOSE (review of the timed arm): TexMemo8Tick is inlined into
// ResolveTextureWith, and the 512-set renormalisation must not ride along into the lookup hot path.
__attribute__((noinline, cold)) inline void TexMemo8RenormCold(uint32_t& clock, TexMemo8Set* sets,
                                                               size_t count) noexcept {
	TexMemo8Renorm(sets, count);
	clock    = TexMemo8Ways;
}

// The next LRU stamp.  At UINT32_MAX every set is renormalised first (renormed = true) and the clock restarts at 8, so
// the stamp returned is larger than every stamp in every set and never 0.
inline uint32_t TexMemo8Tick(uint32_t& clock, TexMemo8Set* sets, size_t count, bool& renormed) noexcept {
	renormed = false;
	if (clock == UINT32_MAX) [[unlikely]] {
		TexMemo8RenormCold(clock, sets, count);
		renormed = true;
	}
	return ++clock;
}

// texmemo8 >= 2 (RC4): whether an entry index holds a key that BELONGS there under the layout `mode`: the direct layout
// (0) puts a key at hash % 4096; the 8-way layout (1..3) in its set, on a non-empty way carrying the key's tag.
// `s` = the set line of `index` (sets[index / 8]).
inline bool TexMemo8Placed(uint32_t mode, uint64_t hash, uint32_t index, const TexMemo8Set& s) noexcept {
	if (mode == 0) {
		return (hash & (TexMemo8Slots - 1u)) == index;
	}
	const uint32_t way = index % TexMemo8Ways;
	return TexMemo8SetOf(hash) == index / TexMemo8Ways && s.use[way] != 0 && s.tag[way] == TexMemo8Tag(hash);
}

// texmemo8 >= 2 (RC2): the verify verdict.  The REAL verdict is decided first, so a real disagreement is booked as one
// even on a lookup the positive control (texmemo8 = 3) picked; an injected lookup that agrees must see its corrupted
// claim rejected (Injected), else the control is broken (InjectMissed).  Only Mismatch changes the memo.
enum class TexMemo8Verdict : uint32_t { Agree, Injected, InjectMissed, Mismatch };
inline TexMemo8Verdict TexMemo8Judge(bool real_ok, bool inject, bool claim_rejected) noexcept {
	if (!real_ok) {
		return TexMemo8Verdict::Mismatch;
	}
	if (!inject) {
		return TexMemo8Verdict::Agree;
	}
	return claim_rejected ? TexMemo8Verdict::Injected : TexMemo8Verdict::InjectMissed;
}

} // namespace Libs::Graphics

#endif // EMULATOR_SRC_GRAPHICS_HOST_GPU_RENDERER_RENDERMEMO8_H_
