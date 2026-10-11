"""F38a2 (HPP-777, ROADMAP s122 item 693(b)(1)-(2)): F25 stand edition 3 - arm G (a read at or past the end of a file
that another writer grows right after the real call 1) and member E (half the trials at offset = size exactly).
Anchors are whole lines; each must occur exactly once. CRLF is kept if the file has it; written with write_bytes.

    python patch_stand_f38a2.py <repo root>"""
import sys

path = sys.argv[1] + '/tests/F25ReadFailStand.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')

edits = [
    # header: edition 3, arm G, usage, exit 6
    ('// is set by the environment before FileSystem::Initialize; =0 and =1 are separate processes of one build.\n',
     '// is set by the environment before FileSystem::Initialize; =0 and =1 are separate processes of one build.\n'
     '//\n'
     '// Edition 3 (F38a2 HPP-777, ROADMAP s122 item 693(b)(1)-(2)): arm G added; in the arms E and G the trials with an even\n'
     '// index read from offset = file size exactly, the odd ones from size + 1 ... size + 4096 (remaining = 0 in all). The\n'
     '// driver is docs/track-f/f38a2/run_stand_f38a2.py.\n'),
    ('//       trial the file is restored through the second handle and checked by sha256 against the original.\n',
     '//       trial the file is restored through the second handle and checked by sha256 against the original.\n'
     '//   G - a read from a position at or past the end of the file (remaining = 0), no injected failure; call 1 is the real\n'
     '//       ReadFile (0 bytes at the end of the file), right after it the hook grows the file to offset + 8192 through the\n'
     '//       second handle (another writer appends while the guest reads the end) and returns the real result. After the\n'
     '//       trial the file is cut back to its size through the second handle and checked by sha256 against the original.\n'
     '//       Row fields of G: trunc_done = the growth succeeded, size_at_c2 = the size after the growth.\n'),
    ('// Usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <out.tsv>\n',
     '// Usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <nG> <out.tsv>\n'),
    ('// after a T trial (the row is written first).\n',
     '// after a T or G trial (the row is written first).\n'),
    # arm constants
    ('constexpr int ARM_COUNT = 5;\n', 'constexpr int ARM_G = 5;\nconstexpr int ARM_COUNT = 6;\n'),
    ('constexpr const char* ARM_NAMES[ARM_COUNT] = {"A", "K", "Z", "E", "T"};\n',
     'constexpr const char* ARM_NAMES[ARM_COUNT] = {"A", "K", "Z", "E", "T", "G"};\n'),
    ('\tHANDLE   trunc_h    = INVALID_HANDLE_VALUE; // T: the second handle of the stand file\n',
     '\tHANDLE   trunc_h    = INVALID_HANDLE_VALUE; // T, G: the second handle of the stand file\n'),
    ('\tuint64_t trunc_to   = 0;                    // T: the size the file is shortened to on call 2\n',
     '\tuint64_t trunc_to   = 0;                    // T: the size the file is shortened to on call 2; G: grown to after call 1\n'),
    ('\tint      trunc_done = 0;                    // T: SetEndOfFile succeeded on call 2\n',
     '\tint      trunc_done = 0;                    // T: SetEndOfFile succeeded on call 2; G: after call 1\n'),
    ('\tint64_t  size_at_c2 = -1;                   // T: the file size seen through the second handle after the shortening\n',
     '\tint64_t  size_at_c2 = -1;                   // T: the file size seen through the second handle after the shortening; G: growth\n'),
    # hook: arm G
    ('\tif (st->mode == ARM_T && k == 2) {\n',
     '\tif (st->mode == ARM_G && k == 1) {\n'
     '\t\t// The real read at the end of the file, then another writer grows the file through the second handle.\n'
     '\t\tconst BOOL r = g_real_read_file(handle, buffer, size, read, overlapped);\n'
     '\t\tLARGE_INTEGER to {};\n'
     '\t\tto.QuadPart = static_cast<LONGLONG>(st->trunc_to);\n'
     '\t\tif (SetFilePointerEx(st->trunc_h, to, nullptr, FILE_BEGIN) != FALSE && SetEndOfFile(st->trunc_h) != FALSE) {\n'
     '\t\t\tst->trunc_done = 1;\n'
     '\t\t}\n'
     '\t\tLARGE_INTEGER now {};\n'
     '\t\tif (GetFileSizeEx(st->trunc_h, &now) != FALSE) {\n'
     '\t\t\tst->size_at_c2 = now.QuadPart;\n'
     '\t\t}\n'
     '\t\treturn r;\n'
     '\t}\n'
     '\tif (st->mode == ARM_T && k == 2) {\n'),
    # trial fields
    ('\tint      trunc_done = 0; // T: the file was shortened on call 2\n',
     '\tint      trunc_done = 0; // T: the file was shortened on call 2; G: the file was grown after call 1\n'),
    ('\tint64_t  size_at_c2 = -1; // T: the file size after the shortening\n',
     '\tint64_t  size_at_c2 = -1; // T: the file size after the shortening; G: after the growth\n'),
    ('\tint      restore_ok = 0; // T: the file was restored and its sha256 equals the original (other arms: 1, not touched)\n',
     '\tint      restore_ok = 0; // T, G: the file was restored and its sha256 equals the original (other arms: 1, not touched)\n'),
    # offsets of E and G
    ('\t// from a position at or past the end of the file (remaining = 0).\n',
     '\t// from a position at or past the end of the file (remaining = 0). Edition 3: the arms E and G read from offset = file\n'
     '\t// size exactly when the trial index is even, from size + 1 ... size + 4096 when it is odd.\n'),
    ('\tif (t.arm == ARM_E) {\n\t\toffset = FILE_SIZE + rng() % 4097;\n\t}\n',
     '\tif (t.arm == ARM_E || t.arm == ARM_G) {\n\t\toffset = (t.index % 2 == 0) ? FILE_SIZE : FILE_SIZE + 1 + rng() % 4096;\n\t}\n'),
    ('\tif (t.arm != ARM_E && rng() % 4 == 0) {\n',
     '\tif (t.arm != ARM_E && t.arm != ARM_G && rng() % 4 == 0) {\n'),
    ('\tst.trunc_to = offset;\n',
     '\tst.trunc_to = (t.arm == ARM_G) ? offset + 8192 : offset;\n'),
    ('\tif (t.arm == ARM_T) {\n\t\tt.restore_ok = RestoreFile(sf.h2, sf.original, sf.sha, std::min<uint64_t>(offset, FILE_SIZE)) ? 1 : 0;\n\t}\n',
     '\tif (t.arm == ARM_T || t.arm == ARM_G) {\n\t\t// G: from = FILE_SIZE (offset >= FILE_SIZE), nothing is written, SetEndOfFile cuts the growth.\n'
     '\t\tt.restore_ok = RestoreFile(sf.h2, sf.original, sf.sha, std::min<uint64_t>(offset, FILE_SIZE)) ? 1 : 0;\n\t}\n'),
    ('// T: write back the file tail from `from` and the original size through the second handle, then compare by sha256.\n',
     '// T, G: write back the file tail from `from` and the original size through the second handle, then compare by sha256.\n'),
    # main: arguments
    ('\tif (argc != 8) {\n\t\tstd::fprintf(stderr, "usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <out.tsv>\\n");\n',
     '\tif (argc != 9) {\n\t\tstd::fprintf(stderr, "usage: f25_read_fail_stand <seed> <nA> <nK> <nZ> <nE> <nT> <nG> <out.tsv>\\n");\n'),
    ('\tconst std::string out_path = argv[7];\n', '\tconst std::string out_path = argv[8];\n'),
    ('\t\t\t\tstd::printf("RESTORE FAILED entry=%d index=%d\\n", t.entry, t.index);\n',
     '\t\t\t\tstd::printf("RESTORE FAILED entry=%d arm=%s index=%d\\n", t.entry, ARM_NAMES[t.arm], t.index);\n'),
]
for old, new in edits:
    n = t.count(old)
    assert n == 1, ('anchor count', n, old[:80])
    t = t.replace(old, new)
if crlf:
    t = t.replace('\n', '\r\n')
open(path, 'wb').write(t.encode('utf-8'))
print('edition 3 applied, edits %d, crlf %s' % (len(edits), crlf))
