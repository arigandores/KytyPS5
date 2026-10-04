import sys
for p in ['C:/kyty/f287/f18c/build/build.ninja', 'C:/kyty/s288/s12a/build/build.ninja']:
    L = open(p, 'rb').read().decode('utf-8', 'replace').split('\n')
    found = False
    for i, l in enumerate(L):
        ln = l.replace(chr(92), '/')
        if l.startswith('build ') and 'SDL2-static.dir' in ln and '/src/SDL.c.obj' in ln:
            blk = []
            k = i + 1
            while k < len(L) and L[k].startswith('  '):
                blk.append(L[k])
                k += 1
            toks = ' '.join(x for x in blk if 'DEFINES' in x or 'FLAGS' in x).split()
            dbg = [t for t in toks if 'DEBUG' in t.upper() or 'ASSERT' in t.upper() or t.startswith(('/O', '-O'))]
            print(p, 'tokens:', dbg)
            found = True
            break
    print(p, 'found', found)
