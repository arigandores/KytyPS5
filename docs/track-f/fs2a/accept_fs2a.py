# FS2a (HPP-381, ROADMAP p.298(v)): acceptance of the second shipment binary - sha256, counts of the named strings in the
# exe (signature, revision, knob names, FixMinimize / FixB9a lines), the same counts for the FS binary dac02fb9 (reference,
# copy in C:/kyty/f287/bin) and the installed exe of the emulator folder (read only, not touched). The form of accept_fsa.py.
import hashlib, sys
BINS = [('fs2a', sys.argv[1]),
        ('dac02fb9 (FS copy)', 'C:/kyty/f287/bin/kyty_emulator_dac02fb9.exe'),
        ('installed', 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe')]
VER = b'KytyPS5-2026-09-15-6a2987a-1854-g9c9d86ae'
STRS = [b'56189185f9e9f9a0ea5174f3f85206e6d099db3d', b'699c1e4b7db359067b461e029b913c4b6e78dc90', VER,
        b'KytyPS5-2026-09-15-6a2987a-1766-g95eec776',
        b'DualSrcBlend: supported=', b'DualSrcBlend: patched', b'KYTY_FIX_DUALSRC', b'KYTY_FIX_B26', b'KYTY_FIX_B1B',
        b'KYTY_FIX_MINIMIZE', b'KYTY_TEST_MINIMIZE', b'FixMinimize: on', b'SwapchainZeroExtent: begin',
        b'KYTY_FIX_B9A', b'FixB9a: on', b'AudioPropagation: calls', b'KYTY_S_PCW', b'KYTY_BIND_LEAN', b'KYTY_RT_SKIP']
WANT = {b'56189185f9e9f9a0ea5174f3f85206e6d099db3d': 1, VER: -1,
        b'DualSrcBlend: supported=': 1, b'DualSrcBlend: patched': 1, b'KYTY_FIX_DUALSRC': 1, b'KYTY_FIX_B26': 1,
        b'KYTY_FIX_B1B': 1, b'KYTY_FIX_MINIMIZE': 1, b'KYTY_TEST_MINIMIZE': 1, b'FixMinimize: on': 1,
        b'KYTY_FIX_B9A': 1, b'FixB9a: on': 1, b'AudioPropagation: calls': 1}
ok = True
for name, path in BINS:
    b = open(path, 'rb').read()
    print('==', name, path, 'size', len(b), 'sha256', hashlib.sha256(b).hexdigest())
    for s in STRS:
        n = b.count(s)
        mark = ''
        if name == 'fs2a' and s in WANT:
            good = n >= 1 if WANT[s] < 0 else n == WANT[s]  # -1: present (version string + label)
            ok &= good
            mark = '  want %s %s' % ('>=1' if WANT[s] < 0 else WANT[s], 'OK' if good else 'FAIL')
        print('  %-44s %d%s' % (s.decode(), n, mark))
print('ACCEPT', 'ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
