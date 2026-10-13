import os, re, sys, collections, time
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present, exit'); sys.exit(3)
LOGS = sys.argv[1:] or ['C:/kyty/m657/m3a/log_m3_sg_v_r1.txt', 'C:/kyty/m657/m3a/log_m3_hb_f.txt',
                        'C:/kyty/m657/m3a/log_m3_i.txt']
SUBS = [
    b'APR submit failed for unknown file id', b'APR submit read failed', b'APR submit event failed',
    b'AMPR submit write-address failed', b'AMM submit command failed', b'APR read missing host file',
    b'APR resolve missing path', b'APR stat failed', b'APR size failed', b'MT265: mode',
    b'user event add:', b'user event edge add:', b'user event trigger:', b'user event delete:',
    b'AMPR event add:', b'AMPR system event add:', b'AMPR event delete:', b'Equeue create:',
    b'Equeue wait:', b'Equeue wait received', b'Equeue wait timedout', b'Equeue delete:',
    b'SystemService event', b'reserve-fixed replace', b'\t type = ', b'\t name = ',
    b'KYTY_PRINT_NAMES', b'Ampr::', b'Sysmodule::', b'SystemService::', b'unsupported param_id',
]
pn_re = re.compile(rb'^\[\d+\]\[[\d:.]+\] (\w+)::(\w+)::(\w+)\(\)')
id_re = re.compile(rb'^\t id = (-?\d+)\s*$')
hexv = lambda l: int(l.split(b'=')[1].strip().split()[0], 16)


def overlap(iv, a, n):
    for (s, l) in iv:
        if a < s + l and s < a + n:
            return (s, l)
    return None


for path in LOGS:
    t0 = time.time()
    cnt = collections.Counter()
    first = {}
    pn = collections.Counter()
    ids = collections.Counter()
    id_prev = collections.Counter()
    eq_names = collections.Counter()
    # memory block state
    prev = b''
    blk = None
    direct_live = []  # (vaddr,size)
    flex_live = []
    dmaps = 0
    dmap_fixed = 0
    dmap_fixed_over_live = []
    dmap_flags = collections.Counter()
    dmap_types = collections.Counter()
    last_type = None
    unmaps = 0
    nlines = 0
    with open(path, 'rb') as f:
        for line in f:
            nlines += 1
            for s in SUBS:
                if s in line:
                    cnt[s] += 1
                    if s not in first:
                        first[s] = (nlines, line[:200])
            m = pn_re.match(line)
            if m:
                pn[m.group(3)] += 1
            m = id_re.match(line)
            if m:
                ids[int(m.group(1))] += 1
                id_prev[prev.strip()[:60]] += 1
            if b'Equeue create:' in line:
                eq_names[line.split(b':', 1)[1].strip()[:40]] += 1
            if line.startswith(b'\t type = '):
                try:
                    last_type = int(line.split(b'=')[1])
                except Exception:
                    last_type = None
            # memory blocks
            if line.startswith(b'\t in_addr  = 0x'):
                blk = {'in': hexv(line), 'ln': nlines, 'type': last_type}
                last_type = None
            elif blk is not None:
                if line.startswith(b'\t out_addr = 0x'):
                    blk['out'] = hexv(line)
                elif line.startswith(b'\t dmem     = 0x'):
                    blk['dmem'] = hexv(line)
                elif line.startswith(b'\t size     = 0x'):
                    blk['size'] = hexv(line)
                elif line.startswith(b'\t size     = '):
                    blk['size'] = int(line.split(b'=')[1])
                elif line.startswith(b'\t flags    = 0x'):
                    blk['flags'] = hexv(line)
                elif line.startswith(b'\t name     = '):
                    blk['flex'] = True
                elif line.startswith(b'\t reason   = ') or line.startswith(b'\t gpu_mode = ') and blk.get('flex'):
                    b = blk
                    blk = None
                    if 'size' in b and 'out' in b:
                        if b.get('flex'):
                            if b['out']:
                                flex_live.append((b['out'], b['size']))
                        else:
                            dmaps += 1
                            dmap_flags[b.get('flags', -1)] += 1
                            dmap_types[b.get('type')] += 1
                            fixed = (b.get('flags', 0) & 0x10) != 0
                            if fixed:
                                dmap_fixed += 1
                                o = overlap(direct_live, b['in'], b['size']) or overlap(flex_live, b['in'], b['size'])
                                if o:
                                    dmap_fixed_over_live.append((b['ln'], hex(b['in']), hex(b['size']), hex(o[0]), hex(o[1])))
                            if b['out']:
                                direct_live.append((b['out'], b['size']))
            if line.startswith(b'\t len   = 0x') and prev.startswith(b'\t start = 0x'):
                unmaps += 1
                a = hexv(prev)
                n = hexv(line)
                direct_live = [(s, l) for (s, l) in direct_live if not (a <= s and s + l <= a + n)]
                flex_live = [(s, l) for (s, l) in flex_live if not (a <= s and s + l <= a + n)]
            prev = line
    print('=' * 100)
    print('LOG', path, 'lines', nlines, 'sec %.1f' % (time.time() - t0))
    for s in SUBS:
        print('  %-45r %8d  first=%s' % (s, cnt[s], first.get(s, ('-', b''))[0]))
        if s in first:
            print('      ', first[s][1])
    print('  PRINT_NAME lines total', sum(pn.values()), 'top', pn.most_common(15))
    print('  "\\t id = N" lines', sum(ids.values()), 'values', sorted(ids.items())[:60])
    print('  "\\t id =" preceding lines', id_prev.most_common(10))
    print('  Equeue names', eq_names.most_common(40))
    print('  MapDirect blocks', dmaps, 'fixed', dmap_fixed, 'flags', dict(dmap_flags), 'type(MapDirectMemory2)', dict(dmap_types))
    print('  start/len pairs (munmap|release)', unmaps)
    print('  fixed direct maps over live direct/flex range', len(dmap_fixed_over_live), dmap_fixed_over_live[:10])
print('DONE')
