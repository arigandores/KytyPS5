"""Track M, M6a3 (HPP-856): third edit of the stand - case ao_obj_span: a grain of 16 bytes whose first 8 bytes lie on a
committed read/write host page and the last 8 on the next page, reserved only (MEM_RESERVE). The OS check must look at
every page of the grain (item 772(v)): ao_obj_unread 1, ao_obj_vq 0, the process lives (a check of the first page only
reads the reserved page - access violation). Whole-line anchors, each must match once; CRLF kept.
Usage: python patch_m6a3_c.py <tree root>   Last line ALL OK or FAIL."""
import sys

ROOT = sys.argv[1].rstrip('/')
T = chr(9)
NL = chr(10)
path = ROOT + '/tests/MWave2DiagStand.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
text = raw.decode('utf-8').replace('\r\n', '\n')
fails = []


def L(*parts):
    return ''.join(parts)


pairs = [
    (L('// M6a3: a committed host page with the protection prot (PAGE_NOACCESS, PAGE_READWRITE | PAGE_GUARD) - not read.', NL),
     L('// M6a3: 8 bytes before the end of a committed read/write host page whose next page is reserved only - a grain of', NL,
       '// 16 bytes spans both pages (not read: the second page is not committed).', NL,
       'const void* HostSpan() {', NL,
       '#if KYTY_PLATFORM == KYTY_PLATFORM_WINDOWS', NL,
       T, 'auto* r = static_cast<uint8_t*>(VirtualAlloc(nullptr, 0x2000, MEM_RESERVE, PAGE_NOACCESS));', NL,
       T, 'if (r == nullptr || VirtualAlloc(r, 0x1000, MEM_COMMIT, PAGE_READWRITE) == nullptr) {', NL,
       T, T, 'std::printf("MStand: m6 host span failed\\n");', NL,
       T, T, 'std::fflush(stdout);', NL,
       T, T, 'std::_Exit(3);', NL,
       T, '}', NL,
       T, 'std::memset(r, 0, 0x1000);', NL,
       T, 'r[0x1000 - 4] = 0x7f;', NL,
       T, 'return r + 0x1000 - 8;', NL,
       '#else', NL,
       T, 'return UNREADABLE;', NL,
       '#endif', NL,
       '}', NL,
       NL,
       '// M6a3: a committed host page with the protection prot (PAGE_NOACCESS, PAGE_READWRITE | PAGE_GUARD) - not read.', NL)),
    (L(T, 'Check("ao_obj_guard", [&] { D::NoteAudioPort(true, HostPage(PAGE_READWRITE | PAGE_GUARD), 0x100, 4); },', NL,
       T, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 1}, {"ao_obj_vq", 0}});', NL),
     L(T, 'Check("ao_obj_guard", [&] { D::NoteAudioPort(true, HostPage(PAGE_READWRITE | PAGE_GUARD), 0x100, 4); },', NL,
       T, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 1}, {"ao_obj_vq", 0}});', NL,
       T, '// M6a3: the grain spans a committed page and a reserved one - every page is checked.', NL,
       T, 'Check("ao_obj_span", [&] { D::NoteAudioPort(true, HostSpan(), 0x100, 4); },', NL,
       T, '      {{"ao_obj_push", 1}, {"ao_obj_nz", 0}, {"ao_obj_unread", 1}, {"ao_obj_vq", 0}});', NL)),
]
for old, new in pairs:
    n = text.count(old)
    if n != 1:
        fails.append('anchor x%d: %s' % (n, old.splitlines()[0][:90]))
        continue
    text = text.replace(old, new, 1)
if not fails:
    if crlf:
        text = text.replace('\n', '\r\n')
    open(path, 'wb').write(text.encode('utf-8'))
for f in fails:
    print('FAILED ' + f)
print('ALL OK' if not fails else 'FAIL')
sys.exit(0 if not fails else 1)
