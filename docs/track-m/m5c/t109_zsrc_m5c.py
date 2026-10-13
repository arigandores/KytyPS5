"""M5c (HPP-847), T109 2aaf0c9ba, ROADMAP p.767(e): source of the Z export of the PS programs that write MRTZ.Z and are
in the recipe catalogue (t109_join_m5c.out.txt): be4c35a2031fd3f4, f25acd918dbac2b5 (T1), 5514e10f1a60df83, c67734666ad63e20.
Read-only except its own outputs in <out dir>/dec/. Steps:
 (A) GCN: decode each raw program (eboot_text, = _Shaders original form) with the translator's own decoder (KYTY_M_DECODE mode of
     shader_cfg_tests_main.exe: CPU decode only, returns before any test case); the EXP target 8 with en bit0 gives the Z vreg;
     list EVERY instruction in the program whose destination range covers that vreg (VALU dst; MIMG/MUBUF/MTBUF/DS/FLAT data
     ranges by dmask/dwords; VINTRP) and classify it: SAT if the dst carries '.clamp' or it is V_MED3_F32 with both 0 and
     1.000000 among its sources, else NOSAT.  'input' = a read of the Z vreg before any writer on the linear order (PS input VGPR).
     Rule p.767(e) 'saturated in [0,1]': every writer SAT and no input path.
 (B) SPIR-V (T1 programs only, corpus base/out.spv of M2a): backward slice from 'OpStore %gl_FragDepth X' through result ids;
     value slice (OpSelect: value operands only; OpCompositeExtract of OpCompositeConstruct: that component; OpPhi: all incoming values); report leaf set (variable loads, constants, image ops) and whether any GLSL.std.450 FClamp/NClamp/FMin/FMax/NMin/NMax/
     FMix occurs on the slice.
Usage: python t109_zsrc_m5c.py <out dir> > t109_zsrc_m5c.out.txt"""
import os, sys, re, subprocess, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
OUT = sys.argv[1]
DEC = 'C:/kyty/m657/m2a/bin/shader_cfg_tests_main.exe'
RAW = 'C:/kyty/f287/f23a/eboot_text/'
SPV = {'be4c35a2031fd3f4': 'C:/kyty/m657/m2a/corpus/base/ps_be4c35a2031fd3f4_a772ac521fadeb8a_0/out.spv',
       'f25acd918dbac2b5': 'C:/kyty/m657/m2a/corpus/base/ps_f25acd918dbac2b5_3595d376277395b4_0/out.spv'}
DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
PROGS = ['be4c35a2031fd3f4', 'f25acd918dbac2b5', '5514e10f1a60df83', 'c67734666ad63e20']
os.makedirs(OUT + '/dec', exist_ok=True)
print('decoder', DEC, 'sha256', hashlib.sha256(open(DEC, 'rb').read()).hexdigest())
LINE = re.compile(r'^pc=0x([0-9a-f]+) fam=(\d+) op=0x([0-9a-f]+) 0x[0-9a-f]+: (\S+)\s*(.*)$')
REG = re.compile(r'\bv(\d+)\b')


def dst_range(mn, rest):
    """(first vreg, count) written, or None"""
    ops = rest.split(';')[0]
    first = ops.split(',')[0].strip()
    m = re.match(r'v(\d+)', first)
    if not m:
        return None
    base = int(m.group(1))
    u = mn.upper()
    if u.startswith(('V_CMP', 'V_READLANE', 'V_READFIRSTLANE')) or u.startswith('S_') or u.startswith('EXP'):
        return None
    if u.startswith('IMAGE_') or u.startswith('IMAGE'):
        dm = re.search(r'dmask=0x([0-9a-f]+)', rest)
        n = bin(int(dm.group(1), 16)).count('1') if dm else 1
        if u.startswith(('IMAGE_STORE', 'IMAGE_ATOMIC')) and 'glc=1' not in rest:
            return None
        return base, max(n, 1)
    if 'STORE' in u or u.startswith('DS_WRITE'):
        return None
    dw = re.search(r'dwords=(\d+)', rest)
    if dw:
        return base, int(dw.group(1))
    m2 = re.search(r'X(\d)$', u) or re.search(r'DWORDX(\d)', u)
    if u.startswith(('BUFFER_LOAD', 'TBUFFER_LOAD', 'DS_READ', 'FLAT_LOAD', 'GLOBAL_LOAD')) and m2:
        return base, int(m2.group(1))
    if re.search(r'(F64|B64|I64|U64)$', u) or u.startswith('V_MAD_U64') or u.startswith('V_MAD_I64'):
        return base, 2
    return base, 1


def srcs(rest):
    ops = rest.split(';')[0].split(',')[1:]
    return [o.strip() for o in ops]


for h in PROGS:
    print('=' * 100)
    raw = RAW + h + '.bin'
    print('PS', h, 'raw', raw, 'sha256', hashlib.sha256(open(raw, 'rb').read()).hexdigest())
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env['KYTY_M_DECODE'] = raw
    p = subprocess.run([DEC], env=env, capture_output=True, timeout=120)
    text = p.stdout.decode('utf-8', 'replace')
    open('%s/dec/ps_%s.txt' % (OUT, h), 'w', newline='\n').write(text)
    print('  decode rc', p.returncode, 'tail', text.strip().split('\n')[-1])
    ins = []
    for ln in text.split('\n'):
        m = LINE.match(ln)
        if m:
            ins.append((int(m.group(1), 16), int(m.group(2)), m.group(4), m.group(5)))
    zexp = [(pc, rest) for pc, fam, mn, rest in ins if mn == 'exp' and 'target=0x08' in rest and
            int(re.search(r'en=0x([0-9a-f]+)', rest).group(1), 16) & 1]
    print('  MRTZ exports with Z:', len(zexp))
    for pc, rest in zexp:
        zr = int(re.search(r'vm=\d+ v(\d+)', rest).group(1))
        print('  export pc=0x%05x Z vreg v%d  (%s)' % (pc, zr, rest))
        writers = []
        first_read = None
        first_write = None
        for k, (ipc, fam, mn, r) in enumerate(ins):
            d = dst_range(mn, r)
            reads = [int(x) for o in srcs(r) for x in REG.findall(o)] if mn != 'exp' else []
            if zr in reads and first_read is None:
                first_read = ipc
            if d and d[0] <= zr < d[0] + d[1]:
                writers.append((ipc, mn, r))
                if first_write is None:
                    first_write = ipc
        inp = (first_write is None) or (first_read is not None and first_read <= first_write) or True
        allsat = True
        for ipc, mn, r in writers:
            dstok = r.split(',')[0]
            sat = ('.clamp' in dstok) or (mn.upper() == 'V_MED3_F32' and '1.000000' in r and
                                         any(s.split('.')[0] == '0' for s in srcs(r)))
            allsat &= sat
            print('     writer pc=0x%05x %-6s %s %s' % (ipc, 'SAT' if sat else 'NOSAT', mn, r[:110]))
        # input path: the Z vreg holds the PS input VGPR value if the first linear writer is conditional (branch skips it)
        # or there is no writer; report the first read/first write order and any branch before the first writer.
        br = [ipc for ipc, fam, mn, r in ins if mn.startswith('S_CBRANCH') and (first_write is None or ipc < first_write)]
        print('     writers %d  first_write %s  first_read %s  conditional branches before first writer %d' % (
            len(writers), ('0x%05x' % first_write) if first_write is not None else '-',
            ('0x%05x' % first_read) if first_read is not None else '-', len(br)))
        input_path = first_write is None or len(br) > 0
        print('     input path possible (no writer, or a branch may skip the first writer): %s' % input_path)
        print('  VERDICT %s saturated_in_0_1=%s (every writer SAT and no input path)' % (h, allsat and not input_path))
    if h in SPV:
        spv = subprocess.run([DIS, SPV[h]], capture_output=True, timeout=60).stdout.decode('utf-8', 'replace')
        print('  SPIR-V', SPV[h], 'sha256', hashlib.sha256(open(SPV[h], 'rb').read()).hexdigest(), 'lines', spv.count('\n'))
        defs = {}
        names = {}
        for ln in spv.split('\n'):
            m = re.match(r'\s*(%\w+) = (Op\w+)\s*(.*)$', ln)
            if m:
                defs[m.group(1)] = (m.group(2), m.group(3))
        stores = re.findall(r'OpStore %gl_FragDepth (%\w+)', spv)
        print('  FragDepth stores', len(stores), stores)
        seen = set(); leaves = collections.Counter(); ops = collections.Counter(); ext = collections.Counter()
        work = list(stores)
        while work:
            x = work.pop()
            if x in seen or x not in defs:
                continue
            seen.add(x)
            op, args = defs[x]
            ops[op] += 1
            if op == 'OpExtInst':
                ext[args.split()[2]] += 1
            if op in ('OpConstant', 'OpConstantComposite', 'OpConstantTrue', 'OpConstantFalse', 'OpVariable'):
                leaves['%s %s' % (op, args)] += 1
                continue
            if op == 'OpLoad':
                ptr = args.split()[1]
                pd = defs.get(ptr, ('?', ''))
                if pd[0] == 'OpAccessChain':
                    leaves['OpLoad <- OpAccessChain %s' % ' '.join(pd[1].split()[1:4])] += 1
                else:
                    leaves['OpLoad <- %s %s' % (ptr, pd[0])] += 1
                continue
            if op.startswith('OpImage'):
                leaves[op] += 1
                continue
            ids = re.findall(r'%\w+', args)
            if op == 'OpPhi':
                nxt = ids[1::2]                      # (value, block) pairs after the type
            elif op == 'OpSelect':
                nxt = ids[2:4]                       # value operands only, not the condition
            elif op == 'OpCompositeExtract':
                src = ids[1]
                idx = [int(t) for t in args.split()[2:]]
                sd = defs.get(src, ('?', ''))
                if sd[0] == 'OpCompositeConstruct' and len(idx) == 1:
                    comps = re.findall(r'%\w+', sd[1])[1:]
                    seen.add(src)
                    ops['OpCompositeConstruct'] += 1
                    nxt = [comps[idx[0]]] if idx[0] < len(comps) else []
                else:
                    nxt = [src]
            else:
                nxt = ids[1:]
            for a in nxt:
                if a in defs:
                    work.append(a)
        print('  slice ids', len(seen), 'ops', dict(ops.most_common(20)))
        print('  GLSL ext ops on slice', dict(ext))
        sat_ops = {k: v for k, v in ext.items() if k in ('FClamp', 'NClamp', 'FMin', 'FMax', 'NMin', 'NMax', 'FMix')}
        print('  clamp/min/max on slice', sat_ops)
        lv = sorted(leaves.items(), key=lambda kv: -kv[1])
        print('  leaves (%d kinds):' % len(lv))
        for k, v in lv[:30]:
            print('     %4d  %s' % (v, k[:150]))
print('DONE')
