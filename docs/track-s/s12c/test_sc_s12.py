"""Offline fixtures of sc_s12.py (track S, link S12c, HPP-496; ROADMAP "SESSION 122" item 408 (l) S12c, item 414 (b), (g)(2), item
419 (v) Z1-Z3).  One case per term and per edge: the plan of every arm; the environment (every KYTY_* / VK_* key, KYTY_S_PCW named,
the path suffixes); admission (one attempt, the arm binary by binary_sha256 with installed_before != it, prereg, installed before in
{FS4, FS5} and after = before, the returns, the restores per mode asis / full / integrity, the post copies of s12_gw); the knob line
S-pcw (=1, =0, FORCE_MS != 0, missing); the W members (hold 300 s edge, [Vulkan][E] in log / stdout, [Vulkan][W] positive control,
limit lines, DualSrcBlend before / after the first GuestOut and 1/0, death markers); the V members (video 2999 / 3000, glitches 0 / 1 /
unread, sheet, frames >= 1 s edge 999 999 / 1 000 000, death in stdout, scene change); the reference word of s12_v0; the blob of
s12_gw (present, sha = snap0, size = snap0 / + 1, absent, absent with .tmp = INTERFERENCE of Z2); the load classes of s12_gr (Z1: one
loading and one loaded, N = last saved = size - 76, the state (e) of the review, no loaded line with its cause, two loaded lines, every
bad class, unknown lines); interference (minimized, Recovering Vulkan swapchain, GamePatch; restored alone is not); the data line of
item 414 (g)(2) through sc_s.classify (a held 150 ms frame with a recipes save -> PCW with its hold_us; NOT_EVALUABLE when empty);
the order (made, not made, death stop, INTERFERENCE stop, not scored, s12_gr conditions); the seal; main; ASCII output in cp1250.
The mutlib early-exit form (item 85 (v)(2)): the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is
`sys.exit(0 if ok else 1)`.  The first output line names this suite and the scorer under test by sha256; the output ends with ALL OK.
    python C:/kyty/s288/s12/test_sc_s12.py [<sc_s12 under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'sc_s12.py')
print('suite test_sc_s12.py sha256 %s target sc_s12.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
_spec = importlib.util.spec_from_file_location('sc_s12_under_test', SRC)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BIN = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
FS4 = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
FS5 = '631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17'
OTHER = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'
SNAP_BIN = 'cc5b747c5bece91e2de2ff99e4e8d8999a98bb46fa651b0220ca7074bf8f92fd'
SNAP_SIZE = 94435713
NEWSHA = 'ab' * 32
BASE = Path('C:/kyty/s288/s12/fx_sc_s12')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
LD = str(BASE / 's12')
(BASE / 'pred').mkdir()
PRED = (BASE / 'pred' / '08_s.md').as_posix()
Path(PRED).write_bytes(b'seal 08 of S12c\n')
PRED_SHA = hashlib.sha256(Path(PRED).read_bytes()).hexdigest()
N_CASES = [0]
A = S.load_sc_s()


def case(name, cond):
    N_CASES[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


# ------------------------------------------------------------------------------------------------ log lines
def FT(n, dt, draws=3000, cg=0):
    return 'FrameTrace: n=%d dt_us=%d lat_us=5 gpu_proc=0 draws=%d cpu_main_us=1 cpu_gpu_us=%d cpu_present_us=1' % (n, dt, draws, cg)


def FX(n, skip=0, held=0):
    return 'FrameTrace-x: n=%d rec_pack=0 skc_held=0 skc_held_inc=%d skc_ap_skip=%d skc_bad=0 sf_bad=0' % (n, held, skip)


def log_lines(tag, level=None, frames=None, dt=16667, pre=(), mid=(), post=(), entered=True, pcw=None, scene_draws=3000, between=()):
    a = S.ARMS[tag]
    level = level or a['level']
    pcw = a['pcw'] if pcw is None else pcw
    out = ['S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=0' % pcw]
    out += list(pre)
    out.append('GuestOut: boot')
    for n in range(1, 4):
        out += [FT(n, 16667, 5), FX(n)]
    out += list(between)
    if entered:
        out.append('GuestOut: Level has started: %s' % level)
    nfr = frames if frames is not None else 0
    for n in range(4, 4 + 1 + nfr):
        out += [FT(n, dt if n > 4 else 16667, scene_draws if n >= 4 else 5), FX(n)]
    out += list(mid)
    out += list(post)
    return out


def hold_frames(us):
    """frames of 16 667 us after the first scene frame summing to >= us"""
    return (us + 16666) // 16667


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(('\n'.join(lines) + '\n').encode('ascii'))


def cache_json(tag, mode, ib=FS4, ia=None, src=None, ra=None, rg=None, ml=None, posts=True):
    cj = dict(arm_start=dict(utc='2026-10-04T10:00:00Z'), return_prev=dict(ok='1'),
              installed_before=dict(sha=ib, path='x'), installed_after=dict(sha=ib if ia is None else ia),
              man_pre_app=dict(sha='a1' * 32), man_pre_glc=dict(sha='b1' * 32), man_post_app=dict(sha='a2' * 32),
              man_post_glc=dict(sha='b2' * 32), glc_pre_copy=dict(sha='b1' * 32), installed_pre_copy=dict(sha='a1' * 32),
              return_app=dict(expected='a1' * 32, got='a1' * 32), return_glc=dict(expected='b1' * 32, got='b1' * 32))
    if mode == 'asis':
        cj['man_launch_glc'] = dict(sha='b1' * 32 if ml is None else ml)
    elif mode == 'full':
        cj['restore_app'] = dict(expected=SNAP_APP, got=SNAP_APP if ra is None else ra)
        cj['restore_glc'] = dict(expected=SNAP_DRV, got=SNAP_DRV if rg is None else rg)
        cj['man_launch_glc'] = dict(sha=SNAP_DRV if ml is None else ml)
    else:
        cj['restore_app'] = dict(expected='c1' * 32, got='c1' * 32 if ra is None else ra)
        cj['restore_glc'] = dict(expected='d1' * 32, got='d1' * 32 if rg is None else rg)
        cj['man_launch_glc'] = dict(sha='d1' * 32 if ml is None else ml)
    if tag == 's12_gw' and posts:
        cj['app_post_copy'] = dict(sha='c1' * 32, path='x')
        cj['glc_post_copy'] = dict(sha='d1' * 32, path='x')
    return cj


def run_json(tag, binary=BIN, env=None, attempts=None, hold=None, gates='', val=None, prereg=None, guest=None):
    a = S.ARMS[tag]
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1', KYTY_GUEST_ARGS='-lvl %s' % a['level'],
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_S_PCW=a['pcw'],
             KYTY_GATE_FILE=LD.replace('/', '\\') + '\\gates.req', KYTY_SAMPLE_GATE=LD.replace('/', '\\') + '\\sample.req')
    if a['cls'] == 'T':
        e.update(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
    if a['val']:
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    if a['rec']:
        e['KYTY_REC'] = LD.replace('/', '\\') + '\\rec_%s.mp4' % tag
    if env is not None:
        e = env(e)
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'g']
    if (a['val'] if val is None else val):
        cmd += ['--vulkan-validation', 'true']
    return dict(tag=tag, binary_sha256=binary, env=e, cmdline=cmd,
                attempts=attempts if attempts is not None else [dict(label='attempt 1', outcome='ok')],
                hold_s=a['hold'] if hold is None else hold, gates=gates,
                guest_args=guest or '-lvl %s' % a['level'],
                prereg=prereg if prereg is not None else dict(sha256=PRED_SHA, path=PRED))


def mkarm(tag, lines, stdout=('Shaders: none',), js=None, cj=None, idx=3600, gl=0, sheet=True, blob=None, ld=LD):
    shutil.rmtree(ld, ignore_errors=True)
    os.makedirs(os.path.join(ld, 'runs_s'))
    a = S.ARMS[tag]
    write(os.path.join(ld, 'log_%s.txt' % tag), lines)
    if stdout is not None:
        write(os.path.join(ld, 'stdout_%s.txt' % tag), list(stdout))
    with open(os.path.join(ld, '%s.json' % tag), 'w') as f:
        json.dump(js if js is not None else run_json(tag), f)
    with open(os.path.join(ld, 'runs_s', '%s.cache.json' % tag), 'w') as f:
        json.dump(cj if cj is not None else cache_json(tag, a['mode']), f)
    if a['rec']:
        if idx is not None:
            write(os.path.join(ld, 'rec_%s.mp4.idx' % tag), ['%d 0' % i for i in range(idx)])
        if gl is not None:
            write(os.path.join(ld, 'glitch_%s.txt' % tag), ['x: %s frames' % idx,'one-frame glitches: %d' % gl])
        if sheet:
            write(os.path.join(ld, 'sheet_%s.txt' % tag), ['sheet: x.png frames 1 step 1 tiles 8x6'])
    if blob is not None:
        write(os.path.join(ld, 'app_post', 's12_gw', 'MANIFEST.txt'), blob)


def score(tag):
    with contextlib.redirect_stdout(io.StringIO()):
        return S.score(tag, LD, PRED, A)


def row(r, prefix):
    for name, ok in r['members']:
        if name.startswith(prefix):
            return ok
    for x in r['admit']:
        if x[0].startswith(prefix):
            return x[1]
    return 'absent'


H300 = hold_frames(300000000)
DUAL = 'DualSrcBlend: supported=1 enabled=1'
VKW = '[Vulkan][W][2] a warning'
BLOB_OK = ['PipelineCache/PPSA21564.bin %d %s' % (SNAP_SIZE + 1000, NEWSHA)]
ok = True

# ------------------------------------------------------------------------------------------------ constants and plan
ok &= case('order', S.ORDER == ('s12_w', 's12_v', 's12_gw', 's12_gr', 's12_v0'))
ok &= case('plan s12_w', S.plan('s12_w') == 's12 underwater_aerial_garden M asis 310 1 - 300 600 0 1 w')
ok &= case('plan s12_v', S.plan('s12_v') == 's12 underwater_aerial_garden M asis 330 1 - 300 480 1 0 v')
ok &= case('plan s12_gw', S.plan('s12_gw') == 's12 hero_kratos T full 330 1 - 100 480 1 0 gw')
ok &= case('plan s12_gr', S.plan('s12_gr') == 's12 hero_kratos T integrity 120 1 s12_gw 100 480 1 0 gr')
ok &= case('plan s12_v0', S.plan('s12_v0') == 's12 underwater_aerial_garden M asis 330 0 - 300 480 1 0 v0')
ok &= case('constants', S.BIN_S12 == BIN and S.INST_OK == (FS4, FS5) and S.SNAP_BIN_SHA == SNAP_BIN and S.SNAP_BIN_SIZE == SNAP_SIZE
           and S.BLOB_PREFIX == 76 and S.HOLD_MIN_US == 300000000 and S.FRAMES_VIDEO == 3000 and S.K2_US == 1000000
           and S.K3_US == 100000 and S.SNAP_APP == SNAP_APP and S.SNAP_DRV == SNAP_DRV and S.VK_LIMIT == '100000000')
ok &= case('BLOB_PREFIX = snap0 size - the loaded N of the integrity arms of S10 (94 435 713 - 94 435 637)', SNAP_SIZE - 94435637 == 76)

# ------------------------------------------------------------------------------------------------ environment
for t in S.ORDER:
    ok &= case('env exact %s' % t, S.env_row(t, run_json(t)['env'])[0])
ok &= case('env W carries the VK keys', 'VK_LAYER_PATH' in S.expected_env('s12_w')[0] and
           S.expected_env('s12_w')[0]['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] == '100000000' and 'VK_LAYER_PATH' not in S.expected_env('s12_v')[0])
ok &= case('env T carries AV trace', S.expected_env('s12_gw')[0].get('KYTY_AV_TRACE') == '1' and
           'KYTY_AV_TRACE' not in S.expected_env('s12_v')[0])
ok &= case('env v0 names KYTY_S_PCW=0', S.expected_env('s12_v0')[0]['KYTY_S_PCW'] == '0' and S.expected_env('s12_v')[0]['KYTY_S_PCW'] == '1')
ok &= case('env W has no KYTY_REC', 'KYTY_REC' not in S.expected_env('s12_w')[1] and 'KYTY_REC' in S.expected_env('s12_v')[1])


def env_with(**kw):
    def f(e):
        e = dict(e)
        for k, v in kw.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
        return e
    return f


ok &= case('env extra key fails', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_S_PCW_FORCE_MS='15000'))['env'])[0])
ok &= case('env missing KYTY_S_PCW fails (Z3)', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_S_PCW=None))['env'])[0])
ok &= case('env KYTY_S_PCW=0 on s12_v fails', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_S_PCW='0'))['env'])[0])
ok &= case('env filter key fails', not S.env_row('s12_w', run_json('s12_w', env=env_with(VK_LAYER_MESSAGE_ID_FILTER='x'))['env'])[0])
ok &= case('env limit value fails', not S.env_row('s12_w', run_json('s12_w', env=env_with(VK_LAYER_DUPLICATE_MESSAGE_LIMIT='1000000'))['env'])[0])
ok &= case('env rec path suffix fails', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_REC='C:\\x\\rec_s12_v0.mp4'))['env'])[0])
ok &= case('env gate path suffix fails', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_GATE_FILE='C:\\x\\g.req'))['env'])[0])
ok &= case('env checkpoints fails', not S.env_row('s12_v', run_json('s12_v', env=env_with(KYTY_GPU_CHECKPOINTS='1'))['env'])[0])

# ------------------------------------------------------------------------------------------------ W arm
WL = log_lines('s12_w', frames=H300, pre=[DUAL, VKW])
mkarm('s12_w', WL)
r = score('s12_w')
ok &= case('W clean PASS', r['word'] == 'PASS')
ok &= case('W binary named by binary_sha256, installed before printed apart', r['binary'] == BIN and r['installed_before'] == FS4)
mkarm('s12_w', log_lines('s12_w', frames=H300 - 1, pre=[DUAL, VKW]))
ok &= case('W hold below 300 s FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[DUAL, VKW], mid=['[Vulkan][E][2] boom']))
ok &= case('W [Vulkan][E] in log FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', WL, stdout=['[Vulkan][E] boom'])
ok &= case('W [Vulkan][E] in stdout FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[DUAL]))
ok &= case('W without [Vulkan][W] FAIL (positive control)', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[DUAL, VKW], mid=['x this will be the last time reporting it']))
ok &= case('W limit line in log FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', WL, stdout=['x this will be the last time reporting it'])
ok &= case('W limit line in stdout FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[VKW], mid=[DUAL]))
ok &= case('W DualSrcBlend after the first GuestOut FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[VKW], between=[DUAL]))
ok &= case('W DualSrcBlend between the first GuestOut and the entry FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=['DualSrcBlend: supported=1 enabled=0', VKW]))
ok &= case('W DualSrcBlend enabled=0 FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=['DualSrcBlend: supported=0 enabled=1', VKW]))
ok &= case('W DualSrcBlend supported=0 FAIL', score('s12_w')['word'] == 'FAIL')
mkarm('s12_w', log_lines('s12_w', frames=H300, pre=[DUAL, VKW], mid=['--- Fatal Error ---']))
ok &= case('W death marker FAIL', score('s12_w')['word'] == 'FAIL' and score('s12_w')['death'] == 1)
mkarm('s12_w', WL, js=run_json('s12_w', val=False))
ok &= case('W without validation NOT_ADMITTED', score('s12_w')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', log_lines('s12_v', frames=H300), js=run_json('s12_v', val=True))
ok &= case('V with validation NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')

# ------------------------------------------------------------------------------------------------ V arm
VL = log_lines('s12_v', frames=H300)
mkarm('s12_v', VL)
ok &= case('V clean PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', log_lines('s12_v', frames=20000, dt=15000))
ok &= case('V hold exactly 300 000 000 us PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', log_lines('s12_v', frames=20000, dt=15000, between=['GuestOut: Level has started: hub_title']))
ok &= case('V another level starting before the entry is not the entry PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL, gl=0)
write(os.path.join(LD, 'glitch_s12_v.txt'), ['x: 3600 frames'])
ok &= case('V glitch file without its line NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', VL, idx=2999)
ok &= case('V video 2999 FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', VL, idx=3000)
ok &= case('V video 3000 PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL, idx=None)
ok &= case('V no index NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', VL, gl=1)
ok &= case('V one glitch FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', VL, gl=None)
ok &= case('V glitch unread NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', VL, sheet=False)
ok &= case('V no sheet FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', VL, sheet=False)
write(os.path.join(LD, 'sheet_s12_v.txt'), ['ffmpeg failed'])
ok &= case('V sheet output without its sheet line FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', log_lines('s12_v', frames=H300, mid=[FT(9000, 1000000), FX(9000)]))
ok &= case('V frame of exactly 1 s FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', log_lines('s12_v', frames=H300, mid=[FT(9000, 999999), FX(9000)]))
ok &= case('V frame of 999 999 us PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL, stdout=['Unhandled exception: x'])
ok &= case('V death in stdout FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', log_lines('s12_v', frames=H300 - 1))
ok &= case('V hold below 300 s FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', log_lines('s12_v', frames=10, mid=['GuestOut: Level has started: other'] +
                         sum(([FT(20000 + i, 16667), FX(20000 + i)] for i in range(H300)), [])))
ok &= case('V hold stops at a scene change FAIL', score('s12_v')['word'] == 'FAIL')
mkarm('s12_v', log_lines('s12_v', frames=H300, entered=False))
ok &= case('V not entered NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', log_lines('s12_v', frames=H300, scene_draws=99))
ok &= case('V entry without a scene frame (draws 99) NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', log_lines('s12_v', frames=H300, scene_draws=100))
ok &= case('V scene frame at draws 100 PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v0', log_lines('s12_v0', frames=H300))
ok &= case('v0 clean REFERENCE_PASS', score('s12_v0')['word'] == 'REFERENCE_PASS')
mkarm('s12_v0', log_lines('s12_v0', frames=H300), gl=2)
ok &= case('v0 glitch REFERENCE_FAIL', score('s12_v0')['word'] == 'REFERENCE_FAIL')

# ------------------------------------------------------------------------------------------------ admission and the knob line
mkarm('s12_v', log_lines('s12_v', frames=H300, pcw='0'))
ok &= case('V knob line =0 NOT_ADMITTED (Z3)', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v0', log_lines('s12_v0', frames=H300, pcw='1'))
ok &= case('v0 knob line =1 NOT_ADMITTED (Z3)', score('s12_v0')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', [x.replace('FORCE_MS=0', 'FORCE_MS=15000') for x in VL])
ok &= case('V knob line FORCE_MS=15000 NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', [x for x in VL if not x.startswith('S-pcw:')])
ok &= case('V no knob line NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL + ['S-pcw: KYTY_S_PCW=0 KYTY_S_PCW_FORCE_MS=0'])
ok &= case('V a second knob line =0 NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', binary=FS4))
ok &= case('V arm binary FS4 by binary_sha256 NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, cj=cache_json('s12_v', 'asis', ib=FS5))
ok &= case('V installed before FS5 PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL, cj=cache_json('s12_v', 'asis', ib=OTHER))
ok &= case('V installed before 540c035a NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, cj=cache_json('s12_v', 'asis', ib=BIN))
ok &= case('V installed before = the arm binary NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, cj=cache_json('s12_v', 'asis', ia=FS5))
ok &= case('V installed after != before NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
cj = cache_json('s12_v', 'asis')
cj['return_app'] = dict(expected='a1' * 32, got='a3' * 32)
mkarm('s12_v', VL, cj=cj)
ok &= case('V return_app differs NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
cj = cache_json('s12_v', 'asis')
cj['return_glc'] = dict(expected='b1' * 32)
mkarm('s12_v', VL, cj=cj)
ok &= case('V return_glc missing got NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
cj = cache_json('s12_v', 'asis')
cj['return_glc'] = {}
mkarm('s12_v', VL, cj=cj)
ok &= case('V return_glc empty NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
cj = cache_json('s12_v', 'asis')
cj['return_prev'] = dict(ok='0')
mkarm('s12_v', VL, cj=cj)
ok &= case('V return_prev 0 NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
cj = cache_json('s12_v', 'asis')
cj['restore_app'] = dict(expected=SNAP_APP, got=SNAP_APP)
mkarm('s12_v', VL, cj=cj)
ok &= case('V asis with a restore NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, cj=cache_json('s12_v', 'asis', ml='b9' * 32))
ok &= case('V asis man_launch_glc != man_pre_glc NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, cj=None)
os.remove(os.path.join(LD, 'runs_s', 's12_v.cache.json'))
ok &= case('V no cache json NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', attempts=[dict(label='attempt 1'), dict(label='attempt 2')]))
ok &= case('V two attempts NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', attempts=[dict(label='attempt 1', pipeline_cache_off=True)]))
ok &= case('V pipeline cache retry NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', hold=331))
ok &= case('V hold 331 NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', gates='x'))
ok &= case('V gates not empty NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', guest='-lvl hero_kratos'))
ok &= case('V guest args NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', prereg=dict(sha256='0' * 64, path=PRED)))
ok &= case('V prereg sha NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', prereg=dict(sha256=PRED_SHA, path=PRED.replace('/', '\\'))))
ok &= case('V prereg path with backslashes PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL, js=run_json('s12_v', prereg=dict(sha256=PRED_SHA, path=PRED.replace('08_s', '07_s'))))
ok &= case('V prereg path of another seal NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')
mkarm('s12_v', VL, js=run_json('s12_v', env=env_with(KYTY_GAME_PATCH='p.txt')))
ok &= case('V env with KYTY_GAME_PATCH NOT_ADMITTED', score('s12_v')['word'] == 'NOT_ADMITTED')

# ------------------------------------------------------------------------------------------------ interference
mkarm('s12_v', VL + ['Window 1 minimized'])
ok &= case('V window minimized INTERFERENCE', score('s12_v')['word'] == 'INTERFERENCE')
mkarm('s12_v', VL + ['Window 1 restored', 'Window 1 lost keyboard focus'])
ok &= case('V window restored / focus alone PASS', score('s12_v')['word'] == 'PASS')
mkarm('s12_v', VL + ['Recovering Vulkan swapchain'])
ok &= case('V Recovering Vulkan swapchain INTERFERENCE', score('s12_v')['word'] == 'INTERFERENCE')
mkarm('s12_v', VL + ['GamePatch: applied x'])
ok &= case('V GamePatch line INTERFERENCE', score('s12_v')['word'] == 'INTERFERENCE')
mkarm('s12_v', VL + ['x GamePatch: in a text'])
ok &= case('V GamePatch inside a line is not the line PASS', score('s12_v')['word'] == 'PASS')

# ------------------------------------------------------------------------------------------------ missing files
mkarm('s12_v', VL, stdout=None)
ok &= case('V stdout missing NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', VL)
os.remove(os.path.join(LD, 's12_v.json'))
ok &= case('V json missing NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')
mkarm('s12_v', VL)
os.remove(os.path.join(LD, 'log_s12_v.txt'))
ok &= case('V log missing NOT_EVALUABLE', score('s12_v')['word'] == 'NOT_EVALUABLE')

# ------------------------------------------------------------------------------------------------ s12_gw blob (Z2)
GWL = log_lines('s12_gw', frames=200, pre=['Vulkan pipeline cache: loading _PipelineCache\\PPSA21564.bin',
                                         'Vulkan pipeline cache: loaded 94435637 bytes from _PipelineCache\\PPSA21564.bin'],
                post=['Vulkan pipeline cache: saved 94436000 bytes to _PipelineCache\\PPSA21564.bin (5000 us)',
                      'Vulkan pipeline cache: saved 94436637 bytes to _PipelineCache\\PPSA21564.bin (5000 us)'])
mkarm('s12_gw', GWL, blob=BLOB_OK)
r = score('s12_gw')
ok &= case('gw blob grown PASS', r['word'] == 'PASS')
ok &= case('gw data: saves 2 last 94436637, loaded [94435637]', any('saves: 2, last 94436637 bytes, forced 0' in d and
                                                                   '[94435637]' in d for d in r['data']))
ok &= case('gw data: pcw recipes NOT_EVALUABLE when none', any('pcw recipes: NOT_EVALUABLE' in d for d in r['data']))
ok &= case('gw data: held frames NOT_EVALUABLE when none', any('held frames >= 100 ms' in d and 'NOT_EVALUABLE' in d for d in r['data']))
mkarm('s12_gw', GWL, blob=['PipelineCache/PPSA21564.bin %d %s' % (SNAP_SIZE + 1000, SNAP_BIN)])
ok &= case('gw sha = snap0 FAIL', score('s12_gw')['word'] == 'FAIL')
mkarm('s12_gw', GWL, blob=['PipelineCache/PPSA21564.bin %d %s' % (SNAP_SIZE, NEWSHA)])
ok &= case('gw size = snap0 FAIL', score('s12_gw')['word'] == 'FAIL')
mkarm('s12_gw', GWL, blob=['PipelineCache/PPSA21564.bin %d %s' % (SNAP_SIZE + 1, NEWSHA)])
ok &= case('gw size = snap0 + 1 PASS', score('s12_gw')['word'] == 'PASS')
mkarm('s12_gw', GWL, blob=['PipelineCache/PPSA21564.6e17b0d77613b26c.bin 5 %s' % NEWSHA])
r = score('s12_gw')
ok &= case('gw bin absent, no tmp FAIL (the present row fails)', r['word'] == 'FAIL' and row(r, 'PPSA21564.bin present') is False)
mkarm('s12_gw', GWL, blob=['PipelineCache/PPSA21564.bin.tmp 5 %s' % NEWSHA])
r = score('s12_gw')
ok &= case('gw bin absent with tmp INTERFERENCE (Z2)', r['word'] == 'INTERFERENCE' and 'tmp' in r['why'])
mkarm('s12_gw', GWL, blob=BLOB_OK + ['PipelineCache/PPSA21564.bin.tmp 5 %s' % NEWSHA])
r = score('s12_gw')
ok &= case('gw bin present with tmp PASS, tmp printed', r['word'] == 'PASS' and any('.tmp present True' in d for d in r['data']))
mkarm('s12_gw', GWL)
ok &= case('gw no manifest FAIL', score('s12_gw')['word'] == 'FAIL')
mkarm('s12_gw', GWL + ['ErrorDeviceLost'], blob=BLOB_OK)
ok &= case('gw death FAIL', score('s12_gw')['word'] == 'FAIL')
mkarm('s12_gw', GWL, blob=BLOB_OK, cj=cache_json('s12_gw', 'full', posts=False))
ok &= case('gw post copies not recorded NOT_ADMITTED', score('s12_gw')['word'] == 'NOT_ADMITTED')
mkarm('s12_gw', GWL, blob=BLOB_OK, cj=cache_json('s12_gw', 'full', ra='a9' * 32))
ok &= case('gw restore app != snap0 NOT_ADMITTED', score('s12_gw')['word'] == 'NOT_ADMITTED')
mkarm('s12_gw', GWL, blob=BLOB_OK, cj=cache_json('s12_gw', 'full', rg='a9' * 32, ml='a9' * 32))
ok &= case('gw restore glc != snap0_drv NOT_ADMITTED', score('s12_gw')['word'] == 'NOT_ADMITTED')
mkarm('s12_gw', GWL, blob=BLOB_OK, cj=cache_json('s12_gw', 'full', ml='a9' * 32))
ok &= case('gw man_launch_glc != restore NOT_ADMITTED', score('s12_gw')['word'] == 'NOT_ADMITTED')
SAVES = ['Vulkan pipeline cache: save failed (ErrorOutOfHostMemory, 0 bytes)', 'Vulkan pipeline cache: failed to write x',
         'Vulkan pipeline cache: failed to create cache directory',
         'Vulkan pipeline cache: saved 7 bytes to _PipelineCache\\PPSA21564.bin (1 us) forced', 'Vulkan pipeline cache: zzz']
mkarm('s12_gw', GWL + SAVES, blob=BLOB_OK)
r = score('s12_gw')
ok &= case('gw save classes counted (Z1)', any('saves: 3, last 7 bytes, forced 1, save failed 1, failed to write 1, failed to create '
                                               'cache directory 1' in d for d in r['data']) and
           any('unknown 1' in d for d in r['data']))

# ------------------------------------------------------------------------------------------------ s12_gr load classes (Z1)
GW_SAVED = 94436637
GW_POST = ['PipelineCache/PPSA21564.bin %d %s' % (GW_SAVED + 76, NEWSHA)]


def gr_arm(pre, gw_post=GW_POST, gw_saves=(GW_SAVED,), more=()):
    mkarm('s12_gr', log_lines('s12_gr', frames=200, pre=pre, post=list(more)), cj=cache_json('s12_gr', 'integrity'))
    write(os.path.join(LD, 'log_s12_gw.txt'), log_lines('s12_gw', frames=5, post=[
        'Vulkan pipeline cache: saved %d bytes to _PipelineCache\\PPSA21564.bin (5 us)' % n for n in gw_saves]))
    with open(os.path.join(LD, 'runs_s', 's12_gw.cache.json'), 'w') as f:
        json.dump(cache_json('s12_gw', 'full'), f)
    if gw_post is not None:
        write(os.path.join(LD, 'app_post', 's12_gw', 'MANIFEST.txt'), gw_post)


LOADING = 'Vulkan pipeline cache: loading _PipelineCache\\PPSA21564.bin'


def LOADED(n):
    return 'Vulkan pipeline cache: loaded %d bytes from _PipelineCache\\PPSA21564.bin' % n


gr_arm([LOADING, LOADED(GW_SAVED)])
ok &= case('gr loaded = last saved = size - 76 PASS', score('s12_gr')['word'] == 'PASS')
gr_arm([LOADING, LOADED(GW_SAVED)], gw_saves=(GW_SAVED, GW_SAVED + 5))
r = score('s12_gr')
ok &= case('gr loaded != the last saved (state (e)) FAIL', r['word'] == 'FAIL' and row(r, 'N = the last') is False
           and row(r, 'N = size') is True)
gr_arm([LOADING, LOADED(GW_SAVED)], gw_saves=(GW_SAVED + 5, GW_SAVED))
ok &= case('gr loaded = the LAST saved, not the first PASS', score('s12_gr')['word'] == 'PASS')
gr_arm([LOADING, LOADED(GW_SAVED)], gw_post=['PipelineCache/PPSA21564.bin %d %s' % (GW_SAVED + 75, NEWSHA)])
r = score('s12_gr')
ok &= case('gr size - 76 != N FAIL', r['word'] == 'FAIL' and row(r, 'N = size') is False)
gr_arm([LOADING, LOADED(GW_SAVED)], gw_post=None)
ok &= case('gr no gw manifest FAIL', score('s12_gr')['word'] == 'FAIL')
gr_arm([LOADING, LOADED(GW_SAVED)], gw_saves=())
ok &= case('gr no gw saved line FAIL', score('s12_gr')['word'] == 'FAIL')
gr_arm(['Vulkan pipeline cache: initializing _PipelineCache\\PPSA21564.bin', 'Vulkan pipeline cache: initialized empty'])
r = score('s12_gr')
ok &= case('gr no loaded line: FAIL with the cause named', r['word'] == 'FAIL' and
           any('no loaded line: initializing 1, initialized empty 1' in n and v is False for n, v in r['members']))
gr_arm([])
r = score('s12_gr')
ok &= case('gr no load line at all: FAIL, cause named', r['word'] == 'FAIL' and
           any('no load line of any class' in n for n, v in r['members']))
gr_arm([LOADING, LOADED(GW_SAVED), LOADED(GW_SAVED)])
r = score('s12_gr')
ok &= case('gr two loaded lines FAIL: the one-loaded row and the N rows fail', r['word'] == 'FAIL' and row(r, 'exactly one "loaded') is False and row(r, 'N = the last') is False and row(r, 'N = size') is False)
gr_arm([LOADING, LOADING, LOADED(GW_SAVED)])
ok &= case('gr two loading lines FAIL', score('s12_gr')['word'] == 'FAIL')
gr_arm([LOADED(GW_SAVED)])
ok &= case('gr no loading line FAIL', score('s12_gr')['word'] == 'FAIL')
for bad in ('initializing x', 'initialized empty', 'invalidating x (invalid file size)', 'driver rejected x (e); starting empty',
            'disabled (ErrorInitializationFailed)'):
    gr_arm([LOADING, LOADED(GW_SAVED), 'Vulkan pipeline cache: %s' % bad])
    r = score('s12_gr')
    ok &= case('gr bad class "%s" FAIL' % bad.split(' (')[0], r['word'] == 'FAIL' and
               row(r, '0 "%s' % bad.split(' x')[0].split(' (')[0]) is False)
gr_arm([LOADING, LOADED(GW_SAVED)], more=['--- Error ---'])
ok &= case('gr death FAIL', score('s12_gr')['word'] == 'FAIL')
gr_arm([LOADING, LOADED(GW_SAVED)])
os.remove(os.path.join(LD, 'glitch_s12_gr.txt'))
ok &= case('gr glitch unread NOT_EVALUABLE', score('s12_gr')['word'] == 'NOT_EVALUABLE')
gr_arm([LOADING, LOADED(GW_SAVED)])
os.remove(os.path.join(LD, 'sheet_s12_gr.txt'))
ok &= case('gr no sheet FAIL', score('s12_gr')['word'] == 'FAIL')
gr_arm([LOADING, LOADED(GW_SAVED)])
cj = cache_json('s12_gr', 'integrity', ra='c9' * 32)
with open(os.path.join(LD, 'runs_s', 's12_gr.cache.json'), 'w') as f:
    json.dump(cj, f)
ok &= case('gr restore app != the post copy of gw NOT_ADMITTED', score('s12_gr')['word'] == 'NOT_ADMITTED')
gr_arm([LOADING, LOADED(GW_SAVED)])
os.remove(os.path.join(LD, 'runs_s', 's12_gw.cache.json'))
ok &= case('gr without the gw cache json NOT_ADMITTED', score('s12_gr')['word'] == 'NOT_ADMITTED')

# ------------------------------------------------------------------------------------------------ item 414 (g)(2) through sc_s
REC_LINE = 'AvTrace: pcw recipes copied=10 count=1843 lock_us=12 hold_us=4321'
T_PRE = [LOADING, LOADED(94435637)]
lines = log_lines('s12_gw', frames=20, pre=T_PRE)
k = max(i for i, x in enumerate(lines) if x.startswith('FrameTrace: n=10 '))
lines[k] = FT(10, 150000)
lines[k + 1] = FX(10, held=1)
lines.insert(k, 'PipelinePrecache: saved 1843 recipes (19822711 bytes)')
lines.insert(k, REC_LINE)
j = max(i for i, x in enumerate(lines) if x.startswith('FrameTrace: n=15 '))
lines[j] = FT(15, 120000)
lines.append('AvTrace: pcw recipes copied=0 count=1843 lock_us=3 hold_us=79')
mkarm('s12_gw', lines, blob=BLOB_OK)
r = score('s12_gw')
d = [x for x in r['data'] if 'held frames >= 100 ms' in x]
ok &= case('414 (g)(2): a held 150 ms frame with a recipes save is PCW with its hold_us', len(d) == 1 and
           '1 held: n 10 150.0 ms PCW/' in d[0] and 'recipes-lines 1 hold_us 4321 +recipes-save' in d[0] and 'shown >= 100 ms 1' in d[0])
ok &= case('414 (g)(2): pcw recipes line counted', any('pcw recipes: lines 2, hold_us sum 4400 max 4321, lock_us max 12' in x
                                                     for x in r['data']))
h = S.held_data(os.path.join(LD, 'log_s12_gw.txt'), os.path.join(LD, 'stdout_s12_gw.txt'), 'hero_kratos', A)
ok &= case('held_data attribution on (T-3 0 = 0, T-4 no queue and no precache line)', h['attr_ok'] and h['t3'] and h['t4'])
ok &= case('held_data not entered -> None', S.held_data(os.path.join(LD, 'log_s12_gw.txt'), os.path.join(LD, 'stdout_s12_gw.txt'),
                                                        'nolevel', A) is None)
ok &= case('fmt_held None', S.fmt_held(None).startswith('NOT_EVALUABLE'))
ok &= case('fmt_rec empty', S.fmt_rec([]).startswith('NOT_EVALUABLE'))
mkarm('s12_v', VL)
ok &= case('no 414 data line on an M arm', not any('pcw recipes' in x for x in score('s12_v')['data']))

# ------------------------------------------------------------------------------------------------ vc classes and blob_state
ok &= case('vc_class loading / loaded / saved / save failed', S.vc_class(b'loading x') == 'loading' and S.vc_class(b'loaded 5 bytes')
           == 'loaded' and S.vc_class(b'saved 5 bytes') == 'saved' and S.vc_class(b'save failed (x)') == 'save failed')
ok &= case('vc_class initializing / initialized empty', S.vc_class(b'initializing p') == 'initializing' and
           S.vc_class(b'initialized empty') == 'initialized empty')
ok &= case('vc_class unknown None', S.vc_class(b'zz') is None)
write(os.path.join(LD, 'bs', 'MANIFEST.txt'), ['PipelineCache/PPSA21564.bin 10 %s' % NEWSHA, 'PipelineCache/PPSA21564.bin.tmp 3 x',
                                               'ShaderCache_PPSA21564/a.bin 1 y', 'bad line'])
b = S.blob_state(os.path.join(LD, 'bs'))
ok &= case('blob_state reads bin and tmp', b == dict(manifest=True, bin=True, size=10, sha=NEWSHA, tmp=True))
ok &= case('blob_state without manifest', S.blob_state(os.path.join(LD, 'nope'))['manifest'] is False)

# ------------------------------------------------------------------------------------------------ order (--allowed)
OD = os.path.join(str(BASE), 'order')


def made(tags, words=None, death=None, posts=True):
    shutil.rmtree(OD, ignore_errors=True)
    os.makedirs(os.path.join(OD, 'runs_s'))
    for t in tags:
        write(os.path.join(OD, '%s.json' % t), ['{}'])
        sj = dict(word=(words or {}).get(t, 'PASS'), death=(death or {}).get(t, 0), why='')
        if (words or {}).get(t) != 'unscored':
            with open(os.path.join(OD, 'runs_s', '%s.score.json' % t), 'w') as f:
                json.dump(sj, f)
    if posts:
        for d in ('app_post', 'glc_post'):
            write(os.path.join(OD, d, 's12_gw', 'MANIFEST.txt'), ['x'])


made([])
ok &= case('allowed s12_w first', S.allowed('s12_w', OD)[0] == 0)
ok &= case('allowed s12_v before s12_w -> 1', S.allowed('s12_v', OD)[0] == 1)
ok &= case('allowed unknown -> 1', S.allowed('s12_x', OD)[0] == 1)
made(['s12_w'])
ok &= case('allowed s12_w made -> 1', S.allowed('s12_w', OD)[0] == 1)
ok &= case('allowed s12_v after s12_w', S.allowed('s12_v', OD)[0] == 0)
made(['s12_w'], words={'s12_w': 'FAIL'})
ok &= case('allowed after a FAIL without death', S.allowed('s12_v', OD)[0] == 0)
made(['s12_w'], death={'s12_w': 1}, words={'s12_w': 'FAIL'})
ok &= case('allowed stops after a death marker (rc 6)', S.allowed('s12_v', OD)[0] == 6)
made(['s12_w'], words={'s12_w': 'INTERFERENCE'})
ok &= case('allowed stops after INTERFERENCE (rc 6)', S.allowed('s12_v', OD)[0] == 6)
made(['s12_w'], words={'s12_w': 'unscored'})
ok &= case('allowed refuses an unscored previous arm (rc 6)', S.allowed('s12_v', OD)[0] == 6)
made(['s12_w', 's12_v', 's12_gw'])
ok &= case('allowed s12_gr after gw PASS', S.allowed('s12_gr', OD)[0] == 0)
made(['s12_w', 's12_v', 's12_gw'], words={'s12_gw': 'FAIL'})
ok &= case('allowed s12_gr after gw FAIL', S.allowed('s12_gr', OD)[0] == 0)
made(['s12_w', 's12_v', 's12_gw'], words={'s12_gw': 'NOT_ADMITTED'})
ok &= case('allowed s12_gr refused after gw NOT_ADMITTED (rc 6)', S.allowed('s12_gr', OD)[0] == 6)
made(['s12_w', 's12_v', 's12_gw'], words={'s12_gw': 'NOT_EVALUABLE'})
ok &= case('allowed s12_gr refused after gw NOT_EVALUABLE (rc 6)', S.allowed('s12_gr', OD)[0] == 6)
made(['s12_w', 's12_v', 's12_gw'], posts=False)
ok &= case('allowed s12_gr refused without the post copies (rc 6)', S.allowed('s12_gr', OD)[0] == 6)
made(['s12_w', 's12_v', 's12_gw', 's12_gr'])
ok &= case('allowed s12_v0 last', S.allowed('s12_v0', OD)[0] == 0)
made(['s12_w', 's12_v', 's12_gw', 's12_gr'], words={'s12_v': 'NOT_EVALUABLE'})
ok &= case('allowed s12_v0 after a NOT_EVALUABLE arm', S.allowed('s12_v0', OD)[0] == 0)

# ------------------------------------------------------------------------------------------------ seal
SD = os.path.join(str(BASE), 'seal')
os.makedirs(SD, exist_ok=True)
names = []
for n in S.SEALED_NAMES:
    p = n if ':' in n else os.path.join(SD, n)
    names.append((n, p))


def mkseal(skip=None, badsha=None, binline=True, binsha=BIN):
    lines = []
    for n, p in names:
        if n == skip:
            continue
        if ':' in n:
            sha = hashlib.sha256(Path(n).read_bytes()).hexdigest()
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            Path(p).write_bytes(n.encode())
            sha = hashlib.sha256(n.encode()).hexdigest()
        lines.append('seal: %s %s' % ('0' * 64 if n == badsha else sha, n))
    if binline:
        lines.append('s12 binary: %s C:/kyty/s288/bin/kyty_emulator_adb0c82f.exe' % binsha)
    write(os.path.join(SD, 'seal.md'), lines)
    return os.path.join(SD, 'seal.md')


ok &= case('check_seal OK', S.check_seal(mkseal(), SD)[0])
ok &= case('check_seal a sha differs', not S.check_seal(mkseal(badsha='s12/sc_s12.py'), SD)[0])
ok &= case('check_seal a name missing', not S.check_seal(mkseal(skip='sc_s.py'), SD)[0])
ok &= case('check_seal an absolute name missing', not S.check_seal(mkseal(skip='C:/kyty/scripts/s51_vidglitch.py'), SD)[0])
ok &= case('check_seal no binary line', not S.check_seal(mkseal(binline=False), SD)[0])
ok &= case('check_seal another binary', not S.check_seal(mkseal(binsha=FS4), SD)[0])
ok &= case('check_seal no file', not S.check_seal(os.path.join(SD, 'none.md'), SD)[0])
ok &= case('sealed names', set(S.SEALED_NAMES) >= {'s12/go_s12.sh', 's12/sc_s12.py', 's12/test_sc_s12.py', 's12/mut_sc_s12.py',
                                                    'sc_s.py', 'cachex_s.py', 's9/enter_scene_s9.py', 'C:/kyty/s142/sc142.py'})

# ------------------------------------------------------------------------------------------------ main and ASCII
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--plan', 's12_gr'])
ok &= case('main --plan', rc == 0 and buf.getvalue().strip() == S.plan('s12_gr'))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--plan', 'zz'])
ok &= case('main --plan unknown rc 2', rc == 2)
saved = S.LD, S.PRED_PATH
S.LD, S.PRED_PATH = LD, PRED
mkarm('s12_v', VL)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--tag', 's12_v'])
out = buf.getvalue()
sj = json.load(open(os.path.join(LD, 'runs_s', 's12_v.score.json')))
ok &= case('main --tag writes the score json', rc == 0 and sj['word'] == 'PASS' and sj['binary'] == BIN and sj['death'] == 0)
ok &= case('main --tag output ASCII (cp1250 strict)', out.encode('cp1250', 'strict') == out.encode('ascii', 'strict'))
ok &= case('main --tag first line', out.startswith('ARM s12_v level underwater_aerial_garden kind v: PASS'))
mkarm('s12_v', VL, stdout=['--- Fatal Error ---'])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--tag', 's12_v'])
sj = json.load(open(os.path.join(LD, 'runs_s', 's12_v.score.json')))
ok &= case('main --tag writes the death count', rc == 0 and sj['death'] == 1 and sj['word'] == 'FAIL')
S.LD = OD
made(['s12_w', 's12_v', 's12_gw', 's12_gr'], words={'s12_gr': 'FAIL'})
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--summary'])
ok &= case('main --summary pair NOT PASS when s12_gr fails', '(3) pair s12_gw / s12_gr NOT PASS' in buf.getvalue())
made(['s12_w', 's12_v', 's12_gw', 's12_gr'])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--summary'])
ok &= case('main --summary pair PASS', '(3) pair s12_gw / s12_gr PASS;' in buf.getvalue())
made(['s12_w'])
S.LD = OD
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--allowed', 's12_v'])
ok &= case('main --allowed', rc == 0 and 'ALLOWED s12_v: yes' in buf.getvalue())
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--allowed', 's12_gw'])
ok &= case('main --allowed refuses out of order (rc 1, no)', rc == 1 and 'ALLOWED s12_gw: no' in buf.getvalue())
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main(['--summary'])
ok &= case('main --summary', rc == 0 and 'S12C (1) s12_w PASS; (2) s12_v NOT_MADE; (3) pair s12_gw / s12_gr NOT PASS' in buf.getvalue())
S.LD, S.PRED_PATH = saved
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = S.main([])
ok &= case('main no option rc 2', rc == 2)
ok &= case('asc', S.asc('a\u2014b') == 'a?b')

print('cases: %d' % N_CASES[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
