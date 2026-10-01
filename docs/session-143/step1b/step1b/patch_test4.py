"""Link 1b (HPP-321), after the stopped counted run: the suite reads in 1 MB chunks everywhere (part A line "S.CHUNK = 1 << 26"
-> 1 << 20; the chunk edges stay tested by s1 at 37 bytes), and two fixtures for the survivors seen: rpt_vke (a report with a
[Vulkan][W] line is not a validation stop) and vs_kind (a line carrying two markers: only the "--- Error ---" one changes
class).  Each anchor must hit exactly once."""
p = 'C:/kyty/s143/test_sc143.py'
t = open(p, 'rb').read().decode('utf-8')
reps = [
    ("S.CHUNK = 1 << 26\n", "S.CHUNK = 1 << 20     # link 1b: 64 MB read buffers per small fixture file made the suite slow; edges: s1\n"),
    ("S.profile(P143)\nS.CHUNK = 1 << 20     # link 1b: a 64 MB read buffer per small fixture file costs ~14 ms each; chunk edges: s1\n",
     "S.profile(P143)\n"),
    ("ok &= case('C5i the class is read by the report in profile 143 for a V too', e['marks'][0]['cls'] == 'VALIDATION_STOP')\n",
     "ok &= case('C5i the class is read by the report in profile 143 for a V too', e['marks'][0]['cls'] == 'VALIDATION_STOP')\n"
     "e = wstop('C5l', ['--- Build ---', 'v0', '--- Error ---', '[Vulkan][W][1]: a warning', ' in a.cpp:1'])\n"
     "ok &= case('C5l a report with a [Vulkan][W] line (not E) is not a validation stop -> K1', e['outcome'] == 'K1')\n"
     "e = wstop('C5m', ['GpuHangAbort: --- Error ---', '[Vulkan][E][1]: x', ' in a.cpp:1'])\n"
     "ok &= case('C5m a line carrying GpuHangAbort: and --- Error ---: only the --- Error --- mark becomes VALIDATION_STOP',\n"
     "           sorted((m['kind'], m['cls']) for m in e['marks']) == [('--- Error ---', 'VALIDATION_STOP'), ('GpuHangAbort:', 'K2')])\n"),
]
for a, b in reps:
    n = t.count(a)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, a[:90]))
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('utf-8'))
print('patched %d' % len(reps))
