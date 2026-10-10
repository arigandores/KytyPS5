"""F36a (HPP-758, ROADMAP s122 item 687(e)(0)(i)): structural finder of the form-A select sites in a SPIR-V module, validated against
the F23a/F23f census (sites_f23f.json, 17 S12 modules, 52 sites) and then applied to the FS11 translation of be4c35a2031fd3f4.

Rule (stated before use; the finder is accepted only if it gives exactly the census sids on all 17 S12 modules):
  site = OpSelect %r with result type OpTypeInt 32 0 whose operand 'new' reaches an OpImageSample* / OpImageGather* /
  OpImageSparse* result through OpCompositeExtract / OpCompositeConstruct (the indexed member) / OpBitcast / OpCopyObject only,
  and whose operand 'old' is defined by OpSelect, OpPhi or OpBitcast.
Per site printed: sid, cid, nid, oid, opcode of cond / old, the sampling instruction of 'new' (opcode, image operands), whether the
sample is in the same block as the select, the stage / execution model.
Usage: python sites_f36a.py validate | python sites_f36a.py show <module.spv> ...  ASCII only."""
import json
import struct
import sys

NL = chr(10)
OPN = {169: 'OpSelect', 245: 'OpPhi', 124: 'OpBitcast', 81: 'OpCompositeExtract', 80: 'OpCompositeConstruct', 83: 'OpCopyObject',
       87: 'OpImageSampleImplicitLod', 88: 'OpImageSampleExplicitLod', 89: 'OpImageSampleDrefImplicitLod',
       90: 'OpImageSampleDrefExplicitLod', 91: 'OpImageSampleProjImplicitLod', 92: 'OpImageSampleProjExplicitLod',
       93: 'OpImageSampleProjDrefImplicitLod', 94: 'OpImageSampleProjDrefExplicitLod', 95: 'OpImageFetch', 96: 'OpImageGather',
       97: 'OpImageDrefGather', 98: 'OpImageRead', 168: 'OpLogicalNot', 171: 'OpINotEqual', 167: 'OpLogicalAnd',
       172: 'OpUGreaterThan', 179: 'OpSLessThanEqual', 170: 'OpIEqual', 166: 'OpLogicalOr', 248: 'OpLabel'}
SAMPLE = set(range(87, 98)) | set(range(305, 316))
IMOPS = [(1, 'Bias'), (2, 'Lod'), (4, 'Grad'), (8, 'ConstOffset'), (16, 'Offset'), (32, 'ConstOffsets'), (64, 'Sample'),
         (128, 'MinLod')]


def words(b):
    return list(struct.unpack('<%dI' % (len(b) // 4), b))


def parse(b):
    w = words(b)
    defs, uint_t, blk, model = {}, set(), {}, None
    cur = None
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        x = w[i:i + n]
        if op == 21 and x[2] == 32 and x[3] == 0:
            uint_t.add(x[1])
        if op == 15:
            model = x[1]
        if op == 248:
            cur = x[1]
        # result-producing instructions with (type, result) layout used here
        if op in OPN and op not in (248, 15):
            if n >= 3:
                defs[x[2]] = (op, x)
                blk[x[2]] = cur
        elif n >= 3 and op not in (71, 72, 5, 6, 15, 16, 17, 11, 14):
            defs.setdefault(x[2], (op, x))
            blk.setdefault(x[2], cur)
        i += n
    return defs, uint_t, blk, model


def trace_new(defs, nid, depth=0):
    """returns (sample result id, opcode) or None; follows only extract / construct member / bitcast / copy"""
    if depth > 12 or nid not in defs:
        return None
    op, x = defs[nid]
    if op in SAMPLE:
        return nid, op
    if op in (124, 83):
        return trace_new(defs, x[3], depth + 1)
    if op == 81:
        comp, idx = x[3], x[4:]
        if comp in defs and defs[comp][0] == 80 and len(idx) >= 1:
            cx = defs[comp][1]
            mem = cx[3:]
            if idx[0] < len(mem):
                return trace_new(defs, mem[idx[0]], depth + 1)
            return None
        return trace_new(defs, comp, depth + 1)
    return None


def sites(b):
    defs, uint_t, blk, model = parse(b)
    out = []
    for rid, (op, x) in sorted(defs.items()):
        if op != 169 or x[1] not in uint_t:
            continue
        c, nw, old = x[3], x[4], x[5]
        t = trace_new(defs, nw)
        if t is None or old not in defs or defs[old][0] not in (169, 245, 124):
            continue
        sx = defs[t[0]][1]
        # image operands: OpImageSample*: type res sampledimage coord [mask ops]
        mask = sx[5] if len(sx) > 5 and t[1] in (87, 88, 91, 92, 95, 96) else (sx[6] if len(sx) > 6 else 0)
        ops = [nm for bit, nm in IMOPS if mask & bit]
        out.append({'sid': rid, 'cid': c, 'nid': nw, 'oid': old, 'cond_op': OPN.get(defs[c][0], str(defs[c][0])) if c in defs else '?',
                    'old_op': OPN.get(defs[old][0], str(defs[old][0])), 'sample_id': t[0], 'sample_op': OPN.get(t[1], str(t[1])),
                    'image_operands': ops, 'same_block_as_sample': blk.get(rid) == blk.get(t[0]), 'block': blk.get(rid)})
    return model, out


def main():
    if sys.argv[1] == 'validate':
        d = json.load(open('C:/kyty/f287/f23f/sites_f23f.json'))
        ok = True
        tot = 0
        for h, v in sorted(d.items()):
            b = open('C:/kyty/f287/f23f/s12spv/' + v['spv'], 'rb').read()
            _, s = sites(b)
            got = sorted(x['sid'] for x in s)
            exp = sorted(x['sid'] for x in v['sites'])
            same = got == exp
            ok &= same
            tot += len(got)
            print(h, v['stage'], 'census', len(exp), 'finder', len(got), 'EQUAL' if same else 'DIFF %s vs %s' % (got, exp))
        print('total finder sites', tot)
        print('ALL OK' if ok else 'FAIL')
        return 0 if ok else 1
    for p in sys.argv[2:]:
        model, s = sites(open(p, 'rb').read())
        print('==', p, 'model', model, 'sites', len(s))
        for x in s:
            print(json.dumps(x, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
