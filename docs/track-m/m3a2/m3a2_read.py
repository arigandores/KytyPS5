"""Track M link M3a2 (HPP-861; ROADMAP s122 item 778 (d)(3)-(8), 783 (b), (d), 786 (g), 787 (g)): the reader of one tag of the series
M3 of wave 2 on MS2 c630327b and MS1 ea35b679 (installed).  Port of C:/kyty/m657/m3a/m3a_read.py (M3a, HPP-842).  Rows and members only,
NO VERDICT on a theme (the reading is M3b2, the lead).  The sealed FS15c reader C:/kyty/f287/fs15c/fs15c_read.py (sha256 R_SHA) is
IMPORTED, not copied (scan of the log, first scene frame, stdout scan, the knob members of FS15 and FixF20Stat); a fresh instance per tag
with its level constant SKY rebound to the level of the tag.  Changes against M3a: the binaries MS2 / MS1, the installed binary before and
after every tag = MS1, the tag table of the seal section 3 (prefix m3w2_), the MS2 mask 0x3b (T306 on) and signature 0d2da32c (item 786),
the line 'MT125: mode=' (MS2 only; 0 lines at MS1), the T125 members of item 778 (g)(2)(v) with item 783 (b) on the G4 V Sky Garden
m3w2_sg_v and the T125 rows on every MS2 tag.  ASCII only.

    python m3a2_read.py <tag> [--json <out>]
    python m3a2_read.py --dir <fixture dir> --tag <tag> [--json <out>]
    python m3a2_read.py --table [--runs <dir>]
    python m3a2_read.py --plan <tag>                                      the plan line (compared with the dry run of go_m3a2.sh)

DEFINITIONS (seal pred.md section 4): entry line, first scene frame, quit, death markers, the knob lines of FS15 - as fs15c_read.py.
  MWave1   'MWave1: mask=0x<hh> T234=<d> T233=<d> T256=<d> T306=<d> T032=<d> T203=<d>': every parsed line mask = the mask of the plan (MS2
           0x3b; the arm T306=0 0x33; MS1 0x33); >= 1 line (note N1 of item 761 (e): absent only at KYTY_SHADER_CACHE=0 - never set).
  MT265 / MT272 / MT231 / MT125   'MT<n>: mode=<0|1>' (once per process when the path is first used; absent - not called, a row): every
           parsed line mode = the plan (1; 0 for the theme of the arm); MT125 - 0 lines at MS1 (no such code).
  signature / cache dir   the hash of 'ShaderSeed: compatibility=' and the last part of 'Shader translation cache: ': MS2 0d2da32c... and
           variant_fixb26_fixb1b_fixf10_fixf19_mw1_<mask>; MS1 8dcf3177... and ..._mw1_33.
  T125 lines  'MT125Stat: when=exit mixed=<n> mixed_nz=<n>' (at_quick_exit, at =1 only); 'AudioOut: opened SDL device' (count);
           'AudioOut: SDL_OpenAudioDevice failed' and 'AudioOut: SDL audio init failed' and 'AudioIn: SDL init failed' (count);
           'FixF8: mode=1' (count); 'AudioStat: ... init_calls=<n> ...' (only with KYTY_AV_TRACE=1 - absent in the V form).
  G5 measure   as M3a: rows after the first scene frame from + 30 s; end A - before the first 'Event: quit'; end B - all.
MEMBERS V / W / P - as M3a (the SCENE_OK form; item 295 (b); P: lived, 0 death markers) plus the track M lines of the plan.
MEMBERS T125 (only m3w2_sg_v, item 778 (g)(2)(v), 783 (b); Q2 reading of the seal section 4): MT125: mode=1 (>= 1 line, all 1);
  exactly one MT125Stat line and mixed_nz >= 1; opened SDL device = REF_OPENED + 1 (REF_OPENED 3 - the MS1 support log m3_sg_v_r1);
  0 lines of both open / init refusals; FixF8: mode=1 >= 1 (item 790 (b)(1): init_calls of item 778 (g)(2)(v) - NOT MEASURED in the game,
  AudioStat: needs KYTY_AV_TRACE=1 which is not set).
MEMBER ON EVERY MS2 TAG (item 790 (b)(2)): 0 lines 'AudioOut: SDL audio init failed' and 'AudioIn: SDL init failed'.
REFERENCE TAG m3w2_g5_ap (item 790 (a)): the warm-up of the G5 arm A (MS1, a V of the series); members are computed and printed, the tag
  is a reference, not a gate member (a death marker or a frame >= 1 s in it is a row of the seal, not a failure).
NOTE N1 (item 783 (d)): at =1 the bus port numbers move by +1 (audio_handle, port= of AudioStat:, dev= of AvTrace: audio); the reader
  never fixes or compares a port number.
FORM ROWS - the group 'form FS15' of M3a (FixF20 / F24 / F25 / F21 / B12 / F29 / B13 / LogAsync and FixF20Stat), a NO is a question.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

G = 'C:/kyty/m657/m3a2'
R_PATH = 'C:/kyty/f287/fs15c/fs15c_read.py'
R_SHA = '9ef2975702ce8d3b94afdd9c0f3d9198a743711721fa570ac816acb70bb79cf2'
SEAL_PATH = G + '/pred.md'
MS1 = 'ea35b679b0bcfe83767093204f348b189384cab1a7b273f89b164b64cba4d4df'
MS2 = 'c630327bc2a3d9ce13c75edb5d64621d594541dafa7d4a5e97a86b95ba6e7bdf'
INSTALLED = MS1
BIN_PATH = {'ms1': 'C:/kyty/m657/bin/kyty_emulator_ea35b679.exe', 'ms2': 'C:/kyty/m657/bin/kyty_emulator_c630327b.exe'}
BIN_SHA = {'ms1': MS1, 'ms2': MS2}
SIG = {'ms1': '8dcf31779bbcb7c6e605653a138dae162f645a46', 'ms2': '0d2da32ca7ff8b4e4c0fc008726e2c59abe2a8f5'}
DIR0 = 'variant_fixb26_fixb1b_fixf10_fixf19'
VKLAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
LIMIT = '100000000'
POKELOG = '27e46c:909090909090'
LEVELS = {'sg': 'underwater_aerial_garden', 'hb': 'hoover_beach', 'mg': 'mini_giants_garden'}
TBITS = {'234': 0x01, '233': 0x02, '256': 0x04, '306': 0x08, '032': 0x10, '203': 0x20}
HLE_THEMES = ('265', '272', '231', '125')
MASK = {'ms1': 0x33, 'ms2': 0x3b}
REF_OPENED = 3
T125_TAGS = ('m3w2_sg_v',)
REF_TAGS = ('m3w2_g5_ap',)
HOLD_OPT = {'v': 330, 'w': 310, 'p': 150}
K2_US = 1000000
HOLD_V_US = 300000000
HOLD_W_S = 310
VIDEO_MIN = 3000
G5_SKIP_US = 30000000
RX_MW = re.compile(rb'MWave1: mask=0x([0-9a-f]{2}) T234=(\d) T233=(\d) T256=(\d) T306=(\d) T032=(\d) T203=(\d)\s*$')
RX_MT = re.compile(rb'MT(265|272|231|125): mode=(\d+)\s*$')
RX_MTS = re.compile(rb'MT125Stat: when=exit mixed=(\d+) mixed_nz=(\d+)\s*$')
RX_AST = re.compile(rb'AudioStat: .* init_calls=(\d+) ')
RX_GPA = re.compile(rb'^GamePatch: applied sha=([0-9a-f]{16}) pokes=(\d+) pvar=2 audio_sync=0\s*$')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
TAG_RX = re.compile(r'^(m3w2_[a-z0-9_]+?)(_r[1-3])?$')


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_r(level):
    real = sha_file(R_PATH)
    if real != R_SHA:
        raise SystemExit('m3a2_read: %s sha256 %s is not the sealed FS15c reader %s' % (R_PATH, (real or 'missing')[:16], R_SHA[:16]))
    spec = importlib.util.spec_from_file_location('fs15c_read_m3a2_' + level, R_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.SKY = level
    return mod


def plan_of(tag):
    """The plan of a tag (the table of the seal section 3 = the case of go_m3a2.sh); None for an unknown tag."""
    m = TAG_RX.match(tag or '')
    if not m:
        return None
    b = m.group(1)
    p = dict(base_tag=b, knob=None, patch=False)
    v = dict(kind='v', sd=300, timeout=480, hold=330)
    w = dict(kind='w', sd=100, timeout=900, hold=310)
    pp = dict(kind='p', sd=300, timeout=480, hold=150)
    mm = re.match(r'^m3w2_(sg|hb|mg)_([vw])$', b)
    mt = re.match(r'^m3w2_(sg|hb|mg|g5)_t(125|306)0(p|w)?$', b)
    sg = LEVELS['sg']
    if b == 'm3w2_i':
        p.update(bin='ms2', level=sg, cache='K0', save='K1', **v)
    elif mm:
        L, k = mm.groups()
        p.update(bin='ms2', level=LEVELS[L], cache='K1', save='K1', **(w if k == 'w' else v))
    elif b == 'm3w2_g5_ap':
        p.update(bin='ms1', level=sg, cache='K0', save='KA', **v)
    elif b in ('m3w2_g5_a1', 'm3w2_g5_a2'):
        p.update(bin='ms1', level=sg, cache='KA', save='none', **v)
    elif b in ('m3w2_g5_b1', 'm3w2_g5_b2'):
        p.update(bin='ms2', level=sg, cache='K1', save='K1', **v)
    elif b == 'm3w2_g6':
        p.update(bin='ms2', level=sg, cache='K1', save='none', patch=True, **v)
    elif mt:
        L, th, suf = mt.groups()
        lv = LEVELS['sg'] if L == 'g5' else LEVELS[L]
        if L == 'g5' and suf == 'w':
            return None
        if th == '306':
            if suf == 'p':
                p.update(bin='ms2', level=lv, cache='K1', save='KT', **pp)
            else:
                p.update(bin='ms2', level=lv, cache='KT', save='none', **(w if suf == 'w' else v))
        else:
            if suf == 'p':
                return None
            p.update(bin='ms2', level=lv, cache='K1', save='none', **(w if suf == 'w' else v))
        p['knob'] = ('KYTY_M_T' + th, '0')
    else:
        return None
    p['theme_off'] = p['knob'][0][8:] if p['knob'] else None
    return p


def plan_line(tag):
    """The fields of the dry-run line of go_m3a2.sh that the reader checks: bin level kind sd timeout hold cache save knob."""
    p = plan_of(tag)
    if p is None:
        return None
    return 'bin %s level %s kind %s sd %d timeout %d hold %d cache %s save %s knob %s patch %d' % (
        p['bin'], p['level'], p['kind'], p['sd'], p['timeout'], p['hold'], p['cache'], p['save'],
        '%s=%s' % p['knob'] if p['knob'] else '-', 1 if p['patch'] else 0)


def mask_of(p):
    m = MASK[p['bin']]
    if p['theme_off'] in TBITS:
        m &= ~TBITS[p['theme_off']]
    return m


def dir_of(p):
    m = mask_of(p)
    if m == 0:
        return DIR0
    return '%s_mw1_%02x' % (DIR0, m)


def hle_want(p, th):
    if th == '125' and p['bin'] != 'ms2':
        return None
    return 0 if p['theme_off'] == th else 1


def expected_env(p, keys_seal, patch_path):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + p['level'], KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None,
             KYTY_QUEUE_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8')
    if p['kind'] == 'w':
        e.update(VK_LAYER_PATH=VKLAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=LIMIT)
    elif p['kind'] == 'v':
        e.update(KYTY_REC=None)
    if p['knob']:
        e[p['knob'][0]] = p['knob'][1]
    if p['patch']:
        e.update(KYTY_GAME_PATCH=patch_path, KYTY_POKE=POKELOG, KYTY_KEYS=keys_seal)
    return e


def seal_lines(seal):
    keys = patch = None
    t = open(seal, 'rb').read().decode('utf-8', 'replace') if seal and os.path.exists(seal) else ''
    for line in t.splitlines():
        if line.startswith('keys: ') and keys is None:
            keys = line[6:].strip()
        if line.startswith('patch file: ') and patch is None:
            patch = line[12:].strip()
    pth = patch.split(' ', 1)[1] if patch and ' ' in patch else None
    return keys, pth


def scan_m(path):
    """Second pass: the lines of track M and GamePatch."""
    r = dict(mw=[], mw_bad=0, mt={'265': [], '272': [], '231': [], '125': []}, mt_bad=0, texoff=0, gp=0, gp_applied=[], gp_refused=0,
             gp_poke=0, devlost=0, mts=[], mts_bad=0, opened=0, open_failed=0, init_failed=0, in_init_failed=0, f8=0, astat=[],
             astat_bad=0, avtrace=0)
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'FrameTrace'):
                continue
            if b'MWave1:' in line:
                m = RX_MW.search(line)
                if m:
                    r['mw'].append(int(m.group(1), 16))
                else:
                    r['mw_bad'] += 1
            if b': mode=' in line and (b'MT2' in line or b'MT125' in line):
                m = RX_MT.search(line)
                if m:
                    r['mt'][m.group(1).decode()].append(int(m.group(2)))
                elif re.search(rb'MT(265|272|231|125): mode=', line):
                    r['mt_bad'] += 1
            if b'MT125Stat:' in line:
                m = RX_MTS.search(line)
                if m:
                    r['mts'].append((int(m.group(1)), int(m.group(2))))
                else:
                    r['mts_bad'] += 1
            if b'AudioOut: opened SDL device' in line:
                r['opened'] += 1
            if b'SDL_OpenAudioDevice failed' in line:
                r['open_failed'] += 1
            if b'SDL audio init failed' in line:
                r['init_failed'] += 1
            if b'AudioIn: SDL init failed' in line:
                r['in_init_failed'] += 1
            if b'FixF8: mode=1' in line:
                r['f8'] += 1
            if b'AudioStat:' in line:
                m = RX_AST.search(line)
                if m:
                    r['astat'].append(int(m.group(1)))
                else:
                    r['astat_bad'] += 1
            if b'AvTrace:' in line:
                r['avtrace'] += 1
            if b'MTexOffset:' in line:
                r['texoff'] += 1
            if line.startswith(b'GamePatch: '):
                r['gp'] += 1
                m = RX_GPA.match(line)
                if m:
                    r['gp_applied'].append((m.group(1).decode(), int(m.group(2))))
                elif line.startswith(b'GamePatch: refused'):
                    r['gp_refused'] += 1
                elif line.startswith(b'GamePatch: poke '):
                    r['gp_poke'] += 1
            low = line.lower()
            if b'errordevicelost' in low or b'device lost' in low:
                r['devlost'] += 1
    return r


def g5_measure(x, R):
    i, after = R.first_scene(x)
    if i is None:
        return None
    q = x['quit_ln']
    t = 0
    a_rows, b_rows = [], []
    for (n, dt, d, ln) in after:
        if t >= G5_SKIP_US:
            b_rows.append(dt)
            if q is None or ln < q:
                a_rows.append(dt)
        t += dt

    def st(rows):
        if not rows:
            return dict(n=0, mean=None, sd=None, se=None)
        n = len(rows)
        mu = sum(rows) / n
        sd = math.sqrt(sum((v - mu) ** 2 for v in rows) / (n - 1)) if n > 1 else 0.0
        return dict(n=n, mean=round(mu, 2), sd=round(sd, 2), se=round(sd / math.sqrt(n), 3))
    return dict(end_a=st(a_rows), end_b=st(b_rows), first_scene_n=x['ft'][i][0], quit_ln=q)


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet', 'plan', 'k0_cmp',
             'base_cmp')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH)
    return p


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def m_members(p, y):
    """The track M lines of the plan (members)."""
    out = []
    if y is None:
        return [('track M lines: no log', False)]
    want = mask_of(p)
    out.append(('MWave1: mask=0x%02x on every parsed line, >= 1 line (lines %s, unparsable %d; note N1 of item 761 (e))' % (
        want, ['0x%02x' % v for v in y['mw'][:4]], y['mw_bad']), bool(y['mw']) and y['mw_bad'] == 0 and all(v == want for v in y['mw'])))
    for th in HLE_THEMES:
        hw = hle_want(p, th)
        if hw is None:
            out.append(('MS1: 0 lines MT%s: mode= (%d)' % (th, len(y['mt'][th])), not y['mt'][th]))
        else:
            out.append(('MT%s: mode=%d on every parsed line (lines %s; absent - not called, a row)' % (th, hw, y['mt'][th][:4]),
                        all(v == hw for v in y['mt'][th])))
    out.append(('MT unparsable lines 0 (%d)' % y['mt_bad'], y['mt_bad'] == 0))
    return out


def t125_members(p, y):
    """Item 778 (g)(2)(v) with item 783 (b): only on the tags of T125_TAGS (the G4 V Sky Garden of MS2 at =1)."""
    mts = y['mts']
    m = [('MT125: mode=1 - >= 1 line, every line 1 (%s)' % y['mt']['125'][:4], bool(y['mt']['125']) and all(v == 1 for v in y['mt']['125'])),
         ('MT125Stat: when=exit - exactly one line, unparsable 0 (%d, bad %d)' % (len(mts), y['mts_bad']), len(mts) == 1 and y['mts_bad'] == 0),
         ('mixed_nz >= 1 (%s)' % (mts[0][1] if len(mts) == 1 else '-'), len(mts) == 1 and mts[0][1] >= 1),
         ('AudioOut: opened SDL device = REF_OPENED + 1 = %d (item 783 (b); %d)' % (REF_OPENED + 1, y['opened']), y['opened'] == REF_OPENED + 1),
         ('0 lines SDL_OpenAudioDevice failed (%d) and SDL audio init failed (%d)' % (y['open_failed'], y['init_failed']),
          y['open_failed'] == 0 and y['init_failed'] == 0)]
    m.append(('FixF8: mode=1 >= 1 (%d; item 790 (b)(1) - init_calls of item 778 (g)(2)(v) not measured in the game, AudioStat lines %d '
              'a row)' % (y['f8'], len(y['astat'])), y['f8'] >= 1))
    return m


def audio_init_member(y):
    """Item 790 (b)(2): on every tag of MS2."""
    return ('0 lines AudioOut: SDL audio init failed (%d) and AudioIn: SDL init failed (%d) (item 790 (b)(2))' % (
        y['init_failed'], y['in_init_failed']), y['init_failed'] == 0 and y['in_init_failed'] == 0)


def t125_rows(y):
    mts = y['mts']
    return dict(mt125=y['mt']['125'][:3], mt125stat=mts[:2], opened=y['opened'], open_failed=y['open_failed'],
                init_failed=y['init_failed'], in_init_failed=y['in_init_failed'], fixf8=y['f8'], audiostat=len(y['astat']),
                audiostat_init_max=max(y['astat']) if y['astat'] else None, avtrace=y['avtrace'])


def form_members(R, kind, x):
    if kind == 'p':
        return []
    out = [R.f20_member(x, 1), R.f24_member(x, 1), R.f25_member(x, 1), R.f21_member(x, 1), R.f29_member(x, 1), R.mode_member(x),
           R.b13_member(x), R.b12_member(x)]
    out += R.stat_members(x, False)
    return out


def read_tag(tag, pth):
    p = plan_of(tag)
    res = dict(tag=tag, reader_sha256=sha_file(os.path.abspath(__file__)), plan=plan_line(tag))
    if p is None:
        res.update(status='NOT_ADMITTED', admitted=False, interference='unknown tag')
        return res
    R = load_r(p['level'])
    res.update(level=p['level'], bin=p['bin'], kind=p['kind'])
    run = json.load(open(pth['run'], encoding='utf-8')) if os.path.exists(pth['run']) else None
    jbin = (run or {}).get('binary_sha256')
    inst_b = (text(pth['installed_before']) or '').strip() or None
    inst_a = (text(pth['installed_after']) or '').strip() or None
    inst_t = (text(pth['installed_sha']) or '').strip() or None
    seal_sha = sha_file(pth['seal'])
    keys_seal, patch_path = seal_lines(pth['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(pth['manifest_cmp']) or '').strip().splitlines()
    hlev = (text(pth['level']) or '').strip() or None
    plan_txt = (text(pth['plan']) or '').strip()
    k0c = (text(pth['k0_cmp']) or '').strip()
    bcmp = (text(pth['base_cmp']) or '').strip()
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(pth['log'])
    x = R.scan(pth['log']) if have_log else None
    y = scan_m(pth['log']) if have_log else None
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = R.env_diff(kenv, expected_env(p, keys_seal, patch_path))
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = R.stdout_scan(pth['stdout'])
    vv = 'true' if p['kind'] == 'w' else 'false'
    want_bin = BIN_SHA[p['bin']]
    s_stand = None if so is None else so['stand']
    want_plan = '%s %s %s %s %s %s' % (p['bin'], want_bin, p['cache'], p['save'], p['kind'], '%s=%s' % p['knob'] if p['knob'] else '')
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = %s %s (%s)' % (p['bin'], want_bin[:8], (jbin or '-')[:16]), jbin == want_bin),
        ('installed during the tag = %s %s (%s)' % (p['bin'], want_bin[:8], (inst_t or '-')[:16]), inst_t == want_bin),
        ('installed before = after = MS1 ea35b679 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == INSTALLED and inst_a == INSTALLED),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('the plan of go_m3a2.sh = the plan of the reader (%s / %s)' % (plan_txt, want_plan.strip()), plan_txt == want_plan.strip()),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('0 ExitFatal: lines (log %s; whole stdout %s)' % ((x or {}).get('stand'), s_stand), x is not None and x['stand'] == 0 and s_stand == 0),
        ('last --vulkan-validation %s (%s)' % (vv, R.last_flag(cmd, '--vulkan-validation')), R.last_flag(cmd, '--vulkan-validation') == vv),
        ('last --shader-validation false (%s)' % R.last_flag(cmd, '--shader-validation'), R.last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (p['level'], ga, hlev), ga == '-lvl ' + p['level'] and hlev == p['level']),
        ('hold option %d s (%s)' % (p['hold'], (run or {}).get('hold_s')), (run or {}).get('hold_s') == p['hold']),
        ('log present', have_log),
        ('stdout present', so is not None),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % ((x or {}).get('minimized'), (x or {}).get('recovering'),
                                                                                  (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature %s and cache dir %s (%s / %s)' % (SIG[p['bin']][:8], dir_of(p), [z[:8] for z in (x or {}).get('sig') or []],
                                                                (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG[p['bin']]] and x['variant_dir'] == [dir_of(p)]),
        ('GamePatch lines: %s (lines %s, applied %s, refused %s)' % (
            'exactly one applied, 0 refused' if p['patch'] else 'none', (y or {}).get('gp'), (y or {}).get('gp_applied'),
            (y or {}).get('gp_refused')),
         y is not None and ((len(y['gp_applied']) == 1 and y['gp_refused'] == 0) if p['patch'] else y['gp'] == 0)),
        ('no DiagB32 line (%s)' % (x or {}).get('diagb32'), x is not None and x['diagb32'] == 0),
        ('no TestLogStall line (%s)' % (x or {}).get('stall_lines'), x is not None and x['stall_lines'] == 0),
        ('no TestHidLoss line (%s)' % (x or {}).get('hidloss'), x is not None and x['hidloss'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
        ('live caches before the tag = K0 (%s)' % (k0c[:60] or '-'),
         tag == 'm3w2_i' or k0c.startswith('KSET EQUAL4')),
        ('live caches of the run = %s (%s)' % (p['cache'], bcmp[:60] or '-'),
         p['cache'] == 'K0' or bcmp.startswith('manifest cmp EQUAL')),
    ]
    if x is not None and p['kind'] != 'p':
        ok = len(x['summary']) == 1 and x['summary_bad'] == 0
        adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), ok))
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['status'] = 'ADMITTED' if admitted else 'NOT_ADMITTED'
    res['admitted'] = admitted
    res['interference'] = None if admitted else 'admission member: %s' % [a for a, b in adm if not b][:3]
    idx_n = None
    if os.path.exists(pth['idx']):
        with open(pth['idx'], 'rb') as fi:
            idx_n = sum(1 for _ in fi)
    gl = None
    gt = text(pth['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    sheet = (text(pth['sheet']) or '').strip()[:120] or None
    res['members'] = res['form'] = res['info'] = res['g5'] = None
    res['ok'] = res['form_ok'] = None
    if x is not None and admitted:
        lived = att.get('outcome') == 'ok' and att.get('hold_exit') is None
        death = x['death'] + ((so or {}).get('death') or [])
        death_m = ('0 death markers (log and stdout) %s; device lost lines %d' % (death[:3], y['devlost']),
                   not death and so is not None and y['devlost'] == 0)
        i, hold, ge1, ge1_with_first, info = R.scene(x)
        if p['kind'] == 'v':
            end_ok = att.get('close_killed') is False and att.get('close_rc') is not None
            m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
                 ('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
                 death_m,
                 ('0 frames >= 1 s after the first scene frame (%d; first %s; with the first frame %d)' % (ge1, info['first_scene_n'],
                                                                                                       ge1_with_first),
                  i is not None and ge1 == 0),
                 ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN),
                 ('0 one-frame glitches (%s)' % gl, gl == 0),
                 ('sheet for the lead made (%s)' % sheet, bool(sheet)),
                 ('exit by the harness: Event: quit line in the log (%s)' % x['quit_ln'], x['quit_ln'] is not None),
                 ('after Event: quit: 0 --- Fatal Error --- (log %d; whole stdout %s)' % (x['fatal_after_quit'], (so or {}).get('fatal')),
                  x['quit_ln'] is not None and x['fatal_after_quit'] == 0 and (so or {}).get('fatal') == 0),
                 ('the process ended before the harness timeout (close_killed %s, close_rc %s)' % (att.get('close_killed'),
                                                                                                   att.get('close_rc')), end_ok)]
        elif p['kind'] == 'w':
            lived_w = lived and (att.get('hold_s') or 0) >= HOLD_W_S
            g = x['first_guest_ln']
            dual = [d for d in x['dual'] if d[0] and g is not None and d[1] < g]
            m = [('lived to the end of the hold (outcome %s, hold_exit %s, hold_s %s >= 310)' % (att.get('outcome'), att.get('hold_exit'),
                                                                                             att.get('hold_s')), lived_w),
                 death_m,
                 ('0 [Vulkan][E] (%d)' % x['vke'], x['vke'] == 0),
                 ('0 limit lines of the layer (%d)' % x['vk_limit'], x['vk_limit'] == 0),
                 ('positive control: [Vulkan][W] %d > 0' % x['vkw'], x['vkw'] > 0),
                 ('DualSrcBlend: supported=1 enabled=1 before the first GuestOut (%d)' % len(dual), bool(dual))]
        else:
            m = [('the process lived through the hold (outcome %s, hold_exit %s)' % (att.get('outcome'), att.get('hold_exit')), lived),
                 death_m]
        if p['kind'] != 'p':
            m += m_members(p, y)
        if p['bin'] == 'ms2':
            m.append(audio_init_member(y))
        t125 = None
        if p['base_tag'] in T125_TAGS:
            t125 = t125_members(p, y)
            m += [('T125 ' + a, b) for a, b in t125]
        f = form_members(R, p['kind'], x)
        info.update(vke=x['vke'], vkw=x['vkw'], mwave1=['0x%02x' % v for v in y['mw'][:3]],
                    mt=dict((k, v[:3]) for k, v in y['mt'].items()), mtexoffset=y['texoff'], gamepatch_applied=y['gp_applied'],
                    gamepatch_pokes=y['gp_poke'], video_index=idx_n, glitches=gl, t125=t125_rows(y))
        res['members'] = [[a, bool(b)] for a, b in m]
        res['t125_ok'] = None if t125 is None else all(b for _, b in t125)
        res['form'] = [[a, bool(b)] for a, b in f]
        res['ok'] = all(b for _, b in m)
        res['form_ok'] = all(b for _, b in f) if f else None
        res['info'] = info
        res['g5'] = g5_measure(x, R)
        res['exit'] = dict(close_rc=att.get('close_rc'), close_s=att.get('close_s'), close_killed=att.get('close_killed'))
    res['reference'] = p['base_tag'] in REF_TAGS
    res['reading'] = ('ADMITTED, members %s, form FS15 %s (no verdict; reading - M3b2)' % (
        'ALL YES' if res['ok'] else 'NOT ALL YES', 'ALL YES' if res['form_ok'] else ('none' if res['form_ok'] is None else 'NOT ALL YES'))
        if admitted else 'NOT_ADMITTED: %s' % res['interference'])
    if res['reference']:
        res['reading'] += '; REFERENCE tag - the warm-up of the G5 arm A (item 790 (a)), not a gate member'
    return res


def rows_out(res):
    out = ['tag %s (plan: %s)  reader sha256 %s' % (res['tag'], res.get('plan'), res['reader_sha256'])]
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res.get('admission') or []:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    if res.get('members') is not None:
        out.append('  MEMBERS %s' % ('ALL YES' if res['ok'] else 'NOT ALL YES'))
        for a, b in res['members']:
            out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        if res['form']:
            out.append('  FORM FS15 (rows; a NO - question to the lead) %s' % ('ALL YES' if res['form_ok'] else 'NOT ALL YES'))
            for a, b in res['form']:
                out.append('    [%s] %s' % ('YES' if b else 'NO', a))
        if res.get('t125_ok') is not None:
            out.append('  T125 MEMBERS %s' % ('ALL YES' if res['t125_ok'] else 'NOT ALL YES'))
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1600])
        out.append('  G5 MEASURE %s' % json.dumps(res['g5'], sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | bin | level | kind | members | form FS15 | frames >= 1 s | glitches | video | hold_s | mean dt (+30 s, end A) | '
           'MWave1 | T125 opened / mixed_nz |', '|' + '---|' * 14]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if plan_of(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                yn = (lambda v: '-' if v is None else ('ALL YES' if v else 'NOT ALL YES'))
                inf = r.get('info') or {}
                g5 = (r.get('g5') or {}).get('end_a') or {}
                t1 = inf.get('t125') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s |' % (
                    t, r['status'], r.get('bin'), r.get('level'), r.get('kind'), yn(r.get('ok')), yn(r.get('form_ok')),
                    inf.get('frames_ge1s'), inf.get('glitches'), inf.get('video_index'), inf.get('hold_s'), g5.get('mean'),
                    inf.get('mwave1'), t1.get('opened'), [z[1] for z in t1.get('mt125stat') or []]))
    return out


def main(argv):
    if '--plan' in argv:
        print(plan_line(argv[argv.index('--plan') + 1]) or 'unknown')
        return 0
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader m3a2_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for line in table(rd):
            print(line)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        pth = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        pth = paths(tag)
    if plan_of(tag) is None:
        print('usage: m3a2_read.py <tag> | --dir D --tag T | --table | --plan <tag>')
        return 2
    res = read_tag(tag, pth)
    for line in rows_out(res):
        print(line)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
