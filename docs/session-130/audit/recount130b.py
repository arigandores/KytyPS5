# Variant B of the independent recount (HPP-153): the row n = F (p = -1) goes to the OUTGOING block
# (arm switch at position 89 of the outgoing block, p.28), incomplete last block reported separately;
# ABBA pairs (2i, 2i+1) of complete blocks: per-pair H/cmp arm2 - arm4, mean +- 2SE. s12: sum of all hold rows.
import sys, re, math

def rows_of(path):
    arm_re = re.compile(rb'GateArm: arm=(\d+) arms=\d+ block=(\d+) frame=(\d+) .*text=(\S+)')
    gates = []
    rows = []
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'GateArm:'):
                m = arm_re.search(line)
                gates.append((int(m.group(2)), int(m.group(3)), m.group(4).decode()))
            elif line.startswith(b'FrameTrace-x'):
                d = {}
                for kv in line.split():
                    if b'=' in kv:
                        k, v = kv.split(b'=', 1)
                        if k == b'n' or k.startswith(b'ac_'):
                            try: d[k.decode()] = int(v)
                            except ValueError: pass
                rows.append(d)
    return gates, rows

def assign(gates, rows):
    # block of row: last gate with F < n  (n = F -> previous block)
    out = []
    gi = -1
    for r in rows:
        while gi + 1 < len(gates) and gates[gi + 1][1] < r['n']:
            gi += 1
        if gi < 0: continue
        b, F, arm = gates[gi]
        p = r['n'] - F - 1
        out.append((b, arm, p, r))
    return out

def main(tag):
    gates, rows = rows_of('C:/kyty/s130/log_%s.txt' % tag)
    if not gates:
        s = {}
        for r in rows:
            for k, v in r.items():
                if k != 'n': s[k] = s.get(k, 0) + v
        i123 = sum(1 for r in rows if r['ac_cbad_m'] + r['ac_cbad_e'] != r['ac_cbad'] or
                   r['ac_cbe_ro'] + r['ac_cbe_na'] + r['ac_cbe_oth'] != r['ac_cbad_e'] or
                   sum(r[k] for k in ('ac_cbm_nosnap', 'ac_cbm_bad', 'ac_cbm_left', 'ac_cbm_stale', 'ac_cbm_remark', 'ac_cbm_new', 'ac_cbm_pend', 'ac_cbm_host')) != r['ac_cbad_m'])
        print(tag, 'rows', len(rows), 'cbad', s['ac_cbad'], 'cbad_m', s['ac_cbad_m'], 'cbm_bad', s['ac_cbm_bad'], 'cbm_left', s['ac_cbm_left'],
              'nosnap', s['ac_cbm_nosnap'], 'cmp', s['ac_cmp_pages'], 'I1-3 bad rows', i123, 'jstale', s['ac_jstale'])
        return
    a = assign(gates, rows)
    maxp = {}
    for b, arm, p, r in a: maxp[b] = max(maxp.get(b, -9), p)
    complete = {b for b, m in maxp.items() if m >= 89}
    print(tag, 'blocks', len(maxp), 'complete', len(complete), 'incomplete', sorted(set(maxp) - complete), 'maxp', {b: maxp[b] for b in sorted(set(maxp) - complete)})
    for label, pred in (('all', lambda b, p: True), ('all_complete', lambda b, p: b in complete),
                        ('win', lambda b, p: 10 <= p <= 88), ('win_complete', lambda b, p: b in complete and 10 <= p <= 88)):
        for arm in ('armcopy=2', 'armcopy=4'):
            n = cmp = cbad = m = host = hd = 0
            for b, ar, p, r in a:
                if ar == arm and pred(b, p):
                    n += 1; cmp += r['ac_cmp_pages']; cbad += r['ac_cbad']; m += r['ac_cbad_m']; host += r['ac_cbm_host']; hd += r['ac_cbm_host_d']
            print('  %-13s %s rows=%d cmp=%d cbad=%d M=%d H=%d host_d=%d share=%.5f%%' % (label, arm, n, cmp, cbad, m, host - hd, hd, 100.0 * cbad / cmp if cmp else 0))
    # pairs
    blk = {}
    for b, arm, p, r in a:
        if b in complete and 10 <= p <= 88:
            e = blk.setdefault(b, [arm, 0, 0]); e[1] += r['ac_cbm_host'] - r['ac_cbm_host_d']; e[2] += r['ac_cmp_pages']
    diffs = []
    bs = sorted(blk)
    for i in range(0, len(bs) - 1, 2):
        x, y = blk[bs[i]], blk[bs[i + 1]]
        if x[0] == y[0]: continue
        h2 = x if x[0] == 'armcopy=2' else y; h4 = y if h2 is x else x
        diffs.append(100.0 * (h2[1] / h2[2] - h4[1] / h4[2]))
    k = len(diffs)
    mu = sum(diffs) / k
    se = math.sqrt(sum((d - mu) ** 2 for d in diffs) / (k - 1) / k)
    print('  pairs(win,complete) k=%d mean=%+.5f%% 2SE=%.5f%%' % (k, mu, 2 * se))

for t in sys.argv[1:]:
    main(t)
