"""Auditor microbenchmark (no game, no build): cost of QueryThreadCycleTime on a real handle of the calling thread,
and whether the running quantum is included (cycle delta across a busy loop ~ wall)."""
import ctypes, time, statistics
from ctypes import wintypes
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
OpenThread = k32.OpenThread; OpenThread.restype = wintypes.HANDLE
OpenThread.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
QTCT = k32.QueryThreadCycleTime; QTCT.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_ulonglong)]; QTCT.restype = wintypes.BOOL
GCTI = k32.GetCurrentThreadId; GCTI.restype = wintypes.DWORD
h = OpenThread(0x0040 | 0x0002 | 0x0008, False, GCTI())  # QUERY_INFORMATION | SUSPEND_RESUME | GET_CONTEXT
c = ctypes.c_ulonglong()
N = 200000
def loop(fn):
    t0 = time.perf_counter_ns()
    for _ in range(N):
        fn()
    return (time.perf_counter_ns() - t0) / N
res_q, res_b = [], []
for rep in range(5):
    res_q.append(loop(lambda: QTCT(h, ctypes.byref(c))))
    res_b.append(loop(lambda: GCTI()))
q, b = statistics.median(res_q), statistics.median(res_b)
print('QueryThreadCycleTime per call (python loop) ns', round(q, 1), 'baseline GetCurrentThreadId', round(b, 1), 'diff ns', round(q - b, 1))
# does the cycle count include the running quantum?  busy-spin 2 us .. 50 us and compare cycle delta with wall
QPF = time.perf_counter_ns
# TSC freq estimate from cycle time over a 200 ms busy loop
a = ctypes.c_ulonglong(); z = ctypes.c_ulonglong()
QTCT(h, ctypes.byref(a)); t0 = QPF()
while QPF() - t0 < 200_000_000:
    pass
QTCT(h, ctypes.byref(z)); t1 = QPF()
f = (z.value - a.value) / (t1 - t0)
print('cycles per ns over a 200 ms busy loop', round(f, 4))
for us in (2, 5, 20):
    ratios = []
    for _ in range(2000):
        QTCT(h, ctypes.byref(a)); t0 = QPF()
        while QPF() - t0 < us * 1000:
            pass
        QTCT(h, ctypes.byref(z)); t1 = QPF()
        ratios.append((z.value - a.value) / f / (t1 - t0))
    print('busy %2d us: cycle-ns / wall-ns median %.3f  p10 %.3f  p90 %.3f  zeros %d' % (us, statistics.median(ratios),
          sorted(ratios)[200], sorted(ratios)[1800], sum(1 for r in ratios if r == 0)))
