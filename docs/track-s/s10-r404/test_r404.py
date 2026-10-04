"""test_r404.py - track S link S10 (HPP-433; ROADMAP "SESSION 122" item 404 (g)): the fixtures of item 404 on the REAL logs of the
five arms made under seal 06b (C:/kyty/s288/s10): (1) c5_0 - on the domain T-1 4 183 / 4 183 and T-6 150 / 150 PASS, the data
row of the whole log T-1 4 251 / 4 271 and T-6 171 / 170, the arm admitted (the original scorer b8f5e3fa: FAIL on T-1 and T-6
only); (5) pi_w1, pi_r1, pi_w0, pi_r0 - the outcome and every printed member equal under the original scorer (r404/orig/sc_s9.py,
sha256 b8f5e3fa, seal 06b) and the new one, apart from the rows T-1 / T-6 (now on the domain, plus the whole-log data row whose
values are the original rows) and the name of the prereg row; and c5_0 - every printed member equal apart from the same rows.
The synthetic fixtures (2) - (4) and the prior-seal rows are in s9/test_sc_s9.py.  No process is started.  ASCII; ends ALL OK.
    python C:/kyty/s288/s10/r404/test_r404.py [<sc_s9 under test>]
"""
import hashlib
import importlib.util
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s9/sc_s9.py'
OLD = os.path.join(HERE, 'orig', 'sc_s9.py')
ORIG_SHA = 'b8f5e3faed8c512873553293372e509e4ccfafaedb5d0e4d216da3ead580e39a'
P06B = 'C:/kyty/s288/pred/06b_s.md'
SHA06B = '605ebfa5440ea1ac318749250c625b022f873d0237b37294cc97ffb069e3560b'
ROOT = 'C:/kyty/s288/s10'
C5_LOG_SHA = '138f4efe8323069574c8559618555bc2f032b868f5a70ac0b466ed7b00eec380'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_r404.py sha256 %s target sc_s9.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(NEW)))


def load(p, name):
    sp = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


ok = True
ok &= case('R0 the original scorer is b8f5e3fa and the seal 06b is 605ebfa5 (not changed)',
           sha(OLD) == ORIG_SHA and sha(P06B) == SHA06B)
S0 = load(OLD, 'sc_s9_orig')
S1 = load(NEW, 'sc_s9_new')
ID_OLD = ('T-1 sum skc_ap_skip = skipped-draw lines', 'T-6 distinct frame= of skipped draws = sum skc_held_inc (main)')
PREREG_OLD = 'prereg = the seal now'
PREREG_NEW = 'prereg = the seal now (or the seal 06b for the five arms made under it, item 404 (g))'


def norm_old(lines):
    """The printed lines of the original scorer without the T-1 / T-6 rows (returned apart) and with the prereg row name of now."""
    rest, ids = [], {}
    for x in lines:
        s = x.strip()
        hit = [k for k in ID_OLD if (' ident %s (' % k) in x]
        if hit:
            ids[hit[0][:3]] = s
            continue
        rest.append(x.replace(' admit %s (' % PREREG_OLD, ' admit %s (' % PREREG_NEW))
    return rest, ids


def norm_new(lines):
    rest, ids, data = [], {}, None
    for x in lines:
        if ' ident T-1 / T-6 whole log (data, item 404) (' in x:
            data = x.strip()
            continue
        if ' ident T-1 sum skc_ap_skip = skipped-draw lines, on the domain' in x:
            ids['T-1'] = x.strip()
            continue
        if ' ident T-6 distinct frame= of skipped draws = sum skc_held_inc (main), on the domain' in x:
            ids['T-6'] = x.strip()
            continue
        rest.append(x)
    return rest, ids, data


def det(row):
    """The detail of a printed identity row: the text inside the last parentheses."""
    return row[row.rfind('(') + 1:-1] if row else None


res = {}
for tag in ('c5_0', 'pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'):
    t0 = time.time()
    r0 = S0.score_arm(tag, None, ROOT, SHA06B, P06B, None, True)
    r1 = S1.score_arm(tag, None, ROOT, None, S1.PRED_PATH, None, True)
    f0, f1 = S0.fmt_arm(r0), S1.fmt_arm(r1)
    o_rest, o_ids = norm_old(f0)
    n_rest, n_ids, n_data = norm_new(f1)
    res[tag] = (r0, r1, o_rest, o_ids, n_rest, n_ids, n_data)
    print('scored %s in %.1f s: original %s %s, new %s %s' % (tag, time.time() - t0, 'PASS' if not r0['fail'] else 'FAIL',
                                                             r0['fail'], 'PASS' if not r1['fail'] else 'FAIL', r1['fail']))
    for x in sorted(n_ids.values()) + [n_data]:
        print('  new %s' % x)

r0, r1, o_rest, o_ids, n_rest, n_ids, n_data = res['c5_0']
ok &= case('R1a c5_0 log sha256 138f4efe (the log of the arm, not changed)', r1.get('log_sha') == C5_LOG_SHA or
           sha(ROOT + '/log_c5_0.txt') == C5_LOG_SHA)
ok &= case('R1b c5_0 original: FAIL on T-1 and T-6 only (4251 / 4271, 171 / 170)',
           sorted(r0['fail']) == sorted(['identity: ' + ID_OLD[0], 'identity: ' + ID_OLD[1]]) and
           det(o_ids.get('T-1')) == '4251 / 4271' and det(o_ids.get('T-6')) == '171 / 170')
ok &= case('R1c c5_0 new: T-1 on the domain frame >= 240 PASS 4183 / 4183 (0 lines without frame=), T-6 PASS 150 / 150',
           (n_ids.get('T-1') or '').startswith('PASS ident T-1 sum skc_ap_skip = skipped-draw lines, on the domain frame >= the '
                                                'first scene frame 240 (item 404) (4183 / 4183 (lines without frame= 0))') and
           (n_ids.get('T-6') or '').startswith('PASS ident T-6') and det(n_ids.get('T-6')) == '150 / 150' and
           ' frame 240 (item 404)' in n_ids.get('T-6', ''))
ok &= case('R1d c5_0 new: the data row of the whole log T-1 4251 / 4271; T-6 171 / 170, not a member (n/a)',
           n_data == 'n/a  ident T-1 / T-6 whole log (data, item 404) (T-1 4251 / 4271; T-6 171 / 170)')
ok &= case('R1e c5_0 new: admitted (no failure), entered, the first scene frame n 240', r1['fail'] == [] and r1['entered'] and
           r1['first'][0] == 240)
ok &= case('R1f c5_0: every other printed line equal (the outcome line PASS / FAIL apart)',
           [x for x in o_rest[1:]] == [x for x in n_rest[1:]] and o_rest[0].replace(': FAIL;', ': PASS;') == n_rest[0])
f5, w5, _ = S1.read_c5(lambda t: r1 if t == 'c5_0' else None)
ok &= case('R1g c5_0 C5 reading by the letter of item 355 (d): 630 creations median 215 -> NO -> form APP',
           r1['create']['n'] == 630 and r1['create']['med'] == 215 and (f5, w5) == ('app', 'NO'))
for tag in ('pi_w1', 'pi_r1', 'pi_w0', 'pi_r0'):
    r0, r1, o_rest, o_ids, n_rest, n_ids, n_data = res[tag]
    ok &= case('R5 %s: the outcome and every printed member equal (original %s, new %s); T-1 / T-6 PASS on the domain; the data '
               'row = the original rows (%s; %s)' % (tag, 'PASS' if not r0['fail'] else 'FAIL', 'PASS' if not r1['fail'] else 'FAIL',
                                                    det(o_ids.get('T-1')), det(o_ids.get('T-6'))),
               r0['fail'] == r1['fail'] == [] and o_rest == n_rest and
               (n_ids.get('T-1') or '').startswith('PASS') and (n_ids.get('T-6') or '').startswith('PASS') and
               n_data == 'n/a  ident T-1 / T-6 whole log (data, item 404) (T-1 %s; T-6 %s)' % (det(o_ids.get('T-1')),
                                                                                            det(o_ids.get('T-6'))) and
               (o_ids.get('T-1') or '').startswith('PASS') and (o_ids.get('T-6') or '').startswith('PASS'))
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
