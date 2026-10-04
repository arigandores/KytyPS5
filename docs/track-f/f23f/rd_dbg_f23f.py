# F23f (HPP-592): debug of the chunk -> event mapping (no replacement, no readback): for the chunks of RD_CHUNKS prints every
# action / event whose chunkIndex equals it (event id, action name, depth) and the structured chunk name; plus counts.  ASCII only.
import os, traceback
OUT = os.environ.get('RD_OUT', 'C:/kyty/f287/f23f/runs/dbg.txt')
out = open(OUT, 'w')
NL = chr(10)


def main():
    import renderdoc as rd
    want = set(int(x) for x in os.environ['RD_CHUNKS'].split(','))
    cap = rd.OpenCaptureFile()
    cap.OpenFile(os.environ['RD_CAP'], '', None)
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    sdf = ctrl.GetStructuredFile()
    for c in sorted(want):
        out.write('chunk %d name %s' % (c, sdf.chunks[c].name if c < len(sdf.chunks) else '?') + NL)
    nact = [0]
    hits = []

    def walk(acts, depth):
        for a in acts:
            nact[0] += 1
            for ev in a.events:
                if ev.chunkIndex in want:
                    hits.append((ev.chunkIndex, ev.eventId, a.eventId, depth, a.GetName(sdf), int(a.flags)))
            walk(a.children, depth + 1)
    walk(ctrl.GetRootActions(), 0)
    out.write('actions %d' % nact[0] + NL)
    for h in sorted(hits):
        out.write('HIT chunk %d event %d action %d depth %d flags %x name %s' % h + NL)
    # draws with the same name around: first 5 draws of the frame with their events' chunk indices
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
