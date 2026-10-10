# F36a (HPP-758; section 0.4 caveat): sampler state bound to the PS be4c35a2031fd3f4 at the events RD_EIDS (no replacement):
# per used sampler descriptor - binding, compare function / UseComparison, filter. Reads UsedDescriptor.sampler (rd_f36a.py read
# .descriptor and printed '?'). Output RD_OUT json.  ASCII only; os._exit.
import os, json, traceback
OUT = os.environ['RD_OUT']


def main():
    import renderdoc as rd
    cap = rd.OpenCaptureFile()
    cap.OpenFile(os.environ['RD_CAP'], '', None)
    st, ctrl = cap.OpenCapture(rd.ReplayOptions(), None)
    res = {'cap': os.environ['RD_CAP'], 'events': []}
    for eid in [int(x) for x in os.environ['RD_EIDS'].split(',')]:
        ctrl.SetFrameEvent(eid, True)
        ps = ctrl.GetPipelineState()
        sm = []
        for u in ps.GetSamplers(rd.ShaderStage.Pixel):
            s = getattr(u, 'sampler', None)
            acc = getattr(u, 'access', None)
            if s is None:
                continue
            sm.append({'index': int(getattr(acc, 'index', -1)), 'elem': int(getattr(acc, 'arrayElement', 0)),
                       'compareFunction': str(getattr(s, 'compareFunction', '?')),
                       'UseComparison': bool(s.UseComparison()) if hasattr(s, 'UseComparison') else None,
                       'filter': str(getattr(s, 'filter', '?'))[:120],
                       'attrs': [a for a in dir(s) if not a.startswith('_')][:60]})
        res['events'].append({'eid': eid, 'samplers': sm})
    json.dump(res, open(OUT, 'w'), indent=1)
    ctrl.Shutdown(); cap.Shutdown()
    return 0


code = 2
try:
    code = main()
except BaseException:
    open(OUT + '.err', 'w').write(traceback.format_exc())
os._exit(code)
