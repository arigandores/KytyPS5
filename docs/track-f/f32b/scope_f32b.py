# F32b (HPP-734): files under C:/kyty modified after 2026-10-01Z that look like emulator output but are outside the sweep glob of p.672(b)(2)
import os, re, time, collections, sys
T0 = 1790812800  # 2026-10-01T00:00:00Z
known = set(l.split('\t')[0] for l in open('C:/kyty/f287/f32a/loglist_f32a.tsv', encoding='utf-8'))
GLOB = re.compile(r'^(log_.*\.txt|_kyty.*\.txt)(\.xz)?$')
out = []
c = collections.Counter()
for root, dirs, files in os.walk('C:/kyty'):
    if os.path.exists('C:/kyty/SEALED_RUN.lock'):
        print('LOCK'); sys.exit(3)
    r = root.replace(chr(92), '/')
    if '/games/' in r + '/' or '/.git' in r:
        dirs[:] = []
        continue
    for f in files:
        p = r + '/' + f
        try:
            st = os.stat(p)
        except OSError:
            continue
        if st.st_mtime <= T0:
            continue
        if GLOB.match(f):
            c['glob'] += 1
            if p not in known:
                c['glob_not_in_list'] += 1
                out.append(('GLOBMISS', st.st_size, p))
            continue
        if not re.search(r'\.(txt|log)(\.xz)?$', f):
            continue
        if st.st_size < 200000:
            continue
        if f.endswith('.xz'):
            out.append(('XZ_OTHER', st.st_size, p))
            continue
        try:
            with open(p, 'rb') as fh:
                b = fh.read(1 << 20)
        except OSError:
            continue
        tags = [k.decode() for k in (b'Fork build', b'FrameTrace', b'GuestOut', b'Level has started', b'SysFileRead', b'[Vulkan]') if k in b]
        if tags:
            out.append(('EMUTEXT:' + ','.join(tags), st.st_size, p))
print(dict(c))
print(collections.Counter(o[0] for o in out))
with open(sys.argv[1], 'w', encoding='utf-8') as o:
    for x in out:
        o.write('%s\t%d\t%s\n' % x)
