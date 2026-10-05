"""S16d (HPP-608, ROADMAP s122 item 516(v)): probe P-S16 - catalogue, recipe and eboot.bin readers (read only).

Catalogue S13b: C:/kyty/s288/s13/seeds/PPSA21564 (manifest C:/kyty/s288/s13/seeds_manifest.txt, sha256 65a95adf...).
Translation cache files: format KytySC3 (shaderTranslationCache.cpp WritePlan / Save); the parse below is the one of
S16a docs/track-s/s16a/f19amb.py (parse to the exact end of every file), extended with the key and the number of the
images of each permutation whose stored manual comparison flag is set.
Recipes: pipelines.bin, format KytyPR1 (pipelineCache.cpp RecipeWriter / RecordGraphicsRecipe / RecordComputeRecipe).
GCN: AMDGPU ELFs inside eboot.bin, key = XXH3-64 of the section .shader_text (or .text), code = its first code_size
words (method of F11a t1scan_f11a.py / F23a gcn_f23a.py eboot_programs). GCN goes only to the link's work folder.
"""
import collections
import hashlib
import mmap
import os
import re
import struct

import xxhash

CATALOG = 'C:/kyty/s288/s13/seeds/PPSA21564'
MANIFEST = 'C:/kyty/s288/s13/seeds_manifest.txt'
MANIFEST_SHA = '65a95adf3de91f5f343253d3d0bdf51931411dd7dbe48518f9e28cfcaa0935fd'
EBOOT = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
SIG_PREFIX = 'KytySC3:26ce5fc7'
STAGE_NAME = {1: 'vs', 2: 'ps', 4: 'cs', 5: 'ms'}
NO_START = 0xFFFFFFFF


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest():
    """(manifest sha256, files listed, files whose size and sha256 match)."""
    msha = sha256_file(MANIFEST)
    listed = ok = 0
    bad = []
    for line in open(MANIFEST, 'r', encoding='utf-8'):
        parts = line.split()
        if len(parts) != 3:
            continue
        listed += 1
        name, size, sha = parts[0], int(parts[1]), parts[2]
        path = os.path.join(CATALOG, name)
        if os.path.exists(path) and os.path.getsize(path) == size and sha256_file(path) == sha:
            ok += 1
        else:
            bad.append(name)
    return msha, listed, ok, bad


class R:
    def __init__(s, d, p=0):
        s.d = d
        s.p = p

    def u8(s):
        v = s.d[s.p]
        s.p += 1
        return v

    def u32(s):
        v = struct.unpack_from('<I', s.d, s.p)[0]
        s.p += 4
        return v

    def u64(s):
        v = struct.unpack_from('<Q', s.d, s.p)[0]
        s.p += 8
        return v

    def skip(s, n):
        s.p += n

    def podvec(s, size):
        n = s.u32()
        b = s.d[s.p:s.p + n * size]
        s.p += n * size
        return n, b

    def string(s):
        n = s.u32()
        s.p += n

    def value(s):
        s.p += 12


def _shader_info(r):
    r.podvec(36)
    images = []
    for _ in range(r.u32()):
        r.skip(4 * 2 + 4 * 4 + 4 + 4 + 4)
        flags = [r.u8() for _ in range(7)]
        r.skip(4 * 4)
        r.podvec(4)
        images.append(flags[3])
    r.podvec(12)
    r.podvec(12)
    for _ in range(r.u32()):
        r.skip(12)
        r.string()
        r.skip(1)
    for _ in range(r.u32()):
        r.skip(12)
        r.string()
    r.skip(32 + 4 + 4 + 1 + 1)
    return images


def _plan(r):
    r.skip(4 + 8 + 4 + 4)
    for _ in range(r.u32()):
        r.skip(4 + 8)
        n = r.u32()
        r.skip(12 * n)
    r.podvec(72)
    for _ in range(r.u32()):
        r.skip(4)
        r.skip(12 * 8)
        if r.u8():
            r.skip(20)
    r.podvec(4)
    for _ in range(r.u32()):
        r.value()
        r.skip(4 + 1)
    r.podvec(1)
    r.skip(3)
    for _ in range(r.u32()):
        r.value()
        r.podvec(4)
        r.podvec(4)
    r.skip(28)
    r.skip(12 * 4)
    return _shader_info(r)


def _compiled(r):
    r.skip(4 + 8 + 4 * 5)
    _shader_info(r)
    r.skip(12)
    r.podvec(4)
    for _ in range(r.u32()):
        r.skip(4)
        r.podvec(4)


def parse_cache_file(path):
    """dict(sig, stage, hash, udc, code_size, state, perms=[manual image count of each permutation]) - raises on a
    parse that does not end at the end of the file."""
    d = open(path, 'rb').read()
    nl = d.index(b'\n') + 1
    sig = d[:nl - 1].decode('ascii')
    r = R(d, nl + 8)
    st = r.u32()
    h = r.u64()
    udc = r.u32()
    cs = r.u32()
    n = r.u32()
    ss = struct.unpack_from('<%dI' % n, d, r.p)
    r.p += 4 * n
    base_dc = _plan(r)
    perms = []
    for _ in range(r.u32()):
        r.podvec(12)
        ni, ib = r.podvec(44)
        manual = sum(1 for i in range(ni) if ib[44 * i + 33] and (i >= len(base_dc) or base_dc[i]))
        _compiled(r)
        r.podvec(4)
        perms.append(manual)
    if r.p != len(d):
        raise ValueError('not at end %d/%d' % (r.p, len(d)))
    return dict(sig=sig, stage=st, hash=h, udc=udc, code_size=cs, state=tuple(ss), perms=perms)


def key_file_name(stage, h, udc, code_size, state):
    """ShaderTranslationCache::PathOf: <vs|ps|cs>_<hash>_<XXH3(udc, code_size, static state)>.bin."""
    data = struct.pack('<II', udc, code_size) + struct.pack('<%dI' % len(state), *state)
    prefix = 'vs' if stage == 1 else 'ps' if stage == 2 else 'cs'
    return '%s_%016x_%016x.bin' % (prefix, h, xxhash.xxh3_64_intdigest(data))


def parse_recipes(path):
    """(signature, layout sizes dict, list of recipes, end_ok). Recipe: dict(index, kind 1|2, stages=[dict(stage, hash,
    udc, code_size, state, perm, info bytes)], in record order VS, PS / CS)."""
    d = open(path, 'rb').read()
    if d[:8] != b'KytyPR1\n':
        raise ValueError('magic')
    n = struct.unpack_from('<I', d, 8)[0]
    sig = d[12:12 + n].decode('ascii')
    p = 12 + n
    m = re.search(r'(\d+):(\d+):(\d+):(\d+):(\d+):(\d+)$', sig)
    if not m:
        raise ValueError('layout')
    sizes = [int(x) for x in m.groups()]
    lay = dict(vs=sizes[0], ps=sizes[1], cs=sizes[2], rendering=sizes[3], vertex_input=sizes[4], static=sizes[5])
    cnt = struct.unpack_from('<I', d, p)[0]
    p += 4

    def key(p):
        st, h, udc, cs, k = struct.unpack_from('<IQIII', d, p)
        ss = struct.unpack_from('<%dI' % k, d, p + 24)
        return dict(stage=st, hash=h, udc=udc, code_size=cs, state=tuple(ss)), p + 24 + 4 * k

    recipes = []
    for index in range(cnt):
        kind = d[p]
        p += 1
        stages = []
        if kind == 1:
            a, p = key(p)
            a['perm'] = struct.unpack_from('<I', d, p)[0]
            p += 4
            psa = d[p]
            p += 1
            b = None
            if psa:
                b, p = key(p)
                b['perm'] = struct.unpack_from('<I', d, p)[0]
                p += 4
            p += lay['rendering'] + lay['vertex_input'] + lay['static']
            a['info'] = d[p:p + lay['vs']]
            p += lay['vs']
            stages.append(a)
            if psa:
                b['info'] = d[p:p + lay['ps']]
                p += lay['ps']
                stages.append(b)
        elif kind == 2:
            a, p = key(p)
            a['perm'] = struct.unpack_from('<I', d, p)[0]
            p += 4
            a['info'] = d[p:p + lay['cs']]
            p += lay['cs']
            stages.append(a)
        else:
            raise ValueError('kind %d at recipe %d' % (kind, index))
        recipes.append(dict(index=index, kind=kind, stages=stages))
    return sig, lay, recipes, p == len(d)


ELF_MAGIC = bytes([0x7F, 0x45, 0x4C, 0x46, 2, 1, 1])


def eboot_programs(path=EBOOT):
    """{hash int: .shader_text bytes} of the AMDGPU ELFs (e_machine 0xE0) in eboot.bin, and the number of ELF texts."""
    progs = {}
    n_elf = 0
    with open(path, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        e = mm.find(ELF_MAGIC)
        while e != -1:
            if struct.unpack_from('<H', mm, e + 18)[0] == 0xE0:
                try:
                    shoff = struct.unpack_from('<Q', mm, e + 0x28)[0]
                    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', mm, e + 0x3A)
                    secs = []
                    for k in range(shnum):
                        b = e + shoff + k * shentsize
                        name, typ, flags, addr, off, size = struct.unpack_from('<IIQQQQ', mm, b)
                        secs.append((name, off, size))
                    stroff = e + secs[shstrndx][1]
                    for name, off, size in secs:
                        end = mm.find(bytes([0]), stroff + name)
                        if mm[stroff + name:end] in (b'.text', b'.shader_text'):
                            code = bytes(mm[e + off:e + off + size])
                            n_elf += 1
                            h = xxhash.xxh3_64_intdigest(code)
                            if h not in progs:
                                progs[h] = code
                except (struct.error, IndexError):
                    pass
            e = mm.find(ELF_MAGIC, e + 1)
        mm.close()
    return progs, n_elf


def can_fit(start, size):
    return size != 0 and start <= 32 and size <= 32 - start


def start_for(cursor, size):
    """PushData::StartFor (ShaderIR.h)."""
    return cursor if can_fit(cursor, size) else NO_START


def advance(cursor, start, dd):
    """BindingLayout::AdvancePushData: the cursor moves only when the stage uses push data."""
    return start + dd if start != NO_START else cursor


def knob_names(tree):
    """Every literal KYTY_* name in the signature set and in the two pipeline files of a tree (superset of the knobs
    read once per process by the translator and the cache)."""
    names = set()
    roots = [os.path.join(tree, 'src/graphics/shader')]
    files = [os.path.join(tree, 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'),
             os.path.join(tree, 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp')]
    for root in roots:
        for dp, dn, fn in os.walk(root):
            for x in fn:
                if x.endswith(('.cpp', '.h', '.inc')):
                    files.append(os.path.join(dp, x))
    for path in files:
        text = open(path, 'r', encoding='utf-8', errors='replace').read()
        names.update(re.findall(r'"(KYTY_[A-Z0-9_]+)', text))
    return sorted(names)
