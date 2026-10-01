import sys, hashlib
bins = {'6f495a65':'C:/kyty/f287/bin/kyty_emulator_6f495a65.exe','abce7916':'C:/kyty/f287/bin/kyty_emulator_abce7916.exe','9235a7ac':'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe'}
pats = [b'699c1e4b7db359067b461e029b913c4b6e78dc90', b'KYTY_FIX_MINIMIZE', b'FixMinimize: on', b'SwapchainZeroExtent: begin', b'SwapchainZeroExtent: end frames_dropped=',
        b'KYTY_TEST_MINIMIZE', b'TestMinimize: minimize', b'TestMinimize: restore', b'TestMinimize: armed', b'TestMinimize: config',
        b'Level has started: ', b'KYTY_FIX_B1B', b'KYTY_FIX_B26', b'KYTY_FIX_DUALSRC', b'KYTY_S_PCW', b'gaf7e5ff9', b'Vulkan presentation retry exhausted']
data = {k: open(v,'rb').read() for k,v in bins.items()}
for k,d in data.items():
    print(k, 'sha256', hashlib.sha256(d).hexdigest()[:16], 'bytes', len(d))
print('pattern', *bins.keys())
for p in pats:
    print(p.decode(), *[data[k].count(p) for k in bins])
