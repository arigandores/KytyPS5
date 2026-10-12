# F47e (HPP-810): replay of the f47_rd captures (B34 splash blocks; ROADMAP s122 item 708(d) with items 715, 718, 721-724, 731, 734, 735).
# qrenderdoc --python rd_f47e.py ; exits by os._exit. Form of F7b rd_f7b.py. Env:
#   RD_CAP    capture path (C:/kyty/f287/f47d/f47_rd_kNN.rdc)
#   RD_OUT    output dir (C:/kyty/f287/f47e/rd/<kNN>)
#   RD_PHASE  "inv"   - actions, presents, the copy into the swapchain, PNG + raw of the presented guest image after the last event (G' (3))
#             "hist"  - RD_PTS json [{"name","tex","x","y"}]: pixel history of every point on the named texture (resource id int), all mods
#             "state" - RD_EIDS "e1,e2": pipeline state, shaders (SPIR-V saved), bound resources, blend, viewport/scissor, vertex out
#             "save"  - RD_SAVE "tex@eid,tex@eid": texture PNG + raw bytes (mip 0) after the event
#             "debug" - RD_DBG "eid:x,y;..." pixel debug traces
import os, sys, traceback, json

CAP = os.environ.get('RD_CAP', '')
OUTDIR = os.environ.get('RD_OUT', 'C:/kyty/f287/f47e/rd')
PHASE = os.environ.get('RD_PHASE', 'inv')
os.makedirs(OUTDIR, exist_ok=True)
out = open(os.path.join(OUTDIR, 'rd_%s.txt' % PHASE), 'w', encoding='utf-8')


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

    tbyint = {rid_int(k): k for k in textures}
    bbyint = {rid_int(k): k for k in buffers}

    def texdesc(rid):
        t = textures.get(rid)
        if t is None:
            return 'res(%s)' % rid_int(rid)
        return 'tex %d %dx%dx%d arr=%d mips=%d fmt=%s ms=%d cf=%s name=%s' % (
            rid_int(rid), t.width, t.height, t.depth, t.arraysize, t.mips, t.format.Name(), t.msSamp, t.creationFlags, resnames.get(rid, ''))

    actions = []

    def walk(acts):
        for a in acts:
            actions.append(a)
            walk(a.children)

    walk(ctrl.GetRootActions())
    byeid = {a.eventId: a for a in actions}
    presents = [a for a in actions if a.flags & rd.ActionFlags.Present]
    last = actions[-1].eventId
    P('actions %d, last eid %d, presents %s' % (len(actions), last, [(a.eventId, a.GetName(sf)) for a in presents]))

    def pv(v):
        return '(%.6f %.6f %.6f %.6f)' % tuple(v.floatValue[:4])

    def pu(v):
        return '(%08x %08x %08x %08x)' % tuple(v.uintValue[:4])

    def save_tex(rid, eid, mip=0, tag=''):
        t = textures[rid]
        ctrl.SetFrameEvent(eid, True)
        ts = rd.TextureSave()
        ts.resourceId = rid
        ts.destType = rd.FileType.PNG
        ts.mip = mip
        ts.alpha = rd.AlphaMapping.Discard
        fn = os.path.join(OUTDIR, 'tex_%d_e%d_m%d%s.png' % (rid_int(rid), eid, mip, tag))
        ok = ctrl.SaveTexture(ts, fn)
        P('  saved png %s %s' % (fn, ok))
        try:
            raw = bytes(ctrl.GetTextureData(rid, rd.Subresource(mip, 0, 0)))
            rfn = os.path.join(OUTDIR, 'tex_%d_e%d_m%d%s.raw' % (rid_int(rid), eid, mip, tag))
            open(rfn, 'wb').write(raw)
            P('  saved raw %s %d bytes (%s)' % (rfn, len(raw), texdesc(rid)))
        except Exception as e:
            P('  raw err', e)

    if PHASE == 'inv':
        kinds = {}
        for a in actions:
            for f in ('Drawcall', 'Dispatch', 'Clear', 'Copy', 'Resolve', 'Present', 'PassBoundary'):
                if a.flags & getattr(rd.ActionFlags, f):
                    kinds[f] = kinds.get(f, 0) + 1
        P('kinds', kinds)
        P('textures %d buffers %d' % (len(textures), len(buffers)))
        P('--- last 40 actions:')
        for a in actions[-40:]:
            outs = [rid_int(o) for o in a.outputs if o != rd.ResourceId.Null()]
            P('  eid %d flags=%s name=%s outs=%s depth=%s copySrc=%s copyDst=%s' % (
                a.eventId, int(a.flags), a.GetName(sf), outs, rid_int(a.depthOut) if a.depthOut != rd.ResourceId.Null() else '-',
                rid_int(a.copySource) if a.copySource != rd.ResourceId.Null() else '-',
                rid_int(a.copyDestination) if a.copyDestination != rd.ResourceId.Null() else '-'))
        # copies / blits whose destination is used by the present, and the present's own resources
        cands = []
        for a in actions:
            if a.flags & (rd.ActionFlags.Copy | rd.ActionFlags.Resolve) and a.copyDestination != rd.ResourceId.Null():
                cands.append(a)
        P('--- copies (last 12):')
        for a in cands[-12:]:
            P('  eid %d %s src=%s dst=%s' % (a.eventId, a.GetName(sf), texdesc(a.copySource) if a.copySource in textures else rid_int(a.copySource),
                                             texdesc(a.copyDestination) if a.copyDestination in textures else rid_int(a.copyDestination)))
        P('--- big colour textures (w >= 1280):')
        for rid, t in textures.items():
            if t.width >= 1280 and t.height >= 720:
                P('  ' + texdesc(rid))
        info = {'last': last, 'presents': [a.eventId for a in presents]}
        for p in presents:
            P('present eid %d src=%s dst=%s outs=%s' % (p.eventId, rid_int(p.copySource) if p.copySource != rd.ResourceId.Null() else '-',
                                                       rid_int(p.copyDestination) if p.copyDestination != rd.ResourceId.Null() else '-',
                                                       [rid_int(o) for o in p.outputs if o != rd.ResourceId.Null()]))
        # the guest image shown: source of the last copy before the (last) present
        pe = presents[-1].eventId if presents else last
        prev = [a for a in cands if a.eventId < pe]
        if prev:
            g = prev[-1]
            info['show_copy'] = g.eventId
            info['show_src'] = rid_int(g.copySource)
            info['show_dst'] = rid_int(g.copyDestination)
            P('shown guest image: copy eid %d src %s -> dst %s' % (g.eventId, texdesc(g.copySource), texdesc(g.copyDestination)))
            if g.copySource in textures:
                save_tex(g.copySource, last, 0, '_shown')
            if g.copyDestination in textures:
                save_tex(g.copyDestination, last, 0, '_dst')
        json.dump(info, open(os.path.join(OUTDIR, 'inv.json'), 'w'), indent=1)
    elif PHASE == 'hist':
        pts = json.load(open(os.environ['RD_PTS']))
        heid = int(os.environ.get('RD_HEID', '0') or 0)
        ctrl.SetFrameEvent(heid if heid > 0 else last, True)
        P('history at event %d' % (heid if heid > 0 else last))
        res_all = []
        for p in pts:
            tid = tbyint[int(p['tex'])]
            X, Y = int(p['x']), int(p['y'])
            hist = ctrl.PixelHistory(tid, X, Y, rd.Subresource(int(p.get('mip', 0)), int(p.get('slice', 0)), 0), rd.CompType.Typeless)
            P('-- HIST %s (%d,%d) on %s : %d mods' % (p['name'], X, Y, texdesc(tid), len(hist)))
            mods = []
            for m in hist:
                a = byeid.get(m.eventId)
                flags = ''.join(f for f, c in ((' depthFail', m.depthTestFailed), (' stencilFail', m.stencilTestFailed),
                                               (' discard', m.shaderDiscarded), (' culled', m.backfaceCulled),
                                               (' clip', m.depthClipped or m.viewClipped or m.scissorClipped),
                                               (' direct', m.directShaderWrite), (' unbound', m.unboundPS)) if c)
                P('   eid %d %s passed=%s prim=%d frag=%d pre=%s out=%s post=%s preU=%s outU=%s postU=%s flags:%s' % (
                    m.eventId, a.GetName(sf) if a else '?', m.Passed(), m.primitiveID, m.fragIndex, pv(m.preMod.col),
                    pv(m.shaderOut.col), pv(m.postMod.col), pu(m.preMod.col), pu(m.shaderOut.col), pu(m.postMod.col), flags))
                mods.append({'eid': m.eventId, 'name': a.GetName(sf) if a else '?', 'passed': bool(m.Passed()), 'prim': m.primitiveID,
                             'frag': m.fragIndex, 'pre': list(m.preMod.col.floatValue[:4]), 'out': list(m.shaderOut.col.floatValue[:4]),
                             'post': list(m.postMod.col.floatValue[:4]), 'preU': list(m.preMod.col.uintValue[:4]),
                             'outU': list(m.shaderOut.col.uintValue[:4]), 'postU': list(m.postMod.col.uintValue[:4]),
                             'flags': flags.strip(), 'draw': bool(a is not None and (a.flags & rd.ActionFlags.Drawcall)),
                             'clear': bool(a is not None and (a.flags & rd.ActionFlags.Clear)),
                             'copy': bool(a is not None and (a.flags & (rd.ActionFlags.Copy | rd.ActionFlags.Resolve))),
                             'dispatch': bool(a is not None and (a.flags & rd.ActionFlags.Dispatch))})
            res_all.append({'pt': p, 'mods': mods})
        json.dump(res_all, open(os.path.join(OUTDIR, 'hist_%s.json' % os.environ.get('RD_HTAG', 'x')), 'w'), indent=1)
    elif PHASE == 'act':
        def dump(obj, depth, pre):
            try:
                n = obj.NumChildren()
            except Exception:
                n = 0
            name = obj.name
            try:
                if n == 0:
                    bt = obj.type.basetype
                    if str(bt).endswith('Resource'):
                        v = obj.data.basic.id
                    elif str(bt).endswith('Float'):
                        v = obj.data.basic.d
                    elif str(bt).endswith('String'):
                        v = obj.data.str
                    elif str(bt).endswith('Boolean'):
                        v = obj.data.basic.b
                    elif str(bt).endswith('SignedInteger'):
                        v = obj.data.basic.i
                    else:
                        v = obj.data.basic.u
                    P('%s%s = %s' % (pre, name, v))
                    return
            except Exception as e:
                P('%s%s = ? (%s)' % (pre, name, e))
                return
            P('%s%s {%d}' % (pre, name, n))
            if depth > 6:
                return
            for i in range(min(n, 64)):
                dump(obj.GetChild(i), depth + 1, pre + '  ')
        for eid in [int(v) for v in os.environ.get('RD_EIDS', '').split(',') if v.strip()]:
            a = byeid.get(eid)
            if a is None:
                P('==== ACT %d: no action' % eid)
                continue
            outs = [rid_int(o) for o in a.outputs if o != rd.ResourceId.Null()]
            P('==== ACT %d %s flags=%d outs=%s depth=%s copySrc=%s copyDst=%s parent=%s' % (
                eid, a.GetName(sf), int(a.flags), outs, rid_int(a.depthOut) if a.depthOut != rd.ResourceId.Null() else '-',
                texdesc(a.copySource) if a.copySource in textures else rid_int(a.copySource),
                texdesc(a.copyDestination) if a.copyDestination in textures else rid_int(a.copyDestination),
                a.parent.GetName(sf) if a.parent else '-'))
            for ev in a.events:
                if ev.eventId == eid:
                    dump(sf.chunks[ev.chunkIndex], 0, '  ')
        rng = os.environ.get('RD_RANGE', '')
        if rng:
            lo, hi = [int(v) for v in rng.split('-')]
            P('---- actions in %d..%d' % (lo, hi))
            for a in actions:
                if lo <= a.eventId <= hi:
                    outs = [rid_int(o) for o in a.outputs if o != rd.ResourceId.Null()]
                    P('  eid %d flags=%d %s outs=%s copySrc=%s copyDst=%s' % (a.eventId, int(a.flags), a.GetName(sf), outs,
                      rid_int(a.copySource) if a.copySource != rd.ResourceId.Null() else '-',
                      rid_int(a.copyDestination) if a.copyDestination != rd.ResourceId.Null() else '-'))
    elif PHASE == 'usage':
        allres = {}
        allres.update(tbyint)
        allres.update(bbyint)
        for rs in [int(v) for v in os.environ.get('RD_RES', '').split(',') if v.strip()]:
            rid = allres.get(rs)
            if rid is None:
                P('==== USAGE %d: unknown resource' % rs)
                continue
            us = ctrl.GetUsage(rid)
            kinds = {}
            for u in us:
                kinds[str(u.usage)] = kinds.get(str(u.usage), 0) + 1
            P('==== USAGE %d %s : %d uses, kinds %s' % (rs, texdesc(rid) if rid in textures else 'buf', len(us), sorted(kinds.items())))
            for u in us:
                un = str(u.usage).split('.')[-1]
                if not any(k in un for k in ('Resource', 'Constants', 'VertexBuffer', 'IndexBuffer', 'Indirect')) or 'RW' in un:
                    a = byeid.get(u.eventId)
                    P('   eid %d %s %s' % (u.eventId, un, a.GetName(sf) if a else '?'))
            P('   first use eid %s last use eid %s' % (us[0].eventId if us else '-', us[-1].eventId if us else '-'))
    elif PHASE == 'vsout':
        for eid in [int(v) for v in os.environ.get('RD_EIDS', '').split(',') if v.strip()]:
            ctrl.SetFrameEvent(eid, True)
            a = byeid[eid]
            st = ctrl.GetPipelineState()
            refl = st.GetShaderReflection(rd.ShaderStage.Vertex)
            mo = ctrl.GetPostVSData(0, 0, rd.MeshDataStage.VSOut)
            P('==== VSOUT %d %s numIndices %d stride %d count %d' % (eid, a.GetName(sf), a.numIndices, mo.vertexByteStride, mo.numIndices))
            data = bytes(ctrl.GetBufferData(mo.vertexResourceId, mo.vertexByteOffset, 0))
            import struct as _st
            nv = min(mo.numIndices, 64)
            idx = []
            if mo.indexResourceId != rd.ResourceId.Null():
                ib = bytes(ctrl.GetBufferData(mo.indexResourceId, mo.indexByteOffset, 0))
                w = mo.indexByteStride
                for i in range(nv):
                    idx.append(_st.unpack_from('<I' if w == 4 else '<H', ib, i * w)[0])
            else:
                idx = list(range(nv))
            nf = mo.vertexByteStride // 4
            P('  indices %s' % idx)
            for v in sorted(set(idx)):
                off = v * mo.vertexByteStride
                if off + mo.vertexByteStride <= len(data):
                    vals = _st.unpack_from('<%df' % nf, data, off)
                    P('  v%d %s' % (v, ' '.join('%.6g' % x for x in vals)))
            sig = [(s_.varName, s_.compCount) for s_ in refl.outputSignature]
            P('  sig %s' % sig)
    elif PHASE == 'state':
        infos = []
        for eid in [int(v) for v in os.environ.get('RD_EIDS', '').split(',') if v.strip()]:
            a = byeid[eid]
            ctrl.SetFrameEvent(eid, True)
            st = ctrl.GetPipelineState()
            vk = ctrl.GetVulkanPipelineState()
            P('==== STATE EID %d %s numIndices=%d numInstances=%d indexOffset=%d vertexOffset=%d flags=%d' % (
                eid, a.GetName(sf), a.numIndices, a.numInstances, a.indexOffset, a.vertexOffset, int(a.flags)))
            info = {'eid': eid, 'name': a.GetName(sf), 'numIndices': a.numIndices, 'outs': [], 'ro': [], 'rw': []}
            for i, o in enumerate(a.outputs):
                if o != rd.ResourceId.Null():
                    P('  RT[%d] %s' % (i, texdesc(o)))
                    info['outs'].append([i, rid_int(o)])
            if a.depthOut != rd.ResourceId.Null():
                P('  DS %s' % texdesc(a.depthOut))
            try:
                for i, b in enumerate(vk.colorBlend.blends[:8]):
                    P('  blend[%d] en=%s src=%s dst=%s op=%s | a src=%s dst=%s op=%s mask=%x logic=%s/%s' % (
                        i, b.enabled, b.colorBlend.source, b.colorBlend.destination, b.colorBlend.operation,
                        b.alphaBlend.source, b.alphaBlend.destination, b.alphaBlend.operation, b.writeMask,
                        b.logicOperationEnabled, b.logicOperation))
                info['blend'] = [[bool(b.enabled), str(b.colorBlend.source), str(b.colorBlend.destination), str(b.colorBlend.operation),
                                  str(b.alphaBlend.source), str(b.alphaBlend.destination), str(b.alphaBlend.operation), int(b.writeMask)]
                                 for b in vk.colorBlend.blends[:8]]
                P('  blendConst %s' % (list(vk.colorBlend.blendFactor),))
                ds = vk.depthStencil
                P('  depth test=%s write=%s func=%s stencil=%s' % (ds.depthTestEnable, ds.depthWriteEnable, ds.depthFunction, ds.stencilTestEnable))
                r = vk.rasterizer
                P('  raster cull=%s frontCCW=%s fill=%s' % (r.cullMode, r.frontCCW, r.fillMode))
                for v in vk.viewportScissor.viewportScissors[:2]:
                    P('  viewport (%.1f %.1f %.1f %.1f) scissor (%d %d %d %d)' % (v.vp.x, v.vp.y, v.vp.width, v.vp.height,
                                                                              v.scissor.x, v.scissor.y, v.scissor.width, v.scissor.height))
            except Exception as e:
                P('  vk state err', e)
            for stage, sname in ((rd.ShaderStage.Vertex, 'vs'), (rd.ShaderStage.Pixel, 'ps'), (rd.ShaderStage.Compute, 'cs')):
                refl = st.GetShaderReflection(stage)
                if refl is None:
                    continue
                sid = st.GetShader(stage)
                info[sname] = rid_int(sid)
                spv = os.path.join(OUTDIR, '%s_%d.spv' % (sname, rid_int(sid)))
                if not os.path.exists(spv):
                    open(spv, 'wb').write(bytes(refl.rawBytes))
                P('  %s shader %d spirv %s bytes %d entry %s' % (sname, rid_int(sid), spv, len(refl.rawBytes), st.GetShaderEntryPoint(stage)))
                for s_ in refl.outputSignature:
                    P('    out sig name=%s reg=%d comp=%d sys=%s type=%s' % (s_.varName, s_.regIndex, s_.compCount, s_.systemValue, s_.varType))
                try:
                    for ro in st.GetReadOnlyResources(stage):
                        for d in ro.access if hasattr(ro, 'access') else []:
                            pass
                except Exception:
                    pass
                try:
                    for used in st.GetReadOnlyResources(stage, True):
                        r_ = used.descriptor.resource
                        P('    RO idx=%s res=%s' % (used.access.index, texdesc(r_) if r_ in textures else ('buf %d' % rid_int(r_))))
                        info['ro'].append([sname, used.access.index, rid_int(r_)])
                    for used in st.GetReadWriteResources(stage, True):
                        r_ = used.descriptor.resource
                        P('    RW idx=%s res=%s' % (used.access.index, texdesc(r_) if r_ in textures else ('buf %d' % rid_int(r_))))
                        info['rw'].append([sname, used.access.index, rid_int(r_)])
                    for used in st.GetConstantBlocks(stage, True):
                        r_ = used.descriptor.resource
                        P('    CB idx=%s res=%s off=%d size=%d' % (used.access.index, rid_int(r_), used.descriptor.byteOffset, used.descriptor.byteSize))
                except Exception as e:
                    P('    bindings err', e)
            infos.append(info)
        json.dump(infos, open(os.path.join(OUTDIR, 'state_%s.json' % os.environ.get('RD_STAG', 'x')), 'w'), indent=1)
    elif PHASE == 'save':
        for item in os.environ.get('RD_SAVE', '').split(','):
            if not item.strip():
                continue
            t, e = item.split('@')
            save_tex(tbyint[int(t)], int(e), 0, '')
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
