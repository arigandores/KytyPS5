# F4a2 (HPP-346, ROADMAP p.262(v)): acceptance of the F4c binary - counts of the named strings in the exe, sha256,
# the same counts for the installed 9235a7ac copy (reference) and the F4a binary 34d293ad.
import hashlib, sys
BINS = [('f4a2', sys.argv[1]),
        ('9235a7ac (installed copy)', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe'),
        ('34d293ad (F4a)', 'C:/kyty/f287/bin/kyty_emulator_34d293ad.exe')]
STRS = [b'699c1e4b7db359067b461e029b913c4b6e78dc90', b'846a041a4d4902a2afc2ca8f1d7067c5d2ae982b',
        b'DualSrcBlend: supported=', b'DualSrcBlend: patched', b'DualSrcBlend: skip', b'KYTY_FIX_DUALSRC',
        b'KYTY_FIX_B26', b'KYTY_S_PCW', b'KYTY_BIND_LEAN', b'06f049f252b4f374f9489a8a8fedb14c054e88f6']
WANT = {b'699c1e4b7db359067b461e029b913c4b6e78dc90': 1, b'DualSrcBlend: supported=': 1, b'DualSrcBlend: patched': 1,
        b'KYTY_FIX_B26': 0, b'KYTY_S_PCW': 0}
ok = True
for name, path in BINS:
    b = open(path, 'rb').read()
    print('==', name, path, 'size', len(b), 'sha256', hashlib.sha256(b).hexdigest())
    for s in STRS:
        n = b.count(s)
        mark = ''
        if name == 'f4a2' and s in WANT:
            good = n == WANT[s]
            ok &= good
            mark = '  want %d %s' % (WANT[s], 'OK' if good else 'FAIL')
        print('  %-44s %d%s' % (s.decode(), n, mark))
print('ACCEPT', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
