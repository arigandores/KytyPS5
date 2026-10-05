"""Offline fixtures of s15/enter_scene_s15.py (track S, link S15a, HPP-601; ROADMAP "SESSION 122" item 511 (z)(4)-(5)) WITHOUT the
game: the hold of a U arm.  Part 1 - pure: parse_hold_u (the form, MIN > CAP); UHold on synthetic logs and video indexes - the rows
before the entry line, the exact level name, the first scene frame (draws >= 100 after the entry line and before the next start
line), the presented time after it, the anchor "entry" of item 511 (z)(5), the edges 120 000 000 / 119 999 999 us and 3 000 / 2 999
frames, the cap 300 000 000 us, a torn row, an incomplete last line, the poll in steps; UHold = sc_s.locate / the scorer's domain on
the same synthetic logs.  Part 2 - the hold loop of attempt() with a stand-in emulator (python) writing the log and the video index:
the cause "met", "cap", "game ended"; the json fields hold_end / hold_rule; without --hold-u the S9 hold.  Part 3 - the replay of
real S13b logs (when present): UHold rows / entry row / first scene frame / presented time = the scorer sc_s15 (sc_s.locate).
The generated file = mk_enter_s15.py applied to s9/enter_scene_s9.py (byte for byte).  The first output line names this suite and
the target by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s15/test_enter_scene_s15.py [<enter_scene_s15.py under test>]
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'enter_scene_s15.py')
print('suite test_enter_scene_s15.py sha256 %s target enter_scene_s15.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
NL = chr(10)
_spec = importlib.util.spec_from_file_location('enter_s15_under_test', SRC)
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
_s2 = importlib.util.spec_from_file_location('sc15_for_enter', os.path.join(HERE, 'sc_s15.py'))
SC = importlib.util.module_from_spec(_s2)
_s2.loader.exec_module(SC)
A = SC.A
BASE = Path(os.environ.get('FX_ENTER_BASE') or 'C:/kyty/s288/s15/fx_enter_s15')   # a hand mutant runs in its own directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name), flush=True)
    if not cond and os.environ.get('FX_FAST') == '1' and not name.startswith('U15 '):
        sys.exit(1)        # S15a hand mutants (hmut_s15.py): stop at the first failing case; the full suite never sets it
    return bool(cond)


def FT(n, dt, draws=3000):
    return 'FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=%d cpu_main_us=1 cpu_gpu_us=1 cpu_present_us=1' % (n, dt, draws)


def START(level):
    return 'GuestOut: Level has started: %s' % level


def write(p, lines, end=NL):
    Path(p).write_bytes((NL.join(lines) + end).encode('ascii'))
    return Path(p)


def idx(p, n):
    return write(p, ['%d %d %.3f' % (k, k + 1, k / 60.0) for k in range(n)]) if n else write(p, [], end='')


RULE = (120000000, 3000, 300000000)


def uh_of(lines, frames, level='lvl', name='a'):
    lp = write(BASE / ('%s.log' % name), lines)
    ip = idx(BASE / ('%s.idx' % name), frames)
    u = E.UHold(lp, ip, level, RULE)
    u.poll()
    return u


ok = True
# ================================================================================ part 1: pure
ok &= case('E1 parse_hold_u "120:3000:300" -> (120 000 000 us, 3 000, 300 000 000 us); the constants: scene draws 100, wall + 60 s',
           E.parse_hold_u('120:3000:300') == (120000000, 3000, 300000000) and E.SCENE_DRAWS_U == 100 and E.U_WALL_EXTRA_S == 60 and
           E.SCENE_DRAWS_U == A.SCENE_DRAWS)
bad = 0
for txt in ('120:3000', 'a:b:c', '301:3000:300', '120:3000:0', '', None, '120:-1:300'):
    try:
        E.parse_hold_u(txt)
    except SystemExit:
        bad += 1
ok &= case('E2 parse_hold_u refuses 7 of 7 other forms (two fields, letters, MIN > CAP, CAP 0, empty, None, a sign)', bad == 7)
PRE = [FT(1, 10000, 5000), FT(2, 10000, 5000), START('other')]
L1 = PRE + [START('lvl'), FT(3, 900000, 20), FT(4, 40000000, 50), FT(5, 60000000, 3000)] + \
    [FT(6 + k, 30000000) for k in range(4)]
u = uh_of(L1, 3000)
ok &= case('U1 rows before the entry line are not counted; the entry row eg = 2; the first scene frame = the row 4 (n 5, draws 3 000)',
           u.rows == 9 and u.eg == 2 and u.fi == 4 and u.anchor() == 'fi')
ok &= case('U2 presented after the first scene frame = the rows after it only (4 x 30 s = 120 s); after the entry 220.9 s',
           u.shown() == 120000000 and u.after_entry_us == 220900000)
ok &= case('U3 the edge 120 000 000 us and 3 000 frames -> "met"', u.done() == 'met')
u = uh_of(L1, 2999)
ok &= case('U4 120 s and 2 999 frames -> not done (the video holds the arm)', u.done() is None)
L2 = L1[:-1] + [FT(9, 29999999)]
u = uh_of(L2, 5000)
ok &= case('U5 119 999 999 us and 5 000 frames -> not done (the time holds the arm)', u.shown() == 119999999 and u.done() is None)
L3 = L1 + [FT(10, 180000000)]
u = uh_of(L3, 10)
ok &= case('U6 the cap: 300 000 000 us after the first scene frame with 10 frames -> "cap"', u.shown() == 300000000 and
           u.done() == 'cap')
u = uh_of(L3[:-1] + [FT(10, 179999999)], 10)
ok &= case('U7 299 999 999 us with 10 frames -> not done', u.done() is None)
L5 = PRE + [START('lvl'), FT(3, 900000, 20), FT(4, 900000, 50), START('next'), FT(5, 60000000, 3000)] + \
    [FT(6 + k, 30000000) for k in range(2)]
u = uh_of(L5, 3000)
ok &= case('U8 item 511 (z)(5): the next start line before any row with draws >= 100 -> no first scene frame, anchor "entry", the '
           'presented time = every row after the entry line (121.8 s); a later row of 3 000 draws does not set it',
           u.fi is None and u.closed and u.anchor() == 'entry' and u.shown() == 121800000 and u.done() == 'met')
u = uh_of([x for x in L1 if x != START('lvl')], 9999)
ok &= case('U9 no entry line -> no anchor, never done (the S9 hold rules: the wall cap)', u.anchor() is None and u.done() is None)
u = uh_of(PRE + [START('lvl_diorama'), START('lvl ')] + L1[4:], 3000, level='lvl')
ok &= case('U10 the level name is exact: "lvl_diorama" is not "lvl"; "lvl " (trailing blank) is "lvl" (the strip of sc_s)',
           u.eg == 2 and u.closed is False)
L11 = L1[:5] + ['FrameTrace: n=99 lat_us=1 draws=9000', 'FrameTrace-x: n=5 skc_ap_skip=0', 'xFrameTrace: n=7 dt_us=5'] + L1[5:]
u = uh_of(L11, 3000)
ok &= case('U11 a torn row (no dt_us), a FrameTrace-x line and a line not beginning with "FrameTrace: n=" are not rows',
           u.rows == 9 and u.fi == 4 and u.shown() == 120000000)
lp = BASE / 'step.log'
ip = BASE / 'step.idx'
write(lp, L1[:6], end='')
idx(ip, 0)
u = E.UHold(lp, ip, 'lvl', RULE)
r1 = u.poll()
st1 = (u.rows, u.fi)
with open(lp, 'ab') as f:
    f.write((NL + NL.join(L1[6:]) + NL).encode('ascii'))
with open(ip, 'ab') as f:
    f.write(('%s' % NL.join('%d %d 0.0' % (k, k) for k in range(2999))).encode('ascii'))
r2 = u.poll()
v2 = u.video
with open(ip, 'ab') as f:
    f.write((NL + '2999 2999 0.0' + NL).encode('ascii'))
r3 = u.poll()
ok &= case('U12 the poll in steps: an incomplete last log line is not a row until its newline; an incomplete index line is not a '
           'frame; the state after three polls = the one-shot state ("met" at the third)', r1 is None and st1 == (3, None) and
           r2 is None and v2 == 2998 and r3 == 'met' and u.video == 3000 and u.rows == 9 and u.fi == 4)
u = E.UHold(write(BASE / 'nov.log', L1), None, 'lvl', RULE)
ok &= case('U13 no video index (an arm without --rec) -> video 0: the time alone never ends it before the cap', u.poll() is None and
           u.video == 0)
# UHold = sc_s.locate and the scorer's domain on the same synthetic logs
same = True
for lines, lvl in ((L1, 'lvl'), (L5, 'lvl'), (L11, 'lvl'), (PRE + [START('lvl')] + [FT(9 + k, 1000, 99 + k) for k in range(3)], 'lvl')):
    lp = write(BASE / 'loc.log', lines)
    s = A.scan_s(str(lp))
    eg, end, fi = A.locate(s, lvl)
    u = E.UHold(lp, None, lvl, RULE)
    u.poll()
    want = sum(r[1] for r in s['rows'][fi + 1:]) if fi is not None else sum(r[1] for r in s['rows'][eg:])
    same &= (u.rows, u.eg, u.fi, u.shown()) == (len(s['rows']), eg, fi, want)
ok &= case('U14 UHold rows / entry row / first scene frame / presented time = sc_s.scan_s + sc_s.locate (+ the domain of sc_s15) on '
           '4 synthetic logs (fi, (z)(5), torn rows, the threshold 99 / 100)', same)
# the generated file
mk = os.path.join(HERE, 'mk_enter_s15.py')
gen = BASE / 'gen.py'
p = subprocess.run([sys.executable, mk, str(gen)], capture_output=True, text=True, timeout=60)
ok &= case('U15 the target = mk_enter_s15.py applied to s9/enter_scene_s9.py (byte for byte); ASCII only',
           p.returncode == 0 and gen.read_bytes() == Path(SRC).read_bytes() and all(b < 128 for b in Path(SRC).read_bytes()))
# ================================================================================ part 2: the hold loop of attempt()
EMU = BASE / 'emu'
ROOTD = BASE / 'root'
EMU.mkdir()
ROOTD.mkdir()
E.EMU = EMU
E.ROOT = ROOTD
E.close_game = E.kill_game
E.STABLE_FRAMES = 5
E.STABLE_DRAWS = 100
FAKE = BASE / 'fake_emu.py'
FAKE.write_text('''import sys, time, pathlib
emu, idxp, nrows, dt, nidx, live = pathlib.Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6])
with open(emu / '_kyty.txt', 'w', newline='\\n') as f:
    f.write('LevelDocument Loaded: lvl\\nGuestOut: Level has started: lvl\\n')
    for n in range(nrows):
        f.write('FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=3000 cpu_main_us=1 cpu_gpu_us=1\\n' % (n + 1, dt))
if idxp != '-':
    with open(idxp, 'w', newline='\\n') as f:
        for k in range(nidx):
            f.write('%d %d 0.0\\n' % (k, k))
time.sleep(live)
''', encoding='ascii')


def run_attempt(tag, nrows, dt, nidx, live, hold_u='120:3000:300', rec=True):
    opts = types.SimpleNamespace(level='lvl', timeout=60, hold=300 if hold_u else 2, hold_u=hold_u, rec=rec)
    ip = (ROOTD / ('rec_%s.mp4.idx' % tag)).as_posix() if rec else '-'
    args = [sys.executable, str(FAKE), str(EMU), ip, str(nrows), str(dt), str(nidx), str(live)]
    t0 = time.monotonic()
    res = E.attempt('attempt 1', tag, opts, dict(os.environ), args, 1)
    return res, time.monotonic() - t0


res, wall = run_attempt('h1', 1300, 99000, 3000, 30)
he = res.get('hold_end') or {}
ok &= case('H1 the stand-in: 1 300 rows of 99 ms (128.6 s after the first scene frame) and 3 000 index lines -> stable, the hold '
           'ends "met" at once (anchor fi, video 3 000), the attempt ok; the wall < 25 s',
           res['outcome'] == 'ok' and he.get('cause') == 'met' and he.get('anchor') == 'fi' and he.get('video_frames') == 3000
           and he.get('shown_us') == 1299 * 99000 and wall < 25)
res, wall = run_attempt('h2', 3100, 99000, 10, 30)
he = res.get('hold_end') or {}
ok &= case('H2 3 100 rows (306.8 s) and 10 index lines -> "cap" (the video below 3 000; E3-video FAILS later by the letter)',
           res['outcome'] == 'ok' and he.get('cause') == 'cap' and he.get('video_frames') == 10 and wall < 25)
res, wall = run_attempt('h3', 200, 99000, 10, 4)
he = res.get('hold_end') or {}
ok &= case('H3 200 rows (19.7 s) and the stand-in exits after 4 s -> "game ended", hold_exit set (E3-death reads it)',
           res['outcome'] == 'ok' and he.get('cause') == 'game ended' and res.get('hold_exit') is not None and wall < 25)
res, wall = run_attempt('h4', 200, 99000, 10, 30, hold_u=None)
ok &= case('H4 without --hold-u: the S9 hold (2 s), no hold_end', res['outcome'] == 'ok' and 'hold_end' not in res and
           1.5 <= (res.get('hold_s') or 0) <= 10)
E.U_WALL_EXTRA_S = 1
res, wall = run_attempt('h6', 5, 99000, 0, 30, hold_u='1:5:2')
E.U_WALL_EXTRA_S = 60
he = res.get('hold_end') or {}
ok &= case('H6 the wall cap: --hold-u 1:5:2 with the extra 1 s, 5 rows (0.4 s after the first scene frame), no video and a stand-in that '
           'lives 30 s -> the hold ends "wall cap" after 2 + 1 s (not at the end of the stand-in), the game alive',
           res['outcome'] == 'ok' and he.get('cause') == 'wall cap' and 2.5 <= (res.get('hold_s') or 0) <= 6 and
           res.get('hold_exit') is None)
src = Path(SRC).read_text(encoding='ascii')
ok &= case('H5 <tag>.json carries hold_rule (min_shown_s, video_frames, cap_s, wall_extra_s, scene_draws) = sc_s15.HOLD_RULE_U for '
           '--hold-u 120:3000:300; --hold-u needs --hold > 0',
           'hold_rule = dict(min_shown_s=mn // 1000000, video_frames=fr, cap_s=cap // 1000000,' in src and
           'wall_extra_s=U_WALL_EXTRA_S, scene_draws=SCENE_DRAWS_U)' in src and 'hold_rule=hold_rule,' in src and
           "raise SystemExit('--hold-u needs --hold > 0')" in src and
           dict(min_shown_s=120, video_frames=3000, cap_s=300, wall_extra_s=E.U_WALL_EXTRA_S, scene_draws=E.SCENE_DRAWS_U) ==
           SC.HOLD_RULE_U)
# ================================================================================ part 3: real S13b logs (data of the replay)
REAL = [('u_04', 'ps_logo'), ('u_06', 'underwater_aerial_garden'), ('k_02', 'intro_next'), ('u_01', 'title_controller_ship')]
have = [(t, lv) for t, lv in REAL if os.path.isfile('C:/kyty/s288/s13/log_%s.txt' % t)]
same = True
for t, lv in have:
    lp = 'C:/kyty/s288/s13/log_%s.txt' % t
    s = A.scan_s(lp)
    eg, end, fi = A.locate(s, lv)
    u = E.UHold(Path(lp), Path('C:/kyty/s288/s13/rec_%s.mp4.idx' % t), lv, RULE)
    u.poll()
    want = sum(r[1] for r in s['rows'][fi + 1:]) if fi is not None else sum(r[1] for r in s['rows'][eg:])
    print('data %s: rows %d eg %s fi %s anchor %s presented %.3f s video %d -> %s' % (t, u.rows, u.eg, u.fi, u.anchor(),
                                                                                    u.shown() / 1e6, u.video, u.done()))
    same &= (u.rows, u.eg, u.fi, u.shown()) == (len(s['rows']), eg, fi, want)
ok &= case('R1 the replay of %d real S13b logs (u_04 ps_logo (z)(5), u_06, k_02, u_01): UHold = sc_s.locate and the domain' % len(have),
           len(have) == 0 or same)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
