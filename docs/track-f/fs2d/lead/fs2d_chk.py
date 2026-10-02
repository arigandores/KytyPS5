"""FS2d lead recount (HPP-384): own counts on the FS2c logs, no executor code imported."""
import hashlib, re, sys
D = 'C:/kyty/f287/fs2c/'
TAGS = ['fs2_w', 'fs2_w0', 'fs2_v', 'fs2_t', 'fs2_tw']
DEATH = [b'Unhandled exception', b'DEVICE_LOST', b'device lost', b'Fatal error', b'EXCEPTION_ACCESS_VIOLATION', b'--- Error ---']
PAT = {
    'vke': b'[Vulkan][E]',
    'fixmin': b'FixMinimize: on',
    'fixb9a': b'FixB9a: on',
    'dual': b'DualSrcBlend: supported=1 enabled=1',
    'assert': b'ASSERT:',
    'umsg': b'user_msg_param',
    'apstub': b'[AudioPropagation_v1]',
    'stubcall': b'Unresolved import stub called',
    'tmin': b'TestMinimize: minimize',
    'trest': b'TestMinimize: restore',
    'winmin': b'Window 1 minimized',
    'recover': b'Recovering Vulkan swapchain',
    'zbeg': b'SwapchainZeroExtent: begin',
    'zend': b'SwapchainZeroExtent: end',
    'vuid': b'VUID-VkSwapchainCreateInfoKHR-imageExtent-01689',
    'extent0': b'imageExtent (width = 0, height = 0)',
    'lvl': b'Level has started',
    'limit': b'last time reporting',
    'srccreate': b'SourceCreate',
}
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()
ok = True
for t in TAGS:
    for kind in ('log', 'stdout'):
        p = D + '%s_%s.txt' % (kind, t)
        c = dict.fromkeys(PAT, 0); deaths = 0
        apstub_stub = 0; first = {}; after_tmin_extent = None; vuid_near = None
        lines = []
        with open(p, 'rb') as f:
            for n, l in enumerate(f):
                for k, v in PAT.items():
                    if v in l:
                        c[k] += 1
                        first.setdefault(k, n)
                if b'[AudioPropagation_v1]' in l and b'Unresolved import stub called' in l:
                    apstub_stub += 1
                for d in DEATH:
                    if d in l:
                        deaths += 1; break
                if 'tmin' in first and after_tmin_extent is None and b'[Vulkan][E]' in l and PAT['extent0'] in l:
                    after_tmin_extent = n; lines = []
                if after_tmin_extent is not None and vuid_near is None and n - after_tmin_extent <= 3 and PAT['vuid'] in l:
                    vuid_near = n - after_tmin_extent
        print('%-7s %-6s sha %s deaths %d apstub_stubcall %d %s extent0_after_tmin_line %s vuid_offset %s' % (
            t, kind, sha(p)[:16], deaths, apstub_stub,
            ' '.join('%s=%d' % (k, c[k]) for k in PAT), after_tmin_extent, vuid_near))
        if kind == 'log':
            if t in ('fs2_w', 'fs2_v', 'fs2_t'):
                ok &= c['vke'] == 0 and deaths == 0 and c['fixmin'] == 1 and c['fixb9a'] == 1 and c['assert'] == 0 \
                    and c['umsg'] == 0 and apstub_stub == 0 and c['dual'] >= 1 and c['limit'] == 0
            if t in ('fs2_w', 'fs2_v'):
                ok &= c['tmin'] == 1 and c['zbeg'] == 1 and c['zend'] == 1
            if t == 'fs2_w0':
                ok &= c['fixmin'] == 0 and after_tmin_extent is not None and vuid_near is not None and vuid_near <= 3
print('FS2D RECOUNT', 'ALL OK' if ok else 'MISMATCH')
