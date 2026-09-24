# Recount of vds111b (GO terms, D1-D5), obs111 (P1-P5 inputs) and vid111 (check111 numbers) - audit 111.
import sys, pickle, json, re
sys.path.insert(0, 'C:/kyty/s111/audit111')
from abba import load

MARK = (b'DaSlotVerify: MISMATCH', b'DrawAheadVerify: MISMATCH', b'--- Error ---', b'--- Fatal Error ---',
        b'--- std::terminate ---', b'--- abort() ---', b'GpuHangAbort', b'ErrorDeviceLost', b'AsyncPipelines: skipped draw',
        b'GpuClockPin:', b'BvhLoopCapTrip', b'CsStall:', b'GpuCheckpoint', b'Unhandled exception')


def stdout_marks(path):
    c = {}
    with open(path, 'rb') as f:
        for raw in f:
            for m in MARK:
                if m in raw: c[m.decode()] = c.get(m.decode(), 0) + 1
    return c


def totals(P, keys, first=0):
    t = {k: 0 for k in keys}; rows = 0
    for n, r in P['rows'].items():
        if n < first: continue
        if 'da_q_free' not in r and 'cspfree_hit' not in r: continue
        rows += 1
        for k in keys: t[k] += r.get(k, 0)
    return t, rows


K = ('da_slot_bad', 'da_chk_ok', 'da_chk_bad', 'da_q_free', 'da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn',
     'cspfree_hit', 'cspfree_bad', 'cs_sync_new', 'cs_sync_wait', 'da_hit')
for tag in ('vds111', 'vds111b'):
    try:
        P = load(tag)
    except Exception:
        continue
    t, rows = totals(P, K)
    print('==', tag, 'rows with x-line', rows, 'log markers', {k.decode(): v for k, v in P['counts'].items() if v})
    print('   totals', t)
    print('   per flip', {k: round(v / rows, 3) for k, v in t.items()})
    print('   stdout markers', stdout_marks('C:/kyty/s111/stdout_%s.txt' % tag))
    print('   Gate lines', [g.decode() for g in P['gatelines']])
    bad = t['da_slot_bad'] + t['da_chk_bad'] + P['counts'][b'DaSlotVerify: MISMATCH'] + P['counts'][b'DrawAheadVerify: MISMATCH']
    print('   BAD', bad, 'D1', bad == 0, 'D2', 800 <= t['da_q_free'] / rows <= 1400, 'D3', t['da_guard_busy'] / rows <= 5,
          'D4', t['da_q_taking'] / rows <= 5, 'D5', t['da_hint_torn'] == 0, ' checks per hit', t['da_chk_ok'] / max(1, t['da_hit']))

# obs111
P = load('obs111')
rows = [r for n, r in P['rows'].items() if n >= 2100 and 'pl_cont_n' in r]
s = lambda k: sum(r.get(k, 0) for r in rows) / len(rows)
wall = s('pl_cont_wall_ns') / 1000
print('== obs111 rows', len(rows), 'contended wall us/flip %.2f' % wall, 'h1 %.2f h2 %.2f h0 %.2f h3 %.2f' % (
    s('pl_cont_h1_ns') / 1000, s('pl_cont_h2_ns') / 1000, s('pl_cont_h0_ns') / 1000, s('pl_cont_h3_ns') / 1000),
      'acq %.2f' % s('pl_cont_n'), 'wq hold %.2f us/flip n %.1f -> %.3f us/call' % (
          s('pl_wq_hold_ns') / 1000, s('pl_wq_hold_n'), s('pl_wq_hold_ns') / max(1, s('pl_wq_hold_n')) / 1000),
      'wp hold %.2f' % (s('pl_wp_hold_ns') / 1000), 'spin share %.3f' % (s('pl_cont_cpu_ns') / max(1, s('pl_cont_wall_ns'))),
      'tag1 share %.4f' % (s('pl_cont_h1_ns') / max(1, s('pl_cont_wall_ns'))))
print('   stdout markers', stdout_marks('C:/kyty/s111/stdout_obs111.txt'), 'log', {k.decode(): v for k, v in P['counts'].items() if v})

# vid111 (check111 numbers): scene rows after the stable frame
meta = json.load(open('C:/kyty/s111/vid111.json'))
P = load('vid111')
print('== vid111 json keys', sorted(meta.keys()))
for k in ('stable_frame', 'stable', 'attempts', 'rec', 'env'):
    if k in meta: print('  ', k, meta[k] if k != 'env' else {kk: vv for kk, vv in meta[k].items() if kk.startswith('KYTY')})
for first in (0, 280, 300, 2100):
    rs = [r for n, r in P['rows'].items() if n > first and 'cspfree_hit' in r]
    if not rs: continue
    tt = {k: sum(r.get(k, 0) for r in rs) for k in ('cspfree_hit', 'cspfree_bad', 'da_q_free', 'da_slot_bad', 'cs_sync_new', 'cs_sync_wait')}
    print('   rows n>%d: %d' % (first, len(rs)), {k: (v, round(v / len(rs), 3)) for k, v in tt.items()})
print('   stdout markers', stdout_marks('C:/kyty/s111/stdout_vid111.txt'), 'log', {k.decode(): v for k, v in P['counts'].items() if v})
print('   gate lines', P['gatelines'])
idx = open('C:/kyty/s111/rec_vid111.mp4.idx', 'rb').read().count(b'\n')
print('   idx lines', idx)
print('   glitch report', open('C:/kyty/s111/vid111_glitch.txt').read().strip())
P = load('vss111')
print('== vss111 log', {k.decode(): v for k, v in P['counts'].items() if v}, 'stdout', stdout_marks('C:/kyty/s111/stdout_vss111.txt'))
print('   glitch report', open('C:/kyty/s111/vss111_glitch.txt').read().strip())
