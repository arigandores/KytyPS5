import re, os, sys
pat = re.compile(sys.argv[1])
root = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/KytyPS5/src'
for base, _, files in os.walk(root):
    for fn in files:
        if not fn.endswith(('.cpp', '.h', '.inc')): continue
        p = os.path.join(base, fn).replace(os.sep, '/')
        for i, l in enumerate(open(p, encoding='utf-8', errors='replace'), 1):
            if pat.search(l): print(p[len(root) + 1:], i, l.rstrip()[:170])
