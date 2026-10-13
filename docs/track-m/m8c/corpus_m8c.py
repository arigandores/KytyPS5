"""Track M, M8c (HPP-860, ROADMAP s122 items 778(d)(2), 775(g)(2), 786(g)(3)): gate G2 on the MS2 tree - port of
m657/m7a/corpus_m7a.py (same rows: C:/kyty/s288/s7 t1_base.tsv, A rows, outcome not HARNESS_UNSUPPORTED, perm != '-';
same GCN and cache files checked by sha256). Each row in its own process by KYTY_RECOMPILE="<gcn>;<cache>;<out.spv>;<perm>",
every other KYTY_* removed, at IDLE priority, MS2 shader_cfg_tests:
  z     the six translator KYTY_M_* = 0 (T234 T233 T256 T306 T032 T203), nothing else
  d     every KYTY_* unset (the MS2 defaults: mask 0x3b) + KYTY_RECOMPILE_T306=1 (probe lines only; M7b member 773(g)(4):
        the probe does not change out.spv)
References: FS15 = m657/m2d/corpus/base (FS15 exe, M2d), MS1 defaults = m657/m2d/corpus/d, M7a tree at KYTY_M_T306=1 =
m657/m7a/corpus/m1.
Member 775(g)(2) (row outside T1): CS 7b4078750f32db50, GCN words m657/m7a/cs7b/7b4078750f32db50.bin, game cache record
cs_7b4078750f32db50_28f7a21f24d8d3cc.bin (sha256 2b20e2c7...), perm 0, with KYTY_RECOMPILE_T306=1, arms
  cs_d  defaults (unset), cs_1  KYTY_M_T306=1, cs_0  KYTY_M_T306=0.
Modes:
  run <ms2 exe> <out> [--workers N]
  check <out>
Members of check (prints ALL OK / FAIL, writes corpus_m8c.tsv):
  (1) every process rc 0 with out.spv (z, d: 269 rows each; cs_d, cs_1, cs_0);
  (2) z == FS15 byte for byte on 269 of 269 rows;
  (3) the rows where d != MS1 defaults are exactly ps_5a34b303576ee324_914a71d3664b53ab_0 and
      ps_f47c0c097c598a36_3de3d43ef41686a6_0;
  (4) oracle on those two rows in d (lines recompile-t306 from the SPIR-V words): every pc of the M5b RC3(a) list gives
      exactly one line path=const, components 2, its (x, y); fallback nonconstant = cube = range = 0; on every other row
      0 records and fallback (0, 0, 0, 0);
  (5) d == M7a tree at KYTY_M_T306=1 (m7a/corpus/m1) on 269 of 269 rows (MS2 translator = M7a repair + defaults; the
      other MS2 commits - T125, KYTY_DIAG_M5W2, stand - are outside the translator);
  (6) 775(g)(2): cs_d and cs_1 - 6 records recompile-t306 of hash 7b4078750f32db50, pairs (1,1), (1,0), (0,1) two each,
      every path=const components 2, fallback (0, 0, 0, 6); cs_0 - 0 records, fallback (0, 0, 0, 0); cs_d out.spv ==
      cs_1 out.spv; cs_1 out.spv == M7a cs7b/out_1.spv and cs_0 out.spv == M7a cs7b/out_0.spv (sha256)."""
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys
import threading

S7 = 'C:/kyty/s288/s7'
GCN_ROOT = 'C:/kyty/s288/s4/gcn'
CACHE_CUR = S7 + '/cache_cur'
T1 = S7 + '/t1_base.tsv'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
FS15 = 'C:/kyty/m657/m2d/corpus/base'
MS1D = 'C:/kyty/m657/m2d/corpus/d'
M7A1 = 'C:/kyty/m657/m7a/corpus/m1'
CS7B = 'C:/kyty/m657/m7a/cs7b'
CS_GCN = CS7B + '/7b4078750f32db50.bin'
CS_CACHE = CS7B + '/cs_7b4078750f32db50_28f7a21f24d8d3cc.bin'
CS_CACHE_SHA = '2b20e2c757f59c8f711f2e0f9f0283ad730bfa45ab999da5c882f3c85a7fbb30'
CONFIGS = ['z', 'd']
CS_ARMS = ['cs_d', 'cs_1', 'cs_0']
IDLE = 0x40
KNOBS = ['KYTY_M_T234', 'KYTY_M_T233', 'KYTY_M_T256', 'KYTY_M_T306', 'KYTY_M_T032', 'KYTY_M_T203']
PS_ROWS = ['ps_5a34b303576ee324_914a71d3664b53ab_0', 'ps_f47c0c097c598a36_3de3d43ef41686a6_0']
# M5b review RC3(a): pc in dwords -> (x, y)
ORACLE = {
    '5a34b303576ee324': {62: (0, 1), 64: (1, -1), 67: (0, -1), 70: (-1, 0), 73: (1, 0), 78: (-1, -1), 81: (-1, 1),
                         84: (1, 1)},
    'f47c0c097c598a36': {99: (1, 0), 215: (0, 1)},
}
CS_WANT = sorted([(1, 1), (1, 1), (1, 0), (1, 0), (0, 1), (0, 1)])


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
        for k in KNOBS:
            env[k] = '0'
    else:
        env['KYTY_RECOMPILE_T306'] = '1'
    if name == 'cs_1':
        env['KYTY_M_T306'] = '1'
    if name == 'cs_0':
        env['KYTY_M_T306'] = '0'
    return env


def cmd_run(argv):
    exe, out = argv[0], argv[1]
    workers = 2
    for i, a in enumerate(argv):
        if a == '--workers':
            workers = int(argv[i + 1])
    check_halt()
    print('ms2 exe', exe, sha256_file(exe))
    if sha256_file(CS_CACHE) != CS_CACHE_SHA:
        raise SystemExit('cs cache sha mismatch')
    rows = load_rows()
    jobs = [(r, c) for r in rows for c in CONFIGS] + [(None, c) for c in CS_ARMS]
    print('rows', len(rows), 'configs', CONFIGS, 'cs arms', CS_ARMS, 'processes', len(jobs), 'workers', workers)
    lock = threading.Lock()
    done = [0, 0]

    def run(job):
        r, name = job
        work = '%s/%s/%s' % (out, name, r['rid'] if r else '7b4078750f32db50')
        spv = work + '/out.spv'
        if os.path.exists(spv) and os.path.exists(work + '/rc.txt'):
            with lock:
                done[1] += 1
            return
        check_halt()
        os.makedirs(work, exist_ok=True)
        env = config_env(name)
        if r:
            env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (gcn_path(r), cache_path(r), spv, r['perm'])
        else:
            env['KYTY_RECOMPILE'] = '%s;%s;%s;%s' % (CS_GCN, CS_CACHE, spv, '0')
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


LINE = re.compile(r'recompile-t306: hash=([0-9a-f]{16}) pc=0x([0-9a-f]+) x=(-?\d+) y=(-?\d+) z=(-?\d+) '
                  r'components=(\d+) path=(\w+)')
FALL = re.compile(r'recompile-t306-fallback: nonconstant=(\d+) cube=(\d+) range=(\d+) records=(\d+)')


def probe(path):
    text = open(path, 'rb').read().decode('utf-8', 'replace')
    recs = [(m.group(1), int(m.group(2), 16), int(m.group(3)), int(m.group(4)), int(m.group(6)), m.group(7))
            for m in LINE.finditer(text)]
    falls = [tuple(int(x) for x in m.groups()) for m in FALL.finditer(text)]
    return recs, falls


def cmd_check(argv):
    out = argv[0]
    rows = load_rows()
    n = len(rows)
    ok = True
    shas = {}
    bad = []
    refs = {'fs15': FS15, 'ms1d': MS1D, 'm7a1': M7A1}
    for r in rows:
        for c in CONFIGS + list(refs):
            base = refs.get(c, out + '/' + c)
            w = '%s/%s' % (base, r['rid'])
            rc = open(w + '/rc.txt').read().strip() if os.path.exists(w + '/rc.txt') else 'missing'
            spv = w + '/out.spv'
            shas[c, r['rid']] = sha256_file(spv) if os.path.exists(spv) else None
            if rc != '0' or shas[c, r['rid']] is None:
                bad.append((c, r['rid'], rc))
    cs = {}
    for a in CS_ARMS:
        w = '%s/%s/7b4078750f32db50' % (out, a)
        rc = open(w + '/rc.txt').read().strip() if os.path.exists(w + '/rc.txt') else 'missing'
        spv = w + '/out.spv'
        cs[a] = (rc, sha256_file(spv) if os.path.exists(spv) else None, w + '/log.txt')
        if rc != '0' or cs[a][1] is None:
            bad.append((a, '7b4078750f32db50', rc))
    print('(1) rows %d processes %d failed %d %s' % (n, n * len(CONFIGS) + len(CS_ARMS), len(bad), bad[:5]))
    ok &= not bad and n == 269
    eq = sum(1 for r in rows if shas['z', r['rid']] == shas['fs15', r['rid']])
    print('(2) z (six translator KYTY_M_*=0) == FS15: %d of %d' % (eq, n))
    ok &= eq == n
    diff = sorted(r['rid'] for r in rows if shas['d', r['rid']] != shas['ms1d', r['rid']])
    print('(3) rows MS2 defaults != MS1 defaults: %d %s' % (len(diff), diff))
    ok &= diff == sorted(PS_ROWS)
    lines = []
    for r in rows:
        recs, falls = probe('%s/d/%s/log.txt' % (out, r['rid']))
        if r['rid'] not in PS_ROWS:
            if recs or len(falls) != 1 or falls[0] != (0, 0, 0, 0):
                lines.append('d %s unexpected records %d fallback %s' % (r['rid'], len(recs), falls))
                ok = False
            continue
        want = ORACLE[r['hash16']]
        lines.append('d %s fallback %s records %d' % (r['rid'], falls, len(recs)))
        ok &= len(falls) == 1 and falls[0][:3] == (0, 0, 0) and falls[0][3] == len(want)
        ok &= len(recs) == len(want)
        for pc_dw, (x, y) in sorted(want.items()):
            hit = [q for q in recs if q[1] == pc_dw * 4]
            good = len(hit) == 1 and hit[0][0] == r['hash16'] and hit[0][5] == 'const' and hit[0][4] == 2 and \
                (hit[0][2], hit[0][3]) == (x, y)
            lines.append('  pc %3d want (%2d,%2d) got %s %s' % (pc_dw, x, y,
                         [(q[2], q[3], q[4], q[5]) for q in hit], 'match' if good else 'NO-MATCH'))
            ok &= good
    print('(4) oracle on the two PS rows (d) and probe silence elsewhere:')
    print('\n'.join(lines))
    eq = sum(1 for r in rows if shas['d', r['rid']] == shas['m7a1', r['rid']])
    print('(5) d == M7a tree at KYTY_M_T306=1: %d of %d' % (eq, n))
    ok &= eq == n
    print('(6) 775(g)(2) CS 7b4078750f32db50 with the game cache record, perm 0:')
    for a in CS_ARMS:
        recs, falls = probe(cs[a][2])
        pairs = sorted((q[2], q[3]) for q in recs)
        if a == 'cs_0':
            good = not recs and falls == [(0, 0, 0, 0)]
        else:
            good = (len(recs) == 6 and pairs == CS_WANT and all(q[0] == '7b4078750f32db50' and q[5] == 'const' and
                    q[4] == 2 for q in recs) and falls == [(0, 0, 0, 6)])
        print('  %s rc %s records %d pairs %s fallback %s spv %s %s' % (a, cs[a][0], len(recs), pairs, falls,
              (cs[a][1] or '-')[:16], 'OK' if good else 'FAIL'))
        ok &= good
    m7a_1, m7a_0 = sha256_file(CS7B + '/out_1.spv'), sha256_file(CS7B + '/out_0.spv')
    g = cs['cs_d'][1] == cs['cs_1'][1] and cs['cs_1'][1] == m7a_1 and cs['cs_0'][1] == m7a_0
    print('  cs_d == cs_1: %s; cs_1 == M7a out_1 (%s): %s; cs_0 == M7a out_0 (%s): %s -> %s' % (
        cs['cs_d'][1] == cs['cs_1'][1], m7a_1[:16], cs['cs_1'][1] == m7a_1, m7a_0[:16], cs['cs_0'][1] == m7a_0,
        'OK' if g else 'FAIL'))
    ok &= g
    with open(out + '/corpus_m8c.tsv', 'w', newline='\n') as f:
        cols = ['fs15', 'ms1d', 'm7a1'] + CONFIGS
        f.write('row\t' + '\t'.join('sha_' + c for c in cols) + '\n')
        for r in rows:
            f.write(r['rid'] + '\t' + '\t'.join(shas[c, r['rid']] or '-' for c in cols) + '\n')
        for a in CS_ARMS:
            f.write('cs_7b4078750f32db50_' + a + '\t' + (cs[a][1] or '-') + '\n')
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        sys.exit(cmd_run(sys.argv[2:]))
    sys.exit(cmd_check(sys.argv[2:]))
