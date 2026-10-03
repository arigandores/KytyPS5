# F11a (HPP-455), member (4) of ROADMAP p.370(g): the compute shaders of the 8 dispatches EID 3399-3455 of the
# enemy_final capture. qrenderdoc --python rd_f11a.py ; read only (the capture is not modified), exits by os._exit.
# For every EID: the action name, the bound compute shader (ResourceId, resource name, entry point) and the raw
# SPIR-V bytes of the bound module -> rd/cs_e<EID>.spv and its sha256 (matched to a guest hash by match_f11a.py).
# Env: RD_CAP (default C:/kyty/f287/f7a/enemy_final_600.rdc), RD_OUT (default C:/kyty/f287/f11a/rd).
import os
import hashlib
import traceback

CAP = os.environ.get('RD_CAP', 'C:/kyty/f287/f7a/enemy_final_600.rdc')
OUTDIR = os.environ.get('RD_OUT', 'C:/kyty/f287/f11a/rd')
EIDS = [3399, 3413, 3419, 3427, 3433, 3441, 3447, 3455]
os.makedirs(OUTDIR, exist_ok=True)
out = open(os.path.join(OUTDIR, 'rd_f11a.txt'), 'w', encoding='utf-8')


def P(*a):
    out.write(' '.join(str(x) for x in a) + chr(10))
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
    P('capture:', CAP)
    rd.InitialiseReplay(rd.GlobalEnvironment(), [])
    cap = rd.OpenCaptureFile()
    if cap.OpenFile(CAP, '', None) != rd.ResultCode.Succeeded:
        P('open failed')
        return 1
    res, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if res != rd.ResultCode.Succeeded:
        P('replay failed', res)
        return 1
    sf = ctrl.GetStructuredFile()
    resnames = {r.resourceId: r.name for r in ctrl.GetResources()}
    actions = []

    def walk(acts):
        for a in acts:
            actions.append(a)
            walk(a.children)

    walk(ctrl.GetRootActions())
    byeid = {a.eventId: a for a in actions}
    for eid in EIDS:
        a = byeid.get(eid)
        if a is None:
            P('EID', eid, 'no action')
            continue
        ctrl.SetFrameEvent(eid, True)
        st = ctrl.GetPipelineState()
        sid = st.GetShader(rd.ShaderStage.Compute)
        refl = st.GetShaderReflection(rd.ShaderStage.Compute)
        raw = bytes(refl.rawBytes) if refl is not None else b''
        sha = hashlib.sha256(raw).hexdigest() if raw else '-'
        if raw:
            open(os.path.join(OUTDIR, 'cs_e%d.spv' % eid), 'wb').write(raw)
        P('EID', eid, 'action', a.GetName(sf), 'dispatch', tuple(a.dispatchDimension),
          'cs', str(sid), 'name', resnames.get(sid, ''), 'entry', refl.entryPoint if refl is not None else '-',
          'encoding', str(refl.encoding) if refl is not None else '-', 'spv_bytes', len(raw), 'sha256', sha)
    P('done')
    ctrl.Shutdown()
    cap.Shutdown()
    return 0


try:
    hide_ui()
    rc = main()
except Exception:
    P('EXCEPTION', traceback.format_exc())
    rc = 2
out.close()
os._exit(rc if isinstance(rc, int) else 0)
