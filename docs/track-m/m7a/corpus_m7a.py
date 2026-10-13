"""Track M, M7a (HPP-852, ROADMAP s122 items 767(g), M5a 2.3 member 4): the T1 corpus on the M7a tree - port of
m657/m2d/corpus_m2d.py (same rows: C:/kyty/s288/s7 t1_base.tsv, A rows, outcome not HARNESS_UNSUPPORTED, perm != '-';
same GCN and cache files checked by sha256). Each row in its own process by KYTY_RECOMPILE="<gcn>;<cache>;<out.spv>;<perm>",
every other KYTY_* removed, at IDLE priority:
  m0    M7a shader_cfg_tests, every KYTY_* unset (the MS1 defaults, T306 = 0) + KYTY_RECOMPILE_T306=1 (probe lines only)
  m1    M7a shader_cfg_tests, KYTY_M_T306=1 + KYTY_RECOMPILE_T306=1
  ms1t  MS1 shader_cfg_tests (m657/m2d/tests/shader_cfg_tests_ms1.exe), KYTY_M_T306=1 (the code before the repair, =1)
Reference for =0: m657/m2d/corpus/d (MS1 exe, every KYTY_* unset; M2d member (2)-(4)).
Modes:
  run <m7a exe> <ms1 exe> <out> [--configs c1,c2] [--workers N]
  check <out>
Members of check (prints ALL OK / FAIL, writes corpus_m7a.tsv and oracle_ps.txt):
  (1) every process rc 0 with out.spv (m0, m1, ms1t);
  (2) m0 == M2d d byte for byte on 269 of 269 rows (=0 is MS1);
  (3) the rows where m1 != m0 are exactly ps_5a34b303576ee324_914a71d3664b53ab_0 and ps_f47c0c097c598a36_3de3d43ef41686a6_0;
  (4) oracle on those two rows (m1 log, lines recompile-t306 read from the SPIR-V words): every pc of the M5b RC3(a)
      list gives exactly one line with path=const, components 2 and its (x, y); no other line; recompile-t306-fallback
      nonconstant = cube = range = 0; in m0 0 records and 0 fallbacks on every row;
  (5) justification of the repair scope: m1 == ms1t byte for byte on 269 of 269 rows (the game PS have a non-constant
      lane mask; the repair changes only the constant-mask case)."""
import collections
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
M2D_D = 'C:/kyty/m657/m2d/corpus/d'
CONFIGS = ['m0', 'm1', 'ms1t']
IDLE = 0x40
PS_ROWS = ['ps_5a34b303576ee324_914a71d3664b53ab_0', 'ps_f47c0c097c598a36_3de3d43ef41686a6_0']
# M5b review RC3(a): pc in dwords -> (x, y)
ORACLE = {
    '5a34b303576ee324': {62: (0, 1), 64: (1, -1), 67: (0, -1), 70: (-1, 0), 73: (1, 0), 78: (-1, -1), 81: (-1, 1),
                         84: (1, 1)},
    'f47c0c097c598a36': {99: (1, 0), 215: (0, 1)},
}


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
    if name in ('m0', 'm1'):
        env['KYTY_RECOMPILE_T306'] = '1'
    if name in ('m1', 'ms1t'):
        env['KYTY_M_T306'] = '1'
    return env


def cmd_run(argv):
    m7a_exe, ms1_exe, out = argv[0], argv[1], argv[2]
    configs = CONFIGS
    workers = 2
    for i, a in enumerate(argv):
        if a == '--configs':
            configs = argv[i + 1].split(',')
        if a == '--workers':
            workers = int(argv[i + 1])
    check_halt()
    print('m7a exe', m7a_exe, sha256_file(m7a_exe))
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
        exe = ms1_exe if name == 'ms1t' else m7a_exe
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
    ok = True
    shas = {}
    bad = []
    for r in rows:
        for c in CONFIGS + ['d']:
            base = M2D_D if c == 'd' else out + '/' + c
            w = '%s/%s' % (base, r['rid'])
            rc = open(w + '/rc.txt').read().strip() if os.path.exists(w + '/rc.txt') else 'missing'
            spv = w + '/out.spv'
            shas[c, r['rid']] = sha256_file(spv) if os.path.exists(spv) else None
            if rc != '0' or shas[c, r['rid']] is None:
                bad.append((c, r['rid'], rc))
    n = len(rows)
    print('(1) rows %d processes %d failed %d %s' % (n, n * 4, len(bad), bad[:5]))
    ok &= not bad and n == 269
    eq_d = sum(1 for r in rows if shas['m0', r['rid']] == shas['d', r['rid']])
    print('(2) m0 == M2d d (MS1 defaults): %d of %d' % (eq_d, n))
    ok &= eq_d == n
    diff = sorted(r['rid'] for r in rows if shas['m1', r['rid']] != shas['m0', r['rid']])
    print('(3) rows m1 != m0: %d %s' % (len(diff), diff))
    ok &= diff == sorted(PS_ROWS)
    lines = []
    for r in rows:
        recs, falls = probe('%s/m0/%s/log.txt' % (out, r['rid']))
        if recs or len(falls) != 1 or falls[0] != (0, 0, 0, 0):
            lines.append('m0 %s records %d fallback %s' % (r['rid'], len(recs), falls))
            ok = False
    for r in rows:
        recs, falls = probe('%s/m1/%s/log.txt' % (out, r['rid']))
        if r['rid'] not in PS_ROWS:
            if recs or len(falls) != 1 or falls[0] != (0, 0, 0, 0):
                lines.append('m1 %s unexpected records %d fallback %s' % (r['rid'], len(recs), falls))
                ok = False
            continue
        want = ORACLE[r['hash16']]
        lines.append('m1 %s fallback %s records %d' % (r['rid'], falls, len(recs)))
        ok &= len(falls) == 1 and falls[0][:3] == (0, 0, 0) and falls[0][3] == len(want)
        ok &= len(recs) == len(want)
        for pc_dw, (x, y) in sorted(want.items()):
            hit = [q for q in recs if q[1] == pc_dw * 4]
            good = len(hit) == 1 and hit[0][0] == r['hash16'] and hit[0][5] == 'const' and hit[0][4] == 2 and \
                (hit[0][2], hit[0][3]) == (x, y)
            lines.append('  pc %3d want (%2d,%2d) got %s %s' % (pc_dw, x, y,
                         [(q[2], q[3], q[4], q[5]) for q in hit], 'match' if good else 'NO-MATCH'))
            ok &= good
    print('(4) oracle on the two PS rows and probe silence elsewhere:')
    print('\n'.join(lines))
    eq_t = sum(1 for r in rows if shas['m1', r['rid']] == shas['ms1t', r['rid']])
    print('(5) m1 == ms1t (MS1 code at KYTY_M_T306=1): %d of %d' % (eq_t, n))
    ok &= eq_t == n
    with open(out + '/corpus_m7a.tsv', 'w', newline='\n') as f:
        f.write('row\t' + '\t'.join('sha_' + c for c in ['d'] + CONFIGS) + '\n')
        for r in rows:
            f.write(r['rid'] + '\t' + '\t'.join(shas[c, r['rid']] or '-' for c in ['d'] + CONFIGS) + '\n')
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        sys.exit(cmd_run(sys.argv[2:]))
    sys.exit(cmd_check(sys.argv[2:]))
