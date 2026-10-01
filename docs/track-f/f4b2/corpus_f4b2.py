# F4b2 (HPP-347, Red Team): outcome of the own rewrite (spv_f4b2.rewrite, p.262(b)(1)) on every fragment
# module of the translation cache (read only). Only a census: which PS would be patched or skipped IF a
# pipeline with a SRC1 factor used them, and whether the Location 0 / Index 1 outputs have equal types.
# Usage: python corpus_f4b2.py <cache_dir>
import collections
import glob
import importlib.util
import os
import struct
import sys

spec = importlib.util.spec_from_file_location('s', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spv_f4b2.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

files = sorted(glob.glob(sys.argv[1] + '/ps_*.bin'))
count = collections.Counter()
mods_total = 0
mismatch = []
per_file_mods = collections.Counter()
for f in files:
    raw = open(f, 'rb').read()
    n = 0
    mb = struct.pack('<I', s.MAGIC)
    offs = []
    k = raw.find(mb)
    while k >= 0:
        offs.append(k)
        k = raw.find(mb, k + 1)
    for k in offs:  # byte offsets: modules need not be 4-aligned in the file
        body = raw[k:]
        words = list(struct.unpack('<%dI' % (len(body) // 4), body[:len(body) // 4 * 4]))
        st = 0
        e = s.walk(words, st)
        if not e:
            count['walk_failed'] += 1
            continue
        m = words[st:e]
        n += 1
        p = s.parse(m)
        if not any(ep[0] == 4 for ep in p['eps']):
            count['not_fragment'] += 1
            continue
        oc, out = s.rewrite(m)
        count[oc] += 1
        if oc == 'patched':
            q = s.parse(out)
            o = s.outputs(q)
            t0 = [r[2] for r in o if r[3] == [0] and r[4] == []]
            t1 = [r[2] for r in o if r[3] == [0] and r[4] == [1]]
            if t0 != t1:
                mismatch.append((os.path.basename(f), t0, t1))
    per_file_mods[n] += 1
    mods_total += n
print('files', len(files), 'modules', mods_total, 'modules per file', dict(per_file_mods))
for k, v in sorted(count.items()):
    print('outcome', k, v)
print('patched with Location 0 / Index 1 type mismatch:', len(mismatch))
for r in mismatch[:20]:
    print('  ', r)
