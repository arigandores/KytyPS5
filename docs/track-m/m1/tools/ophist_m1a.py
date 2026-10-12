"""M1a (HPP-835): full opcode histogram of the 5 698 unique ASTRO BOT eboot shader programs (C:/kyty/f287/f23a/eboot_text,
written by F23a gcn_f23a.py --eboot). Walk = gcn_f23a.walk (unchanged); op fields of DS/FLAT/MUBUF/MTBUF filled here
(RDNA2 encodings [I]): DS op = w[25:18]; FLAT op = w[24:18], seg = w[15:14]; MUBUF op = w[24:18]; MTBUF op = w[18:16]
| w1? (RDNA2: op[2:0] = w[18:16], op[3] = w1[21]); SMEM op already set. Modifier kind (sdwa/dpp16/dpp8) counted per
fam:op. Read-only; refuses to run under C:/kyty/SEALED_RUN.lock.
Usage: python ophist_m1a.py -> C:/kyty/m657/m1a/ophist.tsv"""
import collections, importlib.util, os, struct, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
spec = importlib.util.spec_from_file_location('g', 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
D = 'C:/kyty/f287/f23a/eboot_text/'
inst = collections.Counter(); progs = collections.Counter(); mods = collections.Counter(); status = collections.Counter()
files = sorted(os.listdir(D))
for fn in files:
    b = open(D + fn, 'rb').read()
    words = list(struct.unpack_from('<%dI' % (len(b) // 4), b, 0))
    out, st = g.walk(words)
    status[st.split('@')[0]] += 1
    seen = set()
    for pc, fam, op, size, ex in out:
        w = words[pc]
        w1 = words[pc + 1] if pc + 1 < len(words) else 0
        if fam == 'DS':
            op = (w >> 18) & 0xff
        elif fam == 'FLAT':
            op = (w >> 18) & 0x7f
            fam = 'FLAT.' + {0: 'flat', 1: 'scratch', 2: 'global', 3: 'seg3'}[(w >> 14) & 3]
        elif fam == 'MUBUF':
            op = (w >> 18) & 0x7f
        elif fam == 'MTBUF':
            op = ((w >> 16) & 7) | (((w1 >> 21) & 1) << 3)
        elif fam == 'EXP':
            op = 0
        k = '%s:%x' % (fam, op if op is not None else -1)
        inst[k] += 1
        seen.add(k)
        if 'mod' in ex:
            mods[(k, ex['mod'])] += 1
    for k in seen:
        progs[k] += 1
os.makedirs('C:/kyty/m657/m1a', exist_ok=True)
with open('C:/kyty/m657/m1a/ophist.tsv', 'w', encoding='utf-8', newline='\n') as f:
    f.write('famop\tinstructions\tprograms\tsdwa\tdpp16\tdpp8\n')
    for k in sorted(inst, key=lambda x: (x.split(':')[0], int(x.split(':')[1], 16) if x.split(':')[1] != '-1' else -1)):
        f.write('%s\t%d\t%d\t%d\t%d\t%d\n' % (k, inst[k], progs[k], mods[(k, 'sdwa')], mods[(k, 'dpp16')],
                                             mods[(k, 'dpp8')] + mods[(k, 'dpp8fi')]))
print('programs', len(files), 'status', dict(status), 'distinct fam:op', len(inst))
