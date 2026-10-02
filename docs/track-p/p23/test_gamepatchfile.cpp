// P23 (HPP-404): fixtures of the patch file loader against the real header src/loader/gamePatchFile.h (ROADMAP s122 item
// 333(d)-(e): each directive and edge - sha mismatch, unknown directive, bad hex, overlap, env conflict, no file) and of
// the file patches/PPSA21564_pvar.txt against the P-var constants of src/kernel/pvar.h and the real eboot.bin.
// Usage: test_gamepatchfile.exe <worktree> <eboot.bin>
#define KYTY_PVAR_ARITHMETIC_ONLY
#include "kernel/pvar.h"
#include "loader/gamePatchFile.h"

#include <cstdio>
#include <cstring>
#include <fstream>
#include <iterator>
#include <string>

namespace G = Loader::GamePatchFile;

static int g_fail = 0;
static int g_pass = 0;

static void Check(bool ok, const std::string& what) {
	if (ok) {
		g_pass++;
	} else {
		g_fail++;
		std::printf("FAIL %s\n", what.c_str());
	}
}

static std::string ShaOf(const std::string& text) {
	G::Sha256 h;
	h.Update(reinterpret_cast<const uint8_t*>(text.data()), text.size());
	return h.FinalHex();
}

static const std::string SHA_A = "3b5100797fe83663e18a650f82f901d066acf1029ae80cfb1be638fe0839debd";
static const std::string SHA_B = "3b5100797fe83663e18a650f82f901d066acf1029ae80cfb1be638fe0839debe";

struct Out {
	bool        ok = false;
	G::Spec     spec;
	G::Refusal  refusal;
	int         hashed = 0;
};

static Out Run(const std::string* text, const std::string& eboot, const G::Env& env = {}) {
	Out o;
	o.ok = G::Decide(
	    text,
	    [&] {
		    o.hashed++;
		    return eboot;
	    },
	    env, &o.spec, &o.refusal);
	return o;
}

static Out RunText(const std::string& text, const G::Env& env = {}, const std::string& eboot = SHA_A) {
	return Run(&text, eboot, env);
}

static bool Cleared(const Out& o) {
	return o.spec.sha256.empty() && o.spec.pokes.empty() && !o.spec.pvar2 && !o.spec.audio_sync0;
}

// A refusal with the reason; the spec is cleared on every refusal.
static void Refused(const Out& o, const char* reason, const std::string& what) {
	const bool ok = !o.ok && o.refusal.reason == reason && Cleared(o);
	if (!ok) {
		std::printf("  got ok=%d reason=%s detail=%s\n", o.ok ? 1 : 0, o.refusal.reason.c_str(), o.refusal.detail.c_str());
	}
	Check(ok, what + " -> refused " + reason);
}

static void Applied(const Out& o, const std::string& what) {
	if (!o.ok) {
		std::printf("  got reason=%s detail=%s\n", o.refusal.reason.c_str(), o.refusal.detail.c_str());
	}
	Check(o.ok && o.refusal.reason.empty(), what + " -> applied");
}

static const std::string HEAD = "sha256 " + SHA_A + "\n";
static const std::string BODY = "poke 2a470b:c5fb10051ddd0a08c5fb5905b5c40a08c5f25a8d40ffffff90\npoke 687375:e790cb07\npvar 2\naudio_sync 0\n";

static void Sha() {
	Check(ShaOf("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "sha256 empty");
	Check(ShaOf("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", "sha256 abc");
	Check(ShaOf("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") ==
	          "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
	      "sha256 448 bits (two blocks)");
	G::Sha256         h;
	const std::string seven(7, 'a');
	for (int i = 0; i < 1000000 / 7; i++) {
		h.Update(reinterpret_cast<const uint8_t*>(seven.data()), 7);
	}
	h.Update(reinterpret_cast<const uint8_t*>(seven.data()), 1000000 % 7);
	Check(h.FinalHex() == "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0", "sha256 million a, 7-byte chunks");
	// Lengths around the padding edges: one-shot equals byte by byte.
	for (size_t n: {55u, 56u, 57u, 63u, 64u, 65u, 119u, 120u, 128u}) {
		const std::string s(n, 'x');
		G::Sha256         b;
		for (char ch: s) {
			b.Update(reinterpret_cast<const uint8_t*>(&ch), 1);
		}
		Check(b.FinalHex() == ShaOf(s), "sha256 length " + std::to_string(n) + " chunked = one-shot");
	}
	Check(ShaOf(std::string(56, 'x')) != ShaOf(std::string(55, 'x')), "sha256 55 != 56");
}

static void Valid() {
	const auto o = RunText(HEAD + BODY);
	Applied(o, "canonical file");
	Check(o.hashed == 1, "canonical: eboot hashed once");
	Check(o.spec.sha256 == SHA_A && o.spec.pokes.size() == 2 && o.spec.pvar2 && o.spec.audio_sync0, "canonical: spec");
	Check(o.spec.pokes.size() == 2 && o.spec.pokes[0].offset == 0x2a470b && o.spec.pokes[0].bytes.size() == 25 &&
	          o.spec.pokes[1].offset == 0x687375 && o.spec.pokes[1].bytes.size() == 4 && o.spec.pokes[1].bytes[0] == 0xe7 &&
	          o.spec.pokes[1].bytes[3] == 0x07 && o.spec.pokes[1].hex == "e790cb07",
	      "canonical: pokes");
	// Tolerated form: CRLF, tabs, inline comments, upper-case hex, blank lines, no final newline.
	std::string upper = SHA_A;
	for (auto& ch: upper) {
		if (ch >= 'a' && ch <= 'f') {
			ch = static_cast<char>(ch - 'a' + 'A');
		}
	}
	const auto f = RunText("# head\r\n\r\n  sha256\t" + upper + "  # x\r\n\tpoke 687375:E790CB07 #c\r\npvar 2\r\naudio_sync 0");
	Applied(f, "CRLF, tabs, comments, upper-case hex, no final newline");
	Check(f.spec.sha256 == SHA_A && f.spec.pokes.size() == 1 && f.spec.pokes[0].bytes[0] == 0xe7, "tolerated form: spec");
	// Optional directives: only sha256.
	const auto s = RunText(HEAD);
	Applied(s, "sha256 only");
	Check(s.spec.pokes.empty() && !s.spec.pvar2 && !s.spec.audio_sync0, "sha256 only: no pokes, no pvar, no audio_sync");
	Check(RunText(HEAD + "pvar 2\n").spec.pvar2 && !RunText(HEAD + "pvar 2\n").spec.audio_sync0, "pvar without audio_sync");
	Check(RunText(HEAD + "poke 0:00\n").ok, "poke at offset 0");
	Check(RunText(HEAD + "poke ffffffff:00\n").ok, "poke at the last offset below 0x100000000");
}

static void ShaMismatch() {
	const auto o = RunText(HEAD + BODY, {}, SHA_B);
	Refused(o, "sha", "eboot sha256 differs in the last digit");
	Check(o.hashed == 1, "sha mismatch: hashed once");
	Refused(RunText(HEAD + BODY, {}, ""), "sha", "eboot unreadable (empty hash)");
	G::Env env;
	env.pvar = "0";
	Refused(RunText(HEAD + BODY, env, SHA_B), "sha", "sha mismatch is checked before env");
}

static void Directives() {
	const auto u = RunText(HEAD + "pokes 1:00\n");
	Refused(u, "directive", "unknown directive");
	Check(u.hashed == 0, "unknown directive: eboot not hashed");
	Refused(RunText(HEAD + BODY + "pvar2\n"), "directive", "unknown directive after valid lines");
	Refused(RunText("poke 1:00\n" + HEAD), "directive", "first directive not sha256");
	Refused(RunText("pvar 2\n" + HEAD), "directive", "pvar before sha256");
	Refused(RunText(HEAD + HEAD), "directive", "two sha256");
	Refused(RunText("# only a comment\n\n"), "directive", "no directive at all");
	Refused(RunText(""), "directive", "empty file");
	Refused(RunText("sha256 " + SHA_A + " x\n"), "directive", "sha256 with two arguments");
	Refused(RunText("sha256\n"), "directive", "sha256 without argument");
	Refused(RunText(HEAD + "pvar 1\n"), "directive", "pvar 1");
	Refused(RunText(HEAD + "pvar 0\n"), "directive", "pvar 0");
	Refused(RunText(HEAD + "pvar\n"), "directive", "pvar without value");
	Refused(RunText(HEAD + "pvar 2 2\n"), "directive", "pvar with two values");
	Refused(RunText(HEAD + "pvar 2\npvar 2\n"), "directive", "pvar twice");
	Refused(RunText(HEAD + "audio_sync 1\n"), "directive", "audio_sync 1");
	Refused(RunText(HEAD + "audio_sync 0\naudio_sync 0\n"), "directive", "audio_sync twice");
	Refused(RunText(HEAD + "poke 1:00 2:00\n"), "directive", "poke with two arguments");
	Refused(RunText(HEAD + "poke\n"), "directive", "poke without argument");
}

static void BadHex() {
	const auto o = RunText(HEAD + "poke 2a470b:abc\n");
	Refused(o, "hex", "poke bytes odd length");
	Check(o.hashed == 0, "bad hex: eboot not hashed");
	Refused(RunText(HEAD + "poke 2a470b:zz\n"), "hex", "poke bytes not hex");
	Refused(RunText(HEAD + "poke 2a470b:\n"), "hex", "poke bytes empty");
	Refused(RunText(HEAD + "poke 2g:00\n"), "hex", "poke offset not hex");
	Refused(RunText(HEAD + "poke :00\n"), "hex", "poke offset empty");
	Refused(RunText(HEAD + "poke 100000000:00\n"), "hex", "poke offset >= 0x100000000");
	Refused(RunText(HEAD + "poke 0x2a470b:00\n"), "hex", "poke offset with 0x");
	Refused(RunText(HEAD + "poke 2a470b\n"), "hex", "poke without colon");
	Refused(RunText(HEAD + "poke 2a470b:00:00\n"), "hex", "poke with two colons");
	Refused(RunText("sha256 " + SHA_A.substr(1) + "\n"), "hex", "sha256 63 digits");
	Refused(RunText("sha256 " + SHA_A + "0\n"), "hex", "sha256 65 digits");
	Refused(RunText("sha256 " + std::string(63, '0') + "g\n"), "hex", "sha256 not hex");
}

static void Overlaps() {
	const auto o = RunText(HEAD + "poke 10:0000\npoke 11:00\n");
	Refused(o, "overlap", "second poke inside the first");
	Check(o.hashed == 0, "overlap in the file: eboot not hashed");
	Refused(RunText(HEAD + "poke 11:00\npoke 10:0000\n"), "overlap", "first poke inside the second");
	Refused(RunText(HEAD + "poke 10:00\npoke 10:00\n"), "overlap", "same offset");
	Refused(RunText(HEAD + "poke 10:000000\npoke 8:000000000000000000\n"), "overlap", "partial overlap from below (9 bytes at 8)");
	Check(RunText(HEAD + "poke 10:000000\npoke 8:0000000000000000\n").ok, "8 bytes at 8 end right before 0x10");
	Check(RunText(HEAD + "poke 10:00\npoke 11:00\n").ok, "adjacent pokes do not overlap");
	Check(RunText(HEAD + "poke 11:00\npoke 10:00\n").ok, "adjacent pokes, reverse order");
}

static void EnvConflicts() {
	const std::string file = HEAD + BODY;
	G::Env            e;
	e.pvar = "0";
	Refused(RunText(file, e), "env", "KYTY_PVAR=0 against pvar 2");
	e.pvar = "";
	Refused(RunText(file, e), "env", "KYTY_PVAR empty against pvar 2");
	e.pvar = "1";
	Refused(RunText(file, e), "env", "KYTY_PVAR=1 against pvar 2");
	e.pvar = "2";
	Applied(RunText(file, e), "KYTY_PVAR=2 with pvar 2");
	e.pvar = "0";
	Applied(RunText(HEAD + "poke 687375:e790cb07\naudio_sync 0\n", e), "KYTY_PVAR=0 with a file without pvar");

	G::Env a;
	a.audio_sync = "1";
	Refused(RunText(file, a), "env", "KYTY_AUDIO_SYNC=1 against audio_sync 0");
	a.audio_sync = "0";
	Applied(RunText(file, a), "KYTY_AUDIO_SYNC=0 with audio_sync 0");
	a.audio_sync = "";
	Applied(RunText(file, a), "KYTY_AUDIO_SYNC empty (atoi 0, off) with audio_sync 0");
	a.audio_sync = "1";
	Applied(RunText(HEAD + "pvar 2\n", a), "KYTY_AUDIO_SYNC=1 with a file without audio_sync");

	G::Env p;
	p.poke = "27e46c:909090909090";
	Applied(RunText(file, p), "KYTY_POKE 27e46c (the tags' log patch) with the file");
	p.poke = "27e46c:909090909090,2a470b:c5fb10051ddd0a08c5fb5905b5c40a08c5f25a8d40ffffff90";
	Refused(RunText(file, p), "overlap", "KYTY_POKE repeating the limiter poke");
	p.poke = "2a470a:0000";
	Refused(RunText(file, p), "overlap", "KYTY_POKE covering the first byte of the limiter poke");
	p.poke = "2a4723:00";
	Refused(RunText(file, p), "overlap", "KYTY_POKE at the last byte of the limiter poke");
	p.poke = "2a4724:00";
	Applied(RunText(file, p), "KYTY_POKE right after the limiter poke");
	p.poke = "2a470a:00";
	Applied(RunText(file, p), "KYTY_POKE right before the limiter poke");
	p.poke = "687379:00,687374:00";
	Applied(RunText(file, p), "KYTY_POKE on both sides of the Havok poke");
	p.poke = "687376:0";
	Applied(RunText(file, p), "KYTY_POKE with one nibble writes nothing (the loop writes whole pairs)");
	p.poke = "2a470b::00";
	Refused(RunText(file, p), "overlap", "KYTY_POKE a::b is two parts for Common::Split (empty part dropped)");
	p.poke = "2a470b";
	Applied(RunText(file, p), "KYTY_POKE item of one part is skipped as the loop skips it");
	p.poke = "2a470b:00:00";
	Applied(RunText(file, p), "KYTY_POKE item of three parts is skipped as the loop skips it");
	p.poke = ",,27e46c:90,,";
	Applied(RunText(file, p), "KYTY_POKE empty items");
	p.poke = "100000000:00";
	Refused(RunText(file, p), "env", "KYTY_POKE at an absolute address");
	p.poke = "";
	Applied(RunText(file, p), "KYTY_POKE empty");
	const auto h = RunText(file, e);
	Check(h.hashed == 1, "env conflict: checked after the hash (sha first)");
}

static void NoFile() {
	const auto o = Run(nullptr, SHA_A);
	Refused(o, "open", "no file");
	Check(o.hashed == 0, "no file: eboot not hashed");
}

static bool ReadAll(const std::string& path, std::string* text) {
	std::ifstream f(path, std::ios::binary);
	if (!f) {
		return false;
	}
	text->assign(std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>());
	return true;
}

static std::string HashPath(const std::string& path) {
	std::ifstream f(path, std::ios::binary);
	if (!f) {
		return {};
	}
	G::Sha256 h;
	std::string buf(1 << 20, '\0');
	for (;;) {
		f.read(buf.data(), static_cast<std::streamsize>(buf.size()));
		const auto got = f.gcount();
		if (got > 0) {
			h.Update(reinterpret_cast<const uint8_t*>(buf.data()), static_cast<size_t>(got));
		}
		if (!f) {
			break;
		}
	}
	return h.FinalHex();
}

static void RealFile(const std::string& wt, const std::string& eboot) {
	std::string text;
	const bool  read = ReadAll(wt + "/patches/PPSA21564_pvar.txt", &text);
	Check(read, "patches/PPSA21564_pvar.txt read");
	if (!read) {
		return;
	}
	const std::string sha = HashPath(eboot);
	std::printf("eboot sha256 %s\n", sha.c_str());
	const auto o = Run(&text, sha);
	Applied(o, "the file against the real eboot.bin");
	namespace P = Libs::LibKernel::PVar;
	Check(o.spec.pvar2 && o.spec.audio_sync0, "the file: pvar 2, audio_sync 0");
	Check(o.spec.pokes.size() == 2, "the file: two pokes");
	if (o.spec.pokes.size() == 2) {
		const auto& lim = o.spec.pokes[0];
		const auto& hav = o.spec.pokes[1];
		Check(lim.offset == P::LIMITER && lim.bytes.size() == sizeof(P::LIMITER_BYTES) &&
		          std::memcmp(lim.bytes.data(), P::LIMITER_BYTES, sizeof(P::LIMITER_BYTES)) == 0,
		      "the file: limiter poke = PVar LIMITER / LIMITER_BYTES (the bytes the arming checks)");
		Check(hav.offset == P::HAVOK && hav.bytes.size() == sizeof(P::HAVOK_BYTES) &&
		          std::memcmp(hav.bytes.data(), P::HAVOK_BYTES, sizeof(P::HAVOK_BYTES)) == 0,
		      "the file: Havok poke = PVar HAVOK / HAVOK_BYTES");
	}
	Check(text.find("27e46c") == std::string::npos, "the file: no 27e46c (the log patch)");
	// The ix_sha form (p.333(zh)(1)): the same file with one sha digit changed.
	std::string bad = text;
	const auto  at  = bad.find("\nsha256 ") + 8; // the directive, not the word in a comment
	bad[at]         = bad[at] == '0' ? '1' : '0';
	Refused(Run(&bad, sha), "sha", "the file with one sha digit changed (form of ix_sha)");
	G::Env env;
	env.poke = "27e46c:909090909090";
	Applied(Run(&text, sha, env), "the file + KYTY_POKE 27e46c (form of iv_5/iv_6)");
}

int main(int argc, char** argv) {
	if (argc != 3) {
		std::printf("usage: test_gamepatchfile <worktree> <eboot.bin>\n");
		return 2;
	}
	Sha();
	Valid();
	ShaMismatch();
	Directives();
	BadHex();
	Overlaps();
	EnvConflicts();
	NoFile();
	RealFile(argv[1], argv[2]);
	std::printf("checks %d, failures %d\n", g_pass + g_fail, g_fail);
	if (g_fail == 0) {
		std::printf("ALL OK\n");
	}
	return g_fail == 0 ? 0 : 1;
}
