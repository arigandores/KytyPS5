# F4c: independent check of F4b RC1 (read-only, no game). ASCII output.
import hashlib, re, sys
EM = 'C:/kyty/KytyPS5/ps5 em/'
bins = {'9235a7ac': EM + 'kyty_emulator.exe',
        '34d293ad': 'C:/kyty/f287/bin/kyty_emulator_34d293ad.exe',
        '5821482a': 'C:/kyty/f287/bin/kyty_emulator_5821482a.exe'}
for k, p in bins.items():
    b = open(p, 'rb').read()
    sha = hashlib.sha256(b).hexdigest()
    sigs = sorted(set(m.decode() for m in re.findall(rb'(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])', b)))
    print('bin', k, 'sha256', sha, 'has699c1e4b', b.count(b'699c1e4b7db359067b461e029b913c4b6e78dc90'),
          'has846a041a', len([s for s in sigs if s.startswith('846a041a')]),
          'DualSrcBlend', b.count(b'DualSrcBlend: supported='), 'stale', b.count(b'stale recipes'))
pb = open(EM + '_ShaderCache/PPSA21564/pipelines.bin', 'rb').read()
print('pipelines.bin sha256', hashlib.sha256(pb).hexdigest(), 'bytes', len(pb))
m = re.search(rb'KytySC3:[0-9a-f]{8,40}[^\x00]{0,80}', pb[:4096])
print('pipelines.bin head sig', m.group(0)[:120].decode('ascii', 'replace').encode('ascii','replace').decode() if m else None)
for tag in ['f2c_a', 'f2c_b', 'f2c_c']:
    p = 'C:/kyty/f287/f2c/log_%s.txt' % tag
    hits = []
    with open(p, 'rb') as f:
        for line in f:
            if b'PipelinePrecache' in line or b'DualSrcBlend' in line:
                hits.append(line.strip()[:200].decode('ascii', 'replace'))
                if len(hits) >= 6: break
    print('log', tag, 'precache lines', len(hits))
    for h in hits: print('   ', h)
