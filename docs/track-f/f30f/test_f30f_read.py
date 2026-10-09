"""Fixtures of f30f_read.py (Track F link F30f, HPP-711; ROADMAP s122 item 643 (d), (g), item 644 (b)-(d)): a clean synthetic tag of each
kind (c3, c4, v; scenes s1, s9 with the keys, in) reads ADMITTED with every member YES; every admission member (harness, (D1)-(D7), RC4,
parse), every member of each kind ((K), (K'), race, RC1, RC2 (a) / (b), RC3, K_B, (C1), (V), (O)) and each edge (x lines 1499 / 1500,
2999 / 3000, share 0.95, chk_b 999 999 / 1 000 000, threshold 99 / 100 of RC2 (b), 40 lines of RC3, tear of one event vs two, blocks of
OLD 90 %, the two skipped blocks) flips the reading; the STOP rows; FixB42 window increments; kappa; the scene rows; strict cp1250 output
without PYTHONIOENCODING; the last line is ALL OK.  Early-exit form of mutlib (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII
only.  The reader is loaded in-process from argv[1] (default: f30f_read.py beside this file); the fixture directories live under BASE.
usage: python test_f30f_read.py [<f30f_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f30f_read.py')
BASE = Path(os.path.join(HERE, 'fx_f30f'))   # mutlib gives every job its own copy of this directory
_spec = importlib.util.spec_from_file_location('f30f_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f30f_read.py sha256 %s target f30f_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = '3bc7ada7980a89fee30b17780f8dfbee0b3921332d81f1f63984d6252a811347'   # literals, not the reader's constants (mutants)
FS10 = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'
TBIN = 'C:/kyty/f287/bin/kyty_emulator_3bc7ada7.exe'
FS10BIN = 'C:/kyty/f287/bin/kyty_emulator_abfded5e.exe'
KREF = os.path.join(HERE, 'kref_f30f.tsv')
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
KEYS = ('@1300:a/@45 @1380:w/@45 @1500:w/@96 @1650:h/@975 @2600:f/@1003 @3550:w/@18 @3600:d/@30 @3650:s/@31 @3700:a/@31 '
        '@3750:w/@49 @3800:w/@90 @3900:h/@966 @4850:f/@984 @5800:w/@17 @5830:d/@25 @5860:s/@25 @5890:a/@25 @5920:w/@25')
LEVEL = {'s1': 'underwater_aerial_garden', 's9': 'underwater_aerial_garden', 'in': 'intro_next', 's6': 'sponge_dirty_bath'}
FIELDS = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx',
          'rts_race', 'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
          'rts_xb_bound', 'rts_xb_pass', 'rts_early')
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
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8',
             KYTY_RT_SKIP={'c3': '3', 'c4': '4', 'v': '2', 'v2': '2'}[kind])
    if kind in ('v', 'v2'):
        e['KYTY_REC'] = 'C:/x/rec.mp4'
    if scene == 's9':
        e['KYTY_KEYS'] = KEYS
    return e


def spec(kind, scene='s1'):
    knob = {'c3': 3, 'c4': 4, 'v': 2, 'v2': 2}[kind]
    nfr = {'c3': 1600, 'c4': 1600, 'v': 3100, 'v2': 3100}[kind]
    head = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', '  version: Fork build arigandores/KytyPS5 a1d1d86',
            'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
            'RtSkip: mode %d ctx_slots=8 groups=11 rec_bytes=7192' % knob,
            'FixB42: mode=1 hit=2 applied=1 drawn=5 rearm=0 hit_all=2 last_frame=1 extent=480x270 cmask=0x1 clear=00000000/00000000']
    mid = ['FixB42Ext: mode=1 extent=480x270 hit=6 applied=4 drawn=9 rearm=0 frame=50',
           'FixB42: mode=1 hit=3 applied=0 drawn=1 rearm=0 hit_all=9 last_frame=60 extent=1920x1080 cmask=0x1 clear=00000000/00000000']
    frames = [frame() for _ in range(nfr)]
    if kind == 'c3':
        mid.append('RtSkipVerify: MISMATCH frame=900 bits=0x401 reg=1 chain=0 colors=5 depth=1 pa=1 pb=1 mode=3')
        frames[100]['rts_bad'] = 1
    if kind == 'c4':
        for b in ('0x220', '0x200', '0x010'):
            mid.append('RtSkipVerify: MISMATCH frame=900 bits=%s reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=4' % b)
        frames[100].update(rts_bad=3, rts_bad_b=3, rts_bad_rx=2, rts_bad_noreg=3, rts_xb_ids=5, rts_xb_bound=1)
    bda = [700 if kind in ('v', 'v2') else 100] * nfr
    tail = ['LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0']
    hold = {'c3': 150, 'c4': 150, 'v': 300, 'v2': 300}[kind]
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold) + 0.1, started_s=30.0, stable_s=42.0, launch_sha256=TB)
    run = dict(binary_sha256=TB, env=env_of(scene, kind), cmdline=cmd, attempts=[att], guest_args='-lvl ' + LEVEL[scene], hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()), gates='', schedule='')
    side = dict(installed_before=FS10, installed_after=FS10, installed_sha=TB, level=LEVEL[scene])
    vread = None
    if kind == 'c4':
        vread = dict(tag='f30_%s_v' % scene, proc=dict(rts_xb_ids=150, rts_xb_live=99, rts_xb_bound=100, rts_xb_pass=0))
    return dict(head=head, pre=[frame(rts_n=7, rts_pa=0, rts_chk=0, rts_pb=0, rts_chk_b=0) for _ in range(3)], entry=True, mid=mid, frames=frames,
                bda=bda, tail=tail, run=run, side=side, vread=vread, scene=scene, kind=kind, idx=(3200 if kind in ('v', 'v2') else 0),
                stdout='', drop=set(), extra_draw=0, n0=(100 if scene == 's9' else 1))


def xline(n, f, drop=()):
    return 'FrameTrace-x: n=%d ds_ring_new=0 ' % n + ' '.join('%s=%d' % (k, v) for k, v in f.items() if k not in drop)


def lines_of(s):
    L = list(s['head'])
    n = s['n0']
    for f in s['pre']:
        L += ['FrameTrace: n=%d dt_us=16000 draws=10' % n, 'FrameTrace-draw: n=%d logs=1 bda_scan=50' % n, xline(n, f)]
        n += 1
    L.append('GuestOut: Level has started: ')
    if s['entry']:
        L.append('GuestOut: Level has started: %s' % LEVEL[s['scene']])
    L += s['mid']
    for i, f in enumerate(s['frames']):
        L += ['FrameTrace: n=%d dt_us=33000 draws=500' % n, 'FrameTrace-draw: n=%d logs=1 bda_scan=%d' % (n, s['bda'][i]),
              xline(n, f, s['drop'] if i == 7 else ())]
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
    if s['idx']:
        with open(os.path.join(d, 'rec.idx'), 'w') as f:
            f.write('r\n' * s['idx'])
    if s['vread'] is not None:
        with open(os.path.join(d, 'v_read.json'), 'w') as f:
            json.dump(s['vread'], f)


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


def adm(r, start):
    for a, b in r['admission']:
        if a.startswith(start):
            return b
    return None


def mem(r, start):
    for a, b in (r['members'] or []):
        if a.startswith(start):
            return b
    return None


def mod(s, fn):
    t = copy.deepcopy(s)
    fn(t)
    return t


# --- clean tags ---
CLEAN = {}
for kind, scene in (('c3', 's1'), ('c4', 's1'), ('v', 's1'), ('c3', 's9'), ('v', 's9'), ('c3', 'in'), ('v2', 's6')):
    s = spec(kind, scene)
    r = read(s)
    CLEAN[(kind, scene)] = (s, r)
    ok &= check('%s %s clean ADMITTED %s' % (kind, scene, [a for a, x in r['admission'] if not x][:3]), r['status'] == 'ADMITTED')
    ok &= check('%s %s clean members all YES %s' % (kind, scene, [a for a, x in (r['members'] or []) if not x]),
                r['members'] is not None and all(x for a, x in r['members']))
    ok &= check('%s %s clean no STOP %s' % (kind, scene, r['stop']), r['stop'] == [])
c3, r3 = CLEAN[('c3', 's1')]
c4, r4 = CLEAN[('c4', 's1')]
cv, rv = CLEAN[('v', 's1')]
ok &= check('members count c3 3, c4 2, v 4', len(r3['members']) == 3 and len(r4['members']) == 2 and len(rv['members']) == 4)
ok &= check('clean c4 K_B (i) 2, (ii) 2, exact reconciliation', r4['kb'] == dict(i=2, ii=2, lines_mode4=3, lines_b=3, bad=3, bad_b=3, exact=True))
ok &= check('clean c4 RC2 (b) rows: ids checked, live 99 not checked, bound 100 checked, pass 0 not checked %s' % r4['rc2b'],
            r4['rc2b'] == ['rts_xb_ids v 150 c4 5 ok', 'rts_xb_live v 99 < 100 - not checked (c4 0)', 'rts_xb_bound v 100 c4 1 ok',
                           'rts_xb_pass v 0 < 100 - not checked (c4 0)'])
ok &= check('clean v sums: window chk_b 3100 x 400 %d, process includes the pre frames n %d' % (rv['win']['rts_chk_b'], rv['proc']['rts_n']),
            rv['win']['rts_chk_b'] == 1240000 and rv['proc']['rts_n'] == 3100 * 500 + 21)
ok &= check('clean v BDA OLD, read blocks 33, OLD chk_b %s' % rv['bda'], rv['bda']['mode'] == 'OLD' and rv['bda']['read_blocks'] == 33
            and rv['bda']['chkb_old'] == (3100 - 180) * 400)
for t in ('f30_s1_c3', 'f30_s9_v_r2', 'f30_in_c4', 'f30_s6_v2', 'f30_s8_v2_r1'):
    ok &= check('tag form %s' % t, R.TAG_RX.match(t) is not None)
for t in ('f30_s0_c3', 'f30_s1_c5', 'f30_s1_v_r4', 'f30_x_v', 'b12_v'):
    ok &= check('tag form refused %s' % t, R.TAG_RX.match(t) is None)

# --- harness admission ---
for key, val in (('installed_before', TB), ('installed_after', TB), ('installed_sha', FS10), ('level', 'pot')):
    ok &= check('admission side %s' % key, read(mod(c3, lambda t: t['side'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
for key, val in (('binary_sha256', FS10), ('guest_args', '-lvl pot'), ('hold_s', 151), ('gates', 'rtskip=1'), ('schedule', 'x')):
    ok &= check('admission run %s' % key, read(mod(c3, lambda t: t['run'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
ok &= check('admission prereg', read(mod(c3, lambda t: t['run']['prereg'].__setitem__('sha256', 'x')))['status'] == 'NOT_ADMITTED')
for k, v in (('KYTY_RT_SKIP', '2'), ('KYTY_FIX_B42', '0'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'), ('KYTY_RK3_CENSUS', '1'),
             ('KYTY_SPINE', '1'), ('KYTY_REC', 'x'), ('KYTY_KEYS', KEYS)):
    ok &= check('admission env %s=%s' % (k, v), read(mod(c3, lambda t: t['run']['env'].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
for k0 in ('KYTY_RT_SKIP', 'KYTY_GPU_CLOCK_PIN', 'KYTY_FRAME_TRACE'):
    ok &= check('admission env missing %s' % k0, read(mod(c3, lambda t: t['run']['env'].pop(k0)))['status'] == 'NOT_ADMITTED')
ok &= check('admission s9 without KYTY_KEYS', read(mod(CLEAN[('c3', 's9')][0], lambda t: t['run']['env'].pop('KYTY_KEYS')))['status'] == 'NOT_ADMITTED')
ok &= check('admission s9 keys changed', read(mod(CLEAN[('c3', 's9')][0], lambda t: t['run']['env'].__setitem__('KYTY_KEYS', KEYS[:-1])))['status'] == 'NOT_ADMITTED')
ok &= check('admission v without KYTY_REC', read(mod(cv, lambda t: t['run']['env'].pop('KYTY_REC')))['status'] == 'NOT_ADMITTED')
for extra in (['--vulkan-validation', 'true'], ['--shader-validation', 'true'], ['--rd'], ['--graphics-debug-dump', 'true']):
    ok &= check('admission cmdline %s' % extra, read(mod(c3, lambda t: t['run'].__setitem__('cmdline', t['run']['cmdline'] + extra)))['status'] == 'NOT_ADMITTED')
ok &= check('admission --graphics-debug-dump false is fine', read(mod(c3, lambda t: t['run'].__setitem__('cmdline', t['run']['cmdline'] + ['--graphics-debug-dump', 'false'])))['status'] == 'ADMITTED')
for k, v in (('outcome', 'timeout'), ('hold_exit', 3), ('started_s', None), ('stable_s', 'x')):
    ok &= check('admission attempt %s=%s' % (k, v), read(mod(c3, lambda t: t['run']['attempts'][0].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
ok &= check('window: stable = started, hold_s 149.9 - NO', read(mod(c3, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=149.9)))['status'] == 'NOT_ADMITTED')
ok &= check('window: stable = started, hold_s 150.0 - YES', read(mod(c3, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=150.0)))['status'] == 'ADMITTED')
ok &= check('window: stable 5 s after the entry, hold_s 145.0 - YES (150 from the entry)', read(mod(c3, lambda t: t['run']['attempts'][0].update(stable_s=35.0, hold_s=145.0)))['status'] == 'ADMITTED')
ok &= check('window: v stable = started, hold_s 299.9 - NO', read(mod(cv, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=299.9)))['status'] == 'NOT_ADMITTED')
ok &= check('admission no entry line', read(mod(c3, lambda t: t.__setitem__('entry', False)))['status'] == 'NOT_ADMITTED')
for ln in ('Window 1 minimized', 'Recovering Vulkan swapchain 1'):
    ok &= check('window event %s - INTERFERENCE' % ln, read(mod(c3, lambda t: t['mid'].append(ln)))['status'] == 'INTERFERENCE')
ok &= check('window event restored only - ADMITTED', read(mod(c3, lambda t: t['mid'].append('Window 1 restored')))['status'] == 'ADMITTED')
ok &= check('no summary line - INTERFERENCE', read(mod(c3, lambda t: t.__setitem__('tail', [])))['status'] == 'INTERFERENCE')
ok &= check('two summary lines - NOT_ADMITTED', read(mod(c3, lambda t: t.__setitem__('tail', t['tail'] * 2)))['status'] == 'NOT_ADMITTED')
for ln in ('GamePatch: x', 'DiagB32 x', 'TestLogStall: x'):
    ok &= check('admission line %s' % ln, read(mod(c3, lambda t: t['mid'].append(ln)))['status'] == 'NOT_ADMITTED')
ok &= check('admission signature', read(mod(c3, lambda t: t['head'].__setitem__(2, 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40))))['status'] == 'NOT_ADMITTED')
ok &= check('admission catalog', read(mod(c3, lambda t: t['head'].__setitem__(3, 'Shader translation cache: C:/e/variant_fixb26_fixb1b_fixf10')))['status'] == 'NOT_ADMITTED')
ok &= check('log absent - NOT_ADMITTED', R.read_tag('f30_s1_c3', dict(R.paths('f30_s1_c3', os.path.join(TMP, 'none')), log='C:/no/such/log.txt'))['status'] == 'NOT_ADMITTED')

# --- (D1)-(D7) ---
ok &= check('(D1) two mode lines', adm(read(mod(c3, lambda t: t['head'].append('RtSkip: mode 3 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) another value', adm(read(mod(c3, lambda t: t['head'].append('RtSkip: mode 2 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) no mode line', adm(read(mod(c3, lambda t: t['head'].pop(4))), '(D1)') is False)
ok &= check('(D1) prefixed line counts', adm(read(mod(c3, lambda t: t['head'].__setitem__(4, '[1][x] RtSkip: mode 3 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is True)
r = read(mod(c3, lambda t: t['mid'].append('RtSkip: refused reason=rk3cen')))
ok &= check('(D2) refused line - NO and STOP', adm(r, '(D2)') is False and any('refused' in z for z in r['stop']))
r = read(mod(c3, lambda t: t['frames'][3].__setitem__('rts_refuse', 1)))
ok &= check('(D2) rts_refuse 1', adm(r, '(D2)') is False)
ok &= check('(D3) gate rtskip=3 fine', adm(read(mod(c3, lambda t: t['mid'].append('Gate: rtskip=3 frame=5'))), '(D3)') is True)
ok &= check('(D3) gate rtskip=0', adm(read(mod(c3, lambda t: t['mid'].append('Gate: rtskip=0 frame=5'))), '(D3)') is False)
for k in ('rts_xthr', 'rts_acqw'):
    r = read(mod(c3, lambda t: t['pre'].__setitem__(0, dict(t['pre'][0], **{k: 1}))))
    ok &= check('(D4) %s before the entry - NO and STOP' % k, adm(r, '(D4)') is False and any('(D4)' in z for z in r['stop']))
ok &= check('(D5) c3 1500 x lines YES', adm(read(mod(c3, lambda t: t.__setitem__('frames', t['frames'][:1500]))), '(D5)') is True)
ok &= check('(D5) c3 1499 x lines NO', adm(read(mod(c3, lambda t: t.__setitem__('frames', t['frames'][:1499]))), '(D5)') is False)
ok &= check('(D5) c4 1499 x lines NO', adm(read(mod(c4, lambda t: t.__setitem__('frames', t['frames'][:1499]))), '(D5)') is False)
ok &= check('(D5) v 3000 x lines YES', adm(read(mod(cv, lambda t: t.__setitem__('frames', t['frames'][:3000]))), '(D5)') is True)
ok &= check('(D5) v 2999 x lines NO', adm(read(mod(cv, lambda t: t.__setitem__('frames', t['frames'][:2999]))), '(D5)') is False)
ok &= check('(D5) share: 3000 x, 3157 draw YES', adm(read(mod(cv, lambda t: (t.__setitem__('frames', t['frames'][:3000]), t.__setitem__('extra_draw', 157)))), '(D5)') is True)
ok &= check('(D5) share: 3000 x, 3158 draw NO', adm(read(mod(cv, lambda t: (t.__setitem__('frames', t['frames'][:3000]), t.__setitem__('extra_draw', 158)))), '(D5)') is False)
ok &= check('(D6) rts_ovf in the window', adm(read(mod(c3, lambda t: t['frames'][5].__setitem__('rts_ovf', 1))), '(D6)') is False)
ok &= check('(D6) rts_ovf before the entry fine', adm(read(mod(c3, lambda t: t['pre'].__setitem__(1, dict(t['pre'][1], rts_ovf=1)))), '(D6)') is True)
r = read(mod(c3, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', FS10)))
ok &= check('(D7) launch_sha256 not T - NOT_ADMITTED', adm(r, '(D7)') is False and r['status'] == 'NOT_ADMITTED')
ok &= check('(D7) no launch_sha256', adm(read(mod(c3, lambda t: t['run']['attempts'][0].pop('launch_sha256'))), '(D7)') is False)
ok &= check('(D7) fork line of FS10', adm(read(mod(c3, lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 dc5d471'))), '(D7)') is False)
ok &= check('(D7) two fork lines', adm(read(mod(c3, lambda t: t['head'].append('  version: Fork build arigandores/KytyPS5 a1d1d86'))), '(D7)') is False)
ok &= check('(D7) no fork line', adm(read(mod(c3, lambda t: t['head'].pop(1))), '(D7)') is False)
ok &= check('(D7) fork line a1d1d86-dirty', adm(read(mod(c3, lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 a1d1d86-dirty'))), '(D7)') is False)
ok &= check('(D7) fork text without version: is not the line', adm(read(mod(c3, lambda t: t['head'].__setitem__(1, 'Fork build arigandores/KytyPS5 a1d1d86'))), '(D7)') is False)
ok &= check('(D7) binary_sha256 of FS10 with launch_sha256 of T - (D7) NO', adm(read(mod(c3, lambda t: t['run'].__setitem__('binary_sha256', FS10))), '(D7)') is False)
ok &= check('(D7) binary_sha256 != launch_sha256', adm(read(mod(c3, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', 'f' * 64))), '(D7)') is False)
ok &= check('(D7) pinned copy not T', adm(read(mod(c3, lambda t: t.__setitem__('binpath', FS10BIN))), '(D7)') is False)
r = read(mod(c3, lambda t: (t['mid'].append('Window 1 minimized'), t['run']['attempts'][0].__setitem__('launch_sha256', FS10))))
ok &= check('(D7) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
ok &= check('(D7) letter row printed: 0 version lines in a clean log', '(0 lines) NO' in [a for a, b in r3['admission'] if a.startswith('(D7)')][0])
ok &= check('(D7) the letter row does not decide: a version line in the log changes nothing', read(mod(c3, lambda t: t['mid'].append('x KytyPS5-2026-09-15-6a2987a-1906-ga1d1d863')))['status'] == 'ADMITTED')
S9, R9 = CLEAN[('c3', 's9')]
ok &= check('S9 clean: last n 1702 >= 1650 %s' % [a for a, b in R9['admission'] if a.startswith('S9 ')], adm(R9, 'S9 ') is True)
ok &= check('S9 last n 1650 - YES', adm(read(mod(S9, lambda t: t.__setitem__('n0', 48))), 'S9 ') is True)
ok &= check('S9 last n 1649 - NOT_ADMITTED', read(mod(S9, lambda t: t.__setitem__('n0', 47)))['status'] == 'NOT_ADMITTED')
ok &= check('S9 member absent at s1', adm(r3, 'S9 ') is None)
r = read(mod(S9, lambda t: t['mid'].append('InputScript: press h at 52.58 s (present 1650)')))
ok &= check('S9 InputScript presents - reference row', [a for a, b in r['admission'] if a.startswith('S9 ')][0].endswith('max 1650, lines 1)'))
ok &= check('(D7) rule is the variant', R.D7_RULE == 'variant')

# --- RC4 missing field, parse ---
for k in ('rts_bad_rx', 'rts_bad_b', 'rts_chk_b', 'rts_race', 'rts_xb_pass', 'rts_lost'):
    r = read(mod(c3, lambda t: t.__setitem__('drop', {k})))
    ok &= check('RC4 missing %s in one window line - NOT_ADMITTED' % k, r['status'] == 'NOT_ADMITTED' and adm(r, 'RC4 ') is False)
r = read(mod(c3, lambda t: t['pre'].__setitem__(0, dict((a, b) for a, b in t['pre'][0].items() if a != 'rts_bad_rx'))))
ok &= check('RC4 missing field before the entry - NOT_ADMITTED', adm(r, 'RC4 ') is False)
r = read(mod(c3, lambda t: t.__setitem__('drop', {'rts_early'})))
ok &= check('RC4 a field outside REQ may be absent', r['status'] == 'ADMITTED')
r = read(mod(cv, lambda t: (t['frames'][10].__setitem__('rts_chk', 421), t['frames'][11].__setitem__('rts_chk', 419))))
ok &= check('parse: tear of one event chk/pa across two lines - YES', adm(r, 'parse') is True)
r = read(mod(cv, lambda t: (t['frames'][10].__setitem__('rts_chk', 422), t['frames'][11].__setitem__('rts_chk', 418))))
ok &= check('parse: prefix 2 (item 651 (v)(2)) - NO, NOT_ADMITTED and STOP', adm(r, 'parse') is False and r['status'] == 'NOT_ADMITTED'
            and any('item 651' in z for z in r['stop']))
r = read(mod(cv, lambda t: (t['frames'][10].__setitem__('rts_chk', 421), t['frames'][12].__setitem__('rts_chk', 419))))
ok &= check('parse: one event carried across two lines (prefix 1 on two lines) - YES, no STOP', adm(r, 'parse') is True and r['stop'] == [])
r = read(mod(cv, lambda t: t['frames'][10].__setitem__('rts_pa', 419)))
ok &= check('parse: a lost event (pa sum -1, item 651 (v)(3)) - NO and STOP', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(cv, lambda t: (t['frames'][10].__setitem__('rts_chk', 421), t['frames'][11].__setitem__('rts_chk', 419))))
ok &= check('parse: max prefix deviation row 1 for chk/pa', '"chk_pa": 1' in [a for a, b in r['admission'] if a.startswith('parse')][0])
r = read(mod(cv, lambda t: t['frames'][10].__setitem__('rts_chk', 421)))
ok &= check('parse: chk sum != pa sum - NO and STOP', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(cv, lambda t: (t['frames'][10].__setitem__('rts_chk_b', 401), t['frames'][11].__setitem__('rts_chk_b', 399))))
ok &= check('parse: tear chk_b/pb - YES', adm(r, 'parse') is True)
r = read(mod(cv, lambda t: t['frames'][10].__setitem__('rts_pb', 401)))
ok &= check('parse: pb sum != chk_b sum - NO and STOP', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(c4, lambda t: (t['frames'][100].update(rts_bad_b=1), t['frames'][101].update(rts_bad_b=2))))
ok &= check('parse: rx one event ahead of bad_b at a line (torn) - parse YES', adm(r, 'parse') is True)
r = read(mod(c4, lambda t: (t['frames'][100].update(rts_bad_b=0), t['frames'][101].update(rts_bad_b=3))))
ok &= check('parse: rx two events ahead of bad_b at a line (item 651 (v)(4)) - parse NO and STOP', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_rx=4, rts_bad_b=4, rts_bad=4)))
ok &= check('parse: rx/b/bad consistent 4/4/4 but lines 3 < 4 - parse YES', adm(r, 'parse') is True)
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_rx=3, rts_bad_b=2)))
ok &= check('parse: rx sum 3 > b sum 2 - NO and STOP (item 649 (v))', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_b=4)))
ok &= check('parse: b sum 4 > bad sum 3 - NO and STOP', adm(r, 'parse') is False and any('item 651' in z for z in r['stop']))
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_noreg=4)))
ok &= check('parse: noreg 4 > bad 3 - NO', adm(r, 'parse') is False)
r = read(mod(c3, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x401 reg=1 chain=0 colors=1 depth=0 pa=1 pb=0 mode=3')))
ok &= check('parse: 2 lines > bad 1 - NO', adm(r, 'parse') is False)
r = read(mod(c3, lambda t: t['mid'].append('RtSkipVerify: something else')))
ok &= check('parse: unparsable RtSkipVerify - NO', adm(r, 'parse') is False)
r = read(mod(cv, lambda t: t['frames'][10].__setitem__('rts_n', 300)))
ok &= check('parse: chk_b 400 <= chk 420 <= n - the sums still hold (n 300 in one line)', adm(r, 'parse') is True)
r = read(mod(cv, lambda t: [f.__setitem__('rts_n', 410) for f in t['frames']]))
ok &= check('parse: chk sum > n sum - NO, no STOP (not of item 651 (b))', adm(r, 'parse') is False and r['stop'] == [])
dup = mod(c3, lambda t: None)
CNT[0] += 1
dd = os.path.join(TMP, 'dup')
write(dd, dup)
lp = os.path.join(dd, 'log.txt')
data = open(lp, 'rb').read().replace(b'FrameTrace-x: n=200 ds_ring_new=0 ', b'FrameTrace-x: n=200 ds_ring_new=0 rts_bad=0 ', 1)
open(lp, 'wb').write(data)
r = R.read_tag('f30_s1_c3', R.paths('f30_s1_c3', dd))
ok &= check('parse: duplicate field in a line - NO', adm(r, 'parse') is False)

# --- c3 members ---
r = read(mod(c3, lambda t: t['mid'].__setitem__(2, t['mid'][2].replace('bits=0x401', 'bits=0x404'))))
ok &= check('(K) no line with bit 0x001 - NO', mem(r, '(K)') is False and r['status'] == 'ADMITTED')
r = read(mod(c3, lambda t: t['mid'].__setitem__(2, t['mid'][2].replace('mode=3', 'mode=2'))))
ok &= check('(K) line mode=2 - NO', mem(r, '(K)') is False)
r = read(mod(c3, lambda t: (t['mid'].pop(2), t['frames'][100].__setitem__('rts_bad', 0))))
ok &= check('(K) no line, rts_bad 0 - NO', mem(r, '(K)') is False)
r = read(mod(c3, lambda t: t['frames'][100].__setitem__('rts_bad', 0)))
ok &= check('(K) the line with bit 0x001 but process rts_bad 0 - NO', mem(r, '(K)') is False)
r = read(mod(c3, lambda t: t['frames'][100].__setitem__('rts_bad_noreg', 1)))
ok &= check("(K') noreg 1 - NO and STOP", mem(r, "(K')") is False and any("(K')" in z for z in r['stop']))
r = read(mod(c3, lambda t: t['pre'].__setitem__(2, dict(t['pre'][2], rts_race=1))))
ok &= check('c3 race 1 before the entry (process) - NO and STOP', mem(r, 'race') is False and any('rts_race' in z for z in r['stop']))

# --- c4 admission members RC1-RC3 and K_B ---
r = read(mod(c4, lambda t: t['frames'][3].__setitem__('rts_skip', 1)))
ok &= check('RC1 rts_skip 1 - NOT_ADMITTED, no STOP (item 649 (v))', adm(r, 'RC1 ') is False and r['status'] == 'NOT_ADMITTED' and r['stop'] == [])
r = read(mod(c4, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames']]))
ok &= check('RC1 rts_chk_b 0 - NOT_ADMITTED', adm(r, 'RC1 ') is False)
r = read(mod(c4, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames'][1:]] and None))
ok &= check('RC1 rts_chk_b 400 >= 1 - YES', adm(r, 'RC1 ') is True)
for k in ('rts_xb_meta', 'rts_xb_ser'):
    r = read(mod(c4, lambda t: t['frames'][9].__setitem__(k, 1)))
    ok &= check('RC2 (a) %s 1 - NOT_ADMITTED' % k, adm(r, 'RC2 (a)') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c4, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 3 ctx_slots=8 groups=11 rec_bytes=7192')))
ok &= check('RC2 (a) mode 3 line at c4 - NO', adm(r, 'RC2 (a)') is False)
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_xb_ids', 0)))
ok &= check('RC2 (b) v ids 150 >= 100 and c4 0 - NOT_ADMITTED', adm(r, 'RC2 (b)') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_xb_bound', 0)))
ok &= check('RC2 (b) edge v bound 100 and c4 0 - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: t['vread']['proc'].__setitem__('rts_xb_live', 100)))
ok &= check('RC2 (b) v live 100 and c4 0 - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: (t['vread']['proc'].__setitem__('rts_xb_bound', 99), t['frames'][100].__setitem__('rts_xb_bound', 0))))
ok &= check('RC2 (b) v bound 99 and c4 0 - not checked, YES', adm(r, 'RC2 (b)') is True)
r = read(mod(c4, lambda t: t['vread']['proc'].pop('rts_xb_pass')))
ok &= check('RC2 (b) v sum missing - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: t.__setitem__('vread', None)))
ok &= check('RC2 (b) no v read - WAITS_V, not admitted, no RC2 (b) row', r['status'] == 'WAITS_V' and not r['admitted'] and adm(r, 'RC2 (b)') is None)
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_rx=1)))
ok &= check('RC3 exact: rx 1 vs lines 2 - NOT_ADMITTED and STOP (item 649 (v))', adm(r, 'RC3 ') is False and r['status'] == 'NOT_ADMITTED'
            and any('RC3 reconciliation failed' in z for z in r['stop']))
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_b=3, rts_bad_rx=3, rts_bad=4)))
ok &= check('RC3 lines 3 < bad 4 (not exact): rx 3 >= 2, b 3 >= 3 YES, no STOP', adm(r, 'RC3 ') is True and r['stop'] == [])
r = read(mod(c4, lambda t: t['frames'][100].update(rts_bad_b=2, rts_bad_rx=2)))
ok &= check('RC3 exact: b 2 vs lines 3 - NO', adm(r, 'RC3 ') is False)


def c4_many(nl, bad, b, rx, rx_lines):
    def fn(t):
        t['mid'] = [z for z in t['mid'] if not z.startswith('RtSkipVerify')]
        for i in range(nl):
            bits = '0x030' if i < rx_lines else '0x200'
            t['mid'].append('RtSkipVerify: MISMATCH frame=%d bits=%s reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=4' % (i, bits))
        t['frames'][100].update(rts_bad=bad, rts_bad_b=b, rts_bad_rx=rx, rts_bad_noreg=0)
    return mod(c4, fn)


r = read(c4_many(40, 40, 40, 5, 5))
ok &= check('RC3 40 lines = bad 40: exact, rx 5 = lines 5 YES', adm(r, 'RC3 ') is True and r['kb']['exact'] is True)
r = read(c4_many(40, 40, 40, 6, 5))
ok &= check('RC3 40 lines = bad 40: exact, rx 6 vs 5 NO', adm(r, 'RC3 ') is False)
r = read(c4_many(40, 41, 41, 6, 5))
ok &= check('RC3 exhausted (bad 41): rx 6 >= 5 YES', adm(r, 'RC3 ') is True and r['kb']['exact'] is False)
r = read(c4_many(40, 41, 41, 4, 5))
ok &= check('RC3 exhausted: rx 4 < lines 5 NO, no STOP of RC3 (lines exhausted)', adm(r, 'RC3 ') is False and not any('RC3' in z for z in r['stop']))
r = read(c4_many(40, 41, 39, 0, 0))
ok &= check('RC3 exhausted: b 39 < lines with 0x3f0 40 NO', adm(r, 'RC3 ') is False)
r = read(c4_many(41, 41, 41, 6, 5))
ok &= check('RC3 41 lines = bad 41: lines over the limit 40 - parse NO, not exact (>=), RC3 YES', adm(r, 'parse') is False
            and r['kb']['exact'] is False and adm(r, 'RC3 ') is True)
r = read(c4_many(40, 50, 50, 0, 0))
ok &= check('K_B (i) rx 0 - member NO, tag ADMITTED (dead =4 is not a refusal)', r['status'] == 'ADMITTED' and mem(r, 'K_B (i)') is False)
r = read(c4_many(3, 3, 3, 2, 0))
ok &= check('K_B (i) rx 2 with no R/X line: exact reconciliation NO', adm(r, 'RC3 ') is False)
r = read(c4_many(40, 60, 60, 2, 0))
ok &= check('K_B (i) 2 by the counter with no R/X line when exhausted: (i) YES, (ii) NO', mem(r, 'K_B (i)') is True and mem(r, 'K_B (ii)') is False)
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_race', 2)))
ok &= check('c4 race - reference, no STOP', r['stop'] == [] and r['status'] == 'ADMITTED')
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_bad_noreg', 3)))
ok &= check('c4 noreg - no STOP', r['stop'] == [])

# --- v members ---


def chkb(t, total):
    n = len(t['frames'])
    q, rem = divmod(total, n)
    for i, f in enumerate(t['frames']):
        f['rts_chk_b'] = f['rts_pb'] = q + (1 if i < rem else 0)


ok &= check('(C1) window chk_b 1 000 000 YES', mem(read(mod(cv, lambda t: chkb(t, 1000000))), '(C1)') is True)
ok &= check('(C1) window chk_b 999 999 NO', mem(read(mod(cv, lambda t: chkb(t, 999999))), '(C1)') is False)
ok &= check('(C1) chk_b before the entry does not count', mem(read(mod(cv, lambda t: (chkb(t, 999999), t['pre'].__setitem__(0, dict(t['pre'][0], rts_chk_b=5, rts_pb=5, rts_chk=5, rts_pa=5))))), '(C1)') is False)
r = read(mod(cv, lambda t: t['frames'][20].update(rts_bad=1)))
ok &= check('(V) rts_bad 1 - NO and STOP outcome', mem(r, '(V)') is False and any('(V) != 0' in z for z in r['stop']))
r = read(mod(cv, lambda t: t['pre'].__setitem__(0, dict(t['pre'][0], rts_bad=1))))
ok &= check('(V) rts_bad 1 before the entry (process) - NO and STOP', mem(r, '(V)') is False and any('(V) != 0' in z for z in r['stop']))
r = read(mod(cv, lambda t: (t['frames'][20].update(rts_bad=1), t['run']['attempts'][0].__setitem__('launch_sha256', FS10))))
ok &= check('(V) != 0 without (D7) - no STOP of (V)', not any('(V) != 0' in z for z in r['stop']))
r = read(mod(cv, lambda t: (t['frames'][20].update(rts_bad=1), t.__setitem__('frames', t['frames'][:2000]))))
ok &= check('(V) != 0 with (D5) failed - STOP anyway (RC3 of item 643 (g))', any('(V) != 0' in z for z in r['stop']))
r = read(mod(cv, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x010 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=2')))
ok &= check('(V) a RtSkipVerify line with rts_bad 0 - NO and STOP', mem(r, '(V)') is False and any('(V) != 0' in z for z in r['stop']))
r = read(mod(cv, lambda t: t['frames'][20].__setitem__('rts_race', 1)))
ok &= check('v race 1 - NO and STOP', mem(r, 'race') is False and any('rts_race' in z for z in r['stop']))
r = read(mod(cv, lambda t: t.__setitem__('bda', [100] * len(t['bda']))))
ok &= check('(O) NEW - NO', mem(r, '(O)') is False and r['bda']['mode'] == 'NEW')
r = read(mod(cv, lambda t: t.__setitem__('bda', [100] * 180 + [700] * (len(t['bda']) - 180))))
ok &= check('(O) the two first blocks are skipped - OLD', r['bda']['mode'] == 'OLD' and mem(r, '(O)') is True)
r = read(mod(cv, lambda t: t.__setitem__('bda', [100] * 270 + [700] * (len(t['bda']) - 270))))
ok &= check('(O) one read block NEW of 33 - still OLD (>= 90 %%) %s' % r['bda'], r['bda']['mode'] == 'OLD')
r = read(mod(cv, lambda t: t.__setitem__('bda', [100] * (180 + 4 * 90) + [700] * (len(t['bda']) - 180 - 4 * 90))))
ok &= check('(O) four read blocks NEW of 33 - MIXED %s' % r['bda'], r['bda']['mode'] == 'MIXED' and mem(r, '(O)') is False)
r = read(mod(cv, lambda t: t.__setitem__('bda', [700] * 180 + [400] * 90 + [700] * (len(t['bda']) - 270))))
ok &= check('(O) a read block of 400 in an OLD entry - its chk_b not counted (%s)' % r['bda'], r['bda']['mode'] == 'OLD'
            and r['bda']['chkb_old'] == (3100 - 270) * 400)
r = read(mod(cv, lambda t: t.__setitem__('bda', [599] * len(t['bda']))))
ok &= check('(O) blocks of 599 - not OLD', r['bda']['mode'] != 'OLD')
r = read(mod(cv, lambda t: t.__setitem__('bda', [600] * len(t['bda']))))
ok &= check('(O) blocks of 600 - OLD', r['bda']['mode'] == 'OLD')
r = read(mod(cv, lambda t: [f.update(rts_chk_b=300, rts_pb=300) for f in t['frames']]))
ok &= check('(O) OLD but chk_b in OLD blocks 876 000 < 10^6 - NO', r['bda']['mode'] == 'OLD' and mem(r, '(O)') is False)
r = read(mod(cv, lambda t: t.__setitem__('frames', t['frames'][:300])))
ok &= check('(O) fewer than 3 read blocks - SHORT', r['bda']['mode'] == 'SHORT')
r = read(mod(cv, lambda t: t.__setitem__('bda', [600] * 180 + [100] * (len(t['bda']) - 180))))
ok &= check('(O) chk_b of skipped blocks not counted as OLD (NEW entry, chkb_old 0)', r['bda']['chkb_old'] == 0)

# --- FixB42, kappa, references ---
b42 = rv['b42']
ok &= check('FixB42 window increments: 480x270 hit 4 applied 3 drawn 4, 1920x1080 3/0/1 %s' % b42['per_extent'],
            b42['per_extent'] == {'480x270': dict(hit=4, applied=3, drawn=4), '1920x1080': dict(hit=3, applied=0, drawn=1)}
            and b42['inc'] == dict(hit=7, applied=3, drawn=5) and b42['lines'] == 3)
r = read(mod(cv, lambda t: t['mid'].append('FixB42: mode=1 hit=2 applied=1 drawn=7 rearm=0 hit_all=2 last_frame=1 extent=480x270 cmask=0x1 clear=0/0')))
ok &= check('FixB42 a lower later line does not lower the max', r['b42']['per_extent']['480x270'] == dict(hit=4, applied=3, drawn=4))
ok &= check('window rts_lost reference', read(mod(cv, lambda t: t['frames'][9].__setitem__('rts_lost', 3)))['win']['rts_lost'] == 3)
kp = rv['kappa']
ok &= check('kappa: share 400/500 = 0.8 over Sky Garden 0.8802 / OLD 0.8798 %s' % kp, kp['share_v2'] == 0.8 and kp['by']['ALL']['kappa'] == round(0.8 / 0.8802, 4)
            and kp['by']['OLD']['kappa'] == round(0.8 / 0.8798, 4) and kp['by']['ALL']['inside'] is True)
r = read(mod(cv, lambda t: [f.update(rts_n=1000) for f in t['frames']]))
ok &= check('kappa 0.4 / 0.88 outside [0.80; 1.25] - a row, not a member, tag ADMITTED', r['kappa']['by']['ALL']['inside'] is False and r['status'] == 'ADMITTED')
r = read(mod(c3, lambda t: t.__setitem__('stdout', '--- Fatal Error --- x')))
ok &= check('death markers - reference row', '--- Fatal Error ---' in r['ref']['death'])
ok &= check('rows out ASCII and STOP none', all(ord(c) < 128 for c in '\n'.join(R.rows_out(rv))) and R.rows_out(rv)[-1] == '  STOP none')

# --- the table and the scene rows ---
rd = os.path.join(TMP, 'runs')
for t, r in (('f30_s1_c3', r3), ('f30_s1_c4', r4), ('f30_s1_v', rv), ('f30_s9_c3', CLEAN[('c3', 's9')][1]), ('f30_s9_v', CLEAN[('v', 's9')][1])):
    os.makedirs(os.path.join(rd, t))
    rr = dict(r, tag=t)
    json.dump(rr, open(os.path.join(rd, t, 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table: 5 tag rows', sum(1 for l in tb if l.startswith('| f30_')) == 5)
srow = [l for l in tb if l.startswith('counted ')]
ok &= check('scene rows: counted 2 (s1, s9), live K_B 1 (s1), OLD with K_B 1 %s' % srow,
            srow == ['counted 2 of 9 (S1 True); with live K_B 1 (S1 or S9 True); OLD with live K_B 1, OLD 2 - rows for F30g by item 643 (d)(9)-(10)'])
s1row = [l for l in tb if l.startswith('s1 ')]
s9row = [l for l in tb if l.startswith('s9 ')]
ok &= check('scene row s9: no c4 - K_B not checked %s' % s9row, s9row and 'K_B(i) not checked' in s9row[0])
ok &= check('scene row s1: counted, FixB42 applied 3 %s' % s1row, s1row and 'counted True OLD True' in s1row[0] and s1row[0].endswith('applied in counted v 3'))

# --- strict cp1250 output, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, c4)
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'f30_s1_c4', '--json', js])
        R.main(['--table', '--runs', rd])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written, ASCII, status ADMITTED', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read())
            and json.load(open(js))['status'] == 'ADMITTED')
for bad in ('fs10_v', 'f30_s1_c5', 'f30_s1_v_r4', 'b12_v'):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %s' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
