"""Fixtures of f30q_read.py (Track F link F30q, HPP-727; ROADMAP s122 item 664 (z)(1)-(5), item 665 (v) RC1-RC5 of F30p, (g)): a clean
synthetic tag of each form (w6 at s1; c6 at s1, s6 and s9 with the keys) reads ADMITTED with no STOP row; every harness member (binary T3,
FS11 before / after, env of the form incl. VK_LAYER_* at w6, the last --vulkan-validation true at w6 / false at c6, window, entry, events,
summary, signature) and every member of item 665 (v) flips the reading: RC1 (rts_inj_nos 0 / 1 at T, the tail after T), RC2 (difference
-1 / -2 / +1 / +2, a missing name, rts_inj as a prefix of the other four), RC3 (rts_bad_s = inj_s - 1 / - 2, rts_race = inj_race - 1 / - 2),
RC4 (floor(pb/4096) -1 / -2 / +1 / +2), (inj) at c6 (inj >= 1; inj 0 with none >= 1 - admitted, K_S NO; inj 0 with none 0 - STOP at
q >= 1 and at q = 0), RC5 / (D7) (launch sha, json sha, fork line, version strings, the version in the pinned copy), (D1) (the text of the
print place; value 5; two lines), (D5) 1499 / 1500 at c6 and a reference row at w6, the w6 members ([Vulkan][E], [Vulkan][W], DualSrcBlend
before / after the first GuestOut, limit line, death marker, lived, sum rts_inj); the inherited parse members (closing point T at distance
3 / 4, RC1 / RC2 / RC4 of F30l, the reconciliation with mode=6); the K_S row; the scene rows and the table; strict cp1250 output without
PYTHONIOENCODING; the last line is ALL OK.  Early-exit form of mutlib (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: f30q_read.py beside this file); the fixture directories live under BASE.
usage: python test_f30q_read.py [<f30q_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f30q_read.py')
BASE = Path(os.path.join(HERE, 'fx_f30q'))   # mutlib gives every job its own copy of this directory
_spec = importlib.util.spec_from_file_location('f30q_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f30q_read.py sha256 %s target f30q_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = '505969510fb20f7ce56a5195b3b6d2209af812bc0c2c85eccb6368a712b1bf34'   # literals, not the reader's constants (mutants)
FS11 = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
T2 = 'bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163'
TBIN = 'C:/kyty/f287/bin/kyty_emulator_50596951.exe'
FS11BIN = 'C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe'
T2BIN = 'C:/kyty/f287/bin/kyty_emulator_bba692c6.exe'
KREF = os.path.join(HERE, 'kref_f30q.tsv')
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
KEYS = ('@1300:a/@45 @1380:w/@45 @1500:w/@96 @1650:h/@975 @2600:f/@1003 @3550:w/@18 @3600:d/@30 @3650:s/@31 @3700:a/@31 '
        '@3750:w/@49 @3800:w/@90 @3900:h/@966 @4850:f/@984 @5800:w/@17 @5830:d/@25 @5860:s/@25 @5890:a/@25 @5920:w/@25')
LEVEL = {'s1': 'underwater_aerial_garden', 's9': 'underwater_aerial_garden', 's6': 'sponge_dirty_bath', 's2': 'hoover_beach'}
B8 = ('rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p', 'rts_bad_m', 'rts_bad_l')
I5 = ('rts_inj', 'rts_inj_s', 'rts_inj_race', 'rts_inj_nos', 'rts_inj_none')
FIELDS = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx',
          'rts_race', 'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
          'rts_xb_bound', 'rts_xb_pass', 'rts_early') + B8 + I5
NFR = 1600
NINJ = 156   # floor(1600 x 400 / 4096) = 156
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def frame(**kw):
    f = dict((k, 0) for k in FIELDS)
    f.update(rts_n=500, rts_pa=420, rts_chk=420, rts_pb=400, rts_chk_b=400)
    f.update(kw)
    return f


def env_of(scene, kind):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + LEVEL[scene], KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s',
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_RT_SKIP='6')
    if kind == 'w6':
        e.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    if scene == 's9':
        e['KYTY_KEYS'] = KEYS
    return e


INJ_FRAMES = list(range(200, 200 + NINJ))   # one perturbation per frame, the report carries S


def inject(f):
    f.update(rts_inj=1, rts_inj_s=1, rts_bad=1, rts_bad_noreg=1, rts_bad_b=1, rts_bad_s=1)


def spec(kind, scene):
    head = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', '  version: Fork build arigandores/KytyPS5 ea38426',
            'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
            'RtSkip: mode 6 ctx_slots=8 groups=11 rec_bytes=7192',
            'FixB42: mode=1 hit=2 applied=1 drawn=5 rearm=0 hit_all=2 last_frame=1 extent=480x270 cmask=0x1 clear=00000000/00000000']
    if kind == 'w6':
        head.append('DualSrcBlend: supported=1 enabled=1')
    mid = ['FixB42Ext: mode=1 extent=480x270 hit=6 applied=4 drawn=9 rearm=0 frame=50']
    for i in range(40):
        mid.append('RtSkipVerify: MISMATCH frame=%d bits=0x040 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=6' % (900 + i))
    if kind == 'w6':
        mid.append('[Vulkan][W] Validation Warning: x')
    frames = [frame() for _ in range(NFR)]
    for i in INJ_FRAMES:
        inject(frames[i])
    frames[50]['rts_xb_pass'] = 3
    frames[60]['rts_xb_ser'] = 2
    tail = ['LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0']
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    if kind == 'w6':
        cmd += ['--vulkan-validation', 'true']
    att = dict(outcome='ok', hold_exit=None, hold_s=150.1, started_s=30.0, stable_s=42.0, launch_sha256=TB)
    run = dict(binary_sha256=TB, env=env_of(scene, kind), cmdline=cmd, attempts=[att], guest_args='-lvl ' + LEVEL[scene], hold_s=150,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()), gates='', schedule='')
    side = dict(installed_before=FS11, installed_after=FS11, installed_sha=TB, level=LEVEL[scene])
    return dict(head=head, pre=[frame(rts_n=7, rts_pa=0, rts_chk=0, rts_pb=0, rts_chk_b=0) for _ in range(3)], entry=True, mid=mid,
                frames=frames, bda=[100] * NFR, tail=tail, run=run, side=side, scene=scene, kind=kind, stdout='', drop=set(), extra_draw=0,
                n0=(100 if scene == 's9' else 1), order=None)


def xline(n, f, drop=(), order=None):
    keys = list(f.keys()) if order is None else order + [k for k in f if k not in order]
    return 'FrameTrace-x: n=%d ds_ring_new=0 ' % n + ' '.join('%s=%d' % (k, f[k]) for k in keys if k not in drop)


def lines_of(s):
    L = list(s['head'])
    n = s['n0']
    for f in s['pre']:
        L += ['FrameTrace: n=%d dt_us=16000 draws=10' % n, 'FrameTrace-draw: n=%d logs=1 bda_scan=50' % n, xline(n, f, (), s['order'])]
        n += 1
    L.append('GuestOut: Level has started: ')
    if s['entry']:
        L.append('GuestOut: Level has started: %s' % LEVEL[s['scene']])
    L += s['mid']
    for i, f in enumerate(s['frames']):
        L += ['FrameTrace: n=%d dt_us=33000 draws=500' % n, 'FrameTrace-draw: n=%d logs=1 bda_scan=%d' % (n, s['bda'][i]),
              xline(n, f, s['drop'] if i == 7 else (), s['order'])]
        n += 1
    for _ in range(s['extra_draw']):
        L.append('FrameTrace-draw: n=%d logs=1 bda_scan=100' % n)
        n += 1
    L += s['tail']
    return L


def write(d, s):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(lines_of(s)) + '\n').encode('ascii'))
    with open(os.path.join(d, 'es.json'), 'w') as f:
        json.dump(s['run'], f)
    for k, v in s['side'].items():
        with open(os.path.join(d, k + '.txt'), 'w') as f:
            f.write(v + '\n')
    with open(os.path.join(d, 'seal.md'), 'wb') as f:
        f.write(SEAL)
    with open(os.path.join(d, 'stdout.txt'), 'w') as f:
        f.write(s['stdout'])
    with open(os.path.join(d, 'bin.txt'), 'w') as f:
        f.write(s.get('binpath', TBIN) + '\n')
    shutil.copyfile(KREF, os.path.join(d, 'kref.tsv'))


shutil.rmtree(str(BASE), ignore_errors=True)
os.makedirs(str(BASE), exist_ok=True)
TMP = str(BASE)
CNT = [0]


def tag_of(s):
    return 'f30_%s_%s' % (s['scene'], s['kind'])


def read(s, tag=None):
    CNT[0] += 1
    d = os.path.join(TMP, 'c%d' % CNT[0])
    write(d, s)
    t = tag or tag_of(s)
    r = R.read_tag(t, R.paths(t, d))
    shutil.rmtree(d, ignore_errors=True)
    return r


def row(r, start):
    for a, b in r['admission'] + (r['members'] or []):
        if a.startswith(start):
            return b
    return None


def ref(r, start):
    for a, b in r.get('reference_rows') or []:
        if a.startswith(start):
            return b
    return None


def mod(s, fn):
    t = copy.deepcopy(s)
    fn(t)
    return t


def stopped(r, text):
    return any(text in z for z in r['stop'])


def fr(t, i, **kw):
    t['frames'][i].update(kw)


# --- clean tags ---
CLEAN = {}
for kind, scene in (('w6', 's1'), ('c6', 's1'), ('c6', 's9'), ('c6', 's6')):
    s = spec(kind, scene)
    r = read(s)
    CLEAN[(kind, scene)] = (s, r)
    ok &= check('%s %s clean ADMITTED %s' % (kind, scene, [a for a, x in r['admission'] if not x][:3]), r['status'] == 'ADMITTED')
    ok &= check('%s %s clean no STOP %s' % (kind, scene, r['stop']), r['stop'] == [])
    ok &= check('%s %s clean K_S YES' % (kind, scene), r['ks'] is True)
    ok &= check('%s %s inj at T %s' % (kind, scene, r['inj']['at_t']), r['inj']['at_t'] == dict(rts_inj=NINJ, rts_inj_s=NINJ, rts_inj_race=0,
                                                                                                    rts_inj_nos=0, rts_inj_none=0))
c6, r6 = CLEAN[('c6', 's1')]
w6, rw = CLEAN[('w6', 's1')]
ok &= check('w6 members 7 all YES %s' % rw['members'], len(rw['members']) == 7 and all(b for a, b in rw['members']))
ok &= check('c6 members none (rows only)', r6['members'] == [])
ok &= check('c6 reference rows none; w6 reference rows (D2)-(D6) 5', r6['reference_rows'] == [] and len(rw['reference_rows']) == 5)
ok &= check('w6 executor variant (D2)-(D6) ok', rw['w6_variant_d2_d6'] is True)
ok &= check('natural S 0 at T and process', r6['inj']['natural_s_at_t'] == 0 and r6['inj']['natural_s_proc'] == 0)
ok &= check('MISMATCH mode=6 bit 0x040 lines 40', r6['mm6_s_lines'] == 40 and r6['verify_lines'] == 40)
ok &= check('clean c6 reconciliation lines exhausted ok %s' % r6['rec'], r6['rec']['exact'] is False and r6['rec']['ok'] is True)
for t in ('f30_s1_w6', 'f30_s1_c6', 'f30_s9_c6_r2', 'f30_s1_w6_r1'):
    ok &= check('tag form %s' % t, R.TAG_RX.match(t) is not None)
for t in ('f30_s2_w6', 'f30_s0_c6', 'f30_s1_c5', 'f30_cy_c6', 'f30_cy_v', 'f30_s1_c6_r4', 'f30_s1_w6_r0', 'f30_s1_c4', 'b12_w'):
    ok &= check('tag form refused %s' % t, R.TAG_RX.match(t) is None)
ok &= check('parts', R.parts('f30_s9_c6_r2') == ('s9', 'c6', '_r2') and R.parts('f30_s1_w6') == ('s1', 'w6', ''))

# --- harness admission ---
for key, val in (('installed_before', TB), ('installed_after', TB), ('installed_sha', FS11), ('installed_sha', T2), ('level', 'pot')):
    ok &= check('admission side %s=%s' % (key, val[:8]), read(mod(c6, lambda t: t['side'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
for key, val in (('binary_sha256', T2), ('guest_args', '-lvl pot'), ('hold_s', 151), ('gates', 'rtskip=6'), ('schedule', 'x')):
    ok &= check('admission run %s' % key, read(mod(c6, lambda t: t['run'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
ok &= check('admission prereg', read(mod(c6, lambda t: t['run']['prereg'].__setitem__('sha256', 'x')))['status'] == 'NOT_ADMITTED')
for k, v in (('KYTY_RT_SKIP', '5'), ('KYTY_RT_SKIP', '2'), ('KYTY_FIX_B42', '0'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'),
             ('KYTY_REC', 'x'), ('KYTY_KEYS', KEYS), ('VK_LAYER_PATH', 'C:/VulkanSDK/1.4.357.0/Bin')):
    ok &= check('admission c6 env %s=%s' % (k, v[:8]), read(mod(c6, lambda t: t['run']['env'].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
for k, v in (('VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000'), ('VK_LAYER_MESSAGE_ID_FILTER', 'x'), ('KYTY_RT_SKIP', '2')):
    ok &= check('admission w6 env %s=%s' % (k, v[:8]), read(mod(w6, lambda t: t['run']['env'].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
for k0 in ('VK_LAYER_PATH', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT', 'KYTY_RT_SKIP'):
    ok &= check('admission w6 env missing %s' % k0, read(mod(w6, lambda t: t['run']['env'].pop(k0)))['status'] == 'NOT_ADMITTED')
ok &= check('admission c6 env missing KYTY_FRAME_TRACE', read(mod(c6, lambda t: t['run']['env'].pop('KYTY_FRAME_TRACE')))['status'] == 'NOT_ADMITTED')
ok &= check('admission s9 without KYTY_KEYS', read(mod(CLEAN[('c6', 's9')][0], lambda t: t['run']['env'].pop('KYTY_KEYS')))['status'] == 'NOT_ADMITTED')
ok &= check('admission c6 with --vulkan-validation true last',
            read(mod(c6, lambda t: t['run']['cmdline'].extend(['--vulkan-validation', 'true'])))['status'] == 'NOT_ADMITTED')
ok &= check('admission w6 with --vulkan-validation false last',
            read(mod(w6, lambda t: t['run']['cmdline'].extend(['--vulkan-validation', 'false'])))['status'] == 'NOT_ADMITTED')
for extra in (['--shader-validation', 'true'], ['--rd'], ['--graphics-debug-dump', 'true']):
    ok &= check('admission cmdline %s' % extra, read(mod(c6, lambda t: t['run']['cmdline'].extend(extra)))['status'] == 'NOT_ADMITTED')
for k, v in (('outcome', 'timeout'), ('hold_exit', 3), ('started_s', None)):
    ok &= check('admission attempt %s=%s' % (k, v), read(mod(c6, lambda t: t['run']['attempts'][0].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
ok &= check('window 149.9 - NO', read(mod(c6, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=149.9)))['status'] == 'NOT_ADMITTED')
ok &= check('window 150.0 - YES', read(mod(c6, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=150.0)))['status'] == 'ADMITTED')
ok &= check('admission no entry line', read(mod(c6, lambda t: t.__setitem__('entry', False)))['status'] == 'NOT_ADMITTED')
for ln in ('Window 1 minimized', 'Recovering Vulkan swapchain 1'):
    ok &= check('window event %s - INTERFERENCE' % ln, read(mod(c6, lambda t: t['mid'].append(ln)))['status'] == 'INTERFERENCE')
ok &= check('no summary line - INTERFERENCE', read(mod(c6, lambda t: t.__setitem__('tail', [])))['status'] == 'INTERFERENCE')
ok &= check('two summary lines - NOT_ADMITTED', read(mod(c6, lambda t: t.__setitem__('tail', t['tail'] * 2)))['status'] == 'NOT_ADMITTED')
for ln in ('GamePatch: x', 'DiagB32 x', 'TestLogStall: x'):
    ok &= check('admission line %s' % ln, read(mod(c6, lambda t: t['mid'].append(ln)))['status'] == 'NOT_ADMITTED')
ok &= check('admission signature', read(mod(c6, lambda t: t['head'].__setitem__(2, 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40))))['status'] == 'NOT_ADMITTED')
ok &= check('admission catalog', read(mod(c6, lambda t: t['head'].__setitem__(3, 'Shader translation cache: C:/e/variant_fixb26_fixb1b_fixf10')))['status'] == 'NOT_ADMITTED')

# --- (D1) the text of the print place, (D5), (D7) = RC5 ---
r = read(mod(c6, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 6 ctx_slots=8 groups=11')))
ok &= check('(D1) mode line without rec_bytes - NO', row(r, '(D1)') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 5 ctx_slots=8 groups=11 rec_bytes=7192')))
ok &= check('(D1) mode 5 - NO', row(r, '(D1)') is False)
r = read(mod(c6, lambda t: t['head'].append('RtSkip: mode 6 ctx_slots=8 groups=11 rec_bytes=7192')))
ok &= check('(D1) two mode lines - NO', row(r, '(D1)') is False)
r = read(mod(w6, lambda t: t['head'].pop(4)))
ok &= check('(D1) at w6 is a member - no line NO', row(r, '(D1)') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: t['head'].append('[T1] RtSkip: mode 6 ctx_slots=8 groups=11 rec_bytes=7192 extra')))
ok &= check('(D1) mode line with other text - NO', row(r, '(D1)') is False)
ok &= check('(D5) 1499 lines - NO', read(mod(c6, lambda t: t.__setitem__('frames', t['frames'][:1499]) or t.__setitem__('bda', t['bda'][:1499])))['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: (t.__setitem__('frames', t['frames'][:1500]), t.__setitem__('bda', t['bda'][:1500]))))
ok &= check('(D5) 1500 lines - ok', row(r, '(D5)') is True)
def short_w(t):
    t['frames'] = t['frames'][:1000]
    t['bda'] = t['bda'][:1000]
    for i in range(200 + 97, 200 + NINJ):   # floor(1000 x 400 / 4096) = 97 perturbations
        fr(t, i, rts_inj=0, rts_inj_s=0, rts_bad=0, rts_bad_noreg=0, rts_bad_b=0, rts_bad_s=0)


r = read(mod(w6, short_w))
ok &= check('(D5) at w6 is a reference row (1000 lines: status ADMITTED, row NO, variant NO) %s' % r['why'],
            ref(r, '(D5)') is False and r['w6_variant_d2_d6'] is False and r['status'] == 'ADMITTED' and row(r, '(D5)') is None)
ok &= check('(D5) at c6 extra draw lines 5 percent - NO', read(mod(c6, lambda t: t.__setitem__('extra_draw', 90)))['status'] == 'NOT_ADMITTED')
for nm, fn in (('launch sha T2', lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', T2)),
               ('json sha other', lambda t: t['run'].__setitem__('binary_sha256', T2)),
               ('fork line 6fbdcf6', lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 6fbdcf6')),
               ('fork line twice', lambda t: t['head'].append('  version: Fork build arigandores/KytyPS5 ea38426')),
               ('log version -1907', lambda t: t['mid'].append('x KytyPS5-2026-09-15-6a2987a-1907-g6fbdcf67 y')),
               ('pinned copy FS11', lambda t: t.__setitem__('binpath', FS11BIN)),
               ('pinned copy T2', lambda t: t.__setitem__('binpath', T2BIN))):
    r = read(mod(c6, fn))
    ok &= check('(D7) RC5 %s - NO' % nm, row(r, '(D7)') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, '(D7)'))
r = read(mod(c6, lambda t: t['mid'].append('x KytyPS5-2026-09-15-6a2987a-1908-gea38426b y')))
ok &= check('(D7) log version -1908-gea38426b - ok', row(r, '(D7)') is True and r['status'] == 'ADMITTED')
r = read(mod(w6, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', T2)))
ok &= check('(D7) at w6 is a member', row(r, '(D7)') is False and r['status'] == 'NOT_ADMITTED')

# --- fields: the 5 names, whole tokens ---
for k in I5:
    r = read(mod(c6, lambda t: t.__setitem__('drop', {k})))
    ok &= check('missing field %s - NOT_ADMITTED' % k, r['status'] == 'NOT_ADMITTED' and row(r, 'RC4 (F30f)') is False)
r = read(mod(c6, lambda t: t.__setitem__('order', ['rts_inj_none', 'rts_inj_nos', 'rts_inj_race', 'rts_inj_s', 'rts_inj'])))
ok &= check('name order reversed - same reading', r['status'] == 'ADMITTED' and r['inj']['at_t'] == r6['inj']['at_t'])
# rts_inj only as the prefix of the other four (dropped on every line): never read as rts_inj
r = read(mod(c6, lambda t: [f.pop('rts_inj') for f in t['frames'] + t['pre']]))
ok &= check('rts_inj absent on every line, the other four present - missing field, not their value',
            r['status'] == 'NOT_ADMITTED' and r['inj']['proc']['rts_inj'] == 0)

# --- RC1 (F30p) ---
r = read(mod(c6, lambda t: fr(t, 200, rts_inj_s=0, rts_inj_nos=1)))
ok &= check('RC1 nos 1 at T - NO and STOP', row(r, 'RC1 (F30p') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'RC1 (F30p)')
            and r['ks'] is False)
r = read(mod(w6, lambda t: fr(t, 200, rts_inj_s=0, rts_inj_nos=1)))
ok &= check('RC1 at w6 - NO and STOP', row(r, 'RC1 (F30p') is False and stopped(r, 'RC1 (F30p)'))
# a tail after T: the last line breaks chk = pa by 1 and carries nos 1 - at T nos 0
r = read(mod(c6, lambda t: fr(t, NFR - 1, rts_chk=421, rts_inj_nos=1, rts_inj_none=0)))
ok &= check('RC1 read at T: nos only on the tail after T - ok (process nos 1 is a row) %s' % r['why'],
            row(r, 'RC1 (F30p') is True and r['inj']['proc']['rts_inj_nos'] == 1 and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: (fr(t, NFR - 1, rts_chk=421), fr(t, NFR - 2, rts_inj_nos=1))))
ok &= check('RC1: nos at the line before the tail - inside T - NO', row(r, 'RC1 (F30p') is False)

# --- RC2 (F30p) ---
r = read(mod(c6, lambda t: fr(t, 200, rts_inj_s=0)))
ok &= check('RC2 difference -1 - ok', row(r, 'RC2 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: (fr(t, 200, rts_inj_s=0), fr(t, 201, rts_inj_s=0))))
ok &= check('RC2 difference -2 - NO and STOP', row(r, 'RC2 (F30p') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'RC2 (F30p'))
r = read(mod(c6, lambda t: fr(t, 100, rts_inj_s=1, rts_bad=1, rts_bad_noreg=1, rts_bad_b=1, rts_bad_s=1)))
ok &= check('RC2 difference +1 - ok', row(r, 'RC2 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: fr(t, 100, rts_inj_s=2, rts_bad=2, rts_bad_noreg=2, rts_bad_b=2, rts_bad_s=2)))
ok &= check('RC2 difference +2 - NO', row(r, 'RC2 (F30p') is False and r['status'] == 'NOT_ADMITTED')

# --- RC3 (F30p) ---
r = read(mod(c6, lambda t: fr(t, 200, rts_bad_s=0, rts_bad_p=1)))
ok &= check('RC3 bad_s = inj_s - 1 - ok', row(r, 'RC3 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: (fr(t, 200, rts_bad_s=0, rts_bad_p=1), fr(t, 201, rts_bad_s=0, rts_bad_p=1))))
ok &= check('RC3 bad_s = inj_s - 2 - NO', row(r, 'RC3 (F30p') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: fr(t, 200, rts_inj_s=0, rts_inj_race=1)))
ok &= check('RC3 race 0 = inj_race 1 - 1 - ok', row(r, 'RC3 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: (fr(t, 200, rts_inj_s=0, rts_inj_race=1), fr(t, 201, rts_inj_s=0, rts_inj_race=1))))
ok &= check('RC3 race 0 = inj_race 2 - 2 - NO', row(r, 'RC3 (F30p') is False)
r = read(mod(c6, lambda t: (fr(t, 200, rts_inj_s=0, rts_inj_race=1, rts_race=1), fr(t, 201, rts_inj_s=0, rts_inj_race=1))))
ok &= check('RC3 race 1 = inj_race 2 - 1 - ok', row(r, 'RC3 (F30p') is True)

# --- RC4 (F30p) ---
r = read(mod(c6, lambda t: fr(t, 200, rts_inj=0, rts_inj_s=0)))
ok &= check('RC4 inj+none = q - 1 - ok', row(r, 'RC4 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: (fr(t, 200, rts_inj=0, rts_inj_s=0), fr(t, 201, rts_inj=0, rts_inj_s=0))))
ok &= check('RC4 inj+none = q - 2 - NO and STOP', row(r, 'RC4 (F30p') is False and stopped(r, 'RC4 (F30p'))
r = read(mod(c6, lambda t: fr(t, 100, rts_inj_none=1)))
ok &= check('RC4 inj+none = q + 1 - ok', row(r, 'RC4 (F30p') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: fr(t, 100, rts_inj_none=2)))
ok &= check('RC4 inj+none = q + 2 - NO', row(r, 'RC4 (F30p') is False and r['status'] == 'NOT_ADMITTED')

# --- (inj) at c6 ---
def no_inj(t, none):
    for i in INJ_FRAMES:
        fr(t, i, rts_inj=0, rts_inj_s=0, rts_inj_none=1 if (none and i == INJ_FRAMES[0]) else 0)
    if none:
        fr(t, INJ_FRAMES[0], rts_inj_none=NINJ)


r = read(mod(c6, lambda t: no_inj(t, True)))
ok &= check('(inj) inj 0, none 156 - ADMITTED, member YES, K_S NO %s' % r['why'], r['status'] == 'ADMITTED' and row(r, '(inj)') is True
            and r['ks'] is False and r['stop'] == [])
r = read(mod(c6, lambda t: no_inj(t, False)))
ok &= check('(inj) inj 0, none 0, pb >= 4096 - NO, STOP code defect and RC4', row(r, '(inj)') is False and stopped(r, 'code defect')
            and row(r, 'RC4 (F30p') is False)


def small_pb(t):
    for f in t['frames']:
        f.update(rts_pb=1, rts_chk_b=1)
    no_inj(t, False)


r = read(mod(c6, small_pb))
ok &= check('(inj) inj 0, none 0, pb 1600 < 4096 - RC4 ok, (inj) NO, STOP', row(r, 'RC4 (F30p') is True and row(r, '(inj)') is False
            and stopped(r, 'code defect') and r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: (no_inj(t, False), fr(t, 200, rts_inj=1, rts_inj_s=1), fr(t, 100, rts_inj_none=NINJ - 1))))
ok &= check('(inj) inj 1 - YES', row(r, '(inj)') is True and r['ks'] is True)

# --- w6 members ---
for nm, fn, start in (('[Vulkan][E]', lambda t: t['mid'].append('[Vulkan][E] Validation Error: x'), '0 [Vulkan][E]'),
                      ('no [Vulkan][W]', lambda t: t['mid'].remove('[Vulkan][W] Validation Warning: x'), 'positive control'),
                      ('no DualSrcBlend', lambda t: t['head'].pop(), 'DualSrcBlend'),
                      ('DualSrcBlend 1 0', lambda t: t['head'].__setitem__(-1, 'DualSrcBlend: supported=1 enabled=0'), 'DualSrcBlend'),
                      ('DualSrcBlend after GuestOut', lambda t: (t['head'].pop(), t['mid'].append('DualSrcBlend: supported=1 enabled=1')), 'DualSrcBlend'),
                      ('limit line', lambda t: t['mid'].append('[Vulkan][W] x this will be the last time reporting it'), '0 limit'),
                      ('death marker', lambda t: t['mid'].append('--- Fatal Error ---'), '0 death'),
                      ('stdout death', lambda t: t.__setitem__('stdout', 'Unhandled exception: x'), '0 death'),
                      ('sum rts_inj 0', lambda t: no_inj(t, True), 'sum at T rts_inj'),
                      ('not lived', lambda t: t['run']['attempts'][0].__setitem__('outcome', 'timeout'), 'lived')):
    r = read(mod(w6, fn))
    ok &= check('w6 member %s - NO' % nm, row(r, start) is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(w6, lambda t: t['mid'].append('[Vulkan][E] Validation Error: x')))
ok &= check('w6 [Vulkan][E] - STOP', stopped(r, 'w6: [Vulkan][E]'))
ok &= check('c6 [Vulkan][E] line - no w6 member, no STOP', read(mod(c6, lambda t: t['mid'].append('[Vulkan][E] x')))['stop'] == [])

# --- inherited parse members ---
r = read(mod(c6, lambda t: [fr(t, NFR - k, rts_chk=421) for k in (1, 2, 3)]))
ok &= check('closing point T at distance 3 - ok', row(r, 'parse') is True and r['status'] == 'ADMITTED')
r = read(mod(c6, lambda t: [fr(t, NFR - k, rts_chk=421) for k in (1, 2, 3, 4)]))
ok &= check('closing point T at distance 4 - NO and STOP', row(r, 'parse') is False and stopped(r, 'parse identity'))
ok &= check('RC1 (F30l) rts_skip 1 - NO', row(read(mod(c6, lambda t: fr(t, 5, rts_skip=1))), 'RC1 (F30l)') is False)
ok &= check('RC2 (F30l) bad_b > bad - NO', row(read(mod(c6, lambda t: fr(t, 5, rts_bad_b=1, rts_bad_p=1))), 'RC2 (F30l)') is False)
ok &= check('RC4 (F30l) noreg != bad - NO', row(read(mod(c6, lambda t: fr(t, 200, rts_bad_noreg=0))), 'RC4 (F30l)') is False)
r = read(mod(c6, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x080 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=6')))
ok &= check('reconciliation: a 0x080 line with rts_bad_p 0 - NO (and 41 lines > 40 - parse NO)', row(r, 'reconciliation') is False)
r = read(mod(c6, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x040 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=5')))
ok &= check('MISMATCH mode=5 line not counted for mode 6 reconciliation', r['rec']['n'] == 40)

# --- inherited members on the base c6x (port of the F30m blocks; the reports of frame 100 exact, no perturbation found: none 156) ---
SEVEN = (('0x010', dict(rts_bad_r=1)), ('0x020', dict(rts_bad_xr=1)), ('0x020', dict(rts_bad_xc=1)), ('0x020', dict(rts_bad_xe=1)),
         ('0x040', dict(rts_bad_s=1)), ('0x080', dict(rts_bad_p=1)), ('0x100', dict(rts_bad_m=1)))


def put_reports(t, reps, mode=6):
    """reps: [(bits text, {counter: 1})] - one MISMATCH line and the counters of RtsReport per report, all in frame 100."""
    t['mid'] = [z for z in t['mid'] if not z.startswith('RtSkipVerify')]
    f = t['frames'][100]
    for k in ('rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx') + B8:
        f[k] = 0
    for bits, cnt in reps:
        b = int(bits, 16)
        t['mid'].append('RtSkipVerify: MISMATCH frame=900 bits=%s reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=%d' % (bits, mode))
        f['rts_bad'] += 1
        f['rts_bad_noreg'] += 1
        if b & 0x3f0:
            f['rts_bad_b'] += 1
        if b & 0x030:
            f['rts_bad_rx'] += 1
        for k, v in cnt.items():
            f[k] += v


def to_c6x(t):
    no_inj(t, True)
    for i in INJ_FRAMES:
        fr(t, i, rts_bad=0, rts_bad_noreg=0, rts_bad_b=0, rts_bad_s=0)
    put_reports(t, SEVEN)


c6x = mod(c6, to_c6x)
rx = read(c6x)
ok &= check('c6x base ADMITTED, K_S NO, exact reconciliation of 7 %s %s' % (rx['why'], rx.get('rec')), rx['status'] == 'ADMITTED' and rx['ks'] is False
            and rx['rec']['exact'] is True and rx['rec']['ok'] is True and rx['rec']['n'] == 7 and rx['stop'] == [])
ok &= check('c6x reconciliation lines', rx['rec']['lines'] == dict(rx=4, b=7, x=3, rts_bad_r=1, rts_bad_s=1, rts_bad_p=1, rts_bad_m=1, rts_bad_l=0))
ok &= check('c6x b - rx = 3', rx['b_minus_rx'] == 3)
ok &= check('log absent - NOT_ADMITTED', R.read_tag('f30_s1_c6', dict(R.paths('f30_s1_c6', os.path.join(TMP, 'none')), log='C:/no/such/log.txt'))['status'] == 'NOT_ADMITTED')

# (D1)-(D7)
ok &= check('(D1) mode 2 at c6', row(read(mod(c6x, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 2 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) no mode line', row(read(mod(c6x, lambda t: t['head'].pop(4))), '(D1)') is False)
ok &= check('(D1) mode 6 once plus a mode 2 line - NO', row(read(mod(c6x, lambda t: t['head'].append('RtSkip: mode 2 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
r = read(mod(c6x, lambda t: t['mid'].append('RtSkip: refused reason=rk3cen')))
ok &= check('(D2) refused line - NO and STOP', row(r, '(D2)') is False and stopped(r, 'refused'))
ok &= check('(D2) rts_refuse 1 - NO', row(read(mod(c6x, lambda t: fr(t, 5, rts_refuse=1))), '(D2)') is False)
ok &= check('(D3) gate rtskip=6 fine', row(read(mod(c6x, lambda t: t['mid'].append('Gate: rtskip=6 frame=5'))), '(D3)') is True)
ok &= check('(D3) gate rtskip=1', row(read(mod(c6x, lambda t: t['mid'].append('Gate: rtskip=1 frame=5'))), '(D3)') is False)
for k in ('rts_xthr', 'rts_acqw'):
    r = read(mod(c6x, lambda t: t['pre'].__setitem__(0, dict(t['pre'][0], **{k: 1}))))
    ok &= check('(D4) %s before the entry - NO and STOP' % k, row(r, '(D4)') is False and stopped(r, '(D4)'))
ok &= check('(D5) c6 1500 x lines YES', row(read(mod(c6x, lambda t: t.__setitem__('frames', t['frames'][:1500]))), '(D5)') is True)
ok &= check('(D5) c6 1499 x lines NO', row(read(mod(c6x, lambda t: t.__setitem__('frames', t['frames'][:1499]))), '(D5)') is False)
ok &= check('(D5) share: 1600 x, 1685 draw NO', row(read(mod(c6x, lambda t: t.__setitem__('extra_draw', 85))), '(D5)') is False)
ok &= check('(D5) share: 1600 x, 1684 draw YES', row(read(mod(c6x, lambda t: t.__setitem__('extra_draw', 84))), '(D5)') is True)
ok &= check('(D6) rts_ovf in the window', row(read(mod(c6x, lambda t: fr(t, 5, rts_ovf=1))), '(D6)') is False)
ok &= check('(D6) rts_ovf before the entry - YES', row(read(mod(c6x, lambda t: t['pre'].__setitem__(0, dict(t['pre'][0], rts_ovf=1)))), '(D6)') is True)
ok &= check('(D7) no launch_sha256', row(read(mod(c6x, lambda t: t['run']['attempts'][0].pop('launch_sha256'))), '(D7)') is False)
ok &= check('(D7) fork line ea38426-dirty', row(read(mod(c6x, lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 ea38426-dirty'))), '(D7)') is False)
ok &= check('(D7) no fork line', row(read(mod(c6x, lambda t: t['head'].pop(1))), '(D7)') is False)
ok &= check('(D7) binary_sha256 != launch_sha256', row(read(mod(c6x, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', 'f' * 64))), '(D7)') is False)
ok &= check('(D7) a version string of FS11 in the log - NO', row(read(mod(c6x, lambda t: t['mid'].append('KytyPS5-2026-09-15-6a2987a-1910-gee9632be'))), '(D7)') is False)
r = read(mod(c6x, lambda t: (t['mid'].append('Window 1 minimized'), t['run']['attempts'][0].__setitem__('launch_sha256', FS11))))
ok &= check('(D7) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: (t['mid'].append('Window 1 minimized'), fr(t, 200, rts_inj_s=0, rts_inj_nos=1))))
ok &= check('RC1 (F30p) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
r = read(mod(c6, lambda t: (t['mid'].append('Window 1 minimized'), no_inj(t, False))))
ok &= check('(inj) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')

# fields
for k in B8 + ('rts_bad_rx', 'rts_bad_b', 'rts_chk_b', 'rts_xb_pass'):
    r = read(mod(c6x, lambda t: t.__setitem__('drop', {k})))
    ok &= check('missing %s in one window line - NOT_ADMITTED and not 0' % k, r['status'] == 'NOT_ADMITTED' and row(r, 'RC4 (F30f)') is False)
r = read(mod(c6x, lambda t: t['pre'].__setitem__(0, dict((a, b) for a, b in t['pre'][0].items() if a != 'rts_bad_l'))))
ok &= check('missing rts_bad_l before the entry - NOT_ADMITTED', row(r, 'RC4 (F30f)') is False)
ok &= check('a field outside REQ may be absent', read(mod(c6x, lambda t: t.__setitem__('drop', {'rts_early'})))['status'] == 'ADMITTED')
CNT[0] += 1
dd = os.path.join(TMP, 'tok')
write(dd, c6x)
lp = os.path.join(dd, 'log.txt')
data = open(lp, 'rb').read().replace(b' rts_bad_r=0 ', b' rts_bad_rq=0 ', 1)
open(lp, 'wb').write(data)
r = R.read_tag('f30_s1_c6', R.paths('f30_s1_c6', dd))
ok &= check('name taken whole: rts_bad_rq is not rts_bad_r - missing field', row(r, 'RC4 (F30f)') is False)
x = R.scan(lp, LEVEL['s1'])
ok &= check('name taken whole: rts_bad_rx sum not mixed into rts_bad_r (rx 4, r 1)', x['proc']['rts_bad_rx'] == 4 and x['proc']['rts_bad_r'] == 1)
data = open(lp, 'rb').read().replace(b' rts_inj=0 ', b' rts_injq=0 ', 1)
open(lp, 'wb').write(data)
x = R.scan(lp, LEVEL['s1'])
ok &= check('name taken whole: rts_injq is not rts_inj - the line misses rts_inj %s' % x['x_missing_names'], x['x_missing'] == 1
            and 'rts_inj' in x['x_missing_names'][0][1] and 'rts_bad_r' in x['x_missing_names'][0][1])
shutil.rmtree(dd, ignore_errors=True)

# parse of item 651 (b)
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk=421), fr(t, 11, rts_chk=419))))
ok &= check('parse: tear of one event - YES', row(r, 'parse') is True)
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk=422), fr(t, 11, rts_chk=418))))
ok &= check('parse: chk/pa prefix 2 - YES, dev2 1', row(r, 'parse') is True and r['ref']['prefix_dev2']['chk_pa'] == 1 and r['ref']['prefix_maxdev']['chk_pa'] == 2)
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk=424), fr(t, 11, rts_chk=416))))
ok &= check('parse: chk/pa prefix 4 - YES', row(r, 'parse') is True and r['status'] == 'ADMITTED')
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk=425), fr(t, 11, rts_chk=415))))
ok &= check('parse: chk/pa prefix 5 - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk_b=402), fr(t, 11, rts_chk_b=398))))
ok &= check('parse: chk_b/pb prefix 2 - YES, dev2 1', row(r, 'parse') is True and r['ref']['prefix_dev2']['chkb_pb'] == 1)
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk_b=404), fr(t, 11, rts_chk_b=396))))
ok &= check('parse: chk_b/pb prefix 4 - YES', row(r, 'parse') is True and r['status'] == 'ADMITTED')
r = read(mod(c6x, lambda t: (fr(t, 10, rts_chk_b=405), fr(t, 11, rts_chk_b=395))))
ok &= check('parse: chk_b/pb prefix 5 - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: (fr(t, 99, rts_bad_b=4), fr(t, 100, rts_bad_b=3))))
ok &= check('parse: b/bad prefix 4 - YES', row(r, 'parse') is True)
r = read(mod(c6x, lambda t: (fr(t, 99, rts_bad_b=5), fr(t, 100, rts_bad_b=2))))
ok &= check('parse: b/bad prefix 5 - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: (put_reports(t, [('0x020', dict(rts_bad_xr=1))] * 8), fr(t, 100, rts_bad_b=4), fr(t, 101, rts_bad_b=4))))
ok &= check('parse: rx/b prefix 4 - YES', row(r, 'parse') is True)
r = read(mod(c6x, lambda t: (put_reports(t, [('0x020', dict(rts_bad_xr=1))] * 8), fr(t, 100, rts_bad_b=3), fr(t, 101, rts_bad_b=5))))
ok &= check('parse: rx/b prefix 5 - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: fr(t, 10, rts_pb=401)))
ok &= check('parse: pb sum != chk_b sum - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad_rx=8)))
ok &= check('parse: rx 8 > b 7 - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
ok &= check('parse: unparsable RtSkipVerify - NO', row(read(mod(c6x, lambda t: t['mid'].append('RtSkipVerify: something else'))), 'parse') is False)
r = read(mod(c6x, lambda t: fr(t, 10, rts_chk=421)))
ok &= check('parse: chk sum 1 over pa sum - NO and STOP', row(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: (put_reports(t, [('0x040', dict(rts_bad_s=1))]), t['mid'].append(t['mid'][-1]))))
ok &= check('parse: 2 lines > bad 1 - NO', row(r, 'parse') is False)
r = read(mod(c6x, lambda t: (fr(t, 100, rts_bad_b=1), fr(t, 101, rts_bad_b=6))))
ok &= check('parse: rx 4 three events ahead of b 1 at a line, sums equal - YES', row(r, 'parse') is True)
r = read(mod(c6x, lambda t: fr(t, 5, rts_chk_b=421, rts_pb=421, rts_chk=420)))
ok &= check('parse: chk 420 < chk_b 421 on a line, process chk >= chk_b - parse YES (per line reference)', row(r, 'parse') is True)
r = read(mod(c6x, lambda t: [fr(t, i, rts_n=10) for i in range(NFR)]))
ok &= check('parse: chk > n (process) - NO', row(r, 'parse') is False)
r = read(mod(c6x, lambda t: t['frames'][100].update(rts_bad_noreg=8)))
ok &= check('parse: noreg 8 > bad 7 - NO', row(r, 'parse') is False)

# RC1 of F30l
for kd, s in (('c6x', c6x), ('w6', w6)):
    r = read(mod(s, lambda t: fr(t, 3, rts_skip=1)))
    ok &= check('RC1 (F30l) %s rts_skip 1 - NOT_ADMITTED and STOP' % kd, row(r, 'RC1 (F30l)') is False and r['status'] == 'NOT_ADMITTED'
                and stopped(r, 'RC1 (F30l)'))
r = read(mod(c6x, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames']]))
ok &= check('RC1 (F30l) rts_chk_b = rts_pb = 0 - NO', row(r, 'RC1 (F30l)') is False)
r = read(mod(c6x, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames'][1:]]))
ok &= check('RC1 (F30l) rts_chk_b = rts_pb = 400 >= 1 - YES', row(r, 'RC1 (F30l)') is True)
r = read(mod(c6x, lambda t: [f.update(rts_chk=300, rts_pa=300) for f in t['frames']]))
ok &= check('RC1 (F30l) rts_chk 300 < rts_chk_b 400 - NO', row(r, 'RC1 (F30l)') is False)

# item 662 (g): the closing point T
ok &= check('clean c6x: T is the last line, distance 0, tail deviations 0', rx['ref'].get('close_dist') == 0
            and rx['ref'].get('close_idx') == rx['ref'].get('x_full') and rx['ref'].get('tail_dev') == dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0))
for k in (1, 2, 3):
    r = read(mod(c6x, lambda t: t['frames'][-k].update(rts_chk_b=401)))
    ok &= check('item 662: chk_b event open on the last %d lines - ADMITTED, distance %d' % (k, k), row(r, 'parse') is True
                and row(r, 'RC1 (F30l)') is True and r['status'] == 'ADMITTED' and r['ref'].get('close_dist') == k
                and r['ref'].get('tail_dev', {}).get('chkb_pb') == 1 and r['stop'] == [])
r = read(mod(c6x, lambda t: t['frames'][-4].update(rts_chk_b=401)))
ok &= check('item 662: chk_b event open on the last 4 lines - NO and STOP', row(r, 'parse') is False and row(r, 'RC1 (F30l)') is False
            and r['status'] == 'NOT_ADMITTED' and stopped(r, 'item 651') and r['ref'].get('close_dist') == 4)
r = read(mod(c6x, lambda t: t['frames'][-3].update(rts_pb=401)))
ok &= check('item 662: pb ahead on the last 3 lines - ADMITTED', r['status'] == 'ADMITTED' and r['ref'].get('close_dist') == 3)
r = read(mod(c6x, lambda t: t['frames'][-4].update(rts_pb=401)))
ok &= check('item 662: pb ahead on the last 4 lines - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED' and row(r, 'parse') is False)
r = read(mod(c6x, lambda t: t['frames'][-3].update(rts_chk=421)))
ok &= check('item 662: chk/pa event open on the last 3 lines - ADMITTED', r['status'] == 'ADMITTED' and r['ref'].get('tail_dev', {}).get('chk_pa') == 1)
r = read(mod(c6x, lambda t: t['frames'][800].update(rts_chk_b=401)))
ok &= check('item 662: loss of one event in the middle - NO and STOP', row(r, 'parse') is False and row(r, 'RC1 (F30l)') is False
            and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: t['frames'][-2].update(rts_chk_b=404)))
ok &= check('item 662: tail deviation 4 on the last 2 lines - ADMITTED', r['status'] == 'ADMITTED' and r['ref'].get('tail_dev', {}).get('chkb_pb') == 4)
r = read(mod(c6x, lambda t: t['frames'][-2].update(rts_chk_b=405)))
ok &= check('item 662: tail deviation 5 on the last 2 lines - NO and STOP', r['status'] == 'NOT_ADMITTED' and row(r, 'parse') is False
            and stopped(r, 'item 651'))
r = read(mod(c6x, lambda t: t['frames'][-1].update(rts_skip=1, rts_chk_b=401)))
ok &= check('item 662 (b): rts_skip 1 on the tail after T - RC1 NO by the process sum', row(r, 'RC1 (F30l)') is False and r['ref'].get('close_dist') == 1)
r = read(mod(c6x, lambda t: (t['frames'][-1].update(rts_chk_b=401), t['frames'][-2].update(rts_skip=1))))
ok &= check('item 662: rts_skip 1 at T - RC1 NO', row(r, 'RC1 (F30l)') is False)
r = read(mod(c6x, lambda t: ([f.update(rts_chk=300, rts_pa=300) for f in t['frames']], t['frames'][-1].update(rts_chk=10 ** 7, rts_pa=10 ** 7,
                                                                                                            rts_chk_b=401))))
ok &= check('item 662: chk < chk_b at T, process chk >= chk_b - RC1 NO (at T)', row(r, 'RC1 (F30l)') is False and r['ref'].get('close_dist') == 1)
r = read(mod(c6x, lambda t: t['frames'][-1].update(rts_chk=421, rts_chk_b=10 ** 7, rts_pb=10 ** 7)))
ok &= check('item 662 (b): chk >= chk_b at T, process chk < chk_b - RC1 NO (process)', row(r, 'RC1 (F30l)') is False and r['ref'].get('close_dist') == 1)
r = read(mod(c6x, lambda t: t['frames'][-3].update(rts_bad_rx=4)))
ok &= check('item 662 (v)(1): rx ahead of b on the last 3 lines - distance 3, parse YES', r['ref'].get('close_dist') == 3 and row(r, 'parse') is True
            and r['ref'].get('tail_dev', {}).get('rx_b') == 1)
r = read(mod(c6x, lambda t: t['frames'][-4].update(rts_bad_rx=4)))
ok &= check('item 662 (v)(1): rx ahead of b on the last 4 lines - distance 4, parse NO', r['ref'].get('close_dist') == 4 and row(r, 'parse') is False)
r = read(mod(c6x, lambda t: t['frames'][-3].update(rts_bad_b=4, rts_bad=0, rts_bad_noreg=0)))
ok &= check('item 662 (v)(1): b ahead of bad on the last 3 lines - distance 3, tail b_bad 4', r['ref'].get('close_dist') == 3
            and r['ref'].get('tail_dev', {}).get('b_bad') == 4)
r = read(mod(c6x, lambda t: (t['frames'][-3].update(rts_chk_b=402), t['frames'][-1].update(rts_chk_b=398))))
ok &= check('item 662: event torn in the tail and closed at the last line - distance 0, tail 0', r['status'] == 'ADMITTED'
            and r['ref'].get('close_dist') == 0 and r['ref'].get('tail_dev') == dict(chk_pa=0, chkb_pb=0, rx_b=0, b_bad=0))
r = read(mod(c6x, lambda t: [f.update(rts_chk_b=401) for f in t['frames']]))
ok &= check('item 662: T only before the window - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED' and row(r, 'parse') is False)
r = read(mod(c6, lambda t: fr(t, NFR - 1, rts_chk=421, rts_inj=3)))
ok &= check('RC4 (F30p) read at T: 3 perturbations on the tail after T only - ok (process inj 159)', row(r, 'RC4 (F30p') is True
            and r['inj']['proc']['rts_inj'] == NINJ + 3)
r = read(mod(c6, lambda t: (fr(t, NFR - 1, rts_chk=421), fr(t, NFR - 2, rts_inj=3))))
ok &= check('RC4 (F30p) 3 extra perturbations inside T - NO', row(r, 'RC4 (F30p') is False)

# RC2 of F30l
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad_s=8)))
ok &= check('RC2 (F30l) s 8 > b 7 - NO and STOP', row(r, 'RC2 (F30l)') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'RC2 (F30l)'))
for k in ('rts_bad_r', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_xr'):
    ok &= check('RC2 (F30l) %s 5 > rx 4 - NO' % k, row(read(mod(c6x, lambda t: fr(t, 100, **{k: 5}))), 'RC2 (F30l)') is False)
ok &= check('RC2 (F30l) l 8 > b 7 - NO', row(read(mod(c6x, lambda t: fr(t, 100, rts_bad_l=8))), 'RC2 (F30l)') is False)
ok &= check('RC2 (F30l) s 8 > b 7 but <= bad 9 - NO', row(read(mod(c6x, lambda t: fr(t, 100, rts_bad=9, rts_bad_noreg=9, rts_bad_s=8))), 'RC2 (F30l)') is False)
ok &= check('RC2 (F30l) b 8 > bad 7 - NO', row(read(mod(c6x, lambda t: fr(t, 100, rts_bad_b=8))), 'RC2 (F30l)') is False)
r = read(mod(c6x, lambda t: (fr(t, 100, rts_bad_s=8), t['mid'].append('Window 1 minimized'))))
ok &= check('RC2 (F30l) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')


def rc2_case(rx_, r_, xr, xc, xe, b, s8_extra):
    def fn(t):
        t['frames'][100].update(rts_bad=b, rts_bad_noreg=b, rts_bad_b=b, rts_bad_rx=rx_, rts_bad_r=r_, rts_bad_xr=xr, rts_bad_xc=xc,
                                rts_bad_xe=xe, rts_bad_s=s8_extra, rts_bad_p=0, rts_bad_m=0, rts_bad_l=0)
        t['mid'] = [z for z in t['mid'] if not z.startswith('RtSkipVerify')]
    return mod(c6x, fn)


ok &= check('RC2 tolerance: rx 5 = r+xr+xc+xe 4 + 1 - YES', row(read(rc2_case(5, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is True)
ok &= check('RC2 tolerance: rx 6 > 4 + 1 - NO', row(read(rc2_case(6, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is False)
ok &= check('RC2 tolerance: b 9 = sum8 8 + 1 - YES', row(read(rc2_case(4, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is True)
ok &= check('RC2 tolerance: b 10 > sum8 8 + 1 - NO', row(read(rc2_case(4, 1, 1, 1, 1, 10, 4)), 'RC2 (F30l)') is False)
ok &= check('RC2 per line - reference row', 'lines out of RC2 0' in [a for a, b in rx['admission'] if a.startswith('RC2 (F30l)')][0])

# RC4 of F30l
for kd, s in (('c6x', c6x), ('w6', w6)):
    r = read(mod(s, lambda t: fr(t, 100, rts_bad_noreg=0, rts_bad=1, rts_bad_b=1, rts_bad_p=1)))
    ok &= check('RC4 (F30l) %s noreg != bad - NO and STOP' % kd, row(r, 'RC4 (F30l)') is False and r['status'] == 'NOT_ADMITTED'
                and stopped(r, 'RC4 (F30l)'))

# reconciliation (mode=6)
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad_s=2, rts_bad_b=7)))
ok &= check('reconciliation exact: s 2 vs lines 1 - NO and STOP', row(r, 'reconciliation') is False and stopped(r, 'reconciliation failed'))
ok &= check('reconciliation exact: lines with X 3 > xr+xc+xe 2 - NO', row(read(mod(c6x, lambda t: fr(t, 100, rts_bad_xe=0))), 'reconciliation') is False)
ok &= check('reconciliation exact: xr 2 <= lines X 3 = xr+xc+xe 3 - YES',
            row(read(mod(c6x, lambda t: fr(t, 100, rts_bad_xr=2, rts_bad_xc=0, rts_bad_xe=1))), 'reconciliation') is True)
ok &= check('reconciliation exact: xc 4 > lines X 3 - NO', row(read(mod(c6x, lambda t: fr(t, 100, rts_bad_xr=0, rts_bad_xc=4, rts_bad_xe=0))), 'reconciliation') is False)
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad=8, rts_bad_noreg=8, rts_bad_b=8, rts_bad_p=2)))
ok &= check('reconciliation exhausted-form (lines 7 < bad 8): p 2 >= 1 YES, no STOP', row(r, 'reconciliation') is True and r['rec']['exact'] is False
            and not stopped(r, 'reconciliation'))
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad=8, rts_bad_noreg=8, rts_bad_b=8, rts_bad_m=0, rts_bad_p=2)))
ok &= check('reconciliation not exact: m 0 < lines 1 - NO, no STOP', row(r, 'reconciliation') is False and not stopped(r, 'reconciliation'))
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad=8, rts_bad_noreg=8, rts_bad_xe=0)))
ok &= check('reconciliation not exact: xr+xc+xe 2 < lines with X 3 - NO', row(r, 'reconciliation') is False and r['rec']['exact'] is False)
r = read(mod(c6x, lambda t: fr(t, 100, rts_bad=8, rts_bad_noreg=8, rts_bad_rx=4, rts_bad_xr=0, rts_bad_xc=0, rts_bad_xe=3, rts_bad_r=1)))
ok &= check('reconciliation not exact: xr+xc+xe 3 >= lines with X 3 - YES', row(r, 'reconciliation') is True)
r = read(mod(c6x, lambda t: (fr(t, 100, rts_bad=8, rts_bad_noreg=8),
                              t['mid'].append('RtSkipVerify: MISMATCH frame=9 bits=0x040 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=2'))))
ok &= check('reconciliation counts only mode=6 lines: a mode=2 line ignored', row(r, 'reconciliation') is True and r['rec']['n'] == 7
            and r['rec']['exact'] is False)


def many(nl, bad, s_cnt, s_lines):
    def fn(t):
        put_reports(t, [('0x040', dict(rts_bad_s=1)) if i < s_lines else ('0x200', dict(rts_bad_l=1)) for i in range(nl)])
        f = t['frames'][100]
        extra = bad - nl
        f['rts_bad'] += extra
        f['rts_bad_noreg'] += extra
        f['rts_bad_b'] += extra
        f['rts_bad_l'] += extra
        f['rts_bad_s'] = s_cnt
        f['rts_bad_l'] = f['rts_bad_b'] - s_cnt
    return mod(c6x, fn)


r = read(many(40, 40, 5, 5))
ok &= check('reconciliation 40 lines = bad 40: exact, s 5 YES', row(r, 'reconciliation') is True and r['rec']['exact'] is True)
ok &= check('reconciliation 40 = 40: s 6 vs 5 NO', row(read(many(40, 40, 6, 5)), 'reconciliation') is False)
r = read(many(40, 41, 6, 5))
ok &= check('reconciliation exhausted (bad 41): s 6 >= 5 YES', row(r, 'reconciliation') is True and r['rec']['exact'] is False)
r = read(many(40, 41, 4, 5))
ok &= check('reconciliation exhausted: s 4 < 5 NO, no STOP', row(r, 'reconciliation') is False and not stopped(r, 'reconciliation'))
r = read(mod(c6x, lambda t: put_reports(t, [('0x040', dict(rts_bad_s=1))] * 41)))
ok &= check('parse: 41 lines = bad 41 > 40 lines - NO; reconciliation not exact', row(r, 'parse') is False and r['rec']['exact'] is False)
r = read(mod(c6x, lambda t: put_reports(t, [('0x010', dict(rts_bad_r=1))])))
ok &= check('reconciliation exact: one R line (bit 0x010) against r 1, rx 1, b 1 - YES', row(r, 'reconciliation') is True and r['rec']['exact'] is True)
r = read(mod(c6x, lambda t: put_reports(t, [('0x020', dict(rts_bad_xr=1))])))
ok &= check('reconciliation exact: one X line (bit 0x020) - r 0 against lines with 0x010 0 - YES', row(r, 'reconciliation') is True
            and r['rec']['lines']['rts_bad_r'] == 0)

# RC2 / RC3 / K_S edges of the new code
r = read(mod(c6, lambda t: [fr(t, i, rts_inj_s=0, rts_inj_race=1, rts_race=1) for i in (200, 201)]))
ok &= check('RC2 (F30p): 2 perturbations raced, race 2 - ADMITTED (the race term counts) %s' % r['why'], r['status'] == 'ADMITTED'
            and row(r, 'RC2 (F30p') is True)
r = read(mod(c6, lambda t: [fr(t, i, rts_inj_s=0, rts_inj_race=1, rts_race=1) for i in INJ_FRAMES]))
ok &= check('K_S: every perturbation raced (inj 156, inj_s 0, nos 0) - ADMITTED, K_S NO', r['status'] == 'ADMITTED' and r['ks'] is False)


def bad_short(t):
    for i in (200, 201):
        fr(t, i, rts_bad=0, rts_bad_noreg=0, rts_bad_b=0)
    fr(t, NFR - 1, rts_chk=421, rts_bad=2, rts_bad_noreg=2, rts_bad_b=2)


r = read(mod(c6, bad_short))
ok &= check('RC3 (F30p): rts_bad at T 154 < inj_s 156 - 1 with bad_s 156 (the tail restores the process sums) - NO %s' % r['why'],
            row(r, 'RC3 (F30p') is False and row(r, 'RC2 (F30l)') is True and row(r, 'parse') is True)

# references
ok &= check('FixB42 window increments 480x270 4/3/4', rx['b42']['per_extent'].get('480x270') == dict(hit=4, applied=3, drawn=4))
r = read(mod(c6x, lambda t: t.__setitem__('stdout', '--- Fatal Error --- x')))
ok &= check('death markers - reference row at c6', '--- Fatal Error ---' in r['ref']['death'] and r['status'] == 'ADMITTED')
ok &= check('mm_bits counts per bits text', rx['mm_bits'] == {'0x010': 1, '0x020': 3, '0x040': 1, '0x080': 1, '0x100': 1})
ok &= check('rows out ASCII and STOP none', all(ord(c) < 128 for c in '\n'.join(R.rows_out(rx))) and R.rows_out(rx)[-1] == '  STOP none')

# --- scene rows and table ---
rd = os.path.join(TMP, 'runs')
for t, s in (('f30_s1_w6', w6), ('f30_s1_c6', c6), ('f30_s9_c6', CLEAN[('c6', 's9')][0])):
    d = os.path.join(rd, t)
    os.makedirs(d, exist_ok=True)
    write(os.path.join(TMP, 'w_' + t), s)
    rr = R.read_tag(t, R.paths(t, os.path.join(TMP, 'w_' + t)))
    json.dump(rr, open(os.path.join(d, 'read.json'), 'w'), default=list)
d = os.path.join(rd, 'f30_s2_c6')
os.makedirs(d, exist_ok=True)
s2 = mod(c6, lambda t: (t.__setitem__('scene', 's2'), t['run']['env'].__setitem__('KYTY_GUEST_ARGS', '-lvl hoover_beach'),
                        t['run'].__setitem__('guest_args', '-lvl hoover_beach'), t['side'].__setitem__('level', 'hoover_beach'), no_inj(t, True)))
write(os.path.join(TMP, 'w_s2'), s2)
json.dump(R.read_tag('f30_s2_c6', R.paths('f30_s2_c6', os.path.join(TMP, 'w_s2'))), open(os.path.join(d, 'read.json'), 'w'), default=list)
tb = R.table(rd)
last = tb[-1]
ok &= check('scene rows: K_S YES 2 (s1 s9), S1 or S9 True: %s' % last, 'K_S YES 2 (s1 s9)' in last and 'S1 or S9 among them True' in last)
ok &= check('scene rows: s2 admitted, K_S False', any(l.startswith('s2 hoover_beach: c6 ADMITTED; K_S False') for l in tb))
ok &= check('scene rows: w6 all YES', any(l.startswith('w6 f30_s1_w6: ADMITTED; members all YES') for l in tb))
ok &= check('table rows 4', sum(1 for l in tb if l.startswith('| f30_')) == 4)
d = os.path.join(rd, 'f30_s3_c6')
os.makedirs(d, exist_ok=True)
s3 = mod(c6, lambda t: (t.__setitem__('scene', 's3'), t['run']['env'].__setitem__('KYTY_GUEST_ARGS', '-lvl mini_giants_garden'),
                        t['run'].__setitem__('guest_args', '-lvl mini_giants_garden'), t['side'].__setitem__('level', 'mini_giants_garden'),
                        fr(t, 5, rts_ovf=1)))
LEVEL['s3'] = 'mini_giants_garden'
write(os.path.join(TMP, 'w_s3'), s3)
r3 = R.read_tag('f30_s3_c6', R.paths('f30_s3_c6', os.path.join(TMP, 'w_s3')))
json.dump(r3, open(os.path.join(d, 'read.json'), 'w'), default=list)
ok &= check('s3 fixture NOT_ADMITTED with K_S True', r3['status'] == 'NOT_ADMITTED' and r3['ks'] is True)
tb = R.table(rd)
ok &= check('scene rows: a NOT_ADMITTED tag with K_S True is not counted: %s' % tb[-1], 'K_S YES 2 (s1 s9)' in tb[-1])
rd2 = os.path.join(TMP, 'runs2')
os.makedirs(os.path.join(rd2, 'f30_s9_c6'))
shutil.copyfile(os.path.join(rd, 'f30_s9_c6', 'read.json'), os.path.join(rd2, 'f30_s9_c6', 'read.json'))
tb2 = R.table(rd2)
ok &= check('scene rows: only s9 live - S1 or S9 True: %s' % tb2[-1], 'K_S YES 1 (s9)' in tb2[-1] and 'S1 or S9 among them True' in tb2[-1])
rd3 = os.path.join(TMP, 'runs3')
os.makedirs(os.path.join(rd3, 'f30_s6_c6'))
json.dump(dict(CLEAN[('c6', 's6')][1], tag='f30_s6_c6'), open(os.path.join(rd3, 'f30_s6_c6', 'read.json'), 'w'), default=list)
tb3 = R.table(rd3)
ok &= check('scene rows: only s6 live - S1 or S9 False: %s' % tb3[-1], 'K_S YES 1 (s6)' in tb3[-1] and 'S1 or S9 among them False' in tb3[-1])

# --- S9 window end: last FrameTrace n >= 1650 ---
s9 = CLEAN[('c6', 's9')][0]
r = read(mod(s9, lambda t: t.__setitem__('n0', 1650 - 3 - NFR + 1)))
ok &= check('S9 last n 1650 - ok', row(r, 'S9 window end') is True and r['status'] == 'ADMITTED')
r = read(mod(s9, lambda t: t.__setitem__('n0', 1650 - 3 - NFR)))
ok &= check('S9 last n 1649 - NO', row(r, 'S9 window end') is False and r['status'] == 'NOT_ADMITTED')
ok &= check('S9 member only at s9', row(r6, 'S9 window end') is None)

# --- strict cp1250 output, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, w6)
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'f30_s1_w6', '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('json written, status ADMITTED', json.load(open(js))['status'] == 'ADMITTED')
out = io.StringIO()
with contextlib.redirect_stdout(out):
    rc_u = R.main(['f30_cy_v'])
    rc_j = R.main(['--dir', d, '--tag', 'f30_s1_w6', '--json', os.path.join(d, 'es.json')])
ok &= check('usage rc 2 for a tag of F30m; refusal to overwrite the run json', rc_u == 2 and rc_j == 2)
shutil.rmtree(str(BASE), ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
