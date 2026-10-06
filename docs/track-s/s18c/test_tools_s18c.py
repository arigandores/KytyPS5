"""S18c (HPP-644): fixtures of the S18c harness tools - go_s18c.sh refusals before the seal check on a temporary root (S18C_GO_ROOT): usage,
the order, the gate lines ACCUMULATION / SIGNATURE_571G3 (item 569 (d)(3), 571 (g)(3)), the input states, KYTY_S_REPLAY_TEST at the shipment
tags (item 576 (e)(3)), a made tag, RETURN_FAILED; aside_s18c.sh refusals and the one repeat; the derived copies of mk_s18c.py (only the root
differs from S17c2); the tag tables of go / launch / aside / reader agree; bash -n and ASCII of every script; no external timeout command in
go_s18c.sh.  Never takes the lock, never starts the game (every go call ends before the seal check).  ASCII only; ends with ALL OK.
usage: python test_tools_s18c.py"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

G = 'C:/kyty/s288/s18c'
S2 = 'C:/kyty/s288/s17c2'
BASH = 'C:/Program Files/Git/bin/bash.exe'
FILES = ('go_s18c.sh', 'launch_s18c.sh', 'wait_s18c.sh', 'post_s18c.sh', 'aside_s18c.sh', 's18c_read.py', 'enter_scene.py', 'guard_s18c.py',
         'mk_s18c.py', 'test_s18c_read.py', 'test_tools_s18c.py', 'mut_s18c_read.py', 'checkseal_s18c.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_s18c.py sha256 %s target go_s18c.sh sha256 %s aside_s18c.sh sha256 %s mk_s18c.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(G + '/go_s18c.sh'), sha(G + '/aside_s18c.sh'), sha(G + '/mk_s18c.py')))
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


def run(args, env_extra=None, drop=()):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_') or k in drop:
            env.pop(k)
    env.update(env_extra or {})
    p = subprocess.run([BASH] + args, capture_output=True, env=env)
    return p.returncode, (p.stdout + p.stderr).decode('ascii', 'replace')


TMP = G + '/fx_tools'
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
ok = True
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - the go fixtures would read exit 3; not run')
    sys.exit(1)


def root(name):
    r = TMP + '/' + name
    os.makedirs(os.path.join(r, 'runs'))
    os.makedirs(os.path.join(r, 'state'))
    return r


def mk_run(r, tag, lines=None):
    os.makedirs(os.path.join(r, 'runs', tag), exist_ok=True)
    if lines is not None:
        open(os.path.join(r, 'runs', tag, 'read.txt'), 'w', newline='\n').write(''.join('  %s\n' % x for x in lines) + '  READING MEMBERS_PASS\n')


def mk_replay(r, tag):
    os.makedirs(os.path.join(r, 'state', tag, 'replay'), exist_ok=True)
    open(os.path.join(r, 'state', tag, 'replay', 'replay.cur'), 'w').write('3\n')


def go(r, tag, env_extra=None):
    e = {'S18C_GO_ROOT': r.replace(chr(92), '/')}
    e.update(env_extra or {})
    return run([G + '/go_s18c.sh', tag], e)


r0 = root('r0')
rc, out = go(r0, 's18_c20')
ok &= check(rc == 2 and 'usage' in out, 'go: unknown tag s18_c20 -> rc 2 usage')
rc, out = go(r0, 'x')
ok &= check(rc == 2 and 'usage' in out, 'go: unknown tag x -> rc 2 usage')
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and 'order: s18_c02' in out, 'go: s18_c03 without runs/s18_c02 -> rc 2 order')
mk_run(r0, 's18_c02')
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and "gate: line 'ACCUMULATION s18_c02 OK'" in out, 'go: no read.txt of s18_c02 -> rc 2 gate')
mk_run(r0, 's18_c02', ['ACCUMULATION s18_c02 BREACH'])
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and 'gate:' in out, 'go: ACCUMULATION s18_c02 BREACH -> rc 2 gate (stop of the series)')
mk_run(r0, 's18_c02', ['ACCUMULATION s18_c02 UNDETERMINED'])
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and 'gate:' in out, 'go: ACCUMULATION s18_c02 UNDETERMINED -> rc 2 gate')
mk_run(r0, 's18_c02', ['ACCUMULATION s18_c02 OK x'])
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and 'gate:' in out, 'go: a line with a tail is not the whole gate line -> rc 2')
mk_run(r0, 's18_c02', ['ACCUMULATION s18_c02 OK'])
rc, out = go(r0, 's18_c03')
ok &= check(rc == 2 and 'input state cap_acc' in out, 'go: gate passed, no state/s18_c02/replay -> rc 2 input state')
mk_replay(r0, 's18_c02')
rc, out = go(r0, 's18_c03')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_c03 passes every check before the seal -> rc 1 no seal (never the lock)')
r0 = root('r0b')
mk_run(r0, 's18_c01', ['ACCUMULATION s18_c01 OK'])
rc, out = go(r0, 's18_c02')
ok &= check(rc == 2 and "SIGNATURE_571G3 s18_c01 OK" in out, 'go: s18_c02 needs SIGNATURE_571G3 s18_c01 OK as well -> rc 2')
mk_run(r0, 's18_c01', ['ACCUMULATION s18_c01 OK', 'SIGNATURE_571G3 s18_c01 OK'])
mk_replay(r0, 's18_c01')
rc, out = go(r0, 's18_c02')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_c02 with both lines -> rc 1 no seal')
rc, out = go(root('r0c'), 's18_c01')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_c01 has no gate and no input folder -> rc 1 no seal')
os.makedirs(os.path.join(r0, 'runs', 's18_c04'))
rc, out = go(r0, 's18_c04')
ok &= check(rc == 2 and 'exists' in out, 'go: runs/s18_c04 exists -> rc 2 a tag runs once')
os.makedirs(os.path.join(r0, 'state', 's18_c05'))
rc, out = go(r0, 's18_c05')
ok &= check(rc == 2 and 'state/s18_c05 exists' in out, 'go: state/s18_c05 exists -> rc 2')
# shipment tags
r1 = root('r1')
rc, out = go(r1, 's18_ks')
ok &= check(rc == 2 and 'order: s18_c19' in out, 'go: s18_ks without s18_c19 -> rc 2 order')
mk_run(r1, 's18_c19', ['ACCUMULATION s18_c19 BREACH'])
rc, out = go(r1, 's18_ks')
ok &= check(rc == 2 and "gate: line 'ACCUMULATION s18_c19 OK'" in out, 'go: s18_ks needs ACCUMULATION s18_c19 OK')
mk_run(r1, 's18_c19', ['ACCUMULATION s18_c19 OK'])
rc, out = go(r1, 's18_ks', {'KYTY_S_REPLAY_TEST': 'stop'})
ok &= check(rc == 2 and 'input state cat_full' in out and 'item 576' not in out, 's18_ks: KYTY_S_REPLAY_TEST in the caller is not refused')
mk_replay(r1, 's18_c19')
rc, out = go(r1, 's18_ks')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_ks with the gate and state/s18_c19/replay -> rc 1 no seal')
for t in ('s18_r', 's18_e1', 's18_e2', 's18_v', 's18_w'):
    rc, out = go(r1, t, {'KYTY_S_REPLAY_TEST': 'stop'})
    ok &= check(rc == 2 and 'item 576 (e)(3)' in out, 'go: %s with KYTY_S_REPLAY_TEST in the caller -> rc 2 refused (item 576 (e)(3))' % t)
    rc, out = go(r1, t, {'KYTY_S_REPLAY_TEST': ''})
    ok &= check(rc == 2 and 'item 576 (e)(3)' in out, 'go: %s with an empty KYTY_S_REPLAY_TEST -> rc 2 refused' % t)
mk_run(r1, 's18_ks', ['SIGNATURE_571G3 s18_ks BREACH'])
rc, out = go(r1, 's18_r')
ok &= check(rc == 2 and "gate: line 'SIGNATURE_571G3 s18_ks OK'" in out, 'go: s18_r needs SIGNATURE_571G3 s18_ks OK')
mk_run(r1, 's18_ks', ['SIGNATURE_571G3 s18_ks OK'])
rc, out = go(r1, 's18_r')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_r passes -> rc 1 no seal')
mk_run(r1, 's18_r')
rc, out = go(r1, 's18_e1')
ok &= check(rc == 2 and 'input state chain' in out, 'go: s18_e1 without state/s18_r/all -> rc 2 input state chain')
for d in ('_ShaderCache', 'GLCache'):
    os.makedirs(os.path.join(r1, 'state', 's18_r', 'all', d))
rc, out = go(r1, 's18_e1')
ok &= check(rc == 2 and 'input state chain' in out, 'go: s18_e1 without runs/s18_r/manifest_run.tsv -> rc 2')
open(os.path.join(r1, 'runs', 's18_r', 'manifest_run.tsv'), 'w').write('x\n')
rc, out = go(r1, 's18_e1')
ok &= check(rc == 1 and 'no seal' in out, 'go: s18_e1 with the chain state -> rc 1 no seal')
open(os.path.join(r1, 'RETURN_FAILED'), 'w').write('x\n')
rc, out = go(r1, 's18_e2')
ok &= check(rc == 1 and 'RETURN_FAILED' in out, 'go: RETURN_FAILED -> rc 1')
# aside
ra = root('ra')
rc, out = run([G + '/aside_s18c.sh', 's18_c07', 'rep'], {'S18C_ROOT': ra})
ok &= check(rc == 2 and 'no runs/s18_c07' in out, 'aside: no runs -> rc 2')
mk_run(ra, 's18_c07', [])
rc, out = run([G + '/aside_s18c.sh', 's18_c07', 'rep'], {'S18C_ROOT': ra})
ok &= check(rc == 2 and 'does not read NOT_ADMITTED' in out, 'aside: a MEMBERS_PASS tag is not set aside -> rc 2')
open(os.path.join(ra, 'runs', 's18_c07', 'read.txt'), 'w').write('  READING NOT_ADMITTED\n')
rc, out = run([G + '/aside_s18c.sh', 's18_c07', 'ed2'], {'S18C_ROOT': ra})
ok &= check(rc == 2 and 'usage' in out, 'aside: reason ed2 refused')
rc, out = run([G + '/aside_s18c.sh', 's18_c07', 'rep'], {'S18C_ROOT': ra})
ok &= check(rc == 0 and 'ASIDE OK s18_c07 rep' in out and not os.path.exists(os.path.join(ra, 'runs', 's18_c07')), 'aside: one repeat')
mk_run(ra, 's18_c07', [])
open(os.path.join(ra, 'runs', 's18_c07', 'read.txt'), 'w').write('  READING NOT_ADMITTED\n')
rc, out = run([G + '/aside_s18c.sh', 's18_c07', 'rep'], {'S18C_ROOT': ra})
ok &= check(rc == 6 and 'second interference' in out, 'aside: second interference -> rc 6 question to the lead')
rc, out = run([G + '/aside_s18c.sh', 's17c_r3b', 'rep'], {'S18C_ROOT': ra})
ok &= check(rc == 2 and 'usage' in out, 'aside: a tag of S17c2 refused')
rc, out = run([G + '/launch_s18c.sh', 's18_c20'])
ok &= check(rc == 2 and 'usage' in out, 'launch: unknown tag -> rc 2 before any check')
# tag tables agree
sys.path.insert(0, G)
import s18c_read  # noqa: E402
tags = list(s18c_read.ORDER)
for f in ('launch_s18c.sh', 'aside_s18c.sh'):
    t = open(os.path.join(G, f), encoding='ascii').read()
    m = re.search(r'case "\$T" in ([a-z0-9_|]+)\) ;;', t)
    ok &= check(m is not None and m.group(1).split('|') == tags, '%s: the tag table = the reader ORDER (25 tags)' % f)
gs = open(G + '/go_s18c.sh', encoding='ascii').read()
lv = re.search(r'LEVELS=\(([^)]*)\)', gs).group(1).split()
ok &= check(tuple(lv) == s18c_read.LEVELS, 'go_s18c.sh LEVELS = the reader LEVELS (19, in order)')
ok &= check('KV="KYTY_S_REPLAY=3 KYTY_FIX_F19=1 KYTY_AV_TRACE=1 KYTY_SHADER_SEED=0 KYTY_S_REPLAY_TEST=stop"' in gs and
            'CAPV="KYTY_S_REPLAY=2 KYTY_FIX_F19=0 KYTY_SHADER_SEED=0"' in gs and
            's18_r)  LV=$SKY; PREV=s18_ks;  IN=cat_full; FORM=p; KV="KYTY_SHADER_SEED=0"' in gs and
            's18_v)  LV=$SKY; PREV=s18_e2;  IN=inst_cat; FORM=v; H=330; KV="";;' in gs and
            's18_w)  LV=$SKY; PREV=s18_v;   IN=cat_full; FORM=w; H=310; KV=""' in gs and 's18_e2) LV=$MGG; PREV=s18_e1;  IN=chain;' in gs,
            'go_s18c.sh: forms of the tags = the seal (capture, stand, defaults)')
ok &= check('BIN_EXPECT=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' in gs and
            'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in gs and '--stable-draws 100' in gs,
            'go_s18c.sh: binary S18a2, installed FS8, stable 100')
ok &= check(not re.search(r'(^|[;&|(\s])timeout\s', gs.replace('--timeout ', '--TO ')), 'go_s18c.sh: no external timeout command')
# derived copies
for name, src, n_diff in (('enter_scene.py', 'enter_scene.py', 2), ('guard_s18c.py', 'guard_s17c2.py', 2)):
    a = open(os.path.join(S2, src), 'rb').read().decode('ascii').split('\n')
    b = open(os.path.join(G, name), 'rb').read().decode('ascii').split('\n')
    if name == 'guard_s18c.py':
        b = b[1:]
        n_diff = 1
    diff = [i for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
    ok &= check(len(a) == len(b) and len(diff) == n_diff and all('s18c' in b[i] for i in diff), '%s: differs from S17c2 only in %d root line(s)'
                % (name, n_diff))
for f in ('procload.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'run_safety99.py', 'sheet142.py', 'r_addr.py', 'tc_s17c.py',
          'state_s17c.py', 'gates_default.txt'):
    ok &= check(sha(os.path.join(G, f)) == sha(os.path.join(S2, f)), '%s: byte copy of S17c2' % f)
# bash -n, ASCII
for f in FILES:
    p = os.path.join(G, f)
    if not os.path.exists(p):
        ok &= check(False, '%s exists' % f)
        continue
    b = open(p, 'rb').read()
    ok &= check(all(c < 128 for c in b) and b'\r\n' not in b, '%s: ASCII, LF' % f)
    if f.endswith('.sh'):
        rc, out = run(['-n', p])
        ok &= check(rc == 0, '%s: bash -n' % f)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % N[0])
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
