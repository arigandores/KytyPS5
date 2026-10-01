# F4b2 (HPP-347, Red Team): own repeat of the proof of ROADMAP s122 p.262(b)(3), independent of
# dualSrcBlend.h and of the F4a2 scripts. Reads the translation cache file of PS 5514e10f1a60df83
# (read only), extracts the fragment module by walking instructions (not by the size prefix), parses
# the interface (types, decorations, entry point, stores), applies its own rewrite of p.262(b)(1)
# (Output at Location 1 -> Location 0 + OpDecorate Index 1 right after) and compares it word for word
# with the module written by the emulator function (proof_f4a2.exe, file given on the command line).
# Usage: python spv_f4b2.py <cache.bin> <out_dir> [<function_output.spv> ...]
import hashlib
import struct
import sys

MAGIC = 0x07230203
OP = {5: 'OpName', 15: 'OpEntryPoint', 16: 'OpExecutionMode', 19: 'OpTypeVoid', 21: 'OpTypeInt',
      22: 'OpTypeFloat', 23: 'OpTypeVector', 32: 'OpTypePointer', 54: 'OpFunction', 56: 'OpFunctionEnd',
      59: 'OpVariable', 62: 'OpStore', 71: 'OpDecorate', 72: 'OpMemberDecorate', 74: 'OpGroupDecorate',
      75: 'OpGroupMemberDecorate', 73: 'OpDecorationGroup', 332: 'OpDecorateId', 5632: 'OpDecorateString'}
SC = {1: 'Input', 3: 'Output', 2: 'Uniform', 0: 'UniformConstant', 12: 'StorageBuffer', 9: 'PushConstant', 7: 'Function', 6: 'Private'}


def walk(words, start):
    """Instruction walk from a module header at `start`; returns the end (exclusive) after the first
    OpFunctionEnd that is followed by a word that is not a valid instruction header, or by the end."""
    if start + 5 > len(words) or words[start] != MAGIC:
        return None
    i = start + 5
    last_end = None
    while i < len(words):
        cnt = words[i] >> 16
        op = words[i] & 0xffff
        if cnt == 0 or i + cnt > len(words):
            break
        if op == 56:
            last_end = i + cnt
        i += cnt
        if last_end == i:
            # next word: another function or the end of the module
            if i >= len(words):
                break
            nop = words[i] & 0xffff
            if nop != 54:
                break
    return last_end


def insts(m):
    i = 5
    while i < len(m):
        cnt = m[i] >> 16
        yield i, m[i] & 0xffff, m[i:i + cnt]
        i += cnt


def lit_str(ws):
    b = b''.join(struct.pack('<I', w) for w in ws)
    return b.split(b'\0', 1)[0].decode('ascii', 'replace')


def parse(m):
    names, types, var_sc, var_ty, decos, stores, eps, modes, groups = {}, {}, {}, {}, [], {}, [], [], []
    for at, op, ins in insts(m):
        if op == 5:
            names[ins[1]] = lit_str(ins[2:])
        elif op in (19, 21, 22, 23, 32):
            types[ins[1]] = (op, ins[2:])
        elif op == 59:
            var_sc[ins[2]] = ins[3]
            var_ty[ins[2]] = ins[1]
        elif op in (71, 72, 332, 5632):
            decos.append((at, op, list(ins[1:])))
        elif op in (73, 74, 75):
            groups.append((at, op))
        elif op == 62:
            stores[ins[1]] = stores.get(ins[1], 0) + 1
        elif op == 15:
            nm_words = ins[3:]
            name = lit_str(nm_words)
            nlen = (len(name) + 1 + 3) // 4
            eps.append((ins[1], ins[2], name, list(ins[3 + nlen:])))
        elif op == 16:
            modes.append(list(ins[1:]))
    return dict(names=names, types=types, var_sc=var_sc, var_ty=var_ty, decos=decos, stores=stores,
                eps=eps, modes=modes, groups=groups)


def type_str(types, tid):
    if tid not in types:
        return f'%{tid}?'
    op, a = types[tid]
    if op == 32:
        return f'ptr({SC.get(a[0], a[0])},{type_str(types, a[1])})'
    if op == 23:
        return f'vec{a[1]}<{type_str(types, a[0])}>'
    if op == 22:
        return f'f{a[0]}'
    if op == 21:
        return f'{"i" if a[1] else "u"}{a[0]}'
    if op == 19:
        return 'void'
    return f'op{op}'


def outputs(p):
    rows = []
    for v, sc in p['var_sc'].items():
        if sc != 3:
            continue
        d = [(op, a[1:]) for _, op, a in p['decos'] if op == 71 and a[0] == v]
        loc = [x[1][1] for x in d if x[1][0] == 30]
        idx = [x[1][1] for x in d if x[1][0] == 32]
        bi = [x[1][1] for x in d if x[1][0] == 11]
        rows.append((v, p['names'].get(v, ''), type_str(p['types'], p['var_ty'][v]), loc, idx, bi,
                     p['stores'].get(v, 0)))
    return sorted(rows)


def rewrite(m):
    """Own implementation of p.262(b)(1)."""
    p = parse(m)
    if any(op == 71 and a[1] == 32 for _, op, a in p['decos']):
        return 'has_index', None
    if any(op == 72 and a[2] in (30, 32) for _, op, a in p['decos']):
        return 'member_decoration', None
    outs = {}
    for at, op, a in p['decos']:
        if op == 71 and a[1] == 30 and p['var_sc'].get(a[0]) == 3:
            outs.setdefault(a[2], []).append((at, a[0]))
    if any(k >= 2 for k in outs):
        return 'location_above1', None
    if 1 not in outs:
        return 'no_location1', None
    if len(outs[1]) > 1:
        return 'multiple_location1', None
    if 0 not in outs:
        return 'no_location0', None
    at, var = outs[1][0]
    out = list(m[:at]) + [(4 << 16) | 71, var, 30, 0] + [(4 << 16) | 71, var, 32, 1] + list(m[at + 4:])
    return 'patched', out


def wbytes(ws):
    return b''.join(struct.pack('<I', w) for w in ws)


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    raw = open(src, 'rb').read()
    print('file', src.split('/')[-1], 'bytes', len(raw), 'sha256', hashlib.sha256(raw).hexdigest())
    words = list(struct.unpack('<%dI' % (len(raw) // 4), raw[:len(raw) // 4 * 4]))
    starts = [i for i, w in enumerate(words) if w == MAGIC]
    # also unaligned magic occurrences
    unal = [k for k in range(len(raw) - 3) if raw[k:k + 4] == struct.pack('<I', MAGIC) and k % 4 != 0]
    print('magic word offsets', starts, 'unaligned', unal)
    mods = []
    for s in starts:
        e = walk(words, s)
        print('module at word', s, 'byte', s * 4, 'walk end', e, 'words', None if e is None else e - s,
              'size-prefix word', words[s - 1] if s else None)
        if e:
            mods.append(words[s:e])
    assert len(mods) == 1, 'expected one module'
    m = mods[0]
    open(out_dir + '/own_in.spv', 'wb').write(wbytes(m))
    print('own_in.spv words', len(m), 'sha256', hashlib.sha256(wbytes(m)).hexdigest())
    p = parse(m)
    print('header version 0x%08x generator 0x%08x bound %d' % (m[1], m[2], m[3]))
    for model, fid, name, iface in p['eps']:
        print('entry point model', model, '(4=Fragment)', 'name', name, 'interface', ['%%%d %s' % (v, p['names'].get(v, '')) for v in iface])
    print('execution modes', p['modes'])
    print('decoration groups', p['groups'])
    print('outputs (id, name, type, Location, Index, BuiltIn, OpStore count):')
    for r in outputs(p):
        print('  ', r)
    oc, out = rewrite(m)
    print('own rewrite outcome', oc)
    open(out_dir + '/own_out.spv', 'wb').write(wbytes(out))
    print('own_out.spv words', len(out), 'sha256', hashlib.sha256(wbytes(out)).hexdigest())
    q = parse(out)
    print('rewritten outputs:')
    for r in outputs(q):
        print('  ', r)
    # word difference with realignment
    first = next(k for k in range(len(m)) if out[k] != m[k])
    print('first differing word', first, 'in 0x%08x out 0x%08x' % (m[first], out[first]))
    rest = [k for k in range(len(m)) if k != first and (out[k] if k < first else out[k + 4]) != m[k]]
    print('differing words outside the Location literal and the 4 inserted:', rest)
    print('inserted', ['0x%08x' % w for w in out[first + 1:first + 5]])
    # interface unchanged
    print('entry point equal', p['eps'] == q['eps'], 'modes equal', p['modes'] == q['modes'],
          'bound equal', m[3] == out[3], 'stores equal', p['stores'] == q['stores'])
    for f in sys.argv[3:]:
        b = open(f, 'rb').read()
        print('compare', f.split('/')[-1], 'sha256', hashlib.sha256(b).hexdigest(), 'byte-equal to own_out', b == wbytes(out))
    print('ALL OK' if oc == 'patched' and not rest else 'FAIL')


if __name__ == '__main__':
    main()
