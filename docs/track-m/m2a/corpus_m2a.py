"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(ii)-(iii), (g)(2)): the T1 corpus (C:/kyty/s288/s7, rows of corpus_f12d.py:
A rows, outcome not HARNESS_UNSUPPORTED, perm != '-') translated offline by the FS15 build (base) and the M2a build (dev) at
the knob settings
  base  FS15 exe, every KYTY_* unset             u     dev exe, every KYTY_* unset
  z     dev exe, the six KYTY_M_<theme>=0         t<T>  dev exe, KYTY_M_<T>=1 (one theme)
  all   dev exe, the six knobs =1
each row by KYTY_RECOMPILE="<gcn>;<cache file>;<out.spv>;<perm>" in its own process (other KYTY_* removed). Rows already
done (out.spv + rc.txt) are not run again, so the run can be split (--configs). Lock and STOP before every process.
Modes:
  run <base exe> <dev exe> <out> [--configs c1,c2] [--workers N]
  predict <dev exe> <out>      - KYTY_M_DECODE (the translator's own decoder) over every corpus GCN dump; per theme the set
                                 of programs with the instruction -> <out>/predict.tsv (written before the theme runs)
  check <out>                  - members: u == base and z == base byte for byte on every row; per theme the set of
                                 programs with a row t<T> != base is a subset of the predicted set and >= 1; all = union;
                                 prints the table and ALL OK / FAIL, writes corpus_m2a.tsv
"""
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
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']
CONFIGS = ['base', 'u', 'z'] + ['t' + t for t in THEMES] + ['all']


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
    elif name == 'all':
        for t in THEMES:
            env['KYTY_M_' + t] = '1'
    elif name.startswith('t'):
        env['KYTY_M_' + name[1:]] = '1'
    return env


def cmd_run(argv):
    base_exe, dev_exe, out = argv[0], argv[1], argv[2]
    configs = CONFIGS
    workers = 8
    for i, a in enumerate(argv):
        if a == '--configs':
            configs = argv[i + 1].split(',')
        if a == '--workers':
            workers = int(argv[i + 1])
    check_halt()
    rows = load_rows()
    jobs = [(r, c) for r in rows for c in configs]
    print('rows', len(rows), 'configs', configs, 'processes', len(jobs))
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
        exe = base_exe if name == 'base' else dev_exe
        try:
            p = subprocess.run([exe], cwd=work, env=env, capture_output=True, timeout=300)
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


PATTERNS = {
    'T234': lambda fam, op, text: fam == 16 and re.search(r': DS_M(IN|AX)_F32 ', text) is not None,
    'T233': lambda fam, op, text: (fam == 8 and op in (0x141, 0x11f)) or (fam == 7 and op in (0x1f, 0x20, 0x21)),
    'T203': lambda fam, op, text: re.search(r': V_ALIGNBYTE_B32 ', text) is not None,
    'T306': lambda fam, op, text: fam == 17 and re.search(r': IMAGE_SAMPLE\w* ', text, re.I) is not None and
    re.search(r'sample_flags=\S*offset', text) is not None,
    'T032': lambda fam, op, text: fam in (13, 14) and re.search(r': T?BUFFER_STORE_FORMAT_(X|XY|XYZ|XYZW) ', text)
    is not None,
    'T256': lambda fam, op, text: False,
}


def cmd_predict(argv):
    dev_exe, out = argv[0], argv[1]
    check_halt()
    rows = load_rows()
    progs = {}
    for r in rows:
        progs.setdefault((r['stage'], r['hash16']), gcn_path(r))
    os.makedirs(out + '/decode', exist_ok=True)
    table = []
    sets = collections.defaultdict(set)
    counts = collections.defaultdict(int)
    for (stage, h), g in sorted(progs.items()):
        check_halt()
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        env['KYTY_M_DECODE'] = g
        p = subprocess.run([dev_exe], env=env, capture_output=True, timeout=120)
        text = p.stdout.decode('utf-8', 'replace')
        open('%s/decode/%s_%s.txt' % (out, stage, h), 'w', newline='\n').write(text)
        hits = collections.Counter()
        for line in text.split('\n'):
            m = re.match(r'pc=0x[0-9a-f]+ fam=(\d+) op=0x([0-9a-f]+) (.*)$', line)
            if not m:
                continue
            fam, op, rest = int(m.group(1)), int(m.group(2), 16), m.group(3)
            for t, f in PATTERNS.items():
                if f(fam, op, rest):
                    hits[t] += 1
        ok_decode = p.returncode == 0 and 'm-decode: words=' in text
        for t in THEMES:
            if hits[t]:
                sets[t].add(h)
                counts[t] += hits[t]
        table.append('\t'.join([stage, h, str(int(ok_decode))] + [str(hits[t]) for t in THEMES]))
    with open(out + '/predict.tsv', 'w', newline='\n') as f:
        f.write('\t'.join(['stage', 'hash16', 'decode_ok'] + THEMES) + '\n')
        f.write('\n'.join(table) + '\n')
    print('programs', len(progs), 'decode failures', sum(1 for t in table if t.split('\t')[2] != '1'))
    for t in THEMES:
        print('predict %s programs %d instructions %d' % (t, len(sets[t]), counts[t]))
    print('predict.tsv sha256', sha256_file(out + '/predict.tsv'))
    return 0


def cmd_check(argv):
    out = argv[0]
    rows = load_rows()
    pred = collections.defaultdict(set)
    with open(out + '/predict.tsv') as f:
        hdr = f.readline().rstrip('\n').split('\t')
        for line in f:
            c = dict(zip(hdr, line.rstrip('\n').split('\t')))
            for t in THEMES:
                if int(c[t]) > 0:
                    pred[t].add(c['hash16'])
    ok = True

    def res(name, r):
        work = '%s/%s/%s' % (out, name, r['rid'])
        rc = open(work + '/rc.txt').read().strip() if os.path.exists(work + '/rc.txt') else 'missing'
        sha = sha256_file(work + '/out.spv') if rc == '0' and os.path.exists(work + '/out.spv') else None
        return rc, sha

    table = []
    changed = collections.defaultdict(set)
    bad_rc = []
    for r in rows:
        shas = {}
        for c in CONFIGS:
            rc, sha = res(c, r)
            if sha is None:
                bad_rc.append((r['rid'], c, rc))
            shas[c] = sha
        for c in CONFIGS[3:]:
            if shas[c] != shas['base']:
                changed[c].add(r['hash16'])
        table.append('\t'.join([r['rid'], r['stage'], r['hash16'], r['perm']] + [shas[c] or '-' for c in CONFIGS]))
    with open(out + '/corpus_m2a.tsv', 'w', newline='\n') as f:
        f.write('\t'.join(['row', 'stage', 'hash16', 'perm'] + ['sha_' + c for c in CONFIGS]) + '\n')
        f.write('\n'.join(table) + '\n')
    print('rows', len(rows), 'processes', len(rows) * len(CONFIGS), 'failed', len(bad_rc), bad_rc[:5])
    ok &= not bad_rc
    for c in ('u', 'z'):
        diff = [l.split('\t')[0] for l in table if l.split('\t')[4 + CONFIGS.index(c)] != l.split('\t')[4]]
        print('G2 %s == base on %d of %d rows (differ %d) %s' % (c, len(rows) - len(diff), len(rows), len(diff),
                                                                diff[:3]))
        ok &= not diff
    union = set()
    for t in THEMES:
        c = 't' + t
        outside = sorted(changed[c] - pred[t])
        union |= changed[c]
        member = not outside and (len(changed[c]) >= 1)
        print('theme %s predicted %d changed %d changed-not-predicted %d predicted-not-changed %d %s %s' % (
            t, len(pred[t]), len(changed[c]), len(outside), len(pred[t] - changed[c]),
            'MEMBER_OK' if member else ('NONE_CHANGED' if not changed[c] and not outside else 'OUTSIDE'), outside[:5]))
        if t != 'T256':
            ok &= member
        else:
            ok &= not outside
    print('all changed %d union of themes %d all-not-in-union %s' % (len(changed['all']), len(union),
                                                                   sorted(changed['all'] - union)[:5]))
    ok &= changed['all'] <= union
    print('corpus_m2a.tsv sha256', sha256_file(out + '/corpus_m2a.tsv'))
    print('ALL OK' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    mode = sys.argv[1]
    sys.exit({'run': cmd_run, 'predict': cmd_predict, 'check': cmd_check}[mode](sys.argv[2:]))
