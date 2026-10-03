# F7b (HPP-398): floor draw analysis of the enemy_final capture (B39 diagnosis, ROADMAP p.327(e)).
# qrenderdoc --python rd_f7b.py ; exits by os._exit. Env:
#   RD_CAP   capture (default C:/kyty/f287/f7a/enemy_final_600.rdc)
#   RD_OUT   output dir (default C:/kyty/f287/f7b/rd)
#   RD_PHASE "hist" (pixel history + state of the found draws) | "debug" (RD_DBG="eid:x,y;eid:x,y" pixel debug traces)
#   RD_PHASE "vsout" (RD_VS="eid,eid": post-VS outputs, raw vertex/index bytes and signatures)
# Points are given in 1280x720 thumbnail space and scaled to every texture's size.
import os, sys, glob, traceback, struct, json

CAP = os.environ.get('RD_CAP', 'C:/kyty/f287/f7a/enemy_final_600.rdc')
OUTDIR = os.environ.get('RD_OUT', 'C:/kyty/f287/f7b/rd')
PHASE = os.environ.get('RD_PHASE', 'hist')
os.makedirs(OUTDIR, exist_ok=True)
out = open(os.path.join(OUTDIR, 'rd_f7b_%s.txt' % PHASE), 'w', encoding='utf-8')

# thumbnail-space points (1280x720): floor F1..F6, Astro body A1, saucer U1, arena rim R1
POINTS = [
    ('F1', 300, 520), ('F2', 950, 480), ('F3', 640, 670), ('F4', 150, 420), ('F5', 1150, 600), ('F6', 820, 390),
    ('A1', 640, 565), ('U1', 640, 300), ('R1', 640, 700),
]


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

    def texdesc(rid):
        t = textures.get(rid)
        if t is None:
            return 'tex(%s)' % rid
        return 'tex %d %dx%dx%d arr=%d mips=%d fmt=%s ms=%d name=%s' % (
            rid_int(rid), t.width, t.height, t.depth, t.arraysize, t.mips, t.format.Name(), t.msSamp, resnames.get(rid, ''))

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
        return '(%.4f %.4f %.4f %.4f)' % tuple(v.floatValue[:4])

    def dump_state(eid, tag):
        a = byeid[eid]
        ctrl.SetFrameEvent(eid, True)
        st = ctrl.GetPipelineState()
        vk = ctrl.GetVulkanPipelineState()
        P('==== STATE %s EID %d %s numIndices=%d numInstances=%d' % (tag, eid, a.GetName(sf), a.numIndices, a.numInstances))
        for i, o in enumerate(a.outputs):
            if o != rd.ResourceId.Null():
                P('  RT[%d] %s' % (i, texdesc(o)))
        if a.depthOut != rd.ResourceId.Null():
            P('  DS %s' % texdesc(a.depthOut))
        try:
            for i, b in enumerate(vk.colorBlend.blends[:8]):
                P('  blend[%d] en=%s src=%s dst=%s op=%s | a src=%s dst=%s op=%s mask=%x' % (
                    i, b.enabled, b.colorBlend.source, b.colorBlend.destination, b.colorBlend.operation,
                    b.alphaBlend.source, b.alphaBlend.destination, b.alphaBlend.operation, b.writeMask))
            ds = vk.depthStencil
            P('  depth test=%s write=%s func=%s stencil=%s' % (ds.depthTestEnable, ds.depthWriteEnable, ds.depthFunction, ds.stencilTestEnable))
            r = vk.rasterizer
            P('  raster cull=%s frontCCW=%s fill=%s' % (r.cullMode, r.frontCCW, r.fillMode))
        except Exception as e:
            P('  vk state err', e)
        info = {'eid': eid}
        for stage, sname in ((rd.ShaderStage.Vertex, 'vs'), (rd.ShaderStage.Pixel, 'ps')):
            refl = st.GetShaderReflection(stage)
            if refl is None:
                P('  %s none' % sname)
                continue
            sid = st.GetShader(stage)
            info[sname] = rid_int(sid)
            P('  %s shader %d name=%s entry=%s debugName=%s' % (sname, rid_int(sid), resnames.get(sid, ''),
                                                              st.GetShaderEntryPoint(stage), getattr(refl, 'debugInfo', None) and refl.debugInfo.files and refl.debugInfo.files[0].filename))
            spv = os.path.join(OUTDIR, '%s_%d.spv' % (sname, rid_int(sid)))
            if not os.path.exists(spv):
                open(spv, 'wb').write(bytes(refl.rawBytes))
            P('    spirv %s bytes %d' % (spv, len(refl.rawBytes)))
            for s in refl.readOnlyResources:
                P('    refl RO name=%s textureType=%s isTexture=%s bind=%s' % (s.name, s.textureType, s.isTexture, getattr(s, 'fixedBindNumber', '?')))
            for s in refl.samplers:
                P('    refl SAMP name=%s bind=%s' % (s.name, getattr(s, 'fixedBindNumber', '?')))
            for c in refl.constantBlocks:
                P('    refl CB name=%s vars=%d size=%d bufferBacked=%s' % (c.name, len(c.variables), c.byteSize, c.bufferBacked))
            for s in refl.readWriteResources:
                P('    refl RW name=%s isTexture=%s' % (s.name, s.isTexture))
            for r in st.GetReadOnlyResources(stage):
                d = r.descriptor
                acc = r.access
                if d.resource == rd.ResourceId.Null():
                    continue
                if d.resource in textures:
                    P('    RO idx=%d arr=%d %s view fmt=%s mip=%d+%d slice=%d+%d swz=%s' % (
                        acc.index, acc.arrayElement, texdesc(d.resource), d.format.Name(), d.firstMip, d.numMips,
                        d.firstSlice, d.numSlices, d.swizzle))
                    info.setdefault('tex_' + sname, []).append(rid_int(d.resource))
                else:
                    P('    RO idx=%d arr=%d buf %d off=%d len=%d name=%s' % (acc.index, acc.arrayElement, rid_int(d.resource),
                                                                         d.byteOffset, d.byteSize, resnames.get(d.resource, '')))
                    info.setdefault('buf_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            for r in st.GetSamplers(stage):
                s = r.descriptor if not hasattr(r, 'sampler') else r.sampler
                try:
                    P('    SAMP idx=%d arr=%d filter=%s addr=%s/%s/%s mipBias=%s minLOD=%s maxLOD=%s aniso=%s border=%s' % (
                        r.access.index, r.access.arrayElement, s.filter, s.addressU, s.addressV, s.addressW, s.mipBias,
                        s.minLOD, s.maxLOD, s.maxAnisotropy, getattr(s, 'borderColorValue', None) and list(s.borderColorValue.floatValue)))
                except Exception as e:
                    P('    SAMP err', e)
            for r in st.GetConstantBlocks(stage):
                d = r.descriptor
                if d.resource == rd.ResourceId.Null():
                    P('    CB idx=%d inline/push len=%d' % (r.access.index, d.byteSize))
                    continue
                P('    CB idx=%d buf %d off=%d len=%d' % (r.access.index, rid_int(d.resource), d.byteOffset, d.byteSize))
                info.setdefault('cb_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            for r in st.GetReadWriteResources(stage):
                d = r.descriptor
                if d.resource == rd.ResourceId.Null():
                    continue
                P('    RW idx=%d %s' % (r.access.index, texdesc(d.resource) if d.resource in textures else 'buf %d off=%d len=%d' % (
                    rid_int(d.resource), d.byteOffset, d.byteSize)))
                if d.resource not in textures:
                    info.setdefault('rw_' + sname, []).append((rid_int(d.resource), d.byteOffset, d.byteSize))
            # buffer bytes (small) for constants
            for key in ('buf_' + sname, 'cb_' + sname, 'rw_' + sname):
                for (b, off, ln) in info.get(key, []):
                    n = min(ln if ln > 0 else 4096, 65536)
                    try:
                        data = bytes(ctrl.GetBufferData(byint.get(b) or [k for k in buffers if rid_int(k) == b][0], off, n))
                        fn = os.path.join(OUTDIR, 'buf_e%d_%s_%d_%d.bin' % (eid, sname, b, off))
                        open(fn, 'wb').write(data)
                        P('    bytes %s %d' % (fn, len(data)))
                    except Exception as e:
                        P('    buffer read err', b, e)
            if sname == 'ps':
                try:
                    targets = ctrl.GetDisassemblyTargets(True)
                    dis = ctrl.DisassembleShader(st.GetGraphicsPipelineObject(), refl, targets[0])
                    fn = os.path.join(OUTDIR, 'ps_%d.rd.txt' % rid_int(sid))
                    if not os.path.exists(fn):
                        open(fn, 'w', encoding='utf-8').write(dis)
                    P('    disasm %s (%s)' % (fn, targets[0]))
                except Exception as e:
                    P('    disasm err', e)
        return info

    def tex_stats(rid, eid):
        t = textures[rid]
        ctrl.SetFrameEvent(eid, True)
        for mip in sorted(set([0, max(0, t.mips - 1)] + list(range(min(t.mips, 3))))):
            sub = rd.Subresource(mip, 0, 0)
            try:
                mn, mx = ctrl.GetMinMax(rid, sub, rd.CompType.Typeless)
                P('    stats tex %d mip %d (%dx%d) min=%s max=%s' % (rid_int(rid), mip, max(1, t.width >> mip), max(1, t.height >> mip), pv(mn), pv(mx)))
            except Exception as e:
                P('    minmax err', e)
            if mip == 0 or mip == t.mips - 1:
                ts = rd.TextureSave()
                ts.resourceId = rid
                ts.destType = rd.FileType.PNG
                ts.mip = mip
                ts.alpha = rd.AlphaMapping.Discard
                fn = os.path.join(OUTDIR, 'tex_%d_e%d_m%d.png' % (rid_int(rid), eid, mip))
                ok = ctrl.SaveTexture(ts, fn)
                P('    saved %s %s' % (fn, ok))
                if mip == 0 and t.width * t.height <= 4096 * 4096:
                    try:
                        raw = bytes(ctrl.GetTextureData(rid, sub))
                        rfn = os.path.join(OUTDIR, 'tex_%d_e%d_m0.raw' % (rid_int(rid), eid))
                        open(rfn, 'wb').write(raw)
                        P('    raw %s %d bytes' % (rfn, len(raw)))
                    except Exception as e:
                        P('    raw err', e)

    if PHASE == 'hist':
        # targets: final presented image of frame 2 and every colour/depth target of draws in frame 2
        tgts = {}
        for a in actions:
            if first2 < a.eventId <= last and (a.flags & rd.ActionFlags.Drawcall):
                for o in a.outputs:
                    if o != rd.ResourceId.Null() and textures[o].width >= 1280:
                        tgts[o] = 1
                if a.depthOut != rd.ResourceId.Null() and textures[a.depthOut].width >= 1280:
                    tgts[a.depthOut] = 1
        if presents:
            pa = presents[-1]
            for r in [pa.copySource, pa.copyDestination] + list(pa.outputs):
                if r != rd.ResourceId.Null() and r in textures:
                    tgts[r] = 1
        P('history targets:', [texdesc(t) for t in tgts])
        ctrl.SetFrameEvent(last, True)
        hits = {}
        for tid in tgts:
            t = textures[tid]
            if t.msSamp > 1:
                continue
            for (name, x, y) in POINTS:
                X = x * t.width // 1280
                Y = y * t.height // 720
                try:
                    hist = ctrl.PixelHistory(tid, X, Y, rd.Subresource(0, 0, 0), rd.CompType.Typeless)
                except Exception as e:
                    P('hist err', e)
                    continue
                mods = [m for m in hist if first2 < m.eventId <= last]
                P('-- HIST %s (%d,%d) on %s : %d mods in frame 2 (%d total)' % (name, X, Y, texdesc(tid), len(mods), len(hist)))
                for m in mods:
                    a = byeid.get(m.eventId)
                    ok = m.Passed()
                    P('   eid %d %s passed=%s prim=%d frag=%d pre=%s out=%s post=%s depth pre=%.6f post=%.6f flags:%s%s%s%s%s' % (
                        m.eventId, a.GetName(sf) if a else '?', ok, m.primitiveID, m.fragIndex, pv(m.preMod.col), pv(m.shaderOut.col),
                        pv(m.postMod.col), m.preMod.depth, m.postMod.depth,
                        ' depthFail' if m.depthTestFailed else '', ' discard' if m.shaderDiscarded else '',
                        ' culled' if m.backfaceCulled else '', ' clip' if m.depthClipped or m.viewClipped or m.scissorClipped else '',
                        ' direct' if m.directShaderWrite else ''))
                    if ok and a is not None and (a.flags & rd.ActionFlags.Drawcall):
                        hits.setdefault(m.eventId, set()).add('%s@%d' % (name, rid_int(tid)))
        P('== draws that passed at the points:')
        for eid in sorted(hits):
            P('  eid %d : %s' % (eid, ' '.join(sorted(hits[eid]))))
        infos = []
        for eid in sorted(hits):
            infos.append(dump_state(eid, ' '.join(sorted(hits[eid]))))
        seen = set()
        for info in infos:
            for tid in info.get('tex_ps', []):
                if (tid, info['eid']) in seen:
                    continue
                seen.add((tid, info['eid']))
                if tid in [rid_int(k) for k in tgts]:
                    continue
                P('== TEX stats eid %d tex %d' % (info['eid'], tid))
                tex_stats(byint[tid], info['eid'])
        json.dump(infos, open(os.path.join(OUTDIR, 'draws_hist.json'), 'w'), indent=1)
    elif PHASE == 'vsout':
        sigs = {}
        for e in [int(v) for v in os.environ.get('RD_VS', '950,960,1321,1028').split(',') if v.strip()]:
            ctrl.SetFrameEvent(e, True)
            st = ctrl.GetPipelineState()
            refl = st.GetShaderReflection(rd.ShaderStage.Vertex)
            prefl = st.GetShaderReflection(rd.ShaderStage.Pixel)
            mesh = ctrl.GetPostVSData(0, 0, rd.MeshDataStage.VSOut)
            sig = [{'name': s_.varName, 'sem': s_.semanticName, 'reg': s_.regIndex, 'comp': s_.compCount,
                    'type': str(s_.varType), 'sys': str(s_.systemValue)} for s_ in refl.outputSignature]
            psig = [{'name': s_.varName, 'reg': s_.regIndex, 'comp': s_.compCount} for s_ in prefl.inputSignature] if prefl else []
            P('---- VSOUT eid %d vs %d stride %d numIndices %d vbo %d ibo %s ioff %d istride %d' % (
                e, rid_int(st.GetShader(rd.ShaderStage.Vertex)), mesh.vertexByteStride, mesh.numIndices,
                mesh.vertexByteOffset, mesh.indexResourceId, mesh.indexByteOffset, mesh.indexByteStride))
            P('  vs out sig', sig)
            P('  ps in sig', psig)
            try:
                vb = bytes(ctrl.GetBufferData(mesh.vertexResourceId, mesh.vertexByteOffset, 0))
                fn = os.path.join(OUTDIR, 'vsout_e%d.bin' % e)
                open(fn, 'wb').write(vb)
                P('  vertex bytes %s %d' % (fn, len(vb)))
                if mesh.indexResourceId != rd.ResourceId.Null():
                    ib = bytes(ctrl.GetBufferData(mesh.indexResourceId, mesh.indexByteOffset, mesh.numIndices * mesh.indexByteStride))
                    fn = os.path.join(OUTDIR, 'vsidx_e%d.bin' % e)
                    open(fn, 'wb').write(ib)
                    P('  index bytes %s %d' % (fn, len(ib)))
            except Exception as ex:
                P('  read err', ex)
            sigs[e] = {'stride': mesh.vertexByteStride, 'numIndices': mesh.numIndices, 'istride': mesh.indexByteStride,
                       'sig': sig, 'psig': psig}
        json.dump(sigs, open(os.path.join(OUTDIR, 'vsout.json'), 'w'), indent=1)
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
            P('  steps %d -> %s' % (n, fn))
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
