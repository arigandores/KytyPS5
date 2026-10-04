# F17a (HPP-525): aggregation of sweep.jsonl (sweep_f17a.py) and sweep2.jsonl (sweep2_f17a.py).
# Writes agg_summary.txt, logs_w.tsv, f6_keys.tsv, runs.tsv next to the inputs.  The names of foreign applications in the
# layer texts are replaced by <app> (general rule 28).
# Usage: python agg_f17a.py <dir with sweep.jsonl and sweep2.jsonl>
import collections, json, re, sys

d = sys.argv[1].rstrip('/')
R = [json.loads(l) for l in open(d + '/sweep.jsonl', encoding='utf-8') if l.startswith('{')]
R2 = {}
for l in open(d + '/sweep2.jsonl', encoding='utf-8'):
    if l.startswith('{'):
        r = json.loads(l)
        R2[r['path']] = r
APP = re.compile(r'VK_LAYER_\w+_HOOK|C:\\ProgramData\\[^)\s]+')


def mask(t):
    return APP.sub('<app>', t)


out = []


def p(*a):
    out.append(' '.join(str(x) for x in a))


W = [r for r in R if r['val']]
sha_w = {}
for r in sorted(W, key=lambda x: x['path']):
    sha_w.setdefault(r['sha256'], r)
U = list(sha_w.values())  # distinct validation logs (first path per sha256)
p('logs', len(R), 'GiB %.1f' % (sum(r['size'] for r in R) / 2.0 ** 30), 'distinct by sha256', len({r['sha256'] for r in R}))
p('validation logs', len(W), 'distinct', len(U), 'by root', dict(collections.Counter(r['path'].split('/')[2] for r in W)))
p('distinct validation logs: with F6 lines', sum(1 for r in U if r['f6_sum']), 'without', sum(1 for r in U if not r['f6_sum']),
  '(of them with [Vulkan][E]:', sum(1 for r in U if not r['f6_sum'] and r['ve']), ')')
p('logs without validation that have [Vulkan][W] lines', sum(1 for r in R if not r['val'] and r['vw']))
p('identity f6_sum + last_report == f6_broad fails in', sum(1 for r in R if r['f6_sum'] + r['cnt']['last_report'] != r['f6_broad']), 'logs')
p('identity vw == f6_sum + sum(wo) fails in', sum(1 for r in R if r['vw'] != r['f6_sum'] + sum(r['wo'].values()) + r['wo_over']), 'logs')
p('F6 lines, distinct validation logs', sum(r['f6_sum'] for r in U), '; all validation logs', sum(r['f6_sum'] for r in W))
p('[Vulkan][W] lines, distinct validation logs', sum(r['vw'] for r in U), '; [Vulkan][E]', sum(r['ve'] for r in U))
p('logs with the duplicate limit reached (last_report > 0), distinct', sum(1 for r in U if r['cnt']['last_report']))
p()
p('== lines of the binding paths, all', len(R), 'logs ==')
tot = collections.Counter()
logs_with = collections.Counter()
for r in R:
    for k, n in r['cnt'].items():
        tot[k] += n
        logs_with[k] += 1 if n else 0
for k in sorted(tot):
    p('cnt', k, tot[k], 'in', logs_with[k], 'logs')
for k in ('nco', 'mrt', 'rct_slots'):
    c = collections.Counter()
    for r in R:
        for a, n in r[k].items():
            c[a] += n
    p(k, dict(sorted(c.items())))
tx = collections.defaultdict(collections.Counter)
txw = collections.defaultdict(collections.Counter)
for r in R:
    for k, v in r['txt'].items():
        for t in v:
            tx[k][t] += 1
            if r['val']:
                txw[k][t] += 1
for k in sorted(r['txt'] for r in R[:1])[0] if False else sorted(R[0]['txt']):
    p('txt', k, 'distinct texts', len(tx[k]))
    for t, n in tx[k].most_common(8):
        p('    logs', n, '(validation', txw[k][t], ')', mask(t)[:200])
p()
p('== other [Vulkan][W] texts (digits -> #) ==')
wo = collections.Counter()
wol = collections.Counter()
for r in R:
    for t, n in r['wo'].items():
        wo[mask(t)] += n
        wol[mask(t)] += 1
for t, n in wo.most_common():
    p('lines', n, 'logs', wol[t], '|', t[:230])
p('wo_over', sum(r['wo_over'] for r in R))
p()
p('== F6 keys (types|command|Location|name|attachment index|null), distinct validation logs ==')
f6 = collections.Counter()
f6l = collections.Counter()
for r in U:
    for k, n in r['f6'].items():
        f6[k] += n
        f6l[k] += 1
with open(d + '/f6_keys.tsv', 'wb') as fo:
    fo.write(b'types\tcommand\tlocation\tname\tattachment_index\tnull_handle\tlines\tlogs\n')
    for k, n in sorted(f6.items(), key=lambda x: -x[1]):
        fo.write(('\t'.join(k.split('|')) + '\t%d\t%d\n' % (n, f6l[k])).encode())
        p(k, n, 'logs', f6l[k])
p('distinct (command, Location)', len({tuple(k.split('|')[1:3]) for k in f6}), '; distinct Location', sorted({int(k.split('|')[2]) for k in f6}),
  '; name == out_mrt_<Location> and index == Location in every key:', all(k.split('|')[3] == 'out_mrt_' + k.split('|')[2] and k.split('|')[4] == k.split('|')[2] for k in f6),
  '; types', sorted({k.split('|')[0] for k in f6}))
p()
p('== draw runs (sweep2), distinct validation logs with F6 ==')
miss = [r['path'] for r in U if r['f6_sum'] and r['path'] not in R2]
p('logs with F6 not in sweep2', len(miss), miss[:4])
p('identity sweep2 f6 == sweep f6_sum fails in', sum(1 for r in U if r['path'] in R2 and R2[r['path']]['f6'] != r['f6_sum']), 'logs')
run = collections.Counter()
runl = collections.Counter()
runlv = collections.defaultdict(set)
first = {}
over = 0
for r in U:
    q = R2.get(r['path'])
    if not q:
        continue
    over += q['run_over']
    for k, n in q['run'].items():
        run[k] += n
        runl[k] += 1
        runlv[k].update(r['lvl'][:1])
        if k not in first:
            first[k] = '%s:%d' % (r['path'], q['first'][k])
p('runs', sum(run.values()), 'distinct keys', len(run), 'run_over', over)


def derive(k):
    locs = k.split(':', 1)[1].split(',')
    nn = sorted(int(x[:-1]) for x in locs if x.endswith('n'))
    nb = sorted(int(x) for x in locs if not x.endswith('n'))
    lo = (max(nn) + 1) if nn else 0
    hi = min(nb) if nb else 8
    return nn, nb, lo, hi


with open(d + '/runs.tsv', 'wb') as fo:
    fo.write(b'run\truns\tlogs\tscenes\tcount_min\tcount_max\tholes_below_count\tlocations_at_or_above_count\tfirst\n')
    for k, n in sorted(run.items(), key=lambda x: -x[1]):
        nn, nb, lo, hi = derive(k)
        fo.write(('%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n' % (k, n, runl[k], len(runlv[k]), lo, hi, ','.join(map(str, nn)) or '-',
                                                          ','.join(map(str, nb)) or '-', first[k])).encode())
for k, n in sorted(run.items(), key=lambda x: -x[1])[:40]:
    nn, nb, lo, hi = derive(k)
    p('%-52s runs %9d logs %3d scenes %3d  colorAttachmentCount in [%d, %d]  holes %s' % (k, n, runl[k], len(runlv[k]), lo, hi, nn or '-'))
bad = [k for k in run if derive(k)[2] > derive(k)[3]]
p('runs with an impossible count range (two draws merged by the ascending rule)', len(bad), 'keys,', sum(run[k] for k in bad), 'runs')
c0 = sum(n for k, n in run.items() if derive(k)[3] == 0)
p('runs whose count range allows only 0 colour attachments (Location 0 reported as at-or-above count)', c0)
p()
p('== per distinct validation log: logs_w.tsv ==')
with open(d + '/logs_w.tsv', 'wb') as fo:
    fo.write(b'path\tsha256_16\tsize\tscene\tver\tvulkan_w\tvulkan_e\tf6\tlast_report\tdualsrc\trtskip_mode_line\truns\trun_keys\tcopies\n')
    copies = collections.Counter(r['sha256'] for r in W)
    for r in sorted(U, key=lambda x: x['path']):
        q = R2.get(r['path'], {'runs': 0, 'run': {}})
        fo.write(('%s\t%s\t%d\t%s\t%s\t%d\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\n' % (
            r['path'], r['sha256'][:16], r['size'], (r['lvl'] or ['-'])[0], r['ver'] or '-', r['vw'], r['ve'], r['f6_sum'], r['cnt']['last_report'],
            ';'.join(r['txt']['dualsrc'])[:60] or '-', 1 if r['txt']['rts_mode'] else 0, q['runs'], len(q['run']), copies[r['sha256']])).encode())
scenes = collections.Counter((r['lvl'] or ['-'])[0] for r in U if r['f6_sum'])
p('scenes among distinct validation logs with F6:', len(scenes), dict(scenes.most_common()))
p('validation logs with F6 and the RtSkip mode line:', sum(1 for r in U if r['f6_sum'] and r['txt']['rts_mode']), 'of', sum(1 for r in U if r['f6_sum']))
p('validation logs with F6 by DualSrcBlend text:', dict(collections.Counter(';'.join(r['txt']['dualsrc'])[:50] or '-' for r in U if r['f6_sum'])))
open(d + '/agg_summary.txt', 'wb').write(('\n'.join(out) + '\n').encode('utf-8'))
print('\n'.join(out))
