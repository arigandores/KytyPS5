# F31a (HPP-729, ROADMAP s122 item 664(l)(3)): list of the game logs under C:/kyty with mtime >= the installation of dac02fb9
# (2026-10-02T06:52:29Z, C:/kyty/s146/step0/times.txt line 10), plain and .xz.  A file is a candidate by name
# ('log*.txt', 'log*.txt.xz', '_kyty*.txt', '_kyty*.txt.xz', 'stdout*' excluded) and a game log by content: the marker
# b'TITLE_ID, string = PPSA21564' in its first 256 KiB (plain) or first 4 MiB decompressed (.xz).
# Skipped directories: .git, build*, wt, _ShaderCache, _Shaders, _ShaderSeeds, _RenderDoc, games, node_modules, __pycache__,
# scrub, tools, VulkanSDK.  Fixture paths (the regex of loglist_f20a.py) are excluded.
# Output: <out.tsv> 'path <TAB> size <TAB> mtime_utc <TAB> json path or -', and a census on stdout.
# Usage: python loglist_f31a.py <out.tsv>
import calendar, lzma, os, re, sys, time

out = sys.argv[1]
T0 = calendar.timegm(time.strptime('2026-10-02T06:52:29', '%Y-%m-%dT%H:%M:%S'))
MARK = b'TITLE_ID, string = PPSA21564'
SKIP = {'.git', 'wt', '_ShaderCache', '_Shaders', '_ShaderSeeds', '_RenderDoc', 'games', 'node_modules', '__pycache__',
        'scrub', 'tools', 'VulkanSDK'}
fx = re.compile(r'/(fx/|fx_|work_|mut|test_|fixt)')
name_ok = re.compile(r'^(log.*\.txt(\.xz)?|_kyty.*\.txt(\.xz)?)$')
rows = []
cand = 0
old = 0
notgame = 0
for dp, dn, fn in os.walk('C:/kyty'):
    dn[:] = [x for x in dn if x not in SKIP and not x.startswith('build')]
    d = dp.replace(os.sep, '/')
    names = set(fn)
    for f in fn:
        if not name_ok.match(f):
            continue
        p = d + '/' + f
        if fx.search(p):
            continue
        cand += 1
        st = os.stat(p)
        if st.st_mtime < T0:
            old += 1
            continue
        try:
            if f.endswith('.xz'):
                with lzma.open(p, 'rb') as h:
                    head = h.read(1 << 22)
            else:
                with open(p, 'rb') as h:
                    head = h.read(1 << 18)
        except Exception as e:
            print('read error', p, type(e).__name__, e)
            continue
        if MARK not in head:
            notgame += 1
            continue
        js = '-'
        if f.startswith('log_'):
            tag = f[4:].split('.txt')[0]
            m = re.fullmatch(r'(.*)_a\d+', tag)
            for t in ([tag] + ([m.group(1)] if m else [])):
                for c in (t + '.json', t + '.json.xz'):
                    if c in names:
                        js = d + '/' + c
                        break
                if js != '-':
                    break
        rows.append((p, st.st_size, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(st.st_mtime)), js))
rows.sort(key=lambda r: r[0])
paths = [r[0] for r in rows]
assert len(set(paths)) == len(paths)
with open(out, 'w', encoding='utf-8', newline='\n') as o:
    for r in rows:
        o.write('%s\t%d\t%s\t%s\n' % r)
print('candidates', cand, 'older than T0', old, 'not game', notgame, 'game logs', len(rows),
      'xz', sum(1 for r in rows if r[0].endswith('.xz')), 'bytes', sum(r[1] for r in rows))
