import os, re, sys
pat = re.compile(sys.argv[1])
roots = sys.argv[2:] or ['C:/kyty/KytyPS5/src']
for rootdir in roots:
    for root, d, fs in os.walk(rootdir):
        for f in fs:
            if not f.endswith(('.cpp', '.h', '.inc')):
                continue
            p = os.path.join(root, f).replace(os.sep, '/')
            with open(p, 'rb') as fh:
                lines = fh.read().decode('utf8', 'replace').split(chr(10))
            for i, l in enumerate(lines, 1):
                if pat.search(l):
                    print(p.replace('C:/kyty/KytyPS5/', '') + ':' + str(i) + ': ' + l.strip()[:170])
