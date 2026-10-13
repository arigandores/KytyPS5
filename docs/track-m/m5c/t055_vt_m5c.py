"""M5c (HPP-847), T055 6b79b7a00, ROADMAP p.767(zh): who calls the game's AvPlayer wrappers.
Read-only static analysis of eboot.elf (F26a copy). Steps:
 (1) function starts in the VideoPlayerOrbis AvPlayer cluster 0x1053d5f..0x1055dfc (push rbp; mov rbp,rsp after int3 padding);
 (2) for each wrapper that holds an AvPlayer import call site: R_X86_64_RELATIVE slots whose addend is that function (vtable slots),
     and direct call/jmp rel32 to it;
 (3) vptr candidates: rip-relative lea/mov into the contiguous run of slots; virtual call displacement = slot - vptr;
 (4) indirect call sites 'call qword ptr [reg + disp8/disp32]' with those displacements over all code (count and the first 10):
     the displacement is shared with every other interface, so the count is an upper bound, not the caller set.
Usage: python t055_vt_m5c.py > t055_vt_m5c.out.txt"""
import os, sys, struct, re, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_OP_MEM
from capstone.x86 import X86_REG_RIP
ELF = 'C:/kyty/f287/f26a/eboot.elf'
elf = Elf(ELF); e = elf.data
print('eboot.elf sha256', hashlib.sha256(e).hexdigest(), 'size', len(e))
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
LO, HI = 0x1053a00, 0x1055e40
# import stubs (avcall_m5a.out.txt, [c] M5a)
STUBS = {0x74ebca0: 'SetLooping', 0x74ebcb0: 'SetTrickSpeed', 0x74ebcc0: 'Stop', 0x74ebcd0: 'Start', 0x74ebce0: 'AddSource',
         0x74ebcf0: 'Init', 0x74ebd00: 'PostInit', 0x74ebd10: 'IsActive', 0x74ebd20: 'EnableStream', 0x74ebd30: 'GetStreamInfo',
         0x74ebd40: 'Resume', 0x74ebd50: 'Pause', 0x74ebd60: 'GetVideoDataEx', 0x74ebd70: 'Close', 0x74ebd80: 'StreamCount',
         0x74ebd90: 'JumpToTime', 0x74ebda0: 'SetAvSyncMode'}


def func_starts(lo, hi):
    """starts: 0x10-aligned address after int3 (0xcc) padding, or right after a ret (0xc3) when the code there is push rbp; mov rbp,rsp"""
    st = []
    b = elf.read(lo, hi - lo)
    for i in range(1, len(b)):
        if (lo + i) % 16 == 0 and ((b[i - 1] == 0xcc and b[i] != 0xcc) or (b[i - 1] == 0xc3 and b[i:i + 4] == bytes([0x55, 0x48, 0x89, 0xe5]))):
            st.append(lo + i)
    return st


def enclosing(addr, starts):
    k = None
    for s in starts:
        if s <= addr:
            k = s
        else:
            break
    return k


starts = func_starts(LO, HI)
# map stub call sites to wrapper functions
wrap = {}
for ins in md.disasm(elf.read(LO, HI - LO), LO):
    if ins.mnemonic == 'call' and ins.op_str.startswith('0x'):
        t = int(ins.op_str, 16)
        if t in STUBS:
            wrap.setdefault(enclosing(ins.address, starts), []).append((STUBS[t], ins.address))
print('wrapper functions with AvPlayer import calls (function start: [(import, site)])')
for f in sorted(wrap):
    print('  0x%x %s' % (f, wrap[f]))
# relocations
phoff = struct.unpack('<Q', e[32:40])[0]; phnum = struct.unpack('<H', e[56:58])[0]
tags = {}
for i in range(phnum):
    t, fl, off, va, pa, fs, ms, al = struct.unpack('<IIQQQQQQ', e[phoff + 56 * i: phoff + 56 * i + 56])
    if t == 2:
        for j in range(0, fs, 16):
            tg, v = struct.unpack('<QQ', e[off + j: off + j + 16])
            if tg == 0:
                break
            tags.setdefault(tg, v)
RELA, RELASZ = tags[0x7], tags[0x8]
by_add = collections.defaultdict(list)
slot_add = {}
for k in range(RELASZ // 24):
    r_off, r_info, r_add = struct.unpack('<QQq', elf.read(RELA + 24 * k, 24))
    if (r_info & 0xffffffff) == 8:
        by_add[r_add].append(r_off)
        slot_add[r_off] = r_add
print('RELA entries', RELASZ // 24)
focus = {f: n for f, lst in wrap.items() for n, _ in lst}
slots_of = {}
for f in sorted(wrap):
    s = by_add.get(f, [])
    slots_of[f] = s
    print('  wrapper 0x%x (%s): vtable slots %s' % (f, focus[f], ['0x%x' % x for x in s]))
# direct calls
code_hits = collections.defaultdict(list)
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    for m in re.finditer(rb'[\xe8\xe9]', code):
        i = m.start()
        if i + 5 > len(code):
            continue
        t = v + i + 5 + struct.unpack('<i', code[i + 1:i + 5])[0]
        if t in wrap:
            code_hits[t].append(('call' if code[i] == 0xe8 else 'jmp', v + i))
for f in sorted(wrap):
    print('  wrapper 0x%x (%s): direct rel32 hits %d %s' % (f, focus[f], len(code_hits[f]), ['%s@0x%x' % h for h in code_hits[f][:8]]))
# vtable runs around the JumpToTime/IsActive slots
all_slots = sorted(slot_add)
import bisect


def run_of(s):
    i = bisect.bisect_left(all_slots, s)
    a = i
    while a > 0 and all_slots[a - 1] == all_slots[a] - 8:
        a -= 1
    b = i
    while b + 1 < len(all_slots) and all_slots[b + 1] == all_slots[b] + 8:
        b += 1
    return all_slots[a], all_slots[b] + 8


runs = {}
for f, s in slots_of.items():
    for x in s:
        runs.setdefault(run_of(x), set()).add(x)
print('vtable runs holding wrapper slots: %d' % len(runs))
for (a, b), xs in sorted(runs.items()):
    print('  run 0x%x..0x%x (%d slots)' % (a, b, (b - a) // 8))
    for x in range(a, b, 8):
        ad = slot_add[x]
        tag = focus.get(ad, '')
        print('     slot 0x%x +0x%x -> 0x%x %s' % (x, x - a, ad, tag))
# vptr candidates: rip-relative references into each run
refs = collections.defaultdict(list)
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    # lea r64,[rip+disp32]: 48/4c 8d modrm(00 reg 101)
    for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', code):
        i = m.start()
        if i + 7 > len(code):
            continue
        t = v + i + 7 + struct.unpack('<i', code[i + 3:i + 7])[0]
        for (a, b) in runs:
            if a <= t < b:
                refs[(a, b)].append((v + i, t))
disp_want = {}
for (a, b), lst in sorted(refs.items()):
    print('  run 0x%x: lea refs %d %s' % (a, len(lst), ['0x%x->+0x%x' % (s, t - a) for s, t in lst[:12]]))
    vp = collections.Counter(t for s, t in lst)
    for t, n in vp.most_common(3):
        for x in runs[(a, b)]:
            disp_want[(t, x)] = x - t
print('virtual call displacements (vptr, slot -> disp, wrapper):')
for (t, x), d in sorted(disp_want.items()):
    print('  vptr 0x%x slot 0x%x disp 0x%x %s' % (t, x, d, focus[slot_add[x]]))
# indirect call sites with these displacements, any base register
want_d = collections.defaultdict(set)
for (t, x), d in disp_want.items():
    if d >= 0:
        want_d[d].add(focus[slot_add[x]])
sites = collections.defaultdict(list)
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    for m in re.finditer(rb'\xff[\x50-\x57\x90-\x97]', code):
        i = m.start()
        mod = code[i + 1] >> 6
        rm = code[i + 1] & 7
        if rm == 4:
            continue
        if mod == 1:
            d = code[i + 2] if code[i + 2] < 128 else code[i + 2] - 256
        else:
            if i + 6 > len(code):
                continue
            d = struct.unpack('<i', code[i + 2:i + 6])[0]
        if d in want_d:
            sites[d].append(v + i)
for d in sorted(want_d):
    print('  disp 0x%x (%s): indirect call sites %d' % (d, ','.join(sorted(want_d[d])), len(sites[d])))
    for s in sites[d][:10]:
        print('     0x%x' % s)
print('DONE')
