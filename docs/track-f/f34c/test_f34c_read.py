"""Fixtures of f34c_read.py (Track F link F34c, HPP-740; ROADMAP s122 item 673 (z)(2), 674 (v)-(g), 676 (b)-(l)): a clean synthetic tag of
each form (w0, vn, vl, wn, wl) reads ADMITTED with all members YES; every admission member, every path member (P1)-(P5), every V member
(V1)-(V5) and every W member flips the reading; one fixture group per member (b)-(k) of item 676 with its edges; strict cp1250 output without
PYTHONIOENCODING; the last line is ALL OK.  Early-exit form of mutlib (ok = True, ok &= ..., sys.exit(0 if ok else 1)).  ASCII only.
usage: python test_f34c_read.py [<f34c_read.py under test>]"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f34c_read.py')
TMP = os.path.join(HERE, 'fx_f34c')
_spec = importlib.util.spec_from_file_location('f34c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_f34c_read.py sha256 %s target f34c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(SRC)))
N = [0, 0]
SEAL = b'seal fixture\n'
TB = 'ea51ae80521e83000679467ce6efadd44b449428629a566e1a4053f8cb5750ce'   # literals, not the reader's constants
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
OFF = 20          # present - n of the synthetic natural start
NI = 2600         # n of the first FrameTrace after the intro line
DELTA = 4540
FORMS = {'b6_w0': 'w0', 'b6_v': 'vn', 'b6_v2': 'vn', 'b6_vl': 'vl', 'b6_w': 'wn', 'b6_wl': 'wl'}


def check(name, cond):
    N[0] += 1
    if not cond:
        N[1] += 1
    print('%-4s %s' % ('ok' if cond else 'FAIL', name))
    return bool(cond)


def spec(form, **kw):
    """The synthetic tag: knobs of the log and of the json."""
    s = dict(form=form, natural=form in ('vn', 'wn'), w=form in ('w0', 'wn', 'wl'), ni=NI if form in ('vn', 'wn') else 310,
             delta=DELTA, end_after_sw=600 if form in ('vn', 'vl') else 300, sub=True, intro=True, title_before=True, presses=(2170, 2460),
             sched=(2170, 2460), ga=None, vke=[], vkw_after=3, vkw_before=2, limit=0, skip=[], held=[], death=None, minimized=False,
             summary=True, extra_env={}, drop_env=None, outcome='ok', hold_exit=None, hold_end='sublevel', prereg_ok=True, manifest='EQUAL',
             idx_from=0, glitch=[], glitch_count=None, sheet='sheets done', inst=TB, sig=SIG, gamepatch=False, vv=None)
    s.update(kw)
    return s


def build_log(s):
    L = []
    a = L.append
    a('LogAsync: mode=1 limit_bytes=268435456 drain_ms=5000 stall_ms=100 flush_ms=100')
    a('FixB13: mode=1')
    a('BufferCache: FixB12: mode=1')
    a('DualSrcBlend: supported=1 enabled=1')
    a('ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:KytySC3:%s:robust' % s['sig'])
    a('Shader translation cache: C:\\kyty\\x\\_ShaderCache\\PPSA21564\\%s' % VARIANT_DIR)
    if s['natural']:
        a('GuestArgs: source=none argc=1')
        a('GuestArgs:   argv[0] = KytyEmu')
        for p in s['sched']:
            a('InputScript: scheduled j at present %d (hold 150 ms)' % p)
    else:
        lv = SKY if s['form'] == 'w0' else 'intro_next'
        a('GuestArgs: source=KYTY_GUEST_ARGS argc=3')
        a('GuestArgs:   argv[0] = KytyEmu')
        a('GuestArgs:   argv[1] = -lvl')
        a('GuestArgs:   argv[2] = %s' % lv)
    if s['gamepatch']:
        a('GamePatch: file x')
    ni = s['ni']
    n_sw = ni + s['delta']
    end = n_sw + s['end_after_sw'] + 5 if s['sub'] else ni + 5000
    end = s.get('end', end)
    vke = dict((n, 1) for n in s['vke'])
    skip = {}
    for n, fr in s['skip']:
        skip.setdefault(n, []).append(fr)
    held = {}
    for n in s['held']:
        held[n] = held.get(n, 0) + 1
    w_after_at = set(range(ni + 10, ni + 10 + s['vkw_after']))
    for n in range(1, end + 1):
        a('FrameTrace: n=%d dt_us=16667 lat_us=1 draws=%d dispatches=3' % (n, 500 if n >= ni else 50))
        if s['natural'] and n == 900 and s['title_before']:
            a('GuestOut: Level has started: title_controller_ship')
        if s['natural']:
            for p in s['presses']:
                if n == p - OFF:
                    a('InputScript: press j at 40.00 s (present %d)' % p)
                if n == p - OFF + 9:
                    a('InputScript: release j at 40.15 s (present %d)' % (p + 9))
            if n == 2500 and not s['title_before']:
                a('GuestOut: Level has started: title_controller_ship')
        if s['intro'] and n == ni - 1:   # after the FrameTrace of n_intro - 1: n_intro is the next FrameTrace
            if s['form'] == 'w0':
                a('LevelDocument Loaded: %s' % SKY)
                a('GuestOut: Level has started: %s' % SKY)
            else:
                a('GuestOut: Level has started: intro_next')
        if s['w'] and n == 100:   # after a FrameTrace, before the intro line: n_cur < n_intro
            for _ in range(s['vkw_before']):
                a('[Vulkan][W][2]: a warning before the intro')
        if s['w'] and n in w_after_at:
            a('[Vulkan][W][2]: vkCmdDrawIndexed(): a validation warning')
        if n in vke:
            a('[Vulkan][E][2]: VUID-x validation error')
        if s['limit'] and n == ni + 20:
            a('[Vulkan][W][2]: x this will be the last time reporting it')
        for fr in skip.get(n, []):
            a('AsyncPipelines: skipped draw draw#1 frame=%d vs=0x1 ps=0x2' % fr)
        for _ in range(held.get(n, 0)):
            a('AsyncPipelines: flip %d held (incomplete frame)' % n)
        if s['sub'] and s['intro'] and n == n_sw - 1:
            a('GuestOut: SubLevelLocator sublevel_locator_hub [hub_crashsite_tutorial], state changed 6->7')
            a('GuestOut: SubLevelLocator sublevel_locator_space [BA8ED2DC-4A50-756E-1105-39A16AC655DB], state changed 7->6')
        if s['death'] is not None and n == s['death']:
            a('--- Error ---')
        if s['minimized'] and n == ni + 100:
            a('Window 1 minimized')
    if s['summary']:
        a('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=10 bytes=100 max_queued_bytes=10 sync_lines=0 drain_timeouts=0')
    return '\n'.join(L) + '\n'


def write(d, s):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    form = s['form']
    open(os.path.join(d, 'log.txt'), 'w', newline='\n').write(build_log(s))
    open(os.path.join(d, 'stdout.txt'), 'w').write('stdout\n')
    open(os.path.join(d, 'seal.md'), 'wb').write(SEAL)
    env = dict(KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/g', KYTY_SAMPLE_GATE='C:/s', KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1',
               KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if form == 'w0':
        env['KYTY_GUEST_ARGS'] = '-lvl ' + SKY
    elif form in ('vl', 'wl'):
        env['KYTY_GUEST_ARGS'] = '-lvl intro_next'
    if form in ('vn', 'wn'):
        env['KYTY_KEYS'] = '@2170:j,@2460:j'
    if s['w']:
        env.update(VK_LAYER_PATH='C:/VulkanSDK/1.4.357.0/Bin', VK_LAYER_DUPLICATE_MESSAGE_LIMIT='100000000')
    else:
        env['KYTY_REC'] = 'C:/r.mp4'
    env.update(s['extra_env'])
    if s['drop_env']:
        env.pop(s['drop_env'], None)
    vv = s['vv'] or ('true' if s['w'] else 'false')
    cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false', '--shader-validation', 'false', '--game', 'g', '--vulkan-validation', vv]
    ga = None if form in ('vn', 'wn') else ('-lvl ' + (SKY if form == 'w0' else 'intro_next'))
    if s['ga'] is not None:
        ga = s['ga']
    hold = {'w0': 310, 'vn': 600, 'vl': 600, 'wn': 1800, 'wl': 1800}[form]
    att = dict(outcome=s['outcome'], hold_exit=s['hold_exit'], hold_s=310.2 if form == 'w0' else 300.0, hold_end=s['hold_end'])
    js = dict(binary_sha256=TB, prereg=dict(sha256=hashlib.sha256(SEAL if s['prereg_ok'] else b'x').hexdigest()), env=env, cmdline=cmd,
              attempts=[att], guest_args=ga, hold_s=hold)
    json.dump(js, open(os.path.join(d, 'es.json'), 'w'))
    open(os.path.join(d, 'installed_before.txt'), 'w').write(s['inst'] + '\n')
    open(os.path.join(d, 'installed_after.txt'), 'w').write(TB + '\n')
    open(os.path.join(d, 'manifest_cmp.txt'), 'w').write('manifest cmp %s 10 files\n' % s['manifest'])
    open(os.path.join(d, 'level.txt'), 'w').write((SKY if form == 'w0' else 'intro_next') + '\n')
    if not s['w']:
        ni = s['ni']
        off = OFF if s['natural'] else 0
        end = ni + s['delta'] + s['end_after_sw'] + 5
        with open(os.path.join(d, 'rec.idx'), 'w') as f:
            for i, n in enumerate(range(s['idx_from'] + 1, end + 1)):
                f.write('%d %d %.3f\n' % (i, n + off, i / 60.0))
        gl = ['C:/r.mp4: %d frames 960x540, index entries %d' % (end, end), 'one-frame glitches: %d' % (
            len(s['glitch']) if s['glitch_count'] is None else s['glitch_count'])]
        for p in s['glitch']:
            gl.append('  video %5d present %6d t=%7.2fs diff_prev= 40.0 diff_next= 40.0' % (p - off, p, 1.0))
        open(os.path.join(d, 'glitch.txt'), 'w').write('\n'.join(gl) + '\n')
        if s['sheet'] is not None:
            open(os.path.join(d, 'sheet.txt'), 'w').write('room window present [1; 2] step 10: 46 tiles\n%s\n' % s['sheet'])
    return d


def read(tag, s):
    d = write(os.path.join(TMP, tag), s)
    return R.read_tag(tag, R.paths(tag, d))


def mem(r, prefix):
    for a, b in r['members'] or []:
        if a.startswith(prefix):
            return b
    return None


def adm_fail(r):
    return r['status'] == 'INTERFERENCE' and r['members'] is None


ok = True
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)

# --- clean tags of each form
want = {'b6_w0': 'W0_MEMBERS_ALL_YES', 'b6_v': 'ROOM_COVERED', 'b6_v2': 'ROOM_COVERED', 'b6_vl': 'ROOM_COVERED',
        'b6_w': 'W_MEMBERS_ALL_YES', 'b6_wl': 'W_MEMBERS_ALL_YES'}
for tag, form in FORMS.items():
    r = read(tag, spec(form))
    ok &= check('%s clean ADMITTED %s' % (tag, [a for a, x in r['admission'] if not x]), r['status'] == 'ADMITTED')
    ok &= check('%s clean path %s (want %s) %s' % (tag, r['path_status'], want[tag], [a[:60] for a, x in (r['members'] or []) if not x]),
                r['path_status'] == want[tag])
    ok &= check('%s clean all members YES' % tag, r['members'] is not None and all(x for a, x in r['members']))
    r2 = read(tag + '_r1', spec(form))
    ok &= check('%s_r1 reads as the same form' % tag, r2['form'] == form and r2['path_status'] == want[tag])

# --- admission members (every form)
for tag, form in FORMS.items():
    base = spec(form)
    for key, val in (('prereg_ok', False), ('manifest', 'DIFFER'), ('inst', 'abfded5e' * 8), ('minimized', True), ('sig', '0' * 40),
                     ('gamepatch', True)):
        ok &= check('%s admission %s' % (tag, key), adm_fail(read(tag, dict(base, **{key: val}))))
    ok &= check('%s admission extra env VK_LAYER_MESSAGE_ID_FILTER' % tag,
                adm_fail(read(tag, dict(base, extra_env={'VK_LAYER_MESSAGE_ID_FILTER': 'x'}))))
    ok &= check('%s admission extra env KYTY_FIX_B12' % tag, adm_fail(read(tag, dict(base, extra_env={'KYTY_FIX_B12': '1'}))))
    ok &= check('%s admission env missing KYTY_GPU_CLOCK_PIN' % tag, adm_fail(read(tag, dict(base, drop_env='KYTY_GPU_CLOCK_PIN'))))
    ok &= check('%s admission validation flag flipped' % tag, adm_fail(read(tag, dict(base, vv='false' if base['w'] else 'true'))))
    ok &= check('%s admission guest args' % tag, adm_fail(read(tag, dict(base, ga='-lvl other'))))
    ok &= check('%s no summary and no [E] -> INTERFERENCE run' % tag, adm_fail(read(tag, dict(base, summary=False))))
for form in ('vn', 'wn'):
    ok &= check('%s natural form with KYTY_GUEST_ARGS in env -> INTERFERENCE' % form,
                adm_fail(read('b6_v' if form == 'vn' else 'b6_w', spec(form, extra_env={'KYTY_GUEST_ARGS': '-lvl intro_next'}))))
    ok &= check('%s natural form without KYTY_KEYS -> INTERFERENCE' % form,
                adm_fail(read('b6_v' if form == 'vn' else 'b6_w', spec(form, drop_env='KYTY_KEYS'))))
ok &= check('w0 admission entry outcome', adm_fail(read('b6_w0', spec('w0', outcome='timeout'))))
ok &= check('w0 admission entry line', adm_fail(read('b6_w0', spec('w0', intro=False))))
ok &= check('vn entry outcome timeout is NOT an admission member (P3 reads it)',
            read('b6_v', spec('vn', intro=False, outcome='timeout'))['status'] != 'INTERFERENCE')

# --- (P1)-(P3) natural path
r = read('b6_v', spec('vn', ga=None, extra_env={}))
ok &= check('vn (P1) yes on source=none', mem(r, '(P1)') is True)
r = read('b6_v', spec('vn', sched=(2170,)))
ok &= check('vn (P2) one scheduled line -> NO', mem(r, '(P2)') is False)
r = read('b6_v', spec('vn', presses=(2170, 2461), sched=(2170, 2460)))
ok &= check('vn (P2) press at 2461 -> NO', mem(r, '(P2)') is False)
r = read('b6_v', spec('vn', title_before=False))
ok &= check('vn (P3) title after the first press -> NO, NOT_ENTERED', mem(r, '(P3)') is False and r['path_status'] == 'NOT_ENTERED')
r = read('b6_v', spec('vn', intro=False, outcome='timeout', hold_end=None))
ok &= check('vn (P3) no intro line -> NOT_ENTERED (attempt counted)', r['path_status'] == 'NOT_ENTERED')
r = read('b6_vl', spec('vl', intro=False, outcome='timeout'))
ok &= check('vl no intro line -> NOT_ENTERED', r['path_status'] == 'NOT_ENTERED')

# --- (b) item 676 (b): a [Vulkan][E] at W is read only by 674 (g)(2)
for tag, form in (('b6_w', 'wn'), ('b6_wl', 'wl')):
    ni = spec(form)['ni']
    r = read(tag, spec(form, vke=[ni + 1000], summary=False, death=ni + 1000, outcome='ok', hold_exit=1, sub=False, end=ni + 1001))
    ok &= check('%s (b) [E] before the room -> admitted, W_LAYER_ERROR' % tag, r['admitted'] and r['path_status'] == 'W_LAYER_ERROR')
    ok &= check('%s (b) death marker of the layer exit is not a flag' % tag, 'DEATH_MARKER' not in r['flags'] and r['status'] == 'ADMITTED')
    ok &= check('%s (b) note: room not passed by the layer' % tag, 'room not passed by the layer' in ' '.join(r['info']['notes']))
    ok &= check('%s (b) stop n printed' % tag, r['info']['stop_n'] == ni + 1000 and r['info']['e_out_room'] == 1 and r['info']['e_in_room'] == 0)
    r = read(tag, spec(form, vke=[ni + 2880], summary=False))
    ok &= check('%s (b) [E] at n_intro + 2880 (edge) -> in the room, passed' % tag, r['path_status'] == 'W_LAYER_ERROR'
                and r['info']['e_in_room'] == 1 and 'not passed' not in ' '.join(r['info']['notes']))
    r = read(tag, spec(form, vke=[ni + 2879], summary=False))
    ok &= check('%s (b) [E] at n_intro + 2879 -> outside, not passed' % tag, r['info']['e_out_room'] == 1
                and 'not passed' in ' '.join(r['info']['notes']))
    r = read(tag, spec(form, vke=[ni - 50], summary=False))
    ok &= check('%s (b) [E] before the intro -> not passed, outside' % tag, r['path_status'] == 'W_LAYER_ERROR' and r['info']['e_out_room'] == 1)
    r = read(tag, spec(form, vke=[ni + 3331], summary=False))
    ok &= check('%s (b) [E] at n_intro + 3331 -> outside the room window' % tag, r['info']['e_out_room'] == 1)
ok &= check('w0 [E] -> member NO (fs11_w form)', mem(read('b6_w0', spec('w0', vke=[400])), '0 [Vulkan][E]') is False)

# --- (v) item 676 (v): off_L of b6_vl is not computed; the windows
r = read('b6_vl', spec('vl'))
t = r['timeline']
ok &= check('vl (v) off is None, off_L [U] note', t['off'] is None and 'off_L [U]' in t['off_note'])
ok &= check('vl (v) sheet window [n_intro + 2880; n_intro + 3355]', t['sheet_p'] == [310 + 2880, 310 + 3355])
ok &= check('vl (v) cutscene records [n_intro; n_sw + 25]', t['cut_p'] == [310, 310 + DELTA + 25])
ok &= check('vl (v) big frames without a correction', t['big_p'] == [310 + 2950, 310 + 3050, 310 + 3150, 310 + 3250])
r = read('b6_v', spec('vn'))
t = r['timeline']
ok &= check('vn off = median of the input lines (%s)' % t['off'], t['off'] == OFF)
ok &= check('vn sheet window [P_intro + 2880; P_intro + 3330]', t['sheet_p'] == [NI + OFF + 2880, NI + OFF + 3330])
ok &= check('vn cutscene [n_intro + off; n_sw + off]', t['cut_p'] == [NI + OFF, NI + DELTA + OFF])
ok &= check('room window in n [n_intro + 2880; n_intro + 3330]', t['room_n'] == [NI + 2880, NI + 3330])

# --- (g) item 676 (g): W coverage by the event
r = read('b6_w', spec('wn', sub=False, end=NI + 4000))
ok &= check('wn (g) no sub-level line -> W_SHORT', r['path_status'] == 'W_SHORT')
r = read('b6_w', spec('wn', end_after_sw=299, end=NI + DELTA + 299))
ok &= check('wn (g) tail n_sw + 299 -> W_TAIL_SHORT', r['path_status'] == 'W_TAIL_SHORT' and mem(r, '(P5)_W') is False)
r = read('b6_w', spec('wn', end_after_sw=300, end=NI + DELTA + 300))
ok &= check('wn (g) tail n_sw + 300 (edge) -> all yes', r['path_status'] == 'W_MEMBERS_ALL_YES')
r = read('b6_w', spec('wn', delta=900))
ok &= check('wn (g) delta 900 out of the band -> reference only, W_MEMBERS_ALL_YES', r['path_status'] == 'W_MEMBERS_ALL_YES')
r = read('b6_wl', spec('wl', delta=5000))
ok &= check('wl (g) delta 5000 -> reference only', r['path_status'] == 'W_MEMBERS_ALL_YES')

# --- (d) item 676 (d): positive control of the cutscene W
for tag, form in (('b6_w', 'wn'), ('b6_wl', 'wl')):
    r = read(tag, spec(form, vkw_after=0, vkw_before=5))
    ok &= check('%s (d) [W] only before n_intro -> W_NO_POSITIVE_CONTROL' % tag, r['path_status'] == 'W_NO_POSITIVE_CONTROL')
    r = read(tag, spec(form, vkw_after=1))
    ok &= check('%s (d) one [W] after n_intro (edge) -> all yes' % tag, r['path_status'] == 'W_MEMBERS_ALL_YES')
    r = read(tag, spec(form, limit=1))
    ok &= check('%s (d) a limit line -> W_NO_POSITIVE_CONTROL' % tag, r['path_status'] == 'W_NO_POSITIVE_CONTROL')
    r = read(tag, spec(form, death=spec(form)['ni'] + 500))
    ok &= check('%s death marker without [E] -> INTERFERENCE_FLAG' % tag, 'DEATH_MARKER' in r['flags'] and r['status'] != 'ADMITTED')
ok &= check('w0 [W] 0 -> positive control NO', mem(read('b6_w0', spec('w0', vkw_after=0, vkw_before=0)), 'positive control') is False)
ok &= check('w0 limit line -> NO', mem(read('b6_w0', spec('w0', limit=1)), '0 limit lines') is False)

# --- (e) item 676 (e): COLD_ROOM by the position in the log, not by frame=
for tag, form in (('b6_v', 'vn'), ('b6_vl', 'vl')):
    ni = spec(form)['ni']
    r = read(tag, spec(form, skip=[(ni + 2900, 5)]))
    ok &= check('%s (e) skipped inside the window by position, frame= outside -> COLD_ROOM' % tag, 'COLD_ROOM' in r['flags']
                and mem(r, '(V5)') is False)
    r = read(tag, spec(form, skip=[(ni + 100, ni + 2900)]))
    ok &= check('%s (e) skipped outside by position, frame= inside -> no COLD_ROOM' % tag, 'COLD_ROOM' not in r['flags']
                and mem(r, '(V5)') is True)
    r = read(tag, spec(form, held=[ni + 2880]))
    ok &= check('%s (e) held at n_intro + 2880 (edge) -> COLD_ROOM' % tag, 'COLD_ROOM' in r['flags'])
    r = read(tag, spec(form, held=[ni + 3331]))
    ok &= check('%s (e) held at n_intro + 3331 -> no COLD_ROOM' % tag, 'COLD_ROOM' not in r['flags'])
    r = read(tag, spec(form, held=[ni + k for k in range(64)]))
    c = r['info']['cold']
    ok &= check('%s (e) 64 held lines before the window -> 64th n printed, held in the window [U]' % tag,
                c['held_64th_n'] == ni + 63 and c['held_in_room_unknown'] and 'COLD_ROOM' not in r['flags'])
    r = read(tag, spec(form, held=[ni + k for k in range(63)]))
    ok &= check('%s (e) 63 held lines -> no 64th, not unknown' % tag, r['info']['cold']['held_64th_n'] is None
                and not r['info']['cold']['held_in_room_unknown'])

# --- (z) item 676 (z): statuses of the V forms that leave no sheet
for tag, form in (('b6_v', 'vn'), ('b6_vl', 'vl')):
    ni = spec(form)['ni']
    r = read(tag, spec(form, sub=False, end=ni + 3329))
    ok &= check('%s (z) last n = n_intro + 3329 -> ROOM_NOT_COVERED' % tag, r['path_status'] == 'ROOM_NOT_COVERED' and mem(r, '(P5)') is False)
    r = read(tag, spec(form, sub=False, end=ni + 3330))
    ok &= check('%s (z) last n = n_intro + 3330 (edge), no sub-level -> TIMELINE_OTHER' % tag, r['path_status'] == 'TIMELINE_OTHER'
                and mem(r, '(P5)') is True)
    for dl, st in ((4479, 'TIMELINE_OTHER'), (4480, 'ROOM_COVERED'), (4620, 'ROOM_COVERED'), (4621, 'TIMELINE_OTHER')):
        r = read(tag, spec(form, delta=dl))
        ok &= check('%s (z) delta %d -> %s' % (tag, dl, st), r['path_status'] == st)

# --- (i) item 676 (i): W not entered
r = read('b6_w', spec('wn', intro=False, outcome='timeout', sub=False, end=3000))
ok &= check('wn (i) no intro line -> W_NOT_ENTERED (admitted)', r['admitted'] and r['path_status'] == 'W_NOT_ENTERED')
r = read('b6_wl', spec('wl', intro=False, outcome='timeout', sub=False, end=3000))
ok &= check('wl (i) no intro line -> W_NOT_ENTERED', r['path_status'] == 'W_NOT_ENTERED')

# --- (k) item 676 (k): glitches on the cutscene records
r = read('b6_v', spec('vn', glitch=[NI + OFF + 100]))
ok &= check('vn (k) glitch inside the cutscene -> (V3) NO', mem(r, '(V3)') is False)
r = read('b6_v', spec('vn', glitch=[NI + OFF - 1]))
ok &= check('vn (k) glitch one present before P_intro -> (V3) YES, reference', mem(r, '(V3)') is True)
r = read('b6_v', spec('vn', glitch=[NI + DELTA + OFF + 1]))
ok &= check('vn (k) glitch one present after P_sw -> (V3) YES', mem(r, '(V3)') is True)
r = read('b6_vl', spec('vl', glitch=[310 + DELTA + 25]))
ok &= check('vl (k) glitch at n_sw + 25 (edge of L) -> (V3) NO', mem(r, '(V3)') is False)
r = read('b6_v', spec('vn', glitch=[], glitch_count=None))
ok &= check('vn (V3) clean -> YES', mem(r, '(V3)') is True)
d = write(os.path.join(TMP, 'nogl'), spec('vn'))
os.remove(os.path.join(d, 'glitch.txt'))
ok &= check('vn (V3) no detector output -> NO', mem(R.read_tag('b6_v', R.paths('b6_v', d)), '(V3)') is False)

# --- (V1), (V2), (V4)
r = read('b6_v', spec('vn', hold_exit=3221225477))
ok &= check('vn (V1) hold_exit set -> NO and flag NOT_LIVED', mem(r, '(V1) the process lived') is False and 'NOT_LIVED' in r['flags'])
r = read('b6_v', spec('vn', death=NI + 3000))
ok &= check('vn (V1) death marker -> NO and INTERFERENCE_FLAG DEATH_MARKER', mem(r, '(V1) 0 death') is False and 'DEATH_MARKER' in r['flags'])
r = read('b6_v', spec('vn', idx_from=NI + OFF + DELTA - 3000 + 1 - OFF))
ok &= check('vn (V2) 2999 cutscene records -> NO (%s)' % r['info']['records_cut'], mem(r, '(V2)') is False and r['info']['records_cut'] == 2999)
r = read('b6_v', spec('vn', idx_from=NI + OFF + DELTA - 3000 - OFF))
ok &= check('vn (V2) 3000 cutscene records (edge) -> YES', mem(r, '(V2)') is True)
r = read('b6_v', spec('vn', sheet='sheets FAILED room or big image missing'))
ok &= check('vn (V4) sheets FAILED -> NO', mem(r, '(V4)') is False)
r = read('b6_v', spec('vn', sheet=None))
ok &= check('vn (V4) no sheet.txt -> NO', mem(r, '(V4)') is False)

# --- no log, table, usage, cp1250
d = write(os.path.join(TMP, 'nolog'), spec('vn'))
os.remove(os.path.join(d, 'log.txt'))
r = R.read_tag('b6_v', R.paths('b6_v', d))
ok &= check('no log -> INTERFERENCE, no members', r['status'] == 'INTERFERENCE' and r['members'] is None)
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'b6_v'))
json.dump(read('b6_v', spec('vn')), open(os.path.join(rd, 'b6_v', 'read.json'), 'w'), default=list)
tb = R.table(rd)
ok &= check('table has one row', len(tb) == 3 and '| b6_v | ADMITTED | ROOM_COVERED |' in tb[2])
d = write(os.path.join(TMP, 'cp'), spec('wn'))
js = os.path.join(TMP, 'o.json')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        rc_cp = R.main(['--dir', d, '--tag', 'b6_w', '--json', js])
        R.main(['--dir', d, '--tag', 'b6_w', '--timeline'])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
    rc_cp = None
ok &= check('output in strict cp1250 without PYTHONIOENCODING, rc 0', cp_ok and rc_cp == 0 and len(raw.getvalue()) > 1000)
ok &= check('output ASCII only', all(c < 128 for c in raw.getvalue()))
ok &= check('json written and ASCII', os.path.exists(js) and all(c < 128 for c in open(js, 'rb').read()))
ok &= check('reader source ASCII only', all(c < 128 for c in open(SRC, 'rb').read()))
for bad in ('b6_x', 'b6_v_r5', 'b6_v3', 'fs11_w', 'b6_w0_r0'):
    with contextlib.redirect_stdout(io.StringIO()):
        rc_u = R.main([bad])
    ok &= check('usage rc 2 for %s' % bad, rc_u == 2)
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d failed %d' % (N[0], N[1]))
print('ALL OK' if ok and N[1] == 0 else 'FAILED')
sys.exit(0 if ok and N[1] == 0 else 1)
