"""F33d (HPP-745): own reading of stand edition 2 TSVs (run_stand_f33d.py) by ROADMAP s122 item 675(d)(1) with item 678
(arms H, HG) and item 680(b) (H: rc in {0, 321}). Independent of read_f33c.py (written from the letter of the items).

    python read_f33d.py <runs dir> [label]

Prints one line per (fix, arm) present: member YES/NO and the counts. Last line 'MEMBERS ALL YES' / 'MEMBERS NOT ALL'.
For a mutant runs dir the expected outcome is NO on the arm that must catch it ('caught' = the member fails).
"""
import csv
import os
import sys

RUNS = sys.argv[1]
LABEL = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(RUNS.rstrip('/'))


def rows(fix, arm):
    p = '%s/fix%s/stand_%s.tsv' % (RUNS, fix, arm)
    if not os.path.exists(p):
        return None
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))


def n(r, k):
    v = r.get(k, '')
    return int(v) if v not in ('', None) else 0


def rc(r):
    return None if r['rc'] == '' else int(r['rc']) & 0xffffffff


def cnt(rs, k):
    return sum(1 for r in rs if n(r, k) > 0)


def classes(rs):
    return {k: cnt(rs, k) for k in ('second', 'crash', 'hang', 'cut', 'expired')}


def fmt(c):
    return ' '.join('%s %d' % kv for kv in c.items())


def rcs(rs):
    out = {}
    for r in rs:
        out[rc(r)] = out.get(rc(r), 0) + 1
    return out


lines = []
ok_all = True


def put(name, ok, text):
    global ok_all
    ok_all = ok_all and ok
    lines.append('%-26s %-4s %s' % (name, 'YES' if ok else 'NO', text))


for fix in ('1', '0'):
    for arm in ('P2', 'R2', 'G', 'C', 'N', 'H', 'HG'):
        rs = rows(fix, arm)
        if rs is None:
            continue
        name = '=%s %s %d' % (fix, arm, len(rs))
        ctl = sum(1 for r in rs if r['control'] == '1')
        live = [r for r in rs if r['control'] == '1']
        if fix == '1' and arm == 'P2':
            c = classes(rs)
            put(name, ctl == len(rs) and not any(c.values()), 'control %d; %s; rc %s' % (ctl, fmt(c), rcs(rs)))
        elif fix == '1' and arm == 'R2':
            c = classes(live)
            put(name, not any(c.values()), 'live %d; live: %s; all: %s' % (len(live), fmt(c), fmt(classes(rs))))
        elif fix == '1' and arm == 'G':
            c = classes(live)
            put(name, len(live) >= min(100, len(rs) // 2) and not any(c.values()),
                'live %d; live: %s; all: %s' % (len(live), fmt(c), fmt(classes(rs))))
        elif fix == '1' and arm == 'C':
            bad = [r['seed'] for r in rs
                   if not (n(r, 'walks') == 1 and rc(r) == 321 and n(r, 'reenter') >= 1 and n(r, 'nested') == 0)]
            put(name, not bad and not any(classes(rs).values()),
                'walks==1 rc 321 reenter>=1 nested 0 - fails %d %s; reenter min %d; %s; dur max %.2f' % (
                    len(bad), bad[:5], min(n(r, 'reenter') for r in rs), fmt(classes(rs)),
                    max(float(r['dur_s']) for r in rs)))
        elif fix == '1' and arm == 'N':
            bad = [r['seed'] for r in rs if not (n(r, 'walks') == 1 and rc(r) == 0 and n(r, 'k1') == 0)]
            put(name, not bad, 'walks==1 rc 0 k1 0 - fails %d %s' % (len(bad), bad[:5]))
        elif fix == '1' and arm == 'H':
            order = sum(1 for r in rs if r['control'] == '1')
            exp = sum(1 for r in rs if n(r, 'expired') >= 1)
            okrc = sum(1 for r in rs if rc(r) in (0, 321))
            c = classes(rs)
            dts = [float(r['h_dt_s']) for r in rs if r['h_dt_s']]
            put(name, order == len(rs) and exp == len(rs) and okrc == len(rs) and c['hang'] == 0 and c['second'] == 0
                and c['crash'] == 0,
                'order %d; expired %d; rc %s; hang %d second %d crash %d; cut %d (ref); dt_s %.3f..%.3f (ref)' % (
                    order, exp, rcs(rs), c['hang'], c['second'], c['crash'], c['cut'],
                    min(dts) if dts else -1, max(dts) if dts else -1))
        elif fix == '1' and arm == 'HG':
            order = sum(1 for r in rs if r['control'] == '1')
            exp = sum(1 for r in rs if n(r, 'expired') >= 1)
            ok0 = sum(1 for r in rs if rc(r) == 0)
            c = classes(rs)
            dts = [float(r['h_dt_s']) for r in rs if r['h_dt_s']]
            indt = sum(1 for d in dts if 12.0 <= d <= 13.5)
            put(name, order == len(rs) and exp == len(rs) and ok0 == len(rs) and c['hang'] == 0 and c['second'] == 0
                and indt == len(rs),
                'order %d; expired %d; rc %s; hang %d second %d; dt in [12;13.5] %d; dt_s %.3f..%.3f; cut %d (ref)' % (
                    order, exp, rcs(rs), c['hang'], c['second'], indt, min(dts) if dts else -1,
                    max(dts) if dts else -1, c['cut']))
        elif fix == '0' and arm == 'P2':
            c = classes(rs)
            put(name, c['second'] >= 1, 'control %d; %s; rc %s (=0 control: second >= 1)' % (ctl, fmt(c), rcs(rs)))
        elif fix == '0' and arm in ('C', 'N'):
            k1 = cnt(rs, 'k1')
            put(name, k1 == 0, 'k1 %d; rc %s' % (k1, rcs(rs)))
        else:
            put(name, True, 'not a member (ref): %s' % fmt(classes(rs)))
        if fix == '0':
            e = sum(n(r, 'expired') for r in rs)
            if e:
                put('=0 %s wait_expired' % arm, False, 'lines %d' % e)
        lo = sum(n(r, 'leftover') for r in rs)
        if lo:
            put('%s leftover' % name, False, 'leftover %d' % lo)

print('runs', RUNS, 'label', LABEL)
for line in lines:
    print(line)
print('MEMBERS ALL YES' if ok_all else 'MEMBERS NOT ALL')
