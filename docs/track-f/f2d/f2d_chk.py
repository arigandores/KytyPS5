# F2d (HPP-311): lead's own recount of the three F2c logs (does not import the F2c code).
import re, hashlib, sys
D = 'C:/kyty/f287/f2c/'
TSV = 'C:/kyty/KytyPS5/docs/track-f/f1a/b26_shaders.tsv'
rows = [l.split('\t') for l in open(TSV, encoding='utf-8').read().splitlines()[1:] if l.strip()]
h96 = {r[0].lower() for r in rows if r[2] == '0x21'}
h5 = {r[0].lower() for r in rows if r[2] in ('0x0c', '0xe3')}
assert len(h96) == 96 and len(h5) == 5, (len(h96), len(h5))
RX_OPC = re.compile(rb'(SOP1|SOP2|SOPC|SOPK|SOPP|VOP1|VOP2|VOP3|VOPC|SMEM|MUBUF|MIMG|DS|FLAT)[^\n]{0,40}?(0x[0-9a-fA-F]+)')
RX_CSP = re.compile(rb'CsPretranslate: (ready|skipped|miss|hit) hash=([0-9a-fA-F]{16})(.*)')
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost', b'DbgExit')
ok = True
exp = {'a': ('1', (96, 0, 0, 4)), 'b': ('1', (96, 0, 0, 4)), 'c': ('0', (96, 1, 4, 0))}
for t in 'abc':
    p = D + 'log_f2c_%s.txt' % t
    hs = hashlib.sha256()
    prof = {}
    csp = {}
    reopen = 0
    cfg_out = 0
    deaths = 0
    vk_e = 0
    trips = 0
    cache_line = b''
    for l in open(p, 'rb'):
        hs.update(l)
        if b'opcode is not implemented' in l:
            m = RX_OPC.search(l)
            k = (m.group(1).decode(), m.group(2).decode().lower()) if m else ('?', '?')
            prof[k] = prof.get(k, 0) + 1
        m = RX_CSP.search(l)
        if m:
            h = m.group(2).decode().lower()
            if h in h96 and m.group(1) in (b'miss', b'hit'):
                reopen += 1
            if h in h5 and m.group(1) in (b'ready', b'skipped'):
                csp.setdefault(h, []).append(m.group(1).decode() + m.group(3).decode(errors='replace')[:90])
        if b'shader CFG build failed' in l and b'CsPretranslate:' not in l:
            cfg_out += 1
        if any(d in l for d in DEATH):
            deaths += 1
        if b'[Vulkan][E]' in l:
            vk_e += 1
        if b'BvhLoopCapTrip:' in l:
            trips += 1
        if b'Shader translation cache:' in l and not cache_line:
            cache_line = l.strip()[:160]
    p21 = sum(v for (f, o), v in prof.items() if f == 'SOP1' and o == '0x21')
    p0c = sum(v for (f, o), v in prof.items() if f == 'SOP1' and o == '0x0c')
    pe3 = sum(v for (f, o), v in prof.items() if f in ('VOPC', 'VOP3') and o == '0xe3')
    pf3 = sum(v for (f, o), v in prof.items() if f in ('VOPC', 'VOP3') and o == '0xf3')
    got = (p21, p0c, pe3, pf3)
    print('f2c_%s sha256 %s' % (t, hs.hexdigest()))
    print('  profile 0x21/0x0c/0xe3/0xf3 = %s (expect %s) other=%s' % (got, exp[t][1], {k: v for k, v in prof.items() if k not in (('SOP1', '0x21'), ('SOP1', '0x0c'), ('VOPC', '0xe3'), ('VOPC', '0xf3'))}))
    print('  B26a reopen: miss|hit of 96 = %d, CFG failed outside CsPretranslate = %d, deaths = %d, [Vulkan][E] = %d, BvhLoopCapTrip = %d' % (reopen, cfg_out, deaths, vk_e, trips))
    print('  cache line: %s' % cache_line.decode(errors='replace'))
    for h in sorted(h5):
        print('   %s %s' % (h, csp.get(h)))
    ok &= got == exp[t][1]
    ok &= reopen == 0 and deaths == 0 and vk_e == 0
    ok &= all(len(csp.get(h, [])) == 1 for h in h5)
print('ALL OK' if ok else 'MISMATCH')
sys.exit(0 if ok else 1)
