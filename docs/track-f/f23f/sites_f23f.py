"""F23f (HPP-592, ROADMAP s122 item 498(g)(2)(v), (3)): form-A sites of the 17 programs in the S12 SPIR-V.
Reads sel_f23f.jsonl (F23a census before CompileProgram), sel_f23f_post.jsonl (the same census on the compiled IR, with the
SPIR-V ids of the select and its condition / new / old), sel_f23f.status.jsonl (plain = S12). Checks:
  (1) the form-A items before and after CompileProgram are the same multiset of (level, depth, new, old);
  (2) every post item id is an OpSelect of the S12 module whose operands are exactly (cid, nid, oid);
  (3) the condition id chain (type bool) is printed (opcode of the condition definition) - the input of the references.
Output: sites_f23f.out.txt, sites_f23f.json ({program: {spv, sites: [{sid, cid, nid, oid, type, depth, lvl, ...}]}})."""
import collections
import json
import struct
import sys

D = 'C:/kyty/f287/f23f/'
NL = chr(10)
OPN = {169: 'OpSelect', 170: 'OpIEqual', 171: 'OpINotEqual', 164: 'OpLogicalEqual', 165: 'OpLogicalNotEqual',
       166: 'OpLogicalOr', 167: 'OpLogicalAnd', 168: 'OpLogicalNot', 245: 'OpPhi', 61: 'OpLoad', 124: 'OpBitcast',
       176: 'OpUGreaterThan', 177: 'OpSGreaterThan', 178: 'OpUGreaterThanEqual', 180: 'OpULessThan', 182: 'OpULessThanEqual',
       184: 'OpFOrdEqual', 186: 'OpFOrdNotEqual', 188: 'OpFOrdLessThan', 190: 'OpFOrdGreaterThan', 192: 'OpFOrdLessThanEqual',
       194: 'OpFOrdGreaterThanEqual', 179: 'OpSGreaterThanEqual', 181: 'OpSLessThan', 183: 'OpSLessThanEqual',
       185: 'OpFUnordEqual', 187: 'OpFUnordNotEqual', 189: 'OpFUnordLessThan', 191: 'OpFUnordGreaterThan',
       41: 'OpConstantTrue', 42: 'OpConstantFalse', 81: 'OpCompositeExtract', 339: 'OpGroupNonUniformElect'}


def parse(path):
    data = open(path, 'rb').read()
    w = struct.unpack('<%dI' % (len(data) // 4), data)
    i = 5
    defs = {}
    types = {}
    while i < len(w):
        n = w[i] >> 16
        op = w[i] & 0xffff
        ins = w[i:i + n]
        if op == 20:
            types[ins[1]] = 'bool'
        elif op == 21:
            types[ins[1]] = 'int%d%s' % (ins[2], 's' if ins[3] else 'u')
        elif op == 22:
            types[ins[1]] = 'float%d' % ins[2]
        # value instructions with <type, result>
        if n >= 3 and op not in (71, 72, 15, 16, 17, 5, 6, 14, 3, 11, 10, 248, 249, 250, 247, 246, 62, 63, 252, 253, 254, 255, 4416):
            if op >= 41 and op != 54 or op in (43, 44):
                defs.setdefault(ins[2], (op, ins, i))
        if op == 54:
            defs.setdefault(ins[2], (op, ins, i))
        i += n
    return defs, types


def key(it):
    return (it['lvl'], it['depth'], it['new'], it['old'])


def main():
    pre = {}
    for line in open(D + 'sel_f23f.jsonl', encoding='utf-8'):
        d = json.loads(line)
        pre[d['hash']] = d
    post = {}
    for line in open(D + 'sel_f23f_post.jsonl', encoding='utf-8'):
        d = json.loads(line)
        post[d['hash']] = d
    m = json.load(open(D + 'map_f23f.json'))
    out = []
    res = {}
    ok = True
    for h in sorted(pre, key=lambda x: (m[x]['stage'], x)):
        a = [it for it in pre[h]['items'] if it['A']]
        b = [it for it in post[h]['items'] if it['A']]
        same = collections.Counter(key(x) for x in a) == collections.Counter(key(x) for x in b)
        ok &= same
        s12 = list(m[h]['s12'].values())[0]
        defs, types = parse(D + 's12spv/' + s12['file'])
        sites = []
        line = '%s %s formA pre %d post %d same %s spv %s' % (m[h]['stage'], h, len(a), len(b), same, s12['sha'][:16])
        out.append(line)
        for it in b:
            d = defs.get(it['sid'])
            good = d is not None and d[0] == 169 and list(d[1][3:6]) == [it['cid'], it['nid'], it['oid']]
            ok &= good
            tname = types.get(d[1][1], '?') if d else '?'
            cd = defs.get(it['cid'])
            cop = OPN.get(cd[0], str(cd[0])) if cd else 'none'
            sites.append(dict(sid=it['sid'], cid=it['cid'], nid=it['nid'], oid=it['oid'], type=tname, lvl=it['lvl'],
                              depth=it['depth'], new=it['new'], old=it['old'], B=it['B'], cond_op=cop, ok=good))
            out.append('  site %%%d = OpSelect %s %%%d %%%d %%%d  %s  depth %d new %s old %s B %d cond_def %s' % (
                it['sid'], tname, it['cid'], it['nid'], it['oid'], 'OK' if good else 'MISMATCH', it['depth'], it['new'],
                it['old'], it['B'], cop))
        res[h] = dict(stage=m[h]['stage'], spv=s12['file'], spv_sha=s12['sha'], sites=sites)
    out.append('ALL OK' if ok else 'FAILED')
    open(D + 'sites_f23f.out.txt', 'w', encoding='utf-8', newline=NL).write(NL.join(out) + NL)
    json.dump(res, open(D + 'sites_f23f.json', 'w'), indent=1, sort_keys=True)
    print(NL.join(out))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
