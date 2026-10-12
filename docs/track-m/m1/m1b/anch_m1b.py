# M1b: own check of anchors "<commit>:<path>:<line>" (anchor text and +1) for a sample of themes, against git show (no M1a code reused).
# Usage: python anch_m1b.py T010 T011 ...   (cwd = KytyPS5 root)
import csv, subprocess, sys, re
D = 'docs/track-m/m1/'
want = set(sys.argv[1:])
rows = [r for r in csv.DictReader(open(D + 'upstream_detail.tsv', encoding='utf-8', newline=''), delimiter='\t', quoting=csv.QUOTE_NONE)
        if r['тема'] in want]
cache = {}
def lines(commit, path):
    k = (commit, path)
    if k not in cache:
        p = subprocess.run(['git', 'show', f'{commit}:{path}'], capture_output=True)
        cache[k] = p.stdout.decode('utf-8', 'replace').split('\n') if p.returncode == 0 else None
    return cache[k]
ok = True
seen = set()
for r in rows:
    m = re.search(r'([0-9a-f]{8}):([^:\s]+):(\d+)', r['основание'])
    tag = f"{r['тема']} {r['класс']} {r['sha'][:9]}"
    if not m:
        print(tag, 'NO_ANCHOR', r['основание'][:60])
        continue
    key = m.group(0)
    if key in seen:
        continue
    seen.add(key)
    c, path, n = m.group(1), m.group(2), int(m.group(3))
    L = lines(c, path)
    if L is None:
        print(tag, 'PATH_MISSING', key); ok = False; continue
    a, a1 = r['якорь'].strip(), r['якорь_плюс1'].strip()
    got, got1 = L[n - 1].strip() if n <= len(L) else None, L[n].strip() if n < len(L) else None
    st = 'OK' if (got == a and got1 == a1) else 'MISMATCH'
    if st != 'OK':
        ok = False
    print(tag, st, key)
    if st != 'OK':
        print('   want:', a[:120], '|', a1[:120]); print('   got :', (got or '')[:120], '|', (got1 or '')[:120])
print('ALL OK' if ok else 'FAILED')
