"""F18e (HPP-541): manual sensitivity of test_f18e_read.py - each edit of f18e_read.py below must make the suite fail (exit != 0).
usage: python sens_f18e.py   (ASCII only; ends with ALL OK when every edit is caught)"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'f18e_read.py'), 'rb').read().decode('utf-8')
print('suite sens_f18e.py sha256 %s target f18e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('fire + 10 s -> + 11 s', 'S0_F8_AFTER_FIRE_US = 10000000', 'S0_F8_AFTER_FIRE_US = 11000000'),
    ('s0 init 256 -> 255', 'S0_INIT_MIN = 256', 'S0_INIT_MIN = 255'),
    ('s0 ratio 5 -> 4.9', 'S0_RATIO_MIN = 5.0', 'S0_RATIO_MIN = 4.9'),
    ('s1 acq 300 -> 299', 'S1_ACQ_MIN = 300', 'S1_ACQ_MIN = 299'),
    ('s1 ratio band widened', 'S1_RATIO_LO, S1_RATIO_HI = 0.95, 1.05', 'S1_RATIO_LO, S1_RATIO_HI = 0.94, 1.06'),
    ('n0 init band widened', 'N0_INIT_LO, N0_INIT_HI = 254, 257', 'N0_INIT_LO, N0_INIT_HI = 253, 258'),
    ('n0 window width 16 -> 17', 'N0_STEP_S, N0_WRAP, N0_WIDTH_S = 3, 256, 16', 'N0_STEP_S, N0_WRAP, N0_WIDTH_S = 3, 256, 17'),
    ('n0 wrap 256 -> 257', 'N0_STEP_S, N0_WRAP, N0_WIDTH_S = 3, 256, 16', 'N0_STEP_S, N0_WRAP, N0_WIDTH_S = 3, 257, 16'),
    ('n1 acq 250 -> 249', 'N1_ACQ_MIN = 250', 'N1_ACQ_MIN = 249'),
    ('live rate 0.25 -> 0.2', 'LIVE_RATE_MIN = 0.25', 'LIVE_RATE_MIN = 0.2'),
    ('status 2 not allowed (letter before item 448)', 'STATUS_OK = (1, 2)', 'STATUS_OK = (1,)'),
    ('status 0 allowed', 'STATUS_OK = (1, 2)', 'STATUS_OK = (0, 1, 2)'),
    ('done attempts not checked', 'DONE_ATTEMPTS = 300', 'DONE_ATTEMPTS = 299'),
    ('window skip 5 s -> 4 s', 'WIN_SKIP_US = 5000000', 'WIN_SKIP_US = 4000000'),
    ('video 3000 -> 2999', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ('frame >= 1 s +1 us', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('W1 upper edge inclusive', "if s['dev'] == 0 or s['t'] < lo or (hi is not None and s['t'] >= hi):",
     "if s['dev'] == 0 or s['t'] < lo or (hi is not None and s['t'] > hi):"),
    ('window lower edge exclusive', "if s['dev'] == 0 or s['t'] < lo or (hi is not None and s['t'] >= hi):",
     "if s['dev'] == 0 or s['t'] <= lo or (hi is not None and s['t'] >= hi):"),
    ('dev = 0 rows counted in rates', "if s['dev'] == 0 or s['t'] < lo", "if s['t'] < lo"),
    ('every port -> any port', "    if any(x is False for x in res):\n        mem = False", "    if all(x is False for x in res):\n        mem = False"),
    ('N5 KYTY_HAPTICS in env allowed', "and 'KYTY_HAPTICS' not in env", ''),
    ('N5 disabled line allowed', "           ('lines Haptics: disabled by KYTY_HAPTICS=0 = 0 (N5)', r['hap_off'] == 0),\n", ''),
    ('Haptics opened allowed', "           ('lines Haptics: pad audio device ... opened = 0', r['hap_open'] == 0),\n", ''),
    ('A = 0 admitted', "r['a'] is not None and r['a'] >= 1", "r['a'] is not None and r['a'] >= 0"),
    ('A counted over the whole log', "                r['a'] = r['opened']\n", ''),
    ('prereg not checked', "None if run is None or seal_sha is None else pre == seal_sha", 'True'),
    ('json binary not checked', '(jbin == BIN_EXPECT and inst == BIN_EXPECT)', '(inst == BIN_EXPECT)'),
    ('installed_sha not checked', '(jbin == BIN_EXPECT and inst == BIN_EXPECT)', '(jbin == BIN_EXPECT)'),
    ('stand value not checked', "and env.get('KYTY_TEST_AUDIOLOSS') == (STAND_VALUE if sp['stand'] else None)", ''),
    ('other KYTY_FIX_ allowed', "and fix_keys == ['KYTY_FIX_F8']", ''),
    ('FixF8 count not checked', "(len(r['fix']) == 1 and r['fix'][0][1] == 1)", "(len(r['fix']) >= 1)"),
    ('n TestAudioLoss lines allowed', "else r['tal'] == 0", 'else True'),
    ('config invalid allowed', "(r['config_on'] == 1 and r['config_bad'] == 0)", "(r['config_on'] == 1)"),
    ('minimized not interference', "interf = bool(r['win'].get('minimized')) or ", 'interf = '),
    ('N1 host noise off', "only_init = host_noise_member and sum(1 for v in vals if v is False) == 1", 'only_init = False'),
    ('N1 host noise even with other failures', "only_init = host_noise_member and sum(1 for v in vals if v is False) == 1",
     'only_init = host_noise_member'),
    ('F counts only AudioOut', "F = r['init_out'] + r['init_in']", "F = r['init_out']"),
    ('s0 refutation off', "refuted = r['f8'] == 0 and r['fire'] is not None and r['done'] is not None", 'refuted = False'),
    ('n0 refutation without coverage', 'refuted = r[\'f8\'] == 0 and cover is True and live', 'refuted = r[\'f8\'] == 0 and live'),
    ('n0 init read after the F8 line', "before = [s for s in stat if r['f8_first'] is not None and s['ln'] < r['f8_first']]",
     "before = [s for s in stat if r['f8_first'] is not None]"),
    ('s0 bracket up ignored (low only)', "elif r['f8_up'] is not None and r['f8_up'] <= r['fire'][1] + S0_F8_AFTER_FIRE_US:",
     "elif r['f8_low'] is not None and r['f8_low'] <= r['fire'][1] + S0_F8_AFTER_FIRE_US:"),
    ('s0 first row after done -> last row', "mem.append(('init_calls in the first AudioStat row after done >= 256 (%s)' % (after[0]['init_calls'] if after else None),\n                    None if not after else after[0]['init_calls'] >= S0_INIT_MIN))",
     "mem.append(('init_calls in the first AudioStat row after done >= 256 (%s)' % (after[-1]['init_calls'] if after else None),\n                    None if not after else after[-1]['init_calls'] >= S0_INIT_MIN))"),
    ('n1 init only on the last row', "bad = [s['ln'] for s in stat if s['init_calls'] > 1]", "bad = [s['ln'] for s in stat[-1:] if s['init_calls'] > 1]"),
    ('harm hold length not checked', "and (att.get('hold_s') or 0) >= sp['hold']", ''),
    ('stdout death ignored', "death = r['death'] + (sd or [])", "death = r['death']"),
    ('harm off for s1/n1', "harm_on = tag in ('f8_s1', 'f8_n1')", 'harm_on = False'),
    ('harm on for s0/n0', "harm_on = tag in ('f8_s1', 'f8_n1')", 'harm_on = True'),
    ('ident q_fail off', "        if s['q_fail'] > s['pushes']:\n            q.append(s['ln'])", "        pass"),
    ('ident acq at =0 off', "        if fix == '0' and s['acq'] != 0:\n            acq0.append(s['ln'])", "        pass"),
    ('ident decrease across ports', "        prev = last.get(s['port'])", "        prev = last.get(0)"),
    ('manifest always EQUAL', "bool(mc) and mc.startswith('manifest cmp EQUAL')", 'True'),
    ('installed after not checked', "('installed adb0c82f after the return', sha_a == WANT)", "('installed adb0c82f after the return', True)"),
    ('scene change does not end the hold', "if after_entry and r['scene_change_line'] is None:", 'if after_entry:'),
]
T = tempfile.mkdtemp(prefix='f18e_sens_')
bad = []
try:
    shutil.copy2(os.path.join(HERE, 'test_f18e_read.py'), os.path.join(T, 'test_f18e_read.py'))
    for name, old, new in EDITS:
        if SRC.count(old) != 1:
            bad.append(name)
            print('ANCHOR %s: count %d' % (name, SRC.count(old)))
            continue
        open(os.path.join(T, 'f18e_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
        p = subprocess.run([sys.executable, os.path.join(T, 'test_f18e_read.py')], capture_output=True, cwd=T)
        caught = p.returncode != 0
        nf = [x for x in p.stdout.decode('ascii', 'replace').split('\n') if x.startswith('checks ')]
        print('%s %s (%s)' % ('CAUGHT' if caught else 'MISSED', name, nf[-1].strip() if nf else 'no count'))
        if not caught:
            bad.append(name)
finally:
    shutil.rmtree(T, ignore_errors=True)
print('edits %d missed %d' % (len(EDITS), len(bad)))
if bad:
    sys.exit(1)
print('ALL OK')
