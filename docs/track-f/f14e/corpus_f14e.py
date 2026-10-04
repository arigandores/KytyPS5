"""F14e (HPP-505, ROADMAP s122 items 409(g)(2), 415(v)): offline translation of the T1 corpus (C:/kyty/s288/s7, form of
F12d corpus_f12d.py) by the build without the fix (base = parent of the code commit + test part A) and by the build with
it, in the readings (1)-(4) of item 415(v).

Rows: the A rows of t1_base.tsv with outcome OK (the 269 rows of F14a f14a_spv.tsv). Each row is translated by
KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;<perm>" in a separate process of shader_cfg_tests, all other KYTY_*
variables removed, in the configurations
  base     base exe, nothing set
  f0       fix exe, KYTY_FIX_F19=0
  fu       fix exe, KYTY_FIX_F19 unset
  f0m      fix exe, KYTY_FIX_F19=0,   KYTY_RECOMPILE_F19_FORMAT=k16UNorm
  fum      fix exe, KYTY_FIX_F19 unset, KYTY_RECOMPILE_F19_FORMAT=k16UNorm
  f1       fix exe, KYTY_FIX_F19=1
  f1m16    fix exe, KYTY_FIX_F19=1,   KYTY_RECOMPILE_F19_FORMAT=k16UNorm
  f1m8     fix exe, KYTY_FIX_F19=1,   KYTY_RECOMPILE_F19_FORMAT=k8UNorm
Readings (all must hold, ALL OK):
  G0  every process rc 0 and out.spv written;
  R1  f0, fu, f0m, fum == base byte for byte on every row; no "[f19] stand" line in their stderr;
  R2  f1 == base on every row;
  R3  f1m16 != base exactly on the rows whose stand line says manual_to_native > 0 (a manual place stored in the
      specialization); in each such row ManualDepthCompare sites 0 and OpImageSampleDref* >= 1; every other row == base;
      the count N of such rows is compared with the 48 manual rows of F14a (f14a_spv.tsv manual > 0), every row of the
      symmetric difference printed with its counts;
  R4  f1m8 == base on every row.
Resumable: a job whose out.spv, rc.txt and stderr.txt exist is not run again. --budget <s>: no new process is started
after that many seconds (the readings are printed only when every job is done). Rule 27: before every process the lock
C:/kyty/SEALED_RUN.lock and C:/kyty/f287/STOP are checked; found -> stop, exit 5 / 4 (finished jobs are kept).
Usage: python corpus_f14e.py <base exe> <fix exe> <out dir> [--workers N] [--budget S]
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
F14A = 'C:/kyty/KytyPS5/docs/track-f/f14a/f14a_spv.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
TIMEOUT = 180

CONFIGS = [
    ('base', 'base', None, None),
    ('f0', 'fix', '0', None),
    ('fu', 'fix', None, None),
    ('f0m', 'fix', '0', 'k16UNorm'),
    ('fum', 'fix', None, 'k16UNorm'),
    ('f1', 'fix', '1', None),
    ('f1m16', 'fix', '1', 'k16UNorm'),
    ('f1m8', 'fix', '1', 'k8UNorm'),
]

OP_SAMPLE = {87, 88, 96}
OP_DREF = {89, 90, 97}
OP_FCMP = set(range(180, 192))


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


def spv_sites(path):
    """(Dref count, ManualDepthCompare count) - the parser of F14a f14a_corpus.py analyse()."""
    data = open(path, 'rb').read()
    words = struct.unpack('<%dI' % (len(data) // 4), data)
    assert words[0] == 0x07230203
    insts = []
    i = 5
    while i < len(words):
        wc, op = words[i] >> 16, words[i] & 0xffff
        insts.append((op, words[i + 1:i + wc]))
        i += wc
    float_types = {w[0] for op, w in insts if op == 22 and len(w) >= 2 and w[1] == 32}
    const = {w[1]: w[2] for op, w in insts if op == 43 and w[0] in float_types}
    dref = 0
    sample_res, extract, fcmp, sel = set(), {}, {}, []
    for op, w in insts:
        if op in OP_DREF:
            dref += 1
        elif op in OP_SAMPLE:
            sample_res.add(w[1])
        elif op == 81 and len(w) >= 3:
            extract[w[1]] = w[2]
        elif op in OP_FCMP and len(w) >= 4:
            fcmp[w[1]] = (w[2], w[3], op)
        elif op == 169 and len(w) >= 5:
            sel.append(w)
    manual = 0
    for w in sel:
        if w[0] not in float_types or w[2] not in fcmp:
            continue
        if const.get(w[3]) != 0x3f800000 or const.get(w[4]) != 0:
            continue
        x = fcmp[w[2]][1]
        if x in extract and extract[x] in sample_res:
            manual += 1
    return dref, manual


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('base_exe')
    ap.add_argument('fix_exe')
    ap.add_argument('out')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--budget', type=float, default=480.0)
    args = ap.parse_args()
    t_start = time.time()
    check_halt()
    exes = {'base': args.base_exe, 'fix': args.fix_exe}

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
        rid, r, g, c, (name, exe_key, f19, fmt) = job
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
        if f19 is not None:
            env['KYTY_FIX_F19'] = f19
        if fmt is not None:
            env['KYTY_RECOMPILE_F19_FORMAT'] = fmt
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
        stand = [line for line in err.splitlines() if line.startswith('[f19] stand')]
        res[(rid, cfg[0])] = {'rc': rc, 'sha': sha256_file(spv) if rc == '0' and os.path.exists(spv) else None,
                              'stand': stand, 'spv': spv}
    bad = [(k, v['rc']) for k, v in res.items() if v['rc'] != '0' or v['sha'] is None]
    print('G0 processes', len(res), 'failed', len(bad), bad[:5])
    ok &= not bad
    rids = sorted({j[0] for j in jobs})
    by_rid = {j[0]: j[1] for j in jobs}
    r1 = [(rid, n) for rid in rids for n in ('f0', 'fu', 'f0m', 'fum')
          if res[(rid, n)]['sha'] != res[(rid, 'base')]['sha'] or res[(rid, n)]['stand']]
    print('R1 rows', len(rids), 'f0/fu/f0m/fum differing from base or with a stand line:', len(r1), r1[:5])
    ok &= not r1
    r2 = [rid for rid in rids if res[(rid, 'f1')]['sha'] != res[(rid, 'base')]['sha']]
    print('R2 f1 != base:', len(r2), r2[:5])
    ok &= not r2
    table = []
    stored, differ, r3_bad = set(), set(), []
    for rid in rids:
        stand = res[(rid, 'f1m16')]['stand']
        to_native = 0
        if stand:
            to_native = int(stand[0].split('manual_to_native=')[1].split()[0])
        b_dref, b_manual = spv_sites(res[(rid, 'base')]['spv'])
        m_dref, m_manual = spv_sites(res[(rid, 'f1m16')]['spv'])
        d = res[(rid, 'f1m16')]['sha'] != res[(rid, 'base')]['sha']
        if to_native > 0:
            stored.add(rid)
        if d:
            differ.add(rid)
            if m_manual != 0 or m_dref < 1:
                r3_bad.append(rid)
        table.append([rid, by_rid[rid]['hash16'], str(to_native), str(b_dref), str(b_manual), str(m_dref),
                      str(m_manual), str(int(d)), str(int(res[(rid, 'f1m8')]['sha'] != res[(rid, 'base')]['sha']))])
    with open(args.out + '/corpus_f14e.tsv', 'w', encoding='ascii', newline='\n') as f:
        f.write('\t'.join(['row', 'hash16', 'stand_manual_to_native', 'base_dref', 'base_manual', 'f1m16_dref',
                           'f1m16_manual', 'f1m16_ne_base', 'f1m8_ne_base']) + '\n')
        for t in table:
            f.write('\t'.join(t) + '\n')
    print('R3 rows with a stored manual place (stand manual_to_native > 0):', len(stored),
          '; rows f1m16 != base:', len(differ), '; differ - stored', sorted(differ - stored)[:5],
          '; stored - differ', sorted(stored - differ)[:5], '; differing rows with manual sites or no Dref', r3_bad[:5])
    ok &= differ == stored and not r3_bad
    f14a = {}
    for r in csv.DictReader(open(F14A, encoding='ascii'), delimiter='\t'):
        f14a['%s_%s' % (r['stage'], r['id'])] = int(r['manual'])
    f14a_manual = {rid for rid, m in f14a.items() if m > 0}
    print('R3 N =', len(differ), 'of the', len(f14a_manual), 'manual rows of F14a; F14a rows matched', len(set(f14a) & set(rids)))
    for rid in sorted(differ ^ f14a_manual):
        row = [t for t in table if t[0] == rid]
        print('   N!=48 row', rid, 'in differ' if rid in differ else 'not in differ', 'f14a manual', f14a.get(rid),
              'row', row[0][2:] if row else None)
    r4 = [rid for rid in rids if res[(rid, 'f1m8')]['sha'] != res[(rid, 'base')]['sha']]
    print('R4 f1m8 != base:', len(r4), r4[:5])
    ok &= not r4
    print('base exe', args.base_exe, sha256_file(args.base_exe))
    print('fix exe ', args.fix_exe, sha256_file(args.fix_exe))
    print('corpus_f14e.tsv rows', len(table), 'sha256', sha256_file(args.out + '/corpus_f14e.tsv'))
    print('wall %.1f s' % (time.time() - t_start))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
