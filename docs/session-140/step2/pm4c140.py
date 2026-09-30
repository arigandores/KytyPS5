"""pm4c140 - the scorer of the PM4 per-opcode census of session 140 (ROADMAP s122 items 210 (e)(3)-(6), 212 (b)-(k),
213 (b)-(d); design docs/session-140/design140.md rev 1 (56a77d9e...), review docs/session-140/review140.md (6ed3adff...)).
Session 140 step 2, HPP-268, Harness Engineer.  ASCII output only (item 175 (v), process 3).

The census: build 05431dad at the arm-0 knob string of kp137 (the gate file gates_base.txt, no schedule), Sky Garden, pin,
4 x 300 s with KYTY_PM4_TRACE = 0, 1, 1, 0 (pm4c140a..pm4c140d, one attempt each).  The instrument is MEASUREMENT ONLY
(item 65 (v)): every level is [c] of one run WITH the instrument - not a gain, not a ceiling, not a price; NAMED is a target
of the s141 selection, not a candidate.

THE ROW (item 212 (v)): FrameTrace:, FrameTrace-draw:, FrameTrace-x: of one n (each exactly once) and a FrameTrace-pm4:
line after that FrameTrace-x: and before the next FrameTrace: line.  THE WINDOW W of a run: full rows with n >= 1800 and
n < the last full row of the log; a NEW row has bda_scan <= 300 (items 40 (e)(1), 184 (b)).  Every mean is over the NEW
rows of W.  A site value is truncated per flip, so raw* = U + 0.5 us for every site printed in the row (item 212 (zh)).

PER RUN (k): c_k (item 212 (d)): candidates = the sites of the set E (O(1) handlers by the map) with mean C >= 1000/frame,
plus E as a whole when its mean sum C >= 1000/frame; c_s = 1000 * sum raw* / sum C (ns); c_k = min; none -> IF5; c_k out of
[3, 100] ns -> IF5b; c_k > 40 ns -> the note c-HIGH (item 213 (v)).
Candidate g (10, item 212 (b), (g)): L_g,k = mean_r [ sum_g raw* - c_k * sum_g C / 1000 - A_g,r ] with the deductions
    REG, MEM, SYNC, STATE 0;  MM_out a_hold_us + a_wait_us (exact);  DRAW_out a_hold_us - mh_disp_us + a_wait_us;
    DISP_out mh_disp_us + a_wait_us;  EOP_adj (pl_eop_ns + pl_bar_ns + pl_sub_ns)/1000;  WAITFLIP_adj pl_sub_ns/1000;
    FLIP_low mh_pres_us + mh_pres_wait_us (item 212 (b)).
The upper form U_g (item 213 (b), RC1 (a)): c = 3 ns and the minimal deductions (MM_out the same; DRAW_out a_hold - mh_disp;
DISP_out mh_disp; EOP_adj pl_eop + pl_bar; WAITFLIP_adj and FLIP_low 0).  Beside: L at c = 22.9 and c = 0, 2SE by blocks
of 90 rows, n_g/frame and c_k * n_g / 1000 (RC2 of s139), the break-even c*_g (mean = 400, min = 325; item 213 (v)).
IDENTITIES (runs with 1; item 212 (z)): g = 1000 * (pl_proc - S_pm4 - (pl_cmd + pl_pref + pl_gc + pl_sub) - prefetch* -
stream-prefetch*) / pl_cmd_n in [-1000 * pl_sub / pl_cmd_n - 0.5; 250] ns (IF6); F = pl_cmd_n - sum C(op*, nop*) in
[-0.5 %; 50 %] of pl_cmd_n (IF7); M = sum_MIX_MM raw* - (a_hold_us + a_wait_us) >= -5 us (IF8); H = a_hold_n - sum C(S1)
>= -0.5 % a_hold_n and, when C(op2c, op38) = 0 in every row, |H| <= 0.5 % a_hold_n (IF9).  The identities are GROSS (RC9):
the lower edge of g catches a double count >= ~1 ms [I], F a loss >= 50 %; the levels stand on the map and IF1-IF5, IF10.
INSTRUMENT_FAIL (any run): IF0 environment/build (json: build 05431dad, KYTY_PM4_TRACE of the tag, no KYTY_GATE_SCHEDULE /
ABBA, pin 1, no checkpoints, no video, the gate words = the base; log: the Gate: lines = the arm-0 set of kp137, no
GateArm:; the seal sha in the json of a registered call); IF1 an op*/nop* name in a run with 0 (any FrameTrace-pm4: line);
IF2 < 99 % of the NEW window rows of a run with 1 carry an op*/nop* name; IF3 a name outside the 56 of the map (any line);
IF4 C(op3f) > 0 in W of a run with 1; IF5 / IF5b; IF6-IF9; IF10 > 1 % of the NEW rows with FrameTrace:, -draw:, -x: in the n
range of a run with 1 lack the FrameTrace-pm4: line; IF11 a field of pl_proc_ns, pl_cmd_ns, pl_cmd_n, a_hold_us, a_wait_us,
a_hold_n, mh_disp_us, mh_pres_us, mh_pres_wait_us missing in a NEW window row (item 212 (b)).  IF2, IF4-IF10 are judged on a
run with 1 that has at least one NEW window row (a run with 0 such rows is DEBT, not IF).
DEBT (items 210 (e)(4), 212 (e)): a run with < 4000 NEW window rows is DEBT; a run with 1 DEBT -> the outcome DEBT; a run
with 0 DEBT does not change the outcome (then the price reference is not printed).
OUTCOME: any IF -> INSTRUMENT_FAIL; else DEBT; else NAMED when a candidate has (L_b + L_c)/2 >= 400 AND min(L_b, L_c) >= 325;
then LEVEL-INFLATED (item 213 (g)): X = mean_bc(Sigma) - mean(D0 of the runs with 0 that are not DEBT), Sigma_r = sum of
all op*/nop* raw* - c_k * sum C / 1000 - (a_hold_us + a_wait_us) - (pl_eop + pl_bar + pl_sub)/1000 (the exact deductions,
the ones D0 makes), D0_r = pl_proc - a_hold - a_wait - (pl_cmd + pl_gc + pl_sub + pl_eop + pl_bar + pl_pref) - prefetch -
stream-prefetch (the formula of review140 section 1, printed U without +0.5), 2SE by rows; X - 2SE > 0 -> LEVEL-INFLATED X and
a NAMED candidate keeps NAMED only when L_g - X passes both thresholds (X charged whole), else it passed only by bound; no
run with 0 left -> X not evaluable, no consequence.  No NAMED -> SPREAD (by bound) when a candidate's U_g passes both
thresholds or a candidate passed only by bound (item 213 (b), (g)); else SPREAD.  Labels: NAMED on MM_out / DRAW_out /
DISP_out -> "with arm-0 instrument" (RC3); on WAITFLIP_adj / SYNC / FLIP_low -> "wait class" (item 212 (g)).

MODES (ascii stdout; --out writes json):
    python pm4c140.py --tag pm4c140<x> [--dir D] [--out F]   the per-call form of the chain: MASKED (no level)
    python pm4c140.py --smoke pm4s140 [--dir D] [--out F]    the smoke of step 2: MASKED (RC7 of review140)
    python pm4c140.py --all [--dir D] [--out F]               the census reading over the 4 runs (step 3)
    python pm4c140.py --check-seal --tag pm4c140<x> [--dir D] the pre-seal check of the chain
    exit 0 read / check passed, 1 not read (IF, DEBT, missing input) / check failed, 2 usage or scorer error.
"""
import hashlib
import json
import math
import os
import re
import sys

ROOT = 'C:/kyty/s140'
PRED_SHA = None           # pred/01_pm4c140.md - filled at the seal (step 2)
PRED_BYTES = None         # pred/01_pm4c140.md - filled at the seal (step 2)
PRED_NAME = 'pred/01_pm4c140.md'
SEALS_NAME = 'SEALS140.txt'
CHAIN_NAME = 'go140a.sh'
BUILD_SHA = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
BASE_SHA = '573ae9d2f24944c4fa92a14070645e3fe5b21bd6ee3365502e6ba768c0087fbc'
SEQ = ('pm4c140a', 'pm4c140b', 'pm4c140c', 'pm4c140d')
SMOKE = 'pm4s140'
TRACE = {'pm4c140a': '0', 'pm4c140b': '1', 'pm4c140c': '1', 'pm4c140d': '0', 'pm4s140': '1'}
ON = ('pm4c140b', 'pm4c140c')
OFF = ('pm4c140a', 'pm4c140d')
N_MIN = 1800
BDA_NEW = 300
MIN_NEW_ROWS = 4000
NAMED_MEAN = 400.0
NAMED_EACH = 325.0
C_LO = 3.0
C_HI = 100.0
C_HIGH = 40.0
C_CMP = 22.9
E_MIN = 1000.0
TRUNC = 0.5
G_HI = 250.0
G_LO_PAD = 0.5
F_LO = 0.005
F_HI = 0.5
M_MIN = -5.0
H_TOL = 0.005
P1_MIN = 0.99
IF10_MAX = 0.01
BLOCK = 90
KNOBS = ('mutsite=1', 'plkstat=1', 'bindlap=1', 'pathlap=1', 'rbcen=1')
IF11_FIELDS = ('pl_proc_ns', 'pl_cmd_ns', 'pl_cmd_n', 'a_hold_us', 'a_wait_us', 'a_hold_n', 'mh_disp_us', 'mh_pres_us',
               'mh_pres_wait_us')
FATAL = b'AsyncPipelines: skipped draw'
MM_PRICE_NS = 20.0        # RC3 of review140: the arm-0 marks of one MutexMark hold outside a_hold/a_wait [I]

# The map (C:/kyty/s140/step0/opmap140.tsv, sha256 0492b2d0...): name -> (class, group, E)
MAP = {
    'op11': ('OUT', 'STATE', 1), 'op12': ('OUT', 'STATE', 0), 'op13': ('OUT', 'STATE', 1),
    'op15': ('MIX_MM', 'DISPMM', 0), 'op16': ('MIX_MM', 'DISPMM', 0), 'op20': ('OUT', 'SYNC', 0),
    'op22': ('OUT', 'SYNC', 0), 'op24': ('MIX_MM', 'DRAWMM', 0), 'op25': ('MIX_MM', 'DRAWMM', 0),
    'op26': ('OUT', 'STATE', 1), 'op27': ('MIX_MM', 'DRAWMM', 0), 'op2a': ('OUT', 'STATE', 1),
    'op2c': ('MIX_MM', 'DRAWMM', 0), 'op2d': ('MIX_MM', 'DRAWMM', 0), 'op2f': ('OUT', 'STATE', 1),
    'op35': ('MIX_MM', 'DRAWMM', 0), 'op37': ('OUT', 'MEM', 0), 'op38': ('MIX_MM', 'DRAWMM', 0),
    'op3a': ('MIX_MM', 'DRAWMM', 0), 'op3c': ('OUT', 'SYNC', 0), 'op3f': ('NEST', 'NEST', 0),
    'op40': ('OUT', 'MEM', 0), 'op42': ('OUT', 'STATE', 1), 'op46': ('OUT', 'EOP', 0),
    'op47': ('OUT', 'EOP', 0), 'op48': ('OUT', 'EOP', 0), 'op50': ('OUT', 'MEM', 0),
    'op58': ('OUT', 'STATE', 1), 'op59': ('OUT', 'SYNC', 0), 'op63': ('OUT', 'REG', 0),
    'op64': ('OUT', 'REG', 0), 'op69': ('OUT', 'REG', 0), 'op76': ('OUT', 'REG', 0),
    'op79': ('OUT', 'REG', 0), 'op7a': ('OUT', 'REG', 0), 'op81': ('OUT', 'MEM', 0),
    'op83': ('OUT', 'MEM', 0), 'op84': ('OUT', 'STATE', 1), 'op85': ('OUT', 'STATE', 1),
    'op86': ('OUT', 'SYNC', 0), 'op88': ('OUT', 'SYNC', 0), 'op8e': ('OUT', 'MEM', 0),
    'op93': ('OUT', 'SYNC', 0), 'op9f': ('OUT', 'REG', 0),
    'nop00': ('MIX_PF', 'FLIP', 0), 'nop06': ('OUT', 'WAITFLIP', 0), 'nop09': ('OUT', 'STATE', 0),
    'nop0b': ('OUT', 'STATE', 0), 'nop0c': ('OUT', 'STATE', 0), 'nop14': ('OUT', 'STATE', 1),
    'nop17': ('MIX_PF', 'FLIP', 0), 'nop18': ('OUT', 'EOP', 0), 'nop1a': ('OUT', 'STATE', 0),
}
NONOP = ('gc', 'prefetch', 'stream-prefetch')
S1 = ('op27', 'op35', 'op3a', 'op2d', 'op24', 'op25', 'op15', 'op16')
MULTI = ('op2c', 'op38')
GROUPS = ('REG', 'DRAWMM', 'DISPMM', 'EOP', 'MEM', 'SYNC', 'WAITFLIP', 'STATE', 'FLIP', 'NEST')
# candidate -> (groups, class label)
CANDS = {
    'REG': (('REG',), ''),
    'MM_out': (('DRAWMM', 'DISPMM'), 'with arm-0 instrument'),
    'DRAW_out': (('DRAWMM',), 'with arm-0 instrument'),
    'DISP_out': (('DISPMM',), 'with arm-0 instrument'),
    'EOP_adj': (('EOP',), ''),
    'MEM': (('MEM',), ''),
    'SYNC': (('SYNC',), 'wait class'),
    'WAITFLIP_adj': (('WAITFLIP',), 'wait class'),
    'STATE': (('STATE',), ''),
    'FLIP_low': (('FLIP',), 'wait class'),
}
CAND_ORDER = ('REG', 'MM_out', 'DRAW_out', 'DISP_out', 'EOP_adj', 'MEM', 'SYNC', 'WAITFLIP_adj', 'STATE', 'FLIP_low')
# RC3 of review140: the instrument marks inside a candidate by the code (file:line, per packet)
MARKS = {
    'MM_out': 'renderDraw.cpp:4971-4974 / renderCompute.cpp:412-415 head NowNs; frameStats.h:2975-2978 tail NowNs + Add '
              '(~MutexMark); graphicsRun.cpp:3022/:3368/:3299 FrameStats::Scope - one set per hold (a_hold_n)',
    'DRAW_out': 'as MM_out, draw holds',
    'DISP_out': 'as MM_out, dispatch holds',
    'EOP_adj': 'frameStats.h:3143-3172 PathSpan pl_eop/pl_bar/pl_sub inside nop18/op46 (pathlap=1) - one pair per span',
    'WAITFLIP_adj': 'frameStats.h:3143-3172 PathSpan pl_sub inside nop06 (pathlap=1) - one pair per span',
}

FIELD = re.compile(rb'(?:^|\s)([A-Za-z_]\w*)=(-?\d+)')
SITE = re.compile(rb'(?:^|\s)([\w\-\+]+)=(\d+)/(\d+)')
PRE_M = b'FrameTrace: '
PRE_D = b'FrameTrace-draw: '
PRE_X = b'FrameTrace-x: '
PRE_PM4 = b'FrameTrace-pm4:'
PRE_SUB = b'FrameTrace-submit:'
PRE_GATE = b'Gate: '
PRE_ARM = b'GateArm:'


def fsha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 22), b''):
            h.update(block)
    return h.hexdigest()


def body_sha(data):
    """sha256 of the scorer text with the two seal lines in their unfilled form (the seal names it)."""
    t = data.decode('utf-8')
    t = re.sub(r"^PRED_SHA = .*$", "PRED_SHA = None           # pred/01_pm4c140.md - filled at the seal (step 2)", t,
               count=1, flags=re.M)
    t = re.sub(r"^PRED_BYTES = .*$", "PRED_BYTES = None         # pred/01_pm4c140.md - filled at the seal (step 2)", t,
               count=1, flags=re.M)
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


# --- the log --------------------------------------------------------------------------------------------------------
def parse_log(path):
    """One pass in binary.  Returns dict(rows=[row...] in the order of their FrameTrace: line, gates=[...], arms=int,
    fatal=int, names_all=set of pm4 names on any line, orphans=int, dups=int)."""
    by_n = {}
    order = []
    dups = set()
    gates = []
    arms = 0
    fatal = 0
    names_all = set()
    orphans = 0
    last_x = None
    with open(path, 'rb') as stream:
        for line in stream:
            if line.startswith(b'FrameTrace'):
                if line.startswith(PRE_M):
                    last_x = None
                    f = dict((k.decode(), int(v)) for k, v in FIELD.findall(line[len(PRE_M):]))
                    n = f.get('n')
                    if n is None:
                        continue
                    if n in by_n and by_n[n].get('m') is not None:
                        dups.add(n)
                        continue
                    r = by_n.setdefault(n, dict(n=n, m=None, d=None, x=None, pm4=None, sub=None))
                    r['m'] = f
                    order.append(n)
                elif line.startswith(PRE_D) or line.startswith(PRE_X):
                    key, pre = ('d', PRE_D) if line.startswith(PRE_D) else ('x', PRE_X)
                    f = dict((k.decode(), int(v)) for k, v in FIELD.findall(line[len(pre):]))
                    n = f.get('n')
                    if n is None:
                        continue
                    r = by_n.setdefault(n, dict(n=n, m=None, d=None, x=None, pm4=None, sub=None))
                    if r[key] is not None:
                        dups.add(n)
                        continue
                    r[key] = f
                    if key == 'x':
                        last_x = n
                elif line.startswith(PRE_PM4) or line.startswith(PRE_SUB):
                    key, pre = ('pm4', PRE_PM4) if line.startswith(PRE_PM4) else ('sub', PRE_SUB)
                    sites = {}
                    for k, u, c in SITE.findall(line[len(pre):]):
                        sites[k.decode()] = (int(u), int(c))
                    if key == 'pm4':
                        names_all.update(sites)
                    if last_x is None or by_n[last_x][key] is not None:
                        if key == 'pm4':
                            orphans += 1
                        continue
                    by_n[last_x][key] = sites
                continue
            if line.startswith(PRE_GATE):
                m = re.match(rb'Gate: (\S+=\S+)', line)
                if m:
                    gates.append(m.group(1).decode('ascii', 'replace'))
            elif line.startswith(PRE_ARM):
                arms += 1
            elif FATAL in line:
                fatal += 1
    rows = []
    for n in order:
        if n in dups:
            continue
        r = by_n[n]
        merged = {}
        for key in ('m', 'd', 'x'):
            for k, v in (r[key] or {}).items():
                merged.setdefault(k, v)
        rows.append(dict(n=n, has3=r['m'] is not None and r['d'] is not None and r['x'] is not None,
                         pm4=r['pm4'], sub=r['sub'], f=merged))
    return dict(rows=rows, gates=gates, arms=arms, fatal=fatal, names_all=names_all, orphans=orphans, dups=len(dups))


def window(parsed):
    """(W: the NEW full rows of the window, rows3: the NEW rows with the three lines in the n range, last_full_n)."""
    full = [r for r in parsed['rows'] if r['has3'] and r['pm4'] is not None]
    if not full:
        return [], [], None
    last = max(r['n'] for r in full)
    rng = [r for r in parsed['rows'] if r['has3'] and N_MIN <= r['n'] < last and r['f'].get('bda_scan', 10 ** 12) <= BDA_NEW]
    w = [r for r in rng if r['pm4'] is not None]
    return w, rng, last


def raw_star(sites, name):
    uc = sites.get(name)
    return (uc[0] + TRUNC) if uc is not None else 0.0


def count(sites, name):
    uc = sites.get(name)
    return uc[1] if uc is not None else 0


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float('nan')


def sd(xs):
    xs = list(xs)
    if len(xs) < 2:
        return float('nan')
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def se_rows(xs):
    xs = list(xs)
    return sd(xs) / math.sqrt(len(xs)) if len(xs) >= 2 else float('nan')


def se_blocks(xs):
    xs = list(xs)
    nb = len(xs) // BLOCK
    if nb < 2:
        return float('nan')
    bm = [mean(xs[i * BLOCK:(i + 1) * BLOCK]) for i in range(nb)]
    return sd(bm) / math.sqrt(nb)


def fnum(v, nd=1):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return 'n/a'
    return ('%.' + str(nd) + 'f') % v


def ops(sites):
    return [k for k in sites if k in MAP]


def group_of(name):
    return MAP[name][1]


def row_group(sites, groups):
    s = 0.0
    c = 0
    for k, (u, n) in sites.items():
        if k in MAP and MAP[k][1] in groups:
            s += u + TRUNC
            c += n
    return s, c


def deduction(cand, f, upper=False):
    a_hold = f.get('a_hold_us', 0)
    a_wait = f.get('a_wait_us', 0)
    mh_disp = f.get('mh_disp_us', 0)
    if cand == 'MM_out':
        return a_hold + a_wait
    if cand == 'DRAW_out':
        return a_hold - mh_disp + (0 if upper else a_wait)
    if cand == 'DISP_out':
        return mh_disp + (0 if upper else a_wait)
    if cand == 'EOP_adj':
        return (f.get('pl_eop_ns', 0) + f.get('pl_bar_ns', 0) + (0 if upper else f.get('pl_sub_ns', 0))) / 1000.0
    if cand == 'WAITFLIP_adj':
        return 0.0 if upper else f.get('pl_sub_ns', 0) / 1000.0
    if cand == 'FLIP_low':
        return 0.0 if upper else f.get('mh_pres_us', 0) + f.get('mh_pres_wait_us', 0)
    return 0.0


def d0_row(r):
    f = r['f']
    named = sum(f.get(k, 0) for k in ('pl_cmd_ns', 'pl_gc_ns', 'pl_sub_ns', 'pl_eop_ns', 'pl_bar_ns', 'pl_pref_ns'))
    return (f.get('pl_proc_ns', 0) / 1000.0 - f.get('a_hold_us', 0) - f.get('a_wait_us', 0) - named / 1000.0
            - (r['pm4'].get('prefetch', (0, 0))[0]) - (r['pm4'].get('stream-prefetch', (0, 0))[0]))


# --- the run json (IF0) ----------------------------------------------------------------------------------------------
def base_words(root):
    p = os.path.join(root, 'gates_base.txt')
    if not os.path.isfile(p) or fsha(p) != BASE_SHA:
        return None
    return open(p, encoding='utf-8').read().split()


def if0_rows(tag, meta, parsed, root):
    """The IF0 checks of a run: list of (name, ok)."""
    env = (meta or {}).get('env') or {}
    words = base_words(root)
    out = [('json readable', meta is not None),
           ('build %s' % BUILD_SHA[:8], (meta or {}).get('binary_sha256') == BUILD_SHA),
           ('KYTY_PM4_TRACE=%s' % TRACE[tag], env.get('KYTY_PM4_TRACE') == TRACE[tag]),
           ('no KYTY_GATE_SCHEDULE / ABBA', 'KYTY_GATE_SCHEDULE' not in env and 'KYTY_GATE_SCHEDULE_ABBA' not in env),
           ('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1'),
           ('no KYTY_GPU_CHECKPOINTS, KYTY_REC, KYTY_GPU_WALL',
            not any(k in env for k in ('KYTY_GPU_CHECKPOINTS', 'KYTY_REC', 'KYTY_GPU_WALL'))),
           ('gates = the base %s' % BASE_SHA[:8], words is not None and ((meta or {}).get('gates') or '').split() == words),
           ('log Gate: lines = the arm-0 set of kp137 %s' % ' '.join(KNOBS),
            parsed is not None and sorted(parsed['gates']) == sorted(KNOBS)),
           ('log without GateArm:', parsed is not None and parsed['arms'] == 0)]
    if tag in SEQ and PRED_SHA is not None:
        pre = (meta or {}).get('prereg') or {}
        out.append(('prereg sha = PRED_SHA', pre.get('sha256') == PRED_SHA and pre.get('bytes') == PRED_BYTES))
    return out


# --- one run --------------------------------------------------------------------------------------------------------
def eval_run(tag, root):
    log = os.path.join(root, 'log_%s.txt' % tag)
    jpath = os.path.join(root, '%s.json' % tag)
    res = dict(tag=tag, trace=TRACE[tag], log=log, log_sha=None, present=False)
    try:
        meta = json.load(open(jpath, encoding='utf-8'))
        if not isinstance(meta, dict):
            meta = None
    except (OSError, ValueError):
        meta = None
    if not os.path.isfile(log):
        res['if'] = {'IF0': [('log present', False)] + if0_rows(tag, meta, None, root)}
        res['fails'] = ['IF0']
        res['new_rows'] = 0
        res['debt'] = True
        return res, None
    res['present'] = True
    res['log_sha'] = fsha(log)
    parsed = parse_log(log)
    w, rng, last = window(parsed)
    res['rows_full'] = sum(1 for r in parsed['rows'] if r['has3'] and r['pm4'] is not None)
    res['last_full_n'] = last
    res['new_rows'] = len(w)
    res['debt'] = len(w) < MIN_NEW_ROWS
    res['fatal'] = parsed['fatal']
    res['orphans'] = parsed['orphans']
    res['dups'] = parsed['dups']
    res['knob_log'] = parsed['gates']
    ifs = {}
    ifs['IF0'] = if0_rows(tag, meta, parsed, root)
    opnames = sorted(k for k in parsed['names_all'] if k not in NONOP)
    unknown = sorted(k for k in parsed['names_all'] if k not in MAP and k not in NONOP)
    ifs['IF3'] = [('names outside the map: %s' % (','.join(unknown) or 'none'), not unknown)]
    missing = [k for k in IF11_FIELDS if any(k not in r['f'] for r in w)]
    ifs['IF11'] = [('fields in every NEW window row: missing %s' % (','.join(missing) or 'none'), not missing)]
    on = TRACE[tag] == '1'
    res['on'] = on
    res['names'] = opnames
    if not on:
        ifs['IF1'] = [('no op*/nop* name on any FrameTrace-pm4: line: %s' % (','.join(opnames) or 'none'), not opnames)]
    calc = dict(rows=w)
    if on and w:
        with_names = sum(1 for r in w if ops(r['pm4']))
        ifs['IF2'] = [('P1 rows with an op*/nop* name %d of %d' % (with_names, len(w)), with_names >= P1_MIN * len(w))]
        nest = sum(count(r['pm4'], 'op3f') for r in w)
        ifs['IF4'] = [('C(op3f) in W = %d' % nest, nest == 0)]
        # c_k (item 212 (d))
        emeans = {}
        for s in sorted(k for k, v in MAP.items() if v[2] == 1):
            emeans[s] = (mean(count(r['pm4'], s) for r in w), sum(raw_star(r['pm4'], s) for r in w),
                         sum(count(r['pm4'], s) for r in w))
        cands = [(s, 1000.0 * v[1] / v[2]) for s, v in emeans.items() if v[0] >= E_MIN and v[2] > 0]
        esum_c = sum(v[0] for v in emeans.values())
        if esum_c >= E_MIN:
            tot_c = sum(v[2] for v in emeans.values())
            if tot_c > 0:
                cands.append(('E', 1000.0 * sum(v[1] for v in emeans.values()) / tot_c))
        res['c_cands'] = cands
        ck = min(c for _, c in cands) if cands else None
        res['c_k'] = ck
        ifs['IF5'] = [('c_k candidates %s' % (','.join(s for s, _ in cands) or 'none'), bool(cands))]
        ifs['IF5b'] = [('c_k in [%g, %g] ns' % (C_LO, C_HI), ck is not None and C_LO <= ck <= C_HI)]
        # identities (item 212 (z))
        fm = lambda k: mean(r['f'].get(k, 0) for r in w)
        s_pm4 = mean(sum(raw_star(r['pm4'], k) for k in ops(r['pm4'])) for r in w)
        c_pm4 = mean(sum(count(r['pm4'], k) for k in ops(r['pm4'])) for r in w)
        pl_cmd_n = fm('pl_cmd_n')
        # the coverage in integer ns per row (1000 * raw* is an integer): exact at the edges of the tolerance
        ident_ns = mean(r['f'].get('pl_proc_ns', 0) - 1000.0 * sum(raw_star(r['pm4'], k) for k in ops(r['pm4']))
                        - (r['f'].get('pl_cmd_ns', 0) + r['f'].get('pl_pref_ns', 0) + r['f'].get('pl_gc_ns', 0)
                           + r['f'].get('pl_sub_ns', 0))
                        - 1000.0 * (raw_star(r['pm4'], 'prefetch') + raw_star(r['pm4'], 'stream-prefetch')) for r in w)
        g = ident_ns / pl_cmd_n if pl_cmd_n > 0 else float('nan')
        g_lo = (-fm('pl_sub_ns') / pl_cmd_n - G_LO_PAD) if pl_cmd_n > 0 else float('nan')
        fpk = pl_cmd_n - c_pm4
        mm = mean(row_group(r['pm4'], ('DRAWMM', 'DISPMM'))[0] for r in w) - fm('a_hold_us') - fm('a_wait_us')
        a_hold_n = fm('a_hold_n')
        hh = a_hold_n - mean(sum(count(r['pm4'], k) for k in S1) for r in w)
        multi0 = all(count(r['pm4'], k) == 0 for r in w for k in MULTI)
        calc.update(g=g, g_lo=g_lo, F=fpk, M=mm, H=hh, multi0=multi0, s_pm4=s_pm4, c_pm4=c_pm4, pl_cmd_n=pl_cmd_n)
        ifs['IF6'] = [('g in [lower, %g] ns/iteration' % G_HI, g_lo <= g <= G_HI)]
        ifs['IF7'] = [('F in [-%g, %g] x pl_cmd_n' % (F_LO, F_HI), -F_LO * pl_cmd_n <= fpk <= F_HI * pl_cmd_n)]
        ifs['IF8'] = [('M >= %g us' % M_MIN, mm >= M_MIN)]
        ifs['IF9'] = [('H >= -%g a_hold_n%s' % (H_TOL, ' and |H| <= it (no op2c/op38)' if multi0 else ''),
                       hh >= -H_TOL * a_hold_n and (not multi0 or abs(hh) <= H_TOL * a_hold_n))]
        lack = sum(1 for r in rng if r['pm4'] is None)
        ifs['IF10'] = [('NEW rows without FrameTrace-pm4: %d of %d' % (lack, len(rng)), lack <= IF10_MAX * len(rng))]
        # partition (exact by construction; a failure is a scorer error)
        tot = mean(sum(raw_star(r['pm4'], k) for k in ops(r['pm4'])) for r in w)
        parts = sum(mean(row_group(r['pm4'], (grp,))[0] for r in w) for grp in GROUPS)
        if abs(tot - parts) > 1e-6 * max(1.0, abs(tot)):
            print('scorer error: the partition of the groups does not sum to the sites')
            raise SystemExit(2)
    res['if'] = ifs
    res['fails'] = sorted(k for k, rows in ifs.items() if not all(ok for _, ok in rows))
    res['c_k'] = res.get('c_k')
    return res, calc


def levels(res, calc, c_over=None, upper=False):
    """Per candidate: (L, 2SE blocks, n_g/frame, B = mean(G - A), per-row values).  c_over replaces c_k; upper -> U_g."""
    w = calc['rows']
    c = c_over if c_over is not None else res['c_k']
    out = {}
    for cand in CAND_ORDER:
        groups = CANDS[cand][0]
        vals = []
        bs = []
        ns = []
        for r in w:
            s, n = row_group(r['pm4'], groups)
            a = deduction(cand, r['f'], upper=upper)
            bs.append(s - a)
            ns.append(n)
            vals.append(s - c * n / 1000.0 - a)
        out[cand] = dict(L=mean(vals), se2=2.0 * se_blocks(vals), n=mean(ns), B=mean(bs), vals=vals)
    return out


def sigma_rows(res, calc):
    out = []
    for r in calc['rows']:
        s = sum(raw_star(r['pm4'], k) for k in ops(r['pm4']))
        c = sum(count(r['pm4'], k) for k in ops(r['pm4']))
        f = r['f']
        out.append(s - res['c_k'] * c / 1000.0 - f.get('a_hold_us', 0) - f.get('a_wait_us', 0)
                   - (f.get('pl_eop_ns', 0) + f.get('pl_bar_ns', 0) + f.get('pl_sub_ns', 0)) / 1000.0)
    return out


def passes(lb, lc):
    return (lb + lc) / 2.0 >= NAMED_MEAN and min(lb, lc) >= NAMED_EACH


def breakeven(bb, nb, bc, nc):
    """c*_mean (mean of b, c = 400) and c*_min (min of b, c = 325), ns; None when the level does not depend on c."""
    nbar = (nb + nc) / 2.0
    cm = 1000.0 * ((bb + bc) / 2.0 - NAMED_MEAN) / nbar if nbar > 0 else None
    each = [1000.0 * (b - NAMED_EACH) / n for b, n in ((bb, nb), (bc, nc)) if n > 0]
    cmin = min(each) if each else None
    return cm, cmin


# --- the census reading ------------------------------------------------------------------------------------------------
def decide(root):
    runs = {}
    calcs = {}
    for tag in SEQ:
        runs[tag], calcs[tag] = eval_run(tag, root)
    fails = [(t, k) for t in SEQ for k in runs[t]['fails']]
    out = dict(runs=runs, if_fails=['%s %s' % x for x in fails], notes=[])
    if fails:
        out['outcome'] = 'INSTRUMENT_FAIL'
        return out, calcs
    if any(runs[t]['debt'] for t in ON):
        out['outcome'] = 'DEBT'
        return out, calcs
    b, c = ON
    lv = {t: levels(runs[t], calcs[t]) for t in ON}
    up = {t: levels(runs[t], calcs[t], c_over=C_LO, upper=True) for t in ON}
    l229 = {t: levels(runs[t], calcs[t], c_over=C_CMP) for t in ON}
    l0 = {t: levels(runs[t], calcs[t], c_over=0.0) for t in ON}
    cmax = max(runs[b]['c_k'], runs[c]['c_k'])
    table = {}
    for cand in CAND_ORDER:
        lb, lc = lv[b][cand]['L'], lv[c][cand]['L']
        ub, uc = up[b][cand]['L'], up[c][cand]['L']
        cm, cmin = breakeven(lv[b][cand]['B'], lv[b][cand]['n'], lv[c][cand]['B'], lv[c][cand]['n'])
        sens = any(x is not None and min(C_LO, cmax) < x < max(C_LO, cmax) for x in (cm, cmin))
        table[cand] = dict(Lb=lb, Lc=lc, mean=(lb + lc) / 2.0, se2b=lv[b][cand]['se2'], se2c=lv[c][cand]['se2'],
                           nb=lv[b][cand]['n'], nc=lv[c][cand]['n'], Ub=ub, Uc=uc, pass_L=passes(lb, lc),
                           pass_U=passes(ub, uc), L229=(l229[b][cand]['L'] + l229[c][cand]['L']) / 2.0,
                           L0=(l0[b][cand]['L'] + l0[c][cand]['L']) / 2.0, cstar_mean=cm, cstar_min=cmin, sens=sens,
                           label=CANDS[cand][1])
    out['table'] = table
    # LEVEL-INFLATED (item 213 (g))
    sig = {t: sigma_rows(runs[t], calcs[t]) for t in ON}
    d0 = {t: [d0_row(r) for r in calcs[t]['rows']] for t in OFF if calcs[t] is not None}
    usable = [t for t in OFF if not runs[t]['debt'] and t in d0]
    x = x2se = None
    inflated = False
    if usable:
        s_mean = mean(mean(sig[t]) for t in ON)
        s_se = 0.5 * math.sqrt(sum(se_rows(sig[t]) ** 2 for t in ON))
        d_mean = mean(mean(d0[t]) for t in usable)
        d_se = math.sqrt(sum(se_rows(d0[t]) ** 2 for t in usable)) / len(usable)
        x = s_mean - d_mean
        x2se = 2.0 * math.sqrt(s_se ** 2 + d_se ** 2)
        inflated = x - x2se > 0
    out['X'] = x
    out['X2se'] = x2se
    out['X_runs'] = usable
    out['inflated'] = inflated
    named = []
    bound = []
    for cand in CAND_ORDER:
        t = table[cand]
        if t['pass_L']:
            if inflated and not passes(t['Lb'] - x, t['Lc'] - x):
                bound.append(cand)
            else:
                named.append(cand)
        elif t['pass_U']:
            bound.append(cand)
    named.sort(key=lambda k: -table[k]['mean'])
    out['named'] = named
    out['bound'] = bound
    if named:
        out['outcome'] = 'NAMED'
    elif bound:
        out['outcome'] = 'SPREAD (by bound)'
    else:
        out['outcome'] = 'SPREAD'
    out['sensitive'] = [k for k in CAND_ORDER if table[k]['sens']]
    return out, calcs


# --- printing ------------------------------------------------------------------------------------------------------------
def print_run_masked(res):
    lines = ['run %s KYTY_PM4_TRACE=%s log %s sha256 %s' % (res['tag'], res['trace'], res['log'], res['log_sha'] or 'none')]
    if res.get('present'):
        lines.append('  full rows %d, last full n %s, NEW window rows (item 212 (v)) %d -> %s; duplicate n %d; orphan pm4 '
                     'lines %d; fatal marker lines %d' % (res['rows_full'], res['last_full_n'], res['new_rows'],
                                                          'DEBT' if res['debt'] else 'reads', res['dups'], res['orphans'],
                                                          res['fatal']))
        lines.append('  knob string from the log: %s' % (' '.join(res['knob_log']) or 'none'))
        lines.append('  op*/nop* names on the FrameTrace-pm4: lines: %d distinct' % len(res['names']))
        if res.get('on') and 'c_cands' in res:
            lines.append('  c_k candidates of E with >= %g/frame: %s; c_k in [%g, %g] ns: %s%s'
                         % (E_MIN, ','.join(s for s, _ in res['c_cands']) or 'none', C_LO, C_HI,
                            'yes' if 'IF5b' not in res['fails'] else 'NO',
                            '' if res['c_k'] is None or res['c_k'] <= C_HIGH else ' (c-HIGH above %g ns)' % C_HIGH))
    for k in sorted(res['if']):
        for name, ok in res['if'][k]:
            lines.append('  %s %s: %s' % (k, 'PASS' if ok else 'FAIL', name))
    return lines


def print_reading(out, calcs):
    runs = out['runs']
    lines = []
    for t in SEQ:
        lines += print_run_masked(runs[t])
    lines.append('THE IDENTITIES (item 212 (z); gross - RC9: the lower edge of g catches a double count >= ~1 ms [I], F a loss '
                 '>= 50 %; the levels stand on the map and IF1-IF5, IF10)')
    for t in ON:
        cc = calcs[t]
        if cc is not None and 'g' in cc:
            lines.append('  %s g %s ns/iteration (lower %s, upper %g); F %s /frame (pl_cmd_n %s); M %s us; H %s (op2c/op38 '
                         'zero in every row: %s)' % (t, fnum(cc['g'], 2), fnum(cc['g_lo'], 2), G_HI, fnum(cc['F']),
                                                     fnum(cc['pl_cmd_n']), fnum(cc['M']), fnum(cc['H'], 2), cc['multi0']))
    for t in ON:
        r = runs[t]
        if r.get('c_k') is not None:
            lines.append('  %s c_k %s ns = min of %s%s' % (t, fnum(r['c_k'], 2), ', '.join('%s %s' % (s, fnum(v, 2))
                                                                                        for s, v in r['c_cands']),
                                                         ' c-HIGH' if r['c_k'] > C_HIGH else ''))
    lines.append('VERDICT %s' % out['outcome'])
    if out['outcome'] == 'INSTRUMENT_FAIL':
        lines.append('  failed: %s' % ', '.join(out['if_fails']))
        return lines
    if out['outcome'] == 'DEBT':
        lines.append('  a run with 1 has < %d NEW window rows: %s' % (MIN_NEW_ROWS, ', '.join(
            '%s %d' % (t, runs[t]['new_rows']) for t in ON)))
        return lines
    tb = out['table']
    lines.append('THE CANDIDATES (us/frame, [c] of one run with the instrument; not a gain, not a ceiling, not a price; '
                 'b = %s, c = %s; 2SE by blocks of %d rows)' % (ON[0], ON[1], BLOCK))
    lines.append('  %-13s %9s %9s %9s %7s %7s %9s %9s %9s %9s %9s %9s %9s %s' % (
        'candidate', 'L_b', 'L_c', 'mean', '2SE_b', '2SE_c', 'n_b/fr', 'n_c/fr', 'U_b', 'U_c', 'L@22.9', 'L@0',
        'c*mean', 'c*min / notes'))
    for cand in CAND_ORDER:
        t = tb[cand]
        notes = []
        if t['sens']:
            notes.append('c-SENSITIVE')
        if t['label']:
            notes.append(t['label'])
        lines.append('  %-13s %9s %9s %9s %7s %7s %9s %9s %9s %9s %9s %9s %9s %s %s' % (
            cand, fnum(t['Lb']), fnum(t['Lc']), fnum(t['mean']), fnum(t['se2b']), fnum(t['se2c']), fnum(t['nb']),
            fnum(t['nc']), fnum(t['Ub']), fnum(t['Uc']), fnum(t['L229']), fnum(t['L0']), fnum(t['cstar_mean'], 2),
            fnum(t['cstar_min'], 2), ' '.join(notes)))
    for t in ON:
        r = runs[t]
        lines.append('  %s c_k %s ns: c_k * n_g / 1000 per candidate: %s' % (t, fnum(r['c_k'], 2), ', '.join(
            '%s %s' % (cand, fnum(r['c_k'] * levels_n(calcs[t], cand) / 1000.0)) for cand in CAND_ORDER)))
    lines.append('THE INSTRUMENT MARKS INSIDE A CANDIDATE BY THE CODE (RC3; [I]):')
    for cand in ('MM_out', 'DRAW_out', 'DISP_out', 'EOP_adj', 'WAITFLIP_adj'):
        est = []
        for t in ON:
            f = calcs[t]['rows']
            if cand in ('MM_out', 'DRAW_out', 'DISP_out'):
                key = {'MM_out': None, 'DRAW_out': 'draws', 'DISP_out': 'dispatches'}[cand]
                nn = mean(r['f'].get('a_hold_n', 0) if key is None else r['f'].get(key, 0) for r in f)
                est.append('%s %s holds/frame x %g ns = %s us/frame [I]' % (t, fnum(nn), MM_PRICE_NS, fnum(nn * MM_PRICE_NS
                                                                                                     / 1000.0)))
            else:
                keys = ('pl_eop_n', 'pl_bar_n', 'pl_sub_n') if cand == 'EOP_adj' else ('pl_sub_n',)
                nn = mean(sum(r['f'].get(k, 0) for k in keys) for r in f)
                est.append('%s %s spans/frame x %g ns = %s us/frame [I]' % (t, fnum(nn), C_CMP, fnum(nn * C_CMP / 1000.0)))
        lines.append('  %s: %s; %s' % (cand, MARKS[cand], '; '.join(est)))
    lines.append('  REG, MEM, SYNC, STATE, FLIP_low: no instrument mark inside by the code beyond the site pair itself')
    lines.append('FLIP_low - a lower bound with a gap <= mh_pres_us + mh_pres_wait_us of the run (199.6 [c, kp137]) from the '
                 'present thread (RC4); item 212 (b) stands')
    lines.append('TIME-DEPENDENT PATHS (RC10): pl_sub_n, submits, release-mem-* sites n of FrameTrace-submit: per run')
    for t in SEQ:
        cc = calcs[t]
        if cc is None or not cc['rows']:
            lines.append('  %s no rows' % t)
            continue
        rw = cc['rows']
        lines.append('  %s (KYTY_PM4_TRACE=%s) pl_sub_n %s submits %s release-mem n %s' % (
            t, TRACE[t], fnum(mean(r['f'].get('pl_sub_n', 0) for r in rw), 2),
            fnum(mean(r['f'].get('submits', 0) for r in rw), 2),
            fnum(mean(sum(v[1] for k, v in (r['sub'] or {}).items() if k.startswith('release-mem-')) for r in rw), 2)))
    lines.append('LEVEL-INFLATED (item 213 (g)): X = mean_bc(Sigma) - mean(D0 of %s)' % (','.join(out['X_runs']) or 'none'))
    if out['X'] is None:
        lines.append('  X not evaluable (no run with 0 outside DEBT) - no consequence')
    else:
        lines.append('  X %s us/frame, 2SE by rows %s -> %s' % (fnum(out['X']), fnum(out['X2se']),
                                                                'LEVEL-INFLATED %s' % fnum(out['X']) if out['inflated']
                                                                else 'no consequence'))
    for t in OFF:
        cc = calcs[t]
        if cc is not None and cc['rows']:
            lines.append('  D0(%s) %s us/frame over %d NEW rows%s' % (t, fnum(mean(d0_row(r) for r in cc['rows'])),
                                                                      len(cc['rows']), ' (DEBT)' if runs[t]['debt'] else ''))
    lines.append('THE OPCODE TABLE (RC6; reference, not the outcome): name class group | per run: raw* n/frame c_k*n/1000 '
                 'corrected')
    names = sorted(set(k for t in ON for r in calcs[t]['rows'] for k in ops(r['pm4'])))
    for k in names:
        cells = []
        for t in ON:
            rw = calcs[t]['rows']
            rs = mean(raw_star(r['pm4'], k) for r in rw)
            nn = mean(count(r['pm4'], k) for r in rw)
            ded = runs[t]['c_k'] * nn / 1000.0
            cells.append('%s %s %s %s' % (fnum(rs), fnum(nn), fnum(ded), fnum(rs - ded)))
        lines.append('  %-6s %-6s %-8s | %s' % (k, MAP[k][0], MAP[k][1], ' | '.join(cells)))
    nop = []
    for t in ON:
        rw = [r for r in calcs[t]['rows']
              if count(r['pm4'], 'nop17') == (r['sub'] or {}).get('flip', (0, 0))[1] and count(r['pm4'], 'nop00') > 0]
        tot_c = sum(count(r['pm4'], 'nop00') for r in rw)
        nop.append('%s %s ns over %d rows' % (t, fnum(1000.0 * sum(raw_star(r['pm4'], 'nop00') for r in rw) / tot_c, 2)
                                              if tot_c else 'n/a', len(rw)))
    lines.append('COMPARATOR nop00 (RC2 (b); reference, not a gate): %s' % '; '.join(nop))
    if not any(runs[t]['debt'] for t in SEQ):
        mo = lambda ts, fn: mean(mean(fn(r) for r in calcs[t]['rows']) for t in ts)
        ddt = mo(ON, lambda r: r['f'].get('dt_us', 0)) - mo(OFF, lambda r: r['f'].get('dt_us', 0))
        dd0 = mo(ON, d0_row) - mo(OFF, d0_row)
        dpp = mo(ON, lambda r: r['f'].get('pl_proc_ns', 0)) - mo(OFF, lambda r: r['f'].get('pl_proc_ns', 0))
        npk = mo(ON, lambda r: sum(count(r['pm4'], k) for k in ops(r['pm4'])))
        lines.append('PRICE REFERENCE (item 210 (e)(5)(v); [c, between runs]; not a gate): d dt_us %s us, d D0 %s us, '
                     'd pl_proc / packets %s ns' % (fnum(ddt), fnum(dd0), fnum(dpp / npk if npk else float('nan'), 2)))
    else:
        lines.append('PRICE REFERENCE not printed (a DEBT run, item 212 (e))')
    if out['outcome'] == 'NAMED':
        for cand in out['named']:
            t = tb[cand]
            lines.append('NAMED %s%s mean %s (b %s, c %s) - a target of the s141 selection, not a candidate, not a gain'
                         % (cand, (' (%s)' % t['label']) if t['label'] else '', fnum(t['mean']), fnum(t['Lb']),
                            fnum(t['Lc'])))
    if out['bound']:
        lines.append('BY BOUND (item 213 (b), (g)): %s' % ', '.join(out['bound']))
    if out['sensitive']:
        lines.append('c-SENSITIVE (item 213 (v); the outcome does not change): %s' % ', '.join(out['sensitive']))
    return lines


def levels_n(calc, cand):
    return mean(row_group(r['pm4'], CANDS[cand][0])[1] for r in calc['rows'])


def masked_json(res):
    keep = ('tag', 'trace', 'log', 'log_sha', 'present', 'rows_full', 'last_full_n', 'new_rows', 'debt', 'fatal', 'orphans',
            'dups', 'knob_log', 'fails')
    d = dict((k, res[k]) for k in keep if k in res)
    d['names_n'] = len(res.get('names', []))
    d['c_cands'] = [s for s, _ in res.get('c_cands', [])]
    d['if'] = dict((k, [[n, ok] for n, ok in v]) for k, v in res['if'].items())
    d['printed_delta'] = 'no'
    return d


# --- the seal ------------------------------------------------------------------------------------------------------------
def check_seal(tag, root, self_path):
    rows = []
    pred = os.path.join(root, PRED_NAME)
    pdata = open(pred, 'rb').read() if os.path.isfile(pred) else None
    rows.append(('PRED_SHA / PRED_BYTES = the seal file', pdata is not None and PRED_SHA is not None
                 and hashlib.sha256(pdata).hexdigest() == PRED_SHA and len(pdata) == PRED_BYTES))
    text = pdata.decode('utf-8', 'replace') if pdata is not None else ''
    own = body_sha(open(self_path, 'rb').read())
    rows.append(('the seal names this scorer body sha256 %s' % own[:16], ('scorer body sha256: %s' % own) in text))
    chain = os.path.join(root, CHAIN_NAME)
    csha = fsha(chain) if os.path.isfile(chain) else 'none'
    rows.append(('the seal names the chain sha256 %s' % csha[:16], ('chain sha256: %s' % csha) in text))
    seals = os.path.join(root, SEALS_NAME)
    bad = []
    listed = 0
    if os.path.isfile(seals):
        for line in open(seals, encoding='utf-8'):
            m = re.match(r'^([0-9a-f]{64})  (\S.*)$', line.rstrip('\n'))
            if not m:
                continue
            listed += 1
            p = m.group(2) if re.match(r'^[A-Za-z]:/', m.group(2)) else os.path.join(root, m.group(2))
            if not os.path.isfile(p) or fsha(p) != m.group(1):
                bad.append(m.group(2))
    rows.append(('%s lists files, every sha256 matches the disk (%d listed, differ: %s)'
                 % (SEALS_NAME, listed, ','.join(bad) or 'none'), listed > 0 and not bad))
    rows.append(('the tag %s is a registered call' % tag, tag in SEQ))
    ok = all(v for _, v in rows)
    lines = ['pm4c140 --check-seal %s: %s' % (tag, 'PASS' if ok else 'FAIL')] + [
        '  %s %s' % ('ok' if v else 'NO', n) for n, v in rows]
    return ok, lines


def emit(lines, out_path, data):
    for line in lines:
        print(line)
    if out_path:
        d = os.path.dirname(out_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(out_path, 'w', encoding='ascii') as stream:
            json.dump(data, stream, indent=1, sort_keys=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)

    def opt(flag):
        if flag in argv:
            i = argv.index(flag)
            return argv[i + 1] if i + 1 < len(argv) else ''
        return None
    root = opt('--dir') or ROOT
    out_path = opt('--out')
    head = 'pm4c140 scorer sha256 %s body %s' % (fsha(os.path.abspath(__file__)),
                                                   body_sha(open(os.path.abspath(__file__), 'rb').read()))
    if '--check-seal' in argv:
        tag = opt('--tag')
        if tag not in SEQ:
            print('usage: pm4c140.py --check-seal --tag pm4c140a|b|c|d')
            return 2
        ok, lines = check_seal(tag, root, os.path.abspath(__file__))
        emit([head] + lines, None, None)
        return 0 if ok else 1
    if '--all' in argv:
        out, calcs = decide(root)
        lines = [head] + print_reading(out, calcs)
        data = dict(outcome=out['outcome'], if_fails=out['if_fails'], named=out.get('named', []),
                    bound=out.get('bound', []), sensitive=out.get('sensitive', []), X=out.get('X'), X2se=out.get('X2se'),
                    inflated=out.get('inflated'), runs=dict((t, masked_json(out['runs'][t])) for t in SEQ),
                    table=dict((k, dict((kk, vv) for kk, vv in v.items())) for k, v in out.get('table', {}).items()),
                    printed_delta='yes', scorer=head)
        emit(lines, out_path, data)
        return 0 if out['outcome'] in ('NAMED', 'SPREAD', 'SPREAD (by bound)') else 1
    tag = opt('--tag')
    smoke = opt('--smoke')
    if smoke is not None:
        if smoke != SMOKE:
            print('usage: pm4c140.py --smoke pm4s140')
            return 2
        tag = smoke
    elif tag not in SEQ:
        print('usage: pm4c140.py --tag pm4c140a|b|c|d | --smoke pm4s140 | --all | --check-seal --tag <call>')
        return 2
    res, _ = eval_run(tag, root)
    lines = [head] + print_run_masked(res)
    verdict = 'RUN_FAIL' if res['fails'] else ('RUN_DEBT' if res['debt'] else 'RUN_READS')
    lines.append('VERDICT %s: %s (masked: no level, no c_k value, no identity value - printed_delta=no; RC7 of review140)'
                 % (tag, verdict))
    emit(lines, out_path, dict(masked_json(res), verdict=verdict, scorer=head))
    return 0 if verdict == 'RUN_READS' else 1


if __name__ == '__main__':
    sys.exit(main())
