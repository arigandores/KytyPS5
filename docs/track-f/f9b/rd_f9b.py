# F9b (HPP-411): qrenderdoc --python rd_f9b.py ; env RD_CAP, RD_OUT, RD_MODE.
# Modes:
#   list    - every action: EID, kind, name, outputs, depth; plus texture table (no per-event state)
#   hist    - pixel history: RD_TEX=<id> RD_PX=x,y [RD_EID=<eid>]
#   state   - pipeline state at events RD_EIDS=a,b,c : shaders, RTs, read-only/read-write resources, viewport
#   save    - save textures at events: RD_SAVE="eid:texid:mip:slice,..." RD_DIR=<dir>
#   pick    - pick pixel values: RD_PICK="eid:texid:x:y:mip,..."
# Writes 'done' and exits the process.
import os, traceback

OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f9/f9b/out.txt')
out = open(OUT, 'w', encoding='utf-8')
NL = chr(10)


def P(*a):
    out.write(' '.join(str(x) for x in a) + NL)
    out.flush()


def rid_int(r):
    return int(str(r).split('::')[-1])


def main():
    import renderdoc as rd
    CAP = os.environ['RD_CAP']
    mode = os.environ.get('RD_MODE', 'list')
    P('capture', CAP, 'mode', mode)
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(CAP, '', None) != rd.ResultCode.Succeeded:
        P('open failed')
        return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st)
        return 1
    sf = ctrl.GetStructuredFile()
    texs = {rid_int(t.resourceId): t for t in ctrl.GetTextures()}
    bufs = {rid_int(b.resourceId): b for b in ctrl.GetBuffers()}
    names = {rid_int(r.resourceId): r.name for r in ctrl.GetResources()}
    rid_of = {rid_int(t.resourceId): t.resourceId for t in ctrl.GetTextures()}
    for b in ctrl.GetBuffers():
        rid_of[rid_int(b.resourceId)] = b.resourceId

    def tdesc(i):
        t = texs.get(i)
        if t is None:
            b = bufs.get(i)
            if b is not None:
                return 'buf%d len=%d %s' % (i, b.length, names.get(i, ''))
            return 'res%d %s' % (i, names.get(i, ''))
        return 'tex%d %dx%dx%d a%d m%d %s %s' % (i, t.width, t.height, t.depth, t.arraysize, t.mips, t.format.Name(),
                                                names.get(i, ''))

    def walk(acts):
        for a in acts:
            yield a
            for x in walk(a.children):
                yield x

    if mode == 'list':
        for a in walk(ctrl.GetRootActions()):
            f = a.flags
            kind = ''
            if f & rd.ActionFlags.Drawcall: kind = 'DRAW'
            elif f & rd.ActionFlags.Dispatch: kind = 'DISP'
            elif f & rd.ActionFlags.Clear: kind = 'CLEAR'
            elif f & rd.ActionFlags.Copy: kind = 'COPY'
            elif f & rd.ActionFlags.Present: kind = 'PRESENT'
            elif f & rd.ActionFlags.PassBoundary: kind = 'PASS'
            if not kind:
                continue
            outs = [rid_int(o) for o in a.outputs if o != rd.ResourceId.Null()]
            dep = rid_int(a.depthOut) if a.depthOut != rd.ResourceId.Null() else 0
            extra = ''
            if kind == 'DRAW':
                extra = ' n=%d inst=%d' % (a.numIndices, a.numInstances)
            if kind == 'DISP':
                extra = ' grp=%s' % (tuple(a.dispatchDimension),)
            if kind in ('COPY',):
                extra = ' src=%d dst=%d' % (rid_int(a.copySource), rid_int(a.copyDestination))
            P('E%d %s %s outs=%s d=%d%s' % (a.eventId, kind, a.GetName(sf), outs, dep, extra))
        P('TEXTURES')
        for i in sorted(texs):
            P(tdesc(i))
    elif mode == 'hist':
        tid = int(os.environ['RD_TEX'])
        x, y = [int(v) for v in os.environ['RD_PX'].split(',')]
        eid = int(os.environ.get('RD_EID', '0'))
        if eid == 0:
            eid = max(a.eventId for a in walk(ctrl.GetRootActions()))
        ctrl.SetFrameEvent(eid, True)
        P('hist', tdesc(tid), 'px', x, y, 'at', eid)
        t = texs[tid]
        sub = rd.Subresource(0, 0, 0)
        hist = ctrl.PixelHistory(rid_of[tid], x, y, sub, t.format.compType)
        for m in hist:
            def col(mv):
                return '(%.4f %.4f %.4f %.4f)' % tuple(mv.col.floatValue[:4])
            P('E%d prim=%d frag=%d pass=%s pre=%s post=%s shout=%s flags=%s' % (
                m.eventId, m.primitiveID, m.fragIndex, m.Passed(), col(m.preMod), col(m.postMod), col(m.shaderOut),
                [n for n in ('sampleMasked', 'backfaceCulled', 'depthClipped', 'viewClipped', 'scissorClipped',
                             'shaderDiscarded', 'depthTestFailed', 'stencilTestFailed', 'predicationSkipped',
                             'unboundPS', 'directShaderWrite') if getattr(m, n, False)]))
    elif mode == 'state':
        for e in [int(v) for v in os.environ['RD_EIDS'].split(',') if v]:
            ctrl.SetFrameEvent(e, True)
            ps = ctrl.GetPipelineState()
            P('==== E%d' % e)
            for stg, sn in ((rd.ShaderStage.Vertex, 'VS'), (rd.ShaderStage.Pixel, 'PS'), (rd.ShaderStage.Compute, 'CS')):
                sh = ps.GetShader(stg)
                if sh == rd.ResourceId.Null():
                    continue
                refl = ps.GetShaderReflection(stg)
                ent = ps.GetShaderEntryPoint(stg)
                P(' %s %s %s entry=%s' % (sn, rid_int(sh), names.get(rid_int(sh), ''), ent))
                try:
                    for ro in ps.GetReadOnlyResources(stg, False):
                        r = ro.descriptor.resource
                        if r == rd.ResourceId.Null():
                            continue
                        P('  RO bind=%s %s view=%s mip=%d+%d' % (ro.access.index, tdesc(rid_int(r)),
                                                                 ro.descriptor.format.Name(), ro.descriptor.firstMip,
                                                                 ro.descriptor.numMips))
                    for rw in ps.GetReadWriteResources(stg, False):
                        r = rw.descriptor.resource
                        if r == rd.ResourceId.Null():
                            continue
                        P('  RW bind=%s %s off=%d len=%d' % (rw.access.index, tdesc(rid_int(r)),
                                                            rw.descriptor.byteOffset, rw.descriptor.byteSize))
                    for cb in ps.GetConstantBlocks(stg, False):
                        r = cb.descriptor.resource
                        if r == rd.ResourceId.Null():
                            continue
                        P('  CB bind=%s %s off=%d len=%d' % (cb.access.index, tdesc(rid_int(r)),
                                                            cb.descriptor.byteOffset, cb.descriptor.byteSize))
                except Exception as ex:
                    P('  res err', ex)
            try:
                for o in ps.GetOutputTargets():
                    r = o.resource
                    if r != rd.ResourceId.Null():
                        P('  OUT %s view=%s' % (tdesc(rid_int(r)), o.format.Name()))
                d = ps.GetDepthTarget()
                if d.resource != rd.ResourceId.Null():
                    P('  DEPTH %s' % tdesc(rid_int(d.resource)))
                vp = ps.GetViewport(0)
                P('  VP %.0f %.0f %.0f %.0f' % (vp.x, vp.y, vp.width, vp.height))
            except Exception as ex:
                P('  out err', ex)
    elif mode == 'save':
        d = os.environ['RD_DIR']
        for item in os.environ['RD_SAVE'].split(','):
            if not item:
                continue
            e, tid, mip, sl = [int(v) for v in item.split(':')]
            ctrl.SetFrameEvent(e, True)
            s = rd.TextureSave()
            s.resourceId = rid_of[tid]
            s.mip = mip
            s.slice.sliceIndex = sl
            s.alpha = rd.AlphaMapping.Discard
            s.destType = rd.FileType.PNG
            p = '%s/e%d_t%d_m%d_s%d.png' % (d, e, tid, mip, sl)
            r = ctrl.SaveTexture(s, p)
            P('save', p, r, tdesc(tid))
    elif mode == 'pick':
        for item in os.environ['RD_PICK'].split(','):
            if not item:
                continue
            e, tid, x, y, mip = [int(v) for v in item.split(':')]
            ctrl.SetFrameEvent(e, True)
            v = ctrl.PickPixel(rid_of[tid], x, y, rd.Subresource(mip, 0, 0), rd.CompType.Typeless)
            P('pick E%d t%d (%d,%d) m%d f=%s u=%s' % (e, tid, x, y, mip, tuple(v.floatValue[:4]),
                                                    tuple(v.uintValue[:4])))
    elif mode == 'buf':
        # RD_BUF="eid:bufid:offset:len,..." -> hex dwords
        for item in os.environ['RD_BUF'].split(','):
            if not item:
                continue
            e, bid, off, ln = [int(v) for v in item.split(':')]
            ctrl.SetFrameEvent(e, True)
            data = ctrl.GetBufferData(rid_of[bid], off, ln)
            P('buf E%d b%d off=%d len=%d' % (e, bid, off, ln))
            import struct
            n = len(data) // 4
            w = struct.unpack('<%dI' % n, bytes(data[:n * 4]))
            for i in range(0, n, 8):
                P('  [%3d] ' % i + ' '.join('%08x' % x for x in w[i:i + 8]))
    elif mode == 'bufdump':
        # RD_BUF="eid:bufid,..." -> RD_DIR/b<id>_e<eid>.bin (whole buffer)
        for item in os.environ['RD_BUF'].split(','):
            if not item:
                continue
            e, bid = [int(v) for v in item.split(':')]
            ctrl.SetFrameEvent(e, True)
            data = ctrl.GetBufferData(rid_of[bid], 0, 0)
            p = '%s/b%d_e%d.bin' % (os.environ['RD_DIR'], bid, e)
            open(p, 'wb').write(bytes(data))
            P('bufdump', p, len(data))
    elif mode == 'args':
        # every action whose name contains one of RD_NAMES (comma list): print the API chunk arguments
        wanted = [s for s in os.environ.get('RD_NAMES', 'FillBuffer,CopyBuffer,UpdateBuffer').split(',') if s]

        def sd(o, depth=0):
            if depth > 3:
                return '...'
            if o.NumChildren() > 0:
                return '{' + ', '.join('%s=%s' % (c.name, sd(c, depth + 1)) for c in
                                       [o.GetChild(k) for k in range(min(o.NumChildren(), 12))]) + '}'
            try:
                v = o.AsString()
                if v:
                    return v
            except Exception:
                pass
            for get in ('AsUInt', 'AsInt', 'AsFloat'):
                try:
                    return str(getattr(o, get)())
                except Exception:
                    pass
            return '?'

        for a in walk(ctrl.GetRootActions()):
            nm = a.GetName(sf)
            if not any(s in nm for s in wanted):
                continue
            for ev in a.events:
                ch = sf.chunks[ev.chunkIndex]
                P('E%d %s %s' % (ev.eventId, ch.name, sd(ch)))
    elif mode == 'dis':
        e = int(os.environ['RD_EID'])
        stg = {'PS': rd.ShaderStage.Pixel, 'VS': rd.ShaderStage.Vertex, 'CS': rd.ShaderStage.Compute}[
            os.environ.get('RD_STAGE', 'PS')]
        ctrl.SetFrameEvent(e, True)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(stg)
        pipe = ps.GetGraphicsPipelineObject() if stg != rd.ShaderStage.Compute else ps.GetComputePipelineObject()
        targets = ctrl.GetDisassemblyTargets(True)
        P('targets', list(targets))
        P('ro', [(r.name, r.fixedBindNumber, r.fixedBindSetOrSpace, str(r.textureType)) for r in refl.readOnlyResources])
        P('rw', [(r.name, r.fixedBindNumber, r.fixedBindSetOrSpace, str(r.textureType)) for r in refl.readWriteResources])
        txt = ctrl.DisassembleShader(pipe, refl, targets[0])
        out.write(txt)
        out.write(NL)
    P('done')
    ctrl.Shutdown()
    cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    out.write(traceback.format_exc())
out.close()
os._exit(code)
