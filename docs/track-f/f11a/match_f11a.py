# F11a (HPP-455), member (4): match the SPIR-V of the compute shaders bound at EID 3399-3455 (rd/cs_e<EID>.spv
# written by rd_f11a.py) to guest shader hashes, by sha256 of the module, against every module stored in the
# translation cache files cs_<hash16>_<key16>.bin (read only; extractor of docs/track-f/f10a/run_k4d.py, calibrated
# there 269 of 269) and the S7 corpus outputs work/A/A_<hash16>_*/out.spv. Verdict "BVH" for an EID: its guest
# hash is one of the programs whose reachable decode has IMAGE_BVH(64)_INTERSECT_RAY (t1scan_f11a.py --all,
# all ELFs of eboot.bin). No process with a device; exits 3 when C:/kyty/SEALED_RUN.lock exists.
import os
import sys
import glob
import struct
import hashlib

LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    sys.exit(3)
NL = chr(10)
D = 'C:/kyty/f287/f11a/'
EIDS = [3399, 3413, 3419, 3427, 3433, 3441, 3447, 3455]
MAGIC = struct.pack('<I', 0x07230203)
ROOTS = ['C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564', 'C:/kyty/s288/snap0/ShaderCache_PPSA21564',
         'C:/kyty/f287/f7a/cache_run', 'C:/kyty/f287/f7a/cache_snap']


def modules(data):
    out = []
    pos = 0
    while True:
        i = data.find(MAGIC, pos)
        if i < 0:
            break
        if i < 4:
            pos = i + 4
            continue
        n = struct.unpack_from('<I', data, i - 4)[0]
        if n >= 5 and i + 4 * n <= len(data):
            out.append(data[i:i + 4 * n])
            pos = i + 4 * n
        else:
            pos = i + 4
    return out


lines = []


def p(*a):
    lines.append(' '.join(str(x) for x in a))


want = {}
for eid in EIDS:
    fn = D + 'rd/cs_e%d.spv' % eid
    if os.path.exists(fn):
        want[eid] = hashlib.sha256(open(fn, 'rb').read()).hexdigest()
p('EIDs with SPIR-V from the replay:', len(want), 'of', len(EIDS))
index = {}
nfiles = nmods = 0
for root in ROOTS:
    files = glob.glob(root + '/**/cs_*.bin', recursive=True)
    for k, fn in enumerate(files):
        if k % 500 == 0 and os.path.exists(LOCK):
            sys.exit(3)
        base = os.path.basename(fn)[:-4].split('_')
        if len(base) < 3:
            continue
        nfiles += 1
        for m_i, m in enumerate(modules(open(fn, 'rb').read())):
            nmods += 1
            index.setdefault(hashlib.sha256(m).hexdigest(), set()).add((base[1], fn.replace(chr(92), '/'), m_i))
for fn in glob.glob('C:/kyty/s288/s7/work/A/A_*/out.spv'):
    h16 = os.path.basename(os.path.dirname(fn)).split('_')[1]
    nmods += 1
    index.setdefault(hashlib.sha256(open(fn, 'rb').read()).hexdigest(), set()).add((h16, fn.replace(chr(92), '/'), 0))
p('indexed: cache files', nfiles, 'modules (cache + S7 out.spv)', nmods, 'distinct sha256', len(index))
bvh = set()
for ln in open(D + 't1scan_f11a.out.txt', encoding='utf-8'):
    if ln.startswith('all-ELF BVH program hashes:'):
        bvh = set(ln.split(':', 1)[1].split())
p('BVH programs of eboot.bin (t1scan_f11a.py --all):', len(bvh))
verdict = {}
for eid in EIDS:
    sha = want.get(eid)
    if sha is None:
        p('EID', eid, 'no SPIR-V')
        verdict[eid] = 'NO_SPIRV'
        continue
    hits = sorted(index.get(sha, set()))
    hashes = sorted(set(h for h, _, _ in hits))
    if not hashes:
        verdict[eid] = 'NOT_MATCHED'
    else:
        verdict[eid] = 'BVH' if any(h in bvh for h in hashes) else 'NO_BVH'
    p('EID', eid, 'spv_sha256', sha[:16], 'guest hash', ','.join(hashes) or '-', 'verdict', verdict[eid],
      'source', (hits[0][1] + ' module ' + str(hits[0][2])) if hits else '-')
p('SUMMARY', ' '.join('%d=%s' % (e, verdict[e]) for e in EIDS))
if os.path.exists(LOCK):
    sys.exit(3)
open(D + 'match_f11a.out.txt', 'wb').write((NL.join(lines) + NL).encode('utf-8'))
print(NL.join(lines))
