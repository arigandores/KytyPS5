# M5a HLE1: static call sites of the AvPlayer / AudioOut2 / printf PLT stubs in eboot.elf (C:/kyty/f287/f26a/eboot.elf,
# the decrypted eboot of F26a; PLT stub addresses from docs/track-f/f26a/plt.tsv). For AvPlayer: the order of calls
# inside each calling function (linear disassembly of the window around the call sites) - to answer whether
# SetAvSyncMode is called before AddSource (T055 12ff57160), IsActive before Start (6b79b7a00), and which streams
# are enabled. Read-only.
import os, sys, struct, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)
sys.path.insert(0, 'C:/kyty/scripts')
from s8_elf import Elf
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_REG_RIP, X86_OP_MEM, X86_OP_IMM

ELF = 'C:/kyty/f287/f26a/eboot.elf'
PLT = 'C:/kyty/KytyPS5/docs/track-f/f26a/plt.tsv'
stub = {}
for ln in open(PLT, encoding='utf-8'):
    a = ln.rstrip('\n').split('\t')
    if len(a) >= 6 and (a[2] in ('libSceAvPlayer', 'libSceAudioOut2') or a[3] in ('Q2V+iqvjgC0', 'hcuQgD53UxM', 'eLdDw6l0-bU', 'YQ0navp+YIc')):
        stub[int(a[0], 16)] = a[5].split('::')[-1] + '(' + a[3] + ')'
elf = Elf(ELF)
e = elf.data
calls = collections.defaultdict(list)
for v, off, fs in elf.code_segments():
    code = e[off:off + fs]
    for m in re.finditer(rb'[\xe8\xe9]', code):
        i = m.start()
        t = v + i + 5 + struct.unpack('<i', code[i + 1:i + 5])[0]
        if t in stub:
            calls[t].append((v + i, 'call' if code[i] == 0xe8 else 'jmp'))
print('ELF', ELF, 'size', len(e))
tot = collections.Counter()
for t in sorted(stub):
    print('%-45s stub 0x%x  sites %d  %s' % (stub[t], t, len(calls[t]), ' '.join('%s@0x%x' % (k, a) for a, k in calls[t][:12])))
# AvPlayer: cluster call sites (within 0x1800 bytes) and disassemble each cluster to list calls in order
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
av = sorted((a, stub[t]) for t in calls for a, k in calls[t] if 'AvPlayer' in stub[t])
clusters = []
for a, n in av:
    if clusters and a - clusters[-1][-1][0] < 0x1800:
        clusters[-1].append((a, n))
    else:
        clusters.append([(a, n)])
print('\nAvPlayer call-site clusters: %d' % len(clusters))
for cl in clusters:
    lo, hi = cl[0][0] - 0x80, cl[-1][0] + 0x20
    print('--- cluster 0x%x..0x%x : %s' % (lo, hi, ', '.join(n.split('(')[0] for _, n in cl)))
    # immediates loaded into esi/edx right before each AvPlayer call (args 2/3)
    ins = list(md.disasm(elf.read(lo, hi - lo), lo))
    for k, x in enumerate(ins):
        if x.mnemonic in ('call', 'jmp') and x.operands and x.operands[0].type == X86_OP_IMM and x.operands[0].imm in stub:
            prev = []
            for y in ins[max(0, k - 6):k]:
                if y.mnemonic in ('mov', 'xor', 'lea') and any(r in y.op_str.split(',')[0] for r in ('esi', 'rsi', 'edx', 'rdx', 'edi', 'rdi')):
                    note = ''
                    for op in y.operands:
                        if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP and y.mnemonic == 'lea':
                            s = elf.cstr(y.address + y.size + op.mem.disp, 100)
                            if s and all(32 <= c < 127 for c in s[:30]): note = ' "%s"' % s.decode('latin1')
                    prev.append('%s %s%s' % (y.mnemonic, y.op_str, note))
            print('   0x%x %s %-28s | %s' % (x.address, x.mnemonic, stub[x.operands[0].imm].split('(')[0], ' ; '.join(prev)))
print('DONE')
