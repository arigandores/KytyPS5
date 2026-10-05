"""S16d (HPP-608): fixtures of the probe scorer s16d_score.py - one per member and edge; the last line is ALL OK."""
import copy
import sys

import s16d_score as S

SIG = S.SIG_A + ':robust:ftz:cbank:fixb26:fixb1b:fixf10'
FAILS = []


def check(name, cond):
    print(('ok   ' if cond else 'FAIL ') + name)
    if not cond:
        FAILS.append(name)


def res(st='OK', eq='1', dd='0', start=str(S.NO_START), stored_start=None, plan='same', val='1', f19='-', ind='0',
        spv='aa', phase=None):
    r = dict(st=st, eq=eq, dd=dd, start=start, stored_start=stored_start if stored_start is not None else start,
             plan=plan, val=val, f19=f19, ind=ind, spv=spv)
    if phase:
        r['phase'] = phase
    return r


class World:
    """A synthetic catalogue: recipes with stage descriptors, arm A results (A1 = A2 unless changed), arm B results."""

    def __init__(self):
        self.recipes = []
        self.A1 = {}
        self.B = {}
        self.manual = {}
        self.n = 0

    def jid(self, p):
        self.n += 1
        return '%s%d' % (p, self.n)

    def stage(self, stage, file, perm=0, in_eboot=True, fused=False, manual=0):
        st = dict(stage=stage, file=file, perm=perm, file_ok=True, in_eboot=in_eboot, fused=fused, jobsA={},
                  jobsB1={}, jobsB2={})
        self.manual['%s#%d' % (file, perm)] = manual
        if in_eboot:
            for form in ('A0', 'K', 'C'):
                j = self.jid('a')
                st['jobsA'][form] = j
                self.A1[j] = res()
        return st

    def graphics(self, vs_stage=1, with_ps=True, manual_ps=0, **kw):
        idx = len(self.recipes)
        stages = [self.stage(vs_stage, 'vs%d.bin' % idx, in_eboot=kw.get('vs_in', True),
                             fused=kw.get('vs_fused', False))]
        if with_ps:
            stages.append(self.stage(2, 'ps%d.bin' % idx, manual=manual_ps))
        rec = dict(index=idx, kind=1, stages=stages)
        if all(s['in_eboot'] for s in stages):
            first = stages[1] if with_ps else stages[0]
            for form in ('K', 'C'):
                variants = ['k16UNorm', 'k8UNorm'] if first is stages[1] and manual_ps else ['-']
                first['jobsB1'][form] = {}
                for v in variants:
                    j = self.jid('b')
                    first['jobsB1'][form][v] = j
                    f19 = '-'
                    if v == 'k16UNorm':
                        f19 = '[f19]_stand_format=5_manual_to_native=1_kept_manual=0'
                    elif v == 'k8UNorm':
                        f19 = '[f19]_stand_format=1_manual_to_native=0_kept_manual=1'
                    self.B[j] = res(f19=f19)
                if with_ps:
                    stages[0]['jobsB2'][form] = {}
                    for v in variants:
                        j = self.jid('b')
                        stages[0]['jobsB2'][form][v] = {'-': j}
                        self.B[j] = res()
        self.recipes.append(rec)
        return rec

    def compute(self):
        idx = len(self.recipes)
        st = self.stage(4, 'cs%d.bin' % idx)
        for form in ('K', 'C'):
            j = self.jid('b')
            st['jobsB1'][form] = {'-': j}
            self.B[j] = res()
        rec = dict(index=idx, kind=2, stages=[st])
        self.recipes.append(rec)
        return rec

    def meta(self, comparator=True, f19_expected=None):
        comp = []
        if comparator:
            for k in range(10):
                c = dict(file='c%d' % k, perm=0)
                for kind in ('base', 'stride', 'format', 'spirv'):
                    j = self.jid('a')
                    c[kind] = j
                    self.A1[j] = res(eq='1' if kind == 'base' else '0')
                comp.append(c)
        m = dict(recipes=self.recipes, denominator=len(self.recipes), comparator=comp, manual=self.manual,
                 manifest=dict(sha='65a95adf00', listed=3, ok=3, bad=[]), cache_sigs={SIG: 3}, parse_fail=[],
                 layout=dict(vs=10288, ps=376, cs=216), report=[],
                 f19_expected=f19_expected if f19_expected is not None else sum(1 for v in self.manual.values() if v))
        return m


def heads(extra_a=None, extra_b=None):
    a = ['S signature=' + SIG + ' enabled=1', 'S layout=10288:376:216', 'K KYTY_VEC_CONST=<unset>'] + (extra_a or [])
    b = ['S signature=' + SIG + ':fixf19 enabled=1', 'S layout=10288:376:216', 'K KYTY_VEC_CONST=<unset>',
         'K KYTY_FIX_F19=1'] + (extra_b or [])
    return {'A1': a, 'A2': list(a), 'B1': b, 'B2': list(b)}


def run(w, m=None, h=None, A2=None):
    m = m or w.meta()
    out, lines = S.score(m, w.A1, A2 if A2 is not None else copy.deepcopy(w.A1), w.B, h or heads())
    return out, lines


# ---- push-data chain (RC1)
check('start_for fits', S.start_for(0, 4) == 0)
check('start_for zero size', S.start_for(0, 0) == S.NO_START)
check('start_for edge 28+4 fits', S.start_for(28, 4) == 28)
check('start_for edge 29+4 no', S.start_for(29, 4) == S.NO_START)
check('advance no push', S.advance(6, S.NO_START, 5) == 6)
check('advance push', S.advance(6, 6, 5) == 11)
rec = dict(kind=1, stages=[dict(stage=5), dict(stage=2)])
ch = S.chain_starts(rec, lambda i: {'dd': '3'} if i == 1 else {'dd': '4'})
check('chain mesh: PS at 6, VS at 9', ch == {1: 6, 0: 9})
rec = dict(kind=1, stages=[dict(stage=1), dict(stage=2)])
ch = S.chain_starts(rec, lambda i: {'dd': '0'} if i == 1 else {'dd': '2'})
check('chain PS without push data: VS at 0', ch == {1: S.NO_START, 0: 0})
ch = S.chain_starts(dict(kind=2, stages=[dict(stage=4)]), lambda i: {'dd': '5'})
check('chain compute at 0', ch == {0: 0})

# ---- all prepared -> PASS_K0, identity, R_B = 1
w = World()
for _ in range(5):
    w.graphics()
w.compute()
out, lines = run(w)
check('clean world: PASS_K0', out['word'] == 'PASS_K0')
check('clean world: R_B K = 1', abs(out['rb']['K'] - 1.0) < 1e-9 and abs(out['rb']['C'] - 1.0) < 1e-9)
check('clean world: no NO_POWER members', out['no_power'] == [])

# ---- each reason, one recipe each, in order
w = World()
r_src = w.graphics(vs_in=False)
r_fused = w.graphics(vs_stage=5, vs_in=False, vs_fused=True)
r_key = w.graphics()
w.A1[r_key['stages'][0]['jobsA']['K']]['eq'] = '0'
r_canon_noinput = w.graphics()
w.A1[r_canon_noinput['stages'][1]['jobsA']['C']] = res(st='NOINPUT')
r_push = w.graphics()
w.A1[r_push['stages'][1]['jobsA']['K']].update(dd='3', start='0', stored_start='0')
w.A1[r_push['stages'][0]['jobsA']['K']].update(dd='2', start='0', stored_start='0')
r_shape = w.graphics()
w.B[r_shape['stages'][1]['jobsB1']['K']['-']] = res(st='SHAPE')
r_ident = w.graphics()
w.A1[r_ident['stages'][0]['jobsA']['K']]['plan'] = 'diff'
r_tr = w.graphics()
w.B[r_tr['stages'][0]['jobsB2']['K']['-']['-']] = res(st='CRASH', phase='T')
r_emit = w.graphics()
w.B[r_emit['stages'][1]['jobsB1']['K']['-']] = res(st='CRASH', phase='E')
r_val = w.graphics()
w.B[r_val['stages'][1]['jobsB1']['K']['-']]['val'] = '0'
r_hang = w.compute()
w.B[r_hang['stages'][0]['jobsB1']['K']['-']] = res(st='HANG', phase='-')
r_ok = w.graphics()
out, lines = run(w)
pr = {row['index']: row for row in out['per_recipe']}
check('src', pr[r_src['index']]['K'] == 'src' and pr[r_src['index']]['C'] == 'src')
check('fused', pr[r_fused['index']]['K'] == 'fused')
check('key (form K only)', pr[r_key['index']]['K'] == 'key' and pr[r_key['index']]['C'] == 'prepared')
check('canon by NOINPUT in form C', pr[r_canon_noinput['index']]['C'] == 'key' and pr[r_canon_noinput['index']]['K'] == 'prepared')
check('push: VS stored start 0 but chain gives 3', pr[r_push['index']]['K'] == 'push')
check('shape', pr[r_shape['index']]['K'] == 'shape')
check('ident', pr[r_ident['index']]['K'] == 'ident')
check('translate (VS after PS crashed in T)', pr[r_tr['index']]['K'] == 'translate')
check('emit', pr[r_emit['index']]['K'] == 'emit')
check('val', pr[r_val['index']]['K'] == 'val')
check('hang counts as translate', pr[r_hang['index']]['K'] == 'translate')
check('prepared', pr[r_ok['index']]['K'] == 'prepared')
n = len(w.recipes)
check('identity K: prepared + rejected = denominator', out['prepared']['K'] + sum(out['reasons']['K'].values()) == n)
check('R_B K = prepared / denominator', abs(out['rb']['K'] - out['prepared']['K'] / n) < 1e-9)
check('KILL when R_B < 0.90 in both forms', out['word'] in ('KILL', 'NO_POWER') and out['rb']['K'] < 0.9)

# ---- order: a recipe with key AND shape counts key only
w = World()
r = w.graphics()
w.A1[r['stages'][0]['jobsA']['K']]['eq'] = '0'
w.B[r['stages'][1]['jobsB1']['K']['-']] = res(st='SHAPE')
out, _ = run(w)
check('order: key before shape', out['per_recipe'][0]['K'] == 'key')

# ---- harness: out of the denominator, share > 2 % -> NO_POWER
w = World()
for _ in range(99):
    w.graphics()
r = w.graphics()
w.A1[r['stages'][0]['jobsA']['A0']]['eq'] = '0'
out, lines = run(w)
check('harness 1 of 100: not NO_POWER (share 0.01)', out['harness'] == 1 and 'harness_share' not in out['no_power'])
check('harness out of denominator: R_B = 99/99', abs(out['rb']['K'] - 1.0) < 1e-9)
check('harness row', out['per_recipe'][-1]['K'] == 'harness')
for k in range(3):
    w.A1[w.recipes[k]['stages'][1]['jobsA']['A0']]['st'] = 'CRASH'
out, _ = run(w)
check('harness 4 of 100 -> NO_POWER', out['harness'] == 4 and out['word'] == 'NO_POWER')

# ---- KILL / PASS edge at 0.90
w = World()
for _ in range(10):
    w.graphics()
w.B[w.recipes[0]['stages'][1]['jobsB1']['K']['-']]['val'] = '0'
w.B[w.recipes[0]['stages'][1]['jobsB1']['C']['-']]['val'] = '0'
out, _ = run(w)
check('R_B 0.90 exactly in both forms -> PASS_K0', abs(out['rb']['K'] - 0.9) < 1e-9 and out['word'] == 'PASS_K0')
w.B[w.recipes[1]['stages'][1]['jobsB1']['K']['-']]['val'] = '0'
w.B[w.recipes[1]['stages'][1]['jobsB1']['C']['-']]['val'] = '0'
out, _ = run(w)
check('R_B 0.80 both forms -> KILL', out['word'] == 'KILL')
w.B[w.recipes[1]['stages'][1]['jobsB1']['C']['-']]['val'] = '1'
out, _ = run(w)
check('better form decides: K 0.80, C 0.90 -> PASS_K0', out['word'] == 'PASS_K0')

# ---- determinism
w = World()
for _ in range(3):
    w.graphics()
m = w.meta()
A2 = copy.deepcopy(w.A1)
A2[w.recipes[0]['stages'][0]['jobsA']['K']]['spv'] = 'bb'
out, _ = run(w, m=m, A2=A2)
check('nondet -> NO_POWER', out['nondet'] == 1 and 'nondet' in out['no_power'])
A2 = copy.deepcopy(w.A1)
del A2[w.recipes[0]['stages'][0]['jobsA']['C']]
out, _ = run(w, m=m, A2=A2)
check('second run missing a job -> nondet', out['nondet'] == 1)

# ---- comparator
w = World()
for _ in range(3):
    w.graphics()
m = w.meta()
m['comparator'][3]['stride'] = 'nojob'
out, _ = run(w, m=m)
check('comparator 9 of 10 -> NO_POWER', 'comparator' in out['no_power'])
w = World()
w.graphics()
m = w.meta()
w.A1[m['comparator'][0]['stride']] = res(st='CRASH', phase='T')
out, _ = run(w, m=m)
check('comparator crash is not "not equal"', out['comparator']['stride'] == 9 and 'comparator' in out['no_power'])
w = World()
w.graphics()
m = w.meta(comparator=False)
out, _ = run(w, m=m)
check('comparator absent -> NO_POWER', 'comparator' in out['no_power'])

# ---- knobs, signature, layout
w = World()
w.graphics()
out, _ = run(w, h=heads(extra_a=['K KYTY_CBANK_COPY=0']))
check('knob not default in arm A -> NO_POWER', 'knobs_A1' in out['no_power'])
h = heads()
h['B1'] = [x for x in h['B1'] if x != 'K KYTY_FIX_F19=1']
out, _ = run(w, h=h)
check('arm B without KYTY_FIX_F19=1 -> NO_POWER', 'f19_env_B1' in out['no_power'])
h = heads()
h['A1'][0] = 'S signature=KytySC3:deadbeef enabled=1'
out, _ = run(w, h=h)
check('arm A signature member', 'signature_A1' in out['no_power'])
h = heads()
h['A2'][1] = 'S layout=10000:376:216'
out, _ = run(w, h=h)
check('layout member', 'layout_A2' in out['no_power'])
out, _ = run(w)
check('arm B signature is reference only', not any(x.startswith('signature_B') for x in out['no_power']))

# ---- F19 stand control and f19_both
w = World()
for _ in range(2):
    w.graphics(manual_ps=1)
w.graphics()
out, lines = run(w)
check('F19 stand ok, f19_both 2', out['f19_both'] == {'K': 2, 'C': 2} and out['word'] == 'PASS_K0')
j = w.recipes[0]['stages'][1]['jobsB1']['K']['k16UNorm']
w.B[j]['f19'] = '[f19]_stand_format=5_manual_to_native=0_kept_manual=1'
out, _ = run(w)
check('F19 stand wrong at k16 -> NO_POWER', 'f19_stand_K' in out['no_power'])
w = World()
w.graphics(manual_ps=1)
m = w.meta(f19_expected=81)
out, _ = run(w, m=m)
check('F19 permutation count != 81 -> NO_POWER', 'f19_stand_K' in out['no_power'])
w = World()
w.graphics(manual_ps=1)
w.B[w.recipes[0]['stages'][1]['jobsB1']['K']['k8UNorm']]['val'] = '0'
out, _ = run(w)
check('one F19 outcome fails val -> recipe val, f19_both 0', out['per_recipe'][0]['K'] == 'val' and out['f19_both']['K'] == 0)

# ---- b_diff
w = World()
w.graphics(manual_ps=1)
w.graphics()
w.B[w.recipes[1]['stages'][1]['jobsB1']['K']['-']]['eq'] = '0'
w.B[w.recipes[0]['stages'][1]['jobsB1']['K']['k8UNorm']]['eq'] = '0'
w.B[w.recipes[0]['stages'][1]['jobsB1']['C']['k16UNorm']]['eq'] = '0'
out, _ = run(w)
check('b_diff counts non-F19 and k8 mismatches, not k16', len(out['bdiff']) == 2)
w.B[w.recipes[0]['stages'][1]['jobsB1']['K']['k8UNorm']]['ind'] = '1'
out, _ = run(w)
check('b_diff: k8 with an indirect table is not expected equal', len(out['bdiff']) == 1)
check('b_diff does not change the reason (prepared)', out['per_recipe'][1]['K'] == 'prepared')

# ---- manifest / catalogue / denominator members
w = World()
w.graphics()
m = w.meta()
m['manifest']['ok'] = 2
out, _ = run(w, m=m)
check('manifest member', 'manifest' in out['no_power'])
m = w.meta()
m['cache_sigs'] = {SIG: 2, 'KytySC3:other': 1}
out, _ = run(w, m=m)
check('catalogue signature member', 'catalogue' in out['no_power'])
m = w.meta()
m['denominator'] = 1852
out, _ = run(w, m=m)
check('denominator member', 'denominator' in out['no_power'])
m = w.meta()
m['all_jobs'] = ['zzz']
out, _ = run(w, m=m)
check('job without result -> NO_POWER', 'missing_results' in out['no_power'])

print('ALL OK' if not FAILS else 'FAILED %d: %s' % (len(FAILS), ', '.join(FAILS)))
sys.exit(0 if not FAILS else 1)
