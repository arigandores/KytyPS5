# F36b (HPP-759, Red Team; ROADMAP s122 item 687(z)): own parse of the kind of the three form-A sites of be4c35a2031fd3f4
# in the FS11 translation and in the captured S12 module - independent of align_f36a.py / kind_f36a.py.
# For every OpSelect %uint whose condition is OpINotEqual(((x >> (load(lane) & 31)) & 1), 0) (ballot bit of the own lane):
# execution model and modes; the true operand traced back through CompositeExtract / CompositeConstruct / Bitcast to an image
# instruction (opcode, image operands mask), its image and sampler variables (DescriptorSet, Binding) and the component;
# forward data reachability of the site to Output variables (through Function / Private variable store -> load).
# Then: the sites named by F36a (FS11 5011, 5013, 5037; S12 5038, 5040, 5064) are matched by (image binding, sampler binding,
# component, false-operand shape) between S12 and FS11.  Usage: python kind_f36b.py <fs11.spv> <s12.spv>.  ASCII only.
import struct, sys, json

NAMES = {57: 'OpFunctionCall', 87: 'OpImageSampleImplicitLod', 88: 'OpImageSampleExplicitLod', 89: 'OpImageSampleDrefImplicitLod',
         90: 'OpImageSampleDrefExplicitLod', 95: 'OpImageFetch', 96: 'OpImageGather', 98: 'OpImageRead'}


def parse(path):
    b = open(path, 'rb').read()
    w = struct.unpack('<%dI' % (len(b) // 4), b)
    ins = []
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        ins.append((op, list(w[i + 1:i + n])))
        i += n
    return ins


HAS_TYPE = {65, 66, 61, 81, 82, 79, 80, 124, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144,
            145, 146, 147, 148, 149, 150, 151, 152, 156, 157, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179,
            180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
            206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
            230, 231, 232, 233, 234, 12, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107,
            100, 59, 245, 57, 43, 44, 41, 42, 46, 50, 51, 52, 76, 77, 78, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123,
            126, 127, 154, 155, 160, 161, 162, 163, 164, 165, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346,
            347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 4421, 4422, 4423,
            4424, 4425, 4426, 4427, 4428, 4429, 4430, 4431, 4432, 4433, 4434, 4435, 4436, 4437, 4438, 4439, 4440, 4441, 4442, 4443,
            4444, 4445, 4446, 4447, 4448, 4449, 4450, 4451, 4452, 4453, 4454}


def analyse(path):
    ins = parse(path)
    defs, deco, model, modes = {}, {}, None, []
    for op, a in ins:
        if op == 15:
            model = a[0]
        elif op == 16:
            modes.append(a[1])
        elif op == 71:
            deco.setdefault(a[0], {})[a[1]] = a[2:]
        if op in HAS_TYPE and len(a) >= 2:
            defs[a[1]] = (op, a)
        elif op == 59:
            defs[a[1]] = (op, a)
    out_vars = set(a[1] for op, a in ins if op == 59 and a[2] == 3)

    def d(i):
        return defs.get(i, (None, None))

    def var_of_load(i, depth=0):
        op, a = d(i)
        if op == 61:            # OpLoad
            return var_of_load(a[2], depth + 1)
        if op == 65:            # OpAccessChain
            return var_of_load(a[2], depth + 1)
        if op == 59:
            return i
        return None

    def binding(v):
        dd = deco.get(v, {})
        return (dd.get(34, [None])[0], dd.get(33, [None])[0])  # DescriptorSet, Binding

    def lane_bit(c):
        # c = OpINotEqual(x, zero); x = BitwiseAnd(ShiftRightLogical(y, BitwiseAnd(Load(lane), 31)), 1)
        op, a = d(c)
        if op != 171:
            return None
        op2, a2 = d(a[2])
        if op2 != 199:
            return None
        op3, a3 = d(a2[2])
        if op3 != 194:
            return None
        op4, a4 = d(a3[3])
        if op4 != 199:
            return None
        op5, a5 = d(a4[2])
        lane_var = var_of_load(a4[2]) if op5 == 61 else None
        bi = deco.get(lane_var, {}).get(11, [None])[0]   # BuiltIn
        return {'ballot_word': a3[2], 'lane_var': lane_var, 'lane_builtin': bi}

    def trace(i, comp=None, depth=0):
        op, a = d(i)
        if depth > 12 or op is None:
            return {'stop': op}
        if op == 81:            # CompositeExtract
            return trace(a[2], a[3] if comp is None else comp, depth + 1)
        if op == 80:            # CompositeConstruct
            if comp is None:
                return {'stop': 'construct'}
            return trace(a[2 + comp], comp, depth + 1)
        if op == 124:           # Bitcast
            return trace(a[2], comp, depth + 1)
        if op in NAMES:
            si = d(a[2])
            img = smp = None
            if si[0] == 86:     # OpSampledImage
                img, smp = var_of_load(si[1][2]), var_of_load(si[1][3])
            else:
                img = var_of_load(a[2])
            mask = a[4] if len(a) > 4 else 0
            return {'inst': NAMES[op], 'id': i, 'image_operands_mask': mask, 'bias': bool(mask & 1), 'lod': bool(mask & 2),
                    'comp': comp, 'img_binding': binding(img), 'smp_binding': binding(smp) if smp else None}
        return {'stop': op}

    # forward reachability to outputs (Function/Private variables carry data store -> load)
    users = {}
    stores = []
    for op, a in ins:
        if op == 62:
            stores.append((a[0], a[1]))
        elif op in HAS_TYPE and len(a) >= 2:
            for x in a[2:]:
                users.setdefault(x, set()).add(a[1])
    loads_of = {}
    for op, a in ins:
        if op == 61:
            v = var_of_load(a[2])
            loads_of.setdefault(v, set()).add(a[1])
    store_of = {}
    for p, val in stores:
        store_of.setdefault(val, set()).add(var_of_load(p) if d(p)[0] in (59, 65) else None)

    def reach(s):
        seen, st, outs = {s}, [s], set()
        while st:
            x = st.pop()
            for v in store_of.get(x, ()):
                if v in out_vars:
                    outs.add(v)
                elif v is not None:
                    for l in loads_of.get(v, ()):
                        if l not in seen:
                            seen.add(l); st.append(l)
            for u in users.get(x, ()):
                if u not in seen:
                    seen.add(u); st.append(u)
        return sorted(deco.get(o, {}).get(30, [('builtin', deco.get(o, {}).get(11, [None])[0])])[0] if 30 in deco.get(o, {}) else
                      'builtin%s' % deco.get(o, {}).get(11, [None])[0] for o in outs)

    sites = []
    for op, a in ins:
        if op == 169:           # OpSelect
            lb = lane_bit(a[2])
            if lb is None:
                continue
            t = trace(a[3])
            sites.append({'id': a[1], 'cond': a[2], 'true': a[3], 'false': a[4], 'lane': lb, 'new': t,
                          'false_kind': d(a[4])[0]})
    return {'model': model, 'modes': modes, 'sites': sites, 'reach': reach, 'nins': len(ins)}


def main():
    res = {}
    named = {'fs11': [5011, 5013, 5037], 's12': [5038, 5040, 5064]}
    ok = True
    for tag, path in (('fs11', sys.argv[1]), ('s12', sys.argv[2])):
        A = analyse(path)
        print('==', tag, path, 'model', A['model'], '(4 = Fragment)', 'modes', A['modes'], '(12 DepthReplacing, 9 EarlyFragmentTests)')
        sel = [s for s in A['sites'] if s['new'].get('inst')]
        print('  OpSelect %%uint with own-lane ballot-bit condition and an image instruction as true operand: %d' % len(sel))
        rows = []
        for s in A['sites']:
            if s['id'] in named[tag]:
                s['reach_outputs'] = A['reach'](s['id'])
                rows.append(s)
                print('  site %%%d cond %%%d lane builtin %s new %s false-op opcode %s reach Location %s' % (
                    s['id'], s['cond'], s['lane']['lane_builtin'], json.dumps(s['new'], sort_keys=True), s['false_kind'], s['reach_outputs']))
        if len(rows) != 3:
            print('  FAIL named sites found %d of 3' % len(rows)); ok = False
        res[tag] = {'model': A['model'], 'modes': A['modes'], 'named': rows,
                    'all_sites_with_image_new': [(s['id'], s['new'].get('inst'), s['new'].get('comp'), s['new'].get('img_binding'),
                                                  s['new'].get('smp_binding')) for s in sel]}
    # match by (inst, bias, comp, img binding, smp binding)
    key = lambda s: (s['new'].get('inst'), s['new'].get('bias'), s['new'].get('comp'), tuple(s['new'].get('img_binding') or ()),
                     tuple(s['new'].get('smp_binding') or ()))
    for a, b in zip(res['s12']['named'], res['fs11']['named']):
        eq = key(a) == key(b)
        print('match S12 %%%d -> FS11 %%%d: %s  key %s' % (a['id'], b['id'], 'EQUAL' if eq else 'DIFF', key(a)))
        ok &= eq
    for tag in ('fs11', 's12'):
        keys = [key(s) for s in res[tag]['named']]
        uniq = sum(1 for s in res[tag]['all_sites_with_image_new'] if (s[1], None, s[2], tuple(s[3] or ()), tuple(s[4] or ())) in [(k[0], None, k[2], k[3], k[4]) for k in keys])
        print('%s: form-A-like selects with image new sharing a key with the named sites: %d (named 3)' % (tag, uniq))
        for s in res[tag]['named']:
            n = s['new']
            kind_h = A_ok = (res[tag]['model'] == 4 and n.get('inst') == 'OpImageSampleImplicitLod')
            print('  %s %%%d kind H (Fragment + ImplicitLod): %s' % (tag, s['id'], 'yes' if kind_h else 'no'))
            ok &= kind_h
    json.dump(res, open(sys.argv[3] if len(sys.argv) > 3 else 'kind_f36b.json', 'w'), indent=1, sort_keys=True, default=str)
    print('ALL OK' if ok else 'FAIL')


main()
