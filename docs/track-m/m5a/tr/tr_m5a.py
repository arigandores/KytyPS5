"""M5a (HPP-845, ROADMAP p.765(e)): translator themes of wave 2 - T200 (s_waitcnt_vscnt null,0), T113 (GLC/DLC/SLC on
vector memory) and the T306 repair (image_sample_*_o) - census over the 5 698 unique eboot programs
(C:/kyty/f287/f23a/eboot_text, walk = gcn_f23a.walk, unchanged) and membership in the corpus T1 (269 rows of
C:/kyty/m657/m2a/corpus/corpus_m2a.tsv = programs the game translated in the T1 arms, with stage).
Prints, per hit: program hash16, in T1 (stage) or not, pc, raw words, and a short disassembly window before the hit.
Read-only; refuses to run under C:/kyty/SEALED_RUN.lock.
Usage: python tr_m5a.py > tr_m5a.out.txt"""
import collections, csv, importlib.util, os, struct, sys
LOCK = 'C:/kyty/SEALED_RUN.lock'
if os.path.exists(LOCK):
    print('LOCK present - exit 3'); sys.exit(3)
spec = importlib.util.spec_from_file_location('g', 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
D = 'C:/kyty/f287/f23a/eboot_text/'
T1 = 'C:/kyty/m657/m2a/corpus/corpus_m2a.tsv'
SAMPLE_O = {0x30: 'image_sample_o', 0x31: 'image_sample_cl_o', 0x32: 'image_sample_d_o', 0x33: 'image_sample_d_cl_o',
            0x34: 'image_sample_l_o', 0x35: 'image_sample_b_o', 0x36: 'image_sample_b_cl_o', 0x37: 'image_sample_lz_o',
            0x38: 'image_sample_c_o', 0x39: 'image_sample_c_cl_o', 0x3a: 'image_sample_c_d_o',
            0x3b: 'image_sample_c_d_cl_o', 0x3c: 'image_sample_c_l_o', 0x3d: 'image_sample_c_b_o',
            0x3e: 'image_sample_c_b_cl_o', 0x3f: 'image_sample_c_lz_o', 0x6c: 'image_sample_cd_o',
            0x6d: 'image_sample_cd_cl_o', 0x6e: 'image_sample_c_cd_o', 0x6f: 'image_sample_c_cd_cl_o'}
# RDNA2 SOPK: 0x17 S_WAITCNT_VSCNT, 0x18 VMCNT, 0x19 EXPCNT, 0x1a LGKMCNT (ISA [I]; our table ScalarAluOps.cpp:91-92)
SOPK_WAIT = {0x17: 'vscnt', 0x18: 'vmcnt', 0x19: 'expcnt', 0x1a: 'lgkmcnt'}

t1 = collections.defaultdict(set)
for r in csv.DictReader(open(T1, encoding='utf-8'), delimiter='\t'):
    t1[r['hash16']].add(r['stage'])


def mem_bits(fam, w, w1):
    if fam in ('MUBUF', 'MTBUF'):
        return dict(glc=(w >> 14) & 1, dlc=(w >> 15) & 1, slc=(w1 >> 22) & 1)
    if fam == 'FLAT':
        return dict(glc=(w >> 16) & 1, dlc=(w >> 12) & 1, slc=(w >> 17) & 1)
    if fam == 'MIMG':
        return dict(glc=(w >> 13) & 1, dlc=(w >> 7) & 1, slc=(w1 >> 22) & 1 if False else (w >> 25) & 1)
    return None


def mem_op(fam, w, w1):
    if fam == 'MUBUF':
        return 'mubuf_0x%02x' % (((w >> 18) & 0x7f) | (((w >> 25) & 1) << 7))
    if fam == 'MTBUF':
        return 'mtbuf_0x%x' % (((w >> 16) & 7) | (((w1 >> 21) & 1) << 3))
    if fam == 'FLAT':
        return 'flat.%s_0x%02x' % ({0: 'flat', 1: 'scratch', 2: 'global', 3: 'seg3'}[(w >> 14) & 3], (w >> 18) & 0x7f)
    return fam


def dis(words, ins):
    pc, fam, op, size, ex = ins
    raw = ' '.join('%08x' % words[pc + k] for k in range(size) if pc + k < len(words))
    nm = g.name_of(fam, op) if fam.startswith('VOP') else ('%s_0x%x' % (fam, op) if op is not None else fam)
    if fam in ('MUBUF', 'MTBUF', 'FLAT'):
        nm = mem_op(fam, words[pc], words[pc + 1])
    if fam == 'MIMG':
        nm = SAMPLE_O.get(op, 'mimg_0x%02x' % op)
    return '%5d %-28s %s' % (pc, nm, raw)


files = sorted(os.listdir(D))
hits = collections.defaultdict(list)   # kind -> [(hash, pc, extra)]
cnt = collections.Counter()
glc_hist = collections.Counter()
prog_words = {}
prog_ins = {}
status = collections.Counter()
for fn in files:
    b = open(D + fn, 'rb').read()
    words = list(struct.unpack_from('<%dI' % (len(b) // 4), b, 0))
    out, st = g.walk(words)
    status[st.split('@')[0]] += 1
    h = fn[:16]
    for idx, (pc, fam, op, size, ex) in enumerate(out):
        w = words[pc]
        w1 = words[pc + 1] if pc + 1 < len(words) else 0
        if fam == 'SOPK' and op in SOPK_WAIT:
            sdst = (w >> 16) & 0x7f
            simm = w & 0xffff
            cnt['sopk_%s' % SOPK_WAIT[op]] += 1
            if op == 0x17:
                hits['vscnt'].append((h, pc, idx, 'sdst=%d imm=%d' % (sdst, simm)))
        if fam in ('MUBUF', 'MTBUF', 'FLAT'):
            mb = mem_bits(fam, w, w1)
            if mb['glc'] or mb['dlc'] or mb['slc']:
                key = '%s glc=%d dlc=%d slc=%d' % (mem_op(fam, w, w1), mb['glc'], mb['dlc'], mb['slc'])
                glc_hist[key] += 1
                hits['glc'].append((h, pc, idx, key))
        if fam == 'MIMG' and op in SAMPLE_O:
            hits['sample_o'].append((h, pc, idx, SAMPLE_O[op]))
    prog_words[h] = words
    prog_ins[h] = out

print('programs', len(files), 'walk status', dict(status))
print('SOPK waitcnt forms', dict(cnt))
for kind in ('vscnt', 'glc', 'sample_o'):
    lst = hits[kind]
    progs = sorted(set(x[0] for x in lst))
    in_t1 = [p for p in progs if p in t1]
    print()
    print('=== %s: instructions %d, programs %d, of them in corpus T1 %d %s' %
          (kind, len(lst), len(progs), len(in_t1), ['%s:%s' % (p, '/'.join(sorted(t1[p]))) for p in in_t1]))
    if kind == 'glc':
        for k, v in sorted(glc_hist.items()):
            print('  form', k, v)
    for h, pc, idx, extra in lst:
        stg = '/'.join(sorted(t1[h])) if h in t1 else '-'
        print('  hit %s T1=%s pc=%d %s' % (h, stg, pc, extra))
        ins = prog_ins[h]
        lo = max(0, idx - (40 if kind == 'sample_o' else 6))
        hi = min(len(ins), idx + 4)
        for k in range(lo, hi):
            print('     ' + ('>' if k == idx else ' ') + dis(prog_words[h], ins[k]))
print()
print('DONE tr_m5a')
