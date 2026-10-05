# F23g (HPP-593, Red Team; ROADMAP s122 item 498(g) F23g): own repeat of valid events of F23f in a RenderDoc replay.
# qrenderdoc --python rd_f23g.py ; env RD_CAP capture, RD_EV json list [{eid, prog, stage, cap_sha}], RD_OUT json file.
# Own code (not rd_f23f.py): per event and arm the state at eid-1 AND at eid is read with the arm's replacement active
# (equality of the arms' states before the event), arms: orig (no replacement), def, def2, mask, mem, sens (F23f files, sha
# checked against arms_f23f.json) and two own positive controls mask_inv / mem_inv (the reference with the bit inverted:
# semantics = sens; built by patch_inv() below from the F23f mask / mem bytes, only instructions with ids >= the def bound).
# Also: depth / stencil state of the draw and GPU counters SamplesPassed / PSInvocations / CSInvocations (no replacement and
# with sens) - does the draw pass any sample at all.  ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, struct, traceback
OUT = os.environ['RD_OUT']
NL = chr(10)
T0 = time.time()
LOGF = open(OUT + '.log', 'a')
A = 'C:/kyty/f287/f23f/arms/'
BIG = 64 * 1024 * 1024


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


def patch_inv(ref, dflt, kind):
    """mask: OpISub %u %m %c0 %bit (new id) -> OpISub %u %m %bit %c1 ; mem: the two OpAccessChain %pu %a %tmp %c0/%c1 (new ids)
    whose result is the pointer of a Volatile OpStore -> indices swapped. Returns (bytes, number of patched instructions)."""
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
    c1id = sorted(c1)[0]
    c0id = sorted(c0)[0]
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
        if kind == 'mask' and op == 130 and n == 5 and w[i + 2] >= bound_def and w[i + 3] in c0:
            bit = w[i + 4]
            w[i + 3], w[i + 4] = bit, c1id
            k += 1
        if kind == 'mem' and op == 65 and n == 5 and w[i + 2] >= bound_def and w[i + 2] in stores and (w[i + 4] in c0 or w[i + 4] in c1):
            w[i + 4] = c1id if w[i + 4] in c0 else c0id
            k += 1
        i += n
    return struct.pack('<%dI' % len(w), *w), k


def main():
    import renderdoc as rd
    evs = json.loads(os.environ['RD_EV'])
    armsj = json.load(open('C:/kyty/f287/f23f/arms_f23f.json'))
    res = {'cap': os.environ['RD_CAP'], 'events': []}
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('opened', os.environ['RD_CAP'])
    tex = {rid(t.resourceId): t for t in ctrl.GetTextures()}
    buf = {rid(b.resourceId): b for b in ctrl.GetBuffers()}
    for ev in evs:
        eid, prog, stg = ev['eid'], ev['prog'], ev['stage']
        sst = rd.ShaderStage.Compute if stg == 'cs' else rd.ShaderStage.Pixel
        r = {'eid': eid, 'prog': prog, 'stage': stg}
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(sst)
        r['bound_sha'] = sha(bytes(refl.rawBytes))
        r['bound_is_cap'] = r['bound_sha'] == ev['cap_sha']
        shid = ps.GetShader(sst)
        entry = refl.entryPoint
        outs = []
        if stg == 'ps':
            for k, d in enumerate(ps.GetOutputTargets()):
                n = rid(d.resource)
                if n > 0:
                    outs.append(('rt%d' % k, 'tex', n, int(getattr(d, 'firstMip', 0)), int(getattr(d, 'firstSlice', 0))))
            dt = ps.GetDepthTarget()
            if rid(dt.resource) > 0:
                outs.append(('depth', 'tex', rid(dt.resource), int(getattr(dt, 'firstMip', 0)), int(getattr(dt, 'firstSlice', 0))))
            try:
                vk = ctrl.GetVulkanPipelineState()
                ds = vk.depthStencil
                def so(f):
                    return {k2: str(getattr(f, k2, '?')) for k2 in ('function', 'passOperation', 'failOperation', 'depthFailOperation', 'reference', 'compareMask', 'writeMask')}
                r['depthstencil'] = {'test': int(ds.depthTestEnable), 'write': int(ds.depthWriteEnable), 'func': str(ds.depthFunction),
                                     'boundsTest': int(getattr(ds, 'depthBoundsEnable', 0)), 'stencil': int(ds.stencilTestEnable),
                                     'front': so(ds.frontFace), 'back': so(ds.backFace)}
            except Exception as e:
                r['depthstencil'] = 'error %s' % e
        for u in ps.GetReadWriteResources(sst):
            d = getattr(u, 'descriptor', None)
            if d is None:
                continue
            n = rid(d.resource)
            if n <= 0:
                continue
            if n in tex:
                t = tex[n]
                for m in range(max(1, t.mips)):
                    for s in range(max(1, t.arraysize)):
                        outs.append(('rwt%d_m%d_s%d' % (n, m, s), 'tex', n, m, s))
            elif n in buf:
                off, size = int(getattr(d, 'byteOffset', 0)), int(getattr(d, 'byteSize', 0))
                if size == 0 or size > buf[n].length - off:
                    size = buf[n].length - off
                if size <= BIG:
                    outs.append(('rwb%d_o%d' % (n, off), 'buf', n, off, size))
                else:
                    r.setdefault('not_read', []).append('buf %d off %d size %d' % (n, off, size))
        seen, uo = set(), []
        for o in outs:
            if o[1:] not in seen:
                seen.add(o[1:]); uo.append(o)
        outs = uo
        r['outputs'] = [o[0] for o in outs]

        def read():
            s = {}
            for key, kind, n, a, b in outs:
                if kind == 'tex':
                    data = bytes(ctrl.GetTextureData(tex[n].resourceId, rd.Subresource(a, b, 0)))
                    t = tex[n]
                    px = max(1, t.width >> a) * max(1, t.height >> a) * (max(1, t.depth >> a) if t.depth > 1 else 1)
                    s[key] = (data, len(data) // px if px else 0)
                else:
                    s[key] = (bytes(ctrl.GetBufferData(buf[n].resourceId, a, b)), 4)
            return s
        r['unit_bytes'] = None
        arms = {}
        dflt = open(A + '%s_%s_def.spv' % (stg, prog), 'rb').read()
        for arm in ('def', 'mask', 'mem', 'sens'):
            b = open(A + '%s_%s_%s.spv' % (stg, prog, arm), 'rb').read()
            exp = armsj[prog]['files'][arm]['sha']
            r['file_sha_' + arm] = sha(b)[:16]
            r['file_sha_ok_' + arm] = sha(b).startswith(exp[:16]) if exp else None
            arms[arm] = b
        arms['def2'] = arms['def']
        arms['mask_inv'], r['inv_patched_mask'] = patch_inv(arms['mask'], dflt, 'mask')
        arms['mem_inv'], r['inv_patched_mem'] = patch_inv(arms['mem'], dflt, 'mem')
        r['sha_mask_inv'] = sha(arms['mask_inv'])[:16]
        r['sha_mem_inv'] = sha(arms['mem_inv'])[:16]
        def N(x, y):
            out = {}
            for k in x:
                a, u = x[k]
                b = y[k][0]
                if len(a) != len(b) or u <= 0:
                    out[k] = -1
                    continue
                if a == b:
                    out[k] = 0
                    continue
                c = 0
                for i in range(0, len(a), 65536):
                    xa, xb = a[i:i + 65536], b[i:i + 65536]
                    if xa != xb:
                        c += sum(1 for j in range(0, len(xa), u) if xa[j:j + u] != xb[j:j + u])
                out[k] = c
            return out
        keep = {}
        for arm in os.environ.get('RD_ARMS', 'orig,def,def2,sens,mask,mem,mask_inv,mem_inv').split(','):
            nid = None
            if arm != 'orig':
                nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, arms[arm], rd.ShaderCompileFlags(), sst)
                if nid == rd.ResourceId.Null():
                    r['build_failed_' + arm] = (err or '')[:300]
                    continue
                ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(eid - 1, True)
            pre = read()
            ctrl.SetFrameEvent(eid, True)
            rr = ctrl.GetPipelineState().GetShaderReflection(sst)
            r['bound_' + arm] = sha(bytes(rr.rawBytes))[:16]
            post = read()
            if nid is not None:
                ctrl.RemoveReplacement(shid)
                ctrl.FreeTargetResource(nid)
            r['sha_post_' + arm] = {k: sha(v[0])[:16] for k, v in post.items()}
            r['sha_pre_' + arm] = {k: sha(v[0])[:16] for k, v in pre.items()}
            r['units'] = {k: v[1] for k, v in post.items()}
            if arm == 'orig':
                keep['orig_pre'], keep['orig_post'] = pre, post
                r['N_writes_orig'] = N(pre, post)
            else:
                r['Npre_orig_' + arm] = N(keep['orig_pre'], pre)
                r['N_writes_' + arm] = N(pre, post)
                if arm == 'def':
                    r['N_writes_def'] = N(pre, post)
                    r['N_def_orig'] = N(post, keep['orig_post'])
                    keep['def'] = post
                else:
                    r['N_def_' + arm] = N(keep['def'], post)
                if arm in ('sens', 'mask'):
                    keep[arm] = post
                if arm == 'mem' and 'mask' in keep:
                    r['N_mask_mem'] = N(keep.pop('mask'), post)
                if arm in ('mask_inv', 'mem_inv') and 'sens' in keep:
                    r['N_sens_' + arm] = N(keep['sens'], post)
            pre = post = None
            P('event', eid, prog, 'arm', arm, 'done')
        keep = None
        res['events'].append(r)
        json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
        P('event', eid, 'written')
    # counters last (may be slow on a long frame)
    try:
        avail = list(ctrl.EnumerateCounters())
        want = [c for c in (rd.GPUCounter.SamplesPassed, rd.GPUCounter.PSInvocations, rd.GPUCounter.CSInvocations) if c in avail]
        res['counters_available'] = [str(c) for c in want]
        for ev in evs:
            for arm in os.environ.get('RD_CARMS', 'orig,sens,def').split(','):
                nid = None
                if arm != 'orig':
                    stg = ev['stage']
                    sst = rd.ShaderStage.Compute if stg == 'cs' else rd.ShaderStage.Pixel
                    ctrl.SetFrameEvent(ev['eid'], True)
                    ps = ctrl.GetPipelineState()
                    shid = ps.GetShader(sst)
                    b = open(A + '%s_%s_%s.spv' % (stg, ev['prog'], arm), 'rb').read()
                    nid, err = ctrl.BuildTargetShader(ps.GetShaderReflection(sst).entryPoint, rd.ShaderEncoding.SPIRV, b, rd.ShaderCompileFlags(), sst)
                    ctrl.ReplaceResource(shid, nid)
                t1 = time.time()
                vals = ctrl.FetchCounters(want)
                got = {}
                for v in vals:
                    if v.eventId == ev['eid']:
                        got[str(v.counter)] = int(v.value.u64)
                ev.setdefault('counters', {})[arm] = got
                ev['counters_s_' + arm] = round(time.time() - t1, 1)
                if nid is not None:
                    ctrl.RemoveReplacement(shid)
                    ctrl.FreeTargetResource(nid)
                res['counters'] = [{'eid': e['eid'], 'counters': e.get('counters'), } for e in evs]
                json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
                P('counters', ev['eid'], arm, got)
    except Exception:
        res['counters_error'] = traceback.format_exc()[-800:]
        json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    LOGF.write(traceback.format_exc())
    LOGF.flush()
LOGF.close()
os._exit(code)
