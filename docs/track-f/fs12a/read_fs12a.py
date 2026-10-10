"""FS12a (HPP-750; ROADMAP s122 item 683(g)(1)): reader of the stand KYTY_TEST_EXITFATAL TSVs of the FS12 binary
(run_stand_fs12a.py) - the members of item 675(d)(1) with item 678(v), 680(b), 681(v)(1)-(2) at the DEFAULT (KYTY_FIX_F21
not set, runs/fixd/) and the control KYTY_FIX_F21=0 (runs/fix0/). Port of read_f33c.py (a4212bed) and read_f33c2.py
(66ec6149): the member functions are theirs; the arm set and N are those of item 683(g)(1).

    python read_fs12a.py <runs dir>   -> member table; last line 'MEMBERS ALL YES' / 'MEMBERS NOT ALL'

Default (fixd), seeds exactly 1..N:
  P2 200 - control 200 of 200; second = crash = hang = cut = expired = 0 (675(d)(1)).
  C 50   - walks 1, rc 321, reenter >= 1, nested 0, classes 0, done_seen 0 in every trial (675(d)(1), 681(v)(2)).
  CN 50  - walks 1, nested 0, reenter >= 2, expired 0, expired_seen 0, rc 321, hang 0, crash 0, dur < 6 s in every trial
           (681(v)(1)); stand control: nested_fatal = 1 in every trial.
  H 20   - order executed (control) 20, expired >= 1 in 20 of 20, rc in {0, 321} (crash 0), hang 0, second 0 (678(b) with
           680(b)); rc distribution, dt and cut - reference.
  HG 20  - expired >= 1 in 20 of 20, rc 0 in 20, hang 0, second 0, dt (first entry of the main thread -> process end) in
           [12; 13.5] s in 20 of 20 (678(v)); cut - reference.
  every trial: cfg_fix = 1 (the stand's 'ExitFatal: config ... fix=1') and the line 'FixF21: mode=1' in its _kyty.txt
           copy / stdout / stderr (item 683(g)(1): "FixF21: mode=1 in every trial").
Control (fix0): P2 200 - second >= 1 (675(d)(1)); cfg_fix = 0 and 'FixF21: mode=0' in every trial; no 'FixF21:
  wait_expired' line.
Every (fix, arm): leftover 0.
"""
import csv
import os
import sys

DUR_LIMIT_S = 6.0  # item 681(v)(1)
HG_DT = (12.0, 13.5)  # item 678(v)
PLAN = [('d', 'P2', 200), ('d', 'C', 50), ('d', 'CN', 50), ('d', 'H', 20), ('d', 'HG', 20), ('0', 'P2', 200)]
CLS = ('second', 'crash', 'hang', 'cut', 'expired')


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
    return {k: cnt(rs, k) for k in CLS}


def fmt(c):
    return ' '.join('%s %d' % kv for kv in c.items())


def rcs(rs):
    out = {}
    for r in rs:
        out[rc(r)] = out.get(rc(r), 0) + 1
    return out


def dur(r):
    return float(r['dur_s']) if r.get('dur_s', '') != '' else float('inf')


def mode_seen(runs, fix, arm, seed, want):
    base = '%s/fix%s/%s/%s' % (runs, fix, arm, seed)
    for ext in ('.log', '.out', '.err'):
        if os.path.exists(base + ext):
            t = open(base + ext, 'rb').read().decode('utf-8', 'replace')
            if ('FixF21: mode=%s ' % want) in t or t.rstrip().endswith('FixF21: mode=%s' % want):
                return True
    return False


def cn_fails(r):
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
    f = []
    if n(r, 'walks') != 1:
        f.append('walks')
    if rc(r) != 321:
        f.append('rc')
    if n(r, 'reenter') < 1:
        f.append('reenter')
    if n(r, 'nested') != 0:
        f.append('nested')
    for k in CLS:
        if n(r, k) != 0:
            f.append(k)
    if n(r, 'done_seen') != 0:
        f.append('done_seen')
    return f


def h_fails(r):
    f = []
    if n(r, 'control') != 1:
        f.append('order')
    if n(r, 'expired') < 1:
        f.append('expired')
    if rc(r) not in (0, 321) or n(r, 'crash') != 0:
        f.append('rc/crash')
    if n(r, 'hang') != 0:
        f.append('hang')
    if n(r, 'second') != 0:
        f.append('second')
    return f


def hg_fails(r):
    f = []
    if n(r, 'expired') < 1:
        f.append('expired')
    if rc(r) != 0:
        f.append('rc')
    if n(r, 'hang') != 0:
        f.append('hang')
    if n(r, 'second') != 0:
        f.append('second')
    dt = r.get('h_dt_s', '')
    if dt == '' or not (HG_DT[0] <= float(dt) <= HG_DT[1]):
        f.append('dt')
    return f


def fails_text(rs, fn):
    fails = {}
    for r in rs:
        for k in fn(r):
            fails.setdefault(k, []).append(r['seed'])
    return fails


def read(runs):
    lines = []
    ok = [True]

    def put(name, good, text):
        ok[0] = ok[0] and good
        lines.append('%-28s %-4s %s' % (name, 'YES' if good else 'NO', text))

    for fix, arm, N in PLAN:
        rs = load(runs, fix, arm)
        name = '%s %s %d' % ('default' if fix == 'd' else '=0', arm, N)
        if not rs:
            put(name, False, 'no trials')
            continue
        seeds = sorted(int(r['seed']) for r in rs)
        put(name + ' seeds', seeds == list(range(1, N + 1)), 'n %d, seeds 1..%d exactly: %s' % (
            len(rs), N, seeds == list(range(1, N + 1))))
        if fix == 'd' and arm == 'P2':
            ctl = sum(1 for r in rs if n(r, 'control') == 1)
            c = classes(rs)
            put(name, ctl == len(rs) and not any(c.values()), 'control %d; %s; rc %s' % (ctl, fmt(c), rcs(rs)))
        elif fix == 'd' and arm == 'C':
            fl = fails_text(rs, c_fails)
            ds = sum(1 for r in rs if n(r, 'done_seen') == 0)
            put(name, not fl, 'walks 1, rc 321, reenter>=1, nested 0, classes 0, done_seen 0 - fails %s; done_seen 0 in %d '
                'of %d; reenter min %d; %s; dur max %.3f' % ({k: len(v) for k, v in fl.items()} or 0, ds, len(rs),
                                                              min(n(r, 'reenter') for r in rs), fmt(classes(rs)),
                                                              max(dur(r) for r in rs)))
        elif fix == 'd' and arm == 'CN':
            fl = fails_text(rs, cn_fails)
            put(name, not fl, 'walks 1, nested 0, reenter>=2, expired 0, expired_seen 0, rc 321, hang 0, crash 0, dur<%.0f s - '
                'fails %s; reenter min %d; dur %.3f..%.3f; rc %s; cut %d second %d (ref)' % (
                    DUR_LIMIT_S, {k: len(v) for k, v in fl.items()} or 0, min(n(r, 'reenter') for r in rs),
                    min(dur(r) for r in rs), max(dur(r) for r in rs), rcs(rs), cnt(rs, 'cut'), cnt(rs, 'second')))
            nf = sum(1 for r in rs if n(r, 'nested_fatal') == 1)
            put('default CN stand nested_fatal', nf == len(rs), 'nested_fatal = 1 in %d of %d (stand control)' % (nf, len(rs)))
        elif fix == 'd' and arm == 'H':
            fl = fails_text(rs, h_fails)
            dts = sorted(float(r['h_dt_s']) for r in rs if r.get('h_dt_s', '') != '')
            put(name, not fl, 'order 1, expired>=1, rc in {0,321}, crash 0, hang 0, second 0 - fails %s; rc %s; dt_s %.3f..%.3f '
                '(ref); cut %d (ref)' % ({k: len(v) for k, v in fl.items()} or 0, rcs(rs), dts[0] if dts else -1,
                                         dts[-1] if dts else -1, cnt(rs, 'cut')))
        elif fix == 'd' and arm == 'HG':
            fl = fails_text(rs, hg_fails)
            dts = sorted(float(r['h_dt_s']) for r in rs if r.get('h_dt_s', '') != '')
            put(name, not fl, 'expired>=1, rc 0, hang 0, second 0, dt in [%.1f; %.1f] - fails %s; rc %s; dt_s %.3f..%.3f; cut %d '
                '(ref); control %d (ref)' % (HG_DT[0], HG_DT[1], {k: len(v) for k, v in fl.items()} or 0, rcs(rs),
                                              dts[0] if dts else -1, dts[-1] if dts else -1, cnt(rs, 'cut'),
                                              cnt(rs, 'control')))
        elif fix == '0' and arm == 'P2':
            sec = cnt(rs, 'second')
            put(name, sec >= 1, 'second %d (>= 1); control %d; %s; rc %s' % (sec, cnt(rs, 'control'), fmt(classes(rs)),
                                                                              rcs(rs)))
            e = sum(n(r, 'expired') for r in rs)
            put('=0 P2 no wait_expired', e == 0, 'FixF21: wait_expired lines %d' % e)
        want = '1' if fix == 'd' else '0'
        bad_cfg = [r['seed'] for r in rs if r.get('cfg_fix', '') != want]
        miss = [r['seed'] for r in rs if not mode_seen(runs, fix, arm, r['seed'], want)]
        put(name + ' mode', not bad_cfg and not miss, "cfg_fix=%s in %d of %d; 'FixF21: mode=%s' in %d of %d" % (
            want, len(rs) - len(bad_cfg), len(rs), want, len(rs) - len(miss), len(rs)))
        lo = sum(n(r, 'leftover') for r in rs)
        put(name + ' leftover', lo == 0, 'leftover copies %d' % lo)
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
