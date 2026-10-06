"""Track S link S17c (HPP-613; ROADMAP s122 item 524 (z) K2(2)-K6, items 531 (v)(d), 532 (b)-(zh), 533 (b)(g), 536 (b)(v), 537 (e)(zh),
541 (b)(g), 548 (b)(v)): the reader of the S-replay tags, seal edition 3 - binary S17a4 ed2686da (code 9238a182); the K2(2) tags s17c_v0 and
s17c_w0 were made on S17a2 2b5e2ce6 (code a2fee0d9) under edition 2 and are carried without a repeat (item 548 (b)), read by the rules of
edition 2.  Rows and a READING word per tag, the member table K2(2)-K6 over the tags; NO verdict (the lead's, S17d HPP-614).  Definitions -
seal docs/track-s/s17c.md section 4 (= pred/s17c_seal.md).  Raw word values of reject lines never reach the output (item 548 (v)(2)).
usage: python s17c_read.py <tag> [--json <out>]       read one made tag (runs/<tag>, log_<tag>.txt, <tag>.json, state/...)
       python s17c_read.py --table                   the member table K2(2)-K6 from runs/<tag>/read.json of every tag
       python s17c_read.py --stop537                 exit 0 'STOP537 GO' / 1 'STOP537 STOP': item 537 (zh), canon_mismatch of s17c_c2 = 0
       python s17c_read.py --catalogue <replay.<g>.bin>   offline rows of a catalogue (R_ADDR, KEEP >= 0x10000, sources)
       python s17c_read.py --k4x <live folder> <rebuilt folder> <manifest> [--stand <file> <index>]   the K4 comparison alone
  Every path is under ROOT (default C:/kyty/s288/s17c; the fixtures set S17C_ROOT, S17C_SEAL, S17C_BIN).  ASCII output only.
READING  NOT_ADMITTED (admission row NO: interference of the run, a repeat only by a lead item, item 273 (z)) -> FORM_FAIL (installed binary
         or manifest after the return) -> MEMBERS_FAIL (a member NO) -> NOT_EVALUABLE (a member not determined) -> MEMBERS_PASS.
         REPORT rows never change the word."""
import hashlib
import json
import os
import re
import struct
import sys

import xxhash

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc_s17c  # noqa: E402
import state_s17c  # noqa: E402

ROOT = os.environ.get('S17C_ROOT', 'C:/kyty/s288/s17c')
SEAL_PATH = os.environ.get('S17C_SEAL', 'C:/kyty/s288/s17c/pred/s17c_seal.md')
BIN_PATH = os.environ.get('S17C_BIN', 'C:/kyty/s288/bin/kyty_emulator_ed2686da.exe')
BIN_EXPECT = 'ed2686da6fc959b1b4f0f308a9cbd1bae20a2e97750b5823df70ccb8c8f41d5b'
VERSION = b'KytyPS5-2026-09-15-6a2987a-2336-g9238a182'
REV = '9238a18'
FS6 = '9325446cdd3c960b83474125dbb38164390c857c998c3ccc856d5f30bf7360f2'
FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
INSTALLED_OK = (FS8,)     # edition 3: the installed binary at the print (items 545, 547)
# K2(2) carried from edition 2 (items 537 (e), 548 (b)): binary, version, revision, seal file and installed set of edition 2.
CARRIED = ('s17c_v0', 's17c_w0')
BIN_PATH_ED2 = os.environ.get('S17C_BIN_ED2', 'C:/kyty/s288/bin/kyty_emulator_2b5e2ce6.exe')
BIN_EXPECT_ED2 = '2b5e2ce677c557bb0dd28ccc114588aea5c4b6f56c10ab1450faadd81328d544'
VERSION_ED2 = b'KytyPS5-2026-09-15-6a2987a-2311-ga2fee0d9'
REV_ED2 = 'a2fee0d'
SEAL_PATH_ED2 = os.environ.get('S17C_SEAL_ED2', 'C:/kyty/s288/s17c/pred/s17c_seal_ed2.md')
INSTALLED_OK_ED2 = (FS6, FS8)
REJECT_KINDS = ('self', 'residual', 'base', 'big')
SIG1 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19'   # KYTY_FIX_F19=1 (rebuild)
SIG0 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10'          # KYTY_FIX_F19=0 (capture)
DIR1 = 'variant_fixb26_fixb1b_fixf10_fixf19'
DIR0 = 'variant_fixb26_fixb1b_fixf10'
SKY = 'underwater_aerial_garden'
LIMIT = '100000000'
SHARE_MIN = 0.90          # item 524 (z) K4, item 531 (v)(3)
HIT_MIN = 0.90            # item 524 (z) K4 (RC2), item 532 (zh)
PREP_MAX_MS = 180000      # item 524 (z) K5, item 229 (d)(2)
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000
K2_US = 1000000
KEEP_BIG = 0x10000        # item 532 (e) RC5 reference row
ORDER = ('s17c_v0', 's17c_w0', 's17c_c2', 's17c_ca', 's17c_cc', 's17c_n0', 's17c_r3', 's17c_rs', 's17c_e3', 's17c_ew', 's17c_ks',
         's17c_kn', 's17c_kc')
BASE_ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1', 'KYTY_GPU_CLOCK_PIN': '1',
            'KYTY_GPU_MARKERS': '0', 'KYTY_GUEST_ARGS': '-lvl ' + SKY}
PATH_KEYS = ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE', 'KYTY_REC')
SPEC = {
    's17c_v0': dict(form='v', hold=330, state='installed', env={'KYTY_S_REPLAY': '0'}),
    's17c_w0': dict(form='w', hold=310, state='installed', env={'KYTY_S_REPLAY': '0'}),
    's17c_c2': dict(form='v', hold=330, state='empty_f10', env={'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0'}),
    's17c_ca': dict(form='n', hold=120, state='empty_f10', env={'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0', 'KYTY_S_REPLAY_TEST': 'addr'}),
    's17c_cc': dict(form='n', hold=120, state='empty_f10', env={'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0', 'KYTY_S_REPLAY_TEST': 'canon'}),
    's17c_n0': dict(form='v', hold=330, state='empty_f19', env={'KYTY_S_REPLAY': '0', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'}),
    's17c_r3': dict(form='p', hold=0, state='cat_c2', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'}),
    's17c_rs': dict(form='p', hold=0, state='cat_c2', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1',
                                                          'KYTY_S_REPLAY_TEST': 'spec'}),
    's17c_e3': dict(form='v', hold=330, state='rb_r3', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'}),
    's17c_ew': dict(form='w', hold=310, state='rb_r3', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1'}),
    's17c_ks': dict(form='p', hold=0, state='cat_c2', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1',
                                                          'KYTY_S_REPLAY_TEST': 'stop'}),
    's17c_kn': dict(form='n', hold=60, state='k_ks', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'}),
    's17c_kc': dict(form='n', hold=60, state='cat_c2', env={'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1',
                                                          'KYTY_S_REPLAY_TEST': 'corrupt'}),
}
STATE_SRC = {'cat_c2': 's17c_c2', 'rb_r3': 's17c_r3', 'k_ks': 's17c_ks'}
GROUP = {'s17c_v0': 'K2(2)', 's17c_w0': 'K2(2)', 's17c_c2': 'K3', 's17c_ca': 'K3', 's17c_cc': 'K3', 's17c_n0': 'K4/K5',
         's17c_r3': 'K4', 's17c_rs': 'K4', 's17c_e3': 'K5', 's17c_ew': 'K5', 's17c_ks': 'K6', 's17c_kn': 'K6', 's17c_kc': 'K6'}

RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_AV = re.compile(rb'AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=')
RX_KV = re.compile(rb'([a-z_]+)=([^ \r\n]*)')
RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_CULPRIT = re.compile(r'culprit=(\d+):role(\d+):([0-9a-f]{8})->([0-9a-f]{8})')
RX_CULPRIT_RES = re.compile(r'culprit=(\d+):role(\d+)(?![0-9:])')
RX_WHY = re.compile(r'^capture reject why=(.*?) hash=(0x[0-9a-fA-F]+) words=(\d+)$')
RX_ROW = re.compile(r'((?:vs|ps|cs)_[0-9a-f]{16}_[0-9a-f]{16}\.bin)\t(\d+)\t([0-9a-f]{16})\t(\d+)\t([0-9a-f]{16})$')
M_SR = b'ShaderReplay:'
M_GUEST = b'GuestOut:'
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
M_SPECFAIL = b'shader resource specialization failed'
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


def edition(tag):
    """(name, binary sha256, binary copy, version, revision, seal file, installed set) of the tag: edition 2 for the carried K2(2) tags."""
    if tag in CARRIED:
        return ('S17a2 2b5e2ce6 (K2(2) carried from edition 2, item 548 (b))', BIN_EXPECT_ED2, BIN_PATH_ED2, VERSION_ED2, REV_ED2,
                SEAL_PATH_ED2, INSTALLED_OK_ED2)
    return ('S17a4 ed2686da', BIN_EXPECT, BIN_PATH, VERSION, REV, SEAL_PATH, INSTALLED_OK)


def reject_parse(body):
    """A 'capture reject why=<why> hash=<h> words=<n>' line -> dict.  kind = the first word of why ('?' when not [a-z_]+ or no why); the
    fields branch (addr|exact), ok, complete, n (digits); culprit <i> and role <r>; canon_zero = 1 when the self culprit goes to 00000000.
    Raw word values are read only into canon_zero and never returned (item 548 (v)(2))."""
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


def reject_clean(body):
    """The committed form of a reject line - kind, branch, ok, complete, culprit <i>:role<r>, canon_zero, n, hash, words; no raw values."""
    d = reject_parse(body)
    out = ['why=%s' % d['kind']]
    for k in ('branch', 'ok', 'complete'):
        if d[k] is not None:
            out.append('%s=%s' % (k, d[k]))
    if d['culprit'] is not None:
        out.append('culprit=%s:role%s' % (d['culprit'], d['role']))
    if d['canon_zero'] is not None:
        out.append('canon_zero=%d' % d['canon_zero'])
    if d['n'] is not None:
        out.append('n=%s' % d['n'])
    out.append('hash=%s words=%s' % (d['hash'], d['words']))
    return ' '.join(out)


def reject_summary(rejects):
    """(lines by kind, residual 'branch:role<r>' of the first culprit by count) of the logged reject lines (reference, item 541 (g))."""
    kinds, res = {}, {}
    for _, body in rejects:
        d = reject_parse(body)
        k = d['kind'] if d['kind'] in REJECT_KINDS else 'other'
        kinds[k] = kinds.get(k, 0) + 1
        if d['kind'] == 'residual':
            key = '%s:role%s' % (d['branch'] or 'none', d['role'] if d['role'] is not None else '-')
            res[key] = res.get(key, 0) + 1
    return dict(sorted(kinds.items())), dict(sorted(res.items()))


def paths(tag):
    d = os.path.join(ROOT, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in ('installed_sha', 'installed_before', 'installed_after', 'manifest_cmp', 'glitch',
                                                       'sheet', 'state_in', 'state_out', 'state_in_name'))
    p.update(dir=d, log=os.path.join(ROOT, 'log_%s.txt' % tag), stdout=os.path.join(ROOT, 'stdout_%s.txt' % tag),
             run=os.path.join(ROOT, '%s.json' % tag), idx=os.path.join(ROOT, 'rec_%s.mp4.idx' % tag),
             state=os.path.join(ROOT, 'state', tag), readjson=os.path.join(d, 'read.json'))
    return p


# ----------------------------------------------------------------------------------------------------------------- log scan

def scan(log_path):
    """One streaming pass over the emulator log; every row the members need."""
    r = dict(lines=0, sha256=None, sr=0, mode=[], capture=[], reject=[], stand=[], rebuild=[], rebuild_src=[], rebuild_spec=[],
             skipped=[], hits=[], close_req=[], close_joined=[], precache_no=[], prep=None, prep_line=None, stc=[], av=[],
             first_guest=None, entry_line=None, scene_change_line=None, first_scene_n=None, hold_us=0, k2_after=0, ft_rows=0,
             death=[], vke=0, vkw=0, vk_limit=0, dual=[], skipped_draw=0, win={}, recovering=0, gamepatch=0, specfail=0, rev=[])
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
                elif body.startswith(b'rebuild-src '):
                    r['rebuild_src'].append((ln, d))
                elif body.startswith(b'rebuild-spec '):
                    r['rebuild_spec'].append((ln, d))
                elif body.startswith(b'rebuild '):
                    r['rebuild'].append((ln, d))
                elif body.startswith(b'hits '):
                    r['hits'].append((ln, d))
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
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('log', ln, rv))
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == SKY:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['first_guest'] is None and M_GUEST in raw:
                r['first_guest'] = ln
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
    r = dict(present=False, death=[], sr=0, specfail=0, rev=[], sha256=None)
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
    """Offline rows of one generation file: the r_addr.py scan (layout of the ShaderReplayLayout line of S17a2) plus the program
    hashes of R-SRC and the KEEP words >= 0x10000 (item 532 (e)).  Raises ValueError on a malformed file."""
    import r_addr
    data = open(path, 'rb').read()
    base = r_addr.scan(data)
    L = r_addr.LAYOUT
    compat_size = struct.unpack_from('<I', data, L['file.compat_size'])[0]
    compat = data[L['file']:L['file'] + compat_size].decode('ascii', 'replace')
    pos = L['file'] + compat_size
    generation, _checksum, n_src, n_spec, _n_pipe = struct.unpack_from('<QQIII', data, pos)
    pos += L['body']
    hashes = []
    for _ in range(n_src):
        hashes.append(struct.unpack_from('<Q', data, pos + L['src.hash'])[0])
        sw, cw, bw = struct.unpack_from('<III', data, pos + L['src.static_words'])
        pos += L['src'] + 4 * (sw + cw + bw)
    keep_big = 0
    spec_ids = []
    for _ in range(n_spec):
        spec_ids.append(struct.unpack_from('<Q', data, pos + L['spec.spec_id'])[0])
        (n_words,) = struct.unpack_from('<I', data, pos + L['spec.words'])
        pos += L['spec']
        for k in range(n_words):
            at = pos + k * L['word']
            if data[at + L['word.role']] == 0 and struct.unpack_from('<I', data, at + L['word.value'])[0] >= KEEP_BIG:
                keep_big += 1
        pos += n_words * L['word']
    base.update(compat=compat, src_hashes=sorted(set(hashes)), keep_big=keep_big, spec_ids=spec_ids)
    return base


def catalogue_of(tag):
    """(generation number of replay.cur, path of its file, catalogue dict or None, error) of the saved state of a tag."""
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


# ----------------------------------------------------------------------------------------------------------------- K4 comparison

def read_manifest(path):
    """rebuild_manifest.tsv -> (header signature or None, rows [(file, index, spec_hash, start, xxh)], bad lines).  Accepts the header
    with its newline (S17a2) and the old form whose first data row follows the signature on the header line (item 532 (g)); blank
    lines and CR are skipped."""
    sig, rows, bad = None, [], 0
    data = open(path, 'rb').read().decode('ascii', 'replace')
    for line in data.split('\n'):
        line = line.rstrip('\r')
        if not line:
            continue
        if line.startswith('#'):
            rest = line.split(' signature ', 1)[1] if ' signature ' in line else ''
            m = RX_ROW.search(rest)
            if m:
                sig = rest[:m.start()]
                rows.append((m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5)))
            else:
                sig = rest
            continue
        m = RX_ROW.match(line)
        if m:
            rows.append((m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5)))
        else:
            bad += 1
    return sig, rows, bad


def k4x(live_dir, rb_dir, manifest_path, stand=None):
    """The comparison of K4 (item 524 (z), RC2; item 531 (d)(8); item 532 (d)(b), (zh)).  A permutation is the key (cache file name,
    the bytes of its specialization, its push-data start).  live_perms = distinct keys of the live folder (cold =0 of the same signature);
    rebuilt = the keys of the manifest rows (file, index -> that permutation of the rebuilt folder); rb_hit = live keys among rebuilt;
    rb_dead = rebuilt keys not live; rb_live_mismatch = rb_hit keys whose SPIR-V XXH3 differ.  Self-checks: every manifest row finds its
    permutation and its start and XXH3 equal the manifest (manifest_bad), every file parses (live_bad, rb_bad), signatures."""
    out = dict(ok=False, error=None)
    if not (os.path.isdir(live_dir) and os.path.isdir(rb_dir) and os.path.isfile(manifest_path)):
        out['error'] = 'input missing: live %s rebuilt %s manifest %s' % (os.path.isdir(live_dir), os.path.isdir(rb_dir),
                                                                         os.path.isfile(manifest_path))
        return out
    live, live_bad = tc_s17c.read_folder(live_dir)
    rb, rb_bad = tc_s17c.read_folder(rb_dir)
    sig, rows, mbad = read_manifest(manifest_path)
    live_keys = {}
    dup = 0
    for name, f in live.items():
        for p in f['perms']:
            k = (name, p['spec'], p['start'])
            if k in live_keys:
                dup += 1
            live_keys[k] = p['spirv_xxh3']
    rb_keys = {}
    manifest_bad = 0
    row_key = {}
    for (name, index, _sh, start, xxh) in rows:
        f = rb.get(name)
        if f is None or index >= len(f['perms']):
            manifest_bad += 1
            continue
        p = f['perms'][index]
        if p['start'] != start or ('%016x' % p['spirv_xxh3']) != xxh:
            manifest_bad += 1
        k = (name, p['spec'], p['start'])
        rb_keys[k] = p['spirv_xxh3']
        row_key[(name, index)] = k
    hit = [k for k in live_keys if k in rb_keys]
    mism = [k for k in hit if live_keys[k] != rb_keys[k]]
    out.update(ok=True, live_files=len(live), live_perms=len(live_keys), live_dup=dup, live_bad=len(live_bad), rb_files=len(rb),
               rb_bad=len(rb_bad), manifest_rows=len(rows), manifest_bad_lines=mbad, manifest_bad=manifest_bad, rebuilt=len(rb_keys),
               rb_hit=len(hit), rb_dead=len([k for k in rb_keys if k not in live_keys]), rb_live_mismatch=len(mism),
               manifest_sig=sig, live_sigs=sorted(set(f['signature'] for f in live.values())),
               rb_sigs=sorted(set(f['signature'] for f in rb.values())),
               hit_share=(len(hit) / len(live_keys)) if live_keys else None)
    if stand is not None:
        try:
            sk = row_key.get((stand[0], int(stand[1])))
        except (TypeError, ValueError):
            sk = None
        out['stand_in_manifest'] = sk is not None
        out['stand_in_live'] = sk is not None and sk in live_keys
        out['stand_mismatch'] = sk is not None and sk in live_keys and live_keys[sk] != rb_keys[sk]
    return out


# ----------------------------------------------------------------------------------------------------------------- members

class Rows:
    def __init__(self):
        self.adm, self.form, self.mem, self.rep = [], [], [], []

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


def env_rows(rows, tag, run):
    spec = SPEC[tag]
    env = (run or {}).get('env') or {}
    want = dict(BASE_ENV)
    want.update(spec['env'])
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
    elif vk:
        bad.append('VK_LAYER_* %s' % sorted(vk))
    rows.a('environment = the form of the tag (seal section 3; KYTY_SHADER_PREPARE absent - item 536 (v) N1)', not bad,
           'offending %s' % bad if bad else 'KYTY keys %s' % sorted(kyty))
    val = None
    cmd = (run or {}).get('cmdline') or []
    for i, x in enumerate(cmd):
        if x == '--vulkan-validation':
            val = cmd[i + 1] if i + 1 < len(cmd) else None
    want_val = 'true' if spec['form'] == 'w' else 'false'
    rows.a('command line --vulkan-validation (last) = %s' % want_val, val == want_val, val)


def state_rows(rows, tag, p, sin):
    """The input state of the tag (state_in.txt) against its name (seal section 3)."""
    spec = SPEC[tag]
    name = first_line(text(p['state_in_name']))
    rows.a('input state name = %s' % spec['state'], name == spec['state'], name)
    if sin is None:
        rows.a('input state described (state_in.txt)', False, 'missing')
        return
    st = spec['state']
    f10, f19, rp = sin.get('f10', {}), sin.get('f19', {}), sin.get('replay', {})
    if st == 'installed':
        rows.a('input state installed: no replay folder before the tag', rp.get('present') is False, rp)
    elif st == 'empty_f10':
        ok = f10.get('present') is False and rp.get('present') is False
        rows.a('input state empty_f10: %s absent (so no pipelines.bin, item 532 (v)) and replay absent' % DIR0, ok, (f10, rp))
    elif st == 'empty_f19':
        rows.a('input state empty_f19: %s absent and replay absent' % DIR1, f19.get('present') is False and rp.get('present') is False,
               (f19, rp))
    else:
        src = STATE_SRC[st]
        saved = os.path.join(paths(src)['state'], 'replay')
        want = {}
        if os.path.isdir(saved):
            for n in sorted(os.listdir(saved)):
                fp = os.path.join(saved, n)
                if os.path.isfile(fp):
                    want[n] = (os.path.getsize(fp), sha_file(fp))
        same = rp.get('present') is True and rp.get('replay_files') == want and len(want) > 0
        rows.a('input state %s: replay = state/%s/replay byte for byte' % (st, src), same,
               'files %d / saved %d' % (len(rp.get('replay_files') or {}), len(want)))
        if st == 'cat_c2':
            rows.a('input state cat_c2: %s absent (empty variant folder of the rebuild signature)' % DIR1, f19.get('present') is False, f19)
        elif st == 'rb_r3':
            rows.a('input state rb_r3: %s present with pipelines.bin (the folder of s17c_r3)' % DIR1,
                   f19.get('present') is True and f19.get('pipelines_bin') is True, f19)
        else:
            rows.r('input state k_ks: %s' % DIR1, f19)


def common(tag, p, r, so, run):
    rows = Rows()
    spec = SPEC[tag]
    att = ((run or {}).get('attempts') or [{}])[0] if run else {}
    rows.a('run record <tag>.json present, one attempt', run is not None and len((run or {}).get('attempts') or []) == 1,
           'attempts %s' % (len((run or {}).get('attempts') or []) if run else None))
    ename, bexp, bpath, ver, rev, seal, inst = edition(tag)
    sha = first_line(text(p['installed_sha'])) or None
    rows.a('binary of the run = %s (json and installed_sha.txt)' % ename,
           (run or {}).get('binary_sha256') == bexp and sha == bexp, '%s / %s' % ((run or {}).get('binary_sha256'), sha))
    vb = None
    if os.path.exists(bpath):
        vb = ver in open(bpath, 'rb').read()
    rows.a('version string %s in the binary copy' % ver.decode(), vb is True, vb)
    revs = r['rev'] + so['rev']
    badrev = [x for x in revs if rev not in x[2]]
    rows.a('revision texts of log / stdout name %s' % rev, not badrev, 'texts %d, other %s' % (len(revs), badrev[:3]))
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    rows.a('prereg sha256 = the seal file (%s)' % os.path.basename(seal), pre is not None and pre == sha_file(seal),
           '%s / %s' % (pre, sha_file(seal)))
    env_rows(rows, tag, run)
    win = r['win'].get('minimized', 0)
    rows.a('no window minimized, no Recovering Vulkan swapchain, no GamePatch line', win == 0 and r['recovering'] == 0 and
           r['gamepatch'] == 0, 'minimized %d recovering %d gamepatch %d' % (win, r['recovering'], r['gamepatch']))
    sin_t = text(p['state_in'])
    sin = state_s17c.parse(sin_t) if sin_t is not None else None
    state_rows(rows, tag, p, sin)
    rows.a('emulator log present', r['sha256'] is not None, r['sha256'])
    b = first_line(text(p['installed_before'])) or None
    a = first_line(text(p['installed_after'])) or None
    rows.f('installed binary before = after, %s' % ('FS6 or FS8' if inst == INSTALLED_OK_ED2 else 'FS8'),
           b is not None and b == a and b in inst, '%s / %s' % (b, a))
    mc = first_line(text(p['manifest_cmp']))
    rows.f('manifest of the caches after the return EQUAL', mc.startswith('manifest cmp EQUAL'), mc[:120])
    rows.r('window lines', r['win'])
    rows.r('death markers log / stdout', '%d / %d %s' % (len(r['death']), len(so['death']), (r['death'] + so['death'])[:3]))
    rows.r('skipped draw lines', r['skipped_draw'])
    rows.r('translation cache directory lines', r['stc'][:4])
    rows.r('exit', 'outcome %s detail %s hold_exit %s hold_s %s close_rc %s close_killed %s close_s %s' % (
        att.get('outcome'), att.get('detail'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'),
        att.get('close_s')))
    rows.r('preparation screen (startup wait finished)', '%s ms at line %s' % (r['prep'], r['prep_line']))
    return rows, att, sin


def lived(att, hold):
    """The process lived to the end of the hold: outcome ok, hold_exit null, attempt hold_s >= H."""
    return att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= hold


def entered(r, att):
    return r['entry_line'] is not None and att.get('outcome') == 'ok'


def directory_ok(r, want):
    return len(r['stc']) >= 1 and all(x.replace(chr(92), '/').endswith(want) for x in r['stc'])


def video_rows(rows, tag, p, r, so, att, group, report=False):
    add = (lambda name, ok, det: rows.r(name, '%s %s' % (yn(ok), det))) if report else rows.m
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    add('%s video index records >= %d' % (group, VIDEO_MIN), None if idx_n is None else idx_n >= VIDEO_MIN, idx_n)
    gt = text(p['glitch'])
    gl = None
    if gt:
        m = RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    add('%s 0 one-frame glitches (s51_vidglitch.py 4 6)' % group, None if gl is None else gl == 0, gl)
    st = text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    add('%s sheet of the lead made' % group, None if st is None else sheet is not None, sheet)
    nd = len(r['death']) + len(so['death'])
    add('%s 0 death markers (log, stdout)' % group, nd == 0, nd)


def hold_rows(rows, r, att, hold, group, frame_hold=True):
    rows.m('%s entered (Level has started: %s, outcome ok)' % (group, SKY), entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('%s the process lived to the end of the hold (%d s)' % (group, hold), lived(att, hold),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    if frame_hold:
        rows.m('%s shown hold after the first scene frame >= 300 s' % group, r['hold_us'] >= HOLD_MIN_US, '%.1f s' % (r['hold_us'] / 1e6))
    rows.r('frames >= 1 s after the first scene frame', r['k2_after'])


def last_capture(r):
    """The last 'capture ... at=stop' line (item 531 (v)(3)): dict or None."""
    stops = [d for _, d in r['capture'] if d.get('at') == 'stop']
    return stops[-1] if stops else None


def soft_close(att):
    return att.get('close_killed') is False and att.get('close_rc') is not None


def av_catalogue(r, hashes, after_line):
    """AvTrace: shader lines (one per new permutation) after the line after_line whose program hash is in the catalogue."""
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
    r = scan(p['log'])
    so = stdout_scan(p['stdout'])
    rt = text(p['run'])
    run = json.loads(rt) if rt else None
    rows, att, sin = common(tag, p, r, so, run)
    sout_t = text(p['state_out'])
    sout = state_s17c.parse(sout_t) if sout_t is not None else None
    extra = {}
    g = GROUP[tag]
    nsr = r['sr'] + so['sr']
    if tag in ('s17c_v0', 's17c_w0'):
        hold_rows(rows, r, att, spec['hold'], g)
        if tag == 's17c_v0':
            rows.m('K2(2) 0 ShaderReplay: lines (log, stdout)', nsr == 0, '%d / %d' % (r['sr'], so['sr']))
            rows.m('K2(2) no replay folder after the run (state_out.txt)', None if sout is None else
                   sout.get('replay', {}).get('present') is False, (sout or {}).get('replay'))
            video_rows(rows, tag, p, r, so, att, 'K2(2)')
        else:
            rows.m('K2(2) W 0 [Vulkan][E]', r['vke'] == 0, r['vke'])
            dual_before = [x for x in r['dual'] if r['first_guest'] is not None and x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]
            rows.m('K2(2) W positive control of the layer: [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut',
                   r['vkw'] > 0 and len(dual_before) >= 1, 'W %d, dual %s, first GuestOut %s' % (r['vkw'], r['dual'][:2], r['first_guest']))
            rows.r('ShaderReplay: lines (log / stdout)', '%d / %d' % (r['sr'], so['sr']))
            rows.r('limit lines of the layer', r['vk_limit'])
    elif tag in ('s17c_c2', 's17c_ca', 's17c_cc'):
        hold_rows(rows, r, att, spec['hold'], 'K3', frame_hold=(tag == 's17c_c2'))
        rows.a('K3 fitness: line PipelinePrecache: no <path> yet (item 532 (v))', len(r['precache_no']) >= 1, r['precache_no'][:2])
        md = r['mode'][0][1] if r['mode'] else {}
        rows.m('K3 mode line mode=2 compat=absent (a new catalogue)', md.get('mode') == '2' and md.get('compat') == 'absent', md)
        rows.m('K3 translation cache directory = %s (signature of KYTY_FIX_F19=0)' % DIR0, directory_ok(r, DIR0), r['stc'][:2])
        lc = last_capture(r)
        rows.r('capture lines (save / stop)', '%d / %d' % (sum(1 for _, d in r['capture'] if d.get('at') == 'save'),
                                                          sum(1 for _, d in r['capture'] if d.get('at') == 'stop')))
        rows.r('last capture at=stop', lc)
        kinds, res = reject_summary(r['reject'])
        rows.r('capture reject lines logged by kind (self/base/big <= 20 by their sum, residual <= 20 of its own, item 546 (b))', kinds)
        rows.r('residual branch:role of the first culprit (diagnostics, not a member, item 541 (g))', res)
        rows.r('capture reject lines (first 5; committed form without raw values, item 548 (v)(2))',
               [reject_clean(x[1]) for x in r['reject'][:5]])
        rows.r('shader resource specialization failed in _kyty.txt / stdout (item 531 (d)(5))', '%d / %d' % (r['specfail'], so['specfail']))
        g_c, gf, cat, cerr = catalogue_of(tag)
        rows.r('saved catalogue', 'replay.cur %s file %s error %s' % (g_c, gf and os.path.basename(gf), cerr))
        if tag == 's17c_c2':
            if lc is None:
                for nm in ('canon_mismatch = 0', 'canon_base = 0', 'dropped_queue = 0', 'sources > 0', 'specs > 0',
                           'generation file on disk', 'offline R_ADDR = 0'):
                    rows.m('K3 %s (no capture at=stop line - K3 and K4 not determined, item 531 (v)(3))' % nm, None)
            else:
                cm, cb = num(lc, 'canon_mismatch'), num(lc, 'canon_base')
                rows.m('K3 canon_mismatch = 0 (canon_self + canon_residual)', cm == 0, 'canon_mismatch %s self %s residual %s' % (
                    cm, lc.get('canon_self'), lc.get('canon_residual')))
                rows.m('K3 canon_base = 0 (item 531 (v)(2))', cb == 0, cb)
                dq = num(lc, 'dropped_queue')
                rows.m('K3 dropped_queue = 0 (read at a soft close, item 532 (z) N4)', (dq == 0) if soft_close(att) else None,
                       'dropped_queue %s soft close %s' % (dq, soft_close(att)))
                rows.m('K3 sources > 0', (num(lc, 'sources') or 0) > 0, lc.get('sources'))
                rows.m('K3 specs > 0', (num(lc, 'specs') or 0) > 0, lc.get('specs'))
                gen = num(lc, 'gen')
                rows.m('K3 generation file on disk = gen of the last capture line and readable', cat is not None and g_c == gen,
                       'replay.cur %s gen %s error %s' % (g_c, gen, cerr))
                rows.m('K3 offline R_ADDR = 0 ("the role layout agrees", item 532 (e))', None if cat is None else cat['R_ADDR'] == 0,
                       None if cat is None else cat['R_ADDR'])
                rows.r('canon_big, canon_self, canon_residual (reference)', '%s %s %s' % (lc.get('canon_big'), lc.get('canon_self'),
                                                                                       lc.get('canon_residual')))
                rows.r('pipes, pipes_waiting (denominator of K4), catalogue_*', '%s %s %s/%s/%s' % (
                    lc.get('pipes'), lc.get('pipes_waiting'), lc.get('catalogue_sources'), lc.get('catalogue_specs'),
                    lc.get('catalogue_pipes')))
                extra['pipes_waiting'] = num(lc, 'pipes_waiting')
                extra['last_capture'] = lc
            f10 = os.path.join(p['state'], 'f10')
            if os.path.isdir(f10):
                files, bad = tc_s17c.read_folder(f10)
                sigs = sorted(set(x['signature'] for x in files.values()))
                rows.r('signature of the capture folder state/s17c_c2/f10 (reference; seal section 1: = %s)' % SIG0,
                       'files %d bad %d signatures %s equal %s' % (len(files), len(bad), sigs, sigs == [SIG0]))
            else:
                rows.r('signature of the capture folder state/s17c_c2/f10 (reference)', 'folder not saved')
            if cat is not None:
                rows.r('KEEP words >= 0x10000 (reference, item 532 (e))', cat['keep_big'])
                rows.r('catalogue sources / specs / pipes / words / keep', '%d %d %d %d %d' % (cat['sources'], cat['specs'], cat['pipes'],
                                                                                         cat['words'], cat['keep']))
                extra['catalogue_programs'] = len(cat['src_hashes'])
        elif tag == 's17c_ca':
            st = [x for x in r['stand'] if x[1].startswith('stand addr applied')]
            rows.m('K3 stand addr: line stand addr applied', None if not st else True, st[:1])
            rows.m('K3 stand addr: offline R_ADDR > 0 on the catalogue of the tag', None if (not st or cat is None) else cat['R_ADDR'] > 0,
                   None if cat is None else cat['R_ADDR'])
            if st and cat is not None:
                sid = st[0][2].get('spec')
                rows.r('stand spec id in the catalogue', sid is not None and int(sid, 16) in set(cat['spec_ids']))
        else:
            ok, det = canon_stand(r)
            rows.m('K3 stand canon: pair stand canon applied hash=H rejected=1 / capture reject why=self ... culprit=<i>:role6:<raw>'
                   '->00000000 ... hash=H and canon_mismatch >= 1 (item 536 (b))', ok, det)
    elif tag == 's17c_n0':
        hold_rows(rows, r, att, spec['hold'], 'K4/K5')
        rows.m('K4 translation cache directory = %s (signature of KYTY_FIX_F19=1)' % DIR1, directory_ok(r, DIR1), r['stc'][:2])
        _g, _f, cat, cerr = catalogue_of('s17c_c2')
        n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
        rows.m('K5 null control: translations of catalogue programs in the game > 0 (cold =0, empty variant folder)',
               None if n_cat is None else n_cat > 0, 'catalogue programs %s of new permutations %s after the preparation line %s; %s' % (
                   n_cat, n_all, r['prep_line'], cerr))
        live = os.path.join(p['state'], 'f19')
        files, bad = tc_s17c.read_folder(live) if os.path.isdir(live) else ({}, [('<folder>', 'missing')])
        rows.m('K4 live folder saved (state/s17c_n0/f19) and every file readable', os.path.isdir(live) and not bad and len(files) > 0,
               'files %d bad %s' % (len(files), bad[:3]))
        rows.r('ShaderReplay: lines (log / stdout)', '%d / %d' % (r['sr'], so['sr']))
        video_rows(rows, tag, p, r, so, att, 'control (report)', report=True)
        extra['catalogue_translations'] = n_cat
    elif tag in ('s17c_r3', 's17c_rs'):
        rebuild_rows(rows, tag, p, r, so, att, extra)
    elif tag in ('s17c_e3', 's17c_ew'):
        hold_rows(rows, r, att, spec['hold'], 'K5')
        sk = [x for x in r['skipped'] if x[1] == 'recipes_current']
        rows.m('K5 fitness: rebuild skipped reason=recipes_current (the folder of s17c_r3)', len(sk) >= 1 and not r['rebuild'],
               'skipped %s rebuild lines %d' % (r['skipped'][:2], len(r['rebuild'])))
        if tag == 's17c_e3':
            _g, _f, cat, cerr = catalogue_of('s17c_c2')
            n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
            r3 = read_json_of('s17c_r3') or {}
            n0 = read_json_of('s17c_n0') or {}
            cont = (r3.get('extra') or {}).get('guest_catalogue_translations')
            ok = None if (n_cat is None or cont is None) else (None if cont != 0 else n_cat == 0)
            rows.m('K5 translations of catalogue programs in the game = 0 (not determined when s17c_r3 translated catalogue programs after '
                   'its preparation screen)', ok, 'e3 %s of %s; r3 after its preparation %s; %s' % (n_cat, n_all, cont, cerr))
            ctl = (n0.get('extra') or {}).get('catalogue_translations')
            rows.m('K5 null control s17c_n0 > 0', None if ctl is None else ctl > 0, ctl)
            rows.m('K5 preparation screen <= 180 s (startup wait finished)', None if r['prep'] is None else r['prep'] <= PREP_MAX_MS,
                   '%s ms' % r['prep'])
            rows.r('new permutations before the preparation line', sum(1 for x in r['av'] if r['prep_line'] and x[0] < r['prep_line']))
            video_rows(rows, tag, p, r, so, att, 'K5')
            extra['catalogue_translations'] = n_cat
        else:
            rows.m('K5 W 0 [Vulkan][E]', r['vke'] == 0, r['vke'])
            dual_before = [x for x in r['dual'] if r['first_guest'] is not None and x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]
            rows.m('K5 W positive control of the layer: [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut',
                   r['vkw'] > 0 and len(dual_before) >= 1, 'W %d, dual %s' % (r['vkw'], r['dual'][:2]))
            rows.r('limit lines of the layer', r['vk_limit'])
            rows.r('death markers (W)', len(r['death']) + len(so['death']))
    elif tag == 's17c_ks':
        stop_rows(rows, p, r, so, att, sout)
    elif tag in ('s17c_kn', 's17c_kc'):
        hold_rows(rows, r, att, spec['hold'], 'K6', frame_hold=False)
        nd = len(r['death']) + len(so['death'])
        rows.m('K6 0 death markers (the game path as before)', nd == 0, nd)
        rb = r['rebuild'][-1][1] if r['rebuild'] else {}
        g_c, _f, _cat, _e = catalogue_of('s17c_c2')
        md = r['mode'][0][1] if r['mode'] else {}
        if tag == 's17c_kn':
            rows.m('K6 mode line mode=3 compat=ok', md.get('mode') == '3' and md.get('compat') == 'ok', md)
            rows.m('K6 the next start rebuilds the rest: a rebuild line (no skip), perms_cached > 0, pipelines_bin=written',
                   bool(rb) and not r['skipped'] and (num(rb, 'perms_cached') or 0) > 0 and rb.get('pipelines_bin') == 'written',
                   'skipped %s rebuild %s' % (r['skipped'][:1], dict((k, rb.get(k)) for k in ('records', 'prepared', 'perms_new',
                                                                                             'perms_cached', 'pipelines_bin'))))
            r3 = read_json_of('s17c_r3') or {}
            rows.r('prepared of s17c_r3 (reference)', ((r3.get('extra') or {}).get('rebuild') or {}).get('prepared'))
        else:
            st = [x for x in r['stand'] if x[1].startswith('stand corrupt applied')]
            sg = num(st[0][2], 'generation') if st else None
            rows.m('K6 stand corrupt applied generation = the current generation of s17c_c2', None if not st else sg == g_c,
                   'stand %s c2 %s' % (sg, g_c))
            ok = None if not st or g_c is None else (md.get('compat') == 'ok' and num(md, 'generation') == g_c - 1 and
                                                    num(md, 'corrupt') == g_c)
            rows.m('K6 the previous generation is loaded: mode line compat=ok generation=G-1 corrupt=G', ok, md)
            rows.r('rebuild line', dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'pipelines_bin')))
    return rows, dict(tag=tag, group=g, log_sha256=r['sha256'], stdout_sha256=so['sha256'], extra=extra)


def canon_stand(r):
    """(ok, detail) of item 536 (b): YES only for the pair of lines of one hash H and canon_mismatch >= 1 of the last capture line;
    anything else is NOT DETERMINED, never NO."""
    applied = [(ln, d) for ln, t, d in r['stand'] if t.startswith('stand canon applied') and d.get('rejected') == '1']
    if not applied:
        return None, 'no stand canon applied ... rejected=1 line (rejected=0 lines %d)' % sum(
            1 for _, t, d in r['stand'] if t.startswith('stand canon applied') and d.get('rejected') == '0')
    lc = last_capture(r) or (r['capture'][-1][1] if r['capture'] else {})
    cm = num(lc, 'canon_mismatch')
    for ln, d in applied:
        h = d.get('hash')
        for rl, body in r['reject']:
            if ' hash=%s ' % h not in body + ' ' or not body.startswith('capture reject why=self'):
                continue
            for m in RX_CULPRIT.finditer(body):
                if m.group(2) == '6' and m.group(4) == '00000000':
                    return (cm is not None and cm >= 1) or None, 'hash %s stand line %d reject line %d culprit=%s:role6 canon_zero=1 ' \
                        'canon_mismatch %s' % (h, ln, rl, m.group(1), cm)
    return None, 'no capture reject why=self with culprit role6 ->00000000 of hash %s (reject lines %d)' % (
        [d.get('hash') for _, d in applied], len(r['reject']))


def rebuild_rows(rows, tag, p, r, so, att, extra):
    md = r['mode'][0][1] if r['mode'] else {}
    g_c, _f, cat, cerr = catalogue_of('s17c_c2')
    rows.m('K4 mode line mode=3 compat=ok generation = replay.cur of s17c_c2', md.get('mode') == '3' and md.get('compat') == 'ok' and
           g_c is not None and num(md, 'generation') == g_c, '%s / c2 %s' % (md, g_c))
    rb = r['rebuild'][-1][1] if r['rebuild'] else None
    rows.m('K4 a rebuild line and no rebuild skipped line', rb is not None and not r['skipped'], 'rebuild %d skipped %s' % (
        len(r['rebuild']), r['skipped'][:1]))
    nd = len(r['death']) + len(so['death'])
    rows.m('K4 0 death markers on the rebuild tag (item 531 (d)(4))', nd == 0, (r['death'] + so['death'])[:3])
    rows.m('K4 the process reached the end of the preparation screen (--until-prep outcome prep)', att.get('outcome') == 'prep',
           att.get('outcome'))
    rb = rb or {}
    rows.m('K4 pipelines_bin=written', rb.get('pipelines_bin') == 'written', rb.get('pipelines_bin'))
    recs, prep, rej, pend = num(rb, 'records'), num(rb, 'prepared'), num(rb, 'rejected'), num(rb, 'pending')
    ident = None if None in (recs, prep, rej, pend) else prep + rej + pend == recs
    rows.m('K4 identity prepared + rejected + pending = records', ident, '%s + %s + %s = %s' % (prep, rej, pend, recs))
    parts = [num(rb, k) for k in ('rej_src', 'rej_fused', 'rej_key', 'rej_version', 'rej_shape', 'rej_translate', 'rej_emit', 'rej_val',
                                  'rej_write', 'rej_ref')]
    part = None if None in parts or rej is None else sum(parts) == rej
    rows.m('K4 partition of the reasons: sum rej_* (rej_ref included, item 531 (g)) = rejected', part, '%s = %s' % (parts, rej))
    c2 = read_json_of('s17c_c2') or {}
    pw = (c2.get('extra') or {}).get('pipes_waiting')
    share = None if (prep is None or recs is None or pw is None or recs + pw == 0) else prep / float(recs + pw)
    rows.m('K4 share prepared / (records + pipes_waiting of s17c_c2) >= 0.90 (item 531 (v)(3))', None if share is None else
           share >= SHARE_MIN, 'share %s = %s / (%s + %s)' % (None if share is None else round(share, 4), prep, recs, pw))
    rows.r('pending (0 after a complete rebuild, S16a section 7)', pend)
    rows.r('rej_ref (> 0 = code defect, read in S17d, item 531 (g))', rb.get('rej_ref'))
    rows.r('records vs catalogue pipes of s17c_c2', '%s / %s' % (recs, None if cat is None else cat['pipes']))
    for k in ('perms_new', 'perms_cached', 'rb_push_moved', 'rb_spec_changed', 'groups_same_pc', 'group_sources', 'translate_ms', 'wall_ms'):
        rows.r(k, rb.get(k))
    rows.r('rebuild-src / rebuild-spec', '%s / %s' % (r['rebuild_src'][-1][1] if r['rebuild_src'] else None,
                                                     r['rebuild_spec'][-1][1] if r['rebuild_spec'] else None))
    rows.r('hits lines (the counter of this run, item 524 (z))', [d for _, d in r['hits']][-2:])
    n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
    rows.r('new permutations after the preparation line: catalogue programs / all (input of K5)', '%s / %s' % (n_cat, n_all))
    extra['guest_catalogue_translations'] = n_cat
    extra['rebuild'] = dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'pipelines_bin'))
    live = os.path.join(paths('s17c_n0')['state'], 'f19')
    rbdir = os.path.join(p['state'], 'f19')
    man = os.path.join(p['state'], 'replay', 'rebuild_manifest.tsv')
    stand = None
    if tag == 's17c_rs':
        st = [x for x in r['stand'] if x[1].startswith('stand spec applied')]
        stand = (st[0][2].get('file'), st[0][2].get('permutation')) if st else None
    x = k4x(live, rbdir, man, stand)
    extra['k4x'] = dict((k, v) for k, v in x.items() if k not in ('live_sigs', 'rb_sigs'))
    if not x['ok']:
        rows.m('K4 comparison with the live translation (s17c_n0): inputs present', None, x['error'])
        return
    sig_ok = x['manifest_sig'] == SIG1 and x['live_sigs'] == [SIG1] and x['rb_sigs'] == [SIG1]
    clean = x['live_bad'] == 0 and x['rb_bad'] == 0 and x['manifest_bad'] == 0 and x['manifest_bad_lines'] == 0
    rows.m('K4 comparison self-checks: every file readable, every manifest row found with its start and XXH3, signatures = %s' % SIG1,
           sig_ok and clean, 'live_bad %d rb_bad %d manifest_bad %d bad_lines %d manifest_sig %s live_sigs %s rb_sigs %s' % (
               x['live_bad'], x['rb_bad'], x['manifest_bad'], x['manifest_bad_lines'], x['manifest_sig'], x['live_sigs'], x['rb_sigs']))
    det = sig_ok and clean
    rows.r('live_perms / rebuilt / rb_hit / rb_dead / rb_live_mismatch', '%d / %d / %d / %d / %d' % (
        x['live_perms'], x['rebuilt'], x['rb_hit'], x['rb_dead'], x['rb_live_mismatch']))
    if tag == 's17c_r3':
        rows.m('K4 rb_hit / live_perms >= 0.90 (item 532 (zh))', None if not det or not x['live_perms'] else x['hit_share'] >= HIT_MIN,
               '%s / %s = %s' % (x['rb_hit'], x['live_perms'], None if x['hit_share'] is None else round(x['hit_share'], 4)))
        rows.m('K4 rb_live_mismatch = 0 on rb_hit', None if not det else x['rb_live_mismatch'] == 0, x['rb_live_mismatch'])
    else:
        st_ok = stand is not None and x.get('stand_in_live') is True
        rows.m('K4 stand spec: line stand spec applied and its (file, index) among live_perms of s17c_n0 (item 532 (d)(b))',
               None if not st_ok else True, 'stand %s in manifest %s in live %s' % (stand, x.get('stand_in_manifest'), x.get('stand_in_live')))
        rows.m('K4 stand spec: rb_live_mismatch > 0', None if (not st_ok or not det) else x['rb_live_mismatch'] > 0,
               '%d (stand permutation differs: %s)' % (x['rb_live_mismatch'], x.get('stand_mismatch')))


def stop_rows(rows, p, r, so, att, sout):
    st = [x for x in r['stand'] if x[1].startswith('stand stop applied')]
    sl = st[0][0] if st else None
    stopped = [ln for ln, d in r['rebuild'] if d.get('pipelines_bin') == 'stopped']
    rows.m('K6 stand stop applied line', None if not st else True, st[:1])
    rows.m('K6 sign of the break: rebuild ... pipelines_bin=stopped after stand stop applied (item 532 (b))', None if sl is None else
           any(ln > sl for ln in stopped), 'stand line %s stopped lines %s' % (sl, stopped[:2]))
    f19 = (sout or {}).get('f19', {})
    rows.m('K6 pipelines.bin is not written at the break (state_out.txt, %s)' % DIR1, None if sout is None else
           f19.get('pipelines_bin') is not True, f19)
    rows.r('close stop requested / joined lines', '%s / %s' % (r['close_req'][:1], r['close_joined'][:1]))
    order = None
    if sl is not None and r['close_req'] and r['close_joined'] and stopped:
        order = sl < r['close_req'][0][0] and sl < stopped[0] and stopped[0] < r['close_joined'][0][0]
    rows.r('order stand < requested, stand < stopped < joined (S17a2 section 2)', order)
    rows.r('wait_ms of close stop joined (reference, item 533 (b))', r['close_joined'][0][1].get('wait_ms') if r['close_joined'] else None)
    man = os.path.join(p['state'], 'replay', 'rebuild_manifest.tsv')
    rows.r('rebuild_manifest.tsv after the break (S17a2: not written)', os.path.exists(man))
    rows.r('translation cache files after the break (S17a2: saved)', f19.get('cache_files'))
    rows.r('no startup wait line (the close path)', r['prep_line'] is None)
    nd = len(r['death']) + len(so['death'])
    rows.r('death markers', nd)


# ----------------------------------------------------------------------------------------------------------------- output

def print_rows(tag, rows, meta):
    print('S17c reader tag %s group %s' % (tag, meta['group']))
    print('  log sha256 %s stdout sha256 %s' % (meta['log_sha256'], meta['stdout_sha256']))
    for title, lst in (('ADMISSION', rows.adm), ('FORM', rows.form), ('MEMBERS', rows.mem)):
        print('  %s' % title)
        for name, ok, det in lst:
            print('    %-15s %s | %s' % (yn(ok), asc(name), det[:400]))
    print('  REPORT')
    for name, det in rows.rep:
        print('    %s: %s' % (asc(name), det[:400]))
    print('  READING %s' % rows.word())


def to_json(tag, rows, meta):
    return dict(meta, reading=rows.word(), admission=[list(x) for x in rows.adm], form=[list(x) for x in rows.form],
                members=[list(x) for x in rows.mem], report=[list(x) for x in rows.rep])


def table():
    print('S17c member table K2(2)-K6 (no verdict - S17d)')
    for tag in ORDER:
        d = read_json_of(tag)
        if d is None:
            print('  %-8s %-6s NOT READ' % (tag, GROUP[tag]))
            continue
        print('  %-8s %-6s READING %s' % (tag, GROUP[tag], d['reading']))
        for name, ok, det in d['members']:
            print('      %-15s %s | %s' % (yn(ok), name, det[:200]))
    return 0


def stop537():
    """Item 537 (zh): the series stops after the K3 tags when the capture tag s17c_c2 gives canon_mismatch > 0 (any reason).  GO only when
    runs/s17c_c2/read.json exists, its reading is not NOT_ADMITTED and canon_mismatch of its last capture at=stop line is 0."""
    d = read_json_of('s17c_c2')
    if d is None:
        return False, 's17c_c2 not read (runs/s17c_c2/read.json missing)'
    if d.get('reading') == 'NOT_ADMITTED':
        return False, 's17c_c2 reading NOT_ADMITTED (interference: one repeat by the same name, item 537 (e))'
    cm = num((d.get('extra') or {}).get('last_capture') or {}, 'canon_mismatch')
    if cm is None:
        return False, 's17c_c2 has no capture at=stop line (K3 and K4 not determined, item 531 (v)(3))'
    if cm != 0:
        return False, 's17c_c2 canon_mismatch %d > 0 - the series stops after K3, question to the lead (item 537 (zh))' % cm
    return True, 's17c_c2 canon_mismatch 0, reading %s' % d.get('reading')


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--table':
        return table()
    if argv[0] == '--stop537':
        ok, why = stop537()
        print('STOP537 %s %s' % ('GO' if ok else 'STOP', why))
        return 0 if ok else 1
    if argv[0] == '--catalogue':
        c = catalogue(argv[1])
        print('catalogue %s generation %d sources %d specs %d pipes %d words %d keep %d keep_big %d R_ADDR %d programs %d compat %s' % (
            argv[1], c['generation'], c['sources'], c['specs'], c['pipes'], c['words'], c['keep'], c['keep_big'], c['R_ADDR'],
            len(c['src_hashes']), c['compat']))
        return 0
    if argv[0] == '--k4x':
        stand = (argv[5], argv[6]) if len(argv) > 6 and argv[4] == '--stand' else None
        x = k4x(argv[1], argv[2], argv[3], stand)
        for k in sorted(x):
            print('%s %s' % (k, asc(str(x[k]))))
        return 0 if x['ok'] else 1
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
