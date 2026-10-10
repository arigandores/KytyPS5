# F36a (HPP-758; ROADMAP s122 item 687(e)(0)(ii)): qrenderdoc --python rd_inv_f36a.py - inventory of the executions of the PS
# be4c35a2031fd3f4 in one capture, no shader replacement, no readback of contents.
# Modules: every Shader resource of the replay is hashed (rawBytes of GetShader for its first entry point); the ids whose sha256 is
# the S12 / captured module of the program (CAP_SHA) are the marks of the structured-data scan of F23f (sdscan_f23f.scan: create
# module -> pipeline -> bind -> draw by command buffer); every marked draw -> its event id (action whose events hold the chunk).
# Per event: bound PS sha (must be CAP_SHA), colour targets, depth target, colour blend, depth / stencil state, numIndices,
# numInstances; then GPU counters SamplesPassed, PSInvocations (FetchCounters, whole frame, no replacement); the execution
# number in the frame = rank of the event among the events of the program, by event id.
# Env: RD_CAP, RD_OUT (json).  ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, traceback
OUT = os.environ['RD_OUT']
LOGF = open(OUT + '.log', 'a')
NL = chr(10)
T0 = time.time()
CAP_SHA = 'ebff0feeb90b9b35c7aecbd6fc542fb6ded352504b70442b9172f533a571cb96'
PROG = 'ps_be4c35a2031fd3f4'


def P(*a):
    LOGF.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    LOGF.flush()


def rid_num(r):
    try:
        return int(str(r).split('::')[-1])
    except Exception:
        return -1


def g(o, *names, default=None):
    for n in names:
        if hasattr(o, n):
            return getattr(o, n)
    return default


def main():
    import renderdoc as rd
    sys.path.insert(0, 'C:/kyty/f287/f23f')
    import sdscan_f23f
    res = {'cap': os.environ['RD_CAP'], 'prog': PROG, 'cap_sha': CAP_SHA}
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('opened', os.environ['RD_CAP'])
    marks, nsh, shas = {}, 0, {}
    for r in ctrl.GetResources():
        if r.type != rd.ResourceType.Shader:
            continue
        nsh += 1
        try:
            eps = ctrl.GetShaderEntryPoints(r.resourceId)
            if not eps:
                continue
            refl = ctrl.GetShader(rd.ResourceId.Null(), r.resourceId, eps[0])
            s = hashlib.sha256(bytes(refl.rawBytes)).hexdigest()
        except Exception as e:
            P('shader', r.resourceId, 'error', e)
            continue
        shas[str(r.resourceId)] = s
        if s == CAP_SHA:
            marks[str(r.resourceId)] = PROG
    res['shader_resources'] = nsh
    res['marked_module_ids'] = sorted(marks)
    P('shader resources', nsh, 'marked', sorted(marks))
    sacts, nmod, npipe = sdscan_f23f.scan(ctrl.GetStructuredFile(), marks)
    res['scan'] = {'modules': nmod, 'pipelines': npipe, 'marked_actions': len(sacts)}
    P('scan modules', nmod, 'pipelines', npipe, 'marked actions', len(sacts))
    by_chunk = {}

    def walk(al):
        for a in al:
            for ev in a.events:
                by_chunk[ev.chunkIndex] = a
            walk(a.children)
    walk(ctrl.GetRootActions())
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    evs = []
    for ci, nm, stage, sha, name in sacts:
        a = by_chunk.get(ci)
        evs.append({'chunk': ci, 'call': nm, 'eid': a.eventId if a is not None else -1})
    evs.sort(key=lambda e: e['eid'])
    sdf = ctrl.GetStructuredFile()
    for k, e in enumerate(evs):
        e['exec_no'] = k + 1
        if e['eid'] < 0:
            continue
        ctrl.SetFrameEvent(e['eid'], False)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(rd.ShaderStage.Pixel)
        e['bound_sha'] = hashlib.sha256(bytes(refl.rawBytes)).hexdigest() if refl is not None else ''
        e['bound_is_cap'] = e['bound_sha'] == CAP_SHA
        act = by_chunk[e['chunk']]
        e['action'] = act.GetName(sdf)
        e['numIndices'], e['numInstances'] = int(act.numIndices), int(act.numInstances)
        rts = []
        for i, d in enumerate(ps.GetOutputTargets()):
            n = rid_num(g(d, 'resource', 'resourceId'))
            if n > 0:
                t = textures.get(n)
                rts.append({'slot': i, 'res': n, 'fmt': t.format.Name() if t else '?', 'w': t.width if t else 0, 'h': t.height if t else 0,
                            'mip': int(g(d, 'firstMip', default=0)), 'slice': int(g(d, 'firstSlice', default=0))})
        e['rts'] = rts
        dt = ps.GetDepthTarget()
        n = rid_num(g(dt, 'resource', 'resourceId'))
        e['depth'] = {'res': n, 'fmt': textures[n].format.Name() if n in textures else '?'} if n > 0 else None
        try:
            e['blend'] = [{'en': int(b.enabled), 'mask': '%x' % int(b.writeMask)} for b in ps.GetColorBlends()]
        except Exception as ex:
            e['blend'] = 'error %s' % ex
        try:
            vk = ctrl.GetVulkanPipelineState()
            ds = vk.depthStencil
            e['ds'] = {'test': int(ds.depthTestEnable), 'write': int(ds.depthWriteEnable), 'func': str(ds.depthFunction),
                       'stencil': int(ds.stencilTestEnable),
                       'front': {k2: str(getattr(ds.frontFace, k2, '?')) for k2 in ('function', 'passOperation', 'failOperation', 'depthFailOperation', 'reference', 'compareMask', 'writeMask')}}
        except Exception as ex:
            e['ds'] = 'error %s' % ex
        P('event', e['eid'], 'exec', e['exec_no'], 'bound_is_cap', e['bound_is_cap'])
    res['events'] = evs
    json.dump(res, open(OUT, 'w'), indent=1, sort_keys=True)
    try:
        avail = list(ctrl.EnumerateCounters())
        want = [c for c in (rd.GPUCounter.SamplesPassed, rd.GPUCounter.PSInvocations) if c in avail]
        res['counters_available'] = [str(c) for c in want]
        t1 = time.time()
        vals = ctrl.FetchCounters(want)
        res['counters_s'] = round(time.time() - t1, 1)
        byeid = {e['eid']: e for e in evs}
        for v in vals:
            if v.eventId in byeid:
                byeid[v.eventId].setdefault('counters', {})[{int(rd.GPUCounter.SamplesPassed): 'SamplesPassed', int(rd.GPUCounter.PSInvocations): 'PSInvocations'}.get(int(v.counter), str(v.counter))] = int(v.value.u64)
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
