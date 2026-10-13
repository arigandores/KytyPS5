import os, re, sys, glob, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present, exit'); sys.exit(3)
SRC = 'C:/kyty/KytyPS5/src'
GAME = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app'
files = ['libs/libAmpr.cpp', 'libs/libSysmodule.cpp', 'libs/libSystemService.cpp', 'libs/libAppContent.cpp', 'libs/libKernel.cpp']
want_kernel = re.compile(r'UserEvent|AmprEvent|AmprSystemEvent|WaitEqueue|MapDirectMemory|MapNamedDirectMemory|Munmap|ReleaseDirectMemory|AllocateDirectMemory|AllocateMainDirectMemory|ReserveVirtualRange|BatchMap|MapFlexible|CreateEqueue')
nids = []
for f in files:
    for ln, line in enumerate(open(os.path.join(SRC, f), encoding='utf-8', errors='replace'), 1):
        m = re.search(r'LIB_FUNC\("([^"]+)",\s*([\w:]+)\)', line)
        if not m:
            continue
        if f.endswith('libKernel.cpp') and not want_kernel.search(m.group(2)):
            continue
        if f.endswith('libSystemService.cpp') and 'SystemService::' not in m.group(2):
            continue
        if f.endswith('libAppContent.cpp') and 'Initialize' not in m.group(2):
            continue
        nids.append((f, ln, m.group(1), m.group(2)))
bins = [os.path.join(GAME, 'eboot.bin')] + sorted(glob.glob(os.path.join(GAME, 'sce_module', '*.prx')))
data = {}
for b in bins:
    d = open(b, 'rb').read()
    data[b] = d
    print('BIN', os.path.basename(b), len(d), hashlib.sha256(d).hexdigest()[:16])
imp = 0
for f, ln, nid, name in nids:
    hits = []
    for b, d in data.items():
        pat = re.compile(re.escape(nid.encode()) + rb'#([A-Za-z0-9_+\-]+)#([A-Za-z0-9_+\-]+)\x00')
        for m in pat.finditer(d):
            hits.append('%s:%s#%s' % (os.path.basename(b), m.group(1).decode(), m.group(2).decode()))
    if hits:
        imp += 1
    print('%s %-14s %-60s %s' % ('IMP' if hits else '---', nid, f + ':' + str(ln) + ' ' + name, ','.join(sorted(set(hits)))))
print('TOTAL nids', len(nids), 'imported', imp)
