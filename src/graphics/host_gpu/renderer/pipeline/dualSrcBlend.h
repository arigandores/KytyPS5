#pragma once

// Track F, F4a2 (HPP-346, ROADMAP s122 p.262(b)): the translated pixel shader writes the MRT1 export as an
// output at Location 1; the second blend source of the guest is taken to be MRT1 ([I] of p.262(b), not verified).
// Vulkan reads the SRC1 factors from the output at Location 0 Index 1. Under KYTY_FIX_DUALSRC=1 a
// pipeline with SRC1 factors gets its own fragment module rewritten by RewriteLocation1ToIndex1; the
// translated module, its cache file and its other pipelines are untouched. Header-only, no Vulkan:
// the proof executable of p.262(b)(3) includes this same function. Outside the translation cache
// signature set (src/graphics/shader/** and the three files of CMakeLists.txt SHADER_CACHE_EXTRA_FILES).

#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

namespace Libs::Graphics::DualSrcBlend {

enum class Outcome : uint8_t {
	Patched,            // out: Location 1 -> Location 0, OpDecorate Index 1 inserted after it
	Malformed,          // not a SPIR-V module this parser can walk
	MemberDecoration,   // a Location or Index decoration on a struct member
	HasIndex,           // the module already decorates something with Index
	NoLocation1,        // no Output variable at Location 1
	MultipleLocation1,  // more than one Output variable at Location 1
	NoLocation0,        // no Output variable at Location 0
	LocationAbove1,     // an Output variable at Location >= 2
};

inline const char* OutcomeName(Outcome outcome) {
	switch (outcome) {
		case Outcome::Patched: return "patched";
		case Outcome::Malformed: return "malformed";
		case Outcome::MemberDecoration: return "member_decoration";
		case Outcome::HasIndex: return "has_index";
		case Outcome::NoLocation1: return "no_location1";
		case Outcome::MultipleLocation1: return "multiple_location1";
		case Outcome::NoLocation0: return "no_location0";
		case Outcome::LocationAbove1: return "location_above1";
	}
	return "unknown";
}

// `out` is written only for Outcome::Patched: `in` with the literal of the one OpDecorate <var>
// Location 1 of an Output variable set to 0 and OpDecorate <var> Index 1 inserted right after it.
// No new id, so the header bound stays; every other word is copied unchanged.
inline Outcome RewriteLocation1ToIndex1(std::span<const uint32_t> in, std::vector<uint32_t>& out) {
	constexpr uint32_t kMagic             = 0x07230203u;
	constexpr uint32_t kOpVariable        = 59u;
	constexpr uint32_t kOpDecorate        = 71u;
	constexpr uint32_t kOpMemberDecorate  = 72u;
	constexpr uint32_t kStorageOutput     = 3u;
	constexpr uint32_t kDecorationLoc     = 30u;
	constexpr uint32_t kDecorationIndex   = 32u;
	constexpr size_t   kHeaderWords       = 5;
	constexpr size_t   kNone              = static_cast<size_t>(-1);

	if (in.size() < kHeaderWords || in[0] != kMagic) {
		return Outcome::Malformed;
	}
	const uint32_t bound = in[3];
	if (bound == 0 || bound > (1u << 22u)) {
		return Outcome::Malformed;
	}
	// Pass 1: storage class of every OpVariable, Location decorations, Index decorations.
	std::vector<uint8_t> is_output(bound, 0);
	struct LocationDecoration {
		size_t   word;     // offset of the OpDecorate instruction
		uint32_t target;
		uint32_t location;
	};
	std::vector<LocationDecoration> locations;
	for (size_t i = kHeaderWords; i < in.size();) {
		const uint32_t count = in[i] >> 16u;
		const uint32_t op    = in[i] & 0xffffu;
		if (count == 0 || count > in.size() - i) {
			return Outcome::Malformed;
		}
		if (op == kOpVariable && count >= 4) {
			if (in[i + 2] >= bound) {
				return Outcome::Malformed;
			}
			if (in[i + 3] == kStorageOutput) {
				is_output[in[i + 2]] = 1;
			}
		} else if (op == kOpDecorate && count >= 3) {
			if (in[i + 2] == kDecorationIndex) {
				return Outcome::HasIndex;
			}
			if (in[i + 2] == kDecorationLoc) {
				if (count != 4) {
					return Outcome::Malformed;
				}
				locations.push_back({i, in[i + 1], in[i + 3]});
			}
		} else if (op == kOpMemberDecorate && count >= 4) {
			if (in[i + 3] == kDecorationLoc || in[i + 3] == kDecorationIndex) {
				return Outcome::MemberDecoration;
			}
		}
		i += count;
	}
	// Pass 2: the Output variables by location.
	size_t location1 = kNone;
	bool   location0 = false;
	for (const auto& d: locations) {
		if (d.target >= bound || is_output[d.target] == 0) {
			continue;
		}
		if (d.location >= 2) {
			return Outcome::LocationAbove1;
		}
		if (d.location == 0) {
			location0 = true;
		} else if (location1 != kNone) {
			return Outcome::MultipleLocation1;
		} else {
			location1 = d.word;
		}
	}
	if (location1 == kNone) {
		return Outcome::NoLocation1;
	}
	if (!location0) {
		return Outcome::NoLocation0;
	}
	const uint32_t target = in[location1 + 1];
	out.clear();
	out.reserve(in.size() + 4);
	out.insert(out.end(), in.begin(), in.begin() + static_cast<std::ptrdiff_t>(location1 + 4));
	out[location1 + 3] = 0;
	out.push_back((4u << 16u) | kOpDecorate);
	out.push_back(target);
	out.push_back(kDecorationIndex);
	out.push_back(1);
	out.insert(out.end(), in.begin() + static_cast<std::ptrdiff_t>(location1 + 4), in.end());
	return Outcome::Patched;
}

} // namespace Libs::Graphics::DualSrcBlend
