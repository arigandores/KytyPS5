"""Track S link S18c (HPP-644; ROADMAP s122 item 569 (d)(3)-(5), item 571 (g)(3), item 576 (e), item 579 (v)): the reader of the S-replay
shipment tags on the S18a2 binary b3cee576 (code 0005e11f = FS8a 302347b4 + the S-replay cherry-picks + default 3 + the RC1 fix).  Port of
the S17c2 reader s17c2_read.py (seal edition 4, C:/kyty/s288/s17c2).  Tags (seal docs/track-s/s18c.md = pred/s18c_seal.md):
  s18_c01 .. s18_c19  the replay catalogue of the 19 known levels (the U arms of S15), KYTY_S_REPLAY=2 KYTY_FIX_F19=0 KYTY_SHADER_SEED=0,
                      hold 330 s; the replay folder is NOT cleared between them (accumulation, item 569 (d)(3));
  s18_ks              the stand stop of edition 4 (form s17c_ks2, item 576 (e)(2), members of item 566 (v));
  s18_r               the rebuild at the default (no KYTY_S_REPLAY) from the catalogue into an empty _fixf19, KYTY_SHADER_SEED=0;
  s18_e1, s18_e2      first entries (Sky Garden, mini_giants_garden) at the default after s18_r without a cache return between them;
  s18_v               V Sky Garden at the default on the installed caches plus the catalogue;
  s18_w               W Sky Garden at the default (the rebuild under the validation layer, then the hold).
Rows and a READING word per tag, an ACCUMULATION line per capture tag and a SIGNATURE line on s18_c01 / s18_ks; the member table; NO
verdict (the lead's, S18d HPP-645).  Raw word values of reject lines never reach the output (item 548 (v)(2)).
usage: python s18c_read.py <tag> [--json <out>]       read one made tag (runs/<tag>, log_<tag>.txt, <tag>.json, state/...)
       python s18c_read.py --table                   the member table of the made tags
  Paths: ROOT (default C:/kyty/s288/s18c); the fixtures set S18C_ROOT, S18C_SEAL, S18C_BIN.  ASCII output only.
READING  NOT_ADMITTED (admission row NO: interference of the run, item 273 (z)) -> FORM_FAIL (installed binary or manifest after the return)
         -> MEMBERS_FAIL (a member NO) -> NOT_EVALUABLE (a member not determined) -> MEMBERS_PASS.  REPORT rows never change the word."""
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import state_s17c  # noqa: E402

ROOT = os.environ.get('S18C_ROOT', 'C:/kyty/s288/s18c')
SEAL_PATH = os.environ.get('S18C_SEAL', 'C:/kyty/s288/s18c/pred/s18c_seal.md')
BIN_PATH = os.environ.get('S18C_BIN', 'C:/kyty/s288/bin/kyty_emulator_b3cee576.exe')
BIN_EXPECT = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1897-g0005e11f'
REV = '0005e11'
FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
INSTALLED_OK = (FS8,)     # the installed binary at the print (items 545, 564)
SIG1 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19'   # KYTY_FIX_F19=1 (default)
SIG0 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10'          # KYTY_FIX_F19=0 (capture)
DIR1 = 'variant_fixb26_fixb1b_fixf10_fixf19'
DIR0 = 'variant_fixb26_fixb1b_fixf10'
SKY = 'underwater_aerial_garden'
MGG = 'mini_giants_garden'
LEVELS = ('title_controller_ship', 'intro_next', 'worldmap', 'ps_logo', 'hub_crashsite', SKY, 'penguin_atlantis', 'time_stopper_ghost_world',
          'rotating_level_day_and_night', 'bumper_enemy_snowy_canyon', 'big_hand_pirate_island', 'timestop_casino', MGG, 'ice_iceberg',
          'sponge_dirty_bath', 'hoover_beach', 'volcano_mountain', 'voxel_world', 'enemy_gorilla')   # S15 U arms, 16_s.md section 2
SHARE_MIN = 0.90          # item 569 (d)(4): prepared / records
PREP_MAX_MS = 180000      # item 569 (d)(4), item 229 (d)(2)
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000
K2_US = 1000000
LIMIT = '100000000'       # VK_LAYER_DUPLICATE_MESSAGE_LIMIT of the W form (item 295)
REJECT_KINDS = ('self', 'residual', 'base', 'big')
CAPS = tuple('s18_c%02d' % (i + 1) for i in range(19))
ORDER = CAPS + ('s18_ks', 's18_r', 's18_e1', 's18_e2', 's18_v', 's18_w')
LAST_CAP = CAPS[-1]
CAPV = {'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0', 'KYTY_SHADER_SEED': '0'}
KSV = {'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1', 'KYTY_SHADER_SEED': '0', 'KYTY_S_REPLAY_TEST': 'stop'}
ENTV = {'KYTY_SHADER_SEED': '0', 'KYTY_AV_TRACE': '1'}
SPEC = {}
for _i, _t in enumerate(CAPS):
    SPEC[_t] = dict(level=LEVELS[_i], form='c', hold=330, state='cap0' if _i == 0 else 'cap_acc', prev=CAPS[_i - 1] if _i else None,
                    env=dict(CAPV), group='CAP')
SPEC['s18_ks'] = dict(level=SKY, form='p', hold=0, state='cat_full', prev=LAST_CAP, env=dict(KSV), group='KS')
SPEC['s18_r'] = dict(level=SKY, form='p', hold=0, state='cat_full', prev='s18_ks', env={'KYTY_SHADER_SEED': '0'}, group='R')
SPEC['s18_e1'] = dict(level=SKY, form='v', hold=330, state='chain', prev='s18_r', env=dict(ENTV), group='E')
SPEC['s18_e2'] = dict(level=MGG, form='v', hold=330, state='chain', prev='s18_e1', env=dict(ENTV), group='E')
SPEC['s18_v'] = dict(level=SKY, form='v', hold=330, state='inst_cat', prev='s18_e2', env={}, group='V')
SPEC['s18_w'] = dict(level=SKY, form='w', hold=310, state='cat_full', prev='s18_v', env={}, group='W')
SEED0_TAGS = CAPS + ('s18_ks', 's18_r', 's18_e1', 's18_e2')   # KYTY_SHADER_SEED=0 in the form: 0 seed lines is an admission row
# item 576 (e)(3): no KYTY_S_REPLAY_TEST at s18_r, s18_e1, s18_e2, s18_v, s18_w - their forms carry no such key, so the extra-key row of
# env_rows refuses it (go_s18c.sh refuses it in the calling environment before the lock).
BASE_ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1', 'KYTY_GPU_CLOCK_PIN': '1',
            'KYTY_GPU_MARKERS': '0'}

RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_AV = re.compile(rb'AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=')
RX_KV = re.compile(rb'([a-z_]+)=([^ \r\n]*)')
RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_SIG = re.compile(rb'ShaderSeed: compatibility=KytySeed1:[^:]*:[^:]*:(KytySC3:[0-9a-f]{40}(?::[a-z0-9]+)*)::')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d) enabled=(\d)')
RX_CULPRIT = re.compile(r'culprit=(\d+):role(\d+):([0-9a-f]{8})->([0-9a-f]{8})')
RX_CULPRIT_RES = re.compile(r'culprit=(\d+):role(\d+)(?![0-9:])')
RX_WHY = re.compile(r'^capture reject why=(.*?) hash=(0x[0-9a-fA-F]+) words=(\d+)$')
M_SR = b'ShaderReplay:'
M_GUEST = b'GuestOut:'
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
M_SPECFAIL = b'shader resource specialization failed'
M_SEED = b'ShaderSeed: installed'
M_QUIT = b'Event: quit'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')


# ----------------------------------------------------------------------------------------------------------------- small helpers

def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def first_line(t):
    return (t or '').split('\n')[0].strip()


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def kv(raw):
    """'a=1 b=x' fields of a ShaderReplay line -> dict of str."""
    return dict((k.decode(), v.decode('ascii', 'replace')) for k, v in RX_KV.findall(raw))


def num(d, k):
    try:
        return int(d[k])
    except (KeyError, ValueError, TypeError):
        return None


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def paths(tag):
    d = os.path.join(ROOT, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in ('installed_sha', 'installed_before', 'installed_after', 'manifest_cmp', 'glitch',
                                                       'sheet', 'state_in', 'state_out', 'state_in_name', 'chain_cmp'))
    p.update(dir=d, log=os.path.join(ROOT, 'log_%s.txt' % tag), stdout=os.path.join(ROOT, 'stdout_%s.txt' % tag),
             run=os.path.join(ROOT, '%s.json' % tag), idx=os.path.join(ROOT, 'rec_%s.mp4.idx' % tag),
             state=os.path.join(ROOT, 'state', tag), readjson=os.path.join(d, 'read.json'))
    return p


def reject_parse(body):
    """A 'capture reject why=<why> hash=<h> words=<n>' line -> dict (edition 3, item 541 (g), 548 (v)(2)); raw word values are read only into
    canon_zero and never returned."""
    d = dict(kind='?', branch=None, culprit=None, role=None, canon_zero=None, n=None, ok=None, complete=None, hash=None, words=None)
    m = RX_WHY.match(body.strip())
    if not m:
        return d
    why = m.group(1)
    d['hash'], d['words'] = m.group(2), m.group(3)
    toks = why.split()
    if toks and re.match(r'^[a-z_]+$', toks[0]):
        d['kind'] = toks[0]
    f = dict(x.split('=', 1) for x in toks[1:] if '=' in x)
    if f.get('branch') in ('addr', 'exact'):
        d['branch'] = f['branch']
    for k in ('ok', 'complete', 'n'):
        if re.match(r'^\d+$', f.get(k, '')):
            d[k] = f[k]
    c = RX_CULPRIT.search(why)
    if c:
        d['culprit'], d['role'], d['canon_zero'] = c.group(1), c.group(2), 1 if c.group(4) == '00000000' else 0
    else:
        c = RX_CULPRIT_RES.search(why)
        if c:
            d['culprit'], d['role'] = c.group(1), c.group(2)
    return d


def reject_summary(rejects):
    kinds = {}
    for _, body in rejects:
        d = reject_parse(body)
        k = d['kind'] if d['kind'] in REJECT_KINDS else 'other'
        kinds[k] = kinds.get(k, 0) + 1
    return dict(sorted(kinds.items()))


# ----------------------------------------------------------------------------------------------------------------- log scan

def scan(log_path, level):
    """One streaming pass over the emulator log; every row the members need.  The entry is the first 'Level has started: <level>'.
    k2_after - frames >= 1 s after the first scene frame (the SCENE_OK domain of sc146); k2_entry - frames >= 1 s from the entry line to
    the first scene frame inclusive (reference, the other reading)."""
    r = dict(lines=0, sha256=None, sr=0, mode=[], capture=[], reject=[], stand=[], rebuild=[], skipped=[], close_req=[], close_joined=[],
             precache_no=[], prep=None, prep_line=None, stc=[], av=[], first_guest=None, entry_line=None, scene_change_line=None,
             first_scene_n=None, hold_us=0, k2_after=0, k2_entry=0, ft_rows=0, death=[], skipped_draw=0, win={}, recovering=0,
             gamepatch=0, specfail=0, rev=[], seed=0, quit=[], sig=[], dual=[], vke=0, vkw=0, vk_limit=0)
    if not log_path or not os.path.exists(log_path):
        return r
    h = hashlib.sha256()
    after_entry = in_scene = False
    with open(log_path, 'rb') as f:
        for raw in f:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
            if b'FrameTrace: n=' in raw:
                m = RX_FT.search(raw)
                if m:
                    n, dt = int(m.group(1)), int(m.group(2))
                    r['ft_rows'] += 1
                    if after_entry and r['scene_change_line'] is None:
                        if not in_scene:
                            if dt >= K2_US:
                                r['k2_entry'] += 1
                            md = RX_DRAWS.search(m.group(3))
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['first_scene_n'] = n
                        else:
                            r['hold_us'] += dt
                            if dt >= K2_US:
                                r['k2_after'] += 1
                    continue
            if M_SR in raw:
                r['sr'] += 1
                body = raw.split(M_SR, 1)[1].strip()
                d = kv(body)
                if body.startswith(b'mode='):
                    r['mode'].append((ln, d))
                elif body.startswith(b'capture reject '):
                    r['reject'].append((ln, body.decode('ascii', 'replace')))
                elif body.startswith(b'capture sources='):
                    r['capture'].append((ln, d))
                elif body.startswith(b'stand '):
                    r['stand'].append((ln, body.decode('ascii', 'replace'), d))
                elif body.startswith(b'rebuild skipped '):
                    r['skipped'].append((ln, d.get('reason')))
                elif body.startswith(b'rebuild '):
                    r['rebuild'].append((ln, d))
                elif body.startswith(b'close stop requested'):
                    r['close_req'].append((ln, d))
                elif body.startswith(b'close stop joined'):
                    r['close_joined'].append((ln, d))
            if b'AvTrace: shader ' in raw:
                m = RX_AV.search(raw)
                if m:
                    r['av'].append((ln, int(m.group(2), 16), m.group(1).decode('ascii', 'replace')))
            if b'PipelinePrecache: no ' in raw and raw.rstrip().endswith(b' yet'):
                r['precache_no'].append(ln)
            if r['prep'] is None and b'ShaderPreparation: startup wait finished' in raw:
                m = RX_PREP.search(raw)
                r['prep'] = int(m.group(1)) if m else None
                r['prep_line'] = ln
            if b'Shader translation cache: ' in raw:
                r['stc'].append(raw.split(b'Shader translation cache: ', 1)[1].strip()[:200].decode('ascii', 'replace'))
            if b'ShaderSeed: compatibility=' in raw:
                m = RX_SIG.search(raw)
                r['sig'].append(m.group(1).decode('ascii') if m else '<unparsed>')
            if b'DualSrcBlend:' in raw:
                m = RX_DUAL.search(raw)
                if m:
                    r['dual'].append((ln, int(m.group(1)), int(m.group(2))))
            if b'[Vulkan][' in raw:
                if b'[Vulkan][E]' in raw:
                    r['vke'] += 1
                if b'[Vulkan][W]' in raw:
                    r['vkw'] += 1
            if b'this will be the last time reporting it' in raw:
                r['vk_limit'] += 1
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('log', ln, rv))
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['first_guest'] is None and M_GUEST in raw:
                r['first_guest'] = ln
            if M_SEED in raw:
                r['seed'] += 1
            if M_QUIT in raw:
                r['quit'].append(ln)
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'Recovering Vulkan swapchain' in raw:
                r['recovering'] += 1
            if b'GamePatch:' in raw:
                r['gamepatch'] += 1
            if M_SPECFAIL in raw:
                r['specfail'] += 1
            if b'Window ' in raw:
                m = RX_WIN.search(raw)
                if m:
                    k = m.group(1).decode()
                    r['win'][k] = r['win'].get(k, 0) + 1
            for dm in DEATH:
                if dm in raw:
                    r['death'].append(('log', dm.decode(), ln))
    r['sha256'] = h.hexdigest()
    return r


def stdout_scan(path):
    r = dict(present=False, death=[], sr=0, specfail=0, rev=[], sha256=None, seed=0)
    if not path or not os.path.exists(path):
        return r
    r['present'] = True
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            if M_SR in raw:
                r['sr'] += 1
            if M_SPECFAIL in raw:
                r['specfail'] += 1
            if M_SEED in raw:
                r['seed'] += 1
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('stdout', i, rv))
            for dm in DEATH:
                if dm in raw:
                    r['death'].append(('stdout', dm.decode(), i))
    r['sha256'] = h.hexdigest()
    return r


# ----------------------------------------------------------------------------------------------------------------- catalogue

def catalogue(path):
    """Offline rows of one generation file (edition 3): r_addr.py scan plus the program hashes of R-SRC."""
    import r_addr
    data = open(path, 'rb').read()
    base = r_addr.scan(data)
    L = r_addr.LAYOUT
    compat_size = struct.unpack_from('<I', data, L['file.compat_size'])[0]
    compat = data[L['file']:L['file'] + compat_size].decode('ascii', 'replace')
    pos = L['file'] + compat_size
    generation, _checksum, n_src, _n_spec, _n_pipe = struct.unpack_from('<QQIII', data, pos)
    pos += L['body']
    hashes = []
    for _ in range(n_src):
        hashes.append(struct.unpack_from('<Q', data, pos + L['src.hash'])[0])
        sw, cw, bw = struct.unpack_from('<III', data, pos + L['src.static_words'])
        pos += L['src'] + 4 * (sw + cw + bw)
    base.update(compat=compat, src_hashes=sorted(set(hashes)), generation=generation)
    return base


def catalogue_of(tag):
    """(generation number of replay.cur, path of its file, catalogue dict or None, error) of the saved replay folder of a tag."""
    rp = os.path.join(paths(tag)['state'], 'replay')
    cur = os.path.join(rp, 'replay.cur')
    if not os.path.exists(cur):
        return None, None, None, 'no %s' % cur
    try:
        g = int(open(cur, 'rb').read().split()[0])
    except (ValueError, IndexError):
        return None, None, None, 'replay.cur unreadable'
    f = os.path.join(rp, 'replay.%d.bin' % g)
    if not os.path.exists(f):
        return g, f, None, 'generation file missing'
    try:
        return g, f, catalogue(f), None
    except (ValueError, struct.error) as e:
        return g, f, None, 'unreadable: %s' % e


def saved_files(tag):
    """{name: (size, sha256)} of the files of state/<tag>/replay ({} when absent)."""
    saved = os.path.join(paths(tag)['state'], 'replay')
    want = {}
    if os.path.isdir(saved):
        for n in sorted(os.listdir(saved)):
            fp = os.path.join(saved, n)
            if os.path.isfile(fp):
                want[n] = (os.path.getsize(fp), sha_file(fp))
    return want


# ----------------------------------------------------------------------------------------------------------------- stand stop (item 566 (v))

def first_stand(r, prefix):
    for ln, t, d in r['stand']:
        if t.startswith(prefix):
            return ln, d
    return None


def stop_facts(r):
    """The rows of the stop tag from one scan: the five lines of item 566 (v), the timeout lines, the stopped rebuild line."""
    stopped = [(ln, d) for ln, d in r['rebuild'] if d.get('pipelines_bin') == 'stopped']
    return dict(applied=first_stand(r, 'stand stop applied'), seen=first_stand(r, 'stand stop seen'),
                timeout=sum(1 for _, t, _d in r['stand'] if t.startswith('stand stop timeout')),
                req=r['close_req'][0] if r['close_req'] else None, joined=r['close_joined'][0] if r['close_joined'] else None,
                stopped=stopped[0] if stopped else None, quit=len(r['quit']))


def close_path(f, exit_code):
    """Item 566 (v) (RC1) on s18_ks: YES only for the lines in the order stand stop applied processed=P records=R -> close stop requested
    precache_active=1 -> stand stop seen ... processed=P records=R -> rebuild ... pipelines_bin=stopped -> close stop joined wait_ms=...,
    one P in both lines and P < R, 0 stand stop timeout lines, 0 Event: quit lines, exit code 0.  A timeout line -> NO; any other
    difference -> NOT DETERMINED.  -> (ok, detail)."""
    if f['timeout'] > 0:
        return False, 'stand stop timeout lines %d' % f['timeout']
    a, q, s, b, j = f['applied'], f['req'], f['seen'], f['stopped'], f['joined']
    det = 'applied %s requested %s seen %s stopped %s joined %s quit %d exit %s' % (
        a and a[0], q and q[0], s and s[0], b and b[0], j and j[0], f['quit'], exit_code)
    if None in (a, q, s, b, j):
        return None, 'missing line: ' + det
    if not (a[0] < q[0] < s[0] < b[0] < j[0]):
        return None, 'order: ' + det
    pa, ra, ps, rs = num(a[1], 'processed'), num(a[1], 'records'), num(s[1], 'processed'), num(s[1], 'records')
    if None in (pa, ra, ps, rs) or pa != ps or ra != rs or not pa < ra:
        return None, 'P/R: applied %s/%s seen %s/%s; %s' % (pa, ra, ps, rs, det)
    if q[1].get('precache_active') != '1':
        return None, 'precache_active=%s; %s' % (q[1].get('precache_active'), det)
    if f['quit'] != 0:
        return None, 'Event: quit lines %d; %s' % (f['quit'], det)
    if exit_code != 0:
        return None, 'exit code %s; %s' % (exit_code, det)
    return True, 'P %d R %d; %s' % (pa, ra, det)


# ----------------------------------------------------------------------------------------------------------------- accumulation (item 569 (d)(3))

def accumulation(tag, md, lc, cur, cat_ok, prev):
    """The accumulation members of a capture tag.  md - its mode line; lc - its last capture at=stop line (None when absent); cur - the
    replay.cur of its saved replay folder (None when absent); cat_ok - the generation file of cur reads; prev - None for s18_c01, else
    dict(cur=replay.cur of the saved replay folder of the previous capture tag, cs=catalogue_sources, cp=catalogue_specs of its last
    at=stop line).  -> [(name, ok, detail)]:
      mode     s18_c01: mode=2 compat=absent generation=0; later: mode=2 compat=ok and generation = replay.cur of the previous tag;
      ondisk   replay.cur = gen of the last at=stop line and its generation file reads; gen=0 (no save in this start - executor's variant,
               seal section 4): replay.cur = the previous replay.cur and catalogue_* of the line = sources / specs / pipes of the mode line;
      nondec   (later tags) catalogue_sources and catalogue_specs of the last at=stop line >= those of the previous tag."""
    out = []
    if prev is None:
        out.append(('mode', md.get('mode') == '2' and md.get('compat') == 'absent' and md.get('generation') == '0', md))
    else:
        ok = md.get('mode') == '2' and md.get('compat') == 'ok' and prev.get('cur') is not None and num(md, 'generation') == prev['cur']
        out.append(('mode', ok, 'mode line %s / previous replay.cur %s' % (md, prev.get('cur'))))
    if lc is None:
        out.append(('ondisk', None, 'no capture at=stop line'))
    else:
        gen = num(lc, 'gen')
        if gen == 0:
            same = (prev is not None and cur is not None and cur == prev.get('cur') and
                    all(num(lc, 'catalogue_' + k) == num(md, k) for k in ('sources', 'specs', 'pipes')))
            out.append(('ondisk', same and cat_ok, 'gen 0 (no save): replay.cur %s previous %s catalogue %s' % (
                cur, prev and prev.get('cur'), [lc.get('catalogue_' + k) for k in ('sources', 'specs', 'pipes')])))
        else:
            out.append(('ondisk', cur is not None and gen == cur and cat_ok, 'replay.cur %s gen %s readable %s' % (cur, gen, cat_ok)))
    if prev is not None:
        if lc is None or prev.get('cs') is None or prev.get('cp') is None:
            out.append(('nondec', None, 'no at=stop line here or at the previous tag'))
        else:
            cs, cp = num(lc, 'catalogue_sources'), num(lc, 'catalogue_specs')
            out.append(('nondec', cs is not None and cp is not None and cs >= prev['cs'] and cp >= prev['cp'],
                        'catalogue_sources %s >= %s, catalogue_specs %s >= %s' % (cs, prev['cs'], cp, prev['cp'])))
    return out


def acc_word(rows):
    """ACCUMULATION OK / BREACH / UNDETERMINED from the accumulation members (a False -> BREACH, else a None -> UNDETERMINED)."""
    vals = [ok for _, ok, _ in rows]
    if any(v is False for v in vals):
        return 'BREACH'
    if any(v is None for v in vals):
        return 'UNDETERMINED'
    return 'OK'


def signature_ok(r, want):
    """Item 571 (g)(3): the full signature string of the 'ShaderSeed: compatibility=' line(s) = want (every line, >= 1)."""
    return len(r['sig']) >= 1 and all(s == want for s in r['sig'])


# ----------------------------------------------------------------------------------------------------------------- members

class Rows:
    def __init__(self):
        self.adm, self.form, self.mem, self.rep = [], [], [], []
        self.lines = []

    def a(self, name, ok, detail=''):
        self.adm.append((name, ok, asc(str(detail))))

    def f(self, name, ok, detail=''):
        self.form.append((name, ok, asc(str(detail))))

    def m(self, name, ok, detail=''):
        self.mem.append((name, ok, asc(str(detail))))

    def r(self, name, detail):
        self.rep.append((name, asc(str(detail))))

    def word(self):
        if any(ok is not True for _, ok, _ in self.adm):
            return 'NOT_ADMITTED'
        if any(ok is not True for _, ok, _ in self.form):
            return 'FORM_FAIL'
        if any(ok is False for _, ok, _ in self.mem):
            return 'MEMBERS_FAIL'
        if any(ok is None for _, ok, _ in self.mem):
            return 'NOT_EVALUABLE'
        return 'MEMBERS_PASS'


def yn(ok):
    return {True: 'YES', False: 'NO', None: 'NOT DETERMINED'}[ok]


def want_env(tag):
    spec = SPEC[tag]
    want = dict(BASE_ENV)
    want['KYTY_GUEST_ARGS'] = '-lvl ' + spec['level']
    want.update(spec['env'])
    return want


def env_rows(rows, tag, run):
    spec = SPEC[tag]
    env = (run or {}).get('env') or {}
    want = want_env(tag)
    kyty = dict((k, v) for k, v in env.items() if k.startswith('KYTY_'))
    bad = []
    for k, v in want.items():
        if kyty.get(k) != v:
            bad.append('%s=%s want %s' % (k, kyty.get(k), v))
    allowed = set(want) | {'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE'} | ({'KYTY_REC'} if spec['form'] == 'v' else set())
    for k in kyty:
        if k not in allowed:
            bad.append('extra %s' % k)
    for k in ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE'):
        if not kyty.get(k):
            bad.append('no %s' % k)
    if spec['form'] == 'v' and not kyty.get('KYTY_REC'):
        bad.append('no KYTY_REC')
    vk = dict((k, v) for k, v in env.items() if k.startswith('VK_LAYER_'))
    if spec['form'] == 'w':
        if not vk.get('VK_LAYER_PATH'):
            bad.append('no VK_LAYER_PATH')
        if vk.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT') != LIMIT:
            bad.append('VK_LAYER_DUPLICATE_MESSAGE_LIMIT=%s' % vk.get('VK_LAYER_DUPLICATE_MESSAGE_LIMIT'))
        if 'VK_LAYER_MESSAGE_ID_FILTER' in vk:
            bad.append('VK_LAYER_MESSAGE_ID_FILTER')
        extra_vk = sorted(k for k in vk if k not in ('VK_LAYER_PATH', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT', 'VK_LAYER_MESSAGE_ID_FILTER'))
        if extra_vk:
            bad.append('VK_LAYER_* extra %s' % extra_vk)
    elif vk:
        bad.append('VK_LAYER_* %s' % sorted(vk))
    rows.a('environment = the form of the tag (seal section 2; no KYTY_S_REPLAY_TEST at the shipment tags, item 576 (e)(3))', not bad,
           'offending %s' % bad if bad else 'KYTY keys %s' % sorted(kyty))
    val = None
    cmd = (run or {}).get('cmdline') or []
    for i, x in enumerate(cmd):
        if x == '--vulkan-validation':
            val = cmd[i + 1] if i + 1 < len(cmd) else None
    want_val = 'true' if spec['form'] == 'w' else 'false'
    rows.a('command line --vulkan-validation (last) = %s' % want_val, val == want_val, val)


def state_rows(rows, tag, p, sin):
    spec = SPEC[tag]
    st = spec['state']
    name = first_line(text(p['state_in_name']))
    rows.a('input state name = %s' % st, name == st, name)
    if sin is None:
        rows.a('input state described (state_in.txt)', False, 'missing')
        return
    f10, f19, rp = sin.get('f10', {}), sin.get('f19', {}), sin.get('replay', {})
    if st == 'cap0':
        rows.a('input state cap0: %s absent and replay absent' % DIR0, f10.get('present') is False and rp.get('present') is False, (f10, rp))
        return
    src = spec['prev'] if st in ('cap_acc', 'chain') else LAST_CAP
    want = saved_files(src)
    same = rp.get('present') is True and rp.get('replay_files') == want and len(want) > 0
    rows.a('input state %s: replay = state/%s/replay byte for byte' % (st, src), same,
           'files %d / saved %d' % (len(rp.get('replay_files') or {}), len(want)))
    if st == 'cap_acc':
        rows.a('input state cap_acc: %s absent (empty capture folder)' % DIR0, f10.get('present') is False, f10)
    elif st == 'cat_full':
        rows.a('input state cat_full: %s absent (empty variant folder of the default signature)' % DIR1, f19.get('present') is False, f19)
    elif st == 'inst_cat':
        rows.a('input state inst_cat: %s present with pipelines.bin (the installed folder)' % DIR1,
               f19.get('present') is True and f19.get('pipelines_bin') is True, f19)
    else:
        rows.a('input state chain: %s present with pipelines.bin' % DIR1, f19.get('present') is True and f19.get('pipelines_bin') is True, f19)
        cc = first_line(text(p['chain_cmp']))
        rows.a('input state chain: manifest of the caches at the input = manifest of the run state of %s (no return between, item 569 (d)(4))'
               % spec['prev'], cc.startswith('manifest cmp EQUAL'), cc[:120])


def common(tag, p, r, so, run):
    rows = Rows()
    att = ((run or {}).get('attempts') or [{}])[0] if run else {}
    rows.a('run record <tag>.json present, one attempt', run is not None and len((run or {}).get('attempts') or []) == 1,
           'attempts %s' % (len((run or {}).get('attempts') or []) if run else None))
    sha = first_line(text(p['installed_sha'])) or None
    rows.a('binary of the run = S18a2 b3cee576 (json binary_sha256 and installed_sha.txt; item 579)',
           (run or {}).get('binary_sha256') == BIN_EXPECT and sha == BIN_EXPECT, '%s / %s' % ((run or {}).get('binary_sha256'), sha))
    vb = None
    if os.path.exists(BIN_PATH):
        vb = VERSION in open(BIN_PATH, 'rb').read()
    rows.a('version string %s in the binary copy' % VERSION.decode(), vb is True, vb)
    revs = r['rev'] + so['rev']
    badrev = [x for x in revs if REV not in x[2]]
    rows.a('revision texts of log / stdout name %s' % REV, not badrev and len(revs) > 0, 'texts %d, other %s' % (len(revs), badrev[:3]))
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    rows.a('prereg sha256 = the seal file (%s)' % os.path.basename(SEAL_PATH), pre is not None and pre == sha_file(SEAL_PATH),
           '%s / %s' % (pre, sha_file(SEAL_PATH)))
    env_rows(rows, tag, run)
    if tag in SEED0_TAGS:
        rows.a('0 lines ShaderSeed: installed (log, stdout; KYTY_SHADER_SEED=0)', r['seed'] == 0 and so['seed'] == 0,
               '%d / %d' % (r['seed'], so['seed']))
    else:
        rows.r('lines ShaderSeed: installed (log / stdout; seed at the default)', '%d / %d' % (r['seed'], so['seed']))
    win = r['win'].get('minimized', 0)
    rows.a('no window minimized, no Recovering Vulkan swapchain, no GamePatch line', win == 0 and r['recovering'] == 0 and
           r['gamepatch'] == 0, 'minimized %d recovering %d gamepatch %d' % (win, r['recovering'], r['gamepatch']))
    sin_t = text(p['state_in'])
    sin = state_s17c.parse(sin_t) if sin_t is not None else None
    state_rows(rows, tag, p, sin)
    rows.a('emulator log present', r['sha256'] is not None, r['sha256'])
    b = first_line(text(p['installed_before'])) or None
    a = first_line(text(p['installed_after'])) or None
    rows.f('installed binary before = after, FS8', b is not None and b == a and b in INSTALLED_OK, '%s / %s' % (b, a))
    mc = first_line(text(p['manifest_cmp']))
    rows.f('manifest of the caches after the return EQUAL', mc.startswith('manifest cmp EQUAL'), mc[:120])
    rows.r('window lines', r['win'])
    rows.r('death markers log / stdout', '%d / %d %s' % (len(r['death']), len(so['death']), (r['death'] + so['death'])[:3]))
    rows.r('skipped draw lines', r['skipped_draw'])
    rows.r('translation cache directory lines', r['stc'][:4])
    rows.r('signature lines (ShaderSeed: compatibility)', r['sig'][:2])
    rows.r('exit', 'outcome %s detail %s hold_exit %s hold_s %s close_rc %s close_killed %s close_s %s' % (
        att.get('outcome'), att.get('detail'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'),
        att.get('close_s')))
    rows.r('preparation screen (startup wait finished)', '%s ms at line %s' % (r['prep'], r['prep_line']))
    return rows, att, sin


def exit_code(att):
    """The exit code of a process that ended by itself (outcome exited, detail 'exit code <n>'), else None."""
    m = re.match(r'^exit code (-?\d+)$', str(att.get('detail') or ''))
    return int(m.group(1)) if att.get('outcome') == 'exited' and m else None


def lived(att, hold):
    return att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= hold


def entered(r, att):
    return r['entry_line'] is not None and att.get('outcome') == 'ok'


def directory_ok(r, want):
    return len(r['stc']) >= 1 and all(x.replace(chr(92), '/').endswith(want) for x in r['stc'])


def deaths(r, so):
    return len(r['death']) + len(so['death'])


def video_rows(rows, p, r, so, group):
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    rows.m('%s video index records >= %d' % (group, VIDEO_MIN), None if idx_n is None else idx_n >= VIDEO_MIN, idx_n)
    gt = text(p['glitch'])
    gl = None
    if gt:
        m = RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    rows.m('%s 0 one-frame glitches (s51_vidglitch.py 4 6)' % group, None if gl is None else gl == 0, gl)
    st = text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    rows.m('%s sheet of the lead made' % group, None if st is None else sheet is not None, sheet)


def scene_rows(rows, r, so, att, hold, group, level):
    """The members of SCENE_OK (item 569 (d)(4)): entered, lived to the end of the hold, shown hold after the first scene frame >= 300 s,
    0 death markers, 0 frames >= 1 s after the first scene frame (the domain of sc146); the frames >= 1 s from the entry line to the
    first scene frame - a report row (the other reading)."""
    rows.m('%s entered (Level has started: %s, outcome ok)' % (group, level), entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('%s the process lived to the end of the hold (%d s)' % (group, hold), lived(att, hold),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    rows.m('%s shown hold after the first scene frame >= 300 s' % group, r['hold_us'] >= HOLD_MIN_US, '%.1f s' % (r['hold_us'] / 1e6))
    rows.m('%s 0 death markers (log, stdout)' % group, deaths(r, so) == 0, deaths(r, so))
    rows.m('%s 0 frames >= 1 s after the first scene frame' % group, None if r['first_scene_n'] is None else r['k2_after'] == 0,
           'frames %d, first scene frame n=%s' % (r['k2_after'], r['first_scene_n']))
    rows.r('frames >= 1 s from the entry line to the first scene frame (other reading, reference)', r['k2_entry'])


def last_capture(r):
    stops = [d for _, d in r['capture'] if d.get('at') == 'stop']
    return stops[-1] if stops else None


def soft_close(att):
    return att.get('close_killed') is False and att.get('close_rc') is not None


def av_catalogue(r, hashes, after_line):
    if after_line is None:
        return None, None
    hs = set(hashes)
    after = [x for x in r['av'] if x[0] > after_line]
    return sum(1 for x in after if x[1] in hs), len(after)


def read_json_of(tag):
    t = text(paths(tag)['readjson'])
    return json.loads(t) if t else None


def read_tag(tag):
    if tag not in SPEC:
        raise SystemExit('unknown tag %s' % tag)
    p = paths(tag)
    spec = SPEC[tag]
    lv = spec['level']
    r = scan(p['log'], lv)
    so = stdout_scan(p['stdout'])
    rt = text(p['run'])
    run = json.loads(rt) if rt else None
    rows, att, sin = common(tag, p, r, so, run)
    sout_t = text(p['state_out'])
    sout = state_s17c.parse(sout_t) if sout_t is not None else None
    extra = {}
    g = spec['group']
    if g == 'CAP':
        capture_rows(rows, tag, p, r, so, att, extra)
    elif g == 'KS':
        stop_rows(rows, r, so, att, sout, extra)
    elif g == 'R':
        rebuild_rows(rows, tag, p, r, so, att, extra)
    elif g == 'E':
        entry_rows(rows, tag, p, r, so, att, extra)
    elif g == 'V':
        v_rows(rows, tag, p, r, so, att, extra)
    else:
        w_rows(rows, tag, r, so, att, extra)
    return rows, dict(tag=tag, group=g, level=lv, log_sha256=r['sha256'], stdout_sha256=so['sha256'], extra=extra)


def capture_rows(rows, tag, p, r, so, att, extra):
    """A capture tag (item 569 (d)(3)): entry, 0 deaths, canon_mismatch 0, dropped_queue 0, offline R_ADDR 0, generation file on disk;
    from the second tag compat=ok, generation = replay.cur of the previous tag, catalogue_sources / catalogue_specs not decreasing."""
    spec = SPEC[tag]
    lv = spec['level']
    rows.a('capture fitness: line PipelinePrecache: no <path> yet (empty capture folder, item 532 (v))', len(r['precache_no']) >= 1,
           r['precache_no'][:2])
    rows.m('CAP entered (Level has started: %s, outcome ok)' % lv, entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('CAP the process lived to the end of the hold (%d s)' % spec['hold'], lived(att, spec['hold']),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    rows.m('CAP 0 death markers (log, stdout)', deaths(r, so) == 0, deaths(r, so))
    rows.m('CAP translation cache directory = %s (signature of KYTY_FIX_F19=0)' % DIR0, directory_ok(r, DIR0), r['stc'][:2])
    md = r['mode'][0][1] if r['mode'] else {}
    lc = last_capture(r)
    g_c, gf, cat, cerr = catalogue_of(tag)
    prev = None
    if spec['prev'] is not None:
        pj = read_json_of(spec['prev']) or {}
        pe = pj.get('extra') or {}
        prev = dict(cur=pe.get('replay_cur'), cs=pe.get('catalogue_sources'), cp=pe.get('catalogue_specs'))
    acc = accumulation(tag, md, lc, g_c, cat is not None, prev)
    names = dict(mode='CAP accumulation: mode line mode=2 and %s' % ('compat=absent generation=0 (first tag)' if prev is None else
                                                                     'compat=ok, generation = replay.cur of %s' % spec['prev']),
                 ondisk='CAP accumulation: generation file on disk = gen of the last capture at=stop line and readable',
                 nondec='CAP accumulation: catalogue_sources and catalogue_specs not decreasing against %s' % spec['prev'])
    for k, ok, det in acc:
        rows.m(names[k], ok, det)
    if lc is None:
        for nm in ('canon_mismatch = 0', 'dropped_queue = 0', 'catalogue_sources > 0 and catalogue_specs > 0', 'offline R_ADDR = 0'):
            rows.m('CAP %s (no capture at=stop line - not determined)' % nm, None)
    else:
        cm = num(lc, 'canon_mismatch')
        rows.m('CAP canon_mismatch = 0 (canon_self + canon_residual)', cm == 0, 'canon_mismatch %s self %s residual %s' % (
            cm, lc.get('canon_self'), lc.get('canon_residual')))
        dq = num(lc, 'dropped_queue')
        rows.m('CAP dropped_queue = 0 (read at a soft close, item 532 (z) N4)', (dq == 0) if soft_close(att) else None,
               'dropped_queue %s soft close %s' % (dq, soft_close(att)))
        rows.m('CAP catalogue_sources > 0 and catalogue_specs > 0', (num(lc, 'catalogue_sources') or 0) > 0 and
               (num(lc, 'catalogue_specs') or 0) > 0, '%s / %s' % (lc.get('catalogue_sources'), lc.get('catalogue_specs')))
        rows.m('CAP offline R_ADDR = 0 ("the role layout agrees", item 532 (e))', None if cat is None else cat['R_ADDR'] == 0,
               None if cat is None else cat['R_ADDR'])
        rows.r('this start: sources specs pipes canon_base canon_big pipes_waiting', ' '.join(str(lc.get(k)) for k in (
            'sources', 'specs', 'pipes', 'canon_base', 'canon_big', 'pipes_waiting')))
        rows.r('catalogue after the tag: sources / specs / pipes', '%s / %s / %s' % (
            lc.get('catalogue_sources'), lc.get('catalogue_specs'), lc.get('catalogue_pipes')))
        extra.update(catalogue_sources=num(lc, 'catalogue_sources'), catalogue_specs=num(lc, 'catalogue_specs'),
                     catalogue_pipes=num(lc, 'catalogue_pipes'), pipes_waiting=num(lc, 'pipes_waiting'))
    rows.r('mode line', md)
    rows.r('capture lines (save / stop)', '%d / %d' % (sum(1 for _, d in r['capture'] if d.get('at') == 'save'),
                                                      sum(1 for _, d in r['capture'] if d.get('at') == 'stop')))
    rows.r('capture reject lines logged by kind', reject_summary(r['reject']))
    rows.r('shader resource specialization failed in _kyty.txt / stdout', '%d / %d' % (r['specfail'], so['specfail']))
    rows.r('saved catalogue', 'replay.cur %s file %s error %s' % (g_c, gf and os.path.basename(gf), cerr))
    rows.r('shown hold after the first scene frame (reference)', '%.1f s, first scene frame n=%s' % (r['hold_us'] / 1e6, r['first_scene_n']))
    if cat is not None:
        rows.r('catalogue file: sources / specs / pipes / words / keep / programs', '%d %d %d %d %d %d' % (
            cat['sources'], cat['specs'], cat['pipes'], cat['words'], cat['keep'], len(cat['src_hashes'])))
        extra['catalogue_programs'] = len(cat['src_hashes'])
    extra['replay_cur'] = g_c
    word = acc_word([x for x in acc])
    rows.lines.append('ACCUMULATION %s %s' % (tag, word))
    extra['accumulation'] = word
    if prev is None:
        sg = signature_ok(r, SIG0)
        rows.m('CAP signature line = %s (item 571 (g)(3), the KYTY_FIX_F19=0 string of the first tag; executor reading, seal section 4)' %
               SIG0, sg, r['sig'][:2])
        rows.lines.append('SIGNATURE_571G3 %s %s' % (tag, 'OK' if sg else 'BREACH'))


def stop_rows(rows, r, so, att, sout, extra):
    """s18_ks (item 576 (e)(2)): the members of item 566 (v) on the S18a2 binary; the signature line of KYTY_FIX_F19=1 (item 571 (g)(3))."""
    md = r['mode'][0][1] if r['mode'] else {}
    g_c = (read_json_of(LAST_CAP) or {}).get('extra', {}).get('replay_cur')
    rows.m('KS mode line mode=3 compat=ok generation = replay.cur of %s' % LAST_CAP, md.get('mode') == '3' and md.get('compat') == 'ok' and
           g_c is not None and num(md, 'generation') == g_c, '%s / %s' % (md, g_c))
    f = stop_facts(r)
    ec = exit_code(att)
    ok, det = close_path(f, ec)
    rows.m('KS the break by the real close path: applied -> close requested precache_active=1 -> stand stop seen -> rebuild '
           'pipelines_bin=stopped -> close joined, one P < R, 0 timeout, 0 Event: quit, exit code 0 (item 566 (v))', ok, det)
    sl = f['applied'][0] if f['applied'] else None
    rows.m('KS sign of the break: rebuild ... pipelines_bin=stopped after stand stop applied (item 532 (b))', None if sl is None else
           (f['stopped'] is not None and f['stopped'][0] > sl), 'stand line %s stopped line %s' % (sl, f['stopped'] and f['stopped'][0]))
    f19 = (sout or {}).get('f19', {})
    rows.m('KS pipelines.bin is not written at the break (state_out.txt, %s)' % DIR1, None if sout is None else
           f19.get('pipelines_bin') is not True, f19)
    rows.m('KS 0 death markers', deaths(r, so) == 0, deaths(r, so))
    sg = signature_ok(r, SIG1)
    rows.m('KS signature line = %s (item 571 (g)(3), the first KYTY_FIX_F19=1 tag)' % SIG1, sg, r['sig'][:2])
    rows.lines.append('SIGNATURE_571G3 s18_ks %s' % ('OK' if sg else 'BREACH'))
    sd = f['stopped'][1] if f['stopped'] else {}
    rows.r('stopped rebuild line', dict((k, sd.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                                 'pipelines_bin')))
    rows.r('waited_ms of stand stop seen / wait_ms of close stop joined', '%s / %s' % (f['seen'] and f['seen'][1].get('waited_ms'),
                                                                                    f['joined'] and f['joined'][1].get('wait_ms')))
    rows.r('no startup wait line (the close path)', r['prep_line'] is None)
    extra['ks'] = dict(timeout=f['timeout'], seen=f['seen'] is not None, a=num(sd, 'perms_new'), records=num(sd, 'records'))


def rebuild_rows(rows, tag, p, r, so, att, extra):
    """s18_r (item 569 (d)(4)): the rebuild at the default from the catalogue into an empty _fixf19."""
    md = r['mode'][0][1] if r['mode'] else {}
    cj = read_json_of(LAST_CAP) or {}
    g_c = (cj.get('extra') or {}).get('replay_cur')
    rows.m('R mode line mode=3 compat=ok generation = replay.cur of %s (the default 3)' % LAST_CAP, md.get('mode') == '3' and
           md.get('compat') == 'ok' and g_c is not None and num(md, 'generation') == g_c, '%s / %s' % (md, g_c))
    rows.m('R translation cache directory = %s (the default signature)' % DIR1, directory_ok(r, DIR1), r['stc'][:2])
    rb = r['rebuild'][-1][1] if r['rebuild'] else None
    rows.m('R a rebuild line and no rebuild skipped line', rb is not None and not r['skipped'], 'rebuild %d skipped %s' % (
        len(r['rebuild']), r['skipped'][:1]))
    rows.m('R 0 death markers', deaths(r, so) == 0, (r['death'] + so['death'])[:3])
    rows.m('R the process reached the end of the preparation screen (--until-prep outcome prep)', att.get('outcome') == 'prep',
           att.get('outcome'))
    rb = rb or {}
    rows.m('R pipelines_bin=written', rb.get('pipelines_bin') == 'written', rb.get('pipelines_bin'))
    recs, prep, rej, pend = num(rb, 'records'), num(rb, 'prepared'), num(rb, 'rejected'), num(rb, 'pending')
    ident = None if None in (recs, prep, rej, pend) else prep + rej + pend == recs
    rows.m('R identity prepared + rejected + pending = records', ident, '%s + %s + %s = %s' % (prep, rej, pend, recs))
    parts = [num(rb, k) for k in ('rej_src', 'rej_fused', 'rej_key', 'rej_version', 'rej_shape', 'rej_translate', 'rej_emit', 'rej_val',
                                  'rej_write', 'rej_ref')]
    part = None if None in parts or rej is None else sum(parts) == rej
    rows.m('R partition of the reasons: sum rej_* (rej_ref included) = rejected', part, '%s = %s' % (parts, rej))
    share = None if (prep is None or not recs) else prep / float(recs)
    rows.m('R share prepared / records >= 0.90 (item 569 (d)(4))', None if share is None else share >= SHARE_MIN,
           'share %s = %s / %s' % (None if share is None else round(share, 4), prep, recs))
    rows.m('R preparation screen <= 180 s (startup wait finished; item 229 (d)(2))', None if r['prep'] is None else r['prep'] <= PREP_MAX_MS,
           '%s ms' % r['prep'])
    pw = (cj.get('extra') or {}).get('pipes_waiting')
    alt = None if (prep is None or recs is None or pw is None or recs + pw == 0) else round(prep / float(recs + pw), 4)
    rows.r('share prepared / (records + pipes_waiting of %s) (edition 4 form, reference)' % LAST_CAP, '%s (pipes_waiting %s)' % (alt, pw))
    rows.r('records vs catalogue pipes of %s' % LAST_CAP, '%s / %s' % (recs, (cj.get('extra') or {}).get('catalogue_pipes')))
    for k in ('pending', 'rej_ref', 'perms_new', 'perms_cached', 'rb_push_moved', 'rb_spec_changed', 'translate_ms', 'wall_ms'):
        rows.r(k, rb.get(k))
    extra['rebuild'] = dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                     'pipelines_bin'))
    extra['prep_ms'] = r['prep']


def entry_rows(rows, tag, p, r, so, att, extra):
    """s18_e1 / s18_e2 (item 569 (d)(4)): first entries after s18_r at the default without a cache return between them."""
    spec = SPEC[tag]
    lv = spec['level']
    md = r['mode'][0][1] if r['mode'] else {}
    rows.m('E mode line mode=3 compat=ok (the default 3)', md.get('mode') == '3' and md.get('compat') == 'ok', md)
    sk = [x for x in r['skipped'] if x[1] == 'recipes_current']
    rows.m('E line rebuild skipped reason=recipes_current and no rebuild line', len(sk) >= 1 and not r['rebuild'],
           'skipped %s rebuild lines %d' % (r['skipped'][:2], len(r['rebuild'])))
    rows.m('E translation cache directory = %s' % DIR1, directory_ok(r, DIR1), r['stc'][:2])
    scene_rows(rows, r, so, att, spec['hold'], 'E', lv)
    video_rows(rows, p, r, so, 'E')
    _g, _f, cat, cerr = catalogue_of(LAST_CAP)
    n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
    rows.m('E translations in the game of programs of the replay catalogue (%s) = 0 (after the preparation line)' % LAST_CAP,
           None if n_cat is None else n_cat == 0, 'catalogue programs %s of new permutations %s after line %s; %s' % (
               n_cat, n_all, r['prep_line'], cerr))
    rows.r('translations of other programs after the preparation line (reference)', None if n_cat is None else n_all - n_cat)
    rows.r('new permutations before the preparation line', sum(1 for x in r['av'] if r['prep_line'] and x[0] < r['prep_line']))
    extra['catalogue_translations'] = n_cat


def v_rows(rows, tag, p, r, so, att, extra):
    """s18_v (item 569 (d)(4)): V Sky Garden at the default on the installed caches plus the catalogue; the seal names the line
    rebuild skipped reason=recipes_current (the installed _fixf19/pipelines.bin carries the current recipe signature); a rebuild instead
    passes the line member only with a preparation screen <= 180 s."""
    spec = SPEC[tag]
    md = r['mode'][0][1] if r['mode'] else {}
    rows.m('V mode line mode=3 compat=ok (the default 3)', md.get('mode') == '3' and md.get('compat') == 'ok', md)
    sk = [x for x in r['skipped'] if x[1] == 'recipes_current']
    if sk and not r['rebuild']:
        ok, det = True, 'named: rebuild skipped reason=recipes_current'
    elif r['rebuild'] and not r['skipped']:
        ok = None if r['prep'] is None else r['prep'] <= PREP_MAX_MS
        det = 'NOT the named line: a rebuild, preparation screen %s ms' % r['prep']
    else:
        ok, det = False, 'skipped %s rebuild lines %d' % (r['skipped'][:2], len(r['rebuild']))
    rows.m('V line rebuild skipped reason=recipes_current (named by the seal), or a rebuild with a preparation screen <= 180 s', ok, det)
    rows.m('V translation cache directory = %s' % DIR1, directory_ok(r, DIR1), r['stc'][:2])
    scene_rows(rows, r, so, att, spec['hold'], 'V', spec['level'])
    video_rows(rows, p, r, so, 'V')


def w_rows(rows, tag, r, so, att, extra):
    """s18_w (item 569 (d)(4)): W at the default; the rebuild of an empty _fixf19 from the catalogue runs under the layer (seal section 2)."""
    spec = SPEC[tag]
    rows.m('W entered (Level has started: %s, outcome ok)' % spec['level'], entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('W the process lived to the end of the hold (%d s)' % spec['hold'], lived(att, spec['hold']),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    rows.m('W 0 [Vulkan][E]', r['vke'] == 0, r['vke'])
    dual_before = [x for x in r['dual'] if r['first_guest'] is not None and x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]
    rows.m('W positive control of the layer: [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut',
           r['vkw'] > 0 and len(dual_before) >= 1, 'W %d, dual %s, first GuestOut %s' % (r['vkw'], r['dual'][:2], r['first_guest']))
    rb = r['rebuild'][-1][1] if r['rebuild'] else {}
    rows.r('rebuild line under the layer (records prepared pipelines_bin)', '%s %s %s; skipped %s' % (
        rb.get('records'), rb.get('prepared'), rb.get('pipelines_bin'), r['skipped'][:1]))
    rows.r('limit lines of the layer', r['vk_limit'])
    rows.r('death markers (W)', deaths(r, so))
    rows.r('frames >= 1 s after the first scene frame (W, reference)', r['k2_after'])


# ----------------------------------------------------------------------------------------------------------------- output

def print_rows(tag, rows, meta):
    print('S18c reader tag %s group %s level %s' % (tag, meta['group'], meta['level']))
    print('  log sha256 %s stdout sha256 %s' % (meta['log_sha256'], meta['stdout_sha256']))
    for title, lst in (('ADMISSION', rows.adm), ('FORM', rows.form), ('MEMBERS', rows.mem)):
        print('  %s' % title)
        for name, ok, det in lst:
            print('    %-15s %s | %s' % (yn(ok), asc(name), det[:400]))
    print('  REPORT')
    for name, det in rows.rep:
        print('    %s: %s' % (asc(name), det[:400]))
    for x in rows.lines:
        print('  %s' % x)
    print('  READING %s' % rows.word())


def to_json(tag, rows, meta):
    return dict(meta, reading=rows.word(), admission=[list(x) for x in rows.adm], form=[list(x) for x in rows.form],
                members=[list(x) for x in rows.mem], report=[list(x) for x in rows.rep], lines=list(rows.lines))


def table():
    print('S18c member table, seal docs/track-s/s18c.md (no verdict - S18d HPP-645)')
    print('  item 569 (d)(5) members (1)-(2): S18a ACCEPTED item 573, S18a2 ACCEPTED item 578 (KytyPS5 03e7ab2d), S18b ACCEPTED item 576 '
          '(PASS_WITH_FIXES, RC1 by code), S18b2 ACCEPTED item 579 (PASS, RC 0; KytyPS5 abd476c6)')
    for tag in ORDER:
        d = read_json_of(tag)
        if d is None:
            print('  %-8s %-4s NOT READ' % (tag, SPEC[tag]['group']))
            continue
        print('  %-8s %-4s %-28s READING %s %s' % (tag, SPEC[tag]['group'], SPEC[tag]['level'], d['reading'], ' '.join(d.get('lines') or [])))
        for name, ok, det in d['members']:
            print('      %-15s %s | %s' % (yn(ok), asc(name), asc(det)[:200]))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--table':
        return table()
    tag = argv[0]
    rows, meta = read_tag(tag)
    print_rows(tag, rows, meta)
    if '--json' in argv:
        out = argv[argv.index('--json') + 1]
        with open(out, 'w') as f:
            json.dump(to_json(tag, rows, meta), f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
