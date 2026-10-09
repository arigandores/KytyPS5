"""Fixtures of the F30f chain (Track F link F30f, HPP-711; ROADMAP s122 item 643 (d), item 649): the dry-run plan of go_f30f.sh for every
tag form (level, knob KYTY_RT_SKIP, hold, video, stable draws, the keys of S9 only), refusals of the tag names, the planner next_f30f.py
(order c3 -> c4 -> v, a dead or not admitted c3 drops the scene, interference waits for the lead, reserves v2 and intro_next, STOP, READ,
LIMIT, DONE), the copies of the F29e tools (unchanged or with the names moved), enter_scene.py = F29e + launch_sha256 only, post /
launch refusals, strict cp1250 output.  Not mutated (process tools).  ASCII only; ends with ALL OK.
usage: python test_tools_f30f.py"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
F29E = 'C:/kyty/f287/f29e'
BASH = 'C:/Program Files/Git/bin/bash.exe'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f30f.py sha256 %s target go_f30f.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_f30f.sh'))))
N = [0, 0]
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def bash(script, *args, env=None):
    e = dict(os.environ)
    e.update(env or {})
    r = subprocess.run([BASH, os.path.join(HERE, script)] + list(args), capture_output=True, env=e)
    return r.returncode, r.stdout.decode('ascii', 'replace')


# --- dry-run plans of go_f30f.sh ---
LV = {'s1': 'underwater_aerial_garden', 's2': 'hoover_beach', 's3': 'mini_giants_garden', 's4': 'timestop_casino',
      's5': 'rotating_level_day_and_night', 's6': 'sponge_dirty_bath', 's7': 'time_stopper_ghost_world', 's8': 'big_hand_pirate_island',
      's9': 'underwater_aerial_garden', 'in': 'intro_next'}
KEYS = open('C:/kyty/KytyPS5/docs/track-f/fs3c/keys_a2_presents.txt', encoding='ascii').read().strip()
for sc in LV:
    for kd in ('c3', 'c4', 'v'):
        for rep in ('', '_r2'):
            t = 'f30_%s_%s%s' % (sc, kd, rep)
            rc, out = bash('go_f30f.sh', t, env={'F30F_DRYRUN': '1'})
            want_rt = {'c3': '3', 'c4': '4', 'v': '2'}[kd]
            want_h = {'c3': '150', 'c4': '150', 'v': '300'}[kd]
            good = (rc == 0 and ('level %s ' % LV[sc]) in out and ('KYTY_RT_SKIP=%s ' % want_rt) in out and (' hold %s ' % want_h) in out
                    and (('rec --rec ' in out) == (kd == 'v')) and ((' sd 500 ' in out) == (sc == 'in')) and ((' sd 300 ' in out) == (sc != 'in'))
                    and (('KYTY_KEYS=' + KEYS) in out) == (sc == 's9') and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in out
                    and ' timeout 480 ' in out)
            ok &= check('dry-run %s: %s' % (t, out.strip()[:160]), good)
for sc in ('s6', 's7', 's8'):
    rc, out = bash('go_f30f.sh', 'f30_%s_v2' % sc, env={'F30F_DRYRUN': '1'})
    ok &= check('dry-run v2 %s' % sc, rc == 0 and 'KYTY_RT_SKIP=2 ' in out and 'rec --rec' in out and ' hold 300 ' in out)
for bad in ('f30_s1_v2', 'f30_s5_v2', 'f30_in_v2', 'f30_s0_c3', 'f30_s1_c5', 'f30_s1_c3_r4', 'b12_v', ''):
    rc, out = bash('go_f30f.sh', bad, env={'F30F_DRYRUN': '1'})
    ok &= check('go refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('launch_f30f.sh', bad)
    ok &= check('launch refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('post_f30f.sh', bad)
    ok &= check('post refuses %r rc 2' % bad, rc == 2)
lockf = os.path.join(HERE, 'fx_tools_lock.txt')
open(lockf, 'w').write('fixture lock\n')
rc, out = bash('post_f30f.sh', 'f30_s1_c3', env={'F30F_LOCK': lockf})
ok &= check('post refuses under a lock rc 3 (%s)' % out.strip()[:60], rc == 3)
os.remove(lockf)
go = open(os.path.join(HERE, 'go_f30f.sh'), encoding='ascii').read()
ok &= check('go: no cache copy or return (cp -a, mv before_) - item 643 (d)(1)', 'cp -a' not in go and 'before_$d' not in go)
ok &= check('go: T installed by full sha, FS10 returned from the pinned copy',
            'TB=3bc7ada7980a89fee30b17780f8dfbee0b3921332d81f1f63984d6252a811347' in go and
            'FS10=abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe' in go and 'cp "$PINNED" "$GAME"' in go)
ok &= check('go: lock by noclobber, lock.log lines, procload masked', 'set -o noclobber' in go and 'lock taken $T' in go
            and 'lock released $T' in go and '| mask >' in go)
ok &= check('go: KYTY_* and VK_LAYER_* unset before the call', "grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'" in go)
ok &= check('go: no validation, no RenderDoc, no checkpoints, no patch in the call',
            all(w not in go.split('F20E_PIDFILE=')[1] for w in ('--vulkan-validation', '--rd', 'KYTY_GPU_CHECKPOINTS', 'KYTY_GAME_PATCH')))

# --- the planner ---
spec = importlib.util.spec_from_file_location('next_f30f', os.path.join(HERE, 'next_f30f.py'))
NX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(NX)
FX = os.path.join(HERE, 'fx_tools')


def runs(tags):
    shutil.rmtree(FX, ignore_errors=True)
    rd = os.path.join(FX, 'runs')
    os.makedirs(rd)
    for t, r in tags.items():
        os.makedirs(os.path.join(rd, t))
        if r is not None:
            json.dump(r, open(os.path.join(rd, t, 'read.json'), 'w'))
    return rd


def R(status, *members):
    return dict(status=status, members=[['m', bool(x)] for x in members] if members else None)


GOOD3 = R('ADMITTED', 1, 1, 1)
DEAD3 = R('ADMITTED', 0, 1, 1)
GOOD4 = R('ADMITTED', 1, 1)
VNEW = R('ADMITTED', 1, 1, 1, 0)
VOLD = R('ADMITTED', 1, 1, 1, 1)
INT = R('INTERFERENCE')
NA = R('NOT_ADMITTED')


def full(upto, extra=None):
    d = {}
    for i in range(1, upto + 1):
        d.update({'f30_s%d_c3' % i: GOOD3, 'f30_s%d_c4' % i: GOOD4, 'f30_s%d_v' % i: VOLD})
    d.update(extra or {})
    return d


P = NX.plan
ok &= check('planner: empty - NEXT f30_s1_c3', P(runs({})) == 'NEXT f30_s1_c3')
ok &= check('planner: c3 made, no read - READ', P(runs({'f30_s1_c3': None})) == 'READ f30_s1_c3')
ok &= check('planner: c3 alive - NEXT c4', P(runs({'f30_s1_c3': GOOD3})) == 'NEXT f30_s1_c4')
ok &= check('planner: c4 WAITS_V - NEXT v', P(runs({'f30_s1_c3': GOOD3, 'f30_s1_c4': R('WAITS_V', 1, 1)})) == 'NEXT f30_s1_v')
ok &= check('planner: c4 NOT_ADMITTED - NEXT v (item 649 (v))', P(runs({'f30_s1_c3': GOOD3, 'f30_s1_c4': NA})) == 'NEXT f30_s1_v')
ok &= check('planner: c3 dead - the scene drops, NEXT s2 c3', P(runs({'f30_s1_c3': DEAD3})) == 'NEXT f30_s2_c3')
ok &= check('planner: c3 NOT_ADMITTED - the scene drops (item 649 (g))', P(runs({'f30_s1_c3': NA})) == 'NEXT f30_s2_c3')
ok &= check('planner: c3 INTERFERENCE - next scene', P(runs({'f30_s1_c3': INT})) == 'NEXT f30_s2_c3')
ok &= check('planner: repeat _r1 replaces the interfered c3', P(runs({'f30_s1_c3': INT, 'f30_s1_c3_r1': GOOD3})) == 'NEXT f30_s1_c4')
ok &= check('planner: s1..s5 done - NEXT s6 c3', P(runs(full(5))) == 'NEXT f30_s6_c3')
nine = full(9, {'f30_s6_v': VNEW})
ok &= check('planner: all 9, s6 v NEW - reserve v2 s6', P(runs(nine)) == 'NEXT f30_s6_v2')
nine['f30_s6_v2'] = VNEW
ok &= check('planner: v2 made - DONE (no second v2)', P(runs(nine)).startswith('DONE'))
ok &= check('planner: v NEW at s5 - no v2 (only s6..s8)', P(runs(full(9, {'f30_s5_v': VNEW}))).startswith('DONE'))
drop = full(9, {'f30_s4_c3': DEAD3})
del drop['f30_s4_c4'], drop['f30_s4_v']
ok &= check('planner: a dropped scene - reserve intro_next c3', P(runs(drop)) == 'NEXT f30_in_c3')
drop['f30_in_c3'] = GOOD3
ok &= check('planner: intro_next c4 next', P(runs(drop)) == 'NEXT f30_in_c4')
drop.update({'f30_in_c4': GOOD4, 'f30_in_v': VNEW})
ok &= check('planner: intro_next done - DONE with the dropped scene', P(runs(drop)) == 'DONE made 28 (dropped s4, v2 -)')
ok &= check('planner: interference left - WAIT', P(runs(full(9, {'f30_s3_v': INT}))).startswith('WAIT lead repeat item for f30_s3_v'))
d = runs({})
open(os.path.join(FX, 'SERIES_STOP'), 'w').write('x reason\n')
ok &= check('planner: SERIES_STOP - STOP', P(d).startswith('STOP SERIES_STOP: x reason'))
big = full(8)
big.update({'f30_s1_c4_r%d' % j: GOOD4 for j in (1, 2, 3)})
big.update({'f30_s2_c4_r%d' % j: GOOD4 for j in (1, 2, 3)})
big.update({'f30_s3_c4_r%d' % j: GOOD4 for j in (1, 2, 3)})
ok &= check('planner: 24 + 9 = 33 made - LIMIT before s9', P(runs(big)) == 'LIMIT 33 made tags')

# --- copies of the F29e tools ---
SAME = ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'launch_run.py', 'run_safety99.py', 'sheet142.py', 'gates_default.txt')
for f in SAME:
    ok &= check('copy unchanged %s' % f, sha(os.path.join(HERE, f)) == sha(os.path.join(F29E, f)))
for f in ('guard', 'hold', 'runchk', 'queue', 'tempo'):
    a = open(os.path.join(F29E, '%s_f29e.py' % f), encoding='utf-8').read()
    b = open(os.path.join(HERE, '%s_f30f.py' % f), encoding='utf-8').read().split('\n', 1)[1]
    a2 = a.replace('f29e', 'f30f').replace('F29E', 'F30F').replace('F29e', 'F30f').replace('HPP-704', 'HPP-711')
    ok &= check('copy %s_f30f.py = F29e with the names moved' % f, a2 == b)
a = open(os.path.join(F29E, 'enter_scene.py'), encoding='utf-8').read().replace('f29e', 'f30f').replace('F29E', 'F30F').replace('F29e', 'F30f').replace('HPP-704', 'HPP-711')
b = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
bl = b.split('\n')[2:]
extra = [l for l in bl if l not in a.split('\n')]
ok &= check('enter_scene.py = F29e + launch_sha256 only (%s)' % [l.strip()[:60] for l in extra], len(extra) == 3 and all('launch_sha256' in l or 'F30f (HPP-711, item 644' in l for l in extra))
for f, own in (('runchk_f30f.py', "OWN = 'HPP-711'"), ('queue_f30f.py', "OWN = 'HPP-711'")):
    ok &= check('%s own issue HPP-711' % f, own in open(os.path.join(HERE, f), encoding='utf-8').read())
ok &= check('runchk reads F30F_RUN_ID, launch passes it', "os.environ.get('F30F_RUN_ID'" in open(os.path.join(HERE, 'runchk_f30f.py'), encoding='utf-8').read()
            and 'F30F_RUN_ID="${PAPERCLIP_RUN_ID:-}"' in open(os.path.join(HERE, 'launch_f30f.sh'), encoding='ascii').read())
for f in ('launch_f30f.sh', 'wait_f30f.sh', 'chk_f30f.sh', 'post_f30f.sh', 'go_f30f.sh'):
    t = open(os.path.join(HERE, f), 'rb').read()
    code = b' '.join(l for l in t.split(b'\n') if not l.lstrip().startswith(b'#'))
    ok &= check('%s ASCII, LF, no f29e / HPP-704 / b12 names in the code lines' % f, all(c < 128 for c in t) and b'\r\n' not in t
                and b'f29e' not in code.lower() and b'HPP-704' not in code and b'b12_' not in code)

# --- strict cp1250 output of the planner ---
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        NX.main(['--runs', runs(full(2))])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check('planner output strict cp1250, ASCII (%r)' % raw.getvalue()[:60], cp_ok and all(c < 128 for c in raw.getvalue()) and raw.getvalue().startswith(b'NEXT f30_s3_c3'))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
