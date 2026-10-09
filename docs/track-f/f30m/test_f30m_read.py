"""Fixtures of f30m_read.py (Track F link F30m, HPP-723; ROADMAP s122 item 655 (e), (zh); item 658 (b) RC1-RC4 of F30l, (v)): a clean
synthetic tag of each kind (c5 at s1 and s9 with the keys; cy_v, cy_c3, cy_c4) reads ADMITTED with every member YES; every admission member
(harness, (D1)-(D7) = RC3 of F30l, RC4 of F30f with the 8 bit counters, parse, RC1 / RC2 / RC4 of F30l, 'PB item 6 dropped', the
reconciliation, RC2 (a) / (b) at cy_c4), every member of each kind (K_B'' and the 7 sources, (gamma), (C1), (V), race, (O), (K), (K')) and
each edge (x lines 1499 / 1500, 2999 / 3000, xb_ser 99 / 100, chk_b 999 999 / 10^6, the tolerance 1 of RC2, the name rts_bad_r against
rts_bad_rx, 40 lines of the reconciliation) flips the reading; the STOP rows; the scene rows; strict cp1250 output without
PYTHONIOENCODING; the last line is ALL OK.  Early-exit form of mutlib (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
The reader is loaded in-process from argv[1] (default: f30m_read.py beside this file); the fixture directories live under BASE.
usage: python test_f30m_read.py [<f30m_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f30m_read.py')
BASE = Path(os.path.join(HERE, 'fx_f30m'))   # mutlib gives every job its own copy of this directory
_spec = importlib.util.spec_from_file_location('f30m_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f30m_read.py sha256 %s target f30m_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = 'bba692c6c161afc0cd2bd3245cea574f7fb82e7a4aae4c065826898403107163'   # literals, not the reader's constants (mutants)
FS11 = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'
TBIN = 'C:/kyty/f287/bin/kyty_emulator_bba692c6.exe'
FS11BIN = 'C:/kyty/f287/bin/kyty_emulator_ea51ae80.exe'
TOLDBIN = 'C:/kyty/f287/bin/kyty_emulator_3bc7ada7.exe'
KREF = os.path.join(HERE, 'kref_f30m.tsv')
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
KEYS = ('@1300:a/@45 @1380:w/@45 @1500:w/@96 @1650:h/@975 @2600:f/@1003 @3550:w/@18 @3600:d/@30 @3650:s/@31 @3700:a/@31 '
        '@3750:w/@49 @3800:w/@90 @3900:h/@966 @4850:f/@984 @5800:w/@17 @5830:d/@25 @5860:s/@25 @5890:a/@25 @5920:w/@25')
LEVEL = {'s1': 'underwater_aerial_garden', 's9': 'underwater_aerial_garden', 's6': 'sponge_dirty_bath', 'cy': 'cymbal_party_land'}
B8 = ('rts_bad_r', 'rts_bad_xr', 'rts_bad_xc', 'rts_bad_xe', 'rts_bad_s', 'rts_bad_p', 'rts_bad_m', 'rts_bad_l')
FIELDS = ('rts_n', 'rts_skip', 'rts_pa', 'rts_pb', 'rts_chk', 'rts_chk_b', 'rts_bad', 'rts_bad_noreg', 'rts_bad_b', 'rts_bad_rx',
          'rts_race', 'rts_refuse', 'rts_xthr', 'rts_acqw', 'rts_ovf', 'rts_lost', 'rts_xb_ids', 'rts_xb_live', 'rts_xb_meta', 'rts_xb_ser',
          'rts_xb_bound', 'rts_xb_pass', 'rts_early') + B8
KNOB = {'c5': 5, 'v': 2, 'c3': 3, 'c4': 4}
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
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_RT_SKIP=str(KNOB[kind]))
    if kind == 'v':
        e['KYTY_REC'] = 'C:/x/rec.mp4'
    if scene == 's9':
        e['KYTY_KEYS'] = KEYS
    return e


SEVEN = (('0x010', dict(rts_bad_r=1)), ('0x020', dict(rts_bad_xr=1)), ('0x020', dict(rts_bad_xc=1)), ('0x020', dict(rts_bad_xe=1)),
         ('0x040', dict(rts_bad_s=1)), ('0x080', dict(rts_bad_p=1)), ('0x100', dict(rts_bad_m=1)))


def put_reports(t, reps, mode):
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


def spec(kind, scene):
    knob = KNOB[kind]
    nfr = 3100 if kind == 'v' else 1600
    head = ['LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100', '  version: Fork build arigandores/KytyPS5 6fbdcf6',
            'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
            'RtSkip: mode %d ctx_slots=8 groups=11 rec_bytes=7192' % knob,
            'FixB42: mode=1 hit=2 applied=1 drawn=5 rearm=0 hit_all=2 last_frame=1 extent=480x270 cmask=0x1 clear=00000000/00000000']
    mid = ['FixB42Ext: mode=1 extent=480x270 hit=6 applied=4 drawn=9 rearm=0 frame=50']
    frames = [frame() for _ in range(nfr)]
    t = dict(head=head, mid=mid, frames=frames)
    if kind in ('c5', 'c4'):
        put_reports(t, SEVEN, knob)
    if kind == 'c4':
        frames[100].update(rts_xb_ids=5, rts_xb_bound=1)
    if kind == 'c3':
        mid.append('RtSkipVerify: MISMATCH frame=900 bits=0x401 reg=1 chain=0 colors=5 depth=1 pa=1 pb=1 mode=3')
        frames[100]['rts_bad'] = 1
    if kind == 'v':
        for i in range(200, 300):
            frames[i]['rts_xb_ser'] = 1
    if kind != 'c5':
        frames[50]['rts_xb_pass'] = 3
    bda = [700 if kind == 'v' else 100] * nfr
    tail = ['LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0']
    hold = 300 if kind == 'v' else 150
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=float(hold) + 0.1, started_s=30.0, stable_s=42.0, launch_sha256=TB)
    run = dict(binary_sha256=TB, env=env_of(scene, kind), cmdline=cmd, attempts=[att], guest_args='-lvl ' + LEVEL[scene], hold_s=hold,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()), gates='', schedule='')
    side = dict(installed_before=FS11, installed_after=FS11, installed_sha=TB, level=LEVEL[scene])
    vread = None
    if kind == 'c4':
        vread = dict(tag='f30_cy_v', proc=dict(rts_xb_ids=150, rts_xb_live=99, rts_xb_bound=100, rts_xb_pass=0))
    return dict(head=head, pre=[frame(rts_n=7, rts_pa=0, rts_chk=0, rts_pb=0, rts_chk_b=0) for _ in range(3)], entry=True, mid=t['mid'],
                frames=frames, bda=bda, tail=tail, run=run, side=side, vread=vread, scene=scene, kind=kind, idx=(3200 if kind == 'v' else 0),
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


def stopped(r, text):
    return any(text in z for z in r['stop'])


# --- clean tags ---
CLEAN = {}
for kind, scene in (('c5', 's1'), ('c5', 's9'), ('v', 'cy'), ('c3', 'cy'), ('c4', 'cy'), ('c5', 's6')):
    s = spec(kind, scene)
    r = read(s)
    CLEAN[(kind, scene)] = (s, r)
    ok &= check('%s %s clean ADMITTED %s' % (kind, scene, [a for a, x in r['admission'] if not x][:3]), r['status'] == 'ADMITTED')
    ok &= check('%s %s clean members all YES %s' % (kind, scene, [a for a, x in (r['members'] or []) if not x]),
                r['members'] is not None and all(x for a, x in r['members']))
    ok &= check('%s %s clean no STOP %s' % (kind, scene, r['stop']), r['stop'] == [])
c5, r5 = CLEAN[('c5', 's1')]
cv, rv = CLEAN[('v', 'cy')]
c3, r3 = CLEAN[('c3', 'cy')]
c4, r4 = CLEAN[('c4', 'cy')]
ok &= check('members count c5 8, c4 8, c3 3, v 5', len(r5['members']) == 8 and len(r4['members']) == 8 and len(r3['members']) == 3
            and len(rv['members']) == 5)
ok &= check("clean c5 K_B'' sum 7, live R X:xr X:xc X:xe S P M %s" % r5['kb2'], r5['kb2']['sum7'] == 7
            and r5['kb2']['live'] == ['R', 'X:xr', 'X:xc', 'X:xe', 'S', 'P', 'M'] and r5['kb2']['l_ref'] == 0)
ok &= check('clean c5 reconciliation exact %s' % r5['rec'], r5['rec']['exact'] is True and r5['rec']['ok'] is True and r5['rec']['n'] == 7
            and r5['rec']['lines'] == dict(rx=4, b=7, x=3, rts_bad_r=1, rts_bad_s=1, rts_bad_p=1, rts_bad_m=1, rts_bad_l=0))
ok &= check('clean c5 b - rx = 3 (member row RC6)', r5['b_minus_rx'] == 3)
ok &= check('clean c4 RC2 (b) rows %s' % r4['rc2b'],
            r4['rc2b'] == ['rts_xb_ids v 150 c4 5 ok', 'rts_xb_live v 99 < 100 - not checked (c4 0)', 'rts_xb_bound v 100 c4 1 ok',
                           'rts_xb_pass v 0 < 100 - not checked (c4 3)'])
ok &= check('clean v: window chk_b 3100 x 400, xb_ser 100, OLD %s' % rv['bda'], rv['win']['rts_chk_b'] == 1240000 and rv['proc']['rts_xb_ser'] == 100
            and rv['bda']['mode'] == 'OLD')
for t in ('f30_s1_c5', 'f30_s9_c5_r2', 'f30_cy_v', 'f30_cy_c3', 'f30_cy_c4_r1'):
    ok &= check('tag form %s' % t, R.TAG_RX.match(t) is not None)
for t in ('f30_s0_c5', 'f30_s1_c3', 'f30_s1_v', 'f30_cy_c5', 'f30_cy_v2', 'f30_in_v', 'f30_s1_c5_r4', 'f30_cy_v_r0', 'b12_v'):
    ok &= check('tag form refused %s' % t, R.TAG_RX.match(t) is None)
ok &= check('parts of f30_s9_c5_r2 and f30_cy_c4', R.parts('f30_s9_c5_r2') == ('s9', 'c5', '_r2') and R.parts('f30_cy_c4') == ('cy', 'c4', ''))

# --- harness admission ---
for key, val in (('installed_before', TB), ('installed_after', TB), ('installed_before', 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'),
                 ('installed_sha', FS11), ('installed_sha', '3bc7ada7980a89fee30b17780f8dfbee0b3921332d81f1f63984d6252a811347'), ('level', 'pot')):
    ok &= check('admission side %s=%s' % (key, val[:8]), read(mod(c5, lambda t: t['side'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
for key, val in (('binary_sha256', FS11), ('guest_args', '-lvl pot'), ('hold_s', 151), ('gates', 'rtskip=1'), ('schedule', 'x')):
    ok &= check('admission run %s' % key, read(mod(c5, lambda t: t['run'].__setitem__(key, val)))['status'] == 'NOT_ADMITTED')
ok &= check('admission prereg', read(mod(c5, lambda t: t['run']['prereg'].__setitem__('sha256', 'x')))['status'] == 'NOT_ADMITTED')
for k, v in (('KYTY_RT_SKIP', '2'), ('KYTY_RT_SKIP', '4'), ('KYTY_FIX_B42', '0'), ('KYTY_GAME_PATCH', 'p'), ('KYTY_GPU_CHECKPOINTS', '1'),
             ('KYTY_REC', 'x'), ('KYTY_KEYS', KEYS)):
    ok &= check('admission env %s=%s' % (k, v[:8]), read(mod(c5, lambda t: t['run']['env'].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
for k0 in ('KYTY_RT_SKIP', 'KYTY_GPU_CLOCK_PIN', 'KYTY_FRAME_TRACE'):
    ok &= check('admission env missing %s' % k0, read(mod(c5, lambda t: t['run']['env'].pop(k0)))['status'] == 'NOT_ADMITTED')
ok &= check('admission s9 without KYTY_KEYS', read(mod(CLEAN[('c5', 's9')][0], lambda t: t['run']['env'].pop('KYTY_KEYS')))['status'] == 'NOT_ADMITTED')
ok &= check('admission cy_v without KYTY_REC', read(mod(cv, lambda t: t['run']['env'].pop('KYTY_REC')))['status'] == 'NOT_ADMITTED')
ok &= check('admission cy_c3 with KYTY_RT_SKIP=5', read(mod(c3, lambda t: t['run']['env'].__setitem__('KYTY_RT_SKIP', '5')))['status'] == 'NOT_ADMITTED')
for extra in (['--vulkan-validation', 'true'], ['--shader-validation', 'true'], ['--rd'], ['--graphics-debug-dump', 'true']):
    ok &= check('admission cmdline %s' % extra, read(mod(c5, lambda t: t['run'].__setitem__('cmdline', t['run']['cmdline'] + extra)))['status'] == 'NOT_ADMITTED')
for k, v in (('outcome', 'timeout'), ('hold_exit', 3), ('started_s', None)):
    ok &= check('admission attempt %s=%s' % (k, v), read(mod(c5, lambda t: t['run']['attempts'][0].__setitem__(k, v)))['status'] == 'NOT_ADMITTED')
ok &= check('window: c5 hold_s 149.9 from the entry - NO', read(mod(c5, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=149.9)))['status'] == 'NOT_ADMITTED')
ok &= check('window: c5 hold_s 150.0 from the entry - YES', read(mod(c5, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=150.0)))['status'] == 'ADMITTED')
ok &= check('window: cy_v hold_s 299.9 - NO', read(mod(cv, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=299.9)))['status'] == 'NOT_ADMITTED')
ok &= check('window: cy_v hold_s 300.0 - YES', read(mod(cv, lambda t: t['run']['attempts'][0].update(stable_s=30.0, hold_s=300.0)))['status'] == 'ADMITTED')
ok &= check('admission no entry line', read(mod(c5, lambda t: t.__setitem__('entry', False)))['status'] == 'NOT_ADMITTED')
ok &= check('admission cy entry line of another level', read(mod(cv, lambda t: t['side'].__setitem__('level', 'enemy_final')))['status'] == 'NOT_ADMITTED')
for ln in ('Window 1 minimized', 'Recovering Vulkan swapchain 1'):
    ok &= check('window event %s - INTERFERENCE' % ln, read(mod(c5, lambda t: t['mid'].append(ln)))['status'] == 'INTERFERENCE')
ok &= check('no summary line - INTERFERENCE', read(mod(c5, lambda t: t.__setitem__('tail', [])))['status'] == 'INTERFERENCE')
ok &= check('two summary lines - NOT_ADMITTED', read(mod(c5, lambda t: t.__setitem__('tail', t['tail'] * 2)))['status'] == 'NOT_ADMITTED')
for ln in ('GamePatch: x', 'DiagB32 x', 'TestLogStall: x'):
    ok &= check('admission line %s' % ln, read(mod(c5, lambda t: t['mid'].append(ln)))['status'] == 'NOT_ADMITTED')
ok &= check('admission signature', read(mod(c5, lambda t: t['head'].__setitem__(2, 'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40))))['status'] == 'NOT_ADMITTED')
ok &= check('admission catalog', read(mod(c5, lambda t: t['head'].__setitem__(3, 'Shader translation cache: C:/e/variant_fixb26_fixb1b_fixf10')))['status'] == 'NOT_ADMITTED')
ok &= check('log absent - NOT_ADMITTED', R.read_tag('f30_s1_c5', dict(R.paths('f30_s1_c5', os.path.join(TMP, 'none')), log='C:/no/such/log.txt'))['status'] == 'NOT_ADMITTED')

# --- (D1)-(D7) ---
ok &= check('(D1) two mode lines', adm(read(mod(c5, lambda t: t['head'].append('RtSkip: mode 5 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) mode 2 at c5', adm(read(mod(c5, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 2 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) mode 4 at cy_c3', adm(read(mod(c3, lambda t: t['head'].__setitem__(4, 'RtSkip: mode 4 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
ok &= check('(D1) no mode line', adm(read(mod(c5, lambda t: t['head'].pop(4))), '(D1)') is False)
ok &= check('(D1) mode 5 once plus a mode 2 line - NO', adm(read(mod(c5, lambda t: t['head'].append('RtSkip: mode 2 ctx_slots=8 groups=11 rec_bytes=7192'))), '(D1)') is False)
r = read(mod(c5, lambda t: t['mid'].append('RtSkip: refused reason=rk3cen')))
ok &= check('(D2) refused line - NO and STOP', adm(r, '(D2)') is False and stopped(r, 'refused'))
ok &= check('(D3) gate rtskip=5 fine', adm(read(mod(c5, lambda t: t['mid'].append('Gate: rtskip=5 frame=5'))), '(D3)') is True)
ok &= check('(D3) gate rtskip=1', adm(read(mod(c5, lambda t: t['mid'].append('Gate: rtskip=1 frame=5'))), '(D3)') is False)
for k in ('rts_xthr', 'rts_acqw'):
    r = read(mod(c5, lambda t: t['pre'].__setitem__(0, dict(t['pre'][0], **{k: 1}))))
    ok &= check('(D4) %s before the entry - NO and STOP' % k, adm(r, '(D4)') is False and stopped(r, '(D4)'))
ok &= check('(D5) c5 1500 x lines YES', adm(read(mod(c5, lambda t: t.__setitem__('frames', t['frames'][:1500]))), '(D5)') is True)
ok &= check('(D5) c5 1499 x lines NO', adm(read(mod(c5, lambda t: t.__setitem__('frames', t['frames'][:1499]))), '(D5)') is False)
ok &= check('(D5) cy_c4 1499 NO', adm(read(mod(c4, lambda t: t.__setitem__('frames', t['frames'][:1499]))), '(D5)') is False)
ok &= check('(D5) cy_c3 1500 YES', adm(read(mod(c3, lambda t: t.__setitem__('frames', t['frames'][:1500]))), '(D5)') is True)
ok &= check('(D5) cy_v 3000 YES', adm(read(mod(cv, lambda t: t.__setitem__('frames', t['frames'][:3000]))), '(D5)') is True)
ok &= check('(D5) cy_v 2999 NO', adm(read(mod(cv, lambda t: t.__setitem__('frames', t['frames'][:2999]))), '(D5)') is False)
ok &= check('(D5) share: 3000 x, 3158 draw NO', adm(read(mod(cv, lambda t: (t.__setitem__('frames', t['frames'][:3000]), t.__setitem__('extra_draw', 158)))), '(D5)') is False)
ok &= check('(D5) share: 3000 x, 3157 draw YES', adm(read(mod(cv, lambda t: (t.__setitem__('frames', t['frames'][:3000]), t.__setitem__('extra_draw', 157)))), '(D5)') is True)
ok &= check('(D6) rts_ovf in the window', adm(read(mod(c5, lambda t: t['frames'][5].__setitem__('rts_ovf', 1))), '(D6)') is False)
r = read(mod(c5, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', FS11)))
ok &= check('(D7) launch_sha256 FS11 - NOT_ADMITTED and STOP', adm(r, '(D7)') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, '(D7)'))
ok &= check('(D7) no launch_sha256', adm(read(mod(c5, lambda t: t['run']['attempts'][0].pop('launch_sha256'))), '(D7)') is False)
ok &= check('(D7) fork line of T a1d1d86', adm(read(mod(c5, lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 a1d1d86'))), '(D7)') is False)
ok &= check('(D7) fork line 6fbdcf6-dirty', adm(read(mod(c5, lambda t: t['head'].__setitem__(1, '  version: Fork build arigandores/KytyPS5 6fbdcf6-dirty'))), '(D7)') is False)
ok &= check('(D7) two fork lines', adm(read(mod(c5, lambda t: t['head'].append('  version: Fork build arigandores/KytyPS5 6fbdcf6'))), '(D7)') is False)
ok &= check('(D7) no fork line', adm(read(mod(c5, lambda t: t['head'].pop(1))), '(D7)') is False)
ok &= check('(D7) binary_sha256 != launch_sha256', adm(read(mod(c5, lambda t: t['run']['attempts'][0].__setitem__('launch_sha256', 'f' * 64))), '(D7)') is False)
ok &= check('(D7) binary_sha256 FS11 with launch_sha256 T2 - the (D7) row NO', adm(read(mod(c5, lambda t: t['run'].__setitem__('binary_sha256', FS11))), '(D7)') is False)
ok &= check('(D7) pinned copy FS11',adm(read(mod(c5, lambda t: t.__setitem__('binpath', FS11BIN))), '(D7)') is False)
ok &= check('(D7) pinned copy T (old binary)', adm(read(mod(c5, lambda t: t.__setitem__('binpath', TOLDBIN))), '(D7)') is False)
ok &= check('(D7) a version string of T2 in the log - YES', adm(read(mod(c5, lambda t: t['mid'].append('x KytyPS5-2026-09-15-6a2987a-1907-g6fbdcf67 y'))), '(D7)') is True)
ok &= check('(D7) a version string of T in the log - NO (RC3 of F30l)', adm(read(mod(c5, lambda t: t['mid'].append('x KytyPS5-2026-09-15-6a2987a-1906-ga1d1d863'))), '(D7)') is False)
ok &= check('(D7) a version string of FS11 in the log - NO', adm(read(mod(c5, lambda t: t['mid'].append('KytyPS5-2026-09-15-6a2987a-1910-gee9632be'))), '(D7)') is False)
r = read(mod(c5, lambda t: (t['mid'].append('Window 1 minimized'), t['run']['attempts'][0].__setitem__('launch_sha256', FS11))))
ok &= check('(D7) failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')
S9, R9 = CLEAN[('c5', 's9')]
ok &= check('S9 last n 1650 - YES', adm(read(mod(S9, lambda t: t.__setitem__('n0', 48))), 'S9 ') is True)
ok &= check('S9 last n 1649 - NOT_ADMITTED', read(mod(S9, lambda t: t.__setitem__('n0', 47)))['status'] == 'NOT_ADMITTED')
ok &= check('S9 member absent at s1 and cy', adm(r5, 'S9 ') is None and adm(rv, 'S9 ') is None)

# --- RC4 of F30f / RC2 of F30l: fields ---
for k in B8 + ('rts_bad_rx', 'rts_bad_b', 'rts_chk_b', 'rts_xb_pass'):
    r = read(mod(c5, lambda t: t.__setitem__('drop', {k})))
    ok &= check('missing %s in one window line - NOT_ADMITTED and not 0' % k, r['status'] == 'NOT_ADMITTED' and adm(r, 'RC4 (F30f)') is False)
r = read(mod(c5, lambda t: t['pre'].__setitem__(0, dict((a, b) for a, b in t['pre'][0].items() if a != 'rts_bad_l'))))
ok &= check('missing rts_bad_l before the entry - NOT_ADMITTED', adm(r, 'RC4 (F30f)') is False)
ok &= check('a field outside REQ may be absent', read(mod(c5, lambda t: t.__setitem__('drop', {'rts_early'})))['status'] == 'ADMITTED')
CNT[0] += 1
dd = os.path.join(TMP, 'tok')
write(dd, c5)
lp = os.path.join(dd, 'log.txt')
data = open(lp, 'rb').read().replace(b' rts_bad_r=0 ', b' rts_bad_rq=0 ', 1)
open(lp, 'wb').write(data)
r = R.read_tag('f30_s1_c5', R.paths('f30_s1_c5', dd))
ok &= check('name taken whole: rts_bad_rq is not rts_bad_r - missing field', adm(r, 'RC4 (F30f)') is False)
x = R.scan(lp, LEVEL['s1'])
ok &= check('name taken whole: rts_bad_rx sum not mixed into rts_bad_r (rx 4, r 1)', x['proc']['rts_bad_rx'] == 4 and x['proc']['rts_bad_r'] == 1)
shutil.rmtree(dd, ignore_errors=True)

# --- parse of item 651 (b) ---
r = read(mod(c5, lambda t: (t['frames'][10].__setitem__('rts_chk', 421), t['frames'][11].__setitem__('rts_chk', 419))))
ok &= check('parse: tear of one event - YES', adm(r, 'parse') is True)
r = read(mod(c5, lambda t: (t['frames'][10].__setitem__('rts_chk', 422), t['frames'][11].__setitem__('rts_chk', 418))))
ok &= check('parse: prefix 2 - NO, NOT_ADMITTED and STOP', adm(r, 'parse') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'item 651'))
r = read(mod(c5, lambda t: t['frames'][10].__setitem__('rts_pb', 401)))
ok &= check('parse: pb sum != chk_b sum - NO and STOP', adm(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_rx=8)))
ok &= check('parse: rx 8 > b 7 - NO and STOP', adm(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c5, lambda t: t['mid'].append('RtSkipVerify: something else')))
ok &= check('parse: unparsable RtSkipVerify - NO', adm(r, 'parse') is False)
r = read(mod(c5, lambda t: t['frames'][10].__setitem__('rts_chk', 421)))
ok &= check('parse: chk sum 1 over pa sum (prefix within 1) - NO and STOP', adm(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c3, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x401 reg=1 chain=0 colors=1 depth=0 pa=1 pb=0 mode=3')))
ok &= check('parse: 2 lines > bad 1 - NO', adm(r, 'parse') is False)
r = read(mod(c5, lambda t: (t['frames'][100].update(rts_bad_b=1), t['frames'][101].update(rts_bad_b=6))))
ok &= check('parse: rx 4 three events ahead of b 1 at a line, sums equal - NO and STOP', adm(r, 'parse') is False and stopped(r, 'item 651'))
r = read(mod(c5, lambda t: put_reports(t, [('0x040', dict(rts_bad_s=1))] * 41, 5)))
ok &= check('parse: 41 lines = bad 41 > 40 lines - NO; reconciliation not exact', adm(r, 'parse') is False and r['rec']['exact'] is False)

# --- RC1 of F30l ---
for kd, s in (('c5', c5), ('v', cv), ('c3', c3), ('c4', c4)):
    r = read(mod(s, lambda t: t['frames'][3].__setitem__('rts_skip', 1)))
    ok &= check('RC1 %s rts_skip 1 - NOT_ADMITTED and STOP' % kd, adm(r, 'RC1 (F30l)') is False and r['status'] == 'NOT_ADMITTED'
                and stopped(r, 'RC1 (F30l)'))
r = read(mod(c5, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames']]))
ok &= check('RC1 rts_chk_b = rts_pb = 0 - NO', adm(r, 'RC1 (F30l)') is False)
r = read(mod(c5, lambda t: [f.update(rts_pb=0, rts_chk_b=0) for f in t['frames'][1:]]))
ok &= check('RC1 rts_chk_b = rts_pb = 400 >= 1 - YES', adm(r, 'RC1 (F30l)') is True)
r = read(mod(c5, lambda t: t['frames'][10].update(rts_pb=401)))
ok &= check('RC1 rts_chk_b != rts_pb - NO', adm(r, 'RC1 (F30l)') is False)
r = read(mod(c5, lambda t: [f.update(rts_chk=300, rts_pa=300) for f in t['frames']]))
ok &= check('RC1 rts_chk 300 < rts_chk_b 400 - NO', adm(r, 'RC1 (F30l)') is False)

# --- RC2 of F30l ---
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_s=8)))
ok &= check('RC2 s 8 > b 7 - NO and STOP', adm(r, 'RC2 (F30l)') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'RC2 (F30l)'))
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_r=5)))
ok &= check('RC2 r 5 > rx 4 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xc=5)))
ok &= check('RC2 xc 5 > rx 4 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xe=5)))
ok &= check('RC2 xe 5 > rx 4 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xr=5)))
ok &= check('RC2 xr 5 > rx 4 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_l=8)))
ok &= check('RC2 l 8 > b 7 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad=9, rts_bad_noreg=9, rts_bad_s=8)))
ok &= check('RC2 s 8 > b 7 but <= bad 9 - NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_b=8)))
ok &= check('RC2 b 8 > bad 7 - the RC2 row NO', adm(r, 'RC2 (F30l)') is False)
r = read(mod(c5, lambda t: (t['frames'][100].update(rts_bad_s=8), t['mid'].append('Window 1 minimized'))))
ok &= check('RC2 failure wins over an interference - NOT_ADMITTED', r['status'] == 'NOT_ADMITTED')


def rc2_case(rx, r_, xr, xc, xe, b, s8_extra):
    def fn(t):
        f = t['frames'][100]
        f.update(rts_bad=b, rts_bad_noreg=b, rts_bad_b=b, rts_bad_rx=rx, rts_bad_r=r_, rts_bad_xr=xr, rts_bad_xc=xc, rts_bad_xe=xe,
                 rts_bad_s=s8_extra, rts_bad_p=0, rts_bad_m=0, rts_bad_l=0)
        t['mid'] = [z for z in t['mid'] if not z.startswith('RtSkipVerify')]
    return mod(c5, fn)


ok &= check('RC2 tolerance: rx 5 = r+xr+xc+xe 4 + 1 - YES', adm(read(rc2_case(5, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is True)
ok &= check('RC2 tolerance: rx 6 > 4 + 1 - NO', adm(read(rc2_case(6, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is False)
ok &= check('RC2 tolerance: b 9 = sum8 8 + 1 - YES', adm(read(rc2_case(4, 1, 1, 1, 1, 9, 4)), 'RC2 (F30l)') is True)
ok &= check('RC2 tolerance: b 10 > sum8 8 + 1 - NO', adm(read(rc2_case(4, 1, 1, 1, 1, 10, 4)), 'RC2 (F30l)') is False)
ok &= check('RC2 per line - reference row', 'lines out of RC2 0' in [a for a, b in r5['admission'] if a.startswith('RC2 (F30l)')][0])

# --- RC4 of F30l, PB item 6 ---
for kd, s in (('c5', c5), ('c4', c4)):
    r = read(mod(s, lambda t: t['frames'][100].update(rts_bad_noreg=6)))
    ok &= check('RC4 %s noreg 6 != bad 7 - NO and STOP' % kd, adm(r, 'RC4 (F30l)') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'RC4 (F30l)'))
r = read(mod(cv, lambda t: t['frames'][20].update(rts_bad=1)))
ok &= check('RC4 cy_v noreg 0 != bad 1 - NO', adm(r, 'RC4 (F30l)') is False)
ok &= check('RC4 absent at cy_c3 (value 3)', adm(r3, 'RC4 (F30l)') is None)
r = read(mod(c5, lambda t: t['frames'][50].update(rts_xb_pass=1)))
ok &= check('PB item 6 dropped: c5 xb_pass 1 - NO and STOP', adm(r, 'PB item 6') is False and r['status'] == 'NOT_ADMITTED' and stopped(r, 'PB item 6'))
ok &= check('PB item 6 member absent at cy_v (xb_pass 3 fine)', adm(rv, 'PB item 6') is None and rv['status'] == 'ADMITTED')

# --- reconciliation (c5, c4) ---
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_s=2, rts_bad_b=7)))
ok &= check('reconciliation exact: s 2 vs lines 1 - NO and STOP', adm(r, 'reconciliation') is False and stopped(r, 'reconciliation failed'))
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xe=0)))
ok &= check('reconciliation exact: lines with X 3 > xr+xc+xe 2 - NO', adm(r, 'reconciliation') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xr=2, rts_bad_xc=0, rts_bad_xe=1)))
ok &= check('reconciliation exact: xr 2 <= lines X 3 = xr+xc+xe 3 - YES', adm(r, 'reconciliation') is True)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad_xr=0, rts_bad_xc=4, rts_bad_xe=0)))
ok &= check('reconciliation exact: xc 4 > lines X 3 - NO', adm(r, 'reconciliation') is False)
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad=8, rts_bad_noreg=8, rts_bad_b=8, rts_bad_p=2)))
ok &= check('reconciliation exhausted-form (lines 7 < bad 8): p 2 >= 1 YES, no STOP', adm(r, 'reconciliation') is True and r['rec']['exact'] is False
            and not stopped(r, 'reconciliation'))
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad=8, rts_bad_noreg=8, rts_bad_b=8, rts_bad_m=0, rts_bad_p=2)))
ok &= check('reconciliation not exact: m 0 < lines 1 - NO, no STOP', adm(r, 'reconciliation') is False and not stopped(r, 'reconciliation'))
r = read(mod(c5, lambda t: t['frames'][100].update(rts_bad=8, rts_bad_noreg=8, rts_bad_xe=0)))
ok &= check('reconciliation not exact: xr+xc+xe 2 < lines with X 3 - NO', adm(r, 'reconciliation') is False and r['rec']['exact'] is False)
r = read(mod(c5, lambda t: (t['frames'][100].update(rts_bad=8, rts_bad_noreg=8),
                             t['mid'].append('RtSkipVerify: MISMATCH frame=9 bits=0x040 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=2'))))
ok &= check('reconciliation counts only the lines of the knob mode: a mode=2 line ignored - YES, not exact', adm(r, 'reconciliation') is True
            and r['rec']['n'] == 7 and r['rec']['exact'] is False)


def many(nl, bad, s_cnt, s_lines):
    def fn(t):
        put_reports(t, [('0x040', dict(rts_bad_s=1)) if i < s_lines else ('0x200', dict(rts_bad_l=1)) for i in range(nl)], 5)
        f = t['frames'][100]
        extra = bad - nl
        f['rts_bad'] += extra
        f['rts_bad_noreg'] += extra
        f['rts_bad_b'] += extra
        f['rts_bad_l'] += extra
        f['rts_bad_s'] = s_cnt
        f['rts_bad_l'] = f['rts_bad_b'] - s_cnt
    return mod(c5, fn)


r = read(many(40, 40, 5, 5))
ok &= check('reconciliation 40 lines = bad 40: exact, s 5 YES', adm(r, 'reconciliation') is True and r['rec']['exact'] is True)
r = read(many(40, 40, 6, 5))
ok &= check('reconciliation 40 = 40: s 6 vs 5 NO', adm(r, 'reconciliation') is False)
r = read(many(40, 41, 6, 5))
ok &= check('reconciliation exhausted (bad 41): s 6 >= 5 YES', adm(r, 'reconciliation') is True and r['rec']['exact'] is False)
r = read(many(40, 41, 4, 5))
ok &= check('reconciliation exhausted: s 4 < 5 NO, no STOP', adm(r, 'reconciliation') is False and not stopped(r, 'reconciliation'))
ok &= check('reconciliation absent at cy_v and cy_c3', adm(rv, 'reconciliation') is None and adm(r3, 'reconciliation') is None)

# --- K_B'' members (c5, cy_c4) ---
NAMES = ('R', 'X:xr', 'X:xc', 'X:xe', 'S', 'P', 'M')
for i, (bits, cnt) in enumerate(SEVEN):
    for base, tagk in ((c5, 'c5'), (c4, 'c4')):
        r = read(mod(base, lambda t: put_reports(t, [(bits, cnt)], R.KNOB[tagk])))
        ok &= check("K_B'' %s one report %s %s - live, only source %s YES %s" % (tagk, bits, list(cnt), NAMES[i], r['kb2']['live']),
                    r['status'] == 'ADMITTED' and mem(r, "K_B''") is True and r['kb2']['live'] == [NAMES[i]]
                    and mem(r, 'source %s ' % NAMES[i]) is True
                    and sum(1 for a, b in r['members'] if a.startswith('source ') and b) == 1)
r = read(mod(c5, lambda t: put_reports(t, [('0x200', dict(rts_bad_l=1))], 5)))
ok &= check("K_B'' only L - dead, L reference 1", r['status'] == 'ADMITTED' and mem(r, "K_B''") is False and r['kb2']['l_ref'] == 1)
r = read(mod(c5, lambda t: put_reports(t, [('0x001', {}), ('0x004', {})], 5)))
ok &= check("K_B'' only A bits - dead, A-only lines 2 (reference)", mem(r, "K_B''") is False and r['kb2']['a_only_lines'] == 2)
r = read(mod(c5, lambda t: put_reports(t, [], 5)))
ok &= check("K_B'' no report - dead, tag ADMITTED (a dead control is not a refusal)", r['status'] == 'ADMITTED' and mem(r, "K_B''") is False)
r = read(mod(c5, lambda t: t['frames'][100].__setitem__('rts_race', 2)))
ok &= check('c5 race - reference, no STOP', r['stop'] == [] and r['status'] == 'ADMITTED' and r['kb2']['race'] == 2)

# --- cy_c4 RC2 (a) / (b) ---
for k in ('rts_xb_meta', 'rts_xb_ser'):
    r = read(mod(c4, lambda t: t['frames'][9].__setitem__(k, 1)))
    ok &= check('RC2 (a) %s 1 - NOT_ADMITTED' % k, adm(r, 'RC2 (a)') is False and r['status'] == 'NOT_ADMITTED')
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_xb_ids', 0)))
ok &= check('RC2 (b) v ids 150 and c4 0 - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: t['frames'][100].__setitem__('rts_xb_bound', 0)))
ok &= check('RC2 (b) edge v bound 100 and c4 0 - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: (t['vread']['proc'].__setitem__('rts_xb_bound', 99), t['frames'][100].__setitem__('rts_xb_bound', 0))))
ok &= check('RC2 (b) v bound 99 and c4 0 - not checked, YES', adm(r, 'RC2 (b)') is True)
r = read(mod(c4, lambda t: t['vread']['proc'].pop('rts_xb_pass')))
ok &= check('RC2 (b) v sum missing - NO', adm(r, 'RC2 (b)') is False)
r = read(mod(c4, lambda t: t.__setitem__('vread', None)))
ok &= check('RC2 (b) no v read - WAITS_V', r['status'] == 'WAITS_V' and not r['admitted'] and adm(r, 'RC2 (b)') is None)
ok &= check('RC2 (a) absent at c5', adm(r5, 'RC2 (a)') is None)
G0 = R.G
R.G = os.path.join(TMP, 'gmode')
for t, adm_ in (('f30_cy_v', True), ('f30_cy_c3', True)):
    os.makedirs(os.path.join(R.G, 'runs', t))
    json.dump(dict(admitted=adm_), open(os.path.join(R.G, 'runs', t, 'read.json'), 'w'))
pv = R.paths('f30_cy_c4')
ok &= check('paths: cy_c4 reads the read.json of f30_cy_v (%s)' % pv['vread'], (pv['vread'] or '').replace('\\', '/').endswith('runs/f30_cy_v/read.json'))
json.dump(dict(admitted=False), open(os.path.join(R.G, 'runs', 'f30_cy_v', 'read.json'), 'w'))
ok &= check('paths: a not admitted f30_cy_v is not read', R.paths('f30_cy_c4')['vread'] is None)
ok &= check('paths: c5 has no v read', R.paths('f30_s1_c5')['vread'] is None)
R.G = G0

# --- cy_v members ---
r = read(mod(cv, lambda t: t['frames'][250].__setitem__('rts_xb_ser', 0)))
ok &= check('(gamma) xb_ser 99 - NO, tag ADMITTED', mem(r, '(gamma)') is False and r['status'] == 'ADMITTED' and r['stop'] == [])
r = read(mod(cv, lambda t: (t['frames'][250].__setitem__('rts_xb_ser', 0), t['pre'].__setitem__(0, dict(t['pre'][0], rts_xb_ser=1)))))
ok &= check('(gamma) xb_ser 99 in the window + 1 before the entry = process 100 - YES', mem(r, '(gamma)') is True)


def chkb(t, total):
    n = len(t['frames'])
    q, rem = divmod(total, n)
    for i, f in enumerate(t['frames']):
        f['rts_chk_b'] = f['rts_pb'] = q + (1 if i < rem else 0)


ok &= check('(C1) 1 000 000 YES', mem(read(mod(cv, lambda t: chkb(t, 1000000))), '(C1)') is True)
ok &= check('(C1) 999 999 NO', mem(read(mod(cv, lambda t: chkb(t, 999999))), '(C1)') is False)
r = read(mod(cv, lambda t: (chkb(t, 999999), t['pre'].__setitem__(0, dict(t['pre'][0], rts_chk_b=5, rts_pb=5, rts_chk=5, rts_pa=5)))))
ok &= check('(C1) chk_b before the entry does not count - NO; window 999 999, process 1 000 004', mem(r, '(C1)') is False
            and r['win']['rts_chk_b'] == 999999 and r['proc']['rts_chk_b'] == 1000004)
r = read(mod(cv, lambda t: t['frames'][20].update(rts_bad=1, rts_bad_noreg=1)))
ok &= check('(V) rts_bad 1 - NO and STOP outcome 640 (e)(4)', mem(r, '(V)') is False and stopped(r, '(V) != 0'))
r = read(mod(cv, lambda t: t['mid'].append('RtSkipVerify: MISMATCH frame=1 bits=0x010 reg=0 chain=0 colors=1 depth=0 pa=1 pb=1 mode=2')))
ok &= check('(V) a RtSkipVerify line - NO and STOP', mem(r, '(V)') is False and stopped(r, '(V) != 0'))
r = read(mod(cv, lambda t: (t['frames'][20].update(rts_bad=1, rts_bad_noreg=1), t['run']['attempts'][0].__setitem__('launch_sha256', FS11))))
ok &= check('(V) != 0 without (D7) - no STOP of (V)', not stopped(r, '(V) != 0'))
r = read(mod(cv, lambda t: t['frames'][20].__setitem__('rts_race', 1)))
ok &= check('cy_v race 1 - NO and STOP', mem(r, 'race') is False and stopped(r, 'rts_race'))
r = read(mod(cv, lambda t: t.__setitem__('bda', [100] * len(t['bda']))))
ok &= check('(O) NEW - NO', mem(r, '(O)') is False and r['bda']['mode'] == 'NEW')
r = read(mod(cv, lambda t: t.__setitem__('bda', [600] * len(t['bda']))))
ok &= check('(O) blocks of 600 - OLD', r['bda']['mode'] == 'OLD' and mem(r, '(O)') is True)
r = read(mod(cv, lambda t: t.__setitem__('bda', [599] * len(t['bda']))))
ok &= check('(O) blocks of 599 - not OLD', r['bda']['mode'] != 'OLD')

# --- cy_c3 members ---
r = read(mod(c3, lambda t: t['mid'].__setitem__(-1, t['mid'][-1].replace('bits=0x401', 'bits=0x404'))))
ok &= check('(K) no line with bit 0x001 - NO', mem(r, '(K)') is False and r['status'] == 'ADMITTED')
r = read(mod(c3, lambda t: t['frames'][100].__setitem__('rts_bad', 0)))
ok &= check('(K) line but process rts_bad 0 - NO', mem(r, '(K)') is False)
r = read(mod(c3, lambda t: t['frames'][100].__setitem__('rts_bad_noreg', 1)))
ok &= check("(K') noreg 1 - NO and STOP", mem(r, "(K')") is False and stopped(r, "(K')"))
r = read(mod(c3, lambda t: t['pre'].__setitem__(2, dict(t['pre'][2], rts_race=1))))
ok &= check('cy_c3 race before the entry - NO and STOP', mem(r, 'race') is False and stopped(r, 'rts_race'))

# --- references ---
ok &= check('FixB42 window increments 480x270 4/3/4', rv['b42']['per_extent'].get('480x270') == dict(hit=4, applied=3, drawn=4))
r = read(mod(c5, lambda t: t.__setitem__('stdout', '--- Fatal Error --- x')))
ok &= check('death markers - reference row', '--- Fatal Error ---' in r['ref']['death'])
ok &= check('mm_bits counts per bits text', r5['mm_bits'] == {'0x010': 1, '0x020': 3, '0x040': 1, '0x080': 1, '0x100': 1})
ok &= check('rows out ASCII and STOP none', all(ord(c) < 128 for c in '\n'.join(R.rows_out(r5))) and R.rows_out(r5)[-1] == '  STOP none')

# --- the table and the scene rows ---
rd = os.path.join(TMP, 'runs')
dead = read(mod(c5, lambda t: put_reports(t, [], 5)))
only_s = read(mod(CLEAN[('c5', 's9')][0], lambda t: put_reports(t, [('0x040', dict(rts_bad_s=1))], 5)))
only_r4 = read(mod(c4, lambda t: put_reports(t, [('0x010', dict(rts_bad_r=1))], 4)))
for t, r in (('f30_s1_c5', dead), ('f30_s9_c5', only_s), ('f30_s6_c5', CLEAN[('c5', 's6')][1]), ('f30_cy_v', rv), ('f30_cy_c3', r3),
             ('f30_cy_c4', only_r4)):
    os.makedirs(os.path.join(rd, t))
    json.dump(dict(r, tag=t), open(os.path.join(rd, t, 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table: 6 tag rows', sum(1 for l in tb if l.startswith('| f30_')) == 6)
srow = [l for l in tb if l.startswith('scenes with live')]
ok &= check("scene rows: live 3 (s6 s9; cy), S1 or S9 True, sources all 7 %s" % srow,
            srow == ["scenes with live K_B'' 3 (s1..s9: s6 s9; cy True); S1 or S9 among them True; live sources over them "
                     "['M', 'P', 'R', 'S', 'X:xc', 'X:xe', 'X:xr'] - rows for F30n by item 655 (zh)(1)-(3), 658 (v)"])
s1row = [l for l in tb if l.startswith('s1 ')]
ok &= check('scene row s1: dead %s' % s1row, s1row and "K_B'' False" in s1row[0])
cyrow = [l for l in tb if l.startswith('cy ')]
ok &= check('scene row cy: counted True %s' % cyrow, cyrow and cyrow[0].endswith('counted True'))
def cy_table(name, rows):
    rdx = os.path.join(TMP, name)
    for t, r in rows:
        os.makedirs(os.path.join(rdx, t))
        json.dump(dict(r, tag=t), open(os.path.join(rdx, t, 'read.json'), 'w'), default=list)
    return R.table(rdx)


tb2 = cy_table('runs2', [('f30_cy_v', read(mod(cv, lambda t: t['frames'][250].__setitem__('rts_xb_ser', 0)))), ('f30_cy_c3', r3), ('f30_cy_c4', r4)])
cy2 = [l for l in tb2 if l.startswith('cy ')][0]
ok &= check('scene rows: (gamma) dead with c3 / c4 present - cy not counted %s' % cy2, cy2.endswith('counted False') and '(gamma) False' in cy2)
r3d = read(mod(c3, lambda t: t['mid'].__setitem__(-1, t['mid'][-1].replace('bits=0x401', 'bits=0x404'))))
tb3 = cy_table('runs3', [('f30_cy_v', rv), ('f30_cy_c3', r3d), ('f30_cy_c4', r4)])
cy3 = [l for l in tb3 if l.startswith('cy ')][0]
ok &= check('scene rows: cy_c3 (K) dead - cy not counted, its live c4 not in the count %s' % cy3, cy3.endswith('counted False')
            and [l for l in tb3 if l.startswith('scenes with live')][0].startswith("scenes with live K_B'' 0 "))

# --- strict cp1250 output, json, usage ---
d = os.path.join(TMP, 'cp')
write(d, c4)
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'f30_cy_c4', '--json', js])
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
for bad in ('fs10_v', 'f30_s1_c3', 'f30_cy_c5', 'f30_s1_c5_r4'):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %s' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
