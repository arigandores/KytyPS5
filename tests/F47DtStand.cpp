// Track F, F47g (HPP-824, ROADMAP s122 item 740(v)(1)): stand of KYTY_DIAG_F47DT without the game.
// The real module (graphics/host_gpu/renderer/diagF47Dt.cpp) with its real hashing, records, files, register shadow and
// exit line; "guest memory" is a host buffer of the stand (SetGuestReaderForStand: the address IS the host pointer), the
// upload source is the module's own hook NoteImageSource / NoteImageUpload called as BufferCache / TextureCache call it.
// Each arm prints "ARM <name> ..." to stdout; the module lines go to <out>/stand.log. KYTY_DIAG_F47DT of the process
// decides =0 / =1 (read once): the runner run_stand_f47g.py starts the stand twice and checks both.
//
// Arms (an "image" is a range of the guest buffer; every StandImage line carries ih / sh / cmp):
//   P  staging upload, then ONE byte of guest memory changes without any cache call  -> cmp=ne  (positive control)
//   N  staging upload, no change                                                      -> cmp=eq  (negative control)
//   A  pooled copy (Common::AsyncMemcpy, the real pool) into a staging buffer, StagingAsync note, line before and after
//      the copy landed                                                                -> last line sst=hashed cmp=eq
//   L  pooled copy, the fake ring generation moves before the copy is resolved          -> sst=lost cmp=und
//   I  import note (hash of guest at record), then one byte changes                     -> cmp=ne; I0 unchanged -> eq
//   O  owner note                                                                      -> sst=unmeasured cmp=und
//   U  upload without a note                                                           -> why=no_note cmp=und
//   D  deferred upload (levels 1..), guest changes, completion upload (levels 0..)      -> cur=new prev=old cmp=und
//   R  register words: write, push, clear, write, pop                                  -> the popped values
//   C  file cap 26 MiB (23 MiB written before): three 2 MiB ranges -> C0 new, one "F47dt: capped" line, C1/C2 capped
// Usage: f47dt_stand <out_dir>    Exit 0; 2 - bad arguments.
#include "common/emulatorConfig.h"
#include "common/logging/log.h"
#include "common/parallelCopy.h"
#include "common/subsystems.h"
#include "common/threads.h"
#include "graphics/guest_gpu/pm4.h"
#include "graphics/host_gpu/renderer/diagF47Dt.h"

#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <string>
#include <vector>

namespace D = Libs::Graphics::DiagF47Dt;

namespace {

bool StandReader(uint64_t vaddr, uint64_t size, std::vector<uint8_t>* /*copy*/, const uint8_t** ptr) {
	(void)size;
	*ptr = reinterpret_cast<const uint8_t*>(vaddr);
	return true;
}

struct FakeRing {
	uint64_t generation = 1;
};

uint64_t FakeGeneration(const void* ring) {
	return static_cast<const FakeRing*>(ring)->generation;
}

uint64_t Addr(const std::vector<uint8_t>& g, size_t offset) {
	return reinterpret_cast<uint64_t>(g.data() + offset);
}

void Fill(std::vector<uint8_t>* g, uint64_t seed) {
	uint64_t x = seed;
	for (auto& b: *g) {
		x ^= x << 13u;
		x ^= x >> 7u;
		x ^= x << 17u;
		b = static_cast<uint8_t>(x >> 24u);
	}
}

void StagingUpload(uint32_t index, uint64_t addr, uint64_t size, uint32_t first, uint32_t count, uint32_t pend, bool comp) {
	std::vector<uint8_t> staging(reinterpret_cast<const uint8_t*>(addr), reinterpret_cast<const uint8_t*>(addr) + size);
	D::NoteImageSource(D::SrcKind::Staging, addr, size, staging.data(), nullptr, nullptr, 0);
	D::NoteImageUpload(index, addr, size, first, count, pend, comp);
}

} // namespace

int main(int argc, char** argv) {
	if (argc != 2) {
		std::fprintf(stderr, "usage: f47dt_stand <out_dir>\n");
		return 2;
	}
	const std::string out = argv[1];
	std::filesystem::create_directories(out);
	std::filesystem::current_path(out); // _f47dt/ of the module goes here

	Common::InitializeThreads();
	Common::Subsystems subsystems;
	subsystems.Initialize<Config::Lifecycle>();
	Config::ConfigOptions options;
	options.printf_direction   = Config::LogDirection::File;
	options.printf_output_file = "stand.log";
	Config::Load(options);
	subsystems.Initialize<Log::Lifecycle>();

	const char* env = std::getenv("KYTY_DIAG_F47DT");
	D::SetGuestReaderForStand(&StandReader);
	// Files before arm C: P 1 + N 1 + A 8 + L 8 + I 1 + I0 1 + O 1 + U 1 + D 1 = 23 MiB; C0 (2 MiB) fits in 26 MiB, C1 does not.
	D::SetFileCapForStand(26u << 20u);
	D::SetPresentForStand(700);
	const bool on = D::On();
	std::printf("F47DT env=%s on=%d\n", env != nullptr ? env : "(unset)", on ? 1 : 0);

	constexpr size_t MiB = 1u << 20u;
	std::vector<uint8_t> g(64 * MiB);
	Fill(&g, 0x47d7);

	// P / N
	{
		const auto p = Addr(g, 0 * MiB);
		const auto n = Addr(g, 2 * MiB);
		StagingUpload(1, p, MiB, 0, 1, 0, false);
		StagingUpload(2, n, MiB, 0, 1, 0, false);
		g[0 * MiB + 12345] ^= 0x5au;
		D::SetPresentForStand(701);
		std::printf("ARM P addr=0x%" PRIx64 " size=0x%zx\n", p, MiB);
		D::StandImage(0, p, MiB);
		std::printf("ARM N addr=0x%" PRIx64 " size=0x%zx\n", n, MiB);
		D::StandImage(1, n, MiB);
	}
	// A / L - the real copy pool; the stand waits for it (the module never does)
	{
		const auto           size = 8 * MiB;
		const auto           a    = Addr(g, 8 * MiB);
		const auto           l    = Addr(g, 16 * MiB);
		std::vector<uint8_t> sa(size);
		std::vector<uint8_t> sl(size);
		FakeRing             ring_a;
		FakeRing             ring_l;
		Common::AsyncMemcpy(sa.data(), reinterpret_cast<const void*>(a), size);
		D::NoteImageSource(D::SrcKind::StagingAsync, a, size, sa.data(), &ring_a, &FakeGeneration, ring_a.generation);
		D::NoteImageUpload(3, a, size, 0, 1, 0, false);
		Common::AsyncMemcpy(sl.data(), reinterpret_cast<const void*>(l), size);
		D::NoteImageSource(D::SrcKind::StagingAsync, l, size, sl.data(), &ring_l, &FakeGeneration, ring_l.generation);
		D::NoteImageUpload(4, l, size, 0, 1, 0, false);
		D::SetPresentForStand(702);
		std::printf("ARM A0 addr=0x%" PRIx64 " size=0x%zx\n", a, size);
		D::StandImage(0, a, size);
		ring_l.generation++;
		Common::WaitAsyncCopies();
		std::printf("ARM A1 addr=0x%" PRIx64 " size=0x%zx\n", a, size);
		D::StandImage(0, a, size);
		std::printf("ARM L addr=0x%" PRIx64 " size=0x%zx\n", l, size);
		D::StandImage(1, l, size);
	}
	// I / I0 / O / U
	{
		const auto i  = Addr(g, 24 * MiB);
		const auto i0 = Addr(g, 26 * MiB);
		const auto o  = Addr(g, 28 * MiB);
		const auto u  = Addr(g, 30 * MiB);
		D::NoteImageSource(D::SrcKind::Import, i, MiB, nullptr, nullptr, nullptr, 0);
		D::NoteImageUpload(5, i, MiB, 0, 1, 0, false);
		D::NoteImageSource(D::SrcKind::Import, i0, MiB, nullptr, nullptr, nullptr, 0);
		D::NoteImageUpload(6, i0, MiB, 0, 1, 0, false);
		D::NoteImageSource(D::SrcKind::Owner, o, MiB, nullptr, nullptr, nullptr, 0);
		D::NoteImageUpload(7, o, MiB, 0, 1, 0, false);
		D::NoteImageUpload(8, u, MiB, 0, 1, 0, false);
		g[24 * MiB + 777] ^= 0x01u;
		D::SetPresentForStand(703);
		std::printf("ARM I addr=0x%" PRIx64 " size=0x%zx\n", i, MiB);
		D::StandImage(0, i, MiB);
		std::printf("ARM I0 addr=0x%" PRIx64 " size=0x%zx\n", i0, MiB);
		D::StandImage(1, i0, MiB);
		std::printf("ARM O addr=0x%" PRIx64 " size=0x%zx\n", o, MiB);
		D::StandImage(2, o, MiB);
		std::printf("ARM U addr=0x%" PRIx64 " size=0x%zx\n", u, MiB);
		D::StandImage(3, u, MiB);
	}
	// D - deferred completion with changed guest bytes in between
	{
		const auto d = Addr(g, 32 * MiB);
		StagingUpload(9, d, MiB, 1, 3, 1, false);
		g[32 * MiB + 99] ^= 0x80u;
		StagingUpload(UINT32_MAX, d, MiB, 0, 1, 0, true);
		D::SetPresentForStand(704);
		std::printf("ARM D addr=0x%" PRIx64 " size=0x%zx\n", d, MiB);
		D::StandImage(0, d, MiB);
	}
	// R - register words through write / push / clear / write / pop
	{
		using namespace Libs::Graphics;
		static int ctx       = 0;
		static int saved     = 0;
		const uint32_t blend = 0x40010501u;
		const uint32_t mask  = 0x0000000fu;
		D::NoteCtxWrite(&ctx, Pm4::CB_BLEND0_CONTROL, &blend, 1, 0);
		D::NoteCtxWrite(&ctx, Pm4::CB_TARGET_MASK, &mask, 1, 2);
		D::NoteCtxOp(&ctx, &saved, D::CtxOp::Push);
		D::NoteCtxOp(&ctx, &saved, D::CtxOp::Clear);
		const uint32_t other = 0x12345678u;
		D::NoteCtxWrite(&ctx, Pm4::CB_BLEND0_CONTROL, &other, 1, 0);
		std::printf("ARM R1 (after clear + write: CB_BLEND0_CONTROL=12345678 CB_TARGET_MASK=R)\n");
		D::StandRegs(&ctx);
		D::NoteCtxOp(&ctx, &saved, D::CtxOp::Pop);
		std::printf("ARM R2 (after pop: CB_BLEND0_CONTROL=40010501 CB_TARGET_MASK=0000000f)\n");
		D::StandRegs(&ctx);
	}
	// C - the file cap (last: it ends the files of the process)
	{
		D::SetPresentForStand(705);
		for (uint32_t k = 0; k < 3; k++) {
			const auto c = Addr(g, (40 + 2 * k) * MiB);
			StagingUpload(10 + k, c, 2 * MiB, 0, 1, 0, false);
			std::printf("ARM C%u addr=0x%" PRIx64 " size=0x%zx\n", k, c, 2 * MiB);
			D::StandImage(k, c, 2 * MiB);
		}
	}
	D::PrintExitStat();
	std::printf("DONE\n");
	std::fflush(stdout);
	return 0;
}
