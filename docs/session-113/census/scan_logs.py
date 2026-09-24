"""Read-only: per-frame BDA regime counters from archived FrameTrace logs.

usage: python scan_logs.py <log> [<log> ...]
Writes nothing; prints window medians and the frames around regime transitions.
"""
import re
import sys
import statistics as st

FIELDS = {
    b'FrameTrace': ['dt_us', 'draws', 'dispatches', 'faults', 'faults_gpu', 'dmas', 'cpu_gpu_us', 'submits'],
    b'FrameTrace-draw': ['bda_us', 'bda_n', 'bda_scan', 'bda_skip', 'bda_bskip', 'buf_new', 'buf_new_us',
                         'bufepoch', 'prot_calls', 'prot_pages', 'prot_gpu', 'prot_gpu_pages', 'img_new',
                         'img_free', 'img_up', 'sync_ups', 'ob_n', 'bb_n'],
    b'FrameTrace-x': ['bda_hit', 'bda_rng', 'bda_rng_e', 'bda_drng', 'pb2_pass', 'pb2_sync', 'pb2_up',
                      'pb2_reg', 'fbp_n', 'buflru_n', 'fw_n', 'tex_inval', 'up_tmp_n', 'stg_inbig_n',
                      'bc_ok', 'a_mut_us', 'bfast_miss', 'sync_noop', 'pb_refault', 'pb_inval_flush'],
}
KV = re.compile(rb'(\w+)=(\d+)')
WAITSUB = re.compile(rb'([\w-]+)=(\d+)/(\d+)')


def parse(path):
    frames = {}
    with open(path, 'rb') as f:
        for line in f:
            if not line.startswith(b'FrameTrace'):
                continue
            head, _, rest = line.partition(b':')
            if head in FIELDS:
                kv = dict(KV.findall(rest))
                if b'n' not in kv:
                    continue
                n = int(kv[b'n'])
                d = frames.setdefault(n, {})
                for k in FIELDS[head]:
                    v = kv.get(k.encode())
                    if v is not None:
                        d[k] = int(v)
            elif head in (b'FrameTrace-wait', b'FrameTrace-submit'):
                # no n= on these lines: attach to the last main frame seen
                pass
    return frames


def parse_unmap(path):
    """unmap waits/submits per FrameTrace frame (the wait/submit lines follow their frame's main line)."""
    out = {}
    cur = None
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace: n='):
                m = re.match(rb'FrameTrace: n=(\d+)', line)
                cur = int(m.group(1))
            elif cur is not None and (line.startswith(b'FrameTrace-wait:') or line.startswith(b'FrameTrace-submit:')):
                kind = 'w' if line.startswith(b'FrameTrace-wait:') else 's'
                for name, us, cnt in WAITSUB.findall(line):
                    if name == b'unmap':
                        out.setdefault(cur, {})['unmap_' + kind] = int(cnt)
    return out


def med(vals):
    return st.median(vals) if vals else float('nan')


def mean(vals):
    return sum(vals) / len(vals) if vals else float('nan')


def summarize(frames, lo, hi, cls=None):
    sel = [d for n, d in frames.items() if lo <= n <= hi and (cls is None or cls(d))]
    keys = sorted({k for d in sel for k in d})
    res = {'frames': len(sel)}
    for k in keys:
        vals = [d[k] for d in sel if k in d]
        res[k] = (mean(vals), med(vals))
    # derived: visits per scanning call
    vpc = []
    for d in sel:
        calls = d.get('bda_n', 0) - d.get('bda_hit', 0)
        if calls > 0 and 'bda_scan' in d:
            vpc.append((d['bda_scan'] + d.get('bda_skip', 0)) / calls)
    res['visits_per_scanning_call'] = (mean(vpc), med(vpc))
    spc = []
    for d in sel:
        calls = d.get('bda_n', 0) - d.get('bda_hit', 0)
        if calls > 0 and 'bda_scan' in d:
            spc.append(d['bda_scan'] / calls)
    res['scans_per_scanning_call'] = (mean(spc), med(spc))
    return res


def main():
    for path in sys.argv[1:]:
        frames = parse(path)
        um = parse_unmap(path)
        for n, d in um.items():
            if n in frames:
                frames[n].update(d)
        print('=' * 100)
        print(path, 'frames', len(frames))
        for lo, hi, label, cls in [
            (300, 1799, 'pre 300-1799 all', None),
            (2100, 10 ** 9, 'win >=2100 all', None),
            (300, 10 ** 9, '>=300 OLD-level frames (bda_scan>=500)', lambda d: d.get('bda_scan', 0) >= 500),
            (300, 10 ** 9, '>=300 NEW-level frames (bda_scan<200)', lambda d: d.get('bda_scan', 0) < 200),
        ]:
            r = summarize(frames, lo, hi, cls)
            print('--', label, 'frames', r.pop('frames'))
            print('   ' + '  '.join('%s=%.2f/%.1f' % (k, v[0], v[1]) for k, v in sorted(r.items())))
        # transitions: first frame >= 100 at OLD level, and every OLD<->NEW switch of a 5-frame median
        ns = sorted(frames)
        lvl = {}
        for i, n in enumerate(ns):
            w = [frames[m].get('bda_scan', 0) for m in ns[max(0, i - 2):i + 3]]
            lvl[n] = 'O' if med(w) >= 500 else ('N' if med(w) < 200 else '?')
        prev = None
        switches = []
        for n in ns:
            if lvl[n] in 'ON' and lvl[n] != prev:
                switches.append((n, lvl[n]))
                prev = lvl[n]
        print('   switches (5-frame median):', switches[:40], '...' if len(switches) > 40 else '')
        for n0, s in switches[:6]:
            print('   around frame', n0, '->', s)
            for n in range(n0 - 4, n0 + 5):
                d = frames.get(n)
                if d:
                    print('     n=%d scan=%s skip=%s bda_n=%s hit=%s rng=%s rng_e=%s drng=%s pb2_sync=%s buf_new=%s faults=%s draws=%s unmap_w=%s unmap_s=%s fbp=%s' % (
                        n, d.get('bda_scan'), d.get('bda_skip'), d.get('bda_n'), d.get('bda_hit'), d.get('bda_rng'),
                        d.get('bda_rng_e'), d.get('bda_drng'), d.get('pb2_sync'), d.get('buf_new'), d.get('faults'),
                        d.get('draws'), d.get('unmap_w'), d.get('unmap_s'), d.get('fbp_n')))


if __name__ == '__main__':
    main()
