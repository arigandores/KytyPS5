"""F33c (HPP-744): reading of the stand edition 2 TSVs by ROADMAP s122 item 675(d)(1)-(2) with item 678 (arms H, HG).

    python read_f33c.py [runs dir]   -> prints the member table; the last line is 'MEMBERS ALL YES' or 'MEMBERS NOT ALL'

Per arm the TSV runs/fix<f>/stand_<arm>.tsv (run_stand_f33c.py); the line 'FixF21: mode=<f>' is looked for in the
trial's _kyty.txt copy (<seed>.log) and in its stdout/stderr; 'FixF21: wait_expired' is counted from stderr (TSV field).
"""
import csv
import os
import sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/f287/f33c/runs'
CLS = ('second', 'crash', 'hang', 'cut', 'expired')


def rows(fix, arm):
    p = '%s/fix%s/stand_%s.tsv' % (RUNS, fix, arm)
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))


def i(r, k):
    v = r.get(k, '')
    return int(v) if v not in ('', None) else 0


def rcu(r):
    return None if r['rc'] == '' else int(r['rc']) & 0xffffffff


def mode_seen(fix, arm, seed):
    base = '%s/fix%s/%s/%s' % (RUNS, fix, arm, seed)
    for ext in ('.log', '.out', '.err'):
        if os.path.exists(base + ext):
            t = open(base + ext, 'rb').read().decode('utf-8', 'replace')
            if ('FixF21: mode=%s ' % fix) in t or t.rstrip().endswith('FixF21: mode=%s' % fix):
                return True
    return False


def seeds_ok(rs, n):
    return sorted(int(r['seed']) for r in rs) == list(range(1, n + 1))


def cls_sum(rs):
    return {c: sum(1 for r in rs if (i(r, c) > 0)) for c in CLS}


out = []
ok_all = True


def member(name, ok, text):
    global ok_all
    ok_all &= ok
    out.append('%-34s %s  %s' % (name, 'YES' if ok else 'NO ', text))


def dts(rs):
    v = sorted(float(r['h_dt_s']) for r in rs if r['h_dt_s'] != '')
    return v


# --- =1 ---
P2 = rows('1', 'P2')
c = cls_sum(P2)
ctl = sum(i(r, 'control') for r in P2)
member('(1) =1 P2 600', seeds_ok(P2, 600) and ctl == 600 and not any(c.values()),
       'n %d control %d; %s' % (len(P2), ctl, ' '.join('%s %d' % kv for kv in c.items())))
R2 = rows('1', 'R2')
live = [r for r in R2 if i(r, 'control') == 1]
c = cls_sum(live)
c_all = cls_sum(R2)
member('(1) =1 R2 600 (live control)', seeds_ok(R2, 600) and not any(c.values()),
       'n %d live %d; live: %s; all: %s' % (len(R2), len(live), ' '.join('%s %d' % kv for kv in c.items()),
                                            ' '.join('%s %d' % kv for kv in c_all.items())))
G = rows('1', 'G')
live = sum(i(r, 'control') for r in G)
c = cls_sum(G)
member('(1) =1 G 200', seeds_ok(G, 200) and live >= 100 and not any(c.values()),
       'n %d live %d; %s' % (len(G), live, ' '.join('%s %d' % kv for kv in c.items())))
C = rows('1', 'C')
bad = [r['seed'] for r in C if not (i(r, 'walks') == 1 and rcu(r) == 321 and i(r, 'reenter') >= 1
                                     and i(r, 'nested') == 0)]
member('(1) =1 C 50', seeds_ok(C, 50) and not bad,
       'n %d; walks==1, rc 321, reenter>=1, nested 0 fails %d %s; reenter min %d max %d; k1 %d' % (
           len(C), len(bad), bad[:5], min(i(r, 'reenter') for r in C), max(i(r, 'reenter') for r in C),
           sum(i(r, 'k1') for r in C)))
N = rows('1', 'N')
bad = [r['seed'] for r in N if not (i(r, 'walks') == 1 and rcu(r) == 0 and i(r, 'k1') == 0)]
member('(1) =1 N 50', seeds_ok(N, 50) and not bad, 'n %d; walks==1, rc 0, k1 0 fails %d %s' % (len(N), len(bad),
                                                                                               bad[:5]))
for arm in ('H', 'HG'):
    R = rows('1', arm)
    order = sum(i(r, 'control') for r in R)
    exp = sum(1 for r in R if i(r, 'expired') >= 1)
    rc0 = sum(1 for r in R if rcu(r) == 0)
    hang = sum(i(r, 'hang') for r in R)
    sec = sum(i(r, 'second') for r in R)
    v = dts(R)
    ok = seeds_ok(R, 20) and order == 20 and exp == 20 and rc0 == 20 and hang == 0 and sec == 0
    extra = ''
    if arm == 'HG':
        inside = sum(1 for x in v if 12.0 <= x <= 13.5)
        ok = ok and inside == 20 and len(v) == 20
        extra = '; dt in [12;13.5] %d of %d' % (inside, len(v))
    member('(1) =1 %s 20 (item 678)' % arm, ok,
           'n %d order executed %d; expired %d rc0 %d hang %d second %d%s; dt_s min %.3f max %.3f (ref); cut %d (ref); '
           'expired lines max %d' % (len(R), order, exp, rc0, hang, sec, extra, v[0] if v else -1, v[-1] if v else -1,
                                     sum(i(r, 'cut') for r in R), max(i(r, 'expired') for r in R) if R else -1))
# --- =0 control ---
P20 = rows('0', 'P2')
sec = sum(i(r, 'second') for r in P20)
member('(1) =0 P2 200', seeds_ok(P20, 200) and sec >= 1,
       'n %d second %d; control %d; %s' % (len(P20), sec, sum(i(r, 'control') for r in P20),
                                          ' '.join('%s %d' % kv for kv in cls_sum(P20).items())))
for arm in ('C', 'N'):
    R = rows('0', arm)
    k1 = sum(i(r, 'k1') for r in R)
    member('(1) =0 %s 50' % arm, seeds_ok(R, 50) and k1 == 0,
           'n %d k1 %d; rc %s' % (len(R), k1, sorted(set(rcu(r) for r in R))))
# --- (2) ---
allr = {}
for fix in ('0', '1'):
    for arm in ('P2', 'R2', 'G', 'C', 'N', 'H', 'HG'):
        allr[(fix, arm)] = rows(fix, arm)
exp0 = sum(i(r, 'expired') for (f, a), rs in allr.items() if f == '0' for r in rs)
member('(2) =0 no wait_expired', exp0 == 0, 'wait_expired lines at =0: %d' % exp0)
miss = []
tot = 0
for (f, a), rs in allr.items():
    for r in rs:
        tot += 1
        if not mode_seen(f, a, r['seed']):
            miss.append('%s/%s/%s' % (f, a, r['seed']))
member('(2) FixF21: mode=<value> by value', not miss, 'trials %d, without the line of their value %d %s' % (
    tot, len(miss), miss[:5]))
left = sum(i(r, 'leftover') for rs in allr.values() for r in rs)
out.append('%-34s      %s' % ('leftover copies after trials', left))
print('\n'.join(out))
print('MEMBERS ALL YES' if ok_all else 'MEMBERS NOT ALL')
