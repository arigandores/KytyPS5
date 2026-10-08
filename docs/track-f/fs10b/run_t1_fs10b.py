# FS10b (HPP-685, Red Team, ROADMAP s122 item 624(e)(2)): own run of t1 / t1b on my build of the FS10 source (worktree
# C:/kyty/f287/fs10b/wt on dc5d4712). Own driver (not a copy of run_tests_fs10a.py). Every child gets an environment
# without any KYTY_* variable; the knob only where named. Members, named before the run:
#  T1  my log_async_tests.exe <dir>: rc 0, last line "ALL OK", "failures=0".
#  T1b =0 byte for byte with the code before F25k: the F25k reference executable (f25k/ref/log_async_tests_ref.exe,
#      sha256 printed) "--child seq0" (no variable) == mine "--child seq0" at KYTY_FIX_B36=0 (sha256). Negative controls:
#      mine unset and mine =1 differ from it.
#  T1c the value table of the FS10a read (first "LogAsync:" line of the seq0 file): unset, "1", "true", "on", "yes", "2",
#      "TRUE" -> "LogAsync: mode=1 ..."; "0", "false", "off", "no", "OFF", "No" -> no "LogAsync:" line; "" printed (on
#      Windows an empty value may reach getenv as "" or be dropped - both read as ON by the code).
#  T1d path =1 of FS10 = path =1 of T2 (the binary of the series F25m, worktree f25k2/wt HEAD 0c8fcba2): T2
#      log_async_tests.exe "--child seq0" at KYTY_FIX_B36=1 and mine unset (default) and mine =1 - the lines without the
#      "LogAsync:" prefix equal; the "LogAsync: mode=" line equal; the summary line printed (its byte counts may differ only
#      by timing fields). T2 =0 == mine =0 byte for byte.
import hashlib
import os
import subprocess
import sys

B = 'C:/kyty/f287/fs10b/build'
MINE = B + '/log_async_tests.exe'
REF = 'C:/kyty/f287/f25k/ref/log_async_tests_ref.exe'
T2X = 'C:/kyty/f287/f25k2/build/log_async_tests.exe'
OUT = 'C:/kyty/f287/fs10b/runs_t1'
ok = True


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else '-'


def env(val=None, unset=True):
    e = {k: v for k, v in os.environ.items() if not k.upper().startswith('KYTY_')}
    if val is not None:
        e['KYTY_FIX_B36'] = val
    return e


def member(name, cond, text=''):
    global ok
    print('%s %s %s' % ('OK  ' if cond else 'FAIL', name, text))
    ok &= bool(cond)


def child(exe, path, val):
    if os.path.exists(path):
        os.remove(path)
    r = subprocess.run([exe, '--child', 'seq0', path], capture_output=True, env=env(val))
    return r.returncode


def first_async(p):
    for ln in open(p, 'rb').read().decode('utf-8', 'replace').split('\n'):
        if ln.startswith('LogAsync:'):
            return ln
    return ''


def without(p, prefix='LogAsync:'):
    return [ln for ln in open(p, 'rb').read().split(b'\n') if not ln.startswith(prefix.encode())]


os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if os.path.isfile(OUT + '/' + f):
        os.remove(OUT + '/' + f)
print('exe mine %s ref %s T2 %s' % (sha(MINE)[:16], sha(REF)[:16], sha(T2X)[:16]))

# T1
LA = OUT + '/la'
os.makedirs(LA, exist_ok=True)
r = subprocess.run([MINE, LA], capture_output=True, env=env())
so = r.stdout.decode('utf-8', 'replace')
open(OUT + '/log_async_tests.log', 'w', encoding='utf-8', newline='\n').write(so + r.stderr.decode('utf-8', 'replace'))
lines = so.splitlines()
summ = [ln for ln in lines if 'failures=' in ln]
member('T1 log_async_tests rc 0, ALL OK, failures=0', r.returncode == 0 and lines and lines[-1] == 'ALL OK' and summ and 'failures=0' in summ[-1],
       'rc=%d last=%r %s' % (r.returncode, lines[-1] if lines else '', summ[-1] if summ else ''))

# T1b
rr = child(REF, OUT + '/ref.txt', None)
r0 = child(MINE, OUT + '/m0.txt', '0')
ru = child(MINE, OUT + '/mu.txt', None)
r1 = child(MINE, OUT + '/m1.txt', '1')
h = {k: sha(OUT + '/' + k + '.txt') for k in ('ref', 'm0', 'mu', 'm1')}
print('   rc ref %d m0 %d mu %d m1 %d; sha ref %s m0 %s mu %s m1 %s' % (rr, r0, ru, r1, h['ref'][:16], h['m0'][:16], h['mu'][:16], h['m1'][:16]))
member('T1b mine =0 == reference (code before F25k)', rr == 0 and r0 == 0 and h['ref'] == h['m0'] and h['ref'] != '-')
member('T1b negative control: mine unset differs', h['mu'] != h['ref'])
member('T1b negative control: mine =1 differs', h['m1'] != h['ref'])

# T1c
table = [(None, True), ('1', True), ('true', True), ('on', True), ('yes', True), ('2', True), ('TRUE', True),
         ('0', False), ('false', False), ('off', False), ('no', False), ('OFF', False), ('No', False), ('', True)]
for i, (val, want_on) in enumerate(table):
    p = OUT + '/v%02d.txt' % i
    rc = child(MINE, p, val)
    fa = first_async(p) if os.path.exists(p) else '<no file>'
    got_on = fa.startswith('LogAsync: mode=1 ')
    got_off = fa == ''
    member('T1c value %r -> %s' % (val, 'mode=1' if want_on else 'no LogAsync line'),
           rc == 0 and (got_on if want_on else got_off), 'rc=%d first=%r' % (rc, fa[:60]))

# T1d
t1 = child(T2X, OUT + '/t2_1.txt', '1')
t0 = child(T2X, OUT + '/t2_0.txt', '0')
member('T1d T2 =0 == mine =0 byte for byte', t0 == 0 and sha(OUT + '/t2_0.txt') == h['m0'])
for k in ('mu', 'm1'):
    a, b = OUT + '/t2_1.txt', OUT + '/' + k + '.txt'
    member('T1d T2 =1 vs mine %s: lines without LogAsync: equal' % k, t1 == 0 and without(a) == without(b))
    member('T1d T2 =1 vs mine %s: mode line equal' % k, first_async(a) == first_async(b), repr(first_async(b)[:80]))
    sa = [ln for ln in open(a, 'rb').read().decode('utf-8', 'replace').split('\n') if ln.startswith('LogAsync: full_waits')]
    sb = [ln for ln in open(b, 'rb').read().decode('utf-8', 'replace').split('\n') if ln.startswith('LogAsync: full_waits')]
    print('   summary T2 %r\n   summary %s %r; bytes equal %s' % (sa, k, sb, sha(a) == sha(b)))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
