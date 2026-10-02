D = 'C:/kyty/KytyPS5/docs/session-145/audit/'
src = open(D + 'mf145.py', 'rb').read().decode('utf-8')
def rep(a, b, n=1):
    global src
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
rep("# mf145.py - Session Auditor, s145 step 3 (HPP-353): cache manifests runs145/cache_<tag>.{before,after}.json - files added /",
    "# mf146.py - Session Auditor, s146 step 3 (HPP-389): cache manifests runs146/cache_<tag>.{before,after}.json - files added /")
rep("R = 'C:/kyty/s145/runs145'", "R = 'C:/kyty/s146/runs146'")
rep("order = ['w145_00', 'w145_01']\nfor i in range(2, 18):\n    order += ['v145_%02d' % i, 'w145_%02d' % i]",
    "order = ['i146_v', 'w146_00'] + ['r146_%02d' % i for i in range(1, 5)]\nfor i in range(5, 20):\n    order += ['v146_%02d' % i, 'w146_%02d' % i]")
a = src.index("ref = load('C:/kyty/s144/runs144/cache_w144_20.after.json')")
b = src.index("prev = ('start', s)")
src = src[:a] + ("ref = load('C:/kyty/s145/runs145/cache_w145_17.after.json')\n"
    "s = load(R + '/cache_i146_v.before.json')\n"
    "print('WARM-UP before manifest sha256 %s entries %s; against the end of the s145 series (cache_w145_17.after.json, entries %s): (added, removed, changed) %s; pipelines.bin sha %s -> %s' % (\n"
    "    hashlib.sha256(open(R + '/cache_i146_v.before.json', 'rb').read()).hexdigest()[:16], cnt(s), cnt(ref) if ref else None, diff(ref, s) if ref else 'n/a',\n"
    "    str(ref.get(('shader', 'pipelines.bin'), ('?',))[0])[:8] if ref else None, str(s.get(('shader', 'pipelines.bin'), ('?',))[0])[:8]))\n"
    "st = load(R + '/cache_start.json')\n"
    "ia = load(R + '/cache_i146_v.after.json')\n"
    "print('SERIES start manifest cache_start.json sha256 %s entries %s; against the gate reference cache_i146_v.after.json (sha256 %s): (added, removed, changed) %s' % (\n"
    "    hashlib.sha256(open(R + '/cache_start.json', 'rb').read()).hexdigest()[:16], cnt(st), hashlib.sha256(open(R + '/cache_i146_v.after.json', 'rb').read()).hexdigest()[:16], diff(ia, st) or 'same'))\n") + src[b:]
rep("    new = sorted(k[1] for k in (set(fa) - set(fb)) if k[0] == 'shader') if fa is not None and fb is not None else []",
    "    new = sorted(k[1] for k in (set(fa) - set(fb)) if k[0] == 'shader') if fa is not None and fb is not None else []\n"
    "    nv = sum(1 for x in new if 'variant_' in x)\n"
    "    vf = sorted(set(x.replace(chr(92), '/').split('/')[0] for k in (fa or {}) for x in [k[1]] if k[0] == 'shader' and 'variant_' in x))\n"
    "    new = [x.replace(chr(92), '/').split('/')[-1] for x in new]\n"
    "    pk = [k for k in (fa or {}) if k[0] == 'shader' and k[1].replace(chr(92), '/').endswith('pipelines.bin')]\n"
    "    pch = [k[1].replace(chr(92), '/') for k in pk if fb is not None and fb.get(k) != fa.get(k)]")
rep("new shader files %d (cs %d, ps %d, vs %d, other %d)' % (", "new shader files %d (cs %d, ps %d, vs %d, other %d); of them in a variant folder %d; variant folders %s; recipe files changed %s' % (")
rep("        sum(1 for x in new if not x.startswith(('cs_', 'ps_', 'vs_')))))", "        sum(1 for x in new if not x.startswith(('cs_', 'ps_', 'vs_'))), nv, vf, pch))")
assert '145' not in src.replace('cache_w145_17', '').replace('s145/runs145', '').replace('s145 series', ''), [l for l in src.split(chr(10)) if '145' in l]
open('C:/kyty/s146/step3/mf146.py', 'wb').write(src.encode('utf-8'))
print('written')
