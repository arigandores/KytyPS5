# Track F link F12g (HPP-481): data for the one-word difference of buffer 138 (bind 4) on eid 128281 of k03 (rd_f12g_k03.txt:276-282).
# qrenderdoc --python rd_f12g_b138.py ; Env: RD_CAP, RD_OUT, RD_EIDS=<eid,eid,...>, RD_BUF=<resource number>, RD_SPV1, RD_N=<replays>
# For every eid: pre (EID-1), then RD_N replays of the original module (EID-1 -> EID, force), then one replay with RD_SPV1 bytes;
# prints the non-zero 4-byte words of the buffer (index, hex value) and sha256 of the output image 21829 for every replay.
# ASCII only; exits by os._exit.
import os, traceback, hashlib, time
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f12g/rd_f12g_b138.txt')
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
    eids = [int(x) for x in os.environ['RD_EIDS'].split(',') if x.strip()]
    bufn = int(os.environ.get('RD_BUF', '138'))
    nrep = int(os.environ.get('RD_N', '4'))
    spv1 = open(os.environ['RD_SPV1'], 'rb').read()
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(os.environ['RD_CAP'], '', None) != rd.ResultCode.Succeeded:
        P('open failed'); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        P('replay failed', st); return 1
    buffers = {rid_num(b.resourceId): b for b in ctrl.GetBuffers()}
    textures = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}
    b = buffers[bufn]
    t = textures[21829]

    def nz():
        data = bytes(ctrl.GetBufferData(b.resourceId, 0, 0))
        w = struct.unpack('<%dI' % (len(data) // 4), data)
        return [(i, '%08x' % v) for i, v in enumerate(w) if v != 0][:16], len(data)

    def img():
        return hashlib.sha256(bytes(ctrl.GetTextureData(t.resourceId, rd.Subresource(0, 0, 0)))).hexdigest()[:16]

    for eid in eids:
        ctrl.SetFrameEvent(eid - 1, True)
        P('eid', eid, 'pre', nz(), 'img', img())
        for k in range(nrep):
            ctrl.SetFrameEvent(eid - 1, True)
            ctrl.SetFrameEvent(eid, True)
            P('eid', eid, 'orig', k + 1, nz(), 'img', img())
        ps = ctrl.GetPipelineState()
        shid = ps.GetShader(rd.ShaderStage.Compute)
        refl = ps.GetShaderReflection(rd.ShaderStage.Compute)
        nid, err = ctrl.BuildTargetShader(refl.entryPoint, rd.ShaderEncoding.SPIRV, spv1, rd.ShaderCompileFlags(), rd.ShaderStage.Compute)
        if nid == rd.ResourceId.Null():
            P('BUILD_FAILED', err)
        else:
            ctrl.ReplaceResource(shid, nid)
            for k in range(2):
                ctrl.SetFrameEvent(eid - 1, True)
                ctrl.SetFrameEvent(eid, True)
                P('eid', eid, 'r1', k + 1, nz(), 'img', img())
            ctrl.RemoveReplacement(shid)
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
