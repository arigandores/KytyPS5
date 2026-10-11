# Track F link F42a (HPP-779, ROADMAP s122 item 694(g)(3)): replay arms of row F20 on f12_rd_k03 (method of F12g
# rd_f12g_b138.py: SetFrameEvent(EID - 1) -> SetFrameEvent(EID), buffer 138 before and after).
# qrenderdoc --python rd_f42a.py ; Env: RD_CAP, RD_OUT, RD_EID, RD_N (replays per arm), RD_SEED (arm order of a round),
#   RD_BUF (138), RD_TEX (21829), RD_WORD (32824), RD_MODS="name=path;name=path;..." (modules for the replaced arms),
#   RD_DUMP=<path> - dump mode: write the SPIR-V of the compute shader at RD_EID (the snapshot module) and stop.
# Arm 'o' = the snapshot module without a replacement; every other arm = BuildTargetShader(bytes) + ReplaceResource.
# Per replay one line: eid, round, arm, P0 (non-zero words of the buffer at EID - 1), the value of RD_WORD after EID,
# the non-zero words after (first 16), sha256[:16] of the output image. ASCII only; exits by os._exit.
import os, traceback, hashlib, time
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f42a/replay/rd_f42a.txt')
NL = chr(10)
out = open(OUT, 'w')
T0 = time.time()


def P(*a):
    out.write(('[%7.1f] ' % (time.time() - T0)) + ' '.join(str(x) for x in a) + NL)
    out.flush()


def rid_num(r):
    return int(str(r).split('::')[-1])


def main():
    import renderdoc as rd
    import struct
    eid = int(os.environ['RD_EID'])
    nrep = int(os.environ.get('RD_N', '20'))
    seed = int(os.environ.get('RD_SEED', '1'))
    bufn = int(os.environ.get('RD_BUF', '138'))
    texn = int(os.environ.get('RD_TEX', '21829'))
    wordi = int(os.environ.get('RD_WORD', '32824'))
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    buffers = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    b = buffers[bufn]
    t = textures[texn]
    ctrl.SetFrameEvent(eid, True)
    ps = ctrl.GetPipelineState()
    shid = ps.GetShader(rd.ShaderStage.Compute)
    refl = ps.GetShaderReflection(rd.ShaderStage.Compute)
    raw = bytes(refl.rawBytes)
    P('eid', eid, 'shader', rid_num(shid), 'entry', refl.entryPoint, 'raw_bytes', len(raw), 'raw_sha256',
      hashlib.sha256(raw).hexdigest())
    if os.environ.get('RD_DUMP'):
        open(os.environ['RD_DUMP'], 'wb').write(raw)
        P('dumped', os.environ['RD_DUMP'])
        P('done')
        ctrl.Shutdown(); cap.Shutdown()
        return 0

    built = {}
    for item in os.environ.get('RD_MODS', '').split(';'):
        if not item.strip():
            continue
        name, path = item.split('=', 1)
        data = open(path, 'rb').read()
        nid, err = ctrl.BuildTargetShader(refl.entryPoint, rd.ShaderEncoding.SPIRV, data, rd.ShaderCompileFlags(),
                                          rd.ShaderStage.Compute)
        if nid == rd.ResourceId.Null():
            P('BUILD_FAILED', name, err)
            return 1
        built[name] = nid
        P('built', name, path, 'sha256', hashlib.sha256(data).hexdigest(), 'id', rid_num(nid))
    arms = ['o'] + sorted(built)

    def words():
        data = bytes(ctrl.GetBufferData(b.resourceId, 0, 0))
        return struct.unpack('<%dI' % (len(data) // 4), data)

    def img():
        return hashlib.sha256(bytes(ctrl.GetTextureData(t.resourceId, rd.Subresource(0, 0, 0)))).hexdigest()[:16]

    state = (seed * 2654435761 + 1) & 0xffffffff

    def nxt():
        nonlocal state
        state ^= (state << 13) & 0xffffffff
        state ^= state >> 17
        state ^= (state << 5) & 0xffffffff
        return state

    current = None
    for k in range(nrep):
        order = list(arms)
        for i in range(len(order) - 1, 0, -1):
            j = nxt() % (i + 1)
            order[i], order[j] = order[j], order[i]
        for arm in order:
            if current != arm:
                if current is not None and current != 'o':
                    ctrl.RemoveReplacement(shid)
                if arm != 'o':
                    ctrl.ReplaceResource(shid, built[arm])
                current = arm
            ctrl.SetFrameEvent(eid - 1, True)
            pre = words()
            p0 = sum(1 for v in pre if v != 0)
            ctrl.SetFrameEvent(eid, True)
            w = words()
            nz = [(i, '%08x' % v) for i, v in enumerate(w) if v != 0][:16]
            P('eid', eid, 'round', k + 1, 'arm', arm, 'p0_nonzero', p0, 'word', '%08x' % w[wordi], 'nz', nz,
              'img', img())
    if current is not None and current != 'o':
        ctrl.RemoveReplacement(shid)
    for nid in built.values():
        ctrl.FreeTargetResource(nid)
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
