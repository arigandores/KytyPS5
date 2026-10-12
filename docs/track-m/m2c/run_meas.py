"""M2c (HPP-840, ROADMAP s122 item 758(e)): run the MEASUREMENT build of shader_recompiler_compute_tests (patch_meas.py:
every top-level check and case wrapped, one failure does not stop the run) at one knob setting, in its own process,
every other KYTY_* removed, cwd = the exe folder. Writes <out>/<name>.log and <out>/<name>.tsv (label, PASS/FAIL/EXC).
Settings: z (all off), ms1 (T234, T233, T306, T032, T203 = 1; mask 0x3b), all (six = 1; mask 0x3f), t<T> (one theme).
Usage: python run_meas.py <exe> <out dir> <name> [cases] (cases: M2C_CASES_ONLY=1, only the case loops). Lock and STOP before the process.
  compare <out> <a> <b>  - labels whose result differs between <a>.tsv and <b>.tsv; prints ALL OK when none."""
import hashlib
import os
import subprocess
import sys
import time

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
THEMES = ['T234', 'T233', 'T256', 'T306', 'T032', 'T203']


def env_for(name):
    if name == 'z':
        return {}
    if name == 'ms1':
        return {'KYTY_M_' + t: '1' for t in THEMES if t != 'T256'}
    if name == 'all':
        return {'KYTY_M_' + t: '1' for t in THEMES}
    assert name[0] == 't' and name[1:] in THEMES, name
    return {'KYTY_M_' + name[1:]: '1'}


def read_tsv(path):
    rows = {}
    order = []
    for line in open(path, encoding='utf-8'):
        label, result = line.rstrip('\n').split('\t')
        if label not in rows:
            order.append(label)
        rows[label] = result
    return order, rows


def compare(out, a, b):
    oa, ra = read_tsv(os.path.join(out, a + '.tsv'))
    ob, rb = read_tsv(os.path.join(out, b + '.tsv'))
    diff = 0
    for label in oa + [l for l in ob if l not in ra]:
        x, y = ra.get(label, '-'), rb.get(label, '-')
        if x != y:
            diff += 1
            print('DIFF %-6s %-6s %s' % (x, y, label))
    print('%s: %d labels, FAIL %d; %s: %d labels, FAIL %d; differing %d' % (
        a, len(ra), sum(1 for v in ra.values() if v != 'PASS'), b, len(rb), sum(1 for v in rb.values() if v != 'PASS'),
        diff))
    print('ALL OK' if diff == 0 else 'FAIL')


def run(exe, out, name):
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        sys.exit(3)
    exe = os.path.abspath(exe)
    os.makedirs(out, exist_ok=True)
    print('exe', exe, hashlib.sha256(open(exe, 'rb').read()).hexdigest(), 'config', name, env_for(name))
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(env_for(name))
    if len(sys.argv) > 4 and sys.argv[4] == 'cases':
        env['M2C_CASES_ONLY'] = '1'  # patch_meas2.py: host checks skipped
    t0 = time.time()
    try:
        p = subprocess.run([exe], capture_output=True, timeout=3300, env=env, cwd=os.path.dirname(exe))
        rc, data = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        rc, data = 'timeout', (e.stdout or b'') + (e.stderr or b'')
    open(os.path.join(out, name + '.log'), 'wb').write(data)
    text = data.decode('utf-8', 'replace').replace('\r', '')
    rows = []
    for line in text.split('\n'):
        if line.startswith('[m2c] '):
            parts = line.split(' ', 2)
            rows.append((parts[2] if len(parts) > 2 else '', parts[1]))
    with open(os.path.join(out, name + '.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        for label, result in rows:
            f.write('%s\t%s\n' % (label, result))
    fails = [r for r in rows if r[1] != 'PASS']
    passed = 'ShaderRecompilerComputeTests: all cases passed' in text
    print('%s rc=%s %.1fs labels=%d fail=%d end_line=%d' % (name, rc, time.time() - t0, len(rows), len(fails),
                                                          1 if passed else 0))
    for label, result in fails:
        print('  %s %s' % (result, label))
    print('ALL OK' if rc == 0 and passed and len(rows) > 0 else 'FAIL')


if sys.argv[1] == 'compare':
    compare(sys.argv[2], sys.argv[3], sys.argv[4])
else:
    run(sys.argv[1], sys.argv[2], sys.argv[3])
