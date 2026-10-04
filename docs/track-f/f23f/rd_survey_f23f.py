# F23f (HPP-592; ROADMAP s122 item 498(g)(2)(a), (g)): qrenderdoc --python rd_survey_f23f.py - replay SURVEY (no shader
# replacement, no readback of resource contents): for every marked action of the structured-data reading (RD_ACTS = file
# with 'ACT chunk=<i> ... name=<prog>' lines) finds the event id (last API event of the action with that chunk index), moves to
# it (SetFrameEvent forward, not forced) and prints: the bound module sha256 of the stage (rawBytes of the reflection), for
# draws the colour targets (resource, format, size, mip, slice), the depth target, the colour blend of every target (enable,
# write mask, colour / alpha equations), depth state; for both kinds every read-write descriptor (resource, offset, size,
# kind) and every read-only buffer descriptor.  Output: RD_OUT.  ASCII only; exits by os._exit.
import os, traceback, hashlib, time
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f23f/runs/survey.txt')
out = open(OUT, 'w')
NL = chr(10)
T0 = time.time()


def P(*a):
    out.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    out.flush()


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
    import sys
    sys.path.insert(0, 'C:/kyty/f287/f23f')
    import sdscan_f23f
    marks = {}
    for line in open(os.environ['RD_MARKS']):
        if line.startswith('MODULE ') and ' name=' in line:
            f = line.split()
            marks[f[1]] = f[-1].split('=', 1)[1]
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('capture', os.environ['RD_CAP'], 'opened')
    sacts, nmod, npipe = sdscan_f23f.scan(ctrl.GetStructuredFile(), marks)
    P('replay sdf scan: modules', nmod, 'pipelines', npipe, 'marked actions', len(sacts))
    acts = [(ci, name, stage) for ci, nm, stage, sha, name in sacts]
    by_chunk = {}

    def walk(a_list):
        for a in a_list:
            for ev in a.events:
                by_chunk[ev.chunkIndex] = a
            walk(a.children)
    walk(ctrl.GetRootActions())
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    buffers = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}
    rows = []
    for ci, name, stage in acts:
        a = by_chunk.get(ci)
        rows.append((a.eventId if a is not None else -1, ci, name, stage, a))
    rows.sort()
    for eid, ci, name, stage, a in rows:
        if a is None:
            P('EVENT chunk', ci, name, 'NOT FOUND'); continue
        ctrl.SetFrameEvent(eid, False)
        ps = ctrl.GetPipelineState()
        sst = rd.ShaderStage.Compute if stage == 'cs' else rd.ShaderStage.Pixel
        refl = ps.GetShaderReflection(sst)
        raw = bytes(refl.rawBytes) if refl is not None else b''
        flags = int(a.flags)
        P('EVENT eid', eid, 'chunk', ci, 'prog', name, 'stage', stage, 'module_sha', hashlib.sha256(raw).hexdigest(), 'bytes', len(raw),
          'action', a.GetName(ctrl.GetStructuredFile()), 'numIndices', a.numIndices, 'numInstances', a.numInstances,
          'dispatch', 'x'.join(str(int(v)) for v in a.dispatchDimension))
        if stage == 'ps':
            outs = ps.GetOutputTargets()
            for k, d in enumerate(outs):
                n = rid_num(g(d, 'resource', 'resourceId'))
                if n <= 0:
                    continue
                t = textures.get(n)
                P('  RT', k, 'res', n, 'fmt', t.format.Name() if t else '?', 'w', t.width if t else '?', 'h', t.height if t else '?',
                  'mips', t.mips if t else '?', 'arr', t.arraysize if t else '?', 'firstMip', g(d, 'firstMip', default='?'),
                  'firstSlice', g(d, 'firstSlice', default='?'), 'viewfmt', g(d, 'format', default=None).Name() if g(d, 'format') is not None else '?')
            dt = ps.GetDepthTarget()
            n = rid_num(g(dt, 'resource', 'resourceId'))
            if n > 0:
                t = textures.get(n)
                P('  DEPTH res', n, 'fmt', t.format.Name() if t else '?', 'w', t.width if t else '?', 'h', t.height if t else '?')
            try:
                for k, b in enumerate(ps.GetColorBlends()):
                    cb, ab = b.colorBlend, b.alphaBlend
                    P('  BLEND', k, 'enabled', int(b.enabled), 'writeMask', '%x' % int(b.writeMask), 'color', str(cb.source), str(cb.destination),
                      str(cb.operation), 'alpha', str(ab.source), str(ab.destination), str(ab.operation))
            except Exception as e:
                P('  BLEND error', e)
            try:
                vk = ctrl.GetVulkanPipelineState()
                ds = vk.depthStencil
                P('  DEPTHSTATE test', int(ds.depthTestEnable), 'write', int(ds.depthWriteEnable), 'func', str(ds.depthFunction),
                  'stencil', int(ds.stencilTestEnable))
                P('  RASTER discard', int(vk.rasterizer.rasterizerDiscardEnable), 'samples', vk.multisample.rasterSamples)
            except Exception as e:
                P('  VKSTATE error', e)
        for kind, lst in (('RW', ps.GetReadWriteResources(sst)), ('RO', ps.GetReadOnlyResources(sst))):
            for u in lst:
                d = getattr(u, 'descriptor', None)
                acc = getattr(u, 'access', None)
                if d is None:
                    continue
                n = rid_num(d.resource)
                if n <= 0:
                    continue
                if n in textures:
                    if kind == 'RO':
                        continue
                    t = textures[n]
                    P('  %s tex' % kind, n, 'bind', g(acc, 'index', default='?'), 'elem', g(acc, 'arrayElement', default='?'), 'fmt', t.format.Name(),
                      'w', t.width, 'h', t.height, 'd', t.depth, 'mips', t.mips, 'arr', t.arraysize, 'bytes', t.byteSize)
                elif n in buffers:
                    P('  %s buf' % kind, n, 'bind', g(acc, 'index', default='?'), 'elem', g(acc, 'arrayElement', default='?'), 'len', buffers[n].length,
                      'off', g(d, 'byteOffset', default='?'), 'size', g(d, 'byteSize', default='?'))
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    out.write(traceback.format_exc())
    out.flush()
out.close()
os._exit(code)
