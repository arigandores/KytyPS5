"""Fixtures of the F30q chain (Track F link F30q, HPP-727; ROADMAP s122 item 664 (z), item 665 (v)): the dry-run plan of go_f30q.sh for every
tag form (w6: level Sky Garden, KYTY_RT_SKIP=6, form W of item 295 (b) - --vulkan-validation true, VK_LAYER_PATH,
VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000, stable draws 100, timeout 900, hold 150, no video; c6: s1..s9, KYTY_RT_SKIP=6, stable draws 300,
timeout 480, hold 150, no video, the keys of S9 only), refusals of the tag names (the F30m names included), the planner next_f30q.py (w6
first, then s1..s9 c6; a w6 that is not ADMITTED with every member YES holds the series; interference waits for the lead, STOP, READ,
LIMIT 10, BUDGET 5400 s, DONE), the copies of the F30m tools (unchanged or with the names moved), the binaries of go_f30q.sh (T3 installed,
FS11 returned), post / launch refusals, the form of item 634 (items 660, 661), strict cp1250 output.  Not mutated (process tools).  ASCII
only; ends with ALL OK.
usage: python test_tools_f30q.py"""
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
F30M = 'C:/kyty/f287/f30m'
BASH = 'C:/Program Files/Git/bin/bash.exe'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_tools_f30q.py sha256 %s target go_f30q.sh sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'go_f30q.sh'))))
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


# --- dry-run plans of go_f30q.sh ---
LV = {'s1': 'underwater_aerial_garden', 's2': 'hoover_beach', 's3': 'mini_giants_garden', 's4': 'timestop_casino',
      's5': 'rotating_level_day_and_night', 's6': 'sponge_dirty_bath', 's7': 'time_stopper_ghost_world', 's8': 'big_hand_pirate_island',
      's9': 'underwater_aerial_garden'}
KEYS = open('C:/kyty/KytyPS5/docs/track-f/fs3c/keys_a2_presents.txt', encoding='ascii').read().strip()
FORMS = [('s1', 'w6')] + [('s%d' % i, 'c6') for i in range(1, 10)]
for sc, kd in FORMS:
    for rep in ('', '_r2'):
        t = 'f30_%s_%s%s' % (sc, kd, rep)
        rc, out = bash('go_f30q.sh', t, env={'F30Q_DRYRUN': '1'})
        if kd == 'w6':
            form = (' sd 100 ' in out and ' timeout 900 ' in out and 'rec --emu-arg=--vulkan-validation --emu-arg=true ' in out
                    and 'VK_LAYER_PATH=C:/VulkanSDK/1.4.357.0/Bin VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000 ' in out
                    and 'VK_LAYER_MESSAGE_ID_FILTER' not in out)
        else:
            form = ' sd 300 ' in out and ' timeout 480 ' in out and ' rec - ' in out and 'VK_LAYER' not in out
        good = (rc == 0 and ('level %s ' % LV[sc]) in out and 'KYTY_RT_SKIP=6 ' in out and ' hold 150 ' in out and form
                and (('KYTY_KEYS=' + KEYS) in out) == (sc == 's9') and 'KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0' in out)
        ok &= check('dry-run %s: %s' % (t, out.strip()[-200:]), good)
for bad in ('f30_s2_w6', 'f30_s9_w6', 'f30_s1_c5', 'f30_s1_c4', 'f30_cy_v', 'f30_cy_c4', 'f30_s0_c6', 'f30_cy_c6', 'f30_s1_c6_r4',
            'f30_s1_w6_r0', 'b12_w', ''):
    rc, out = bash('go_f30q.sh', bad, env={'F30Q_DRYRUN': '1'})
    ok &= check('go refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('launch_f30q.sh', bad)
    ok &= check('launch refuses %r rc 2' % bad, rc == 2)
    rc, out = bash('post_f30q.sh', bad)
    ok &= check('post refuses %r rc 2' % bad, rc == 2)
lockf = os.path.join(HERE, 'fx_tools_lock.txt')
open(lockf, 'w').write('fixture lock\n')
rc, out = bash('post_f30q.sh', 'f30_s1_c6', env={'F30Q_LOCK': lockf})
ok &= check('post refuses under a lock rc 3 (%s)' % out.strip()[:60], rc == 3)
os.remove(lockf)
go = open(os.path.join(HERE, 'go_f30q.sh'), encoding='ascii').read()
ok &= check('go: no cache copy or return (cp -a, mv before_)', 'cp -a' not in go and 'before_$d' not in go)
ok &= check('go: T3 installed by full sha from its pinned copy, FS11 returned from the pinned copy',
            'TB=505969510fb20f7ce56a5195b3b6d2209af812bc0c2c85eccb6368a712b1bf34' in go and
            'BIN=$F/bin/kyty_emulator_50596951.exe' in go and 'PINNED=$F/bin/kyty_emulator_ea51ae80.exe' in go and
            'FS11=ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce' in go and 'cp "$PINNED" "$GAME"' in go
            and 'cp "$BIN" "$GAME"' in go)
ok &= check('go: the pinned copies have the named sha256', sha('C:/kyty/f287/bin/kyty_emulator_50596951.exe') ==
            '505969510fb20f7ce56a5195b3b6d2209af812bc0c2c85eccb6368a712b1bf34' and sha('C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe') ==
            'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce')
ok &= check('go: no FS10 / T / T2 sha in the code', 'abfded5e' not in go and '3bc7ada7' not in go and 'bba692c6' not in go)
ok &= check('go: lock by noclobber, lock.log lines, procload masked', 'set -o noclobber' in go and 'lock taken $T' in go
            and 'lock released $T' in go and '| mask >' in go)
ok &= check('go: KYTY_* and VK_LAYER_* unset before the call', "grep -o '^\\(KYTY\\|VK_LAYER\\)_[A-Z0-9_]*'" in go)
ok &= check('go: validation only by REC of w6; no RenderDoc, no checkpoints, no patch in the call',
            all(w not in go.split('F20E_PIDFILE=')[1] for w in ('--vulkan-validation', '--rd', 'KYTY_GPU_CHECKPOINTS', 'KYTY_GAME_PATCH'))
            and go.count('--emu-arg=--vulkan-validation --emu-arg=true') == 1
            and not any('VK_LAYER_MESSAGE_ID_FILTER' in l for l in go.split('\n') if not l.lstrip().startswith('#')))
ok &= check('go: seal f30q_seal.md, lock text F30q HPP-727', 'SEAL=$G/pred/f30q_seal.md' in go and 'F30q HPP-727 go_f30q.sh' in go)

# --- the planner ---
spec = importlib.util.spec_from_file_location('next_f30q', os.path.join(HERE, 'next_f30q.py'))
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
    return dict(status=status, members=[['m', bool(x)] for x in members] if members else [])


W6 = R('ADMITTED', 1, 1, 1, 1, 1, 1, 1)
W6N = R('ADMITTED', 1, 1, 1, 1, 1, 1, 0)
C6 = R('ADMITTED')
INT = R('INTERFERENCE')
NA = R('NOT_ADMITTED')


def eps(upto, extra=None):
    d = {'f30_s1_w6': W6}
    d.update(('f30_s%d_c6' % i, C6) for i in range(1, upto + 1))
    d.update(extra or {})
    return d


P = NX.plan
ok &= check('planner: empty - NEXT f30_s1_w6', P(runs({})) == 'NEXT f30_s1_w6')
ok &= check('planner: w6 made, no read - READ', P(runs({'f30_s1_w6': None})) == 'READ f30_s1_w6')
ok &= check('planner: w6 ADMITTED all YES - NEXT s1 c6', P(runs(eps(0))) == 'NEXT f30_s1_c6')
r = P(runs({'f30_s1_w6': W6N}))
ok &= check('planner: w6 a member NO - HOLD (%s)' % r, r.startswith('HOLD f30_s1_w6 ADMITTED'))
r = P(runs({'f30_s1_w6': NA}))
ok &= check('planner: w6 NOT_ADMITTED - HOLD (%s)' % r, r.startswith('HOLD f30_s1_w6 NOT_ADMITTED'))
ok &= check('planner: w6 INTERFERENCE - WAIT, no c6', P(runs({'f30_s1_w6': INT})).startswith('WAIT lead repeat item for f30_s1_w6'))
ok &= check('planner: w6 repeat _r1 replaces the interfered w6', P(runs({'f30_s1_w6': INT, 'f30_s1_w6_r1': W6})) == 'NEXT f30_s1_c6')
ok &= check('planner: c6 made, no read - READ', P(runs(eps(0, {'f30_s1_c6': None}))) == 'READ f30_s1_c6')
ok &= check('planner: s1 done - NEXT s2', P(runs(eps(1))) == 'NEXT f30_s2_c6')
ok &= check('planner: c6 NOT_ADMITTED - the series goes on', P(runs(eps(1, {'f30_s1_c6': NA}))) == 'NEXT f30_s2_c6')
ok &= check('planner: c6 INTERFERENCE - next scene', P(runs(eps(0, {'f30_s1_c6': INT}))) == 'NEXT f30_s2_c6')
r = P(runs(eps(9, {'f30_s3_c6': INT})))
ok &= check('planner: interference at s3 left after all - WAIT (%s)' % r, r.startswith('WAIT lead repeat item for f30_s3_c6'))
r = P(runs(eps(9, {'f30_s3_c6': INT, 'f30_s3_c6_r1': C6})))
ok &= check('planner: repeat _r1 replaces the interfered c6 - DONE made 10 (%s)' % r, r.startswith('DONE made 10'))
r = P(runs(eps(9)))
ok &= check('planner: all 10 - DONE made 10 (%s)' % r, r.startswith('DONE made 10'))
r = P(runs(eps(9, {'f30_s4_c6': NA})))
ok &= check('planner: DONE notes a NOT_ADMITTED c6 (%s)' % r, r.startswith('DONE') and 'f30_s4_c6 NOT_ADMITTED' in r)
d = runs({})
open(os.path.join(FX, 'SERIES_STOP'), 'w').write('x reason\n')
ok &= check('planner: SERIES_STOP - STOP', P(d).startswith('STOP SERIES_STOP: x reason'))
d = runs({})
open(os.path.join(FX, 'RETURN_FAILED'), 'w').write('t\n')
ok &= check('planner: RETURN_FAILED - STOP', P(d).startswith('STOP RETURN_FAILED'))
lim = eps(8, {'f30_s1_c6_r1': C6})
ok &= check('planner: 10 made non-interference - LIMIT before s9', P(runs(lim)) == 'LIMIT 10 made tags')

def locklog(pairs):
    out = []
    for t, a, b in pairs:
        out += ['lock taken %s 2026-10-09T%s' % (t, a), 'lock released %s 2026-10-09T%s' % (t, b)]
    return '\n'.join(out) + '\n'


ok &= check('planner: lock seconds of the pairs', NX.lock_seconds(runs({}, locklog([('a', '10:00:00Z', '10:05:00Z'), ('b', '11:00:00Z', '11:00:30Z')]))) == 330)
ok &= check('planner: an open pair counts nothing', NX.lock_seconds(runs({}, 'lock taken a 2026-10-09T10:00:00Z\n')) == 0)
r = P(runs(eps(8), locklog([('a', '10:00:00Z', '11:23:01Z')])))
ok &= check('planner: lock 4981 s + 420 > 5400 - BUDGET (%s)' % r, r.startswith('BUDGET lock 4981 s'))
r = P(runs(eps(8), locklog([('a', '10:00:00Z', '11:23:00Z')])))
ok &= check('planner: lock 4980 s + 420 = 5400 - NEXT s9 (%s)' % r, r == 'NEXT f30_s9_c6')
r = P(runs({}, locklog([('a', '10:00:00Z', '11:22:01Z')])))
ok &= check('planner: lock 4921 + 480 > 5400 at w6 - BUDGET (%s)' % r, r.startswith('BUDGET') and 'f30_s1_w6' in r)

# --- copies of the F30m tools ---
SAME = ('dispstate.py', 'manifest_fs4c.py', 'procload.py', 'idle142.py', 'launch_run.py', 'run_safety99.py', 'sheet142.py', 'gates_default.txt',
        'kref_f30q.tsv')
for f in SAME:
    ok &= check('copy unchanged %s' % f, sha(os.path.join(HERE, f)) == sha(os.path.join(F30M, f.replace('f30q', 'f30m'))))
HDR = ('# Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)): copy of the F30m (HPP-723) file with the names moved (f30m -> f30q, '
       'F30m -> F30q, F30M_ -> F30Q_, HPP-723 -> HPP-727); no change of meaning.')


def moved(text):
    return text.replace('f30m', 'f30q').replace('F30M', 'F30Q').replace('F30m', 'F30q').replace('HPP-723', 'HPP-727')


for f in ('guard', 'hold', 'runchk', 'queue', 'tempo', 'kref'):
    a = open(os.path.join(F30M, '%s_f30m.py' % f), encoding='utf-8').read()
    b = open(os.path.join(HERE, '%s_f30q.py' % f), encoding='utf-8').read()
    ok &= check('copy %s_f30q.py = F30m with the names moved, one header line' % f, b.split('\n', 1)[0] == HDR and
                b.split('\n', 1)[1] == moved(a.split('\n', 1)[1]))
a = open(os.path.join(F30M, 'enter_scene.py'), encoding='utf-8').read()
b = open(os.path.join(HERE, 'enter_scene.py'), encoding='utf-8').read()
ok &= check('enter_scene.py = F30m with the names moved, one header line', b.split('\n', 1)[0] == HDR and b.split('\n', 1)[1] == moved(a.split('\n', 1)[1])
            and "ROOT = pathlib.Path('C:/kyty/f287/f30q')" in b)
for f, own in (('runchk_f30q.py', "OWN = 'HPP-727'"), ('queue_f30q.py', "OWN = 'HPP-727'")):
    ok &= check('%s own issue HPP-727' % f, own in open(os.path.join(HERE, f), encoding='utf-8').read())
ok &= check('runchk reads F30Q_RUN_ID, launch passes it', "os.environ.get('F30Q_RUN_ID'" in open(os.path.join(HERE, 'runchk_f30q.py'), encoding='utf-8').read()
            and 'F30Q_RUN_ID="${PAPERCLIP_RUN_ID:-}"' in open(os.path.join(HERE, 'launch_f30q.sh'), encoding='ascii').read())
ok &= check('chk_f30q.sh reads the comments of HPP-727', '/api/issues/HPP-727/comments' in open(os.path.join(HERE, 'chk_f30q.sh'), encoding='ascii').read())
for f in ('launch_f30q.sh', 'wait_f30q.sh', 'chk_f30q.sh', 'post_f30q.sh', 'go_f30q.sh'):
    t = open(os.path.join(HERE, f), 'rb').read()
    code = b' '.join(l for l in t.split(b'\n') if not l.lstrip().startswith(b'#'))
    ok &= check('%s ASCII, LF, no f30m / HPP-723 / F30M_ names in the code lines' % f, all(c < 128 for c in t) and b'\r\n' not in t
                and b'f30m' not in code.lower() and b'HPP-723' not in code and b'F30M_' not in code)

# --- item 660 (d)(4), 661 (b): the form of item 634 in launch_f30q.sh and go_f30q.sh ---
import re
import subprocess
LINTER = 'C:/kyty/KytyPS5/ps5 em/docs/form634_check.py'
LINT_LINE = 'python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f30q || exit 10'


def code_of(f):
    return [(n, l.strip()) for n, l in enumerate(open(os.path.join(HERE, f), encoding='ascii').read().split('\n'), 1)
            if l.strip() and not l.strip().startswith('#')]


for f in ('launch_f30q.sh', 'go_f30q.sh'):
    cl = code_of(f)
    ok &= check('p661: %s first executable line is the linter with exit 10 (%s)' % (f, cl[0][1][:70]), cl[0][1] == LINT_LINE)
    ok &= check('p660: %s has no block logic (guard_block, open-block, guard status/tag/close)' % f,
                not any(re.search(r'guard_block|open-block|guard_\w*\.py\s+(status|tag|close|open-block)\b', s) for _, s in cl))
lc = code_of('launch_f30q.sh')
ok &= check('p660 (d)(1): launch has no guard_*.py / hold_*.py call', not any(re.search(r'guard_\w*\.py|hold_\w*\.py', s) for _, s in lc))
ok &= check('p660 (d)(1): launch keeps the display, the queue and the launch', any('dispstate.py' in s for _, s in lc)
            and any('queue_f30q.py' in s for _, s in lc) and any('nohup bash -c "bash $G/go_f30q.sh $T' in s for _, s in lc))
gc = code_of('go_f30q.sh')
lock_n = next(n for n, s in gc if 'lock taken $T' in s)
man_n = next(n for n, s in gc if n > lock_n and 'manifest_fs4c.py' in s)
scans = [n for n, s in gc if re.search(r'guard_\w*\.py\s+scan\b(?!.*--pidfile)', s)]
holds = [n for n, s in gc if re.search(r'hold_\w*\.py\s+check\b', s)]
ok &= check('p660 (d)(2): go has no guard / hold check before the lock line %d' % lock_n,
            not any(n < lock_n for n in scans + holds))
ok &= check('p660 (d)(2): go has ONE guard scan and ONE hold check, after the lock %d and before the manifest %d (%s / %s)'
            % (lock_n, man_n, scans, holds), len(scans) == 1 and len(holds) == 1 and lock_n < scans[0] < man_n and lock_n < holds[0] < man_n)
ok &= check('p660 (d)(3): go keeps procload, the watch during the tag, kill-own by pid, the FS11 return',
            any('procload.py' in s for _, s in gc) and any('hold_f30q.py watch' in s or 'guard_f30q.py watch' in s for _, s in gc)
            and any('kill-own --pidfile' in s for _, s in gc) and 'cp "$PINNED" "$GAME"' in go)
r = subprocess.run([sys.executable, LINTER, '--series', HERE], capture_output=True, text=True)
ok &= check('p661: linter --series f30q rc 0, last line ALL OK (%s)' % r.stdout.strip().split('\n')[-1], r.returncode == 0 and r.stdout.strip().split('\n')[-1] == 'ALL OK')
BADD = os.path.join(HERE, 'fx_p660_bad')
shutil.rmtree(BADD, ignore_errors=True)
os.makedirs(BADD)
for f in ('launch_f30q.sh', 'go_f30q.sh'):
    shutil.copy2(os.path.join(F30M, 'old', 'p660', f.replace('f30q', 'f30m')), os.path.join(BADD, f))
r = subprocess.run([sys.executable, LINTER, '--series', BADD], capture_output=True, text=True)
ok &= check('p661 negative: linter on the pre-660 scripts rc 1, FORM634 FAILED (%s)' % r.stdout.strip().split('\n')[-1],
            r.returncode != 0 and 'FORM634 FAILED' in r.stdout)
lt = open(os.path.join(HERE, 'launch_f30q.sh'), encoding='ascii').read().replace('--series C:/kyty/f287/f30q', '--series ' + BADD.replace('\\', '/'))
open(os.path.join(BADD, 'launch_bad.sh'), 'w', encoding='ascii', newline='\n').write(lt)
tmf = os.path.join(BADD, 'times.txt')
r = subprocess.run([BASH, os.path.join(BADD, 'launch_bad.sh').replace('\\', '/'), 'f30_s7_c6'], capture_output=True, text=True,
                   env=dict(os.environ, F30Q_TIMES=tmf.replace('\\', '/'), F30Q_DRYRUN='2', F30Q_DISP_SKIP='1', F30Q_QUEUE_SKIP='1'))
ok &= check('p661 (b)(1): a launcher whose linter fails exits 10 before anything, no times.txt line (rc %d)' % r.returncode,
            r.returncode == 10 and not os.path.exists(tmf))
shutil.rmtree(BADD, ignore_errors=True)
TMF2 = os.path.join(HERE, 'fx_p660_times.txt')
if os.path.exists(TMF2):
    os.remove(TMF2)
gb = os.path.join(HERE, 'guard_block.txt')
gbs = sha(gb) if os.path.exists(gb) else None
rc, out = bash('launch_f30q.sh', 'f30_s7_c6', env={'F30Q_TIMES': TMF2.replace('\\', '/'), 'F30Q_DRYRUN': '2', 'F30Q_DISP_SKIP': '1', 'F30Q_QUEUE_SKIP': '1'})
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
ok &= check('planner output strict cp1250, ASCII (%r)' % raw.getvalue()[:60], cp_ok and all(c < 128 for c in raw.getvalue()) and raw.getvalue().startswith(b'NEXT f30_s3_c6'))
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
