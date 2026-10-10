# F36b (HPP-759, Red Team; ROADMAP s122 item 687(z)): own replay of be4c35a2031fd3f4 events of one capture - own code, not rd_f36a.py.
# qrenderdoc --python rd_f36b.py ; env RD_CAP capture, RD_EV json list [{eid, exec_no, PSInvocations, SamplesPassed}], RD_OUT json.
# Per event and arm (orig, def, mask, mem, sens, mask_inv, mem_inv, m3, diag, orig2): the arm's replacement, then
#   pre  = SetFrameEvent(pre_eid) (pre_eid = first event of the action's event group - 1; F36a section 0.8), read OUTPUTS and INPUTS,
#   post = SetFrameEvent(eid), read OUTPUTS; for orig and sens also SetFrameEvent(eid - 1) outputs (mutant m1': 'before' of F23f).
# OUTPUTS: colour targets, depth-stencil, PS read-write descriptors (textures all mips/slices, buffers bound range <= 64 MiB).
# INPUTS (own G1 extension): PS and VS read-only descriptors and constant blocks (textures: all mips/slices of the view range,
#   buffers: bound range), each subresource <= 64 MiB (larger - named, not read).
# Arms: def/mask/mem/sens - F36a files (sha checked against arms_f36a.json); mask_inv/mem_inv - patch_inv of F23g (own copy below);
#   m3 - mask with the mask word of the FIRST rewritten site (%5011) := 0 - 0 (the site always takes the old value);
#   diag - refs_f23f.rewrite as F36a (slots at the end of the largest bound 'buffers' read-write range).
# Counters: slot words raw at orig pre/post, def pre/post, diag pre/post (mutants m2 / m2' and the collision check are computed
#   offline from them).  N(x, y) = units that differ (texels by bytes/texel of the subresource, 4-byte words of buffers); -1 = not
#   comparable.  ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, struct, traceback
sys.path.insert(0, 'C:/kyty/f287/f23f')
OUT = os.environ['RD_OUT']
LOGF = open(OUT + '.log', 'a')
NL = chr(10)
T0 = time.time()
BIG = 64 * 1024 * 1024
CAP_SHA = 'ebff0feeb90b9b35c7aecbd6fc542fb6ded352504b70442b9172f533a571cb96'
ARMDIR = 'C:/kyty/f287/f36a/arms/ps_be4c35a2031fd3f4_%s.spv'


def P(*a):
    LOGF.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    LOGF.flush()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rid(r):
    try:
        return int(str(r).split('::')[-1])
    except Exception:
        return -1


def words(b):
    return list(struct.unpack('<%dI' % (len(b) // 4), b))


def nd(a, b, unit):
    if a is None or b is None or len(a) != len(b) or unit <= 0:
        return -1
    if a == b:
        return 0
    n = 0
    for i in range(0, len(a), 1 << 16):
        x, y = a[i:i + 65536], b[i:i + 65536]
        if x != y:
            for j in range(0, len(x), unit):
                if x[j:j + unit] != y[j:j + unit]:
                    n += 1
    return n


def cmpd(x, y, skip=None):
    o = {}
    for k in x:
        if k not in y:
            o[k] = -1
            continue
        a, u = x[k]
        b = y[k][0]
        if skip and k == skip[0]:
            lo, hi = skip[1], skip[2]
            o[k] = -1 if len(a) != len(b) else nd(a[:lo], b[:lo], 4) + nd(a[hi:], b[hi:], 4)
        else:
            o[k] = nd(a, b, u)
    return o


def patch_inv(ref, dflt, kind, only_first=False, zero_bit=False):
    """F23g patch_inv (own copy). mask: OpISub %u %m %c0 %bit (id >= def bound) -> OpISub %u %m %bit %c1 (inverted bit);
    with zero_bit: -> OpISub %u %m %c0 %c0 (mask 0: the site takes the old value). mem: the Volatile-store access chains with
    constant index 0/1 -> swapped. only_first: only the first such instruction in module order."""
    w = words(ref)
    bound_def = words(dflt)[3]
    consts = {}
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        if op == 43 and n == 4:
            consts.setdefault(w[i + 3], []).append(w[i + 2])
        i += n
    c0, c1 = set(consts.get(0, [])), set(consts.get(1, []))
    c1id, c0id = sorted(c1)[0], sorted(c0)[0]
    stores = set()
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        if op == 62 and n == 4 and w[i + 3] == 1:
            stores.add(w[i + 1])
        i += n
    k = 0
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        if not (only_first and k >= 1):
            if kind == 'mask' and op == 130 and n == 5 and w[i + 2] >= bound_def and w[i + 3] in c0:
                if zero_bit:
                    w[i + 4] = c0id
                else:
                    bit = w[i + 4]
                    w[i + 3], w[i + 4] = bit, c1id
                k += 1
            elif kind == 'mem' and op == 65 and n == 5 and w[i + 2] >= bound_def and w[i + 2] in stores and (w[i + 4] in c0 or w[i + 4] in c1):
                w[i + 4] = c1id if w[i + 4] in c0 else c0id
                k += 1
        i += n
    return struct.pack('<%dI' % len(w), *w), k


def main():
    import renderdoc as rd
    import refs_f23f as R
    evs = json.loads(os.environ['RD_EV'])
    aj = json.load(open('C:/kyty/f287/f36a/arms_f36a.json'))
    blobs = {}
    for a in ('def', 'mask', 'mem', 'sens'):
        blobs[a] = open(ARMDIR % a, 'rb').read()
        assert sha(blobs[a]) == aj['files'][a]['sha'], ('arm sha', a)
    blobs['mask_inv'], k1 = patch_inv(blobs['mask'], blobs['def'], 'mask')
    blobs['mem_inv'], k2 = patch_inv(blobs['mem'], blobs['def'], 'mem')
    blobs['m3'], k3 = patch_inv(blobs['mask'], blobs['def'], 'mask', only_first=True, zero_bit=True)
    res = {'cap': os.environ['RD_CAP'], 'patched': {'mask_inv': k1, 'mem_inv': k2, 'm3': k3},
           'arm_sha': {a: sha(b) for a, b in blobs.items()}, 'events': []}
    for a in ('mask_inv', 'mem_inv', 'm3'):
        open('C:/kyty/f287/f36b/arms_%s.spv' % a, 'wb').write(blobs[a])
    P('patched', res['patched'])
    sites = [tuple(s) for s in aj['sites']]
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    grp = {}

    def walk(al):
        for a in al:
            evl = [e.eventId for e in a.events]
            for e in evl + [a.eventId]:
                grp[e] = (min(evl + [a.eventId]), evl)
            walk(a.children)
    walk(ctrl.GetRootActions())
    tex = {rid(t.resourceId): t for t in ctrl.GetTextures()}
    buf = {rid(b.resourceId): b for b in ctrl.GetBuffers()}
    PS, VS = rd.ShaderStage.Pixel, rd.ShaderStage.Vertex
    for ev in evs:
        eid = ev['eid']
        r = dict(ev)
        first, evl = grp[eid]
        pre_eid = first - 1
        r['pre_eid'], r['group'] = pre_eid, evl
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(PS)
        r['bound_is_cap'] = sha(bytes(refl.rawBytes)) == CAP_SHA
        shid = ps.GetShader(PS)
        entry = refl.entryPoint
        rwn = [x.name for x in refl.readWriteResources]
        outs, cands, large = [], [], []
        for k, d in enumerate(ps.GetOutputTargets()):
            if rid(d.resource) > 0:
                outs.append(('rt%d' % k, 'tex', rid(d.resource), int(d.firstMip), int(d.firstSlice), 1, 1))
        dt = ps.GetDepthTarget()
        if rid(dt.resource) > 0:
            outs.append(('depth', 'tex', rid(dt.resource), int(dt.firstMip), int(dt.firstSlice), 1, 1))
        for u in ps.GetReadWriteResources(PS):
            d = u.descriptor
            n = rid(d.resource)
            if n <= 0:
                continue
            nm = rwn[u.access.index] if 0 <= u.access.index < len(rwn) else '?'
            if n in tex:
                t = tex[n]
                outs.append(('rw_%s_%d_t%d' % (nm, u.access.arrayElement, n), 'tex', n, 0, 0, max(1, t.mips), max(1, t.arraysize)))
            elif n in buf:
                off, size = int(d.byteOffset), int(d.byteSize)
                if size == 0 or size > buf[n].length - off:
                    size = buf[n].length - off
                if size > BIG:
                    large.append(('out', nm, n, size)); continue
                key = 'rw_%s_%d_b%d_o%d' % (nm, u.access.arrayElement, n, off)
                outs.append((key, 'buf', n, off, size, 0, 0))
                cands.append((nm, u.access.arrayElement, n, off, size, key))
        ins = []
        for stg, sn in ((PS, 'ps'), (VS, 'vs')):
            for u in list(ps.GetReadOnlyResources(stg)) + list(ps.GetConstantBlocks(stg)):
                d = u.descriptor
                n = rid(d.resource)
                if n <= 0:
                    continue
                if n in tex:
                    t = tex[n]
                    fm = int(getattr(d, 'firstMip', 0)); nmp = int(getattr(d, 'numMips', 0)) or (max(1, t.mips) - fm)
                    fs = int(getattr(d, 'firstSlice', 0)); nsl = int(getattr(d, 'numSlices', 0)) or (max(1, t.arraysize) - fs)
                    ins.append(('in_%s_t%d_m%d_%d_s%d_%d' % (sn, n, fm, nmp, fs, nsl), 'tex', n, fm, fs, nmp, nsl))
                elif n in buf:
                    off, size = int(d.byteOffset), int(d.byteSize)
                    if size == 0 or size > buf[n].length - off:
                        size = buf[n].length - off
                    if size > BIG:
                        large.append(('in', sn, n, size)); continue
                    ins.append(('in_%s_b%d_o%d_%d' % (sn, n, off, size), 'buf', n, off, size, 0, 0))
        seen = set()
        ins = [x for x in ins if not (x[1:] in seen or seen.add(x[1:]))]
        r['outputs'] = [o[0] for o in outs]
        r['inputs'] = [o[0] for o in ins]
        r['large'] = [list(x) for x in large]

        def read(lst):
            s = {}
            for key, kind, n, a, b, nm, ns in lst:
                if kind == 'buf':
                    s[key] = (bytes(ctrl.GetBufferData(buf[n].resourceId, a, b)), 4)
                    continue
                t = tex[n]
                for m in range(a, a + nm):
                    for sl in range(b, b + ns):
                        px = max(1, t.width >> m) * max(1, t.height >> m) * (max(1, t.depth >> m) if t.depth > 1 else 1)
                        est = px * 16
                        k2 = '%s|m%d|s%d' % (key, m, sl)
                        if est > BIG * 2:
                            large.append(('sub', k2, est)); continue
                        data = bytes(ctrl.GetTextureData(t.resourceId, rd.Subresource(m, sl, 0)))
                        s[k2] = (data, (len(data) // px if px else 0) or 4)  # block-compressed: 4-byte words
            return s

        bc = [c for c in cands if c[0] == 'buffers']
        dvid = R.named_var(blobs['def'], 'buffers')
        name, ae, bn, boff, bsize, ckey = max(bc, key=lambda x: x[4])
        base_w = bsize // 4 - 2 * len(sites) - 1
        dblob, ndg = R.rewrite(blobs['def'], sites, 'diag', diag_var=dvid, diag_base=base_w, diag_prefix=(ae, 0))
        lo, hi = base_w * 4, base_w * 4 + 8 * len(sites) + 4
        r['diag'] = {'key': ckey, 'base_word': base_w, 'rewritten': ndg, 'sha': sha(dblob)[:16]}
        arms = os.environ.get('RD_ARMS', 'orig,def,mask,mem,sens,mask_inv,mem_inv,m3,diag,orig2').split(',')
        keep = {}
        for arm in arms:
            blob = None if arm in ('orig', 'orig2') else (dblob if arm == 'diag' else blobs[arm])
            nid = None
            if blob is not None:
                nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, blob, rd.ShaderCompileFlags(), PS)
                if nid == rd.ResourceId.Null():
                    r['build_failed_' + arm] = (err or '')[:300]; continue
                ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(pre_eid, True)
            pre = read(outs)
            pin = read(ins) if arm in ('orig', 'def', 'sens', 'mask', 'orig2') else None
            em1 = None
            if arm in ('orig', 'sens'):
                ctrl.SetFrameEvent(eid - 1, True)
                em1 = read(outs)
            ctrl.SetFrameEvent(eid, True)
            bsha = sha(bytes(ctrl.GetPipelineState().GetShaderReflection(PS).rawBytes))
            post = read(outs)
            if nid is not None:
                ctrl.RemoveReplacement(shid)
                ctrl.FreeTargetResource(nid)
            r['bound_ok_' + arm] = bsha == (CAP_SHA if blob is None else sha(blob))
            r['slots_pre_' + arm] = list(struct.unpack('<7I', pre[ckey][0][lo:hi]))
            r['slots_post_' + arm] = list(struct.unpack('<7I', post[ckey][0][lo:hi]))
            if arm == 'orig':
                keep['pre'], keep['post'], keep['in'], keep['em1'] = pre, post, pin, em1
                r['writes'] = cmpd(pre, post)
                r['n_in_bytes'] = sum(len(v[0]) for v in pin.values())
            else:
                skip = (ckey, lo, hi) if arm == 'diag' else None
                r['Npre_' + arm] = cmpd(keep['pre'], pre, skip)
                if pin is not None:
                    r['Nin_' + arm] = cmpd(keep['in'], pin)
                if em1 is not None:
                    r['Nem1_' + arm] = cmpd(keep['em1'], em1)
                    r['Nem1_vs_pre_orig'] = cmpd(keep['pre'], keep['em1'])
                if arm == 'def':
                    keep['def'] = post
                    r['N_orig_def'] = cmpd(keep['post'], post)
                elif arm == 'orig2':
                    r['N_null'] = cmpd(keep['post'], post)
                elif arm == 'diag':
                    r['selfcheck'] = cmpd(keep['def'], post, skip)
                else:
                    r['N_def_' + arm] = cmpd(keep['def'], post)
                    if arm == 'mask':
                        keep['mask'] = post
                    if arm == 'sens':
                        keep['sens'] = post
                    if arm in ('mem', 'm3') and 'mask' in keep:
                        r['N_mask_' + arm] = cmpd(keep['mask'], post)
                    if arm in ('mask_inv', 'mem_inv') and 'sens' in keep:
                        r['N_sens_' + arm] = cmpd(keep['sens'], post)
            pre = post = pin = em1 = None
            P('event', eid, 'arm', arm, 'done')
        r['t'] = round(time.time() - T0, 1)
        res['events'].append(r)
        json.dump(res, open(OUT, 'w'), sort_keys=True)
        P('event', eid, 'written')
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    LOGF.write(traceback.format_exc()); LOGF.flush()
LOGF.close()
os._exit(code)
