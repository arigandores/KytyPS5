"""Session 125 audit (HPP-77): independent recount of the [I] rows of design125 rev 2 section 3.4/3.7 and of
sources125.md, from the sealed g2_119 logs.  Own parser; no code shared with g2_119.py or rows125.py.

Blocks come from GateArm: lines (block b of period P starting at frame F: rows n = F+1 .. F+P, the report shift is
done by the emulator, s67).  Window = positions 10..88 of the block inclusive (ROADMAP s122 p.55(b) rule, not the
p.28(b) exception).  Populations:
  G  - g2_119-style selection with window 10..88: complete blocks, kept rows >= FIRST_FRAME 2100, whole ABBA
       quartets (the g2_119 rule, window changed only); arm 0 rows.
  X  - GateArm blocks, arm 0, excluded blocks exactly as rows125.py lists them (sh119: 3, 84, 85; mut119: 3, 84).
  R  - reproduction of rows125.py grouping by the 'blk' field of the main line (block 0 then also holds every row
       before the schedule; positions are taken in sorted-n order inside a blk group).
Also: a sweep of every C:/kyty/s116..s124 log_*.txt for guest-send timing lines (LagTrace:, AvTrace: flip,
GpuSubmitOps:, SampleTrace:).
usage: python recount125.py [--sweep]"""
import re, sys, statistics, glob, os, hashlib

LOGS = {'sh119': ('C:/kyty/s119/log_sh119.txt', {3, 84, 85}),
        'mut119': ('C:/kyty/s119/log_mut119.txt', {3, 84})}
SHA = {'sh119': 'fe8b0e2373a9f6daa1dc072b46212309d8a74558a97affdeb639f9ef11b8f0ba',
       'mut119': '2b0adcb807055d736e89338aced5f39b4bd682c50d98e142799c847622eec8c8'}
WIN_LO, WIN_HI = 10, 88          # p.55(b), inclusive
FIRST_FRAME = 2100
KV = re.compile(rb'(\w+)=(-?\d+)')
GA = re.compile(rb'^GateArm: arm=(\d+) arms=\d+ block=(\d+) frame=(\d+) period=(\d+)')
WANT = {b'FrameTrace: ': ('dt_us', 'cpu_gpu_us', 'lat_us', 'arm', 'blk', 'draws'),
        b'FrameTrace-draw: ': ('spin_gpu_us', 'bda_scan'),
        b'FrameTrace-x: ': ('da_wjobs', 'da_wdrop', 'da_wskip', 'da_wdepth', 'da_wlag_us', 'slc_total',
                            'gw_idle_ns', 'cram_write')}
NEED = [f for fs in WANT.values() for f in fs if f != 'cram_write']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def parse(path):
    rows, blocks = {}, []
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'GateArm:'):
                m = GA.match(line)
                blocks.append(tuple(int(x) for x in m.groups()))    # arm, block, frame, period
                continue
            for pre, fields in WANT.items():
                if line.startswith(pre):
                    d = {k.decode(): int(v) for k, v in KV.findall(line[len(pre):])}
                    if 'n' not in d:
                        break
                    r = rows.setdefault(d['n'], {})
                    for k in fields:
                        if k in d and k not in r:
                            r[k] = d[k]
                    break
    return rows, blocks


def stats(sel, label):
    def mean(fn):
        return statistics.fmean(fn(r) for r in sel)
    J = sum(r['da_wjobs'] for r in sel)
    out = {
        'rows': len(sel),
        'dt_us': mean(lambda r: r['dt_us']),
        'cpu_net': mean(lambda r: r['cpu_gpu_us'] - r['spin_gpu_us']),
        'dt-cpu_net': mean(lambda r: r['dt_us'] - (r['cpu_gpu_us'] - r['spin_gpu_us'])),
        'busy_mean': mean(lambda r: r['cpu_gpu_us'] / r['dt_us']),
        'busy_med': statistics.median(r['cpu_gpu_us'] / r['dt_us'] for r in sel),
        'lat_us': mean(lambda r: r['lat_us']),
        'wjobs': mean(lambda r: r['da_wjobs']), 'wdrop': mean(lambda r: r['da_wdrop']),
        'wskip': mean(lambda r: r['da_wskip']),
        'lag/job': sum(r['da_wlag_us'] for r in sel) / J,
        'depth/job': sum(r['da_wdepth'] for r in sel) / J,
        'slc_total': mean(lambda r: r['slc_total']), 'bda_scan': mean(lambda r: r['bda_scan']),
        'gw_idle_ns': mean(lambda r: r['gw_idle_ns']),
        'n_min': min(r['_n'] for r in sel), 'n_max': max(r['_n'] for r in sel),
    }
    print('  [%s] rows %d  n %d..%d' % (label, out['rows'], out['n_min'], out['n_max']))
    for k in ('dt_us', 'cpu_net', 'dt-cpu_net', 'busy_mean', 'busy_med', 'lat_us', 'wjobs', 'wdrop', 'wskip',
              'lag/job', 'depth/job', 'slc_total', 'bda_scan', 'gw_idle_ns'):
        print('    %-11s %12.3f' % (k, out[k]))
    return out


def run(tag):
    path, excl = LOGS[tag]
    s = sha(path)
    print('%s  %s  sha %s  %s' % (tag, path, s, 'OK' if s == SHA[tag] else 'MISMATCH'))
    rows, blocks = parse(path)
    for n, r in rows.items():
        r['_n'] = n
    full = lambda r: all(k in r for k in NEED)
    arm_of = {b: a for a, b, fr, p in blocks}
    geom = {b: (fr, p) for a, b, fr, p in blocks}
    # the rows' own arm must agree with the GateArm arm (row-arm check)
    bad_arm = 0
    win = {}
    for b, (fr, p) in geom.items():
        ns = list(range(fr + 1, fr + p + 1))
        if not all(n in rows for n in ns):
            continue
        for n in ns:
            if rows[n].get('arm') != arm_of[b] or rows[n].get('blk') != b:
                bad_arm += 1
        win[b] = ns[WIN_LO:WIN_HI + 1]
    print('  GateArm blocks %d, complete %d, row-arm/blk mismatches %d, window len %d'
          % (len(blocks), len(win), bad_arm, len(next(iter(win.values())))))
    # population G: g2_119 rule with window 10..88
    elig = {b: ns for b, ns in win.items() if min(ns) >= FIRST_FRAME}
    used = set()
    for q in range(0, max(geom) + 1, 4):
        quartet = range(q, q + 4)
        if all(k in elig for k in quartet):
            used.update(quartet)
    G = [rows[n] for b in sorted(used) if arm_of[b] == 0 for n in elig[b] if full(rows[n])]
    gb = sorted(b for b in used if arm_of[b] == 0)
    print('  G blocks arm0: %d (%d..%d)' % (len(gb), gb[0], gb[-1]))
    res = {'G': stats(G, 'G g2-rule, window 10..88')}
    # population X: GateArm blocks, arm 0, rows125's exclusion list
    xb = sorted(b for b in win if arm_of[b] == 0 and b not in excl)
    X = [rows[n] for b in xb for n in win[b] if full(rows[n])]
    print('  X blocks arm0: %d %s' % (len(xb), xb[:4]))
    res['X'] = stats(X, 'X GateArm blocks, rows125 exclusions')
    # population R: rows125 reproduction (group by blk field)
    grp = {}
    for n, r in rows.items():
        if 'blk' in r and 'arm' in r:
            grp.setdefault(r['blk'], []).append(n)
    R = []
    for b, ns in grp.items():
        if b in excl:
            continue
        ns.sort()
        for i, n in enumerate(ns):
            if rows[n]['arm'] == 0 and WIN_LO <= i <= WIN_HI and full(rows[n]):
                R.append(rows[n])
    res['R'] = stats(R, 'R rows125 reproduction (blk grouping)')
    R0 = [r for r in R if r['blk'] == 0]
    print('  R block-0 rows: %d, n %d..%d, mean dt_us %.1f' % (len(R0), min(r['_n'] for r in R0),
          max(r['_n'] for r in R0), statistics.fmean(r['dt_us'] for r in R0)))
    cw = sum(r.get('cram_write', 0) for r in rows.values())
    print('  cram_write sum over all rows: %d' % cw)
    return res


def sweep():
    pats = [b'LagTrace:', b'AvTrace: flip', b'GpuSubmitOps:', b'SampleTrace:']
    files = sorted(glob.glob('C:/kyty/s11[6-9]/log_*.txt') + glob.glob('C:/kyty/s12[0-4]/log_*.txt'))
    tot = {p: 0 for p in pats}
    print('sweep: %d logs' % len(files))
    for fn in files:
        c = {p: 0 for p in pats}
        with open(fn, 'rb') as f:
            for line in f:
                for p in pats:
                    if p in line:
                        c[p] += 1
        for p in pats:
            tot[p] += c[p]
        print('  %-40s %12d B  %s' % (fn, os.path.getsize(fn), ' '.join('%s=%d' % (p.decode(), c[p]) for p in pats)))
    print('sweep total: ' + ' '.join('%s=%d' % (p.decode(), tot[p]) for p in pats))


if __name__ == '__main__':
    for t in LOGS:
        run(t)
    if '--sweep' in sys.argv:
        sweep()
