"""F38a (HPP-763, ROADMAP s122 item 691(v)-(g)): KYTY_FIX_F25 in src/kernel/fileSystem.cpp (default 0).
Usage: patch_fs_f38a.py <repo root>. Whole-line anchors, each must occur exactly once; CRLF kept as found; writes bytes."""
import sys

path = sys.argv[1].rstrip('/') + '/src/kernel/fileSystem.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
assert 'KYTY_FIX_F25' not in text, 'already patched'

BS = chr(92)
NL = BS + 'n'
TAB_ESC = BS + 't'


def rep(old, new):
    global text
    n = text.count(old)
    assert n == 1, 'anchor count %d: %r' % (n, old[:80])
    text = text.replace(old, new)


# 1. The knob and the report line, before the HOST_FILE_WRITE_BUFFERED comment (after FixB4Enabled).
anchor1 = '// Host write path with a user-space buffer that _Exit does not flush: stdio fwrite on non-Windows hosts\n'
add1 = (
    '// Track F, F38a (HPP-763, ROADMAP s122 item 691(v)-(g), row F25): KYTY_FIX_F25 (default 0: unset, "", 0/false/off/no =\n'
    '// OFF; read once, first by Initialize). At 1 a double read failure of ReadGuestWithRetry (the direct read into the guest\n'
    '// buffer and the retry through a host buffer both gave 0 with nbytes > 0 and remaining > 0) is returned by KernelRead /\n'
    '// KernelPread as KERNEL_ERROR_EIO instead of 0 - a 0 in the middle of a file is the end of the file for the guest -\n'
    '// unless the file size read again is at or below the read position (the file was shortened meanwhile: a real end of\n'
    '// file, 0 as before). The guest buffer is not written; the file position is the one before the call.\n'
    'static bool FixF25Enabled() {\n'
    '\tstatic const bool enabled = Common::EnvFlagOn("KYTY_FIX_F25");\n'
    '\treturn enabled;\n'
    '}\n'
    '\n'
    '// F25, KYTY_FIX_F25=1 only: one line per double read failure returned as EIO, at most 32 per process.\n'
    'static void FixF25Report(int d, uint64_t nbytes, uint64_t pos) {\n'
    '\tstatic std::atomic<int> logged {0};\n'
    '\tif (logged.fetch_add(1, std::memory_order_relaxed) < 32) {\n'
    '\t\tLOGF("FixF25: read failed twice d=%d size=%" PRIu64 " pos=%" PRIu64 "' + NL + '", d, nbytes, pos);\n'
    '\t}\n'
    '}\n'
    '\n')
rep(anchor1, add1 + anchor1)

# 2. Initialize: the mode line after the FixB4 one.
anchor2 = '\tLOGF("FixB4: mode=%d' + NL + '", FixB4Enabled() ? 1 : 0);\n'
rep(anchor2, anchor2 + '\tLOGF("FixF25: mode=%d' + NL + '", FixF25Enabled() ? 1 : 0);\n')

# 3. ReadGuestWithRetry: the double failure flag.
old3 = ('void ReadGuestWithRetry(File* file, void* buf, size_t nbytes, uint64_t pos, uint64_t remaining,\n'
        '                        uint32_t* bytes_read) {\n'
        '\tfile->f.Read(buf, static_cast<uint32_t>(nbytes), bytes_read);\n')
new3 = ('// Track F, F38a (row F25): *failed_twice - true only when the direct read gave 0 with nbytes > 0 and remaining > 0\n'
        '// and the retry read gave 0 too; false on every other path (the early return included).\n'
        'void ReadGuestWithRetry(File* file, void* buf, size_t nbytes, uint64_t pos, uint64_t remaining,\n'
        '                        uint32_t* bytes_read, bool* failed_twice) {\n'
        '\t*failed_twice = false;\n'
        '\tfile->f.Read(buf, static_cast<uint32_t>(nbytes), bytes_read);\n')
rep(old3, new3)
old3b = ('\tif (*bytes_read != 0) {\n'
         '\t\tstd::memcpy(buf, temporary.data(), *bytes_read);\n'
         '\t}\n'
         '}\n')
new3b = ('\tif (*bytes_read != 0) {\n'
         '\t\tstd::memcpy(buf, temporary.data(), *bytes_read);\n'
         '\t} else {\n'
         '\t\t*failed_twice = true;\n'
         '\t}\n'
         '}\n')
rep(old3b, new3b)

# 4. KernelRead: decide under file->mutex, return after the is_invalid check.
old4 = ('\tuint32_t bytes_read = 0;\n'
        '\tReadGuestWithRetry(file, buf, nbytes, pos, remaining, &bytes_read);\n')
new4 = ('\tuint32_t bytes_read = 0;\n'
        '\tbool     read_failed_twice = false;\n'
        '\tReadGuestWithRetry(file, buf, nbytes, pos, remaining, &bytes_read, &read_failed_twice);\n'
        '\t// Track F, F38a (row F25, ROADMAP s122 item 691(v)(2)-(3)): at KYTY_FIX_F25=1 a double read failure is an I/O\n'
        '\t// error unless the size read again is at or below pos (the file was shortened meanwhile); the position stays pos.\n'
        '\tbool fix_f25_eio = false;\n'
        '\tif (read_failed_twice && FixF25Enabled()) {\n'
        '\t\tfix_f25_eio = pos < file->f.Size();\n'
        '\t\tfile->f.Seek(pos);\n'
        '\t}\n')
rep(old4, new4)
old4b = ('\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tLOGF("' + TAB_ESC + 'Read %u bytes from: %s' + NL + '", bytes_read, Common::PathToString(file->real_name).c_str());\n')
new4b = ('\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tif (fix_f25_eio) {\n'
         '\t\tFixF25Report(d, nbytes, pos);\n'
         '\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tLOGF("' + TAB_ESC + 'Read %u bytes from: %s' + NL + '", bytes_read, Common::PathToString(file->real_name).c_str());\n')
rep(old4b, new4b)

# 5. KernelPread: the same; the file position is restored by the existing Seek(pos).
old5 = ('\tfile->f.Seek(offset);\n'
        '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_read);\n'
        '\tfile->f.Seek(pos);\n')
new5 = ('\tbool read_failed_twice = false;\n'
        '\tfile->f.Seek(offset);\n'
        '\tReadGuestWithRetry(file, buf, nbytes, static_cast<uint64_t>(offset), remaining, &bytes_read,\n'
        '\t                   &read_failed_twice);\n'
        '\t// Track F, F38a (row F25, item 691(v)(2)-(3)): see KernelRead; the file position is restored just below as before.\n'
        '\tbool fix_f25_eio = false;\n'
        '\tif (read_failed_twice && FixF25Enabled()) {\n'
        '\t\tfix_f25_eio = static_cast<uint64_t>(offset) < file->f.Size();\n'
        '\t}\n'
        '\tfile->f.Seek(pos);\n')
rep(old5, new5)
old5b = ('\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tLOGF("' + TAB_ESC + 'Read %u bytes (pos = %" PRId64 ") from: %s' + NL + '", bytes_read, offset,\n')
new5b = ('\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tif (fix_f25_eio) {\n'
         '\t\tFixF25Report(d, nbytes, static_cast<uint64_t>(offset));\n'
         '\t\treturn KERNEL_ERROR_EIO;\n'
         '\t}\n'
         '\n'
         '\tLOGF("' + TAB_ESC + 'Read %u bytes (pos = %" PRId64 ") from: %s' + NL + '", bytes_read, offset,\n')
rep(old5b, new5b)

if crlf:
    text = text.replace('\n', '\r\n')
open(path, 'wb').write(text.encode('utf-8'))
print('patched', path, 'crlf' if crlf else 'lf')
