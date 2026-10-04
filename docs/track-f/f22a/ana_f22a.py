# F22a (HPP-576): summary of sweep_sample.jsonl / sweep_ctx.jsonl (sweep_f22a.py) with the identities against F21a.
# Usage: python ana_f22a.py <f22a dir> <f21a dir>   -> prints the report text (ana_f22a.txt)
import collections, json, os, statistics, sys

d, f21 = sys.argv[1], sys.argv[2]
C = collections.Counter
f21r = {}
for l in open(os.path.join(f21, 'sweep_all.jsonl'), encoding='utf-8'):
    if l.strip():
        r = json.loads(l)
        f21r[r['path']] = r
groups = {}
for name in ('sample', 'ctx'):
    groups[name] = [json.loads(l) for l in open(os.path.join(d, 'sweep_%s.jsonl' % name), encoding='utf-8') if l.strip()]
out = []


def P(*a):
    out.append(' '.join(str(x) for x in a))


def short(p):
    return p.replace('C:/kyty/', '')


bad = []
for name, recs in groups.items():
    for r in recs:
        p = r['path']
        if r.get('missing'):
            bad.append(('missing', p))
            continue
        if r['lines'] != f21r[p]['lines']:
            bad.append(('lines != F21a', p, r['lines'], f21r[p]['lines']))
        if r['size_now'] != r['size_list']:
            bad.append(('size changed', p))
        if r.get('xz_rc', 0) != 0:
            bad.append(('xz_rc', p))
        if r['drf_n'] != len(r['drf']) + r['drf_bad']:
            bad.append(('drf identity', p))
        if r['drf_n'] > 32:
            bad.append(('drf > 32', p))
        if r['levels_over']:
            bad.append(('levels_over', p))
        for x in r['drf']:
            if x['next_read'] is not None and x['next_read'][0] not in ('file', 'pos'):
                bad.append(('next_read form', p))
        for s in r['stdout']:
            if s.get('xz_rc', 0) != 0:
                bad.append(('stdout xz_rc', s['path']))
P('== 0. Identities (lines = F21a per path, size unchanged, xz_rc 0, drf_n = len(drf) + drf_bad, drf_n <= 32, levels_over 0)')
P('records', sum(len(v) for v in groups.values()), 'failures', len(bad), bad[:10], '-', 'IDENTITIES ALL OK' if not bad else 'IDENTITIES FAILED')
P('invariant drf_bad over all records', sum(r['drf_bad'] for v in groups.values() for r in v),
  '; addrlen_other', sum(r['addrlen_other'] for v in groups.values() for r in v),
  '; rd_other', sum(r['rd_other'] for v in groups.values() for r in v))

for name, recs in groups.items():
    P()
    P('== %s: %d logs' % (name, len(recs)))
    byb = C(r['bin'] for r in recs)
    P('logs by binary:', dict(byb))
    P('lines', sum(r['lines'] for r in recs))
    P('-- 1. KernelRead: direct read failed')
    w = [r for r in recs if r['drf_n']]
    P('logs with >= 1 line', len(w), 'of', len(recs), '; lines', sum(r['drf_n'] for r in recs), '; logs at the cap 32', sum(r['drf_n'] == 32 for r in recs))
    P('by binary (logs with / lines):', {b: (sum(1 for r in w if r['bin'] == b), sum(r['drf_n'] for r in w if r['bin'] == b)) for b in sorted(set(r['bin'] for r in w))})
    sizes = [x['size'] for r in w for x in r['drf']]
    if sizes:
        P('request sizes: n', len(sizes), 'min', min(sizes), 'median', statistics.median(sizes), 'max', max(sizes),
          '; >= 64 KiB', sum(s >= 65536 for s in sizes), '; page multiple', sum(s % 4096 == 0 for s in sizes))
    nr = [x['next_read'] for r in w for x in r['drf']]
    P('next Read line after it: none', sum(1 for x in nr if x is None), '; form', dict(C(x[0] for x in nr if x)),
      '; n == 0', sum(1 for x in nr if x and x[1] == 0), '; n == request size', sum(1 for r in w for x in r['drf'] if x['next_read'] and x['next_read'][1] == x['size']),
      '; 0 < n < request', sum(1 for r in w for x in r['drf'] if x['next_read'] and 0 < x['next_read'][1] < x['size']),
      '; distance in lines max', max([x[2] - y['line'] for r in w for y in r['drf'] for x in [y['next_read']] if x] or [0]))
    lv = C()
    for r in w:
        for x in r['drf']:
            lv[x['level'] or '<before level>'] += 1
    P('levels of the lines:', dict(lv.most_common()))
    P('levels (distinct, excl. before level):', len([k for k in lv if k != '<before level>']))
    for r in sorted(w, key=lambda r: r['path']):
        P('   %-55s %s drf %2d levels %s sizes %s next %s' % (short(r['path'])[:55], r['bin'], r['drf_n'],
          sorted(set(x['level'] for x in r['drf'])), [hex(x['size']) for x in r['drf']][:6],
          [x['next_read'][:2] if x['next_read'] else None for x in r['drf']][:6]))
    P('-- 2. Read lines (the file paths are exercised): KernelRead', sum(r['rd_file'] for r in recs), '(n=0:', sum(r['rd_file0'] for r in recs), ') ; KernelPread',
      sum(r['rd_pos'] for r in recs), '(n=0:', sum(r['rd_pos0'] for r in recs), ') ; directory', sum(r['rd_dir'] for r in recs), '; random', sum(r['rd_rand'] for r in recs))
    P('logs with KernelRead lines', sum(r['rd_file'] > 0 for r in recs), '; with KernelPread lines', sum(r['rd_pos'] > 0 for r in recs))
    P('-- 3. sockets: Recvfrom blocks', sum(r['recv_n'] for r in recs), 'in', sum(r['recv_n'] > 0 for r in recs), 'logs ; Sendto blocks', sum(r['send_n'] for r in recs), 'in', sum(r['send_n'] > 0 for r in recs), 'logs')
    rl = C()
    for r in recs:
        rl.update(r['recv_levels'])
    if rl:
        P('   Recvfrom by level', dict(rl))
    P('-- 4. APR/AMPR/AMM lines', dict(sum((C(r['apr']) for r in recs), C())))
    P('-- 5. PRINT_NAME: logs with lines', sum(r['pn_n'] > 0 for r in recs), '; lines', sum(r['pn_n'] for r in recs))
    pr = sum((C(r['pn_read']) for r in recs), C())
    P('   read-ish functions', dict(pr.most_common()))
    for r in recs:
        if r['pn_n']:
            P('   %-55s %s pn %d funcs %d read-ish %s' % (short(r['path'])[:55], r['bin'], r['pn_n'], r['pn_funcs'], r['pn_read']))
    P('-- 6. stdout SysFileRead: ReadFile failed: logs with a stdout file', sum(1 for r in recs if r['stdout']),
      '; stdout files', sum(len(r['stdout']) for r in recs), '; logs with >= 1 line', sum(1 for r in recs if any(s['sfr_n'] for s in r['stdout'])))
    err = sum((C(s['sfr_err']) for r in recs for s in r['stdout']), C())
    P('   lines by error', dict(err), '; inside the log (sfr_log)', sum(r['sfr_log'] for r in recs))
    both = [(r['drf_n'], max([s['sfr_n'] for s in r['stdout']] or [0])) for r in recs if r['stdout']]
    P('   pairs (drf_n, max stdout sfr_n) where either > 0:', sorted(C(x for x in both if x != (0, 0)).items()))
    P('   logs with drf > 0 and stdout sfr = 0:', sum(1 for a, b in both if a > 0 and b == 0), '; drf = 0 and sfr > 0:', sum(1 for a, b in both if a == 0 and b > 0))
    P('-- 7. StreamRead lines', sum(r['stream_n'] for r in recs), 'TORN', sum(r['torn_n'] for r in recs), '; fatal lines', sum(r['fatal'] for r in recs), 'in', sum(r['fatal'] > 0 for r in recs), 'logs')
    lvls = set(x['level'] for r in recs for x in r['levels'])
    P('-- 8. distinct levels in these logs', len(lvls))
print('\n'.join(out))
