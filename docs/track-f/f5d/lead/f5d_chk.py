# F5d (HPP-358) lead recount: (a) layer activity after the episode; (g) outcome of V =0 with the stand; sha256 of inputs
import hashlib, sys
D = 'C:/kyty/f287/f5c/'
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()
DEATH = [b'--- Error', b'EXIT', b'ErrorDeviceLost', b'Fatal Error', b'SIGABRT', b'Unhandled exception']
def scan(tag):
    p = D + 'log_' + tag + '.txt'
    st = {'minimize': None, 'restore': None, 'rec': 0, 'E': 0, 'W2_after_restore': 0, 'E_after_restore': 0, 'death': 0,
          'zero_begin': 0, 'zero_end': 0, 'fixon': 0, 'last': b'', 'lines': 0, 'ft_after_restore': 0, 'limit': 0}
    with open(p, 'rb') as f:
        for n, line in enumerate(f, 1):
            st['lines'] = n
            if line.strip():
                st['last'] = line.strip()[:120]
            if b'TestMinimize: minimize' in line: st['minimize'] = n
            elif b'TestMinimize: restore' in line: st['restore'] = n
            if b'Recovering Vulkan swapchain' in line: st['rec'] += 1
            if b'[Vulkan][E]' in line:
                st['E'] += 1
                if st['restore']: st['E_after_restore'] += 1
            if b'[Vulkan][W][2]' in line and st['restore']: st['W2_after_restore'] += 1
            if b'last time reporting it' in line: st['limit'] += 1
            if any(k in line for k in DEATH): st['death'] += 1
            if b'SwapchainZeroExtent: begin' in line: st['zero_begin'] += 1
            if b'SwapchainZeroExtent: end' in line: st['zero_end'] += 1
            if b'FixMinimize: on' in line: st['fixon'] += 1
            if st['restore'] and line.startswith(b'FrameTrace'): st['ft_after_restore'] += 1
    st['last'] = st['last'].decode('utf-8', 'replace')
    return p, st
for tag in sys.argv[1:]:
    p, st = scan(tag)
    print(tag, 'sha256', sha(p))
    for k in sorted(st):
        print(' ', k, st[k])
    so = D + 'stdout_' + tag + '.txt'
    try:
        print('  stdout sha256', sha(so))
        with open(so, 'rb') as f:
            s = f.read()
        print('  stdout death', sum(s.count(k) for k in DEATH), 'Recovering', s.count(b'Recovering Vulkan swapchain'))
    except OSError as e:
        print('  stdout', e)
print('F5D CHK DONE')
