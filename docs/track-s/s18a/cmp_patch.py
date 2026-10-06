"""S18a (HPP-642): for a source patch and its simulated cherry-pick (git show --format= output), compare per file the
ordered list of changed lines (+/-, without the ---/+++ headers) and count context/header lines that differ.
Usage: python cmp_patch.py <src.diff> <sim.diff> [<only path prefix>]
"""
import sys


def parse(path, only):
    files = {}
    cur = None
    for line in open(path, 'rb').read().decode('utf-8').split('\n'):
        if line.startswith('diff --git '):
            cur = line.split(' b/', 1)[1]
            files[cur] = {'changed': [], 'context': []}
            continue
        if cur is None:
            continue
        if line.startswith('+++ ') or line.startswith('--- '):
            continue
        if line.startswith('+') or line.startswith('-'):
            files[cur]['changed'].append(line)
        elif line.startswith(' '):
            files[cur]['context'].append(line)
    if only:
        files = {k: v for k, v in files.items() if any(k.startswith(p) for p in only)}
    return files


only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
a = parse(sys.argv[1], only)
b = parse(sys.argv[2], only)
ok = True
for f in sorted(set(a) | set(b)):
    if f not in a or f not in b:
        print('%s: only in %s' % (f, 'source' if f in a else 'simulated'))
        ok = False
        continue
    same = a[f]['changed'] == b[f]['changed']
    ok &= same
    ctx_a, ctx_b = a[f]['context'], b[f]['context']
    print('%s: changed lines %d / %d identical=%s; context lines %d / %d identical=%s' % (
        f, len(a[f]['changed']), len(b[f]['changed']), same, len(ctx_a), len(ctx_b), ctx_a == ctx_b))
print('CHANGED LINES IDENTICAL' if ok else 'CHANGED LINES DIFFER')
