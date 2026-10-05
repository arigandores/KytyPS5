"""S17c (HPP-613; ROADMAP s122 item 524 (z) K4, item 531 (d)(8), item 532 (g)(zh)): reader of a translation cache file of the emulator
(shaderTranslationCache.cpp, FORMAT_VERSION 3, KytyPS5 a2fee0d9) - the permutations of one program: for every permutation the bytes of
its specialization (WriteSpecialization), its push-data start (BindingLayout.push_data_start_dword) and XXH3-64 of its SPIR-V.

File = signature line ('KytySC...\\n') + u64 XXH3 of the payload + payload; payload = key echo, plan (WritePlan), u32 count, then per
permutation: specialization, compiled info (WriteCompiledInfo), SPIR-V (u32 count + words).  POD sizes below are the in-memory sizes of
the structs that Writer::PodVec copies (all enums 4 bytes; ShaderIR.h, ResourceMaterialization.h, ResourceSnapshot.h at a2fee0d9);
the self-checks of a parse: the payload checksum, the cursor at the end of the payload, every SPIR-V starts with 0x07230203.
usage: python tc_s17c.py <file or folder> [...]      prints one summary line per folder / file; rc 1 on any unreadable file.
ASCII only."""
import os
import struct
import sys

import xxhash

SZ_MEMORY_INFO = 72      # 15 x 4 + 9 bools -> 69, aligned 72
SZ_BUFFER_RES = 36       # 7 x 4 + 5 bools -> 33, aligned 36
SZ_SAMPLER_RES = 12      # 2 x 4 + 2 bools -> 10, aligned 12
SZ_PAIR = 12             # 3 x 4
SZ_INDIRECT = 20         # 5 x 4
SZ_UNIFORM_FILL = 28     # kind + resource + 3 x 4 + words + value
SZ_SPEC_BUFFER = 12      # 3 x 4
SZ_SPEC_IMAGE = 44       # 8 x 4, 2 bools, pad 2, u32, bool, pad 3
SPIRV_MAGIC = 0x07230203
TYPE_OPAQUE = None       # not needed: a Value is always (u32 type, u64 bits) - 12 bytes


class Bad(Exception):
    pass


class R:
    def __init__(self, data, pos=0):
        self.d = data
        self.p = pos

    def take(self, n):
        if n < 0 or self.p + n > len(self.d):
            raise Bad('short at %d need %d' % (self.p, n))
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def u8(self):
        return self.take(1)[0]

    def u32(self):
        return struct.unpack('<I', self.take(4))[0]

    def u64(self):
        return struct.unpack('<Q', self.take(8))[0]

    def podvec(self, size):
        n = self.u32()
        return n, self.take(n * size)

    def strg(self):
        n = self.u32()
        self.take(n)

    def value(self):
        self.take(12)


def skip_image(r):
    r.take(4 * 9)            # source .. shader_swizzle (9 x u32 / enum)
    r.take(7)                # 7 bools
    r.take(4 * 4)            # depth_compare_op, indirect_root, indirect_mapping_offset, indirect_search_iterations
    r.podvec(4)              # indirect_resources


def skip_shader_info(r):
    r.podvec(SZ_BUFFER_RES)
    for _ in range(r.u32()):
        skip_image(r)
    r.podvec(SZ_SAMPLER_RES)
    r.podvec(SZ_PAIR)
    for _ in range(r.u32()):     # inputs
        r.take(12)
        r.strg()
        r.take(1)
    for _ in range(r.u32()):     # outputs
        r.take(12)
        r.strg()
    r.take(32)                   # vertex_fetch_components
    r.take(8)                    # two i32
    r.take(2)                    # two bools


def skip_plan(r):
    r.take(4 + 8 + 4 + 4)
    for _ in range(r.u32()):     # value_storage
        r.take(4 + 8)
        n = r.u32()
        if n > 4096:
            raise Bad('num_args %d' % n)
        r.take(12 * n)
    r.podvec(SZ_MEMORY_INFO)
    for _ in range(r.u32()):     # descriptor_sources
        r.take(4)
        r.take(12 * 8)
        if r.u8():
            r.take(SZ_INDIRECT)
    r.podvec(4)                  # materialization_sources
    for _ in range(r.u32()):     # srt_reads
        r.value()
        r.take(4 + 1)
    r.podvec(1)                  # clean_flat_slots
    r.take(3)                    # three bools
    for _ in range(r.u32()):     # control_flow
        r.value()
        r.podvec(4)
        r.podvec(4)
    r.take(SZ_UNIFORM_FILL)
    r.take(12 * 4)               # uniform_fill.values
    skip_shader_info(r)


def parse_bytes(data):
    """-> dict(signature, stage, hash, perms=[dict(spec=<bytes>, start=<int>, spirv_xxh3=<int>, words=<int>)])."""
    nl = data.find(b'\n')
    if nl < 0 or not data.startswith(b'KytySC'):
        raise Bad('signature')
    sig = data[:nl].decode('ascii', 'replace')
    pos = nl + 1
    if len(data) < pos + 8:
        raise Bad('short header')
    stored = struct.unpack_from('<Q', data, pos)[0]
    pos += 8
    if xxhash.xxh3_64_intdigest(data[pos:]) != stored:
        raise Bad('checksum')
    r = R(data, pos)
    stage = r.u32()
    phash = r.u64()
    r.take(8)                    # user_data_count, code_size
    r.podvec(4)                  # static_state
    skip_plan(r)
    n = r.u32()
    perms = []
    for _ in range(n):
        s0 = r.p
        r.podvec(SZ_SPEC_BUFFER)
        r.podvec(SZ_SPEC_IMAGE)
        spec = data[s0:r.p]
        r.take(4 + 8 + 4 * 5)    # compiled info head
        skip_shader_info(r)
        start = r.u32()          # BindingLayout.push_data_start_dword
        r.take(8)                # memory_offset_dword, memory_offset_count
        r.podvec(4)              # user_data_registers
        for _ in range(r.u32()):
            r.take(4)
            r.podvec(4)
        nw, words = r.podvec(4)
        if nw == 0 or struct.unpack_from('<I', words, 0)[0] != SPIRV_MAGIC:
            raise Bad('spirv magic')
        perms.append(dict(spec=spec, start=start, spirv_xxh3=xxhash.xxh3_64_intdigest(words), words=nw))
    if r.p != len(data):
        raise Bad('trailing %d' % (len(data) - r.p))
    return dict(signature=sig, stage=stage, hash=phash, perms=perms)


def parse_file(path):
    with open(path, 'rb') as f:
        return parse_bytes(f.read())


def cache_files(folder):
    """The translation cache files of a variant folder: <vs|ps|cs>_<16 hex>_<16 hex>.bin, sorted."""
    out = []
    if not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        if name[:3] in ('vs_', 'ps_', 'cs_') and name.endswith('.bin') and len(name) == 3 + 16 + 1 + 16 + 4:
            out.append(name)
    return out


def read_folder(folder):
    """-> (files {name: parsed}, bad [(name, reason)])."""
    files, bad = {}, []
    for name in cache_files(folder):
        try:
            files[name] = parse_file(os.path.join(folder, name))
        except (Bad, OSError, struct.error) as e:
            bad.append((name, str(e)))
    return files, bad


def main(argv):
    rc = 0
    for p in argv:
        if os.path.isdir(p):
            files, bad = read_folder(p)
            perms = sum(len(f['perms']) for f in files.values())
            sigs = sorted(set(f['signature'] for f in files.values()))
            print('folder %s files %d perms %d bad %d signatures %d' % (p, len(files), perms, len(bad), len(sigs)))
            for s in sigs:
                print('  signature %s files %d' % (s, sum(1 for f in files.values() if f['signature'] == s)))
            for name, why in bad[:10]:
                print('  BAD %s %s' % (name, why))
            rc = rc or (1 if bad else 0)
        else:
            try:
                f = parse_file(p)
                print('file %s perms %d signature %s' % (p, len(f['perms']), f['signature']))
            except (Bad, OSError, struct.error) as e:
                print('BAD %s %s' % (p, e))
                rc = 1
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
