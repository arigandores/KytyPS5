# F16a (HPP-518): groups of the ENOENT KernelStat paths.  Reads enoent_stat.tsv and enoent_fam.tsv (agg_f16a.py).
# Group = (directory, extension) with the component after 'levels' replaced by '*', the components after
# 'cinematics' and 'layers' replaced by '*' and digit runs by '#'.
# Class of a path against the package (first match):
#   HIT_OTHER_DIR   the same file name exists in another directory of the package (a search over directories)
#   HIT_OTHER_EXT   the same stem with another extension exists in the same directory
#   STEM_ELSEWHERE  the same stem with another extension exists elsewhere in the package
#   NOWHERE         no file of the package has this stem
# Output: enoent_grp.tsv (one row per group), grp_summary.txt (totals by class; 'ALL OK' when the sums agree).
import collections, csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
DIG = re.compile(r'\d+')
KINDS = ('stat_same', 'stat_family', 'stat_samestem', 'stat_other', 'open_same', 'open_samestem', 'open_other', 'none')


def grp(p):
    d, b = p.rsplit('/', 1)
    ext = '.' + b.rsplit('.', 1)[1] if '.' in b else '<dir or no ext>'
    parts = d.split('/')
    out = []
    star = False
    for x in parts:
        if star:
            out.append('*')
            star = False
            continue
        out.append(x if x == 'app0' else DIG.sub('#', x))
        if x in ('levels', 'cinematics', 'layers'):
            star = True
    return '/'.join(out), DIG.sub('#', ext)


def klass(r):
    if int(r['base_other_dirs']):
        return 'HIT_OTHER_DIR'
    if r['stem_ext_same_dir'] != '-':
        return 'HIT_OTHER_EXT'
    if int(r['stem_any']):
        return 'STEM_ELSEWHERE'
    return 'NOWHERE'


G = {}
tot = collections.Counter()
tot_p = collections.Counter()
n_paths = n_events = 0
for r in csv.DictReader(open(HERE + '/enoent_stat.tsv', encoding='utf-8'), delimiter='\t'):
    k = grp(r['path'])
    g = G.setdefault(k, {'paths': 0, 'events': 0, 'logs': 0, 'max1': 0, 'cls': collections.Counter(), 'cls_e': collections.Counter(),
                         'sample': r['path'], 'first': r['first'], 'kinds': collections.Counter(), 'noparent': 0})
    c = klass(r)
    e = int(r['events'])
    g['paths'] += 1
    g['events'] += e
    g['logs'] = max(g['logs'], int(r['logs']))
    g['max1'] = max(g['max1'], int(r['max_events_one_log']))
    g['cls'][c] += 1
    g['cls_e'][c] += e
    g['noparent'] += 1 - int(r['parent_dir'])
    tot[c] += e
    tot_p[c] += 1
    n_paths += 1
    n_events += e
n_next = 0
for r in csv.DictReader(open(HERE + '/enoent_fam.tsv', encoding='utf-8'), delimiter='\t'):
    k = grp(r['sample'])
    for x in KINDS:
        G[k]['kinds'][x] += int(r[x])
        n_next += int(r[x])
CL = ('HIT_OTHER_DIR', 'HIT_OTHER_EXT', 'STEM_ELSEWHERE', 'NOWHERE')
with open(HERE + '/enoent_grp.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('dir\text\tpaths\tevents\tlogs_max\tmax_events_one_path_one_log\tparent_dir_absent\t' + '\t'.join('paths_' + x for x in CL) + '\t' +
            '\t'.join(KINDS) + '\tsample\tfirst\n')
    for k in sorted(G, key=lambda x: -G[x]['events']):
        g = G[k]
        o.write('%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\t%s\n' % (
            k[0], k[1], g['paths'], g['events'], g['logs'], g['max1'], g['noparent'], '\t'.join(str(g['cls'][x]) for x in CL),
            '\t'.join(str(g['kinds'][x]) for x in KINDS), g['sample'], g['first']))
with open(HERE + '/grp_summary.txt', 'w', encoding='utf-8', newline='\n') as o:
    o.write('groups\t%d\npaths\t%d\nevents\t%d\nnext_call_events\t%d\n' % (len(G), n_paths, n_events, n_next))
    for x in CL:
        o.write('class %s\tpaths %d\tevents %d\n' % (x, tot_p[x], tot[x]))
    by_ext = collections.Counter()
    by_ext_p = collections.Counter()
    for k, g in G.items():
        by_ext[k[1]] += g['events']
        by_ext_p[k[1]] += g['paths']
    for x, n in by_ext.most_common():
        o.write('ext %s\tpaths %d\tevents %d\n' % (x, by_ext_p[x], n))
    ok = sum(tot.values()) == n_events == n_next and sum(tot_p.values()) == n_paths
    o.write('ALL OK\n' if ok else 'CHECK FAILED\n')
print(open(HERE + '/grp_summary.txt', encoding='utf-8').read())
