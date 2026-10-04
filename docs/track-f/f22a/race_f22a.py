# F22a (HPP-576, item 474(e)(2)): race stand - a second thread flips one page of the destination between READWRITE and
# READONLY while the main thread calls ReadFile into the buffer (the emulator's case: the GPU thread re-protects guest
# pages while a guest read is in flight, fileSystem.cpp:839-:843). Question: can ReadFile return TRUE with fewer bytes
# than requested (not at EOF), or FALSE with lpNumberOfBytesRead != 0, so that ReadGuestWithRetry (retry only when
# bytes_read == 0) would hand the guest a short read?  No game, no emulator.
# Usage: python race_f22a.py <work dir> <out.txt> <reads per size>
import ctypes, ctypes.wintypes as W, collections, os, sys, threading, time

work, out, nreads = sys.argv[1], sys.argv[2], int(sys.argv[3])
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
k32.VirtualAlloc.restype = ctypes.c_void_p
k32.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, W.DWORD, W.DWORD]
k32.VirtualProtect.argtypes = [ctypes.c_void_p, ctypes.c_size_t, W.DWORD, ctypes.POINTER(W.DWORD)]
k32.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, W.DWORD]
k32.CreateFileW.restype = W.HANDLE
k32.CreateFileW.argtypes = [W.LPCWSTR, W.DWORD, W.DWORD, ctypes.c_void_p, W.DWORD, W.DWORD, W.HANDLE]
k32.ReadFile.argtypes = [W.HANDLE, ctypes.c_void_p, W.DWORD, ctypes.POINTER(W.DWORD), ctypes.c_void_p]
k32.SetFilePointerEx.argtypes = [W.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), W.DWORD]
k32.CloseHandle.argtypes = [W.HANDLE]
PAGE = 4096
lines = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    lines.append(s)
    print(s, flush=True)


os.makedirs(work, exist_ok=True)
path = os.path.join(work, 'f22a_race.bin')
FSIZE = 16 << 20
data = os.urandom(FSIZE)
with open(path, 'wb') as f:
    f.write(data)
P('F22a race stand: reads per size', nreads, '; file', FSIZE, 'bytes; Windows', sys.getwindowsversion().build)
for size, flag in ((64 << 10, 0), (1 << 20, 0), (8 << 20, 0), (8 << 20, 0x10000000), (8 << 20, 0x20000000)):
    pages = size // PAGE + 1
    buf = k32.VirtualAlloc(None, pages * PAGE, 0x3000, 0x04)
    flip = buf + (pages // 2) * PAGE
    stop = [False]
    flips = [0]

    def flipper():
        old = W.DWORD(0)
        while not stop[0]:
            k32.VirtualProtect(flip, PAGE, 0x02, ctypes.byref(old))
            k32.VirtualProtect(flip, PAGE, 0x04, ctypes.byref(old))
            flips[0] += 1

    th = threading.Thread(target=flipper)
    th.start()
    h = k32.CreateFileW(path, 0x80000000, 7, None, 3, flag, None)
    cls = collections.Counter()
    errs = collections.Counter()
    partial_landed = 0
    t0 = time.time()
    for i in range(nreads):
        off = (i * 3 * PAGE) % (FSIZE - size)
        off -= off % PAGE
        k32.SetFilePointerEx(h, off, None, 0)
        got = W.DWORD(0xFFFFFFFF)
        ok = k32.ReadFile(h, buf, size, ctypes.byref(got), None)
        e = ctypes.get_last_error() if not ok else 0
        if ok and got.value == size:
            cls['ok_full'] += 1
        elif ok:
            cls['ok_short'] += 1
        elif got.value == 0:
            cls['fail_zero'] += 1
            errs[e] += 1
        else:
            cls['fail_nonzero'] += 1
            errs[e] += 1
    stop[0] = True
    th.join()
    k32.CloseHandle(h)
    old = W.DWORD(0)
    k32.VirtualProtect(flip, PAGE, 0x04, ctypes.byref(old))
    k32.VirtualFree(buf, 0, 0x8000)
    P('size %-8d flag 0x%08x reads %d flips %d wall %.1f s classes %s errors %s' % (size, flag, nreads, flips[0], time.time() - t0, dict(cls), dict(errs)))
os.remove(path)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('RACE DONE')
