"""F14c (HPP-489, ROADMAP s122 item 400(v)(1)): compare-sample sites of one SPIR-V module and the bindings they read.

The site rule is the one of f14a_corpus.py (F14a, KytyPS5 a015bb9f) unchanged:
  native = OpImageSampleDref{Implicit,Explicit}Lod (89, 90), OpImageDrefGather (97);
  manual = the ManualDepthCompare/CompareDepth pattern of spirvEmitterImage.cpp: a non-Dref OpImageSample{Implicit,Explicit}Lod
  (87, 88) or OpImageGather (96) result R, OpCompositeExtract X = R[k], a float compare C(ref, X) with X as the SECOND operand,
  OpSelect float C 1.0 0.0 (one site per OpSelect).
New here: for every site the sampled-image operand is followed back - OpSampledImage(image, sampler), each through OpLoad and
  an optional OpAccessChain to its OpVariable - and named by (DescriptorSet, Binding, array index); the index is the constant
  value or 'dyn'.  The image type of the variable gives Dim and the Depth flag.
Pure python (struct), no device; ASCII only.  Used by rd_cmp_f14c.py inside qrenderdoc and by test_spv_sites_f14c.py.
"""
import struct

OP_SAMPLE = {87: 'ImplicitLod', 88: 'ExplicitLod', 96: 'Gather'}
OP_DREF = {89: 'DrefImplicitLod', 90: 'DrefExplicitLod', 97: 'DrefGather'}
FCMP_NAME = {180: 'FOrdEqual', 181: 'FUnordEqual', 182: 'FOrdNotEqual', 183: 'FUnordNotEqual', 184: 'FOrdLessThan',
             185: 'FUnordLessThan', 186: 'FOrdGreaterThan', 187: 'FUnordGreaterThan', 188: 'FOrdLessThanEqual',
             189: 'FUnordLessThanEqual', 190: 'FOrdGreaterThanEqual', 191: 'FUnordGreaterThanEqual'}
DIM = {0: '1D', 1: '2D', 2: '3D', 3: 'Cube', 4: 'Rect', 5: 'Buffer', 6: 'SubpassData'}


def parse(data):
    n = len(data) // 4
    words = struct.unpack('<%dI' % n, data[:4 * n])
    if not words or words[0] != 0x07230203:
        return None
    insts = []
    i = 5
    while i < len(words):
        wc, op = words[i] >> 16, words[i] & 0xffff
        if wc == 0:
            return None
        insts.append((op, words[i + 1:i + wc]))
        i += wc
    return insts


def sites(data):
    """returns (sites, error).  Each site: dict kind ('manual'|'native'), op, cmp, img, smp, img_dim, img_depth, img_arrayed."""
    insts = parse(data)
    if insts is None:
        return [], 'not SPIR-V'
    float_types, int_types = set(), set()
    for op, w in insts:
        if op == 22 and len(w) >= 2 and w[1] == 32:
            float_types.add(w[0])
        elif op == 21 and len(w) >= 2:
            int_types.add(w[0])
    fconst, iconst = {}, {}
    defs = {}
    deco = {}
    ptr_pointee = {}
    var_type = {}
    image_type = {}
    arr_elem = {}
    for op, w in insts:
        if op == 43 and len(w) >= 3:
            if w[0] in float_types:
                fconst[w[1]] = w[2]
            elif w[0] in int_types:
                iconst[w[1]] = w[2]
        elif op == 71 and len(w) >= 3:  # OpDecorate target deco value
            if w[1] in (33, 34):  # Binding, DescriptorSet
                deco.setdefault(w[0], {})[w[1]] = w[2]
        elif op == 32 and len(w) >= 3:  # OpTypePointer res storage type
            ptr_pointee[w[0]] = w[2]
        elif op == 59 and len(w) >= 2:  # OpVariable type res storage
            var_type[w[1]] = w[0]
        elif op == 25 and len(w) >= 8:  # OpTypeImage res sampledType dim depth arrayed ms sampled format
            image_type[w[0]] = (DIM.get(w[2], str(w[2])), w[3], w[4])
        elif op in (28, 29) and len(w) >= 2:  # OpTypeArray / OpTypeRuntimeArray res elem
            arr_elem[w[0]] = w[1]
    # result id -> (op, words) for instructions with a result: type res ...
    RESULT_AT1 = {61, 65, 66, 86, 81, 87, 88, 89, 90, 96, 97, 169, 83, 100} | set(FCMP_NAME)
    for op, w in insts:
        if op in RESULT_AT1 and len(w) >= 2:
            defs[w[1]] = (op, w)

    def follow(vid):
        """id of a loaded image or sampler -> (set, binding, index, var id)"""
        seen = 0
        while seen < 16:
            seen += 1
            d = defs.get(vid)
            if d is None:
                if vid in var_type:
                    dd = deco.get(vid, {})
                    return (dd.get(34), dd.get(33), 0, vid)
                return (None, None, None, vid)
            op, w = d
            if op == 61:  # OpLoad type res ptr
                vid = w[2]
            elif op == 83:  # OpCopyObject
                vid = w[2]
            elif op in (65, 66):  # OpAccessChain / InBounds type res base idx...
                base = w[2]
                idx = w[3] if len(w) > 3 else None
                iv = iconst.get(idx, 'dyn') if idx is not None else 0
                if base in var_type:
                    dd = deco.get(base, {})
                    return (dd.get(34), dd.get(33), iv, base)
                return (None, None, iv, base)
            else:
                return (None, None, None, vid)
        return (None, None, None, vid)

    def img_info(var):
        t = var_type.get(var)
        t = ptr_pointee.get(t, t)
        t = arr_elem.get(t, t)
        return image_type.get(t, ('?', None, None))

    def resolve(si):
        d = defs.get(si)
        if d is None or d[0] != 86:
            return None, None, ('?', None, None)
        _, w = d
        im = follow(w[2])
        sm = follow(w[3])
        return im, sm, img_info(im[3])

    out = []
    extract = {}
    fcmp = {}
    sample_inst = {}
    sel = []
    for op, w in insts:
        if op in OP_DREF and len(w) >= 3:
            im, sm, ti = resolve(w[2])
            out.append({'kind': 'native', 'op': OP_DREF[op], 'cmp': '-', 'img': im, 'smp': sm,
                        'img_dim': ti[0], 'img_depth': ti[1], 'img_arrayed': ti[2]})
        elif op in OP_SAMPLE and len(w) >= 3:
            sample_inst[w[1]] = (op, w)
        elif op == 81 and len(w) >= 3:
            extract[w[1]] = w[2]
        elif op in FCMP_NAME and len(w) >= 4:
            fcmp[w[1]] = (w[2], w[3], op)
        elif op == 169 and len(w) >= 5:
            sel.append(w)
    for w in sel:
        if w[0] not in float_types or w[2] not in fcmp:
            continue
        if fconst.get(w[3]) != 0x3f800000 or fconst.get(w[4]) != 0:
            continue
        x = fcmp[w[2]][1]
        if x in extract and extract[x] in sample_inst:
            sop, sw = sample_inst[extract[x]]
            im, sm, ti = resolve(sw[2])
            out.append({'kind': 'manual', 'op': OP_SAMPLE[sop], 'cmp': FCMP_NAME[fcmp[w[2]][2]], 'img': im, 'smp': sm,
                        'img_dim': ti[0], 'img_depth': ti[1], 'img_arrayed': ti[2]})
    return out, None


def key(s):
    """a printable key of the bindings of one site: kind/op/cmp img=set:binding[idx] smp=set:binding[idx]"""
    def b(t):
        if t is None:
            return '?'
        return '%s:%s[%s]' % (t[0], t[1], t[2])
    return '%s/%s/%s img=%s smp=%s' % (s['kind'], s['op'], s['cmp'], b(s['img']), b(s['smp']))
