"""F23c (HPP-587, ROADMAP s122 item 493(g)(1)): historical control H on the reference PS 0xe197e307a5f2cb39.

Inputs of the step (made by this script, equal for all jobs of one runner process):
  - SPIR-V: work/ref_normal.spv (main b6858d6d translation by default), work/ref_predoff.spv (KYTY_PRED_ELIM=0);
    sensitivity variants made here from ref_predoff.spv: the two form-A selects (%286 = select(%167, U, Y-coordinate y),
    %306 = select(%167, V, Y-coordinate x)) get their two value operands swapped, so on active lanes they return
    `old` - sens_both, sens_286, sens_306 (spirv-val with --uniform-buffer-standard-layout before use);
  - synthetic NV12 frames (one R8 image of W x 1.5H rows, as the reference samples it): noise (seeded PCG64),
    grad (Y = (x + 3y) mod 256, chroma = (5x xor 7y) mod 256), rows (every row constant in Y: (37r + 11) mod 256,
    chroma (53r + x) mod 256 - a row read from a wrong place shows up at once).
Runner: f23c_hrun.exe (one process per configuration; every job = own shader module + own pipeline + own draw).
Measure: N_diff(a, b) = pixels of the target whose bytes differ in any channel.
Rows: null controls (same SPIR-V twice: normal/normal2, predoff/predoff2), H (normal vs predoff), sensitivity
(predoff vs sens_*), and the DISABLE_OPTIMIZATION pipelines of both (reference candidate of stage 2, item (2)).
Output: h_f23c.out.txt (+ h_f23c.json); the raw targets are deleted after hashing (sha256 kept)."""
import hashlib
import json
import os
import struct
import subprocess
import sys
import time

import numpy as np

D = 'C:/kyty/f287/f23c/'
W = D + 'work/'
SPV_VAL = 'C:/VulkanSDK/1.4.357.0/Bin/spirv-val.exe'
RUN = D + 'f23c_hrun.exe'
OUT = D + 'h_f23c.out.txt'
lines = []


def log(s):
    print(s, flush=True)
    lines.append(s)


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


# ---- SPIR-V sensitivity variants -------------------------------------------------------------------------------
OP_SELECT = 169


def parse(words):
    """yields (offset, opcode, operands) for every instruction after the 5-word header"""
    i = 5
    while i < len(words):
        n = words[i] >> 16
        op = words[i] & 0xffff
        yield i, op, words[i + 1:i + n]
        i += n


def defs(words):
    """result id -> (opcode, operands) for instructions with <type, result> layout (opcodes used below only)"""
    d = {}
    for off, op, ops in parse(words):
        if op in (OP_SELECT, 81, 124, 87, 80):  # Select, CompositeExtract, Bitcast, ImageSampleImplicitLod, CompositeConstruct
            d[ops[1]] = (op, ops)
    return d


def make_sens(src, dst, targets):
    data = open(src, 'rb').read()
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    d = defs(words)
    done = []
    for off, op, ops in parse(words):
        if op == OP_SELECT and ops[1] in targets:
            cond, a, b = ops[2], ops[3], ops[4]
            exp_cond, exp_new, exp_old = targets[ops[1]]
            assert (cond, a, b) == (exp_cond, exp_new, exp_old), (ops[1], cond, a, b)
            # new = CompositeExtract 0 of CompositeConstruct of Bitcast of CompositeExtract of an ImageSample
            assert d[a][0] == 81, d[a]
            words[off + 4], words[off + 5] = b, a
            done.append(ops[1])
    assert sorted(done) == sorted(targets), done
    with open(dst, 'wb') as f:
        f.write(struct.pack('<%dI' % len(words), *words))
    return done


def make_ctrue(src, dst, only=None):
    """condition control: OpSelect with condition %167 (EXEC of the stage = quad-expanded ballot of non-helper lanes,
    true on every invocation that writes a pixel) get the constant true as condition - all of them (only=None) or the
    listed result ids; the values of written pixels are the same by SPIR-V semantics"""
    data = open(src, 'rb').read()
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    true_id = [ops[1] for off, op, ops in parse(words) if op == 41]
    assert len(true_id) == 1, true_id
    n = 0
    for off, op, ops in parse(words):
        if op == OP_SELECT and ops[2] == 167 and (only is None or ops[1] in only):
            words[off + 3] = true_id[0]
            n += 1
    with open(dst, 'wb') as f:
        f.write(struct.pack('<%dI' % len(words), *words))
    return n


def chain(words, rid, depth=6):
    d = defs(words)
    out = []
    cur = rid
    for _ in range(depth):
        if cur not in d:
            out.append('%%%d(def outside)' % cur)
            break
        op, ops = d[cur]
        name = {OP_SELECT: 'Select', 81: 'CompositeExtract', 124: 'Bitcast', 87: 'ImageSampleImplicitLod', 80: 'CompositeConstruct'}[op]
        out.append('%%%d=%s' % (cur, name))
        if op == 87:
            break
        cur = ops[2]
    return ' <- '.join(out)


# Form-A selects of ref_predoff.spv (b8_forms_predoff.tsv: 2 elements; ids from spirv-dis of this file):
TARGETS = {286: (167, 285, 196), 306: (167, 305, 224)}


def prepare_spirv():
    src = W + 'ref_predoff.spv'
    data = open(src, 'rb').read()
    words = list(struct.unpack('<%dI' % (len(data) // 4), data))
    for rid in TARGETS:
        log('form-A select %%%d: new chain %s' % (rid, chain(words, TARGETS[rid][1])))
    variants = {'sens_both': TARGETS, 'sens_286': {286: TARGETS[286]}, 'sens_306': {306: TARGETS[306]}}
    for name, t in variants.items():
        dst = W + 'ref_%s.spv' % name
        done = make_sens(src, dst, t)
        r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', dst], capture_output=True, text=True)
        log('variant %s: swapped %s, spirv-val rc %d %s, sha256 %s' % (name, done, r.returncode, (r.stdout + r.stderr).strip()[:200], sha(dst)))
        assert r.returncode == 0
    for name, only in (('ctrue_all', None), ('ctrue_formA', set(TARGETS))):
        dst = W + 'ref_%s.spv' % name
        n = make_ctrue(src, dst, only)
        r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', dst], capture_output=True, text=True)
        log('variant %s: %d select conditions %%167 -> constant true, spirv-val rc %d, sha256 %s' % (name, n, r.returncode, sha(dst)))
        assert r.returncode == 0
    sys.path.insert(0, D)
    import phi_f23c
    for name, base, kw in (('phi_formA', 'predoff', {'select_ids': set(TARGETS)}), ('phi_all', 'predoff', {'cond_id': 167}),
                           ('phi_normal', 'normal', {'cond_id': 167}), ('blend_formA', 'predoff', {'select_ids': set(TARGETS)}),
                           ('blend_all', 'predoff', {'cond_id': 167})):
        dst = W + 'ref_%s.spv' % name
        fn = phi_f23c.blend if name.startswith('blend') else phi_f23c.rewrite
        out, done = fn(open(W + 'ref_%s.spv' % base, 'rb').read(), **kw)
        open(dst, 'wb').write(out)
        r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', dst], capture_output=True, text=True)
        log('variant %s (from %s): %d OpSelect -> %s, spirv-val rc %d %s, sha256 %s' % (
            name, base, len(done), 'bit blend' if name.startswith('blend') else 'branch + OpPhi', r.returncode, (r.stdout + r.stderr).strip()[:300], sha(dst)))
        assert r.returncode == 0
    for v in ('normal', 'normal2', 'predoff', 'predoff2'):
        p = W + 'ref_%s.spv' % v
        r = subprocess.run([SPV_VAL, '--target-env', 'vulkan1.3', '--uniform-buffer-standard-layout', p], capture_output=True, text=True)
        log('spirv %s: sha256 %s, %d bytes, spirv-val rc %d' % (v, sha(p), os.path.getsize(p), r.returncode))
        assert r.returncode == 0


# ---- synthetic NV12 frames ----------------------------------------------------------------------------------------
def make_tex(pattern, w, h):
    th = h * 3 // 2
    path = W + 'tex_%s_%dx%d.r8' % (pattern, w, th)
    if os.path.exists(path):
        return path, th
    if pattern == 'noise':
        img = np.random.Generator(np.random.PCG64(0xF23C)).integers(0, 256, size=(th, w), dtype=np.uint8)
    elif pattern == 'grad':
        y, x = np.mgrid[0:th, 0:w]
        img = ((x + 3 * y) % 256).astype(np.uint8)
        img[h:, :] = (((5 * x) ^ (7 * y)) % 256)[h:, :].astype(np.uint8)
    elif pattern == 'rows':
        y, x = np.mgrid[0:th, 0:w]
        img = ((37 * y + 11) % 256).astype(np.uint8)
        img[h:, :] = ((53 * y + x) % 256)[h:, :].astype(np.uint8)
    else:
        raise ValueError(pattern)
    img.tofile(path)
    return path, th


# ---- runs ---------------------------------------------------------------------------------------------------------
JOBS = [('normal', 0), ('normal2', 0), ('predoff', 0), ('predoff2', 0), ('sens_both', 0), ('sens_286', 0), ('sens_306', 0),
        ('normal', 1), ('predoff', 1), ('ctrue_all', 0), ('ctrue_formA', 0),
        ('phi_formA', 0), ('phi_all', 0), ('phi_normal', 0), ('phi_formA', 1),
        ('blend_formA', 0), ('blend_all', 0)]
CONFIGS = [
    # name, pattern, video w, h, filter, fmt, vs
    ('c01', 'noise', 3840, 2160, 'nearest', 32, 'tri'),
    ('c02', 'noise', 3840, 2160, 'linear', 32, 'tri'),
    ('c03', 'grad', 3840, 2160, 'nearest', 32, 'tri'),
    ('c04', 'grad', 3840, 2160, 'linear', 32, 'tri'),
    ('c05', 'rows', 3840, 2160, 'nearest', 32, 'tri'),
    ('c06', 'rows', 3840, 2160, 'linear', 32, 'tri'),
    ('c07', 'noise', 1920, 1080, 'nearest', 16, 'tri'),
    ('c08', 'noise', 1920, 1080, 'linear', 16, 'tri'),
    ('c09', 'noise', 3840, 2160, 'nearest', 32, 'diamond'),
]


def ndiff(a, b, bpp):
    pa = a.reshape(-1, bpp)
    pb = b.reshape(-1, bpp)
    return int(np.count_nonzero(np.any(pa != pb, axis=1)))


def run_config(cfg, validate=False):
    name, pattern, w, h, filt, fmt, vs = cfg
    tex, th = make_tex(pattern, w, h)
    bpp = 16 if fmt == 32 else 8
    args = [RUN, '--vs', W + 'vs_%s.spv' % vs, '--tex', tex, '--texw', str(w), '--texh', str(th), '--rtw', str(w), '--rth', str(h),
            '--fmt', str(fmt), '--filter', filt, '--cbw', '%d' % w]
    if validate:
        args.append('--validate')
    outs = []
    for k, (v, fl) in enumerate(JOBS):
        o = W + 'out_%s_%d_%s_f%d.bin' % (name, k, v, fl)
        args += ['--job', W + 'ref_%s.spv' % v, o, str(fl)]
        outs.append((v, fl, o))
    env = dict(os.environ)
    env['__GL_SHADER_DISK_CACHE'] = '0'
    if validate:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    t0 = time.time()
    r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=400)
    dt = time.time() - t0
    txt = r.stdout + r.stderr
    dev_lines = [l for l in txt.splitlines() if l.startswith(('device ', 'picked'))]
    val = [l for l in txt.splitlines() if l.startswith('VALIDATION') or l.startswith('validation errors')]
    res = {'cfg': name, 'pattern': pattern, 'video': '%dx%d' % (w, h), 'tex': '%dx%d' % (w, th), 'tex_sha': sha(tex), 'filter': filt,
           'fmt': fmt, 'vs': vs, 'rc': r.returncode, 'wall_s': round(dt, 1), 'validate': validate, 'devices': dev_lines,
           'validation': val[:20]}
    if r.returncode != 0:
        log('%s: runner rc %d\n%s' % (name, r.returncode, txt[-3000:]))
        res['ok'] = False
        return res
    data = {}
    shas = {}
    for v, fl, o in outs:
        b = np.fromfile(o, dtype=np.uint8)
        data[(v, fl)] = b
        shas['%s_f%d' % (v, fl)] = hashlib.sha256(b.tobytes()).hexdigest()
    npx = w * h
    base = data[('normal', 0)]
    if fmt == 32:
        f = base.view(np.float32).reshape(-1, 4)
    else:
        f = base.view(np.float16).astype(np.float32).reshape(-1, 4)
    unwritten = int(np.count_nonzero(np.all(f == -7.0, axis=1)))
    res.update({
        'pixels': npx,
        'unwritten_normal': unwritten,
        'stats_normal': 'R %.4f..%.4f G %.4f..%.4f B %.4f..%.4f A %.4f..%.4f distinct-R %d' % (
            f[:, 0].min(), f[:, 0].max(), f[:, 1].min(), f[:, 1].max(), f[:, 2].min(), f[:, 2].max(), f[:, 3].min(), f[:, 3].max(),
            len(np.unique(f[:, 0]))),
        'null_normal': ndiff(data[('normal', 0)], data[('normal2', 0)], bpp),
        'null_predoff': ndiff(data[('predoff', 0)], data[('predoff2', 0)], bpp),
        'H': ndiff(data[('normal', 0)], data[('predoff', 0)], bpp),
        'sens_both': ndiff(data[('predoff', 0)], data[('sens_both', 0)], bpp),
        'sens_286': ndiff(data[('predoff', 0)], data[('sens_286', 0)], bpp),
        'sens_306': ndiff(data[('predoff', 0)], data[('sens_306', 0)], bpp),
        'noopt_normal_vs_normal': ndiff(data[('normal', 0)], data[('normal', 1)], bpp),
        'noopt_predoff_vs_predoff': ndiff(data[('predoff', 0)], data[('predoff', 1)], bpp),
        'noopt_predoff_vs_normal': ndiff(data[('normal', 0)], data[('predoff', 1)], bpp),
        'ctrue_all_vs_normal': ndiff(data[('normal', 0)], data[('ctrue_all', 0)], bpp),
        'ctrue_formA_vs_normal': ndiff(data[('normal', 0)], data[('ctrue_formA', 0)], bpp),
        'phi_formA_vs_normal': ndiff(data[('normal', 0)], data[('phi_formA', 0)], bpp),
        'phi_all_vs_normal': ndiff(data[('normal', 0)], data[('phi_all', 0)], bpp),
        'phi_normal_vs_normal': ndiff(data[('normal', 0)], data[('phi_normal', 0)], bpp),
        'phi_formA_noopt_vs_normal': ndiff(data[('normal', 0)], data[('phi_formA', 1)], bpp),
        'blend_formA_vs_normal': ndiff(data[('normal', 0)], data[('blend_formA', 0)], bpp),
        'blend_all_vs_normal': ndiff(data[('normal', 0)], data[('blend_all', 0)], bpp),
        'sha': shas,
    })
    res['ok'] = res['null_normal'] == 0 and res['null_predoff'] == 0 and res['sens_both'] > 0
    for v, fl, o in outs:
        os.remove(o)
    log('%s %-5s %s %-7s fmt%d %-7s rc %d %.1f s val=%s | null %d/%d | H %d | sens both/286/306 %d/%d/%d | noopt n/p/p-vs-n %d/%d/%d | ctrue all/A vs normal %d/%d | phi A/all/normal/A-noopt vs normal %d/%d/%d/%d | blend A/all vs normal %d/%d | unwritten %d of %d | %s' % (
        name, pattern, res['video'], filt, fmt, vs, r.returncode, dt, 'on' if validate else 'off', res['null_normal'], res['null_predoff'],
        res['H'], res['sens_both'], res['sens_286'], res['sens_306'], res['noopt_normal_vs_normal'], res['noopt_predoff_vs_predoff'],
        res['noopt_predoff_vs_normal'], res['ctrue_all_vs_normal'], res['ctrue_formA_vs_normal'],
        res['phi_formA_vs_normal'], res['phi_all_vs_normal'], res['phi_normal_vs_normal'], res['phi_formA_noopt_vs_normal'],
        res['blend_formA_vs_normal'], res['blend_all_vs_normal'], unwritten, npx, res['stats_normal']))
    if validate:
        log('   validation lines: %s' % (val[:5],))
    return res


def main():
    log('F23c H run %s; runner sha256 %s; vs_tri %s; vs_diamond %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), sha(RUN),
                                                                       sha(W + 'vs_tri.spv'), sha(W + 'vs_diamond.spv')))
    prepare_spirv()
    only = sys.argv[1:]
    results = []
    for i, cfg in enumerate(CONFIGS):
        if only and cfg[0] not in only:
            continue
        results.append(run_config(cfg))
        if i == 0:
            for l in results[-1].get('devices', []):
                log('   ' + l)
    # one validation run (layer on) of the first configuration
    if not only or 'val' in only:
        results.append(run_config(CONFIGS[0], validate=True))
    allok = all(r.get('ok') for r in results)
    hsum = sum(r.get('H', 0) for r in results)
    log('SUMMARY: configurations %d, controls alive in all %s, H total %d, H > 0 in %d configurations' % (
        len(results), allok, hsum, sum(1 for r in results if r.get('H', 0) > 0)))
    log('ALL OK' if allok else 'CONTROL FAILURE')
    json.dump(results, open(D + 'h_f23c.json', 'w'), indent=1)
    open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
