"""M1a: verify every basis of form b3dc9c67:<path>:<N> - line N equals anchor and line N+1 equals anchor_plus1 (strip)."""
import json, re, subprocess, collections, os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
GIT = 'C:/Program Files/Git/cmd/git.exe'
R = json.load(open('C:/kyty/m657/m1a/merged_raw.json', encoding='utf-8'))
cache = {}
def lines(path):
    if path not in cache:
        p = subprocess.run([GIT, '-C', 'C:/kyty/KytyPS5', 'show', 'b3dc9c67:' + path], capture_output=True)
        cache[path] = p.stdout.decode('utf-8', 'replace').split('\n') if p.returncode == 0 else None
    return cache[path]
RE = re.compile(r'b3dc9c67:([^:\s]+):(\d+)')
stat = collections.Counter()
bad = []
for h, v in R.items():
    m = RE.search(v['basis'])
    if not m:
        stat['no_line_basis'] += 1
        continue
    path, n = m.group(1), int(m.group(2))
    L = lines(path)
    if L is None:
        stat['no_file'] += 1; bad.append((h, 'nofile', path)); continue
    a = L[n - 1].strip() if n - 1 < len(L) else None
    b = L[n].strip() if n < len(L) else None
    ok_a = a == v['anchor'].strip()
    ok_b = b == v['anchor_plus1'].strip()
    if ok_a and ok_b:
        stat['ok'] += 1
    else:
        stat['mismatch'] += 1
        bad.append((h, path, n, ok_a, ok_b, repr(a)[:80], repr(v['anchor'])[:80], repr(b)[:60], repr(v['anchor_plus1'])[:60]))
print(dict(stat))
for x in bad:
    print(x)
kinds = collections.Counter()
for v in R.values():
    if not RE.search(v['basis']):
        kinds[v['basis'].split(':')[0][:20]] += 1
print(kinds.most_common(20))
