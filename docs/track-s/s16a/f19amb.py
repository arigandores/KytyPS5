# S16a (Probe Designer, HPP-605): offline count over the S13b catalogue (C:/kyty/s288/s13/seeds/PPSA21564), read only.
# Parses every translation-cache file (format KytySC3, shaderTranslationCache.cpp WritePlan / Save at KytyPS5 5fc57612)
# and the recipes (pipelineCache.cpp RecordGraphicsRecipe / RecordComputeRecipe), then counts:
#  - permutations whose specialization has an image with manual_depth_compare=1 on a plan image with depth_compare=1
#    (the only specialization bit the KYTY_FIX_F19=1 rule can flip; old rule: manual = non-null and format != k32Float)
#  - recipes referencing such a permutation (F19-ambiguous without the guest format).
# Self-check: every file must parse to its exact end (AtEnd) - otherwise the counts are void.
import os, re, struct, sys, collections, hashlib

ROOT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s13/seeds/PPSA21564'

class R:
    def __init__(s, d, p=0): s.d = d; s.p = p
    def u8(s): v = s.d[s.p]; s.p += 1; return v
    def u32(s): v = struct.unpack_from('<I', s.d, s.p)[0]; s.p += 4; return v
    def i32(s): v = struct.unpack_from('<i', s.d, s.p)[0]; s.p += 4; return v
    def u64(s): v = struct.unpack_from('<Q', s.d, s.p)[0]; s.p += 8; return v
    def skip(s, n): s.p += n
    def podvec(s, size): n = s.u32(); b = s.d[s.p:s.p + n * size]; s.p += n * size; return n, b
    def string(s): n = s.u32(); s.p += n
    def value(s): s.p += 12

def shader_info(r):
    r.podvec(36)  # buffers
    images = []
    for _ in range(r.u32()):
        r.skip(4 * 2 + 4 * 4 + 4 + 4 + 4)  # source, first_use_pc, 4 enums, mip_count, conv, swizzle
        flags = [r.u8() for _ in range(7)]  # read written atomic depth_compare cube r128 manual
        r.skip(4 * 4)  # depth_compare_op, indirect_root, mapping_offset, iterations
        r.podvec(4)
        images.append(flags[3])
    r.podvec(12); r.podvec(12)  # samplers, sampled pairs
    for _ in range(r.u32()):
        r.skip(12); r.string(); r.skip(1)
    for _ in range(r.u32()):
        r.skip(12); r.string()
    r.skip(32 + 4 + 4 + 1 + 1)
    return images

def plan(r):
    r.skip(4 + 8 + 4 + 4)
    for _ in range(r.u32()):
        r.skip(4 + 8); n = r.u32(); r.skip(12 * n)
    r.podvec(72)
    for _ in range(r.u32()):
        r.skip(4); r.skip(12 * 8)
        if r.u8(): r.skip(20)
    r.podvec(4)
    for _ in range(r.u32()):
        r.value(); r.skip(4 + 1)
    r.podvec(1); r.skip(3)
    for _ in range(r.u32()):
        r.value(); r.podvec(4); r.podvec(4)
    r.skip(28); r.skip(12 * 4)
    return shader_info(r)

def compiled(r):
    r.skip(4 + 8 + 4 * 5)
    shader_info(r)
    r.skip(12); r.podvec(4)
    for _ in range(r.u32()):
        r.skip(4); r.podvec(4)

files = sorted(x for x in os.listdir(ROOT) if re.match(r'^(vs|ps|cs)_[0-9a-f]{16}_[0-9a-f]{16}\.bin$', x))
perm_amb = {}      # key tuple -> list of bool per permutation
bad = 0; perms = 0; amb_perms = 0; files_amb = 0; dc_files = 0
for name in files:
    d = open(os.path.join(ROOT, name), 'rb').read()
    nl = d.index(b'\n') + 1
    r = R(d, nl + 8)
    try:
        st = r.u32(); h = r.u64(); udc = r.u32(); cs = r.u32(); n = r.u32()
        ss = struct.unpack_from('<%dI' % n, d, r.p); r.p += 4 * n
        base_dc = plan(r)
        flags = []
        for _ in range(r.u32()):
            r.podvec(12)
            ni, ib = r.podvec(44)
            manual = any(ib[44 * i + 33] and i < len(base_dc) and base_dc[i] for i in range(ni))
            # candidate (indirect) images beyond the plan count: inherit the root; count any manual flag there too
            manual = manual or any(ib[44 * i + 33] for i in range(len(base_dc), ni))
            compiled(r)
            r.podvec(4)
            flags.append(manual)
        if r.p != len(d):
            raise ValueError('not at end %d/%d' % (r.p, len(d)))
    except Exception as e:
        bad += 1; print('PARSE_FAIL', name, e); continue
    perm_amb[(st, h, udc, cs, tuple(ss))] = flags
    perms += len(flags); amb_perms += sum(flags); files_amb += any(flags); dc_files += any(base_dc)

d = open(os.path.join(ROOT, 'pipelines.bin'), 'rb').read()
n = struct.unpack_from('<I', d, 8)[0]; p = 12 + n; cnt = struct.unpack_from('<I', d, p)[0]; p += 4
def key(p):
    st, h, udc, cs, k = struct.unpack_from('<IQIII', d, p); ss = struct.unpack_from('<%dI' % k, d, p + 24)
    return (st, h, udc, cs, tuple(ss)), p + 24 + 4 * k
rec = collections.Counter()
import json, lzma
EBOOT = sys.argv[2] if len(sys.argv) > 2 else 'C:/kyty/KytyPS5/docs/track-f/f23a/scan_eboot.jsonl.xz'
eb = set()
with lzma.open(EBOOT, 'rt') as f:
    for l in f: eb.add(int(json.loads(l)['hash'], 16))
gcn = collections.Counter(); addr = collections.Counter(); both = collections.Counter()
progs = set(); progs_in = collections.Counter()
for kk in perm_amb: progs.add((kk[0], kk[1]))
for s, h in progs: progs_in[(s, h in eb)] += 1
for _ in range(cnt):
    k = d[p]; p += 1; refs = []
    if k == 1:
        a, p = key(p); ia = struct.unpack_from('<I', d, p)[0]; p += 4; refs.append((a, ia))
        psa = d[p]; p += 1
        if psa:
            b, p = key(p); ib = struct.unpack_from('<I', d, p)[0]; p += 4; refs.append((b, ib))
        p += 44 + 516 + 125
        vs = d[p:p + 10288]; p += 10288 + (376 if psa else 0)
        rn = struct.unpack_from('<i', vs, 10148)[0]; bn = struct.unpack_from('<i', vs, 10160)[0]
        used = False
        for j in range(max(rn, bn, 0)):
            f0, f1 = struct.unpack_from('<II', vs, 16 * j); ba = struct.unpack_from('<Q', vs, 1024 + 280 * j)[0]
            used = used or bool(f0 or (f1 & 0xffff) or ba)
        addr[used] += 1
    else:
        a, p = key(p); ia = struct.unpack_from('<I', d, p)[0]; p += 4 + 216; refs.append((a, ia))
    missing = any(kk not in perm_amb or ii >= len(perm_amb[kk]) for kk, ii in refs)
    amb = (not missing) and any(perm_amb[kk][ii] for kk, ii in refs)
    rec[(k, 'missing' if missing else ('f19_ambiguous' if amb else 'clean'))] += 1
    g = all(kk[1] in eb for kk, ii in refs); gcn[(k, g)] += 1; both[(g, amb)] += 1
print('files', len(files), 'parse_fail', bad, 'files_with_depth_compare_image', dc_files, 'files_with_manual_perm', files_amb)
print('permutations', perms, 'f19_ambiguous_permutations', amb_perms)
print('recipes', cnt, 'end_ok', p == len(d), dict(rec))
print('programs (stage enum, in eboot)', dict(progs_in))
print('recipes all-stage GCN in eboot (kind, found)', dict(gcn))
print('graphics recipes with nonzero address words in used VS input slots (True/False)', dict(addr))
print('recipes (gcn_found, f19_ambiguous)', dict(both))
print('ALL OK' if bad == 0 and p == len(d) else 'CHECK FAILED')
