"""F25m (HPP-680; ROADMAP s122 item 620, seal 2): fixtures of the seal 2 members - tempo_f25m.py (each form, each edge, the level line,
the hold line, xz, the real logs b36_s1 / b36_f0), dispstate.py (the line, the exit code, the hold modes ending by the stop file and by
max), the chain text (go_f25m.sh: display check before the lock, the hold process from before the lock to after 'lock released', stop
before every move, seal 2 required, DISPLAY_OFF branch; launch_f25m.sh: display check before the TAG line; post_f25m.sh: the tempo member
and SERIES_STOP), strict cp1250 output.  ASCII only; ends with ALL OK.
usage: python test_p620_f25m.py"""
import hashlib
import lzma
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tempo_f25m as TP  # noqa: E402

TMP = os.path.join(HERE, 'fx_p620')
print('suite test_p620_f25m.py sha256 %s target tempo_f25m.py sha256 %s dispstate.py sha256 %s go_f25m.sh sha256 %s launch_f25m.sh sha256 %s '
      'post_f25m.sh sha256 %s' % tuple(hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (
          os.path.abspath(__file__), os.path.join(HERE, 'tempo_f25m.py'), os.path.join(HERE, 'dispstate.py'), os.path.join(HERE, 'go_f25m.sh'),
          os.path.join(HERE, 'launch_f25m.sh'), os.path.join(HERE, 'post_f25m.sh'))))
ok = True
nchk = 0


def check(name, cond, got=None):
    global ok, nchk
    nchk += 1
    if not cond:
        ok = False
        print('FAIL %s (got %s)' % (name, got))


def env_cp1250():
    e = dict(os.environ)
    e.pop('PYTHONIOENCODING', None)
    e['PYTHONUTF8'] = '0'
    return e


def py(args, timeout=120):
    p = subprocess.run([sys.executable] + args, capture_output=True, env=env_cp1250(), timeout=timeout)
    return p.returncode, p.stdout.decode('ascii', 'replace'), p.stderr.decode('ascii', 'replace'), p.stdout


if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)
NL = chr(10)
TAB = chr(9)


def write(name, lines, xz=False):
    p = os.path.join(TMP, name)
    data = (NL.join(lines) + NL).encode('ascii')
    if xz:
        with lzma.open(p, 'wb') as f:
            f.write(data)
    else:
        open(p, 'wb').write(data)
    return p


def harness_log(dts, before=(500000,)):
    out = ['FrameTrace: n=%d dt_us=%d draws=5' % (i, d) for i, d in enumerate(before)]
    out.append('GuestOut: Level has started: ')
    for i, d in enumerate(dts):
        out.append('FrameTrace: n=%d dt_us=%d draws=5' % (100 + i, d))
        out.append(TAB + ' display_buffer_index = %d' % (i % 2))
    return out


RUN = write('run.txt', ['17.9 s  Level has started: pot_treasure_cave', 'holding the run for 150 s', 'hold end: ft_total 0'])

# ---- tempo: harness form
for name, dts, st, rc in (('fast 20 ms', [20000] * 50, 'PASS', 0), ('slow 267 ms', [267000] * 50, 'FAIL', 1),
                          ('edge exactly 100 ms', [100000] * 10, 'EDGE', 3), ('just under 99 999 us', [99999] * 10, 'PASS', 0),
                          ('just over 100 001 us', [100001] * 10, 'FAIL', 1), ('mean of mixed 10 ms / 190 ms = 100 ms', [10000, 190000], 'EDGE', 3),
                          ('mean of mixed 15 ms x 9 / 500 ms = 63.5 ms', [15000] * 9 + [500000], 'PASS', 0)):
    p = write('h_%d.txt' % rc, harness_log(dts))
    t = TP.tempo(p, RUN)
    check('tempo harness %s -> %s' % (name, st), t['status'] == st and t['rc'] == rc and t['form'] == 'harness' and t['frames'] == len(dts), t)
p = write('h_before.txt', harness_log([20000] * 5, before=[900000] * 50))
t = TP.tempo(p, RUN)
check('tempo harness: FrameTrace lines before the level line are not counted', t['status'] == 'PASS' and t['frames'] == 5, t)
check('tempo harness: a row of flip records', any('flip records after the level line 5' in r for r in t['rows']), t['rows'])
p = write('h_xz.txt.xz', harness_log([267000] * 5), xz=True)
t = TP.tempo(p, RUN)
check('tempo harness: an xz log is read', t['status'] == 'FAIL' and t['frames'] == 5, t)
p = write('nolevel.txt', ['FrameTrace: n=1 dt_us=20000 draws=5', TAB + ' display_buffer_index = 0'])
t = TP.tempo(p, RUN)
check('tempo: no level line -> UNDETERMINED rc 2', t['status'] == 'UNDETERMINED' and t['rc'] == 2 and t['why'] == 'no level line', t)
p = write('levelonly.txt', ['GuestOut: Level has started: '])
t = TP.tempo(p, RUN)
check('tempo: level line, 0 frames, 0 flips -> UNDETERMINED (user form, 0 flips)', t['status'] == 'UNDETERMINED' and t['form'] == 'user', t)


# ---- tempo: user form (flip records over the hold)
def user_log(nflip, lf=()):
    out = [TAB + ' display_buffer_index = 1', 'GuestOut: Level has started: ']
    for i in range(nflip):
        out.append(TAB + ' video_out_handle     = 1')
        out.append(TAB + ' display_buffer_index = %d' % (i % 2))
    for n, t in lf:
        out.append('LongFrame: n=%d dt_us=500000 log_async=0 t_ms=%d' % (n, t))
    return out


for name, nflip, st in (('587 flips / 150 s (b36_s1 form) = 3.9 fps', 587, 'FAIL'), ('9000 flips / 150 s = 60 fps', 9000, 'PASS'),
                        ('1500 flips / 150 s = exactly 10 fps', 1500, 'EDGE'), ('1501 flips / 150 s', 1501, 'PASS'),
                        ('1499 flips / 150 s', 1499, 'FAIL')):
    p = write('u_%d.txt' % nflip, user_log(nflip))
    t = TP.tempo(p, RUN)
    check('tempo user %s -> %s' % (name, st), t['status'] == st and t['form'] == 'user' and t['frames'] == nflip, t)
p = write('u_lf.txt', user_log(600, lf=((37, 1000), (622, 151100))))
t = TP.tempo(p, RUN)
check('tempo user: LongFrame span row (585 frames over 150.1 s)', any('LongFrame span n 37..622 over 150.1 s: 3.90 fps' in r for r in t['rows']), t['rows'])
p = write('u_lf1.txt', user_log(600, lf=((37, 1000),)))
t = TP.tempo(p, RUN)
check('tempo user: one LongFrame line - no span row', any('(< 2, no span row)' in r for r in t['rows']), t['rows'])
t = TP.tempo(p, os.path.join(TMP, 'absent_run.txt'))
check('tempo user: no run.txt -> UNDETERMINED', t['status'] == 'UNDETERMINED' and 'hold line' in t['why'], t)
RUN2 = write('run_nohold.txt', ['no hold here'])
t = TP.tempo(p, RUN2)
check('tempo user: run.txt without the hold line -> UNDETERMINED', t['status'] == 'UNDETERMINED', t)
RUN3 = write('run_two.txt', ['holding the run for 150 s', 'holding the run for 300 s'])
p = write('u_3000.txt', user_log(3000))
t = TP.tempo(p, RUN3)
check('tempo user: the last hold line counts (3000 / 300 s = 10 fps EDGE)', t['status'] == 'EDGE', t)

# ---- tempo CLI: strict cp1250, exit codes
for name, f, rc in (('PASS', 'h_0.txt', 0), ('FAIL', 'h_1.txt', 1), ('EDGE', 'h_3.txt', 3), ('UNDETERMINED', 'nolevel.txt', 2)):
    r, out, err, raw = py([os.path.join(HERE, 'tempo_f25m.py'), os.path.join(TMP, f), RUN])
    check('tempo CLI %s: exit %d, first line TEMPO %s, ASCII' % (name, rc, name), r == rc and out.startswith('TEMPO %s' % name) and
          all(b < 128 for b in raw) and not err, (r, out, err))
r, out, err, raw = py([os.path.join(HERE, 'tempo_f25m.py'), os.path.join(TMP, 'h_3.txt'), RUN])
check('tempo CLI EDGE names both readings', 'dt < 100 ms -> FAIL, >= 10 fps -> PASS' in out, out)
r, out, err, raw = py([os.path.join(HERE, 'tempo_f25m.py')])
check('tempo CLI usage -> exit 9', r == 9, (r, out))

# ---- tempo on the real logs of the DISPLAY_OFF tags (the reason of item 620)
for tag, form, lo, hi in (('b36_s1', 'user', 3.5, 4.5), ('b36_f0', 'harness', 3.5, 4.5)):
    lp = os.path.join(HERE, 'log_%s.txt' % tag)
    rp = None
    for d in (os.path.join(HERE, 'runs', tag), ) + tuple(os.path.join(HERE, 'runs', x) for x in sorted(os.listdir(os.path.join(HERE, 'runs')))
                                                          if x.startswith(tag + '.display')):
        if os.path.isfile(os.path.join(d, 'run.txt')):
            rp = os.path.join(d, 'run.txt')
            break
    if os.path.isfile(lp) and rp:
        t = TP.tempo(lp, rp)
        check('tempo real %s: FAIL, form %s, fps in [%.1f; %.1f]' % (tag, form, lo, hi), t['status'] == 'FAIL' and t['form'] == form and
              lo <= t['fps'] <= hi, (t['status'], t['form'], t['fps']))
    else:
        check('tempo real %s: log and run.txt present' % tag, False, (lp, rp))

# ---- dispstate.py
DSP = os.path.join(HERE, 'dispstate.py')
r, out, err, raw = py([DSP])
m = re.match(r'^dispstate (ON|OFF|DIMMED|UNKNOWN) idle_s -?\d+ utc \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', out)
check('dispstate: one line of the form, ASCII, no stderr', m is not None and all(b < 128 for b in raw) and not err, (out, err))
if m:
    check('dispstate: exit code matches the state', r == {'ON': 0, 'OFF': 1, 'DIMMED': 2, 'UNKNOWN': 3}[m.group(1)], (r, m.group(1)))
stop = os.path.join(TMP, 'disp.stop')
open(stop, 'w').close()
t0 = time.time()
r, out, err, raw = py([DSP, '--hold-until', stop, '--max', '60'])
dt = time.time() - t0
check('dispstate --hold-until: the stop file ends it (< 10 s), request set and reset, exit 0',
      r == 0 and 'hold request set' in out and 'hold reset (stop file)' in out and dt < 10 and all(b < 128 for b in raw), (r, out, err, dt))
check('dispstate --hold-until: the start state line', re.search(r'hold start dispstate (ON|OFF|DIMMED|UNKNOWN) idle_s', out) is not None, out)
t0 = time.time()
r, out, err, raw = py([DSP, '--hold-until', os.path.join(TMP, 'never.stop'), '--max', '2'])
dt = time.time() - t0
check('dispstate --hold-until: max ends it', r == 0 and 'hold reset (max)' in out and dt < 10, (r, out, dt))
r, out, err, raw = py([DSP, '--hold', '1'])
check('dispstate --hold 1: probe mode sets and resets', 'hold request set' in out and 'dispstate after' in out and r in (0, 1, 2, 3), (r, out))

# ---- chain text
GO = open(os.path.join(HERE, 'go_f25m.sh')).read()
BASH = next(b for b in ('C:/Program Files/Git/usr/bin/bash.exe', 'C:/Program Files/Git/bin/bash.exe') if os.path.isfile(b))
LA = open(os.path.join(HERE, 'launch_f25m.sh')).read()
PO = open(os.path.join(HERE, 'post_f25m.sh')).read()
i_ds = GO.find('DS=$(python $G/dispstate.py)')
i_hold = GO.find('python $G/dispstate.py --hold-until $OUT/disp.stop')
i_lock = GO.find('if ! { echo "F25m HPP-680 go_f25m.sh $T pid')
i_rel = GO.find('log "lock released (rc $RCX)"')
i_da = GO.find('DA=$(python $G/dispstate.py); DARC=$?')
i_sd = GO.find('stop_disp', i_da)
check('go: display check before the hold, the hold before the lock', 0 < i_ds < i_hold < i_lock, (i_ds, i_hold, i_lock))
check('go: display OFF before the lock -> exit 6, the folder moved (not an attempt)', '[ $DSRC = 0 ] || {' in GO and '.dispoff_' in GO and 'exit 6; }' in GO)
check('go: display check after lock released, then the hold stops', i_rel < i_da < i_sd, (i_rel, i_da, i_sd))
check('go: DISPLAY_OFF branch moves the tag folder before the user branch', GO.find('$OUT.display_') < GO.find('elif [ -e $OUT/USER_FOUND ]; then') and
      'if [ $DARC != 0 ] && [ -f $OUT/run.txt ]; then' in GO)
for tagline in ('mv $OUT $OUT.lock_', 'mv $OUT $OUT.user_$(date -u +%H%M%S); python $G/guard_f25m.py close user_found > /dev/null; log "user emulator',
                'mv $OUT $OUT.session_'):
    j = GO.find(tagline, i_hold)
    check('go: stop_disp right before "%s"' % tagline[:24], j > 0 and GO.rfind('stop_disp', 0, j) > GO.rfind(NL, 0, j) - 1 and
          GO.rfind('stop_disp', 0, j) > i_hold, j)
check('go: the lock-stays branch stops the hold too', 'stop_disp' + NL + '    echo "$(u) $T" > $G/RETURN_FAILED' in GO)
check('go: DISPLAY_OFF after the tag writes SERIES_STOP', 'DISPLAY_OFF after the tag (item 620 (g)(1)): $DA" > $G/SERIES_STOP' in GO)
check('go: seal 2 required', '[ -f "$G/pred/f25m_seal2.md" ] ||' in GO)
check('go: the request flags of item 620 (v)(1) named', 'ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED' in GO)
DS_SRC = open(DSP).read()
check('dispstate: the request ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED, reset ES_CONTINUOUS, no powercfg / no input',
      'SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED)' in DS_SRC and
      'SetThreadExecutionState(ES_CONTINUOUS)' in DS_SRC and 'powercfg' not in DS_SRC and 'SendInput' not in DS_SRC and
      'keybd_event' not in DS_SRC and 'mouse_event' not in DS_SRC)
j1 = LA.find('DS=$(python $G/dispstate.py)')
check('launch: display check before the guard TAG line, exit 6, restoreA exempt', 0 < j1 < LA.find('guard_f25m.py tag $T') and
      'exit 6' in LA and '"$T" != restoreA' in LA)
check('post: tempo after the reader, SERIES_STOP on a non-PASS', PO.find('python tempo_f25m.py $G/log_$T.txt $D/run.txt') > PO.find('f25m_read.py $T --json') and
      '[ $TRC != 0 ]' in PO and '> $G/SERIES_STOP' in PO)
check('post: W executor variant row only', 'executor variant for W (mean dt < 200 ms)' in PO)
r = subprocess.run([BASH, '-n', os.path.join(HERE, 'go_f25m.sh')], capture_output=True)
check('go: bash -n', r.returncode == 0, r.stderr)
r = subprocess.run([BASH, '-n', os.path.join(HERE, 'launch_f25m.sh')], capture_output=True)
check('launch: bash -n', r.returncode == 0, r.stderr)
r = subprocess.run([BASH, '-n', os.path.join(HERE, 'post_f25m.sh')], capture_output=True)
check('post: bash -n', r.returncode == 0, r.stderr)
for f in ('go_f25m.sh', 'launch_f25m.sh', 'post_f25m.sh', 'tempo_f25m.py', 'dispstate.py'):
    b = open(os.path.join(HERE, f), 'rb').read()
    check('%s: LF only, ASCII only' % f, b'\r' not in b and all(c < 128 for c in b))

shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
