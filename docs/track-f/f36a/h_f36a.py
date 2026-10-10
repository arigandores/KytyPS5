"""F36a (HPP-758; copy of f23f/h_f23f.py with D -> f36a, output h_f36a.*; rewriter refs_f23f.py unchanged); was F23f (HPP-592, ROADMAP s122 item 498(g)(1)): positive check of the two references of RC1 on H BEFORE the game programs.
From ref_predoff.spv of F23c (reference PS 0xe197e307a5f2cb39, KYTY_PRED_ELIM=0; form-A sites %286 = select(%167, %285, %196),
%306 = select(%167, %305, %224)) the references (a) 'mask' and (b) 'mem' of refs_f23f.py are built; each must be = normal and
!= predoff byte for byte (N_diff over pixels) on the configurations c01, c07, c09 of the F23c stand (f23c_hrun.exe, its
inputs and VS - F23c files, unchanged). Null control normal/normal2 = 0 and H (normal/predoff) > 0 are repeated in the same
process. Structural checks: no OpSelect left at %286/%306, no OpPhi added, spirv-val (vulkan1.3, standard layout) rc 0.
Output: h_f36a.out.txt, h_f36a.json, work/ref_mask.spv, work/ref_mem.spv (+ .spvasm). Item 498(d)(i): a failure = one method
fix inside F23f, a second failure = stop and report."""
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, 'C:/kyty/f287/f23f')
import refs_f23f as R  # noqa: E402

D = 'C:/kyty/f287/f36a/'
C = 'C:/kyty/f287/f23c/'
W = D + 'work/'
CW = C + 'work/'
SPV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
SPV_DIS = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-dis.exe'
RUN = C + 'f23c_hrun.exe'
SITES = [(286, 167, 285, 196), (306, 167, 305, 224)]
CONFIGS = [('c01', 'noise', 3840, 2160, 'nearest', 32, 'tri'),
           ('c07', 'noise', 1920, 1080, 'nearest', 16, 'tri'),
           ('c09', 'noise', 3840, 2160, 'nearest', 32, 'diamond')]
lines = []


def log(s):
    print(s, flush=True)
    lines.append(s)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def count_ops(path, op):
    return sum(1 for x in R.instrs(R.words_of(open(path, 'rb').read())) if x[0] & 0xffff == op)


def ndiff(a, b, bpp):
    return int(np.count_nonzero(np.any(a.reshape(-1, bpp) != b.reshape(-1, bpp), axis=1)))


def main():
    os.makedirs(W, exist_ok=True)
    log('F36a H check %s; stand %s sha256 %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), RUN, sha(RUN)))
    src = CW + 'ref_predoff.spv'
    base = open(src, 'rb').read()
    for v in ('normal', 'normal2', 'predoff'):
        log('input %s sha256 %s' % (v, sha(CW + 'ref_%s.spv' % v)))
    ok = True
    for kind in ('mask', 'mem'):
        out, n = R.rewrite(base, SITES, kind)
        p = W + 'ref_%s.spv' % kind
        open(p, 'wb').write(out)
        left = R.selects_at(out, [s[0] for s in SITES])
        r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', p], capture_output=True, text=True)
        subprocess.run([SPV_DIS, '--raw-id', p, '-o', p + 'asm'], capture_output=True)
        phi0, phi1 = count_ops(src, 245), count_ops(p, 245)
        sel0, sel1 = count_ops(src, 169), count_ops(p, 169)
        good = n == 2 and not left and r.returncode == 0 and phi1 == phi0 and sel1 == sel0 - 2
        ok &= good
        log('reference %s: rewritten %d, OpSelect left at sites %s, OpSelect %d -> %d, OpPhi %d -> %d, spirv-val rc %d %s, sha256 %s, %d bytes %s' % (
            kind, n, left, sel0, sel1, phi0, phi1, r.returncode, (r.stdout + r.stderr).strip()[:300], sha(p), len(out),
            'OK' if good else 'FAIL'))
    jobs = [('normal', CW + 'ref_normal.spv'), ('normal2', CW + 'ref_normal2.spv'), ('predoff', CW + 'ref_predoff.spv'),
            ('mask', W + 'ref_mask.spv'), ('mem', W + 'ref_mem.spv')]
    results = []
    for name, pattern, w, h, filt, fmt, vs in CONFIGS:
        th = h * 3 // 2
        tex = CW + 'tex_%s_%dx%d.r8' % (pattern, w, th)
        bpp = 16 if fmt == 32 else 8
        args = [RUN, '--vs', CW + 'vs_%s.spv' % vs, '--tex', tex, '--texw', str(w), '--texh', str(th), '--rtw', str(w), '--rth', str(h),
                '--fmt', str(fmt), '--filter', filt, '--cbw', '%d' % w]
        outs = []
        for k, (v, p) in enumerate(jobs):
            o = W + 'hout_%s_%d_%s.bin' % (name, k, v)
            args += ['--job', p, o, '0']
            outs.append((v, o))
        env = dict(os.environ)
        env['__GL_SHADER_DISK_CACHE'] = '0'
        t0 = time.time()
        r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=400)
        dt = time.time() - t0
        if r.returncode != 0:
            log('%s: stand rc %d %s' % (name, r.returncode, (r.stdout + r.stderr)[-2000:]))
            ok = False
            continue
        dev = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith(('device ', 'picked'))]
        data = {v: np.fromfile(o, dtype=np.uint8) for v, o in outs}
        shas = {v: hashlib.sha256(data[v].tobytes()).hexdigest() for v in data}
        res = dict(cfg=name, tex_sha=sha(tex), wall_s=round(dt, 1), devices=dev, sha=shas,
                   null=ndiff(data['normal'], data['normal2'], bpp), H=ndiff(data['normal'], data['predoff'], bpp),
                   mask_vs_normal=ndiff(data['mask'], data['normal'], bpp), mask_vs_predoff=ndiff(data['mask'], data['predoff'], bpp),
                   mem_vs_normal=ndiff(data['mem'], data['normal'], bpp), mem_vs_predoff=ndiff(data['mem'], data['predoff'], bpp),
                   mask_vs_mem=ndiff(data['mask'], data['mem'], bpp), pixels=w * h)
        good = (res['null'] == 0 and res['H'] > 0 and res['mask_vs_normal'] == 0 and res['mask_vs_predoff'] > 0 and
                res['mem_vs_normal'] == 0 and res['mem_vs_predoff'] > 0)
        res['ok'] = good
        ok &= good
        results.append(res)
        for v, o in outs:
            os.remove(o)
        log('%s %s %dx%d %s fmt%d %s %.1f s | null %d | H %d | mask vs normal %d, vs predoff %d | mem vs normal %d, vs predoff %d | mask vs mem %d | %s' % (
            name, pattern, w, h, filt, fmt, vs, dt, res['null'], res['H'], res['mask_vs_normal'], res['mask_vs_predoff'],
            res['mem_vs_normal'], res['mem_vs_predoff'], res['mask_vs_mem'], 'OK' if good else 'FAIL'))
        if name == 'c01':
            for l in dev:
                log('   ' + l)
    json.dump(results, open(D + 'h_f36a.json', 'w'), indent=1)
    log('ALL OK' if ok else 'FAILED')
    open(D + 'h_f36a.out.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
