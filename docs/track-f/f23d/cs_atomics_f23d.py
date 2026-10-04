"""F23d (HPP-588): do the 18 form-A CS of F23a use atomics or storage writes (order-dependent output -> N_diff > 0 without a
driver error)? Reads the translation cache files cs_<hash16>_*.bin of the installed folder (read only), counts OpAtomic*
(opcodes 227..242, 4998..5000 not used) and OpStore into StorageBuffer/Image writes (OpImageWrite 99) per SPIR-V module.
Output: C:/kyty/f287/f23d/cs_atomics_f23d.out.txt"""
import glob
import os
import struct

FORMS = 'C:/kyty/KytyPS5/docs/track-f/f23a/b8_forms_normal.tsv'
CACHE = 'C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564/'
INV = 'C:/kyty/f287/f23c/inv_f23c_programs.tsv'
MAGIC = b'\x03\x02\x23\x07'
ATOMIC = set(range(227, 243))
out = []
cov = {}
for line in open(INV, encoding='utf-8').read().splitlines()[1:]:
    s, h, fb, caps = line.split('\t')
    cov[(s, h)] = caps != '-'
for line in open(FORMS, encoding='utf-8').read().splitlines()[1:]:
    if not line.strip():
        continue
    s, h = line.split('\t')[:2]
    if s != 'cs':
        continue
    files = sorted(glob.glob(CACHE + 'cs_%s_*.bin' % h))
    res = []
    for p in files:
        d = open(p, 'rb').read()
        i = d.find(MAGIC)
        while i >= 0:
            n = struct.unpack_from('<I', d, i - 4)[0]
            if not (5 < n and i + 4 * n <= len(d)):
                i = d.find(MAGIC, i + 4)
                continue
            w = struct.unpack_from('<%dI' % n, d, i)
            j = 5
            na = nw = 0
            while j < n:
                c = w[j] >> 16
                op = w[j] & 0xffff
                if c == 0:
                    break
                if op in ATOMIC:
                    na += 1
                if op == 99:
                    nw += 1
                j += c
            res.append((os.path.basename(p), na, nw))
            i = d.find(MAGIC, i + 4 * n)
    a = max((r[1] for r in res), default=-1)
    out.append('cs %s covered=%s files=%d modules=%d max_atomics=%d max_imagewrite=%d' % (
        h, 'yes' if cov.get(('cs', h)) else 'no', len(files), len(res), a, max((r[2] for r in res), default=-1)))
open('C:/kyty/f287/f23d/cs_atomics_f23d.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('\n'.join(out))
