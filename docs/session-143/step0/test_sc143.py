"""Offline fixtures of sc143.py (session 143 step 0, HPP-297; ROADMAP s122 item 231 (i)(1)-(4)).  PART A: the whole suite of
sc142.py (test_sc142.py of link 1b, every case unchanged) run on sc143.py in PROFILE 142 (sc143.profile(sc143.P142): the tags,
seal, chain name and roots of session 142) - the reading of sc142 after item 224 holds in the ported code.  PART B (at the
end): the profile of session 143 - the new terms and edges of item 231 (i).
Session 142 header of PART A: offline fixtures of sc142.py (the scorer of the scene census sc142 and of SCENE_OK on Sky Garden; session 142 step 0,
HPP-277; link 1b HPP-282: the RC1-RC10 terms of item 224 (a) in the block "link 1b" at the end; ROADMAP s122 item 221 (v), (g)(2)-(4), items 215 (v)(2), 217 (b), 218 (g)-(d)).  One case per condition and per
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
    python C:/kyty/s143/test_sc143.py [<sc143 under test>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import hashlib as _h
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc143.py')
print('suite test_sc143.py sha256 %s target sc143.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc143_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
P143 = S.profile(S.P142)     # PART A runs in profile 142; PART B restores the profile of session 143

BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
OTHER = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
SKY = 'underwater_aerial_garden'
PRED_SHA = 'ab' * 32
BASE = Path('C:/kyty/s143/fx_sc143')   # mutlib gives every job its own copy of this directory
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


def mkrun(root, tag, lines, js=None, stdout_lines=(), es_lines=(), glitch=(3200, 0), sheet=True, log=True, stdout=True):
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
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        (root / 'step2').mkdir(exist_ok=True)
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-09-30T00:00:00Z go142a %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\n' % (
                tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-09-30T00:00:00Z go142a %s sheet rc 0 sheet_%s.png sha256 %s\n' % (
                tag, tag, _h.sha256(b'png').hexdigest()))
    if not stdout:
        (root / ('stdout_%s.txt' % tag)).unlink()
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
e = census('o7c', LONG, js=js_for('c142_01', attempt=dict(ft_tail=0, hold_s=None, outcome='timeout')))
ok &= case('o7c ft_tail 0 without a hold (hold_s None) -> no tail stall; no stable -> NOT_EVALUABLE (item 224 (a)(4))',
           not e['tail_stall'] and e['outcome'] == 'NOT_EVALUABLE')
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
VF = 'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features, version = 2'
VW = '[Vulkan][W][2]: vkCmdDrawIndexed(): warn'
W_BASE = scene_lines(SKY, [150000] * 2000)
W_LINES = [VF] + W_BASE + [VW] * 3


def pair(name, v_lines=None, w_lines=None, v_js=None, w_js=None, v_glitch=(3200, 0), w_extra=(), v_std=(), w_es=(),
         w_std=(), v_es=()):
    root = BASE / name
    mkrun(root, 'v142', v_lines if v_lines is not None else scene_lines(SKY, v_post()), js=v_js, glitch=v_glitch,
          stdout_lines=v_std, es_lines=v_es)
    mkrun(root, 'w142', (w_lines if w_lines is not None else W_LINES) + list(w_extra), js=w_js, glitch=None, sheet=False,
          es_lines=w_es, stdout_lines=w_std)
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
v, w = pair('k6', v_js=js_for('v142', attempt=dict(hold_exit=1)))
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k6 V hold_exit -> the death row and the attempt row (item 224 (a)(4)) fail', word == 'NO' and
           row_ok(rows, 'V 0 death markers') is False and row_ok(rows, 'V attempt ok') is False
           and sum(1 for r in rows if not r[1]) == 2)
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
v, w = pair('k11b', v_glitch=None)
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('k11b V glitch file missing -> the glitch, video and coverage rows fail', word == 'NO' and
           row_ok(rows, 'V 0 one-frame') is False and row_ok(rows, 'V video >= 3000') is False and
           row_ok(rows, 'V video frames >=') is False and sum(1 for r in rows if not r[1]) == 3)
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
           and 'CENSUS made 4 of 10 (of them attempt made without json 0), admitted 3' in out2)
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
ok &= case('m8 the build is 9235a7ac and the seal path is s142', S.BUILD_SHA == BUILD and S.PRED_PATH == 'C:/kyty/s142/pred/02_sc142.md')
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
# ---------------- link 1b (HPP-282, item 224 (a)(1)-(10)): one case per new term and per edge
LV = 'bumper_enemy_snowy_canyon'
ok &= case('m8b the seal of link 1b is pred/02_sc142.md', S.PRED_PATH == 'C:/kyty/s142/pred/02_sc142.md')
ok &= case('b0 the check logs of item 224 (b)(2): s1s128, s2s128 of s128; s6s137 log and stdout of s137',
           S.CHECK_K2 == (('s1s128', 'C:/kyty/s128'), ('s2s128', 'C:/kyty/s128')) and S.CHECK_VAL ==
           ('s6s137', 'C:/kyty/s137/log_s6s137.txt', 'C:/kyty/s137/stdout_s6s137.txt'))
d = S.derive(mem([(1, 20000, 100), (2, 50, 3000), (3, 10, 3000), (4, 40, 3000), (5, 30, 3000), (6, 20, 3000)], [('lvl', 0)]), 'lvl')
ok &= case('f3 dt median and max after the first scene frame (10 20 30 40 50 -> 30, 50)', d['dt_median_us'] == 30
           and d['dt_max_us'] == 50)
# RC1: the outcome class by the FIRST death marker by position (item 224 (a)(1))
e = census('n1', None, lines=scene_lines(LV, LONG) + ['vkQueueSubmit failed: ErrorDeviceLost (-4)', '--- Fatal Error ---'],
           js=js_for('c142_01', attempt=dict(hold_exit=321)))
ok &= case('n1 ErrorDeviceLost -> --- Fatal Error --- + hold_exit -> K2 (the crash is the consequence), markers in order',
           e['outcome'] == 'K2' and [m['kind'] for m in e['marks']] == ['ErrorDeviceLost', '--- Fatal Error ---']
           and e['reason'].startswith('first death marker ErrorDeviceLost'))
e = census('n2', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1', '--- Error ---'],
           js=js_for('c142_01', attempt=dict(outcome='exited', hold_s=None, ft_tail=None)))
ok &= case('n2 GpuHangAbort: -> --- Error --- + exited -> K2', e['outcome'] == 'K2')
e = census('n3', None, lines=scene_lines(LV, LONG) + ['--- Error ---', 'GpuHangAbort: requested=1'])
ok &= case('n3 --- Error --- -> GpuHangAbort: -> K1', e['outcome'] == 'K1' and e['marks'][0]['kind'] == '--- Error ---')
e = census('n3b', None, lines=scene_lines(LV, LONG) + ['--- Fatal Error ---', 'vkWaitSemaphores failed: ErrorDeviceLost'])
ok &= case('n3b --- Fatal Error --- -> ErrorDeviceLost -> K1', e['outcome'] == 'K1')
e = census('n4', None, lines=scene_lines(LV, LONG) + ['--- Error ---'], stdout_lines=['GpuHangAbort: requested=1'])
ok &= case('n4 a crash in the log, a hang only in the stdout -> K1 (stdout markers after the log ones)',
           e['outcome'] == 'K1' and [m['src'] for m in e['marks']] == ['log', 'stdout'])
e = census('n4b', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1'], stdout_lines=['--- Fatal Error ---'])
ok &= case('n4b a hang in the log, a crash only in the stdout -> K2', e['outcome'] == 'K2')
e = census('n4c', LONG, stdout_lines=['GpuHangAbort: requested=1', '--- Fatal Error ---'])
ok &= case('n4c stdout only: hang then crash -> K2', e['outcome'] == 'K2')
e = census('n4d', LONG, stdout_lines=['--- Fatal Error ---', 'GpuHangAbort: requested=1'])
ok &= case('n4d stdout only: crash then hang -> K1', e['outcome'] == 'K1')
e = census('n5', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1'],
           es_lines=['WARNING: the game ENDED inside the hold after 9.0 s, returncode 1 (0x00000001)'])
ok &= case('n5 a hang in the log + the ENDED line (attempt markers after the log) -> K2', e['outcome'] == 'K2')
e = census('n6', None, lines=[ft(i, 16667) for i in range(1, 900)] + ['GpuHangAbort: requested=1', '--- Error ---'])
ok &= case('n6 not entered: the stop key is the first marker by position (GpuHangAbort:)', e['outcome'] == 'NOT_ENTERED'
           and e['key'] == 'GpuHangAbort:')
e = census('n6b', None, lines=[ft(i, 16667) for i in range(1, 900)] + ['--- Error ---'], stdout_lines=['GpuHangAbort: x'])
ok &= case('n6b not entered: a log crash before a stdout hang -> key --- Error ---', e['key'] == '--- Error ---')
out_n = '\n'.join(S.fmt_entry(census('n7', None, lines=scene_lines(LV, LONG) + ['GpuHangAbort: requested=1',
                                                                               '--- Error ---'])))
ok &= case('n7 the markers are printed in order with class, source and position',
           out_n.find('K2 GpuHangAbort: log@') < out_n.find('K1 --- Error --- log@') and out_n.find('K2 GpuHangAbort: log@') > 0)
e = census('n8', None, lines=scene_lines(LV, LONG) + ['Event: quit', 'GpuHangAbort: requested=1', '--- Error ---'])
ok &= case('n8 markers after Event: quit: letter K2 by the first, variant vx HOLDS_120', e['outcome'] == 'K2'
           and e['outcome_vx'] == 'HOLDS_120')
# RC2: the admission row of W "validation active" by three terms (item 224 (a)(2))


def w_lines(pre=(VF,), post=(VW,) * 3):
    return list(pre) + W_BASE + list(post)


ok &= case('v0 the W of k1 carries the admission row validation active and it passes; V has no such row',
           any(a[0].startswith('validation active') and a[1] for a in ent(BASE / 'k1', 'w142')['admit'])
           and not any(a[0].startswith('validation active') for a in ent(BASE / 'k1', 'v142')['admit']))
ok &= case('v1a a "no validation layer:" line -> W not admitted', fails('v1a', 'W admitted',
           w_lines=w_lines(pre=(VF, 'no validation layer: VK_LAYER_KHRONOS_validation'))))
ok &= case('v1b no VK_EXT_validation_features line -> W not admitted', fails('v1b', 'W admitted', w_lines=w_lines(pre=())))
ok &= case('v1c no [Vulkan][ line -> W not admitted', fails('v1c', 'W admitted', w_lines=w_lines(post=())))
ok &= case('v1d another extension of the layer only -> W not admitted', fails('v1d', 'W admitted', w_lines=w_lines(
           pre=('VK_LAYER_KHRONOS_validation available extension: VK_EXT_debug_utils, version = 1',))))
ok &= case('v1e "no validation layer:" in the W stdout -> W not admitted', fails('v1e', 'W admitted', w_std=[
           'no validation layer: VK_LAYER_KHRONOS_validation']))
v, w = pair('v1f', w_lines=W_BASE, w_std=[VF, VW])
ok &= case('v1f the layer lines in the W stdout count -> admitted, YES', S.scene_ok(v, w, 'viewed')[0] == 'YES'
           and w['val']['ok'])
ok &= case('v1g exactly one layer line and one [Vulkan][ line (the edges >= 1) -> YES',
           S.scene_ok(*pair('v1g', w_lines=w_lines(post=(VW,))), sheet='viewed')[0] == 'YES')
root = BASE / 'v1h'
mkrun(root, 'v142', scene_lines(SKY, v_post()))
mkrun(root, 'w142', w_lines(), log=False, glitch=None, sheet=False, stdout_lines=[VF, VW])
ok &= case('v1h W without its log -> validation not active even with the stdout lines',
           not ent(root, 'w142')['val']['ok'])
# RC3: the video length and the coverage (item 224 (a)(3))
ok &= case('r1 V video 2 999 frames -> the video row fails (coverage still holds)', fails('r1', 'V video >= 3000 frames',
           v_lines=scene_lines(SKY, [100000] * 3000), v_glitch=(2999, 0)))
ok &= case('r1b V video 3 000 frames -> YES', S.scene_ok(*pair('r1b', v_lines=scene_lines(SKY, [100000] * 3000),
                                                              v_glitch=(3000, 0)), sheet='viewed')[0] == 'YES')
v, w = pair('r2')
ok &= case('r2 the V log carries 3 114 FrameTrace rows', v['rows_total'] == 3114)
ok &= case('r2b V video 3 013 frames against 3 114 rows -> the coverage row fails', fails('r2b', 'V video frames >= FrameTrace',
           v_glitch=(3013, 0)))
ok &= case('r2c V video 3 014 frames against 3 114 rows -> YES', S.scene_ok(*pair('r2c', v_glitch=(3014, 0)),
                                                                          sheet='viewed')[0] == 'YES')
v, w = pair('r3')
Path(BASE / 'r3' / 'glitch_v142.txt').write_text('Traceback (most recent call last):\nValueError: invalid literal\n')
v = ent(BASE / 'r3', 'v142')
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('r3 an unreadable video (s51_vidglitch.py traceback) -> the video, coverage and glitch rows fail, NO',
           word == 'NO' and row_ok(rows, 'V video >= 3000') is False and row_ok(rows, 'V video frames >=') is False
           and row_ok(rows, 'V 0 one-frame') is False)
e = census('r4', LONG, glitch=(100, 0))
out_r = '\n'.join(S.fmt_entry(e))
ok &= case('r4 census: a failed coverage prints "glitches not conclusive" and does not change the outcome',
           e['outcome'] == 'HOLDS_120' and 'NO - glitches not conclusive' in out_r and not e['cover'])
root = BASE / 'r5'
mkrun(root, 'c142_01', scene_lines(LV, LONG))
(root / 'rec_c142_01.mp4.idx').write_bytes(b'0 1 0.10\n1 2 0.12\nbad line\n2 3 0.15\n')
e = ent(root, 'c142_01')
out_r = '\n'.join(S.fmt_entry(e))
ok &= case('r5 .idx records are counted (lines of >= 3 fields) and printed with the video and FrameTrace counts',
           e['idx'] == 3 and 'video: frames 3200, .idx records 3, FrameTrace rows in all %d, after the first scene frame %d'
           % (e['rows_total'], e['derive']['frames_after_first']) in out_r)
ok &= case('r5b without the .idx file the record count is None', ent(BASE / 'r4', 'c142_01')['idx'] is None)
# RC4: HOLDS_120 only with a stable attempt; the attempt row of V (item 224 (a)(4))
e = census('h1', LONG, js=js_for('c142_01', attempt=dict(ft_tail=None, hold_s=None, outcome='timeout')))
ok &= case('h1 (replaces o7b) a timeout of enter_scene with 120 s shown -> NOT_EVALUABLE, no stable (timeout)',
           e['outcome'] == 'NOT_EVALUABLE' and e['reason'] == 'no stable (timeout)' and not e['tail_stall'])
e = census('h2', LONG, js=js_for('c142_01', attempt=dict(hold_s=119.9)))
ok &= case('h2 hold_s 119.9 -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE' and e['reason'].startswith('hold_s'))
e = census('h2b', LONG, js=js_for('c142_01', attempt=dict(hold_s=120.0)))
ok &= case('h2b hold_s 120.0 -> HOLDS_120', e['outcome'] == 'HOLDS_120')
e = census('h2c', LONG, js=js_for('c142_01', attempt=dict(hold_s=None)))
ok &= case('h2c attempt ok without hold_s -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
ok &= case('h3 V timeout (no hold) -> the V attempt row fails', fails('h3', 'V attempt ok',
           v_js=js_for('v142', attempt=dict(outcome='timeout', hold_s=None))))
ok &= case('h4 V hold_s 329.9 -> the V attempt row fails', fails('h4', 'V attempt ok',
           v_js=js_for('v142', attempt=dict(hold_s=329.9))))
v, w = pair('h5', v_es=['WARNING: the game ENDED inside the hold after 9.0 s, returncode 1 (0x00000001)'])
word, rows = S.scene_ok(v, w, 'viewed')
ok &= case('h5 V ENDED line -> the attempt and death rows fail, NO', word == 'NO' and row_ok(rows, 'V attempt ok') is False
           and row_ok(rows, 'V 0 death markers') is False)
# RC5: the sheet file and its sha (item 224 (a)(5))


def sheet_case(name, act):
    v, w = pair(name)
    act(BASE / name)
    v = ent(BASE / name, 'v142')
    word, rows = S.scene_ok(v, w, 'viewed')
    return word, row_ok(rows, 'V sheet file'), S.scene_ok(v, w, None)[0]


TP = 'step2/times.txt'
res = sheet_case('s1', lambda r: (r / 'sheet_v142.png').unlink())
ok &= case('s1 viewed without sheet_v142.png -> NO; unset -> PENDING_SHEET (by the letter)', res == ('NO', False, 'PENDING_SHEET'))
res = sheet_case('s2', lambda r: (r / 'sheet_v142.png').write_bytes(b''))
ok &= case('s2 an empty sheet -> NO', res[:2] == ('NO', False))
res = sheet_case('s3', lambda r: (r / 'sheet_v142.png').write_bytes(b'another png'))
ok &= case('s3 a sheet whose sha is not the times.txt line -> NO', res[:2] == ('NO', False))
res = sheet_case('s4', lambda r: (r / 'rec_v142.mp4').write_bytes(b'another video'))
ok &= case('s4 a video whose sha is not the times.txt line -> NO', res[:2] == ('NO', False))
res = sheet_case('s5', lambda r: (r / TP).unlink())
ok &= case('s5 no step2/times.txt -> NO', res[:2] == ('NO', False))


def s6(r):
    (r / 'rec_v142.mp4').unlink()
    keep = [l for l in (r / TP).read_text().splitlines(True) if 's51_vidglitch' not in l]
    (r / TP).write_text(''.join(keep))


res = sheet_case('s6', s6)
ok &= case('s6 no video and no video line -> NO', res[:2] == ('NO', False))


def s7(r):
    (r / 'sheet_v142.png').write_bytes(b'')
    keep = [l for l in (r / TP).read_text().splitlines(True) if ' sheet rc ' not in l]
    (r / TP).write_text(''.join(keep))


res = sheet_case('s7', s7)
ok &= case('s7 an empty sheet and no sheet line -> NO', res[:2] == ('NO', False))


def s8(r):
    lines = (r / TP).read_text().splitlines(True)
    (r / TP).write_text(''.join(l.replace('sha256 ', 'sha256 0') for l in lines) + ''.join(lines))


res = sheet_case('s8', s8)
ok &= case('s8 the last matching times.txt lines count (a stale line before them) -> YES', res[:2] == ('YES', True))


def s9(r):
    lines = (r / TP).read_text().splitlines(True)
    (r / TP).write_text(''.join(lines) + ''.join(l.replace('sha256 ', 'sha256 f', 1) if ' sheet rc ' in l else l
                                                 for l in lines if ' sheet rc ' in l))


res = sheet_case('s9', s9)
ok &= case('s9 a later sheet line with another sha -> NO', res[:2] == ('NO', False))
# RC6: W ft_tail > 0 (item 224 (a)(6))
ok &= case('w1 W ft_tail 0 -> the W ft_tail row fails', fails('w1', 'W ft_tail > 0', w_js=js_for('w142', attempt=dict(ft_tail=0))))
ok &= case('w2 W ft_tail None -> the W ft_tail row fails', fails('w2', 'W ft_tail > 0',
           w_js=js_for('w142', attempt=dict(ft_tail=None))))
ok &= case('w3 W ft_tail 1 -> YES', S.scene_ok(*pair('w3', w_js=js_for('w142', attempt=dict(ft_tail=1))), sheet='viewed')[0] == 'YES')
# RC7: a scene change after the entry line (item 224 (a)(7))


def changed(name, change, before=100, after=(2000000, 16667), **kw):
    lines = scene_lines(LV, [16667] * before) + [change] + [ft(15 + before + i, dt) for i, dt in enumerate(after)]
    return census(name, None, lines=kw.pop('lines_extra', lambda l: l)(lines), **kw)


e = changed('q1', start('volcano_mountain'))
ok &= case('q1 another level started after the entry -> NOT_EVALUABLE scene change; the 2 s row after it is not K2, printed apart',
           e['outcome'] == 'NOT_EVALUABLE' and e['reason'] == 'scene change' and e['derive']['k2'] == []
           and e['derive']['other_starts'] == [('volcano_mountain', 114)] and e['derive']['after_change'] ==
           dict(rows=2, dt_us=2016667, k2=1) and e['derive']['frames_after_first'] == 100)
ok &= case('q2 the same level started again -> NOT_EVALUABLE', changed('q2', start(LV))['outcome'] == 'NOT_EVALUABLE')
ok &= case('q3 an empty name started -> NOT_EVALUABLE', changed('q3', 'GuestOut: Level has started: ')['outcome'] == 'NOT_EVALUABLE')
e = changed('q4', start('volcano_mountain'), lines_extra=lambda l: l[:40] + [ft(99, 1000000)] + l[40:])
ok &= case('q4 a K2 frame before the change -> K2', e['outcome'] == 'K2' and e['reason'] == 'frame dt >= 1 s before the scene change')
e = changed('q5', start('volcano_mountain'), lines_extra=lambda l: l[:40] + ['--- Error ---'] + l[40:] + ['GpuHangAbort: x'])
ok &= case('q5 a log crash before the change -> K1 (the hang after it does not decide)', e['outcome'] == 'K1')
e = changed('q5c', start('volcano_mountain'), lines_extra=lambda l: l[:40] + ['GpuHangAbort: x', '--- Error ---'] + l[40:])
ok &= case('q5c two log markers before the change: the first (hang) decides -> K2', e['outcome'] == 'K2')
e = changed('q10', start('volcano_mountain'), after=(16667, 1000000, 16667), lines_extra=lambda l: l + [start('voxel_world')])
ok &= case('q10 two changes: the first one cuts (a 1 s row between them is not classified) -> NOT_EVALUABLE',
           e['outcome'] == 'NOT_EVALUABLE' and [x[0] for x in e['derive']['other_starts']] == ['volcano_mountain', 'voxel_world'])
e = changed('q5b', start('volcano_mountain'), lines_extra=lambda l: l + ['GpuHangAbort: requested=1'])
ok &= case('q5b a log marker only after the change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6', start('volcano_mountain'), stdout_lines=['--- Fatal Error ---'])
ok &= case('q6 a stdout marker with a change -> NOT_EVALUABLE (stdout is after the log)', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6b', start('volcano_mountain'), js=js_for('c142_01', attempt=dict(hold_exit=1, ft_tail=0)))
ok &= case('q6b hold_exit and tail stall with a change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
e = changed('q6c', start('volcano_mountain'), js=js_for('c142_01', attempt=dict(outcome='exited', hold_s=None)))
ok &= case('q6c exited with a change -> NOT_EVALUABLE', e['outcome'] == 'NOT_EVALUABLE')
out_q = '\n'.join(S.fmt_entry(changed('q7', start('volcano_mountain'))))
ok &= case('q7 the change is printed with the name and the last n before it', "[('volcano_mountain', 114)]" in out_q
           and 'rows after it 2' in out_q)
ok &= case('q8 V with a later start -> the V change row fails', fails('q8', 'V no scene change',
           v_lines=scene_lines(SKY, v_post()) + [start(SKY)]))
ok &= case('q8b W with a later start -> the W change row fails', fails('q8b', 'W no scene change',
           w_lines=W_LINES + ['GuestOut: Level has started: ']))
e = changed('q9', start('volcano_mountain'))
ok &= case('q9 the sum after the entry line stops at the change', e['derive']['dt_after_entry_us'] == 1500000 + 20000 +
           2000000 + 16667 * 100)
# RC8: an attempt without json; the emulator stdout missing (item 224 (a)(8))
root = BASE / 'j1'
mkrun(root, 'c142_01', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_01', attempt=dict(outcome='timeout')))
(root / 'attempt_c142_02.txt').write_text('made\n')
mkrun(root, 'c142_03', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_03', attempt=dict(outcome='timeout')))
mkrun(root, 'c142_04', [ft(i, 16667) for i in range(1, 50)], js=js_for('c142_04', attempt=dict(outcome='timeout')))
PRJ = root / 'pred.md'
PRJ.write_text('fixture\n', encoding='utf-8')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rj = S.main(['--tag', 'c142_02'], root=str(root), pred=str(PRJ))
    rj2 = S.main(['--tag', 'c142_05'], root=str(root), pred=str(PRJ))
    rj3 = S.main(['--stop-check', 'c142_05'], root=str(root), pred=str(PRJ))
    S.main(['--summary'], root=str(root), pred=str(PRJ))
out_j = buf.getvalue()
ok &= case('j1 --tag of an attempt without json -> ATTEMPT MADE, NO JSON (instrument), rc 1; without the marker NO_RUN',
           rj == 1 and 'TAG c142_02: ATTEMPT MADE, NO JSON (instrument)' in out_j and rj2 == 1 and 'TAG c142_05: NO_RUN' in out_j)
ok &= case('j2 summary: the attempt without json in the tag list and the census map, made 4 (1 without json), not admitted',
           'TAG c142_02: ATTEMPT MADE, NO JSON (instrument)' in out_j and
           'c142_02 big_hand_pirate_island ATTEMPT MADE, NO JSON (instrument) - not admitted' in ' '.join(out_j.split()) and
           'CENSUS made 4 of 10 (of them attempt made without json 1)' in out_j)
ok &= case('j3 the stop rule: not entered, no json, not entered, not entered -> no stop (--stop-check rc 0, summary not met)',
           rj3 == 0 and 'STOP RULE before c142_05: not met' in out_j and 'STOP RULE (item 221 (g)(4)): not met' in out_j)
root = BASE / 'j4'
mkrun(root, 'c142_01', scene_lines(LV, LONG))
(root / 'stdout_c142_01.txt').unlink()
e = ent(root, 'c142_01')
ok &= case('j4 census without the emulator stdout -> printed MISSING', not e['stdout_present'] and
           'emulator stdout: MISSING' in '\n'.join(S.fmt_entry(e)))
v, w = pair('j5')
(BASE / 'j5' / 'stdout_v142.txt').unlink()
ok &= case('j5 V without the emulator stdout -> the V stdout row fails', row_ok(S.scene_ok(ent(BASE / 'j5', 'v142'), w,
           'viewed')[1], 'V emulator stdout present') is False)
v, w = pair('j6')
(BASE / 'j6' / 'stdout_w142.txt').unlink()
ok &= case('j6 W without the emulator stdout -> the W stdout row fails', row_ok(S.scene_ok(v, ent(BASE / 'j6', 'w142'),
           'viewed')[1], 'W emulator stdout present') is False)
# RC9: n gaps after the first scene frame; torn lines (item 224 (a)(9))


def shifted(k):
    """V lines with every post row from index k on renumbered +1 (one gap, the dt sum unchanged)."""
    lines = scene_lines(SKY, v_post())
    i0 = lines.index(ft(14, 2000000, 894)) + 1
    for j in range(i0 + k, len(lines)):
        p = lines[j].split(' ', 2)
        lines[j] = 'FrameTrace: n=%d %s' % (int(p[1][2:]) + 1, p[2])
    return lines


ok &= case('g1 V one n gap after the first scene frame -> the gap row fails', fails('g1', 'V n gaps', v_lines=shifted(1500)))
ok &= case('g2 a gap before the first scene frame is not counted -> YES', S.scene_ok(*pair('g2', v_lines=scene_lines(
           SKY, v_post(), pre=[ft(12, 1500000, 20), ft(40, 20000, 99)])), sheet='viewed')[0] == 'YES')
e = census('g3', None, lines=scene_lines(LV, LONG) + ['FrameTrace: n=77 dt_', 'FrameTrace: n=78 dt_us=16667 lat_us=1'])
ok &= case('g3 a torn FrameTrace line is counted and printed', e['torn'] == 1 and 'torn FrameTrace lines 1' in
           '\n'.join(S.fmt_entry(e)))
# RC10: the second reading by the order; the info line of W beside V (item 224 (a)(2), (10))
ok &= case('f1 the forms by the order: first five B5a 1/5 B5 2/5, last five B5a 1/5 B5 0/5',
           'first five B5a 1/5 B5 2/5; last five B5a 1/5 B5 0/5' in out3)
ok &= case('f2 the summary prints the dt median and max of V and W', 'info dt_us after the first scene frame: V median 96774 '
           'max 97374; W median 150000 max 150000; W presented 300.0 s over 2000 frames' in out2)
# item 224 (b)(2): the check lines on synthetic device-lost and validation logs
cb = BASE / 'cb'


def cb_run(tag, lines, std=()):
    mkrun(cb, tag, lines, stdout_lines=std, glitch=None, sheet=False, js=js_for('c142_01', attempt=dict(hold_exit=321)))


cb_run('q1', scene_lines(LV, LONG) + ['vkQueueSubmit failed: ErrorDeviceLost (-4)', '--- Fatal Error ---'])
cb_run('q2', scene_lines(LV, LONG) + ['GpuHangAbort: requested=1', '--- Error ---'])
cb_run('q3', scene_lines(LV, LONG) + ['--- Fatal Error ---', 'vkQueueSubmit failed: ErrorDeviceLost (-4)'])
(cb / 'qv.txt').write_bytes(('\n'.join([VF, VW, VW]) + '\n').encode())
(cb / 'qn.txt').write_bytes(('\n'.join([VF, 'no validation layer: x', VW]) + '\n').encode())
S.CHECK_K2 = (('q1', str(cb)), ('q2', str(cb)))
S.CHECK_VAL = ('qv', str(cb / 'qv.txt'), str(cb / 'none.txt'))
n1b, t1b, l1b = S.checks1b()
ok &= case('b1 check lines: device lost and hang before the crash -> K2, validation active -> 3 of 3',
           (n1b, t1b) == (3, 3) and l1b[-1] == 'CHECK1B 3 of 3')
S.CHECK_K2 = (('q1', str(cb)), ('q3', str(cb)))
S.CHECK_VAL = ('qn', str(cb / 'qn.txt'), str(cb / 'none.txt'))
n1b, t1b, l1b = S.checks1b()
ok &= case('b2 a crash before the device lost and a "no validation layer" line -> 1 of 3', (n1b, t1b) == (1, 3))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rb2 = S.main(['--check1b'])
    S.CHECK_K2 = (('q1', str(cb)), ('q2', str(cb)))
    S.CHECK_VAL = ('qv', str(cb / 'qv.txt'), str(cb / 'none.txt'))
    rb1 = S.main(['--check1b'])
ok &= case('b3 main --check1b: rc 1 on a failed check, rc 0 on 3 of 3', rb2 == 1 and rb1 == 0)
try:
    (out_n + out_r + out_q + out_j + buf.getvalue()).encode('cp1250', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('m6b the new printed lines are ASCII (strict cp1250)', enc)
# ---------------- added after the counted full mutlib run of link 1b (add-only; survivors half, sk_v_att_ok, ma_nojs)
root = BASE / 'y1'
PRY = root / 'pred.md'
mkrun(root, 'c142_05', scene_lines('ice_iceberg', [16667] * 100 + [1200000] + [16667] * 7300))
mkrun(root, 'c142_06', scene_lines('sponge_dirty_bath', [16667] * 50 + [150000] + [16667] * 7300))
PRY.write_text('fixture\n', encoding='utf-8')
for t in ('c142_05', 'c142_06'):
    j = json.loads((root / ('%s.json' % t)).read_text(encoding='utf-8'))
    j['prereg']['sha256'] = hashlib.sha256(PRY.read_bytes()).hexdigest()
    (root / ('%s.json' % t)).write_text(json.dumps(j), encoding='utf-8')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    S.main(['--summary'], root=str(root), pred=str(PRY))
ok &= case('y1 the forms by the order at the edge: c142_05 (K2 in the window) is of the first five, c142_06 (K3) of the last five',
           'first five B5a 1/5 B5 1/5; last five B5a 0/5 B5 1/5' in buf.getvalue())
ok &= case('y2 V attempt outcome timeout with hold_s 330 -> the V attempt row fails', fails('y2', 'V attempt ok',
           v_js=js_for('v142', attempt=dict(outcome='timeout', hold_s=330.0))))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ry = S.main(['--tag', 'c142_02'], root=str(BASE / 'j1'), pred=str(BASE / 'j1' / 'pred.md'))
ok &= case('y3 main --tag alone on an attempt without json prints ATTEMPT MADE, NO JSON and not NO_RUN, rc 1', ry == 1 and
           buf.getvalue().strip() == 'TAG c142_02: ATTEMPT MADE, NO JSON (instrument)')
# ================= PART B (session 143, HPP-297; item 231 (i)(1)-(4)): the profile of session 143 - one case per new term
# and per new edge: the constants (levels, pairs, order, seal, chain), admission of V / W tags, SCENE_OK per level over its
# pair (V without W, W without V, W stopped early, a W of another level, two levels in one summary), the sheet per V tag
# (--sheet-tags), the stop rule over V tags only (a W call included), B33 and its 120 s variant at the edge, the W 310 s
# info row, the levels line, the score json of runs143, the seal of session 143, the regression of item 231 (i)(4) on a
# synthetic profile 142, and ASCII in strict cp1250.
S.profile(P143)
LV1, LV2, LV3 = 'spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower'
ok &= case('B1 the ten levels of item 231 (i)(1) in that order', S.LEVELS == (
    'spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
    'spring_punch_monster_cave', 'gulliver_island', 'rocket_hourglass', 'pot_treasure_cave', 'booster_magic_lamp',
    'rocket_space_station'))
ok &= case('B2 pairs v143_NN / w143_NN per level; SEQ = V then W per level; census = the V tags; W tags',
           S.PAIRS[0] == ('v143_01', 'w143_01', LV1) and S.PAIRS[9] == ('v143_10', 'w143_10', 'rocket_space_station')
           and len(S.PAIRS) == 10 and S.SEQ[:4] == ('v143_01', 'w143_01', 'v143_02', 'w143_02') and len(S.SEQ) == 20
           and S.SEQ[-1] == 'w143_10' and [t for t, _ in S.CENSUS] == ['v143_%02d' % i for i in range(1, 11)]
           and [lv for _, lv in S.CENSUS] == list(S.LEVELS) and S.W_TAGS == tuple('w143_%02d' % i for i in range(1, 11))
           and S.V_TAGS == tuple('v143_%02d' % i for i in range(1, 11)))
ok &= case('B3 the seal path, chain name, runs dir and scorer name of session 143; the s142 lines are printed in 143 only',
           S.PRED_PATH == 'C:/kyty/s143/pred/01_sc143.md' and S.CHAIN == 'go143a' and S.RUNS == 'runs143'
           and S.SCORER == 'sc143.py' and S.EXTRA is True and S.ROOT == 'C:/kyty/s143' and S.P142['EXTRA'] is False)
ok &= case('B4 the constants of sc142 after item 224 are unchanged (item 231 (i)(3)); the harness W hold 310 is info only',
           (S.SCENE_DRAWS, S.ENTRY_WIN, S.K2_US, S.K3_US, S.HOLD_CENSUS_US, S.HOLD_CENSUS_S, S.HOLD_SCENE_US, S.HOLD_W_S,
            S.HOLD_V_S, S.FRAMES_V, S.COVER_SLACK, S.PRIO_US, S.STOP_RUN, S.HALF, S.HOLD_W_HARNESS_S) ==
           (100, 599, 1000000, 100000, 120000000, 120, 300000000, 300, 330, 3000, 100, 50000, 3, 5, 310)
           and S.OPCODE_BASE == {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4} and S.BUILD_SHA == BUILD)
ok &= case('B5 level_of: V and W of a level; a tag of session 142 is unknown in profile 143',
           S.level_of('v143_03') == LV3 and S.level_of('w143_03') == LV3 and S.level_of('c142_01') is None
           and S.level_of('v142') is None and S.level_of('w143_11') is None)


def js143(tag, attempt=None, **over):
    is_w = tag in S.W_TAGS
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x'] + (['--vulkan-validation', 'true'] if is_w else [])
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl %s' % S.level_of(tag), 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    if is_w:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    else:
        env['KYTY_REC'] = 'C:\\kyty\\s143\\rec_%s.mp4' % tag
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,
             pipeline_cache_off=False)
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD, guest_args='-lvl %s' % S.level_of(tag), gates='', env=env, cmdline=cmd,
              prereg=dict(path=S.PRED_PATH, sha256=PRED_SHA), attempts=[a])
    js.update(over)
    return js


def mk143(root, tag, lines=None, js=None, glitch=(3200, 0), sheet=True, log=True, chain='go143a'):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    is_w = tag in S.W_TAGS
    lv = S.level_of(tag)
    if lines is None:
        lines = ([VF] + scene_lines(lv, [150000] * 2000) + [VW] * 3) if is_w else scene_lines(lv, v_post())
    (root / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js143(tag)), encoding='utf-8')
    if log:
        (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / ('stdout_%s.txt' % tag)).write_bytes(b'\n')
    (root / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if is_w:
        return str(root)
    if glitch is not None:
        (root / ('glitch_%s.txt' % tag)).write_text('C:/kyty/s143/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                    'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        (root / 'step2').mkdir(exist_ok=True)
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-10-01T00:00:00Z %s %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\n' % (
                chain, tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-10-01T00:00:00Z %s %s sheet rc 0 sheet_%s.png sha256 %s\n' % (
                chain, tag, tag, _h.sha256(b'png').hexdigest()))
    return str(root)


def adm143(tag, **over):
    js = js143(tag)
    for k, v in over.items():
        if k == 'env_del':
            for x in v:
                js['env'].pop(x, None)
        elif k == 'env_set':
            js['env'].update(v)
        else:
            js[k] = v
    return all(a[1] for a in S.admit(tag, js, PRED_SHA))


ok &= case('B6 good V (v143_04) and W (w143_04) jsons are admitted', adm143('v143_04') and adm143('w143_04'))
BAD143 = [('V of level 02 with the guest args of level 01', 'v143_02', dict(guest_args='-lvl %s' % LV1)),
          ('W with a video', 'w143_01', dict(env_set={'KYTY_REC': 'C:/kyty/s143/rec_w143_01.mp4'})),
          ('V without a video', 'v143_01', dict(env_del=['KYTY_REC'])),
          ('V with the video of its W', 'v143_01', dict(env_set={'KYTY_REC': 'C:/kyty/s143/rec_w143_01.mp4'})),
          ('W without validation', 'w143_05', dict(cmdline=['e', '--vulkan-validation', 'false'])),
          ('V with validation', 'v143_05', dict(cmdline=['e', '--vulkan-validation', 'false', '--vulkan-validation', 'true'])),
          ('W without VK_LAYER_PATH', 'w143_10', dict(env_del=['VK_LAYER_PATH'])),
          ('the seal path of session 142', 'v143_01', dict(prereg=dict(path='C:/kyty/s142/pred/02_sc142.md', sha256=PRED_SHA)))]
for name, tag, over in BAD143:
    ok &= case('B7 refused: %s' % name, not adm143(tag, **over))


def pair143(name, n=1, v=True, w=True, v_lines=None, w_lines=None, v_js=None, w_js=None, v_glitch=(3200, 0)):
    root = BASE / name
    vt, wt, lv = S.PAIRS[n - 1]
    if v:
        mk143(root, vt, v_lines, v_js, glitch=v_glitch)
    if w:
        mk143(root, wt, w_lines, w_js)
    return S.entry_of(vt, str(root), PRED_SHA), S.entry_of(wt, str(root), PRED_SHA), S.PAIRS[n - 1]


v, w, p = pair143('P1')
word, rows = S.scene_ok(v, w, 'viewed', p)
ok &= case('B8 a good pair of level 01 -> YES; every row PASS, the pair row and the sheet row of sheet_v143_01.png among them',
           word == 'YES' and all(r[1] for r in rows) and row_ok(rows, 'V v143_01 and W w143_01 are the pair of one level')
           is True and row_ok(rows, 'V sheet file sheet_v143_01.png present') is True and len(rows) == 27)
ok &= case('B8b the same pair: sheet row unfilled -> PENDING_SHEET; not-viewed -> NO',
           S.scene_ok(v, w, None, p)[0] == 'PENDING_SHEET' and S.scene_ok(v, w, 'not-viewed', p)[0] == 'NO')
v, w, p = pair143('P2', w=False)
word, rows = S.scene_ok(v, w, 'viewed', p)
ok &= case('B9 a level with V and no W -> NO: W made FAIL and the pair row FAIL',
           word == 'NO' and row_ok(rows, 'W made') is False and row_ok(rows, 'V v143_01 and W w143_01') is False)
v, w, p = pair143('P3', v=False)
word, rows = S.scene_ok(v, w, 'viewed', p)
ok &= case('B10 a level with W and no V -> NO: V made FAIL, the sheet row FAIL (no V)',
           word == 'NO' and row_ok(rows, 'V made') is False and row_ok(rows, 'V sheet file') is False)
v, w, p = pair143('P4', w_js=js143('w143_01', attempt=dict(hold_exit=3221225477, hold_s=120.3)))
word, rows = S.scene_ok(v, w, 'viewed', p)
ok &= case('B11 W stopped early (hold_exit, hold_s 120.3) -> NO: the W hold and death rows fail',
           word == 'NO' and row_ok(rows, 'W hold reached') is False and row_ok(rows, 'W 0 death markers') is False)
v, w, p = pair143('P5', w_js=js143('w143_01', attempt=dict(outcome='timeout', hold_s=None, ft_tail=None)))
ok &= case('B11b W not stable (timeout) -> NO', S.scene_ok(v, w, 'viewed', p)[0] == 'NO')
v, w, p = pair143('P6', w_js=js143('w143_01', attempt=dict(hold_s=305.0)))
ok &= case('B11c W hold_s 305.0 (>= 300 of item 221 (g)(3), < 310 of the harness) -> YES by the letter',
           S.scene_ok(v, w, 'viewed', p)[0] == 'YES')
v, w, p = pair143('P7', n=2, w_js=dict(js143('w143_02'), guest_args='-lvl %s' % LV1))
word, rows = S.scene_ok(v, w, 'viewed', p)
ok &= case('B12 the W of level 02 run with the guest args of level 01 -> NO: W not admitted, the pair row fails',
           word == 'NO' and row_ok(rows, 'W admitted') is False and row_ok(rows, 'V v143_02 and W w143_02') is False)
v, w, p = pair143('P7b', n=1)
w2 = S.entry_of('w143_01', str(BASE / 'P7b'), PRED_SHA)
word, rows = S.scene_ok(v, w2, 'viewed', S.PAIRS[1])
ok &= case('B12b the entries of level 01 offered as the pair of level 02 -> NO by the pair row',
           word == 'NO' and row_ok(rows, 'V v143_02 and W w143_02') is False)
ok &= case('B12c scene_ok without a pair reads the first pair of the profile',
           row_ok(S.scene_ok(v, w2, 'viewed')[1], 'V v143_01 and W w143_01') is True)
word, rows = S.scene_ok(dict(v, tag='v143_09'), w2, 'viewed', S.PAIRS[0])
ok &= case('B12d an entry under another V tag with the right guest args -> NO by the pair row only',
           word == 'NO' and [r[0][:30] for r in rows if not r[1]] == ['V v143_01 and W w143_01 are th'])
v, w, p = pair143('P7c', n=1, v_js=dict(js143('v143_01'), guest_args='-lvl %s' % LV2))
ok &= case('B12e the V of level 01 run with the guest args of level 02 -> the pair row fails (and V not admitted)',
           row_ok(S.scene_ok(v, w, 'viewed', p)[1], 'V v143_01 and W w143_01') is False)
R2 = BASE / 'P8'
PR8 = R2 / 'pred.md'
R2.mkdir(parents=True, exist_ok=True)
PR8.write_text('fixture 143\n', encoding='utf-8')
SH8 = hashlib.sha256(PR8.read_bytes()).hexdigest()
K2V = scene_lines(LV3, [16667] * 100 + [1200000] + list(v_post()))
for t, lines in (('v143_01', None), ('w143_01', None), ('v143_02', None), ('v143_03', K2V), ('w143_03', None)):
    mk143(R2, t, lines, dict(js143(t), prereg=dict(path=S.PRED_PATH, sha256=SH8)))
out8, ents8, words8 = S.summary(str(R2), SH8, 'viewed')
T8 = '\n'.join(out8)


def block(lines, head):
    i = lines.index(head)
    j = i + 1
    while j < len(lines) and lines[j].startswith('  '):
        j += 1
    return lines[i + 1:j]


b1 = block(out8, 'SCENE_OK %s: YES' % LV1) if 'SCENE_OK %s: YES' % LV1 in out8 else ['FAIL']
b2 = block(out8, 'SCENE_OK %s: NO' % LV2) if 'SCENE_OK %s: NO' % LV2 in out8 else []
b3 = block(out8, 'SCENE_OK %s: NO' % LV3) if 'SCENE_OK %s: NO' % LV3 in out8 else []
ok &= case('B13 two levels in one summary do not mix: level 01 YES with every row PASS; level 02 (V, no W) NO by W made only;'
           ' level 03 (V with a K2 frame, W good) NO by the dt row only',
           all(not x.startswith('  FAIL') for x in b1) and
           [x for x in b2 if x.startswith('  FAIL')] == ['  FAIL W made ()', '  FAIL V v143_02 and W w143_02 are the pair of '
                                                         'one level (guest args -lvl booster_construction in both) '
                                                         '(-lvl booster_construction / None)']
           and [x.split(' (')[0] for x in b3 if x.startswith('  FAIL')] == ['  FAIL V no frame dt >= 1 s after the first scene frame'])
ok &= case('B14 the levels line: YES 1, PENDING_SHEET 0, NO 9 of 10; the not-made levels are NO with V and W made FAIL',
           'SCENE_OK LEVELS: YES 1, PENDING_SHEET 0, NO 9 of 10' in out8 and words8[0] == 'YES' and
           '  FAIL V made ()' in block(out8, 'SCENE_OK rocket_space_station: NO'))
ok &= case('B15 the census of 143 reads the V tags only: made 3, admitted 3; B5a 1/10 (v143_03), B5 1/10; W tags not in it',
           'CENSUS made 3 of 10 (of them attempt made without json 0), admitted 3' in out8 and
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 1/10 [c] (admitted and entered 3)' in out8 and
           'FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): 1/10 [c] (admitted and entered 3)' in out8
           and not any(x.startswith('  w143_') for x in out8))
ok &= case('B16 the W 310 s info row: yes for a W at 310.0; "W not made" without a W',
           '  info W hold_s >= 310 (item 231 (i)(2), the harness hold; executor reading, not in the verdict): yes' in b1
           and '  info W hold_s >= 310 (item 231 (i)(2), the harness hold; executor reading, not in the verdict): W not made'
           in b2)
v, w, p = pair143('P9', w_js=js143('w143_01', attempt=dict(hold_s=309.9)))
o9 = []
for t, e in (('v143_01', v), ('w143_01', w)):
    (BASE / 'P9' / ('%s.json' % t)).write_text(json.dumps(dict(json.loads((BASE / 'P9' / ('%s.json' % t)).read_text()),
                                                                prereg=dict(path=S.PRED_PATH, sha256=SH8))))
o9 = S.summary(str(BASE / 'P9'), SH8, 'viewed')[0]
ok &= case('B16b W hold_s 309.9: the info row says NO (309.9), the verdict by the letter is YES',
           any(x.endswith('executor reading, not in the verdict): NO (309.9)') for x in o9) and 'SCENE_OK %s: YES' % LV1 in o9)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rs1 = S.main(['--summary', '--sheet', 'viewed', '--sheet-tags', 'v143_03'], root=str(R2), pred=str(PR8))
    rs2 = S.main(['--summary', '--sheet', 'viewed', '--sheet-tags', 'w143_01'], root=str(R2), pred=str(PR8))
o10 = buf.getvalue().split('\n')
ok &= case('B17 --sheet-tags: the sheet row applies to the named V only (level 01 -> PENDING_SHEET); a W tag -> rc 2',
           rs1 == 0 and 'SCENE_OK %s: PENDING_SHEET' % LV1 in o10 and rs2 == 2
           and 'usage: --sheet-tags takes V tags only: w143_01' in o10)
v, w, p = pair143('P10')
with open(BASE / 'P10' / 'step2' / 'times.txt', 'w', encoding='utf-8') as f:
    f.write('2026-10-01T00:00:00Z go142a v143_01 s51_vidglitch rc 0 glitch_v143_01.txt sha256 %s rec_v143_01.mp4 sha256 %s\n'
            '2026-10-01T00:00:00Z go142a v143_01 sheet rc 0 sheet_v143_01.png sha256 %s\n' % (
                'ab' * 32, _h.sha256(b'mp4 v143_01').hexdigest(), _h.sha256(b'png').hexdigest()))
v = S.entry_of('v143_01', str(BASE / 'P10'), PRED_SHA)
ok &= case('B18 the sheet lines of times.txt must carry the chain name go143a (go142a lines do not count) -> NO',
           S.scene_ok(v, w, 'viewed', p)[0] == 'NO' and not v['sheet']['ok'])
ok &= case('B18b only V tags carry a sheet state; W does not', w['sheet'] is None and v['sheet'] is not None)
R11 = BASE / 'P11'
for t in ('v143_01', 'w143_01', 'v143_02', 'w143_02', 'v143_03'):
    mk143(R11, t, [ft(i, 16667) for i in range(1, 50)], js143(t, attempt=dict(outcome='timeout', hold_s=None)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rk = [S.main(['--stop-check', t], root=str(R11), pred=str(BASE / 'nopred.md'))
          for t in ('w143_03', 'v143_03', 'w143_02', 'v143_04', 'v143_01', 'x')]
ok &= case('B19 the stop rule over V tags: three V not entered before w143_03 -> rc 5 (its own V counts), before v143_03 and '
           'w143_02 -> rc 0 (the W not entered are not census), before v143_04 -> rc 5, v143_01 -> rc 0, unknown -> rc 2',
           rk == [5, 0, 0, 5, 0, 2])
R12 = BASE / 'P12'
mk143(R12, 'v143_02', [ft(i, 16667) for i in range(1, 50)], js143('v143_02', attempt=dict(outcome='timeout', hold_s=None)))
mk143(R12, 'v143_01', [ft(i, 16667) for i in range(1, 50)], js143('v143_01', attempt=dict(outcome='timeout', hold_s=None)))
mk143(R12, 'v143_03', None)
mk143(R12, 'v143_04', [ft(i, 16667) for i in range(1, 50)], js143('v143_04', attempt=dict(outcome='timeout', hold_s=None)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rk12 = S.main(['--stop-check', 'w143_04'], root=str(R12), pred=str(BASE / 'nopred.md'))
ok &= case('B19b an entered V breaks the run: NE, NE, entered, NE before w143_04 -> rc 0', rk12 == 0)


def b33_lines(rem):
    """V of level 01: window 599 rows of 16 667, hold rows of 99 999 and one K3 row 150 000 whose cumulative presented time
    after the entry line is 120 000 000 - 47 530 + rem (rem 47 530 -> exactly 120 s)."""
    post = [16667] * 599 + [99999] * 1063 + [rem, 150000] + [16667] * 2000
    return scene_lines(LV1, post)


e = S.derive(S.scan(mk143(BASE / 'P13a', 'v143_01', b33_lines(47530)) + '/log_v143_01.txt'), LV1)
e2 = S.derive(S.scan(mk143(BASE / 'P13b', 'v143_01', b33_lines(47531)) + '/log_v143_01.txt'), LV1)
ok &= case('B20 B33 variant edge: the K3 hold row at exactly 120 000 000 us after the entry line is within 120 s; 1 us later '
           'it is not; the letter counts it both times',
           e['k3h'] == [(1678, 150000)] and e['k3h120'] == [(1678, 150000)] and e2['k3h'] == [(1678, 150000)]
           and e2['k3h120'] == [])
e3 = S.derive(S.scan(mk143(BASE / 'P13d', 'v143_01', scene_lines(LV1, [16667] * 700 + [100000] + [16667] * 3000))
                     + '/log_v143_01.txt'), LV1)
ok &= case('B20c a hold row of exactly 100 000 us within 120 s is K3 of both readings', e3['k3h'] == [(715, 100000)]
           and e3['k3h120'] == [(715, 100000)])
ok &= case('B20b K3 in the entry window is not B33', S.derive(S.scan(mk143(BASE / 'P13c', 'v143_01', scene_lines(
    LV1, [16667] * 10 + [150000] + [16667] * 3000)) + '/log_v143_01.txt'), LV1)['k3h120'] == [])
R14 = BASE / 'P14'
PR14 = R14 / 'pred.md'
R14.mkdir(parents=True, exist_ok=True)
PR14.write_text('fixture 143 b33\n', encoding='utf-8')
SH14 = hashlib.sha256(PR14.read_bytes()).hexdigest()
mk143(R14, 'v143_01', b33_lines(47530), dict(js143('v143_01'), prereg=dict(path=S.PRED_PATH, sha256=SH14)))
mk143(R14, 'v143_02', scene_lines(LV2, [16667] * 599 + [99999] * 1500 + [150000] + [16667] * 2000),
      dict(js143('v143_02'), prereg=dict(path=S.PRED_PATH, sha256=SH14)))
mk143(R14, 'v143_03', scene_lines(LV3, [16667] * 8000), dict(js143('v143_03'), prereg=dict(path=S.PRED_PATH, sha256=SH14)))
mk143(R14, 'v143_04', scene_lines('path_maker_mana_tree', [16667] * 599 + [99999] * 100 + [150000] + [16667] * 8000),
      dict(js143('v143_04'), prereg=dict(path=S.PRED_PATH, sha256=SH14), binary_sha256=OTHER))
o14 = S.summary(str(R14), SH14, None)[0]
ok &= case('B21 FORM B33 over admitted V: v143_01 (K3 at 120 s, both readings), v143_02 (K3 past 120 s, letter only); '
           'v143_04 of another build not counted -> letter 2/10 with tags, variant 1/10',
           'FORM B33 (a frame 100 ms <= dt < 1 s on the hold after the window): 2/10 [c] (admitted and entered 3) '
           'v143_01,v143_02; executor variant (the hold within 120 s of presented time after the entry line): 1/10' in o14)
ok &= case('B21b the levels line with no W made: YES 0, PENDING_SHEET 0, NO 10 of 10',
           'SCENE_OK LEVELS: YES 0, PENDING_SHEET 0, NO 10 of 10' in o14)
ok &= case('B22 the K3 hold line of 120 s is printed per entry in profile 143',
           any(x.startswith('  K3 hold within 120 s of presented time after the entry line (executor variant') for x in o14))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rt = S.main(['--tag', 'v143_03'], root=str(R14), pred=str(PR14))
sj = json.loads((R14 / 'runs143' / 'v143_03.score.json').read_text(encoding='utf-8'))
ok &= case('B23 main --tag of 143 writes runs143/<tag>.score.json (rc 0 when admitted) with the 120 s K3 list',
           rt == 0 and sj['tag'] == 'v143_03' and sj['derive']['k3h120'] == [] and sj['outcome'] == 'HOLDS_120')
REQ143 = ('go143a.sh', 'sc143.py', 'test_sc143.py', 'mut_sc143.py', 'enter_scene.py', 'sheet142.py', 'fgcpu143.py',
          'test_fgcpu143.py', 'test_go143a.py', 'C:/kyty/scripts/s51_vidglitch.py')
ok &= case('B24 the seal of 143 names the harness, scorer, fixtures, mutants, enter_scene.py, sheet142.py, the CPU row and '
           's51_vidglitch.py (item 231 (i)(4))', all(n in S.SEALED_NAMES for n in REQ143))
rs = BASE / 'seal143'
rs.mkdir()
shutil.copyfile(SRC, rs / 'sc143.py')
ls143 = []
for name in S.SEALED_NAMES:
    if name.startswith('C:/'):
        sh = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    elif name != 'sc143.py':
        (rs / name).write_bytes(('fixture ' + name).encode())
        sh = hashlib.sha256((rs / name).read_bytes()).hexdigest()
    else:
        sh = hashlib.sha256(Path(SRC).read_bytes()).hexdigest()
    ls143.append('seal: %s %s' % (sh, name))
(rs / 'pred.md').write_text('seal 143\n' + '\n'.join(ls143) + '\n', encoding='utf-8')
g143, r143 = S.check_seal(str(rs / 'pred.md'), str(rs), SRC)
(rs / 'pred2.md').write_text('seal 143\n' + '\n'.join(x.replace(' sc143.py', ' sc142.py') for x in ls143) + '\n',
                             encoding='utf-8')
ok &= case('B25 the seal check of 143 passes on its names (the scorer by sc143.py) and fails with the scorer named sc142.py',
           g143 and len(r143) == len(S.SEALED_NAMES) + 1 and S.check_seal(str(rs / 'pred2.md'), str(rs), SRC)[0] is False)
# the regression of item 231 (i)(4) on a synthetic profile 142
RG = BASE / 'rg'
RG.mkdir()
P142_REAL = dict(S.P142)
B33_REAL = S.REGRESS_B33
S.P142 = dict(S.P142, ROOT=RG.as_posix(), PRED_PATH=(RG / 'pred.md').as_posix())
(RG / 'pred.md').write_text('fixture 142\n', encoding='utf-8')
SHR = hashlib.sha256((RG / 'pred.md').read_bytes()).hexdigest()
old = S.profile(S.P142)
mkrun(RG, 'v142', scene_lines(SKY, v_post()), js=js_for('v142', prereg=dict(path=S.PRED_PATH, sha256=SHR)))
mkrun(RG, 'w142', W_LINES, js=js_for('w142', prereg=dict(path=S.PRED_PATH, sha256=SHR)), glitch=None, sheet=False)
mkrun(RG, 'c142_01', scene_lines('bumper_enemy_snowy_canyon', [16667] * 7300),
      js=js_for('c142_01', prereg=dict(path=S.PRED_PATH, sha256=SHR)))
mkrun(RG, 'c142_02', scene_lines('big_hand_pirate_island', [16667] * 700 + [150000] + [16667] * 7300),
      js=js_for('c142_02', prereg=dict(path=S.PRED_PATH, sha256=SHR)))
mkrun(RG, 'c142_03', scene_lines('timestop_casino', [16667] * 700 + [150000] + [16667] * 7300),
      js=js_for('c142_03', prereg=dict(path=S.PRED_PATH, sha256=SHR), binary_sha256=OTHER))
outr = S.summary(str(RG), SHR, 'viewed')[0]
S.profile(old)
EXP = RG / 'expected.txt'
EXP.write_bytes(('\r\n'.join(outr) + '\r\n').encode('ascii'))
S.REGRESS_B33 = ('c142_02',)
okr, lr = S.regress142(str(EXP))
ok &= case('B26 regress142 on a synthetic profile 142: byte-identical, 0 differing lines, B33 c142_02 -> PASS; the summary '
           'of profile 142 has no line of 143 (no pair row, no B33, no levels line); the profile is restored after it',
           okr and lr[-1] == 'REGRESS142: PASS' and 'byte-identical yes; differing lines 0' in lr[0] and
           not any('pair of one level' in x or 'FORM B33' in x or 'SCENE_OK LEVELS' in x or 'K3 hold within' in x
                   for x in outr) and 'SCENE_OK underwater_aerial_garden: YES' in outr and S.ROOT == 'C:/kyty/s143'
           and S.CHAIN == 'go143a' and S.EXTRA is True and S.SEQ[0] == 'v143_01')
EXP.write_bytes(('\r\n'.join(outr[:5] + ['changed line'] + outr[6:]) + '\r\n').encode('ascii'))
okr2, lr2 = S.regress142(str(EXP))
ok &= case('B27 one changed line -> FAIL with the DIFF line pair printed (line 6)', not okr2 and
           'DIFF line 6 expected: changed line' in lr2 and lr2[-1] == 'REGRESS142: FAIL')
EXP.write_bytes(('\n'.join(outr) + '\n').encode('ascii'))
okr3, lr3 = S.regress142(str(EXP))
ok &= case('B28 the same text with LF only -> not byte-identical -> FAIL (0 differing lines)', not okr3 and
           'byte-identical NO; differing lines 0' in lr3[0])
EXP.write_bytes(('\r\n'.join(outr) + '\r\n').encode('ascii'))
S.REGRESS_B33 = ('c142_01',)
ok &= case('B29 B33 tags other than item 231 (g)(1) -> FAIL', S.regress142(str(EXP))[0] is False)
S.REGRESS_B33 = ('c142_02',)
ok &= case('B30 a missing expected file -> FAIL', S.regress142(str(RG / 'none.txt'))[0] is False)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rr = S.main(['--regress142'])
ok &= case('B31 main --regress142 -> rc 1 against the default expected file of the real s142 summary (the fixture root '
           'differs), rc of a PASS is 0', rr == 1 and 'REGRESS142: FAIL' in buf.getvalue())
S.P142 = P142_REAL
S.REGRESS_B33 = B33_REAL
ok &= case('B32 the real profile 142 and the regression constants of item 231 (g)(1)', S.P142['ROOT'] == 'C:/kyty/s142'
           and S.P142['PRED_PATH'] == 'C:/kyty/s142/pred/02_sc142.md' and S.P142['CHAIN'] == 'go142a'
           and S.P142['PAIRS'] == (('v142', 'w142', SKY),) and S.REGRESS_B33 == ('c142_02', 'c142_03', 'c142_05')
           and S.REGRESS_FILE == 'C:/kyty/s142/step4/summary142_viewed.txt')
x = S.profile(dict(CHAIN='zz'))
ok &= case('B33 profile() sets the values and returns the old ones', S.CHAIN == 'zz' and x == dict(CHAIN='go143a'))
S.profile(x)
try:
    ('\n'.join(out8 + o9 + o10 + o14 + lr + lr2 + lr3) + buf.getvalue()).encode('cp1250', errors='strict')
    ('\n'.join(out8 + o14)).encode('ascii', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('B34 every new printed line is ASCII (strict cp1250 and ascii)', enc)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
