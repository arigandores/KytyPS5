"""Offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,
HPP-277; ROADMAP s122 item 221 (v), (g)(2)-(4), items 215 (v)(2), 217 (b), 218 (g)-(d)).  One case per condition and per
edge: the first scene frame (draws 99/100, rows before the entry line, its dt out of K2/K3/window), the frame 599/600 after
the first frame (the window of 599, item 221 (v)), dt = 1 000 000 / 999 999 (K2) and 100 000 / 99 999 (K3), the sum of dt
after the entry line 120 s / 1 us less, after the first frame 300 s / 1 us less, 2 999 / 3 000 frames, 0 / 1 [Vulkan][E],
every death marker (log and stdout; at exit), hold_exit, the ENDED line, an exited attempt, the tail stall, a stopped
validation run, every admission check, SCENE_OK YES / PENDING_SHEET / NO and a missing run, the stop rule, the seal check,
the calibration logic on synthetic logs, the variant vx, the per-entry rows (skipped draws, opcode profile 96/1/4,
stubbed functions, PriorityStall > 50 ms, BvhLoopCapTrip), scanning across chunk boundaries, and the ASCII output in strict
cp1250 (item 175 (v)).  Synthetic logs only; the real s122 logs are read by sc142.py --calib.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last
statement is `sys.exit(0 if ok else 1)`; no subprocess (main() is called in-process).
The first output line names this suite and the scorer under test by sha256 (item 150 (v)); the output ends with ALL OK.
    python C:/kyty/s142/test_sc142.py [<sc142 under test>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc142.py')
print('suite test_sc142.py sha256 %s target sc142.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc142_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
OTHER = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
SKY = 'underwater_aerial_garden'
PRED_SHA = 'ab' * 32
BASE = Path('C:/kyty/s142/fx_sc142')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
N_CASES = [0]


def case(name, cond):
    N_CASES[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def ft(n, dt, draws=3000):
    return 'FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=%d dispatches=1 faults=0' % (n, dt, draws)


def start(level):
    return 'GuestOut: Level has started: %s' % level


def scene_lines(level, post, first_dt=2000000, pre=None, first_draws=894):
    """boot rows, the empty start, loading, the entry line, a loading row, the first scene frame, then the rows post."""
    out = [ft(i, 20000, 5) for i in range(1, 6)] + [start('')] + [ft(i, 20000, 5) for i in range(6, 11)]
    out += [ft(11, 30000, 3000)]            # draws >= 100 BEFORE the entry line: never the first scene frame
    out += [start(level)] + (pre if pre is not None else [ft(12, 1500000, 20), ft(13, 20000, 99)])
    n = 14
    out += [ft(n, first_dt, first_draws)]
    for dt in post:
        n += 1
        out.append(ft(n, dt, 3000))
    return out


def v_post(total=300000000, count=3100):
    base = 96774
    rows = [base] * (count - 1)
    rows.append(total - base * (count - 1))
    return rows


def env_for(tag):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GATE_FILE': 'C:\\kyty\\s142\\gates.req',
         'KYTY_QUEUE_TRACE': '1', 'KYTY_GUEST_ARGS': '-lvl %s' % S.level_of(tag), 'KYTY_GPU_CLOCK_PIN': '1',
         'KYTY_GPU_MARKERS': '0'}
    if tag == 'w142':
        e['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    else:
        e['KYTY_REC'] = 'C:\\kyty\\s142\\rec_%s.mp4' % tag
    return e


def js_for(tag, attempt=None, **over):
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x']
    if tag == 'w142':
        cmd += ['--vulkan-validation', 'true']
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=330.0 if tag != 'w142' else 310.0, hold_exit=None,
             ft_tail=300, pipeline_cache_off=False)
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD, guest_args='-lvl %s' % S.level_of(tag), gates='', env=env_for(tag),
              cmdline=cmd, prereg=dict(path=S.PRED_PATH, sha256=PRED_SHA), attempts=[a])
    js.update(over)
    return js


def mkrun(root, tag, lines, js=None, stdout_lines=(), es_lines=(), glitch=(3200, 0), sheet=True, log=True):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js_for(tag)), encoding='utf-8')
    if log:
        (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(stdout_lines) + '\n').encode('utf-8'))
    (root / ('%s.stdout.txt' % tag)).write_bytes(('\n'.join(es_lines) + '\nVERDICT: x\n').encode('utf-8'))
    if glitch is not None:
        (root / ('glitch_%s.txt' % tag)).write_text('C:/kyty/s142/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                    'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
    return str(root)


def ent(root, tag):
    return S.entry_of(tag, str(root), PRED_SHA)


def mem(rows, starts, quit=None):
    """An in-memory scan: rows (n, dt, draws) in log order after the starts given as (name, index-before-row)."""
    out = dict(rows=[], starts=[], quit=None)
    pos = 0
    si = dict((i, name) for name, i in starts)
    for i, r in enumerate(rows):
        if i in si:
            out['starts'].append((si[i], pos))
            pos += 10
        if quit is not None and i == quit:
            out['quit'] = pos
            pos += 10
        out['rows'].append((r[0], r[1], r[2], pos))
        pos += 10
    return out


def row_ok(rows, prefix):
    hit = [r for r in rows if r[0].startswith(prefix)]
    return hit[0][1] if len(hit) == 1 else None


ok = True

# ---------------- derive: the first scene frame, the window, K2 / K3 (in memory)
R = [(1, 20000, 5), (2, 30000, 3000), (3, 1500000, 20), (4, 20000, 99), (5, 2000000, 100)] + \
    [(6 + i, 16667, 3000) for i in range(700)]
d = S.derive(mem(R, [('lvl', 2)]), 'lvl')
ok &= case('d1 the first scene frame is the first row after the entry line with draws >= 100 (99 skipped, row before '
           'the entry out)', d['entered'] and d['first'] == (5, 2000000, 100))
ok &= case('d2 the first frame dt 2 s is neither K2 nor K3; the 1.5 s loading row before it is not K2',
           d['k2'] == [] and d['k3w'] == [] and d['k3h'] == [])
ok &= case('d3 window = 599 rows after the first frame, hold = the rest', d['window'] == 599 and d['hold'] == 101)
d = S.derive(mem(R, [('lvl', 1)]), 'lvl')
ok &= case('d1b with the entry line before n 2 the first scene frame is n 2 (draws 3000)', d['first'] == (2, 30000, 3000))
R2 = [(1, 20000, 100)] + [(2 + i, 16667, 3000) for i in range(1000)]
R2[599] = (R2[599][0], 100000, 3000)      # the 599th row after the first frame: last of the window
R2[600] = (R2[600][0], 100000, 3000)      # the 600th: first of the hold
d = S.derive(mem(R2, [('lvl', 0)]), 'lvl')
ok &= case('d4 frame 599 after the first frame -> K3 window; frame 600 -> K3 hold',
           d['k3w'] == [(R2[599][0], 100000)] and d['k3h'] == [(R2[600][0], 100000)])
R3 = [(1, 20000, 100), (2, 1000000, 3000), (3, 999999, 3000), (4, 100000, 3000), (5, 99999, 3000)] + \
     [(6 + i, 16667, 3000) for i in range(800)]
R3[700] = (R3[700][0], 1000000, 3000)
d = S.derive(mem(R3, [('lvl', 0)]), 'lvl')
ok &= case('d5 dt 1 000 000 -> K2 (entry and hold located); 999 999 -> K3 not K2', d['k2'] == [(2, 1000000, 'entry'),
           (R3[700][0], 1000000, 'hold')] and (3, 999999) in d['k3w'])
ok &= case('d6 dt 100 000 -> K3; 99 999 -> nothing', (4, 100000) in d['k3w'] and all(x[0] != 5 for x in d['k3w']))
ok &= case('d6b a K2 frame (dt 1 000 000) is not also a K3 frame', all(x[0] != 2 for x in d['k3w']))
R5 = [(1, 20000, 100)] + [(2 + i, 16667, 3000) for i in range(700)]
R5[599] = (R5[599][0], 1000000, 3000)
R5[600] = (R5[600][0], 1000000, 3000)
d = S.derive(mem(R5, [('lvl', 0)]), 'lvl')
ok &= case('d6c K2 at frame 599 after the first frame is "entry", at frame 600 "hold"',
           [x[2] for x in d['k2']] == ['entry', 'hold'])
d = S.derive(mem(R, [('', 0), ('lvlx', 2)]), 'lvl')
ok &= case('d7 only another level whose name contains the target (and the empty start) -> not entered',
           not d['entered'] and d['first'] is None)
d = S.derive(mem(R, [('lvl', 2), ('lvl', 200)]), 'lvl')
ok &= case('d8 the first entry line of the level is used', d['first'] == (5, 2000000, 100))
d = S.derive(mem([(1, 50000000, 5), (2, 70000000, 20), (3, 50000000, 30)], [('lvl', 1)]), 'lvl')
ok &= case('d9 no row with draws >= 100 -> no first frame; the sum after the entry line counts rows after it only',
           d['first'] is None and d['dt_after_entry_us'] == 120000000)
d = S.derive(mem([(1, 20000, 100), (2, 16667, 3000), (4, 16667, 3000), (5, 16667, 3000)], [('lvl', 0)]), 'lvl')
ok &= case('d10 n gaps are counted', d['n_gaps'] == 1)
R4 = [(1, 20000, 100)] + [(2 + i, 16667, 3000) for i in range(20)] + [(30, 2000000, 3000), (31, 1500000, 3000)]
d = S.derive(mem(R4, [('lvl', 0)], quit=21), 'lvl')
ok &= case('d11 letter: rows after Event: quit and the last row count (K2 30, 31); variant vx: neither',
           [x[0] for x in d['k2']] == [30, 31] and d['vx']['k2'] == [] and d['vx']['frames_after_first'] == 20)
d = S.derive(mem([(1, 20000, 100)] + [(2 + i, 16667, 3000) for i in range(5)] + [(9, 500000, 3000)], [('lvl', 0)]), 'lvl')
ok &= case('d12 variant vx drops the last row of the log (a K3 there), the letter keeps it',
           d['k3w'] == [(9, 500000)] and d['vx']['k3w'] == [])

# ---------------- scan: chunk boundaries, markers, rows of the entry print
S.CHUNK = 37
lines = scene_lines('lvl', [16667] * 50) + [
    'AsyncPipelines: skipped draw DrawIndexAuto frame=193 vs=0x1 ps=0x0 pending=3 total_skipped=1',
    'AsyncPipelines: skipped draw DrawIndexAuto frame=193 vs=0x1 ps=0x0 pending=3 total_skipped=2',
    'AsyncPipelines: skipped draw DrawIndexAuto frame=197 vs=0x1 ps=0x0 pending=3 total_skipped=3',
    '=== Stubbed function, returning OK ===', '[12]\tsceVoiceChatFoo', 'PriorityStall: tick=1 unsub=1 us=50000 site=+0x1',
    'PriorityStall: tick=2 unsub=1 us=50001 site=+0x1', 'BvhLoopCapTrip: trips=+96 total=96 near=+0 near_total=0',
    '[Vulkan][W][2]: warn', '[Vulkan][E][3]: err', '--- Fatal Error ---', 'GpuHangAbort: requested=1']
p = BASE / 'scan1.txt'
p.write_bytes(('\n'.join(lines)).encode('utf-8'))           # no newline at the end: the last line still counts
sc = S.scan(str(p))
S.CHUNK = 1 << 26
ok &= case('s1 rows across chunk boundaries of 37 bytes (64 rows) and the sha of the file',
           len(sc['rows']) == 64 and sc['sha256'] == hashlib.sha256(p.read_bytes()).hexdigest())
ok &= case('s2 skipped draw lines 3, frames 2', sc['skip_lines'] == 3 and len(sc['skip_frames']) == 2)
ok &= case('s3 the stubbed function name is read from the next line', [n for n, _ in sc['stubs']] == ['sceVoiceChatFoo'])
ok &= case('s4 the last line without a newline is read (GpuHangAbort)', [k for k, _, _ in sc['hang']] == ['GpuHangAbort:'])
ok &= case('s5 --- Fatal Error --- is not also --- Error ---', [k for k, _, _ in sc['crash']] == ['--- Fatal Error ---'])
ok &= case('s6 [Vulkan][E] 1, [Vulkan][W] not counted; BvhLoopCapTrip 1', len(sc['vke']) == 1 and len(sc['bvh']) == 1)
p = BASE / 'scan2.txt'
p.write_bytes(('\n'.join([start('lvl'), 'FrameTrace: n=5 dt_us=20000 lat_us=1 gpu_proc=0', ft(6, 20000, 100),
                          'Event: quit', 'GpuHangAbort: requested=1', 'Event: quit', ft(7, 16667)]) + '\n').encode('utf-8'))
sc = S.scan(str(p))
d = S.derive(sc, 'lvl')
mk = S.markers(sc, None, d['entry_pos'], sc['quit'])
ok &= case('s7 a FrameTrace row without draws= is never the first scene frame; the first Event: quit is the exit line',
           d['first'] == (6, 20000, 100) and len(mk) == 1 and mk[0]['at_exit']
           and sc['quit'] == p.read_bytes().find(b'Event: quit'))

# ---------------- entry_of on files: every per-entry row
OPS = ['CsPretranslate: skipped hash=1 reason=x unsupported family=SOP1 opcode=0x21 raw=[0x1] reason=SOP1 opcode is not '
       'implemented'] * 96 + ['x unsupported family=SOP1 opcode=0x0C raw=[0x1] reason=SOP1 opcode is not implemented'] + \
      ['x unsupported family=VOPC opcode=0xe3 raw=[0x1] reason=VOPC opcode is not implemented'] * 4
cl = [ft(i, 16667) for i in range(1, 7300)]
root = BASE / 'e1'
mkrun(root, 'c142_01', OPS[:12] + scene_lines('bumper_enemy_snowy_canyon', [16667] * 7300) + OPS[12:] + lines[-12:-2])
e = ent(root, 'c142_01')
ok &= case('e1 a census entry: admitted, entered, HOLDS_120', all(a[1] for a in e['admit']) and e['outcome'] == 'HOLDS_120')
ok &= case('e2 opcode profile 96/1/4 (case of the hex folded) -> equal', e['ops']['profile_equal'] and e['ops']['total'] == 101)
ok &= case('e3 PriorityStall: us 50000 is not > 50 ms, 50001 is', e['prio']['over'] == 1 and e['prio']['max'] == 50001)
ok &= case('e4 per-entry rows: 3 skipped draw lines, 1 stub, 1 BvhLoopCapTrip, 1 [Vulkan][E] (census: not a gate)',
           e['skip']['lines'] == 3 and e['stubs'] == ['sceVoiceChatFoo'] and e['bvh'] == 1 and e['vke'] == 1)
root = BASE / 'e5'
mkrun(root, 'c142_01', OPS[:90] + ['x family=VOP2 opcode=0x3b reason=VOP2 opcode is not implemented'] +
      scene_lines('bumper_enemy_snowy_canyon', [16667] * 7300) + OPS[90:] + OPS[0:1])
e = ent(root, 'c142_01')
dd = dict(((x[0], x[1]), x) for x in e['ops']['diff'])
ok &= case('e5 opcode difference: SOP1 0x21 96 (90+6+1 = 97, +1; after entry 7), a new VOP2 0x3b +1',
           not e['ops']['profile_equal'] and dd[('SOP1', '0x21')][2:] == (97, 96, 1, 7) and dd[('VOP2', '0x3b')][4] == 1
           and ('SOP1', '0x0c') not in dd)

root = BASE / 'e5b'
mkrun(root, 'c142_01', OPS[:95] + scene_lines('bumper_enemy_snowy_canyon', [16667] * 7300) + OPS[96:97])
e = ent(root, 'c142_01')
dd = dict(((x[0], x[1]), x) for x in e['ops']['diff'])
ok &= case('e5b opcode difference: SOP1 0x21 95 (-1), VOPC 0xe3 absent (-4), SOP1 0x0c equal',
           dd.get(('SOP1', '0x21'), (0,) * 6)[4] == -1 and dd.get(('VOPC', '0xe3'), (0,) * 6)[2:5] == (0, 4, -4)
           and ('SOP1', '0x0c') not in dd)

# ---------------- the census outcome and its edges
def census(name, post, **kw):
    root = BASE / name
    lvl = 'bumper_enemy_snowy_canyon'
    mkrun(root, 'c142_01', kw.pop('lines', None) or scene_lines(lvl, post, **kw.pop('sl', {})), **kw)
    return ent(root, 'c142_01')


# after the entry line: the loading rows 1.5 s + 0.02 s, the first frame 2 s, then post
base_us = 1500000 + 20000 + 2000000
e = census('o1', [16667] * 6985 + [120000000 - base_us - 16667 * 6985])
ok &= case('o1 sum dt after the entry line = 120 000 000 -> HOLDS_120', e['derive']['dt_after_entry_us'] == 120000000
           and e['outcome'] == 'HOLDS_120')
e = census('o1b', [16667] * 6985 + [120000000 - base_us - 16667 * 6985 - 1])
ok &= case('o1b one us less -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
LONG = [16667] * 7300
for i, (mk, cls) in enumerate(((b'Unhandled exception: 0xc0000005', 'K1'), (b'--- Fatal Error ---', 'K1'),
                               (b'--- Error ---', 'K1'), (b'GpuHangAbort: requested=6000', 'K2'),
                               (b'[Vulkan] ErrorDeviceLost', 'K2'))):
    e = census('o2_%d' % i, None, lines=scene_lines('bumper_enemy_snowy_canyon', LONG) + [mk.decode()])
    ok &= case('o2 death marker %s in the log -> %s' % (mk.decode()[:20], cls), e['outcome'] == cls and len(e['marks']) == 1)
    e = census('o3_%d' % i, LONG, stdout_lines=[mk.decode()])
    ok &= case('o3 death marker %s in the emulator stdout -> %s' % (mk.decode()[:20], cls), e['outcome'] == cls)
e = census('o4', LONG, js=js_for('c142_01', attempt=dict(hold_exit=3221225477)))
ok &= case('o4 hold_exit set -> K1', e['outcome'] == 'K1')
e = census('o5', LONG, es_lines=['WARNING: the game ENDED inside the hold after 50.0 s, returncode 1 (0x00000001)'])
ok &= case('o5 the ENDED line of enter_scene -> K1', e['outcome'] == 'K1' and e['ended'])
e = census('o6', LONG, js=js_for('c142_01', attempt=dict(outcome='exited', hold_s=None, ft_tail=None)))
ok &= case('o6 an attempt that exited before stable -> K1', e['outcome'] == 'K1')
e = census('o7', LONG, js=js_for('c142_01', attempt=dict(ft_tail=0)))
ok &= case('o7 ft_tail 0 at the end of the hold -> K2 (tail stall)', e['outcome'] == 'K2' and e['tail_stall'])
e = census('o7b', LONG, js=js_for('c142_01', attempt=dict(ft_tail=None, hold_s=None, outcome='timeout')))
ok &= case('o7b ft_tail None -> no tail stall; timeout of enter_scene is not a marker', not e['tail_stall']
           and e['outcome'] == 'HOLDS_120')
e = census('o7c', LONG, js=js_for('c142_01', attempt=dict(ft_tail=0, hold_s=None, outcome='timeout')))
ok &= case('o7c ft_tail 0 without a hold (hold_s None) -> no tail stall', not e['tail_stall'] and e['outcome'] == 'HOLDS_120')
e = census('o7d', LONG, js=js_for('c142_01', attempt=dict(ft_tail=None)))
ok &= case('o7d ft_tail None with a hold -> no tail stall', not e['tail_stall'] and e['outcome'] == 'HOLDS_120')
e = census('o8', [16667] * 100 + [1000000] + [16667] * 7300)
ok &= case('o8 a frame dt 1 s after the first scene frame -> K2', e['outcome'] == 'K2')
e = census('o9', None, lines=[ft(i, 16667) for i in range(1, 9000)] + ['--- Error ---'])
ok &= case('o9 no entry line -> NOT_ENTERED, key = the first marker', e['outcome'] == 'NOT_ENTERED' and
           e['key'] == '--- Error ---')
e = census('o9b', None, lines=[ft(i, 16667) for i in range(1, 9000)],
           js=js_for('c142_01', attempt=dict(outcome='timeout', hold_s=None)))
ok &= case('o9b no entry line, no marker -> key attempt:timeout', e['key'] == 'attempt:timeout')
e = census('o10', None, lines=scene_lines('bumper_enemy_snowy_canyon', LONG) + ['Event: quit', '--- Fatal Error ---'])
ok &= case('o10 a marker after Event: quit: letter K1, variant vx HOLDS_120, flagged at exit',
           e['outcome'] == 'K1' and e['outcome_vx'] == 'HOLDS_120' and e['marks'][0]['at_exit'])
e = census('o11', None, lines=[start('bumper_enemy_snowy_canyon')] + [ft(i, 50000, 20) for i in range(1, 3000)])
ok &= case('o11 entered without a scene frame -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
e = census('o12', LONG, log=False)
ok &= case('o12 a made run without its log -> NOT_ENTERED', e['outcome'] == 'NOT_ENTERED' and not e['log_present'])

# ---------------- admission
def adm(tag, **over):
    js = js_for(tag)
    for k, v in over.items():
        if k == 'env_del':
            for x in v:
                js['env'].pop(x, None)
        elif k == 'env_set':
            js['env'].update(v)
        elif k == 'attempt':
            js['attempts'][0].update(v)
        else:
            js[k] = v
    return S.admit(tag, js, PRED_SHA)


ok &= case('a1 good jsons of V, W and a census tag are admitted', all(all(a[1] for a in adm(t)) for t in ('v142', 'w142', 'c142_05')))
BAD = [('two attempts', 'v142', dict(attempts=[dict(label='attempt 1'), dict(label='attempt 2')])),
       ('a warmup', 'v142', dict(attempts=[dict(label='warmup')])),
       ('another build', 'v142', dict(binary_sha256=OTHER)),
       ('another level', 'c142_02', dict(guest_args='-lvl bumper_enemy_snowy_canyon')),
       ('a non-empty gate file', 'v142', dict(gates='rtskip=1')),
       ('no clock pin', 'v142', dict(env_del=['KYTY_GPU_CLOCK_PIN'])),
       ('markers 1', 'v142', dict(env_set={'KYTY_GPU_MARKERS': '1'})),
       ('checkpoints', 'v142', dict(env_set={'KYTY_GPU_CHECKPOINTS': '0'})),
       ('a schedule', 'c142_01', dict(env_set={'KYTY_GATE_SCHEDULE': '90:a|b'})),
       ('ABBA', 'c142_01', dict(env_set={'KYTY_GATE_SCHEDULE_ABBA': '1'})),
       ('no video in the census', 'c142_03', dict(env_del=['KYTY_REC'])),
       ('a video of another tag', 'v142', dict(env_set={'KYTY_REC': 'C:/kyty/s142/rec_w142.mp4'})),
       ('a video in W', 'w142', dict(env_set={'KYTY_REC': 'C:/kyty/s142/rec_w142.mp4'})),
       ('validation in V', 'v142', dict(cmdline=['e', '--vulkan-validation', 'false', '--vulkan-validation', 'true'])),
       ('no validation in W', 'w142', dict(cmdline=['e', '--vulkan-validation', 'true', '--vulkan-validation', 'false'])),
       ('no VK_LAYER_PATH in W', 'w142', dict(env_del=['VK_LAYER_PATH'])),
       ('another seal sha', 'v142', dict(prereg=dict(path=S.PRED_PATH, sha256='cd' * 32))),
       ('another seal path', 'v142', dict(prereg=dict(path='C:/kyty/s140/pred/01_sc142.md', sha256=PRED_SHA))),
       ('no prereg', 'v142', dict(prereg=None)),
       ('a pipeline-cache retry', 'v142', dict(attempt=dict(pipeline_cache_off=True)))]
for name, tag, over in BAD:
    ok &= case('a2 refused: %s' % name, not all(a[1] for a in adm(tag, **over)))
ok &= case('a3 the last --vulkan-validation value counts (false then true = W)',
           S.last_value(['--vulkan-validation', 'false', '--vulkan-validation', 'true'], '--vulkan-validation') == 'true')
ok &= case('a4 a seal sha None refuses', not all(a[1] for a in S.admit('v142', js_for('v142'), None)))
ok &= case('a4b a seal sha None and a prereg without sha refuses',
           not all(a[1] for a in S.admit('v142', js_for('v142', prereg=dict(path=S.PRED_PATH)), None)))

# ---------------- SCENE_OK
W_LINES = scene_lines(SKY, [150000] * 2000) + ['[Vulkan][W][2]: vkCmdDrawIndexed(): warn'] * 3


def pair(name, v_lines=None, w_lines=None, v_js=None, w_js=None, v_glitch=(3200, 0), w_extra=(), v_std=(), w_es=()):
    root = BASE / name
    mkrun(root, 'v142', v_lines if v_lines is not None else scene_lines(SKY, v_post()), js=v_js, glitch=v_glitch,
          stdout_lines=v_std)
    mkrun(root, 'w142', (w_lines if w_lines is not None else W_LINES) + list(w_extra), js=w_js, glitch=None, sheet=False,
          es_lines=w_es)
    return ent(root, 'v142'), ent(root, 'w142')


v, w = pair('k1')
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k1 every condition true (sum after the first frame = 300 000 000, 3 100 frames, first frame 2 s out) + sheet '
           'viewed -> YES', word == 'YES' and v['derive']['dt_after_first_us'] == 300000000 and all(r[1] for r in rows))
ok &= case('k1b the sheet row unfilled -> PENDING_SHEET', S.scene_ok(v, w, None)[0] == 'PENDING_SHEET')
ok &= case('k1c the sheet row not-viewed -> NO', S.scene_ok(v, w, 'not-viewed')[0] == 'NO')
ok &= case('k1d W with [Vulkan][W] only and slow frames (dt rule not applied to W) is fine', w['vke'] == 0)
word, rows = S.scene_ok(None, w, 'viewed')
ok &= case('k2 V missing -> NO, the V row fails', word == 'NO' and row_ok(rows, 'V made') is False)
word, rows = S.scene_ok(v, None, 'viewed')
ok &= case('k2b W missing -> NO, the W row fails', word == 'NO' and row_ok(rows, 'W made') is False)


def fails(name, want_row, **kw):
    v, w = pair(name, **kw)
    word, rows = S.scene_ok(v, w, 'viewed')
    return word == 'NO' and row_ok(rows, want_row) is False and sum(1 for r in rows if not r[1]) == 1


ok &= case('k3 V not admitted (another build)', fails('k3', 'V admitted', v_js=js_for('v142', binary_sha256=OTHER)))
v, w = pair('k4', v_lines=[ft(i, 96774) for i in range(1, 3200)])
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k4 V not entered -> NO, the entry row fails', word == 'NO' and row_ok(rows, 'V entered') is False)
ok &= case('k5 V a death marker in the emulator stdout', fails('k5', 'V 0 death markers', v_std=['ErrorDeviceLost']))
ok &= case('k6 V hold_exit', fails('k6', 'V 0 death markers', v_js=js_for('v142', attempt=dict(hold_exit=1))))
P = v_post()
P[1500] = 1000000
ok &= case('k7 V a frame dt 1 s after the first scene frame', fails('k7', 'V no frame dt >= 1 s', v_lines=scene_lines(SKY, P)))
ok &= case('k7b V first frame dt 5 s is out of the rule', S.scene_ok(*pair('k7b', v_lines=scene_lines(SKY, v_post(),
           first_dt=5000000)), sheet='viewed')[0] == 'YES')
ok &= case('k8 V tail stall', fails('k8', 'V no frame dt >= 1 s', v_js=js_for('v142', attempt=dict(ft_tail=0))))
ok &= case('k9 V sum after the first frame 299 999 999', fails('k9', 'V sum dt_us', v_lines=scene_lines(SKY, v_post(299999999))))
v, w = pair('k10', v_lines=scene_lines(SKY, v_post(count=3000)))
v2, w2 = pair('k10b', v_lines=scene_lines(SKY, v_post(count=2999, total=300000000 - 0)))
ok &= case('k10 V 3 000 frames after the first frame pass the frame row, 2 999 fail it',
           row_ok(S.scene_ok(v, w, 'viewed')[1], 'V >= 3000') is True and row_ok(S.scene_ok(v2, w2, 'viewed')[1], 'V >= 3000') is False)
ok &= case('k11 V one glitch', fails('k11', 'V 0 one-frame', v_glitch=(3200, 1)))
ok &= case('k11b V glitch file missing', fails('k11b', 'V 0 one-frame', v_glitch=None))
v, w = pair('k11c')
Path(BASE / 'k11c' / 'glitch_v142.txt').write_text('C:/kyty/s142/rec_v142.mp4: 3200 frames 960x540, index entries 3200\n')
v = ent(BASE / 'k11c', 'v142')
ok &= case('k11c V glitch file without the glitch line -> the glitch row fails',
           v['glitch'] is None and row_ok(S.scene_ok(v, w, 'viewed')[1], 'V 0 one-frame') is False)
ok &= case('k12 W one [Vulkan][E] line', fails('k12', 'W 0 [Vulkan][E]', w_extra=['[Vulkan][E][5]: vkQueueSubmit(): bad']))
root = BASE / 'k12b'
mkrun(root, 'v142', scene_lines(SKY, v_post()))
mkrun(root, 'w142', W_LINES, glitch=None, sheet=False, stdout_lines=['[Vulkan][E][5]: in the stdout'])
ok &= case('k12b W one [Vulkan][E] line in the emulator stdout -> the row fails',
           row_ok(S.scene_ok(ent(root, 'v142'), ent(root, 'w142'), 'viewed')[1], 'W 0 [Vulkan][E]') is False)
ok &= case('k13 W stopped early by the validation (hold_exit, hold_s 42): hold row and marker row fail',
           S.scene_ok(*pair('k13', w_js=js_for('w142', attempt=dict(hold_exit=1, hold_s=42.0))), sheet='viewed')[0] == 'NO')
ok &= case('k13b W hold_s 299.9 -> the hold row fails', fails('k13b', 'W hold reached', w_js=js_for('w142', attempt=dict(hold_s=299.9))))
ok &= case('k13c W hold_s 300.0 -> passes', S.scene_ok(*pair('k13c', w_js=js_for('w142', attempt=dict(hold_s=300.0))),
                                                          sheet='viewed')[0] == 'YES')
ok &= case('k13d W timeout of the entry -> the hold row fails', fails('k13d', 'W hold reached',
           w_js=js_for('w142', attempt=dict(outcome='timeout', hold_s=None))))
ok &= case('k13e W ENDED line -> death and hold rows fail', S.scene_ok(*pair('k13e', w_es=['WARNING: the game ENDED inside '
           'the hold after 9.0 s, returncode 1 (0x00000001)']), sheet='viewed')[0] == 'NO')
root = BASE / 'k14'
mkrun(root, 'v142', scene_lines(SKY, v_post()))
mkrun(root, 'w142', W_LINES, log=False, glitch=None, sheet=False)
word, rows = S.scene_ok(ent(root, 'v142'), ent(root, 'w142'), 'viewed')
ok &= case('k14 W without its log -> NO: not entered and the [Vulkan][E] row fails (no count without a log)',
           word == 'NO' and row_ok(rows, 'W entered') is False and row_ok(rows, 'W 0 [Vulkan][E]') is False)
ok &= case('k15 W death marker', fails('k15', 'W 0 death markers', w_extra=['GpuHangAbort: requested=6000']))

# ---------------- the stop rule of item 221 (g)(4)
NE = 'NOT_ENTERED'
ok &= case('t1 three in a row not entered with one marker -> stop',
           S.stop_check([('a', NE, 'x'), ('b', NE, 'x'), ('c', NE, 'x')]) == (True, ['a', 'b', 'c']))
ok &= case('t2 two -> no stop', S.stop_check([('a', NE, 'x'), ('b', NE, 'x')])[0] is False)
ok &= case('t3 three with different markers -> no stop', S.stop_check([('a', NE, 'x'), ('b', NE, 'y'), ('c', NE, 'x')])[0] is False)
ok &= case('t4 broken by an entered level -> no stop',
           S.stop_check([('a', NE, 'x'), ('b', 'HOLDS_120', None), ('c', NE, 'x'), ('d', NE, 'x')])[0] is False)
ok &= case('t5 a different marker then three alike -> stop on the last three',
           S.stop_check([('a', NE, 'y'), ('b', NE, 'x'), ('c', NE, 'x'), ('d', NE, 'x')]) == (True, ['b', 'c', 'd']))
root = BASE / 't6'
for t in ('c142_01', 'c142_02', 'c142_03'):
    mkrun(root, t, [ft(i, 16667) for i in range(1, 50)], js=js_for(t, attempt=dict(outcome='timeout', hold_s=None)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc6 = S.main(['--stop-check', 'c142_04'], root=str(root), pred=str(BASE / 'nopred.md'))
    rc6b = S.main(['--stop-check', 'c142_03'], root=str(root), pred=str(BASE / 'nopred.md'))
    rc6c = S.main(['--stop-check', 'zz'], root=str(root), pred=str(BASE / 'nopred.md'))
ok &= case('t6 main --stop-check: before c142_04 three timeouts -> rc 5; before c142_03 two -> rc 0; unknown tag -> rc 2',
           rc6 == 5 and rc6b == 0 and rc6c == 2)

# ---------------- the seal check
root = BASE / 'seal'
root.mkdir()
shutil.copyfile(SRC, root / 'sc142.py')
lines_seal = []
for name in S.SEALED_NAMES:
    if name.startswith('C:/'):
        sh = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    elif name != 'sc142.py':
        (root / name).write_bytes(('fixture ' + name).encode())
        sh = hashlib.sha256((root / name).read_bytes()).hexdigest()
    else:
        sh = hashlib.sha256(Path(SRC).read_bytes()).hexdigest()
    lines_seal.append('seal: %s %s' % (sh, name))
PRED = root / 'pred.md'
PRED.write_text('seal fixture\n' + '\n'.join(lines_seal) + '\n', encoding='utf-8')
good, rows = S.check_seal(str(PRED), str(root), SRC)
ok &= case('e6 the seal check passes on every sha line (scorer included)', good and len(rows) == len(S.SEALED_NAMES) + 1)
(root / 'go142a.sh').write_bytes(b'changed')
ok &= case('e7 a changed sealed file fails the seal check', S.check_seal(str(PRED), str(root), SRC)[0] is False)
(root / 'go142a.sh').write_bytes(b'fixture go142a.sh')
PRED.write_text('seal fixture\n' + '\n'.join(x for x in lines_seal if not x.endswith(' mut_sc142.py')) + '\n', encoding='utf-8')
ok &= case('e8 a sealed name without its line fails', S.check_seal(str(PRED), str(root), SRC)[0] is False)
PRED.write_text('seal fixture\n' + '\n'.join(lines_seal) + '\n', encoding='utf-8')
other = root / 'other_scorer.py'
other.write_bytes(b'# another scorer')
ok &= case('e9 a scorer whose sha is not the seal line fails', S.check_seal(str(PRED), str(root), str(other))[0] is False)
ok &= case('e10 a missing seal file fails', S.check_seal(str(root / 'none.md'), str(root), SRC)[0] is False)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rcs = S.main(['--check-seal'], root=str(root), pred=str(PRED))
ok &= case('e11 main --check-seal on a good seal -> rc 0, SEAL: PASS', rcs == 0 and 'SEAL: PASS' in buf.getvalue())
(root / 'go142a.sh').write_bytes(b'changed again')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rcs2 = S.main(['--check-seal'], root=str(root), pred=str(PRED))
ok &= case('e12 main --check-seal on a broken seal -> rc 1, SEAL: FAIL', rcs2 == 1 and 'SEAL: FAIL' in buf.getvalue())

# ---------------- the calibration logic on synthetic logs (the real ones: sc142.py --calib)
cal = BASE / 'cal'
cal.mkdir()
W599 = [16667] * 700


def cal_log(name, lines):
    p = cal / name
    p.write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    return str(p)


def post_at(pairs, count=900):
    rows = [16667] * count
    for i, dt in pairs:
        rows[i] = dt
    return rows


# first frame n 14; post row i has n 15 + i
S.CALIB = (('eatl122', cal_log('a', scene_lines('pa', post_at([(176, 1391088), (177, 116791)]))), 'pa'),
           ('edes122', cal_log('b', scene_lines('in', post_at([(4930, 23796476)], 5000))), 'in'),
           ('atl122', cal_log('c', scene_lines('pa', post_at([(10, 95006)]))), 'pa'),
           ('ednn122', cal_log('d', scene_lines('dn', post_at([(1811, 118647)], 2000))), 'dn'),
           ('eght122', cal_log('e', scene_lines('gh', post_at([(374, 263946)]))), 'gh'))
n, cl = S.calib()
ok &= case('c1 calibration logic 5 of 5 on synthetic forms (K2 191 entry, K2 4945 hold, none, K3 hold 1826, K3 window 389)',
           n == 5 and cl[-1] == 'CALIB 5 of 5')
S.CALIB = S.CALIB[:2] + (('atl122', cal_log('c2', scene_lines('pa', post_at([(10, 100000)]))), 'pa'),) + S.CALIB[3:]
n, cl = S.calib()
ok &= case('c2 a K3 in the atl122 form -> 4 of 5', n == 4)
S.CALIB = (('eatl122', cal_log('a2', scene_lines('pa', post_at([(700, 1391088)]))), 'pa'),)
ok &= case('c3 eatl122 form with K2 on the hold -> fails', S.calib()[0] == 0)


def renum(lines, idx, n):
    """the post row idx (0-based after the first scene frame) renumbered to n (derive does not need monotonic n)."""
    k = lines.index(ft(14, 2000000, 894)) + 1 + idx
    parts = lines[k].split(' ', 2)
    lines[k] = 'FrameTrace: n=%d %s' % (n, parts[2])
    return lines


BADCAL = (('eatl122', renum(scene_lines('pa', post_at([(700, 1391088)])), 700, 191), 'pa'),
          ('edes122', scene_lines('in', post_at([(4930 - 4930 + 100, 23796476)], 5000)), 'in'),
          ('atl122', scene_lines('pa', post_at([(700, 100000)])), 'pa'),
          ('ednn122', scene_lines('dn', post_at([(1811, 118647), (20, 100000)], 2000)), 'dn'),
          ('eght122', scene_lines('gh', post_at([(375, 263946)])), 'gh'))
BADCAL = tuple((t, renum(l, 100, 4945) if t == 'edes122' else l, lv) for t, l, lv in BADCAL)
res = []
for i, (t, l, lv) in enumerate(BADCAL):
    S.CALIB = ((t, cal_log('bad%d' % i, l), lv),)
    res.append(S.calib()[0])
ok &= case('c4 each calibration form fails on its near miss (eatl K2 191 on the hold; edes K2 4945 in the window; atl K3 on '
           'the hold; ednn K3 in the window; eght K3 at 390 not 389)', res == [0, 0, 0, 0, 0])

# ---------------- main: one tag, the summary, the forms B5a / B5, ASCII in strict cp1250
root = BASE / 'm'
mkrun(root, 'v142', scene_lines(SKY, v_post()))
mkrun(root, 'w142', W_LINES, glitch=None, sheet=False)
mkrun(root, 'c142_01', scene_lines('bumper_enemy_snowy_canyon', [16667] * 100 + [1200000] + [16667] * 7300))
mkrun(root, 'c142_02', scene_lines('big_hand_pirate_island', [16667] * 50 + [150000] + [16667] * 7300))
mkrun(root, 'c142_03', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_03', attempt=dict(outcome='timeout')))
mkrun(root, 'c142_04', scene_lines('mini_giants_garden', [16667] * 500 + [150000] + [16667] * 7000),
      js=js_for('c142_04', binary_sha256=OTHER))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rcm = S.main(['--tag', 'c142_01'], root=str(root), pred=str(BASE / 'nopred.md'))
    rcm4 = S.main(['--tag', 'c142_04'], root=str(root), pred=str(BASE / 'nopred.md'))
    rcm5 = S.main(['--tag', 'c142_05'], root=str(root), pred=str(BASE / 'nopred.md'))
    rcm6 = S.main(['--tag', 'x'], root=str(root), pred=str(BASE / 'nopred.md'))
    rcu = S.main([], root=str(root), pred=str(BASE / 'nopred.md'))
out1 = buf.getvalue()
sj = json.loads((root / 'runs142' / 'c142_01.score.json').read_text(encoding='utf-8'))
ok &= case('m1 main --tag: the score json carries the outcome K2; rc 1 without the seal (prereg), not admitted rc 1, '
           'NO_RUN rc 1, unknown tag rc 2, no mode rc 2', sj['outcome'] == 'K2' and rcm == 1 and rcm4 == 1 and rcm5 == 1
           and rcm6 == 2 and rcu == 2 and 'NO_RUN' in out1)
PRM = root / 'pred.md'
PRM.write_text('fixture\n', encoding='utf-8')
for t in ('v142', 'w142', 'c142_01', 'c142_02', 'c142_03', 'c142_04'):
    j = json.loads((root / ('%s.json' % t)).read_text(encoding='utf-8'))
    j['prereg']['sha256'] = hashlib.sha256(PRM.read_bytes()).hexdigest()
    (root / ('%s.json' % t)).write_text(json.dumps(j), encoding='utf-8')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rca = S.main(['--tag', 'c142_02'], root=str(root), pred=str(PRM))
    rcsum = S.main(['--summary'], root=str(root), pred=str(PRM))
    rcsum2 = S.main(['--summary', '--sheet', 'viewed'], root=str(root), pred=str(PRM))
out2 = buf.getvalue()
ok &= case('m2 an admitted census tag -> rc 0; the K3 of its window is printed with "no warm base"',
           rca == 0 and 'K3 entry window (no warm base): [(65, 150000)]' in out2)
ok &= case('m3 summary: SCENE_OK PENDING_SHEET without the sheet row, YES with it', rcsum == 0 and rcsum2 == 0 and
           'SCENE_OK underwater_aerial_garden: PENDING_SHEET' in out2 and 'SCENE_OK underwater_aerial_garden: YES' in out2)
ok &= case('m4 summary: FORM B5a 1/10 (c142_01), FORM B5 2/10 (c142_01 K2 in the window, c142_02; c142_04 of another '
           'build is not admitted and not counted), census made 4, admitted 3',
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 1/10 [c] (admitted and entered 2)' in out2 and
           'FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): 2/10 [c] (admitted and entered 2)' in out2
           and 'CENSUS made 4 of 10, admitted 3' in out2)
ok &= case('m5 summary: the tags not made are printed', 'TAG c142_05: not made' in out2)
try:
    (out1 + out2).encode('cp1250', errors='strict')
    (out1 + out2).encode('ascii', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('m6 every printed line is ASCII (strict cp1250 and ascii)', enc)
ok &= case('m7 the constants: 10 census levels in the order of item 221 (g)(1); V, W first', S.SEQ[:2] == ('v142', 'w142')
           and [lv for _, lv in S.CENSUS] == ['bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino',
                                               'mini_giants_garden', 'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach',
                                               'volcano_mountain', 'voxel_world', 'enemy_gorilla'])
ok &= case('m8 the build is 9235a7ac and the seal path is s142', S.BUILD_SHA == BUILD and S.PRED_PATH == 'C:/kyty/s142/pred/01_sc142.md')
# ---------------- added after the counted full mutlib run (add-only; survivors sealed_vid, sk_w_ok, su_b5a)
REQUIRED = ('go142a.sh', 'sc142.py', 'test_sc142.py', 'mut_sc142.py', 'enter_scene.py', 'C:/kyty/scripts/s51_vidglitch.py')
ok &= case('x1 the seal must name the harness, the scorer, the fixtures, the mutants, enter_scene.py and s51_vidglitch.py '
           '(item 221 (g)(4))', all(n in S.SEALED_NAMES for n in REQUIRED))
ok &= case('x2 W with an attempt outcome other than ok -> the hold row fails even with hold_s 310',
           fails('x2', 'W hold reached', w_js=js_for('w142', attempt=dict(outcome='timeout', hold_s=310.0))))
root = BASE / 'x3'
PRX = root / 'pred.md'
mkrun(root, 'c142_01', scene_lines('bumper_enemy_snowy_canyon', [16667] * 100 + [1200000] + [16667] * 7300))
mkrun(root, 'c142_02', scene_lines('big_hand_pirate_island', [16667] * 50 + [150000] + [16667] * 7300))
mkrun(root, 'c142_06', scene_lines('sponge_dirty_bath', [16667] * 700 + [1200000] + [16667] * 7300))
PRX.write_text('fixture\n', encoding='utf-8')
for t in ('c142_01', 'c142_02', 'c142_06'):
    j = json.loads((root / ('%s.json' % t)).read_text(encoding='utf-8'))
    j['prereg']['sha256'] = hashlib.sha256(PRX.read_bytes()).hexdigest()
    (root / ('%s.json' % t)).write_text(json.dumps(j), encoding='utf-8')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    S.main(['--summary'], root=str(root), pred=str(PRX))
out3 = buf.getvalue()
ok &= case('x3 forms: B5a 2/10 (K2 in the window c142_01, K2 on the hold c142_06), B5 2/10 (c142_01, K3 in the window c142_02)',
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 2/10 [c] (admitted and entered 3)' in out3 and
           'FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): 2/10 [c] (admitted and entered 3)' in out3)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
