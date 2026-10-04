# F18c (HPP-539, ROADMAP s122 item 441(d)(1)): driver of the F8 stand tests/F8AudioStand.cpp (target f8_audio_stand) -
# one process per run, each in its own working directory under <out dir>/cwd_<run>. Child environment: every KYTY_*
# variable removed, then KYTY_FIX_F8=<fix> unless fix is 'unset'; SDL_AUDIODRIVER set per run (dummy or disk - never a host
# driver; the stand itself refuses anything else, run 'refuse' checks that).
# Members (item 441(d)(1)): (i) direct path - after A init calls of the opens and 253..255 more calls the old ids queue
# fine, after call 257 - A every opened device fails with "Invalid audio device ID"; (ii) SdlAudioAcquire - 10 000 calls,
# 0 queue failures, SDL_WasInit(AUDIO) != 0, init_calls 1; (iii) 2 threads x 5 000 SdlAudioAcquire - init_calls 1.
# The driver "dummy" has one output device only (SDL_dummyaudio.c:55, SDL_audio.c:1367): three devices are opened under
# "disk" (SDL_AUDIODRIVER=disk, device name = output file in the run directory), one under "dummy"; run i_dummy3_fix0
# shows the refusal of the 2nd and 3rd dummy open. Controls: the same loop as (i) at KYTY_FIX_F8=1 (no failure, init_calls 1),
# KYTY_FIX_F8 unset (= 0), the driver refusal.
# Halts before a run when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists (rules 27, 26).
# Usage: python run_stand_f18c.py <exe> <out dir>    -> <out dir>/stand_f18c.txt, last line ALL OK or FAILED <n>
import hashlib, os, re, subprocess, sys, time

exe, outdir = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(outdir, exist_ok=True)
sha = hashlib.sha256(open(exe, 'rb').read()).hexdigest()
ERR = 'Invalid audio device ID'


def run(name, args, driver, fix):
    cwd = os.path.join(outdir, 'cwd_' + name)
    os.makedirs(cwd, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_') and k.upper() != 'SDL_AUDIODRIVER'}
    if fix != 'unset':
        env['KYTY_FIX_F8'] = fix
    if driver is not None:
        env['SDL_AUDIODRIVER'] = driver
    t0 = time.time()
    p = subprocess.run([exe] + args, cwd=cwd, env=env, capture_output=True, timeout=120)
    out = p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
    open(os.path.join(outdir, 'out_' + name + '.txt'), 'w', encoding='utf-8', newline='\n').write(out)
    kv = {}
    for line in out.split('\n'):
        m = re.match(r'^([a-z_]+)=(.*)$', line)
        if m and m.group(1) not in kv:
            kv[m.group(1)] = m.group(2).strip('"')
    kv['_rc'] = p.returncode
    kv['_fixf8_lines'] = sum(1 for line in out.split('\n') if line == 'FixF8: mode=1')
    kv['_end'] = out.rstrip('\n').endswith('END')
    kv['_open_failed'] = [line for line in out.split('\n') if line.startswith('open_failed=')]
    kv['_calls'] = [tuple(map(int, m.groups())) for m in re.finditer(r'^call (\d+) fail (\d+)$', out, re.M)]
    kv['_wall'] = time.time() - t0
    return kv


def num(kv, k):
    return int(kv.get(k, '-1'))


results = []


def check(name, kv, conds):
    bad = [c for c, ok in conds if not ok]
    results.append((name, not bad, bad, kv))


def direct(name, driver, ndev, prefix, fix, opened, inits):
    # inits = init calls of the opens (one per open attempt, as site C1); first failure expected at call 257 - inits.
    args = ['i', str(ndev)] + ([prefix] if prefix else [])
    kv = run(name, args, driver, fix)
    exp = 257 - inits
    calls = kv['_calls']
    check(name, kv, [
        ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
        ('devices_opened %d' % opened, num(kv, 'devices_opened') == opened),
        ('open_failed %d' % (ndev - opened), len(kv['_open_failed']) == ndev - opened),
        ('first_fail_call %d' % exp, num(kv, 'first_fail_call') == exp),
        ('fail_devices_at_first %d of %d' % (opened, opened), num(kv, 'fail_devices_at_first') == opened),
        ('every call >= %d fails on all devices' % exp, len(calls) == 300 - exp + 1 and all(f == opened for _, f in calls)),
        ('first_error %s' % ERR, kv.get('first_error') == ERR),
        ('init_calls %d' % (inits + 300), num(kv, 'init_calls') == inits + 300),
        ('acq 0', num(kv, 'acq') == 0),
        ('no FixF8 line', kv['_fixf8_lines'] == 0),
        ('driver %s' % driver, kv.get('driver') == driver),
    ])
    return kv


def direct_fix1(name, driver, ndev, prefix, opened):
    args = ['i', str(ndev)] + ([prefix] if prefix else [])
    kv = run(name, args, driver, '1')
    check(name, kv, [
        ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
        ('devices_opened %d' % opened, num(kv, 'devices_opened') == opened),
        ('first_fail_call 0', num(kv, 'first_fail_call') == 0),
        ('queue_failed 0', num(kv, 'queue_failed') == 0),
        ('init_failed 0', num(kv, 'init_failed') == 0),
        ('init_calls 1', num(kv, 'init_calls') == 1),
        ('acq %d' % (ndev + 300), num(kv, 'acq') == ndev + 300),
        ('was_init != 0', num(kv, 'was_init') != 0),
        ('one FixF8 line', kv['_fixf8_lines'] == 1),
    ])


def acquire(name, driver, ndev, prefix):
    args = ['ii', str(ndev)] + ([prefix] if prefix else [])
    kv = run(name, args, driver, '1')
    check(name, kv, [
        ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
        ('devices_opened %d' % ndev, num(kv, 'devices_opened') == ndev),
        ('calls 10000', num(kv, 'calls') == 10000),
        ('queue_failed 0', num(kv, 'queue_failed') == 0),
        ('init_failed 0', num(kv, 'init_failed') == 0),
        ('was_init != 0', num(kv, 'was_init') != 0),
        ('init_calls 1', num(kv, 'init_calls') == 1),
        ('acq %d' % (ndev + 10000), num(kv, 'acq') == ndev + 10000),
        ('one FixF8 line', kv['_fixf8_lines'] == 1),
    ])


def threads(name, driver, ndev, prefix):
    args = ['iii', str(ndev)] + ([prefix] if prefix else [])
    kv = run(name, args, driver, '1')
    check(name, kv, [
        ('rc 0 and END', kv['_rc'] == 0 and kv['_end']),
        ('acquire_failed 0', num(kv, 'acquire_failed') == 0),
        ('init_calls_after_threads 1', num(kv, 'init_calls_after_threads') == 1),
        ('acq_after_threads 10000', num(kv, 'acq_after_threads') == 10000),
        ('was_init_after_threads != 0', num(kv, 'was_init_after_threads') != 0),
        ('devices_opened %d' % ndev, num(kv, 'devices_opened') == ndev),
        ('queue_failed_after 0', num(kv, 'queue_failed_after') == 0),
        ('init_calls 1', num(kv, 'init_calls') == 1),
    ])


plan = [
    lambda: direct('i_disk3_fix0', 'disk', 3, 'dev_', '0', 3, 3),
    lambda: direct('i_dummy1_fix0', 'dummy', 1, None, '0', 1, 1),
    lambda: direct('i_dummy3_fix0', 'dummy', 3, None, '0', 1, 3),
    lambda: direct('i_disk3_unset', 'disk', 3, 'dev_', 'unset', 3, 3),
    lambda: acquire('ii_disk3_fix1', 'disk', 3, 'dev_'),
    lambda: acquire('ii_dummy1_fix1', 'dummy', 1, None),
    lambda: threads('iii_dummy1_fix1', 'dummy', 1, None),
    lambda: threads('iii_disk3_fix1', 'disk', 3, 'dev_'),
    lambda: direct_fix1('i_disk3_fix1', 'disk', 3, 'dev_', 3),
    lambda: direct_fix1('i_dummy1_fix1', 'dummy', 1, None, 1),
]

for step in plan:
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('HALT lock or STOP')
        sys.exit(3)
    step()

kv = run('refuse', ['i', '1'], None, '0')
check('refuse', kv, [('rc 3', kv['_rc'] == 3), ('no device opened', 'devices_opened' not in kv)])
kv = run('refuse_host', ['i', '1'], 'directsound', '0')
check('refuse_host', kv, [('rc 3', kv['_rc'] == 3), ('no device opened', 'devices_opened' not in kv)])

with open(os.path.join(outdir, 'stand_f18c.txt'), 'w', encoding='utf-8', newline='\n') as f:
    def w(s):
        print(s)
        f.write(s + '\n')
    w('# exe %s sha256 %s' % (exe, sha))
    nbad = 0
    for name, ok, bad, kv in results:
        keys = ['devices_opened', 'first_fail_call', 'fail_devices_at_first', 'queue_failed', 'first_error', 'init_calls',
                'acq', 'was_init', 'init_calls_after_threads', 'acq_after_threads', 'acquire_failed', 'driver']
        vals = ' '.join('%s=%s' % (k, kv[k]) for k in keys if k in kv)
        w('%s %s rc=%s fixf8_lines=%d open_failed=%d wall=%.1fs %s' % ('PASS' if ok else 'FAIL', name, kv['_rc'],
                                                                         kv['_fixf8_lines'], len(kv['_open_failed']),
                                                                         kv['_wall'], vals))
        for c in bad:
            w('    failed: ' + c)
        nbad += 0 if ok else 1
    w('ALL OK' if nbad == 0 else 'FAILED %d' % nbad)
sys.exit(0 if nbad == 0 else 1)
