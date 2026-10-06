"""S17c2 (HPP-640): fixtures of the harness scripts of seal edition 4 that the reader suite does not cover - aside_s17c2.sh (the reason rep only:
refusals for a carried tag, an unknown reason, a missing run, an admitted tag, a running call; the move after NOT_ADMITTED; the second
interference of the same tag -> code 6), the derived files of mk_s17c2.py (enter_scene.py differs from the S17c file only by its root and
header; launch / wait / post name S17c2), go_s17c2.sh (tags, order, KYTY_SHADER_SEED=0 in every KV, the S-replay manifests, _ShaderSeeds in the
cache manifest, binary 43ef1cc1), and ASCII only of every harness file.  The first output line names the suite and the targets with sha256;
the output ends with ALL OK.  ASCII only.
usage: python test_tools_s17c2.py"""
import hashlib
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ED3 = 'C:/kyty/s288/s17c'
FILES = ('aside_s17c2.sh', 'go_s17c2.sh', 'launch_s17c2.sh', 'wait_s17c2.sh', 'post_s17c2.sh', 'enter_scene.py', 'guard_s17c2.py',
         'mk_s17c2.py', 's17c2_read.py', 'test_s17c2_read.py', 'mut_s17c2_read.py', 'checkseal_s17c2.py', 'test_tools_s17c2.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_s17c2.py sha256 %s targets %s' % (sha(os.path.abspath(__file__)), ' '.join(
    '%s sha256 %s' % (f, sha(os.path.join(HERE, f))) for f in FILES[:9])))
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


ok = True
BASH = shutil.which('bash') or 'C:/Program Files/Git/bin/bash.exe'
FX = os.path.join(HERE, 'fx_tools')
shutil.rmtree(FX, ignore_errors=True)
os.makedirs(FX)


def aside(tag, why, root):
    env = dict(os.environ, S17C2_ROOT=root.replace(chr(92), '/'))
    p = subprocess.run([BASH, os.path.join(HERE, 'aside_s17c2.sh'), tag, why], capture_output=True, env=env)
    return p.returncode, p.stdout.decode('ascii', 'replace')


def mkroot(name, read_word='NOT_ADMITTED', sha_line='43ef1cc1'):
    r = os.path.join(FX, name)
    os.makedirs(os.path.join(r, 'runs', 's17c_ks2'))
    os.makedirs(os.path.join(r, 'state', 's17c_ks2'))
    open(os.path.join(r, 'runs', 's17c_ks2', 'read.txt'), 'w').write('  READING %s\n' % read_word)
    open(os.path.join(r, 'runs', 's17c_ks2', 'installed_sha.txt'), 'w').write(sha_line + '\n')
    for f in ('log_s17c_ks2.txt', 's17c_ks2.json', 'go_s17c_ks2.out.txt'):
        open(os.path.join(r, f), 'w').write('x\nrc=0\n')
    return r


r = mkroot('a1')
rc, out = aside('s17c_c2', 'rep', r)
ok &= check(rc == 2 and 'carried from edition 3' in out, 'aside refuses a carried edition 3 tag')
rc, out = aside('s17c_ks2', 'ed2', r)
ok &= check(rc == 2 and 'usage' in out, 'aside refuses the reason ed2 (edition 4: rep only)')
rc, out = aside('s17c_kn2', 'rep', r)
ok &= check(rc == 2 and 'no runs/s17c_kn2' in out, 'aside refuses a tag without a run')
rc, out = aside('s17c_xx', 'rep', r)
ok &= check(rc == 2 and 'usage' in out, 'aside refuses an unknown tag')
r2 = mkroot('a2', read_word='MEMBERS_PASS')
rc, out = aside('s17c_ks2', 'rep', r2)
ok &= check(rc == 2 and 'NOT_ADMITTED' in out and os.path.isdir(os.path.join(r2, 'runs', 's17c_ks2')), 'aside refuses an admitted tag')
r3 = mkroot('a3')
open(os.path.join(r3, 'go_s17c_ks2.out.txt'), 'w').write('running\n')
rc, out = aside('s17c_ks2', 'rep', r3)
ok &= check(rc == 2 and 'no rc line' in out, 'aside refuses while the call has no rc line')
rc, out = aside('s17c_ks2', 'rep', r)
ok &= check(rc == 0 and 'ASIDE OK s17c_ks2 rep' in out and not os.path.exists(os.path.join(r, 'runs', 's17c_ks2')) and
            not os.path.exists(os.path.join(r, 'state', 's17c_ks2')) and not os.path.exists(os.path.join(r, 'log_s17c_ks2.txt')),
            'aside rep after NOT_ADMITTED moves runs, state and the files')
moved = [d for d in os.listdir(os.path.join(r, 'runs')) if d.startswith('s17c_ks2.rep_')]
ok &= check(len(moved) == 1, 'aside keeps the run as runs/<tag>.rep_<UTC>')
os.makedirs(os.path.join(r, 'runs', 's17c_ks2'))
open(os.path.join(r, 'runs', 's17c_ks2', 'read.txt'), 'w').write('  READING NOT_ADMITTED\n')
rc, out = aside('s17c_ks2', 'rep', r)
ok &= check(rc == 6 and 'second interference' in out, 'aside: the second interference of the same tag -> code 6 (question to the lead)')

# derived files
e3 = open(os.path.join(ED3, 'enter_scene.py'), 'rb').read().decode('ascii')
e4 = open(os.path.join(HERE, 'enter_scene.py'), 'rb').read().decode('ascii')
ok &= check(e4.split('\n', 1)[1].replace("ROOT = pathlib.Path('C:/kyty/s288/s17c2')", "ROOT = pathlib.Path('C:/kyty/s288/s17c')") == e3,
            'enter_scene.py = the S17c file except the header line and ROOT')
g3 = open(os.path.join(ED3, 'guard_s17c.py'), 'rb').read().decode('ascii')
g4 = open(os.path.join(HERE, 'guard_s17c2.py'), 'rb').read().decode('ascii')
ok &= check(g4.split('\n', 1)[1].replace("G = 'C:/kyty/s288/s17c2'", "G = 'C:/kyty/s288/s17c'") == g3.split('\n', 1)[1],
            'guard_s17c2.py = guard_s17c.py except the first docstring line and G')
for f in ('procload.py', 'idle142.py', 'launch_run.py', 'manifest_fs4c.py', 'run_safety99.py', 'sheet142.py', 'gates_default.txt', 'tc_s17c.py',
          'r_addr.py', 'state_s17c.py'):
    ok &= check(sha(os.path.join(HERE, f)) == sha(os.path.join(ED3, f)), 'verbatim copy of the S17c file %s' % f)
la = open(os.path.join(HERE, 'launch_s17c2.sh')).read()
ok &= check('go_s17c.sh' not in la and 'guard_s17c.py' not in la and 'G=C:/kyty/s288/s17c2' in la and
            's17c_r3b|s17c_rsb|s17c_ks2|s17c_kn2|s17c_c2h|s17c_n0h|s17c_r3h|s17c_e3h) ;;' in la, 'launch_s17c2.sh names S17c2 and its tags')
po = open(os.path.join(HERE, 'post_s17c2.sh')).read()
ok &= check('s17c2_read.py $T --json' in po and 's17c_c2h|s17c_n0h|s17c_e3h)' in po and 'G=C:/kyty/s288/s17c2' in po,
            'post_s17c2.sh reads with s17c2_read.py, video for the three v tags')
wa = open(os.path.join(HERE, 'wait_s17c2.sh')).read()
ok &= check('F=C:/kyty/s288/s17c2/go_$T.out.txt' in wa, 'wait_s17c2.sh waits for the S17c2 output')
go = open(os.path.join(HERE, 'go_s17c2.sh')).read()
kv = [ln for ln in go.split('\n') if ln.startswith('  s17c_') and 'KV=' in ln]
ok &= check(len(kv) == 8 and all('KYTY_SHADER_SEED=0' in ln or 'KV="$R3' in ln for ln in kv) and
            'R3="KYTY_S_REPLAY=3 KYTY_FIX_F19=1 KYTY_AV_TRACE=1 KYTY_SHADER_SEED=0"' in go, 'go_s17c2.sh: KYTY_SHADER_SEED=0 in every KV')
ok &= check([ln.split(')')[0].strip() for ln in kv] == ['s17c_r3b', 's17c_rsb', 's17c_ks2', 's17c_kn2', 's17c_c2h', 's17c_n0h', 's17c_r3h',
                                                         's17c_e3h'], 'go_s17c2.sh: the eight tags in order')
ok &= check('PREV=s17c_r3b' in kv[1] and 'PREV=s17c_rsb' in kv[2] and 'PREV=s17c_ks2' in kv[3] and 'PREV=s17c_kn2' in kv[4] and
            'PREV=s17c_c2h' in kv[5] and 'PREV=s17c_n0h' in kv[6] and 'PREV=s17c_r3h' in kv[7] and 'PREV' not in kv[0],
            'go_s17c2.sh: order by PREV')
ok &= check('BIN_EXPECT=43ef1cc14ec2c116fdcce9ac71f9d854d0ec6498bd6e538fa479b1ecdf57fbb3' in go and
            'BIN=C:/kyty/s288/bin/kyty_emulator_43ef1cc1.exe' in go and 'FS8=2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b' in go,
            'go_s17c2.sh: binary S17a5, installed FS8')
ok &= check('"_ShaderSeeds=$EMU/_ShaderSeeds")' in go and 'mf_in.tsv "f19=$F19" "replay=$RP"' in go and
            'mf_out.tsv "f19=$F19" "replay=$RP"' in go, 'go_s17c2.sh: _ShaderSeeds in the cache manifest; S-replay manifests in and out')
ok &= check('cat_c2) SRCD=$E3/state/s17c_c2;;' in go and 'k_ks2) SRCD=$G/state/s17c_ks2;;' in go and 'cat_c2h) SRCD=$G/state/s17c_c2h;;' in go
            and 'rb_r3h) SRCD=$G/state/s17c_r3h;;' in go, 'go_s17c2.sh: sources of the input states')
ok &= check('timeout' not in go.replace('--timeout', ''), 'go_s17c2.sh: no external timeout around the tag')
for f in FILES + ('state_s17c.py', 'tc_s17c.py', 'r_addr.py', 'procload.py', 'manifest_fs4c.py'):
    p = os.path.join(HERE, f)
    ok &= check(os.path.exists(p) and all(b < 128 for b in open(p, 'rb').read()), 'ASCII only: %s' % f)
for f in ('go_s17c2.sh', 'launch_s17c2.sh', 'wait_s17c2.sh', 'post_s17c2.sh', 'aside_s17c2.sh'):
    p = subprocess.run([BASH, '-n', os.path.join(HERE, f)], capture_output=True)
    ok &= check(p.returncode == 0, 'bash -n %s' % f)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
