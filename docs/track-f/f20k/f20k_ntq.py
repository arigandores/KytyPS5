# F20k (HPP-630, Red Team): cost of NtQuerySystemInformation(SystemProcessInformation) with a 2 MiB buffer and of
# CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD) on this machine - the calls the KYTY_DIAG_B32 sampler makes
# (diagB32.cpp KernelQuery / M5Refresh). Measurement only, no game.
import ctypes, time, statistics, sys
from ctypes import wintypes

ntdll = ctypes.WinDLL('ntdll')
k32 = ctypes.WinDLL('kernel32')
NtQSI = ntdll.NtQuerySystemInformation
NtQSI.argtypes = [wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG, ctypes.POINTER(wintypes.ULONG)]
NtQSI.restype = ctypes.c_long

size = 2 << 20
buf = ctypes.create_string_buffer(size)
need = wintypes.ULONG(0)
st = NtQSI(5, buf, size, ctypes.byref(need))
if st == ctypes.c_long(0xC0000004).value:
    size = need.value + (256 << 10)
    buf = ctypes.create_string_buffer(size)
    st = NtQSI(5, buf, size, ctypes.byref(need))
print('status=0x%08x need=%d buf=%d' % (st & 0xffffffff, need.value, size))

# count processes / threads
off = 0; nproc = 0; nthr = 0
raw = buf.raw
while True:
    nxt = int.from_bytes(raw[off:off+4], 'little')
    nt = int.from_bytes(raw[off+4:off+8], 'little')
    nproc += 1; nthr += nt
    if nxt == 0: break
    off += nxt
print('processes=%d threads=%d' % (nproc, nthr))

def bench(fn, n):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter_ns(); fn(); ts.append(time.perf_counter_ns() - t0)
    ts.sort()
    return ts

def q():
    NtQSI(5, buf, size, ctypes.byref(need))

TH32CS_SNAPTHREAD = 0x4
k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
def snap():
    h = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    k32.CloseHandle(h)

for name, fn, n in (('NtQuerySystemInformation(5)', q, 200), ('CreateToolhelp32Snapshot(THREAD)', snap, 50)):
    ts = bench(fn, n)
    us = [t / 1000 for t in ts]
    print('%s n=%d min_us=%.0f p50_us=%.0f p90_us=%.0f max_us=%.0f mean_us=%.0f' % (
        name, n, us[0], us[len(us)//2], us[int(len(us)*0.9)], us[-1], statistics.mean(us)))
