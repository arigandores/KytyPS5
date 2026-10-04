"""F23d (HPP-588, Red Team): own repeat of H of F23c on the same files, with own comparison code and a reversed job order.

Inputs (F23c files, read only): C:/kyty/f287/f23c/f23c_hrun.exe, work/ref_{normal,predoff,ctrue_formA,blend_formA,sens_both}.spv,
work/vs_tri.spv, work/tex_noise_1920x1620.r8 (configuration c07 of F23c: 1920x1080, nearest, R16G16B16A16).
Checks:
  (1) sha256 of every input against the values printed by F23c (h_f23c.out.txt);
  (2) own SPIR-V word diff: ctrue_formA vs predoff differs only in the condition word of %286 and %306 (-> OpConstantTrue);
      sens_both vs predoff differs only in the two value words of %286 and %306 (swapped);
  (3) GPU: one runner process, jobs in the order predoff, ctrue_formA, blend_formA, sens_both, normal, predoff, normal
      (F23c ran normal first); N_diff by own numpy code (pixel = 8 bytes -> one uint64);
  guard: the runner is killed when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP appears (poll 0.5 s).
Output: C:/kyty/f287/f23d/h_f23d.out.txt"""
import hashlib
import os
import struct
import subprocess
import sys
import time

import numpy as np

S = 'C:/kyty/f287/f23c/'
W = S + 'work/'
D = 'C:/kyty/f287/f23d/'
OUT = D + 'h_f23d.out.txt'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
lines = []


def log(s):
    print(s, flush=True)
    lines.append(s)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


EXPECT = {
    'f23c_hrun.exe': 'cffb14017c77d97263a651e191b10d6547d01d1e736787c454e31949e043e95b',
    'work/vs_tri.spv': '02b8bf84911ffd66e631f88127ff00a3427124c00aa87c10636c061007dcc37d',
    'work/ref_normal.spv': 'f62b88f82f1ca942c01d0f4de3c64a5b8d20ed124503c1e316995a43d7b077d9',
    'work/ref_predoff.spv': '83341d3d9940dbc824a1935a6bf7ce845d8eca264f5c5bef4da943bcc39ad46c',
    'work/ref_ctrue_formA.spv': '73ce291295c8d674100d93edf1161208cf90fe297a84a173c24b3eeeb653ef16',
    'work/ref_blend_formA.spv': '0c775634c6c73dfc0bf9556bcea55b0db909ea45fb8b331c3b4c62505084dd7f',
    'work/ref_sens_both.spv': '30547b7539755744cc95a5a8383b7446a91aadab95bb26d0323b9b1142dd614a',
}


def words(p):
    b = open(p, 'rb').read()
    return list(struct.unpack('<%dI' % (len(b) // 4), b))


def insts(w):
    i = 5
    while i < len(w):
        n = w[i] >> 16
        yield i, w[i] & 0xffff, w[i + 1:i + n]
        i += n


def main():
    ok = True
    log('F23d H repeat %s' % time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    for rel, exp in EXPECT.items():
        got = sha(S + rel)
        log('sha256 %-26s %s %s' % (rel, got, 'OK' if got == exp else 'MISMATCH'))
        ok &= got == exp
    pre = words(W + 'ref_predoff.spv')
    true_id = [ops[1] for _, op, ops in insts(pre) if op == 41]
    sel = {ops[1]: (off, ops) for off, op, ops in insts(pre) if op == 169}
    for name, kind in (('ctrue_formA', 'cond'), ('sens_both', 'swap')):
        w = words(W + 'ref_%s.spv' % name)
        diff = [k for k in range(min(len(w), len(pre))) if w[k] != pre[k]]
        exp = set()
        for rid in (286, 306):
            off, ops = sel[rid]
            if kind == 'cond':
                exp.add(off + 3)
            else:
                exp |= {off + 4, off + 5}
        good = len(w) == len(pre) and set(diff) == exp
        if kind == 'cond':
            good &= all(w[k] == true_id[0] for k in diff)
        else:
            good &= all(w[sel[r][0] + 4] == sel[r][1][4] and w[sel[r][0] + 5] == sel[r][1][3] for r in (286, 306))
        log('word diff %s vs predoff: %d words at %s, expected %s -> %s' % (name, len(diff), diff, sorted(exp), 'OK' if good else 'BAD'))
        ok &= good
    if not ok:
        log('INPUT CHECK FAILED')
        return finish(False)
    order = ['predoff', 'ctrue_formA', 'blend_formA', 'sens_both', 'normal', 'predoff', 'normal']
    args = [S + 'f23c_hrun.exe', '--vs', W + 'vs_tri.spv', '--tex', W + 'tex_noise_1920x1620.r8', '--texw', '1920', '--texh', '1620',
            '--rtw', '1920', '--rth', '1080', '--fmt', '16', '--filter', 'nearest', '--cbw', '1920']
    outs = []
    for k, v in enumerate(order):
        o = D + 'o_%d_%s.bin' % (k, v)
        args += ['--job', W + 'ref_%s.spv' % v, o, '0']
        outs.append((v, o))
    env = dict(os.environ)
    env['__GL_SHADER_DISK_CACHE'] = '0'
    if os.path.exists(LOCK) or os.path.exists(STOP):
        log('lock or STOP before start')
        return finish(False)
    t0 = time.time()
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    killed = None
    while p.poll() is None:
        if os.path.exists(LOCK) or os.path.exists(STOP):
            p.kill()
            killed = 'lock' if os.path.exists(LOCK) else 'STOP'
            break
        time.sleep(0.5)
    txt = p.communicate()[0].decode('latin1')
    log('runner rc %s wall %.1f s killed %s' % (p.returncode, time.time() - t0, killed))
    for l in txt.splitlines():
        if l.startswith(('device ', 'picked', 'validation', 'FAIL')):
            log('   ' + l)
    if killed or p.returncode != 0:
        return finish(False)
    px = {}
    for k, (v, o) in enumerate(outs):
        a = np.fromfile(o, dtype=np.uint64)
        px[k] = a
        log('job %d %-12s sha256 %s pixels %d' % (k, v, hashlib.sha256(a.tobytes()).hexdigest(), a.size))
        os.remove(o)

    def nd(i, j):
        return int(np.count_nonzero(px[i] != px[j]))

    rows = [('null normal (job 4 vs 6)', nd(4, 6), '== 0'), ('null predoff (job 0 vs 5)', nd(0, 5), '== 0'),
            ('H normal vs predoff (job 4 vs 0)', nd(4, 0), '> 0'), ('ctrue_formA vs normal (1 vs 4)', nd(1, 4), '== 0'),
            ('blend_formA vs normal (2 vs 4)', nd(2, 4), '== 0'), ('sens_both vs predoff (3 vs 0)', nd(3, 0), '> 0'),
            ('sens_both vs normal (3 vs 4)', nd(3, 4), '> 0')]
    for name, n, want in rows:
        good = (n == 0) if want == '== 0' else (n > 0)
        log('%-34s N_diff %9d  expect %s -> %s' % (name, n, want, 'OK' if good else 'BAD'))
        ok &= good
    log('F23c c07 for comparison: H 2064897, null 0/0, ctrue_formA 0, blend_formA 0, sens_both(vs predoff) 2073600')
    return finish(ok)


def finish(ok):
    log('ALL OK' if ok else 'NOT OK')
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
