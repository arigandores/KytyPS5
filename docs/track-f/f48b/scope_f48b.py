# F48b (HPP-831): files under C:/kyty modified after 2026-10-10Z outside the sweep list of F48a that carry emulator text.
# Differences from scope_f48a.py (= scope_f32b.py): NO size threshold, NO extension filter (binary extensions excluded),
# stronger emulator markers incl. fatal/device-lost/stdout forms. Usage: python scope_f48b.py <out.tsv>
import os, re, collections, sys
T0 = 1791590400  # 2026-10-10T00:00:00Z
known = set(l.split('\t')[0] for l in open('C:/kyty/f287/f48a/sw/loglist_f32a.tsv', encoding='utf-8'))
GLOB = re.compile(r'^(log_.*\.txt|_kyty.*\.txt)(\.xz)?$')
BIN = re.compile(r'\.(exe|dll|pdb|obj|lib|pkl|bin|rdc|mp4|idx|png|jpg|zip|7z|gz|bundle|pack|idx|spv|nv12|o|a|ilk|exp|pch|ninja_deps|db|sqlite|dds|gnfp|json|py|pyc|cpp|h|hpp|c|cmake|md)$', re.I)
TAGS = (b'Fork build', b'FrameTrace', b'GuestOut', b'Level has started', b'[Vulkan]', b'--- Fatal Error ---', b'ErrorDeviceLost',
        b'GpuCheckpoint', b'Unhandled exception', b'GpuHangAbort', b'EmergencyShutdown', b'PipelinePrecache')
out = []; c = collections.Counter()
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
        c['mtime'] += 1
        if GLOB.match(f):
            c['glob'] += 1
            if p not in known:
                out.append(('GLOBMISS', st.st_size, p))
            continue
        if BIN.search(f) or st.st_size == 0:
            continue
        c['read'] += 1
        try:
            if f.endswith('.xz'):
                import lzma
                with lzma.open(p, 'rb') as fh:
                    b = fh.read(1 << 20)
            else:
                with open(p, 'rb') as fh:
                    b = fh.read(1 << 20)
        except Exception:
            continue
        tags = [k.decode() for k in TAGS if k in b]
        if tags:
            out.append(('EMUTEXT:' + ','.join(tags), st.st_size, p))
print(dict(c))
print(collections.Counter(o[0].split(':')[0] for o in out), 'under 200000 bytes:', sum(1 for o in out if o[1] < 200000))
with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as o:
    for x in sorted(out, key=lambda x: x[2]):
        o.write('%s\t%d\t%s\n' % x)
