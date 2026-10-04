# F22a (HPP-576, ROADMAP s122 item 474(e)(2)): host stand - what Win32 ReadFile does when the destination buffer has a
# page that user mode may not write (the form of the emulator's GPU write tracking: VirtualProtect of guest pages).
# No game, no emulator: a temp file in <work dir>, a VirtualAlloc buffer, ctypes calls only.
# Per case: ReadFile return, lpNumberOfBytesRead, GetLastError, the file pointer after the call, how many bytes of the
# writable pages before / after the protected page received file data (the rest stays 0xCC), and then the emulator's
# fallback (ReadGuestWithRetry, 58b6c5ad:src/kernel/fileSystem.cpp:762): Seek(pos), ReadFile into a host buffer, memcpy
# (here: unprotect + memmove - the tracker's handler does the unprotect in the emulator).
# Usage: python stand_f22a.py <work dir> <out.txt>
import ctypes, ctypes.wintypes as W, os, sys

work, out = sys.argv[1], sys.argv[2]
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
MEM_COMMIT_RESERVE, MEM_RELEASE = 0x3000, 0x8000
PROT = {'READWRITE': 0x04, 'READONLY': 0x02, 'NOACCESS': 0x01, 'GUARD_RW': 0x104}
GENERIC_READ, OPEN_EXISTING = 0x80000000, 3
SHARE = 7
FLAGS = {'cached': 0, 'random': 0x10000000, 'nobuf': 0x20000000}

lines = []


def P(*a):
    s = ' '.join(str(x) for x in a)
    lines.append(s)
    print(s, flush=True)


def make_file(path, size):
    data = bytes(((i * 7 + (i >> 12)) & 0xFF) | 1 for i in range(size))  # never 0xCC-only pattern; byte i is known
    with open(path, 'wb') as f:
        f.write(data)
    return data


def tell(h):
    pos = ctypes.c_longlong(0)
    k32.SetFilePointerEx(h, 0, ctypes.byref(pos), 1)
    return pos.value


def case(name, path, data, flag, nbytes, pages, bad_page, prot, start=0):
    size = pages * PAGE
    buf = k32.VirtualAlloc(None, size, MEM_COMMIT_RESERVE, PROT['READWRITE'])
    ctypes.memset(buf, 0xCC, size)
    old = W.DWORD(0)
    if bad_page is not None:
        k32.VirtualProtect(buf + bad_page * PAGE, PAGE, PROT[prot], ctypes.byref(old))
    h = k32.CreateFileW(path, GENERIC_READ, SHARE, None, OPEN_EXISTING, FLAGS[flag], None)
    if start:
        k32.SetFilePointerEx(h, start, None, 0)
    got = W.DWORD(0xFFFFFFFF)
    ctypes.set_last_error(0)
    ok = k32.ReadFile(h, buf, nbytes, ctypes.byref(got), None)
    err = ctypes.get_last_error() if not ok else 0
    pos_after = tell(h)
    if bad_page is not None:
        k32.VirtualProtect(buf + bad_page * PAGE, PAGE, PROT['READWRITE'], ctypes.byref(old))
    mem = ctypes.string_at(buf, size)
    want = data[start:start + nbytes]
    landed_before = landed_after = 0
    nw = len(want)  # < nbytes when the request runs past EOF
    lim = bad_page * PAGE if bad_page is not None else nw
    for i in range(min(lim, nw)):
        if mem[i] == want[i]:
            landed_before += 1
    if bad_page is not None:
        for i in range((bad_page + 1) * PAGE, nw):
            if mem[i] == want[i]:
                landed_after += 1
    in_bad = 0
    if bad_page is not None:
        for i in range(bad_page * PAGE, min((bad_page + 1) * PAGE, nw)):
            if mem[i] == want[i]:
                in_bad += 1
    # emulator fallback: only when bytes_read == 0 and the request is not at EOF
    fb = '-'
    if got.value == 0 and nbytes != 0 and len(data) - start > 0:
        k32.SetFilePointerEx(h, start, None, 0)
        tmp = ctypes.create_string_buffer(nbytes)
        got2 = W.DWORD(0)
        ok2 = k32.ReadFile(h, tmp, nbytes, ctypes.byref(got2), None)
        ctypes.memmove(buf, tmp, got2.value)
        mem2 = ctypes.string_at(buf, got2.value)
        fb = 'ok2=%d got2=%d equal=%d pos2=%d' % (ok2, got2.value, int(mem2 == want[:got2.value]), tell(h))
    elif got.value != 0:
        fb = 'not taken (got != 0)'
    k32.CloseHandle(h)
    k32.VirtualFree(buf, 0, MEM_RELEASE)
    P('%-34s flag=%-6s n=%-8d prot=%-9s bad_page=%-4s ok=%d got=%-8d err=%-5d pos_after=%-8d landed_before=%-8d '
      'in_bad=%-5d landed_after=%-8d fallback: %s' % (name, flag, nbytes, prot if bad_page is not None else '-',
                                                      bad_page, ok, got.value, err, pos_after, landed_before, in_bad,
                                                      landed_after, fb))
    return ok, got.value, err


os.makedirs(work, exist_ok=True)
small = os.path.join(work, 'f22a_small.bin')
big = os.path.join(work, 'f22a_big.bin')
ds = make_file(small, 16 * PAGE)
db = make_file(big, 2048 * PAGE)  # 8 MiB
P('F22a stand: ReadFile into a buffer with one protected page; Windows', sys.getwindowsversion())
P('control: no protected page')
for flag in ('cached', 'random', 'nobuf'):
    case('ctl_small', small, ds, flag, 16 * PAGE, 16, None, None)
    case('ctl_big', big, db, flag, 2048 * PAGE, 2048, None, None)
P('protected page inside the buffer')
for prot in ('READONLY', 'NOACCESS', 'GUARD_RW'):
    for flag in ('cached', 'random', 'nobuf'):
        case('small_mid', small, ds, flag, 16 * PAGE, 16, 8, prot)
        case('small_first', small, ds, flag, 16 * PAGE, 16, 0, prot)
        case('small_last', small, ds, flag, 16 * PAGE, 16, 15, prot)
        case('big_mid', big, db, flag, 2048 * PAGE, 2048, 1024, prot)
        case('big_last', big, db, flag, 2048 * PAGE, 2048, 2047, prot)
        case('big_mid_from_off', big, db, flag, 1024 * PAGE, 1024, 512, prot, start=512 * PAGE)
P('request past EOF with a protected page beyond the file data (file 16 pages, buffer 20 pages, page 18 protected)')
for prot in ('READONLY', 'NOACCESS'):
    case('eof_tail_bad', small, ds, 'cached', 20 * PAGE, 20, 18, prot)
    case('eof_tail_ok', small, ds, 'cached', 20 * PAGE, 20, None, prot)
P('read that starts at EOF (remaining 0): the emulator takes no fallback; page 0 protected')
case('at_eof_bad', small, ds, 'cached', 4 * PAGE, 4, 0, 'READONLY', start=16 * PAGE)
P('second read of the same case (file now warm) - repeatability')
for prot in ('READONLY',):
    for flag in ('cached', 'random', 'nobuf'):
        case('big_mid_again', big, db, flag, 2048 * PAGE, 2048, 1024, prot)
P('unaligned destination as in the game logs (dst ...f900, ...27c0): the request starts at an offset inside page 0')


def case_off(name, path, data, flag, nbytes, boff, bad_page, prot):
    pages = (boff + nbytes + PAGE - 1) // PAGE + 1
    buf = k32.VirtualAlloc(None, pages * PAGE, MEM_COMMIT_RESERVE, PROT['READWRITE'])
    ctypes.memset(buf, 0xCC, pages * PAGE)
    old = W.DWORD(0)
    if bad_page is not None:
        k32.VirtualProtect(buf + bad_page * PAGE, PAGE, PROT[prot], ctypes.byref(old))
    h = k32.CreateFileW(path, GENERIC_READ, SHARE, None, OPEN_EXISTING, FLAGS[flag], None)
    got = W.DWORD(0xFFFFFFFF)
    ctypes.set_last_error(0)
    ok = k32.ReadFile(h, buf + boff, nbytes, ctypes.byref(got), None)
    err = ctypes.get_last_error() if not ok else 0
    pos_after = tell(h)
    if bad_page is not None:
        k32.VirtualProtect(buf + bad_page * PAGE, PAGE, PROT['READWRITE'], ctypes.byref(old))
    mem = ctypes.string_at(buf + boff, nbytes)
    want = data[:nbytes]
    landed = sum(1 for i in range(0, len(want), 64) if mem[i] == want[i])  # sampled every 64 bytes
    fb = '-'
    if got.value == 0:
        k32.SetFilePointerEx(h, 0, None, 0)
        tmp = ctypes.create_string_buffer(nbytes)
        got2 = W.DWORD(0)
        ok2 = k32.ReadFile(h, tmp, nbytes, ctypes.byref(got2), None)
        ctypes.memmove(buf + boff, tmp, got2.value)
        fb = 'ok2=%d got2=%d equal=%d' % (ok2, got2.value, int(ctypes.string_at(buf + boff, got2.value) == want[:got2.value]))
    k32.CloseHandle(h)
    k32.VirtualFree(buf, 0, MEM_RELEASE)
    P('%-34s flag=%-6s n=%-9d boff=0x%x prot=%-9s bad_page=%-5s ok=%d got=%-9d err=%-5d pos_after=%-9d landed_sampled=%-7d fallback: %s'
      % (name, flag, nbytes, boff, prot if bad_page is not None else '-', bad_page, ok, got.value, err, pos_after, landed, fb))


huge = os.path.join(work, 'f22a_huge.bin')
dh = make_file(huge, 40627200)
for flag in ('cached', 'random'):
    case_off('off_ctl_623248', huge, dh, flag, 623248, 0x900, None, None)
    for prot in ('READONLY', 'NOACCESS'):
        case_off('off_623248_mid', huge, dh, flag, 623248, 0x900, 76, prot)
        case_off('off_623248_first', huge, dh, flag, 623248, 0x900, 0, prot)
        case_off('off_40627200_mid', huge, dh, flag, 40627200, 0x7c0, 4960, prot)
        case_off('off_40627200_last', huge, dh, flag, 40627200, 0x7c0, 9919, prot)
os.remove(huge)
os.remove(small)
os.remove(big)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
P('STAND DONE')
