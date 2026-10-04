# F16a (HPP-518): aggregation of sweep_f16a.jsonl against the game package.
# Logs with the same sha256 are counted once (the first path in sorted order is kept).
# Output (directory of the script):
#   enoent_stat.tsv    one row per ENOENT KernelStat path: logs, events, first log:line, events with 'file not found' on
#                      the next line, package classes
#   enoent_fam.tsv     the same by family (digit runs below the mount point replaced by '#'): paths, logs, events,
#                      max events of one path in one log, next-call kinds, package classes, a sample
#   enoent_open.tsv    KernelOpen requests without a matching 'Open' line: path|flags, logs, requests, matched, package
#   msgs.tsv           the F7 / F5 messages: logs with the message, lines, distinct texts
#   agg_summary.txt    totals and identities
# Package classes of a guest path /<mount>/<rel> (PKG = games/PPSA21564-app, lower-case comparison):
#   exact      <rel> is a file or a directory of the package (must be 0 for an ENOENT path)
#   base_dirs  the same file name exists in other directories of the package (count)
#   stem_ext   the same directory and the same stem with another extension (list)
#   stem_any   the same stem with another extension anywhere in the package (count)
#   parent     the parent directory of <rel> exists in the package
#   other_mnt  <rel> exists under _DownloadData / _TempData / _SaveData of the emulator folder
import collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
EMU = 'C:/kyty/KytyPS5/ps5 em'
PKG = EMU + '/games/PPSA21564-app'
DIG = re.compile(r'\d+')

files = set()
dirs = set([''])
by_base = collections.defaultdict(list)
by_stem = collections.defaultdict(list)
for dp, dn, fn in os.walk(PKG):
    d = dp.replace(os.sep, '/')[len(PKG):].strip('/').lower()
    for x in dn:
        dirs.add((d + '/' + x.lower()).strip('/'))
        by_base[x.lower()].append(d)
    for x in fn:
        xl = x.lower()
        files.add((d + '/' + xl).strip('/'))
        by_base[xl].append(d)
        by_stem[xl.rsplit('.', 1)[0] if '.' in xl else xl].append((d, xl))
other = set()
other_roots = []
for sub in ('_DownloadData', '_TempData', '_SaveData'):
    r = EMU + '/' + sub
    if os.path.isdir(r):
        other_roots.append(sub)
        for dp, dn, fn in os.walk(r):
            d = dp.replace(os.sep, '/')[len(r):].strip('/').lower()
            for x in list(dn) + list(fn):
                other.add((d + '/' + x.lower()).strip('/'))


def split_mount(p):
    q = p.replace(chr(92), '/')
    parts = [x for x in q.split('/') if x not in ('', '.')]
    if not parts:
        return '', ''
    return parts[0], '/'.join(parts[1:]).lower()


def classes(p):
    mount, rel = split_mount(p)
    base = rel.rsplit('/', 1)[-1]
    d = rel.rsplit('/', 1)[0] if '/' in rel else ''
    st = base.rsplit('.', 1)[0] if '.' in base else base
    exact = rel in files or rel in dirs
    base_dirs = [x for x in by_base.get(base, ()) if x != d]
    stem_ext = sorted(set(x for dd, x in by_stem.get(st, ()) if dd == d and x != base))
    stem_any = [1 for dd, x in by_stem.get(st, ()) if x != base]
    om = any(o == rel or o.endswith('/' + rel) for o in other) if rel else False
    return {'mount': mount, 'exact': int(exact), 'base_dirs': len(base_dirs), 'stem_ext': stem_ext, 'stem_any': len(stem_any),
            'parent': int(d in dirs), 'other_mnt': int(om)}


def fam_of(p):
    q = p.split('/', 2)
    if len(q) == 3 and q[0] == '':
        return '/' + q[1] + '/' + DIG.sub('#', q[2])
    return DIG.sub('#', p)


recs = []
seen = {}
dups = 0
for l in open(HERE + '/sweep_f16a.jsonl', encoding='utf-8'):
    if not l.startswith('{'):
        continue
    d = json.loads(l)
    if d['sha256'] in seen:
        dups += 1
        continue
    seen[d['sha256']] = d['path']
    recs.append(d)
recs.sort(key=lambda d: d['path'])

S = collections.OrderedDict()
S['logs_in_sweep'] = len(recs) + dups
S['duplicate_sha256'] = dups
S['distinct_logs'] = len(recs)
S['bytes'] = sum(d['bytes'] for d in recs)
S['lines'] = sum(d['lines'] for d in recs)
S['logs_with_file_not_found'] = sum(1 for d in recs if d['nf_total'])
S['file_not_found_lines'] = sum(d['nf_total'] for d in recs)
S['kernelstat_lines'] = sum(d['stat_total'] for d in recs)
S['kernelstat_app_mount'] = sum(d['app_stat'] for d in recs)
S['kernelstat_app_absent_from_package'] = sum(d['app_miss'] for d in recs)
S['absent_but_next_line_not_nf'] = sum(d['miss_noadj'] for d in recs)
S['present_but_next_line_nf'] = sum(d['adj_inpkg'] for d in recs)
S['nf_lines_not_after_kernelstat'] = sum(d['nf_unattr'] for d in recs)
S['logs_with_thread_headers_KernelStat'] = sum(1 for d in recs if d['msg'].get('hdr_stat'))

paths = {}
bad_identity = []
nonapp_total = 0
for d in recs:
    tot = 0
    for p, (n_stat, n_nf, ln, n_adj) in d['stat'].items():
        tot += n_nf
        e = paths.get(p)
        if e is None:
            paths[p] = e = {'logs': 0, 'n': 0, 'adj': 0, 'first': '%s:%d' % (d['path'], ln), 'max_log': 0, 'stat': 0}
        e['logs'] += 1
        e['n'] += n_nf
        e['adj'] += n_adj
        e['stat'] += n_stat
        e['max_log'] = max(e['max_log'], n_nf)
        if split_mount(p)[0] not in ('app0', 'hostapp'):
            nonapp_total += n_nf
    if tot != d['nf_total']:
        bad_identity.append((d['path'], d['nf_total'], tot, d['miss_noadj'], d['adj_inpkg'], d['nf_unattr']))
S['enoent_stat_distinct_paths'] = len(paths)
S['enoent_stat_events'] = sum(e['n'] for e in paths.values())
S['enoent_stat_events_other_mounts'] = nonapp_total
S['logs_identity_events_eq_nf_lines'] = len(recs) - len(bad_identity)
S['logs_identity_broken'] = len(bad_identity)

cls = {}
with open(HERE + '/enoent_stat.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('path\tlogs\tevents\tmax_events_one_log\tevents_nf_next_line\tfirst\tmount\texact\tparent_dir\tbase_other_dirs\tstem_ext_same_dir\tstem_any\tother_mount\n')
    for p in sorted(paths):
        e = paths[p]
        c = cls[p] = classes(p)
        o.write('%s\t%d\t%d\t%d\t%d\t%s\t%s\t%d\t%d\t%d\t%s\t%d\t%d\n' % (
            p, e['logs'], e['n'], e['max_log'], e['adj'], e['first'], c['mount'], c['exact'], c['parent'], c['base_dirs'],
            ','.join(c['stem_ext']) or '-', c['stem_any'], c['other_mnt']))
S['paths_exact_in_package'] = sum(c['exact'] for c in cls.values())
S['paths_parent_dir_exists'] = sum(c['parent'] for c in cls.values())
S['paths_same_name_other_dir'] = sum(1 for c in cls.values() if c['base_dirs'])
S['paths_same_stem_other_ext_same_dir'] = sum(1 for c in cls.values() if c['stem_ext'])
S['paths_same_stem_other_ext_anywhere'] = sum(1 for c in cls.values() if c['stem_any'])
S['paths_other_mount'] = sum(c['other_mnt'] for c in cls.values())
S['paths_by_mount'] = dict(collections.Counter(c['mount'] for c in cls.values()))
S['paths_no_candidate_at_all'] = sum(1 for c in cls.values() if not (c['exact'] or c['base_dirs'] or c['stem_any'] or c['other_mnt']))

fam = {}
for p, e in paths.items():
    f = fam.setdefault(fam_of(p), {'paths': 0, 'n': 0, 'logs': 0, 'max_log': 0, 'sample': p, 'first': e['first'], 'base_dirs': 0,
                                   'stem_ext': 0, 'stem_any': 0, 'other': 0, 'exact': 0, 'parent': 0})
    c = cls[p]
    f['paths'] += 1
    f['n'] += e['n']
    f['logs'] = max(f['logs'], e['logs'])
    f['max_log'] = max(f['max_log'], e['max_log'])
    f['base_dirs'] += 1 if c['base_dirs'] else 0
    f['stem_ext'] += 1 if c['stem_ext'] else 0
    f['stem_any'] += 1 if c['stem_any'] else 0
    f['other'] += c['other_mnt']
    f['exact'] += c['exact']
    f['parent'] += c['parent']
nxt = collections.defaultdict(collections.Counter)
nxt_s = {}
for d in recs:
    for f, k in d['next'].items():
        nxt[f].update(k)
    for k, v in d['next_s'].items():
        nxt_s.setdefault(k, v)
KINDS = ('stat_same', 'stat_family', 'stat_samestem', 'stat_other', 'open_same', 'open_samestem', 'open_other', 'none')
tot_kinds = collections.Counter()
with open(HERE + '/enoent_fam.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('family\tpaths\tlogs_max\tevents\tmax_events_one_path_one_log\t' + '\t'.join(KINDS) +
            '\texact\tparent_dir\tsame_name_other_dir\tsame_stem_other_ext_same_dir\tsame_stem_other_ext_any\tother_mount\tsample\tfirst\n')
    for f in sorted(fam, key=lambda x: -fam[x]['n']):
        e = fam[f]
        k = nxt.get(f, {})
        tot_kinds.update(k)
        o.write('%s\t%d\t%d\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s\n' % (
            f, e['paths'], e['logs'], e['n'], e['max_log'], '\t'.join(str(k.get(x, 0)) for x in KINDS), e['exact'], e['parent'],
            e['base_dirs'], e['stem_ext'], e['stem_any'], e['other'], e['sample'], e['first']))
S['families'] = len(fam)
S['next_call_kinds'] = dict(tot_kinds)
S['next_call_events'] = sum(tot_kinds.values())
with open(HERE + '/next_samples.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('family\tkind\tsample\n')
    for k in sorted(nxt_s):
        f, kind = k.rsplit('|', 1)
        o.write('%s\t%s\t%s\n' % (f, kind, nxt_s[k]))

opens = {}
for d in recs:
    for k, (n_req, n_ok, ln) in d['open_un'].items():
        e = opens.setdefault(k, {'logs': 0, 'req': 0, 'ok': 0, 'first': '%s:%d' % (d['path'], ln)})
        e['logs'] += 1
        e['req'] += n_req
        e['ok'] = max(e['ok'], n_ok)
S['kernelopen_requests'] = sum(d['open_total'] for d in recs)
S['kernelopen_unmatched_distinct'] = len(opens)
oc = collections.Counter()
with open(HERE + '/enoent_open.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('path\tflags\tlogs\trequests\tmatched_open_lines_of_rel_max\tfirst\tmount\texact\tparent_dir\tbase_other_dirs\tstem_ext_same_dir\tstem_any\tother_mount\tcreat\n')
    for k in sorted(opens):
        p, fl = k.rsplit('|', 1)
        e = opens[k]
        c = classes(p)
        creat = int((int(fl, 16) & 0x200) != 0) if re.fullmatch(r'[0-9a-fA-F]{8}', fl) else -1
        key = 'exact' if c['exact'] else ('absent' if c['mount'] in ('app0', 'hostapp') else 'other_mount_path')
        oc[key] += 1
        o.write('%s\t%s\t%d\t%d\t%d\t%s\t%s\t%d\t%d\t%d\t%s\t%d\t%d\t%d\n' % (
            p, fl, e['logs'], e['req'], e['ok'], e['first'], c['mount'], c['exact'], c['parent'], c['base_dirs'],
            ','.join(c['stem_ext']) or '-', c['stem_any'], c['other_mnt'], creat))
S['kernelopen_unmatched_by_package'] = dict(oc)

msg_logs = collections.Counter()
msg_lines = collections.Counter()
texts = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, '']))
for d in recs:
    for k, n in d['msg'].items():
        if n:
            msg_logs[k] += 1
            msg_lines[k] += n
    for k, t in d['txt'].items():
        if t:
            msg_logs[k] += 1
        for text, (n, ln) in t.items():
            msg_lines[k] += n
            e = texts[k][text]
            e[0] += 1
            e[1] += n
            if not e[2]:
                e[2] = '%s:%d' % (d['path'], ln)
with open(HERE + '/msgs.tsv', 'w', encoding='utf-8', newline='\n') as o:
    o.write('message\tlogs\tlines\tdistinct_texts\n')
    for k in sorted(set(msg_logs) | set(texts)):
        o.write('%s\t%d\t%d\t%d\n' % (k, msg_logs[k], msg_lines[k], len(texts.get(k, ()))))
    o.write('\nmessage\ttext\tlogs\tlines\tfirst\n')
    for k in sorted(texts):
        for text in sorted(texts[k], key=lambda x: -texts[k][x][0]):
            e = texts[k][text]
            o.write('%s\t%s\t%d\t%d\t%s\n' % (k, text, e[0], e[1], e[2]))
S['msg_logs'] = dict(msg_logs)
S['msg_lines'] = dict(msg_lines)
S['other_mount_roots_found'] = other_roots
S['package_files'] = len(files)
S['package_dirs'] = len(dirs) - 1

with open(HERE + '/agg_summary.txt', 'w', encoding='utf-8', newline='\n') as o:
    for k, v in S.items():
        o.write('%s\t%s\n' % (k, json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v))
    o.write('\nidentity broken (path, nf_lines, events, miss_noadj, adj_inpkg, nf_unattr):\n')
    for b in bad_identity:
        o.write('\t'.join(str(x) for x in b) + '\n')
    ok = not bad_identity and S['paths_exact_in_package'] == 0
    o.write('\n' + ('ALL OK' if ok else 'CHECK FAILED') + '\n')
print(open(HERE + '/agg_summary.txt', encoding='utf-8').read())
