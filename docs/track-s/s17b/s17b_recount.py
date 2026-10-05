"""S17b (HPP-612, Red Team): own recount of K2(1) of ROADMAP s122 item 524(z) - SPIR-V of the T1 corpus by the tests
binary of the parent 2990fe06 against the tests binary of S17a 283a6ef9 (unset and KYTY_S_REPLAY=0), byte for byte on
every A row with outcome OK. Written independently of docs/track-s/s17a/corpus_s17a.py (same inputs: t1_base.tsv of
C:/kyty/s288/s7, GCN of s4, cache files of s7/cache_cur). Extra arms: S17a with KYTY_S_REPLAY=1 (the knob on - the
recompile path must not reach the replay code) and a power control: the parent with KYTY_FIX_F19=0 (a translator rule
change; the count of differing rows is printed, it is the proof that the comparator sees a translator difference).
Usage: python s17b_recount.py <parent exe> <S17a exe> <out dir>
"""
import concurrent.futures as cf
import csv
import hashlib
import os
import subprocess
import sys
import time

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
EXPECT = {'parent': '32c50dc48f8de10fe8a97f0781e77ad1042c701a71c161ae9c11b3a0e81b46b7',
          's17a': '56405997c1c0601633a280ead0a0408f2ef26296f8a9cf3e4bcf8e95e96810ee'}


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parent, s17a, out = sys.argv[1], sys.argv[2], sys.argv[3]
    t0 = time.time()
    exes = {'parent': parent, 's17a': s17a}
    for k, p in exes.items():
        s = sha(p)
        print('exe', k, p, s, 'expected' if s == EXPECT[k] else 'UNEXPECTED')
        if s != EXPECT[k]:
            sys.exit(3)
    rows = [r for r in csv.DictReader(open(S7 + '/t1_base.tsv', encoding='ascii'), delimiter='\t')
            if r['row'] == 'A' and r['outcome'] == 'OK']
    print('rows', len(rows))
    arms = [('P', 'parent', {}), ('S', 's17a', {}), ('S0', 's17a', {'KYTY_S_REPLAY': '0'}),
            ('S1', 's17a', {'KYTY_S_REPLAY': '1'}), ('PF0', 'parent', {'KYTY_FIX_F19': '0'})]
    jobs = []
    for r in rows:
        gcn = None
        for arm in r['gcn_arms'].split(','):
            p = '%s/%s/%s_%s.bin' % (GCN_ROOT, arm, r['stage'], r['hash16'])
            if os.path.exists(p) and os.path.getsize(p) > 0 and sha(p) == r['gcn_sha256']:
                gcn = p
                break
        cache = '%s/cache_cur/%s_%s_%s.bin' % (S7, r['stage'], r['hash16'], r['key16'])
        if gcn is None or sha(cache) != r['cache_sha256']:
            print('input missing or sha mismatch', r['hash16'])
            sys.exit(3)
        rid = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
        for name, exe, extra in arms:
            jobs.append((rid, name, exe, extra, gcn, cache, r['perm']))

    def run(job):
        rid, name, exe, extra, gcn, cache, perm = job
        if os.path.exists(LOCK) or os.path.exists(STOP):
            return (rid, name, 'halt', None, False)
        work = '%s/%s/%s' % (out, name, rid)
        os.makedirs(work, exist_ok=True)
        spv = work + '/out.spv'
        if os.path.exists(spv):
            os.remove(spv)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (gcn, cache, spv, perm)
        env.update(extra)
        p = subprocess.run([exes[exe]], cwd=work, env=env, capture_output=True, timeout=180)
        text = p.stdout + p.stderr
        return (rid, name, p.returncode, sha(spv) if os.path.exists(spv) else None, b'ShaderReplay' in text)

    res = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for rid, name, rc, s, noisy in ex.map(run, jobs):
            res[(rid, name)] = (rc, s, noisy)
    halted = [k for k, v in res.items() if v[0] == 'halt']
    if halted:
        print('HALT', len(halted))
        sys.exit(5)
    rids = sorted({j[0] for j in jobs})
    ok = True
    failed = [(k, v[0]) for k, v in res.items() if v[0] != 0 or v[1] is None]
    print('processes', len(res), 'rc!=0 or no spv', len(failed), failed[:5])
    ok &= not failed
    for name in ('S', 'S0', 'S1'):
        diff = [rid for rid in rids if res[(rid, name)][1] != res[(rid, 'P')][1]]
        print('arm', name, 'rows differing from parent', len(diff), diff[:5])
        ok &= not diff
    noisy = [k for k, v in res.items() if v[2]]
    print('ShaderReplay text in output', len(noisy), noisy[:5])
    ok &= not noisy
    pf = [rid for rid in rids if res[(rid, 'PF0')][1] != res[(rid, 'P')][1]]
    print('power control: parent KYTY_FIX_F19=0 rows differing from parent', len(pf), pf[:5])
    with open(out + '/recount.tsv', 'w', encoding='ascii', newline=chr(10)) as f:
        f.write(chr(9).join(['rid', 'P', 'S', 'S0', 'S1', 'PF0']) + chr(10))
        for rid in rids:
            f.write(chr(9).join([rid] + [str(res[(rid, n)][1]) for n in ('P', 'S', 'S0', 'S1', 'PF0')]) + chr(10))
    print('recount.tsv sha256', sha(out + '/recount.tsv'))
    print('wall %.1f s' % (time.time() - t0))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
