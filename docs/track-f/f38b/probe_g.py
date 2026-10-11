"""F38b (HPP-764, Red Team): LOCAL probe only (worktree C:/kyty/f287/f38b/wt, never main) - arm G of the F25 stand:
a read from a position at or past the end of the file (remaining = 0, as E); the hook lets call 1 read for real (0 bytes
at the end of the file) and then grows the file through the second handle to offset + 8192 (another writer appends while
the guest reads at the end), returning the real result. Correct code: remaining = 0 -> early return, no flag -> ret 0,
no error. After the trial the file is cut back to its size and checked by sha256 (RestoreFile from FILE_SIZE).
The count of G comes from the environment F38B_NG (default 0: the stand is unchanged in its rows).
Row fields reused: trunc_done = the growth succeeded, size_at_c2 = the size after the growth.
usage: probe_g.py <wt>"""
import sys

path = sys.argv[1] + '/tests/F25ReadFailStand.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')

edits = [
    ('constexpr int ARM_T = 4;\nconstexpr int ARM_COUNT = 5;\nconstexpr const char* ARM_NAMES[ARM_COUNT] = {"A", "K", "Z", "E", "T"};\n',
     'constexpr int ARM_T = 4;\nconstexpr int ARM_G = 5; // F38b probe\nconstexpr int ARM_COUNT = 6;\n'
     'constexpr const char* ARM_NAMES[ARM_COUNT] = {"A", "K", "Z", "E", "T", "G"};\n'),
    ('\tif (st->mode == ARM_T && k == 2) {\n',
     '\tif (st->mode == ARM_G && k == 1) {\n'
     '\t\t// F38b probe: the real read at the end of the file, then another writer grows the file.\n'
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
    ('\tif (t.arm == ARM_E) {\n\t\toffset = FILE_SIZE + rng() % 4097;\n\t}\n',
     '\tif (t.arm == ARM_E || t.arm == ARM_G) {\n\t\toffset = FILE_SIZE + rng() % 4097;\n\t}\n'),
    ('\tif (t.arm != ARM_E && rng() % 4 == 0) {\n',
     '\tif (t.arm != ARM_E && t.arm != ARM_G && rng() % 4 == 0) {\n'),
    ('\tst.trunc_to = offset;\n',
     '\tst.trunc_to = (t.arm == ARM_G) ? offset + 8192 : offset;\n'),
    ('\tif (t.arm == ARM_T) {\n\t\tt.restore_ok = RestoreFile(sf.h2, sf.original, sf.sha, std::min<uint64_t>(offset, FILE_SIZE)) ? 1 : 0;\n\t}\n',
     '\tif (t.arm == ARM_T || t.arm == ARM_G) {\n\t\tt.restore_ok = RestoreFile(sf.h2, sf.original, sf.sha, std::min<uint64_t>(offset, FILE_SIZE)) ? 1 : 0;\n\t}\n'),
    ('\tstd::array<int, ARM_COUNT> counts {};\n\tfor (int a = 0; a < ARM_COUNT; a++) {\n',
     '\tstd::array<int, ARM_COUNT> counts {};\n'
     '\tcounts[ARM_G] = std::getenv("F38B_NG") != nullptr ? std::atoi(std::getenv("F38B_NG")) : 0; // F38b probe\n'
     '\tfor (int a = 0; a < ARM_T + 1; a++) {\n'),
]
for old, new in edits:
    assert t.count(old) == 1, ('anchor count', t.count(old), old[:60])
    t = t.replace(old, new)
if crlf:
    t = t.replace('\n', '\r\n')
open(path, 'wb').write(t.encode('utf-8'))
print('probe G applied, crlf', crlf)
