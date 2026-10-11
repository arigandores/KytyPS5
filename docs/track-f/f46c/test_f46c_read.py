"""Fixtures of f46c_read.py (Track F link F46c, HPP-800; ROADMAP s122 item 702 (g)(4), (d)(2); item 711 (b)(1), (v) N1): the clean
synthetic tags f26s_0 / f26s_1 / f26s_1b / f26s_t<k> / f26s_c<k> (and _r1) read ADMITTED; every admission member flips the status
(binary T, installed FS13 before / after, prereg, env exact - missing / extra knob, KYTY_FIX_F26 value, the TINT_DCC key as a number:
'0x571006000', '571006000', '0x0000000571006000' equal, other key NOT; FixF26 lines at =0 / =1 / after GuestOut / mode=0; F26Tint lines
at a tint tag - key with 16 digits = env number, other key, other mode, after GuestOut, unparsable; F26Tint line or f26_tint_applied > 0
on a non-tint tag; the 4 keys S1..S4 after the entry - one missing, one only before the entry, fill / size of a stale line different;
site field; unparsable dcc_stale line; 'skipped draw'; identities - f26_kept != dcc_stale_bucket_only at =1, f26_* != 0 at =0,
dcc_stale_apply at =0, f26_tint_* at TINT=0, a second cleared line of one n, cleared lines > mark events, line counts != the last
DiagF5 line, adopt kept_applied; hold 300.0 / 299.9 s; video 2 999 / 3 000; death marker in log / stdout; manifest; window minimized);
the event class of every kind (kept_applied, kept why=decode, deferred, nolayer, levels, range, partial, layers, off, exact_stale) and
NO_APPLY (a mark class without cleared; with cleared - not); exec_present; first_exec; hexnum; strict cp1250 output; the last line is
ALL OK.  Early-exit form (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_f46c_read.py [<f46c_read.py under test>]"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f46c_read.py')
BASE = os.path.join(HERE, 'fx_f46c_read')
_spec = importlib.util.spec_from_file_location('f46c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f46c_read.py sha256 %s target f46c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = '9c1b268ffffebcbf26e3ce33de94fb24c9b555fe89441fafcf40b7197d03ae69'   # literals, not the reader's constants
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1921-g7e8481e5'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
KEYS = [('000000051c630000', '0000000571006000', '00000000', '38000', 0x571006000),
        ('0000000511650000', '0000000570aee000', '20202020', '1e000', 0x570aee000),
        ('00000005168c0000', '0000000570b24000', '00000000', '1e000', 0x570b24000),
        ('0000000510d10000', '000000056d898000', '20202020', '14000', 0x56d898000)]
NAMES = R.F5_NAMES
ok = True


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
        print('FAIL %s' % name)
    return bool(cond)


def f5line(frame, **kv):
    d = dict((n, 0) for n in NAMES)
    d.update(kv)
    return 'DiagF5: frame=%d ' % frame + ' '.join('%s=%d' % (n, d[n]) for n in NAMES)


def ds(n, p, img, dcc, fix, why=None, site='prepare'):
    t = 'DiagF5Ev: dcc_stale site=%s n=%d present=%d gpu=%d image=0x%s dcc=0x%s extent=2432x1368 exact=fresh fix=%s' % (
        site, n, p, p - 10, img, dcc, fix)
    return t + (' why=%s' % why if why else '')


def da(n, p, img, dcc, result, site):
    return 'DiagF5Ev: dcc_stale_apply n=%d present=%d gpu=%d image=0x%s dcc=0x%s result=%s layers=0x00000001 site=%s' % (
        n, p, p - 10, img, dcc, result, site)


def fx(n, p, dcc, img, site):
    return 'DiagF5Ev: f26_first_exec n=%d present=%d dcc=0x%s image=0x%s site=%s' % (n, p, dcc, img, site)


def stale(img, dcc, fill, size):
    return 'TextureCache: stale pending DCC fill ignored image=0x%s dcc=0x%s fill=0x%s size=0x%s seq=1 last=2 cpu=0' % (img, dcc, fill, size)


def spec(tag):
    base = R.base_of(tag)
    on = base != 'f26s_0'
    tint = base.startswith(('f26s_t', 'f26s_c'))
    env = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/x/g', KYTY_SAMPLE_GATE='C:/x/s', KYTY_QUEUE_TRACE='1',
               KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_REC='C:/x/rec.mp4', KYTY_DIAG_F5='1',
               KYTY_DIAG_F5ID='1', KYTY_DCC_TRACE='1', KYTY_FIX_F26='1' if on else '0')
    L = ['LogAsync: mode=1 limit_bytes=1 drain_ms=1 stall_ms=1 flush_ms=1', 'Fork build arigandores/KytyPS5 7e8481e', 'FixF21: mode=1 wait_ms=12000',
         'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG, 'Shader translation cache: C:/e/_ShaderCache/PPSA21564/%s' % VARIANT_DIR,
         'FixB12: mode=1', 'FixB13: mode=1', 'DiagF5Id: mode=1']
    if on:
        L.append('FixF26: mode=1')
    if tint:
        k = int(base[-1])
        mode = '1' if base.startswith('f26s_t') else '2'
        env.update(KYTY_F26_TINT=mode, KYTY_F26_TINT_DCC='0x%x' % KEYS[k - 1][4])
        L.append('F26Tint: mode=%s dcc=0x%016x' % (mode, KEYS[k - 1][4]))
    L.append(f5line(1))
    # before the entry: one event of another key
    kept = kapp = 0
    L.append(stale('0000000512570000', '000000056c058000', '00000000', '6000'))
    if on:
        L.append(ds(1, 10, '0000000512570000', '000000056c058000', 'kept_applied'))
        kept += 1
        kapp += 1
    else:
        L.append(ds(1, 10, '0000000512570000', '000000056c058000', 'off'))
    L += ['GuestOut: Level has started: ', 'GuestOut: Level has started: %s' % SKY, 'FrameTrace: n=10 dt_us=500000 draws=20',
          'FrameTrace: n=11 dt_us=16000 draws=300']
    for i in range(20000):
        L.append('FrameTrace: n=%d dt_us=16700 draws=300' % (12 + i))
        if i == 50:
            for j, (img, dcc, fill, size, num) in enumerate(KEYS):
                n = 2 + j
                if on:
                    if j in (0, 2):
                        L.append(ds(n, 238, img, dcc, 'kept_applied'))
                        kept += 1
                        kapp += 1
                    else:
                        L.append(ds(n, 238, img, dcc, 'kept', 'decode'))
                        kept += 1
                else:
                    L.append(stale(img, dcc, fill, size))
                    L.append(ds(n, 238, img, dcc, 'off'))
        if i == 60:
            if on:
                for j in (1, 3):
                    img, dcc = KEYS[j][0], KEYS[j][1]
                    L.append(da(2 + j, 240, img, dcc, 'cleared', 'mat'))
                    L.append(fx(2 + j, 240, dcc, img, 'mat'))
                    kapp += 1
            else:
                for j in range(4):
                    L.append(fx(2 + j, 300, KEYS[j][1], KEYS[j][0], 'prepare'))
        if i == 1000:
            L.append(f5line(500, f26_kept=kept, f26_kept_applied=kapp, dcc_stale_bucket_only=kept if on else 5,
                            f26_tint_applied=3 if tint else 0))
    L += ['Event: quit', 'LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 '
          'drain_timeouts=0']
    cmd = ['emu', '--vulkan-validation', 'false', '--shader-validation', 'false']
    att = dict(outcome='ok', hold_exit=None, hold_s=330.2, close_rc=0, close_killed=False, close_s=4.1)
    run = dict(binary_sha256=TB, env=env, cmdline=cmd, attempts=[att], guest_args='-lvl ' + SKY, hold_s=330,
               prereg=dict(sha256=hashlib.sha256(SEAL).hexdigest()))
    side = dict(installed_before=FS13, installed_after=FS13, installed_sha=TB, level=SKY, manifest_cmp='manifest cmp EQUAL files 5 listsha x',
                glitch='one-frame glitches: 0', sheet='sheet ok')
    return dict(lines=L, run=run, side=side, idx=3200, stdout='stdout line\n')


def write(d, s):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'wb') as f:
        f.write(('\n'.join(s['lines']) + '\n').encode('ascii'))
    with open(os.path.join(d, 'es.json'), 'w') as f:
        json.dump(s['run'], f)
    for k, v in s['side'].items():
        with open(os.path.join(d, k + '.txt'), 'w') as f:
            f.write(v + '\n')
    with open(os.path.join(d, 'seal.md'), 'wb') as f:
        f.write(SEAL)
    if s['stdout'] is not None:
        with open(os.path.join(d, 'stdout.txt'), 'w') as f:
            f.write(s['stdout'])
    if s['idx']:
        with open(os.path.join(d, 'rec.idx'), 'w') as f:
            f.write(''.join('%d %d 0.0\n' % (i, i + 1) for i in range(s['idx'])))
    with open(os.path.join(d, 'bin.exe'), 'wb') as f:
        f.write(b'xx' + VERSION + b'yy')


shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE, exist_ok=True)
CNT = [0]


def read(s, tag):
    CNT[0] += 1
    d = os.path.join(BASE, 'c%d' % CNT[0])
    write(d, s)
    r = R.read_tag(tag, R.paths(tag, d))
    shutil.rmtree(d, ignore_errors=True)
    return r


def failed_has(r, start):
    return any(a.startswith(start) or a.startswith('702 (g)(4): ' + start) for a in r['failed'])


def lines_map(s, fn):
    s = copy.deepcopy(s)
    s['lines'] = fn(s['lines'])
    return s


def sub(s, old, new):
    return lines_map(s, lambda L: [new if l == old else l for l in L])


def drop(s, pred):
    return lines_map(s, lambda L: [l for l in L if not pred(l)])


def insert_after(s, pred, new):
    def f(L):
        out = []
        done = False
        for l in L:
            out.append(l)
            if not done and pred(l):
                out += new if isinstance(new, list) else [new]
                done = True
        return out
    return lines_map(s, f)


# ---- clean tags
for tag in ('f26s_0', 'f26s_1', 'f26s_1b', 'f26s_t1', 'f26s_c1', 'f26s_t2', 'f26s_c4', 'f26s_0_r1', 'f26s_t3_r1'):
    r = read(spec(tag), tag)
    ok &= check('clean %s ADMITTED (%s)' % (tag, r['failed'][:2]), r['status'] == 'ADMITTED')
r1 = read(spec('f26s_1'), 'f26s_1')
ev = dict((e['k'], e) for e in r1['events'])
ok &= check('S1 kept_applied, exec = event present, not NO_APPLY', ev[1]['cls'] == 'kept_applied' and ev[1]['exec_present'] == 238
            and not ev[1]['no_apply'] and ev[1]['allowed'] and not ev[1]['mark'])
ok &= check('S2 kept why=decode with cleared -> not NO_APPLY, exec 240, first_exec 240 mat', ev[2]['cls'] == 'kept why=decode' and
            not ev[2]['no_apply'] and ev[2]['exec_present'] == 240 and ev[2]['first_exec'] == [dict(present=240, image=KEYS[1][0], site='mat')])
r0 = read(spec('f26s_0'), 'f26s_0')
e0 = dict((e['k'], e) for e in r0['events'])
ok &= check('=0 class off, first_exec 300, stale lines 1', e0[3]['cls'] == 'off' and e0[3]['first_exec'][0]['present'] == 300 and
            e0[3]['stale_lines'] == 1 and not e0[3]['allowed'])
ok &= check('rows: stale lines before / after at =0 = 1 / 4', r0['rows']['stale_lines_before'] == 1 and r0['rows']['stale_lines_after'] == 4)
ok &= check('idx last present 3200 records 3200', r1['idx'] == dict(records=3200, last_present=3200))

# ---- classes (item 711 (b)(1)) and NO_APPLY
S2 = ds(3, 238, KEYS[1][0], KEYS[1][1], 'kept', 'decode')
for fix, why, cls, allowed, mark in (('kept_applied', None, 'kept_applied', True, False), ('kept', 'decode', 'kept why=decode', True, True),
                                     ('kept', 'deferred', 'kept why=deferred', True, True), ('kept', 'nolayer', 'kept why=nolayer', False, False),
                                     ('kept', 'levels', 'kept why=levels', False, False), ('kept', 'range', 'kept why=range', False, False),
                                     ('kept', 'partial', 'kept why=partial', False, False), ('kept', 'layers', 'kept why=layers', False, False),
                                     ('exact_stale', None, 'exact_stale', False, False), ('fallback', None, 'fallback', False, False)):
    s = sub(spec('f26s_1'), S2, ds(3, 238, KEYS[1][0], KEYS[1][1], fix, why, site='adopt' if why == 'deferred' else 'prepare'))
    e = [x for x in read(s, 'f26s_1')['events'] if x['k'] == 2][0]
    ok &= check('class %s -> "%s" allowed %s mark %s' % (fix + (' ' + why if why else ''), cls, allowed, mark),
                e['cls'] == cls and e['allowed'] == allowed and e['mark'] == mark)
s = drop(spec('f26s_1'), lambda l: l.startswith('DiagF5Ev: dcc_stale_apply n=3 '))
e = [x for x in read(s, 'f26s_1')['events'] if x['k'] == 2][0]
ok &= check('decode without cleared -> NO_APPLY, exec None', e['no_apply'] and e['exec_present'] is None)
s = sub(spec('f26s_1'), da(3, 240, KEYS[1][0], KEYS[1][1], 'cleared', 'mat'), da(3, 240, KEYS[1][0], KEYS[1][1], 'declined', 'mat'))
e = [x for x in read(s, 'f26s_1')['events'] if x['k'] == 2][0]
ok &= check('decode with declined only -> NO_APPLY, declined 1', e['no_apply'] and e['declined'] == 1)
s = sub(spec('f26s_1'), da(3, 240, KEYS[1][0], KEYS[1][1], 'cleared', 'mat'), da(3, 240, KEYS[1][0], KEYS[1][1], 'dropped', 'fill'))
e = [x for x in read(s, 'f26s_1')['events'] if x['k'] == 2][0]
ok &= check('decode with dropped only -> NO_APPLY, dropped [fill]', e['no_apply'] and e['dropped'] == ['fill'])

# ---- admission members
def flips(name, s, tag, start):
    r = read(s, tag)
    return check('%s -> NOT_ADMITTED by "%s" (%s)' % (name, start, r['failed'][:2]), r['status'] == 'NOT_ADMITTED' and failed_has(r, start))


def keeps(name, s, tag):
    r = read(s, tag)
    return check('%s -> ADMITTED (%s)' % (name, r['failed'][:2]), r['status'] == 'ADMITTED')


def run_edit(s, fn):
    s = copy.deepcopy(s)
    fn(s)
    return s


ok &= flips('binary F44a', run_edit(spec('f26s_1'), lambda s: s['run'].update(binary_sha256='d760708d' + TB[8:])), 'f26s_1', 'json binary')
ok &= flips('installed during = FS13', run_edit(spec('f26s_1'), lambda s: s['side'].update(installed_sha=FS13)), 'f26s_1', 'installed during')
ok &= flips('installed before FS12', run_edit(spec('f26s_1'), lambda s: s['side'].update(installed_before=FS12)), 'f26s_1', 'installed before')
ok &= flips('installed after FS12', run_edit(spec('f26s_0'), lambda s: s['side'].update(installed_after=FS12)), 'f26s_0', 'installed before')
ok &= flips('prereg other', run_edit(spec('f26s_1'), lambda s: s['run']['prereg'].update(sha256='0' * 64)), 'f26s_1', 'json prereg')
ok &= flips('env missing KYTY_DCC_TRACE', run_edit(spec('f26s_1'), lambda s: s['run']['env'].pop('KYTY_DCC_TRACE')), 'f26s_1', 'env =')
ok &= flips('env missing KYTY_DIAG_F5ID', run_edit(spec('f26s_0'), lambda s: s['run']['env'].pop('KYTY_DIAG_F5ID')), 'f26s_0', 'env =')
ok &= flips('env KYTY_FIX_F26=1 at f26s_0', run_edit(spec('f26s_0'), lambda s: s['run']['env'].update(KYTY_FIX_F26='1')), 'f26s_0', 'env =')
ok &= flips('env KYTY_FIX_F26=true at f26s_1', run_edit(spec('f26s_1'), lambda s: s['run']['env'].update(KYTY_FIX_F26='true')), 'f26s_1', 'env =')
ok &= flips('env extra KYTY_FIX_F29', run_edit(spec('f26s_1'), lambda s: s['run']['env'].update(KYTY_FIX_F29='1')), 'f26s_1', 'env =')
ok &= flips('env extra KYTY_GAME_PATCH', run_edit(spec('f26s_1'), lambda s: s['run']['env'].update(KYTY_GAME_PATCH='p')), 'f26s_1', 'env =')
ok &= flips('env tint on f26s_1', run_edit(spec('f26s_1'), lambda s: s['run']['env'].update(KYTY_F26_TINT='1')), 'f26s_1', 'env =')
ok &= flips('env KYTY_TEST_HIDLOSS', run_edit(spec('f26s_1'), lambda s: s['run']['env'].update(KYTY_TEST_HIDLOSS='1')), 'f26s_1', 'no KYTY_TEST_')
ok &= flips('env t1 key of S2', run_edit(spec('f26s_t1'), lambda s: s['run']['env'].update(KYTY_F26_TINT_DCC='0x570aee000')), 'f26s_t1', 'env =')
ok &= flips('env t1 mode 2', run_edit(spec('f26s_t1'), lambda s: s['run']['env'].update(KYTY_F26_TINT='2')), 'f26s_t1', 'env =')
ok &= flips('env c1 key not hex', run_edit(spec('f26s_c1'), lambda s: s['run']['env'].update(KYTY_F26_TINT_DCC='0xzz')), 'f26s_c1', 'env =')
# N1: the key as a number
ok &= keeps('N1 env key without 0x', run_edit(spec('f26s_t1'), lambda s: s['run']['env'].update(KYTY_F26_TINT_DCC='571006000')), 'f26s_t1')
ok &= keeps('N1 env key 16 digits', run_edit(spec('f26s_t1'), lambda s: s['run']['env'].update(KYTY_F26_TINT_DCC='0x0000000571006000')),
            'f26s_t1')
ok &= keeps('N1 env key upper case', run_edit(spec('f26s_c1'), lambda s: s['run']['env'].update(KYTY_F26_TINT_DCC='0X571006000')), 'f26s_c1')
T1 = 'F26Tint: mode=1 dcc=0x%016x' % KEYS[0][4]
ok &= keeps('N1 line key without leading zeros', sub(spec('f26s_t1'), T1, 'F26Tint: mode=1 dcc=0x571006000'), 'f26s_t1')
ok &= flips('F26Tint other key', sub(spec('f26s_t1'), T1, 'F26Tint: mode=1 dcc=0x%016x' % KEYS[1][4]), 'f26s_t1', "'F26Tint")
ok &= flips('F26Tint other mode', sub(spec('f26s_t1'), T1, 'F26Tint: mode=2 dcc=0x%016x' % KEYS[0][4]), 'f26s_t1', "'F26Tint")
ok &= flips('F26Tint absent at t1', drop(spec('f26s_t1'), lambda l: l.startswith('F26Tint:')), 'f26s_t1', "'F26Tint")
ok &= flips('F26Tint unparsable', sub(spec('f26s_t1'), T1, 'F26Tint: mode=1 key=5'), 'f26s_t1', "'F26Tint")
ok &= flips('F26Tint after GuestOut', insert_after(drop(spec('f26s_t1'), lambda l: l.startswith('F26Tint:')),
                                                    lambda l: l.startswith('GuestOut: Level has started: '), T1), 'f26s_t1', "'F26Tint")
ok &= flips('F26Tint line on f26s_1', insert_after(spec('f26s_1'), lambda l: l.startswith('FixF26:'), T1), 'f26s_1', 'no tint')
ok &= flips('F26Tint line on f26s_0', insert_after(spec('f26s_0'), lambda l: l.startswith('FixB13:'), T1), 'f26s_0', 'no tint')
s = lines_map(spec('f26s_1b'), lambda L: [l.replace('f26_tint_applied=0', 'f26_tint_applied=2') if l.startswith('DiagF5: frame=500') else l
                                          for l in L])
ok &= flips('f26_tint_applied 2 on f26s_1b', s, 'f26s_1b', 'no tint')
ok &= flips('FixF26 line at f26s_0', insert_after(spec('f26s_0'), lambda l: l.startswith('FixB13:'), 'FixF26: mode=1'), 'f26s_0', 'KYTY_FIX_F26=0')
ok &= flips('FixF26 absent at f26s_1', drop(spec('f26s_1'), lambda l: l.startswith('FixF26:')), 'f26s_1', "'FixF26")
ok &= flips('FixF26 mode=0 at f26s_1', sub(spec('f26s_1'), 'FixF26: mode=1', 'FixF26: mode=0'), 'f26s_1', "'FixF26")
ok &= flips('FixF26 after GuestOut', insert_after(drop(spec('f26s_1'), lambda l: l.startswith('FixF26:')),
                                                   lambda l: l.startswith('GuestOut: Level has started: '), 'FixF26: mode=1'), 'f26s_1', "'FixF26")
# the 4 keys
ok &= flips('S3 missing at =1', drop(spec('f26s_1'), lambda l: l.startswith('DiagF5Ev: dcc_stale site=prepare n=4 ')), 'f26s_1', 'the 4 keys')
s = drop(spec('f26s_0'), lambda l: l.startswith('DiagF5Ev: dcc_stale site=prepare n=5 '))
s = insert_after(s, lambda l: l.startswith('DiagF5Ev: dcc_stale site=prepare n=1 '), ds(5, 9, KEYS[3][0], KEYS[3][1], 'off'))
ok &= flips('S4 only before the entry', s, 'f26s_0', 'the 4 keys')
ok &= flips('S1 stale fill other', sub(spec('f26s_0'), stale(*KEYS[0][:4]), stale(KEYS[0][0], KEYS[0][1], '20202020', '38000')), 'f26s_0',
            'the 4 keys')
ok &= flips('S2 stale size other', sub(spec('f26s_0'), stale(*KEYS[1][:4]), stale(KEYS[1][0], KEYS[1][1], '20202020', '1f000')), 'f26s_0',
            'the 4 keys')
r = read(spec('f26s_0'), 'f26s_0')
ok &= check('=0 stale fill/size equal all 4', all(e['stale_fill_size_ok'] and e['stale_lines'] == 1 for e in r['events']))
ok &= flips('unparsable dcc_stale (no site)', insert_after(spec('f26s_1'), lambda l: l.startswith('FrameTrace: n=20 '),
                                                            'DiagF5Ev: dcc_stale n=9 present=1 gpu=1 image=0x1 dcc=0x2'), 'f26s_1', 'field site=')
ok &= flips('skipped draw line', insert_after(spec('f26s_1'), lambda l: l.startswith('FrameTrace: n=30 '),
                                              'AsyncPipelines: skipped draw DrawIndex frame=198 vs=0x1 ps=0x0 pending=2 total_skipped=1'),
            'f26s_1', "0 'skipped draw'")
# identities
F5 = [l for l in spec('f26s_1')['lines'] if l.startswith('DiagF5: frame=500')][0]
ok &= flips('f26_kept != bucket_only at =1', sub(spec('f26s_1'), F5, F5.replace('dcc_stale_bucket_only=5', 'dcc_stale_bucket_only=6')), 'f26s_1',
            'identity: every DiagF5')
F50 = [l for l in spec('f26s_0')['lines'] if l.startswith('DiagF5: frame=500')][0]
ok &= flips('f26_kept 1 at =0', sub(spec('f26s_0'), F50, F50.replace('f26_kept=0', 'f26_kept=1')), 'f26s_0', 'identity: every DiagF5')
ok &= flips('dcc_stale_apply at =0', insert_after(spec('f26s_0'), lambda l: l.startswith('FrameTrace: n=30 '),
                                                   da(2, 30, KEYS[0][0], KEYS[0][1], 'dropped', 'fill')), 'f26s_0', 'identity: KYTY_FIX_F26=0')
ok &= flips('f26_tint_skip at TINT=0', sub(spec('f26s_1'), F5, F5.replace('f26_tint_skip=0', 'f26_tint_skip=1')), 'f26s_1',
            'identity: every DiagF5')
ok &= flips('kept_applied count != last line', sub(spec('f26s_1'), F5, F5.replace('f26_kept_applied=5', 'f26_kept_applied=6')), 'f26s_1',
            'identity: every DiagF5')
s = insert_after(spec('f26s_1'), lambda l: l.startswith('DiagF5Ev: dcc_stale_apply n=3 '), da(3, 241, KEYS[1][0], KEYS[1][1], 'cleared', 'prepare'))
ok &= flips('second cleared line of n 3', s, 'f26s_1', 'identity: cleared lines')
s = sub(spec('f26s_1'), ds(3, 238, KEYS[1][0], KEYS[1][1], 'kept', 'decode'), ds(3, 238, KEYS[1][0], KEYS[1][1], 'kept_applied'))
s = sub(s, F5, F5.replace('f26_kept_applied=5', 'f26_kept_applied=6'))
ok &= flips('cleared lines > mark events', s, 'f26s_1', 'identity: cleared lines')
ok &= flips('line count: an extra kept line before the last DiagF5', insert_after(spec('f26s_1'), lambda l: l.startswith('FrameTrace: n=30 '),
            ds(9, 30, '0000000500000000', '0000000560000000', 'kept', 'nolayer')), 'f26s_1', 'identity: line counts')
r = read(insert_after(spec('f26s_1'), lambda l: l.startswith('DiagF5: frame=500'), ds(9, 900, '0000000500000000', '0000000560000000', 'kept',
                                                                                       'nolayer')), 'f26s_1')
ok &= check('a kept line AFTER the last DiagF5 line - variant member stays (letter row differs)',
            r['status'] == 'ADMITTED' and r['info']['identities_letter']['counts_whole_log']['f26_kept'] == 6)
s = sub(spec('f26s_1'), ds(2, 238, KEYS[0][0], KEYS[0][1], 'kept_applied'), ds(2, 238, KEYS[0][0], KEYS[0][1], 'kept_applied', site='adopt'))
ok &= flips('adopt kept_applied', s, 'f26s_1', 'identity: site=adopt')
r = read(spec('f26s_1'), 'f26s_1')
ok &= check('letter row cleared prepare <= decode (0 <= 2) true', r['info']['identities_letter']['f45a_letter_cleared_prepare_le_decode'])
# form members
def hold_spec(us_total):
    s = spec('f26s_1')
    L = [l for l in s['lines'] if not (l.startswith('FrameTrace: n=') and int(l.split('n=')[1].split()[0]) >= 12)]
    i = [j for j, l in enumerate(L) if l.startswith('FrameTrace: n=11 ')][0]
    n = us_total // 16700
    rest = us_total - n * 16700
    rows = ['FrameTrace: n=%d dt_us=16700 draws=300' % (12 + q) for q in range(n)]
    if rest:
        rows.append('FrameTrace: n=%d dt_us=%d draws=300' % (12 + n, rest))
    s['lines'] = L[:i + 1] + rows + L[i + 1:]
    return s
ok &= keeps('hold 300.0 s', hold_spec(300000000), 'f26s_1')
ok &= flips('hold 299.9 s', hold_spec(299900000), 'f26s_1', 'hold >= 300')
ok &= flips('video 2999', run_edit(spec('f26s_1'), lambda s: s.update(idx=2999)), 'f26s_1', 'video index')
ok &= keeps('video 3000', run_edit(spec('f26s_1'), lambda s: s.update(idx=3000)), 'f26s_1')
ok &= flips('death marker in log', insert_after(spec('f26s_1'), lambda l: l.startswith('FrameTrace: n=40 '), 'GpuHangAbort: x'), 'f26s_1',
            '0 death')
ok &= flips('death marker in stdout', run_edit(spec('f26s_1'), lambda s: s.update(stdout='--- Fatal Error ---\n')), 'f26s_1', '0 death')
ok &= flips('manifest not EQUAL', run_edit(spec('f26s_1'), lambda s: s['side'].update(manifest_cmp='manifest cmp DIFFER 1')), 'f26s_1',
            'caches returned')
ok &= flips('window minimized', insert_after(spec('f26s_1'), lambda l: l.startswith('FrameTrace: n=40 '), 'Window 1 minimized'), 'f26s_1',
            'window events')
ok &= flips('no LogAsync summary (killed)', drop(spec('f26s_1'), lambda l: l.startswith('LogAsync: full_waits=')), 'f26s_1', 'summary line')
ok &= flips('signature other', sub(spec('f26s_1'), 'ShaderSeed: compatibility=x:KytySC3:%s:y' % SIG,
                                   'ShaderSeed: compatibility=x:KytySC3:%s:y' % ('0' * 40)), 'f26s_1', 'translation signature')
# helpers
ok &= check('hexnum', R.hexnum('0x0000000571006000') == R.hexnum('571006000') == 0x571006000 and R.hexnum('0x') is None and
            R.hexnum('xyz') is None and R.hexnum(None) is None)
ok &= check('knobs t3', R.knobs('f26s_t3_r1') == dict(KYTY_DIAG_F5='1', KYTY_DIAG_F5ID='1', KYTY_DCC_TRACE='1', KYTY_GPU_CLOCK_PIN='1',
                                                    KYTY_GPU_MARKERS='0', KYTY_FIX_F26='1', KYTY_F26_TINT='1', KYTY_F26_TINT_DCC='0x570b24000'))
ok &= check('tag rx', all(R.TAG_RX.match(t) for t in ('f26s_0', 'f26s_1b_r2', 'f26s_c4')) and not any(
    R.TAG_RX.match(t) for t in ('f26s_t5', 'f26s_2', 'f26s_0_r4', 'f29_v')))
# strict cp1250 output of the CLI
d = os.path.join(BASE, 'cli')
write(d, spec('f26s_t2'))
env = dict(os.environ)
env.pop('PYTHONIOENCODING', None)
env['PYTHONUTF8'] = '0'
p = subprocess.run([sys.executable, SRC, '--dir', d, '--tag', 'f26s_t2'], capture_output=True, env=env)
out = p.stdout
ok &= check('CLI rc 0 and ASCII output (cp1250 strict) rc %d' % p.returncode, p.returncode == 0 and all(c < 128 for c in out) and
            out.decode('cp1250', 'strict').count('STATUS ADMITTED') == 1)
shutil.rmtree(BASE, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
if ok and N[1] == 0:
    print('ALL OK')
sys.exit(0 if ok and N[1] == 0 else 1)
