"""Session 140 step 0 (Probe Designer): PRIOR data for design140.md from the kp137a..h logs (s137, 05431dad, trace 0).

Not census data. Prints per log: full rows (FrameTrace + -draw + -x with n), rows with bda_scan <= 300 (item 40 (e)(1) band),
the same after the schedule start frame; FrameTrace-pm4 sites per row; the arm-0 identity preview
  D0 = pl_proc - 1000*(a_hold + a_wait) - (pl_cmd + pl_gc + pl_sub + pl_eop + pl_bar + pl_pref) - pm4:prefetch - pm4:stream-prefetch
on arm-0 rows of window 10..88 of each GateArm block (item 55 (b)); counts of 'indirect buffer:' / 'branch:' lines.
Usage: python prior140.py > prior140.out.txt
"""
import re, sys, glob, hashlib, statistics as st

FIELD = re.compile(rb'(?:^|\s)([A-Za-z_][\w]*)=(-?\d+)')
SITE = re.compile(rb'\s([\w\-]+)=(\d+)/(\d+)')
GATE = re.compile(rb'GateArm: arm=(\d+) arms=\d+ block=(\d+) frame=(\d+)')
LOGS = sorted(glob.glob('C:/kyty/s137/log_kp137[a-h].txt'))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def scan(p):
    rows, arms, last_n = {}, [], None
    ib = br = 0
    with open(p, 'rb') as f:
        for ln in f:
            if ln.startswith(b'FrameTrace'):
                for pre, sid in ((b'FrameTrace: ', 'm'), (b'FrameTrace-draw: ', 'd'), (b'FrameTrace-x: ', 'x')):
                    if ln.startswith(pre):
                        d = {k.decode(): int(v) for k, v in FIELD.findall(ln[len(pre):])}
                        if 'n' in d:
                            r = rows.setdefault(d['n'], {'_s': set()})
                            for k, v in d.items():
                                r.setdefault(k, v)
                            r['_s'].add(sid)
                            if sid == 'x':
                                last_n = d['n']
                        break
                else:
                    if ln.startswith(b'FrameTrace-pm4:') and last_n is not None:
                        r = rows[last_n]
                        if '_pm4' not in r:
                            r['_pm4'] = {k.decode(): (int(a), int(c)) for k, a, c in SITE.findall(ln[15:])}
                continue
            if ln.startswith(b'GateArm:'):
                m = GATE.match(ln)
                if m:
                    arms.append((int(m.group(3)), int(m.group(1))))
                continue
            if b'indirect buffer:' in ln:
                ib += 1
            elif b'\t branch:' in ln:
                br += 1
    return rows, arms, ib, br


def arm_of(n, arms):
    a = None
    for fr, arm in arms:
        if n >= fr:
            a = (fr, arm)
        else:
            break
    return a


def main():
    tot = []
    for p in LOGS:
        rows, arms, ib, br = scan(p)
        full = {n: r for n, r in rows.items() if r['_s'] >= {'m', 'd', 'x'}}
        start = arms[0][0] if arms else 0
        new_all = sum(1 for r in full.values() if r.get('bda_scan', 10**9) <= 300)
        new_after = sum(1 for n, r in full.items() if n >= start and r.get('bda_scan', 10**9) <= 300)
        after = sum(1 for n in full if n >= start)
        D0, parts = [], {}
        for n, r in full.items():
            a = arm_of(n, arms)
            if a is None or a[1] != 0:
                continue
            p_in = n - a[0]
            if not (10 <= p_in <= 88):
                continue
            need = ('pl_proc_ns', 'a_hold_us', 'a_wait_us', 'pl_cmd_ns', 'pl_gc_ns', 'pl_sub_ns', 'pl_eop_ns', 'pl_bar_ns',
                    'pl_pref_ns', 'pl_cmd_n')
            if any(k not in r for k in need):
                continue
            pm = r.get('_pm4', {})
            pref = pm.get('prefetch', (0, 0))[0]
            spref = pm.get('stream-prefetch', (0, 0))[0]
            gc = pm.get('gc', (0, 0))[0]
            named = (r['pl_cmd_ns'] + r['pl_gc_ns'] + r['pl_sub_ns'] + r['pl_eop_ns'] + r['pl_bar_ns'] + r['pl_pref_ns']) / 1000.0
            out = r['pl_proc_ns'] / 1000.0 - r['a_hold_us'] - r['a_wait_us']
            D0.append(out - named - pref - spref)
            for k, v in (('out_wall', out), ('named', named), ('pm4_prefetch', pref), ('pm4_stream_prefetch', spref),
                         ('pm4_gc', gc), ('pl_cmd_n', r['pl_cmd_n']), ('pl_proc_us', r['pl_proc_ns'] / 1000.0),
                         ('dt_us', r.get('dt_us', 0)), ('draws', r.get('draws', 0))):
                parts.setdefault(k, []).append(v)
        print('LOG %s sha256 %s' % (p, sha(p)))
        print('  full rows %d; bda_scan<=300 all %d; after schedule start (frame %d) %d of %d; indirect-buffer lines %d, branch lines %d'
              % (len(full), new_all, start, new_after, after, ib, br))
        sites = {}
        for r in full.values():
            for k in r.get('_pm4', {}):
                sites[k] = sites.get(k, 0) + 1
        print('  FrameTrace-pm4 site names over full rows: %s' % sorted(sites.items()))
        if D0:
            m = st.mean(D0)
            se = st.stdev(D0) / len(D0) ** 0.5
            print('  arm0 w10-88 rows %d: residual D0 %.1f (2SE %.1f) us/frame' % (len(D0), m, 2 * se))
            for k, v in parts.items():
                print('    %s mean %.1f' % (k, st.mean(v)))
            tot.append((len(D0), m))
        sys.stdout.flush()
    if tot:
        n = sum(a for a, _ in tot)
        print('POOLED arm0 rows %d residual D0 %.1f us/frame (row-weighted)' % (n, sum(a * b for a, b in tot) / n))


if __name__ == '__main__':
    main()
