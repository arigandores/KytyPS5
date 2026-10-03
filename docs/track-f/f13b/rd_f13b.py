# F13b (HPP-483): analysis of the f13_rd capture (B41, ending_boss_after_credit black screen, ROADMAP s122 p.391(z)).
# qrenderdoc --python rd_f13b.py ; exits by os._exit. Env:
#   RD_CAP   capture (default C:/kyty/f287/f13a/f13_rd.rdc)
#   RD_OUT   output dir (default C:/kyty/f287/f13b/rd)
#   RD_PHASE "flow"  - every action of frame 2 (after the first present): name, written textures and their min/max after
#                      the action; draws - full state (shaders, inputs with min/max, blend, constants bytes)
#            "save"  - PNG of the textures listed in RD_SAVE="eid:tex,eid:tex" at those events
#            "debug" - RD_DBG="eid:x,y;..." pixel debug traces of draws
# Template: docs/track-f/f7b/rd_f7b.py (F7b).
import os, sys, traceback, json

CAP = os.environ.get('RD_CAP', 'C:/kyty/f287/f13a/f13_rd.rdc')
OUTDIR = os.environ.get('RD_OUT', 'C:/kyty/f287/f13b/rd')
PHASE = os.environ.get('RD_PHASE', 'flow')
os.makedirs(OUTDIR, exist_ok=True)
out = open(os.path.join(OUTDIR, 'rd_f13b_%s.txt' % PHASE), 'w', encoding='utf-8')


def P(*a):
    out.write(' '.join(str(x) for x in a) + '\n')
    out.flush()


def hide_ui():
    try:
        from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is not None:
            for w in app.topLevelWidgets():
                w.hide()
    except Exception:
        pass


def main():
    import renderdoc as rd
    P('capture:', CAP, 'phase', PHASE)
    rd.InitialiseReplay(rd.GlobalEnvironment(), [])
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(CAP, '', None) != rd.ResultCode.Succeeded:
        P('open failed')
        return 1
    res, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if res != rd.ResultCode.Succeeded:
        P('replay failed', res)
        return 1
    textures = {t.resourceId: t for t in ctrl.GetTextures()}
    buffers = {b.resourceId: b for b in ctrl.GetBuffers()}
    resnames = {r.resourceId: r.name for r in ctrl.GetResources()}
    sf = ctrl.GetStructuredFile()

    def rid_int(r):
        return int(str(r).split('::')[-1])

    byint = {rid_int(k): k for k in textures}
    bufint = {rid_int(k): k for k in buffers}

    def texdesc(rid):
        t = textures.get(rid)
        if t is None:
            return 'res %d' % rid_int(rid)
        return 'tex %d %dx%dx%d arr=%d mips=%d fmt=%s' % (
            rid_int(rid), t.width, t.height, t.depth, t.arraysize, t.mips, t.format.Name())

    actions = []

    def walk(acts):
        for a in acts:
            actions.append(a)
            walk(a.children)

    walk(ctrl.GetRootActions())
    byeid = {a.eventId: a for a in actions}
    presents = [a for a in actions if a.flags & rd.ActionFlags.Present]
    P('presents:', [(a.eventId, a.GetName(sf)) for a in presents])
    last = presents[-1].eventId if presents else actions[-1].eventId
    first2 = presents[0].eventId if len(presents) > 1 else 0
    P('frame 2 = events (%d, %d]' % (first2, last))

    def pv(v):
        return '(%.5g %.5g %.5g %.5g)' % tuple(v.floatValue[:4])

    def minmax(rid, mip=0, sl=0):
        try:
            mn, mx = ctrl.GetMinMax(rid, rd.Subresource(mip, sl, 0), rd.CompType.Typeless)
            return '%s..%s' % (pv(mn), pv(mx))
        except Exception as e:
            return 'minmax err %s' % e

    def written(a, eid):
        w = []
        if a.flags & rd.ActionFlags.Drawcall:
            for o in a.outputs:
                if o != rd.ResourceId.Null():
                    w.append(o)
            if a.depthOut != rd.ResourceId.Null():
                w.append(a.depthOut)
        if a.flags & (rd.ActionFlags.Clear | rd.ActionFlags.Copy | rd.ActionFlags.Resolve):
            if a.copyDestination != rd.ResourceId.Null():
                w.append(a.copyDestination)
        if a.flags & rd.ActionFlags.Dispatch:
            st = ctrl.GetPipelineState()
            for r in st.GetReadWriteResources(rd.ShaderStage.Compute):
                d = r.descriptor
                if d.resource != rd.ResourceId.Null():
                    w.append(d.resource)
        return w

    def dump_state(eid, a):
        st = ctrl.GetPipelineState()
        vk = ctrl.GetVulkanPipelineState()
        P('  ==== STATE EID %d %s numIndices=%d numInstances=%d indexOffset=%d vertexOffset=%d' % (
            eid, a.GetName(sf), a.numIndices, a.numInstances, a.indexOffset, a.vertexOffset))
        try:
            for i, b in enumerate(vk.colorBlend.blends[:8]):
                P('    blend[%d] en=%s src=%s dst=%s op=%s | a src=%s dst=%s op=%s mask=%x' % (
                    i, b.enabled, b.colorBlend.source, b.colorBlend.destination, b.colorBlend.operation,
                    b.alphaBlend.source, b.alphaBlend.destination, b.alphaBlend.operation, b.writeMask))
            ds = vk.depthStencil
            P('    depth test=%s write=%s func=%s stencil=%s' % (ds.depthTestEnable, ds.depthWriteEnable, ds.depthFunction, ds.stencilTestEnable))
            vp = vk.viewportScissor
            for v in vp.viewportScissors[:2]:
                P('    viewport x=%g y=%g w=%g h=%g scissor x=%d y=%d w=%d h=%d' % (
                    v.vp.x, v.vp.y, v.vp.width, v.vp.height, v.scissor.x, v.scissor.y, v.scissor.width, v.scissor.height))
            r = vk.rasterizer
            P('    raster cull=%s fill=%s' % (r.cullMode, r.fillMode))
        except Exception as e:
            P('    vk state err', e)
        stages = [(rd.ShaderStage.Vertex, 'vs'), (rd.ShaderStage.Pixel, 'ps')] if a.flags & rd.ActionFlags.Drawcall else \
            [(rd.ShaderStage.Compute, 'cs')]
        info = {'eid': eid}
        for stage, sname in stages:
            refl = st.GetShaderReflection(stage)
            if refl is None:
                P('    %s none' % sname)
                continue
            sid = st.GetShader(stage)
            info[sname] = rid_int(sid)
            spv = os.path.join(OUTDIR, '%s_%d.spv' % (sname, rid_int(sid)))
            if not os.path.exists(spv):
                open(spv, 'wb').write(bytes(refl.rawBytes))
            P('    %s shader %d spirv bytes %d' % (sname, rid_int(sid), len(refl.rawBytes)))
            for r in st.GetReadOnlyResources(stage):
                d = r.descriptor
                if d.resource == rd.ResourceId.Null():
                    continue
                if d.resource in textures:
                    P('    %s RO idx=%d arr=%d %s view fmt=%s mip=%d+%d | %s' % (
                        sname, r.access.index, r.access.arrayElement, texdesc(d.resource), d.format.Name(), d.firstMip,
                        d.numMips, minmax(d.resource, d.firstMip)))
                    info.setdefault('tex_' + sname, []).append(rid_int(d.resource))
                else:
                    P('    %s RO idx=%d buf %d off=%d len=%d' % (sname, r.access.index, rid_int(d.resource), d.byteOffset, d.byteSize))
                    info.setdefault('buf_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            for r in st.GetReadWriteResources(stage):
                d = r.descriptor
                if d.resource == rd.ResourceId.Null():
                    continue
                if d.resource in textures:
                    P('    %s RW idx=%d %s' % (sname, r.access.index, texdesc(d.resource)))
                else:
                    P('    %s RW idx=%d buf %d off=%d len=%d' % (sname, r.access.index, rid_int(d.resource), d.byteOffset, d.byteSize))
                    info.setdefault('rw_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            for r in st.GetConstantBlocks(stage):
                d = r.descriptor
                if d.resource == rd.ResourceId.Null():
                    P('    %s CB idx=%d inline/push len=%d' % (sname, r.access.index, d.byteSize))
                    continue
                P('    %s CB idx=%d buf %d off=%d len=%d' % (sname, r.access.index, rid_int(d.resource), d.byteOffset, d.byteSize))
                info.setdefault('cb_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            for key in ('buf_' + sname, 'cb_' + sname):
                for (b, off, ln) in info.get(key, []):
                    n = min(ln if ln > 0 else 4096, 65536)
                    try:
                        data = bytes(ctrl.GetBufferData(bufint[b], off, n))
                        fn = os.path.join(OUTDIR, 'buf_e%d_%s_%d_%d.bin' % (eid, sname, b, off))
                        open(fn, 'wb').write(data)
                        P('    bytes %s %d' % (os.path.basename(fn), len(data)))
                    except Exception as e:
                        P('    buffer read err', b, e)
            try:
                targets = ctrl.GetDisassemblyTargets(True)
                pipe = st.GetComputePipelineObject() if sname == 'cs' else st.GetGraphicsPipelineObject()
                dis = ctrl.DisassembleShader(pipe, refl, targets[0])
                fn = os.path.join(OUTDIR, '%s_%d.rd.txt' % (sname, rid_int(sid)))
                if not os.path.exists(fn):
                    open(fn, 'w', encoding='utf-8').write(dis)
            except Exception as e:
                P('    disasm err', e)
        return info

    if PHASE == 'flow':
        infos = []
        tex_seen = {}
        for a in actions:
            if not (first2 < a.eventId <= last):
                continue
            if a.children:
                continue
            eid = a.eventId
            ctrl.SetFrameEvent(eid, True)
            kind = []
            for nm, fl in (('DRAW', rd.ActionFlags.Drawcall), ('DISPATCH', rd.ActionFlags.Dispatch), ('CLEAR', rd.ActionFlags.Clear),
                           ('COPY', rd.ActionFlags.Copy), ('PRESENT', rd.ActionFlags.Present), ('RESOLVE', rd.ActionFlags.Resolve)):
                if a.flags & fl:
                    kind.append(nm)
            line = 'EID %d %s %s' % (eid, '/'.join(kind) or 'OTHER', a.GetName(sf))
            if a.flags & rd.ActionFlags.Dispatch:
                line += ' groups=%s' % (list(a.dispatchDimension),)
            if a.flags & (rd.ActionFlags.Copy | rd.ActionFlags.Clear):
                line += ' src=%s dst=%s' % (texdesc(a.copySource) if a.copySource != rd.ResourceId.Null() else '-',
                                            texdesc(a.copyDestination) if a.copyDestination != rd.ResourceId.Null() else '-')
            P(line)
            if a.flags & rd.ActionFlags.Present:
                for r in [a.copySource, a.copyDestination] + list(a.outputs):
                    if r != rd.ResourceId.Null() and r in textures:
                        P('  present res %s | %s' % (texdesc(r), minmax(r)))
            try:
                w = written(a, eid)
            except Exception as e:
                P('  written err', e)
                w = []
            for r in w:
                if r in textures:
                    t = textures[r]
                    P('  W %s | after: %s' % (texdesc(r), minmax(r)))
                    tex_seen[rid_int(r)] = eid
                else:
                    P('  W buf %d' % rid_int(r))
            if a.flags & rd.ActionFlags.Drawcall:
                infos.append(dump_state(eid, a))
            if a.flags & rd.ActionFlags.Dispatch:
                st = ctrl.GetPipelineState()
                sid = st.GetShader(rd.ShaderStage.Compute)
                P('  cs shader %d' % rid_int(sid))
        json.dump({'infos': infos, 'tex_last_write': tex_seen}, open(os.path.join(OUTDIR, 'flow.json'), 'w'), indent=1)
    elif PHASE == 'save':
        for item in os.environ.get('RD_SAVE', '').split(','):
            if not item.strip():
                continue
            e, tid = [int(v) for v in item.split(':')]
            ctrl.SetFrameEvent(e, True)
            rid = byint[tid]
            ts = rd.TextureSave()
            ts.resourceId = rid
            ts.destType = rd.FileType.PNG
            ts.mip = 0
            ts.alpha = rd.AlphaMapping.Discard
            fn = os.path.join(OUTDIR, 'tex_%d_e%d.png' % (tid, e))
            ok = ctrl.SaveTexture(ts, fn)
            P('saved', os.path.basename(fn), ok, minmax(rid))
    elif PHASE == 'debug':
        for item in os.environ.get('RD_DBG', '').split(';'):
            if not item.strip():
                continue
            e, xy = item.split(':')
            eid = int(e)
            x, y = [int(v) for v in xy.split(',')]
            ctrl.SetFrameEvent(eid, True)
            inputs = rd.DebugPixelInputs()
            inputs.sample = 0
            inputs.primitive = rd.ReplayController.NoPreference
            inputs.view = rd.ReplayController.NoPreference
            P('---- DEBUG eid %d pixel %d,%d' % (eid, x, y))
            trace = ctrl.DebugPixel(x, y, inputs)
            if trace is None or trace.debugger is None:
                P('  debug failed (no trace)')
                continue
            fn = os.path.join(OUTDIR, 'dbg_e%d_%d_%d.txt' % (eid, x, y))
            f = open(fn, 'w', encoding='utf-8')
            n = 0
            while n < 200000:
                more = ctrl.ContinueDebug(trace.debugger)
                if not more:
                    break
                for s in more:
                    n += 1
                    for ch in s.changes:
                        v = ch.after
                        cnt = max(1, v.columns * max(1, v.rows))
                        try:
                            fv = [round(q, 6) for q in v.value.f32v[:min(cnt, 16)]]
                            uv = list(v.value.u32v[:min(cnt, 16)])
                        except Exception:
                            fv, uv = '?', '?'
                        f.write('[%d] inst=%d %s %s f=%s u=%s\n' % (s.stepIndex, s.nextInstruction, v.name, v.type, fv, uv))
            f.close()
            P('  steps %d -> %s' % (n, os.path.basename(fn)))
            ctrl.FreeTrace(trace)
    P('done')
    ctrl.Shutdown()
    cap.Shutdown()
    rd.ShutdownReplay()
    return 0


hide_ui()
code = 2
try:
    code = main()
except BaseException:
    P(traceback.format_exc())
out.close()
os._exit(code)
