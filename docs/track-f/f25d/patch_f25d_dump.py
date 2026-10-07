# F25d (HPP-667; item 599(b)(8)): diag_b32_tests --dump-bench <dir> writes the CloseWindowBench report texts of fixed
# inputs (the RC8 cases and the 6.6 s / 21 s windows) to <dir> and exits - the equivalence check of the index fix: the
# texts of the quadratic code (before) and of the indexed code (after) must be equal byte for byte.
# Usage: python patch_f25d_dump.py <worktree root>
import sys

ROOT = sys.argv[1].rstrip('/\\')
T = 'tests/DiagB32Tests.cpp'
t = open(ROOT + '/' + T, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor count %d != %d: %r' % (n, count, old[:120]))
    return text.replace(old, new)


DUMP = r'''
#ifdef KYTY_DIAG_B32_F25
// F25d (item 599(b)(8)): the report texts of fixed bench inputs, one file per input (equivalence of the index fix).
static int DumpBench(const char* dir) {
	struct In {
		const char* name;
		uint32_t    before, nsamples, nwaits, nopen, nmatch, kq_every, seed;
	};
	const In ins[] = {{"w6600", 100, 1320, 200, 0, 0, 0, 1},
	                  {"w21000", 100, 4200, 0, 0, 0, 0, 1},
	                  {"r2000_s11", 1, kHist - 1, 2000, 90, 0, 0, 11},
	                  {"r2000_s12", 1, kHist - 1, 2000, 90, 0, 0, 12},
	                  {"r20000_s11", 1, kHist - 1, 20000, 90, 0, 0, 11},
	                  {"r20000_s15", 1, kHist - 1, 20000, 90, 0, 0, 15},
	                  {"r20000_open0", 1, kHist - 1, 20000, 0, 0, 0, 21},
	                  {"r500_s3", 1, 800, 500, 40, 0, 0, 3},
	                  {"m2000_kq9", 1, kHist - 1, 2000, 90, 45, 9, 31},
	                  {"m20000_kq13", 1, kHist - 1, 20000, 90, 90, 13, 32},
	                  {"m300_kq1", 50, 1500, 300, 60, 30, 1, 33},
	                  {"m300_kq40", 50, 1500, 300, 60, 60, 40, 34}};
	for (const auto& x: ins) {
		Test::BenchIn in;
		in.nslots   = 90;
		in.before   = x.before;
		in.nsamples = x.nsamples;
		in.nwaits   = x.nwaits;
		in.nopen    = x.nopen;
		in.nmatch   = x.nmatch;
		in.kq_every = x.kq_every;
		in.seed     = x.seed;
		const auto  o    = Test::CloseWindowBench(in);
		std::string path = std::string(dir) + "/" + x.name + ".txt";
		FILE*       f    = std::fopen(path.c_str(), "wb");
		if (f == nullptr) {
			std::printf("cannot write %s\n", path.c_str());
			return 1;
		}
		std::fwrite(o.text.data(), 1, o.text.size(), f);
		std::fclose(f);
		size_t open_lines = 0;
		for (size_t p = o.text.find(" open=1 "); p != std::string::npos; p = o.text.find(" open=1 ", p + 1)) {
			open_lines++;
		}
		size_t sw_t = 0; // -t lines with Sr or Sw samples (the nearest-snapshot split in use)
		for (const auto& l: Lines(o.text)) {
			if (StartsWith(l, "DiagB32-t: ") && (l.find(" Sr=0 ") == std::string::npos || l.find(" Sw=0 ") == std::string::npos)) {
				sw_t++;
			}
		}
		std::printf("%s bytes=%zu close_ms=%.3f open_w_lines=%zu t_lines_with_Sr_or_Sw=%zu\n", x.name, o.text.size(),
		            static_cast<double>(o.close_ns) / 1e6, open_lines, sw_t);
	}
	return 0;
}
#endif

int main(int argc, char** argv) {
#ifdef KYTY_DIAG_B32_F25
	if (argc == 3 && std::strcmp(argv[1], "--dump-bench") == 0) {
		return DumpBench(argv[2]);
	}
#else
	(void)argc;
	(void)argv;
#endif
'''
t = sub(t, '\nint main() {\n', DUMP)
open(ROOT + '/' + T, 'wb').write(t.encode('utf-8'))
print('DUMP PATCH OK')
