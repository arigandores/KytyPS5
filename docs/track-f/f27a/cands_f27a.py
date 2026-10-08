import os, datetime, collections, sys
cut = datetime.datetime(2026, 9, 27, 1, 41).timestamp()
skip_top = {'build', 'KytyPS5', 'tools', 'scrub', '_cleanup401'}
skip_any = {'.git', '_ShaderCache', '_Shaders', 'games', '_RenderDoc', 'node_modules', 'vidframes', '_ShaderSeeds'}
c = []
old = 0
for dp, dn, fn in os.walk('C:/kyty'):
    dpn = dp.replace(os.sep, '/')
    if dpn.rstrip('/') == 'C:/kyty':
        dn[:] = [d for d in dn if d not in skip_top]
    dn[:] = [d for d in dn if d not in skip_any]
    for f in fn:
        if not (f.endswith('.txt') or f.endswith('.txt.xz') or f.endswith('.log') or f.endswith('.log.xz')):
            continue
        p = dpn + '/' + f
        try:
            st = os.stat(p)
        except OSError:
            continue
        if st.st_size < 200000:
            continue
        if st.st_mtime < cut:
            old += 1
            continue
        c.append((p, st.st_size, st.st_mtime))
emu = 'C:/kyty/KytyPS5/ps5 em'
for f in os.listdir(emu):
    p = emu + '/' + f
    if os.path.isfile(p) and (f.endswith('.txt')) and os.path.getsize(p) > 200000 and os.path.getmtime(p) >= cut:
        c.append((p, os.path.getsize(p), os.path.getmtime(p)))
tot = sum(x[1] for x in c)
print(len(c), 'files', round(tot / 2**30, 1), 'GiB; older skipped', old)
print('xz', sum(1 for x in c if x[0].endswith('.xz')))
with open(sys.argv[1], 'w', encoding='utf-8') as o:
    o.write('\n'.join(x[0] for x in c) + '\n')
d = collections.Counter(x[0].split('/')[2] for x in c)
print(d.most_common(80))
