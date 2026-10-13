"""Track M, M7b (HPP-853, ROADMAP s122 items 767(l), 773(g)(5)): own run of the T1 corpus on the M7b build of the M7a
worktree commit 91a46dc5 (C:/kyty/m657/m7b/build/shader_cfg_tests.exe) - independent of corpus_m7a.py (own runner and
own comparison; the same row list C:/kyty/s288/s7/t1_base.tsv, rows A, outcome != HARNESS_UNSUPPORTED, perm != '-').
Every KYTY_* of the environment is removed; IDLE priority; one process per row and config:
  z0   KYTY_M_T306 unset, no KYTY_RECOMPILE_T306 (the probe is OFF - the shipping state of =0)
  z1   KYTY_M_T306=1, no probe
  p1   KYTY_M_T306=1, KYTY_RECOMPILE_T306=1 (probe lines; out.spv must equal z1 - the probe does not change the answer)
  p0   KYTY_RECOMPILE_T306=1 at =0 (out.spv must equal z0; 0 records, 0 fallbacks)
Reference: C:/kyty/m657/m2d/corpus/d (MS1 exe, every KYTY_* unset).
Usage: python corpus_m7b.py run <exe> <out>  |  python corpus_m7b.py check <out>   (check prints ALL OK / FAIL)"""
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
S7 = 'C:/kyty/s288/s7'
GCN = 'C:/kyty/s288/s4/gcn'
REF = 'C:/kyty/m657/m2d/corpus/d'
CONFIGS = ['z0', 'z1', 'p1', 'p0']
IDLE = 0x40


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rows():
    lines = open(S7 + '/t1_base.tsv', encoding='ascii').read().split('\n')
    hdr = lines[0].split('\t')
    out = []
    for line in lines[1:]:
        if not line.strip():
            continue
        r = dict(zip(hdr, line.split('\t')))
        if r['row'] == 'A' and r['outcome'] != 'HARNESS_UNSUPPORTED' and r['perm'] != '-':
            r['rid'] = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
            out.append(r)
    return out


def gcn(r):
    for arm in r['gcn_arms'].split(','):
        p = '%s/%s/%s_%s.bin' % (GCN, arm, r['stage'], r['hash16'])
        if os.path.exists(p) and os.path.getsize(p) > 0 and sha(p) == r['gcn_sha256']:
            return p
    raise SystemExit('no GCN ' + r['hash16'])


def cache(r):
    p = '%s/cache_cur/%s_%s_%s.bin' % (S7, r['stage'], r['hash16'], r['key16'])
    if sha(p) != r['cache_sha256']:
        raise SystemExit('cache sha ' + p)
    return p


def run(argv):
    exe, out = argv
    print('exe', exe, sha(exe))
    rs = rows()
    jobs = [(r, c) for r in rs for c in CONFIGS]
    print('rows', len(rs), 'processes', len(jobs))

    def one(job):
        if os.path.exists(LOCK) or os.path.exists(STOP):
            raise SystemExit('LOCK/STOP')
        r, c = job
        w = '%s/%s/%s' % (out, c, r['rid'])
        os.makedirs(w, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        if c in ('z1', 'p1'):
            env['KYTY_M_T306'] = '1'
        if c in ('p0', 'p1'):
            env['KYTY_RECOMPILE_T306'] = '1'
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (gcn(r), cache(r), w + '/out.spv', r['perm'])
        p = subprocess.run([exe], cwd=w, env=env, capture_output=True, timeout=300, creationflags=IDLE)
        open(w + '/log.txt', 'wb').write(p.stdout + p.stderr)
        open(w + '/rc.txt', 'w').write(str(p.returncode))

    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for f in [ex.submit(one, j) for j in jobs]:
            f.result()
    print('done')


REC = re.compile(rb'recompile-t306: hash=(\w+) pc=0x(\w+) x=(-?\d+) y=(-?\d+) z=(-?\d+) components=(\d+) path=(\w+)')
FAL = re.compile(rb'recompile-t306-fallback: nonconstant=(\d+) cube=(\d+) range=(\d+) records=(\d+)')
MTX = re.compile(rb'MTexOffset: [^\n]*')


def check(argv):
    out = argv[0]
    rs = rows()
    ok = True
    h = {}
    bad = []
    for r in rs:
        for c in CONFIGS + ['ref']:
            w = (REF if c == 'ref' else out + '/' + c) + '/' + r['rid']
            rc = open(w + '/rc.txt').read().strip() if os.path.exists(w + '/rc.txt') else 'missing'
            h[c, r['rid']] = sha(w + '/out.spv') if os.path.exists(w + '/out.spv') else None
            if rc != '0' or h[c, r['rid']] is None:
                bad.append((c, r['rid'], rc))
    print('(a) rows %d, processes rc!=0 or no out.spv: %d %s' % (len(rs), len(bad), bad[:4]))
    ok &= len(rs) == 269 and not bad
    n = sum(1 for r in rs if h['z0', r['rid']] == h['ref', r['rid']])
    print('(b) =0 (z0, probe off) == MS1 M2d d byte for byte: %d of %d' % (n, len(rs)))
    ok &= n == len(rs)
    d1 = sorted(r['rid'] for r in rs if h['z1', r['rid']] != h['z0', r['rid']])
    print('(c) rows =1 != =0: %d %s' % (len(d1), d1))
    ok &= d1 == ['ps_5a34b303576ee324_914a71d3664b53ab_0', 'ps_f47c0c097c598a36_3de3d43ef41686a6_0']
    n1 = sum(1 for r in rs if h['p1', r['rid']] == h['z1', r['rid']])
    n0 = sum(1 for r in rs if h['p0', r['rid']] == h['z0', r['rid']])
    print('(d) probe on does not change out.spv: =1 %d of %d, =0 %d of %d' % (n1, len(rs), n0, len(rs)))
    ok &= n1 == len(rs) and n0 == len(rs)
    recs0 = fal0 = 0
    mtx = {}
    for r in rs:
        t0 = open('%s/p0/%s/log.txt' % (out, r['rid']), 'rb').read()
        recs0 += len(REC.findall(t0))
        fal0 += sum(int(x) for m in FAL.findall(t0) for x in m[:3])
        for c in CONFIGS:
            t = open('%s/%s/%s/log.txt' % (out, c, r['rid']), 'rb').read()
            mtx[c] = mtx.get(c, 0) + len(MTX.findall(t))
    print('(e) =0 probe: records %d, fallback lines counted %d; MTexOffset lines per config %s' % (recs0, fal0, mtx))
    ok &= recs0 == 0 and fal0 == 0 and all(v == 0 for v in mtx.values())
    for rid in d1:
        t = open('%s/p1/%s/log.txt' % (out, rid), 'rb').read()
        print('   p1', rid, [(int(m[1], 16) // 4, int(m[2]), int(m[3]), int(m[5]), m[6].decode()) for m in REC.findall(t)],
              [m for m in FAL.findall(t)])
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    if os.path.exists(LOCK):
        print('LOCK present - exit 3')
        sys.exit(3)
    sys.exit(run(sys.argv[2:]) if sys.argv[1] == 'run' else check(sys.argv[2:]))
