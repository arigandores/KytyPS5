"""Track M link M9f (HPP-871): the in-process fixture suite of the T188 rules t188_rules.py - the suite that mutlib v4.1 runs against
every mutant of mut_t188.py (the mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last
statement is `sys.exit(0 if ok else 1)`; no subprocess, no file except the scorer).  One or more cases per member and per edge (see
test_m9f.py, which runs this suite as its first part): the line forms (the field tuples of the code are written here, not taken from
the scorer), the mode witness, E, Z, N, I1, I2a-d, I3, I4, I5, I6, I8, I9, the class choice, the class rows, the field open and the T109
rows of items 789 (g) and 791 (v).  First line 'suite ... target ...', last line ALL OK.  ASCII only.
usage: python test_t188.py [<t188_rules.py under test>]"""
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 't188_rules.py')
print('suite test_t188.py sha256 %s target t188_rules.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('t188_rules_under_test', SRC)
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
N_CASES = [0]
BASE = Path('C:/kyty/m657/m9f/fx_t188')   # mutlib gives every job its own copy of this directory (unused by the cases)
BASE.mkdir(parents=True, exist_ok=True)

# the field tuples of the code (main 2042c697 src/libs/diagT188.cpp kNames, kClassNames, the T188Img head and the T109Stat format)
STAT = ('part', 'part_st', 'part_fill', 'part_copy', 'part_unk', 'part_off', 'part_synced', 'part_dlmem', 'reopen', 'ep_new',
        'ep_prop', 'prop_merge', 'w_mipal', 'w_inmip', 'w_other', 'w_bytes', 'img_bytes', 'img_bytes_unsync',
        'img_full_unsync', 'in_pass', 'in_pass_unsync', 'cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop',
        'cl_oth', 'cl_vo', 'cl_cover', 'cl_cmp', 'cl_msaa', 'cl_free', 'cl_commit', 'cl_copydst', 'cl_skip', 'cl_none',
        'open', 'ep_pend', 'pend_done', 'pend_drop', 'pend_free', 'pend_open', 'lost_bytes', 'lost_pend_bytes', 'w_ovf',
        'sync_full', 'sync_part', 'dl_mem', 'ep_bad', 'lock_bad', 'tint_ep', 'tint_mips', 'tint_bytes', 'tint_part_mips',
        'tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu', 'tint_skip_ovf', 'tint_bad', 'tint_rb_req',
        'tint_rb0_ok', 'tint_rb0_bad', 'tint_rb0_none', 'tint_rb0_nofmt', 'tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad',
        'tint_rb1_none')
CLS = ('ev', 'ev_st', 'ev_fill', 'ev_copy', 'ev_off', 'ev_synced', 'ev_dlmem', 'ep_new', 'ep_prop', 'cl_smp', 'cl_rt',
       'cl_rtclr', 'cl_vo', 'cl_commit', 'cl_free', 'lost_bytes', 'lost_pend_bytes', 'img_bytes', 'tint_ep', 'tint_mips',
       'tint_bytes', 'tint_skip', 'tint_rb0_ok', 'tint_rb0_bad', 'tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad')
HEAD = ('fmt', 'tile', 'w', 'h', 'levels', 'layers', 'cmp', 'samples', 'usage', 'vol')
T109 = ('d32', 'zx_d32', 'zx_narrow', 'bias_d32', 'bias_narrow', 'ovr_w', 'ovr_vpc', 'zx_narrow_vi', 'bias_narrow_vi', 'narrow_cd')
I3_MAP = (('ev', ('part',)), ('ev_st', ('part_st',)), ('ev_fill', ('part_fill',)), ('ev_copy', ('part_copy',)), ('ev_off', ('part_off',)),
          ('ev_synced', ('part_synced',)), ('ev_dlmem', ('part_dlmem',)), ('ep_new', ('ep_new',)), ('ep_prop', ('ep_prop',)),
          ('cl_smp', ('cl_smp',)), ('cl_rt', ('cl_rt',)), ('cl_rtclr', ('cl_rtclr',)), ('cl_vo', ('cl_vo',)),
          ('cl_commit', ('cl_commit',)), ('cl_free', ('cl_free',)), ('lost_bytes', ('lost_bytes',)),
          ('lost_pend_bytes', ('lost_pend_bytes',)), ('img_bytes', ('img_bytes',)), ('tint_ep', ('tint_ep',)),
          ('tint_mips', ('tint_mips',)), ('tint_bytes', ('tint_bytes',)),
          ('tint_skip', ('tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu', 'tint_skip_ovf')),
          ('tint_rb0_ok', ('tint_rb0_ok',)), ('tint_rb0_bad', ('tint_rb0_bad',)), ('tint_rb1_ok', ('tint_rb1_ok',)),
          ('tint_rb1_over', ('tint_rb1_over',)), ('tint_rb1_bad', ('tint_rb1_bad',)))
PLAN_MODE = (2, 'all', 4)


def case(name, cond):
    N_CASES[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


ok = True
ok &= case('the field tuples of the scorer = the code (70 / 27 / 10 / 10) and the I3 map, plan mode (2, all, 4), share 0.8, max 2, '
           'cover 0.5', T.STAT == STAT and T.CLS == CLS and T.HEAD == HEAD and T.T109 == T109 and T.I3_MAP == I3_MAP
           and T.PLAN_MODE == PLAN_MODE and T.SHARE == 0.8 and T.MAX_CLASSES == 2 and T.COVER_MIN == 0.5)

# ---- a consistent exit state -------------------------------------------------------------------------------------------------------
def base_stat():
    e = dict((k, 0) for k in STAT)
    e.update(part=100, part_st=60, part_fill=30, part_copy=10, part_unk=0, part_off=7, part_synced=20, part_dlmem=5, reopen=15,
             ep_new=60, ep_prop=4, w_mipal=50, w_inmip=30, w_other=20, w_bytes=1000, img_bytes=5000, img_bytes_unsync=4000,
             img_full_unsync=6000, in_pass=40, in_pass_unsync=30, cl_smp=20, cl_rt=10, cl_rtclr=5, cl_vo=1, cl_cover=3, cl_free=10,
             cl_commit=5, cl_copydst=2, open=8, ep_pend=6, pend_done=3, pend_drop=1, pend_free=1, pend_open=1, lost_bytes=900,
             lost_pend_bytes=100, tint_ep=20, tint_mips=30, tint_bytes=500, tint_skip_fmt=4, tint_skip_vol=2, tint_skip_cpu=1,
             tint_rb_req=8, tint_rb0_ok=6, tint_rb0_none=2, tint_rb1_ok=3, tint_rb1_over=2, tint_rb1_none=1)
    return e


def img_rows(e):
    """Two classes and key=other summing to e (I3)."""
    a = dict((k, 0) for k in CLS)
    b = dict((k, 0) for k in CLS)
    o = dict((k, 0) for k in CLS)
    for c, gs in I3_MAP:
        v = sum(e[g] for g in gs)
        a[c] = v // 2
        b[c] = v // 4
        o[c] = v - a[c] - b[c]
    a.update(lost_bytes=600, lost_pend_bytes=0, tint_bytes=300, tint_ep=10)
    b.update(lost_bytes=250, lost_pend_bytes=50, tint_bytes=150, tint_ep=5)
    o.update(lost_bytes=50, lost_pend_bytes=50, tint_bytes=50, tint_ep=5)
    ra = dict(when='exit', key='00000000000000aa', **dict((k, i + 1) for i, k in enumerate(HEAD)))
    ra.update(a)
    rb = dict(when='exit', key='00000000000000bb', **dict((k, i + 2) for i, k in enumerate(HEAD)))
    rb.update(b)
    ro = dict(when='exit', key='other')
    ro.update(o)
    return [ra, rb, ro]


def t109(when, **kw):
    d = dict((k, 0) for k in T109)
    d.update(when=when, d32=100, zx_d32=20, zx_narrow=5, bias_d32=10, bias_narrow=2, ovr_w=3, ovr_vpc=1, zx_narrow_vi=3,
             bias_narrow_vi=1, narrow_cd=2)
    d.update(kw)
    return d


def state(e=None, img=None, t9=None, mode=None, per=None):
    e = e or base_stat()
    r = T.empty()
    r['mode'] = [PLAN_MODE] if mode is None else mode
    r['stat'] = (per or []) + [dict(e, when='exit')]
    r['img'] = img_rows(e) if img is None else img
    r['t109'] = [t109('periodic', zx_narrow=4, zx_narrow_vi=2), t109('exit')] if t9 is None else t9
    return r


M5 = dict(when='exit', inv_part_src=100, inv_part=100, inv_off=7)


def mem_of(ch, prefix):
    return [b for a, b in ch if a.startswith(prefix)]


ch0 = T.checks(state(), M5)
ok &= case('consistent state: every stop member holds (%d members)' % len(ch0), all(b for _, b in ch0) and len(ch0) >= 20)
ok &= case('rows: img rows of the fixture sum to the globals (I3 holds)', mem_of(ch0, 'I3') == [True])


def broken(prefix, mut, m5=M5, **kw):
    r = state(**kw)
    mut(r)
    ch = T.checks(r, m5)
    others = [a for a, b in ch if not b and not a.startswith(prefix)]
    return mem_of(ch, prefix), others


def setx(field, v):
    def f(r):
        r['stat'][-1][field] = v
    return f


def addx(field, dv):
    def f(r):
        r['stat'][-1][field] += dv
    return f


# I1
m, o = broken('I1', setx('part_unk', 1))
ok &= case('I1: part_unk 1 -> I1 violated (and Z)', m == [False])
m, o = broken('I1', addx('part_st', 1))
ok &= case('I1: part_st + 1 -> violated', m == [False])
# I2a / I2b / I2c / I2d
m, o = broken('I2a', addx('reopen', 1))
ok &= case('I2a: reopen + 1 -> violated', m == [False])
m, o = broken('I2b', addx('cl_dt', 1))
ok &= case('I2b: cl_dt + 1 (a closing site outside T188Img) -> violated', m == [False])
m, o = broken('I2b', addx('cl_none', 5))
ok &= case('I2b: cl_none is not in the sum -> holds', m == [True])
m, o = broken('I2b', addx('open', 1))
ok &= case('I2b: open + 1 -> violated', m == [False])
m, o = broken('I2c', addx('pend_open', 1))
ok &= case('I2c: pend_open + 1 -> violated', m == [False])
s3 = 20 + 10 + 5 + 1


def pend_eq(v):
    def f(r):
        e = r['stat'][-1]
        e['ep_pend'] = v
        e['pend_open'] = v - (e['pend_done'] + e['pend_drop'] + e['pend_free'])
    return f


m, o = broken('I2d', pend_eq(s3))
ok &= case('I2d edge: ep_pend = cl_smp + .. + cl_vo -> holds', m == [True])
m, o = broken('I2d', pend_eq(s3 + 1))
ok &= case('I2d edge: ep_pend = S3 sum + 1 -> violated', m == [False])
# I4
m, o = broken('I4: part = w_mipal', addx('w_other', 1))
ok &= case('I4: w_other + 1 -> violated', m == [False])
m, o = broken('I4: part_off', setx('part_off', 100))
ok &= case('I4 edge: part_off = part -> holds', m == [True])
m, o = broken('I4: part_off', setx('part_off', 101))
ok &= case('I4: part_off = part + 1 -> violated', m == [False])
m, o = broken('I4: part_off', setx('w_bytes', 5001))
ok &= case('I4: w_bytes > img_bytes -> violated', m == [False])
m, o = broken('I4: part_off', setx('img_bytes_unsync', 5000))
ok &= case('I4 edge: img_bytes_unsync = img_bytes -> holds', m == [True])
m, o = broken('I4: part_off', setx('img_bytes_unsync', 5001))
ok &= case('I4: img_bytes_unsync > img_bytes -> violated', m == [False])
m, o = broken('I4: in_pass', setx('in_pass_unsync', 40))
ok &= case('I4 edge: in_pass_unsync = in_pass -> holds', m == [True])
m, o = broken('I4: in_pass', setx('in_pass_unsync', 41))
ok &= case('I4: in_pass_unsync > in_pass -> violated', m == [False])
m, o = broken('I4: in_pass', setx('in_pass', 101))
ok &= case('I4: in_pass > part -> violated', m == [False])
# I3 per field
viol = []
for c, gs in I3_MAP:
    r = state()
    r['img'][0][c] += 1
    if mem_of(T.checks(r, M5), 'I3') != [False]:
        viol.append(c)
ok &= case('I3: +1 in any of the 27 class fields of a row -> violated (fields not caught: %s)' % viol, not viol and len(I3_MAP) == 27)
r = state()
r['img'][2]['ev'] += 1
ok &= case('I3: key=other is in the sum (+1 there -> violated)', mem_of(T.checks(r, M5), 'I3') == [False])
r = state()
r['stat'][-1]['tint_skip_ovf'] += 1
r['img'][2]['tint_skip'] += 1
ok &= case('I3: tint_skip = sum of the five tint_skip_* (ovf +1 on both sides -> holds)', mem_of(T.checks(r, M5), 'I3') == [True])
r = state()
r['img'] = [g for g in r['img'] if g['key'] != 'other']
ok &= case('I3: a missing key=other row (its share lost) -> violated', mem_of(T.checks(r, M5), 'I3') == [False])
# I6
m, o = broken('I6: tint_ep', setx('tint_ep', s3 + 3))
ok &= case('I6 edge: tint_ep = S3 sum + pend_done -> holds (I3 aside)', m == [True])
m, o = broken('I6: tint_ep', setx('tint_ep', s3 + 4))
ok &= case('I6: tint_ep = S3 sum + pend_done + 1 -> violated', m == [False])
m, o = broken('I6: tint_ep', setx('tint_bad', 1))
ok &= case('I6: tint_bad 1 -> violated', m == [False])


def row_set(i, **kw):
    def f(r):
        r['img'][i].update(kw)
    return f


m, o = broken('I6 (=2)', row_set(0, tint_bytes=600))
ok &= case('I6 (=2) edge: class tint_bytes = lost_bytes + lost_pend_bytes -> holds', m == [True])
m, o = broken('I6 (=2)', row_set(1, tint_bytes=301))
ok &= case('I6 (=2): class tint_bytes > lost + lost_pend by 1 -> violated', m == [False])
m, o = broken('I6 (=2)', row_set(2, tint_bytes=101))
ok &= case('I6 (=2): the key=other row is checked too', m == [False])
m, o = broken('I6: tint_rb_req = ', addx('tint_rb0_nofmt', 1))
ok &= case('I6: rb0_nofmt + 1 -> tint_rb_req equation violated', m == [False])
m, o = broken('I6: tint_rb0_ok', addx('tint_rb1_none', 1))
ok &= case('I6: rb1_none + 1 -> tint_rb0_ok equation violated', m == [False])
m, o = broken('I6: tint_rb0_ok', setx('tint_rb1_bad', 1))
ok &= case('I6: rb1_bad 1 -> violated (also Z)', m == [False])


def rbreq(v, ntint):
    def f(r):
        e = r['stat'][-1]
        e['tint_rb_req'] = v
        e['tint_rb0_none'] = v - e['tint_rb0_ok']
        r['img'][0]['tint_ep'] = 10 if ntint >= 1 else 0
        r['img'][1]['tint_ep'] = 5 if ntint >= 2 else 0
        r['img'][2]['tint_ep'] = ntint - 2 if ntint > 2 else 0
        tot = sum(g['tint_ep'] for g in r['img'])
        e['tint_ep'] = tot
    return f


m, o = broken('I6: tint_rb_req <=', rbreq(8, 2))
ok &= case('I6 edge: tint_rb_req = K x 2 classes (8) -> holds', m == [True])
m, o = broken('I6: tint_rb_req <=', rbreq(9, 2))
ok &= case('I6: tint_rb_req = 9 > 4 x 2 -> violated', m == [False])
m, o = broken('I6: tint_rb_req <=', rbreq(12, 3))
ok &= case('I6: key=other with tint_ep 1 counts as one more class (12 <= 4 x 3) -> holds', m == [True])
# I8 / Z
m, o = broken('I8', setx('lock_bad', 1))
ok &= case('I8: lock_bad 1 -> violated (also Z)', m == [False] and any(a.startswith('Z:') for a in o))
m, o = broken('I8', setx('ep_bad', 1))
ok &= case('I8: ep_bad 1 -> violated', m == [False])
per = [dict(base_stat(), when='periodic', tint_rb0_bad=1)]
ok &= case('Z: an invariant nonzero on a PERIODIC line (exit clean) -> violated', mem_of(T.checks(state(per=per), M5), 'Z:') == [False])
ok &= case('Z: all invariants 0 on every line -> holds', mem_of(ch0, 'Z:') == [True])
# N
ok &= case('N: mode=1 -> mode member violated', mem_of(T.checks(state(mode=[(1, 'all', 4)]), M5), 'N: exactly') == [False])
ok &= case('N: cls=1 (a class list) -> violated', mem_of(T.checks(state(mode=[(2, '1', 4)]), M5), 'N: exactly') == [False])
ok &= case('N: two mode lines -> violated', mem_of(T.checks(state(mode=[PLAN_MODE, PLAN_MODE]), M5), 'N: exactly') == [False])
ok &= case('N: no mode line -> violated', mem_of(T.checks(state(mode=[]), M5), 'N: exactly') == [False])
m, o = broken('N (I7', setx('tint_skip_cls', 1))
ok &= case('N (I7, cls=all): tint_skip_cls 1 -> violated', m == [False])
# E
r = state()
r['stat'].append(dict(base_stat(), when='exit'))
ok &= case('E: two T188Stat exit lines -> violated, identities not evaluated', mem_of(T.checks(r, M5), 'E: exactly') == [False]
      and mem_of(T.checks(r, M5), 'I1-I8') == [False])
r = state()
r['stat'] = [dict(base_stat(), when='periodic')]
ok &= case('E: no exit line (killed) -> violated', mem_of(T.checks(r, M5), 'E: exactly') == [False])
r = state(t9=[t109('periodic')])
ok &= case('E: no T109Stat exit line -> violated and I9 not evaluated', mem_of(T.checks(r, M5), 'E: exactly') == [False]
      and mem_of(T.checks(r, M5), 'I9: the T109Stat exit line exists') == [False])
r = state()
r['img'].append(dict(r['img'][2]))
ok &= case('E: key=other twice -> violated', mem_of(T.checks(r, M5), 'E: T188Img') == [False])
r = state()
r['img'] = []
ok &= case('E: no T188Img row -> violated', mem_of(T.checks(r, M5), 'E: T188Img') == [False])
r = state()
r['img_bad'] = 1
ok &= case('E: one unparsable T188Img line -> violated', mem_of(T.checks(r, M5), 'E: 0 unparsable') == [False])
# I5
ok &= case('I5: holds with the M5W2 exit total', mem_of(ch0, 'I5') == [True])
ok &= case('I5: M5W2 total when=periodic -> violated', mem_of(T.checks(state(), dict(M5, when='periodic')), 'I5') == [False])
ok &= case('I5: no M5W2 total -> violated', mem_of(T.checks(state(), None), 'I5') == [False])
ok &= case('I5: part != inv_part_src -> violated', mem_of(T.checks(state(), dict(M5, inv_part_src=101)), 'I5') == [False])
ok &= case('I5: part_off != inv_off with inv_part = inv_part_src -> violated', mem_of(T.checks(state(), dict(M5, inv_off=8)), 'I5') == [False])
ok &= case('I5: part_off != inv_off with inv_part != inv_part_src -> the member does not apply (holds)',
      mem_of(T.checks(state(), dict(M5, inv_off=8, inv_part=150)), 'I5') == [True])
ok &= case('I5: m5_on=False -> no I5 member', mem_of(T.checks(state(), None, m5_on=False), 'I5') == [])
# I9
for kw, want, nm in ((dict(zx_narrow=20), True, 'zx_narrow = zx_d32 edge'), (dict(zx_narrow=21), False, 'zx_narrow > zx_d32'),
                     (dict(zx_d32=101, zx_narrow=5), False, 'zx_d32 > d32'), (dict(bias_d32=100), True, 'bias_d32 = d32 edge'),
                     (dict(bias_narrow=11), False, 'bias_narrow > bias_d32'), (dict(bias_d32=101), False, 'bias_d32 > d32'),
                     (dict(ovr_vpc=3), True, 'ovr_vpc = ovr_w edge'), (dict(ovr_vpc=4), False, 'ovr_vpc > ovr_w')):
    r = state(t9=[t109('exit', **kw)])
    ok &= case('I9: %s -> %s' % (nm, 'holds' if want else 'violated'), mem_of(T.checks(r, M5), 'I9') == [want])

# ---- edges added for the mutants (mut_t188.py) ------------------------------------------------------------------------------------
r = state()
r['mode_bad'] = 1
ok &= case('N: one unparsable mode line next to a good one -> N violated', mem_of(T.checks(r, M5), 'N: exactly') == [False])
r = state()
r['img'].append(dict(r['img'][0], when='periodic'))
ok &= case('E: a T188Img row with when=periodic -> violated', mem_of(T.checks(r, M5), 'E: T188Img') == [False])
for fld in ('stat_bad', 't109_bad', 'mode_bad'):
    r = state()
    r[fld] = 1
    ok &= case('E: one unparsable line (%s) -> violated' % fld, mem_of(T.checks(r, M5), 'E: 0 unparsable') == [False])


def unk_moved(r):
    r['stat'][-1]['part_unk'] = 1
    r['stat'][-1]['part_st'] -= 1


m, o = broken('I1', unk_moved)
ok &= case('I1: part_unk 1 with the sum kept -> violated by the member part_unk = 0', m == [False])
m, o = broken('I4: part_off', setx('w_bytes', 5000))
ok &= case('I4 edge: w_bytes = img_bytes -> holds', m == [True])


def in_pass_part(r):
    r['stat'][-1]['in_pass'] = 100


m, o = broken('I4: in_pass', in_pass_part)
ok &= case('I4 edge: in_pass = part -> holds', m == [True])


def rb0bad(r):
    r['stat'][-1]['tint_rb0_bad'] = 1
    r['stat'][-1]['tint_rb0_none'] -= 1


m, o = broken('I6: tint_rb0_ok', rb0bad)
ok &= case('I6: rb0_bad 1 with tint_rb_req kept -> the rb0_ok member violated', m == [False])
r = state()
r['img'][1]['tint_rb0_ok'] = 0
r['img'][2]['tint_rb0_ok'] += 1
ok &= case('class rows: a class with rb0_ok 0 -> readback not alive', T.class_rows(r)[1]['readback_alive'] is False)

def st_to_copy(r):
    r['stat'][-1]['part_st'] -= 1
    r['stat'][-1]['part_copy'] += 1


m, o = broken('I1', st_to_copy)
ok &= case('I1: one event moved from part_st to part_copy (sum kept) -> holds', m == [True])
m, o = broken('I6 (=2)', row_set(1, lost_bytes=200, lost_pend_bytes=100, tint_bytes=300))
ok &= case('I6 (=2) edge: tint_bytes = lost_bytes + lost_pend_bytes with lost_pend 100 -> holds', m == [True])


def rb1bad_kept(r):
    r['stat'][-1]['tint_rb1_bad'] = 1
    r['stat'][-1]['tint_rb1_none'] -= 1


m, o = broken('I6: tint_rb0_ok', rb1bad_kept)
ok &= case('I6: rb1_bad 1 with the rb0_ok equation kept -> violated by rb1_bad = 0', m == [False])

# ---- line forms -----------------------------------------------------------------------------------------------------------------------
e = base_stat()
sl = ('[12][00:01:02.003] T188Stat: when=exit ' + ' '.join('%s=%d' % (k, e[k]) for k in STAT) + '\r\n').encode()
im = img_rows(e)
il = ('T188Img: when=exit key=00000000000000aa ' + ' '.join('%s=%d' % (k, im[0][k]) for k in HEAD) + ' ' +
      ' '.join('%s=%d' % (k, im[0][k]) for k in CLS) + '\n').encode()
ol = ('T188Img: when=exit key=other ' + ' '.join('%s=%d' % (k, im[2][k]) for k in CLS) + '\n').encode()
tl = ('T109Stat: when=exit ' + ' '.join('%s=%d' % (k, t109('exit')[k]) for k in T109) + '\n').encode()
r = T.empty()
for ln in (b'T188: mode=2 cls=all k=4\n', sl, il, ol, tl, b'T188: mode=x\n', sl.replace(b' tint_rb1_none=', b' tint_rb1_nonx='),
           il[:60] + b'\n', b'T109Stat: when=exit d32=1\n', sl.replace(b'part_st=', b'part_fill=', 1),
           b'GuestOut: nothing T18 here\n'):
    T.parse_line(ln, r)
ok &= case('parse: the 70-field exit line with a log prefix and CRLF', len(r['stat']) == 1 and r['stat'][0] == dict(e, when='exit'))
ok &= case('parse: a class row with its 10 head fields and 27 class fields', len(r['img']) == 2 and r['img'][0]['key'] == '00000000000000aa'
      and r['img'][0]['fmt'] == 1 and r['img'][0]['vol'] == 10 and r['img'][0]['tint_rb1_bad'] == im[0]['tint_rb1_bad'])
ok &= case('parse: the key=other row has no head fields', r['img'][1]['key'] == 'other' and 'fmt' not in r['img'][1])
ok &= case('parse: the T109Stat line, 10 fields in order', r['t109'] == [t109('exit')])
ok &= case('parse: mode line parsed once, the broken one is unparsable', r['mode'] == [PLAN_MODE] and r['mode_bad'] == 1)
ok &= case('parse: a renamed field, fields out of order -> unparsable (2 T188Stat)', r['stat_bad'] == 2)
ok &= case('parse: a truncated T188Img line -> unparsable', r['img_bad'] == 1)
ok &= case('parse: a short T109Stat line -> unparsable', r['t109_bad'] == 1)
ok &= case('parse: the field order is the code order (70 / 27 / 10 / 10)', len(STAT) == 70 and len(CLS) == 27 and len(T109) == 10
      and len(HEAD) == 10 and STAT[0] == 'part' and STAT[-1] == 'tint_rb1_none' and CLS[-1] == 'tint_rb1_bad'
      and T109[-1] == 'narrow_cd')

# ---- class choice / class rows / open ---------------------------------------------------------------------------------------------
c0 = T.class_choice(state())
ok &= case('choice: rows 600 then 300 of total 1000 -> 2 classes, share 0.9 >= 0.8; other never chosen',
      c0['chosen'] == ['00000000000000aa', '00000000000000bb'] and abs(c0['share'] - 0.9) < 1e-9 and c0['reached'])


def chs(vals, other=0):
    e = base_stat()
    e['lost_bytes'] = sum(vals) + other
    e['lost_pend_bytes'] = 0
    rows = []
    for i, v in enumerate(vals):
        d = dict(when='exit', key='%016x' % (0x10 + i), ev=100 - i)
        d.update(dict((k, 0) for k in CLS if k != 'ev'), lost_bytes=v)
        d.update(dict((k, 1) for k in HEAD))
        rows.append(d)
    o = dict(when='exit', key='other', **dict((k, 0) for k in CLS))
    o['lost_bytes'] = other
    rows.append(o)
    r = T.empty()
    r['stat'] = [dict(e, when='exit')]
    r['img'] = rows
    return T.class_choice(r)


c = chs([800, 100, 100])
ok &= case('choice edge: the first class reaches exactly 0.8 -> 1 class, reached', c['chosen'] == ['%016x' % 0x10] and c['reached'])
c = chs([799, 100, 101])
ok &= case('choice: 0.799 -> a second class (by bytes: 101 before 100)', c['chosen'] == ['%016x' % 0x10, '%016x' % 0x12] and c['reached'])
c = chs([300, 300, 300, 100])
ok &= case('choice: 3 classes needed -> stops at 2, share 0.6 not reached, rest named', len(c['chosen']) == 2 and not c['reached']
      and c['rest_bytes'] == 400 and 'not determined' in c['note'])
c = chs([10, 10], other=980)
ok &= case('choice: key=other carries 98 % -> only real classes, share 0.02 not reached', len(c['chosen']) == 2 and not c['reached'])
c = chs([0, 0])
ok &= case('choice: scene sum 0 -> no class', c['chosen'] == [] and c['total'] == 0 and 'scene sum 0' in c['note'])
c = chs([50, 50])
ok &= case('choice: tie of bytes -> the larger ev first (key 0x10)', c['chosen'][0] == '%016x' % 0x10)
cr = T.class_rows(state())
ok &= case('class rows: readback alive only for rows with rb0_ok >= 1 and global rb0_bad = rb1_bad = 0; key=other never alive',
      [x['readback_alive'] for x in cr] == [x['rb0_ok'] >= 1 and x['key'] != 'other' for x in cr])
r = state()
r['stat'][-1]['tint_rb1_bad'] = 1
ok &= case('class rows: a global rb1_bad 1 -> no class alive', not any(x['readback_alive'] for x in T.class_rows(r)))
ok &= case('class rows: coverage 300 / 600 = 0.5 -> cover >= 0.5 (edge)', cr[0]['coverage'] == 0.5 and cr[0]['cover_ge_05'])
r = state()
r['img'][0]['tint_bytes'] = 299
ok &= case('class rows: coverage 299 / 600 -> below 0.5', not T.class_rows(r)[0]['cover_ge_05'])
r = state()
r['img'][0]['lost_bytes'] = 0
ok &= case('class rows: lost 0 -> coverage none, not >= 0.5', T.class_rows(r)[0]['coverage'] is None and not T.class_rows(r)[0]['cover_ge_05'])
ok &= case('open: read at ep_bad = 0', T.open_field(base_stat()) == 8)
ok &= case('open: not read at ep_bad 1 (item 788 (g) N2)', T.open_field(dict(base_stat(), ep_bad=1)) is None)
ok &= case('open: no exit line -> not read', T.open_field(None) is None)

# ---- T109 rows (item 791 (v), 789 (g)(3)) ------------------------------------------------------------------------------------------
def tr(seq):
    r = T.empty()
    r['t109'] = [t109(w, zx_narrow=10, zx_narrow_vi=10 - dv, bias_narrow=2, bias_narrow_vi=2 - db) for w, dv, db in seq]
    return T.t109_rows(r)


ok &= case('791: one exit line with difference 1 -> not counted', tr([('exit', 1, 0)])['zx_part_791'] is False)
ok &= case('791: difference first at exit (periodic 0) -> not counted', tr([('periodic', 0, 0), ('exit', 1, 0)])['zx_part_791'] is False)
ok &= case('791: periodic 1, exit 1 -> counted', tr([('periodic', 1, 0), ('exit', 1, 0)])['zx_part_791'] is True)
ok &= case('791: periodic 1, later periodic 0, exit 1 -> not counted', tr([('periodic', 1, 0), ('periodic', 0, 0), ('exit', 1, 0)])['zx_part_791'] is False)
ok &= case('791: periodic 0, periodic 1, exit 2 -> counted', tr([('periodic', 0, 0), ('periodic', 1, 0), ('exit', 2, 0)])['zx_part_791'] is True)
ok &= case('791: periodic 1, exit 0 -> not counted', tr([('periodic', 1, 0), ('exit', 0, 0)])['zx_part_791'] is False)
ok &= case('791: periodic 1 without an exit line -> not counted', tr([('periodic', 1, 0), ('periodic', 1, 0)])['zx_part_791'] is False)
ok &= case('791 form for bias: periodic 1, exit 1 -> counted; zx 0 -> not', (lambda q: q['bias_part_791'] is True and q['zx_part_791'] is False)(
    tr([('periodic', 0, 1), ('exit', 0, 1)])))
q = tr([('exit', 0, 0)])
ok &= case('789 (g)(3): zx_narrow = zx_narrow_vi >= 1 on the exit line -> zx_eq_all', q['zx_eq_all'] is True)
ok &= case('789 (g)(3): difference 1 -> not zx_eq_all', tr([('exit', 1, 0)])['zx_eq_all'] is False)
r = T.empty()
r['t109'] = [t109('exit', zx_narrow=0, zx_narrow_vi=0)]
ok &= case('789 (g)(3): zx_narrow 0 -> not zx_eq_all (form (4))', T.t109_rows(r)['zx_eq_all'] is False and T.t109_rows(r)['zx_narrow_ge1'] is False)
ok &= case('T109 rows: armed d32 >= 1, ovr_vpc >= 1 flags of the exit line', q['armed_d32'] and q['ovr_vpc_ge1'] and q['i9'])
r = T.empty()
r['t109'] = [t109('exit', narrow_cd=5)]
ok &= case('T109 reference: narrow_cd > zx_vi + bias_vi -> reference flag false (not a stop)', T.t109_rows(r)['vi_ref']['cd_le'] is False
      and mem_of(T.checks(state(t9=r['t109']), M5), 'I9') == [True])
c = chs([500, 0], other=500)
ok &= case('choice: a zero row after a class ends the choice (share 0.5, one class)', c['chosen'] == ['%016x' % 0x10] and not c['reached'])
print('cases %d' % N_CASES[0])
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
