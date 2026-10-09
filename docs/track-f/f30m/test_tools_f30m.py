"""Fixtures of the F30m chain (Track F link F30m, HPP-723; ROADMAP s122 item 655 (e)): the dry-run plan of go_f30m.sh for every tag form
(level, knob KYTY_RT_SKIP 5 / 2 / 3 / 4, hold, video only at cy_v, stable draws 300, the keys of S9 only), refusals of the tag names (the F30f
names included), the planner next_f30m.py (s1..s9 c5, then cy_v -> (gamma) -> cy_c3 -> (K) -> cy_c4, interference waits for the lead,
STOP, READ, LIMIT 12, BUDGET 7200 s, DONE), the copies of the F30f tools (unchanged or with the names moved), the binaries of go_f30m.sh (T2
installed, FS11 returned), post / launch refusals, strict cp1250 output.  Not mutated (process tools).  ASCII only; ends with ALL OK.
usage: python test_tools_f30m.py"""
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
F30F = 'C:/kyty/f287/f30f'
BASH = 'C:/Program Files/Git/bin/bash.exe'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f30m.py sha256 %s target go_f30m.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_f30m.sh'))))
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


# --- dry-run plans of go_f30m.sh ---
LV = {'s1': 'underwater_aerial_garden', 's2': 'hoover_beach', 's3': 'mini_giants_garden', 's4': 'timestop_casino',
      's5': 'rotating_level_day_and_night', 's6': 'sponge_dirty_bath', 's7': 'time_stopper_ghost_world', 's8': 'big_hand_pirate_island',
      's9': 'underwater_aerial_garden', 'cy': 'cymbal_party_land'}
KEYS = open('C:/kyty/KytyPS5/docs/track-f/fs3c/keys_a2_presents.txt', encoding='ascii').read().strip()
FORMS = [('s%d' % i, 'c5') for i in range(1, 10)] + [('cy', 'v'), ('cy', 'c3'), ('cy', 'c4')]
for sc, kd in FORMS:
    for rep in ('', '_r2'):
        t = 'f30_%s_%s%s' % (sc, kd, rep)
        rc, out = bash('go_f30m.sh', t, env={'F30M_DRYRUN': '1'})
        want_rt = {'c5': '5', 'c3': '3', 'c4': '4', 'v': '2'}[kd]
        want_h = {'c5': '150', 'c3': '150', 'c4': '150', 'v': '300'}[kd]
        good = (rc == 0 and ('level %s ' % LV[sc]) in out and ('KYTY_RT_SKIP=%s ' % want_rt) in out and (' hold %s ' % want_h) in out
                and (('rec --rec ' in out) == (kd == 'v')) and ' sd 300 ' in out
                and (('KYTY_KEYS=' + KEYS) in out) == (sc == 's9') and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in out
                and ' timeout 480 ' in out)
        ok &= check('dry-run %s: %s' % (t, out.strip()[:160]), good)
for bad in ('f30_s1_c3', 'f30_s1_c4', 'f30_s1_v', 'f30_s6_v2', 'f30_in_c3', 'f30_s0_c5', 'f30_cy_c5', 'f30_cy_v2', 'f30_s1_c5_r4', 'b12_v', ''):
    rc, out = bash('go_f30m.sh', bad, env={'F30M_DRYRUN': '1'})
    ok &= check('go refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('launch_f30m.sh', bad)
    ok &= check('launch refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('post_f30m.sh', bad)
    ok &= check('post refuses %r rc 2' % bad, rc == 2)
lockf = os.path.join(HERE, 'fx_tools_lock.txt')
open(lockf, 'w').write('fixture lock\n')
rc, out = bash('post_f30m.sh', 'f30_s1_c5', env={'F30M_LOCK': lockf})
ok &= check('post refuses under a lock rc 3 (%s)' % out.strip()[:60], rc == 3)
os.remove(lockf)
go = open(os.path.join(HERE, 'go_f30m.sh'), encoding='ascii').read()
ok &= check('go: no cache copy or return (cp -a, mv before_)', 'cp -a' not in go and 'before_$d' not in go)
ok &= check('go: T2 installed by full sha from its pinned copy, FS11 returned from the pinned copy',
            'TB=bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163' in go and
            'BIN=$F/bin/kyty_emulator_bba692c6.exe' in go and 'PINNED=$F/bin/kyty_emulator_ea51ae80.exe' in go and
            'FS11=ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce' in go and 'cp "$PINNED" "$GAME"' in go
            and 'cp "$BIN" "$GAME"' in go)
ok &= check('go: the pinned copies have the named sha256', sha('C:/kyty/f287/bin/kyty_emulator_bba692c6.exe') ==
            'bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163' and sha('C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe') ==
            'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce')
ok &= check('go: no FS10 / T sha in the code', 'abfded5e' not in go and '3bc7ada7' not in go)
ok &= check('go: lock by noclobber, lock.log lines, procload masked', 'set -o noclobber' in go and 'lock taken $T' in go
            and 'lock released $T' in go and '| mask >' in go)
ok &= check('go: KYTY_* and VK_LAYER_* unset before the call', "grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'" in go)
ok &= check('go: no validation, no RenderDoc, no checkpoints, no patch in the call',
            all(w not in go.split('F20E_PIDFILE=')[1] for w in ('--vulkan-validation', '--rd', 'KYTY_GPU_CHECKPOINTS', 'KYTY_GAME_PATCH')))
ok &= check('go: seal f30m_seal.md, lock text F30m HPP-723', 'SEAL=$G/pred/f30m_seal.md' in go and 'F30m HPP-723 go_f30m.sh' in go)

# --- the planner ---
spec = importlib.util.spec_from_file_location('next_f30m', os.path.join(HERE, 'next_f30m.py'))
NX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(NX)
FX = os.path.join(HERE, 'fx_tools')


def runs(tags, lock=None):
    shutil.rmtree(FX, ignore_errors=True)
    rd = os.path.join(FX, 'runs')
    os.makedirs(rd)
    for t, r in tags.items():
        os.makedirs(os.path.join(rd, t))
        if r is not None:
            json.dump(r, open(os.path.join(rd, t, 'read.json'), 'w'))
    if lock is not None:
        open(os.path.join(rd, 'lock.log'), 'w').write(lock)
    return rd


def R(status, *members):
    return dict(status=status, members=[['m', bool(x)] for x in members] if members else None)


C5 = R('ADMITTED', 1, 1, 0, 0, 0, 0, 0, 0)
C5D = R('ADMITTED', 0, 0, 0, 0, 0, 0, 0, 0)
VG = R('ADMITTED', 1, 1, 1, 1, 0)
VNG = R('ADMITTED', 0, 1, 1, 1, 0)
K3 = R('ADMITTED', 1, 1, 1)
K3D = R('ADMITTED', 0, 1, 1)
C4 = R('ADMITTED', 1, 0, 0, 0, 0, 0, 0, 0)
INT = R('INTERFERENCE')
NA = R('NOT_ADMITTED')


def eps(upto, extra=None):
    d = dict(('f30_s%d_c5' % i, C5) for i in range(1, upto + 1))
    d.update(extra or {})
    return d


P = NX.plan
ok &= check('planner: empty - NEXT f30_s1_c5', P(runs({})) == 'NEXT f30_s1_c5')
ok &= check('planner: made, no read - READ', P(runs({'f30_s1_c5': None})) == 'READ f30_s1_c5')
ok &= check('planner: s1 done - NEXT s2', P(runs(eps(1))) == 'NEXT f30_s2_c5')
ok &= check('planner: c5 dead K_B - the series goes on', P(runs(eps(1, {'f30_s1_c5': C5D}))) == 'NEXT f30_s2_c5')
ok &= check('planner: c5 NOT_ADMITTED - the series goes on', P(runs(eps(1, {'f30_s1_c5': NA}))) == 'NEXT f30_s2_c5')
ok &= check('planner: c5 INTERFERENCE - next scene', P(runs({'f30_s1_c5': INT})) == 'NEXT f30_s2_c5')
ok &= check('planner: repeat _r1 replaces the interfered c5', P(runs(eps(9, {'f30_s1_c5': INT, 'f30_s1_c5_r1': C5}))) == 'NEXT f30_cy_v')
ok &= check('planner: s1..s9 done - NEXT f30_cy_v', P(runs(eps(9))) == 'NEXT f30_cy_v')
ok &= check('planner: cy_v (gamma) YES - NEXT cy_c3', P(runs(eps(9, {'f30_cy_v': VG}))) == 'NEXT f30_cy_c3')
r = P(runs(eps(9, {'f30_cy_v': VNG})))
ok &= check('planner: cy_v (gamma) NO - DONE, c3/c4 not made (%s)' % r, r.startswith('DONE made 10') and '(gamma) not reachable' in r)
r = P(runs(eps(9, {'f30_cy_v': NA})))
ok &= check('planner: cy_v NOT_ADMITTED - DONE, c3/c4 not made (%s)' % r, r.startswith('DONE') and 'cy_v NOT_ADMITTED' in r)
ok &= check('planner: cy_v INTERFERENCE - WAIT', P(runs(eps(9, {'f30_cy_v': INT}))).startswith('WAIT lead repeat item for f30_cy_v'))
ok &= check('planner: cy_c3 (K) YES - NEXT cy_c4', P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': K3}))) == 'NEXT f30_cy_c4')
ok &= check('planner: cy_c3 (K) NO - still NEXT cy_c4 (letter of item 655 (e)(3))', P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': K3D}))) == 'NEXT f30_cy_c4')
ok &= check('planner: cy_c3 NOT_ADMITTED - NEXT cy_c4', P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': NA}))) == 'NEXT f30_cy_c4')
r = P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': K3D, 'f30_cy_c4': C4})))
ok &= check('planner: cy_c3 (K) NO, c4 made - DONE with the note cy not counted (%s)' % r, r.startswith('DONE made 12') and 'cy not counted' in r)
ok &= check('planner: cy_c3 INTERFERENCE - WAIT', P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': INT}))).startswith('WAIT lead repeat item for f30_cy_c3'))
r = P(runs(eps(9, {'f30_cy_v': VG, 'f30_cy_c3': K3, 'f30_cy_c4': C4})))
ok &= check('planner: all 12 - DONE made 12 (%s)' % r, r.startswith('DONE made 12'))
ok &= check('planner: interference at s3 left after all - WAIT', P(runs(eps(9, {'f30_s3_c5': INT, 'f30_cy_v': VNG}))).startswith('WAIT lead repeat item for f30_s3_c5'))
d = runs({})
open(os.path.join(FX, 'SERIES_STOP'), 'w').write('x reason\n')
ok &= check('planner: SERIES_STOP - STOP', P(d).startswith('STOP SERIES_STOP: x reason'))
d = runs({})
open(os.path.join(FX, 'RETURN_FAILED'), 'w').write('t\n')
ok &= check('planner: RETURN_FAILED - STOP', P(d).startswith('STOP RETURN_FAILED'))
lim = eps(9, {'f30_s1_c5_r1': C5, 'f30_s2_c5_r1': C5, 'f30_s3_c5_r1': C5})
ok &= check('planner: 12 made non-interference - LIMIT before cy_v', P(runs(lim)) == 'LIMIT 12 made tags')


def locklog(pairs):
    out = []
    for t, a, b in pairs:
        out += ['lock taken %s 2026-10-09T%s' % (t, a), 'lock released %s 2026-10-09T%s' % (t, b)]
    return '\n'.join(out) + '\n'


ok &= check('planner: lock seconds of the pairs', NX.lock_seconds(runs({}, locklog([('a', '10:00:00Z', '10:05:00Z'), ('b', '11:00:00Z', '11:00:30Z')]))) == 330)
ok &= check('planner: an open pair counts nothing', NX.lock_seconds(runs({}, 'lock taken a 2026-10-09T10:00:00Z\n')) == 0)
r = P(runs(eps(8), locklog([('a', '10:00:00Z', '11:55:01Z')])))
ok &= check('planner: lock 6901 s + 300 > 7200 - BUDGET (%s)' % r, r.startswith('BUDGET lock 6901 s'))
r = P(runs(eps(8), locklog([('a', '10:00:00Z', '11:55:00Z')])))
ok &= check('planner: lock 6900 s + 300 = 7200 - NEXT s9 (%s)' % r, r == 'NEXT f30_s9_c5')
r = P(runs(eps(9), locklog([('a', '10:00:00Z', '11:52:31Z')])))
ok &= check('planner: lock 6751 + 450 > 7200 at cy_v - BUDGET (%s)' % r, r.startswith('BUDGET') and 'f30_cy_v' in r)

# --- copies of the F30f tools ---
SAME = ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'launch_run.py', 'run_safety99.py', 'sheet142.py', 'gates_default.txt',
        'kref_f30m.tsv')
for f in SAME:
    ok &= check('copy unchanged %s' % f, sha(os.path.join(HERE, f)) == sha(os.path.join(F30F, f.replace('f30m', 'f30f'))))


def moved(text):
    import re
    t = text.replace('f287/f30f', 'f287/f30m').replace('F30F_', 'F30M_').replace('HPP-711', 'HPP-723')
    return re.sub(r'_f30f\b', '_f30m', t).replace('_f30f.', '_f30m.')


for f in ('guard', 'hold', 'runchk', 'queue', 'tempo', 'kref'):
    a = open(os.path.join(F30F, '%s_f30f.py' % f), encoding='utf-8').read()
    b = open(os.path.join(HERE, '%s_f30m.py' % f), encoding='utf-8').read()
    ok &= check('copy %s_f30m.py = F30f with the names moved, one header line' % f, b.startswith('# Track F link F30m (HPP-723;') and
                b.split('\n', 1)[1] == moved(a))
a = open(os.path.join(F30F, 'enter_scene.py'), encoding='utf-8').read()
b = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene.py = F30f with the names moved, one header line', b.split('\n', 1)[1] == moved(a)
            and "ROOT = pathlib.Path('C:/kyty/f287/f30m')" in b)
for f, own in (('runchk_f30m.py', "OWN = 'HPP-723'"), ('queue_f30m.py', "OWN = 'HPP-723'")):
    ok &= check('%s own issue HPP-723' % f, own in open(os.path.join(HERE, f), encoding='utf-8').read())
ok &= check('runchk reads F30M_RUN_ID, launch passes it', "os.environ.get('F30M_RUN_ID'" in open(os.path.join(HERE, 'runchk_f30m.py'), encoding='utf-8').read()
            and 'F30M_RUN_ID="${PAPERCLIP_RUN_ID:-}"' in open(os.path.join(HERE, 'launch_f30m.sh'), encoding='ascii').read())
ok &= check('chk_f30m.sh reads the comments of HPP-723', '/api/issues/HPP-723/comments' in open(os.path.join(HERE, 'chk_f30m.sh'), encoding='ascii').read())
for f in ('launch_f30m.sh', 'wait_f30m.sh', 'chk_f30m.sh', 'post_f30m.sh', 'go_f30m.sh'):
    t = open(os.path.join(HERE, f), 'rb').read()
    code = b' '.join(l for l in t.split(b'\n') if not l.lstrip().startswith(b'#'))
    ok &= check('%s ASCII, LF, no f30f / HPP-711 / F30F_ names in the code lines' % f, all(c < 128 for c in t) and b'\r\n' not in t
                and b'f30f' not in code.lower() and b'HPP-711' not in code and b'F30F_' not in code)

# --- item 660 (d)(4), 661 (b): the form of item 634 in launch_f30m.sh and go_f30m.sh ---
import re
import subprocess
LINTER = 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py'
LINT_LINE = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f30m || exit 10'


def code_of(f):
    return [(n, l.strip()) for n, l in enumerate(open(os.path.join(HERE, f), encoding='ascii').read().split('\n'), 1)
            if l.strip() and not l.strip().startswith('#')]


for f in ('launch_f30m.sh', 'go_f30m.sh'):
    cl = code_of(f)
    ok &= check('p661: %s first executable line is the linter with exit 10 (%s)' % (f, cl[0][1][:70]), cl[0][1] == LINT_LINE)
    ok &= check('p660: %s has no block logic (guard_block, open-block, guard status/tag/close)' % f,
                not any(re.search(r'guard_block|open-block|guard_\w*\.py\s+(status|tag|close|open-block)\b', s) for _, s in cl))
lc = code_of('launch_f30m.sh')
ok &= check('p660 (d)(1): launch has no guard_*.py / hold_*.py call', not any(re.search(r'guard_\w*\.py|hold_\w*\.py', s) for _, s in lc))
ok &= check('p660 (d)(1): launch keeps the display, the queue and the launch', any('dispstate.py' in s for _, s in lc)
            and any('queue_f30m.py' in s for _, s in lc) and any('nohup bash -c "bash $G/go_f30m.sh $T' in s for _, s in lc))
gc = code_of('go_f30m.sh')
lock_n = next(n for n, s in gc if 'lock taken $T' in s)
man_n = next(n for n, s in gc if n > lock_n and 'manifest_fs4c.py' in s)
scans = [n for n, s in gc if re.search(r'guard_\w*\.py\s+scan\b(?!.*--pidfile)', s)]
holds = [n for n, s in gc if re.search(r'hold_\w*\.py\s+check\b', s)]
ok &= check('p660 (d)(2): go has no guard / hold check before the lock line %d' % lock_n,
            not any(n < lock_n for n in scans + holds))
ok &= check('p660 (d)(2): go has ONE guard scan and ONE hold check, after the lock %d and before the manifest %d (%s / %s)'
            % (lock_n, man_n, scans, holds), len(scans) == 1 and len(holds) == 1 and lock_n < scans[0] < man_n and lock_n < holds[0] < man_n)
ok &= check('p660 (d)(3): go keeps procload, the watch during the tag, kill-own by pid, the FS11 return',
            any('procload.py' in s for _, s in gc) and any('hold_f30m.py watch' in s or 'guard_f30m.py watch' in s for _, s in gc)
            and any('kill-own --pidfile' in s for _, s in gc) and 'cp "$PINNED" "$GAME"' in go)
r = subprocess.run([sys.executable, LINTER, '--series', HERE], capture_output=True, text=True)
ok &= check('p661: linter --series f30m rc 0, last line ALL OK (%s)' % r.stdout.strip().split('\n')[-1], r.returncode == 0 and r.stdout.strip().split('\n')[-1] == 'ALL OK')
BADD = os.path.join(HERE, 'fx_p660_bad')
shutil.rmtree(BADD, ignore_errors=True)
os.makedirs(BADD)
for f in ('launch_f30m.sh', 'go_f30m.sh'):
    shutil.copy2(os.path.join(HERE, 'old', 'p660', f), os.path.join(BADD, f))
r = subprocess.run([sys.executable, LINTER, '--series', BADD], capture_output=True, text=True)
ok &= check('p661 negative: linter on the pre-660 scripts rc 1, FORM634 FAILED (%s)' % r.stdout.strip().split('\n')[-1],
            r.returncode != 0 and 'FORM634 FAILED' in r.stdout)
lt = open(os.path.join(HERE, 'launch_f30m.sh'), encoding='ascii').read().replace('--series C:/kyty/f287/f30m', '--series ' + BADD.replace('\\', '/'))
open(os.path.join(BADD, 'launch_bad.sh'), 'w', encoding='ascii', newline='\n').write(lt)
tmf = os.path.join(BADD, 'times.txt')
r = subprocess.run([BASH, os.path.join(BADD, 'launch_bad.sh').replace('\\', '/'), 'f30_s7_c5'], capture_output=True, text=True,
                   env=dict(os.environ, F30M_TIMES=tmf.replace('\\', '/'), F30M_DRYRUN='2', F30M_DISP_SKIP='1', F30M_QUEUE_SKIP='1'))
ok &= check('p661 (b)(1): a launcher whose linter fails exits 10 before anything, no times.txt line (rc %d)' % r.returncode,
            r.returncode == 10 and not os.path.exists(tmf))
shutil.rmtree(BADD, ignore_errors=True)
TMF2 = os.path.join(HERE, 'fx_p660_times.txt')
if os.path.exists(TMF2):
    os.remove(TMF2)
gb = os.path.join(HERE, 'guard_block.txt')
gbs = sha(gb) if os.path.exists(gb) else None
rc, out = bash('launch_f30m.sh', 'f30_s7_c5', env={'F30M_TIMES': TMF2.replace('\\', '/'), 'F30M_DRYRUN': '2', 'F30M_DISP_SKIP': '1', 'F30M_QUEUE_SKIP': '1'})
ok &= check('p660 (d)(1): launch dry-run 2 rc 0 without guard calls, guard_block.txt untouched (%s)' % out.strip().split('\n')[-1][:40],
            rc == 0 and out.strip().split('\n')[-1] == 'dryrun2' and (sha(gb) if os.path.exists(gb) else None) == gbs)
if os.path.exists(TMF2):
    os.remove(TMF2)

# --- strict cp1250 output of the planner ---
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        NX.main(['--runs', runs(eps(2))])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check('planner output strict cp1250, ASCII (%r)' % raw.getvalue()[:60], cp_ok and all(c < 128 for c in raw.getvalue()) and raw.getvalue().startswith(b'NEXT f30_s3_c5'))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
