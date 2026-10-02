"""Offline fixtures of sc146.py (session 146 step 0, HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7), item 300 (b)(4)).
PARTS A-E: the whole suite of sc145.py (C:/kyty/s145/test_sc145.py, every case unchanged) run on sc146.py in the profiles
142-145 (sc146.profile(sc146.P145) first) - the reading of sc145 holds in the ported code.  PART F (at the end): the profile
of session 146 - the 35 tags and their order, the re-check and second-hold V, the W form on the shipment binary (precache by
default), the DualSrcBlend control (control stop term, data row of every W, the variant of item 281 (g)), the stubs (F13) and
asserts (F14) rows, the tile events (D-4), SKIPPED_V_NOT_ENTERED (--skip-w, the summary), the stop-check from score.json (its
source line and the fall back to the log), the three-V rule over every made V, the RECHECK / B40 / Sky Garden / DATA lines,
the real log of the warm-up i146_v, ASCII.  Cases F1-F22.  Link 1b (HPP-395, item 316 (b)-(d)): the seal pred/02_sc146.md
(F2), the skip of a W only on positive evidence and only on the V key attempt:<outcome> - F13 with the key, F13b-F13k (no
log in the log and the json reading, 0 bytes with the old and the empty sha line, another sha in both readings, no
times.txt, another attempt outcome, the death marker keys K1 / K2 / VALIDATION_STOP in the log, the stdout and the json
reading, the cases A and B of the Red Team experiment rt146_skipfx), their lines in F22.
    python C:/kyty/s146/test_sc146.py [<sc146 under test>]
Session 145 header (carried):
Offline fixtures of sc145.py (session 145 step 0, HPP-350; ROADMAP s122 item 273 (k)(1)-(5)).  PARTS A-D: the whole
suite of sc144.py (C:/kyty/s144/test_sc144.py, every case unchanged) run on sc145.py: PART A in profile 142, PARTS B and C
in profile 143, PART D in profile 144 (sc145.profile(sc145.P144)) - the reading of sc144 holds in the ported code.
PART E (at the end): the profile of session 145 - the 34 tags and their order, the control W, the W repeat of
rocket_hourglass with the V v144_09 of s144 (its root, chain, seal, log sha and sheet), the cold census, the W filter of
one message and its violations, the window event (minimized, Recovering without minimized, the stdout, other window
lines, chunks), the layer limit (control 0 required, other W "layer truncated"), the video continuity of B38 (the gap of
60 ms, the margin of 12 ms, before / after the first scene frame, the longest run), the stop rule of the window event, the
summary lines, the regression of profile 144 on a synthetic profile, the real constants, ASCII.
Link 1b of s145 (HPP-379, ROADMAP item 295): PART E drops the filter of one message; the W form rows 295 (b)(1)-(4) (held /
not held, the 10 s edge of (b)(3), the third field 2 exactly, the form line edges), the window lines by kind and the
nearest one to every K2 / K3 frame (+-2 s edges, entry / hold, stdout lines not positioned), the alignment of the video
continuity (shares within 8 ms, the best shift and its tie rule, the 10 % mark), the summary lines, the NEW295 rows of the
regression of profile 144 (cases E34-E44).
Session 144 header (carried): PARTS A-C: the whole
suite of sc143.py (C:/kyty/s143/test_sc143.py of link 1b, every case unchanged) run on sc144.py: PART A in profile 142, PARTS
B and C in profile 143 (sc144.profile(sc144.P143)) - the reading of sc143 after items 242, 246 holds in the ported code.
PART D (at the end): the profile of session 144 - the 33 tags and their order, the control W, the cross-session pair (a W
of s144 with the V of s143: its root, chain, seal, log sha and sheet), the W form of item 254 (e) and its violations, the W
stopped before / after the first GuestOut line, the stop rules of item 254 (k)(4) (control, two W, three V), the repeated
entry V, the skipped-draw frames by distinct frame= (debt D-7), the regression of profile 143, ASCII.
Session 143 header (carried): PART A: the whole suite of
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
    python C:/kyty/s145/test_sc145.py [<sc145 under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc146.py')
print('suite test_sc146.py sha256 %s target sc146.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc146_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
P146 = S.profile(S.P145)     # PARTS A-E run in the profiles 142-145; PART F restores the profile of session 146
P145 = S.profile(S.P144)     # PARTS A-D run in the profiles 142-144; PART E restores the profile of session 145
P144 = S.profile(S.P143)     # PARTS B, C run in profile 143; PART D restores the profile of session 144
P143 = S.profile(S.P142)     # PART A runs in profile 142; PART B restores the profile of session 143

BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
OTHER = '05431dad252676b05128828a42169de0c1f84aff799838a513a0d80b32afcd84'
SKY = 'underwater_aerial_garden'
PRED_SHA = 'ab' * 32
BASE = Path('C:/kyty/s146/fx_sc146')   # mutlib gives every job its own copy of this directory
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
S.CHUNK = 1 << 20     # link 1b: 64 MB read buffers per small fixture file made the suite slow; edges: s1
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
           S.PRED_PATH == 'C:/kyty/s143/pred/02_sc143.md' and S.CHAIN == 'go143a' and S.RUNS == 'runs143'
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
             pipeline_cache_off=False, level=S.level_of(tag))
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
        (root / 'step2').mkdir(exist_ok=True)
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-10-01T00:00:00Z %s %s enter_scene end rc 0 log_%s.txt sha256 %s\n' % (
                chain, tag, tag, _h.sha256((root / ('log_%s.txt' % tag)).read_bytes()).hexdigest()))
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
           [x.split(' (')[0] for x in b2 if x.startswith('  FAIL')] == ['  FAIL W made', '  FAIL V v143_02 and W w143_02 are the pair of one level']
           and [x.split(' (')[0] for x in b3 if x.startswith('  FAIL')] == ['  FAIL V no frame dt >= 1 s after the first scene frame'])
ok &= case('B14 the levels line: YES 1, PENDING_SHEET 0, NO 9 of 10; the not-made levels are NO with V and W made FAIL',
           'SCENE_OK LEVELS: YES 1, PENDING_SHEET 0, NO 9 of 10' in out8 and words8[0] == 'YES' and
           '  FAIL V made ()' in block(out8, 'SCENE_OK rocket_space_station: NO'))
ok &= case('B15 the census of 143 reads the V tags only: made 3, admitted 3; B5a 1/10 (v143_03), B5 1/10; W tags not in it',
           'CENSUS made 3 of 10 (of them attempt made without json 0), admitted 3' in out8 and
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 1/10 [c] (admitted and entered 3)' in out8 and
           'FORM B5 (a frame dt >= 100 ms in the entry window, no warm base): 1/10 [c] (admitted and entered 3)' in out8
           and not any(x.startswith('  w143_') and ' -> ' not in x for x in out8))
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
        (rs / name).parent.mkdir(parents=True, exist_ok=True)
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
# ================= PART C (session 143 link 1b, HPP-321; ROADMAP item 242 (b)-(e)): one case per new term and per new edge -
# (c) B5a on the whole V and its variant 120 s, K2 by place, K2 only after 120 s, the outcome on 120 s of the map (A) row
# (K2 at 119 s / 121 s / exactly 120 s / 1 us later; markers, hold_exit and the tail stall before / after the cut); (d) W
# without the dt rule and the class VALIDATION_STOP (the report edges: the next "--- Build ---", the location line, 50
# lines; log and stdout; profile 142 keeps K1); (e) the pair row by the json level and the log sha of step2/times.txt;
# (b) the cache continuity lines and the forms without the tags after the first break.
FILL = 40000          # a filler row: 40 ms, neither K2 nor K3
PRE_US = 1500000 + 20000 + 2000000     # the loading rows and the first scene frame of scene_lines: 3.52 s after the entry


def k2_at(level, end_us, k2=1200000, tail=7000, fill=FILL):
    """A V log whose K2 frame (dt k2) ends at end_us of presented time after the entry line (end_us - PRE_US - k2 must be a
    multiple of fill), then tail rows of 40 ms."""
    n = (end_us - PRE_US - k2) // fill
    assert PRE_US + n * fill + k2 == end_us, end_us
    return scene_lines(level, [fill] * n + [k2] + [fill] * tail)


LV4 = 'path_maker_mana_tree'
d119 = S.derive(S.scan(mk143(BASE / 'C1a', 'v143_01', k2_at(LV1, 119000000)) + '/log_v143_01.txt'), LV1)
d121 = S.derive(S.scan(mk143(BASE / 'C1b', 'v143_01', k2_at(LV1, 121000000)) + '/log_v143_01.txt'), LV1)
d120 = S.derive(S.scan(mk143(BASE / 'C1c', 'v143_01', k2_at(LV1, 120000000)) + '/log_v143_01.txt'), LV1)
d120b = S.derive(S.scan(mk143(BASE / 'C1d', 'v143_01', k2_at(LV1, 120000001, k2=1200001)) + '/log_v143_01.txt'), LV1)
ok &= case('C1 a K2 frame ending at 119 s of presented time after the entry line is within 120 s; at 121 s it is not; '
           'the whole-V K2 list holds both (place hold)',
           d119['k2_120'] == [(2872, 1200000, 'hold')] and d119['k2'] == [(2872, 1200000, 'hold')]
           and d121['k2_120'] == [] and d121['k2'] == [(2922, 1200000, 'hold')])
ok &= case('C1b the edge: a K2 frame ending at exactly 120 000 000 us is within; 1 us later it is not; the cut is the first '
           'row past 120 s', d120['k2_120'] == [(2897, 1200000, 'hold')] and d120b['k2_120'] == [] and
           d120['cut120_pos'] is not None and d120b['cut120_pos'] is not None and d120b['cut120_pos'] < d120['cut120_pos'])
ok &= case('C1c a log that never passes 120 s has no cut', S.derive(S.scan(mk143(BASE / 'C1e', 'v143_01', scene_lines(
    LV1, [FILL] * 100)) + '/log_v143_01.txt'), LV1)['cut120_pos'] is None)
d1e = S.derive(S.scan(mk143(BASE / 'C1f', 'v143_01', scene_lines(LV1, [FILL] * 598 + [1000000, 1000000] + [FILL] * 100))
                      + '/log_v143_01.txt'), LV1)
ok &= case('C1e K2 of exactly 1 000 000 us within 120 s is in the 120 s list; frame 598 after the first frame is entry, '
           '599 is hold', d1e['k2_120'] == [(613, 1000000, 'entry'), (614, 1000000, 'hold')])
RC = BASE / 'C2'
mk143(RC, 'v143_01', k2_at(LV1, 119000000))
mk143(RC, 'v143_02', k2_at(LV2, 121000000))
mk143(RC, 'v143_03', scene_lines(LV3, [16667] * 10 + [1500000] + [FILL] * 8000))
mk143(RC, 'v143_04', scene_lines(LV4, [FILL] * 8000))
oc = S.summary(str(RC), PRED_SHA, None)[0]
ec = dict((t, S.entry_of(t, str(RC), PRED_SHA)) for t in ('v143_01', 'v143_02', 'v143_03', 'v143_04'))
ok &= case('C2 B5a by the letter on the whole V: 3/10 (v143_01 at 119 s, v143_02 at 121 s, v143_03 in the window)',
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 3/10 [c] (admitted and entered 4)' in oc)
ok &= case('C2b the variant 120 s: 2/10 v143_01,v143_03; K2 by place on the whole V: entry 1 v143_03, hold 2 v143_01,v143_02',
           'FORM B5a variant 120 s (a frame dt >= 1 s within 120 s of presented time after the entry line; the class '
           'decision and pooling with s142 use this one, item 242 (c)): 2/10 [c] v143_01,v143_03; K2 by place on the whole '
           'V: entry 1 v143_03, hold 2 v143_01,v143_02' in oc)
ok &= case('C2c K2 only after 120 s: v143_02 (a separate row (B), form edes122)',
           'K2 ON THE HOLD AFTER 120 s ONLY (a separate row (B) of register F per level, form edes122, not B5a; item 242 '
           '(c)): v143_02' in oc)
ok &= case('C2d the map (A) rows carry both outcomes: v143_01 K2 / K2, v143_02 HOLDS_120 on 120 s / K2 on the whole V, '
           'v143_04 HOLDS_120 / HOLDS_120',
           ec['v143_01']['outcome120'][0] == 'K2' and ec['v143_01']['outcome'] == 'K2' and
           ec['v143_02']['outcome120'] == ('HOLDS_120', 'held') and ec['v143_02']['outcome'] == 'K2' and
           ec['v143_04']['outcome120'][0] == 'HOLDS_120' and ec['v143_04']['outcome'] == 'HOLDS_120' and
           '    map (A) row %s: outcome on 120 s HOLDS_120 (held); outcome on the whole V K2 (frame dt >= 1 s or tail stall)'
           % LV2 in oc)
ok &= case('C2e the entry print of a V: the K2 frames within 120 s and both outcomes',
           any(x.startswith('  K2 frames within 120 s of presented time after the entry line (item 242 (c)): [(2872, '
                            '1200000, \'hold\')]; outcome on 120 s: K2') for x in oc))
LATE = [FILL] * 8000
BOOM = 'Unhandled exception: access violation'


def with_marker(at, line, level=LV1):
    """scene_lines with the line inserted after post row `at` (cumulative 3.52 s + 40 ms per row)."""
    out = scene_lines(level, LATE)
    i = out.index(ft(14 + at, FILL))
    return out[:i + 1] + [line] + out[i + 1:]


e = S.entry_of('v143_01', mk143(BASE / 'C3a', 'v143_01', with_marker(3500, BOOM)), PRED_SHA)
ok &= case('C3 a log death marker after 120 s (row 3500, 143.5 s): on 120 s HOLDS_120, on the whole V K1',
           e['outcome120'][0] == 'HOLDS_120' and e['outcome'] == 'K1')
e = S.entry_of('v143_01', mk143(BASE / 'C3b', 'v143_01', with_marker(2000, BOOM)), PRED_SHA)
ok &= case('C3b a log death marker before 120 s (row 2000, 83.5 s): K1 on 120 s and on the whole V',
           e['outcome120'][0] == 'K1' and e['outcome'] == 'K1')
R3 = BASE / 'C3c'
mk143(R3, 'v143_01', scene_lines(LV1, LATE))
(R3 / 'stdout_v143_01.txt').write_bytes(b'--- Fatal Error ---\n')
e = S.entry_of('v143_01', str(R3), PRED_SHA)
ok &= case('C3c a stdout marker with a cut: not on 120 s (no time), K1 on the whole V',
           e['outcome120'][0] == 'HOLDS_120' and e['outcome'] == 'K1')
R3d = BASE / 'C3d'
mk143(R3d, 'v143_01', scene_lines(LV1, [FILL] * 100), js143('v143_01', attempt=dict(hold_s=130.0)))
(R3d / 'stdout_v143_01.txt').write_bytes(b'--- Fatal Error ---\n')
e = S.entry_of('v143_01', str(R3d), PRED_SHA)
ok &= case('C3d without a cut (the log never passes 120 s) a stdout marker counts on 120 s too: K1',
           e['outcome120'][0] == 'K1' and e['derive']['cut120_pos'] is None)
e = S.entry_of('v143_01', mk143(BASE / 'C3e', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(hold_exit=3221225477))), PRED_SHA)
ok &= case('C3e hold_exit with a cut: on 120 s HOLDS_120, on the whole V K1', e['outcome120'][0] == 'HOLDS_120'
           and e['outcome'] == 'K1')
e = S.entry_of('v143_01', mk143(BASE / 'C3f', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(ft_tail=0))), PRED_SHA)
ok &= case('C3f the tail stall with a cut: on 120 s HOLDS_120, on the whole V K2', e['outcome120'][0] == 'HOLDS_120'
           and e['outcome'] == 'K2')
e = S.entry_of('v143_01', mk143(BASE / 'C3g', 'v143_01', scene_lines(LV1, [FILL] * 100),
                                js143('v143_01', attempt=dict(ft_tail=0))), PRED_SHA)
ok &= case('C3g the tail stall without a cut: K2 on 120 s', e['outcome120'] == ('K2', 'tail stall'))
e = S.entry_of('v143_01', mk143(BASE / 'C3h', 'v143_01', scene_lines(LV1, [FILL] * 100),
                                js143('v143_01', attempt=dict(hold_exit=3221225477))), PRED_SHA)
ok &= case('C3h hold_exit without a cut: K1 on 120 s', e['outcome120'][0] == 'K1')
e = S.entry_of('v143_01', mk143(BASE / 'C3i', 'v143_01', [ft(i, 16667) for i in range(1, 50)],
                                js143('v143_01', attempt=dict(outcome='timeout', hold_s=None))), PRED_SHA)
ok &= case('C3i not entered: NOT_ENTERED on 120 s', e['outcome120'][0] == 'NOT_ENTERED')
sc_lines = scene_lines(LV1, LATE[:3500]) + [start('other_level')] + [ft(9000 + i, FILL) for i in range(10)]
e = S.entry_of('v143_01', mk143(BASE / 'C3j', 'v143_01', sc_lines), PRED_SHA)
ok &= case('C3j a scene change after 120 s: on 120 s HOLDS_120 (the change is not seen), on the whole V NOT_EVALUABLE',
           e['outcome120'][0] == 'HOLDS_120' and e['outcome'] == 'NOT_EVALUABLE')
sc_lines = scene_lines(LV1, LATE[:1000]) + [start('other_level')] + [ft(9000 + i, FILL) for i in range(4000)]
e = S.entry_of('v143_01', mk143(BASE / 'C3k', 'v143_01', sc_lines), PRED_SHA)
ok &= case('C3k a scene change before 120 s: NOT_EVALUABLE on 120 s', e['outcome120'] == ('NOT_EVALUABLE', 'scene change'))
sc_lines = scene_lines(LV1, LATE[:100] + [1200000] + LATE[:100]) + [start('other_level')] + [ft(9000 + i, FILL)
                                                                                               for i in range(4000)]
e = S.entry_of('v143_01', mk143(BASE / 'C3l', 'v143_01', sc_lines), PRED_SHA)
ok &= case('C3l a K2 frame before a scene change before 120 s: K2 on 120 s', e['outcome120'][0] == 'K2')
sc_lines = with_marker(500, BOOM)
sc_lines = sc_lines[:sc_lines.index(ft(14 + 1000, FILL))] + [start('other_level')] + [ft(9000 + i, FILL) for i in range(4000)]
e = S.entry_of('v143_01', mk143(BASE / 'C3m', 'v143_01', sc_lines), PRED_SHA)
ok &= case('C3m a log marker before a scene change before 120 s: its class on 120 s', e['outcome120'][0] == 'K1')
e = S.entry_of('v143_01', mk143(BASE / 'C3n', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(outcome='exited'))), PRED_SHA)
ok &= case('C3n an exited attempt is K1 on 120 s', e['outcome120'][0] == 'K1')
e = S.entry_of('v143_01', mk143(BASE / 'C3o', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(outcome='timeout'))), PRED_SHA)
ok &= case('C3o an attempt not stable is NOT_EVALUABLE on 120 s', e['outcome120'] == ('NOT_EVALUABLE', 'no stable (timeout)'))
e = S.entry_of('v143_01', mk143(BASE / 'C3p', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(hold_s=119.9))), PRED_SHA)
ok &= case('C3p hold_s 119.9 is NOT_EVALUABLE on 120 s', e['outcome120'][0] == 'NOT_EVALUABLE')
e = S.entry_of('v143_01', mk143(BASE / 'C3q', 'v143_01', scene_lines(LV1, [FILL] * 100)), PRED_SHA)
ok &= case('C3q presented time after the entry line < 120 s: NOT_EVALUABLE on 120 s',
           e['outcome120'] == ('NOT_EVALUABLE', 'presented time after the entry line < 120 s'))
e = S.entry_of('v143_01', mk143(BASE / 'C3r', 'v143_01', scene_lines(LV1, [], first_draws=50) +
                                [ft(15 + i, FILL, 50) for i in range(4000)]), PRED_SHA)
ok &= case('C3r no first scene frame: NOT_EVALUABLE on 120 s', e['outcome120'] == ('NOT_EVALUABLE', 'no first scene frame'))
e = S.entry_of('v143_01', mk143(BASE / 'C3s', 'v143_01', scene_lines(LV1, LATE),
                                js143('v143_01', attempt=dict(hold_s=120.0))), PRED_SHA)
ok &= case('C3s hold_s exactly 120 is enough on 120 s: HOLDS_120', e['outcome120'] == ('HOLDS_120', 'held'))
e = S.entry_of('v143_01', mk143(BASE / 'C3t', 'v143_01', scene_lines(LV1, [FILL] * 2912)), PRED_SHA)
ok &= case('C3t exactly 120 000 000 us presented after the entry line: no cut, HOLDS_120 on 120 s',
           e['derive']['cut120_pos'] is None and e['derive']['dt_after_entry_us'] == 120000000 and
           e['outcome120'] == ('HOLDS_120', 'held'))
RW = BASE / 'C4'
WK2 = [VF] + scene_lines(LV1, [16667] * 700 + [1200000] + [150000] * 2000) + [VW] * 3
mk143(RW, 'w143_01', WK2)
mk143(RW, 'v143_01', scene_lines(LV1, [16667] * 700 + [1200000] + list(v_post())))
ew = S.entry_of('w143_01', str(RW), PRED_SHA)
ev = S.entry_of('v143_01', str(RW), PRED_SHA)
fw = S.fmt_entry(ew)
ok &= case('C4 a W with a frame dt 1.2 s: the outcome has no dt rule (HOLDS_120), the frame is an info line; the V with the '
           'same frame is K2; the W has no outcome on 120 s',
           ew['outcome'] == 'HOLDS_120' and ew['outcome_vx'] == 'HOLDS_120' and ev['outcome'] == 'K2'
           and ew['outcome120'] is None and
           any(x.startswith('  frames dt >= 1 s after the first scene frame: [(715, 1200000, \'hold\')] (info, under '
                            'validation, not classified') for x in fw) and not any(x.startswith('  K2 frames') for x in fw))
mk143(RW / 'b', 'w143_01', WK2, js143('w143_01', attempt=dict(ft_tail=0)))
ok &= case('C4b a W with the tail stall stays K2', S.entry_of('w143_01', str(RW / 'b'), PRED_SHA)['outcome'] == 'K2')
REP = ['--- Build ---', 'v0.0.0 label', '--- Error ---', '[Vulkan][E][1]: Validation Error: [ VUID-x ] bad', ' in vulkanWindow.cpp:912']
vc = S.entry_of('v143_01', mk143(RW / 'c', 'v143_01'), PRED_SHA)
wc = S.entry_of('w143_01', mk143(RW / 'c', 'w143_01', WK2), PRED_SHA)
ok &= case('C4c the W SCENE_OK has no dt row: a W with a frame dt 1.2 s and a good V -> YES',
           S.scene_ok(vc, wc, 'viewed')[0] == 'YES')


def wstop(name, rep, tag='w143_01', std=False):
    base = ([VF] + scene_lines(LV1, [150000] * 300) + [VW]) if tag in S.W_TAGS else scene_lines(LV1, LATE)
    root = mk143(BASE / name, tag, base if std else base + rep)
    if std:
        Path(root, 'stdout_%s.txt' % tag).write_bytes(('\n'.join(rep) + '\n').encode())
    return S.entry_of(tag, root, PRED_SHA)


e = wstop('C5a', REP)
ok &= case('C5 "--- Error ---" with [Vulkan][E] in its report -> VALIDATION_STOP (not K1), outcome VALIDATION_STOP',
           [m['cls'] for m in e['marks']] == ['VALIDATION_STOP'] and e['outcome'] == 'VALIDATION_STOP'
           and e['outcome_vx'] == 'VALIDATION_STOP' and 'first death marker --- Error ---' in e['reason'])
w5, rows5 = S.scene_ok(S.entry_of('v143_01', mk143(BASE / 'C5a', 'v143_01'), PRED_SHA), e, 'viewed')
ok &= case('C5b such a W fails SCENE_OK by its death-marker row and its [Vulkan][E] row only',
           w5 == 'NO' and sorted(r[0] for r in rows5 if not r[1]) == ['W 0 [Vulkan][E] lines',
                                                                     'W 0 death markers (incl. hold_exit, exited)'])
e = wstop('C5c', ['--- Build ---', 'v0', '--- Error ---', 'Error: something', ' in graphicsRun.cpp:77', '[Vulkan][E][1]: x'])
ok &= case('C5c a [Vulkan][E] line after the location line is not in the report -> K1', e['outcome'] == 'K1')
e = wstop('C5d', ['--- Build ---', 'v0', '--- Error ---', 'Error: one', '--- Build ---', '[Vulkan][E][1]: x'])
ok &= case('C5d a [Vulkan][E] line after the next "--- Build ---" is not in the report -> K1', e['outcome'] == 'K1')
e = wstop('C5e', ['--- Error ---'] + ['filler %d' % i for i in range(49)] + ['[Vulkan][E][1]: x'])
e2 = wstop('C5f', ['--- Error ---'] + ['filler %d' % i for i in range(50)] + ['[Vulkan][E][1]: x'])
ok &= case('C5e the report is at most 50 lines after the title: line 50 counts, line 51 does not',
           e['outcome'] == 'VALIDATION_STOP' and e2['outcome'] == 'K1')
e = wstop('C5g', REP, std=True)
ok &= case('C5g the report in the emulator stdout -> VALIDATION_STOP (src stdout)',
           [(m['cls'], m['src']) for m in e['marks']] == [('VALIDATION_STOP', 'stdout')])
e = wstop('C5h', ['--- Build ---', 'v0', '--- Fatal Error ---', '[Vulkan][E][1]: x', ' in a.cpp:1'])
ok &= case('C5h "--- Fatal Error ---" with [Vulkan][E] stays K1 (only "--- Error ---" is the validation exit)',
           e['outcome'] == 'K1')
e = wstop('C5i', REP, tag='v143_01')
ok &= case('C5i the class is read by the report in profile 143 for a V too', e['marks'][0]['cls'] == 'VALIDATION_STOP')
e = wstop('C5l', ['--- Build ---', 'v0', '--- Error ---', '[Vulkan][W][1]: a warning', ' in a.cpp:1'])
ok &= case('C5l a report with a [Vulkan][W] line (not E) is not a validation stop -> K1', e['outcome'] == 'K1')
e = wstop('C5m', ['GpuHangAbort: --- Error ---', '[Vulkan][E][1]: x', ' in a.cpp:1'])
ok &= case('C5m a line carrying GpuHangAbort: and --- Error ---: only the --- Error --- mark becomes VALIDATION_STOP',
           sorted((m['kind'], m['cls']) for m in e['marks']) == [('--- Error ---', 'VALIDATION_STOP'), ('GpuHangAbort:', 'K2')])
wstop('C5j', REP)
lg = S.scan(str(BASE / 'C5j' / 'log_w143_01.txt'))
old = S.profile(S.P142)
r142 = S.build('w142', SKY, js_for('w142'), lg, None, None, str(BASE / 'C5j'), PRED_SHA)
S.profile(old)
ok &= case('C5j profile 142 keeps the reading of s142: the same report -> K1 (the scan still finds it)',
           [m['cls'] for m in r142['marks']] == ['K1'] and len(lg['err_vk']) == 1)
ok &= case('C5k err_reports on a file: the position of the "--- Error ---" line whose report carries [Vulkan][E]',
           len(S.scan(str(BASE / 'C5a' / 'log_w143_01.txt'))['err_vk']) == 1 and
           S.scan(str(BASE / 'C5c' / 'log_w143_01.txt'))['err_vk'] == set())
RP = BASE / 'C6'
v6, w6, p6 = pair143('C6')
ok &= case('C6 the pair row passes with the log sha of times.txt and the json level of both',
           row_ok(S.scene_ok(v6, w6, 'viewed', p6)[1], 'V v143_01 and W w143_01 are the pair of one level') is True)
Path(BASE / 'C6' / 'log_v143_01.txt').write_bytes(Path(BASE / 'C6' / 'log_v143_01.txt').read_bytes() + b'x\n')
v6b = S.entry_of('v143_01', str(BASE / 'C6'), PRED_SHA)
ok &= case('C6b a replaced V log (its sha != the enter_scene end line of times.txt) -> the pair row FAIL',
           row_ok(S.scene_ok(v6b, w6, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False and v6b['times_log_sha'] is not None)
v6c, w6c, _ = pair143('C6c')
Path(BASE / 'C6c' / 'log_w143_01.txt').write_bytes(b'other\n')
w6c = S.entry_of('w143_01', str(BASE / 'C6c'), PRED_SHA)
ok &= case('C6c a replaced W log -> FAIL', row_ok(S.scene_ok(v6c, w6c, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False)
v6d, w6d, _ = pair143('C6d', w_js=js143('w143_01', attempt=dict(level=LV2)))
ok &= case('C6d the W json level of another level -> FAIL',
           row_ok(S.scene_ok(v6d, w6d, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False)
v6e, w6e, _ = pair143('C6e', v_js=js143('v143_01', attempt=dict(level=None)))
ok &= case('C6e the V json without a level -> FAIL',
           row_ok(S.scene_ok(v6e, w6e, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False)
v6f, w6f, _ = pair143('C6f')
(BASE / 'C6f' / 'step2' / 'times.txt').write_text('', encoding='utf-8')
v6f = S.entry_of('v143_01', str(BASE / 'C6f'), PRED_SHA)
ok &= case('C6f no enter_scene end line in times.txt -> FAIL', v6f['times_log_sha'] is None and
           row_ok(S.scene_ok(v6f, w6f, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False)
v6g, w6g, _ = pair143('C6g')
with open(BASE / 'C6g' / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
    f.write('2026-10-01T00:00:01Z go143a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\n' % ('ef' * 32))
    f.write('2026-10-01T00:00:02Z go142a v143_01 enter_scene end rc 0 log_v143_01.txt sha256 %s\n' % ('cd' * 32))
v6g = S.entry_of('v143_01', str(BASE / 'C6g'), PRED_SHA)
ok &= case('C6g the LAST enter_scene end line of the chain go143a counts (a go142a line does not)',
           v6g['times_log_sha'] == 'ef' * 32 and row_ok(S.scene_ok(v6g, w6g, 'viewed', p6)[1], 'V v143_01 and W w143_01')
           is False)
v6h, w6h, _ = pair143('C6h')
v6h['log_sha'] = None
v6h['times_log_sha'] = None
ok &= case('C6h no log sha on either side is not equal -> FAIL',
           row_ok(S.scene_ok(v6h, w6h, 'viewed', p6)[1], 'V v143_01 and W w143_01') is False)


def manifest(root, tag, when, files, roots=('shader', 'pipeline', 'glcache'), absent=()):
    (Path(root) / 'runs143').mkdir(parents=True, exist_ok=True)
    (Path(root) / 'runs143' / ('cache_%s.%s.json' % (tag, when))).write_text(json.dumps(dict(
        roots=[[r, 'C:/x/' + r, r not in absent] for r in roots], files=[list(f) for f in files])), encoding='utf-8')


F0 = [('shader', 'a.bin', 10, 1, 'aa' * 32), ('pipeline', 'p.bin', 20, 2, 'bb' * 32), ('glcache', 'd/x.toc', 5, 3, 'cc' * 32)]
F1 = F0 + [('shader', 'b.bin', 11, 4, 'dd' * 32)]
RK = BASE / 'C7'
for t in ('v143_01', 'w143_01', 'v143_02', 'w143_02', 'v143_03'):
    mk143(RK, t)
manifest(RK, 'v143_01', 'before', F0)
manifest(RK, 'v143_01', 'after', F1)
manifest(RK, 'w143_01', 'before', F1)
manifest(RK, 'w143_01', 'after', F1)
manifest(RK, 'v143_02', 'before', F1)
manifest(RK, 'v143_02', 'after', F1)
manifest(RK, 'w143_02', 'before', F1)
manifest(RK, 'w143_02', 'after', F1)
manifest(RK, 'v143_03', 'before', F1)
manifest(RK, 'v143_03', 'after', F1)
o7 = S.summary(str(RK), PRED_SHA, None)[0]
ok &= case('C7 equal manifests: one "same" line per adjacent pair of made tags (4), the run of v143_01 adds one file, '
           'no break',
           sum(1 for x in o7 if x.endswith(': same (shader 2 files, pipeline 1 files, glcache 1 files)')) == 4 and
           '  within v143_01 (before the lock -> after the run): shader +1 -0 ~0; pipeline +0 -0 ~0; glcache +0 -0 ~0' in o7
           and 'FORMS without the tags after the first cache break (item 242 (b)): no break - the forms above stand' in o7
           and o7[o7.index('STOP RULE (item 221 (g)(4)): not met') + 1].startswith('CACHE CONTINUITY (item 242 (b)'))
F2 = [('shader', 'a.bin', 10, 9, 'aa' * 32)] + F1[1:]
manifest(RK, 'v143_02', 'before', F2)
o7b = S.summary(str(RK), PRED_SHA, None)[0]
ok &= case('C7b an mtime changed between w143_01 and v143_02 -> "cache changed between tags" with the root counts; the forms '
           'without v143_02 and later are printed over v143_01 only',
           '  w143_01 -> v143_02: cache changed between tags (shader +0 -0 ~1; pipeline +0 -0 ~0; glcache +0 -0 ~0)' in o7b and
           'FORMS without the tags after the first cache break (before v143_02; item 242 (b)): over V v143_01: B5a 0/10, '
           'B5a variant 120 s 0/10, B5 0/10, B33 0/10 (variant 120 s 0/10)' in o7b)
manifest(RK, 'v143_02', 'before', F1)
F3 = [x for x in F1 if x[0] != 'glcache']
manifest(RK, 'w143_02', 'before', F3, absent=('glcache',))
o7c = S.summary(str(RK), PRED_SHA, None)[0]
ok &= case('C7c a root absent (GLCache gone) between v143_02 and w143_02 -> a break with "presence changed"; the first break '
           'decides the forms',
           '  v143_02 -> w143_02: cache changed between tags (shader +0 -0 ~0; pipeline +0 -0 ~0; glcache +0 -1 ~0 presence '
           'changed)' in o7c and 'FORMS without the tags after the first cache break (before w143_02; item 242 (b)): over V '
           'v143_01,v143_02:' in ' '.join(o7c))
manifest(RK, 'w143_02', 'before', F1)
(RK / 'runs143' / 'cache_w143_02.after.json').unlink()
o7d = S.summary(str(RK), PRED_SHA, None)[0]
ok &= case('C7d a missing manifest -> NOT EVALUABLE, counted as a break (executor variant)',
           '  w143_02 -> v143_03: NOT EVALUABLE (manifest missing: after w143_02) - counted as a break (executor variant)'
           in o7d and any(x.startswith('FORMS without the tags after the first cache break (before v143_03;') for x in o7d))
(RK / 'runs143' / 'cache_w143_02.after.json').write_text('{broken', encoding='utf-8')
ok &= case('C7e a broken manifest reads as missing', S.cache_manifest(str(RK), 'w143_02', 'after') is None and
           S.cache_manifest(str(RK), 'w143_02', 'before') is not None)
ok &= case('C7f a pair with a tag not made has no line (v143_03 -> w143_03)',
           not any(x.startswith('  v143_03 -> w143_03') for x in o7d))
RH = BASE / 'C7h'
for t in ('v143_01', 'w143_01', 'v143_02', 'w143_02'):
    mk143(RH, t)
manifest(RH, 'v143_01', 'after', F0)
manifest(RH, 'w143_01', 'before', F0)
manifest(RH, 'w143_01', 'after', F0)
manifest(RH, 'v143_02', 'before', F1)
manifest(RH, 'v143_02', 'after', F1)
manifest(RH, 'w143_02', 'before', F0)
o7h = S.summary(str(RH), PRED_SHA, None)[0]
ok &= case('C7h two breaks (before v143_02 and before w143_02): the FIRST decides the forms',
           any(x.startswith('FORMS without the tags after the first cache break (before v143_02;') for x in o7h)
           and sum(1 for x in o7h if 'cache changed between tags' in x) == 2)
manifest(RH, 'w143_02', 'before', [F1[0][:4] + ('ee' * 32,)] + F1[1:])
ok &= case('C7i only the sha256 of a file differs -> changed (~1)', S.cache_diff(
    S.cache_manifest(str(RH), 'v143_02', 'after'), S.cache_manifest(str(RH), 'w143_02', 'before'))['shader'] ==
    (0, 0, 1, False))
mk143(RK / 'k2', 'v143_01', k2_at(LV1, 119000000))
mk143(RK / 'k2', 'w143_01')
mk143(RK / 'k2', 'v143_02', k2_at(LV2, 119000000))
manifest(RK / 'k2', 'v143_01', 'after', F0)
manifest(RK / 'k2', 'w143_01', 'before', F0)
manifest(RK / 'k2', 'w143_01', 'after', F0)
manifest(RK / 'k2', 'v143_02', 'before', F1)
o7g = S.summary(str(RK / 'k2'), PRED_SHA, None)[0]
ok &= case('C7g the forms without the tags after the break count the kept V: B5a 1/10 and its variant 1/10 over v143_01',
           'FORMS without the tags after the first cache break (before v143_02; item 242 (b)): over V v143_01: B5a 1/10, '
           'B5a variant 120 s 1/10, B5 0/10, B33 0/10 (variant 120 s 0/10)' in o7g and
           'FORM B5a (a frame dt >= 1 s after the first scene frame): 2/10 [c] (admitted and entered 2)' in o7g)
ok &= case('C8 the seal of 143 names the cache manifest, the lock check, their suite and the three call wrappers of step 2',
           all(n in S.SEALED_NAMES for n in ('cachemf143.py', 'lockcheck143.py', 'test_tools143.py', 'step2/next_one.sh',
                                             'step2/call_one.sh', 'step2/wait_one.sh')) and S.CACHE_ROOTS ==
           ('shader', 'pipeline', 'glcache') and S.VSTOP == 'VALIDATION_STOP' and S.REPORT_LINES == 50)
try:
    ('\n'.join(oc + o7 + o7b + o7c + o7d + o7g + fw)).encode('ascii', errors='strict')
    encc = True
except UnicodeError:
    encc = False
ok &= case('C9 every line new in link 1b is ASCII', encc)
ok &= case('C10 profile 142 prints no line of link 1b (no 120 s outcome, no map (A) row, no B5a variant, no cache '
           'continuity, no W info line)', not any(s in x for x in outr for s in (
               'outcome on 120 s', 'map (A) row', 'FORM B5a variant', 'K2 ON THE HOLD', 'CACHE CONTINUITY', 'FORMS without',
               'under validation, not classified', 'json level')) and any('K2 frames (dt >= 1 s' in x for x in outr))
# ================= PART D (session 144, HPP-330; ROADMAP item 254 (e), (k)(1)-(5)): the profile of session 144 - the 33 tags
# and their order, the control W, the cross-session pair (a W of s144 with the V of s143), the W form and its violations,
# the W stopped before / after the first GuestOut line, the stop rules (control, two W, three V), the repeated-entry V, the
# skipped-draw frames by distinct frame= (debt D-7), the regression of profile 143 on a synthetic profile, ASCII.
S.profile(P144)
OLD8 = ('v143_01', 'v143_02', 'v143_03', 'v143_04', 'v143_05', 'v143_06', 'v143_09', 'v143_10')
LV8 = ('spring_punch_sky_aztec', 'booster_construction', 'mini_astro_clock_tower', 'path_maker_mana_tree',
       'spring_punch_monster_cave', 'gulliver_island', 'booster_magic_lamp', 'rocket_space_station')
LV12 = ('rocket_hourglass', 'pot_treasure_cave', 'bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino',
        'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach', 'volcano_mountain', 'voxel_world', 'enemy_gorilla',
        'mini_giants_garden')
SEQ144 = (['w144_00'] + ['w144_%02d' % i for i in range(1, 9)] +
          [x for i in range(9, 21) for x in ('v144_%02d' % i, 'w144_%02d' % i)])
ok &= case('D1 the 33 tags of item 254 (k)(1) in that order; the pairs: the eight v143 V with w144_01..08, then v144_NN / '
           'w144_NN of the twelve levels (mini_giants_garden last); the census = the twelve v144 V; W tags = control + 20',
           list(S.SEQ) == SEQ144 and len(S.SEQ) == 33 and S.CONTROL == ('w144_00', SKY) and
           S.PAIRS[:8] == tuple((v, 'w144_%02d' % (i + 1), lv) for i, (v, lv) in enumerate(zip(OLD8, LV8))) and
           S.PAIRS[8:] == tuple(('v144_%02d' % (i + 9), 'w144_%02d' % (i + 9), lv) for i, lv in enumerate(LV12)) and
           S.CENSUS == tuple(('v144_%02d' % (i + 9), lv) for i, lv in enumerate(LV12)) and S.LEVELS == LV8 + LV12 and
           S.V_TAGS == OLD8 + tuple('v144_%02d' % i for i in range(9, 21)) and
           S.W_TAGS == tuple('w144_%02d' % i for i in range(0, 21)))
ok &= case('D2 the root, seal, chain, runs dir, scorer of 144; the V of another session: root s143, chain go143a, seal '
           'pred/02_sc143.md; their sheet rows are fixed viewed (item 254 (a)); W stop run 2; halves of six',
           S.ROOT == 'C:/kyty/s144' and S.PRED_PATH == 'C:/kyty/s144/pred/01_sc144.md' and S.CHAIN == 'go144a' and
           S.RUNS == 'runs144' and S.SCORER == 'sc144.py' and S.EXTRA is True and S.FORM144 is True and
           sorted(S.XSRC) == sorted(OLD8) and all(S.XSRC[v] == dict(root='C:/kyty/s143', chain='go143a',
                                                                    pred='C:/kyty/s143/pred/02_sc143.md') for v in OLD8)
           and S.XSHEET == OLD8 and S.W_STOP_RUN == 2 and S.HALF == 6 and S.NUMW == {5: 'five', 6: 'six'})
ok &= case('D3 the constants of sc143 after items 242, 246 are unchanged in profile 144 (item 254 (k)(3))',
           (S.SCENE_DRAWS, S.ENTRY_WIN, S.K2_US, S.K3_US, S.HOLD_CENSUS_US, S.HOLD_CENSUS_S, S.HOLD_SCENE_US, S.HOLD_W_S,
            S.HOLD_V_S, S.FRAMES_V, S.COVER_SLACK, S.PRIO_US, S.STOP_RUN, S.HOLD_W_HARNESS_S, S.REPORT_LINES) ==
           (100, 599, 1000000, 100000, 120000000, 120, 300000000, 300, 330, 3000, 100, 50000, 3, 310, 50)
           and S.OPCODE_BASE == {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4} and S.BUILD_SHA == BUILD
           and S.CACHE_ROOTS == ('shader', 'pipeline', 'glcache') and S.VSTOP == 'VALIDATION_STOP')
ok &= case('D4 level_of in 144: control -> Sky Garden; v143_09 and w144_07 -> booster_magic_lamp; v144_20 / w144_20 -> '
           'mini_giants_garden; v143_07 (not a pair of 144), w143_01, v144_08 -> unknown',
           S.level_of('w144_00') == SKY and S.level_of('v143_09') == 'booster_magic_lamp' and
           S.level_of('w144_07') == 'booster_magic_lamp' and S.level_of('v144_20') == 'mini_giants_garden' and
           S.level_of('w144_20') == 'mini_giants_garden' and S.level_of('v143_07') is None and
           S.level_of('w143_01') is None and S.level_of('v144_08') is None)
K144 = ('ROOT', 'PRED_PATH', 'CHAIN', 'RUNS', 'SCORER', 'EXTRA', 'FORM144', 'LEVELS', 'PAIRS', 'CENSUS', 'SEQ', 'V_TAGS',
        'W_TAGS', 'SEALED_NAMES', 'CONTROL', 'XSRC', 'XSHEET', 'HALF')
ok &= case('D5 the profiles 143 and 142 set every key the profile 144 changes (FORM144 off, no control, no other-session V, '
           'halves of five)', all(set(K144) <= set(p) for p in (S.P143, S.P142)) and
           all(p['FORM144'] is False and p['CONTROL'] is None and p['XSRC'] == {} and p['XSHEET'] == () and p['HALF'] == 5
               for p in (S.P143, S.P142)) and S.P143['SEQ'][0] == 'v143_01' and len(S.P143['SEQ']) == 20)
PR4 = BASE / 'pred144.md'
PR4.write_text('fixture seal 144 part D\n', encoding='utf-8')
SH4 = hashlib.sha256(PR4.read_bytes()).hexdigest()
PRE = ('PipelinePrecache: 1842 recipes -> 1660 graphics + 141 compute pipelines queued, 41 skipped, 3456 sources loaded, '
       'complete, 492 ms')


def js144(tag, attempt=None, form=True, **over):
    is_w = tag in S.W_TAGS
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x'] + (['--vulkan-validation', 'true'] if is_w else [])
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl %s' % S.level_of(tag), 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    if is_w:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        if form:
            env['KYTY_PIPELINE_PRECACHE'] = '0'
    else:
        env['KYTY_REC'] = 'C:\\kyty\\s144\\rec_%s.mp4' % tag
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,
             pipeline_cache_off=False, level=S.level_of(tag))
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD, guest_args='-lvl %s' % S.level_of(tag), gates='', env=env, cmdline=cmd,
              prereg=dict(path=S.PRED_PATH, sha256=SH4), attempts=[a])
    js.update(over)
    return js


def wl(lv, post=None):
    return [VF] + scene_lines(lv, [150000] * 2000 if post is None else post) + [VW] * 3


def mk144(root, tag, lines=None, js=None, glitch=(3200, 0), sheet=True, chain='go144a', std=()):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    is_w = tag in S.W_TAGS
    lv = S.level_of(tag)
    if lines is None:
        lines = wl(lv) if is_w else [PRE] + scene_lines(lv, v_post())
    (root / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js144(tag)), encoding='utf-8')
    (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / 'step2').mkdir(exist_ok=True)
    with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
        f.write('2026-10-01T00:00:00Z %s %s enter_scene end rc 0 log_%s.txt sha256 %s\n' % (
            chain, tag, tag, _h.sha256((root / ('log_%s.txt' % tag)).read_bytes()).hexdigest()))
    (root / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(std) + '\n').encode('utf-8'))
    (root / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if is_w:
        return str(root)
    if glitch is not None:
        (root / ('glitch_%s.txt' % tag)).write_text('C:/kyty/s144/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                    'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-10-01T00:00:00Z %s %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\n' % (
                chain, tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-10-01T00:00:00Z %s %s sheet rc 0 sheet_%s.png sha256 %s\n' % (
                chain, tag, tag, _h.sha256(b'png').hexdigest()))
    return str(root)


XSRC_REAL = dict(S.XSRC)


def xroot(name, tags=OLD8, js_over=None, lines=None):
    """A fixture root of 'session 143' with the given v143 V (chain go143a, its own seal), and S.XSRC pointed at it."""
    xr = BASE / name / 'x143'
    xr.mkdir(parents=True, exist_ok=True)
    xp = xr / 'pred143.md'
    xp.write_text('fixture seal 143\n', encoding='utf-8')
    xs = hashlib.sha256(xp.read_bytes()).hexdigest()
    for v in tags:
        js = js144(v, prereg=dict(path=xp.as_posix(), sha256=xs))
        js.update((js_over or {}).get(v, {}))
        mk144(xr, v, None if lines is None else lines.get(v), js, chain='go143a')
    S.XSRC = dict((v, dict(root=xr.as_posix(), chain='go143a', pred=xp.as_posix())) for v in OLD8)
    return xr, xp


def adm_rows(e, prefix):
    return [a for a in e['admit'] if a[0].startswith(prefix)]


def adm_ok(e):
    return all(a[1] for a in e['admit'])


RD = BASE / 'D6'
for t in ('w144_00', 'w144_01', 'v144_09', 'w144_09'):
    mk144(RD, t)
eD = dict((t, S.entry_of(t, str(RD), SH4)) for t in ('w144_00', 'w144_01', 'v144_09', 'w144_09'))
ok &= case('D6 good control W, W-only tag, V and W of a pair are admitted; the W carries the env and line rows of the form, the '
           'V the env and positive-control rows (one each)',
           all(adm_ok(e) for e in eD.values()) and
           all(len(adm_rows(eD[t], 'W form: ')) == 2 for t in ('w144_00', 'w144_01', 'w144_09')) and
           len(adm_rows(eD['v144_09'], 'V positive control')) == 1 and len(adm_rows(eD['v144_09'], 'V shipped')) == 1
           and eD['v144_09']['precache'] == dict(log=1, stdout=0, any=1) and eD['w144_09']['precache']['log'] == 0)
BADW = [('W without KYTY_PIPELINE_PRECACHE in the env', dict(js=js144('w144_09', form=False))),
        ('W with KYTY_PIPELINE_PRECACHE=1', dict(js=dict(js144('w144_09'), env=dict(js144('w144_09')['env'],
                                                                                       KYTY_PIPELINE_PRECACHE='1')))),
        ('W with the precache line in its log', dict(lines=[PRE] + wl('rocket_hourglass'))),
        ('W stopped during the startup precache (no line) without the env', dict(
            js=js144('w144_09', form=False), lines=[VF, VW, ft(1, 20000, 5), '--- Fatal Error ---']))]
for i, (name, kw) in enumerate(BADW):
    e = S.entry_of('w144_09', mk144(BASE / ('D7_%d' % i), 'w144_09', **kw), SH4)
    ok &= case('D7 the W form violated -> the tag is not admitted (FAIL): %s' % name,
               not adm_ok(e) and [a[0][:7] for a in e['admit'] if not a[1]] == ['W form:'])
e = S.entry_of('w144_09', mk144(BASE / 'D7o', 'w144_09', std=[PRE]), SH4)
ok &= case('D7c the precache line in the emulator stdout of a W only: an executor member [I] (item 258 (d)) - printed, the tag '
           'stays admitted', adm_ok(e) and e['precache']['stdout'] == 1 and any(
               'executor member [I] (item 258 (d), not in the verdict): the same line in the emulator stdout 1,' in x
               for x in S.fmt_entry(e)))
e = S.entry_of('w144_09', mk144(BASE / 'D7s', 'w144_09', lines=['PipelinePrecache: saved 5 recipes (9 bytes)'] +
                                wl('rocket_hourglass')), SH4)
ok &= case('D7b only the line "PipelinePrecache: N recipes ->" is the form line by the letter: a "saved" line passes and is '
           'printed as "any" 1', adm_ok(e) and e['precache'] == dict(log=0, stdout=0, any=1) and
           any('any "PipelinePrecache:" line 1' in x for x in S.fmt_entry(e)))
BADV = [('V without the precache line (the positive control)', dict(lines=scene_lines('rocket_hourglass', v_post()))),
        ('V run in the W form (KYTY_PIPELINE_PRECACHE=0)', dict(js=dict(js144('v144_09'), env=dict(
            js144('v144_09')['env'], KYTY_PIPELINE_PRECACHE='0'))))]
for i, (name, kw) in enumerate(BADV):
    e = S.entry_of('v144_09', mk144(BASE / ('D8_%d' % i), 'v144_09', **kw), SH4)
    ok &= case('D8 refused V: %s' % name, not adm_ok(e) and len([a for a in e['admit'] if not a[1]]) == 1)
PRD = BASE / 'D9' / 'pred.md'
(BASE / 'D9').mkdir(parents=True, exist_ok=True)
PRD.write_text('fixture seal 144\n', encoding='utf-8')
SHD = hashlib.sha256(PRD.read_bytes()).hexdigest()
mk144(BASE / 'D9', 'w144_09', js=dict(js144('w144_09', form=False), prereg=dict(path=S.PRED_PATH, sha256=SHD)))
mk144(BASE / 'D9', 'v144_09', js=dict(js144('v144_09'), prereg=dict(path=S.PRED_PATH, sha256=SHD)))
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    rw = S.main(['--tag', 'w144_09'], root=str(BASE / 'D9'), pred=str(PRD))
    rv = S.main(['--tag', 'v144_09'], root=str(BASE / 'D9'), pred=str(PRD))
ok &= case('D9 main --tag: a W out of the form -> rc 1 (admission FAIL names the form row); a good V -> rc 0; the score json '
           'goes to runs144', rw == 1 and rv == 0 and 'FAIL W form: KYTY_PIPELINE_PRECACHE=0' in _b.getvalue() and
           (BASE / 'D9' / 'runs144' / 'w144_09.score.json').is_file())
# the cross-session pair
R10 = BASE / 'D10'
xr, xp = xroot('D10')
mk144(R10, 'w144_01')
v10 = S.entry_of('v143_01', str(R10), SH4)
w10 = S.entry_of('w144_01', str(R10), SH4)
word, rows = S.scene_ok(v10, w10, 'viewed', S.PAIRS[0])
ok &= case('D10 a W of s144 with the V of s143 (its root, chain go143a, its seal) -> YES; the V is read from the other root with '
           'that seal; the pair row names its own session', word == 'YES' and v10 is not None and adm_ok(v10) and
           v10['times_log_sha'] == v10['log_sha'] and row_ok(rows, 'V v143_01 and W w144_01 are the pair of one level') is True
           and any('step2/times.txt of its own session; item 254 (e)' in r[0] for r in rows) and len(rows) == 27)
o10 = S.summary(str(R10), SH4, None)[0]
o10b = S.summary(str(R10), SH4, 'not-viewed')[0]
ok &= case('D10b the sheet row of a v143 V is viewed by item 254 (a) whatever --sheet says (unset, not-viewed): YES; its detail '
           'names the item', 'SCENE_OK spring_punch_sky_aztec: YES' in o10 and 'SCENE_OK spring_punch_sky_aztec: YES' in o10b
           and any(x.endswith('(viewed (item 254 (a): viewed at the close of s143))') for x in o10))
ok &= case('D10c the V of another session is printed in its own block (root, chain, seal); a V without its json is named',
           any(x.startswith('V OF ANOTHER SESSION v143_01 (the pair of item 254 (e); root %s, chain go143a, seal %s)'
                            % (xr.as_posix(), xp.as_posix())) for x in o10) and
           'TAG v143_10 (V of another session, root %s): NO JSON' % xr.as_posix() not in o10 and
           any(x.startswith('TAG v143_') and 'not made' in x for x in o10) is False)
Path(xr, 'log_v143_01.txt').write_bytes(Path(xr, 'log_v143_01.txt').read_bytes() + b'x\n')
v11 = S.entry_of('v143_01', str(R10), SH4)
ok &= case('D11 a replaced V log of s143 (sha != its enter_scene end line of the s143 times.txt) -> the pair row FAIL, NO',
           S.scene_ok(v11, w10, 'viewed', S.PAIRS[0])[0] == 'NO' and
           row_ok(S.scene_ok(v11, w10, 'viewed', S.PAIRS[0])[1], 'V v143_01 and W w144_01') is False)
xr, xp = xroot('D12')
tp = xr / 'step2' / 'times.txt'
tp.write_text(tp.read_text(encoding='utf-8').replace(' go143a v143_01 enter_scene end ', ' go144a v143_01 enter_scene end '),
              encoding='utf-8')
v12 = S.entry_of('v143_01', str(R10), SH4)
ok &= case('D12 the enter_scene end line of the V written under the chain go144a (not its own go143a) -> no times sha, FAIL',
           v12['times_log_sha'] is None and row_ok(S.scene_ok(v12, w10, 'viewed', S.PAIRS[0])[1], 'V v143_01 and W w144_01')
           is False)
xr, xp = xroot('D13', js_over={'v143_01': dict(guest_args='-lvl booster_construction')})
v13 = S.entry_of('v143_01', str(R10), SH4)
ok &= case('D13 the V of s143 run for another level (guest args) -> V not admitted and the pair row FAIL',
           not adm_ok(v13) and row_ok(S.scene_ok(v13, w10, 'viewed', S.PAIRS[0])[1], 'V v143_01 and W w144_01') is False)
xr, xp = xroot('D14', js_over={'v143_01': dict(prereg=dict(path=S.PRED_PATH, sha256=SH4))})
v14 = S.entry_of('v143_01', str(R10), SH4)
ok &= case('D14 the V of s143 must carry the seal of s143: a json with the seal of 144 -> V not admitted, NO',
           not adm_ok(v14) and S.scene_ok(v14, w10, 'viewed', S.PAIRS[0])[0] == 'NO')
xr, xp = xroot('D15')
xp.write_text('the seal of 143 changed\n', encoding='utf-8')
v15 = S.entry_of('v143_01', str(R10), SH4)
ok &= case('D15 the seal of s143 changed after the V ran (its sha now != the json) -> V not admitted', not adm_ok(v15))
R16 = BASE / 'D16'
mk144(R16, 'v143_01', js=js144('v143_01'))
mk144(R16, 'w144_01')
S.XSRC = dict((v, dict(root=(BASE / 'D16' / 'none').as_posix(), chain='go143a', pred='none.md')) for v in OLD8)
ok &= case('D16 a v143 V lying in the s144 root is not read (the V of another session comes from its own root only) -> V made '
           'FAIL', S.entry_of('v143_01', str(R16), SH4) is None and
           row_ok(S.scene_ok(None, S.entry_of('w144_01', str(R16), SH4), 'viewed', S.PAIRS[0])[1], 'V made') is False)
xr, xp = xroot('D17')
v17 = S.entry_of('v143_02', str(R10), SH4)
ok &= case('D17 the V of level 01 of s143 offered as the pair of level 02 (w144_02) -> NO by the pair row',
           S.scene_ok(S.entry_of('v143_01', str(R10), SH4), S.entry_of('w144_01', str(R10), SH4), 'viewed',
                      S.PAIRS[1])[0] == 'NO' and v17 is not None)
# the W stop key: before / after the first GuestOut line
STOPW = [VF, ft(1, 20000, 5)] + REP
e = S.entry_of('w144_09', mk144(BASE / 'D18a', 'w144_09', lines=STOPW), SH4)
ok &= case('D18 a W stopped by validation before the first GuestOut line -> stop key "VALIDATION_STOP --- Error ---", no '
           'GuestOut position, outcome NOT_ENTERED (no entry line)', e['wkey'] == 'VALIDATION_STOP --- Error ---' and
           e['guestout'] is None and e['outcome'] == 'NOT_ENTERED')
e = S.entry_of('w144_09', mk144(BASE / 'D18b', 'w144_09', lines=wl('rocket_hourglass', [150000] * 300) + REP), SH4)
ok &= case('D18b a W stopped in the game after GuestOut (the B35 expectation for mini_giants_garden) -> VALIDATION_STOP, '
           'entered, NO stop key (it does not count for the two-W rule)',
           e['wkey'] is None and e['derive']['entered'] and e['outcome'] == 'VALIDATION_STOP' and e['guestout'] is not None)
e = S.entry_of('w144_09', mk144(BASE / 'D18c', 'w144_09', lines=[VF, ft(1, 20000, 5)], std=REP), SH4)
ok &= case('D18c no GuestOut line in the log and the stop report in the emulator stdout -> key from the stdout marker',
           e['wkey'] == 'VALIDATION_STOP --- Error ---')
e = S.entry_of('w144_09', mk144(BASE / 'D18d', 'w144_09', std=REP), SH4)
ok &= case('D18d a GuestOut line in the log and a marker in the stdout only (no position against the log) -> no key',
           e['wkey'] is None and e['outcome'] == 'VALIDATION_STOP')
e = S.entry_of('w144_09', mk144(BASE / 'D18e', 'w144_09', lines=[VF, ft(1, 20000, 5)],
                                js=js144('w144_09', attempt=dict(outcome='exited', hold_s=None))), SH4)
e2 = S.entry_of('w144_09', mk144(BASE / 'D18f', 'w144_09', lines=[VF, ft(1, 20000, 5)],
                                 js=js144('w144_09', attempt=dict(outcome='timeout', hold_s=None))), SH4)
ok &= case('D18e no GuestOut, no marker: exited -> key "K1 hold_exit / ENDED / exited"; a timeout (no marker) -> no key',
           e['wkey'] == 'K1 hold_exit / ENDED / exited' and e2['wkey'] is None)
e = S.entry_of('w144_09', mk144(BASE / 'D18g', 'w144_09', lines=[VF, ft(1, 20000, 5), 'GpuHangAbort: x', start('')] + REP),
               SH4)
ok &= case('D18g the first marker before the GuestOut line decides the key (GpuHangAbort before, the report after) -> K2',
           e['wkey'] == 'K2 GpuHangAbort:')
lg = BASE / 'D18h'
mk144(lg, 'w144_09', lines=STOPW)
(lg / 'log_w144_09.txt').unlink()
e = S.entry_of('w144_09', str(lg), SH4)
ok &= case('D18h a W without its log has no key and fails the form line row itself (no log is no proof of the form)',
           e['wkey'] is None and [a[1] for a in e['admit'] if a[0].startswith('W form: no')] == [False])
fw = S.fmt_entry(S.entry_of('w144_09', str(BASE / 'D18a'), SH4))
ok &= case('D18i the W print carries the form line and the stop-before-GuestOut line with its key',
           any(x.startswith('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log 0; executor member [I]')
               for x in fw)
           and '  W stop before the first GuestOut line (item 254 (k)(4)): first GuestOut at None; stop key VALIDATION_STOP '
           '--- Error ---' in fw)
ok &= case('D19 stop_check_w: two in a row with one key -> stop; different keys or a keyless W between -> no; the last two of '
           'three', S.stop_check_w([('a', 'K'), ('b', 'K')]) == (True, ['a', 'b']) and
           S.stop_check_w([('a', 'K'), ('b', 'L')]) == (False, []) and
           S.stop_check_w([('a', 'K'), ('b', None), ('c', 'K')]) == (False, []) and
           S.stop_check_w([('a', 'L'), ('b', 'K'), ('c', 'K')]) == (True, ['b', 'c']) and S.stop_check_w([]) == (False, []))


def sc_main(root, tag):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = S.main(['--stop-check', tag], root=str(root), pred=str(PR4))
    return rc, b.getvalue()


R20 = BASE / 'D20'
mk144(R20, 'w144_00')
mk144(R20, 'w144_01', lines=STOPW)
mk144(R20, 'w144_02', lines=STOPW)
r20a = sc_main(R20, 'w144_02')
r20b = sc_main(R20, 'w144_03')
ok &= case('D20 two W in a row stopped before GuestOut with one key: before w144_03 -> rc 5 naming them; before w144_02 (one) '
           '-> rc 0; the control good -> not met',
           r20a[0] == 0 and r20b[0] == 5 and 'STOP RULE W before w144_03 (two W in a row stopped before the first GuestOut line '
           'with one key): STOP w144_01,w144_02' in r20b[1] and 'STOP RULE CONTROL before w144_03: not met' in r20b[1])
R21 = BASE / 'D21'
mk144(R21, 'w144_00')
mk144(R21, 'w144_01', lines=STOPW)
mk144(R21, 'w144_02', lines=wl('booster_construction', [150000] * 300) + REP)
ok &= case('D21 one W stopped before GuestOut and the next stopped in the game after GuestOut -> rc 0 before w144_03',
           sc_main(R21, 'w144_03')[0] == 0)
R22 = BASE / 'D22'
for t in ['w144_%02d' % i for i in range(0, 9)]:
    mk144(R22, t)
mk144(R22, 'v144_09')
mk144(R22, 'w144_09', lines=STOPW)
mk144(R22, 'v144_10')
mk144(R22, 'w144_10', lines=STOPW)
ok &= case('D22 two W separated by a V (w144_09, v144_10, w144_10) count as two W in a row -> rc 5 before v144_11; rc 0 before '
           'w144_10', sc_main(R22, 'v144_11')[0] == 5 and sc_main(R22, 'w144_10')[0] == 0)
R23 = BASE / 'D23'
mk144(R23, 'w144_00', lines=STOPW)
r23 = sc_main(R23, 'w144_01')
ok &= case('D23 the control W stopped by validation -> rc 5 before the first tag; both readings say stop',
           r23[0] == 5 and 'STOP RULE CONTROL before w144_01: STOP; letter stop (death marker VALIDATION_STOP --- Error ---; '
           '[Vulkan][E] 1); executor reading [I] (the gate) stop' in r23[1])
R24 = BASE / 'D24'
mk144(R24, 'w144_00', js=js144('w144_00', form=False))
r24 = sc_main(R24, 'w144_01')
ok &= case('D24 the control W out of the form only (no env, otherwise clean) -> letter pass, the gate (item 254 (k)(7)) stop rc 5',
           r24[0] == 5 and 'letter pass (none); executor reading [I] (the gate) stop (W admitted (W form: KYTY_PIPELINE_PRECACHE=0'
           in r24[1])
R25 = BASE / 'D25'
mk144(R25, 'w144_00', lines=[VF] + [ft(i, 16667, 5) for i in range(1, 50)],
      js=js144('w144_00', attempt=dict(outcome='timeout', hold_s=None, ft_tail=None)))
r25 = sc_main(R25, 'w144_01')
ok &= case('D25 the control W not entered without a marker (timeout) -> letter pass, gate stop rc 5 (W entered FAIL)',
           r25[0] == 5 and 'letter pass (none)' in r25[1] and 'W entered' in r25[1])
R26 = BASE / 'D26'
mk144(R26, 'w144_00', lines=wl(SKY) + ['[Vulkan][E][1]: Validation Error: x'])
r26 = sc_main(R26, 'w144_01')
R27 = BASE / 'D27'
R27.mkdir(parents=True, exist_ok=True)
(R27 / 'attempt_w144_00.txt').write_text('made\n')
r27 = sc_main(R27, 'w144_01')
r27b = sc_main(BASE / 'D27none', 'w144_01')
ok &= case('D26 a [Vulkan][E] line in the control W without a death marker -> letter stop rc 5; an attempt of the control '
           'without json -> gate stop rc 5; a control not made -> "not made", rc 0',
           r26[0] == 5 and 'letter stop ([Vulkan][E] 1)' in r26[1] and r27[0] == 5 and
           'attempt made without json (instrument)' in r27[1] and r27b[0] == 0 and
           'STOP RULE CONTROL before w144_01: not made' in r27b[1])
o27 = S.summary(str(R27), SH4, None)[0]
ok &= case('D26d the summary of a series whose control W attempt has no json: the control line says STOP by the gate',
           any(x.startswith('CONTROL W w144_00 (underwater_aerial_garden, item 254 (k)(4)): STOP; letter (death marker or '
                            '[Vulkan][E]) pass (none); executor reading [I] (any W row or admission row failing; the gate) stop '
                            '(attempt made without json (instrument))') for x in o27))
R28 = BASE / 'D28'
for t in ['w144_%02d' % i for i in range(0, 9)]:
    mk144(R28, t)
for t in ('v144_09', 'w144_09', 'v144_10', 'w144_10', 'v144_11'):
    mk144(R28, t, lines=[ft(i, 16667) for i in range(1, 50)], js=js144(t, attempt=dict(outcome='timeout', hold_s=None)))
r28 = sc_main(R28, 'w144_11')
r28b = sc_main(R28, 'v144_11')
ok &= case('D28 three census V in a row not entered with one key -> rc 5 before w144_11 (the W not entered without a marker '
           'have no key); two of them -> rc 0 before v144_11',
           r28[0] == 5 and 'STOP RULE before w144_11: STOP v144_09,v144_10,v144_11' in r28[1] and r28b[0] == 0)
ok &= case('D28b stop-check of an unknown tag (a v143 V, a 143 tag) -> rc 2',
           sc_main(R28, 'v143_01')[0] == 2 and sc_main(R28, 'w143_01')[0] == 2)
# the summary of profile 144
R29 = BASE / 'D29'
PR29 = R29 / 'pred.md'
R29.mkdir(parents=True, exist_ok=True)
PR29.write_text('fixture seal 144 summary\n', encoding='utf-8')
SH29 = hashlib.sha256(PR29.read_bytes()).hexdigest()
xr, xp = xroot('D29x', tags=('v143_01', 'v143_02'))
SKIP = ['AsyncPipelines: skipped draw (pipeline not ready) frame=5', 'AsyncPipelines: skipped draw (pipeline not ready) frame=5',
        'AsyncPipelines: skipped draw (pipeline not ready) frame=7']
for t in ['w144_%02d' % i for i in range(0, 9)] + ['v144_09', 'w144_09', 'v144_10']:
    lines = None
    if t == 'v144_09':
        lines = [PRE] + scene_lines('rocket_hourglass', v_post()) + SKIP
    if t == 'v144_10':
        lines = [PRE] + scene_lines('pot_treasure_cave', [16667] * 700 + [150000] + list(v_post()))
    if t == 'w144_02':
        lines = STOPW
    mk144(R29, t, lines=lines, js=dict(js144(t), prereg=dict(path=S.PRED_PATH, sha256=SH29)))
o29 = S.summary(str(R29), SH29, None)[0]
o29v = S.summary(str(R29), SH29, 'viewed')[0]
ok &= case('D29 the levels line over 20 pairs: level 01 (v143_01 + w144_01) YES, level 02 (w144_02 stopped) NO, v144_09 pair '
           'PENDING_SHEET without --sheet, YES with viewed',
           'SCENE_OK spring_punch_sky_aztec: YES' in o29 and 'SCENE_OK booster_construction: NO' in o29 and
           'SCENE_OK rocket_hourglass: PENDING_SHEET' in o29 and 'SCENE_OK LEVELS: YES 1, PENDING_SHEET 1, NO 18 of 20' in o29
           and 'SCENE_OK rocket_hourglass: YES' in o29v and 'SCENE_OK LEVELS: YES 2, PENDING_SHEET 0, NO 18 of 20' in o29v)
ok &= case('D30 the control line PASS, the W form line (V 4 of 4 made with the line incl. the two v143, W 10 of 10), the census '
           'header of repeated entries, the map row marked "repeated entry", the halves of six, the W stop line',
           'CONTROL W w144_00 (underwater_aerial_garden, item 254 (k)(4)): PASS; letter (death marker or [Vulkan][E]) pass '
           '(none); executor reading [I] (any W row or admission row failing; the gate) pass (none)' in o29 and
           'W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE 4 of 4 made; '
           'W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log 10 of 10 made; violated: none; executor member [I] (item 258 '
           '(d), not in the verdict; a hit is a question to the lead): W with the line in the emulator stdout: none' in o29 and
           'CENSUS = the V tags v144_09..v144_20, REPEATED entries (item 254 (k)(2)): the map rows and the forms B5 / B5a / B33 '
           'below are of repeated entries, apart from the cold entries of s142 / s143' in o29 and
           'CENSUS made 2 of 12 (of them attempt made without json 0), admitted 2' in o29 and
           any(x.startswith('    map (A) row rocket_hourglass (repeated entry): outcome on 120 s HOLDS_120') for x in o29) and
           'FORMS second reading by the order (shared caches warm from earlier runs): first six B5a 0/6 B5 0/6; last six B5a '
           '0/6 B5 0/6' in o29 and
           'STOP RULE W (item 254 (k)(4): two W in a row stopped before the first GuestOut line with one key): not met; keys '
           'w144_02 VALIDATION_STOP --- Error ---' in o29)
ok &= case('D31 the census forms read the repeated-entry V only (v144_10 K3 on the hold -> B33 1/12); the W and the v143 V are '
           'not in it', 'FORM B33 (a frame 100 ms <= dt < 1 s on the hold after the window): 1/12 [c] (admitted and entered 2) '
           'v144_10; executor variant (the hold within 120 s of presented time after the entry line): 1/12' in o29 and
           not any(x.startswith('  v143_') or x.startswith('  w144_') for x in o29 if ' first ' in x and ' K2 ' in x))
ok &= case('D32 the skipped draws of a V: 3 lines, 2 frames by distinct frame= ids (debt D-7), the reading named in the print',
           '  AsyncPipelines skipped draw: 3 lines, 2 frames (distinct frame= ids, debt D-7; counted, not fatal)' in o29)
xr2 = BASE / 'D29x' / 'x143'
(xr2 / 'v143_01.json').unlink()
o29n = S.summary(str(R29), SH29, None)[0]
ok &= case('D33 the v143 V without its json -> "NO JSON" line and level 01 NO (V made FAIL)',
           'TAG v143_01 (V of another session, root %s): NO JSON' % xr2.as_posix() in o29n and
           'SCENE_OK spring_punch_sky_aztec: NO' in o29n)
mk144(R29, 'w144_09', lines=wl('rocket_hourglass'), js=dict(js144('w144_09', form=False),
                                                           prereg=dict(path=S.PRED_PATH, sha256=SH29)))
o29f = S.summary(str(R29), SH29, 'viewed')[0]
ok &= case('D34 a W out of the form in the summary: the W FORM line names it, its level is NO by "W admitted"',
           any(x.startswith('W FORM (item 254 (e)):') and 'violated: w144_09;' in x for x in o29f) and
           'SCENE_OK rocket_hourglass: NO' in o29f and
           any(x.startswith('  FAIL W admitted (') and 'W form' in x for x in block(o29f, 'SCENE_OK rocket_hourglass: NO')))
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    rsh = S.main(['--summary', '--sheet', 'viewed', '--sheet-tags', 'v144_10'], root=str(R29), pred=str(PR29))
o35 = _b.getvalue().split('\n')
ok &= case('D35 --sheet-tags v144_10: the v144_09 pair falls back to PENDING_SHEET / NO by its rows; the v143 V stay viewed',
           rsh == 0 and 'SCENE_OK rocket_hourglass: NO' in o35 and 'SCENE_OK spring_punch_sky_aztec: NO' in o35 and
           any(x.endswith('(viewed (item 254 (a): viewed at the close of s143))') for x in o35))
CH_OLD = S.CHUNK
S.CHUNK = 64
pj = mk144(BASE / 'D18j', 'w144_09', lines=[VF, VW, ft(1, 20000, 5)] + ['filler line %d' % i for i in range(20)] +
           [start(''), ft(2, 20000, 5)] + ['filler line %d' % i for i in range(20)] + [start('')] + REP)
gj = S.scan(pj + '/log_w144_09.txt')['guestout']
S.CHUNK = CH_OLD
rawj = Path(pj, 'log_w144_09.txt').read_bytes()
ok &= case('D18j the first GuestOut line is kept across chunks (64-byte chunks, two GuestOut lines): its line start',
           gj == rawj.find(b'GuestOut') and gj is not None and rawj.find(b'GuestOut', gj + 1) > gj)
e = S.entry_of('w144_09', mk144(BASE / 'D18k', 'w144_09', lines=[VF, ft(1, 20000, 5), 'GpuHangAbort: x'] + REP + [start('')]),
               SH4)
ok &= case('D18k two markers before the GuestOut line: the FIRST by position gives the key (K2 GpuHangAbort:, not the report)',
           e['wkey'] == 'K2 GpuHangAbort:')
e = S.entry_of('w144_09', mk144(BASE / 'D18l', 'w144_09', js=js144('w144_09', attempt=dict(outcome='exited', hold_s=None))),
               SH4)
ok &= case('D18l a GuestOut line, no marker, exited -> no key (the attempt markers count only without a GuestOut line)',
           e['wkey'] is None and e['exited'])
lm = BASE / 'D18m'
mk144(lm, 'w144_09', lines=STOPW, js=js144('w144_09', attempt=dict(outcome='exited', hold_s=None)))
(lm / 'log_w144_09.txt').unlink()
e = S.entry_of('w144_09', str(lm), SH4)
ok &= case('D18m no log, exited -> no key (a W without its log never counts for the two-W rule)', e['wkey'] is None)
R22b = BASE / 'D22b'
for t in ['w144_%02d' % i for i in range(0, 7)] + ['v144_09']:
    mk144(R22b, t)
mk144(R22b, 'w144_07', lines=STOPW)
mk144(R22b, 'w144_08', lines=STOPW)
(R22b / 'attempt_w144_09.txt').write_text('made\n')
r22b = sc_main(R22b, 'v144_10')
ok &= case('D22b an attempt of a W without json is a made W without a key: it breaks the run of the last two made W '
           '(w144_08 key, w144_09 none) -> rc 0 before v144_10', r22b[0] == 0 and 'keys w144_08 VALIDATION_STOP --- Error ---, '
           'w144_09 None' in r22b[1])
R26b = BASE / 'D26b'
mk144(R26b, 'w144_00', js=js144('w144_00', attempt=dict(outcome='exited')))
r26b = sc_main(R26b, 'w144_01')
R26c = BASE / 'D26c'
mk144(R26c, 'w144_00')
(R26c / 'log_w144_00.txt').unlink()
r26c = sc_main(R26c, 'w144_01')
ok &= case('D26b the control W exited (attempt marker) -> letter stop; the control without its log -> gate stop naming '
           '"log missing"', r26b[0] == 5 and 'letter stop (hold_exit / ENDED / exited)' in r26b[1] and r26c[0] == 5 and
           'log missing' in r26c[1])
mk144(R29, 'v144_10', lines=scene_lines('pot_treasure_cave', v_post()), js=dict(js144('v144_10'),
                                                                                prereg=dict(path=S.PRED_PATH, sha256=SH29)))
o29g = S.summary(str(R29), SH29, 'viewed')[0]
ok &= case('D34b a V without the precache line in the summary: the W FORM line names it before the W',
           any(x.startswith('W FORM (item 254 (e)):') and 'violated: v144_10,w144_09;' in x for x in o29g))
mk144(R29, 'w144_10', std=[PRE], js=dict(js144('w144_10'), prereg=dict(path=S.PRED_PATH, sha256=SH29)))
o29h = S.summary(str(R29), SH29, 'viewed')[0]
ok &= case('D34c a W with the precache line in its emulator stdout: the W FORM line names it as the executor member [I] '
           '(a question to the lead), it is not among the violated', any(x.startswith('W FORM (item 254 (e)):') and
           x.endswith('W with the line in the emulator stdout: w144_10') and 'violated: v144_10,w144_09;' in x for x in o29h))
S.XSRC = dict(XSRC_REAL)
REQ144 = ('go144a.sh', 'sc144.py', 'test_sc144.py', 'mut_sc144.py', 'enter_scene.py', 'sheet142.py', 'fgcpu144.py',
          'test_fgcpu144.py', 'test_go144a.py', 'C:/kyty/scripts/s51_vidglitch.py', 'cachemf144.py', 'lockcheck144.py',
          'test_tools144.py', 'step2/next_one.sh', 'step2/call_one.sh', 'step2/wait_one.sh', 'step2/apichk144.py',
          'C:/kyty/s143/step2/times.txt', 'C:/kyty/s143/pred/02_sc143.md')
ok &= case('D36 the seal of 144 names the harness, scorer, fixtures, mutants, enter_scene.py, sheet142.py, s51_vidglitch.py, '
           'the tools, the step 2 wrappers with the API check, and the s143 times.txt and seal the pairs read',
           all(n in S.SEALED_NAMES for n in REQ144) and len(S.SEALED_NAMES) == 24)
rs4 = BASE / 'seal144'
rs4.mkdir()
shutil.copyfile(SRC, rs4 / 'sc144.py')
ls4 = []
for name in S.SEALED_NAMES:
    if name.startswith('C:/kyty/s143/'):
        sh = 'cd' * 32
    elif name.startswith('C:/'):
        sh = hashlib.sha256(Path(name).read_bytes()).hexdigest()
    elif name != 'sc144.py':
        (rs4 / name).parent.mkdir(parents=True, exist_ok=True)
        (rs4 / name).write_bytes(('fixture ' + name).encode())
        sh = hashlib.sha256((rs4 / name).read_bytes()).hexdigest()
    else:
        sh = hashlib.sha256(Path(SRC).read_bytes()).hexdigest()
    ls4.append('seal: %s %s' % (sh, name))
(rs4 / 'pred.md').write_text('seal 144\n' + '\n'.join(ls4) + '\n', encoding='utf-8')
g4, r4 = S.check_seal(str(rs4 / 'pred.md'), str(rs4), SRC)
ok &= case('D37 the seal check of 144: the scorer by sc144.py; an outside file (C:/...) is hashed at its own path - a wrong '
           'sha of the s143 times.txt fails the check', not g4 and
           [r[0] for r in r4 if not r[1]] == ['C:/kyty/s143/pred/02_sc143.md', 'C:/kyty/s143/step2/times.txt'] and
           [r for r in r4 if r[0] == 'this scorer in the seal'][0][1] is True)
# the regression of item 254 (k)(5) on a synthetic profile 143
RG3 = BASE / 'rg143'
RG3.mkdir()
P143_REAL = dict(S.P143)
B33_143 = S.REGRESS143_B33
S.P143 = dict(S.P143, ROOT=RG3.as_posix(), PRED_PATH=(RG3 / 'pred.md').as_posix())
(RG3 / 'pred.md').write_text('fixture 143 regress\n', encoding='utf-8')
SH3 = hashlib.sha256((RG3 / 'pred.md').read_bytes()).hexdigest()
old = S.profile(S.P143)
mk143(RG3, 'v143_01', None, dict(js143('v143_01'), prereg=dict(path=S.PRED_PATH, sha256=SH3)))
mk143(RG3, 'w143_01', None, dict(js143('w143_01'), prereg=dict(path=S.PRED_PATH, sha256=SH3)))
mk143(RG3, 'v143_02', scene_lines(LV2, [16667] * 700 + [150000] + [16667] * 7300),
      dict(js143('v143_02'), prereg=dict(path=S.PRED_PATH, sha256=SH3)))
mk143(RG3, 'v143_03', scene_lines(LV3, [16667] * 700 + [150000] + [16667] * 7300),
      dict(js143('v143_03'), prereg=dict(path=S.PRED_PATH, sha256=SH3), binary_sha256=OTHER))
out3 = S.summary(str(RG3), SH3, 'viewed')[0]
S.profile(old)
EX3 = RG3 / 'expected.txt'
EX3.write_bytes(('\r\n'.join(out3) + '\r\n').encode('ascii'))
S.REGRESS143_B33 = ('v143_02',)
ok3, l3 = S.regress143(str(EX3))
ok &= case('D38 regress143 on a synthetic profile 143: byte-identical, B33 v143_02 -> PASS; the profile 144 is restored; the '
           'profile 143 summary has no line of 144 (no control, no W FORM, no repeated entry, no stop-W line)',
           ok3 and l3[-1] == 'REGRESS143: PASS' and 'byte-identical yes; differing lines 0' in l3[0] and S.ROOT == 'C:/kyty/s144'
           and S.CHAIN == 'go144a' and S.FORM144 is True and S.SEQ[0] == 'w144_00' and S.XSRC == XSRC_REAL and
           'SCENE_OK spring_punch_sky_aztec: YES' in out3 and
           not any(s in x for x in out3 for s in ('CONTROL W', 'W FORM', 'repeated entry', 'STOP RULE W', 'precache form',
                                                 'distinct frame=', 'of its own session', 'V OF ANOTHER SESSION')))
EX3.write_bytes(('\r\n'.join(out3[:3] + ['changed'] + out3[4:]) + '\r\n').encode('ascii'))
ok3b, l3b = S.regress143(str(EX3))
EX3.write_bytes(('\n'.join(out3) + '\n').encode('ascii'))
ok3c, l3c = S.regress143(str(EX3))
EX3.write_bytes(('\r\n'.join(out3) + '\r\n').encode('ascii'))
S.REGRESS143_B33 = ('v143_01',)
ok3d = S.regress143(str(EX3))[0]
S.REGRESS143_B33 = ('v143_02',)
ok3e = S.regress143(str(BASE / 'none143.txt'))[0]
ok &= case('D39 regress143 fails on a changed line (DIFF line 4 printed), on LF only, on other B33 tags, on a missing file',
           not ok3b and 'DIFF line 4 expected: changed' in l3b and not ok3c and 'byte-identical NO; differing lines 0' in l3c[0]
           and not ok3d and not ok3e)
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    rr3 = S.main(['--regress143'])
ok &= case('D40 main --regress143 -> rc 1 against the real s143 summary from the fixture root', rr3 == 1 and
           'REGRESS143: FAIL' in _b.getvalue())
S.P143 = P143_REAL
S.REGRESS143_B33 = B33_143
ok &= case('D41 the real profile 143 and the regression constants of item 254 (g)(4), (k)(5)',
           S.P143['ROOT'] == 'C:/kyty/s143' and S.P143['PRED_PATH'] == 'C:/kyty/s143/pred/02_sc143.md' and
           S.P143['CHAIN'] == 'go143a' and S.P143['RUNS'] == 'runs143' and S.P143['SCORER'] == 'sc143.py' and
           S.REGRESS143_B33 == ('v143_02', 'v143_07', 'v143_08', 'v143_09') and
           S.REGRESS143_FILE == 'C:/kyty/s143/step4/summary143_viewed.txt' and S.REGRESS_FILE ==
           'C:/kyty/s142/step4/summary142_viewed.txt')
try:
    ('\n'.join(o10 + o29 + o29v + o29n + o29f + o35 + fw + l3 + l3b + r20b[1].split('\n') + r23[1].split('\n') +
               r24[1].split('\n'))).encode('cp1250', errors='strict')
    ('\n'.join(o10 + o29 + o29f + fw + l3)).encode('ascii', errors='strict')
    encd = True
except UnicodeError:
    encd = False
ok &= case('D42 every line new in profile 144 is ASCII (strict cp1250 and ascii)', encd)
# ================= PART E (session 145, HPP-350; ROADMAP item 273 (k)(1)-(5)): the profile of session 145 - the 34 tags and
# their order, the control W, the W repeat of rocket_hourglass paired with the V v144_09 of s144, the cold census, the W filter
# of one message, the window event (minimized / Recovering without minimized / stdout / other window lines / chunks), the layer
# limit (control 0 required, other W "layer truncated"), the video continuity of B38 (gap, margin, before/after the first scene
# frame, longest run), the stop rule of the window event, the summary lines, the regression of profile 144 on a synthetic
# profile, the real constants, ASCII.
S.profile(P145)
LV16 = ('small_pot_lava', 'spin_drill_natural_cave', 'enemy_taco', 'jack_in_the_box', 'final_shooting', 'picup_light',
        'enemy_snake', 'light_gadget_graveyard', 'shuriken_ninja_castle', 'final_stage', 'mini_rocket_chain',
        'enemy_chameleon', 'bonus_path_maker_mix', 'enemy_bird', 'cymbal_party_land', 'enemy_final')
SEQ145 = ['w145_00', 'w145_01'] + [x for i in range(2, 18) for x in ('v145_%02d' % i, 'w145_%02d' % i)]
FILT = 'Undefined-Value-ShaderOutputNotConsumed-DynamicRendering'
ok &= case('E1 the 34 tags of item 273 (k)(1) in that order; the pairs: v144_09 with w145_01, then v145_NN / w145_NN of the '
           'sixteen levels (enemy_final last); the census = the sixteen v145 V; W tags = control + 17',
           list(S.SEQ) == SEQ145 and len(S.SEQ) == 34 and S.CONTROL == ('w145_00', SKY) and
           S.PAIRS[0] == ('v144_09', 'w145_01', 'rocket_hourglass') and len(S.PAIRS) == 17 and
           S.PAIRS[1:] == tuple(('v145_%02d' % (i + 2), 'w145_%02d' % (i + 2), lv) for i, lv in enumerate(LV16)) and
           S.CENSUS == tuple(('v145_%02d' % (i + 2), lv) for i, lv in enumerate(LV16)) and
           S.LEVELS == ('rocket_hourglass',) + LV16 and
           S.V_TAGS == ('v144_09',) + tuple('v145_%02d' % i for i in range(2, 18)) and
           S.W_TAGS == tuple('w145_%02d' % i for i in range(0, 18)))
ok &= case('E2 the root, seal, chain, runs dir, scorer of 145; the V of another session: v144_09 from root s144, chain go144a, '
           'seal pred/01_sc144.md; its sheet row fixed viewed by item 273 (a); halves of eight; the W form line; the flags',
           S.ROOT == 'C:/kyty/s145' and S.PRED_PATH == 'C:/kyty/s145/pred/03_sc145.md' and S.CHAIN == 'go145a' and
           S.RUNS == 'runs145' and S.SCORER == 'sc145.py' and S.EXTRA is True and S.FORM144 is True and
           S.FORM145 is True and S.REPEAT is False and
           S.XSRC == {'v144_09': dict(root='C:/kyty/s144', chain='go144a', pred='C:/kyty/s144/pred/01_sc144.md')} and
           S.XSHEET == ('v144_09',) and S.XSHEET_NOTE == ' (item 273 (a): viewed at the close of s144)' and
           S.W_STOP_RUN == 2 and S.HALF == 8 and S.NUMW == {5: 'five', 6: 'six'} and
           S.W_FORM_LINE == 'W form: limit=100000000 filter=none')
ok &= case('E3 the constants of sc144 are unchanged in profile 145 (item 273 (k)(3))',
           (S.SCENE_DRAWS, S.ENTRY_WIN, S.K2_US, S.K3_US, S.HOLD_CENSUS_US, S.HOLD_CENSUS_S, S.HOLD_SCENE_US, S.HOLD_W_S,
            S.HOLD_V_S, S.FRAMES_V, S.COVER_SLACK, S.PRIO_US, S.STOP_RUN, S.HOLD_W_HARNESS_S, S.REPORT_LINES) ==
           (100, 599, 1000000, 100000, 120000000, 120, 300000000, 300, 330, 3000, 100, 50000, 3, 310, 50)
           and S.OPCODE_BASE == {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4} and S.BUILD_SHA == BUILD
           and S.CACHE_ROOTS == ('shader', 'pipeline', 'glcache') and S.VSTOP == 'VALIDATION_STOP')
ok &= case('E3b the new constants: the gap 60 ms and the margin 12 ms of AUDIT144 s1.3, the window keys, the limit, F6 and '
           'Recovering texts', S.VC_GAP == 0.060 and S.VC_MARG == 0.012 and
           S.WIN_KEYS == ('minimized', 'restored', 'resized', 'size changed', 'lost keyboard focus') and
           S.M_LIMIT == b'this will be the last time reporting it' and S.M_F6 == b'and this write is unused.' and
           S.M_REC == b'Recovering Vulkan swapchain')
ok &= case('E3c the constants of item 295: the end of the hold 10 s, +-2 s of the window line, 8 ms, +-50 ms, 600 rows, 10 %, the '
           '15 window kinds of window.cpp, the s144 W not held',
           S.LAYER_END_US == 10000000 and S.WIN_NEAR_US == 2000000 and S.VQ_NEAR == 0.008 and S.VQ_SHIFT_MS == 50 and
           S.VQ_ROWS == 600 and S.VQ_MARK == 0.10 and
           S.WIN_ALL == ('shown', 'hidden', 'exposed', 'moved to', 'resized', 'size changed', 'minimized', 'maximized',
                         'restored', 'gained keyboard focus', 'lost keyboard focus', 'closed', 'got unknown event',
                         'Mouse entered window', 'Mouse left window') and
           S.REGRESS144_NOTHELD == ('w144_09', 'w144_20') and S.REGRESS144_B3 == S.REGRESS144_LIMIT)
ok &= case('E4 level_of in 145: control -> Sky Garden; v144_09 and w145_01 -> rocket_hourglass; v145_17 / w145_17 -> '
           'enemy_final; v145_01, w144_09, v144_10 -> unknown',
           S.level_of('w145_00') == SKY and S.level_of('v144_09') == 'rocket_hourglass' and
           S.level_of('w145_01') == 'rocket_hourglass' and S.level_of('v145_17') == 'enemy_final' and
           S.level_of('w145_17') == 'enemy_final' and S.level_of('v145_02') == 'small_pot_lava' and
           S.level_of('v145_01') is None and S.level_of('w144_09') is None and S.level_of('v144_10') is None)
K145 = K144 + ('FORM145', 'REPEAT', 'XSHEET_NOTE')
ok &= case('E5 the profiles 144, 143 and 142 set every key the profile 145 changes; P144 keeps the values of sc144 (root s144, '
           'go144a, control w144_00, 33 tags, the v143 V of another session, halves of six, FORM145 off, repeated entries)',
           all(set(K145) <= set(p) for p in (S.P144, S.P143, S.P142)) and
           all(p['FORM145'] is False for p in (S.P144, S.P143, S.P142)) and S.P144['REPEAT'] is True and
           S.P144['ROOT'] == 'C:/kyty/s144' and S.P144['CHAIN'] == 'go144a' and S.P144['CONTROL'] == ('w144_00', SKY) and
           len(S.P144['SEQ']) == 33 and S.P144['SEQ'] == tuple(SEQ144) and S.P144['HALF'] == 6 and
           S.P144['SCORER'] == 'sc144.py' and S.P144['PRED_PATH'] == 'C:/kyty/s144/pred/01_sc144.md' and
           sorted(S.P144['XSRC']) == sorted(OLD8) and S.P144['XSHEET'] == OLD8 and
           S.P144['XSHEET_NOTE'] == ' (item 254 (a): viewed at the close of s143)' and 'apichk144' in ' '.join(
               S.P144['SEALED_NAMES']) and len(S.P144['SEALED_NAMES']) == 24)
REQ145 = ('go145a.sh', 'sc145.py', 'test_sc145.py', 'mut_sc145.py', 'enter_scene.py', 'sheet142.py', 'fgcpu145.py',
          'test_fgcpu145.py', 'test_go145a.py', 'C:/kyty/scripts/s51_vidglitch.py', 'cachemf145.py', 'lockcheck145.py',
          'test_tools145.py', 'step2/next_one.sh', 'step2/call_one.sh', 'step2/wait_one.sh', 'step2/pre_one.sh',
          'step2/apichk145.py', 'step2/gate145.py', 'step2/test_gate145.py', 'C:/kyty/s144/step2/times.txt',
          'C:/kyty/s144/pred/01_sc144.md', 'C:/kyty/s144/runs144/cache_w144_20.after.json')
ok &= case('E6 the seal of 145 names the harness, scorer, fixtures, mutants, enter_scene.py, sheet142.py, s51_vidglitch.py, the '
           'tools, the step 2 wrappers with the API check and the gate, the s144 times.txt and seal the pair reads and the '
           'reference of the gate (item 295 (e)); no name of 144', all(n in S.SEALED_NAMES for n in REQ145) and
           len(S.SEALED_NAMES) == 28 and
           not any('144' in n and not n.startswith('C:/kyty/s144/') for n in S.SEALED_NAMES))
PR5 = BASE / 'pred145.md'
PR5.write_text('fixture seal 145 part E\n', encoding='utf-8')
SH5 = hashlib.sha256(PR5.read_bytes()).hexdigest()


def js145(tag, attempt=None, form=True, filt=None, dup='100000000', **over):
    is_w = tag in S.W_TAGS
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x'] + (['--vulkan-validation', 'true'] if is_w else [])
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl %s' % S.level_of(tag), 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    if is_w:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        if form:
            env['KYTY_PIPELINE_PRECACHE'] = '0'
        if filt is not None:
            env['VK_LAYER_MESSAGE_ID_FILTER'] = filt
        if dup is not None:
            env['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = dup
    else:
        env['KYTY_REC'] = 'C:\\kyty\\s145\\rec_%s.mp4' % tag
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,
             pipeline_cache_off=False, level=S.level_of(tag))
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD, guest_args='-lvl %s' % S.level_of(tag), gates='', env=env, cmdline=cmd,
              prereg=dict(path=S.PRED_PATH, sha256=SH5), attempts=[a])
    js.update(over)
    return js


def mk145(root, tag, lines=None, js=None, glitch=(3200, 0), sheet=True, chain='go145a', std=(), idx=None, extra=()):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    is_w = tag in S.W_TAGS
    lv = S.level_of(tag)
    if lines is None:
        lines = (wl(lv) if is_w else [PRE] + scene_lines(lv, v_post())) + list(extra)
    (root / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js145(tag)), encoding='utf-8')
    (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / 'step2').mkdir(exist_ok=True)
    with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
        f.write('2026-10-01T00:00:00Z %s %s enter_scene end rc 0 log_%s.txt sha256 %s\n' % (
            chain, tag, tag, _h.sha256((root / ('log_%s.txt' % tag)).read_bytes()).hexdigest()))
    (root / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(std) + '\n').encode('utf-8'))
    (root / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if is_w:
        return str(root)
    if idx is not None:
        (root / ('rec_%s.mp4.idx' % tag)).write_text(''.join('%d %d %.3f\n' % (i, i + 1, x) for i, x in enumerate(idx)))
    if glitch is not None:
        (root / ('glitch_%s.txt' % tag)).write_text('C:/kyty/s145/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                    'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-10-01T00:00:00Z %s %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\n' % (
                chain, tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-10-01T00:00:00Z %s %s sheet rc 0 sheet_%s.png sha256 %s\n' % (
                chain, tag, tag, _h.sha256(b'png').hexdigest()))
    return str(root)


XSRC145 = dict(S.XSRC)


def x144root(name, js_over=None, lines=None):
    """A fixture root of 'session 144' with v144_09 (chain go144a, its own seal), and S.XSRC pointed at it."""
    xr = BASE / name / 'x144'
    xr.mkdir(parents=True, exist_ok=True)
    xp = xr / 'pred144.md'
    xp.write_text('fixture seal 144\n', encoding='utf-8')
    xs = hashlib.sha256(xp.read_bytes()).hexdigest()
    js = js145('v144_09', prereg=dict(path=xp.as_posix(), sha256=xs))
    js['env']['KYTY_REC'] = 'C:\\kyty\\s144\\rec_v144_09.mp4'
    js.update(js_over or {})
    mk145(xr, 'v144_09', lines, js, chain='go144a')
    S.XSRC = {'v144_09': dict(root=xr.as_posix(), chain='go144a', pred=xp.as_posix())}
    return xr, xp


WMIN = 'Window 1 minimized'
WREC = 'Recovering Vulkan swapchain (vkQueuePresentKHR: eErrorOutOfDateKHR)'
LIM = ('[Vulkan][W][2]: (Warning - This VUID has now been reported 1000000 times, which is the duplicate_message_limit value, '
       'this will be the last time reporting it).')
F6L = ('[Vulkan][W][2]: vkCmdDrawIndexed(): Inside [VK_SHADER_STAGE_FRAGMENT_BIT] it writes to [Output variable, Location 1, '
       '"out_mrt_1"] but there is no VkRenderingInfo::pColorAttachments[1] and this write is unused.')
RE = BASE / 'E7'
for t in ('w145_00', 'w145_01', 'v145_02', 'w145_02'):
    mk145(RE, t)
eE = dict((t, S.entry_of(t, str(RE), SH5)) for t in ('w145_00', 'w145_01', 'v145_02', 'w145_02'))
ok &= case('E7 good control W, W repeat and the V and W of a pair are admitted; each W carries the four rows of item 295 (b) '
           'and the window row, no filter row; the V the filter row of the shipped defaults and the window row',
           all(adm_ok(e) for e in eE.values()) and
           all([a[0][:11] for a in adm_rows(eE[t], 'W 295(b)(')] == ['W 295(b)(4)', 'W 295(b)(1)', 'W 295(b)(2)',
                                                                     'W 295(b)(3)'] and
               len(adm_rows(eE[t], 'window event: ')) == 1 and not adm_rows(eE[t], 'W filter')
               for t in ('w145_00', 'w145_01', 'w145_02')) and
           len([a for a in eE['v145_02']['admit'] if 'VK_LAYER_MESSAGE_ID_FILTER' in a[0]]) == 1 and
           len(adm_rows(eE['v145_02'], 'window event: ')) == 1 and eE['w145_02']['winev'] is False and
           eE['w145_02']['limit'] == 0 and eE['w145_02']['vcont'] is None)
BADF = [('W with the filter of step 0', js145('w145_02', filt=FILT)),
        ('W with the limit of s144 (1000000)', js145('w145_02', dup='1000000')),
        ('W without the limit', js145('w145_02', dup=None)),
        ('W with the limit and a blank', js145('w145_02', dup='100000000 ')),
        ('W with a filter "none" in the env', js145('w145_02', filt='none')),
        ('W with an empty filter in the env', js145('w145_02', filt=''))]
for i, (name, js) in enumerate(BADF):
    e = S.entry_of('w145_02', mk145(BASE / ('E8_%d' % i), 'w145_02', js=js), SH5)
    ok &= case('E8 the W form line of item 295 (b)(4) violated -> the tag is not admitted by the row (b)(4) only: %s' % name,
               not adm_ok(e) and [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(4)'])
jv = js145('v145_02')
jv['env']['VK_LAYER_MESSAGE_ID_FILTER'] = FILT
e = S.entry_of('v145_02', mk145(BASE / 'E9', 'v145_02', js=jv), SH5)
ok &= case('E9 a V with the filter of the W -> not admitted by "V shipped defaults: no VK_LAYER_MESSAGE_ID_FILTER" only',
           not adm_ok(e) and [a[0] for a in e['admit'] if not a[1]] ==
           ['V shipped defaults: no VK_LAYER_MESSAGE_ID_FILTER in the env (item 273 (k)(2))'])
e = S.entry_of('w145_02', mk145(BASE / 'E10', 'w145_02', lines=wl('small_pot_lava')[:40] + [WMIN, WREC] +
                                wl('small_pot_lava')[40:]), SH5)
fE10 = S.fmt_entry(e)
ok &= case('E10 a W with "Window 1 minimized" and the Recovering line -> the admission row "window event" fails alone; the print '
           'says it is not an outcome of the level and names the gate stop',
           e['winev'] and not adm_ok(e) and [a[0][:13] for a in e['admit'] if not a[1]] == ['window event:'] and
           e['win']['minimized'] == 1 and e['win']['recovering'] == 1 and
           any(x.startswith('  window events (item 273 (k)(3)): minimized 1, restored 0, resized 0, size changed 0, lost '
                            'keyboard focus 0, Recovering Vulkan swapchain 1 -> WINDOW EVENT: not an outcome of the level')
               for x in fE10))
e = S.entry_of('w145_02', mk145(BASE / 'E11', 'w145_02', extra=[WREC]), SH5)
ok &= case('E11 "Recovering Vulkan swapchain" without any "minimized" line -> a window event (the admission row fails); the '
           'print names minimized 0 and Recovering 1',
           e['winev'] and e['win']['minimized'] == 0 and e['win']['recovering'] == 1 and not adm_ok(e) and
           any(x.startswith('  window events (item 273 (k)(3)): minimized 0, restored 0, resized 0, size changed 0, lost '
                            'keyboard focus 0, Recovering Vulkan swapchain 1 -> WINDOW EVENT') for x in S.fmt_entry(e)))
e = S.entry_of('w145_02', mk145(BASE / 'E11b', 'w145_02', std=[WREC]), SH5)
ok &= case('E11b the Recovering line in the emulator stdout only -> counted, a window event',
           e['winev'] and e['win']['recovering'] == 1 and e['win']['minimized'] == 0 and not adm_ok(e))
e = S.entry_of('w145_02', mk145(BASE / 'E12', 'w145_02', std=[WMIN]), SH5)
ok &= case('E12 the "minimized" line in the emulator stdout only -> counted, a window event', e['winev'] and
           e['win']['minimized'] == 1 and not adm_ok(e))
OTH = ['Window 1 restored', 'Window 1 resized to 1280x720', 'Window 1 size changed to 1280x720', 'Window 1 lost keyboard focus',
       'Window 1 gained keyboard focus', 'Window 1 moved to 10,10', 'Window 1 exposed', 'Window 12 lost keyboard focus']
e = S.entry_of('w145_02', mk145(BASE / 'E13', 'w145_02', extra=OTH), SH5)
ok &= case('E13 only other window lines (restored, resized, size changed, lost focus twice; gained, moved, exposed not counted) '
           '-> counted, no event, admitted, the print says "no event"',
           not e['winev'] and adm_ok(e) and e['win'] == dict(minimized=0, restored=1, resized=1, **{
               'size changed': 1, 'lost keyboard focus': 2, 'recovering': 0}) and
           any(x.endswith('Recovering Vulkan swapchain 0 -> no event') for x in S.fmt_entry(e)))
e = S.entry_of('w145_02', mk145(BASE / 'E13b', 'w145_02', extra=['Window minimized', 'the window 1 minimized later',
                                                                  'Window 1 minimizedX']), SH5)
ok &= case('E13b "Window minimized" without an id and "minimizedX" are not the line of window.cpp; "the window 1 minimized" '
           '(lower case) is not either -> no event', not e['winev'] and e['win']['minimized'] == 0)
RE14 = BASE / 'E14'
mk145(RE14, 'w145_00')
mk145(RE14, 'w145_01')
mk145(RE14, 'v145_02', extra=[WMIN])
mk145(RE14, 'w145_02')
e14 = S.entry_of('v145_02', str(RE14), SH5)
o14 = S.summary(str(RE14), SH5, 'viewed')[0]
ok &= case('E14 a V with a window event -> V not admitted, its level NO by "V admitted", not admitted in the census; the '
           'WINDOW EVENTS line names it',
           not adm_ok(e14) and 'SCENE_OK small_pot_lava: NO' in o14 and
           row_ok(S.scene_ok(e14, S.entry_of('w145_02', str(RE14), SH5), 'viewed', S.PAIRS[1])[1], 'V admitted') is False
           and any(x.startswith('  v145_02 small_pot_lava') and x.split(' admitted ')[1].startswith('NO') for x in o14) and
           '  info W w145_02 layer limit lines 0; window events V yes, W no' in o14 and
           any(x.startswith('WINDOW EVENTS (item 273 (k)(3)): tags with a "minimized" or "Recovering Vulkan swapchain" line '
                            '(not an outcome of the level; the gate stops the series): v145_02;') for x in o14))
CH5 = S.CHUNK
S.CHUNK = 37
pc = mk145(BASE / 'E15', 'w145_02', extra=[WMIN, LIM, F6L, WREC, 'Window 1 restored', LIM])
sc15 = S.scan(pc + '/log_w145_02.txt')
S.CHUNK = CH5
ok &= case('E15 the window, Recovering, limit and F6 lines are counted once each across 37-byte chunks',
           sc15['win']['minimized'] == 1 and sc15['win']['restored'] == 1 and sc15['rec'] == 1 and sc15['limit'] == 2 and
           sc15['f6'] == 1)


def sc5(root, tag):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = S.main(['--stop-check', tag], root=str(root), pred=str(PR5))
    return rc, b.getvalue()


R16 = BASE / 'E16'
mk145(R16, 'w145_00', extra=[LIM])
r16 = sc5(R16, 'w145_01')
c16 = S.control_state(S.entry_of('w145_00', str(R16), SH5))
R16b = BASE / 'E16b'
mk145(R16b, 'w145_00')
r16b = sc5(R16b, 'w145_01')
o16 = S.summary(str(R16), SH5, None)[0]
f16 = S.fmt_entry(S.entry_of('w145_00', str(R16), SH5))
f16b = S.fmt_entry(S.entry_of('w145_00', str(R16b), SH5))
ok &= case('E16 the control W with one layer limit line -> a letter term of the control stop (item 273 (k)(2)), rc 5 before '
           'w145_01; the control with 0 limit lines -> rc 0; the print and the LAYER LIMIT line name the control rule',
           r16[0] == 5 and c16[1] is True and 'layer limit lines 1 (item 273 (k)(2): 0 required in the control W)' in c16[2]
           and 'STOP RULE CONTROL before w145_01: STOP; letter stop (layer limit lines 1' in r16[1] and r16b[0] == 0 and
           'STOP RULE CONTROL before w145_01: not met' in r16b[1] and
           '  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): 1 - control W: 0 required -> '
           'FAIL' in f16 and
           '  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): 0 - control W: 0 required -> '
           'PASS' in f16b and
           'LAYER LIMIT (item 273 (k)(2)): control W w145_00: 1 lines -> FAIL (a letter term of the control stop); other W '
           'with layer limit lines (layer truncated, the outcome by the letter): none' in o16)
R17 = BASE / 'E17'
mk145(R17, 'w145_00', std=[LIM])
e17 = S.entry_of('w145_00', str(R17), SH5)
ok &= case('E17 the limit line in the emulator stdout of the control W -> counted (1), letter stop',
           e17['limit'] == 1 and S.control_state(e17)[1] is True and sc5(R17, 'w145_01')[0] == 5)
R18 = BASE / 'E18'
xr, xp = x144root('E18x')
mk145(R18, 'w145_00')
mk145(R18, 'w145_01', extra=[LIM, LIM])
o18 = S.summary(str(R18), SH5, None)[0]
e18 = S.entry_of('w145_01', str(R18), SH5)
ok &= case('E18 a non-control W with two limit lines -> not admitted by the row (b)(1) only (item 295 (b)(1)), printed LAYER '
           'TRUNCATED: the pair (V v144_09 + W w145_01) NO; the LAYER LIMIT line names it; the control PASS',
           not adm_ok(e18) and [a[0][:11] for a in e18['admit'] if not a[1]] == ['W 295(b)(1)'] and e18['limit'] == 2 and
           any(x.endswith('2 - LAYER TRUNCATED (the outcome stands by the letter)') for x in S.fmt_entry(e18)) and
           '  layer limit lines ("this will be the last time reporting it", item 273 (k)(2)): 0' in S.fmt_entry(
               eE['w145_02']) and
           'SCENE_OK rocket_hourglass: NO' in o18 and
           'LAYER LIMIT (item 273 (k)(2)): control W w145_00: 0 lines -> PASS; other W with layer limit lines (layer truncated, '
           'the outcome by the letter): w145_01' in o18 and
           any(x == '  info W w145_01 layer limit lines 2 (layer truncated); window events V no, W no' for x in o18))
e = S.entry_of('w145_02', mk145(BASE / 'E19', 'w145_02', extra=[F6L, F6L, '[Vulkan][W][1]: Removing layer X',
                                                                '[Vulkan][W][3]: y', '[Vulkan][I][4]: z']), SH5)
ok &= case('E19 the F6 text lines (2), the validation-type lines (bit 2 of the type: [2] x5 incl. the 3 of wl and F6 x2, [3]; '
           'not [1], [4]) and the validation-layer lines of item 295 (b)(2) (third field 2 exactly: 5) are printed; the W form '
           'print of item 295 (b)',
           e['f6'] == 2 and e['vkval'] == 6 and e['vk2'] == 5 and adm_ok(e) and any(
               x == '  W form of item 295 (b): held; the form line "W form: limit=100000000 filter=none" (PASS); '
               'validation-layer lines [W][2] / [E][2] 5 (log and stdout); the last one of the log 0.000 s before the last '
               'FrameTrace row of the hold; F6 text lines ("... and this write is unused.") 2; [Vulkan][ lines of the '
               'validation type (bit 2) 6 (info)' for x in S.fmt_entry(e)))


def rows_at(ends, n0=1):
    """FrameTrace rows (n, dt_us, draws, pos) whose ends lie at the given times when anchored at the last one."""
    out = []
    for i, x in enumerate(ends):
        dt = 16667 if i == 0 else int(round((x - ends[i - 1]) * 1e6))
        out.append((n0 + i, dt, 3000, i))
    return out


rr = rows_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
it = [0.0, 0.1, 0.2, 0.5, 0.6]
ok &= case('E20 vcont: rows ending at 0.3 and 0.4 inside the record gap 0.2..0.5 -> after the first scene frame n 3: 2 rows in '
           '1 gap, the longest (2, 4, 5, 0.3 s, record 2); first frame n 4: 1 after, 1 before; n 5: none after, 2 before',
           S.vcont(rr, it, 3) == dict(after=2, gaps=1, before=0, longest=(2, 4, 5, 0.3, 2)) and
           S.vcont(rr, it, 4) == dict(after=1, gaps=1, before=1, longest=(2, 4, 5, 0.3, 2)) and
           S.vcont(rr, it, 5) == dict(after=0, gaps=0, before=2, longest=None))
rr = rows_at([0.0, 0.211, 0.213, 0.487, 0.489, 0.6])
it = [0.0, 0.2, 0.5, 0.6]
ok &= case('E20b the margin of 12 ms: row ends 11 ms after the gap start and 11 ms before its end are taken as the edge records; '
           '13 ms inside are counted', S.vcont(rr, it, 1) == dict(after=2, gaps=1, before=0, longest=(2, 3, 4, 0.3, 1)))
rr = rows_at([0.0, 0.03, 0.06])
rr2 = rows_at([0.0, 0.03, 0.061])
ok &= case('E20c the gap of the records must exceed 60 ms: a 60 ms gap is not examined, a 61 ms one is',
           S.vcont(rr, [0.0, 0.0, 0.06], 1) == dict(after=0, gaps=0, before=0, longest=None) and
           S.vcont(rr2, [0.0, 0.0, 0.061], 1) == dict(after=1, gaps=1, before=0, longest=(1, 2, 2, 0.061, 1)))
rr = rows_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
it = [0.0, 0.1, 0.25, 0.4, 0.5, 0.95, 1.0]
ok &= case('E20d three gaps hold rows (0.1..0.25: n 3; 0.25..0.4: n 4; 0.5..0.95: n 7..10), a 50 ms gap is not examined: '
           'the longest run is the gap with the most rows, the counts add up',
           S.vcont(rr, it, 1) == dict(after=6, gaps=3, before=0, longest=(4, 7, 10, 0.45, 4)))
ok &= case('E20e vcont None without rows, without records or without a first scene frame',
           S.vcont([], [0.0, 1.0], 1) is None and S.vcont(rows_at([0.0, 1.0]), [], 1) is None and
           S.vcont(rows_at([0.0, 1.0]), None, 1) is None and S.vcont(rows_at([0.0, 1.0]), [0.0, 1.0], None) is None)
ip = BASE / 'E21.idx'
ip.write_text('0 1 0.000\n1 2\n2 3 x\n3 4 0.250 extra\n\n4 5 0.5\n')
ok &= case('E21 idx_times: lines of >= 3 fields with a number in the third; others skipped; a missing file -> None',
           S.idx_times(str(ip)) == [0.0, 0.25, 0.5] and S.idx_times(str(BASE / 'none.idx')) is None)
vl = [PRE] + scene_lines('small_pot_lava', [16667] * 3100)
nrow = sum(1 for x in vl if x.startswith('FrameTrace'))
t_end = 0.0
idx = []
ftr = [x for x in vl if x.startswith('FrameTrace')]
dts = [int(x.split('dt_us=')[1].split()[0]) for x in ftr]
ends = []
c = 0.0
for d in reversed(dts):
    ends.append(100.0 - c)
    c += d / 1e6
ends.reverse()
fn = [int(x.split('n=')[1].split()[0]) for x in ftr if int(x.split('draws=')[1].split()[0]) >= 100 and
      int(x.split('n=')[1].split()[0]) >= 14][0]
gap_rows = [i for i in range(len(ftr)) if int(ftr[i].split('n=')[1].split()[0]) in (fn + 1, fn + 2, fn + 3)]
idx = [x for i, x in enumerate(ends) if i not in gap_rows]
R22 = BASE / 'E22'
mk145(R22, 'v145_02', lines=vl, idx=idx, glitch=(3200, 0))
e22 = S.entry_of('v145_02', str(R22), SH5)
ok &= case('E22 a V whose .idx lacks the records of the three frames after the first scene frame -> continuity 3 rows in 1 gap, '
           'longest 3 rows n fn+1..fn+3; printed as data; the V stays admitted (not a gate)',
           e22['vcont'] == dict(after=3, gaps=1, before=0, longest=(3, fn + 1, fn + 3, e22['vcont']['longest'][3],
                                                                     gap_rows[0] - 1)) and adm_ok(e22) and
           any(x.startswith('  video continuity (B38, item 273 (k)(3), the method of AUDIT144 s1.3; data next to SCENE_OK, '
                            'not a gate): FrameTrace rows after the first scene frame ending inside a .idx gap > 60 ms: 3 in 1 '
                            'gaps; longest run 3 rows n %d..%d' % (fn + 1, fn + 3)) for x in S.fmt_entry(e22)))
o22 = S.summary(str(R22), SH5, None)[0]
ok &= case('E22b the summary names the V with a run of >= 2 rows without a record (3 rows) next to SCENE_OK',
           'VIDEO CONTINUITY (B38, item 273 (k)(3); data, not a gate): V with a run of >= 2 rows without a video record after '
           'the first scene frame: v145_02 3 rows' in o22 and any(
               x.startswith('  info video continuity of V v145_02 (B38, item 273 (k)(3); data, not a gate - "0 glitches" '
                            'covers the frames in the video): FrameTrace rows after the first scene frame ending inside a .idx '
                            'gap > 60 ms: 3 in 1 gaps') for x in o22))
# the cross-session pair: v144_09 of s144 with w145_01
R23 = BASE / 'E23'
xr, xp = x144root('E23')
mk145(R23, 'w145_01')
v23 = S.entry_of('v144_09', str(R23), SH5)
w23 = S.entry_of('w145_01', str(R23), SH5)
word, rows = S.scene_ok(v23, w23, 'not-viewed', S.PAIRS[0])
o23 = S.summary(str(R23), SH5, None)[0]
ok &= case('E23 the W repeat w145_01 with the V v144_09 of s144 (its root, chain go144a, its seal) -> the pair row names its own '
           'session; the sheet row of v144_09 is viewed by item 273 (a) whatever --sheet says',
           v23 is not None and adm_ok(v23) and v23['times_log_sha'] == v23['log_sha'] and
           row_ok(rows, 'V v144_09 and W w145_01 are the pair of one level') is True and
           'SCENE_OK rocket_hourglass: YES' in o23 and any(
               x.endswith('(viewed (item 273 (a): viewed at the close of s144))') for x in o23) and
           any(x.startswith('V OF ANOTHER SESSION v144_09 (the pair of item 254 (e); root %s, chain go144a, seal %s)' % (
               xr.as_posix(), xp.as_posix())) for x in o23))
Path(xr, 'log_v144_09.txt').write_bytes(Path(xr, 'log_v144_09.txt').read_bytes() + b'x\n')
v23b = S.entry_of('v144_09', str(R23), SH5)
ok &= case('E23b a replaced V log of s144 (sha != its enter_scene end line of the s144 times.txt) -> the pair row FAIL, NO',
           S.scene_ok(v23b, w23, 'viewed', S.PAIRS[0])[0] == 'NO' and
           row_ok(S.scene_ok(v23b, w23, 'viewed', S.PAIRS[0])[1], 'V v144_09 and W w145_01') is False)
xr, xp = x144root('E23c')
tp = xr / 'step2' / 'times.txt'
tp.write_text(tp.read_text(encoding='utf-8').replace(' go144a v144_09 enter_scene end ', ' go145a v144_09 enter_scene end '),
              encoding='utf-8')
v23c = S.entry_of('v144_09', str(R23), SH5)
ok &= case('E23c the enter_scene end line of v144_09 written under the chain go145a (not its own go144a) -> no times sha, FAIL',
           v23c['times_log_sha'] is None and row_ok(S.scene_ok(v23c, w23, 'viewed', S.PAIRS[0])[1], 'V v144_09 and W w145_01')
           is False)
xr, xp = x144root('E23d', js_over=dict(guest_args='-lvl pot_treasure_cave'))
v23d = S.entry_of('v144_09', str(R23), SH5)
ok &= case('E23d the V of s144 run for another level (guest args) -> V not admitted, the pair row FAIL',
           not adm_ok(v23d) and row_ok(S.scene_ok(v23d, w23, 'viewed', S.PAIRS[0])[1], 'V v144_09 and W w145_01') is False)
xr, xp = x144root('E23e', js_over=dict(prereg=dict(path=S.PRED_PATH, sha256=SH5)))
v23e = S.entry_of('v144_09', str(R23), SH5)
ok &= case('E23e the V of s144 must carry the seal of s144: a json with the seal of 145 -> V not admitted, NO',
           not adm_ok(v23e) and S.scene_ok(v23e, w23, 'viewed', S.PAIRS[0])[0] == 'NO')
R23f = BASE / 'E23f'
mk145(R23f, 'v144_09')
mk145(R23f, 'w145_01')
S.XSRC = {'v144_09': dict(root=(BASE / 'E23f' / 'none').as_posix(), chain='go144a', pred='none.md')}
ok &= case('E23f a v144_09 lying in the s145 root is not read (the V of another session comes from its own root only)',
           S.entry_of('v144_09', str(R23f), SH5) is None and
           row_ok(S.scene_ok(None, S.entry_of('w145_01', str(R23f), SH5), 'viewed', S.PAIRS[0])[1], 'V made') is False)
xr, xp = x144root('E23g')
ok &= case('E23g the V v144_09 offered as the pair of level 02 (w145_02) -> NO by the pair row',
           S.scene_ok(S.entry_of('v144_09', str(R23), SH5), S.entry_of('w145_01', str(R23), SH5), 'viewed',
                      S.PAIRS[1])[0] == 'NO')
# the summary of profile 145
R24 = BASE / 'E24'
xr, xp = x144root('E24x')
for t in ('w145_00', 'w145_01', 'v145_02', 'w145_02', 'v145_03'):
    lines = None
    if t == 'v145_03':
        lines = [PRE] + scene_lines('spin_drill_natural_cave', [16667] * 700 + [150000] + list(v_post())) + [
            'Window 1 restored']
    mk145(R24, t, lines=lines)
o24 = S.summary(str(R24), SH5, None)[0]
o24v = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24 the summary of 145: the cold census header (no repeated entry), the map rows marked "cold first entry", halves '
           'of eight, YES of the cross-session pair, PENDING_SHEET / YES of a new pair, the levels line over 17',
           'CENSUS = the V tags v145_02..v145_17, COLD first entries of never-entered levels (item 273 (k)(1)-(2)): the map '
           'rows and the forms B5 / B5a / B33 below go into the cold pools' in o24 and
           not any('REPEATED entries' in x or 'repeated entry' in x for x in o24) and
           any(x.startswith('    map (A) row small_pot_lava (cold first entry): outcome on 120 s HOLDS_120') for x in o24) and
           'FORMS second reading by the order (shared caches warm from earlier runs): first 8 B5a 0/8 B5 0/8; last 8 B5a 0/8 '
           'B5 0/8' in o24 and 'SCENE_OK rocket_hourglass: YES' in o24 and 'SCENE_OK small_pot_lava: PENDING_SHEET' in o24 and
           'SCENE_OK small_pot_lava: YES' in o24v and 'SCENE_OK LEVELS: YES 1, PENDING_SHEET 1, NO 15 of 17' in o24 and
           'CENSUS made 2 of 16 (of them attempt made without json 0), admitted 2' in o24 and
           'FORM B33 (a frame 100 ms <= dt < 1 s on the hold after the window): 1/16 [c] (admitted and entered 2) v145_03; '
           'executor variant (the hold within 120 s of presented time after the entry line): 1/16' in o24)
ok &= case('E24b the new summary lines: window events none, layer limit (control PASS, none truncated), the W FORM 295 line 3 '
           'of 3 and V 3 of 3, the window lines by kind, near none, the alignment none, the video continuity line; the W FORM '
           'line of 254 (e) still printed',
           'WINDOW EVENTS (item 273 (k)(3)): tags with a "minimized" or "Recovering Vulkan swapchain" line (not an outcome of '
           'the level; the gate stops the series): none; tags with only other window lines (restored, resized, size changed, '
           'lost keyboard focus): v145_03' in o24 and
           'LAYER LIMIT (item 273 (k)(2)): control W w145_00: 0 lines -> PASS; other W with layer limit lines (layer truncated, '
           'the outcome by the letter): none' in o24 and
           'W FORM 295 (item 295 (b)(1)-(4): 0 layer limit lines, validation active by [W][2] / [E][2] lines, the last one '
           'within 10 s of the hold end, the form line W form: limit=100000000 filter=none): every row passed by 3 of 3 made W; '
           'failing: none; not held (rows (1)-(3) n/a): none; V without VK_LAYER_MESSAGE_ID_FILTER 3 of 3 made, violated: none; '
           'F6 text lines in the W (info): w145_00 0, w145_01 0, w145_02 0' in o24 and
           'WINDOW LINES BY KIND (item 295 (g); log and stdout; data): v145_03: restored 1' in o24 and
           'WINDOW LINE NEAR A K2 / K3 FRAME (item 295 (g); within 2 s; data): none' in o24 and
           'VIDEO CONTINUITY ALIGNMENT (item 295 (d); data, not a gate): V whose count at the best anchor shift differs by more '
           'than 10 % [I]: none' in o24 and
           'VIDEO CONTINUITY (B38, item 273 (k)(3); data, not a gate): V with a run of >= 2 rows without a video record after '
           'the first scene frame: none' in o24 and any(x.startswith('W FORM (item 254 (e)):') for x in o24) and
           any(x.startswith('  info video continuity of V v145_02 (B38, item 273 (k)(3); data, not a gate - "0 glitches" '
                            'covers the frames in the video): n/a') for x in o24) and
           'CONTROL W w145_00 (underwater_aerial_garden, item 254 (k)(4)): PASS; letter (death marker or [Vulkan][E]) pass '
           '(none); executor reading [I] (any W row or admission row failing; the gate) pass (none)' in o24)
mk145(R24, 'w145_02', js=js145('w145_02', filt=FILT))
o24f = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24c a W with the filter of step 0 in the summary: the W FORM 295 line names it by (b)(4), its level NO by "W '
           'admitted"', any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'every row passed by 2 of 3 made W; failing: '
                            'w145_02 (b)(4);' in x for x in o24f) and 'SCENE_OK small_pot_lava: NO' in o24f)
jv3 = js145('v145_03')
jv3['env']['VK_LAYER_MESSAGE_ID_FILTER'] = FILT
mk145(R24, 'v145_03', js=jv3)
o24g = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24d a V with the filter in the summary: the W FORM 295 line counts it among the V and names it',
           any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'V without VK_LAYER_MESSAGE_ID_FILTER 2 of 3 made, '
               'violated: v145_03;' in x for x in o24g))
mk145(R24, 'w145_02', extra=[LIM])
o24h = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24e a W with a limit line in the summary: the W FORM 295 line names it by (b)(1), the LAYER LIMIT line names it, '
           'its level NO', any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'failing: w145_02 (b)(1);' in x
                               for x in o24h) and 'SCENE_OK small_pot_lava: NO' in o24h and any(
               x.startswith('LAYER LIMIT (item 273 (k)(2)):') and x.endswith('the outcome by the letter): w145_02') for x in o24h))
mk145(R24, 'w145_02', js=js145('w145_02', attempt=dict(outcome='timeout')))
o24i = S.summary(str(R24), SH5, 'viewed')[0]
ok &= case('E24f a W not held (timeout) in the summary: the W FORM 295 line names it among the not held',
           any(x.startswith('W FORM 295 (item 295 (b)(1)-(4):') and 'not held (rows (1)-(3) n/a): w145_02;' in x for x in o24i))
# the stop rule of the window event
R25 = BASE / 'E25'
mk145(R25, 'w145_00')
mk145(R25, 'w145_01', extra=[WMIN, WREC])
r25 = sc5(R25, 'v145_02')
r25b = sc5(R25, 'w145_01')
ok &= case('E25 the made tag right before has a window event -> rc 5 naming it; before w145_01 (the control clean) -> not met',
           r25[0] == 5 and 'STOP RULE WINDOW EVENT before v145_02 (item 273 (k)(3)-(4): the made tag right before with a '
           '"minimized" or "Recovering Vulkan swapchain" line; question to the lead about a repeat): STOP w145_01 (minimized 1,'
           in r25[1] and r25b[0] == 0 and 'STOP RULE WINDOW EVENT before w145_01' in r25b[1] and
           'not met (w145_00: minimized 0,' in r25b[1])
R25c = BASE / 'E25c'
mk145(R25c, 'w145_00', extra=[WREC])
r25c = sc5(R25c, 'w145_01')
R25d = BASE / 'E25d'
mk145(R25d, 'w145_00', extra=['Window 1 lost keyboard focus', 'Window 1 restored'])
r25d = sc5(R25d, 'w145_01')
ok &= case('E25b the control W with only "Recovering Vulkan swapchain" -> rc 5 (window event and the gate reading of the '
           'control); the control with lost focus and restored only -> rc 0',
           r25c[0] == 5 and 'STOP w145_00 (' in r25c[1] and r25d[0] == 0 and 'not met (w145_00: ' in r25d[1])
R25e = BASE / 'E25e'
mk145(R25e, 'w145_00')
(R25e / 'attempt_w145_01.txt').write_text('made\n')
r25e = sc5(R25e, 'v145_02')
r25f = sc5(BASE / 'E25none', 'w145_00')
ok &= case('E25c the tag right before made without json -> the window rule "not met (no json of w145_01)"; the first tag -> '
           '"not met (no tag made)"', 'STOP RULE WINDOW EVENT before v145_02' in r25e[1] and
           'not met (no json of w145_01)' in r25e[1] and r25f[0] == 0 and 'not met (no tag made)' in r25f[1])
R25g = BASE / 'E25g'
mk145(R25g, 'w145_00', extra=[WMIN])
mk145(R25g, 'w145_01')
r25g = sc5(R25g, 'v145_02')
ok &= case('E25d the window rule reads the made tag right before only: an event two tags back is not its stop (the control rule '
           'still stops on the control: its admission row fails)', 'not met (w145_01: minimized 0,' in r25g[1] and
           r25g[0] == 5 and 'STOP RULE CONTROL before v145_02: STOP' in r25g[1])
ok &= case('E26 stop-check of an unknown tag (v144_09, a 144 tag, v145_01) -> rc 2',
           sc5(R25, 'v144_09')[0] == 2 and sc5(R25, 'w144_09')[0] == 2 and sc5(R25, 'v145_01')[0] == 2)
VA = BASE / 'E27.txt'
VA.write_text('VCONT s144 v144_09: rows 5, records 6 (records - rows +1), rows with a record within 8 ms 5 (100.0 %); first '
              'scene frame n 349; presented frames WITHOUT a video record: before / at the first scene frame 0, after it 0 in 0 '
              'gaps; longest run after it: none; top runs []\n'
              'VCONT s143 v143_10: rows 14030, records 14022 (records - rows -8), rows with a record within 8 ms 7539 (53.7 %); '
              'first scene frame n 388; presented frames WITHOUT a video record: before / at the first scene frame 1, after it 35 '
              'in 2 gaps; longest run after it: 34 rows n 390..423 over 0.567 s of dt (idx gap 2.182 s after record 389); top '
              'runs [(34, 390, 423, 2.182)]\nALL DONE\n', encoding='ascii')
ok &= case('E27 vcont_audit reads the VCONT lines of vidcont144.out.txt (none and a run); a missing file -> {}',
           S.vcont_audit(str(VA)) == {('s144', 'v144_09'): ('349', 0, 0, 0, None),
                                      ('s143', 'v143_10'): ('388', 1, 35, 2, (34, 390, 423, 389))} and
           S.vcont_audit(str(BASE / 'none.txt')) == {})
# the regression of item 273 (k)(5) on a synthetic profile 144
RG4 = BASE / 'rg144'
RG4.mkdir()
P144_REAL = dict(S.P144)
WINEV_REAL, LIMIT_REAL = S.REGRESS144_WINEV, S.REGRESS144_LIMIT
(RG4 / 'pred.md').write_text('fixture 144 regress\n', encoding='utf-8')
SH44 = hashlib.sha256((RG4 / 'pred.md').read_bytes()).hexdigest()
S.P144 = dict(S.P144, ROOT=RG4.as_posix(), PRED_PATH=(RG4 / 'pred.md').as_posix(), SEQ=('w144_00', 'v144_09', 'w144_09'),
              PAIRS=(('v144_09', 'w144_09', 'rocket_hourglass'),), CENSUS=(('v144_09', 'rocket_hourglass'),),
              V_TAGS=('v144_09',), W_TAGS=('w144_00', 'w144_09'), LEVELS=('rocket_hourglass',), XSRC={}, XSHEET=(), HALF=1)
old = S.profile(S.P144)
mk144(RG4, 'w144_00', js=dict(js144('w144_00'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
vl4 = [PRE] + scene_lines('rocket_hourglass', v_post())
f4 = [x for x in vl4 if x.startswith('FrameTrace')]
d4 = [int(x.split('dt_us=')[1].split()[0]) for x in f4]
e4 = []
c = 0.0
for d in reversed(d4):
    e4.append(400.0 - c)
    c += d / 1e6
e4.reverse()
mk144(RG4, 'v144_09', lines=vl4, js=dict(js144('v144_09'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
(RG4 / 'rec_v144_09.mp4.idx').write_text(''.join('%d %d %.4f\n' % (i, i + 1, x) for i, x in enumerate(e4)
                                                 if i not in (20, 21)))
mk144(RG4, 'w144_09', lines=wl('rocket_hourglass')[:30] + [WMIN, WREC, LIM] + wl('rocket_hourglass')[30:],
      js=dict(js144('w144_09'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
out4 = S.summary(str(RG4), SH44, 'viewed')[0]
ev4 = S.entry_of('v144_09', str(RG4), SH44)
S.profile(old)
EX4 = RG4 / 'expected.txt'
EX4.write_bytes(('\r\n'.join(out4) + '\r\n').encode('ascii'))
vc4 = ev4['vcont']
VX4 = RG4 / 'vcont.txt'


def vline(vc, first, n_after=None):
    lg = vc['longest']
    return ('VCONT s144 v144_09: rows 1, records 1 (records - rows +0), rows with a record within 8 ms 1 (1.0 %%); first scene '
            'frame n %s; presented frames WITHOUT a video record: before / at the first scene frame %d, after it %d in %d '
            'gaps; longest run after it: %s; top runs []\n' % (first, vc['before'], vc['after'] if n_after is None else n_after,
                                                               vc['gaps'], 'none' if lg is None else
                                                               '%d rows n %d..%d over 0.033 s of dt (idx gap %.3f s after '
                                                               'record %d)' % (lg[0], lg[1], lg[2], lg[3], lg[4])))


VX4.write_text(vline(vc4, ev4['derive']['first'][0]), encoding='ascii')
S.REGRESS144_WINEV, S.REGRESS144_LIMIT = ('w144_09',), ('w144_09',)
NOTHELD_REAL, B3_REAL = S.REGRESS144_NOTHELD, S.REGRESS144_B3
S.REGRESS144_NOTHELD, S.REGRESS144_B3 = (), ()
XB = dict(S.XSRC)
ok4, l4 = S.regress144(str(EX4), str(VX4))
ok &= case('E28 regress144 on a synthetic profile 144: byte-identical; the new rows apart (window event w144_09, layer limit '
           'w144_09, control 0, the continuity of the V equal to the audit line) -> PASS; the profile 145 is restored; the '
           'profile 144 summary has no line of 145',
           ok4 and l4[-1] == 'REGRESS144: PASS' and 'byte-identical yes; differing lines 0' in l4[0] and
           vc4 is not None and vc4['after'] == 2 and
           'NEW ROWS of profile 145 on the same logs (not in the regression file; item 273 (k)(2)-(3)):' in l4 and
           'NEW295 ROWS held: W not held (rows (1)-(3) n/a) none (expected : stopped by validation) -> PASS' in l4 and
           any(x.startswith('NEW295 ROWS (b)(1) layer limit lines 0:') and x.endswith('failing 1 w144_09 -> PASS') for x in l4)
           and any(x.startswith('NEW295 ROWS (b)(4) the form line:') and x.endswith('failing 2 w144_00,w144_09 -> PASS')
                   for x in l4) and
           any(x.startswith('NEW295 w144_09 W: held; (b)(1) 1 -> FAIL; (b)(2) ') for x in l4) and
           any(x.startswith('NEW295 v144_09 V: window lines ') for x in l4) and
           S.ROOT == 'C:/kyty/s145' and S.CHAIN == 'go145a' and S.FORM145 is True and S.SEQ[0] == 'w145_00' and
           S.XSRC == XB and S.P144['ROOT'] == RG4.as_posix())
S.XSRC = dict(XSRC145)
ok &= case('E28b the profile 144 summary prints no line of 145 (no window, layer limit, filter, continuity, cold census)',
           not any(s in x for x in out4 for s in ('WINDOW EVENT', 'LAYER LIMIT', 'W FILTER', 'VIDEO CONTINUITY', 'window events',
                                                 'layer limit', 'cold first entry', 'COLD first', 'video continuity',
                                                 'message filter', 'item 273', 'W FORM 295', 'WINDOW LINE', 'window line',
                                                 'item 295', 'W 295')) and
           any('REPEATED entries' in x for x in out4))
EX4.write_bytes(('\r\n'.join(out4[:3] + ['changed'] + out4[4:]) + '\r\n').encode('ascii'))
ok4b, l4b = S.regress144(str(EX4), str(VX4))
EX4.write_bytes(('\n'.join(out4) + '\n').encode('ascii'))
ok4c, l4c = S.regress144(str(EX4), str(VX4))
EX4.write_bytes(('\r\n'.join(out4) + '\r\n').encode('ascii'))
VX4.write_text(vline(vc4, ev4['derive']['first'][0], n_after=vc4['after'] + 1), encoding='ascii')
ok4d, l4d = S.regress144(str(EX4), str(VX4))
VX4.write_text(vline(vc4, ev4['derive']['first'][0]), encoding='ascii')
S.REGRESS144_WINEV = ()
ok4e, l4e = S.regress144(str(EX4), str(VX4))
S.REGRESS144_WINEV, S.REGRESS144_LIMIT = ('w144_09',), ()
ok4f, l4f = S.regress144(str(EX4), str(VX4))
S.REGRESS144_LIMIT = ('w144_09',)
ok4g = S.regress144(str(BASE / 'none144.txt'), str(VX4))[0]
ok4h, l4h = S.regress144(str(EX4), str(BASE / 'none_vc.txt'))
ok &= case('E29 regress144 fails on a changed line (DIFF line 4), on LF only, on a continuity different from the audit line, on '
           'another window-event set, on another layer-limit set, on a missing file, without the audit file',
           not ok4b and 'DIFF line 4 expected: changed' in l4b and not ok4c and 'byte-identical NO; differing lines 0' in l4c[0]
           and not ok4d and 'DIFFERENT' in '\n'.join(l4d) and 'NEW ROWS continuity: 0 of 1 V equal' in '\n'.join(l4d) and
           not ok4e and 'NEW ROWS window event: tags w144_09 (expected , AUDIT144 s2 (2)) -> FAIL' in l4e and
           not ok4f and any(x.startswith('NEW ROWS layer limit:') and x.endswith('-> FAIL') for x in l4f) and not ok4g and
           not ok4h)
S.REGRESS144_B3 = ('w144_09',)
ok4j, l4j = S.regress144(str(EX4), str(VX4))
S.REGRESS144_B3, S.REGRESS144_NOTHELD = (), ('w144_09',)
ok4k, l4k = S.regress144(str(EX4), str(VX4))
S.REGRESS144_NOTHELD = ()
ok &= case('E29c the NEW295 rows decide alone (the old rows pass): another expected set of (b)(3) -> FAIL; another not-held '
           'set -> FAIL', not ok4j and any(x.startswith('NEW295 ROWS (b)(3)') and x.endswith('-> FAIL') for x in l4j) and
           all(not x.endswith('-> FAIL') for x in l4j if not x.startswith('NEW295 ROWS (b)(3)')) and not ok4k and
           any(x.startswith('NEW295 ROWS held:') and x.endswith('-> FAIL') for x in l4k) and
           all(not x.endswith('-> FAIL') for x in l4k if not x.startswith('NEW295 ROWS held:')))
old = S.profile(S.P144)
mk144(RG4, 'w144_09', lines=wl('rocket_hourglass')[:30] + [WMIN, WREC, LIM] + wl('rocket_hourglass')[30:],
      js=dict(js144('w144_09', attempt=dict(hold_exit=5.0)), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
S.profile(old)
S.REGRESS144_NOTHELD = ('w144_09',)
ok4m, l4m = S.regress144(str(EX4), str(VX4))
S.REGRESS144_NOTHELD = ()
ok &= case('E29d a W of the profile 144 not held (hold_exit) -> the held row names it and passes when expected; its rows '
           '(1)-(3) are n/a', 'NEW295 ROWS held: W not held (rows (1)-(3) n/a) w144_09 (expected w144_09: stopped by '
           'validation) -> PASS' in l4m and any(x.startswith('NEW295 w144_09 W: NOT held (hold_exit / ENDED / exited); (b)(1) '
                                                             'n/a (W not held: hold_exit / ENDED / exited) -> PASS') for x in l4m))
old = S.profile(S.P144)
mk144(RG4, 'w144_09', lines=wl('rocket_hourglass')[:30] + [WMIN, WREC, LIM] + wl('rocket_hourglass')[30:],
      js=dict(js144('w144_09'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
mk144(RG4, 'w144_00', lines=wl(SKY) + [LIM], js=dict(js144('w144_00'), prereg=dict(path=S.PRED_PATH, sha256=SH44)))
out4i = S.summary(str(RG4), SH44, 'viewed')[0]
S.profile(old)
EX4I = RG4 / 'expected_i.txt'
EX4I.write_bytes(('\r\n'.join(out4i) + '\r\n').encode('ascii'))
S.REGRESS144_LIMIT = ('w144_00', 'w144_09')
ok4i, l4i = S.regress144(str(EX4I), str(VX4))
ok &= case('E29b the control w144_00 with a limit line fails the layer-limit row even when the expected set names it; every '
           'other row passes (the summary of the profile byte for byte with the control rewritten), so its control term decides',
           not ok4i and any(x.startswith('NEW ROWS layer limit:') and 'control w144_00 1 lines -> FAIL' in x for x in l4i) and
           'byte-identical yes' in l4i[0] and all(not x.endswith('-> FAIL') for x in l4i if not x.startswith('NEW ROWS layer limit:')))
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    rr4 = S.main(['--regress144'])
ok &= case('E30 main --regress144 -> rc 1 against the real s144 summary from the fixture root', rr4 == 1 and
           'REGRESS144: FAIL' in _b.getvalue())
S.P144 = P144_REAL
S.REGRESS144_WINEV, S.REGRESS144_LIMIT = WINEV_REAL, LIMIT_REAL
S.REGRESS144_NOTHELD, S.REGRESS144_B3 = NOTHELD_REAL, B3_REAL
ok &= case('E31 the real regression constants of item 273 (k)(5): the s144 summary viewed, the audit continuity file, the '
           'window event of w144_09, the 13 W with limit lines', S.REGRESS144_FILE ==
           'C:/kyty/s144/step4/summary144_viewed.txt' and S.VCONT144_FILE ==
           'C:/kyty/KytyPS5/docs/session-144/audit/vidcont144.out.txt' and S.REGRESS144_WINEV == ('w144_09',) and
           S.REGRESS144_LIMIT == tuple('w144_%02d' % i for i in (2, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17)) and
           S.P144['ROOT'] == 'C:/kyty/s144' and S.P144['SEQ'] == tuple(SEQ144))
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    rt = S.main(['--tag', 'w145_02'], root=str(BASE / 'E10'), pred=str(PR5))
ok &= case('E32 main --tag of a W with a window event -> rc 1 (admission FAIL names the window row); the score json goes to '
           'runs145', rt == 1 and 'FAIL window event: no "Window <id> minimized"' in _b.getvalue() and
           (BASE / 'E10' / 'runs145' / 'w145_02.score.json').is_file())
# ---------------- link 1b (HPP-379, item 295): the W form rows (b)(1)-(4), the window kinds and the nearest window line, the
# alignment of the video continuity
RE34 = BASE / 'E34'
LV2 = 'small_pot_lava'


def w34(name, lines, std=(), js=None):
    return S.entry_of('w145_02', mk145(BASE / name, 'w145_02', lines=lines, std=std, js=js), SH5)


def row34(e, k):
    x = [a for a in e['admit'] if a[0].startswith('W 295(b)(%d)' % k)]
    return (x[0][1], x[0][2]) if len(x) == 1 else None


def ins_after(lines, n, text):
    i = [k for k, x in enumerate(lines) if x.startswith('FrameTrace: n=%d ' % n)][0]
    return lines[:i + 1] + [text] + lines[i + 1:]


l34 = [VF, VW] + scene_lines(LV2, [150000] * 100 + [100000] * 100)
e = w34('E34a', ins_after(l34, 114, VW))
ok &= case('E34 (b)(3): the LAST validation-layer line (an earlier one before the entry line aside) followed by rows of exactly '
           '10 000 000 us to the hold end -> PASS (the edge of 10 s); (b)(1), (b)(2) pass',
           row34(e, 3) == (True, '10000000 us') and row34(e, 1) == (True, '0') and row34(e, 2) == (True, '2') and adm_ok(e))
l34b = [VF] + scene_lines(LV2, [150000] * 100 + [100000] * 99 + [100001])
e = w34('E34b', ins_after(l34b, 114, VW))
ok &= case('E34b (b)(3): 1 us more (10 000 001 us) -> FAIL, the only failing row', row34(e, 3) == (False, '10000001 us') and
           [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(3)'])
e = w34('E34c', [VF, '[Vulkan][W][1]: Removing layer X because it is a duplicate', '[Vulkan][W][3]: y', '[Vulkan][I][2]: z',
                 '[Vulkan][W][12]: q'] + scene_lines(LV2, [150000] * 50))
ok &= case('E34c (b)(2): only loader [W][1], [W][3], [I][2] and [W][12] lines -> (b)(2) FAIL with 0, (b)(3) FAIL with none; '
           'the old row "validation active" still passes on the loader line', row34(e, 2) == (False, '0') and
           row34(e, 3) == (False, 'none') and [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(2)', 'W 295(b)(3)']
           and e['val']['ok'] is True)
e = w34('E34d', [VF] + scene_lines(LV2, [150000] * 50) + ['[Vulkan][E][2]: vkCmdDraw(): an error'])
ok &= case('E34d (b)(2)-(3): one [Vulkan][E][2] line after the last row -> both pass (1; 0 us)', row34(e, 2) == (True, '1')
           and row34(e, 3) == (True, '0 us'))
e = w34('E34e', [VF] + scene_lines(LV2, [150000] * 50), std=['[Vulkan][W][2]: in the stdout only'])
ok &= case('E34e a validation-layer line in the emulator stdout only: (b)(2) PASS (log and stdout), (b)(3) FAIL (the log has '
           'none)', row34(e, 2) == (True, '1') and row34(e, 3) == (False, 'none'))
e = w34('E34f', [VF] + scene_lines(LV2, [150000] * 50) + [VW], std=[LIM])
e2 = w34('E34g', [VF] + scene_lines(LV2, [150000] * 50) + [VW, LIM])
ok &= case('E34f (b)(1): a limit line in the stdout or in the log -> FAIL with 1, the only failing row',
           row34(e, 1) == (False, '1') and row34(e2, 1) == (False, '1') and
           [a[0][:11] for a in e['admit'] if not a[1]] == ['W 295(b)(1)'] and
           [a[0][:11] for a in e2['admit'] if not a[1]] == ['W 295(b)(1)'])
l35 = [VF, '[Vulkan][W][2]: early, before the entry line'] + scene_lines(LV2, [150000] * 80)
e = w34('E35', l35)
ok &= case('E35 (b)(3): the only layer line before the entry line -> the whole hold after it (12 000 000 us + the first frame '
           'and the loading rows) -> FAIL', row34(e, 3)[0] is False and int(row34(e, 3)[1].split()[0]) > 10000000)
l35b = [VF] + scene_lines(LV2, [150000] * 80) + [start('another_level'), VW, ft(200, 150000)]
e = w34('E35b', l35b)
ok &= case('E35b (b)(3): the layer line after a scene change -> the rows after the change are not the hold -> 0 us, PASS',
           row34(e, 3) == (True, '0 us'))
for i, (name, lines, js, why) in enumerate((
        ('a death marker with a [Vulkan][E] report (VALIDATION_STOP)', [VF] + scene_lines(LV2, [150000] * 20) + [
            '--- Error ---', '[Vulkan][E][2]: vkCreateGraphicsPipelines(): bad', LIM], None, 'death marker --- Error ---'),
        ('the attempt outcome timeout', [VF, 'x'], js145('w145_02', attempt=dict(outcome='timeout')),
         'attempt outcome timeout'),
        ('hold_exit set', [VF] + scene_lines(LV2, [150000] * 20), js145('w145_02', attempt=dict(hold_exit=12.0)),
         'hold_exit / ENDED / exited'),
        ('the attempt outcome exited', [VF] + scene_lines(LV2, [150000] * 20), js145('w145_02', attempt=dict(
            outcome='exited')), 'hold_exit / ENDED / exited'))):
    e = w34('E36_%d' % i, lines, js=js)
    ok &= case('E36 a W not held (%s): the rows (1)-(3) print n/a and pass, (b)(4) is still read; the print says NOT held' % name,
               all(row34(e, k) == (True, 'n/a (W not held: %s)' % why) for k in (1, 2, 3)) and row34(e, 4)[0] is True and
               e['held'] == (False, why) and any(x.startswith('  W form of item 295 (b): NOT held (%s) - rows (1)-(3) n/a;' % why)
                                                 for x in S.fmt_entry(e)))
pd = mk145(BASE / 'E36d', 'w145_02')
os.remove(pd + '/log_w145_02.txt')
e = S.entry_of('w145_02', pd, SH5)
ok &= case('E36d a W without its log -> not held (log missing), rows (1)-(3) n/a', e['held'] == (False, 'log missing') and
           row34(e, 3) == (True, 'n/a (W not held: log missing)'))
e = w34('E36e', [VF, VW, 'x'])
e2 = w34('E36f', [VF, start(LV2), VW])
ok &= case('E36e (b)(3) on a held W without the entry line, and with the entry line but no hold row -> FAIL with none',
           row34(e, 3) == (False, 'none') and row34(e2, 3) == (False, 'none') and e['held'][0] and e2['held'][0])
e = w34('E36b', [VF, 'x'], js=js145('w145_02', attempt=dict(outcome='timeout'), filt=FILT))
ok &= case('E36b a W not held with the filter in its env -> the row (b)(4) FAIL', row34(e, 4) == (
    False, 'W form: limit=100000000 filter=%s' % FILT))
ok &= case('E36c w_form4: the form line from the env; the key present with the value "none" or "" fails',
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000'}) == (True, 'W form: limit=100000000 filter=none') and
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000', 'VK_LAYER_MESSAGE_ID_FILTER': 'none'}) == (
               False, 'W form: limit=100000000 filter=none') and
           S.w_form4({'VK_LAYER_DUPLICATE_MESSAGE_LIMIT': '100000000', 'VK_LAYER_MESSAGE_ID_FILTER': ''}) == (
               False, 'W form: limit=100000000 filter=') and S.w_form4({}) == (False, 'W form: limit=None filter=none'))
KINDS = ['Window 1 shown', 'Window 1 hidden', 'Window 1 exposed', 'Window 1 moved to 10,10', 'Window 1 resized to 1280x720',
         'Window 1 size changed to 1280x720', 'Window 1 minimized', 'Window 1 maximized', 'Window 1 restored',
         'Window 1 gained keyboard focus', 'Window 1 lost keyboard focus', 'Window 1 closed', 'Window 1 got unknown event 7',
         'Mouse entered window 1', 'Mouse left window 12']
e = w34('E37', wl(LV2) + KINDS[:8] + ['Mouse entered window', 'Window x closed', 'window 1 shown', 'Window 1 shownX'],
        std=KINDS[8:] + KINDS[:1])
ok &= case('E37 the 15 window kinds of window.cpp are counted in the log and the stdout (shown twice); "Mouse entered window" '
           'without an id, "Window x", lower case and "shownX" are not',
           e['winall'] == dict((k, 2 if k == 'shown' else 1) for k in S.WIN_ALL) and
           any(x == '  window lines by kind (item 295 (g); log and stdout; data): shown 2, hidden 1, exposed 1, moved to 1, '
               'resized 1, size changed 1, minimized 1, maximized 1, restored 1, gained keyboard focus 1, lost keyboard focus '
               '1, closed 1, got unknown event 1, Mouse entered window 1, Mouse left window 1' for x in S.fmt_entry(e)))
CH6 = S.CHUNK
S.CHUNK = 41
sc37 = S.scan(str(BASE / 'E37' / 'log_w145_02.txt'))
S.CHUNK = CH6
ok &= case('E37b the window kinds and their positions across 41-byte chunks: 8 lines once each',
           sum(sc37['winall'].values()) == 8 and len(sc37['winpos']) == 8 and
           [k for k, _ in sc37['winpos']] == list(S.WIN_ALL[:8]))
post38 = [16667] * 10 + [150000] + [50000] * 40 + [16667] * 200 + [150000] + [50000] * 39 + [50001] + [16667] * 320 + \
         [1500000] + [16667] * 500 + [1200000] + [16667] * 10
l38 = [PRE] + scene_lines(LV2, post38)
l38 = ins_after(l38, 65, 'Mouse entered window 1')
l38 = ins_after(l38, 306, 'Window 1 moved to 5,5')
l38 = ins_after(l38, 626, 'Window 1 lost keyboard focus')
e38 = S.entry_of('v145_02', mk145(BASE / 'E38', 'v145_02', lines=l38, std=['Window 1 hidden']), SH5)
ok &= case('E38 the nearest window line of each K2 / K3 frame: a line exactly 2 s after a K3 frame -> found (+2.000 s); a line '
           '2.000001 s after the next one -> none; a line right before a K2 frame -> 0 s; a K2 frame with only a stdout line '
           '-> none; entry / hold by the 599 rows of the window',
           e38['winnear'] == [(25, 150000, 'K3', 'entry', ('Mouse entered window', 2000000)), (266, 150000, 'K3', 'entry', None),
                              (627, 1500000, 'K2', 'hold', ('lost keyboard focus', 0)), (1128, 1200000, 'K2', 'hold', None)]
           and e38['winall']['hidden'] == 1 and
           any(x == '  window line nearest each K2 / K3 frame after the first scene frame (item 295 (g); +-2 s of presented time '
               'by byte position in the log; data): K2 2 frames, K3 2 frames; with a window line within 2 s: n 25 K3 entry dt '
               '150000 -> Mouse entered window +2.000 s; n 627 K2 hold dt 1500000 -> lost keyboard focus +0.000 s; K2 without '
               'one: n 1128 K2 hold dt 1200000 -> none; K3 without one (none): 1' for x in S.fmt_entry(e38)))
l38b = ins_after(scene_lines(LV2, [16667] * 10 + [1500000] + [400000] * 4 + [16667] * 200 + [100000] + [16667] * 200 +
                             [1000000] + [16667] * 182 + [150000] + [16667] * 5), 26, 'Window 1 exposed')
l38b = [PRE] + ins_after(l38b, 24, 'Window 1 shown')
e38b = S.entry_of('v145_02', mk145(BASE / 'E38b', 'v145_02', lines=l38b), SH5)
ok &= case('E38b a line at the end of the row before a frame is at 0 for that frame; a line at the end of a frame is at 0 for it '
           'and for the next; a line before a frame is negative; the nearest wins (a line 1.9 s before loses to one at 0.4 s)',
           e38b['winnear'] == [
               (25, 1500000, 'K2', 'entry', ('shown', 0)), (26, 400000, 'K3', 'entry', ('exposed', 0)),
               (27, 400000, 'K3', 'entry', ('exposed', 0)), (28, 400000, 'K3', 'entry', ('exposed', -400000)),
               (29, 400000, 'K3', 'entry', ('exposed', -800000)), (230, 100000, 'K3', 'entry', None),
               (431, 1000000, 'K2', 'entry', None), (614, 150000, 'K3', 'hold', None)])
e38d = S.entry_of('v145_02', mk145(BASE / 'E38d', 'v145_02', lines=[PRE] + scene_lines(LV2, [16667] * 10) + [
    start('another_level'), ft(100, 1500000)]), SH5)
ok &= case('E38d a K2 frame after a scene change is not a frame of the hold: no K2 / K3 frame', e38d['winnear'] == [])
XS38 = S.XSRC
S.XSRC = {'v144_09': dict(root=(BASE / 'E38' / 'none').as_posix(), chain='go144a', pred='none.md')}
o38 = S.summary(str(BASE / 'E38'), SH5, None)[0]
S.XSRC = XS38
ok &= case('E38c the summary names the K2 / K3 frames with a window line within 2 s and the tags by kind',
           'WINDOW LINE NEAR A K2 / K3 FRAME (item 295 (g); within 2 s; data): v145_02 n 25 K3 entry -> Mouse entered window '
           '+2.000 s; v145_02 n 627 K2 hold -> lost keyboard focus +0.000 s' in o38 and
           'WINDOW LINES BY KIND (item 295 (g); log and stdout; data): v145_02: hidden 1, moved to 1, lost keyboard focus 1, '
           'Mouse entered window 1' in o38)
rq = rows_at([0.1 * i for i in range(21)])
iq = sorted([0.1 * i - 0.0105 for i in range(20) if i not in (5, 6, 7)] + [2.0])
q = S.vquality(rq, iq, 2)
ok &= case('E39 vquality: records 10.5 ms before the row ends except the anchor; rows 5..7 without a record: within 8 ms 1 of 21 '
           'at shift 0, the best shift -3 ms (18 rows; a plateau -8..-3 ms, the smaller |shift|), the continuity count 3 at '
           'both, no mark; the 600 rows after the first scene frame are 19 (from it on: 20)',
           q == dict(rows=21, near=1, n600=19, near600=1, n600f=20, near600f=1, shift=-3, near_best=18, after0=3,
                     after_best=3, mark=False))
ok &= case('E39b the print of the alignment', S.fmt_vq(q) == 'rows with a .idx record within 8 ms: 1 of 21 (4.8 %); in the 19 '
           'rows after the first scene frame 1 (5.3 %) [from the first scene frame on: 1 of 20]; best shift of the anchor in '
           '+-50 ms -3 ms (18 rows within 8 ms); rows without a record after the first scene frame: 3 at shift 0, 3 at the best '
           'shift' and S.fmt_vq(None).startswith('n/a'))
iq2 = [0.1 * i - 0.0105 for i in range(20)] + [2.0]
q2 = S.vquality(rq, iq2, 2)
iq3 = [0.1 * i + 0.0105 for i in range(20)] + [2.0]
q3 = S.vquality(rq, iq3, 2)
ok &= case('E39c the best shift: -3 ms for records 10.5 ms early, +3 ms for records 10.5 ms late (symmetric); 21 of 21 within '
           '8 ms there', q2['shift'] == -3 and q2['near_best'] == 21 and q3['shift'] == 3 and q3['near_best'] == 21)
iq4 = [0.1 * i for i in range(21)]
q4 = S.vquality(rq, iq4, 2)
ok &= case('E39d exact records: shift 0 (a plateau -8..+8 ms, the smaller |shift| wins), all rows within 8 ms; 19 of the 19 '
           'rows after the first scene frame, 20 of 20 from it on',
           q4['shift'] == 0 and q4['near'] == 21 and q4['near_best'] == 21 and q4['n600'] == 19 and q4['near600'] == 19 and
           q4['n600f'] == 20 and q4['near600f'] == 20)
ok &= case('E39f near_count: exactly 8 ms is within, 8.1 ms is not; the record before and the record after are both looked at; '
           'beyond the last record or before the first',
           S.near_count([0.0], [0.008]) == 1 and S.near_count([0.0], [0.0081]) == 0 and
           S.near_count([1.0], [0.995, 1.5]) == 1 and S.near_count([1.0], [0.5, 1.004]) == 1 and
           S.near_count([3.0], [1.0, 2.0]) == 0 and S.near_count([0.0], [1.0]) == 0 and
           S.near_count([1.0, 1.5, 2.0], [1.0, 2.0]) == 2)
iq5 = [0.1 * i - 0.0105 if i % 2 == 0 else 0.1 * i + 0.0105 for i in range(20)] + [2.0]
q5 = S.vquality(rq, iq5, 2)
ok &= case('E39g a tie between -3 and +3 ms (records of even rows early, of odd rows late; 11 rows each) -> the negative shift',
           q5['shift'] == -3 and q5['near_best'] == 11)
iq6 = [0.1 * i - 0.0125 for i in range(20)] + [2.0]
q6 = S.vquality(rq, iq6, 2)
ok &= case('E39h records 12.5 ms early: at shift 0 every row ends 12.5 ms inside a gap of 100 ms (18 rows after the first scene '
           'frame), at the best shift -5 ms (21 rows within 8 ms) 7.5 ms inside the margin (0 rows) -> mark [I] and printed',
           q6 == dict(rows=21, near=1, n600=19, near600=1, n600f=20, near600f=1, shift=-5, near_best=21, after0=18,
                      after_best=0, mark=True) and S.fmt_vq(q6).endswith(
               'rows without a record after the first scene frame: 18 at shift 0, 0 at the best shift - [I] the counts differ '
               'by more than 10 %'))
ok &= case('E39e vquality None without rows, records, a first scene frame or its row',
           S.vquality([], iq, 2) is None and S.vquality(rq, [], 2) is None and S.vquality(rq, iq, None) is None and
           S.vquality(rq, iq, 99) is None)
VC_REAL = S.vcont
for a0, ab, mk in ((10, 11, False), (10, 12, True), (10, 9, False), (10, 8, True), (0, 0, False), (0, 1, True)):
    seq = iter([a0, ab])
    S.vcont = lambda *a, **k: dict(after=next(seq))
    qm = S.vquality(rq, iq, 2)
    S.vcont = VC_REAL
    ok &= case('E40 the mark of item 295 (d): %d at shift 0, %d at the best shift -> mark %s (more than 10 %% of the first; 0 '
               'against > 0)' % (a0, ab, mk), qm['mark'] is mk and qm['after0'] == a0 and qm['after_best'] == ab)
rr40 = rows_at([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
ok &= case('E40b vcont with a shift moves every row end after the anchoring: 0 -> 2 rows (n 4, 5); -0.05 s -> 4 (n 4, 5, 6 in '
           'the long gap, n 7 in the last); +0.25 s -> 1 (n 4 in the last gap; n 1..3 in the long gap are before the first '
           'scene frame)',
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, 0.0)['after'] == 2 and
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, -0.05)['after'] == 4 and
           S.vcont(rr40, [0.0, 0.1, 0.2, 0.5, 0.6], 3, 0.25)['after'] == 1)
e41 = S.entry_of('v145_02', str(R22), SH5)
ok &= case('E41 a V with a .idx prints the alignment line next to the continuity line (the record lacking three frames: the '
           'count 3 at shift 0); a V without K2 / K3 frames prints so', e41['vq'] is not None and e41['vq']['after0'] == 3 and
           any(x.startswith('  video continuity alignment (item 295 (d); data, not a gate): rows with a .idx record within '
                            '8 ms: ') for x in S.fmt_entry(e41)) and
           '  window line nearest each K2 / K3 frame after the first scene frame (item 295 (g); +-2 s of presented time by '
           'byte position in the log; data): no K2 / K3 frame after the first scene frame' in S.fmt_entry(e41))
try:
    ('\n'.join(o14 + o18 + o23 + o24 + o24f + fE10 + l4 + l4b + l4d + r16[1].split('\n') + r25[1].split('\n') +
               S.fmt_entry(e22) + o24h + o38 + S.fmt_entry(e38) + S.fmt_entry(e41))).encode('cp1250', errors='strict')
    ('\n'.join(o24 + fE10 + l4 + S.fmt_entry(e22))).encode('ascii', errors='strict')
    ence = True
except UnicodeError:
    ence = False
ok &= case('E33 every line new in profile 145 is ASCII (strict cp1250 and ascii)', ence)
# ---------------- PART F (session 146 step 0, HPP-386; ROADMAP s122 item 309 (k), (l)(1)-(7), item 300 (b)(4), item 281 (g)):
# the profile of session 146 - the 35 tags and their order, the re-check and second-hold V, the W form on the shipment binary
# (precache by default), the DualSrcBlend control (control stop term, data row of every W, variant [I] of item 281 (g)), the
# stubs (F13) and asserts (F14) rows, the tile events (D-4), SKIPPED_V_NOT_ENTERED (--skip-w and the summary), the stop-check
# from score.json (its source line, the fall back to the log), the three-V rule over every made V, RECHECK / B40 / Sky Garden
# lines, ASCII.
S.profile(P146)
BUILD6 = 'dac02fb9d6fd32b3e812bb4cce6468375e746f8724a222d7f9b4073f49d1200e'
LV15 = ('robot_builder_next', 'interactive_credit_00', 'non_interactive_credit', 'ending_boss_after_credit',
        'collectible_viewer', 'hub_crashsite_diorama', 'diorama_controller_skin', 'diorama_astro_skin', 'diorama_zoo',
        'fragile_battle_1', 'voxel_challenge_1', 'armadillo_challenge_1', 'fragile_battle_2', 'voxel_challenge_2',
        'fragile_battle_3')
RCK = (('r146_01', 'hoover_beach'), ('r146_02', 'sponge_dirty_bath'), ('r146_03', 'timestop_casino'),
       ('r146_04', 'bonus_path_maker_mix'))
SEQ146 = ['w146_00'] + [r for r, _ in RCK] + [x for i in range(5, 20) for x in ('v146_%02d' % i, 'w146_%02d' % i)]
ok &= case('F1 the 35 tags of item 309 (l)(2) in that order; control w146_00 on Sky Garden; the re-check r146_01..03 and the '
           'second hold r146_04 (V only, outside the census); the 15 pairs v146_NN / w146_NN of the list of step 0; no V of '
           'another session',
           list(S.SEQ) == SEQ146 and len(S.SEQ) == 35 and S.CONTROL == ('w146_00', SKY) and S.RECHECK == RCK and
           S.PAIRS == tuple(('v146_%02d' % (i + 5), 'w146_%02d' % (i + 5), lv) for i, lv in enumerate(LV15)) and
           S.CENSUS == tuple(('v146_%02d' % (i + 5), lv) for i, lv in enumerate(LV15)) and S.LEVELS == LV15 and
           S.V_TAGS == tuple(r for r, _ in RCK) + tuple('v146_%02d' % i for i in range(5, 20)) and
           S.W_TAGS == ('w146_00',) + tuple('w146_%02d' % i for i in range(5, 20)) and S.XSRC == {} and S.XSHEET == ())
ok &= case('F2 the root, seal, chain, runs dir, scorer of 146; the build dac02fb9; the flags (FORM146 on, REPEAT off); halves '
           'of eight; the W form line of item 295 unchanged; B40 and warm-up names',
           S.ROOT == 'C:/kyty/s146' and S.PRED_PATH == 'C:/kyty/s146/pred/02_sc146.md' and S.CHAIN == 'go146a' and
           S.RUNS == 'runs146' and S.SCORER == 'sc146.py' and S.EXTRA is True and S.FORM144 is True and
           S.FORM145 is True and S.FORM146 is True and S.REPEAT is False and S.BUILD_SHA == BUILD6 and S.HALF == 8 and
           S.W_FORM_LINE == 'W form: limit=100000000 filter=none' and S.B40_TAG == 'r146_04' and
           S.B40_FIRST == 'v145_14' and S.WARMUP == ('i146_v', 'score_i146_v.txt'))
ok &= case('F3 the constants of sc145 are unchanged in profile 146 (item 309 (l)(4))',
           (S.SCENE_DRAWS, S.ENTRY_WIN, S.K2_US, S.K3_US, S.HOLD_CENSUS_US, S.HOLD_CENSUS_S, S.HOLD_SCENE_US, S.HOLD_W_S,
            S.HOLD_V_S, S.FRAMES_V, S.COVER_SLACK, S.PRIO_US, S.STOP_RUN, S.HOLD_W_HARNESS_S, S.REPORT_LINES, S.W_STOP_RUN,
            S.LAYER_END_US, S.WIN_NEAR_US, S.VQ_NEAR, S.VQ_SHIFT_MS, S.VQ_ROWS, S.VQ_MARK, S.VC_GAP, S.VC_MARG) ==
           (100, 599, 1000000, 100000, 120000000, 120, 300000000, 300, 330, 3000, 100, 50000, 3, 310, 50, 2, 10000000,
            2000000, 0.008, 50, 600, 0.10, 0.060, 0.012) and
           S.OPCODE_BASE == {('SOP1', '0x21'): 96, ('SOP1', '0x0c'): 1, ('VOPC', '0xe3'): 4} and
           S.M_STUBCALL == b'Unresolved import stub called' and S.M_ASSERT == b'ASSERT:' and S.M_UMP == b'user_msg_param')
ok &= case('F4 level_of in 146: control -> Sky Garden; r146_01..04 -> the re-check levels; v146_05 / w146_19 -> the list; '
           'v145_02, w146_04, r146_05, i146_v -> unknown',
           S.level_of('w146_00') == SKY and [S.level_of(r) for r, _ in RCK] == [lv for _, lv in RCK] and
           S.level_of('v146_05') == 'robot_builder_next' and S.level_of('w146_19') == 'fragile_battle_3' and
           S.level_of('v145_02') is None and S.level_of('w146_04') is None and S.level_of('r146_05') is None and
           S.level_of('i146_v') is None)
K146 = ('ROOT', 'PRED_PATH', 'CHAIN', 'RUNS', 'SCORER', 'EXTRA', 'FORM144', 'FORM145', 'FORM146', 'REPEAT', 'BUILD_SHA',
        'RECHECK', 'LEVELS', 'PAIRS', 'CENSUS', 'SEQ', 'V_TAGS', 'W_TAGS', 'SEALED_NAMES', 'CONTROL', 'XSRC', 'XSHEET',
        'XSHEET_NOTE', 'HALF')
ok &= case('F5 P145 and P146 set every key profile 146 changes; P145 keeps sc145 (root s145, go145a, 9235a7ac, FORM146 off, 34 '
           'tags, the v144_09 of another session); the profiles 144, 143, 142 carry FORM146 off and the build 9235a7ac',
           set(K146) <= set(S.P145) and set(K146) <= set(S.P146) and S.P145['FORM146'] is False and
           S.P145['BUILD_SHA'] == BUILD and S.P145['ROOT'] == 'C:/kyty/s145' and len(S.P145['SEQ']) == 34 and
           S.P145['CHAIN'] == 'go145a' and S.P145['RECHECK'] == () and 'v144_09' in S.P145['XSRC'] and
           all(p['FORM146'] is False and p['BUILD_SHA'] == BUILD and p['RECHECK'] == () for p in (S.P144, S.P143, S.P142)))
REQ146 = ('go146a.sh', 'sc146.py', 'test_sc146.py', 'mut_sc146.py', 'enter_scene.py', 'sheet142.py', 'fgcpu146.py',
          'cachemf146.py', 'lockcheck146.py', 'tiles146.py', 'test_tools146.py', 'C:/kyty/scripts/s51_vidglitch.py',
          'step2/next_one.sh', 'step2/call_one.sh', 'step2/wait_one.sh', 'step2/pre_one.sh', 'step2/apichk146.py',
          'step2/gate146.py', 'step2/test_gate146.py', 'runs146/cache_i146_v.after.json', 'score_i146_v.txt',
          'pred/00_i146.md', 'step0/lvl146.py', 'step0/lvl146.out.txt')
ok &= case('F6 the seal of 146 names the chain, scorer, fixtures, mutants, enter_scene.py, sheet142.py, s51_vidglitch.py, the '
           'tile tool, the step 2 wrappers with the API check and the gate, the warm-up manifest, reading and seal, the list '
           'script and its output; no name of 145',
           all(n in S.SEALED_NAMES for n in REQ146) and not any('145' in n for n in S.SEALED_NAMES))
PR6 = BASE / 'pred146.md'
PR6.write_text('fixture seal 146 part F\n', encoding='utf-8')
SH6 = hashlib.sha256(PR6.read_bytes()).hexdigest()
DUAL11 = 'DualSrcBlend: supported=1 enabled=1'


def js146(tag, attempt=None, precache=None, dup='100000000', **over):
    is_w = tag in S.W_TAGS
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x'] + (['--vulkan-validation', 'true'] if is_w else [])
    env = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GUEST_ARGS': '-lvl %s' % S.level_of(tag), 'KYTY_GPU_CLOCK_PIN': '1',
           'KYTY_GPU_MARKERS': '0'}
    if is_w:
        env['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        if precache is not None:
            env['KYTY_PIPELINE_PRECACHE'] = precache
        if dup is not None:
            env['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = dup
    else:
        env['KYTY_REC'] = 'C:\\kyty\\s146\\rec_%s.mp4' % tag
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=310.0 if is_w else 330.0, hold_exit=None, ft_tail=300,
             pipeline_cache_off=False, level=S.level_of(tag))
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD6, guest_args='-lvl %s' % S.level_of(tag), gates='', env=env, cmdline=cmd,
              prereg=dict(path=S.PRED_PATH, sha256=SH6), attempts=[a])
    js.update(over)
    return js


def wl6(lv, dual=True, post=None):
    return ([DUAL11] if dual else []) + [VF, PRE] + scene_lines(lv, [150000] * 2000 if post is None else post) + [VW] * 3


def mk146(root, tag, lines=None, js=None, glitch=(3200, 0), sheet=True, std=(), extra=(), tiles=None):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    is_w = tag in S.W_TAGS
    lv = S.level_of(tag)
    if lines is None:
        lines = (wl6(lv) if is_w else [PRE] + scene_lines(lv, v_post())) + list(extra)
    (root / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js146(tag)), encoding='utf-8')
    (root / ('log_%s.txt' % tag)).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    (root / 'step2').mkdir(exist_ok=True)
    with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
        f.write('2026-10-02T00:00:00Z go146a %s enter_scene end rc 0 log_%s.txt sha256 %s\n' % (
            tag, tag, _h.sha256((root / ('log_%s.txt' % tag)).read_bytes()).hexdigest()))
    (root / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(std) + '\n').encode('utf-8'))
    (root / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if is_w:
        return str(root)
    if tiles is not None:
        (root / ('tiles_%s.txt' % tag)).write_text(tiles)
    if glitch is not None:
        (root / ('glitch_%s.txt' % tag)).write_text('C:/kyty/s146/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                    'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if sheet:
        (root / ('sheet_%s.png' % tag)).write_bytes(b'png')
        (root / ('rec_%s.mp4' % tag)).write_bytes(('mp4 ' + tag).encode())
        with open(root / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
            f.write('2026-10-02T00:00:00Z go146a %s s51_vidglitch rc 0 glitch_%s.txt sha256 %s rec_%s.mp4 sha256 %s\n' % (
                tag, tag, 'ab' * 32, tag, _h.sha256(('mp4 ' + tag).encode()).hexdigest()))
            f.write('2026-10-02T00:00:00Z go146a %s sheet rc 0 sheet_%s.png sha256 %s\n' % (
                tag, tag, _h.sha256(b'png').hexdigest()))
    return str(root)


def run6(args, root):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = S.main(args, root=str(root), pred=str(PR6))
    return rc, b.getvalue()


RF = BASE / 'F7'
for t in ('w146_00', 'r146_01', 'v146_05', 'w146_05'):
    mk146(RF, t)
eF = dict((t, S.entry_of(t, str(RF), SH6)) for t in ('w146_00', 'r146_01', 'v146_05', 'w146_05'))
ok &= case('F7 good control W, re-check V, and the V and W of a pair are admitted; the build row names dac02fb9; every W has the '
           'row "W form on the shipment binary" and NOT the row of the precache lines of profile 144-145; the V keeps "V positive '
           'control"',
           all(adm_ok(e) for e in eF.values()) and
           all(len(adm_rows(eF[t], 'W form on the shipment binary: no KYTY_PIPELINE_PRECACHE')) == 1 and
               not adm_rows(eF[t], 'W form: no "PipelinePrecache') and not adm_rows(eF[t], 'W form: KYTY_PIPELINE_PRECACHE=0')
               for t in ('w146_00', 'w146_05')) and
           all(len(adm_rows(eF[t], 'build dac02fb9')) == 1 for t in eF) and
           len(adm_rows(eF['v146_05'], 'V positive control')) == 1 and len(adm_rows(eF['r146_01'], 'V positive control')) == 1)
for i, (name, pc) in enumerate((('KYTY_PIPELINE_PRECACHE=0', '0'), ('KYTY_PIPELINE_PRECACHE=1', '1'),
                                ('KYTY_PIPELINE_PRECACHE empty', ''))):
    e = S.entry_of('w146_05', mk146(BASE / ('F8_%d' % i), 'w146_05', js=js146('w146_05', precache=pc)), SH6)
    ok &= case('F8 a W with %s in its env -> not admitted by the shipment-binary form row only' % name,
               not adm_ok(e) and [a[0][:30] for a in e['admit'] if not a[1]] == ['W form on the shipment binary:'])
e = S.entry_of('w146_05', mk146(BASE / 'F9', 'w146_05', lines=[x for x in wl6(S.level_of('w146_05')) if x != PRE]), SH6)
e9b = S.entry_of('w146_05', mk146(BASE / 'F9b', 'w146_05', lines=wl6(S.level_of('w146_05')) + [PRE]), SH6)
ok &= case('F9 a W without a "PipelinePrecache: N recipes ->" line is still admitted (a data row in 146); the print gives 0; a W '
           'with two such lines prints 2',
           adm_ok(e) and e['precache']['log'] == 0 and adm_ok(e9b) and e9b['precache']['log'] == 2 and
           '  W precache by default (item 300 (b)(4); data): "PipelinePrecache: N recipes ->" lines log 0, stdout 0' in
           S.fmt_entry(e))
DCASES = (('the line before the first GuestOut', [DUAL11] + wl6(SKY, dual=False), True),
          ('the line after the first GuestOut only', wl6(SKY, dual=False)[:8] + [DUAL11] + wl6(SKY, dual=False)[8:], False),
          ('supported=1 enabled=0', ['DualSrcBlend: supported=1 enabled=0'] + wl6(SKY, dual=False), False),
          ('supported=0 enabled=1', ['DualSrcBlend: supported=0 enabled=1'] + wl6(SKY, dual=False), False),
          ('no line', wl6(SKY, dual=False), False),
          ('a W without any GuestOut line, the line present', [DUAL11, VF, PRE, ft(1, 20000, 5)], True),
          ('two lines, the second one 1/1', ['DualSrcBlend: supported=0 enabled=0', DUAL11] + wl6(SKY, dual=False), True),
          ('supported=1 enabled=10 (two digits)', ['DualSrcBlend: supported=1 enabled=10'] + wl6(SKY, dual=False), False))
for i, (name, lines, want) in enumerate(DCASES):
    root = mk146(BASE / ('F10_%d' % i), 'w146_00', lines=lines)
    e = S.entry_of('w146_00', root, SH6)
    c = S.control_state(e)
    rc, out = run6(['--stop-check', 'r146_01'], root)
    fm = [x for x in S.fmt_entry(e) if x.startswith('  W DualSrcBlend control')]
    ok &= case('F10 DualSrcBlend %s -> %s; the control letter %s; rc of the stop-check before r146_01 %s; the print' % (
        name, 'present' if want else 'ABSENT', 'pass' if want else 'stop', 0 if want else 5),
        e['dual_ok'] is want and (('no line "DualSrcBlend: supported=1 enabled=1" before the first GuestOut line (item 300 '
                                   '(b)(4))' in c[2]) is (not want)) and (rc == (0 if want else 5) or (i == 5 and rc == 5))
        and len(fm) == 1 and (('-> present;' in fm[0]) if want else ('-> ABSENT;' in fm[0] and fm[0].endswith('FAIL'))))
e = S.entry_of('w146_05', mk146(BASE / 'F10b', 'w146_05', lines=wl6(S.level_of('w146_05'), dual=False)), SH6)
ok &= case('F10b a non-control W without the DualSrcBlend line is admitted (a data row, item 309 (l)(4)); the print names the '
           'variant of item 281 (g) FAIL',
           adm_ok(e) and e['dual_ok'] is False and
           any(x.startswith('  W DualSrcBlend control') and x.endswith('; not in the verdict): FAIL') for x in S.fmt_entry(e)))
STUB = 'Unresolved import stub called: b-dYXrjSNZU'
ASR = 'ASSERT: failed something'
UMP = '\t user_msg_param = 0x0000000000000000'
CH6 = S.CHUNK
S.CHUNK = 37
root = mk146(BASE / 'F11', 'v146_05', extra=[STUB, STUB, ASR, UMP], std=[STUB, ASR, UMP, UMP])
e11 = S.entry_of('v146_05', root, SH6)
S.CHUNK = CH6
f11 = S.fmt_entry(e11)
ok &= case('F11 stubs (F13) and asserts (F14) counted in log and stdout across 37-byte chunks; the print rows; a V with them is '
           'still admitted (data rows)',
           e11['stubcall'] == dict(log=2, stdout=1) and e11['asserts'] == dict(log=1, stdout=1, ump_log=1, ump_stdout=2) and
           adm_ok(e11) and
           '  stubs (F13, item 309 (l)(4); data): "Unresolved import stub called" lines log 2, stdout 1' in f11 and
           '  asserts (F14, item 309 (l)(4); data): "ASSERT:" lines log 1, stdout 1; "user_msg_param" lines log 1, stdout 2 - != '
           '0: a row of the close in register F' in f11)
e11b = S.entry_of('v146_05', mk146(BASE / 'F11b', 'v146_05'), SH6)
ok &= case('F11b no stub / assert lines -> zeros, no register note',
           e11b['stubcall'] == dict(log=0, stdout=0) and e11b['asserts'] == dict(log=0, stdout=0, ump_log=0, ump_stdout=0) and
           '  asserts (F14, item 309 (l)(4); data): "ASSERT:" lines log 0, stdout 0; "user_msg_param" lines log 0, stdout 0' in
           S.fmt_entry(e11b))
TL = 'TILES rec_v146_05.mp4 sha256 %s: frames 12000; tile events T4 2, T12 1; events [[10, 0, 0, 6.2, 6.3, 0.6, 1], [20, 3, 3, 14.0, 13.0, 1.0, 2]]\n' % ('ab' * 32)
e12 = S.entry_of('v146_05', mk146(BASE / 'F12', 'v146_05', tiles=TL), SH6)
e12b = S.entry_of('v146_05', mk146(BASE / 'F12b', 'v146_05', tiles='TILES rec_v146_05.mp4 ERROR size\n'), SH6)
e12c = S.entry_of('v146_05', mk146(BASE / 'F12c', 'v146_05'), SH6)
e12d = S.entry_of('v146_05', mk146(BASE / 'F12d', 'v146_05', tiles='TILES rec_v146_05.mp4 sha256 %s: frames 5; tile events T4 0, '
                                   'T12 0; events \n' % ('ab' * 32)), SH6)
ok &= case('F12 tile events read from tiles_<V>.txt (T4 2, T12 1, the events printed); an error line or no file -> n/a; never '
           'an admission row',
           e12['tiles']['t4'] == 2 and e12['tiles']['t12'] == 1 and e12['tiles']['frames'] == 12000 and
           e12b['tiles'] is None and e12c['tiles'] is None and adm_ok(e12) and adm_ok(e12b) and
           e12d['tiles'] is not None and e12d['tiles']['t4'] == 0 and e12d['tiles']['events'] == '' and
           any(x.startswith('  tile events (D-4, the auditor tile rule of AUDIT145 s1.4, threshold 4; data): frames 12000; frames '
                            'with a tile event T4 2, T12 1; events') for x in S.fmt_entry(e12)) and
           '  tile events (D-4, the auditor tile rule of AUDIT145 s1.4, threshold 4; data): n/a (no tiles_<tag>.txt)' in
           S.fmt_entry(e12c))
# SKIPPED_V_NOT_ENTERED: --skip-w from the json of --tag and from the log
R13 = BASE / 'F13'
mk146(R13, 'v146_05', lines=[PRE] + [ft(i, 20000, 5) for i in range(1, 50)])
rcA, outA = run6(['--skip-w', 'w146_05'], R13)
run6(['--tag', 'v146_05'], R13)
rcB, outB = run6(['--skip-w', 'w146_05'], R13)
mk146(R13, 'v146_06')
run6(['--tag', 'v146_06'], R13)
rcC, outC = run6(['--skip-w', 'w146_06'], R13)
rcD, outD = run6(['--skip-w', 'w146_07'], R13)
rcE, outE = run6(['--skip-w', 'w146_00'], R13)
rcF, outF = run6(['--skip-w', 'v146_05'], R13)
L13 = (R13 / 'log_v146_05.txt').read_bytes()
T13 = ('; log_v146_05.txt %d bytes sha256 %s = the enter_scene end line of step2/times.txt, no entry line (item 309 (k)(1), '
       '316 (b)-(d))\n' % (len(L13), _h.sha256(L13).hexdigest()[:16]))
ok &= case('F13 --skip-w: a V without its entry line, no marker, its log = the times.txt line -> rc 0 SKIPPED_V_NOT_ENTERED '
           'with the V key attempt:ok and the log evidence (from the log before --tag, from score.json after it); an entered V '
           '-> rc 1 RUN; a V not made -> rc 1 (no reading); the control W and a V tag -> usage rc 2',
           rcA == 0 and outA == 'SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED key attempt:ok (log (no '
           'score.json))' + T13 and
           rcB == 0 and outB == 'SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED key attempt:ok (json)' + T13 and
           rcC == 1 and outC.startswith('RUN w146_06: its V v146_06 outcome HOLDS_120 (json)') and
           rcD == 1 and outD.startswith('RUN w146_07: its V v146_07 has no reading') and rcE == 2 and rcF == 2)
(R13 / 'skipped_w146_05.txt').write_text('SKIPPED_V_NOT_ENTERED w146_05 x\n')
o13 = S.summary(str(R13), SH6, None)[0]
ok &= case('F14 the summary of a skipped W: the TAG line, the pair NO by "W made", the SKIPPED line names it; the W is not a made '
           'W of the stop rules',
           'TAG w146_05: SKIPPED_V_NOT_ENTERED (item 309 (k)(1): the V of its pair is NOT_ENTERED; not an attempt)' in o13 and
           'SCENE_OK robot_builder_next: NO' in o13 and
           'SKIPPED_V_NOT_ENTERED (item 309 (k)(1); W not called, not attempts): w146_05' in o13 and
           not S.made('w146_05', str(R13)))
# link 1b (item 316 (b)-(d)): the skip only on positive evidence and only on the V key attempt:<outcome>
NE = [PRE] + [ft(i, 20000, 5) for i in range(1, 50)]
HD = 'w146_05: its V v146_05 outcome NOT_ENTERED key '
NOEV = ' - no positive evidence (item 316 (b))'
EMPTY = _h.sha256(b'').hexdigest()
o1b = []


def sk(root):
    rc, o = run6(['--skip-w', 'w146_05'], root)
    o1b.append(o)
    return rc, o.rstrip('\n')


def tline(root, sh):
    with open(Path(root) / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
        f.write('2026-10-02T00:00:01Z go146a v146_05 enter_scene end rc 0 log_v146_05.txt sha256 %s\n' % sh)


r = Path(mk146(BASE / 'F13b', 'v146_05', lines=NE))
(r / 'log_v146_05.txt').unlink()
rcx, ox = sk(r)
ok &= case('F13b no log of the V (log reading, RC1 case A) -> rc 1 RUN, the key named, no positive evidence',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); no log_v146_05.txt' + NOEV)
r = Path(mk146(BASE / 'F13c', 'v146_05', lines=NE))
run6(['--tag', 'v146_05'], r)
(r / 'log_v146_05.txt').unlink()
rcx, ox = sk(r)
ok &= case('F13c no log of the V after its score.json (json reading: the json log sha = times.txt) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (json); no log_v146_05.txt' + NOEV)
r = Path(mk146(BASE / 'F13d', 'v146_05', lines=NE))
(r / 'log_v146_05.txt').write_bytes(b'')
rcx, ox = sk(r)
ok &= case('F13d the V log is 0 bytes, times.txt names the sha of the log written (RC1 case B) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
tline(r, EMPTY)
rcx, ox = sk(r)
ok &= case('F13e the V log is 0 bytes and the last times.txt line names the sha of 0 bytes (the sha alone would pass) -> rc 1 '
           'RUN by the size member',
           S.times_log_sha(str(r), 'v146_05') == EMPTY and
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
r = Path(mk146(BASE / 'F13f', 'v146_05', lines=NE))
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
tline(r, 'cd' * 32)
rcx, ox = sk(r)
ok &= case('F13f the V log sha != the last enter_scene end line of times.txt (log reading) -> rc 1 RUN, both sha named',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt sha256 %s != the enter_scene '
           'end line of step2/times.txt cdcdcdcdcdcdcdcd' % lf[:16] + NOEV)
r = Path(mk146(BASE / 'F13g', 'v146_05', lines=NE))
ts = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
run6(['--tag', 'v146_05'], r)
with open(r / 'log_v146_05.txt', 'ab') as f:
    f.write(b'tail written after the score\n')
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
rcx, ox = sk(r)
ok &= case('F13g the V log changed after its score.json (json reading taken: the json log sha = times.txt; the file now '
           'differs) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (json); log_v146_05.txt sha256 %s != the enter_scene end line of '
           'step2/times.txt %s' % (lf[:16], ts[:16]) + NOEV)
r = Path(mk146(BASE / 'F13h', 'v146_05', lines=NE))
(r / 'step2' / 'times.txt').unlink()
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
rcx, ox = sk(r)
ok &= case('F13h no step2/times.txt (no enter_scene end line) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt sha256 %s != the enter_scene '
           'end line of step2/times.txt none' % lf[:16] + NOEV)
r = Path(mk146(BASE / 'F13i', 'v146_05', lines=NE, js=js146('v146_05', attempt=dict(outcome='no_stable'))))
lb = (r / 'log_v146_05.txt').read_bytes()
rcx, ox = sk(r)
ok &= case('F13i another attempt outcome, no marker, the log = times.txt -> rc 0 SKIPPED with the key attempt:no_stable',
           rcx == 0 and ox == 'SKIPPED_V_NOT_ENTERED ' + HD + 'attempt:no_stable (log (no score.json)); log_v146_05.txt %d '
           'bytes sha256 %s = the enter_scene end line of step2/times.txt, no entry line (item 309 (k)(1), 316 (b)-(d))' % (
               len(lb), _h.sha256(lb).hexdigest()[:16]))
VREP = ['--- Build ---', 'v0.0.0 label', '--- Error ---', '[Vulkan][E][1]: Validation Error: [ VUID-x ] bad', ' in x.cpp:1']
MK = (('k1err', NE + ['--- Error ---'], (), 'K1'), ('k1av', NE + ['Unhandled exception: 0xc0000005'], (), 'K1'),
      ('k1fatal', NE + ['--- Fatal Error ---'], (), 'K1'), ('k2hang', NE + ['GpuHangAbort: requested=6000'], (), 'K2'),
      ('k2lost', NE + ['[Vulkan] ErrorDeviceLost'], (), 'K2'), ('k2std', NE, ('vkQueueSubmit failed: ErrorDeviceLost',), 'K2'),
      ('vstop', NE + VREP, (), 'VALIDATION_STOP'))
res = []
for nm, lines, std, cls in MK:
    r = Path(mk146(BASE / ('F13j_' + nm), 'v146_05', lines=lines, std=std))
    e = S.entry_of('v146_05', str(r), SH6)
    rcx, ox = sk(r)
    run6(['--tag', 'v146_05'], r)
    rcy, oy = sk(r)
    res.append((nm, e['outcome'] == 'NOT_ENTERED' and e['marks'][0]['cls'] == cls and not e['key'].startswith('attempt:') and
                rcx == 1 and ox == 'RUN ' + HD + '%s (log (no score.json)); a death marker before the entry line - the W runs '
                '(item 316 (c))' % e['key'] and
                rcy == 1 and oy == 'RUN ' + HD + '%s (json); a death marker before the entry line - the W runs (item 316 (c))'
                % e['key']))
ok &= case('F13j (item 316 (c), RC2) a V NOT_ENTERED whose key is a death marker - K1 (--- Error ---, access violation, '
           '--- Fatal Error ---), K2 (GpuHangAbort:, ErrorDeviceLost in the log and in the emulator stdout), VALIDATION_STOP '
           '- with the log = times.txt -> rc 1 RUN with the key, from the log and from score.json: %s' % (
               ', '.join(nm for nm, x in res if not x) or 'all'), all(x for _, x in res) and len(res) == 7)
SRC145 = Path('C:/kyty/s145/v145_02.json')
jx = json.loads(SRC145.read_text(encoding='utf-8')) if SRC145.is_file() else js146('v146_05')
r = BASE / 'F13k'
r.mkdir(parents=True)
(r / 'v146_05.json').write_text(json.dumps(jx), encoding='utf-8')
rcx, ox = sk(r)
(r / 'log_v146_05.txt').write_bytes(b'')
rcy, oy = sk(r)
kx = 'attempt:%s' % jx['attempts'][0].get('outcome')
ok &= case('F13k the experiment rt146_skipfx of the Red Team on a synthetic root (only the V json, a copy of the real '
           'C:/kyty/s145/v145_02.json; no times.txt, no score.json): case A no log, case B a log of 0 bytes -> rc 1 RUN both',
           rcx == 1 and ox == 'RUN ' + HD + kx + ' (log (no score.json)); no log_v146_05.txt' + NOEV and
           rcy == 1 and oy == 'RUN ' + HD + kx + ' (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
# the stop-check source (item 309 (k)(2)): json when its log sha = times.txt, else the log
R15 = BASE / 'F15'
mk146(R15, 'w146_00')
run6(['--tag', 'w146_00'], R15)
rc15, out15 = run6(['--stop-check', 'r146_01'], R15)
sj = json.load(open(R15 / 'runs146' / 'w146_00.score.json', encoding='utf-8'))
sj['log_sha'] = 'cd' * 32
json.dump(sj, open(R15 / 'runs146' / 'w146_00.score.json', 'w', encoding='utf-8'))
rc15b, out15b = run6(['--stop-check', 'r146_01'], R15)
(R15 / 'runs146' / 'w146_00.score.json').write_text('{broken')
rc15c, out15c = run6(['--stop-check', 'r146_01'], R15)
(R15 / 'runs146' / 'w146_00.score.json').unlink()
rc15d, out15d = run6(['--stop-check', 'r146_01'], R15)
st = lambda o: [x for x in o.split('\n') if x.startswith('STOP RULE')]
ok &= case('F15 the stop-check reads the control from score.json when its log sha = times.txt (source "json"); a json with '
           'another log sha, a broken json, no json -> the log (source named); the decision lines are the same in all four',
           rc15 == rc15b == rc15c == rc15d == 0 and
           'STOP CHECK SOURCES before r146_01 (item 309 (k)(2)): w146_00 json' in out15 and
           'w146_00 log (score.json log sha cdcdcdcdcdcdcdcd != times.txt ' in out15b and
           'w146_00 log (score.json broken)' in out15c and 'w146_00 log (no score.json)' in out15d and
           st(out15) == st(out15b) == st(out15c) == st(out15d) and len(st(out15)) == 4)
# the three-V rule over every made V of SEQ (re-check, second hold, census) with one key
R16 = BASE / 'F16'
mk146(R16, 'w146_00')
NOENT = [PRE] + [ft(i, 20000, 5) for i in range(1, 50)]
for t in ('r146_01', 'r146_02', 'r146_03'):
    mk146(R16, t, lines=NOENT)
rc16, out16 = run6(['--stop-check', 'r146_04'], R16)
mk146(R16, 'r146_04')
rc16b, out16b = run6(['--stop-check', 'v146_05'], R16)
ok &= case('F16 three V in a row NOT_ENTERED with one key (the three re-check V) -> STOP rc 5 before r146_04; one entered V after '
           'them breaks the run -> rc 0 before v146_05',
           rc16 == 5 and 'STOP RULE before r146_04: STOP r146_01,r146_02,r146_03' in out16 and rc16b == 0 and
           'STOP RULE before v146_05: not met' in out16b)
# RECHECK words and the B40 line
R17 = BASE / 'F17'
mk146(R17, 'w146_00')
mk146(R17, 'r146_01')
mk146(R17, 'r146_02', lines=[PRE] + scene_lines('sponge_dirty_bath', v_post()[:1000] + [1000000] + v_post()[1001:]))
mk146(R17, 'r146_03', glitch=(3200, 1))
mk146(R17, 'r146_04', lines=[PRE] + scene_lines('bonus_path_maker_mix', v_post()[:1000] + [4624510] + v_post()[1001:]))
o17v = S.summary(str(R17), SH6, 'viewed')[0]
o17n = S.summary(str(R17), SH6, None)[0]
o17x = S.summary(str(R17), SH6, 'not-viewed')[0]
o17t = S.summary(str(R17), SH6, 'viewed', ['r146_02'])[0]
rl = lambda o, lv: [x for x in o if x.startswith('RECHECK %s ' % lv)]
ok &= case('F17 RECHECK: every V row of item 221 (g)(3) and the sheet viewed -> PASSES; sheet unset -> PENDING_SHEET; not-viewed '
           '-> REMOVES SCENE_OK; a frame dt 1 s on the hold -> REMOVES; one glitch -> REMOVES; --sheet-tags limits the sheet '
           'row to the named V',
           rl(o17v, 'hoover_beach')[0].endswith(': PASSES') and rl(o17n, 'hoover_beach')[0].endswith(': PENDING_SHEET') and
           rl(o17x, 'hoover_beach')[0].endswith(': REMOVES SCENE_OK') and
           rl(o17v, 'sponge_dirty_bath')[0].endswith(': REMOVES SCENE_OK') and
           rl(o17v, 'timestop_casino')[0].endswith(': REMOVES SCENE_OK') and
           rl(o17t, 'hoover_beach')[0].endswith(': PENDING_SHEET') and
           not any(x.startswith('RECHECK bonus_path_maker_mix') for x in o17v))
R17b = BASE / 'F17b'
mk146(R17b, 'r146_01', sheet=False)
o17b = S.summary(str(R17b), SH6, 'viewed')[0]
R17c = BASE / 'F17c'
mk146(R17c, 'r146_01')
with open(R17c / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
    f.write('2026-10-02T00:00:01Z go146a r146_01 enter_scene end rc 0 log_r146_01.txt sha256 %s\n' % ('ef' * 32))
o17c = S.summary(str(R17c), SH6, 'viewed')[0]
ok &= case('F17b RECHECK with the sheet viewed but no sheet file -> REMOVES SCENE_OK; with the log sha != the last enter_scene '
           'end line of times.txt -> REMOVES SCENE_OK (the guest-args / json level / log sha row)',
           rl(o17b, 'hoover_beach')[0].endswith(': REMOVES SCENE_OK') and rl(o17c, 'hoover_beach')[0].endswith(': REMOVES SCENE_OK')
           and any(x.startswith('  FAIL V guest args -lvl hoover_beach') for x in o17c))
b40 = [x for x in o17v if x.startswith('B40 SECOND HOLD bonus_path_maker_mix (r146_04;')]
ok &= case('F18 the B40 line of r146_04 names its K2 frame (n, dt 4 624 510) and the first hold v145_14',
           len(b40) == 1 and '4624510' in b40[0] and 'the first hold v145_14 had K2 n 7249' in b40[0])
(R17 / 'score_i146_v.txt').write_text('fs_read tag i146_v\nWARMUP VERDICT i146_v: PASS\n')
o19 = S.summary(str(R17), SH6, None)[0]
sky = [x for x in o19 if x.startswith('SKY GARDEN ON dac02fb9 (item 300 (d)')]
ok &= case('F19 the Sky Garden line reads the WARMUP VERDICT line of score_i146_v.txt and the control W PASS',
           len(sky) == 1 and 'warm-up V i146_v WARMUP VERDICT i146_v: PASS (score_i146_v.txt sha256 ' in sky[0] and
           sky[0].endswith('control W w146_00 PASS'))
R19c = BASE / 'F19c'
mk146(R19c, 'w146_00', lines=wl6(SKY, dual=False))
(R19c / 'score_i146_v.txt').write_text('WARMUP VERDICT i146_v: FAIL (x)\nFS VERDICT i146_v: PASS\n')
o19c = S.summary(str(R19c), SH6, None)[0]
ok &= case('F19c the Sky Garden line: a control W without the DualSrcBlend line -> STOP; the WARMUP VERDICT line (not another '
           'verdict line) is quoted',
           any(x.startswith('SKY GARDEN ON dac02fb9') and x.endswith('control W w146_00 STOP') and
               'warm-up V i146_v WARMUP VERDICT i146_v: FAIL (x)' in x for x in o19c))
o19b = S.summary(str(R16), SH6, None)[0]
ok &= case('F19b without score_i146_v.txt the Sky Garden line says so; the DATA lines name every made tag',
           any(x.startswith('SKY GARDEN ON dac02fb9') and 'no WARMUP VERDICT line' in x for x in o19b) and
           any(x.startswith('DATA stubs (F13; "Unresolved import stub called" log/stdout): w146_00 0/0; r146_01 0/0') for x in
               o19b) and
           'DATA asserts (F14; "ASSERT:" / "user_msg_param" lines, log and stdout): tags with != 0 (a row of the close in '
           'register F): none' in o19b and
           any(x.startswith('DATA DualSrcBlend control per W (supported=1 enabled=1 before the first GuestOut): w146_00 present')
               for x in o19b))
CEN = [x for x in S.summary(str(RF), SH6, None)[0] if x.startswith('CENSUS = ')]
ok &= case('F20 the census header of 146 names v146_05..v146_19 and item 309 (l)(2)-(3); the re-check V are outside it',
           len(CEN) == 1 and CEN[0].startswith('CENSUS = the V tags v146_05..v146_19, COLD first entries of never-entered levels '
                                               'on dac02fb9 (item 309 (l)(2)-(3))'))
REAL = 'C:/kyty/s146/log_i146_v.txt'
if os.path.isfile(REAL):
    sr = S.scan(REAL)
    gp = sr['guestout']
    ok &= case('F21 the real log of the warm-up i146_v (dac02fb9): one DualSrcBlend line 1/1 before the first GuestOut; 0 stub, '
               '0 assert lines (positive control of the reader on the installed binary)',
               len(sr['dual']) == 1 and sr['dual'][0][1] == (1, 1) and gp is not None and sr['dual'][0][0] < gp and
               sr['stubcall'] == 0 and sr['asserts'] == 0)
try:
    ('\n'.join(f11 + S.fmt_entry(e12) + o13 + o17v + o19 + o19b + [out15, out15b, outA, outB, outC] + o1b)).encode('cp1250',
                                                                                                             errors='strict')
    enc6 = True
except UnicodeError:
    enc6 = False
ok &= case('F22 every line new in profile 146 is ASCII (strict cp1250)', enc6)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
