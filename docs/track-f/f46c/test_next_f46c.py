"""Fixtures of next_f46c.py (Track F link F46c, HPP-800; ROADMAP s122 item 702 (g)(2), (g)(4), (d)(2); item 711 (b)(1); item 716): the
order of the series (f26s_0 -> f26s_1 -> f26s_1b -> t1, c1, ...), settled = ADMITTED or _r1 made, the repeat rule (_r1 after NOT_ADMITTED,
_r2 only with F46C_REPEAT_OK=1), the event rule on every class (kept_applied, kept why=decode, deferred - call; nolayer, levels, range,
partial, layers, exact_stale, off - no call, 'no mark by construction'; NO_APPLY - no call; event not found; f26s_1 two NOT_ADMITTED - all
undetermined), the key from the admitted attempt (_r1 when the base failed), the lock budget of item 716 (149 min 59 s - goes, 150 min 0 s -
goes, 150 min 1 s - stop; an open lock counts to now), strict cp1250 output; the last line is ALL OK.  Early-exit form.  ASCII only.
usage: python test_next_f46c.py [<next_f46c.py under test>]"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'next_f46c.py')
BASE = os.path.join(HERE, 'fx_next_f46c')
_spec = importlib.util.spec_from_file_location('next_f46c_under_test', SRC)
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_next_f46c.py sha256 %s target next_f46c.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
ok = True
DCC = ['0000000571006000', '0000000570aee000', '0000000570b24000', '000000056d898000']


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


CNT = [0]
shutil.rmtree(BASE, ignore_errors=True)


def runs(tags, classes=None, no_apply=None, lock=None, found=None):
    """tags: {tag: status}; f26s_1 events with classes [4]."""
    CNT[0] += 1
    d = os.path.join(BASE, 'r%d' % CNT[0])
    os.makedirs(d)
    classes = classes or ['kept_applied', 'kept why=decode', 'kept_applied', 'kept why=decode']
    no_apply = no_apply or [False] * 4
    found = found or [True] * 4
    for t, st in tags.items():
        os.makedirs(os.path.join(d, t))
        if st is None:
            continue
        ev = [dict(k=k + 1, found=found[k], cls=classes[k], no_apply=no_apply[k], dcc=DCC[k]) for k in range(4)]
        json.dump(dict(status=st, events=ev), open(os.path.join(d, t, 'read.json'), 'w'))
    if lock is not None:
        open(os.path.join(d, 'lock.log'), 'w').write(lock)
    return d


def may(d, tag, now='2026-10-11T20:00:00Z'):
    return X.may(d, tag, X.datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%SZ'))


A, NA = 'ADMITTED', 'NOT_ADMITTED'
d = runs({})
ok &= check('empty: f26s_0 MAY', may(d, 'f26s_0')[0] == 0)
ok &= check('empty: f26s_1 NOT YET', may(d, 'f26s_1')[0] == 7)
ok &= check('empty: t1 NOT YET (f26s_1 not settled)', may(d, 'f26s_t1')[0] == 7)
ok &= check('bad tag usage', may(d, 'f29_v')[0] == 2)
d = runs({'f26s_0': A})
ok &= check('f26s_0 done: f26s_1 MAY, f26s_1b NOT YET, f26s_0 exists', may(d, 'f26s_1')[0] == 0 and may(d, 'f26s_1b')[0] == 7 and
            may(d, 'f26s_0')[0] == 7)
d = runs({'f26s_0': NA})
ok &= check('f26s_0 NOT_ADMITTED: f26s_1 NOT YET, f26s_0_r1 MAY, f26s_0_r2 REPEAT RULE', may(d, 'f26s_1')[0] == 7 and
            may(d, 'f26s_0_r1')[0] == 0 and may(d, 'f26s_0_r2')[0] == 11)
d = runs({'f26s_0': NA, 'f26s_0_r1': NA})
ok &= check('f26s_0 two NOT_ADMITTED: settled, f26s_1 MAY', may(d, 'f26s_1')[0] == 0)
os.environ.pop('F46C_REPEAT_OK', None)
ok &= check('f26s_0_r2 without the lead item - REPEAT RULE', may(d, 'f26s_0_r2')[0] == 11)
os.environ['F46C_REPEAT_OK'] = '1'
ok &= check('f26s_0_r2 with F46C_REPEAT_OK=1 - MAY', may(d, 'f26s_0_r2')[0] == 0)
os.environ.pop('F46C_REPEAT_OK', None)
d = runs({'f26s_0': A, 'f26s_0_r1': None})
ok &= check('_r1 of an ADMITTED tag - REPEAT RULE', may(d, 'f26s_0_r1')[0] in (7, 11))
d = runs({'f26s_0': A, 'f26s_1': None})
ok &= check('f26s_1 running (no read.json): f26s_1b NOT YET', may(d, 'f26s_1b')[0] == 7)
d = runs({'f26s_0': A, 'f26s_1': A})
ok &= check('f26s_1 done: f26s_1b MAY, t1 NOT YET', may(d, 'f26s_1b')[0] == 0 and may(d, 'f26s_t1')[0] == 7)
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A})
ok &= check('1b done: t1 MAY, c1 NOT YET, t2 NOT YET', may(d, 'f26s_t1')[0] == 0 and may(d, 'f26s_c1')[0] == 7 and may(d, 'f26s_t2')[0] == 7)
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A, 'f26s_t1': A})
ok &= check('t1 done: c1 MAY', may(d, 'f26s_c1')[0] == 0)
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A, 'f26s_t1': A, 'f26s_c1': A})
ok &= check('c1 done: t2 MAY', may(d, 'f26s_t2')[0] == 0)
# event rule on every class
for cls, call in (('kept_applied', True), ('kept why=decode', True), ('kept why=deferred', True), ('kept why=nolayer', False),
                  ('kept why=levels', False), ('kept why=range', False), ('kept why=partial', False), ('kept why=layers', False),
                  ('exact_stale', False), ('off', False), ('fallback', False)):
    d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A}, classes=[cls, 'kept_applied', 'kept_applied', 'kept_applied'])
    rc, msg = may(d, 'f26s_t1')
    rk = X.event_rule(d)[0]
    ok &= check('class %s: t1 %s (%s)' % (cls, 'MAY' if call else 'EVENT RULE', msg), (rc == 0) == call and (rc == 8) == (not call) and
                rk[1] == call and (call or 'no mark by construction' in rk[3]))
    if not call:
        ok &= check('class %s: c1 EVENT RULE, t2 MAY (S1 skipped)' % cls, may(d, 'f26s_c1')[0] == 8 and may(d, 'f26s_t2')[0] == 0)
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A}, no_apply=[False, True, False, False])
ok &= check('S2 NO_APPLY: t2 EVENT RULE "not distinguishable"', may(d, 'f26s_t2')[0] == 8 and 'not distinguishable' in X.event_rule(d)[1][3])
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A}, found=[True, True, False, True])
ok &= check('S3 not found: t3 EVENT RULE', may(d, 'f26s_t3')[0] == 8)
d = runs({'f26s_0': A, 'f26s_1': NA, 'f26s_1_r1': NA, 'f26s_1b': A})
ok &= check('f26s_1 two NOT_ADMITTED: every event undetermined, t1 EVENT RULE', all(not e[1] for e in X.event_rule(d)) and
            may(d, 'f26s_t1')[0] == 8)
d = runs({'f26s_0': A, 'f26s_1': NA, 'f26s_1_r1': A, 'f26s_1b': A})
ok &= check('f26s_1 base NOT_ADMITTED, _r1 ADMITTED: key from _r1, t1 MAY', may(d, 'f26s_t1')[0] == 0 and X.event_rule(d)[0][2] == '0x571006000')
ok &= check('order with 4 calls', X.order(runs({'f26s_0': A, 'f26s_1': A}))[0] == ['f26s_0', 'f26s_1', 'f26s_1b', 'f26s_t1', 'f26s_c1', 'f26s_t2',
                                                                              'f26s_c2', 'f26s_t3', 'f26s_c3', 'f26s_t4', 'f26s_c4'])
# budget (item 716)
def lock(sec_total, open_last=False):
    t0 = X.datetime.datetime(2026, 10, 11, 12, 0, 0)
    a = X.datetime.timedelta(seconds=sec_total - 60)
    s = 'lock taken f26s_0 %sZ\nlock released f26s_0 %sZ\n' % (t0.isoformat(), (t0 + a).isoformat())
    t1 = t0 + a + X.datetime.timedelta(seconds=100)
    if open_last:
        s += 'lock taken f26s_1 %sZ\n' % t1.isoformat()
    else:
        s += 'lock taken f26s_1 %sZ\nlock released f26s_1 %sZ\n' % (t1.isoformat(), (t1 + X.datetime.timedelta(seconds=60)).isoformat())
    return s
for sec, rc in ((8999, 0), (9000, 0), (9001, 12)):
    d = runs({'f26s_0': A, 'f26s_1': A}, lock=lock(sec))
    ok &= check('budget %d s -> %s' % (sec, rc), may(d, 'f26s_1b')[0] == rc and X.lock_sum(d)[0] == sec)
d = runs({'f26s_0': A, 'f26s_1': A}, lock=lock(3600, open_last=True))
ok &= check('open lock counts to now and blocks', may(d, 'f26s_1b')[0] in (7, 12))
s0, op = X.lock_sum(d, X.datetime.datetime(2026, 10, 11, 13, 0, 40))
ok &= check('open lock to now: sum %d open %s' % (s0, op), op == ['f26s_1'] and s0 == 3540 + (13 * 3600 + 40 - (12 * 3600 + 3540 + 100))
            - 0)
# CLI: --key, --budget, cp1250
d = runs({'f26s_0': A, 'f26s_1': A, 'f26s_1b': A})
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
p = subprocess.run([sys.executable, SRC, '--key', '4', '--runs', d], capture_output=True, env=env)
ok &= check('CLI --key 4 -> 0x56d898000', p.returncode == 0 and p.stdout.strip() == b'0x56d898000')
d2 = runs({'f26s_0': A, 'f26s_1': A}, classes=['kept why=layers'] * 4)
p = subprocess.run([sys.executable, SRC, '--key', '1', '--runs', d2], capture_output=True, env=env)
ok &= check('CLI --key 1 on layers -> exit 8', p.returncode == 8)
p = subprocess.run([sys.executable, SRC, '--plan', '--runs', d], capture_output=True, env=env)
ok &= check('CLI --plan ASCII cp1250 strict', p.returncode == 0 and all(c < 128 for c in p.stdout) and b'S4 CALL key 0x56d898000' in p.stdout)
d3 = runs({}, lock=lock(9001))
p = subprocess.run([sys.executable, SRC, '--budget', '--runs', d3], capture_output=True, env=env)
ok &= check('CLI --budget 9001 -> exit 12', p.returncode == 12 and b'BUDGET EXCEEDED' in p.stdout)
shutil.rmtree(BASE, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok and N[1] == 0:
    print('ALL OK')
sys.exit(0 if ok and N[1] == 0 else 1)
