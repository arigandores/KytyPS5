// F4a2 (HPP-346, ROADMAP s122 p.262(b)(3)): the proof without the game. Calls the same function the
// emulator calls (Libs::Graphics::DualSrcBlend::RewriteLocation1ToIndex1 from
// src/graphics/host_gpu/renderer/pipeline/dualSrcBlend.h, included from the tree given by /I) on a raw
// SPIR-V module, writes the rewritten module and prints the outcome and the word difference; then
// checks the skip branches on mutations of the same module.
// Usage: proof_f4a2.exe <in.spv> <out.spv>
#define _CRT_SECURE_NO_WARNINGS
#include "graphics/host_gpu/renderer/pipeline/dualSrcBlend.h"

#include <cstdio>
#include <vector>

int main(int argc, char** argv) {
	using Libs::Graphics::DualSrcBlend::Outcome;
	using Libs::Graphics::DualSrcBlend::OutcomeName;
	using Libs::Graphics::DualSrcBlend::RewriteLocation1ToIndex1;
	if (argc != 3) {
		std::printf("usage: proof_f4a2 <in.spv> <out.spv>\n");
		return 2;
	}
	std::vector<uint32_t> in;
	if (FILE* f = std::fopen(argv[1], "rb"); f != nullptr) {
		uint32_t w = 0;
		while (std::fread(&w, sizeof(w), 1, f) == 1) {
			in.push_back(w);
		}
		std::fclose(f);
	} else {
		std::printf("cannot open %s\n", argv[1]);
		return 2;
	}
	std::vector<uint32_t> out;
	const auto outcome = RewriteLocation1ToIndex1(in, out);
	std::printf("in words %zu outcome %s out words %zu\n", in.size(), OutcomeName(outcome), out.size());
	if (outcome != Outcome::Patched) {
		return 1;
	}
	// Word difference: the first index where the streams differ, then a realignment after the
	// inserted instruction; every other word must be equal.
	size_t i = 0;
	while (i < in.size() && in[i] == out[i]) {
		i++;
	}
	std::printf("first differing word %zu: in 0x%08x out 0x%08x\n", i, i < in.size() ? in[i] : 0u, out[i]);
	size_t diffs = 0;
	for (size_t k = 0; k < in.size(); k++) {
		const size_t m = k <= i ? k : k + 4; // out has 4 words inserted after word i
		if (in[k] != out[m]) {
			std::printf("diff in[%zu]=0x%08x out[%zu]=0x%08x\n", k, in[k], m, out[m]);
			diffs++;
		}
	}
	std::printf("inserted out[%zu..%zu] = 0x%08x 0x%08x 0x%08x 0x%08x\n", i + 1, i + 4, out[i + 1],
	            out[i + 2], out[i + 3], out[i + 4]);
	std::printf("changed words (excluding the 4 inserted): %zu\n", diffs);
	if (FILE* f = std::fopen(argv[2], "wb"); f != nullptr) {
		std::fwrite(out.data(), sizeof(uint32_t), out.size(), f);
		std::fclose(f);
	} else {
		std::printf("cannot write %s\n", argv[2]);
		return 2;
	}

	// Skip branches on mutations of the same module: word i is the Location literal of out_mrt_1,
	// word i - 3 the first word of its OpDecorate (4 words).
	int  failed = 0;
	auto expect = [&failed](const char* name, const std::vector<uint32_t>& words, Outcome want) {
		std::vector<uint32_t> scratch;
		const auto            got = RewriteLocation1ToIndex1(words, scratch);
		const bool            ok  = got == want && (got == Outcome::Patched || scratch.empty());
		std::printf("selftest %-24s want %-18s got %-18s %s\n", name, OutcomeName(want), OutcomeName(got),
		            ok ? "OK" : "FAIL");
		failed += ok ? 0 : 1;
	};
	expect("original", in, Outcome::Patched);
	expect("rewritten_again", out, Outcome::HasIndex);
	auto m = in;
	m[i] = 2;
	expect("location1_to_2", m, Outcome::LocationAbove1);
	m    = in;
	m[i] = 0;
	expect("location1_to_0", m, Outcome::NoLocation1);
	m        = in;
	m[i - 2] = 0x7fffffffu; // decoration target outside the id bound
	expect("location1_target_bad", m, Outcome::NoLocation1);
	m = in;
	m.resize(i - 1); // cut inside the OpDecorate of out_mrt_1
	expect("truncated", m, Outcome::Malformed);
	m    = in;
	m[0] = 0;
	expect("bad_magic", m, Outcome::Malformed);
	// The instruction before it is OpDecorate %out_mrt_0 Location 0 (words i-7..i-4).
	if (in[i - 7] == 0x00040047u && in[i - 5] == 30u && in[i - 4] == 0u) {
		m        = in;
		m[i - 4] = 1;
		expect("location0_to_1", m, Outcome::MultipleLocation1);
		m        = in;
		m[i - 6] = 0x7fffffffu; // out_mrt_0 decoration off any variable; Input %6 stays at Location 0
		expect("location0_target_bad", m, Outcome::NoLocation0);
		m        = in;
		m[i - 7] = 0x00040048u; // OpMemberDecorate %18 member 0 Location
		m[i - 5] = 0;
		m[i - 4] = 30;
		expect("member_location", m, Outcome::MemberDecoration);
	} else {
		std::printf("selftest location0 cases: unexpected neighbour instruction\n");
		failed++;
	}
	std::printf("selftest %s\n", failed == 0 ? "ALL OK" : "FAILED");
	return failed == 0 ? 0 : 1;
}
