# F9a: qrenderdoc --python rd_count.py ; RD_CAP=<capture>, RD_OUT=<file>. Counts the actions of a capture by flag (no
# per-draw state), writes one summary line and 'done', exits the process. ASCII only.
import os, traceback
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f9/rd_count.txt')
out = open(OUT, 'w')
def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    st = cap.OpenFile(os.environ['RD_CAP'], '', None)
    if st != rd.ResultCode.Succeeded:
        out.write('open failed %s' % st + chr(10)); return 1
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    if st != rd.ResultCode.Succeeded:
        out.write('replay failed %s' % st + chr(10)); return 1
    c = {'draw': 0, 'dispatch': 0, 'clear': 0, 'copy': 0, 'present': 0, 'other': 0}
    eids = []
    def walk(acts):
        for a in acts:
            f = a.flags
            if f & rd.ActionFlags.Drawcall: c['draw'] += 1
            elif f & rd.ActionFlags.Dispatch: c['dispatch'] += 1
            elif f & rd.ActionFlags.Clear: c['clear'] += 1
            elif f & rd.ActionFlags.Copy: c['copy'] += 1
            elif f & rd.ActionFlags.Present: c['present'] += 1
            elif not a.children: c['other'] += 1
            if not a.children: eids.append(a.eventId)
            walk(a.children)
    walk(ctrl.GetRootActions())
    seg = []; n = 0
    def walk2(acts):
        nonlocal n
        for a in acts:
            if a.flags & rd.ActionFlags.Drawcall: n += 1
            if a.flags & rd.ActionFlags.Present: seg.append('present@%d after %d draws' % (a.eventId, n)); n = 0
            walk2(a.children)
    walk2(ctrl.GetRootActions())
    out.write(' | '.join(seg) + ' | tail %d draws' % n + chr(10))
    out.write('capture %s draws %d dispatches %d clears %d copies %d presents %d other %d eid %d..%d' % (
        os.environ['RD_CAP'], c['draw'], c['dispatch'], c['clear'], c['copy'], c['present'], c['other'],
        min(eids) if eids else 0, max(eids) if eids else 0) + chr(10))
    out.write('done' + chr(10))
    ctrl.Shutdown(); cap.Shutdown()
    return 0
code = 2
try:
    code = main()
except BaseException:
    out.write(traceback.format_exc())
out.close()
os._exit(code)
