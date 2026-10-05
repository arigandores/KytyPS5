"""FS7c (HPP-567): manual sensitivity of test_fs7c_read.py - each edit of fs7c_read.py below must make the suite fail (exit != 0).
Port of F19e sens_f19e.py.  usage: python sens_fs7c.py   (ASCII only; ends with ALL OK when every edit is caught)"""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, 'fs7c_read.py'), 'rb').read().decode('utf-8')
print('suite sens_fs7c.py sha256 %s target fs7c_read.py sha256 %s' % (
    hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), hashlib.sha256(SRC.encode('utf-8')).hexdigest()))
EDITS = [
    # constants
    ('frame >= 1 s +1 us', 'K2_US = 1000000', 'K2_US = 1000001'),
    ('frame >= 1 s -1 us', 'K2_US = 1000000', 'K2_US = 999999'),
    ('window pre 1 s -> 1.1 s', 'WIN_PRE_US = 1000000', 'WIN_PRE_US = 1100000'),
    ('window pre 1 s -> 0.9 s', 'WIN_PRE_US = 1000000', 'WIN_PRE_US = 900000'),
    ('block 2700000 -> 2700001', 'BLOCK_US = 2700000', 'BLOCK_US = 2700001'),
    ('block 2700000 -> 2699999', 'BLOCK_US = 2700000', 'BLOCK_US = 2699999'),
    ('free 50000 -> 50001', 'FREE_US = 50000', 'FREE_US = 50001'),
    ('free 50000 -> 49999', 'FREE_US = 50000', 'FREE_US = 49999'),
    ('video 3000 -> 2999', 'VIDEO_MIN = 3000', 'VIDEO_MIN = 2999'),
    ('acq 250 -> 251', 'N1_ACQ_MIN = 250', 'N1_ACQ_MIN = 251'),
    ('acq 250 -> 249', 'N1_ACQ_MIN = 250', 'N1_ACQ_MIN = 249'),
    ('status {1, 2} -> {1}', 'STATUS_OK = (1, 2)', 'STATUS_OK = (1,)'),
    ('status {1, 2} -> {0, 1, 2}', 'STATUS_OK = (1, 2)', 'STATUS_OK = (0, 1, 2)'),
    ('delay 60 -> 30', "DELAY = '60'", "DELAY = '30'"),
    ('hold_ms 3000 -> 2000', "HOLD_MS = '3000'", "HOLD_MS = '2000'"),
    ('hold fs7_n 840 -> 839', "'fs7_n': dict(mode=None, hold=840)", "'fs7_n': dict(mode=None, hold=839)"),
    ('hold fs7_h 330 -> 331', "'fs7_h': dict(mode='hold', hold=330)", "'fs7_h': dict(mode='hold', hold=331)"),
    ('expected installed = FS7', "WANT = '9325446c", "WANT = '8df61c00"),
    ('revision text d6ee2dc -> 3904522', "REV = 'd6ee2dc'", "REV = '3904522'"),
    # Fix members and N4
    ('first GuestOut = level start line', "M_GUEST = b'GuestOut:'", "M_GUEST = b'GuestOut: Level has started: '"),
    ('FixF8 needs the order (N4 broken)', "f8v, f8d = fix_member(r['fixl']['F8'], fg, False)", "f8v, f8d = fix_member(r['fixl']['F8'], fg, True)"),
    ('FixB24 order not checked', "b24v, b24d = fix_member(r['fixl']['B24'], fg, True)", "b24v, b24d = fix_member(r['fixl']['B24'], fg, False)"),
    ('FixB4 order not checked', "b4v, b4d = fix_member(r['fixl']['B4'], fg, True)", "b4v, b4d = fix_member(r['fixl']['B4'], fg, False)"),
    ('Fix other lines ignored', '    ok = len(ones) == 1 and not other\n', '    ok = len(ones) == 1\n'),
    ('Fix count >= 1', '    ok = len(ones) == 1 and not other\n', '    ok = len(ones) >= 1 and not other\n'),
    ('Fix before -> before or equal later', '    return ones[0] < first_guest, det', '    return ones[0] < first_guest + 1000, det'),
    ('Fix without GuestOut -> True', '    if first_guest is None:\n        return None, det', '    if first_guest is None:\n        return True, det'),
    ('FixB4 prefix matches FixB42', "M_FIX = {'F8': b'FixF8:', 'B24': b'FixB24:', 'B4': b'FixB4:'}",
     "M_FIX = {'F8': b'FixF8:', 'B24': b'FixB24:', 'B4': b'FixB4'}"),
    ('fs7_n members without FixB24', "        mem.append((fix_rows[0][0], fix_rows[0][1]))\n        mem.append(('lines TestHidLoss: = 0",
     "        mem.append((fix_rows[0][0], True))\n        mem.append(('lines TestHidLoss: = 0"),
    ('fs7_n TestHidLoss member off', "        mem.append(('lines TestHidLoss: = 0 (%d)' % r['thl'], r['thl'] == 0))",
     "        mem.append(('lines TestHidLoss: = 0 (%d)' % r['thl'], True))"),
    ('fs7_h members without Fix rows', '        mem += fix_rows\n', '        pass\n'),
    # admission
    ('version string not checked', "VERSION in open(p['bin'], 'rb').read()),", "True),"),
    ('revision not checked', "bool(r['rev']) and all(x == REV for x in r['rev'])", 'True'),
    ('revision any instead of all and empty ok', "bool(r['rev']) and all(x == REV for x in r['rev'])", 'all(x == REV for x in r[\'rev\'])'),
    ('env: KYTY_FIX_* allowed', '    common_env = (not fix_keys and ', '    common_env = (True and '),
    ('env: KYTY_HAPTICS allowed', "'KYTY_HAPTICS' not in env and 'KYTY_GAME_PATCH'", "'KYTY_GAME_PATCH'"),
    ('env: KYTY_TEST_AUDIOLOSS allowed', "\n                  and 'KYTY_TEST_AUDIOLOSS' not in env)", ')'),
    ('env n: AV_TRACE not required', "(common_env and env.get('KYTY_AV_TRACE') == '1' and 'KYTY_TEST_HIDLOSS' not in env)",
     "(common_env and 'KYTY_TEST_HIDLOSS' not in env)"),
    ('env n: HIDLOSS allowed', "(common_env and env.get('KYTY_AV_TRACE') == '1' and 'KYTY_TEST_HIDLOSS' not in env)",
     "(common_env and env.get('KYTY_AV_TRACE') == '1')"),
    ('env h: stand value not checked', "(common_env and env.get('KYTY_TEST_HIDLOSS') == '%s:%s' % (DELAY, sp['mode']))", '(common_env)'),
    ('N5 quit order not checked', "                 and (r['quit_line'] is None or r['quit_line'] > st['ln']))]", '                 )]'),
    ('n vibration admission off', "        adm += [('line AudioOut: vibration port present', r['vib_line'] is not None),",
     "        adm += [('line AudioOut: vibration port present', True),"),
    ('n A >= 1 -> A >= 0', "r['a'] is not None and r['a'] >= 1", "r['a'] is not None and r['a'] >= 0"),
    ('n TestAudioLoss admission off', "('lines TestAudioLoss: = 0 (%d)' % r['tal'], r['tal'] == 0)", "('lines TestAudioLoss: = 0 (%d)' % r['tal'], True)"),
    ('interference ignored', "    adm.append(('no interference: window minimized / Recovering Vulkan swapchain / GamePatch line', not interf))\n", ''),
    ('form ignored', "    elif any(v is not True for _, v in form):\n        word = 'FORM_FAIL'\n", ''),
    # members
    ('h members read the strict window', 'k2w = None if wide is None else sorted(i for i in wide if frames[i][2] >= K2_US)',
     'k2w = None if strict is None else sorted(i for i in strict if frames[i][2] >= K2_US)'),
    ('wide window: pre-fire frames off', '        wide.add(i)\n', '        pass\n'),
    ('h guest_sdl member off', "None if st is None else st['guest_sdl'] == 0))\n        mem.append(('frames >= 1 s in the stand window",
     "True))\n        mem.append(('frames >= 1 s in the stand window"),
    ('h po_wait member off', "None if st is None else st['po_wait_max_us'] >= BLOCK_US))", 'True))'),
    ('n F8 member off', "mem.append(('F8 lines in the whole log = 0 (%d)' % r['f8'], r['f8'] == 0))",
     "mem.append(('F8 lines in the whole log = 0 (%d)' % r['f8'], True))"),
    ('n init_calls <= 2', "bad = [s['ln'] for s in astat if s['init_calls'] > 1]", "bad = [s['ln'] for s in astat if s['init_calls'] > 2]"),
    ('n acq reads the first row', '        last = astat[-1] if astat else None\n', '        last = astat[0] if astat else None\n'),
    ('n status reads dev 0 rows too', "    astat_dev = [s for s in astat if s['dev'] != 0]", '    astat_dev = list(astat)'),
    ('host noise off', "        word = 'HOST_NOISE' if only_init else 'MEMBERS_FAIL'", "        word = 'MEMBERS_FAIL'"),
    ('host noise for any F', "        host_noise_member = (v is False and F >= 1)", "        host_noise_member = (v is False)"),
    # harm, identities, order
    ('harm counts the window too (h)', 'k2_out = [i for i in k2_scene if i not in out_win]', 'k2_out = list(k2_scene)'),
    ('identities ignored (h)', "    elif any(v is False for v in iv):\n        word = 'IDENT_FAIL'\n", ''),
    ('identities after harm', "    elif any(v is False for v in iv):\n        word = 'IDENT_FAIL'\n    elif any(v is False for v in hv):\n        word = 'HARM_FAIL'\n",
     "    elif any(v is False for v in hv):\n        word = 'HARM_FAIL'\n    elif any(v is False for v in iv):\n        word = 'IDENT_FAIL'\n"),
    ('n identities are gates', '    iv = [v for _, v in ident] if stand else []', '    iv = [v for _, v in ident]'),
    ('ident t_us fire < done strict', 'ts[0] < ts[1] < ts[2] <= ts[3]', 'ts[0] < ts[1] < ts[2] < ts[3]'),
    ('ident removed not checked', "ident.append(('removed = 0 in hold', None if st is None else st['removed'] == 0))",
     "ident.append(('removed = 0 in hold', True))"),
    ('hold_s check off', "(att.get('hold_s') or 0) >= sp['hold']", 'True'),
    ('no glitch file -> pass', "('0 one-frame glitches (%s)' % gl, None if gl is None else gl == 0)", "('0 one-frame glitches (%s)' % gl, gl in (None, 0))"),
    ('exit is a gate', "        hold_ok = att.get('outcome') == 'ok' and att.get('hold_exit') is None",
     "        hold_ok = att.get('close_rc') == 0 and att.get('outcome') == 'ok' and att.get('hold_exit') is None"),
]
T = tempfile.mkdtemp(prefix='fs7c_sens_')
bad = []
try:
    shutil.copy2(os.path.join(HERE, 'test_fs7c_read.py'), os.path.join(T, 'test_fs7c_read.py'))
    for name, old, new in EDITS:
        if SRC.count(old) != 1:
            bad.append(name)
            print('ANCHOR %s: count %d' % (name, SRC.count(old)))
            continue
        open(os.path.join(T, 'fs7c_read.py'), 'wb').write(SRC.replace(old, new).encode('utf-8'))
        p = subprocess.run([sys.executable, os.path.join(T, 'test_fs7c_read.py')], capture_output=True, cwd=T)
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
