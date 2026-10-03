"""F12d (HPP-477, ROADMAP s122 item 391(g)(3)): offline translation of the T1 corpus (C:/kyty/s288/s7, form of S7/F10c)
by the build without the fix (base) and by the build with it at KYTY_FIX_F10=0 and =1.

Rows: the A rows of t1_base.tsv (GCN dump + translation cache file of the 56189185 signature, one row per permutation)
whose S7 outcome is not HARNESS_UNSUPPORTED (the KYTY_RECOMPILE path takes CS and PS only). Each row is translated by
KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;<perm>" in a separate process of shader_cfg_tests, all other KYTY_*
variables removed, in the configurations
  base      base exe, KYTY_FIX_F10 not set
  f0        fix exe, KYTY_FIX_F10=0
  fu        fix exe, KYTY_FIX_F10 not set
  f1        fix exe, KYTY_FIX_F10=1
and, for the BVH programs only (t1scan_f11a.tsv bvh > 0), the same four at KYTY_BVH_NATIVE=0 (IR path): base_ir, f0_ir,
fu_ir, f1_ir. Gates (all must hold, ALL OK):
  G1  every process rc 0 and out.spv written;
  G2  f0 == base and fu == base byte for byte on every row (both paths);
  G3  f1 != base exactly on the rows of the BVH programs (native path; IR path: every BVH row differs);
  G4  every program with a differing f1 row is a BVH program, every BVH program has a differing f1 row;
  G5  380bb9d636390bae is in the corpus; its SPIR-V of base, f0, f1 (all permutations) kept with sha256.
Usage: python corpus_f12d.py <base exe> <fix exe> <out dir> [--workers N]. Rule 27: before every process the lock
C:/kyty/SEALED_RUN.lock and C:/kyty/f287/STOP are checked; found -> stop, exit 5 / 4 (rows done so far are kept).
"""
import argparse
import collections
import concurrent.futures as cf
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
SCAN = 'C:/kyty/KytyPS5/docs/track-f/f11a/t1scan_f11a.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
TIMEOUT = 180
P380 = '380bb9d636390bae'


class Halt(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def check_halt():
    if os.path.exists(STOP):
        raise Halt('STOP')
    if os.path.exists(LOCK):
        raise Halt('LOCK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base_exe')
    ap.add_argument('fix_exe')
    ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=6)
    args = ap.parse_args()
    t_start = time.time()
    check_halt()

    with open(T1, encoding='ascii') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        rows_all = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
    rows = [r for r in rows_all if r['row'] == 'A' and r['outcome'] != 'HARNESS_UNSUPPORTED' and r['perm'] != '-']
    skipped = [r for r in rows_all if r['row'] == 'A' and r not in rows]
    with open(SCAN, encoding='ascii') as f:
        shdr = f.readline().rstrip('\n').split('\t')
        scan = [dict(zip(shdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
    bvh = sorted({s['hash16'] for s in scan if s['bvh'] not in ('', '0')})
    print('t1 rows', len(rows_all), 'A rows run', len(rows), 'A rows skipped (HARNESS_UNSUPPORTED/probe)', len(skipped),
          'stages', dict(collections.Counter(r['stage'] for r in rows)))
    print('BVH programs (t1scan_f11a bvh > 0):', len(bvh), ' '.join(bvh))
    in_corpus_bvh = sorted({r['hash16'] for r in rows if r['hash16'] in bvh})
    print('BVH programs with run rows:', len(in_corpus_bvh), ' '.join(in_corpus_bvh))

    def gcn_path(r):
        for arm in r['gcn_arms'].split(','):
            p = '%s/%s/%s_%s.bin' % (GCN_ROOT, arm, r['stage'], r['hash16'])
            if os.path.exists(p) and os.path.getsize(p) > 0:
                if sha256_file(p) != r['gcn_sha256']:
                    raise SystemExit('GCN sha mismatch ' + p)
                return p
        raise SystemExit('no GCN for ' + r['hash16'])

    def cache_path(r):
        p = '%s/%s_%s_%s.bin' % (CACHE_CUR, r['stage'], r['hash16'], r['key16'])
        if sha256_file(p) != r['cache_sha256']:
            raise SystemExit('cache sha mismatch ' + p)
        return p

    configs = [('base', args.base_exe, None, None), ('f0', args.fix_exe, '0', None), ('fu', args.fix_exe, None, None),
               ('f1', args.fix_exe, '1', None)]
    configs_ir = [(c + '_ir', exe, v, '0') for c, exe, v, _ in configs]
    jobs = []
    for r in rows:
        rid = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
        g, c = gcn_path(r), cache_path(r)
        for cfg in configs + (configs_ir if r['hash16'] in bvh else []):
            jobs.append((rid, r, g, c, cfg))
    print('processes', len(jobs))
    os.makedirs(args.out, exist_ok=True)
    results = {}
    lock = threading.Lock()

    def run(job):
        rid, r, g, c, (name, exe, f10, native) = job
        check_halt()
        work = '%s/%s/%s' % (args.out, name, rid)
        os.makedirs(work, exist_ok=True)
        spv = work + '/out.spv'
        if os.path.exists(spv):
            os.remove(spv)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (g, c, spv, r['perm'])
        if f10 is not None:
            env['KYTY_FIX_F10'] = f10
        if native is not None:
            env['KYTY_BVH_NATIVE'] = native
        try:
            p = subprocess.run([exe], cwd=work, env=env, capture_output=True, timeout=TIMEOUT)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, out, err = 'timeout', e.stdout or b'', e.stderr or b''
        with open(work + '/stdout.txt', 'wb') as f:
            f.write(out)
        with open(work + '/stderr.txt', 'wb') as f:
            f.write(err)
        sha = sha256_file(spv) if (rc == 0 and os.path.exists(spv)) else None
        with lock:
            results[(rid, name)] = {'rc': rc, 'sha': sha}

    halted = None
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for fu in cf.as_completed(futs):
            try:
                fu.result()
            except Halt as h:
                halted = str(h)
                for g2 in futs:
                    g2.cancel()
    if halted:
        print('HALT', halted)
        sys.exit(5 if halted == 'LOCK' else 4)

    ok = True
    rids = sorted({j[0] for j in jobs})
    by_rid = {j[0]: j[1] for j in jobs}
    # G1
    bad = [(k, v) for k, v in results.items() if v['rc'] != 0 or v['sha'] is None]
    print('G1 processes', len(results), 'failed', len(bad), bad[:5])
    ok &= not bad and len(results) == len(jobs)
    table = []
    diff_prog = set()
    for rid in rids:
        r = by_rid[rid]
        is_bvh = r['hash16'] in bvh
        for suffix in ('', '_ir'):
            if suffix and not is_bvh:
                continue
            b = results[(rid, 'base' + suffix)]['sha']
            f0 = results[(rid, 'f0' + suffix)]['sha']
            fu = results[(rid, 'fu' + suffix)]['sha']
            f1 = results[(rid, 'f1' + suffix)]['sha']
            table.append('\t'.join([rid, r['stage'], r['hash16'], r['perm'], 'ir' if suffix else 'native',
                                    '1' if is_bvh else '0', b, f0, fu, f1, str(int(f0 == b)), str(int(fu == b)),
                                    str(int(f1 != b))]))
            if f1 != b and not suffix:
                diff_prog.add(r['hash16'])
    tsv = args.out + '/corpus_f12d.tsv'
    with open(tsv, 'w', encoding='ascii', newline='\n') as f:
        f.write('\t'.join(['row', 'stage', 'hash16', 'perm', 'path', 'bvh', 'sha_base', 'sha_f0', 'sha_unset', 'sha_f1',
                           'f0_eq_base', 'unset_eq_base', 'f1_ne_base']) + '\n')
        f.write('\n'.join(table) + '\n')
    cols = [line.split('\t') for line in table]
    g2 = [c for c in cols if c[10] != '1' or c[11] != '1']
    print('G2 rows (native + ir)', len(cols), 'f0/unset != base:', len(g2), [c[0] + '/' + c[4] for c in g2[:5]])
    ok &= not g2
    g3_bad = [c for c in cols if (c[5] == '1') != (c[12] == '1')]
    n_bvh_rows = sum(1 for c in cols if c[5] == '1')
    print('G3 BVH rows', n_bvh_rows, '(native', sum(1 for c in cols if c[5] == '1' and c[4] == 'native'), 'ir',
          sum(1 for c in cols if c[4] == 'ir'), ') f1 != base on BVH rows',
          sum(1 for c in cols if c[5] == '1' and c[12] == '1'), '; non-BVH rows', len(cols) - n_bvh_rows,
          'f1 == base', sum(1 for c in cols if c[5] == '0' and c[12] == '0'), '; violations', len(g3_bad),
          [c[0] + '/' + c[4] for c in g3_bad[:5]])
    ok &= not g3_bad
    g4a = sorted(diff_prog - set(bvh))
    g4b = sorted(set(in_corpus_bvh) - diff_prog)
    print('G4 programs with a differing f1 row', len(diff_prog), 'not BVH', g4a, '; BVH without a difference', g4b)
    ok &= not g4a and not g4b
    keep = args.out + '/spv380'
    os.makedirs(keep, exist_ok=True)
    lines380 = []
    for rid in rids:
        if by_rid[rid]['hash16'] != P380:
            continue
        for name in ('base', 'f0', 'f1', 'base_ir', 'f0_ir', 'f1_ir'):
            src = '%s/%s/%s/out.spv' % (args.out, name, rid)
            dst = '%s/%s_%s.spv' % (keep, rid, name)
            shutil.copyfile(src, dst)
            lines380.append('%s  %s  %d' % (sha256_file(dst), os.path.basename(dst), os.path.getsize(dst)))
    with open(keep + '/SHA256_380b.txt', 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(lines380) + '\n')
    print('G5 380bb9d636390bae rows', sum(1 for rid in rids if by_rid[rid]['hash16'] == P380))
    for line in lines380:
        print('   ', line)
    ok &= any(by_rid[rid]['hash16'] == P380 for rid in rids)
    print('base exe', args.base_exe, sha256_file(args.base_exe))
    print('fix exe ', args.fix_exe, sha256_file(args.fix_exe))
    print('corpus_f12d.tsv rows', len(table), 'sha256', sha256_file(tsv))
    print('wall %.1f s' % (time.time() - t_start))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
