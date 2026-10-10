"""F33c2 (HPP-748): reader of the stand KYTY_TEST_EXITFATAL edition 3 TSVs (run_stand_f33c2.py) by ROADMAP s122 item
681(v)(1)-(3) with item 675(d)(1).

    python read_f33c2.py <runs dir>

Members at KYTY_FIX_F21=1:
  CN (681(v)(1)), in every trial: walks 1, nested 0, reenter >= 2, expired 0, expired_seen 0, rc 321, hang 0, crash 0,
     dur_s < 6. Stand control (not a member of the fix): nested_fatal = 1 in every trial - otherwise the arm did not
     raise its second fatal and the reading is 'stand' (edition 4), item 681(v)(5).
  C  (675(d)(1) + 681(v)(2)): walks 1, rc 321, reenter >= 1, nested 0 in every trial; second = crash = hang = cut =
     expired = 0; done_seen = 0 in every trial.
  P2 (675(d)(1)): control in every trial; second = crash = hang = cut = expired = 0.
At KYTY_FIX_F21=0: CN - reference (walks >= 2 and nested >= 1 expected, printed, not a member); C - k1 0 (675(d)(1)).
Every (fix, arm): leftover 0; at =0 no 'FixF21: wait_expired' line.
Last line 'MEMBERS ALL YES' / 'MEMBERS NOT ALL'. Fixtures: test_read_f33c2.py.
"""
import csv
import os
import sys

DUR_LIMIT_S = 6.0  # item 681(v)(1)


def load(runs, fix, arm):
    p = '%s/fix%s/stand_%s.tsv' % (runs, fix, arm)
    if not os.path.exists(p):
        return None
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))


def n(r, k):
    v = r.get(k, '')
    return int(v) if v not in ('', None) else 0


def rc(r):
    return None if r.get('rc', '') == '' else int(r['rc']) & 0xffffffff


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


def dur(r):
    return float(r['dur_s']) if r.get('dur_s', '') != '' else float('inf')


def cn_fails(r):
    """Names of the CN members (681(v)(1)) that this trial fails."""
    f = []
    if n(r, 'walks') != 1:
        f.append('walks')
    if n(r, 'nested') != 0:
        f.append('nested')
    if n(r, 'reenter') < 2:
        f.append('reenter')
    if n(r, 'expired') != 0:
        f.append('expired')
    if n(r, 'expired_seen') != 0:
        f.append('expired_seen')
    if rc(r) != 321:
        f.append('rc')
    if n(r, 'hang') != 0:
        f.append('hang')
    if n(r, 'crash') != 0:
        f.append('crash')
    if not dur(r) < DUR_LIMIT_S:
        f.append('dur')
    return f


def c_fails(r):
    """Names of the C members (675(d)(1) + 681(v)(2)) that this trial fails."""
    f = []
    if n(r, 'walks') != 1:
        f.append('walks')
    if rc(r) != 321:
        f.append('rc')
    if n(r, 'reenter') < 1:
        f.append('reenter')
    if n(r, 'nested') != 0:
        f.append('nested')
    for k in ('second', 'crash', 'hang', 'cut', 'expired'):
        if n(r, k) != 0:
            f.append(k)
    if n(r, 'done_seen') != 0:
        f.append('done_seen')
    return f


def read(runs):
    lines = []
    ok = [True]

    def put(name, good, text):
        ok[0] = ok[0] and good
        lines.append('%-26s %-4s %s' % (name, 'YES' if good else 'NO', text))

    for fix in ('1', '0'):
        for arm in ('CN', 'C', 'P2'):
            rs = load(runs, fix, arm)
            if rs is None:
                continue
            name = '=%s %s %d' % (fix, arm, len(rs))
            if not rs:
                put(name, False, 'no trials')
                continue
            if fix == '1' and arm == 'CN':
                fails = {}
                for r in rs:
                    for k in cn_fails(r):
                        fails.setdefault(k, []).append(r['seed'])
                put(name, not fails,
                    'walks 1, nested 0, reenter>=2, expired 0, expired_seen 0, rc 321, hang 0, crash 0, dur<%.0f s - '
                    'fails %s; reenter min %d; dur %.3f..%.3f; rc %s; cut %d second %d (ref)' % (
                        DUR_LIMIT_S, {k: len(v) for k, v in fails.items()} or 0, min(n(r, 'reenter') for r in rs),
                        min(dur(r) for r in rs), max(dur(r) for r in rs), rcs(rs), cnt(rs, 'cut'), cnt(rs, 'second')))
                nf = sum(1 for r in rs if n(r, 'nested_fatal') == 1)
                put('=1 CN stand nested_fatal', nf == len(rs), 'nested_fatal = 1 in %d of %d (stand control)' % (
                    nf, len(rs)))
            elif fix == '1' and arm == 'C':
                fails = {}
                for r in rs:
                    for k in c_fails(r):
                        fails.setdefault(k, []).append(r['seed'])
                ds = sum(1 for r in rs if n(r, 'done_seen') == 0)
                put(name, not fails,
                    'walks 1, rc 321, reenter>=1, nested 0, classes 0, done_seen 0 - fails %s; done_seen 0 in %d of %d; '
                    '%s; dur max %.3f' % ({k: len(v) for k, v in fails.items()} or 0, ds, len(rs), fmt(classes(rs)),
                                          max(dur(r) for r in rs)))
            elif fix == '1' and arm == 'P2':
                ctl = sum(1 for r in rs if r.get('control') == '1')
                c = classes(rs)
                put(name, ctl == len(rs) and not any(c.values()), 'control %d; %s; rc %s' % (ctl, fmt(c), rcs(rs)))
            elif fix == '0' and arm == 'CN':
                w2 = sum(1 for r in rs if n(r, 'walks') >= 2)
                n1 = sum(1 for r in rs if n(r, 'nested') >= 1)
                nf = sum(1 for r in rs if n(r, 'nested_fatal') == 1)
                put(name, True, 'reference: walks>=2 %d, nested>=1 %d, nested_fatal 1 %d of %d; rc %s; %s; dur %.3f..%.3f'
                    % (w2, n1, nf, len(rs), rcs(rs), fmt(classes(rs)), min(dur(r) for r in rs),
                       max(dur(r) for r in rs)))
            elif fix == '0' and arm == 'C':
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
    return lines, ok[0]


def main():
    runs = sys.argv[1]
    lines, ok = read(runs)
    print('runs', runs)
    for line in lines:
        print(line)
    print('MEMBERS ALL YES' if ok else 'MEMBERS NOT ALL')
    return 0


if __name__ == '__main__':
    sys.exit(main())
