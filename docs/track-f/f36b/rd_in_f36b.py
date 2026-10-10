# F36b (HPP-759): debug of the inputs that rd_f36b.py could not compare (N = -1): textures 22482 and 25514 of be4c35a2031fd3f4 events
# in f12_rd_k03. Per event (RD_EV eids) and arm (orig, orig2, def, sens): SetFrameEvent(pre_eid) and read every mip / slice of the
# two textures twice; print length and sha256 of each read, the format and size of the texture. ASCII only; exits by os._exit.
import os, sys, json, time, hashlib, traceback
OUT = os.environ['RD_OUT']
NL = chr(10)
CAP_SHA = 'ebff0feeb90b9b35c7aecbd6fc542fb6ded352504b70442b9172f533a571cb96'
ARMDIR = 'C:/kyty/f287/f36a/arms/ps_be4c35a2031fd3f4_%s.spv'
TEX = [22482, 25514, 27059, 30739]


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def rid(r):
    try:
        return int(str(r).split('::')[-1])
    except Exception:
        return -1


def main():
    import renderdoc as rd
    res = {'events': []}
    cap = rd.OpenCaptureFile()
    cap.OpenFile(os.environ['RD_CAP'], '', None)
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    grp = {}

    def walk(al):
        for a in al:
            evl = [e.eventId for e in a.events]
            for e in evl + [a.eventId]:
                grp[e] = min(evl + [a.eventId])
            walk(a.children)
    walk(ctrl.GetRootActions())
    tex = {rid(t.resourceId): t for t in ctrl.GetTextures()}
    res['tex'] = {n: {'fmt': str(tex[n].format.Name()), 'w': tex[n].width, 'h': tex[n].height, 'mips': tex[n].mips, 'arr': tex[n].arraysize,
                      'msamp': tex[n].msSamp} for n in TEX if n in tex}
    PS = rd.ShaderStage.Pixel
    for eid in json.loads(os.environ['RD_EV']):
        pre = grp[eid] - 1
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        shid = ps.GetShader(PS)
        entry = ps.GetShaderReflection(PS).entryPoint
        r = {'eid': eid, 'pre': pre, 'arms': {}}
        for arm in ('orig', 'def', 'sens', 'orig2'):
            nid = None
            if arm in ('def', 'sens'):
                nid, err = ctrl.BuildTargetShader(entry, rd.ShaderEncoding.SPIRV, open(ARMDIR % arm, 'rb').read(), rd.ShaderCompileFlags(), PS)
                ctrl.ReplaceResource(shid, nid)
            ctrl.SetFrameEvent(pre, True)
            a = {}
            for n in TEX:
                if n not in tex:
                    continue
                t = tex[n]
                for m in range(max(1, t.mips)):
                    for s in range(max(1, t.arraysize)):
                        x = [bytes(ctrl.GetTextureData(t.resourceId, rd.Subresource(m, s, 0))) for _ in range(2)]
                        a['t%d_m%d_s%d' % (n, m, s)] = [(len(y), sha(y)) for y in x]
            r['arms'][arm] = a
            if nid is not None:
                ctrl.RemoveReplacement(shid)
                ctrl.FreeTargetResource(nid)
        res['events'].append(r)
        json.dump(res, open(OUT, 'w'), sort_keys=True, indent=0)
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    open(OUT + '.log', 'a').write(traceback.format_exc())
os._exit(code)
