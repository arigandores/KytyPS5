"""S18c2 (HPP-654): fixtures of the S18c2 harness tools - go_s18c2.sh refusals before the seal check on temporary roots (S18C2_GO_ROOT,
S18C2_GO_SRC): usage, KYTY_S_REPLAY_TEST in the caller (item 576 (e)(3)), a made tag, the catalogue replay_known against the manifest
c644e3ad (missing, a changed byte, an extra file; the real catalogue passes to the seal check), RETURN_FAILED; launch / idle / aside refusals
and the one repeat; the derived files = the output of mk_s18c2.py byte for byte; enter_scene.py and guard_s18c2.py differ from S18c only in
the root lines; byte copies of the helpers; the tag tables; the form of s18_w2 in go_s18c2.sh; no external timeout; bash -n, ASCII, LF.
Never takes the lock, never starts the game (every go call ends before the seal check).  ASCII only; ends with ALL OK.
usage: python test_tools_s18c2.py"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

G = 'C:/kyty/s288/s18c2'
S1 = 'C:/kyty/s288/s18c'
BASH = 'C:/Program Files/Git/bin/bash.exe'
DERIVED = ('go_s18c2.sh', 'launch_s18c2.sh', 'wait_s18c2.sh', 'post_s18c2.sh', 'aside_s18c2.sh', 'idle_s18c2.sh', 'enter_scene.py',
           'guard_s18c2.py')
COPIES = ('procload.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'run_safety99.py', 'state_s17c.py', 'gates_default.txt')
FILES = DERIVED + ('s18c2_read.py', 'mk_s18c2.py', 'test_s18c2_read.py', 'test_tools_s18c2.py', 'mut_s18c2_read.py', 'checkseal_s18c2.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_s18c2.py sha256 %s target go_s18c2.sh sha256 %s mk_s18c2.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(G + '/go_s18c2.sh'), sha(G + '/mk_s18c2.py')))
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


def run(args, env_extra=None):
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('KYTY_'):
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


def go(r, src, tag, env_extra=None):
    e = {'S18C2_GO_ROOT': r, 'S18C2_GO_SRC': src}
    e.update(env_extra or {})
    return run([G + '/go_s18c2.sh', tag], e)


def fake_src(name, files):
    s = TMP + '/' + name
    os.makedirs(s + '/replay_known')
    for n, b in files.items():
        open(s + '/replay_known/' + n, 'wb').write(b)
    return s


r0 = root('r0')
rc, out = go(r0, S1, 's18_w')
ok &= check(rc == 2 and 'usage: go_s18c2.sh s18_w2' in out, 'go: the S18c tag s18_w -> rc 2 usage')
rc, out = go(r0, S1, 'x')
ok &= check(rc == 2 and 'usage' in out, 'go: unknown tag x -> rc 2 usage')
rc, out = go(r0, S1, 's18_w2', {'KYTY_S_REPLAY_TEST': 'stop'})
ok &= check(rc == 2 and 'item 576 (e)(3)' in out, 'go: KYTY_S_REPLAY_TEST=stop in the caller -> rc 2 refused')
rc, out = go(r0, S1, 's18_w2', {'KYTY_S_REPLAY_TEST': ''})
ok &= check(rc == 2 and 'item 576 (e)(3)' in out, 'go: an empty KYTY_S_REPLAY_TEST in the caller -> rc 2 refused')
rc, out = go(r0, TMP + '/nosrc', 's18_w2')
ok &= check(rc == 2 and 'replay_known missing' in out, 'go: no replay_known -> rc 2')
src_bad = fake_src('srcbad', {'replay.45.bin': b'a', 'replay.46.bin': b'b', 'replay.cur': b'46\n'})
rc, out = go(r0, src_bad, 's18_w2')
ok &= check(rc == 2 and 'replay.45.bin sha256 differs from the manifest c644e3ad' in out, 'go: replay_known bytes differ -> rc 2')
src_x = fake_src('srcx', {'replay.45.bin': b'a', 'replay.46.bin': b'b', 'replay.cur': b'46\n', 'replay.47.bin': b'c'})
rc, out = go(r0, src_x, 's18_w2')
ok &= check(rc == 2 and 'differ from the manifest c644e3ad' in out, 'go: an extra file in replay_known -> rc 2')
src_m = fake_src('srcm', {'replay.45.bin': b'a', 'replay.cur': b'46\n'})
rc, out = go(r0, src_m, 's18_w2')
ok &= check(rc == 2 and 'differ from the manifest c644e3ad' in out, 'go: a file missing in replay_known -> rc 2')
src_c = TMP + '/srccopy'
shutil.copytree(S1 + '/replay_known', src_c + '/replay_known')
with open(src_c + '/replay_known/replay.cur', 'ab') as f:
    f.write(b' ')
rc, out = go(r0, src_c, 's18_w2')
ok &= check(rc == 2 and 'replay.cur sha256 differs' in out, 'go: one byte added to replay.cur of a copy of the real catalogue -> rc 2')
rc, out = go(r0, S1, 's18_w2')
ok &= check(rc == 1 and 'no seal' in out, 'go: the real catalogue passes every check before the seal -> rc 1 no seal (never the lock)')
os.makedirs(os.path.join(r0, 'runs', 's18_w2'))
rc, out = go(r0, S1, 's18_w2')
ok &= check(rc == 2 and 'exists' in out, 'go: runs/s18_w2 exists -> rc 2 a tag runs once')
r1 = root('r1')
os.makedirs(os.path.join(r1, 'state', 's18_w2'))
rc, out = go(r1, S1, 's18_w2')
ok &= check(rc == 2 and 'state/s18_w2 exists' in out, 'go: state/s18_w2 exists -> rc 2')
r2 = root('r2')
open(os.path.join(r2, 'RETURN_FAILED'), 'w').write('x\n')
rc, out = go(r2, S1, 's18_w2')
ok &= check(rc == 1 and 'RETURN_FAILED' in out, 'go: RETURN_FAILED -> rc 1')
# launch, idle, aside
for f in ('launch_s18c2.sh', 'idle_s18c2.sh'):
    rc, out = run([G + '/' + f, 's18_w'])
    ok &= check(rc == 2 and 'usage' in out, '%s: the S18c tag s18_w -> rc 2 usage before any check' % f)
ra = root('ra')
rc, out = run([G + '/aside_s18c2.sh', 's18_w2', 'rep'], {'S18C2_ROOT': ra})
ok &= check(rc == 2 and 'no runs/s18_w2' in out, 'aside: no runs -> rc 2')
os.makedirs(os.path.join(ra, 'runs', 's18_w2'))
open(os.path.join(ra, 'runs', 's18_w2', 'read.txt'), 'w').write('  READING MEMBERS_FAIL\n')
rc, out = run([G + '/aside_s18c2.sh', 's18_w2', 'rep'], {'S18C2_ROOT': ra})
ok &= check(rc == 2 and 'does not read NOT_ADMITTED' in out, 'aside: a MEMBERS_FAIL tag is not set aside -> rc 2')
open(os.path.join(ra, 'runs', 's18_w2', 'read.txt'), 'w').write('  READING NOT_ADMITTED\n')
rc, out = run([G + '/aside_s18c2.sh', 's18_w2', 'rep'], {'S18C2_ROOT': ra})
ok &= check(rc == 0 and 'ASIDE OK s18_w2 rep' in out and not os.path.exists(os.path.join(ra, 'runs', 's18_w2')), 'aside: one repeat')
os.makedirs(os.path.join(ra, 'runs', 's18_w2'))
open(os.path.join(ra, 'runs', 's18_w2', 'read.txt'), 'w').write('  READING NOT_ADMITTED\n')
rc, out = run([G + '/aside_s18c2.sh', 's18_w2', 'rep'], {'S18C2_ROOT': ra})
ok &= check(rc == 6 and 'second interference' in out, 'aside: second interference -> rc 6 question to the lead')
rc, out = run([G + '/aside_s18c2.sh', 's18_w', 'rep'], {'S18C2_ROOT': ra})
ok &= check(rc == 2 and 'usage' in out, 'aside: an S18c tag refused')
# tag tables, form
for f in ('launch_s18c2.sh', 'aside_s18c2.sh', 'idle_s18c2.sh'):
    t = open(os.path.join(G, f), encoding='ascii').read()
    m = re.search(r'case "\$T" in ([a-z0-9_|]+)\) ;;', t)
    ok &= check(m is not None and m.group(1) == 's18_w2', '%s: the tag table = s18_w2' % f)
gs = open(G + '/go_s18c2.sh', encoding='ascii').read()
ok &= check('  s18_w2) LV=$SKY; IN=cat_full; FORM=w; H=310; KV="KYTY_SHADER_SEED=0"; '
            'VK="VK_LAYER_PATH=$VKLAYER VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000";;' in gs and
            '  w) FA="--timeout 900 --emu-arg=--vulkan-validation --emu-arg=true --hold $H";;' in gs and 'SKY=underwater_aerial_garden' in gs,
            'go_s18c2.sh: the form of s18_w2 (Sky Garden, cat_full, w, 310 s, KYTY_SHADER_SEED=0, the layer limit 100000000)')
ok &= check('BIN_EXPECT=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' in gs and
            'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in gs and '--stable-draws 100' in gs and
            'SEAL=$G/pred/s18c2_seal.md' in gs and '"_ShaderSeeds=$EMU/_ShaderSeeds"' in gs and '"_ShaderCache=$EMU/_ShaderCache"' in gs,
            'go_s18c2.sh: binary S18a2, installed FS8, stable 100, the seal, the return manifest with _ShaderSeeds and _ShaderCache (replay/)')
ok &= check('cat_full) rm -rf "$F19" "$RP"; cp -a $SRCD "$RP"' in gs and 'SRCD=$SRCG/replay_known' in gs and 'KYTY_S_REPLAY=' not in gs.split(
    'case "$T" in\n  s18_w2)')[1].split('esac')[0], 'go_s18c2.sh: input cat_full from replay_known; no KYTY_S_REPLAY in the form')
ok &= check(not re.search(r'(^|[;&|(\s])timeout\s', gs.replace('--timeout ', '--TO ')), 'go_s18c2.sh: no external timeout command')
# derived files = mk_s18c2.py output
MK = TMP + '/mk/'
os.makedirs(MK)
p = subprocess.run([sys.executable, G + '/mk_s18c2.py', MK], capture_output=True)
ok &= check(p.returncode == 0, 'mk_s18c2.py runs')
for f in DERIVED + COPIES:
    ok &= check(os.path.exists(MK + f) and sha(MK + f) == sha(os.path.join(G, f)), '%s = the output of mk_s18c2.py byte for byte' % f)
for name, src in (('enter_scene.py', 'enter_scene.py'), ('guard_s18c2.py', 'guard_s18c.py')):
    a = open(os.path.join(S1, src), 'rb').read().decode('ascii').split('\n')
    b = open(os.path.join(G, name), 'rb').read().decode('ascii').split('\n')
    diff = [i for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
    ok &= check(len(a) == len(b) and len(diff) == 2 and all('s18c2' in b[i] for i in diff), '%s: differs from S18c only in 2 root lines' % name)
for f in COPIES:
    ok &= check(sha(os.path.join(G, f)) == sha(os.path.join(S1, f)), '%s: byte copy of S18c' % f)
# bash -n, ASCII, LF
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
