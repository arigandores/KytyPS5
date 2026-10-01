# F4a (HPP-335, Emu Engineer): read-only check of ROADMAP s122 p.254(zh)(1) - does PS 5514e10f1a60df83
# (record 1592 of pipelines.bin) write a fragment output decorated Index 1? Reads the SPIR-V modules stored in the
# shader translation cache file(s) _ShaderCache/PPSA21564/ps_<hash>_*.bin (no game, no emulator).
# Usage: python spv_index.py <cache dir> <shader hash hex>
import glob
import hashlib
import os
import struct
import sys

MAGIC = 0x07230203
OP_ENTRY_POINT = 15
OP_EXECUTION_MODE = 16
OP_NAME = 5
OP_VARIABLE = 59
OP_DECORATE = 71
DEC_BUILTIN = 11
DEC_LOCATION = 30
DEC_INDEX = 32
SC_OUTPUT = 3
EXEC_MODEL = {0: 'Vertex', 4: 'Fragment', 5: 'GLCompute'}


def modules(data):
    # SPIR-V words are stored as PodVec<uint32_t> (u32 count + words); find every magic at a 4-aligned offset
    # whose preceding u32 is a plausible word count, then walk instructions within that count.
    out = []
    for off in range(4, len(data) - 20, 4):
        if struct.unpack_from('<I', data, off)[0] != MAGIC:
            continue
        count = struct.unpack_from('<I', data, off - 4)[0]
        if count < 5 or off + 4 * count > len(data):
            continue
        out.append((off, struct.unpack_from('<%dI' % count, data, off)))
    return out


def parse(words):
    pos = 5
    entry = []
    names = {}
    out_vars = set()
    deco = {}
    while pos < len(words):
        w = words[pos]
        op = w & 0xffff
        n = w >> 16
        if n == 0 or pos + n > len(words):
            return None
        ins = words[pos:pos + n]
        if op == OP_ENTRY_POINT:
            entry.append(EXEC_MODEL.get(ins[1], str(ins[1])))
        elif op == OP_NAME:
            raw = b''.join(struct.pack('<I', x) for x in ins[2:])
            names[ins[1]] = raw.split(b'\0')[0].decode('ascii', 'replace')
        elif op == OP_VARIABLE and ins[3] == SC_OUTPUT:
            out_vars.add(ins[2])
        elif op == OP_DECORATE:
            deco.setdefault(ins[1], []).append(tuple(ins[2:]))
        pos += n
    return entry, names, out_vars, deco


def main():
    cache_dir, h = sys.argv[1], sys.argv[2].lower()
    files = sorted(glob.glob(os.path.join(cache_dir, 'ps_%s_*.bin' % h)))
    print('files', len(files))
    total_mod = 0
    total_index = 0
    for f in files:
        data = open(f, 'rb').read()
        sig = data.split(b'\n', 1)[0].decode('ascii', 'replace')
        print('file', os.path.basename(f), 'size', len(data), 'sha256', hashlib.sha256(data).hexdigest(), 'sig', sig)
        for off, words in modules(data):
            p = parse(words)
            if p is None:
                print('  module @%d: unparsable, skipped' % off)
                continue
            total_mod += 1
            entry, names, out_vars, deco = p
            print('  module @%d words %d entry %s outputs %d' % (off, len(words), ','.join(entry), len(out_vars)))
            for v in sorted(out_vars):
                d = deco.get(v, [])
                loc = [x[1] for x in d if x[0] == DEC_LOCATION]
                idx = [x[1] for x in d if x[0] == DEC_INDEX]
                bi = [x[1] for x in d if x[0] == DEC_BUILTIN]
                total_index += len(idx)
                print('    out %%%d %s Location=%s Index=%s BuiltIn=%s' % (v, names.get(v, '?'), loc, idx, bi))
            all_index = sum(1 for v in deco.values() for x in v if x[0] == DEC_INDEX)
            print('    OpDecorate Index in module (any target):', all_index)
    print('SUMMARY modules', total_mod, 'output Index decorations', total_index)


if __name__ == '__main__':
    main()
