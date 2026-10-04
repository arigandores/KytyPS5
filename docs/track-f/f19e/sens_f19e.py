"""F19e (HPP-549): manual sensitivity of test_f19e_read.py - each edit of f19e_read.py below must make the suite fail (exit != 0).
usage: python sens_f19e.py   (ASCII only; ends with ALL OK when every edit is caught)"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'f19e_read.py'), 'rb').read().decode('utf-8')
print('suite sens_f19e.py sha256 %s target f19e_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    ('frame >= 1 s +1 us', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('frame >= 1 s -1 us', 'K2_US = 1000000', 'K2_US = 999999'),
    ('window pre 1 s -> 1.1 s', 'WIN_PRE_US = 1000000', 'WIN_PRE_US = 1100000'),
    ('window pre 1 s -> 0.9 s', 'WIN_PRE_US = 1000000', 'WIN_PRE_US = 900000'),
    ('block 2700000 -> 2700001', 'BLOCK_US = 2700000', 'BLOCK_US = 2700001'),
    ('block 2700000 -> 2699999', 'BLOCK_US = 2700000', 'BLOCK_US = 2699999'),
    ('free 50000 -> 50001', 'FREE_US = 50000', 'FREE_US = 50001'),
    ('free 50000 -> 49999', 'FREE_US = 50000', 'FREE_US = 49999'),
    ('video 3000 -> 2999', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ('delay 60 -> 30', "DELAY = '60'", "DELAY = '30'"),
    ('hold_ms 3000 -> 2000', "HOLD_MS = '3000'", "HOLD_MS = '2000'"),
    ('wide window: pre-fire frames off', '        wide.add(i)\n', '        pass\n'),
    ('wide window: break condition >=', '        if acc > WIN_PRE_US:', '        if acc >= WIN_PRE_US:'),
    ('strict window to the end of the log', 'strict = set(i for i, fr in enumerate(frames) if fire_ln < fr[0] < stat_ln)',
     'strict = set(i for i, fr in enumerate(frames) if fire_ln < fr[0])'),
    ('members read the strict window', 'k2w = None if wide is None else sorted(i for i in wide if frames[i][2] >= K2_US)',
     'k2w = None if strict is None else sorted(i for i in strict if frames[i][2] >= K2_US)'),
    ('harm counts the window too', 'k2_out = [i for i in k2_scene if i not in out_win]', 'k2_out = list(k2_scene)'),
    ('harm off for h1/n1', "harm_on = tag in ('b24_h1', 'b24_n1')", 'harm_on = False'),
    ('harm on for all', "harm_on = tag in ('b24_h1', 'b24_n1')", 'harm_on = True'),
    ('stop iteration off', "elif stop_member is not None and mem[stop_member][1] is False:", 'elif False:'),
    ('h0 stop member index shifted', "        stop_member = len(mem)\n        mem.append((win_txt + ' >= 1'", "        stop_member = 0\n        mem.append((win_txt + ' >= 1'"),
    ('identities ignored', "    elif any(v is False for _, v in ident):\n        word = 'IDENT_FAIL'\n", ''),
    ('identities after harm', "    elif any(v is False for _, v in ident):\n        word = 'IDENT_FAIL'\n    elif any(v is False for v in hv):\n        word = 'HARM_FAIL'\n",
     "    elif any(v is False for v in hv):\n        word = 'HARM_FAIL'\n    elif any(v is False for _, v in ident):\n        word = 'IDENT_FAIL'\n"),
    ('ident pad_calls sum drops trig', "st['pad_calls'] == st['pad_vib'] + st['pad_led'] + st['pad_trig']", "st['pad_calls'] >= st['pad_vib'] + st['pad_led']"),
    ('ident probes <=', "st['probes_run'] <= st['probes_posted']", "True"),
    ('ident removed in hold not checked', "st['removed'] == (1 if sp['mode'] == 'detach' else 0)", "st['removed'] <= 1"),
    ('ident t_us fire < done strict', 'ts[0] < ts[1] < ts[2] <= ts[3]', 'ts[0] < ts[1] < ts[2] < ts[3]'),
    ('ident t_us armed <= attach', 'ts[0] < ts[1] < ts[2] <= ts[3]', 'ts[0] <= ts[1] < ts[2] <= ts[3]'),
    ('ident t_us attach-fire not checked', 'ts[0] < ts[1] < ts[2] <= ts[3]', 'ts[0] < ts[1] and ts[2] <= ts[3]'),
    ('invariant =0 po_wait not checked', "st['po_applied'] == 0 and st['po_wait_max_us'] == 0", "st['po_applied'] == 0"),
    ('invariant =0 po_applied not checked', "st['po_applied'] == 0 and st['po_wait_max_us'] == 0", "st['po_wait_max_us'] == 0"),
    ('invariant =1 guest_sdl not checked', "ident.append(('invariant guest_sdl = 0 at =1', None if st is None else st['guest_sdl'] == 0))",
     "ident.append(('invariant guest_sdl = 0 at =1', True))"),
    ('prereg not checked', "None if run is None or seal_sha is None else pre == seal_sha", 'True'),
    ('json binary not checked', '(jbin == BIN_EXPECT and inst == BIN_EXPECT)', '(inst == BIN_EXPECT)'),
    ('installed_sha not checked', '(jbin == BIN_EXPECT and inst == BIN_EXPECT)', '(jbin == BIN_EXPECT)'),
    ('stand env value not checked', "and env.get('KYTY_TEST_HIDLOSS') == want_stand", ''),
    ('other KYTY_FIX_ allowed', "and fix_keys == ['KYTY_FIX_B24']", ''),
    ('game patch allowed', "and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env", "and 'KYTY_GPU_CHECKPOINTS' not in env"),
    ('checkpoints allowed', "and 'KYTY_GAME_PATCH' not in env and 'KYTY_GPU_CHECKPOINTS' not in env", "and 'KYTY_GAME_PATCH' not in env"),
    ('FixB24 count not checked', "fix_ok = (len(r['fix']) == 1 and r['fix'][0][1] == 1) if", "fix_ok = (len(r['fix']) >= 1) if"),
    ('FixB24 at =0 allowed', "if sp['fix'] == '1' else len(r['fix']) == 0", "if sp['fix'] == '1' else True"),
    ('other pad allowed', "           ('pad lines of another pad = 0 (%s)' % [x[2] for x in other_pads][:3], not other_pads)]", '           ]'),
    ('config invalid allowed', "and cfg[3] == HOLD_MS and r['config_bad'] == 0)", 'and cfg[3] == HOLD_MS)'),
    ('config mode not checked', "cfg[1] == DELAY and cfg[2] == sp['mode'] and", "cfg[1] == DELAY and"),
    ('armed not required', "('armed exactly 1 line (%d)' % len(r['armed']), armed is not None)", "('armed exactly 1 line (%d)' % len(r['armed']), True)"),
    ('attach not required', "% (len(r['attach']), r['attach_bad']), attach is not None)", "% (len(r['attach']), r['attach_bad']), True)"),
    ('test pad line not required', "len(test_pads) == 1)", 'True)'),
    ('fire mode not checked', "fire is not None and fire[2] == sp['mode'])", 'fire is not None)'),
    ('done not required', "('done exactly 1 line (%d)' % len(r['done']), done is not None)", "('done exactly 1 line (%d)' % len(r['done']), True)"),
    ('stat mode not checked', "st is not None and st['mode'] == sp['mode'] and r['stat_bad'] == 0)", "st is not None and r['stat_bad'] == 0)"),
    ('stat malformed allowed', "st is not None and st['mode'] == sp['mode'] and r['stat_bad'] == 0)", "st is not None and st['mode'] == sp['mode'])"),
    ('pad_calls >= 0', "None if st is None else st['pad_calls'] >= 1),", "None if st is None else st['pad_calls'] >= 0),"),
    ('probe difference not checked', "None if st is None else st['probes_posted'] - st['probes_run'] == 0)", 'True)'),
    ('N5 quit order not checked', "and (r['quit_line'] is None or r['quit_line'] > st['ln'])", ''),
    ('N5 attach < stat not checked', "attach is not None and st is not None and attach[0] < st['ln']", "attach is not None and st is not None"),
    ('n1 TestHidLoss lines allowed', "adm += [('lines TestHidLoss: = 0 (%d)' % r['thl'], r['thl'] == 0),", "adm += [('lines TestHidLoss: = 0 (%d)' % r['thl'], True),"),
    ('n1 pad lines allowed', "('pad lines = 0 (%d)' % len(r['pads']), not r['pads'])]", "('pad lines = 0 (%d)' % len(r['pads']), True)]"),
    ('minimized not interference', "interf = bool(r['win'].get('minimized')) or ", 'interf = '),
    ('manifest always EQUAL', "bool(mc) and mc.startswith('manifest cmp EQUAL')", 'True'),
    ('installed after not checked', "('installed adb0c82f after the return', sha_a == WANT)", "('installed adb0c82f after the return', True)"),
    ('harm hold length not checked', "and (att.get('hold_s') or 0) >= sp['hold']", ''),
    ('stdout death ignored', "death = r['death'] + (sd or [])", "death = r['death']"),
    ('scene change does not end the hold', "if after_entry and r['scene_change_line'] is None:", 'if after_entry:'),
    ('removed line regex accepts the debug form', "RX_REMOVED = re.compile(rb'Controller (-?\\d+): removed\\b')", "RX_REMOVED = re.compile(rb'Controller.*removed')"),
    ('d removed lines count >= 1', "len(r['removed']) == 1))", "len(r['removed']) >= 1))"),
    ('d removed counter >= 1', "None if st is None else st['removed'] == 1))", "None if st is None else st['removed'] >= 1))"),
    ('h1 guest_sdl member off', "None if st is None else st['guest_sdl'] == 0))\n        mem.append((win_txt + ' = 0'", "True))\n        mem.append((win_txt + ' = 0'"),
    ('h1 po_wait member off', "None if st is None else st['po_wait_max_us'] >= BLOCK_US))", 'True))'),
    ('h0 pad_wait member off', "mem.append(('pad_wait_max_us >= 2700000 (%s)' % g('pad_wait_max_us'), None if st is None else st['pad_wait_max_us'] >= BLOCK_US))",
     "mem.append(('pad_wait_max_us >= 2700000 (%s)' % g('pad_wait_max_us'), True))"),
    ('n1 FixB24 member off', "    elif tag == 'b24_n1':\n        mem.append(('line FixB24: mode=1 (%d)' % len(r['fix']), len(r['fix']) == 1 and r['fix'][0][1] == 1))",
     "    elif tag == 'b24_n1':\n        mem.append(('line FixB24: mode=1 (%d)' % len(r['fix']), True))"),
]
T = tempfile.mkdtemp(prefix='f19e_sens_')
bad = []
try:
    shutil.copy2(os.path.join(HERE, 'test_f19e_read.py'), os.path.join(T, 'test_f19e_read.py'))
    for name, old, new in EDITS:
        if SRC.count(old) != 1:
            bad.append(name)
            print('ANCHOR %s: count %d' % (name, SRC.count(old)))
            continue
        open(os.path.join(T, 'f19e_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
        p = subprocess.run([sys.executable, os.path.join(T, 'test_f19e_read.py')], capture_output=True, cwd=T)
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
