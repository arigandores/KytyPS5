"""F20c (HPP-561): fixtures of f20c_read.py - one per member of item 462 (g)-(d) and per edge (scene frames 722 / 723 / 828 / 829, IR in
the window, cache save in the interval, only PriorityStall, dt_us = 100 000), admission members, series reading, cp1250 output.
usage: python test_f20c_read.py   (ASCII only; the last line is ALL OK when every check passes)"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f20c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f20c_read.py sha256 %s target f20c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(R.__file__)))
T = tempfile.mkdtemp(prefix='f20c_fx_')
ADB = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
FS6 = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
OLD = '631ff987' + '0' * 56
fails = []
n_checks = [0]


def check(name, cond):
    n_checks[0] += 1
    if not cond:
        fails.append(name)
        print('FAIL', name)


def mklog(name, n=6200, dt=None, iv=None, after=None, head=(), quit_at=None, level_name='underwater_aerial_garden', first_draws=150,
          tail=()):
    """n frames after the first scene frame (default dt 50 000 us); iv{idx: [lines]} go BEFORE the line of frame idx;
    after{idx: [lines]} go right after it; quit_at - 'Event: quit' before the frame idx."""
    dt = dt or {}
    iv = iv or {}
    after = after or {}
    L = ['Kyty fixture header'] + list(head)
    for k in range(1, 4):
        L.append('FrameTrace: n=%d dt_us=16000 draws=5' % k)
    L.append('[1][00:00:01.000] Level has started: %s' % level_name)
    L.append('FrameTrace: n=10 dt_us=20000 draws=99')
    L.append('FrameTrace: n=11 dt_us=200000 draws=%d' % first_draws)
    for i in range(1, n + 1):
        if quit_at == i:
            L.append('Event: quit')
        L.extend(iv.get(i, []))
        L.append('FrameTrace: n=%d dt_us=%d draws=300 x=1' % (11 + i, dt.get(i, 50000)))
        L.extend(after.get(i, []))
    L.extend(tail)
    p = os.path.join(T, name + '.txt')
    with open(p, 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    return p


def ev(path, b=ADB):
    return R.evaluate(R.scan(path), b)


SLOW = 150000
# --- base
e = ev(mklog('base'))
check('base entered', e['entered'] and e['first_n'] == 11)
check('base frames 6200', e['frames'] == 6200)
check('base window read', e['window_read'])
check('base warm', e['warm'] and e['window_dump'] == 0)
check('base B2 0', e['b2_frames'] == [])
check('base hold (310 s)', e['hold'] and abs(e['scene_s'] - 310.0) < 1e-6)
check('base unattr 0', e['unattr'] == 0 and e['unattr_f20a'] == 0 and e['hold_frames'] == [])
check('base k1s 0', e['k1s_after'] == 0)
# --- B2 window edges 722 / 723 / 828 / 829
e = ev(mklog('w722', dt={722: SLOW}))
check('722 not B2', e['b2_frames'] == [] and e['window_slow'] == [])
check('722 hold frame nothing', len(e['hold_frames']) == 1 and e['hold_frames'][0]['letter'] == 'nothing' and e['unattr'] == 1)
e = ev(mklog('w723', dt={723: SLOW}))
check('723 B2', [x[0] for x in e['b2_frames']] == [723])
e = ev(mklog('w828', dt={828: SLOW}))
check('828 B2', [x[0] for x in e['b2_frames']] == [828])
e = ev(mklog('w829', dt={829: SLOW}))
check('829 not B2', e['b2_frames'] == [] and e['unattr'] == 1)
# --- dump in the window: cold
e = ev(mklog('ir750', iv={750: ['%12 = OpLoad %float %11']}, dt={760: SLOW}))
check('IR in window -> cold', not e['warm'] and e['window_dump'] == 1 and e['window_dump_frames'] == [[750, 1]])
check('cold -> no B2 frame', e['b2_frames'] == [])
check('cold still hold, frame nothing', e['hold'] and e['unattr'] == 1)
e = ev(mklog('ir722', iv={722: ['  %5 = OpLabel'], 829: ['%6 = OpLabel']}))
check('IR at 722 and 829 -> warm', e['warm'] and e['window_dump'] == 0)
e = ev(mklog('ir723', iv={723: ['%5 = OpLabel']}))
check('IR at 723 -> cold', not e['warm'])
e = ev(mklog('ir828', iv={828: ['%5 = OpLabel']}))
check('IR at 828 -> cold', not e['warm'])
e = ev(mklog('irind', iv={800: ['    %5 = OpLabel', '\t%6 = OpLabel']}))
check('indented and tab-led IR in window -> cold, 2 lines', not e['warm'] and e['window_dump'] == 2)
e = ev(mklog('gcn724', iv={724: ['0001a4: V_MOV_B32 v0, v1']}))
check('GCN line in window -> cold', not e['warm'] and e['window_dump'] == 1)
e = ev(mklog('gcntab', iv={724: ['\t0001a4: V_MOV_B32 v0, v1']}))
check('tab-led GCN line not counted -> warm', e['warm'])
e = ev(mklog('irafter', after={760: ['%5 = OpLabel']}))
check('IR after frame 760 counts in interval of 761 -> cold', not e['warm'] and e['window_dump_frames'] == [[761, 1]])
# --- cache save in the interval
PCS = 'Vulkan pipeline cache: saved 123 bytes (104445 us)'
e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}))
check('saved in interval -> not B2', e['b2_frames'] == [] and len(e['window_slow']) == 1)
check('saved on adb0c82f letter -> nothing', e['hold_frames'][0]['letter'] == 'nothing' and e['unattr'] == 1)
check('saved on adb0c82f variant F20a -> unattributed', e['hold_frames'][0]['f20a'] == 'pcs after S12' and e['unattr_f20a'] == 1)
e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}), FS6)
check('saved on FS6 letter -> nothing', e['hold_frames'][0]['letter'] == 'nothing')
e = ev(mklog('pcs', iv={760: [PCS]}, dt={760: SLOW}), OLD)
check('saved on 631ff987 -> B33', e['hold_frames'][0]['letter'] == 'B33' and e['unattr'] == 0 and e['unattr_f20a'] == 0)
e = ev(mklog('pcsir', iv={760: [PCS, '%1 = OpLabel']}, dt={760: SLOW}))
check('saved + IR on adb0c82f letter -> B5, variant unattributed', e['hold_frames'][0]['letter'] == 'B5' and e['unattr'] == 0
      and e['unattr_f20a'] == 1)
# --- only PriorityStall
e = ev(mklog('prio', iv={760: ['PriorityStall: queue 1 us=150844 op=x']}, dt={760: SLOW}))
check('only PriorityStall -> B2 frame', [x[0] for x in e['b2_frames']] == [760] and e['b2_frames'][0][3:] == [1, 150844])
check('only PriorityStall -> prio only, unattributed', e['hold_frames'][0]['letter'] == 'prio only' and e['unattr'] == 1)
# --- BvhLoopCapTrip
e = ev(mklog('trip', iv={760: ['BvhLoopCapTrip: cs 0x1 n 1']}, dt={760: SLOW}))
check('trip -> not B2', e['b2_frames'] == [])
check('trip -> B1b attributed', e['hold_frames'][0]['letter'] == 'B1b' and e['unattr'] == 0)
# --- dt_us = 100 000 edge
e = ev(mklog('d100', dt={760: 100000}))
check('dt 100000 -> B2 frame', [x[0] for x in e['b2_frames']] == [760] and e['unattr'] == 1)
e = ev(mklog('d99', dt={760: 99999}))
check('dt 99999 -> nothing', e['b2_frames'] == [] and e['hold_frames'] == [])
# --- window reach
e = ev(mklog('q827', n=900, quit_at=828))
check('quit before 828 -> window not read', not e['window_read'] and e['frames'] == 827 and not e['warm'] and e['ended_by'] == 'quit')
e = ev(mklog('n828', n=828))
check('exactly 828 frames -> window read', e['window_read'] and e['warm'])
e = ev(mklog('n827', n=827))
check('827 frames -> not read', not e['window_read'])
# --- hold edge
e = ev(mklog('h300', n=6000))
check('scene exactly 300 s -> hold', e['hold'] and e['scene_s'] == 300.0)
e = ev(mklog('h2999', n=6000, dt={6000: 49999}))
check('scene 299.999999 s -> no hold', not e['hold'])
e = ev(mklog('h2999s', n=5990, dt={760: SLOW}))
check('no hold -> unattributed not counted', e['unattr'] == 0 and len(e['hold_frames']) == 1)
# --- entry window edge 10 s (idx 201 starts at 10.0 s)
e = ev(mklog('t995', dt={200: SLOW}))
check('idx 200 (9.95 s) entry window, not a hold frame', [x[0] for x in e['entry_window']] == [200] and e['hold_frames'] == [])
e = ev(mklog('t10', dt={201: SLOW}))
check('idx 201 (10.0 s) hold frame', [x['idx'] for x in e['hold_frames']] == [201] and e['hold_frames'][0]['t_before_s'] == 10.0
      and e['entry_window'] == [])
# --- scene borders
e = ev(mklog('lvl2', after={1000: ['Level has started: hub_main']}))
check('next level line ends the scene', e['frames'] == 1000 and e['ended_by'] == 'level' and not e['hold'])
e = ev(mklog('lvlempty', after={1000: ['Level has started: ']}))
check('empty level name does not end the scene', e['frames'] == 6200)
e = ev(mklog('quitlate', quit_at=6100))
check('frames after quit not counted', e['frames'] == 6099 and e['ended_by'] == 'quit')
e = ev(mklog('other', level_name='hub_main'))
check('other level -> not entered', not e['entered'] and e['frames'] == 0)
e = ev(mklog('draws99', first_draws=99, n=830))
check('draws 99 -> first scene frame is the next one', e['first_n'] == 12 and e['frames'] == 829)
e = ev(mklog('draws100', first_draws=100, n=830))
check('draws 100 -> first scene frame', e['first_n'] == 11 and e['frames'] == 830)
# --- reference
e = ev(mklog('ref', dt={300: 1000000, 100: 1200000}, iv={500: ['--- Fatal Error ---'], 600: ['AsyncPipelines: skipped draw 1']}))
check('k1s after window 1 (idx 300), not idx 100', e['k1s_after'] == 1)
check('death marker found', [d[0] for d in e['death']] == ['--- Fatal Error ---'])
check('skipped draw counted', e['skipped'] == 1)
e = ev(mklog('win', iv={500: ['Window 1 minimized', 'Recovering Vulkan swapchain']}))
check('window events counted', e['minimized'] == 1 and e['recovering'] == 1)


# --- admission (read_tag on a fixture dir)
def mkdir_tag(name, log_kw=None, env_extra=None, cmd_extra=(), binary=ADB, inst_b=None, inst_a=None, prereg=None, guest=None,
              hold=330, mcmp='manifest cmp EQUAL files 3323 listsha a9', glitch='one-frame glitches: 0', drop=()):
    d = os.path.join(T, 'dir_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(mklog('lg_' + name, **(log_kw or {})), os.path.join(d, 'log.txt'))
    with open(os.path.join(d, 'seal.md'), 'w', newline='\n') as f:
        f.write('seal fixture\n')
    s = sha(os.path.join(d, 'seal.md'))
    env = {k: '1' for k in R.HARN}
    env.update(env_extra or {})
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--shader-validation', 'false', '--game', 'x'] + list(cmd_extra)
    js = dict(binary_sha256=binary, env=env, cmdline=cmd, prereg=dict(sha256=prereg or s), guest_args=guest or '-lvl underwater_aerial_garden',
              hold_s=hold, attempts=[dict(outcome='ok', hold_exit=None, hold_s=hold)])
    with open(os.path.join(d, 'es.json'), 'w') as f:
        json.dump(js, f)
    for fn, v in (('installed_before.txt', inst_b or binary), ('installed_after.txt', inst_a or binary), ('manifest_cmp.txt', mcmp),
                  ('glitch.txt', glitch), ('stdout.txt', 'ok'), ('rec.idx', '1\n2\n3')):
        if fn not in drop:
            with open(os.path.join(d, fn), 'w', newline='\n') as f:
                f.write(v + '\n')
    return R.read_tag(name, R.paths(name, d)), d


res, gd = mkdir_tag('good')
check('good admitted', res['admitted'] and all(b for _, b in res['admission']))
check('good reading', res['reading'].startswith('B2: warm, frames 0; B32: hold, unattributed 0'))
check('good reference glitches 0, video 3', res['ref']['glitches'] == 0 and res['ref']['video_index'] == 3)
res, _ = mkdir_tag('fs6', binary=FS6)
check('FS6 binary admitted', res['admitted'])
BAD = (('other binary', dict(binary=OLD)), ('installed after differs', dict(inst_a=OLD)), ('installed before differs', dict(inst_b=OLD)),
       ('prereg mismatch', dict(prereg='0' * 64)), ('env KYTY_GAME_PATCH', dict(env_extra={'KYTY_GAME_PATCH': 'p.txt'})),
       ('env KYTY_AV_TRACE', dict(env_extra={'KYTY_AV_TRACE': '1'})), ('env KYTY_S_PCW', dict(env_extra={'KYTY_S_PCW': '1'})),
       ('shader-validation last true', dict(cmd_extra=('--shader-validation', 'true'))),
       ('vulkan-validation last true', dict(cmd_extra=('--vulkan-validation', 'true'))), ('--rd', dict(cmd_extra=('--rd',))),
       ('guest args', dict(guest='-lvl hub_main')), ('hold 120', dict(hold=120)),
       ('GamePatch line', dict(log_kw=dict(head=('GamePatch: applied x',)))),
       ('TestHidLoss line', dict(log_kw=dict(head=('TestHidLoss: config on 60:hold',)))),
       ('GateArm line', dict(log_kw=dict(iv={50: ['GateArm: n=1 arm=A']}))),
       ('not entered', dict(log_kw=dict(level_name='hub_main'))),
       ('minimized', dict(log_kw=dict(iv={50: ['Window 1 minimized']}))),
       ('recovering', dict(log_kw=dict(iv={50: ['Recovering Vulkan swapchain']}))),
       ('manifest differs', dict(mcmp='manifest cmp DIFFER 3 files')), ('manifest missing', dict(drop=('manifest_cmp.txt',))),
       ('installed after missing', dict(drop=('installed_after.txt',))))
for nm, kw in BAD:
    res, _ = mkdir_tag(nm.replace(' ', '_').replace('-', ''), **kw)
    check('admission fails: ' + nm, not res['admitted'] and res['reading'].startswith('INTERFERENCE'))
res, _ = mkdir_tag('death', log_kw=dict(iv={500: ['--- Fatal Error ---']}, dt={300: 1000000}), glitch='one-frame glitches: 2')
check('death and k1s are reference only (admitted)', res['admitted'] and res['ref']['k1s_after'] == 1 and len(res['ref']['death_log']) == 1
      and res['ref']['glitches'] == 2)
res, _ = mkdir_tag('cold', log_kw=dict(iv={750: ['%1 = OpLabel']}))
check('cold tag admitted, B2 cold not in N', res['admitted'] and 'cold window' in res['reading'])
res, _ = mkdir_tag('short', log_kw=dict(n=800))
check('short tag: window not read, no hold', res['admitted'] and 'window not read' in res['reading'] and 'no hold' in res['reading'])


# --- series and reading (item 462 (d))
def fake(admitted=True, read=True, warm=True, b2=0, hold=True, un=0, unf=None):
    return dict(admitted=admitted, eval=dict(window_read=read, warm=warm, b2_frames=[[760]] * b2, hold=hold, unattr=un,
                                             unattr_f20a=un if unf is None else unf))


s = R.series([fake() for _ in range(24)])
check('base 6 + 24 warm = 30', s['sum']['warm'] == 30 and s['sum']['holds'] == 32)
check('B2 30 and 0 -> NOT A DEFECT', 'B2' in s['b2'] and 'NOT A DEFECT' in s['b2'] and '0 of 30' in s['b2'])
check('B32 32 and 0 -> NOT A DEFECT', 'NOT A DEFECT' in s['b32'] and '0 of 32' in s['b32'])
check('stop adding tags at warm 30', not s['need_more'])
s = R.series([fake() for _ in range(23)])
check('29 warm -> SHORTAGE', 'SHORTAGE, 0 of 29 (1 to go)' in s['b2'] and s['need_more'])
s = R.series([fake() for _ in range(23)] + [fake(b2=2)])
check('one entry with B2 frames -> DEFECT 1 of 30', 'DEFECT candidate, 1 of 30' in s['b2'] and 'p = 0.033' in s['b2'])
s = R.series([fake() for _ in range(22)] + [fake(un=3)])
check('one hold with unattributed -> B32 DEFECT', 'DEFECT candidate, 1 of 31' in s['b32'])
s = R.series([fake() for _ in range(22)] + [fake(un=0, unf=1)])
check('variant F20a counted apart', 'NOT A DEFECT' in s['b32'] and 'DEFECT candidate, 1 of 31' in s['b32_f20a'])
s = R.series([fake() for _ in range(23)] + [fake(admitted=False)])
check('interference not counted', s['sum']['warm'] == 29 and s['tags']['interference'] == 1)
s = R.series([fake() for _ in range(23)] + [fake(warm=False)])
check('cold not counted in B2, counted in B32', s['sum']['warm'] == 29 and s['sum']['holds'] == 32 and s['tags']['cold'] == 1)
s = R.series([fake() for _ in range(23)] + [fake(read=False, warm=False, hold=False)])
check('unread window and no hold', s['sum']['warm'] == 29 and s['sum']['holds'] == 31 and s['tags']['unread'] == 1)
s = R.series([fake(warm=False) for _ in range(30)])
check('30 tags made -> stop even below 30 warm', not s['need_more'] and s['sum']['warm'] == 6)
check('CP upper for 0 of 30 = 0.116', abs(R.cp(0, 30, False) - 0.1157) < 0.001)
check('CP 1 of 30', abs(R.cp(1, 30, True) - 0.00084) < 0.0002 and abs(R.cp(1, 30, False) - 0.1722) < 0.001)

# --- cp1250 output, no PYTHONIOENCODING
env = {k: v for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8')}
for args in (['--dir', gd, '--tag', 'good'], ['--series', '--runs', os.path.join(T, 'none')]):
    p = subprocess.run([sys.executable, R.__file__] + args, capture_output=True, env=env)
    ok = p.returncode == 0
    try:
        p.stdout.decode('cp1250', 'strict')
    except UnicodeDecodeError:
        ok = False
    check('cp1250 output %s' % args[0], ok and all(b < 128 for b in p.stdout))
p = subprocess.run([sys.executable, R.__file__, '--dir', gd, '--tag', 'good', '--json', os.path.join(T, 'r.json')], capture_output=True, env=env)
j = json.load(open(os.path.join(T, 'r.json')))
check('json written', p.returncode == 0 and j['admitted'] and j['tag'] == 'good')
src = open(R.__file__, 'rb').read()
check('reader source ASCII only', all(b < 128 for b in src))

shutil.rmtree(T, ignore_errors=True)
print('checks %d, failed %d' % (n_checks[0], len(fails)))
if fails:
    print('FAILED:', fails)
    sys.exit(1)
print('ALL OK')
