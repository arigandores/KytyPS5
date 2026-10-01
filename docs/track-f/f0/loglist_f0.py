# F0 (HPP-289): list of logs for the sweep - C:/kyty/**/log_*.txt and _kyty*.txt (p.228(b)(3)); names and sizes only, no content read
import os, re, sys, collections
root = 'C:/kyty'
rows = []
for dp, dn, fn in os.walk(root):
    d = dp.replace(os.sep, '/')
    # skip git internals and build trees (no logs of game runs there)
    dn[:] = [x for x in dn if x not in ('.git', 'build', '_ShaderCache', '_Shaders', 'node_modules')]
    for f in fn:
        if (f.startswith('log_') and f.endswith('.txt')) or (f.startswith('_kyty') and f.endswith('.txt')):
            p = d + '/' + f
            try:
                rows.append((p, os.path.getsize(p), os.path.getmtime(p)))
            except OSError:
                pass
rows.sort()
with open('C:/kyty/f287/f0/loglist_f0.tsv', 'w', encoding='utf-8', newline='\n') as o:
    for p, s, m in rows:
        o.write('%s\t%d\t%d\n' % (p, s, int(m)))
tot = sum(r[1] for r in rows)
print('files', len(rows), 'bytes', tot, 'GB %.1f' % (tot / 1e9))
by = collections.Counter(); bys = collections.Counter()
for p, s, m in rows:
    rel = p[len(root) + 1:]
    top = rel.split('/')[0] if '/' in rel else '(root)'
    by[top] += 1; bys[top] += s
for k in sorted(by, key=lambda k: -bys[k])[:60]:
    print('%-28s %5d %8.2f GB' % (k, by[k], bys[k] / 1e9))
# depth classes
fx = re.compile(r'/(fx_|work_|mut|test_|fixt)')
nfx = sum(1 for p, s, m in rows if fx.search(p))
print('in fixture/mutant dirs', nfx, 'real candidates', len(rows) - nfx, 'GB real %.1f' % (sum(s for p, s, m in rows if not fx.search(p)) / 1e9))
print('direct children of s*/ :', sum(1 for p, s, m in rows if re.match(r'C:/kyty/s\d+[^/]*/[^/]+$', p)), ' root:', sum(1 for p, s, m in rows if re.match(r'C:/kyty/[^/]+$', p)))
