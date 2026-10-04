# Track F link F12g (HPP-481; ROADMAP s122 item 391 (g)(4)): qrenderdoc --python rd_f12g.py
# Env: RD_CAP=<capture>  RD_OUT=<report txt>  RD_DIR=<dir for raw dumps>  RD_CHUNKS=<chunk,chunk,...> (chunk indices of the
#      dispatches of 380bb9d6 by the structured-data reader of F12f, docs/track-f/f12f/runs/rdsd_k0N_summary.txt)
#      RD_SPV0=<offline =0 SPIR-V of F12d>  RD_SPV1=<offline =1 SPIR-V of F12d>  RD_MAXD=<max dispatches to measure, default all>
# For every marked dispatch (EID found by the chunk index of its last API event, then checked by the sha256 of the raw module bytes):
#   pre  - state of every read-write resource of the dispatch at EID-1 (before the dispatch; data)
#   o1   - SetFrameEvent(EID, force) with the original module
#   o2   - EID-1 (force), then EID (force) again: second replay with the original module (control B)
#   r0   - ReplaceResource(module, BuildTargetShader(=0 bytes)): replacement neutrality (data, not a member of item 391)
#   r1   - ReplaceResource(module, BuildTargetShader(=1 bytes)): the measure, N_diff = texels of r1 != o1
#   o3   - RemoveReplacement, EID (force): the original again (data)
# Control A: raw module bytes in the capture == RD_SPV0 bytes (byte for byte, length and every byte).
# Every texture read-write resource: all mips/slices, sha256, texel size from bytes / (w*h*d) of mip 0; diff and zero texel counts.
# Every buffer read-write resource: sha256 of the bound range (whole buffer when the range is 0); diff in 4-byte words when <= 64 MiB.
# Raw dumps of every texture state go to RD_DIR (img_<eid>_<res>_<state>.bin) for the offline recount.  ASCII only; exits by os._exit.
import os, traceback, hashlib, time
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f12g/rd_f12g.txt')
DUMP = os.environ.get('RD_DIR', 'C:/kyty/f287/f12g/dump')
NL = chr(10)
out = open(OUT, 'w')
T0 = time.time()
BIG = 64 * 1024 * 1024


def P(*a):
    out.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    out.flush()


def rid_num(r):
    return int(str(r).split('::')[-1])


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    import renderdoc as rd
    os.makedirs(DUMP, exist_ok=True)
    spv0 = open(os.environ['RD_SPV0'], 'rb').read()
    spv1 = open(os.environ['RD_SPV1'], 'rb').read()
    P('spv0', os.environ['RD_SPV0'], len(spv0), sha(spv0))
    P('spv1', os.environ['RD_SPV1'], len(spv1), sha(spv1))
    chunks = [int(x) for x in os.environ['RD_CHUNKS'].split(',') if x.strip()]
    maxd = int(os.environ.get('RD_MAXD', '0') or 0)
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        P('open failed', st); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    P('capture', os.environ['RD_CAP'], 'opened')
    disp = []

    def walk(acts):
        for a in acts:
            if a.flags & rd.ActionFlags.Dispatch:
                disp.append(a)
            walk(a.children)
    walk(ctrl.GetRootActions())
    by_chunk = {}
    for a in disp:
        for ev in a.events:
            by_chunk.setdefault(ev.chunkIndex, a)
    P('dispatches', len(disp))
    targets = []
    for c in chunks:
        a = by_chunk.get(c)
        P('chunk', c, '-> eid', a.eventId if a is not None else 'NOT FOUND')
        if a is not None:
            targets.append(a)
    if maxd > 0:
        targets = targets[:maxd]
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    buffers = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}

    def rw_list():
        ps = ctrl.GetPipelineState()
        res = []
        used = ps.GetReadWriteResources(rd.ShaderStage.Compute)
        for u in used:
            d = getattr(u, 'descriptor', None)
            if d is not None:
                acc = u.access
                res.append((rid_num(d.resource), int(getattr(acc, 'index', -1)), int(getattr(acc, 'arrayElement', 0)),
                            int(getattr(d, 'byteOffset', 0)), int(getattr(d, 'byteSize', 0))))
            else:
                for r in u.resources:
                    res.append((rid_num(r.resourceId), int(u.bindPoint.bind) if hasattr(u, 'bindPoint') else -1, 0, 0, 0))
        out_ = []
        seen = set()
        for r in res:
            if r[0] == 0 or r in seen:
                continue
            seen.add(r)
            out_.append(r)
        return out_

    def read_state(rws):
        st = {}
        for (n, idx, ae, off, size) in rws:
            key = (n, off, size)
            if key in st:
                continue
            if n in textures:
                t = textures[n]
                parts = []
                for m in range(max(1, t.mips)):
                    for s in range(max(1, t.arraysize)):
                        parts.append(bytes(ctrl.GetTextureData(t.resourceId, rd.Subresource(m, s, 0))))
                data = b''.join(parts)
                st[key] = ('tex', data if len(data) <= BIG else None, len(parts[0]) if parts else 0, sha(data), len(data))
            elif n in buffers:
                b = buffers[n]
                data = bytes(ctrl.GetBufferData(b.resourceId, off, size))
                st[key] = ('buf', data if len(data) <= BIG else None, 0, sha(data), len(data))
            else:
                st[key] = ('unknown', b'', 0, sha(b''), 0)
            data = None
        return st

    def texel_size(n, mip0_bytes):
        t = textures[n]
        npx = max(1, t.width) * max(1, t.height) * max(1, t.depth)
        return mip0_bytes // npx if npx else 0

    def ndiff(a, b, unit):
        if unit <= 0 or len(a) != len(b):
            return -1
        if a == b:
            return 0
        c = 0
        for i in range(0, len(a), unit):
            if a[i:i + unit] != b[i:i + unit]:
                c += 1
        return c

    def nzero(a, unit):
        if unit <= 0:
            return -1
        z = bytes(unit)
        c = 0
        for i in range(0, len(a), unit):
            if a[i:i + unit] == z:
                c += 1
        return c

    for a in targets:
        eid = a.eventId
        P('=== DISPATCH eid', eid, 'name', a.GetName(ctrl.GetStructuredFile()))
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        shid = ps.GetShader(rd.ShaderStage.Compute)
        refl = ps.GetShaderReflection(rd.ShaderStage.Compute)
        raw = bytes(refl.rawBytes)
        P('shader', shid, 'entry', refl.entryPoint, 'encoding', refl.encoding, 'raw bytes', len(raw), 'sha', sha(raw))
        P('dims', 'x'.join(str(int(v)) for v in a.dispatchDimension), 'threads', 'x'.join(str(int(v)) for v in refl.dispatchThreadsDimension))
        ca = (raw == spv0)
        nd = sum(1 for i in range(min(len(raw), len(spv0))) if raw[i] != spv0[i]) if not ca else 0
        P('CONTROL_A', 'OK' if ca else 'FAIL', 'len_capture', len(raw), 'len_spv0', len(spv0), 'differing_bytes_in_common_length', nd)
        rws = rw_list()
        for (n, idx, ae, off, size) in rws:
            if n in textures:
                t = textures[n]
                P('RW tex', n, 'bind', idx, 'elem', ae, 'w', t.width, 'h', t.height, 'd', t.depth, 'mips', t.mips, 'arr', t.arraysize,
                  'fmt', t.format.Name(), 'bytes', t.byteSize)
            elif n in buffers:
                P('RW buf', n, 'bind', idx, 'elem', ae, 'len', buffers[n].length, 'off', off, 'size', size)
            else:
                P('RW unknown', n, 'bind', idx)
        states = {}
        ctrl.SetFrameEvent(eid - 1, True)
        states['pre'] = read_state(rws)
        ctrl.SetFrameEvent(eid, True)
        states['o1'] = read_state(rws)
        ctrl.SetFrameEvent(eid - 1, True)
        ctrl.SetFrameEvent(eid, True)
        states['o2'] = read_state(rws)
        built = {}
        for tag, blob in (('r0', spv0), ('r1', spv1)):
            nid, err = ctrl.BuildTargetShader(refl.entryPoint, rd.ShaderEncoding.SPIRV, blob, rd.ShaderCompileFlags(),
                                              rd.ShaderStage.Compute)
            P('build', tag, nid, 'errors', (err or '')[:1500].replace(NL, ' | '))
            if nid == rd.ResourceId.Null():
                P('BUILD_FAILED', tag)
                continue
            built[tag] = nid
            ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(eid - 1, True)
            ctrl.SetFrameEvent(eid, True)
            ps2 = ctrl.GetPipelineState()
            refl2 = ps2.GetShaderReflection(rd.ShaderStage.Compute)
            raw2 = bytes(refl2.rawBytes) if refl2 is not None else b''
            P('replaced', tag, 'bound shader', ps2.GetShader(rd.ShaderStage.Compute), 'raw sha', sha(raw2), 'len', len(raw2))
            states[tag] = read_state(rws)
            ctrl.RemoveReplacement(shid)
        ctrl.SetFrameEvent(eid - 1, True)
        ctrl.SetFrameEvent(eid, True)
        refl3 = ctrl.GetPipelineState().GetShaderReflection(rd.ShaderStage.Compute)
        P('after remove: raw sha', sha(bytes(refl3.rawBytes)))
        states['o3'] = read_state(rws)
        for tag, nid in built.items():
            ctrl.FreeTargetResource(nid)
        keys = list(states['o1'].keys())
        for key in keys:
            kind, b_o1, mip0, _sh, nbytes = states['o1'][key]
            n = key[0]
            unit = texel_size(n, mip0) if kind == 'tex' else 4
            line = ['RES', kind, n, 'off', key[1], 'size', key[2], 'bytes', nbytes, 'unit', unit]
            for s in ('pre', 'o1', 'o2', 'r0', 'r1', 'o3'):
                if s in states:
                    line += [s, states[s][key][3][:16]]
            P(*line)
            small = b_o1 is not None
            if kind == 'tex' and small:
                t = textures[n]
                for s in ('pre', 'o1', 'o2', 'r0', 'r1', 'o3'):
                    if s in states:
                        open(os.path.join(DUMP, 'img_%d_%d_%s.bin' % (eid, n, s)), 'wb').write(states[s][key][1])
            if small:
                for x, y in (('o1', 'o2'), ('o1', 'pre'), ('o1', 'r0'), ('o1', 'r1'), ('r0', 'r1'), ('o1', 'o3')):
                    if x in states and y in states:
                        P('  NDIFF', n, x, y, ndiff(states[x][key][1], states[y][key][1], unit), 'of', nbytes // unit if unit else -1)
                for s in ('pre', 'o1', 'r0', 'r1'):
                    if s in states:
                        P('  NZERO', n, s, nzero(states[s][key][1], unit))
            else:
                for x, y in (('o1', 'o2'), ('o1', 'pre'), ('o1', 'r0'), ('o1', 'r1'), ('r0', 'r1'), ('o1', 'o3')):
                    if x in states and y in states:
                        P('  EQUAL_SHA', n, x, y, states[x][key][3] == states[y][key][3])
        states = None
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
