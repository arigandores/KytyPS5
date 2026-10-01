"""Offline fixtures of sc_s.py (track S, link S3, HPP-313; ROADMAP "SESSION 122" item 241 (v)-(z); S0 4.5 and the S1 RC2-RC17).
One case per term and per edge: the counters skc_ap_skip / skc_held_inc / skc_held / skc_bad and a missing FrameTrace-x or
field; T-1 at 199 999 / 200 000 lines; T-2 at 64 / 65; T-6 +-1 (RC5); the held series (length 1, open at the end, across the
window 599 / 600, at the first scene frame in both readings, two series one row apart) and the visible gap at 99 999 /
100 000 and 999 999 / 1 000 000; gap_pipe (RC4); the secondary +-2 rule; the classes PCW -> SHADER -> PRIO -> GPUTHR -> WAIT
with both stall conventions (RC3, RC8); PREP over groups i-2 .. i+1, one line one row, the tie, compile_us without
shader-emit, the pipeline kinds (RC16, S0 4.5 (7)-(8)); attribution only on T with T-3 / T-4 (RC7); the leads of S-early and
the empty denominator (RC11); the preparation lines; cold / warm medians 4 999 / 5 000 / 19 999 / 20 000 and 9 / 10
creations; the KYTY_* families and the strict row (RC6, RC14, RC15); the cache protocol rows (RC1, RC12) per restore mode; the
cold and warm gates and the snap0 pairs (RC9, RC12); the C1-C4 reading at every threshold (RC2, RC10); S-warm with the base
>= 5 (RC9); the T2 reading; S-pcw (a)-(e); the order of the arms (RC13); the seal; the inheritance check; video is not a
freeze identity (RC17); ASCII output in strict cp1250.  Synthetic logs only; the 12 sc142 logs are read by --regress.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last
statement is `sys.exit(0 if ok else 1)`; no subprocess (main() is called in-process).
S3b (HPP-325, ROADMAP item 250): the fixtures of RC1 (installed_after = installed_before), RC2 (return_prev_ok, the
continuity data row), RC3 (PCW rows attributed, gap_pipe minus PRIO only, the second reading (v)(2) before item 250), RC4
(the cold gate in C1-C4, "undetermined (T-3/T-4)" apart, a not cold C1 -> L0 reserve), RC5 (pcw_int is T, the AvTrace pcw
lines, not PREP), RC6 (Incomplete -> ARM1_CODE_DEFECT), RC7 (KYTY_FIX_), RC8 (not attributed rows), RC10 (man_launch_glc,
glc_post bases), RC11 (VALIDATION_STOP_PRE_LEVEL); D14 and H4c now read the governing gap_pipe of item 250 (g)(2).
S4b (HPP-349, ROADMAP item 265): RX_SHADER on the real line 232419 of s4/log_c1_0.txt (a label with a space) and on a
one-word label, the order of the branches on the real shader-emit / shader-cache / shader-spec lines, a T arm with the
real lines (T-3, the cold gate), the admission of the seal 02 arms against seal 02, --json-out (section 12).
The first output line names this suite and the scorer under test by sha256 (item 150 (v)); the output ends with ALL OK.
    python C:/kyty/s288/test_sc_s.py [<sc_s under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc_s.py')
print('suite test_sc_s.py sha256 %s target sc_s.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc_s_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BUILD = '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7'
PBIN = 'cd' * 32
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'
BASE = Path('C:/kyty/s288/s3/fx_sc_s')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
RM = {'s4': str(BASE / 's4'), 's6': str(BASE / 's6')}
PRED4 = (BASE / 'pred' / '01_s.md').as_posix()
PRED6 = (BASE / 'pred' / '02_s.md').as_posix()
(BASE / 'pred').mkdir()
Path(PRED4).write_bytes(b'seal of S4\n')
Path(PRED6).write_bytes(('seal of S6\npcw binary: %s C:/x/kyty.exe\n' % PBIN).encode('ascii'))
PRED_SHA = hashlib.sha256(Path(PRED4).read_bytes()).hexdigest()
PRED6_SHA = hashlib.sha256(Path(PRED6).read_bytes()).hexdigest()
N_CASES = [0]
OUTS = []


def case(name, cond):
    N_CASES[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


# ------------------------------------------------------------------------------------------------ log lines
def FT(n, dt, draws=3000, cg=0):
    return 'FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=%d cpu_main_us=1 cpu_gpu_us=%d cpu_present_us=1' % (
        n, dt, draws, cg)


def FX(n, skip=0, held=0, hk=0, bad=0):
    return 'FrameTrace-x: n=%d rec_pack=0 skc_held=%d skc_held_inc=%d skc_ap_skip=%d skc_bad=%d sf_bad=0' % (
        n, hk, held, skip, bad)


def SKIP(frame, vs=1, ps=2, pending=1):
    return 'AsyncPipelines: skipped draw DrawIndex frame=%d vs=0x%016x ps=0x%016x pending=%d total_skipped=1' % (
        frame, vs, ps, pending)


def HELDL(n):
    return 'AsyncPipelines: flip %d held' % n


def PRIO(us):
    return 'PriorityStall: tick=1 unsub=1 us=%d site=+0x90a231' % us


def DSAVE(b, us=90000, forced=False):
    return 'Vulkan pipeline cache: saved %d bytes to _PipelineCache/PPSA21564.bin (%d us)%s' % (b, us, ' forced' if forced else '')


def RSAVE(n):
    return 'PipelinePrecache: saved %d recipes (100 bytes)' % n


def SH(h, tr, comp, label='VS'):
    return 'AvTrace: shader %s hash=0x%016x translate_us=%d compile_us=%d permutations=1' % (label, h, tr, comp)


def EMIT(us):
    return 'AvTrace: shader-emit VS hash=0x0000000000000001 emit_us=%d validate_us=1 module_us=2 words=3' % us


def GFX(us, kind='async', wait=7):
    if kind == 'async':
        return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 async wait_us=%d pending=0' % (us, wait)
    if kind == 'precache':
        return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5 precache' % us
    return 'AvTrace: pipeline gfx vs=1 ps=2 us=%d total=5' % us


def CS(us, kind='async'):
    if kind == 'async':
        return 'AvTrace: pipeline cs cs=1 us=%d total=5 async wait_us=3 hash=0x0000000000000009' % us
    if kind == 'sync':
        return 'AvTrace: pipeline cs cs=1 us=%d total=5 sync hash=0x0000000000000009' % us
    if kind == 'precache':
        return 'AvTrace: pipeline cs cs=1 us=%d total=5 precache' % us
    return 'AvTrace: pipeline cs cs=1 waited_us=%d hash=0x0000000000000009' % us


def LOAD(us):
    return 'AvTrace: shader-cache load hash=0x0000000000000003 permutations=1 us=%d' % us


def REG(h, us):
    return 'ShaderRegister: hash=%016x type=1 size=2 scratch=0 code=0000000000000000 header=0000000000000000 host_us=%d 1=2' % (h, us)


def FIRST(h, us):
    return 'ShaderFirstUse: hash=%016x stage=1 words=2 ud=3 host_us=%d' % (h, us)


def QUEUED(r, g=1, c=1, sk=41):
    return ('PipelinePrecache: %d recipes -> %d graphics + %d compute pipelines queued, %d skipped, 9 sources loaded, '
            'complete, 381 ms (scratch: 0 pipelines, max 0 dwords/thread)' % (r, g, c, sk))


def START(level):
    return 'GuestOut: Level has started: %s' % level


HEADER_T = [QUEUED(100, 1, 1), GFX(300, 'precache'), CS(300, 'precache'), 'PipelinePrecache: all pipelines created, 400 ms',
            'ShaderPreparation: ready completed=100 total=100 skipped=41',
            'ShaderPreparation: startup wait finished in 77 ms presents_other=0 presents_main=0',
            'Vulkan pipeline cache: loaded 90000 bytes from _PipelineCache/PPSA21564.bin']
HEADER_M = [QUEUED(100, 1, 1), 'PipelinePrecache: all pipelines created, 400 ms',
            'ShaderPreparation: ready completed=100 total=100 skipped=41',
            'ShaderPreparation: startup wait finished in 77 ms presents_other=0 presents_main=0',
            'Vulkan pipeline cache: loaded 90000 bytes from _PipelineCache/PPSA21564.bin']


def scene(level, post, first=None, header=(), nox=(), pre_entry=(), tail=()):
    """header events, boot rows 1-3, start '', rows 4-5, the entry line (+ pre_entry events), loading row 6 (draws 20),
    the first scene frame 7, then post rows 8...; a row is (dt, dict(cg, skip, held, hk, bad, ev, draws))."""
    out = list(header)
    for n in range(1, 4):
        out += [FT(n, 20000, 5), FX(n)]
    out.append(START(''))
    for n in (4, 5):
        out += [FT(n, 20000, 5), FX(n)]
    out.append(START(level))
    out += list(pre_entry)
    out += [FT(6, 900000, 20), FX(6)]
    rows = [first or (15000, {})] + list(post)
    n = 7
    for dt, o in rows:
        out += list(o.get('ev', ()))
        if o.get('held', 0) > 0 and not o.get('nohl'):
            out.append(HELDL(n))      # the present thread's "flip N held" line of a held flip (first 64 per process)
        out.append(FT(n, dt, o.get('draws', 900 if n == 7 else 3000), o.get('cg', 0)))
        if n not in nox:
            out.append(FX(n, o.get('skip', 0), o.get('held', 0), o.get('hk', 0), o.get('bad', 0)))
        n += 1
    out += list(tail)
    return out


def write_log(path, lines):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))
    return str(path)


def sc(lines, name='x'):
    return S.scan_s(write_log(BASE / 'logs' / ('%s.txt' % name), lines))


def lv(s, level='lvl'):
    return S.locate(s, level)


# ------------------------------------------------------------------------------------------------ runs
def env_for(spec, **over):
    e = dict(S.expected_env(spec))
    e.update(KYTY_GATE_FILE='x/gates.req', KYTY_SAMPLE_GATE='x/sample.req',
             KYTY_REC='C:\\kyty\\s288\\%s\\rec_%s.mp4' % (spec['link'], spec['tag']))
    if spec['val']:
        e['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
    for k, v in over.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def js_for(tag, env_over=None, attempt=None, **over):
    spec = S.SPEC[tag]
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'x']
    if spec['val']:
        cmd += ['--vulkan-validation', 'true']
    a = dict(label='attempt 1', attempt=1, outcome='ok', hold_s=float(spec['hold']), hold_exit=None, ft_tail=300,
             pipeline_cache_off=False)
    a.update(attempt or {})
    js = dict(tag=tag, binary_sha256=BUILD if spec['link'] == 's4' else PBIN, guest_args='-lvl %s' % spec['level'],
              gates='', env=env_for(spec, **(env_over or {})), cmdline=cmd, hold_s=spec['hold'],
              prereg=dict(path=PRED4 if spec['link'] == 's4' else PRED6,
                          sha256=PRED_SHA if spec['link'] == 's4' else PRED6_SHA), attempts=[a])
    js.update(over)
    return js


def cj_for(tag, **over):
    spec = S.SPEC[tag]
    d = dict(man_pre_app=dict(sha='11' * 32), man_pre_glc=dict(sha='12' * 32), man_post_app=dict(sha='13' * 32),
             man_post_glc=dict(sha='14' * 32), glc_pre_copy=dict(sha='15' * 32),
             return_app=dict(expected='16' * 32, got='16' * 32), return_glc=dict(expected='17' * 32, got='17' * 32),
             installed_before=dict(sha=BUILD), installed_after=dict(sha=BUILD), return_prev=dict(ok='1'))
    if spec['mode'] == 'integrity':
        d['restore_app'] = dict(expected='aa' * 32, got='aa' * 32)
    else:
        d['restore_app'] = dict(expected=SNAP_APP, got=SNAP_APP)
    if spec['mode'] == 'full':
        d['restore_glc'] = dict(expected=SNAP_DRV, got=SNAP_DRV)
    else:
        d['restore_glc'] = dict(expected='bb' * 32, got='bb' * 32)
    d['man_launch_glc'] = dict(sha=d['restore_glc']['got'])
    if tag in ('c1_0', 'c3_0', 'c1_1', 'c3_1', 'c1_2', 'c3_2', 'pcw_3'):
        d['glc_post_copy'] = dict(sha='bb' * 32)
    if tag == 'pcw_3':
        d['app_post_copy'] = dict(sha='aa' * 32)
    d.update(over)
    return d


def mkarm(tag, lines, js=None, stdout_shaders=0, glitch=(3200, 0), cj=None, root=None, extra_stdout=()):
    spec = S.SPEC[tag]
    d = Path((root or RM)[spec['link']])
    (d / 'runs_s').mkdir(parents=True, exist_ok=True)
    (d / ('%s.json' % tag)).write_text(json.dumps(js if js is not None else js_for(tag)), encoding='utf-8')
    write_log(d / ('log_%s.txt' % tag), lines)
    st = ['Shaders: VS %d | PS 0 | CS 0 | GS 0 | LS 0 | HS 0 | TES 0' % (i + 1) for i in range(stdout_shaders)]
    (d / ('stdout_%s.txt' % tag)).write_bytes(('\n'.join(list(extra_stdout) + st) + '\n').encode('utf-8'))
    (d / ('%s.stdout.txt' % tag)).write_bytes(b'VERDICT: x\n')
    if glitch is not None:
        (d / ('glitch_%s.txt' % tag)).write_text('C:/x/rec_%s.mp4: %d frames 960x540, index entries %d\n'
                                                 'one-frame glitches: %d\n' % (tag, glitch[0], glitch[0], glitch[1]))
    (d / 'runs_s' / ('%s.cache.json' % tag)).write_text(json.dumps(cj if cj is not None else cj_for(tag)),
                                                        encoding='utf-8')


def arm(tag, root=None, ix=None):
    spec = S.SPEC[tag]
    return S.score_arm(tag, root or RM, PRED_SHA if spec['link'] == 's4' else PRED6_SHA,
                       BUILD if spec['link'] == 's4' else PBIN, ix, PRED4 if spec['link'] == 's4' else PRED6)


def rows_ok(post_n=10, dt=16000):
    return [(dt, {}) for _ in range(post_n)]


def t_lines(level, post, first=None, pre_entry=(), tail=(), header=None, nox=()):
    return scene(level, post, first, HEADER_T if header is None else header, nox, pre_entry, tail)


def m_lines(level, post, first=None, pre_entry=(), tail=(), nox=()):
    return scene(level, post, first, HEADER_M, nox, pre_entry, tail)


ok = True

# ================================================================================================ 1 inheritance and spec
try:
    S.load142(S.SC142_PATH, '00' * 32)
    inh = False
except SystemExit as e:
    inh = 'inheritance is broken' in str(e)
ok &= case('A1 load142 refuses a sc142.py whose sha256 is not the pinned one', inh)
ok &= case('A2 the pinned sc142.py is the s142 file (sha 1ce612cd...) and B is it', S.SHA142.startswith('1ce612cd')
           and S.SC142_PATH == 'C:/kyty/s142/sc142.py' and S.B.ENTRY_WIN == 599 and S.B.K3_US == 100000)
tags = [x['tag'] for x in S.ARMS]
ok &= case('A3 the arms of item 241: S-warm 3 M + sw_t1, C1-C4 x3 L0 candidates, T2 10, G 2 + 3, S6 6', tags[:4] ==
           ['sw_m1', 'sw_m2', 'sw_m3', 'sw_t1'] and tags[4:8] == ['c1_0', 'c2_0', 'c3_0', 'c4_0'] and
           len([t for t in tags if t.startswith('t2_')]) == 10 and tags[-6:] == ['pcw_1', 'pcw_2', 'pcw_3', 'pcw_int',
                                                                               'pcw_4', 'pcw_val'] and len(tags) == 37)
ok &= case('A4 levels: S-warm (e), L0 and reserves (d), T2 base and reserves (zh), G, Sky Garden for S6',
           [S.SPEC[t]['level'] for t in ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1')] == ['big_hand_pirate_island', 'voxel_world',
                                                                                 'ice_iceberg', 'big_hand_pirate_island']
           and [S.SPEC['c1_%d' % k]['level'] for k in range(3)] == ['shuriken_ninja_castle', 'jack_in_the_box',
                                                                    'cymbal_party_land']
           and [S.SPEC['t2_%02d' % k]['level'] for k in (1, 5, 6, 10)] == ['small_pot_lava', 'hero_kratos', 'picup_light',
                                                                           'bonus_path_maker_mix']
           and S.SPEC['g_1']['level'] == 'underwater_aerial_garden' and S.SPEC['g_2']['level'] == 'big_hand_pirate_island'
           and S.SPEC['g_3_1']['level'] == 'jack_in_the_box' and S.SPEC['pcw_val']['level'] == 'underwater_aerial_garden')
ok &= case('A5 classes and modes: sw_m* M, sw_t1/C/T2 T, g G; C2/C4 GLCache from C1/C3; C4 salted; pcw_int integrity',
           [S.SPEC[t]['cls'] for t in ('sw_m1', 'sw_t1', 'c2_0', 't2_03', 'g_3_0', 'pcw_1')] == ['M', 'T', 'T', 'T', 'G', 'M']
           and S.SPEC['c2_0']['glc_from'] == 'c1_0' and S.SPEC['c4_1']['glc_from'] == 'c3_1' and S.SPEC['c4_0']['salt']
           and not S.SPEC['c3_0']['salt'] and S.SPEC['c1_0']['mode'] == 'full' and S.SPEC['pcw_int']['mode'] == 'integrity'
           and S.SPEC['pcw_int']['app_from'] == 'pcw_3' and S.SPEC['pcw_val']['val'] and not S.SPEC['pcw_4']['val'])
ok &= case('A6 S6 knob values ABBA 0 1 1 0, integrity and validation 1, holds 330 / 120 / 310; S4 holds 120',
           [S.SPEC[t]['pcw'] for t in ('pcw_1', 'pcw_2', 'pcw_3', 'pcw_int', 'pcw_4', 'pcw_val')] == ['0', '1', '1', '1', '0', '1']
           and [S.SPEC[t]['hold'] for t in ('pcw_1', 'pcw_int', 'pcw_val', 'c1_0', 'sw_m1')] == [330, 120, 310, 120, 120])
ok &= case('A7 plan lines: c4_0 salt and 900 s; pcw_val validation 600 s; sw_m1 100 / 480',
           S.plan(S.SPEC['c4_0']) == 's4 shuriken_ninja_castle T glc_from 120 1 - 0 c3_0 - 100 900'
           and S.plan(S.SPEC['pcw_val']) == 's6 underwater_aerial_garden M full 310 0 1 1 - - 300 600'
           and S.plan(S.SPEC['sw_m1']) == 's4 big_hand_pirate_island M full 120 0 - 0 - - 100 480'
           and S.plan(S.SPEC['pcw_int']) == 's6 underwater_aerial_garden T integrity 120 0 1 0 pcw_3 pcw_3 300 480')
ok &= case('A7c pcw_int is a T arm (RC5, item 247 (b) V3): the trace environment, T-3 / T-4 apply',
           S.SPEC['pcw_int']['cls'] == 'T' and S.expected_env(S.SPEC['pcw_int'])['KYTY_AV_TRACE'] == '1'
           and S.expected_env(S.SPEC['pcw_int'])['KYTY_S_PCW'] == '1' and S.SPEC['pcw_2']['cls'] == 'M')
ok &= case('A7b the sealed environments literally: M base, T + traces, G + DUMP_GCN=1, C4 + its tag as the salt, S6 + the '
           'knob and the stand', S.expected_env(S.SPEC['sw_m1']) == dict(
               KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1',
               KYTY_GUEST_ARGS='-lvl big_hand_pirate_island', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
           and S.expected_env(S.SPEC['c4_2'])['KYTY_PIPELINE_SALT'] == 'c4_2'
           and S.expected_env(S.SPEC['g_1'])['KYTY_DUMP_GCN'] == '1'
           and S.expected_env(S.SPEC['sw_t1'])['KYTY_SHADER_REGISTER_TRACE'] == '1'
           and S.expected_env(S.SPEC['pcw_4'])['KYTY_S_PCW'] == '0' and S.expected_env(S.SPEC['pcw_4'])['KYTY_S_PCW_FORCE_MS'] == '15000')
ok &= case('A8 constants of item 241: snap0 d8ca8c8e, snap0_drv 1767ca0a, 20 000 / 5 000 / 10, [0.5; 2], 0.25, 6 760, '
           '50 % / 5, 15 / 50 %, force 15000', S.SNAP_APP == SNAP_APP and S.SNAP_DRV == SNAP_DRV and S.COLD_US == 20000
           and S.WARM_US == 5000 and S.MIN_CREATE == 10 and S.RET_LO == 0.5 and S.RET_HI == 2.0 and S.GLC_WARM == 0.25
           and S.SALT_PREP_MS == 6760 and S.WARM_KEEP == 0.5 and S.WARM_BASE_MIN == 5 and S.PCW_MIN_WRITES == 15
           and S.PCW_POS_FRAC == 0.5 and S.PCW_FORCE_MS == '15000' and S.BUILD_SHA == BUILD)
ok &= case('A9 seal paths and links (item 265: S4 seal 03 of S4b, the seal 02 arms sw_m1..sw_t1 + c1_0 by seal 02 829ac684, S6 a '
           'later seal 04)', S.PRED_PATH == 'C:/kyty/s288/pred/03_s.md'
           and S.PRED_S6 == 'C:/kyty/s288/pred/04_s.md' and S.PRED_02 == 'C:/kyty/s288/pred/02_s.md'
           and S.SHA_02 == '829ac684f2de5311cda035b5135d6bb262448bf282f5a2e803a2e73e447c6515'
           and S.SEAL02_TAGS == ('sw_m1', 'sw_m2', 'sw_m3', 'sw_t1', 'c1_0') and S.SEAL_PREV == (S.PRED_02, S.SHA_02, S.SEAL02_TAGS)
           and S.LINKS == {'s4': 'C:/kyty/s288/s4', 's6': 'C:/kyty/s288/s6'} and S.INDEX_PATH == 'C:/kyty/s288/s3/snap0_index.json')

# ================================================================================================ 2 environment (RC6, RC14, RC15)
for tag, extra, want_fam, want_strict, label in (
        ('sw_m1', {}, True, True, 'M arm exactly as sealed'),
        ('c4_0', {}, True, True, 'C4 with its salt'),
        ('c3_0', dict(KYTY_PIPELINE_SALT='c3_0'), False, False, 'a salt on C3 (only C4 is salted, item 241 (g)(4))'),
        ('c4_0', dict(KYTY_PIPELINE_SALT=None), False, False, 'C4 without the salt'),
        ('sw_m1', dict(KYTY_ASYNC_PIPELINE_WAIT_US='900000'), False, False, 'KYTY_ASYNC_PIPELINE_WAIT_US=900000 (RC6)'),
        ('sw_m1', dict(KYTY_CACHE_MODE='prepare-cold'), False, False, 'KYTY_CACHE_MODE (RC3 / RC6)'),
        ('sw_m1', dict(KYTY_CS_PRETRANSLATE='0'), False, False, 'KYTY_CS_PRETRANSLATE=0 (RC15)'),
        ('g_1', dict(KYTY_DUMP_GCN=None), False, False, 'G arm without KYTY_DUMP_GCN (RC14)'),
        ('g_1', dict(KYTY_DUMP_GCN='2'), False, False, 'G arm with KYTY_DUMP_GCN=2'),
        ('sw_t1', dict(KYTY_SHADER_REGISTER_TRACE=None), False, False, 'T arm without the register trace'),
        ('sw_t1', dict(KYTY_AV_TRACE=None), True, False, 'T arm without KYTY_AV_TRACE: not a family - strict row only'),
        ('pcw_1', dict(KYTY_S_PCW='1'), False, False, 'pcw_1 with KYTY_S_PCW=1'),
        ('pcw_2', dict(KYTY_S_PCW_FORCE_MS='20000'), False, False, 'the stand at 20000 ms'),
        ('sw_m1', dict(KYTY_DUMP_FRAME='5'), False, False, 'a KYTY_DUMP_* knob'),
        ('sw_m1', dict(KYTY_GPU_CHECKPOINTS='1'), True, False, 'KYTY_GPU_CHECKPOINTS - strict row'),
        ('sw_m1', dict(KYTY_REC=None), True, False, 'no KYTY_REC - strict row (path key present)'),
        ('sw_m1', dict(KYTY_FIX_B26='0'), False, False, 'KYTY_FIX_B26=0 - a family since S3b (RC7, item 245 (a))'),
        ('pcw_2', dict(KYTY_FIX_B26='1'), False, False, 'KYTY_FIX_B26=1 on an S6 arm (RC7)')):
    (fo, _), (so, _) = S.env_rows(S.SPEC[tag], env_for(S.SPEC[tag], **extra))
    ok &= case('B env %s: family %s strict %s' % (label, want_fam, want_strict), fo == want_fam and so == want_strict)
ok &= case('B env families: KYTY_ASYNC_ KYTY_PIPELINE_ KYTY_SHADER_ KYTY_S_ KYTY_DUMP_ + KYTY_CACHE_MODE KYTY_CS_PRETRANSLATE',
           S.in_family('KYTY_ASYNC_HOLD_FRAME') and S.in_family('KYTY_PIPELINE_CACHE') and S.in_family('KYTY_SHADER_PREPARE')
           and S.in_family('KYTY_S_PCW') and S.in_family('KYTY_DUMP_GCN') and S.in_family('KYTY_CACHE_MODE')
           and S.in_family('KYTY_CS_PRETRANSLATE') and not S.in_family('KYTY_AV_TRACE') and not S.in_family('KYTY_SALT')
           and S.in_family('KYTY_FIX_B26') and not S.in_family('KYTY_FIXB26'))

# ================================================================================================ 3 scan and counters
L = t_lines('lvl', [(16000, dict(skip=1, ev=[SKIP(8)])), (16000, dict(held=1)), (16000, {})],
            tail=['FrameTrace: n=99 dt_us='])
s = sc(L, 'c3')
eg, end, fi = lv(s)
ok &= case('C1 locate: entry group, first scene frame = draws >= 100 after the entry line (rows with draws >= 100 before '
           'the entry are not it)', s['rows'][fi][0] == 7 and eg == 5 and end == len(s['rows']))
ok &= case('C2 counters read from FrameTrace-x by n: skip 1 / held 1 / held 0', S.xget(s, fi + 1, 0) == 1 and
           S.xget(s, fi + 2, 1) == 1 and S.xget(s, fi + 3, 1) == 0 and S.held(s, fi + 2) and not S.held(s, fi + 3))
ok &= case('C3 a torn FrameTrace line is counted and is an identity FAIL', s['torn'] == 1 and dict(
    (n, o) for n, o, d in S.identities(s, dict(present=True, shaders=0), 'T'))['torn FrameTrace rows = 0'] is False)
s3b = sc(t_lines('lvl', [(16000, dict(bad=1)), (16000, {})]), 'c3b')
ok &= case('C3b skc_bad read from the scan (printed 1)', dict((n, d) for n, o, d in S.identities(
    s3b, dict(present=True, shaders=0), 'T'))['info skc_bad (unreachable by code, RC5; printed, no control)'] == 1)
s3c = sc(scene('lvl', [(16000, {})], header=HEADER_T, pre_entry=[]) [:0] + HEADER_T + [FT(1, 20000, 5), FX(1), START('lvl'),
                                                                                       FT(2, 20000, 99), FX(2),
                                                                                       FT(3, 30000, 100), FX(3),
                                                                                       FT(4, 16000, 3000), FX(4),
                                                                                       START('other'), FT(5, 16000), FX(5),
                                                                                       FT(6, 16000), FX(6)], 'c3c')
eg3, end3, fi3 = lv(s3c)
ok &= case('C3c draws 99 is not the first scene frame, draws 100 is; a later start line ends the rows of the scene',
           s3c['rows'][fi3][0] == 3 and end3 == 4)
ok &= case('C4 header lines: queued (R, G, C, skipped), created ms, ready, startup wait ms, loaded bytes',
           s['queued'] == (100, 1, 1, 41) and s['created_ms'] == 400 and s['ready'] == (100, 100, 41) and
           s['waited_ms'] == 77 and s['dload'] == [90000])
s2 = sc(t_lines('lvl', rows_ok(3), nox=(9,)), 'c5')
idn = dict((n, (o, d)) for n, o, d in S.identities(s2, dict(present=True, shaders=0), 'T'))
ok &= case('C5 a row without FrameTrace-x -> identity FAIL', idn['rows without FrameTrace-x or a field = 0'][0] is False)
L6 = t_lines('lvl', rows_ok(3))
L6 = [x.replace(' skc_held_inc=0', '') if x.startswith('FrameTrace-x: n=9 ') else x for x in L6]
s6 = sc(L6, 'c6')
idn = dict((n, (o, d)) for n, o, d in S.identities(s6, dict(present=True, shaders=0), 'T'))
ok &= case('C6 a FrameTrace-x without the skc_held_inc field -> identity FAIL',
           idn['rows without FrameTrace-x or a field = 0'][0] is False)
s7 = sc(t_lines('lvl', [(16000, {}), (16000, {})]) + [FT(11, 16000), FX(11)], 'c7')
idn = dict((n, (o, d)) for n, o, d in S.identities(s7, dict(present=True, shaders=0), 'T'))
ok &= case('C7 a gap of n -> identity FAIL', idn['gaps of n = 0'][0] is False)


def mem_ident(nskip, held_sum, held_lines, frames, cls='M', hk=0, bad=0, avtrace=0):
    rows = [(i + 1, 16000, 3000, 0, i) for i in range(4)]
    x = {1: (nskip, held_sum, hk, bad), 2: (0, 0, 0, 0), 3: (0, 0, 0, 0), 4: (0, 0, 0, 0)}
    skips = [(1, frames[i % len(frames)] if frames else None, 'a', 'b', 1) for i in range(nskip)]
    s = S.new_scan()
    s.update(rows=rows, x=x, skips=skips, held_lines=held_lines, avtrace=avtrace)
    return dict((n, (o, d)) for n, o, d in S.identities(s, dict(present=True, shaders=0), cls))


i1 = mem_ident(199999, 3, 3, [1, 2, 3])
i2 = mem_ident(200000, 3, 3, [1, 2, 3])
ok &= case('C8 T-1 at 199 999 lines holds and is checked; at 200 000 lines not applicable (None)',
           i1['T-1 sum skc_ap_skip = skipped-draw lines'][0] is True and i2['T-1 sum skc_ap_skip = skipped-draw lines'][0] is None)
ok &= case('C9 T-6 below 200 000 lines: 3 distinct frames = 3 held; at 200 000 lines not applicable',
           i1['T-6 distinct frame= of skipped draws = sum skc_held_inc (main)'][0] is True and
           i2['T-6 distinct frame= of skipped draws = sum skc_held_inc (main)'][0] is None)
ok &= case('C10 T-6 +1 (4 distinct frames, 3 held) -> FAIL (RC5)',
           mem_ident(4, 3, 3, [1, 2, 3, 4])['T-6 distinct frame= of skipped draws = sum skc_held_inc (main)'][0] is False)
ok &= case('C11 T-6 -1 (2 distinct frames, 3 held) -> FAIL',
           mem_ident(4, 3, 3, [1, 2])['T-6 distinct frame= of skipped draws = sum skc_held_inc (main)'][0] is False)
ok &= case('C12 T-2: 64 held and 64 lines; 65 held and 64 lines -> hold; 65 held and 65 lines -> FAIL',
           mem_ident(0, 64, 64, [])['T-2 min(64, sum skc_held_inc) = flip held lines'][0] is True and
           mem_ident(0, 65, 64, [])['T-2 min(64, sum skc_held_inc) = flip held lines'][0] is True and
           mem_ident(0, 65, 65, [])['T-2 min(64, sum skc_held_inc) = flip held lines'][0] is False)
ok &= case('C13 T-1 and T-6 hold on 3 lines, 3 frames, 3 held', mem_ident(3, 3, 3, [1, 2, 3])[
    'T-1 sum skc_ap_skip = skipped-draw lines'][0] is True and mem_ident(3, 3, 3, [1, 2, 3])[
    'T-6 distinct frame= of skipped draws = sum skc_held_inc (main)'][0] is True)
s_off = S.new_scan()
s_off.update(rows=[(1, 1, 1, 0, 1)], x={1: (2, 0, 0, 0)}, skips=[(0, 1, 'a', 'b', 1)] * 3)
ok &= case('C14 T-1 3 lines vs sum 2 -> FAIL', dict((n, o) for n, o, d in S.identities(
    s_off, dict(present=True, shaders=0), 'M'))['T-1 sum skc_ap_skip = skipped-draw lines'] is False)
ok &= case('C15 sum skc_held = 1 -> FAIL (RC5)', mem_ident(0, 0, 0, [], hk=1)['sum skc_held (skip-ceil holds) = 0'][0] is False
           and mem_ident(0, 0, 0, [], hk=0)['sum skc_held (skip-ceil holds) = 0'][0] is True)
ok &= case('C16 skc_bad 1 is printed, never a FAIL (RC5: unreachable)', mem_ident(0, 0, 0, [], bad=1)[
    'info skc_bad (unreachable by code, RC5; printed, no control)'] == (None, 1))
ok &= case('C17 null control of an M arm: one AvTrace line -> FAIL; 0 -> PASS',
           mem_ident(0, 0, 0, [], avtrace=1)['null control M: 0 AvTrace / ShaderRegister / ShaderFirstUse lines'][0] is False
           and mem_ident(0, 0, 0, [])['null control M: 0 AvTrace / ShaderRegister / ShaderFirstUse lines'][0] is True)

for post, want, label in (([(16000, dict(skip=1, ev=[SKIP(8)])), (16000, dict(held=1)), (16000, {})], 0, 'the next row held'),
                          ([(16000, dict(skip=1, ev=[SKIP(8)])), (16000, {}), (16000, dict(held=1)), (16000, {})], 0,
                           'held through one row'),
                          ([(16000, dict(skip=1, ev=[SKIP(8)])), (16000, {}), (16000, {}), (16000, dict(held=1))], 1,
                           'neither of the two next rows held (violation)')):
    d = dict((n, dd) for n, o, dd in S.identities(sc(t_lines('lvl', post), 'ss'), dict(present=True, shaders=0), 'T'))
    ok &= case('C17b shown_skip +-2: %s -> %d (printed, secondary)' % (label, want),
               d['info shown_skip by the +-2 rows rule (secondary to T-6, RC5)'] == want)
# T-3 / T-4 (S0 4.5 (14))
s8 = sc(t_lines('lvl', [(16000, dict(ev=[SH(5, 10, 10), SH(6, 10, 10)]))]), 'c8')
for nsh, want in ((2, True), (1, False), (3, False)):
    d = dict((n, o) for n, o, _ in S.identities(s8, dict(present=True, shaders=nsh), 'T'))
    ok &= case('C18 T-3 AvTrace shader 2 vs stdout %d -> %s' % (nsh, want),
               d['T-3 AvTrace: shader lines = stdout Shaders: lines'] is want)
d = dict((n, o) for n, o, _ in S.identities(s8, dict(present=False, shaders=0), 'T'))
ok &= case('C19 T-3 without the emulator stdout -> FAIL', d['T-3 AvTrace: shader lines = stdout Shaders: lines'] is False)
s8b = sc(t_lines('lvl', rows_ok(2)), 'c8b')
d = dict((n, o) for n, o, _ in S.identities(s8b, dict(present=False, shaders=0), 'T'))
ok &= case('C19b T-3 with 0 AvTrace shader lines and no stdout -> FAIL (the stdout must be there)',
           d['T-3 AvTrace: shader lines = stdout Shaders: lines'] is False)
for g, c, want in ((1, 1, True), (2, 1, False), (0, 1, False), (1, 2, False)):
    hdr = [QUEUED(100, g, c), GFX(300, 'precache'), CS(300, 'precache')]
    s9 = sc(t_lines('lvl', rows_ok(2), header=hdr), 'c9')
    d = dict((n, o) for n, o, _ in S.identities(s9, dict(present=True, shaders=0), 'T'))
    ok &= case('C20 T-4 2 precache lines vs G %d + C %d -> %s' % (g, c, want),
               d['T-4 AvTrace pipeline precache lines = G + C queued'] is want)
s10 = sc(t_lines('lvl', rows_ok(2), header=[GFX(300, 'precache')]), 'c10')
ok &= case('C21 T-4 without a queued line -> FAIL', dict((n, o) for n, o, _ in S.identities(
    s10, dict(present=True, shaders=0), 'T'))['T-4 AvTrace pipeline precache lines = G + C queued'] is False)

# ================================================================================================ 4 series, gaps, readings
H = dict(held=1)


def fz(post, first=None, reading=1, attr=False, header=None, name='fz'):
    s = sc(t_lines('lvl', post, first, header=header), name)
    eg, end, fi = lv(s)
    return S.freeze(s, fi, end, S.assign_prep(s), attr, reading), s, fi


f, s, fi = fz([(16000, {}), (30000, H), (40000, {}), (16000, {})])
x = f['series']
ok &= case('D1 a series of length 1: gap = its dt + the next row dt (70 000); closed', len(x) == 1 and x[0]['flips'] == 1
           and x[0]['gap_us'] == 70000 and x[0]['closed'] and x[0]['n0'] == 9)
f, s, fi = fz([(16000, {}), (30000, H), (40000, H)])
ok &= case('D2 a series to the end of the log: gap = sum of its rows (70 000), open', len(f['series']) == 1 and
           f['series'][0]['gap_us'] == 70000 and not f['series'][0]['closed'])
post = [(16000, {}) for _ in range(598)] + [(16000, H), (16000, H), (16000, {})]
f, s, fi = fz(post)
ok &= case('D3 a series starting at the 599th row after the first frame is in the window, at the 600th in the hold',
           f['series'][0]['part'] == 'window' and f['window']['rows'] == 599 and f['hold']['rows'] == 2)
post = [(16000, {}) for _ in range(599)] + [(16000, H), (16000, {})]
f, s, fi = fz(post)
ok &= case('D4 a series at the 600th row is a hold series; held flips counted in the hold',
           f['series'][0]['part'] == 'hold' and f['hold']['held'] == 1 and f['window']['held'] == 0)
f1, s, fi = fz([(16000, H), (16000, {})], first=(500000, H), reading=1)
f2, _, _ = fz([(16000, H), (16000, {})], first=(500000, H), reading=2)
ok &= case('D5 a held first scene frame: reading 1 (letter) starts the series at it (gap 532 000, held 2), reading 2 '
           'from the next row (gap 32 000, held 1)', f1['series'][0]['gap_us'] == 532000 and f1['window']['held'] == 2
           and f2['series'][0]['gap_us'] == 32000 and f2['window']['held'] == 1 and f1['series'][0]['n0'] == 7)
f1, s, fi = fz([(16000, H), (16000, {})], first=(500000, {}), reading=1)
ok &= case('D6 a first scene frame that is not held: both readings start after it',
           f1['series'][0]['n0'] == 8 and f1['window']['held'] == 1)
f, s, fi = fz([(16000, H), (20000, {}), (16000, H), (16000, {})])
ok &= case('D7 two series one presented row apart: two series, the row between closes the first (gap 36 000 / 32 000)',
           [x['gap_us'] for x in f['series']] == [36000, 32000])
for gap, w100, w1s in ((99999, 0, 0), (100000, 1, 0), (999999, 1, 0), (1000000, 1, 1)):
    f, s, fi = fz([(gap - 10000, H), (10000, {})])
    ok &= case('D8 visible gap %d -> >= 100 ms %d, >= 1 s %d' % (gap, w100, w1s),
               f['window']['gap100'] == w100 and f['window']['gap1s'] == w1s)
for dt, w100, w1s in ((99999, 0, 0), (100000, 1, 0), (999999, 1, 0), (1000000, 1, 1)):
    f, s, fi = fz([(dt, {}), (16000, {})])
    ok &= case('D9 a presented row dt %d -> dt >= 100 ms %d, presented %d, >= 1 s %d' % (dt, w100, w100, w1s),
               f['window']['dt100'] == w100 and f['window']['shown100'] == w100 and f['window']['dt1s'] == w1s
               and f['window']['shown1s'] == w1s)
f, s, fi = fz([(150000, H), (16000, {})])
ok &= case('D10 a held row with dt >= 100 ms counts in dt100 but not as presented', f['window']['dt100'] == 1
           and f['window']['shown100'] == 0)
f, s, fi = fz([(16000, {}), (30000, H), (40000, {}), (16000, H), (16000, {}), (16000, {})])
ok &= case('D11 T-5 partition holds (gaps + presented rows outside series = sum dt of the domain)',
           f['T5'][0] == f['T5'][1] and f['T5'][1] == 16000 + 30000 + 40000 + 16000 + 16000 + 16000)
# gap_pipe (RC4): rows >= 100 ms of class PRIO / PCW in the series (closing row included) are subtracted
post = [(300000, dict(held=1, ev=[PRIO(200000)])), (300000, dict(ev=[PRIO(200000)])), (16000, dict(ev=[PRIO(200000)])),
        (16000, {})]
f, s, fi = fz(post)
x = f['series'][0]
ok &= case('D12 gap_pipe = gap - PRIO rows (the held row and the closing row, both robust PRIO): 600 000 - 600 000 = 0',
           x['gap_us'] == 600000 and x['gap_pipe_us'] == 0)
post = [(300000, dict(held=1, ev=[PRIO(200000)])), (300000, dict(cg=200000)), (16000, {})]
f, s, fi = fz(post)
ok &= case('D13 a GPUTHR closing row is not subtracted; PRIO by group i only is not robust -> 600 000 kept',
           f['series'][0]['gap_pipe_us'] == 600000)
post = [(300000, dict(held=1)), (300000, dict(ev=[DSAVE(5)])), (16000, {})]
f, s, fi = fz(post)
ok &= case('D14 a PCW row in the series (a driver write in group i or i+1) is NOT subtracted by the governing gap_pipe '
           '(item 250 (g)(2): 600 000 kept); the second reading (v)(2) before item 250 subtracts it -> 0',
           f['series'][0]['gap_pipe_us'] == 600000 and f['series'][0]['gap_pipe_old_us'] == 0
           and f['window']['pipe100'] == 1 and f['window']['pipe100_old'] == 0)
post = [(1200000, dict(held=1, ev=[DSAVE(5)])), (16000, {})]
f, s, fi = fz(post, attr=True)
ok &= case('D14b RC3: a held PCW row of 1.2 s in a series -> governing gap_pipe 1 216 000 >= 1 s (pipe1s 1, attributed 1); '
           '(v)(2) before item 250 16 000 (pipe1s_old 0, attributed_old 0)', f['series'][0]['gap_pipe_us'] == 1216000 and
           f['window']['pipe1s'] == 1 and f['window']['pipe1s_old'] == 0 and S.attributed(f, True, 1000000) == 1
           and S.attributed_old(f, True, 1000000) == 0)
post = [(1200000, dict(held=1, ev=[DSAVE(5), PRIO(700000)])), (16000, dict(ev=[PRIO(700000)])), (16000, {})]
f, s, fi = fz(post, attr=True)
ok &= case('D14c a row that is PCW and stalls stays PCW (PCW before PRIO): not subtracted by the governing gap_pipe',
           f['series'][0]['gap_pipe_us'] == 1216000)
post = [(1200000, {}), (16000, dict(ev=[DSAVE(5)]))]
f, s, fi = fz(post, attr=True)
ok &= case('D14d RC3: a presented PCW row of 1.2 s with attribution "not" -> attributed >= 1 s 1, of them PCW 1; the old '
           'reading 0; not in the not attributed rows', [x['cls'] for x in f['long']] == ['PCW'] and f['long'][0]['attr'] == 'not'
           and S.attributed(f, True, 1000000) == 1 and S.attributed_pcw(f, True, 1000000) == 1
           and S.attributed_old(f, True, 1000000) == 0 and S.unattributed(f, True, 1000000)['n'] == 0)
ok &= case('D14e the PCW count and the old reading are undetermined (None) without the attribution',
           S.attributed_pcw(f, False, 1) is None and S.attributed_old(f, False, 1) is None and S.unattributed(f, False, 1) is None)
post = [(1300000, {}), (1300000, dict(cg=900000)), (1300000, dict(ev=[PRIO(700000)])), (16000, dict(ev=[PRIO(700000)])),
        (16000, {})]
f, s, fi = fz(post, attr=True)
u = S.unattributed(f, True, 1000000)
ok &= case('D14f RC8: presented rows of 1.3 s WAIT, GPUTHR, PRIO -> not attributed 3 (WAIT 1, GPUTHR 1, PRIO 1); attributed 0',
           u == dict(n=3, series=0, WAIT=1, GPUTHR=1, PRIO=1) and S.attributed(f, True, 1000000) == 0
           and 'WAIT 1, GPUTHR 1, PRIO 1' in S.fmt_unattr(u))
post = [(1100000, dict(held=1, ev=[PRIO(700000)])), (16000, dict(ev=[PRIO(700000)])), (16000, {})]
f, s, fi = fz(post, attr=True)
ok &= case('D14g RC8: a series of gap 1 116 000 whose PRIO row is subtracted (gap_pipe 16 000) is printed as not '
           'attributed series 1', S.unattributed(f, True, 1000000)['series'] == 1 and S.attributed(f, True, 1000000) == 0)
post = [(1100000, dict(held=1)), (16000, {})]
f, s, fi = fz(post, attr=True)
ok &= case('D14g2 RC8 edge: a series of gap 1 116 000 with no PRIO row (gap_pipe 1 116 000 >= 1 s) is attributed, '
           'NOT a not attributed series', S.unattributed(f, True, 1000000)['series'] == 0 and
           S.attributed(f, True, 1000000) == 1)
f, s, fi = fz([(999999, {}), (16000, {})], attr=True)
ok &= case('D14h RC8 edge: a WAIT row of 999 999 is not counted at 1 s, counted at 100 ms',
           S.unattributed(f, True, 1000000)['n'] == 0 and S.unattributed(f, True, 100000)['n'] == 1)
post = [(1100000, dict(held=1, ev=[PRIO(700000)])), (16000, dict(ev=[PRIO(700000)])), (16000, {})]
f, s, fi = fz(post)
ok &= case('D15 >= 1 s by gap 1 116 000 but gap_pipe 16 000 -> pipe1s 0, gap1s 1', f['window']['gap1s'] == 1 and
           f['window']['pipe1s'] == 0 and f['window']['pipe100'] == 0)
post = [(30000, dict(held=1, ev=[GFX(20000), GFX(19999)])), (16000, {})]
f, s, fi = fz(post)
ok &= case('D17 async gfx in the series groups: count 2, cold 1 (20 000 is cold), us 39 999', f['series'][0]['async_n'] == 2
           and f['series'][0]['async_cold'] == 1 and f['series'][0]['async_us'] == 39999)
post = [(100000, dict(held=1, ev=[PRIO(50000)])), (16000, dict(ev=[PRIO(50000)])), (16000, {})]
f, s, fi = fz(post)
ok &= case('D18 a PRIO row of exactly 100 000 us in the series is subtracted: gap_pipe 16 000', f['series'][0]['gap_pipe_us'] == 16000)

# ================================================================================================ 5 classes and PREP
def one_class(post, idx=0, attr=True, header=None, name='cl'):
    s = sc(t_lines('lvl', post, header=header), name)
    eg, end, fi = lv(s)
    i = fi + 1 + idx
    return S.classify(s, i, S.assign_prep(s), attr), s, i


c, s, i = one_class([(200000, dict(ev=[DSAVE(5)]))])
ok &= case('E1 PCW: a driver write in group i', c[0] == 'PCW')
c, s, i = one_class([(200000, {}), (16000, dict(ev=[RSAVE(5)]))])
ok &= case('E2 PCW: a recipe write in group i+1', c[0] == 'PCW')
c, s, i = one_class([(200000, {}), (16000, {}), (16000, dict(ev=[DSAVE(5)]))], attr=False)
ok &= case('E3 a write in group i+2 is not PCW', c[0] != 'PCW')
c, s, i = one_class([(200000, dict(ev=[DSAVE(5), PRIO(150000)])), (16000, dict(ev=[PRIO(150000)]))])
ok &= case('E4 PCW stands before PRIO', c[0] == 'PCW')
c, s, i = one_class([(200000, dict(ev=[PRIO(100000)])), (16000, dict(ev=[PRIO(100000)]))], attr=False)
ok &= case('E5 PRIO robust: stall dt/2 in group i and in group i+1, cpu_gpu 0 -> PRIO', c[0] == 'PRIO' and c[5] == 100000
           and c[6] == 100000)
c, s, i = one_class([(200000, dict(ev=[PRIO(99999)])), (16000, dict(ev=[PRIO(100000)]))], attr=False)
ok &= case('E6 stall dt/2 - 1 in group i -> not PRIO (WAIT)', c[0] == 'WAIT')
c, s, i = one_class([(200000, dict(ev=[PRIO(100000)])), (16000, dict(ev=[PRIO(99999)]))], attr=False)
ok &= case('E7 stall dt/2 - 1 in group i+1 -> not PRIO (RC8: both conventions)', c[0] == 'WAIT')
c, s, i = one_class([(200000, dict(cg=99999, ev=[PRIO(100000)])), (16000, dict(ev=[PRIO(100000)]))], attr=False)
ok &= case('E8 cpu_gpu dt/2 - 1 with robust stalls -> PRIO', c[0] == 'PRIO')
c, s, i = one_class([(200000, dict(cg=100000, ev=[PRIO(100000)])), (16000, dict(ev=[PRIO(100000)]))], attr=False)
ok &= case('E9 cpu_gpu dt/2 -> GPUTHR, not PRIO', c[0] == 'GPUTHR')
c, s, i = one_class([(200000, dict(cg=99999))], attr=False)
ok &= case('E10 cpu_gpu dt/2 - 1, no stall -> WAIT', c[0] == 'WAIT')
c, s, i = one_class([(200000, dict(ev=[PRIO(-1), PRIO(100000)])), (16000, dict(ev=[PRIO(100000)]))], attr=False)
ok &= case('E11 a stall line without us (-1) adds nothing', c[0] == 'PRIO' and c[5] == 100000)
# SHADER and PREP (attribution on a T arm)
c, s, i = one_class([(200000, dict(ev=[SH(5, 50000, 50001)]))])
ok &= case('E12 dt - PREP = 99 999 -> SHADER (PREP = translate + compile = 100 001); partly (PREP >= dt/2)',
           c[0] == 'SHADER' and c[1] == 'SHADER-partly' and c[2] == 100001 and c[3] == 100001 and c[4] == 0)
c, s, i = one_class([(200000, dict(ev=[SH(5, 50000, 50000)]))])
ok &= case('E13 dt - PREP = 100 000 -> not SHADER (attribution "not"), PREP = dt/2', c[0] == 'WAIT' and c[1] == 'not')
c, s, i = one_class([(300000, dict(ev=[SH(5, 100000, 49999), GFX(100000, 'none')]))])
ok &= case('E14 PREP 249 999 of dt 300 000: SHADER (dt - PREP < 100 000), partly; TR 149 999, PL 100 000 (sync gfx)',
           c[1] == 'SHADER-partly' and c[3] == 149999 and c[4] == 100000)
c, s, i = one_class([(300000, dict(ev=[SH(5, 100000, 49999), GFX(100000, 'none')]))], attr=False)
ok &= case('E15 the same frame on a non-T arm: attribution undetermined, class by the rest (RC7)', c[1] == 'undetermined'
           and c[0] == 'WAIT')
c, s, i = one_class([(150000, dict(ev=[SH(5, 40000, 35000)]))])
ok &= case('E13b PREP = dt/2 exactly (75 000 of 150 000): SHADER and partly', c[1] == 'SHADER-partly')
c, s, i = one_class([(150000, dict(ev=[SH(5, 40000, 34999)]))])
ok &= case('E13c PREP = dt/2 - 1: SHADER, not partly', c[1] == 'SHADER')
c, s, i = one_class([(250000, dict(ev=[SH(5, 1, 1)]))])
ok &= case('E16 PREP small, no skip, no async: not SHADER', c[1] == 'not')
c, s, i = one_class([(250000, dict(ev=[SKIP(9)]))])
ok &= case('E17 a skipped-draw line in group i -> SHADER (burden on the route, RC6(3))', c[0] == 'SHADER' and c[1] == 'SHADER')
c, s, i = one_class([(16000, dict(ev=[SKIP(9)])), (16000, {}), (250000, {})], idx=2)
ok &= case('E18 a skipped draw in group i-2 -> SHADER', c[0] == 'SHADER')
c, s, i = one_class([(16000, dict(ev=[SKIP(9)])), (16000, {}), (16000, {}), (250000, {})], idx=3)
ok &= case('E19 a skipped draw in group i-3 -> not SHADER', c[0] != 'SHADER')
c, s, i = one_class([(250000, {}), (16000, dict(ev=[GFX(1000)]))])
ok &= case('E20 an async gfx completion in group i+1 -> SHADER', c[0] == 'SHADER')
c, s, i = one_class([(250000, {}), (16000, {}), (16000, dict(ev=[GFX(1000)]))])
ok &= case('E21 an async gfx completion in group i+2 -> not SHADER', c[0] != 'SHADER')
c, s, i = one_class([(250000, {}), (16000, dict(ev=[GFX(1000, 'precache'), CS(1000)]))])
ok &= case('E22 precache gfx and async cs completions are not "pipeline gfx async" -> not SHADER', c[0] != 'SHADER')
# PREP assignment (RC16): a line of group g goes to the largest dt among rows g-1 .. g+2
c, s, i = one_class([(16000, dict(ev=[SH(5, 60000, 60000)])), (16000, {}), (200000, {})], idx=2)
ok &= case('E23 an AvTrace line in group i-2 is assigned to row i (largest dt of i-3 .. i): PREP 120 000', c[2] == 120000)
c, s, i = one_class([(200000, {}), (16000, dict(ev=[SH(5, 60000, 60000)]))])
ok &= case('E24 an AvTrace line in group i+1 is assigned to row i', c[2] == 120000)
c, s, i = one_class([(200000, {}), (16000, {}), (16000, dict(ev=[SH(5, 60000, 60000)]))])
ok &= case('E25 an AvTrace line in group i+2 is not assigned to row i', c[2] == 0)
s = sc(t_lines('lvl', [(200000, {}), (16000, dict(ev=[SH(5, 60000, 60000)])), (300000, {})]), 'e26')
eg, end, fi = lv(s)
pr = S.assign_prep(s)
ok &= case('E26 one line, one row: the larger dt (row i+2, 300 000) takes it, row i gets 0; counted once',
           pr.get(fi + 1, [0, 0]) == [0, 0] and pr.get(fi + 3) == [120000, 0] and sum(sum(v) for v in pr.values()) == 120000)
s = sc(t_lines('lvl', [(200000, {}), (16000, dict(ev=[SH(5, 60000, 60000)])), (200000, {})]), 'e27')
eg, end, fi = lv(s)
pr = S.assign_prep(s)
ok &= case('E27 a tie of dt: the earliest row takes the line', pr.get(fi + 1) == [120000, 0] and fi + 3 not in pr)
c, s, i = one_class([(200000, dict(ev=[SH(5, 1000, 2000), EMIT(90000)]))])
ok &= case('E28 compile_us and shader-emit are not added (PREP 3 000)', c[2] == 3000)
c, s, i = one_class([(200000, dict(ev=[GFX(1000, 'async'), GFX(2000, 'precache'), GFX(4000, 'none'), CS(8000, 'async'),
                                       CS(16000, 'sync'), CS(32000, 'precache'), CS(64000, 'waited'), LOAD(128000)]))])
ok &= case('E29 PREP kinds: gfx without suffix, cs sync, waited_us, shader-cache load (4 000 + 16 000 + 64 000 + 128 000); '
           'not async, not precache', c[2] == 212000 and c[4] == 212000 and c[3] == 0)
s = sc(t_lines('lvl', [(16000, dict(ev=[GFX(10, 'async'), GFX(20, 'precache'), GFX(40, 'none'), CS(80, 'async'),
                                       CS(160, 'sync'), CS(320, 'precache'), CS(640, 'waited')]))]), 'e30')
ok &= case('E30 pipeline kinds parsed: gfx async / precache / none, cs async / sync / precache / waited',
           [(e[1], e[2], e[3]) for e in s['pipe'] if e[0] > 0] == [('gfx', 'async', 10), ('gfx', 'precache', 20), ('gfx', 'none', 40),
                                                       ('cs', 'async', 80), ('cs', 'sync', 160), ('cs', 'precache', 320),
                                                       ('cs', 'waited', 640)])
ok &= case('E31 in-game creations = gfx async + none, cs async + sync (not precache, not waited)',
           sorted(S.creations(s)) == [10, 40, 80, 160])
ok &= case('E32 creations after a group: only lines at or after it', S.creations(s, 10 ** 6) == [])

# ================================================================================================ 6 cold / warm, medians
for us, n, want in (([4999] * 10, 10, 'WARM'), ([5000] * 10, 10, 'WARM'), ([5001] * 10, 10, 'MID'),
                    ([19999] * 10, 10, 'MID'), ([20000] * 10, 10, 'COLD'), ([20000] * 9, 9, 'NOTHING')):
    ok &= case('F1 creations %d x %d -> %s' % (n, us[0], want), S.cold_class(us)[0] == want)
ok &= case('F2 median: odd middle, even mean of the two middles, empty None', S.med([3, 1, 2]) == 2 and
           S.med([1, 2, 3, 10]) == 2.5 and S.med([]) is None)
ok &= case('F3 the median decides, not the mean: 5 x 100 000 + 5 x 1 000 -> mean of 1 000 and 100 000 = 50 500 COLD',
           S.cold_class([100000] * 5 + [1000] * 5) == ('COLD', 50500.0))

# ================================================================================================ 7 S-early (RC11)
post = [(250000, dict(ev=[REG(5, 1000), SH(5, 100000, 100000), FIRST(5, 2000)])), (16000, {})]
s = sc(t_lines('lvl', post), 'g1')
eg, end, fi = lv(s)
f = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
e = S.early(s, f, fi, True)
ok &= case('G1 lead = FirstUse - min Register = 1 000 < cost PREP 200 000 -> short 1 of 1', e['known'] == 1 and
           e['short'] == 1 and e['events'][0]['lead'] == 1000 and e['events'][0]['cost'] == 200000)
post = [(250000, dict(ev=[FIRST(5, 900000), SH(5, 100000, 100000)])), (16000, dict(ev=[REG(5, 500), REG(5, 1000)]))]
s = sc(t_lines('lvl', post), 'g2')
eg, end, fi = lv(s)
f = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
e = S.early(s, f, fi, True)
ok &= case('G2 FirstUse before Register in the text, two Registers of one hash (min 500): lead 899 500 >= cost -> short 0',
           e['events'][0]['lead'] == 899500 and e['short'] == 0 and e['known'] == 1)
post = [(250000, dict(ev=[FIRST(5, 900), SH(5, 100000, 100000)])), (16000, {})]
s = sc(t_lines('lvl', post), 'g3')
eg, end, fi = lv(s)
f = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
e = S.early(s, f, fi, True)
ok &= case('G3 a hash without registration: lead unknown, not in the denominator', e['known'] == 0 and e['share'] is None)
ok &= case('G4 S-early on a non-T arm: undetermined (None)', S.early(s, f, fi, False) is None)
post = [(250000, dict(ev=[REG(5, 1000), SH(5, 100000, 100000), FIRST(5, 201000)])), (16000, {})]
s = sc(t_lines('lvl', post), 'g4b')
eg, end, fi = lv(s)
e = S.early(s, S.freeze(s, fi, end, S.assign_prep(s), True, 1), fi, True)
ok &= case('G4b lead = cost (200 000) is not short (lead < cost)', e['known'] == 1 and e['short'] == 0)
post = [(300000, dict(held=1, ev=[SKIP(8, 5, 6), GFX(250000)])), (16000, dict(ev=[REG(5, 10), REG(6, 20), FIRST(5, 100),
                                                                                    FIRST(6, 50)]))]
s = sc(t_lines('lvl', post), 'g5')
eg, end, fi = lv(s)
f = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
e = S.early(s, f, fi, True)
ser = [x for x in e['events'] if x['kind'] == 'series']
ok &= case('G5 a series with gap_pipe >= 100 ms is one event: cost = async us 250 000, lead = min over its pair 30',
           len(ser) == 1 and ser[0]['cost'] == 250000 and ser[0]['lead'] == 30)

# ================================================================================================ 8 arms end to end
IX = dict(any={'%016x' % 1, '%016x' % 2, '%016x' % 3}, cur={'%016x' % 1, '%016x' % 2}, pairs={'%016x/%016x' % (1, 2)})
# a cold T arm (C1-like): entry, skip pair (1,2) and (1,3), new permutation, new recipe after the entry
cold_post = [(16000, dict(skip=1, ev=[SKIP(8, 1, 2), SH(7, 100, 100)])), (16000, dict(held=1)),
             (16000, dict(skip=1, ev=[SKIP(10, 1, 3), RSAVE(101)])), (16000, dict(held=1)), (16000, {})]
cold_post += [(16000, dict(ev=[GFX(30000)])) for _ in range(10)]
mkarm('c1_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1)
r = arm('c1_0', ix=IX)
ok &= case('H1 a clean T arm: PASS, attribution determined, cold gate (perm 1, recipe +1, skip 2)', r['fail'] == [] and
           r['attr_ok'] and r['gates']['cold'] and r['gates']['perm_after'] == 1 and r['gates']['rec_new_after'] == 1
           and r['gates']['skip_after'] == 2)
ok &= case('H2 the snap0 pairs (RC12): 2 skipped pairs, both shaders in snap0 (any) 2, current 1, in recipes 1',
           r['snap_pairs'] == dict(pairs=2, both_any=2, both_cur=1, recipe=1))
ok &= case('H3 creations of the arm: 10 x 30 000 -> COLD (letter); after the entry the same', r['create']['all'][0] == 'COLD'
           and r['create']['all_n'] == 10 and r['create']['after'][0] == 'COLD')
ok &= case('H4 attributed (item 241 (v)(2)) on a T arm: numbers, not None', r['att100'] == 0 and r['att1s'] == 0)
s = sc(t_lines('lvl', [(150000, dict(held=1, skip=1, ev=[SKIP(8)])), (16000, {})]), 'h4b')
eg, end, fi = lv(s)
fzz = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
ok &= case('H4b a held SHADER row >= 100 ms is not counted as a presented row; its series (gap_pipe 166 000) is: 1',
           S.attributed(fzz, True, 100000) == 1)
s = sc(t_lines('lvl', [(300000, dict(held=1, skip=1, ev=[SKIP(8), DSAVE(5)])), (16000, {}), (16000, {})]), 'h4c')
eg, end, fi = lv(s)
fzz = S.freeze(s, fi, end, S.assign_prep(s), True, 1)
ok &= case('H4c a series of gap 316 000 whose held row is PCW (before SHADER): governing gap_pipe 316 000 -> 1 attributed '
           'series (item 250 (g)); (v)(2) before item 250: gap_pipe 16 000 -> 0', S.attributed(fzz, True, 100000) == 1
           and S.attributed_old(fzz, True, 100000) == 0)
ok &= case('H5 the first scene frame agrees with the inherited sc142.derive (identity row)', any(
    n.startswith('first scene frame') and o for n, o, d in r['ident']))
txt = '\n'.join(S.fmt_arm(r))
OUTS.append(txt)
ok &= case('H6 the arm text names PASS, the attribution, both readings and the gates', 'ARM c1_0 level shuriken_ninja_castle'
           in txt and ': PASS;' in txt and 'DETERMINED' in txt and 'reading 1' in txt and 'reading 2' in txt and 'gates:' in txt)
mkarm('c1_1', t_lines('jack_in_the_box', [(16000, dict(skip=1, ev=[SKIP(8)])), (16000, dict(held=1)), (16000, {})]),
      stdout_shaders=0)
r = arm('c1_1')
ok &= case('H7 no new permutation after the entry -> not cold (RC12); recipes +0 -> not cold', not r['gates']['cold'])
mkarm('c1_2', t_lines('cymbal_party_land', [(16000, dict(skip=1, ev=[SKIP(8), RSAVE(101)])), (16000, dict(held=1)),
                                          (16000, {})]), stdout_shaders=0)
ok &= case('H7b a skip and a new recipe but no new permutation after the entry -> not cold', not arm('c1_2')['gates']['cold'])
mkarm('c1_2', t_lines('cymbal_party_land', [(16000, dict(ev=[SH(7, 1, 1), RSAVE(101)])), (16000, {})]), stdout_shaders=1)
r = arm('c1_2')
ok &= case('H8 no skipped draw after the entry -> not cold', not r['gates']['cold'] and r['gates']['perm_after'] == 1)
mkarm('t2_01', t_lines('small_pot_lava', [(16000, dict(skip=1, ev=[SKIP(8), SH(7, 1, 1)])), (16000, dict(held=1)),
                                          (16000, {})], header=HEADER_T + [RSAVE(101)]), stdout_shaders=1)
r = arm('t2_01')
ok &= case('H9 a new recipe saved only BEFORE the entry line -> not cold', not r['gates']['cold']
           and r['gates']['rec_new_after'] == 0)
mkarm('t2_02', t_lines('spin_drill_natural_cave', [(16000, dict(skip=1, ev=[SKIP(8), SH(7, 1, 1), RSAVE(101)])),
                                                   (16000, dict(held=1)), (16000, {})]), stdout_shaders=2)
r = arm('t2_02')
ok &= case('H10 T-3 broken (1 AvTrace shader vs 2 Shaders:) -> FAIL and attribution undetermined, gate not cold (RC7)',
           any('T-3' in x for x in r['fail']) and not r['attr_ok'] and r['att100'] is None and not r['gates']['cold'])
# warm M arm
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), stdout_shaders=0)
r = arm('sw_m1')
ok &= case('H11 a clean M arm: PASS, attribution undetermined, warm gate (0 Shaders:, recipes 100 -> 100)', r['fail'] == []
           and not r['attr_ok'] and r['gates']['warm'] and r['att100'] is None and r['early'] is None)
mkarm('sw_m2', m_lines('voxel_world', [(16000, dict(ev=[RSAVE(101)]))]), stdout_shaders=0)
ok &= case('H12 a recipe added -> not warm', not arm('sw_m2')['gates']['warm'])
mkarm('sw_m3', m_lines('ice_iceberg', rows_ok(3)), stdout_shaders=1)
ok &= case('H13 a stdout Shaders: line -> not warm', not arm('sw_m3')['gates']['warm'])
mkarm('sw_m3', m_lines('ice_iceberg', [(16000, dict(ev=[SH(5, 1, 1)]))]), stdout_shaders=0)
r = arm('sw_m3')
ok &= case('H14 an AvTrace line on an M arm -> null control FAIL', any('null control' in x for x in r['fail']))
# admission rows
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js_for('sw_m2', env_over=dict(KYTY_ASYNC_PIPELINE_WAIT_US='900000')))
r = arm('sw_m2')
ok &= case('H15 KYTY_ASYNC_PIPELINE_WAIT_US in the json env -> admission FAIL (RC6)', any('families' in x for x in r['fail']))
for over, label in ((dict(binary_sha256='ee' * 32), 'another binary'), (dict(guest_args='-lvl x'), 'other guest args'),
                    (dict(gates='a=1'), 'gates not empty'), (dict(hold_s=110), 'hold 110'),
                    (dict(prereg=dict(path=PRED4, sha256='00' * 32)), 'another seal'),
                    (dict(binary_sha256=PBIN), 'the S6 binary on an S4 arm'),
                    (dict(prereg=dict(path='C:/x/01_s.md', sha256=PRED_SHA)), 'another seal path'),
                    (dict(attempts=[dict(label='attempt 1', outcome='ok', hold_s=120.0, hold_exit=None, ft_tail=1,
                                         pipeline_cache_off=True)]), 'pipeline-cache retry'),
                    (dict(attempts=[dict(label='attempt 1'), dict(label='attempt 2')]), 'two attempts'),
                    (dict(cmdline=['x', '--vulkan-validation', 'true']), 'validation on an S4 arm')):
    mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js_for('sw_m2', **over))
    r = arm('sw_m2')
    ok &= case('H16 admission FAIL: %s' % label, len([x for x in r['fail'] if x.startswith('admission')]) >= 1)
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js_for('sw_m2', env_over=dict(KYTY_REC=None)))
ok &= case('H17 no video -> admission FAIL', any('video' in x for x in arm('sw_m2')['fail']))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js_for('sw_m2', env_over=dict(KYTY_REC='C:/x/rec_sw_m1.mp4')))
ok &= case('H17b a video file of another tag -> admission FAIL', any('video' in x for x in arm('sw_m2')['fail']))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js_for('sw_m2', env_over=dict(KYTY_GPU_CHECKPOINTS='1')))
ok &= case('H18 KYTY_GPU_CHECKPOINTS -> admission FAIL', any('CHECKPOINTS' in x for x in arm('sw_m2')['fail']))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)))
ok &= case('H19 the same arm clean -> PASS', arm('sw_m2')['fail'] == [])
# cache protocol rows (RC1, RC12)
for key, val, label in (('restore_app', dict(expected=SNAP_APP, got='00' * 32), 'snap0 not reached'),
                        ('restore_app', dict(expected='00' * 32, got='00' * 32), 'another app source'),
                        ('restore_glc', dict(expected=SNAP_DRV, got='00' * 32), 'GLCache not at snap0_drv'),
                        ('restore_glc', dict(expected='00' * 32, got='00' * 32), 'another GLCache source on a full arm'),
                        ('return_app', dict(expected='16' * 32, got='00' * 32), 'the app return failed'),
                        ('return_glc', dict(expected='17' * 32), 'the GLCache return without a result'),
                        ('return_app', {}, 'the app return not recorded at all'),
                        ('installed_after', dict(sha='ee' * 32), 'the binary not back (after != before, RC1)'),
                        ('installed_after', BUILD, 'installed_after not a note (a bare string)'),
                        ('installed_before', {}, 'no installed_before (RC1)'),
                        ('installed_before', dict(sha='ab'), 'installed_before not a sha256'),
                        ('return_prev', {}, 'no return_prev_ok (RC2)'),
                        ('return_prev', dict(ok='0'), 'return_prev ok 0 (RC2)'),
                        ('man_launch_glc', {}, 'no man_launch_glc (RC10)'),
                        ('man_launch_glc', dict(sha='00' * 32), 'man_launch_glc != restore_glc.got (RC10)'),
                        ('man_post_glc', {}, 'a missing manifest after the arm'),
                        ('glc_pre_copy', {}, 'no GLCache copy before the arm')):
    mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', **{key: val}))
    ok &= case('H20 cache protocol FAIL: %s' % label, len([x for x in arm('sw_m2')['fail'] if x.startswith('admission')]) >= 1)
for over, label in ((dict(installed_before={}, installed_after={}), 'neither installed_before nor installed_after '
                      '(None = None is not a return)'),
                     (dict(installed_before=dict(sha='ab'), installed_after=dict(sha='ab')),
                      'installed_before = installed_after but not a sha256')):
    mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', **over))
    ok &= case('H20b RC1 edge: %s -> the binary row FAIL' % label,
               any(x.startswith('admission') and 'installed binary' in x for x in arm('sw_m2')['fail']))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', restore_glc=dict(expected=SNAP_DRV, got='00' * 32),
                                                           man_launch_glc=dict(sha='00' * 32)))
r = arm('sw_m2')
ok &= case('H20c GLCache not at snap0_drv while man_launch_glc = restore_glc.got (RC10 row clean) -> the restore of '
           'GLCache row FAIL alone', [x for x in r['fail'] if x.startswith('admission')] != [] and
           all('restore of GLCache' in x for x in r['fail'] if x.startswith('admission')))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj={})
ok &= case('H21 an empty cache json -> FAIL', len(arm('sw_m2')['fail']) >= 3)
Path(RM['s4'], 'runs_s', 'sw_m2.cache.json').unlink()
ok &= case('H22 no cache json -> FAIL (present row)', any('cache protocol json present' in x for x in arm('sw_m2')['fail']))
mkarm('c2_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1)
ok &= case('H23 C2 restores GLCache from glc_post of c1_0 (bb...) -> PASS', arm('c2_0')['fail'] == [])
mkarm('c2_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1,
      cj=cj_for('c2_0', restore_glc=dict(expected=SNAP_DRV, got=SNAP_DRV)))
ok &= case('H24 C2 restored to snap0_drv instead of the C1 post copy -> FAIL', any('GLCache' in x for x in arm('c2_0')['fail']))
mkarm('c1_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1, cj=cj_for('c1_0', glc_post_copy={}))
r1 = arm('c1_0')
r2 = arm('c2_0')
ok &= case('H25 C1 without its glc_post copy: C1 FAIL (a later arm restores it) and C2 cannot match', any(
    'glc_post' in x for x in r1['fail']) and len(r2['fail']) >= 1)
mkarm('c1_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1)
ok &= case('H26 a missing arm -> score_arm None', arm('c3_0') is None)
# RC17: the video frames are not an identity
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), glitch=(5, 0))
ok &= case('H27 video frames (5) far below the rows: no FAIL - video is a picture check (RC17)', arm('sw_m2')['fail'] == [])
REAL_FREEZE = S.freeze


def bad_freeze(*a):
    f = REAL_FREEZE(*a)
    f['T5'] = (f['T5'][0] + 1, f['T5'][1])
    return f


S.freeze = bad_freeze
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)))
r5 = arm('sw_m2')
S.freeze = REAL_FREEZE
ok &= case('H27b a broken T-5 partition (fault injected) -> identity FAIL of both readings', any(
    'T-5 partition (reading 1)' in x for x in r5['fail']) and any('T-5 partition (reading 2)' in x for x in r5['fail']))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), extra_stdout=['Cache test mode: prepare-cold (fresh driver namespace 1)'])
ok &= case('H28 Cache test mode in the stdout is counted', arm('sw_m2')['prep']['cache_test'] == 1)
mkarm('sw_m2', ['FrameTrace: n=1 dt_us=16000 draws=5', FX(1)])
r = arm('sw_m2')
ok &= case('H29 a log without the entry line: not entered, no freeze reading, the arm text says so', r['entered'] is False
           and 'f1' not in r and 'no freeze reading' in '\n'.join(S.fmt_arm(r)))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)))
# RC1: the installed binary returned need not be 9235a7ac (installed_after = installed_before)
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', installed_before=dict(sha='ab' * 32),
                                                               installed_after=dict(sha='ab' * 32)))
ok &= case('H30 RC1: installed before = after = another build (ab...) -> PASS (the constant 9235a7ac is gone)',
           arm('sw_m2')['fail'] == [])
# RC2: the continuity data row (not an admission row)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), cj=cj_for('sw_m1', arm_start=dict(
    utc='2026-10-01T05:00:00Z'), return_app=dict(expected='a1' * 32, got='a1' * 32), return_glc=dict(expected='b1' * 32,
                                                                                                       got='b1' * 32)))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', arm_start=dict(utc='2026-10-01T05:10:00Z'),
                                                               man_pre_app=dict(sha='a1' * 32), man_pre_glc=dict(sha='b1' * 32)))
r = arm('sw_m2')
ok &= case('H31 RC2: the live manifests before the arm = the returns of the previous arm (sw_m1 by arm_start) -> "same"',
           r['continuity'] == ('same as the return of sw_m1', 'sw_m1') and r['fail'] == [] and
           'continuity of the live caches with the previous arm of S' in '\n'.join(S.fmt_arm(r)))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', arm_start=dict(utc='2026-10-01T05:10:00Z'),
                                                               man_pre_app=dict(sha='a1' * 32), man_pre_glc=dict(sha='b2' * 32)))
r = arm('sw_m2')
ok &= case('H32 RC2: GLCache differs from the previous return -> "foreign chain between arms (glc)", the arm still PASS',
           r['continuity'][0] == 'foreign chain between arms (glc)' and r['fail'] == [])
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), cj=cj_for('sw_m2', arm_start=dict(utc='2026-10-01T04:00:00Z')))
ok &= case('H33 RC2: the earliest arm -> "no previous arm of S"; no arm_start -> undetermined',
           arm('sw_m2')['continuity'][0] == 'no previous arm of S' and S.continuity('x', {}, lambda t: None)[0] == 'undetermined')
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)))
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)))

# ================================================================================================ 9 C1-C4 reading (RC2, RC10)
def c_arm(tag, level, us, prep_ms=400, rec=100, n=10, cold='cold'):  # noqa: E302
    """cold: 'cold' (perm, recipe, skip after the entry), 'level' (none of them - level not cold), 't34' (cold rows but
    T-3 broken: 2 stdout Shaders: lines against 1 AvTrace shader line)."""
    hdr = [QUEUED(rec, 1, 1), GFX(300, 'precache'), CS(300, 'precache'), 'PipelinePrecache: all pipelines created, %d ms' % prep_ms]
    head = cold_post[:5] if cold != 'level' else [(16000, {}) for _ in range(5)]
    post = head + [(16000, dict(ev=[GFX(us)])) for _ in range(n)]
    mkarm(tag, t_lines(level, post, header=hdr), stdout_shaders={'cold': 1, 'level': 0, 't34': 2}[cold])


def read_c_with(m1, m2, m3, m4, prep4=7000, n1=10, rec=100, n2=10, cold=('cold',) * 4):
    for t in ('c1_0', 'c2_0', 'c3_0', 'c4_0'):
        p = Path(RM['s4'], '%s.json' % t)
        if p.exists():
            p.unlink()
    c_arm('c1_0', 'shuriken_ninja_castle', m1, n=n1, cold=cold[0])
    if m2 is not None:
        c_arm('c2_0', 'shuriken_ninja_castle', m2, n=n2, cold=cold[1])
    if m3 is not None:
        c_arm('c3_0', 'shuriken_ninja_castle', m3, cold=cold[2])
    if m4 is not None:
        c_arm('c4_0', 'shuriken_ninja_castle', m4, prep_ms=prep4, rec=rec, cold=cold[3])
    get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
    return S.read_c(get), get


def arms_ok(get):
    return get


(res, lines), get = read_c_with(40000, 5000, 40000, 40000)
OUTS.append('\n'.join(lines))
ok &= case('I1 C1 40 000, C2 5 000, C3 40 000, C4 40 000 prep 7 000: neutral YES, GLCache warm YES, salt YES',
           res['k'] == 0 and res['neutral'] is True and res['glc_warm'] is True and res['salt'] is True)
ok &= case('I2 the reading prints the ms per recipe (7 000 / 100 = 70.00) and the band over 114 levels [I] (RC10)',
           res['ms_per_recipe'] == 70.0 and any('ms per recipe (C4) = 7000 / 100 = 70.00' in x and '[I, band]' in x
                                                and '47 / 193 / 559 s at 6 / 28 / 83 recipes per level for 95 levels '
                                                    '(limit 180 s)' in x for x in lines))
(res, lines), _ = read_c_with(19999, 5000, 40000, 40000)
ok &= case('I3 C1 median 19 999 -> neutral NO, salt NO (absolute thresholds, RC2)', res['neutral'] is False and res['salt'] is False)
(res, lines), _ = read_c_with(20000, 5000, 40000, 40000)
ok &= case('I4 C1 20 000, C3 40 000 (ratio 2.0) -> neutral YES', res['neutral'] is True)
(res, lines), _ = read_c_with(20000, 5000, 40001, 40000)
ok &= case('I5 C3/C1 = 2.00005 -> neutral NO', res['neutral'] is False)
(res, lines), _ = read_c_with(40000, 5000, 20000, 40000)
ok &= case('I6 C3/C1 = 0.5 -> neutral YES', res['neutral'] is True)
(res, lines), _ = read_c_with(40000, 5000, 19999, 40000)
ok &= case('I7 C3 19 999 -> neutral NO', res['neutral'] is False)
(res, lines), _ = read_c_with(19999, 5000, 20000, 40000)
ok &= case('I7b C1 19 999, C3 20 000 (ratio in the corridor) -> neutral NO (C1 below 20 000)', res['neutral'] is False)
(res, lines), _ = read_c_with(20000, 5000, 19999, 40000)
ok &= case('I7c C1 20 000, C3 19 999 (ratio in the corridor) -> neutral NO (C3 below 20 000)', res['neutral'] is False)
(res, lines), _ = read_c_with(20000, 5000, 20000, 19999)
ok &= case('I12b C1 20 000, C4 19 999 (ratio in the corridor, prep 7 000) -> salt NO (C4 below 20 000)', res['salt'] is False)
(res, lines), _ = read_c_with(40000, 5000, 40000, 40000, n2=9)
ok &= case('I14b C2 with 9 creations -> "GLCache keeps warmth" undetermined (nothing to classify)', res['glc_warm'] is None)
(res, lines), _ = read_c_with(40000, 10000, 40000, 40000)
ok &= case('I8 C2 = 0.25 x C1 -> GLCache keeps warmth YES', res['glc_warm'] is True)
(res, lines), _ = read_c_with(40000, 10001, 40000, 40000)
ok &= case('I9 C2 = 0.25 x C1 + 1 -> NO', res['glc_warm'] is False)
(res, lines), _ = read_c_with(40000, 5000, 40000, 40000, prep4=6760)
ok &= case('I10 prep_ms C4 6 760 -> salt YES', res['salt'] is True)
(res, lines), _ = read_c_with(40000, 5000, 40000, 40000, prep4=6759)
ok &= case('I11 prep_ms C4 6 759 -> salt NO (RC2: the ratio alone is tautological)', res['salt'] is False)
(res, lines), _ = read_c_with(40000, 5000, 40000, 19999)
ok &= case('I12 C4 median 19 999 -> salt NO', res['salt'] is False)
(res, lines), _ = read_c_with(40000, 5000, 40000, 80001)
ok &= case('I13 C4/C1 > 2 -> salt NO', res['salt'] is False)
(res, lines), _ = read_c_with(40000, None, None, None)
ok &= case('I14 only C1: every reading undetermined (None), T2 may not go', res['neutral'] is None and res['glc_warm'] is None
           and res['salt'] is None and any('T2 base may go: NO' in x for x in lines))
for t in ('c1_1', 'c1_2'):
    Path(RM['s4'], '%s.json' % t).unlink()
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, n1=9)
ok &= case('I15 C1 with 9 creations -> L0 0 rejected, the reserve L0 1 (jack_in_the_box) is next', res['k'] == 1 and
           any('-> reserve' in x for x in lines))
ok &= case('I16 l0_choice: candidate 1 not made -> k 1', S.l0_choice(get)[0] == 1)
for t in ('c1_0', 'c2_0', 'c3_0', 'c4_0'):
    Path(RM['s4'], '%s.json' % t).unlink()
mkarm('c1_0', t_lines('shuriken_ninja_castle', rows_ok(3)), stdout_shaders=0)
mkarm('c1_1', t_lines('jack_in_the_box', rows_ok(3)), stdout_shaders=0)
mkarm('c1_2', t_lines('cymbal_party_land', rows_ok(3)), stdout_shaders=0)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
res, lines = S.read_c(get)
ok &= case('I17 all three L0 candidates with < 10 creations -> L0 exhausted, undetermined', res['k'] is None and
           any('exhausted' in x for x in lines))
for t in ('c1_1', 'c1_2'):
    Path(RM['s4'], '%s.json' % t).unlink()
# RC4 (item 250 (d)): the cold gate in C1-C4
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('cold', 'cold', 'level', 'cold'))
OUTS.append('\n'.join(lines))
ok &= case('N1 C3 "level not cold" -> out of the count: "return neutralises" undetermined (None), the word printed; '
           'GLCache and salt still read', res['k'] == 0 and res['neutral'] is None and res['glc_warm'] is True and
           res['salt'] is True and any('return neutralises: undetermined (C3 out of the count: level not cold)' in x
                                       for x in lines) and any('C3 c3_0: arm PASS; cold gate level not cold' in x for x in lines))
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('cold', 'level', 'cold', 'cold'))
ok &= case('N2 C2 not cold -> "GLCache keeps warmth" undetermined; neutral YES', res['glc_warm'] is None and
           res['neutral'] is True and any('GLCache keeps warmth: undetermined (C2 out of the count: level not cold)' in x
                                         for x in lines))
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('cold', 'cold', 'cold', 'level'))
ok &= case('N3 C4 not cold -> "salt neutralises" undetermined', res['salt'] is None and res['neutral'] is True and
           any('salt neutralises: undetermined (C4 out of the count: level not cold)' in x for x in lines))
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('cold', 'cold', 't34', 'cold'))
ok &= case('N4 C3 with T-3 broken: arm FAIL, the gate word "undetermined (T-3/T-4)" (not "level not cold"); neutral None',
           res['neutral'] is None and any('cold gate undetermined (T-3/T-4) -> arm FAIL' in x for x in lines))
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('level', 'cold', 'cold', 'cold'))
ok &= case('N5 C1 "level not cold" with 10 creations -> L0 0 to the reserve (lead addition of item 250 (d)); L0 1 not made '
           '-> k 1', res['k'] == 1 and any('level not cold -> reserve (item 250 (d))' in x for x in lines))
(res, lines), get = read_c_with(40000, 5000, 40000, 40000, cold=('t34', 'cold', 'cold', 'cold'))
ok &= case('N6 C1 with T-3 broken and 10 creations: L0 stays 0 (gate undetermined (T-3/T-4), not a reserve); every reading '
           'undetermined', res['k'] == 0 and res['neutral'] is None and res['glc_warm'] is None and res['salt'] is None and
           any('gate undetermined (T-3/T-4) -> L0' in x for x in lines))
made = S.made_fn(RM)
for t in ('t2_01', 't2_02'):
    if Path(RM['s4'], '%s.json' % t).exists():
        Path(RM['s4'], '%s.json' % t).unlink()
ok &= case('N7 C1-C4 with C1 undetermined: T2 refused rc 6 (no "return neutralises")', S.allowed('t2_01', made, get)[0] == 6)
ok &= case('N8 cold_word: no gates (no scene frame) -> "undetermined (no scene frame)"; gates without a word -> by cold',
           S.cold_word({}) == 'undetermined (no scene frame)' and S.cold_word(dict(gates=dict(cold=True))) == 'cold'
           and S.cold_word(dict(gates=dict(cold=False))) == 'level not cold')
(res, lines), get = read_c_with(40000, 5000, 40000, 40000)
ok &= case('N9 all four cold -> the readings as before (neutral, warm, salt YES) and "counted" printed', res['neutral'] is True
           and res['glc_warm'] is True and res['salt'] is True and sum(1 for x in lines if '-> counted;' in x) == 4)
ok &= case('N10 the C reading names the unprotected GLCache during the arm and the stop of T2 only (item 250 (e), (zh))',
           any('GLCache during the arm: not protected' in x for x in lines) and any('the stop holds the T2 base only' in x
                                                                                  for x in lines))
# RC10: the files of glc_post whose base never changed inside a S arm
rs4 = Path(RM['s4'], 'runs_s')
(rs4 / 'c1_0.glc_launch.txt').write_text('a/b.bin\t1\tt\tx\na/b.toc\t1\tt\tx\n')
(rs4 / 'c1_0.glc_post.txt').write_text('a/b.bin\t2\tt\ty\na/b.toc\t1\tt\tx\n')
gp = Path(RM['s4'], 'glc_post', 'c1_0')
gp.mkdir(parents=True, exist_ok=True)
(gp / 'MANIFEST.txt').write_text('a/b.bin\t2\tt\ty\na/b.toc\t1\tt\tx\nc/d.bin\t1\tt\tz\n')
ok &= case('N11 RC10 glc_post bases: a/b changed inside c1_0 -> c1_0 1 of 3 files never changed in the S arms',
           S.glc_foreign(RM, 0) == 'c1_0 1 of 3 files' and S.glc_base('a/b.toc\t1') == 'a/b' and S.glc_base('a/bdir/x') == 'a/bdir/x')
(rs4 / 'c1_0.glc_post.txt').unlink()
ok &= case('N12 without the post manifest of the arm no base counts as changed (3 of 3); without glc_post -> undetermined',
           S.glc_foreign(RM, 0) == 'c1_0 3 of 3 files' and S.glc_foreign(RM, 2) == 'undetermined (no glc_post copy)')
shutil.rmtree(gp)
(rs4 / 'c1_0.glc_launch.txt').unlink()

# ================================================================================================ 10 S-warm (RC9)
def base_log(name, level, held_n, dt100_n, hold_long=0):
    post = [(16000, dict(held=1, skip=1, ev=[SKIP(1000 + k)])) for k in range(held_n)] + [(16000, {})] + [(150000, {}) for _ in range(dt100_n)]
    if hold_long:
        post += [(16000, {}) for _ in range(599 - len(post))] + [(150000, {}) for _ in range(hold_long)]
    return write_log(BASE / 'base' / ('%s.txt' % name), m_lines(level, post + rows_ok(3)))


def warm_arm(tag, level, held_n, dt100_n, shaders=0):
    post = [(16000, dict(held=1, skip=1, ev=[SKIP(1000 + k)])) for k in range(held_n)] + [(16000, {})] + [(150000, {}) for _ in range(dt100_n)]
    mkarm(tag, m_lines(level, post + rows_ok(3)), stdout_shaders=shaders)


BL = dict(c142_02=base_log('b02', 'big_hand_pirate_island', 10, 14, hold_long=1), c142_09=base_log('b09', 'voxel_world', 5, 7),
          c142_05=base_log('b05', 'ice_iceberg', 45, 3))


def warm_read(spec_rows):
    for (tag, lv_, _), (h, d, sh) in zip(S.WARM, spec_rows):
        warm_arm(tag, lv_, h, d, sh)
    get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
    return S.read_warm(get, lambda t: S.base_of(t, BL[t]))


w = warm_read([(5, 7, 0), (3, 4, 0), (30, 1, 0)])
OUTS.append('\n'.join(w))
ok &= case('W1 held 5 of base 10 -> (i) STAYS (>= 50 %); dt100 7 of 14 -> (ii) STAYS', 'warm 5 base 10 -> STAYS' in w[0]
           and '(ii) window dt >= 100 ms warm 7' in w[0] and "base 14 {'WAIT': 14} -> STAYS" in w[0])
ok &= case('W2 held 3 of base 5 -> STAYS; dt100 4 of base 7 -> STAYS; ice_iceberg (ii) base 3 < 5 -> undetermined',
           'warm 3 base 5 -> STAYS' in w[1] and 'base 3 {} -> undetermined' in w[2].replace("{'WAIT': 3}", '{}'))
ok &= case('W3 (i) stays in 3 of 3; (ii) stays in all 2 determined -> the narrowing sentence', any(
    '(i) stays in 3 of 3 determined' in x for x in w) and any('stays in 2 of 2 determined -> ALL DETERMINED STAY' in x for x in w))
w = warm_read([(4, 6, 0), (2, 3, 0), (22, 1, 0)])
ok &= case('W4 held 4 of 10, 2 of 5, 22 of 45 -> goes; dt100 6 of 14, 3 of 7 -> goes', any('(i) stays in 0 of 3' in x
                                                                                         for x in w) and any(
    '(ii) stays in 0 of 2' in x for x in w))
w = warm_read([(5, 7, 1), (3, 4, 0), (30, 1, 0)])
ok &= case('W5 a not warm arm (a Shaders: line) is out of the count', 'not warm' in w[0] and any(
    '(i) stays in 2 of 2 determined' in x for x in w))
BL2 = dict(BL)
BL2['c142_09'] = base_log('b09b', 'voxel_world', 4, 4)
for (tag, lv_, _), (h, d, sh) in zip(S.WARM, [(5, 7, 0), (3, 4, 0), (30, 1, 0)]):
    warm_arm(tag, lv_, h, d, sh)
w = S.read_warm(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None), lambda t: S.base_of(t, BL2[t]))
ok &= case('W6 base 4 events -> undetermined on that level for both components (RC9: base >= 5)', 'base 4 -> undetermined'
           in w[1] and 'base 4 {' in w[1])
ok &= case('W7 the reading names the regression to the mean (RC9(g))', any('regression to the mean' in x for x in w))
BL3 = dict(BL)
BL3['c142_09'] = base_log('b09c', 'voxel_world', 5, 5)
for (tag, lv_, _), (h, d, sh) in zip(S.WARM, [(5, 7, 0), (3, 3, 0), (30, 1, 0)]):
    warm_arm(tag, lv_, h, d, sh)
w = S.read_warm(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None), lambda t: S.base_of(t, BL3[t]))
ok &= case('W6b a base of exactly 5 events is determined: dt100 3 of 5 -> STAYS', "base 5 {'WAIT': 5} -> STAYS" in w[1])
for (tag, lv_, _), (h, d, sh) in zip(S.WARM, [(5, 7, 0), (3, 3, 0), (30, 1, 0)]):
    warm_arm(tag, lv_, h, d, sh)
w = S.read_warm(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None), lambda t: S.base_of(t, BL[t]))
ok &= case('W6c (ii) stays on one of two determined levels -> "not all stay"', any(
    '(ii) stays in 1 of 2 determined -> not all stay' in x for x in w))
mkarm('sw_t1', t_lines('big_hand_pirate_island', [(16000, dict(held=1)), (16000, {})] + rows_ok(3)), stdout_shaders=0)
w = S.read_warm(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None), lambda t: S.base_of(t, BL[t]))
ok &= case('W8 the trace-cost row T - M on big_hand_pirate_island (RC7 null control)', any(
    'trace cost T - M on big_hand_pirate_island' in x and 'held -4' in x for x in w))

# ================================================================================================ 11 T2 and the order (RC13)
for t in list(S.SPEC):
    for d in RM.values():
        for p in (Path(d, '%s.json' % t), Path(d, 'attempt_%s.txt' % t)):
            if p.exists():
                p.unlink()
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
made = S.made_fn(RM)
ok &= case('J1 order: sw_m1 first allowed; sw_m2 needs sw_m1; C1 needs S-warm', S.allowed('sw_m1', made, get)[0] == 0
           and S.allowed('sw_m2', made, get)[0] == 1 and S.allowed('c1_0', made, get)[0] == 1)
Path(RM['s4'], 'attempt_sw_m1.txt').write_text('x')
ok &= case('J2 an attempt marker counts as made (no repeat): sw_m1 refused, sw_m2 allowed', S.allowed('sw_m1', made, get)[0] == 1
           and S.allowed('sw_m2', made, get)[0] == 0)
for t in ('sw_m2', 'sw_m3', 'sw_t1'):
    Path(RM['s4'], 'attempt_%s.txt' % t).write_text('x')
ok &= case('J3 S-warm done: c1_0 allowed, c1_1 refused rc 6 (L0 is 0), c2_0 needs c1_0', S.allowed('c1_0', made, get)[0] == 0
           and S.allowed('c1_1', made, get)[0] == 6 and S.allowed('c2_0', made, get)[0] == 1)
(res, lines), get = read_c_with(19999, 5000, 40000, 40000)
ok &= case('J4 C1-C4 made without "return neutralises": T2 refused rc 6 (item 241 (d): report and stop)',
           S.allowed('t2_01', made, get)[0] == 6)
ok &= case('J5 g_1 allowed after C1-C4 without the T2 base (no neutralisation)', S.allowed('g_1', made, get)[0] == 0)
(res, lines), get = read_c_with(40000, 5000, 40000, 40000)
ok &= case('J6 with neutralisation: t2_01 allowed, t2_02 needs t2_01, g_1 waits for the T2 base',
           S.allowed('t2_01', made, get)[0] == 0 and S.allowed('t2_02', made, get)[0] == 1 and S.allowed('g_1', made, get)[0] == 1)
t2 = [(16000, dict(skip=1, ev=[SKIP(8), SH(7, 1, 1), RSAVE(101)])), (16000, dict(held=1)), (16000, {})]
for j in range(5):
    tg = 't2_%02d' % (j + 1)
    mkarm(tg, t_lines(S.SPEC[tg]['level'], t2), stdout_shaders=1)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
ok &= case('J7 five counted T2 arms: the reserve t2_06 refused rc 6; g_1 allowed', S.allowed('t2_06', made, get)[0] == 6
           and S.allowed('g_1', made, get)[0] == 0)
t2r = S.read_t2(get)
OUTS.append('\n'.join(t2r))
ok &= case('J8 the T2 reading: 5 counted; S-early denominator 0 -> undetermined (RC11)', any('T2 counted 5 of 5' in x
                                                                                            for x in t2r) and any(
    'undetermined (denominator 0)' in x for x in t2r))
mkarm('t2_05', t_lines('hero_kratos', rows_ok(3)), stdout_shaders=0)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None)
ok &= case('J9 one T2 arm not cold: the reserve t2_06 allowed; t2_07 needs t2_06', S.allowed('t2_06', made, get)[0] == 0
           and S.allowed('t2_07', made, get)[0] == 1 and S.allowed('g_1', made, get)[0] == 1)
ok &= case('J9b the T2 reading counts only cold arms: 4 of 5', any('T2 counted 4 of 5' in x for x in S.read_t2(get)))
RMX = {'s4': str(BASE / 'x4'), 's6': str(BASE / 'x6')}
early_post = [(16000, dict(skip=1, ev=[SKIP(8), SH(9, 1, 1), RSAVE(101)])), (16000, dict(held=1)), (16000, {}), (16000, {}),
              (16000, {}), (250000, dict(ev=[REG(5, 1000), SH(5, 100000, 100000), FIRST(5, 2000)])), (16000, {}),
              (16000, {}), (16000, {}), (16000, {}),
              (250000, dict(ev=[REG(6, 0), SH(6, 100000, 100000), FIRST(6, 900000)])), (16000, {}), (16000, {})]
mkarm('t2_01', t_lines('small_pot_lava', early_post), stdout_shaders=3, root=RMX)
t2x = S.read_t2(S.make_get(RMX, {'s4': PRED4, 's6': PRED6}, None))
OUTS.append('\n'.join(t2x))
ok &= case('J9c S-early first half: lead < cost in 1 of 2 events -> ">= 50 %" (the edge)', any(
    'lead < cost in 1 of 2 events -> >= 50 %' in x for x in t2x))
Path(RM['s4'], 'attempt_g_1.txt').write_text('x')
ok &= case('J10 g_2 after g_1; g_3_0 needs g_2; g_3_1 refused (L0 is 0)', S.allowed('g_2', made, get)[0] == 0
           and S.allowed('g_3_0', made, get)[0] == 1 and S.allowed('g_3_1', made, get)[0] == 6)
ok &= case('J11 S6 order: pcw_1 first, pcw_int needs pcw_3, pcw_val needs pcw_4', S.allowed('pcw_1', made, get)[0] == 0
           and S.allowed('pcw_int', made, get)[0] == 1 and S.allowed('pcw_val', made, get)[0] == 1)

# ================================================================================================ 12 S-pcw (item 241 (z)(5))
PCWOV = 'AvTrace: pcw overlap wait gfx id0=11 id1=12 wait_us=%d gen0=3 gen1=5'
PCWREC = 'AvTrace: pcw recipes copied=4 count=1842 lock_us=%d hold_us=%d'


def pcw_lines(level, n_writes, frames_with, forced=True, savefail=0, loaded=90000, disabled=False, last=777, t=False,
              trace=(), incomplete=0):
    post = [(16000, {}) for _ in range(599)]
    hold = []
    for k in range(n_writes):
        b = last if k == n_writes - 1 else 500
        if k < frames_with:
            hold += [(150000, dict(ev=[DSAVE(b, forced=forced)]))]
        else:
            hold += [(16000, dict(ev=[DSAVE(b, forced=forced)])), (16000, {})]
    hold += [(16000, dict(ev=['Vulkan pipeline cache: save failed (x, 5 bytes)'] * savefail +
                          ['Vulkan pipeline cache: save failed (Incomplete, 4096 bytes)'] * incomplete + list(trace)))]
    head = list(HEADER_T[:-1]) if t else []           # pcw_int is a T arm (RC5): queued + precache lines for T-4
    head += ['Vulkan pipeline cache: disabled (KYTY_PIPELINE_CACHE=0)'] if disabled else []
    head += ['Vulkan pipeline cache: loaded %d bytes from x' % loaded]
    big = [(int(300000000 / 700) + 1, {}) for _ in range(700)]
    return scene(level, post + hold + big, None, head)


TRACE_INT = (PCWOV % 2500, PCWOV.replace('wait gfx', 'wait cs') % 900, PCWREC % (40, 1200), PCWREC % (10, 700))


def pcw_all(w0=15, f0=8, w1=15, f1=0, loaded=777, val_vke=0, glitch=(3000, 0), fail1=0, f0_4=None, disabled=False,
            trace=TRACE_INT, inc1=0, inc0=0, val_lines=None, int_t4=True):
    for t in ('pcw_1', 'pcw_4'):
        mkarm(t, pcw_lines(S.SKY, w0, f0 if (t == 'pcw_1' or f0_4 is None) else f0_4, incomplete=inc0), glitch=glitch)
    for t in ('pcw_2', 'pcw_3'):
        mkarm(t, pcw_lines(S.SKY, w1, f1, savefail=fail1, incomplete=inc1 if t == 'pcw_3' else 0), glitch=glitch)
    li = pcw_lines(S.SKY, 0, 0, loaded=loaded, disabled=disabled, t=True, trace=trace)
    if not int_t4:
        li = [x for x in li if not x.startswith('AvTrace: pipeline cs')]
    mkarm('pcw_int', li, glitch=glitch)
    vl = pcw_lines(S.SKY, w1, 0) + ['VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features',
                                    '[Vulkan][W] x'] + ['[Vulkan][E] y'] * val_vke
    mkarm('pcw_val', vl if val_lines is None else val_lines[0], glitch=glitch if val_lines is None else val_lines[1])
    return S.read_pcw(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None))


word, lines = pcw_all()
OUTS.append('\n'.join(lines))
ok &= case('K1 15 writes, 8 frames (>= 50 %) on arms 0; 15 writes, 0 frames on arms 1; integrity 777 = 777; validation '
           'clean; video ok -> MACHINE_PASS_PENDING_SHEET', word == 'MACHINE_PASS_PENDING_SHEET')
word, lines = pcw_all(w0=16, f0=8)
ok &= case('K1b arms 0 with 8 frames of 16 writes (exactly 50 %) -> positive control PASS', word == 'MACHINE_PASS_PENDING_SHEET')
word, lines = pcw_all(w0=100, f0=49)
ok &= case('K1c arms 0 with 49 frames of 100 writes (49 %) -> POSCTRL_FAIL', word == 'POSCTRL_FAIL')
word, lines = pcw_all(f0=7)
ok &= case('K2 arms 0 with 7 frames of 15 writes (< 50 %) -> POSCTRL_FAIL (counts toward the kill rule (z)(7))',
           word == 'POSCTRL_FAIL')
word, lines = pcw_all(w0=14, f0=7)
ok &= case('K3 arms 0 with 14 writes -> POSCTRL_FAIL', word == 'POSCTRL_FAIL')
word, lines = pcw_all(f1=1)
ok &= case('K4 an arm 1 with one frame >= 100 ms with a write -> ARM1_FAIL', word == 'ARM1_FAIL')
word, lines = pcw_all(w1=14)
ok &= case('K5 arms 1 with 14 writes -> ARM1_FAIL', word == 'ARM1_FAIL')
word, lines = pcw_all(fail1=1)
ok &= case('K6 a save failure on an arm 1 -> ARM1_FAIL', word == 'ARM1_FAIL')
word, lines = pcw_all(loaded=778)
ok &= case('K7 integrity: loaded 778 != last write 777 -> ARM1_FAIL (c)', word == 'ARM1_FAIL' and any(
    '(c) integrity' in x and 'FAIL' in x for x in lines))
word, lines = pcw_all(disabled=True)
ok &= case('K7b integrity with a "disabled" line -> ARM1_FAIL (c)', word == 'ARM1_FAIL')
word, lines = pcw_all(f0_4=7)
ok &= case('K7c pcw_4 (the second arm 0) below 50 % -> POSCTRL_FAIL (both arms 0 are the positive control)',
           word == 'POSCTRL_FAIL')
word, lines = pcw_all(val_vke=1)
ok &= case('K8 one [Vulkan][E] in the validation arm -> ARM1_FAIL (d)', word == 'ARM1_FAIL')
word, lines = pcw_all(glitch=(2999, 0))
ok &= case('K9 a video of 2 999 frames -> ARM1_FAIL (e)', word == 'ARM1_FAIL')
word, lines = pcw_all(glitch=(3200, 1))
ok &= case('K10 one glitch -> ARM1_FAIL (e)', word == 'ARM1_FAIL')
Path(RM['s6'], 'pcw_val.json').unlink()
word, lines = S.read_pcw(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None))
ok &= case('K11 an arm not made -> NOT_EVALUABLE', word == 'NOT_EVALUABLE')
s = sc(pcw_lines(S.SKY, 3, 1), 'k12')
eg, end, fi = S.locate(s, S.SKY)
p = S.pcw_arm(s, fi, end)
ok &= case('K12 pcw_arm counts writes only on the hold (after 599 rows), forced writes, frames with a write in i-1..i+1',
           p['writes'] == 3 and p['forced'] == 3 and p['frames'] == 1 and p['last_bytes'] == 777)
s = sc(scene(S.SKY, [(16000, {}) for _ in range(599)] + [(150000, {}), (16000, dict(ev=[DSAVE(5)])), (16000, {}),
                                                         (16000, {}), (150000, {}), (16000, {}), (16000, {}),
                                                         (16000, dict(ev=[DSAVE(5)])), (16000, {})]), 'k13')
eg, end, fi = S.locate(s, S.SKY)
p = S.pcw_arm(s, fi, end)
ok &= case('K13 a write in group i+1 counts for frame i; a write in group i+3 does not (the window i-1..i+1)',
           p['frames'] == 1 and p['writes'] == 2)
s = sc(scene(S.SKY, [(16000, dict(ev=[DSAVE(5)] if k == 10 else [])) for k in range(599)] +
             [(16000, {}), (16000, dict(ev=[DSAVE(5)])), (150000, {}), (16000, {}), (16000, {}), (16000, {}),
              (150000, {}), (16000, {}), (16000, dict(ev=[DSAVE(5)])), (16000, {})]), 'k14')
eg, end, fi = S.locate(s, S.SKY)
p = S.pcw_arm(s, fi, end)
ok &= case('K14 a write in the window is not counted; a write in group i-1 counts for frame i; one in group i+2 does not',
           p['writes'] == 2 and p['frames'] == 1 and p['frames_n'] == [609])
# RC5: the AvTrace pcw lines (S5c 2ce6326e formats), pcw_int on T
s = sc(t_lines('lvl', [(200000, dict(ev=[PCWOV % 150000, PCWOV.replace('wait gfx', 'cs') % 7,
                                          PCWOV.replace('wait gfx', 'wait cs') % 9, 'AvTrace: pcw overlap gfx id0=1 id1=2',
                                          PCWREC % (40, 1200)]))]), 'k15')
eg, end, fi = lv(s)
pt = S.pcw_trace(s)
c = S.classify(s, fi + 1, S.assign_prep(s), True)
ok &= case('K15 pcw overlap lines parsed by kind (wait gfx / cs / wait cs / gfx), wait_us (a line without it kept), the '
           'recipes line lock_us / hold_us; max only (not added)', pt['overlap'] == 4 and pt['kinds'] == {
               'wait gfx': 1, 'cs': 1, 'wait cs': 1, 'gfx': 1} and pt['wait_us_max'] == 150000 and pt['recipes'] == 1 and
           pt['lock_us_max'] == 40 and pt['hold_us_max'] == 1200 and s['pcw_ov'][0][3:] == (3, 5))
ok &= case('K16 the pcw lines are not PREP (a 150 000 us overlap line in group i leaves PREP 0) and not pipe events',
           c[2] == 0 and s['pipe'] == [x for x in s['pipe'] if x[0] == 0] and S.pcw_trace(sc(t_lines('lvl', rows_ok(2)),
                                                                                              'k16')) is None)
word, lines = pcw_all()
OUTS.append('\n'.join(lines))
ok &= case('K17 the S-pcw reading prints (z)(1) on pcw_int by number: 2 overlap lines, wait_us max 2 500 "upper bound, not '
           'added", 2 recipes lines, lock_us max 40, hold_us max 1 200', word == 'MACHINE_PASS_PENDING_SHEET' and any(
               "overlap lines 2 [('wait cs', 1), ('wait gfx', 1)], wait_us max 2500 (the creation time - an upper bound, "
               "not added as a wait" in x and 'recipes lines 2, lock_us max 40, hold_us max 1200' in x for x in lines))
word, lines = pcw_all(trace=())
ok &= case('K18 0 pcw lines on pcw_int -> (z)(1) undetermined, the word MACHINE_UNDETERMINED (never above it)',
           word == 'MACHINE_UNDETERMINED' and any('(z)(1) waits of GuestGpu on pcw_int: undetermined' in x for x in lines))
word, lines = pcw_all(trace=(PCWREC % (1, 2),))
ok &= case('K18b only the recipes line on pcw_int (0 overlap) -> (z)(1) determined: overlap 0', word ==
           'MACHINE_PASS_PENDING_SHEET' and any('overlap lines 0' in x for x in lines))
word, lines = pcw_all(int_t4=False)
ok &= case('K19 pcw_int with T-4 broken (a precache line missing) -> identity FAIL -> NOT_EVALUABLE (T rows apply)',
           word == 'NOT_EVALUABLE')
# RC6: Incomplete on an arm 1
word, lines = pcw_all(inc1=1)
ok &= case('K20 "save failed (Incomplete" on pcw_3 -> ARM1_CODE_DEFECT (not ARM1_FAIL), the line names the defect of the '
           'iteration code, once per route', word == 'ARM1_CODE_DEFECT' and any(
               "'pcw_3': 1" in x and 'defect of the iteration code (item 245 (v))' in x for x in lines))
word, lines = pcw_all(inc1=1, f1=1)
ok &= case('K20b Incomplete together with a frame on an arm 1 -> ARM1_CODE_DEFECT (the arm is repeated after the fix)',
           word == 'ARM1_CODE_DEFECT')
word, lines = pcw_all(inc0=1)
ok &= case('K21 Incomplete on the arms 0 is not the defect of arms 1 -> MACHINE_PASS_PENDING_SHEET', word ==
           'MACHINE_PASS_PENDING_SHEET')
s = sc(pcw_lines(S.SKY, 1, 0, incomplete=2, savefail=1), 'k22')
ok &= case('K22 the scan counts Incomplete apart from the other save failures (2 / 1)', s['savefail_inc'] == 2 and
           s['savefail'] == 1)
# RC11: pcw_val stopped by validation before the entry line
vstop = HEADER_M + ['VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features', '[Vulkan][W] x'] + \
    [y for n in range(1, 4) for y in (FT(n, 20000, 5), FX(n))] + ['[Vulkan][E] SRC1_ALPHA without dualSrcBlend']
word, lines = pcw_all(val_lines=(vstop, (90, 0)))
OUTS.append('\n'.join(lines))
ok &= case('K23 pcw_val stopped by validation before the entry line -> VALIDATION_STOP_PRE_LEVEL: (d) undetermined, not '
           'FAIL, out of the hold / video / admission checks; word MACHINE_UNDETERMINED', word == 'MACHINE_UNDETERMINED'
           and any('VALIDATION_STOP_PRE_LEVEL' in x and 'not counted toward the kill rule' in x for x in lines))
vnone = HEADER_M + [y for n in range(1, 4) for y in (FT(n, 20000, 5), FX(n))]
word, lines = pcw_all(val_lines=(vnone, (90, 0)))
ok &= case('K24 pcw_val not entered WITHOUT a [Vulkan][E] line is not a validation stop -> NOT_EVALUABLE (hold)',
           word == 'NOT_EVALUABLE')
word, lines = pcw_all(val_vke=1)
ok &= case('K25 pcw_val entered with one [Vulkan][E] -> (d) FAIL -> ARM1_FAIL (the stop after the entry is a FAIL)',
           word == 'ARM1_FAIL' and any('(d) validation: active' in x and 'FAIL' in x for x in lines))
# item 254 (e): form W of the validation arm
ok &= case('K26 form W: the expected environment of pcw_val carries KYTY_PIPELINE_PRECACHE=0 (a family key), no other '
           'arm does', S.expected_env(S.SPEC['pcw_val']).get('KYTY_PIPELINE_PRECACHE') == '0' and S.in_family(
               'KYTY_PIPELINE_PRECACHE') and all('KYTY_PIPELINE_PRECACHE' not in S.expected_env(S.SPEC[t]) for t in S.SPEC
                                                 if t != 'pcw_val'))
s = sc(['PipelinePrecache: 5 recipes -> x', QUEUED(100, 1, 1), 'PipelinePrecache: saved 3 recipes',
        'PipelinePrecache: all pipelines created, 4 ms'], 'k26')
ok &= case('K26b the scan counts every "PipelinePrecache: N recipes ->" line (the short and the full form: 2), not the '
           'saved / created lines', s['queued_n'] == 2)
word, lines = pcw_all()
ok &= case('K26c form W clean (no recipes line in pcw_val) -> the positive control row PASS, word unchanged',
           word == 'MACHINE_PASS_PENDING_SHEET' and any(x[0].startswith('form W positive control') and x[1] for x in
                                                       S.score_arm('pcw_val', RM)['admit']))
word, lines = pcw_all(val_lines=([QUEUED(100, 1, 1)] + pcw_lines(S.SKY, 15, 0) + [
    'VK_LAYER_KHRONOS_validation available extension: VK_EXT_validation_features'], (3000, 0)))
ok &= case('K26d a "PipelinePrecache: 100 recipes ->" line in pcw_val (the start precache ran) -> admission FAIL of '
           'pcw_val -> NOT_EVALUABLE', word == 'NOT_EVALUABLE' and 'admission: form W positive control: no '
           '"PipelinePrecache: N recipes ->" line (item 254 (e))' in S.score_arm('pcw_val', RM)['fail'])
word, lines = pcw_all()
mkarm('pcw_val', pcw_lines(S.SKY, 15, 0) + ['VK_LAYER_KHRONOS_validation available extension: '
                                            'VK_EXT_validation_features'], glitch=(3000, 0),
      js=js_for('pcw_val', env_over=dict(KYTY_PIPELINE_PRECACHE=None)))
word, lines = S.read_pcw(S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None))
ok &= case('K26e pcw_val without KYTY_PIPELINE_PRECACHE=0 -> the family row FAIL -> NOT_EVALUABLE', word == 'NOT_EVALUABLE'
           and any(x.startswith('admission: KYTY_* families') for x in S.score_arm('pcw_val', RM)['fail']))

# ================================================================================================ 13 seal and main
SEAL = BASE / 'seal.md'
fa = BASE / 'fa.txt'
fa.write_text('a')
ha = hashlib.sha256(b'a').hexdigest()
me = hashlib.sha256(Path(SRC).read_bytes()).hexdigest()
lines = ['seal: %s %s' % (ha, str(fa).replace('\\', '/'))] + ['seal: %s %s' % (ha, n) for n in S.SEALED_NAMES]
SEAL.write_text('\n'.join(lines) + '\npcw binary: %s C:/x/kyty.exe\n' % PBIN)
okk, rows, pb = S.check_seal(str(SEAL), str(BASE), SRC)
ok &= case('L1 check_seal: a sealed file that differs -> FAIL; the pcw binary line is read', okk is False and
           pb == (PBIN, 'C:/x/kyty.exe'))
okk, rows, pb = S.check_seal(str(BASE / 'none.md'), str(BASE), SRC)
ok &= case('L2 check_seal of a missing seal -> FAIL, no binary', okk is False and pb is None)
SEAL.write_text('seal: %s sc_s.py\n' % me)
okk, rows, pb = S.check_seal(str(SEAL), str(BASE), SRC)
ok &= case('L3 a seal without the other sealed names -> FAIL (no seal line rows)', okk is False and any(
    r[2] == 'no seal line' for r in rows) and pb is None)
ok &= case('L4 the sealed names carry the harness, scorer, fixtures, mutants, cache tool, index, sc142 and its fixtures',
           all(n in S.SEALED_NAMES for n in ('go_s.sh', 'sc_s.py', 'test_sc_s.py', 'mut_sc_s.py', 'cachex_s.py',
                                             's3/snap0_index.json', 'C:/kyty/s142/sc142.py', 'C:/kyty/s142/test_sc142.py',
                                             'enter_scene.py', 'C:/kyty/scripts/s51_vidglitch.py')))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc1 = S.main(['--plan', 'c4_0'])
    rc2 = S.main(['--plan', 'zz'])
    rc3 = S.main(['--tag', 'zz'], root_map=RM)
    rc4 = S.main(['--allowed', 'zz'], root_map=RM)
    rc5 = S.main([], root_map=RM)
o = buf.getvalue()
OUTS.append(o)
ok &= case('L5 main --plan prints the plan rc 0; unknown tags rc 2; no option rc 2', rc1 == 0 and rc2 == 2 and rc3 == 2
           and rc4 == 2 and rc5 == 2 and 's4 shuriken_ninja_castle T glc_from' in o)
js = js_for('sw_m2')
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc6 = S.main(['--tag', 'sw_m2'], root_map=RM, pred=PRED4, pred_s6=PRED6, index=str(BASE / 'noindex.json'))
    rc7 = S.main(['--tag', 'g_3_2'], root_map=RM, pred=PRED4, pred_s6=PRED6)
    rc7b = S.main(['--tag', 'sw_m3'], root_map=RM, pred=PRED4, pred_s6=PRED6)
    rc8 = S.main(['--allowed', 'sw_m3'], root_map=RM, pred=PRED4, pred_s6=PRED6)
o = buf.getvalue()
OUTS.append(o)
ok &= case('L6 main --tag a clean arm rc 0 and the score json written; a missing arm rc 1 (NO_RUN)', rc6 == 0 and
           Path(RM['s4'], 'runs_s', 'sw_m2.score.json').is_file() and rc7 == 1 and 'ARM g_3_2: NO_RUN' in o and rc7b == 1
           and 'ARM sw_m3: ATTEMPT MADE, NO JSON (instrument)' in o)
ok &= case('L7 main --allowed prints the reason and returns the rc', 'ALLOWED sw_m3:' in o and rc8 in (0, 1))
js['prereg'] = dict(path=PRED4, sha256='00' * 32)
mkarm('sw_m2', m_lines('voxel_world', rows_ok(3)), js=js)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc9 = S.main(['--tag', 'sw_m2'], root_map=RM, pred=PRED4, pred_s6=PRED6)
ok &= case('L8 main --tag on an arm sealed by another seal -> rc 1', rc9 == 1)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc10 = S.main(['--read-c', '--read-t2'], root_map=RM, pred=PRED4, pred_s6=PRED6)
o = buf.getvalue()
OUTS.append(o)
ok &= case('L9 main --read-c --read-t2 rc 0 with both headers', rc10 == 0 and 'READ C1-C4' in o and 'READ T2' in o)
idx = BASE / 'ix.json'
idx.write_text(json.dumps(dict(shaders=[dict(stage='vs', hash='%016x' % 1, key='k', current=True),
                                        dict(stage='ps', hash='%016x' % 2, key='k', current=False)],
                               pairs=['%016x/%016x' % (1, 2)])), encoding='ascii')
ix = S.load_index(str(idx))
ok &= case('L10 load_index: any / current hash sets and pairs; a missing index -> None',
           ix['any'] == {'%016x' % 1, '%016x' % 2} and ix['cur'] == {'%016x' % 1} and ix['pairs'] == {'%016x/%016x' % (1, 2)}
           and S.load_index(str(BASE / 'none.json')) is None)
# ================================================================================================ 12 S4b (HPP-349, item 265)
# real lines of C:/kyty/s288/s4/log_c1_0.txt (sha256 49d0a522...2d902), byte for byte, by their line numbers
REAL_EMIT = b'AvTrace: shader-emit vs hash=0x960ad032acbd9134 emit_us=3082 validate_us=14 module_us=77 words=30174'     # line 232401
REAL_CSAVE = b'AvTrace: shader-cache save hash=0x960ad032acbd9134 permutations=1 ok=1 us=2561'    # line 232417
REAL_SPEC = b'AvTrace: shader-spec ShaderRecompiler VS hash=0x960ad032acbd9134 perm=1 b:e000010/0/fac b:2000010/0/fac b:2000010/0/fac b:2000001/0/fac b:2000010/0/fac b:e000010/0/fac b:2000010/0/fac b:2000010/0/fac'     # line 232418
REAL_SH = b'AvTrace: shader ShaderRecompiler VS hash=0x960ad032acbd9134 translate_us=11705 compile_us=6169 permutations=1'       # line 232419
m = S.RX_SHADER.search(REAL_SH)
ok &= case('S4b-1 RX_SHADER reads the real line 232419 of log_c1_0.txt (label with a space, 4fc501f4 pipelineCache.cpp:3916): '
           'label ShaderRecompiler VS, hash, translate_us 11705, compile_us 6169', m is not None
           and m.group(1) == b'ShaderRecompiler VS' and m.group(2) == b'960ad032acbd9134' and m.group(3) == b'11705'
           and m.group(4) == b'6169')
m1 = S.RX_SHADER.search(SH(0x55, 7, 8).encode('ascii'))
ok &= case('S4b-2 a one-word label (the former form) still reads: label VS, translate 7, compile 8', m1 is not None
           and m1.group(1) == b'VS' and m1.group(2) == b'0000000000000055' and m1.group(3) == b'7' and m1.group(4) == b'8')
p4b = BASE / 'logs' / 's4b_real.txt'
p4b.parent.mkdir(parents=True, exist_ok=True)
p4b.write_bytes(b'\n'.join([REAL_EMIT, REAL_CSAVE, REAL_SPEC, REAL_SH, LOAD(9).encode('ascii')]) + b'\n')
s = S.scan_s(str(p4b))
ok &= case('S4b-3 order of the branches: of the real shader-emit / shader-cache save / shader-spec / shader lines only the '
           '"AvTrace: shader " line enters s[sh] (label, hash, translate, compile, line 4); shader-cache load goes to s[load]',
           s['sh'] == [(0, 'ShaderRecompiler VS', '960ad032acbd9134', 11705, 6169, 4)] and s['load'] == [(0, 9)]
           and s['avtrace'] == 5)
real_post = [(16000, dict(skip=1, ev=[SKIP(8, 1, 2), REAL_EMIT.decode('ascii'), REAL_CSAVE.decode('ascii'),
                                       REAL_SPEC.decode('ascii'), REAL_SH.decode('ascii')])), (16000, dict(held=1)),
             (16000, dict(ev=[RSAVE(101)])), (16000, {})]
real_post += [(16000, dict(ev=[GFX(30000)])) for _ in range(10)]
mkarm('c1_0', t_lines('shuriken_ninja_castle', real_post), stdout_shaders=1)
r = arm('c1_0', ix=IX)
t3 = [x for x in r['ident'] if x[0].startswith('T-3')]
ok &= case('S4b-4 a T arm with the real lines: T-3 1 / 1 PASS, attribution determined, cold gate "cold" (perm 1, recipe +1, '
           'skip 1), arm PASS', r['fail'] == [] and r['attr_ok'] and t3 and t3[0][1] is True and t3[0][2] == '1 / 1'
           and r['gates']['cold_word'] == 'cold' and r['gates']['perm_after'] == 1 and r['gates']['rec_new_after'] == 1
           and r['gates']['skip_after'] == 1)
# item 265 (g): the arms made under an earlier seal are admitted against it, by name; the others against the seal now
PREV = (BASE / 'pred' / 'prev_s.md').as_posix()
Path(PREV).write_bytes(b'an earlier seal\n')
PREV_SHA = hashlib.sha256(Path(PREV).read_bytes()).hexdigest()
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=PREV, sha256=PREV_SHA)))
mkarm('c2_0', t_lines('shuriken_ninja_castle', cold_post), stdout_shaders=1)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, PREV_SHA, ('sw_m1', 'c1_0')))
a1 = dict((x[0], x[1]) for x in get('sw_m1')['admit'])
a2 = dict((x[0], x[1]) for x in get('c2_0')['admit'])
ok &= case('S4b-5 an arm of the earlier seal: row "prereg = the seal of its run prev_s.md (item 265 (g))" PASS, arm PASS; '
           'an arm after it: row "prereg = the seal now" PASS', a1.get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is True and 'prereg = the seal now' not in a1 and get('sw_m1')['fail'] == [] and a2.get('prereg = the seal now')
           is True)
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, '00' * 32, ('sw_m1', 'c1_0')))
ok &= case('S4b-5b the earlier seal whose sha256 is not the pinned one admits none: prereg row FAIL',
           dict((x[0], x[1]) for x in get('sw_m1')['admit']).get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is False)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)))
get = S.make_get(RM, {'s4': PRED4, 's6': PRED6}, None, (PREV, PREV_SHA, ('sw_m1', 'c1_0')))
ok &= case('S4b-5c an arm of the earlier seal list whose json names the seal now -> prereg row FAIL (routed to its run)',
           dict((x[0], x[1]) for x in get('sw_m1')['admit']).get('prereg = the seal of its run prev_s.md (item 265 (g))')
           is False)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=PREV, sha256=PREV_SHA)))
jo = BASE / 'out' / 'sw_m1.s03.json'
sj = Path(RM['s4'], 'runs_s', 'sw_m1.score.json')
if sj.exists():
    sj.unlink()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc11 = S.main(['--tag', 'sw_m1', '--json-out', str(jo)], root_map=RM, pred=PRED4, pred_s6=PRED6,
                  prev=(PREV, PREV_SHA, ('sw_m1',)))
o = buf.getvalue()
OUTS.append(o)
ok &= case('S4b-6 main --tag --json-out: rc 0, the json at the given path, runs_s/<tag>.score.json not written',
           rc11 == 0 and jo.is_file() and json.load(open(jo, encoding='utf-8'))['tag'] == 'sw_m1' and not sj.exists()
           and 'PASS admit prereg = the seal of its run prev_s.md (item 265 (g))' in o)
mkarm('sw_m1', m_lines('big_hand_pirate_island', rows_ok(5)), js=js_for('sw_m1', prereg=dict(path=S.PRED_02, sha256=S.SHA_02)))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc12 = S.main(['--tag', 'sw_m1', '--json-out', str(jo)], root_map=RM, pred=S.PRED_PATH, pred_s6=PRED6)
o = buf.getvalue()
OUTS.append(o)
ok &= case('S4b-7 main under the production seal routes the seal 02 arms to the real pred/02_s.md (pinned 829ac684): '
           'prereg row PASS, rc 0', rc12 == 0 and 'PASS admit prereg = the seal of its run 02_s.md (item 265 (g)) (829ac684)' in o)

try:
    '\n'.join(OUTS).encode('cp1250', errors='strict')
    '\n'.join(OUTS).encode('ascii', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('L11 every printed line is ASCII (strict cp1250 and ascii, item 175 (v))', enc)
print('checks: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
