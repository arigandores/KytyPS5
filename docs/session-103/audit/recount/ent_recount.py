# Independent recount of the session-103 BVH loop-cap entry series. Auditor's own code (no scorer import).
import json, os, re, glob, hashlib, sys

ROOT = 'C:/kyty/s103'
OUTD = 'C:/kyty/s103/audit103/recount'
# sealed marker set (pred/01 s3: run_safety99.failure_marker) plus a broader "suspicious" set, reported separately
SEALED = [b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
          b'std::terminate', b'abort()', b'fatal', b'unhandled exception']
BROAD = [b'--- error ---', b'device lost', b'devicelost', b'vk_error_device', b'access violation', b'tdr',
         b'gpuhang', b'hung', b'nvlddmkm']
re_dt = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
re_xn = re.compile(rb'^FrameTrace-x: n=(\d+)')
re_trip = re.compile(rb' bl_trip=(\d+)')
re_near = re.compile(rb' bl_near=(\d+)')
re_cap = re.compile(rb'^BvhLoopCapTrip: trips=\+(\d+) total=(\d+) near=\+(\d+) near_total=(\d+)')


def scan(tag):
    r = dict(tag=tag, armed=0, armed_lines=[], sealed=[], broad=[], ft=0, ftx=0, ftx_with_bl=0, trip_sum=0, near_sum=0,
             cap_lines=0, cap_trip_total=0, cap_near_total=0, cap_inc_trip=0, cap_inc_near=0, max_dt=0, max_dt_n=None,
             last_ft_line=0, last_ftx_line=0, last_cap_line=0, ft_ns=[], ftx_ns=[], trip_frames=[], near_frames=[])
    p = '%s/log_%s.txt' % (ROOT, tag)
    with open(p, 'rb') as f:
        for ln_no, ln in enumerate(f, 1):
            if ln.startswith(b'FrameTrace: '):
                m = re_dt.match(ln)
                if m:
                    r['ft'] += 1; n = int(m.group(1)); dt = int(m.group(2)); r['ft_ns'].append(n)
                    if dt > r['max_dt']: r['max_dt'] = dt; r['max_dt_n'] = n
                    r['last_ft_line'] = ln_no
                continue
            if ln.startswith(b'FrameTrace-x: '):
                r['ftx'] += 1; r['last_ftx_line'] = ln_no
                m = re_xn.match(ln); n = int(m.group(1)) if m else None; r['ftx_ns'].append(n)
                a = re_trip.search(ln); b = re_near.search(ln)
                if a or b: r['ftx_with_bl'] += 1
                if a and int(a.group(1)): r['trip_sum'] += int(a.group(1)); r['trip_frames'].append((n, int(a.group(1))))
                if b and int(b.group(1)): r['near_sum'] += int(b.group(1)); r['near_frames'].append((n, int(b.group(1))))
                continue
            if ln.startswith(b'BvhLoopCap: '):
                r['armed_lines'].append(ln.strip()[:120].decode('latin1'))
                if ln.startswith(b"BvhLoopCap: cap=65536 token=''"): r['armed'] += 1
            m = re_cap.match(ln)
            if m:
                r['cap_lines'] += 1; r['last_cap_line'] = ln_no
                r['cap_inc_trip'] += int(m.group(1)); r['cap_inc_near'] += int(m.group(3))
                r['cap_trip_total'] = int(m.group(2)); r['cap_near_total'] = int(m.group(4))
            low = ln.lower()
            for t in SEALED:
                if t in low:
                    r['sealed'].append((ln_no, ln.strip()[:160].decode('latin1'))); break
            else:
                for t in BROAD:
                    if t in low and len(r['broad']) < 6:
                        r['broad'].append((ln_no, ln.strip()[:160].decode('latin1'))); break
    # stdout of the run, if any (hang reports may go to stdout)
    r['stdout_sealed'] = []
    for sp in glob.glob('%s/stdout_%s.txt' % (ROOT, tag)):
        with open(sp, 'rb') as f:
            for ln_no, ln in enumerate(f, 1):
                low = ln.lower()
                if any(t in low for t in SEALED):
                    r['stdout_sealed'].append((ln_no, ln.strip()[:160].decode('latin1')))
    doc = json.load(open('%s/%s.json' % (ROOT, tag), encoding='utf-8'))
    r['binary'] = doc.get('binary_sha256')
    r['env'] = doc.get('env')
    r['attempts'] = [(a.get('label'), a.get('outcome'), a.get('hold_exit'), a.get('hold_s')) for a in doc.get('attempts') or []]
    r['started'] = doc.get('started'); r['finished'] = doc.get('finished')
    r['prereg_sha'] = (doc.get('prereg') or {}).get('sha256')
    return r


def main():
    tags = ['ent103_%02d' % i for i in range(1, 68)]
    extra = sorted(os.path.basename(p)[:-5] for p in glob.glob(ROOT + '/ent103_*.json'))
    lines = []
    def P(*a):
        s = ' '.join(str(x) for x in a); print(s); lines.append(s)
    P('entry json files present:', extra)
    res = [scan(t) for t in tags]
    warm = scan('ent103_warm')
    envs = set(json.dumps(r['env'], sort_keys=True) for r in res)
    P('distinct env dicts across 67:', len(envs)); P(' env:', list(envs)[0] if len(envs) == 1 else envs)
    P('binaries:', sorted(set(r['binary'] for r in res)), 'warm:', warm['binary'])
    P('prereg sha seen by runs:', sorted(set(r['prereg_sha'] for r in res)))
    P('pred/01 sha now:', hashlib.sha256(open(ROOT + '/pred/01_bvh_cap_series.md', 'rb').read()).hexdigest())
    P('%-10s %5s %4s %-28s %9s %9s %9s %9s %6s %6s %6s %8s %s' % ('tag', 'armed', 'hang', 'attempt(outcome,hold_exit,hold_s)',
      'ftx_trip', 'log_trip', 'ftx_near', 'log_near', 'ft', 'ftx', 'capln', 'max_dt_s', 'notes'))
    for r in res + [warm]:
        notes = []
        if r['sealed']: notes.append('SEALED:%s' % r['sealed'][:2])
        if r['stdout_sealed']: notes.append('STDOUT:%s' % r['stdout_sealed'][:2])
        if r['broad']: notes.append('broad:%s' % r['broad'][:2])
        if r['ft'] != r['ftx']: notes.append('ft!=ftx')
        if r['trip_sum'] != r['cap_trip_total'] or r['near_sum'] != r['cap_near_total']: notes.append('FTX-vs-LOG MISMATCH')
        if r['cap_lines'] and r['last_cap_line'] > r['last_ftx_line']: notes.append('cap line after last FTX')
        if r['cap_inc_trip'] != r['cap_trip_total'] or r['cap_inc_near'] != r['cap_near_total']: notes.append('increments!=total')
        if r['armed'] != 1: notes.append('armed_lines=%s' % r['armed_lines'])
        P('%-10s %5d %4s %-28s %9d %9d %9d %9d %6d %6d %6d %8.3f %s' % (
            r['tag'], r['armed'], 'Y' if r['sealed'] or r['stdout_sealed'] else '-', r['attempts'], r['trip_sum'], r['cap_trip_total'],
            r['near_sum'], r['cap_near_total'], r['ft'], r['ftx'], r['cap_lines'], r['max_dt'] / 1e6, '; '.join(notes)))
    # verdict items (sealed pred/01 s4)
    tr = lambda r: max(r['trip_sum'], r['cap_trip_total'])
    nr = lambda r: max(r['near_sum'], r['cap_near_total'])
    hang = [r['tag'] for r in res if any(b'gpuwaitslow' not in x[1].lower().encode() for x in r['sealed'] + r['stdout_sealed'])]
    slow_only = [r['tag'] for r in res if (r['sealed'] or r['stdout_sealed']) and r['tag'] not in hang]
    notok = [r['tag'] for r in res if not (r['attempts'] and r['attempts'][-1][1] == 'ok' and r['attempts'][-1][2] is None)]
    A1 = all(r['armed'] >= 1 for r in res)
    A2 = not hang and not notok
    A3 = all(nr(r) == 0 for r in res)
    trips = [(r['tag'], tr(r)) for r in res if tr(r) > 0]
    A4 = len(trips) <= 15
    worst = max(r['max_dt'] for r in res)
    worst_tag = [r['tag'] for r in res if r['max_dt'] == worst]
    A5 = worst < 30_000_000
    P('A1 armed', A1, '| A2 no hang', A2, 'hangs', hang, 'slow-only', slow_only, 'not ok/hold', notok,
      '| A3 margin', A3, 'near entries', [(r['tag'], nr(r)) for r in res if nr(r)],
      '| A4 trips', A4, len(trips), trips, 'total', sum(t for _, t in trips),
      '| A5 worst dt %.6f s' % (worst / 1e6), worst_tag, A5)
    P('VERDICT', 'ACCEPTED' if all([A1, A2, A3, A4, A5]) else 'NOT ACCEPTED')
    # trip frame detail
    for r in res:
        if r['trip_frames'] or r['near_frames'] or r['cap_lines']:
            P(' detail', r['tag'], 'trip frames', r['trip_frames'], 'near frames', r['near_frames'],
              'ft n range', (min(r['ft_ns']), max(r['ft_ns'])), 'ftx n range', (min(n for n in r['ftx_ns'] if n is not None), max(n for n in r['ftx_ns'] if n is not None)),
              'last lines ft/ftx/cap', r['last_ft_line'], r['last_ftx_line'], r['last_cap_line'])
    P('warm-up:', warm['tag'], 'attempts', warm['attempts'], 'armed', warm['armed'], 'trips', tr(warm), 'near', nr(warm),
      'sealed markers', warm['sealed'][:3], warm['stdout_sealed'][:3], 'max_dt %.3f' % (warm['max_dt'] / 1e6), 'started', warm['started'],
      'first counted started', res[0]['started'])
    # chronological order
    order_ok = all(res[i]['started'] <= res[i + 1]['started'] for i in range(len(res) - 1))
    P('counted entries in chronological order:', order_ok, 'first', res[0]['started'], 'last', res[-1]['finished'])
    open(OUTD + '/ent_recount.out.txt', 'w').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
