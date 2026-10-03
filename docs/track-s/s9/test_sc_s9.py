"""Offline fixtures of sc_s9.py (track S, link S9, HPP-431; ROADMAP "SESSION 122" item 355 (g)-(zh), (k)).
One case per term and per edge of the new code: the inheritance check; the arms of S10 (order, levels, classes, modes, knobs,
binaries, holds); the environment of every arm kind and the family / strict rows; the plan lines and UNDETERMINED; scan_x
(row count, BvhLoopCapTrip groups, CsPretranslate kinds, GamePatch, the in-game creation lines with and without a us field,
precache excluded) and the stdout form line; the BvhLoopCapTrip column window i-1 .. i; T-4 under KYTY_PIPELINE_PRECACHE=0; the
cold gate letter / variant; the S-early cost with the async creations of i-2 .. i+1; the haze detector of the lead (the ffmpeg
command, the saturation arithmetic, the median of frames >= 300, the threshold 0.75, gap 3, length 5, frame 1 002 in both
readings) with the positive fixture (the cached saturations of C:/kyty/s288/s6/rec_pcw_int.mp4: the series 1 928 - 1 946 after
frame 1 002) and the negative one (rec_pcw_1.mp4: none after frame 1 002) - the caches carry the video sha256 and are made by
sc_s9.py itself (provenance re-checked by --regress); the cache protocol rows per mode (full / integrity / U); admission; whole
arms through score_arm (pi W / R, c5_0 with PRECACHE=0, T2, u); the readings of C5, the repeat of integrity, T2 and U at every
threshold; the order of S10; the seal; main; ASCII output in strict cp1250.  Synthetic logs only, no process is started.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement
is `sys.exit(0 if ok else 1)`.  The first output line names this suite and the scorer under test by sha256; the output ends
with ALL OK.
    python C:/kyty/s288/s9/test_sc_s9.py [<sc_s9 under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc_s9.py')
print('suite test_sc_s9.py sha256 %s target sc_s9.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc_s9_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BIN_S = 'f3b3aa3bef3f0ceadf668d0fc8bd68230ab1e3158d87bbc0b4c66b92a6651ca3'
BIN_U = '4aa62e95f74ecab749e1e096fd8fd54cc6bb27353346bad98cf3df5f77c1ffac'
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'
EMPTY = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
HZ_INT = 'C:/kyty/s288/s9/fx/haze_pcw_int.json'
HZ_ONE = 'C:/kyty/s288/s9/fx/haze_pcw_1.json'
VID_INT = '705cb5fd93be7b23970b0037f5ec6b156cca5ad8ed887b54fda537434763f045'
VID_ONE = '518df1a033bc59626fde738c11e52c09baa8f1906a213ceb072a0259c58363ce'
BASE = Path('C:/kyty/s288/s9/fx_sc_s9')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
ROOT = str(BASE / 's10')
(BASE / 'pred').mkdir()
PRED = (BASE / 'pred' / '05_s.md').as_posix()
Path(PRED).write_bytes(b'seal of S10\n')
PRED_SHA = hashlib.sha256(Path(PRED).read_bytes()).hexdigest()
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
    return 'AsyncPipelines: skipped draw DrawIndex frame=%d vs=0x%016x ps=0x%016x pending=1 total_skipped=1' % (frame, vs, ps)


def HELDL(n):
    return 'AsyncPipelines: flip %d held' % n


def DSAVE(b, us=90000, forced=True):
    return 'Vulkan pipeline cache: saved %d bytes to _PipelineCache/PPSA21564.bin (%d us)%s' % (b, us, ' forced' if forced else '')


def LOADED(b):
    return 'Vulkan pipeline cache: loaded %d bytes from _PipelineCache/PPSA21564.bin' % b


def SH(h, tr, comp, label='VS'):
    return 'AvTrace: shader %s hash=0x%016x translate_us=%d compile_us=%d permutations=1' % (label, h, tr, comp)


def GFX(us, kind='async'):
    if kind == 'async':
        return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 async wait_us=7 pending=0' % us
    if kind == 'precache':
        return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 precache' % us
    return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5' % us


def CSL(us, kind='sync'):
    if kind == 'sync':
        return 'AvTrace: pipeline cs cs=1 us=%d total=5 sync hash=0x0000000000000009' % us
    if kind == 'precache':
        return 'AvTrace: pipeline cs cs=1 us=%d total=5 precache' % us
    return 'AvTrace: pipeline cs cs=1 waited_us=%d hash=0x0000000000000009' % us


def REG(h, us):
    return 'ShaderRegister: hash=%016x type=1 size=2 scratch=0 code=0 header=0 host_us=%d 1=2' % (h, us)


def FIRST(h, us):
    return 'ShaderFirstUse: hash=%016x stage=1 words=2 ud=3 host_us=%d' % (h, us)


def QUEUED(r, g=1, c=1):
    return ('PipelinePrecache: %d recipes -> %d graphics + %d compute pipelines queued, 0 skipped, 9 sources loaded, complete, '
            '381 ms (scratch: 0 pipelines, max 0 dwords/thread)' % (r, g, c))


def START(level):
    return 'GuestOut: Level has started: %s' % level


PREP_LINES = ['PipelinePrecache: all pipelines created, 400 ms', 'ShaderPreparation: ready completed=100 total=100 skipped=0',
              'ShaderPreparation: startup wait finished in 77 ms presents_other=0 presents_main=0']
HEADER_T = [QUEUED(100), GFX(300, 'precache'), CSL(300, 'precache')] + PREP_LINES + [LOADED(90000)]
HEADER_M = [QUEUED(100)] + PREP_LINES + [LOADED(90000)]
HEADER_P0 = [LOADED(90000)]                                    # KYTY_PIPELINE_PRECACHE=0: no precache, no queue


def scene(level, post, header=(), pre_entry=(), tail=(), first=None):
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
    out += [FT(6, 900000, 20), FX(6)]
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


def write_log(path, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    return str(path)


def env_for(tag, form=None, **over):
    spec = S.resolved(S.SPEC[tag], form)
    e = dict(S.expected_env(spec))
    e.update(KYTY_GATE_FILE='x/gates.req', KYTY_SAMPLE_GATE='x/sample.req', KYTY_REC='C:\\kyty\\s288\\s10\\rec_%s.mp4' % tag)
    for k, v in over.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def js_for(tag, form=None, env_over=None, attempt=None, **over):
    spec = S.SPEC[tag]
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=float(spec['hold']), hold_exit=None, ft_tail=300,
             pipeline_cache_off=False, prep_created_s=30.0, prep_ready_s=31.0)
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BIN_U if spec['binkind'] == 'u' else BIN_S, guest_args='-lvl %s' % spec['level'],
              gates='', env=env_for(tag, form, **(env_over or {})), cmdline=['kyty_emulator.exe', '--vulkan-validation', 'false'],
              hold_s=spec['hold'], prereg=dict(path=PRED, sha256=PRED_SHA), attempts=[a])
    js.update(over)
    return js


def cj_for(tag, **over):
    spec = S.SPEC[tag]
    d = dict(man_pre_app=dict(sha='11' * 32), man_pre_glc=dict(sha='12' * 32), man_post_app=dict(sha='13' * 32),
             man_post_glc=dict(sha='14' * 32), glc_pre_copy=dict(sha='15' * 32),
             return_app=dict(expected='16' * 32, got='16' * 32), return_glc=dict(expected='17' * 32, got='17' * 32),
             installed_before=dict(sha=BIN_U), installed_after=dict(sha=BIN_U), return_prev=dict(ok='1'))
    if spec['mode'] == 'integrity':
        d['restore_app'] = dict(expected='aa' * 32, got='aa' * 32)
        d['restore_glc'] = dict(expected='bb' * 32, got='bb' * 32)
        d['man_launch_glc'] = dict(sha='bb' * 32)
    elif spec['mode'] == 'u':
        d['restore_app'] = dict(expected=EMPTY, got=EMPTY)
        d['man_launch_glc'] = dict(sha='12' * 32)
        d['seeds'] = dict(sha=S.SEEDS_SHA)
    else:
        d['restore_app'] = dict(expected=SNAP_APP, got=SNAP_APP)
        d['restore_glc'] = dict(expected=SNAP_DRV, got=SNAP_DRV)
        d['man_launch_glc'] = dict(sha=SNAP_DRV)
    if tag in ('pi_w1', 'pi_w0'):
        d['app_post_copy'] = dict(sha='aa' * 32)
        d['glc_post_copy'] = dict(sha='bb' * 32)
    d.update(over)
    return d


def sat_for(series=(), n=3200, base=0.5, low=0.2):
    s = [base] * n
    for a, b in series:
        for i in range(a, b + 1):
            s[i] = low
    return s


def mkarm(tag, lines, form=None, js=None, stdout_shaders=0, glitch=(3200, 0), cj=None, extra_stdout=(), knob=True,
          video=True, sat=None):
    spec = S.SPEC[tag]
    if spec['group'] in ('pi', 'c5', 't2', 'cs0') and knob and not any(x.startswith('S-pcw:') for x in lines):
        k = ('%s %s' % (spec['pcw'], '15000')) if spec['pcw'] is not None else '0 0'
        lines = ['S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=%s' % tuple(k.split())] + list(lines)
    d = Path(ROOT)
    (d / 'runs_s').mkdir(parents=True, exist_ok=True)
    (d / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js_for(tag, form)), encoding='utf-8')
    write_log(d / ('log_%s.txt' % tag), lines)
    st = ['Shaders: VS %d | PS 0 | CS 0 | GS 0 | LS 0 | HS 0 | TES 0' % (i + 1) for i in range(stdout_shaders)]
    (d / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(list(extra_stdout) + st) + '\n').encode('utf-8'))
    (d / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if glitch is not None:
        (d / ('glitch_%s.txt' % tag)).write_text('C:/x/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                 'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    if video:
        vb = ('fake video %s' % tag).encode('ascii')
        (d / ('rec_%s.mp4' % tag)).write_bytes(vb)
        if spec['group'] == 'pi':
            json.dump(dict(video='x', video_sha256=hashlib.sha256(vb).hexdigest(), crop=S.HAZE_CROP, scale=[S.HAZE_W, S.HAZE_H],
                           sat=sat if sat is not None else sat_for()),
                      open(str(d / 'runs_s' / ('%s.haze.json' % tag)), 'w', encoding='ascii'))
    (d / 'runs_s' / ('%s.cache.json' % tag)).write_text(json.dumps(cj if cj is not None else cj_for(tag)), encoding='utf-8')


def rm_arm(tag):
    for p in Path(ROOT).glob('*%s*' % tag):
        if p.is_file():
            p.unlink()
    for p in (Path(ROOT) / 'runs_s').glob('%s.*' % tag):
        p.unlink()


def arm(tag, form=None):
    return S.score_arm(tag, form, ROOT, PRED_SHA, PRED, None, True)


def getter():
    return S.make_get(ROOT, PRED, True)


def made():
    return S.made_fn(ROOT)


def rows(n, dt=16000):
    return [(dt, {}) for _ in range(n)]


ok = True

# ================================================================================================ 1 inheritance, constants, arms
try:
    S.load_sc_s(S.SC_S_PATH, '00' * 32)
    inh = False
except SystemExit as e:
    inh = 'inheritance is broken' in str(e)
ok &= case('A1 load_sc_s refuses a sc_s.py whose sha256 is not the pinned one', inh)
ok &= case('A2 the inherited sc_s.py is the scorer of seals 03 / 04 (8b0e0aff) and A.B is sc142', S.SC_S_PATH ==
           'C:/kyty/s288/sc_s.py' and S.SHA_SC_S == '8b0e0aff407cc82ad0a98542676764b5a0c8a867266075aa81a92a09316dc5a4'
           and S.B.ENTRY_WIN == 599 and S.A.SHA142.startswith('1ce612cd'))
ok &= case('A3 binaries s = f3b3aa3b, u = 4aa62e95; snapshots d8ca8c8e / 1767ca0a; empty set e3b0c442; catalogue 72605a65',
           S.BIN_S == BIN_S and S.BIN_U == BIN_U and S.SNAP_APP == SNAP_APP and S.SNAP_DRV == SNAP_DRV and S.EMPTY_SHA == EMPTY
           and S.SEEDS_SHA == '72605a65d15470f8e60a8a4d16c3a4b4d34cd557bbe6e8c17c9ba6441892f098'
           and S.SEEDS_PATH == 'C:/kyty/s288/s9/seeds')
ok &= case('A4 constants of item 355: C5 10 / 20 000, screen 180 s, kill 2 of 5, T2 5, holds 330 / 120, W >= 300 s, video 3 000, '
           'stand 15000, gate reading letter', S.C5_MIN == 10 and S.C5_US == 20000 and S.PREP_LIMIT_S == 180 and S.U_KILL == 2
           and S.U_N == 5 and S.T2_NEED == 5 and S.HOLD_W == 330 and S.HOLD_T == 120 and S.HOLD_W_US == 300000000
           and S.FRAMES_VIDEO == 3000 and S.PCW_FORCE_MS == '15000' and S.T2_GATE_READING == 'letter')
ok &= case('A5 the detector constants of item 355 (g): crop 300x60 at (660, 60), 60x12, frames >= 300, 0.75, gap 3, length 5, '
           'after 1 002', S.HAZE_CROP == 'crop=300:60:660:60' and (S.HAZE_W, S.HAZE_H) == (60, 12) and S.HAZE_FROM == 300
           and S.HAZE_FRAC == 0.75 and S.HAZE_GAP == 3 and S.HAZE_LEN == 5 and S.HAZE_AFTER == 1002)
ok &= case('A6 paths: link C:/kyty/s288/s10, seal pred/05_s.md, Sky Garden, L0 shuriken_ninja_castle', S.LINK_DIR ==
           'C:/kyty/s288/s10' and S.PRED_PATH == 'C:/kyty/s288/pred/05_s.md' and S.SKY == 'underwater_aerial_garden'
           and S.L0 == 'shuriken_ninja_castle')
ok &= case('A7 lists of lvl_s9.out.txt: T2 hero_kratos .. symbol_triangle (10), U underwater .. fragile_battle_1 (5)',
           S.T2_LIST == ('hero_kratos', 'hero_drake', 'voxel_challenge_3', 'armadillo_challenge_2', 'fragile_battle_4',
                         'voxel_challenge_4', 'fragile_battle_5', 'voxel_challenge_5', 'miniboss_challenge_genie',
                         'symbol_triangle')
           and S.U_LIST == ('underwater_aerial_garden', 'hoover_beach', 'robot_builder_next', 'interactive_credit_00',
                            'fragile_battle_1'))
ok &= case('A8 the order of S10 (item 355 (k); t2_cs0 right after t2_1, item 355 (d))', S.SEQ == [
    'pi_w1', 'pi_r1', 'pi_w0', 'pi_r0', 'c5_0', 't2_1', 't2_cs0', 't2_2', 't2_3', 't2_4', 't2_5', 't2_6', 't2_7', 't2_8', 't2_9',
    't2_10', 'u_1', 'u_2', 'u_3', 'u_4', 'u_5'])
sp = S.SPEC
ok &= case('A9 pi arms: W M full hold 330, R T integrity from their W hold 120; knobs 1 1 0 0; binary s',
           [sp[t]['cls'] for t in S.PI_ORDER] == ['M', 'T', 'M', 'T'] and [sp[t]['mode'] for t in S.PI_ORDER] ==
           ['full', 'integrity', 'full', 'integrity'] and [sp[t]['pcw'] for t in S.PI_ORDER] == ['1', '1', '0', '0'] and
           [sp[t]['hold'] for t in S.PI_ORDER] == [330, 120, 330, 120] and sp['pi_r1']['src'] == 'pi_w1' and
           sp['pi_r0']['src'] == 'pi_w0' and all(sp[t]['level'] == S.SKY and sp[t]['binkind'] == 's' for t in S.PI_ORDER)
           and S.PI_W == {'pi_r1': 'pi_w1', 'pi_r0': 'pi_w0'})
ok &= case('A10 c5_0: T full on L0, salt and PRECACHE=0, binary s, not a T2 form arm', sp['c5_0']['cls'] == 'T' and
           sp['c5_0']['salt'] and sp['c5_0']['pre0'] and sp['c5_0']['level'] == S.L0 and not sp['c5_0']['t2form'] and
           sp['c5_0']['mode'] == 'full' and sp['c5_0']['binkind'] == 's' and not sp['c5_0']['cs0'])
ok &= case('A11 T2 arms: T full, the level of the list, the form slot, binary s; t2_cs0 on the level of t2_1 with cs0',
           all(sp['t2_%d' % (j + 1)]['level'] == S.T2_LIST[j] and sp['t2_%d' % (j + 1)]['t2form'] and
               sp['t2_%d' % (j + 1)]['cls'] == 'T' and not sp['t2_%d' % (j + 1)]['cs0'] and
               not sp['t2_%d' % (j + 1)]['salt'] for j in range(10)) and sp['t2_cs0']['level'] == 'hero_kratos' and
           sp['t2_cs0']['cs0'] and sp['t2_cs0']['t2form'] and sp['t2_cs0']['group'] == 'cs0')
ok &= case('A12 u arms: T, form U, binary u, the U list in order, no knob, no salt', all(
    sp['u_%d' % (j + 1)]['level'] == S.U_LIST[j] and sp['u_%d' % (j + 1)]['mode'] == 'u' and sp['u_%d' % (j + 1)]['u'] and
    sp['u_%d' % (j + 1)]['binkind'] == 'u' and sp['u_%d' % (j + 1)]['cls'] == 'T' and sp['u_%d' % (j + 1)]['pcw'] is None and
    not sp['u_%d' % (j + 1)]['salt'] for j in range(5)))
r5 = S.resolved(sp['t2_3'], 'c5')
ra = S.resolved(sp['t2_3'], 'app')
rc5 = S.resolved(sp['c5_0'], 'app')
ok &= case('A13 resolved(): T2 form C5 -> salt and PRECACHE=0; APP -> neither; a non-T2 arm keeps its spec, form None',
           r5['salt'] and r5['pre0'] and r5['form'] == 'c5' and not ra['salt'] and not ra['pre0'] and ra['form'] == 'app' and
           rc5['salt'] and rc5['pre0'] and rc5['form'] is None and not sp['t2_3']['salt'])

# ================================================================================================ 2 environment
base_env = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1',
                KYTY_GPU_MARKERS='0')
T_ENV = dict(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
ok &= case('B1 pi_w1 env = base + KYTY_S_PCW=1 + the stand 15000 (M, no trace)', S.expected_env(sp['pi_w1']) == dict(
    base_env, KYTY_GUEST_ARGS='-lvl underwater_aerial_garden', KYTY_S_PCW='1', KYTY_S_PCW_FORCE_MS='15000'))
ok &= case('B2 pi_r0 env = base + T + KYTY_S_PCW=0 + 15000', S.expected_env(sp['pi_r0']) == dict(
    base_env, KYTY_GUEST_ARGS='-lvl underwater_aerial_garden', KYTY_S_PCW='0', KYTY_S_PCW_FORCE_MS='15000', **T_ENV))
ok &= case('B3 c5_0 env = base + T + KYTY_PIPELINE_SALT=c5_0 + KYTY_PIPELINE_PRECACHE=0', S.expected_env(sp['c5_0']) == dict(
    base_env, KYTY_GUEST_ARGS='-lvl shuriken_ninja_castle', KYTY_PIPELINE_SALT='c5_0', KYTY_PIPELINE_PRECACHE='0', **T_ENV))
ok &= case('B4 t2_3 form C5 env: the salt of its tag + PRECACHE=0; form APP: neither', S.expected_env(r5) == dict(
    base_env, KYTY_GUEST_ARGS='-lvl voxel_challenge_3', KYTY_PIPELINE_SALT='t2_3', KYTY_PIPELINE_PRECACHE='0', **T_ENV) and
    S.expected_env(ra) == dict(base_env, KYTY_GUEST_ARGS='-lvl voxel_challenge_3', **T_ENV))
ok &= case('B5 t2_cs0 env: + KYTY_CS_PRETRANSLATE=0 in both forms', S.expected_env(S.resolved(sp['t2_cs0'], 'app')) == dict(
    base_env, KYTY_GUEST_ARGS='-lvl hero_kratos', KYTY_CS_PRETRANSLATE='0', **T_ENV) and
    S.expected_env(S.resolved(sp['t2_cs0'], 'c5'))['KYTY_PIPELINE_SALT'] == 't2_cs0')
ok &= case('B6 u_2 env: + KYTY_SHADER_SEED_PATH=C:/kyty/s288/s9/seeds + KYTY_CACHE_MODE=prepare-cold', S.expected_env(sp['u_2'])
           == dict(base_env, KYTY_GUEST_ARGS='-lvl hoover_beach', KYTY_SHADER_SEED_PATH='C:/kyty/s288/s9/seeds',
                   KYTY_CACHE_MODE='prepare-cold', **T_ENV))
for tag, form, over, wf, ws, label in (
        ('pi_w1', None, {}, True, True, 'pi_w1 as sealed'),
        ('t2_cs0', 'app', dict(KYTY_CS_PRETRANSLATE=None), False, False, 't2_cs0 without KYTY_CS_PRETRANSLATE'),
        ('t2_2', 'app', dict(KYTY_CACHE_MODE='prepare-cold'), False, False, 'a T2 arm with KYTY_CACHE_MODE'),
        ('u_1', None, dict(KYTY_SHADER_SEED_PATH=None), False, False, 'u_1 without the seed path'),
        ('u_1', None, dict(KYTY_SHADER_SEED_PATH='C:/x'), False, False, 'u_1 with another seed path'),
        ('t2_2', 'c5', dict(KYTY_PIPELINE_SALT='t2_1'), False, False, 'a T2 form C5 salt of another tag'),
        ('c5_0', None, dict(KYTY_PIPELINE_PRECACHE=None), False, False, 'c5_0 with the precache'),
        ('pi_r1', None, dict(KYTY_AV_TRACE=None), True, False, 'pi_r1 without KYTY_AV_TRACE: strict row only'),
        ('pi_r1', None, dict(KYTY_REC=None), True, False, 'no KYTY_REC: strict row only'),
        ('pi_w0', None, dict(KYTY_FIX_B1B='1'), False, False, 'KYTY_FIX_B1B on an S10 arm (family KYTY_FIX_)')):
    (fo, _), (so, _) = S.env_rows(S.resolved(sp[tag], form), env_for(tag, form, **over))
    ok &= case('B7 env %s: family %s strict %s' % (label, wf, ws), fo == wf and so == ws)
ok &= case('B8 families are the inherited ones (+ KYTY_CACHE_MODE, KYTY_CS_PRETRANSLATE)', S.FAMILIES == S.A.FAMILIES and
           S.FAMILY_KEYS == ('KYTY_CACHE_MODE', 'KYTY_CS_PRETRANSLATE') and S.in_family('KYTY_SHADER_SEED_PATH') and
           S.in_family('KYTY_CACHE_MODE') and not S.in_family('KYTY_AV_TRACE') and S.PATH_KEYS == S.A.PATH_KEYS)

# ================================================================================================ 3 plan
ok &= case('C1 plan pi_w1 / pi_r1', S.plan(S.resolved(sp['pi_w1'], None)) ==
           's10 underwater_aerial_garden M full 330 0 1 - 300 480 0 0 0 s -' and S.plan(S.resolved(sp['pi_r1'], None)) ==
           's10 underwater_aerial_garden T integrity 120 0 1 pi_w1 300 480 0 0 0 s -')
ok &= case('C2 plan c5_0 / t2_2 C5 / t2_2 APP / t2_cs0 APP / u_1', S.plan(S.resolved(sp['c5_0'], None)) ==
           's10 shuriken_ninja_castle T full 120 1 - - 100 480 1 0 0 s -' and S.plan(S.resolved(sp['t2_2'], 'c5')) ==
           's10 hero_drake T full 120 1 - - 100 480 1 0 0 s c5' and S.plan(S.resolved(sp['t2_2'], 'app')) ==
           's10 hero_drake T full 120 0 - - 100 480 0 0 0 s app' and S.plan(S.resolved(sp['t2_cs0'], 'app')) ==
           's10 hero_kratos T full 120 0 - - 100 480 0 1 0 s app' and S.plan(S.resolved(sp['u_1'], None)) ==
           's10 underwater_aerial_garden T u 120 0 - - 100 600 0 0 1 u -')
ok &= case('C3 a T2 arm without a form -> UNDETERMINED (go_s9.sh rc 6)', S.plan(S.resolved(sp['t2_5'], None)) == 'UNDETERMINED'
           and S.plan(S.resolved(sp['t2_cs0'], None)) == 'UNDETERMINED')

# ================================================================================================ 4 scan_x
xl = [FT(1, 1000), 'BvhLoopCapTrip: trips=+1 total=1', FT(2, 1000), 'FrameTrace: n=3 torn', 'BvhLoopCapTrip: trips=+1 total=2',
      'CsPretranslate: ready hash=1 us=2 kb=1 ready_kb=1', 'CsPretranslate: hit hash=1 saved_us=2 hits=1',
      'CsPretranslate: miss hash=1 reason=x', 'CsPretranslate: enqueue skipped hash=1 reason=y', 'CsPretranslate: skipped hash=1 r',
      'CsPretranslate: summary queued=1 ready=1 failed=0 hits=1 missed=1 evicted=0', 'GamePatch: file x', 'GamePatch: applied',
      GFX(30000, 'async'), GFX(25000, 'none'), CSL(40000, 'sync'), CSL(5, 'waited'), GFX(1, 'precache'), CSL(2, 'precache'),
      FT(3, 1000), 'xBvhLoopCapTrip: no', ' GamePatch: no']
sx = S.scan_x(write_log(BASE / 'logs' / 'x.txt', xl))
ok &= case('D1 scan_x rows = valid FrameTrace rows (a torn row is not a row)', sx['rows'] == 3)
ok &= case('D2 BvhLoopCapTrip: lines with the group index (the number of rows before them); a line not at the start ignored',
           sx['bvh'] == [1, 2])
ok &= case('D3 CsPretranslate: by kind, "enqueue skipped" one kind', sx['csp'] == {'ready': 1, 'hit': 1, 'miss': 1,
                                                                                  'enqueue skipped': 1, 'skipped': 1,
                                                                                  'summary': 1})
ok &= case('D4 GamePatch: lines at the start of a line counted', sx['gamepatch'] == 2)
ok &= case('D5 in-game creations: AvTrace pipeline lines without "precache" - us of async / none / sync kept, a waited line '
           'without a us field counted apart, precache lines excluded', sorted(sx['create']) == [25000, 30000, 40000] and
           sx['create_nous'] == 1)
ss = S.A.scan_s(str(BASE / 'logs' / 'x.txt'))
ok &= case('D6 the scan_x row count equals the inherited scan_s rows on the same log', sx['rows'] == len(ss['rows']))
Path(BASE / 'logs' / 'so.txt').write_bytes(b'Cache test mode: prepare-cold (fresh driver namespace 1)\nCache test mode: cold (x)\n'
                                           b' Cache test mode: prepare-cold\n')
so = S.scan_stdout_x(str(BASE / 'logs' / 'so.txt'))
ok &= case('D7 stdout: "Cache test mode: prepare-cold" counted apart from every "Cache test mode:" line; a missing file absent',
           so['prepare_cold'] == 1 and so['any'] == 2 and so['present'] and
           not S.scan_stdout_x(str(BASE / 'logs' / 'none.txt'))['present'])
ok &= case('D8 BvhLoopCapTrip column: lines in groups i-1 and i of a frame counted, i-2 and i+1 not',
           S.bvh_col(dict(bvh=[3, 4, 5, 6, 6]), [dict(n=50, i=5), dict(n=51, i=8)]) == [(50, 2), (51, 0)] and
           S.bvh_col(dict(bvh=[7]), [dict(n=1, i=8)]) == [(1, 1)])

# ================================================================================================ 5 T-4, gate, early
s_p0 = dict(pipe=[], queued=None)
s_p1 = dict(pipe=[(1, 'gfx', 'precache', 5, 0, None)], queued=None)
s_q = dict(pipe=[(1, 'gfx', 'precache', 5, 0, None), (1, 'cs', 'precache', 5, 0, None)], queued=(10, 1, 1, 0))
ok &= case('E1 T-4 under PRECACHE=0: no queue and 0 precache lines holds; a precache line or a queue breaks it',
           S.ident_t4(s_p0, dict(pre0=True))[0] and not S.ident_t4(s_p1, dict(pre0=True))[0] and
           not S.ident_t4(s_q, dict(pre0=True))[0] and not S.ident_t4(dict(pipe=[], queued=(10, 1, 1, 0)), dict(pre0=True))[0])
ok &= case('E2 T-4 without PRECACHE=0 = the inherited letter: precache lines = G + C queued, no queue -> broken',
           S.ident_t4(s_q, dict(pre0=False))[0] and not S.ident_t4(s_p0, dict(pre0=False))[0] and
           not S.ident_t4(dict(pipe=s_p1['pipe'], queued=(10, 1, 1, 0)), dict(pre0=False))[0])
g_full = dict(attr_ok=True, perm_after=1, rec_new_after=1, skip_after=1)
g_norec = dict(g_full, rec_new_after=0)
ok &= case('E3 gate letter: new permutation AND new recipe AND skipped draw', S.gate9(g_full, dict(pre0=False), 'letter') ==
           (True, 'cold') and S.gate9(g_norec, dict(pre0=True), 'letter') == (False, 'level not cold') and
           S.gate9(dict(g_full, perm_after=0), dict(pre0=False), 'letter')[0] is False and
           S.gate9(dict(g_full, skip_after=0), dict(pre0=False), 'letter')[0] is False)
ok &= case('E4 gate variant: the recipe member dropped only under PRECACHE=0', S.gate9(g_norec, dict(pre0=True), 'variant') ==
           (True, 'cold') and S.gate9(g_norec, dict(pre0=False), 'variant') == (False, 'level not cold') and
           S.gate9(dict(g_norec, skip_after=0), dict(pre0=True), 'variant')[0] is False and
           S.gate9(dict(g_norec, perm_after=0), dict(pre0=True), 'variant')[0] is False)
ok &= case('E5 gate: no gate dict -> undetermined (no scene frame); attribution broken -> undetermined (T-3/T-4); the default '
           'reading is the constant', S.gate9(None, dict(pre0=False)) == (False, 'undetermined (no scene frame)') and
           S.gate9(dict(g_full, attr_ok=False), dict(pre0=False)) == (False, 'undetermined (T-3/T-4)') and
           S.gate9(g_norec, dict(pre0=True)) == (False, 'level not cold'))
# early9: two SHADER frames (rows 10 and 20) and one series; async creations of groups 8..11 count for row 10
s_e = dict(reg=[('aa', 100), ('bb', 100)], first=[(9, 'aa', 50100), (19, 'bb', 40100)],
           sh=[(9, 'VS', 'aa', 1, 1, 0), (19, 'VS', 'bb', 1, 1, 0)], skips=[],
           pipe=[(7, 'gfx', 'async', 1000, 0, None), (8, 'gfx', 'async', 30000, 0, None), (11, 'cs', 'async', 25000, 0, None),
                 (12, 'gfx', 'async', 777, 0, None), (10, 'gfx', 'none', 999, 0, None), (10, 'gfx', 'precache', 5, 0, None)])
fz_e = dict(long=[dict(attr='SHADER', i=10, n=110, prep=20000), dict(attr='not', i=15, n=115, prep=0),
                  dict(attr='SHADER-partly', i=20, n=120, prep=40000)], series=[])
e9 = S.early9(s_e, fz_e, True)
ok &= case('E6 S-early cost of a frame = PREP + async creations of groups i-2 .. i+1 (not i-3, not i+2, not sync / precache)',
           e9 is not None and [x['cost'] for x in e9['events']] == [75000, 40000] and
           [x['cost_prep'] for x in e9['events']] == [20000, 40000])
ok &= case('E7 S-early lead = FirstUse - Register (50 000 / 40 000): short by the letter 1 of 2 (40 000 = cost is not short), '
           'by PREP only 0 of 2', e9['known'] == 2 and e9['short'] == 1 and e9['short_prep'] == 0 and
           [x['lead'] for x in e9['events']] == [50000, 40000])
ok &= case('E8 S-early without attribution -> None', S.early9(s_e, fz_e, False) is None)

# ================================================================================================ 6 haze
ok &= case('H1 the ffmpeg command of the lead detector', S.haze_cmd('v.mp4') == [
    'ffmpeg', '-loglevel', 'error', '-i', 'v.mp4', '-vf', 'crop=300:60:660:60,scale=60:12', '-f', 'rawvideo', '-pix_fmt',
    'rgb24', '-'])
px = bytes([10, 20, 30]) * (60 * 12)
px2 = bytes([0, 0, 0]) * (60 * 12) + bytes([255, 0, 0]) * (60 * 12) + b'\x01\x02'
sat1 = S.haze_sat_bytes(px)
sat2 = S.haze_sat_bytes(px2)
ok &= case('H2 saturation of a frame = mean of (max - min) / (max + 1) over 60x12 pixels; a partial frame dropped',
           len(sat1) == 1 and abs(sat1[0] - 20.0 / 31) < 1e-12 and len(sat2) == 2 and sat2[0] == 0 and
           abs(sat2[1] - 255.0 / 256) < 1e-12)
ok &= case('H3 the median over frames >= 300 (odd and even counts); <= 300 frames -> 0',
           S.haze_med([9.0] * 300 + [1.0, 3.0, 2.0]) == 2.0 and S.haze_med([9.0] * 300 + [1.0, 4.0]) == 2.5 and
           S.haze_med([1.0] * 300) == 0)
s_h = [1.0] * 1200
for i in (400, 401, 402, 403, 404, 405):        # end - start = 5 -> kept
    s_h[i] = 0.74
for i in (500, 501, 502, 503, 504):             # end - start = 4 -> dropped
    s_h[i] = 0.74
for i in (600, 604, 605, 606, 607, 608):        # gap 4 between 600 and 604 -> two runs, the second 4 long -> dropped
    s_h[i] = 0.74
for i in (700, 703, 706):                        # gap 3 merges 700 .. 706 -> kept
    s_h[i] = 0.74
for i in (800, 801, 802, 803, 804, 805):        # exactly 0.75 x median is not low
    s_h[i] = 0.75
for i in (100, 101, 102, 103, 104, 105, 106):   # before frame 300 never low
    s_h[i] = 0.1
med_h, low_h, runs_h = S.haze_runs(s_h)
ok &= case('H4 haze_runs: below 0.75 x median low, gap <= 3 merges, kept when end - start >= 5, frames < 300 ignored',
           med_h == 1.0 and runs_h == [[400, 405], [700, 706]] and low_h == 6 + 5 + 6 + 3)
ok &= case('H5 after frame 1 002: letter = start > 1 002, variant = any frame > 1 002',
           S.haze_after([[300, 1002], [1000, 1010], [1003, 1010]]) == ([[1003, 1010]], [[1000, 1010], [1003, 1010]])
           and S.haze_after([[1002, 1002]]) == ([], []))
hz_int = json.load(open(HZ_INT, encoding='ascii'))
hz_one = json.load(open(HZ_ONE, encoding='ascii'))
mi, li, ri = S.haze_runs(hz_int['sat'])
m1, l1, r1 = S.haze_runs(hz_one['sat'])
ok &= case('H6 POSITIVE: the cached saturations of rec_pcw_int.mp4 (sha 705cb5fd, 3 749 frames): the series 1 928 - 1 946 is the '
           'only one after frame 1 002', hz_int['video_sha256'] == VID_INT and len(hz_int['sat']) == 3749 and
           S.haze_after(ri) == ([[1928, 1946]], [[1928, 1946]]) and ri[-1] == [1928, 1946])
ok &= case('H7 NEGATIVE: rec_pcw_1.mp4 (sha 518df1a0, 9 923 frames): series up to frame 1 002 only, none after it',
           hz_one['video_sha256'] == VID_ONE and len(hz_one['sat']) == 9923 and S.haze_after(r1) == ([], []) and
           r1 and r1[-1][1] == 1002)
vb = b'fake video for the cache'
Path(BASE / 'v.mp4').write_bytes(vb)
json.dump(dict(video_sha256=hashlib.sha256(vb).hexdigest(), crop=S.HAZE_CROP, scale=[60, 12], sat=s_h),
          open(str(BASE / 'v.json'), 'w', encoding='ascii'))
ho = S.haze_of(str(BASE / 'v.mp4'), str(BASE / 'v.json'))
ok &= case('H8 haze_of reads the cache of the same video sha and crop (no ffmpeg); a missing video -> None',
           ho is not None and ho['runs'] == runs_h and ho['frames'] == 1200 and ho['after'] == [] and
           S.haze_of(str(BASE / 'none.mp4')) is None)
json.dump(dict(video_sha256='00' * 32, crop=S.HAZE_CROP, scale=[60, 12], sat=s_h), open(str(BASE / 'v2.json'), 'w', encoding='ascii'))
_real_sat = S.haze_sat
S.haze_sat = lambda path, ffmpeg='ffmpeg': [0.5] * 7       # stands for ffmpeg: no process in the suite
ho2 = S.haze_of(str(BASE / 'v.mp4'), str(BASE / 'v2.json'))
S.haze_sat = _real_sat
ok &= case('H8b a cache of another video sha is not used (the detector runs again and rewrites the cache)',
           ho2 is not None and ho2['frames'] == 7 and json.load(open(str(BASE / 'v2.json'), encoding='ascii'))['video_sha256']
           == hashlib.sha256(vb).hexdigest())

# ================================================================================================ 7 cache rows and admission
def crow(tag, **over):
    rs = S.cache_rows(S.SPEC[tag], cj_for(tag, **over), lambda t: cj_for(t))
    return [r for r in rs if not r[1]]


ok &= case('F1 cache rows pass as sealed: pi_w1 (full + post copies), pi_r1 (integrity), u_1 (form U), t2_2 (full)',
           not crow('pi_w1') and not crow('pi_r1') and not crow('u_1') and not crow('t2_2'))
ok &= case('F2 full: the app restore must be snap0, GLCache snap0_drv, launch = restore', crow('t2_2', restore_app=dict(
    expected='99' * 32, got='99' * 32)) and crow('t2_2', restore_glc=dict(expected='99' * 32, got='99' * 32)) and
    crow('t2_2', man_launch_glc=dict(sha='99' * 32)) and crow('t2_2', restore_app=dict(expected=SNAP_APP, got='99' * 32)) and
    crow('t2_2', restore_app=dict(expected='99' * 32, got=SNAP_APP)) and
    [r[0] for r in crow('t2_2', restore_glc=dict(expected='99' * 32, got='99' * 32), man_launch_glc=dict(sha='99' * 32))]
    == ['restore of GLCache = snap0_drv 1767ca0a'])
ok &= case('F3 integrity: the restores must be the post copies of its W', crow('pi_r1', restore_app=dict(
    expected=SNAP_APP, got=SNAP_APP)) and crow('pi_r0', restore_glc=dict(expected=SNAP_DRV, got=SNAP_DRV)) and
    S.cache_rows(S.SPEC['pi_r1'], cj_for('pi_r1'), lambda t: cj_for(t, app_post_copy=dict(sha='cc' * 32)))[0][1] is False)
ok &= case('F4 form U: the app restore must be the empty set; a GLCache restore before the arm fails; launch = man_pre_glc; '
           'the catalogue sha = the sealed one', crow('u_1', restore_app=dict(expected=SNAP_APP, got=SNAP_APP)) and
           crow('u_1', restore_glc=dict(expected=SNAP_DRV, got=SNAP_DRV)) and crow('u_1', man_launch_glc=dict(sha='99' * 32))
           and crow('u_1', seeds=dict(sha='99' * 32)) and crow('u_1', seeds={}))
ok &= case('F5 returns, the installed binary, return_prev, the manifests and the post copies of W are rows', crow(
    'pi_w1', return_app=dict(expected='16' * 32, got='99' * 32)) and crow('pi_w1', return_glc=dict(expected='17' * 32)) and
    crow('pi_w1', installed_after=dict(sha=BIN_S)) and crow('pi_w1', installed_before=dict(sha='ab')) and
    crow('pi_w1', installed_before=dict(sha='ab'), installed_after=dict(sha='ab')) and
    crow('pi_w1', return_prev=dict(ok='0')) and crow('pi_w1', man_post_glc={}) and crow('pi_w1', glc_post_copy={}) and
    crow('pi_w0', app_post_copy={}) and not crow('pi_r1', glc_post_copy={}))
ok &= case('F6 no cache json -> one failing row', S.cache_rows(S.SPEC['u_1'], None, lambda t: None) ==
           [('cache protocol json present', False, 'missing')])


def adm(tag, form=None, **over):
    js = js_for(tag, form, **over)
    rs = S.admit(S.resolved(S.SPEC[tag], form), js, PRED_SHA, cj_for(tag), lambda t: cj_for(t), PRED)
    return [r[0] for r in rs if not r[1]]


ok &= case('G1 admission passes as sealed (pi_w1, t2_4 C5, u_3)', not adm('pi_w1') and not adm('t2_4', 'c5') and not adm('u_3'))
ok &= case('G2 the binary: s arms need f3b3aa3b, u arms 4aa62e95', adm('pi_w1', binary_sha256=BIN_U) and
           adm('u_3', binary_sha256=BIN_S))
ok &= case('G3 KYTY_GAME_PATCH in the env, validation true, another hold, a retry, a wrong seal, gates, guest args, 2 attempts',
           'no KYTY_GAME_PATCH (item 342 (e))' in adm('pi_w1', env_over=dict(KYTY_GAME_PATCH='p.txt')) and
           adm('pi_w1', cmdline=['--vulkan-validation', 'true']) and
           adm('pi_w1', hold_s=120) and adm('pi_w1', attempt=dict(pipeline_cache_off=True)) and
           adm('pi_w1', prereg=dict(path=PRED, sha256='00' * 32)) and adm('pi_w1', prereg=dict(path='C:/x', sha256=PRED_SHA))
           and adm('pi_w1', gates='x') and adm('pi_w1', guest_args='-lvl x') and
           adm('pi_w1', attempts=[dict(label='attempt 1'), dict(label='attempt 2')]) and
           adm('pi_w1', env_over=dict(KYTY_GPU_CHECKPOINTS='1')) and adm('pi_w1', env_over=dict(KYTY_GATE_SCHEDULE='x')) and
           adm('pi_w1', env_over=dict(KYTY_REC='C:/x/rec_other.mp4')))
ok &= case('G4 a T2 arm admitted against its form: an APP env under the C5 form fails the family row and the strict row',
           'KYTY_* families = the seal (item 241 (v)(6), letter)' in adm('t2_4', 'c5', env=env_for('t2_4', 'app')) and
           'every KYTY_* key = the seal (executor variant, stricter)' in adm('t2_4', 'c5', env=env_for('t2_4', 'app')))

# ================================================================================================ 8 whole arms
W_POST = [(900000, {}) for _ in range(340)]                   # 306 s presented after the first scene frame
mkarm('pi_w1', scene(S.SKY, W_POST[:200] + [(16000, dict(ev=[DSAVE(1000)]))] + W_POST[200:] +
                     [(16000, dict(ev=[DSAVE(94435637)]))], header=HEADER_M))
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M))
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]))
g = getter()
aw, ar = g('pi_w1'), g('pi_r1')
ok &= case('I1 pi_w1 and pi_r1 admitted and readable: the knob lines, last write 94 435 637, R loaded it, the R T-4 letter',
           not aw['fail'] and not ar['fail'] and aw['saves']['last_bytes'] == 94435637 and ar['loaded'] == 94435637
           and S.clean_arm(aw) and S.clean_arm(ar) and ar['attr_ok'] and not aw['attr_ok'])
ok &= case('I2 haze read from the cache of the fake video on pi arms', aw['haze'] is not None and aw['haze']['after'] == [] and
           aw['haze']['frames'] == 3200)
w0, rd = S.read_pi(g)
ok &= case('I3 read_pi: no series anywhere, both R loaded the last write of their W -> READ_2', w0 == 'READ_2' and any(
    'pi_r1 loaded 94435637 bytes = last write of pi_w1 94435637, disabled 0 -> PASS' in x for x in rd))
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]), sat=sat_for([(1928, 1946)]))
w1, _ = S.read_pi(getter())
ok &= case('I4 a series after 1 002 in pi_r1 only -> READ_1', w1 == 'READ_1')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]), sat=sat_for([(1500, 1510)]))
w2, _ = S.read_pi(getter())
ok &= case('I5 series in both R and both loaded -> READ_2', w2 == 'READ_2')
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5)]), sat=sat_for([(1928, 1946)]))
w3, _ = S.read_pi(getter())
ok &= case('I6 series in both R but pi_r1 loaded another size -> READ_OTHER', w3 == 'READ_OTHER')
mkarm('pi_r1', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(94435637)]))
w4, _ = S.read_pi(getter())
ok &= case('I7 a series only in pi_r0 -> READ_3', w4 == 'READ_3')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), sat=sat_for([(2000, 2010)]))
w5, _ = S.read_pi(getter())
ok &= case('I8 a series only in a W arm -> READ_3', w5 == 'READ_3')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), sat=sat_for([(1000, 1010)]))
w6, rd6 = S.read_pi(getter())
ok &= case('I9 a W series across frame 1 002 (1 000 - 1 010): letter READ_2, the variant READ_3 printed as DIFFERS',
           w6 == 'READ_2' and any('READ_3 - DIFFERS (edge 1 002)' in x for x in rd6))
mkarm('pi_w0', scene(S.SKY, rows(30) + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M))
w7, rd7 = S.read_pi(getter())
ok &= case('I10 a W arm presented < 300 s -> NOT_EVALUABLE', w7 == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(2999, 0))
ok &= case('I11 a pi arm with a video < 3 000 frames -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3000, 0))
ok &= case('I11b a pi arm with exactly 3 000 video frames is readable', S.read_pi(getter())[0] == 'READ_2')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), glitch=(3200, 1))
ok &= case('I12 a pi arm with a one-frame glitch -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M), knob=False)
ok &= case('I13 the knob line missing on a pi arm -> admission FAIL -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE'
           and any('knob line' in x for x in getter()('pi_w0')['fail']))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M,
                     tail=['Unhandled exception: x']))
ok &= case('I14 a death marker on a pi arm -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M))
rm_arm('pi_r0')
ok &= case('I15 an arm not made -> NOT_EVALUABLE', S.read_pi(getter())[0] == 'NOT_EVALUABLE')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000), 'Vulkan pipeline cache: disabled (x)']))
ok &= case('I16 a disabled line on an R arm -> loaded FAIL -> READ_OTHER (no series)', S.read_pi(getter())[0] == 'READ_OTHER')
mkarm('pi_r0', scene(S.SKY, rows(20), header=HEADER_T[:-1] + [LOADED(5000)]))
ok &= case('I17 pi_word table: (r1, r0, w, loaded)', S.pi_word(dict(pi_r1=True, pi_r0=False, pi_w1=True, pi_w0=True),
                                                               {'a': False}) == 'READ_1' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': False}) == 'READ_OTHER' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=False), {'a': True}) == 'READ_2' and
           S.pi_word(dict(pi_r1=False, pi_r0=True, pi_w1=False, pi_w0=False), {'a': False}) == 'READ_3' and
           S.pi_word(dict(pi_r1=False, pi_r0=False, pi_w1=False, pi_w0=True), {'a': False}) == 'READ_3' and
           S.pi_word(dict(pi_r1=True, pi_r0=True, pi_w1=False, pi_w0=False), {'a': True, 'b': False}) == 'READ_OTHER')

# ---- c5_0 and the C5 reading
C5_EV = [GFX(30000, 'async') for _ in range(5)] + [GFX(20000, 'none') for _ in range(5)]
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0))
g = getter()
c5 = g('c5_0')
ok &= case('J1 c5_0 under PRECACHE=0: T-4 holds with no queue, attribution determined, the knob line 0 / 0, admitted',
           not c5['fail'] and c5['attr_ok'] and c5['create']['n'] == 10 and c5['create']['med'] == 25000)
f5, w5_, _ = S.read_c5(g)
ok &= case('J2 10 creations median 25 000 -> YES -> form C5', (f5, w5_) == ('c5', 'YES'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV[1:]))] + rows(10), header=HEADER_P0))
ok &= case('J3 9 creations -> NO -> form APP', S.read_c5(getter())[:2] == ('app', 'NO'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=[GFX(20000, 'async')] * 6 + [GFX(19999, 'none')] * 4))] + rows(10),
                    header=HEADER_P0))
ok &= case('J4 median exactly 20 000 -> YES (>=)', S.read_c5(getter())[:2] == ('c5', 'YES'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=[GFX(19999, 'async')] * 5 + [GFX(19998, 'none')] * 6))] + rows(10),
                    header=HEADER_P0))
ok &= case('J5 median 19 999 -> NO', S.read_c5(getter())[:2] == ('app', 'NO'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV + [GFX(1, 'precache')] * 9 + [CSL(1, 'waited')] * 9))] + rows(10),
                    header=[LOADED(90000)]))
c5b = getter()('c5_0')
ok &= case('J6 precache lines and waited lines are not in-game creations of the letter (median stays 25 000); a precache line '
           'breaks T-4 under PRECACHE=0 -> the arm FAILs -> UNDETERMINED', c5b['create']['n'] == 10 and
           c5b['create']['med'] == 25000 and c5b['create']['nous'] == 9 and S.read_c5(getter())[:2] == (None, 'UNDETERMINED'))
mkarm('c5_0', scene('other_level', [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0))
ok &= case('J7 c5_0 not entered -> UNDETERMINED, no T2 form', S.read_c5(getter())[:2] == (None, 'UNDETERMINED'))
rm_arm('c5_0')
ok &= case('J8 c5_0 not made -> NOT_MADE', S.read_c5(getter())[:2] == (None, 'NOT_MADE'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0), knob=False)
ok &= case('J9 c5_0 without the knob line 0 / 0 of f3b3aa3b -> FAIL -> UNDETERMINED', S.read_c5(getter())[:2] ==
           (None, 'UNDETERMINED'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0 + ['GamePatch: applied 4 pokes']))
ok &= case('J10 a GamePatch: line in the log -> admission FAIL (item 342 (e))', any('GamePatch' in x for x in getter()('c5_0')['fail']))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0))

# ---- T2 arms and their reading (form C5 now)
T2_EV = [SH(0x10 + 0, 50, 50), SKIP(8)]


def t2_arm(tag, cold=True, form='c5', extra=(), lv=None):
    lvl = lv or S.SPEC[tag]['level']
    pre = [SH(0xaa, 50, 50)] if False else []
    post = [(16000, dict(ev=([SH(0x77, 50, 50)] if cold else []) + ([SKIP(8)] if cold else []) + list(extra),
                         skip=1 if cold else 0, held=1 if cold else 0))] + rows(10)
    hdr = HEADER_P0 if form == 'c5' else HEADER_T
    mkarm(tag, scene(lvl, post, header=hdr), form=form, stdout_shaders=1 if cold else 0)


t2_arm('t2_1')
t2a = getter()('t2_1')
ok &= case('K1 a T2 arm in form C5: admitted, attribution, the gate letter "level not cold" (no recipe under PRECACHE=0), the '
           'variant "cold"', not t2a['fail'] and t2a['attr_ok'] and S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'),
                                                                              'letter')[1] == 'level not cold'
           and S.gate9(t2a['gates'], S.resolved(S.SPEC['t2_1'], 'c5'), 'variant')[1] == 'cold')
ok &= case('K2 t2_counted: letter False, variant True on that arm; a failing arm never counts', not S.t2_counted(t2a) and
           S.t2_counted(t2a, 'variant') and not S.t2_counted(None) and not S.t2_counted(dict(t2a, fail=['x']), 'variant')
           and not S.t2_counted(dict(t2a, entered=False), 'variant'))
lt = S.read_t2(getter())
ok &= case('K3 read_t2 prints the form, OUT by the letter, the variant count, the S-early row', lt[0].startswith('T2 form: c5;')
           and any(x.startswith('t2_1 hero_kratos: OUT;') for x in lt) and any('T2 counted 0 of 5 needed (variant gate: 1)' == x
                                                                                for x in lt)
           and any('S-early first half' in x and 'undetermined (denominator 0)' in x for x in lt))
t2_arm('t2_cs0', extra=['CsPretranslate: hit hash=1 saved_us=2 hits=1'])
lt2 = S.read_t2(getter())
ok &= case('K4 t2_cs0 against t2_1: the deltas and the CsPretranslate lines as data rows', any(
    x.startswith('t2_cs0 (KYTY_CS_PRETRANSLATE=0) against t2_1') and "('hit', 1)" in x for x in lt2))
c_t2 = getter()('t2_cs0')
ok &= case('K5 the BvhLoopCapTrip column, skip / held rows of a T2 arm', c_t2['skip_rows'] == 1 and c_t2['held'] == 1 and
           c_t2['bvh'] == [] and c_t2['skips_after'] == 1 and c_t2['skips_after_scene'] == 1)
mkarm('t2_7', scene(S.SPEC['t2_7']['level'], rows(600) + [(150000, dict(ev=['BvhLoopCapTrip: trips=+1 total=1']))] + rows(3),
                    header=HEADER_P0), form='c5')
k6 = getter()('t2_7')
ok &= case('K6 a presented frame >= 100 ms on the hold counts in dt100 (window + hold); its BvhLoopCapTrip line of group i in '
           'the column', k6['dt100'] == 1 and k6['bvh'] == [(608, 1)] and k6['f1']['hold']['shown100'] == 1)
rm_arm('t2_7')

# ================================================================================================ 9 order
mk = made()
g = getter()
ok &= case('L1 order: pi_w1 .. pi_r0 and c5_0 made -> t2_1 allowed (form C5 decided), t2_2 waits for t2_cs0, made tags refused',
           S.allowed('t2_cs0', mk, g)[0] == 1 and S.allowed('t2_2', mk, g)[0] == 0 and S.allowed('pi_w1', mk, g)[0] == 1)
rm_arm('t2_cs0')
mk = made()
g = getter()
ok &= case('L2 t2_cs0 right after t2_1; t2_2 before t2_cs0 refused (order); t2_cs0 before t2_1 refused',
           S.allowed('t2_cs0', mk, g)[0] == 0 and S.allowed('t2_2', mk, g) == (1, 't2_cs0 not made') and
           S.allowed('t2_cs0', lambda t: mk(t) and t != 't2_1', g) == (1, 't2_1 not made'))
rm_arm('c5_0')
mk = made()
ok &= case('L3 without c5_0 the T2 arms wait (rc 1); an unknown tag rc 2', S.allowed('t2_2', mk, getter()) ==
           (1, 'c5_0 not made') and S.allowed('zz', mk, getter())[0] == 2)
mkarm('c5_0', scene('other_level', [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0))
ok &= case('L4 c5_0 made but UNDETERMINED -> T2 refused rc 6', S.allowed('t2_cs0', made(), getter())[0] == 6)
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV))] + rows(10), header=HEADER_P0))
ok &= case('L5 the pi order: pi_r1 needs pi_w1 ... c5_0 needs pi_r0', S.allowed('pi_r1', lambda t: t in ('pi_w1',), getter())
           == (0, 'ok') and S.allowed('pi_w0', lambda t: t in ('pi_w1',), getter())[0] == 1 and
           S.allowed('c5_0', lambda t: t in ('pi_w1', 'pi_r1', 'pi_w0'), getter()) == (1, 'pi_r0 not made'))
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M, tail=['ErrorDeviceLost']))
ok &= case('L6 a death marker in an earlier arm stops every later tag (rc 6)', S.allowed('t2_cs0', made(), getter())[0] == 6
           and 'death marker' in S.allowed('t2_cs0', made(), getter())[1])
mkarm('pi_w0', scene(S.SKY, W_POST + [(16000, dict(ev=[DSAVE(5000)]))], header=HEADER_M))
for j in range(2, 6):
    t2_arm('t2_%d' % j, form='c5')
t2_arm('t2_cs0')
mk = made()
g = getter()
ok &= case('L7 by the letter none of five counted -> the reserve t2_6 allowed; u_1 waits for T2', S.allowed('t2_6', mk, g) ==
           (0, 'ok') and S.allowed('u_1', mk, g)[0] == 1)
for j in range(6, 11):
    t2_arm('t2_%d' % j, form='c5')
mk = made()
g = getter()
ok &= case('L9 every T2 tag made -> T2 done -> u_1 allowed, u_2 waits for u_1', S.t2_done(g, mk) and
           S.allowed('u_1', mk, g) == (0, 'ok') and S.allowed('u_2', mk, g) == (1, 'u_1 not made'))
mkarm('c5_0', scene(S.L0, [(16000, dict(ev=C5_EV[1:]))] + rows(10), header=HEADER_P0))      # 9 creations -> NO -> form APP


def t2_app(tag, cold=True):
    ev = [SH(0x77, 50, 50), SKIP(8)] + (['PipelinePrecache: saved 101 recipes (100 bytes)'] if cold else [])
    mkarm(tag, scene(S.SPEC[tag]['level'], [(16000, dict(ev=ev, skip=1, held=1))] + rows(10), header=HEADER_T), form='app',
          stdout_shaders=1)


for j in range(1, 6):
    t2_app('t2_%d' % j)
t2_app('t2_cs0')
for j in range(6, 11):
    rm_arm('t2_%d' % j)
mk = made()
g = getter()
ok &= case('L10 form APP: five T2 arms cold by the letter (a recipe saved after the entry) -> T2 done with exactly five, the '
           'reserve t2_6 refused rc 6', S.read_c5(g)[0] == 'app' and S.t2_counted(g('t2_5')) and S.t2_done(g, mk) and
           S.allowed('t2_6', mk, g)[0] == 6 and S.allowed('u_1', lambda t: mk(t) and t != 't2_cs0', g)[0] == 1)
t2_app('t2_5', cold=False)
mk = made()
g = getter()
ok &= case('L11 four counted -> T2 not done, the reserve t2_6 allowed, u_1 waits', not S.t2_done(g, mk) and
           S.allowed('t2_6', mk, g) == (0, 'ok') and S.allowed('u_1', mk, g)[0] == 1)
t2_app('t2_5')

# ================================================================================================ 10 U arms
U_HDR = ['ShaderSeed: compatibility=x', 'ShaderSeed: installed (615 shaders)'] + HEADER_T
U_STD = ['Cache test mode: prepare-cold (fresh driver namespace 1)']


def u_arm(tag, skip=False, att=False, gates=True, std=True, created=30.0, ready=31.0, lv=None):
    hdr = U_HDR if gates else HEADER_T
    post = [(16000, dict(ev=[SKIP(8)] if skip else [], skip=1 if skip else 0, held=1 if skip else 0))]
    if att:
        post += [(150000, dict(ev=[SH(0x55, 140000, 1000)]))]
    post += rows(10)
    mkarm(tag, scene(lv or S.SPEC[tag]['level'], post, header=hdr), stdout_shaders=1 if att else 0,
          extra_stdout=U_STD if std else (), js=js_for(tag, attempt=dict(prep_created_s=created, prep_ready_s=ready)))


for j in range(1, 6):
    u_arm('u_%d' % j)
g = getter()
wu, lu = S.read_u(g)
ok &= case('M1 five U arms with both gates, no skip, no attributed frame, screens 31 s -> ALIVE_BY_PROBE_5', wu == 'ALIVE_BY_PROBE_5'
           and not g('u_1')['fail'])
u_arm('u_2', skip=True)
ok &= case('M2 one arm with a skipped draw after the first scene frame -> still alive (kill at 2)', S.read_u(getter())[0] ==
           'ALIVE_BY_PROBE_5')
u_arm('u_4', att=True)
ok &= case('M3 a second arm with an attributed frame >= 100 ms -> KILLED', S.read_u(getter())[0] == 'KILLED')
u_arm('u_2')
u_arm('u_4')
u_arm('u_5', created=181.0, ready=30.0)
ok &= case('M4 a screen of 181 s (the later of the two lines) -> KILLED', S.read_u(getter())[0] == 'KILLED')
u_arm('u_5', created=180.0, ready=179.0)
ok &= case('M5 a screen of exactly 180 s -> not over (alive)', S.read_u(getter())[0] == 'ALIVE_BY_PROBE_5')
u_arm('u_5', created=None, ready=30.0)
ok &= case('M6 one screen line not seen -> the screen undetermined -> UNDETERMINED', S.read_u(getter())[0] == 'UNDETERMINED')
u_arm('u_5', gates=False)
f_, gw_, _, _ = S.u_eval(getter()('u_5'))
ok &= case('M7 no "ShaderSeed: installed" -> CATALOGUE NOT INSTALLED, undetermined member', f_ is None and
           gw_.startswith('CATALOGUE NOT INSTALLED') and S.read_u(getter())[0] == 'UNDETERMINED')
u_arm('u_5', std=False)
ok &= case('M8 no "Cache test mode: prepare-cold" -> CATALOGUE NOT INSTALLED', S.u_eval(getter()('u_5'))[1].startswith(
    'CATALOGUE NOT INSTALLED'))
mk = made()
ok &= case('M9 u_5 is allowed after u_4 when every earlier U arm installed the catalogue', S.allowed(
    'u_5', lambda t: t != 'u_5' and mk(t), getter()) == (0, 'ok'))
u_arm('u_2', gates=False)
ok &= case('M10 u_3 refused rc 6 when u_2 had no catalogue', S.allowed('u_3', lambda t: mk(t) and t not in ('u_3', 'u_4', 'u_5'),
                                                                       getter())[0] == 6)
u_arm('u_2')
u_arm('u_5')
ok &= case('M11 u_eval of a not made arm -> undetermined', S.u_eval(None)[0] is None and S.u_eval(None)[1] == 'not made')

# ================================================================================================ 11 seal and main
seal = BASE / 'pred' / 'seal.md'
names = list(S.SEALED_NAMES)
lines = []
for n in names:
    p = n if n.startswith('C:/') else os.path.join('C:/kyty/s288', n)
    lines.append('seal: %s %s' % (S.A.sha_file(p) if os.path.isfile(p) else '00' * 32, n))
lines += ['s binary: %s C:/x/s.exe' % BIN_S, 'u binary: %s C:/x/u.exe' % BIN_U]
seal.write_text('\n'.join(lines) + '\n', encoding='ascii')
okk, rows_, bins = S.check_seal(str(seal), 'C:/kyty/s288', me=SRC)
bad = [r[0] for r in rows_ if not r[1]]
ok &= case('N1 check_seal: the binary lines read, a missing file fails its row only', bins == {'s': (BIN_S, 'C:/x/s.exe'),
                                                                                         'u': (BIN_U, 'C:/x/u.exe')}
           and all(r[1] for r in rows_ if r[0].startswith('binary lines')))
seal.write_text('\n'.join(lines[:-1]) + '\n', encoding='ascii')
ok &= case('N2 check_seal: no u binary line -> the binary row fails', not [r for r in S.check_seal(str(seal), 'C:/kyty/s288', me=SRC)[1]
                                                                          if r[0].startswith('binary lines')][0][1])
seal.write_text('\n'.join(lines[1:]) + '\n', encoding='ascii')
ok &= case('N3 check_seal: a sealed name without its line fails its row and the whole check', any(
    r[0] == names[0] and r[2] == 'no seal line' for r in S.check_seal(str(seal), 'C:/kyty/s288', me=SRC)[1]) and
    S.check_seal(str(seal), 'C:/kyty/s288', me=SRC)[0] is False)
ok &= case('N4 check_seal: a missing seal file fails', S.check_seal(str(BASE / 'nothing.md'))[0] is False)
ok &= case('N5 the sealed names include the harness, the scorer, the suites, the lists, the export, the detector, sc_s, cachex',
           all(x in S.SEALED_NAMES for x in ('s9/go_s9.sh', 's9/sc_s9.py', 's9/test_sc_s9.py', 's9/mut_sc_s9.py',
                                             's9/test_go_s9.py', 's9/enter_scene_s9.py', 's9/lvl_s9.out.txt',
                                             's9/seeds_manifest.txt', 'lead/haze_s8.py', 'sc_s.py', 'cachex_s.py',
                                             's9/fx/haze_pcw_int.json', 's9/fx/haze_pcw_1.json')))


def run_main(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = S.main(argv, ROOT, PRED)
    return rc, buf.getvalue()


rc1, o1 = run_main(['--plan', 't2_2'])
rc2, o2 = run_main(['--plan', 't2_2', '--form', 'c5'])
ok &= case('O1 main --plan: the form from the C5 reading (APP now) or --form', rc1 == 0 and o1.strip() ==
           's10 hero_drake T full 120 0 - - 100 480 0 0 0 s app' and o2.strip() == 's10 hero_drake T full 120 1 - - 100 480 1 0 0 s c5')
rc3, o3 = run_main(['--allowed', 'u_1'])
ok &= case('O2 main --allowed prints the ALLOWED line and returns the rc', rc3 == 1 and o3.startswith('ALLOWED u_1: no'))
rc4, o4 = run_main(['--tag', 'u_1', '--json-out', str(BASE / 'u_1.score.json')])
ok &= case('O3 main --tag: the arm printed, the json written, rc 0 for an admitted arm', rc4 == 0 and o4.startswith('ARM u_1') and
           json.load(open(str(BASE / 'u_1.score.json'), encoding='utf-8'))['tag'] == 'u_1')
mkarm('u_1', scene('x', rows(5), header=U_HDR), extra_stdout=U_STD, glitch=None, js=js_for('u_1', binary_sha256=BIN_S))
rc5, _ = run_main(['--tag', 'u_1', '--json-out', str(BASE / 'u_1b.score.json')])
rc6, o6 = run_main(['--tag', 'zz'])
ok &= case('O4 main --tag of a failing arm rc 1; an unknown tag rc 2', rc5 == 1 and rc6 == 2)
rc7, o7 = run_main(['--summary'])
try:
    o7.encode('cp1250', 'strict')
    asc = all(ord(c) < 128 for c in o7 + o4 + o1)
except UnicodeError:
    asc = False
ok &= case('O5 --summary runs, the output is ASCII (strict cp1250)', rc7 == 0 and asc and 'READ C5' in o7 and 'READ S-cat' in o7)
sd = BASE / 'seeds' / 'PPSA21564'
sd.mkdir(parents=True)
(sd / 'a.bin').write_bytes(b'abc')
(sd / 'compatibility.txt').write_bytes(b'x\n')
want = hashlib.sha256(('a.bin 3 %s\ncompatibility.txt 2 %s\n' % (hashlib.sha256(b'abc').hexdigest(),
                                                                  hashlib.sha256(b'x\n').hexdigest())).encode('ascii')).hexdigest()
ok &= case('O6 seeds_sha: the manifest of seedexp_s9.py ("<name> <bytes> <sha256>" sorted); a missing dir -> None',
           S.seeds_sha(str(sd)) == (want, 2) and S.seeds_sha(str(BASE / 'nope'))[0] is None)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
