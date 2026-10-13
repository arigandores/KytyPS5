# M5a HLE1 (T031): format strings with a dynamic precision ".*" in eboot.elf and the call paths that hand them to
# OUR guestPrintf. Eboot imports printf/puts/vsnprintf from libc_v1 and they resolve to HLE LibC (exact name
# "<nid>[libc_v1][libc_v1.1]", src/libs/libC.cpp:870-872 at dd73d04d); snprintf eLdDw6l0-bU is registered only under
# LibcInternal, so the eboot import of it from libc resolves to libc.prx (guest code) - not ours.
# Method: every direct call to the printf / vsnprintf stubs and to the functions that contain a vsnprintf call
# (wrappers); for each call site the nearest preceding "lea <reg>, [rip+X]" of each argument register gives the
# literal format. Read-only static analysis; no claim about execution.
import os, sys, struct, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_REG_RIP, X86_OP_MEM

elf = Elf('C:/kyty/f287/f26a/eboot.elf'); e = elf.data
STUBS = {0x74e7440: ('printf', 'rdi'), 0x74e7400: ('vsnprintf', 'rdx'), 0x74ec2a0: ('puts', 'rdi'),
         0x74ec290: ('snprintf(libc.prx, not ours)', 'rdx')}
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
segs = elf.code_segments()

def call_sites(targets):
    out = collections.defaultdict(list)
    for v, off, fs in segs:
        code = e[off:off + fs]
        for m in re.finditer(rb'[\xe8\xe9]', code):
            i = m.start()
            t = v + i + 5 + struct.unpack('<i', code[i + 1:i + 5])[0]
            if t in targets: out[t].append(v + i)
    return out

def func_start(a):
    # nearest preceding "55 48 89 e5" (push rbp; mov rbp, rsp) within 0x4000
    lo = a - 0x4000
    blob = elf.read(lo, a - lo)
    k = blob.rfind(b'\x55\x48\x89\xe5')
    return lo + k if k >= 0 else None

def args_before(a, back=0x60):
    # decode forward from several start offsets, keep the decoding that lands exactly on a
    best = None
    for s in range(a - back, a):
        ins = list(md.disasm(elf.read(s, a - s + 5), s))
        if ins and any(x.address == a for x in ins):
            best = [x for x in ins if x.address < a]
            break
    regs = {}
    for x in best or []:
        if x.mnemonic == 'lea' and x.operands[1].type == X86_OP_MEM and x.operands[1].mem.base == X86_REG_RIP:
            r = x.op_str.split(',')[0].strip()
            s = elf.cstr(x.address + x.size + x.operands[1].mem.disp, 300)
            if s is not None: regs[r] = s
    return regs

sites = call_sites(set(STUBS))
# wrappers: functions containing a vsnprintf call (they take the format in some register)
wrappers = {}
for a in sites[0x74e7400]:
    fs_ = func_start(a)
    if fs_ is not None: wrappers[fs_] = a
wsites = call_sites(set(wrappers))
print('direct sites: ' + ', '.join('%s %d' % (STUBS[t][0], len(sites[t])) for t in STUBS))
print('vsnprintf wrappers (function start <- vsnprintf site): %d' % len(wrappers))
for w in sorted(wrappers):
    print('   0x%x (vsnprintf at 0x%x) callers %d' % (w, wrappers[w], len(wsites[w])))
dyn = re.compile(rb'%[-+ #0]*(?:\d+|\*)?\.\*')
fmt_any = collections.Counter(); hits = []
def scan_site(kind, a):
    regs = args_before(a)
    for r, s in regs.items():
        if b'%' in s:
            fmt_any[kind] += 1
            if dyn.search(s): hits.append((kind, a, r, s))
for t in STUBS:
    for a in sites[t]: scan_site(STUBS[t][0], a)
for w in wrappers:
    for a in wsites[w]: scan_site('wrapper_0x%x' % w, a)
print('call sites with a literal %%-format in an argument register:', dict(fmt_any))
print('of them with dynamic precision ".*": %d' % len(hits))
for kind, a, r, s in hits:
    print('   %-28s site 0x%x %s "%s"' % (kind, a, r, s.decode('latin1').replace('\n', '\\n')[:160]))
# all strings in the image containing a dynamic precision (whatever their consumer)
allc = [m.group(0) for m in re.finditer(rb'[\x20-\x7e\n\t]{2,300}?\x00', e) if dyn.search(m.group(0))]
print('strings anywhere in eboot.elf with ".*" precision: %d (unique %d)' % (len(allc), len(set(allc))))
for s in sorted(set(allc))[:60]:
    print('    "%s"' % s[:-1].decode('latin1').replace('\n', '\\n')[:150])
print('DONE')
