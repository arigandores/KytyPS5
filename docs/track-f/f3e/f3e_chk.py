"""F3e (HPP-343, lead): own recount of F3d tags by p.259(e)(4)-(5) - fault pages, pairs X / (X>>8)&~0x3fff, low pages,
BvhLoopCapTrip lines, death markers, [Vulkan][E], translation cache lines, sum dt after the first scene frame, frames >= 1 s.
Does not import the F3d reader. Chunked byte scan; exits 3 if the sealed-run lock appears between files."""
import hashlib, os, re, sys
R = 'C:/kyty/f287/f3d/'
LOCK = 'C:/kyty/SEALED_RUN.lock'
TAGS = [('f3d_a1', 'big_hand_pirate_island'), ('f3d_a2', 'big_hand_pirate_island'), ('f3d_a3', 'voxel_world'),
        ('f3d_a4', 'voxel_world'), ('f3d_bv', 'underwater_aerial_garden'), ('f3d_bw', 'underwater_aerial_garden'),
        ('f3d_c1', 'big_hand_pirate_island'), ('f3d_c2', 'voxel_world')]
GIB4 = 1 << 32
PAGE = 0x4000
CH = 1 << 24
RXF = re.compile(rb'Accessed non-GPU cached memory at (?:0x)?([0-9a-fA-F]+)')
RXT = re.compile(rb'Shader translation cache:([^\r\n]*)')
RXFT = re.compile(rb'FrameTrace:[^\n]*?\bn=(\d+)[^\n]*?\bdt_us=(\d+)[^\n]*?\bdraws=(\d+)')
CNT = {'trip': b'BvhLoopCapTrip:', 'vke': b'[Vulkan][E]', 'err': b'--- Error ---', 'lost': b'ErrorDeviceLost',
       'fatal': b'Fatal Error', 'limit': b'last time reporting it', 'minim': b'minimized', 'recov': b'Recovering Vulkan swapchain'}


def scan(path, level):
    h = hashlib.sha256()
    entry = ('Level has started: %s' % level).encode()
    faults = set(); tc = []; c = {k: 0 for k in CNT}; ft = []; epos = None
    off = 0; tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CH)
            h.update(b)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf; continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if whole:
                for m in RXF.finditer(whole):
                    faults.add(int(m.group(1), 16))
                for m in RXT.finditer(whole):
                    tc.append(m.group(1).strip().decode('latin1'))
                for k, v in CNT.items():
                    c[k] += whole.count(v)
                if epos is None:
                    i = whole.find(entry)
                    if i >= 0:
                        epos = off + i
                for m in RXFT.finditer(whole):
                    ft.append((off + m.start(), int(m.group(2)), int(m.group(3))))
                off += len(whole)
            if not b:
                break
    after = [x for x in ft if epos is not None and x[0] > epos]
    fi = next((i for i, x in enumerate(after) if x[2] >= 100), None)
    post = after[fi + 1:] if fi is not None else []
    pairs = sorted((a, (a >> 8) & ~(PAGE - 1)) for a in faults if a >= GIB4 and ((a >> 8) & ~(PAGE - 1)) in faults)
    lows = sorted(a for a in faults if a < GIB4)
    return dict(sha=h.hexdigest(), pages=len(faults), pairs=pairs, lows=lows, tc=sorted(set(x.replace('/', '\\').rstrip('\\').split('\\')[-1] for x in tc)),
                ntc=len(tc), c=c, entry=epos is not None, hold=sum(x[1] for x in post) / 1e6, nfr=len(post),
                mean=(sum(x[1] for x in post) / len(post)) if post else None, ge1s=sum(1 for x in post if x[1] >= 1000000),
                ge100=sum(1 for x in post[600:] if x[1] >= 100000), maxdt=max((x[1] for x in post), default=None))


ok = True
for tag, lvl in TAGS:
    if os.path.exists(LOCK):
        print('LOCK appeared before', tag); sys.exit(3)
    r = scan(R + 'log_%s.txt' % tag, lvl)
    c = r['c']
    deaths = c['err'] + c['lost'] + c['fatal']
    print('== %s %s log sha256 %s' % (tag, lvl, r['sha']))
    print('  fault pages %d; pairs %s; low pages %s' % (r['pages'], ['0x%x/0x%x' % p for p in r['pairs']], ['0x%x' % a for a in r['lows']]))
    print('  BvhLoopCapTrip %d; death markers %d (err %d lost %d fatal %d); [Vulkan][E] %d; limit lines %d; minimized %d; recovering %d'
          % (c['trip'], deaths, c['err'], c['lost'], c['fatal'], c['vke'], c['limit'], c['minim'], c['recov']))
    print('  translation cache lines %d dirs %s; entry %s; frames after first scene frame %d; sum dt %.1f s; mean dt %s; frames >= 1 s %d; max dt %s; frames >= 100 ms after 600 %d'
          % (r['ntc'], r['tc'], r['entry'], r['nfr'], r['hold'], None if r['mean'] is None else round(r['mean']), r['ge1s'], r['maxdt'], r['ge100']))
    fix1 = tag[4] in 'ab'
    if fix1:
        ok &= (not r['pairs']) and (not r['lows']) and c['trip'] == 0 and deaths == 0 and r['ge1s'] == 0 and r['tc'] == ['variant_fixb26_fixb1b']
    else:
        ok &= len(r['pairs']) >= 1 and r['tc'] == ['variant_fixb26']
    if tag == 'f3d_bw':
        ok &= c['vke'] == 0
for f in ['rec_f3d_a2.mp4', 'rec_f3d_a4.mp4', 'rec_f3d_bv.mp4', 'sheet_f3d_a2.png', 'sheet_f3d_a4.png', 'sheetpair_f3d_bv.png',
          'glitch_f3d_a2.txt', 'glitch_f3d_a4.txt', 'glitch_f3d_bv.txt']:
    h = hashlib.sha256(open(R + f, 'rb').read()).hexdigest()
    print(f, h)
for f in ['glitch_f3d_a2.txt', 'glitch_f3d_a4.txt', 'glitch_f3d_bv.txt']:
    print(f, open(R + f, encoding='utf-8', errors='replace').read().strip().replace('\n', ' | '))
print('F3E RECOUNT', 'ALL OK' if ok else 'MISMATCH')
