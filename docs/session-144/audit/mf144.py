# mf144.py - Session Auditor, s144 step 3 (HPP-333): the cache manifests runs144/cache_<tag>.{before,after}.json by own code.
#  (1) the start: cache_w144_00.before = C:/kyty/s143/runs143/cache_w143_10.after.json by path, size, sha256 (item 266 (c));
#  (2) continuity: after N = before N+1 over the 33 tags, per root;
#  (3) what a run changes: files added / removed / changed between before and after of each tag, per root; the recipe file
#      _ShaderCache/PPSA21564/pipelines.bin of W (item 254 (e): a W in the form writes no recipes) and of V;
#  (4) the live recipe file now against the last manifest.
# READ ONLY. No code of cachemf144.py / gate144.py.
import json, hashlib, os

S = 'C:/kyty/s144/runs144'
tags = ['w144_%02d' % i for i in range(0, 9)]
for i in range(9, 21):
    tags += ['v144_%02d' % i, 'w144_%02d' % i]


def load(p):
    m = json.load(open(p, encoding='utf-8'))
    return {(f[0], f[1]): (f[2], f[4]) for f in m['files']}, m.get('taken_utc'), hashlib.sha256(open(p, 'rb').read()).hexdigest()


def diff(a, b):
    add = sorted(k for k in b if k not in a)
    rem = sorted(k for k in a if k not in b)
    chg = sorted(k for k in a if k in b and a[k] != b[k])
    return add, rem, chg


def byroot(keys):
    o = {}
    for r, n in keys:
        o[r] = o.get(r, 0) + 1
    return o


ref, rt, rs = load('C:/kyty/s143/runs143/cache_w143_10.after.json')
b0, t0, s0 = load('%s/cache_w144_00.before.json' % S)
a, r, c = diff(ref, b0)
print('START: cache_w143_10.after.json sha256 %s (taken %s, %d files) against cache_w144_00.before.json sha256 %s (taken %s, %d files): added %d removed %d changed %d -> %s' % (
    rs, rt, len(ref), s0, t0, len(b0), len(a), len(r), len(c), 'EQUAL' if not (a or r or c) else 'DIFFERENT'))
ok = True
prev = None
prevt = None
wrec = True
for t in tags:
    b, tb, sb = load('%s/cache_%s.before.json' % (S, t))
    af, ta, sa = load('%s/cache_%s.after.json' % (S, t))
    if prev is not None:
        a, r, c = diff(prev, b)
        same = not (a or r or c)
        ok &= same
        if not same:
            print('BREAK between %s.after and %s.before: added %s removed %s changed %s' % (prevt, t, byroot(a), byroot(r), byroot(c)))
    a, r, c = diff(b, af)
    pb = b.get(('shader', 'pipelines.bin'))
    pa = af.get(('shader', 'pipelines.bin'))
    if t.startswith('w') and pb != pa:
        wrec = False
    print('RUN %s before %s (%s) after %s (%s): files %d -> %d; added %s removed %s changed %s; pipelines.bin %s bytes %s -> %s bytes %s%s' % (
        t, tb, sb[:12], ta, sa[:12], len(b), len(af), byroot(a), byroot(r), byroot(c), pb[0] if pb else None, pb[1][:8] if pb else None,
        pa[0] if pa else None, pa[1][:8] if pa else None, '' if pb == pa else '  <== recipes changed'))
    prev, prevt = af, t
print('CONTINUITY after N = before N+1 over %d tags: %s' % (len(tags), 'ALL OK' if ok else 'BREAKS'))
print('W RECIPES: pipelines.bin before = after in every W: %s' % wrec)
live = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/pipelines.bin'
h = hashlib.sha256(open(live, 'rb').read()).hexdigest()
last = prev.get(('shader', 'pipelines.bin'))
print('LIVE pipelines.bin now: %d bytes sha256 %s; in cache_w144_20.after.json: %s bytes %s; equal %s' % (os.path.getsize(live), h, last[0], last[1], h == last[1]))
print('ALL DONE')
