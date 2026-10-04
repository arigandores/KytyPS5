"""F14f (HPP-506, ROADMAP s122 items 409(g)(2), 415(v), 415(g)): Red Team's own offline translation of the T1 corpus (all 269
A rows OK of C:/kyty/s288/s7/t1_base.tsv) by the base exe and the fix exe of F14e, own code and own reader.

Configurations (KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;<perm>", one process per row, all other KYTY_* removed):
  base   base exe
  f0     fix, KYTY_FIX_F19=0           f0m   fix, =0 + KYTY_RECOMPILE_F19_FORMAT=k16UNorm
  fu     fix, unset                    fum   fix, unset + KYTY_RECOMPILE_F19_FORMAT=k16UNorm
  f1     fix, =1                       f1m16 fix, =1 + k16UNorm        f1m8 fix, =1 + k8UNorm
Reader (item 415(v) readings (1)-(4)): sha256 of out.spv against base per row; for the rows where f1m16 differs, own
SPIR-V opcode counts: Dref = OpImageSampleDref*/OpImageSampleProjDref*/OpImageDrefGather (89, 90, 93, 94, 97), plain =
OpImageSampleImplicitLod/ExplicitLod (87, 88); invariant per changed row: Dref(f1m16) - Dref(base) = k and plain(base) -
plain(f1m16) = k with k = the manual count of the row in F14a f14a_spv.tsv (one manual site = one plain sample + shader
compare, natively one Dref sample); the changed set must equal the set of F14a rows with manual > 0.
Usage: python f14f_corpus.py <base exe> <fix exe> <out> [--workers N] [--rows N]
Rule 27: lock and STOP are checked before every process (exit 5 / 4).
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
import time

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
F14A = 'C:/kyty/KytyPS5/docs/track-f/f14a/f14a_spv.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
CONFIGS = {'base': ('base', None, None), 'f0': ('fix', '0', None), 'fu': ('fix', None, None),
           'f0m': ('fix', '0', 'k16UNorm'), 'fum': ('fix', None, 'k16UNorm'), 'f1': ('fix', '1', None),
           'f1m16': ('fix', '1', 'k16UNorm'), 'f1m8': ('fix', '1', 'k8UNorm')}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def counts(path):
    data = open(path, 'rb').read()
    w = struct.unpack('<%dI' % (len(data) // 4), data)
    c = collections.Counter()
    i = 5
    while i < len(w):
        n, op = w[i] >> 16, w[i] & 0xffff
        if n == 0:
            raise ValueError('bad spv ' + path)
        if op in (89, 90, 93, 94, 97):
            c['dref'] += 1
        elif op in (87, 88):
            c['plain'] += 1
        i += n
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base')
    ap.add_argument('fix')
    ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--configs', default=','.join(CONFIGS))
    a = ap.parse_args()
    exes = {'base': a.base, 'fix': a.fix}
    cfgs = a.configs.split(',')
    rows = [r for r in csv.DictReader(open(T1, encoding='ascii'), delimiter='\t') if r['row'] == 'A' and r['outcome'] == 'OK']
    f14a = {}
    for r in csv.DictReader(open(F14A, encoding='ascii'), delimiter='\t'):
        f14a['%s_%s' % (r['stage'], r['id'])] = int(r['manual'] or 0)
    jobs = []
    for r in rows:
        rid = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
        g = None
        for arm in r['gcn_arms'].split(','):
            p = '%s/%s/%s_%s.bin' % (GCN_ROOT, arm, r['stage'], r['hash16'])
            if os.path.exists(p) and os.path.getsize(p) > 0 and sha(p) == r['gcn_sha256']:
                g = p
                break
        c = '%s/%s_%s_%s.bin' % (CACHE_CUR, r['stage'], r['hash16'], r['key16'])
        if g is None or sha(c) != r['cache_sha256']:
            sys.exit('input missing or sha mismatch for ' + rid)
        for n in cfgs:
            jobs.append((rid, r['perm'], g, c, n))
    print('rows', len(rows), 'jobs', len(jobs), 'F14a rows', len(f14a), 'F14a manual>0', sum(1 for v in f14a.values() if v))
    t0 = time.time()

    def run(job):
        rid, perm, g, c, n = job
        if os.path.exists(LOCK) or os.path.exists(STOP):
            return (job, 'halt')
        exe, f19, fmt = CONFIGS[n]
        d = '%s/%s/%s' % (a.out, n, rid)
        os.makedirs(d, exist_ok=True)
        spv = d + '/out.spv'
        if os.path.exists(spv):
            os.remove(spv)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (g, c, spv, perm)
        if f19 is not None:
            env['KYTY_FIX_F19'] = f19
        if fmt is not None:
            env['KYTY_RECOMPILE_F19_FORMAT'] = fmt
        p = subprocess.run([exes[exe]], cwd=d, env=env, capture_output=True, timeout=180)
        open(d + '/stderr.txt', 'wb').write(p.stderr)
        return (job, p.returncode if os.path.exists(spv) else 'nospv')

    bad = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for job, rc in ex.map(run, jobs):
            if rc == 'halt':
                print('HALT lock/STOP')
                sys.exit(5)
            if rc != 0:
                bad.append((job[0], job[4], rc))
    print('processes', len(jobs), 'failed', len(bad), bad[:5], 'wall %.1f s' % (time.time() - t0))
    ok = not bad
    rids = sorted({j[0] for j in jobs})
    h = {(n, rid): sha('%s/%s/%s/out.spv' % (a.out, n, rid)) for n in cfgs for rid in rids}
    diff = {n: sorted(rid for rid in rids if h[(n, rid)] != h[('base', rid)]) for n in cfgs if n != 'base'}
    for n in cfgs:
        if n != 'base':
            print('%-6s rows != base: %d' % (n, len(diff[n])))
    for n in ('f0', 'fu', 'f0m', 'fum', 'f1', 'f1m8'):
        if n in diff:
            ok &= not diff[n]
    if 'f1m16' in diff:
        man = sorted(rid for rid in rids if f14a.get(rid, 0) > 0)
        unk = [rid for rid in rids if rid not in f14a]
        ch = diff['f1m16']
        print('f1m16 changed', len(ch), 'F14a manual rows', len(man), 'changed-manual', sorted(set(ch) - set(man)),
              'manual-changed', sorted(set(man) - set(ch)), 'rows not in F14a', len(unk))
        ok &= set(ch) == set(man) and not unk
        inv_bad = []
        for rid in ch:
            cb = counts('%s/base/%s/out.spv' % (a.out, rid))
            c1 = counts('%s/f1m16/%s/out.spv' % (a.out, rid))
            k = f14a.get(rid, 0)
            if c1['dref'] - cb['dref'] != k or cb['plain'] - c1['plain'] != k:
                inv_bad.append((rid, k, cb['dref'], c1['dref'], cb['plain'], c1['plain']))
        print('invariant Dref +k / plain -k per changed row: violations', len(inv_bad), inv_bad[:5])
        ok &= not inv_bad
        print('sum k over changed rows', sum(f14a.get(r, 0) for r in ch))
    print('base exe', sha(a.base))
    print('fix exe ', sha(a.fix))
    print('ALL OK' if ok else 'NOT OK')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
