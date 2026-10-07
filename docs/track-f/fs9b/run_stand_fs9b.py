# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): own run of the B13 stand of my own FS9 build
# (C:/kyty/f287/fs9b/build, worktree 11164d72). Not a copy of run_stand_fs9a.py. Child environment: every KYTY_* removed,
# the knob only where the arm names it. Members (named before the run):
#   M1 no variable: forced 11/12/13 x bits 0/1, free 11/12 x 0/1, before/after x 0/1 - lost 0, fix_b13=1, "FixB13: mode=1";
#   M2 KYTY_FIX_B13=0: forced point 1 bits 0 - lost >= 1, fix_b13=0, "FixB13: mode=0";
#   M3 (control of the member, not of the code) no variable, forced point 1 - refused (exit 2): the =0 point is unreachable;
#   M4 value table (mode before, 1 iteration): unset/""/1/2/true/" 0" -> 1; 0/false/off/no/OFF -> 0 (FixB13Enabled form);
#   M5 (reference) swap build no variable forced 11/12/13 bits 0 - lost 0 (the swap target has the =1 order at 1);
#       swap build =0 forced 1 bits 0 - lost 0 (reversed order control).
# Output: stdout + runs_stand/<arm>.txt; last line ALL OK / FAILED.
import os
import re
import subprocess
import sys

B = 'C:/kyty/f287/fs9b/build'
OUT = 'C:/kyty/f287/fs9b/runs_stand'
N = int(os.environ.get('FS9B_N', '100000'))
os.makedirs(OUT, exist_ok=True)
ok = True


def env_with(val):
    e = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
    if val is not None:
        e['KYTY_FIX_B13'] = val
    return e


def run(name, exe, val, mode, point, bits, iters):
    r = subprocess.run([B + '/' + exe, mode, str(point), str(bits), str(iters)], env=env_with(val),
                       capture_output=True, timeout=120)
    txt = r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace')
    open(OUT + '/' + name + '.txt', 'w', encoding='utf-8', newline='\n').write('rc=%d\n%s' % (r.returncode, txt))
    m = re.search(r'B13 build=(\w+) fix_b13=(\d) mode=\S+ point=\d+ bits=\d iters=(\d+) lost=(\d+)', txt)
    fm = re.findall(r'FixB13: mode=(\d)', txt)
    return r.returncode, (m.groups() if m else None), fm


def say(name, cond, extra=''):
    global ok
    ok &= bool(cond)
    print('%-58s %s %s' % (name, 'OK' if cond else 'FAIL', extra), flush=True)


print('N per arm', N)
for mode, pts in (('forced', (11, 12, 13)), ('free', (11, 12)), ('before', (11,)), ('after', (11,))):
    for p in pts:
        for b in (0, 1):
            name = 'M1_unset_%s_p%d_b%d' % (mode, p, b)
            rc, g, fm = run(name, 'b13_epoch_stand.exe', None, mode, p, b, N)
            say(name, rc == 0 and g and g[0] == 'code' and g[1] == '1' and int(g[2]) == N and g[3] == '0' and fm == ['1'],
                'rc=%d %s FixB13=%s' % (rc, g, fm))
rc, g, fm = run('M2_k0_forced_p1_b0', 'b13_epoch_stand.exe', '0', 'forced', 1, 0, N)
say('M2_k0_forced_p1_b0 lost >= 1', rc == 0 and g and g[1] == '0' and int(g[3]) >= 1 and fm == ['0'],
    'rc=%d %s FixB13=%s' % (rc, g, fm))
rc, g, fm = run('M3_unset_forced_p1_b0', 'b13_epoch_stand.exe', None, 'forced', 1, 0, 10)
say('M3_unset_forced_p1_b0 refused (exit 2)', rc == 2, 'rc=%d %s' % (rc, g))
for val, want in ((None, '1'), ('', '1'), ('1', '1'), ('2', '1'), ('true', '1'), (' 0', '1'),
                  ('0', '0'), ('false', '0'), ('off', '0'), ('no', '0'), ('OFF', '0')):
    nm = 'M4_val_%s' % ('unset' if val is None else repr(val).replace(' ', '_').replace("'", ''))
    rc, g, fm = run(nm, 'b13_epoch_stand.exe', val, 'before', 11 if want == '1' else 1, 0, 1)
    say('%s -> %s' % (nm, want), rc == 0 and g and g[1] == want and fm == [want], 'rc=%d %s FixB13=%s' % (rc, g, fm))
for p in (11, 12, 13):
    rc, g, fm = run('M5_swap_unset_forced_p%d_b0' % p, 'b13_epoch_stand_swap.exe', None, 'forced', p, 0, N)
    say('M5_swap_unset_forced_p%d_b0 lost 0' % p, rc == 0 and g and g[0] == 'swap' and g[1] == '1' and g[3] == '0', 'rc=%d %s' % (rc, g))
rc, g, fm = run('M5_swap_k0_forced_p1_b0', 'b13_epoch_stand_swap.exe', '0', 'forced', 1, 0, N)
say('M5_swap_k0_forced_p1_b0 lost 0', rc == 0 and g and g[0] == 'swap' and g[1] == '0' and g[3] == '0', 'rc=%d %s' % (rc, g))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
