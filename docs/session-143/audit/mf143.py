# mf143.py - Session Auditor, s143 step 3 (HPP-300), item 249 (v): the recipe file at the start and the end of every
# sc143 tag, by the cache manifests runs143/cache_<tag>.{before,after}.json: size -> number of records -> the sha256 of
# the file rebuilt from the current file (header with that count + the first N records) against the manifest sha256.
# Also: frames with "AsyncPipelines: skipped draw" counted by the frame= id of the line (second reading of the form).
import json, hashlib, struct, re, mmap
CUR = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/pipelines.bin'
R = json.load(open('C:/kyty/s143/step3/recipes143.json'))
ends = R['_ends_cur']
hdr = R['cur']['header_bytes']
d = open(CUR, 'rb').read()
assert hashlib.sha256(d).hexdigest() == R['cur']['sha256'], 'the current file changed since recipes143.py'
K = R['cur']['flagged'][0]['index']
size2n = {ends[i]: i + 1 for i in range(len(ends))}
def rebuilt(n):
    return hashlib.sha256(d[:hdr - 4] + struct.pack('<I', n) + d[hdr:ends[n - 1]]).hexdigest()
print('snap0 (1842 records) rebuilt sha = snap0 sha: %s' % (rebuilt(1842) == R['snap0']['sha256']))
print('seed (638 records) rebuilt sha = seed sha: %s' % (rebuilt(638) == R['seed']['sha256']))
ok = True
prev = None
for i in range(1, 11):
    for t in ('v143_%02d' % i, 'w143_%02d' % i):
        for ph in ('before', 'after'):
            m = json.load(open('C:/kyty/s143/runs143/cache_%s.%s.json' % (t, ph)))
            row = [f for f in m['files'] if f[0] == 'shader' and f[1] == 'pipelines.bin']
            drv = [f for f in m['files'] if f[0] == 'pipeline' and f[1] == 'PPSA21564.bin']
            if not row:
                print('%s %s: NO pipelines.bin row' % (t, ph)); ok = False; continue
            size, sha = row[0][2], row[0][4]
            n = size2n.get(size)
            same = (n is not None and rebuilt(n) == sha)
            ok &= same
            cont = '' if prev is None else (' = previous manifest' if prev == sha else ' CHANGED since the previous manifest')
            if ph == 'before' and prev is not None and prev != sha:
                ok = False
            print('%s %s taken %s pipelines.bin %d bytes -> %s records, rebuilt sha = manifest sha %s, holds record %d: %s; driver cache %s bytes%s' % (
                t, ph, m.get('taken_utc'), size, n, same, K, (n is not None and n > K), drv[0][2] if drv else None, cont if ph == 'before' else ''))
            prev = sha
print('MANIFEST CHAIN: %s' % ('ALL OK' if ok else 'FAIL'))
FR = re.compile(b' frame=([0-9]+)')
for i in range(1, 11):
    t = 'v143_%02d' % i
    with open('C:/kyty/s143/log_%s.txt' % t, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        ids = set(); lines = 0; noid = 0; sample = None
        p = mm.find(b'AsyncPipelines: skipped draw')
        while p != -1:
            e = mm.find(b'\x0a', p)
            ln = mm[p:e]
            lines += 1
            q = FR.search(ln)
            if q: ids.add(int(q.group(1)))
            else: noid += 1
            if sample is None: sample = ln[:200].decode('ascii', 'replace')
            p = mm.find(b'AsyncPipelines: skipped draw', e)
        mm.close()
    S = json.load(open('C:/kyty/s143/runs143/%s.score.json' % t))
    print('SKIP %s lines %d distinct frame= ids %d (lines without id %d) scorer frames %d %s' % (
        t, lines, len(ids), noid, S['skip']['frames'], 'EQUAL' if len(ids) == S['skip']['frames'] else 'DIFFERENT'))
    if i == 1: print('SAMPLE', sample)
print('ALL DONE')
