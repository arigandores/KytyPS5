# F16a (HPP-518): aggregation of sweep2_f16a.jsonl.  Output: agg2_summary.txt, open_enoent.tsv (one row per
# KernelOpen path absent from the package: logs, requests, kinds of the next guest FS call).
import collections, json, os

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
recs = [json.loads(l) for l in open(HERE + '/sweep2_f16a.jsonl', encoding='utf-8') if l.startswith('{')]
S = collections.OrderedDict()
S['logs'] = len(recs)
S['odx_stem_log_pairs_enoent_file_in_package'] = sum(d['odx_enoent_inpkg'] for d in recs)
S['odx_stem_log_pairs_reached'] = sum(d['odx_reached'] for d in recs)
S['odx_stem_log_pairs_unreached'] = sum(d['odx_unreached'] for d in recs)
S['odx_stem_log_pairs_enoent_no_file_in_package'] = sum(d['odx_enoent_nopkg'] for d in recs)
un = collections.Counter()
un_first = {}
for d in recs:
    for s in d['odx_unreached_s']:
        un[s] += 1
        un_first.setdefault(s, d['path'])
S['odx_unreached_distinct_stems'] = len(un)
opens = {}
for d in recs:
    for p, (n, kinds) in d['open_enoent'].items():
        e = opens.setdefault(p, [0, 0, collections.Counter(), 0])
        e[0] += 1
        e[1] += n
        e[2].update(kinds)
        e[3] = max(e[3], n)
kt = collections.Counter()
for e in opens.values():
    kt.update(e[2])
S['open_enoent_distinct_paths'] = len(opens)
S['open_enoent_requests'] = sum(e[1] for e in opens.values())
S['open_enoent_next_kinds'] = dict(kt)
S['open_enoent_max_requests_one_path_one_log'] = max([e[3] for e in opens.values()] or [0])
KINDS = ('stat_same', 'stat_samestem', 'stat_other', 'open_same', 'open_samestem', 'open_other', 'none')
with open(HERE + '/open_enoent.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('path\tlogs\trequests\tmax_requests_one_log\t' + '\t'.join(KINDS) + '\n')
    for p in sorted(opens):
        e = opens[p]
        o.write('%s\t%d\t%d\t%d\t%s\n' % (p, e[0], e[1], e[3], '\t'.join(str(e[2].get(k, 0)) for k in KINDS)))
empty = {}
for d in recs:
    for p, (n, s) in d['empty'].items():
        e = empty.setdefault(p, [0, 0, 0, []])
        e[0] += 1
        e[1] += n
        e[2] = max(e[2], n)
        if len(e[3]) < 6:
            e[3] += ['%s %s' % (d['path'], x) for x in s[:2]]
with open(HERE + '/agg2_summary.txt', 'w', encoding='utf-8', newline='\n') as o:
    for k, v in S.items():
        o.write('%s\t%s\n' % (k, json.dumps(v, sort_keys=True) if isinstance(v, dict) else v))
    o.write('\nunreached stems (stem, logs, first log):\n')
    for s, n in un.most_common(60):
        o.write('%s\t%d\t%s\n' % (s, n, un_first[s]))
    o.write('\nempty resource names (path, logs, events, max events one log) and samples:\n')
    for p, e in sorted(empty.items()):
        o.write('%s\t%d\t%d\t%d\n' % (p, e[0], e[1], e[2]))
        for x in e[3][:6]:
            o.write('    %s\n' % x)
    ok = S['odx_stem_log_pairs_reached'] + S['odx_stem_log_pairs_unreached'] == S['odx_stem_log_pairs_enoent_file_in_package']
    o.write('\n' + ('ALL OK' if ok else 'CHECK FAILED') + '\n')
print(open(HERE + '/agg2_summary.txt', encoding='utf-8').read()[:6000])
