# F4b2 (HPP-347, Red Team): own acceptance of the F4c binary by ROADMAP s122 p.262(v) and p.268(v):
# sha256 of the copy and of the build output, counts of byte strings in the binary (ASCII), the version
# string of the build tree, and the same counts on the installed 9235a7ac (read only) for contrast.
import hashlib
import sys

files = {
    'F4c copy': 'C:/kyty/f287/bin/kyty_emulator_c9a5e198.exe',
    'F4c build': 'C:/kyty/f287/f4a2/build/install/kyty_emulator.exe',
    'installed': 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe',
}
need = [
    ('699c1e4b7db359067b461e029b913c4b6e78dc90', 1),
    ('846a041a', None),
    ('DualSrcBlend: supported=', 1),
    ('DualSrcBlend: patched', 1),
    ('DualSrcBlend: skip ps=', None),
    ('KYTY_FIX_DUALSRC', None),
    ('KYTY_FIX_B26', 0),
    ('KYTY_S_PCW', 0),
    ('KYTY_BIND_LEAN', None),
    ('KytyPS5-2026-09-15-6a2987a-1374-g06f049f2-dirty', 1),
    ('06f049f252b4f374f9489a8a8fedb14c054e88f6', None),
    ('no_spirv', None),
    ('location_above1', None),
]
ok = True
data = {}
for k, p in files.items():
    b = open(p, 'rb').read()
    data[k] = b
    print(k, p, 'bytes', len(b), 'sha256', hashlib.sha256(b).hexdigest())
ok &= hashlib.sha256(data['F4c copy']).hexdigest().startswith('c9a5e198')
ok &= data['F4c copy'] == data['F4c build']
ok &= hashlib.sha256(data['installed']).hexdigest().startswith('9235a7ac')
print('%-50s %8s %8s %8s %s' % ('string', 'F4c', 'want', '9235a7ac', 'ok'))
for s, want in need:
    c = data['F4c copy'].count(s.encode())
    i = data['installed'].count(s.encode())
    good = want is None or c == want
    ok &= good
    print('%-50s %8d %8s %8d %s' % (s, c, '-' if want is None else want, i, 'OK' if good else 'FAIL'))
print('ACCEPT ALL OK' if ok else 'ACCEPT FAIL')
sys.exit(0 if ok else 1)
