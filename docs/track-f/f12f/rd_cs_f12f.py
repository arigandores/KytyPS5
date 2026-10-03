# Track F link F12f (HPP-480; ROADMAP s122 item 391 (g)(4)): qrenderdoc --python rd_cs_f12f.py
# RD_CAP=<capture> RD_OUT=<file> RD_MARK=<sha256,sha256,...>.
# For every dispatch of the capture: the event id, the dispatch size, the sha256 and the size of the RAW module bytes of the bound
# compute shader (ShaderReflection.rawBytes, the SPIR-V as the application passed it), and the mark '380b' when the sha256 is one of
# RD_MARK (the offline SPIR-V of 380bb9d636390bae of F12d section 5, KytyPS5 docs/track-f/f12d.md); a summary line and 'done'; exits the
# process (os._exit).  DATA ONLY: the search for the dispatches of 380bb9d6 and controls A/B are F12g's (item 391 (g)(4)).  ASCII only.
import os, traceback, hashlib
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f12f/rd_cs.txt')
MARK = set(x.strip().lower() for x in os.environ.get('RD_MARK', '').split(',') if x.strip())
out = open(OUT, 'w')
NL = chr(10)


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + NL); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        out.write('replay failed %s' % st + NL); return 1
    out.write('capture %s' % os.environ['RD_CAP'] + NL)
    out.write('mark %s' % ','.join(sorted(MARK)) + NL)
    disp = []

    def walk(acts):
        for a in acts:
            if a.flags & rd.ActionFlags.Dispatch:
                disp.append(a)
            walk(a.children)
    walk(ctrl.GetRootActions())
    seen = {}
    marked = []
    for a in disp:
        ctrl.SetFrameEvent(a.eventId, False)
        ps = ctrl.GetPipelineState()
        refl = ps.GetShaderReflection(rd.ShaderStage.Compute)
        if refl is None:
            sha, n = 'none', 0
        else:
            raw = bytes(refl.rawBytes)
            sha, n = hashlib.sha256(raw).hexdigest(), len(raw)
        dims = 'x'.join(str(int(v)) for v in a.dispatchDimension)
        m = '380b' if sha in MARK else '-'
        if m == '380b':
            marked.append(a.eventId)
        seen[sha] = seen.get(sha, 0) + 1
        out.write('DISPATCH eid=%d dims=%s cs_sha=%s bytes=%d mark=%s name=%s' % (
            a.eventId, dims, sha, n, m, a.GetName(ctrl.GetStructuredFile()).replace(' ', '_')) + NL)
    for sha in sorted(seen):
        out.write('CS sha=%s dispatches=%d mark=%s' % (sha, seen[sha], '380b' if sha in MARK else '-') + NL)
    out.write('SUMMARY dispatches %d distinct_cs %d marked_380b %d marked_eids %s' % (
        len(disp), len(seen), len(marked), ','.join(str(e) for e in marked) if marked else '-') + NL)
    out.write('done' + NL)
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    out.write(traceback.format_exc())
out.close()
os._exit(code)
