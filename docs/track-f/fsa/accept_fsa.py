# FSa (HPP-368, ROADMAP p.282(g)(1)): acceptance of the shipment binary - sha256, counts of the named strings in the exe
# (signature, revision, knob names, DualSrcBlend lines), the same counts for the F3d binary 2e6df8f0 (LF 478868b5) and
# the installed 9235a7ac copy (reference). Read only.
import hashlib, sys
BINS = [('fsa', sys.argv[1]),
        ('2e6df8f0 (F3d)', 'C:/kyty/f287/bin/kyty_emulator_2e6df8f0.exe'),
        ('9235a7ac (installed copy)', 'C:/kyty/s128/kyty_emulator_9235a7ac.exe')]
STRS = [b'56189185f9e9f9a0ea5174f3f85206e6d099db3d', b'699c1e4b7db359067b461e029b913c4b6e78dc90',
        b'KytyPS5-2026-09-15-6a2987a-1766-g95eec776', b'fba4fbfd',
        b'DualSrcBlend: supported=', b'DualSrcBlend: patched', b'KYTY_FIX_DUALSRC', b'KYTY_FIX_B26', b'KYTY_FIX_B1B',
        b'KYTY_FIX_MINIMIZE', b'KYTY_TEST_MINIMIZE', b'SwapchainZeroExtent: begin', b'KYTY_S_PCW', b'KYTY_BIND_LEAN',
        b'KYTY_RT_SKIP']
WANT = {b'56189185f9e9f9a0ea5174f3f85206e6d099db3d': 1, b'KytyPS5-2026-09-15-6a2987a-1766-g95eec776': -1,
        b'DualSrcBlend: supported=': 1, b'DualSrcBlend: patched': 1, b'KYTY_FIX_DUALSRC': 1, b'KYTY_FIX_B26': 1,
        b'KYTY_FIX_B1B': 1, b'KYTY_FIX_MINIMIZE': 1, b'KYTY_TEST_MINIMIZE': 1}
ok = True
for name, path in BINS:
    b = open(path, 'rb').read()
    print('==', name, path, 'size', len(b), 'sha256', hashlib.sha256(b).hexdigest())
    for s in STRS:
        n = b.count(s)
        mark = ''
        if name == 'fsa' and s in WANT:
            good = n >= 1 if WANT[s] < 0 else n == WANT[s]  # -1: present (version string + label)
            ok &= good
            mark = '  want %s %s' % ('>=1' if WANT[s] < 0 else WANT[s], 'OK' if good else 'FAIL')
        print('  %-44s %d%s' % (s.decode(), n, mark))
print('ACCEPT', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
