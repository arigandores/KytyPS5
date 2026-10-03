# F13b (HPP-483): shader replacement in replay for the final pass of f13_rd (EID 1247, PS ResourceId 237, RT 5692).
# Template: C:/kyty/scripts/rd_probe.py (RenderDoc pixel debug does not take this PS: FragmentBarycentricKHR).
# Variants of ps_237.spvasm (raw ids, spirv-dis --raw-id of the PS taken from the capture by rd_f13b.py flow):
#   ident  - the same module reassembled (control: replacement machinery keeps the output)
#   probe  - output (%731, %732, %733, %743): the scene after the reversible tonemap (r, g, b) and the fade weight (bitcast
#            of %565 = CB dword at byte 12 of the PS constant block) at the point of the fade lerp
#   nofade - the three fade weights %743/%745/%747 replaced by float 0.0: the composite without the fade
# qrenderdoc --python rd_f13b_probe.py ; exits by os._exit. Output: rd/rd_f13b_probe.txt
import os, sys, re, traceback, subprocess

CAP = os.environ.get('RD_CAP', 'C:/kyty/f287/f13a/f13_rd.rdc')
OUTDIR = os.environ.get('RD_OUT', 'C:/kyty/f287/f13b/rd')
ASM = os.path.join(OUTDIR, 'ps_237.spvasm')
EID = 1247
ORIG = 237
RT = 5692
SPIRV_AS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-as.exe'
PTS = [(1920, 1080), (100, 100), (3700, 2000), (1920, 200), (600, 1800)]
out = open(os.path.join(OUTDIR, 'rd_f13b_probe.txt'), 'w', encoding='utf-8')


def P(*a):
    out.write(' '.join(str(x) for x in a) + '\n')
    out.flush()


def variant(lines, kind):
    res = []
    bound = None
    for l in lines:
        m = re.match(r'; Bound: (\d+)', l)
        if m:
            bound = int(m.group(1))
    zero = None
    for l in lines:
        m = re.match(r'\s*%(\d+) = OpConstant %2 0$', l)
        if m:
            zero = int(m.group(1))
            break
    nid = bound
    done = 0
    for l in lines:
        s = l.strip()
        if kind == 'probe':
            if s == 'OpStore %13 %1266':
                done += 1
                continue  # the probe store below replaces the final store
            res.append(l)
            if s.startswith('%748 = '):
                res.append('%%%d = OpCompositeConstruct %%3 %%731 %%732 %%733 %%743' % nid)
                res.append('OpStore %%13 %%%d' % nid)
                nid += 1
                done += 1
            continue
        if kind == 'nofade':
            m = re.match(r'%(743|745|747) = OpBitcast %2 %565$', s)
            if m:
                res.append('%%%s = OpCopyObject %%2 %%%d' % (m.group(1), zero))
                done += 1
                continue
        res.append(l)
    text = '\n'.join(res)
    text = re.sub(r'; Bound: \d+', '; Bound: %d' % (nid + 1), text)
    need = {'ident': 0, 'probe': 2, 'nofade': 3}[kind]
    return text, done == need, zero


def main():
    import renderdoc as rd
    lines = open(ASM, encoding='utf-8').read().split('\n')
    rd.InitialiseReplay(rd.GlobalEnvironment(), [])
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(CAP, '', None) != rd.ResultCode.Succeeded:
        P('open failed')
        return 1
    res, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if res != rd.ResultCode.Succeeded:
        P('replay failed', res)
        return 1
    rid = lambda r: int(str(r).split('::')[-1])
    orig_id = [r.resourceId for r in ctrl.GetResources() if rid(r.resourceId) == ORIG][0]
    tex = [t for t in ctrl.GetTextures() if rid(t.resourceId) == RT][0]
    sub = rd.Subresource(0, 0, 0)

    def report(tag):
        ctrl.SetFrameEvent(EID, True)
        mn, mx = ctrl.GetMinMax(tex.resourceId, sub, rd.CompType.Typeless)
        P('%-7s RT %d after EID %d: min=(%s) max=(%s)' % (tag, RT, EID, ' '.join('%.5f' % v for v in mn.floatValue[:4]),
                                                         ' '.join('%.5f' % v for v in mx.floatValue[:4])))
        for (x, y) in PTS:
            pv = ctrl.PickPixel(tex.resourceId, x, y, sub, rd.CompType.Typeless)
            P('   pixel (%d,%d) = (%s)' % (x, y, ' '.join('%.5f' % v for v in pv.floatValue[:4])))

    report('orig')
    for kind in ('ident', 'probe', 'nofade', 'ident'):
        text, ok, zero = variant(lines, kind)
        if not ok:
            P(kind, 'patch sites not found', 'zero id', zero)
            continue
        asm = os.path.join(OUTDIR, 'ps_237_%s.spvasm' % kind)
        spv = os.path.join(OUTDIR, 'ps_237_%s.spv' % kind)
        open(asm, 'w', encoding='utf-8', newline='\n').write(text)
        r = subprocess.run([SPIRV_AS, '--target-env', 'vulkan1.3', asm, '-o', spv], capture_output=True, text=True)
        if r.returncode != 0:
            P(kind, 'spirv-as failed', r.stderr[:800])
            continue
        new_id, errors = ctrl.BuildTargetShader('main', rd.ShaderEncoding.SPIRV, open(spv, 'rb').read(),
                                                rd.ShaderCompileFlags(), rd.ShaderStage.Pixel)
        if new_id == rd.ResourceId.Null():
            P(kind, 'build failed', errors[:800])
            continue
        ctrl.ReplaceResource(orig_id, new_id)
        report(kind)
        ctrl.RemoveReplacement(orig_id)
        ctrl.FreeTargetResource(new_id)
    report('restored')
    P('done')
    ctrl.Shutdown()
    cap.Shutdown()
    rd.ShutdownReplay()
    return 0


code = 2
try:
    code = main()
except BaseException:
    P(traceback.format_exc())
out.close()
os._exit(code)
