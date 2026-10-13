"""M5b (HPP-846): independent recount of M5a translator numbers (T200, T113, T306, T133 DIM) over the 5 698 eboot
programs with an OWN linear GFX10 length decoder (no import of gcn_f23a.py). Read-only; exits 3 under the lock.
Usage: python rc_tr_m5b.py > rc_tr_m5b.out.txt"""
import collections, csv, os, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3'); sys.exit(3)
D = 'C:/kyty/f287/f23a/eboot_text/'
T1 = 'C:/kyty/m657/m2a/corpus/corpus_m2a.tsv'
t1 = collections.defaultdict(set)
for r in csv.DictReader(open(T1, encoding='utf-8'), delimiter='\t'):
    t1[r['hash16']].add(r['stage'])

SAVEEXEC = set(range(0x24, 0x2c)) | set(range(0x33, 0x37)) | set(range(0x3c, 0x48))


def vsrc_extra(s):
    if s == 255:
        return 1
    if s in (0xF9, 0xFA, 0xE9, 0xEA):
        return 1
    return 0


def decode(words):
    """yield (pc, fam, w0, w1, size, info) linearly; info dict"""
    pc = 0
    n = len(words)
    while pc < n:
        w = words[pc]
        w1 = words[pc + 1] if pc + 1 < n else 0
        info = {}
        if (w >> 23) == 0x17D:
            fam = 'SOP1'; size = 1 + (1 if (w & 0xff) == 255 else 0)
            info['op'] = (w >> 8) & 0xff; info['sdst'] = (w >> 16) & 0x7f
        elif (w >> 23) == 0x17E:
            fam = 'SOPC'; size = 1 + (1 if (w & 0xff) == 255 or ((w >> 8) & 0xff) == 255 else 0)
        elif (w >> 23) == 0x17F:
            fam = 'SOPP'; size = 1; info['op'] = (w >> 16) & 0x7f; info['imm'] = w & 0xffff
        elif (w >> 28) == 0xB:
            fam = 'SOPK'; info['op'] = (w >> 23) & 0x1f; info['sdst'] = (w >> 16) & 0x7f; info['imm'] = w & 0xffff
            size = 2 if info['op'] == 0x15 else 1
        elif (w >> 30) == 2:
            fam = 'SOP2'; info['op'] = (w >> 23) & 0x7f; info['sdst'] = (w >> 16) & 0x7f
            size = 1 + (1 if (w & 0xff) == 255 or ((w >> 8) & 0xff) == 255 else 0)
        elif (w >> 25) == 0x3F:
            fam = 'VOP1'; info['op'] = (w >> 9) & 0xff; info['vdst'] = (w >> 17) & 0xff; info['src0'] = w & 0x1ff
            size = 1 + vsrc_extra(w & 0x1ff)
        elif (w >> 25) == 0x3E:
            fam = 'VOPC'; info['op'] = (w >> 17) & 0xff; size = 1 + vsrc_extra(w & 0x1ff)
        elif (w >> 31) == 0:
            fam = 'VOP2'; op = (w >> 25) & 0x3f; info['op'] = op; info['vdst'] = (w >> 17) & 0xff
            size = 1 + vsrc_extra(w & 0x1ff)
            if op in (0x20, 0x21, 0x2c, 0x2d, 0x37, 0x38) and size == 1:
                size = 2
        else:
            top6 = w >> 26
            if top6 == 0x35:
                fam = 'VOP3'; info['op'] = (w >> 16) & 0x3ff; info['vdst'] = w & 0xff
                s0, s1, s2 = w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff
                size = 2 + (1 if 255 in (s0, s1, s2) else 0)
            elif top6 == 0x33:
                fam = 'VOP3P'; s0, s1, s2 = w1 & 0x1ff, (w1 >> 9) & 0x1ff, (w1 >> 18) & 0x1ff
                size = 2 + (1 if 255 in (s0, s1, s2) else 0)
            elif top6 == 0x32:
                fam = 'VINTRP'; size = 1
            elif top6 == 0x36:
                fam = 'DS'; size = 2; info['vdst'] = (w1 >> 24) & 0xff
            elif top6 == 0x37:
                fam = 'FLAT'; size = 2
            elif top6 == 0x38:
                fam = 'MUBUF'; size = 2; info['op'] = ((w >> 18) & 0x7f) | (((w >> 25) & 1) << 7); info['vdata'] = (w1 >> 8) & 0xff
            elif top6 == 0x3A:
                fam = 'MTBUF'; size = 2; info['vdata'] = (w1 >> 8) & 0xff
            elif top6 == 0x3C:
                fam = 'MIMG'; nsa = (w >> 1) & 3; size = 2 + nsa
                info['op'] = (w >> 18) & 0x7f; info['dim'] = (w >> 3) & 7; info['vaddr'] = w1 & 0xff
                info['vdata'] = (w1 >> 8) & 0xff
            elif top6 == 0x3E:
                fam = 'EXP'; size = 2
            elif top6 == 0x3D:
                fam = 'SMEM'; size = 2
            else:
                fam = 'UNK'; size = 1
        yield pc, fam, w, w1, size, info
        pc += size


def exec_write(fam, w, w1, info):
    if fam in ('SOP1', 'SOP2', 'SOPK') and info.get('sdst') in (126, 127):
        return True
    if fam == 'SOP1' and info.get('op') in SAVEEXEC:
        return True
    if fam == 'VOPC' and (info['op'] & 0x10):
        return 'cmpx?'
    if fam == 'VOP3' and info['op'] < 0x100 and (info['op'] & 0x10):
        return 'cmpx?'
    return False


BR_COND = set(range(0x04, 0x0a)) | set(range(0x17, 0x1b))
ENDS = {0x01, 0x1b, 0x1e}


def decode_one(words, pc):
    for t in decode(words[pc:pc + 4] + [0, 0, 0]):
        return (pc,) + t[1:]


def decode_at(words):
    return []


def walk(words):
    """reachability walk from pc 0 following SOPP branches; returns instructions sorted by pc"""
    seen = {}
    work = [0]
    n = len(words)
    while work:
        pc = work.pop()
        while 0 <= pc < n and pc not in seen:
            t = decode_one(words, pc)
            seen[pc] = t
            fam, info = t[1], t[5]
            if fam == 'SOPP':
                op = info['op']
                if op in ENDS:
                    break
                simm = info['imm'] - 0x10000 if info['imm'] & 0x8000 else info['imm']
                if op == 0x02:
                    pc = pc + 1 + simm
                    continue
                if op in BR_COND:
                    work.append(pc + 1 + simm)
            if fam == 'SOP1' and info['op'] in (0x20, 0x21):  # s_setpc / s_swappc: stop
                if info['op'] == 0x20:
                    break
            pc += t[4]
    return [seen[k] for k in sorted(seen)]


progs = sorted(f[:-4] for f in os.listdir(D) if f.endswith('.bin'))
print('programs', len(progs))
unk = 0; overrun = 0; endpgm_missing = 0
vscnt = []; other_wait = collections.Counter(); glc = []; sample_o = []; dim1d = collections.Counter(); dim1d_ins = 0
dim_hist = collections.Counter()
for h in progs:
    b = open(D + h + '.bin', 'rb').read()
    words = [int.from_bytes(b[i:i + 4], 'little') for i in range(0, len(b) - len(b) % 4, 4)]
    allins = {t[0]: t for t in decode_at(words)}
    ins = walk(words)
    end = ins[-1][0] + ins[-1][4]
    if end != len(words):
        overrun += 1
    if not any(f == 'SOPP' and i['op'] == 1 for _, f, _, _, _, i in ins):
        endpgm_missing += 1
    for k, (pc, fam, w, w1, size, info) in enumerate(ins):
        if fam == 'UNK':
            unk += 1
        if fam == 'SOPK' and info['op'] in (0x17, 0x18, 0x19, 0x1a):
            if info['op'] == 0x17:
                nxt = ins[k + 1] if k + 1 < len(ins) else None
                nxt_end = nxt is not None and nxt[1] == 'SOPP' and nxt[5]['op'] == 1
                vscnt.append((h, pc, info['sdst'], info['imm'], nxt_end))
            else:
                other_wait[info['op']] += 1
        if fam in ('MUBUF', 'MTBUF'):
            g_, d_, s_ = (w >> 14) & 1, (w >> 15) & 1, (w1 >> 22) & 1
            if g_ or d_ or s_:
                glc.append((h, pc, fam, info.get('op'), g_, d_, s_))
        if fam == 'FLAT':
            g_, d_, s_ = (w >> 16) & 1, (w >> 12) & 1, (w >> 17) & 1
            if g_ or d_ or s_:
                glc.append((h, pc, fam, None, g_, d_, s_))
        if fam == 'SMEM':
            g_, d_ = (w >> 16) & 1, (w >> 14) & 1
            if g_ or d_:
                glc.append((h, pc, 'SMEM', (w >> 18) & 0xff, g_, d_, 0))
        if fam == 'MIMG':
            dim_hist[info['dim']] += 1
            if info['dim'] == 0:
                dim1d[h] += 1; dim1d_ins += 1
            g_, d_, s_ = (w >> 13) & 1, (w >> 7) & 1, (w >> 25) & 1
            if g_ or d_ or s_:
                glc.append((h, pc, 'MIMG', info['op'], g_, d_, s_))
            if 0x30 <= info['op'] <= 0x3f or 0x6c <= info['op'] <= 0x6f:
                v = info['vaddr']
                # last linear writer of v and exec writes / branches between
                wr = None
                for j in range(k - 1, -1, -1):
                    p2, f2, x0, x1, s2, i2 = ins[j]
                    if i2.get('vdst') == v and f2 in ('VOP1', 'VOP2', 'VOP3'):
                        wr = j; break
                    if f2 in ('MUBUF', 'MTBUF', 'MIMG', 'DS', 'FLAT') and i2.get('vdata', i2.get('vdst', -1)) is not None:
                        base = i2.get('vdata', i2.get('vdst'))
                        if base is not None and base <= v < base + 4 and f2 != 'MIMG' or (f2 == 'MIMG' and base <= v < base + 4 and j != k):
                            wr = j; break
                ex = []; br = []
                if wr is not None:
                    for j in range(wr + 1, k):
                        p2, f2, x0, x1, s2, i2 = ins[j]
                        e = exec_write(f2, x0, x1, i2)
                        if e:
                            ex.append((p2, f2, '%08x' % x0, e))
                        if f2 == 'SOPP' and (i2['op'] == 2 or i2['op'] in BR_COND):
                            br.append(p2)
                # branch targets landing inside (wr, k]
                land = []
                if wr is not None:
                    lo, hi = ins[wr][0], pc
                    for p2, f2, x0, x1, s2, i2 in ins:
                        if f2 == 'SOPP' and (i2['op'] == 2 or i2['op'] in BR_COND):
                            simm = i2['imm'] - 0x10000 if i2['imm'] & 0x8000 else i2['imm']
                            tgt = p2 + 1 + simm
                            if lo < tgt <= hi:
                                land.append((p2, tgt))
                wdesc = None
                if wr is not None:
                    p2, f2, x0, x1, s2, i2 = ins[wr]
                    lit = words[p2 + 1] if f2 == 'VOP1' and i2.get('src0') == 255 else None
                    wdesc = (p2, f2, i2.get('op'), i2.get('src0'), None if lit is None else '%08x' % lit)
                sample_o.append((h, pc, info['op'], v, wdesc, ex, br, land))
print('decoder: UNK words', unk, 'programs not ending exactly at file end', overrun, 'programs without s_endpgm', endpgm_missing)
print('SOPK waits other than vscnt', dict(other_wait))
vp = sorted(set(x[0] for x in vscnt))
print('vscnt instr', len(vscnt), 'programs', len(vp), 'in T1', sum(1 for p in vp if p in t1))
for x in vscnt:
    print('  vscnt', x[0], 'T1=' + ','.join(sorted(t1.get(x[0], []))) if x[0] in t1 else 'T1=-', 'pc', x[1], 'sdst', x[2], 'imm', x[3], 'next_is_endpgm', x[4])
gp = sorted(set(x[0] for x in glc))
print('glc/dlc/slc instr', len(glc), 'programs', len(gp))
for x in glc:
    print('  bits', x[0], 'T1=' + (','.join(sorted(t1[x[0]])) if x[0] in t1 else '-'), 'pc', x[1], x[2], 'op', x[3], 'glc/dlc/slc', x[4], x[5], x[6])
op_ = sorted(set(x[0] for x in sample_o))
print('sample_o instr', len(sample_o), 'programs', len(op_))
for x in sample_o:
    print('  _o', x[0], 'T1=' + (','.join(sorted(t1[x[0]])) if x[0] in t1 else '-'), 'pc', x[1], 'op 0x%02x' % x[2], 'vaddr v%d' % x[3],
          'writer', x[4], 'exec_writes', x[5], 'branches', x[6], 'landings', x[7])
print('MIMG dim hist', dict(sorted(dim_hist.items())))
print('MIMG DIM=1D (field 0): programs', len(dim1d), 'instr', dim1d_ins)
print('ALL DONE')
