"""Offline models of our HLE code at KytyPS5 main dd73d04d (no emulator, no game).
Each model replicates the control flow of the cited lines; it shows what OUR code does for a
given guest call sequence. Guest behaviour itself is NOT measured here."""
import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present, exit'); sys.exit(3)

ok = True

# ---------------------------------------------------------------- T309 (libAmpr.cpp)
# dd73d04d:src/libs/libAmpr.cpp:937-946 EnsureCommandBufferRecordSpace: fail if record_size > size
#   or write_offset > size - record_size;  :1198-1216 AppendWriteAddressRecord record_size = 0x20;
# :2026-2035 AppendWriteAddressCommand -> EBUSY on fail; :975-977 ReadFile record 0x14/0x18;
# :1705-1710 MeasureCommandSizeFixed32 = 0x20 (NID 4fgtGfXDrFc :2588).
OURS_WA = lambda v: 0x20
SDK_WA = lambda v: 8 if v <= 3 else (12 if v < (1 << 34) else 16)   # [I] per upstream 41beda436
READ = lambda off: 0x18 if (off >> 32) else 0x14


class Cb:
    def __init__(self, size):
        self.size, self.off, self.recs = size, 0, []

    def append(self, kind, rs):
        if rs == 0 or rs > self.size or self.off > self.size - rs:
            return 'EBUSY' if kind == 'wa' else 'EFAULT'
        self.recs.append((self.off, kind))
        self.off += rs
        return 'OK'


def batch_hardcoded(size, pairs, wa_size):
    cb = Cb(size)
    lost = []
    for i in range(pairs):
        r1 = cb.append('read', READ(0))
        r2 = cb.append('wa', wa_size(i + 1))
        if r1 != 'OK' or r2 != 'OK':
            lost.append((i, r1, r2))
    return cb.off, lost


def fits_by_sdk(size, pairs):
    need = sum(READ(0) + SDK_WA(i + 1) for i in range(pairs))
    return need, need <= size


print('== T309 model: 768-byte buffer, 16 read+fence pairs, fence value i+1')
need, fits = fits_by_sdk(768, 16)
print('  SDK sizes [I]: bytes needed', need, 'fits', fits)
off, lost = batch_hardcoded(768, 16, OURS_WA)
print('  OUR code, guest sized batch by SDK constants: final offset', off, 'lost pairs', lost)
ok &= fits and [l[0] for l in lost] == [14, 15]
# guest that measures before each append (calls 4fgtGfXDrFc -> our 0x20) and submits when full
cb = Cb(768); submits = 0; lost2 = 0
for i in range(16):
    need_pair = READ(0) + 0x20  # measured by OUR measure functions
    if cb.off + need_pair > cb.size:
        submits += 1; cb = Cb(768)
    if cb.append('read', READ(0)) != 'OK' or cb.append('wa', OURS_WA(i + 1)) != 'OK':
        lost2 += 1
submits += 1
print('  OUR code, guest measuring via 4fgtGfXDrFc before append: lost', lost2, 'submits', submits)
ok &= lost2 == 0
print('  => difference exists ONLY if the guest sizes WriteAddress records without calling our measure')

# ---------------------------------------------------------------- T141 (libAmpr.cpp)
# :1259-1284 AllocateAmmAutoDirectMemory: pool g_amm_auto_pool filled only by AmmGiveDirectMemory
# (:2387-2411, NID Q07J7XpvhrU); otherwise KernelAllocateDirectMemory each time, never returned.
# :1438-1439 Unmap -> KernelMunmap(va,size) (mapping only, direct memory stays allocated).
print('== T141 model: repeated AMM MapAuto(16 MiB)/Unmap with empty auto pool')
DMEM = 16 << 30
allocated = 0; fail_at = None
for k in range(2000):
    sz = 16 << 20
    if allocated + sz > DMEM:
        fail_at = k; break
    allocated += sz          # MapAuto: new dmem
    # Unmap: KernelMunmap - no ReleaseDirectMemory
print('  cycles until EAGAIN (16 GiB dmem, nothing else allocated):', fail_at, 'allocated', allocated >> 20, 'MiB')
ok &= fail_at == 1024
print('  reachable only via NIDs JEVYGhDc97M / ojBkmG7+CgE (AmmCommandBufferMap*) + lwS-7y3jcBI etc. (see imports_m5a.out.txt)')

# ---------------------------------------------------------------- T246 (eventQueue.cpp)
# :94-141 GetTriggeredEvents; :116-122 reset_func / EV_CLEAR; :288-295 UserEventResetFunc clears only with EV_CLEAR
EV_ONESHOT, EV_CLEAR = 0x10, 0x20


def get_triggered(events, num):
    out = []
    for e in events:
        while e['triggered']:
            out.append(e['id'])
            if e['flags'] & EV_ONESHOT:
                break
            if e['reset'] == 'user':
                if e['flags'] & EV_CLEAR:
                    e['triggered'] = False
            elif e['reset'] == 'clear_always':
                e['triggered'] = False
            elif e['flags'] & EV_CLEAR:
                e['triggered'] = False
            if len(out) >= num:
                break
        if len(out) >= num:
            break
    return out


print('== T246 model: one wait with num=8')
for name, ev in [('AddUserEvent (level, EV_ADD)', dict(id=1, flags=0x01, reset='user', triggered=True)),
                 ('AddUserEventEdge (EV_CLEAR)', dict(id=2, flags=0x21, reset='user', triggered=True)),
                 ('GPU EOP (InterruptEventResetFunc)', dict(id=3, flags=0x01, reset='clear_always', triggered=True)),
                 ('VideoOut (ResetVideoOutEvent)', dict(id=4, flags=0x01, reset='clear_always', triggered=True))]:
    r = get_triggered([ev], 8)
    print('  %-36s -> %d copies' % (name, len(r)))
    if name.startswith('AddUserEvent ('):
        ok &= len(r) == 8
    else:
        ok &= len(r) == 1
print('ALL OK' if ok else 'FAIL')
