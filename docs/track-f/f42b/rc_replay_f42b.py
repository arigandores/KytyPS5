"""F42b (HPP-780, Red Team; ROADMAP s122 item 694(g)(3), (g)(5)): own recount of the F42a replay arm from the raw lines of
rd_e<EID>.txt (written independently of rdread_f42a.py). Line form:
  [t] eid <E> round <r> arm <o|z|a|op|ap> p0_nonzero <n> word <hex> nz [(idx, 'hex'), ...] img <sha16>
Members (EID 128281): R0 - p0_nonzero = 0 in every replay; K' - o' (op) >= 2 distinct words; K - z >= 2 distinct words;
P3' - a' (ap) one value, equal to the OR of all values of op and ap, image set of ap subset of op; P3 - same for a vs z.
Also: N = 20 per arm, no nonzero word other than 32824; EID 44806 / 84820 - reading lines (values, images).
Outcome by the table R1-R6 (item 694(g)(3)) is printed as 'candidate' only - the reading is the lead's (F42d).
Usage: python rc_replay_f42b.py <replay dir>"""
import ast
import re
import sys
from collections import Counter, defaultdict

D = sys.argv[1]
pat = re.compile(r'eid (\d+) round (\d+) arm (\w+) p0_nonzero (\d+) word ([0-9a-f]{8}) nz (\[.*?\]) img ([0-9a-f]+)')
ok = True


def chk(c, msg):
    global ok
    print(('ok   ' if c else 'FAIL ') + msg)
    ok &= c


res = {}
for eid in ('128281', '44806', '84820'):
    rows = defaultdict(list)
    for ln in open('%s/rd_e%s.txt' % (D, eid), encoding='utf-8', errors='replace'):
        m = pat.search(ln)
        if m:
            e, r, arm, p0, word, nz, img = m.groups()
            assert e == eid
            rows[arm].append((int(r), int(p0), word, ast.literal_eval(nz), img))
    res[eid] = rows
    for arm in ('op', 'ap', 'o', 'z', 'a'):
        v = rows[arm]
        words = Counter(x[2] for x in v)
        imgs = Counter(x[4] for x in v)
        other = sum(1 for x in v for (i, _) in x[3] if i != 32824)
        print('eid %s arm %-2s N %d rounds %s p0>0 %d words %s imgs %s other_nonzero %d' % (
            eid, arm, len(v), sorted(set(x[0] for x in v)) == list(range(1, len(v) + 1)), sum(1 for x in v if x[1] > 0),
            dict(words), dict(imgs), other))
        chk(len(v) == 20, 'eid %s arm %s N = 20' % (eid, arm))
        chk(all(x[1] == 0 for x in v), 'eid %s arm %s R0 p0_nonzero = 0 in every replay' % (eid, arm))
        chk(other == 0, 'eid %s arm %s no nonzero word other than 32824' % (eid, arm))

r = res['128281']


def vals(arm):
    return set(x[2] for x in r[arm])


def imgs(arm):
    return set(x[4] for x in r[arm])


def orall(*arms):
    acc = 0
    for a in arms:
        for v in vals(a):
            acc |= int(v, 16)
    return '%08x' % acc


kp = len(vals('op')) >= 2
k = len(vals('z')) >= 2
p3p = len(vals('ap')) == 1 and vals('ap') == {orall('op', 'ap')} and imgs('ap') <= imgs('op')
p3 = len(vals('a')) == 1 and vals('a') == {orall('z', 'a')} and imgs('a') <= imgs('z')
print("K' (o' >= 2 values) %s; K (z >= 2 values) %s; P3' %s; P3 %s" % (kp, k, p3p, p3))
cand = 'R1' if kp and p3p else ('R2' if (not kp) and k and p3 and len(vals('ap')) == 1 and imgs('ap') <= imgs('op') else
                                 ('R3' if not kp and not k else 'R4/R5 - read by hand'))
print('candidate outcome (not a verdict):', cand)
print('ALL OK' if ok else 'FAIL')
