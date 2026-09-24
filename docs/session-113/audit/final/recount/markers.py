# Stream a log (and optional stdout file) counting lines containing marker substrings.
import sys, json
MARK = [b'GpuWaitSlow', b'GpuHangAbort', b'AsyncPipelines: skipped draw', b'--- Error ---', b'--- Fatal Error ---',
        b'--- std::terminate ---', b'--- abort() ---', b'Unhandled exception', b'BdaNarrowMiss', b'MISMATCH',
        b'PriorityStall:', b'GpuIdlePrio:', b'GpuClockPin:', b'BufferGc:', b'GateArm:', b'Gate: ', b'DeviceLost',
        b'device lost', b'BdaNarrow', b'GpuMarker']
res = {}
for path in sys.argv[1:]:
    c = {m.decode(): 0 for m in MARK}; first = {}
    try:
        with open(path, 'rb') as f:
            for line in f:
                if line.startswith(b'FrameTrace'):
                    continue
                for m in MARK:
                    if m in line:
                        k = m.decode(); c[k] += 1
                        if k not in first: first[k] = line[:260].decode('latin1').rstrip()
    except FileNotFoundError:
        c = 'missing'
    res[path] = {'counts': {k: v for k, v in c.items() if v} if isinstance(c, dict) else c, 'first': first}
print(json.dumps(res, indent=1))
