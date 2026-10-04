# F19c (HPP-547, ROADMAP s122 item 451(e)(1)): driver of the B24 stand tests/B24PadStand.cpp (target b24_pad_stand) -
# one process per run, each in its own working directory under <out dir>/cwd_<run>. Child environment: every KYTY_* and
# SDL_* variable removed, then KYTY_FIX_B24=<fix> unless fix is 'unset'. The stand switches the host joystick drivers off
# by hints (only the SDL virtual driver is left); num_joysticks_at_init = 0 checks that no host device was enumerated.
# Members (item 451(e)(1)): (i) =0: X holds SDL_LockJoysticks 3000 ms, Y calls SetVibration with new values - wall
# >= 2 700 ms; (ii) =1, the same: each wall of SetVibration, SetLightBar, SetTriggerEffect < 50 ms, guest_sdl = 0, the
# Rumble callback of the virtual pad holds the last written value <= 100 ms after the lock is released; (iii) =1:
# 2 threads x 10 000 SetVibration with random values while the pad is attached and detached - no crash (rc 0 and END),
# every received value was written (rumble_bad 0), the last applied value = the last written one.
# Controls: (i) with KYTY_FIX_B24 unset (= 0) and at =1 (the wall falls under 50 ms); (ii) at =0 (the walls stay >= 2 700 ms
# for the first call, guest_sdl > 0).
# Halts before a run when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists (rules 27, 26).
# Usage: python run_stand_f19c.py <exe> <out dir>    -> <out dir>/stand_f19c.txt, last line ALL OK or FAILED <n>
import hashlib, os, re, subprocess, sys, time

exe, outdir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
HOLD_US = 2700000
FAST_US = 50000
LAT_US = 100000


def run(name, case, fix):
    cwd = os.path.join(outdir, 'cwd_' + name)
    os.makedirs(cwd, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_') and not k.upper().startswith('SDL_')}
    if fix != 'unset':
        env['KYTY_FIX_B24'] = fix
    t0 = time.time()
    p = subprocess.run([exe, case], cwd=cwd, env=env, capture_output=True, timeout=180)
    out = p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
    open(os.path.join(outdir, 'out_' + name + '.txt'), 'w', encoding='utf-8', newline='\n').write(out)
    kv = {}
    for line in out.split('\n'):
        m = re.match(r'^([a-z_0-9]+)=(.*)$', line)
        if m and m.group(1) not in kv:
            kv[m.group(1)] = m.group(2).strip('"')
    kv['_rc'] = p.returncode
    kv['_fixb24_lines'] = sum(1 for line in out.split('\n') if line == 'FixB24: mode=1')
    kv['_end'] = out.rstrip('\n').endswith('END')
    kv['_wall'] = time.time() - t0
    return kv


def num(kv, k):
    try:
        return int(kv.get(k, '-1'))
    except ValueError:
        return -1


results = []


def check(name, kv, conds):
    bad = [c for c, ok in conds if not ok]
    results.append((name, not bad, bad, kv))


def common(kv, fix1):
    return [
        ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
        ('num_joysticks_at_init 0 (no host device)', num(kv, 'num_joysticks_at_init') == 0),
        ('connected 1', num(kv, 'connected') == 1),
        ('fix_b24 %d' % (1 if fix1 else 0), num(kv, 'fix_b24') == (1 if fix1 else 0)),
        ('FixB24 lines %d' % (1 if fix1 else 0), kv['_fixb24_lines'] == (1 if fix1 else 0)),
        ('shutdown_ok 1', num(kv, 'shutdown_ok') == 1),
        ('rumble_bad 0', num(kv, 'rumble_bad') == 0),
    ]


def case_i(name, fix):
    kv = run(name, 'i', fix)
    fix1 = fix == '1'
    conds = common(kv, fix1) + [('pad_vib 1', num(kv, 'pad_vib') == 1)]
    if fix1:
        conds += [('wall_vib_us < %d' % FAST_US, 0 <= num(kv, 'wall_vib_us') < FAST_US),
                  ('guest_sdl 0', num(kv, 'guest_sdl') == 0)]
    else:
        conds += [('wall_vib_us >= %d' % HOLD_US, num(kv, 'wall_vib_us') >= HOLD_US),
                  ('guest_sdl >= 2', num(kv, 'guest_sdl') >= 2),
                  ('po_applied 0', num(kv, 'po_applied') == 0),
                  ('po_wait_max_us 0', num(kv, 'po_wait_max_us') == 0)]
    check(name, kv, conds)


def case_ii(name, fix):
    kv = run(name, 'ii', fix)
    fix1 = fix == '1'
    conds = common(kv, fix1) + [
        ('pad_vib 3, pad_led 1, pad_trig 1', (num(kv, 'pad_vib'), num(kv, 'pad_led'), num(kv, 'pad_trig')) == (3, 1, 1)),
        ('trig_ok 1', num(kv, 'trig_ok') == 1),
        ('latency_us in [0, %d]' % LAT_US, 0 <= num(kv, 'latency_us') <= LAT_US) if fix1 else ('latency_us >= -1', True),
        ('last_after_300ms_ok 1', num(kv, 'last_after_300ms_ok') == 1),
    ]
    if fix1:
        conds += [('wall_vib_us < %d' % FAST_US, 0 <= num(kv, 'wall_vib_us') < FAST_US),
                  ('wall_led_us < %d' % FAST_US, 0 <= num(kv, 'wall_led_us') < FAST_US),
                  ('wall_trig_us < %d' % FAST_US, 0 <= num(kv, 'wall_trig_us') < FAST_US),
                  ('y_done_before_unlock 1', num(kv, 'y_done_before_unlock') == 1),
                  ('guest_sdl 0', num(kv, 'guest_sdl') == 0),
                  ('po_wait_max_us >= 2 500 000 (PadOutput waited the lock)', num(kv, 'po_wait_max_us') >= 2500000)]
    else:
        conds += [('wall_vib_us >= %d' % HOLD_US, num(kv, 'wall_vib_us') >= HOLD_US),
                  ('guest_sdl > 0', num(kv, 'guest_sdl') > 0),
                  ('po_applied 0', num(kv, 'po_applied') == 0)]
    check(name, kv, conds)


def case_iii(name):
    kv = run(name, 'iii', '1')
    conds = common(kv, True) + [
        ('writes 20000', num(kv, 'writes') == 20000),
        ('pad_vib 20001', num(kv, 'pad_vib') == 20001),
        ('guest_sdl 0', num(kv, 'guest_sdl') == 0),
        ('churn_cycles >= 20', num(kv, 'churn_cycles') >= 20),
        ('detaches >= 10 and removes >= 10', num(kv, 'detaches') >= 10 and num(kv, 'removes') >= 10),
        ('final_connected 1', num(kv, 'final_connected') == 1),
        ('latency_us in [0, %d]' % LAT_US, 0 <= num(kv, 'latency_us') <= LAT_US),
        ('last_after_300ms_ok 1 (last applied = last written)', num(kv, 'last_after_300ms_ok') == 1),
        ('rumble_calls > 0', num(kv, 'rumble_calls') > 0),
    ]
    check(name, kv, conds)


plan = [
    lambda: case_i('i_fix0', '0'),
    lambda: case_i('i_unset', 'unset'),
    lambda: case_ii('ii_fix1', '1'),
    lambda: case_iii('iii_fix1'),
    lambda: case_i('i_fix1', '1'),
    lambda: case_ii('ii_fix0', '0'),
    lambda: case_iii('iii_fix1_b'),
]

for step in plan:
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('HALT lock or STOP')
        sys.exit(3)
    step()

with open(os.path.join(outdir, 'stand_f19c.txt'), 'w', encoding='utf-8', newline='\n') as f:
    def w(s):
        print(s)
        f.write(s + '\n')
    w('# exe %s sha256 %s' % (exe, sha))
    nbad = 0
    keys = ['num_joysticks_at_init', 'fix_b24', 'wall_vib_us', 'wall_led_us', 'wall_trig_us', 'y_done_before_unlock',
            'latency_us', 'last_after_300ms_ok', 'writes', 'churn_cycles', 'attaches', 'detaches', 'adds', 'removes',
            'final_connected', 'pad_vib', 'pad_led', 'pad_trig', 'pad_wait_max_us', 'po_applied', 'po_wait_max_us',
            'guest_sdl', 'rumble_calls', 'rumble_bad', 'led_calls', 'effect_calls']
    for name, ok, bad, kv in results:
        vals = ' '.join('%s=%s' % (k, kv[k]) for k in keys if k in kv)
        w('%s %s rc=%s fixb24_lines=%d wall=%.1fs %s' % ('PASS' if ok else 'FAIL', name, kv['_rc'], kv['_fixb24_lines'],
                                                        kv['_wall'], vals))
        for c in bad:
            w('    failed: ' + c)
        nbad += 0 if ok else 1
    w('ALL OK' if nbad == 0 else 'FAILED %d' % nbad)
sys.exit(0 if nbad == 0 else 1)
