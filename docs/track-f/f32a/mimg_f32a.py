# F32a (HPP-733): row F11 - does any shader program of eboot.bin contain IMAGE_BVH64_INTERSECT_RAY (MIMG op 0xE7)?
# Uses the F23a walker unchanged (docs/track-f/f23a/gcn_f23a.py: eboot_programs(), walk(), words_of()).
# Positive control: IMAGE_BVH_INTERSECT_RAY (MIMG op 0xE6) count > 0 in the same walk; synthetic fixtures below.
# Usage: python mimg_f32a.py [--fixtures | --t1]
import os, sys, importlib.util, collections

F23A = os.environ.get('F32A_F23A', 'C:/kyty/KytyPS5/docs/track-f/f23a/gcn_f23a.py')
BVH, BVH64 = 0xE6, 0xE7


def load():
    spec = importlib.util.spec_from_file_location('gcn_f23a', F23A)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def mimg_word(op, nsa=0):
    # MIMG gfx10: [31:26] = 0x3C, op[6:0] at [24:18], op[7] at bit 0, NSA dwords at [2:1]
    return (0x3C << 26) | ((op & 0x7F) << 18) | ((op >> 7) & 1) | ((nsa & 3) << 1)


def count(g, words):
    ins, st = g.walk(words)
    c = collections.Counter(op for (_, fam, op, _, _) in ins if fam == 'MIMG')
    return c, st


def fixtures(g):
    ok = True
    s_endpgm = 0xBF810000
    w = [mimg_word(BVH, 1), 0, 0, mimg_word(BVH64, 2), 0, 0, 0, s_endpgm]
    c, st = count(g, w)
    r = c[BVH] == 1 and c[BVH64] == 1 and st == 'OK'
    print(('OK   ' if r else 'FAIL ') + 'synthetic BVH + BVH64 with NSA sizes', dict(c), st)
    ok &= r
    w = [mimg_word(0x00), 0, s_endpgm]
    c, st = count(g, w)
    r = c[BVH] == 0 and c[BVH64] == 0 and c[0] == 1
    print(('OK   ' if r else 'FAIL ') + 'synthetic non-BVH MIMG not counted', dict(c), st)
    ok &= r
    return ok


def main():
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        sys.exit(3)
    g = load()
    ok = fixtures(g)
    if '--fixtures' in sys.argv:
        print('ALL OK' if ok else 'FAILED')
        sys.exit(0 if ok else 1)
    progs, n_elf = g.eboot_programs()
    tot = collections.Counter()
    status = collections.Counter()
    with_bvh, with_bvh64 = [], []
    for h, p in progs.items():
        c, st = count(g, g.words_of(p['code']))
        status[st] += 1
        tot.update(c)
        if c[BVH]:
            with_bvh.append((h, c[BVH], st))
        if c[BVH64]:
            with_bvh64.append((h, c[BVH64], st))
    print('eboot ELF', n_elf, 'unique programs', len(progs))
    print('walk status', dict(status))
    print('MIMG op 0xE6 IMAGE_BVH_INTERSECT_RAY: instructions', tot[BVH], 'programs', len(with_bvh))
    print('MIMG op 0xE7 IMAGE_BVH64_INTERSECT_RAY: instructions', tot[BVH64], 'programs', len(with_bvh64))
    for h, n, st in with_bvh:
        print('bvh32', h, n, st)
    for h, n, st in with_bvh64:
        print('bvh64', h, n, st)
    print('ALL OK' if ok else 'FAILED')



def t1_main():
    # T1 corpus (runtime GCN dumps of the game, C:/kyty/s288/s4/gcn) - the same counts
    g = load()
    progs, stages = g.t1_programs()
    tot = collections.Counter()
    status = collections.Counter()
    nb = nb64 = 0
    for h, p in progs.items():
        c, st = count(g, p['words'])
        status[st] += 1
        tot.update(c)
        nb += 1 if c[BVH] else 0
        nb64 += 1 if c[BVH64] else 0
    print('T1 unique programs', len(progs), 'walk status', dict(status))
    print('T1 BVH instructions', tot[BVH], 'programs', nb, '; BVH64 instructions', tot[BVH64], 'programs', nb64)


if __name__ == '__main__':
    if '--t1' in sys.argv:
        t1_main()
    else:
        main()
