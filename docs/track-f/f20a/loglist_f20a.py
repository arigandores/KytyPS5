# F20a (HPP-551, ROADMAP s122 item 451(e)): list of the game logs of sessions 128+ and of the tracks, with the tag json
# of every log.  Roots of the task: C:/kyty/s<NNN> with 128 <= NNN <= 199 (the 's1*' of the task), C:/kyty/f287,
# C:/kyty/p283, C:/kyty/s288, C:/kyty/play.  Debt (a)(2) of item 451: every root is walked ONCE - the roots are a set of
# normalised paths, no root lies inside another, and the rows are checked for repeated paths (the count is printed).
# Names: 'log_*.txt', 'log_*.txt.xz', '_kyty*.txt', '_kyty*.txt.xz', and 'log.txt' / 'log.txt.xz' under C:/kyty/play.
# Fixture directories are excluded ('/fx/', '/fx_', '/work_', '/mut', '/test_', '/fixt') - the form of loglist_f19a.py.
# Tag json of 'log_<tag>.txt[.xz]': the first existing of <dir>/<tag>.json, <dir>/<tag>.json.xz, <dir>/../<tag>.json;
# for C:/kyty/play/<stamp>/log.txt - any '*.json' of the directory (listed, the reader picks).
# Output: <out.tsv> lines 'path <TAB> size <TAB> mtime <TAB> root <TAB> json path or -', plain files first (small first).
# Usage: python loglist_f20a.py <out.tsv>
import os, re, sys

out = sys.argv[1]
base = 'C:/kyty'
roots = []
for d in sorted(os.listdir(base)):
    m = re.fullmatch(r's(1\d\d)', d)
    if m and int(m.group(1)) >= 128 and os.path.isdir(base + '/' + d):
        roots.append(base + '/' + d)
for d in ('f287', 'p283', 's288', 'play'):
    if os.path.isdir(base + '/' + d) and base + '/' + d not in roots:
        roots.append(base + '/' + d)
assert len(set(roots)) == len(roots)
for a in roots:
    for b in roots:
        assert a == b or not (a + '/').startswith(b + '/'), (a, b)
fx = re.compile(r'/(fx/|fx_|work_|mut|test_|fixt)')
rows = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in ('.git', 'build', 'wt', '_ShaderCache', '_Shaders', 'node_modules', '__pycache__')]
        d = dp.replace(os.sep, '/')
        names = set(fn)
        for f in fn:
            ok = (f.startswith('log_') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or \
                 (f.startswith('_kyty') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or \
                 (r.endswith('/play') and f in ('log.txt', 'log.txt.xz'))
            if not ok:
                continue
            p = d + '/' + f
            if fx.search(p):
                continue
            js = '-'
            if f.startswith('log_'):
                tag = f[4:].split('.txt')[0]
                if tag + '.json' in names:
                    js = d + '/' + tag + '.json'
                elif tag + '.json.xz' in names:
                    js = d + '/' + tag + '.json.xz'
                else:
                    up = d.rsplit('/', 1)[0] + '/' + tag + '.json'
                    if os.path.isfile(up):
                        js = up
            elif r.endswith('/play'):
                c = sorted(x for x in fn if x.endswith('.json'))
                if c:
                    js = ';'.join(d + '/' + x for x in c)
            st = os.stat(p)
            rows.append((p, st.st_size, int(st.st_mtime), r, js))
rows.sort(key=lambda x: (x[0].endswith('.xz'), x[1], x[0]))
paths = [x[0] for x in rows]
print('rows', len(rows), 'distinct paths', len(set(paths)), 'repeated paths', len(rows) - len(set(paths)))
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    for p, s, mt, r, js in rows:
        f.write('%s\t%d\t%d\t%s\t%s\n' % (p, s, mt, r, js))
plain = [x for x in rows if not x[0].endswith('.xz')]
xz = [x for x in rows if x[0].endswith('.xz')]
print('roots', len(roots), 'files', len(rows), 'plain', len(plain), 'GiB %.1f' % (sum(x[1] for x in plain) / 2.0 ** 30),
      'xz', len(xz), 'GiB %.1f' % (sum(x[1] for x in xz) / 2.0 ** 30), 'with json', sum(1 for x in rows if x[4] != '-'))
by = {}
for p, s, mt, r, js in rows:
    k = r.rsplit('/', 1)[1]
    by.setdefault(k, [0, 0, 0])
    by[k][0] += 1
    by[k][1] += s
    by[k][2] += js != '-'
print(' '.join('%s:%d/%.1fG/j%d' % (k, v[0], v[1] / 2.0 ** 30, v[2]) for k, v in sorted(by.items())))
nojs = {}
for p, s, mt, r, js in rows:
    if js == '-':
        nojs.setdefault(p.rsplit('/', 1)[0], []).append(p.rsplit('/', 1)[1])
print('directories with logs without a json:', len(nojs))
for d in sorted(nojs)[:80]:
    print('  ', d, len(nojs[d]), nojs[d][:3])
