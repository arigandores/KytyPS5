"""Offline fixtures of pm4c140.py (the scorer of the PM4 per-opcode census of session 140; ROADMAP s122 items 210 (e)(3)-(6),
212 (b)-(k), 213 (b)-(d); design140.md section 11 FX1-FX26 and review140 RC8): one case per edge of every IF (IF0 per check,
IF1-IF11 per field), per DEBT edge (4000 / 3999 in b, c, both, a), per outcome edge (400 / 325, the mean and the minimum),
per deduction A_g (MM_out, DRAW_out, DISP_out, EOP_adj, WAITFLIP_adj, FLIP_low in the form of item 212 (b)) and its upper
form U_g, c_k (min of two candidates, the branch "E whole", the band 3 / 100), the window (n 1799 / 1800, the last full row,
NEW 300 / 301, the pm4 line out of place), the truncation +0.5, SPREAD (by bound) against SPREAD (item 213 (b)), LEVEL-INFLATED
keeping and removing NAMED (item 213 (g)), c-SENSITIVE by break-even (item 213 (v)), the labels (RC3, item 212 (g)), the
opcode table columns (RC6), the masked forms (RC7), the RC3 / RC4 / RC9 / RC10 lines, the pre-seal check and the ASCII
output in a strict cp1250 stdout (item 175 (v), process 3).  Synthetic logs only; the map is checked against opmap140.tsv.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last
statement is `sys.exit(0 if ok else 1)`; no subprocess (main() is called in-process).
The first output line names this suite and the scorer under test by sha256 (item 150 (v)); the output ends with ALL OK.
    python C:/kyty/s140/test_pm4c140.py [<pm4c140 under test>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import re
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'pm4c140.py')
print('suite test_pm4c140.py sha256 %s target pm4c140.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('pm4c140_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BUILD = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
BASE_GATES = 'C:/kyty/s140/gates_base.txt'
OPMAP = 'C:/kyty/s140/step0/opmap140.tsv'
OPMAP_SHA = '0492b2d0271c3f092072b861072db0fb47b062f0995797c6493c9e095d72a145'
GATES_TEXT = ' '.join(Path(BASE_GATES).read_text(encoding='utf-8').split())
KN = ['mutsite=1', 'plkstat=1', 'bindlap=1', 'pathlap=1', 'rbcen=1']
TR = {'pm4c140a': '0', 'pm4c140b': '1', 'pm4c140c': '1', 'pm4c140d': '0', 'pm4s140': '1'}
BASE = Path('C:/kyty/s140/fx_pm4c140')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
N = [0]


def case(name, cond):
    N[0] += 1
    if not cond:
        print('FAIL ' + name)
    return bool(cond)


def close(a, b, tol=1e-6):
    return a is not None and b is not None and not (isinstance(a, float) and math.isnan(a)) and abs(a - b) <= tol


# --- the synthetic census ---------------------------------------------------------------------------------------------
# One row of a run with 1 (per frame; U us / C packets).  c_k = 1000 * 19.5 / 1000 = 19.5 ns (op2a, the only E site).
ON_SITES = {'op2a': (19, 1000), 'op69': (200, 2000), 'op27': (2800, 5000), 'op15': (400, 268), 'nop18': (100, 20),
            'op37': (30, 50), 'op3c': (20, 10), 'nop06': (50, 1), 'op12': (20, 100), 'nop17': (60, 1)}
NONOP_SITES = {'gc': (10, 5), 'prefetch': (28, 5)}
X_FIELDS = dict(bda_scan=50, pl_cmd_ns=600000, pl_gc_ns=60000, pl_sub_ns=55000, pl_sub_n=20, pl_eop_ns=40000, pl_eop_n=10,
                pl_bar_ns=12000, pl_bar_n=5, pl_pref_ns=1000, a_hold_us=2800, a_wait_us=150, a_hold_n=5268, mh_disp_us=300,
                mh_pres_us=40, mh_pres_wait_us=20)
M_FIELDS = dict(dt_us=34000, submits=40, draws=5000, dispatches=268)
SUB_SITES = {'release-mem-irq': (14, 10), 'release-mem-data1': (7, 9), 'flip': (0, 1)}
C_K = 19.5
NAMED_NS = ('pl_cmd_ns', 'pl_gc_ns', 'pl_sub_ns', 'pl_eop_ns', 'pl_bar_ns', 'pl_pref_ns')


def val(v, i):
    """A per-row value: an int, or a list cycled over the row index."""
    return v[i % len(v)] if isinstance(v, list) else v


def row_lines(n, i, on, sites, x_over, m_over, g_ns, fpk, d0_off, drop_pm4, cmd_n, pm4_line_first, sub_sites):
    ss = dict((k, (val(u, i), val(c, i))) for k, (u, c) in sites.items())
    x = dict(X_FIELDS)
    for k, v in x_over.items():
        if v is None:
            x.pop(k, None)
        else:
            x[k] = val(v, i)
    m = dict(M_FIELDS)
    m.update(dict((k, val(v, i)) for k, v in m_over.items()))
    nonop = dict(NONOP_SITES)
    ops_ = dict((k, v) for k, v in ss.items() if k not in ('gc', 'prefetch', 'stream-prefetch'))
    for k in ('gc', 'prefetch', 'stream-prefetch'):
        if k in ss:
            nonop[k] = ss[k]
    csum = sum(c for _, c in ops_.values())
    x['pl_cmd_n'] = cmd_n if cmd_n is not None else csum + fpk
    named = sum(x.get(k, 0) for k in NAMED_NS)
    named_on = sum(x.get(k, 0) for k in ('pl_cmd_ns', 'pl_gc_ns', 'pl_sub_ns', 'pl_pref_ns'))   # eop, bar are inside sites
    pref_u = nonop.get('prefetch', (0, 0))[0]
    stream_u = nonop.get('stream-prefetch', (0, 0))[0]
    if on:
        s_ns = sum(1000 * u + 500 for u, _ in ops_.values())
        pre_ns = sum(1000 * nonop[k][0] + 500 for k in ('prefetch', 'stream-prefetch') if k in nonop)
        proc = s_ns + named_on + pre_ns + int(round(val(g_ns, i) * x['pl_cmd_n']))
    else:
        proc = int(round(1000 * (val(d0_off, i) + x.get('a_hold_us', 0) + x.get('a_wait_us', 0) + pref_u + stream_u))) + named
    x['pl_proc_ns'] = proc
    for k, v in x_over.items():
        if v is None:
            x.pop(k, None)
        elif k in ('pl_proc_ns', 'pl_cmd_n'):
            x[k] = val(v, i)
    allsites = dict(nonop)
    allsites.update(ops_)
    fmt = lambda d: ' '.join('%s=%d' % (k, v) for k, v in d.items())
    pm4 = 'FrameTrace-pm4: ' + ' '.join('%s=%d/%d' % (k, u, c) for k, (u, c) in allsites.items())
    out = []
    if pm4_line_first:
        out.append(pm4)
    out.append('FrameTrace: n=%d %s' % (n, fmt(m)))
    out.append('FrameTrace-draw: n=%d logs=1' % n)
    out.append('FrameTrace-x: n=%d %s' % (n, fmt(x)))
    out.append('FrameTrace-wait: other=100/2')
    out.append('FrameTrace-submit: ' + ' '.join('%s=%d/%d' % (k, u, c) for k, (u, c) in sub_sites.items()))
    if not drop_pm4 and not pm4_line_first:
        out.append(pm4)
    return out


def write_run(root, tag, rows=200, sites=None, x_over=None, m_over=None, g_ns=50, fpk=100, d0_off=2000.0, start=1800,
              pre_rows=0, gates=None, arms=0, env_over=None, meta_over=None, extra_lines=(), row_hook=None, cmd_n=None,
              no_json=False, no_log=False, prereg=None):
    """A run: `rows` window rows n = start .. start+rows-1 plus one last full row (excluded), `pre_rows` rows before
    start.  row_hook(i, n) -> dict of per-row overrides (sites / x_over / drop_pm4 / pm4_line_first / skip)."""
    on = TR[tag] == '1'
    base_sites = dict(ON_SITES) if on else {}
    if sites is not None:
        base_sites = dict(sites)
    lines = ['Kyty synthetic log %s' % tag]
    for k in (KN if gates is None else gates):
        lines.append('Gate: %s frame=1' % k)
    for _ in range(arms):
        lines.append('GateArm: arm=0 arms=2 block=0 frame=1800 period=90 abba=1 text=bindlean=0')
    lines += list(extra_lines)
    idx = 0
    for n in list(range(start - pre_rows, start)) + list(range(start, start + rows + 1)):
        h = row_hook(idx, n) if row_hook else {}
        if h.get('skip'):
            idx += 1
            continue
        s = dict(base_sites)
        s.update(h.get('sites', {}))
        for k in h.get('del_sites', ()):
            s.pop(k, None)
        xo = dict(x_over or {})
        xo.update(h.get('x_over', {}))
        rl = row_lines(n, idx, on, s, xo, dict(m_over or {}, **h.get('m_over', {})), g_ns, fpk, d0_off,
                       h.get('drop_pm4', False), cmd_n, h.get('pm4_line_first', False), h.get('sub', SUB_SITES))
        drop = tuple({'d': 'FrameTrace-draw:', 'x': 'FrameTrace-x:'}[k] for k in h.get('drop_lines', ()))
        lines += [l for l in rl if not (drop and l.startswith(drop))]
        lines += h.get('after', [])
        idx += 1
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    if not no_log:
        (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('ascii'))
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_PM4_TRACE': TR[tag],
           'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden'}
    for k, v in (env_over or {}).items():
        if v is None:
            env.pop(k, None)
        else:
            env[k] = v
    meta = dict(tag=tag, binary_sha256=BUILD, env=env, gates=GATES_TEXT, attempts=[dict(outcome='ok', hold_s=300.0)])
    if prereg is not None:
        meta['prereg'] = prereg
    meta.update(meta_over or {})
    if not no_json:
        (root / ('%s.json' % tag)).write_text(json.dumps(meta), encoding='utf-8')


CNT = [0]


def census(runs=None, **common):
    """Four runs into a fresh directory; runs = {tag: kwargs}; returns the directory."""
    CNT[0] += 1
    root = BASE / ('c%03d' % CNT[0])
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    shutil.copyfile(BASE_GATES, root / 'gates_base.txt')
    for tag in S.SEQ:
        kw = dict(common)
        kw.update((runs or {}).get(tag, {}))
        write_run(root, tag, **kw)
    return root


def run_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.main(argv)
    return rc, buf.getvalue()


def decide(root):
    out, calcs = S.decide(str(root))
    return out


def with_sites(tag_sites):
    return dict((t, dict(sites=s)) for t, s in tag_sites.items())


def on_sites(**over):
    s = dict(ON_SITES)
    for k, v in over.items():
        if v is None:
            s.pop(k, None)
        else:
            s[k] = v
    return s


ok = True
SMALL = 200
REAL_MIN = S.MIN_NEW_ROWS
S.MIN_NEW_ROWS = SMALL   # every case below uses 200 window rows; the real 4000 is restored for the DEBT edges

# --- 0. constants and the map ------------------------------------------------------------------------------------------------
ok &= case('k1 the constants of items 210 (e), 212, 213 as sealed', S.N_MIN == 1800 and S.BDA_NEW == 300
           and S.NAMED_MEAN == 400.0 and S.NAMED_EACH == 325.0 and S.C_LO == 3.0 and S.C_HI == 100.0 and S.C_HIGH == 40.0
           and S.C_CMP == 22.9 and S.E_MIN == 1000.0 and S.TRUNC == 0.5 and S.G_HI == 250.0 and S.G_LO_PAD == 0.5
           and S.F_LO == 0.005 and S.F_HI == 0.5 and S.M_MIN == -5.0 and S.H_TOL == 0.005 and S.P1_MIN == 0.99
           and S.IF10_MAX == 0.01 and S.BLOCK == 90 and S.MM_PRICE_NS == 20.0)
ok &= case('k2 build, base, tags, trace per tag, the knob set of arm 0 of kp137, the IF11 fields of item 212 (b)',
           S.BUILD_SHA == BUILD and S.BASE_SHA == '573ae9d2f24944c4fa92a14070645e3fe5b21bd6ee3365502e6ba768c0087fbc'
           and S.SEQ == ('pm4c140a', 'pm4c140b', 'pm4c140c', 'pm4c140d') and S.SMOKE == 'pm4s140' and S.TRACE == TR
           and S.ON == ('pm4c140b', 'pm4c140c') and S.OFF == ('pm4c140a', 'pm4c140d') and list(S.KNOBS) == KN
           and S.IF11_FIELDS == ('pl_proc_ns', 'pl_cmd_ns', 'pl_cmd_n', 'a_hold_us', 'a_wait_us', 'a_hold_n', 'mh_disp_us',
                                 'mh_pres_us', 'mh_pres_wait_us') and S.ROOT == 'C:/kyty/s140'
           and S.PRED_NAME == 'pred/01_pm4c140.md' and S.SEALS_NAME == 'SEALS140.txt' and S.CHAIN_NAME == 'go140a.sh'
           and S.FATAL == b'AsyncPipelines: skipped draw')
ok &= case('k3 the real gate base has the sealed sha', hashlib.sha256(Path(BASE_GATES).read_bytes()).hexdigest() == S.BASE_SHA)
tsv = Path(OPMAP).read_bytes()
tmap = {}
for ln in tsv.decode('utf-8').splitlines():
    if not ln or ln.startswith('#') or ln.startswith('name\t'):
        continue
    c = ln.split('\t')
    if c[4] != 'NONOP':
        tmap[c[0]] = (c[4], c[5], int(c[6]))
ok &= case('k4 MAP = opmap140.tsv (sha 0492b2d0...) name by name: class, group, E; 53 opcode names + 3 non-opcode',
           hashlib.sha256(tsv).hexdigest() == OPMAP_SHA and tmap == S.MAP and len(S.MAP) == 53
           and S.NONOP == ('gc', 'prefetch', 'stream-prefetch'))
ok &= case('k5 E = the 10 sites of the map (item 212 (d)); S1 and the multi-draw pair of P2; the groups and candidates of '
           'item 212 (g)', sorted(k for k, v in S.MAP.items() if v[2] == 1) == sorted(
               ['op11', 'op13', 'op26', 'op2a', 'op2f', 'op42', 'op58', 'op84', 'op85', 'nop14'])
           and S.S1 == ('op27', 'op35', 'op3a', 'op2d', 'op24', 'op25', 'op15', 'op16') and S.MULTI == ('op2c', 'op38')
           and S.GROUPS == ('REG', 'DRAWMM', 'DISPMM', 'EOP', 'MEM', 'SYNC', 'WAITFLIP', 'STATE', 'FLIP', 'NEST')
           and S.CAND_ORDER == ('REG', 'MM_out', 'DRAW_out', 'DISP_out', 'EOP_adj', 'MEM', 'SYNC', 'WAITFLIP_adj', 'STATE',
                                'FLIP_low')
           and dict((k, v[0]) for k, v in S.CANDS.items()) == {
               'REG': ('REG',), 'MM_out': ('DRAWMM', 'DISPMM'), 'DRAW_out': ('DRAWMM',), 'DISP_out': ('DISPMM',),
               'EOP_adj': ('EOP',), 'MEM': ('MEM',), 'SYNC': ('SYNC',), 'WAITFLIP_adj': ('WAITFLIP',), 'STATE': ('STATE',),
               'FLIP_low': ('FLIP',)}
           and [k for k in S.CAND_ORDER if S.CANDS[k][1] == 'with arm-0 instrument'] == ['MM_out', 'DRAW_out', 'DISP_out']
           and [k for k in S.CAND_ORDER if S.CANDS[k][1] == 'wait class'] == ['SYNC', 'WAITFLIP_adj', 'FLIP_low'])

# --- 1. the parser and the window ----------------------------------------------------------------------------------------
ok &= case('FX23 the truncation correction: a site 5/1 -> raw* 5.5; an absent site 0', S.raw_star({'op69': (5, 1)}, 'op69') == 5.5
           and S.raw_star({}, 'op69') == 0.0 and S.count({'op69': (5, 1)}, 'op69') == 1)
R0 = BASE / 'w1'
write_run(R0, 'pm4c140b', rows=10, pre_rows=3)
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('FX26 n = 1799 out of the window, 1800 in; the last full row (n 1810) out; 10 rows', last == 1810
           and [r['n'] for r in w] == list(range(1800, 1810)) and len([r for r in p['rows'] if r['n'] == 1799]) == 1)


def hook_x(n0, x):
    return lambda i, n: dict(x_over=x) if n == n0 else {}


write_run(R0, 'pm4c140b', rows=10, row_hook=hook_x(1803, {'bda_scan': 301}))
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
write_run(R0, 'pm4c140c', rows=10, row_hook=hook_x(1803, {'bda_scan': 300}))
w2, _, _ = S.window(S.parse_log(str(R0 / 'log_pm4c140c.txt')))
write_run(R0, 'pm4c140d', rows=10, row_hook=hook_x(1803, {'bda_scan': None}))
w3, _, _ = S.window(S.parse_log(str(R0 / 'log_pm4c140d.txt')))
ok &= case('W1 NEW: bda_scan 300 in, 301 out, missing out (items 40 (e)(1), 212 (v))', len(w) == 9 and 1803 not in [r['n'] for r in w]
           and len(w2) == 10 and len(w3) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(pm4_line_first=True) if n == 1805 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('FX25 a FrameTrace-pm4: line before the FrameTrace: of its frame is not the line of that row (the row 1805 is not '
           'full; the line after the x of 1804 is taken, the second one is an orphan)',
           1805 not in [r['n'] for r in w] and 1805 in [r['n'] for r in rng] and p['orphans'] == 1 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_pm4=True, after=['FrameTrace: n=99999 dt_us=1',
                                                                                     'FrameTrace-pm4: op69=1/1'])
          if n == 1804 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W2 a pm4 line after the next FrameTrace: line does not belong to the row before it (orphan)',
           1804 not in [r['n'] for r in w] and p['orphans'] == 1)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(after=['FrameTrace: n=1806 dt_us=1']) if n == 1802 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W3 a duplicate n is dropped whole', 1806 not in [r['n'] for r in w] and p['dups'] == 1 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(after=['FrameTrace-x: n=1806 bda_scan=1']) if n == 1806 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W3b a duplicate FrameTrace-x: line of one n drops the row whole', 1806 not in [r['n'] for r in w] and p['dups'] == 1)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_lines=('x',)) if n == 1804 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W3c a frame without its FrameTrace-x: line: not full, its pm4 line is an orphan (the x line opens the place of '
           'the pm4 line, not the draw line)', 1804 not in [r['n'] for r in w] and p['orphans'] == 1 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_lines=('d',)) if n == 1804 else {})
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
ok &= case('W3d a frame without its FrameTrace-draw: line is not full', 1804 not in [r['n'] for r in w] and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_pm4=True) if n == 1810 else {})
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
ok &= case('W6 the last FULL row sets the end: the last frame without its pm4 line is not the last full row (1809 is, and '
           'is excluded)', last == 1809 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(skip=True) if n == 1810 else {})
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
ok &= case('W4 the last full row is excluded whatever its n (1809 here)', last == 1809 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, extra_lines=['AsyncPipelines: skipped draw x', 'GateArm: arm=1'])
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
ok &= case('W5 the fatal marker and GateArm: lines are counted; the Gate: lines are read in order',
           p['fatal'] == 1 and p['arms'] == 1 and p['gates'] == KN)

# --- 2. the base census: SPREAD, every candidate by its formula ---------------------------------------------------------------
R = census()
out = decide(R)
tb = out.get('table', {})
exp_lb = {
    'REG': 200.5 - C_K * 2.0,
    'MM_out': 2800.5 + 400.5 - C_K * 5.268 - (2800 + 150),
    'DRAW_out': 2800.5 - C_K * 5.0 - (2800 - 300 + 150),
    'DISP_out': 400.5 - C_K * 0.268 - (300 + 150),
    'EOP_adj': 100.5 - C_K * 0.02 - (40 + 12 + 55),
    'MEM': 30.5 - C_K * 0.05,
    'SYNC': 20.5 - C_K * 0.01,
    'WAITFLIP_adj': 50.5 - C_K * 0.001 - 55,
    'STATE': 19.5 + 20.5 - C_K * 1.1,
    'FLIP_low': 60.5 - C_K * 0.001 - (40 + 20),
}
exp_u = {
    'REG': 200.5 - 3 * 2.0, 'MM_out': 3201 - 3 * 5.268 - 2950, 'DRAW_out': 2800.5 - 3 * 5.0 - (2800 - 300),
    'DISP_out': 400.5 - 3 * 0.268 - 300, 'EOP_adj': 100.5 - 3 * 0.02 - (40 + 12), 'MEM': 30.5 - 3 * 0.05,
    'SYNC': 20.5 - 3 * 0.01, 'WAITFLIP_adj': 50.5 - 3 * 0.001, 'STATE': 40 - 3 * 1.1, 'FLIP_low': 60.5 - 3 * 0.001,
}
ok &= case('b0 the base census reads SPREAD (every level below 400, every U_g below the thresholds)',
           out['outcome'] == 'SPREAD' and out['named'] == [] and out['bound'] == [])
for cand in S.CAND_ORDER:
    t = tb.get(cand, {})
    ok &= case('A1 %s: L = sum raw* - c_k n / 1000 - A (item 212 (b), (g)) = %.4f in b and c' % (cand, exp_lb[cand]),
               close(t.get('Lb'), exp_lb[cand]) and close(t.get('Lc'), exp_lb[cand]) and close(t.get('mean'), exp_lb[cand]))
    ok &= case('A2 %s: U = the upper form (c 3 ns, minimal deduction; item 213 (b)) = %.4f' % (cand, exp_u[cand]),
               close(t.get('Ub'), exp_u[cand]) and close(t.get('Uc'), exp_u[cand]))
ok &= case('A3 n_g/frame beside the level (RC2): REG 2000, MM_out 5268, STATE 1100',
           close(tb['REG']['nb'], 2000) and close(tb['MM_out']['nc'], 5268) and close(tb['STATE']['nb'], 1100))
ok &= case('A4 L at 22.9 ns and at 0 beside (item 212 (d)): REG 200.5 - 45.8 and 200.5',
           close(tb['REG']['L229'], 200.5 - 45.8) and close(tb['REG']['L0'], 200.5))
ok &= case('A5 c_k of the base = 19.5 ns on op2a (1000/frame) and E whole (the E sum is 1000/frame)',
           close(out['runs']['pm4c140b']['c_k'], 19.5) and out['runs']['pm4c140b']['c_cands'] == [('op2a', 19.5), ('E', 19.5)])
ok &= case('A6 the break-even c* of REG (2000 packets/frame): mean 400 at 1000 (200.5 - 400)/2000 = -99.75; min 325 at '
           '1000 (200.5 - 325)/2000 = -62.25', close(tb['REG']['cstar_mean'], -99.75) and close(tb['REG']['cstar_min'], -62.25))
ok &= case('A7 the 2SE of a constant level is 0 by blocks of 90 rows (200 rows -> 2 blocks)', close(tb['REG']['se2b'], 0.0))
ok &= case('A6b the break-even of MM_out uses B = mean(sum raw* - A): (251 - 400) / 5.268 and (251 - 325) / 5.268',
           close(tb['MM_out']['cstar_mean'], 1000 * (251.0 - 400) / 5268) and close(tb['MM_out']['cstar_min'],
                                                                                   1000 * (251.0 - 325) / 5268))
S.MIN_NEW_ROWS = 180
o = decide(census(runs={t: dict(rows=180, sites=on_sites(op69=([300] * 90 + [310] * 91, 0))) for t in S.ON}))
S.MIN_NEW_ROWS = SMALL
ok &= case('A7b 2SE by blocks of 90: block means 300.5 and 310.5 -> SE 5.0 -> 2SE 10.0',
           close(o['table']['REG']['se2b'], 10.0) and close(o['table']['REG']['se2c'], 10.0))
o = decide(census(runs={'pm4c140b': dict(sites=on_sites(op69=([418, 419], 2000))),
                        'pm4c140c': dict(sites=on_sites(op69=([428, 429], 2000)))}))
ok &= case('A6c the break-even of the minimum is the smaller of b and c: min(1000 (419 - 325) / 2000, 1000 (429 - 325) / 2000) = 47',
           close(o['table']['REG']['cstar_min'], 47.0))
o = decide(census(runs={t: dict(sites=on_sites(op69=([349, 350], 2000))) for t in S.ON}))
ok &= case('A6d c-SENSITIVE by the minimum alone: REG raw 350 at 2000 packets - c*min 12.5 in (3, 19.5), c*mean < 0',
           o['sensitive'] == ['REG'] and close(o['table']['REG']['cstar_min'], 12.5) and o['table']['REG']['cstar_mean'] < 0)
rc, txt = run_main(['--all', '--dir', str(R), '--out', str(R / 'all.json')])
ok &= case('A8 --all: rc 0, VERDICT SPREAD, the RC9 identities text, the RC4 FLIP_low line, the RC10 line of each run, the RC3 '
           'marks of MM_out/DRAW_out/DISP_out/EOP_adj/WAITFLIP_adj, the price reference',
           rc == 0 and 'VERDICT SPREAD\n' in txt and 'gross - RC9' in txt and 'from the present thread (RC4)' in txt
           and all(('  %s (KYTY_PM4_TRACE=%s) pl_sub_n 20.00 submits 40.00 release-mem n 19.00' % (t, TR[t])) in txt
                   for t in S.SEQ)
           and all(('  %s: ' % c) in txt for c in ('MM_out', 'DRAW_out', 'DISP_out', 'EOP_adj', 'WAITFLIP_adj'))
           and 'pm4c140b 5268.0 holds/frame x 20 ns = 105.4 us/frame [I]' in txt
           and 'pm4c140b 35.0 spans/frame x 22.9 ns = 0.8 us/frame [I]' in txt
           and 'PRICE REFERENCE (item 210 (e)(5)(v)' in txt)
optab = [l for l in txt.splitlines() if re.match(r'^  (op|nop)[0-9a-f]{2} ', l)]
ok &= case('RC6 the opcode table: every op row carries class, group and per run raw*, n/frame, c_k n/1000, corrected; the '
           'values of op69', len(optab) == 10 and all(len(l.split('|')) == 3 and all(len(c.split()) == 4 for c in l.split('|')[1:])
                                                        for l in optab)
           and any(l.startswith('  op69   OUT    REG      | 200.5 2000.0 39.0 161.5 | 200.5 2000.0 39.0 161.5') for l in optab))
jd = json.loads((R / 'all.json').read_text(encoding='ascii'))
ok &= case('A9 the json: outcome, printed_delta yes, the table, the four runs masked', jd['outcome'] == 'SPREAD'
           and jd['printed_delta'] == 'yes' and 'REG' in jd['table'] and sorted(jd['runs']) == list(S.SEQ))
ok &= case('A10 the identities of the base: g 50 ns, F 100, M 251, H 0 (exact)', close(out['runs']['pm4c140b'].get('c_k'), 19.5)
           and 'g 50.00 ns/iteration (lower -6.93, upper 250)' in txt and 'F 100.0 /frame' in txt and 'M 251.0 us' in txt
           and 'H 0.00' in txt and out['sensitive'] == [])
ok &= case('A11 the nop00 comparator line and D0 of a and d', 'COMPARATOR nop00 (RC2 (b); reference, not a gate)' in txt
           and 'D0(pm4c140a) 2000.0 us/frame over 200 NEW rows' in txt and 'D0(pm4c140d) 2000.0' in txt)

# --- 3. the outcome edges (REG with C = 0: the level does not depend on c, U = L) -------------------------------------------
def reg_edge(ub, uc, **kw):
    return census(runs={'pm4c140b': dict(sites=on_sites(op69=(ub, 0))), 'pm4c140c': dict(sites=on_sites(op69=(uc, 0)))}, **kw)


for name, ub, uc, want in (('FX1 b 400.0 / c 400.0', [399, 400], [399, 400], 'NAMED'),
                           ('FX2 b 475.0 / c 325.0', [474, 475], [324, 325], 'NAMED'),
                           ('FX3 b 399.9 / c 400.0 (mean 399.95)', [399, 399, 399, 400, 400], [399, 400], 'SPREAD'),
                           ('FX4 b 475.1 / c 324.9', [474, 474, 475, 475, 475], [324, 324, 324, 325, 325], 'SPREAD'),
                           ('FX2b b 325.0 / c 475.0', [324, 325], [474, 475], 'NAMED'),
                           ('FX4b b 324.9 / c 475.1', [324, 324, 324, 325, 325], [474, 474, 475, 475, 475], 'SPREAD')):
    o = decide(reg_edge(ub, uc))
    ok &= case('%s -> %s' % (name, want), o['outcome'] == want and (o['named'] == ['REG']) == (want == 'NAMED'))
o = decide(census(runs={'pm4c140b': dict(sites=on_sites(op69=([379, 380], 0))),
                        'pm4c140c': dict(sites=on_sites(op69=([379, 380], 0)))}))
ok &= case('O1 a level of 380 with C = 0 fails and its U = L fails too -> plain SPREAD', o['outcome'] == 'SPREAD')

# FX5 and the overlap: MM_out exactly 400 after the exact deduction, DRAW_out 300 (both printed)
mm = on_sites(op27=([2949, 2950], 0), op15=([399, 400], 0))
o = decide(census(runs={t: dict(sites=mm, x_over={'a_hold_n': 0}) for t in S.ON}))
ok &= case('FX5 MM_out = 2950 + 400 - (2800 + 150) = 400.0 -> NAMED (with arm-0 instrument label); DRAW_out 300.0 and '
           'DISP_out -50.0 printed beside (the overlap: MM_out passes, DRAW_out does not)',
           o['outcome'] == 'NAMED' and o['named'] == ['MM_out'] and close(o['table']['MM_out']['mean'], 400.0)
           and close(o['table']['DRAW_out']['mean'], 300.0) and close(o['table']['DISP_out']['mean'], -50.0)
           and o['table']['MM_out']['label'] == 'with arm-0 instrument')
Rm = census(runs={t: dict(sites=mm, x_over={'a_hold_n': 0}) for t in S.ON})
rc, txt = run_main(['--all', '--dir', str(Rm)])
ok &= case('L1 the printed NAMED line carries the label (RC3) and says target, not candidate',
           'NAMED MM_out (with arm-0 instrument) mean 400.0 (b 400.0, c 400.0) - a target of the s141 selection, not a '
           'candidate, not a gain' in txt and 'VERDICT NAMED\n' in txt and rc == 0)
mm2 = on_sites(op27=([2949, 2950], 0), op15=([399, 400], 0))
o = decide(census(runs={t: dict(sites=mm2, x_over={'a_hold_n': 0, 'a_wait_us': 151}) for t in S.ON}))
ok &= case('FX5b the same with a_wait 151 -> MM_out 399.0: not NAMED (the deduction is subtracted, a_wait included)',
           o['outcome'] != 'NAMED' and close(o['table']['MM_out']['mean'], 399.0))

# FX6 in the form of item 212 (b): FLIP raw 450, mh_pres 40, mh_pres_wait 20 -> 390 -> not NAMED; U = 450 -> by bound
fl = on_sites(nop17=([449, 450], 0), nop00=None)
o = decide(census(runs={t: dict(sites=fl) for t in S.ON}))
ok &= case('FX6 FLIP_low = 450 - (40 + 20) = 390.0 -> not NAMED; its U (no deduction) 450 passes -> SPREAD (by bound) naming '
           'FLIP_low', o['outcome'] == 'SPREAD (by bound)' and close(o['table']['FLIP_low']['mean'], 390.0)
           and close(o['table']['FLIP_low']['Ub'], 450.0) and o['bound'] == ['FLIP_low'])
o = decide(census(runs={t: dict(sites=fl, x_over={'mh_pres_wait_us': 0, 'mh_pres_us': 50}) for t in S.ON}))
ok &= case('FX6b the same with mh_pres 50, mh_pres_wait 0 -> 400.0 -> NAMED (wait class)', o['outcome'] == 'NAMED'
           and o['named'] == ['FLIP_low'] and o['table']['FLIP_low']['label'] == 'wait class')
o = decide(census(runs={t: dict(sites=fl, x_over={'mh_pres_wait_us': 11, 'mh_pres_us': 40}) for t in S.ON}))
ok &= case('FX6c mh_pres_wait enters the deduction: 450 - 51 = 399.0 -> not NAMED', o['outcome'] != 'NAMED'
           and close(o['table']['FLIP_low']['mean'], 399.0))

# each deduction A_g and its unit (RC8): exact values with C = 0
ded = on_sites(op27=(2000, 0), op15=(1000, 0), nop18=(500, 0), nop06=(300, 0), nop17=(200, 0))
xo = {'a_hold_us': 1500, 'a_wait_us': 100, 'mh_disp_us': 700, 'pl_eop_ns': 30000, 'pl_bar_ns': 20000, 'pl_sub_ns': 70000,
      'mh_pres_us': 33, 'mh_pres_wait_us': 44, 'a_hold_n': 0}
o = decide(census(runs={t: dict(sites=ded, x_over=xo) for t in S.ON}))
T = o.get('table', {})
for cand, want, up in (('MM_out', 2000.5 + 1000.5 - 1600, 2000.5 + 1000.5 - 1600),
                       ('DRAW_out', 2000.5 - (1500 - 700 + 100), 2000.5 - (1500 - 700)),
                       ('DISP_out', 1000.5 - (700 + 100), 1000.5 - 700),
                       ('EOP_adj', 500.5 - (30 + 20 + 70), 500.5 - (30 + 20)),
                       ('WAITFLIP_adj', 300.5 - 70, 300.5),
                       ('FLIP_low', 200.5 - (33 + 44), 200.5)):
    ok &= case('RC8 %s: the deduction in its unit (us; pl_* ns / 1000) -> L %.1f, U %.1f' % (cand, want, up),
               close(T.get(cand, {}).get('mean'), want) and close(T.get(cand, {}).get('Ub'), up))

# SPREAD (by bound) from U only (item 213 (b)): REG with C = 2000: L 380 fails, U 413 passes
o = decide(census(runs={t: dict(sites=on_sites(op69=([418, 419], 2000))) for t in S.ON}))
ok &= case('B1 REG L 380.0 (c_k 19.5) fails, U 413.0 (3 ns) passes -> SPREAD (by bound) naming REG; c-SENSITIVE (c*mean '
           '9.5 lies in (3, 19.5))', o['outcome'] == 'SPREAD (by bound)' and o['bound'] == ['REG']
           and close(o['table']['REG']['mean'], 380.0) and close(o['table']['REG']['Ub'], 413.0)
           and close(o['table']['REG']['cstar_mean'], 1000 * (419.0 - 400) / 2000.0) and o['sensitive'] == ['REG'])
o = decide(census(runs={t: dict(sites=on_sites(op69=([415, 416], 2000))) for t in S.ON}))
ok &= case('B2 REG U 410.0 but each U 410.0 >= 325 and mean >= 400 -> by bound; U 399 would not: REG L 377, U 410',
           o['outcome'] == 'SPREAD (by bound)' and close(o['table']['REG']['Ub'], 410.0))
o = decide(census(runs={t: dict(sites=on_sites(op69=([400, 401], 2000))) for t in S.ON}))
ok &= case('B3 REG U 395.0 (L 362.0) -> plain SPREAD; c* mean -2.5 ns is not between 3 and c_k -> not c-SENSITIVE',
           o['outcome'] == 'SPREAD' and close(o['table']['REG']['Ub'], 395.0) and o['sensitive'] == [])
o = decide(census(runs={'pm4c140b': dict(sites=on_sites(op69=([418, 419], 2000))),
                        'pm4c140c': dict(sites=on_sites(op69=([320, 321], 2000)))}))
ok &= case('B4 by bound needs both thresholds of U: U_b 413, U_c 315 -> plain SPREAD', o['outcome'] == 'SPREAD')
o = decide(census(runs={t: dict(sites=on_sites(op69=([438, 439], 2000))) for t in S.ON}))
ok &= case('B5 REG L 400.0 with C 2000 at c_k 19.5 -> NAMED; c*mean 19.5 = c_k is not strictly inside -> not c-SENSITIVE',
           o['outcome'] == 'NAMED' and close(o['table']['REG']['mean'], 400.0) and o['sensitive'] == [])
tw = on_sites(op69=([470, 471], 0), op27=([2999, 3000], 0), op15=([399, 400], 0))
o = decide(census(runs={t: dict(sites=tw, x_over={'a_hold_n': 0}) for t in S.ON}))
ok &= case('B6 two NAMED candidates are listed by the mean, highest first (REG 471 before MM_out 450)',
           close(o['table']['REG']['mean'], 471.0) and close(o['table']['MM_out']['mean'], 450.0)
           and o['named'] == ['REG', 'MM_out'])
tw2 = on_sites(op69=([410, 411], 0), op27=([2999, 3000], 0), op15=([399, 400], 0))
o = decide(census(runs={t: dict(sites=tw2, x_over={'a_hold_n': 0}) for t in S.ON}))
ok &= case('B6b the other order: MM_out 450 before REG 411', o['named'] == ['MM_out', 'REG'])
wf = on_sites(nop06=([454, 455], 0))
o = decide(census(runs={t: dict(sites=wf) for t in S.ON}))
ok &= case('B7 WAITFLIP_adj 455 - 55 = 400.0 -> NAMED (wait class)', o['outcome'] == 'NAMED' and o['named'] == ['WAITFLIP_adj']
           and o['table']['WAITFLIP_adj']['label'] == 'wait class')
sy = on_sites(op3c=([399, 400], 0))
o = decide(census(runs={t: dict(sites=sy) for t in S.ON}))
ok &= case('B8 SYNC 400.0 -> NAMED (wait class); EOP 400 with pl_* deductions', o['named'] == ['SYNC']
           and o['table']['SYNC']['label'] == 'wait class')
eo = on_sites(nop18=([506, 507], 0))
o = decide(census(runs={t: dict(sites=eo) for t in S.ON}))
ok &= case('B9 EOP_adj 507 - (40 + 12 + 55) = 400.0 -> NAMED (no label)', o['named'] == ['EOP_adj']
           and o['table']['EOP_adj']['label'] == '')
for cand, sites in (('MEM', on_sites(op37=([399, 400], 0))), ('STATE', on_sites(op12=([399, 400], 0)))):
    o = decide(census(runs={t: dict(sites=sites) for t in S.ON}))
    ok &= case('B10 %s at 400.0 -> NAMED' % cand, o['named'] == [cand])

# LEVEL-INFLATED (item 213 (g)): REG 450 / 450 with C = 0; Sigma = sum raw* - c n - a_hold - a_wait - (eop+bar+sub)
rs = on_sites(op69=([449, 450], 0))
sig = sum(u + 0.5 for k, (u, c) in rs.items() if k != 'op69') + 450.0 - C_K * sum(c for k, (u, c) in rs.items()
                                                                                    if k != 'op69') / 1000.0 - 2950 - 107
for x_t, keep in ((49.5, True), (50.5, False), (-0.5, True), (-100.0, True)):
    o = decide(census(runs={'pm4c140b': dict(sites=rs), 'pm4c140c': dict(sites=rs),
                            'pm4c140a': dict(d0_off=round(sig - x_t, 3)), 'pm4c140d': dict(d0_off=round(sig - x_t, 3))}))
    ok &= case('I%s X = %+.1f -> %s' % ('1' if keep else '2', x_t, 'NAMED kept' if keep else 'SPREAD (by bound), REG by bound'),
               close(o.get('X'), x_t, 1e-3) and ((o['outcome'] == 'NAMED' and o['named'] == ['REG']) if keep
                                                  else (o['outcome'] == 'SPREAD (by bound)' and o['bound'] == ['REG']))
               and o['inflated'] == (x_t > 0))
o = decide(census(runs={'pm4c140b': dict(sites=rs), 'pm4c140c': dict(sites=rs),
                        'pm4c140a': dict(d0_off=[round(sig - 510, 3), round(sig + 490, 3)]),
                        'pm4c140d': dict(d0_off=[round(sig - 510, 3), round(sig + 490, 3)])}))
ok &= case('I3 X = +10 within 2SE by rows (SD 500 per row of a and d) -> no consequence, NAMED kept',
           close(o.get('X'), 10.0, 1e-3) and not o['inflated'] and o['outcome'] == 'NAMED' and o['X2se'] > 10.0)
o = decide(census(runs={'pm4c140b': dict(sites=rs), 'pm4c140c': dict(sites=rs),
                        'pm4c140a': dict(d0_off=round(sig - 50.5, 3), rows=150), 'pm4c140d': dict(d0_off=round(sig - 1000, 3))}))
ok &= case('I4 a run with 0 in DEBT is left out of D0 (a: 150 < 200 rows) - X from d alone = +1000 -> REG by bound',
           o['X_runs'] == ['pm4c140d'] and close(o.get('X'), 1000.0, 1e-3) and o['outcome'] == 'SPREAD (by bound)')
o = decide(census(runs={'pm4c140b': dict(sites=rs), 'pm4c140c': dict(sites=rs),
                        'pm4c140a': dict(rows=150), 'pm4c140d': dict(rows=150)}))
ok &= case('I5 both runs with 0 in DEBT -> X not evaluable, no consequence (NAMED stands)', o.get('X') is None
           and o['outcome'] == 'NAMED')
rc, txt = run_main(['--all', '--dir', str(census(runs={'pm4c140b': dict(sites=rs), 'pm4c140c': dict(sites=rs),
                                                       'pm4c140a': dict(d0_off=round(sig - 60, 3)),
                                                       'pm4c140d': dict(d0_off=round(sig - 60, 3))}))])
ok &= case('I6 the printed LEVEL-INFLATED line and BY BOUND line', 'LEVEL-INFLATED 60.0' in txt and 'BY BOUND (item 213 (b), (g)): REG'
           in txt and 'VERDICT SPREAD (by bound)' in txt)

# --- 4. c_k (item 212 (d)) --------------------------------------------------------------------------------------------------
for name, sites, want in (
        ('C1 min of two candidates (op2a 19.5, op13 24.5, E whole 22.0) -> 19.5',
         on_sites(op13=(24, 1000)), 19.5),
        ('C2 the branch E whole: op2a 600 + op13 600 (neither >= 1000; sum 1200) -> E = 1000 (11.5 + 13.5) / 1200',
         on_sites(op2a=(11, 600), op13=(13, 600)), 1000 * 25.0 / 1200),
        ('C3 op2a exactly 1000/frame is a candidate', on_sites(op2a=(19, 1000)), 19.5)):
    o = decide(census(runs={t: dict(sites=sites) for t in S.ON}))
    ok &= case(name, close(o['runs']['pm4c140b'].get('c_k'), want) and 'pm4c140b IF5' not in o['if_fails'])
o = decide(census(runs={t: dict(sites=on_sites(op2a=(19, 999))) for t in S.ON}))
ok &= case('FX15 E: max C 999 and the E sum 999 -> IF5 (INSTRUMENT_FAIL)', o['outcome'] == 'INSTRUMENT_FAIL'
           and 'pm4c140b IF5' in o['if_fails'] and 'pm4c140c IF5' in o['if_fails'])
o = decide(census(runs={t: dict(sites=on_sites(op2a=(19, 998), op13=(0, 1))) for t in S.ON}))
ok &= case('FX15b E sum 999 of two sites -> IF5', 'pm4c140b IF5' in o['if_fails'])
for name, sites, bad in (('2.9', on_sites(op2a=(14, 5000)), True), ('3.0', on_sites(op2a=([2, 3], 1000)), False),
                         ('100.0', on_sites(op2a=([99, 100], 1000)), False),
                         ('100.1', on_sites(op2a=([99, 99, 100, 100, 100], 1000)), True)):
    o = decide(census(runs={t: dict(sites=sites) for t in S.ON}))
    ok &= case('FX16 c_k %s ns -> %s' % (name, 'IF5b' if bad else 'in the band'), ('pm4c140b IF5b' in o['if_fails']) == bad)
rc, txt = run_main(['--tag', 'pm4c140b', '--dir', str(census(runs={t: dict(sites=on_sites(op2a=([40, 41], 1000)))
                                                                     for t in S.ON}))])
ok &= case('C4 c_k 41.0 > 40 -> the masked note c-HIGH (a note, not a gate)', 'c-HIGH above 40 ns' in txt and rc == 0)
rc, txt = run_main(['--tag', 'pm4c140b', '--dir', str(census(runs={t: dict(sites=on_sites(op2a=([39, 40], 1000)))
                                                                     for t in S.ON}))])
ok &= case('C5 c_k 40.0 -> no c-HIGH', 'c-HIGH' not in txt and rc == 0)

# --- 5. the identities -----------------------------------------------------------------------------------------------------
for name, g, bad in (('lower - 0.01', -6.01, True), ('lower', -6.0, False), ('250.0', 250.0, False), ('250.1', 250.1, True)):
    o = decide(census(runs={t: dict(g_ns=g, cmd_n=10000) for t in S.ON}))
    ok &= case('FX17 g %s (pl_sub 55 us, pl_cmd_n 10000 -> lower -6.0 ns) -> %s' % (name, 'IF6' if bad else 'ok'),
               ('pm4c140b IF6' in o['if_fails']) == bad and ('pm4c140c IF6' in o['if_fails']) == bad)
for name, f, bad in (('-0.51 %', -51, True), ('-0.50 %', -50, False), ('50.0 %', 5000, False), ('50.1 %', 5010, True)):
    # op27 1550 packets -> the sum of C is 5000 at op12 100; op12 then sets the sum to 10000 - F
    o = decide(census(runs={t: dict(sites=on_sites(op27=(2800, 1550), op12=(20, 100 + 5000 - f)), cmd_n=10000,
                                    x_over={'a_hold_n': 1818}) for t in S.ON}))
    ok &= case('FX18 F %s of pl_cmd_n 10000 -> %s' % (name, 'IF7' if bad else 'ok'), ('pm4c140b IF7' in o['if_fails']) == bad)
for name, u27, bad in (('-5.1', [2899] + [2900] * 9, True), ('-5.0', 2900, False)):
    o = decide(census(runs={t: dict(sites=on_sites(op27=(u27, 5000)), x_over={'a_hold_us': 3156}) for t in S.ON}))
    ok &= case('FX19 M %s us -> %s' % (name, 'IF8' if bad else 'ok'), ('pm4c140b IF8' in o['if_fails']) == bad)
for name, c27, multi, bad in (('+0.6 % (H 31 of 6000), no op2c', 5701, False, True), ('+0.5 % (30)', 5702, False, False),
                              ('-0.5 % (-30)', 5762, False, False), ('-0.6 % (-31)', 5763, False, True),
                              ('+0.6 % with op2c present', 5701, True, False), ('-0.6 % with op2c present', 5763, True, True)):
    s = on_sites(op27=(2900, c27))
    if multi:
        s['op2c'] = (5, 1)
    o = decide(census(runs={t: dict(sites=s, x_over={'a_hold_n': 6000}) for t in S.ON}))
    ok &= case('FX20 H %s -> %s' % (name, 'IF9' if bad else 'ok'), ('pm4c140b IF9' in o['if_fails']) == bad)

# --- 6. IF1-IF4, IF10, IF11 ---------------------------------------------------------------------------------------------------
o = decide(census(runs={'pm4c140a': dict(sites={'op27': (5, 1)})}))
ok &= case('FX11 op27 on a pm4 line of a (0) -> IF1 INSTRUMENT_FAIL', o['outcome'] == 'INSTRUMENT_FAIL' and o['if_fails'] == ['pm4c140a IF1'])
o = decide(census(runs={'pm4c140d': dict(pre_rows=2, row_hook=lambda i, n: dict(sites={'nop17': (1, 1)}) if n == 1798 else {})}))
ok &= case('IF1b a name on a line of d outside the window (n 1798) -> IF1 (any line)', o['if_fails'] == ['pm4c140d IF1'])
for name, k_without, bad in (('98.9 %', 11, True), ('99.0 %', 10, False)):
    o = decide(census(runs={'pm4c140b': dict(rows=1000, sites=on_sites(op2a=(20, 1100)),
                                             row_hook=lambda i, n, k=k_without: dict(del_sites=list(ON_SITES),
                                                                                     x_over={'a_hold_n': 0})
                                             if 1800 <= n < 1800 + k else {})}))
    ok &= case('FX12 P1 %s of the NEW window rows of b with a name -> %s' % (name, 'IF2' if bad else 'ok'),
               ('pm4c140b IF2' in o['if_fails']) == bad)
o = decide(census(runs={'pm4c140c': dict(sites=on_sites(opff=(1, 1)))}))
ok &= case('FX13 a name outside the map (opff) -> IF3', 'pm4c140c IF3' in o['if_fails'])
o = decide(census(runs={'pm4c140a': dict(sites={'stream-prefetch': (1, 1)})}))
ok &= case('IF3b a non-opcode name (stream-prefetch) at 0 is neither IF1 nor IF3', o['if_fails'] == [])
o = decide(census(runs={'pm4c140c': dict(row_hook=lambda i, n: dict(sites={'op3f': (0, 1)}) if n == 1850 else {})}))
ok &= case('FX14 op3f=0/1 in one window row of c -> IF4', o['if_fails'] == ['pm4c140c IF4'])
o = decide(census(runs={'pm4c140c': dict(pre_rows=2, row_hook=lambda i, n: dict(sites={'op3f': (0, 1)}) if n == 1799 else {})}))
ok &= case('IF4b op3f outside the window (n 1799) -> not IF4', 'pm4c140c IF4' not in o['if_fails'])
for name, k, bad in (('1.1 %', 11, True), ('1.0 %', 10, False)):
    o = decide(census(runs={'pm4c140b': dict(rows=1000, sites=on_sites(op2a=(20, 1100)),
                                             row_hook=lambda i, n, k=k: dict(drop_pm4=True) if 1900 <= n < 1900 + k else {})}))
    ok &= case('FX21 %s of the NEW rows of b without the pm4 line -> %s' % (name, 'IF10' if bad else 'ok'),
               ('pm4c140b IF10' in o['if_fails']) == bad)
for fld in S.IF11_FIELDS:
    o = decide(census(runs={'pm4c140b': dict(row_hook=lambda i, n, f=fld: dict(x_over={f: None}) if n == 1900 else {})}))
    ok &= case('IF11 %s missing in one NEW window row of b -> IF11' % fld, 'pm4c140b IF11' in o['if_fails'])
o = decide(census(runs={'pm4c140a': dict(row_hook=lambda i, n: dict(x_over={'mh_pres_wait_us': None}) if n == 1900 else {})}))
ok &= case('IF11b a field missing in a run with 0 -> IF11 too', o['if_fails'] == ['pm4c140a IF11'])

# --- 7. IF0 ----------------------------------------------------------------------------------------------------------------
IF0_CASES = (
    ('build', dict(meta_over={'binary_sha256': '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'})),
    ('trace 0 in b', dict(env_over={'KYTY_PM4_TRACE': '0'})),
    ('trace missing', dict(env_over={'KYTY_PM4_TRACE': None})),
    ('schedule', dict(env_over={'KYTY_GATE_SCHEDULE': '90+1800:bindlean=0|bindlean=1'})),
    ('abba', dict(env_over={'KYTY_GATE_SCHEDULE_ABBA': '1'})),
    ('pin missing', dict(env_over={'KYTY_GPU_CLOCK_PIN': None})),
    ('checkpoints', dict(env_over={'KYTY_GPU_CHECKPOINTS': '1'})),
    ('video', dict(env_over={'KYTY_REC': 'x.mp4'})),
    ('wall', dict(env_over={'KYTY_GPU_WALL': '1'})),
    ('gates differ', dict(meta_over={'gates': GATES_TEXT.replace('bindlean=0', 'bindlean=1')})),
    ('knob log without rbcen', dict(gates=KN[:4])),
    ('knob log with bindlean=1', dict(gates=KN + ['bindlean=1'])),
    ('GateArm line', dict(arms=1)),
    ('json missing', dict(no_json=True)),
    ('log missing', dict(no_log=True)),
)
for name, kw in IF0_CASES:
    o = decide(census(runs={'pm4c140b': kw}))
    ok &= case('IF0 %s -> INSTRUMENT_FAIL (pm4c140b IF0)' % name, o['outcome'] == 'INSTRUMENT_FAIL'
               and 'pm4c140b IF0' in o['if_fails'])
    rows0 = dict(o['runs']['pm4c140b']['if']['IF0'])
    if name == 'json missing':
        ok &= case('IF0 json missing names the row json readable NO', rows0.get('json readable') is False)
    if name == 'log missing':
        ok &= case('IF0 log missing names the row log present NO and still carries the json rows',
                   rows0.get('log present') is False and rows0.get('json readable') is True)
Rg = census()
(Rg / 'gates_base.txt').write_bytes((GATES_TEXT + ' extra=1' + chr(10)).encode('ascii'))
for tg in S.SEQ:
    jp = Rg / ('%s.json' % tg)
    mt = json.loads(jp.read_text(encoding='utf-8'))
    mt['gates'] = GATES_TEXT + ' extra=1'
    jp.write_text(json.dumps(mt), encoding='utf-8')
o = decide(Rg)
ok &= case('IF0e a base file other than the sealed sha (the json gates equal to it) -> IF0 in every run',
           sorted(o['if_fails']) == ['pm4c140a IF0', 'pm4c140b IF0', 'pm4c140c IF0', 'pm4c140d IF0'])
o = decide(census(runs={'pm4c140a': dict(env_over={'KYTY_PM4_TRACE': '1'})}))
ok &= case('IF0b trace 1 in a (0 expected) -> IF0', 'pm4c140a IF0' in o['if_fails'])
o = decide(census(runs={'pm4c140b': dict(gates=list(reversed(KN)))}))
ok &= case('IF0c the knob lines in another order -> not IF0', o['if_fails'] == [])
S.PRED_SHA, S.PRED_BYTES = 'a' * 64, 10
o1 = decide(census(runs=dict((t, dict(prereg={'sha256': 'a' * 64, 'bytes': 10})) for t in S.SEQ)))
o2 = decide(census(runs=dict((t, dict(prereg={'sha256': 'a' * 64, 'bytes': 11 if t == 'pm4c140c' else 10})) for t in S.SEQ)))
o3 = decide(census())
S.PRED_SHA, S.PRED_BYTES = None, None
ok &= case('IF0d sealed: the prereg sha and bytes of each registered json = PRED_SHA / PRED_BYTES; a differing byte count or '
           'no prereg -> IF0', o1['if_fails'] == [] and o2['if_fails'] == ['pm4c140c IF0']
           and sorted(o3['if_fails']) == ['pm4c140a IF0', 'pm4c140b IF0', 'pm4c140c IF0', 'pm4c140d IF0'])

# --- 8. DEBT at the real 4000 (items 210 (e)(4), 212 (e)) --------------------------------------------------------------------
S.MIN_NEW_ROWS = REAL_MIN
ok &= case('D0 the real minimum is 4000 NEW window rows (the scorer constant, read before any override)', REAL_MIN == 4000)
o = decide(census(runs={'pm4c140a': dict(rows=10), 'pm4c140d': dict(rows=10), 'pm4c140b': dict(rows=4000),
                        'pm4c140c': dict(rows=4000)}))
ok &= case('FX7 4000 NEW rows in b and c -> reads (not DEBT)', o['outcome'] == 'SPREAD')
o = decide(census(runs={'pm4c140a': dict(rows=10), 'pm4c140d': dict(rows=10), 'pm4c140b': dict(rows=3999),
                        'pm4c140c': dict(rows=4000)}))
ok &= case('FX8 3999 in b -> DEBT (item 212 (e))', o['outcome'] == 'DEBT')
o = decide(census(runs={'pm4c140a': dict(rows=10), 'pm4c140d': dict(rows=10), 'pm4c140b': dict(rows=4000),
                        'pm4c140c': dict(rows=3999)}))
ok &= case('FX8b 3999 in c -> DEBT', o['outcome'] == 'DEBT')
Rd = census(runs={'pm4c140a': dict(rows=10), 'pm4c140d': dict(rows=10), 'pm4c140b': dict(rows=3999),
                  'pm4c140c': dict(rows=3999)})
rc, txt = run_main(['--all', '--dir', str(Rd)])
ok &= case('FX9 3999 in b and c -> DEBT, rc 1, the counts printed', rc == 1 and 'VERDICT DEBT\n' in txt
           and 'pm4c140b 3999, pm4c140c 3999' in txt)
Rp = census(runs={'pm4c140a': dict(rows=3999), 'pm4c140d': dict(rows=4000), 'pm4c140b': dict(rows=4000),
                  'pm4c140c': dict(rows=4000)})
rc, txt = run_main(['--all', '--dir', str(Rp)])
ok &= case('FX10 3999 in a -> the outcome does not change (SPREAD), the price reference is not printed', rc == 0
           and 'VERDICT SPREAD\n' in txt and 'PRICE REFERENCE not printed' in txt)
Rq = census(runs={'pm4c140a': dict(rows=4000), 'pm4c140d': dict(rows=4000, d0_off=2010.0), 'pm4c140b': dict(rows=4000),
                  'pm4c140c': dict(rows=4000, m_over={'dt_us': 34100})})
rc, txt = run_main(['--all', '--dir', str(Rq)])
ok &= case('FX10b no DEBT anywhere -> the price reference: d dt_us 50.0, d pl_proc / packets printed', rc == 0
           and 'PRICE REFERENCE (item 210 (e)(5)(v); [c, between runs]; not a gate): d dt_us 50.0 us' in txt)
o = decide(census(runs={'pm4c140a': dict(rows=10, sites={'op27': (5, 1)}), 'pm4c140d': dict(rows=10),
                        'pm4c140b': dict(rows=10), 'pm4c140c': dict(rows=10)}))
ok &= case('FX22 IF1 and DEBT at once -> INSTRUMENT_FAIL', o['outcome'] == 'INSTRUMENT_FAIL' and o['if_fails'] == ['pm4c140a IF1'])
o = decide(census(runs={'pm4c140a': dict(rows=10), 'pm4c140d': dict(rows=10), 'pm4c140b': dict(rows=0, pre_rows=5),
                        'pm4c140c': dict(rows=4000)}))
ok &= case('D1 a run with 1 without any NEW window row -> DEBT, not IF (IF2, IF4-IF10 need a row)',
           o['outcome'] == 'DEBT' and o['if_fails'] == [])
S.MIN_NEW_ROWS = SMALL

# --- 9. the masked forms (RC7), the smoke, the per-call form -----------------------------------------------------------------
Rk = census(runs={t: dict(sites=on_sites(op69=([449, 450], 0))) for t in S.ON})
rc, txt = run_main(['--tag', 'pm4c140b', '--dir', str(Rk), '--out', str(Rk / 'b.json')])
jb = json.loads((Rk / 'b.json').read_text(encoding='ascii'))
txh = re.sub(r'[0-9a-f]{16,}', '', txt)
ok &= case('M1 --tag pm4c140b: RUN_READS rc 0, masked - no level, no c_k value, no identity value, no table (REG 450 would '
           'show as 450.0)', rc == 0 and 'VERDICT pm4c140b: RUN_READS' in txt and 'printed_delta=no' in txt
           and '450' not in txh and '19.5' not in txh and 'THE CANDIDATES' not in txt and 'g 50' not in txt
           and 'NEW window rows (item 212 (v)) 200 -> reads' in txt and 'c_k candidates of E with >= 1000/frame: op2a' in txt
           and 'c_k in [3, 100] ns: yes' in txt and 'IF6 PASS' in txt)
ok &= case('M2 the per-call json: printed_delta no, no table, no level, the IF rows', jb['printed_delta'] == 'no'
           and 'table' not in jb and jb['verdict'] == 'RUN_READS' and 'c_k' not in jb and 'IF6' in jb['if']
           and '450' not in re.sub(r'[0-9a-f]{16,}', '', json.dumps(jb))
           and '19.5' not in re.sub(r'[0-9a-f]{16,}', '', json.dumps(jb)) and jb['c_cands'] == ['op2a', 'E'])
rc, txt = run_main(['--tag', 'pm4c140a', '--dir', str(Rk)])
ok &= case('M3 --tag pm4c140a (0): IF0, IF1, IF3, IF11 rows; RUN_READS', rc == 0 and 'IF1 PASS' in txt and 'IF0 PASS' in txt
           and 'IF11 PASS' in txt and 'IF3 PASS' in txt and 'IF6' not in txt)
Rs = BASE / 'smoke'
Rs.mkdir(parents=True, exist_ok=True)
shutil.copyfile(BASE_GATES, Rs / 'gates_base.txt')
write_run(Rs, 'pm4s140', rows=300, sites=on_sites(op69=([449, 450], 0)))
rc, txt = run_main(['--smoke', 'pm4s140', '--dir', str(Rs), '--out', str(Rs / 's.json')])
ok &= case('M4 --smoke pm4s140: masked (no level), the names, E candidates, c_k in the band, IF and identities PASS; the knob '
           'string from the log', rc == 0 and 'VERDICT pm4s140: RUN_READS' in txt
           and '450' not in re.sub(r'[0-9a-f]{16,}', '', txt)
           and 'op*/nop* names on the FrameTrace-pm4: lines: 10 distinct' in txt and 'knob string from the log: ' + ' '.join(KN)
           in txt and 'IF9 PASS' in txt and 'IF5b PASS' in txt)
write_run(Rs, 'pm4s140', rows=300, sites=on_sites(op3f=(1, 1)))
rc, txt = run_main(['--smoke', 'pm4s140', '--dir', str(Rs)])
ok &= case('M5 the smoke with an IF -> RUN_FAIL rc 1', rc == 1 and 'VERDICT pm4s140: RUN_FAIL' in txt and 'IF4 FAIL' in txt)
S.MIN_NEW_ROWS = REAL_MIN
rc, txt = run_main(['--tag', 'pm4c140c', '--dir', str(Rk)])
S.MIN_NEW_ROWS = SMALL
ok &= case('M6 a call below 4000 NEW rows -> RUN_DEBT rc 1, the masked line says DEBT', rc == 1
           and 'VERDICT pm4c140c: RUN_DEBT' in txt and 'NEW window rows (item 212 (v)) 200 -> DEBT' in txt)
rc, txt = run_main(['--tag', 'pm4c140b', '--dir', str(census(runs={t: dict(sites=on_sites(op2a=([99, 99, 100, 100, 100], 1000)))
                                                                     for t in S.ON}))])
ok &= case('M6b c_k 100.1 ns: the masked line says c_k in the band NO, RUN_FAIL', rc == 1 and 'c_k in [3, 100] ns: NO' in txt
           and 'IF5b FAIL' in txt)
for argv in (['--tag', 'pm4c140e'], ['--smoke', 'pm4s141'], [], ['--check-seal', '--tag', 'pm4s140'], ['--tag', 'pm4s140']):
    rc, txt = run_main(argv + ['--dir', str(Rk)])
    ok &= case('M7 usage %r -> rc 2' % argv, rc == 2 and txt.startswith('usage'))
rc, txt = run_main(['--all', '--dir', str(census(runs={'pm4c140c': dict(sites=on_sites(op3f=(0, 1)))}))])
ok &= case('M8 --all with an IF -> rc 1, VERDICT INSTRUMENT_FAIL, the failed list', rc == 1
           and 'VERDICT INSTRUMENT_FAIL\n' in txt and 'failed: pm4c140c IF4' in txt)

# --- 10. the pre-seal check -----------------------------------------------------------------------------------------------
Rc = BASE / 'seal'
(Rc / 'pred').mkdir(parents=True, exist_ok=True)
(Rc / 'go140a.sh').write_bytes(b'#!/bin/bash\n')
own = S.body_sha(Path(SRC).read_bytes())
pred_text = ('seal\nscorer body sha256: %s\nchain sha256: %s\n' % (own, hashlib.sha256(b'#!/bin/bash\n').hexdigest())).encode()
(Rc / 'pred' / '01_pm4c140.md').write_bytes(pred_text)
(Rc / 'x.txt').write_bytes(b'x')
(Rc / 'SEALS140.txt').write_text('# seal\n%s  x.txt\n%s  pred/01_pm4c140.md\n' % (
    hashlib.sha256(b'x').hexdigest(), hashlib.sha256(pred_text).hexdigest()), encoding='utf-8')


def seal_run(tag='pm4c140a', psha=None, pbytes=None):
    S.PRED_SHA = hashlib.sha256(pred_text).hexdigest() if psha is None else psha
    S.PRED_BYTES = len(pred_text) if pbytes is None else pbytes
    try:
        return run_main(['--check-seal', '--tag', tag, '--dir', str(Rc)])
    finally:
        S.PRED_SHA, S.PRED_BYTES = None, None


rc, txt = seal_run()
ok &= case('P1 the pre-seal check passes on a consistent seal (rc 0, 5 ok rows)', rc == 0 and 'check-seal pm4c140a: PASS' in txt
           and txt.count('  ok ') == 5)
rc, txt = seal_run(psha='0' * 64)
ok &= case('P2 PRED_SHA differs -> FAIL rc 1', rc == 1 and 'NO PRED_SHA' in txt)
rc, txt = seal_run(pbytes=len(pred_text) + 1)
ok &= case('P3 PRED_BYTES differs -> FAIL', rc == 1)
(Rc / 'go140a.sh').write_bytes(b'#!/bin/bash\n# changed\n')
rc, txt = seal_run()
(Rc / 'go140a.sh').write_bytes(b'#!/bin/bash\n')
ok &= case('P4 the chain changed after the seal -> FAIL', rc == 1 and 'NO the seal names the chain' in txt)
(Rc / 'x.txt').write_bytes(b'y')
rc, txt = seal_run()
(Rc / 'x.txt').write_bytes(b'x')
ok &= case('P5 a sealed file changed -> FAIL naming it', rc == 1 and 'differ: x.txt' in txt)
st = (Rc / 'SEALS140.txt').read_text(encoding='utf-8')
(Rc / 'SEALS140.txt').write_text('# empty\n', encoding='utf-8')
rc, txt = seal_run()
(Rc / 'SEALS140.txt').write_text(st, encoding='utf-8')
ok &= case('P6 SEALS140.txt without a sha line -> FAIL', rc == 1)
(Rc / 'pred' / '01_pm4c140.md').write_bytes(pred_text.replace(own.encode(), b'0' * 64))
S.PRED_SHA = hashlib.sha256(pred_text.replace(own.encode(), b'0' * 64)).hexdigest()
S.PRED_BYTES = len(pred_text)
rc, txt = run_main(['--check-seal', '--tag', 'pm4c140d', '--dir', str(Rc)])
S.PRED_SHA, S.PRED_BYTES = None, None
(Rc / 'pred' / '01_pm4c140.md').write_bytes(pred_text)
ok &= case('P7 the seal names another scorer body -> FAIL', rc == 1 and 'NO the seal names this scorer body' in txt)
ok &= case('P8 body_sha ignores only the two seal lines', S.body_sha(b"PRED_SHA = 'abc'\nPRED_BYTES = 5\nx\n")
           == S.body_sha(b"PRED_SHA = None\nPRED_BYTES = 7\nx\n") != S.body_sha(b"PRED_SHA = None\nPRED_BYTES = 7\ny\n"))

# --- 11. ASCII in a strict cp1250 stdout (item 175 (v), process 3) --------------------------------------------------------------
def run_cp1250(argv):
    raw = io.BytesIO()
    wr = io.TextIOWrapper(raw, encoding='cp1250', errors='strict', newline='')
    save = sys.stdout
    sys.stdout = wr
    try:
        rc = S.main(argv)
        wr.flush()
    except UnicodeError:
        rc = 'UnicodeError'
    finally:
        sys.stdout = save
    return rc, raw.getvalue()


Rn = census(runs={t: dict(sites=on_sites(op69=([449, 450], 0))) for t in S.ON})
for argv in (['--all', '--dir', str(Rn)], ['--tag', 'pm4c140b', '--dir', str(Rn)], ['--tag', 'pm4c140a', '--dir', str(Rn)],
             ['--smoke', 'pm4s140', '--dir', str(Rs)], ['--all', '--dir', str(census(runs={'pm4c140a': dict(no_log=True)}))]):
    rc, raw = run_cp1250(argv)
    ok &= case('Z1 %s under a strict cp1250 stdout -> no encoding error, ASCII only' % argv[0], rc in (0, 1)
               and all(c < 128 for c in raw) and len(raw) > 0)
ok &= case('Z2 the scorer source is ASCII only', all(c < 128 for c in Path(SRC).read_bytes()))

print('%d checks' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
