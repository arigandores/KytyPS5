import re, hashlib, json, sys, os
# FS5d (HPP-512) lead recount of FS5c tags; port of C:/kyty/f287/fs4/fs4d/lead473.py (FS4d), imports no FS5c code
# aborts (rc 3) as soon as C:/kyty/SEALED_RUN.lock appears (general rule 27)
# usage: python lead512.py <out.json> fs5_v,fs5_w,fs5_r1,fs5_hb
D = 'C:/kyty/f287/fs5/fs5c/'
LOCK = 'C:/kyty/SEALED_RUN.lock'
def lockchk():
    if os.path.exists(LOCK):
        print('LOCK APPEARED - abort'); sys.exit(3)
def sha(p):
    h = hashlib.sha256(); n = 0
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b); n += 1
            if n % 64 == 0: lockchk()
    return h.hexdigest()
DEATH = [b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost']
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DR = re.compile(rb' draws=(\d+)')
RX_ST = re.compile(rb'FixSvalStat: validated=(\d+) rejected=(\d+)')
RX_FS = re.compile(rb'FixSval: mode=(\d+) ubo_std_layout=(\d+)')
RX_WIN = re.compile(rb'Window \d+ minimized')
def scan(p, level):
    r = dict(svf=0, svf_hash=set(), fs=[], st_n=0, st_last=None, death={}, ve=0, vw=0, last=0, dual=None, first_guest=None,
             entry=None, first_scene=None, hold_us=0, max_dt=0, k1s=0, change=None, win=0, recov=0, focus=0, skipped=0,
             pc_first=None, rev=set(), cache_dirs=set(), gamepatch=0, lines=0)
    with open(p, 'rb') as f:
        for i, ln in enumerate(f, 1):
            if i % 2000000 == 0: lockchk()
            r['lines'] = i
            if b'FrameTrace: n=' in ln:
                if r['entry'] is not None and r['change'] is None:
                    m = RX_FT.search(ln)
                    if m:
                        dt = int(m.group(2))
                        if r['first_scene'] is None:
                            d = RX_DR.search(m.group(3))
                            if d and int(d.group(1)) >= 100: r['first_scene'] = i
                        else:
                            r['hold_us'] += dt; r['max_dt'] = max(r['max_dt'], dt)
                            if dt >= 1000000: r['k1s'] += 1
                continue
            if b'[Vulkan][' in ln:
                if b'[Vulkan][E]' in ln: r['ve'] += 1
                if b'[Vulkan][W]' in ln: r['vw'] += 1
                if b'last time reporting it' in ln: r['last'] += 1
                continue
            if b'SPIR-V validation failed' in ln:
                r['svf'] += 1
                for m in re.finditer(rb'hash=0x([0-9a-fA-F]+)', ln): r['svf_hash'].add(m.group(1).decode())
            if b'FixSval' in ln:
                m = RX_FS.search(ln)
                if m: r['fs'].append((i, int(m.group(1)), int(m.group(2))))
                m = RX_ST.search(ln)
                if m: r['st_n'] += 1; r['st_last'] = (i, int(m.group(1)), int(m.group(2)))
            if b'---' in ln or b'Unhandled' in ln or b'GpuHang' in ln or b'DeviceLost' in ln:
                for d in DEATH:
                    if d in ln: r['death'][d.decode()] = r['death'].get(d.decode(), 0) + 1
            if r['dual'] is None and b'DualSrcBlend: supported=' in ln: r['dual'] = (i, ln.strip()[-40:].decode('latin1'))
            if r['first_guest'] is None and b'GuestOut' in ln: r['first_guest'] = i
            if b'minimized' in ln and RX_WIN.search(ln): r['win'] += 1
            if b'Recovering Vulkan swapchain' in ln: r['recov'] += 1
            if b'lost keyboard focus' in ln: r['focus'] += 1
            if b'AsyncPipelines: skipped draw' in ln: r['skipped'] += 1
            if b'GamePatch:' in ln: r['gamepatch'] += 1
            if b'Shader translation cache:' in ln: r['cache_dirs'].add(ln.split(b'cache:', 1)[1].strip().decode('latin1'))
            if r['pc_first'] is None and b'PipelinePrecache:' in ln: r['pc_first'] = ln.strip()[:120].decode('latin1')
            if b'Fork build arigandores/KytyPS5 ' in ln or b', git = ' in ln:
                m = re.search(rb'(?:KytyPS5 |-g)([0-9a-f]{7})', ln)
                r['rev'].add(m.group(1).decode() if m else '?')
            if b'Level has started:' in ln:
                if r['entry'] is None and level in ln: r['entry'] = i
                elif r['entry'] is not None and r['change'] is None and level not in ln: r['change'] = i
    for k in ('svf_hash', 'rev', 'cache_dirs'): r[k] = sorted(r[k])
    return r
SG = b'underwater_aerial_garden'; HB = b'hoover_beach'
TAGS = sys.argv[2].split(',')
out = {}
for t in TAGS:
    lockchk()
    o = {}
    rd = D + 'runs/' + t + '/'
    for k in ('installed_sha', 'installed_before', 'installed_after', 'cold'):
        o[k] = open(rd + k + '.txt').read().strip()
    o['manifest_cmp'] = open(rd + 'manifest_cmp.txt').read().strip().splitlines()[0]
    o['manifest_cmp_ref'] = open(rd + 'manifest_cmp_ref.txt').read().strip().splitlines()[0]
    lv = HB if t == 'fs5_hb' else SG
    fl = {'log': D + 'log_' + t + '.txt', 'out': D + 'stdout_' + t + '.txt'}
    js = json.load(open(D + t + '.json'))
    o['json_binary_sha256'] = js.get('binary_sha256')
    o['attempts'] = [(a.get('outcome'), a.get('detail')) for a in js.get('attempts', []) if isinstance(a, dict)]
    if t != 'fs5_w':
        fl['mp4'] = D + 'rec_' + t + '.mp4'; fl['idx'] = D + 'rec_' + t + '.mp4.idx'
        o['idx_lines'] = sum(1 for _ in open(fl['idx'], 'rb'))
    for k, p in fl.items(): o['sha_' + k] = sha(p)
    o['log'] = scan(fl['log'], lv); o['out'] = scan(fl['out'], lv)
    out[t] = o
    print(t, 'scanned', flush=True)
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str)
print('done')
