# F19a (HPP-543; copy of f18a/loglist_f19a.py): list of the game logs of sessions 106+ and of the tracks for sweep_f19a.py.
# Roots of the task: C:/kyty/s<NNN> with NNN >= 106, C:/kyty/f287, C:/kyty/p283, C:/kyty/s288; extra root (not in the
# task, added by the link): C:/kyty/play - the recorded play sessions of the user (the only runs not cut at ~340 s).
# Names: 'log_*.txt', 'log_*.txt.xz', '_kyty*.txt', '_kyty*.txt.xz', and 'log.txt' under C:/kyty/play.
# Fixture directories are excluded ('/fx/', '/fx_', '/work_', '/mut', '/test_', '/fixt') - the form of sweep_f17a.py.
# Output: <out.tsv> lines 'path <TAB> size <TAB> root', plain files first (largest last), then '.xz'.
# Usage: python loglist_f19a.py <out.tsv>
import os, re, sys

out = sys.argv[1]
base = 'C:/kyty'
roots = []
for d in sorted(os.listdir(base)):
    m = re.fullmatch(r's(\d+)', d)
    if m and int(m.group(1)) >= 106 and os.path.isdir(base + '/' + d):
        roots.append(base + '/' + d)
roots += [base + '/f287', base + '/p283', base + '/s288', base + '/play']
fx = re.compile(r'/(fx/|fx_|work_|mut|test_|fixt)')
rows = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in ('.git', 'build', 'wt', '_ShaderCache', '_Shaders', 'node_modules', '__pycache__')]
        d = dp.replace(os.sep, '/')
        for f in fn:
            ok = (f.startswith('log_') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or \
                 (f.startswith('_kyty') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or \
                 (r.endswith('/play') and f == 'log.txt')
            if not ok:
                continue
            p = d + '/' + f
            if fx.search(p):
                continue
            rows.append((p, os.path.getsize(p), r))
rows.sort(key=lambda x: (x[0].endswith('.xz'), x[1], x[0]))
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    for p, s, r in rows:
        f.write('%s\t%d\t%s\n' % (p, s, r))
plain = [x for x in rows if not x[0].endswith('.xz')]
xz = [x for x in rows if x[0].endswith('.xz')]
print('roots', len(roots), 'files', len(rows), 'plain', len(plain), 'GiB %.1f' % (sum(x[1] for x in plain) / 2.0 ** 30),
      'xz', len(xz), 'GiB %.1f' % (sum(x[1] for x in xz) / 2.0 ** 30))
by = {}
for p, s, r in rows:
    k = r.rsplit('/', 1)[1]
    by.setdefault(k, [0, 0])
    by[k][0] += 1
    by[k][1] += s
print(' '.join('%s:%d/%.1fG' % (k, v[0], v[1] / 2.0 ** 30) for k, v in sorted(by.items())))
