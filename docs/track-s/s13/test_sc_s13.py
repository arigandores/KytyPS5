"""Offline fixtures of sc_s13.py (track S, link S13a, HPP-498; ROADMAP "SESSION 122" item 408 (l), item 229 (e)(1), (3), item 355
(e), item 371 (v), item 410 (g)(6)(iii), item 414 (b), (g)(1), (g)(5)-(7), item 419 (v) Z3, item 428 (v), (g)).
S13a2 (item 428): KYTY_S_PCW=1 named on every arm (absent / 0 / FORCE_MS / KYTY_FIX_* FAIL), every S-pcw: line against the env
of the arm (a line other than the env FAILS, a line = an env of 0 passes that row), the field "entered" and the word
KNOWN_SCENES_ENTERED at every edge (Q1-Q13).
One case per term and per edge of the new code: the inheritance check; the arms of S13b (order, levels, classes, modes, the chain
of the collection sources, holds, video, validation); the environment of every arm kind with the family / strict rows; the plan
lines; the seal line "installed:" (PENDING, named, malformed, repeated) and the edition 11b (S9r2 observation 3); scan_y (the
compatibility and translation cache lines, DualSrcBlend before / after the first GuestOut, [Vulkan][E], the window events);
the export state; the cache protocol rows per mode; admission; whole arms through score_arm (a clean U arm, a skip after the
first scene frame, a held first scene frame, the data rows of item 414 (g)(5)-(7): a line after the entry with frame= below the
first scene frame, a line without frame= counted by the counter -> FAIL (MINOR-7), the edge of the domain with frame= = n + 2
-> FAIL (MINOR-6)); every member of item 229 (e)(1), (3) at its edges (skip rows / lines, held flips, attributed >= 100 ms, the
screen 180.0 / 180.1 s and its lower bound, video 3 000 / 2 999 frames, glitches, the sheet, death markers, the catalogue gates,
not entered); the W members (300 s, [Vulkan][E], the rows of item 295 (b), DualSrcBlend); the S-early distinct events and the
print without "PREP-only" for a series; the words of (e)(1), (e)(3) and KNOWN_SCENES; the order of S13b; the seal; main; ASCII
output in strict cp1250.  Synthetic logs only, no game.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement
is `sys.exit(0 if ok else 1)`.  The first output line names this suite and the scorer under test by sha256; the output ends
with ALL OK.
    python C:/kyty/s288/s13/test_sc_s13.py [<sc_s13 under test>]
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc_s13.py')
print('suite test_sc_s13.py sha256 %s target sc_s13.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc_s13_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BS = chr(92)
NL = chr(10)
INST = 'ab' * 32
SIG = 'KytySC3:1234abcd:robust:ftz:cbank:fixb26:fixb1b:fixf10'
VAR = 'variant_fixb26_fixb1b_fixf10'
EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
BASE = Path('C:/kyty/s288/s13/fx_sc_s13')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
ROOT = str(BASE / 's13')
(BASE / 'pred').mkdir()
PRED = (BASE / 'pred' / '11b_s.md').as_posix()
Path(PRED).write_bytes(('installed: %s %s %s\n' % (INST, SIG, VAR)).encode('ascii'))
PRED_SHA = hashlib.sha256(Path(PRED).read_bytes()).hexdigest()
INSTT = (INST, SIG, VAR)
N_CASES = [0]


def case(name, cond):
    N_CASES[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


# ------------------------------------------------------------------------------------------------ log lines
def FT(n, dt, draws=3000, cg=0):
    return 'FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=%d cpu_main_us=1 cpu_gpu_us=%d cpu_present_us=1' % (
        n, dt, draws, cg)


def FX(n, skip=0, held=0):
    return 'FrameTrace-x: n=%d rec_pack=0 skc_held=0 skc_held_inc=%d skc_ap_skip=%d skc_bad=0 sf_bad=0' % (n, held, skip)


def SKIP(frame, vs=1, ps=2):
    if frame is None:
        return 'AsyncPipelines: skipped draw DrawIndex vs=0x%016x ps=0x%016x total_skipped=1' % (vs, ps)
    return 'AsyncPipelines: skipped draw DrawIndex frame=%d vs=0x%016x ps=0x%016x pending=1 total_skipped=1' % (frame, vs, ps)


def HELDL(n):
    return 'AsyncPipelines: flip %d held' % n


def SH(h, tr, comp, label='VS'):
    return 'AvTrace: shader %s hash=0x%016x translate_us=%d compile_us=%d permutations=1' % (label, h, tr, comp)


def GFX(us, kind='async'):
    if kind == 'async':
        return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 async wait_us=7 pending=0' % us
    return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 precache' % us


def CSL(us):
    return 'AvTrace: pipeline cs cs=1 us=%d total=5 precache' % us


def QUEUED(r, g=1, c=1):
    return ('PipelinePrecache: %d recipes -> %d graphics + %d compute pipelines queued, 0 skipped, 9 sources loaded, complete, '
            '381 ms (scratch: 0 pipelines, max 0 dwords/thread)' % (r, g, c))


def START(level):
    return 'GuestOut: Level has started: %s' % level


PREP_LINES = ['PipelinePrecache: all pipelines created, 400 ms', 'ShaderPreparation: ready completed=100 total=100 skipped=0',
              'ShaderPreparation: startup wait finished in 77 ms presents_other=0 presents_main=0']
TCACHE = 'Shader translation cache: _ShaderCache' + BS + 'PPSA21564' + BS + VAR
COMPAT = 'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:%s::10288:376:216:44:516:125:000010de:00002c59' % SIG
HEAD0 = ['DualSrcBlend: supported=1 enabled=1', TCACHE, 'Vulkan pipeline cache: disabled (KYTY_PIPELINE_CACHE=0)', COMPAT,
         'ShaderSeed: installed (5 shaders)', 'S-pcw: KYTY_S_PCW=1 KYTY_S_PCW_FORCE_MS=0']
HEADER_T = HEAD0 + [QUEUED(100), GFX(300, 'precache'), CSL(300)] + PREP_LINES
HEADER_M = HEAD0 + [QUEUED(100)] + PREP_LINES


def scene(level, post, header=(), pre_entry=(), tail=(), first=None, loading=()):
    """header, boot rows 1-3, start '', rows 4-5, the entry line, loading row 6 (draws 20), the first scene frame 7, then post
    rows 8...; a row is (dt, dict(cg, skip, held, ev, draws))."""
    out = list(header)
    for n in range(1, 4):
        out += [FT(n, 20000, 5), FX(n)]
    out.append(START(''))
    for n in (4, 5):
        out += [FT(n, 20000, 5), FX(n)]
    out.append(START(level))
    out += list(pre_entry)
    lo = dict(loading)
    out += list(lo.get('ev', ()))
    out += [FT(6, 900000, 20), FX(6, lo.get('skip', 0), lo.get('held', 0))]
    n = 7
    for dt, o in [first or (15000, {})] + list(post):
        out += list(o.get('ev', ()))
        if o.get('held', 0) > 0:
            out.append(HELDL(n))
        out.append(FT(n, dt, o.get('draws', 900 if n == 7 else 3000), o.get('cg', 0)))
        out.append(FX(n, o.get('skip', 0), o.get('held', 0)))
        n += 1
    out += list(tail)
    return out


def write(path, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    return str(path)


def env_for(tag, **over):
    spec = S.SPEC[tag]
    e = dict(S.expected_env(spec))
    e.update(KYTY_GATE_FILE='x/gates.req', KYTY_SAMPLE_GATE='x/sample.req')
    if spec['rec']:
        e['KYTY_REC'] = 'C:' + BS + 'kyty' + BS + 's288' + BS + 's13' + BS + 'rec_%s.mp4' % tag
    if spec['val']:
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    for k, v in over.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def js_for(tag, env_over=None, attempt=None, **over):
    spec = S.SPEC[tag]
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=float(spec['hold']), hold_exit=None, ft_tail=300,
             pipeline_cache_off=False, prep_created_s=30.0, prep_ready_s=31.0)
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=INST, guest_args='-lvl %s' % spec['level'], gates='', env=env_for(tag, **(env_over or {})),
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if spec['val'] else 'false'], hold_s=spec['hold'],
              prereg=dict(path=PRED, sha256=PRED_SHA), attempts=[a])
    js.update(over)
    return js


SEEDS_MANI_FX = BASE / 'seeds_manifest.txt'
SEEDS_MANI_FX.write_bytes(b'x 1 y\n')
S.SEEDS_MANI = SEEDS_MANI_FX.as_posix()
SEEDS_FSHA = hashlib.sha256(b'x 1 y\n').hexdigest()


def cj_for(tag, **over):
    spec = S.SPEC[tag]
    d = dict(man_pre_app=dict(sha='11' * 32), man_pre_glc=dict(sha='12' * 32), man_post_app=dict(sha='13' * 32),
             man_post_glc=dict(sha='14' * 32), glc_pre_copy=dict(sha='15' * 32),
             return_app=dict(expected='16' * 32, got='16' * 32), return_glc=dict(expected='17' * 32, got='17' * 32),
             installed_before=dict(sha=INST), installed_after=dict(sha=INST), return_prev=dict(ok='1'),
             man_launch_glc=dict(sha='12' * 32))
    if spec['mode'] == 'cat':
        want = EMPTY if spec['src'] == 'empty' else ('c%d' % (int(spec['src'][2:]) % 10)) * 32
        d['restore_app'] = dict(expected=want, got=want)
        d['app_post_copy'] = dict(sha=('c%d' % ((spec['k'] + 1) % 10)) * 32)
    else:
        d['restore_app'] = dict(expected=EMPTY, got=EMPTY)
        d['seeds'] = dict(sha=SEEDS_FSHA)
    for k, v in over.items():
        if v is None:
            d.pop(k, None)
        else:
            d[k] = v
    return d


def make_arm(tag, lines, root=ROOT, js=None, cj=None, stdout=None, video=True, frames=3000, glitches=0, sheet=True):
    """Write the files of one arm into root and return its score (score_arm with the fixture seal)."""
    r = Path(root)
    write(r / ('log_%s.txt' % tag), lines)
    std = stdout if stdout is not None else (['Cache test mode: prepare-cold (fresh driver namespace 1)'] +
                                             ['Shaders: VS 0x1'] * sum(1 for x in lines if x.startswith('AvTrace: shader ')))
    write(r / ('stdout_%s.txt' % tag), std)
    (r / ('%s.json' % tag)).write_text(json.dumps(js or js_for(tag)), encoding='utf-8')
    (r / 'runs_s').mkdir(parents=True, exist_ok=True)
    (r / 'runs_s' / ('%s.cache.json' % tag)).write_text(json.dumps(cj or cj_for(tag)), encoding='utf-8')
    for f in ('rec_%s.mp4' % tag, 'glitch_%s.txt' % tag, 'sheet_%s.png' % tag):
        if (r / f).exists():
            (r / f).unlink()
    if video:
        (r / ('rec_%s.mp4' % tag)).write_bytes(b'video')
        write(r / ('glitch_%s.txt' % tag), ['rec_%s.mp4: %d frames 960x540' % (tag, frames), 'one-frame glitches: %d' % glitches])
    if sheet:
        (r / ('sheet_%s.png' % tag)).write_bytes(b'png')
    return S.score_arm(tag, root, PRED_SHA, PRED, INSTT)


def post_rows(n=10, dt=16000):
    return [(dt, {}) for _ in range(n)]


def W(name, ms):
    return dict((m[0], m[1]) for m in ms).get(name, 'absent')


ok = True
# ================================================================================ inheritance, arms, environment, plans
try:
    S.load_sc_s9(S.SC_S9_PATH, '0' * 64)
    inh = False
except SystemExit as e:
    inh = 'inheritance is broken' in str(e)
ok &= case('A1 the inherited sc_s9.py is refused when its sha256 is not the pinned one', inh and S.SHA_SC_S9.startswith('db65fdc8'))
ok &= case('A2 sc_s13.py is ASCII only', all(b < 128 for b in Path(SRC).read_bytes()))
ok &= case('B1 39 arms: k_01 .. k_19, u_01 .. u_19, w13 in this order', S.SEQ == ['k_%02d' % i for i in range(1, 20)] +
           ['u_%02d' % i for i in range(1, 20)] + ['w13'] and len(S.LIST13) == 19 == S.N_KNOWN)
ok &= case('B2 the 19 levels = LIST13 of lvl_s13.out.txt in order (first title_controller_ship, 6th Sky Garden, last '
           'enemy_gorilla)', S.LIST13[0] == 'title_controller_ship' and S.LIST13[5] == 'underwater_aerial_garden' and
           S.LIST13[9] == 'bumper_enemy_snowy_canyon' and S.LIST13[18] == 'enemy_gorilla' and len(set(S.LIST13)) == 19)
lvl_out = Path(HERE) / 'lvl_s13.out.txt'
if lvl_out.exists():
    l13 = [x for x in lvl_out.read_text(encoding='ascii').splitlines() if x.startswith('LIST13 ')]
    ok &= case('B3 LIST13 of the scorer = the line LIST13 of lvl_s13.out.txt', len(l13) == 1 and l13[0].split()[1:] ==
               list(S.LIST13))
k1, k2, k19 = S.SPEC['k_01'], S.SPEC['k_02'], S.SPEC['k_19']
ok &= case('B4 k arms: class M, mode cat, hold 180, no video, no validation; k_01 from the empty set, k_02 from k_01, k_19 '
           'from k_18; level K<NN>', k1['cls'] == 'M' and k1['mode'] == 'cat' and k1['hold'] == 180 and not k1['rec'] and
           not k1['val'] and k1['src'] == 'empty' and k2['src'] == 'k_01' and k19['src'] == 'k_18' and
           k19['level'] == 'enemy_gorilla' and k2['level'] == 'intro_next')
u1, u19, w = S.SPEC['u_01'], S.SPEC['u_19'], S.SPEC['w13']
ok &= case('B5 u arms: class T, mode u, hold 120, video, no validation; w13: Sky Garden, class M, mode u, hold 330, '
           'validation, no video', u1['cls'] == 'T' and u1['mode'] == 'u' and u1['hold'] == 120 and u1['rec'] and
           not u1['val'] and u19['level'] == 'enemy_gorilla' and w['level'] == 'underwater_aerial_garden' and
           w['cls'] == 'M' and w['mode'] == 'u' and w['hold'] == 330 and w['val'] and not w['rec'])
ok &= case('B6 constants: HOLD_K 180, HOLD_U 120, HOLD_W 330, HOLD_W_US 300 s, FRAMES_VIDEO 3000, PREP_LIMIT_S 180',
           (S.HOLD_K, S.HOLD_U, S.HOLD_W, S.HOLD_W_US, S.FRAMES_VIDEO, S.PREP_LIMIT_S) ==
           (180, 120, 330, 300000000, 3000, 180))
e = S.expected_env(k1)
ok &= case('C1 environment k: the base + CLOCK_PIN + MARKERS + KYTY_S_PCW=1 (item 428 (v)(1)), no trace, no seed path, no '
           'cache mode', e == dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1',
                                 KYTY_GUEST_ARGS='-lvl title_controller_ship', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0',
                                 KYTY_S_PCW='1'))
e = S.expected_env(u1)
ok &= case('C2 environment u: + AV_TRACE, REGISTER_TRACE, the seed path s13/seeds, prepare-cold',
           e.get('KYTY_AV_TRACE') == '1' and e.get('KYTY_SHADER_REGISTER_TRACE') == '1' and
           e.get('KYTY_SHADER_SEED_PATH') == 'C:/kyty/s288/s13/seeds' and e.get('KYTY_CACHE_MODE') == 'prepare-cold')
e = S.expected_env(w)
ok &= case('C3 environment w13: the seed path and prepare-cold, no trace', e.get('KYTY_SHADER_SEED_PATH') ==
           'C:/kyty/s288/s13/seeds' and e.get('KYTY_CACHE_MODE') == 'prepare-cold' and 'KYTY_AV_TRACE' not in e)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01'))
ok &= case('C4 env rows of a clean u arm: family and strict PASS', fo and so)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_CACHE_MODE=None))
ok &= case('C5 a missing KYTY_CACHE_MODE: the family row FAILS', not fo and 'KYTY_CACHE_MODE' in fd)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_QUEUE_TRACE='0'))
ok &= case('C6 a non-family key differs: family PASS, strict FAILS', fo and not so and 'KYTY_QUEUE_TRACE' in sd)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_REC=None))
ok &= case('C7 a u arm without KYTY_REC: strict FAILS', not so)
(fo, fd), (so, sd) = S.env_rows(k1, env_for('k_01', KYTY_REC='x/rec_k_01.mp4'))
ok &= case('C8 a k arm with KYTY_REC: strict FAILS; without it PASS with no difference named', not so and
           S.env_rows(k1, env_for('k_01'))[1] == (True, '-'))
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_FIX_B42='1'))
ok &= case('C9 a KYTY_FIX_* key in the env: the family row FAILS', not fo)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_S_PCW=None))
ok &= case('C10 no KYTY_S_PCW in the env (item 428 (v)(1)) -> the family row FAILS naming it', not fo and 'KYTY_S_PCW' in fd)
(fo, fd), (so, sd) = S.env_rows(u1, env_for('u_01', KYTY_S_PCW_FORCE_MS='0'))
ok &= case('C11 KYTY_S_PCW_FORCE_MS in the env -> the family row FAILS naming it', not fo and 'KYTY_S_PCW_FORCE_MS' in fd)
ok &= case('C12 every arm (k, u, w13) expects KYTY_S_PCW=1', all(S.expected_env(S.SPEC[t]).get('KYTY_S_PCW') == '1'
                                                             for t in S.SEQ) and S.SPCW_ENV == '1')
ok &= case('D1 plan k_01 / k_02: "s13 <level> M cat 180 empty|k_01 100 600 0 0"',
           S.plan(k1) == 's13 title_controller_ship M cat 180 empty 100 600 0 0' and
           S.plan(k2) == 's13 intro_next M cat 180 k_01 100 600 0 0')
ok &= case('D2 plan u_19 "s13 enemy_gorilla T u 120 - 100 600 1 0"; w13 "s13 underwater_aerial_garden M u 330 - 300 600 0 1"',
           S.plan(u19) == 's13 enemy_gorilla T u 120 - 100 600 1 0' and
           S.plan(w) == 's13 underwater_aerial_garden M u 330 - 300 600 0 1')
# ================================================================================ seal line, editions
sp = BASE / 'pred' / 'x.md'


def inst_of(text):
    sp.write_text(text, encoding='ascii')
    return S.seal_installed(sp.as_posix())


ok &= case('E1 "installed: PENDING" -> (PENDING, None, None)', inst_of('a\ninstalled: PENDING\nb\n') == ('PENDING', None, None))
ok &= case('E2 "installed: <sha> <sig> <variant>" -> the triple', inst_of('installed: %s %s %s\n' % (INST, SIG, VAR)) == INSTT)
ok &= case('E3 malformed: a short sha, a signature not KytySC3:, a variant not variant_, two lines, none, PENDING with more',
           inst_of('installed: %s %s %s\n' % (INST[:63], SIG, VAR)) is None and
           inst_of('installed: %s X:%s %s\n' % (INST, SIG, VAR)) is None and
           inst_of('installed: %s %s v_%s\n' % (INST, SIG, VAR)) is None and
           inst_of('installed: PENDING\ninstalled: PENDING\n') is None and inst_of('nothing\n') is None and
           inst_of('installed: PENDING %s %s\n' % (SIG, VAR)) is None and inst_of('installed: %s %s\n' % (INST, SIG)) is None)
ok &= case('E4 no seal file -> None', S.seal_installed((BASE / 'pred' / 'none.md').as_posix()) is None)
sb, sbb = BASE / 'pred' / 'e09.md', BASE / 'pred' / 'e09b.md'
S.SEAL_BASE, S.SEAL_B = sb.as_posix(), sbb.as_posix()
sb.write_text('seal: %s s13/sc_s13.py\ninstalled: PENDING\ngo_s13 call: x\n' % ('0' * 64), encoding='ascii')
ok &= case('E5 current_seal: 11 while 11b is absent; edition rows empty', S.current_seal() == sb.as_posix() and
           S.edition_rows() == [])
sbb.write_text('seal: %s s13/sc_s13.py\nedition: 11b by item 999\ninstalled: %s %s %s\ngo_s13 call: x\n' % ('0' * 64, INST, SIG, VAR),
               encoding='ascii')
er = S.edition_rows()
ok &= case('E6 the edition 11b exists: current_seal = 11b; the same lines but installed / edition, 11 PENDING, 11b named -> ok',
           S.current_seal() == sbb.as_posix() and len(er) == 2 and all(x[1] for x in er))
sbb.write_text('seal: %s s13/sc_s13.py\ninstalled: %s %s %s\ngo_s13 call: x\nextra\n' % ('0' * 64, INST, SIG, VAR), encoding='ascii')
ok &= case('E7 11b with an extra line -> the line row FAILS', not S.edition_rows()[0][1])
sbb.write_text('go_s13 call: x\nseal: %s s13/sc_s13.py\ninstalled: %s %s %s\n' % ('0' * 64, INST, SIG, VAR), encoding='ascii')
ok &= case('E8 11b with the lines in another order -> FAILS', not S.edition_rows()[0][1])
sbb.write_text('seal: %s s13/sc_s13.py\ninstalled: PENDING\ngo_s13 call: x\n' % ('0' * 64), encoding='ascii')
ok &= case('E9 11b still PENDING -> the installed row FAILS', not S.edition_rows()[1][1])
sb.write_text('seal: %s s13/sc_s13.py\ninstalled: %s %s %s\ngo_s13 call: x\n' % ('0' * 64, INST, SIG, VAR), encoding='ascii')
sbb.write_text('seal: %s s13/sc_s13.py\ninstalled: %s %s %s\ngo_s13 call: x\n' % ('0' * 64, INST, SIG, VAR), encoding='ascii')
ok &= case('E10 11 not PENDING -> the installed row FAILS', not S.edition_rows()[1][1])
sbb.unlink()
sb.unlink()
ok &= case('E11 edition rows with 11b but no 11 -> one failing row', (sbb.write_text('x\n') or True) and
           S.edition_rows() == [('edition 11b: the seal 11 exists', False, sb.as_posix())])
sbb.unlink()
# check_seal on a fixture root
CR = BASE / 'cs'
for name in S.SEALED_NAMES:
    if not name.startswith('C:/'):
        p = CR / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(('stand-in of %s' % name).encode('ascii'))
shutil.copy2(SRC, CR / 's13' / 'sc_s13.py')


def sha_p(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


seal_lines = ['seal: %s %s' % (sha_p(n if n.startswith('C:/') else CR / n), n) for n in S.SEALED_NAMES]
GAMEF = BASE / 'game.exe'
GAMEF.write_bytes(b'installed build')
GSHA = sha_p(GAMEF)
cs = CR / 'pred' / '11_s.md'
cs.parent.mkdir(parents=True, exist_ok=True)
S.SEAL_BASE, S.SEAL_B = cs.as_posix(), (CR / 'pred' / '11b_s.md').as_posix()
cs.write_text(NL.join(seal_lines + ['installed: PENDING']) + NL, encoding='ascii')
good, rows, inst = S.check_seal(cs.as_posix(), CR.as_posix(), (CR / 's13' / 'sc_s13.py').as_posix(), GAMEF.as_posix())
ok &= case('F1 check_seal: every sealed file, this scorer, "installed: PENDING" -> PASS (no binary row while PENDING)', good and
           inst == ('PENDING', None, None) and not any(r[0].startswith('the installed binary now') for r in rows))
cs.write_text(NL.join(seal_lines[1:] + ['installed: PENDING']) + NL, encoding='ascii')
ok &= case('F2 a sealed name without its line -> FAIL', not S.check_seal(cs.as_posix(), CR.as_posix(),
                                                                       (CR / 's13' / 'sc_s13.py').as_posix())[0])
cs.write_text(NL.join(seal_lines) + NL, encoding='ascii')
ok &= case('F3 no line "installed:" -> FAIL (S9r2 observation 3)', not S.check_seal(cs.as_posix(), CR.as_posix(),
                                                                                   (CR / 's13' / 'sc_s13.py').as_posix())[0])
cs.write_text(NL.join(seal_lines + ['installed: PENDING']) + NL, encoding='ascii')
(CR / 'pred' / '11b_s.md').write_text(NL.join(seal_lines + ['installed: %s %s %s' % (GSHA, SIG, VAR)]) + NL, encoding='ascii')
good, rows, inst = S.check_seal(None, CR.as_posix(), (CR / 's13' / 'sc_s13.py').as_posix(), GAMEF.as_posix())
ok &= case('F4 the edition 11b in force: check_seal reads it, its edition rows pass, the installed binary now = its line -> PASS',
           good and inst[0] == GSHA and any(r[0].startswith('the installed binary now') and r[1] for r in rows) and
           any(r[0].startswith('edition 11b') for r in rows))
GAMEF.write_bytes(b'another build')
ok &= case('F5 the installed binary now != the line "installed:" -> FAIL', not S.check_seal(
    None, CR.as_posix(), (CR / 's13' / 'sc_s13.py').as_posix(), GAMEF.as_posix())[0])
GAMEF.write_bytes(b'installed build')
(CR / 's13' / 'sc_s13.py').write_bytes(b'another scorer')
ok &= case('F6 a sealed file changed (this scorer) -> FAIL', not S.check_seal(
    None, CR.as_posix(), (CR / 's13' / 'sc_s13.py').as_posix(), GAMEF.as_posix())[0])
shutil.copy2(SRC, CR / 's13' / 'sc_s13.py')
(BASE / 'other_scorer.py').write_bytes(b'not the sealed scorer')
good, rows, inst = S.check_seal(None, CR.as_posix(), (BASE / 'other_scorer.py').as_posix(), GAMEF.as_posix())
ok &= case('F6b the running scorer is not the sealed s13/sc_s13.py (the sealed files unchanged) -> FAIL on that row only',
           not good and [r[0] for r in rows if not r[1]] == ['this scorer in the seal'])
(CR / 'pred' / '11b_s.md').unlink()
S.SEAL_BASE, S.SEAL_B = (BASE / 'pred' / '11_s.md').as_posix(), PRED
ok &= case('F7 the sealed names cover the harness, the scorer, both suites, the mutants, the export and its suite, the list '
           'and its output, the inherited scorers, the tool, the video detector',
           all(n in S.SEALED_NAMES for n in ('s13/go_s13.sh', 's13/sc_s13.py', 's13/test_sc_s13.py', 's13/test_go_s13.py',
                                             's13/mut_sc_s13.py', 's13/seedexp_s13.py', 's13/test_seedexp_s13.py',
                                             's13/lvl_s13.py', 's13/lvl_s13.out.txt', 's9/sc_s9.py', 'sc_s.py',
                                             'C:/kyty/s142/sc142.py', 'C:/kyty/KytyPS5/tools/shader_seed.py',
                                             'C:/kyty/scripts/s51_vidglitch.py', 's9/enter_scene_s9.py', 'cachex_s.py')))
# ================================================================================ scan_y
sy = BASE / 'sy.txt'
write(sy, ['DualSrcBlend: supported=1 enabled=1', TCACHE, COMPAT, COMPAT.replace('KytySC3', 'Other'), 'GuestOut: x',
           '[Vulkan][E][2] bad', 'x [Vulkan][E] y', 'Window 1 minimized', 'Window 1 restored', 'Window 1 lost keyboard focus',
           'Window 2 minimized', 'x Recovering Vulkan swapchain 1', 'Window 1 shown'])
y = S.scan_y(sy.as_posix())
ok &= case('G1 scan_y: the first compatibility line, the translation cache with "/", DualSrcBlend before GuestOut, 2 [Vulkan][E], '
           'window events by kind, 1 recover', y['compat'] == COMPAT[len('ShaderSeed: compatibility='):] and
           y['tcache'] == '_ShaderCache/PPSA21564/' + VAR and y['dual_before'] and y['vke'] == 2 and
           y['win'] == {'minimized': 2, 'restored': 1, 'lost keyboard focus': 1} and y['recover'] == 1)
write(sy, ['GuestOut: Level has started: ', 'DualSrcBlend: supported=1 enabled=1'])
ok &= case('G2 DualSrcBlend after the first GuestOut line -> dual_before False', not S.scan_y(sy.as_posix())['dual_before'])
write(sy, ['DualSrcBlend: supported=1 enabled=0', 'GuestOut: x'])
ok &= case('G3 "enabled=0" before GuestOut -> dual_before False', not S.scan_y(sy.as_posix())['dual_before'])
# ================================================================================ export state
ER = BASE / 'exp'
(ER / 'seeds' / 'PPSA21564').mkdir(parents=True)
(ER / 'seeds' / 'PPSA21564' / 'a.bin').write_bytes(b'aaa')
live, nlive = S.manifest_sha((ER / 'seeds' / 'PPSA21564').as_posix())
mtext = 'a.bin 3 %s\n' % hashlib.sha256(b'aaa').hexdigest()
(ER / 'seeds_manifest.txt').write_bytes(mtext.encode('ascii'))
msha = hashlib.sha256(mtext.encode('ascii')).hexdigest()
(ER / 'runs_s').mkdir()
(ER / 'runs_s' / 'k_19.cache.json').write_text(json.dumps(dict(app_post_copy=dict(sha='9' * 64))))


def exp_out(lines):
    (ER / 'seedexp_s13.out.txt').write_text(NL.join(lines) + NL, encoding='ascii')
    return S.export_state(ER.as_posix(), (ER / 'seedexp_s13.out.txt').as_posix(), (ER / 'seeds_manifest.txt').as_posix(),
                          (ER / 'seeds').as_posix())


GOODX = ['source arm k_19 app_post_copy %s' % ('9' * 64), 'compatibility.txt: K:1', 'removed duplicates (F17): 0 (same)',
         'SEEDS manifest C:/x/seeds_manifest.txt files 1 sha256 %s (= x)' % msha, 'EXPORT: OK']
good, rows, d = exp_out(GOODX)
ok &= case('H1 export state OK: EXPORT: OK, manifest line = the file = the live catalogue, source = app_post_copy of k_19; '
           'duplicates and compatibility read', good and live == msha and nlive == 1 and d['dup'] == '0' and d['compat'] == 'K:1')
ok &= case('H2 no export output -> NOT OK', not S.export_state(ER.as_posix(), (ER / 'none.txt').as_posix())[0])
ok &= case('H3 the last line is not EXPORT: OK -> NOT OK', not exp_out(GOODX[:-1] + ['EXPORT: CHECK FAILED'])[0])
ok &= case('H4 the manifest line differs from the file -> NOT OK', not exp_out(GOODX[:3] + [
    'SEEDS manifest C:/x files 1 sha256 %s (= x)' % ('8' * 64), 'EXPORT: OK'])[0])
ok &= case('H5 the source of another arm or another sha -> NOT OK', not exp_out(
    ['source arm k_18 app_post_copy %s' % ('9' * 64)] + GOODX[1:])[0] and not exp_out(
    ['source arm k_19 app_post_copy %s' % ('7' * 64)] + GOODX[1:])[0])
(ER / 'seeds' / 'PPSA21564' / 'b.bin').write_bytes(b'b')
ok &= case('H6 the live catalogue changed after the export -> NOT OK', not exp_out(GOODX)[0])
(ER / 'seeds' / 'PPSA21564' / 'b.bin').unlink()
ok &= case('H7 the manifest format "<name> <bytes> <sha256>" sorted (as seedexp)', exp_out(GOODX)[0] and
           S.manifest_sha((ER / 'none').as_posix()) == (None, 0))
# ================================================================================ cache rows and admission
EXAMPLE = {}


def cjs(t):
    return EXAMPLE.get(t)


EXAMPLE['k_01'] = cj_for('k_01')
rows = S.cache_rows(k2, cj_for('k_02', restore_app=dict(expected='c1' * 32, got='c1' * 32)), cjs, INSTT)
ok &= case('I1 k_02: restore = app_post_copy of k_01 -> every row PASS', all(r[1] for r in rows))
rows = S.cache_rows(k2, cj_for('k_02', restore_app=dict(expected=EMPTY, got=EMPTY)), cjs, INSTT)
ok &= case('I2 k_02 restored from the empty set (not the post copy of k_01) -> the restore row FAILS', not rows[0][1])
rows = S.cache_rows(k2, cj_for('k_02', restore_app=dict(expected='c1' * 32, got='99' * 32)), cjs, INSTT)
ok &= case('I2b k_02: expected = the post copy of k_01 but the live set got another sha -> the restore row FAILS', not rows[0][1])
rows = S.cache_rows(k1, cj_for('k_01'), cjs, INSTT)
ok &= case('I3 k_01: restore = the empty set; app_post_copy recorded', all(r[1] for r in rows) and
           any(r[0].startswith('app_post_copy recorded') for r in rows))
rows = S.cache_rows(k1, cj_for('k_01', app_post_copy=None), cjs, INSTT)
ok &= case('I4 k_01 without app_post_copy -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01'), cjs, INSTT)
ok &= case('I5 u_01: the empty set, GLCache as found, the catalogue = seeds_manifest.txt -> PASS', all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', seeds=dict(sha='0' * 64)), cjs, INSTT)
ok &= case('I6 u_01 with another catalogue sha -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', restore_glc=dict(expected='1' * 64, got='1' * 64)), cjs, INSTT)
ok &= case('I7 GLCache restored before a U arm -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', man_launch_glc=dict(sha='0' * 64)), cjs, INSTT)
ok &= case('I8 man_launch_glc != man_pre_glc -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', return_app=dict(expected='1' * 64, got='2' * 64)), cjs, INSTT)
ok &= case('I9 return_app != its copy -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', installed_after=dict(sha='0' * 64)), cjs, INSTT)
ok &= case('I10 installed after != before -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', installed_before=dict(sha='0' * 64), installed_after=dict(sha='0' * 64)), cjs, INSTT)
ok &= case('I11 installed before = after but != the seal line -> FAILS only that row', [r[0] for r in rows if not r[1]] ==
           ['installed binary before the arm = the seal line "installed:" (S9r2 observation 3)'])
rows = S.cache_rows(u1, cj_for('u_01', return_prev=dict(ok='0')), cjs, INSTT)
ok &= case('I12 return_prev not ok -> FAILS', not all(r[1] for r in rows))
rows = S.cache_rows(u1, cj_for('u_01', man_post_glc=None), cjs, INSTT)
ok &= case('I13 a manifest not recorded -> FAILS', not all(r[1] for r in rows))
ok &= case('I14 no cache json -> one failing row', S.cache_rows(u1, None, cjs, INSTT) == [('cache protocol json present', False,
                                                                                          'missing')])
ok &= case('I15 the seal PENDING (inst None) -> the installed row FAILS', not all(r[1] for r in S.cache_rows(
    u1, cj_for('u_01'), cjs, None)))


def adm(tag, js):
    return [r[0] for r in S.admit(S.SPEC[tag], js, PRED_SHA, PRED, cj_for(tag), cjs, INSTT) if not r[1]]


R_BIN = 'arm binary = binary_sha256 of the json = the seal line "installed:" (item 414 (b))'
R_SPCW = 'KYTY_S_PCW=1 named in the env (item 419 (v) Z3, item 428 (v)(2))'
R_FORCE = 'no KYTY_S_PCW_FORCE_MS / KYTY_FIX_* in the env (item 428 (v)(1))'
ok &= case('J1 admission of a clean u arm and a clean w13 -> no failing row', adm('u_01', js_for('u_01')) == [] and
           adm('w13', js_for('w13')) == [] and adm('k_01', js_for('k_01')) == [])
ok &= case('J2 json binary != the seal line -> that row FAILS (item 414 (b))', adm('u_01', js_for('u_01', binary_sha256='0' * 64))
           == [R_BIN])
ok &= case('J3 two attempts -> FAILS', adm('u_01', js_for('u_01', attempts=[{'label': 'attempt 1'}, {'label': 'attempt 2'}])) ==
           ['one attempt (--attempts 1, no warmup)'])
ok &= case('J4 another -lvl -> FAILS', adm('u_01', js_for('u_01', guest_args='-lvl x')) == ['guest args -lvl title_controller_ship'])
ok &= case('J5 KYTY_GAME_PATCH -> its row FAILS', 'no KYTY_GAME_PATCH (item 342 (e))' in adm('u_01', js_for('u_01', env_over=dict(
    KYTY_GAME_PATCH='p.txt'))))
ok &= case('J6 KYTY_S_PCW absent (u_01) / =0 (w13) / empty (k_01) in the env -> the row "KYTY_S_PCW=1 named" FAILS; =1 passes '
           '(J1)', R_SPCW in adm('u_01', js_for('u_01', env_over=dict(KYTY_S_PCW=None))) and
           R_SPCW in adm('w13', js_for('w13', env_over=dict(KYTY_S_PCW='0'))) and
           R_SPCW in adm('k_01', js_for('k_01', env_over=dict(KYTY_S_PCW=''))) and R_SPCW not in adm('u_01', js_for('u_01')))
ok &= case('J6b KYTY_S_PCW_FORCE_MS / KYTY_FIX_B42 in the env -> the force row FAILS; KYTY_FIXED (not the prefix KYTY_FIX_) -> not '
           'that row', R_FORCE in adm('u_01', js_for('u_01', env_over=dict(KYTY_S_PCW_FORCE_MS='0'))) and
           R_FORCE in adm('u_01', js_for('u_01', env_over=dict(KYTY_FIX_B42='1'))) and
           R_FORCE not in adm('u_01', js_for('u_01', env_over=dict(KYTY_FIXED='1'))))
ok &= case('J7 KYTY_GPU_CHECKPOINTS / KYTY_GATE_SCHEDULE / KYTY_GATE_SCHEDULE_ABBA -> their rows FAIL', 'no KYTY_GPU_CHECKPOINTS' in
           adm('u_01', js_for('u_01', env_over=dict(KYTY_GPU_CHECKPOINTS='1'))) and 'no KYTY_GATE_SCHEDULE' in
           adm('u_01', js_for('u_01', env_over=dict(KYTY_GATE_SCHEDULE='x'))) and 'no KYTY_GATE_SCHEDULE' in
           adm('u_01', js_for('u_01', env_over=dict(KYTY_GATE_SCHEDULE_ABBA='1'))))
ok &= case('J8 the video of another tag -> the video row FAILS; a k arm with a video -> "no video" FAILS',
           'video KYTY_REC rec_u_01.mp4' in adm('u_01', js_for('u_01', env_over=dict(KYTY_REC='x/rec_u_02.mp4'))) and
           'no video (KYTY_REC absent)' in adm('k_01', js_for('k_01', env_over=dict(KYTY_REC='x/rec_k_01.mp4'))))
ok &= case('J9 --vulkan-validation true on a u arm / false on w13 -> FAILS', adm('u_01', js_for(
    'u_01', cmdline=['k', '--vulkan-validation', 'true'])) == ['--vulkan-validation false'] and adm('w13', js_for(
    'w13', cmdline=['k', '--vulkan-validation', 'false'])) == ['--vulkan-validation true'])
R_WF = 'W form line "W form: limit=100000000 filter=none" (item 295 (b)(4)), no VK_LAYER_MESSAGE_ID_FILTER'
ok &= case('J10 W form: another limit, a message filter -> the form row FAILS; no VK_LAYER_PATH -> its row FAILS',
           adm('w13', js_for('w13', env_over=dict(VK_LAYER_DUPLICATE_MESSAGE_LIMIT='1000000'))) == [R_WF] and
           adm('w13', js_for('w13', env_over=dict(VK_LAYER_MESSAGE_ID_FILTER='x'))) == [R_WF] and
           adm('w13', js_for('w13', env_over=dict(VK_LAYER_PATH=None))) == ['VK_LAYER_PATH in the W env'])
ok &= case('J11 another hold / gates / prereg sha / a pipeline-cache retry -> exactly that row FAILS',
           adm('u_01', js_for('u_01', hold_s=121)) == ['hold --hold 120'] and
           adm('u_01', js_for('u_01', gates='x')) == ['gates empty (shipped defaults)'] and
           adm('u_01', js_for('u_01', prereg=dict(path=PRED, sha256='0'))) == ['prereg = the seal'] and
           adm('u_01', js_for('u_01', prereg=dict(path=PRED + 'x', sha256=PRED_SHA))) == ['prereg = the seal'] and
           adm('u_01', js_for('u_01', attempt=dict(pipeline_cache_off=True))) == ['no pipeline-cache retry'])
ok &= case('J12 prereg with back slashes of the same path -> PASS', adm('u_01', js_for('u_01', prereg=dict(
    path=PRED.replace('/', BS), sha256=PRED_SHA))) == [])
# ================================================================================ whole arms
UL = 'title_controller_ship'
clean = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T))
ok &= case('K1 a clean U arm: PASS, entered, attribution determined, 0 / 0 / 0 after the first scene frame, data rows 0 / 0',
           clean is not None and clean['fail'] == [] and clean['entered'] and clean['attr_ok'] and
           clean['after'] == dict(skip_rows=0, skip_lines=0, held=0) and clean['pre_dom'] == 0 and clean['nof'] == 0 and
           clean['att100'] == 0)
mu = S.members_u(clean)
ok &= case('K2 the members of the clean arm: all ok, the arm word PASS', all(m[1] is True for m in mu) and S.arm_word(mu) == 'PASS'
           and [m[0] for m in mu] == ['catalogue installed (gates)', 'E1-skip', 'E1-held', 'E1-attr', 'E1-screen', 'E3-video',
                                      'E3-death'])
r = make_arm('u_01', scene(UL, [(16000, dict(skip=1, held=1, ev=[SKIP(8)]))] + post_rows(), header=HEADER_T))
mu = S.members_u(r)
ok &= case('K3 a skipped draw and a held flip on frame 8 (after the first scene frame) -> E1-skip and E1-held FAIL, the arm FAIL',
           r['fail'] == [] and r['after'] == dict(skip_rows=1, skip_lines=1, held=1) and W('E1-skip', mu) is False and
           W('E1-held', mu) is False and S.arm_word(mu) == 'FAIL')
r = make_arm('u_01', scene(UL, [(16000, dict(skip=1, ev=[SKIP(8)]))] + post_rows(), header=HEADER_T))
ok &= case('K3b a skipped draw without a held flip on frame 8: rows with a skip 1, lines 1, held 0 (T-6 broken -> the arm FAILS, '
           'the members undetermined)', r['after'] == dict(skip_rows=1, skip_lines=1, held=0) and
           any(f.startswith('identity: T-6 ') for f in r['fail']) and W('E1-skip', S.members_u(r)) is None)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, first=(15000, dict(skip=1, held=1, ev=[SKIP(9)]))))
mu = S.members_u(r)
ok &= case('K4 the edge: a skipped draw (frame= 9 = n + 2) and a held flip ON the first scene frame -> not after it: E1-skip and '
           'E1-held ok, reading 1 with the first frame = 1 (data), identities PASS', r['fail'] == [] and
           r['after'] == dict(skip_rows=0, skip_lines=0, held=0) and r['held_r1'] == 1 and W('E1-skip', mu) is True and
           W('E1-held', mu) is True)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, loading=dict(skip=1, ev=[SKIP(6)])))
ok &= case('K5 item 414 (g)(5): a skipped-draw line after the entry line with frame= 6 below the first scene frame 7 -> data row 1, '
           'identities PASS, members ok', r['fail'] == [] and r['pre_dom'] == 1 and r['nof'] == 0 and
           S.arm_word(S.members_u(r)) == 'PASS')
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, first=(15000, dict(skip=1, held=1, ev=[SKIP(7)]))))
ok &= case('K5b the edge: frame= 7 = the first scene frame is not below it -> the data row 0', r['fail'] == [] and r['pre_dom'] == 0)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T + [SKIP(1)]))
ok &= case('K5c a skipped-draw line BEFORE the entry line (frame= 1) -> not in the data row "after the entry line" (0), the domain '
           'identities PASS', r['fail'] == [] and r['pre_dom'] == 0)
r = make_arm('u_01', scene(UL, [(16000, dict(skip=1, ev=[SKIP(None)]))] + post_rows(), header=HEADER_T))
ok &= case('K6 MINOR-7: a line without frame= counted by skc_ap_skip in the domain -> the domain T-1 FAILS (the arm FAILS, the '
           'members undetermined), the data row "without frame=" = 1', any(f.startswith('identity: T-1 ') for f in r['fail']) and
           r['nof'] == 1 and S.arm_word(S.members_u(r)) == 'UNDETERMINED')
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, loading=dict(skip=1, ev=[SKIP(8)])))
ok &= case('K7 MINOR-6, the edge of the domain with frame= = n + 2: a line in the group of row 6 counted there (below the domain) '
           'but labelled frame= 8 -> the domain T-1 FAILS (a false FAIL, the safe direction)',
           any(f.startswith('identity: T-1 ') for f in r['fail']))
r = make_arm('u_01', scene(UL, [(16000, dict(skip=1, held=1, ev=[SKIP(8)]))] + post_rows(), header=HEADER_T))
ok &= case('K8 the data rows of item 414 (g)(5)-(7) are printed by fmt_arm', any('frame= below the first scene frame 0' in x and
                                                                                'without frame= 0' in x for x in S.fmt_arm(r)))
r = make_arm('u_01', scene(UL, [(150000, dict(ev=[SH(5, 120000, 0)]))] + post_rows(), header=HEADER_T))
mu = S.members_u(r)
ok &= case('K9 a presented frame of 150 ms with PREP 120 ms (SHADER) -> attributed 1, E1-attr FAILS', r['fail'] == [] and
           r['att100'] == 1 and W('E1-attr', mu) is False)
r = make_arm('u_01', scene(UL, [(99999, dict(ev=[SH(5, 90000, 0)]))] + post_rows(), header=HEADER_T))
ok &= case('K10 the edge 99 999 us -> not >= 100 ms: E1-attr ok', r['att100'] == 0 and W('E1-attr', S.members_u(r)) is True)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=[SH(6, 1, 1)]),
             stdout=['Cache test mode: prepare-cold'])
ok &= case('K11 T-3 broken (an AvTrace shader line without its stdout line) -> attribution undetermined, the arm FAILS, members '
           'undetermined', not r['attr_ok'] and r['fail'] != [] and W('E1-attr', S.members_u(r)) is None)
r = make_arm('u_01', scene(UL, post_rows(), header=[QUEUED(100, 2, 1) if x.startswith('PipelinePrecache: 100 recipes') else x
                                                    for x in HEADER_T]))
ok &= case('K11b T-4 broken (2 precache lines, 3 queued) -> attribution undetermined, the arm FAILS', not r['attr_ok'] and
           any(f.startswith('identity: T-4 ') for f in r['fail']) and W('E1-attr', S.members_u(r)) is None)
r = make_arm('u_01', [x for x in scene(UL, post_rows(), header=HEADER_T) if not x.startswith('ShaderSeed: installed')])
mu = S.members_u(r)
ok &= case('K12 no "ShaderSeed: installed" -> CATALOGUE NOT INSTALLED: undetermined, the arm UNDETERMINED',
           W('catalogue installed (gates)', mu) is None and S.arm_word(mu) == 'UNDETERMINED' and
           mu[0][2].startswith('CATALOGUE NOT INSTALLED'))
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), stdout=['Cache test mode: other'])
ok &= case('K13 no "Cache test mode: prepare-cold" in stdout -> CATALOGUE NOT INSTALLED', not S.gate_word(r)[0])
r = make_arm('u_01', scene('other_level', post_rows(), header=HEADER_T))
ok &= case('K14 not entered (another level) -> E1 members undetermined, the arm UNDETERMINED', not r['entered'] and
           S.arm_word(S.members_u(r)) == 'UNDETERMINED')
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=['Unhandled exception: x']))
ok &= case('K15 a death marker -> E3-death FAILS, the arm FAIL', W('E3-death', S.members_u(r)) is False and
           S.arm_word(S.members_u(r)) == 'FAIL')
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), frames=2999)
ok &= case('K16 a video of 2 999 frames -> E3-video FAILS; 3 000 ok (K1)', W('E3-video', S.members_u(r)) is False)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), glitches=1)
ok &= case('K17 one one-frame glitch -> E3-video FAILS', W('E3-video', S.members_u(r)) is False)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), sheet=False)
ok &= case('K18 no sheet -> E3-video FAILS', W('E3-video', S.members_u(r)) is False)
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), video=False)
ok &= case('K19 no video -> E3-video undetermined', W('E3-video', S.members_u(r)) is None)
make_arm('u_01', scene(UL, post_rows(), header=HEADER_T))
Path(ROOT, 'rec_u_01.mp4').unlink()
r = S.score_arm('u_01', ROOT, PRED_SHA, PRED, INSTT)
ok &= case('K19b a glitch file but no video file -> E3-video undetermined', not r['video'] and r['glitch'] is not None and
           W('E3-video', S.members_u(r)) is None)
for sec_c, sec_r, want, nm in ((180.0, 179.0, True, 'K20 the screen 180.0 s (later of the two) -> ok'),
                               (180.1, 12.0, False, 'K21 the screen 180.1 s -> FAILS'),
                               (12.0, 180.1, False, 'K22 the later line 180.1 s (ready) -> FAILS')):
    r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), js=js_for('u_01', attempt=dict(prep_created_s=sec_c,
                                                                                                  prep_ready_s=sec_r)))
    ok &= case(nm, W('E1-screen', S.members_u(r)) is want)
lines = [x for x in scene(UL, post_rows(), header=HEADER_T) if not x.startswith('ShaderPreparation: ready')]
r = make_arm('u_01', lines + ['ShaderPreparation: progress done=1 total=9 elapsed_ms=181000',
                              'ShaderPreparation: progress done=2 total=9 elapsed_ms=170000'],
             js=js_for('u_01', attempt=dict(prep_ready_s=None)))
ok &= case('K23 no ready line, the maximum progress 181 000 ms (not the last) -> lower bound > 180 s: FAILS',
           W('E1-screen', S.members_u(r)) is False and r['screen'] == (181.0, 'lower bound'))
r = make_arm('u_01', lines + ['ShaderPreparation: progress done=1 total=9 elapsed_ms=179000'],
             js=js_for('u_01', attempt=dict(prep_ready_s=None)))
ok &= case('K24 progress 179 000 ms -> undetermined', W('E1-screen', S.members_u(r)) is None)
r = make_arm('u_01', lines + ['ShaderPreparation: progress done=1 total=9 elapsed_ms=180000'],
             js=js_for('u_01', attempt=dict(prep_ready_s=None)))
ok &= case('K25 progress 180 000 ms -> not above 180: undetermined', W('E1-screen', S.members_u(r)) is None)
r = make_arm('u_01', lines, js=js_for('u_01', attempt=dict(prep_ready_s=None, outcome='timeout')))
ok &= case('K26 no line, the attempt ended by timeout -> the bound is --timeout 600 s: FAILS',
           r['screen'] == (600.0, 'lower bound') and W('E1-screen', S.members_u(r)) is False)
r = make_arm('u_01', lines + ['ShaderPreparation: progress done=1 total=9 elapsed_ms=1000'],
             js=js_for('u_01', attempt=dict(prep_ready_s=None, outcome='timeout')))
ok &= case('K26b progress 1 000 ms and the timeout -> the bound is the larger, 600 s: FAILS', r['screen'] == (600.0, 'lower bound')
           and W('E1-screen', S.members_u(r)) is False)
r = make_arm('u_01', lines, js=js_for('u_01', attempt=dict(prep_ready_s=None)))
ok &= case('K27 neither the lines nor progress nor timeout -> undetermined', r['screen'] == (None, 'none') and
           W('E1-screen', S.members_u(r)) is None)
r = make_arm('u_01', [x.replace('KYTY_S_PCW=1', 'KYTY_S_PCW=0') for x in scene(UL, post_rows(), header=HEADER_T)])
ok &= case('K28 the log line KYTY_S_PCW=0 against the env 1 -> the S-pcw: row FAILS (the log != the env); the E1 members '
           'undetermined, the arm UNDETERMINED',
           any('S-pcw' in f for f in r['fail']) and W('E1-skip', S.members_u(r)) is None and
           S.arm_word(S.members_u(r)) == 'UNDETERMINED')
r = make_arm('u_01', [x for x in scene(UL, post_rows(), header=HEADER_T) if not x.startswith('S-pcw:')])
ok &= case('K29 no knob line -> admission FAILS', any('S-pcw' in f for f in r['fail']))
r = make_arm('u_01', [x.replace('KYTY_S_PCW=1', 'KYTY_S_PCW=0') for x in scene(UL, post_rows(), header=HEADER_T)],
             js=js_for('u_01', env_over=dict(KYTY_S_PCW='0')))
ok &= case('K28b env KYTY_S_PCW=0 and the log line =0: the S-pcw: row PASSES (the log = the env), the env row FAILS (=0)',
           ('admission: ' + R_SPCW) in r['fail'] and not any('S-pcw:' in f for f in r['fail']))
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T), js=js_for('u_01', env_over=dict(KYTY_S_PCW=None)))
ok &= case('K28c no KYTY_S_PCW in the env, the log line =1 -> the env row and the S-pcw: row FAIL',
           ('admission: ' + R_SPCW) in r['fail'] and any('S-pcw:' in f for f in r['fail']))
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T + ['S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0']))
ok &= case('K28d two S-pcw: lines, the second =0 against the env 1 -> the S-pcw: row FAILS (every line)',
           any('S-pcw:' in f for f in r['fail']) and not ('admission: ' + R_SPCW) in r['fail'])
r = make_arm('u_01', [x.replace('KYTY_S_PCW_FORCE_MS=0', 'KYTY_S_PCW_FORCE_MS=15000') for x in
                      scene(UL, post_rows(), header=HEADER_T)])
ok &= case('K28e the log line with KYTY_S_PCW_FORCE_MS=15000 -> the S-pcw: row FAILS', any('S-pcw:' in f for f in r['fail']))
r = make_arm('u_01', [x.replace(SIG, SIG.replace('fixf10', 'fixf11')) for x in scene(UL, post_rows(), header=HEADER_T)])
ok &= case('K30 the compatibility line on another signature -> admission FAILS', any('compatibility' in f for f in r['fail']))
r = make_arm('u_01', [x.replace(VAR, 'variant_fixb26_fixb1b') for x in scene(UL, post_rows(), header=HEADER_T)])
ok &= case('K31 the translation cache of another variant -> admission FAILS', any('translation cache' in f for f in r['fail']))
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=['Window 1 minimized']))
ok &= case('K32 a window minimized -> admission FAILS (item 273 (z)); restored only -> PASS', any('window event' in f for f in r['fail'])
           and make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=['Window 1 restored']))['fail'] == [])
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=['Recovering Vulkan swapchain']))
ok &= case('K33 "Recovering Vulkan swapchain" -> admission FAILS', any('window event' in f for f in r['fail']))
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T, tail=['GamePatch: applied']))
ok &= case('K34 a GamePatch: line -> admission FAILS', any('GamePatch' in f for f in r['fail']))
ok &= case('K35 an arm not made -> None; members "not made" undetermined', S.score_arm('u_02', ROOT, PRED_SHA, PRED, INSTT) is None
           and S.arm_word(S.members_u(None)) == 'UNDETERMINED')
r = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T))
Path(ROOT, 'log_u_01.txt').unlink()
r = S.score_arm('u_01', ROOT, PRED_SHA, PRED, INSTT)
ok &= case('K36 no log -> fail "no log", undetermined', r['fail'] == ['no log'] and S.arm_word(S.members_u(r)) == 'UNDETERMINED')
# S-early: distinct events, the print
e = dict(events=[dict(kind='frame', n=8, cost=500, cost_prep=100, lead=50), dict(kind='series', n=8, cost=900, cost_prep=900,
                                                                                 lead=None),
                 dict(kind='frame', n=12, cost=300, cost_prep=300, lead=400),
                 dict(kind='frame', n=13, cost=300, cost_prep=300, lead=300)], known=3, short=1)
d = S.early_distinct(e)
ok &= case('L1 item 414 (g)(1): a frame event with the n of a series event is one event -> 3 distinct (the series kept), known 2, '
           'lead < cost 0 (lead = cost is not shorter)', len(d['events']) == 3 and
           [x['kind'] for x in d['events']] == ['series', 'frame', 'frame'] and d['known'] == 2 and d['short'] == 0 and
           S.early_distinct(None) is None)
r = make_arm('u_01', scene(UL, [(150000, dict(skip=1, held=1, ev=[SKIP(8), GFX(70000)]))] + post_rows(), header=HEADER_T))
fa = S.fmt_arm(r)
ok &= case('L2 the print: a series event names its cost "async creation us", no "PREP-only" anywhere; the distinct count line',
           any('S-early event series n 8' in x and 'async creation us' in x for x in fa) and not any('PREP-only' in x for x in fa)
           and any('distinct events 1 (item 414 (g)(1))' in x for x in fa))
# ================================================================================ W
WL = 'underwater_aerial_garden'
WH = HEADER_M
wpost = [(100000000, {}), (100000000, {}), (100000000, {})]
w_ok = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] note']), video=False, sheet=False,
                stdout=['Cache test mode: prepare-cold'])
mw = S.members_w(w_ok)
ok &= case('M1 a clean W: admitted, entered, 300 s after the first scene frame, 0 [Vulkan][E], the rows of item 295 (b), '
           'DualSrcBlend before GuestOut -> PASS', w_ok['fail'] == [] and S.arm_word(mw) == 'PASS' and
           w_ok['derive142']['dt_after_first_us'] == 300000000)
r = make_arm('w13', scene(WL, [(100000000, {}), (100000000, {}), (99999999, {})], header=WH, tail=['[Vulkan][W][2] note']),
             video=False, sheet=False, stdout=['Cache test mode: prepare-cold'])
ok &= case('M2 299 999 999 us after the first scene frame -> FAILS', W('W >= 300 s presented after the first scene frame',
                                                                       S.members_w(r)) is False)
r = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][E][2] error']), video=False, sheet=False,
             stdout=['Cache test mode: prepare-cold'])
ok &= case('M3 a [Vulkan][E] line -> FAILS', W('W 0 [Vulkan][E] (log + stdout)', S.members_w(r)) is False)
r = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] x this will be the last time reporting it']),
             video=False, sheet=False, stdout=['Cache test mode: prepare-cold'])
ok &= case('M4 a layer limit line -> the row 295 (b)(1) FAILS', S.arm_word(S.members_w(r)) == 'FAIL')
r = make_arm('w13', scene(WL, wpost, header=WH), video=False, sheet=False, stdout=['Cache test mode: prepare-cold'])
ok &= case('M5 no validation-layer line -> the row 295 (b)(2) FAILS (and (b)(3))', S.arm_word(S.members_w(r)) == 'FAIL')
r = make_arm('w13', scene(WL, wpost[:2] + [(100000000, dict(ev=['[Vulkan][W][2] early']))], header=WH), video=False, sheet=False,
             stdout=['Cache test mode: prepare-cold'])
ok &= case('M6 the last layer line 100 s before the end of the hold -> the row 295 (b)(3) FAILS', S.arm_word(S.members_w(r)) == 'FAIL')
r = make_arm('w13', scene(WL, wpost, header=WH[1:] + ['GuestOut: hello', WH[0]], tail=['[Vulkan][W][2] n']), video=False,
             sheet=False, stdout=['Cache test mode: prepare-cold'])
ok &= case('M7 DualSrcBlend only after the first GuestOut line -> FAILS', W('W "DualSrcBlend: supported=1 enabled=1" before the '
                                                                          'first GuestOut line (item 300 (b)(4))',
                                                                          S.members_w(r)) is False)
r = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] n', 'Unhandled exception: y']), video=False, sheet=False,
             stdout=['Cache test mode: prepare-cold'])
ok &= case('M8 a death marker on W -> FAILS', S.arm_word(S.members_w(r)) == 'FAIL')
r = make_arm('w13', [x for x in scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] n']) if not x.startswith('ShaderSeed: inst')],
             video=False, sheet=False, stdout=['Cache test mode: prepare-cold'])
ok &= case('M9 W without the catalogue installed -> UNDETERMINED, the gate row undetermined', S.arm_word(S.members_w(r)) ==
           'UNDETERMINED' and W('catalogue installed (gates)', S.members_w(r)) is None)
r = make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] n', 'Window 1 minimized']), video=False, sheet=False,
             stdout=['Cache test mode: prepare-cold'])
ok &= case('M12 W with the catalogue installed but an admission row failing (a window minimized) -> the row "W admitted and '
           'entered" undetermined, the arm UNDETERMINED', W('W admitted and entered', S.members_w(r)) is None and
           S.arm_word(S.members_w(r)) == 'UNDETERMINED')
ok &= case('M10 W not made -> UNDETERMINED', S.arm_word(S.members_w(None)) == 'UNDETERMINED')
make_arm('w13', scene(WL, wpost, header=WH, tail=['[Vulkan][W][2] n']), video=False, sheet=False,
         stdout=['Cache test mode: prepare-cold'])
Path(ROOT, 'log_w13.txt').unlink()
r = S.score_arm('w13', ROOT, PRED_SHA, PRED, INSTT)
mw = S.members_w(r)
ok &= case('M11 W without a log -> DualSrcBlend and 300 s undetermined, the arm UNDETERMINED (not FAIL)', S.arm_word(mw) ==
           'UNDETERMINED' and W('W "DualSrcBlend: supported=1 enabled=1" before the first GuestOut line (item 300 (b)(4))', mw) is None)
# ================================================================================ words
UCLEAN = make_arm('u_01', scene(UL, post_rows(), header=HEADER_T))


def get_of(over=None, wr=w_ok):
    over = over or {}

    def get(t):
        if t == 'w13':
            return over.get(t, wr)
        if t in over:
            return over[t]
        if t.startswith('u_'):
            x = copy.deepcopy(UCLEAN)
            x['tag'] = t
            x['level'] = S.SPEC[t]['level']
            return x
        return None
    return get


word, out = S.read_known(get_of())
ok &= case('N1 19 clean U arms and a clean W -> KNOWN_SCENES PASS, (e)(1) PASS 19 of 19, (e)(3) PASS', word == 'PASS' and
           any(x.startswith('(e)(1) alone') and 'PASS; PASS 19 of 19' in x for x in out) and
           any(x.startswith('(e)(3) alone') and ': PASS;' in x for x in out))
bad = copy.deepcopy(UCLEAN)
bad['after']['held'] = 1
word, out = S.read_known(get_of({'u_07': bad}))
ok &= case('N2 one held flip in u_07 -> KNOWN_SCENES FAIL, (e)(1) FAIL, (e)(3) PASS; the member count line', word == 'FAIL' and
           any(x.startswith('(e)(1) alone') and ': FAIL;' in x for x in out) and
           any(x.startswith('(e)(3) alone') and ': PASS;' in x for x in out) and
           any(x == 'member E1-held: ok 18, fails 1, undetermined 0 of 19' for x in out))
word, out = S.read_known(get_of({'u_19': None}))
ok &= case('N3 one U arm not made -> UNDETERMINED', word == 'UNDETERMINED')
bad = copy.deepcopy(UCLEAN)
bad['glitch'] = dict(video_frames=3000, glitches=2)
word, out = S.read_known(get_of({'u_03': bad}))
ok &= case('N4 glitches in u_03 -> KNOWN_SCENES FAIL, (e)(1) PASS, (e)(3) FAIL', word == 'FAIL' and
           any(x.startswith('(e)(1) alone') and ': PASS;' in x for x in out) and
           any(x.startswith('(e)(3) alone') and ': FAIL;' in x for x in out))
bad = copy.deepcopy(w_ok)
bad['vke'] = 1
word, out = S.read_known(get_of({}, bad))
ok &= case('N5 a [Vulkan][E] on W -> KNOWN_SCENES FAIL, (e)(3) FAIL', word == 'FAIL' and
           any(x.startswith('(e)(3) alone') and ': FAIL;' in x for x in out))
word, out = S.read_known(get_of({}, None))
ok &= case('N6 W not made -> UNDETERMINED', word == 'UNDETERMINED')
bad = copy.deepcopy(UCLEAN)
bad['after']['held'] = 1
und = copy.deepcopy(UCLEAN)
und['att100'] = None
word, out = S.read_known(get_of({'u_02': bad, 'u_05': und}))
ok &= case('N7 a FAIL and an UNDETERMINED arm -> FAIL', word == 'FAIL')
ok &= case('N8 sub_word / arm_word', S.sub_word(['PASS', 'UNDETERMINED']) == 'UNDETERMINED' and S.sub_word(['PASS']) == 'PASS'
           and S.arm_word([('a', True, ''), ('b', None, '')]) == 'UNDETERMINED' and
           S.arm_word([('a', False, ''), ('b', None, '')]) == 'FAIL')
r1 = copy.deepcopy(UCLEAN)
r1['after'] = dict(skip_rows=1, skip_lines=0, held=0)
r2 = copy.deepcopy(UCLEAN)
r2['after'] = dict(skip_rows=0, skip_lines=1, held=0)
ok &= case('N9 E1-skip fails on a row with a skip alone and on a skipped-draw line alone', W('E1-skip', S.members_u(r1)) is False
           and W('E1-skip', S.members_u(r2)) is False)
r3 = copy.deepcopy(UCLEAN)
r3['att100'] = None
ok &= case('N10 E1-attr with the attribution undetermined (att100 None) on an admitted arm -> undetermined, not a failure',
           W('E1-attr', S.members_u(r3)) is None and S.arm_word(S.members_u(r3)) == 'UNDETERMINED')
# ================================================================================ entry (item 428 (g), V7)
def rec(**over):
    d = dict(entered=False, window={}, marks=[], ended=False, exited=False)
    d.update(over)
    return d


ok &= case('Q1 entry_state: not made -> void; the entry line -> yes; no log (no window field) -> void; a clean attempt without '
           'the line -> no', S.entry_state(None)[0] == 'void' and S.entry_state(rec(entered=True))[0] == 'yes' and
           S.entry_state(dict(entered=False, marks=[], ended=False, exited=False))[0] == 'void' and
           S.entry_state(rec()) == ('no', 'no entry line in a clean attempt'))
ok &= case('Q2 entry_state without the line: a death marker / hold_exit (ended) / exited / minimized / Recovering -> void; '
           'restored only -> no; the entry line with a death marker -> yes',
           S.entry_state(rec(marks=[dict(kind='crash')]))[0] == 'void' and S.entry_state(rec(ended=True))[0] == 'void' and
           S.entry_state(rec(exited=True))[0] == 'void' and S.entry_state(rec(window={'minimized': 1}))[0] == 'void' and
           S.entry_state(rec(window={'recover': 1}))[0] == 'void' and S.entry_state(rec(window={'restored': 2}))[0] == 'no' and
           S.entry_state(rec(entered=True, marks=[dict(kind='crash')]))[0] == 'yes')
rk = make_arm('k_04', scene('other_level', post_rows(), header=HEADER_M), video=False, sheet=False,
              stdout=['Cache test mode: none'])
ru = make_arm('u_04', scene('other_level', post_rows(), header=HEADER_T))
ok &= case('Q3 whole arms not entering ps_logo (k_04 class M, u_04 class T, clean) -> entry no on both; fmt_arm prints the field',
           S.entry_state(rk)[0] == 'no' and S.entry_state(ru)[0] == 'no' and not rk['entered'] and
           any(x.startswith('  entered (item 428 (g)): no (') for x in S.fmt_arm(ru)) and
           any(x.startswith('  entered (item 428 (g)): yes (') for x in S.fmt_arm(clean)))
UNO = copy.deepcopy(UCLEAN)
UNO['entered'] = False
ne = S.not_enterable(get_of({'k_04': rec(), 'u_04': UNO}))
ok &= case('Q4 not_enterable: ps_logo with k_04 and u_04 both no -> True; the other 18 (k not made) -> False',
           len(ne) == 19 and ne[3][0] == 'ps_logo' and ne[3][3] is True and ne[3][1][0] == 'no' and ne[3][2][0] == 'no' and
           [x[3] for x in ne].count(True) == 1 and ne[0][1][0] == 'void' and ne[0][2][0] == 'yes')


def ent_line(out):
    return [x for x in out if x.startswith('KNOWN_SCENES_ENTERED')]


word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UNO}))
el = ent_line(out)
ok &= case('Q5 ps_logo not entered in k_04 and u_04 (both clean) -> not enterable: KNOWN_SCENES UNDETERMINED (unchanged), '
           'KNOWN_SCENES_ENTERED PASS on 18 of 19, the list names ps_logo, the entry line of u_04 NOT ENTERABLE',
           word == 'UNDETERMINED' and len(el) == 1 and ': PASS - denominator 18 of 19' in el[0] and
           el[0].endswith('not enterable by -lvl: ps_logo') and
           any(x.startswith('entry u_04 ps_logo') and x.endswith('NOT ENTERABLE by -lvl') for x in out) and
           any(x.startswith('entry u_01 ') and x.endswith('in the denominator') for x in out))
word, out = S.read_known(get_of({'k_04': rec(entered=True), 'u_04': UNO}))
ok &= case('Q6 entered in k_04 only -> in the denominator: u_04 UNDETERMINED -> KNOWN_SCENES_ENTERED UNDETERMINED on 19',
           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0] and ent_line(out)[0].endswith('lvl: none'))
word, out = S.read_known(get_of({'k_04': rec(), 'u_04': copy.deepcopy(UCLEAN)}))
ok &= case('Q7 k_04 no but u_04 entered -> in the denominator: PASS on 19', ': PASS - denominator 19 of 19' in ent_line(out)[0])
word, out = S.read_known(get_of({'u_04': UNO}))
ok &= case('Q8 k_04 not made (void) and u_04 no -> in the denominator: UNDETERMINED on 19',
           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0])
UDEAD = copy.deepcopy(UNO)
UDEAD['marks'] = [dict(kind='crash')]
word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UDEAD}))
ok &= case('Q9 u_04 without the line but with a death marker (void) -> in the denominator; its E3-death FAILS -> FAIL on 19',
           ': FAIL - denominator 19 of 19' in ent_line(out)[0])
UWIN = copy.deepcopy(UNO)
UWIN['window'] = {'minimized': 1}
word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UWIN}))
ok &= case('Q10 u_04 without the line but with a window event (void) -> in the denominator: UNDETERMINED on 19',
           ': UNDETERMINED - denominator 19 of 19' in ent_line(out)[0])
bad = copy.deepcopy(w_ok)
bad['vke'] = 1
word, out = S.read_known(get_of({'k_04': rec(), 'u_04': UNO}, bad))
ok &= case('Q11 ps_logo not enterable and a [Vulkan][E] on w13 -> KNOWN_SCENES_ENTERED FAIL on 18',
           ': FAIL - denominator 18 of 19' in ent_line(out)[0])
ok &= case('Q12 entered_word: a denominator 0 with w13 PASS -> UNDETERMINED; an excluded FAIL arm is not counted -> PASS; a FAIL '
           'in the denominator -> FAIL; w13 FAIL / UNDETERMINED -> FAIL / UNDETERMINED',
           S.entered_word([True] * 19, ['UNDETERMINED'] * 19, 'PASS') == ('UNDETERMINED', []) and
           S.entered_word([True] + [False] * 18, ['FAIL'] + ['PASS'] * 18, 'PASS') == ('PASS', ['PASS'] * 18) and
           S.entered_word([False] * 19, ['PASS'] * 18 + ['FAIL'], 'PASS')[0] == 'FAIL' and
           S.entered_word([True] * 19, ['PASS'] * 19, 'FAIL')[0] == 'FAIL' and
           S.entered_word([False] * 19, ['PASS'] * 19, 'UNDETERMINED')[0] == 'UNDETERMINED' and
           S.entered_word([False] * 19, ['PASS'] * 19, 'PASS') == ('PASS', ['PASS'] * 19))
word, out = S.read_known(get_of())
ok &= case('Q13 19 clean U arms and a clean W -> KNOWN_SCENES PASS and KNOWN_SCENES_ENTERED PASS on 19, list none',
           word == 'PASS' and ': PASS - denominator 19 of 19' in ent_line(out)[0] and ent_line(out)[0].endswith('lvl: none'))
# ================================================================================ order
OR = BASE / 'order'
OR.mkdir()


def made_of(tags):
    return lambda t: t in tags


def get_or(over):
    return lambda t: over.get(t)


plain = dict(marks=[], window={})
ok &= case('O1 k_01 first -> allowed; k_02 before k_01 -> rc 1; an unknown tag rc 2; a made tag rc 1',
           S.allowed('k_01', made_of(()), get_or({}), lambda: False)[0] == 0 and
           S.allowed('k_02', made_of(()), get_or({}), lambda: False)[0] == 1 and
           S.allowed('zz', made_of(()), get_or({}), lambda: False)[0] == 2 and
           S.allowed('k_01', made_of(('k_01',)), get_or({}), lambda: False)[0] == 1)
ks = tuple('k_%02d' % i for i in range(1, 20))
ok &= case('O2 u_01 after k_19 with the export OK -> 0; without the export -> rc 6', S.allowed(
    'u_01', made_of(ks), get_or(dict((t, plain) for t in ks)), lambda: True)[0] == 0 and S.allowed(
    'u_01', made_of(ks), get_or(dict((t, plain) for t in ks)), lambda: False)[0] == 6)
dead = dict(marks=[dict(kind='crash')], window={})
ok &= case('O3 a death marker in an earlier arm -> rc 6 (the series stops)', S.allowed(
    'k_03', made_of(('k_01', 'k_02')), get_or({'k_01': dead, 'k_02': plain}), lambda: True)[0] == 6)
ok &= case('O4 a window event (minimized / recover) in an earlier arm -> rc 6', S.allowed(
    'k_02', made_of(('k_01',)), get_or({'k_01': dict(marks=[], window={'minimized': 1})}), lambda: True)[0] == 6 and S.allowed(
    'k_02', made_of(('k_01',)), get_or({'k_01': dict(marks=[], window={'recover': 1})}), lambda: True)[0] == 6 and S.allowed(
    'k_02', made_of(('k_01',)), get_or({'k_01': dict(marks=[], window={'restored': 1})}), lambda: True)[0] == 0)
nocat = dict(marks=[], window={}, prep=dict(seed_installed=0, prepare_cold=1))
cat = dict(marks=[], window={}, prep=dict(seed_installed=1, prepare_cold=1))
ok &= case('O5 u_02 after u_01 with the catalogue not installed -> rc 6; installed -> 0', S.allowed(
    'u_02', made_of(ks + ('u_01',)), get_or(dict([(t, plain) for t in ks] + [('u_01', nocat)])), lambda: True)[0] == 6 and
    S.allowed('u_02', made_of(ks + ('u_01',)), get_or(dict([(t, plain) for t in ks] + [('u_01', cat)])), lambda: True)[0] == 0)
us = tuple('u_%02d' % i for i in range(1, 20))
ok &= case('O6 w13 after u_19 -> 0; before u_19 -> rc 1', S.allowed('w13', made_of(ks + us), get_or(dict(
    [(t, plain) for t in ks] + [(t, cat) for t in us])), lambda: True)[0] == 0 and S.allowed('w13', made_of(ks + us[:-1]), get_or(
        dict([(t, plain) for t in ks] + [(t, cat) for t in us])), lambda: True)[0] == 1)
ok &= case('O6b w13 after u_19 with the catalogue not installed in u_03 -> rc 6', S.allowed('w13', made_of(ks + us), get_or(dict(
    [(t, plain) for t in ks] + [(t, nocat if t == 'u_03' else cat) for t in us])), lambda: True)[0] == 6)
mf = S.made_fn(OR.as_posix())
(OR / 'attempt_k_01.txt').write_text('x')
(OR / 'k_02.json').write_text('{}')
ok &= case('O7 made_fn: an attempt marker or a json counts as made', mf('k_01') and mf('k_02') and not mf('k_03'))
# ================================================================================ main and output
make_arm('u_02', scene('intro_next', post_rows(), header=HEADER_T, tail=['Window 1 minimized']))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc1 = S.main(['--plan', 'u_19'], ROOT, PRED)
    rc2 = S.main(['--plan', 'zz'], ROOT, PRED)
    rc3 = S.main(['--installed'], ROOT, PRED)
    rc4 = S.main(['--seal-path'], ROOT, PRED)
    rc5 = S.main(['--tag', 'u_02'], ROOT, PRED)
    rc5b = S.main(['--tag', 'u_01'], ROOT, PRED)
    rc6 = S.main(['--tag', 'u_09'], ROOT, PRED)
    rc7 = S.main([], ROOT, PRED)
    sp.write_text('installed: bad\n', encoding='ascii')
    rc9 = S.main(['--installed', '--seal', sp.as_posix()], ROOT, PRED)
o = buf.getvalue()
ok &= case('P0 --seal-path prints the seal relative to the root, one line; --installed on a malformed seal -> rc 1',
           os.path.relpath(PRED, S.ROOT).replace(BS, '/') in o.split(NL) and not PRED in o.split(NL) and rc9 == 1 and
           'installed MALFORMED' in o)
ok &= case('P1 main: --plan rc 0 / unknown 2; --installed prints the seal line; --seal-path relative to the root; --tag of a '
           'failing arm rc 1, of a passing arm rc 0, both write the score json; of a not made arm NO_RUN rc 1; usage rc 2',
           rc1 == 0 and rc2 == 2 and rc3 == 0 and ('installed %s %s %s' % (INST, SIG, VAR)) in o and rc4 == 0 and rc5 == 1 and
           rc5b == 0 and 'ARM u_01' in o and 'ARM u_02' in o and (Path(ROOT) / 'runs_s' / 'u_01.score.json').exists() and
           (Path(ROOT) / 'runs_s' / 'u_02.score.json').exists() and rc6 == 1 and 'NO_RUN' in o and rc7 == 2)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc8 = S.main(['--read'], ROOT, PRED)
o2 = buf.getvalue()
ok &= case('P2 --read prints the collection, the export and the known scenes with the word', rc8 == 0 and
           'READ collection arms' in o2 and 'READ export:' in o2 and 'KNOWN_SCENES (item 229 (e)(1) with (3)): UNDETERMINED' in o2
           and 'KNOWN_SCENES_ENTERED (item 428 (g)' in o2 and 'entry u_04 ps_logo' in o2)
ok &= case('P3 the output of main is ASCII', all(ord(c) < 128 for c in o + o2))
try:
    (o + o2).encode('cp1250', 'strict')
    cp = True
except UnicodeError:
    cp = False
ok &= case('P4 the output of --plan, --installed, --seal-path, --tag, --read encodes in strict cp1250 (no process started: '
           'mutlib keeps its workers)', cp and 's13 enemy_gorilla T u 120 - 100 600 1 0' in o)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
