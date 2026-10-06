"""S17a (HPP-611, ROADMAP s122 item 524(z) K2(1)): the SPIR-V of the T1 corpus (C:/kyty/s288/s7, the form of
corpus_f14e.py / corpus_f12d.py) by the tests binary of the parent commit of S17a (clean worktree) and by the tests
binary of S17a, byte for byte on every OK row (only SPIR-V, RC10(a) of the S16b review).

Rows: the A rows of t1_base.tsv with outcome OK. Each row is translated by KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;
<perm>" in a separate process of shader_cfg_tests, all other KYTY_* variables removed, in the configurations
  base     parent exe, nothing set
  s17a     S17a exe, nothing set (KYTY_S_REPLAY unset = 0)
  s17a0    S17a exe, KYTY_S_REPLAY=0
Readings (all must hold, ALL OK): G0 every process rc 0 and out.spv written; R1 s17a == base and s17a0 == base byte for
byte on every row; no "ShaderReplay:" text in any stderr or stdout.
Rule 27: before every process the lock C:/kyty/SEALED_RUN.lock and C:/kyty/s288/STOP are checked.
Usage: python corpus_s17a.py <parent exe> <S17a exe> <out dir> [--workers N] [--budget S]
"""
import argparse
import collections
import concurrent.futures as cf
import csv
import hashlib
import os
import struct
import subprocess
import sys
import threading
import time

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
TIMEOUT = 180

CONFIGS = [
    ('base', 'base', None),
    ('s17a', 'fix', None),
    ('s17a0', 'fix', '0'),
]

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
    ap.add_argument('s17a_exe')
    ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--budget', type=float, default=480.0)
    args = ap.parse_args()
    t_start = time.time()
    check_halt()
    exes = {'base': args.base_exe, 'fix': args.s17a_exe}

    rows_all = list(csv.DictReader(open(T1, encoding='ascii'), delimiter='\t'))
    rows = [r for r in rows_all if r['row'] == 'A' and r['outcome'] == 'OK']
    print('t1 rows', len(rows_all), 'A rows OK', len(rows), 'stages', dict(collections.Counter(r['stage'] for r in rows)))

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

    jobs = []
    for r in rows:
        rid = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
        g, c = gcn_path(r), cache_path(r)
        for cfg in CONFIGS:
            jobs.append((rid, r, g, c, cfg))
    os.makedirs(args.out, exist_ok=True)

    def done(job):
        work = '%s/%s/%s' % (args.out, job[4][0], job[0])
        return all(os.path.exists(work + '/' + n) for n in ('rc.txt', 'stderr.txt'))

    todo = [j for j in jobs if not done(j)]
    print('jobs', len(jobs), 'done before', len(jobs) - len(todo), 'to run', len(todo))
    lock = threading.Lock()
    started = [0]

    def run(job):
        rid, r, g, c, (name, exe_key, replay) = job
        if time.time() - t_start > args.budget:
            return 'budget'
        check_halt()
        work = '%s/%s/%s' % (args.out, name, rid)
        os.makedirs(work, exist_ok=True)
        spv = work + '/out.spv'
        for n in ('out.spv', 'rc.txt', 'stderr.txt', 'stdout.txt'):
            if os.path.exists(work + '/' + n):
                os.remove(work + '/' + n)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (g, c, spv, r['perm'])
        if replay is not None:
            env['KYTY_S_REPLAY'] = replay
        try:
            p = subprocess.run([exes[exe_key]], cwd=work, env=env, capture_output=True, timeout=TIMEOUT)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, out, err = 'timeout', e.stdout or b'', e.stderr or b''
        with open(work + '/stdout.txt', 'wb') as f:
            f.write(out)
        with open(work + '/stderr.txt', 'wb') as f:
            f.write(err)
        with open(work + '/rc.txt', 'w', encoding='ascii') as f:
            f.write(str(rc) + '\n')
        with lock:
            started[0] += 1
        return 'ran'

    halted = None
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(run, j) for j in todo]
        for fu in cf.as_completed(futs):
            try:
                fu.result()
            except Halt as h:
                halted = str(h)
                for g2 in futs:
                    g2.cancel()
    remaining = [j for j in jobs if not done(j)]
    print('ran this call', started[0], 'remaining', len(remaining), 'wall %.1f s' % (time.time() - t_start))
    if halted:
        print('HALT', halted)
        sys.exit(5 if halted == 'LOCK' else 4)
    if remaining:
        print('INCOMPLETE - call again')
        sys.exit(2)

    ok = True
    res = {}
    for rid, r, g, c, cfg in jobs:
        work = '%s/%s/%s' % (args.out, cfg[0], rid)
        rc = open(work + '/rc.txt', encoding='ascii').read().strip()
        spv = work + '/out.spv'
        err = open(work + '/stderr.txt', 'rb').read().decode('utf-8', 'replace')
        out_text = open(work + '/stdout.txt', 'rb').read().decode('utf-8', 'replace')
        res[(rid, cfg[0])] = {'rc': rc, 'sha': sha256_file(spv) if rc == '0' and os.path.exists(spv) else None,
                              'replay': 'ShaderReplay:' in err or 'ShaderReplay:' in out_text, 'spv': spv}
    bad = [(k, v['rc']) for k, v in res.items() if v['rc'] != '0' or v['sha'] is None]
    print('G0 processes', len(res), 'failed', len(bad), bad[:5])
    ok &= not bad
    rids = sorted({j[0] for j in jobs})
    r1 = [(rid, n) for rid in rids for n in ('s17a', 's17a0') if res[(rid, n)]['sha'] != res[(rid, 'base')]['sha']]
    print('R1 rows', len(rids), 's17a/s17a0 differing from base:', len(r1), r1[:5])
    ok &= not r1
    noisy = [k for k, v in res.items() if v['replay']]
    print('ShaderReplay text in output:', len(noisy), noisy[:5])
    ok &= not noisy
    nl = chr(10)
    with open(args.out + '/corpus_s17a.tsv', 'w', encoding='ascii', newline=nl) as f:
        f.write(chr(9).join(['rid', 'base_sha', 's17a_sha', 's17a0_sha']) + nl)
        for rid in rids:
            f.write(chr(9).join([rid, str(res[(rid, 'base')]['sha']), str(res[(rid, 's17a')]['sha']),
                                 str(res[(rid, 's17a0')]['sha'])]) + nl)
    print('base exe', args.base_exe, sha256_file(args.base_exe))
    print('s17a exe', args.s17a_exe, sha256_file(args.s17a_exe))
    print('corpus_s17a.tsv rows', len(rids), 'sha256', sha256_file(args.out + '/corpus_s17a.tsv'))
    print('wall %.1f s' % (time.time() - t_start))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
