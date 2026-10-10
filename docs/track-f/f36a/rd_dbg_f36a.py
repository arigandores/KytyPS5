# F36a (HPP-758): debug (not scoring) - where is "before the event" in the replay. For RD_EID: the action holding it, its event
# list (eventId, chunk name), the previous action (eventId, name, flags); then rt0 / depth sha and the diag-free orig state at:
# eid - 1, the first event of the action's group - 1, the previous action's eventId, eid. ASCII only; os._exit.
import os, sys, json, time, hashlib, traceback
OUT = os.environ['RD_OUT']
LOGF = open(OUT, 'w')
NL = chr(10)


def P(*a):
    LOGF.write(' '.join(str(x) for x in a) + NL)
    LOGF.flush()


def rid_num(r):
    try:
        return int(str(r).split('::')[-1])
    except Exception:
        return -1


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    cap.OpenFile(os.environ['RD_CAP'], '', None)
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    sdf = ctrl.GetStructuredFile()
    eid = int(os.environ['RD_EID'])
    found = []

    def walk(al):
        for a in al:
            if any(e.eventId == eid for e in a.events) or a.eventId == eid:
                found.append(a)
            walk(a.children)
    walk(ctrl.GetRootActions())
    a = found[0]
    P('action', a.eventId, a.GetName(sdf), 'flags', str(a.flags))
    for e in a.events:
        P('  event', e.eventId, sdf.chunks[e.chunkIndex].name if e.chunkIndex < len(sdf.chunks) else '?')
    pv = None
    P('previous action', pv.eventId if pv else None, pv.GetName(sdf) if pv else None, str(pv.flags) if pv else None)
    if pv:
        for e in pv.events:
            P('  prev event', e.eventId, sdf.chunks[e.chunkIndex].name if e.chunkIndex < len(sdf.chunks) else '?')
    ctrl.SetFrameEvent(eid, True)
    ps = ctrl.GetPipelineState()
    rt0 = ps.GetOutputTargets()[0].resource
    dt = ps.GetDepthTarget().resource
    tex = {rid_num(t.resourceId): t for t in ctrl.GetTextures()}

    def snap(tag, e):
        ctrl.SetFrameEvent(e, True)
        x = bytes(ctrl.GetTextureData(rt0, rd.Subresource(0, 0, 0)))
        y = bytes(ctrl.GetTextureData(dt, rd.Subresource(0, 0, 0)))
        P('state', tag, e, 'rt0', hashlib.sha256(x).hexdigest()[:16], 'depth', hashlib.sha256(y).hexdigest()[:16])
        return x
    first = a.events[0].eventId
    s1 = snap('eid-1', eid - 1)
    s2 = snap('group_first-1', first - 1)
    s3 = snap('prev_action', pv.eventId) if pv else None
    s4 = snap('eid', eid)
    s5 = snap('eid-1 again', eid - 1)
    P('done')
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    LOGF.write(traceback.format_exc())
LOGF.close()
os._exit(code)
