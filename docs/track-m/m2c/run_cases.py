"""M2c (HPP-840, ROADMAP s122 item 758(e)): every case of shader_recompiler_compute_tests (MakeCases + MakeGraphicsCases)
on the MEASUREMENT build (patch_meas.py + patch_meas2.py + patch_meas3.py; host checks skipped, M2C_CASES_ONLY=1) at
one knob setting. The process starts at M2C_FROM; after a device loss the later results of that process are dropped:
a case that lost the device when it was NOT the first case of its process is run again first in a new process (once);
lost as the first case -> result DL, the next process starts after it. A process that ends inside a case (fatal exit,
crash) -> result CRASH for that case, the next process starts after it. Every other KYTY_* removed; cwd = exe folder.
Writes <out>/<name>.tsv (idx, name, result, first failure line) and <out>/<name>_p<k>.log.
Settings: z (all off), ms1 (T234, T233, T306, T032, T203 = 1), all (six = 1), t<T> (one theme).
Usage: python run_cases.py <exe> <out dir> <name>   |   compare <out a>/<name a> <out b>/<name b>.
Lock and STOP before every process. Prints ALL OK when every case PASSes, else FAIL with the list."""
import hashlib
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']
# Cases never run: 224 FlatVirtualAddressRebasesGuestAllocation loses the device -> GPU driver reset (TDR) freezes the
# user's screen (user complaint in HPP-840, 2026-10-12). Needs an exe built with patch_meas4.py (string M2C_SKIP).
SKIP = '224'
BELOW_NORMAL = 0x00004000


def env_for(name):
    if name == 'z':
        return {}
    if name == 'ms1':
        return {'KYTY_M_' + t: '1' for t in THEMES if t != 'T256'}
    if name == 'all':
        return {'KYTY_M_' + t: '1' for t in THEMES}
    assert name[0] == 't' and name[1:] in THEMES, name
    return {'KYTY_M_' + name[1:]: '1'}


def one(exe, out, name, k, start):
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)
    env = {k2: v for k2, v in os.environ.items() if not k2.startswith('KYTY_')}
    env.update(env_for(name))
    env['M2C_CASES_ONLY'] = '1'
    env['M2C_FROM'] = str(start)
    env['M2C_SKIP'] = SKIP
    try:
        p = subprocess.run([exe], capture_output=True, timeout=1500, env=env, cwd=os.path.dirname(exe),
                           creationflags=BELOW_NORMAL)
        rc, data = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc, data = 'timeout', (e.stdout or b'') + (e.stderr or b'')
    open(os.path.join(out, '%s_p%d.log' % (name, k)), 'wb').write(data)
    return rc, data.decode('utf-8', 'replace').replace('\r', '').split('\n')


def parse(lines):
    """[(idx, name, result, msg)] in order; result None when the case did not finish."""
    cases = []
    cur = None
    msg = ''
    for l in lines:
        if l.startswith('[m2c] IDX '):
            parts = l.split(' ', 3)
            cur = [int(parts[2]), parts[3] if len(parts) > 3 else '', None, '']
            cases.append(cur)
            msg = ''
        elif cur is not None and l.startswith('[m2c] ') and cur[2] is None:
            cur[2] = l.split(' ', 2)[1]
            cur[3] = msg
        elif cur is not None and cur[2] is None and 'failed at' in l and not msg:
            msg = l.strip()[:220]
    return cases, any('all cases passed' in l for l in lines)


def run(exe, out, name):
    exe = os.path.abspath(exe)
    if b'M2C_SKIP' not in open(exe, 'rb').read():
        print('REFUSED: exe has no M2C_SKIP (build it with patch_meas4.py) - case 224 would reset the GPU driver')
        sys.exit(5)
    os.makedirs(out, exist_ok=True)
    print('exe', exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest(), 'config', name, env_for(name))
    t0 = time.time()
    results = {}
    start, k, retried = 0, 0, set()
    while True:
        rc, lines = one(exe, out, name, k, start)
        cases, done = parse(lines)
        k += 1
        nxt = None
        for pos, (idx, cname, res, msg) in enumerate(cases):
            if res is None:
                results[idx] = (cname, 'CRASH', 'rc=%s' % rc)
                nxt = idx + 1
                break
            if 'DeviceLost' in msg:
                # no retry (each retry is one more driver reset); stop the whole run - a new device-losing case
                # must be added to SKIP by hand before the next run
                results[idx] = (cname, 'DL', msg)
                print('DEVICE LOST at case %d %s - run stopped, add it to SKIP' % (idx, cname))
                return finish(out, name, results, k, t0)
            results[idx] = (cname, res, msg)
        if nxt is None:
            if done or not cases:
                break
            nxt = cases[-1][0] + 1
        start = nxt
        if k > 400:
            print('too many restarts')
            break
    return finish(out, name, results, k, t0)


def finish(out, name, results, k, t0):
    with open(os.path.join(out, name + '.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for idx in sorted(results):
            cname, res, msg = results[idx]
            f.write('%d\t%s\t%s\t%s\n' % (idx, cname, res, msg))
    bad = [(i, results[i]) for i in sorted(results) if results[i][1] != 'PASS']
    print('%s processes=%d cases=%d not_pass=%d %.1fs' % (name, k, len(results), len(bad), time.time() - t0))
    for i, (cname, res, msg) in bad:
        print('  %d %s %s | %s' % (i, res, cname, msg[:160]))
    print('ALL OK' if not bad and results else 'FAIL')


def load(spec):
    d = {}
    for line in open(spec + '.tsv', encoding='utf-8'):
        idx, cname, res, msg = line.rstrip('\n').split('\t')
        d[cname] = (res, msg)
    return d


def compare(a, b):
    da, db = load(a), load(b)
    names = list(da) + [n for n in db if n not in da]
    diff = 0
    for n in names:
        x, y = da.get(n, ('-', ''))[0], db.get(n, ('-', ''))[0]
        if x != y:
            diff += 1
            print('DIFF %-5s %-5s %s | %s' % (x, y, n, (db.get(n) or da.get(n))[1][:150]))
    print('%s cases %d, %s cases %d, differing %d' % (a, len(da), b, len(db), diff))
    print('ALL OK' if diff == 0 else 'FAIL')


if sys.argv[1] == 'compare':
    compare(sys.argv[2], sys.argv[3])
else:
    run(sys.argv[1], sys.argv[2], sys.argv[3])
