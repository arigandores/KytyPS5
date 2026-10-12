"""M2d (HPP-841, ROADMAP s122 items 756(g)(2), 762(v)): the T1 corpus on the MS1 tree - port of m657/m2a/corpus_m2a.py
(same rows: C:/kyty/s288/s7 t1_base.tsv, A rows, outcome not HARNESS_UNSUPPORTED, perm != '-'; same GCN and cache files
checked by sha256). Settings, each row in its own process by KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;<perm>" with
every other KYTY_* removed:
  base  FS15 shader_cfg_tests (m657/m2a/bin/shader_cfg_tests_fs15.exe), every KYTY_* unset
  z     MS1 shader_cfg_tests, the six KYTY_M_<theme>=0 (every M knob off)
  d     MS1 shader_cfg_tests, every KYTY_* unset (the MS1 defaults: T234, T233, T032, T203 on)
  e     MS1 shader_cfg_tests, explicit KYTY_M_T234=T233=T032=T203=1, T256=T306=0
Rows already done (out.spv + rc.txt) are not run again. Lock and STOP before every process.
Modes:
  run <base exe> <ms1 exe> <out> [--configs c1,c2] [--workers N]
  check <out> <m2a corpus4 dir>
Members of check (prints ALL OK / FAIL, writes corpus_m2d.tsv):
  (1) every process rc 0 with out.spv;
  (2) z == base byte for byte on every row (G2 of item 756(g)(2): MS1 at =0 of every knob = FS15);
  (3) base == the M2a base (corpus4, same FS15 exe) byte for byte on every row (the base is the same one);
  (4) d == e on every row (the defaults are the explicit knobs =1 of the four MS1 themes, T256/T306 off);
  (5) the programs where d != base are a subset of the union of the M2a predicted sets of T234, T233, T032, T203
      (corpus4/predict.tsv, the translator's own decoder) and >= 1;
  (6) the programs where d != base = the union of the programs changed by tT234, tT233, tT032, tT203 in M2a (corpus4).
"""
import collections
import concurrent.futures as cf
import hashlib
import os
import subprocess
import sys
import threading

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']
MS1 = ['T234', 'T233', 'T032', 'T203']
CONFIGS = ['base', 'z', 'd', 'e']
IDLE = 0x40


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


def load_rows():
    with open(T1, encoding='ascii') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        rows_all = [dict(zip(hdr, line.rstrip('\n').split('\t'))) for line in f if line.strip()]
    rows = [r for r in rows_all if r['row'] == 'A' and r['outcome'] != 'HARNESS_UNSUPPORTED' and r['perm'] != '-']
    for r in rows:
        r['rid'] = '%s_%s_%s_%s' % (r['stage'], r['hash16'], r['key16'], r['perm'])
    return rows


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


def config_env(name):
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    if name == 'z':
        for t in THEMES:
            env['KYTY_M_' + t] = '0'
    elif name == 'e':
        for t in THEMES:
            env['KYTY_M_' + t] = '1' if t in MS1 else '0'
    return env


def cmd_run(argv):
    base_exe, ms1_exe, out = argv[0], argv[1], argv[2]
    configs = CONFIGS
    workers = 2
    for i, a in enumerate(argv):
        if a == '--configs':
            configs = argv[i + 1].split(',')
        if a == '--workers':
            workers = int(argv[i + 1])
    check_halt()
    print('base exe', base_exe, sha256_file(base_exe))
    print('ms1 exe', ms1_exe, sha256_file(ms1_exe))
    rows = load_rows()
    jobs = [(r, c) for r in rows for c in configs]
    print('rows', len(rows), 'configs', configs, 'processes', len(jobs), 'workers', workers)
    lock = threading.Lock()
    done = [0, 0]

    def run(job):
        r, name = job
        work = '%s/%s/%s' % (out, name, r['rid'])
        spv = work + '/out.spv'
        if os.path.exists(spv) and os.path.exists(work + '/rc.txt'):
            with lock:
                done[1] += 1
            return
        check_halt()
        os.makedirs(work, exist_ok=True)
        env = config_env(name)
        env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (gcn_path(r), cache_path(r), spv, r['perm'])
        exe = base_exe if name == 'base' else ms1_exe
        try:
            p = subprocess.run([exe], cwd=work, env=env, capture_output=True, timeout=300, creationflags=IDLE)
            rc, o = p.returncode, p.stdout + p.stderr
        except subprocess.TimeoutExpired as e:
            rc, o = 'timeout', (e.stdout or b'') + (e.stderr or b'')
        open(work + '/log.txt', 'wb').write(o)
        open(work + '/rc.txt', 'w').write(str(rc))
        with lock:
            done[0] += 1

    halted = None
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run, j) for j in jobs]
        for fu in cf.as_completed(futs):
            try:
                fu.result()
            except Halt as h:
                halted = str(h)
                for g in futs:
                    g.cancel()
    print('ran', done[0], 'already done', done[1])
    if halted:
        print('HALT', halted)
        return 5 if halted == 'LOCK' else 4
    return 0


def cmd_check(argv):
    out, m2a = argv[0], argv[1]
    rows = load_rows()
    pred = collections.defaultdict(set)
    with open(m2a + '/predict.tsv') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        for line in f:
            c = dict(zip(hdr, line.rstrip('\n').split('\t')))
            for t in THEMES:
                if int(c[t]) > 0:
                    pred[t].add(c['hash16'])
    print('m2a predict.tsv sha256', sha256_file(m2a + '/predict.tsv'))
    m2a_rows = {}
    with open(m2a + '/corpus_m2a.tsv') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        for line in f:
            c = dict(zip(hdr, line.rstrip('\n').split('\t')))
            m2a_rows[c['row']] = c
    print('m2a corpus_m2a.tsv sha256', sha256_file(m2a + '/corpus_m2a.tsv'))
    ok = True

    def res(name, r):
        work = '%s/%s/%s' % (out, name, r['rid'])
        rc = open(work + '/rc.txt').read().strip() if os.path.exists(work + '/rc.txt') else 'missing'
        sha = sha256_file(work + '/out.spv') if rc == '0' and os.path.exists(work + '/out.spv') else None
        return rc, sha

    table = []
    bad_rc = []
    differ = collections.defaultdict(list)
    d_changed = set()
    m2a_changed = set()
    for r in rows:
        shas = {}
        for c in CONFIGS:
            rc, sha = res(c, r)
            if sha is None:
                bad_rc.append((r['rid'], c, rc))
            shas[c] = sha
        if shas['z'] != shas['base']:
            differ['z'].append(r['rid'])
        mr = m2a_rows.get(r['rid'])
        if mr is None or mr['sha_base'] != shas['base']:
            differ['m2a_base'].append(r['rid'])
        if shas['d'] != shas['e']:
            differ['d_e'].append(r['rid'])
        if shas['d'] != shas['base']:
            d_changed.add(r['hash16'])
        if mr is not None:
            for t in MS1:
                if mr['sha_t' + t] != mr['sha_base']:
                    m2a_changed.add(r['hash16'])
        table.append('\t'.join([r['rid'], r['stage'], r['hash16'], r['perm']] + [shas[c] or '-' for c in CONFIGS]))
    with open(out + '/corpus_m2d.tsv', 'w', newline='\n') as f:
        f.write('\t'.join(['row', 'stage', 'hash16', 'perm'] + ['sha_' + c for c in CONFIGS]) + '\n')
        f.write('\n'.join(table) + '\n')
    n = len(rows)
    print('(1) rows %d processes %d failed %d %s' % (n, n * len(CONFIGS), len(bad_rc), bad_rc[:5]))
    ok &= not bad_rc
    print('(2) z == base (FS15) on %d of %d rows, differ %d %s' % (n - len(differ['z']), n, len(differ['z']),
                                                                differ['z'][:3]))
    ok &= not differ['z']
    print('(3) base == M2a base on %d of %d rows, differ %d %s' % (n - len(differ['m2a_base']), n,
                                                                 len(differ['m2a_base']), differ['m2a_base'][:3]))
    ok &= not differ['m2a_base']
    print('(4) d == e on %d of %d rows, differ %d %s' % (n - len(differ['d_e']), n, len(differ['d_e']),
                                                        differ['d_e'][:3]))
    ok &= not differ['d_e']
    union_pred = set()
    for t in MS1:
        union_pred |= pred[t]
    outside = sorted(d_changed - union_pred)
    print('(5) d != base: %d programs; predicted union T234/T233/T032/T203 %d; outside %d %s' % (
        len(d_changed), len(union_pred), len(outside), outside[:5]))
    ok &= not outside and len(d_changed) >= 1
    print('(6) M2a union of tT234/tT233/tT032/tT203 changed %d; d changed %d; equal %s; d-only %s m2a-only %s' % (
        len(m2a_changed), len(d_changed), d_changed == m2a_changed, sorted(d_changed - m2a_changed)[:5],
        sorted(m2a_changed - d_changed)[:5]))
    ok &= d_changed == m2a_changed
    print('corpus_m2d.tsv sha256', sha256_file(out + '/corpus_m2d.tsv'))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    mode = sys.argv[1]
    sys.exit({'run': cmd_run, 'check': cmd_check}[mode](sys.argv[2:]))
