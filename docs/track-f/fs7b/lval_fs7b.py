# FS7b (HPP-566, Red Team): table of values of the two FS7 readings on my own stands (the same sources audio.cpp /
# controller.cpp). Child environment: every KYTY_* and SDL_* removed, then KYTY_FIX_F8 / KYTY_FIX_B24 = <value> unless
# the value is UNSET. F8: stand case 'ii disk 3 dev_'-free form is not needed - case 'ii 1' under SDL_AUDIODRIVER=dummy;
# the reading is seen as the count of 'FixF8: mode=1' lines (1 = on, 0 = off). B24: case 'i' (X holds the joystick lock
# 3 s), the reading is the line fix_b24=<0|1> and the count of 'FixB24: mode=1' lines.
# Expected (form of FS4a 17adaf80 + Common::EnvValueOn): UNSET -> 1, "" -> 1, 0/false/OFF/no -> 0, 1/2/true/" 0" -> 1.
# Halts before a process when the lock or STOP exists (exit 3).
# Usage: python lval_fs7b.py <f8 exe> <b24 exe> <out dir>   -> <out dir>/lval.txt, last line LVALUES ALL OK or FAILED <n>
import os, re, subprocess, sys

f8, b24, outdir = [os.path.abspath(x) for x in sys.argv[1:4]]
os.makedirs(outdir, exist_ok=True)
VALUES = [('UNSET', 1), ('', 1), ('0', 0), ('false', 0), ('OFF', 0), ('no', 0), ('1', 1), ('2', 1), ('true', 1), (' 0', 1)]


def run(exe, args, knob, value, extra):
    if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
        print('HALT lock or STOP', flush=True)
        sys.exit(3)
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_') and not k.upper().startswith('SDL_')}
    env.update(extra)
    if value != 'UNSET':
        env[knob] = value
    cwd = os.path.join(outdir, 'cwd')
    os.makedirs(cwd, exist_ok=True)
    p = subprocess.run([exe] + args, cwd=cwd, env=env, capture_output=True, timeout=120)
    return p.returncode, p.stdout.decode('utf-8', 'replace').replace('\r\n', '\n')


lines = []
nbad = 0
for value, exp in VALUES:
    rc, out = run(f8, ['ii', '1'], 'KYTY_FIX_F8', value, {'SDL_AUDIODRIVER': 'dummy'})
    got = sum(1 for x in out.split('\n') if x == 'FixF8: mode=1')
    m = re.search(r'^init_calls=(\d+)', out, re.M)
    ok = rc == 0 and got == exp
    nbad += 0 if ok else 1
    lines.append('%s F8  value=%r expected=%d FixF8_lines=%d init_calls=%s rc=%d' % ('PASS' if ok else 'FAIL', value, exp, got,
                                                                                   m.group(1) if m else '?', rc))
    rc, out = run(b24, ['i'], 'KYTY_FIX_B24', value, {})
    m = re.search(r'^fix_b24=(\d+)', out, re.M)
    fb = int(m.group(1)) if m else -1
    got = sum(1 for x in out.split('\n') if x == 'FixB24: mode=1')
    ok = rc == 0 and fb == exp and got == exp
    nbad += 0 if ok else 1
    lines.append('%s B24 value=%r expected=%d fix_b24=%d FixB24_lines=%d rc=%d' % ('PASS' if ok else 'FAIL', value, exp, fb, got, rc))
lines.append('LVALUES ALL OK' if nbad == 0 else 'LVALUES FAILED %d' % nbad)
with open(os.path.join(outdir, 'lval.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(0 if nbad == 0 else 1)
