import os, sys
# usage: srch.py <root> <ext,ext> <pat1> [pat2 ...]
root = sys.argv[1]
exts = tuple(sys.argv[2].split(','))
pats = sys.argv[3:]
sys.stdout.reconfigure(encoding='utf-8')
for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith(exts):
            continue
        p = os.path.join(dp, f)
        try:
            L = open(p, 'rb').read().decode('utf-8', 'replace').split('\n')
        except Exception:
            continue
        for i, l in enumerate(L):
            for pat in pats:
                if pat in l:
                    print(p.replace(os.sep, '/'), i + 1, l.strip()[:180])
                    break
