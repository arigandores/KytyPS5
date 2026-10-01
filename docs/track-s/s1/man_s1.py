#!/usr/bin/env python3
# S1 (Red Team): own manifest of snap0 and of the installed caches (read only), compared with S0's manifest lines.
import os, hashlib, sys
EMU = 'C:/kyty/KytyPS5/ps5 em'
def man(root_map):
    out = []
    for prefix, root in root_map:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                rel = prefix + os.path.relpath(p, root).replace('\\', '/')
                h = hashlib.sha256()
                with open(p, 'rb') as fh:
                    for b in iter(lambda: fh.read(1 << 20), b''):
                        h.update(b)
                out.append('%s %d %s' % (rel, os.path.getsize(p), h.hexdigest()))
    return sorted(out)
snap = man([('PipelineCache/', 'C:/kyty/s288/snap0/PipelineCache'), ('ShaderCache_PPSA21564/', 'C:/kyty/s288/snap0/ShaderCache_PPSA21564')])
inst = man([('PipelineCache/', EMU + '/_PipelineCache'), ('ShaderCache_PPSA21564/', EMU + '/_ShaderCache/PPSA21564')])
s0 = open('C:/kyty/s288/s0/out/snap0_manifest.txt', encoding='utf-8').read().splitlines()
for name, m in (('snap0', snap), ('installed', inst)):
    txt = '\n'.join(m) + '\n'
    open('C:/kyty/s288/s1/man_%s.txt' % name, 'w', newline='\n').write(txt)
    print(name, 'files', len(m), 'bytes', sum(int(x.split(' ')[1]) for x in m), 'sha_text', hashlib.sha256(txt.encode()).hexdigest(),
          'eq_S0_lines', m == s0, 'only_here', len(set(m) - set(s0)), 'only_S0', len(set(s0) - set(m)))
print('installed == snap0 lines:', inst == snap)
