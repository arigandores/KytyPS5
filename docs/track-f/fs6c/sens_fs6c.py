"""FS6c (HPP-557): manual sensitivity of test_fs6c_read.py - each edit of fs6c_read.py below must make the suite fail (exit != 0).
Port of F15e sens_f15e.py with the edits of the env at the defaults of the binary and of the W rows.
usage: python sens_fs6c.py   (ASCII only; ends with ALL OK when every edit is caught)"""
import concurrent.futures, hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'fs6c_read.py'), 'rb').read().decode('utf-8')
print('suite sens_fs6c.py sha256 %s target fs6c_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('hold threshold 300 s - 1 us', 'HOLD_MIN_US = 300000000', 'HOLD_MIN_US = 299999999'),
    ('video threshold 2999', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ('frame >= 1 s threshold +1 us', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('FixB4 order vs the first GuestOut ignored', "and (r['guest_first'] is None or r['b4'][0][0] < r['guest_first']))", ')'),
    ('FixB4 mode ignored', 'all(mm == 1 for _, mm in r[\'b4\'])', 'True'),
    ('fatal counted before quit too', "                if r['quit_line'] is not None:\n                    r['fatal_after_quit'] += 1",
     "                r['fatal_after_quit'] += 1"),
    ('m_files line not counted', "                    r['null_after_quit'] += 1", "                    pass"),
    ('killed ignored', "end_ok = att.get('close_killed') is False and att.get('close_rc') is not None",
     "end_ok = att.get('close_rc') is not None"),
    ('KYTY_FIX_ in the env allowed', "env_ok = None if run is None else (fix_keys == [] and ", "env_ok = None if run is None else ("),
    ('GAME_PATCH allowed', "and 'KYTY_GAME_PATCH' not in env", ''),
    ('GPU_CHECKPOINTS allowed', "and 'KYTY_GPU_CHECKPOINTS' not in env)", ')'),
    ('version string ignored', 'return VERSION in open(path, \'rb\').read()', 'return True'),
    ('version string of F15c', "VERSION = b'KytyPS5-2026-09-15-6a2987a-1879-g3904522d'", "VERSION = b'KytyPS5-2026-09-15-6a2987a-1878-g5c2c5e52'"),
    ('tag binary expected F15c', "BIN_EXPECT = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'",
     "BIN_EXPECT = '907569f641bfea9fb9881213b77588a2c8365a084512e5ef734baf5aae82aff1'"),
    ('installed after not checked', 'after_ok=sha_a == WANT', 'after_ok=True'),
    ('installed before not checked', 'before_ok=sha_b == WANT', 'before_ok=True'),
    ('manifest always EQUAL', "manifest_ok=bool(mc) and mc.startswith('manifest cmp EQUAL')", 'manifest_ok=True'),
    ('scene change does not end the hold', "if after_entry and r['scene_change_line'] is None:", 'if after_entry:'),
    ('hold_exit ignored', "hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None", "hold_ok = att.get('outcome') == 'ok'"),
    ('minimized not interference', "not res['win'].get('minimized') and ", ''),
    ('stdout death ignored', "death = r['death'] + (sd or [])", "death = r['death']"),
    ('W: [Vulkan][E] not counted', "                    r['vke'] += 1", "                    pass"),
    ('W: positive control ignored', "('positive control of the layer, [Vulkan][W] > 0', res['vkw'] > 0)",
     "('positive control of the layer, [Vulkan][W] > 0', True)"),
    ('W: DualSrcBlend enabled ignored', "dual_ok=any(s == 1 and e == 1 and", "dual_ok=any(s == 1 and"),
    ('W: DualSrcBlend order ignored', "(r['guest_first'] is None or ln < r['guest_first'])\n", "True\n"),
    ('W kind gets the video members', "    if k == 'v':\n        m += [", "    if True:\n        m += ["),
]
T = tempfile.mkdtemp(prefix='fs6c_sens_')
bad = []


def one(i, name, old, new):
    d = os.path.join(T, 'e%02d' % i)
    os.makedirs(d)
    shutil.copy2(os.path.join(HERE, 'test_fs6c_read.py'), os.path.join(d, 'test_fs6c_read.py'))
    open(os.path.join(d, 'fs6c_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
    p = subprocess.run([sys.executable, os.path.join(d, 'test_fs6c_read.py')], capture_output=True, cwd=d)
    nf = [x for x in p.stdout.decode('ascii', 'replace').split(chr(10)) if x.startswith('checks ')]
    return p.returncode != 0, nf[-1].strip() if nf else 'no count'


try:
    jobs = []
    for i, (name, old, new) in enumerate(EDITS):
        if SRC.count(old) != 1:
            bad.append(name)
            print('ANCHOR %s: count %d' % (name, SRC.count(old)))
            continue
        jobs.append((i, name, old, new))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda j: one(*j), jobs))
    for (i, name, old, new), (caught, cnt) in zip(jobs, res):
        print('%s %s (%s)' % ('CAUGHT' if caught else 'MISSED', name, cnt))
        if not caught:
            bad.append(name)
finally:
    shutil.rmtree(T, ignore_errors=True)
print('edits %d missed %d' % (len(EDITS), len(bad)))
if bad:
    sys.exit(1)
print('ALL OK')
