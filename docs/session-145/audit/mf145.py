# mf145.py - Session Auditor, s145 step 3 (HPP-353): cache manifests runs145/cache_<tag>.{before,after}.json - files added /
# removed / changed (sha256) per tag and per transition, by root (own reading; no scorer code). Rows of a manifest:
# [root, name, size, mtime_ns, sha256]. READ ONLY.
import json, os, hashlib

R = 'C:/kyty/s145/runs145'
order = ['w145_00', 'w145_01']
for i in range(2, 18):
    order += ['v145_%02d' % i, 'w145_%02d' % i]


def load(p):
    if not os.path.isfile(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    return {(x[0], x[1]): (x[4], x[2]) for x in d['files']}


def diff(a, b):
    res = {}
    for k in set(a) | set(b):
        e = res.setdefault(k[0], [0, 0, 0])
        if k not in a:
            e[0] += 1
        elif k not in b:
            e[1] += 1
        elif a[k] != b[k]:
            e[2] += 1
    return {r: tuple(v) for r, v in sorted(res.items()) if any(v)}


def cnt(a):
    return {r: sum(1 for k in a if k[0] == r) for r in ('shader', 'pipeline', 'glcache')}


ref = load('C:/kyty/s144/runs144/cache_w144_20.after.json')
s = load(R + '/cache_start.json')
print('START manifest sha256 %s entries %s; against the end of s144 (cache_w144_20.after.json, entries %s): (added, removed, changed) %s; pipelines.bin sha %s -> %s' % (
    hashlib.sha256(open(R + '/cache_start.json', 'rb').read()).hexdigest()[:16], cnt(s), cnt(ref), diff(ref, s),
    str(ref.get(('shader', 'pipelines.bin'), ('?',))[0])[:8], str(s.get(('shader', 'pipelines.bin'), ('?',))[0])[:8]))
prev = ('start', s)
breaks = 0
for t in order:
    fb = load('%s/cache_%s.before.json' % (R, t))
    fa = load('%s/cache_%s.after.json' % (R, t))
    tr = diff(prev[1], fb) if fb is not None and prev[1] is not None else None
    if tr:
        breaks += 1
    new = sorted(k[1] for k in (set(fa) - set(fb)) if k[0] == 'shader') if fa is not None and fb is not None else []
    print('TAG %s: %s -> before: %s; before -> after (added, removed, changed) %s; shader files after %s; pipelines.bin %s -> %s; new shader files %d (cs %d, ps %d, vs %d, other %d)' % (
        t, prev[0], tr if tr else ('same' if tr is not None else 'n/a'), diff(fb, fa) if fb is not None and fa is not None else 'n/a (manifest after missing)',
        cnt(fa)['shader'] if fa else None,
        str(fb.get(('shader', 'pipelines.bin'), ('?',))[0])[:8] if fb else None, str(fa.get(('shader', 'pipelines.bin'), ('?',))[0])[:8] if fa else None,
        len(new), sum(1 for x in new if x.startswith('cs_')), sum(1 for x in new if x.startswith('ps_')), sum(1 for x in new if x.startswith('vs_')),
        sum(1 for x in new if not x.startswith(('cs_', 'ps_', 'vs_')))))
    prev = (t + ' after', fa) if fa is not None else (t + ' before', fb)
print('TRANSITIONS with a difference (manifest after N != manifest before N+1): %d' % breaks)
print('ALL DONE')
