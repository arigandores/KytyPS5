# S14e (HPP-528) Red Team: own recount of member (0') of ROADMAP s122 item 430(g)(2), 439(v), 442 - independent of c0p_s14k.py.
# Inputs: pickles of rt_s14e_ext.py (six S10 logs + other S10 logs), the S14j dump (streamed, binary), score.json "first".
import sys, os, re, json, pickle, hashlib, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'): sys.exit(5)
S = os.path.dirname(os.path.abspath(__file__))
DUMP = 'C:/kyty/s288/s14j/specdump_snap0.txt'
SIG = 'KytySC3:699c1e4b7db359067b461e029b913c4b6e78dc90:robust:ftz:cbank'
COUNTED = ['t2_1', 't2_2', 't2_4', 't2_5', 't2_7']
ALL = COUNTED + ['t2_cs0']
OTHER = ['c5_0', 'pi_r0', 'pi_r1', 'pi_w0', 'pi_w1', 't2_3', 't2_6', 'u_1', 'u_2', 'u_3', 'u_4', 'u_5']
FIN = {'t2_1': (31, 34), 't2_2': (1, 2), 't2_4': (1, 1), 't2_5': (6, 9), 't2_7': (9, 9), 't2_cs0': (30, 32)}

def tokens(tail):
    t = tail.strip()
    return t  # exact printed text (after the single leading space)

# --- dump
h = hashlib.sha256(); recs = []; fsig = {}; tot = None
with open(DUMP, 'rb') as f:
    for l in f:
        h.update(l); s = l.rstrip(b'\r\n').decode('latin1')
        m = re.match(r'SpecDump: file=(\S+) stage=(\w+) hash=0x([0-9a-f]{16}) perm=(\d+) spec=(.*)$', s)
        if m: recs.append((m.group(1), m.group(2), m.group(3), int(m.group(4)), m.group(5).strip())); continue
        m = re.match(r'SpecDump: file-sig file=(\S+) sig=(\S+)$', s)
        if m: fsig[m.group(1)] = m.group(2); continue
        m = re.match(r'SpecDump: files=(\d+) read=(\d+) failed=(\d+) perms=(\d+)$', s)
        if m: tot = tuple(map(int, m.groups()))
print('dump sha256', h.hexdigest(), 'totals', tot, 'records', len(recs), collections.Counter(r[1] for r in recs))
def trhash(sig):
    m = re.search(r'KytySC3:([0-9a-f]{40})(:[A-Za-z][\w:]*)?', sig or '')
    return m.group(0) if m else None
rsig = collections.Counter(trhash(fsig.get(r[0])) for r in recs)
print('record signatures', dict(rsig))
dsame = collections.defaultdict(set)   # (stage, spec) -> hashes, signature of S10
dany = collections.defaultdict(set)    # spec -> {(stage, hash)} any stage, any signature
for fn, st, hs, perm, sp in recs:
    dany[sp].add((st, hs))
    if st in ('VS', 'PS') and fsig.get(fn, '').find(SIG) >= 0: dsame[(st, sp)].add(hs)

L = {t: pickle.load(open(os.path.join(S, t + '.pkl'), 'rb')) for t in ALL + OTHER}
first = {t: json.load(open('C:/kyty/s288/s10/runs_s/%s.score.json' % t))['first'][0] for t in ALL}

def series(d, fst, join=1):
    rows = [(n, ln) for n, ln in d['rows'] if ln > d['ent']]
    sk = he = 0; out = []; cur = None; gap = 0
    for n, ln in rows:
        held, skip = d['skc'].get(n, (0, 0))
        w = (1 if skip > 0 and n > fst else 0) + (held if n >= fst else 0)
        sk += 1 if skip > 0 and n > fst else 0; he += held if n >= fst else 0
        if skip > 0 or held > 0:
            if cur is None: cur = dict(a=n, b=n, w=0, rows={})
            cur['b'] = n; cur['w'] += w; cur['rows'][n] = w; gap = 0
        elif cur is not None:
            gap += 1
            if gap > join: out.append(cur); cur = None
    if cur is not None: out.append(cur)
    return out, (sk, he)

def types_of(d):
    return d

# stage <-> ShaderRegister type, learned from the targets themselves (each compiled hash: types of its registrations)
def regs_before(d, hs, line):
    return [r for r in d['regs'].get(hs, ()) if r[0] < line]

REG2 = {'PS': 'b', 'VS': '8b'}
def stage_type(d, st, hs, line):
    ts = collections.Counter(r[2] for r in regs_before(d, hs, line))
    return ts

def clsb(st, r):
    return (r[2], r[3].get(REG2[st]))

res = {}
for t in ALL:
    d = L[t]; ser, sh = series(d, first[t])
    assert sh == FIN[t], (t, sh, FIN[t])
    # learn the type of the stage: the type of the registrations of compiled hashes of that stage
    tmap = collections.defaultdict(collections.Counter)
    for c in d['comp']:
        for r in regs_before(d, c[2], c[0]): tmap[c[1]][r[2]] += 1
    TY = {st: cnt.most_common(1)[0][0] for st, cnt in tmap.items()}
    tg = []
    for c in d['comp']:
        line, st, hs, perm, sp, fr, hostb = c
        if line < d['ent'] or st not in ('VS', 'PS') or fr is None: continue
        s = next((s for s in ser if s['a'] <= fr <= s['b']), None)
        if s is None: continue
        tg.append(dict(c=c, s=s))
    res[t] = dict(ser=ser, tg=tg, TY=TY)
    print(t, 'first', first[t], 'skip/held', sh, 'series', [(s['a'], s['b'], s['w']) for s in ser], 'targets', len(tg), 'types', TY,
          'unpaired spec', sum(1 for c in d['comp'] if c[4] is None))

def predicted(t, x, mode):
    d = L[t]; line, st, hs, perm, sp, fr, hostb = x['c']; ty = res[t]['TY'][st]
    sp = sp.strip()
    regs = [r for r in regs_before(d, hs, line) if r[2] == ty]
    if mode == 'R6':
        if dsame.get((st, sp)): return True, 'dump'
        if any(c[1] == st and c[4] is not None and c[4].strip() == sp and c[0] < line and c is not x['c'] for c in d['comp']): return True, 'compile'
        return False, None
    if mode == 'ANY':   # any record of the dump (any stage, any signature) or any compile of any S10 process other than this target
        if sp in dany: return True, 'dump-any'
        for u, e in L.items():
            for c in e['comp']:
                if c[4] is not None and c[4].strip() == sp and not (u == t and c is x['c']): return True, 'compile:' + u
        return False, None
    # decisive (item 430(g)(2)): T = last registration before the compile line; class cls_b; candidates (i) and (ii)
    if not regs: return False, 'noreg'
    T = max(regs); tcls = set(clsb(st, r) for r in regs)
    def bef(r): return r[0] < T[0] or r[1] < T[1]
    def cls_of(h2): return set(clsb(st, r) for r in d['regs'].get(h2, ()) if r[2] == ty and bef(r))
    for h2 in dsame.get((st, sp), ()):
        if cls_of(h2) & tcls: return True, 'dump:' + h2[:8]
    for c in d['comp']:
        if c is x['c'] or c[1] != st or c[4] is None or c[4].strip() != sp: continue
        if not (c[0] < T[0] or (c[6] is not None and c[6] < T[1])): continue
        if cls_of(c[2]) & tcls: return True, 'compile:' + c[2][:8]
    return False, None

for mode in ('DEC', 'R6', 'ANY'):
    wp = w = 0; npred = 0; ntg = 0; miss = []
    for t in COUNTED:
        for s in res[t]['ser']:
            ok = True
            for x in res[t]['tg']:
                if x['s'] is not s: continue
                p, why = predicted(t, x, mode); ntg += 1; npred += p; ok &= p
                if not p: miss.append((t, s['a'], x['c'][1], x['c'][2][:8]))
            w += s['w']; wp += s['w'] if ok else 0
    print('MODE', mode, 'C = %d / %d = %.4f' % (wp, w, wp / w), 'targets predicted %d of %d' % (npred, ntg))
    if mode != 'DEC': print('   not predicted:', miss)

# generous attribution for the R6 ceiling: a series row is blocked only by a not-ceiling-predictable target whose frame is
# that row (per-row), or series without gap joining
for join in (0, 1, 3):
    wp = w = 0
    for t in COUNTED:
        ser, _ = series(L[t], first[t], join)
        for s in ser:
            ok = True
            for x in res[t]['tg']:
                fr = x['c'][5]
                if s['a'] <= fr <= s['b'] and not predicted(t, x, 'R6')[0]: ok = False
            w += s['w']; wp += s['w'] if ok else 0
    print('R6 with gap join %d: %d / %d = %.4f' % (join, wp, w, wp / w))
wp = w = 0
for t in COUNTED:
    for s in res[t]['ser']:
        bad = set(x['c'][5] for x in res[t]['tg'] if x['s'] is s and not predicted(t, x, 'R6')[0])
        for n, rw in s['rows'].items():
            w += rw; wp += 0 if n in bad else rw
print('R6 per row (a row is lost only if a blocked target lands on it): %d / %d = %.4f' % (wp, w, wp / w))
# where the blocking targets sit inside their series
for t in COUNTED:
    for s in res[t]['ser']:
        for x in res[t]['tg']:
            if x['s'] is s and not predicted(t, x, 'R6')[0]:
                print('  blocked', t, 'series %d..%d w %d' % (s['a'], s['b'], s['w']), x['c'][1], x['c'][2], 'frame', x['c'][5],
                      'row weights from frame', sum(v for n, v in s['rows'].items() if n >= x['c'][5]))
